import re, os, json, html, glob, yaml
R = '/root/workspace/DevTools/k'
D = R + '/009_kubernetes_statefulset'
LOGS = sorted(glob.glob(R + '/logs/009_statefulset/lab-run/*.log'))
ansi = re.compile(r'\x1b\[[0-9;]*[A-Za-z]|\[\d+(;\d+)*m|\[J')
norm = lambda x: ' '.join(ansi.sub('', x).replace('\r', '').split())
logtxt = '\n'.join(open(f, errors='ignore').read() for f in LOGS)
loglines = set(norm(l) for l in logtxt.split('\n'))
logcmds = set(norm(l[2:]) for l in logtxt.split('\n') if l.startswith('$ '))
imgs = json.load(open(R + '/logs/009_statefulset/images.json'))
docs = {'README.md': D + '/README.md', 'T': D + '/01_Theory/README.md', 'L': D + '/02_LAB/README.md'}
problems = []

# 1) captions, order, fig ids
for key in ['T', 'L']:
    s = open(docs[key]).read()
    figs = re.findall(r'<p align="center" id="fig-(\d+)">\s*<img src="([^"]+)"[^>]*>\s*<br>\s*<em><b>รูปที่ (\d+)</b> (.*?)</em>', s, re.S)
    nums = [int(a) for a, _, _, _ in figs]
    if nums != list(range(1, len(nums) + 1)): problems.append(f'{key}: fig ids not sequential {nums}')
    for a, src, b, cap in figs:
        if a != b: problems.append(f'{key}: id fig-{a} vs รูปที่ {b}')
    srcmap = {os.path.normpath(os.path.join(os.path.dirname(docs[key]), src)): html.unescape(cap) for _, src, _, cap in figs}
    order = [os.path.normpath(os.path.join(os.path.dirname(docs[key]), src)) for _, src, _, _ in figs]
    mine = [i for i in imgs if i['id'].startswith(key)]
    idx = []
    for i in mine:
        p = os.path.normpath(i['path'])
        if p not in srcmap: problems.append(f'{key}: image {i["id"]} not used as figure'); continue
        if srcmap[p] != i['caption_th']: problems.append(f'{key}: caption mismatch {i["id"]}\n   doc: {srcmap[p]}\n   json:{i["caption_th"]}')
        idx.append(order.index(p))
    if idx != sorted(idx): problems.append(f'{key}: image order differs from images.json')
    print(f'{key}: {len(figs)} figures, {len(mine)} storyboard images')

# 2) YAML parse
for name, p in docs.items():
    s = open(p).read()
    for i, blk in enumerate(re.findall(r'```yaml\n(.*?)```', s, re.S)):
        try: list(yaml.safe_load_all(blk))
        except Exception as e: problems.append(f'{name}: yaml block {i} parse error: {e}')

# 3) text blocks from logs
for name in ['T', 'L']:
    s = open(docs[name]).read()
    miss = []
    for blk in re.findall(r'```text\n(.*?)```', s, re.S):
        if '├──' in blk or '│' in blk: continue
        for l in blk.split('\n'):
            n = norm(l)
            if not n or n == '...' or n.startswith('...'): continue
            if n not in loglines and not any(n in x for x in loglines if len(n) > 25):
                miss.append(l)
    for m in miss: problems.append(f'{name}: text line not in logs: {m!r}')

# 4) commands in bash blocks + file refs
base = D + '/02_LAB'
for name in ['T', 'L', 'README.md']:
    s = open(docs[name]).read()
    cwd = base
    unk = []
    for blk in re.findall(r'```bash\n(.*?)```', s, re.S):
        for l in blk.split('\n'):
            l = l.strip()
            if not l: continue
            m = re.match(r'cd (/workspace/009_kubernetes_statefulset/02_LAB\S*)', l)
            if m: cwd = m.group(1).replace('/workspace/009_kubernetes_statefulset', D)
            for f in re.findall(r'(?:-f|--patch-file)\s+(\S+)', l) + re.findall(r'(?:^|\s)(\.{1,2}/\S+\.sh)', l) + re.findall(r'(migrate/\S+\.yaml)', l):
                f=f.rstrip(';')
                if f in ('-','pg.tar'): continue
                if not os.path.exists(os.path.join(cwd, f)): problems.append(f'{name}: file ref {f} not found from {cwd}')
            if norm(l) not in logcmds: unk.append(l)
    print(f'--- {name}: bash lines not literally in logs ({len(unk)}):')
    for u in unk: print('    ', u)

print('\nPROBLEMS:', len(problems))
for p in problems: print(' -', p)
