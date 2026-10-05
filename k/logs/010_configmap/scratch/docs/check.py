#!/usr/bin/env python3
"""ตรวจ README บท 010: ลิงก์/ภาพ, anchor, ภาพครบ+caption, YAML, ไฟล์ที่อ้างในคำสั่ง, ผลลัพธ์มาจาก log, คำต้องห้าม"""
import json, os, re, glob, unicodedata, html
import yaml

K = '/root/workspace/DevTools/k'
CH = f'{K}/010_kubernetes_configmap'
LAB = f'{CH}/02_LAB'
imgs = json.load(open(f'{K}/logs/010_configmap/images.json'))
byid = {x['id']: x for x in imgs}
paths_json = {x['path'] for x in imgs}
docs = {'main': f'{CH}/README.md', 'theory': f'{CH}/01_Theory/README.md', 'lab': f'{CH}/02_LAB/README.md'}
errors, warns = [], []

# corpus ของผลจริง
corpus = ''
for f in glob.glob(f'{K}/logs/010_configmap/lab-run/*') + glob.glob(f'{K}/logs/010_configmap/scratch/t/*.log'):
    corpus += open(f, errors='replace').read() + '\n'
for f in glob.glob(f'{LAB}/labs/**/*', recursive=True) + glob.glob(f'{LAB}/som-shop-v6/**/*', recursive=True):
    if os.path.isfile(f) and not f.endswith('.png') and 'node_modules' not in f and 'package-lock' not in f:
        corpus += open(f, errors='replace').read() + '\n'
corpus_lines = set(l.strip() for l in corpus.splitlines())


def slug(h):
    h = re.sub(r'<[^>]+>', '', h).strip().lower()
    out = []
    for ch in h:
        c = unicodedata.category(ch)
        if ch in ' -_' or c[0] in 'LMN':
            out.append('-' if ch == ' ' else ch)
    return ''.join(out)


def blocks(text):
    return re.findall(r'^```(\w*)\n(.*?)^```', text, re.S | re.M)


for name, p in docs.items():
    text = open(p).read()
    d = os.path.dirname(p)
    nocode = re.sub(r'^```.*?^```', '', text, flags=re.S | re.M)
    # anchors
    anchors = set()
    seen = {}
    for h in re.findall(r'^#{1,6} (.+)$', nocode, re.M):
        s = slug(h)
        n = seen.get(s, 0); seen[s] = n + 1
        anchors.add(s if n == 0 else f'{s}-{n}')
    anchors |= set(re.findall(r'id="([^"]+)"', text))
    # links
    links = re.findall(r'\]\(([^)\s]+)\)', nocode) + re.findall(r'src="([^"]+)"', nocode)
    for l in links:
        if l.startswith('http'):
            continue
        if l.startswith('#'):
            if l[1:] not in anchors:
                errors.append(f'{name}: anchor ไม่มีปลายทาง {l}')
            continue
        path, _, frag = l.partition('#')
        full = os.path.normpath(os.path.join(d, path))
        if not os.path.exists(full):
            if full in paths_json:
                warns.append(f'{name}: ภาพยังไม่มีไฟล์ (กำลังสร้าง ชื่อตรง images.json) {os.path.basename(full)}')
            else:
                errors.append(f'{name}: ลิงก์/ภาพไม่มีไฟล์ {l}')
    # figures + captions
    figs = re.findall(r'<img src="([^"]+)" alt="[^"]*"[^>]*><br>\n  <em>(?:<b>รูปที่ \d+</b> )?(.*?)</em>', text)
    used = []
    for src, cap in figs:
        full = os.path.normpath(os.path.join(d, src))
        m = [x for x in imgs if x['path'] == full]
        if m:
            used.append(m[0]['id'])
            if m[0]['caption_th'] != cap:
                errors.append(f'{name}: caption ไม่ตรง {m[0]["id"]}')
    if name == 'theory':
        exp = [f'T{i:02d}' for i in range(1, 41)]
        if used != exp:
            errors.append(f'theory: ภาพ T ไม่ครบ/ไม่ตามลำดับ {used}')
    if name == 'lab':
        exp = {f'L{i:02d}' for i in range(1, 22)}
        if set(used) != exp or len(used) != 21:
            errors.append(f'lab: ภาพ L ไม่ครบ {sorted(exp - set(used))} dup={len(used)}')
        shots = re.findall(r'src="(images/screenshots/[^"]+)"', text)
        if len(set(shots)) != 4:
            errors.append(f'lab: screenshot ไม่ครบ 4 {shots}')
    # fig numbering
    nums = [int(x) for x in re.findall(r'id="fig-(\d+)"', text)]
    if nums != list(range(1, len(nums) + 1)):
        errors.append(f'{name}: เลขรูปไม่ต่อเนื่อง')
    # yaml
    for lang, body in blocks(text):
        if lang == 'yaml':
            try:
                list(yaml.safe_load_all(body))
            except Exception as e:
                errors.append(f'{name}: YAML parse ไม่ได้: {body[:60]!r} {e}')
    # text blocks มาจาก log
    for lang, body in blocks(text):
        if lang != 'text':
            continue
        for line in body.splitlines():
            s = line.strip()
            if not s or s == '...' or s.startswith('...'):
                continue
            s2 = s[2:] if s.startswith('$ ') else s
            if name == 'main' or (s not in corpus_lines and s2 not in corpus):
                if name == 'main':
                    continue  # main มีแต่โครงสร้างโฟลเดอร์
                if '├──' in s or '└──' in s or '│' in s:
                    continue
                errors.append(f'{name}: บรรทัดผลลัพธ์ไม่พบใน log: {s[:100]}')
    # คำต้องห้าม
    for bad in ['2224', '172.18.0.1', 'askpass', '30090', '30091', 'cm010', 'k8s-lab-cm', 'cmsec', 'k8s-lab.sh']:
        if bad in text:
            errors.append(f'{name}: มีคำต้องห้าม {bad}')
    if re.search(r'\b1300\d\b', text):
        errors.append(f'{name}: มี port 1300x')
    if '{{' in text:
        errors.append(f'{name}: placeholder ค้าง')

# คำสั่งอ้างไฟล์จริง (LAB README): ติดตาม cd
text = open(docs['lab']).read()
cwd = LAB
for lang, body in blocks(text):
    if lang != 'bash':
        continue
    for line in body.splitlines():
        m = re.match(r'\s*cd (\S+)', line)
        if m:
            t = m.group(1)
            cwd = t if t.startswith('/') else os.path.normpath(os.path.join(cwd, t))
            cwd = cwd.replace('/workspace/010_kubernetes_configmap', CH)
            if not os.path.isdir(cwd):
                errors.append(f'lab: cd ไปโฟลเดอร์ที่ไม่มี {t}')
        for tok in re.findall(r'(?:-f |-k |--from-file=|--from-env-file=|\./|bash )([\w./=-]+)', line):
            if tok in ('.', '-') or tok.startswith('/') or tok in ('logo.bin', 'big.txt', 'big2.txt'):
                continue
            tok = tok.split('=')[-1]
            if not os.path.exists(os.path.join(cwd, tok)):
                errors.append(f'lab: ไฟล์ในคำสั่งไม่พบ {tok} (cwd={cwd.replace(CH, "")}) :: {line.strip()[:80]}')

for e in errors:
    print('ERROR', e)
for w in sorted(set(warns)):
    print('WARN ', w)
print(f'errors={len(errors)} warns={len(set(warns))}')
