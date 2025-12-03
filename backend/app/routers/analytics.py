from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
import json
from app.database import get_db
from app.models.user import User
from app.models.wardrobe import WardrobeItem
from app.models.analytics import WearLog
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

@router.get("/dashboard")
def get_analytics_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive wardrobe analytics"""
    
    # Total items
    total_items = db.query(WardrobeItem).filter(WardrobeItem.user_id == current_user.id).count()
    
    # Most worn items
    most_worn = db.query(WardrobeItem).filter(
        WardrobeItem.user_id == current_user.id
    ).order_by(WardrobeItem.wear_count.desc()).limit(5).all()
    
    # Least worn items
    least_worn = db.query(WardrobeItem).filter(
        WardrobeItem.user_id == current_user.id,
        WardrobeItem.wear_count > 0
    ).order_by(WardrobeItem.wear_count.asc()).limit(5).all()
    
    # Never worn items
    never_worn = db.query(WardrobeItem).filter(
        WardrobeItem.user_id == current_user.id,
        WardrobeItem.wear_count == 0
    ).count()
    
    # Cost per wear analysis
    items_with_cost = db.query(WardrobeItem).filter(
        WardrobeItem.user_id == current_user.id,
        WardrobeItem.cost > 0,
        WardrobeItem.wear_count > 0
    ).all()
    
    cost_per_wear_items = []
    total_spent = 0
    total_wears = 0
    
    for item in items_with_cost:
        cpw = item.cost / item.wear_count
        cost_per_wear_items.append({
            "id": item.id,
            "name": item.name,
            "cost": item.cost,
            "wear_count": item.wear_count,
            "cost_per_wear": round(cpw, 2)
        })
        total_spent += item.cost
        total_wears += item.wear_count
    
    avg_cost_per_wear = total_spent / total_wears if total_wears > 0 else 0
    
    # Category distribution
    items = db.query(WardrobeItem).filter(WardrobeItem.user_id == current_user.id).all()
    category_dist = {}
    color_dist = {}
    season_dist = {}
    
    for item in items:
        # Categories
        cat = item.type or "Other"
        category_dist[cat] = category_dist.get(cat, 0) + 1
        
        # Colors
        color = item.color or "Unknown"
        color_dist[color] = color_dist.get(color, 0) + 1
        
        # Seasons
        season = item.season or "All-season"
        season_dist[season] = season_dist.get(season, 0) + 1
    
    # Eco score (based on wear frequency and longevity)
    eco_score = 0
    if total_items > 0:
        avg_wear_count = sum(item.wear_count for item in items) / total_items
        eco_score = min(100, int(avg_wear_count * 10))
    
    return {
        "summary": {
            "total_items": total_items,
            "never_worn": never_worn,
            "total_spent": round(total_spent, 2),
            "avg_cost_per_wear": round(avg_cost_per_wear, 2),
            "eco_score": eco_score
        },
        "most_worn": [
            {
                "id": item.id,
                "name": item.name,
                "wear_count": item.wear_count,
                "color": item.color
            }
            for item in most_worn
        ],
        "least_worn": [
            {
                "id": item.id,
                "name": item.name,
                "wear_count": item.wear_count,
                "days_since_worn": (datetime.now() - item.last_worn).days if item.last_worn else 0
            }
            for item in least_worn
        ],
        "cost_per_wear": sorted(cost_per_wear_items, key=lambda x: x["cost_per_wear"])[:10],
        "category_distribution": category_dist,
        "color_distribution": color_dist,
        "season_distribution": season_dist
    }

@router.get("/insights")
def get_ai_insights(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get AI-generated wardrobe insights"""
    
    from app.services.groq_service import groq_service
    
    # Get analytics data
    items = db.query(WardrobeItem).filter(WardrobeItem.user_id == current_user.id).all()
    
    if not items:
        return {"insights": ["Start building your wardrobe to get personalized insights!"]}
    
    # Prepare data for AI
    summary = {
        "total_items": len(items),
        "categories": {},
        "colors": {},
        "wear_patterns": []
    }
    
    for item in items:
        cat = item.type or "other"
        summary["categories"][cat] = summary["categories"].get(cat, 0) + 1
        
        color = item.color or "unknown"
        summary["colors"][color] = summary["colors"].get(color, 0) + 1
        
        if item.wear_count > 0:
            summary["wear_patterns"].append({
                "name": item.name,
                "count": item.wear_count
            })
    
    prompt = f"""Analyze this wardrobe data: {json.dumps(summary)}
    
    Provide 5 actionable insights and recommendations. Return as JSON array:
    [
        {{"insight": "Your insight here", "action": "Recommended action"}}
    ]"""
    
    result = groq_service.generate_text(prompt)
    
    try:
        if "[" in result and "]" in result:
            json_start = result.index("[")
            json_end = result.rindex("]") + 1
            insights = json.loads(result[json_start:json_end])
        else:
            insights = []
    except:
        insights = [
            {"insight": "Your wardrobe is growing!", "action": "Keep adding versatile pieces"}
        ]
    
    return {"insights": insights}
