from enum import StrEnum

from sqlalchemy import Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, IdMixin, TimestampMixin


class JobType(StrEnum):
    PARSE_BOOK = "parse_book"
    GENERATE_AUDIO = "generate_audio"


class JobStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"


class Job(IdMixin, TimestampMixin, Base):
    __tablename__ = "jobs"

    job_type: Mapped[str] = mapped_column(String(64), index=True)
    status: Mapped[str] = mapped_column(String(32), default=JobStatus.PENDING.value, index=True)
    payload: Mapped[dict] = mapped_column(JSONB, default=dict)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(Text)
