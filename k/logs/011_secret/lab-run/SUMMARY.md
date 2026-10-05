# SUMMARY — ทดสอบ LAB บท 011 Secret (5 ต.ค. 2569)

- container: `k8s-lab-secret011-9ffaf1` (owner `agent-011`, image `8108a1bc7901`, SSH 2224, NodePort 30080-30082 → host 30090-30092) — **ยังเปิดอยู่** ดู `handoff.md`
- สร้างตามสกิล k8s-lab (`up --ssh --nodeport`, `--privileged --hostname k8s-lab`, docker cp ไป `/workspace/011_kubernetes_secret/02_LAB`) — ใช้ `K8S_LAB_MAX=7` เพราะมี `k8s-lab-*` ของ agent อื่นรันอยู่ 6 ตัว (ผู้ใช้อนุญาตกรณีพิเศษ 1 ตัว) ไม่ได้แตะ container อื่น; lock/TMPDIR อยู่ใน `scratch/t` (ไม่ใช้ /tmp)
- คลัสเตอร์: kind v1.37.0 3 Node Ready (`k8s-up` 50 วิ), kubectl v1.37.1
- เวลาใน log เป็น UTC ของ host (container แสดงเวลา Asia/Bangkok = +7)
- log: `lab00.log`–`lab09.log` (คำสั่ง + output จริง + `[rc=N]`), `handoff-test.log` (ฉาก screenshot เปลี่ยนรหัส + คืนสภาพ)

## ผลรายข้อ

| LAB | ผล | เวลาจริง | ผลจริงสำคัญ |
|-----|----|---------|-------------|
| 0 เตรียม | ✅ | 54 วิ (postgres pull+save+load 16 วิ, build+load som-shop-web:1.5 37 วิ) | 3 Node Ready; `postgres:17.11-alpine` + `som-shop-web:1.5` บน lab-worker/lab-worker2; มี openssl 3.0.13; **ไม่มี** htpasswd/strings/xxd/hexdump |
| 1 base64 | ✅ | 3 วิ | `password: bWVvdzEyMzQ=`, `username: c29t`; decode `meow1234`; `echo` → `bWVvdzEyMzQK`, `echo -n` → `bWVvdzEyMzQ=`; describe `password:  8 bytes` / `username:  3 bytes`; go-template base64decode ได้; สร้างซ้ำ → `error: failed to create secret secrets "demo" already exists` |
| 2 type | ✅ | 4 วิ | `pw.txt` 8 byte (ไม่มี newline) → `bWVvdzEyMzQ=`; ไฟล์มี newline → `bWVvdzEyMzQK`; stringData ชนะ `override-by-stringData`; last-applied เก็บ `"stringData":{"PASSWORD":"override-by-stringData",...}` เป็นข้อความ; ผ่าน pipe เก็บเป็น base64 ใน data; `--server-side` ไม่มี annotation; basic-auth ว่าง → `[data[username]: Required value, data[password]: Required value]`; tls ไม่มี key → `data[tls.key]: Required value`; cert ไม่ใช่ PEM → `tls: failed to find any PEM data in certificate input`; dockerconfigjson decode เห็น `"password":"example-pass"` + `auth` = `som:example-pass`; 1.1 MB → `data: Too long: may not be more than 1048576 bytes` |
| 3 ใช้ใน Pod | ✅ | 2 นาที 45 วิ | env `DB_PASSWORD=meow1234`, `SD_PASSWORD=override-by-stringData`, `SD_USERNAME=som`; `tmpfs on /etc/secret type tmpfs (ro,relatime,size=…,noswap)`; 0400 → `-r--------`; เขียนไฟล์ → `Read-only file system`; `/proc/1/environ` เห็น DB_PASSWORD; **ไฟล์เปลี่ยนหลัง 71 วิ และ 81 วิ** (แผนเขียน 47) env ค่าเดิม; Pod ใหม่ได้ค่าใหม่ `newpass-01`; immutable → `The Secret "frozen" is invalid: data: Forbidden: field is immutable when \`immutable\` is set` และ patch `immutable:false` → `immutable: Forbidden: …` → ต้องลบแล้วสร้างใหม่ |
| 4 TLS | ✅ | 21 วิ | `subject=CN = shop.som.local`, `notAfter=Oct  5 11:35:09 2027 GMT`; key ไม่ใช่ PEM → `tls: failed to find any PEM data in key input`; curl ทันทีหลัง Ready → `rc=35` (SSL_ERROR_SYSCALL) รอ 5 วิแล้ว → `curl: (60) SSL certificate problem: self-signed certificate`; `-k`/`--cacert`/`--resolve` → `HTTPS ร้านน้องส้ม`; `https://127.0.0.1` + cacert → `(60) SSL: no alternative certificate subject name matches target host name '127.0.0.1'`; http ไปพอร์ต https → `400 The plain HTTP request was sent to HTTPS port`; ไฟล์ใน Pod `-r--------`; จาก host (gateway:30091) ได้ทั้ง `-k` และ (60) → เครื่องนักศึกษา `https://localhost:30081` ใช้ได้ (เบราว์เซอร์เตือน cert) |
| 5 imagePullSecrets | ✅ | 1 นาที 42 วิ | ใช้ `som-menu:1.0` (busybox+menu.txt) ตามแผน; `/v2/` ไม่ใส่รหัส 401; nopull → `authorization failed: no basic auth credentials` (สถานะที่ 20 วิ = `ImagePullBackOff`); regcred → Running `Successfully pulled … in 311ms`, log `เมนูลับของน้องส้ม: ปลาทูย่างซีอิ๊ว 🐟`; wrongcred → `401 Unauthorized`; SA default + regcred → viasa Running `[{"name":"regcred"}]`; **cached (ns reg2, ไม่มีบัตร, nodeName lab-worker ที่มี image แล้ว) → ยัง `no basic auth credentials`** ยืนยัน kubelet ตรวจบัตรซ้ำ; **Pod `som-shop-web:1.5` บน lab-worker เดียวกันรันได้ (`som-shop-web:1.5 ok`)** และ LAB9 ร้านรันปกติ → ไม่กระทบ; cleanup ลบ ns/registry/logout ครบ |
| 6 projected + token | ✅ | 6 วิ | `/etc/som/{announcement.txt,db/password,pod-name}` โหมด `-r--r-----` tmpfs ro; ค่า `proj` / `newpass-01` / `วันนี้ปลาทูสดมาก 🐟`; `builder-token kubernetes.io/service-account-token 3`; describe แสดง `token: eyJhbGciOiJSUzI1NiIs…` เต็ม; `get sa builder -o yaml` ไม่มี `secrets:`; `create token --duration=10m` ได้ JWT `sub: system:serviceaccount:default:builder` |
| 7 RBAC | ✅ | 15 วิ | intern get pods/configmaps = yes, get/list secrets = no; get/list/describe → `Forbidden`; `get pod spod -o yaml` เห็นแค่ `secretKeyRef: key: password, name: demo` (ระวัง: last-applied ก็แสดงแค่ชื่อเช่นกัน); exec → `cannot create resource "pods/exec"`; maker get secrets = no, create pods = yes → `stolen=newpass-01` |
| 8 etcd | ✅ | 2 วิ | `--keys` แสดง 12 key; `grep -a -o newpass-01` เจอ; `cat -v` เห็น protobuf `password^R newpass-01`; ConfigMap เห็น `วันนี้ปลาทูสดมาก`; grep encryption ใน kube-apiserver.yaml → `rc=1` (ไม่มี) |
| 9 ร้าน som-shop-v7 | ✅ | ~4 นาที (ไม่นับฉาก handoff) | ดูตารางด้านล่าง |

### LAB9 รายขั้น (คลัสเตอร์สะอาด เริ่มจาก `k8s-010/`)

| ขั้น | ผลจริง | orders |
|-----|-------|--------|
| เริ่ม | `apply -f k8s-010/` → sts+deploy rollout 14 วิ; **ร้านใหม่ orders=0** → POST 3 ออเดอร์ → `orders=3`; history 1 `1.5 ป้ายร้านจาก ConfigMap` | 0→3 |
| A | intern context สร้างด้วย `rbac/intern-context.sh`; `grep -o 'som:[a-z0-9]*@'` ใน deploy = **4 บรรทัด** (web + db-seed ใน spec และอีก 2 ใน annotation last-applied; แผนเขียน 3); sts/pod เห็น `POSTGRES_PASSWORD value: meow1234`; get secrets → Forbidden | 3 |
| B | `secret/som-db-secret created`; describe `DATABASE_URL: 52 bytes`, `POSTGRES_PASSWORD: 8 bytes`; ไม่มี annotation; `apply --dry-run=server -f examples/05-secret.example.yaml` → Warning `missing the kubectl.kubernetes.io/last-applied-configuration annotation` + `configured (server dry run)` | 3 |
| C1 | `statefulset.apps/som-db configured` rollout **1.7 วิ**, PVC `data-som-db-0` เดิม, uid Pod ใหม่; intern เห็น `secretKeyRef key: POSTGRES_PASSWORD name: som-db-secret` | 3 |
| C2 | rollout 17.6 วิ; hit.sh 12/12 ok กระจาย 3 Pod; footer `Kubernetes LAB 011 · รหัส DB อยู่ใน Secret som-db-secret`; history 2 `1.5 รหัส DB จาก Secret`; intern `grep -c meow1234` = **0**; get/describe secret → Forbidden; can-i get secrets no, pods/exec no, pods/log yes; exec → Forbidden; intern logs db-seed ได้ (`seeded 6 products (new: 0)`) | 3 |
| D1 | `ALTER ROLE`; web เดิม 200×6; `-h som-db-0.som-db` รหัสเก่า → `FATAL:  password authentication failed for user "som"`, รหัสใหม่ → `1`; `-h 127.0.0.1` รหัสมั่ว → `1` (pg_hba `127.0.0.1/32 trust`, `host all all all scram-sha-256`) | 3 |
| D2 | Pod ใหม่ `Init:Error` restart วน; **log db-seed เต็ม**: stack `parser.js:306` → `error: password authentication failed for user "som"` → object `severity: 'FATAL', code: '28P01', file: 'auth.c', line: '329', routine: 'auth_failed'` → `Node.js v22.23.3`; Pod เดิมยัง 200×6; `error: deployment "som-web" exceeded its progress deadline`, `Progressing False ProgressDeadlineExceeded`, `3/3 UP-TO-DATE 1` | 3 |
| D3 | `secret/som-db-secret configured` (+Warning missing last-applied); rollout 18.1 วิ; POST → `order_id 4`; 12/12 ok `orders=4`; annotation last-applied เก็บ base64 (`grep -c purr5678` = 0) | 4 |
| D4 | ลบ som-db-0 → Ready; `count(*)` 4 เท่าเดิม; รหัส `purr5678` ใช้ได้ | 4 |
| E | `som-tls` → `30-https.yaml` Warning `would violate PodSecurity "restricted:latest": allowPrivilegeEscalation != false …, unrestricted capabilities …, runAsNonRoot != true …, seccompProfile …`; `-k` `/api/stats` ได้ร้าน; `--cacert` `/api/shop` ได้ JSON; ไม่มี -k → `rc=60`; POST ผ่าน HTTPS → order 5; `/` → `200 text/html`; tls ไฟล์ `-r--------`; **`extra/30-https-restricted.yaml` (nginxinc/nginx-unprivileged:1.27-alpine) apply ไม่มี Warning ทำงานได้** `uid=101(nginx)` ไฟล์ `-r--r----- root nginx` (fsGroup) — ทดสอบแล้วสลับกลับเป็น `k8s/30-https.yaml` | 5 |
| F | etcd → `postgres://som:purr5678@` | 5 |
| สภาพสุดท้าย | `apply -f k8s/` (sts แสดง `configured` แต่ `kubectl diff` ว่าง ไม่ restart); จาก host: `gateway:30090/api/stats` และ `https://gateway:30092/api/stats` → `orders=5`, `/` 200 ทั้งคู่; ssh 2224 PASS (password+key) | 5 |

## การเปลี่ยนแปลงจากแผน / สิ่งที่พบใหม่

1. volume อัปเดตหลัง **71 / 81 วิ** (แผน 47 วิ) → ใช้คำว่า "ราว 1 นาที (ไม่เกิน ~1.5 นาที)"
2. LAB9 บนคลัสเตอร์สะอาด `k8s-010/` เริ่มที่ **orders=0** → README ต้องมีขั้น POST 3 ออเดอร์ (หรือเปิดเว็บสั่ง 3 ครั้ง) ก่อนขั้น A ถึงจะได้ orders=3 ตามภาพ
3. ขั้น A `grep -o 'som:[a-z0-9]*@'` ได้ 4 บรรทัด (แผน 3)
4. ไฟล์ตัวอย่างอยู่ที่ `som-shop-v7/examples/05-secret.example.yaml` (แผนเขียน `k8s/`) — ดีกว่าเพราะ `kubectl apply -f k8s/` ไม่ apply ไฟล์ตัวอย่าง
5. ข้อความเต็ม db-seed ยืนยันแล้ว: `error: password authentication failed for user "som"` อยู่หลังบรรทัด stack ที่ 4 และก่อน object ที่จบด้วย `routine: 'auth_failed'`
6. ทางเลือก PSA restricted (`extra/30-https-restricted.yaml`) ผ่านจริง ไม่มี Warning
7. `rollout restart` ทำให้ history มี change-cause ซ้ำ `1.5 รหัส DB จาก Secret` ทุก revision (2,3,4…) — README ควรบอกหรือใช้ `kubectl annotate … kubernetes.io/change-cause=… --overwrite`
8. LAB2 ใช้ `pw.txt` เป็นทั้ง cert และ key → error เป็น `… PEM data in certificate input`; แบบ `key input` เกิดใน LAB4 (cert จริง + key ผิด)
9. openssl req พิมพ์จุด/บวก (progress ของ keygen) ยาวหลายบรรทัดใน stderr — ปกติ
10. `lab06.log` มี token ของ SA builder เต็ม (คลัสเตอร์ทดลองชั่วคราว ใช้ไม่ได้เมื่อลบ container) — ถ้าจะนำ log ไปเผยแพร่ให้ตัดออก

## ป้าย/ข้อความในภาพที่ไม่ตรงผลจริง (เทียบ `images.json`)

| ภาพ | จุดที่ไม่ตรง (Text verbatim / caption_th / Scene) | ผลจริง | ควรใช้แทน |
|-----|---------------------|-------|-----------|
| T19 | Text `"~47 วินาที"`; caption "วัดได้ ~47 วินาที" | 71 และ 81 วิ | `"~1 นาที"`; caption "วัดได้ราว 1 นาที (71–81 วินาที)" |
| L05 | Text `"~47 วินาที"`; caption "เปลี่ยนใน ~47 วินาที" | 71 และ 81 วิ | `"~1 นาที"`; caption "เปลี่ยนในราว 1 นาที" |
| L14 | Text `"orders=3"` / caption "ออเดอร์ 3" — ถูกเฉพาะเมื่อ README มีขั้นสั่ง 3 ออเดอร์ (k8s-010/ บนคลัสเตอร์สะอาดเริ่ม 0) | `orders=0` → POST 3 → `orders=3` | คงป้ายไว้ได้ ถ้า README มีขั้นสั่ง 3 ออเดอร์; ไม่งั้นแก้ caption เป็น "สั่ง 3 ออเดอร์ก่อน → orders=3" |
| T14 | caption "get -o yaml จะเห็นแค่ data" | `apply` แล้ว `get -o yaml` เห็น stringData ใน annotation last-applied ด้วย | "ฟิลด์ที่เก็บจริงเป็น data (แต่ถ้า apply ไฟล์ annotation last-applied มี stringData ติดมา — ดู T15)" |
| L08 | Text `"ErrImagePull"` | ที่ 20 วิ STATUS = `ImagePullBackOff` (สลับกับ `ErrImagePull`), event `no basic auth credentials` | `"ErrImagePull / ImagePullBackOff"` หรือ `"no basic auth credentials"` (เล็กน้อย) |
| L10 | Text `"secretKeyRef: demo"` | YAML จริง `secretKeyRef:` / `key: password` / `name: demo` | `"secretKeyRef → name: demo"` (เล็กน้อย) |
| L13 | caption "intern อ่านได้แค่ Pod/ConfigMap" | `rbac/intern.yaml` ให้ get/list/watch pods, pods/log, configmaps, deployments, statefulsets | "intern อ่านได้ Pod/ConfigMap/Deployment แต่ไม่ได้ Secret" |
| T09 | caption "key ไม่ใช่ PEM → failed to find any PEM data in key input" | ถูก (LAB4); แต่ LAB2 คำสั่ง `--cert=pw.txt` ได้ `… in certificate input` | ป้าย `"failed to find any PEM data"` ใช้ได้ทั้งสองแบบ — ไม่ต้องแก้ |

ภาพ needs_test อื่น (T05 T06 T10 T11 T15 T17 T18 T20 T21 T23–T27 T32 T35, L02 L03 L04 L06 L07 L09 L11 L12 L16–L21) และภาพที่อ้างค่าจริง (T02 T04 T12 T13 L01 L15 L22) **ตรงกับผลจริง** — เช่น L16 "~2 วินาที" (1.7 วิ), L17 "meow1234: 0 บรรทัด", L18 "200 OK" + "password authentication failed", L19 "Init:Error"/"auth_failed", L20 "orders=4", L21 "Warning PodSecurity", T04 "≤ 1 MiB" (`may not be more than 1048576 bytes`)

## ข้อควรระวังสำหรับนักศึกษา

- `echo` ใส่ newline → ใช้ `echo -n` / `printf`; ไฟล์ `--from-file` ต้องไม่มี newline ท้าย
- `kubectl apply` ไฟล์ stringData = รหัสเป็นข้อความใน annotation → ใช้ `kubectl create secret` หรือ `apply --server-side`; ห้าม commit ไฟล์ที่มีรหัสจริง (`.gitignore` มี `secret.yaml`, `*.secret.yaml`, `*.key`, `*.crt`)
- volume อัปเดตเองราว 1 นาที แต่ env ไม่เปลี่ยน ต้อง restart Pod; immutable ต้องลบแล้วสร้างใหม่
- HTTPS: curl ทันทีอาจได้ rc=35 รอ 5 วิ; self-signed → เบราว์เซอร์เตือน; ใช้ `localhost` ไม่ใช่ `127.0.0.1` (SAN)
- LAB5 อย่าใช้ image ของร้านใน registry (kubelet v1.37 ตรวจบัตรซ้ำ) และอย่า `crictl rmi`; รัน `./cleanup-registry.sh` ทุกครั้ง
- ทดสอบรหัส DB ต้องใช้ `-h som-db-0.som-db` (127.0.0.1 เป็น trust ผ่านเสมอ)
- เปลี่ยนรหัสต้อง 2 ฝั่ง: `ALTER USER` + แก้ Secret + `rollout restart`; Pod เดิมยังทำงานได้ไม่ได้แปลว่ารหัสใหม่ถูก; ถ้าลืมแก้ Secret rollout จะค้าง `ProgressDeadlineExceeded` (Pod เดิมยังขาย)
- ห้ามใช้ `kubectl edit` ใน shell ที่ไม่มี tty (ใช้ `patch`/`apply`); token ของ context intern หมดอายุ 24h รัน `rbac/intern-context.sh` ใหม่
- kind ไม่มี encryption at rest — ใครเข้าถึง etcd อ่าน Secret ได้หมด
