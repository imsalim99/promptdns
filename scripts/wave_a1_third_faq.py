"""Final gap: append each page's FAQS1 third question to the visible grid AND
the literal mainEntity schema, completing the 3-FAQ minimum on the deep guides."""
import json
import pathlib
import re

PAGES = pathlib.Path('src/pages')
src = pathlib.Path('scripts/wave_a1_faqs.py').read_text(encoding='utf-8')
m = re.search(r'FAQS1\s*=\s*\{', src)
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
FAQS1 = eval(src[start:i + 1])

applied = 0
for slug, pair in FAQS1.items():
    p = PAGES / f'{slug}.astro'
    s = p.read_text(encoding='utf-8')
    have = s.count('<details')
    if have >= 3:
        continue
    q, a = pair
    detail = (
        '<details class="group rounded-xl border border-line bg-panel/60 px-5 py-4 open:border-accent/40">'
        f'<summary class="flex cursor-pointer list-none items-center justify-between gap-4 font-semibold text-ink [&::-webkit-details-marker]:hidden">{q}'
        '<span class="text-accent transition-transform duration-200 group-open:rotate-45">+</span></summary>'
        f'<p class="mt-3 text-sm leading-relaxed text-ink-dim">{a}</p></details>'
    )
    last = s.rfind('</details>')
    s = s[:last + len('</details>')] + detail + s[last + len('</details>'):]
    # schema: insert into the literal mainEntity array before its closing ]
    fstart = s.find('const faqSchema')
    key = s.find('mainEntity', fstart)
    open_b = s.find('[', key)
    close_b = s.find(']', open_b)
    entry = (
        "\n    {'@type': 'Question', 'name': " + json.dumps(q) + ', "acceptedAnswer": { '
        + "'@type': 'Answer'" + ', "text": ' + json.dumps(a) + ' } },'
    )
    s = s[:open_b + 1] + entry + s[close_b:]
    p.write_text(s, encoding='utf-8')
    applied += 1
    print(f'{slug}: +1 -> {have + 1} FAQs, schema synced')
print('completed:', applied)
