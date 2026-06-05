"""
Sanity-check your microphone and transcription pipeline without
starting the full web server.

Usage:  python scripts/test_mic.py
        python scripts/test_mic.py --seconds 5
        python scripts/test_mic.py --language es
"""
import argparse
import sys
import os

import numpy as np
import sounddevice as sd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.core.config import settings
from backend.core.logging import logger
from backend.services.transcription import transcribe
from backend.services.translation import translate


def list_devices():
    logger.info("Available audio input devices:")
    for i, dev in enumerate(sd.query_devices()):
        if dev["max_input_channels"] > 0:
            logger.info(f"  [{i}] {dev['name']}")


def record(seconds: int, sample_rate: int) -> np.ndarray:
    logger.info(f"Recording for {seconds}s at {sample_rate} Hz — speak now...")
    audio = sd.rec(
        int(seconds * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype="float32",
    )
    sd.wait()
    return audio.flatten()


def main():
    parser = argparse.ArgumentParser(description="Test mic → transcription → translation")
    parser.add_argument("--seconds",  type=int, default=4,    help="Recording duration (default: 4)")
    parser.add_argument("--language", type=str, default=None, help="Force source language, e.g. 'es'")
    parser.add_argument("--list-devices", action="store_true", help="List audio input devices and exit")
    args = parser.parse_args()

    if args.list_devices:
        list_devices()
        sys.exit(0)

    if args.language:
        settings.whisper_language = args.language

    audio = record(args.seconds, settings.audio_sample_rate)

    logger.info("Transcribing...")
    transcript = transcribe(audio)

    if not transcript:
        logger.warning("No speech detected. Try speaking louder or increasing --seconds.")
        sys.exit(1)

    logger.info(f"Transcript  : {transcript}")

    logger.info("Translating...")
    translated = translate(transcript)
    logger.info(f"Translation : {translated}")

    logger.info("Pipeline working correctly.")


if __name__ == "__main__":
    main()