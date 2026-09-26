#!/usr/bin/env python3
"""Assemble 003 README from README.tmpl.md + blocks/*.sh + ../../003_LAB_Docker_Build_Push/Jenkinsfile + real outputs in out2/."""
import json, re, pathlib
W = pathlib.Path(__file__).resolve().parent.parent
LAB = W.parent.parent / '003_LAB_Docker_Build_Push'
O = W / 'out2'
t = (W / 'README.tmpl.md').read_text()

def clean(txt):
    return [l for l in txt.splitlines() if not l.startswith('[Pipeline]') and not l.startswith('Masking supported pattern')]

def stages(n):
    cur, res = None, {}
    for l in (O / f'b{n}.txt').read_text().splitlines():
        m = re.match(r'\[Pipeline\] \{ \((.+)\)$', l)
        if m: cur = m.group(1); res[cur] = []; continue
        if cur: res[cur].append(l)
    return {k: clean('\n'.join(v)) for k, v in res.items()}

def pick(lines, keep, tail):
    out, last = [], -2
    for i, l in enumerate(lines):
        if keep(l) or i >= len(lines) - tail:
            if last != i - 1 and out: out.append('...')
            out.append(l); last = i
    return '\n'.join(out)

def dur(n):
    ms = json.loads((O / f'b{n}.json').read_text())['duration']; s = round(ms / 1000)
    return f'{s // 60} นาที {s % 60} วินาที' if s >= 60 else f'{s} วินาที'

s1, s2 = stages(1), stages(2)
build_keep = lambda l: l.startswith('+ ssh') or re.match(r'#\d+ \[\d/6\] ', l) or re.search(r'added \d+ packages', l) or re.match(r'#\d+ CACHED', l)
outs = {
    'b1-preflight': '\n'.join(s1['Preflight']), 'b1-clone': '\n'.join(s1['Clone']),
    'b1-build': pick(s1['Build'], build_keep, 2), 'b1-test': '\n'.join(s1['Test']),
    'b1-deploy': '\n'.join(s1['Deploy']), 'b2-build': pick(s2['Build'], build_keep, 2),
    'b2-deploy': '\n'.join(s2['Deploy']),
    'b3': '\n'.join(l for l in clean((O / 'b3.txt').read_text()) if not l.startswith('Stage "')),
}
pf = '\n'.join(s1['Preflight'])
cnt = lambda st, pat: sum(1 for l in st if re.search(pat, l))
b6 = json.loads((O / 'b6.json').read_text())['result']
vals = {
    'jenkins_host': re.search(r'^jenkins: (\S+)', pf, re.M).group(1),
    'devtools_host': re.search(r'^devtools: (\S+)', pf, re.M).group(1),
    'b1_duration': dur(1), 'b2_duration': dur(2), 'b3_duration': dur(3),
    'b1_cached': cnt(s1['Build'], r'^#\d+ CACHED'), 'b2_cached': cnt(s2['Build'], r'^#\d+ CACHED'),
    'b1_pushed': cnt(s1['Push'], r': Pushed$'), 'b2_pushed': cnt(s2['Push'], r': Pushed$'),
    'test_date': (O / 'date').read_text().strip(),
    'restart_result': f'gateway เดิม, build #6 = `{b6}` โดยไม่ต้องตั้งค่า SSH ใหม่',
}
t = re.sub(r'\{\{block:([\w-]+)\}\}', lambda m: '```bash\n' + (W / 'blocks' / f'{m.group(1)}.sh').read_text() + '```', t)
t = re.sub(r'\{\{out:([\w-]+)\}\}', lambda m: outs[m.group(1)] if m.group(1) in outs else (O / f'{m.group(1)}.txt').read_text().rstrip('\n'), t)
t = re.sub(r'\{\{val:(\w+)\}\}', lambda m: str(vals[m.group(1)]), t)
t = t.replace('{{jenkinsfile}}', (LAB / 'Jenkinsfile').read_text().rstrip('\n'))
assert not re.search(r'\{\{(block|out|val):', t), 'unfilled placeholder'
(LAB / 'README.md').write_text(t)
print('written', LAB / 'README.md', len(t.splitlines()), 'lines'); print(vals)
