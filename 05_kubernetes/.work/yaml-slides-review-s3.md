แก้และตรวจเสร็จแล้วใน [Kubernetes_Session3_Slides.html](/root/workspace/DevTools/05_kubernetes/03_Session3_Application_Deployment/Kubernetes_Session3_Slides.html) โดยไม่ได้สร้างไฟล์รายงานเพิ่ม

## ส่วน A: Feedback ก่อนแก้

คะแนนเรียงตาม 5 หมวด: YAML | คำอธิบาย | ครบถ้วน | อ่านออก | เลย์เอาต์

| หน้า | Object | YAML | อธิบาย | ครบ | อ่าน | เลย์ | ปัญหา/ข้อเสนอแก้ |
|---:|---|---:|---:|---:|---:|---:|---|
| 4 | โครง object | 5 | 4 | 5 | 4 | 5 | YAML ตรง ConfigMap จริงและ footer ถูกต้อง แต่ข้อความใน diagram เล็ก จึงต้องพึ่งบล็อกโค้ดด้านล่าง |
| 5 | `manifests/` | 5 | 5 | 5 | 4 | 3 | รายชื่อไฟล์และคำสั่งตรง guide แต่ panel ซ้ายเตี้ยกว่าการ์ดมาก เกิดพื้นที่ว่างเกินเป้าหมาย |
| 6 | Deployment / Service / ConfigMap | 5 | 3 | 5 | 5 | 5 | `targetPort ชี้ container` กว้างเกินไป; ตาม schema คือเลขหรือชื่อพอร์ตบน Pod เป้าหมาย |
| 17 | Secret / PVC | 5 | 5 | 5 | 4 | 4 | ค่าและคำอธิบายถูกต้อง แต่มีการ์ด 5 ใบและข้อความค่อนข้างแน่น |
| 28 | Ingress rules/paths | 5 | 5 | 5 | 5 | 3 | snippet ถูกต้องแต่เริ่มจาก `spec` ทำให้ panel ซ้ายสั้นและขาดบริบท object |
| 29 | Ingress backend/host/TLS | 5 | 5 | 5 | 5 | 4 | แยก manifest ปกติ/เสียชัดเจน; host และ TLS ระบุชัดว่าไม่ได้อยู่ในไฟล์ |
| 40 | RollingUpdate | 5 | 5 | 5 | 5 | 3 | field และค่า default ถูกต้อง แต่ snippet เพียง 8 บรรทัด ทำให้สองคอลัมน์ไม่สมดุล |
| 41 | Recreate/readiness | 5 | 5 | 5 | 4 | 4 | ข้อมูลจากสองไฟล์ระบุแหล่งชัดเจนและ default `revisionHistoryLimit: 10` ถูกต้อง |
| 53 | Resources/QoS | 5 | 3 | 5 | 5 | 3 | นิยาม QoS “ครบและเท่ากัน” ยังไม่ระบุว่าต้องครบทุก container และทั้ง CPU+memory; panel ซ้ายสั้น |
| 63 | Broken manifests | 5 | 3 | 5 | 4 | 4 | การระบุว่าจะเห็น `CrashLoopBackOff` ตรง ๆ ไม่สอดคล้อง runlog v1.36 ซึ่ง STATUS อาจเป็น `Error` ขณะที่ Events แสดง `BackOff` |
| 73 | ชุดสมบูรณ์ 10 ไฟล์ | 5 | 5 | 5 | 4 | 3 | รายชื่อไฟล์และ dependency ถูกต้อง แต่ panel รายการไฟล์เตี้ยกว่าการ์ดมาก |

Object ที่ยังไม่มีหน้าก่อนแก้: **ไม่มี** — ครบโครง object, `manifests/`, Deployment/Service/ConfigMap, Secret/PVC, Ingress, strategy, resources, broken manifests และชุดสมบูรณ์

## ส่วน B: สิ่งที่แก้และคะแนนหลังแก้

| หน้า | สิ่งที่แก้ | คะแนนหลังแก้ |
|---:|---|---|
| 4 | ไม่แก้; เนื้อหาและตำแหน่งผ่านแล้ว | 5/4/5/4/5 |
| 5 | เพิ่มความสูง/padding ของ code panel และย่อข้อความการ์ดให้สมดุล | 5/5/5/5/5 |
| 6 | แก้คำอธิบาย `targetPort` เป็นพอร์ตเลขหรือชื่อบน Pod เป้าหมาย | 5/5/5/5/5 |
| 17 | ไม่แก้; ตรวจซ้ำแล้วไม่มี overflow | 5/5/5/4/4 |
| 28 | เพิ่ม `apiVersion`, `kind`, `metadata.name/namespace` จาก manifest จริง | 5/5/5/5/5 |
| 29 | ไม่แก้; YAML ปกติ/เสียและผล 503 ถูกต้อง | 5/5/5/5/4 |
| 40 | เติม header, metadata และ selector จาก `02-web-deployment.yaml` จริง | 5/5/5/5/5 |
| 41 | ไม่แก้; ยืนยัน Recreate, probe และ default ผ่าน `kubectl explain` | 5/5/5/4/4 |
| 53 | เติมบริบท Deployment จริง และแก้นิยาม Guaranteed/Burstable/BestEffort | 5/5/5/5/5 |
| 63 | เพิ่มค่าจาก `fixed/02-imagepull.yaml`; แก้คำอธิบาย crash ให้ตรง STATUS/Events จริง | 5/5/5/5/4 |
| 73 | เพิ่มความสูง/padding ของ panel รายการ 10 ไฟล์ | 5/5/5/5/5 |

หลังแก้ทุกหน้าใช้ `pre.code` ขนาด 18px, มี 8–18 บรรทัด, ไม่มี code/card overflow และไม่มีส่วนใดชน footer

## ส่วน C: ผลตรวจสุดท้าย

- `check-slides.js`: **ผ่าน**
- Slides: **90 หน้า**
- ขนาด: **5.1 MB**
- Images: 47; `brokenImages: []`
- `externalRefs: []`
- `externalImports: 0`
- `pageErrors: []`
- Navigation: ซ้าย/ขวา/Space/Home/End/Overview/Help ผ่านครบ
- `labFoldersReferenced`: **7 โฟลเดอร์ครบ**
- Footer ทุกหน้า YAML ชี้ anchor ที่มีจริงใน `YAML_Guide.md`
- หน้าสอนทุก object อยู่ก่อนสไลด์แล็บแรกที่ใช้งาน
- Object ที่ยังขาด: **ไม่มี**
- ข้อจำกัด: deck อยู่ที่เพดาน **90 หน้า** พอดี
- ตรวจ schema กับ Kubernetes server **v1.36.4** ผ่าน container เดิม `devtools-k8s-verify`; ตามแนวทาง `devtools-lab` ไม่ได้สร้างหรือลบ container ใด ๆ
- ภาพ render รอบสุดท้ายอยู่ที่ [.work/slide-shots-s3](/root/workspace/DevTools/05_kubernetes/.work/slide-shots-s3)