#!/usr/bin/env python3
"""ตรวจเอกสารบท 014: ลิงก์/ภาพ, anchor, ภาพ T/L ครบตามลำดับ + caption, YAML/JSON parse, ไฟล์ที่คำสั่งอ้าง, คำต้องห้าม"""
import html, json, os, re, sys, unicodedata
import yaml

ROOT = '/root/workspace/DevTools/k'
CH = os.path.join(ROOT, '014_kubernetes_helm')
DOCS = {
    'top': os.path.join(CH, 'README.md'),
    'theory': os.path.join(CH, '01_Theory/README.md'),
    'lab': os.path.join(CH, '02_LAB/README.md'),
}
IMAGES = json.load(open(os.path.join(ROOT, 'logs/014_helm/images.json')))
pending = {os.path.normpath(x['path']) for x in IMAGES}
errors, notes = [], []


def slug(h):
    h = h.strip().lower()
    out = []
    for ch in h:
        cat = unicodedata.category(ch)
        if ch in ' -_' or cat[0] in 'LMN':
            out.append('-' if ch == ' ' else ch)
    return ''.join(out)


def anchors_of(path):
    t = open(path).read()
    t_nocode = re.sub(r'^```.*?^```[ \t]*$', '', t, flags=re.S | re.M)
    seen, res = {}, set()
    for m in re.finditer(r'^(#{1,6})\s+(.*)$', t_nocode, re.M):
        s = slug(re.sub(r'[`*]', '', m.group(2)))
        n = seen.get(s, 0)
        res.add(s if n == 0 else f'{s}-{n}')
        seen[s] = n + 1
    res |= set(re.findall(r'id="([^"]+)"', t))
    return res


anchor_cache = {}
for name, path in DOCS.items():
    text = open(path).read()
    base = os.path.dirname(path)
    text_nocode = re.sub(r'^```.*?^```[ \t]*$', '', text, flags=re.S | re.M)
    # 1) img src + markdown links
    targets = re.findall(r'<img src="([^"]+)"', text) + re.findall(r'\]\(([^)\s]+)\)', text_nocode)
    for tgt in targets:
        if tgt.startswith(('http://', 'https://', 'mailto:')):
            continue
        file_part, _, frag = tgt.partition('#')
        full = os.path.normpath(os.path.join(base, file_part)) if file_part else path
        if file_part and not os.path.exists(full):
            if full in pending:
                notes.append(f'{name}: ภาพที่กำลังสร้าง (ชื่อตรง images.json): {os.path.relpath(full, CH)}')
            else:
                errors.append(f'{name}: ไม่พบไฟล์ {tgt}')
            continue
        if frag:
            if full.endswith('.md'):
                anchor_cache.setdefault(full, anchors_of(full))
                if frag not in anchor_cache[full]:
                    errors.append(f'{name}: anchor ไม่มีปลายทาง {tgt}')
    # 4) YAML/JSON blocks
    for m in re.finditer(r'^```(yaml|json)\n(.*?)^```', text, flags=re.S | re.M):
        lang, body = m.group(1), m.group(2)
        try:
            if lang == 'yaml':
                list(yaml.safe_load_all(body))
            else:
                json.loads(body)
        except Exception as e:
            errors.append(f'{name}: {lang} block parse ไม่ได้ (บรรทัด {text[:m.start()].count(chr(10))+1}): {str(e)[:80]}')
    # template syntax ใน yaml block = ผิด
    for m in re.finditer(r'^```yaml\n(.*?)^```', text, flags=re.S | re.M):
        if '{{' in m.group(1):
            errors.append(f'{name}: yaml block มี {{{{ }}}} (ควรเป็น gotemplate)')
    # 6) คำต้องห้าม
    for bad in ['2224', '2225', '172.18.0.1', 'askpass', 'helm014', '0044d7', 'LS0tLS1CRUdJTiBQUklW', 'deep_vision']:
        if bad in text:
            errors.append(f'{name}: พบคำต้องห้าม {bad}')
    for m in re.finditer(r'\b(1300\d|3009\d|3010\d)\b', text):
        errors.append(f'{name}: พบพอร์ตเครื่องทดสอบ {m.group(0)}')

# 3) T/L ครบ ตามลำดับ + caption
def check_series(doc, prefix):
    path = DOCS[doc]
    text = open(path).read()
    base = os.path.dirname(path)
    items = [x for x in IMAGES if x['id'].startswith(prefix)]
    figs = [(m.start(), os.path.normpath(os.path.join(base, m.group(1))), html.unescape(m.group(2)))
            for m in re.finditer(r'<img src="([^"]+)"[^>]*><br>\s*<em>(.*?)</em>', text, re.S)]
    order = []
    for x in items:
        p = os.path.normpath(x['path'])
        hit = [f for f in figs if f[1] == p]
        if not hit:
            errors.append(f'{doc}: ไม่ได้ใช้ภาพ {x["id"]} {os.path.basename(p)}')
            continue
        if len(hit) > 1:
            errors.append(f'{doc}: ใช้ภาพ {x["id"]} ซ้ำ')
        pos, _, cap = hit[0]
        order.append((pos, x['id']))
        cap_plain = re.sub(r'<[^>]+>', '', cap)
        if x['caption_th'] not in cap_plain:
            errors.append(f'{doc}: caption ไม่ตรง {x["id"]}')
    if [i for _, i in sorted(order)] != [i for _, i in order]:
        errors.append(f'{doc}: ลำดับภาพ {prefix} ไม่ตรง images.json')
    return len(order)

nT = check_series('theory', 'T')
nL = check_series('lab', 'L')
# รูปที่ N ต่อเนื่อง และ fig-N ตรงกับเลข
for doc in ('theory', 'lab'):
    text = open(DOCS[doc]).read()
    nums = [(int(a), int(b)) for a, b in re.findall(r'id="fig-(\d+)">\s*<img[^>]*><br>\s*<em><b>รูปที่ (\d+)</b>', text)]
    if any(a != b for a, b in nums) or [a for a, _ in nums] != list(range(1, len(nums) + 1)):
        errors.append(f'{doc}: เลขรูป/ fig id ไม่ต่อเนื่อง')
    notes.append(f'{doc}: รูปที่มีเลข {len(nums)} ภาพ')

# 5) ไฟล์ที่คำสั่งอ้าง (บล็อก bash ใน LAB) — path สัมพัทธ์ตาม cd ล่าสุด
LAB = os.path.join(CH, '02_LAB')
created = re.compile(r'(mychart|broken-|/traefik(/|$)|auth|pulled|som-shop-0\.1\.0\.tgz|Chart\.lock|harbor-addons/charts|/root/)')
lab_text = open(DOCS['lab']).read()
cwd = LAB
checked = 0
for m in re.finditer(r'^```bash\n(.*?)^```', lab_text, re.S | re.M):
    for line in m.group(1).splitlines():
        line = line.split(' #')[0]
        cd = re.match(r'\s*cd\s+(\S+)', line)
        if cd:
            d = cd.group(1).replace('/workspace/014_kubernetes_helm', CH)
            cwd = os.path.normpath(d if d.startswith('/') else os.path.join(cwd, d))
            continue
        for tok in re.findall(r'(?<![\w/.:-])((?:\.\./|\./)?(?:charts|labs|som-shop-v10|hit\.sh|static-old|harbor-addons|make-broken\.sh|\.\./lab05-first)[\w./-]*)', line):
            if created.search(tok) or '$' in tok:
                continue
            full = os.path.normpath(os.path.join(cwd, tok))
            checked += 1
            if not os.path.exists(full):
                errors.append(f'lab: คำสั่งอ้างไฟล์ที่ไม่มี {tok} (cwd={os.path.relpath(cwd, CH)})')

print(f'ภาพ T ใช้ {nT}/52, ภาพ L ใช้ {nL}/34, path ในคำสั่งที่ตรวจ {checked}')
for n in sorted(set(notes)):
    print('NOTE', n)
for e in errors:
    print('ERROR', e)
print('ผล:', 'ผ่าน' if not errors else f'{len(errors)} ปัญหา')
sys.exit(1 if errors else 0)
