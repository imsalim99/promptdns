"""READ-ONLY body-copy quality audit over src/pages (no changes).

Measures, per the auditor's 3 questions plus word counts:
1. ESP (spf-dkim-dmarc-*) and provider playbook architecture: data file vs inline,
   unique-fact density (DKIM selectors, SPF includes, per-ESP strings), shared-sentence similarity.
2. Non-tool content guides: zero-table count, zero-FAQ count, intro style (entity-first vs narrative).
3. AI filler phrase scan + word-count distribution.
"""
import pathlib
import re
from collections import Counter
from difflib import SequenceMatcher

PAGES = pathlib.Path('src/pages')
TOOL_SLUGS = set()  # filled from tools registry

tools_ts = pathlib.Path('src/data/tools.ts').read_text(encoding='utf-8')
TOOL_SLUGS = set(re.findall(r"href: '/([a-z0-9-]+)/'", tools_ts))

EXCLUDE = {'app', 'login', '404', 'index'}

def strip_html(s: str) -> str:
    s = re.sub(r'<script.*?</script>', ' ', s, flags=re.S)
    s = re.sub(r'<style.*?</style>', ' ', s, flags=re.S)
    s = re.sub(r'<[^>]+>', ' ', s)
    s = re.sub(r'&\w+;', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()

def body_text(s: str) -> str:
    # text within <main>...</main> if present, else body
    m = re.search(r'<body[^>]*>(.*)</body>', s, re.S)
    t = m.group(1) if m else s
    return strip_html(t)

def word_count(t: str) -> int:
    return len(t.split())

def norm_sentences(text: str):
    return [re.sub(r'[^a-z0-9 ]', '', sent.lower()).strip() for sent in re.split(r'(?<=[.!?])\s+', text) if len(sent.split()) >= 6]

# ---------------- 1. ESP + provider architecture ----------------
esp_files = sorted(PAGES.glob('spf-dkim-dmarc-*.astro'))
provider_files = sorted(p for p in PAGES.glob('*.astro') if 'ProviderPlaybookTemplate' in p.read_text(encoding='utf-8', errors='ignore')[:2000])

print(f'ESP pages: {len(esp_files)} | provider playbook pages: {len(provider_files)}')

# do ESP pages use a central data file or inline content?
import_data = sum(1 for p in esp_files if re.search(r"import .* from '\.\./data/", p.read_text(encoding='utf-8', errors='ignore')[:3000]))
inline_data = len(esp_files) - import_data
print(f'ESP: import-from-data-file: {import_data}, inline/self-contained: {inline_data}')

# unique-fact density: DKIM selector names and SPF include strings per ESP page
sel_hits, inc_hits = 0, 0
for p in esp_files:
    t = p.read_text(encoding='utf-8', errors='ignore')
    if re.search(r'(selector|s=|s1|s2|k1|dkim[_ -]?key|2048|1024)', t, re.I):
        sel_hits += 1
    if re.search(r'include:[a-z0-9._-]+', t):
        inc_hits += 1
print(f'ESP pages mentioning a concrete DKIM selector/key detail: {sel_hits}/{len(esp_files)}')
print(f'ESP pages containing a concrete SPF include: string: {inc_hits}/{len(esp_files)}')

# shared-sentence similarity across ESP pages (sample pairwise on intros)
esp_texts = []
for p in esp_files:
    t = body_text(p.read_text(encoding='utf-8', errors='ignore'))
    esp_texts.append((p.stem, norm_sentences(t)[:12]))  # first ~12 sentences (intro+steps region)
sent_count = Counter()
for _, sents in esp_texts:
    for sent in set(sents):
        sent_count[sent] += 1
n = len(esp_texts)
shared = [(s, c) for s, c in sent_count.most_common(12) if c >= max(3, n // 2)]
print(f'\nESP sentences appearing in >=50% of pages: {len(shared)}')
for s, c in shared:
    print(f'  [{c}/{n}] {s[:110]}')
# sample pairwise similarity of the intro regions
import itertools
sims = []
for (a, sa), (b, sb) in itertools.combinations(esp_texts[:14], 2):
    if not sa or not sb:
        continue
    r = SequenceMatcher(None, ' '.join(sa), ' '.join(sb)).ratio()
    sims.append(r)
if sims:
    print(f'ESP intro-region pairwise similarity (sample of {len(sims)} pairs): avg {sum(sims)/len(sims):.2f}, max {max(sims):.2f}')

# provider pages: inline data + shared sentence analysis
prov_texts = []
for p in provider_files:
    t = body_text(p.read_text(encoding='utf-8', errors='ignore'))
    prov_texts.append((p.stem, norm_sentences(t)[:12]))
sent_count_p = Counter()
for _, sents in prov_texts:
    for sent in set(sents):
        sent_count_p[sent] += 1
shared_p = [(s, c) for s, c in sent_count_p.most_common(10) if c >= max(3, len(prov_texts) // 2)]
print(f'\nProvider sentences appearing in >=50% of pages: {len(shared_p)}')
for s, c in shared_p:
    print(f'  [{c}/{len(prov_texts)}] {s[:110]}')

# ---------------- 2. non-tool guides: tables, FAQs, intros, word counts ----------------
content_pages = []
for p in sorted(PAGES.rglob('*.astro')):
    slug = p.stem
    if slug in TOOL_SLUGS or slug in EXCLUDE or slug.startswith('spf-dkim-dmarc-') or slug in ('tools',):
        continue
    if 'ProviderPlaybookTemplate' in p.read_text(encoding='utf-8', errors='ignore')[:2000]:
        continue
    s = p.read_text(encoding='utf-8', errors='ignore')
    if 'BaseLayout' not in s:
        continue
    content_pages.append((p, s))

print(f'\nNon-tool content pages analyzed: {len(content_pages)}')
zero_table, zero_faq, narrative_intro, entity_intro, thin = [], [], [], [], []
for p, s in content_pages:
    slug = p.stem
    text = body_text(s)
    wc = word_count(text)
    tables = len(re.findall(r'<table', s))
    faqs = len(re.findall(r'<details', s))
    # first sentence of the answer block or first <p> after h1
    m = re.search(r'data-vs="answer">\s*<p[^>]*>(.*?)</p>', s, re.S) or re.search(r'</h1>\s*<p[^>]*>(.*?)</p>', s, re.S)
    first_sent = strip_html(m.group(1)).split('. ')[0] if m else ''
    is_entity = bool(re.match(r'^(An?|The)\s+[A-Z]', first_sent)) or (' is ' in first_sent[:100] and not re.match(r'^(Every|When|If|Most|While|Whether|Before|Since)', first_sent))
    if tables == 0: zero_table.append(slug)
    if faqs == 0: zero_faq.append(slug)
    (entity_intro if is_entity else narrative_intro).append(slug)
    if wc < 500: thin.append((slug, wc))

print(f'zero <table> in page: {len(zero_table)} -> {zero_table[:12]}')
print(f'zero FAQs (no <details>): {len(zero_faq)} -> {zero_faq[:12]}')
print(f'entity-first intros: {len(entity_intro)} | narrative/other intros: {len(narrative_intro)}')
print(f'narrative-intro pages (first 12): {narrative_intro[:12]}')
print(f'pages under 500 words: {len(thin)} -> {thin[:12]}')

# ---------------- 3. AI filler scan ----------------
FILLERS = ['crucial', 'delve', 'seamless', 'seamlessly', 'robust', 'landscape', 'when it comes to',
           "in today's", 'comprehensive guide', 'pivotal', 'leverage', 'unlock', 'harness', 'elevate',
           'game-changer', 'cutting-edge', 'in the realm of', 'navigating the']
print('\nAI filler scan (body text):')
total_hits = 0
for f in FILLERS:
    c = 0
    files = []
    for p, s in content_pages:
        t = body_text(s).lower()
        n = t.count(f)
        if n:
            c += n
            files.append(p.stem)
    if c:
        total_hits += c
        print(f'  "{f}": {c} hits in {len(files)} pages -> {files[:6]}')
if not total_hits:
    print('  none found')

# whole-corpus word-count distribution
wcs = sorted(word_count(body_text(s)) for _, s in content_pages)
if wcs:
    import statistics
    print(f'\ncontent page word counts: min {wcs[0]}, median {statistics.median(wcs)}, max {wcs[-1]}')
