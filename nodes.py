import json
from fractions import Fraction
import torch
from .camera import DEFAULT, parse_state
from .renderer import render_sequence


class H3CameraGuide:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "camera_state": ("STRING", {"default": json.dumps(DEFAULT), "multiline": True}),
            "width": ("INT", {"default": 576, "min": 64, "max": 1920, "step": 8}),
            "height": ("INT", {"default": 1024, "min": 64, "max": 1920, "step": 8}),
            "frames": ("INT", {"default": 124, "min": 1, "max": 720}),
            "fps": ("FLOAT", {"default": 24.0, "min": 1.0, "max": 60.0, "step": 1.0}),
        }}

    RETURN_TYPES = ("IMAGE", "VIDEO", "FLOAT", "STRING")
    RETURN_NAMES = ("rgb_frames", "video", "fps", "camera_json")
    FUNCTION = "generate"
    CATEGORY = "H3/Camera Guide"
    DESCRIPTION = "Local 3D camera keyframes to clean RGB frames / VIDEO. Connect rgb_frames to H3 ref_videos.ref_video_0 at 24 fps."

    def generate(self, camera_state, width, height, frames, fps):
        from comfy_api.latest import InputImpl, Types
        from comfy.utils import ProgressBar
        import comfy.model_management
        state = parse_state(camera_state)
        if not (64 <= width <= 1920 and 64 <= height <= 1920 and 1 <= frames <= 720 and 1 <= fps <= 60):
            raise ValueError("Render parameters out of bounds")
        if width*height*frames > 180_000_000:
            raise ValueError("MVP memory limit: width * height * frames must be <= 180 million. Reduce resolution or duration.")
        bar = ProgressBar(frames)
        def progress(n):
            comfy.model_management.throw_exception_if_processing_interrupted()
            bar.update_absolute(n)
        images = torch.from_numpy(render_sequence(state,width,height,frames,fps,progress))
        video = InputImpl.VideoFromComponents(Types.VideoComponents(images=images,frame_rate=Fraction(str(fps))),bit_depth=8)
        return images, video, float(fps), json.dumps(state)


NODE_CLASS_MAPPINGS = {"H3CameraGuide": H3CameraGuide}
NODE_DISPLAY_NAME_MAPPINGS = {"H3CameraGuide": "H3 3D Camera Guide"}
