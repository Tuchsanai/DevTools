# บทที่ 3: Kubernetes ReplicaSet — ร้านน้องส้มไม่มีวันปิด

> **รายวิชา:** Software Development Tools and Environments (DevTools)
> **หัวข้อ:** Kubernetes ReplicaSet, replicas / selector / template, self-healing, scale, labels, การกระจาย Pod บนหลาย Node และร้านหลายสาขา
> **ผลลัพธ์การเรียนรู้ที่เกี่ยวข้อง:** CLO-5, CLO-6

<p align="center">
  <img src="01_Theory/images/01-opening-shop-closed.png" alt="Pod ร้านน้องส้มถูกลบ ร้านปิด" width="900"><br>
  <em>Pod ร้านน้องส้มถูกลบแล้วไม่มีใครเปิดร้านคืน บทนี้น้องส้มจะมีหัวหน้าลูกเรือ ReplicaSet คอยนับกล่องให้ครบเสมอ</em>
</p>

## บทนี้เรียนอะไร

บทที่ 2 เราสร้าง Pod ทีละตัว ลบแล้วก็หายไปเลย บทนี้ให้ **ReplicaSet** ดูแลจำนวน Pod ให้ครบตามที่ขอตลอดเวลา เราจะอ่าน YAML ของ ReplicaSet ลองลบ Pod ดูว่ามันซ่อมตัวเองอย่างไร เพิ่ม-ลดจำนวน ดูว่ามันนับ Pod จาก label แล้วปิดท้ายด้วย **ร้านอาหารแมวน้องส้มหลายสาขา** ที่มีหน้าร้านหลาย Pod บนคลัสเตอร์ kind ของตัวเอง

| ส่วน | เนื้อหา | ลิงก์ |
|---|---|---|
| 📖 **ทฤษฎี** | ReplicaSet คืออะไร, วงจรนับ-เทียบ-แก้, อ่าน YAML (`replicas` / `selector` / `template`) ทีละบรรทัด, เจ้าของ Pod, self-healing, scale, labels, การกระจาย Pod, ข้อจำกัดเรื่องเปลี่ยนเวอร์ชัน และปูทางไป Deployment / Service (มีคำถามทบทวนพร้อมแนวคำตอบ) | [01_Theory/README.md](01_Theory/README.md) |
| 🧪 **ปฏิบัติการ** | LAB 0–4: สร้างคลัสเตอร์ → ReplicaSet แรก + self-healing → scale + labels → Pod บนหลาย Node → **LAB สุดท้าย: ร้านอาหารแมวน้องส้มหลายสาขา** พร้อมสรุปคำสั่ง kubectl ท้ายบท | [02_LAB/README.md](02_LAB/README.md) |

## คำแนะนำในการเรียน

1. **อ่านทฤษฎีก่อน** อย่างน้อยหัวข้อ 1–6 แล้วเริ่ม LAB 0–1 ได้เลย
2. ก่อนทำ LAB 2–4 ให้อ่านหัวข้อ 7–12 (scale, labels, การกระจาย Pod, แก้แม่พิมพ์, port-forward)
3. ทำ LAB **ตามลำดับ** ใช้เวลารวมประมาณ 2.5–3 ชั่วโมง
4. สังเกตสัญลักษณ์ในเอกสาร LAB ว่าคำสั่งรันที่ไหน: 🖥️ บนเครื่องนักศึกษา / 🐧 ใน SSH session ของ k8s-lab / 🌐 browser
5. ผลลัพธ์ในเอกสารมาจากการทดลองจริง (Kubernetes v1.37.0) แต่ **ชื่อ Pod ถูกสุ่มทุกครั้ง** และเวลา, IP, ชื่อ Node อาจต่างจากเครื่องของนักศึกษา
6. ลองตอบคำถามทบทวนด้วยตัวเองก่อนเปิดดูแนวคำตอบ

> **ขอบเขตของบทนี้:** ใช้ **ReplicaSet กับ Pod เท่านั้น** การเปิดเว็บยังใช้ `kubectl port-forward` ร่วมกับแท็บ PORTS ของ VS Code ส่วน Deployment และ Service เป็น **เนื้อหาของบทถัดไป**

## สิ่งที่ต้องมีก่อนเริ่ม

- ผ่าน [บทที่ 2: Kubernetes Pod](../002_kubernetes_pod/README.md) แล้ว อ่าน YAML ของ Pod ได้ และรู้จัก labels, probes, `kubectl logs` / `exec` / `port-forward`
- มี container **`k8s-lab`** (หรือสร้างใหม่ใน LAB 0) ล็อกอินได้ด้วย `ssh -p 2223 root@localhost` (รหัส `passwd` ใช้เพื่อการเรียนเท่านั้น)
- VS Code + extension Container Tools และ Dev Containers (ใช้ใน LAB 4)
- เครื่องต่ออินเทอร์เน็ตได้ (ดึง image จาก Docker Hub)

## โครงสร้างโฟลเดอร์

```text
003_kubernetes_Replicaset/
├── README.md                         ← หน้านี้
├── 01_Theory/
│   ├── README.md                     ← เอกสารทฤษฎี
│   └── images/                       ← ภาพประกอบ (+ imagegen-prompts.md)
└── 02_LAB/
    ├── README.md                     ← คู่มือ LAB 0–4
    ├── images/                       ← ภาพประกอบ LAB + screenshots/ ภาพหน้าจอจริง
    ├── labs/                         ← YAML ของ LAB 1–3
    │   ├── lab01-first-rs/web-rs.yaml
    │   └── lab02-labels/extra-pod.yaml
    └── som-menu/                     ← LAB 4 ร้านอาหารแมวน้องส้มหลายสาขา
        ├── app/                      ← เว็บหน้าร้าน Node.js (server.js + Dockerfile)
        └── k8s/                      ← som-menu-rs.yaml (v1.0) และ som-menu-rs-v2.yaml (v2.0)
```

ใน LAB 0 จะ `git clone` repo เข้า container แล้วทำงานที่ `/workspace/DevTools/05_kubernetes/003_kubernetes_Replicaset/02_LAB` ภายใน k8s-lab

## เริ่มเลย

👉 [อ่านทฤษฎี](01_Theory/README.md) → [ลงมือทำ LAB](02_LAB/README.md)
