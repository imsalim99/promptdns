"""Extract the true visible FAQ pairs from the BUILT dist HTML (FaqAccordion
renders at runtime, so dist is the rendered truth) and rebuild the source
faqSchema mainEntity from them."""
import json
import pathlib
import re

for slug in ['dns-providers', 'email-deliverability']:
    dist = pathlib.Path(f'dist/{slug}/index.html').read_text(encoding='utf-8')
    pairs = []
    for m in re.finditer(r'<summary[^>]*>(.*?)<span[^>]*>.*?</span></summary>(.*?)</details>', dist, re.S):
        q = re.sub(r'<[^>]+>', '', m.group(1)).strip()
        a = re.sub(r'<[^>]+>', ' ', m.group(2))
        a = re.sub(r'\s+', ' ', a).strip()
        if q and a:
            pairs.append((q, a))
    print(f'{slug}: {len(pairs)} visible pairs from dist')

    p = pathlib.Path(f'src/pages/{slug}.astro')
    s = p.read_text(encoding='utf-8')
    qjson = ',\n    '.join(
        "{'@type': 'Question', 'name': " + json.dumps(q) + ', "acceptedAnswer": { '
        + "'@type': 'Answer'" + ', "text": ' + json.dumps(a) + ' } }'
        for q, a in pairs
    )
    fs = s.find('const faqSchema')
    fm = s.find('---', fs)
    key = s.find('mainEntity', fs)
    open_b = s.find('[', key)
    depth = 0
    close_b = open_b
    for i in range(open_b, fm):
        if s[i] == '[':
            depth += 1
        elif s[i] == ']':
            depth -= 1
            if depth == 0:
                close_b = i
                break
    s = s[:open_b + 1] + '\n    ' + qjson + '\n  ' + s[close_b:]
    p.write_text(s, encoding='utf-8')
    print(f'{slug}: schema rebuilt with {len(pairs)}')
