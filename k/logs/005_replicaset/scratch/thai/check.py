import json,re,sys
ch=sys.argv[1]
items=json.load(open(f'{ch}-items.json')); P=json.load(open(f'{ch}-patch.json'))
TH=re.compile('[฀-๿]'); bad=0
assert set(P)=={x['id'] for x in items}, set(x['id'] for x in items)^set(P)
for x in items:
    p=P[x['id']]; L=p['labels']
    errs=[]
    if not 1<=len(L)<=7: errs.append(f'count {len(L)}')
    if any(not l.strip() or '"' in l for l in L): errs.append('empty/quote')
    if not any(TH.search(l) for l in L): errs.append('no thai')
    for q in re.findall(r"'([^']+)'",p['extra']):
        if q not in L and TH.search(q): errs.append(f'extra refs unknown {q!r}')
    for l in L:
        if l not in p['extra'] and len(L)>1: errs.append(f'label not placed in extra: {l!r}')
    long=[l for l in L if TH.search(l) and len(l)>24]
    if long: print('  note long:',x['id'],long)
    if errs: bad+=1; print(x['id'],errs)
print(ch,'items',len(items),'bad',bad)
