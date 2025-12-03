from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
import json
from app.database import get_db
from app.models.user import User
from app.models.wardrobe import WardrobeItem
from app.routers.auth import get_current_user
from app.services.huggingface_service import huggingface_service
from app.utils.helpers import json_to_dict

router = APIRouter(prefix="/api/chatbot", tags=["Chatbot"])

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    conversation_history: List[ChatMessage] = []

@router.post("/chat")
def chat_with_style_coach(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Chat with IBM Granite model-powered fashion advisor"""
    
    # Build context about user
    wardrobe_count = db.query(WardrobeItem).filter(WardrobeItem.user_id == current_user.id).count()
    
    user_context = f"""I'm your fashion advisor. I know that:
- You have {wardrobe_count} items in your wardrobe
- Your body shape: {current_user.body_shape or 'not specified'}
- Your skin tone: {current_user.skin_tone or 'not specified'}
- Your location: {current_user.location or 'not specified'}
- Your style preferences: {current_user.style_preferences or 'not specified'}

I'm here to provide personalized fashion advice, outfit suggestions, and style tips."""
    
    # Prepare conversation history
    history = [{"role": "system", "content": user_context}]
    
    for msg in request.conversation_history[-5:]:  # Last 5 messages
        history.append({"role": msg.role, "content": msg.content})
    
    # Get response from IBM model
    response = huggingface_service.chat(request.message, history)
    
    return {
        "message": request.message,
        "response": response,
        "model": "IBM Granite 3.1 8B"
    }

@router.get("/quick-tips")
def get_quick_tips(current_user: User = Depends(get_current_user)):
    """Get quick fashion tips"""
    tips = [
        "Mix textures for visual interest",
        "The rule of thirds: accessories should take up 1/3 of your outfit",
        "Neutral colors are your foundation",
        "Invest in quality basics",
        "Tailoring can transform an outfit"
    ]
    
    return {"tips": tips}
