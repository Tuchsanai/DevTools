# สเปกการสอน YAML "ของทุกระบบ" (yolo1 ออกแบบ · 2026-09-02 · ผู้ใช้สั่ง "อยากให้มีการสอนเพิ่มเกี่ยวกับ YAML ของทุกระบบ")

เป้าหมาย: นักศึกษาอ่าน manifest ของทุก object ในชุดได้ "ทีละบรรทัด" รู้ว่าแต่ละ field มีไว้ทำไม ค่าที่ใช้มาจากไหน ถ้าเปลี่ยนจะเกิดอะไร และผิดบ่อยตรงไหน — โดยไม่ต้องจำ (ใช้ `kubectl explain` ได้)

## 1. ที่ที่ต้องมี (สามที่ ต้องสอดคล้องกัน)
| ที่ | เนื้อหา | ผู้ทำ |
|---|---|---|
| A. README ของทุกแล็บ (21) | หัวข้อใหม่ **`## n. อ่าน YAML ของแล็บนี้`** วางหลังหัวข้อ "1. Clone โค้ดแล็บ" (ก่อนขั้นตอนลงมือ) | cyolo1 ต่อครั้ง |
| B. `0N_Session*/YAML_Guide.md` (3 ไฟล์) | คู่มือ YAML ของ object ที่ "เรียนครั้งนี้" 150-400 บรรทัด (รวมบททบทวน) · จบในตัวต่อครั้ง (แจกแยกได้) | cyolo1 ต่อครั้ง |
| C. สไลด์ทั้ง 3 ไฟล์ | หน้า "กายวิภาค YAML — <object>" 1-2 หน้าต่อ object วางก่อนแล็บแรกที่ใช้ object นั้น + สไลด์ "YAML คืออะไร" 2 หน้าในครั้งที่ 1 | cyolo1 ต่อครั้ง (หลัง A/B ผ่านตรวจ) |
| D. ไดอะแกรม `01_.../slides_assets/d09-yaml-anatomy.svg` (+ .excalidraw) | กายวิภาค object: apiVersion / kind / metadata / spec / status พร้อมคำอธิบายสั้น · และสำเนาใน 02_/03_ | cyolo1 (canvas ส่วนตัว) |

## 2. object ที่ต้องสอน และ "เรียนครั้งไหน"
| object / กลไก | ครั้ง | แล็บแรกที่ใช้ | field ที่ต้องอธิบายให้ครบ |
|---|---|---|---|
| **โครง object ทุกชนิด** | 1 | 004 | apiVersion (group/version · หาได้จาก `kubectl api-resources`) · kind · metadata (name, namespace, labels, annotations) · spec vs status (ใครเขียน) · YAML syntax: ย่อหน้า 2 ช่อง · list ด้วย `-` · string/number/bool (ทำไม `"5432"` ต้องมี quote) · หลาย object คั่น `---` · comment `#` · `kubectl apply --dry-run=client -f` · `kubectl explain <kind>.spec.<field>` · เทียบ `kubectl get -o yaml` กับไฟล์ |
| Pod | 1 | 003/004 | spec.containers[] (name · image · imagePullPolicy IfNotPresent/Always/Never · ports.containerPort · env/envFrom · command/args) · หลาย container ใน Pod เดียว · restartPolicy · field ที่แก้ไม่ได้ (immutable) |
| ReplicaSet | 1 | 006 | spec.replicas · spec.selector.matchLabels **ต้องตรงกับ** spec.template.metadata.labels · template = Pod spec ทั้งก้อน |
| Deployment | 1 | 007 | ทุกอย่างของ RS + spec.strategy (RollingUpdate: maxSurge/maxUnavailable · Recreate) · minReadySeconds · revisionHistoryLimit · annotation `kubernetes.io/change-cause` |
| Service | 2 | 008/009 | spec.type (ClusterIP · NodePort · LoadBalancer) · spec.selector · spec.ports[] (port · targetPort ชื่อหรือเลข · nodePort 30000-32767 · protocol) · ชื่อ DNS `svc.namespace.svc.cluster.local` · Endpoints มาจาก selector |
| ConfigMap | 2 | 010 | data (ทุกค่าเป็น string) · การใช้: `envFrom.configMapRef` · `env[].valueFrom.configMapKeyRef` · mount เป็นไฟล์ (กล่าวถึง) · เปลี่ยนค่าแล้วต้อง restart |
| Secret | 2 | 011 | type Opaque · stringData (เขียน) vs data (base64 ที่ระบบเก็บ) · `env[].valueFrom.secretKeyRef` · `envFrom.secretRef` · ห้าม commit ค่าจริง |
| Volume / PVC | 2 | 012/013 | volumes[] (emptyDir · persistentVolumeClaim.claimName) ↔ volumeMounts[] (name · mountPath) · PVC: accessModes (RWO/ROX/RWX) · resources.requests.storage · storageClassName (ไม่ระบุ = default) · PGDATA subdir |
| Probes | 2 | 014 | readinessProbe / livenessProbe (+ startupProbe กล่าวถึง) · httpGet (path · port ชื่อ/เลข) · exec.command · initialDelaySeconds · periodSeconds · timeoutSeconds · failureThreshold · successThreshold · ผลที่ต่างกันเมื่อ fail |
| Ingress | 3 | 017 (ประตูสำเร็จรูปตั้งแต่ 006) | spec.ingressClassName · rules[].http.paths[] (path · pathType Prefix/Exact · backend.service.name/port.number) · host (ไม่ใส่ = ทุก host) · tls (กล่าวถึง) |
| resources | 3 | 019 | resources.requests / limits · หน่วย cpu (m) memory (Mi/Gi) · QoS class · ผลตอน schedule vs ตอนรัน |
| Downward API | 1/2 | 007+ | env.valueFrom.fieldRef (metadata.name · spec.nodeName) — ทำไมการ์ดสถานะรู้ชื่อ Pod |
| Namespace ในไฟล์ | 1 | 006+ | metadata.namespace ในไฟล์ vs `-n` · ผลเมื่อขัดกัน |
| โครงโฟลเดอร์ manifests/ | 3 | 015 | ลำดับชื่อไฟล์ 01-.. · `kubectl apply -f <dir>` · `kubectl diff -f` · `kubectl get -f` |

## 3. รูปแบบบังคับของหัวข้อ "อ่าน YAML ของแล็บนี้" ใน README (A)
1. ตารางไฟล์ทั้งหมดของแล็บ: `| ไฟล์ | kind | ทำอะไรในแล็บนี้ | อธิบายละเอียดที่ |` — **ต้องมีทุกไฟล์ .yaml ในโฟลเดอร์แล็บ** (รวม manifests/ broken/ fixed/ exercise/) linter จะตรวจ
2. สำหรับ **field ที่แล็บนี้ใช้เป็นครั้งแรก** (ตามตารางข้อ 2): แสดง YAML จริงจากไฟล์ (ตัดเฉพาะส่วนที่เกี่ยวได้ แต่ห้ามแต่งค่า) ใน ```yaml พร้อม comment ภาษาไทยท้ายบรรทัดหรือตาราง `| บรรทัด/field | ความหมาย | ถ้าเปลี่ยนค่านี้ |`
3. สำหรับ field ที่เรียนไปแล้ว: ไม่อธิบายซ้ำ ให้ลิงก์ `[ดู YAML_Guide.md → <หัวข้อ>](../YAML_Guide.md#<anchor>)` (anchor ต้องมีจริงในไฟล์ B)
4. 1 ย่อหน้า "ผิดบ่อยในแล็บนี้": ข้อผิดพลาด YAML ที่เจอจริง (เช่น selector ไม่ตรง label → Pod ไม่ถูกนับ · `"5432"` ไม่ใส่ quote → error · ย่อหน้าผิด → `unknown field`) พร้อมข้อความ error จริงถ้ามีใน runlog
5. ปิดด้วย 1 บรรทัด: `kubectl explain <kind>.spec...` ที่ใช้ดู field ของแล็บนี้
6. ความยาว README หลังเพิ่ม: เป้าหมาย ≤ 450 บรรทัด — ถ้าเกิน ให้ย่อส่วน Expected output ที่ยาวเกินจำเป็น ห้ามตัดขั้นตอน/สามส่วน · ห้ามเปลี่ยนแนวคิดหลัก · ผ่าน check-readme.py 0 FAIL

## 4. รูปแบบบังคับของ `YAML_Guide.md` (B) — ต่อครั้ง
```
# คู่มือ YAML ครั้งที่ N — <ธีม>
> อ่านคู่กับแล็บ 0NN-0NN · ทุกตัวอย่างคัดจากไฟล์จริงในโฟลเดอร์แล็บของครั้งนี้
## 0. อ่าน YAML ให้เป็น (เฉพาะครั้งที่ 1 · ครั้งที่ 2-3 สรุป 5 บรรทัด + ชี้ว่าครั้งที่ 1 มีฉบับเต็ม เป็นข้อความ ไม่ใช่ path)
## 1. <object แรกของครั้ง>   ← หนึ่งหัวข้อต่อ object ในตารางข้อ 2 (anchor = ชื่อ object ตัวเล็ก เช่น #deployment)
   - ทำไมต้องมี (1-2 ประโยค เชื่อมกับปัญหาในแล็บ)
   - โครงเต็ม: ```yaml จากไฟล์จริง (ระบุชื่อไฟล์/แล็บ) พร้อม comment ไทยทุกบรรทัดสำคัญ
   - ตาราง field: | field | ค่าที่ใช้ได้ | ค่า default | ถ้าเปลี่ยน/ลืมจะเกิดอะไร |
   - "ผิดบ่อย" 2-4 ข้อ พร้อมข้อความ error จริง (จาก runlog ถ้ามี) และวิธีดู (`describe` / `explain`)
   - คำสั่งดูของจริง: `kubectl get <kind> <name> -o yaml`, `kubectl explain ...`
## ท้าย: ตารางสรุป field ทั้งหมดของครั้งนี้ (field | object | แล็บ) + "จำภาพเดียวให้ได้: ..."
```
- ห้ามอ้าง path ข้ามโฟลเดอร์ครั้ง (ลิงก์ได้เฉพาะ `0NN-.../README.md` และไฟล์ในครั้งเดียวกัน) · ลิงก์ทุกอันต้องมีจริง
- README ระดับครั้ง (`0N_Session*/README.md`) เพิ่มบรรทัดลิงก์ไป `YAML_Guide.md` ในส่วนต้น · README ระดับชุดเพิ่ม 1 บรรทัดว่าแต่ละครั้งมีคู่มือ YAML

## 5. สไลด์ (C) — หลัง A/B ผ่านตรวจ · **ผู้สอนย้ำ (20:20): ทุกครั้งต้องมีหน้า YAML ของทุก object ที่ใช้ในครั้งนั้น** — object ใหม่ 1-2 หน้าเต็ม · object ที่เรียนแล้วแต่ยังใช้ = หน้าทบทวน 1 หน้า (ไฟล์สไลด์แต่ละครั้งจบในตัว)
- ครั้งที่ 1: 2 หน้า "YAML คืออะไร / โครง object" (ใช้ d09-yaml-anatomy.svg) + กายวิภาค Pod · ReplicaSet · Deployment (อย่างละ 1-2 หน้า) วางก่อนสไลด์แล็บ 004/006/007 ตามลำดับ
- ครั้งที่ 2: ทบทวนโครง object + Deployment + Ingress(ประตู) (ทบทวน) · Service · ConfigMap · Secret · Volume/PVC · Probes (เต็ม) ก่อนแล็บ 008/010/011/013/014
- ครั้งที่ 3: ทบทวนโครง object + Deployment/Service/ConfigMap + Secret/PVC (ทบทวน) · manifests/ · Ingress paths · strategy · resources · broken manifests · ชุดสมบูรณ์ (เต็ม) ก่อนแล็บ 015/017/018/019/020/021
- รูปแบบหน้า: ซ้าย `pre.code` YAML จริง (ไฮไลต์ field ด้วย span .k/.g/.y ของต้นแบบ · ≥ 18px) · ขวา การ์ด 3-4 ใบอธิบาย field สำคัญ + 1 การ์ด "ผิดบ่อย" · หัวเรื่อง "กายวิภาค YAML — <object>" · footer ชี้ `YAML_Guide.md#<anchor>`
- รวมไม่เกิน 90 หน้าต่อไฟล์ · ผ่าน check-slides.js · ผ่าน loop ตรวจหน้า (cyolo1) + yolo1 ดู

## 4b. YAML_Guide.md ครั้งที่ 2-3 ต้องมีหัวข้อ "ทบทวน" 10-20 บรรทัดสำหรับ object ที่เรียนไปแล้วแต่ยังใช้ในครั้งนี้ (Deployment/Service/Ingress/ConfigMap/Secret/PVC) เพื่อให้ไฟล์จบในตัว (เพิ่มในรอบแก้หลัง reviewer)

## 6. ความถูกต้อง (บังคับ)
- คำอธิบายทุก field ต้องถูกต้องตาม Kubernetes v1.36 (ตรวจกับ `kubectl explain` ใน container ได้) · ค่า default ต้องระบุตามจริง (เช่น imagePullPolicy default = IfNotPresent เมื่อ tag ไม่ใช่ latest · pathType ไม่มี default ต้องระบุ · Service type default = ClusterIP · restartPolicy default = Always · probe periodSeconds default 10 timeoutSeconds 1 failureThreshold 3 successThreshold 1)
- ตัวอย่าง YAML ต้องมาจากไฟล์จริงในโฟลเดอร์แล็บ ห้ามแต่งไฟล์ใหม่ (ถ้าจำเป็นต้องแสดง field ที่ไฟล์ไม่มี ให้บอกว่า "ตัวอย่างเพิ่มเติม ไม่ได้อยู่ในไฟล์ของแล็บ")
- yolo1 reviewer จะตรวจทุกหัวข้อกับ `kubectl explain` และ runlog · ที่ผิดจะถูกส่งกลับให้แก้
