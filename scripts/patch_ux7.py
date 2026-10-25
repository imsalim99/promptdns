"""One-off patch: dashboard UX round 7 (owner feedback).
- Recent-activity card gets a close button.
- Domains-screen scan result now renders in a proper panel like Overview
  (it was rendering inside a faint <p> placeholder).
"""
import pathlib

p = pathlib.Path("src/pages/app.astro")
s = p.read_text(encoding="utf-8")

# 1. Domains screen: status line becomes a real panel container
old = """      const statusLine = document.createElement('p');
      statusLine.id = 'dom-scan-status';
      statusLine.className = 'pd-panel-note';
      statusLine.hidden = true;"""
new = """      const statusLine = document.createElement('div');
      statusLine.id = 'dom-scan-status';
      statusLine.className = 'pd-panel';
      statusLine.hidden = true;"""
assert old in s, "statusLine anchor"
s = s.replace(old, new, 1)

# 2. showActivityCard: normalize container to a panel, add close button
old = """    async function showActivityCard(domainId: number, container: HTMLElement): Promise<void> {
      container.hidden = false;
      container.innerHTML = '<p class="pd-panel-note">Loading activity…</p>';
      try {
        const res = await fetch('/api/domains/history?id=' + domainId);
        const data = await res.json() as { runs: { outcome: string; score: number | null; changes: number; ran_at: string }[] };
        const runs = (data.runs ?? []).slice(0, 4);
        const latest = runs[0];
        const headline = !latest ? 'Scan complete - first run logged.'
          : latest.outcome === 'changed' ? 'Something changed during this scan.'
          : latest.outcome === 'unresolvable' ? 'The domain did not resolve on this run.'
          : 'No changes since the previous snapshot.';
        const color = !latest || latest.outcome === 'ok' ? 'var(--pd-pass)' : latest.outcome === 'changed' ? 'var(--pd-warn)' : 'var(--pd-fail)';
        container.innerHTML =
          '<div class="pd-act-head" style="color:' + color + '">' + headline + '</div>' +
          '<p class="pd-act-expl">' + esc(SCAN_EXPLANATION) + '</p>' +
          (runs.length
            ? '<table class="pd-table pd-table-sm" style="width:100%"><thead><tr><th>Time (UTC)</th><th>Result</th><th>Score</th></tr></thead><tbody>' +
              runs.map((r) => '<tr><td class="pd-mono">' + r.ran_at.slice(0, 16).replace('T', ' ') + '</td><td>' + (r.outcome === 'changed' ? '<span class="pd-text-warn">changed (' + r.changes + ')</span>' : r.outcome === 'unresolvable' ? '<span class="pd-text-fail">unresolvable</span>' : '<span class="pd-text-pass">no changes</span>') + '</td><td class="pd-mono">' + (r.score === null ? 'n/a' : r.score) + '</td></tr>').join('') +
              '</tbody></table>'
            : '');
        container.style.borderLeft = '3px solid ' + color;
      } catch {
        container.innerHTML = '<p class="pd-panel-note">Could not load activity.</p>';
      }
    }"""
new = """    async function showActivityCard(domainId: number, container: HTMLElement): Promise<void> {
      container.hidden = false;
      container.className = 'pd-panel';
      container.style.position = 'relative';
      container.innerHTML = '<p class="pd-panel-note">Loading activity…</p>';
      try {
        const res = await fetch('/api/domains/history?id=' + domainId);
        const data = await res.json() as { runs: { outcome: string; score: number | null; changes: number; ran_at: string }[] };
        const runs = (data.runs ?? []).slice(0, 4);
        const latest = runs[0];
        const headline = !latest ? 'Scan complete - first run logged.'
          : latest.outcome === 'changed' ? 'Something changed during this scan.'
          : latest.outcome === 'unresolvable' ? 'The domain did not resolve on this run.'
          : 'No changes since the previous snapshot.';
        const color = !latest || latest.outcome === 'ok' ? 'var(--pd-pass)' : latest.outcome === 'changed' ? 'var(--pd-warn)' : 'var(--pd-fail)';
        container.innerHTML =
          '<button type="button" class="pd-act-close" aria-label="Dismiss activity">×</button>' +
          '<div class="pd-act-head" style="color:' + color + '">' + headline + '</div>' +
          '<p class="pd-act-expl">' + esc(SCAN_EXPLANATION) + '</p>' +
          (runs.length
            ? '<table class="pd-table pd-table-sm" style="width:100%"><thead><tr><th>Time (UTC)</th><th>Result</th><th>Score</th></tr></thead><tbody>' +
              runs.map((r) => '<tr><td class="pd-mono">' + r.ran_at.slice(0, 16).replace('T', ' ') + '</td><td>' + (r.outcome === 'changed' ? '<span class="pd-text-warn">changed (' + r.changes + ')</span>' : r.outcome === 'unresolvable' ? '<span class="pd-text-fail">unresolvable</span>' : '<span class="pd-text-pass">no changes</span>') + '</td><td class="pd-mono">' + (r.score === null ? 'n/a' : r.score) + '</td></tr>').join('') +
              '</tbody></table>'
            : '');
        container.style.borderLeft = '3px solid ' + color;
        container.querySelector('.pd-act-close')!.addEventListener('click', () => {
          container.hidden = true;
          container.innerHTML = '';
        });
      } catch {
        container.innerHTML = '<p class="pd-panel-note">Could not load activity.</p>';
      }
    }"""
assert old in s, "showActivityCard anchor"
s = s.replace(old, new, 1)

# 3. CSS: close button styling
old = """    .pd-act-head { font-family: var(--pd-font-display); font-weight: 600; font-size: 14px; }
    .pd-act-expl { font-size: 12px; color: var(--pd-ink-dim); margin-top: 5px; }"""
new = """    .pd-act-head { font-family: var(--pd-font-display); font-weight: 600; font-size: 14px; }
    .pd-act-expl { font-size: 12px; color: var(--pd-ink-dim); margin-top: 5px; }
    .pd-act-close { position: absolute; top: 10px; right: 12px; font-size: 16px; line-height: 1; color: var(--pd-ink-faint); }
    .pd-act-close:hover { color: var(--pd-ink); }"""
assert old in s, "close css anchor"
s = s.replace(old, new, 1)

p.write_text(s, encoding="utf-8")
print("UX round 7 applied")
