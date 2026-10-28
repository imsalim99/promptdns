"""Final pass: rebuild the 5 remaining hub-page faqSchema consts (minified shapes)
from inline details + FaqAccordion pairs, using find-based anchors."""
import json
import pathlib
import re

PAGES = pathlib.Path('src/pages')

for slug in ['ai-web-infrastructure', 'dns-providers', 'email-deliverability', 'ip-and-networking', 'ssl-tls']:
    p = PAGES / f'{slug}.astro'
    s = p.read_text(encoding='utf-8')
    pairs = []
    # inline details
    for m in re.finditer(r'<summary[^>]*>(.*?)<span[^>]*>.*?</span></summary>(.*?)</details>', s, re.S):
        q = re.sub(r'<[^>]+>', '', m.group(1)).strip()
        a = re.sub(r'<[^>]+>', ' ', m.group(2))
        a = re.sub(r'\s+', ' ', a).strip()
        if q and a:
            pairs.append((q, a))
    # accordion pairs
    am = re.search(r'<FaqAccordion faqs=\{\[(.*?)\]\}', s, re.S)
    if am:
        for q, a in re.findall(r'\["((?:[^"\\]|\\.)*)",\s*"((?:[^"\\]|\\.)*)"\]', am.group(1)):
            pairs.append((q.replace("\\'", "'"), a.replace("\\'", "'")))
    seen, uniq = set(), []
    for q, a in pairs:
        if q not in seen:
            seen.add(q)
            uniq.append((q, a))
    qjson = ',\n    '.join(
        "{'@type': 'Question', 'name': " + json.dumps(q) + ', "acceptedAnswer": { '
        + "'@type': 'Answer'" + ', "text": ' + json.dumps(a) + ' } }'
        for q, a in uniq
    )
    clean = (
        'const faqSchema = {\n'
        "  '@context': 'https://schema.org',\n"
        "  '@type': 'FAQPage',\n"
        '  mainEntity: [\n    ' + qjson + '\n  ],\n};'
    )
    fs = s.find('const faqSchema')
    if fs < 0:
        print('NO CONST:', slug)
        continue
    end = s.find('};', fs)
    if end < fs:
        print('NO END:', slug)
        continue
    s = s[:fs] + clean + s[end + len('\n};'):]
    p.write_text(s, encoding='utf-8')
    print(f'{slug}: rebuilt with {len(uniq)} questions')
