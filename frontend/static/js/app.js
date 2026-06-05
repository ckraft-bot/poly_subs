/**
 * app.js
 * Wires AudioCapture → WebSocket → SubtitleRenderer.
 * Loaded last so AudioCapture and SubtitleRenderer are already defined.
 */
(function () {
  const btnStart = document.getElementById('btn-start');
  const btnStop  = document.getElementById('btn-stop');
  const statusEl = document.getElementById('status-indicator');

  const renderer = new SubtitleRenderer();
  let capture    = null;
  let socket     = null;

  // ── status helper ──────────────────────────────────────────────────

  function setStatus(state, label) {
    statusEl.className   = `status ${state}`;
    statusEl.textContent = `● ${label}`;
  }

  // ── start ──────────────────────────────────────────────────────────

  async function start() {
    btnStart.disabled = true;
    btnStop.disabled  = false;
    renderer.clear();
    setStatus('live', 'Connecting…');

    const wsUrl = `ws://${location.host}/ws/audio`;
    socket = new WebSocket(wsUrl);
    socket.binaryType = 'arraybuffer';

    socket.onopen = async () => {
      setStatus('live', 'Live');
      capture = new AudioCapture({
        sampleRate: 16000,
        chunkMs:    250,
        onChunk: (buffer) => {
          if (socket?.readyState === WebSocket.OPEN) {
            socket.send(buffer);
          }
        },
      });

      try {
        await capture.start();
      } catch (err) {
        // Mic permission denied or device error
        setStatus('error', 'Mic error');
        renderer.showError(err.message);
        stop();
      }
    };

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.error) {
        setStatus('error', 'Server error');
        renderer.showError(data.error);
      } else {
        renderer.render(data);
      }
    };

    socket.onerror = () => {
      setStatus('error', 'Connection error');
      renderer.showError('WebSocket connection failed.');
    };

    socket.onclose = () => {
      if (capture) stop(); // unexpected close → clean up
    };
  }

  // ── stop ───────────────────────────────────────────────────────────

  function stop() {
    capture?.stop();
    socket?.close();
    capture = socket = null;
    btnStart.disabled = false;
    btnStop.disabled  = true;
    setStatus('idle', 'Idle');
  }

  // ── bind buttons ───────────────────────────────────────────────────

  btnStart.addEventListener('click', start);
  btnStop.addEventListener('click',  stop);
})();