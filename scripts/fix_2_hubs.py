"""Final 2 pages: rebuild faqSchema mainEntity via bracket-depth scan within the
frontmatter region (handles consts that close without semicolons)."""
import json
import pathlib
import re

PAGES = pathlib.Path('src/pages')

for slug in ['dns-providers', 'email-deliverability']:
    p = PAGES / f'{slug}.astro'
    s = p.read_text(encoding='utf-8')
    pairs = []
    for m in re.finditer(r'<summary[^>]*>(.*?)<span[^>]*>.*?</span></summary>(.*?)</details>', s, re.S):
        q = re.sub(r'<[^>]+>', '', m.group(1)).strip()
        a = re.sub(r'<[^>]+>', ' ', m.group(2))
        a = re.sub(r'\s+', ' ', a).strip()
        if q and a:
            pairs.append((q, a))
    am = re.search(r'<FaqAccordion faqs=\{\[(.*?)\]\}', s, re.S)
    if am:
        for q, a in re.findall(r'\["((?:[^"\\]|\\.)*)",\s*"((?:[^"\\]|\\.)*)"\]', am.group(1)):
            pairs.append((q.replace("\\'", "'"), a.replace("\\'", "'")))
    seen, uniq = set(), []
    for q, a in pairs:
        if q not in seen:
            seen.add(q)
            uniq.append((q, a))
    qjson = ',\n    '.join(
        "{'@type': 'Question', 'name': " + json.dumps(q) + ', "acceptedAnswer": { '
        + "'@type': 'Answer'" + ', "text": ' + json.dumps(a) + ' } }'
        for q, a in uniq
    )
    fs = s.find('const faqSchema')
    fm = s.find('---', fs)
    key = s.find('mainEntity', fs)
    open_b = s.find('[', key)
    # bracket-depth scan for the matching close
    depth = 0
    close_b = open_b
    for i in range(open_b, fm):
        if s[i] == '[':
            depth += 1
        elif s[i] == ']':
            depth -= 1
            if depth == 0:
                close_b = i
                break
    s = s[:open_b + 1] + '\n    ' + qjson + '\n  ' + s[close_b:]
    p.write_text(s, encoding='utf-8')
    print(f'{slug}: rebuilt with {len(uniq)} questions (bracket scan)')
