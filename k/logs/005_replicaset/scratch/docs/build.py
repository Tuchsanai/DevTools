#!/usr/bin/env python3
"""ประกอบ README บท 005 จาก template: แทน {{FIG:Txx}}/{{FIG:Lxx}}/{{FIG:Sx}} ด้วยบล็อกภาพ (caption จาก images.json) และ {{FIGTOC}} ด้วยสารบัญรูปภาพ"""
import html, json, re, os

ROOT = "/root/workspace/DevTools/k"
CH = f"{ROOT}/005_kubernetes_replicaset"
HERE = os.path.dirname(os.path.abspath(__file__))
IMGS = {i["id"]: i for i in json.load(open(f"{ROOT}/logs/005_replicaset/images.json"))}

SHORT = {
 "T01": "บูธเดี่ยวหาย ไม่มีใครสร้างใหม่", "T02": "สามปัญหาที่ค้างจากบท 002–004", "T03": "อุปมาใหม่ของบทนี้",
 "T04": "reconciliation loop", "T05": "controller อยู่ใน kube-controller-manager", "T06": "level-triggered",
 "T07": "โครง ReplicaSet 3 ส่วน", "T08": "อ่าน YAML ของ ReplicaSet", "T09": "การตั้งชื่อ Pod ของ ReplicaSet",
 "T10": "matchLabels และ matchExpressions", "T11": "label ของ template ไม่ตรง selector", "T12": "ownerReferences ป้ายเจ้าของ",
 "T13": "อ่านสถานะ ReplicaSet", "T14": "self-healing", "T15": "ตัวใหม่เกิดขณะตัวเก่า Terminating",
 "T16": "drain: Pod เดี่ยว vs ReplicaSet", "T17": "ไทม์ไลน์เรือล่ม", "T18": "scale ReplicaSet",
 "T19": "ลำดับการลบตอน scale ลง", "T20": "นับจาก label ไม่ใช่ชื่อ", "T21": "กับดักที่ 1 รับเลี้ยง Pod หลง",
 "T22": "กับดักที่ 2 ลบ Pod ที่เกิน", "T23": "กับดักที่ 3 selector ทับกัน", "T24": "ถอด label เพื่อ debug",
 "T25": "selector แก้ไม่ได้", "T26": "template ใหม่ไม่เปลี่ยน Pod เดิม", "T27": "ลบ RS 3 แบบ",
 "T28": "orphan แล้วรับเลี้ยงใหม่", "T29": "ReplicationController รุ่นพี่", "T30": "ReplicaSet กับ ResourceQuota",
 "T31": "Pod Security Admission กับ ReplicaSet", "T32": "required anti-affinity", "T33": "preferred และ topology spread",
 "T34": "ชื่อและ IP เปลี่ยนทุกครั้ง", "T35": "สรุปบทที่ 5", "T36": "ปัญหาที่ส่งต่อบท 006 และ 007",
 "L01": "LAB 0 เตรียมคลัสเตอร์", "L02": "LAB 1 ReplicaSet แรก", "L03": "LAB 2 ลบ Pod แล้วดูด้วย -w",
 "L04": "LAB 2 drain และเรือล่ม", "L05": "LAB 3 scale", "L06": "LAB 4 กับดัก label",
 "L07": "LAB 5 template ใหม่ Pod เดิมไม่เปลี่ยน", "L08": "LAB 6 cascade vs orphan", "L09": "LAB 7 quota, LimitRange, PSA",
 "L10": "LAB 8 กระจาย replica", "L11": "LAB 9 สถาปัตยกรรมร้าน 3 บูธ", "L12": "LAB 9 เตรียม image",
 "L13": "LAB 9 3 บูธบน 2 เรือ", "L14": "LAB 9 port-forward ทีละบูธ", "L15": "LAB 9 ออเดอร์ไม่ตรงกัน",
 "L16": "LAB 9 ลบบูธแล้วข้อมูลหาย", "L17": "LAB 9 scale 3→5→2", "L18": "LAB 9 template promo",
 "L19": "LAB 9 เปลี่ยนรุ่นทีละบูธด้วยมือ", "L20": "สรุป LAB 9 และปัญหาส่งต่อ",
}

SHOTS = {
 "S1": ("images/screenshots/20261005_0831_lab9rs_01-booth-1.png", "ภาพหน้าจอจริง บูธที่ 1",
        "ภาพหน้าจอจริงจากการทดลอง: บูธแรก หัวเว็บ \"⚓ บูธ som-booth-rmcck\" สั่งซื้อไป 1 ครั้ง ช่องออเดอร์ทั้งหมดเป็น 1 และอาหารเม็ดสูตรปลาทูน่าเหลือ 19 ชิ้น"),
 "S2": ("images/screenshots/20261005_0831_lab9rs_02-booth-2.png", "ภาพหน้าจอจริง บูธที่ 2",
        "ภาพหน้าจอจริงจากการทดลอง: บูธที่สอง \"⚓ บูธ som-booth-gxx9d\" (ReplicaSet เดียวกัน แบบพิมพ์เดียวกัน) แต่ออเดอร์ทั้งหมดเป็น 2 ไม่รวมออเดอร์ของบูธแรก"),
 "S3": ("images/screenshots/20261005_0831_lab9rs_03-booth-3.png", "ภาพหน้าจอจริง บูธที่ 3",
        "ภาพหน้าจอจริงจากการทดลอง: บูธที่สาม \"⚓ บูธ som-booth-tdxr6\" ออเดอร์ทั้งหมด 3 — ร้านเดียวกันแต่มีสมุดออเดอร์ 3 เล่ม เพราะแต่ละบูธมีฐานข้อมูล (emptyDir) ของตัวเอง"),
 "S4": ("images/screenshots/20261005_0832_lab9rs_04-replacement-booth-0-orders.png", "ภาพหน้าจอจริง บูธใหม่ออเดอร์ 0",
        "ภาพหน้าจอจริงจากการทดลอง: หลังลบบูธ som-booth-rmcck ReplicaSet สร้างบูธใหม่ som-booth-z96mn ภายในราว 7 วินาที ร้านกลับมาครบ 3 บูธ แต่ออเดอร์ทั้งหมดเป็น 0 และสต็อกกลับเป็นค่าตั้งต้น เพราะฐานข้อมูลของบูธใหม่ว่างเปล่า (และต้องเปิด port-forward ใหม่เพราะตัวเดิมหลุด)"),
}


def build(tpl_name, out_path, img_prefix_strip, index_mode=False):
    src = open(os.path.join(HERE, tpl_name), encoding="utf-8").read()
    order = []

    def fig(m):
        key = m.group(1)
        order.append(key)
        n = len(order)
        if key.startswith("S"):
            path, short, cap = SHOTS[key]
            width = 700
        else:
            it = IMGS[key]
            path = it["path"].split("005_kubernetes_replicaset/")[1]
            path = path[len(img_prefix_strip):] if path.startswith(img_prefix_strip) else path
            short, cap, width = SHORT[key], it["caption_th"], 900
        return (f'<p align="center" id="fig-{n}">\n'
                f'  <img src="{path}" alt="รูปที่ {n} {html.escape(short, quote=True)}" width="{width}"><br>\n'
                f'  <em><b>รูปที่ {n}</b> {html.escape(cap, quote=False)}</em>\n</p>')

    body = re.sub(r"\{\{FIG:([TLS]\d+)\}\}", fig, src)
    # สารบัญรูปภาพ 2 คอลัมน์
    rows = []
    half = (len(order) + 1) // 2
    for i in range(half):
        a = order[i]
        j = i + half
        cell = lambda k, n: f"{n} | [{SHORT.get(k) or SHOTS[k][1]}](#fig-{n})"
        right = cell(order[j], j + 1) if j < len(order) else " | "
        rows.append(f"| {cell(a, i + 1)} | {right} |")
    toc = "| รูปที่ | เรื่อง | รูปที่ | เรื่อง |\n|:---:|---|:---:|---|\n" + "\n".join(rows)
    body = body.replace("{{FIGTOC}}", toc)
    open(out_path, "w", encoding="utf-8").write(body)
    print(out_path, len(body.encode()), "bytes,", len(order), "figures:", " ".join(order))
    return order


if __name__ == "__main__":
    build("theory.md", f"{CH}/01_Theory/README.md", "01_Theory/")
    build("lab.md", f"{CH}/02_LAB/README.md", "02_LAB/")
    # หน้ารวม: path ของภาพอยู่ใต้ 005_kubernetes_replicaset/ อยู่แล้ว
    src = open(os.path.join(HERE, "index.md"), encoding="utf-8").read()
    it = IMGS["T01"]
    src = src.replace("{{T01_PATH}}", it["path"].split("005_kubernetes_replicaset/")[1]).replace("{{T01_CAP}}", html.escape(it["caption_th"], quote=False))
    open(f"{CH}/README.md", "w", encoding="utf-8").write(src)
    print(f"{CH}/README.md", len(src.encode()), "bytes")
