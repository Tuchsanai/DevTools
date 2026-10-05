## Troubleshooting

| อาการ | สาเหตุ | วิธีแก้ |
|---|---|---|
| `ls` ใน k8s-lab ไม่เจอ `labs/` หรือ `som-shop-v2/`, kubectl แจ้ง `the path "labs/..." does not exist` | ยังไม่ได้ `docker cp` หรืออยู่ผิดโฟลเดอร์ | 🖥️ `docker cp 006_kubernetes_service k8s-lab:/workspace/` แล้ว 🐧 `cd /workspace/006_kubernetes_service/02_LAB` (ตรวจด้วย `pwd`) |
| `kubectl get nodes` ต่อคลัสเตอร์ไม่ได้ (connection refused) | ยังไม่มีคลัสเตอร์ หรือ `k8s-lab` เพิ่ง restart | 🐧 `k8s-up` ใหม่ ถ้าจะทำ LAB 10 ต้อง build/`kind load` image ใหม่ (ข้อ 10.2) |
| `Error from server (NotFound): namespaces "shop" not found` | ข้าม LAB 1 หรือเก็บกวาดไปแล้ว | เริ่มใหม่จาก LAB 1 (`kubectl apply -f labs/lab01-before-service/`) แล้วทำ LAB ที่ต้องมีก่อนตามบรรทัด "ต้องมีจาก LAB ..." |
| `provided port is already allocated` ตอน apply NodePort 30080 | Service อื่นจอง 30080 อยู่ (ตัวอย่างของบทที่ 1, `web-nodeport` ของ LAB 8 หรือ `som-web` ที่ยังไม่ลบ) | `kubectl get svc -A \| grep 30080` แล้วลบตัวที่ค้าง (LAB 0 ขั้นที่ 4, LAB 8 ขั้นที่ 7) |
| browser เปิด `http://localhost:30080` ไม่ได้ ทั้งที่ใน k8s-lab `curl -s localhost:30080` ได้ | container `k8s-lab` ไม่ได้ publish พอร์ต 30080 (สร้างไม่ตรงบทที่ 1) หรือโปรแกรมอื่นบนเครื่องใช้พอร์ตนี้ | 🖥️ `docker port k8s-lab` ต้องมีบรรทัดของ `30080/tcp` ถ้าไม่มี ใช้ทางสำรอง 🖥️ `ssh -p 2223 -L 30080:localhost:30080 root@localhost` แล้วเปิด `http://localhost:30080` อีกครั้ง (ถ้าพอร์ตชน เปลี่ยนเลขซ้ายเป็น `-L 13080:localhost:30080` แล้วเปิด `http://localhost:13080`) |
| browser refresh แล้วเห็นชื่อ Pod เดิมตลอด | keep-alive ของ browser (ไม่ใช่ความผิดปกติ) | ดูการกระจายด้วย `curl` วน หรือ `./hit.sh` (LAB 8 ขั้นที่ 4) |
| `ping` ClusterIP ได้ 100% packet loss | ClusterIP เป็น IP เสมือน (ปกติ) | ทดสอบด้วย `wget`/`curl` ไปที่พอร์ตของ Service |
| `nslookup web` มีบรรทัด `** server can't find ... NXDOMAIN` ปน และ exit 1 / `nslookup web.shop` ได้ NXDOMAIN | ข้อจำกัดของ `nslookup` ใน busybox | ใช้ชื่อเต็ม `web.shop.svc.cluster.local` กับ nslookup ส่วนการทดสอบแอปใช้ `wget http://web.shop` |
| `wget: bad address 'web'` | เรียกชื่อสั้นจาก namespace อื่น หรือสะกดผิด | ใช้ `web.shop` หรือชื่อเต็ม ตรวจชื่อด้วย `kubectl get svc -A` |
| `wget: can't connect to remote host (10.96.x.x): Connection refused` | Service ไม่มี endpoint ที่ ready (selector ผิด/Pod ไม่ ready) หรือ targetPort ผิด หรือ Service เพิ่งสร้าง (~1 วินาทีแรก) | ลองซ้ำ 1 ครั้ง แล้วไล่ตาม LAB 7: `get endpointslice -l kubernetes.io/service-name=<svc>`, `describe svc`, `get pods --show-labels` |
| `wget: download timed out` | เรียกพอร์ตที่ Service ไม่ได้ประกาศ, NetworkPolicy กั้น หรือเรียก Pod IP ที่ไม่มีแล้ว | ตรวจ `PORT(S)` ของ Service, `kubectl get netpol -A`, ใช้ชื่อ Service แทน IP |
| ENDPOINTS แสดง IP ครบแต่บางบูธไม่ได้ลูกค้า | บูธนั้น `ready=false` | ดูด้วย jsonpath `conditions.ready` หรือ `describe endpointslice` (LAB 6) |
| ENDPOINTS แสดง `... + 2 more...` | kubectl ตัดการแสดงผลเกิน 3 IP | ใช้ jsonpath `{range .items[0].endpoints[*]}...` |
| `sessionAffinity` ยังเป็น `ClientIP` ทำให้ LAB 6 ยิงไปบูธเดียว | ลืมปิดในท้าย LAB 5 | `kubectl -n shop patch svc web -p '{"spec":{"sessionAffinity":"None"}}'` |
| `client` ใน shop เรียก `web` ได้ `download timed out` หลัง LAB 9 ขั้นที่ 4 | NetworkPolicy เลือก Pod `app=web` แล้วอนุญาตเฉพาะ `kitchen` (ตั้งใจให้เห็น) | ลบ policy `kubectl -n shop delete netpol web-from-kitchen` หรือลบ namespace ตามขั้นที่ 5 |
| `wget http://supplier.shop` ได้ `409 Conflict` / nslookup ExternalName ไม่ได้ A record | Host header ไม่ตรง (ข้อจำกัดของ ExternalName) / เครื่องไม่มีอินเทอร์เน็ต | เป็นผลที่คาดไว้ ดูแค่บรรทัด `canonical name = example.com` |
| `./hit.sh: Permission denied` | สิทธิ์ execute หายระหว่างคัดลอกไฟล์ | `chmod +x hit.sh` หรือรันด้วย `bash hit.sh` |
| `som-web` ค้าง `Init:0/2` นาน, log `wait-for-db` พิมพ์ `รอฐานข้อมูล som-db...` ซ้ำ ๆ | db ยังไม่ Ready หรือ Service `som-db` ไม่มี endpoint | `kubectl -n som-shop get pods,endpointslice` และ `kubectl -n som-shop logs -l app=som-web -c wait-for-db` ตรวจว่า apply `10-db.yaml` แล้ว |
| `som-web` ค้าง `ErrImagePull` / `ImagePullBackOff` (`som-shop-web:1.2`) | ยังไม่ `kind load docker-image` หรือสร้างคลัสเตอร์ใหม่หลัง load | ทำข้อ 10.2 แล้ว `kubectl -n som-shop delete pod -l app=som-web` |
| `kind load docker-image postgres:...` ขึ้น `ctr: content digest sha256:...: not found` | image หลาย platform | ใช้ `docker save --platform linux/amd64 ...` + `kind load image-archive` (ข้อ 10.2) |
| หน้าเว็บ 503 "ร้านกำลังเตรียมสินค้า" ค้าง | db เกิดใหม่และยังว่าง (ตั้งใจให้เห็นในข้อ 10.9) | ลบบูธ web 1 ตัวตามข้อ 10.10 |
| log ของ web มี `db connection lost: terminating connection due to administrator command` | สายเก่าไป db ตัวที่ถูกลบขาด | ปกติ pool ต่อใหม่เองใน request ถัดไป |
| Event `Readiness probe failed: ... connect: connection refused` ตอน Pod เพิ่งเริ่ม / บูธที่ถูกลบขึ้น `Error` ชั่วครู่ | แอปยังไม่เปิดพอร์ต / Next.js ออกด้วย exit code ไม่เป็น 0 ตอนรับ SIGTERM | ปกติ ไม่ต้องแก้ |
| err ของ `hit.sh` ตอนลบบูธมากกว่าในเอกสาร | เครื่องช้ากว่า บูธใหม่ Ready ช้ากว่า | ปกติ บันทึกตัวเลขของตัวเองไว้เทียบกับบทที่ 7 |
| `hit.sh` หรือ `kubectl ... -w` ค้างอยู่ในอีกหน้าต่าง | ยังไม่ได้หยุด | กด Ctrl+C ในหน้าต่างนั้น ถ้าหาไม่เจอใช้ `pkill -f "[h]it.sh"` |

---

## Checklist ส่งงาน

ส่งภาพหน้าจอ (screenshot ของ terminal/browser) ตามรายการ พร้อมคำตอบคำถามชวนคิดอย่างน้อย LAB ละ 1 ข้อ และคำถามท้าย LAB 10 ทั้ง 5 ข้อ

- [ ] **LAB 0** `kubectl get svc -A` (มี `kubernetes`, `kube-dns`), `mode: iptables` และผล `grep -E '3008[0-2]'` ที่ว่าง
- [ ] **LAB 1** `wget` ด้วย Pod IP ได้ก่อนลบ และ `download timed out` หลังลบ พร้อม `get pods -o wide` ที่เห็นชื่อ/IP ใหม่
- [ ] **LAB 2** `get svc,endpointslice` ที่ ENDPOINTS ตรงกับ Pod IP, คำเตือน `v1 Endpoints is deprecated` และ ping ClusterIP 100% packet loss คู่กับ `wget http://web` ที่ได้
- [ ] **LAB 3** `web-alt:8080` ได้ / `web-alt` timed out และ error `spec.ports[1].name: Required value`
- [ ] **LAB 4** `resolv.conf`, `nslookup web.shop.svc.cluster.local` และ env `WEB_*` ของ `client` (ว่าง) เทียบ `client2`
- [ ] **LAB 5** ผลยิง 30 ครั้งแบบ `None` และแบบ `ClientIP` (30/30)
- [ ] **LAB 6** jsonpath ที่มี `ready=false` คู่กับผลยิง 30 ครั้งที่ไม่ไปบูธนั้น
- [ ] **LAB 7** ENDPOINTS `<unset>` ของ `web-typo` และ PORTS `8080` ของ `web-badport` พร้อมผลหลังแก้
- [ ] **LAB 8** browser ที่ `http://localhost:30080` แสดง `web v1 from web-...`, ผล `curl` วน 30 ครั้ง, error ของ 29999 และ 30080 ซ้ำ, `web-lb` ที่ `<pending>`
- [ ] **LAB 9** `bad address 'web'` จาก `kitchen`, nslookup ของ `web-headless` (3 IP) เทียบ `web` (1 IP), `canonical name = example.com` และผล NetworkPolicy port 8080 (timed out) เทียบ port 80 (ได้)
- [ ] **LAB 10** (1) `get rs,svc -n som-shop` (2) log `db-seed` `new: 6/0/0` (3) browser หน้าร้าน 1.2 ที่ `localhost:30080` (4) `./hit.sh` ครบทุกบูธ + `/api/stats` `orders=` เท่ากันทุกบูธ (5) EndpointSlice ของ `som-db` ก่อน/หลังลบ Pod db + ClusterIP เดิม + หน้า 503 (6) ร้านกลับมา `orders=0` (7) Pod ยัง 1.2 หลัง `set image` (8) `hit.sh` ที่เห็น 1.2/1.3 ปน และผล `-q` ตอนลบทีเดียว (ตัวเลข err ของตัวเอง) (9) browser หน้าร้าน 1.3
- [ ] ท้ายสุด `kubectl get ns` เหลือ namespace ตั้งต้น 5 ตัว และ `kubectl get svc -A | grep 3008` ว่าง

---

## ตารางเก็บกวาดและคืนสภาพ

ใช้ตรวจหลังจบแต่ละ LAB หรือเมื่อผลเริ่มเพี้ยน 🐧 ทุกคำสั่งรันใน SSH session ของ k8s-lab

| สิ่งที่อาจค้าง | มาจาก LAB | ตรวจด้วย | คืนสภาพด้วย |
|---|---|---|---|
| ตัวอย่าง `web` ของบทที่ 1 ที่จอง 30080 | ก่อนบทนี้ | `kubectl get svc -A \| grep 30080` | `kubectl delete -f /workspace/examples/web-deployment.yaml` |
| namespace `shop` (ReplicaSet `web`, `client`, `client2`, Service ทั้งหมด, NetworkPolicy) | 1–9 | `kubectl get all,netpol -n shop` | `kubectl delete ns shop` |
| Service `web-quick` | 2 | `kubectl -n shop get svc web-quick` | `kubectl -n shop delete svc web-quick` |
| `sessionAffinity: ClientIP` ของ `web` | 5 | `kubectl -n shop get svc web -o jsonpath='{.spec.sessionAffinity}'` | `kubectl -n shop patch svc web -p '{"spec":{"sessionAffinity":"None"}}'` |
| บูธที่ไม่มี `index.html` (`0/1`) | 6 | `kubectl -n shop get pods` | คืนไฟล์ตามขั้นที่ 4 หรือ `kubectl -n shop delete pod <ชื่อ>` ให้ ReplicaSet สร้างใหม่ |
| Service `web-typo`, `web-badport` | 7 | `kubectl -n shop get svc` | `kubectl delete -f labs/lab07-debug/` |
| Service `web-nodeport` (30080), `web-lb` | 8 | `kubectl get svc -A \| grep -E '30080\|LoadBalancer'` | `kubectl delete -f labs/lab08-nodeport/web-nodeport.yaml -f labs/lab08-nodeport/web-lb.yaml` |
| namespace `kitchen` | 9 | `kubectl get ns kitchen` | `kubectl delete ns kitchen` |
| NetworkPolicy `web-from-kitchen` | 9 | `kubectl get netpol -A` | `kubectl -n shop delete netpol web-from-kitchen` |
| namespace `som-shop` (30080) | 10 | `kubectl get ns som-shop` | `kubectl delete ns som-shop` |
| `hit.sh` ที่ยังยิงอยู่ | 10 | `pgrep -af "[h]it.sh"` | Ctrl+C หรือ `pkill -f "[h]it.sh"` |
| image `som-shop-web:1.2`/`1.3`, postgres บน Node | 10 | `docker exec lab-worker crictl images \| grep -E "som-shop\|postgres"` | **เก็บไว้** ใช้ต่อในบทที่ 7 |

ตอนลบของที่ไม่มีอยู่แล้ว kubectl อาจแจ้ง `NotFound` ซึ่งไม่เป็นไร

---

## เก็บกวาดหลังจบบท

🐧 **ใน SSH session ของ k8s-lab** ตรวจครั้งสุดท้าย

```bash
kubectl get ns
kubectl get svc -A
pgrep -af "[h]it.sh" || echo "ไม่มี hit.sh ค้าง"
```

ผลที่ถูกต้อง: เหลือ namespace ตั้งต้น 5 ตัว (`default`, `kube-node-lease`, `kube-public`, `kube-system`, `local-path-storage`), Service มีแค่ `kubernetes` และ `kube-dns` และไม่มี `hit.sh` ค้าง

คลัสเตอร์ `lab` และ image `som-shop-web:1.2`/`1.3` บน Node **เก็บไว้ใช้ต่อในบทที่ 7 (Deployment)** ซึ่งเริ่มจากปัญหา "เปลี่ยนรุ่นแล้วร้านสะดุด" ของ LAB 10 ถ้าต้องการคืนทรัพยากรเครื่อง ให้ลบคลัสเตอร์ด้วย `k8s-down` (image ที่ `kind load` ไว้จะหายไปด้วย ครั้งหน้าต้อง `k8s-up` และ build/`kind load` ใหม่) แล้วออกจาก SSH ด้วย `exit`

---

> **หมายเหตุเกี่ยวกับภาพประกอบ:** ภาพประกอบ LAB (ยกเว้นภาพในโฟลเดอร์ [`images/screenshots/`](images/screenshots/) ซึ่งเป็นภาพหน้าจอจริงจากการทดลอง) สร้างขึ้นด้วยปัญญาประดิษฐ์สำหรับการสร้างภาพเพื่อใช้ประกอบการเรียนการสอน ชุดคำสั่งสร้างภาพอยู่ใน [`images/imagegen-prompts.md`](images/imagegen-prompts.md) ภาพใช้อุปมาเชิงเปรียบเทียบ ตัวเลขในภาพ (เช่น IP และจำนวน err) เป็นค่าตัวอย่าง ให้ยึดผลลัพธ์คำสั่งในเอกสารและในเครื่องของนักศึกษาเป็นหลัก ภาพหน้าจอจริงถ่ายจาก browser ที่เปิด NodePort 30080 โดยตรง (บนเครื่องนักศึกษาคือ `http://localhost:30080`) ชื่อ Pod, IP และจำนวนออเดอร์ในภาพมาจากการทดลองรอบที่ถ่ายภาพ จึงอาจต่างจากผลคำสั่งในเอกสาร
