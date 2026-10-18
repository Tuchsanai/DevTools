# บทที่ 4: Kubernetes Deployment — เปลี่ยนเมนูโดยร้านไม่ปิด

> **รายวิชา:** Software Development Tools and Environments (DevTools)
> **หัวข้อ:** Kubernetes Deployment, Deployment → ReplicaSet → Pod, rolling update, maxSurge / maxUnavailable, rollout status / history / undo และการเปลี่ยนเวอร์ชันร้านโดยไม่ปิดร้าน
> **ผลลัพธ์การเรียนรู้ที่เกี่ยวข้อง:** CLO-5, CLO-6

<p align="center">
  <img src="01_Theory/images/01-opening-menu-change-closed.png" alt="น้องส้มเปลี่ยนเมนูทีไร ร้านปิดทุกที" width="900"><br>
  <em>บทที่แล้วเปลี่ยนเมนูทีไรต้องลบ Pod เก่าเองจนร้านปิดชั่วครู่ บทนี้น้องส้มมีผู้จัดการลูกเรือ Deployment คอยทยอยเปลี่ยนกล่องทีละใบ ร้านจึงเปิดอยู่ตลอด</em>
</p>

## บทนี้เรียนอะไร

บทที่ 3 ReplicaSet ดูแลจำนวน Pod ได้ แต่พอแก้แม่พิมพ์เป็นรุ่นใหม่ ต้องลบ Pod เก่าเองและร้านปิดไปชั่วครู่ บทนี้ใช้ **Deployment** ซึ่งสร้าง ReplicaSet ให้อีกชั้น แล้ว **ทยอยเปลี่ยน Pod ทีละตัว (rolling update)** จดประวัติทุกรุ่น และ **ย้อนกลับได้ในคำสั่งเดียว** (rollback) ปิดท้ายด้วย **ร้านอาหารแมวน้องส้ม** ที่เปลี่ยนจากเมนู 1.0 เป็น 2.0 แล้วย้อนกลับ โดยร้านไม่ปิดเลย

| ส่วน | เนื้อหา | ลิงก์ |
|---|---|---|
| 📖 **ทฤษฎี** | Deployment คืออะไร, 3 ชั้น Deployment → ReplicaSet → Pod, อ่าน YAML ทีละบรรทัด, ชื่อ Pod 3 ท่อนและเจ้าของ 2 ชั้น, ใครดูแลอะไร, rolling update, maxSurge / maxUnavailable / minReadySeconds, rollout status / history / undo, อัปเดตพังแต่ร้านไม่ปิด และปูทางไป Service (มีคำถามทบทวนพร้อมแนวคำตอบ) | [01_Theory/README.md](01_Theory/README.md) |
| 🧪 **ปฏิบัติการ** | LAB 0–4: สร้างคลัสเตอร์ → Deployment แรก → rolling update + rollback → อัปเดตพังแต่ร้านไม่ปิด → **LAB สุดท้าย: ร้านอาหารแมวน้องส้มเปลี่ยนเมนูโดยไม่ปิดร้าน** พร้อมสรุปคำสั่ง kubectl ท้ายบท | [02_LAB/README.md](02_LAB/README.md) |

## คำแนะนำในการเรียน

1. **อ่านทฤษฎีก่อน** อย่างน้อยหัวข้อ 1–6 แล้วเริ่ม LAB 0–1 ได้เลย
2. ก่อนทำ LAB 2–4 ให้อ่านหัวข้อ 7–13 (rolling update, maxSurge / maxUnavailable, rollout, rollback, อัปเดตพัง, YAML ร้านน้องส้ม, port-forward)
3. ทำ LAB **ตามลำดับ** ใช้เวลารวมประมาณ 2.5–3 ชั่วโมง
4. สังเกตสัญลักษณ์ในเอกสาร LAB ว่าคำสั่งรันที่ไหน: 🖥️ บนเครื่องนักศึกษา / 🐧 ใน SSH session ของ k8s-lab / 🌐 browser
5. ผลลัพธ์ในเอกสารมาจากการทดลองจริง (Kubernetes v1.37.0) แต่ **ชื่อ ReplicaSet และ Pod ถูกสุ่มทุกครั้ง** และเวลา, IP, ชื่อ Node อาจต่างจากเครื่องของนักศึกษา
6. ลองตอบคำถามทบทวนด้วยตัวเองก่อนเปิดดูแนวคำตอบ

> **ขอบเขตของบทนี้:** ใช้ **Deployment, ReplicaSet และ Pod** การเปิดเว็บยังใช้ `kubectl port-forward` ร่วมกับแท็บ PORTS ของ VS Code ส่วน Service เป็น **เนื้อหาของบทถัดไป**

## สิ่งที่ต้องมีก่อนเริ่ม

- ผ่าน [บทที่ 3: Kubernetes ReplicaSet](../003_kubernetes_Replicaset/README.md) แล้ว อ่าน YAML ของ ReplicaSet ได้ (`replicas` / `selector` / `template`) และรู้ว่า ReplicaSet นับ Pod จากป้าย
- มี container **`k8s-lab`** (หรือสร้างใหม่ใน LAB 0) ล็อกอินได้ด้วย `ssh -p 2223 root@localhost` (รหัส `passwd` ใช้เพื่อการเรียนเท่านั้น)
- VS Code + extension Container Tools และ Dev Containers (ใช้ใน LAB 4)
- เครื่องต่ออินเทอร์เน็ตได้ (ดึง image จาก Docker Hub)

## โครงสร้างโฟลเดอร์

```text
004_kubernetes_Deployment/
├── README.md                         ← หน้านี้
├── 01_Theory/
│   ├── README.md                     ← เอกสารทฤษฎี
│   └── images/                       ← ภาพประกอบ (+ imagegen-prompts.md)
└── 02_LAB/
    ├── README.md                     ← คู่มือ LAB 0–4
    ├── images/                       ← ภาพประกอบ LAB + screenshots/ ภาพหน้าจอจริง
    ├── labs/                         ← YAML ของ LAB 1–3
    │   ├── lab01-first-deploy/web-deploy.yaml
    │   ├── lab02-rolling-update/web-deploy-v2.yaml
    │   └── lab03-bad-update/web-deploy-bad.yaml
    └── som-menu/                     ← LAB 4 ร้านอาหารแมวน้องส้มเปลี่ยนเมนูโดยไม่ปิดร้าน
        ├── app/                      ← เว็บหน้าร้าน Node.js (server.js + Dockerfile)
        └── k8s/                      ← som-menu-deploy.yaml (v1.0) และ som-menu-deploy-v2.yaml (v2.0)
```

ใน LAB 0 จะ `git clone` repo เข้า container แล้วทำงานที่ `/workspace/DevTools/05_kubernetes/004_kubernetes_Deployment/02_LAB` ภายใน k8s-lab

## เริ่มเลย

👉 [อ่านทฤษฎี](01_Theory/README.md) → [ลงมือทำ LAB](02_LAB/README.md)

**บทถัดไป:** [บทที่ 5: Kubernetes Service — ที่อยู่เดียวของร้านน้องส้ม](../005_kubernetes_Service/README.md)
