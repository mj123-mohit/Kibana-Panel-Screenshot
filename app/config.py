# app/config.py

from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    KIBANA_URL: str
    USERNAME: str
    PASSWORD: str
    OUTPUT_DIR: Optional[str] = "screenshots"  # default

    class Config:
        env_file = ".env"

settings = Settings()
