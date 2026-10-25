"""One-off patch: app.astro monitoring UX round 2.
- card-status div moves to the bottom of each domain card
- monitored chip reflects paused state (green/amber)
- Pause/Resume + Monitoring report buttons per card
- report panel: what is monitored, last 30 runs, per-domain alerts
"""
import pathlib

p = pathlib.Path("src/pages/app.astro")
s = p.read_text(encoding="utf-8")

# 1. DomainRow type gains paused
old = "type DomainRow = { id: number; domain: string; score: number | null; grade: string | null; checkedAt: string | null; checks: ScanCheck[] | null };"
new = "type DomainRow = { id: number; domain: string; paused: boolean; score: number | null; grade: string | null; checkedAt: string | null; checks: ScanCheck[] | null };"
assert old in s, "type anchor"
s = s.replace(old, new, 1)

# 2. chip reflects paused state
old = """      const monitorChip = document.createElement('span');
      monitorChip.className = 'rounded-full border border-pass/30 bg-pass/10 px-2 py-0.5 font-mono text-[10px] text-pass';
      monitorChip.title = 'This domain is re-checked automatically every 6 hours';
      monitorChip.textContent = '● monitored';
      left.appendChild(monitorChip);"""
new = """      const monitorChip = document.createElement('span');
      monitorChip.className = d.paused
        ? 'rounded-full border border-warn/30 bg-warn/10 px-2 py-0.5 font-mono text-[10px] text-warn'
        : 'rounded-full border border-pass/30 bg-pass/10 px-2 py-0.5 font-mono text-[10px] text-pass';
      monitorChip.title = d.paused
        ? 'Automatic monitoring is paused for this domain. Resume to re-enter the 6-hour cycle.'
        : 'This domain is re-checked automatically every 6 hours';
      monitorChip.textContent = d.paused ? '● paused' : '● monitored';
      left.appendChild(monitorChip);"""
assert old in s, "chip anchor"
s = s.replace(old, new, 1)

# 3. remove early cardStatus append (moves to bottom)
old = """      head.appendChild(right);
      card.appendChild(head);

      const cardStatus = document.createElement('div');
      cardStatus.className = 'card-status mt-3 hidden rounded-md px-3 py-2 text-xs font-medium';
      card.appendChild(cardStatus);"""
new = """      head.appendChild(right);
      card.appendChild(head);"""
assert old in s, "early status anchor"
s = s.replace(old, new, 1)

# 4. bottom section: status + report + actions
old = """      if (d.checkedAt) {
        const when = document.createElement('p');
        when.className = 'mt-3 font-mono text-[10px] text-ink-faint';
        when.textContent = `Last scanned: ${d.checkedAt.replace('T', ' ').slice(0, 16)} UTC`;
        card.appendChild(when);
      }
      return card;
    }"""
new = """      if (d.checkedAt) {
        const when = document.createElement('p');
        when.className = 'mt-3 font-mono text-[10px] text-ink-faint';
        when.textContent = `Last scanned: ${d.checkedAt.replace('T', ' ').slice(0, 16)} UTC`;
        card.appendChild(when);
      }

      const cardStatus = document.createElement('div');
      cardStatus.className = 'card-status mt-3 hidden rounded-md px-3 py-2 text-xs font-medium';
      card.appendChild(cardStatus);

      const report = document.createElement('div');
      report.className = 'domain-report mt-3 hidden rounded-lg border border-line bg-panel/40 p-4';
      card.appendChild(report);

      const actions = document.createElement('div');
      actions.className = 'mt-3 flex flex-wrap items-center gap-3 border-t border-line pt-3';
      const reportBtn = document.createElement('button');
      reportBtn.className = 'text-xs font-medium text-accent hover:text-accent-soft';
      reportBtn.textContent = 'Monitoring report';
      reportBtn.addEventListener('click', () => toggleReport(reportBtn, report, d));
      actions.appendChild(reportBtn);
      const pauseBtn = document.createElement('button');
      pauseBtn.className = 'text-xs text-ink-faint hover:text-warn';
      pauseBtn.textContent = d.paused ? 'Resume monitoring' : 'Pause monitoring';
      pauseBtn.addEventListener('click', async () => {
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
      });
      actions.appendChild(pauseBtn);
      card.appendChild(actions);
      return card;
    }

    async function toggleReport(btn: HTMLButtonElement, box: HTMLElement, d: DomainRow) {
      if (!box.classList.contains('hidden')) {
        box.classList.add('hidden');
        btn.textContent = 'Monitoring report';
        return;
      }
      btn.textContent = 'Hide report';
      box.textContent = '';
      box.classList.remove('hidden');
      const loading = document.createElement('p');
      loading.className = 'text-xs text-ink-faint';
      loading.textContent = 'Loading…';
      box.appendChild(loading);
      try {
        const res = await fetch(`/api/domains/history?id=${d.id}`);
        const data = (await res.json()) as {
          runs: { outcome: string; score: number | null; changes: number; ran_at: string }[];
          alerts: { severity: string; title: string; detail: string; created_at: string; read_at: string | null }[];
        };
        box.textContent = '';

        const what = document.createElement('p');
        what.className = 'text-xs leading-relaxed text-ink-dim';
        what.innerHTML = '<strong class="text-ink">What is monitored:</strong> website DNS (A/AAAA), nameservers, mail routing (MX), SPF (validity + lookup count), DMARC (policy), DKIM (common selectors), DNSSEC (DS record). Checks and weights follow the <a href="/methodology/" class="text-accent">methodology</a>. Cadence: every 6 hours.';
        box.appendChild(what);

        const logTitle = document.createElement('p');
        logTitle.className = 'mt-3 text-xs font-semibold text-ink';
        logTitle.textContent = 'Scan activity (last 30 runs)';
        box.appendChild(logTitle);

        if (!data.runs.length) {
          const none = document.createElement('p');
          none.className = 'mt-1 text-xs text-ink-faint';
          none.textContent = 'No runs logged yet. Automatic runs appear here every 6 hours; "Scan now" also logs a run.';
          box.appendChild(none);
        } else {
          const table = document.createElement('table');
          table.className = 'mt-2 w-full text-left text-xs';
          table.innerHTML = '<thead><tr class="text-ink-faint"><th class="py-1 font-medium">Time (UTC)</th><th class="font-medium">Result</th><th class="font-medium">Score</th></tr></thead>';
          const tbody = document.createElement('tbody');
          for (const r of data.runs) {
            const tr = document.createElement('tr');
            tr.className = 'border-t border-line/60';
            const outcome = r.outcome === 'changed'
              ? `<span class="text-warn">changed (${r.changes})</span>`
              : r.outcome === 'unresolvable'
                ? '<span class="text-fail">unresolvable</span>'
                : '<span class="text-pass">no changes</span>';
            tr.innerHTML = `<td class="py-1 font-mono text-[11px] text-ink-dim">${r.ran_at.replace('T', ' ').slice(0, 16)}</td><td>${outcome}</td><td class="font-mono text-ink-dim">${r.score === null ? 'n/a' : `${r.score}/100`}</td>`;
            tbody.appendChild(tr);
          }
          table.appendChild(tbody);
          box.appendChild(table);
        }

        const alertTitle = document.createElement('p');
        alertTitle.className = 'mt-3 text-xs font-semibold text-ink';
        alertTitle.textContent = `Alerts for this domain (${data.alerts.length})`;
        box.appendChild(alertTitle);
        if (!data.alerts.length) {
          const none = document.createElement('p');
          none.className = 'mt-1 text-xs text-ink-faint';
          none.textContent = 'None - nothing has changed since monitoring started.';
          box.appendChild(none);
        } else {
          for (const a of data.alerts) {
            const p = document.createElement('p');
            p.className = 'mt-1 text-xs text-ink-dim';
            p.textContent = `${a.created_at.replace('T', ' ').slice(0, 16)} - ${a.title}: ${a.detail.split('\\n').join(' / ')}`;
            box.appendChild(p);
          }
        }
      } catch {
        box.textContent = '';
        const err = document.createElement('p');
        err.className = 'text-xs text-fail';
        err.textContent = 'Could not load the report.';
        box.appendChild(err);
      }
    }"""
assert old in s, "bottom anchor"
s = s.replace(old, new, 1)

p.write_text(s, encoding="utf-8")
print("app.astro patched")
