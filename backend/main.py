from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from backend.core.config import settings
from backend.core.logging import logger
from backend.routers import health, audio
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Real-time speech translation to live subtitles",
)
# Mount static assets and templates
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
templates = Jinja2Templates(directory="frontend/templates")
# Register routers
app.include_router(health.router)
app.include_router(audio.router)
@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "app_name": settings.app_name,
            "target_language": settings.nllb_target_language,
        },
    )
@app.on_event("startup")
async def on_startup():
    logger.info(f"ðŸŽ™ï¸  {settings.app_name} v{settings.app_version} starting up")
    logger.info(f"   Whisper: {settings.whisper_model_size} | NLLB: {settings.nllb_model_name}")
    logger.info(f"   Target language: {settings.nllb_target_language}")