#!/usr/bin/env python3
"""ตรวจเอกสารบท 008: ลิงก์/ภาพ, anchor, ภาพ T/L ครบและเรียงลำดับ, caption ตรง images.json,
YAML parse ได้, ไฟล์ที่อ้างในคำสั่งมีจริง, ไม่มีรายละเอียดเครื่องทดสอบ"""
import html, json, os, re, sys, unicodedata
import yaml

ROOT = '/root/workspace/DevTools/k'
CH = os.path.join(ROOT, '008_kubernetes_pv_pvc')
DOCS = {
    'index': os.path.join(CH, 'README.md'),
    'theory': os.path.join(CH, '01_Theory/README.md'),
    'lab': os.path.join(CH, '02_LAB/README.md'),
}
IMAGES = json.load(open(os.path.join(ROOT, 'logs/008_pv_pvc/images.json')))
PENDING = {os.path.normpath(i['path']) for i in IMAGES}
CAP = {os.path.normpath(i['path']): i for i in IMAGES}
FORBIDDEN = [r'\b2224\b', r'172\.18\.0\.1', r'askpass', r'\b1300\d\b', r'\b3009\d\b']

FENCE = re.compile(r'^(?:> )?```[^\n`]*\n.*?^(?:> )?```[ \t]*$', re.M | re.S)
errors = []
def err(doc, msg):
    errors.append(f'[{doc}] {msg}')

def slug(text):
    t = re.sub(r'<[^>]+>', '', text).strip().lower()
    t = re.sub(r'`', '', t)
    out = []
    for ch in t:
        cat = unicodedata.category(ch)
        if ch in ' -_' or cat[0] in 'LMN':
            out.append('-' if ch == ' ' else ch)
    return ''.join(out)

def anchors_of(path):
    s = open(path).read()
    s_nocode = FENCE.sub('', s)
    res, seen = set(), {}
    for m in re.finditer(r'^#{1,6}\s+(.*)$', s_nocode, re.M):
        a = slug(m.group(1))
        n = seen.get(a, 0); seen[a] = n + 1
        res.add(a if n == 0 else f'{a}-{n}')
    res |= set(re.findall(r'id="([^"]+)"', s))
    return res

stats = {}
for name, path in DOCS.items():
    if not os.path.exists(path):
        err(name, 'ไม่มีไฟล์'); continue
    s = open(path).read()
    base = os.path.dirname(path)
    noc = FENCE.sub('', s)
    noc = re.sub(r'````.*?````', '', noc)
    noc = re.sub(r'`[^`\n]*`', '', noc)
    # forbidden
    for pat in FORBIDDEN:
        for m in re.finditer(pat, s):
            err(name, f'พบข้อความต้องห้าม {m.group(0)!r} ที่ตำแหน่ง {m.start()}')
    # links + images
    targets = re.findall(r'\]\(([^)\s]+)\)', noc) + re.findall(r'src="([^"]+)"', noc)
    pend = 0
    for t in targets:
        if re.match(r'https?://', t):
            continue
        file_part, _, frag = t.partition('#')
        fp = os.path.normpath(os.path.join(base, file_part)) if file_part else path
        if not os.path.exists(fp):
            if fp in PENDING:
                pend += 1
            else:
                err(name, f'ลิงก์/ภาพชี้ไฟล์ที่ไม่มี: {t}')
            continue
        if frag:
            if not fp.endswith('.md'):
                continue
            if frag not in anchors_of(fp):
                err(name, f'anchor ไม่มีปลายทาง: {t}')
    # figures + captions
    figs = re.findall(r'<p align="center" id="fig-(\d+)">\s*<img src="([^"]+)" alt="([^"]*)"[^>]*><br>\s*<em><b>รูปที่ (\d+)</b> (.*?)</em>', s, re.S)
    used = []
    for num, src, alt, num2, cap in figs:
        if num != num2:
            err(name, f'id fig-{num} ไม่ตรงกับ "รูปที่ {num2}"')
        if not alt.startswith(f'รูปที่ {num} '):
            err(name, f'alt ของ fig-{num} ไม่ขึ้นต้นด้วย "รูปที่ {num}"')
        fp = os.path.normpath(os.path.join(base, src))
        if fp in CAP:
            used.append(CAP[fp]['id'])
            if html.unescape(cap).strip() != CAP[fp]['caption_th']:
                err(name, f'caption ไม่ตรง fig-{num} ({CAP[fp]["id"]})\n   doc: {html.unescape(cap)}\n   json: {CAP[fp]["caption_th"]}')
    nums = [int(n) for n, *_ in figs]
    if nums != list(range(1, len(nums) + 1)):
        err(name, f'เลขรูปไม่ต่อเนื่อง: {nums}')
    # toc of figures: every fig-N id referenced
    for n in nums:
        if f'(#fig-{n})' not in s:
            err(name, f'สารบัญรูปภาพไม่มี fig-{n}')
    prefix = {'theory': 'T', 'lab': 'L'}.get(name)
    if prefix:
        want = [i['id'] for i in IMAGES if i['id'].startswith(prefix)]
        got = [u for u in used if u.startswith(prefix)]
        if got != want:
            err(name, f'ลำดับ/ความครบของภาพ {prefix} ไม่ตรง\n   missing={sorted(set(want)-set(got))} extra={[g for g in got if g not in want]} order_ok={sorted(got)==got}')
    # yaml blocks
    nyaml = 0
    for m in re.finditer(r'```yaml\n(.*?)```', s, re.S):
        nyaml += 1
        try:
            list(yaml.safe_load_all(m.group(1)))
        except Exception as e:
            err(name, f'YAML parse ไม่ผ่าน (บรรทัด ~{s[:m.start()].count(chr(10))+1}): {str(e).splitlines()[0]}')
    stats[name] = dict(size=len(s.encode()), figs=len(figs), pending=pend, yaml=nyaml)

# รวมชื่อ object จาก YAML จริงทั้งหมดของบท
NAMES = {'pod': set(), 'deploy': set(), 'pvc': set()}
for dp, _, fs in os.walk(os.path.join(CH, '02_LAB')):
    for f in fs:
        if f.endswith('.yaml') and 'node_modules' not in dp:
            for d in yaml.safe_load_all(open(os.path.join(dp, f))):
                if not d: continue
                k = {'Pod': 'pod', 'Deployment': 'deploy', 'PersistentVolumeClaim': 'pvc'}.get(d.get('kind'))
                if k: NAMES[k].add(d['metadata']['name'])
                if d.get('kind') == 'Pod':
                    for v in d['spec'].get('volumes', []):
                        if 'ephemeral' in v: NAMES['pvc'].add(f"{d['metadata']['name']}-{v['name']}")
# commands → files (เฉพาะ LAB และ theory)
WS = '/workspace/008_kubernetes_pv_pvc'
for name in [n for n in ("lab", "theory") if os.path.exists(DOCS[n])]:
    s = open(DOCS[name]).read()
    cwd = None
    ncheck = 0
    for m in re.finditer(r'```bash\n(.*?)```', s, re.S):
        for line in m.group(1).splitlines():
            line = line.split(' #')[0]
            for cm in re.finditer(r'(?:^|[;&]\s*)cd\s+(\S+)', line):
                d = cm.group(1)
                if d.startswith(WS):
                    cwd = os.path.join(CH, os.path.relpath(d, WS))
                elif cwd and not d.startswith('/') and not d.startswith('$'):
                    cwd = os.path.normpath(os.path.join(cwd, d))
                if cwd and not os.path.isdir(cwd):
                    err(name, f'cd ไปโฟลเดอร์ที่ไม่มี: {d}')
            for fm in re.finditer(r'(?<!rm )(?:-f|--filename)\s+(\S+)', line):
                f = fm.group(1).rstrip(';')
                if f in ('-',) or '$' in f:
                    continue
                if name == 'theory':
                    continue
                if cwd is None:
                    err(name, f'อ้างไฟล์โดยไม่รู้ cwd: {line.strip()}'); continue
                ncheck += 1
                if not os.path.exists(os.path.join(cwd, f)):
                    err(name, f'ไฟล์ไม่มีจริง (cwd={os.path.relpath(cwd, CH)}): {f}  ← {line.strip()[:90]}')
            for sm in re.finditer(r'sed "[^"]*"\s+(\S+\.yaml)', line):
                ncheck += 1
                if cwd and not os.path.exists(os.path.join(cwd, sm.group(1))):
                    err(name, f'ไฟล์ใน sed ไม่มีจริง: {sm.group(1)}')
            if name == 'lab' and cwd:
                for km in re.finditer(r'\b(pod|deploy|pvc)[/ ]([a-z][a-z0-9-]+)', line):
                    kind, obj = km.groups()
                    if obj in ('-l', 'som', 'ledger-pod') and kind!='pod':
                        pass
                    names = NAMES.get(kind, set())
                    if obj in names or obj.startswith('-'):
                        continue
                    if kind == 'pvc' and obj in ('notes','ledger','kept','std','ex','imm','rwo-data','fsg-e','fsg-data','som-db-data','nd-data','manual-claim','too-big'):
                        err(name, f'ชื่อ PVC {obj} ไม่มีใน YAML')
                    elif kind in ('pod','deploy'):
                        err(name, f'ชื่อ {kind}/{obj} ไม่มีใน YAML ← {line.strip()[:80]}')
    stats[name]['filerefs'] = ncheck

for e in errors:
    print('✗', e)
for k, v in stats.items():
    print(k, v)
print('ERRORS:', len(errors))
sys.exit(1 if errors else 0)
