import os
import base64
import requests
from typing import List, Dict
from pathlib import Path
import json
import re
from dotenv import load_dotenv

# Force load environment variables
load_dotenv(override=True)

class ImageAnalysisService:
    def __init__(self):
        # Get GROQ API key directly from environment
        self.api_key = os.getenv("GROQ_API_KEY")
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model_id = "meta-llama/llama-4-scout-17b-16e-instruct"  # Updated model
        
        # Debug output
        if self.api_key:
            print("✅ GROQ Llama 4 Scout Vision initialized for image analysis")
            print(f"   Model: {self.model_id}")
            print(f"   Using API key: {self.api_key[:20]}...")
        else:
            print("❌ GROQ_API_KEY not found in environment!")
            
            # Try to load from settings
            try:
                from app.config import settings
                if settings.GROQ_API_KEY:
                    self.api_key = settings.GROQ_API_KEY
                    print(f"✅ Loaded from settings: {self.api_key[:20]}...")
            except Exception as e:
                print(f"⚠️ Could not load from settings: {e}")
        
        if not self.api_key or len(self.api_key) < 10:
            print("⚠️ GROQ_API_KEY not properly set - image analysis disabled")
            print("   Get your key at: https://console.groq.com/keys")
            print("   Add to backend/.env file: GROQ_API_KEY=gsk_your_key_here")
    
    def encode_image_to_base64(self, image_path: str) -> str:
        """Convert image file to base64 string"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def analyze_outfit_image(self, image_path: str, gender: str) -> List[Dict]:
        """Analyze generated outfit image using GROQ Llama 4 Scout Vision"""
        
        if not self.api_key or len(self.api_key) < 10:
            print("⚠️ GROQ API key not available, using fallback items")
            return self._get_fallback_items(gender)
        
        try:
            # Check if file exists
            if not Path(image_path).exists():
                print(f"❌ Image file not found: {image_path}")
                return self._get_fallback_items(gender)
            
            print(f"🔍 Analyzing image with GROQ Llama 4 Scout Vision: {image_path}")
            
            # Encode image to base64
            base64_image = self.encode_image_to_base64(image_path)
            
            # Create prompt for Llama 4 Scout Vision
            prompt = f"""
Analyze this {gender} fashion outfit image and identify ALL visible clothing items.

For each item, provide:
- type: clothing category (shirt, pants, shoes, jacket, dress, skirt, blazer, sweater, hoodie, etc.)
- color: specific color (navy blue, light pink, beige, white, black, gray, etc.)
- description: brief 3-5 word description

Return ONLY a valid JSON array:
[
    {{"type": "shirt", "color": "white", "description": "cotton button-down shirt"}},
    {{"type": "pants", "color": "navy blue", "description": "slim fit chinos"}},
    {{"type": "shoes", "color": "brown", "description": "leather dress shoes"}}
]

List 3-6 items. Be accurate and specific.
"""
            
            # Call GROQ API with Llama 4 Scout Vision
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model_id,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 1024,
                "top_p": 1
            }
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"❌ GROQ API error: {response.status_code} - {response.text}")
                return self._get_fallback_items(gender)
            
            result = response.json()
            analysis_text = result['choices'][0]['message']['content']
            
            print(f"📝 GROQ Response: {analysis_text[:200]}...")
            
            # Extract JSON array from response
            json_match = re.search(r'\[.*\]', analysis_text, re.DOTALL)
            if json_match:
                items = json.loads(json_match.group())
                print(f"✅ Analyzed {len(items)} items from image")
                return items
            
            print("⚠️ Could not parse GROQ response, using fallback")
            return self._get_fallback_items(gender)
            
        except requests.exceptions.Timeout:
            print("❌ GROQ API request timed out")
            return self._get_fallback_items(gender)
        except Exception as e:
            print(f"❌ Image analysis failed: {e}")
            import traceback
            traceback.print_exc()
            return self._get_fallback_items(gender)
    
    def _get_fallback_items(self, gender: str) -> List[Dict]:
        """Fallback items based on gender"""
        if gender == "male":
            return [
                {"type": "shirt", "color": "white", "description": "casual cotton shirt"},
                {"type": "pants", "color": "navy blue", "description": "chino pants"},
                {"type": "shoes", "color": "brown", "description": "leather casual shoes"},
                {"type": "jacket", "color": "gray", "description": "casual blazer"}
            ]
        else:
            return [
                {"type": "top", "color": "pastel pink", "description": "summer blouse"},
                {"type": "skirt", "color": "beige", "description": "midi flare skirt"},
                {"type": "shoes", "color": "nude", "description": "block heel sandals"},
                {"type": "bag", "color": "tan", "description": "leather crossbody bag"}
            ]

# Singleton instance
_image_analysis_service = None

def get_image_analysis_service():
    global _image_analysis_service
    if _image_analysis_service is None:
        _image_analysis_service = ImageAnalysisService()
    return _image_analysis_service

# Initialize on import
image_analysis_service = get_image_analysis_service()
