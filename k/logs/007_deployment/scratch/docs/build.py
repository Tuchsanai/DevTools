#!/usr/bin/env python3
"""ประกอบ README บท 007 จากไฟล์ *.src.md
- {{FIG:T05|ชื่อสั้น}}            → <p align="center" id="fig-N"> + caption_th จาก images.json (ตรงทุกตัวอักษร)
- {{SS:ไฟล์|ชื่อสั้น|คำบรรยาย}}   → ภาพหน้าจอจริง (images/screenshots/<ไฟล์>)
- {{FIGTOC}}                       → ตารางสารบัญรูปภาพ (2 คอลัมน์คู่)
"""
import html, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = '/root/workspace/DevTools/k'
IMG = {x['id']: x for x in json.load(open(f'{ROOT}/logs/007_deployment/images.json', encoding='utf-8'))}

JOBS = [
    ('theory.src.md', f'{ROOT}/007_kubernetes_deployment/01_Theory/README.md', f'{ROOT}/007_kubernetes_deployment/01_Theory'),
    ('lab.src.md', f'{ROOT}/007_kubernetes_deployment/02_LAB/README.md', f'{ROOT}/007_kubernetes_deployment/02_LAB'),
    ('index.src.md', f'{ROOT}/007_kubernetes_deployment/README.md', f'{ROOT}/007_kubernetes_deployment'),
]

PAT = re.compile(r'\{\{(FIG|SS):([^}]*)\}\}')


def build(src, dst, base):
    text = open(os.path.join(HERE, src), encoding='utf-8').read()
    n = 0
    toc = []

    def fig(m):
        nonlocal n
        kind, arg = m.group(1), m.group(2)
        n += 1
        if kind == 'FIG':
            iid, short = arg.split('|', 1)
            rel = os.path.relpath(IMG[iid]['path'], base)
            cap = IMG[iid]['caption_th']
            width = 900
        else:
            fname, short, cap = arg.split('|', 2)
            rel = f'images/screenshots/{fname}'
            width = 700
        toc.append((n, short))
        return (f'<p align="center" id="fig-{n}">\n'
                f'  <img src="{rel}" alt="รูปที่ {n} {html.escape(short, quote=True)}" width="{width}"><br>\n'
                f'  <em><b>รูปที่ {n}</b> {html.escape(cap, quote=False)}</em>\n'
                f'</p>')

    text = PAT.sub(fig, text)
    if '{{FIGTOC}}' in text:
        half = (len(toc) + 1) // 2
        rows = ['| รูปที่ | เรื่อง | รูปที่ | เรื่อง |', '|:---:|---|:---:|---|']
        for i in range(half):
            a = toc[i]
            b = toc[i + half] if i + half < len(toc) else None
            cell_b = f'| {b[0]} | [{b[1]}](#fig-{b[0]}) |' if b else '| | |'
            rows.append(f'| {a[0]} | [{a[1]}](#fig-{a[0]}) {cell_b}')
        text = text.replace('{{FIGTOC}}', '\n'.join(rows))
    open(dst, 'w', encoding='utf-8').write(text)
    print(f'{dst}: {n} figures, {len(text.encode())} bytes')


for src, dst, base in JOBS:
    if os.path.exists(os.path.join(HERE, src)):
        build(src, dst, base)
