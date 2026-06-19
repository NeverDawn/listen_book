from functools import cached_property
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_prefix="LISTEN_BOOK_",
        extra="ignore",
    )

    database_url: str = "postgresql+psycopg://listen_book_app:change-me@localhost:5432/listen_book"
    secret_key: str = "change-me-in-development"
    storage_root: Path = Field(default=PROJECT_ROOT / "storage")
    cors_origins_raw: str = Field(
        default="http://localhost:5173,http://127.0.0.1:5173",
        validation_alias="LISTEN_BOOK_CORS_ORIGINS",
    )

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins_raw.split(",") if origin.strip()]

    @cached_property
    def uploads_dir(self) -> Path:
        return self.storage_root / "uploads"

    @cached_property
    def parsed_dir(self) -> Path:
        return self.storage_root / "parsed"

    @cached_property
    def audio_dir(self) -> Path:
        return self.storage_root / "audio"


settings = Settings()
