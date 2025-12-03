from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.models.user import User
from app.routers.auth import get_current_user
from app.database import get_db

router = APIRouter(prefix="/api/profile", tags=["Profile"])

class ProfileUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None

class ProfileResponse(BaseModel):
    id: int
    username: str
    email: str
    
    class Config:
        from_attributes = True

@router.get("/", response_model=ProfileResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return current_user

@router.put("/update", response_model=ProfileResponse)
def update_profile(
    profile_data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile"""
    
    # Check if username is taken by another user
    if profile_data.username and profile_data.username != current_user.username:
        existing_user = db.query(User).filter(
            User.username == profile_data.username,
            User.id != current_user.id
        ).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already taken")
    
    # Check if email is taken by another user
    if profile_data.email and profile_data.email != current_user.email:
        existing_user = db.query(User).filter(
            User.email == profile_data.email,
            User.id != current_user.id
        ).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already taken")
    
    # Update fields
    if profile_data.username:
        current_user.username = profile_data.username
    if profile_data.email:
        current_user.email = profile_data.email
    
    db.commit()
    db.refresh(current_user)
    
    return current_user
