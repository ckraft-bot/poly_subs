"""
Pre-downloads Whisper and NLLB-200 models to the local cache.
Run once before starting the app:  python scripts/download_models.py
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.core.config import settings
from backend.core.logging import logger


def download_whisper():
    logger.info(f"Downloading Whisper '{settings.whisper_model_size}' ...")
    from faster_whisper import WhisperModel
    WhisperModel(
        settings.whisper_model_size,
        device="cpu",           # always download on CPU
        compute_type="int8",
        download_root=settings.models_dir,
    )
    logger.info("Whisper ✓")


def download_nllb():
    logger.info(f"Downloading NLLB '{settings.nllb_model_name}' ...")
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
    AutoTokenizer.from_pretrained(
        settings.nllb_model_name,
        cache_dir=settings.models_dir,
    )
    AutoModelForSeq2SeqLM.from_pretrained(
        settings.nllb_model_name,
        cache_dir=settings.models_dir,
    )
    logger.info("NLLB ✓")


def main():
    os.makedirs(settings.models_dir, exist_ok=True)
    logger.info(f"Saving models to: {settings.models_dir}")

    download_whisper()
    download_nllb()

    logger.info("All models downloaded. You're ready to run: make dev")


if __name__ == "__main__":
    main()