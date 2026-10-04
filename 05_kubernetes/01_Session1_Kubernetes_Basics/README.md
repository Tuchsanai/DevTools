# ครั้งที่ 1 — Kubernetes Basics: กลไกการรักษาสภาพของระบบให้สอดคล้องกับข้อกำหนด

การสอนครั้งนี้เริ่มจากข้อจำกัดของ Docker Compose บนเครื่องเดียว จากนั้นจึงศึกษาสถาปัตยกรรม control plane, etcd, worker node,
Pod, YAML, label, ReplicaSet และ Deployment ผ่าน SkillSpace เฉพาะชั้น web
เป้าหมายคือการอธิบายสภาพที่ต้องการ (desired state) และ self-healing จากหลักฐาน แทนการจดจำคำสั่งสร้าง object

ผู้เรียนสามารถศึกษา manifest ทีละ field ได้จาก [คู่มือ YAML ครั้งที่ 1](./YAML_Guide.md) ซึ่งใช้ตัวอย่างจริงจากปฏิบัติการ 001-007

เนื้อหานี้เป็นจุดเริ่มต้นของชุดวิชา จึงยังไม่มีการสอนครั้งก่อนหน้าสำหรับเชื่อมโยง เนื้อหาจะเชื่อมความรู้เดิมเรื่อง
image, container และ Compose ไปสู่การพิจารณากลไกที่ทำหน้าที่กำกับระบบเมื่อมีหลาย node

## สไลด์ของครั้งนี้

สไลด์สำหรับการสอนครั้งนี้คือ [`Kubernetes_Session1_Slides.html`](./Kubernetes_Session1_Slides.html) (126 หน้า) — สามารถเปิดในเว็บเบราว์เซอร์ได้โดยตรง (file://) โดยไม่ต้องเชื่อมต่ออินเทอร์เน็ต
เมื่อมีไฟล์ตามชื่อมาตรฐานแล้ว ให้เปิดจากโฟลเดอร์นี้ด้วยเว็บเบราว์เซอร์หรือคำสั่งต่อไปนี้:

```bash
xdg-open Kubernetes_Session1_Slides.html
```

ไฟล์สามารถเปิดผ่าน `file://` ด้วยเว็บเบราว์เซอร์ได้โดยไม่ต้องเปิด web server; หากต้องการศึกษาภาพรวมทั้งชุด ให้พิจารณา README ระดับชุด

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

## เนื้อหาสถาปัตยกรรมที่ขยายเพิ่มเติม

สไลด์ส่วนทฤษฎีขยายอยู่หลังภาพรวม LAB 001 และมีทางลัด “Kubernetes Architecture” ในสารบัญและมุมมอง `O`
คำศัพท์ใช้ชื่อทางวิชาการภาษาอังกฤษควบคู่กับคำอธิบายภาษาไทย พร้อมลิงก์เอกสารทางการท้ายสไลด์

- Control plane: kube-apiserver, authentication/authorization/admission, scheduler และ controller-manager
- etcd: ขอบเขตข้อมูล, Raft consensus, quorum, revision/MVCC/watch, snapshot และการกู้คืน
- Node: kubelet, CRI/runtime, CNI, kube-proxy, CoreDNS และบทบาทของ CSI/ส่วนต่อขยาย
- ลำดับจาก `kubectl apply` ไปสู่ Pod ที่พร้อมใช้งาน, self-healing, Node heartbeat และการวิเคราะห์ปัญหาตามองค์ประกอบ
- High availability, stacked/external etcd และข้อจำกัดของ kind ที่มี control plane/etcd เพียงหนึ่งสมาชิก

มีเนื้อหาขยายใน LAB ที่เกี่ยวข้องเรื่อง Namespace/RBAC, Pod lifecycle/probes, requests/limits,
ความสัมพันธ์ spec/status, labels/ownership และข้อจำกัดของ rollout/rollback
ท้ายชุดมีอภิธานศัพท์สำหรับทบทวน; คำถามในส่วนสถาปัตยกรรมคลิกเพื่อเปิดเฉลยได้ และแสดงเฉลยเมื่อพิมพ์

เนื้อหาและแผนภาพใหม่เปิดได้โดยไม่เชื่อมต่ออินเทอร์เน็ต ส่วนลิงก์เอกสารอ้างอิงต้องใช้อินเทอร์เน็ต
เวอร์ชันและตัวอย่างผลลัพธ์ของ LAB อ้างอิงชุดการสอนเดิม ให้ตรวจค่าจริงหลัง `k8s-bootstrap`

## ปฏิบัติการทั้ง 7

| ปฏิบัติการ | โฟลเดอร์ | หัวข้อหลัก | ประเด็นสำคัญ |
|---:|---|---|---|
| 001 | [`001-kubernetes-introduction/`](./001-kubernetes-introduction/) | จากเครื่องเดียวสู่กลไกกำกับดูแล cluster | สำรวจ API server, control plane/worker และหยุด worker เพื่อวิเคราะห์สถานะ |
| 002 | [`002-kubectl-and-namespace/`](./002-kubectl-and-namespace/) | kubectl และ Namespace | เปรียบเทียบ default กับทุก namespace และอ่าน object ผ่าน get/describe/YAML |
| 003 | [`003-pod-the-smallest-unit/`](./003-pod-the-smallest-unit/) | Pod ไม่ใช่ container เดี่ยว | เปิด SkillSpace Pod, อ่าน Events/logs และทดลอง sidecar |
| 004 | [`004-declarative-yaml/`](./004-declarative-yaml/) | Declarative YAML | apply ซ้ำ เปรียบเทียบสภาพที่ต้องการกับสภาพจริง (actual state) และเปลี่ยน web v1 เป็น v2 |
| 005 | [`005-labels-the-glue/`](./005-labels-the-glue/) | Labels และ selectors | จัดกลุ่ม Pod โดยไม่ผูกกับชื่อหรือ IP แล้วจงใจทำ selector ว่าง |
| 006 | [`006-desired-state-and-self-healing/`](./006-desired-state-and-self-healing/) | สภาพที่ต้องการและ self-healing | ลบ Pod ภายใต้ ReplicaSet แล้วสังเกต Pod ทดแทนพร้อม request ต่อเนื่อง |
| 007 | [`007-deployment-manages-change/`](./007-deployment-manages-change/) | Deployment กำกับการเปลี่ยนแปลง | scale, rollout, rollback และวิเคราะห์ rollout ที่ใช้ image ซึ่งไม่มีอยู่จริง |

## ลำดับที่ควรทำ

ลำดับหลักคือ `001 → 002 → 003 → 004 → 005 → 006 → 007` เนื่องจากแต่ละปฏิบัติการเพิ่มระดับ abstraction อย่างเป็นลำดับ

- หากเตรียม cluster และ image แล้ว สามารถข้าม “ขั้นติดตั้ง” ใน 001 ได้ แต่ไม่ควรข้ามแนวคิด control plane/worker
- สามารถดำเนินปฏิบัติการ 002 หลัง 003 ได้ หากผู้สอนต้องการให้ผู้เรียนศึกษา Pod ก่อน แล้วจึงอธิบาย namespace
- ควรดำเนินปฏิบัติการ 004–007 ตามลำดับ เนื่องจาก YAML และ label เป็นพื้นฐานของ ReplicaSet/Deployment
- หากมีเวลาจำกัด ผู้สอนสามารถสาธิต sidecar ในปฏิบัติการ 003 แทนการให้ผู้เรียนดำเนินการด้วยตนเอง แต่ผู้เรียนยังต้องอธิบายทรัพยากรที่ container ภายใน Pod ใช้ร่วมกันได้

## เตรียมเฉพาะครั้งนี้

หลังจากเตรียมเครื่องตาม README ระดับชุดแล้ว ให้ตรวจสอบ cluster และ image web ก่อนเริ่มดำเนินการ:

```bash
kubectl get nodes
docker exec devtools-control-plane crictl images | grep k8s-lab-web
kubectl get ns lab002 lab003 lab004 lab005 lab006 lab007 --ignore-not-found
```

LAB 001 สำรวจ resource ระดับ cluster จึงไม่สร้าง namespace; LAB 002 ใช้ `lab002` เพื่อทดลอง
ส่วน LAB 003–007 ใช้ `lab003` ถึง `lab007` ตามลำดับ
ตั้งแต่ LAB 006 คำสั่งในเทอร์มินัลของเครื่องเรียนจะเรียก Ingress ที่ `http://localhost` (พอร์ต 80)
ส่วนเบราว์เซอร์บนเครื่องของผู้เรียนให้เปิด `http://localhost:8080`; LAB 003–005 ใช้ port-forward ที่ `http://localhost:3000`

## การล้างทรัพยากรเมื่อสิ้นสุดการสอนครั้งนี้

แต่ละปฏิบัติการกำหนดให้ลบ namespace ของตนเอง คำสั่งต่อไปนี้ใช้ตรวจสอบและล้างทรัพยากรเมื่อสิ้นสุดการสอนครั้งนี้:

```bash
kubectl delete ns lab002 lab003 lab004 lab005 lab006 lab007 --ignore-not-found
kubectl get ns lab002 lab003 lab004 lab005 lab006 lab007 --ignore-not-found
```

ผลการตรวจสอบบรรทัดสุดท้ายต้องไม่แสดง namespace เหล่านี้ หากสถานะยังเป็น `Terminating` ให้รอจน controller ดำเนินการเสร็จสิ้น
ไม่จำเป็นต้องลบ cluster หากจะดำเนินการเรียนในครั้งถัดไป เนื่องจากยังต้องใช้ image และส่วนประกอบส่วนกลางต่อไป

## รายการตรวจสอบเมื่อสิ้นสุดการสอนครั้งนี้

- [ ] อธิบายได้ว่า Kubernetes เพิ่มกลไกกำกับดูแลใดเหนือการเรียกใช้งาน container บนเครื่องเดียว
- [ ] อธิบายหน้าที่ API server, etcd, scheduler, controller-manager และ kubelet พร้อมเส้นทางสร้าง Pod ได้
- [ ] คำนวณ quorum ของ etcd 3/5 สมาชิก และแยก replication ออกจาก backup ได้
- [ ] อธิบายข้อจำกัด HA ของ kind ที่มี control plane หนึ่งเครื่องและใช้ host ร่วมกันได้
- [ ] อธิบายได้ว่า Pod เป็นหน่วย schedule และต่างจาก container อย่างไร
- [ ] อ่าน `apiVersion`, `kind`, `metadata`, `spec` และแยกสภาพที่ต้องการจากสภาพจริงได้
- [ ] อธิบายได้ว่า label/selector เชื่อม object โดยไม่ผูกชื่อหรือ IP อย่างไร
- [ ] คาดการณ์ได้ว่าเกิดสิ่งใดขึ้นเมื่อลบ Pod เดี่ยวและ Pod ภายใต้ ReplicaSet/Deployment
- [ ] อธิบาย scale, rollout และ rollback โดยอ้างหลักฐานจาก ReplicaSet/Pod ได้

ภาพรวมที่ควรจดจำ: **Deployment ประกาศสภาพที่ต้องการ และ controller ทำหน้าที่ลดส่วนต่างระหว่างสภาพที่ต้องการกับสภาพจริง**
