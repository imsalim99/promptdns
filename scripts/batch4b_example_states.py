"""
 BATCH 4b: example diagnostic states on remaining tools.
 
 Patterns:
  - tbody tools: sample note + sample rows, results div unhidden, JS hides note on run
  - grid tools (JS builds cards into an empty div): static sample cards + note, JS wipes on run
  - agents-txt-checker: sample agents.txt content in the <pre> + note
 
 Skipped on purpose (no empty first paint): spf-flattener and robots-txt-checker
 (static tables already), my-ip and dns-leak-test (live at first paint),
 generators and llms-txt-generator (the form itself is the centerpiece).
 """
import pathlib
import re

BS = chr(92)

FREE_NOTE = (
    '<p id="{prefix}-sample-note" data-vs="example" class="mt-6 text-xs text-ink-faint">\n'
    '        Sample diagnostic for <code>example.com</code>. Enter your own domain above for live results.\n'
    '      </p>\n'
)

TBODY_TOOLS = {
    'dns-response-time-test': ('st', '<tr><td class="font-medium text-ink">Cloudflare</td><td class="font-mono text-xs text-ink-dim">8 ms</td><td class="font-mono text-xs text-ink-dim">14 ms</td><td class="font-mono text-xs text-ink-dim">+6 ms</td></tr><tr><td class="font-medium text-ink">Google</td><td class="font-mono text-xs text-ink-dim">21 ms</td><td class="font-mono text-xs text-ink-dim">33 ms</td><td class="font-mono text-xs text-ink-dim">+12 ms</td></tr><tr><td class="font-medium text-ink">AliDNS</td><td class="font-mono text-xs text-ink-dim">45 ms</td><td class="font-mono text-xs text-ink-dim">52 ms</td><td class="font-mono text-xs text-ink-dim">+7 ms</td></tr>'),
    'nameserver-lookup': ('nsl', '<tr><td class="font-medium text-ink">a.iana-servers.net</td><td><code>199.43.135.53</code></td><td><code>2001:500:8f::53</code></td></tr><tr><td class="font-medium text-ink">b.iana-servers.net</td><td><code>199.43.133.53</code></td><td><code>2001:500:8d::53</code></td></tr>'),
    'reverse-ip-lookup': ('ri', '<tr><td class="font-medium text-ink">PTR query for 8.8.8.8</td><td class="text-sm text-ink-dim"><code>dns.google</code></td></tr><tr><td class="font-medium text-ink">Forward-confirm (FCrDNS)</td><td class="text-sm text-ink-dim"><code>dns.google</code> resolves back to 8.8.8.8, valid</td></tr>'),
    'tls-rpt-checker': ('tr', '<tr><td class="font-medium text-ink">Record</td><td><code>v=TLSRPTv1; rua=mailto:tls-reports@example.com</code></td></tr><tr><td class="font-medium text-ink">Reporting address</td><td class="text-sm text-ink-dim">tls-reports@example.com</td></tr><tr><td class="font-medium text-ink">Report format</td><td class="text-sm text-ink-dim">Daily JSON summaries (RFC 8460)</td></tr>'),
    'wildcard-dns-tester': ('wc', '<tr><td class="font-mono text-xs text-accent-soft">q7x2p9.example.com</td><td class="text-sm text-ink-dim">NXDOMAIN, no wildcard record detected</td></tr><tr><td class="font-mono text-xs text-accent-soft">k4m8w1.example.com</td><td class="text-sm text-ink-dim">NXDOMAIN, no wildcard record detected</td></tr>'),
    'autodiscover-checker': ('ad', '<tr><td class="font-mono text-xs text-accent-soft">autodiscover.example.com</td><td class="text-sm text-ink-dim">CNAME found, pointing to autodiscover.outlook.com</td></tr><tr><td class="font-mono text-xs text-accent-soft">_autodiscover._tcp.example.com (SRV)</td><td class="text-sm text-ink-dim">No SRV record (CNAME method is in use)</td></tr>'),
    'bimi-record-checker': ('bimi', '<tr><td class="font-mono text-xs text-accent-soft">v</td><td class="font-mono text-xs">BIMI1</td><td class="text-sm text-ink-dim">Protocol version</td></tr><tr><td class="font-mono text-xs text-accent-soft">l</td><td class="font-mono text-xs">https://example.com/bimi/logo.svg</td><td class="text-sm text-ink-dim">Logo location, SVG Tiny 1.2 format</td></tr><tr><td class="font-mono text-xs text-accent-soft">a</td><td class="font-mono text-xs">https://example.com/bimi/vmc.pem</td><td class="text-sm text-ink-dim">VMC certificate location (optional)</td></tr>'),
    'ip-reputation-checker': ('ipr', '<tr><td class="font-medium text-ink">Spamhaus SBL</td><td><span class="inline-flex rounded bg-pass/15 px-2 py-0.5 text-xs font-semibold text-pass">Not listed</span></td><td class="text-sm text-ink-dim">No listing found</td></tr><tr><td class="font-medium text-ink">Barracuda</td><td><span class="inline-flex rounded bg-pass/15 px-2 py-0.5 text-xs font-semibold text-pass">Not listed</span></td><td class="text-sm text-ink-dim">No listing found</td></tr><tr><td class="font-medium text-ink">SpamCop</td><td><span class="inline-flex rounded bg-pass/15 px-2 py-0.5 text-xs font-semibold text-pass">Not listed</span></td><td class="text-sm text-ink-dim">No listing found</td></tr>'),
    'mta-sts-checker': ('ms', '<tr><td class="font-medium text-ink">DNS record</td><td class="text-sm text-ink-dim"><code>v=STS1</code> present at _smtp._tls.example.com</td></tr><tr><td class="font-medium text-ink">Policy mode</td><td class="text-sm text-ink-dim">enforce</td></tr><tr><td class="font-medium text-ink">MX matches policy</td><td class="text-sm text-ink-dim">All MX hosts are listed in the policy file</td></tr>'),
    'ip-lookup': ('ipl', '<tr><td class="font-medium text-ink">IP</td><td><code>8.8.8.8</code></td></tr><tr><td class="font-medium text-ink">Organization</td><td class="text-sm text-ink-dim">GOOGLE</td></tr><tr><td class="font-medium text-ink">Country</td><td class="text-sm text-ink-dim">United States</td></tr><tr><td class="font-medium text-ink">PTR</td><td class="text-sm text-ink-dim"><code>dns.google</code></td></tr>'),
    'email-header-analyzer': ('eha', '<tr><td class="font-mono text-xs text-accent-soft">1</td><td class="text-sm text-ink-dim">mail-sor1.example.com</td><td class="text-sm text-ink-dim">mx.google.com</td><td class="font-mono text-xs text-ink-dim">2 s</td></tr><tr><td class="font-mono text-xs text-accent-soft">2</td><td class="text-sm text-ink-dim">192.0.2.10</td><td class="text-sm text-ink-dim">mail.example.com</td><td class="font-mono text-xs text-ink-dim">0 s</td></tr>'),
    'dmarc-report-analyzer': ('draf', '<tr><td class="font-mono text-xs text-accent-soft">209.85.220.41</td><td>12</td><td class="text-sm text-ink-dim">example.com</td><td>pass</td><td>pass</td><td>pass</td><td>none</td></tr><tr><td class="font-mono text-xs text-accent-soft">203.0.113.9</td><td>3</td><td class="text-sm text-ink-dim">example.com</td><td>fail</td><td>fail</td><td>fail</td><td>none</td></tr>'),
    'ai-log-analyzer': ('al', '<tr><td class="font-mono text-xs text-accent-soft">GPTBot</td><td>42</td><td class="text-sm text-ink-dim">/blog/, /docs/</td></tr><tr><td class="font-mono text-xs text-accent-soft">ClaudeBot</td><td>18</td><td class="text-sm text-ink-dim">/, /pricing/</td></tr>'),
    'cidr-calculator': ('cidr', '<tr><td class="font-medium text-ink">Network</td><td><code>192.168.1.0/24</code></td></tr><tr><td class="font-medium text-ink">Usable hosts</td><td class="text-sm text-ink-dim">254</td></tr><tr><td class="font-medium text-ink">First, last usable</td><td class="text-sm text-ink-dim"><code>192.168.1.1</code>, <code>192.168.1.254</code></td></tr>'),
    'punycode-converter': ('pc', '<tr><td class="font-medium text-ink">Unicode</td><td><code>m' + chr(252) + 'nchen.de</code></td></tr><tr><td class="font-medium text-ink">Punycode (IDNA)</td><td><code>xn--mnchen-3ya.de</code></td></tr>'),
    'dns-resolver-tester': ('rt2', '<tr><td class="font-medium text-ink">example.com</td><td class="font-mono text-xs text-ink-dim">3600</td><td><code>93.184.216.34</code></td></tr>'),
    'ipv4-to-ipv6-converter': ('v6', '<tr><td class="font-medium text-ink">IPv4 input</td><td><code>8.8.8.8</code></td></tr><tr><td class="font-medium text-ink">IPv6 mapped form</td><td><code>::ffff:8.8.8.8</code></td></tr><tr><td class="font-medium text-ink">IPv6 dotted form</td><td><code>::ffff:808:808</code></td></tr>'),
}

GRID_TOOLS = {
    'dns-speed-test': ('st', '<div class="rounded-lg border border-line bg-panel/60 p-4"><div class="font-display text-2xl font-bold text-accent">12 ms</div><div class="text-xs text-ink-faint">Cloudflare, ranked fastest</div></div><div class="rounded-lg border border-line bg-panel/60 p-4"><div class="font-display text-2xl font-bold text-ink">24 ms</div><div class="text-xs text-ink-faint">Google</div></div><div class="rounded-lg border border-line bg-panel/60 p-4"><div class="font-display text-2xl font-bold text-ink">48 ms</div><div class="text-xs text-ink-faint">AliDNS</div></div>'),
    'delegation-checker': ('dl', '<div class="rounded-lg border border-line bg-panel/60 p-4"><p class="font-medium text-ink">a.iana-servers.net</p><p class="mt-1 text-sm text-ink-dim">Answering, authoritative for the zone</p></div><div class="rounded-lg border border-line bg-panel/60 p-4"><p class="font-medium text-ink">b.iana-servers.net</p><p class="mt-1 text-sm text-ink-dim">Answering, answers match the first NS</p></div>'),
    'glue-record-checker': ('gr', '<div class="rounded-lg border border-line bg-panel/60 p-4"><p class="font-medium text-ink">ns1.example.com</p><p class="mt-1 text-sm text-ink-dim">Glue A record present at the parent: <code>192.0.2.1</code></p></div><div class="rounded-lg border border-line bg-panel/60 p-4"><p class="font-medium text-ink">ns2.example.com</p><p class="mt-1 text-sm text-ink-dim">No glue at the parent, in-bailiwick name may fail resolution</p></div>'),
    'smtp-tester': ('sm', '<div class="rounded-lg border border-line bg-panel/60 p-4"><p class="font-medium text-ink">MX: mx1.example.com (10)</p><p class="mt-1 text-sm text-ink-dim">Port 25 reachable, STARTTLS offered</p></div><div class="rounded-lg border border-line bg-panel/60 p-4"><p class="font-medium text-ink">TLS certificate</p><p class="mt-1 text-sm text-ink-dim">Valid for mx1.example.com, not expired</p></div>'),
    'axfr-checker': ('ax', '<div class="rounded-lg border border-line bg-panel/60 p-4"><p class="font-medium text-ink">a.iana-servers.net</p><p class="mt-1 text-sm text-ink-dim">AXFR refused, zone transfer properly restricted</p></div><div class="rounded-lg border border-line bg-panel/60 p-4"><p class="font-medium text-ink">b.iana-servers.net</p><p class="mt-1 text-sm text-ink-dim">AXFR refused, zone transfer properly restricted</p></div>'),
    'ai-crawler-checker': ('aic', '<div class="rounded-lg border border-line bg-panel/60 p-4"><p class="font-medium text-ink">GPTBot</p><p class="mt-1 text-sm text-ink-dim">Allowed on all paths</p></div><div class="rounded-lg border border-line bg-panel/60 p-4"><p class="font-medium text-ink">ClaudeBot</p><p class="mt-1 text-sm text-ink-dim">Allowed on all paths</p></div><div class="rounded-lg border border-line bg-panel/60 p-4"><p class="font-medium text-ink">CCBot</p><p class="mt-1 text-sm text-ink-dim">Blocked by Disallow: /</p></div>'),
    'ai-readiness-checker': ('air', '<div class="rounded-lg border border-line bg-panel/60 p-4"><p class="font-medium text-ink">robots.txt</p><p class="mt-1 text-sm text-ink-dim">Found, 12 directives parsed</p></div><div class="rounded-lg border border-line bg-panel/60 p-4"><p class="font-medium text-ink">llms.txt</p><p class="mt-1 text-sm text-ink-dim">Not published yet</p></div><div class="rounded-lg border border-line bg-panel/60 p-4"><p class="font-medium text-ink">AI crawler access</p><p class="mt-1 text-sm text-ink-dim">6 of 8 major bots allowed</p></div>'),
    'schema-validator': ('sv', '<div class="rounded-lg border border-line bg-panel/60 p-4"><p class="font-medium text-ink">Valid JSON-LD</p><p class="mt-1 text-sm text-ink-dim">@type: WebApplication, 0 errors</p></div>'),
}


def unhide_results_div(s: str, div_id: str) -> str:
    m = re.search(r'<div id="' + div_id + r'"([^>]*)>', s)
    assert m, div_id + ': results div not found'
    tag = m.group(0)
    new_tag = tag.replace(' hidden', '', 1)
    return s.replace(tag, new_tag, 1)


def add_tbody_state(s: str, prefix: str, rows: str) -> str:
    div_id = f'{prefix}-results'
    # sample note before the results div
    note = FREE_NOTE.format(prefix=prefix)
    anchor = f'<div id="{div_id}"'
    assert anchor in s, div_id + ': anchor'
    s = s.replace(anchor, note + anchor, 1)
    s = unhide_results_div(s, div_id)
    # rows into tbody
    tb = f'<tbody id="{prefix}-tbody"></tbody>'
    assert tb in s, div_id + ': empty tbody'
    s = s.replace(tb, f'<tbody id="{prefix}-tbody">{rows}</tbody>', 1)
    # JS: hide note at first tbody wipe
    var_m = re.search(r"(?:const|let)\s+(\w+)\s*=\s*document\.getElementById\('" + prefix + r"-tbody'\)", s)
    assert var_m, div_id + ': tbody var not found'
    var = var_m.group(1)
    wipe = f"{var}.innerHTML = '';"
    idx = s.find(wipe)
    assert idx >= 0, div_id + ': wipe not found'
    s = s[:idx] + f"document.getElementById('{prefix}-sample-note')?.classList.add('hidden');\n    " + s[idx:]
    return s


def add_grid_state(s: str, prefix: str, cards: str) -> str:
    div_id = f'{prefix}-results'
    note = FREE_NOTE.format(prefix=prefix)
    div_re = re.compile(r'<div id="' + div_id + r'"([^>]*)>.*?</div>\s*\n', re.S)
    m = div_re.search(s)
    if not m:
        # simpler: empty div form
        empty = f'<div id="{div_id}"'
        assert empty in s, div_id + ': anchor'
    # operate on the empty div: <div id="X-results" class="..."></div>
    tag_re = re.compile(r'<div id="' + div_id + r'"([^>]*)></div>')
    m2 = tag_re.search(s)
    assert m2, div_id + ': empty results div not found'
    attrs = m2.group(1).replace(' hidden', '', 1)
    replacement = (
        note
        + f'<div id="{div_id}"' + attrs + '>'
        + cards
        + '</div>'
    )
    s = s[:m2.start()] + replacement + s[m2.end():]
    # JS: hide note at first resultsEl wipe
    wipe = "resultsEl.innerHTML = '';"
    idx = s.find(wipe)
    assert idx >= 0, div_id + ': wipe not found'
    s = s[:idx] + f"document.getElementById('{prefix}-sample-note')?.classList.add('hidden');\n    " + s[idx:]
    return s


changed, problems = [], []
for slug, (prefix, rows) in TBODY_TOOLS.items():
    p = pathlib.Path(f'src/pages/{slug}.astro')
    s = p.read_text(encoding='utf-8')
    try:
        s = add_tbody_state(s, prefix, rows)
        p.write_text(s, encoding='utf-8')
        changed.append(slug)
    except AssertionError as e:
        problems.append(f'{slug}: {e}')

for slug, (prefix, cards) in GRID_TOOLS.items():
    p = pathlib.Path(f'src/pages/{slug}.astro')
    s = p.read_text(encoding='utf-8')
    try:
        s = add_grid_state(s, prefix, cards)
        p.write_text(s, encoding='utf-8')
        changed.append(slug)
    except AssertionError as e:
        problems.append(f'{slug}: {e}')

# agents-txt-checker: sample content in the <pre>
p = pathlib.Path('src/pages/agents-txt-checker.astro')
s = p.read_text(encoding='utf-8')
old = '<pre id="at-content" class="max-h-72 overflow-auto rounded-lg border border-line bg-panel-2 p-4 font-mono text-xs leading-relaxed text-ink-dim"></pre>'
new = (
    '<p id="at-sample-note" data-vs="example" class="mt-6 text-xs text-ink-faint">\n'
    '        Sample agents.txt. Enter any site above to read its real file.\n'
    '      </p>\n'
    '    <pre id="at-content" class="max-h-72 overflow-auto rounded-lg border border-line bg-panel-2 p-4 font-mono text-xs leading-relaxed text-ink-dim">GPTBot: allow\nClaudeBot: allow\nCCBot: disallow\nPerplexityBot: allow\n\n# Sample content. Enter any site above for live results.</pre>'
)
assert old in s, 'agents pre'
s = s.replace(old, new, 1)
p.write_text(s, encoding='utf-8')
changed.append('agents-txt-checker')

print('changed:', len(changed))
print('problems:', problems if problems else 'none')
