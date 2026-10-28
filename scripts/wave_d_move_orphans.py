"""Wave D fix: move orphaned <li> items from after </BaseLayout> into the page's
last in-content <ul> (the real Related list), restoring valid markup."""
import pathlib
import re

PAGES = pathlib.Path('src/pages')

fixed = 0
for p in sorted(PAGES.rglob('*.astro')):
    s = p.read_text(encoding='utf-8')
    bl = s.rfind('</BaseLayout>')
    if bl < 0:
        continue
    tail = s[bl + len('</BaseLayout>'):]
    items = re.findall(r'<li>.*?</li>', tail, re.S)
    if not items:
        continue
    orphan_block = tail
    # target: the last <ul> ... </ul> BEFORE </BaseLayout>
    ul_end = s.rfind('</ul>', 0, bl)
    ul_start = s.rfind('<ul', 0, ul_end)
    if ul_start < 0 or ul_end < ul_start:
        print('NO TARGET UL:', p.stem)
        continue
    # remove the orphaned tail
    s = s[:bl + len('</BaseLayout>')] + ('\n' if tail.startswith('\n') else '') + s[bl + len('</BaseLayout>') + len(orphan_block):]
    # insert items before the target ul's close
    s = s[:ul_end] + ''.join(items) + s[ul_end:]
    p.write_text(s, encoding='utf-8')
    fixed += 1
    print(f'{p.stem}: {len(items)} orphan items moved into in-page list')
print('fixed:', fixed)
