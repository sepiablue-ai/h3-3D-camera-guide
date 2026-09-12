"""CPU-only trajectory-to-language compiler. No vision inference or subject actions."""
import json
import re
from .camera import parse_state, sample


def saved_trajectory(metadata, filename, width, height, frames, fps):
    """Recover only a matching native SaveVideo -> H3CameraGuide render, never a result video."""
    from pathlib import Path
    workflow = json.loads(metadata.get('prompt', '{}'))
    matches = []
    for save in workflow.values():
        if save.get('class_type') != 'SaveVideo':
            continue
        inputs = save.get('inputs', {})
        prefix = inputs.get('filename_prefix')
        link = inputs.get('video')
        if not isinstance(prefix,str) or not isinstance(link,list) or len(link)!=2 or link[1]!=1:
            continue
        if not re.fullmatch(re.escape(Path(prefix.replace('\\','/')).name)+r'_\d+_?', Path(filename).stem):
            continue
        guide = workflow.get(str(link[0]), {})
        if guide.get('class_type') != 'H3CameraGuide':
            continue
        g = guide.get('inputs', {})
        if g.get('source_mode','render') != 'render':
            continue
        if (g.get('width'),g.get('height'),g.get('frames')) != (width,height,frames) or abs(float(g.get('fps',0))-fps)>1e-6:
            continue
        matches.append(parse_state(g['camera_state']))
    return matches[0] if len(matches)==1 else None


def stamp(t):
    return f"{int(t)//60:02d}:{t%60:06.3f}"


def view(k):
    e = k['elevation']
    angle = 'near-vertical overhead, looking down' if e >= 75 else 'high-angle, looking down' if e > 15 else 'near-vertical underside, looking up' if e <= -75 else 'low-angle, looking up' if e < -15 else 'level with the aim point'
    return (f"{angle}; scene azimuth {k['orbit']:g} degrees, elevation {e:g} degrees, "
            f"distance {k['distance']:g} scene units, vertical FOV {k['fov']:g} degrees")


def compile_camera(camera_json, frames=None, fps=None):
    raw = json.loads(camera_json) if isinstance(camera_json, str) else camera_json
    if raw.get('source_mode') == 'reuse_video' and not raw.get('camera_state'):
        raise ValueError('Reused video has no verified trajectory. Supply its original camera keyframes; arbitrary video motion cannot be inferred by these rules.')
    frames = raw.get('frames', frames)
    fps = raw.get('fps', fps)
    if frames is None or fps is None:
        raise ValueError('Trajectory needs frames and fps metadata. Connect camera_json from the updated H3 Camera Guide.')
    state = parse_state(raw['camera_state'] if raw.get('source_mode') == 'reuse_video' else raw)
    if not 1 <= frames <= 720 or not 1 <= fps <= 60:
        raise ValueError('Invalid frame count or fps')
    end = (frames - 1) / fps
    times = sorted({0., end, *(k['t'] for k in state['keys'] if 0 < k['t'] < end)})
    lines = ['[Shot 1] One continuous camera take. The following trajectory controls only the camera.',
             'Coordinates describe the guide scene: +Y is up, +Z is scene-front, +X is scene-right; these are not instructions for a person to face or move in any direction.',
             f'At {stamp(0)}, the camera starts {view(sample(state, 0))}.']
    for ta, tb in zip(times, times[1:]):
        a, b = sample(state, ta), sample(state, tb)
        moves = []
        da, de, dd, df = (b[n]-a[n] for n in ('orbit','elevation','distance','fov'))
        if abs(da) > 1e-6:
            direction = '+Z toward +X' if da > 0 else '+Z toward -X'
            moves.append(f"the camera arcs around the aim point by {abs(da):g} degrees in the {direction} azimuth direction (unwrapped azimuth {a['orbit']:g} to {b['orbit']:g} degrees, including all full turns); this is camera travel around the scene, not an in-place pan")
        if abs(de) > 1e-6:
            moves.append(f"the camera {'rises' if de > 0 else 'descends'} along a vertical arc, changing elevation from {a['elevation']:g} to {b['elevation']:g} degrees while aiming at the specified point")
        if abs(dd) > 1e-6:
            moves.append(f"the camera {'pulls out' if dd > 0 else 'pushes in'} from {a['distance']:g} to {b['distance']:g} scene units from the aim point")
        if abs(df) > 1e-6:
            moves.append(f"the lens zooms {'out' if df > 0 else 'in'}, changing vertical FOV from {a['fov']:g} to {b['fov']:g} degrees")
        delta = [y-x for x,y in zip(a['target'],b['target'])]
        if any(abs(v) > 1e-6 for v in delta):
            moves.append(f"the camera rig and its aim point translate together from aim coordinates {a['target']} to {b['target']} in scene units, independently of any character movement")
        if moves:
            lines.append(f'From {stamp(ta)} to {stamp(tb)}, ' + '; simultaneously, '.join(moves) + f'. At {stamp(tb)}, the camera is {view(b)}.')
        else:
            lines.append(f'From {stamp(ta)} to {stamp(tb)}, hold the camera position, aim and lens fixed.')
    lines.append('Match these times. Between saved keyframes use smooth ease-in and ease-out (u*u*(3-2*u)); simultaneous position, aim and lens changes belong to the same take. Character pose and action are defined only by the scene description.')
    return '\n'.join(lines)


def compose(scene_prompt, identity_prompt, camera_text, use_reference_video, soundscape, music):
    # Fail visibly for common conflicts; do not delete or reinterpret user action text.
    conflict = re.search(r'(?i)\b(camera\s+(?:moves?|pans?|tilts?|arcs?|orbits?|zooms?|pushes|pulls|tracks|stays)|locked.off camera|static camera|camera movement)\b|カメラ(?:は|が|を|ワーク)|天井視点|俯瞰|ローアングル', scene_prompt)
    if conflict:
        raise ValueError('Scene prompt contains a camera instruction. Put camera direction in the 3D editor; keep character actions in scene_prompt. Found: '+conflict.group())
    if re.search(r'<Video\s+\d+>', scene_prompt + identity_prompt):
        raise ValueError('Video reference labels are managed by use_reference_video; remove them from scene/identity text.')
    if not scene_prompt.strip():
        raise ValueError('scene_prompt must not be empty')
    video_definition = '\n<Video 1> supplies camera viewpoint changes and timing only.' if use_reference_video else ''
    video_rule = ' Use <Video 1> only for the camera trajectory. Its proxy geometry, pose, action and appearance are not character instructions.' if use_reference_video else ''
    return (f'subject_definitions:\n{identity_prompt.strip()}{video_definition}\n\n'
            'summary:\n[reference generation] Create one continuous video with the scene action and camera trajectory specified below.\n\n'
            'retention_analysis:\nUse the pictures for the identity described above. The scene description controls character actions and setting; the camera trajectory controls viewpoint, lens and timing only.'+video_rule+'\n\n'
            f'detailed_description:\nScene description:\n{scene_prompt.strip()}\n\nCamera trajectory:\n{camera_text}\nDo not render camera rigs, paths, axes, grids, labels or editing UI.\n\n'
            f'overall_soundscape:\n{soundscape.strip()}\n\nnon_diegetic_music:\n{music.strip()}')


class H3CameraPrompt:
    @classmethod
    def INPUT_TYPES(cls):
        return {'required': {
            'camera_json': ('STRING', {'forceInput': True}),
            'scene_prompt': ('STRING', {'multiline':True,'default':'Render <Subject 1> sitting at a cafe table, calmly lifting a coffee cup and taking a sip. She wears a casual short-sleeve T-shirt and blue jeans. The cafe is warm and cozy.'}),
            'identity_prompt': ('STRING', {'multiline':True,'default':'<Subject 1> is the same adult woman shown in <Picture 1>, <Picture 2>, and <Picture 3>. Preserve her identity, face and hairstyle.'}),
            'use_reference_video': ('BOOLEAN', {'default':True}),
            'soundscape': ('STRING', {'default':'Quiet cafe ambience, faint background chatter and light cup sounds. No speech.','multiline':True}),
            'music': ('STRING', {'default':'None.'}),
        }}
    RETURN_TYPES = ('STRING','STRING')
    RETURN_NAMES = ('combined_prompt','camera_prompt')
    FUNCTION = 'generate'
    OUTPUT_NODE = True
    CATEGORY = 'H3/Camera Guide'
    DESCRIPTION = 'CPU rules for all saved camera segments. Scene text controls actions; trajectory text controls camera only. use_reference_video must match H3 video wiring.'

    def generate(self,camera_json,scene_prompt,identity_prompt,use_reference_video,soundscape,music):
        camera = compile_camera(camera_json)
        prompt = compose(scene_prompt,identity_prompt,camera,use_reference_video,soundscape,music)
        return {'ui':{'text':[camera]},'result':(prompt,camera)}
