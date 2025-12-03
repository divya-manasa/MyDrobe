from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models.user import User
from app.routers.auth import get_current_user
from app.utils.helpers import dict_to_json
import json

router = APIRouter(prefix="/api/profile", tags=["Profile"])

class ProfileUpdateRequest(BaseModel):
    full_name: str = None
    body_shape: str = None
    skin_tone: str = None
    location: str = None
    style_preferences: dict = None
    measurements: dict = None
    eco_preference: str = None
    price_range_min: float = None
    price_range_max: float = None
    preferred_brands: list = None
    size_preferences: dict = None

@router.put("/update")
def update_profile(
    request: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if request.full_name:
        current_user.full_name = request.full_name
    if request.body_shape:
        current_user.body_shape = request.body_shape
    if request.skin_tone:
        current_user.skin_tone = request.skin_tone
    if request.location:
        current_user.location = request.location
    if request.style_preferences:
        current_user.style_preferences = dict_to_json(request.style_preferences)
    if request.measurements:
        current_user.measurements = dict_to_json(request.measurements)
    if request.eco_preference:
        current_user.eco_preference = request.eco_preference
    if request.price_range_min is not None:
        current_user.price_range_min = request.price_range_min
    if request.price_range_max is not None:
        current_user.price_range_max = request.price_range_max
    if request.preferred_brands:
        current_user.preferred_brands = dict_to_json(request.preferred_brands)
    if request.size_preferences:
        current_user.size_preferences = dict_to_json(request.size_preferences)
    
    db.commit()
    db.refresh(current_user)
    
    return {"message": "Profile updated successfully", "user": {
        "id": current_user.id,
        "full_name": current_user.full_name,
        "body_shape": current_user.body_shape,
        "skin_tone": current_user.skin_tone,
        "location": current_user.location
    }}

@router.get("/settings")
def get_settings(current_user: User = Depends(get_current_user)):
    return {
        "eco_preference": current_user.eco_preference,
        "price_range": {
            "min": current_user.price_range_min,
            "max": current_user.price_range_max
        },
        "preferred_brands": json.loads(current_user.preferred_brands) if current_user.preferred_brands else [],
        "size_preferences": json.loads(current_user.size_preferences) if current_user.size_preferences else {}
    }
