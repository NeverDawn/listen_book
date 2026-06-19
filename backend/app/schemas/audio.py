from uuid import UUID

from pydantic import BaseModel, Field


class AudioAssetRead(BaseModel):
    id: UUID
    sentence_id: UUID
    status: str
    audio_url: str | None
    duration_ms: int | None

    model_config = {"from_attributes": True}


class AudioPrefetchRequest(BaseModel):
    sentence_ids: list[UUID] = Field(min_length=1, max_length=20)


class AudioPrefetchResponse(BaseModel):
    assets: list[AudioAssetRead]
    queued_sentence_ids: list[UUID]
