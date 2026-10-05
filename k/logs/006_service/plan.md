# แผนบทเรียน 006 — Kubernetes Service (ประภาคารที่ชื่อและที่อยู่ไม่เคยเปลี่ยน)

> สถานะ: แผน + storyboard ภาพเท่านั้น (ยังไม่เขียน README/ไฟล์ LAB และยังไม่รัน LAB)
> แตกจากบทรวม `logs/005_rs_deploy_svc/plan.md` ตามสัญญา `logs/005_replicaset/scratch/split-contract.md`
> Storyboard ภาพ: `logs/006_service/images.json` (Theory 36 ภาพ T01–T36, LAB 24 ภาพ L01–L24) สร้างจาก `logs/006_service/build_images.py` (+ `imgcommon.py` ส่วนกลาง ห้ามแก้) → ได้ `images.json`, `image-sources.tsv`, `README-split.md`, `006_kubernetes_service/01_Theory/images/imagegen-prompts.md`, `006_kubernetes_service/02_LAB/images/imagegen-prompts.md`
> ภาพตัวละครอ้างอิง: `006_kubernetes_service/01_Theory/images/00-character-som.png`
> ผล pre-check ที่ใช้ (รันจริง 5 ต.ค. 2569 ใน container ชั่วคราว ลบแล้ว): `logs/005_rs_deploy_svc/precheck.md`

## 0. ภาพรวมและข้อกำหนด

- ผู้เรียนผ่านบท 001 (k8s-lab, kind `lab`: lab-control-plane / lab-worker / lab-worker2, K8s v1.37; พอร์ต 30080–30082 ของเครื่องนักศึกษา map เข้า NodePort 30080–30082 ของ lab-control-plane ด้วย extraPortMappings), 002 (Pod, labels, probes, init/native sidecar, som-shop all-in-one), 003 (scheduling, Node ล่ม, Downward API), 004 (Namespace, quota, PSA, NetworkPolicy, DNS search domain, `som-shop-web:1.1`, port-forward หลุดเมื่อ Pod ถูกลบ) และ **005 (ReplicaSet: selector/template/ownerReferences/scale, แก้ template แล้ว Pod เดิมไม่เปลี่ยน, ร้าน 3 บูธที่ db ไม่ตรงกัน)**
- เข้าเครื่อง: `ssh -p 2223 root@localhost` (รหัส `passwd`) หรือ JupyterLab `http://localhost:8889`
- โฟลเดอร์ LAB: `docker cp 006_kubernetes_service k8s-lab:/workspace/` แล้ว `cd /workspace/006_kubernetes_service/02_LAB`
- **บทนี้เป็นบทแรกที่เปิดร้านจาก browser ด้วย `http://localhost:30080` โดยไม่ต้อง port-forward/ssh -L**
- ตัวสร้าง Pod หลัง Service ในทุก LAB = **ReplicaSet** (เรียนแล้ว) — Service เลือก Pod ด้วย label ไม่สนว่าใครสร้าง; **ห้ามใช้ Deployment และ `kubectl rollout` ในขั้นตอน** (กล่าวปูทางบท 007 ได้ในท้ายบท); `kubectl expose rs/web` ใช้ได้
- ยังไม่สอน (ปูทางเท่านั้น): Deployment/rollout (บท 007), PVC/StatefulSet, Ingress/Gateway, ConfigMap/Secret แบบละเอียด, HPA, Job
- ทุก LAB อยู่ใน namespace ของ LAB (LAB1–LAB9 ใช้ `shop` ร่วมกัน + `kitchen` ใน LAB9, LAB10 ใช้ `som-shop`) และจบด้วย `kubectl delete ns ...` (ถ้าหยุดกลางทาง ให้ `kubectl delete ns shop` แล้วเริ่ม LAB ถัดไปจาก `labs/lab01-*` ใหม่ได้)
- Pod busybox ทุกตัวใส่ `terminationGracePeriodSeconds: 1`; image สาธารณะ (`nginx:1.27-alpine`, `busybox:1.36`) ให้ Node pull เอง (pre-check #6); image ที่ build เองใช้ `kind load docker-image ... --name lab`; postgres ใช้ `docker save --platform linux/amd64 postgres:17.11-alpine -o /workspace/006_kubernetes_service/02_LAB/pg.tar && kind load image-archive ... --name lab` หรือให้ Node pull เอง
- kubectl 1.37 พิมพ์ `pod "x" deleted from <ns> namespace` (pre-check #4)
- NodePort `30080` ถูกจองทั้งคลัสเตอร์ → LAB8 ต้องลบ `web-nodeport` ก่อนเริ่ม LAB10

### แอปตัวอย่าง LAB1–LAB9 (ไม่ต้อง build)

ReplicaSet `web` ใน ns `shop`: `nginx:1.27-alpine`, label `app=web`, `ports: [{name: http, containerPort: 80}]`, `command: ["sh","-c","echo \"web $VERSION from $(hostname)\" > /usr/share/nginx/html/index.html && exec nginx -g 'daemon off;'"]`, env `VERSION=v1`, readinessProbe `httpGet / port http periodSeconds 2` → `wget`/`curl` เห็นชื่อ Pod ทันที (`web v1 from web-7xkqp`)

### ผล pre-check ที่เกี่ยวข้อง (คัดลอกจาก `precheck.md` พร้อมเลขข้อเดิม)

| # | คำถาม | ผลจริง | ผลต่อแผน |
|---|---|---|---|
| 1 | kube-proxy mode ของ kind 0.33 | `mode: iptables` (ConfigMap `kube-proxy` ใน kube-system); Service CIDR `10.96.0.0/16` (`kubernetes` = `10.96.0.1`, DNS `10.96.0.10`) | ทฤษฎีอธิบาย iptables เป็นหลัก กล่าวถึง nftables/ipvs ว่าเป็นโหมดอื่น; LAB ให้ดู mode จริง |
| 4 | ลบ Pod ของ RS | ตัวใหม่ขึ้นภายใน ~3 วิ (ตัวเก่ายัง Terminating อยู่ก็สร้างแล้ว); ownerReferences `{"kind":"ReplicaSet","name":"snack-rs","controller":true,"blockOwnerDeletion":true}`; kubectl 1.37 พิมพ์ `pod "x" deleted from default namespace` | ภาพ/README ใช้ข้อความรูปแบบใหม่ |
| 6 | `kind load docker-image nginx:1.27-alpine` | **ล้มเหลว** `ctr: content digest sha256:...: not found` (image multi-arch แบบเดียวกับ postgres บท 004) แต่ Node ดึง image จาก Docker Hub เองได้ → rollout ผ่าน | LAB ไม่ต้อง `kind load` image สาธารณะ (nginx/busybox) ให้ Node pull เอง; image ที่ build เอง (`som-shop-web`) ยังต้อง `kind load docker-image`; postgres ใช้ `docker save --platform linux/amd64` + `kind load image-archive` หรือให้ Node pull เอง |
| 11 | Endpoints vs EndpointSlice | `kubectl get endpoints` → `Warning: v1 Endpoints is deprecated in v1.33+; use discovery.k8s.io/v1 EndpointSlice`; `kubectl get endpointslice -l kubernetes.io/service-name=web` → `web-krm6m IPv4 80 10.244.2.7,10.244.1.4,10.244.2.8` | สอน EndpointSlice เป็นหลัก |
| 12 | Pod ไม่ ready | Pod `0/1 Running`; **คอลัมน์ ENDPOINTS ของ `get endpointslice` ยังแสดง 3 IP** แต่ `.endpoints[].conditions.ready` = `false` สำหรับตัวนั้น (kube-proxy ไม่ส่งไป) | กับดัก: ดู ready ด้วย jsonpath/`describe endpointslice` |
| 13 | selector ผิด | EndpointSlice `PORTS <unset> ENDPOINTS <unset>`; `describe svc` → `Endpoints:` ว่าง; `wget` → `wget: can't connect to remote host (10.96.27.5): Connection refused` | LAB7 debug |
| 14 | DNS | `nslookup web.default.svc.cluster.local` → `Address: 10.96.47.123`; resolv.conf `search default.svc.cluster.local svc.cluster.local cluster.local` / `nameserver 10.96.0.10` / `options ndots:5`; headless (`clusterIP: None`) คืน Pod IP 3 ตัว | ✓ |
| 15 | NodePort ผิดช่วง | `Invalid value: 29999: provided port is not in the valid range. The range of valid ports is 30000-32767` | ✓ |
| 16 | LoadBalancer ใน kind | `EXTERNAL-IP <pending>`, ได้ nodePort อัตโนมัติ (`80:30456/TCP`) | ทฤษฎี + LAB8 ลองเพิ่ม |
| 17 | ExternalName | `ext ExternalName <none> example.com` | ทฤษฎีสั้น + LAB9 |
| 18 | การกระจายโหลด (iptables สุ่ม) | ClusterIP 9 ครั้ง → 5/4/**0** (ไม่ round-robin); NodePort 12 ครั้ง → 5/5/2 | LAB5 ยิง ≥30 ครั้ง แล้ว `sort \| uniq -c`; อธิบายว่าสุ่ม |
| 19 | NodePort ผ่าน extraPortMappings จากนอก container | host `:30090`/`:30091` (map → 30080/30081 ของ container → kind control-plane) ได้หน้าเว็บ และกระจายหลาย Pod | เครื่องนักศึกษาใช้ `http://localhost:30080` ตรง ๆ (ต้องยืนยันบน k8s-lab จริง) |
| 20 | browser keep-alive | Chromium (Playwright) `fetch('/')` 10 ครั้ง → **Pod เดียวกัน 10/10** | LAB8/10: browser ติด Pod เดียว ให้ใช้ curl วนดูการกระจาย |
| 23 | seed พร้อมกัน 3 replicas (initContainer `db-seed` ของบท 004) | **2 ใน 3 Pod init restart 1 ครั้ง** `error: duplicate key value violates unique constraint "pg_type_typname_nsp_index"` (code `23505`, `CREATE TABLE IF NOT EXISTS` ชนกัน) แล้วรอบที่สองผ่าน (`seeded 6 products (new: 0)`) | 1.2 ใช้ `pg_advisory_xact_lock` ครอบ seed; README อธิบาย race |
| 24 | web ต่อ db ผ่าน Service `som-db` | ได้ (`DATABASE_URL=postgres://som:meow1234@som-db:5432/catshop`); rollout 3 replicas 13.6 วิ | ✓ (บทนี้ใช้ ReplicaSet แทน Deployment — เวลาเริ่ม Pod ต้องวัดใหม่) |
| 25 | ลบ Pod db (emptyDir) | Pod ใหม่พร้อมใน 4.2 วิ; `relation "orders" does not exist`; หน้าเว็บ **HTTP 500** ขณะที่ `/api/health` ยัง `{"ok":true,"db":"up"}` → web ยัง Ready; initContainer ไม่รันซ้ำเอง ต้อง `kubectl rollout restart deploy/som-web` จึงสร้างตารางใหม่ (ข้อมูลเดิมหาย) | 1.2: หน้าเว็บแสดงข้อความเป็นมิตร + 503 แทน 500; **บทนี้ยังไม่รู้ rollout → เติมสินค้าใหม่ด้วยการลบ Pod web 1 ตัว** (initContainer ของ Pod ใหม่รัน) |
| 26 | build `som-shop-web:1.1` ใน container | 28.6 วิ | 1.2/1.3 build จาก source เดียวด้วย build-arg ~30 วิ/ครั้ง (ครั้งที่สองเร็วกว่าเพราะ cache) |
| 27 | API สั่งซื้อ | `POST /api/orders` body `{"product_id":1,"qty":2}` → `{"ok":true,"order_id":1,...}` | ใช้ใน LAB10 พิสูจน์ออเดอร์รวม db เดียว และข้อมูลหาย |

ข้อ 2, 3, 5, 7–10, 21, 22 เป็นเรื่อง ReplicaSet (บท 005) และ Deployment/rollout/zero-downtime (บท 007) — บทนี้อ้างถึง #21/#22 เป็นข้อมูลประกอบหลักการ preStop ในทฤษฎีหัวข้อ 12 เท่านั้น

### อุปมา (ต่อจากบท 001–005 + ของใหม่บทนี้)

| Kubernetes | อุปมาท่าเรือ | ใหม่? |
|---|---|---|
| container / Pod / Node / Control Plane / Namespace | ตู้สินค้า / กล่องใส teal มีป้าย IP เป็น "บูธร้าน" มีกันสาด / เรือ / หอบังคับการ / โซนทาสี | – |
| label / ReplicaSet / Pod template | ป้ายห้อยกระเป๋าสี / หัวหน้ากะ (หุ่นยนต์ teal ถือคลิปบอร์ดนับหัว) / พิมพ์เขียว | บท 005 |
| **Service** | **ประภาคาร/เคาน์เตอร์ต้อนรับ** บนท่า มีป้ายชื่อและป้ายที่อยู่คงที่ ส่งลูกค้าไปบูธที่พร้อม | ใหม่ |
| ClusterIP | ป้ายที่อยู่ของประภาคาร — เป็นภาพโฮโลแกรม ไม่มีคนอยู่ข้างใน (ping ไม่ตอบ) | ใหม่ |
| EndpointSlice | คลิปบอร์ดรายชื่อบูธที่เปิดอยู่ ติดข้างประภาคาร (≤100 แถวต่อแผ่น) | ใหม่ |
| EndpointSlice controller | เสมียนหุ่นยนต์ในหอ ส่องกล้องดูบูธแล้วเขียนคลิปบอร์ด | ใหม่ |
| readinessProbe | ไฟเขียวหน้าบูธ (ไฟแดง = ไม่ได้ลูกค้า) | ใหม่ (ต่อบท 002) |
| kube-proxy | ป้ายบอกทางบนเรือทุกลำ (และที่ท่าหอ) — หุ่นยนต์ทาสีป้ายฟังวิทยุจากหอ | ใหม่ |
| NodePort | ประตูทางขึ้นเรือหมายเลข 30080 บนทุก Node | ใหม่ |
| LoadBalancer | เครนของผู้ให้บริการคลาวด์ที่ส่งป้ายที่อยู่สาธารณะ (ใน kind ไม่มา → `<pending>`) | ใหม่ |
| ExternalName | เสาป้ายชี้ออกทะเลไปเกาะซัพพลายเออร์ | ใหม่ |
| headless | สมุดโทรศัพท์รายชื่อบูธ (ไม่มีเคาน์เตอร์กลาง — ห้ามวาดคนไม่มีหัว) | ใหม่ |
| sessionAffinity | บัตรสมาชิกที่พาลูกค้าไปบูธเดิม | ใหม่ |
| keep-alive | เชือกเส้นเดียวผูกลูกค้ากับบูธเดียว | ใหม่ |
| NetworkPolicy | รั้ว + ยามหน้าประตูโซน (บท 004) ตรวจหลังป้ายบอกทางเปลี่ยนที่อยู่แล้ว | ต่อบท 004 |
| (บท 007) Deployment | เงาผู้จัดการร้าน (หุ่นยนต์กรมท่าผูกหูกระต่าย) — ปรากฏเฉพาะภาพปูทาง T36/L24 | ปูทาง |

### เรื่องเล่า

บท 005 จบลงที่ร้านน้องส้มมี 3 บูธที่หัวหน้ากะดูแลให้ครบเสมอ แต่ลูกค้ายังหาร้านไม่เจอ: บูธเกิดใหม่ทีไรได้ IP ใหม่ น้องส้มต้อง port-forward ทีละบูธ สายหลุดทุกครั้งที่บูธถูกแทน และแต่ละบูธมีฐานข้อมูลของตัวเอง ออเดอร์ไม่ตรงกัน บทนี้น้องส้มสร้าง **ประภาคาร** ที่ชื่อและที่อยู่ไม่เคยเปลี่ยน มี **คลิปบอร์ดรายชื่อบูธที่ไฟเขียว** ที่อัปเดตเอง ติด **ป้ายบอกทางบนเรือทุกลำ** เปิด **ประตูหมายเลข 30080** ให้ลูกค้าจาก browser และปิดท้ายด้วยการ **แยกครัวกลาง (db) ออกจากหน้าร้าน (web)** ครั้งแรก — ออเดอร์จากทุกบูธรวมที่เดียว แก้ปัญหาบท 005 ได้ แต่เมื่ออยากเปลี่ยนเมนูเป็นรุ่น 1.3 หัวหน้ากะไม่เปลี่ยนบูธเดิมให้ น้องส้มต้องรื้อบูธเองจนร้านสะดุด — ไปสู่ "ผู้จัดการร้าน" (Deployment) บทที่ 7

## 1. โครงสารบัญทฤษฎี (`01_Theory/README.md`)

หัวเอกสารแบบบท 001–005: รายวิชา/หัวข้อ/CLO, บทก่อนหน้า (ลิงก์บท 005), บทคัดย่อ, วัตถุประสงค์การเรียนรู้ (~12 ข้อ), สารบัญ, สารบัญรูปภาพ, ตารางอุปมา; ทุก output ใช้ "ผลจริง" จาก pre-check/การรัน LAB (หลังทดสอบ)

1. **บทนำ: บูธครบ 3 แต่ลูกค้าหาไม่เจอ** (T01–T03)
   - ทบทวนบท 005: ReplicaSet ทำให้จำนวนบูธครบ แต่ (ก) Pod ใหม่ = ชื่อใหม่ + IP ใหม่ (ข) port-forward ผูกกับ Pod เดียว หลุดเมื่อ Pod ถูกลบ (บท 004 LAB10, บท 005 LAB สุดท้าย) (ค) แต่ละบูธมี db ของตัวเอง ออเดอร์ไม่ตรงกัน
   - เป้าหมายบท: ที่อยู่คงที่ + กระจายลูกค้า + ส่งเฉพาะบูธที่พร้อม + เปิดร้านสู่ภายนอก + แยก web/db
   - ตารางอุปมาใหม่ (T02)
2. **ทำไมต้องมี Service** (T04–T06)
   - Service = ชื่อคงที่ (DNS) + virtual IP (ClusterIP) + การเลือก Pod ด้วย selector; Service เป็น object ใน API ไม่ใช่โปรแกรมที่รันอยู่บนเครื่องใด
   - ClusterIP ไม่ผูกกับ interface ไหน → `ping` ไม่ตอบ (โหมด iptables) แต่ TCP ไปที่ port ของ Service ได้ (T05)
   - โครง manifest `v1 Service`: `selector`, `ports[]`, `type` (default ClusterIP); selector ไม่สนว่าใครสร้าง Pod (ReplicaSet, Pod เดี่ยว, ภายหลัง Deployment) — ต่างจาก ReplicaSet ตรงที่ Service **ไม่เป็นเจ้าของ** Pod (ไม่มี ownerReferences) (T06)
   - สร้างได้ 2 ทาง: `kubectl expose rs web --port=80` (คัดลอก selector จาก RS) หรือเขียน YAML (แนะนำ)
3. **selector → EndpointSlice** (T07–T09)
   - EndpointSlice controller (ใน kube-controller-manager) watch Service + Pod → เขียน `discovery.k8s.io/v1 EndpointSlice` ที่ติด label `kubernetes.io/service-name=<svc>`, ownerReferences ชี้ Service; 1 slice ≤ 100 endpoint (เกินแตกหลาย slice); ชื่อ slice = `<svc>-<สุ่ม>` (pre-check `web-krm6m`)
   - แต่ละ endpoint: addresses, `conditions.ready/serving/terminating`, nodeName, targetRef (Pod)
   - v1 Endpoints: deprecated ตั้งแต่ v1.33 คำเตือนจริง (pre-check #11); ยังเห็นใน `describe svc` บรรทัด `Endpoints:`
   - Service ไม่มี selector + EndpointSlice ทำมือ (ชี้ IP นอกคลัสเตอร์ เช่น db เดิมของบริษัท) — กล่าวถึงพร้อม YAML ตัวอย่างสั้น (ไม่มี LAB)
4. **ClusterIP และ Service CIDR** (T10)
   - ช่วง Service CIDR ของ kind `10.96.0.0/16` แยกจาก Pod CIDR `10.244.0.0/16`; `kubernetes` (default) = `10.96.0.1` (ทางเข้า API server จากใน Pod), `kube-dns` (kube-system) = `10.96.0.10` (pre-check #1); กำหนด `clusterIP` เองได้แต่ไม่แนะนำ; ClusterIP ไม่เปลี่ยนตลอดอายุ Service (ลบแล้วสร้างใหม่ = IP ใหม่)
5. **พอร์ต: port / targetPort / nodePort / protocol / named port** (T11–T12)
   - `port` (ที่ Service รับ) → `targetPort` (ที่ container ฟัง; ไม่ใส่ = เท่ากับ port) / `nodePort` (เฉพาะ NodePort/LoadBalancer); `protocol` TCP (default) / UDP / SCTP
   - named port: `targetPort: http` อ้าง `containerPort` ที่ชื่อ `http` → แต่ละ Pod ใช้เลขต่างกันได้ เปลี่ยนเลขใน Pod โดยไม่แก้ Service
   - หลายพอร์ตใน Service เดียวต้องตั้ง `name` ทุกพอร์ต (ไม่ตั้ง → API ปฏิเสธ — ข้อความจริงยืนยันใน LAB3)
6. **NodePort** (T13–T15)
   - ช่วง **30000–32767** (error จริงเมื่อผิดช่วง pre-check #15), เปิดบน **ทุก Node** (รวม control-plane), ระบุเองหรือให้สุ่ม, ซ้ำไม่ได้ทั้งคลัสเตอร์ (`provided port is already allocated` — ยืนยันใน LAB8); NodePort = ClusterIP + ประตูบนทุก Node
   - ทำไม `http://localhost:30080` บนเครื่องนักศึกษาใช้ได้: Docker publish 30080 ของเครื่อง → container `k8s-lab` → kind `extraPortMappings` (ตั้งไว้ตั้งแต่บท 001, เปิด `kind-config` ให้ดู) → `lab-control-plane:30080` → kube-proxy บน control-plane → Pod บนเรือลำใดก็ได้ (T14); 30081/30082 เผื่อร้านอื่น
   - ข้อจำกัด: พอร์ตแปลก, ต้องรู้ IP ของ Node, ไม่มี TLS/ชื่อโดเมน → LoadBalancer/Ingress
7. **LoadBalancer** (T16)
   - บนคลาวด์ cloud-controller-manager สร้าง LB ภายนอกแล้วเขียน `status.loadBalancer.ingress`; LoadBalancer = NodePort + ClusterIP + LB ภายนอก
   - kind ไม่มีตัวจัดสรร → `EXTERNAL-IP <pending>` แต่ได้ nodePort (`80:30456/TCP` pre-check #16); ทางเลือก cloud-provider-kind / MetalLB (กล่าวถึง)
8. **ExternalName และ headless** (T17–T18)
   - ExternalName: CNAME ไปชื่อนอกคลัสเตอร์ (`supplier` → `example.com`, pre-check #17 `ext ExternalName <none> example.com`) ไม่มี ClusterIP/selector/proxy; ข้อควรระวัง HTTP Host header/TLS ไม่ตรง
   - headless `clusterIP: None`: DNS คืน A record ของทุก Pod ที่ ready (pre-check #14 คืน 3 IP) ไม่มีการกระจายโดย kube-proxy — ลูกค้าเลือกเอง; ปูทาง workload ที่ต้องเรียก Pod รายตัว (ฐานข้อมูลแบบมีหลายตัว — บทหลัง)
9. **DNS ของ Service** (T19–T21)
   - A record `<svc>.<ns>.svc.cluster.local` → ClusterIP (headless → Pod IP); CoreDNS ที่ `10.96.0.10`
   - resolv.conf (บท 004): `search <ns>.svc.cluster.local svc.cluster.local cluster.local`, `options ndots:5` → ชื่อที่มีจุด < 5 ลองเติม search ทีละตัว; ชื่อสั้น `web` ได้เฉพาะ ns เดียวกัน, ข้าม ns ใช้ `web.shop` (`shop` ไม่ใช่โดเมนจริง แต่ตรงกับ search `svc.cluster.local`) หรือชื่อเต็ม; ชื่อเต็มลงท้ายจุด `web.shop.svc.cluster.local.` ข้ามการเติม search
   - SRV record `_http._tcp.web.shop.svc.cluster.local` สำหรับ named port (กล่าวถึง)
   - env var: kubelet ใส่ `WEB_SERVICE_HOST` / `WEB_SERVICE_PORT` (+ `WEB_PORT_80_TCP...` แบบ docker link) เฉพาะ Pod ที่สร้าง **หลัง** Service และเฉพาะ ns เดียวกัน → ลำดับการสร้างมีผล ใช้ DNS ดีกว่า; ปิดด้วย `enableServiceLinks: false` (T21)
10. **kube-proxy: ป้ายบอกทางบนเรือทุกลำ** (T22–T23)
    - DaemonSet `kube-proxy` ใน kube-system (1 Pod ต่อ Node — `kubectl -n kube-system get ds,pods -l k8s-app=kube-proxy -o wide`) watch Service + EndpointSlice → เขียนกฎในเคอร์เนลของ Node
    - kind = `iptables` (pre-check #1); โหมดอื่น `nftables` (ใหม่กว่า), `ipvs`; DNAT ที่ Node ต้นทาง (ClusterIP → Pod IP) ไม่มี "เครื่องประภาคาร" จริง ไม่มีคอขวดกลาง
    - (ทางเลือก) ดูกฎ: `docker exec lab-worker iptables-save | grep 'shop/web'` — เห็น chain `KUBE-SVC-...`/`KUBE-SEP-...` และ `--probability`
11. **การกระจายโหลด** (T24–T26)
    - iptables เลือก endpoint แบบสุ่มต่อ connection (ไม่ใช่ round-robin, ไม่ใช่ต่อ request): pre-check #18 ClusterIP 9 ครั้ง 5/4/0, NodePort 12 ครั้ง 5/5/2 → ต้องยิง ≥30 ครั้งถึงเห็นภาพรวม
    - keep-alive: browser ใช้ connection เดิม → Pod เดิม (pre-check #20 Chromium 10/10) — ไม่ใช่ว่ามี Pod เดียว
    - `sessionAffinity: ClientIP` + `sessionAffinityConfig.clientIP.timeoutSeconds` (default 10800); ข้อเสีย: ลูกค้าหลังเครื่อง NAT เดียวไปบูธเดียว
    - `internalTrafficPolicy` / `externalTrafficPolicy: Local` (ส่งเฉพาะ Pod บน Node เดียวกัน, รักษา IP ต้นทาง) — กล่าวถึง
12. **readinessProbe ↔ endpoints** (T27–T28)
    - Pod ไม่ ready → endpoint `conditions.ready=false` kube-proxy ไม่ส่งไป แต่ **คอลัมน์ ENDPOINTS ของ `kubectl get endpointslice` ยังแสดง IP** (pre-check #12) → ดูด้วย jsonpath หรือ `describe endpointslice`
    - Pod ที่ถูกลบ: `ready=false, serving=true/false, terminating=true`; ระหว่าง kube-proxy ทุก Node อัปเดตกฎ มีช่วงสั้น ๆ ที่ connection ใหม่ยังไปถึง Pod ที่กำลังปิด → หลักการ `preStop` รอสั้น ๆ + แอปปิดแบบ graceful (pre-check #21/#22 ตัวเลขอ้างอิง) — **ลงมือในบท 007**
    - liveness ไม่ควรพึ่ง db (บทเรียนสำหรับ 1.2: `/api/live` แยกจาก `/api/health`)
13. **debug Service ทีละขั้น** (T29–T31)
    - (1) `get svc`/`describe svc` (2) `get endpointslice -l kubernetes.io/service-name=<svc>` ว่าง? (3) เทียบ `selector` กับ `get pods --show-labels` (4) มี endpoint แต่ `Connection refused` → `targetPort` ตรงพอร์ตที่แอปฟังไหม (5) Pod READY ไหม / `ready=false` (6) DNS `nslookup` (7) ข้าม namespace ใช้ชื่อถูกไหม + NetworkPolicy (timed out ≠ refused)
    - ตัวอย่างผลจริง: selector ผิด → `ENDPOINTS <unset>` + `Connection refused` (pre-check #13 — iptables REJECT เมื่อ Service ไม่มี endpoint); targetPort ผิด → ยืนยันใน LAB7; DNS ผิด → `bad address` (ยืนยันใน LAB7/9)
14. **NetworkPolicy กับ Service** (T32)
    - policy เลือก **Pod** (podSelector) ไม่ใช่ Service; ตรวจที่ Pod ปลายทาง **หลัง DNAT** → `ports` ใน policy ต้องเป็น **targetPort/containerPort** ไม่ใช่ `port` ของ Service; ต้นทางที่เห็นคือ Pod IP ต้นทาง (หรือ Node IP เมื่อเข้าทาง NodePort แบบ Cluster — เตือนว่า policy ที่ใช้ namespaceSelector อาจกั้นลูกค้า NodePort)
    - ต่อบท 004 LAB4 (kindnet บังคับใช้ NetworkPolicy, ถูกกั้น = `download timed out`)
15. **ข้อจำกัดที่ Service ยังไม่ช่วย** (T33)
    - เปลี่ยนรุ่น: แก้ template ของ ReplicaSet (`kubectl set image rs/...`) → Pod เดิมไม่เปลี่ยน ต้องลบ Pod เอง → ร้านสะดุด/ไม่มีประวัติย้อนรุ่น → **บท 007 Deployment**
    - db บน emptyDir หายเมื่อ Pod db เกิดใหม่ → PersistentVolume/PVC (บทหลัง)
    - ลูกค้าภายนอกต้องจำเลขประตู → Ingress/Gateway + ชื่อโดเมน (บทหลัง)
16. **สรุปและบทถัดไป** (T34–T36)
    - ตารางเลือกชนิด Service: ClusterIP (ภายใน — ค่าเริ่มต้น) / NodePort (LAB, on-prem ง่าย ๆ) / LoadBalancer (คลาวด์) / ExternalName (ชื่อภายนอก) / headless (ต้องการ IP ของทุก Pod) / ไม่มี selector + EndpointSlice เอง (ปลายทางนอกคลัสเตอร์)
    - ตารางคำสั่ง: `expose`, `get svc,endpointslice`, `describe svc`, `get endpointslice -l kubernetes.io/service-name=...`, jsonpath conditions, `nslookup`, `kubectl patch svc`, `kubectl create service nodeport`
    - ปูทางบท 007 (T36 — allow): ผู้จัดการร้าน Deployment

## 2. รายการ LAB (`02_LAB/README.md`)

```text
02_LAB/
  README.md
  images/ (L01–L24 + imagegen-prompts.md)
  labs/
    lab01-before-service/{00-ns.yaml (shop), web-rs.yaml (ReplicaSet web nginx 3), client-pod.yaml (busybox client)}
    lab02-clusterip/{web-svc.yaml (ClusterIP port 80 → targetPort http)}
    lab03-ports/{web-alt-svc.yaml (port 8080 → targetPort http), web-multi-svc.yaml (2 พอร์ตมีชื่อ), web-multi-noname.yaml (ตั้งใจผิด)}
    lab04-dns/{client2-pod.yaml}
    lab07-debug/{web-typo-svc.yaml (selector app=wbe), web-badport-svc.yaml (targetPort 8080)}
    lab08-nodeport/{web-nodeport.yaml (NodePort 30080), web-dup-nodeport.yaml (30080 ซ้ำ), web-lb.yaml (LoadBalancer)}
    lab09-cross-ns/{kitchen.yaml (ns kitchen + busybox cook), web-headless.yaml, supplier-externalname.yaml, np-kitchen-8080.yaml, np-kitchen-80.yaml}
  som-shop-v2/
    app/       (สำเนาจาก 004 som-shop-envs/app + แก้เป็น 1.2/1.3 ดูหัวข้อ 3.3)
    k8s/{00-namespace.yaml, 10-db.yaml, 20-web.yaml}
    hit.sh     (bash + curl ใน k8s-lab)
```

| LAB | ชื่อ | เป้าหมาย | ไฟล์ | คำสั่งหลัก | ผลที่ต้องเห็น | สิ่งที่ต้องยืนยันตอนทดสอบ |
|---|---|---|---|---|---|---|
| 0 | เตรียมคลัสเตอร์และตรวจพอร์ต | คลัสเตอร์พร้อม, 30080–30082 ว่าง, รู้จัก Service ที่มีอยู่แล้ว | – | `docker cp 006_kubernetes_service k8s-lab:/workspace/`; `kubectl get nodes`; `kubectl get svc -A \| grep -E '3008[0-2]'` (ต้องไม่มี — ถ้ามี `web` จาก `/workspace/examples` บท 001 ให้ `kubectl delete -f ...`); `kubectl get svc -A`; `kubectl get svc kubernetes`; `kubectl -n kube-system get cm kube-proxy -o yaml \| grep mode`; `kubectl -n kube-system get ds kube-proxy`; `docker exec lab-control-plane cat /kind/kubeadm.conf \| grep -i serviceSubnet` (หรือดู kind config ของบท 001) | 3 Node Ready; ไม่มี Service ใช้ 3008x; `kubernetes ClusterIP 10.96.0.1 443/TCP`, `kube-dns 10.96.0.10 53/UDP,53/TCP,9153/TCP`; `mode: iptables`; kube-proxy DESIRED 3 | ตัวอย่าง NodePort ของบท 001 ค้างในเครื่องนักศึกษาไหม (ชื่อไฟล์/คำสั่งลบที่ถูก); วิธีดู serviceSubnet ที่ใช้ได้จริงใน kind 0.33; คอลัมน์ PORT(S) ของ kube-dns |
| 1 | ปัญหาก่อนมี Service | เห็นว่า Pod IP เปลี่ยนเมื่อ RS สร้างแทน — จด IP ไว้ใช้ไม่ได้ | `lab01-before-service/` | `kubectl apply -f labs/lab01-before-service/`; `kubectl -n shop get rs,pods -o wide --show-labels`; `kubectl -n shop exec client -- wget -qO- http://<IP>`; `kubectl -n shop delete pod <ตัวที่เรียก>`; เรียก IP เดิมซ้ำ; `get pods -o wide` อีกครั้ง | `web v1 from web-xxxxx`; หลังลบ: `pod "web-xxxxx" deleted from shop namespace`, Pod ใหม่ชื่อ/IP ใหม่, wget IP เดิม → timeout/`No route to host`/`Connection refused` | ข้อความ wget เมื่อเรียก IP ที่ไม่มีแล้ว (ขึ้นกับว่ามี Pod อื่นได้ IP นั้นไหม) — ใช้ `-T 3` |
| 2 | ClusterIP แรก + EndpointSlice | สร้าง Service 2 วิธี, อ่าน EndpointSlice, เห็นว่ารายชื่อตาม Pod อัตโนมัติ | `lab02-clusterip/web-svc.yaml` | `kubectl -n shop expose rs web --port=80 --name=web-quick` → `kubectl -n shop get svc web-quick -o yaml` (selector คัดลอกจาก RS) → ลบ; `kubectl apply -f labs/lab02-clusterip/web-svc.yaml`; `kubectl -n shop get svc,endpointslice`; `kubectl -n shop get endpoints web` (คำเตือน); `kubectl -n shop describe svc web`; `kubectl -n shop get endpointslice -l kubernetes.io/service-name=web -o yaml`; `kubectl -n shop exec client -- wget -qO- http://web`; `kubectl -n shop exec client -- ping -c 2 -W 2 <ClusterIP>`; `kubectl -n shop scale rs web --replicas=5` แล้ว `get endpointslice`; ลบ Pod 1 ตัว แล้วดูอีก; scale กลับ 3 | `web ClusterIP 10.96.x.x 80/TCP`; EndpointSlice 3 IP ตรงกับ `get pods -o wide`; `Warning: v1 Endpoints is deprecated in v1.33+; use discovery.k8s.io/v1 EndpointSlice`; ping 100% packet loss แต่ wget ได้; scale 5 → 5 IP, ลบ Pod → IP ใหม่แทนที่ ClusterIP ไม่เปลี่ยน | ping ClusterIP ใน iptables mode ได้ 100% loss จริง (ไม่ใช่ error อื่น); ลำดับ IP ในคอลัมน์; ownerReferences ของ EndpointSlice ชี้ Service |
| 3 | port / targetPort / named port / multi-port | เข้าใจพอร์ต 3 ชั้นและชื่อพอร์ต | `lab03-ports/` | `kubectl apply -f web-alt-svc.yaml`; `wget -qO- http://web-alt:8080`; `wget -T 3 http://web-alt` (port 80 ไม่มี → ไม่ได้); `kubectl apply -f web-multi-svc.yaml` (ports `http 80→http`, `alt 8080→http`) แล้ว `get endpointslice` (PORTS 80); `kubectl apply -f web-multi-noname.yaml` | web-alt:8080 ได้หน้าเว็บ; port 80 ของ web-alt timed out/refused; multi-port ใช้ได้ทั้งสองพอร์ต; ไม่ใส่ชื่อ → `spec.ports[1].name: Required value` | ข้อความ error จริงของ multi-port ไม่มีชื่อ; ผล wget ไปพอร์ตที่ Service ไม่ได้เปิด (คาด timeout เพราะไม่มีกฎ — ยืนยัน) |
| 4 | DNS, search domain, env var | เรียกด้วยชื่อ, เข้าใจ search/ndots, env var มีเฉพาะ Pod หลัง Service | `lab04-dns/client2-pod.yaml` | `kubectl -n shop exec client -- nslookup web`; `... nslookup web.shop.svc.cluster.local`; `... cat /etc/resolv.conf`; `kubectl -n shop exec client -- env \| grep WEB_` (ว่าง — client สร้างใน LAB1 ก่อน Service); `kubectl apply -f client2-pod.yaml` → `env \| grep WEB_`; `kubectl -n shop exec <web pod เก่า> -- env \| grep WEB_` เทียบกับ Pod web ที่สร้างหลัง LAB2 | `Name: web.shop.svc.cluster.local Address: 10.96.x.x`; search `shop.svc.cluster.local ...` ndots:5; client เก่าไม่มี env, client2 มี `WEB_SERVICE_HOST=10.96.x.x`, `WEB_SERVICE_PORT=80`, `WEB_ALT_SERVICE_PORT=8080` | รูปแบบผล nslookup ของ busybox 1.36 (มีบรรทัด NXDOMAIN/`*** Can't find` ปนไหม); ชื่อ env ที่ได้จริงรวม `WEB_SERVICE_PORT_HTTP` |
| 5 | การกระจายโหลด + sessionAffinity | เห็นการสุ่มต่อ connection และผลของ ClientIP | ใช้ของเดิม | `kubectl -n shop exec client -- sh -c 'for i in $(seq 30); do wget -qO- http://web; done' \| sort \| uniq -c`; ทำซ้ำ 2 รอบเทียบ; `kubectl -n shop patch svc web -p '{"spec":{"sessionAffinity":"ClientIP"}}'` แล้วยิงซ้ำ; `kubectl -n shop get svc web -o jsonpath='{.spec.sessionAffinityConfig}'`; patch กลับ `"None"` | 30 ครั้งกระจาย 3 Pod ไม่เท่ากัน (แต่ละรอบต่างกัน); ClientIP → Pod เดียว 30/30; timeoutSeconds 10800 | `seq` มีใน busybox 1.36; สัดส่วนจริง; patch กลับ None แล้ว `sessionAffinityConfig` หายไหม |
| 6 | readinessProbe กับ endpoints | Pod ไม่ ready ยังอยู่ในรายชื่อแต่ไม่ได้ลูกค้า | ใช้ของเดิม | `POD=$(kubectl -n shop get pod -l app=web -o name \| head -1)`; `kubectl -n shop exec $POD -- rm /usr/share/nginx/html/index.html`; `kubectl -n shop get pods -w` (0/1); `kubectl -n shop get endpointslice -l kubernetes.io/service-name=web`; `kubectl -n shop get endpointslice -l kubernetes.io/service-name=web -o jsonpath='{range .items[0].endpoints[*]}{.addresses[0]} {.targetRef.name} ready={.conditions.ready}{"\n"}{end}'`; ยิง 30 ครั้ง; `kubectl -n shop describe pod $POD \| grep Readiness`; คืนไฟล์ `kubectl -n shop exec $POD -- sh -c 'echo "web v1 from $(hostname)" > /usr/share/nginx/html/index.html'` | Pod `0/1 Running`; ENDPOINTS ยังแสดง 3 IP แต่ `ready=false` 1 ตัว; 30 ครั้งไม่ไปตัวนั้น; Event `Readiness probe failed: HTTP probe failed with statuscode: 403`; คืนไฟล์แล้วกลับ `1/1` และ `ready=true` | statuscode ที่ nginx ตอบเมื่อไม่มี index.html (คาด 403); เวลาที่ ready=false ปรากฏ (period 2 วิ × failureThreshold 3) |
| 7 | debug Service | ไล่ debug selector ผิด, targetPort ผิด, ชื่อ DNS ผิด | `lab07-debug/` | apply ทั้งสอง; `kubectl -n shop exec client -- wget -qO- -T 3 http://web-typo`; `get endpointslice -l kubernetes.io/service-name=web-typo`; `describe svc web-typo`; `get pods --show-labels`; แก้ด้วย `kubectl -n shop patch svc web-typo -p '{"spec":{"selector":{"app":"web"}}}'`; `wget http://web-badport`; `get endpointslice ... web-badport` (PORTS 8080); แก้ targetPort เป็น `http`; `wget http://wbe` | typo: `PORTS <unset> ENDPOINTS <unset>`, `wget: can't connect to remote host (10.96.x.x): Connection refused`; badport: มี 3 endpoint แต่ `Connection refused`; DNS ผิด: `wget: bad address 'wbe'`; แก้แล้วได้หน้าเว็บ | ข้อความของ badport (refused หรือ timeout); ข้อความ `bad address` ของ busybox |
| 8 | NodePort 30080, LoadBalancer, keep-alive | เปิดเว็บจาก browser เครื่องนักศึกษา, เข้าใจกติกา NodePort | `lab08-nodeport/` | `kubectl apply -f web-nodeport.yaml`; `kubectl -n shop get svc web-nodeport` (`80:30080/TCP`); ใน k8s-lab: `curl -s localhost:30080`; ทุก Node: `for n in lab-control-plane lab-worker lab-worker2; do curl -s http://$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $n):30080; done`; **เครื่องนักศึกษา:** `http://localhost:30080` + refresh/Ctrl+F5; `for i in $(seq 30); do curl -s localhost:30080; done \| sort \| uniq -c` (หรือ PowerShell `1..30 \| % { curl.exe -s localhost:30080 } \| group`); `kubectl -n shop create service nodeport bad --tcp=80:80 --node-port=29999`; `kubectl apply -f web-dup-nodeport.yaml`; `kubectl apply -f web-lb.yaml` → `get svc web-lb` → ลบ; **ลบ `web-nodeport`** | browser เห็น `web v1 from web-...` (มักชื่อเดิมเมื่อ refresh); curl วนเห็นหลาย Pod; ทั้ง 3 Node ตอบที่ 30080; `The range of valid ports is 30000-32767`; `provided port is already allocated`; LB `EXTERNAL-IP <pending>` `80:3xxxx/TCP`; หลังลบ `get svc -A \| grep 30080` ว่าง | **NodePort จาก host Windows/macOS ผ่าน extraPortMappings จริง** (screenshot); Chrome/Edge ติด Pod เดียวจริงไหม, Ctrl+F5/Incognito เปลี่ยนไหม; คำสั่ง PowerShell; ข้อความ dup nodePort จริง; IP ของ kind node เรียกจาก k8s-lab ได้ |
| 9 | ข้าม namespace, headless, ExternalName, NetworkPolicy | เรียก Service ข้าม ns, เทียบ DNS ของ headless/ExternalName, policy ใช้ targetPort | `lab09-cross-ns/` | `kubectl apply -f kitchen.yaml`; `kubectl -n kitchen exec cook -- wget -qO- -T 3 http://web` (ล้ม) / `http://web.shop` / `http://web.shop.svc.cluster.local`; `cat /etc/resolv.conf`; `kubectl apply -f web-headless.yaml -f supplier-externalname.yaml`; `nslookup web-headless.shop` vs `nslookup web.shop`; `nslookup supplier.shop`; `kubectl -n shop get svc`; NetworkPolicy: `kubectl apply -f np-kitchen-8080.yaml` (podSelector app=web, ingress จาก ns kitchen port **8080**) → `wget -T 3 http://web-alt.shop:8080` timed out → `kubectl delete -f np-kitchen-8080.yaml && kubectl apply -f np-kitchen-80.yaml` (port **80**) → ได้; เก็บกวาด `kubectl delete ns shop kitchen` | `web` → `wget: bad address 'web'`; `web.shop`/ชื่อเต็มได้หน้าเว็บ; headless คืน Pod IP 3 ตัว / web คืน ClusterIP 1 ตัว; ExternalName `canonical name = example.com`; policy port 8080 → `download timed out`, port 80 → ได้; ns ถูกลบ | ExternalName ต้องมีเน็ตออก (ไม่มี → ดูแค่บรรทัด canonical name / `get svc`); kindnet บังคับ policy หลัง DNAT ตามทฤษฎีจริง (8080 ถูกกั้น 80 ผ่าน); ไม่มี NetworkPolicy ค้างจากบท 004 |
| 10 | LAB สุดท้าย: แยก web กับ db ครั้งแรก | รวมทุกอย่าง: Service ClusterIP + NodePort, db กลาง, scale, self-healing, IP db เปลี่ยนแต่ชื่อเดิม, ข้อมูลหาย, เปลี่ยนรุ่นด้วยมือแล้วสะดุด | `som-shop-v2/` | ดูหัวข้อ 3 | ดูหัวข้อ 3 | ดูหัวข้อ 3.7 |

## 3. LAB สุดท้าย — "แยก web กับ db ครั้งแรก" (LAB10)

### 3.1 แนวคิดและเหตุผลการออกแบบ

- บท 002–005 ใส่ web + db ใน Pod เดียว (db = native sidecar คุยผ่าน localhost) → บท 005 scale เป็น 3 บูธแล้ว **ออเดอร์ไม่ตรงกัน** เพราะแต่ละบูธมี db ของตัวเอง
- บทนี้แยกเป็น **2 ReplicaSet + 2 Service** ใน ns `som-shop` (label `pod-security.kubernetes.io/warn: restricted` แบบบท 004):
  - `som-db`: **ReplicaSet** `replicas: 1`, postgres:17.11-alpine, PGDATA บน `emptyDir` (ข้อมูลหายเมื่อ Pod db เกิดใหม่ — ตั้งใจให้เห็น), readiness `pg_isready`; Service **ClusterIP** `som-db:5432` (ไม่เปิด NodePort ให้ db)
  - `som-web`: **ReplicaSet** `replicas: 3` (`som-shop-web:1.2`), init `wait-for-db` (`pg_isready -h som-db`) + `db-seed` (advisory lock), readiness `/api/health`, liveness `/api/live`; Service **NodePort 30080** → `http://localhost:30080`
- web เรียก db ด้วย **ชื่อ Service** (`DATABASE_URL=postgres://som:meow1234@som-db:5432/catshop`) → ลบ Pod db แล้ว IP เปลี่ยน แต่ web ยังต่อได้ (ClusterIP เดิม) = บทเรียนหลักของ Service
- **ไม่ใช้ Deployment/rollout**: เติมสินค้าใหม่หลัง db หาย = ลบ Pod web 1 ตัว (initContainer ของ Pod ใหม่รัน `db-seed` → ตารางกลับมาสำหรับทุกบูธเพราะ db กลางตัวเดียว); เปลี่ยนรุ่น 1.3 = `kubectl set image rs/...` ซึ่งไม่เปลี่ยน Pod เดิม → ลบ Pod เอง → เห็นปัญหาที่บท 007 แก้
- ไม่ใส่ `preStop` / strategy ใด ๆ (เป็นเรื่องบท 007) — error ตอนลบ Pod คือสิ่งที่ต้องการให้เห็น
- seed race (pre-check #23) แก้ด้วย `pg_advisory_xact_lock(5005)` + `ON CONFLICT DO NOTHING` → สอน "replica หลายตัวทำงานซ้ำพร้อมกันต้อง idempotent และกันชน"; กล่าวถึง Job ว่าเป็นทางเลือกในบทหลัง
- web แสดง **ชื่อ Pod + เวอร์ชัน** และมี `/api/whoami` สำหรับ `hit.sh` (browser ติด Pod เดียวเพราะ keep-alive)

### 3.2 สถาปัตยกรรม

```text
เครื่องนักศึกษา  http://localhost:30080
   │ (docker -p 30080 → k8s-lab → kind extraPortMappings → lab-control-plane:30080 → kube-proxy)
   ▼
Service som-web (NodePort 30080, port 80 → targetPort 3000)  ── EndpointSlice: Pod web ที่ ready
   ▼                     ▼                     ▼
Pod som-web-4nhz6     Pod som-web-ccxvw     Pod som-web-pn7qs     (ReplicaSet som-web, replicas 3 → 5 → 3)
   └────── DATABASE_URL=postgres://som:meow1234@som-db:5432/catshop (ชื่อ Service ไม่ใช่ IP) ──────┘
                                   ▼
                    Service som-db (ClusterIP 10.96.x.x, 5432)   ← ชื่อ/IP คงที่แม้ Pod db เกิดใหม่
                                   ▼
                    Pod som-db-xxxxx (ReplicaSet som-db, replicas 1, emptyDir — ข้อมูลหายเมื่อเกิดใหม่)
namespace som-shop (PSA warn: restricted)
```

### 3.3 การเปลี่ยนแอป (`som-shop-v2/app` คัดลอกจาก `004_kubernetes_namespace/02_LAB/som-shop-envs/app`)

**1.2** (build: `docker build --build-arg APP_VERSION=1.2 --build-arg APP_THEME=harbor -t som-shop-web:1.2 .`)
- Dockerfile (runner stage): `ARG APP_VERSION=dev`, `ARG APP_THEME=harbor` → `ENV APP_VERSION=$APP_VERSION APP_THEME=$APP_THEME` (แต่ละ tag "จำ" เวอร์ชันของตัวเอง ไม่ต้องตั้ง env ใน YAML — set image จึงเปลี่ยนป้ายจริง)
- `app/page.tsx`: ป้าย **"เวอร์ชัน 1.2"** ใน hero; แถบ "🐱 เสิร์ฟโดย Pod: `<ชื่อ Pod>`" ใต้ชื่อร้าน (ยังคงใน footer); `className` ตาม `APP_THEME`; ค่าเริ่มต้นใหม่ eyebrow `⚓ ท่าเรือ Kubernetes · ReplicaSet + Service`, footer `Next.js + PostgreSQL · Kubernetes LAB 006` (YAML ตั้ง `SHOP_FOOTER="Next.js + PostgreSQL · Kubernetes LAB 006 · namespace $(POD_NAMESPACE)"` ผ่าน env เดิมของ 1.1)
- query ฐานข้อมูลล้ม (db ใหม่ยังไม่มีตาราง/ต่อไม่ได้) → หน้า "ร้านกำลังเตรียมสินค้า กรุณารอสักครู่" + ชื่อ Pod/เวอร์ชัน และส่ง **HTTP 503** แทน 500 (pre-check #25: 1.1 ได้ 500)
- `app/api/whoami/route.ts` (ใหม่): text `som-web-4nhz6 1.2\n` (`os.hostname()` + `APP_VERSION`) ไม่แตะ db, `dynamic = 'force-dynamic'`
- `app/api/live/route.ts` (ใหม่): `{"ok":true}` ไม่แตะ db (liveness); `/api/health` เดิม (readiness, `SELECT 1`)
- `scripts/seed.mjs`: `BEGIN; SELECT pg_advisory_xact_lock(5005); CREATE TABLE IF NOT EXISTS ...; INSERT ... ON CONFLICT DO NOTHING; COMMIT;` (CREATE TABLE อยู่ใน lock ด้วย) + log `seeded 6 products (new: N)`; `lib/db.ts` คอมเมนต์ว่าเรียก db ผ่านชื่อ Service
- `globals.css`: ธีม `harbor` (teal/navy เดิม)

**1.3** (build: `docker build --build-arg APP_VERSION=1.3 --build-arg APP_THEME=sunset -t som-shop-web:1.3 .` — โค้ดเดียวกัน)
- ธีม `sunset` (hero ส้ม-ชมพู ตลาดนัดริมท่ายามเย็น) + ป้าย "เวอร์ชัน 1.3" + แบนเนอร์ "เมนูใหม่: ขนมปลาทูน่าอบกรอบ 🐟" (แสดงเมื่อ `APP_VERSION=1.3`) — **ไม่แก้ schema** (บท 007 ย้อนรุ่น 1.3 → 1.2 ได้ปลอดภัย)
- `som-shop-web:1.4` ไม่ build (บท 007 ใช้จำลอง tag ผิด)

### 3.4 ไฟล์ manifest

- `k8s/00-namespace.yaml`: Namespace `som-shop` labels `app.kubernetes.io/part-of: som-shop`, `pod-security.kubernetes.io/warn: restricted`
- `k8s/10-db.yaml`
  - **ReplicaSet** `som-db`: `replicas: 1`, selector/labels `app: som-db`, container postgres:17.11-alpine (env เดิม 004: `POSTGRES_USER=som`, `POSTGRES_PASSWORD=meow1234`, `POSTGRES_DB=catshop`, `PGDATA=/var/lib/postgresql/data/pgdata`), `ports: [{name: postgres, containerPort: 5432}]`, emptyDir `db-data`, securityContext restricted (uid/gid 70, fsGroup 70, seccomp RuntimeDefault, drop ALL), readinessProbe `pg_isready -U som -d catshop -h 127.0.0.1` period 3, livenessProbe tcp 5432, resources requests 100m/256Mi limits 500m/512Mi; คอมเมนต์ใหญ่ "emptyDir = ข้อมูลหายเมื่อ Pod นี้เกิดใหม่ (บทหลังใช้ PVC)" และ "replicas ต้องเป็น 1 — postgres 2 ตัวไม่แชร์ข้อมูลกัน"
  - Service `som-db`: ClusterIP, `port: 5432`, `targetPort: postgres`, selector `app: som-db`
- `k8s/20-web.yaml`
  - **ReplicaSet** `som-web`: `replicas: 3`, selector/labels `app: som-web`; Pod: `terminationGracePeriodSeconds: 30`, securityContext restricted แบบ 004; initContainers `wait-for-db` (postgres image, `until pg_isready -h som-db -p 5432 -U som -d catshop; do echo "รอฐานข้อมูล som-db..."; sleep 2; done`) และ `db-seed` (`som-shop-web:1.2`, `node scripts/seed.mjs`, `DATABASE_URL` เดียวกัน); container `web` image `som-shop-web:1.2` `imagePullPolicy: IfNotPresent`, `ports: [{name: http, containerPort: 3000}]`, env `POD_NAMESPACE` (Downward API), `SHOP_NAME`, `SHOP_FOOTER`, `DATABASE_URL=postgres://som:meow1234@som-db:5432/catshop`, `PORT=3000`, `HOSTNAME=0.0.0.0`; readinessProbe `/api/health` period 3 failure 2; livenessProbe `/api/live` initialDelay 10 period 10; resources requests 100m/192Mi limits 500m/512Mi
  - Service `som-web`: `type: NodePort`, `port: 80`, `targetPort: http`, `nodePort: 30080`, selector `app: som-web`
- `hit.sh` (bash + curl, รันใน k8s-lab): `./hit.sh [-q] [URL=http://localhost:30080/api/whoami] [N=60] [DELAY=0.1]` → `curl -s -m 2` ทีละครั้ง, ปกติพิมพ์ตาราง `จำนวน  Pod  เวอร์ชัน` (`sort | uniq -c`) + บรรทัด `ok=… err=…`; `-q` พิมพ์จุด `.`/`x` ระหว่างยิงและสรุป ok/err เท่านั้น (ใช้ระหว่างลบ Pod)

### 3.5 ขั้นตอน

1. **เตรียม**: `kubectl get svc -A | grep 30080` ต้องว่าง (ลบ `web-nodeport` ของ LAB8/examples); `cd som-shop-v2/app` → build 1.2 และ 1.3 (~30 วิ ครั้งที่สองเร็วเพราะ cache) → `kind load docker-image som-shop-web:1.2 som-shop-web:1.3 --name lab`; postgres: `docker save --platform linux/amd64 postgres:17.11-alpine -o ../pg.tar && kind load image-archive ../pg.tar --name lab && rm ../pg.tar` (หรือข้ามให้ Node pull เอง)
2. **db**: `kubectl apply -f k8s/00-namespace.yaml -f k8s/10-db.yaml` → `kubectl -n som-shop wait --for=condition=Ready pod -l app=som-db --timeout=120s` → `kubectl -n som-shop get rs,pods,svc,endpointslice -o wide` (som-db ClusterIP + 1 endpoint ชี้ Pod db)
3. **web**: `kubectl apply -f k8s/20-web.yaml` → `kubectl -n som-shop get pods -w` (เห็น `Init:0/2` → `Init:1/2` → `Running 1/1`) → `kubectl -n som-shop logs -l app=som-web -c db-seed --prefix` (ตัวหนึ่ง `new: 6` อีกสองตัว `new: 0`) → `kubectl -n som-shop get pods -o custom-columns=NAME:.metadata.name,INIT_RESTARTS:.status.initContainerStatuses[*].restartCount,NODE:.spec.nodeName` (restart 0 ทุกตัว, กระจาย 2 เรือ)
4. **ชื่อ Service จากภายใน**: `kubectl -n som-shop exec <pod web> -c web -- node -e "require('dns').lookup('som-db',(e,a)=>console.log(a))"` → ClusterIP ของ som-db (เทียบ `get svc som-db`); `... -- env | grep SOM_DB_SERVICE` (มีเพราะ web สร้างหลัง Service som-db)
5. **เปิดร้าน**: เครื่องนักศึกษา `http://localhost:30080` → ธีม harbor ป้าย "เวอร์ชัน 1.2" + "เสิร์ฟโดย Pod: som-web-…"; refresh หลายครั้ง (มักเห็น Pod เดิม — keep-alive) → ใน k8s-lab `./hit.sh` (60 ครั้ง) เห็นทั้ง 3 Pod `ok=60 err=0`
6. **ออเดอร์รวม db เดียว (แก้ปัญหาบท 005)**: สั่งซื้อ 2–3 ออเดอร์ทางหน้าเว็บ หรือ `curl -s -X POST localhost:30080/api/orders -H 'content-type: application/json' -d '{"product_id":1,"qty":2}'` 3 ครั้ง → `kubectl -n som-shop exec <pod db> -- psql -U som -d catshop -c 'select count(*) from orders'` = 3; เปิดหน้าเว็บจาก Pod ต่าง ๆ (`curl -s localhost:30080 | grep -o 'เสิร์ฟโดย Pod[^<]*'` + ตัวนับออเดอร์ในหน้า) ตัวเลขเท่ากันทุก Pod
7. **scale**: `kubectl -n som-shop scale rs/som-web --replicas=5` → `get pods`, `get endpointslice -l kubernetes.io/service-name=som-web` (5 IP) → `./hit.sh` เห็น 5 Pod
8. **self-healing ใต้ Service**: terminal 1 `./hit.sh -q http://localhost:30080/api/whoami 100`; terminal 2 `kubectl -n som-shop delete pod <web ตัวหนึ่ง>` → RS สร้างแทน (ผ่าน init ใหม่), hit.sh ok เกือบทั้งหมด (err 0–2 ถ้าลบตอนกำลังตอบ — บันทึกจริง) → `kubectl -n som-shop scale rs/som-web --replicas=3`
9. **ลบ Pod db**: `kubectl -n som-shop get pod -l app=som-db -o wide` (จด IP) → `kubectl -n som-shop delete pod -l app=som-db` → RS สร้างใหม่ (~5 วิ) IP ใหม่ → `get svc som-db` ClusterIP **เดิม**, `get endpointslice -l kubernetes.io/service-name=som-db` IP ใหม่ → web ไม่ต้อง restart ก็ต่อได้ (`/api/health` ok) แต่หน้าเว็บ **503 "ร้านกำลังเตรียมสินค้า"** (`curl -s -o /dev/null -w '%{http_code}\n' localhost:30080`) → `psql ... 'select count(*) from orders'` → `relation "orders" does not exist`
10. **เติมสินค้าใหม่**: `kubectl -n som-shop delete pod <web ตัวหนึ่ง>` (แค่ตัวเดียว) → Pod ใหม่รัน `db-seed` (`new: 6`) → **ทุกบูธ** กลับมาขายได้ (db กลาง) แต่ **ออเดอร์ = 0** → อภิปราย: emptyDir + Pod db เกิดใหม่ = ข้อมูลหาย → PVC บทหลัง
11. **อยากอัปเดตเป็น 1.3**: `kubectl -n som-shop set image rs/som-web web=som-shop-web:1.3 db-seed=som-shop-web:1.3` → `kubectl -n som-shop get rs som-web -o jsonpath='{.spec.template.spec.containers[0].image}'` (1.3) แต่ `get pods -o custom-columns=NAME:.metadata.name,IMAGE:.spec.containers[0].image` ยัง 1.2 ทุกตัว + `./hit.sh` ยัง 1.2 (ทบทวนบท 005)
12. **ลบ Pod เองทีละตัว**: terminal 1 `./hit.sh http://localhost:30080/api/whoami 200`; terminal 2 ลบ Pod 1 ตัวแล้วรอ ready (`kubectl -n som-shop delete pod <ชื่อ> && kubectl -n som-shop wait --for=condition=Ready pod -l app=som-web --timeout=90s`) → ผล hit.sh เห็น 1.2 กับ 1.3 ปน (ลูกค้าแต่ละคนเห็นร้านคนละธีม) และอาจมี err เล็กน้อย; ถ้าทำต่อทีละตัวต้องพิมพ์ชื่อ Pod เอง รอเอง — น่าเบื่อและเสี่ยงลบผิด
13. **ลบที่เหลือทีเดียว (ทางลัดที่ผิด)**: terminal 1 `./hit.sh -q http://localhost:30080/api/whoami 200`; terminal 2 `kubectl -n som-shop delete pod -l app=som-web` → Pod ใหม่ทั้งหมดอยู่ใน `Init` → EndpointSlice ไม่มี endpoint ที่ ready → hit.sh err ต่อเนื่องหลายวินาที (คาด `Connection refused`) จนกว่า Pod ใหม่ ready → ได้ 1.3 ครบแต่ **ร้านสะดุด**
14. **ปิดบท**: ตารางเทียบ "ที่ Service แก้ได้" (ชื่อคงที่, db กลาง, กระจายโหลด, เปิดสู่ภายนอก) vs "ที่ยังไม่ได้" (เปลี่ยนรุ่นทีละบูธอัตโนมัติ, รอไฟเขียวก่อนรื้อบูธถัดไป, ประวัติ/ย้อนรุ่น → **บท 007 Deployment**; ข้อมูล db → PVC)
15. **เก็บกวาด**: `kubectl delete ns som-shop` (30080 ว่างอีกครั้ง; image 1.2/1.3 ยังอยู่ใน Node ให้บท 007 ใช้ต่อ)

### 3.6 ผลที่ต้องเห็น

- `get rs -n som-shop`: `som-db 1 1 1`, `som-web 3 3 3` (ภายหลัง 5); `get svc`: `som-db ClusterIP 10.96.x.x 5432/TCP`, `som-web NodePort 10.96.x.x 80:30080/TCP`
- log db-seed: ตัวหนึ่ง `seeded 6 products (new: 6)` ที่เหลือ `(new: 0)` และ init restartCount 0
- browser `localhost:30080`: ป้ายเวอร์ชัน + ชื่อ Pod; `hit.sh` 60 ครั้งกระจายทุก Pod `ok=60 err=0`
- ออเดอร์เท่ากันทุก Pod (db กลาง); scale 5 → EndpointSlice 5 IP
- ลบ Pod db: IP endpoint เปลี่ยน, ClusterIP เดิม, หน้า 503, `relation "orders" does not exist` → ลบ Pod web 1 ตัว → ร้านกลับมา ออเดอร์ 0
- set image rs → Pod เดิมยัง 1.2; ลบทีละตัวเห็น 1.2/1.3 ปน; ลบทีเดียว → err หลายครั้ง

### 3.7 จุดที่ต้องยืนยันตอนทดสอบจริง

1. **NodePort 30080 จาก host ของนักศึกษา** (Windows + Docker Desktop: `http://localhost:30080`) — pre-check #19 ยืนยันแค่กลไกด้วย host port 30090/30091; ถ้าไม่ได้ ทางสำรอง `ssh -p 2223 -L 30080:localhost:30080 root@localhost`
2. **browser keep-alive**: Chrome/Edge จริงติด Pod เดียวไหม (pre-check #20 Chromium 10/10), Ctrl+F5/Incognito เปลี่ยน Pod ไหม
3. **seed + advisory lock**: init restartCount 0 ทุกตัว, log `new: 6` หนึ่งตัว `new: 0` สองตัว (pre-check #23 ไม่มี lock ชน 2/3)
4. **หน้า 503** "ร้านกำลังเตรียมสินค้า" หลังลบ db และ readiness ยังผ่าน (`/api/health` = `SELECT 1`) — ไม่ตรวจตาราง (ถ้าตรวจ web ทั้งหมดจะ not ready → NodePort refused ทั้งร้าน)
5. **web ต่อ db ใหม่เองโดยไม่ restart** (pool ของ `pg` ต่อใหม่ — pre-check #25 `/api/health` ok) และเวลาที่ Pod db ใหม่ ready (pre-check 4.2 วิ)
6. **เติมสินค้าด้วยการลบ Pod web 1 ตัว** ทำให้ทั้งร้านกลับมา (Pod อื่นไม่ต้อง restart) และหน้าเว็บของ Pod อื่นหาย 503 ทันที
7. **hit.sh กระจาย** 60 ครั้งเห็นครบ 3 Pod (และ 5 Pod หลัง scale)
8. **จำนวน err ตอนลบ Pod web ทีละตัว** (ไม่มี preStop — คาด 0–3) และ **ตอนลบทีเดียว** (คาด err ต่อเนื่องเท่ากับเวลา init ~10–20 วิ × 10 ครั้ง/วิ) — บันทึกตัวเลขจริงเพื่อใช้เปิดบท 007; ข้อความ curl ระหว่าง endpoints ว่าง (คาด `Connection refused` ตาม pre-check #13)
9. `kubectl set image rs/som-web web=... db-seed=...` ใช้กับ initContainer ได้ (ชื่อ container ใน initContainers) และเปลี่ยนแค่ template
10. resource 5 web + 1 db (requests ~600m/1.2Gi) ไม่ Pending; PSA warn ไม่มีคำเตือน
11. Pod Next.js ที่ถูกลบแสดง `Error` ชั่วครู่ (pre-check #22) — อธิบายใน README
12. ชื่อ env `SOM_DB_SERVICE_HOST` ใน Pod web

### 3.8 screenshot ที่จะเก็บตอนทดสอบจริง (ไม่ใช่ภาพ imagegen)

- browser `localhost:30080` เวอร์ชัน 1.2 (เห็นชื่อ Pod), หน้า "ร้านกำลังเตรียมสินค้า" (503), เวอร์ชัน 1.3 หลังลบ Pod เอง; browser LAB8 `web v1 from web-...`
- terminal: `get rs,pods,svc,endpointslice -n som-shop`, `hit.sh` (กระจาย + ok/err), EndpointSlice ของ som-db ก่อน/หลังลบ Pod db, hit.sh ตอนลบทีเดียว

## 4. งานถัดไป (หลังอนุมัติแผน)

1. ผู้ประสานงานสร้างภาพจาก `images.json` (gen_images.sh) → ตรวจภาพ (ป้ายสะกด/จำนวนป้าย, น้องส้มตรง reference, หุ่นยนต์ไม่เป็นแมว, ไม่มีคนไม่มีหัว, ไม่มีผู้จัดการร้านนอก T36/L24) → ภาพ `needs_test` สร้าง/ปรับหลังทดสอบ LAB จริง
2. เขียนไฟล์ LAB (`labs/`, `som-shop-v2/` รวมโค้ด 1.2/1.3 + hit.sh) + README ทฤษฎี/LAB + README หน้ารวม (ลิงก์บท 005 ↔ 006 ↔ 007)
3. รัน LAB0–10 ใน container ชั่วคราว (skill k8s-lab) บันทึก `logs/006_service/lab-run/SUMMARY.md` แล้วแก้ README/ภาพด้วยผลจริง; ส่งต่อ image 1.2/1.3 + ตัวเลข err ตอนลบ Pod ให้บท 007
4. ประสานกับบท 005: ตัวอย่างเลข orders/ชื่อบูธใน T03 ให้ตรงกับภาพปิดบท 005; กับบท 007: `k8s-rs/` ของบท 007 คัดลอก `som-shop-v2/k8s/` ของบทนี้

## 5. สรุป storyboard

- **Theory 36 ภาพ (T01–T36)**: บทนำ T01–T03, ทำไมต้องมี Service T04–T06, EndpointSlice T07–T09, Service CIDR T10, พอร์ต T11–T12, NodePort T13–T15, LoadBalancer T16, ExternalName/headless T17–T18, DNS T19–T21, kube-proxy T22–T23, การกระจายโหลด T24–T26, readiness ↔ endpoints T27–T28, debug T29–T31, NetworkPolicy T32, ข้อจำกัด T33, สรุป T34–T36 (T35 "สรุปบทที่ 6", T36 ปูทาง "บทที่ 7" allow)
- **LAB 24 ภาพ (L01–L24)**: LAB0 L01, LAB1 L02, LAB2 L03–L04, LAB3 L05, LAB4 L06, LAB5 L07, LAB6 L08, LAB7 L09, LAB8 L10–L11, LAB9 L12–L14, LAB10 L15–L24 (10 ภาพ: สถาปัตยกรรม, build/load, db+Service, เติมสินค้ากันชน, เปิดร้าน 30080, hit.sh + ออเดอร์รวม, scale + self-healing, ลบ db ข้อมูลหาย, set image แล้วลบ Pod เองจนสะดุด, สรุป + เงาผู้จัดการร้าน allow)
- ภาพเปิดบท T01 ป้าย "บทที่ 6"; ภาพที่ `allow=True` (เห็นผู้จัดการร้าน/คำว่า Deployment): **T36, L24** เท่านั้น
- ที่มาของภาพ: `README-split.md` (ใช้ prompt เดิม 12, แก้ 22, ใหม่ 26)
- **`needs_test: true` (12 ภาพ)**: **T15** ข้อความ `provided port is already allocated` (ยังไม่ได้รันจริง), **T31** targetPort ผิดได้ `Connection refused`, **L05** ข้อความ error multi-port ไม่มีชื่อ, **L10** NodePort จาก browser จริง, **L11** keep-alive Chrome/Edge + LB pending, **L13** headless/ExternalName (ต้องมีเน็ต), **L14** NetworkPolicy port 8080 vs 80 บน kindnet, **L18** seed advisory lock `new: 6/0/0`, **L19** หน้าร้าน 1.2 + ชื่อ Pod, **L20** hit.sh กระจาย `ok=60 err=0` + `orders: 3`, **L22** ลบ db (IP ใหม่, 503, `orders: 3 → 0`), **L23** set image rs + ลบ Pod เอง (1.2/1.3 ปน, err)
- ภาพที่ใช้ค่าจาก pre-check แล้ว (ไม่ติด needs_test แต่ตรวจป้ายหลังรัน): T04/T07/T22 (IP ตัวอย่าง `10.96.47.123`, `10.244.x.x`), T09/L03 (คำเตือน Endpoints), T10/L01 (`10.96.0.1`, `10.96.0.10`, `mode: iptables`), T16 (`80:30456/TCP`), T18 (headless 3 IP), T20 (resolv.conf), T24 (5/4/0), T25 (10/10), T27 (`ready=false`), T30 (`ENDPOINTS <unset>`, `Connection refused`)
- กฎภาพ: ป้าย ≤ 7 ต่อภาพ ระบุตำแหน่งทุกป้าย (ป้ายซ้ำระบุว่าซ้ำ), ป้าย/แถวที่วาดต้องมีข้อความ (ยกเว้นป้ายห้อยสี/กันสาด/แถวไอคอนที่ระบุชัด), ของในภาพเป็นร้านอาหารแมว/ท่าเรือ, headless ≠ คนไม่มีหัว, seed ≠ เมล็ดพืช (เติมสินค้าเข้าชั้น), หุ่นยนต์ไม่เป็นแมว, คนเป็น silhouette
