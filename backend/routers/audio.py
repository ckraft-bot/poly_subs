"""
WebSocket endpoint for real-time audio streaming.

Protocol:
  Client → Server : raw PCM audio bytes (16-bit, 16 kHz, mono)
  Server → Client : JSON  {"text": "...", "translated": "...", "ts": 1234567890}
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.core.logging import logger
from backend.services.subtitle_stream import SubtitleStream

router = APIRouter(prefix="/ws", tags=["audio"])


@router.websocket("/audio")
async def audio_websocket(websocket: WebSocket):
    await websocket.accept()
    stream = SubtitleStream(websocket)
    logger.info("WebSocket connection opened")

    try:
        async for chunk in stream.receive_audio():
            subtitle = await stream.process(chunk)
            if subtitle:
                await websocket.send_json(subtitle)

    except WebSocketDisconnect:
        logger.info("WebSocket connection closed by client")

    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        try:
            await websocket.send_json({"error": str(e)})
        except Exception:
            pass  # connection may already be gone
        await websocket.close()