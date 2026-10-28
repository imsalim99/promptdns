"""WAVE A1 final completion: rerun the 9 pages whose third FAQ failed to insert,
add FAQs for spf-permerror / spf-softfail-vs-hardfail / ip-and-networking, then
regenerate EVERY FAQPage schema from visible details for guaranteed 1:1 parity."""
import json
import pathlib
import re

PAGES = pathlib.Path('src/pages')

EXTRA = {
  'how-to-create-dmarc-record': ('Should I start at p=none or p=quarantine?', 'Start at p=none with rua reporting: two weeks of aggregate reports tell you which legitimate senders exist before any enforcement decision.'),
  'mta-sts-record': ('How often is the MTA-STS policy refreshed?', 'Receivers cache the policy for its max_age, re-fetching at expiry. Changes therefore take up to one max_age cycle to reach every sender.'),
  'multiple-dkim-selectors': ('Do multiple selectors increase lookup count?', 'No: DKIM lookups happen at mail time for the selector in the signature, not during SPF evaluation, so selectors do not touch the SPF 10-lookup budget.'),
  'spf-flattening': ('Does flattening remove the need for DKIM?', 'No. Flattening fixes the SPF lookup limit; DKIM still covers forwarding and alignment. Flattening without monitoring risks silent staleness.'),
  'spf-record-too-long': ('Is there a tool to check both limits at once?', 'Yes: our SPF record checker reports the lookup count and total length together, so you see both limits in one run.'),
  'spf-temperror': ('Can I retry a message that hit TempError myself?', 'Yes: resending after a few minutes usually succeeds because the resolver or nameserver recovered. Persistent TempError means a nameserver problem, not a record problem.'),
  'spf-vs-dmarc': ('Why does my mail pass SPF and still fail DMARC?', 'Because SPF validated the envelope domain, which did not align with the visible From header. DMARC tests alignment; SPF alone cannot provide it.'),
  'tls-rpt-record': ('Can TLS-RPT and DMARC reporting share an address?', 'Yes: both accept mailto URIs and the report formats identify themselves. A dedicated address keeps volume separation cleaner.'),
  'tls-rpt': ('Which providers send TLS reports?', 'Gmail and Microsoft are the major senders today. The reports arrive daily as JSON summaries of successful and failed TLS connections to your MX hosts.'),
  'spf-permerror': [
    ('Does permerror mean my domain is blocked?', 'No. Permerror means receivers could not evaluate your SPF record at all, usually from syntax errors or too many lookups. Fix the record and evaluation resumes.'),
    ('Can I just delete my SPF record to fix permerror?', 'Deleting stops the permerror but leaves your domain unauthenticated. Fix or rebuild the record instead: one v=spf1 record, under 10 lookups.'),
    ('Why did permerror start suddenly?', 'A new include pushed the lookup count over 10, or an edit introduced a syntax error. Our SPF checker reports both conditions in one run.'),
  ],
  'spf-softfail-vs-hardfail': [
    ('Can I use both ~all and -all in one record?', 'No: one all mechanism per record, and it must be last. The qualifier you choose there is the policy receivers apply.'),
    ('Does softfail hurt deliverability?', 'Slightly less than hardfail protection, but receivers mostly treat softfail as a weak signal. It is the safe intermediate step before hardfail.'),
    ('When should I move from ~all to -all?', 'When your aggregate reports show every legitimate source passing. That is the data-driven moment to harden.'),
  ],
  'ip-and-networking': [
    ('What is the difference between an IP and a port?', 'The IP addresses the machine; the port addresses the service on it. DNS finds the address, the port routes to the application.'),
    ('Why do some IPs have no PTR record?', 'PTR is optional and set by the network owner, not the IP user. Missing PTR is common on residential ranges and hurts mail delivery.'),
    ('How do I check who owns an IP?', 'ASN and netblock lookups show the operator. Our IP lookup shows ownership, geolocation, and the PTR in one view.'),
  ],
}

def insert_details(s: str, faqs):
    items = ''
    for q, a in faqs:
        items += (
            '<details class="group rounded-xl border border-line bg-panel/60 px-5 py-4 open:border-accent/40">'
            f'<summary class="flex cursor-pointer list-none items-center justify-between gap-4 font-semibold text-ink [&::-webkit-details-marker]:hidden">{q}'
            '<span class="text-accent transition-transform duration-200 group-open:rotate-45">+</span></summary>'
            f'<p class="mt-3 text-sm leading-relaxed text-ink-dim">{a}</p></details>'
        )
    last = s.rfind('</details>')
    if last > 0:
        return s[:last + len('</details>')] + items + s[last + len('</details>'):], 'appended'
    anchor = s.find('<h2>Related</h2>')
    section = (
        '<h2 class="font-display mt-10 text-xl font-semibold text-ink">Frequently asked questions</h2>\n'
        '      <div class="mt-3 grid gap-3">' + items + '</div>\n      '
    )
    if anchor > 0:
        return s[:anchor] + section + s[anchor:], 'before Related'
    bl = s.rfind('</BaseLayout>')
    dv = s.rfind('</div>', 0, bl)
    return s[:dv] + section + s[dv:], 'before final div'

# 1. the 9 single-pair reruns
for slug, pair in EXTRA.items():
    if slug not in ('how-to-create-dmarc-record', 'mta-sts-record', 'multiple-dkim-selectors',
                    'spf-flattening', 'spf-record-too-long', 'spf-temperror', 'spf-vs-dmarc',
                    'tls-rpt-record', 'tls-rpt'):
        continue
    p = PAGES / f'{slug}.astro'
    s = p.read_text(encoding='utf-8')
    if s.count('<details') >= 3:
        print('skip:', slug)
        continue
    s, how = insert_details(s, [pair])
    p.write_text(s, encoding='utf-8')
    print(f'{slug}: +1 ({how})')

# 2. the three manual pages
for slug, faqs in [(k, v) for k, v in EXTRA.items() if isinstance(v, list)]:
    p = PAGES / f'{slug}.astro'
    s = p.read_text(encoding='utf-8')
    if s.count('<details') >= 3:
        print('skip:', slug)
        continue
    s, how = insert_details(s, faqs)
    p.write_text(s, encoding='utf-8')
    print(f'{slug}: +{len(faqs)} ({how})')

# 3. universal schema parity: regenerate every FAQPage mainEntity from visible details
fixed = 0
for p in sorted(PAGES.rglob('*.astro')):
    s = p.read_text(encoding='utf-8')
    if 'FAQPage' not in s or '<details' not in s:
        continue
    pairs = []
    for m in re.finditer(r'<summary[^>]*>(.*?)<span[^>]*>.*?</span></summary>(.*?)</details>', s, re.S):
        q = re.sub(r'<[^>]+>', '', m.group(1)).strip()
        a = re.sub(r'<[^>]+>', ' ', m.group(2))
        a = re.sub(r'\s+', ' ', a).strip()
        if q and a:
            pairs.append((q, a))
    if not pairs:
        continue
    qjson = ',\n    '.join(
        "{'@type': 'Question', 'name': " + json.dumps(q) + ', "acceptedAnswer": { '
        + "'@type': 'Answer'" + ', "text": ' + json.dumps(a) + ' } }'
        for q, a in pairs
    )
    fstart = s.find('const faqSchema')
    if fstart < 0:
        fstart = s.find('"mainEntity"')
        if fstart < 0:
            continue
        fstart = s.rfind('const', 0, fstart)
        if fstart < 0:
            continue
    key = s.find('mainEntity', fstart)
    open_b = s.find('[', key)
    close_b = s.find(']', open_b)
    if key < 0 or open_b < 0 or close_b < 0:
        continue
    before = s
    s = s[:open_b + 1] + '\n    ' + qjson + '\n  ' + s[close_b:]
    if s != before:
        p.write_text(s, encoding='utf-8')
        fixed += 1
print('schemas regenerated:', fixed)
