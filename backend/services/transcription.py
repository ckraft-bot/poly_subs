"""
Transcription service wrapping Faster-Whisper.
Lazy-loads the model on first use so startup is fast.
"""
import numpy as np
from faster_whisper import WhisperModel
from backend.core.config import settings
from backend.core.logging import logger

_model: WhisperModel | None = None


def get_model() -> WhisperModel:
    global _model
    if _model is None:
        logger.info(f"Loading Whisper model '{settings.whisper_model_size}' ...")
        _model = WhisperModel(
            settings.whisper_model_size,
            device=settings.whisper_device,
            compute_type=settings.whisper_compute_type,
            download_root=settings.models_dir,
        )
        logger.info("Whisper model loaded.")
    return _model


def transcribe(audio_chunk: np.ndarray) -> str:
    """
    Transcribe a numpy float32 PCM array (16 kHz, mono).
    Returns the transcript text, or empty string if nothing detected.
    """
    model = get_model()
    segments, info = model.transcribe(
        audio_chunk,
        language=settings.whisper_language,
        beam_size=5,
        vad_filter=True,        # skip silent chunks automatically
        vad_parameters=dict(
            min_silence_duration_ms=300,
        ),
    )
    text = " ".join(seg.text.strip() for seg in segments).strip()
    if text:
        logger.debug(f"Transcribed ({info.language}, {info.language_probability:.0%}): {text}")
    return text