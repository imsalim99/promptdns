"""One-off patch: dashboard UX round 6 (owner feedback).
Scan now now opens a Recent-activity card in context (Overview below the hero
cards, domain page between head and tabs, Domains table under the table):
result headline, plain explanation of what a scan checks and what "no changes"
means, and the last few runs. Removes the duplicate toast and the sticky
status line.
"""
import pathlib

p = pathlib.Path("src/pages/app.astro")
s = p.read_text(encoding="utf-8")

# ---------- 1. template: activity panel container on Overview ----------
old = """          <div id="ov-hero" class="pd-hero-grid"></div>

          <div class="pd-stat-grid">"""
new = """          <div id="ov-hero" class="pd-hero-grid"></div>

          <div id="ov-activity" class="pd-panel" hidden></div>

          <div class="pd-stat-grid">"""
assert old in s, "overview template anchor"
s = s.replace(old, new, 1)

# ---------- 2. renderDomainHead: dd-status becomes a panel container ----------
old = """        '</div></div>' +
        '<div id="dd-status" class="pd-dd-status" style="display:none"></div>';
      document.getElementById('dd-rescan')!.addEventListener('click', () => void doRescan(d.id, document.getElementById('dd-status') as HTMLElement));"""
new = """        '</div></div>' +
        '<div id="dd-status" hidden></div>';
      document.getElementById('dd-rescan')!.addEventListener('click', () => void doRescan(d.id, document.getElementById('dd-status') as HTMLElement));"""
assert old in s, "renderDomainHead anchor"
s = s.replace(old, new, 1)

# ---------- 3. renderHeroCard: drop the sticky status line ----------
old = """        '<p class="pd-hero-meta">Grade ' + (d.grade ?? '-') + (d.checkedAt ? ' · checked ' + d.checkedAt.slice(11, 16) + ' UTC' : '') + '</p>' +
        '<p class="pd-hero-status" hidden></p>' +
        '</div>' +"""
new = """        '<p class="pd-hero-meta">Grade ' + (d.grade ?? '-') + (d.checkedAt ? ' · checked ' + d.checkedAt.slice(11, 16) + ' UTC' : '') + '</p>' +
        '</div>' +"""
assert old in s, "hero status p anchor"
s = s.replace(old, new, 1)

old = """      const status = card.querySelector('.pd-hero-status') as HTMLElement;
      if (lastScanInfo && lastScanInfo.id === d.id) {
        status.textContent = lastScanInfo.text;
        status.style.color = lastScanInfo.cls;
        status.hidden = false;
      }
      card.querySelector('[data-scan]')!"""
new = """      card.querySelector('[data-scan]')!"""
assert old in s, "lastScanInfo usage anchor"
s = s.replace(old, new, 1)

old = """    let lastScanInfo: { id: number; cls: string; text: string } | null = null;

    function renderHeroCard(d: DomainRow): HTMLElement {"""
new = """    function renderHeroCard(d: DomainRow): HTMLElement {"""
assert old in s, "lastScanInfo decl anchor"
s = s.replace(old, new, 1)

# ---------- 4. doRescan: render the activity card, no toast duplication ----------
old = """    async function doRescan(id: number, statusEl?: HTMLElement): Promise<void> {
      try {
        const res = await fetch('/api/domains/rescan?id=' + id, { method: 'POST' });
        const data = await res.json() as { ok: boolean; error?: string; changed?: boolean };
        if (!data.ok) {
          toast('fail', data.error ?? 'Rescan failed.');
          if (statusEl) { statusEl.textContent = data.error ?? 'Rescan failed.'; statusEl.style.color = 'var(--pd-fail)'; statusEl.hidden = false; }
          return;
        }
        await Promise.all([loadDomains(), loadOverview()]);
        const d = state.domains.find((x) => x.id === id);
        const text = data.changed
          ? 'Something changed - new snapshot stored, alert added.'
          : 'Re-checked just now: no changes since the last snapshot.';
        const cls = data.changed ? 'var(--pd-warn)' : 'var(--pd-pass)';
        toast(data.changed ? 'warn' : 'pass', text);
        lastScanInfo = { id, cls, text: (data.changed ? 'Changed just now. ' : 'Re-checked just now: no changes. ') + 'Last run ' + (d && d.checkedAt ? d.checkedAt.slice(11, 16) + ' UTC' : '') };
        renderHero();
        if (statusEl) { statusEl.textContent = text; statusEl.style.color = cls; statusEl.hidden = false; }
        if (state.currentDomainId === id && d) {
          renderDomainHead(d);
          const dd = document.getElementById('dd-status');
          if (dd) { dd.textContent = text; dd.style.color = cls; dd.style.borderColor = data.changed ? 'rgba(251,191,36,.4)' : 'rgba(74,222,128,.4)'; dd.style.background = data.changed ? 'rgba(251,191,36,.08)' : 'rgba(74,222,128,.08)'; dd.style.display = 'block'; }
        }
        if (state.dmarcDomainId === id) void loadDmarcScreen();
      } catch {
        toast('fail', 'Could not reach the server.');
        if (statusEl) { statusEl.textContent = 'Could not reach the server.'; statusEl.style.color = 'var(--pd-fail)'; statusEl.hidden = false; }
      }
    }"""
new = """    const SCAN_EXPLANATION = 'Every scan checks website DNS, nameservers, mail routing (MX), SPF, DMARC, DKIM, and DNSSEC - the same seven checks as the homepage scanner. "No changes" means none of those values moved since the previous snapshot; the run is still logged.';

    async function showActivityCard(domainId: number, container: HTMLElement): Promise<void> {
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
    }

    async function doRescan(id: number, container?: HTMLElement): Promise<void> {
      if (container) { container.hidden = false; container.innerHTML = '<p class="pd-panel-note">Scanning…</p>'; }
      try {
        const res = await fetch('/api/domains/rescan?id=' + id, { method: 'POST' });
        const data = await res.json() as { ok: boolean; error?: string; changed?: boolean };
        await Promise.all([loadDomains(), loadOverview()]);
        if (!data.ok) {
          if (container) { container.innerHTML = '<p class="pd-panel-note">' + esc(data.error ?? 'Rescan failed.') + '</p>'; container.style.borderLeft = '3px solid var(--pd-fail)'; }
          else toast('fail', data.error ?? 'Rescan failed.');
          return;
        }
        if (container) await showActivityCard(id, container);
        else toast('pass', 'Scan complete.');
        if (state.dmarcDomainId === id) void loadDmarcScreen();
      } catch {
        if (container) { container.innerHTML = '<p class="pd-panel-note">Could not reach the server.</p>'; container.style.borderLeft = '3px solid var(--pd-fail)'; }
        else toast('fail', 'Could not reach the server.');
      }
    }"""
assert old in s, "doRescan anchor"
s = s.replace(old, new, 1)

# ---------- 5. callers pass their containers ----------
old = """      document.getElementById('dd-rescan')!.addEventListener('click', () => void doRescan(d.id, document.getElementById('dd-status') as HTMLElement));"""
new = """      document.getElementById('dd-rescan')!.addEventListener('click', () => void doRescan(d.id, document.getElementById('dd-status') as HTMLElement));"""
assert old in s, "detail caller anchor (unchanged)"
s = s.replace(old, new, 1)

old = """        void doRescan(d.id).finally(() => { b.disabled = false; b.textContent = 'Scan now'; });"""
new = """        void doRescan(d.id, document.getElementById('ov-activity') as HTMLElement).finally(() => { b.disabled = false; b.textContent = 'Scan now'; });"""
assert old in s, "hero caller anchor"
s = s.replace(old, new, 1)

# ---------- 6. CSS for the activity card ----------
old = """    .pd-hero-status { margin-top: 7px; font-size: 11px; }"""
new = """    .pd-act-head { font-family: var(--pd-font-display); font-weight: 600; font-size: 14px; }
    .pd-act-expl { font-size: 12px; color: var(--pd-ink-dim); margin-top: 5px; }"""
assert old in s, "act css anchor"
s = s.replace(old, new, 1)

p.write_text(s, encoding="utf-8")
print("UX round 6 applied")
