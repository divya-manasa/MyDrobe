from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import json
import base64
from pathlib import Path

from app.database import get_db
from app.models.wardrobe import WardrobeItem
from app.services.groq_service import groq_service

router = APIRouter(prefix="/api/wardrobe", tags=["Wardrobe"])

# Create uploads directory
UPLOAD_DIR = Path(__file__).parent.parent.parent.parent / "frontend" / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True, parents=True)

# ========================================
# PYDANTIC MODELS
# ========================================

class AnalyzeImageResponse(BaseModel):
    itemname: str
    category: str
    subcategory: str
    fabric: str
    color: str
    pattern: str
    style: str
    season: str
    gender: str
    occasions: List[str]
    temp_image_path: str

class CreateItemRequest(BaseModel):
    name: str
    category: str
    subcategory: Optional[str] = None
    fabric: str
    color: str
    style: str
    pattern: str
    season: str
    brand: Optional[str] = None
    gender: Optional[str] = None
    occasions: Optional[List[str]] = []
    image_url: Optional[str] = ""  # ✅ NEW: Image path from analysis

class UpdateItemRequest(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    fabric: Optional[str] = None
    color: Optional[str] = None
    style: Optional[str] = None
    pattern: Optional[str] = None
    season: Optional[str] = None
    brand: Optional[str] = None
    gender: Optional[str] = None
    occasions: Optional[List[str]] = None

class WardrobeItemResponse(BaseModel):
    id: int
    name: str
    category: str
    subcategory: Optional[str]
    fabric: str
    color: str
    style: str
    pattern: str
    season: str
    brand: Optional[str]
    gender: Optional[str]
    occasions: Optional[List[str]]
    image_url: Optional[str]

    class Config:
        from_attributes = True

# ========================================
# ANALYZE IMAGE - NO AUTH
# ========================================

@router.post("/analyze-image", response_model=AnalyzeImageResponse)
async def analyze_image(file: UploadFile = File(...)):
    """
    Analyze clothing image using Gemini Vision.
    Saves image and returns analysis.
    """
    try:
        print("📸 Receiving image for analysis...")
        
        # Read image bytes
        image_bytes = await file.read()
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")
        
        # Save image with timestamp
        timestamp = datetime.now().timestamp()
        image_filename = f"outfit_{int(timestamp)}.jpg"
        image_path = UPLOAD_DIR / image_filename
        
        with open(image_path, 'wb') as f:
            f.write(image_bytes)
        
        print(f"💾 Image saved: {image_filename}")
        
        # AI Detection using groq_service
        print("🤖 Analyzing image with Gemini Vision...")
        detected = groq_service.detect_clothing_from_image(image_base64)
        
        print(f"✅ Detection complete: {detected}")
        
        # ✅ Map response with IMAGE PATH
        response = {
            "itemname": detected.get("item_name", "Clothing Item"),
            "category": detected.get("category", "Tops"),
            "subcategory": detected.get("sub_category", ""),
            "fabric": detected.get("fabric", "cotton"),
            "color": detected.get("color", ""),
            "pattern": detected.get("pattern", "solid"),
            "style": detected.get("style", "casual"),
            "season": detected.get("season", "all-season"),
            "gender": detected.get("gender", "unisex"),
            "occasions": detected.get("occasions", ["casual"]),
            "temp_image_path": f"/uploads/{image_filename}"  # ✅ Image path!
        }
        
        print(f"✅ Analysis response: {response}")
        return response
        
    except Exception as e:
        print(f"❌ Analysis error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Image analysis failed: {str(e)}")

# ========================================
# CREATE ITEM - NO AUTH
# ========================================

@router.post("/items", response_model=dict, status_code=201)
async def create_item(
    request: CreateItemRequest,
    db: Session = Depends(get_db)
):
    """
    Create wardrobe item after user confirms/edits the form.
    ✅ NOW SAVES IMAGE URL!
    """
    try:
        print(f"📝 Creating item: {request.name}")
        print(f"   Image: {request.image_url}")
        print(f"   Gender: {request.gender}")
        print(f"   Occasions: {request.occasions}")
        
        # Store extra data as JSON
        extra_data = {
            "gender": request.gender or "unisex",
            "style": request.style or "",
            "occasions": request.occasions or [],
            "fabric": request.fabric or ""
        }
        
        # ✅ SAVE IMAGE URL!
        item = WardrobeItem(
            name=request.name,
            category=request.category or "",
            type=request.subcategory or "",
            color=request.color or "",
            pattern=request.pattern or "",
            brand=request.brand or "",
            size="",
            season=request.season or "",
            occasion=json.dumps(extra_data),
            description=f"{request.color} {request.pattern} {request.subcategory or request.category}",
            image_url=request.image_url or "",  # ✅ SAVE IMAGE URL!
            created_at=datetime.now()
        )
        
        print(f"💾 Item object created: {item}")
        
        db.add(item)
        db.commit()
        db.refresh(item)
        
        print(f"✅ Item created with ID: {item.id}")
        
        return {
            "message": "Item created successfully",
            "item_id": item.id,
            "item": {
                "id": item.id,
                "name": item.name,
                "category": item.category,
                "color": item.color,
                "image_url": item.image_url  # ✅ Return image URL!
            }
        }
        
    except Exception as e:
        db.rollback()
        print(f"❌ Create error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to create item: {str(e)}")

# ========================================
# GET ALL ITEMS - NO AUTH
# ========================================

@router.get("/items", response_model=List[dict])
def get_all_items(
    category: Optional[str] = None,
    color: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get all wardrobe items with optional filters.
    ✅ NOW RETURNS IMAGE URL!
    """
    try:
        query = db.query(WardrobeItem)
        
        if category:
            query = query.filter(WardrobeItem.category == category)
        if color:
            query = query.filter(WardrobeItem.color.ilike(f"%{color}%"))
        
        items = query.all()
        print(f"📦 Retrieved {len(items)} items")
        
        # Map database fields to response
        response_items = []
        for item in items:
            # Parse JSON from occasion column
            try:
                occasion_data = json.loads(item.occasion) if item.occasion else {}
            except:
                occasion_data = {}
            
            response_items.append({
                "id": item.id,
                "name": item.name,
                "category": item.category,
                "subcategory": item.type if item.type else "",
                "fabric": occasion_data.get("fabric", ""),
                "color": item.color if item.color else "",
                "style": occasion_data.get("style", ""),
                "pattern": item.pattern if item.pattern else "",
                "season": item.season if item.season else "",
                "brand": item.brand if item.brand else "",
                "gender": occasion_data.get("gender", ""),
                "occasions": occasion_data.get("occasions", []),
                "image_url": item.image_url if item.image_url else "",  # ✅ IMAGE URL!
                "description": item.description if item.description else ""
            })
        
        return response_items
        
    except Exception as e:
        print(f"❌ Get items error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to retrieve items: {str(e)}")

# ========================================
# GET SINGLE ITEM - NO AUTH
# ========================================

@router.get("/items/{item_id}", response_model=dict)
def get_item(
    item_id: int,
    db: Session = Depends(get_db)
):
    """
    Get single item details.
    ✅ NOW RETURNS IMAGE URL!
    """
    try:
        item = db.query(WardrobeItem).filter(WardrobeItem.id == item_id).first()
        
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        print(f"📄 Retrieved item: {item.name}")
        print(f"📷 Image URL: {item.image_url}")
        
        # Parse JSON from occasion column
        try:
            occasion_data = json.loads(item.occasion) if item.occasion else {}
        except:
            occasion_data = {}
        
        return {
            "id": item.id,
            "name": item.name,
            "category": item.category,
            "subcategory": item.type if item.type else "",
            "fabric": occasion_data.get("fabric", ""),
            "color": item.color if item.color else "",
            "style": occasion_data.get("style", ""),
            "pattern": item.pattern if item.pattern else "",
            "season": item.season if item.season else "",
            "brand": item.brand if item.brand else "",
            "gender": occasion_data.get("gender", ""),
            "occasions": occasion_data.get("occasions", []),
            "image_url": item.image_url if item.image_url else "",  # ✅ IMAGE URL!
            "description": item.description if item.description else ""
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Get item error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ========================================
# UPDATE ITEM - NO AUTH
# ========================================

@router.put("/items/{item_id}", response_model=dict)
def update_item(
    item_id: int,
    request: UpdateItemRequest,
    db: Session = Depends(get_db)
):
    """
    Update wardrobe item.
    """
    try:
        item = db.query(WardrobeItem).filter(WardrobeItem.id == item_id).first()
        
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        # Parse existing JSON data
        try:
            occasion_data = json.loads(item.occasion) if item.occasion else {}
        except:
            occasion_data = {}
        
        # Update fields if provided
        if request.name is not None:
            item.name = request.name
        if request.category is not None:
            item.category = request.category
        if request.color is not None:
            item.color = request.color
        if request.pattern is not None:
            item.pattern = request.pattern
        if request.subcategory is not None:
            item.type = request.subcategory
        if request.season is not None:
            item.season = request.season
        if request.brand is not None:
            item.brand = request.brand
        
        # Update JSON fields
        if request.style is not None:
            occasion_data["style"] = request.style
        if request.fabric is not None:
            occasion_data["fabric"] = request.fabric
        if request.gender is not None:
            occasion_data["gender"] = request.gender
        if request.occasions is not None:
            occasion_data["occasions"] = request.occasions
        
        # Save updated JSON back
        item.occasion = json.dumps(occasion_data)
        
        db.commit()
        db.refresh(item)
        
        print(f"✅ Updated item: {item.name}")
        
        return {"message": "Item updated successfully", "item_id": item.id}
        
    except Exception as e:
        db.rollback()
        print(f"❌ Update error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# ========================================
# DELETE ITEM - NO AUTH
# ========================================

@router.delete("/items/{item_id}", response_model=dict)
def delete_item(
    item_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete wardrobe item.
    """
    try:
        item = db.query(WardrobeItem).filter(WardrobeItem.id == item_id).first()
        
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        db.delete(item)
        db.commit()
        
        print(f"✅ Deleted item: {item.name}")
        
        return {"message": "Item deleted successfully"}
        
    except Exception as e:
        db.rollback()
        print(f"❌ Delete error: {e}")
        raise HTTPException(status_code=500, detail=str(e))