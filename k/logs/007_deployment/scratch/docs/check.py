#!/usr/bin/env python3
"""ตรวจเอกสารบท 007: ลิงก์/ภาพ, anchor, ภาพ T/L ครบและเรียงลำดับ, caption ตรง images.json,
YAML parse ได้, คำสั่งอ้างไฟล์/namespace/deployment/container ที่มีจริง, คำต้องห้าม"""
import glob, html, json, os, re, sys, unicodedata
import yaml

ROOT = '/root/workspace/DevTools/k'
CH = f'{ROOT}/007_kubernetes_deployment'
DOCS = {'index': f'{CH}/README.md', 'theory': f'{CH}/01_Theory/README.md', 'lab': f'{CH}/02_LAB/README.md'}
IMGS = json.load(open(f'{ROOT}/logs/007_deployment/images.json', encoding='utf-8'))
BYPATH = {x['path']: x for x in IMGS}
errors, notes = [], []


def err(doc, msg):
    errors.append(f'[{doc}] {msg}')


def slug(h):
    # GitHub-style: lowercase, ลบอักขระที่ไม่ใช่ตัวอักษร/ตัวเลข/ขีด/ช่องว่าง/_ (คงตัวอักษรไทยและเครื่องหมายกำกับ)
    h = re.sub(r'<[^>]+>', '', h).strip().lower()
    h = re.sub(r'`', '', h)
    out = []
    for ch in h:
        cat = unicodedata.category(ch)
        if ch in '-_ ' or cat[0] in 'LNM':
            out.append(ch)
    return ''.join(out).replace(' ', '-')


# ---------- YAML ของ LAB (ชื่อจริง) ----------
names = {'ns': {'som-shop', 'kube-system', 'default'}, 'deploy': {}, 'files': set()}
for f in glob.glob(f'{CH}/02_LAB/**/*.yaml', recursive=True):
    if '/app/' in f:
        continue
    for d in yaml.safe_load_all(open(f, encoding='utf-8')):
        if not isinstance(d, dict) or 'kind' not in d:
            continue
        md = d.get('metadata', {})
        if d['kind'] == 'Namespace':
            names['ns'].add(md['name'])
        if d['kind'] == 'Deployment':
            spec = d['spec']['template']['spec']
            cs = {c['name'] for c in spec.get('containers', [])} | {c['name'] for c in spec.get('initContainers', [])}
            names['deploy'].setdefault(md['name'], set()).update(cs)
names['deploy'].setdefault('zero', {'web'})

SEARCH_DIRS = [f'{CH}/02_LAB/labs', f'{CH}/02_LAB/som-shop-v3', f'{CH}/02_LAB', CH]

for key, path in DOCS.items():
    text = open(path, encoding='utf-8').read()
    base = os.path.dirname(path)
    # ---- คำต้องห้าม ----
    for bad in ['2224', '172.18.0.1', 'askpass', '30090', '1300', 'deploy007lab', '/root/count', 'round10', 'round.sh', 'som-booths']:
        if bad in text:
            err(key, f'พบคำต้องห้าม {bad!r}')
    # ---- ลิงก์และภาพ ----
    targets = re.findall(r'<img src="([^"]+)"', text) + re.findall(r'\]\(([^)\s]+)\)', text)
    for t in targets:
        if t.startswith(('http://', 'https://', '#', 'mailto:')):
            continue
        p = os.path.normpath(os.path.join(base, t.split('#')[0]))
        if os.path.exists(p):
            continue
        if p in BYPATH:
            notes.append(f'[{key}] ภาพกำลังสร้าง (ชื่อตรง images.json): {os.path.relpath(p, CH)}')
            continue
        err(key, f'ลิงก์/ภาพไม่มีไฟล์: {t}')
    # ---- anchor ----
    heads = set()
    seen = {}
    for m in re.finditer(r'^(#{1,6})\s+(.*)$', text, re.M):
        s = slug(m.group(2))
        n = seen.get(s, 0)
        heads.add(s if n == 0 else f'{s}-{n}')
        seen[s] = n + 1
    heads |= set(re.findall(r'id="([^"]+)"', text))
    for a in re.findall(r'\]\(#([^)]+)\)', text):
        if a not in heads:
            err(key, f'anchor ไม่มีปลายทาง: #{a}')
    # ---- caption ----
    used = []
    for m in re.finditer(r'<img src="([^"]+)"[^>]*><br>\s*<em>(.*?)</em>', text, re.S):
        p = os.path.normpath(os.path.join(base, m.group(1)))
        cap = re.sub(r'^<b>รูปที่ \d+</b>\s*', '', m.group(2).strip())
        cap = html.unescape(cap)
        if p in BYPATH:
            used.append(BYPATH[p]['id'])
            if cap != BYPATH[p]['caption_th']:
                err(key, f'caption ไม่ตรง {BYPATH[p]["id"]}: {cap[:60]}...')
    if key == 'theory':
        want = [f'T{i:02d}' for i in range(1, 37)]
        if used != want:
            err(key, f'ลำดับ/จำนวนภาพ T ไม่ครบ: {used}')
    if key == 'lab':
        want = [f'L{i:02d}' for i in range(1, 24)]
        if used != want:
            err(key, f'ลำดับ/จำนวนภาพ L ไม่ครบ: {used}')
    # เลขรูปเรียงต่อกันและ fig-N มีครบ
    nums = [int(x) for x in re.findall(r'id="fig-(\d+)"', text)]
    if nums != list(range(1, len(nums) + 1)):
        err(key, f'เลข fig ไม่เรียง: {nums}')
    # ---- YAML ----
    for i, blk in enumerate(re.findall(r'```yaml\n(.*?)```', text, re.S)):
        try:
            list(yaml.safe_load_all(blk))
        except Exception as e:
            err(key, f'YAML block {i} parse ไม่ได้: {e}')
    # ---- คำสั่ง ----
    blocks = re.findall(r'```bash\n(.*?)```', text, re.S)
    inline = re.findall(r'`([^`\n]*kubectl [^`\n]*)`', text)
    for cmd in blocks + inline:
        for f in re.findall(r'(?:-f|--patch-file)\s+([\w./-]+\.yaml|[\w./-]+/)', cmd):
            if f.startswith('/workspace/examples'):
                continue
            if not any(os.path.exists(os.path.join(d, f)) for d in SEARCH_DIRS):
                err(key, f'ไฟล์ในคำสั่งไม่มีจริง: {f}')
        for f in re.findall(r'(?:\bcat|\bdiff)\s+([\w./-]+\.yaml)(?:\s+([\w./-]+\.yaml))?', cmd):
            for x in f:
                if x and not any(os.path.exists(os.path.join(d, x)) for d in SEARCH_DIRS):
                    err(key, f'ไฟล์ cat/diff ไม่มีจริง: {x}')
        for ns in re.findall(r'kubectl -n ([\w-]+)', cmd):
            if ns not in names['ns'] and ns not in ('<ns>',):
                err(key, f'namespace ไม่มีใน YAML: {ns}')
        for d in re.findall(r'deploy(?:/|ment\s+|\s+)([a-z][\w-]*)', '\n'.join(l for l in cmd.splitlines() if 'kubectl' in l)):
            if d in ('web', 'som-web', 'som-db') or d in names['deploy']:
                continue
            if d in ('rolling', 'nosurge', 'recreate', 'web-blue', 'web-green', 'web-stable', 'web-canary'):
                continue
            if d.startswith('lab') or d in ('-f',):
                continue
            err(key, f'deployment ไม่มีใน YAML: {d}  ← {cmd.strip()[:80]}')
        for dep, pairs in re.findall(r'set image deploy/([\w-]+)((?:\s+[\w-]+=[\w.:/-]+)+)', cmd):
            for c in re.findall(r'([\w-]+)=', pairs):
                if c not in names['deploy'].get(dep, set()):
                    err(key, f'container {c} ไม่มีใน deploy/{dep}')
        for s in re.findall(r'(?:hit\.sh|\.\./som-shop-v3/hit\.sh)', cmd):
            pass
    if '../som-shop-v3/hit.sh' in text and not os.path.exists(f'{CH}/02_LAB/som-shop-v3/hit.sh'):
        err(key, 'hit.sh ไม่มี')

print('NOTES (ภาพที่ยังไม่มีไฟล์แต่ชื่อตรง images.json):', len(set(notes)))
for k, p in DOCS.items():
    t = open(p, encoding='utf-8').read()
    print(f'{k}: {len(t.encode())} bytes, figures={len(re.findall(chr(60)+"img ", t))}')
if errors:
    print(f'ERRORS: {len(errors)}')
    for e in errors:
        print(' -', e)
    sys.exit(1)
print('ALL CHECKS PASSED')
