# SUMMARY — ทดสอบ LAB บท 006 Service (รันจริง 5 ต.ค. 2569)

- container ทดลอง `k8s-lab-svc006lab-06b9a8` (image `tuchsanai/devtools-kind:2569_1`, ID `8108a1bc7901`, `--privileged --hostname k8s-lab`, SSH `2224→22`, NodePort `30090-30092→30080-30082`) — **ยังเปิดอยู่** ตามคำสั่ง (ดู `handoff.md`) ไม่ได้แตะ `k8s-lab` ของผู้เรียน / `deep_vision_5090_vllm`
- `k8s-up` 48 วิ; kubectl v1.37.1 / server v1.37.0; `docker cp 006_kubernetes_service` → `/workspace/` แล้วรันทุกคำสั่งจาก `02_LAB` (ไฟล์ใน container = repo, ตรวจ md5 ครบ 44 ไฟล์)
- log คำสั่ง+output จริง: `lab00.log` … `lab09.log`, `lab10.log` (รอบสุดท้าย), `lab10-attempt1.log` / `lab10-attempt2.log` (รอบก่อนแก้แอป — เก็บไว้เป็นหลักฐาน/ตัวเลขซ้ำ), `handoff-commands.log` (บรรทัด `### hh:mm:ss` = เวลา UTC ของเครื่อง agent; `date` ในคำสั่ง = เวลาไทย)
- ทดสอบจาก "เครื่องนักศึกษา" ด้วย host ของ agent: `http://172.18.0.1:30090` (gateway → container 30080 → kind extraPortMappings → lab-control-plane:30080) ทั้ง curl และ Playwright Chromium
- ไม่มี Deployment / `kubectl rollout` ในขั้นตอน LAB (ยกเว้นตัวอย่างบท 001 ที่ใช้จำลองของค้างใน LAB 0 แล้วลบทิ้ง)

## ไฟล์ที่สร้าง (`006_kubernetes_service/02_LAB/`)

- `labs/lab01-before-service/{00-ns,web-rs,client-pod}.yaml`, `lab02-clusterip/web-svc.yaml`, `lab03-ports/{web-alt-svc,web-multi-svc,web-multi-noname}.yaml`, `lab04-dns/client2-pod.yaml`, `lab07-debug/{web-typo-svc,web-badport-svc}.yaml`, `lab08-nodeport/{web-nodeport,web-dup-nodeport,web-lb}.yaml`, `lab09-cross-ns/{kitchen,web-headless,supplier-externalname,np-kitchen-8080,np-kitchen-80}.yaml` (18 ไฟล์)
- `som-shop-v2/k8s/{00-namespace,10-db,20-web}.yaml`, `som-shop-v2/hit.sh`, `som-shop-v2/app/` (สำเนาจาก `005_kubernetes_replicaset/02_LAB/som-booths/app` ไม่รวม node_modules/.next แล้วแก้เป็น 1.2/1.3 — 22 ไฟล์ เพิ่มใหม่ `proxy.ts`, `lib/shop.ts`, `app/api/{whoami,live,stats}/route.ts`)
- ยังไม่มี `02_LAB/README.md` (นอกขอบเขตงานนี้)

## ผลรายข้อ

| LAB | ผล | เวลาจริง (agent) | ผลจริงสำคัญ |
|---|---|---|---|
| 0 | ✅ | <1 นาที | 3 Node Ready; จำลองของค้าง `kubectl apply -f /workspace/examples/web-deployment.yaml` → `grep 3008` เห็น `default web NodePort 10.96.10.17 <none> 80:30080/TCP` → `kubectl delete -f /workspace/examples/web-deployment.yaml` (`deployment.apps "web" deleted from default namespace` / `service "web" deleted from default namespace`) → ว่าง; `kubernetes ClusterIP 10.96.0.1 443/TCP`, `kube-dns ClusterIP 10.96.0.10 53/UDP,53/TCP,9153/TCP`; `mode: iptables`; ds kube-proxy `3 3 3`; `docker exec lab-control-plane cat /kind/kubeadm.conf \| grep -i serviceSubnet` → `serviceSubnet: 10.96.0.0/16` ✅ ใช้ได้; `docker ps` ใน k8s-lab เห็น `lab-control-plane 0.0.0.0:30080-30082->30080-30082/tcp` |
| 1 | ✅ | <1 นาที | RS 3/3 ใน ~13 วิ (pull nginx); wget Pod IP → `web v1 from web-9gngn`; ลบ → `pod "web-9gngn" deleted from shop namespace`; wget IP เดิม `-T 3` → **`wget: download timed out`** (exit 1); ตัวใหม่ `web-k2nk5` IP `10.244.2.6` |
| 2 | ✅ | ~1 นาที | `expose rs web` คัดลอก selector `app: web` + label แต่ **`targetPort: 80` (เลข ไม่ใช่ชื่อ http)**; `web ClusterIP 10.96.55.132 80/TCP`, EndpointSlice `web-5r58w IPv4 80 10.244.2.5,10.244.1.4,10.244.2.6`; ownerReferences → `kind: Service, name: web, controller: true`; `get endpoints` → `Warning: v1 Endpoints is deprecated in v1.33+; use discovery.k8s.io/v1 EndpointSlice`; ping ClusterIP `2 packets transmitted, 0 packets received, 100% packet loss` (ping Pod IP ได้); scale 5 → ENDPOINTS แสดง **`10.244.2.5,10.244.1.4,10.244.2.6 + 2 more...`** (ตัดที่ 3); ลบ Pod → IP ใหม่แทน ClusterIP เดิม |
| 3 | ✅ (แก้ไฟล์ 1 จุด) | ~1 นาที | `web-alt:8080` → หน้าเว็บ; `web-alt` (พอร์ต 80) → **`wget: download timed out`** ใช้ 3.06 วิ (ไม่มีกฎ = timeout ไม่ใช่ refused); multi-port `80/TCP,8080/TCP`, EndpointSlice PORTS **`80,80`** (port alt+http ชี้ 80 ทั้งคู่); **ครั้งแรกหลังสร้าง ~1 วิ ได้ `Connection refused`** (kube-proxy ยังไม่ sync) ครั้งถัดไปได้ปกติ; noname (พอร์ตแรกมีชื่อ) → `The Service "web-noname" is invalid: spec.ports[1].name: Required value` (ถ้าไม่มีชื่อทั้งสองพอร์ต → `* spec.ports[0].name: Required value` `* spec.ports[1].name: Required value`) |
| 4 | ✅ (มีข้อควรระวัง) | <1 นาที | `nslookup web` **พิมพ์ `** server can't find web.cluster.local: NXDOMAIN` / `web.svc.cluster.local: NXDOMAIN` ปนกับ `Name: web.shop.svc.cluster.local Address: 10.96.55.132` และ exit 1**; ชื่อเต็มสะอาด; **`nslookup web.shop` → NXDOMAIN** (busybox nslookup ไม่ใช้ search กับชื่อที่มีจุด) แต่ `wget http://web.shop` ได้; resolv.conf `search shop.svc.cluster.local svc.cluster.local cluster.local` / `nameserver 10.96.0.10` / `options ndots:5`; client เก่า `env \| grep WEB_` ว่าง (exit 1) มีแค่ `KUBERNETES_SERVICE_HOST=10.96.0.1`; client2 มี `WEB_SERVICE_HOST=10.96.55.132`, `WEB_SERVICE_PORT=80`, `WEB_ALT_SERVICE_PORT=8080`, `WEB_MULTI_SERVICE_PORT_HTTP=80`, `WEB_MULTI_SERVICE_PORT_ALT=8080` (**`WEB_SERVICE_PORT_HTTP` ไม่มี** เพราะพอร์ตของ Service web ไม่มีชื่อ); Pod web ที่เกิดหลัง Service มี `WEB_SERVICE_HOST` |
| 5 | ✅ | <1 นาที | 30 ครั้ง: `4/14/12`, `8/9/13`; ClientIP → `30 web-k2nk5` (client) และ `30 web-mgz49` (client2 คนละตัว); `sessionAffinityConfig` = `{"clientIP":{"timeoutSeconds":10800}}`; patch กลับ `None` → `sessionAffinityConfig` **หายไป**; หลังกลับ `9/11/10`; `seq` มีใน busybox 1.36 |
| 6 | ✅ | ~1 นาที | ลบ index.html → **ready=false หลัง 7 วิ** (09:00:35 → 09:00:42) Pod `0/1 Running`; ENDPOINTS ยังแสดง 3 IP, jsonpath `10.244.1.5 web-gsgss ready=false`; 30 ครั้ง → `19 web-k2nk5`, `11 web-mgz49` (0 ไปตัวที่ไม่พร้อม); Event `Warning Unhealthy ... spec.containers{nginx}: Readiness probe failed: HTTP probe failed with statuscode: 403`; `describe endpointslice` แสดง `Conditions: Ready: false`; คืนไฟล์ → Ready ใน ~1 วิ |
| 7 | ✅ | ~1 นาที | typo: `wget: can't connect to remote host (10.96.237.174): Connection refused`, `web-typo-rsdpj IPv4 <unset> <unset>`, describe `Selector: app=wbe` / `Endpoints:` ว่าง; patch selector → 3 IP + หน้าเว็บ; badport: **`Connection refused` ทันที (0.06 วิ)**, PORTS `8080`, `Endpoints: 10.244.1.5:8080,...`; patch targetPort http → ได้; `wget: bad address 'wbe'` |
| 8 | ✅ | ~1.5 นาที | `web-nodeport NodePort 10.96.39.125 80:30080/TCP`; ใน k8s-lab `curl localhost:30080` ได้; ทั้ง 3 Node IP:30080 ตอบ; curl 30 ครั้ง `12/9/9`; **จาก host (เท่า localhost:30080 ของนักศึกษา) 30 ครั้ง `7/8/15`**; curl หลาย URL ใน connection เดียว 10/10 Pod เดียว (`Re-using existing connection`); **Chromium: reload 10/10 Pod เดียว, fetch 10/10 Pod เดียว, context ใหม่ (≈Incognito) 5 ครั้ง → 2 ชื่อ (3+2)**; `nodePort: Invalid value: 29999: provided port is not in the valid range. The range of valid ports is 30000-32767`; `The Service "web-dup" is invalid: spec.ports[0].nodePort: Invalid value: 30080: provided port is already allocated`; LB `web-lb LoadBalancer 10.96.28.238 <pending> 80:31841/TCP`; ลบ web-nodeport → curl จาก host **ยังได้ 1 ครั้งใน ~1 วิแรก** แล้ว `curl: (7) Failed to connect ... Couldn't connect to server`; ใน k8s-lab `curl: (56) Recv failure: Connection reset by peer` |
| 9 | ✅ | ~1 นาที | ไม่มี NetworkPolicy ค้าง; `wget: bad address 'web'`; `web.shop` / ชื่อเต็มได้; resolv.conf ของ kitchen `search kitchen.svc.cluster.local ...`; headless `web-headless.shop.svc.cluster.local` คืน 3 Pod IP, `web.shop.svc.cluster.local` คืน `10.96.55.132`; **`nslookup web-headless.shop` → NXDOMAIN** (ต้องชื่อเต็ม); ExternalName `supplier.shop.svc.cluster.local canonical name = example.com` + A/AAAA (เครื่องทดสอบมีเน็ต); `get svc` `supplier ExternalName <none> example.com <none>`, `web-headless ClusterIP None`; policy 8080 → `wget: download timed out`; **policy ทำให้ `client` ใน ns shop ถูกกั้นด้วย** (`download timed out`) เพราะ Pod web ถูก isolate แล้ว; policy 80 → `web-alt.shop:8080` และ `web.shop` ได้; `wget http://supplier.shop` → **`wget: server returned error: HTTP/1.1 409 Conflict`** (Host header ไม่ตรง — ตัวอย่างข้อควรระวัง ExternalName จริง); `kubectl delete ns shop kitchen` 10.7 วิ |
| 10 | ✅ (แก้แอป 2 จุด) | ~8 นาที (รอบสุดท้าย) | ดูหัวข้อถัดไป |

## LAB 10 — ผลตาม "จุดที่ต้องยืนยัน" (แผน 3.7) — ตัวเลขจากรอบสุดท้าย (`lab10.log`) + รอบก่อน

0. build 1.2 **27.6–28.0 วิ** (ไม่มี cache), 1.3 **0.9 วิ** (cache ทั้งหมด ต่างแค่ ENV); `kind load docker-image som-shop-web:1.2 som-shop-web:1.3` 4.4–5.5 วิ (3 Node × 2 image); postgres `docker pull` + `save --platform linux/amd64` + `kind load image-archive` 6–17 วิ; db Ready 3.7–4.3 วิ; web 3 ตัว Ready **~4 วิ** (`Init:0/2 → Init:1/2 → PodInitializing → Running 0/1 → 1/1`)
1. **NodePort จาก host**: ✅ host `:30090` → หน้าร้าน HTTP 200 และ `/api/*` ได้ (Playwright เห็นหน้าเต็ม ป้าย/ธีมถูก) — ยืนยันกลไกเดียวกับ `localhost:30080` ของนักศึกษา; **ยังยืนยันบน Windows + Docker Desktop จริงไม่ได้** (ไม่มีเครื่องนั้นในงานนี้) ทางสำรองในแผน (`ssh -L 30080:localhost:30080`) ยังควรเขียนไว้
2. **keep-alive**: ✅ Chromium reload 10/10 + fetch 10/10 Pod เดียว (ทั้งร้าน nginx และ som-shop 9/9 reload `som-web-jhdzd`); context ใหม่เปลี่ยนได้แบบสุ่ม; Chrome/Edge บน Windows ไม่ได้ทดสอบ
3. **seed + advisory lock**: ✅ ทุกรอบ (5 รอบ รวมแบบ apply ทั้งโฟลเดอร์ที่ seed เริ่มพร้อมกันใน 1 วิ) log `connected to database` / `got seed lock 5005` / `tables ready: products, orders` / `seeded 6 products (new: 6)` หนึ่งตัว, `(new: 0)` สองตัว, INIT_RESTARTS `0,0` ทุกตัว
4. **หน้า 503**: ✅ หลังลบ db: `curl -w %{http_code}` → `503` ×6, `/api/health` → `{"ok":true,"db":"up"}` (Pod ยัง 1/1 Ready), `/api/stats` → `som-web-xxx 1.2 db-not-ready`; browser: `ร้านกำลังเตรียมสินค้า กรุณารอสักครู่ 🐱` / `ฐานข้อมูลยังไม่มีสินค้า (HTTP 503) · หน้านี้จะลองใหม่เองทุก 5 วินาที` / `เสิร์ฟโดย Pod: som-web-zr5pd · เวอร์ชัน 1.2`; psql → `ERROR:  relation "orders" does not exist`
5. **web ต่อ db ใหม่เอง**: ✅ ไม่มี restart; db ใหม่ Ready **4.5–4.7 วิ** หลังสั่งลบ (IP `10.244.2.21 → 10.244.2.26`, ClusterIP `10.96.93.105` เดิม, EndpointSlice ชื่อเดิม `som-db-v78pk` IP ใหม่); log web: `db connection lost: terminating connection due to administrator command (จะต่อใหม่เองใน request ถัดไป)` (ก่อนแก้เป็น `⨯ uncaughtException: error: terminating connection due to administrator command` — ดูการเปลี่ยนแปลงข้อ 2)
6. **เติมสินค้าด้วยการลบ Pod web 1 ตัว**: ✅ Pod ใหม่ Ready 3.6 วิ, seed `new: 6`; ทุก Pod กลับ `200` ทันที `/api/stats` `orders=0 products=6` ทั้ง 3 Pod
7. **hit.sh กระจาย**: ✅ 60 ครั้ง `25/17/18`, `12/21/27`, `26/20/14` ok=60 err=0 (6.5 วิ); 5 Pod `20/8/9/12/11` ok=60 err=0
8. **err ตอนลบ Pod**
   - ลบ web 1 ตัวระหว่าง `hit.sh -q ... 100` (5 Pod): **err 1, 0, 1, 0, 0** (5 ครั้ง) ข้อความ `curl: (56) Recv failure: Connection reset by peer`
   - ลบทีละตัวหลัง set image (`hit.sh ... 200`, 3 Pod): **err 1 และ 0** (2 รอบ) เห็น `1.2` + `1.3` ปน เช่น `6 som-web-lm7jj 1.2 / 58 som-web-mtvzf 1.3 / 62 / 74 (1.2)`
   - **ลบทีเดียว `delete pod -l app=som-web`** (`hit.sh -q ... 200`): **err 5, 7, 4, 4** (4 รอบ) ช่วงมี err **2.3–4.3 วิ**; ข้อความ **`Connection reset by peer` (2–6 ครั้ง) + `Operation timed out` (1–2 ครั้ง)** — **ไม่เจอ `Connection refused`** (ช่วง EndpointSlice ว่าง `<unset> <unset>` สั้นมาก เห็นใน `get endpointslice -w` แค่ 1 บรรทัด) เพราะ Pod ใหม่ Ready ใน ~3 วิบนเครื่องทดสอบ (32 CPU) — เครื่องนักศึกษาที่ช้ากว่าน่าจะ err มากกว่า
9. **`set image` กับ initContainer**: ✅ `kubectl -n som-shop set image rs/som-web web=som-shop-web:1.3 db-seed=som-shop-web:1.3` → `replicaset.apps/som-web image updated`; template `som-shop-web:1.3 som-shop-web:1.3`; `get rs -o wide` IMAGES `som-shop-web:1.3`; Pod ทั้ง 3 ยัง `som-shop-web:1.2` และ hit.sh ยัง 1.2
10. **resource**: ✅ 5 web + 1 db ไม่มี Pending; requests lab-worker 400m/690Mi, lab-worker2 400m/626Mi (เครื่อง 32 CPU/62GB); **ไม่มี PSA warning** ตอน apply
11. **Pod Next.js ถูกลบขึ้น `Error`**: ✅ `get pods -w` เห็น `som-web-rtkdj 0/1 Error 0 61s` ชั่วครู่ก่อนหาย
12. **env**: ✅ `SOM_DB_SERVICE_HOST=10.96.93.105`, `SOM_DB_SERVICE_PORT=5432`; `node -e dns.lookup('som-db')` → ClusterIP เดียวกับ `get svc som-db`

อื่น ๆ: POST orders 3 ครั้ง → `{"ok":true,"order_id":1,...,"stock":18}` … `stock":14}` และ psql `count = 3`; browser กดปุ่ม 🛒 → `สั่งซื้อแล้ว! ออเดอร์ #4` ตัวเลข 3→4; 1.3: แบนเนอร์ `🎉 เมนูใหม่: ขนมปลาทูน่าอบกรอบ 🐟` + ธีมส้ม-ชมพู + `เวอร์ชัน 1.3`; ลบ ns som-shop 10.9–11.2 วิ แล้ว 30080 ว่าง; image 1.2/1.3 ยังอยู่บน Node; Event `Readiness probe failed: ... connect: connection refused` ตอน Pod เพิ่งเริ่ม (ปกติ ก่อน Next.js เปิดพอร์ต)

## การเปลี่ยนแปลงจากแผน

1. **แอปคัดลอกจาก `005_kubernetes_replicaset/02_LAB/som-booths/app`** (ตามคำสั่ง แทน 004 ในแผน — โค้ดเดียวกัน) ไปไว้ที่ `som-shop-v2/app/`
2. **`lib/db.ts` เพิ่ม `pool.on('error', ...)`** — ไม่มีแล้วตอนลบ Pod db ทุก Pod web log `⨯ uncaughtException: error: terminating connection due to administrator command` + stack ยาว (Next.js กันไว้ ไม่ crash แต่ log น่ากลัวและเสี่ยง) → หลังแก้ log บรรทัดเดียวเป็นมิตร (รัน LAB 10 ใหม่ทั้งหมดหลังแก้)
3. **เพิ่ม `GET /api/stats`** (`som-web-xxxxx 1.2 orders=3 products=6`, db ไม่พร้อม → 503 `db-not-ready`) — คำสั่งในแผนข้อ 6 `curl -s localhost:30080 | grep -o 'เสิร์ฟโดย Pod[^<]*'` ไปจับ RSC payload ของ Next.js ด้วย ได้ output ยาวหลายพันตัวอักษร (ดู `lab10-attempt1.log`) → ใช้ `for i in $(seq 12); do curl -s localhost:30080/api/stats; done | sort | uniq -c` แทน
4. **หน้า 503 ทำผ่าน `proxy.ts`** (Next.js 16 middleware, matcher `/`, ตรวจ `SELECT 1 FROM products`) เพราะ App Router page ตั้ง status 503 เองไม่ได้; page.tsx มี fallback ข้อความเดียวกัน (status 200) กรณี db หายระหว่างโหลด; build แสดง `ƒ Proxy (Middleware)`
5. แถบชื่อ Pod เป็นข้อความก้อนเดียว `🐱 เสิร์ฟโดย Pod: <pod> · เวอร์ชัน <v>` (ไม่ใช้ `<code>` แยก) ให้ grep/อ่านง่าย; footer เดิมยังมี `<code>` ชื่อ Pod
6. `web-multi-noname.yaml`: ให้พอร์ตแรกมีชื่อ `http` ไม่ตั้งเฉพาะพอร์ตที่ 2 → error บรรทัดเดียว `spec.ports[1].name: Required value` ตรงภาพ L05 (เดิมไม่มีชื่อทั้งคู่ได้ 2 บรรทัด)
7. `hit.sh` นอกจาก `ok=… err=…` พิมพ์ "ข้อความ error" (`sort | uniq -c` ของข้อความ curl) + "ช่วงที่มี err: x.x วินาที" + เวลาที่ใช้ — ใช้ `curl -sS -f -m 2` (HTTP 5xx นับเป็น err)
8. README ต้องใช้ **ชื่อเต็มกับ `nslookup` ของ busybox** (`web.shop.svc.cluster.local`, `web-headless.shop.svc.cluster.local`, `supplier.shop.svc.cluster.local`) — `nslookup web-headless.shop` / `web.shop` ได้ NXDOMAIN; `nslookup web` ได้แต่มีบรรทัด NXDOMAIN ปนและ exit 1
9. LAB 0: ตัวอย่างบท 001 ลบด้วย `kubectl delete -f /workspace/examples/web-deployment.yaml` (มีทั้ง Deployment+Service `web` ใน default); serviceSubnet ดูได้จาก `/kind/kubeadm.conf` ตามแผน
10. LAB 2: ENDPOINTS ตัดที่ 3 IP (`+ 2 more...`) แม้ `-o wide` → ตอน scale 5 ให้ดูด้วย jsonpath (`{range .items[0].endpoints[*]}...`)
11. LAB 8 (handoff): ฉาก LAB 8 เปิดค้างไว้ที่ nodePort 30081 (sed แก้ตอน apply) เพราะ 30080 ร้านใช้อยู่
12. postgres: ใส่ `docker pull -q postgres:17.11-alpine` ก่อน `docker save --platform linux/amd64` (เครื่องใหม่ยังไม่มี image ให้ save — ไม่ได้ทดสอบกรณีไม่ pull) แล้ว `kind load image-archive ../pg.tar` และลบ tar (ทดสอบผ่าน 3 รอบ)

## ป้าย/ข้อความในภาพ storyboard (`images.json`) เทียบผลจริง

| ภาพ | ตอนนี้ | ผลจริง / ควรใช้แทน |
|---|---|---|
| **T15** (needs_test) | `nodePort: 29999` + `The range of valid ports is 30000-32767`; `nodePort: 30080` + `provided port is already allocated` | ✅ ตรงทั้งคู่ — ไม่ต้องแก้ (ข้อความเต็ม: `spec.ports[0].nodePort: Invalid value: 30080: provided port is already allocated`) |
| **T31** (needs_test) | `targetPort: 8080` / `containerPort: 80` / `Connection refused` | ✅ ตรง (`wget: can't connect to remote host (10.96.234.49): Connection refused` ทันที) |
| **L05** (needs_test) | `ports[1].name: Required value` | ✅ ตรงหลังแก้ไฟล์ (การเปลี่ยนแปลงข้อ 6); caption "ไม่ใส่ชื่อ → apply ไม่ผ่าน" ✅ |
| **L10** (needs_test) | `localhost:30080`, เข้าจาก browser ได้เลย | ✅ กลไกผ่าน (host port → extraPortMappings) ยืนยันบน Windows จริงไม่ได้ — ภาพใช้ได้ |
| **L11** (needs_test) | browser `Pod เดิมทุกครั้ง`, `curl ×30` `หลาย Pod`, `EXTERNAL-IP <pending>` | ✅ ตรง (Chromium 10/10, curl 7/8/15, `<pending>` `80:31841/TCP`) |
| **L13** (needs_test) | `web-headless` ได้ 3 Pod IP / `web` ได้ 1 ClusterIP / `supplier → example.com`; caption "nslookup web-headless" | ป้ายตรง; **caption แก้เป็น "nslookup web-headless.shop.svc.cluster.local"** (ชื่อสั้นแบบมีจุดใน busybox ได้ NXDOMAIN); เพิ่มได้ว่า wget ExternalName ได้ `409 Conflict` (Host header) |
| **L14** (needs_test) | `port: 8080` → `download timed out`, `port: 80` → ผ่าน, `web-alt:8080` | ✅ ตรงเป๊ะ; caption ควรเติม "policy นี้ทำให้ Pod อื่นนอก kitchen (client ใน shop) เข้า web ไม่ได้ด้วย" |
| **L18** (needs_test) | `เพิ่มใหม่ 6` / `0` / `0`, advisory lock | ✅ ตรง (`new: 6/0/0`, init restart 0) |
| **L19** (needs_test) | `เวอร์ชัน 1.2`, `เสิร์ฟโดย Pod: som-web-4nhz6` | ✅ รูปแบบตรง (จริง `🐱 เสิร์ฟโดย Pod: som-web-6h94x · เวอร์ชัน 1.2`; ชื่อ Pod ตัวอย่างใช้ได้) |
| **L20** (needs_test) | `ok=60 err=0`, `ออเดอร์ 3`, 3 ชื่อ Pod | ✅ ตรง (ok=60 err=0 ทุกรอบ, orders=3 ทุก Pod) |
| **L22** (needs_test) | `10.244.1.9 → 10.244.2.14`, `503`, `ออเดอร์ 3 → 0` | ใช้ได้ (ค่าตัวอย่าง); ค่าจริงรอบสุดท้าย **`10.244.2.21 → 10.244.2.26`** (Pod db ใหม่มักอยู่ Node เดิม) และ `ออเดอร์ 4 → 0` (รอบนั้นสั่งเพิ่มจาก browser; ถ้าทำตาม README 3 ออเดอร์ = `3 → 0` ✅); `503` ✅ |
| **L23** (needs_test) | Scene "all booths gone at once, an empty lighthouse clipboard ... customers bumping into a closed gangway door with red X"; ป้าย `err` | ✅ ใช้ได้; ตัวเลขจริงสำหรับ README/บท 007: ทีละตัว err 0–1 / ทีเดียว **err 4–7 ใน 2.3–4.3 วิ** ข้อความ `Connection reset by peer` + `Operation timed out` (ไม่ใช่ `Connection refused` ตามแผนคาด) |
| T24 (pre-check) | `ยิง 9 ครั้ง` `5/4/0` | ✅ ค่าจาก pre-check; ใน LAB จริง 30 ครั้งได้ 4/14/12, 8/9/13 (ไม่ต้องแก้) |
| T25 | `10/10 Pod เดียว` | ✅ ยืนยันซ้ำ (reload 10/10, fetch 10/10) |
| T27 / L08 | `ready=false`, `0/1` | ✅ (เกิดหลังลบ index.html ~7 วิ, statuscode 403) |
| T30 / L09 | `ENDPOINTS <unset>`, `Connection refused` | ✅ ตรง (จริง PORTS ก็ `<unset>` ด้วย) |
| T10 / L01 | `10.96.0.0/16`, `kubernetes 10.96.0.1`, `kube-dns 10.96.0.10`, `mode: iptables` | ✅ ตรงเป๊ะ |
| T16 | `80:30456/TCP` | ค่าตัวอย่าง (จริงสุ่มได้ `80:31841/TCP`) ไม่ต้องแก้ |
| T20 | resolv.conf 3 บรรทัด | ✅ ตรงเป๊ะ (ns shop) |
| L03 | `kubectl expose rs web --port=80` | ✅ (ในคำสั่งจริงต้องมี `-n shop`); ข้อสังเกต: expose ได้ `targetPort: 80` (เลข) ต่างจาก YAML ที่ใช้ `http` |
| L06 | `nslookup web` → `web.shop.svc.cluster.local` / `10.96.47.123` | ป้ายใช้ได้ แต่ README ต้องเตือนว่าผลจริงมีบรรทัด `** server can't find web.cluster.local: NXDOMAIN` ปนและ exit 1 (หรือให้ใช้ชื่อเต็ม) |
| L07 | `30/30` ClientIP | ✅ |
| L12 | `web` (bad address), `web.shop`, ชื่อเต็ม | ✅ (`wget: bad address 'web'`) |
| L21 | `5/5`, ร้านยังขาย | ✅ (ลบ 1 ตัว err 0–1) |
| L16 | build 1.2/1.3 จากโค้ดเดียว | ✅ (1.2 ~28 วิ, 1.3 <1 วิ) |
| T22, T04, T07, L02 IP ตัวอย่าง | `10.96.47.123`, `10.244.2.8`, … | ค่าตัวอย่าง ใช้ได้ |

## ข้อควรระวังสำหรับนักศึกษา (ใส่ README)

- Service ใหม่/พอร์ตใหม่อาจตอบ `Connection refused` ใน ~1 วิแรก (kube-proxy ยังเขียนกฎไม่เสร็จ) ลองใหม่อีกครั้ง; ลบ NodePort แล้วก็ยังตอบได้ ~1 วิ
- `nslookup` ของ busybox: ใช้ชื่อเต็ม `<svc>.<ns>.svc.cluster.local`; ชื่อสั้นมีบรรทัด NXDOMAIN ปน + exit 1, ชื่อที่มีจุด (`web.shop`) ได้ NXDOMAIN ทั้งที่ `wget http://web.shop` ใช้ได้
- `kubectl get endpointslice` ตัดรายการเมื่อเกิน 3 IP (`+ 2 more...`) และแสดง IP ของ Pod ที่ไม่ ready ด้วย → ดู jsonpath conditions
- `kubectl expose` ใส่ `targetPort` เป็นเลขพอร์ต ไม่ใช่ชื่อ
- เรียกพอร์ตที่ Service ไม่ได้เปิด = `download timed out` (ไม่ใช่ refused); targetPort ผิด / ไม่มี endpoint = `Connection refused`
- browser refresh เห็นชื่อ Pod เดิม (keep-alive) ไม่ได้แปลว่ามี Pod เดียว — ใช้ `./hit.sh` / curl วน
- NetworkPolicy ที่เลือก `app=web` ทำให้ทุกคนนอกกฎ (รวม `client` ใน shop เอง) เข้าไม่ได้
- ExternalName ไป `example.com` แล้ว wget ได้ `409 Conflict` = Host header ไม่ตรง (ตัวอย่างข้อจำกัดจริง); ถ้าไม่มีเน็ต nslookup ไม่ได้ A record แต่ยังเห็น `canonical name`
- ลบ Pod db → หน้าเว็บ 503 ทั้งร้านแต่ Pod web ยัง Ready (ตั้งใจ) ; แก้ด้วยการลบ Pod web 1 ตัว และออเดอร์เก่าหายถาวร (emptyDir)
- ตอนลบ Pod web, Pod เก่าขึ้น `Error` ชั่วครู่ และ Event `Readiness probe failed ... connection refused` ตอน Pod เพิ่งเริ่มเป็นเรื่องปกติ
- ตัวเลข err ตอนลบ Pod ขึ้นกับความเร็วเครื่อง (ทดสอบ 32 CPU: ทีเดียว 4–7 ครั้ง) เครื่องช้ากว่าจะเห็นมากกว่า
- ใช้ `pkill -f "[k]ubectl ..."` ถ้าต้องฆ่า process (บทเรียนบท 005)

## สถานะไฟล์/cleanup

- scratch (`logs/006_service/scratch/`): `r.sh`, `container-name`, `k8s-up.out`, `buildtest.out`, `check-1.2.png` / `check-503.png` / `check-1.3.png` (ภาพตรวจของ agent ไม่ใช่ screenshot ส่งงาน), `storyboard-extract.txt`; askpass ลบแล้ว
- ใน container: image ทดลอง `buildtest:1.2` ลบแล้ว, build cache ล้างก่อนรอบสุดท้าย; ไฟล์ `/root/hit*.out`, `/root/w8b.out`, `/root/ep13.out` เป็นผล hit.sh ระหว่างทดสอบ
- container `k8s-lab-svc006lab-06b9a8` ยังรัน (SSH 2224, NodePort 30090–30092) — ผู้ประสานงานลบเอง
