import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Canonical Medical Record Structuring Pipeline"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    ALLOWED_ORIGINS: str = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000,http://127.0.0.1:8000,http://localhost:5500,http://127.0.0.1:5500"
    )
    API_BASE_URL: str = os.getenv("API_BASE_URL", "")
    
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    OUTPUT_DIR: Path = BASE_DIR / "output"
    TERMINOLOGY_DIR: Path = DATA_DIR / "terminologies"
    
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'data' / 'canonical_records.db'}")
    
    CONFIDENCE_ACCEPT_THRESHOLD: float = 0.85
    CONFIDENCE_FLAG_THRESHOLD: float = 0.60
    
    class Config:
        case_sensitive = True

    def __init__(self, **values):
        super().__init__(**values)
        # Normalize postgres:// URLs (e.g. from Supabase or Render) to postgresql:// for SQLAlchemy
        if self.DATABASE_URL.startswith("postgres://"):
            self.DATABASE_URL = self.DATABASE_URL.replace("postgres://", "postgresql://", 1)

settings = Settings()

# Ensure required directories exist
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
settings.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
settings.TERMINOLOGY_DIR.mkdir(parents=True, exist_ok=True)
