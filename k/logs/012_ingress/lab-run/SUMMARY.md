# สรุปการทดสอบ LAB บท 012 Ingress (5 ต.ค. 2569, 13:04–13:25)

- container: `k8s-lab-ing012lab-609d0f` (owner `agent-012-lab`, image `8108a1bc7901` = `tuchsanai/devtools-kind:2569_1`, SSH `2224`, NodePort 30080–30082 → host `30090–30092`, gateway `172.18.0.1`) — **เปิดค้างไว้ตามที่สั่ง** สำหรับ screenshot (ดู `handoff.md`)
- kind v1.37.0 3 Node Ready (k8s-up 48 วิ), kubectl v1.37.1, Traefik v3.7.13, whoami v1.11.0
- ทุกคำสั่งรันใน `/workspace/012_kubernetes_ingress/02_LAB` (docker cp ไม่ bind mount) ผ่าน `bash -l` ต่อเนื่องเหมือนนักศึกษาพิมพ์ ทุกไฟล์ log มีบรรทัด `$ คำสั่ง` + output จริง
- ไม่ได้แตะ `k8s-lab` ของผู้เรียน, `deep_vision_5090_vllm` หรือ container ของ agent อื่น, ไม่ใช้ `/tmp` ของเครื่องนี้ (ไฟล์ชั่วคราวอยู่ `logs/012_ingress/scratch/`), ไม่มี credential จริง (รหัสทั้งหมดเป็นค่าตัวอย่างเพื่อการเรียน: `meow1234` ของบท 011, `meow-admin-123` ของหลังร้าน)

## ผลรายข้อ

| LAB | ผล | เวลาจริง | log | หลักฐานสำคัญ |
|---|---|---|---|---|
| (เตรียม) สภาพท้ายบท 011 | ✅ | postgres archive 16.6 วิ, build+load 1.5 33.7 วิ | `pre011-setup.log` | som-web NodePort 30080 + som-https 30082, som-tls `CN=shop.som.local`, orders=3 |
| 0 เตรียม คืนพอร์ต image | ✅ | build+load 1.6 4.6 วิ (cache) | `lab00.log` | `kubectl get svc -A \| grep 3008` เห็น som-web/som-https → ลบ svc → `ไม่มี NodePort 3008x ค้าง`; Deployment/DB/PVC ยังอยู่; worker มี postgres, som-shop-web 1.5, 1.6 |
| 1 ติดตั้ง Traefik | ✅ | CRD 0.18 วิ, rollout 3.7 วิ | `lab01.log`, `lab01-host.log` | `traefik (default)   traefik.io/ingress-controller`; `curl -i localhost:30080` → `HTTP/1.1 404` `404 page not found`; https → 404; dashboard 200; `/api/version` `{"Version":"3.7.13","Codename":"langres",…}`; entrypoints `traefik :8080 / web :8000 / websecure :8443`; ERR=0; จาก host `gateway:30090` → 404, `:30092/dashboard/` → 200 |
| 1 ลองผิด: ข้าม LAB 0 + ลืม CRD | ✅ (ยืนยัน) | — | `lab01-wrong-order.log` | `The Service "traefik" is invalid: spec.ports[0].nodePort: Invalid value: 30080: provided port is already allocated` (ส่วนอื่น created, Deployment รันได้แต่ไม่มีประตู); ไม่มี CRD → `"Failed to watch" err="failed to list *v1alpha1.MiddlewareTCP: the server could not find the requested resource (get middlewaretcps.traefik.io)"` 40 บรรทัดใน 15 วิ; apply CRD ตามหลัง → บรรทัดใหม่หยุดเพิ่ม (41 → 41 ใน 30 วิ) แต่ยังแนะนำ `rollout restart` → ERR=0; dry-run server ใช้ตรวจล่วงหน้าไม่ได้ (`namespaces "traefik" not found`) |
| 1 ลองผิด: Service อื่นขอ 30080 | ✅ | — | `lab01.log` | `error: failed to create NodePort service: Service "probe" is invalid: spec.ports[0].nodePort: Invalid value: 30080: provided port is already allocated` |
| 2 Ingress แรก | ✅ | rollout 3 แอป 9 วิ | `lab02.log` | ก่อนมีป้าย 404; `-H 'Host: shop.localhost'` → `Name: menu`; `http://shop.localhost:30080` → `Host: shop.localhost:30080`, `X-Forwarded-Port: 30080`; curl `Trying [::1]:30080...` แล้ว `Connected to shop.localhost (127.0.0.1)`; ไม่มี Host/other → 404; `getent hosts` rc=2; `--resolve` ผ่าน; ADDRESS `localhost`; access log มี router `ingress-demo-shop-shop-localhost@kubernetes` |
| 3 fan-out | ✅ | — | `lab03.log` | `/api/stats` → `Name: api GET /api/stats`; `/order` → menu; `/admin/x` → admin; `/apix` → menu (ตก /); port `api:http` ใช้ได้; router rule `Host("shop.localhost") && (Path("/api") \|\| PathPrefix("/api/"))` priority 63/67/41; **`/api` ของ whoami ตอบ JSON** (ดูข้อควรระวัง) |
| 4 host-based | ✅ | — | `lab04.log` | ไม่ใส่ class → `traefik`; admin.localhost → admin (ทุก path); other → 404; `Host: ADMIN.localhost` → admin (ชื่อไม่สนตัวพิมพ์) |
| 5 pathType | ✅ | — | `lab05.log` | strict=true: `/api /api/ /api/x` 200 api, `/apix /API` 404, `/docs /docs/ /docs/a` 200, `/docsx` 404, `/menu` 200, `/menu/ /menux` 404, `/impl /impl/x` 200, `/implx` 404; strict=false: `/apix` → api, `/docs` → **404**, `/implx` → admin; คืนด้วย `kubectl apply -f ingress-controller/00-traefik.yaml` ได้ผลเดิม |
| 6 debug | ✅ | — | `lab06.log` | class nginx → ADDRESS ว่าง + 404; `menuu:80 (<error: services "menuu" not found>)`, `menu:8080 ()`, `Events: <none>`; log `ERR Cannot create service error="service not found" … serviceName=menuu` และ `error="service port not found"`; scale 0 → `HTTP/1.1 503 Service Unavailable` `no available server`; lost (HOSTS `*`) → other/typo/wrong/ไม่มี Host → admin ทั้งหมด; **menu=0 ขณะมี lost ยังได้ 503 (ไม่ไหลไป admin)** |
| 7 TLS | ✅ | — | `lab07.log` | PORTS `80, 443`; `-k` → menu + `X-Forwarded-Proto: https`, `X-Forwarded-Port: 30081`; ไม่มี -k → `curl: (60) SSL certificate problem: self-signed certificate` rc=60; `--cacert` ผ่าน shop/admin; `https://127.0.0.1:30081` rc=60; SNI other → `subject=CN = TRAEFIK DEFAULT CERT`; Ingress ไม่มี spec.tls (paths) ตอบบน 30081 ด้วยใบ DEFAULT (`-k` ได้ menu); `http://localhost:30081/` → `HTTP/1.1 404`; ลองถอด `websecure.http.tls` → `HTTP/2 404` ทั้งที่ใบ shop ถูกส่ง (subject shop.localhost) |
| 8 Middleware | ✅ | — | `lab08.log` | `HTTP/1.1 301 Moved Permanently` `Location: https://shop.localhost:30081/menu?x=1`; https 200 (ไม่วน); **ไม่ใส่ port → `Location: https://shop.localhost/menu?x=1` (= 443) และ `curl -L` rc=7**; basic-auth: http → 301 ก่อน, `HTTP/2 401` + `www-authenticate: Basic realm="traefik"`, ผิด 401, ถูก 200, แอปไม่เห็น `Authorization` (removeHeader); strip: ไม่มีบัตร 401, มีบัตร `GET /orders` + `X-Forwarded-Prefix: /admin`, `/admin` → `GET /`, `/adminx` → menu |
| 9 rolling update | ✅ | 18.3 วิ/300 ครั้ง | `lab09.log` | menu → menu-v2: `ok=300 err=0` (menu 67 / menu-v2 233); rollout restart: `ok=300 err=0`; แบบเปราะ 3 รอบ: `ok=297 err=3 (502×2, 000×1)`, `ok=295 err=5 (502×4, 000×1)`, `ok=297 err=3 (502×2, 000×1)`; คืนค่าแล้ว err=0; `kubectl delete ns ingress-demo` 27 วิ |
| 10 som-shop-v8 | ✅ | hit.sh 15.4 วิ/250, 18.5 วิ/300 | `lab10.log`, `lab10-final-state.log`, `browser-check.log`, `host-final.log` | A: `service/som-web created` (ClusterIP), `statefulset.apps/som-db configured`, ลบ som-https; B: ใบเดิม `CN = shop.som.local` → ใบใหม่ SAN shop/admin/localhost (Warning missing last-applied); C: 2 Ingress `80, 443` ADDRESS localhost; D: 301 → `https://shop.localhost:30081/`, orders=3 → POST `order_id 4` → orders=4, `productId` → `ข้อมูลไม่ถูกต้อง`, admin 301/401/200 + `/stats`, ประตูเดิม `localhost:30080/api/stats` → 404; E: footer ใหม่หลัง restart, restart `ok=250 err=0`, set image 1.6 `ok=300 err=0 (1.5×213 / 1.6×87)`, history 3 แถว; Chromium จริง: 301 → 200 title `ร้านอาหารแมวน้องส้ม`, admin 401/200 |
| เสริม Gateway API | ✅ | CRD 0.97 วิ | `labx-gateway.log` | 10 CRD + ValidatingAdmissionPolicy `safe-upgrades`; GatewayClass `ACCEPTED True`; Gateway `PROGRAMMED True` (`Accepted=True Programmed=True`); 40 ครั้ง × 2 รอบ = **36 : 4** ทั้งสองรอบ; restart Traefik มี `ERR middleware "som-shop-…@kubernetescrd" does not exist` 4 บรรทัดชั่วครู่แล้วหาย; คืนสภาพครบ (CRD 0, redirect/auth ยังทำงาน) |
| ภาพ T06 LoadBalancer | ✅ | — | `extra-T06-loadbalancer.log` | `lbtest LoadBalancer 10.96.3.87 <pending> 80:30265/TCP` |
| SSH | ✅ | — | `ssh-check.log` | password + key `devtoolSSH` ที่ 2224 |

### จุดที่ต้องยืนยันตามแผน (ข้อ 8)

| # | เรื่อง | ผล |
|---|---|---|
| 1 | browser ของนักศึกษา | ยืนยันได้เฉพาะ Chromium (Playwright 1.63, Linux) ผ่าน `--host-resolver-rules` ไป gateway — **ยังไม่ได้ทดสอบ** Chrome/Edge บน Windows/macOS, Firefox, Safari, และ Docker Desktop ฟัง `::1` (ทำจากเครื่องนี้ไม่ได้); curl ใน k8s-lab ลอง `[::1]` ก่อนแล้ว fallback 127.0.0.1 เอง |
| 2 | redirect ไม่ตั้ง port | **ยืนยันแล้ว**: `Location: https://shop.localhost/menu?x=1` (ไม่มีพอร์ต = 443) `curl -L` → rc=7 |
| 3 | namespace จริง `ingress-demo` + รันทั้งบท | ✅ ทุก LAB ใช้ `ingress-demo` ชื่อ middleware `ingress-demo-redirect-https@kubernetescrd` ฯลฯ |
| 4 | hit.sh https + CURL_OPTS | ✅ ค่าเริ่ม `https://shop.localhost:30081/api/whoami` + `CURL_OPTS` (ค่าเริ่ม `-k`) ทดสอบ 4 แบบ: เริ่มต้น ok=60, `--cacert tls.crt` ok=12, `-k --resolve …` ok=6, `CURL_OPTS=" "` → err=2 `curl: (60)` |
| 5 | จำนวน 502 แบบเปราะ | 3–5 ครั้ง/300 (502 2–4 ครั้ง + 000 1 ครั้ง) ทุกรอบ — ใช้คำว่า "อาจเห็น" ตามแผน |
| 6 | orders ใน LAB 10 | เริ่ม 3 (จำลองบท 011) จบ 4 — ภาพไม่ระบุตัวเลขถูกแล้ว (นักศึกษาที่ทำบท 011 ครบจะเริ่มที่ 5) |
| 7 | ภาพ needs_test | ตรวจครบ 47 ภาพ ดูหัวข้อ "ป้ายภาพ" |
| 8 | ไฟล์ CRD สำเนา 248 KB | `kubectl apply -f` ธรรมดาผ่าน (ไม่ติด annotation too long) 0.18 วิ |
| 9 | RBAC ตัด `pods get` | ทำงานปกติ ERR=0 |

## การเปลี่ยนแปลงจากแผน

1. **ไม่ได้เขียน `02_LAB/README.md`** — งานนี้สร้าง manifest/สคริปต์ + log; README ต้องเขียนจาก log ชุดนี้
2. **`/api` ของ whoami ตอบ JSON** (endpoint พิเศษของ `traefik/whoami`) → ตาราง/คำสั่งที่ `grep 'Name:'` จะว่างที่ `/api` พอดี: แก้ `try-paths.sh` ให้ดึง `"name"` จาก JSON (แสดง `Name: api (JSON)`) และใน README ให้ใช้ `/api/stats` หรือ `/api/` เป็นตัวอย่างหลัก
3. **`/API` → 404** ในตาราง LAB 5 (ชื่อ paths.localhost ไม่มีกฎ `/`) ไม่ใช่ menu แบบ pre-check (ที่ทดสอบบน shop.localhost ซึ่งมี `/` → menu)
4. **defaultBackend + endpoint ว่าง**: ด้วย `allowEmptyServices=true` (ไฟล์ของบท) Service ที่ scale 0 ได้ **503** แม้มี lost อยู่ — ไม่ไหลไป admin (ข้อความในแผนข้อ 2 ใช้ได้กับค่าเริ่มต้นของ Traefik เท่านั้น)
5. ไฟล์ LAB 8 เพิ่ม `redirect-noport.yaml` (ลองผิด) และ LAB 9 ใช้ไฟล์ `menu-v2.yaml` / `menu-fragile.yaml` แทน `kubectl set` (whoami ใช้ `--name` ใน args เปลี่ยนด้วย `set image/env` ไม่ได้)
6. LAB 1 ลองผิดใช้ `kubectl create service nodeport probe --tcp=80:80 --node-port=30080` (สั้นกว่า) ส่วนกรณี "ร้านบท 011 ยังจอง 30080" + "ลืม CRD" ทดสอบแยกใน `lab01-wrong-order.log` แล้วล้างทิ้งก่อนทำ LAB 1 ตามลำดับที่ถูก (Traefik image ถูกดึงครั้งแรกในรอบนั้น LAB 1 จึงเห็น `already present on machine` — เวลา pull จริงใช้ค่า pre-check 7.4 วิ)
7. LAB 0 ของนักศึกษาที่มาจากบท 011: build แค่ `som-shop-web:1.6` (1.5 มีอยู่แล้ว) — build 1.5 ซ้ำจาก `som-shop-v8/app` ได้ image ID ใหม่ (ไม่กระทบ Pod เดิม) ให้ทำเฉพาะคลัสเตอร์ใหม่
8. **ต้องเก็บกวาด LAB 1–9 (`kubectl delete ns ingress-demo`) ก่อน LAB 10** เพราะป้าย `shop` ของ ingress-demo ใช้ชื่อ shop.localhost ซ้ำกับร้าน (ไม่ได้ทดลองให้ชนจริง — ใส่เป็นขั้นบังคับ)
9. `hit.sh -q` สรุปตามเวอร์ชัน (`250 1.5 (เวอร์ชัน)`) แทนการไม่พิมพ์สรุปแบบ v7
10. ทุกครั้งที่ Traefik restart (LAB 5, 7, เสริม) ตอนมี Ingress ที่อ้าง Middleware จะมี `ERR … middleware "…@kubernetescrd" does not exist` ชั่วครู่ (provider Ingress โหลดก่อน CRD) — ไม่กระทบหลังจากนั้น
11. คอมเมนต์ใน `som-shop-v8/k8s/*.yaml` แก้จาก "LAB 9 บท 011" เป็น "LAB 10 บท 012" (เนื้อ YAML = precheck)

## ไฟล์ที่สร้าง (`012_kubernetes_ingress/02_LAB/`)

`.gitignore` · `ingress-controller/{traefik-crds-v3.7.13.yml,00-traefik.yaml}` · `lab02-first/{10-apps.yaml,20-ingress.yaml}` · `lab03-fanout/ingress.yaml` · `lab04-hosts/ingress.yaml` · `lab05-pathtype/{ingress.yaml,try-paths.sh}` · `lab06-debug/{wrongclass,typo,lost}.yaml` · `lab07-tls/ingress-tls.yaml` · `lab08-middleware/{redirect,redirect-noport,admin-auth,strip}.yaml` · `lab09-rolling/{loop.sh,menu-v2.yaml,menu-fragile.yaml}` · `labx-gateway/{gateway-rbac.yml,60-gateway.yaml}` · `som-shop-v8/{.gitignore,hit.sh,app/ (สำเนา v7 ไม่แก้โค้ด ไม่มี node_modules/.next),k8s/{00-namespace,10-db,15-config,20-web,40-admin,50-ingress}.yaml}` — ไม่มี `tls.key`/`tls.crt` ในเครื่อง (สร้างใน container เท่านั้น)

## ป้าย/ข้อความในภาพ storyboard ที่ไม่ตรงผลจริง

| ภาพ | ส่วน | ปัจจุบัน | ควรใช้ |
|---|---|---|---|
| **L14** | caption_th | "ทุกชื่อที่ไม่ตรงกฎ — และกฎที่ Service ไม่มี endpoint — ไหลไปโต๊ะของหาย (admin)" | "ทุกชื่อที่ไม่ตรงกฎ (other/typo/class ผิด/ไม่มี Host) ไหลไปโต๊ะของหาย (admin) …" — ตัด "และกฎที่ Service ไม่มี endpoint" (ทดสอบจริง menu=0 ได้ 503 เพราะ `allowEmptyServices=true`) |
| **T47** | caption_th | "(pre-check เจอ 3–6 ครั้งจาก 300)" | "(ทดสอบจริงเจอ err 3–5 ครั้งจาก 300: 502 Bad Gateway และ curl ต่อไม่ได้)" หรือไม่ระบุตัวเลข |
| T23 | label 2 + caption | "Chrome / Edge / curl"; "ทดสอบแล้วใน Chromium 153 และ curl 8.5" | ยืนยันแล้วเฉพาะ Chromium + curl; Edge/Chrome บน Windows/macOS ยังไม่ได้ทดสอบ — ถ้าต้องการตรงผลจริงใช้ "Chromium / curl" หรือคงไว้แต่ README ต้องระบุว่ายังไม่ได้ลอง Edge/Safari/Firefox; curl ลอง `::1` ก่อน แล้วต่อ 127.0.0.1 (label 1 ใช้ได้) |
| T24 | label 1 / caption | "curl -H 'Host: shop.localhost'" | ใช้ได้กับ **HTTP** เท่านั้น — บน HTTPS ที่มี redirect middleware ต้องใส่พอร์ตด้วย (`-H 'Host: shop.localhost:30081'`) ไม่งั้นได้ 301 วน; caption ควรเพิ่ม "(HTTPS ใช้ --resolve)" |
| T09 | label 4 | "เทียบชื่อโดยไม่สนพอร์ต" | ถูกสำหรับการเลือกกฎ (ใช้ได้) แต่ README ต้องบอกว่า Middleware redirectScheme ดูพอร์ตใน Host |
| L03 | caption_th | "ดึง image จาก Docker Hub ได้ตรง ~7 วิ" | รอบนี้ image อยู่ใน cache แล้ว (rollout 3.7 วิ) ค่า ~7 วิ มาจาก pre-check — คงไว้ได้ |
| L11 | ตารางในภาพ | ไม่มี `/API` | ถ้าเพิ่ม `/API` ในภาพต้องเป็น `404` (paths.localhost) |
| L20 | caption_th | "rollout restart สองรอบ" | ทดสอบจริง 3 รอบ ได้ 502 ทุกรอบ — "สองรอบ" ยังใช้ได้ถ้า README ทำ 2 รอบ |
| L31 | label 3 | "36 : 4" | ผลจริงรอบนี้ **36 : 4 ทั้งสองรอบ** (เหมือน pre-check) — คงไว้ได้ แต่ README ต้องบอกว่าสุ่มได้ต่างทุกครั้ง |

ภาพ needs_test อื่นตรงผลจริง: T06 (`<pending>`), T17, T18, T20, T26, T28, T29, T30, T31, T32 (`no available server`), T34, T35, T36, T37, T40, T41, T42 (entrypoints :8000/:8443/:8080), T43 (ข้อความตรงทุกตัวอักษร), T44 (`Failed to watch`), T45 (`Events: <none>`), T46, L01, L04, L06, L08, L09, L13, L16, L18, L19, L22–L28, L30

## ข้อควรระวังสำหรับนักศึกษา (สำหรับ README/Troubleshooting)

1. **CRD ก่อน controller** ถ้าพลาดเห็น `Failed to watch … could not find the requested resource (get middlewaretcps.traefik.io)` → `kubectl apply -f ingress-controller/traefik-crds-v3.7.13.yml` แล้ว `kubectl -n traefik rollout restart deploy/traefik`
2. **คืนพอร์ตก่อนติดตั้ง** (`provided port is already allocated`) — ลบเฉพาะ Service ของร้านบท 011 แล้ว apply 00-traefik.yaml ซ้ำ (ส่วนอื่นที่ created แล้วไม่ต้องลบ)
3. `/api` ของ whoami ตอบ JSON ไม่ใช่ข้อความ `Name:` (ยังถูกส่งไป api ถูกต้อง)
4. หลัง `scale`/`rollout` เสร็จ ให้รอ 2–3 วินาที Traefik ถึงเห็น EndpointSlice ใหม่ (เจอ 503 ครั้งเดียวทันทีหลัง rollout status จบ) และหลัง rollout Pod เก่ายังตอบได้ช่วง preStop 5 วิ
5. `lost.yaml` (defaultBackend) ต้องลบทันทีหลังทดลอง ไม่งั้นทุกชื่อที่ผิดจะเข้า admin แทน 404
6. Host header บน HTTPS ต้องมีพอร์ต (`shop.localhost:30081`) หรือใช้ `--resolve` เพราะ redirectScheme เทียบพอร์ต — เช่นเดียวกับการ tunnel ด้วยพอร์ตอื่น (`ssh -L 8443:localhost:30081`) จะถูก redirect กลับ 30081
7. redirectScheme ต้องใส่ `port: "30081"` (ไม่ใส่ → `https://shop.localhost/…` พอร์ต 443 ที่ไม่มี)
8. ต้อง `--entryPoints.websecure.http.tls=true` ไม่งั้น https ได้ `HTTP/2 404` ทั้งที่ใบรับรองถูก
9. ชื่อ `*.localhost` ใช้ได้กับ curl/Chromium แต่ `getent`/wget/python หาไม่เจอ (rc=2) → `curl -H`/`--resolve`/แก้ hosts
10. `kubectl delete ns ingress-demo` ใช้ราว 27 วิ (preStop 5 วิ) ต้องทำก่อน LAB 10
11. LAB 10 ขั้น B: Warning `missing the kubectl.kubernetes.io/last-applied-configuration annotation` ปกติ; POST ต้องใช้ `product_id` (`productId` → `ข้อมูลไม่ถูกต้อง`)
12. ป้ายร้านบท 012 มีผลหลัง `rollout restart` เท่านั้น (apply 15-config.yaml อย่างเดียวไม่เปลี่ยน)
13. dashboard `--api.insecure=true` ใช้เฉพาะ LAB
