"""
Unit tests for the transcription service.
Uses a synthetic sine wave and silence to avoid needing real audio files.
"""
import numpy as np
import pytest
from unittest.mock import patch, MagicMock

from backend.services.transcription import transcribe, get_model


# ── helpers ───────────────────────────────────────────────────────────

def make_silence(seconds: float = 2.0, sample_rate: int = 16000) -> np.ndarray:
    return np.zeros(int(seconds * sample_rate), dtype=np.float32)


def make_tone(seconds: float = 2.0, sample_rate: int = 16000, freq: int = 440) -> np.ndarray:
    t = np.linspace(0, seconds, int(seconds * sample_rate), endpoint=False)
    return np.sin(2 * np.pi * freq * t).astype(np.float32)


def make_mock_segment(text: str):
    seg = MagicMock()
    seg.text = text
    return seg


# ── tests ─────────────────────────────────────────────────────────────

class TestTranscribe:

    @patch("backend.services.transcription.get_model")
    def test_returns_transcript_text(self, mock_get_model):
        """Happy path: model returns a segment with text."""
        mock_model = MagicMock()
        mock_info  = MagicMock()
        mock_info.language             = "en"
        mock_info.language_probability = 0.99
        mock_model.transcribe.return_value = (
            [make_mock_segment("Hello world")],
            mock_info,
        )
        mock_get_model.return_value = mock_model

        result = transcribe(make_tone())
        assert result == "Hello world"

    @patch("backend.services.transcription.get_model")
    def test_returns_empty_string_on_silence(self, mock_get_model):
        """VAD filtered everything — no segments returned."""
        mock_model = MagicMock()
        mock_info  = MagicMock()
        mock_info.language             = "en"
        mock_info.language_probability = 0.0
        mock_model.transcribe.return_value = ([], mock_info)
        mock_get_model.return_value = mock_model

        result = transcribe(make_silence())
        assert result == ""

    @patch("backend.services.transcription.get_model")
    def test_joins_multiple_segments(self, mock_get_model):
        """Multiple segments should be joined with a space."""
        mock_model = MagicMock()
        mock_info  = MagicMock()
        mock_info.language             = "en"
        mock_info.language_probability = 0.95
        mock_model.transcribe.return_value = (
            [make_mock_segment("Hello"), make_mock_segment("world")],
            mock_info,
        )
        mock_get_model.return_value = mock_model

        result = transcribe(make_tone())
        assert result == "Hello world"

    @patch("backend.services.transcription.get_model")
    def test_strips_whitespace(self, mock_get_model):
        """Segments with extra whitespace should be cleaned up."""
        mock_model = MagicMock()
        mock_info  = MagicMock()
        mock_info.language             = "en"
        mock_info.language_probability = 0.9
        mock_model.transcribe.return_value = (
            [make_mock_segment("  Hello world  ")],
            mock_info,
        )
        mock_get_model.return_value = mock_model

        result = transcribe(make_tone())
        assert result == "Hello world"

    @patch("backend.services.transcription._model", None)
    @patch("backend.services.transcription.WhisperModel")
    def test_model_lazy_loads(self, mock_whisper_class):
        """Model should be instantiated on first call."""
        mock_instance = MagicMock()
        mock_info     = MagicMock()
        mock_info.language             = "en"
        mock_info.language_probability = 0.9
        mock_instance.transcribe.return_value = (
            [make_mock_segment("test")],
            mock_info,
        )
        mock_whisper_class.return_value = mock_instance

        transcribe(make_tone())
        mock_whisper_class.assert_called_once()