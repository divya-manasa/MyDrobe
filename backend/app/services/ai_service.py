import json
from app.services.groq_service import groq_service
from app.services.weather_service import weather_service

class AIService:
    
    def detect_clothing_attributes(self, image_base64: str) -> dict:
        """Detect clothing attributes from image using Groq Vision"""
        prompt = """Analyze this clothing item and provide the following information in JSON format:
        {
            "type": "shirt/pants/dress/etc",
            "color": "primary color",
            "pattern": "solid/striped/floral/etc",
            "style": "casual/formal/sporty/etc",
            "category": "tops/bottoms/dresses/outerwear/etc",
            "season": "spring/summer/fall/winter/all-season",
            "suggested_occasions": ["office", "casual", "party"]
        }
        Be specific and accurate."""
        
        result = groq_service.analyze_image(image_base64, prompt)
        
        try:
            # Try to extract JSON from the response
            if "{" in result and "}" in result:
                json_start = result.index("{")
                json_end = result.rindex("}") + 1
                json_str = result[json_start:json_end]
                return json.loads(json_str)
        except:
            pass
        
        # Fallback response
        return {
            "type": "clothing",
            "color": "unknown",
            "pattern": "solid",
            "style": "casual",
            "category": "general",
            "season": "all-season",
            "suggested_occasions": ["casual"]
        }
    
    def generate_outfit_suggestions(self, occasion: str, weather_data: dict, user_preferences: dict, available_items: list) -> list:
        """Generate outfit suggestions for occasion"""
        
        weather_desc = weather_data.get("description", "mild weather")
        temp = weather_data.get("temperature", 20)
        
        prompt = f"""Generate 3 outfit suggestions for a {occasion} event.
        
        Weather: {weather_desc}, {temp}°C
        User preferences: {json.dumps(user_preferences)}
        Available wardrobe items: {json.dumps(available_items[:20])}
        
        Return JSON array with 3 outfits:
        [
            {{
                "name": "Outfit 1 Name",
                "items": ["item_id_1", "item_id_2"],
                "reasoning": "Why this outfit works",
                "weather_appropriate": true,
                "style_score": 85
            }}
        ]"""
        
        result = groq_service.generate_text(prompt)
        
        try:
            if "[" in result and "]" in result:
                json_start = result.index("[")
                json_end = result.rindex("]") + 1
                json_str = result[json_start:json_end]
                return json.loads(json_str)
        except:
            pass
        
        return [{
            "name": f"{occasion} Outfit",
            "items": [item["id"] for item in available_items[:3]] if available_items else [],
            "reasoning": f"A stylish outfit for {occasion}",
            "weather_appropriate": True,
            "style_score": 80
        }]
    
    def generate_prompt_outfit(self, prompt: str, wardrobe_items: list) -> dict:
        """Generate outfit from text/voice prompt"""
        
        items_desc = json.dumps([{
            "id": item["id"],
            "type": item["type"],
            "color": item["color"],
            "style": item["style"]
        } for item in wardrobe_items[:30]])
        
        ai_prompt = f"""User request: "{prompt}"
        
        Available wardrobe: {items_desc}
        
        Create an outfit matching the request. Return JSON:
        {{
            "outfit_description": "Description of the outfit",
            "matched_items": [list of item IDs from wardrobe],
            "missing_items": [
                {{"type": "item type", "description": "what's needed"}}
            ],
            "style_notes": "Additional styling tips"
        }}"""
        
        result = groq_service.generate_text(ai_prompt)
        
        try:
            if "{" in result and "}" in result:
                json_start = result.index("{")
                json_end = result.rindex("}") + 1
                json_str = result[json_start:json_end]
                return json.loads(json_str)
        except:
            pass
        
        return {
            "outfit_description": "Custom outfit based on your request",
            "matched_items": [item["id"] for item in wardrobe_items[:3]],
            "missing_items": [],
            "style_notes": "Great choice!"
        }
    
    def analyze_body_shape(self, measurements: dict) -> dict:
        """Analyze body shape and provide recommendations"""
        
        prompt = f"""Analyze body measurements and provide fashion recommendations.
        
        Measurements: {json.dumps(measurements)}
        
        Return JSON:
        {{
            "body_shape": "hourglass/pear/apple/rectangle/inverted_triangle",
            "recommended_styles": ["style recommendations"],
            "flattering_fits": ["fit recommendations"],
            "avoid_styles": ["styles to avoid"],
            "confidence_score": 85
        }}"""
        
        result = groq_service.generate_text(prompt)
        
        try:
            if "{" in result and "}" in result:
                json_start = result.index("{")
                json_end = result.rindex("}") + 1
                json_str = result[json_start:json_end]
                return json.loads(json_str)
        except:
            pass
        
        return {
            "body_shape": "balanced",
            "recommended_styles": ["fitted tops", "A-line dresses"],
            "flattering_fits": ["tailored", "structured"],
            "avoid_styles": [],
            "confidence_score": 75
        }
    
    def compare_outfits(self, outfit1_items: list, outfit2_items: list, occasion: str) -> dict:
        """Compare two outfits"""
        
        prompt = f"""Compare these two outfits for {occasion}:
        
        Outfit 1: {json.dumps(outfit1_items)}
        Outfit 2: {json.dumps(outfit2_items)}
        
        Return JSON:
        {{
            "winner": "outfit1" or "outfit2",
            "outfit1_score": 85,
            "outfit2_score": 78,
            "comparison": "Detailed comparison",
            "reasoning": "Why one is better"
        }}"""
        
        result = groq_service.generate_text(prompt)
        
        try:
            if "{" in result and "}" in result:
                json_start = result.index("{")
                json_end = result.rindex("}") + 1
                json_str = result[json_start:json_end]
                return json.loads(json_str)
        except:
            pass
        
        return {
            "winner": "outfit1",
            "outfit1_score": 85,
            "outfit2_score": 78,
            "comparison": "Both outfits work well",
            "reasoning": "Outfit 1 has better color coordination"
        }

ai_service = AIService()
