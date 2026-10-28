"""Repair the corrupted faqSchema consts (bracket-scan spliced JSON into faqs.map
expressions). Rebuilds each as a literal array from the page's visible details."""
import json
import pathlib
import re

PAGES = pathlib.Path('src/pages')
corrupted = sorted(p for p in PAGES.rglob('*.astro') if 'mainEntity: faqs.map' in p.read_text(encoding='utf-8', errors='ignore'))
print('corrupted pages:', len(corrupted))

repaired = 0
for p in corrupted:
    s = p.read_text(encoding='utf-8')
    # visible FAQ pairs from the literal details grid
    pairs = []
    for m in re.finditer(r'<summary[^>]*>(.*?)<span[^>]*>.*?</span></summary>(.*?)</details>', s, re.S):
        q = re.sub(r'<[^>]+>', '', m.group(1)).strip()
        a = re.sub(r'<[^>]+>', ' ', m.group(2))
        a = re.sub(r'\s+', ' ', a).strip()
        if q and a:
            pairs.append((q, a))
    if not pairs:
        print('NO VISIBLE FAQS:', p.stem)
        continue
    qjson = ',\n    '.join(
        "{'@type': 'Question', 'name': " + json.dumps(q) + ', "acceptedAnswer": { '
        + "'@type': 'Answer'" + ', "text": ' + json.dumps(a) + ' } }'
        for q, a in pairs
    )
    clean = (
        'const faqSchema = {\n'
        "  '@context': 'https://schema.org',\n"
        "  '@type': 'FAQPage',\n"
        '  mainEntity: [\n    ' + qjson + '\n  ],\n};'
    )
    # replace from 'const faqSchema = {' to the first line-start '};' after it
    start = s.find('const faqSchema = {')
    end = s.find('\n};', start)
    assert end > start, p.stem
    s = s[:start] + clean + s[end + len('\n};'):]
    p.write_text(s, encoding='utf-8')
    repaired += 1
    print(f'repaired {p.stem}: {len(pairs)} questions')
print('repaired:', repaired)
