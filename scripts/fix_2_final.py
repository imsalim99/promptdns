"""Final fix for dns-providers + email-deliverability:
1. Remove the 3 duplicate inline FAQ details (they duplicate frontmatter faqs).
2. Rebuild faqSchema mainEntity from the frontmatter const faqs (6 questions)."""
import json
import pathlib
import re

for slug in ['dns-providers', 'email-deliverability']:
    p = pathlib.Path(f'src/pages/{slug}.astro')
    s = p.read_text(encoding='utf-8')

    # 1. remove my injected inline grid (contains the duplicate questions)
    grid_start = s.find('<div class="mt-3 grid gap-3"><details')
    if grid_start > 0:
        grid_end = s.find('</div>', grid_start) + len('</div>')
        removed = s[grid_start:grid_end]
        assert removed.count('<div') == 1, 'nested div, abort'
        s = s[:grid_start] + s[grid_end:]
        print(f'{slug}: duplicate grid removed ({removed.count("<details")} details)')
    else:
        print(f'{slug}: grid already gone')

    # 2. parse the frontmatter const faqs pairs
    fm_start = s.find('const faqs')
    arr = s.find('[', fm_start)
    depth = 0
    arr_end = arr
    for i in range(arr, s.find('---', arr)):
        if s[i] == '[':
            depth += 1
        elif s[i] == ']':
            depth -= 1
            if depth == 0:
                arr_end = i
                break
    arr_text = s[arr:arr_end + 1]
    pairs = re.findall(r"[\"']((?:[^\"'\\]|\\.)*)[\"']\s*,\s*[\"']((?:[^\"'\\]|\\.)*)[\"']", arr_text)
    pairs = [(q.replace("\\'", "'"), a.replace("\\'", "'")) for q, a in pairs]
    print(f'{slug}: frontmatter faqs parsed: {len(pairs)}')
    for q, a in pairs[:6]:
        print('   -', q[:60])

    # 3. rebuild faqSchema mainEntity from those pairs
    qjson = ',\n    '.join(
        "{'@type': 'Question', 'name': " + json.dumps(q) + ', "acceptedAnswer": { '
        + "'@type': 'Answer'" + ', "text": ' + json.dumps(a) + ' } }'
        for q, a in pairs
    )
    fs = s.find('const faqSchema')
    fm = s.find('---', fs)
    key = s.find('mainEntity', fs)
    open_b = s.find('[', key)
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
    print(f'{slug}: schema rebuilt with {len(pairs)}')
