# -*- coding: utf-8 -*-
"""Batch-add bylines + FAQs to pages that need them."""
import re, os, glob

# ===== 1) BYLINES =====
byline = (
    '\n    <div class="mt-10 flex items-center gap-3 rounded-xl border border-line bg-panel/40 px-5 py-3">\n'
    '      <span class="grid h-9 w-9 place-items-center rounded-full bg-gradient-to-br from-accent to-violet font-display text-xs font-bold text-canvas">PD</span>\n'
    '      <div>\n'
    '        <p class="text-sm font-medium text-ink">PromptDNS Team</p>\n'
    '        <p class="text-xs text-ink-faint">Last updated: August 2026</p>\n'
    '      </div>\n'
    '    </div>\n'
)
bc = 0
for f in sorted(glob.glob('src/pages/*.astro')) + sorted(glob.glob('src/pages/*/index.astro')):
    s = open(f, encoding='utf-8').read()
    if 'PromptDNS Team' in s or 'BaseLayout' not in s:
        continue
    idx = s.rfind('</BaseLayout>')
    if idx < 0: continue
    div_close = s.rfind('    </div>', 0, idx)
    if div_close < 0: continue
    s = s[:div_close] + byline + s[div_close:]
    open(f, 'w', encoding='utf-8').write(s)
    bc += 1
print('Bylines added:', bc)

# ===== 2) FAQs =====
def add_faqs(slug, extra):
    path = f'src/pages/{slug}.astro'
    if not os.path.exists(path): return
    s = open(path, encoding='utf-8').read()
    existing = len(re.findall(r'<details class="group', s))
    if existing >= 5: return
    need = max(0, 6 - existing)
    to_add = extra[:need]
    if not to_add: return
    html = ''.join(
        '<details class="group rounded-xl border border-line bg-panel/60 px-5 py-4 open:border-accent/40">'
        '<summary class="flex cursor-pointer list-none items-center justify-between gap-4 font-semibold text-ink [&::-webkit-details-marker]:hidden">' + q +
        '<span class="text-accent transition-transform duration-200 group-open:rotate-45">+</span></summary>'
        '<p class="mt-3 text-sm leading-relaxed text-ink-dim">' + a + '</p></details>'
        for q, a in to_add
    )
    if 'Frequently asked questions' in s:
        idx = s.rfind('</details>')
        if idx > 0:
            ins = idx + len('</details>')
            s = s[:ins] + html + s[ins:]
    else:
        block = ('\n      <h2 class="font-display mt-10 text-xl font-semibold text-ink">Frequently asked questions</h2>\n'
                 '      <div class="mt-3 grid gap-3">' + html + '</div>\n')
        if 'Related' in s:
            idx = s.find('Related')
            h2s = s.rfind('<h2', 0, idx)
            if h2s > 0: s = s[:h2s] + block + s[h2s:]
        else:
            idx = s.rfind('    </div>\n  </div>\n</BaseLayout>')
            if idx > 0: s = s[:idx] + block + s[idx:]
    open(path, 'w', encoding='utf-8').write(s)
    print(f'  FAQs: {slug} ({existing} -> {existing + len(to_add)})')

GENERIC = [
    ("How do I verify my changes?","Run the record lookup to confirm live values, then check the propagation checker for worldwide agreement. Both tools run in your browser."),
    ("What TTL should I use?","3600 seconds is the default. Drop to 300 a day before changes so cutover is quick, then restore."),
    ("Do I need an account to use the tools?","No: all tools are free forever with no signup. Paid plans add continuous monitoring and alerts."),
    ("Why do results differ between tools?","Caching: resolvers serve cached answers within TTL. The propagation checker shows which resolvers disagree."),
    ("Is my data private?","Yes: lookups run in your browser over DNS-over-HTTPS. Nothing is sent to our servers."),
    ("Can I use this for client work?","Yes, commercially. White-label reports are available on the Business plan."),
]

# Apply generic FAQs to all pages with < 5 that don't have topic-specific FAQs
for f in sorted(glob.glob('src/pages/*.astro')):
    s = open(f, encoding='utf-8').read()
    if 'BaseLayout' not in s: continue
    existing = len(re.findall(r'<details class="group', s))
    if existing >= 5: continue
    slug = os.path.basename(f).replace('.astro', '')
    add_faqs(slug, GENERIC)
