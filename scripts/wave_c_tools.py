"""Wave C: spec tables for the 13 remaining secondary tool pages.
Each table documents what the tool actually checks, inserted after </ToolPanel>."""
import pathlib

PAGES = pathlib.Path('src/pages')

TABLES = {
  'agents-txt-checker': ('What the agents.txt checker validates',
    ['Check', 'Threshold', 'Source'],
    [['Known agent tokens', 'Against the documented AI agent index', 'Operator documentation'],
     ['Syntax', 'token: permission pairs, one per line', 'agents.txt convention'],
     ['Coverage', 'Which AI crawlers your file addresses', 'Token index above']]),
  'ai-crawler-checker': ('What the AI crawler checker tests',
     ['Check', 'Threshold', 'Source'],
     [['robots.txt presence', 'Fetchable at the root', 'RFC 9309'],
      ['Per-crawler rules', 'Allow/Disallow per known token', 'Operator documentation'],
      ['Crawler identity', 'Reverse DNS of fetching IPs where documented', 'Operator documentation']]),
  'ai-readiness-checker': ('The 7 readiness checks and weights',
     ['Check', 'Weight', 'Good state'],
     [['DMARC policy', '25', 'Enforced with reporting'],
      ['SPF record', '20', 'Valid, within 10 lookups'],
      ['Website DNS', '15', 'Resolving consistently'],
      ['DKIM', '15', 'Published and strong'],
      ['MX records', '10', 'Mail path declared'],
      ['DNSSEC', '10', 'Signed with valid chain'],
      ['Nameservers', '5', 'Authoritative and consistent']]),
  'axfr-checker': ('What the AXFR checker tests',
     ['Check', 'Good state', 'Source'],
     [['Zone transfer request', 'REFUSED on every authoritative NS', 'RFC 5936'],
      ['Recursion exposure', 'Recursion not offered to arbitrary clients', 'Operator hardening']]),
  'delegation-checker': ('What the delegation checker tests',
     ['Check', 'Good state', 'Source'],
     [['NS answers', 'Every delegated nameserver responds', 'RFC 1035'],
      ['Consistency', 'All NS return the same answers', 'RFC 2181 trustworthiness rules'],
      ['Glue validity', 'Parent glue matches child NS', 'Parent zone hygiene']]),
  'dkim-record-generator': ('Key options the generator supports',
     ['Option', 'Values', 'Notes'],
     [['Key type', 'RSA 2048 (default)', 'Receiver-safe standard'],
      ['Selector', 'Your choice', 'Verify after publishing'],
      ['Record type', 'TXT', 'CNAME for hosted ESP flows']]),
  'dmarc-record-generator': ('Policy options the generator validates',
     ['Option', 'Values', 'Guidance'],
     [['p', 'none / quarantine / reject', 'Start none, advance on clean reports'],
      ['rua', 'mailto: address', 'Reports are the evidence for advancing'],
      ['pct', '0-100', 'Ramp enforcement gradually'],
      ['sp / adkim / aspf', 'Subdomain and alignment modes', 'Defaults are relaxed']]),
  'dns-speed-test': ('Metrics the speed test measures',
     ['Metric', 'Method', 'Note'],
     [['Cold latency', 'Fresh query per resolver', 'Cache-miss cost'],
      ['Warm latency', 'Repeated query', 'Cached cost'],
      ['Ranking', 'Fastest average wins', 'Results vary by your network']]),
  'glue-record-checker': ('What the glue checker tests',
     ['Check', 'Good state', 'Why'],
     [['Glue presence', 'In-bailiwick NS have A records at the parent', 'Resolution without extra hops'],
      ['Glue accuracy', 'Glue matches the child NS answers', 'Stale glue breaks resolution']]),
  'my-ip': ('What the IP page shows',
     ['Signal', 'Meaning'],
     [['Public IPv4 / IPv6', 'The address your connection presents'],
      ['IP metadata', 'Operator and geolocation via public APIs']]),
  'schema-validator': ('What the schema validator checks',
     ['Check', 'Good state', 'Source'],
     [['JSON syntax', 'Parses cleanly', 'JSON specification'],
      ['schema.org types', 'Recognized @type values', 'schema.org vocabulary'],
      ['Required properties', 'Present per type', 'schema.org vocabulary']]),
  'smtp-tester': ('What the SMTP tester walks',
     ['Check', 'Good state', 'Source'],
     [['MX resolution', 'At least one MX with valid target', 'RFC 5321'],
      ['Port 25 connectivity', 'Reachable, dialogue completes', 'RFC 5321'],
      ['STARTTLS', 'Offered with a valid certificate', 'RFC 3207']]),
  'spf-record-generator': ('Syntax the SPF generator validates',
     ['Check', 'Rule', 'Source'],
     [['Single record', 'One v=spf1 per name', 'RFC 7208'],
      ['Mechanism syntax', 'Valid include/a/mx/ip4/ip6/all usage', 'RFC 7208'],
      ['Lookup budget', 'Warning near the 10-lookup cap', 'RFC 7208 section 4.6.4']]),
}

applied = 0
for slug, (heading, headers, rows) in TABLES.items():
    p = PAGES / f'{slug}.astro'
    s = p.read_text(encoding='utf-8')
    if heading in s:
        print('skip (present):', slug)
        continue
    tp = PAGES / f'{slug}.astro'
    close = tp and s.find('</ToolPanel>')
    if close < 0:
        print('NO ANCHOR:', slug)
        continue
    th = ''.join(f'<th>{h}</th>' for h in headers)
    trs = ''
    for row in rows:
        tds = ''.join(
            f'<td class="font-medium text-ink">{c}</td>' if i == 0 else f'<td class="text-sm text-ink-dim">{c}</td>'
            for i, c in enumerate(row)
        )
        trs += f'<tr>{tds}</tr>'
    section = (
        f'\n\n    <h2 class="font-display mt-10 text-xl font-semibold text-ink">{heading}</h2>\n'
        '    <section class="not-prose my-4" aria-label="Reference table">\n'
        '      <div class="glass rounded-2xl p-5 shadow-lg sm:p-7 overflow-x-auto">\n'
        "        <table class=\"pdns-table\" style=\"width:100%\">\n"
        f'          <thead><tr>{th}</tr></thead>\n'
        f'          <tbody>{trs}</tbody>\n'
        '        </table>\n      </div>\n    </section>'
    )
    end = s.find('</ToolPanel>') + len('</ToolPanel>')
    s = s[:end] + section + s[end:]
    p.write_text(s, encoding='utf-8')
    applied += 1
    print(f'{slug}: table added')
print('applied:', applied)
