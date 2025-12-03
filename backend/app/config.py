import os
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

# Force load .env file from backend directory
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

print(f"🔍 Loading .env from: {env_path}")
print(f"📂 .env exists: {env_path.exists()}")

class Settings(BaseSettings):
    # API Keys
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    HUGGINGFACE_API_KEY: str = os.getenv("HUGGINGFACE_API_KEY", "")
    OPENWEATHER_API_KEY: str = os.getenv("OPENWEATHER_API_KEY", "")
    SERPAPI_KEY: str = os.getenv("SERPAPI_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    STABILITY_API_KEY: str = os.getenv("STABILITY_API_KEY", "")
    # JWT
    SECRET_KEY_JWT: str = os.getenv("SECRET_KEY_JWT", "smartstyle-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./wardrobe.db")
    
    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Groq Models
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    GROQ_VISION_MODEL: str = "llama-3.2-11b-vision-preview"
    
    # Hugging Face Models
    HF_CHATBOT_MODEL: str = "ibm-granite/granite-3.3-2b-instruct"
    
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

settings = Settings()

# Debug print
print(f"✓ GROQ_API_KEY loaded: {bool(settings.GROQ_API_KEY)} ({settings.GROQ_API_KEY[:15] + '...' if settings.GROQ_API_KEY else 'NOT SET'})")
print(f"✓ STABILITY_API_KEY loaded: {bool(settings.STABILITY_API_KEY)}")
print(f"✓ SERP_API_KEY loaded: {bool(settings.SERPAPI_KEY)}")

@lru_cache()
def get_settings():
    return Settings()
