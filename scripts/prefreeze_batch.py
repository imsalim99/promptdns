"""FINAL PRE-FREEZE BATCH (auditor-converged, 5 items).

1. Homepage centerpiece: entity H1, compact hero, badges + chips on the scanner,
   labeled sample report at first paint, category order per spec 3.2.
2. Missed example states: dkim-record-checker tbody, robots-txt-checker rt-raw.
3. ToolPanel-era result regions: aria-live + reserved min-height class.
4. BaseLayout: auto-Article schema for non-tool content pages (Organization author)
   + full OG/Twitter meta with a default OG image.
5. Category order: DNS -> AI & Web Infrastructure -> Email Authentication -> Domain & IP.
"""
import pathlib
import re

BS = chr(92)

# ---------------------------------------------------------------- 1. DomainScanner
p = pathlib.Path('src/components/DomainScanner.astro')
s = p.read_text(encoding='utf-8')

# badge bar + preset chips above the form
old = '<div id="domain-scanner" class="relative">\n  <!-- Scan input -->'
new = (
    '<div id="domain-scanner" class="relative">\n'
    '  <!-- Attribute badges + 1-click presets (visual semantics, homepage centerpiece) -->\n'
    '  <div class="mb-3 flex flex-wrap items-center justify-between gap-2" aria-label="Tool attributes" data-vs="attributes">\n'
    '    <div class="flex flex-wrap items-center gap-2">\n'
    '      <span class="inline-flex items-center gap-1.5 rounded-full border border-pass/30 bg-pass/10 px-2.5 py-1 font-mono text-[11px] font-semibold text-pass">\n'
    '        <span class="h-1.5 w-1.5 rounded-full bg-pass animate-pulse"></span>\n'
    '        100% Free · No Sign Up\n'
    '      </span>\n'
    '      <span class="inline-flex items-center gap-1.5 rounded-full border border-accent/30 bg-accent/10 px-2.5 py-1 font-mono text-[11px] font-medium text-accent">⚡ 7-Check Security Audit</span>\n'
    '      <span class="inline-flex items-center gap-1.5 rounded-full border border-line bg-panel-2 px-2.5 py-1 font-mono text-[11px] text-ink-dim">🛡️ Client-Side · Zero Logs</span>\n'
    '    </div>\n'
    '    <div class="flex items-center gap-2 text-ink-faint">\n'
    '      <span class="inline-block h-2 w-2 rounded-full bg-accent/60"></span>\n'
    '      <span class="font-mono text-[11px]">DNS-over-HTTPS + HTTP fetches</span>\n'
    '    </div>\n'
    '  </div>\n'
    '  <div class="mb-3 flex flex-wrap items-center gap-2" aria-label="Instant test domains">\n'
    '    <span class="font-mono text-[10px] uppercase tracking-[0.14em] text-ink-faint">Try instantly:</span>\n'
    '    <button type="button" data-preset-domain="cloudflare.com" class="rounded-full border border-line bg-panel-2 px-3 py-1 font-mono text-[11px] text-ink-dim transition-colors hover:border-accent/40 hover:text-accent">cloudflare.com</button>\n'
    '    <button type="button" data-preset-domain="github.com" class="rounded-full border border-line bg-panel-2 px-3 py-1 font-mono text-[11px] text-ink-dim transition-colors hover:border-accent/40 hover:text-accent">github.com</button>\n'
    '    <button type="button" data-preset-domain="openai.com" class="rounded-full border border-line bg-panel-2 px-3 py-1 font-mono text-[11px] text-ink-dim transition-colors hover:border-accent/40 hover:text-accent">openai.com</button>\n'
    '  </div>\n'
    '  <!-- Scan input -->'
)
assert old in s, 'scanner container'
s = s.replace(old, new, 1)

# preset chips: fill + submit the scan form
old = """  import { scanDomain } from '../lib/scan';

  const form = document.getElementById('scan-form') as HTMLFormElement;"""
new = """  import { scanDomain } from '../lib/scan';

  document.addEventListener('click', (e) => {
    const pill = (e.target as HTMLElement).closest('[data-preset-domain]') as HTMLElement | null;
    if (!pill) return;
    const input = document.getElementById('scan-domain') as HTMLInputElement;
    const form = document.getElementById('scan-form') as HTMLFormElement;
    input.value = pill.getAttribute('data-preset-domain') ?? '';
    form.requestSubmit();
  });

  const form = document.getElementById('scan-form') as HTMLFormElement;"""
assert old in s, 'scanner js import'
s = s.replace(old, new, 1)

# sample note before results
old = '  <!-- Results -->\n  <div id="scan-results" class="mt-8 hidden">'
new = (
    '  <!-- Results -->\n'
    '  <p id="scan-sample-note" data-vs="example" class="mt-6 text-xs text-ink-faint">\n'
    '    Sample report for <code>example.com</code>: strong email authentication, DNSSEC not yet enabled. Enter any domain above for a live audit.\n'
    '  </p>\n'
    '  <div id="scan-results" class="mt-2" aria-live="polite">'
)
assert old in s, 'results div'
s = s.replace(old, new, 1)

# sample content inside results: gauge, domain, verdict, grade, cards
old = """          <span id="gauge-score" class="font-display text-5xl font-bold tabular-nums">0</span>"""
new = """          <span id="gauge-score" class="font-display text-5xl font-bold tabular-nums">90</span>"""
assert old in s
s = s.replace(old, new, 1)

old = 'stroke-dasharray="326.7" stroke-dashoffset="326.7"'
assert old in s
s = s.replace(old, 'stroke-dasharray="326.7" stroke-dashoffset="32.7"', 1)

old = '<p id="scan-domain-out" class="font-display text-2xl font-bold break-all"></p>'
new = '<p id="scan-domain-out" class="font-display text-2xl font-bold break-all">example.com</p>'
assert old in s
s = s.replace(old, new, 1)

old = '<p class="mt-2 text-sm leading-relaxed text-ink-dim" id="scan-verdict"></p>'
new = '<p class="mt-2 text-sm leading-relaxed text-ink-dim" id="scan-verdict">Mail authentication is fully enforced and all records resolve consistently. The one gap: DNSSEC is not enabled, so the zone is not cryptographically signed.</p>'
assert old in s
s = s.replace(old, new, 1)

old = '<span id="scan-grade" class="rounded-md border border-line bg-panel px-3 py-1 font-mono text-xs"></span>'
new = '<span id="scan-grade" class="rounded-md border border-line bg-panel px-3 py-1 font-mono text-xs">Grade A- · 90/100</span>'
assert old in s
s = s.replace(old, new, 1)

CARD = (
    '<div class="rounded-xl border {ring} bg-panel/70 p-4">\n'
    '           <div class="flex items-center justify-between gap-2">\n'
    '             <span class="text-sm font-semibold">{icon} {label}</span>\n'
    '             <span class="font-mono text-xs text-ink-dim">{earned}</span>\n'
    '           </div>\n'
    '           <p class="mt-1 font-mono text-xs text-accent">{value}</p>\n'
    '           <p class="mt-2 text-xs leading-relaxed text-ink-dim">{detail}</p>\n'
    '         </div>'
)


def card(label, earned, value, detail, status='pass'):
    icon = {'pass': '<span class="text-pass">✔</span>', 'warn': '<span class="text-warn">▲</span>'}[status]
    ring = {'pass': 'border-pass/30', 'warn': 'border-warn/30'}[status]
    return CARD.format(ring=ring, icon=icon, label=label, earned=earned, value=value, detail=detail)


cards = (
    card('Website DNS', '15/15', 'A 93.184.216.34', 'Resolves on all resolvers.')
    + card('Nameservers', '5/5', 'a.iana-servers.net + 1', 'Authoritative and consistent.')
    + card('MX', '10/10', '0 example.com', 'Mail path declared.')
    + card('SPF', '20/20', 'v=spf1 -all', 'Valid, 0 of 10 lookups used.')
    + card('DMARC', '25/25', 'p=reject, rua set', 'Full enforcement with reporting.')
    + card('DKIM', '15/15', '2048-bit RSA key', 'Selector published and strong.')
    + card('DNSSEC', '0/10', 'No DS record at parent', 'Enable DNSSEC to sign the zone.', 'warn')
)
old = '<div id="scan-cards" class="mt-8 grid gap-3 sm:grid-cols-2 lg:grid-cols-3"></div>'
new = '<div id="scan-cards" class="mt-8 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">' + cards + '</div>'
assert old in s
s = s.replace(old, new, 1)

# JS: hide sample note when a run starts (progress bar reveal is the first state change)
old = "progressEl.classList.remove('hidden');"
idx = s.find(old)
assert idx > 0, 'progress reveal anchor'
s = s[:idx] + "document.getElementById('scan-sample-note')?.classList.add('hidden');\n    " + s[idx:]
p.write_text(s, encoding='utf-8')
print('1. DomainScanner: badges, chips, sample report state')

# ---------------------------------------------------------------- homepage hero
p = pathlib.Path('src/pages/index.astro')
s = p.read_text(encoding='utf-8')
old = '<div class="relative mx-auto max-w-5xl px-4 pb-20 pt-24 text-center lg:pt-32">'
new = '<div class="relative mx-auto max-w-5xl px-4 pb-14 pt-10 text-center lg:pt-14">'
assert old in s
s = s.replace(old, new, 1)

old = """      <h1 class="reveal reveal-2 font-display mx-auto mt-6 max-w-3xl text-4xl font-bold leading-[1.08] tracking-tight sm:text-6xl">
        Your domain's health,<br /><span class="gradient-text">decoded in seconds</span>
      </h1>"""
new = """      <h1 class="reveal reveal-2 font-display mx-auto mt-6 max-w-3xl text-4xl font-bold leading-[1.08] tracking-tight sm:text-6xl">
        Free DNS, Email Authentication &amp;<br /><span class="gradient-text">AI Readiness Checker</span>
      </h1>"""
assert old in s
s = s.replace(old, new, 1)

old = """      <p class="reveal reveal-3 mx-auto mt-6 max-w-2xl text-lg leading-relaxed text-ink-dim">
        Scan your DNS records, email authentication, and DNSSEC in one pass, then dig deeper
        with {TOTAL_TOOLS} free tools and the most complete DNS guide on the internet."""
new = """      <p class="reveal reveal-3 mx-auto mt-6 max-w-2xl text-lg leading-relaxed text-ink-dim">
        Scan a domain in one pass: DNS records, SPF, DKIM, DMARC, DNSSEC, MX, and the
        robots.txt and llms.txt that AI crawlers read. No sign-up, every lookup runs live in your
        browser, then dig deeper with {TOTAL_TOOLS} free tools."""
assert old in s
s = s.replace(old, new, 1)
p.write_text(s, encoding='utf-8')
print('2. Homepage hero: entity H1, compact padding, entity-dense descriptor')

# ---------------------------------------------------------------- category order
p = pathlib.Path('src/data/tools.ts')
s = p.read_text(encoding='utf-8')
ai_start = s.find("  {\n    id: 'ai'")
assert ai_start > 0
array_end = s.find('\n];', ai_start)
ai_block = s[ai_start:array_end].rstrip()
assert ai_block.endswith('},')
s = s[:ai_start] + s[array_end:].lstrip('\n')
email_anchor = "  {\n    id: 'email'"
assert email_anchor in s
s = s.replace(email_anchor, ai_block + '\n' + email_anchor, 1)
p.write_text(s, encoding='utf-8')
print('3. Category order: DNS -> AI & Web Infrastructure -> Email -> Domain & IP')

# ---------------------------------------------------------------- dkim sample state
p = pathlib.Path('src/pages/dkim-record-checker.astro')
s = p.read_text(encoding='utf-8')
old = '<div id="dkim-results" class="mt-6 hidden overflow-x-auto rounded-lg border border-line/60">'
note = (
    '<p id="dkim-sample-note" data-vs="example" class="mt-6 text-xs text-ink-faint">\n'
    '        Sample diagnostic for <code>example.com</code>. Enter any domain above to read its real DKIM record.\n'
    '      </p>\n'
)
assert old in s, 'dkim results div'
s = s.replace(old, note + '<div id="dkim-results" class="mt-2 overflow-x-auto rounded-lg border border-line/60">', 1)
old = '<tbody id="dkim-tbody"></tbody>'
rows = (
    '<tr><td class="font-medium text-ink">v</td><td><code>DKIM1</code></td></tr>'
    '<tr><td class="font-medium text-ink">k</td><td class="text-sm text-ink-dim">rsa (key type)</td></tr>'
    '<tr><td class="font-medium text-ink">p</td><td class="text-sm text-ink-dim"><code>MIGfMA0GCSq...</code>, 2048-bit public key</td></tr>'
)
assert old in s, 'dkim tbody'
s = s.replace(old, '<tbody id="dkim-tbody">' + rows + '</tbody>', 1)
var_m = re.search(r"const (\w+) = document\.getElementById\('dkim-tbody'\)", s)
var = var_m.group(1)
idx = s.find(f"{var}.innerHTML = '';")
assert idx > 0
s = s[:idx] + "document.getElementById('dkim-sample-note')?.classList.add('hidden');\n    " + s[idx:]
p.write_text(s, encoding='utf-8')
print('4. dkim-record-checker sample state')

# ---------------------------------------------------------------- robots rt-raw sample
p = pathlib.Path('src/pages/robots-txt-checker.astro')
s = p.read_text(encoding='utf-8')
old = '      <div id="rt-raw-wrap" class="mt-6 hidden">'
note = (
    '      <p id="rt-sample-note" data-vs="example" class="mt-6 text-xs text-ink-faint">\n'
    '        Sample robots.txt for <code>example.com</code>. Enter any site above to read and validate the real file.\n'
    '      </p>\n'
)
assert old in s, 'rt-raw wrap'
s = s.replace(old, note + '      <div id="rt-raw-wrap" class="mt-2">', 1)
old = '<pre id="rt-raw" class="max-h-96 overflow-auto rounded-lg border border-line bg-panel-2 p-4 font-mono text-xs leading-relaxed text-ink-dim"></pre>'
new = (
    '<pre id="rt-raw" class="max-h-96 overflow-auto rounded-lg border border-line bg-panel-2 p-4 font-mono text-xs leading-relaxed text-ink-dim">User-agent: *\n'
    'Disallow: /private/\n'
    'Disallow: /tmp/\n\n'
    'User-agent: GPTBot\n'
    'Disallow: /\n\n'
    'Sitemap: https://example.com/sitemap.xml</pre>'
)
assert old in s, 'rt-raw pre'
s = s.replace(old, new, 1)
idx = s.find('rawEl.textContent =')
assert idx > 0
s = s[:idx] + "document.getElementById('rt-sample-note')?.classList.add('hidden');\n    " + s[idx:]
p.write_text(s, encoding='utf-8')
print('5. robots-txt-checker rt-raw sample state')
