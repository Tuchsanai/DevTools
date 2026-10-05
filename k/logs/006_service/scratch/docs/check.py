#!/usr/bin/env python3
"""ตรวจ README บท 006: ลิงก์/ภาพ, anchor, ภาพ T/L ครบและเรียง, caption ตรง images.json, YAML parse, ไม่มี Deployment ในขั้นตอน LAB, ไม่มีรายละเอียดเครื่องทดสอบ"""
import json, os, re, html, unicodedata, glob
import yaml

BASE = '/root/workspace/DevTools/k'
CH = f'{BASE}/006_kubernetes_service'
IMGS = json.load(open(f'{BASE}/logs/006_service/images.json', encoding='utf-8'))
BYPATH = {os.path.realpath(i['path']): i for i in IMGS}
FILES = {'top': f'{CH}/README.md', 'theory': f'{CH}/01_Theory/README.md', 'lab': f'{CH}/02_LAB/README.md'}
errors, notes = [], []


def slug(s):
    out = []
    for ch in s.strip().lower():
        if ch == ' ':
            out.append('-')
        elif ch in '-_' or unicodedata.category(ch)[0] in 'LMN':
            out.append(ch)
    return ''.join(out)


def strip_code(text):
    return re.sub(r'^```.*?^```', '', text, flags=re.M | re.S)


def anchors_of(path):
    t = open(path, encoding='utf-8').read()
    ids = set(re.findall(r'id="([^"]+)"', t))
    seen = {}
    for h in re.findall(r'^#{1,6} (.+)$', strip_code(t), flags=re.M):
        s = slug(re.sub(r'`', '', h))
        n = seen.get(s, 0)
        ids.add(s if n == 0 else f'{s}-{n}')
        seen[s] = n + 1
    return ids


pending = 0
for name, path in FILES.items():
    text = open(path, encoding='utf-8').read()
    body = strip_code(text)
    d = os.path.dirname(path)
    my_anchors = anchors_of(path)
    # 1) ลิงก์และภาพ
    targets = re.findall(r'<img src="([^"]+)"', body) + re.findall(r'\]\(([^)\s]+)\)', body)
    for t in targets:
        if t.startswith(('http://', 'https://')):
            continue
        p, _, frag = t.partition('#')
        if p == '':
            if frag not in my_anchors:
                errors.append(f'[{name}] anchor ไม่มีปลายทาง: #{frag}')
            continue
        full = os.path.realpath(os.path.join(d, p))
        if not os.path.exists(full):
            if full in BYPATH:
                pending += 1
            else:
                errors.append(f'[{name}] ไฟล์ไม่มี: {t}')
            continue
        if frag and full.endswith('.md'):
            if frag not in anchors_of(full):
                errors.append(f'[{name}] anchor ในไฟล์อื่นไม่มี: {t}')
    # 2) caption ตรง
    for src, cap in re.findall(r'<img src="([^"]+)"[^>]*><br>\s*<em>(.*?)</em>', text, flags=re.S):
        full = os.path.realpath(os.path.join(d, src))
        if full in BYPATH:
            c = html.unescape(re.sub(r'^<b>รูปที่ \d+</b> ', '', cap.strip()))
            if c != BYPATH[full]['caption_th']:
                errors.append(f'[{name}] caption ไม่ตรง {BYPATH[full]["id"]}:\n   doc={c}\n  json={BYPATH[full]["caption_th"]}')
    # 3) ภาพ T/L ครบและเรียง
    used = [BYPATH[os.path.realpath(os.path.join(d, s))]['id'] for s in re.findall(r'<img src="([^"]+)"', text)
            if os.path.realpath(os.path.join(d, s)) in BYPATH]
    if name == 'theory':
        exp = [f'T{i:02d}' for i in range(1, 37)]
    elif name == 'lab':
        exp = [f'L{i:02d}' for i in range(1, 25)]
    else:
        exp = ['T01']
    if used != exp:
        errors.append(f'[{name}] ลำดับ/ครบของภาพไม่ตรง: {used}')
    nfig = len(re.findall(r'id="fig-\d+"', text))
    figs = [int(x) for x in re.findall(r'id="fig-(\d+)"', text)]
    if figs != list(range(1, nfig + 1)):
        errors.append(f'[{name}] เลขรูปไม่ต่อเนื่อง')
    ss = re.findall(r'<img src="(images/screenshots/[^"]+)"', text)
    for s in ss:
        cap = re.search(re.escape(s) + r'"[^>]*><br>\s*<em>(.*?)</em>', text, flags=re.S).group(1)
        if 'ภาพหน้าจอจริงจากการทดลอง' not in cap:
            errors.append(f'[{name}] screenshot ไม่ระบุว่าเป็นภาพหน้าจอจริง: {s}')
    # 4) YAML parse
    blocks = re.findall(r'^```yaml\n(.*?)^```', text, flags=re.M | re.S)
    for i, b in enumerate(blocks):
        try:
            list(yaml.safe_load_all(b))
        except Exception as e:
            errors.append(f'[{name}] YAML block {i+1} parse ไม่ได้: {str(e).splitlines()[0]}')
        if re.search(r'^\s*kind:\s*Deployment', b, flags=re.M):
            errors.append(f'[{name}] YAML block {i+1} มี kind: Deployment')
    # 5) ไม่มี Deployment ในขั้นตอน LAB (bash/powershell blocks)
    if name == 'lab':
        for b in re.findall(r'^```(?:bash|powershell)\n(.*?)^```', text, flags=re.M | re.S):
            for line in b.splitlines():
                if re.search(r'rollout|create deployment|deploy/|deployment\.apps|kind: Deployment', line, flags=re.I):
                    errors.append(f'[lab] คำสั่งใช้ Deployment: {line}')
                elif re.search(r'deployment', line, flags=re.I) and 'delete -f /workspace/examples/web-deployment.yaml' not in line:
                    errors.append(f'[lab] คำสั่งอ้าง deployment: {line}')
    # 6) รายละเอียดเครื่องทดสอบ / credential
    for pat in [r'\b2224\b', r'172\.18\.0\.1', r'askpass', r'\b1300\d\b', r'\b3009[0-2]\b', r'svc006lab', r'WSL', r'32 CPU', r'deep_vision', r'sk-[A-Za-z0-9]', r'ghp_']:
        for m in re.finditer(pat, text):
            errors.append(f'[{name}] พบรายละเอียดต้องห้าม {pat!r}: ...{text[max(0,m.start()-40):m.end()+20]!r}')
    # 7) path ของไฟล์ LAB ที่อ้างถึงมีจริง
    for p in set(re.findall(r'(?<![\w/])((?:labs|k8s)/[\w./-]+\.yaml)', text)):
        cands = [f'{CH}/02_LAB/{p}', f'{CH}/02_LAB/som-shop-v2/{p}']
        if not any(os.path.exists(c) for c in cands):
            errors.append(f'[{name}] อ้างไฟล์ที่ไม่มี: {p}')
    # 8) YAML ที่ขึ้นต้นด้วยคอมเมนต์ "# LAB" ต้องตรงกับไฟล์จริงทุกบรรทัด (ยกเว้นตัดเป็นส่วน)
    labfiles = {f: open(f, encoding='utf-8').read() for f in glob.glob(f'{CH}/02_LAB/**/*.yaml', recursive=True)}
    alltext = '\n'.join(labfiles.values())
    for i, b in enumerate(blocks):
        missing = [l for l in b.splitlines() if l.strip() and l.strip() not in alltext and not l.strip().startswith('---')]
        if b.lstrip().startswith('# LAB') and missing:
            notes.append(f'[{name}] YAML block {i+1} มีบรรทัดไม่อยู่ในไฟล์จริง: {missing[:3]}')
    notes.append(f'[{name}] {len(text.encode())} bytes, ภาพ fig {nfig} (screenshot {len(ss)}), YAML {len(blocks)} block')

print('\n'.join(notes))
print(f'ภาพที่ชื่อตรง images.json แต่ยังไม่มีไฟล์ (กำลังสร้าง): {pending} จุดอ้างอิง')
print('ERRORS:' if errors else 'ผ่านทุกข้อ', len(errors))
print('\n'.join(errors))
