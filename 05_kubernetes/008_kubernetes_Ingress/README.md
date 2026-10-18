# บทที่ 8: Kubernetes Ingress — ประตูใหญ่บานเดียว หลายร้าน

> **รายวิชา:** Software Development Tools and Environments (DevTools)
> **หัวข้อ:** Ingress และ Ingress Controller (Traefik), ติดตั้งด้วย Helm, namespace เบื้องต้น, แยกทางตามชื่อ (host) และทางเดิน (path), กับดัก Prefix และ backend ชื่อผิด, ร้านกับครัวหลังประตูเดียว
> **ผลลัพธ์การเรียนรู้ที่เกี่ยวข้อง:** CLO-5, CLO-6

<p align="center">
  <img src="01_Theory/images/01-opening-too-many-ports.png" alt="ลูกค้าต้องจำเลข port หลายตัวจนสับสน" width="900"><br>
  <em>บทที่แล้วร้านเก็บออเดอร์ได้ไม่หาย แต่ลูกค้ายังต้องจำเลข port และถ้ามีหลายบริการก็ต้องเปิดหลายประตู บทนี้น้องส้มมียามประตูใหญ่ที่อ่านป้าย Ingress แล้วพาลูกค้าไปร้านที่ถูกตามชื่อที่พิมพ์มา</em>
</p>

## บทนี้เรียนอะไร

บทที่ 5 เราเปิดร้านสู่ภายนอกด้วย Service แบบ NodePort ทุกแอปที่อยากให้ลูกค้าเข้าได้ต้องมีประตู (port) ของตัวเอง บทนี้ใช้ **Ingress** เป็นป้ายกฎว่า **ชื่อไหน / ทางเดินไหน ไปที่ Service ไหน** และ **Ingress Controller** (บทนี้ใช้ **Traefik** ติดตั้งด้วย **Helm**) เป็นยามที่ยืนประตูใหญ่บานเดียว อ่านป้ายแล้วพาลูกค้าไปให้ถูก แอปทุกตัวกลับไปใช้ Service แบบ ClusterIP ข้างในท่า ปิดท้ายด้วย **ร้านอาหารแมวน้องส้มกับครัว** ที่ลูกค้าเข้า `http://shop.localhost:30080` และพ่อครัวเข้า `http://kitchen.localhost:30080` ผ่านประตูเดียวกัน ใช้สมุดออเดอร์เล่มเดียวกัน

| ส่วน | เนื้อหา | ลิงก์ |
|---|---|---|
| 📖 **ทฤษฎี** | Ingress คืออะไร, Ingress กับ Ingress Controller, Helm, namespace เบื้องต้น, อ่าน YAML ของ Ingress ทีละบรรทัด, เส้นทางของคำขอ, แยกตาม host, แยกตาม path และกับดัก Prefix, backend ชื่อผิด, แอปเป็น ClusterIP หลังประตูเดียว, YAML ร้านน้องส้ม และปูทางไป Helm ของร้านเอง (มีคำถามทบทวนพร้อมแนวคำตอบ) | [01_Theory/README.md](01_Theory/README.md) |
| 🧪 **ปฏิบัติการ** | LAB 0–4: สร้างคลัสเตอร์ → ติดตั้ง Traefik ด้วย Helm → แยกทางตามชื่อ → แยกทางตามทางเดิน → **LAB สุดท้าย: ร้านน้องส้มกับครัว ประตูเดียวสองชื่อ** พร้อมสรุปคำสั่งท้ายบท | [02_LAB/README.md](02_LAB/README.md) |

## คำแนะนำในการเรียน

1. **อ่านทฤษฎีก่อน** อย่างน้อยหัวข้อ 1–6 แล้วเริ่ม LAB 0–1 ได้เลย
2. ก่อนทำ LAB 2–4 ให้อ่านหัวข้อ 7–12 (เส้นทางของคำขอ, host, path, backend ชื่อผิด, ClusterIP หลังประตูเดียว, YAML ร้านน้องส้ม)
3. ทำ LAB **ตามลำดับ** Traefik ที่ติดตั้งใน LAB 1 ใช้ต่อจนจบบท ใช้เวลารวมประมาณ 2.5–3 ชั่วโมง
4. สังเกตสัญลักษณ์ในเอกสาร LAB ว่าคำสั่งรันที่ไหน: 🖥️ บนเครื่องนักศึกษา / 🐧 ใน SSH session ของ k8s-lab / 🌐 browser
5. ผลลัพธ์ในเอกสารมาจากการทดลองจริง (Kubernetes v1.37.0, Helm v4.3.0, Traefik v3.7.14) แต่ **ชื่อ Pod ถูกสุ่มทุกครั้ง** และ Pod ที่ตอบแต่ละครั้งอาจต่างจากในเอกสาร
6. ลองตอบคำถามทบทวนด้วยตัวเองก่อนเปิดดูแนวคำตอบ

> **ขอบเขตของบทนี้:** Ingress แบบ HTTP แยกตามชื่อและทางเดิน โดยใช้ Traefik เป็น Ingress Controller (โปรเจกต์ ingress-nginx เลิกพัฒนาแล้ว) ชื่อ `*.localhost` ใช้ได้เลยไม่ต้องตั้ง DNS ส่วน HTTPS / ใบรับรอง และ Gateway API ไม่อยู่ในบทนี้ การทำแพ็กเกจ Helm ของร้านเองเป็น **เนื้อหาของบทถัดไป**

## สิ่งที่ต้องมีก่อนเริ่ม

- ผ่าน [บทที่ 7: Kubernetes PersistentVolume](../007_kubernetes_PersistentVolume/README.md) แล้ว และเข้าใจ Service แบบ ClusterIP / NodePort จาก [บทที่ 5](../005_kubernetes_Service/README.md)
- container **`k8s-lab`** ที่สร้างด้วย **`-p 30080-30082:30080-30082`** (LAB 0) ภายในมี `helm` ให้แล้ว
- เครื่องต่ออินเทอร์เน็ตได้ (ดึง Helm chart และ image จากอินเทอร์เน็ต) และ browser บนเครื่องนักศึกษา

## โครงสร้างโฟลเดอร์

```text
008_kubernetes_Ingress/
├── README.md                         ← หน้านี้
├── 01_Theory/
│   ├── README.md                     ← เอกสารทฤษฎี
│   └── images/                       ← ภาพประกอบ (+ imagegen-prompts.md)
└── 02_LAB/
    ├── README.md                     ← คู่มือ LAB 0–4
    ├── images/                       ← ภาพประกอบ LAB + screenshots/ ภาพหน้าจอจริง
    ├── labs/                         ← ไฟล์ของ LAB 1–3
    │   ├── lab01-controller/traefik-values.yaml
    │   ├── lab02-host/               ← menu-app.yaml, drink-app.yaml, shop-ingress-host.yaml
    │   └── lab03-path/               ← shop-ingress-path.yaml, shop-ingress-typo.yaml
    └── som-menu/                     ← LAB 4 ร้านน้องส้มกับครัว ประตูเดียวสองชื่อ
        ├── app/                      ← Node.js (server.js + Dockerfile) image เดียว 2 โหมด: shop / kitchen
        └── k8s/                      ← som-orders-pvc.yaml, som-menu.yaml, som-kitchen.yaml, som-ingress.yaml
```

ใน LAB 0 จะ `git clone` repo เข้า container แล้วทำงานที่ `/workspace/DevTools/05_kubernetes/008_kubernetes_Ingress/02_LAB` ภายใน k8s-lab

## เริ่มเลย

👉 [อ่านทฤษฎี](01_Theory/README.md) → [ลงมือทำ LAB](02_LAB/README.md)

**บทถัดไป:** [บทที่ 9: Helm Chart — ร้านน้องส้มในกล่องเดียว](../009_kubernetes_Helm/README.md)
