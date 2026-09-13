import copy
import sys
import types
import unittest
from pathlib import Path

pkg=types.ModuleType('guide');pkg.__path__=[str(Path(__file__).resolve().parents[1])];sys.modules['guide']=pkg
from guide.camera import DEFAULT
from guide.camera_prompt import compile_camera, compose, saved_trajectory, screen_direction, describe, H3CameraPrompt
import json


class PromptTests(unittest.TestCase):
    def state(self, **changes):
        a=copy.deepcopy(DEFAULT['keys'][1]);a['t']=0
        b={**copy.deepcopy(a), 't':2, **changes}
        return {'version':1,'keys':[a,b]}

    def test_full_turns_and_reverse_are_not_wrapped(self):
        for orbit in [720,-450,37]:
            text=compile_camera(self.state(orbit=orbit),49,24)
            self.assertGreaterEqual(text.count('At '), 2 if abs(orbit)<60 else 8)
            self.assertIn('At 2.000 seconds:',text)
            self.assertIn('ordered views',text)

    def test_independent_translation_zoom_dolly(self):
        text=compile_camera(self.state(target=[3,2,-1],distance=2,fov=80),49,24)
        for fragment in ['translate the camera rig and its aim point','push in','field of view from 45 to 80']:
            self.assertIn(fragment,text)
        self.assertNotIn('camera arcs',text)

    def test_clip_and_hold(self):
        s=self.state(orbit=90);s['keys'][0]['t']=1;s['keys'][1]['t']=3
        text=compile_camera(s,97,24)
        self.assertIn('From 0.000 to 1.000 seconds, hold',text)
        self.assertIn('From 3.000 to 4.000 seconds, hold',text)
        clipped=compile_camera(s,49,24)
        self.assertIn('At 2.000 seconds: a horizontal view, without looking down or up; a front three-quarter view',clipped)
        self.assertNotIn('At 3.000',clipped)

    def test_reversal_and_static_and_single_frame(self):
        s=self.state(orbit=90);s['keys'].append({**s['keys'][0],'t':4})
        text=compile_camera(s,97,24)
        self.assertEqual(text.count('a frontal view'),2)
        self.assertIn('At 2.000 seconds: a horizontal view, without looking down or up; a side-profile view',text)
        self.assertIn('hold camera',compile_camera(self.state(),49,24))
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
        self.assertIn('At 2.000 seconds:',compile_camera(s))

    def test_saved_guide_not_generated_result_or_resized_video(self):
        w={'g':{'class_type':'H3CameraGuide','inputs':{'camera_state':json.dumps(DEFAULT),'width':576,'height':1024,'frames':124,'fps':24}},'s':{'class_type':'SaveVideo','inputs':{'filename_prefix':'test/guide','video':['g',1]}}}
        metadata={'prompt':json.dumps(w)}
        state=saved_trajectory(metadata,'guide_00001_.mp4',576,1024,124,24)
        self.assertEqual(state,DEFAULT)
        self.assertIsNone(saved_trajectory(metadata,'result_00001_.mp4',576,1024,124,24))
        self.assertIsNone(saved_trajectory(metadata,'guide_00001_.mp4',384,640,124,24))
        self.assertIn('overhead',compile_camera({'source_mode':'reuse_video','camera_state':state,'frames':124,'fps':24}))


    def test_projection_quadrants_and_underside(self):
        k=self.state()['keys'][0]
        for orbit,direction in [(0,'BOTTOM'),(90,'LEFT'),(180,'TOP'),(270,'RIGHT'),(-90,'RIGHT')]:
            self.assertEqual(screen_direction({**k,'orbit':orbit,'elevation':85}),direction)
        self.assertEqual(screen_direction({**k,'elevation':-85}),'TOP')
        self.assertIsNone(screen_direction(k))
        self.assertIsNone(screen_direction({**k,'orbit':180}))

    def test_projection_is_continuous_across_overhead_wording(self):
        k=self.state()['keys'][0]
        for elevation in (74.9,75,75.1,85,89.9):
            self.assertEqual(screen_direction({**k,'elevation':elevation}),'BOTTOM')
            self.assertIn('BOTTOM edge',describe({**k,'elevation':elevation}))
        for orbit in range(-720,721,30):
            for elevation in (-85,-30,0,30,85):
                a={**k,'orbit':orbit,'elevation':elevation}
                self.assertEqual(screen_direction(a),screen_direction({**a,'orbit':orbit+360}))

    def test_projection_ignores_translation_distance_and_lens(self):
        k={**self.state()['keys'][0],'orbit':90,'elevation':45}
        self.assertEqual(screen_direction(k),screen_direction({**k,'target':[3,2,-1],'distance':12,'fov':80}))
        self.assertEqual(screen_direction({**k,'orbit':0,'elevation':85},(1,0,0)),'RIGHT')

    def test_overhead_to_profile_node_output_and_actions(self):
        s=self.state();a=s['keys'][0]
        s['keys']=[{**a,'t':0,'elevation':85},{**a,'t':2.5},{**a,'t':5.125,'orbit':90,'distance':2.8}]
        s.update(frames=124,fps=24)
        result=H3CameraPrompt().generate(json.dumps(s),'She sits and drinks coffee.','Identity.',False,'Quiet.','None.')
        combined,camera=result['result']
        self.assertEqual(result['ui']['text'],[camera])
        self.assertIn('only 5 degrees away from straight down',camera)
        self.assertIn('facial/front side is toward the BOTTOM edge',camera)
        self.assertIn('nose pointing toward the LEFT edge',camera)
        self.assertIn('She sits and drinks coffee.',combined)
        self.assertNotIn('She sits',camera)
        self.assertNotIn('<Video 1>',combined)

    def test_waypoint_limit_and_invalid_duration(self):
        for orbit in (1e300,100000):
            with self.assertRaisesRegex(ValueError,'Too many camera waypoints'):
                compile_camera(self.state(orbit=orbit),49,24)
        for frames,fps in [(1.5,24),(True,24),(49,float('nan')),(49,float('inf'))]:
            with self.assertRaises(ValueError):compile_camera(self.state(),frames,fps)

if __name__=='__main__':unittest.main()
