แก้ [Kubernetes_Session1_Slides.html](/root/workspace/DevTools/05_kubernetes/01_Session1_Kubernetes_Basics/Kubernetes_Session1_Slides.html) และตรวจซ้ำเรียบร้อย โดยไม่ได้สร้างไฟล์รายงานเพิ่ม

## ส่วน A: Feedback ก่อนแก้

คะแนนเรียงตาม: ความถูกต้อง YAML / คำอธิบาย / ความครบถ้วน / อ่านออก / เลย์เอาต์

| หน้าเดิม | Object | คะแนน | ปัญหาและข้อเสนอ |
|---:|---|---|---|
| 35 | YAML คืออะไร | 5 / 3 / 5 / 5 / 3 | วาง `--dry-run=client` ใกล้ error `unknown field` จนอาจเข้าใจว่า client ตรวจ schema ได้; พื้นที่ขวาล่างเกิน 15% |
| 36 | โครง object | 5 / 5 / 5 / 3 / 4 | YAML และคำอธิบายถูกต้อง แต่ thumbnail `d09-yaml-anatomy.svg` เล็กจนอ่านข้อความไม่ได้ |
| 37 | Pod 1/2 | 5 / 4 / 3 / 5 / 3 | อยู่หลัง LAB 003 ซึ่งใช้ Pod แล้ว; อธิบาย default `imagePullPolicy` ไม่ครบกรณี `latest`/ไม่ใส่ tag/digest; พื้นที่ว่างมาก |
| 38 | Pod 2/2 | 5 / 4 / 3 / 5 / 4 | อยู่หลัง LAB 003; กล่าวถึง `envFrom` โดยไม่บอกว่าไม่ได้อยู่ในไฟล์; ข้อความ immutability กว้างและใช้คำว่า “อาจถูกปฏิเสธ” |
| 59 | ReplicaSet | 5 / 5 / 5 / 5 / 3 | YAML, default และ error ถูกต้อง แต่คอลัมน์การ์ดสั้นกว่าโค้ดมาก |
| 60 | Service + Ingress | 5 / 4 / 5 / 5 / 3 | excerpt ตรง `02-door.yaml`; ระบุ default `ClusterIP` แล้ว แต่ยังไม่บอก default protocol `TCP`; คอลัมน์ไม่สมดุล |
| 74 | Deployment 1/2 | 5 / 4 / 5 / 5 / 3 | ค่า default ถูกต้อง แต่ยังไม่บอกการปัดขึ้น/ลงของ `maxSurge` และ `maxUnavailable`; การ์ดสั้นกว่าโค้ด |
| 75 | Deployment + Downward API | 5 / 5 / 5 / 5 / 3 | fieldRef และ default `apiVersion: v1` ถูกต้อง; มีพื้นที่ว่างใต้การ์ดมาก |

Object ที่ยังไม่มีหน้า: **ไม่มี** — ครบ YAML syntax/โครง object, Pod, ReplicaSet, Service+Ingress, Deployment และ Downward API แต่หน้า Pod วางผิดตำแหน่ง

## ส่วน B: สิ่งที่แก้และคะแนนหลังแก้

| หน้าปัจจุบัน | Object | สิ่งที่แก้ | คะแนนหลังแก้ |
|---:|---|---|---|
| 25 | Pod 1/2 | ย้ายก่อน LAB 003; เปลี่ยนตัวอย่างเป็น `web2`, `namespace: lab003` จาก manifest LAB 003; เติม default ของ `imagePullPolicy` และคำสั่งดูของจริง | 5 / 5 / 5 / 5 / 5 |
| 26 | Pod 2/2 | ย้ายก่อน LAB 003; ระบุว่า `envFrom` ไม่อยู่ในไฟล์นี้; เจาะจงว่า `restartPolicy` แก้หลังสร้างไม่ได้และ API ปฏิเสธการเพิ่ม `env` | 5 / 5 / 5 / 5 / 5 |
| 37 | YAML คืออะไร | แยก client dry-run สำหรับ syntax/kind ออกจาก server dry-run สำหรับ schema/admission; ผูก error กับ server dry-run; ขยายการ์ดเต็มแนว | 5 / 5 / 5 / 5 / 5 |
| 38 | โครง object | แทน thumbnail ที่อ่านไม่ออกด้วยป้ายสรุปชัดเจนและชี้ไปภาพเต็มหน้าถัดไป | 5 / 5 / 5 / 5 / 5 |
| 39 | ภาพสนับสนุน d09 | เพิ่มหน้าแสดง `d09-yaml-anatomy.svg` ขนาดเต็ม อ่าน apiVersion/kind/metadata/spec/status ได้จริง | ผ่านด้านการอ่านและเลย์เอาต์ |
| 60 | ReplicaSet | เกลี่ยความสูงการ์ดให้สมดุลกับโค้ด | 5 / 5 / 5 / 5 / 5 |
| 61 | Service + Ingress | เติม default `type: ClusterIP` และ `protocol: TCP`; ขยายการ์ดเต็มแนว | 5 / 5 / 5 / 5 / 5 |
| 75 | Deployment 1/2 | เติม `maxSurge` ปัดขึ้นและ `maxUnavailable` ปัดลง; ปรับเลย์เอาต์ | 5 / 5 / 5 / 5 / 5 |
| 76 | Deployment + Downward API | เกลี่ยคอลัมน์การ์ดให้สูงสมดุลกับโค้ด | 5 / 5 / 5 / 5 / 5 |

ทุก `pre.code` วัดได้ 18px, 7–18 บรรทัด และไม่พบ overflow ของโค้ดหรือการ์ด

## ส่วน C: ผลตรวจสุดท้าย

`check-slides.js` ผ่าน:

- 90 หน้า — ไม่เกินเพดาน 90
- 5.7 MB — ไม่เกิน 15 MB
- 44 images, `brokenImages: []`, images ไม่มี alt: 0
- `externalRefs: []`, `externalImports: 0`
- `pageErrors: []`
- navigation ครบ: ซ้าย/ขวา/Space/Home/End, overview, help, progress, counter และ controls
- `labFoldersReferenced`: ครบทั้ง 7 โฟลเดอร์
- Footer anchors ทั้งหกค่าอยู่จริงใน `YAML_Guide.md`
- ทุก object อยู่ก่อนแล็บแรก: Pod 25 < LAB003 27, ReplicaSet/Service+Ingress 60–61 < LAB006 62, Deployment/Downward API 75–76 < LAB007 77
- Object ที่ยังขาด: **ไม่มี**

ข้อจำกัด: deck อยู่ที่เพดาน 90 หน้าพอดี หากเพิ่มหน้าอีกต้องรวม/ตัดหน้าเดิมก่อน ตรวจ schema กับ Kubernetes server `v1.36.4`; kubectl client เป็น `v1.37.0` แต่ `kubectl explain` อ่าน schema จาก server ตามเป้าหมาย งานนี้ใช้ `devtools-lab` ภายใต้ข้อกำหนดเฉพาะของผู้สอน—ใช้เฉพาะ container `devtools-k8s-verify` ที่มีอยู่และไม่ได้สร้างหรือลบ container ใด ๆ