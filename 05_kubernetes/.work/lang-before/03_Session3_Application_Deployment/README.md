# ครั้งที่ 3 — Application Deployment: ประกอบ เปลี่ยน และวินิจฉัยระบบจริง

ครั้งนี้นำ object ที่เรียนแยกชิ้นมาประกอบเป็น SkillSpace แบบ web-api-db แล้วถามต่อว่า
จะเปิดประตูเดียว อัปเดตโดยผู้ใช้ไม่สะดุด จองทรัพยากรให้ scheduler และหาสาเหตุเมื่อระบบพังอย่างไร
ปลายทางคือการตาม request หนึ่งเส้นจาก browser ผ่าน Ingress/Service/Pod จนถึง PostgreSQL และ PV

อ่าน manifest ทีละ field ได้จาก [`YAML_Guide.md`](./YAML_Guide.md) คู่มือ YAML ประจำครั้งนี้

เนื้อหาต่อยอดจากครั้งที่ 2 ซึ่งมี Service, ConfigMap, Secret, PVC และ probes แล้ว
ครั้งนี้จะมองความสัมพันธ์ทั้งระบบแทนการมอง object เดี่ยว พร้อมใช้ desired state และ Deployment
จากครั้งแรกเป็นกลไก rollout/rollback โดยกล่าวถึงความรู้เดิมเป็นข้อความ ไม่อ้าง path ข้ามโฟลเดอร์

## สไลด์ของครั้งนี้

สไลด์ของครั้งนี้คือ [`Kubernetes_Session3_Slides.html`](./Kubernetes_Session3_Slides.html) (79 หน้า) — ดับเบิลคลิกเปิดในเบราว์เซอร์ได้ทันที (file://) ไม่ต้องต่ออินเทอร์เน็ต
เมื่อไฟล์ถูกเพิ่มตามชื่อมาตรฐาน ให้เปิดจากโฟลเดอร์นี้ด้วย:

```bash
xdg-open Kubernetes_Session3_Slides.html
```

ไฟล์ควรเปิดผ่าน `file://` ได้ทันที; ขั้นเตรียมเครื่องรวมอยู่ใน README ระดับชุด

| ปุ่ม | การทำงาน |
|---|---|
| `←` / `→` | สไลด์ก่อนหน้า / ถัดไป |
| `Space` | สไลด์ถัดไป |
| `PgUp` / `PgDn` | สไลด์ก่อนหน้า / ถัดไป |
| `Home` | ไปหน้าแรก |
| `End` | ไปหน้าสุดท้าย |
| `O` | เปิด overview grid |
| `F` | เปิด/ปิดเต็มจอ |
| `?` | เปิดหน้าช่วยเหลือ |
| `Esc` | ปิด overview หรือหน้าช่วยเหลือ |
| `Ctrl+P` | พิมพ์หรือบันทึก PDF อัตราส่วน 16:9 |

## แล็บทั้ง 7

| แล็บ | โฟลเดอร์ | หัวข้อหลัก | ไฮไลต์ |
|---:|---|---|---|
| 015 | [`015-assembling-a-real-application/`](./015-assembling-a-real-application/) | ประกอบหลาย object เป็นแอป | map manifest กับหน้าที่ แล้วถอด Service/Ingress เพื่ออ่านผลกระทบ |
| 016 | [`016-adding-a-database/`](./016-adding-a-database/) | Stateful ต่างจาก stateless | สร้าง ticket, ลบ db Pod, ตรวจ persistence และทดลอง scale db ผิดวิธี |
| 017 | [`017-ingress-the-front-door/`](./017-ingress-the-front-door/) | Ingress เป็นประตูหน้า | route `/` กับ `/api` ผ่าน URL เดียว และทำ backend Service หาย |
| 018 | [`018-updating-without-downtime/`](./018-updating-without-downtime/) | Rolling update แบบไม่สะดุด | ยิง request ต่อเนื่องระหว่าง v1→v2, ดู ReplicaSet และ rollback |
| 019 | [`019-telling-kubernetes-what-you-need/`](./019-telling-kubernetes-what-you-need/) | Requests, limits และ scheduling | ทำ Pod Pending ด้วย request เกิน และ OOMKilled ด้วย limit ต่ำ |
| 020 | [`020-reading-the-symptoms/`](./020-reading-the-symptoms/) | Troubleshooting ตามอาการ | แยก Pending, ImagePullBackOff, CrashLoopBackOff และ endpoints ว่าง |
| 021 | [`021-the-big-picture/`](./021-the-big-picture/) | ภาพใหญ่และเส้นทาง request | ตาม log จาก Ingress ถึง db แล้วตัด object ทีละชิ้นเพื่อทายอาการ |

## ลำดับที่ควรทำ

เส้นหลักคือ `015 → 016 → 017 → 018 → 019 → 020 → 021`

- 015 เป็นฐานของระบบหลาย object และไม่ควรข้ามก่อนทำแล็บที่เหลือ
- 016 ควรมาก่อน 021 เพื่อแยก stateful data path จาก request path ได้ถูก
- 017 ควรมาก่อน 018 เพราะ request loop ใช้ประตู Ingress เป็นหลักฐานความต่อเนื่อง
- 019 กับ 020 สลับหรือแทรกหลัง 017 ได้; 019 ปูอาการ Pending/OOMKilled ให้ 020 อ่านง่ายขึ้น
- 021 ต้องทำท้ายสุด เพราะเป็น capstone ที่ใช้ mental model จากทุกแล็บ ไม่ใช่ manifest ใหม่อีกชุดหนึ่ง

## เตรียมเฉพาะครั้งนี้

ตรวจ cluster, image, ingress และ metrics-server ก่อนเริ่ม เพราะครั้งนี้ใช้ทั้งหมด:

```bash
kubectl get nodes
docker exec devtools-control-plane crictl images | grep k8s-lab
kubectl -n ingress-nginx get pods
kubectl top nodes
kubectl get ns lab015 lab016 lab017 lab018 lab019 lab020 lab021 --ignore-not-found
```

ครั้งนี้ใช้ namespace `lab015` ถึง `lab021` แยกกัน และเปิดเว็บหลักผ่าน `http://localhost:8080`
คำสั่ง CLI ในเทอร์มินัลของเครื่องเรียนเรียก Ingress ที่ `http://localhost` (พอร์ต 80); เฉพาะเบราว์เซอร์บนเครื่องของคุณจึงใช้ `http://localhost:8080`
ถ้า `kubectl top nodes` ยังไม่มีข้อมูล ให้รอ metrics-server สักครู่แล้วลองใหม่ ไม่ต้องเปลี่ยน manifest
LAB 018 เหมาะกับหลาย terminal สำหรับ request loop, watch และ `stern`; ปิด process เหล่านี้ก่อนเปลี่ยนแล็บ

## เก็บกวาดเมื่อจบครั้ง

```bash
kubectl delete ns lab015 lab016 lab017 lab018 lab019 lab020 lab021 --ignore-not-found
kubectl get ns lab015 lab016 lab017 lab018 lab019 lab020 lab021 --ignore-not-found
```

รอ namespace ที่มี PVC ลบเสร็จ และหยุด request loop/`stern` ที่ค้างอยู่
เมื่อจบทั้งชุดและไม่ต้องเก็บ cluster แล้ว จึงใช้ `k8s-teardown`; อย่ารันระหว่างที่ยังต้องตรวจงาน

## เช็กลิสต์ปิดท้ายครั้ง

- [ ] อธิบายได้ว่า Deployment, Service, ConfigMap, Secret, Ingress และ PVC ประกอบเป็นระบบอย่างไร
- [ ] แยกวิธีดูแล web/api แบบ stateless ออกจาก db แบบ stateful ได้
- [ ] อธิบายได้ว่า Ingress rule ต่างจาก ingress controller และเกี่ยวกับ reverse proxy อย่างไร
- [ ] อธิบายได้ว่า rolling update, readiness และ ReplicaSet ร่วมกันลด downtime อย่างไร
- [ ] แยกผลของ requests ตอน scheduling ออกจาก limits ตอน container รันได้
- [ ] ไล่ตรวจ `get → describe → logs → events` โดยเลือกหลักฐานให้ตรง layer ที่พังได้
- [ ] เล่าเส้นทาง Browser → Ingress → Service → Pod → Service → Pod → db → PVC/PV ได้
- [ ] บอกสิ่งที่ระบบตัวอย่างยังขาดก่อน production เช่น TLS, RBAC, backup และ monitoring ได้

จำภาพเดียวให้ได้: **แอปจริงคือกราฟของ object; เมื่อ request หรือข้อมูลขาดตอน ให้หาว่าเส้นเชื่อมชั้นใดหายก่อนแก้**
