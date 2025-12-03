#gemini-2.0-flash
import base64
import json
import time
from io import BytesIO
from PIL import Image
import google.generativeai as genai
from app.config import get_settings

settings = get_settings()


class GroqService:
    def __init__(self):
        # Configure Google Gemini
        api_key = settings.GEMINI_API_KEY
        if not api_key or api_key == "YOUR_GEMINI_API_KEY_HERE":
            print("\n" + "=" * 80)
            print("⚠️  GEMINI_API_KEY NOT CONFIGURED!")
            print("=" * 80)
            print("Get free key: https://makersuite.google.com/app/apikey")
            print("Add to backend/.env: GEMINI_API_KEY=your_key")
            print("=" * 80 + "\n")
            self.vision_model = None
        else:
            try:
                genai.configure(api_key=api_key)
                self.vision_model = genai.GenerativeModel("gemini-2.0-flash")
                print(f"✅ Google Gemini Vision initialized")
            except Exception as e:
                print(f"❌ Gemini init failed: {e}")
                self.vision_model = None

        print(f"📸 Using: Google gemini-2.0-flash (Vision)")

    def detect_clothing_from_image(self, image_base64: str) -> dict:
        """Detect clothing using Google Gemini Vision"""

        if not self.vision_model:
            print("❌ Gemini not initialized")
            return self._fallback()

        prompt = """You are an expert fashion analyst. Analyze this clothing image in detail.

Identify and return ONLY a valid JSON object with these exact fields:

{
    "item_name": "Descriptive name (e.g., 'Burgundy Silk Anarkali Dress', 'Navy Cotton Shirt')",
    "category": "Main category - choose from: Tops, Bottoms, Dresses, Indian Traditional, Outerwear, Footwear, Accessories",
    "sub_category": "Specific type (e.g., shirt, kurta, kurti, anarkali, jeans, maxi dress, saree, lehenga)",
    "fabric": "Fabric material (e.g., cotton, silk, polyester, chiffon, georgette, denim)",
    "color": "Specific color shade (e.g., burgundy, navy blue, emerald green, mustard yellow)",
    "pattern": "Pattern type (e.g., solid, striped, floral, checkered, embroidered)",
    "style": "Fashion style (e.g., casual, formal, traditional, ethnic, festive, party)",
    "season": "Best season (e.g., spring, summer, fall, winter, all-season)",
    "gender": "Target gender - 'male' for men's wear (shirts, pants, jeans, suits, kurtas, sherwanis), 'female' for dresses, kurtis, sarees, lehengas, blouses, skirts, etc.",
    "occasions": ["List 2-3 occasions"]
}

Return ONLY the JSON object."""

        try:
            print(f"\n{'=' * 80}")
            print(f"🤖 Analyzing with Google Gemini Vision")
            print(f"{'=' * 80}")

            start = time.time()

            # Decode base64 to image
            image_data = base64.b64decode(image_base64)
            image = Image.open(BytesIO(image_data))

            # Generate response
            response = self.vision_model.generate_content([prompt, image])

            elapsed = time.time() - start
            result = response.text.strip()

            print(f"⏱️  Response time: {elapsed:.2f}s")
            print(f"📥 Raw response: {result[:300]}...")

            # Extract JSON
            if "{" in result and "}" in result:
                json_start = result.index("{")
                json_end = result.rindex("}") + 1
                json_str = result[json_start:json_end]
                detected = json.loads(json_str)

                required = [
                    "item_name",
                    "category",
                    "sub_category",
                    "fabric",
                    "color",
                    "pattern",
                    "style",
                    "season",
                    "gender",
                ]

                if all(field in detected for field in required):
                    print(f"✅ DETECTION SUCCESS!")
                    print(f"   📝 {detected['item_name']}")
                    print(f"   👤 Gender: {detected['gender']}")
                    print(f"   📂 {detected['category']} > {detected['sub_category']}")
                    print(f"   🎨 {detected['color']}")
                    print(f"{'=' * 80}\n")
                    return detected
                else:
                    missing = [f for f in required if f not in detected]
                    print(f"⚠️  Missing fields: {missing}")

                    if "gender" not in detected:
                        detected["gender"] = "female"

                    return detected if len(missing) <= 1 else self._fallback()

            else:
                print("⚠️  No JSON in response")
                return self._fallback()

        except Exception as e:
            print(f"❌ ERROR: {e}")
            import traceback

            traceback.print_exc()
            return self._fallback()

    def _fallback(self) -> dict:
        """Fallback when API fails"""
        print("⚠️  Using fallback detection")
        return {
            "item_name": "Clothing Item - Please Edit",
            "category": "Tops",
            "sub_category": "Please specify type",
            "fabric": "Please specify fabric",
            "color": "Please specify color",
            "pattern": "solid",
            "style": "casual",
            "season": "all-season",
            "gender": "female",
            "occasions": ["casual", "everyday"],
        }

    def analyze_barcode_receipt(self, text: str) -> dict:
        """Analyze barcode/receipt text"""
        if not self.vision_model:
            return self._fallback()

        prompt = f"""Extract clothing information from this text: {text}

Return ONLY JSON:
{{
    "item_name": "full item name",
    "category": "category",
    "sub_category": "type",
    "fabric": "fabric",
    "color": "color",
    "pattern": "pattern",
    "style": "style",
    "season": "season",
    "brand": "brand if found"
}}"""

        try:
            response = self.vision_model.generate_content(prompt)
            result = response.text.strip()

            if "{" in result and "}" in result:
                json_start = result.index("{")
                json_end = result.rindex("}") + 1
                return json.loads(result[json_start:json_end])

            return self._fallback()
        except Exception as e:
            print(f"❌ Barcode error: {e}")
            return self._fallback()

    def generate_usage_notification(
        self, item_name: str, days_unworn: int, usage_count: int
    ) -> str:
        """Generate usage notification"""
        if not self.vision_model:
            return f"You haven't worn '{item_name}' in {days_unworn} days."

        try:
            prompt = f"Generate a friendly 1-sentence notification: Item '{item_name}' has been unworn for {days_unworn} days (worn {usage_count} times total). Encourage wearing it or donating."

            response = self.vision_model.generate_content(prompt)
            return response.text.strip()
        except:
            return f"You haven't worn '{item_name}' in {days_unworn} days."

    def suggest_outfit_match(self, item_data: dict, wardrobe_items: list) -> dict:
        """Suggest outfit combinations"""
        if not self.vision_model:
            return {"suggestions": []}

        try:
            prompt = f"""Given this clothing item: {json.dumps(item_data)}

And these available wardrobe items: {json.dumps(wardrobe_items[:10])}

Suggest 3 outfit combinations. Return ONLY JSON:
{{
    "suggestions": [
        {{
            "name": "outfit name",
            "items": ["item_id1", "item_id2"],
            "occasion": "suitable occasion",
            "reasoning": "why this combination works"
        }}
    ]
}}"""

            response = self.vision_model.generate_content(prompt)
            result = response.text.strip()

            if "{" in result and "}" in result:
                json_start = result.index("{")
                json_end = result.rindex("}") + 1
                return json.loads(result[json_start:json_end])

            return {"suggestions": []}
        except:
            return {"suggestions": []}


groq_service = GroqService()
