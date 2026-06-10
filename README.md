# 🎙️ Poly Subs

Real-time speech translation that converts spoken audio into live translated subtitles using **Faster-Whisper** (ASR) and **NLLB-200** (translation).

## Architecture

```
Browser mic
   │  PCM Int16 chunks (WebSocket)
   ▼
FastAPI /ws/audio
   │
   ├─► Faster-Whisper  → transcript text
   └─► NLLB-200        → translated text
           │
           ▼ JSON {"text": "...", "translated": "...", "ts": ...}
       Browser subtitle display
```

## Requirements

- Python 3.10+
- For GPU acceleration: CUDA 11.8+ and a matching PyTorch build

## Installation

PyTorch must be installed separately before everything else due to its custom package index.

**Step 1 — PyTorch (CPU)**
```bash
pip install torch==2.3.0 torchvision==0.18.0 --index-url https://download.pytorch.org/whl/cpu
```

**Step 2 — Everything else**
```bash
pip install -r requirements.txt
```

## Quick Start

**1. Download models** (one-time, ~1–2 GB)

```bash
# Mac / Linux
make download-models

# Windows
python scripts/download_models.py
```

**2. Configure**

```bash
# Mac / Linux
cp .env.example .env

# Windows
copy .env.example .env
```

Edit `.env` to set your target language and model sizes.

**3. Run**

```bash
# Mac / Linux
make dev       # development with hot-reload
make run       # production

# Windows (local only)
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload   # development
uvicorn backend.main:app --host 127.0.0.1 --port 8000             # production
```

Open http://localhost:8000 or http://127.0.0.1:8000 and click **Start**.

> If the browser prompts for microphone access, allow it. The app requires a local microphone permission and must run over localhost.

## Configuration

All options live in `.env`. Key settings:

| Variable | Default | Notes |
|---|---|---|
| `WHISPER_MODEL_SIZE` | `base` | `tiny` = fastest, `large-v3` = most accurate |
| `WHISPER_LANGUAGE` | *(auto-detect)* | Force source language, e.g. `es`, `fr` |
| `NLLB_TARGET_LANGUAGE` | `eng_Latn` | BCP-47 + script tag (see table below) |
| `AUDIO_CHUNK_SECONDS` | `2.0` | Larger = more context but higher latency |

### Supported target languages (common)

| Language | Code |
|---|---|
| English | `eng_Latn` |
| Spanish | `spa_Latn` |
| French | `fra_Latn` |
| German | `deu_Latn` |
| Mandarin (Simplified) | `zho_Hans` |
| Japanese | `jpn_Jpan` |
| Arabic | `arb_Arab` |

NLLB-200 supports 200 languages in total. Full list: [NLLB language codes](https://github.com/facebookresearch/flores/blob/main/flores200/README.md#languages-in-flores-200).