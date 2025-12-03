from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
import os

from app.models.user import User
from app.routers.auth import get_current_user
from app.database import get_db
from app.models.wardrobe import WardrobeItem

try:
    from serpapi import GoogleSearch
    SERP_ENABLED = True
except ImportError:
    SERP_ENABLED = False
    print("⚠️ serpapi not installed - using fallback products")

router = APIRouter(prefix="/api/smart-shopping", tags=["Smart Shopping"])

SERP_API_KEY = os.getenv("SERP_API_KEY", "")

class ShoppingRequest(BaseModel):
    intent: str
    budget_min: Optional[int] = 500
    budget_max: Optional[int] = 5000
    style_preference: Optional[str] = "Casual"
    color_preference: Optional[str] = None
    sustainability: Optional[str] = "Normal"

@router.post("/recommend")
def get_smart_recommendations(
    req: ShoppingRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Smart Shopping Assistant with gap detection and recommendations"""
    
    print(f"\n🛍️ Smart Shopping Request: {req.intent}")
    
    # Default user preferences
    user_size = "M"
    body_shape = "Rectangle"
    
    # Get wardrobe inventory
    wardrobe = db.query(WardrobeItem).filter(
        WardrobeItem.user_id == current_user.id
    ).all()
    
    # Detect wardrobe gaps
    gaps = detect_wardrobe_gaps(wardrobe, req.intent)
    
    # Search products
    products = search_shopping_products(
        query=req.intent,
        budget_min=req.budget_min,
        budget_max=req.budget_max,
        color_preference=req.color_preference,
        sustainability=req.sustainability
    )
    
    # Score and rank products
    scored_products = []
    for prod in products[:8]:
        score = analyze_product_match(
            product=prod,
            wardrobe=wardrobe,
            body_shape=body_shape,
            style_preference=req.style_preference,
            color_preference=req.color_preference
        )
        scored_products.append({**prod, **score})
    
    scored_products.sort(key=lambda x: x['match_score'], reverse=True)
    
    return {
        "gaps": gaps,
        "recommendations": scored_products[:6],
        "user_context": {
            "size": user_size,
            "body_shape": body_shape,
            "style": req.style_preference,
            "budget": f"₹{req.budget_min} - ₹{req.budget_max}"
        }
    }

def detect_wardrobe_gaps(wardrobe: List[WardrobeItem], intent: str) -> List[str]:
    """Detect missing items in wardrobe"""
    gaps = []
    
    item_counts = {}
    for item in wardrobe:
        item_type = item.type.lower() if item.type else "unknown"
        item_counts[item_type] = item_counts.get(item_type, 0) + 1
    
    intent_lower = intent.lower()
    
    if "formal" in intent_lower or "office" in intent_lower:
        if item_counts.get("formal shoes", 0) == 0:
            gaps.append("You have formal wear but no matching formal shoes.")
        if item_counts.get("blazer", 0) == 0:
            gaps.append("Consider adding a blazer to complete your office wardrobe.")
    
    if "winter" in intent_lower or "coat" in intent_lower:
        if item_counts.get("jacket", 0) == 0 and item_counts.get("coat", 0) == 0:
            gaps.append("You are missing warm outerwear for winter.")
    
    if "accessories" in intent_lower:
        if item_counts.get("bag", 0) == 0:
            gaps.append("Your wardrobe lacks professional bags or accessories.")
    
    if not gaps:
        gaps.append("Your wardrobe is well-rounded! These items will add variety.")
    
    return gaps

def search_shopping_products(
    query: str,
    budget_min: int,
    budget_max: int,
    color_preference: Optional[str],
    sustainability: str
) -> List[dict]:
    """Search products using SerpAPI or fallback"""
    
    if not SERP_ENABLED or not SERP_API_KEY:
        return get_fallback_products(query, budget_min, budget_max)
    
    search_query = query
    if color_preference:
        search_query = f"{color_preference} {query}"
    if sustainability == "Eco-only":
        search_query = f"sustainable eco-friendly {query}"
    
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
        
        products = []
        for prod in results.get("shopping_results", [])[:20]:
            price_str = prod.get("extracted_price", prod.get("price", "0"))
            try:
                price = int(float(str(price_str).replace("₹", "").replace(",", "").strip()))
            except:
                price = 0
            
            if budget_min <= price <= budget_max:
                products.append({
                    "name": prod.get("title", "")[:80],
                    "brand": prod.get("source", "Online Store"),
                    "price": f"₹{price:,}",
                    "price_numeric": price,
                    "image": prod.get("thumbnail", "https://images.unsplash.com/photo-1549298916-b41d501d3772?w=300"),
                    "url": prod.get("link", "#"),
                    "rating": prod.get("rating", "4.0"),
                    "store": prod.get("source", "Store"),
                    "is_eco": "eco" in prod.get("title", "").lower() or "sustainable" in prod.get("title", "").lower()
                })
        
        if products:
            return products
        return get_fallback_products(query, budget_min, budget_max)
        
    except Exception as e:
        print(f"❌ SerpAPI error: {e}")
        return get_fallback_products(query, budget_min, budget_max)

def get_fallback_products(query: str, budget_min: int, budget_max: int) -> List[dict]:
    """Fallback products"""
    mid_price = (budget_min + budget_max) // 2
    return [
        {
            "name": f"{query.title()} - Classic Style",
            "brand": "Myntra",
            "price": f"₹{mid_price:,}",
            "price_numeric": mid_price,
            "image": "https://images.unsplash.com/photo-1549298916-b41d501d3772?w=300",
            "url": f"https://www.myntra.com/search?q={query}",
            "rating": "4.2",
            "store": "Myntra",
            "is_eco": False
        },
        {
            "name": f"{query.title()} - Premium",
            "brand": "Amazon",
            "price": f"₹{int(mid_price * 1.2):,}",
            "price_numeric": int(mid_price * 1.2),
            "image": "https://images.unsplash.com/photo-1549298916-b41d501d3772?w=300",
            "url": f"https://www.amazon.in/s?k={query}",
            "rating": "4.5",
            "store": "Amazon",
            "is_eco": False
        }
    ]

def analyze_product_match(
    product: dict,
    wardrobe: List[WardrobeItem],
    body_shape: str,
    style_preference: str,
    color_preference: Optional[str]
) -> dict:
    """Analyze product match score"""
    score = 70
    reasons = []
    
    if color_preference:
        if color_preference.lower() in product['name'].lower():
            score += 15
            reasons.append(f"Matches your {color_preference} preference")
    
    wardrobe_colors = [item.color for item in wardrobe if item.color]
    if any(color and color.lower() in product['name'].lower() for color in wardrobe_colors[:5]):
        score += 10
        reasons.append("Complements your wardrobe")
    
    if style_preference.lower() in product['name'].lower():
        score += 10
        reasons.append(f"Fits your {style_preference} style")
    
    if product.get('is_eco'):
        score += 15
        reasons.append("♻️ Eco-friendly option")
    
    try:
        rating = float(product.get('rating', 0))
        if rating >= 4.5:
            score += 5
            reasons.append("Highly rated")
    except:
        pass
    
    if not reasons:
        reasons.append("Good quality product")
    
    return {
        "match_score": min(score, 100),
        "match_reasons": reasons[:3],
        "recommendation": "Recommended" if score >= 75 else "Good option"
    }
