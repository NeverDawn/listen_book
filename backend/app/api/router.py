from fastapi import APIRouter

from app.api.routes import audio, books, health

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(books.router, prefix="/books", tags=["books"])
api_router.include_router(audio.router, prefix="/audio", tags=["audio"])
