"""One-off patch: /app DMARC sources panel.
- "DMARC sources" button per domain card actions row
- Expandable panel: setup guidance when empty; summary, sources table with
  client-side PTR resolution, and the recent-reports list when data exists.
"""
import pathlib

p = pathlib.Path("src/pages/app.astro")
s = p.read_text(encoding="utf-8")

# 1. imports for PTR resolution
old = """  import type { PdnsResult, PdnsFinding, Severity } from '../data/findings';"""
if old not in s:
    old = None
# app.astro script has no doh import yet; find the script opening to extend imports
anchor_import = "    type ScanCheck = { id: string; label: string; status: string; value: string; earned: number; weight: number };"
assert anchor_import in s, "script type anchor"
s = s.replace(
    anchor_import,
    """    import { lookup, RESOLVERS } from '../lib/doh';

    type ScanCheck = { id: string; label: string; status: string; value: string; earned: number; weight: number };""",
    1,
)

# 2. dmarc panel div after the report panel
old = """      const report = document.createElement('div');
      report.className = 'domain-report mt-3 hidden rounded-lg border border-line bg-panel/40 p-4';
      card.appendChild(report);"""
new = """      const report = document.createElement('div');
      report.className = 'domain-report mt-3 hidden rounded-lg border border-line bg-panel/40 p-4';
      card.appendChild(report);

      const dmarcPanel = document.createElement('div');
      dmarcPanel.className = 'dmarc-panel mt-3 hidden rounded-lg border border-line bg-panel/40 p-4';
      card.appendChild(dmarcPanel);"""
assert old in s, "report panel anchor"
s = s.replace(old, new, 1)

# 3. button in the actions row
old = """      const reportBtn = document.createElement('button');
      reportBtn.className = 'text-xs font-medium text-accent hover:text-accent-soft';
      reportBtn.textContent = 'Monitoring report';
      reportBtn.addEventListener('click', () => toggleReport(reportBtn, report, d));
      actions.appendChild(reportBtn);"""
new = """      const reportBtn = document.createElement('button');
      reportBtn.className = 'text-xs font-medium text-accent hover:text-accent-soft';
      reportBtn.textContent = 'Monitoring report';
      reportBtn.addEventListener('click', () => toggleReport(reportBtn, report, d));
      actions.appendChild(reportBtn);
      const dmarcBtn = document.createElement('button');
      dmarcBtn.className = 'text-xs font-medium text-accent hover:text-accent-soft';
      dmarcBtn.textContent = 'DMARC sources';
      dmarcBtn.addEventListener('click', () => toggleDmarc(dmarcBtn, dmarcPanel, d));
      actions.appendChild(dmarcBtn);"""
assert old in s, "actions anchor"
s = s.replace(old, new, 1)

# 4. toggleDmarc implementation after toggleReport
old = """    async function toggleReport(btn: HTMLButtonElement, box: HTMLElement, d: DomainRow) {"""
new = """    const ptrName = (ip: string) => ip.includes(':') ? null : `${ip.split('.').reverse().join('.')}.in-addr.arpa`;

    async function toggleDmarc(btn: HTMLButtonElement, box: HTMLElement, d: DomainRow) {
      if (!box.classList.contains('hidden')) {
        box.classList.add('hidden');
        btn.textContent = 'DMARC sources';
        return;
      }
      btn.textContent = 'Hide DMARC';
      box.textContent = '';
      box.classList.remove('hidden');
      const loading = document.createElement('p');
      loading.className = 'text-xs text-ink-faint';
      loading.textContent = 'Loading…';
      box.appendChild(loading);
      try {
        const res = await fetch(`/api/domains/dmarc?id=${d.id}`);
        const data = (await res.json()) as {
          ok: boolean;
          error?: string;
          summary?: { reports: number; messages: number; orgs: number; passRate: number | null };
          sources?: { ip: string; volume: number; dmarcPass: number; spfPass: number; dkimPass: number; disposition: string; lastReport: string | null }[];
          reports?: { org_name: string; report_id: string; date_begin: string | null; date_end: string | null; messages_total: number }[];
        };
        box.textContent = '';
        if (!data.ok) {
          const err = document.createElement('p');
          err.className = 'text-xs text-fail';
          err.textContent = data.error ?? 'Could not load DMARC data.';
          box.appendChild(err);
          return;
        }

        const title = document.createElement('p');
        title.className = 'text-xs font-semibold text-ink';
        title.textContent = 'Who is sending email as your domain (from aggregate reports)';
        box.appendChild(title);

        if (!data.summary || data.summary.reports === 0) {
          const empty = document.createElement('div');
          empty.className = 'mt-2 text-xs leading-relaxed text-ink-dim';
          empty.innerHTML =
            'No reports received yet. Setup:' +
            '<ol class="mt-1 list-decimal space-y-1 pl-5">' +
            '<li>Publish your DMARC record with <code class="font-mono">rua=mailto:reports@promptdns.com</code> - the <a href="/dmarc-record-generator/" class="text-accent">record generator</a> builds it.</li>' +
            '<li>First aggregate reports from Gmail, Microsoft, and Yahoo typically arrive within 24-48 hours of the record going live.</li>' +
            '<li>Reports show up here automatically; nothing else to configure.</li>' +
            '</ol>';
          box.appendChild(empty);
          return;
        }

        const sum = data.summary;
        const cards = document.createElement('div');
        cards.className = 'mt-2 grid grid-cols-2 gap-2 sm:grid-cols-4';
        for (const [label, value] of [
          ['Reports received', String(sum.reports)],
          ['Messages analyzed', sum.messages.toLocaleString()],
          ['DMARC pass rate', sum.passRate === null ? 'n/a' : `${sum.passRate}%`],
          ['Reporting providers', String(sum.orgs)],
        ] as [string, string][]) {
          const cell = document.createElement('div');
          cell.className = 'rounded-lg border border-line bg-panel/60 p-2.5 text-center';
          cell.innerHTML = `<div class="font-display text-lg font-bold text-accent">${value}</div><div class="text-[10px] text-ink-faint">${label}</div>`;
          cards.appendChild(cell);
        }
        box.appendChild(cards);

        const srcTitle = document.createElement('p');
        srcTitle.className = 'mt-3 text-xs font-semibold text-ink';
        srcTitle.textContent = 'Sources (aggregated across reports)';
        box.appendChild(srcTitle);

        const table = document.createElement('table');
        table.className = 'mt-2 w-full text-left text-xs';
        table.innerHTML = '<thead><tr class="text-ink-faint"><th class="py-1 font-medium">Source IP</th><th class="font-medium">Host (PTR)</th><th class="font-medium">Volume</th><th class="font-medium">SPF</th><th class="font-medium">DKIM</th><th class="font-medium">DMARC</th></tr></thead>';
        const tbody = document.createElement('tbody');
        box.appendChild(table);
        table.appendChild(tbody);
        const sources = data.sources ?? [];
        for (const src of sources) {
          const tr = document.createElement('tr');
          tr.className = 'border-t border-line/60';
          const pass = (n: number) => (n > 0 ? '<span class="text-pass">pass</span>' : '<span class="text-fail">fail</span>');
          const known = src.dmarcPass > 0;
          tr.innerHTML =
            `<td class="py-1 font-mono text-[11px] text-ink">${src.ip}</td>` +
            '<td class="font-mono text-[11px] text-ink-faint" data-ptr="pending">…</td>' +
            `<td class="font-mono text-[11px] text-ink-dim">${src.volume.toLocaleString()}</td>` +
            `<td>${pass(src.spfPass)}</td><td>${pass(src.dkimPass)}</td>` +
            `<td>${known ? pass(src.dmarcPass) : '<span class="text-warn">unknown</span>'}</td>`;
          tbody.appendChild(tr);
        }
        // PTR resolution (first 20, sequential-light via Promise.allSettled)
        const ptrCells = Array.from(tbody.querySelectorAll<HTMLTableCellElement>('td[data-ptr="pending"]'));
        await Promise.allSettled(sources.slice(0, 20).map(async (src, i) => {
          const arpa = ptrName(src.ip);
          const cell = ptrCells[i];
          if (!arpa || !cell) return;
          try {
            const r = await lookup(arpa, 'PTR', RESOLVERS[0]);
            const host = r.answers.find((a) => a.type === 12)?.data.replace(/^"|"$/g, '').replace(/\\.$/, '');
            if (host) cell.textContent = host;
            else cell.textContent = '-';
          } catch {
            cell.textContent = '-';
          }
        }));

        const repTitle = document.createElement('p');
        repTitle.className = 'mt-3 text-xs font-semibold text-ink';
        repTitle.textContent = 'Recent reports';
        box.appendChild(repTitle);
        const repList = document.createElement('ul');
        repList.className = 'mt-1 space-y-0.5';
        for (const r of data.reports ?? []) {
          const li = document.createElement('li');
          li.className = 'text-xs text-ink-dim';
          li.textContent = `${r.org_name}: ${r.messages_total.toLocaleString()} messages (${r.date_begin ?? '?'} to ${r.date_end ?? '?'})`;
          repList.appendChild(li);
        }
        box.appendChild(repList);
      } catch {
        box.textContent = '';
        const err = document.createElement('p');
        err.className = 'text-xs text-fail';
        err.textContent = 'Could not load DMARC data.';
        box.appendChild(err);
      }
    }

    async function toggleReport(btn: HTMLButtonElement, box: HTMLElement, d: DomainRow) {"""
assert old in s, "toggleReport anchor"
s = s.replace(old, new, 1)

p.write_text(s, encoding="utf-8")
print("app.astro dmarc panel added")
