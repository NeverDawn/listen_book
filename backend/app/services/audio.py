import logging
from pathlib import Path
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.audio import AudioAsset, AudioStatus
from app.models.book import Sentence
from app.services.tts import TTSRequest, default_tts_provider

DEFAULT_VOICE = "zh-CN-XiaoxiaoNeural"
DEFAULT_SPEED = 100
logger = logging.getLogger(__name__)


def sentence_audio_stmt(sentence: Sentence):
    provider = default_tts_provider
    return select(AudioAsset).where(
        AudioAsset.sentence_id == sentence.id,
        AudioAsset.model_name == provider.model_name,
        AudioAsset.model_version == provider.model_version,
        AudioAsset.voice == DEFAULT_VOICE,
        AudioAsset.speed == DEFAULT_SPEED,
        AudioAsset.text_hash == sentence.text_hash,
    )


def audio_file_is_available(asset: AudioAsset) -> bool:
    if asset.storage_path is None:
        return False
    path = Path(asset.storage_path)
    return path.is_file() and path.stat().st_size > 0


def get_existing_sentence_audio(db: Session, sentence: Sentence) -> AudioAsset | None:
    return db.scalar(sentence_audio_stmt(sentence))


def ensure_pending_sentence_audio(db: Session, sentence: Sentence) -> AudioAsset:
    existing = get_existing_sentence_audio(db, sentence)
    if existing is not None:
        return existing

    provider = default_tts_provider
    asset = AudioAsset(
        sentence_id=sentence.id,
        model_name=provider.model_name,
        model_version=provider.model_version,
        voice=DEFAULT_VOICE,
        speed=DEFAULT_SPEED,
        text_hash=sentence.text_hash,
        status=AudioStatus.PENDING.value,
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset


def audio_asset_should_be_queued(asset: AudioAsset) -> bool:
    if asset.status == AudioStatus.READY.value and audio_file_is_available(asset):
        return False
    return asset.status not in {AudioStatus.PENDING.value, AudioStatus.GENERATING.value}


def get_or_create_sentence_audio(db: Session, sentence_id: UUID) -> AudioAsset:
    sentence = db.get(Sentence, sentence_id)
    if sentence is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sentence not found")

    provider = default_tts_provider
    existing = get_existing_sentence_audio(db, sentence)
    if (
        existing is not None
        and existing.status == AudioStatus.READY.value
        and audio_file_is_available(existing)
    ):
        return existing

    asset = existing or AudioAsset(
        sentence_id=sentence.id,
        model_name=provider.model_name,
        model_version=provider.model_version,
        voice=DEFAULT_VOICE,
        speed=DEFAULT_SPEED,
        text_hash=sentence.text_hash,
        status=AudioStatus.PENDING.value,
    )
    if existing is None:
        db.add(asset)

    asset.status = AudioStatus.GENERATING.value
    asset.error_message = None
    db.commit()
    db.refresh(asset)

    try:
        result = provider.generate(
            TTSRequest(text=sentence.text, voice=asset.voice, speed=asset.speed)
        )
    except Exception as exc:
        asset.status = AudioStatus.FAILED.value
        asset.error_message = str(exc)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"TTS generation failed: {exc}",
        ) from exc

    asset.storage_path = result.audio_path
    asset.duration_ms = result.duration_ms
    asset.status = AudioStatus.READY.value
    db.commit()
    db.refresh(asset)
    return asset


def generate_sentence_audio_job(sentence_id: UUID) -> None:
    db = SessionLocal()
    try:
        get_or_create_sentence_audio(db, sentence_id)
    except Exception:
        logger.exception(
            "Background sentence audio generation failed",
            extra={"sentence_id": sentence_id},
        )
    finally:
        db.close()
