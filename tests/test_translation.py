"""
Unit tests for the translation service.
Mocks out the HuggingFace model so no GPU/download is needed.
"""
import pytest
from unittest.mock import patch, MagicMock

from backend.services.translation import translate


# ── helpers ───────────────────────────────────────────────────────────

def make_mock_tokenizer(decoded_output: str = "Hola mundo"):
    tokenizer = MagicMock()
    # inputs.to(device) should return something with **-unpackable keys
    inputs_on_device = {"input_ids": MagicMock(), "attention_mask": MagicMock()}
    tokenizer.return_value.to.return_value = inputs_on_device
    tokenizer.convert_tokens_to_ids.return_value = 256047  # dummy BOS token
    tokenizer.decode.return_value = decoded_output
    return tokenizer


def make_mock_model(output_ids=None):
    model = MagicMock()
    model.generate.return_value = output_ids or [[1, 2, 3]]
    model.to.return_value = model
    return model


# ── tests ─────────────────────────────────────────────────────────────

class TestTranslate:

    @patch("backend.services.translation._model", None)
    @patch("backend.services.translation._tokenizer", None)
    @patch("backend.services.translation.AutoModelForSeq2SeqLM")
    @patch("backend.services.translation.AutoTokenizer")
    def test_translates_text(self, mock_tokenizer_class, mock_model_class):
        """Happy path: returns translated string."""
        mock_tokenizer_class.from_pretrained.return_value = make_mock_tokenizer("Hola mundo")
        mock_model_class.from_pretrained.return_value     = make_mock_model()

        result = translate("Hello world")
        assert result == "Hola mundo"

    def test_empty_string_passthrough(self):
        """Empty input should be returned immediately without touching the model."""
        result = translate("")
        assert result == ""

    @patch("backend.services.translation._model", None)
    @patch("backend.services.translation._tokenizer", None)
    @patch("backend.services.translation.AutoModelForSeq2SeqLM")
    @patch("backend.services.translation.AutoTokenizer")
    def test_returns_original_on_bad_language_code(
        self, mock_tokenizer_class, mock_model_class
    ):
        """Unknown language code → graceful fallback to original text."""
        tokenizer = make_mock_tokenizer()
        tokenizer.convert_tokens_to_ids.return_value = None  # simulates unknown code
        mock_tokenizer_class.from_pretrained.return_value = tokenizer
        mock_model_class.from_pretrained.return_value     = make_mock_model()

        result = translate("Hello world", target_lang="not_a_real_lang")
        assert result == "Hello world"

    @patch("backend.services.translation._model", None)
    @patch("backend.services.translation._tokenizer", None)
    @patch("backend.services.translation.AutoModelForSeq2SeqLM")
    @patch("backend.services.translation.AutoTokenizer")
    def test_model_lazy_loads(self, mock_tokenizer_class, mock_model_class):
        """Model and tokenizer should be instantiated on first call."""
        mock_tokenizer_class.from_pretrained.return_value = make_mock_tokenizer()
        mock_model_class.from_pretrained.return_value     = make_mock_model()

        translate("Hello")
        mock_tokenizer_class.from_pretrained.assert_called_once()
        mock_model_class.from_pretrained.assert_called_once()

    @patch("backend.services.translation._model", None)
    @patch("backend.services.translation._tokenizer", None)
    @patch("backend.services.translation.AutoModelForSeq2SeqLM")
    @patch("backend.services.translation.AutoTokenizer")
    def test_returns_original_on_model_exception(
        self, mock_tokenizer_class, mock_model_class
    ):
        """If model.generate throws, return the original text gracefully."""
        tokenizer = make_mock_tokenizer()
        model     = make_mock_model()
        model.generate.side_effect = RuntimeError("out of memory")
        mock_tokenizer_class.from_pretrained.return_value = tokenizer
        mock_model_class.from_pretrained.return_value     = model

        result = translate("Hello world")
        assert result == "Hello world"