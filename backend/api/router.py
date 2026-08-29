from fastapi import APIRouter

from .routes import chat, health, metadata, search


api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(metadata.router)
api_router.include_router(search.router)
api_router.include_router(chat.router)
