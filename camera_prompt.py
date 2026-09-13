"""CPU-only trajectory-to-language compiler. No vision inference or subject actions."""
import json
import math
import re
from .camera import parse_state, sample, basis


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


def dot(a, b):
    return sum((x * y for x, y in zip(a, b)))

def screen_direction(k, reference_forward=(0, 0, 1)):
    """Project the reference front into the displayed image, with +y downward. Near-degenerate projections have no invented bearing."""
    norm = math.sqrt(dot(reference_forward, reference_forward))
    if not math.isfinite(norm) or norm < 1e-09:
        raise ValueError('Invalid reference forward vector')
    f = [v / norm for v in reference_forward]
    _, right, up, _ = basis(k)
    x = dot(f, right)
    y = -dot(f, up)
    if math.hypot(x, y) < 0.08:
        return None
    index = int(math.floor((math.atan2(y, x) + math.pi / 8) / (math.pi / 4))) % 8
    return ['RIGHT', 'BOTTOM-RIGHT', 'BOTTOM', 'BOTTOM-LEFT', 'LEFT', 'TOP-LEFT', 'TOP', 'TOP-RIGHT'][index]

def describe(k, reference_forward=(0, 0, 1)):
    """Describe composition relative to a fixed orientation anchor, never an actor turn."""
    f = list(reference_forward)
    norm = math.sqrt(dot(f, f))
    f = [v / norm for v in f]
    pos, _, _, _ = basis(k)
    to_camera = [pos[i] - k['target'][i] for i in range(3)]
    horiz = math.hypot(to_camera[0], to_camera[2])
    facing = (to_camera[0] * f[0] + to_camera[2] * f[2]) / max(horiz * math.hypot(f[0], f[2]), 1e-09)
    el = k['elevation']
    angle = abs(el)
    direction = screen_direction(k, f)
    if angle >= 75:
        text = f'a near-vertical overhead shot, only {90 - angle:g} degrees away from straight down, showing the crown and surrounding ground' if el > 0 else f'a near-vertical upward shot, only {90 - angle:g} degrees away from straight up'
    else:
        text = f'a downward-looking view from {angle:g} degrees above horizontal' if el > 5 else f'an upward-looking view from {angle:g} degrees below horizontal' if el < -5 else 'a horizontal view, without looking down or up'
        text += '; ' + ('a frontal view' if facing > 0.966 else 'a rear view' if facing < -0.966 else 'a side-profile view' if abs(facing) < 0.259 else 'a front three-quarter view' if facing > 0 else 'a rear three-quarter view')
    if direction:
        if abs(facing) < 0.259 and angle < 75:
            text += f'; the camera image shows the nose pointing toward the {direction} edge of the displayed image'
        elif angle >= 75:
            text += f'; in this image the facial/front side is toward the {direction} edge, and the back-of-head side is opposite'
        else:
            text += f'; the reference front direction projects toward the {direction} edge of the displayed image'
    return text

def compile_projected(state, frames=124, fps=24, reference_forward=(0, 0, 1)):
    """Describe sampled views along the real smoothstep path. Added waypoints preserve full turns; reject excessive prompt sizes before allocating them."""
    state = parse_state(state)
    if len(reference_forward) != 3 or not all((math.isfinite(v) for v in reference_forward)) or abs(reference_forward[1]) > 1e-06 or (math.hypot(reference_forward[0], reference_forward[2]) < 1e-09):
        raise ValueError('Reference front must be a finite horizontal heading in the current Y-up editor')
    if frames < 1 or fps <= 0:
        raise ValueError('Invalid output duration')
    end = (frames - 1) / fps
    times = sorted({0.0, end, *(k['t'] for k in state['keys'] if 0 < k['t'] < end)})
    extra = []
    for ta, tb in zip(times, times[1:]):
        a, b = (sample(state, ta), sample(state, tb))
        steps = max(1, math.ceil(abs(b['orbit'] - a['orbit']) / 60))
        if steps > 80:
            raise ValueError('Too many camera waypoints for a readable prompt; split the shot')
        extra.extend((ta + (tb - ta) * j / steps for j in range(1, steps)))
    times = sorted(set(times + extra))
    if len(times) > 80:
        raise ValueError('Too many camera waypoints for a readable prompt; split the shot')
    lines = ["[Shot 1] One continuous camera take, without cuts. All image-edge directions below describe the camera composition, not commands for the character to turn or change pose. The orientation anchor is the subject's reference front. Keep the independently specified scene action."]
    for i, t in enumerate(times):
        k = sample(state, t)
        lines.append(f"At {t:.3f} seconds: {describe(k, reference_forward)}. Camera distance from the aim point is {k['distance']:g} scene units; vertical field of view is {k['fov']:g} degrees.")
        if i == len(times) - 1:
            break
        b = sample(state, times[i + 1])
        moves = []
        if k['orbit'] != b['orbit'] or k['elevation'] != b['elevation']:
            moves.append('travel along the camera arc through the ordered views above and below, keeping the aim point in view')
        if k['distance'] != b['distance']:
            moves.append(f"physically {('push in' if b['distance'] < k['distance'] else 'pull back')} from distance {k['distance']:g} to {b['distance']:g}")
        if k['fov'] != b['fov']:
            moves.append(f"change vertical field of view from {k['fov']:g} to {b['fov']:g} degrees")
        if k['target'] != b['target']:
            moves.append(f"translate the camera rig and its aim point together from {k['target']} to {b['target']} in scene coordinates, independently of the actor")
        lines.append(f'From {t:.3f} to {times[i + 1]:.3f} seconds, ' + ('; simultaneously, '.join(moves) if moves else 'hold camera position, aim and lens fixed') + '.')
    lines.append('Preserve the saved smooth ease-in/ease-out timing. When the field of view is unchanged, move the camera physically rather than zooming. Do not rotate the picture to fake the camera move.')
    return '\n'.join(lines)


def compile_camera(camera_json, frames=None, fps=None):
    raw = json.loads(camera_json) if isinstance(camera_json, str) else camera_json
    if raw.get('source_mode') == 'reuse_video' and not raw.get('camera_state'):
        raise ValueError('Reused video has no verified trajectory. Supply its original camera keyframes; arbitrary video motion cannot be inferred by these rules.')
    frames = raw.get('frames', frames)
    fps = raw.get('fps', fps)
    if frames is None or fps is None:
        raise ValueError('Trajectory needs frames and fps metadata. Connect camera_json from the updated H3 Camera Guide.')
    state = parse_state(raw['camera_state'] if raw.get('source_mode') == 'reuse_video' else raw)
    if (not isinstance(frames, (int, float)) or isinstance(frames, bool)
            or not math.isfinite(frames) or not float(frames).is_integer()
            or not isinstance(fps, (int, float)) or isinstance(fps, bool)
            or not math.isfinite(fps) or not 1 <= frames <= 720 or not 1 <= fps <= 60):
        raise ValueError('Invalid frame count or fps')
    return compile_projected(state, frames, fps)


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
