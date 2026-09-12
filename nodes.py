import json
from pathlib import Path
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
        }, "optional": {
            "subject_shape": (["mannequin", "ball"], {"default": "mannequin"}),
            "floor_cues": (["plain", "markers"], {"default": "plain"}),
            "source_mode": (["render", "reuse_video"], {"default": "render"}),
            "video_path": ("STRING", {"default": "", "tooltip": "Reuse mode: local absolute path or ComfyUI input/output annotated filename. No rendering; source dimensions, frames and fps are preserved."}),
            "existing_video": ("VIDEO",),
        }}

    RETURN_TYPES = ("IMAGE", "VIDEO", "FLOAT", "STRING")
    RETURN_NAMES = ("rgb_frames", "video", "fps", "camera_json")
    FUNCTION = "generate"
    CATEGORY = "H3/Camera Guide"
    DESCRIPTION = "Local 3D camera keyframes to clean RGB frames / VIDEO. Connect rgb_frames to H3 ref_videos.ref_video_0 at 24 fps."

    @staticmethod
    def resolve_video_path(value):
        import folder_paths
        value = value.strip().strip('"')
        if not value:
            raise ValueError("Reuse video: select an existing_video input or enter video_path.")
        path = Path(value) if Path(value).is_absolute() else Path(folder_paths.get_annotated_filepath(value))
        if not path.is_file():
            raise ValueError(f"Reuse video file does not exist: {path}")
        return path.resolve()

    @classmethod
    def IS_CHANGED(cls, source_mode="render", video_path="", existing_video=None, **kwargs):
        if source_mode == "reuse_video" and existing_video is None:
            p = cls.resolve_video_path(video_path)
            stat = p.stat()
            return f"{p}:{stat.st_size}:{stat.st_mtime_ns}"
        return "inputs"

    def generate(self, camera_state, width, height, frames, fps, subject_shape="mannequin",
                 floor_cues="plain", source_mode="render", video_path="", existing_video=None):
        from comfy_api.latest import InputImpl, Types
        from comfy.utils import ProgressBar
        import comfy.model_management
        if source_mode == "reuse_video":
            video = existing_video if existing_video is not None else InputImpl.VideoFromFile(str(self.resolve_video_path(video_path)))
            w, h = video.get_dimensions()
            count = video.get_frame_count()
            if not 1 <= count <= 720 or w*h*count > 180_000_000:
                raise ValueError("Reuse video exceeds 720 frames / 180 million pixels, or has unknown frame count. Trim it first.")
            components = video.get_components()
            images = components.images[..., :3]
            source_fps = float(components.frame_rate)
            if images.shape[0] < 1 or not 0 < source_fps <= 240:
                raise ValueError("Invalid source video frame count or fps")
            info = {"source_mode": "reuse_video", "width": w, "height": h,
                    "frames": images.shape[0], "fps": source_fps, "camera_state": None}
            if existing_video is None:
                import av
                from .camera_prompt import saved_trajectory
                try:
                    path = self.resolve_video_path(video_path)
                    with av.open(str(path)) as container:
                        info['camera_state'] = saved_trajectory(container.metadata,path.name,w,h,images.shape[0],source_fps)
                except (ValueError, KeyError, TypeError):
                    pass  # Reuse is still valid; prompt compilation rejects unknown trajectories.
            return images, video, source_fps, json.dumps(info)
        if source_mode != "render":
            raise ValueError("Unknown source_mode")
        if subject_shape not in ("mannequin", "ball") or floor_cues not in ("plain", "markers"):
            raise ValueError("Unknown subject shape or floor cues")
        state = parse_state(camera_state)
        if not (64 <= width <= 1920 and 64 <= height <= 1920 and 1 <= frames <= 720 and 1 <= fps <= 60):
            raise ValueError("Render parameters out of bounds")
        if width*height*frames > 180_000_000:
            raise ValueError("MVP memory limit: width * height * frames must be <= 180 million. Reduce resolution or duration.")
        bar = ProgressBar(frames)
        def progress(n):
            comfy.model_management.throw_exception_if_processing_interrupted()
            bar.update_absolute(n)
        images = torch.from_numpy(render_sequence(state,width,height,frames,fps,progress,
                                                  subject_shape=subject_shape, floor_cues=floor_cues))
        video = InputImpl.VideoFromComponents(Types.VideoComponents(images=images,frame_rate=Fraction(str(fps))),bit_depth=8)
        return images, video, float(fps), json.dumps({**state, "frames": frames, "fps": float(fps), "source_mode": "render"})


NODE_CLASS_MAPPINGS = {"H3CameraGuide": H3CameraGuide}
NODE_DISPLAY_NAME_MAPPINGS = {"H3CameraGuide": "H3 3D Camera Guide"}
