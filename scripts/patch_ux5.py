"""One-off patch: dashboard UX round 5 (owner feedback).
- Score shown as grade-colored text, no rectangle boxes anywhere.
- Settings + Billing items in the avatar menu (billing scrolls to its panel).
- Hero-card Scan now updates the card in place (score, grade, time, status line).
- Domains table gets a per-row Scan button with an inline result line.
- Overview gets a highlighted Add domain button.
"""
import pathlib

p = pathlib.Path("src/pages/app.astro")
s = p.read_text(encoding="utf-8")

# ---------- 1. score style: plain colored text, no box ----------
old = """    .pd-score { font-family: var(--pd-font-display); font-weight: 700; font-size: 17px; width: 40px; height: 40px; border-radius: 10px; display: grid; place-items: center; flex-shrink: 0; }
    .pd-score-a, .pd-score-b { color: var(--pd-pass); background: rgba(74,222,128,.1); border: 1px solid rgba(74,222,128,.3); }
    .pd-score-c, .pd-score-d { color: var(--pd-warn); background: rgba(251,191,36,.1); border: 1px solid rgba(251,191,36,.3); }
    .pd-score-f { color: var(--pd-fail); background: rgba(248,113,113,.1); border: 1px solid rgba(248,113,113,.3); }"""
new = """    .pd-score { font-family: var(--pd-font-display); font-weight: 700; font-size: 15px; color: var(--pd-ink); }
    .pd-score-a, .pd-score-b { color: var(--pd-pass); }
    .pd-score-c, .pd-score-d { color: var(--pd-warn); }
    .pd-score-f { color: var(--pd-fail); }"""
assert old in s, "score css anchor"
s = s.replace(old, new, 1)

# ---------- 2. avatar menu: Settings + Billing ----------
old = """            <div id="nav-user-menu" class="pd-user-menu" hidden>
              <a href="/" class="pd-menu-item">Open website</a>
              <a href="/tools/" class="pd-menu-item">All tools</a>
              <button type="button" id="nav-signout" class="pd-menu-item pd-menu-signout">Sign out</button>
            </div>"""
new = """            <div id="nav-user-menu" class="pd-user-menu" hidden>
              <button type="button" class="pd-menu-item" data-menu-goto="settings">Settings</button>
              <button type="button" class="pd-menu-item" data-menu-goto="settings" data-menu-scroll="billing-panel">Billing</button>
              <a href="/" class="pd-menu-item">Open website</a>
              <a href="/tools/" class="pd-menu-item">All tools</a>
              <button type="button" id="nav-signout" class="pd-menu-item pd-menu-signout">Sign out</button>
            </div>"""
assert old in s, "menu anchor"
s = s.replace(old, new, 1)

old = "            <div class=\"pd-panel\">\n              <div class=\"pd-panel-head\"><h2>Billing</h2><span class=\"pd-planned-chip\">at launch</span></div>"
new = "            <div class=\"pd-panel\" id=\"billing-panel\">\n              <div class=\"pd-panel-head\"><h2>Billing</h2><span class=\"pd-planned-chip\">at launch</span></div>"
assert old in s, "billing panel anchor"
s = s.replace(old, new, 1)

# ---------- 3. Overview: Add domain button in the hero header row ----------
old = """        <section class="pd-screen" id="screen-overview" hidden>
          <div id="ov-hero" class="pd-hero-grid"></div>"""
new = """        <section class="pd-screen" id="screen-overview" hidden>
          <div class="pd-hero-head">
            <div>
              <p class="font-mono text-xs uppercase tracking-widest" style="color:var(--pd-ink-faint)">Your domains</p>
              <h2 class="pd-hero-heading">Live security scores, checked every 6 hours</h2>
            </div>
            <button type="button" class="pd-btn pd-btn-primary" id="ov-add"><i data-lucide="plus" aria-hidden="true"></i>Add domain</button>
          </div>
          <div id="ov-hero" class="pd-hero-grid"></div>"""
assert old in s, "hero head anchor"
s = s.replace(old, new, 1)

old = """    .pd-hero-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 12px; }"""
new = """    .pd-hero-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 12px; }
    .pd-hero-head { display: flex; align-items: center; justify-content: space-between; gap: 12px; flex-wrap: wrap; }
    .pd-hero-heading { font-size: 15px; margin-top: 2px; }
    .pd-hero-status { margin-top: 7px; font-size: 11px; }
    .pd-hero-actions { display: flex; flex-direction: column; gap: 6px; align-items: flex-end; }
    .pd-hero-actions .pd-link { font-size: 11px; }"""
assert old in s, "hero css anchor"
s = s.replace(old, new, 1)

# ---------- 4. renderHeroCard with in-place updates + Details link; renderHero() ----------
old = """      // Hero: the state of your domains, on your face.
      const hero = document.getElementById('ov-hero')!;
      hero.innerHTML = '';
      if (!state.domains.length) {
        hero.innerHTML = '<div class="pd-empty" style="grid-column:1/-1">No domains monitored yet. Add one from the Domains screen and its live health score appears here.</div>';
      }
      for (const d of state.domains) {
        const card = document.createElement('div');
        card.className = 'pd-hero-card';
        const colorCls = gradeClass(d.grade);
        card.innerHTML =
          '<div class="pd-hero-score ' + colorCls + '">' + (d.score ?? '-') + '<small>/100</small></div>' +
          '<div class="pd-hero-main">' +
          '<p class="pd-hero-domain">' + esc(d.domain) + (d.paused ? ' <span class="pd-chip pd-chip-warn">paused</span>' : '') + '</p>' +
          '<div class="pd-health-meta">' + domainChips(d, 3) + '</div>' +
          '<p class="pd-hero-meta">Grade ' + (d.grade ?? '-') + (d.checkedAt ? ' · checked ' + d.checkedAt.slice(11, 16) + ' UTC' : '') + '</p>' +
          '</div>' +
          '<div class="pd-hero-actions"><button type="button" class="pd-btn pd-btn-sm" data-scan="' + d.id + '">Scan now</button></div>';
        hero.appendChild(card);
      }
      hero.querySelectorAll('[data-scan]').forEach((b) => b.addEventListener('click', () => void doRescan(Number((b as HTMLElement).dataset.scan))));

      renderHealthRows(document.getElementById('ov-health')!);"""
new = """      renderHero();
      renderHealthRows(document.getElementById('ov-health')!);"""
assert old in s, "renderOverview hero anchor"
s = s.replace(old, new, 1)

# insert renderHero/renderHeroCard before renderOverview
old = """    function renderOverview(o: { domains: number; max: number; alertsOpen: number; avgScore: number | null; dmarc: { reports: number; messages: number; passRate: number | null; daily: DailyPoint[] } }) {"""
new = """    const lastScan: { id: number; cls: string; text: string } | null = null;
    let lastScanInfo: { id: number; cls: string; text: string } | null = null;

    function renderHeroCard(d: DomainRow): HTMLElement {
      const card = document.createElement('div');
      card.className = 'pd-hero-card';
      card.dataset.hero = String(d.id);
      card.innerHTML =
        '<div class="pd-hero-score ' + gradeClass(d.grade) + '">' + (d.score ?? '-') + '<small>/100</small></div>' +
        '<div class="pd-hero-main">' +
        '<p class="pd-hero-domain">' + esc(d.domain) + (d.paused ? ' <span class="pd-chip pd-chip-warn">paused</span>' : '') + '</p>' +
        '<div class="pd-health-meta">' + domainChips(d, 3) + '</div>' +
        '<p class="pd-hero-meta">Grade ' + (d.grade ?? '-') + (d.checkedAt ? ' · checked ' + d.checkedAt.slice(11, 16) + ' UTC' : '') + '</p>' +
        '<p class="pd-hero-status" hidden></p>' +
        '</div>' +
        '<div class="pd-hero-actions">' +
        '<button type="button" class="pd-btn pd-btn-sm" data-scan="' + d.id + '">Scan now</button>' +
        '<button type="button" class="pd-link" data-open="' + d.id + '">Details →</button>' +
        '</div>';
      const status = card.querySelector('.pd-hero-status') as HTMLElement;
      if (lastScanInfo && lastScanInfo.id === d.id) {
        status.textContent = lastScanInfo.text;
        status.style.color = lastScanInfo.cls;
        status.hidden = false;
      }
      card.querySelector('[data-scan]')!.addEventListener('click', (e) => {
        const b = e.currentTarget as HTMLButtonElement;
        b.disabled = true;
        b.textContent = 'Scanning…';
        void doRescan(d.id).finally(() => { b.disabled = false; b.textContent = 'Scan now'; });
      });
      card.querySelector('[data-open]')!.addEventListener('click', () => openDomain(d.id));
      return card;
    }

    function renderHero() {
      const hero = document.getElementById('ov-hero')!;
      hero.innerHTML = '';
      if (!state.domains.length) {
        hero.innerHTML = '<div class="pd-empty" style="grid-column:1/-1">No domains monitored yet. Click "Add domain" above and its live health score appears here.</div>';
        return;
      }
      for (const d of state.domains) hero.appendChild(renderHeroCard(d));
    }

    function renderOverview(o: { domains: number; max: number; alertsOpen: number; avgScore: number | null; dmarc: { reports: number; messages: number; passRate: number | null; daily: DailyPoint[] } }) {"""
assert old in s, "renderOverview insert anchor"
s = s.replace(old, new, 1)

# ---------- 6. openDomain uses renderDomainHead ----------
old = """      const head = document.getElementById('domain-head')!;
      head.innerHTML =
        '<div class="pd-domain-head"><div class="pd-domain-head-main">' +
        '<h2 class="pd-domain-title">' + esc(d.domain) + '</h2>' +
        '<span class="pd-chip ' + (d.paused ? 'pd-chip-warn' : 'pd-chip-pass') + '">● ' + (d.paused ? 'paused' : 'monitored') + '</span>' +
        '<span class="pd-score ' + gradeClass(d.grade) + '" style="width:46px;height:46px;font-size:20px">' + (d.score ?? '-') + '</span><span class="pd-mono" style="color:var(--pd-ink-faint)">/100</span>' +
        '<span class="pd-grade pd-grade-' + (d.grade ?? 'f').toLowerCase() + '" style="font-size:24px">' + (d.grade ?? '-') + '</span>' +
        '</div><div class="pd-domain-head-actions">' +
        '<button type="button" class="pd-btn pd-btn-sm" id="dd-rescan">Scan now</button>' +
        '<button type="button" class="pd-btn pd-btn-sm" id="dd-pause">' + (d.paused ? 'Resume' : 'Pause') + '</button>' +
        '<button type="button" class="pd-btn pd-btn-sm pd-btn-danger" id="dd-remove">Remove</button>' +
        '</div></div>';

      const status = document.createElement('div');
      status.id = 'dd-status';
      status.style.display = 'none';
      status.className = 'pd-dd-status';
      head.appendChild(status);

      document.getElementById('dd-rescan')!.addEventListener('click', () => void doRescan(d.id));"""
new = """      renderDomainHead(d);"""
assert old in s, "openDomain head anchor"
s = s.replace(old, new, 1)

# ---------- 7. Domains table: per-row Scan + status line; health rows plain score size ----------
old = """      const wrap = document.createElement('div');
      wrap.className = 'pd-table-wrap';
      wrap.innerHTML = '<table class="pd-table"><thead><tr><th>Domain</th><th>Score</th><th>Status</th><th>Last check</th><th></th></tr></thead><tbody></tbody></table>';
      const tbody = wrap.querySelector('tbody')!;
      for (const d of state.domains) {
        const tr = document.createElement('tr');
        tr.innerHTML =
          '<td class="pd-domain-name">' + esc(d.domain) + (d.paused ? ' <span class="pd-chip pd-chip-warn">paused</span>' : '') + '</td>' +
          '<td><span class="pd-score ' + gradeClass(d.grade) + '" style="width:34px;height:34px;font-size:14px">' + (d.score ?? '-') + '</span></td>' +
          '<td>' + domainChips(d, 2) + '</td>' +
          '<td class="pd-cell-dim pd-mono">' + (d.checkedAt ? d.checkedAt.slice(0, 16).replace('T', ' ') : '-') + '</td>' +
          '<td><button type="button" class="pd-link" data-open="' + d.id + '">Open →</button></td>';
        tbody.appendChild(tr);
      }
      list.appendChild(wrap);
      list.querySelectorAll('[data-open]').forEach((b) => b.addEventListener('click', () => openDomain(Number((b as HTMLElement).dataset.open))));"""
new = """      const wrap = document.createElement('div');
      wrap.className = 'pd-table-wrap';
      wrap.innerHTML = '<table class="pd-table"><thead><tr><th>Domain</th><th>Score</th><th>Status</th><th>Last check</th><th></th></tr></thead><tbody></tbody></table>';
      const tbody = wrap.querySelector('tbody')!;
      for (const d of state.domains) {
        const tr = document.createElement('tr');
        tr.innerHTML =
          '<td class="pd-domain-name">' + esc(d.domain) + (d.paused ? ' <span class="pd-chip pd-chip-warn">paused</span>' : '') + '</td>' +
          '<td><span class="pd-score ' + gradeClass(d.grade) + '" style="font-size:14px">' + (d.score ?? '-') + '</span></td>' +
          '<td>' + domainChips(d, 2) + '</td>' +
          '<td class="pd-cell-dim pd-mono">' + (d.checkedAt ? d.checkedAt.slice(0, 16).replace('T', ' ') : '-') + '</td>' +
          '<td style="white-space:nowrap"><button type="button" class="pd-btn pd-btn-xs" data-scan-row="' + d.id + '">Scan</button> <button type="button" class="pd-link" data-open="' + d.id + '">Open →</button></td>';
        tbody.appendChild(tr);
      }
      const statusLine = document.createElement('p');
      statusLine.id = 'dom-scan-status';
      statusLine.className = 'pd-panel-note';
      statusLine.hidden = true;
      list.appendChild(wrap);
      list.appendChild(statusLine);
      list.querySelectorAll('[data-open]').forEach((b) => b.addEventListener('click', () => openDomain(Number((b as HTMLElement).dataset.open))));
      list.querySelectorAll('[data-scan-row]').forEach((b) => {
        const el = b as HTMLButtonElement;
        el.addEventListener('click', () => {
          el.disabled = true;
          el.textContent = 'Scanning…';
          void doRescan(Number(el.dataset.scanRow), statusLine).finally(() => { el.disabled = false; el.textContent = 'Scan'; });
        });
      });"""
assert old in s, "domains table anchor"
s = s.replace(old, new, 1)

# health row score keeps default size now (remove no inline style there) - it already uses plain span.

# ---------- 8. menu goto handlers + overview add button ----------
old = """    document.getElementById('alerts-read')!.addEventListener('click', async () => {
      await fetch('/api/alerts/read', { method: 'POST' });
      await loadAlerts();
    });"""
new = """    document.getElementById('alerts-read')!.addEventListener('click', async () => {
      await fetch('/api/alerts/read', { method: 'POST' });
      await loadAlerts();
    });

    document.querySelectorAll('#nav-user-menu [data-menu-goto]').forEach((b) => {
      b.addEventListener('click', () => {
        userMenu.hidden = true;
        userBtn.setAttribute('aria-expanded', 'false');
        show((b as HTMLElement).dataset.menuGoto!);
        void loadDomains();
        const target = (b as HTMLElement).dataset.menuScroll;
        if (target) document.getElementById(target)?.scrollIntoView({ behavior: 'smooth', block: 'center' });
      });
    });

    document.getElementById('ov-add')!.addEventListener('click', () => {
      show('domains');
      document.getElementById('add-panel')!.hidden = false;
      (document.getElementById('dom-input') as HTMLInputElement).focus();
    });"""
assert old in s, "menu handlers anchor"
s = s.replace(old, new, 1)

p.write_text(s, encoding="utf-8")
print("UX round 5 applied")
