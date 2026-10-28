"""Wave A2 pillar completion: additive page-level sections for the 6 pillars
still missing blueprint content. Page-level additions only; no template edits."""
import pathlib

PAGES = pathlib.Path('src/pages')

def table_section(heading, headers, rows):
    th = ''.join(f'<th>{h}</th>' for h in headers)
    trs = ''
    for row in rows:
        tds = ''.join(
            f'<td class="font-medium text-ink">{c}</td>' if i == 0 else f'<td class="text-sm text-ink-dim">{c}</td>'
            for i, c in enumerate(row)
        )
        trs += f'<tr>{tds}</tr>'
    return (
        f'\n    <h2 class="font-display mt-10 text-xl font-semibold text-ink">{heading}</h2>\n'
        '    <section class="not-prose my-4" aria-label="Reference table">\n'
        '      <div class="glass rounded-2xl p-5 shadow-lg sm:p-7 overflow-x-auto">\n'
        "        <table class=\"pdns-table\" style=\"width:100%\">\n"
        f'          <thead><tr>{th}</tr></thead>\n'
        f'          <tbody>{trs}</tbody>\n'
        '        </table>\n      </div>\n    </section>'
    )

def insert_after_template(s: str, html: str) -> str:
    anchor = s.find('</RecordTypeTemplate')
    if anchor < 0:
        return s
    end = s.find('>', anchor) + 1
    return s[:end] + '\n\n    ' + html.strip() + s[end:]

edits = 0

# 1. spf-record: Return-Path vs Header From alignment section
p = PAGES / 'spf-record.astro'
s = p.read_text(encoding='utf-8')
if 'RFC 5321.MailFrom' not in s:
    section = (
        '\n    <h2 class="font-display mt-10 text-xl font-semibold text-ink">Return-Path vs Header From: why SPF needs DMARC</h2>\n'
        '    <p class="mt-3">SPF validates the envelope sender (the RFC 5321.MailFrom, also called Return-Path), which the receiving server checks before the message body exists. '
        'The domain your recipients see is the RFC 5322.From header, and the two do not have to match.</p>\n'
        '    <p class="mt-3">That gap is why SPF alone cannot stop display-name spoofing: a scammer can send with a perfect envelope and a forged visible sender. '
        'DMARC closes it by requiring alignment, and the aspf tag controls how strictly: aspf=r (relaxed) matches organizational domains, aspf=s (strict) demands an exact match.</p>\n'
        '    <p class="mt-3">Check both sides with the <a href="/spf-record-checker/" class="text-accent hover:text-accent-soft">SPF record checker</a>, then enforce with the <a href="/dmarc-record-checker/" class="text-accent hover:text-accent-soft">DMARC checker</a>.</p>'
    )
    # insert before the FAQ heading if present, else before </article>
    anchor = s.find('<h2')
    # find the FAQ section heading specifically
    faq_anchor = s.find('Frequently asked questions')
    if faq_anchor > 0:
        # back up to the <h2 before it
        h2 = s.rfind('<h2', 0, faq_anchor)
        s = s[:h2] + section.strip() + '\n    ' + s[h2:]
    else:
        art = s.rfind('</article>')
        s = s[:art] + section.strip() + '\n    ' + s[art:]
    p.write_text(s, encoding='utf-8')
    edits += 1
    print('spf-record: Return-Path section added')

# 2. dmarc: 3-stage rollout table
p = PAGES / 'dmarc.astro'
s = p.read_text(encoding='utf-8')
if '3-stage enforcement rollout' not in s and 'Stage 1: p=none' not in s:
    section = table_section(
        'The 3-stage enforcement rollout',
        ['Stage', 'Policy', 'What you learn', 'Risk'],
        [['1. Monitor', 'p=none; rua=...', 'Every source sending as your domain, with pass/fail per protocol', 'None: spoofed mail still delivers'],
         ['2. Quarantine', 'p=quarantine; pct=25 to 100', 'How receivers treat failing mail without bouncing it', 'Failing legitimate mail lands in spam'],
         ['3. Reject', 'p=reject', 'Full enforcement: spoofed mail bounces', 'Legitimate mail bounces if a source still fails']])
    faq_anchor = s.find('Frequently asked questions')
    if faq_anchor > 0:
        h2 = s.rfind('<h2', 0, faq_anchor)
        s = s[:h2] + section + '\n    ' + s[h2:]
    else:
        art = s.rfind('</article>')
        s = s[:art] + section + '\n    ' + s[art:]
    p.write_text(s, encoding='utf-8')
    edits += 1
    print('dmarc: rollout table added')

# 3. dns-propagation: windows table + TTL schedule
p = PAGES / 'dns-propagation.astro'
s = p.read_text(encoding='utf-8')
if 'Propagation window by change type' not in s:
    section = table_section(
        'Propagation window by change type',
        ['Change', 'Typical window', 'Why'],
        [['A / AAAA / CNAME / TXT edit', 'Old record TTL (5 min to 4 h)', 'Resolvers serve the cached answer until it expires'],
         ['Brand-new record', 'Near instant', 'Nothing cached a name that did not exist'],
         ['MX change', 'Old record TTL', 'Mail exchangers cache routing aggressively'],
         ['NS delegation change', 'Up to 48 hours', 'Parent zones cache delegation far longer']]) + table_section(
        'Pre-migration TTL lowering schedule',
        ['When', 'Action'],
        [['T-48 hours', 'Lower the record TTL from 3600 to 300 seconds'],
         ['T-0', 'Make the cutover and verify on live resolvers'],
         ['T+2 hours', 'Confirm all resolvers agree'],
         ['T+24 hours', 'Raise the TTL back to 3600']])
    faq_anchor = s.find('Frequently asked questions')
    if faq_anchor > 0:
        h2 = s.rfind('<h2', 0, faq_anchor)
        s = s[:h2] + section + '\n    ' + s[h2:]
    else:
        art = s.rfind('</article>')
        s = s[:art] + section + '\n    ' + s[art:]
    p.write_text(s, encoding='utf-8')
    edits += 1
    print('dns-propagation: 2 tables added')

# 4. cname-record: record specification table after the template
p = PAGES / 'cname-record.astro'
s = p.read_text(encoding='utf-8')
if 'Record specification' not in s:
    section = table_section(
        'CNAME record specification',
        ['Attribute', 'Value', 'RFC'],
        [['Type code', '5', 'RFC 1035'],
         ['Target format', 'A hostname with its own A or AAAA resolution', 'RFC 1035'],
         ['Apex prohibition', 'CNAME cannot coexist with MX, NS, or SOA at the zone apex', 'RFC 1034 section 3.6.2'],
         ['Apex workaround', 'CNAME flattening or ALIAS records at your DNS host', 'Provider-specific'],
         ['Lookup behavior', 'The resolver restarts at the target hostname', 'Extra query per resolution']])
    s = insert_after_template(s, section)
    p.write_text(s, encoding='utf-8')
    edits += 1
    print('cname-record: spec table added')

# 5. txt-record
p = PAGES / 'txt-record.astro'
s = p.read_text(encoding='utf-8')
if 'Record specification' not in s:
    section = table_section(
        'TXT record specification',
        ['Attribute', 'Value', 'RFC'],
        [['Type code', '16', 'RFC 1035'],
         ['String limit', '255 characters per character-string', 'RFC 1035 section 3.3.14'],
         ['Multi-string', 'Longer values split into multiple quoted strings, concatenated by the resolver', 'How 2048-bit DKIM keys fit'],
         ['Common uses', 'SPF, DKIM, DMARC, site verification', 'Email authentication and ownership proof']])
    s = insert_after_template(s, section)
    p.write_text(s, encoding='utf-8')
    edits += 1
    print('txt-record: spec table added')

# 6. a-record
p = PAGES / 'a-record.astro'
s = p.read_text(encoding='utf-8')
if 'Record specification' not in s:
    section = table_section(
        'A record specification',
        ['Attribute', 'Value', 'RFC'],
        [['Type code', '1', 'RFC 1035'],
         ['RDATA format', 'A 32-bit IPv4 address', 'RFC 1035'],
         ['IPv6 sibling', 'AAAA carries the 128-bit IPv6 form', 'RFC 3596'],
         ['Round-robin', 'Multiple A records rotate answers per query', 'Load distribution without a load balancer']])
    s = insert_after_template(s, section)
    p.write_text(s, encoding='utf-8')
    edits += 1
    print('a-record: spec table added')

print('pillar edits:', edits)
