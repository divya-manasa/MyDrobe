# Step 1: Update WardrobeItem Model
# File: app/models/wardrobe.py

from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.sql import func
from app.database import Base

class WardrobeItem(Base):
    __tablename__ = "wardrobe_items"

    id = Column(Integer, primary_key=True, index=True)
    
    # Basic info
    name = Column(String, nullable=False)
    category = Column(String)
    type = Column(String)  # subcategory
    
    # Appearance
    color = Column(String)
    pattern = Column(String)
    material = Column(String)  # ✅ fabric stored as material
    style = Column(String)  # ✅ NEW - was missing!
    
    # Details
    brand = Column(String)
    size = Column(String)
    season = Column(String)
    
    # New fields for AI detection
    gender = Column(String)  # ✅ NEW
    occasions = Column(JSON)  # ✅ NEW - Array of occasions
    occasion = Column(String)  # ✅ Keep for backward compatibility
    
    # Metadata
    description = Column(Text)
    image_url = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<WardrobeItem(id={self.id}, name='{self.name}', category='{self.category}')>"