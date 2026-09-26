#!/usr/bin/env python3
"""Assemble 003 README from README.tmpl.md + blocks/*.sh + ../../003_LAB_Docker_Build_Push/Jenkinsfile + real outputs in out3/."""
import json, re, pathlib
W = pathlib.Path(__file__).resolve().parent.parent
LAB = W.parent.parent / '003_LAB_Docker_Build_Push'
O = W / 'out3'
t = (W / 'README.tmpl.md').read_text()
rd = lambda f: (O / f).read_text(encoding='utf-8')

def stages(fname):
    cur, res = None, {}
    for l in rd(fname).splitlines():
        m = re.match(r'\[Pipeline\] \{ \((.+)\)$', l)
        if m: cur = m.group(1); res[cur] = []; continue
        if cur and not l.startswith('[Pipeline]') and not l.startswith('Masking supported pattern'):
            res[cur].append(l)
    return res

def pick(lines, keep):
    out = []
    for l in lines:
        if keep(l) and (not out or out[-1] != l): out.append(l)
    return '\n'.join(out).strip('\n')

def secs(ms):
    s = round(ms / 1000)
    return f'{s // 60} นาที {s % 60} วินาที' if s >= 60 else f'{s} วินาที'

def stage_ms(n):
    out = {}
    for l in rd(f'b{n}.stages').splitlines():
        name, state, ms = l.rsplit(' ', 2); out[name] = (state, int(ms))
    return out

s1, s2, s3, s4, fr = (stages(f) for f in ('b1.txt', 'b2.txt', 'b3.txt', 'b4.txt', 'enc-bug-b1.txt'))
ascii_only = lambda l: all(ord(c) < 128 for c in l)
build_keep = lambda l: bool(re.match(r'(\+ ssh|#\d+ \[\d/6\]|#\d+ CACHED$|#\d+ \S+ added \d+ packages|#\d+ naming to|IMAGE |catfood-shop:build)', l))
digest = lambda st, stage: re.search(r'digest: (sha256:[0-9a-f]{64})', '\n'.join(st[stage])).group(1)
j = lambda n: json.loads(rd(f'b{n}.json'))
down = lambda n: secs(sum(stage_ms(n)[k][1] for k in ('Clean', 'Pull', 'Deploy')))
tag = lambda st: re.search(r'lab3-\S+-\d+(?=: digest)', '\n'.join(st['Push'])).group(0)
b3 = [l for l in rd('b3.txt').splitlines() if not l.startswith('[Pipeline]') and not l.startswith('Stage "') and not l.startswith('Masking')]
outs = {
    'b1-connect': '\n'.join(s1['Connect']), 'b1-clone': '\n'.join(s1['Clone']),
    'fresh-build': pick([l for l in fr['Build'] if ascii_only(l)], build_keep),
    'b1-build': pick(s1['Build'], build_keep), 'b1-test': '\n'.join(s1['Test']),
    'b1-push': '\n'.join(s1['Push']).strip('\n'), 'b1-clean': '\n'.join(s1['Clean']),
    'b1-pull': '\n'.join(s1['Pull']), 'b1-deploy': '\n'.join(s1['Deploy']),
    'b2-clean': '\n'.join(s2['Clean']),
    'b2-push-digest': pick(s2['Push'], lambda l: 'digest' in l),
    'b2-pull': '\n'.join(s2['Pull']), 'b2-deploy': '\n'.join(s2['Deploy']),
    'b3': '\n'.join(b3).strip('\n'),
    'b4': '\n'.join(s4['Clone'] + ['...'] + s4['Declarative: Post Actions']),
    'before-b2-app': rd('before-b2-app.txt').rstrip('\n'),
    'cleanup': rd('cleanup-with-foreign.txt').rstrip('\n'),
}
d1, d2 = digest(s1, 'Push'), digest(s2, 'Push')
cm = '\n'.join(s1['Connect'])
b5 = j(5)['result']; b5clean = stage_ms(5)['Clean'][0]
vals = {
    'prefix': re.sub(r'-\d+$', '', tag(s1)),
    'jenkins_host': re.search(r'^jenkins: (\S+)', cm, re.M).group(1),
    'devtools_host': re.search(r'^devtools: (\S+)', cm, re.M).group(1),
    'fresh_pushed': sum(1 for l in fr['Push'] if l.endswith(': Pushed')),
    'b1_duration': secs(j(1)['duration']), 'b2_duration': secs(j(2)['duration']), 'b3_duration': secs(j(3)['duration']),
    'b1_result': j(1)['result'], 'b2_result': j(2)['result'], 'b3_result': j(3)['result'], 'b4_result': j(4)['result'],
    'b1_tag': tag(s1), 'b2_tag': tag(s2), 'b1_digest': d1, 'b2_digest': d2,
    'b1_short': d1[7:19], 'b2_short': d2[7:19],
    'b1_downtime': down(1), 'b2_downtime': down(2),
    'test_date': rd('date').strip(), 'jenkins_version': rd('jenkins_version').split(':')[1].strip(),
    'owner_row': f'| build #5 (มี `catfood-web` ที่ไม่ใช่ของแล็บอยู่ก่อน) | `{b5}` ที่ Clean (`{b5clean}`) ด้วยข้อความ `พบ container catfood-web ที่ไม่ได้สร้างโดย LAB 3` container นั้นยังอยู่ · Pull/Deploy ถูกข้าม · image `catfood-shop:build-5` ที่ build แล้วค้างในเครื่อง (ลบด้วยบล็อกเก็บกวาด) |\n'
                 '| บล็อกเก็บกวาด | ลบ container ที่มี label ของ LAB 3, image ของร้าน และ `/root/lab3-work` · `jenkins`, `cicd-net`, `jenkins_home` และ `catfood-web` ที่ไม่มี label ของแล็บยังอยู่ · รอบทดสอบนี้ใช้ตัวเลือก image ตามชื่อ `catfood-shop` รุ่นก่อน บล็อกปัจจุบันเลือก image ด้วย label `devtools.lab=lab3` (ตรวจ syntax แล้ว แต่ไม่ได้รัน end-to-end ซ้ำ) |\n'
                 '| หมายเหตุการทดสอบ | การรันครั้งแรกของวัน (tag `lab3-20260926-1`) ส่ง config ของ job ผ่าน REST API โดยไม่ระบุ charset ข้อความไทยใน console จึงเพี้ยน จึงแก้เครื่องมือทดสอบให้ส่ง `charset=UTF-8` ลบ build นั้นและรันใหม่ด้วย prefix `' + re.sub(r'-\d+$', '', tag(s1)) + '` tag เดิมยังอยู่บน Docker Hub เป็นหลักฐาน · นักศึกษาวาง Jenkinsfile ผ่านหน้าเว็บ จึงไม่พบปัญหานี้ |',
}
t = re.sub(r'\{\{block:([\w-]+)\}\}', lambda m: '```bash\n' + (W / 'blocks' / f'{m.group(1)}.sh').read_text() + '```', t)
rstrip_lines = lambda s: '\n'.join(l.rstrip() for l in s.split('\n'))    # ผลที่จับจริงบางบรรทัดมีช่องว่างท้าย (ตาราง docker/hostname -I) ตัดทิ้งให้ git diff --check สะอาด
t = re.sub(r'\{\{out:([\w-]+)\}\}', lambda m: rstrip_lines(outs[m.group(1)] if m.group(1) in outs else rd(f'{m.group(1)}.txt').rstrip('\n')), t)
t = re.sub(r'\{\{val:(\w+)\}\}', lambda m: str(vals[m.group(1)]), t)
t = t.replace('{{jenkinsfile}}', (LAB / 'Jenkinsfile').read_text().rstrip('\n'))
assert not re.search(r'\{\{(block|out|val|jenkinsfile)', t), 'unfilled placeholder'
missing = [f for f in re.findall(r'\]\(\./images/([^)]+)\)', t) if not (LAB / 'images' / f).exists()]
assert not missing, f'missing images {missing}'    # ภาพครอป (readability/make_crops.py) และภาพเต็มที่ลิงก์ไว้ต้องมีครบ
(LAB / 'README.md').write_text(t)
print('written', LAB / 'README.md', len(t.splitlines()), 'lines'); print({k: v for k, v in vals.items() if k != 'owner_row'})
