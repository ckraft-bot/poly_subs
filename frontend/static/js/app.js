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
        const denied = err.name === 'NotAllowedError' || err.name === 'SecurityError' || err.name === 'NotFoundError';
        const message = denied
          ? 'Microphone access denied. Allow microphone permissions for this site and refresh the page.'
          : err.message || 'Unable to start microphone capture.';

        console.error('Audio capture error:', err);
        setStatus('error', 'Mic error');
        renderer.showError(message);
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

    socket.onerror = (event) => {
      console.error('WebSocket error:', event);
      setStatus('error', 'Connection error');
      renderer.showError('WebSocket connection failed. Check that the app is running on localhost and try again.');
    };

    socket.onclose = (event) => {
      if (event && event.code !== 1000) {
        console.warn('WebSocket closed unexpectedly:', event);
      }
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