from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
import os

from app.models.user import User
from app.database import get_db
from app.models.wardrobe import WardrobeItem
from app.services.stability_service import get_stability_service
from app.services.image_analysis_service import get_image_analysis_service

try:
    from serpapi import GoogleSearch
    SERP_ENABLED = True
except ImportError:
    SERP_ENABLED = False

router = APIRouter(prefix="/api/prompt-outfit", tags=["Prompt Outfit"])

SERP_API_KEY = os.getenv("SERPAPI_KEY", "")
INDIAN_STORES = ["myntra", "amazon.in", "flipkart", "ajio", "meesho"]

class OutfitRequest(BaseModel):
    prompt: str
    gender: str = "female"

@router.post("/generate")
def generate_outfit_with_sdxl(
    req: OutfitRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Complete outfit generation with image analysis and shopping"""
    
    prompt_text = req.prompt.strip()
    gender = req.gender.lower()
    
    # Add gender context to prompt
    gender_prefix = "men's fashion" if gender == "male" else "women's fashion"
    full_prompt = f"{gender_prefix}, {prompt_text}"
    
    print(f"\n🎨 Generating {gender} outfit for: {prompt_text}")
    
    # 1. Generate image with SDXL
    stability = get_stability_service()
    outfit_image_url = stability.generate_outfit_image(full_prompt)
    print(f"✅ Image URL: {outfit_image_url}")
    
    # 2. Analyze generated image
    analyzed_items = []
    if outfit_image_url.startswith("/uploads"):
        local_path = outfit_image_url.replace("/uploads/", "uploads/")
        analysis_service = get_image_analysis_service()
        analyzed_items = analysis_service.analyze_outfit_image(local_path, gender)
    
    # 3. Wardrobe matching
    wardrobe_items = db.query(WardrobeItem).filter(
        WardrobeItem.user_id == current_user.id
    ).all()
    
    matched_items = []
    missing_items = []
    
    for item in analyzed_items:
        match = next((w for w in wardrobe_items if
                     w.type and w.type.lower() == item['type'].lower() and
                     w.color and item['color'].lower() in w.color.lower()), None)
        
        matched_items.append({
            "name": item['description'],
            "type": item['type'],
            "color": item['color'],
            "available": bool(match)
        })
        
        if not match:
            missing_items.append(item)
    
    print(f"📦 Matched {len([m for m in matched_items if m['available']])} items")
    
    # 4. Shopping suggestions with SerpAPI
    shopping = []
    if SERP_ENABLED and SERP_API_KEY and missing_items:
        for item in missing_items[:3]:  # Top 3 missing items
            search_query = f"{item['color']} {item['type']} {gender}"
            
            try:
                params = {
                    "q": search_query,
                    "tbm": "shop",
                    "gl": "in",
                    "hl": "en",
                    "api_key": SERP_API_KEY
                }
                
                search = GoogleSearch(params)
                results = search.get_dict()
                shopping_results = results.get("shopping_results", [])
                
                # Filter for Indian stores and get top rated
                for prod in shopping_results[:15]:
                    source = prod.get("source", "").lower()
                    
                    # Check if from target stores
                    matched_store = next((store for store in INDIAN_STORES if store in source), None)
                    
                    if matched_store:
                        store_name = matched_store.title() if matched_store != "amazon.in" else "Amazon"
                        shopping.append({
                            "name": prod.get("title", "")[:60],
                            "store": store_name,
                            "price": prod.get("price", "Price not available"),
                            "rating": prod.get("rating", "N/A"),
                            "image": prod.get("thumbnail", outfit_image_url),
                            "url": prod.get("link", "#")
                        })
                        
                        if len(shopping) >= 6:  # Limit to 6 products
                            break
                    
                    if len(shopping) >= 6:
                        break
                        
            except Exception as e:
                print(f"SerpAPI error: {e}")
    
    # Fallback if no shopping results
    if not shopping:
        for item in missing_items[:3]:
            shopping.append({
                "name": f"{item['color'].title()} {item['type'].title()}",
                "store": "Google",
                "price": "Compare prices",
                "rating": "N/A",
                "image": outfit_image_url,
                "url": f"https://www.google.com/search?q={item['color']}+{item['type']}&tbm=shop"
            })
    
    print(f"🛍️ Found {len(shopping)} shopping suggestions")
    
    return {
        "outfit_image": outfit_image_url,
        "summary": f"AI-generated {gender} outfit for: {prompt_text}",
        "analyzed_items": analyzed_items,
        "matched_items": matched_items,
        "shopping": shopping
    }
@router.get("/test-vision")
def test_vision():
    """Test GROQ Llama Vision setup"""
    from app.services.image_analysis_service import get_image_analysis_service
    
    service = get_image_analysis_service()
    
    return {
        "groq_api_key_set": bool(service.api_key),
        "groq_api_key_preview": service.api_key[:20] + "..." if service.api_key else None,
        "model": "llama-3.2-90b-vision-preview",
        "status": "ready" if service.api_key else "not configured"
    }
