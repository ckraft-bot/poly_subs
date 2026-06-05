from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Literal


class Settings(BaseSettings):
    # App
    app_name: str = "TransSubs"
    app_version: str = "0.1.0"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000

    # Whisper (speech-to-text)
    whisper_model_size: Literal["tiny", "base", "small", "medium", "large-v2", "large-v3"] = "base"
    whisper_device: Literal["cpu", "cuda", "auto"] = "auto"
    whisper_compute_type: Literal["int8", "float16", "float32"] = "int8"
    whisper_language: str | None = None  # None = auto-detect

    # NLLB-200 (translation)
    nllb_model_name: str = "facebook/nllb-200-distilled-600M"
    nllb_target_language: str = "eng_Latn"
    nllb_max_length: int = 512
    nllb_device: Literal["cpu", "cuda", "auto"] = "auto"

    # Audio streaming
    audio_sample_rate: int = 16000
    audio_chunk_seconds: float = 2.0
    audio_overlap_seconds: float = 0.3

    # Models cache dir
    models_dir: str = "./models"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()