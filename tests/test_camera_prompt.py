import copy
import sys
import types
import unittest
from pathlib import Path

pkg=types.ModuleType('guide');pkg.__path__=[str(Path(__file__).resolve().parents[1])];sys.modules['guide']=pkg
from guide.camera import DEFAULT
from guide.camera_prompt import compile_camera, compose, saved_trajectory
import json


class PromptTests(unittest.TestCase):
    def state(self, **changes):
        a=copy.deepcopy(DEFAULT['keys'][1]);a['t']=0
        b={**copy.deepcopy(a), 't':2, **changes}
        return {'version':1,'keys':[a,b]}

    def test_full_turns_and_reverse_are_not_wrapped(self):
        for orbit in [720,-450,37]:
            text=compile_camera(self.state(orbit=orbit),49,24)
            self.assertIn(f'by {abs(orbit)} degrees',text)
            self.assertIn('00:02.000',text)

    def test_independent_translation_zoom_dolly(self):
        text=compile_camera(self.state(target=[3,2,-1],distance=2,fov=80),49,24)
        for fragment in ['rig and its aim point translate','pushes in','zooms out']:
            self.assertIn(fragment,text)
        self.assertNotIn('camera arcs',text)

    def test_clip_and_hold(self):
        s=self.state(orbit=90);s['keys'][0]['t']=1;s['keys'][1]['t']=3
        text=compile_camera(s,97,24)
        self.assertIn('From 00:00.000 to 00:01.000, hold',text)
        self.assertIn('From 00:03.000 to 00:04.000, hold',text)
        clipped=compile_camera(s,49,24)
        self.assertIn('azimuth 45 degrees',clipped)
        self.assertNotIn('00:03.000',clipped)

    def test_reversal_and_static_and_single_frame(self):
        s=self.state(orbit=90);s['keys'].append({**s['keys'][0],'t':4})
        text=compile_camera(s,97,24)
        self.assertIn('+Z toward +X',text);self.assertIn('+Z toward -X',text)
        self.assertIn('hold the camera',compile_camera(self.state(),49,24))
        self.assertNotIn('From ',compile_camera(s,1,24))

    def test_preserve_actions_and_no_unresolved_video(self):
        camera=compile_camera(DEFAULT,124,24)
        for action in ['She sits and drinks coffee.','She runs across the cafe.','She stands and waves.']:
            text=compose(action,'<Subject 1> from <Picture 1>.',camera,False,'Quiet.','None.')
            self.assertIn(action,text);self.assertNotIn('<Video 1>',text)
            self.assertNotIn(action,camera)
        self.assertIn('<Video 1>',compose('She sits.','Identity.',camera,True,'Quiet.','None.'))

    def test_conflicts_and_unverifiable_video_fail(self):
        for action in ['The camera pans left. She sits.','カメラは固定。女性は走る。']:
            with self.assertRaises(ValueError):compose(action,'Identity.','camera',False,'Quiet.','None.')
        with self.assertRaises(ValueError):compile_camera({'source_mode':'reuse_video'},124,24)

    def test_metadata_duration_is_authoritative(self):
        s={**self.state(orbit=90),'frames':49,'fps':24}
        self.assertIn('00:02.000',compile_camera(s))

    def test_saved_guide_not_generated_result_or_resized_video(self):
        w={'g':{'class_type':'H3CameraGuide','inputs':{'camera_state':json.dumps(DEFAULT),'width':576,'height':1024,'frames':124,'fps':24}},'s':{'class_type':'SaveVideo','inputs':{'filename_prefix':'test/guide','video':['g',1]}}}
        metadata={'prompt':json.dumps(w)}
        state=saved_trajectory(metadata,'guide_00001_.mp4',576,1024,124,24)
        self.assertEqual(state,DEFAULT)
        self.assertIsNone(saved_trajectory(metadata,'result_00001_.mp4',576,1024,124,24))
        self.assertIsNone(saved_trajectory(metadata,'guide_00001_.mp4',384,640,124,24))
        self.assertIn('overhead',compile_camera({'source_mode':'reuse_video','camera_state':state,'frames':124,'fps':24}))

if __name__=='__main__':unittest.main()
