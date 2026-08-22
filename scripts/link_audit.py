import os, re

dist = 'dist'
routes = set()
for root, _, files in os.walk(dist):
    for f in files:
        rel = os.path.relpath(os.path.join(root, f), dist).replace(os.sep, '/')
        if f.endswith('.html'):
            if rel == 'index.html':
                routes.add('/')
            else:
                routes.add('/' + rel.replace('/index.html', '/').replace('.html', ''))
        else:
            # static assets (favicon, _astro bundles, etc.) are linkable too
            routes.add('/' + rel)

broken = {}
for root, _, files in os.walk(dist):
    for f in files:
        if not f.endswith('.html'):
            continue
        path = os.path.join(root, f)
        rel = os.path.relpath(path, dist).replace(os.sep, '/')
        html = open(path, encoding='utf-8', errors='ignore').read()
        for m in re.finditer(r'href="(/[^"#]*)"', html):
            href = m.group(1)
            if href in routes:
                continue
            broken.setdefault(rel, []).append(href)

if not broken:
    print('ALL INTERNAL LINKS RESOLVE OK')
else:
    total = sum(len(v) for v in broken.values())
    print(f'{total} broken links in {len(broken)} pages:')
    for page, hrefs in sorted(broken.items()):
        print(f'\n  {page}:')
        for h in sorted(set(hrefs)):
            print(f'    -> {h}  (x{hrefs.count(h)})')
