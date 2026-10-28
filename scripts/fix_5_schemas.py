"""Fix the 5 pages whose FAQPage schema has fewer questions than visible FAQs.
Bracket-scan based: replaces the mainEntity array content between [ and the first ]."""
import json
import pathlib
import re

for slug in ['common-network-ports', 'dedicated-vs-shared-ip', 'email-sending-reputation', 'list-unsubscribe-header', 'ssl-tls']:
    p = pathlib.Path(f'src/pages/{slug}.astro')
    s = p.read_text(encoding='utf-8')
    pairs = []
    for m in re.finditer(
        r'<details[^>]*><summary[^>]*>(.*?)<span class="text-accent[^"]*">\+</span></summary>'
        r'<p class="mt-3 text-sm leading-relaxed text-ink-dim">(.*?)</p></details>', s, re.S):
        q = re.sub(r'<[^>]+>', '', m.group(1)).strip()
        a = m.group(2).strip()
        pairs.append((q, a))
    # json.dumps emits properly escaped double-quoted strings valid as JS literals
    qjson = ',\n    '.join(
        "{'@type': 'Question', 'name': " + json.dumps(q) + ', "acceptedAnswer": { '
        + "'@type': 'Answer'" + ', "text": ' + json.dumps(a) + ' } }'
        for q, a in pairs
    )
    fstart = s.find('const faqSchema')
    if fstart < 0:
        print('NO CONST:', slug)
        continue
    key = s.find('mainEntity', fstart)
    open_b = s.find('[', key)
    close_b = s.find(']', open_b)
    if key < 0 or open_b < 0 or close_b < 0:
        print('NO ARRAY:', slug)
        continue
    s = s[:open_b + 1] + '\n    ' + qjson + '\n  ' + s[close_b:]
    p.write_text(s, encoding='utf-8')
    print(f'{slug}: schema regenerated with {len(pairs)} questions')
