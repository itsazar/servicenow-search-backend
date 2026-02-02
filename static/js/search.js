document.addEventListener('DOMContentLoaded', function () {
  const form = document.getElementById('search-form');
  const resultsEl = document.getElementById('results');

  if (!form) return;

  form.addEventListener('submit', async function (e) {
    e.preventDefault();
    const q = document.getElementById('q').value.trim();
    if (!q) return; // ignore empty
    const top_k = 50;
    const threshold = 0.5;

    // show loading empty card
    resultsEl.innerHTML = `<div class="empty-card"><div style="opacity:.6">Searching…</div></div>`;

    try {
      const resp = await fetch('/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ q, top_k, threshold }),
      });
      if (!resp.ok) {
        const err = await resp.json().catch(() => ({}));
        resultsEl.innerHTML = `<div class="empty-card"><div class="error">${escapeHtml(err.error||'Search failed')}</div></div>`;
        return;
      }
      const data = await resp.json();
      renderResults(data.results || []);
    } catch (err) {
      resultsEl.innerHTML = `<div class="empty-card"><div class="error">Network error</div></div>`;
    }
  });

  function renderResults(list) {
    if (!list || list.length === 0) {
      resultsEl.innerHTML = `
        <div class="empty-card">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M21 21l-4.35-4.35" stroke="#9aa6b2" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/><circle cx="11" cy="11" r="6" stroke="#9aa6b2" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>
          <h3>No similar ServiceNow questions found</h3>
          <p>Try adjusting your question or ask a new one.</p>
        </div>`;
      return;
    }

    const grid = document.createElement('div');
    grid.className = 'results-grid';

    list.forEach(r => {
      const article = document.createElement('article');
      article.className = 'card result';
      const url = r.url || '#';
      article.innerHTML = `
        <div class="score-badge">${escapeHtml(r.score)}</div>
        <h3><a href="${escapeHtml(url)}" target="_blank" rel="noopener">${escapeHtml(r.title || r.id || 'result')}</a></h3>
        <p class="snippet">${escapeHtml(r.snippet || r.question_text || '')}</p>
        <a class="source" href="${escapeHtml(url)}" target="_blank" rel="noopener">Source</a>
      `;
      grid.appendChild(article);
    });

    resultsEl.innerHTML = '';
    resultsEl.appendChild(grid);
  }

  function escapeHtml(s) {
    if (s === null || s === undefined) return '';
    return String(s)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

});
