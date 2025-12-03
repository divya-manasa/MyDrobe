from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from app.database import Base

class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    name = Column(String(255), nullable=False)
    event_type = Column(String(100))  # Office, Party, Wedding, Travel, Gym, etc.
    event_date = Column(DateTime(timezone=True))
    location = Column(String(255))
    notes = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Outfit(Base):
    __tablename__ = "outfits"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    event_id = Column(Integer, ForeignKey("events.id"))
    
    name = Column(String(255))
    occasion = Column(String(100))
    items = Column(Text)  # JSON array of item IDs
    ai_reasoning = Column(Text)
    score = Column(Integer)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
