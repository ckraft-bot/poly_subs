/**
 * SubtitleRenderer
 * Updates the live subtitle panels and maintains a scrollable history log.
 */
class SubtitleRenderer {
  constructor() {
    this._origEl    = document.getElementById('text-original');
    this._transEl   = document.getElementById('text-translated');
    this._historyEl = document.getElementById('history');
    this._fadeTimer = null;
  }

  render({ text, translated, ts }) {
    // Update live panels
    this._origEl.textContent  = text;
    this._transEl.textContent = translated;

    // Reset opacity in case they were faded
    this._origEl.style.opacity  = '1';
    this._transEl.style.opacity = '1';

    // Fade after 4 s of silence
    clearTimeout(this._fadeTimer);
    this._fadeTimer = setTimeout(() => {
      this._origEl.style.opacity  = '0.35';
      this._transEl.style.opacity = '0.35';
    }, 4000);

    this._addToHistory(text, translated, ts);
  }

  showError(message) {
    this._origEl.textContent  = `⚠ ${message}`;
    this._transEl.textContent = '';
    this._origEl.style.opacity  = '1';
    this._transEl.style.opacity = '1';
  }

  clear() {
    clearTimeout(this._fadeTimer);
    this._origEl.textContent  = '';
    this._transEl.textContent = '';
    this._historyEl.innerHTML = '';
    this._origEl.style.opacity  = '1';
    this._transEl.style.opacity = '1';
  }

  // ── private ──────────────────────────────────────────────────────────

  _addToHistory(orig, trans, ts) {
    const time = new Date(ts).toLocaleTimeString([], {
      hour:   '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });

    const item = document.createElement('div');
    item.className = 'history-item';
    item.innerHTML = `
      <span class="orig">${this._esc(orig)}</span>
      <span class="trans">${this._esc(trans)}</span>
      <span class="time">${time}</span>
    `;
    this._historyEl.prepend(item);

    // Cap history at 50 entries
    while (this._historyEl.children.length > 50) {
      this._historyEl.lastChild.remove();
    }
  }

  _esc(str) {
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
  }
}