"""Sync docs/route-reconciliation.csv with the actual built site (read+update registry only)."""
import csv
import pathlib

path = pathlib.Path('docs/route-reconciliation.csv')
rows = list(csv.reader(open(path, encoding='utf-8-sig')))
header, body = rows[0], rows[1:]

built = set()
for f in pathlib.Path('dist').rglob('index.html'):
    rel = str(f.relative_to(pathlib.Path('dist')))
    sep = chr(92)
    rel = rel.replace(sep, '/')
    built.add('/' if rel == 'index.html' else '/' + rel.replace('/index.html', '') + '/')

alias = {
    '/bytespider-crawler/': '/bytespider/',
    '/ccbot-explained/': '/ccbot/',
    '/ai-user-agents-list/': '/ai-crawlers-list/',
}

si = header.index('status')
ai = header.index('actual_route')
pi = header.index('planned_path')
updated = 0
for r in body:
    if len(r) <= si or r[si] != 'planned_not_implemented':
        continue
    planned = r[pi].strip()
    actual = alias.get(planned)
    if actual is None:
        actual = planned if planned in built else None
    if actual and actual in built:
        r[si] = 'planned_and_implemented'
        r[ai] = actual
        updated += 1
print('registry rows marked implemented:', updated)

existing_paths = {r[pi].strip() for r in body if len(r) > pi}
new_pages = [
    '/gptbot/', '/claudebot/', '/google-extended/', '/perplexitybot/', '/oai-searchbot/',
    '/ccbot/', '/bytespider/', '/does-blocking-ai-crawlers-hurt-seo/', '/ai-crawler-verification/',
    '/block-ai-crawlers-cloudflare/', '/gptbot-vs-claudebot/', '/dns-server-not-responding/',
    '/dns-probe-finished-nxdomain/', '/err-name-not-resolved/', '/registrar-vs-dns-hosting/',
    '/check-spf-dkim-dmarc-dig/',
]
nid = 457
added = 0
for planned in new_pages:
    if planned in existing_paths or planned not in built:
        continue
    nid += 1
    body.append([str(nid), 'gap-v2', planned, 'content-lane', 'informational', 'Leaf', 'implemented_outside_map', planned])
    added += 1
print('new rows appended:', added)

with open(path, 'w', encoding='utf-8', newline='') as f:
    w = csv.writer(f)
    w.writerow(header)
    w.writerows(body)
print('registry synced')
