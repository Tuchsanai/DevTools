# ครั้งที่ 3 — Application Deployment: ประกอบ เปลี่ยน และวินิจฉัยระบบจริง

การสอนครั้งนี้นำ object ที่ศึกษาแยกส่วนมาประกอบเป็นระบบ SkillSpace แบบ web-api-db และพิจารณาประเด็นต่อเนื่อง ได้แก่
การกำหนดทางเข้าเพียงจุดเดียว การอัปเดตโดยไม่กระทบผู้ใช้ การจัดสรรทรัพยากรแก่ scheduler และการวินิจฉัยความขัดข้องของระบบ
ผลลัพธ์ปลายทางคือความสามารถในการติดตาม request หนึ่งเส้นทางจาก browser ผ่าน Ingress/Service/Pod จนถึง PostgreSQL และ PV

ผู้เรียนสามารถศึกษารายละเอียดของ manifest แยกตาม field ได้จาก [`YAML_Guide.md`](./YAML_Guide.md) ซึ่งเป็นคู่มือ YAML ประจำการสอนครั้งนี้

เนื้อหานี้ต่อยอดจากการสอนครั้งที่ 2 ซึ่งครอบคลุม Service, ConfigMap, Secret, PVC และ probes แล้ว
การสอนครั้งนี้พิจารณาความสัมพันธ์ของระบบโดยรวมแทน object เดี่ยว พร้อมทั้งประยุกต์สภาพที่ต้องการ (desired state) และ Deployment
จากการสอนครั้งแรกเป็นกลไก rollout/rollback โดยกล่าวทบทวนความรู้เดิมเป็นข้อความและไม่อ้าง path ข้ามโฟลเดอร์

## สไลด์ของครั้งนี้

สไลด์สำหรับการสอนครั้งนี้คือ [`Kubernetes_Session3_Slides.html`](./Kubernetes_Session3_Slides.html) (90 หน้า) — สามารถเปิดในเบราว์เซอร์ผ่านการดับเบิลคลิกได้ทันที (file://) โดยไม่ต้องเชื่อมต่ออินเทอร์เน็ต
เมื่อมีไฟล์ตามชื่อมาตรฐานแล้ว ให้เปิดจากโฟลเดอร์นี้ด้วยคำสั่งต่อไปนี้:

```bash
xdg-open Kubernetes_Session3_Slides.html
```

ไฟล์ต้องสามารถเปิดผ่าน `file://` ได้ทันที โดยขั้นตอนการเตรียมเครื่องระบุไว้ใน README ระดับชุด

| ปุ่ม | การทำงาน |
|---|---|
| `←` / `→` | สไลด์ก่อนหน้า / ถัดไป |
| `Space` | สไลด์ถัดไป |
| `PgUp` / `PgDn` | สไลด์ก่อนหน้า / ถัดไป |
| `Home` | ไปหน้าแรก |
| `End` | ไปหน้าสุดท้าย |
| `O` | เปิดมุมมองภาพรวมแบบตาราง |
| `F` | เปิด/ปิดเต็มจอ |
| `?` | เปิดหน้าช่วยเหลือ |
| `Esc` | ปิด overview หรือหน้าช่วยเหลือ |
| `Ctrl+P` | พิมพ์หรือบันทึก PDF อัตราส่วน 16:9 |

## ปฏิบัติการทั้ง 7

| ปฏิบัติการ | โฟลเดอร์ | หัวข้อหลัก | ประเด็นสำคัญ |
|---:|---|---|---|
| 015 | [`015-assembling-a-real-application/`](./015-assembling-a-real-application/) | การประกอบหลาย object เป็นแอปพลิเคชัน | จับคู่ manifest กับหน้าที่ และถอด Service/Ingress เพื่อวิเคราะห์ผลกระทบ |
| 016 | [`016-adding-a-database/`](./016-adding-a-database/) | ความแตกต่างระหว่าง stateful กับ stateless | สร้าง ticket ลบ db Pod ตรวจสอบ persistence และทดลอง scale db ด้วยวิธีที่ไม่เหมาะสม |
| 017 | [`017-ingress-the-front-door/`](./017-ingress-the-front-door/) | Ingress ในฐานะทางเข้าหลัก | กำหนดเส้นทาง `/` กับ `/api` ผ่าน URL เดียว และจำลองการไม่มี backend Service |
| 018 | [`018-updating-without-downtime/`](./018-updating-without-downtime/) | Rolling update โดยไม่หยุดให้บริการ | ส่ง request อย่างต่อเนื่องระหว่าง v1→v2 ตรวจสอบ ReplicaSet และดำเนินการ rollback |
| 019 | [`019-telling-kubernetes-what-you-need/`](./019-telling-kubernetes-what-you-need/) | Requests, limits และ scheduling | ทำให้ Pod อยู่ในสถานะ Pending ด้วย request ที่สูงเกินไป และเกิด OOMKilled ด้วย limit ที่ต่ำเกินไป |
| 020 | [`020-reading-the-symptoms/`](./020-reading-the-symptoms/) | การวินิจฉัยตามอาการ | จำแนก Pending, ImagePullBackOff, CrashLoopBackOff และ endpoints ว่าง |
| 021 | [`021-the-big-picture/`](./021-the-big-picture/) | ภาพรวมและเส้นทาง request | ติดตาม log จาก Ingress ถึง db และถอด object ทีละรายการเพื่อคาดการณ์อาการ |

## ลำดับที่ควรทำ

เส้นหลักคือ `015 → 016 → 017 → 018 → 019 → 020 → 021`

- 015 เป็นพื้นฐานของระบบหลาย object และควรดำเนินการก่อนปฏิบัติการที่เหลือ
- 016 ควรมาก่อน 021 เพื่อแยก stateful data path จาก request path ได้อย่างถูกต้อง
- 017 ควรมาก่อน 018 เพราะ request loop ใช้ประตู Ingress เป็นหลักฐานความต่อเนื่อง
- 019 กับ 020 สามารถสลับลำดับหรือดำเนินการหลัง 017 ได้ โดย 019 ปูพื้นฐานเกี่ยวกับอาการ Pending/OOMKilled เพื่อสนับสนุนการวิเคราะห์ใน 020
- 021 ต้องดำเนินการเป็นลำดับสุดท้าย เนื่องจากเป็น capstone ที่ประยุกต์ mental model จากทุกปฏิบัติการ มิใช่ manifest ชุดใหม่

## การเตรียมสภาพแวดล้อมเฉพาะการสอนครั้งนี้

ให้ตรวจสอบ cluster, image, ingress และ metrics-server ก่อนเริ่ม เนื่องจากการสอนครั้งนี้ใช้องค์ประกอบทั้งหมดดังกล่าว:

```bash
kubectl get nodes
docker exec devtools-control-plane crictl images | grep k8s-lab
kubectl -n ingress-nginx get pods
kubectl top nodes
kubectl get ns lab015 lab016 lab017 lab018 lab019 lab020 lab021 --ignore-not-found
```

การสอนครั้งนี้ใช้ namespace `lab015` ถึง `lab021` แยกจากกัน และเปิดเว็บหลักผ่าน `http://localhost:8080`
คำสั่ง CLI ในเทอร์มินัลของเครื่องเรียนเรียก Ingress ที่ `http://localhost` (พอร์ต 80) ส่วนเบราว์เซอร์บนเครื่องของผู้เรียนใช้ `http://localhost:8080`
หาก `kubectl top nodes` ยังไม่มีข้อมูล ให้รอ metrics-server ชั่วระยะหนึ่งแล้วดำเนินการอีกครั้ง โดยไม่ต้องเปลี่ยน manifest
LAB 018 ควรเปิดหน้าต่าง terminal หลายหน้าต่างสำหรับ request loop, watch และ `stern` และต้องปิด process เหล่านี้ก่อนเปลี่ยนปฏิบัติการ

## การล้างทรัพยากรเมื่อสิ้นสุดการสอนครั้งนี้

```bash
kubectl delete ns lab015 lab016 lab017 lab018 lab019 lab020 lab021 --ignore-not-found
kubectl get ns lab015 lab016 lab017 lab018 lab019 lab020 lab021 --ignore-not-found
```

ให้รอจนการลบ namespace ที่มี PVC เสร็จสมบูรณ์ และหยุด request loop/`stern` ที่ยังทำงานอยู่
เมื่อดำเนินการครบทั้งชุดและไม่จำเป็นต้องคง cluster ไว้แล้ว จึงใช้ `k8s-teardown` โดยห้ามเรียกใช้งานระหว่างการตรวจผลงาน

## รายการตรวจสอบเมื่อสิ้นสุดการสอนครั้งนี้

- [ ] อธิบายได้ว่า Deployment, Service, ConfigMap, Secret, Ingress และ PVC ประกอบเป็นระบบอย่างไร
- [ ] แยกวิธีดูแล web/api แบบ stateless ออกจาก db แบบ stateful ได้
- [ ] อธิบายได้ว่า Ingress rule ต่างจาก ingress controller และเกี่ยวกับ reverse proxy อย่างไร
- [ ] อธิบายได้ว่า rolling update, readiness และ ReplicaSet ร่วมกันลด downtime อย่างไร
- [ ] แยกผลของ requests ระหว่าง scheduling ออกจาก limits ระหว่าง container ทำงานได้
- [ ] ตรวจสอบตามลำดับ `get → describe → logs → events` โดยเลือกหลักฐานให้สอดคล้องกับชั้นของระบบที่ขัดข้องได้
- [ ] อธิบายเส้นทาง Browser → Ingress → Service → Pod → Service → Pod → db → PVC/PV ได้
- [ ] บอกสิ่งที่ระบบตัวอย่างยังขาดก่อน production เช่น TLS, RBAC, backup และ monitoring ได้

ภาพรวมที่ควรจดจำ: **แอปพลิเคชันจริงเป็นกราฟของ object เมื่อ request หรือข้อมูลขาดช่วง ต้องระบุเส้นเชื่อมของชั้นที่สูญหายก่อนดำเนินการแก้ไข**
