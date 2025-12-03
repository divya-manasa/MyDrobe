# backend/app/routers/outfit.py
# ✅ NO AUTHENTICATION - WORKS DIRECTLY

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import json

from app.database import get_db
from app.models.user import User
from app.models.wardrobe import WardrobeItem, Category
from app.services.outfit_service import outfit_service

router = APIRouter(prefix="/api/outfit", tags=["Outfit Suggestions"])

@router.get("/suggest")
async def suggest_outfits(
    event_type: str = Query(...),
    event_date: str = Query(...),
    event_time: str = Query(...),
    formality: str = Query(default="casual"),
    city: str = Query(default="Mumbai"),
    country: str = Query(default="India"),
    avoid_days: int = Query(default=7),
    gender: str = Query(default="unisex"),
    user_id: int = Query(default=1),  # Optional: can pass user_id or use default
    db: Session = Depends(get_db)
):
    """
    Generate gender-specific outfit suggestions WITHOUT authentication.
    Works directly with or without auth - just pass user_id as query param.
    """
    try:
        # Try to get user from database, if not found create default test user
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            # Create or use first user
            user = db.query(User).first()
            if not user:
                raise HTTPException(status_code=404, detail="No user found. Please add wardrobe items first.")

        # Get wardrobe items for this user
        wardrobe_items = db.query(WardrobeItem).filter(
            WardrobeItem.user_id == user.id,
            ((WardrobeItem.gender == gender) | (WardrobeItem.gender == "unisex"))
        ).all()

        if not wardrobe_items:
            return {
                "success": False,
                "message": f"❌ No wardrobe items found for {gender} gender. Please add items to your wardrobe first! 🛍️"
            }

        # Convert wardrobe items to dictionary format
        wardrobe_data = []
        for item in wardrobe_items:
            # Get category name safely
            if hasattr(item, "category") and item.category:
                category_name = item.category.name
            elif hasattr(item, "category_id") and item.category_id:
                cat = db.query(Category).filter(Category.id == item.category_id).first()
                category_name = cat.name if cat else "General"
            else:
                category_name = "General"

            # Parse occasions safely
            try:
                occasions = json.loads(item.occasions) if hasattr(item, 'occasions') and item.occasions else []
            except:
                occasions = []

            wardrobe_data.append({
                "id": item.id,
                "name": item.name,
                "type": item.type,
                "category": category_name,
                "color": item.color,
                "pattern": item.pattern,
                "style": item.style,
                "fabric": getattr(item, "fabric", "cotton"),
                "season": item.season,
                "gender": getattr(item, "gender", "unisex"),
                "occasions": occasions,
                "image_url": item.image_path,
                "wear_count": item.wear_count,
                "last_worn": item.last_worn.isoformat() if item.last_worn else None
            })

        # Mock weather data (you can integrate real weather API later)
        weather = {
            "temperature_celsius": 28,
            "feels_like": 32,
            "condition": "sunny",
            "humidity_percent": 75,
            "rain_probability": 20,
            "uv_index": 7,
            "season": "summer"
        }

        # User style preferences (you can fetch from database later)
        preferences = {
            "preferred_colors": ["navy blue", "black", "grey", "white"],
            "disliked_colors": [],
            "preferred_styles": ["casual", "smart_casual"],
            "body_shape": "average",
            "style_profile": "classic"
        }

        # Generate outfit suggestions using AI service
        suggestions_text = outfit_service.generate_outfit_suggestions(
            event_type=event_type,
            event_date=event_date,
            event_time=event_time,
            formality=formality,
            city=city,
            country=country,
            wardrobe_items=wardrobe_data,
            weather=weather,
            user_preferences=preferences,
            avoid_days=avoid_days
        )

        return {
            "success": True,
            "suggestions": suggestions_text,
            "wardrobe_count": len(wardrobe_data)
        }

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "message": f"❌ Error: {str(e)}"
        }


@router.get("/wardrobe-items")
async def get_wardrobe_items(
    gender: str = Query(default="unisex"),
    user_id: int = Query(default=1),
    db: Session = Depends(get_db)
):
    """Get all wardrobe items for the user (no auth required)"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            user = db.query(User).first()

        if not user:
            return {"success": False, "items": [], "message": "No user found"}

        items = db.query(WardrobeItem).filter(
            WardrobeItem.user_id == user.id,
            ((WardrobeItem.gender == gender) | (WardrobeItem.gender == "unisex"))
        ).all()

        items_data = [
            {
                "id": item.id,
                "name": item.name,
                "type": item.type,
                "color": item.color,
                "image_url": item.image_path
            }
            for item in items
        ]

        return {
            "success": True,
            "items": items_data,
            "count": len(items_data)
        }

    except Exception as e:
        return {"success": False, "items": [], "message": str(e)}