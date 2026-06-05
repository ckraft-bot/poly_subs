from fastapi import APIRouter
from backend.core.config import settings

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/")
async def health_check():
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.app_version,
    }