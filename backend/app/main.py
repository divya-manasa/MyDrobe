from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os

from app.database import engine, Base
from app.routers import wardrobe
from app.models import wardrobe as wardrobe_models

# Create tables
print("🗄️  Creating database...")
Base.metadata.create_all(bind=engine)
print("✅ Database ready")

app = FastAPI(title="SmartStyle AI - Wardrobe Manager")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include wardrobe router
app.include_router(wardrobe.router)

# Frontend path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(backend_dir)
frontend_path = os.path.join(project_root, "frontend")

print(f"📂 Frontend: {frontend_path}")

if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
    print("✅ Frontend ready")
else:
    print("⚠️  Frontend not found")

@app.get("/api/health")
def health():
    return {"status": "healthy", "message": "SmartStyle AI Wardrobe"}
