"""One-off patch: roadmap always visible on the Email screen + fresher no-report copy.
Roadmap shows even before reports arrive (the journey the user is on);
the no-reports setup copy acknowledges an already-published record.
"""
import pathlib

p = pathlib.Path("src/pages/app.astro")
s = p.read_text(encoding="utf-8")

# 1. restructure renderDmarc: roadmap first, always
old = """        const markMap = new Map((data.marks ?? []).map((m) => [m.source_ip, m.mark]));
        const parts: string[] = [];

        if (!data.summary || data.summary.reports === 0) {
          parts.push('<div class="pd-panel"><div class="pd-panel-head"><h2>No reports yet</h2></div>' +
            '<div class="pd-empty" style="text-align:left">Setup:<br><br>1. Publish your DMARC record with <span class="pd-mono">rua=mailto:reports@promptdns.com</span> - the <a href="/dmarc-record-generator/">record generator</a> builds it.<br><br>2. First aggregate reports from Gmail, Microsoft, and Yahoo typically arrive within 24-48 hours of the record going live.<br><br>3. Reports show up here automatically; nothing else to configure.</div></div>');
          box.innerHTML = parts.join('');
          return;
        }
        const sum = data.summary;"""
new = """        const markMap = new Map((data.marks ?? []).map((m) => [m.source_ip, m.mark]));
        const parts: string[] = [];

        // Enforcement roadmap - always visible: it is the journey, reports or not.
        const drow = state.domains.find((x) => x.id === id);
        const policyMatch = drow?.checks?.find((c) => c.id === 'dmarc')?.value.match(/p=(none|quarantine|reject)/);
        const policy = policyMatch ? policyMatch[1] : null;
        const stepCls = (name: string) => policy === name ? 'is-current' : (name === 'none' ? 'is-done' : '');
        const stepStatus = (name: string) => {
          if (policy === name) return 'You are here';
          if (name === 'none') return 'Complete - the record is live';
          if (name === 'quarantine') return policy === 'reject' ? 'Complete' : 'Ready when every source is marked and passing';
          return 'After a clean stretch on quarantine';
        };
        const roadmapHtml = '<div class="pd-panel"><div class="pd-panel-head"><h2>Enforcement roadmap</h2><span class="pd-chip ' + (policy === 'reject' ? 'pd-chip-pass' : 'pd-chip-warn') + '">currently p=' + (policy ?? 'unknown') + '</span></div>' +
          '<div class="pd-roadmap">' +
          '<div class="pd-roadmap-step ' + stepCls('none') + '"><p class="pd-roadmap-name">1 · p=none</p><p class="pd-roadmap-desc">Monitor only. Read reports, mark every source, fix legitimate senders that fail.</p><p class="pd-roadmap-status">' + stepStatus('none') + '</p></div>' +
          '<div class="pd-roadmap-step ' + stepCls('quarantine') + '"><p class="pd-roadmap-name">2 · p=quarantine</p><p class="pd-roadmap-desc">Failing mail goes to spam. Ramp with pct=25 → 100 while watching the reports.</p><p class="pd-roadmap-status">' + stepStatus('quarantine') + '</p></div>' +
          '<div class="pd-roadmap-step ' + stepCls('reject') + '"><p class="pd-roadmap-name">3 · p=reject</p><p class="pd-roadmap-desc">Failing mail is rejected outright. The end goal.</p><p class="pd-roadmap-status">' + stepStatus('reject') + '</p></div>' +
          '</div><p class="pd-panel-note">PromptDNS never changes your policy automatically. Each step is a record edit this screen prepares for you, with a rollback plan.</p></div>';

        if (!data.summary || data.summary.reports === 0) {
          parts.push('<div class="pd-panel"><div class="pd-panel-head"><h2>No reports yet</h2></div>' +
            '<div class="pd-empty" style="text-align:left">Setup:<br><br>1. Publish your DMARC record with <span class="pd-mono">rua=mailto:reports@promptdns.com</span> - the <a href="/dmarc-record-generator/">record generator</a> builds it.<br><br>2. First aggregate reports from Gmail, Microsoft, and Yahoo typically arrive within 24-48 hours of the record going live; give it up to 72.<br><br>3. If nothing arrives after 72 hours: confirm the rua= address matches, and that the Email Routing rule for reports@ is Active.<br><br>4. Reports show up here automatically.</div></div>');
          parts.push(roadmapHtml);
          box.innerHTML = parts.join('');
          return;
        }
        const sum = data.summary;"""
assert old in s, "renderDmarc head anchor"
s = s.replace(old, new, 1)

# 2. remove the now-duplicate roadmap push in the with-data branch
old = """        // Enforcement roadmap (current step from the latest scan's DMARC value)
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
new = """        parts.push(roadmapHtml);"""
assert old in s, "duplicate roadmap anchor"
s = s.replace(old, new, 1)

p.write_text(s, encoding="utf-8")
print("roadmap restructured")
