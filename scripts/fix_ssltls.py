"""Fix ssl-tls step 2: restore faqSchema from the 6 FaqAccordion questions."""
import json
import pathlib
import re

p = pathlib.Path('src/pages/ssl-tls.astro')
s = p.read_text(encoding='utf-8')

am = re.search(r'<FaqAccordion faqs=\{\[(.*?)\]\}', s, re.S)
assert am, 'accordion array not found'
pairs = re.findall(r'\["((?:[^"\\]|\\.)*)",\s*"((?:[^"\\]|\\.)*)"\]', am.group(1))
pairs = [(q.replace("\\'", "'"), a.replace("\\'", "'")) for q, a in pairs]
print('accordion questions:', len(pairs))
qjson = ',\n    '.join(
    "{'@type': 'Question', 'name': " + json.dumps(q) + ', "acceptedAnswer": { '
    + "'@type': 'Answer'" + ', "text": ' + json.dumps(a) + ' } }'
    for q, a in pairs
)
fstart = s.find('const faqSchema')
key = s.find('mainEntity', fstart)
open_b = s.find('[', key)
close_b = s.find(']', open_b)
s = s[:open_b + 1] + '\n    ' + qjson + '\n  ' + s[close_b:]
p.write_text(s, encoding='utf-8')
print('faqSchema restored with', len(pairs), 'questions')
