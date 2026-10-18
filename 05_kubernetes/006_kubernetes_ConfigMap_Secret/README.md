# บทที่ 6: Kubernetes ConfigMap และ Secret — เปลี่ยนป้ายร้านโดยไม่ต้อง build ใหม่

> **รายวิชา:** Software Development Tools and Environments (DevTools)
> **หัวข้อ:** ConfigMap, Secret, ใช้เป็นตัวแปร env (`configMapKeyRef` / `envFrom` / `secretKeyRef`), ใช้เป็นไฟล์ผ่าน volume, ค่าที่อัปเดตเองกับค่าที่ต้อง restart, base64 ไม่ใช่การเข้ารหัส และ `kubectl rollout restart`
> **ผลลัพธ์การเรียนรู้ที่เกี่ยวข้อง:** CLO-5, CLO-6

<p align="center">
  <img src="01_Theory/images/01-opening-rebuild-to-change-sign.png" alt="น้องส้มต้อง build image ใหม่ทุกครั้งที่เปลี่ยนป้ายร้าน" width="900"><br>
  <em>บทที่แล้วร้านมีที่อยู่เดียวแล้ว แต่ชื่อร้าน ประกาศ และเมนูยังฝังอยู่ใน image หรือเขียนไว้ใน YAML ของ Deployment เปลี่ยนทีไรต้อง build ใหม่ บทนี้น้องส้มย้ายค่าตั้งค่าไปไว้ในแฟ้มคู่มือ ConfigMap และย้ายรหัสผ่านไปไว้ในซองปิดผนึก Secret</em>
</p>

## บทนี้เรียนอะไร

ตั้งแต่บทที่ 2 เราเขียนค่าตั้งค่าไว้ใน YAML หรือฝังไว้ใน image ตอน build (ชื่อร้าน, เวอร์ชัน, รหัสฐานข้อมูล) บทนี้แยกค่าเหล่านั้นออกมาเป็น object ของ Kubernetes เอง **ConfigMap** เก็บค่าตั้งค่าทั่วไป และ **Secret** เก็บรหัสผ่าน ทั้งสองอย่างส่งเข้า Pod ได้ **2 แบบ** คือเป็นตัวแปร env (อ่านครั้งเดียวตอน container เริ่ม) หรือเป็นไฟล์ (อัปเดตเองเมื่อแก้) ปิดท้ายด้วย **ร้านอาหารแมวน้องส้ม** ที่ image ไม่มีค่าอะไรฝังเลย แก้เมนูแล้วหน้าเว็บเปลี่ยนเองใน 1 นาที แก้ประกาศแล้วสั่ง `rollout restart` และมีหน้าหลังร้านที่ใช้รหัสจาก Secret

| ส่วน | เนื้อหา | ลิงก์ |
|---|---|---|
| 📖 **ทฤษฎี** | ทำไมต้องแยกค่าตั้งค่าออกจาก image, ConfigMap และ YAML ทีละบรรทัด, env แบบ `configMapKeyRef` / `envFrom`, กับดัก `CreateContainerConfigError`, ConfigMap เป็นไฟล์, env vs ไฟล์, Secret และ base64, Secret ปลอดภัยแค่ไหน, `kubectl rollout restart` และปูทางไป PersistentVolume (มีคำถามทบทวนพร้อมแนวคำตอบ) | [01_Theory/README.md](01_Theory/README.md) |
| 🧪 **ปฏิบัติการ** | LAB 0–4: สร้างคลัสเตอร์ → ConfigMap เป็น env → ConfigMap เป็นไฟล์ → Secret → **LAB สุดท้าย: ร้านอาหารแมวน้องส้มเปลี่ยนป้ายโดยไม่ต้อง build ใหม่** พร้อมสรุปคำสั่งท้ายบท | [02_LAB/README.md](02_LAB/README.md) |

## คำแนะนำในการเรียน

1. **อ่านทฤษฎีก่อน** อย่างน้อยหัวข้อ 1–6 แล้วเริ่ม LAB 0–1 ได้เลย
2. ก่อนทำ LAB 2–4 ให้อ่านหัวข้อ 7–12 (ConfigMap เป็นไฟล์, env vs ไฟล์, Secret, `rollout restart`, YAML ร้านน้องส้ม)
3. ทำ LAB **ตามลำดับ** ใช้เวลารวมประมาณ 2.5–3 ชั่วโมง (มีช่วงรอให้ไฟล์จาก ConfigMap อัปเดตราว 1 นาที)
4. สังเกตสัญลักษณ์ในเอกสาร LAB ว่าคำสั่งรันที่ไหน: 🖥️ บนเครื่องนักศึกษา / 🐧 ใน SSH session ของ k8s-lab / 🌐 browser
5. ผลลัพธ์ในเอกสารมาจากการทดลองจริง (Kubernetes v1.37.0) แต่ **ชื่อ Pod ถูกสุ่มทุกครั้ง** และเวลาที่ไฟล์อัปเดตอาจเร็วหรือช้ากว่าในเอกสารเล็กน้อย
6. ลองตอบคำถามทบทวนด้วยตัวเองก่อนเปิดดูแนวคำตอบ

> **ขอบเขตของบทนี้:** ใช้ ConfigMap และ Secret แบบ env และแบบไฟล์ กับ Pod / Deployment / Service จากบทก่อน รหัสผ่านในไฟล์ LAB เป็น **รหัสตัวอย่างเพื่อการเรียนเท่านั้น** งานจริงห้าม commit Secret ขึ้น Git ส่วนการเก็บข้อมูลไม่ให้หายเมื่อ Pod ถูกสร้างใหม่ (PersistentVolume) เป็น **เนื้อหาของบทถัดไป**

## สิ่งที่ต้องมีก่อนเริ่ม

- ผ่าน [บทที่ 5: Kubernetes Service](../005_kubernetes_Service/README.md) แล้ว เปิดแอปผ่าน NodePort `http://localhost:30080` ได้
- container **`k8s-lab`** ที่สร้างด้วย **`-p 30080-30082:30080-30082`** (LAB 0)
- เครื่องต่ออินเทอร์เน็ตได้ (ดึง image จาก Docker Hub) และ browser บนเครื่องนักศึกษา

## โครงสร้างโฟลเดอร์

```text
006_kubernetes_ConfigMap_Secret/
├── README.md                         ← หน้านี้
├── 01_Theory/
│   ├── README.md                     ← เอกสารทฤษฎี
│   └── images/                       ← ภาพประกอบ (+ imagegen-prompts.md)
└── 02_LAB/
    ├── README.md                     ← คู่มือ LAB 0–4
    ├── images/                       ← ภาพประกอบ LAB + screenshots/ ภาพหน้าจอจริง
    ├── labs/                         ← YAML ของ LAB 1–3
    │   ├── lab01-configmap-env/      ← shop-config.yaml, shop-config-v2.yaml, config-pod.yaml
    │   ├── lab02-configmap-file/     ← web-page.yaml, web-page-v2.yaml, web-deploy.yaml
    │   └── lab03-secret/             ← admin-secret.yaml, secret-pod.yaml
    └── som-menu/                     ← LAB 4 ร้านอาหารแมวน้องส้มเปลี่ยนป้ายโดยไม่ต้อง build ใหม่
        ├── app/                      ← เว็บหน้าร้าน Node.js (server.js + Dockerfile) ไม่มีค่าตั้งค่าฝังใน image
        └── k8s/                      ← som-menu-config(-v2).yaml, som-menu-secret.yaml, som-menu-deploy.yaml, som-menu-svc.yaml
```

ใน LAB 0 จะ `git clone` repo เข้า container แล้วทำงานที่ `/workspace/DevTools/05_kubernetes/006_kubernetes_ConfigMap_Secret/02_LAB` ภายใน k8s-lab

## เริ่มเลย

👉 [อ่านทฤษฎี](01_Theory/README.md) → [ลงมือทำ LAB](02_LAB/README.md)

**บทถัดไป:** [บทที่ 7: Kubernetes PersistentVolume — สมุดออเดอร์ที่ไม่หาย](../007_kubernetes_PersistentVolume/README.md)
