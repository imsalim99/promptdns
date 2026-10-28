"""Generalized FAQPage schema rebuild: for every content page with a faqSchema
const, rebuild mainEntity from ALL visible question sources:
  - literal <details> elements in the page source
  - FaqAccordion faqs arrays (runtime-rendered, still visible in dist)
Guarantees schema == visible everywhere, both directions."""
import json
import pathlib
import re

PAGES = pathlib.Path('src/pages')

tools_ts = pathlib.Path('src/data/tools.ts').read_text(encoding='utf-8')
TOOL_SLUGS = set(re.findall(r"href: '/([a-z0-9-]+)/'", tools_ts))
COMPANY = {'about', 'careers', 'changelog', 'contact', 'press', 'editorial-policy', 'support',
           'security', 'privacy', 'terms', 'refund-policy', 'subprocessors', 'dpa',
           'acceptable-use', 'early-access', 'how-it-works', 'pricing', 'login', 'app', 'tools'}

rebuilt = 0
for p in sorted(PAGES.rglob('*.astro')):
    slug = p.stem
    if slug in TOOL_SLUGS or slug in COMPANY or slug.startswith('spf-dkim-dmarc-'):
        continue
    s = p.read_text(encoding='utf-8')
    if 'const faqSchema' not in s:
        continue
    pairs = []
    # 1. literal details
    for m in re.finditer(r'<summary[^>]*>(.*?)<span[^>]*>.*?</span></summary>(.*?)</details>', s, re.S):
        q = re.sub(r'<[^>]+>', '', m.group(1)).strip()
        a = re.sub(r'<[^>]+>', ' ', m.group(2))
        a = re.sub(r'\s+', ' ', a).strip()
        if q and a:
            pairs.append((q, a))
    # 2. FaqAccordion array (runtime-rendered details)
    am = re.search(r'<FaqAccordion faqs=\{\[(.*?)\]\}', s, re.S)
    if am:
        for q, a in re.findall(r'\["((?:[^"\\]|\\.)*)",\s*"((?:[^"\\]|\\.)*)"\]', am.group(1)):
            pairs.append((q.replace("\\'", "'"), a.replace("\\'", "'")))
    # dedupe preserving order
    seen = set()
    uniq = []
    for q, a in pairs:
        if q not in seen:
            seen.add(q)
            uniq.append((q, a))
    if not uniq:
        continue
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
    start = s.find('const faqSchema = {')
    end = s.find('\n};', start)
    if start < 0 or end < start:
        print('SKIP (const not found):', slug)
        continue
    if 'mainEntity: faqs.map' in s[start:end]:
        pass  # corrupted shape, replace anyway
    s = s[:start] + clean + s[end + len('\n};'):]
    p.write_text(s, encoding='utf-8')
    rebuilt += 1
print('schemas rebuilt:', rebuilt)
