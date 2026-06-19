import uuid
from enum import StrEnum

from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, IdMixin, TimestampMixin


class AudioStatus(StrEnum):
    PENDING = "pending"
    GENERATING = "generating"
    READY = "ready"
    FAILED = "failed"


class AudioAsset(IdMixin, TimestampMixin, Base):
    __tablename__ = "audio_assets"
    __table_args__ = (
        UniqueConstraint(
            "sentence_id",
            "model_name",
            "model_version",
            "voice",
            "speed",
            "text_hash",
        ),
    )

    sentence_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sentences.id"),
        index=True,
    )
    model_name: Mapped[str] = mapped_column(String(120))
    model_version: Mapped[str] = mapped_column(String(120))
    voice: Mapped[str] = mapped_column(String(120))
    speed: Mapped[int] = mapped_column(Integer, default=100)
    text_hash: Mapped[str] = mapped_column(String(64), index=True)
    status: Mapped[str] = mapped_column(String(32), default=AudioStatus.PENDING.value, index=True)
    storage_path: Mapped[str | None] = mapped_column(String(500))
    duration_ms: Mapped[int | None] = mapped_column(Integer)
    error_message: Mapped[str | None] = mapped_column(Text)

    sentence = relationship("Sentence", back_populates="audio_assets")
