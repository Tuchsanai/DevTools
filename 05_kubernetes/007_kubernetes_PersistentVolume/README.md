# บทที่ 7: Kubernetes PersistentVolume — สมุดออเดอร์ที่ไม่หาย

> **รายวิชา:** Software Development Tools and Environments (DevTools)
> **หัวข้อ:** emptyDir vs PersistentVolumeClaim, PVC / PV / StorageClass, Pending → Bound, ที่เก็บผูกกับ Node, accessModes, ลบอะไรแล้วข้อมูลหาย, ฐานข้อมูลบน PVC และร้านที่เก็บออเดอร์ไม่หาย
> **ผลลัพธ์การเรียนรู้ที่เกี่ยวข้อง:** CLO-5, CLO-6

<p align="center">
  <img src="01_Theory/images/01-opening-orders-lost.png" alt="Pod ใหม่ของร้านน้องส้ม สมุดออเดอร์หายหมด" width="900"><br>
  <em>บทที่แล้วร้านเปลี่ยนป้ายได้โดยไม่ต้อง build ใหม่ แต่ทุกครั้งที่ Pod ถูกสร้างใหม่ ข้อมูลที่เขียนไว้ใน Pod หายหมด บทนี้น้องส้มเช่าล็อกเกอร์ PersistentVolume ไว้เก็บสมุดออเดอร์ที่อยู่ได้นานกว่า Pod</em>
</p>

## บทนี้เรียนอะไร

ตั้งแต่บทที่ 2 ข้อมูลที่แอปเขียนไว้ใน container หรือ emptyDir จะหายเมื่อ Pod ถูกลบ และ Deployment ก็สร้าง Pod ใหม่บ่อยมาก (rolling update, restart, scale) บทนี้ใช้ **PersistentVolumeClaim (PVC)** ขอพื้นที่เก็บข้อมูลที่ **อยู่ได้นานกว่า Pod** โดยมี **StorageClass** ของคลัสเตอร์สร้าง **PersistentVolume (PV)** ให้อัตโนมัติ เราจะดูว่า PVC เปลี่ยนจาก `Pending` เป็น `Bound` เมื่อไร ทำไม Pod ที่ใช้ที่เก็บต้องไปอยู่ Node เดิม ลบอะไรแล้วข้อมูลยังอยู่ ลบอะไรแล้วหายถาวร จากนั้นเอาฐานข้อมูล PostgreSQL ไปวางบน PVC และปิดท้ายด้วย **ร้านอาหารแมวน้องส้ม** ที่มีสมุดออเดอร์บน PVC ลบ Pod ลบ Deployment หรือ scale เท่าไร ออเดอร์ก็ไม่หาย

| ส่วน | เนื้อหา | ลิงก์ |
|---|---|---|
| 📖 **ทฤษฎี** | ข้อมูลอยู่ที่ไหนได้บ้าง, PVC / PV / StorageClass, อ่าน YAML ของ PVC ทีละบรรทัด, ต่อ PVC เข้า Pod, Pending → Bound, ที่เก็บผูกกับเรือ (Node Affinity), accessModes, ลบอะไรแล้วข้อมูลหาย, กับดัก PVC ค้าง Pending, ฐานข้อมูลบน PVC และปูทางไป Ingress (มีคำถามทบทวนพร้อมแนวคำตอบ) | [01_Theory/README.md](01_Theory/README.md) |
| 🧪 **ปฏิบัติการ** | LAB 0–4: สร้างคลัสเตอร์ → emptyDir หาย vs PVC อยู่ → PVC, PV และ StorageClass → ฐานข้อมูลบน PVC → **LAB สุดท้าย: สมุดออเดอร์ร้านน้องส้มที่ไม่หาย** พร้อมสรุปคำสั่งท้ายบท | [02_LAB/README.md](02_LAB/README.md) |

## คำแนะนำในการเรียน

1. **อ่านทฤษฎีก่อน** อย่างน้อยหัวข้อ 1–6 แล้วเริ่ม LAB 0–1 ได้เลย
2. ก่อนทำ LAB 2–4 ให้อ่านหัวข้อ 7–12 (ที่เก็บผูกกับเรือ, accessModes, ลบอะไรแล้วหาย, PVC ค้าง Pending, ฐานข้อมูล, YAML ร้านน้องส้ม)
3. ทำ LAB **ตามลำดับ** ใช้เวลารวมประมาณ 2.5–3 ชั่วโมง (LAB 3 ต้องดึง image PostgreSQL ราว 100 MB)
4. สังเกตสัญลักษณ์ในเอกสาร LAB ว่าคำสั่งรันที่ไหน: 🖥️ บนเครื่องนักศึกษา / 🐧 ใน SSH session ของ k8s-lab / 🌐 browser
5. ผลลัพธ์ในเอกสารมาจากการทดลองจริง (Kubernetes v1.37.0) แต่ **ชื่อ Pod, ชื่อ PV และ Node ที่ได้ที่เก็บถูกสุ่มทุกครั้ง**
6. ลองตอบคำถามทบทวนด้วยตัวเองก่อนเปิดดูแนวคำตอบ

> **ขอบเขตของบทนี้:** ใช้ PVC กับ StorageClass `standard` (local-path) ที่มากับ kind ให้สร้าง PV อัตโนมัติ ไม่สร้าง PV เอง ไม่ใช้ StatefulSet หรือที่เก็บบนเครือข่าย ⚠️ **ลบ PVC = ข้อมูลหายถาวร** ทำเฉพาะตอนเก็บกวาดท้าย LAB ส่วนการเข้าร้านด้วยชื่อโดเมนแทน port (Ingress) เป็น **เนื้อหาของบทถัดไป**

## สิ่งที่ต้องมีก่อนเริ่ม

- ผ่าน [บทที่ 6: Kubernetes ConfigMap และ Secret](../006_kubernetes_ConfigMap_Secret/README.md) แล้ว ใช้ Secret และ Service แบบ NodePort ได้
- container **`k8s-lab`** ที่สร้างด้วย **`-p 30080-30082:30080-30082`** (LAB 0)
- เครื่องต่ออินเทอร์เน็ตได้ (ดึง image จาก Docker Hub) และ browser บนเครื่องนักศึกษา

## โครงสร้างโฟลเดอร์

```text
007_kubernetes_PersistentVolume/
├── README.md                         ← หน้านี้
├── 01_Theory/
│   ├── README.md                     ← เอกสารทฤษฎี
│   └── images/                       ← ภาพประกอบ (+ imagegen-prompts.md)
└── 02_LAB/
    ├── README.md                     ← คู่มือ LAB 0–4
    ├── images/                       ← ภาพประกอบ LAB + screenshots/ ภาพหน้าจอจริง
    ├── labs/                         ← YAML ของ LAB 1–3
    │   ├── lab01-emptydir-vs-pvc/    ← notes-emptydir-pod.yaml, notes-pvc.yaml, notes-pod.yaml
    │   ├── lab02-pv-lifecycle/notes-pvc-typo.yaml
    │   └── lab03-database/           ← db-secret.yaml, db-pvc.yaml, db-deploy.yaml
    └── som-menu/                     ← LAB 4 สมุดออเดอร์ร้านน้องส้มที่ไม่หาย
        ├── app/                      ← เว็บหน้าร้าน Node.js (server.js + Dockerfile) เขียนออเดอร์ลง /data/orders.txt
        └── k8s/                      ← som-orders-pvc.yaml, som-menu-deploy.yaml, som-menu-svc.yaml
```

ใน LAB 0 จะ `git clone` repo เข้า container แล้วทำงานที่ `/workspace/DevTools/05_kubernetes/007_kubernetes_PersistentVolume/02_LAB` ภายใน k8s-lab

## เริ่มเลย

👉 [อ่านทฤษฎี](01_Theory/README.md) → [ลงมือทำ LAB](02_LAB/README.md)

**บทถัดไป:** [บทที่ 8: Kubernetes Ingress — ประตูใหญ่บานเดียว หลายร้าน](../008_kubernetes_Ingress/README.md)
