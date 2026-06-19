import uuid

from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, IdMixin, TimestampMixin


class ReadingProgress(IdMixin, TimestampMixin, Base):
    __tablename__ = "reading_progress"
    __table_args__ = (UniqueConstraint("user_id", "book_id"),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        index=True,
    )
    book_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("books.id"),
        index=True,
    )
    chapter_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("chapters.id"),
    )
    paragraph_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("paragraphs.id"),
    )
    sentence_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sentences.id"),
    )
    audio_position_ms: Mapped[int] = mapped_column(Integer, default=0)

    user = relationship("User", back_populates="progress_items")
    book = relationship("Book")
    chapter = relationship("Chapter")
    paragraph = relationship("Paragraph")
    sentence = relationship("Sentence")
