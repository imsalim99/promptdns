"""One-off patch: app.astro jank removal.
Root cause: every action called loadDomains() which clears and rebuilds the
whole list (async fetch in between = empty frame = visible flash).
Fix: in-place updates only.
- Scan now: no-change path touches nothing but the status line + timestamp;
  changed path replaces just that one card (synchronous replaceWith).
- Pause/resume: chip + button text updated in place.
- Remove: card.remove() + empty-state handling, no reload.
- Add: new card appended from the POST response, no reload.
loadDomains() remains only for initial page load.
"""
import pathlib

p = pathlib.Path("src/pages/app.astro")
s = p.read_text(encoding="utf-8")

# 1. scan now handler -> in-place updates
old = """      scanNow.addEventListener('click', async () => {
        scanNow.disabled = true;
        scanNow.textContent = 'Scanning…';
        try {
          const res = await fetch(`/api/domains/rescan?id=${d.id}`, { method: 'POST' });
          const data = (await res.json()) as { ok: boolean; error?: string; changed?: boolean };
          if (data.ok) {
            await loadDomains();
            await loadAlerts();
            setCardStatus(
              d.domain,
              data.changed
                ? 'bg-warn/10 text-warn border border-warn/30'
                : 'bg-pass/10 text-pass border border-pass/30',
              data.changed
                ? 'Something changed on this check - new snapshot stored, alert added below.'
                : 'Re-checked just now: no changes since the last snapshot.',
            );
          } else {
            setCardStatus(d.domain, 'bg-fail/10 text-fail border border-fail/30', data.error ?? 'Rescan failed.');
          }
        } catch {
          setCardStatus(d.domain, 'bg-warn/10 text-warn border border-warn/30', 'Could not reach the server.');
        }
        scanNow.disabled = false;
        scanNow.textContent = 'Scan now';
      });"""
new = """      scanNow.addEventListener('click', async () => {
        scanNow.disabled = true;
        scanNow.textContent = 'Scanning…';
        try {
          const res = await fetch(`/api/domains/rescan?id=${d.id}`, { method: 'POST' });
          const data = (await res.json()) as { ok: boolean; error?: string; changed?: boolean; score?: number; grade?: string; checks?: ScanCheck[] };
          if (data.ok) {
            const when = card.querySelector<HTMLElement>('.last-scanned');
            if (when) when.textContent = `Last scanned: ${new Date().toISOString().replace('T', ' ').slice(0, 16)} UTC`;
            if (data.changed && data.checks) {
              const newRow: DomainRow = { ...d, score: data.score ?? d.score, grade: data.grade ?? d.grade, checks: data.checks, checkedAt: new Date().toISOString() };
              card.replaceWith(domainCard(newRow));
              void loadAlerts();
            }
            setCardStatus(
              d.domain,
              data.changed
                ? 'bg-warn/10 text-warn border border-warn/30'
                : 'bg-pass/10 text-pass border border-pass/30',
              data.changed
                ? 'Something changed on this check - new snapshot stored, alert added below.'
                : 'Re-checked just now: no changes since the last snapshot.',
            );
          } else {
            setCardStatus(d.domain, 'bg-fail/10 text-fail border border-fail/30', data.error ?? 'Rescan failed.');
          }
        } catch {
          setCardStatus(d.domain, 'bg-warn/10 text-warn border border-warn/30', 'Could not reach the server.');
        }
        scanNow.disabled = false;
        scanNow.textContent = 'Scan now';
      });"""
assert old in s, "scanNow anchor"
s = s.replace(old, new, 1)

# 2. remove handler -> card.remove()
old = """      del.addEventListener('click', async () => {
        del.disabled = true;
        await fetch(`/api/domains/delete?id=${d.id}`, { method: 'POST' });
        await loadDomains();
      });"""
new = """      del.addEventListener('click', async () => {
        del.disabled = true;
        try {
          const res = await fetch(`/api/domains/delete?id=${d.id}`, { method: 'POST' });
          const data = (await res.json()) as { ok: boolean };
          if (data.ok) {
            card.remove();
            ensureEmptyState();
            void loadAlerts();
            return;
          }
        } catch { /* fall through: re-enable */ }
        del.disabled = false;
      });"""
assert old in s, "del anchor"
s = s.replace(old, new, 1)

# 3. pause handler -> in-place chip/button update
old = """      pauseBtn.addEventListener('click', async () => {
        pauseBtn.disabled = true;
        try {
          await fetch('/api/domains/pause', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id: d.id, paused: !d.paused }),
          });
          await loadDomains();
        } finally {
          pauseBtn.disabled = false;
        }
      });"""
new = """      pauseBtn.addEventListener('click', async () => {
        pauseBtn.disabled = true;
        try {
          const res = await fetch('/api/domains/pause', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id: d.id, paused: !d.paused }),
          });
          const data = (await res.json()) as { ok: boolean; paused: boolean };
          if (data.ok) {
            d.paused = data.paused;
            monitorChip.className = d.paused
              ? 'rounded-full border border-warn/30 bg-warn/10 px-2 py-0.5 font-mono text-[10px] text-warn'
              : 'rounded-full border border-pass/30 bg-pass/10 px-2 py-0.5 font-mono text-[10px] text-pass';
            monitorChip.title = d.paused
              ? 'Automatic monitoring is paused for this domain. Resume to re-enter the 6-hour cycle.'
              : 'This domain is re-checked automatically every 6 hours';
            monitorChip.textContent = d.paused ? '\\u25cf paused' : '\\u25cf monitored';
            pauseBtn.textContent = d.paused ? 'Resume monitoring' : 'Pause monitoring';
          }
        } finally {
          pauseBtn.disabled = false;
        }
      });"""
assert old in s, "pause anchor"
s = s.replace(old, new, 1)

# 4. last-scanned marker class
old = """      if (d.checkedAt) {
        const when = document.createElement('p');
        when.className = 'mt-3 font-mono text-[10px] text-ink-faint';
        when.textContent = `Last scanned: ${d.checkedAt.replace('T', ' ').slice(0, 16)} UTC`;
        card.appendChild(when);
      }"""
new = """      if (d.checkedAt) {
        const when = document.createElement('p');
        when.className = 'last-scanned mt-3 font-mono text-[10px] text-ink-faint';
        when.textContent = `Last scanned: ${d.checkedAt.replace('T', ' ').slice(0, 16)} UTC`;
        card.appendChild(when);
      }"""
assert old in s, "last-scanned anchor"
s = s.replace(old, new, 1)

# 5. add flow -> append card from response
old = """        const data = (await res.json()) as { ok: boolean; error?: string };
        if (data.ok) {
          showMsg('bg-pass/10 text-pass border border-pass/30', `${input.value.trim().toLowerCase()} added and scanned.`);
          input.value = '';
          await loadDomains();
        } else {
          showMsg('bg-fail/10 text-fail border border-fail/30', data.error ?? 'Could not add the domain.');
        }"""
new = """        const data = (await res.json()) as { ok: boolean; error?: string; domain?: DomainRow };
        if (data.ok && data.domain) {
          const row: DomainRow = { ...data.domain, paused: false };
          document.querySelector('#dom-list .empty-state')?.remove();
          document.getElementById('dom-list')!.appendChild(domainCard(row));
          showMsg('bg-pass/10 text-pass border border-pass/30', `${row.domain} added and scanned.`);
          input.value = '';
        } else {
          showMsg('bg-fail/10 text-fail border border-fail/30', data.error ?? 'Could not add the domain.');
        }"""
assert old in s, "form submit anchor"
s = s.replace(old, new, 1)

# 6. empty-state marker class in loadDomains
old = """        const empty = document.createElement('p');
        empty.className = 'rounded-xl border border-dashed border-line bg-panel/40 p-6 text-center text-sm text-ink-faint';
        empty.textContent = 'No domains yet. Add one above and the first scan runs immediately.';
        list.appendChild(empty);"""
new = """        const empty = document.createElement('p');
        empty.className = 'empty-state rounded-xl border border-dashed border-line bg-panel/40 p-6 text-center text-sm text-ink-faint';
        empty.textContent = 'No domains yet. Add one above and the first scan runs immediately.';
        list.appendChild(empty);"""
assert old in s, "empty state anchor"
s = s.replace(old, new, 1)

# 7. ensureEmptyState helper after loadDomains
old = """    async function loadAlerts() {"""
new = """    function ensureEmptyState() {
      const list = document.getElementById('dom-list')!;
      if (list.querySelector('[data-domain]')) return;
      list.textContent = '';
      const empty = document.createElement('p');
      empty.className = 'empty-state rounded-xl border border-dashed border-line bg-panel/40 p-6 text-center text-sm text-ink-faint';
      empty.textContent = 'No domains yet. Add one above and the first scan runs immediately.';
      list.appendChild(empty);
    }

    async function loadAlerts() {"""
assert old in s, "loadAlerts anchor"
s = s.replace(old, new, 1)

p.write_text(s, encoding="utf-8")
print("app.astro smoothed")
