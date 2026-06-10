/**
 * AudioCapture
 * Captures microphone input via the Web Audio API and streams
 * raw PCM Int16 chunks to a callback.
 */
class AudioCapture {
  constructor({ sampleRate = 16000, chunkMs = 250, onChunk } = {}) {
    this.sampleRate = sampleRate;
    this.chunkMs    = chunkMs;
    this.onChunk    = onChunk;

    this._ctx       = null;
    this._source    = null;
    this._processor = null;
    this._stream    = null;
  }

  async start() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      throw new Error('Browser does not support microphone capture. Use a modern browser and open the app over localhost.');
    }

    const constraints = {
      audio: {
        sampleRate:   this.sampleRate,
        channelCount: 1,       // mono
        echoCancellation:  true,
        noiseSuppression:  true,
        autoGainControl:   true,
      },
      video: false,
    };

    try {
      this._stream = await navigator.mediaDevices.getUserMedia(constraints);
    } catch (err) {
      console.warn('Audio capture failed with strict constraints:', err);
      if (err.name === 'OverconstrainedError' || err.name === 'NotReadableError') {
        this._stream = await navigator.mediaDevices.getUserMedia({ audio: true, video: false });
      } else {
        throw err;
      }
    }

    this._ctx    = new AudioContext({ sampleRate: this.sampleRate });
    this._source = this._ctx.createMediaStreamSource(this._stream);

    // Buffer size closest to the requested chunkMs
    const bufferSize = this._nearestPow2(
      this.sampleRate * (this.chunkMs / 1000)
    );

    this._processor = this._ctx.createScriptProcessor(bufferSize, 1, 1);
    this._processor.onaudioprocess = (e) => {
      const float32 = e.inputBuffer.getChannelData(0);
      const int16   = this._toInt16(float32);
      if (this.onChunk) this.onChunk(int16.buffer);
    };

    this._source.connect(this._processor);
    this._processor.connect(this._ctx.destination);
  }

  stop() {
    this._processor?.disconnect();
    this._source?.disconnect();
    this._ctx?.close();
    this._stream?.getTracks().forEach((t) => t.stop());
    this._ctx = this._source = this._processor = this._stream = null;
  }

  // ── helpers ──────────────────────────────────────────────────────────

  _toInt16(float32) {
    const out = new Int16Array(float32.length);
    for (let i = 0; i < float32.length; i++) {
      const s = Math.max(-1, Math.min(1, float32[i]));
      out[i]  = s < 0 ? s * 0x8000 : s * 0x7fff;
    }
    return out;
  }

  _nearestPow2(n) {
    return Math.pow(2, Math.round(Math.log2(n)));
  }
}