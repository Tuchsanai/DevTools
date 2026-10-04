# สรุปผลทดสอบ LAB 002 — Kubernetes Pod (รันจริง 4 ต.ค. 2569)

- container ทดลอง: `k8s-lab-pod002-20f6d7` (image `tuchsanai/devtools-kind:2569_1`, ID `8108a1bc7901`, `--privileged --hostname k8s-lab`, SSH `2224→22`) — **ยังเปิดไว้** ตาม handoff ดู `handoff.md`
- ไฟล์ LAB อยู่ใน container ที่ `/workspace/002_kubernetes_pod/02_LAB` (`docker cp`, ไม่ bind mount) รัน LAB 0→9 ต่อเนื่องในคลัสเตอร์เดียว
- log คำสั่ง + output จริง: `lab00.log` … `lab09.log` ในโฟลเดอร์นี้

## ผลรายข้อ

| LAB | ผล | หมายเหตุสำคัญจากการรันจริง |
|---|---|---|
| 0 สร้างคลัสเตอร์ | ✅ ผ่าน | `k8s-up` 49.6 วินาที (node image อยู่ใน image แล้ว), context `kind-lab`, 3 node Ready v1.37.0, kube-system 13 Pod Running, control-plane มี taint `node-role.kubernetes.io/control-plane:NoSchedule` |
| 1 `kubectl run` | ✅ ผ่าน | `ContainerCreating` → `1/1 Running` ~6 วินาที, IP `10.244.3.2` บน `lab-worker2`, Events Scheduled→Pulling→Pulled→Created→Started (ข้อความมี prefix `spec.containers{hello}:`), ลบแล้ว `No resources found` |
| 2 Pod YAML แรก | ✅ ผ่าน | dry-run ได้โครง, `explain` ได้, `pod/web created` → `unchanged`, `create` ซ้ำ → `AlreadyExists`, แก้ containerPort แล้ว apply → `Forbidden: pod updates may not change fields other than ...` |
| 3 exec/logs/port-forward | ✅ ผ่าน | nginx/1.27.5, แก้ index.html, port-forward ฟัง `127.0.0.1` + `[::1]`, curl ได้ HTML, **ssh -L จากเครื่อง host ผ่าน SSH port 2224 แล้ว curl ได้หน้าเว็บจริง**, `logs -f` เห็น access log |
| 4 Labels | ✅ ผ่าน | ผลตรงแผนทุกคำสั่ง (`-l`, `in`, `!=`, `-L`, label/--overwrite/`env-`, annotate ภาษาไทย, `delete -l`) |
| 5 Lifecycle | ✅ ผ่าน | completed → `Completed`/phase `Succeeded`; crash → RESTARTS เพิ่ม, STATUS สลับ `Running`/`Error`/`CrashLoopBackOff`; onfailure → restart 1 ครั้งแล้ว `Completed`; bad-image → `ErrImagePull` ⇄ `ImagePullBackOff` |
| 6 env/command/resources | ✅ ผ่าน | env ภาษาไทยแสดงถูก, QoS `Burstable`, `OOMKilled` exit 137, pending → `FailedScheduling ... Insufficient cpu`, env ตัวเลขไม่ใส่ quote → error ชัดเจน |
| 7 Probes | ✅ ผ่าน | readiness `0/1` → สร้างไฟล์ `1/1` → ลบ `0/1` RESTARTS 0; liveness fail แล้ว restart (RESTARTS 1) |
| 8 Multi-container | ✅ ผ่าน | `2/2`, IP เดียว (`hostname -i` เท่ากัน), helper `wget localhost:80` ได้ nginx; init-sidecar `Init:0/1` → `2/2 Running`, `nginx -s stop` → web restart 1 ไฟล์ยังอยู่, ลบ/สร้างใหม่ → ไฟล์เริ่มใหม่ |
| 9 som-shop | ✅ ผ่าน | build 28 วิ, kind load, `2/2 Running`, seed 6 สินค้า, psql 6 แถว, health OK, **port-forward + ssh -L จาก host ได้ HTML ร้าน + กดสั่งซื้อใน browser ได้**, POST /api/orders ลด stock, restart db ข้อมูลอยู่, ลบ Pod + apply ใหม่ข้อมูลกลับค่าตั้งต้น |

## ข้อที่แผนเดาไว้ — ค่าจริง

- **READY ของ som-shop = `2/2`** (นับ web + native sidecar `db`; init ที่จบแล้วไม่นับ) — `kubectl logs som-shop` default เป็น `web` และพิมพ์ `Defaulted container "web" out of: web, db (init), wait-for-db (init), db-seed (init)`
- **ลำดับ STATUS ตอน init** (`kubectl get pod som-shop -w` จริง): `0/2 Init:0/3` → `0/2 Init:1/3` → `1/2 Init:1/3` (db ready) → `1/2 Init:2/3` → `1/2 PodInitializing` → `1/2 Running` → `2/2 Running` รวม ~7–9 วินาที (เมื่อ image อยู่บน node แล้ว) — `PodInitializing` อยู่สั้นมาก การ sample ทีละ 1 วิอาจไม่เห็น
- LAB 8 init-sidecar: `Init:0/1` (~5 วิ เพราะ sleep 5) → `2/2 Running` ไม่ทันเห็น `PodInitializing`
- **วิธีหยุด db ที่ได้ผล**: `kubectl exec som-shop -c db -- su postgres -c 'pg_ctl stop -m fast'` → ขึ้น `waiting for server to shut down....command terminated with exit code 137` (ปกติ เพราะ container ตายระหว่าง exec) db restart ภายใน ~1 วิ: `1/2 Init:0/3 RESTARTS 1` ชั่วขณะ แล้ว `2/2 Running 1` — RESTARTS ที่เพิ่มเป็นของ `db` (web 0), Last State `Completed` exit 0, ข้อมูล (3 ออเดอร์, stock 19/55) ยังอยู่ web ไม่ถูก restart
  - สังเกต: ระหว่าง sidecar restart คอลัมน์ STATUS แสดง `Init:0/3` สั้น ๆ (ไม่ใช่ init รันใหม่) ควรอธิบายในเอกสาร
- **ลบ Pod**: `kubectl delete pod som-shop` ใช้ 0.8 วิ, 10 วิผ่านไปยัง `No resources found`, apply ใหม่ IP เปลี่ยน `10.244.3.15 → 10.244.3.16`, orders 0, stock กลับ 20/15/10/60/40/25, db-seed `seeded 6 products (new: 6)`; port-forward เดิม error `lost connection to pod` ต้องรันใหม่
- **ข้อความ Events จริง** (Kubernetes v1.37 ขึ้นต้น message ด้วย `spec.containers{<name>}:`)
  - CrashLoopBackOff: `Warning  BackOff  kubelet  spec.containers{app}: Back-off restarting failed container app in pod crash-pod_default(<uid>)`; state.waiting `{"message":"back-off 5m0s restarting failed container=app pod=crash-pod_default(...)","reason":"CrashLoopBackOff"}`
  - ImagePullBackOff: `Failed to pull image "nginx:9.99-doesnotexist": rpc error: code = NotFound desc = failed to pull and unpack image "docker.io/library/nginx:9.99-doesnotexist": failed to resolve reference "...": docker.io/library/nginx:9.99-doesnotexist: not found` / `Error: ErrImagePull` / `Error: ImagePullBackOff` / `Back-off pulling image "nginx:9.99-doesnotexist"`
  - OOMKilled: `State: Terminated  Reason: OOMKilled  Exit Code: 137` (Last State เหมือนกัน), STATUS `OOMKilled` สลับ CrashLoopBackOff
  - FailedScheduling: `0/3 nodes are available: 1 node(s) had untolerated taint(s), 2 Insufficient cpu. preemption: 0/3 nodes are available: 3 Preemption is not helpful for scheduling.`
  - Liveness: `Warning Unhealthy ... Liveness probe failed: cat: can't open '/tmp/healthy': No such file or directory` และ `Normal Killing ... Container app failed liveness probe, will be restarted`
  - Readiness: `Readiness probe failed: Get "http://10.244.1.6:80/ready.html": dial tcp ...: connect: connection refused` (ครั้งแรก ก่อน nginx ขึ้น) แล้ว `Readiness probe failed: HTTP probe failed with statuscode: 404`
  - env ตัวเลขไม่ใส่ "": `Error from server (BadRequest): ... json: cannot unmarshal number into Go struct field EnvVar.spec.containers.env.value of type string`

## เวอร์ชันจริงและ image ID

| รายการ | ค่า |
|---|---|
| kubectl client / server | v1.37.1 / v1.37.0 (node `kindest/node` ID `a1ed56cfb0e7`, Debian 13, containerd 2.3.4) |
| kind / Docker ใน container | 0.33.0 / 29.8.2 (containerd image store) |
| nginx | `nginx:1.27-alpine` → nginx/1.27.5 |
| busybox | `busybox:1.36` |
| PostgreSQL | `postgres:17.11-alpine` → PostgreSQL 17.11 (docker image ID `b0f9560a2de0`, บน node `79bd7c99e923`) |
| Node.js ใน image | v22.23.3 (`node:22-alpine`) |
| Next.js / React / pg / TypeScript | 16.3.8 / 19.3.0 / 8.23.1 / 5.9.3 (`@types/node` 22.20.5, `@types/react` 19.3.0, `@types/pg` 8.23.1) — มี `package-lock.json` |
| `som-shop-web:1.0` | docker image ID `fb77bcbdb64a` (305 MB disk, 76.6 MB content), บน node (crictl) `a406a861ff7c` |

## การเปลี่ยนแปลงจากแผน

1. **pin postgres เป็น `postgres:17.11-alpine`** (17-alpine ตอนทดสอบ = 17.11) ทั้ง `db` และ `wait-for-db`
2. **`kind load docker-image postgres:...` ล้มเหลว**: `ERROR: failed to load image: ... ctr ... images import --all-platforms ... content digest sha256:612d...: not found` เพราะ Docker 29 ใช้ containerd image store และ image ที่ pull มาเป็น multi-platform (มีเนื้อหาแค่ amd64) — **แก้ด้วย** `docker save --platform linux/amd64 postgres:17.11-alpine -o /tmp/pg.tar && kind load image-archive /tmp/pg.tar --name lab` (ทดสอบผ่าน) ส่วน `som-shop-web:1.0` ที่ build เอง `kind load docker-image` ได้ปกติ (4.8 วิ) ทางเลือกที่ง่ายกว่าคือไม่ preload ให้ kubelet pull เอง (กรณีนี้ไม่ได้ทดสอบเพราะ preload ไปแล้ว)
3. **ขั้น 6 ของ LAB 9 ใช้ `http://127.0.0.1:3000/api/health` แทน `localhost`**: `wget -qO- http://localhost:3000/...` ใน container web ได้ `Connection refused` เพราะ busybox wget resolve `localhost` เป็น `::1` ก่อน แต่ Next.js (`HOSTNAME=0.0.0.0`) ฟังเฉพาะ IPv4 (`netstat` เห็น `0.0.0.0:3000` ไม่มี `:::3000`) ส่วน Postgres ฟังทั้งคู่ (`localhost:5432` จึงใช้ได้) คงค่า `HOSTNAME=0.0.0.0` ไว้เพราะทนทานกว่า `::` — ใช้เป็นจุดสอนได้ (`localhost` = 127.0.0.1 หรือ ::1) port-forward และ probe ใช้งานได้ปกติ
4. LAB 3: ข้อความที่ echo ลง index.html ใส่ `<meta charset=utf-8>` นำหน้า เพราะ nginx ส่ง `Content-Type: text/html` ไม่มี charset ภาษาไทยอาจเพี้ยนใน browser
5. LAB 5 `onfailure-pod` ออกแบบให้ล้มรอบแรก (exit 1) แล้วสำเร็จรอบสอง โดยใช้ emptyDir `/work` จำว่าเคยลองแล้ว → เห็น RESTARTS 1 + `Completed` เปรียบเทียบกับ crash-pod ได้ชัด (ใช้ emptyDir ก่อนสอนใน LAB 8 — README ควรบอกสั้น ๆ)
6. LAB 5 แก้ bad-image: ทดสอบทั้ง `kubectl apply` ไฟล์ที่แก้ tag แล้วทันที (`pod/bad-image-pod configured` → Running เพราะ `image` เป็น field เดียวที่แก้ได้) และแบบ delete → apply ตามแผน ใช้ได้ทั้งคู่
7. เพิ่มไฟล์ที่แผนไม่ได้ระบุ: `app/globals.css`, `tsconfig.json`, `next-env.d.ts` (Next.js สร้าง), หน้าเว็บเพิ่มกล่องสถิติ (ออเดอร์ทั้งหมด/ชิ้นที่ขาย/จำนวนสินค้า) และ "ออเดอร์ล่าสุด" 5 รายการ, `POST /api/orders` จำกัด qty 1–10 (ตอบ 400 `ข้อมูลไม่ถูกต้อง`) และตอบ 409 เมื่อ stock ไม่พอ; seed log เป็น `seeded 6 products (new: 6)`
8. `public/som.png` crop หน้าน้องส้ม (แบบยิ้มตาปิด) จาก `00-character-som.png` ด้วย PIL ขนาด 256×256
9. Dockerfile runner ไม่ต้อง copy `node_modules/pg` แยก — standalone trace `pg` และ dependency ครบแล้ว (seed รันผ่านใน init container)

## ข้อควรระวังสำหรับนักศึกษา (ใส่ใน README)

- **เวลา**: `k8s-up` ~50 วิ; build `som-shop-web:1.0` ~30 วิในเครื่องทดสอบ (32 core, เน็ตเร็ว; ต้องดึง `node:22-alpine` + `npm ci` 42 แพ็กเกจ เครื่องช้า/เน็ตช้าอาจหลายนาที); `kind load` ~5 วิ
- **Docker Hub rate limit**: LAB ดึง `nginx:1.27-alpine`, `busybox:1.36`, `postgres:17.11-alpine`, `node:22-alpine` แบบ anonymous — ถ้าทั้งห้องใช้ IP เดียวกันอาจโดน `429 Too Many Requests` / `toomanyrequests` (จะเห็นเป็น ErrImagePull) แนะนำ preload ตามข้อ 2 ข้างบน
- **เครื่อง ARM (Apple Silicon)**: คำสั่ง `docker save --platform linux/amd64` ต้องเปลี่ยนเป็น `linux/arm64` (ไม่ได้ทดสอบบน ARM)
- **ลบ Pod busybox ช้า ~30 วิ** (`time kubectl delete` = 30.3 วิ สำหรับ init-sidecar-pod) เพราะ `sh` เป็น PID 1 ไม่ตอบ SIGTERM → รอ terminationGracePeriod 30 วิ บอกให้รอ หรือใช้ `--now`/`--grace-period=1` — ผลเดียวกันทำให้ liveness-exec-pod restart จริงที่ ~75 วิ (fail ที่ ~45 วิ + รอ kill 30 วิ) ให้รอดูอย่างน้อย 90 วิ
- **CrashLoopBackOff ไม่ได้ขึ้นตลอด**: บน K8s 1.37 STATUS ของ crash-pod เป็น `Error` เกือบตลอด (sample 3 นาที: Error 41 ครั้ง, CrashLoopBackOff 18, Running 1) ให้บอกว่าเห็น `Error`/`CrashLoopBackOff` สลับกันเป็นปกติ ดูที่ RESTARTS ที่เพิ่มและ Events `BackOff`
- `ImagePullBackOff` ก็สลับกับ `ErrImagePull` ทุกครั้งที่ลอง pull ใหม่
- `kubectl logs onfailure-pod --previous` หลัง Pod Completed ได้ `unable to retrieve container logs for containerd://...` (container เก่าถูกเก็บกวาด) — ไม่ต้องสั่งข้อนี้
- `pending-pod` ขอ `cpu: "64"` — node ของ kind เห็น CPU เท่าเครื่องจริง (เครื่องทดสอบ allocatable 32) เครื่องที่มีมากกว่า 64 thread จะไม่ Pending (แทบไม่มี)
- port-forward ผูกกับ Pod เดิม: ลบ/สร้าง Pod ใหม่ต้อง Ctrl+C แล้วรัน `kubectl port-forward` ใหม่ (`error: lost connection to pod`)
- ใน k8s-lab จริง port 3000/8080 ใน container ไม่ชนอะไร แต่บนเครื่องนักศึกษาถ้า port 3000/8080 ถูกใช้ (เช่น dev server) ให้เปลี่ยนเลขซ้ายของ `-L` เช่น `-L 13000:localhost:3000`
- เวลาใน busybox (LAB 8) เป็น UTC; เวลาในหน้าร้าน "ออเดอร์ล่าสุด" แปลงเป็น Asia/Bangkok แล้ว
- รหัส DB `meow1234` ใน env เพื่อการเรียนเท่านั้น (บทหน้าใช้ Secret)

## สถานะ cleanup

- container `k8s-lab-pod002-20f6d7` **ยังเปิดอยู่โดยตั้งใจ** (Pod som-shop + port-forward 127.0.0.1:3000 + SSH 2224) — ผู้ประสานงานลบเองด้วย `docker rm -fv k8s-lab-pod002-20f6d7`
- ssh tunnel ฝั่ง agent ปิดแล้ว; askpass และโฟลเดอร์ build ชั่วคราวใน `/tmp/k8s002` ลบแล้ว; ไม่ได้ build/แตะ tag ของผู้ใช้, ไม่ได้แตะ `k8s-lab` และ `deep_vision_5090_vllm`
