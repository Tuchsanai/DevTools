#!/usr/bin/env python3
"""tmp/README.teach.md (+ optional tmp/console-block.md for @CONSOLE@) -> README.md with figures renumbered in order.
Placeholders @XX@ are new figures; references 'ภาพที่ N' / 'ภาพที่ N–M' are remapped from the old numbering."""
import os, re
W = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); LAB = os.path.abspath(os.path.join(W, '..', '..'))
R = open(f'{W}/tmp/README.teach.md', encoding='utf-8').read()
cb = f'{W}/tmp/console-block.md'
R = R.replace('@CONSOLE@\n', open(cb, encoding='utf-8').read() if os.path.exists(cb) else '')
caps = re.findall(r'^\*ภาพที่ (\d+|@\w+@)([ก-ฮ]?)', R, re.M)
mapping, n, last = {}, 0, None
for num, suf in caps:
    if num != last:
        n += 1; last = num
    mapping[num] = n
def sub(m):
    k = m.group(1)
    return 'ภาพที่ ' + str(mapping[k])
R = re.sub(r'ภาพที่ (\d+)–(\d+)', lambda m: f'ภาพที่#{mapping[m.group(1)]}–#{mapping[m.group(2)]}', R)
R = re.sub(r'ภาพที่ (\d+|@\w+@)', sub, R).replace('–#', '–').replace('ภาพที่#', 'ภาพที่ ')
assert '@' not in ''.join(re.findall(r'ภาพที่ \S+', R))
open(f'{LAB}/README.md', 'w', encoding='utf-8').write(R)
print({k: v for k, v in mapping.items() if not k.isdigit() or int(k) != v})
