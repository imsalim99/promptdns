"""One-off patch: dashboard UX - enforcement roadmap on the Email (DMARC) screen.
Three-step policy journey (none -> quarantine -> reject) with the current step
highlighted from the domain's latest scan, plus the guardrail note that
PromptDNS never changes the policy automatically.
"""
import pathlib

p = pathlib.Path("src/pages/app.astro")
s = p.read_text(encoding="utf-8")

# ---------- CSS for the roadmap ----------
old = """    .pd-act-head { font-family: var(--pd-font-display); font-weight: 600; font-size: 14px; }"""
new = """    .pd-roadmap { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
    @media (max-width: 760px) { .pd-roadmap { grid-template-columns: 1fr; } }
    .pd-roadmap-step { border: 1px solid var(--pd-line); border-radius: 10px; padding: 12px 14px; }
    .pd-roadmap-step.is-current { border-color: rgba(34,211,238,.5); background: rgba(34,211,238,.05); }
    .pd-roadmap-step.is-done { border-color: rgba(74,222,128,.4); }
    .pd-roadmap-name { font-family: var(--pd-font-display); font-weight: 600; font-size: 13px; }
    .pd-roadmap-desc { font-size: 11.5px; color: var(--pd-ink-dim); margin-top: 4px; }
    .pd-roadmap-status { font-size: 10.5px; color: var(--pd-ink-faint); margin-top: 7px; font-family: var(--pd-font-mono); }
    .pd-act-head { font-family: var(--pd-font-display); font-weight: 600; font-size: 14px; }"""
assert old in s, "css anchor"
s = s.replace(old, new, 1)

# ---------- roadmap panel in renderDmarc, after the sources panel ----------
old = """        const srcs = data.sources ?? [];
        parts.push('<div class="pd-panel"><div class="pd-panel-head"><h2>Sources</h2><span class="pd-panel-note" style="margin-top:0">Mark each sender so reports can tell legitimate mail from spoofing.</span></div><div class="pd-table-wrap"><table class="pd-table"><thead><tr><th>Source IP</th><th>Host (PTR)</th><th>Volume</th><th>SPF</th><th>DKIM</th><th>DMARC</th><th>Marked</th></tr></thead><tbody id="dmarc-src-rows"></tbody></table></div></div>');"""
new = """        const srcs = data.sources ?? [];
        parts.push('<div class="pd-panel"><div class="pd-panel-head"><h2>Sources</h2><span class="pd-panel-note" style="margin-top:0">Mark each sender so reports can tell legitimate mail from spoofing.</span></div><div class="pd-table-wrap"><table class="pd-table"><thead><tr><th>Source IP</th><th>Host (PTR)</th><th>Volume</th><th>SPF</th><th>DKIM</th><th>DMARC</th><th>Marked</th></tr></thead><tbody id="dmarc-src-rows"></tbody></table></div></div>');

        // Enforcement roadmap (current step from the latest scan's DMARC value)
        const drow = state.domains.find((x) => x.id === id);
        const policyMatch = drow?.checks?.find((c) => c.id === 'dmarc')?.value.match(/p=(none|quarantine|reject)/);
        const policy = policyMatch ? policyMatch[1] : null;
        const stepCls = (name: string) => policy === name ? 'is-current' : (name === 'none' ? 'is-done' : '');
        const stepStatus = (name: string) => {
          if (policy === name) return 'You are here';
          if (name === 'none') return 'Complete - reports are flowing';
          if (name === 'quarantine') return policy === 'reject' ? 'Complete' : 'Ready when every source is marked and passing';
          return 'After a clean stretch on quarantine';
        };
        parts.push('<div class="pd-panel"><div class="pd-panel-head"><h2>Enforcement roadmap</h2><span class="pd-chip ' + (policy === 'reject' ? 'pd-chip-pass' : 'pd-chip-warn') + '">currently p=' + (policy ?? 'unknown') + '</span></div>' +
          '<div class="pd-roadmap">' +
          '<div class="pd-roadmap-step ' + stepCls('none') + '"><p class="pd-roadmap-name">1 · p=none</p><p class="pd-roadmap-desc">Monitor only. Read reports, mark every source, fix legitimate senders that fail.</p><p class="pd-roadmap-status">' + stepStatus('none') + '</p></div>' +
          '<div class="pd-roadmap-step ' + stepCls('quarantine') + '"><p class="pd-roadmap-name">2 · p=quarantine</p><p class="pd-roadmap-desc">Failing mail goes to spam. Ramp with pct=25 → 100 while watching the reports.</p><p class="pd-roadmap-status">' + stepStatus('quarantine') + '</p></div>' +
          '<div class="pd-roadmap-step ' + stepCls('reject') + '"><p class="pd-roadmap-name">3 · p=reject</p><p class="pd-roadmap-desc">Failing mail is rejected outright. The end goal.</p><p class="pd-roadmap-status">' + stepStatus('reject') + '</p></div>' +
          '</div><p class="pd-panel-note">PromptDNS never changes your policy automatically. Each step is a record edit this screen prepares for you, with a rollback plan.</p></div>');"""
assert old in s, "sources anchor"
s = s.replace(old, new, 1)

p.write_text(s, encoding="utf-8")
print("roadmap added")
