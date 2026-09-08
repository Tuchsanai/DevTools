#!/usr/bin/env python3
"""check-lang-diff.py <file>... — verify code blocks/links/images/page count unchanged vs .work/lang-before/<same path>. Exit = FAIL count."""
import re,sys,os
ROOT='/root/workspace/DevTools/05_kubernetes'; ALLOWED_ANCHORS={'หลักการอ่าน-yaml','0-หลักการอ่าน-yaml-โดยสรุป','5-manifest-ที่มีข้อผิดพลาดโดยเจตนาของปฏิบัติการ-020','อ่าน-yaml-ให้เป็น','0-อ่าน-yaml-ให้เป็น-สรุป','5-manifest-ที่พังโดยตั้งใจของแล็บ-020'}
fails=0
def norm_link(l):
    m=re.match(r'(.*YAML_Guide\.md)#(.*)$',l)
    return m.group(1)+'#<guide-anchor>' if m and m.group(2) in ALLOWED_ANCHORS else l
for f in sys.argv[1:]:
    rel=os.path.relpath(os.path.abspath(f),ROOT); b=os.path.join(ROOT,'.work/lang-before',rel)
    if not os.path.exists(b): print('SKIP',rel,'(no before copy)'); continue
    A=open(f,encoding='utf-8').read(); B=open(b,encoding='utf-8').read(); msgs=[]
    if f.endswith('.html'):
        for name,pat in [('pre blocks',r'<pre[^>]*>(.*?)</pre>'),('ASSETS keys',r'"([A-Za-z0-9_]+)"\s*:\s*"data:image/')]:
            a=re.findall(pat,A,re.S); bb=re.findall(pat,B,re.S)
            if a!=bb: msgs.append(f'{name} differ: before {len(bb)} after {len(a)}' + ('' if len(a)!=len(bb) else ' (content changed at index '+str(next(i for i in range(len(a)) if a[i]!=bb[i]))+')'))
        na=len(re.findall(r'<section class="slide',A)); nb=len(re.findall(r'<section class="slide',B))
        if na!=nb: msgs.append(f'slide count {nb}→{na}')
        sa=re.search(r'<style>.*?</style>',A,re.S); sb=re.search(r'<style>.*?</style>',B,re.S)
        if sa and sb and sa.group(0)!=sb.group(0): msgs.append('CSS <style> changed')
    else:
        a=re.findall(r'```[^\n]*\n(.*?)```',A,re.S); bb=re.findall(r'```[^\n]*\n(.*?)```',B,re.S)
        if a!=bb:
            if len(a)!=len(bb): msgs.append(f'fenced blocks count {len(bb)}→{len(a)}')
            else: i=next(i for i in range(len(a)) if a[i]!=bb[i]); msgs.append(f'fenced block #{i+1} content changed: {bb[i][:60]!r} → {a[i][:60]!r}')
        ia=re.findall(r'!\[[^\]]*\]\(([^)]+)\)',A); ib=re.findall(r'!\[[^\]]*\]\(([^)]+)\)',B)
        if ia!=ib: msgs.append(f'image refs differ {ib[:3]} → {ia[:3]}')
        la=[norm_link(x) for x in re.findall(r'(?<!!)\[[^\]]*\]\(([^)]+)\)',A)]; lb=[norm_link(x) for x in re.findall(r'(?<!!)\[[^\]]*\]\(([^)]+)\)',B)]
        if la!=lb: msgs.append(f'link targets differ (count {len(lb)}→{len(la)}) first diff: {next((x for x,y in zip(lb,la) if x!=y),None)}')
        ha=len(re.findall(r'^#{1,6} ',A,re.M)); hb=len(re.findall(r'^#{1,6} ',B,re.M))
        if ha!=hb: msgs.append(f'heading count {hb}→{ha}')
        na=len(A.splitlines()); nb=len(B.splitlines())
        if abs(na-nb)>max(10,nb*0.12): msgs.append(f'length {nb}→{na} lines (>12%)')
    if msgs: fails+=1; print('FAIL',rel,'·',' · '.join(msgs))
    else: print('OK  ',rel)
sys.exit(min(fails,99))
