"""
SubtitleStream: orchestrates audio chunking → transcription → translation
for a single WebSocket connection.
"""
import asyncio
import time
from typing import AsyncGenerator

import numpy as np
from fastapi import WebSocket

from backend.core.config import settings
from backend.core.logging import logger
from backend.services.transcription import transcribe
from backend.services.translation import translate


class SubtitleStream:
    def __init__(self, websocket: WebSocket):
        self.websocket = websocket
        self._buffer = bytearray()
        self._chunk_bytes = int(
            settings.audio_sample_rate
            * settings.audio_chunk_seconds
            * 2  # 16-bit PCM = 2 bytes per sample
        )
        self._overlap_bytes = int(
            settings.audio_sample_rate
            * settings.audio_overlap_seconds
            * 2
        )

    async def receive_audio(self) -> AsyncGenerator[np.ndarray, None]:
        """
        Consume raw PCM bytes from the WebSocket and yield
        float32 numpy arrays of the configured chunk size.

        Overlap is kept at the tail of each chunk so words
        at chunk boundaries aren't clipped.
        """
        async for message in self.websocket.iter_bytes():
            self._buffer.extend(message)

            while len(self._buffer) >= self._chunk_bytes:
                chunk_bytes = bytes(self._buffer[: self._chunk_bytes])

                # Slide forward by (chunk - overlap) so the next chunk
                # re-processes the last `overlap` worth of audio
                advance = self._chunk_bytes - self._overlap_bytes
                self._buffer = self._buffer[advance:]

                audio = (
                    np.frombuffer(chunk_bytes, dtype=np.int16)
                    .astype(np.float32) / 32768.0
                )
                yield audio

    async def process(self, audio: np.ndarray) -> dict | None:
        """
        Run transcription then translation in a thread pool executor
        so neither blocks the async event loop.

        Returns a subtitle event dict, or None if no speech was detected.
        """
        loop = asyncio.get_event_loop()

        transcript = await loop.run_in_executor(None, transcribe, audio)
        if not transcript:
            return None

        translated = await loop.run_in_executor(None, translate, transcript)

        return {
            "text": transcript,
            "translated": translated,
            "ts": int(time.time() * 1000),  # Unix ms timestamp
        }