"""One-off patch: Records tab in domain detail (mockup parity)."""
import pathlib

p = pathlib.Path("src/pages/app.astro")
s = p.read_text(encoding="utf-8")

# 1. Records tab in the template
old = """          <div class="pd-tabs" role="tablist" aria-label="Domain sections">
            <button type="button" class="pd-tab is-active" data-tab="auth" aria-selected="true">Authentication</button>
            <button type="button" class="pd-tab" data-tab="activity" aria-selected="false">Activity</button>
          </div>
          <div class="pd-tabpanel" id="tab-auth"></div>
          <div class="pd-tabpanel" id="tab-activity" hidden></div>"""
new = """          <div class="pd-tabs" role="tablist" aria-label="Domain sections">
            <button type="button" class="pd-tab is-active" data-tab="auth" aria-selected="true">Authentication</button>
            <button type="button" class="pd-tab" data-tab="records" aria-selected="false">Records</button>
            <button type="button" class="pd-tab" data-tab="activity" aria-selected="false">Activity</button>
          </div>
          <div class="pd-tabpanel" id="tab-auth"></div>
          <div class="pd-tabpanel" id="tab-records" hidden></div>
          <div class="pd-tabpanel" id="tab-activity" hidden></div>"""
assert old in s, "tabs template anchor"
s = s.replace(old, new, 1)

# 2. showDomainTab: generic panel mapping
old = """      document.getElementById('tab-auth')!.hidden = tab !== 'auth';
      document.getElementById('tab-activity')!.hidden = tab !== 'activity';
    }"""
new = """      document.querySelectorAll('#screen-domain .pd-tabpanel').forEach((p) => { p.hidden = p.id !== 'tab-' + tab; });
    }"""
assert old in s, "showDomainTab anchor"
s = s.replace(old, new, 1)

# 3. openDomain: render the records tab content
old = """      showDomainTab('auth');"""
new = """      const recBox = document.getElementById('tab-records')!;
      if (d.records && d.records.length) {
        recBox.innerHTML = '<div class="pd-panel"><div class="pd-panel-head"><h2>DNS records as seen in the last scan</h2><span class="pd-chip pd-chip-info">' + d.records.length + ' record(s)</span></div><div class="pd-table-wrap"><table class="pd-table"><thead><tr><th>Type</th><th>Name</th><th>Value</th></tr></thead><tbody>' +
          d.records.map((r) => '<tr><td class="pd-mono">' + esc(r.type) + '</td><td class="pd-mono">' + esc(r.name) + '</td><td class="pd-mono" style="word-break:break-all">' + esc(r.value) + '</td></tr>').join('') +
          '</tbody></table></div><p class="pd-panel-note">Captured during the most recent scan. TXT records include the SPF and DMARC policies.</p></div>';
      } else {
        recBox.innerHTML = '<div class="pd-panel"><div class="pd-panel-head"><h2>DNS records</h2></div><div class="pd-empty">No record values captured yet. Run a scan and they will appear here.</div></div>';
      }

      showDomainTab('auth');"""
assert old in s, "records render anchor"
s = s.replace(old, new, 1)

p.write_text(s, encoding="utf-8")
print("records tab applied")
