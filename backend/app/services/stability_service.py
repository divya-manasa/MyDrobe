import requests
import base64
from pathlib import Path
from app.config import get_settings

settings = get_settings()

class StabilityService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_host = "https://api.stability.ai"
        self.engine_id = "stable-diffusion-xl-1024-v1-0"
    
    def generate_outfit_image(self, prompt: str) -> str:
        """Generate outfit image using Stability AI SDXL"""
        
        if not self.api_key or self.api_key.startswith("YOUR_"):
            print("⚠️ STABILITY_API_KEY not configured - using fallback")
            return self._get_fallback_image()
        
        enhanced_prompt = f"high quality fashion photography, {prompt}, professional studio lighting, detailed clothing textures, fashion magazine style, full body shot"
        
        try:
            response = requests.post(
                f"{self.api_host}/v1/generation/{self.engine_id}/text-to-image",
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                },
                json={
                    "text_prompts": [
                        {
                            "text": enhanced_prompt,
                            "weight": 1
                        },
                        {
                            "text": "blurry, bad quality, distorted, ugly, low resolution, deformed",
                            "weight": -1
                        }
                    ],
                    "cfg_scale": 7,
                    "height": 1344,
                    "width": 768,
                    "samples": 1,
                    "steps": 30,
                }
            )
            
            if response.status_code != 200:
                print(f"❌ Stability AI Error: {response.status_code} - {response.text}")
                return self._get_fallback_image()
            
            data = response.json()
            
            for i, image in enumerate(data["artifacts"]):
                image_data = base64.b64decode(image["base64"])
                
                uploads_dir = Path("uploads/generated")
                uploads_dir.mkdir(parents=True, exist_ok=True)
                
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"outfit_{timestamp}.png"
                filepath = uploads_dir / filename
                
                with open(filepath, "wb") as f:
                    f.write(image_data)
                
                print(f"✅ Image saved: {filepath}")
                return f"/uploads/generated/{filename}"
            
            return self._get_fallback_image()
            
        except Exception as e:
            print(f"❌ Stability AI generation failed: {e}")
            import traceback
            traceback.print_exc()
            return self._get_fallback_image()
    
    def _get_fallback_image(self) -> str:
        return "https://images.unsplash.com/photo-1483985988355-763728e1935b?w=768&h=1344&fit=crop"

# Singleton instance
_stability_service = None

def get_stability_service():
    global _stability_service
    if _stability_service is None:
        api_key = settings.STABILITY_API_KEY
        if not api_key:
            print("⚠️ STABILITY_API_KEY not found in environment")
        _stability_service = StabilityService(api_key or "")
    return _stability_service
