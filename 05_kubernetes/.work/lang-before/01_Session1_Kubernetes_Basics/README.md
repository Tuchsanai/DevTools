# ครั้งที่ 1 — Kubernetes Basics: ใครคอยทำให้ระบบตรงกับที่เราสั่ง?

ครั้งนี้เริ่มจากปัญหาของ Docker Compose บนเครื่องเดียว แล้วค่อยพบ control plane, worker node,
Pod, YAML, label, ReplicaSet และ Deployment ผ่าน SkillSpace ชั้น web เพียงชั้นเดียว
เป้าหมายคืออธิบาย desired state และ self-healing ได้จากหลักฐาน ไม่ใช่จำคำสั่งสร้าง object

อ่าน manifest ทีละ field ได้จาก [คู่มือ YAML ครั้งที่ 1](./YAML_Guide.md) ซึ่งใช้ตัวอย่างจริงจากแล็บ 001-007

นี่คือจุดเริ่มต้นของชุด จึงยังไม่มีครั้งก่อนหน้าให้ต่อยอด เนื้อหาจะเชื่อมความรู้เดิมเรื่อง
image, container และ Compose ไปสู่คำถามใหม่ว่า “เมื่อมีหลาย node ใครเป็นผู้เฝ้าระบบ?”

## สไลด์ของครั้งนี้

สไลด์ของครั้งนี้คือ [`Kubernetes_Session1_Slides.html`](./Kubernetes_Session1_Slides.html) (81 หน้า) — ดับเบิลคลิกเปิดในเบราว์เซอร์ได้ทันที (file://) ไม่ต้องต่ออินเทอร์เน็ต
เมื่อไฟล์ถูกเพิ่มตามชื่อมาตรฐาน ให้เปิดจากโฟลเดอร์นี้ด้วย browser หรือคำสั่ง:

```bash
xdg-open Kubernetes_Session1_Slides.html
```

ไฟล์ควรเปิดผ่าน `file://` ได้โดยไม่ต้องเปิด web server; หากต้องการภาพรวมทั้งชุด ให้ดู README ระดับชุด

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
| 001 | [`001-kubernetes-introduction/`](./001-kubernetes-introduction/) | จากเครื่องเดียวสู่ผู้ดูแล cluster | สำรวจ API server, control plane/worker และหยุด worker เพื่ออ่านอาการ |
| 002 | [`002-kubectl-and-namespace/`](./002-kubectl-and-namespace/) | kubectl และ Namespace | เทียบ default กับทุก namespace และอ่าน object ผ่าน get/describe/YAML |
| 003 | [`003-pod-the-smallest-unit/`](./003-pod-the-smallest-unit/) | Pod ไม่ใช่ container เดี่ยว | เปิด SkillSpace Pod, อ่าน Events/logs และทดลอง sidecar |
| 004 | [`004-declarative-yaml/`](./004-declarative-yaml/) | Declarative YAML | apply ซ้ำ, diff desired/actual และเปลี่ยน web v1 เป็น v2 |
| 005 | [`005-labels-the-glue/`](./005-labels-the-glue/) | Labels และ selectors | จัดกลุ่ม Pod โดยไม่ผูกกับชื่อหรือ IP แล้วจงใจทำ selector ว่าง |
| 006 | [`006-desired-state-and-self-healing/`](./006-desired-state-and-self-healing/) | Desired state และ self-healing | ลบ Pod ใต้ ReplicaSet แล้วดูตัวแทนเกิดขึ้นพร้อม request ต่อเนื่อง |
| 007 | [`007-deployment-manages-change/`](./007-deployment-manages-change/) | Deployment ดูแลการเปลี่ยนแปลง | scale, rollout, rollback และอ่าน rollout ที่ใช้ image ไม่มีจริง |

## ลำดับที่ควรทำ

เส้นหลักคือ `001 → 002 → 003 → 004 → 005 → 006 → 007` เพราะแต่ละแล็บเพิ่ม abstraction ทีละชั้น

- ถ้า cluster และ image ถูกเตรียมแล้ว ข้าม “ขั้นติดตั้ง” ใน 001 ได้ แต่ไม่ควรข้าม concept control plane/worker
- แล็บ 002 แทรกหลัง 003 ได้หากผู้สอนอยากให้เห็น Pod ก่อน แล้วค่อยย้อนมาอธิบาย namespace
- แล็บ 004–007 ควรทำตามลำดับ: YAML และ label เป็นฐานให้ ReplicaSet/Deployment
- หากเวลาจำกัด ให้สาธิต sidecar ใน 003 แทนการลงมือ แต่ยังต้องตอบได้ว่า container ใน Pod แชร์อะไร

## เตรียมเฉพาะครั้งนี้

หลังเตรียมเครื่องครั้งเดียวตาม README ระดับชุด ให้ตรวจ cluster และ image web ก่อนเริ่ม:

```bash
kubectl get nodes
docker exec devtools-control-plane crictl images | grep k8s-lab-web
kubectl get ns lab002 lab003 lab004 lab005 lab006 lab007 --ignore-not-found
```

LAB 001 สำรวจ resource ระดับ cluster จึงไม่สร้าง namespace; LAB 002 ใช้ `lab002` เพื่อทดลอง
ส่วน LAB 003–007 ใช้ `lab003` ถึง `lab007` ตามลำดับ
ตั้งแต่ LAB 006 คำสั่งในเทอร์มินัลของเครื่องเรียนเรียก Ingress ที่ `http://localhost` (พอร์ต 80)
แต่เบราว์เซอร์บนเครื่องของคุณเปิด `http://localhost:8080`; LAB 003–005 ใช้ port-forward ที่ `http://localhost:3000`

## เก็บกวาดเมื่อจบครั้ง

แต่ละแล็บควรลบ namespace ของตนเองอยู่แล้ว คำสั่งนี้เป็นตาข่ายนิรภัยเมื่อจบทั้งครั้ง:

```bash
kubectl delete ns lab002 lab003 lab004 lab005 lab006 lab007 --ignore-not-found
kubectl get ns lab002 lab003 lab004 lab005 lab006 lab007 --ignore-not-found
```

ผลตรวจบรรทัดสุดท้ายควรไม่แสดง namespace เหล่านี้ หากยังเป็น `Terminating` ให้รอ controller ทำงานจนจบ
ไม่ต้องลบ cluster หากจะเรียนครั้งถัดไป เพราะ image และส่วนประกอบกลางยังใช้ต่อ

## เช็กลิสต์ปิดท้ายครั้ง

- [ ] อธิบายได้ว่า Kubernetes เพิ่มผู้ดูแลอะไรเหนือการรัน container บนเครื่องเดียว
- [ ] อธิบายได้ว่า control plane กับ worker node รับผิดชอบคนละส่วนอย่างไร
- [ ] อธิบายได้ว่า Pod เป็นหน่วย schedule และต่างจาก container อย่างไร
- [ ] อ่าน `apiVersion`, `kind`, `metadata`, `spec` และแยก desired state จาก status ได้
- [ ] อธิบายได้ว่า label/selector เชื่อม object โดยไม่ผูกชื่อหรือ IP อย่างไร
- [ ] ทายได้ว่าเกิดอะไรขึ้นเมื่อลบ Pod เปล่ากับ Pod ใต้ ReplicaSet/Deployment
- [ ] อธิบาย scale, rollout และ rollback โดยอ้างหลักฐานจาก ReplicaSet/Pod ได้

จำภาพเดียวให้ได้: **Deployment ประกาศสภาพที่ต้องการ แล้ว controller คอยลดส่วนต่างระหว่าง desired กับ actual state**
