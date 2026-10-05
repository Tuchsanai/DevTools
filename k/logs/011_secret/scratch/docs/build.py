#!/usr/bin/env python3
"""render src/*.md (placeholders) -> 011_kubernetes_secret/*/README.md
{{FIG:T05|ชื่อสั้น}}  -> <p align=center id=fig-N> ... caption_th จาก images.json
{{SS:file.png|ชื่อสั้น|คำบรรยาย}} -> ภาพหน้าจอจริง (images/screenshots/)
{{REF:T05}} -> [รูปที่ N](#fig-N)
{{FIGTABLE}} -> ตารางสารบัญรูปภาพ 2 คอลัมน์
"""
import json, re, sys, os
BASE = '/root/workspace/DevTools/k'
D = os.path.dirname(os.path.abspath(__file__))
imgs = {x['id']: x for x in json.load(open(f'{BASE}/logs/011_secret/images.json'))}
OUT = {'theory': f'{BASE}/011_kubernetes_secret/01_Theory/README.md',
       'lab': f'{BASE}/011_kubernetes_secret/02_LAB/README.md',
       'index': f'{BASE}/011_kubernetes_secret/README.md'}
PH = re.compile(r'\{\{(FIG|SS):([^|}]+)\|([^|}]+)(?:\|([^}]+))?\}\}')

def render(name):
    src = open(f'{D}/src/{name}.md').read()
    figs = []; num = {}
    for m in PH.finditer(src):
        key = m.group(2).strip()
        figs.append((key, m.group(3).strip())); num[key] = len(figs)
    def fig(m):
        kind, key, title, cap = m.group(1), m.group(2).strip(), m.group(3).strip(), m.group(4)
        n = num[key]
        if kind == 'FIG':
            it = imgs[key]
            rel = os.path.relpath(it['path'], os.path.dirname(OUT[name]))
            cap = it['caption_th']; width = 900
        else:
            rel = f'images/screenshots/{key}'; width = 700
        return (f'<p align="center" id="fig-{n}">\n  <img src="{rel}" alt="รูปที่ {n} {title}" width="{width}"><br>\n'
                f'  <em><b>รูปที่ {n}</b> {cap.strip()}</em>\n</p>')
    out = PH.sub(fig, src)
    out = re.sub(r'\{\{REF:([^}]+)\}\}', lambda m: f'[รูปที่ {num[m.group(1)]}](#fig-{num[m.group(1)]})', out)
    if '{{FIGTABLE}}' in out:
        half = (len(figs) + 1) // 2
        rows = ['| รูปที่ | เรื่อง | รูปที่ | เรื่อง |', '|:---:|---|:---:|---|']
        for i in range(half):
            a = figs[i]; b = figs[i + half] if i + half < len(figs) else None
            r = f'| {i+1} | [{a[1]}](#fig-{i+1}) |'
            r += f' {i+half+1} | [{b[1]}](#fig-{i+half+1}) |' if b else ' | |'
            rows.append(r)
        out = out.replace('{{FIGTABLE}}', '\n'.join(rows))
    open(OUT[name], 'w').write(out)
    print(name, len(out.encode()), 'bytes', len(figs), 'figs')

for n in (sys.argv[1:] or ['theory', 'lab', 'index']):
    if os.path.exists(f'{D}/src/{n}.md'): render(n)
