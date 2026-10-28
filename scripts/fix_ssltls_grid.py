"""Remove the duplicate inline FAQ grid from ssl-tls (page already has 6 FAQs via FaqAccordion)."""
import pathlib

p = pathlib.Path('src/pages/ssl-tls.astro')
s = p.read_text(encoding='utf-8')
grid_start = s.find('<div class="mt-3 grid gap-3"><details')
if grid_start < 0:
    print('grid not found (already clean)')
else:
    grid_end = s.find('</div>', grid_start) + len('</div>')
    # safety: the grid contains no nested divs, so the first </div> closes it
    removed = s[grid_start:grid_end]
    assert removed.count('<div') == 1, 'nested div detected, abort'
    s = s[:grid_start] + s[grid_end:]
    p.write_text(s, encoding='utf-8')
    print('duplicate grid removed,', removed.count('<details'), 'details dropped')
