"""
Central config — everything driven from .env, never hardcoded.
All services import settings from here; no service reads env vars directly.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    mysql_url: str = "mysql+pymysql://root:Mano%402005@localhost:3306/resume_rag"
    
    # Ollama / LLM
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "llama3:8b"

    # Embedding model
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    # RAG pipeline
    # chunk_size is in WORDS. all-MiniLM-L6-v2 has a 256-token limit.
    # 200 words ≈ 250 tokens on average — safe headroom.
    chunk_size: int = 200
    chunk_overlap: int = 30
    top_k: int = 5

    # Storage paths
    chroma_path: str = "./data/chroma"
    upload_path: str = "./data/uploads"

    # Upload limits
    max_pdf_size: int = 10_485_760  # 10 MB
    
    # Auth / JWT
    secret_key: str = "change-this-to-a-random-secret-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 hours
    otp_expire_minutes: int = 10                 # OTP valid for 10 minutes

    # Email (SMTP) for OTP delivery
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""       # set in .env: your Gmail address
    smtp_password: str = ""   # set in .env: Gmail app password
    smtp_from: str = ""       # defaults to smtp_user if blank

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache()
def get_settings() -> Settings:
    """Cached singleton — loaded once at startup."""
    return Settings()
