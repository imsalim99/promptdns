"""Merge the clean tail into gen_batch4_smtp.py, fixing the breadcrumb line."""
import pathlib

head = pathlib.Path('scripts/gen_batch4_head.txt').read_text(encoding='utf-8')
tail = pathlib.Path('scripts/gen_batch4_tail.txt').read_text(encoding='utf-8')
# fix the breadcrumb line: double-close braces left from f-string escaping
old = "'  breadcrumb={[[' + chr(34) + 'Home' + chr(34) + ', ' + chr(34) + '/' + chr(34) + '], [' + chr(34) + 'Email Authentication' + chr(34) + ', ' + chr(34) + '/email-authentication/' + chr(34) + '], [' + chr(34) + 'SMTP ' + chr(43) + ' pg[' + chr(39) + 'code' + chr(39) + ']' + chr(34) + ']]}}',"
if old not in tail:
    # simpler: fix the actual line present
    lines = tail.split('\n')
    for i, line in enumerate(lines):
        if 'breadcrumb=' in line and ']]}}' in line:
            lines[i] = line.replace(']]}}', ']]}')
            tail = '\n'.join(lines)
            print('breadcrumb double-close fixed')
            break
merged = head + tail
pathlib.Path('scripts/gen_batch4_smtp.py').write_text(merged, encoding='utf-8')
print('merged')
