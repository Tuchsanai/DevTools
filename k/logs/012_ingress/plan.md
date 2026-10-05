# แผนบท 012 Kubernetes Ingress (5 ต.ค. 2569)

> สถานะ: แผน + storyboard ภาพ (ยังไม่เขียน README/ไฟล์ LAB ฉบับจริง) — pre-check รันจริงใน `k8s-lab-ingress012-961878` แล้ว **ลบทิ้งแล้ว**
> manifest ที่ทดสอบผ่านเก็บไว้ที่ `logs/012_ingress/precheck/` (ใช้เป็นต้นแบบตอนเขียน LAB จริง)

## 0. สรุปการตัดสินใจ

| เรื่อง | ตัดสินใจ | เหตุผลสั้น ๆ |
|-------|---------|-------------|
| Controller | **Traefik v3.7.13** (`traefik:v3.7.13`, release 4 ก.ย. 2026) ติดตั้งด้วย static manifest `00-traefik.yaml` ของบทเอง + CRD ทางการที่ pin tag `v3.7.13` | ยังดูแลอยู่ (v3.7.x ออกแพตช์ทุก 1–2 สัปดาห์), image ทางการ node ของ kind ดึงเองได้ (7.4 วิ ไม่ต้อง kind load), ไม่ต้องใช้ Helm, รองรับ Ingress `networking.k8s.io/v1` + IngressClass + spec.tls และ Gateway API v1.6.2 ใน binary เดียว (ใช้ปูทาง LAB เสริมได้), basicAuth อ่าน Secret `kubernetes.io/basic-auth` ได้ตรง ๆ (ต่อบท 011) |
| ingress-nginx | ไม่ใช้ใน LAB สอนเป็นประวัติ + คำเตือน | repo archive 24 มี.ค. 2026, ไม่มี release/แพตช์ความปลอดภัยอีก, v1.15.1 (ตัวสุดท้าย) รองรับถึง k8s 1.35 แต่คลัสเตอร์นักศึกษาเป็น v1.37 |
| พอร์ต | `web` → NodePort **30080**, `websecure` → **30081**, dashboard (อ่านอย่างเดียว, `api.insecure` เฉพาะ LAB) → **30082** | kind-lab.yaml map แค่ 30080–30082 ไม่มี 80/443; 30081 เคยเป็นพอร์ต HTTPS ของ LAB4 บท 011 (`ngx-tls`) นักศึกษาคุ้น; 30080 = พอร์ตที่ลูกค้าคุ้นของร้าน; ทั้ง 3 พอร์ตต้องคืนจากร้านบท 011 ก่อน (LAB 0) |
| ชื่อโฮสต์ | `shop.localhost`, `admin.localhost` (+ `paths.localhost`, `other.localhost` ใน LAB ย่อย) | Chromium/curl แปลง `*.localhost` → loopback เอง ไม่ต้องแก้ hosts (ยืนยันแล้ว ดูข้อ 2) |
| แอปทดสอบ LAB 1–9 | `traefik/whoami:v1.11.0` (3 MB, node ดึงเอง 1.5 วิ) ชื่อ menu/api/admin | ตอบกลับ `Name:` + บรรทัด `GET /path` + header `Host`/`X-Forwarded-*` → เห็นผล routing ชัด |
| LAB สุดท้าย | `som-shop-v8` = สำเนา som-shop-v7 บท 011 (image `som-shop-web:1.5` + `1.6` build-arg เท่านั้น ไม่แก้โค้ด, ห้าม tag 1.4) | ทดสอบผ่านครบทุกขั้นรวม browser |

## 1. ข้อ 1 — สถานะ ingress-nginx และการเลือก controller

**ข้อเท็จจริงจากแหล่งทางการ (ตรวจ 5 ต.ค. 2569):**

- Kubernetes blog "Ingress NGINX Retirement: What You Need to Know" (11 พ.ย. 2025, SIG Network + Security Response Committee): *"Best-effort maintenance will continue until March 2026. Afterward, there will be no further releases, no bugfixes, and no updates to resolve any security vulnerabilities that may be discovered."* และ *"Existing deployments of Ingress NGINX will continue to function and installation artifacts will remain available."* แนะนำย้ายไป Gateway API หรือ Ingress controller ตัวอื่น — https://kubernetes.io/blog/2025/11/11/ingress-nginx-retirement/
- Statement จาก Steering + SRC (29 ม.ค. 2026) ย้ำให้เริ่มย้ายทันที — https://kubernetes.io/blog/2026/01/29/ingress-nginx-statement/
- GitHub `kubernetes/ingress-nginx`: **archived 24 มี.ค. 2026 (read-only)**, README: *"If you are not already using ingress-nginx, you should not be deploying it"*, เวอร์ชันสุดท้าย v1.15.1 (k8s 1.31–1.35, chart 4.15.1), image/chart เดิมยังดาวน์โหลดได้ — https://github.com/kubernetes/ingress-nginx
- บทความประกอบ: "Before You Migrate: Five Surprising Ingress-NGINX Behaviors" (27 ก.พ. 2026) https://kubernetes.io/blog/2026/02/27/ingress-nginx-before-you-migrate/ และ "Ingress2Gateway 1.0" (20 มี.ค. 2026) https://kubernetes.io/blog/2026/03/20/ingress2gateway-1-0-release/
- Traefik releases: v3.7.13 (4 ก.ย. 2026, latest stable; ก่อนหน้า v3.7.12 26 ส.ค., v3.6.25 31 ก.ค.) — https://github.com/traefik/traefik/releases
- Traefik Kubernetes Ingress provider docs — https://doc.traefik.io/traefik/reference/install-configuration/providers/kubernetes/kubernetes-ingress/
- Traefik Gateway API provider: รองรับ Gateway API **v1.6.2** (`standard-install.yaml`) — https://doc.traefik.io/traefik/reference/install-configuration/providers/kubernetes/kubernetes-gateway/
- CRD/RBAC ที่ pin: `https://raw.githubusercontent.com/traefik/traefik/v3.7.13/docs/content/reference/dynamic-configuration/kubernetes-crd-definition-v1.yml` (10 CRD, 248 KB, `kubectl apply` ธรรมดาผ่าน), `.../kubernetes-crd-rbac.yml` (ใช้เป็นต้นแบบ ClusterRole ของบท โดยเปลี่ยน SA เป็น `traefik/traefik`)

**เทียบตัวเลือก (เหตุผลที่ไม่เลือก):** HAProxy Ingress / Contour / NGINX Gateway Fabric ยังดูแลอยู่เช่นกัน แต่ Contour ต้องมี Envoy + ปรับ hostPort ของ kind, NGINX Gateway Fabric เป็น Gateway API เป็นหลัก (ไม่ใช่ Ingress), F5 NGINX Ingress Controller ใช้ annotation/CRD ชุดของตัวเองและแนะนำ Helm; Traefik จบในไฟล์ YAML เดียว (Deployment + Service NodePort + IngressClass) จึงเหมาะกับนักศึกษาที่ยังไม่รู้ Helm

**มาตรฐาน vs เฉพาะ Traefik (ต้องแยกใน README ชัด ๆ):**

| มาตรฐาน (ใช้ได้กับทุก controller) | เฉพาะ Traefik |
|---|---|
| `Ingress` `networking.k8s.io/v1`: `rules[].host`, `http.paths[].path/pathType`, `backend.service.name/port.number|name`, `defaultBackend`, `tls[].hosts/secretName` | annotation `traefik.ingress.kubernetes.io/router.middlewares: <ns>-<name>@kubernetescrd` (และ `router.entrypoints`, `router.tls`) |
| `IngressClass` + `ingressclass.kubernetes.io/is-default-class` | CRD `Middleware` (`traefik.io/v1alpha1`): `redirectScheme`, `basicAuth`, `stripPrefix`, `rateLimit` |
| Secret `kubernetes.io/tls`, `kubernetes.io/basic-auth` | flag ของ controller: `--providers.kubernetesingress.strictPrefixMatching`, `allowEmptyServices`, `--entryPoints.websecure.http.tls`, `ingressendpoint.hostname` |
| Gateway API (`GatewayClass`/`Gateway`/`HTTPRoute`) | `IngressRoute`/`TraefikService` (ไม่สอน แค่กล่าวถึง) |

## 2. ผล pre-check (ทดลองจริง)

- container: `k8s-lab-ingress012-961878` (owner `agent-012`, image `8108a1bc7901` = `tuchsanai/devtools-kind:2569_1`, NodePort 30080–30082 → host 30090–30092, ไม่ publish SSH) — kind v1.37.0 3 Node Ready, kubectl v1.37.1 — **ลบแล้ว** (`removed`, `k8s-lab.sh ls` ว่าง; ไม่ได้แตะ `k8s-lab` ของผู้เรียน/`deep_vision_5090_vllm`; lock/TMPDIR อยู่ใน `scratch/t`)

### ข้อ 2 — `*.localhost` และวิธีสำรอง

| ทดสอบ | ผลจริง |
|------|-------|
| Chromium 153.0.8010.12 (Playwright บนเครื่อง agent) เปิด `http://shop.localhost:18080/`, `admin.localhost`, `a.b.localhost` ไป http.server ที่ 127.0.0.1 **โดยไม่มีบรรทัดใน /etc/hosts** | **200 ทั้ง 3 ชื่อ** → Chromium แปลง `*.localhost` → loopback เอง |
| curl 8.5.0 `http://shop.localhost:...` | `Trying [::1]` แล้ว `Connected to shop.localhost (127.0.0.1)` → curl แปลงเอง (ใน k8s-lab ก็ใช้ได้: `curl http://shop.localhost:30080/` ได้ `Name: menu`) |
| `getent hosts shop.localhost` (glibc) | **ไม่พบ (rc=2)** → โปรแกรมที่ใช้ resolver ของระบบ (wget, python requests, Node fetch) หาไม่เจอ — Playwright APIRequest (Node) ได้ `getaddrinfo ENOTFOUND shop.localhost` เช่นกัน |
| curl ส่ง Host | `Host: shop.localhost:30080` (มีพอร์ต) — Traefik เทียบ host โดยตัดพอร์ตออกเอง ใช้ได้ |
| `curl -H 'Host: shop.localhost' localhost:30080` | ได้ผลเท่ากับใช้ชื่อ (วิธีสำรองหลักใน README) |
| `curl --resolve shop.localhost:30081:127.0.0.1 --cacert tls.crt https://shop.localhost:30081/` | ผ่าน (SNI ถูก) |
| End-to-end browser: Chromium + `--host-resolver-rules="MAP shop.localhost:30080 <gateway>:30090, ..."` (จำลองพอร์ตของนักศึกษา ไม่แตะพอร์ตจริงของ k8s-lab ผู้เรียน) | `http://shop.localhost:30080/` → **301** → `https://shop.localhost:30081/` → 200 title `ร้านอาหารแมวน้องส้ม` footer `… Kubernetes LAB 012 · เข้าร้านทาง Ingress https://shop.localhost`; `https://admin.localhost:30081/` ไม่มีบัตร 401, มีบัตร 200 `หลังร้านน้องส้ม (admin)`, `/stats` → `som-web-… 1.6 orders=4 products=6` |

วิธีสำรองใน README: (1) `curl -H 'Host: …'` (2) `curl --resolve` (3) แก้ hosts (`C:\Windows\System32\drivers\etc\hosts` / `/etc/hosts`: `127.0.0.1 shop.localhost admin.localhost`) เฉพาะเมื่อ browser/โปรแกรมไม่แปลงให้

### ข้อ 3 — image ของ controller

| image | ผล |
|------|----|
| `traefik:v3.7.13` | node ดึงเองจาก Docker Hub `Successfully pulled image "traefik:v3.7.13" in 7.42s … 55222642 bytes` — **ไม่ต้อง kind load** |
| `traefik/whoami:v1.11.0` | ดึงเอง 1.5 วิ (3 MB) |
| `nginxinc/nginx-unprivileged:1.27-alpine` | ดึงเอง (ใช้กับ som-admin ผ่าน PSA restricted ไม่มี Warning) |
| `postgres:17.11-alpine` | ตามบทเรียนเดิม: `docker pull` + `docker save --platform linux/amd64` + `kind load image-archive` (16 วิ) |
| `som-shop-web:1.5`, `1.6` | `docker build --build-arg APP_VERSION=…` + `kind load docker-image` (สองตัวรวม 35 วิ) |
| CRD จาก raw.githubusercontent.com (tag v3.7.13) และ Gateway API v1.6.2 จาก github releases | apply จากใน container ได้ (ต้องมีอินเทอร์เน็ต) — **ให้สำเนาไฟล์ CRD ไว้ในโฟลเดอร์บทด้วย** เผื่อ github ช้า/บล็อก |

### ผลอื่นที่ยืนยันแล้ว (ใช้เขียน LAB/ภาพ)

| เรื่อง | ผลจริง |
|-------|-------|
| ลำดับติดตั้ง | ถ้า apply controller ก่อน CRD → log `Failed to watch … the server could not find the requested resource (get tlsoptions.traefik.io)` ซ้ำ ๆ → **CRD ก่อนเสมอ** (แล้ว rollout restart ถ้าพลาด) |
| rollout Traefik | 8.5 วิ; `kubectl get ingressclass` → `traefik (default)   traefik.io/ingress-controller` |
| ยังไม่มี Ingress | `curl localhost:30080` → `404 page not found`; dashboard `localhost:30082/dashboard/` → 200, `/api/version` → `{"Version":"3.7.13","Codename":"langres",…}` |
| ADDRESS | ใช้ `--providers.kubernetesingress.ingressendpoint.hostname=localhost` → `kubectl get ing` ADDRESS = `localhost`, status `loadBalancer.ingress[0].hostname: localhost` |
| default class | Ingress ที่ไม่ใส่ `ingressClassName` ถูกเติม `traefik` ตอนสร้าง |
| class ผิด (`nginx`) | CLASS `nginx` ADDRESS ว่าง, Traefik ไม่สร้าง router |
| fan-out | `/api/stats` → api และ path ไม่ถูกตัด (`GET /api/stats`), `/order` → menu, `/admin/x` → admin; port อ้างด้วย `number: 80` หรือ `name: http` ได้ทั้งคู่ |
| host-based | `admin.localhost /` → admin, `other.localhost` → 404, ไม่มี Host → 404 |
| **pathType (ค่าเริ่มต้น Traefik)** | **ไม่ตรงมาตรฐาน**: Prefix `/api` จับ `/apix` ด้วย, Prefix `/docs/` ไม่รับ `/docs` |
| **pathType + `strictPrefixMatching=true`** (ใช้ในไฟล์บท) | `/api` `/api/` `/api/x` → api, `/apix` → 404, `/API` → menu (case-sensitive), `/docs` `/docs/` `/docs/a` → 200, `/docsx` → 404, Exact `/menu` → 200 แต่ `/menu/` `/menux` → 404, ImplementationSpecific `/impl` ทำแบบ Prefix: `/impl/x` 200 `/implx` 404; router rule ที่เห็นใน dashboard `Host("paths.localhost") && (Path("/api") \|\| PathPrefix("/api/"))` |
| Service ชื่อผิด | describe: `menuu:80 (<error: services "menuu" not found>)`, Events `<none>`, log `ERR Cannot create service error="service not found" ingress=typo … serviceName=menuu` |
| port ผิด | describe `menu:8080 ()`, log `ERR … error="service port not found"` |
| endpoints ว่าง (scale 0) | ค่าเริ่มต้น: router ถูกตัด → **404** (หรือไหลไป defaultBackend); `--providers.kubernetesingress.allowEmptyServices=true` (ใช้ในไฟล์บท) → **`503 no available server`**, access log `"GET / HTTP/1.1" 503 20 … "demo-shop-shop-localhost@kubernetes"` |
| defaultBackend | Ingress ที่มีแค่ `spec.defaultBackend` (HOSTS `*`) = **catch-all ของทั้ง controller** — ชื่อที่ไม่ตรงทุกชื่อ, class `nginx`, Service ที่หายไป, Service ที่ไม่มี endpoint → ไหลไป admin หมด → LAB ต้องลบทิ้งหลังทดลอง |
| NodePort ชน | `The Service "traefik" is invalid: spec.ports[0].nodePort: Invalid value: 30080: provided port is already allocated` (ทั้งตอนติดตั้ง Traefik ทับร้านบท 011 และสร้าง Service อื่นทับ Traefik) |
| TLS (ไม่มี flag) | spec.tls โหลดใบรับรองได้ (SNI shop → `subject=CN = shop.localhost`) แต่ router ไม่เป็น TLS → `https://` ได้ **HTTP/2 404** → ต้องใส่ `--entryPoints.websecure.http.tls=true` (ไฟล์บทใส่แล้ว; Ingress จึงไม่ต้องมี annotation) |
| TLS (มี flag) | `-k` ได้ menu; ไม่มี -k → `rc=60`; `--cacert tls.crt` ผ่านทั้ง shop/admin; header `X-Forwarded-Proto: https`, `X-Forwarded-Port: 30081`; SNI ชื่ออื่น → `subject=CN = TRAEFIK DEFAULT CERT` (`--cacert` → rc=60, `-k` → 404); `https://127.0.0.1:30081` → rc=60 (ไม่อยู่ใน SAN); Ingress ที่ไม่มี spec.tls ก็ตอบบน 30081 ด้วยใบ DEFAULT; `http://localhost:30081/` → `HTTP/1.1 404` (ไม่ใช่ 400 แบบ nginx บท 011) |
| Ingress เดียวทั้ง HTTP/HTTPS | ไม่ใส่ `router.entrypoints` → router อยู่ทั้ง `web` และ `websecure` |
| redirect | Middleware `redirectScheme {scheme: https, port: "30081", permanent: true}` → `HTTP/1.1 301 Moved Permanently` `Location: https://shop.localhost:30081/menu?x=1` (เก็บ path+query); บน https ไม่วนซ้ำ (200); **ถ้าไม่กำหนด port จะชี้ :443 ที่นักศึกษาไม่มี** (ทฤษฎี — ยังไม่ได้ยิงยืนยัน ดูข้อ 9) |
| basicAuth | Secret `type: kubernetes.io/basic-auth` (username/password ข้อความธรรมดา) ใช้ได้ตรง: ไม่มีบัตร `HTTP/2 401` + `www-authenticate: Basic realm="traefik"`, ผิด 401, ถูก 200; ไม่ใส่ `removeHeader: true` แอปจะเห็น `Authorization: Basic …` (ร้านใส่ `removeHeader: true`) |
| stripPrefix | `/admin/orders` → แอปเห็น `GET /orders`, `X-Forwarded-Prefix: /admin`; `/adminx` ไม่เข้า (ไป `/` menu) |
| rolling update (readiness + `preStop sleep 5` + maxUnavailable 0) | curl https วน 300 ครั้ง: **ok=300 err=0** (menu 69 / menu-v2 231) |
| ไม่มี readiness/preStop + maxUnavailable 1 | rollout restart 2 รอบ: `ok=293 err=7 (6×502, 1×000)` และ `ok=296 err=4 (3×502, 1×000)` |
| Gateway API (LAB เสริม) | `kubectl apply --server-side -f …/v1.6.2/standard-install.yaml` + RBAC `kubernetes-gateway-rbac.yml` (v3.7.13, แก้ SA) + `--providers.kubernetesgateway=true` → GatewayClass `ACCEPTED True` (controllerName `traefik.io/gateway-controller`), Gateway listener `port: 8000` (= entrypoint web) `PROGRAMMED True`; HTTPRoute weight 90/10 som-web/som-admin ยิง 40 ครั้ง → **36 : 4**; ตอน restart Traefik มี `ERR middleware … does not exist` ชั่วครู่ (หายเอง ไม่กระทบ) |

## 3. ไฟล์ controller ของบท (`02_LAB/ingress-controller/`)

- `traefik-crds-v3.7.13.yml` (สำเนาจาก tag v3.7.13 ไม่แก้) + คำสั่งออนไลน์ทางเลือก
- `00-traefik.yaml` (= `precheck/00-traefik.yaml`): Namespace `traefik`, SA `traefik`, ClusterRole/Binding `traefik` (ตาม upstream), Deployment 1 replica `traefik:v3.7.13` runAsNonRoot 65532 readOnlyRootFilesystem drop ALL (ผ่าน PSA restricted), args:
  `--entryPoints.web.address=:8000`, `--entryPoints.websecure.address=:8443`, `--entryPoints.traefik.address=:8080`, `--entryPoints.websecure.http.tls=true`, `--providers.kubernetesingress=true`, `--providers.kubernetesingress.strictPrefixMatching=true`, `--providers.kubernetesingress.allowEmptyServices=true`, `--providers.kubernetesingress.ingressendpoint.hostname=localhost`, `--providers.kubernetescrd=true`, `--api.dashboard=true`, `--api.insecure=true` (LAB เท่านั้น), `--ping=true` (readiness `/ping`), `--accesslog=true`, `--log.level=INFO`, `--global.checknewversion=false`, `--global.sendanonymoususage=false`; Service NodePort web 80→30080, websecure 443→30081, dashboard 8080→30082; IngressClass `traefik` (default)
- log เตือนที่เห็นทุกครั้ง (อธิบายว่าไม่ใช่ error): `WRN … encoded characters`, `WRN aliasHeadersStrategy is not configured`, `WRN SafeNaming is not explicitly set`
- LAB เสริมเพิ่ม `gateway-rbac.yml` + patch arg `--providers.kubernetesgateway=true`

## 4. สารบัญทฤษฎี (01_Theory/README.md) — 53 ภาพ (T01–T53)

1. **บทนำ: ร้านมีหลายประตู ลูกค้าจำไม่ไหว** (T01–T04) — ต่อบท 011: NodePort 30080 + HTTPS 30082, หน้าแอดมินจะเพิ่มพอร์ตอีก; อุปมาใหม่; เป้าหมาย shop.localhost / admin.localhost
2. **ทำไมต้องมี Ingress** (T05–T07) — NodePort ต่อ Service (30000–32767, เปิดทุก Node), LoadBalancer ต่อ Service (คลาวด์คิดเงินทุกตัว, kind = `<pending>`), Ingress = ทางเข้าเดียว + Service ClusterIP
3. **L4 กับ L7** (T08–T09) — Service/kube-proxy ดู IP:port; controller อ่าน HTTP: method, path, Host (มีพอร์ต), header; ผลคือเลือกปลายทาง/แก้คำขอได้
4. **Ingress resource vs Ingress controller** (T10–T13) — ป้ายไม่มีพนักงาน = ไม่ทำงาน; controller watch Ingress/Service/EndpointSlice/Secret แล้วปรับเอง (ไม่ restart); controller ก็คือ Deployment+Service ใน ns ของตัวเอง; รายชื่อ controller (Traefik, HAProxy Ingress, Contour, NGINX Gateway Fabric, F5 NGINX IC, cloud controllers)
5. **ingress-nginx retirement และการเลือก Traefik** (T14–T15) — ไทม์ไลน์ (ประกาศ 11 พ.ย. 2025 → archive 24 มี.ค. 2026), ผลกระทบ (ยังรันได้แต่ไม่มีแพตช์), คำแนะนำ (Gateway API/controller อื่น, ingress2gateway), เกณฑ์เลือก controller สำหรับ LAB
6. **IngressClass และ default class** (T16–T18) — `spec.controller`, `ingressClassName`, annotation เก่า `kubernetes.io/ingress.class` (deprecated), `is-default-class` และการเติม class ตอนสร้าง, class ผิด → ADDRESS ว่าง, หลาย controller ในคลัสเตอร์เดียว
7. **โครงสร้าง YAML และ backend** (T19–T21) — rules/host/http.paths/backend.service.name + port.number|name (ของ Service ไม่ใช่ containerPort), backend.resource (กล่าวถึง), Service เป็น ClusterIP ได้แล้ว, ingress status ADDRESS
8. **Host-based (name-based virtual hosting)** (T22–T24) — Host header, wildcard host `*.example.com` (ทีละ 1 ระดับ), `*.localhost` → loopback (Chromium/curl ใช่, glibc ไม่ใช่), วิธีสำรอง
9. **Path-based fan-out** (T25–T26) — หลาย path หลาย Service, ลำดับความสำคัญ (Exact ก่อน Prefix, path ยาวกว่าชนะ), path ไม่ถูกตัด (ต้อง rewrite เอง)
10. **pathType** (T27–T30) — Prefix (ตรงทีละท่อน, ไม่สน / ท้าย, case-sensitive), Exact, ImplementationSpecific; ตารางผลจริง `/api` vs `/api/` vs `/apix` vs `/API`; Traefik ต้อง `strictPrefixMatching` (ค่าเริ่มต้นไม่ตรงมาตรฐาน — ตัวอย่างว่าทำไมต้องทดสอบ controller จริง)
11. **defaultBackend / 404 / 503 / 502** (T31–T32) — ไม่ตรงกฎ → 404 ของ controller, `spec.defaultBackend` (ใน Traefik = catch-all ทั้งคลัสเตอร์), 503 endpoints ว่าง (`allowEmptyServices`), 502 Pod ปิดกลางคัน
12. **TLS ที่ Ingress** (T33–T35) — `spec.tls[].hosts/secretName`, Secret `kubernetes.io/tls` ต้องอยู่ ns เดียวกับ Ingress, TLS termination + `X-Forwarded-Proto`, SNI, ใบ DEFAULT, SAN หลายชื่อ vs wildcard (`*.localhost` ไม่แนะนำ), self-signed กับ browser, cert-manager (กล่าวถึง)
13. **Redirect HTTP → HTTPS** (T36–T37) — 301/308, ทำที่ controller (Traefik: Middleware `redirectScheme` หรือ entrypoint redirection), กับดักพอร์ต NodePort (ต้องบอก `port: "30081"`), HSTS (กล่าวถึง)
14. **annotation / Middleware เฉพาะ controller** (T38–T41) — ตารางมาตรฐาน vs เฉพาะ, ชื่อ `<ns>-<name>@kubernetescrd`, ลำดับใน annotation = ลำดับด่าน, basicAuth จาก Secret basic-auth (removeHeader), stripPrefix/replacePathRegex (rewrite), rateLimit (สั้น), Traefik provider `kubernetesIngressNginx` ช่วยย้ายจาก annotation ของ nginx (กล่าวถึง)
15. **Traefik บน kind: entrypoint และ NodePort** (T42–T44) — เส้นทาง laptop → k8s-lab → lab-control-plane → Service traefik → Pod; ทำไมไม่มี 80/443, ทางเลือก hostPort/extraPortMappings ใหม่ (ต้องสร้างคลัสเตอร์ใหม่ จึงไม่ใช้), NodePort ชนกับร้านเดิม, ลำดับ CRD → controller → IngressClass
16. **การ debug** (T45) — `kubectl get ing` (CLASS/ADDRESS), `describe` (backend + endpoints, `<error: …>`, Events `<none>`), log ERR ของ controller, access log (router name + status), dashboard/`/api/http/routers`, ไล่จากนอกเข้าใน (DNS → พอร์ต → class → host/path → Service → endpoints → Pod)
17. **readiness / rolling update ผ่าน Ingress** (T46–T47) — controller ใช้ EndpointSlice (ส่งเฉพาะ Ready), preStop + terminationGrace, maxUnavailable 0; ผลจริง err=0 vs 502
18. **canary / weight** (T48) — Ingress มาตรฐานไม่มี weight; ทางเลือก: TraefikService (CRD), canary annotation ของ ingress-nginx เดิม, Gateway API `backendRefs[].weight` (LAB เสริม)
19. **ข้อจำกัดของ Ingress และ Gateway API** (T49–T50) — HTTP เป็นหลัก, annotation ไม่พกพา, ป้ายเดียวหลายทีม; Gateway API: GatewayClass/Gateway/HTTPRoute, แยกบทบาท, `parentRefs`, weight/header match ในตัว, ingress2gateway
20. **เปรียบเทียบ แนวปฏิบัติ สรุป** (T51–T53) — ตาราง NodePort / LoadBalancer / Ingress / Gateway API (ชั้น, จำนวนประตูภายนอก, host/path, TLS, weight, ใครเป็นเจ้าของ), แนวปฏิบัติ (pin เวอร์ชัน, ClusterIP, TLS+redirect, readiness+preStop, ไม่ commit key, ป้องกันหน้าแอดมิน, ไม่เปิด dashboard insecure ในงานจริง), ปูทาง HPA / Helm / Gateway API

## 5. ตาราง LAB (02_LAB/README.md) — 31 ภาพ (L01–L31)

ทุกคำสั่งรันใน k8s-lab (`ssh -p 2223 root@localhost`), โฟลเดอร์ `02_LAB`; LAB 1–9 ใช้ namespace `ingress-demo` (pre-check ใช้ชื่อ `demo` — ตอนเขียนจริงเปลี่ยนชื่อแล้วทดสอบซ้ำ)

| LAB | ชื่อ / เป้าหมาย | ไฟล์ | คำสั่งหลัก | ผลที่ต้องเห็น (pre-check) | ต้องยืนยันตอนเขียนจริง |
|-----|----------------|------|-----------|-------------------------|-----------------------|
| 0 | เตรียม: คืนพอร์ต + โหลด image | — | `kubectl get nodes`; `kubectl get svc -A \| grep 3008`; `kubectl -n som-shop delete svc som-web som-https` (เก็บ Deployment/DB/PVC ไว้); postgres archive + build `som-shop-web:1.5/1.6` + kind load | ไม่มี Service ถือ 30080–30082; image บนทุก Node | สภาพเครื่องนักศึกษาที่ยังไม่เคยทำบท 011 (ไม่มี ns som-shop) → ข้ามได้ |
| 1 | ติดตั้ง Traefik + IngressClass | `ingress-controller/traefik-crds-v3.7.13.yml`, `00-traefik.yaml` | `kubectl apply -f traefik-crds…`; `kubectl apply -f 00-traefik.yaml`; `rollout status`; `get ingressclass`; `curl localhost:30080`; เปิด `http://localhost:30082/dashboard/` | `traefik (default)`; `404 page not found`; dashboard 200; (ลองผิด) `provided port is already allocated` | เวลา pull บนเน็ตนักศึกษา; dashboard ใน browser ของนักศึกษา |
| 2 | Ingress แรก host เดียว | `lab02-first/10-apps.yaml` (menu/api/admin whoami), `20-ingress.yaml` | `curl -H 'Host: shop.localhost' localhost:30080`; `curl http://shop.localhost:30080/`; browser; `kubectl get ing` | `Name: menu`; ไม่มี Host → 404; ADDRESS `localhost`; `Host: shop.localhost:30080` | browser บน Windows/macOS (Chrome/Edge/Firefox/Safari) |
| 3 | path fan-out | `lab03-fanout/ingress.yaml` | ยิง `/`, `/order`, `/api`, `/api/stats`, `/admin/x` | `/api/stats` → `Name: api` `GET /api/stats`; `/order` → menu; port name/number ใช้ได้ | — |
| 4 | host-based | `lab04-hosts/ingress.yaml` (ไม่ใส่ class) | `curl http://admin.localhost:30080/`; `other.localhost`; `kubectl get ing -o jsonpath='{.spec.ingressClassName}'` | admin; 404; `traefik` ถูกเติม | — |
| 5 | pathType | `lab05-pathtype/ingress.yaml` + `try-paths.sh` | ยิง 15 path; (เสริม) patch Traefik ปิด strict แล้วดูต่าง → คืนค่า | ตารางในข้อ 2 (strict) / `/apix` → api เมื่อปิด | ตอนคืนค่าใช้ `kubectl apply -f 00-traefik.yaml` |
| 6 | debug | `lab06-debug/{wrongclass,typo,lost}.yaml` | apply ทีละไฟล์; `describe ing`; `kubectl -n traefik logs deploy/traefik \| grep ERR`; `scale --replicas=0`; access log | ADDRESS ว่าง; `<error: services "menuu" not found>`; `service port not found`; `503 no available server`; defaultBackend จับทุกชื่อ → **ลบทิ้ง** | ลำดับขั้นให้ defaultBackend ไม่ค้างไป LAB อื่น |
| 7 | TLS | `lab07-tls/ingress-tls.yaml` | `openssl req … -subj '/CN=shop.localhost' -addext 'subjectAltName=DNS:shop.localhost,DNS:admin.localhost,DNS:localhost'`; `kubectl -n ingress-demo create secret tls som-tls …`; curl -k / --cacert / --resolve / openssl s_client | rc=60, --cacert ผ่าน, `TRAEFIK DEFAULT CERT`, 127.0.0.1 rc=60, header `X-Forwarded-Proto: https` | browser บนเครื่องนักศึกษา (`NET::ERR_CERT_AUTHORITY_INVALID`) |
| 8 | Middleware (เฉพาะ Traefik) | `lab08-middleware/{redirect,admin-auth,strip}.yaml` | `kubectl create secret generic admin-auth --type=kubernetes.io/basic-auth --from-literal=username=som --from-literal=password=<ตัวอย่าง>`; curl -i http…; curl -u | `301` + `Location: https://shop.localhost:30081/…`; 401/401/200; `GET /orders` + `X-Forwarded-Prefix: /admin` | ทดลองไม่ใส่ `port` ใน redirectScheme → Location ไป :443 (ยังไม่ได้ยิงยืนยัน) |
| 9 | rolling update ผ่าน Ingress | `lab09-rolling/loop.sh` (curl https วน) | วนระหว่าง `kubectl set …`/`rollout restart`; จากนั้นเอา readiness/preStop ออกแล้วทำซ้ำ | มี: `err=0`; ไม่มี: 502 บางครั้ง (3–6/300) | ความถี่ 502 ขึ้นกับเครื่อง → README เขียนว่า "อาจเห็น" |
| 10 | **ร้านน้องส้มมีหน้าร้านเดียวด้วยชื่อโดเมน** | `som-shop-v8/` (ดูข้อ 6) | ดูข้อ 6 | ดูข้อ 6 | ดูข้อ 6 |
| เสริม | ลองชิม Gateway API | `labx-gateway/{gateway-rbac.yml,60-gateway.yaml}` | apply CRD v1.6.2 `--server-side`; patch arg; สร้าง GatewayClass/Gateway/HTTPRoute; ยิง 40 ครั้ง | `ACCEPTED True`, `PROGRAMMED True`, 36 : 4 | ลบ CRD/flag คืนหลังจบ (หรือคงไว้ปูบทหน้า) |

## 6. LAB 10 (LAB สุดท้าย) — "ร้านน้องส้มมีหน้าร้านเดียวด้วยชื่อโดเมน"

**โฟลเดอร์ `02_LAB/som-shop-v8/`** = สำเนา som-shop-v7 (`app/` ไม่แก้โค้ด, `hit.sh`) + `k8s/` ใหม่ (ต้นแบบที่ทดสอบแล้ว: `precheck/som-shop-v8-k8s/`)

| ไฟล์ | ต่างจาก v7 |
|------|-----------|
| `k8s/00-namespace.yaml`, `10-db.yaml` | เหมือนเดิม |
| `k8s/15-config.yaml` | `SHOP_EYEBROW: "⚓ ท่าเรือ Kubernetes · Ingress"`, `SHOP_FOOTER: "Next.js + PostgreSQL · Kubernetes LAB 012 · เข้าร้านทาง Ingress https://shop.localhost"` (แก้คอมเมนต์หัวไฟล์ที่ยังเขียน "บท 011" ด้วย) |
| `k8s/20-web.yaml` | Service `type: ClusterIP` (ไม่มี nodePort), change-cause `1.5 หน้าร้านผ่าน Ingress` (template ไม่เปลี่ยน → ต้อง `rollout restart` ให้ ConfigMap ใหม่มีผล) |
| ~~`30-https.yaml`~~ | **ลบ** — TLS ย้ายไป Ingress |
| `k8s/40-admin.yaml` (ใหม่) | ConfigMap `som-admin-conf` (nginx `listen 8080`, `location = /stats { proxy_pass http://som-web.som-shop.svc.cluster.local/api/stats; }`, `index.html` "หลังร้านน้องส้ม (admin)") + Deployment `som-admin` `nginxinc/nginx-unprivileged:1.27-alpine` (uid 101, restricted) + Service ClusterIP `som-admin` |
| `k8s/50-ingress.yaml` (ใหม่) | Middleware `redirect-https` (port `"30081"`), `admin-auth` (basicAuth secret `som-admin-auth`, `removeHeader: true`); Ingress `som-shop` (shop.localhost → som-web:80, tls som-tls, mw redirect); Ingress `som-admin` (admin.localhost → som-admin:http, tls som-tls, mw redirect + admin-auth) |
| `hit.sh` | **ต้องแก้**: ค่าเริ่ม URL เป็น `https://shop.localhost:30081/api/whoami` และรับ `CURL_OPTS` (เช่น `--cacert tls.crt`) — pre-check ใช้ loop ของตัวเอง |
| `.gitignore` | `*.key`, `*.crt`, `secret.yaml` (เหมือน v7) |

**ขั้นตอน (ทดสอบจริงตามลำดับนี้ บนคลัสเตอร์ที่มีร้านบท 011 + orders=3):**

- **A — ย้ายประตู:** (ถ้าข้าม LAB 0 จะเจอ `provided port is already allocated` ตอนติดตั้ง Traefik) `kubectl apply -f k8s/00-namespace.yaml -f k8s/10-db.yaml -f k8s/15-config.yaml -f k8s/20-web.yaml` → `service/som-web configured` (NodePort → ClusterIP ผ่าน apply ได้เลย), `kubectl -n som-shop delete deploy som-https cm som-https-conf` (+ svc ถ้ายังอยู่) → `kubectl get svc -A | grep 3008` เหลือแต่ traefik
- **B — TLS ใบใหม่:** som-tls เดิม `CN=shop.som.local` (SAN shop.som.local, localhost) ใช้กับ shop.localhost ไม่ได้ → `openssl req … SAN=DNS:shop.localhost,DNS:admin.localhost,DNS:localhost` → `kubectl -n som-shop create secret tls som-tls … --dry-run=client -o yaml | kubectl apply -f -` (Warning missing last-applied = ปกติ)
- **C — หลังร้าน:** `kubectl -n som-shop create secret generic som-admin-auth --type=kubernetes.io/basic-auth --from-literal=username=som --from-literal=password=<รหัสตัวอย่าง>`; `kubectl apply -f k8s/40-admin.yaml -f k8s/50-ingress.yaml` → `kubectl get ing -n som-shop` = 2 แถว CLASS traefik ADDRESS localhost PORTS `80, 443`
- **D — ตรวจ:** `curl -i http://shop.localhost:30080/` → 301 Location `https://shop.localhost:30081/`; `curl --cacert tls.crt https://shop.localhost:30081/api/stats` → orders เดิม (pre-check 3); POST ผ่าน HTTPS ได้ `order_id` ถัดไป; admin ไม่มีบัตร 401 / มีบัตร 200 + `/stats`; `curl localhost:30080/api/stats` (ไม่มี Host) → 404 (ประตู NodePort เดิมของร้านไม่มีแล้ว); browser `http://shop.localhost:30080` → เตือน cert → หน้าร้าน (pre-check ด้วย Chromium ผ่าน)
- **E — ป้ายบท 012 + rolling update:** `hit.sh` วนระหว่าง `rollout restart deploy/som-web` (ConfigMap ใหม่) → `ok=250 err=0` 17.3 วิ และ footer `LAB 012 · เข้าร้านทาง Ingress https://shop.localhost`; แล้ว `set image deploy/som-web web=som-shop-web:1.6` + `annotate … kubernetes.io/change-cause="1.6 ผ่าน Ingress" --overwrite` → `ok=300 err=0` (1.5 ×112 / 1.6 ×188) 17.9 วิ; history 3 แถว
- **F — ปิดบท:** ร้านคนแน่น → HPA (บทหน้า), ติดตั้ง Traefik/ร้านด้วย Helm chart, Gateway API (LAB เสริม)

ข้อควรระวังที่เจอ: `kubectl apply` ทั้งโฟลเดอร์ v7 ทับไม่ได้ (30-https จะกลับมาจอง 30082 → ชน dashboard); POST body ต้องเป็น `{"product_id":1,"qty":1}` (`productId` ได้ `ข้อมูลไม่ถูกต้อง`); ป้ายใหม่มีผลหลัง rollout restart เท่านั้น

## 7. ภาพ (images.json)

- ทฤษฎี **53** ภาพ (T01–T53), LAB **31** ภาพ (L01–L31) รวม 84 · **needs_test 47** (T 25, L 22)
- ทุก LAB มีภาพเปิด; LAB 10 มี 9 ภาพ (L21–L29 รวม wrap-up), LAB เสริม 2 ภาพ
- รูปแบบ prompt เดิม (Use case / Asset type / Scene / Character / Style / Text (verbatim) / Constraints) — **บท 012 ป้ายมีหมายเลข** (`label 1: "…"`) และ Constraints อ้าง "label N" แทนการพิมพ์ค่าซ้ำ → ค่าที่อาจเปลี่ยนตามผลทดสอบ (พอร์ต, error, err=0, 36 : 4) อยู่ใน Text ที่เดียว; `imgcommon.py` assert ว่า Scene/Constraints ไม่มีค่าเลขพอร์ต 3008x/3009x, `err=`, `orders=` และไม่มีป้ายที่มีตัวเลขซ้ำ
- ตรวจด้วยสคริปต์แล้ว: JSON parse ได้, path/id ไม่ซ้ำ, ทุก prompt มีป้ายไทย ≥ 1 และ ≤ 7 ป้าย, จำนวนป้ายตรงกับ "exactly N", มี Constraint ภาษาไทยครบ
- อุปมาใหม่ (`M_ING` ใน imgcommon.py): Ingress = อาคารประตูหน้าท่าเรือ + ป้ายบอกทาง, controller = หุ่นยนต์พนักงานต้อนรับถือโคม, IngressClass = ตราบนเสื้อกั๊กตรงกับป้ายห้อย (ดาวทอง = default), TLS = ประตูกระจกนิรภัยมีตราประทับ, SNI = บอกชื่อผ่าน intercom, DEFAULT CERT = ตราสีเทา, defaultBackend = โต๊ะของหาย, Middleware = ด่านในทางเดิน (ป้ายลูกศร/ไม้กั้นตรวจบัตร/เครื่องตัดตั๋ว), access log = สมุดเยี่ยม, dashboard = กระดานแก้ว, Gateway API = อาคารผู้โดยสารรุ่นใหม่ (ใช้ได้เฉพาะภาพ `allow=True`)
- สร้างใหม่: `python3 logs/012_ingress/build_images.py` → `images.json` + `012_kubernetes_ingress/{01_Theory,02_LAB}/images/imagegen-prompts.md`; สร้างภาพ: `logs/012_ingress/gen_images.sh` (มีอยู่แล้ว)

## 8. จุดที่ต้องยืนยันตอนเขียน README/LAB จริง

1. **browser ของนักศึกษา**: ยืนยันแล้วเฉพาะ Chromium 153 บน Linux — ต้องลอง Chrome/Edge บน Windows และ macOS, Firefox, Safari (Safari อาจไม่แปลง `*.localhost` → ใช้ hosts) และ Docker Desktop ฟัง `::1` ด้วยหรือไม่ (ถ้าไม่ browser จะ fallback ไป 127.0.0.1 เอง — ควรเห็นผล)
2. redirectScheme ที่ไม่กำหนด `port` → Location ชี้ `:443`? (ยังไม่ได้ยิง) — ถ้าจะใช้เป็นขั้น "ลองผิด" ใน LAB 8
3. เปลี่ยน namespace `demo` → `ingress-demo` และชื่อไฟล์ตามตาราง แล้วรันซ้ำทั้งบท + เก็บ log จริงใน `logs/012_ingress/lab-run/`
4. `hit.sh` ของ v8 รับ https + `CURL_OPTS` (ยังไม่ได้เขียน/ทดสอบ)
5. จำนวน 502 ใน LAB 9 แบบไม่มี preStop (3–6/300 บนเครื่อง agent) อาจเป็น 0 บนเครื่องเร็ว → README ใช้คำว่า "อาจเห็น" และภาพ L20 ไม่ระบุจำนวน
6. orders ใน LAB 10 ขึ้นกับสภาพจากบท 011 (pre-check เริ่ม 3) → ภาพไม่ระบุตัวเลข
7. ภาพ needs_test ทั้ง 47 ภาพเทียบกับ log จริงอีกรอบ (โดยเฉพาะ T09 Host มีพอร์ต, T23 รายชื่อ browser, T36/T37/L18/L22/L26 พอร์ต 30080/30081, L03 dashboard, L11 ตาราง pathType, L31 อัตราส่วน 36 : 4 ซึ่งสุ่มได้ต่างทุกครั้ง → อาจเปลี่ยนเป็น "≈ 90 : 10")
8. ไฟล์ CRD สำเนา (248 KB) ในโฟลเดอร์บท — ตรวจว่า `kubectl apply` ธรรมดาผ่านบนเครื่องนักศึกษา (pre-check ผ่าน ไม่ติด annotation too long)
9. RBAC ของ Traefik: rule `pods get` (ใช้กับ OTel) ตัดออกแล้วในไฟล์บท — ทำงานปกติ ไม่เห็น error; ถ้าต้องการตรง upstream เพิ่มคืนได้

## 9. ไฟล์ในโฟลเดอร์นี้

- `plan.md` (ไฟล์นี้), `images.json`, `build_images.py`, `imgcommon.py` (สำเนาจาก `logs/templates/imgkit/` + บท 012), `gen_images.sh`, `montage.py`
- `precheck/` manifest ที่ทดสอบผ่าน (`00-traefik.yaml` ฉบับสุดท้าย, `10-demo.yaml`, `20-ing.yaml`, `30-debug.yaml`, `40-tls.yaml`, `50-mw.yaml`, `60-gateway.yaml`, `gw-rbac.yml`, `t20.sh`, `som-shop-v8-k8s/`)
- `scratch/` ไฟล์ชั่วคราว (สคริปต์ k8s-lab, สำเนาแอป, ภาพ `pw-shop.png` จาก Chromium) — ลบได้
