from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.sql import func
from app.database import Base

class WearLog(Base):
    __tablename__ = "wear_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("wardrobe_items.id"), nullable=False)
    outfit_id = Column(Integer, ForeignKey("outfits.id"))
    
    worn_date = Column(DateTime(timezone=True), server_default=func.now())

class Analytics(Base):
    __tablename__ = "analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    metric_type = Column(String(100))  # most_worn, least_worn, cost_per_wear, etc.
    metric_data = Column(String(1000))  # JSON string
    period = Column(String(50))  # week, month, year
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
