#!/usr/bin/env python3
"""Assemble 003_LAB_Docker_Build_Push/README.md from README.tmpl.md + blocks/*.sh + the LAB Jenkinsfile
+ real outputs of the sibling/password run in out/. Owner: yolo3.

Placeholders: {{block:x}} (exact tested host block, marked for verify_readme.py), {{out:x}} (evidence),
{{val:x}}, {{fig:key}} (rendered only when the image exists,
figures numbered in order), {{jenkinsfile}}.
Evidence is rewritten only in two declared ways: run-specific names (devtools-lab003-H, jenkins-lab003-H,
cicd-net-lab003-H, jenkins-lab003-H-home) become the learner names, and the Docker Hub account becomes <DOCKER_USER>."""
import json, os, re, pathlib
W = pathlib.Path(__file__).resolve().parent.parent
LAB = W.parent.parent / '003_LAB_Docker_Build_Push'
IMG = LAB / 'images'
O = W / 'out'
state = dict(l.split('=', 1) for l in (W / 'state.env').read_text().split() if '=' in l) if (W / 'state.env').exists() \
    else json.loads((W / 'run-state.json').read_text())
hub_user = os.environ.get('DOCKER_USER') or (W / 'private' / 'hub_user').read_text().strip()

def clean(s):
    for k, v in (('DC', 'devtools'), ('JC', 'jenkins'), ('NET', 'cicd-net'), ('VOL', 'jenkins_home')):
        s = s.replace(state[k], v)
    s = re.sub(r'(?<![A-Za-z0-9_])' + re.escape(hub_user) + r'(?=/catfood-shop)', '<DOCKER_USER>', s)
    return '\n'.join(l.rstrip() for l in s.split('\n'))

rd = lambda f: clean((O / f).read_text(encoding='utf-8'))
NOISE = ('[Pipeline]', 'Masking supported pattern')

def stages(n):
    cur, res = None, {}
    for l in rd(f'b{n}.txt').splitlines():
        m = re.match(r'\[Pipeline\] \{ \((.+)\)$', l)
        if m: cur = m.group(1); res[cur] = []; continue
        if cur and not l.startswith(NOISE): res[cur].append(l)
    return res

def pick(lines, keep=lambda l: True, drop=lambda l: False):
    out = []
    for l in lines:
        if keep(l) and not drop(l) and (not out or out[-1] != l): out.append(l)
    return '\n'.join(out).strip('\n')

def secs(ms):
    s = round(ms / 1000)
    return f'{s // 60} นาที {s % 60} วินาที' if s >= 60 else f'{s} วินาที'

def stage_ms(n):
    return {name: (st, int(ms)) for name, st, ms in (l.rsplit(' ', 2) for l in rd(f'b{n}.stages').splitlines())}

S = {n: stages(n) for n in range(1, 6)}
J = {n: json.loads(rd(f'b{n}.json')) for n in range(1, 6)}
build_keep = lambda l: bool(re.match(r'(\+ sshpass|#\d+ \[\d/6\]|#\d+ CACHED$|#\d+ \S+ added \d+ packages|#\d+ naming to|IMAGE |catfood-shop:build)', l))
layer_noise = lambda l: bool(re.search(r': (Pulling fs layer|Pull complete|Waiting|Download complete|Verifying Checksum)$', l))
digest = lambda n: re.search(r'digest: (sha256:[0-9a-f]{64})', '\n'.join(S[n]['Push'])).group(1)
tag = lambda n: re.search(r'(\S+-\d+)(?=: digest)', '\n'.join(S[n]['Push'])).group(1)
whole = lambda n: pick(rd(f'b{n}.txt').splitlines(), drop=lambda l: l.startswith(NOISE) or l.startswith('Stage "'))
tail = lambda f, k: '\n'.join(rd(f).rstrip('\n').splitlines()[-k:])
b1_digest_lines = [l for l in S[1]['Push'] if ': digest: ' in l] + [l for l in S[1]['Deploy'] if l.startswith(('image: ', 'เว็บตอบ'))]
b2_digest_lines = [l for l in S[2]['Push'] if ': digest: ' in l] + \
    [l for l in S[2]['Pull'] if l.startswith('Digest: ')] + [l for l in S[2]['Deploy'] if l.startswith(('image: ', 'เว็บตอบ'))]
outs = {
    'b1-connect': pick(S[1]['Connect']), 'b1-clone': pick(S[1]['Clone']),
    'b1-build': pick(S[1]['Build'], build_keep), 'b1-test': pick(S[1]['Test']),
    'b1-push': pick(S[1]['Push'], drop=lambda l: l.startswith('+ set +x')), 'b1-clean': pick(S[1]['Clean']),
    'b1-pull': pick(S[1]['Pull'], drop=layer_noise), 'b1-deploy': pick(S[1]['Deploy']),
    'b2-clean': pick(S[2]['Clean']), 'b2-digest': '\n'.join(b2_digest_lines), 'b1-push-digest': '\n'.join(b1_digest_lines),
    'b3': whole(3), 'b4': pick(S[4]['Clone'] + ['...'] + S[4]['Declarative: Post Actions']),
    'b5': pick(S[5]['Connect'] + ['...'] + S[5]['Declarative: Post Actions'], drop=lambda l: l.startswith('+ ') and not l.startswith('+ sshpass')),
    'sshpass-tail': tail('sshpass.txt', 5),
    # harness-only status lines appended by pty_ssh.py / lab.sh are not what a learner's terminal shows
    'ssh-test': pick(rd('ssh-test.txt').splitlines(), drop=lambda l: l.startswith('[exit=')),
    'unpinned': pick(rd('unpinned.txt').splitlines(), drop=lambda l: l.startswith('exit=')),
}
cm = '\n'.join(S[1]['Connect'])
vals = {
    'prefix': re.sub(r'-\d+$', '', tag(1)),
    'jenkins_host': re.search(r'^jenkins: (\S+)', cm, re.M).group(1),
    'devtools_host': re.search(r'^devtools: (\S+)', cm, re.M).group(1),
    'b1_tag': tag(1), 'b2_tag': tag(2), 'b1_digest': digest(1), 'b2_digest': digest(2), 'b1_short': digest(1)[7:19],
    'b2_downtime': secs(sum(stage_ms(2)[k][1] for k in ('Clean', 'Pull', 'Deploy'))),
    'test_date': rd('date').strip(), 'jenkins_version': rd('jenkins_version').split(':')[1].strip(),
}
for n in range(1, 6):
    vals[f'b{n}_result'] = J[n]['result']; vals[f'b{n}_duration'] = secs(J[n]['duration'])
assert [J[n]['result'] for n in range(1, 6)] == ['SUCCESS', 'SUCCESS', 'FAILURE', 'FAILURE', 'FAILURE'], [J[n]['result'] for n in J]
assert digest(2) in '\n'.join(S[2]['Pull']) and digest(2) in '\n'.join(S[2]['Deploy']), 'b2 pull/deploy digest mismatch'
assert digest(1) in outs['b1-push-digest'] and 'ลบแอปเดิม catfood-web' in outs['b2-clean'] and 'ลบแอปเดิม' not in outs['b1-clean']

# figures: key -> (image, link target or None, alt, caption)
FIG = {
    'diagram_architecture': ('lab3_diagram_sibling_architecture.png', None, 'แผนภาพสถาปัตยกรรมของ LAB 3',
        'แผนภาพประกอบ — `jenkins` และ `devtools` เป็น container พี่น้องบน `cicd-net` · Jenkins SSH ไปที่ `devtools:22` ด้วยรหัสผ่านจาก Jenkins Credentials · `git clone` และ `docker` ทั้งหมดรันบน devtools · `catfood-web` อยู่บน Docker ข้างใน devtools'),
    'diagram_pipeline': ('lab3_diagram_sibling_pipeline.png', None, 'แผนภาพลำดับ 8 stage',
        'แผนภาพประกอบ — Jenkins ควบคุม ทุก stage รันบน devtools ผ่าน SSH · Clean เกิดหลัง Push สำเร็จเท่านั้น · Pull ใช้ digest ที่ Push จดไว้ก่อน Deploy'),
    'hub_pat': ('lab3_hub_04_pat_setup_crop.png', 'lab3_hub_04_pat_setup.png', 'หน้าสร้าง Personal Access Token บน Docker Hub',
        'หน้าสร้าง token บน Docker Hub: ตั้งชื่อ เลือก **Access permissions = Repo Read & Write** แล้วกด **Generate** · Docker Hub แสดง token ครั้งเดียว ให้คัดลอกเก็บทันที'),
    'github_source': ('lab3_github_01_source_crop.png', 'lab3_github_01_source.png', 'ซอร์สร้านบน GitHub',
        'โฟลเดอร์ `catfood-shop` บน GitHub ที่ stage Clone ดึงมา'),
}
for c in json.loads((W / 'captures.json').read_text()):   # real host-browser captures: crop shown, full capture linked
    FIG[c['key']] = (f"lab3_sib_{c['key']}_crop.png", f"lab3_sib_{c['key']}.png", c['alt'], c['caption'])

t = (W / 'README.tmpl.md').read_text(encoding='utf-8')
num = [0]
def fig(m):
    img, link, alt, cap = FIG[m.group(1)]
    if not (IMG / img).exists(): return '\x00'
    num[0] += 1
    pic = f'[![{alt}](./images/{img})](./images/{link})' if link else f'![{alt}](./images/{img})'
    return f'{pic}\n\n*ภาพที่ {num[0]} {cap}*'
t = re.sub(r'\{\{fig:(\w+)\}\}', fig, t)
t = re.sub(r'(\n*\x00\n*)+', '\n\n', t)    # a figure not captured yet leaves no gap
t = re.sub(r'\{\{block:([\w-]+)\}\}', lambda m: f'<!-- lab3-test:{m.group(1)} -->\n```bash\n' + (W / 'blocks' / f'{m.group(1)}.sh').read_text() + '```', t)
def outblock(m):
    f = O / f'{m.group(1)}-block.txt'
    return f'\n✅ **ผลจากรอบทดสอบ:**\n\n```text\n{rd(f.name).rstrip()}\n```\n' if f.exists() else ''
t = re.sub(r'\{\{outblock:([\w-]+)\}\}\n', outblock, t)
cl = O / 'cleanup-block.txt'
t = t.replace('{{cleanup_row}}\n', '| บล็อกเก็บกวาด | ลบ container และ image ที่มี label ของ LAB 3 บน Docker ของ devtools และ `/root/lab3-work` · `devtools`, `jenkins` ยังอยู่ |\n' if cl.exists() else '')
t = re.sub(r'\{\{out:([\w-]+)\}\}', lambda m: outs[m.group(1)] if m.group(1) in outs else rd(f'{m.group(1)}.txt').rstrip('\n'), t)
t = re.sub(r'\{\{val:(\w+)\}\}', lambda m: str(vals[m.group(1)]), t)
t = t.replace('{{jenkinsfile}}', (LAB / 'Jenkinsfile').read_text().rstrip('\n'))
assert not re.search(r'\{\{(block|out|outblock|val|fig|jenkinsfile|cleanup_row)', t), 'unfilled placeholder'
missing = [f for f in re.findall(r'\]\(\./images/([^)]+)\)', t) if not (IMG / f).exists()]
assert not missing, f'missing images {missing}'
(LAB / 'README.md').write_text(t, encoding='utf-8')
print('written', LAB / 'README.md', len(t.splitlines()), 'lines,', num[0], 'figures')
print({k: v for k, v in vals.items()})
