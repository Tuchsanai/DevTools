#!/usr/bin/env python3
"""ประกอบ README บท 010 จาก src_*.md — แทน {{FIG:Txx}}, {{SHOT:n}}, {{FIGTOC}}, {{OPEN:T01}} ด้วย caption จริงจาก images.json"""
import json, os, re

K = '/root/workspace/DevTools/k'
CH = f'{K}/010_kubernetes_configmap'
SRC = os.path.dirname(os.path.abspath(__file__))
imgs = {x['id']: x for x in json.load(open(f'{K}/logs/010_configmap/images.json'))}

SHORT = {
 'T01': 'เปิดบท กระดานประกาศกลาง', 'T02': 'ทวนบท 009 ค่าเขียนตรงใน YAML', 'T03': 'อุปมาใหม่ของบทนี้',
 'T04': 'ค่าฝังใน image ต้อง build ใหม่', 'T05': 'หลัก 12-factor แยก config', 'T06': 'อะไรคือ config',
 'T07': 'กายวิภาค ConfigMap', 'T08': 'ขนาดไม่เกิน 1 MiB', 'T09': 'ConfigMap อยู่ใน namespace',
 'T10': 'ไม่ใช่ที่เก็บความลับ', 'T11': 'สร้างด้วย --from-literal', 'T12': 'สร้างด้วย --from-file',
 'T13': 'สร้างด้วย --from-env-file', 'T14': 'ให้ kubectl เขียน YAML', 'T15': 'env ทีละ key (configMapKeyRef)',
 'T16': 'envFrom และ prefix', 'T17': '$(VAR) ใน command/args', 'T18': 'env ชนะ envFrom',
 'T19': 'ชื่อ key ที่กลายเป็น env', 'T20': 'volume ทั้ง ConfigMap', 'T21': 'items เลือกบาง key',
 'T22': 'defaultMode สิทธิ์ไฟล์', 'T23': 'subPath ไฟล์เดียว', 'T24': 'อ้าง ConfigMap/key ที่ไม่มี',
 'T25': 'optional: true', 'T26': 'env ไม่อัปเดตเอง', 'T27': 'volume อัปเดตเอง',
 'T28': '..data symlink สลับทีเดียว', 'T29': 'แอปต้อง reload เอง', 'T30': 'rollout restart และ checksum',
 'T31': 'immutable', 'T32': 'kustomize configMapGenerator', 'T33': 'ConfigMap ของระบบ',
 'T34': 'อ้างข้าม namespace ไม่ได้', 'T35': 'RBAC ของ ConfigMap', 'T36': 'เลือก env หรือ volume',
 'T37': 'แนวปฏิบัติ', 'T38': 'แผนที่สรุปบท', 'T39': 'cheatsheet คำสั่ง', 'T40': 'ปัญหาที่เหลือ → บท 011',
 'L01': 'LAB 0 เตรียมคลัสเตอร์และ image', 'L02': 'LAB 1 ส่องและสร้าง ConfigMap', 'L03': 'LAB 2 env ทีละ key และ $(VAR)',
 'L04': 'LAB 3 envFrom และ prefix', 'L05': 'LAB 4 ไม่มีอยู่และ optional', 'L06': 'LAB 5 mount เป็นไฟล์',
 'L07': 'LAB 6 จับเวลาอัปเดต', 'L08': 'LAB 7 nginx ต้อง reload', 'L09': 'LAB 8 immutable',
 'L10': 'LAB 9 kustomize', 'L11': 'LAB 10 ภาพรวม som-shop-v6', 'L12': 'LAB 10 ขั้น A เริ่มแบบบท 009',
 'L13': 'LAB 10 ขั้น B ป้ายร้านจาก envFrom', 'L14': 'LAB 10 ขั้น C1 แก้แล้วยังไม่เปลี่ยน', 'L15': 'LAB 10 ขั้น C2 rollout restart',
 'L16': 'LAB 10 ขั้นเสริม $(POD_NAMESPACE)', 'L17': 'LAB 10 ขั้น D1 mount ประกาศ', 'L18': 'LAB 10 ขั้น D2 ประกาศเปลี่ยนเอง',
 'L19': 'LAB 10 ขั้น E immutable v2', 'L20': 'LAB 10 ขั้น F รหัสผ่านยังเห็น', 'L21': 'สรุป LAB 10',
}
SHOTS = {
 1: ('images/screenshots/20261005_1724_lab10cm_01-shop-configmap-harbor.png', 'ภาพหน้าจอจริง ร้านจาก ConfigMap ธีม harbor',
     'ภาพหน้าจอจริงจากการทดลอง: ร้าน som-shop-v6 (som-shop-web:1.5) ที่ http://localhost:30080 อ่านค่าจาก ConfigMap som-web-config — ชื่อร้านอาหารแมวน้องส้ม ธีม harbor ออเดอร์ 4 และแถบประกาศ 📢 "วันนี้ปลาทูสดมาก" จาก ConfigMap som-announcement'),
 2: ('images/screenshots/20261005_1726_lab10cm_02-configmap-changed-page-unchanged.png', 'ภาพหน้าจอจริง แก้ ConfigMap แล้วหน้าเว็บยังเดิม',
     'ภาพหน้าจอจริงจากการทดลอง: apply extra/15-config-promo.yaml แล้วรอ 90 วินาที — /api/shop และหน้าเว็บยังเป็นค่าเดิม (ธีม harbor ไม่มีแถบโปรโมชัน) Pod ชื่อเดิม RESTARTS 0'),
 3: ('images/screenshots/20261005_1728_lab10cm_03-after-rollout-sunset-promo.png', 'ภาพหน้าจอจริง หลัง rollout restart',
     'ภาพหน้าจอจริงจากการทดลอง: หลัง kubectl rollout restart — ชื่อร้าน "ร้านน้องส้ม สาขาท่าเรือ" ธีม sunset แถบโปร "🎉 โปรวันนี้: ขนมปลาทูน่าลด 20%" และออเดอร์ยัง 4'),
 4: ('images/screenshots/20261005_1729_lab10cm_04-announcement-updated-no-restart.png', 'ภาพหน้าจอจริง ประกาศเปลี่ยนโดยไม่ restart',
     'ภาพหน้าจอจริงจากการทดลอง: apply extra/16-announcement-1800.yaml + ./wait-announcement.sh 18:00 — Pod แรกเห็นประกาศใหม่หลัง 36 วินาที ทุก Pod หลัง 65 วินาที แถบประกาศเป็น "ปิดร้านเร็ว 18:00 น. ⛵" โดย RESTARTS 0 และ AGE ต่อเนื่อง'),
}


def build(src, out):
    text = open(f'{SRC}/{src}').read()
    outdir = os.path.dirname(out)
    order = []  # (kind, key)
    for m in re.finditer(r'\{\{(FIG|SHOT):([A-Z0-9]+)\}\}', text):
        order.append((m.group(1), m.group(2)))
    num = {o: i + 1 for i, o in enumerate(order)}

    def block(kind, key):
        n = num[(kind, key)]
        if kind == 'FIG':
            x = imgs[key]
            rel = os.path.relpath(x['path'], outdir)
            alt, cap, w = SHORT[key], x['caption_th'], 900
        else:
            p, alt, cap = SHOTS[int(key)]
            rel, w = p, 700
        return (f'<p align="center" id="fig-{n}">\n  <img src="{rel}" alt="รูปที่ {n} {alt}" width="{w}"><br>\n'
                f'  <em><b>รูปที่ {n}</b> {cap}</em>\n</p>')

    text = re.sub(r'\{\{(FIG|SHOT):([A-Z0-9]+)\}\}', lambda m: block(m.group(1), m.group(2)), text)
    # สารบัญรูปภาพ 2 คอลัมน์
    if '{{FIGTOC}}' in text:
        titles = [SHORT[k] if kd == 'FIG' else SHOTS[int(k)][1] for kd, k in order]
        half = (len(titles) + 1) // 2
        rows = ['| รูปที่ | เรื่อง | รูปที่ | เรื่อง |', '|:---:|---|:---:|---|']
        for i in range(half):
            a = f'| {i+1} | [{titles[i]}](#fig-{i+1}) |'
            j = i + half
            b = f' {j+1} | [{titles[j]}](#fig-{j+1}) |' if j < len(titles) else ' | |'
            rows.append(a + b)
        text = text.replace('{{FIGTOC}}', '\n'.join(rows))
    m = re.search(r'\{\{OPEN:(T\d\d)\}\}', text)
    if m:
        x = imgs[m.group(1)]
        rel = os.path.relpath(x['path'], outdir)
        text = text.replace(m.group(0), f'<p align="center">\n  <img src="{rel}" alt="{SHORT[m.group(1)]}" width="900"><br>\n  <em>{x["caption_th"]}</em>\n</p>')
    assert '{{' not in text, re.findall(r'\{\{[^}]*\}\}', text)
    open(out, 'w').write(text)
    print(out, len(text.encode()), 'bytes,', len(order), 'figures')


build('src_theory.md', f'{CH}/01_Theory/README.md')
build('src_lab.md', f'{CH}/02_LAB/README.md')
build('src_main.md', f'{CH}/README.md')
