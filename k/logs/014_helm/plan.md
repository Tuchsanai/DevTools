# แผนบท 014 Kubernetes Helm — ชุดแฟรนไชส์ร้านน้องส้ม

> สถานะ: **แผน + storyboard ภาพ** (ยังไม่เขียน README/ไฟล์ LAB ฉบับจริง)
> pre-check จริงเมื่อ 6 ต.ค. 2569 (เวลาไทย) ใน container ชั่วคราว `k8s-lab-helm014-7de56c` (owner `helm014`) จาก `tuchsanai/devtools-kind:2569_1` (image ID `8108a1bc7901`) จำกัด `--cpus=4 --memory=8g` แบบบท 013, kind 3 Node, Kubernetes v1.37.0, kubectl v1.37.1 — ไม่ publish port ออก host (ทดสอบทุกอย่างด้วย `curl` ภายใน container) **ลบ container แล้ว** (`[k8s-lab] removed k8s-lab-helm014-7de56c`, `k8s-lab.sh ls` ว่าง) ไม่ได้แตะ `k8s-lab` ของผู้เรียนหรือ `deep_vision_5090_vllm`
> ไฟล์ที่ทดสอบแล้วอยู่ใน `precheck/` (chart, values, manifest ที่ render, สคริปต์ที่รันจริง `precheck/commands/run-*.sh`)

---

## 0. สรุปการตัดสินใจ (TL;DR)

| เรื่อง | ตัดสินใจ | หลักฐาน |
|---|---|---|
| เวอร์ชัน Helm | **v4.3.0** (`version.BuildInfo{Version:"v4.3.0", GitCommit:"bec5b06…", GoVersion:"go1.27.1", KubeClientVersion:"v1.37"}`) สอน Helm 4 เป็นหลัก ระบุสิ่งที่ต่างจาก Helm 3 เป็นกล่อง "ถ้าเจอบทความ Helm 3" | `helm version` ใน image |
| Server-side apply | **เป็นค่าเริ่มต้นตอน install** (`--server-side` default `true`), upgrade/rollback ใช้ `auto` (ตามวิธีของ revision ก่อน) — `helm get metadata` แสดง `APPLY_METHOD: server-side apply`, field manager ชื่อ `helm` | help + pre-check |
| flag ที่สอน | `--rollback-on-failure` (แทน `--atomic` ที่ยังใช้ได้แต่ขึ้น `Flag --atomic has been deprecated, use --rollback-on-failure instead`), `--force-replace` (แทน `--force`), `--force-conflicts`, `--take-ownership`, `--wait` (= `watcher`; ไม่ใส่ = `hookOnly`), `--dry-run=client|server` | `helm <cmd> --help` |
| chart API | **`apiVersion: v2`** (v3 ยังทดลอง — `helm lint` บอก `apiVersion 'v3' is not valid. The value must be either "v1" or "v2"` แม้ตั้ง `HELM_EXPERIMENTAL_CHART_V3=1`) | pre-check |
| Traefik | chart **`traefik/traefik` 41.6.1** (appVersion **v3.7.13** ตรงบท 012/013) repo `https://traefik.github.io/charts` | `helm search repo --versions` |
| metrics-server | chart **`metrics-server/metrics-server` 3.14.0** (appVersion **0.9.0** ตรงบท 013) | `helm search repo --versions` |
| ทางย้าย static → Helm (add-on) | **ลบของเดิมก่อน (เก็บ CRD ไว้) แล้วติดตั้ง chart** — adopt ไม่ได้เพราะ selector ของ Deployment ต่างกัน (`field is immutable`) ประตูปิด ~17 วินาที | pre-check LAB 10 |
| ทางย้ายร้าน (kubectl → Helm) | **adopt ได้** ด้วย `--take-ownership --force-conflicts` เพราะ chart ร้านตั้งชื่อ/selector เหมือนบท 013 → ออเดอร์เดิมอยู่ครบ (แต่ upgrade ครั้งแรกที่เปลี่ยน image ต้อง `--force-conflicts` อีกครั้ง) | pre-check LAB 12 |
| chart ร้าน | `02_LAB/charts/som-shop` (ทดสอบแล้วใน `precheck/final/charts/som-shop`) + hook seed (post-install/post-upgrade) + `helm test` + `values.schema.json` + `lookup`/`required`/`genSelfSignedCert` | pre-check |
| OCI | **ทำเป็น LAB หลัก (LAB 11)** — ง่ายพอ: `registry:2` (มี htpasswd) รันใน dockerd ของ k8s-lab, `helm push` / `helm install oci://localhost:5000/...  --plain-http` | pre-check |
| แอป | **1.8 = โค้ดเดิม build ใหม่ด้วย `--build-arg APP_VERSION=1.8`** (ไม่แก้โค้ด) build ซ้ำ 7 วินาทีเพราะ cache — `/api/whoami` ตอบ `… 1.8` | pre-check |
| ห้ามใช้ | Bitnami chart/image (ดู §1.5), plugin ที่ไม่ pin เวอร์ชัน | — |

---

## 1. การตรวจสอบและการตัดสินใจ 4 ข้อ

### 1.1 Helm 4 ต่างจาก Helm 3 อย่างไร (ที่กระทบการสอน)

แหล่งอ้างอิงทางการ:
- Helm 4 Overview — https://helm.sh/docs/overview/ (SSA default, plugin ใหม่/WASM, chart v3 ทดลอง, `--atomic`→`--rollback-on-failure`, `--force`→`--force-replace`, post-renderer ต้องเป็น plugin, `registry login` รับแค่ hostname, ติดตั้งด้วย digest)
- HIP-0023 Server Side Apply — https://helm.sh/community/hips/hip-0023/ (`--server-side=true|false|auto`, install = true, upgrade/rollback = auto, field manager `helm`, `--force-conflicts`)
- Helm 4 Full Changelog — https://helm.sh/docs/changelog/ (4.1 = 2025-11-20, 4.2 = 2026-04-29, 4.3.0, `--wait` strategy, `helm test --logs` เก็บ log ก่อนลบ hook, `--description` ของ rollback)
- Release v4.3.0 — https://github.com/helm/helm/releases/tag/v4.3.0 (ตรวจ ownership ก่อนลบตอน uninstall, `--description` ของ rollback, ฟังก์ชัน duration)
- Helm 3 EOL — https://helm.sh/blog/helm-v3-end-of-life (bug fix ถึง 9 ก.ย. 2569/2026, security fix ถึง 10 ก.พ. 2570/2027)
- Hooks — https://helm.sh/docs/topics/charts_hooks/ (hook 9 ชนิด, delete policy 3 ค่า default `before-hook-creation`, hook ไม่ถูกลบตอน uninstall)

ผลทดลองจริงด้วย helm v4.3.0 (ทุกบรรทัดคือผลที่เห็นจริง):

| หัวข้อ | Helm 3 (ที่นักศึกษาอาจเจอในเน็ต) | Helm 4.3.0 ที่ทดสอบ | ผลกับการสอน |
|---|---|---|---|
| วิธี apply | client-side 3-way merge | `--server-side` default `true` (install), `auto` (upgrade/rollback); `helm get metadata` → `APPLY_METHOD: server-side apply`; managedFields มี `helm Apply` | อธิบาย field manager / conflict กับ `kubectl-client-side-apply` (ต่อยอดบท 013 last-applied) |
| ติดตั้งทับของที่ `kubectl apply` ไว้ | `invalid ownership metadata` | เหมือนเดิม: `Error: INSTALLATION FAILED: unable to continue with install: ServiceAccount "traefik" in namespace "traefik" exists and cannot be imported into the current release: invalid ownership metadata; label validation error: missing key "app.kubernetes.io/managed-by": must be set to "Helm"; annotation validation error: missing key "meta.helm.sh/release-name": …` | LAB 10, LAB 12 |
| adopt | ต้อง label/annotate เอง | มี `--take-ownership` → แล้วเจอ SSA conflict: `conflict occurred while applying object … Apply failed with 3 conflicts: conflicts with "kubectl-client-side-apply" using v1: - .spec.selector …` → `--force-conflicts` แก้ conflict ได้ แต่ selector ต่าง → `spec.selector: Invalid value: … field is immutable` | สอน 3 ชั้นของการย้าย |
| atomic | `--atomic` | `--atomic` ยังรับ แต่ `Flag --atomic has been deprecated, use --rollback-on-failure instead`; `--rollback-on-failure --timeout 40s` + image ผิด → ~42 วินาที `Error: UPGRADE FAILED: release hello failed, and has been rolled back due to rollback-on-failure being set: resource Deployment/helm-demo/hello-podinfo not ready. status: InProgress, message: Updated: 2/3` history ได้ `failed` แล้ว `Rollback to 5` | LAB 4 |
| `--wait` | bool, ไม่ใส่ = ไม่รอ | `--wait WaitStrategy[=watcher]` ค่า `watcher`/`hookOnly`/`legacy` ไม่ใส่ = `hookOnly` (รอเฉพาะ hook) — image ผิดโดยไม่ใส่ `--wait` → `STATUS: deployed` ทั้งที่ Pod `ImagePullBackOff` | LAB 4 สอนให้ใส่ `--wait` เสมอ |
| `--dry-run` | `--dry-run` / `--dry-run=server` | ต้องระบุ `client`/`server`/`none`; **`--dry-run=server` ไม่จับ `service.type=NodePortt`** (ได้ `Dry run complete`) แต่ `helm template … \| kubectl apply --dry-run=server -f -` จับได้ `spec.type: Unsupported value: "NodePortt"` | LAB 6 (ต้องยืนยันซ้ำตอนเขียน LAB) |
| `helm list` | `-a/--all` | ไม่มี `-a` แล้ว (`Error: unknown shorthand flag: 'a' in -a`) — `helm list` แสดง release ทุกสถานะ (เห็น `failed`, `uninstalled` ที่ keep-history) มีตัวกรอง `--deployed/--failed/--uninstalled/...` | ตารางคำสั่ง |
| `helm registry login` | รับ URL ได้ | `http://localhost:5000` → `Error: invalid reference: invalid registry "http://localhost:5000"` ต้องใช้ `localhost:5000` | LAB 11 |
| plugin | ติดตั้งจาก git ได้เลย | ต้อง `--verify=false` ถ้าแหล่งไม่ได้เซ็น (`Error: plugin source does not support verification. Use --verify=false to skip verification`); `helm plugin list` มีคอลัมน์ `TYPE APIVERSION PROVENANCE`; helm-diff **v3.13.1 ใช้กับ Helm 4 ไม่ได้** (`if any flags in the group [validate dry-run] are set none of the others can be`) **v3.15.15 ใช้ได้** | ทฤษฎี + กล่องเสริม (ไม่บังคับใน LAB) |
| chart v3 | — | ยังไม่ใช้ได้ (lint error ทั้งมีและไม่มี `HELM_EXPERIMENTAL_CHART_V3=1`) | สอน v2 อย่างเดียว |
| `helm create` | ไม่มี httproute | scaffold มี `templates/httproute.yaml` (Gateway API) + `tests/test-connection.yaml` ไม่มี `values.schema.json` | LAB 5 |
| `helm lint` + `required` | error | `level=WARN msg="missing required values"` แต่ lint ผ่าน; `helm template` เป็น `Error: execution error at (som-shop/templates/web.yaml:29:28): ติดตั้งครั้งแรกต้องตั้งรหัสฐานข้อมูล: --set db.password=<รหัส>` | LAB 8 |
| release storage | Secret `helm.sh/release.v1` | เหมือนเดิม: `sh.helm.release.v1.<name>.v<N>` label `owner=helm,status=…,version=N`; ถอดด้วย `base64 -d \| base64 -d \| gzip -d` ได้ JSON key `name info chart config manifest hooks version namespace apply_method`; เก็บ 10 รุ่น (`HELM_MAX_HISTORY="10"`) | LAB 4, 12 |
| `rollback` ไม่ระบุเลข | ไป revision ก่อนหน้า | ไป **revision ก่อนหน้า แม้เป็น `failed`** (ทดสอบ: rev 3 failed → `helm rollback som` ได้ `Rollback to 3` ร้านยังเป็น 1.8) | LAB 4/12: ให้ระบุเลขเสมอ |

คำสั่งที่จะสอนและยืนยันแล้วว่าใช้ได้: `version, env, repo add/update/list, search repo --versions, search hub, show chart/values/readme, pull --untar, install (--create-namespace --set -f --wait --timeout --rollback-on-failure --take-ownership --force-conflicts), upgrade (--install --reuse-values --force-conflicts), list, status, get values/--all/manifest/notes/metadata, history, rollback <rev>, uninstall (--keep-history), test --logs, template (--debug), lint, create, package, push, registry login/logout, dependency list/update, plugin install/list/uninstall`

### 1.2 chart ภายนอก: Traefik + metrics-server

แหล่งอ้างอิง: Artifact Hub https://artifacthub.io/packages/helm/traefik/traefik , https://artifacthub.io/packages/helm/metrics-server/metrics-server , repo https://traefik.github.io/charts , https://kubernetes-sigs.github.io/metrics-server/ , source https://github.com/traefik/traefik-helm-chart

- `helm search repo traefik/traefik --versions` → `41.6.1 v3.7.13`, `41.6.0 v3.7.13`, `41.5.0 v3.7.13`, `41.4.0 v3.7.12` → **pin 41.6.1** (ล่าสุดที่ app = v3.7.13)
- `helm search repo metrics-server --versions` → `3.14.0 0.9.0`, `3.13.1 0.8.1` → **pin 3.14.0**
- `helm search hub traefik` เห็น `quench-traefik/traefik 0.0.21`, `aigisuk/traefik 0.1.1 2.7.0-rc2`, `kubeblocks/traefik 41.6.0` → ใช้สอนว่า "ชื่อเหมือนกันไม่ได้แปลว่าเป็นของทางการ" ดูผู้เผยแพร่ (verified publisher) ก่อน
- values ที่ทดสอบ: `precheck/lab10-addons/traefik-values.yaml`, `metrics-server-values.yaml`
  - Traefik: `service.spec.type: NodePort`, `ports.web.nodePort: 30080`, `ports.websecure.nodePort: 30081`, `ports.traefik.expose.default: true` + `nodePort: 30082`, `providers.kubernetesIngress.strictPrefixMatching: true`, `allowEmptyServices: true` (default ของ chart อยู่แล้ว), `publishedService.enabled: false` + `ingressEndpoint.hostname: localhost`, `ingressClass.isDefaultClass: true`, `api.insecure: true`, `accessLog.enabled: true`, `global.checkNewVersion/sendAnonymousUsage: false`
  - **values.schema.json ของ Traefik ปฏิเสธ key ผิด**: ใส่ `logs.access.enabled` ได้ `Error: values don't meet the specifications of the schema(s) in the following chart(s): traefik: - at '': additional properties 'logs' not allowed` → ใช้เป็นตัวอย่างในทฤษฎี/LAB 8
  - metrics-server: `args: [--kubelet-insecure-tls]`
- ผล render (`helm template`) เทียบ static manifest บท 013 (`precheck/lab10-addons/traefik-rendered.yaml`, `traefik-helm-manifest.yaml`, `metrics-server-helm-manifest.yaml`):
  - flags ครบ: `--entryPoints.websecure.http.tls=true`, `--providers.kubernetesingress.strictPrefixMatching=true`, `--providers.kubernetesingress.allowEmptyServices=true`, `--providers.kubernetesingress.ingressendpoint.hostname=localhost`, `--api.insecure=true`, `--accesslog=true`
  - Service NodePort `8080:30082/TCP,80:30080/TCP,443:30081/TCP`, IngressClass `traefik (default)` controller `traefik.io/ingress-controller`, image `docker.io/traefik:v3.7.13`
  - ต่าง: chart เพิ่ม entrypoint metrics `:9100` + prometheus, `--providers.kubernetescrd.allowEmptyServices=true`, ClusterRole/Binding ชื่อ `traefik-traefik` (static = `traefik`), **selector `app.kubernetes.io/name: traefik, app.kubernetes.io/instance: traefik-traefik`** (static = `app: traefik`), **Namespace ไม่อยู่ใน release** (มาจาก `--create-namespace`); CRD 25 ตัวจาก `crds/` ถูกข้ามเพราะมีอยู่แล้ว
  - metrics-server: selector `app.kubernetes.io/name/instance` (static = `k8s-app: metrics-server`), ClusterRole `system:metrics-server-aggregated-reader` (static = `system:aggregated-metrics-reader`), args เหมือนกันครบรวม `--kubelet-insecure-tls`
- **ทางย้าย (ทดสอบจริงตามลำดับ)**
  1. `helm install` ทับ → `invalid ownership metadata` (ไม่มี release ค้าง ปลอดภัย)
  2. `--take-ownership` → SSA conflict กับ `kubectl-client-side-apply` (Service 3 conflicts, Deployment 11 conflicts) **และเกิด release `failed` rev 1**
  3. `--take-ownership --force-conflicts` → `spec.selector … field is immutable` (rev 2 failed)
  4. ⚠️ `helm uninstall` release ที่ล้มนี้ **ลบ ServiceAccount/Service/ClusterRole ที่ถูก take-ownership ไปแล้ว** (เหลือ Deployment) → ร้านปิดทันที ⇒ ใน LAB ให้ทำแค่ข้อ 1 จริง ข้อ 2–4 แสดงเป็น "ผลจริง ไม่ต้องทำตาม"
  5. **ทางที่ใช้**: `kubectl delete -f ingress-controller/00-traefik.yaml` (ไม่ลบ `traefik-crds-v3.7.13.yml` — Middleware ของร้านอยู่บน CRD) → `helm install traefik traefik/traefik --version 41.6.1 -n traefik --create-namespace -f traefik-values.yaml --wait` → ทั้งหมด **18 วินาที**, `hit.sh -q` 600 ครั้ง → `ok=530 err=70`, `ช่วงที่มี err: 16.6 วินาที` (error `SSL_ERROR_SYSCALL` 61 + `Connection reset by peer` 9) — แจ้งนักศึกษาว่าระบบจริงต้องทำ blue/green หรือช่วงปิดปรับปรุง
  6. metrics-server: `kubectl delete -f metrics-server/00-metrics-server.yaml` → `helm install … --wait` **21 วินาที** → `kubectl top nodes` ได้ + `v1beta1.metrics.k8s.io kube-system/metrics-server True`
  - Traefik install เดี่ยว (`--wait`) 13 วินาที; `curl localhost:30080` → `404 page not found`; dashboard `localhost:30082/dashboard/` → 200

### 1.3 chart ของร้าน som-shop

ทดสอบแล้วที่ `precheck/final/charts/som-shop` (จะคัดลอกเป็น `014_kubernetes_helm/02_LAB/charts/som-shop`) — render แล้วอยู่ที่ `precheck/final/rendered-dev.yaml`, `rendered-prod.yaml` (ตัด tls.key ออก)

```text
charts/
├── som-shop/
│   ├── Chart.yaml            apiVersion v2, version 0.1.0, appVersion "1.7", kubeVersion >=1.30.0-0
│   ├── values.yaml           shop.* (การ์ดกระดาน), announcement, web.image/replicas/resources, hpa.*, db.*, externalDatabase.url, seed.enabled, ingress.*, tests.image
│   ├── values.schema.json    replicas 1–6, tag ≠ "1.4", hpa.maxReplicas ≤ 6, host pattern, storage pattern
│   ├── .helmignore
│   └── templates/
│       ├── _helpers.tpl      som-shop.fullname (fullnameOverride|Release.Name), som-shop.labels, som-shop.webImage, som-shop.dbPassword (--set > lookup > required)
│       ├── configmap.yaml    <fn>-web-config (range .Values.shop) + <fn>-announcement
│       ├── secret.yaml       <fn>-db-secret (POSTGRES_PASSWORD + DATABASE_URL ที่ printf ประกอบ; db.enabled=false → required externalDatabase.url)
│       ├── db.yaml           (if db.enabled) headless Service <fn>-db + StatefulSet <fn>-db (volumeClaimTemplates data)
│       ├── web.yaml          Deployment <fn>-web (if not hpa.enabled → replicas), checksum/config + checksum/secret, initContainer wait-for-db, toYaml resources | nindent 12 + Service ClusterIP
│       ├── hpa.yaml          (if hpa.enabled) autoscaling/v2
│       ├── ingress.yaml      (if ingress.enabled) [tls: Secret <fn>-tls = lookup ใบเดิม หรือ genSelfSignedCert + Middleware <fn>-redirect-https] + Ingress <fn>-web
│       ├── seed-job.yaml     hook post-install,post-upgrade (weight 0, delete-policy before-hook-creation,hook-succeeded) node scripts/seed.mjs
│       ├── tests/test-health.yaml   hook test: curl /api/health /api/whoami /api/products (curlimages/curl:8.22.0)
│       └── NOTES.txt         ชื่อร้าน, revision, image, จำนวนบูธ/HPA, คำสั่งเปิดร้าน, helm test
├── values-dev.yaml           SHOP_NAME "(dev)", sunset, replicas 1, hpa off, ingress dev.shop.localhost (http)
└── values-prod.yaml          hpa 2–6, ingress shop.localhost tls
```

- release `som` → ชื่อ object = `som-web`, `som-db`, `som-db-secret`, `som-web-config`, `som-announcement`, `som-tls` **ตรงกับบท 009–013** (DNS `som-db-0.som-db` เดิม) → adopt ร้านบท 013 ได้
- ใช้ฟังก์ชัน: `include`, `define`, `default`, `required`, `lookup`, `quote`, `toYaml | nindent`, `range $k, $v`, `if/else`, `printf`, `b64enc/b64dec`, `sha256sum`, `trunc/trimSuffix`, `genSelfSignedCert`, `index`, `.Template.BasePath`, `.Release.*`, `.Chart.*`
- `values.schema.json` ยังรองรับใน Helm 4 (draft 2020-12): `--set web.image.tag=1.4` → `- at '/web/image/tag': 'not' failed`, `--set web.replicas=9` → `- at '/web/replicas': maximum: got 9, want 6`
- **hook**: seed Job รันหลังสร้าง resource (install ~16–17 วินาทีรวม hook) ทดสอบ hook ล้ม: uninstall dev (PVC ค้าง) → install ใหม่ด้วยรหัสอื่น `purr5678` → ~40 วินาที `Error: INSTALLATION FAILED: failed post-install: resource Job/som-dev/som-seed not ready. status: Failed, message: Job Failed. failed: 1/1` (web `0/1` เพราะ health ต่อ db ไม่ได้) → `helm upgrade … --set db.password=meow1234 --wait` แก้ได้ (upgrade release ที่ failed ได้เลย) `orders=1` กลับมา
- **helm test**: `Phase: Succeeded` + logs `health:   {"ok":true,"db":"up"}`, `whoami:   som-web-… 1.7`, `products: ok`; delete policy `before-hook-creation,hook-succeeded` → Pod ทดสอบหายหลังผ่าน (`--logs` ยังแสดง log) — **หมายเหตุ**: `helm test` ใช้ hook จาก release ที่ติดตั้งไว้ ไม่ใช่ไฟล์ในเครื่อง (แก้ chart แล้วต้อง upgrade ก่อน)
- **lookup**: upgrade dev โดยไม่ `--set db.password` → Secret ยังเป็น `meow1234`; TLS: fingerprint ก่อน/หลัง upgrade เหมือนกัน (`5D:F2:36:86:…`); `helm template` (ไม่ต่อคลัสเตอร์) lookup ได้ค่าว่าง → required error = สอนความต่าง template vs install
- **checksum/config**: `--set announcement="ปลาแซลมอนมาแล้ว"` → ได้ Pod ใหม่เอง (`/api/announcement` ตอบค่าใหม่) ไม่ต้อง `rollout restart` แบบบท 010
- **secret ใน release**: ถอด `sh.helm.release.v1.som.v1` → `{"db": {"password": "meow1234"}, …}` และ manifest มี `DATABASE_URL: "postgres://som:meow1234@som-db-0.som-db:5432/catshop"`; `helm get values` ก็แสดง `password: meow1234` → สอนว่าใครอ่าน Secret ใน namespace ได้ = อ่านรหัสได้ (RBAC บท 011), ห้าม commit values ที่มีรหัส, ทางจริง: External Secrets/Sealed Secrets/SOPS (ทฤษฎี)
- **PVC**: `helm uninstall som -n som-dev` → เหลือ `persistentvolumeclaim/data-som-db-0 Bound` (ต่อบท 009) ติดตั้งใหม่ด้วยรหัสเดิม → `orders=1` ข้อมูลเดิมกลับมา
- `--keep-history`: `helm list` แสดง `uninstalled` rev 11, `helm rollback hello 11` → rev 12 `deployed` (ร้านกลับมา); ไม่ใส่ → `helm history` = `Error: release: not found`; install ชื่อเดิมระหว่าง keep-history → `cannot reuse a name that is still in use` (ใช้ `upgrade --install` ได้)

### 1.4 OCI registry

- `registry:2` + htpasswd (สร้างด้วย `docker run --rm --entrypoint htpasswd httpd:2.4-alpine -Bbn som meow-registry-123`) รันใน dockerd ของ k8s-lab `-p 5000:5000` (ไม่ชนพอร์ต 30080–30082, ไม่ต้อง map ออก host)
- `helm package charts/som-shop` → `som-shop-0.1.0.tgz` (6014 ไบต์)
- push ก่อน login → `basic credential not found`; login ด้วย URL → `invalid registry "http://localhost:5000"`; `helm registry login localhost:5000 -u som --password-stdin --plain-http` → `Login Succeeded`
- `helm push som-shop-0.1.0.tgz oci://localhost:5000/charts --plain-http` → `Pushed: localhost:5000/charts/som-shop:0.1.0` + `Digest: sha256:e607fd8f…`
- `helm show chart oci://… --version 0.1.0 --plain-http`, `helm pull … --untar -d pulled` (โฟลเดอร์ต้องมีอยู่ก่อน ไม่งั้น `no such file or directory`), `helm install oci-som oci://localhost:5000/charts/som-shop --version 0.1.0 --plain-http …` **17 วินาที**, ติดตั้งด้วย digest `…/som-shop@sha256:…` ได้, `helm registry logout` แล้วดึงอีก → `basic credential not found`
- ข้อควรรู้: credential เก็บที่ `~/.config/helm/registry/config.json` เป็น base64 (`{'localhost:5000': {'auth': 'c29tOm...'}}`) — ไม่ใช่การเข้ารหัส (ต่อบท 011)
- **ความต่างกับ `imagePullSecrets` บท 011**: chart ถูกดึงโดย **helm บนเครื่องเรา** (ใช้ registry login) ส่วน image ของ Pod ถูกดึงโดย **kubelet บน Node** (ใช้ imagePullSecrets) — ไม่ทำ LAB push image เข้า registry นี้เพราะ Node ของ kind มองไม่เห็น `localhost:5000` ของ k8s-lab (ต้องตั้ง containerd mirror — ทฤษฎีเท่านั้น)
- dependency OCI ใช้ได้: `oci://ghcr.io/stefanprodan/charts` (podinfo 6.15.0) ใน `Chart.yaml` → `helm dependency update` สร้าง `Chart.lock` + `charts/*.tgz`
- ไม่มีการ push ไป registry ภายนอกจริง

### 1.5 Bitnami (ทำไมต้องระวังแหล่ง chart/image)

แหล่ง: ประกาศทางการ https://github.com/bitnami/charts/issues/35164 ("Upcoming changes to the Bitnami catalog (effective August 28th, 2025)")
- ตั้งแต่ 28 ส.ค. 2568 Bitnami หยุดเผยแพร่ image/chart รุ่นมีเลขเวอร์ชันฟรีใน `docker.io/bitnami` ย้ายของเก่าไป `docker.io/bitnamilegacy` (ไม่อัปเดต ไม่ซัพพอร์ต) มี brownout หลายรอบ ชุดฟรีที่เหลือ (`bitnamisecure`) มีแค่ tag `latest`
- บทเรียน: chart/image ที่ดังที่สุดก็หายหรือเปลี่ยนเงื่อนไขได้ → pin เวอร์ชัน + digest, ใช้ chart ของเจ้าของโปรเจกต์ (Traefik, kubernetes-sigs), มีสำเนาภายใน (OCI registry ของตัวเอง — LAB 11), อ่าน values/ image ที่ chart จะดึงก่อนติดตั้ง (`helm show values`, `helm template | grep image:`)
- บทนี้ **ไม่ใช้ Bitnami** (postgres ใช้ image ทางการ `postgres:17.11-alpine` ใน chart ของเราเอง)

---

## 2. สารบัญทฤษฎี (`01_Theory/README.md`)

1. **บทนำ: ร้านน้องส้มมีสาขาที่ 2** — ทวนบท 013 (ร้าน = 9 ไฟล์ YAML + Traefik + metrics-server ติดตั้งด้วย static manifest), อยากเปิดสาขา dev/prod → ค่าซ้ำ แก้หลายที่ ลืมลำดับ; อุปมาใหม่ของบท; เป้าหมาย
2. **ปัญหาของ YAML ล้วน** — ไฟล์เยอะ/ค่าซ้ำ (ชื่อ, label, image tag ซ้ำ 3 ที่), หลาย environment (copy โฟลเดอร์แล้วแก้ = drift), ไม่มี "รุ่น" ของทั้งชุด (rollout history มีแค่ Deployment), ลบไม่หมด, ไม่รู้ว่าใครติดตั้งอะไร; ตารางเทียบ "สิ่งที่ kubectl apply ทำ / ไม่ทำ"
3. **Helm คืออะไร** — package manager ของ Kubernetes (เทียบ apt/npm), client-only ตั้งแต่ v3 (Tiller ใน v2 = ตัวกลางในคลัสเตอร์สิทธิ์สูง ถูกเอาออก), Helm 4 (ออกปลายปี 2568) และ Helm 3 EOL; ศัพท์ 5 คำ: chart / values / release / revision / repository (+ ตาราง อุปมา)
4. **โครงสร้าง chart** — `Chart.yaml` (apiVersion v2, name, version vs appVersion, type application/library, kubeVersion, dependencies), `values.yaml`, `values.schema.json`, `templates/`, `_helpers.tpl`, `NOTES.txt`, `templates/tests/`, `charts/`, `crds/` (ติดตั้งครั้งแรกเท่านั้น ไม่ upgrade/ไม่ลบ), `.helmignore`, `Chart.lock`; SemVer ของ chart
5. **Go template + Sprig ขั้นพื้นฐาน** — `{{ }}`, `.`, built-in objects (`.Values`, `.Release.Name/Namespace/Revision/IsInstall/IsUpgrade/Service`, `.Chart.Name/Version/AppVersion`, `.Capabilities`, `.Template`), pipeline `|`, `quote`, `default`, `required`, `toYaml`, `indent` vs `nindent`, `{{-` `-}}` ตัดช่องว่าง, `if/else`, `with`, `range` (list และ map), ตัวแปร `$`, `define`/`include` vs `template`, `printf`, `lookup` (และทำไม `helm template` ได้ค่าว่าง), `tpl`, ฟังก์ชันที่ห้ามใช้ใน chart จริงโดยไม่คิด (`randAlphaNum`, `genSelfSignedCert` เปลี่ยนทุก upgrade ถ้าไม่ lookup), checksum annotation pattern
6. **values และลำดับความสำคัญ** — ค่าเริ่มต้นใน chart < parent chart < `-f` (ไฟล์หลังชนะไฟล์หน้า) < `--set`/`--set-string`/`--set-file`/`--set-json`; การ merge แบบ map (list ถูกแทนทั้งก้อน); `helm get values` vs `--all`; upgrade โดยไม่ส่ง values = กลับค่าเริ่มต้น, `--reuse-values` vs `--reset-then-reuse-values`; values ต่อ environment; `values.schema.json` ตรวจก่อน render
7. **การ render และ debug** — `helm template` (client), `helm install --dry-run=client|server`, `--debug`, `helm lint`, `--show-only`, error 4 แบบที่เจอบ่อย (YAML indent, function not defined, required, schema) + ข้อจำกัด `--dry-run=server` ที่เจอจริง → `helm template | kubectl apply --dry-run=server -f -`
8. **lifecycle ของ release** — install → upgrade → rollback → uninstall; สถานะ `pending-install/deployed/superseded/failed/uninstalled/pending-upgrade/pending-rollback`; rollback = revision ใหม่เสมอ (เลขไม่ถอยหลัง), rollback ไม่ใส่เลข; `--wait` strategies (`watcher` ใช้ kstatus, `hookOnly` ค่าเริ่มต้น, `legacy`), `--timeout`, `--rollback-on-failure`, `--cleanup-on-fail`, `upgrade --install` (idempotent สำหรับ CI), `--keep-history`, `--history-max`
9. **Helm 4 กับ server-side apply** — field manager (`helm`, `kubectl-client-side-apply`, `kube-controller-manager`), managedFields, conflict คืออะไร (เทียบ last-applied บท 013), `--server-side`, `--force-conflicts`, `--take-ownership`, `--force-replace`, ทำไมการรับร้านเก่าต้อง force (และ upgrade ครั้งแรกยังชนเพราะ field ที่ถือร่วมกัน), field ที่ helm ไม่ได้ตั้ง (เช่น HPA behavior จากบท 013) ยังอยู่
10. **release เก็บที่ไหน** — Secret `helm.sh/release.v1` ชื่อ `sh.helm.release.v1.<release>.v<N>` (label owner=helm) = base64 (โดย API) + base64 + gzip ของ JSON (chart + config + manifest); ถอดได้ → values ที่มีรหัสอ่านได้; driver อื่น (configmap/sql); history max 10
11. **hooks และ helm test** — 9 ชนิด hook, `hook-weight`, `hook-delete-policy` (3 ค่า default `before-hook-creation`), hook ไม่ใช่ส่วนของ release (uninstall ไม่ลบ), hook Job vs initContainer (บท 009–013 ใช้ db-seed initContainer), ลำดับ install → resources → (wait) → post-install hook; hook ล้ม = release failed; `helm test` = Pod/Job annotation `test` ต้อง exit 0, `--logs`, `--filter`
12. **dependencies (subchart)** — `dependencies:` ใน Chart.yaml (name/version/repository/condition/alias), `helm dependency update/build/list`, `Chart.lock`, `charts/`, ส่งค่าให้ subchart ด้วย key ชื่อ subchart, `global`, umbrella chart (ตัวอย่าง harbor-addons: metrics-server + podinfo แบบ condition), library chart (แนะนำสั้น ๆ)
13. **repository: HTTP vs OCI** — HTTP repo (`index.yaml` + .tgz, `helm repo add/update`), OCI (`oci://`, ไม่ต้อง repo add, `helm push/pull`, `registry login` แค่ hostname, ติดตั้งด้วย digest), Artifact Hub (ค้น, verified publisher, official, security report, `helm search hub`), เก็บสำเนาใน registry ขององค์กร; chart vs image registry และ imagePullSecrets (บท 011)
14. **ความปลอดภัยและแหล่งที่มา** — อ่านก่อนติดตั้ง (`helm show values/readme`, `helm template | grep image:`), pin chart version + appVersion + digest, provenance/`helm verify` (กล่าวถึง), Bitnami 2025 (§1.5), ไม่ใส่ secret จริงใน values ที่ commit, release Secret อ่านได้ (RBAC), ทาง External Secrets / Sealed Secrets / SOPS, plugin ต้อง `--verify` และ pin, `api.insecure`/`--kubelet-insecure-tls` ใช้เฉพาะ LAB
15. **Helm vs Kustomize vs static manifest** — ตารางเทียบ (template vs overlay/patch, มี release/rollback หรือไม่, packaging/แจกจ่าย, ความยากของ debug, `kubectl apply -k` บท 010 configMapGenerator), ใช้ร่วมกันได้ (`helm template | kustomize`, post-renderer plugin)
16. **ปูทาง GitOps และ operator** — Git เป็นแหล่งความจริง, Argo CD Application (`source.chart` + `helm.valueFiles`) / Flux `HelmRelease` อ่าน chart เดียวกัน, ไม่ต้อง `helm upgrade` เอง; operator = หุ่นยนต์ที่ดูแลร้านต่อหลังติดตั้ง (Helm ติดตั้งจบแล้วไม่ดูแลต่อ) — บทถัดไป
17. **ตารางคำสั่งที่ใช้บ่อย** (Helm 4) + ตาราง Helm 3 → Helm 4 flag
18. **สรุปบท + คำถามทบทวน + แหล่งอ้างอิง**

---

## 3. ตาราง LAB (`02_LAB/README.md`)

กติกา: ทำใน `/workspace/014_kubernetes_helm/02_LAB`, 🐧 ใน SSH session ของ k8s-lab, เครื่อง 4 core; ร้านบท 013 (`som-shop`), Traefik และ metrics-server (static) ต้องมีอยู่ก่อน (ถ้าไม่มี มีทางสร้างใหม่ใน LAB 0); รหัสทุกตัวเป็นตัวอย่าง (`meow1234`, `meow-admin-123`, `meow-registry-123`); namespace ที่ใช้: `helm-demo` (LAB 2–4), `first` (LAB 5–6), `som-dev`, `som-shop` (LAB 9, 12), `oci-demo` (LAB 11)

| LAB | ชื่อ (เรื่องเล่า) | ไฟล์ | คำสั่งหลัก | ผลที่ต้องเห็น (จาก pre-check) | ต้องยืนยันตอนเขียน |
|---|---|---|---|---|---|
| 0 | เตรียมท่าเรือ + แอป 1.8 | `som-shop-v10/app` (สำเนา v9) | `helm version`, `helm env \| grep -E "HELM_(CACHE\|CONFIG\|DATA)_HOME\|MAX_HISTORY"`, `kubectl get ns som-shop traefik`, `docker build -q -t som-shop-web:1.8 --build-arg APP_VERSION=1.8 app && kind load docker-image som-shop-web:1.8 --name lab` (+1.7 ถ้าคลัสเตอร์ใหม่ + postgres image-archive) | `Version:"v4.3.0"`, build 1.8 ~7 วินาทีถ้ามี cache 1.7 (ไม่มี cache ~45 วินาที) | เวลา build บนเครื่องนักศึกษา, ทางคลัสเตอร์ใหม่ |
| 1 | แคตตาล็อกแฟรนไชส์ | — | `helm repo add podinfo https://stefanprodan.github.io/podinfo`, `traefik`, `metrics-server`, `helm repo update`, `helm search repo traefik/traefik --versions \| head`, `helm search hub traefik`, `helm show chart/values podinfo/podinfo --version 6.15.0`, `helm pull traefik/traefik --version 41.6.1 --untar` | `41.6.1 v3.7.13`, `3.14.0 0.9.0`, `podinfo 6.15.0`; hub มี `quench-traefik`, `kubeblocks` ชื่อซ้ำ; podinfo `apiVersion: v1` (chart เก่ายังใช้ได้) | เวอร์ชันล่าสุดตอนเขียน (pin เดิม) |
| 2 | เปิดสาขาแรกจากแคตตาล็อก (podinfo) | — | `helm install hello podinfo/podinfo --version 6.15.0 -n helm-demo --create-namespace --set replicaCount=2 --set ui.message="สวัสดีจากร้านน้องส้ม" --wait`, `helm list/status`, `helm get values/manifest/notes/metadata`, `kubectl get secret -l owner=helm`, port-forward 9898 + curl | install 19 วินาที, `REVISION: 1`, `APPLY_METHOD: server-side apply`, `sh.helm.release.v1.hello.v1 helm.sh/release.v1`, curl ได้ `"message": "สวัสดีจากร้านน้องส้ม"` | — |
| 3 | ใบสั่งปรับแต่งร้าน: values | `lab03-values/podinfo-values.yaml` (`precheck/final/podinfo-values.yaml`) | `helm upgrade hello … -f podinfo-values.yaml --set ui.message="--set ชนะ" --wait`, `curl http://podinfo.localhost:30080`, `helm get values` / `--all`, upgrade โดยไม่ส่ง values, `--reuse-values` | `"message": "--set ชนะ"`, สี `#ff8c00`, Ingress ผ่าน Traefik; upgrade ไม่ส่ง values → เหลือ `replicaCount: 1` อย่างเดียว | — |
| 4 | สมุดบันทึกการปรับปรุงร้าน: upgrade/history/rollback | — | image ผิดไม่ใส่ `--wait` → `deployed` + `ImagePullBackOff`; `--atomic` (warning) / `--rollback-on-failure --timeout 40s`; `helm history`; `helm rollback hello 2 --wait`; rollback ไม่ใส่เลข; `uninstall --keep-history` → `list --uninstalled` → `rollback`; ถอด release Secret | rollback → revision ใหม่ `Rollback to 2`; rollback-on-failure ~42 วินาที `failed` + `Rollback to N`; keep-history rollback กลับมา `deployed` | เลข revision ตามลำดับของนักศึกษา |
| 5 | ชุดแฟรนไชส์ชุดแรกของเรา: `helm create` | `lab05-first/` (สร้างเอง) | `helm create mychart`, `tree`, `helm lint`, `helm template web mychart`, `helm install web mychart -n first --create-namespace --wait`, `helm test web -n first --logs` | lint `[INFO] Chart.yaml: icon is recommended` `0 chart(s) failed`; install 8 วินาที; test `Phase: Succeeded` + `'index.html' saved` | nginx:1.16.0 บน ARM (multi-arch, คาดว่าได้) |
| 6 | แม่พิมพ์พัง: render & debug | `lab06-debug/` (คัดลอก mychart แล้วทำพัง) | indent แทน nindent → `helm lint`/`template`/`--debug`; `toYml`; `required`; `--dry-run=server` vs `helm template \| kubectl apply --dry-run=server -f -`; Chart apiVersion v3 | `yaml: line 24: mapping values are not allowed in this context`; `function "toYml" not defined`; `execution error … ต้องใส่ image.repository`; `Dry run complete` (ไม่จับ) vs `spec.type: Unsupported value: "NodePortt"`; `apiVersion 'v3' is not valid` | พฤติกรรม `--dry-run=server` (ทดสอบซ้ำ + ดู issue) |
| 7 | แม่พิมพ์ร้านน้องส้ม: template functions | `charts/som-shop` | อ่าน `_helpers.tpl`, `helm template som charts/som-shop --set db.password=x --show-only templates/configmap.yaml`, `--show-only templates/web.yaml` เทียบ hpa on/off, `--set fullnameOverride=shop2` | ConfigMap 5 การ์ดจาก `range`, `replicas:` หายเมื่อ hpa.enabled, `checksum/config` เปลี่ยนเมื่อแก้ shop.* | — |
| 8 | ใบสั่งต่อสาขา: dev/prod + schema + lookup | `charts/values-dev.yaml`, `values-prod.yaml`, `values.schema.json` | `helm template … -f values-dev.yaml` vs prod (`grep -E "^kind:"`), `--set web.image.tag=1.4`, `--set web.replicas=9`, ไม่มีรหัส (`helm lint` WARN vs `helm template` error), ลอง values ผิด key ของ Traefik | dev 9 object ไม่มี HPA/TLS, prod 12 object (+HPA, Secret tls, Middleware); `'not' failed`, `maximum: got 9, want 6`; `level=WARN msg="missing required values"` | — |
| 9 | ขั้นตอนพิเศษก่อน/หลังเปิดร้าน + ผู้ตรวจรับร้าน | `charts/som-shop` | `helm install som charts/som-shop -n som-dev --create-namespace -f charts/values-dev.yaml --set db.password=meow1234 --wait`, `kubectl get job -n som-dev -w` (seed), `helm test som -n som-dev --logs`, curl dev, ถอด release Secret เห็นรหัส | 17 วินาที, NOTES ภาษาไทย, `som-web-… 1.7 orders=0 products=6`, test Succeeded 3 บรรทัด, `{"db": {"password": "meow1234"}` | เวลาบนเครื่อง 4 core จริง |
| 10 | เปลี่ยนพนักงานต้อนรับ/จดมิเตอร์ให้มาจากแคตตาล็อก (Traefik + metrics-server) | `addons/traefik-values.yaml`, `addons/metrics-server-values.yaml` | `helm template` เทียบ static, `helm install` ทับ (error), [ผลจริง take-ownership/force-conflicts], `kubectl delete -f ../../013…/00-traefik.yaml` (เก็บ CRD), `helm install traefik … --wait` ระหว่าง `hit.sh -q`, metrics-server เหมือนกัน, `helm list -A`, `kubectl top nodes` | `invalid ownership metadata`; ย้าย 18 วินาที `err` ~17 วินาที; `404 page not found`; IngressClass `traefik (default)`; `True` | อัตรา err บนเครื่องนักศึกษา; ไฟล์ static อยู่ในโฟลเดอร์บท 014 (`02_LAB/static-old/`) |
| 11 | โกดังเก็บชุดแฟรนไชส์ (OCI registry) | `registry/` (คำสั่ง htpasswd) | `docker run -d --name som-registry -p 5000:5000 … registry:2`, `helm package`, push (error) → `helm registry login localhost:5000` → push → `helm show chart oci://…` → `helm install oci-som oci://localhost:5000/charts/som-shop --version 0.1.0 --plain-http -n oci-demo --create-namespace …` → logout | `Pushed: localhost:5000/charts/som-shop:0.1.0`, `Digest: sha256:…`, install 17 วินาที, `oci.shop.localhost:30080` ตอบ | registry:2 บน ARM (multi-arch) |
| 12 | **LAB สุดท้าย: ร้านน้องส้มพร้อมส่ง — ติดตั้งทั้งร้านด้วยคำสั่งเดียว** | `charts/som-shop`, `values-dev.yaml`, `values-prod.yaml`, `hit.sh` | ดู §4 | ดู §4 | ดู §4 |

LAB เสริม (ไม่บังคับ): `helm plugin install https://github.com/databus23/helm-diff --version v3.15.15 --verify=false` + `helm diff upgrade` (เห็น `app.kubernetes.io/version: "1.7"` → `"1.8"`), umbrella chart `harbor-addons` (dependencies metrics-server + podinfo `condition: podinfo.enabled`) `helm dependency update` → `Chart.lock`

---

## 4. LAB สุดท้าย (LAB 12): ร้านน้องส้มพร้อมส่ง — ติดตั้งทั้งร้านด้วยคำสั่งเดียว

**การเปลี่ยนแอป**: `som-shop-web:1.8` = โค้ด 1.7 เดิม build ด้วย `--build-arg APP_VERSION=1.8` (เห็นต่างที่ `/api/whoami`, ป้ายเวอร์ชันบนหน้าร้าน) — build ใน LAB 0; ห้ามใช้ tag 1.4 (schema กันไว้)

**โครงร้าน**: `02_LAB/charts/som-shop` (§1.3) + `02_LAB/charts/values-dev.yaml`, `values-prod.yaml`, `02_LAB/hit.sh` (สำเนาจากบท 013)

| ขั้น | ทำอะไร | คำสั่ง | ผลจริงจาก pre-check | ต้องยืนยัน |
|---|---|---|---|---|
| 12.1 จุดเริ่ม | ร้านบท 013 ใน `som-shop` (kubectl), Traefik/metrics-server เป็น Helm แล้ว (LAB 10) | `helm list -A`, `kubectl -n som-shop get deploy,sts,hpa,ing`, `curl -sk https://shop.localhost:30081/api/stats` | `traefik … deployed traefik-41.6.1 v3.7.13`, `metrics-server … metrics-server-3.14.0 0.9.0` | ออเดอร์เดิมของนักศึกษา |
| 12.2 อ่านชุดแฟรนไชส์ | tree + lint + template dev/prod | `helm lint charts/som-shop -f charts/values-prod.yaml --set db.password=x` | `0 chart(s) failed` | — |
| 12.3 สาขา dev คำสั่งเดียว | namespace ใหม่ `som-dev` | `time helm install som charts/som-shop -n som-dev --create-namespace -f charts/values-dev.yaml --set db.password=meow1234 --wait` แล้ว `helm test som -n som-dev --logs`, `curl http://dev.shop.localhost:30080/api/whoami` | 17 วินาที (ไม่ใส่ `--wait` 12 วินาที เพราะรอ hook อยู่แล้ว), `som-web-… 1.7`, หน้าร้านมี `ร้านอาหารแมวน้องส้ม (dev)` ธีม sunset | เวลา install ทั้งร้านบนเครื่องนักศึกษา |
| 12.4 รับร้านเดิมเข้า Helm (prod) | adopt `som-shop` ของบท 013 | (ก) `helm install som charts/som-shop -n som-shop -f charts/values-prod.yaml` → (ข) `helm upgrade --install … --take-ownership` → (ค) `… --take-ownership --force-conflicts --wait` | (ก) `Secret "som-tls" … invalid ownership metadata` (ข) `conflicts with "kubectl-client-side-apply"`: ConfigMap 3 (`.data.SHOP_EYEBROW/FOOTER/PROMO`), Deployment 2, StatefulSet 1 (`.spec.volumeClaimTemplates`) → rev 1 `failed` (ค) rev 2 `deployed`, `orders=1` (ออเดอร์เดิมอยู่), รหัส db มาจาก lookup (ไม่ต้อง `--set`), cert som-tls เดิมถูกใช้ต่อ | รายการ conflict ตามสภาพร้านของนักศึกษา (1.6/1.7, ผลจาก LAB 10 บท 013) |
| 12.5 เก็บของเก่า | Ingress `som-shop` เดิม (host ซ้ำกับ `som-web` ของ chart), Deployment `customers` | `kubectl -n som-shop delete ingress som-shop deploy customers` (**ไม่ลบ** Middleware `redirect-https` เพราะ `som-admin` ยังใช้ — ลบแล้ว admin ได้ `404`) | `301 https://shop.localhost:30081/`, `som-web-… 1.7`; HPA behavior เดิม (window 60) ยังอยู่เพราะ chart ไม่ได้ตั้ง field นี้; annotation change-cause เดิมยังอยู่ | การ์ดหลังร้าน `admin.localhost` ยังเข้าได้ |
| 12.6 อัปเกรดเป็น 1.8 ระหว่างลูกค้าเข้า | หน้าต่าง 2: `bash hit.sh -q https://shop.localhost:30081/api/whoami 400 0.1` | `helm upgrade som charts/som-shop -n som-shop -f charts/values-prod.yaml --set web.image.tag=1.8 --wait` → **conflict อีกครั้ง** `.spec.template.spec.containers[name="web"].image` → ใส่ `--force-conflicts` | 15 วินาที, `ok=400 err=0` (ร้านใหม่ som-prod), `ok=300 err=0` (ร้าน adopt); หลังจากนี้ upgrade/rollback ไม่ต้อง force | ว่า force ครั้งเดียวพอบนร้านนักศึกษา |
| 12.7 ประวัติและย้อนรุ่น | ดูสมุด + ย้อนไป revision ที่เป็น 1.7 | `helm history som -n som-shop`, `helm rollback som <rev 1.7> -n som-shop --wait` ระหว่าง hit.sh | rollback 11 วินาที `ok=300 err=0`; ได้ revision ใหม่ `Rollback to N`; **APP VERSION ในตาราง history = 1.7 ทุกแถว** (มาจาก Chart.yaml ไม่ใช่ image); rollback ไม่ใส่เลขไปรุ่นก่อนหน้าแม้ `failed` | เลข revision (ขึ้นกับว่าเจอ failed กี่ครั้ง) |
| 12.8 ซองในสมุด | ถอด release Secret ของ prod | `kubectl -n som-shop get secret sh.helm.release.v1.som.v2 -o jsonpath='{.data.release}' \| base64 -d \| base64 -d \| gzip -d \| python3 -c …` | manifest มี `DATABASE_URL: "postgres://som:meow1234@…"` แม้ไม่ได้ `--set` | — |
| 12.9 ปิดสาขา dev | uninstall + PVC | `helm uninstall som -n som-dev`, `kubectl -n som-dev get pvc`, ติดตั้งใหม่รหัสเดิม → ออเดอร์อยู่ / (ผลจริง) รหัสใหม่ → hook ล้ม | `data-som-db-0 Bound` ค้าง; `failed post-install: resource Job/som-dev/som-seed not ready … Job Failed. failed: 1/1`; ลบจริง `kubectl delete ns som-dev` | — |
| 12.10 ตรวจรับร้าน + ปิดบท | checklist + GitOps/Kustomize/operator | `helm test som -n som-shop --logs`, `helm list -A`, `kubectl top pod -n som-shop` | `Phase: Succeeded`; 3–4 release (traefik, metrics-server, som/som-shop, [som/som-dev]) | — |

**ทางสำรอง (ไม่มีร้านบท 013)**: `kubectl create ns som-shop` แล้ว `helm install som charts/som-shop -n som-shop -f charts/values-prod.yaml --set db.password=meow1234 --wait` (ทดสอบแล้วใน `som-prod`: 16 วินาที, `301`, `https` ตอบ `1.7`, `curl --cacert` ด้วยใบจาก `som-tls` ผ่าน, HPA `cpu: 8%/50%`, upgrade 1.8 `ok=400 err=0` ช่วง 1.7→1.8 = 91/309, rollback `Rollback to 1` `ok=300 err=0`)

**คำถามท้าย LAB**: ทำไม adopt ร้านได้แต่ adopt Traefik ไม่ได้, ทำไม upgrade แรกหลัง adopt ยัง conflict, rollback เลขอะไร/ทำไมไม่ถอยเลข, PVC ทำไมค้าง, ใครอ่านรหัสใน release ได้, GitOps จะเก็บอะไรใน Git

---

## 5. จุดที่ต้องยืนยันตอนเขียน README/LAB ฉบับจริง

1. **SSA conflict บนร้านจริงของนักศึกษา** (12.4/12.6): รายการ field ต่างตามประวัติบท 013 (เช่นใช้ `kubectl set image` 1.6) — ทดสอบด้วยการไล่บท 013 LAB 11 ให้ครบก่อน adopt
2. **เลข revision** ใน LAB 4 และ 12 (ขึ้นกับจำนวนครั้งที่ล้ม) → ภาพที่มีเลข revision เป็น `needs_test`
3. **เวลา**: install ทั้งร้าน 16–17 วินาที, ย้าย Traefik 18 วินาที / err ~17 วินาที, rollback-on-failure ~42 วินาที — บนเครื่อง 4 core จริงและ image ที่ยังไม่อยู่ใน Node
4. `--dry-run=server` ไม่จับ spec.type ผิด — ทดสอบซ้ำ/ดู issue helm 4 ก่อนเขียนเป็นข้อสรุป
5. ARM: podinfo, nginx:1.16.0 (helm create), registry:2, httpd:2.4-alpine, curlimages/curl, traefik, metrics-server เป็น multi-arch (ยังไม่ลองบน ARM จริง); postgres ใช้ `--platform linux/arm64`
6. Pod Security: namespace ที่ `--create-namespace` สร้างไม่มี label `pod-security.kubernetes.io/warn` (chart ผ่าน restricted อยู่แล้ว) — ตัดสินใจว่าจะ label เองหรือไม่
7. Ingress `dev.shop.localhost` ใน browser ของนักศึกษา (Chrome แปลง `*.localhost` ได้; Safari/Firefox ดูทางสำรองบท 012)
8. helm-diff (LAB เสริม) ต้อง pin v3.15.15 หรือใหม่กว่า
9. สถานะ `helm list` ที่แสดง release `uninstalled` โดยไม่ใส่ตัวกรอง (เห็นจริงใน pre-check — ยืนยันซ้ำ)
10. ผล `helm uninstall` ของ release ที่ adopt ล้ม (ลบ SA/Service ที่ถูกติด label แล้ว) — ยืนยันซ้ำก่อนใส่เป็นคำเตือน

---

## 6. อุปมาใหม่ของบท (ใช้ในภาพ)

| แนวคิด | อุปมา |
|---|---|
| chart | ชุดแฟรนไชส์ร้านสำเร็จรูป: กล่องพร้อมคู่มือ แม่พิมพ์ และใบสั่ง |
| values.yaml | ใบสั่งปรับแต่งร้าน (สี ชื่อ จำนวนบูธ) |
| templates | แม่พิมพ์ป้าย/บูธที่เว้นช่องว่างให้เติม |
| _helpers.tpl | ตรายางที่ใช้ซ้ำ |
| values.schema.json | ด่านตรวจใบสั่ง |
| release | ร้านสาขาที่เปิดจริงจากชุดแฟรนไชส์ (ป้ายชื่อสาขา) |
| revision | สมุดบันทึกการปรับปรุงร้าน (หน้าละ 1 รุ่น) |
| repository / Artifact Hub | แคตตาล็อกแฟรนไชส์ |
| OCI registry | โกดังเก็บชุดแฟรนไชส์ |
| helm (CLI) | หุ่นยนต์ผู้รับเหมาติดตั้งร้าน (หมวกนิรภัยสีส้ม ไม่ใช่หมวกเหล็กโบราณ) |
| hook | ขั้นตอนพิเศษก่อน/หลังเปิดร้าน (เช่น เติมสินค้าเข้าชั้น) |
| helm test | ผู้ตรวจรับร้าน |
| release Secret | สมุดบันทึกเก็บในตู้ของโซน มีสำเนาใบสั่งข้างใน |
| server-side apply / field manager | ป้ายชื่อเจ้าของบนแต่ละช่องของร้าน |
| conflict | ช่องที่มีป้ายเจ้าของ 2 คนแย่งกัน |
| --take-ownership | ติดป้ายสาขาใหม่บนร้านเดิม |
| subchart | กล่องย่อยในกล่องแฟรนไชส์ |
| GitOps (Argo CD/Flux) | หุ่นยนต์เฝ้าแฟ้มแผนร้าน (ตอนท้าย) |

ไฟล์ storyboard: `images.json` (T/L), `build_images.py`, `imgcommon.py` และ `014_kubernetes_helm/0{1_Theory,2_LAB}/images/imagegen-prompts.md`
