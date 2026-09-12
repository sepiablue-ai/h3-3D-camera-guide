"""Run using ComfyUI embedded Python: python.exe -s tests/test_camera.py."""
import importlib.util
import json
from pathlib import Path
import sys
import types
import unittest
import shutil
import subprocess
import numpy as np

root = Path(__file__).resolve().parents[1]
pkg = types.ModuleType('guide'); pkg.__path__ = [str(root)]; sys.modules['guide'] = pkg
from guide.camera import DEFAULT, parse_state, sample, basis
from guide.renderer import render_frame


class CameraTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('node'), 'Node.js is only needed for development parity tests')
    def test_frontend_backend_contract(self):
        code="import {DEFAULT,sample,basis} from './web/camera.mjs'; console.log(JSON.stringify([0,.5,1,3,5.125].map(t=>({pose:sample(DEFAULT,t),basis:basis(sample(DEFAULT,t))}))));"
        rows=json.loads(subprocess.check_output(['node','--input-type=module','-e',code],cwd=root))
        for t,row in zip([0,.5,1,3,5.125],rows):
            k=sample(DEFAULT,t)
            for n in ['orbit','elevation','distance','fov']:
                self.assertAlmostEqual(k[n],row['pose'][n])
            pos,_,up,_=basis(k)
            np.testing.assert_allclose(pos,row['basis']['position'],atol=1e-6)
            np.testing.assert_allclose(up,row['basis']['up'],atol=1e-6)

    def test_roundtrip_and_endpoints(self):
        s = parse_state(json.dumps(DEFAULT))
        for k in s['keys']:
            self.assertEqual(sample(s,k['t']),k)
        self.assertEqual(sample(s,100),s['keys'][-1])

    def test_reject_invalid(self):
        for mutate in [lambda s:s['keys'].append(s['keys'][0]),lambda s:s['keys'][0].update(distance=0),lambda s:s['keys'][0].update(fov=float('nan'))]:
            s=json.loads(json.dumps(DEFAULT));mutate(s)
            with self.assertRaises(ValueError):parse_state(s)

    def test_basis_and_easing(self):
        for t in np.linspace(0,5.125,30):
            k=sample(DEFAULT,t);pos,r,u,f=basis(k)
            np.testing.assert_allclose(np.array([r,u,f])@np.array([r,u,f]).T,np.eye(3),atol=1e-6)
            self.assertAlmostEqual(np.linalg.norm(np.array(pos)-k['target']),k['distance'])
        self.assertAlmostEqual(sample(DEFAULT,.5)['elevation'],42.5)
        self.assertLess(abs(sample(DEFAULT,1-1e-5)['elevation']),1e-6)

    def test_real_render_top_front_side(self):
        frames=[render_frame(sample(DEFAULT,t),144,256) for t in [0,1,5.125]]
        for frame in frames:
            self.assertTrue(np.isfinite(frame).all())
            # Blue body pixels must actually be visible in each orientation.
            self.assertGreater(int(((frame[:,:,2]-frame[:,:,0]>.12)&(frame[:,:,0]<.4)).sum()),20)
            self.assertGreaterEqual(frame.min(),0);self.assertLessEqual(frame.max(),1)
        self.assertGreater(np.abs(frames[0]-frames[1]).mean(),.01)
        self.assertGreater(np.abs(frames[1]-frames[2]).mean(),.001)

if __name__=='__main__':unittest.main()
