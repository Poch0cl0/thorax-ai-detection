from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    PROJECT_NAME: str = "Thorax AI API"
    API_V1_PREFIX: str = "/api/v1"

    DATABASE_URL: str = "sqlite:///./thorax.db"

    SECRET_KEY: str = "change-me-in-production-use-openssl-rand-hex-32"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    UPLOAD_ROOT: str = str(Path("uploads"))

    MODEL_PATH: str | None = None
    MODEL_VERSION: str = "stub-0.1.0"
    INFERENCE_TIMEOUT_SECONDS: float = 120.0

    # Directorios de modelos PySpark ML
    MODELS_DIR: str = "models"
    LR_MODEL_PATH: str = "models/modelo_lr_empaquetado"
    RF_MODEL_PATH: str = "models/modelo_rf_empaquetado"

    # Preprocesamiento de imagen
    IMAGE_SIZE: int = 64
    MAX_IMAGE_SIZE_MB: int = 10

    ENVIRONMENT: Literal["development", "staging", "production"] = "development"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
