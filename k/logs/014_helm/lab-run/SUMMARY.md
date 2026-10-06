# สรุปผลทดสอบ LAB บท 014 (Helm) — รันจริงทุกข้อ

- วันที่: 5–6 ต.ค. 2569 (host UTC 22:39–23:13 = เวลาไทย 05:39–06:13)
- container: `k8s-lab-helm014-0044d7` (owner `helm014`) จาก `tuchsanai/devtools-kind:2569_1` (ID `8108a1bc7901`) `--privileged --hostname k8s-lab --cpus=4 --memory=8g` ไม่มี bind mount; SSH 2225, NodePort 30080–30082 → 30100–30102 — **ยังเปิดไว้สำหรับถ่ายภาพ** (ดู `handoff.md`)
- เครื่องมือ: helm v4.3.0, kubectl v1.37.1, kind 0.33.0, Kubernetes v1.37.0 (3 Node, amd64), k8s-up 54.6 วินาที
- ไม่ได้แตะ `k8s-lab` ของผู้เรียน, `deep_vision_5090_vllm` หรือ `k8s-lab-tuchsanai-07a1dc` (ของ agent อื่น); โควตารวมตอนรัน 2/3; ไม่มีการ push ไป registry ภายนอก (OCI ใช้ `registry:2` ใน dockerd ของ container แล้วลบทิ้ง)
- log: `labNN.log` (คำสั่ง + output จริง, `set -v`), `prep-ch012-013.log`, `lab02-explore.log`/`lab03-explore.log` (รอบสำรวจที่พบเรื่อง values — รัน LAB 2–4 ใหม่ให้เลข revision ตรงกับลำดับนักศึกษา), `lab10-adopt-experiment.log`, `labx.log`, `handoff-setup.log`, `handoff-check.log`

## จุดเริ่ม: สภาพท้ายบท 013 บนคลัสเตอร์นี้ (`prep-ch012-013.log`, 308 วินาที)

ไล่ตามที่นักศึกษาทำจริง: บท 012 LAB 0 (postgres image-archive 19.6 วินาที, build 1.5 = 42.4 วินาทีไม่มี cache, 1.6 = 6.0 วินาที) → LAB 1 (Traefik static + CRD) → LAB 10 (ทางคลัสเตอร์ใหม่, Secret 3 ซอง, ออเดอร์ 3 รายการ, annotate + rollout restart + `set image 1.6`) → บท 013 LAB 1 (metrics-server static) → LAB 11 (build 1.7 = 33 วินาที, `60-hpa.yaml`, `set-last-applied`, apply `15-config`/`20-web`, `70-customers` scale 1 แล้ว 0) ได้สภาพ: `som-web` 1.7 + HPA 2–6, `customers 0/0`, Ingress `som-shop`/`som-admin`, Middleware `redirect-https`/`admin-auth`, rollout history 4 แถว, `orders=3`, `helm list -A` ว่าง
หมายเหตุ: บท 012 สั่งออเดอร์ด้วย `{"productId":4}` ได้ `ข้อมูลไม่ถูกต้อง` ต้องใช้ `{"product_id":4,"qty":1}`

## ผลรายข้อ

| LAB | ผล | เวลา/ค่าจริงสำคัญ |
|---|---|---|
| 0 เตรียม + 1.8 | ✅ | `Version:"v4.3.0"`, `HELM_MAX_HISTORY="10"`; build+load 1.8 **6.5 วินาที** (มี cache 1.7); `docker run … APP_VERSION` = `1.8`; Node มี 1.5/1.6/1.7/1.8 + postgres |
| 1 แคตตาล็อก | ✅ | `traefik/traefik 41.6.1 v3.7.13` (41.6.0, 41.5.0 v3.7.13, 41.4.0 v3.7.12), `metrics-server 3.14.0 0.9.0`, `podinfo 6.15.0`; hub มี `quench-traefik 0.0.21`, `aigisuk 0.1.1 2.7.0-rc2`, `kubeblocks 41.6.0`, `k3s 41.4.2+up41.4.0`; podinfo `apiVersion: v1`; `helm pull --untar` ได้ crds 25 ไฟล์ |
| 2 podinfo | ✅ | install `--wait` **12.2 วินาที** (รอบสำรวจ 8.6), `REVISION: 1`, `APPLY_METHOD: server-side apply`, managedFields `helm Apply` + `kube-controller-manager Update`, Secret `sh.helm.release.v1.hello.v1`, curl ได้ `"message": "สวัสดีจากร้านน้องส้ม"`; namespace จาก `--create-namespace` มี label แค่ `kubernetes.io/metadata.name`, `name` |
| 3 values | ✅ (เปลี่ยนคำสั่ง) | rev 2 `-f` + `--set` 24.5 วินาที `"message": "--set ชนะ"`, `#ff8c00`, Ingress `podinfo.localhost`; **rev 3 `--set replicaCount=1` อย่างเดียว → values เหลือ `replicaCount: 1`, Ingress หาย, curl `404`**; rev 4 `-f`, rev 5 `--reuse-values --set` จำค่าเดิม |
| 4 history/rollback | ✅ | rev 6 image ผิดไม่ใส่ `--wait` = `deployed` 0.2 วินาที + `ErrImagePull`; rev 7 `Rollback to 5` (11.9 วินาที); `--atomic` → `Flag --atomic has been deprecated, use --rollback-on-failure instead`; `--rollback-on-failure --timeout 40s` **43.0 วินาที** `Error: UPGRADE FAILED: release hello failed, and has been rolled back due to rollback-on-failure being set: resource Deployment/helm-demo/hello-podinfo not ready. status: InProgress, message: Updated: 2/3` → rev 8 `failed`, **rev 9 `Rollback to 7`**; `helm rollback hello` (ไม่ใส่เลข) → **rev 10 `Rollback to 8`** (ไป rev ที่ failed, Pod `ErrImagePull`) → `rollback hello 9` rev 11; Secret เหลือ v2–v11 (**v1 ถูกลบเพราะเก็บ 10 รุ่น**); ถอดได้ key `apply_method chart config hooks info manifest name namespace version`; `uninstall --keep-history` → **`helm list` (ไม่ใส่ตัวกรอง) แสดง `uninstalled` rev 11** เหมือน `--uninstalled`; install ชื่อเดิม `cannot reuse a name that is still in use`; `rollback hello 11` → rev 12 deployed; uninstall จริง → `Error: release: not found` |
| 5 helm create | ✅ | lint `[INFO] Chart.yaml: icon is recommended` `1 chart(s) linted, 0 chart(s) failed`; scaffold มี `httproute.yaml`; install **7.4 วินาที**; test `Phase: Succeeded` + `'index.html' saved`; **image ไม่มี `tree`** ใช้ `find mychart -type f \| sort` |
| 6 debug | ✅ | indent: `yaml: line 24: mapping values are not allowed in this context` (`--debug` เห็น `managed-by: Helm  shop: som`); `function "toYml" not defined`; required: `execution error at (mychart/templates/deployment.yaml:41:21): ต้องใส่ image.repository`; v3 (มีบรรทัด `type:`) → **`chart type is not valid in apiVersion 'v3'. It is valid in apiVersion 'v2'`**, ลบ `type:` แล้ว → `apiVersion 'v3' is not valid. The value must be either "v1" or "v2"` (ทั้งมี/ไม่มี `HELM_EXPERIMENTAL_CHART_V3=1`), template → `Error: invalid chart apiVersion`; **`--dry-run=server` + `service.type=NodePortt` → `STATUS: pending-install` `Dry run complete` (ไม่จับ — ยืนยันซ้ำ)**, `helm template \| kubectl apply --dry-run=server` → `spec.type: Unsupported value: "NodePortt"`; install จริง → `server-side apply failed … Unsupported value` และเหลือ release `web2 failed` (ต้อง uninstall) |
| 7 template | ✅ | ConfigMap 5 การ์ดจาก `range` (เรียงตามตัวอักษร), `replicas: 2` หายเมื่อ `hpa.enabled=true`, `toYaml \| nindent 12`, `checksum/config` เปลี่ยน (`26b21079…` → `25db4af1…`), `fullnameOverride=shop2` → `shop2-*` |
| 8 dev/prod/schema | ✅ | **dev 10 object, prod 13** (นับ Job hook + Pod test; ไม่นับ = 8/11); `- at '/web/image/tag': 'not' failed`, `- at '/web/replicas': maximum: got 9, want 6`, `'Shop_Localhost' does not match pattern`; lint ไม่มีรหัส `level=WARN msg="missing required values"` ×2 แต่ `0 chart(s) failed`; template → `execution error at (som-shop/templates/web.yaml:29:28): ติดตั้งครั้งแรกต้องตั้งรหัสฐานข้อมูล…`; template 2 ครั้งได้ใบรับรองต่างกัน (lookup ว่าง); Traefik schema: `additional properties 'logs' not allowed` (และ `accesslog` ตัวเล็ก) |
| 9 hook + test | ✅ | install dev **17.9 วินาที**, NOTES ภาษาไทย, `som-web-… 1.7`, `orders=0 products=6`, หน้าเว็บมี `ร้านอาหารแมวน้องส้ม (dev)` + `🧪 สาขาทดลอง…`; Job seed ถูกลบหลังสำเร็จ (watch เห็น `som-seed-…` → `Completed`); test `Phase: Succeeded` 3 บรรทัด; ถอด Secret ได้ `{"db": {"password": "meow1234"}, …}` + `DATABASE_URL: "postgres://som:meow1234@…"`; upgrade ไม่ส่งรหัส → lookup คงรหัส, ประกาศใหม่ได้ Pod ใหม่เอง (9.7 วินาที); PSA: `kubectl label --dry-run=server … enforce=restricted` ไม่มี warning (chart ผ่าน restricted) |
| 10 add-on | ✅ | install ทับ → `ServiceAccount "traefik" … invalid ownership metadata` (ไม่มี release ค้าง); **ย้าย Traefik 19 วินาที, hit.sh 600 ครั้ง `ok=528 err=72` ช่วง err 18.8 วินาที** (61 `SSL_ERROR_SYSCALL` + 11 `Connection reset by peer`); `404 page not found`, dashboard 200, IngressClass `traefik (default)`, 301 → 30081, admin 401/200, `orders=3`; metrics-server install ทับ error เดียวกัน, ย้าย **21 วินาที**; **APIService `False (FailedDiscoveryCheck)` ทันทีหลัง `--wait`** → `True` ภายใน ~45 วินาที; `kubectl top nodes` ได้; flag ใน render ไม่มีเครื่องหมายคำพูด (`- --api.insecure=true`) |
| 10 ทดลองแยก (`traefik-test`) | ✅ (ยืนยันคำเตือน) | take-ownership → conflict (Service `.spec.selector`, Deployment 11 field) + rev 1 failed; force-conflicts → `spec.selector … field is immutable` rev 2 failed; **`helm uninstall` → `skipping delete of resource not owned by this release` เก็บแค่ Deployment, ลบ SA + Service ที่ถูกยึดไปแล้ว** (สำเนาไม่มี NodePort จึงเห็น Service conflict 1 ไม่ใช่ 3) |
| 11 OCI | ✅ | `som-shop-0.1.0.tgz` 5987 ไบต์; push ก่อน login `basic credential not found`; login URL `invalid registry "http://localhost:5000"`; `Login Succeeded`; `Pushed: localhost:5000/charts/som-shop:0.1.0` `Digest: sha256:ef59e9e3…`; install จาก oci **17.0 วินาที** `oci.shop.localhost` ตอบ; ใช้ digest ได้; config.json `{'localhost:5000': {'auth': 'c29tOm...'}}`; logout แล้ว `basic credential not found` |
| 12 ร้านพร้อมส่ง | ✅ | ดูด้านล่าง |
| เสริม | ✅ | helm-diff v3.15.15 ไม่ใส่ `--verify=false` → `plugin source does not support verification…`; `helm plugin list` `diff 3.15.15 cli/v1 legacy unknown unknown`; diff เห็น `app.kubernetes.io/version: "1.8"` → `"1.7"`; umbrella `harbor-addons` dependency update (podinfo จาก `oci://ghcr.io`) → `Chart.lock`, `charts/*.tgz`, `condition: podinfo.enabled` ทำงาน |
| ARM | ⚠️ ไม่ได้ทดสอบ | ไม่มีเครื่อง ARM (podinfo, nginx:1.16.0, registry:2, httpd:2.4-alpine, curl, traefik, metrics-server คาดว่า multi-arch; postgres ต้อง `--platform linux/arm64`) |

### LAB 12 (จากร้านบท 013 ของคลัสเตอร์นี้)

| ขั้น | ผลจริง |
|---|---|
| 12.1 | `helm list -A` มี traefik/metrics-server (จาก LAB 10), `som-web` 2/2, `customers 0/0`, `orders=3`; managedFields ของ `som-web`: `kube-controller-manager`, `kubectl-rollout`, `kubectl` (set image), `kubectl-client-side-apply` |
| 12.2 | lint prod/dev `0 chart(s) failed` |
| 12.3 dev | **18.0 วินาที**, test Succeeded, `theme-sunset`, `ร้านอาหารแมวน้องส้ม (dev)` |
| 12.4 (ก) | `Secret "som-tls" … invalid ownership metadata` ไม่มี release |
| 12.4 (ข) | **conflict กับ `kubectl-client-side-apply`: ConfigMap `som-web-config` 3 (`.data.SHOP_EYEBROW/FOOTER/PROMO`), Deployment 2 (`env[name="POD_NAMESPACE"].valueFrom.fieldRef`, `initContainers[name="wait-for-db"].command`), StatefulSet 1 (`.spec.volumeClaimTemplates`)** → rev 1 `failed` (ตรงกับ pre-check) |
| 12.4 (ค) | **rev 2 deployed 16.4 วินาที**, `orders=3` อยู่ครบ, fingerprint `som-tls` ก่อน/หลังเท่ากัน (`DF:E2:AD:87:…` ใบจากบท 012 SAN รวม admin.localhost), รหัสจาก lookup, change-cause `1.7 เพิ่ม /api/work + HPA` ยังอยู่, HPA window 60 ยังอยู่; rev 1 เปลี่ยนเป็น `superseded` (description ยังเป็นข้อความ failed) |
| **พบใหม่** | **Deployment มี initContainer 2 ตัว `wait-for-db db-seed`** — `db-seed` ของบท 013 ยังอยู่เพราะ `kubectl-client-side-apply` เป็นเจ้าของ (chart ใช้ hook seed แทน) → เพิ่มขั้น 12.5c ถอดด้วย `kubectl patch --type=json` (มี `test` ชื่อกันลบผิดตัว) ระหว่าง hit.sh **`ok=250 err=0`** |
| 12.5 | ลบ Ingress `som-shop` + Deployment `customers` (เก็บ `redirect-https` ให้ `som-admin`) → `301 https://shop.localhost:30081/`, admin 200, หัวเว็บ `⚓ ท่าเรือ Kubernetes · Helm`, แถบ `🎉 เปิดสาขาใหม่ด้วย Helm คำสั่งเดียว` |
| 12.6 | ไม่ใส่ force → `Apply failed with 1 conflict: … .spec.template.spec.containers[name="web"].image` → **rev 3 failed** (image ยัง 1.7); `--force-conflicts` → **rev 4, 15 วินาที, `ok=400 err=0` (1.7 = 84, 1.8 = 316)** |
| 12.7 | `rollback som 2` → **rev 5 `Rollback to 2`, 11 วินาที, `ok=300 err=0` (215/85)**; APP VERSION ในตาราง history = `1.7` ทุกแถว; upgrade 1.8 ซ้ำ **ไม่ต้อง force** → rev 6, 15 วินาที, `ok=300 err=0` |
| 12.8 | ถอด `sh.helm.release.v1.som.v2` (ไม่ได้ `--set` รหัส) → `DATABASE_URL: "postgres://som:meow1234@…"`, `POSTGRES_PASSWORD: "meow1234"` และ **manifest มี `tls.key` ของใบรับรองด้วย** (แสดงเฉพาะ `LS0tLS1CRUdJTiBQUklW…`) |
| 12.9 | uninstall dev → เหลือ `data-som-db-0 Bound`; ติดตั้งรหัสเดิม 11.9 วินาที `orders=1` กลับมา; **รหัสใหม่ + `--wait --timeout 90s` → 90 วินาที `Error: INSTALLATION FAILED: resource Deployment/som-dev/som-web not ready. status: InProgress, message: Available: 0/1`** (ไม่ถึง hook); **รหัสใหม่ไม่ใส่ `--wait` → 45.7 วินาที `failed post-install: resource Job/som-dev/som-seed not ready. status: Failed, message: Job Failed. failed: 1/1`**; upgrade release ที่ failed ด้วยรหัสเดิมแก้ได้ |
| 12.10 | prod test Succeeded (`whoami: … 1.8`), `curl --cacert` ผ่าน, `kubectl top pod` ได้, `helm list -A` 3 release (+ dev ตอนตั้งฉาก = 4) |

## การเปลี่ยนแปลงจากแผน

1. **โครงไฟล์**: ไฟล์ต่อ LAB อยู่ใต้ `02_LAB/labs/` — `lab01-catalog/` (ที่ pull traefik), `lab03-values/podinfo-values.yaml`, `lab05-first/`, `lab06-debug/make-broken.sh` (**ใหม่**: สร้าง broken-indent/func/required/v3 ให้แทนการพิมพ์ sed เอง), `lab10-addons/{traefik,metrics-server}-values.yaml` + `lab10-addons/static-old/` (สำเนา `00-traefik.yaml`, `traefik-crds-v3.7.13.yml`, `00-metrics-server.yaml` จากบท 013 — บท 014 ไม่ต้องพึ่งโฟลเดอร์บทก่อน), `lab11-registry/`, `labx-extra/harbor-addons/` (**ใหม่**); `charts/som-shop` + `charts/values-{dev,prod}.yaml` (= pre-check ไม่แก้), `hit.sh` (สำเนาบท 013), `som-shop-v10/app` (สำเนา v9 ไม่มี node_modules/.next เพิ่มแค่บรรทัดคอมเมนต์ `1.8` ใน Dockerfile), `.gitignore`; **ยังไม่ได้เขียน `02_LAB/README.md`** (นอกขอบเขตงานนี้)
2. **LAB 3**: Helm 4.3 `upgrade` ที่ไม่ส่ง values เลย = reuse ค่าเดิม (ทดสอบใน `lab03-explore.log`: values ยังครบ) — ฉาก "ค่ากลับค่าเริ่มต้น" ต้องใช้ `helm upgrade … --set replicaCount=1` (ส่งบางค่า ไม่ส่ง `-f`) ได้ `replicaCount: 1` อย่างเดียวและ `404`
3. **LAB 4**: เลข revision ตามลำดับใหม่: rollback-on-failure → rev 8 failed / **rev 9 `Rollback to 7`** (ไม่ใช่ 5), rollback ไม่ใส่เลข → `Rollback to 8`, keep-history rollback ใช้ **11** → rev 12
4. **LAB 5**: `tree` ไม่มีใน image → `find`
5. **LAB 6**: ข้อความ v3 ต่างตามว่ามี `type:` หรือไม่ (ดูตาราง); make-broken.sh คง `type:` ไว้ → นักศึกษาเห็น `chart type is not valid in apiVersion 'v3'` ก่อน
6. **LAB 8**: จำนวน object dev/prod = 10/13 (รวม hook+test) ไม่ใช่ 9/12
7. **LAB 10**: ใช้ไฟล์ static ใน `labs/lab10-addons/static-old/`; รอ APIService ~20–45 วินาทีหลัง install ก่อน `kubectl top`
8. **LAB 12**: เพิ่มขั้น 12.5c ถอด initContainer `db-seed`; ฉากรหัสผิดต้อง **ไม่ใส่ `--wait`** ถึงเห็น `failed post-install` (ถ้าใส่ `--wait` จะล้มที่ Deployment หลัง timeout)
9. ชื่อ release/namespace ตามแผน (`hello`/`helm-demo`, `web`/`first`, `som`/`som-dev`+`som-shop`, `oci-som`/`oci-demo`); เก็บกวาด `first`, `helm-demo`, `oci-demo`, `som-dev` (ท้าย LAB 9) ตามลำดับ

## ป้าย/ข้อความในภาพ storyboard ที่ไม่ตรงผลจริง (`images.json`)

| ภาพ | ป้าย/คำบรรยายปัจจุบัน | ผลจริง | ควรใช้แทน |
|---|---|---|---|
| **T27** | label 1 `upgrade ไม่ส่งใบสั่ง = กลับค่าเริ่มต้น` | ไม่ส่งเลย = reuse ค่าเดิม; ส่งบางค่าถึงรีเซ็ต | `upgrade ส่งแค่บางค่า = ค่าอื่นกลับค่าเริ่มต้น` |
| **L08** | label 1 `upgrade ไม่ส่ง values`; caption "upgrade โดยไม่ส่ง values = เหลือแค่ค่าที่ส่งครั้งนี้" | ต้อง `--set replicaCount=1` อย่างเดียว | label 1 `upgrade --set replicaCount=1 อย่างเดียว`; caption "upgrade ที่ส่งแค่ --set บางค่า (ไม่ส่ง -f) = เหลือแค่ค่าที่ส่งครั้งนี้ ค่าอื่นกลับค่าเริ่มต้น" |
| **L10** (needs_test) | label 4 `Rollback to 5` | rev 8 failed → rev 9 `Rollback to 7` (43 วินาที) | `Rollback to 7` (caption "~40 วินาที" ใช้ได้) |
| **L22** (needs_test) | label 1 `ประตูปิดชั่วคราว ~17 วินาที`; caption "(~17 วินาที)" | ย้ายรวม 19 วินาที, ช่วง err 18.8 วินาที (72/600) | `ประตูปิดชั่วคราว ~19 วินาที` |
| **L27** (needs_test) | label 3 `~17 วินาที`; caption "(~17 วินาที)" | 18.0 วินาที (LAB 12) / 17.9 (LAB 9) | `~18 วินาที` |
| **L28** (needs_test) | label 3 `orders=1 ยังอยู่` | ร้านท้ายบท 013 ของคลัสเตอร์นี้ `orders=3` (ค่าต่างตามนักศึกษา) | `ออเดอร์เดิมยังอยู่` (หรือ `orders=3 ยังอยู่`) |
| **L32** (needs_test) | `failed post-install` / `Job Failed` | จริงเฉพาะคำสั่ง **ไม่ใส่ `--wait`** (45.7 วินาที); ใส่ `--wait` ได้ `Deployment … not ready … Available: 0/1` | ป้ายใช้ได้ถ้า README ให้รันไม่ใส่ `--wait` (แนะนำ) ไม่งั้นเปลี่ยน label 2/3 เป็น `som-web not ready` / `Available: 0/1` |
| L01, L14, L20, L29, L30, L33 (needs_test) | — | ตรง (`helm v4.3.0`, `Dry run complete`/`Unsupported value`, `traefik 41.6.1`/`metrics-server 3.14.0`, 1.7→1.8 `err=0` + upgrade แรกต้อง force, `Rollback to N` (จริง = `Rollback to 2`), dev test ผ่าน/prod HTTPS+HPA/rollback ระบุเลข) | ไม่ต้องแก้ |
| T13, T15, T32, T33, T34, T36–T38, T41, L06, L11, L17, L19, L21, L24 | — | ตรงกับผลจริง (T34 `ถอยไปหน้าก่อนหน้า แม้เป็นรุ่นที่ล้ม` ยืนยันแล้ว: `Rollback to 8`) | ไม่ต้องแก้ |

## ข้อควรระวังสำหรับนักศึกษา (ใส่ใน README)

- ใส่ `--wait` ทุกครั้งที่ install/upgrade (ไม่ใส่ = `deployed` ทั้งที่ Pod `ErrImagePull`) และ **ระบุเลข revision ทุกครั้งที่ rollback** (ไม่ใส่เลขไป rev ก่อนหน้าแม้เป็น failed)
- upgrade ที่ส่ง `--set` บางค่าโดยไม่ส่ง `-f` = ค่าอื่นกลับค่าเริ่มต้น → ส่ง `-f` ทุกครั้งหรือใช้ `--reuse-values`
- `--dry-run=server` ของ Helm 4.3 ไม่ตรวจ field ผิด ใช้ `helm template … | kubectl apply --dry-run=server -f -` เพิ่ม
- install ที่ล้มยังทิ้ง release `failed` ไว้ (เช่น `web2`) ต้อง `helm uninstall` หรือ `upgrade --install`
- **ห้าม `helm uninstall` release ที่ adopt ล้ม** — ลบ SA/Service ที่ถูกยึดไปแล้ว (ประตูปิด) ทำแค่ "ผลจริง ไม่ต้องทำตาม"
- ย้าย Traefik = ประตูปิด ~19 วินาที (ระบบจริงต้องมีช่วงปิดปรับปรุงหรือ blue/green); อย่าลบ `traefik-crds-v3.7.13.yml` (Middleware ของร้านอยู่บน CRD)
- รับร้านเดิมต้อง `--take-ownership --force-conflicts` และ upgrade แรกที่เปลี่ยน image ต้อง `--force-conflicts` อีกครั้ง (ครั้งเดียว); field เก่าที่ chart ไม่ได้ตั้ง (initContainer `db-seed`, annotation `restartedAt`, change-cause, HPA behavior) ยังอยู่
- release Secret เก็บรหัสฐานข้อมูล **และ `tls.key`** ในรูป base64+gzip — ใครอ่าน Secret ใน namespace ได้ = อ่านได้; ห้าม commit values ที่มีรหัส
- PVC `data-som-db-0` ค้างหลัง uninstall — ติดตั้งใหม่ต้องใช้รหัสเดิม ไม่งั้นร้านเปิดไม่ได้; ลบจริงต้อง `kubectl delete ns som-dev`
- namespace ที่ `--create-namespace` สร้างไม่มี label Pod Security (chart ร้านผ่าน restricted อยู่แล้ว ทดสอบด้วย `kubectl label --dry-run=server … enforce=restricted` ไม่มี warning) — แนะนำให้ label `warn=restricted` เองถ้าต้องการให้เหมือน `som-shop`
- Pod เก่าของหน้าร้านแสดงสถานะ `Error` ชั่วครู่ตอนถูกปิดระหว่าง rollout (exit code หลัง SIGTERM) ไม่ใช่ปัญหา (hit.sh `err=0`)
- browser: Chrome/Edge แปลง `*.localhost` เอง; ถ้า map พอร์ตอื่น (เช่น container ทดลอง) ต้องคงพอร์ต 30081 ใน URL เพราะ redirect middleware บังคับพอร์ต
- หลัง metrics-server ติดตั้งด้วย chart รอ ~30 วินาทีก่อน `kubectl top`

## เหตุขัดข้องระหว่างทดสอบ (เฉพาะ container ทดลอง)

ในการทดลองแยก `traefik-test` รอบแรก สคริปต์แปลง namespace พลาดบรรทัด ServiceAccount ทำให้ `kubectl delete -f` ของรอบสองลบ **ServiceAccount `traefik/traefik` ตัวจริงในคลัสเตอร์ทดลอง** ไป แก้โดย `kubectl apply -f static-old/00-traefik.yaml` + `rollout restart` ก่อนเริ่ม LAB 10 (ร้านตอบ `orders=3` ปกติ, บันทึกใน `lab10-adopt-experiment.log`) ไม่กระทบผล LAB 10 เพราะ LAB 10 ลบ Traefik static ทั้งชุดอยู่แล้ว และไม่กระทบเครื่องของผู้เรียน

## container ที่เปิดไว้

`k8s-lab-helm014-0044d7` — SSH `2225`, NodePort `30100/30101/30102` (= 30080/30081/30082), gateway `172.18.0.1` — รายละเอียดฉากใน `handoff.md`
