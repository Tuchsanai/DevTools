import re, os, json, unicodedata
root='002_kubernetes_pod'
files=[f'{root}/README.md',f'{root}/01_Theory/README.md',f'{root}/02_LAB/README.md']
imgs=json.load(open('logs/002_pod/images.json'))
pending={'T05','T32'}
def slug(h):
    h=h.strip().lower()
    h=re.sub(r'[^\w\- ฀-๿]','',h)  # keep word chars, thai, space, hyphen
    return h.replace(' ','-')
used=set(); ok=True
for f in files:
    s=open(f).read(); d=os.path.dirname(f)
    srcs=re.findall(r'<img[^>]*src="([^"]+)"',s)+re.findall(r'!\[[^\]]*\]\(([^)]+)\)',s)
    for src in srcs:
        p=os.path.normpath(os.path.join(d,src)); used.add(os.path.abspath(p))
        if not os.path.exists(p):
            iid=[x['id'] for x in imgs if os.path.abspath(x['path'])==os.path.abspath(p)]
            if iid and iid[0] in pending: print(f'  [pending ok] {f}: {src} ({iid[0]})')
            else: print(f'  MISSING IMG {f}: {src}'); ok=False
    # md links to files
    for m in re.findall(r'\]\(([^)#\s]+)(?:#[^)]*)?\)',s):
        if m.startswith('http'): continue
        if not os.path.exists(os.path.normpath(os.path.join(d,m))): print(f'  MISSING LINK {f}: {m}'); ok=False
    # anchors
    targets=set(re.findall(r'id="([^"]+)"',s))
    code=False
    for line in s.splitlines():
        if line.startswith('```'): code=not code; continue
        if not code and re.match(r'#{1,6} ',line): targets.add(slug(re.sub(r'^#+ ','',line)).replace('`',''))
    for a in re.findall(r'\]\(#([^)]+)\)',s):
        if a not in targets: print(f'  BROKEN ANCHOR {f}: #{a}'); ok=False
    print(f'{f}: {os.path.getsize(f)} bytes, {len(srcs)} images, {len(re.findall(r"]\(#",s))} anchors checked')
for x in imgs:
    if os.path.abspath(x['path']) not in used: print('  UNUSED', x['id'], x['path']); ok=False
# figure order in theory
t=open(files[1]).read()
order=[int(n) for n in re.findall(r'images/(\d\d)-',t) if n!='00']
print('theory order sequential:', order==sorted(order), 'count', len(order))
print('ALL OK' if ok else 'PROBLEMS')
