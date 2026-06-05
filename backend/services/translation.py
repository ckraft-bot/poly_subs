"""
Translation service wrapping NLLB-200 via HuggingFace Transformers.
Lazy-loads the model on first use.
"""
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from backend.core.config import settings
from backend.core.logging import logger

_tokenizer = None
_model = None


def _get_device() -> str:
    if settings.nllb_device == "auto":
        return "cuda" if torch.cuda.is_available() else "cpu"
    return settings.nllb_device


def _load():
    global _tokenizer, _model
    if _model is None:
        logger.info(f"Loading NLLB model '{settings.nllb_model_name}' ...")
        _tokenizer = AutoTokenizer.from_pretrained(
            settings.nllb_model_name,
            cache_dir=settings.models_dir,
        )
        _model = AutoModelForSeq2SeqLM.from_pretrained(
            settings.nllb_model_name,
            cache_dir=settings.models_dir,
        ).to(_get_device())
        logger.info(f"NLLB model loaded on {_get_device()}.")


def translate(text: str, target_lang: str | None = None) -> str:
    """
    Translate text into the configured target language.
    Returns translated string, or the original text on failure.
    """
    if not text:
        return text

    _load()
    target = target_lang or settings.nllb_target_language
    device = _get_device()

    try:
        inputs = _tokenizer(
            text,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=settings.nllb_max_length,
        ).to(device)

        forced_bos = _tokenizer.convert_tokens_to_ids(target)
        if forced_bos is None:
            raise ValueError(f"Unknown NLLB language code: '{target}'")

        output_ids = _model.generate(
            **inputs,
            forced_bos_token_id=forced_bos,
            max_length=settings.nllb_max_length,
            num_beams=4,
            early_stopping=True,
        )
        translated = _tokenizer.decode(output_ids[0], skip_special_tokens=True)
        logger.debug(f"Translated → {translated}")
        return translated

    except Exception as e:
        logger.error(f"Translation failed: {e}")
        return text  # graceful fallback: return original