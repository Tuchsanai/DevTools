#!/usr/bin/env python3
"""check-yaml-teaching.py <session-dir> — every *.yaml in each lab is mentioned in its README's YAML section; YAML_Guide.md exists with anchors referenced by READMEs; session README links the guide."""
import sys, os, re, glob
sess = sys.argv[1].rstrip('/'); fails = 0
def out(k, m):
    global fails
    if k == 'FAIL': fails += 1
    print(f'{k:4s} {m}')
guide = os.path.join(sess, 'YAML_Guide.md')
if not os.path.exists(guide): out('FAIL', 'YAML_Guide.md missing'); sys.exit(1)
g = open(guide, encoding='utf-8').read()
anchors = set()
for h in re.findall(r'^#{1,4} +(.+)$', g, re.M):
    a = re.sub(r'[^\w\s฀-๿-]', '', h.strip().lower()); a = re.sub(r'\s+', '-', a); anchors.add(a)
out('OK' if 150 <= len(g.splitlines()) <= 400 else 'WARN', f'YAML_Guide.md {len(g.splitlines())} lines (target 150-400 incl. recap)')
out('OK' if g.count('```yaml') >= 4 else 'FAIL', f"guide has {g.count('```yaml')} yaml blocks")
out('OK' if not re.search(r'\.\./0[123]_Session', g) else 'FAIL', 'guide has no cross-session path')
sr = open(os.path.join(sess, 'README.md'), encoding='utf-8').read()
out('OK' if 'YAML_Guide.md' in sr else 'FAIL', 'session README links YAML_Guide.md')
for lab in sorted(glob.glob(os.path.join(sess, '0[0-9][0-9]-*'))):
    rp = os.path.join(lab, 'README.md'); t = open(rp, encoding='utf-8').read(); name = os.path.basename(lab)
    yamls = [os.path.relpath(y, lab) for y in glob.glob(os.path.join(lab, '**', '*.yaml'), recursive=True)]
    sec = re.search(r'^## \d+\. การอ่าน YAML ของปฏิบัติการนี้', t, re.M)
    if not sec and yamls: out('FAIL', f'{name}: no "การอ่าน YAML ของปฏิบัติการนี้" section'); continue
    if not yamls:
        out('OK' if sec or True else 'WARN', f'{name}: no manifests (section optional)'); continue
    missing = [y for y in yamls if os.path.basename(y) not in t]
    out('OK' if not missing else 'FAIL', f'{name}: {len(yamls)} yaml files, unmentioned: {missing[:5]}')
    links = re.findall(r'YAML_Guide\.md#([^)\s]+)', t)
    bad = [l for l in links if l not in anchors]
    out('OK' if not bad else 'FAIL', f'{name}: {len(links)} guide links, bad anchors: {bad[:4]}')
    n = len(t.splitlines()); out('OK' if n <= 450 else 'WARN', f'{name}: {n} lines')
print('YAML-TEACHING FAILS =', fails); sys.exit(min(fails, 99))
