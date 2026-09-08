# กติกาสภาพแวดล้อมสำหรับ worker ทุกตัว (parent เขียน · อ่านให้จบก่อนเริ่มงาน)

## 0. หลักการ
- งานทดสอบทุกอย่างทำใน **container ของตัวเอง** จาก image `tuchsanai/devtools-k8s:2569_1`
  ห้ามแตะ container `devtools-k8s` ของผู้ใช้ (มันถือ host port 2299/8080/8443/3000/9090 อยู่)
- ห้ามรัน kind/kubectl บนเครื่อง host โดยตรง · ทุกอย่างรันผ่าน `docker exec` เข้า container ของตัวเอง
- **ต้องลบ container ของตัวเองก่อนส่งงาน** และยืนยันด้วย `docker ps -a --filter name=devtools-k8s-<JOB>` ว่าว่างเปล่า
- ห้ามใส่ email/ชื่อจริง/token/รหัสผ่านจริง ลงเอกสาร screenshot หรือรายงาน — ใช้ placeholder (`<YOUR_NAME>`) เท่านั้น
  (รหัสผ่านของ PostgreSQL ในแล็บเป็นค่าสมมุติ เช่น `labpass` ใช้ได้)

## 1. สร้าง container ของตัวเอง
parent กำหนด `JOB` (ชื่อสั้น ตัวพิมพ์เล็ก) ให้ในคำสั่งงาน

```bash
JOB=<ชื่อ job>                       # เช่น JOB=lab-g1
# path ของ repo "ในมุมมองของ Docker daemon" (เครื่องนี้รัน Claude/Codex อยู่ใน container ที่ mount workspace มาจาก Windows —
# ห้ามใช้ /root/workspace/... เป็น source ของ -v เพราะ daemon จะมองเห็นเป็นโฟลเดอร์ว่าง)
HOSTSRC=$(docker inspect $(hostname) --format '{{range .Mounts}}{{if eq .Destination "/root/workspace"}}{{.Source}}{{end}}{{end}}')/DevTools
docker rm -f devtools-k8s-$JOB 2>/dev/null
docker network inspect k8s-course-net >/dev/null 2>&1 || docker network create --subnet 172.30.0.0/16 k8s-course-net   # network กลาง (มีอยู่แล้ว)
docker run -d --name devtools-k8s-$JOB --privileged --shm-size=1g --ulimit nofile=65536:65536 \
  --network k8s-course-net \
  -v "$HOSTSRC:/root/labwork/DevTools" \
  tuchsanai/devtools-k8s:2569_1
# รอ dockerd ข้างในพร้อม (ปกติ < 30 วินาที)
docker exec devtools-k8s-$JOB bash -lc 'for i in $(seq 1 90); do docker info >/dev/null 2>&1 && exit 0; sleep 2; done; echo dockerd-not-ready; exit 1'
docker exec devtools-k8s-$JOB ls /root/labwork/DevTools/05_kubernetes/app      # ต้องเห็นไฟล์ (ยืนยันว่า mount ถูก)
# สร้าง cluster ด้วยสคริปต์ที่มีอยู่แล้วใน image (2-6 นาที) — ห้ามเขียนสคริปต์สร้าง cluster เอง
docker exec devtools-k8s-$JOB k8s-bootstrap
docker exec devtools-k8s-$JOB kubectl get nodes -o wide
# เข้าถึง container จากฝั่งคุณด้วย "ชื่อ container" บน network กลาง (localhost:port ใช้ไม่ได้ เพราะ port ที่ publish ไปโผล่บน Windows host
# และ IP บน bridge เริ่มต้นถูกกันไว้) — ตัวแปร $IP ในเอกสารนี้จึงเป็นชื่อ container:
IP=devtools-k8s-$JOB
curl -s -m 5 -o /dev/null -w "%{http_code}\n" http://$IP:80/     # ต้องได้ 404 จาก ingress-nginx หลัง bootstrap (ยืนยันว่าเข้าถึงได้)
```

- repo ทั้งก้อนถูก mount ไว้ที่ `/root/labwork/DevTools` ภายใน container (= `~/labwork/DevTools`)
  จึงตรงกับ path ที่นักศึกษาใช้หลัง `git clone https://github.com/Tuchsanai/DevTools.git`
  ไฟล์ที่เขียนใน container จะโผล่บน host ทันที (และกลับกัน)
- โฟลเดอร์ชุดนี้ = `~/labwork/DevTools/05_kubernetes`

## 2. การเข้าถึงหน้าเว็บ (สองทางที่ใช้ทั้งชุด — ห้ามใช้วิธีอื่น)
| ทาง | ใน container ของ worker | ที่นักศึกษาเห็นในเอกสาร | จากฝั่ง host ของ worker (curl/screenshot) |
|---|---|---|---|
| Ingress (ingress-nginx, kind map 80) | `curl localhost:80/` | `http://localhost:8080` | `http://$IP:80` |
| port-forward | `kubectl port-forward svc/web 3000:3000 --address 0.0.0.0` | `http://localhost:3000` | `http://$IP:3000` |

- **ในเอกสาร: เบราว์เซอร์ = localhost:8080 / localhost:3000 · คำสั่ง curl ในเทอร์มินัลของเครื่องเรียน = `http://localhost/…` (port 80) เพราะ 8080 มีเฉพาะฝั่งเครื่องหลัก** (สภาพแวดล้อมของนักศึกษาที่รัน `docker run ... -p 8080:80 -p 3000:3000`) — `$IP` ใช้ทดสอบของ worker เท่านั้น ห้ามโผล่ในเอกสาร
- port-forward ต้องใส่ `--address 0.0.0.0` ไม่งั้นออกนอก container ไม่ได้ · รันเป็น background (`&`) และ `kill` ทิ้งเมื่อจบขั้นตอน
- Ingress ในชุดนี้ **ไม่ใส่ `host:`** (path-only) เพื่อให้ `http://localhost:8080` เปิดได้ตรง ๆ โดยไม่ต้องตั้ง Host header

## 3. image ของแอปตัวอย่าง
```bash
docker exec devtools-k8s-$JOB bash -lc 'cd ~/labwork/DevTools/05_kubernetes/app && ./build-images.sh'   # build ใน dockerd ของ container
docker exec devtools-k8s-$JOB kind load docker-image k8s-lab-web:v1 k8s-lab-web:v2 k8s-lab-api:v1 k8s-lab-db:v1 --name devtools
```
ถ้าไม่ load เข้า kind จะเจอ `ErrImagePull` / `ImagePullBackOff` (ใช้เป็นบทเรียน "ทดลองให้พัง" ได้)
ทุก manifest ที่ใช้ image เหล่านี้ต้องมี `imagePullPolicy: IfNotPresent` (ไม่งั้น kubelet จะพยายาม pull tag จาก registry)

## 4. screenshot จากหน้าเว็บที่รันจริง (Playwright บน host)
```bash
node /root/workspace/DevTools/05_kubernetes/.work/tools/shot.js "http://$IP:80/" <โฟลเดอร์แล็บ>/images/<ชื่อสื่อความหมาย>.png --w 1280 --h 800
#   --full            เก็บทั้งหน้า
#   --reload 3        reload ก่อนถ่าย (ให้ตกที่ Pod อื่น)
#   --selector "css"  ถ่ายเฉพาะ element
#   --wait 2000       รอเพิ่มก่อนถ่าย (ms)
```
- Playwright ใน `/opt/venv` ของ host ใช้ไม่ได้ (browser version ไม่ตรง) — ใช้ `shot.js` นี้เท่านั้น (หรือ MCP `playwright` ถ้ามี)
- ภาพต้องมาจากขั้นตอนที่นักศึกษาทำจริง ณ ขั้นนั้น ห้ามใช้ภาพจำลอง ห้ามตัดต่อ
- ตั้งชื่อไฟล์บอกขั้นตอน เช่น `03-pod-page-first-open.png`, `06-rollout-mixed-v1-v2.png`

## 5. วินัย cluster
- ทุกแล็บใช้ namespace ของตัวเอง `labNNN` (เช่น `lab003`) · จบแล็บ `kubectl delete ns labNNN` และรอจนหายจริง
- ห้ามทิ้ง resource ไว้ให้แล็บถัดไปชน · ห้ามทิ้ง port-forward ค้าง
- ค่าที่ไม่คงที่ (ชื่อ Pod, IP, เวลา, AGE, hash ของ ReplicaSet) ให้เขียนกำกับใน README ว่า "ค่าเหล่านี้ต่างกันได้"

## 6. ก่อนส่งงาน
```bash
docker rm -f devtools-k8s-$JOB
docker ps -a --filter name=devtools-k8s-$JOB      # ต้องว่าง
```
รายงานผลกลับเป็นข้อความ (parent อ่านจาก -o ของคุณ) — **ห้ามสร้างไฟล์สรุปผลเพิ่มเอง** นอกจากไฟล์ที่งานสั่งให้สร้าง
รายงานตรง ๆ ว่าอะไรผ่าน อะไรไม่ผ่าน ห้ามอ้างผลที่ยังไม่เคยเห็นด้วยตา
