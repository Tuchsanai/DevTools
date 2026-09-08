# แกนเนื้อหาของแล็บทั้ง 21 ตัว (yolo1 ออกแบบ · ผู้ทำแล็บทุกคนต้องยึดตามนี้)

อ่านคู่กับ spec ส่วนที่ 2 · 2.5 · 3 · 4 และ `.work/app-requirements.md` (แอปตัวอย่าง)

## กติการ่วมของทุกแล็บ

1. **หนึ่งแล็บ = หนึ่งแนวคิด** ประโยค "แนวคิดหลัก" ด้านล่างต้องปรากฏใน README บล็อก `> 💡 **แนวคิดหลักของแล็บนี้:**` คำต่อคำ
2. **namespace** ของแล็บ = `labNNN` (เช่น `lab003`) สร้างด้วย `kubectl create namespace labNNN` ตอนต้น ลบทิ้งตอน Cleanup
   ยกเว้นแล็บ 001/002 ที่ดู object ที่มีอยู่แล้ว (002 สร้าง `lab002` เพื่อทดลอง)
3. **แอปตัวอย่าง** = SkillSpace (ระบบแจ้งซ่อม/ยืม-คืนครุภัณฑ์) ที่นักศึกษาเคยเห็นบน Docker Compose
   image: `k8s-lab-web:v1` · `k8s-lab-web:v2` · `k8s-lab-api:v1` · `k8s-lab-db:v1` (build ครั้งเดียวจาก `05_kubernetes/app/` แล้ว `kind load`)
   ทุก manifest ที่ใช้ image เหล่านี้ต้องมี `imagePullPolicy: IfNotPresent`
4. **สองทางเปิดเว็บ (ใช้แค่สองทางนี้ทั้งชุด)**
   - `kubectl port-forward ... 3000:3000 --address 0.0.0.0` → `http://localhost:3000` — ใช้เมื่อต้องการ "แอบดู Pod ตัวเดียว" (แล็บ 003-005, 009)
   - "ประตู" = Service `web` (ClusterIP :3000) + Ingress path `/` → เบราว์เซอร์ `http://localhost:8080` · **ในเทอร์มินัลของเครื่องเรียน (container) ใช้ `curl http://localhost/info` (port 80)** เพราะ 8080 มีเฉพาะฝั่งเครื่องหลัก — ใช้ตั้งแต่แล็บ 006 เป็นต้นไป
     เพราะ port-forward ปักอยู่ที่ Pod เดียว มองไม่เห็นการกระจายโหลด/self-healing/readiness
     ในครั้งที่ 1 ให้ไฟล์ `door.yaml` เป็น "ประตูสำเร็จรูป — จะอธิบายในแล็บ 008-009 (Service) และ 017 (Ingress)"
     Ingress ในชุดนี้ **ไม่ใส่ host** (path-only) เพื่อให้เปิด localhost:8080 ได้ตรง ๆ
5. **หลักฐาน 3 มุม** ทุกแล็บ: ผล kubectl · หน้าเว็บ (การ์ดสถานะของแอปแสดงชื่อ Pod ที่ตอบ) · `kubectl logs` / `kubectl get events`
6. **การ์ดสถานะบนหน้าเว็บ** (แอปทำไว้ให้แล้ว) แสดง web Pod ที่ตอบ + เวอร์ชัน + เวลา · สถานะ api (ชื่อ Pod api) · สถานะ db
   และ endpoint `/info` (JSON) สำหรับ `curl` ในลูป — ใช้เป็นหลักฐานหลักของแล็บ 006, 008, 014, 018, 021
7. ค่าที่ต่างกันได้ทุกครั้งที่รัน (ชื่อ Pod ต่อท้าย hash, IP, AGE, เวลา, ชื่อ node ที่ Pod ตกไปอยู่, ตัวเลข CPU/RAM ของเครื่อง) → README ต้องกำกับว่า "ค่าเหล่านี้ต่างกันได้"
8. ไดอะแกรมสถาปัตยกรรมประจำแล็บ = `../slides_assets/labNNN-architecture.svg` (ครั้งละ 7 ไฟล์ · ทีมไดอะแกรมทำตามรายการท้ายเอกสารนี้)
9. เครื่องเรียน = container `devtools-k8s` จาก image `tuchsanai/devtools-k8s:2569_1` · cluster จาก `k8s-bootstrap` (kind `devtools` : 1 control-plane + 2 worker + metrics-server + ingress-nginx) · เวอร์ชัน: Kubernetes v1.36.4 · kubectl v1.37.0 · kind v0.33.0
   คำสั่งเปิดเครื่องเรียนที่ต้องใช้ตรงกันทุกเอกสาร:
   `docker run -d --name devtools-k8s --privileged --shm-size=1g --ulimit nofile=65536:65536 -p 2299:22 -p 8080:80 -p 8443:443 -p 3000:3000 -p 9090:9090 tuchsanai/devtools-k8s:2569_1`
10. โค้ดแล็บอยู่ที่ `~/labwork/DevTools/05_kubernetes/<ครั้ง>/<แล็บ>` หลัง `git clone https://github.com/Tuchsanai/DevTools.git` ใน `~/labwork`

---

# ครั้งที่ 1 — `01_Session1_Kubernetes_Basics` : Kubernetes คืออะไร และมันดูแลแอปให้เราอย่างไร
ธีม: Kubernetes คือระบบที่ "คอยทำให้สภาพจริงตรงกับสภาพที่เราสั่งไว้" · ใช้เฉพาะ **web** ตัวเดียวตลอดครั้งนี้

## 001-kubernetes-introduction
- **แนวคิดหลัก:** Kubernetes คือผู้ดูแลที่คอยรันแอปให้ตรงกับที่เราสั่งไว้เสมอ แม้เครื่องจะพังหรือแอปจะตาย
- **ปัญหาตั้งต้น:** ระบบ SkillSpace บน Docker Compose รันได้บนเครื่องเดียว — ถ้าเครื่องนั้นดับ ถ้าต้องรัน web 10 ตัวบน 3 เครื่อง ถ้า container ตายตอนตีสาม ใครจะเป็นคนสั่ง `docker compose up` ใหม่?
- **ขั้นตอน:**
  1. เปิดเครื่องเรียน + `k8s-bootstrap` (ครั้งแรกของชุด อธิบายว่าได้อะไรมาบ้าง)
  2. `kubectl cluster-info` · `kubectl version` — control plane อยู่ไหน เวอร์ชันอะไร
  3. `kubectl get nodes -o wide` → 3 เครื่อง (1 control-plane + 2 worker) และ `docker ps` ในเครื่องเรียน → เห็นว่าในห้องเรียน "node = container ของ kind"
  4. `kubectl get pods -A` → มีอะไรรันอยู่แล้วบ้าง (kube-system, ingress-nginx, metrics-server) — ผู้ดูแลก็ต้องมีลูกน้อง
  5. `kubectl describe node devtools-worker | head` — เครื่องหนึ่งบอกอะไร (CPU/RAM/Conditions)
  6. build image แอปตัวอย่าง (`app/build-images.sh`) + `kind load docker-image ... --name devtools` + `docker exec devtools-control-plane crictl images | grep k8s-lab` — เตรียมของสำหรับทั้งชุด และปูเรื่อง "image ต้องอยู่บน node" (ImagePullBackOff ในแล็บ 003/020)
  7. `k9s` เปิดดู 1 นาที (แนะนำเป็น "หน้าจอหลักฐาน" ของทั้งชุด · ไม่ต้อง screenshot)
- **ทดลองให้พัง:** `docker stop devtools-worker2` ในเครื่องเรียน → `kubectl get nodes -w` เห็น `NotReady` ภายในราว 40-60 วินาที → `kubectl describe node devtools-worker2` (Conditions: Ready=Unknown) → `docker start devtools-worker2` → กลับเป็น Ready · ชี้ให้เห็นว่า control plane "รู้" ว่าเครื่องหาย และนี่คือจุดที่ Compose ไม่มีให้
- **คำถาม + แนวคำตอบ:**
  1. Docker Compose ทำอะไรไม่ได้บ้างที่ Kubernetes ทำได้? → Compose ทำงานบนเครื่องเดียว ไม่รู้จักเครื่องอื่น ไม่ย้ายงานเมื่อเครื่องดับ ไม่มีตัวเฝ้าสภาพที่ต้องการตลอดเวลา · K8s มี control plane เฝ้าหลาย node และแก้ส่วนต่างให้เอง
  2. control plane กับ worker node ต่างกันอย่างไร? → control plane = สมอง (API server, scheduler, controller, etcd) ตัดสินใจและจำสภาพที่ต้องการ · worker = แรงงาน (kubelet + container runtime) รัน Pod ตามคำสั่ง
  3. ทำไมต้อง `kind load` image? → node ของ cluster เป็นคนดึง image เอง ไม่ใช่เครื่องที่เรา build · image ที่ build ไว้บน dockerd นอก cluster node มองไม่เห็น
- **ชิ้นส่วนแอป:** ยังไม่รัน แค่ build + load image ทั้ง 4
- **ไฟล์:** ไม่มี manifest (ใช้สคริปต์ build ของ app/) · screenshot: ไม่บังคับ (ไม่มี UI)

## 002-kubectl-and-namespace
- **แนวคิดหลัก:** ทุกอย่างใน Kubernetes คือ "object" ที่เราสั่งผ่าน kubectl และถูกจัดกลุ่มด้วย namespace
- **ปัญหาตั้งต้น:** `kubectl get pods` แล้วว่างเปล่า ทั้งที่แล็บ 001 เห็นชัดว่ามี Pod รันอยู่เป็นสิบ — มันหายไปไหน?
- **ขั้นตอน:**
  1. `kubectl get pods` (ว่าง) เทียบ `kubectl get pods -A` (เต็ม) → namespace คือ "ห้อง"; `kubectl get namespaces`
  2. `kubectl get pods -n kube-system` · `-o wide` → คอลัมน์ NODE/IP; อ่านความหมายทีละคอลัมน์
  3. `kubectl api-resources | head -30` → "ทุกอย่างคือ object": Pod, Service, Deployment, Node, Namespace มี KIND/SHORTNAMES/NAMESPACED
  4. `kubectl describe pod -n ingress-nginx <pod>` และ `kubectl get pod ... -o yaml | head -40` → object ทุกตัวมี apiVersion/kind/metadata/spec/status (ปูแล็บ 004)
  5. `kubectl create namespace lab002` · `kubectl get ns lab002 -o yaml` → แม้ namespace ก็เป็น object
  6. `kubectl explain pod.spec.containers | head` — คู่มือในตัว ไม่ต้องจำ field
  7. alias ของเครื่องเรียน `k`, `kgp`, `kgn` และ `kubectl get pods -A --field-selector status.phase=Running | wc -l`
- **ทดลองให้พัง:** `kubectl config set-context --current --namespace=lab002` แล้วสั่ง `kubectl get pods -n kube-system` (เจอ) เทียบ `kubectl get pods` (No resources found in lab002 namespace) → นักศึกษาต้องอ่านข้อความ error ให้ออกว่า "มันบอก namespace มาด้วย" → แก้กลับ `--namespace=default` และ `kubectl config view --minify | grep namespace`
- **คำถาม + แนวคำตอบ:**
  1. namespace มีไว้ทำไม? → แยกกลุ่ม object ให้ไม่ชนชื่อกัน จัดสิทธิ์/โควตาแยกกันได้ และลบทิ้งทั้งห้องได้ในคำสั่งเดียว (นี่คือเหตุผลที่ทุกแล็บใช้ namespace ของตัวเอง)
  2. ทำไมบางทีหา resource ไม่เจอ? → มองผิด namespace (ค่า default ของ context) หรือ resource นั้นเป็น cluster-scoped (Node, Namespace, PV) ไม่มี namespace เลย
  3. `-o wide` กับ `-o yaml` ต่างกันอย่างไร? → wide = ตารางเพิ่มคอลัมน์ที่คนอ่าน · yaml = object เต็มตัวตามที่ API server เก็บจริง รวม status
- **ชิ้นส่วนแอป:** ไม่ใช้ (ดู object ที่มีอยู่แล้ว) · **ไฟล์:** ไม่มี manifest · screenshot: ไม่บังคับ

## 003-pod-the-smallest-unit
- **แนวคิดหลัก:** หน่วยเล็กที่สุดที่ Kubernetes ดูแลคือ Pod ไม่ใช่ container
- **ปัญหาตั้งต้น:** อยากได้หน้าเว็บ SkillSpace ขึ้นบน cluster สักตัวเดียวก่อน — บน Docker เราสั่ง `docker run` แล้วบน Kubernetes สั่งอะไร และทำไมมันไม่เรียกว่า container?
- **ขั้นตอน:**
  1. `kubectl create ns lab003` · `kubectl run web --image=k8s-lab-web:v1 --port=3000 -n lab003` (imperative — ยังไม่เขียน YAML)
  2. `kubectl get pods -n lab003 -w` (ContainerCreating → Running) · `-o wide` (อยู่ node ไหน IP อะไร)
  3. `kubectl describe pod web` อ่าน Events (Scheduled → Pulled → Created → Started) · `kubectl logs web` (Next.js ready)
  4. `kubectl exec web -- hostname` (= ชื่อ Pod) · `kubectl exec -it web -- sh` แล้ว `ps`, `env | grep HOSTNAME`, `wget -qO- localhost:3000/info`
  5. `kubectl port-forward pod/web 3000:3000 --address 0.0.0.0 &` → เปิด `http://localhost:3000` → **screenshot** หน้าเว็บครั้งแรกบน Kubernetes: การ์ดสถานะแสดง "web Pod: web · v1" และ api/db = ยังไม่เชื่อมต่อ (โหมดเดี่ยว)
  6. Pod ที่มี 2 container: `apply -f 02-pod-with-sidecar.yaml` (web + sidecar busybox ที่วน `wget -qO- http://localhost:3000/healthz` ทุก 10 วินาที) → `kubectl logs web2 -c sidecar` เห็นผล ok → พิสูจน์ว่า container ใน Pod เดียวกัน **แชร์ network** (localhost เดียวกัน) — นี่คือเหตุผลที่หน่วยเล็กสุดคือ Pod · `kubectl get pod web2 -o jsonpath='{.spec.containers[*].name}'`
  7. `kubectl delete pod web` → `kubectl get pods` → หายไปเลย ไม่มีใครสร้างใหม่ (**จำภาพนี้ไว้เทียบกับแล็บ 006**)
- **ทดลองให้พัง:** `kubectl run web-broken --image=k8s-lab-web:v9` → `ErrImagePull` → `ImagePullBackOff` · `describe` Events บอก "not found" → อธิบายว่า node ต้องหา image ให้เจอ (tag ผิด/ยังไม่ load) → `kubectl delete pod web-broken`
- **คำถาม + แนวคำตอบ:**
  1. Pod ต่างจาก container อย่างไร? → Pod = ซอง 1 ใบที่มี container ≥1 ตัว แชร์ IP/network/volume/วงจรชีวิตเดียวกัน · container คือ process ในซองนั้น
  2. ทำไมถึงออกแบบให้หน่วยเล็กสุดเป็น Pod? → งานจริงมักต้องมีตัวช่วยเกาะติดแอป (log shipper, proxy, sidecar) ที่ต้องอยู่เครื่องเดียวกัน IP เดียวกัน → จัดกลุ่มเป็น Pod แล้ว scheduler ย้ายทั้งซองทีเดียว
  3. ลบ Pod แล้วทำไมไม่มีตัวใหม่? → เราสร้าง Pod "เปล่า ๆ" ไม่มีใครถือ "จำนวนที่ต้องการ" ไว้ — ต้องรอแล็บ 006
- **ชิ้นส่วนแอป:** web (v1) เดี่ยว · **ไฟล์:** `02-pod-with-sidecar.yaml` (ให้มาสำเร็จ อ่านทีหลังในแล็บ 004) · **screenshot:** `03-first-page-on-kubernetes.png`

## 004-declarative-yaml
- **แนวคิดหลัก:** เราไม่ได้สั่งว่า "ทำอะไร" แต่บอกว่า "อยากได้สภาพแบบไหน" แล้ว Kubernetes จัดการให้เอง (declarative)
- **ปัญหาตั้งต้น:** `kubectl run` พิมพ์ยาวขึ้นเรื่อย ๆ และเพื่อนทำซ้ำไม่ได้เหมือนเรา — บน Compose เราเคยแก้ปัญหานี้ด้วยไฟล์ compose.yaml แล้วบน Kubernetes ล่ะ?
- **ขั้นตอน:**
  1. `kubectl run web --image=k8s-lab-web:v1 --port=3000 --dry-run=client -o yaml` → kubectl แปลงคำสั่งเป็น YAML ให้ดู (สะพาน imperative → declarative) แล้วตัดเหลือ `01-pod.yaml` สั้น ๆ (apiVersion/kind/metadata{name,labels}/spec.containers{name,image,ports,imagePullPolicy})
  2. อธิบาย 4 ส่วนของทุก object ทีละ field · `kubectl apply -f 01-pod.yaml` → `created`
  3. `kubectl apply -f 01-pod.yaml` ซ้ำ → `unchanged` (idempotent — สั่งกี่ครั้งผลเท่าเดิม ต่างจาก `kubectl run` ที่สั่งซ้ำแล้ว error)
  4. `kubectl get pod web -o yaml` → K8s เติมอะไรให้เอง (defaults, status, uid) — ไฟล์เราคือ "ที่อยากได้" ส่วนนี่คือ "ที่เป็นจริง"
  5. แก้ไฟล์ image `:v1` → `:v2` (`02-pod-v2.yaml` หรือ sed) · `kubectl diff -f` ดูก่อน · `apply` → `configured` · port-forward → **screenshot** หน้าเว็บกลายเป็นธีม v2 (สีเขียว ป้าย v2)
  6. ลองแก้ field อื่น เช่น เพิ่ม `env` แล้ว apply → error `Pod "web" is invalid ... may not change fields other than image...` → Pod ส่วนใหญ่ **immutable** ต้องลบแล้วสร้างใหม่ (`kubectl replace --force -f`) → ปูว่าทำไมต้องมี Deployment (แล็บ 007)
  7. `kubectl explain pod.spec.containers.imagePullPolicy` — ใช้คู่มือแทนการเดา
- **ทดลองให้พัง:** ไฟล์ `03-pod-typo.yaml` ที่ย่อหน้าผิด (`containers` อยู่ผิดระดับ) และอีกแบบ `kind: Pods` → อ่าน error 2 แบบให้ออก (`unknown field` / `no matches for kind`) → ใช้ `kubectl apply --dry-run=server -f` ตรวจก่อนจริง → แก้แล้ว apply ผ่าน
- **คำถาม + แนวคำตอบ:**
  1. imperative ต่างจาก declarative อย่างไร? → imperative = สั่งขั้นตอน (run/delete) ต้องรู้สภาพปัจจุบันก่อนสั่ง · declarative = ประกาศปลายทาง ระบบหาทางเอง ทำซ้ำได้ เก็บใน git ได้
  2. apiVersion/kind/metadata/spec แต่ละส่วนบอกอะไร? → กลุ่ม+เวอร์ชันของ API · ชนิด object · ชื่อ/label/namespace ที่ใช้อ้าง · เนื้อหาที่อยากได้ (status คือส่วนที่ระบบเขียนคืน)
  3. ทำไมแก้ image ได้แต่แก้ env ไม่ได้? → Pod ถูกออกแบบให้เป็นหน่วยที่ "ทิ้งแล้วสร้างใหม่" ไม่ใช่แก้ทีละนิด · ตัวที่ดูแลการเปลี่ยนแปลงคือชั้นที่อยู่เหนือ Pod
- **ชิ้นส่วนแอป:** web v1 → v2 · **ไฟล์:** `01-pod.yaml`, `02-pod-v2.yaml`, `03-pod-typo.yaml` · **screenshot:** `05-pod-v2-after-apply.png`

## 005-labels-the-glue
- **แนวคิดหลัก:** label คือกาวที่ทำให้ object ต่าง ๆ รู้จักกัน โดยไม่ต้องรู้จักชื่อหรือ IP ของกันและกัน
- **ปัญหาตั้งต้น:** มี web 3 ตัว (v1 สองตัว v2 หนึ่งตัว) ถ้ามี 300 ตัว จะบอก Kubernetes ว่า "เอาเฉพาะตัวที่เป็น v2" อย่างไร โดยไม่ต้องไล่ชื่อ?
- **ขั้นตอน:**
  1. `01-pods-with-labels.yaml` (3 Pod ในไฟล์เดียวคั่น `---`): web-a{app=web,version=v1,tier=frontend} · web-b{app=web,version=v2,tier=frontend} · web-c{app=web,version=v1}
  2. `kubectl get pods --show-labels` · `-L app,version` (label เป็นคอลัมน์)
  3. เลือกด้วย selector: `-l version=v1` · `-l app=web,version=v2` · `-l 'version in (v1,v2)'` · `-l '!tier'`
  4. `kubectl label pod web-c version=v2 --overwrite` → `-l version=v2` ได้ 2 ตัว (label เปลี่ยน = สมาชิกกลุ่มเปลี่ยนทันที)
  5. ทำงานเป็นกลุ่ม: `kubectl delete pods -l version=v2` → เหลือ web-a ตัวเดียว
  6. ผู้ใช้ label ตัวจริงใน cluster: `kubectl get nodes --show-labels` เห็น `ingress-ready=true` ที่ control-plane และ `kubectl -n ingress-nginx get deploy ingress-nginx-controller -o jsonpath='{.spec.template.spec.nodeSelector}'` → ingress-nginx "เลือก node" ด้วย label ไม่ใช่ชื่อ
  7. (เชื่อมไปแล็บ 006) selector ของ ReplicaSet/Service ก็คือ label เดียวกันนี้ — ปูภาพ
- **ทดลองให้พัง:** ลอก label ที่คนอื่นพึ่งพา: `kubectl label node devtools-control-plane ingress-ready-` แล้ว `kubectl -n ingress-nginx delete pod -l app.kubernetes.io/component=controller` → Pod ใหม่ค้าง `Pending` · `describe` → "node(s) didn't match Pod's node affinity/selector" → ใส่ label กลับ `ingress-ready=true` → Running · (ต้องเขียนขั้นแก้กลับให้ชัด เพราะทุกแล็บถัดไปพึ่ง Ingress)
- **คำถาม + แนวคำตอบ:**
  1. ทำไมระบบใช้ label แทนการอ้างชื่อตรง ๆ? → ชื่อ Pod เปลี่ยนตลอด (สร้างใหม่ = ชื่อใหม่) และมีเป็นร้อย · label บอก "คุณสมบัติ" ที่ไม่ผูกกับตัวตน จึงจับกลุ่มได้แม้สมาชิกเปลี่ยน
  2. selector `app=web` กับ `app=web,version=v2` ต่างกันอย่างไร? → AND ทุกเงื่อนไข · ยิ่งเจาะจงยิ่งได้กลุ่มเล็ก
  3. ถ้าเปลี่ยน label ของ Pod ที่อยู่ใต้ ReplicaSet จะเกิดอะไร? (คิดล่วงหน้า) → RS นับสมาชิกด้วย selector จึง "มองไม่เห็น" Pod นั้นแล้ว → สร้างตัวใหม่มาแทน (พิสูจน์ในแล็บ 006 ได้ถ้าเวลาเหลือ)
- **ชิ้นส่วนแอป:** web v1/v2 หลาย Pod · **ไฟล์:** `01-pods-with-labels.yaml` · **screenshot:** ไม่บังคับ (ถ้าจะมี: port-forward web-b แสดงป้าย v2 ให้เห็นว่า label version=v2 ตรงกับของจริง)

## 006-desired-state-and-self-healing
- **แนวคิดหลัก:** Kubernetes เทียบ "จำนวนที่อยากได้" กับ "จำนวนที่มีจริง" ตลอดเวลา แล้วแก้ส่วนต่างให้เอง
- **ปัญหาตั้งต้น:** แล็บ 003 ลบ Pod แล้วหายไปเลย ใครจะเป็นคนนั่งเฝ้าสร้างใหม่ตอนตีสาม? และถ้าอยากได้ web 3 ตัวรับโหลดร่วมกัน ต้องเขียน YAML 3 ไฟล์หรือ?
- **ขั้นตอน:**
  1. `01-replicaset.yaml` (ReplicaSet web, replicas: 3, selector app=web, template = Pod จากแล็บ 004) → `kubectl get rs,pods` (DESIRED/CURRENT/READY = 3/3/3, ชื่อ Pod = web-xxxxx)
  2. `02-door.yaml` "ประตูสำเร็จรูป" (Service web ClusterIP 3000 selector app=web + Ingress path `/`) → `http://localhost:8080` → รีเฟรชหลายครั้ง → การ์ดสถานะแสดงชื่อ Pod **สลับกัน** → **screenshot 2 ภาพ** ชื่อ Pod ต่างกัน · `for i in $(seq 10); do curl -s http://localhost/info | jq -r .pod; done` เห็นกระจาย 3 ชื่อ
  3. `kubectl delete pod <web-xxxxx>` ในเทอร์มินัลหนึ่ง ขณะที่อีกเทอร์มินัล `kubectl get pods -w` → ตัวใหม่ขึ้นแทนใน 1-2 วินาที ชื่อใหม่ · หน้าเว็บยังเปิดได้ตลอด (จุด "ว้าว" — เทียบกับแล็บ 003)
  4. `kubectl describe rs web` Events: `SuccessfulCreate` · `kubectl get events -n lab006 --sort-by=.lastTimestamp`
  5. `kubectl scale rs web --replicas=5` → 5 · `--replicas=1` → เหลือ 1 (ระบบลบส่วนเกินเอง) · กลับเป็น 3 ด้วยการแก้ไฟล์แล้ว apply (declarative)
  6. ลบทั้งกลุ่มพร้อมกัน `kubectl delete pods -l app=web` → ทั้ง 3 ตัวกลับมาใหม่ · หน้าเว็บอาจ 503 ชั่วครู่แล้วกลับมา
  7. เทียบตาราง: แล็บ 003 (Pod เปล่า) vs แล็บนี้ (Pod ใต้ ReplicaSet)
- **ทดลองให้พัง:** แก้ image ใน `01-replicaset.yaml` เป็น `:v2` แล้ว `apply` → `get rs` เปลี่ยน แต่ `get pods` ยังเป็น Pod เดิม หน้าเว็บยังเป็น v1 → ลบ Pod ไป 1 ตัว → ตัวใหม่เป็น v2 → รีเฟรชเจอ **v1 ปน v2** (screenshot ปน) = ระบบ "พัง" แบบเวอร์ชันไม่ตรงกัน → อธิบายว่า RS ดูแลแค่ "จำนวน" ไม่ดูแล "การเปลี่ยนแปลง" → แก้กลับเป็น v1 + ลบ Pod ที่เป็น v2 → นำไปสู่แล็บ 007
- **คำถาม + แนวคำตอบ:**
  1. self-healing เกิดขึ้นได้อย่างไร? → controller ของ ReplicaSet วนเทียบ desired (3) กับ actual (นับ Pod ที่ตรง selector) ทุกครั้งที่มีเหตุการณ์ · ต่างเมื่อไรก็สร้าง/ลบให้เท่ากัน (reconcile loop)
  2. ทำไมลบ Pod ในแล็บ 003 แล้วไม่มีตัวใหม่ขึ้น? → ไม่มี object ไหนถือ "desired = 1" ไว้ · Pod เปล่าไม่มีเจ้าของ (ดู `ownerReferences` ใน `-o yaml`)
  3. ReplicaSet รู้ได้อย่างไรว่า Pod ไหนเป็นของมัน? → selector = label จากแล็บ 005
- **ชิ้นส่วนแอป:** web v1 ×3 (+ door) · **ไฟล์:** `01-replicaset.yaml`, `02-door.yaml` · **screenshot:** `02-pod-name-a.png`, `02-pod-name-b.png`, `03-after-delete-new-pod.png`, `break-mixed-v1-v2.png`

## 007-deployment-manages-change
- **แนวคิดหลัก:** Deployment คือชั้นที่ดูแล "การเปลี่ยนแปลง" ให้เรา — scale และเปลี่ยนเวอร์ชันโดยไม่ต้องลบของเดิมทิ้งเอง
- **ปัญหาตั้งต้น:** แล็บ 006 อัปเวอร์ชันแล้วต้องไล่ลบ Pod เอง แถมได้ v1 ปน v2 — ถ้ามี 50 Pod และลูกค้ากำลังใช้งานอยู่ จะทำอย่างไร และถ้า v2 พังจะถอยกลับอย่างไร?
- **ขั้นตอน:**
  1. `01-deployment.yaml` (Deployment web replicas 3 v1 — เหมือน RS แต่ kind ต่าง) + `02-door.yaml` → `kubectl get deploy,rs,pods` → เห็น **3 ชั้น** ชื่อไล่กัน web → web-<hash> → web-<hash>-<id>
  2. `kubectl scale deploy web --replicas=5` แล้วกลับ 3 (ผ่าน RS)
  3. เปลี่ยนเวอร์ชันแบบ declarative: แก้ image เป็น `:v2` ใน `03-deployment-v2.yaml` (+ annotation `kubernetes.io/change-cause`) → `apply` → `kubectl rollout status deploy web` → `kubectl get rs` (RS เก่า 0, RS ใหม่ 3 — RS เก่าไม่ถูกลบ!) → **screenshot** เว็บเป็น v2 · `kubectl get pods -w` ระหว่างเปลี่ยนเห็นค่อย ๆ สลับ
  4. `kubectl rollout history deploy web` (REVISION 1, 2 + change-cause)
  5. `kubectl rollout undo deploy web` → RS เก่ากลับมา 3 · **screenshot** เว็บกลับเป็น v1 · `history` เป็น revision 3
  6. `kubectl describe deploy web` → Events: ScalingReplicaSet ... up/down ทีละขั้น
- **ทดลองให้พัง:** apply image `:v3` (ไม่มีจริง) → `rollout status` ค้าง → `get pods`: Pod ใหม่ 1 ตัว `ImagePullBackOff` แต่ Pod เดิม 3 ตัวยัง Running → `curl http://localhost/info` ยังตอบ v1 ได้ (เว็บไม่ล่ม!) → `kubectl rollout undo` → กลับปกติ · บทเรียน: Deployment ไม่ทิ้งของเก่าจนกว่าของใหม่จะพร้อม
- **คำถาม + แนวคำตอบ:**
  1. ทำไมถึงมีสามชั้น? → Pod = ตัวรัน · ReplicaSet = คุมจำนวนของ "เวอร์ชันหนึ่ง" · Deployment = คุมการเปลี่ยนเวอร์ชันโดยสร้าง RS ใหม่แล้วค่อย ๆ ย้ายจำนวนจาก RS เก่า
  2. rollback ทำได้เพราะอะไร? → Deployment เก็บ RS เก่าไว้ (revisionHistoryLimit) ที่ replicas=0 · undo = ย้ายจำนวนกลับไป RS นั้น
  3. ต่างจาก `docker compose up --build` อย่างไร? → compose ทิ้ง container เก่าแล้วสร้างใหม่ทันที (มีช่วงล่ม) และไม่มีประวัติให้ถอย
- **ชิ้นส่วนแอป:** web v1 → v2 → v1 · **ไฟล์:** `01-deployment.yaml`, `02-door.yaml`, `03-deployment-v2.yaml` · **screenshot:** `03-web-v2-after-rollout.png`, `05-web-v1-after-undo.png`

---

# ครั้งที่ 2 — `02_Session2_Networking_Config_Storage` : แอปคุยกันอย่างไร และตั้งค่า/เก็บข้อมูลอย่างไร
ธีม: ของที่ "เกิดใหม่ตลอดเวลา" จะเชื่อมต่อกันและเก็บของได้อย่างไร · เพิ่ม **api** (008) แล้ว **db** (011) ทีละชิ้น
ครั้งนี้ทุกแล็บที่ดูหน้าเว็บใช้ "ประตู" (Service web + Ingress `/`) ยกเว้น 009 · ตั้งแต่ 008 นักศึกษาเขียน Service เอง ส่วน Ingress ยังเป็นไฟล์สำเร็จรูป

## 008-why-we-need-service
- **แนวคิดหลัก:** Pod เกิดใหม่แล้ว IP เปลี่ยน จึงต้องมี "ชื่อคงที่" ให้เรียกแทน
- **ปัญหาตั้งต้น:** บน Compose web เรียก api ด้วยชื่อ `api` เฉย ๆ — บน Kubernetes Pod ของ api มี IP แต่เราเพิ่งเรียนว่า Pod ตายแล้วเกิดใหม่ตลอด แล้ว web จะเรียกใครกันแน่?
- **ขั้นตอน:**
  1. `01-web.yaml` (Deployment web 1 ตัว + Service web + Ingress = ประตู) · `02-api.yaml` (Deployment api replicas 2, ยังไม่มี db) → `kubectl get pods -o wide` จด IP ของ api ทั้ง 2
  2. เรียกด้วย IP ตรง ๆ: `kubectl exec deploy/web -- wget -qO- http://<api-ip>:8000/health` → ได้ · ตั้ง `API_BASE_URL=http://<api-ip>:8000` ให้ web (`03-web-ip.yaml`, apply) → หน้าเว็บ การ์ดสถานะ: api = เชื่อมต่อได้ (ชื่อ Pod api-...), db = ยังไม่มี → **screenshot**
  3. `kubectl delete pod <api-นั้น>` → Pod ใหม่ IP ใหม่ → รีเฟรช → api = **เชื่อมต่อไม่ได้** (screenshot) = ปัญหาจริง
  4. `04-api-service.yaml` (Service api ClusterIP port 8000 selector app=api) → `kubectl get svc,endpoints api` → Endpoints = IP ของ Pod ทั้ง 2 (Service "ตาม" Pod ด้วย label)
  5. เปลี่ยน web ให้เรียก `http://api:8000` (`05-web-by-name.yaml`) → หน้าเว็บกลับมาเชื่อมต่อ · รีเฟรช → ชื่อ Pod api **สลับ 2 ตัว** (Service กระจายโหลดให้ด้วย) → **screenshot**
  6. ลบ Pod api อีกครั้ง → `get endpoints` เปลี่ยน IP เอง · หน้าเว็บไม่สะดุด
  7. DNS ใน cluster: `kubectl exec deploy/web -- nslookup api` → `api.lab008.svc.cluster.local` → เทียบชื่อ service ใน Compose network
- **ทดลองให้พัง:** แก้ selector ของ Service เป็น `app: apii` → `kubectl get endpoints api` = `<none>` → หน้าเว็บ api เชื่อมต่อไม่ได้ ทั้งที่ Pod api ยัง Running → อ่าน `describe svc` แล้วแก้ selector กลับ → endpoints กลับมา
- **คำถาม + แนวคำตอบ:**
  1. ทำไมเรียกด้วย IP ตรง ๆ ไม่ได้? → IP ของ Pod เป็นของชั่วคราว Pod ใหม่ = IP ใหม่ · ไม่มีใครรับประกัน
  2. Service ช่วยอะไร? → ให้ชื่อ DNS + IP คงที่ (ClusterIP) แล้วส่งต่อไปยัง Pod ที่ตรง selector ณ ตอนนั้น · เป็นทั้ง "สมุดโทรศัพท์" และ "ตัวกระจายโหลด"
  3. Service รู้จัก Pod ได้อย่างไร? → label selector → รายการ Endpoints ที่อัปเดตเองเมื่อ Pod เกิด/ตาย
- **ชิ้นส่วนแอป:** web + api (ไม่มี db → การ์ดสถานะ db = ไม่เชื่อมต่อ ถือว่าถูกต้อง) · **ไฟล์:** `01-web.yaml`, `02-api.yaml`, `03-web-ip.yaml`, `04-api-service.yaml`, `05-web-by-name.yaml` · **screenshot:** `02-api-by-ip-connected.png`, `03-api-pod-deleted-unreachable.png`, `05-api-by-service-name.png`

## 009-service-types-and-access
- **แนวคิดหลัก:** Service มีหลายแบบ ต่างกันที่ "ใครเข้าถึงได้" ไม่ใช่ที่การทำงาน
- **ปัญหาตั้งต้น:** บน Compose มีแค่ web ที่ `ports:` ออกนอกเครื่อง ส่วน api/db ซ่อนอยู่ข้างใน — บน Kubernetes จะบอกว่า "ตัวนี้เปิดให้คนนอก ตัวนี้เฉพาะข้างใน" ได้อย่างไร?
- **ขั้นตอน:**
  1. `01-api.yaml` (Deployment + Service api **ClusterIP**) · `02-web-nodeport.yaml` (Deployment web 2 ตัว + Service web **NodePort** nodePort 30080) → `kubectl get svc` อ่านคอลัมน์ TYPE / CLUSTER-IP / PORT(S) `3000:30080/TCP`
  2. จากเครื่องเรียน (นอก cluster): `kubectl get nodes -o wide` เอา INTERNAL-IP → `curl http://<worker1-ip>:30080/info` · `<worker2-ip>` · `<control-plane-ip>` → **ทุก node ตอบ** แม้ Pod ไม่ได้อยู่บน node นั้น (ดู `.pod` ในคำตอบสลับกัน)
  3. ลอง ClusterIP จากเครื่องเรียน: `curl -m 3 http://<api-clusterip>:8000/health` → timeout · จากใน Pod: `kubectl exec deploy/web -- wget -qO- http://api:8000/health` → ได้ → "เฉพาะข้างใน" จริง
  4. เปิดจากเบราว์เซอร์: `kubectl port-forward svc/web 3000:3000 --address 0.0.0.0 &` → `http://localhost:3000` → **screenshot** · หมายเหตุว่าใน cluster จริง เปิด `http://<node-ip>:30080` ได้เลย แต่ในห้องเรียน node อยู่ใน Docker อีกชั้นจึงต้องพึ่ง port-forward/Ingress
  5. `kubectl get svc web -o yaml | grep -A3 ports` อ่าน port / targetPort / nodePort ให้ออกว่าแต่ละตัวอยู่ชั้นไหน
  6. ตารางเทียบ ClusterIP / NodePort / LoadBalancer (มีบน cloud) / Ingress (แล็บ 017) กับ `ports:` ของ Compose
- **ทดลองให้พัง:** ตั้ง `nodePort: 3000` (นอกช่วง 30000-32767) → apply error `provided port is not in the valid range` · สร้าง Service ที่สองใช้ nodePort 30080 ซ้ำ → error `port is already allocated` → อ่าน error แล้วแก้
- **คำถาม + แนวคำตอบ:**
  1. ClusterIP กับ NodePort ต่างกันตรงไหน? → ClusterIP มี IP/ชื่อเฉพาะในเครือข่ายภายใน cluster · NodePort = ClusterIP + เปิดพอร์ตเดียวกันบน **ทุก node** ให้คนนอกเข้า
  2. ใช้อันไหนเมื่อไร? → api/db = ClusterIP เสมอ (ไม่มีเหตุให้คนนอกเรียก) · NodePort ใช้ทดสอบ/ห้องเรียน · งานจริงเปิดผ่าน LoadBalancer หรือ Ingress
  3. ทำไม NodePort ต้องเป็นช่วง 30000-32767? → กันชนกับพอร์ตระบบบน node และให้ทุก node จองพอร์ตเดียวกันได้
- **ชิ้นส่วนแอป:** web ×2 + api · **ไฟล์:** `01-api.yaml`, `02-web-nodeport.yaml`, `03-nodeport-bad.yaml` · **screenshot:** `04-web-via-port-forward.png`

## 010-configmap-separate-config
- **แนวคิดหลัก:** config ไม่ควรอยู่ใน image — build ครั้งเดียวแต่เปลี่ยนพฤติกรรมได้ตามที่ deploy
- **ปัญหาตั้งต้น:** คณะจะเอา SkillSpace ไปใช้ 3 หน่วยงาน ชื่อระบบและสีต่างกัน — จะ build image 3 ชุดหรือ? บน Compose เราใช้ `environment:` แล้วบน Kubernetes เก็บค่าพวกนี้ไว้ที่ไหน?
- **ขั้นตอน:**
  1. deploy web + ประตู (`01-web.yaml`) → `kubectl exec deploy/web -- env | grep -E 'SITE_NAME|THEME'` (ไม่มี) → หน้าเว็บใช้ค่า default ของ image (SkillSpace · น้ำเงิน)
  2. `02-configmap.yaml` (ConfigMap web-config: SITE_NAME="ศูนย์บริการซ่อม คณะวิศวกรรมศาสตร์", THEME=amber) → `kubectl get cm web-config -o yaml`
  3. `03-web-envfrom.yaml` (เพิ่ม `envFrom: configMapRef`) → apply → Pod ใหม่ → `env` เห็นค่า → **screenshot** หน้าเว็บชื่อใหม่ สีเหลือง
  4. แก้ ConfigMap (THEME=rose) แล้ว apply → รีเฟรช → **ไม่เปลี่ยน** → env ถูกอ่านตอน container เริ่มเท่านั้น → `kubectl rollout restart deploy web` → เปลี่ยน → **screenshot**
  5. ใช้ key เดียวแบบ `valueFrom.configMapKeyRef` เทียบ `envFrom` · กล่าวถึงการ mount เป็นไฟล์ (อัปเดตเองได้) แค่ 3 บรรทัด ไม่ทำแล็บ
  6. ตารางเทียบ `environment:` ใน Compose ↔ ConfigMap+env ใน Deployment
- **ทดลองให้พัง:** อ้าง ConfigMap ชื่อผิด (`web-confg`) → Pod ใหม่ `CreateContainerConfigError` · `describe` → `configmap "web-confg" not found` · Deployment ยังคง Pod เก่าไว้ (เว็บไม่ล่ม) → แก้ชื่อ → ผ่าน
- **คำถาม + แนวคำตอบ:**
  1. ถ้าฝัง config ไว้ใน image จะเจอปัญหาอะไร? → เปลี่ยนค่าเดียวต้อง build/push/deploy ใหม่ · image เดียวใช้หลายสภาพแวดล้อมไม่ได้ · เสี่ยงค่าของ dev หลุดไป prod
  2. เปลี่ยน ConfigMap แล้วทำไมหน้าเว็บไม่เปลี่ยน? → env ถูก inject ตอนสร้าง container · ต้อง restart Pod (rollout restart) หรือ mount เป็นไฟล์
  3. ConfigMap ควรเก็บอะไร/ไม่ควรเก็บอะไร? → ค่าที่ไม่ลับ (ชื่อ ธีม URL) · รหัสผ่านไปแล็บ 011
- **ชิ้นส่วนแอป:** web (SITE_NAME/THEME runtime env) · **ไฟล์:** `01-web.yaml`, `02-configmap.yaml`, `03-web-envfrom.yaml`, `04-configmap-rose.yaml` · **screenshot:** `03-web-amber-new-name.png`, `04-web-rose-after-restart.png`

## 011-secret-and-why-not-configmap
- **แนวคิดหลัก:** ข้อมูลลับต้องแยกออกมาต่างหาก และ base64 ไม่ใช่การเข้ารหัส
- **ปัญหาตั้งต้น:** ถึงเวลาต่อฐานข้อมูลจริง — รหัสผ่าน PostgreSQL จะไปอยู่ตรงไหน? ใน image? ใน ConfigMap ที่ใครก็ `kubectl get` ได้? ใน git?
- **ขั้นตอน:**
  1. `01-secret.yaml` (Secret db-secret ใช้ `stringData: POSTGRES_PASSWORD: labpass`) → `kubectl get secret db-secret -o yaml` → เห็นเป็น base64 (`data:`)
  2. `02-db.yaml` (Deployment db จาก `k8s-lab-db:v1` 1 ตัว + Service db :5432; POSTGRES_DB/USER เป็นค่าตรง POSTGRES_PASSWORD จาก `secretKeyRef`) — ยังไม่มี PVC (จงใจ รอ 012/013)
  3. `03-api.yaml` (api อ่าน DB_HOST=db, DB_NAME, DB_USER ค่าตรง + DB_PASSWORD จาก Secret) + `04-web.yaml` + ประตู → หน้าเว็บ **แสดงข้อมูลจริงครั้งแรก** (dashboard มีตัวเลข, การ์ดสถานะเขียวทั้ง 3) → **screenshot**
  4. ถอดหน้ากาก: `kubectl get secret db-secret -o jsonpath='{.data.POSTGRES_PASSWORD}' | base64 -d` → `labpass` → base64 = การ "แปลงรูป" ไม่ใช่การเข้ารหัส
  5. `kubectl exec deploy/api -- env | grep DB_` → Pod เห็นค่าจริงเสมอ (คนที่ exec เข้า Pod ได้ก็เห็น)
  6. ตารางเทียบ ConfigMap vs Secret (ต่างที่: ตั้งใจแยกสิทธิ์ RBAC ได้, ไม่โชว์ใน describe, encrypt at rest ได้, ไม่ commit ลง git) และแนวทางจริง (external secret manager) กล่าวถึงสั้น ๆ
- **ทดลองให้พัง:** แก้ Secret เป็นรหัสผิด (`wrongpass`) + `rollout restart deploy api` → `kubectl logs deploy/api` เห็น `password authentication failed` · `curl` `/ready` ของ api = 503 · หน้าเว็บ db = ไม่เชื่อมต่อ (screenshot) · จุดสังเกต: restart db ไม่ช่วย เพราะ PostgreSQL ตั้งรหัสตอน initdb ครั้งแรกเท่านั้น → แก้ Secret กลับ + restart api → หาย
- **คำถาม + แนวคำตอบ:**
  1. Secret ต่างจาก ConfigMap อย่างไร? → กลไกส่งค่าเหมือนกัน แต่ Secret ถูกจัดเป็น "ของลับ" ให้จำกัดสิทธิ์อ่าน/เข้ารหัสใน etcd ได้ และไม่แสดงค่าใน describe
  2. base64 ปลอดภัยไหม? → ไม่ ถอดกลับได้ในคำสั่งเดียว · ความปลอดภัยมาจาก RBAC + encryption at rest ไม่ใช่จาก base64
  3. ทำไมห้าม commit Secret ลง git? → git จำตลอดกาล ใครเข้าถึง repo ก็ได้รหัส · ให้ commit เฉพาะ "โครง" แล้วใส่ค่าตอน deploy
- **ชิ้นส่วนแอป:** web + api + db (ครั้งแรกที่ครบ 3 ชั้น ไม่มี PVC) · **ไฟล์:** `01-secret.yaml`, `02-db.yaml`, `03-api.yaml`, `04-web.yaml`, `05-door.yaml` · **screenshot:** `03-dashboard-with-real-data.png`, `break-db-auth-failed.png`

## 012-why-data-disappears
- **แนวคิดหลัก:** ข้อมูลที่เขียนไว้ใน container หายเมื่อ Pod เกิดใหม่ เพราะ container ถูกสร้างใหม่จาก image เสมอ
- **ปัญหาตั้งต้น:** ระบบจากแล็บ 011 ใช้งานได้ พนักงานกรอกใบแจ้งซ่อมไป 1 อาทิตย์ แล้ววันหนึ่ง Pod ของ db ถูกย้ายเครื่อง — ข้อมูลจะยังอยู่ไหม? (ให้ทายก่อน)
- **ขั้นตอน:**
  1. apply ทั้งชุดจากแล็บ 011 (`kubectl apply -f manifests/`) → หน้าเว็บมีข้อมูล seed
  2. เพิ่มใบแจ้งซ่อมผ่านหน้าเว็บ (กระดานงานซ่อม → สร้างใบใหม่ ใส่ชื่อที่จำง่าย เช่น "โปรเจกเตอร์ห้อง 999 ภาพไม่ขึ้น") → **screenshot** ก่อน/หลังสร้าง · `kubectl exec deploy/db -- psql -U opsuser -d skillspace -c 'select count(*) from tickets'` = 9
  3. เขียนไฟล์ธรรมดาใน web Pod ด้วย: `kubectl exec deploy/web -- sh -c 'echo hi > /tmp/note.txt'`
  4. `kubectl delete pod -l app=db` → Pod ใหม่ → รอ Ready → psql count = 8 · รีเฟรชหน้าเว็บ ใบที่เพิ่มหายไป → **screenshot** · ไฟล์ /tmp/note.txt ใน web Pod ใหม่ก็หาย
  5. อธิบาย: container = image layers (อ่านอย่างเดียว) + writable layer ที่ตายไปพร้อม container · Pod ใหม่ = container ใหม่ · เทียบกับ `docker rm` แล้ว `docker run` ใหม่
  6. ทดลองขั้นกลาง `emptyDir`: `02-db-emptydir.yaml` (volume emptyDir ที่ PGDATA) → เพิ่มใบซ่อม → `kubectl exec deploy/db -- kill 1` (container restart, Pod เดิม) → ข้อมูลยังอยู่ · `delete pod` → หาย → emptyDir อยู่กับ "Pod" ไม่ใช่ "container" แต่ก็ไม่รอด Pod ใหม่
- **ทดลองให้พัง:** แล็บนี้คือการทำให้พังโดยตัวมันเอง (ข้อ 4) · หัวข้อ "ทดลองให้พัง" ให้ทำซ้ำในมุมกลับ: scale db เป็น 0 แล้ว 1 → ข้อมูลหายเหมือนกัน → "วิธีแก้" = แล็บ 013
- **คำถาม + แนวคำตอบ:**
  1. ทำไมข้อมูลถึงหาย? → เขียนลง writable layer ของ container · Pod ใหม่สร้าง container ใหม่จาก image ที่ไม่มีข้อมูลนั้น
  2. แอปแบบไหนได้รับผลกระทบ? → ทุกอย่างที่เก็บสถานะในตัวเอง (ฐานข้อมูล, อัปโหลดไฟล์, queue) · web/api ที่ไม่เก็บอะไร (stateless) ไม่กระทบ
  3. emptyDir ช่วยอะไรและไม่ช่วยอะไร? → รอด container restart ภายใน Pod เดียวกัน (แชร์ระหว่าง container ใน Pod ได้) แต่หายพร้อม Pod
- **ชิ้นส่วนแอป:** ครบ 3 ชั้น (ไม่มี PVC) · **ไฟล์:** `manifests/` (คัดจาก 011), `02-db-emptydir.yaml` · **screenshot:** `02-ticket-created.png`, `04-ticket-gone-after-pod-recreate.png`

## 013-persistent-storage-with-pvc
- **แนวคิดหลัก:** ถ้าอยากให้ข้อมูลอยู่รอด ต้องเก็บไว้ "นอก" container โดยขอพื้นที่ผ่าน PVC
- **ปัญหาตั้งต้น:** บน Compose เราใช้ named volume `pgdata` แล้วข้อมูลรอด `docker compose down` — บน Kubernetes ที่ Pod ย้ายเครื่องได้ จะขอ "ที่เก็บของนอก container" ได้อย่างไร?
- **ขั้นตอน:**
  1. `01-pvc.yaml` (PersistentVolumeClaim db-data 1Gi ReadWriteOnce ไม่ระบุ storageClassName) → `kubectl get pvc,pv,storageclass` → Bound เอง (kind มี StorageClass `standard` แบบ dynamic)
  2. `02-db.yaml` (Deployment db mount PVC ที่ `/var/lib/postgresql/data` + env `PGDATA=/var/lib/postgresql/data/pgdata`) + Secret/api/web/ประตู เหมือน 011
  3. เพิ่มใบแจ้งซ่อมผ่านหน้าเว็บ → **screenshot** · psql count = 9
  4. `kubectl delete pod -l app=db` → Pod ใหม่ → รีเฟรช → **ข้อมูลยังอยู่ครบ** → **screenshot** · `kubectl describe pvc db-data` (Used By: Pod ใหม่)
  5. ของอยู่ที่ไหนจริง: `kubectl get pv -o wide` → `kubectl describe pv <ชื่อ>` (Path บน node) → `docker exec devtools-worker ls /var/local-path-provisioner/` → เห็นโฟลเดอร์ pgdata "นอก container บน node"
  6. ตารางเทียบ named volume (Compose) ↔ PVC/PV/StorageClass และ emptyDir (แล็บ 012) ↔ PVC
- **ทดลองให้พัง:** `kubectl delete pvc db-data` ขณะ db ยังใช้อยู่ → `get pvc` ค้าง `Terminating` (finalizer `kubernetes.io/pvc-protection` กันไว้) → ลบ Pod db → PVC หายจริง → Pod ใหม่ค้าง `Pending` (`describe`: persistentvolumeclaim "db-data" not found) → apply PVC ใหม่ → Pod ขึ้นแต่ข้อมูลเป็น seed (ลบ PVC = ลบข้อมูล) → บทเรียน: ข้อมูลอยู่ที่ PV ไม่ใช่ที่ Pod
- **คำถาม + แนวคำตอบ:**
  1. PVC คือการขออะไร? → "ใบขอ" พื้นที่ (ขนาด/โหมด) จาก cluster · cluster จัดหา PV (ของจริง) มาผูกให้ · แอปไม่ต้องรู้ว่าดิสก์อยู่ไหน
  2. ต่างจาก emptyDir อย่างไร? → emptyDir ผูกกับ Pod (หายพร้อม Pod) · PVC ผูกกับ namespace/claim ที่มีอายุยืนกว่า Pod
  3. ทำไม db Pod ใหม่ถึงเห็นข้อมูลเดิม? → Pod ใหม่ mount claim เดิม → PV เดิม → ไดเรกทอรีเดิมบน node
- **ชิ้นส่วนแอป:** ครบ 3 ชั้น + PVC · **ไฟล์:** `01-pvc.yaml`, `02-db.yaml`, `03-secret.yaml`, `04-api.yaml`, `05-web.yaml`, `06-door.yaml` · **screenshot:** `03-ticket-created.png`, `04-ticket-survives-pod-delete.png`

## 014-running-is-not-ready
- **แนวคิดหลัก:** "Pod Running" ไม่ได้แปลว่า "แอปพร้อมรับงาน"
- **ปัญหาตั้งต้น:** api ขึ้นมาแล้ว `Running` แต่ db ยังไม่พร้อม — Service ส่ง request ไปให้ api ตัวนั้น ผู้ใช้ก็เจอ error · บน Compose เราเคยแก้ด้วย `healthcheck` + `depends_on: service_healthy` แล้วบน Kubernetes?
- **ขั้นตอน:**
  1. ดู endpoint ที่แอปมีให้: `/health` (ตอบตัวเอง) vs `/ready` (ยิง SELECT 1 เข้า db) · `kubectl exec deploy/web -- wget -qO- http://api:8000/ready`
  2. `01-api-with-probes.yaml` (api replicas 2 + readinessProbe httpGet `/ready` period 5s + livenessProbe httpGet `/health` period 10s) → `get pods` READY 1/1 · `get endpoints api` มี 2 IP
  3. ทำให้ db หาย: `kubectl scale deploy db --replicas=0` → ภายใน ~10 วิ `get pods`: api ยัง `Running` แต่ READY `0/1` · `get endpoints api` = `<none>` · หน้าเว็บ api = ไม่พร้อม → **screenshot** · `describe pod api-...` Events: `Readiness probe failed: HTTP probe failed with statuscode: 503`
  4. `kubectl scale deploy db --replicas=1` → api กลับ 1/1 เอง ไม่ต้อง restart · endpoints กลับมา
  5. liveness: สั่งให้แอป "ป่วย" `kubectl exec deploy/web -- wget -qO- --post-data='{"ok":false}' --header='Content-Type: application/json' http://api:8000/debug/health` (ยิงถูก Pod ตัวใดตัวหนึ่ง) → ~30 วิ `get pods` RESTARTS +1 · Events: `Liveness probe failed` → `Container api failed liveness probe, will be restarted` → หลัง restart หายป่วยเอง
  6. ตารางเทียบ readiness (ถอดออกจาก Service ชั่วคราว) vs liveness (ฆ่าแล้วเกิดใหม่) vs Compose healthcheck/depends_on
- **ทดลองให้พัง:** ตั้ง readinessProbe path ผิด `/readyz` → Pod ใหม่ไม่เคย Ready (0/1) · endpoints ว่าง · `describe` → `statuscode: 404` → แก้ path · และ/หรือ liveness period 1s timeout 1s บน `/ready` → api ถูก restart วนซ้ำเมื่อ db ช้า → บทเรียน "อย่าเอา dependency ไปไว้ใน liveness"
- **คำถาม + แนวคำตอบ:**
  1. readiness กับ liveness ตอบคนละคำถามอย่างไร? → readiness: "ตอนนี้รับงานได้ไหม" (ไม่ได้ = ถอดจาก endpoints ชั่วคราว) · liveness: "ยังมีชีวิตไหม" (ไม่ = restart container)
  2. ทำไม /ready ต้องยิง db จริง? → ถ้าตอบ ok ลอย ๆ Service จะส่งงานให้ทั้งที่ทำงานไม่ได้ · เทียบ healthcheck ของ api ใน Compose ที่ยิง SELECT 1
  3. ทำไมไม่ใส่ db check ไว้ใน liveness? → db ล่ม = api ทุกตัวถูกฆ่าวนไปด้วยทั้งที่ไม่ผิด · ให้ liveness เช็กเฉพาะตัวเอง
- **ชิ้นส่วนแอป:** ครบ 3 ชั้น + PVC + probes (api) · **ไฟล์:** `manifests/` (จาก 013) + `01-api-with-probes.yaml`, `02-api-bad-readiness.yaml` · **screenshot:** `03-api-not-ready-when-db-down.png`, `04-api-ready-again.png`

---

# ครั้งที่ 3 — `03_Session3_Application_Deployment` : ประกอบเป็นระบบจริงและดูแลต่อ
ธีม: เห็นภาพรวมว่าชิ้นส่วนทั้งหมดประกอบกันเป็นระบบที่ใช้งานได้อย่างไร · ทุกแล็บใช้โฟลเดอร์ `manifests/` แล้ว `kubectl apply -f manifests/` · เปิดเว็บผ่าน Ingress 8080

## 015-assembling-a-real-application
- **แนวคิดหลัก:** แอปจริงคือหลาย object ที่ทำงานร่วมกัน ไม่ใช่ object เดียว
- **ปัญหาตั้งต้น:** compose.yaml ไฟล์เดียวมี 3 service — บน Kubernetes ระบบเดียวกันต้องใช้ object กี่ตัว ตัวไหนทำหน้าที่อะไร และถ้าลืมตัวใดตัวหนึ่งจะรู้ได้อย่างไร?
- **ขั้นตอน:**
  1. อ่านโฟลเดอร์ `manifests/` (01-configmap, 02-web-deployment, 03-web-service, 04-api-deployment, 05-api-service, 06-ingress) · ตารางแปลง compose → object (สะพานจากครั้งที่ 1)
  2. `kubectl apply -f manifests/` (ทั้งโฟลเดอร์ในคำสั่งเดียว) → `kubectl get all,ingress,configmap -n lab015` อ่านให้ครบว่ามีอะไรเกิดขึ้น
  3. `http://localhost:8080` → web+api เชื่อมต่อ, db ยังไม่มี (จงใจ — ชั้นข้อมูลไปแล็บ 016) → **screenshot**
  4. "ถ้าขาดตัวไหน": `kubectl delete svc api` → หน้าเว็บ api ไม่เชื่อมต่อ (screenshot) → `kubectl apply -f manifests/` (idempotent — ของที่มีอยู่ unchanged ของที่หายถูกสร้างคืน) · ลอง `delete ingress web` → 404 จาก nginx → apply คืน
  5. `kubectl get -f manifests/` และ `kubectl diff -f manifests/` — เทียบไฟล์กับของจริง
  6. `kubectl get pods -o wide` → web/api กระจายอยู่คนละ node — ระบบเดียวกันวิ่งบนหลายเครื่อง
- **ทดลองให้พัง:** `kubectl delete configmap web-config` แล้ว `rollout restart deploy web` → Pod ใหม่ `CreateContainerConfigError` แต่ Pod เก่ายังให้บริการ → `kubectl apply -f manifests/` คืน → rollout เดินต่อเอง · บทเรียน: โฟลเดอร์ manifests คือ "แหล่งความจริง" apply ซ้ำ = ซ่อม
- **คำถาม + แนวคำตอบ:**
  1. แต่ละ object ในระบบนี้ทำหน้าที่อะไร? → Deployment รันและดูแลจำนวน/เวอร์ชัน · Service ให้ชื่อ+กระจายโหลด · ConfigMap ให้ค่า · Ingress เปิดประตูจากภายนอก
  2. ถ้าขาดตัวไหนจะเกิดอะไร? → ขาด Service api = web หา api ไม่เจอ · ขาด Ingress = คนนอกเข้าไม่ได้แต่ข้างในปกติ · ขาด ConfigMap = Pod ใหม่สร้างไม่ได้
  3. ทำไม apply ทั้งโฟลเดอร์ซ้ำได้โดยไม่พัง? → declarative: ของที่ตรงอยู่แล้ว unchanged · ที่หาย created · ที่ต่าง configured
- **ชิ้นส่วนแอป:** web + api (+ConfigMap + Ingress) · **ไฟล์:** `manifests/01..06` · **screenshot:** `03-web-api-assembled-no-db.png`, `04-api-service-deleted.png`

## 016-adding-a-database
- **แนวคิดหลัก:** ส่วนที่มีข้อมูลต้องการการดูแลต่างจากส่วนที่ไม่มีข้อมูล
- **ปัญหาตั้งต้น:** web กับ api สั่ง scale เป็น 3 ได้สบาย — ถ้าสั่ง db เป็น 3 บ้างจะเกิดอะไร? (ทายก่อน) ทำไมชั้นข้อมูลถึงต้องคิดต่างจากชั้นอื่น?
- **ขั้นตอน:**
  1. เพิ่มไฟล์ใน `manifests/`: 07-secret, 08-pvc, 09-db-deployment (mount PVC, PGDATA subdir, ใช้ Secret), 10-db-service · แก้ 04-api-deployment ให้อ่าน DB_PASSWORD จาก Secret → `kubectl apply -f manifests/` → เฉพาะที่เปลี่ยนถูกสร้าง
  2. `http://localhost:8080` → ครบ 3 ชั้น การ์ดสถานะเขียวหมด dashboard มีข้อมูล → **screenshot**
  3. เพิ่มใบแจ้งซ่อมผ่านหน้าเว็บ → ลบ Pod db → ข้อมูลยังอยู่ (สรุปซ้ำจาก 013 แต่ในบริบทระบบครบ) → **screenshot**
  4. stateless ก่อน: `kubectl scale deploy web --replicas=3` และ `api --replicas=3` → ทุกตัว Ready ทันที รีเฟรชแล้วชื่อ Pod สลับ · `scale ... --replicas=1` กลับได้ทันที ไม่มีอะไรเสีย
  5. stateful: `kubectl scale deploy db --replicas=2` → สังเกตอาการจริง (ตัวที่ 2 `CrashLoopBackOff` เพราะ PGDATA มี lock/ถูกใช้อยู่ หรือ `Pending` เพราะ PV ผูกกับ node เดิม) → `logs` / `describe` อ่านสาเหตุ → `--replicas=1` กลับ
  6. ตาราง stateless vs stateful: scale, ลบทิ้งได้ไหม, ต้องมี PVC ไหม, ลำดับการเริ่ม, backup · กล่าวถึง StatefulSet 3 บรรทัด (มีอยู่ ใช้เมื่อไร ไม่ทำแล็บ)
- **ทดลองให้พัง:** ข้อ 5 คือการพังที่ตั้งใจ (db 2 ตัวบน PVC เดียว) · เพิ่ม: ลบ Secret แล้ว restart api → api /ready 503 → apply คืน
- **คำถาม + แนวคำตอบ:**
  1. stateless กับ stateful ต่างกันอย่างไรในทางปฏิบัติ? → stateless ทิ้ง/สร้าง/scale ได้ตามใจ เพราะไม่มีของติดตัว · stateful ต้องผูกดิสก์ ต้องคุมว่าใครเขียน ต้อง scale อย่างระวัง
  2. ทำไม db scale เป็น 2 แล้วพัง? → PostgreSQL หนึ่ง instance ต้องเป็นเจ้าของ data dir คนเดียว · PV แบบ RWO ผูกกับ node เดียว
  3. ถ้าต้องการ db หลายตัวจริง ๆ ทำอย่างไร? → replication ของ PostgreSQL เอง + StatefulSet (แต่ละตัวมี PVC ของตัวเอง) หรือใช้ managed database
- **ชิ้นส่วนแอป:** ครบ 3 ชั้น + PVC + Secret · **ไฟล์:** `manifests/01..10` · **screenshot:** `02-full-stack-with-data.png`, `03-data-survives.png`, `05-db-scale-2-crash.png` (ถ้า UI ไม่แสดง ใช้ผล kubectl แทน)

## 017-ingress-the-front-door
- **แนวคิดหลัก:** Ingress คือประตูหน้าบ้านที่ทำหน้าที่เดียวกับ reverse proxy ที่เคยเรียน แต่รับคำสั่งจาก Kubernetes
- **ปัญหาตั้งต้น:** ตอนเรียน Traefik เราเคยเจอ "2 service = 2 port, 20 service = 20 port" แล้วแก้ด้วย reverse proxy — บน Kubernetes NodePort ก็มีปัญหาเดียวกัน แล้วใครจะเป็น proxy ให้ และเราสั่งมันอย่างไร?
- **ขั้นตอน:**
  1. `kubectl -n ingress-nginx get pods,svc` → proxy ตัวจริง (ingress-nginx) รันอยู่แล้วตั้งแต่ `k8s-bootstrap` · ดูว่ามันฟัง hostPort 80/443 บน control-plane (ตรงกับ `-p 8080:80` ของเครื่องเรียน) — วาดเส้นทาง host:8080 → container:80 → node:80 → ingress-nginx → Service → Pod
  2. `manifests/06-ingress.yaml` เขียนเอง: rules paths `/` → web:3000, `/api` → api:8000 (pathType Prefix, ไม่ใส่ host) → `kubectl get ingress` / `describe ingress` (Backends)
  3. ทดสอบ: `curl http://localhost/info` (web) · `curl http://localhost/api/whoami` (api ผ่านประตูเดียวกัน) · เบราว์เซอร์เปิด `/` และ `/api/dashboard` → **screenshot 2 ภาพ**
  4. `kubectl -n ingress-nginx logs deploy/ingress-nginx-controller --tail=5` → เห็น access log ของ request ที่เพิ่งยิง (หลักฐาน "ผ่าน proxy")
  5. ตารางเทียบ NodePort vs Ingress vs Traefik (entrypoint/router/service ↔ Ingress rule/path/backend) · กล่าวถึง IngressClass และ TLS 3 บรรทัด
- **ทดลองให้พัง:** แก้ backend service เป็น `web-svc` (ไม่มีจริง) → `curl -i localhost:8080/` = `503 Service Temporarily Unavailable` จาก nginx · `describe ingress` → `error: service "lab017/web-svc" does not exist` · แก้กลับ → 200 · เพิ่ม: สลับ port เป็น 3001 → 503/502 เช่นกัน → อ่าน log ของ controller
- **คำถาม + แนวคำตอบ:**
  1. Ingress ต่างจาก NodePort อย่างไร? → NodePort = เปิดพอร์ตต่อ Service (หลาย service หลายพอร์ต, L4) · Ingress = ประตูเดียว แยกด้วย path/host (L7) และคุม TLS ได้
  2. เกี่ยวกับ reverse proxy ที่เรียนมาอย่างไร? → Ingress คือ "กฎ" · ingress controller (nginx/Traefik) คือ proxy ที่อ่านกฎจาก API server แล้ว config ตัวเองอัตโนมัติ — สิ่งที่เคยเขียนเองใน traefik.yml
  3. ทำไม `/api` ไปถึง api ได้โดยไม่ตัด prefix? → api ของเราตั้ง route ขึ้นต้น `/api/...` อยู่แล้ว · ถ้าแอปไม่รู้จัก prefix ต้องใช้ rewrite annotation
- **ชิ้นส่วนแอป:** ครบ 3 ชั้น + Ingress 2 path · **ไฟล์:** `manifests/01..10` (จาก 016) + `06-ingress.yaml` (2 path), `06-ingress-bad.yaml` · **screenshot:** `03-root-via-ingress.png`, `03-api-dashboard-json-via-ingress.png`

## 018-updating-without-downtime
- **แนวคิดหลัก:** เปลี่ยนเวอร์ชันทีละส่วนทำให้ผู้ใช้ไม่สะดุด
- **ปัญหาตั้งต้น:** ต้องปล่อย SkillSpace v2 ตอนที่พนักงานกำลังใช้งาน — ห้ามมีวินาทีที่หน้าเว็บล่ม ทำได้จริงหรือ? แล้วถ้า v2 มีบั๊กจะถอยกลับภายในกี่วินาที?
- **ขั้นตอน:**
  1. `manifests/02-web-deployment.yaml` web replicas 3 + `strategy.rollingUpdate {maxSurge: 1, maxUnavailable: 0}` + `minReadySeconds: 5` + readinessProbe `/readyz` (จำเป็นสำหรับ zero-downtime) → apply
  2. เทอร์มินัล 2: `while true; do curl -s -m 2 http://localhost/info | jq -r '"\(.pod)  \(.version)"' || echo FAIL; sleep 0.3; done` (ลูปพิสูจน์)
  3. เทอร์มินัล 1: แก้ image `:v2` → `kubectl apply -f manifests/02-web-deployment.yaml` → `kubectl rollout status deploy web` · ลูปเห็น v1 ปน v2 ค่อย ๆ เปลี่ยนโดยไม่มี FAIL · `kubectl get rs -w` เห็น RS ใหม่ขึ้นทีละ 1 RS เก่าลดทีละ 1
  4. **screenshot ระหว่าง rollout** (ใช้ shot.js วนถ่ายทุก 1 วิ เก็บภาพที่ปน v1/v2 — ต้องเป็นภาพจริง) และหลังจบ (v2 ทั้งหมด)
  5. `stern -n lab018 web --tail 3` ดู log ของ Pod หลายตัวพร้อมกันระหว่างเปลี่ยน
  6. `kubectl rollout undo deploy web` → ลูปกลับเป็น v1 ไม่มี FAIL · `rollout history`
- **ทดลองให้พัง:** เปลี่ยน `strategy.type: Recreate` (`02-web-recreate.yaml`) แล้วเปลี่ยนเวอร์ชันอีกครั้ง → ลูปโชว์ `FAIL`/503 ติดกันหลายวินาที (downtime จริง!) → กลับเป็น RollingUpdate · เพิ่ม: ถอด readinessProbe แล้ว rollout → เห็น FAIL ประปราย เพราะ Pod ใหม่รับงานก่อนพร้อม
- **คำถาม + แนวคำตอบ:**
  1. ทำไม rolling update ถึงไม่ทำให้เว็บล่ม? → มี Pod เก่าให้บริการเสมอ (maxUnavailable 0) · Pod ใหม่ถูกใส่เข้า Service ก็ต่อเมื่อ readiness ผ่าน
  2. rollback ทำได้เพราะระบบเก็บอะไรไว้? → ReplicaSet ของทุก revision (replicas 0) พร้อม template เดิม · undo = ย้ายจำนวนกลับ
  3. readinessProbe เกี่ยวอะไรกับ zero-downtime? → ไม่มี probe = Pod ถูกนับว่าพร้อมทันทีที่ container start → request ไปถึงก่อนแอปฟังพอร์ต → error ชั่วครู่
- **ชิ้นส่วนแอป:** ครบ 3 ชั้น · web v1→v2→v1 · **ไฟล์:** `manifests/` + `02-web-recreate.yaml` · **screenshot:** `04-rollout-in-progress-mixed.png`, `04-rollout-done-v2.png`, `06-after-undo-v1.png`

## 019-telling-kubernetes-what-you-need
- **แนวคิดหลัก:** Kubernetes ต้องรู้ว่าแอปใช้ทรัพยากรเท่าไร จึงจะเลือก node ให้ถูกและกันไม่ให้ตัวหนึ่งกินหมด
- **ปัญหาตั้งต้น:** scheduler เลือก node ให้ Pod ได้อย่างไรทั้งที่เราไม่เคยบอกว่าแอปหนักแค่ไหน? ถ้า web ตัวหนึ่ง memory leak จะลาก api/db บน node เดียวกันล้มไปด้วยไหม?
- **ขั้นตอน:**
  1. `kubectl describe node devtools-worker | sed -n '/Allocated resources/,/Events/p'` → ก่อนใส่ requests เห็น 0 (Kubernetes "ไม่รู้") · `kubectl top nodes` / `kubectl top pods -n lab019` (metrics-server)
  2. `manifests/02-web-deployment.yaml` เพิ่ม `resources: requests {cpu: 100m, memory: 128Mi} limits {cpu: 500m, memory: 256Mi}` → apply → `describe node` Allocated เปลี่ยน · `kubectl get pod -o jsonpath='{.spec.containers[0].resources}'`
  3. ขอเกินที่มี: `03-web-too-big.yaml` (requests cpu: 64) → Pod `Pending` · `describe pod` → `0/3 nodes are available: 3 Insufficient cpu` · `kubectl get events` · แก้กลับ
  4. limits ทำงาน: `04-web-oom.yaml` (limits memory: 32Mi) → Pod `OOMKilled` วน RESTARTS · `describe` Last State: Terminated Reason: OOMKilled · แก้กลับ
  5. QoS class: `kubectl get pod -o jsonpath='{.status.qosClass}'` (Guaranteed/Burstable/BestEffort) 3 บรรทัด · กล่าวถึง HPA/ResourceQuota/LimitRange ว่ามีอยู่ ใช้เมื่อไร (ไม่ทำแล็บ)
- **ทดลองให้พัง:** ข้อ 3 (Pending) และข้อ 4 (OOMKilled) คือหัวข้อ "ทดลองให้พัง" 2 อาการ พร้อมวิธีอ่านและแก้กลับ
- **คำถาม + แนวคำตอบ:**
  1. requests กับ limits มีผลคนละจังหวะอย่างไร? → requests ใช้ตอน **schedule** (เลือก node ที่เหลือพอ) · limits ใช้ตอน **รัน** (CPU ถูก throttle · memory เกิน = OOMKilled)
  2. ทำไม Pod Pending ทั้งที่เครื่องยังว่างเยอะ? → scheduler นับจาก requests ที่ "จอง" ไม่ใช่การใช้จริง · ขอเกินที่ node ใดมีให้ทั้งหมด = ไม่มี node รับ
  3. ควรตั้ง requests เท่าไร? → วัดจาก `kubectl top` ตอนใช้งานจริง แล้วตั้ง requests ≈ ค่าเฉลี่ย limits ≈ ค่าสูงสุดที่ยอมรับ
- **ชิ้นส่วนแอป:** web (ตัวเดียวพอ) + ระบบครบถ้ามี · **ไฟล์:** `manifests/`, `03-web-too-big.yaml`, `04-web-oom.yaml` · **screenshot:** ไม่บังคับ (หลักฐานเป็น kubectl)

## 020-reading-the-symptoms
- **แนวคิดหลัก:** อาการที่ Kubernetes แสดง บอกได้ว่าปัญหาอยู่ชั้นไหน
- **ปัญหาตั้งต้น:** เพื่อนส่งโฟลเดอร์ manifests มาให้ apply แล้วหน้าเว็บไม่ขึ้น — มี Pod 4 ตัวสถานะไม่เหมือนกันเลย จะเริ่มดูจากตรงไหน?
- **ขั้นตอน (ลำดับตรวจ get → describe → logs → events ทุกเคส):**
  1. `kubectl apply -f broken/` (4 ไฟล์จงใจพัง อยู่ใน ns lab020) → `kubectl get pods,svc,endpoints` จดอาการ: `Pending` · `ImagePullBackOff` · `CrashLoopBackOff` · Service มี endpoints `<none>`
  2. เคส A `broken/01-pending.yaml` (requests cpu 64) → describe → `Insufficient cpu` → ชั้น scheduler → แก้ requests
  3. เคส B `broken/02-imagepull.yaml` (image `k8s-lab-web:v1.0`) → describe Events `Failed to pull image ... not found` → ชั้น image/registry → แก้ tag (และเทียบเคส "ลืม kind load")
  4. เคส C `broken/03-crashloop.yaml` (web `command: ["node","missing.js"]`) → `logs --previous` → `Cannot find module` → ชั้นแอป → แก้ command
  5. เคส D `broken/04-no-endpoints.yaml` (Service selector `app: wep`) → `get endpoints` ว่าง ทั้งที่ Pod Running → `describe svc` เทียบ label → ชั้น networking → แก้ selector
  6. `kubectl get events -n lab020 --sort-by=.lastTimestamp` มองทั้ง namespace ในจอเดียว · ตารางสรุป อาการ → ชั้นที่พัง → คำสั่งที่เปิดเผยสาเหตุ
  7. Exercise ปริศนาที่ 5 (ไม่มีเฉลยตรง ๆ): Service `targetPort: 3001` → endpoints มี แต่ curl ได้ `connection refused`/504 → ต้องไล่เอง
- **ทดลองให้พัง:** แล็บนี้คือชุด "ทดลองให้พัง" 4 อาการ + วิธีแก้กลับทีละเคส (README ต้องมีหัวข้อ "ทดลองให้พัง" ครอบทั้ง 4)
- **คำถาม + แนวคำตอบ:**
  1. แต่ละอาการชี้ไปที่สาเหตุกลุ่มไหน? → Pending = schedule ไม่ได้ (ทรัพยากร/selector/PVC) · ImagePullBackOff = หา image ไม่เจอ/ไม่มีสิทธิ์ · CrashLoopBackOff = แอปเริ่มแล้วตายเอง (ดู logs) · endpoints ว่าง = selector/label/readiness
  2. ควรไล่ดูอะไรตามลำดับ? → `get` (อาการ) → `describe` (เหตุการณ์รอบ Pod) → `logs` (เสียงของแอป, `--previous` ถ้า crash) → `get events` (ภาพรวม namespace)
  3. Running แต่เว็บยังพัง ควรสงสัยอะไร? → Service/Endpoints/Ingress (ชั้นเชื่อมต่อ) หรือ readiness (แล็บ 014)
- **ชิ้นส่วนแอป:** web/api ในสภาพพัง · **ไฟล์:** `broken/01..04.yaml`, `fixed/01..04.yaml` (เฉลย), `exercise/05-mystery.yaml` · **screenshot:** ไม่บังคับ

## 021-the-big-picture
- **แนวคิดหลัก:** ทุกอย่างที่เรียนมาต่อกันเป็นภาพเดียวได้
- **ปัญหาตั้งต้น:** ผู้ใช้กดปุ่ม "สร้างใบแจ้งซ่อม" ในเบราว์เซอร์ — request นั้นเดินผ่านอะไรบ้างกว่าจะถึง PostgreSQL แล้วกลับมา? ถ้าดึงชิ้นใดออก ผู้ใช้จะเห็นอาการอะไร?
- **ขั้นตอน:**
  1. `manifests/` ฉบับสมบูรณ์ (รวมทุกอย่างจาก 015-019: ConfigMap · Secret · PVC · db/api/web Deployment+Service · probes · resources · rolling strategy · Ingress 2 path) → `kubectl apply -f manifests/` → `kubectl get all,ingress,pvc,secret,configmap -n lab021` → **screenshot** หน้าเว็บสมบูรณ์ผ่าน Ingress
  2. เดินตาม request ด้วยหลักฐาน: สร้างใบแจ้งซ่อมจากเบราว์เซอร์ → `kubectl -n ingress-nginx logs deploy/ingress-nginx-controller --tail=3` (ประตู) → `kubectl logs deploy/web --tail=3` (web) → `kubectl logs deploy/api --tail=3` (api: POST /api/tickets 201) → `kubectl exec deploy/db -- psql ... select ... order by id desc limit 1` (db) · `stern -n lab021 . --tail 2` ดูพร้อมกัน
  3. วาดแผนภาพเส้นทาง (ให้ template ในไดอะแกรม `lab021-architecture.svg`) แล้วให้นักศึกษาเติมชื่อ object: Browser → localhost:8080 → ingress-nginx → Ingress rule `/` → Service web → Pod web → (API_BASE_URL จาก ConfigMap) → Service api → Pod api (DB_PASSWORD จาก Secret) → Service db → Pod db → PVC → PV
  4. ตัดทีละชิ้นแล้วดูอาการ (ลูป `curl http://localhost/info` ค้างไว้): `delete svc db` → การ์ด db แดง (api /ready 503 → api ถูกถอดจาก endpoints → web บอก api ไม่พร้อม) · apply คืน · `delete svc api` → api ไม่เชื่อมต่อ · `delete ingress` → 404 · `scale deploy web --replicas=0` → 503 จาก nginx · apply คืนทุกครั้ง
  5. สรุปตารางใหญ่: object ทุกตัว → หน้าที่ → แล็บที่เรียน → อาการเมื่อหาย
  6. ปิดท้าย: สิ่งที่ยังไม่ได้เรียนและควรอ่านต่อ (HPA · StatefulSet · Job/CronJob · RBAC · Helm · Kustomize · GitOps) ชี้ว่าใช้เมื่อไร
- **ทดลองให้พัง:** ข้อ 4 (ตัดทีละชิ้น 4 แบบ) · แต่ละแบบต้องบอก "อาการที่ผู้ใช้เห็น" + "คำสั่งที่เปิดเผยชิ้นที่หาย" + "แก้กลับ"
- **คำถาม + แนวคำตอบ:**
  1. request หนึ่งเดินผ่าน object อะไรบ้างตามลำดับ? → Ingress (rule) → Service web → Pod web → Service api → Pod api → Service db → Pod db → PVC/PV (ค่า config มาจาก ConfigMap/Secret ระหว่างทาง)
  2. ถ้าตัดชิ้นใดออกระบบจะพังตรงไหน? → ตัดชั้นไหน อาการโผล่ที่ "การ์ดสถานะ" ของชั้นนั้น และ readiness จะถอด Pod ที่พึ่งพาชั้นนั้นออกจาก Service
  3. ระบบนี้ยังขาดอะไรก่อนใช้จริง? → TLS, RBAC, backup ของ PV, HPA, monitoring, secret manager — รู้ว่ามีอยู่และไปอ่านต่อได้
- **ชิ้นส่วนแอป:** ครบทุกชิ้น · **ไฟล์:** `manifests/01..11` · **screenshot:** `01-complete-system.png`, `02-ticket-created-trace.png`, `04-db-service-cut.png`

---

# รายการไดอะแกรม (ทีมไดอะแกรมทำ · ชื่อไฟล์ต้องตรงนี้เป๊ะ)

ทุกครั้ง: `lab0NN-architecture.svg` ครบ 7 ไฟล์ของครั้งนั้น (+ `.excalidraw` ใน `scenes/`)
สไตล์: พื้นขาว เส้นเรียบ (roughness 0) ตัวอักษร ≥ 20px สีตามชุดสไลด์ (acc #1c5cab · ok #116b11 · warn #86590a · crit #a32222 · ink #18181b) · ภาษาไทยได้ · กล่อง Pod/Service/Deployment/Ingress/PVC ใช้รูปแบบเดียวกันทุกภาพ

ครั้งที่ 1 (`01_Session1_Kubernetes_Basics/slides_assets/`):
- d01-compose-vs-kubernetes.svg — เครื่องเดียว+compose vs cluster หลาย node+control plane
- d02-cluster-architecture.svg — control plane (API server/scheduler/controller/etcd) vs worker (kubelet/runtime/Pod) + kubectl
- d03-pod-vs-container.svg — Pod = ซองที่มี container ≥1 แชร์ IP/volume
- d04-declarative-loop.svg — desired state (YAML) → API server → controller เทียบ actual → แก้ส่วนต่าง (วงกลม)
- d05-labels-and-selectors.svg — Pod หลายตัวมี label · selector วงจับกลุ่ม
- d06-deployment-rs-pod.svg — 3 ชั้น Deployment → RS(v1) RS(v2) → Pod
- d07-rolling-vs-recreate.svg — ไทม์ไลน์เปลี่ยนเวอร์ชัน
- d08-learning-loop.svg — ทายผล → รัน → สังเกต → อธิบาย → ทำให้พัง → แก้กลับ
- lab001..lab007-architecture.svg

ครั้งที่ 2 (`02_Session2_Networking_Config_Storage/slides_assets/`):
- d01-pod-ip-changes.svg — web ชี้ IP ของ api Pod ที่ตายแล้ว → Service เป็นชื่อคงที่
- d02-service-types.svg — ClusterIP / NodePort / (LoadBalancer) / Ingress ใครเข้าถึงได้
- d03-config-outside-image.svg — image เดียว + ConfigMap/Secret ต่างกัน → 3 deployment
- d04-secret-base64.svg — stringData → base64 → Pod เห็นค่าจริง
- d05-container-fs-vs-volume.svg — image layers + writable layer / emptyDir / PVC→PV
- d06-readiness-vs-liveness.svg — สองคำถาม สองผลลัพธ์ (ถอดจาก Service / restart)
- d07-request-path-web-api-db.svg — เส้นทางภายใน cluster (สำเนาใช้ในครั้งที่ 3 ด้วย)
- d08-learning-loop.svg (สำเนา)
- lab008..lab014-architecture.svg

ครั้งที่ 3 (`03_Session3_Application_Deployment/slides_assets/`):
- d01-compose-to-objects.svg — compose.yaml 3 service → 10 object
- d02-stateless-vs-stateful.svg
- d03-ingress-vs-nodeport.svg — เทียบกับ reverse proxy/Traefik
- d04-rolling-update-timeline.svg — maxSurge/maxUnavailable + readiness
- d05-requests-limits-scheduling.svg — scheduler จอง requests · limits ตอนรัน
- d06-troubleshooting-ladder.svg — get → describe → logs → events + 4 อาการ
- d07-request-path-browser-to-postgres.svg — ภาพใหญ่ปิดชุด (Browser → 8080 → ingress-nginx → … → PV)
- d08-learning-loop.svg (สำเนา)
- lab015..lab021-architecture.svg
