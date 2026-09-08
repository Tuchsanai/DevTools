แก้ไฟล์ [Kubernetes_Session2_Slides.html](/root/workspace/DevTools/05_kubernetes/02_Session2_Networking_Config_Storage/Kubernetes_Session2_Slides.html:307) แล้ว โดยไม่ได้สร้างไฟล์รายงานเพิ่มหรือสร้าง/ลบ container

## ส่วน A: Feedback ก่อนแก้

คะแนนเรียงตาม: YAML / คำอธิบาย / ความครบถ้วน / อ่านออก / เลย์เอาต์

| หน้าเดิม | Object | คะแนน 5 หมวด | ปัญหาและข้อเสนอแก้ |
|---:|---|---|---|
| 3 | โครง object | 5 / 4 / 4 / 5 / 5 | ตัวอย่างและภาพถูกต้อง แต่คำอธิบาย `status` ย่อเป็น controller ฝ่ายเดียว และเป็นหน้าทบทวนสั้น จึงยังไม่ครอบคลุม syntax ทั้งหมดจากครั้งที่ 1 |
| 8 | Deployment | 5 / 3 / 3 / 5 / 3 | อธิบาย selector ผิดว่า controller จะเลือก Pod ผิดชุด—จริงแล้ว API ปฏิเสธ selector ที่ไม่ตรง template labels; ขาด `maxSurge`, `maxUnavailable`, `Recreate`, `minReadySeconds`, `revisionHistoryLimit` และ change-cause; มีพื้นที่ว่างมาก |
| 9 | Ingress | 5 / 5 / 3 / 5 / 3 | YAML ตรงกับ `01-web.yaml` แต่ไม่กล่าวถึง `tls`; snippet สั้นและพื้นที่ด้านล่างเกิน 15% |
| 10 | Service | 5 / 5 / 3 / 5 / 3 | ClusterIP/NodePort, selector, port และ DNS ถูกต้อง แต่ไม่กล่าวถึง LoadBalancer ตามสเปก; พื้นที่ว่างมาก |
| 33 | ConfigMap | 5 / 4 / 5 / 5 / 3 | ตัวอย่างตรงไฟล์จริง แต่คำอธิบาย ConfigMap volume ยังไม่ชัดว่าไฟล์อัปเดตภายหลังและโปรแกรมต้อง reload; พื้นที่ว่างมาก |
| 45 | Secret | 5 / 4 / 5 / 5 / 3 | ควรระบุชัดว่า `stringData` ถูก merge ลง `data` และ base64 ถอดกลับได้ ไม่ใช่ encryption; พื้นที่ว่างมาก |
| 57 | Volume/emptyDir | 5 / 4 / 5 / 5 / 3 | ควรอธิบายอายุ `emptyDir` ว่าผูกกับ Pod และใช้ข้อความ validation ที่ชัดขึ้น; snippet สั้นและพื้นที่ว่างมาก |
| 70 | PVC | 5 / 5 / 5 / 5 / 3 | field และ default ถูกต้องครบ แต่พื้นที่ด้านล่างมากและคอลัมน์ซ้าย–ขวาไม่สมดุล |
| 82 | Probes | 5 / 5 / 5 / 5 / 3 | กลไก readiness/liveness/startup/exec ถูกต้อง แต่พื้นที่ด้านล่างเกินเกณฑ์ |
| 83 | Probe timings | 5 / 4 / 5 / 5 / 3 | default ถูกต้อง แต่ “ผิดบ่อย” เป็นเพียงคำแนะนำทั่วไป ควรชี้ validation จริง เช่น `periodSeconds: 0`; snippet สั้นและพื้นที่ว่างมาก |

Object ที่ไม่มีหน้าก่อนแก้: **ไม่มี** — มีครบโครง object, Deployment, Ingress, Service, ConfigMap, Secret, Volume/PVC และ Probes แต่บาง field ยังอธิบายไม่ครบตามตารางข้างต้น

Baseline ของทั้งไฟล์คือ 97 หน้า จึงเกินข้อกำหนดสูงสุด 90 หน้า

## ส่วน B: สิ่งที่แก้และคะแนนหลังแก้

| หน้าหลังแก้ | Object | สิ่งที่แก้ | คะแนนหลังแก้ |
|---:|---|---|---|
| 3 | โครง object | ปรับกริดให้โค้ด ภาพกายวิภาค และการ์ดใช้พื้นที่เต็มโดยไม่ชน footer | 5 / 4 / 4 / 5 / 5 |
| 8 | Deployment | ขยาย YAML จริงถึง `template.labels`, container และ image; แก้ selector mismatch เป็น API rejection; เพิ่ม rollout defaults, Recreate, readiness/history และ change-cause | 5 / 5 / 5 / 5 / 5 |
| 9 | Ingress | ใช้ object จริงครบ `apiVersion`, metadata และ spec; เพิ่ม host/TLS พร้อมระบุว่าแล็บไม่ได้กำหนด TLS; ทำ error ของ `pathType` ให้ชัด | 5 / 5 / 5 / 5 / 5 |
| 10 | Service | เพิ่ม LoadBalancer, DNS เต็ม, EndpointSlice และข้อความ API rejection ของ nodePort | 5 / 5 / 5 / 5 / 5 |
| 31 | ConfigMap | แยกผลของ env กับ volume ชัดเจน: env ต้องสร้าง Pod ใหม่ ส่วนไฟล์อัปเดตภายหลังและโปรแกรมต้อง reload | 5 / 5 / 5 / 5 / 5 |
| 42 | Secret | ระบุการ merge `stringData` ลง `data`, base64 ถอดกลับได้ และไม่ใช่ encryption | 5 / 5 / 5 / 5 / 5 |
| 53 | Volume/emptyDir | เติม hierarchy `spec.template.spec`, แก้อายุ emptyDir เป็นผูกกับ Pod และใช้ข้อความ `volumeMounts[0].name: Not found: "data"` ที่อ่านครบ | 5 / 5 / 5 / 5 / 5 |
| 65 | PVC | ปรับกริดให้สมดุล โดยคง access modes, storage request, StorageClass และ claimName จากไฟล์จริง | 5 / 5 / 5 / 5 / 5 |
| 76 | Probes | ขยายโค้ดและการ์ดเต็มพื้นที่ โดยคง `/ready`, `/health` และค่าจริงจาก manifest | 5 / 5 / 5 / 5 / 5 |
| 77 | Probe timings | เติม context HTTP ของ probe จากไฟล์จริง และเปลี่ยน “ผิดบ่อย” เป็น `periodSeconds: 0` ถูก API ปฏิเสธเพราะต้อง ≥ 1 | 5 / 5 / 5 / 5 / 5 |

ทุกหน้าใช้ `pre.code` ขนาด 18px, มี 6–18 บรรทัด และตรวจแล้วไม่มี code/card overflow

เพื่อลดจาก 97 เป็น 90 หน้า ได้รวมสไลด์ “ทฤษฎี 4/4 — หนึ่งประโยคที่ต้องจำ” ของทั้ง 7 แล็บเข้าไปใน caption ของสไลด์โมเดลก่อนหน้า จึงไม่สูญเสียใจความสำคัญ

## ส่วน C: ผลตรวจและข้อจำกัด

ผล `check-slides.js` รอบสุดท้าย:

| รายการ | ผล |
|---|---|
| จำนวนหน้า | **90** — ผ่าน |
| ขนาดไฟล์ | **5.4 MB** — ผ่าน |
| Images | 48 |
| `brokenImages` | `[]` |
| `externalRefs` | `[]` |
| `externalImports` | 0 |
| `pageErrors` | `[]` |
| Navigation | ซ้าย/ขวา/Space/Home/End/Overview/Help/Progress/Counter/Controls ผ่านทั้งหมด |
| End navigation | `#90` |
| `labFoldersReferenced` | **7** — LAB 008–014 ครบ |

หน้า YAML อยู่ก่อนแล็บแรกที่ใช้ครบทั้งหมด และ footer ทั้ง 8 anchor มีหัวข้อจริงใน `YAML_Guide.md`

Object ที่ยังขาดหลังแก้: **ไม่มี**

ข้อจำกัด: container ใช้ client v1.37.0 แต่ Kubernetes server เป็น **v1.36.4** พร้อม emulation v1.36; การตรวจ field/default ใช้ `kubectl explain` ผ่าน `devtools-k8s-verify` ตามที่กำหนด และไม่ได้สร้างหรือลบ container ใด ๆ แนวทางแยกสภาพแวดล้อมจาก skill `devtools-lab` ถูกใช้เฉพาะในการตรวจสอบกับ container ที่ผู้ใช้ระบุเท่านั้น