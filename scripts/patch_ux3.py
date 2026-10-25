"""One-off patch: dashboard UX round 3 (owner feedback).
- Sign out moves into an account menu opened from the user chip.
- Sidebar gains site links: All tools + Guides (browse the website while signed in).
- Logo links back to the homepage.
- Overview leads with big per-domain score cards (the bank-balance moment).
- Scan now shows its result inline in the domain head (no tab switching).
"""
import pathlib

p = pathlib.Path("src/pages/app.astro")
s = p.read_text(encoding="utf-8")

# ---------- template ----------
old = """        <div class="pd-logo"><span>Prompt</span><span class="pd-logo-accent">DNS</span></div>"""
new = """        <a href="/" class="pd-logo" title="Back to promptdns.com"><span>Prompt</span><span class="pd-logo-accent">DNS</span></a>"""
assert old in s, "logo anchor"
s = s.replace(old, new, 1)

old = """          <div class="pd-nav-sep" aria-hidden="true"></div>
          <button type="button" class="pd-nav-item" data-screen="settings"><i data-lucide="settings" aria-hidden="true"></i>Settings</button>"""
new = """          <div class="pd-nav-sep" aria-hidden="true"></div>
          <a href="/tools/" class="pd-nav-item"><i data-lucide="wrench" aria-hidden="true"></i>All tools</a>
          <a href="/dns/" class="pd-nav-item"><i data-lucide="book-open" aria-hidden="true"></i>Guides</a>
          <div class="pd-nav-sep" aria-hidden="true"></div>
          <button type="button" class="pd-nav-item" data-screen="settings"><i data-lucide="settings" aria-hidden="true"></i>Settings</button>"""
assert old in s, "site nav anchor"
s = s.replace(old, new, 1)

old = """          <div class="pd-user">
            <span class="pd-avatar" aria-hidden="true">S</span>
            <div><p class="pd-user-mail" id="nav-user-mail"></p><p class="pd-user-role">Owner</p></div>
          </div>
          <button type="button" id="nav-signout" class="pd-link pd-signout">Sign out</button>"""
new = """          <div class="pd-user-wrap">
            <button type="button" class="pd-user" id="nav-user-btn" aria-expanded="false">
              <span class="pd-avatar" aria-hidden="true">S</span>
              <div><p class="pd-user-mail" id="nav-user-mail"></p><p class="pd-user-role">Owner</p></div>
            </button>
            <div id="nav-user-menu" class="pd-user-menu" hidden>
              <a href="/" class="pd-menu-item">Open website</a>
              <a href="/tools/" class="pd-menu-item">All tools</a>
              <button type="button" id="nav-signout" class="pd-menu-item pd-menu-signout">Sign out</button>
            </div>
          </div>"""
assert old in s, "user chip anchor"
s = s.replace(old, new, 1)

# ---------- Overview screen template: hero cards replace stat row + health panel ----------
old = """        <section class="pd-screen" id="screen-overview" hidden>
          <div class="pd-stat-grid">
            <div class="pd-stat"><p class="pd-stat-label">Domains</p><p class="pd-stat-value" id="ov-domains">-</p><p class="pd-stat-note" id="ov-domains-note"></p></div>
            <div class="pd-stat"><p class="pd-stat-label">Open alerts</p><p class="pd-stat-value" id="ov-alerts">-</p><p class="pd-stat-note">unread, newest first on Alerts</p></div>
            <div class="pd-stat"><p class="pd-stat-label">Average score</p><p class="pd-stat-value" id="ov-avg">-</p><p class="pd-stat-note">latest snapshot per domain</p></div>
            <div class="pd-stat"><p class="pd-stat-label">DMARC pass rate</p><p class="pd-stat-value" id="ov-passrate">-</p><p class="pd-stat-note" id="ov-passrate-note">across your domains</p></div>
          </div>

          <div class="pd-grid-2">
            <div class="pd-panel">
              <div class="pd-panel-head"><h2>Domain health</h2><button type="button" class="pd-link" data-goto="domains">All domains →</button></div>
              <div id="ov-health" class="pd-health-list"></div>
            </div>
            <div class="pd-panel">
              <div class="pd-panel-head"><h2>Next step</h2></div>
              <div id="ov-action"></div>
            </div>
          </div>"""
new = """        <section class="pd-screen" id="screen-overview" hidden>
          <div id="ov-hero" class="pd-hero-grid"></div>

          <div class="pd-stat-grid">
            <div class="pd-stat"><p class="pd-stat-label">Open alerts</p><p class="pd-stat-value" id="ov-alerts">-</p><p class="pd-stat-note">unread, newest first on Alerts</p></div>
            <div class="pd-stat"><p class="pd-stat-label">DMARC pass rate</p><p class="pd-stat-value" id="ov-passrate">-</p><p class="pd-stat-note" id="ov-passrate-note">across your domains</p></div>
            <div class="pd-stat"><p class="pd-stat-label">Domains</p><p class="pd-stat-value" id="ov-domains">-</p><p class="pd-stat-note" id="ov-domains-note"></p></div>
          </div>

          <div class="pd-grid-2">
            <div class="pd-panel">
              <div class="pd-panel-head"><h2>Next step</h2></div>
              <div id="ov-action"></div>
            </div>
            <div class="pd-panel">
              <div class="pd-panel-head"><h2>Latest check results</h2><button type="button" class="pd-link" data-goto="domains">All domains →</button></div>
              <div id="ov-health" class="pd-health-list"></div>
            </div>
          </div>"""
assert old in s, "overview template anchor"
s = s.replace(old, new, 1)

# ---------- CSS ----------
old = """    .pd-logo { font-family: var(--pd-font-display); font-weight: 700; font-size: 17px; padding: 2px 8px 14px; }"""
new = """    .pd-logo { font-family: var(--pd-font-display); font-weight: 700; font-size: 17px; padding: 2px 8px 14px; color: var(--pd-ink); text-decoration: none; }
    .pd-hero-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 12px; }
    .pd-hero-card { background: var(--pd-panel); border: 1px solid var(--pd-line); border-radius: 14px; padding: 18px 20px; display: flex; align-items: center; gap: 16px; }
    .pd-hero-score { font-family: var(--pd-font-display); font-weight: 700; font-size: 46px; line-height: 1; }
    .pd-hero-score small { font-size: 14px; color: var(--pd-ink-faint); font-weight: 500; }
    .pd-hero-main { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 6px; }
    .pd-hero-domain { font-family: var(--pd-font-mono); font-size: 15px; font-weight: 500; }
    .pd-hero-meta { font-size: 11px; color: var(--pd-ink-faint); font-family: var(--pd-font-mono); }
    .pd-user-wrap { position: relative; }
    .pd-user { width: 100%; text-align: left; }
    .pd-user-menu { position: absolute; bottom: calc(100% + 6px); left: 0; right: 0; background: var(--pd-panel-2); border: 1px solid var(--pd-line); border-radius: 10px; padding: 5px; box-shadow: 0 10px 30px rgba(0,0,0,.5); z-index: 40; }
    .pd-menu-item { display: block; width: 100%; text-align: left; padding: 8px 10px; border-radius: 7px; font-size: 12.5px; color: var(--pd-ink-dim); text-decoration: none; }
    .pd-menu-item:hover { background: rgba(34,211,238,.08); color: var(--pd-ink); }
    .pd-menu-signout:hover { color: var(--pd-fail); }
    .pd-dd-status { margin-top: 10px; border-radius: 9px; padding: 9px 13px; font-size: 12.5px; border: 1px solid; }"""
assert old in s, "css logo anchor"
s = s.replace(old, new, 1)

# ---------- JS: renderOverview hero ----------
old = """    function renderOverview(o: { domains: number; max: number; alertsOpen: number; avgScore: number | null; dmarc: { reports: number; messages: number; passRate: number | null; daily: DailyPoint[] } }) {
      (document.getElementById('ov-domains') as HTMLElement).textContent = String(o.domains);
      (document.getElementById('ov-domains-note') as HTMLElement).textContent = 'of ' + o.max + ' on Early access';
      (document.getElementById('ov-alerts') as HTMLElement).textContent = String(o.alertsOpen);
      const avg = document.getElementById('ov-avg') as HTMLElement;
      avg.textContent = o.avgScore === null ? '-' : String(o.avgScore);
      avg.className = 'pd-stat-value ' + (o.avgScore === null ? '' : o.avgScore >= 75 ? 'pd-text-pass' : o.avgScore >= 60 ? 'pd-text-warn' : 'pd-text-fail');
      const pr = document.getElementById('ov-passrate') as HTMLElement;
      pr.textContent = o.dmarc.passRate === null ? '-' : o.dmarc.passRate + '%';
      (document.getElementById('ov-passrate-note') as HTMLElement).textContent = o.dmarc.reports > 0 ? o.dmarc.reports + ' report(s), ' + o.dmarc.messages.toLocaleString() + ' messages' : 'no reports yet';
      renderHealthRows(document.getElementById('ov-health')!);"""
new = """    function renderOverview(o: { domains: number; max: number; alertsOpen: number; avgScore: number | null; dmarc: { reports: number; messages: number; passRate: number | null; daily: DailyPoint[] } }) {
      (document.getElementById('ov-domains') as HTMLElement).textContent = String(o.domains);
      (document.getElementById('ov-domains-note') as HTMLElement).textContent = 'of ' + o.max + ' on Early access';
      (document.getElementById('ov-alerts') as HTMLElement).textContent = String(o.alertsOpen);
      const pr = document.getElementById('ov-passrate') as HTMLElement;
      pr.textContent = o.dmarc.passRate === null ? '-' : o.dmarc.passRate + '%';
      (document.getElementById('ov-passrate-note') as HTMLElement).textContent = o.dmarc.reports > 0 ? o.dmarc.reports + ' report(s), ' + o.dmarc.messages.toLocaleString() + ' messages' : 'no reports yet';

      // Hero: the state of your domains, on your face.
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
assert old in s, "renderOverview anchor"
s = s.replace(old, new, 1)

# ---------- JS: doRescan inline status instead of tab switch ----------
old = """        if (data.ok) {
          await Promise.all([loadDomains(), loadOverview()]);
          toast('pass', data.changed ? 'Something changed - new snapshot stored, alert added.' : 'Re-checked: no changes since the last snapshot.');
          if (state.currentDomainId === id) { await openDomain(id); showDomainTab('activity'); }
          if (state.dmarcDomainId === id) void loadDmarcScreen();
        } else {"""
new = """        if (data.ok) {
          await Promise.all([loadDomains(), loadOverview()]);
          if (state.currentDomainId === id) {
            const el = document.getElementById('dd-status');
            if (el) {
              el.style.display = 'block';
              el.className = 'pd-dd-status ' + (data.changed ? 'border-warn/40 bg-warn/10 text-warn' : 'border-pass/40 bg-pass/10 text-pass');
              el.style.borderColor = data.changed ? 'rgba(251,191,36,.4)' : 'rgba(74,222,128,.4)';
              el.style.background = data.changed ? 'rgba(251,191,36,.08)' : 'rgba(74,222,128,.08)';
              el.style.color = data.changed ? 'var(--pd-warn)' : 'var(--pd-pass)';
              el.textContent = data.changed
                ? 'Something changed on this check - new snapshot stored. The diff is in the Changes list below and on the Alerts screen.'
                : 'Re-checked just now: no changes since the last snapshot. This run is logged in the Scan activity list below.';
            }
          }
          if (state.dmarcDomainId === id) void loadDmarcScreen();
        } else {"""
assert old in s, "doRescan anchor"
s = s.replace(old, new, 1)

# openDomain: add the status line element to the head area
old = """      document.getElementById('dd-rescan')!.addEventListener('click', () => void doRescan(d.id));"""
new = """      const status = document.createElement('div');
      status.id = 'dd-status';
      status.style.display = 'none';
      status.className = 'pd-dd-status';
      head.appendChild(status);

      document.getElementById('dd-rescan')!.addEventListener('click', () => void doRescan(d.id));"""
assert old in s, "status element anchor"
s = s.replace(old, new, 1)

# ---------- JS: user menu toggle ----------
old = """    document.getElementById('nav-signout')!.addEventListener('click', async () => {
      await fetch('/api/auth/logout', { method: 'POST' });
      window.location.href = '/login/';
    });"""
new = """    const userBtn = document.getElementById('nav-user-btn')!;
    const userMenu = document.getElementById('nav-user-menu')!;
    userBtn.addEventListener('click', () => {
      const open = userMenu.hidden;
      userMenu.hidden = !open;
      userBtn.setAttribute('aria-expanded', String(open));
    });
    document.addEventListener('click', (e) => {
      if (!userMenu.hidden && !userMenu.contains(e.target as Node) && !userBtn.contains(e.target as Node)) {
        userMenu.hidden = true;
        userBtn.setAttribute('aria-expanded', 'false');
      }
    });
    document.getElementById('nav-signout')!.addEventListener('click', async () => {
      await fetch('/api/auth/logout', { method: 'POST' });
      window.location.href = '/login/';
    });"""
assert old in s, "signout anchor"
s = s.replace(old, new, 1)

p.write_text(s, encoding="utf-8")
print("UX round 3 applied")
