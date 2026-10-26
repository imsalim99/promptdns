"""One-off patch: light theme + themed chart colors for the dashboard.
- Light variable overrides on #dash-app[data-theme='light'].
- All hardcoded rgba literals converted to color-mix() against the theme
  variables so every surface, chip, border and shadow adapts.
- Chart bar fills move to theme variables.
- Appearance toggle in Settings, persisted in localStorage.
"""
import pathlib

p = pathlib.Path("src/pages/app.astro")
s = p.read_text(encoding="utf-8")

CM = "color-mix(in srgb,"

def swap(old, new, tag):
    global s
    assert old in s, tag + " anchor missing"
    s = s.replace(old, new, 1)

# 1. light overrides + on-accent + sidebar grad + app bg
swap(
    """      --pd-font-display: 'Space Grotesk', 'Segoe UI', sans-serif;
      --pd-font-body: 'Inter', 'Segoe UI', sans-serif;
      --pd-font-mono: 'JetBrains Mono', Consolas, monospace;
      font-family: var(--pd-font-body);
      color: var(--pd-ink);
      font-size: 14px;
      line-height: 1.5;
    }""",
    """      --pd-font-display: 'Space Grotesk', 'Segoe UI', sans-serif;
      --pd-font-body: 'Inter', 'Segoe UI', sans-serif;
      --pd-font-mono: 'JetBrains Mono', Consolas, monospace;
      --pd-sidebar-grad: linear-gradient(180deg, #0a0f1e, #070c18);
      --pd-on-accent: #04121a;
      font-family: var(--pd-font-body);
      color: var(--pd-ink);
      background: var(--pd-bg);
      font-size: 14px;
      line-height: 1.5;
    }
    #dash-app[data-theme='light'] {
      --pd-bg: #f5f7fb;
      --pd-panel: #ffffff;
      --pd-panel-2: #eef2f9;
      --pd-line: #d9e1ee;
      --pd-ink: #101828;
      --pd-ink-dim: #4a5568;
      --pd-ink-faint: #8792a3;
      --pd-accent: #0e7490;
      --pd-violet: #6d28d9;
      --pd-pass: #15803d;
      --pd-warn: #b45309;
      --pd-fail: #b91c1c;
      --pd-sidebar-grad: linear-gradient(180deg, #ffffff, #f5f7fb);
      --pd-on-accent: #ffffff;
    }""",
    "light vars",
)

# 2. sidebar gradient
swap(
    ".pd-sidebar { width: 212px; flex-shrink: 0; border-right: 1px solid var(--pd-line); background: linear-gradient(180deg, #0a0f1e, #070c18);",
    ".pd-sidebar { width: 212px; flex-shrink: 0; border-right: 1px solid var(--pd-line); background: var(--pd-sidebar-grad);",
    "sidebar grad",
)

# 3. rgba -> color-mix conversions
pairs = [
    (".pd-nav-item:hover { background: rgba(34,211,238,.07);",
     ".pd-nav-item:hover { background: " + CM + " var(--pd-accent) 7%, transparent);"),
    (".pd-nav-item.is-active { background: rgba(34,211,238,.12);",
     ".pd-nav-item.is-active { background: " + CM + " var(--pd-accent) 12%, transparent);"),
    (".pd-nav-badge { margin-left: auto; background: rgba(248,113,113,.15); color: var(--pd-fail); border: 1px solid rgba(248,113,113,.35);",
     ".pd-nav-badge { margin-left: auto; background: " + CM + " var(--pd-fail) 15%, transparent); color: var(--pd-fail); border: 1px solid " + CM + " var(--pd-fail) 35%, transparent);"),
    (".pd-health-row:hover { background: rgba(34,211,238,.05); }",
     ".pd-health-row:hover { background: " + CM + " var(--pd-accent) 5%, transparent); }"),
    (".pd-chip-pass { color: var(--pd-pass); border-color: rgba(74,222,128,.35); background: rgba(74,222,128,.07); }",
     ".pd-chip-pass { color: var(--pd-pass); border-color: " + CM + " var(--pd-pass) 35%, transparent); background: " + CM + " var(--pd-pass) 8%, transparent); }"),
    (".pd-chip-warn { color: var(--pd-warn); border-color: rgba(251,191,36,.35); background: rgba(251,191,36,.07); }",
     ".pd-chip-warn { color: var(--pd-warn); border-color: " + CM + " var(--pd-warn) 35%, transparent); background: " + CM + " var(--pd-warn) 8%, transparent); }"),
    (".pd-chip-fail { color: var(--pd-fail); border-color: rgba(248,113,113,.35); background: rgba(248,113,113,.07); }",
     ".pd-chip-fail { color: var(--pd-fail); border-color: " + CM + " var(--pd-fail) 35%, transparent); background: " + CM + " var(--pd-fail) 8%, transparent); }"),
    (".pd-chip-info { color: var(--pd-accent); border-color: rgba(34,211,238,.35); background: rgba(34,211,238,.07); }",
     ".pd-chip-info { color: var(--pd-accent); border-color: " + CM + " var(--pd-accent) 35%, transparent); background: " + CM + " var(--pd-accent) 8%, transparent); }"),
    (".pd-action-card { border: 1px solid rgba(34,211,238,.3); background: rgba(34,211,238,.05);",
     ".pd-action-card { border: 1px solid " + CM + " var(--pd-accent) 30%, transparent); background: " + CM + " var(--pd-accent) 5%, transparent);"),
    (".pd-action-card.is-fix { border-color: rgba(248,113,113,.3); background: rgba(248,113,113,.05); }",
     ".pd-action-card.is-fix { border-color: " + CM + " var(--pd-fail) 30%, transparent); background: " + CM + " var(--pd-fail) 5%, transparent); }"),
    (".pd-btn:hover { border-color: rgba(34,211,238,.45); }",
     ".pd-btn:hover { border-color: " + CM + " var(--pd-accent) 45%, transparent); }"),
    (".pd-btn-danger:hover { border-color: rgba(248,113,113,.5);",
     ".pd-btn-danger:hover { border-color: " + CM + " var(--pd-fail) 50%, transparent);"),
    (".pd-btn.is-me { border-color: rgba(74,222,128,.45); color: var(--pd-pass); background: rgba(74,222,128,.07); }",
     ".pd-btn.is-me { border-color: " + CM + " var(--pd-pass) 45%, transparent); color: var(--pd-pass); background: " + CM + " var(--pd-pass) 8%, transparent); }"),
    (".pd-toast > .pd-toast-pass { border-color: rgba(74,222,128,.4); background: rgba(74,222,128,.1);",
     ".pd-toast > .pd-toast-pass { border-color: " + CM + " var(--pd-pass) 40%, transparent); background: " + CM + " var(--pd-pass) 10%, transparent);"),
    (".pd-toast > .pd-toast-warn { border-color: rgba(251,191,36,.4); background: rgba(251,191,36,.1);",
     ".pd-toast > .pd-toast-warn { border-color: " + CM + " var(--pd-warn) 40%, transparent); background: " + CM + " var(--pd-warn) 10%, transparent);"),
    (".pd-toast > .pd-toast-fail { border-color: rgba(248,113,113,.4); background: rgba(248,113,113,.1);",
     ".pd-toast > .pd-toast-fail { border-color: " + CM + " var(--pd-fail) 40%, transparent); background: " + CM + " var(--pd-fail) 10%, transparent);"),
    ("box-shadow: 0 8px 30px rgba(0,0,0,.45); display: flex; align-items: center; gap: 10px; border: 1px solid; }",
     "box-shadow: 0 8px 30px " + CM + " var(--pd-ink) 20%, transparent); display: flex; align-items: center; gap: 10px; border: 1px solid; }"),
    (".pd-input:focus { outline: none; border-color: var(--pd-accent); box-shadow: 0 0 0 2px rgba(34,211,238,.2); }",
     ".pd-input:focus { outline: none; border-color: var(--pd-accent); box-shadow: 0 0 0 2px " + CM + " var(--pd-accent) 20%, transparent); }"),
    (".pd-table td { padding: 9px 10px; border-bottom: 1px solid rgba(28,42,71,.5);",
     ".pd-table td { padding: 9px 10px; border-bottom: 1px solid " + CM + " var(--pd-line) 60%, transparent);"),
    (".pd-alert.is-unread { background: rgba(34,211,238,.04); }",
     ".pd-alert.is-unread { background: " + CM + " var(--pd-accent) 4%, transparent); }"),
    (".pd-alert-diff { font-family: var(--pd-font-mono); font-size: 12px; background: rgba(0,0,0,.25);",
     ".pd-alert-diff { font-family: var(--pd-font-mono); font-size: 12px; background: " + CM + " var(--pd-ink) 7%, transparent);"),
    ("box-shadow: 0 10px 30px rgba(0,0,0,.5); z-index: 40; }",
     "box-shadow: 0 10px 30px " + CM + " var(--pd-ink) 22%, transparent); z-index: 40; }"),
    (".pd-menu-item:hover { background: rgba(34,211,238,.08);",
     ".pd-menu-item:hover { background: " + CM + " var(--pd-accent) 8%, transparent);"),
]
for old_css, new_css in pairs:
    swap(old_css, new_css, old_css[:60])

# 4. primary button / avatar text color
swap(
    ".pd-btn-primary { background: linear-gradient(90deg, var(--pd-accent), var(--pd-violet)); color: #04121a;",
    ".pd-btn-primary { background: linear-gradient(90deg, var(--pd-accent), var(--pd-violet)); color: var(--pd-on-accent);",
    "btn primary",
)
swap(
    ".pd-avatar { width: 28px; height: 28px; border-radius: 99px; background: linear-gradient(135deg, var(--pd-accent), var(--pd-violet)); color: #04121a;",
    ".pd-avatar { width: 28px; height: 28px; border-radius: 99px; background: linear-gradient(135deg, var(--pd-accent), var(--pd-violet)); color: var(--pd-on-accent);",
    "avatar",
)

# 5. chart bar fills -> theme vars (in drawBars template strings)
swap(
    'fill="#4ade80" opacity="0.75"',
    'fill="var(--pd-pass)" opacity="0.75"',
    "chart pass fill",
)
swap(
    'fill="#f87171" opacity="0.8"',
    'fill="var(--pd-fail)" opacity="0.8"',
    "chart fail fill",
)

# 6. appearance toggle in Settings (top of the grid)
swap(
    """        <section class="pd-screen" id="screen-settings" hidden>
          <div class="pd-grid-2">
            <div class="pd-panel">
              <div class="pd-panel-head"><h2>Account</h2></div>""",
    """        <section class="pd-screen" id="screen-settings" hidden>
          <div class="pd-grid-2">
            <div class="pd-panel">
              <div class="pd-panel-head"><h2>Appearance</h2></div>
              <div class="pd-form-row">
                <span class="pd-form-label">Dashboard theme</span>
                <span style="display:flex;gap:8px">
                  <button type="button" class="pd-btn pd-btn-xs" data-theme-set="dark" aria-pressed="true">Dark</button>
                  <button type="button" class="pd-btn pd-btn-xs" data-theme-set="light" aria-pressed="false">Light</button>
                </span>
              </div>
            </div>
            <div class="pd-panel">
              <div class="pd-panel-head"><h2>Account</h2></div>""",
    "settings appearance anchor",
)

# 7. theme apply/restore + toggle wiring at the top of the script
swap(
    """    const state = { domains: [] as DomainRow[], currentDomainId: null as number | null, dmarcDomainId: null as number | null, max: 3 };""",
    """    const state = { domains: [] as DomainRow[], currentDomainId: null as number | null, dmarcDomainId: null as number | null, max: 3 };

    function applyTheme(t: 'dark' | 'light') {
      const app = document.getElementById('dash-app')!;
      if (t === 'light') app.setAttribute('data-theme', 'light');
      else app.removeAttribute('data-theme');
      try { localStorage.setItem('pd-theme', t); } catch { /* private mode */ }
      document.querySelectorAll('[data-theme-set]').forEach((b) => {
        const active = (b as HTMLElement).dataset.themeSet === t;
        b.setAttribute('aria-pressed', String(active));
        b.classList.toggle('pd-theme-active', active);
      });
    }
    try {
      const savedTheme = localStorage.getItem('pd-theme');
      if (savedTheme === 'light' || savedTheme === 'dark') applyTheme(savedTheme);
    } catch { /* ignore */ }""",
    "theme state anchor",
)

# 8. toggle listeners (next to alerts-read wiring)
swap(
    """    document.getElementById('alerts-read')!.addEventListener('click', async () => {
      await fetch('/api/alerts/read', { method: 'POST' });
      await loadAlerts();
    });""",
    """    document.getElementById('alerts-read')!.addEventListener('click', async () => {
      await fetch('/api/alerts/read', { method: 'POST' });
      await loadAlerts();
    });

    document.querySelectorAll('[data-theme-set]').forEach((b) => {
      b.addEventListener('click', () => applyTheme((b as HTMLElement).dataset.themeSet as 'dark' | 'light'));
    });""",
    "theme listeners anchor",
)

# 9. theme-active button style (anchored to the converted menu hover rule)
swap(
    "    .pd-menu-item:hover { background: " + CM + " var(--pd-accent) 8%, transparent); color: var(--pd-ink); }",
    "    .pd-menu-item:hover { background: " + CM + " var(--pd-accent) 8%, transparent); color: var(--pd-ink); }\n    .pd-theme-active { border-color: var(--pd-accent); color: var(--pd-accent); }",
    "theme active css anchor",
)

p.write_text(s, encoding="utf-8")
print("theme patch applied")
