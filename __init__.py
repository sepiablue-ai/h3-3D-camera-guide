from .nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS
from .camera_prompt import H3CameraPrompt

NODE_CLASS_MAPPINGS['H3CameraPrompt'] = H3CameraPrompt
NODE_DISPLAY_NAME_MAPPINGS['H3CameraPrompt'] = 'H3 Camera Prompt / カメラ専用プロンプト'

WEB_DIRECTORY = "./web"
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
