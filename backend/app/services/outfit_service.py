import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import google.generativeai as genai
from app.config import get_settings

settings = get_settings()

class OutfitSuggestionService:
    def __init__(self):
        # Configure Gemini (more reliable than Groq for this use case)
        api_key = settings.GEMINI_API_KEY
        if api_key and api_key != "YOUR_GEMINI_API_KEY_HERE":
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            print("✅ Gemini AI initialized for outfit suggestions")
        else:
            self.model = None
            print("⚠️ Gemini API not configured")
    
    def generate_outfit_suggestions(
        self,
        event_type: str,
        event_date: str,
        event_time: str,
        formality: str,
        city: str,
        country: str,
        wardrobe_items: List[Dict],
        weather: Dict,
        user_preferences: Dict,
        avoid_days: int = 7
    ) -> str:
        """
        Generate beautiful outfit suggestions with NO JSON output
        Returns formatted text for UI display
        """
        
        if not self.model:
            return self._fallback_response()
        
        # Filter out recently worn items
        available_items = self._filter_recent_items(wardrobe_items, avoid_days)
        
        if len(available_items) < 3:
            return "❌ You need at least 3 items in your wardrobe to get outfit suggestions. Please add more items first! 🛍️"
        
        # Build the prompt
        prompt = self._build_beautiful_prompt(
            event_type, event_date, event_time, formality,
            city, country, available_items, weather, user_preferences, avoid_days
        )
        
        try:
            print(f"\n{'='*80}")
            print(f"🎨 Generating outfit suggestions with Gemini AI")
            print(f"{'='*80}")
            
            response = self.model.generate_content(prompt)
            result = response.text.strip()
            
            print(f"✅ Generated outfit suggestions successfully")
            print(f"{'='*80}\n")
            
            return result
            
        except Exception as e:
            print(f"❌ Error generating suggestions: {e}")
            return self._fallback_response()
    
    def _filter_recent_items(self, items: List[Dict], avoid_days: int) -> List[Dict]:
        """Filter out items worn within avoid_days"""
        cutoff_date = datetime.now() - timedelta(days=avoid_days)
        
        filtered = []
        for item in items:
            if not item.get('last_worn'):
                filtered.append(item)
            else:
                try:
                    last_worn = datetime.fromisoformat(item['last_worn'].replace('Z', '+00:00'))
                    if last_worn < cutoff_date:
                        filtered.append(item)
                except:
                    filtered.append(item)
        
        return filtered if filtered else items  # Return all if nothing available
    
    def _build_beautiful_prompt(
        self, event_type, event_date, event_time, formality,
        city, country, items, weather, preferences, avoid_days
    ) -> str:
        """Build prompt for beautiful UI-friendly output"""
        
        # Format wardrobe items
        wardrobe_text = "\n".join([
            f"- {item['name']} (ID: {item['id']}, Type: {item['type']}, Color: {item['color']}, "
            f"Pattern: {item['pattern']}, Style: {item['style']}, Fabric: {item.get('fabric', 'unknown')}, "
            f"Season: {item['season']}, Gender: {item['gender']}, Worn: {item['wear_count']} times)"
            for item in items[:50]  # Limit to prevent token overflow
        ])
        
        prompt = f"""You are a world-class fashion stylist AI. Create THREE stunning outfit suggestions for a user's upcoming event.

## EVENT DETAILS
📅 Event Type: {event_type.upper()}
🗓️ Date: {event_date}
⏰ Time: {event_time}
🎩 Formality: {formality}
📍 Location: {city}, {country}

## WEATHER CONDITIONS
🌡️ Temperature: {weather.get('temperature_celsius', 25)}°C (feels like {weather.get('feels_like', 28)}°C)
☁️ Condition: {weather.get('condition', 'partly cloudy')}
💧 Humidity: {weather.get('humidity_percent', 70)}%
🌧️ Rain Chance: {weather.get('rain_probability', 20)}%
🌅 Season: {weather.get('season', 'summer')}
☀️ UV Index: {weather.get('uv_index', 5)}

## USER'S WARDROBE (Available Items)
{wardrobe_text}

## USER STYLE PREFERENCES
- Preferred Colors: {', '.join(preferences.get('preferred_colors', ['any color']))}
- Disliked Colors: {', '.join(preferences.get('disliked_colors', ['none']))}
- Style Profile: {preferences.get('style_profile', 'casual')}
- Body Shape: {preferences.get('body_shape', 'average')}
- Preferred Styles: {', '.join(preferences.get('preferred_styles', ['casual']))}

## IMPORTANT RULES
- Do NOT use items worn in the last {avoid_days} days
- Create COMPLETE outfits (top + bottom + optional accessories/shoes)
- Match items by color, style, and occasion
- Consider weather appropriateness
- Use ONLY items from the wardrobe above
- If essential items are missing, clearly state them

## OUTPUT FORMAT (CRITICAL - NO JSON!)

Write your response EXACTLY like this beautiful fashion app UI:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ YOUR EVENT: {event_type.upper()} ✨

{event_date} at {event_time} • {city}, {country}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🌤️ WEATHER & TRENDS

[Write 1-2 sentences about the weather and any relevant seasonal/fashion trends]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💫 OUTFIT #1: [Creative Outfit Name]

🎨 Visual Style: [Describe the overall look in 1 sentence]

👕 OUTFIT ITEMS:
✅ [Item Name from wardrobe] (ID: X)
✅ [Item Name from wardrobe] (ID: Y)
❌ MISSING: [Description of missing item, if any]

💭 Why This Works:
[2-3 sentences explaining why this outfit is perfect for the event, weather, and style]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💫 OUTFIT #2: [Creative Outfit Name]

🎨 Visual Style: [Describe the overall look in 1 sentence]

👕 OUTFIT ITEMS:
✅ [Item Name from wardrobe] (ID: X)
✅ [Item Name from wardrobe] (ID: Y)
❌ MISSING: [Description of missing item, if any]

💭 Why This Works:
[2-3 sentences explaining why this outfit is perfect]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💫 OUTFIT #3: [Creative Outfit Name]

🎨 Visual Style: [Describe the overall look in 1 sentence]

👕 OUTFIT ITEMS:
✅ [Item Name from wardrobe] (ID: X)
✅ [Item Name from wardrobe] (ID: Y)
❌ MISSING: [Description of missing item, if any]

💭 Why This Works:
[2-3 sentences explaining why this outfit is perfect]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 STYLING TIPS FOR YOU

• [Tip 1 based on body shape and weather]
• [Tip 2 based on preferred colors]
• [Tip 3 based on event type]
• [Tip 4 based on season/weather]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

REMEMBER:
- Keep tone warm, friendly, and stylish
- Use emojis to make it visually appealing
- Be specific about which wardrobe items to use (include ID numbers)
- Clearly mark missing items with ❌
- Make it feel like a premium fashion app experience
- NO JSON, NO technical formatting
- Each outfit should feel distinct and special"""

        return prompt
    
    def _fallback_response(self) -> str:
        """Fallback if AI is unavailable"""
        return """━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ AI OUTFIT SUGGESTIONS TEMPORARILY UNAVAILABLE

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

We're having trouble connecting to our AI stylist right now. 
Please try again in a few moments!

In the meantime, try browsing your wardrobe and mixing:
• A neutral top with colorful bottoms
• Monochrome looks for elegance
• Layering pieces for versatility

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

outfit_service = OutfitSuggestionService()
