from PIL import Image
import os
from typing import Dict, Any

class ImageTool:
    @staticmethod
    def inspect_image(image_path: str) -> Dict[str, Any]:
        if not os.path.exists(image_path):
            return {"error": f"Image file not found: {image_path}"}
            
        try:
            with Image.open(image_path) as img:
                return {
                    "format": img.format,
                    "mode": img.mode,
                    "width": img.width,
                    "height": img.height,
                    "aspect_ratio": round(img.width / img.height, 2) if img.height else 0,
                    "file_size_kb": round(os.path.getsize(image_path) / 1024, 2)
                }
        except Exception as e:
            return {"error": f"Failed to inspect image: {e}"}
