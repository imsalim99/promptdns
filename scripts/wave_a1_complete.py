"""WAVE A1 completion: backfill FAQs on every content page still below 3.
Reuses the FAQ data defined in wave_a1_faqs.py (FAQS3 + FAQS1) with the
robust anchoring from the fixer (Related heading, else final div)."""
import json
import pathlib
import re

PAGES = pathlib.Path('src/pages')

# extract FAQS3 and FAQS1 dicts from the earlier script without executing it
src = pathlib.Path('scripts/wave_a1_faqs.py').read_text(encoding='utf-8')
ns = {}
for name in ('FAQS3', 'FAQS1'):
    m = re.search(name + r'\s*=\s*\{', src)
    start = m.end() - 1
    depth = 0
    i = start
    while i < len(src):
        if src[i] == '{':
            depth += 1
        elif src[i] == '}':
            depth -= 1
            if depth == 0:
                break
        i += 1
    ns[name] = eval(src[start:i + 1])
FAQS3, FAQS1 = ns['FAQS3'], ns['FAQS1']
ALL = {**FAQS3, **FAQS1}

tools_ts = pathlib.Path('src/data/tools.ts').read_text(encoding='utf-8')
TOOL_SLUGS = set(re.findall(r"href: '/([a-z0-9-]+)/'", tools_ts))
COMPANY = {
    'about', 'careers', 'changelog', 'contact', 'press', 'editorial-policy', 'support',
    'security', 'privacy', 'terms', 'refund-policy', 'subprocessors', 'dpa',
    'acceptable-use', 'early-access', 'how-it-works', 'pricing', 'login', 'app', 'tools',
}

def insert_faq_section(s: str, faqs) -> str:
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
        return s[:last + len('</details>')] + items + s[last + len('</details>'):], 'appended to grid'
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

applied = 0
for p in sorted(PAGES.rglob('*.astro')):
    slug = p.stem
    if slug in TOOL_SLUGS or slug in COMPANY or slug.startswith('spf-dkim-dmarc-'):
        continue
    if 'ProviderPlaybookTemplate' in p.read_text(encoding='utf-8', errors='ignore')[:2500]:
        continue
    s = p.read_text(encoding='utf-8')
    if 'BaseLayout' not in s:
        continue
    have = s.count('<details')
    if have >= 3:
        continue
    if slug in ALL:
        faqs = ALL[slug]
        if have == 2:
            faqs = faqs[2:] if len(faqs) > 3 - have else faqs[-(3 - have):]
        elif have == 1:
            faqs = faqs[-(3 - have):]
        elif have == 0:
            faqs = faqs[:3]
    else:
        # page with no data entry: synthesize 3 generic-but-relevant FAQs is not
        # allowed (must be unique); log for manual writing instead
        print('NEEDS MANUAL:', slug, f'(have {have})')
        continue
    s, how = insert_faq_section(s, faqs)
    # schema parity: regenerate mainEntity from ALL visible details
    p.write_text(s, encoding='utf-8')
    applied += 1
    print(f'{slug}: +{len(faqs)} FAQs ({how}), now {have + len(faqs)}')
print('pages updated:', applied)
