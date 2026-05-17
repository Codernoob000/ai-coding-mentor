from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, SecretStr
from typing import List

class Settings(BaseSettings):
    # Core Gemini Settings
    GEMINI_API_KEY: SecretStr
    GEMINI_MODEL_NAME: str = "gemini-3.1-flash-lite"
    GEMINI_MAX_OUTPUT_TOKENS: int = 4096
    GEMINI_TEMPERATURE: float = 0.7
    GEMINI_TIMEOUT_SECONDS: float = 60.0
    
    # App Settings
    APP_NAME: str = "AI Coding Mentor"
    PORT: int = 8080
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000", 
        "http://localhost:5173", 
        "https://ai-coding-mentor.vercel.app",
        "https://ai-coding-mentor-theta.vercel.app"
    ]
    CORS_ORIGINS_JSON: str = "" # Allows overriding via ENV as a JSON string

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:////tmp/mentor_agent.db"
    
    # Cloud Deployment
    GCP_PROJECT_ID: str = "second-brain-496517"
    
    # Retry Logic
    LLM_MAX_RETRIES: int = 3

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
