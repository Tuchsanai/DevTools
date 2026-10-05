#!/usr/bin/env python3
"""ประกอบ README บท 006 จากร่างใน scratch/docs แทน {{FIG:Txx}}, {{TOC}}, {{FIGTOC}}, {{LABTOC}}, {{A:หัวข้อ}}"""
import json, re, html, unicodedata, sys, os

BASE = '/root/workspace/DevTools/k'
DOCS = f'{BASE}/logs/006_service/scratch/docs'
CH = f'{BASE}/006_kubernetes_service'
IMGS = {it['id']: it for it in json.load(open(f'{BASE}/logs/006_service/images.json', encoding='utf-8'))}

SHORT = {
    'T01': 'บูธครบ 3 แต่ลูกค้าหาร้านไม่เจอ', 'T02': 'อุปมาใหม่ของบทนี้', 'T03': 'port-forward ทีละ Pod และ db แยกบูธ',
    'T04': 'ทำไมต้องมี Service', 'T05': 'ClusterIP เป็นที่อยู่เสมือน', 'T06': 'โครง manifest ของ Service',
    'T07': 'selector → EndpointSlice', 'T08': 'EndpointSlice controller', 'T09': 'v1 Endpoints เป็นรุ่นเก่า',
    'T10': 'Service CIDR', 'T11': 'port / targetPort / nodePort', 'T12': 'named port และหลายพอร์ต',
    'T13': 'NodePort เปิดบนทุก Node', 'T14': 'เส้นทางจาก browser ถึง Pod', 'T15': 'กติกาของ NodePort',
    'T16': 'LoadBalancer ค้าง pending ใน kind', 'T17': 'ExternalName ชื่อแฝง', 'T18': 'headless สมุดรายชื่อบูธ',
    'T19': 'DNS ของ Service ข้าม namespace', 'T20': 'resolv.conf: search และ ndots', 'T21': 'env var ของ Service',
    'T22': 'kube-proxy ป้ายบอกทางบนทุกเรือ', 'T23': 'kube-proxy watch และโหมด', 'T24': 'สุ่มต่อ connection',
    'T25': 'keep-alive ติดบูธเดิม', 'T26': 'sessionAffinity', 'T27': 'readiness กับ endpoints',
    'T28': 'endpoint ของ Pod ที่กำลังปิด', 'T29': 'บันได debug Service', 'T30': 'selector พิมพ์ผิด',
    'T31': 'targetPort ผิด', 'T32': 'NetworkPolicy ตรวจหลัง DNAT', 'T33': 'สิ่งที่ Service ยังไม่ช่วย',
    'T34': 'ตารางเลือกชนิด Service', 'T35': 'สรุปบทที่ 6', 'T36': 'ปูทางบทที่ 7',
    'L01': 'LAB 0 เตรียมคลัสเตอร์และตรวจพอร์ต', 'L02': 'LAB 1 IP ของ Pod เปลี่ยน', 'L03': 'LAB 2 expose และ EndpointSlice',
    'L04': 'LAB 2 EndpointSlice ตาม Pod เอง', 'L05': 'LAB 3 พอร์ตและชื่อพอร์ต', 'L06': 'LAB 4 DNS และ env var',
    'L07': 'LAB 5 สุ่มและ sessionAffinity', 'L08': 'LAB 6 Pod ไม่ ready', 'L09': 'LAB 7 debug Service',
    'L10': 'LAB 8 NodePort จาก browser', 'L11': 'LAB 8 keep-alive และ LoadBalancer', 'L12': 'LAB 9 เรียกข้าม namespace',
    'L13': 'LAB 9 headless และ ExternalName', 'L14': 'LAB 9 NetworkPolicy ใช้ targetPort', 'L15': 'LAB 10 สถาปัตยกรรม',
    'L16': 'LAB 10 build image 1.2 และ 1.3', 'L17': 'LAB 10 db และ Service som-db', 'L18': 'LAB 10 เติมสินค้าแบบกันชน',
    'L19': 'LAB 10 เปิดร้านที่ 30080', 'L20': 'LAB 10 hit.sh และออเดอร์รวม', 'L21': 'LAB 10 scale และ self-healing',
    'L22': 'LAB 10 ลบ Pod db ข้อมูลหาย', 'L23': 'LAB 10 เปลี่ยนรุ่นด้วยมือจนสะดุด', 'L24': 'สรุป LAB บทที่ 6',
}
SS = {
    'S1': ('20261005_0933_lab10svc_01-shop-nodeport-1.2.png', 'ภาพหน้าจอจริง ร้านเวอร์ชัน 1.2',
           'ภาพหน้าจอจริงจากการทดลอง: เปิด http://localhost:30080 (NodePort โดยตรง ไม่ใช้ port-forward หรือ ssh -L) หน้าร้านธีม harbor ป้าย "เวอร์ชัน 1.2" แถบ "🐱 เสิร์ฟโดย Pod: som-web-tmxnr · เวอร์ชัน 1.2" และออเดอร์ทั้งหมด 4 ซึ่งรวมจากทุกบูธใน db กลางตัวเดียว'),
    'S2': ('20261005_0935_lab10svc_02-503-after-db-deleted.png', 'ภาพหน้าจอจริง หน้า 503 หลังลบ Pod db',
           'ภาพหน้าจอจริงจากการทดลอง: หลังลบ Pod db Service som-db ยังใช้ ClusterIP เดิม 10.96.188.142 แต่ endpoint เปลี่ยนจาก 10.244.2.33 เป็น 10.244.2.38 ฐานข้อมูลใหม่ยังว่าง หน้าเว็บจึงตอบ HTTP 503 "ร้านกำลังเตรียมสินค้า กรุณารอสักครู่" (เสิร์ฟโดย Pod som-web-bx7tz ที่ยัง Ready อยู่)'),
    'S3': ('20261005_0936_lab10svc_03-shop-back-0-orders.png', 'ภาพหน้าจอจริง ร้านกลับมาแต่ออเดอร์ 0',
           'ภาพหน้าจอจริงจากการทดลอง: ลบ Pod web 1 ตัวให้ initContainer db-seed ของ Pod ใหม่เติมสินค้าใหม่ ร้านกลับมาขายได้ทุกบูธ แต่ออเดอร์ทั้งหมด 0 และชิ้นที่ขายแล้ว 0 เพราะข้อมูลเดิมหายไปพร้อม emptyDir ของ Pod db ตัวเก่า'),
    'S4': ('20261005_0937_lab10svc_04-shop-1.3-after-manual-delete.png', 'ภาพหน้าจอจริง ร้านเวอร์ชัน 1.3',
           'ภาพหน้าจอจริงจากการทดลอง: set image rs/som-web เป็น 1.3 แล้ว Pod เดิมยังเป็น 1.2 ต้องลบ Pod ทั้งหมดเอง (ระหว่างนั้น curl 150 ครั้ง error 7) จึงได้ร้านธีม sunset ป้าย "เวอร์ชัน 1.3" และแบนเนอร์ "🎉 เมนูใหม่: ขนมปลาทูน่าอบกรอบ 🐟" — ออเดอร์ 3 ในภาพสั่งหลังเติมสินค้าใหม่และยังอยู่ เพราะลบแค่ Pod web ไม่ได้ลบ db'),
}


def slug(s):
    out = []
    for ch in s.strip().lower():
        if ch == ' ':
            out.append('-')
        elif ch in '-_' or unicodedata.category(ch)[0] in 'LMN':
            out.append(ch)
    return ''.join(out)


def esc(s):
    return html.escape(s, quote=False)


def build(src, dst, kind):
    text = open(f'{DOCS}/{src}', encoding='utf-8').read()
    figs = []  # (n, key, short)

    def fig(m):
        key = m.group(1)
        n = len(figs) + 1
        if key in SS:
            fn, short, cap = SS[key]
            src_ = f'images/screenshots/{fn}'
            width = 700
        else:
            it = IMGS[key]
            fn = os.path.basename(it['path'])
            short, cap = SHORT[key], it['caption_th']
            src_ = f'images/{fn}'
            width = 900
        figs.append((n, key, short))
        return (f'<p align="center" id="fig-{n}">\n'
                f'  <img src="{src_}" alt="รูปที่ {n} {esc(short)}" width="{width}"><br>\n'
                f'  <em><b>รูปที่ {n}</b> {esc(cap)}</em>\n</p>')

    if '{{TOPFIG}}' in text:
        it = IMGS['T01']
        text = text.replace('{{TOPFIG}}', '<p align="center">\n'
            f'  <img src="01_Theory/images/{os.path.basename(it["path"])}" alt="{esc(SHORT["T01"])}" width="900"><br>\n'
            f'  <em>{esc(it["caption_th"])}</em>\n</p>')
    text = re.sub(r'\{\{FIG:(\w+)\}\}', fig, text)

    heads = [h for h in re.findall(r'^## (.+)$', text, flags=re.M)]

    # สารบัญรูปภาพ 2 คอลัมน์
    half = (len(figs) + 1) // 2
    rows = ['| รูปที่ | เรื่อง | รูปที่ | เรื่อง |', '|:---:|---|:---:|---|']
    for i in range(half):
        a = figs[i]
        b = figs[i + half] if i + half < len(figs) else None
        rows.append(f'| {a[0]} | [{a[2]}](#fig-{a[0]}) | ' + (f'{b[0]} | [{b[2]}](#fig-{b[0]}) |' if b else ' | |'))
    text = text.replace('{{FIGTOC}}', '\n'.join(rows))

    if '{{TOC}}' in text:
        toc = []
        for h in heads:
            m = re.match(r'(\d+)\. (.+)', h)
            if m:
                toc.append(f'{m.group(1)}. [{m.group(2)}](#{slug(h)})')
        text = text.replace('{{TOC}}', '\n'.join(toc))

    text = re.sub(r'\{\{A:(.+?)\}\}', lambda m: '#' + slug(m.group(1)), text)
    open(dst, 'w', encoding='utf-8').write(text)
    print(dst, len(text.encode()), 'bytes,', len(figs), 'figures')
    return figs


if __name__ == '__main__':
    which = sys.argv[1:] or ['theory', 'lab', 'top']
    if 'theory' in which:
        parts = sorted(p for p in os.listdir(DOCS) if p.startswith('theory_') and p.endswith('.md'))
        open(f'{DOCS}/_theory.md', 'w', encoding='utf-8').write(''.join(open(f'{DOCS}/{p}', encoding='utf-8').read() for p in parts))
        build('_theory.md', f'{CH}/01_Theory/README.md', 'theory')
    if 'lab' in which:
        parts = sorted(p for p in os.listdir(DOCS) if p.startswith('lab_') and p.endswith('.md'))
        open(f'{DOCS}/_lab.md', 'w', encoding='utf-8').write(''.join(open(f'{DOCS}/{p}', encoding='utf-8').read() for p in parts))
        build('_lab.md', f'{CH}/02_LAB/README.md', 'lab')
    if 'top' in which:
        build('top.md', f'{CH}/README.md', 'top')
