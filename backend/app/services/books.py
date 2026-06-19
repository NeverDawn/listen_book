import logging
import shutil
from pathlib import Path
from uuid import UUID, uuid4

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.audio import AudioAsset
from app.models.book import Book, BookFile, Chapter, Paragraph, Sentence
from app.models.job import Job, JobStatus, JobType
from app.models.progress import ReadingProgress

SUPPORTED_FORMATS = {"txt", "epub", "pdf"}
logger = logging.getLogger(__name__)


def create_uploaded_book(db: Session, file: UploadFile) -> Book:
    original_name = file.filename or "untitled"
    extension = Path(original_name).suffix.lower().lstrip(".")
    if extension not in SUPPORTED_FORMATS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported book format: {extension or 'unknown'}",
        )

    settings.uploads_dir.mkdir(parents=True, exist_ok=True)
    storage_name = f"{uuid4()}.{extension}"
    storage_path = settings.uploads_dir / storage_name

    with storage_path.open("wb") as target:
        shutil.copyfileobj(file.file, target)

    size_bytes = storage_path.stat().st_size
    title = Path(original_name).stem

    book = Book(title=title)
    db.add(book)
    db.flush()

    db.add(
        BookFile(
            book_id=book.id,
            original_filename=original_name,
            file_format=extension,
            storage_path=str(storage_path),
            size_bytes=size_bytes,
        )
    )
    db.add(
        Job(
            job_type=JobType.PARSE_BOOK.value,
            status=JobStatus.PENDING.value,
            payload={
                "book_id": str(book.id),
                "storage_path": str(storage_path),
                "format": extension,
            },
        )
    )
    db.commit()
    db.refresh(book)
    return book


def delete_book(db: Session, book_id: UUID) -> None:
    book = db.get(Book, book_id)
    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    file_paths = _collect_book_storage_paths(db, book)

    sentence_ids = list(
        db.scalars(
            select(Sentence.id)
            .join(Paragraph, Sentence.paragraph_id == Paragraph.id)
            .join(Chapter, Paragraph.chapter_id == Chapter.id)
            .where(Chapter.book_id == book_id)
        ).all()
    )

    if sentence_ids:
        for audio_asset in db.scalars(
            select(AudioAsset).where(AudioAsset.sentence_id.in_(sentence_ids))
        ).all():
            db.delete(audio_asset)

    for progress in db.scalars(
        select(ReadingProgress).where(ReadingProgress.book_id == book_id)
    ).all():
        db.delete(progress)

    for job in db.scalars(select(Job)).all():
        if job.payload.get("book_id") == str(book_id):
            db.delete(job)

    db.delete(book)
    db.commit()

    for file_path in file_paths:
        _delete_storage_file(file_path)


def _collect_book_storage_paths(db: Session, book: Book) -> list[Path]:
    paths: list[Path] = []

    if book.cover_path:
        paths.append(Path(book.cover_path))

    paths.extend(Path(book_file.storage_path) for book_file in book.files)

    audio_paths = db.scalars(
        select(AudioAsset.storage_path)
        .join(Sentence, AudioAsset.sentence_id == Sentence.id)
        .join(Paragraph, Sentence.paragraph_id == Paragraph.id)
        .join(Chapter, Paragraph.chapter_id == Chapter.id)
        .where(Chapter.book_id == book.id)
        .where(AudioAsset.storage_path.is_not(None))
    ).all()
    paths.extend(Path(path) for path in audio_paths if path)

    return paths


def _delete_storage_file(path: Path) -> None:
    try:
        resolved_path = path.resolve()
        storage_root = settings.storage_root.resolve()
        if not resolved_path.is_relative_to(storage_root):
            logger.warning("Skip deleting file outside storage root: %s", resolved_path)
            return
        if resolved_path.is_file():
            resolved_path.unlink()
    except OSError:
        logger.exception("Failed to delete storage file: %s", path)
