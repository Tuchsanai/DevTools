import json, os, re, sys, unicodedata
import yaml

BASE = '/root/workspace/DevTools/k/004_kubernetes_namespace/'
D = json.load(open('/root/workspace/DevTools/k/logs/004_namespace/images.json'))
pending = {os.path.realpath(x['path']) for x in D}
files = [BASE + 'README.md', BASE + '01_Theory/README.md', BASE + '02_LAB/README.md']
errors = []


def slug(h):
    h = re.sub(r'<[^>]+>', '', h).strip().lower()
    out = []
    for ch in h:
        cat = unicodedata.category(ch)
        if ch in '-_' or ch == ' ':
            out.append('-' if ch == ' ' else ch)
        elif cat[0] in 'LMN':
            out.append(ch)
    return ''.join(out)


def strip_code(text):
    return re.sub(r'^```.*?^```', '', text, flags=re.S | re.M)


for f in files:
    text = open(f).read()
    d = os.path.dirname(f)
    nocode = strip_code(text)
    # anchors
    anchors = set()
    seen = {}
    for m in re.finditer(r'^#{1,6} (.+)$', nocode, re.M):
        s = slug(m.group(1).replace('`', ''))
        if s in seen:
            seen[s] += 1; s = f'{s}-{seen[s]}'
        else:
            seen[s] = 0
        anchors.add(s)
    anchors |= set(re.findall(r'id="([^"]+)"', text))
    # links and images
    targets = re.findall(r'\]\(([^)\s]+)\)', nocode) + re.findall(r'<img src="([^"]+)"', text)
    nimg = nlink = 0
    for t in targets:
        if t.startswith('http'):
            continue
        path, _, frag = t.partition('#')
        if path:
            full = os.path.realpath(os.path.join(d, path))
            if not os.path.exists(full):
                if full in pending:
                    pass  # image still being generated, name matches images.json
                else:
                    errors.append(f'{f}: missing target {t}')
            nlink += 1
        if frag and not path:
            if frag not in anchors:
                errors.append(f'{f}: missing anchor #{frag}')
        elif frag and path:
            other = open(os.path.realpath(os.path.join(d, path))).read()
            if f'id="{frag}"' not in other and frag not in {slug(h) for h in re.findall(r'^#{1,6} (.+)$', strip_code(other), re.M)}:
                errors.append(f'{f}: missing anchor {t}')
    # yaml blocks
    for i, b in enumerate(re.findall(r'^```yaml\n(.*?)^```', text, re.S | re.M)):
        try:
            list(yaml.safe_load_all(b))
        except Exception as e:
            errors.append(f'{f}: yaml block {i} parse error: {e}')
    # forbidden test-machine details / secrets
    for bad in ['2224', '172.18.0.1', 'askpass', 'ASKPASS', 'agent']:
        if bad in text:
            errors.append(f'{f}: contains forbidden "{bad}"')
    if re.search(r'eyJ[A-Za-z0-9_-]{20,}', text):
        errors.append(f'{f}: contains full token')
    print(f'{os.path.relpath(f, BASE)}: {len(text.encode())} bytes, {len(re.findall(r"<img ", text))} <img>, {len(targets)} links/imgs checked, {len(anchors)} anchors')

# figure usage + captions
for fname, prefix, n in [(BASE + '01_Theory/README.md', 'T', 38), (BASE + '02_LAB/README.md', 'L', 23)]:
    text = open(fname).read()
    imgs = re.findall(r'<p align="center" id="fig-(\d+)">\s*<img src="([^"]+)"[^>]*><br>\s*<em><b>รูปที่ (\d+)</b> (.*?)</em>', text)
    nums = [int(a) for a, *_ in imgs]
    if nums != list(range(1, len(nums) + 1)):
        errors.append(f'{fname}: figure numbering not sequential')
    for a, src, b, cap in imgs:
        if a != b:
            errors.append(f'{fname}: fig id {a} != label {b}')
    used = []
    for x in D:
        if not x['id'].startswith(prefix):
            continue
        base = os.path.basename(x['path'])
        hits = [(src, cap) for _, src, _, cap in imgs if os.path.basename(src) == base]
        if len(hits) != 1:
            errors.append(f'{fname}: {x["id"]} used {len(hits)} times')
            continue
        if hits[0][1] != x['caption_th']:
            errors.append(f'{fname}: {x["id"]} caption mismatch')
        used.append(x['id'])
    order = [os.path.basename(s) for _, s, _, _ in imgs]
    ids = [x['id'] for x in D if x['id'].startswith(prefix)]
    seq = [i for i in ids if os.path.basename(BYID['path']) in order] if False else None
    idx = [order.index(os.path.basename(x['path'])) for x in D if x['id'].startswith(prefix) and os.path.basename(x['path']) in order]
    if idx != sorted(idx):
        errors.append(f'{fname}: images not in images.json order')
    ss = [s for s in order if s.startswith('20261004')]
    print(f'{os.path.relpath(fname, BASE)}: {prefix}01–{prefix}{n:02d} used {len(used)}/{n}, total figures {len(imgs)} (screenshots {len(ss)})')

# LAB steps: no Service/NodePort/Deployment (except the "ปูทางบทหน้า" note)
lab = open(BASE + '02_LAB/README.md').read()
lab_wo = re.sub(r'^> \*\*ปูทางบทหน้า:\*\*.*$', '', lab, flags=re.M)
lab_wo2 = lab_wo.replace('["Ingress"]', '').replace('Policy Types: Ingress', '')
for w in ['NodePort', 'Deployment', 'ReplicaSet', 'DaemonSet', 'Ingress']:
    for m in re.finditer(r'\b' + w + r'\b', lab_wo2):
        errors.append(f'LAB: forbidden word {w} at {lab_wo[max(0,m.start()-60):m.end()+20]!r}')
for m in re.finditer(r'\bServices?\b|\bkind: Service\b|\bsvc/', lab_wo):
    ctx = lab_wo[max(0, m.start() - 80):m.end() + 20]
    errors.append(f'LAB: Service mention {ctx!r}')
print('ปูทาง notes in LAB:', len(re.findall(r'^> \*\*ปูทางบทหน้า:\*\*', lab, re.M)))

missing_now = [os.path.basename(x['path']) for x in D if not os.path.exists(x['path'])]
print('images not yet generated (name matches images.json):', len(missing_now))
print('ERRORS:', len(errors))
for e in errors:
    print(' -', e)
