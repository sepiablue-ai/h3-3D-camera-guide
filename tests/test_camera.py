"""Run using ComfyUI embedded Python: python.exe -s tests/test_camera.py."""
import importlib.util
import json
from pathlib import Path
import sys
import types
import unittest
import shutil
import subprocess
from unittest.mock import patch
import numpy as np

root = Path(__file__).resolve().parents[1]
pkg = types.ModuleType('guide'); pkg.__path__ = [str(root)]; sys.modules['guide'] = pkg
from guide.camera import DEFAULT, parse_state, sample, basis
from guide.renderer import render_frame


class CameraTests(unittest.TestCase):
    def test_ball_and_floor_cues(self):
        front=sample(DEFAULT,1)
        ball=render_frame(front,144,256,'ball','plain')
        human=render_frame(front,144,256,'mannequin','plain')
        self.assertGreater(np.abs(ball-human).mean(),.02)
        top=sample(DEFAULT,0)
        plain=render_frame(top,144,256,'ball','plain')
        marked=render_frame(top,144,256,'ball','markers')
        self.assertGreater(np.abs(plain-marked).sum(),20)

    def test_reuse_bypasses_renderer_and_ignores_editor_settings(self):
        import torch
        from guide.nodes import H3CameraGuide
        data=torch.zeros((5,16,24,3))
        video=types.SimpleNamespace(get_dimensions=lambda:(24,16),get_frame_count=lambda:5,
            get_components=lambda:types.SimpleNamespace(images=data,frame_rate=24))
        modules={'comfy_api.latest':types.SimpleNamespace(InputImpl=None,Types=None),
                 'comfy.utils':types.SimpleNamespace(ProgressBar=None),
                 'comfy':types.ModuleType('comfy'), 'comfy.model_management':types.ModuleType('comfy.model_management')}
        with patch.dict(sys.modules,modules),patch('guide.nodes.render_sequence',side_effect=AssertionError('Must not render')):
            images,out,fps,info=H3CameraGuide().generate('invalid unused state',1920,1920,720,1,source_mode='reuse_video',existing_video=video)
            self.assertEqual(tuple(images.shape),(5,16,24,3));self.assertIs(out,video);self.assertEqual(fps,24)
            self.assertIsNone(json.loads(info)['camera_state'])
            video.get_frame_count=lambda:721
            with self.assertRaises(ValueError):H3CameraGuide().generate('',1,1,1,1,source_mode='reuse_video',existing_video=video)

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
