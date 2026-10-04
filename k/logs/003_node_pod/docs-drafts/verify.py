import re,os,json,unicodedata,sys
import yaml
root='/root/workspace/DevTools/k/003_kubernetes_node_pod'
imgs=json.load(open('/root/workspace/DevTools/k/logs/003_node_pod/images.json'))
pending={os.path.normpath(x['path']) for x in imgs if not os.path.exists(x['path'])}
cap={os.path.normpath(x['path']):x['caption_th'] for x in imgs}
docs=['README.md','01_Theory/README.md','02_LAB/README.md']
def slug(h):
    h=h.strip().lower()
    out=''.join(c for c in h if unicodedata.category(c)[0] in 'LMN' or c in ' -_')
    return out.replace(' ','-')
errors=0; used=set()
for doc in docs:
    p=os.path.join(root,doc); s=open(p).read(); d=os.path.dirname(p)
    # strip code blocks for heading/link parsing
    out=[];inc=False
    for ln in s.splitlines():
        if re.match(r'^(> )?\s*```',ln): inc=not inc; continue
        if not inc: out.append(ln)
    nocode='\n'.join(out)
    heads=[slug(re.sub(r'`','',m)) for m in re.findall(r'^#{1,6} (.+)$',nocode,flags=re.M)]
    ids=set(re.findall(r'id="([^"]+)"',s))
    targets=set(heads)|ids
    dup=[i for i in ids if s.count(f'id="{i}"')>1]
    if dup: print(doc,'DUP ids',dup); errors+=1
    links=re.findall(r'(?:src|href)="([^"]+)"',nocode)+re.findall(r'\]\(([^)\s]+)\)',nocode)
    nimg=0
    for l in links:
        if l.startswith('http'): continue
        if l.startswith('#'):
            if l[1:] not in targets: print(doc,'BAD ANCHOR',l); errors+=1
            continue
        f=os.path.normpath(os.path.join(d,l.split('#')[0]))
        if f.endswith('.png'): used.add(f); nimg+=1
        if not os.path.exists(f):
            if f in pending: continue
            print(doc,'MISSING',l); errors+=1
    # caption check for figure blocks
    for src,em in re.findall(r'<img src="([^"]+)"[^>]*><br>\s*<em>(.*?)</em>',s,flags=re.S):
        f=os.path.normpath(os.path.join(d,src))
        if f in cap:
            c=re.sub(r'<b>รูปที่ \d+</b> ','',em)
            if c!=cap[f]: print(doc,'CAPTION DIFF',src,'\n  ',c,'\n  ',cap[f]); errors+=1
    # fig numbering sequential
    figs=[int(x) for x in re.findall(r'id="fig-(\d+)"',s)]
    if figs!=list(range(1,len(figs)+1)): print(doc,'FIG ORDER',figs); errors+=1
    nums=[int(x) for x in re.findall(r'<b>รูปที่ (\d+)</b>',s)]
    if nums!=figs: print(doc,'FIG NUM MISMATCH'); errors+=1
    # yaml blocks
    ny=0
    for b in re.findall(r'^```yaml\n(.*?)^```',s,flags=re.S|re.M):
        ny+=1
        try: list(yaml.safe_load_all(b))
        except Exception as e: print(doc,'YAML ERR',e,b[:80]); errors+=1
    print(f'{doc}: {len(s.encode())} bytes, figs={len(figs)}, png refs={nimg}, yaml blocks={ny}, anchors={sum(1 for l in links if l.startswith("#"))}')
for x in imgs:
    if os.path.normpath(x['path']) not in used: print('UNUSED',x['id']); errors+=1
# T/L order in docs
for doc,k in [('01_Theory/README.md','T'),('02_LAB/README.md','L')]:
    s=open(os.path.join(root,doc)).read()
    order=[x['id'] for x in imgs if x['id'].startswith(k)]
    pos=[s.find(os.path.basename(x['path'])) for x in imgs if x['id'].startswith(k)]
    if pos!=sorted(pos): print(doc,'IMAGE ORDER not sequential'); errors+=1
# forbidden words in LAB
s=open(os.path.join(root,'02_LAB/README.md')).read()
sec='';allowed=('### 10.12','> **บทถัดไป')
for line in s.splitlines():
    if line.startswith('#'): sec=line
    if re.search(r'NodePort|Service|Deployment',line):
        ok=sec.startswith('### 10.12') or line.startswith('> **บทถัดไป')
        print(('ALLOWED' if ok else 'FORBIDDEN'),'|',sec[:40],'|',line[:110])
        if not ok: errors+=1
print('pending (still generating):',sorted(os.path.basename(p) for p in pending))
print('ERRORS',errors)
