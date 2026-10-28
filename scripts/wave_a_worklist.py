"""Wave A step 1: build the work list (read-only).

Classifies every non-tool, non-company content page by what it needs to pass
the completion bar: 3+ FAQs, >=1 table, entity-first opener, >=3 in-body links.
Output: scripts/wave-a-worklist.json
"""
import json
import pathlib
import re

PAGES = pathlib.Path('src/pages')

tools_ts = pathlib.Path('src/data/tools.ts').read_text(encoding='utf-8')
TOOL_SLUGS = set(re.findall(r"href: '/([a-z0-9-]+)/'", tools_ts))

# company/utility pages: no FAQs or spec tables expected
COMPANY = {
    'about', 'careers', 'changelog', 'contact', 'press', 'editorial-policy', 'support',
    'security', 'privacy', 'terms', 'refund-policy', 'subprocessors', 'dpa',
    'acceptable-use', 'early-access', 'how-it-works', 'pricing', 'login', 'app',
    'index', '404', 'tools',
}

def strip_html(s: str) -> str:
    s = re.sub(r'<script.*?</script>', ' ', s, flags=re.S)
    s = re.sub(r'<style.*?</style>', ' ', s, flags=re.S)
    s = re.sub(r'<[^>]+>', ' ', s)
    s = re.sub(r'&\w+;', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()

work = []
company_skipped = 0
for p in sorted(PAGES.rglob('*.astro')):
    slug = p.stem
    s = p.read_text(encoding='utf-8', errors='ignore')
    if 'BaseLayout' not in s:
        continue
    if slug in TOOL_SLUGS:
        continue
    if slug in COMPANY:
        company_skipped += 1
        continue
    if slug.startswith('spf-dkim-dmarc-'):  # ESP playbooks: Wave B scope
        continue
    if 'ProviderPlaybookTemplate' in s[:2500]:  # provider playbooks: Wave B scope
        continue

    text = strip_html(s)
    tables = len(re.findall(r'<table', s))
    faqs = len(re.findall(r'<details', s))
    has_answer = 'data-vs="answer"' in s

    m = re.search(r'data-vs="answer">\s*<p[^>]*>(.*?)</p>', s, re.S) or re.search(r'</h1>\s*<p[^>]*>(.*?)</p>', s, re.S)
    first_sent = strip_html(m.group(1)).split('. ')[0] if m else ''
    is_entity = bool(re.match(r'^(An?|The)\s+[A-Z]', first_sent)) or (
        ' is ' in first_sent[:120] and not re.match(r'^(Every|When|If|Most|While|Whether|Before|Since|This guide|This page)', first_sent)
    )

    # in-body internal links (within <article> or main content region)
    am = re.search(r'<article[^>]*>(.*?)</article>', s, re.S)
    region = am.group(1) if am else s
    links = len(re.findall(r'href="/[a-z0-9-]+/?"', region))

    needs = []
    if faqs < 3: needs.append('faqs')
    if tables == 0: needs.append('table')
    if not has_answer: needs.append('answer')
    if not is_entity: needs.append('opener')
    if links < 3: needs.append('links')
    if not needs:
        continue
    work.append({
        'slug': slug,
        'needs': needs,
        'faqs': faqs,
        'tables': tables,
        'links': links,
        'words': len(text.split()),
        'first_sentence': first_sent[:110],
    })

out = pathlib.Path('scripts/wave-a-worklist.json')
out.write_text(json.dumps(work, indent=1), encoding='utf-8')

from collections import Counter
c = Counter()
for w in work:
    for n in w['needs']:
        c[n] += 1
print('pages needing work:', len(work), '| company pages skipped:', company_skipped)
print('needs breakdown:', dict(c))
print('\nfull list:')
for w in work:
    print(f"  {w['slug']}: {','.join(w['needs'])} (faqs={w['faqs']} tables={w['tables']} links={w['links']} words={w['words']})")
