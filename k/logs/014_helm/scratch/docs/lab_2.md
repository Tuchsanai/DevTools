## LAB 5: ชุดแฟรนไชส์ชุดแรกของเรา (helm create)

<p align="center" id="fig-12">
  <img src="images/12-lab05-open.png" alt="รูปที่ 12 LAB 5 helm create" width="900"><br>
  <em><b>รูปที่ 12</b> LAB 5: helm create mychart → lint → template → install → helm test --logs</em>
</p>

**เป้าหมาย:** สร้าง chart ตัวอย่างด้วย `helm create` อ่านโครงสร้าง ตรวจ render ติดตั้ง และสั่งผู้ตรวจรับร้าน

**ไฟล์:** สร้างใน `labs/lab05-first/mychart/` (ไม่เข้า git)

### ขั้นที่ 1: สร้างและดูโครง

```bash
cd /workspace/014_kubernetes_helm/02_LAB/labs/lab05-first
helm create mychart
find mychart -type f | sort
grep -vE "^\s*#|^$" mychart/Chart.yaml
grep -nE "^replicaCount|^image:|^  repository|^  tag|^service:|^  type|^  port" mychart/values.yaml
```

```text
Creating mychart
mychart/.helmignore
mychart/Chart.yaml
mychart/templates/NOTES.txt
mychart/templates/_helpers.tpl
mychart/templates/deployment.yaml
mychart/templates/hpa.yaml
mychart/templates/httproute.yaml
mychart/templates/ingress.yaml
mychart/templates/service.yaml
mychart/templates/serviceaccount.yaml
mychart/templates/tests/test-connection.yaml
mychart/values.yaml
apiVersion: v2
name: mychart
description: A Helm chart for Kubernetes
type: application
version: 0.1.0
appVersion: "1.16.0"
6:replicaCount: 1
9:image:
10:  repository: nginx
14:  tag: ""
53:service:
55:  type: ClusterIP
57:  port: 80
```

> image `k8s-lab` **ไม่มีคำสั่ง `tree`** (`tree: command not found`) จึงใช้ `find ... | sort` ดูโครงแทน

scaffold ของ Helm 4 ได้ chart `apiVersion: v2` ที่มีครบทุกส่วนของทฤษฎีหัวข้อ 4: `_helpers.tpl`, `NOTES.txt`, `tests/` และแม่พิมพ์ที่ปิดไว้ด้วย `if` (hpa, ingress และ **`httproute.yaml`** ของ Gateway API ที่เพิ่มมาใน Helm 4) ไม่มี `values.schema.json` image เริ่มต้นคือ `nginx` tag ว่าง (= `appVersion` `1.16.0`)

### ขั้นที่ 2: lint และ template

```bash
helm lint mychart
helm template web mychart | grep -E "^kind:|image:"
```

```text
==> Linting mychart
[INFO] Chart.yaml: icon is recommended

1 chart(s) linted, 0 chart(s) failed
kind: ServiceAccount
kind: Service
kind: Deployment
          image: "nginx:1.16.0"
kind: Pod
      image: busybox
```

lint ผ่าน (`[INFO]` เป็นแค่คำแนะนำ) render ได้ 4 object: ServiceAccount, Service, Deployment (`nginx:1.16.0` จาก `default .Chart.AppVersion`) และ Pod ทดสอบ (`busybox`) ส่วน hpa/ingress/httproute ไม่ถูก render เพราะค่าเริ่มต้นปิดไว้

### ขั้นที่ 3: ติดตั้งและตรวจรับ

```bash
time helm install web mychart -n first --create-namespace --wait
kubectl -n first get deploy,svc,pod
helm test web -n first --logs
kubectl -n first get pod
```

```text
NAME: web
LAST DEPLOYED: Tue Oct  6 05:52:11 2026
NAMESPACE: first
STATUS: deployed
REVISION: 1
DESCRIPTION: Install complete
NOTES:
1. Get the application URL by running these commands:
  export POD_NAME=$(kubectl get pods --namespace first -l "app.kubernetes.io/name=mychart,app.kubernetes.io/instance=web" -o jsonpath="{.items[0].metadata.name}")
  export CONTAINER_PORT=$(kubectl get pod --namespace first $POD_NAME -o jsonpath="{.spec.containers[0].ports[0].containerPort}")
  echo "Visit http://127.0.0.1:8080 to use your application"
  kubectl --namespace first port-forward $POD_NAME 8080:$CONTAINER_PORT

real	0m7.353s
NAME                          READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/web-mychart   1/1     1            1           7s

NAME                  TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)   AGE
service/web-mychart   ClusterIP   10.96.212.11   <none>        80/TCP    7s

NAME                               READY   STATUS    RESTARTS   AGE
pod/web-mychart-5fd4677f4c-5t8np   1/1     Running   0          7s
NAME: web
LAST DEPLOYED: Tue Oct  6 05:52:11 2026
NAMESPACE: first
STATUS: deployed
REVISION: 1
DESCRIPTION: Install complete
TEST SUITE:     web-mychart-test-connection
Last Started:   Tue Oct  6 05:52:19 2026
Last Completed: Tue Oct  6 05:52:26 2026
Phase:          Succeeded

POD LOGS: web-mychart-test-connection (wget)
Connecting to web-mychart:80 (10.96.212.11:80)
saving to 'index.html'
index.html           100% |********************************|   612  0:00:00 ETA
'index.html' saved

NAME                           READY   STATUS      RESTARTS   AGE
web-mychart-5fd4677f4c-5t8np   1/1     Running     0          15s
web-mychart-test-connection    0/1     Completed   0          7s
```

- ชื่อ object = `<release>-<chart>` (`web-mychart`) ตามตรายาง `mychart.fullname` ของ scaffold
- `helm test` สร้าง Pod `web-mychart-test-connection` ที่ `wget` ไปยัง Service ได้หน้า nginx (612 ไบต์) จบด้วย exit 0 = **`Phase: Succeeded`**
- Pod ทดสอบของ scaffold ค้างเป็น `Completed` เพราะไม่ได้ตั้ง `hook-delete-policy` ให้ลบเมื่อสำเร็จ (ชุดร้านใน LAB 9 ตั้งไว้)

### สิ่งที่เห็น

- `helm create` ได้ chart ที่ใช้งานได้ทันที (lint ผ่าน, install 7.4 วินาที, test `Succeeded`)
- อ่านแม่พิมพ์ของ scaffold เป็นตัวอย่างการใช้ `include`, `with`, `toYaml | nindent` จริง

**คำถามชวนคิด**

1. เปิด `mychart/templates/deployment.yaml` หาบรรทัด `image:` แล้วอธิบายว่า `nginx:1.16.0` มาจากไหนบ้าง
2. ถ้าแก้ `values.yaml` แล้วอยากให้คนอื่นรู้ว่า chart เปลี่ยน ต้องแก้อะไรใน `Chart.yaml`

**เก็บกวาด:** ยังไม่ลบ — LAB 6 คัดลอก `mychart` ไปทำแม่พิมพ์พัง และใช้ release `web` (namespace `first`) ต่อ

---

## LAB 6: แม่พิมพ์พัง: render และ debug

<p align="center" id="fig-13">
  <img src="images/13-lab06-open.png" alt="รูปที่ 13 LAB 6 แม่พิมพ์พัง" width="900"><br>
  <em><b>รูปที่ 13</b> LAB 6: ทำแม่พิมพ์พัง 4 แบบ แล้วหาจุดผิดด้วย helm lint / helm template --debug</em>
</p>

**เป้าหมาย:** อ่าน error ของ Helm 4 แต่ละแบบ หาบรรทัดที่ผิด และเห็นช่องโหว่ของ `--dry-run=server`

**ไฟล์:** `labs/lab06-debug/make-broken.sh` (คัดลอก `../lab05-first/mychart` เป็น `broken-indent`, `broken-func`, `broken-required`, `broken-v3` แล้วแก้ด้วย `sed` โฟลเดอร์ละ 1 จุด รันซ้ำได้)

### ขั้นที่ 1: สร้างแม่พิมพ์พัง

```bash
cd /workspace/014_kubernetes_helm/02_LAB/labs/lab06-debug
bash make-broken.sh
```

```text
=== broken-indent (บรรทัดที่ต่างจาก mychart)
>         {{- toYaml . | indent 2 }}
> podLabels: {shop: som}
=== broken-func (บรรทัดที่ต่างจาก mychart)
>         {{- toYml . | nindent 8 }}
>         {{- toYml . | nindent 8 }}
>         {{- toYml . | nindent 8 }}
=== broken-required (บรรทัดที่ต่างจาก mychart)
>           image: "{{ required "ต้องใส่ image.repository" .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
=== broken-v3 (บรรทัดที่ต่างจาก mychart)
> apiVersion: v3
```

### ขั้นที่ 2: indent แทน nindent (YAML พัง)

```bash
helm lint broken-indent
helm template web broken-indent 2>&1 | tail -3
helm template web broken-indent --debug 2>&1 | grep -n -B2 -A3 "shop: som" | head -12
```

```text
Error: 1 chart(s) linted, 1 chart(s) failed
==> Linting broken-indent
[INFO] Chart.yaml: icon is recommended
[ERROR] templates/deployment.yaml: unable to parse YAML: error converting YAML to JSON: yaml: line 24: mapping values are not allowed in this context

Error: YAML parse error on mychart/templates/deployment.yaml: error converting YAML to JSON: yaml: line 24: mapping values are not allowed in this context

Use --debug flag to render out invalid YAML
50-        app.kubernetes.io/instance: web
51-        app.kubernetes.io/version: "1.16.0"
52:        app.kubernetes.io/managed-by: Helm  shop: som
53-    spec:
54-      serviceAccountName: web-mychart
55-      containers:
```

`line 24` คือบรรทัดของ **ผล render** ของไฟล์นั้น ไม่ใช่บรรทัดใน template `--debug` พิมพ์ YAML ที่พังออกมาให้เห็น: `indent 2` ไม่ขึ้นบรรทัดใหม่ และ `{{-` ตัดบรรทัดก่อนหน้า label `shop: som` จึงไปต่อท้าย `managed-by: Helm` ในบรรทัดเดียวกัน (ทฤษฎีหัวข้อ 5.4)

### ขั้นที่ 3: ชื่อฟังก์ชันผิด

```bash
helm lint broken-func 2>&1 | tail -4
```

```text
[INFO] Chart.yaml: icon is recommended
[ERROR] templates/: parse error at (mychart/templates/deployment.yaml:18): function "toYml" not defined

Error: 1 chart(s) linted, 1 chart(s) failed
```

error นี้เกิดตอน **parse template** (ก่อน render) บอกไฟล์และบรรทัดของ template ตรง ๆ (`deployment.yaml:18`)

### ขั้นที่ 4: required

```bash
helm template web broken-required --set image.repository= 2>&1 | head -3
helm template web broken-required | grep "image:" | head -1
```

```text
Error: execution error at (mychart/templates/deployment.yaml:41:21): ต้องใส่ image.repository

Use --debug flag to render out invalid YAML
          image: "nginx:1.16.0"
```

`required` หยุด render พร้อมข้อความที่เราเขียนเองและตำแหน่ง `บรรทัด:คอลัมน์` ถ้ามีค่า (`nginx` จากค่าเริ่มต้น) ก็ผ่านตามปกติ

### ขั้นที่ 5: chart apiVersion v3

```bash
helm lint broken-v3 2>&1 | tail -4
HELM_EXPERIMENTAL_CHART_V3=1 helm lint broken-v3 2>&1 | tail -3
sed -i '/^type:/d' broken-v3/Chart.yaml
helm lint broken-v3 2>&1
helm template web broken-v3 2>&1 | head -3
```

```text
[INFO] Chart.yaml: icon is recommended
[ERROR] Chart.yaml: chart type is not valid in apiVersion 'v3'. It is valid in apiVersion 'v2'

Error: 1 chart(s) linted, 1 chart(s) failed
[ERROR] Chart.yaml: chart type is not valid in apiVersion 'v3'. It is valid in apiVersion 'v2'

Error: 1 chart(s) linted, 1 chart(s) failed
==> Linting broken-v3
[ERROR] Chart.yaml: apiVersion 'v3' is not valid. The value must be either "v1" or "v2"
[INFO] Chart.yaml: icon is recommended

Error: 1 chart(s) linted, 1 chart(s) failed
Error: invalid chart apiVersion
```

chart API v3 ของ Helm 4 **ยังเป็นงานทดลอง** แม้ตั้ง `HELM_EXPERIMENTAL_CHART_V3=1` ก็ยังใช้ไม่ได้ ข้อความแรกบ่นเรื่องบรรทัด `type:` ลบออกแล้วจึงเห็นข้อความหลัก `apiVersion 'v3' is not valid` — chart ที่เขียนวันนี้ใช้ `apiVersion: v2`

### ขั้นที่ 6: ช่องโหว่ของ --dry-run=server

ใช้ `mychart` ที่ดี แต่พิมพ์ค่าผิด `service.type=NodePortt`

```bash
helm install web2 ../lab05-first/mychart -n first --dry-run=server --set service.type=NodePortt 2>&1 | head -8
helm install web2 ../lab05-first/mychart -n first --dry-run=server --set service.type=NodePortt 2>&1 | grep -n "type:"
helm template web2 ../lab05-first/mychart --set service.type=NodePortt | kubectl apply --dry-run=server -n first -f - 2>&1 | tail -3
```

```text
NAME: web2
LAST DEPLOYED: Tue Oct  6 05:52:33 2026
NAMESPACE: first
STATUS: pending-install
REVISION: 1
DESCRIPTION: Dry run complete
HOOKS:
---
58:  type: NodePortt
deployment.apps/web2-mychart created (server dry run)
pod/web2-mychart-test-connection created (server dry run)
The Service "web2-mychart" is invalid: spec.type: Unsupported value: "NodePortt": supported values: "ClusterIP", "ExternalName", "LoadBalancer", "NodePort"
```

<p align="center" id="fig-14">
  <img src="images/14-lab06-dryrun-gap.png" alt="รูปที่ 14 LAB 6 ช่องโหว่ของ dry-run=server" width="900"><br>
  <em><b>รูปที่ 14</b> helm install --dry-run=server ผ่าน (Dry run complete) แต่ kubectl apply --dry-run=server จับ spec.type ผิดได้ — ตรวจสองชั้น</em>
</p>

`helm install --dry-run=server` ของ Helm 4.3.0 ตอบ `Dry run complete` ทั้งที่ manifest มี `type: NodePortt` (Helm ใช้ "server" เพื่อให้ `lookup` เห็นคลัสเตอร์ แต่ไม่ได้ส่ง object ให้ API server ตรวจ) ส่วน `kubectl apply --dry-run=server` ส่งให้ API server validate จริงจึงจับได้ ถ้าติดตั้งจริงล่ะ

```bash
helm install web2 ../lab05-first/mychart -n first --set service.type=NodePortt 2>&1 | tail -2
helm list -n first
helm uninstall web2 -n first
helm list -n first
```

```text
Error: INSTALLATION FAILED: server-side apply failed for object first/web2-mychart /v1, Kind=Service: Service "web2-mychart" is invalid: spec.type: Unsupported value: "NodePortt": supported values: "ClusterIP", "ExternalName", "LoadBalancer", "NodePort"
NAME	NAMESPACE	REVISION	UPDATED                                	STATUS  	CHART        	APP VERSION
web 	first    	1       	2026-10-06 05:52:11.552625655 +0700 +07	deployed	mychart-0.1.0	1.16.0
web2	first    	1       	2026-10-06 05:52:34.197006681 +0700 +07	failed  	mychart-0.1.0	1.16.0
release "web2" uninstalled
NAME	NAMESPACE	REVISION	UPDATED                                	STATUS  	CHART        	APP VERSION
web 	first    	1       	2026-10-06 05:52:11.552625655 +0700 +07	deployed	mychart-0.1.0	1.16.0
```

install จริงล้มที่ API server **และทิ้ง release `web2` สถานะ `failed` ไว้** (object ที่สร้างไปแล้วบางตัวอาจค้างด้วย) ต้อง `helm uninstall web2` เอง ไม่งั้น install ชื่อเดิมซ้ำไม่ได้

> **ตรวจสองชั้นก่อนติดตั้งของสำคัญ:** `helm lint` + `helm template` (รูปแบบ chart) แล้ว `helm template ... | kubectl apply --dry-run=server -f -` (ความถูกต้องของ object)

### สิ่งที่เห็น

| แบบ | ข้อความหลัก | ชี้ไปที่ |
|---|---|---|
| ย่อหน้าผิด | `yaml: line 24: mapping values are not allowed in this context` | บรรทัดของผล render (ใช้ `--debug`) |
| ฟังก์ชันผิด | `function "toYml" not defined` | `deployment.yaml:18` ของ template |
| ลืมค่า | `execution error at (...deployment.yaml:41:21): ต้องใส่ image.repository` | บรรทัด:คอลัมน์ของ template |
| chart v3 | `apiVersion 'v3' is not valid` / `invalid chart apiVersion` | `Chart.yaml` |
| field ผิด | `Dry run complete` (helm) vs `spec.type: Unsupported value` (kubectl) | ต้องตรวจด้วย API server |

**คำถามชวนคิด**

1. ทำไม error ของ `toYml` บอกบรรทัดของไฟล์ template ได้ตรง ๆ แต่ error ของ indent บอกบรรทัดของผล render
2. ถ้าจะใส่ขั้นตรวจ chart ลงใน CI จะเรียงคำสั่งอะไรบ้าง

**เก็บกวาด LAB 5–6:**

```bash
helm uninstall web -n first; kubectl delete ns first
```

```text
release "web" uninstalled
namespace "first" deleted
```

โฟลเดอร์ `labs/lab05-first/mychart` และ `labs/lab06-debug/broken-*` เก็บไว้ดูได้ (ไม่เข้า git) หรือลบด้วย `rm -rf labs/lab05-first/mychart labs/lab06-debug/broken-*` (สั่งในโฟลเดอร์ `02_LAB`)

---

## LAB 7: แม่พิมพ์ร้านน้องส้ม (template functions)

<p align="center" id="fig-15">
  <img src="images/15-lab07-open.png" alt="รูปที่ 15 LAB 7 อ่านแม่พิมพ์" width="900"><br>
  <em><b>รูปที่ 15</b> LAB 7: อ่านแม่พิมพ์ som-shop — range การ์ดกระดาน, if hpa ไม่ใส่ replicas, include ตรายาง, toYaml resources</em>
</p>

**เป้าหมาย:** อ่านชุดแฟรนไชส์ `charts/som-shop` และพิสูจน์ด้วย `helm template` ว่าแต่ละฟังก์ชันให้ผลอะไร (ไม่ติดตั้งอะไร ไม่ต่อคลัสเตอร์)

**ไฟล์:** `charts/som-shop/` (ใส่ `--set db.password=x` ทุกครั้งเพราะ `helm template` ไม่ต่อคลัสเตอร์ — LAB 8 อธิบาย)

### ขั้นที่ 1: โครงชุดและตรายาง

```bash
cd /workspace/014_kubernetes_helm/02_LAB
find charts -type f | sort
cat charts/som-shop/Chart.yaml
grep -n "define" charts/som-shop/templates/_helpers.tpl
```

```text
charts/som-shop/.helmignore
charts/som-shop/Chart.yaml
charts/som-shop/templates/NOTES.txt
charts/som-shop/templates/_helpers.tpl
charts/som-shop/templates/configmap.yaml
charts/som-shop/templates/db.yaml
charts/som-shop/templates/hpa.yaml
charts/som-shop/templates/ingress.yaml
charts/som-shop/templates/secret.yaml
charts/som-shop/templates/seed-job.yaml
charts/som-shop/templates/tests/test-health.yaml
charts/som-shop/templates/web.yaml
charts/som-shop/values.schema.json
charts/som-shop/values.yaml
charts/values-dev.yaml
charts/values-prod.yaml
# ชุดแฟรนไชส์ร้านอาหารแมวน้องส้ม (บท 014) — chart API v2 (Helm 3 และ Helm 4 ใช้ได้)
apiVersion: v2
name: som-shop
description: ร้านอาหารแมวน้องส้ม — หน้าร้าน Next.js + ครัว PostgreSQL + Ingress + HPA
type: application
version: 0.1.0          # เวอร์ชันของ chart (ชุดแฟรนไชส์) — แก้ทุกครั้งที่แก้ templates
appVersion: "1.7"       # เวอร์ชันแอปเริ่มต้น = tag ของ som-shop-web ถ้าไม่ได้ตั้ง web.image.tag
kubeVersion: ">=1.30.0-0"
keywords: [som-shop, kubernetes-lab]
4:{{- define "som-shop.fullname" -}}
9:{{- define "som-shop.labels" -}}
18:{{- define "som-shop.webImage" -}}
23:{{- define "som-shop.dbPassword" -}}
```

เทียบแม่พิมพ์กับไฟล์ YAML ของบท 013

| แม่พิมพ์ | object ที่ได้ (release `som`) | แทนไฟล์บท 013 |
|---|---|---|
| `configmap.yaml` | ConfigMap `som-web-config`, `som-announcement` | `15-config.yaml` |
| `secret.yaml` | Secret `som-db-secret` | สร้างเองด้วย `kubectl create secret` (บท 011) |
| `db.yaml` | Service `som-db` + StatefulSet `som-db` | `10-db.yaml` |
| `web.yaml` | Deployment + Service `som-web` | `20-web.yaml` |
| `hpa.yaml` | HPA `som-web` | `60-hpa.yaml` |
| `ingress.yaml` | Ingress `som-web` (+ Secret `som-tls`, Middleware `som-redirect-https` เมื่อ tls) | `50-ingress.yaml` + `kubectl create secret tls` |
| `seed-job.yaml` | Job `som-seed` (hook) | initContainer `db-seed` ใน `20-web.yaml` |
| `tests/test-health.yaml` | Pod `som-test-health` (test) | — (ใหม่) |

ชุดนี้ **ไม่มี** หลังร้าน `som-admin` และลูกค้าจำลอง `customers` (LAB 12 จัดการของสองอย่างนี้)

### ขั้นที่ 2: range — การ์ดบนกระดานประกาศ

```bash
helm template som charts/som-shop --set db.password=x --show-only templates/configmap.yaml
```

```text
---
# Source: som-shop/templates/configmap.yaml
# กระดานประกาศ 2 แผ่น: ป้ายร้าน (envFrom) + ประกาศหน้าร้าน (mount เป็นไฟล์)
apiVersion: v1
kind: ConfigMap
metadata:
  name: som-web-config
  labels:
    app.kubernetes.io/name: som-shop
    app.kubernetes.io/instance: som
    app.kubernetes.io/version: "1.7"
    app.kubernetes.io/managed-by: Helm
    helm.sh/chart: som-shop-0.1.0
data:
  APP_THEME: "harbor"
  SHOP_EYEBROW: "⚓ ท่าเรือ Kubernetes · Helm"
  SHOP_FOOTER: "Next.js + PostgreSQL · Kubernetes LAB 014 · ติดตั้งทั้งร้านด้วย Helm"
  SHOP_NAME: "ร้านอาหารแมวน้องส้ม"
  SHOP_PROMO: ""


---
# Source: som-shop/templates/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: som-announcement
  labels:
    app.kubernetes.io/name: som-shop
    app.kubernetes.io/instance: som
    app.kubernetes.io/version: "1.7"
    app.kubernetes.io/managed-by: Helm
    helm.sh/chart: som-shop-0.1.0
data:
  announcement.txt: "วันนี้ปลาทูสดมาก 🐟\n"
```

- `range $key, $value := .Values.shop` สร้างการ์ด 5 ใบ **เรียงตามตัวอักษรของ key** (APP_THEME มาก่อน SHOP_*) ไม่ใช่ตามลำดับใน `values.yaml`
- ทุกค่าครอบ `quote` (`SHOP_PROMO: ""` ยังเป็นข้อความว่าง ไม่ใช่ `null`)
- label 5 บรรทัดมาจากตรายาง `som-shop.labels` ตัวเดียว
- ป้ายหัวร้านเปลี่ยนเป็น `⚓ ท่าเรือ Kubernetes · Helm` (บท 013 เป็น `· HPA`)

### ขั้นที่ 3: if — replicas หายเมื่อเปิด HPA

```bash
helm template som charts/som-shop --set db.password=x --show-only templates/web.yaml | grep -nE "^kind:|replicas:|image:|checksum"
helm template som charts/som-shop --set db.password=x --set hpa.enabled=true --show-only templates/web.yaml | grep -nE "^kind:|replicas:|image:"
```

```text
4:kind: Service
25:kind: Deployment
35:  replicas: 2
49:        # แก้กระดานประกาศ/ซอง → ค่า checksum เปลี่ยน → ได้ Pod ใหม่เอง (ไม่ต้อง rollout restart)
50:        checksum/config: 26b21079c94c41e739e54c86e0e6bc3b645c05616ab6adc55adccc304e8ec8fd
51:        checksum/secret: 2548f708d02bc8233b43c88f4e535af3aafba6687be9427412f7330e9871ec36
59:          image: postgres:17.11-alpine
75:          image: som-shop-web:1.7
4:kind: Service
25:kind: Deployment
58:          image: postgres:17.11-alpine
74:          image: som-shop-web:1.7
```

`hpa.enabled=false` (ค่าเริ่มต้น) มี `replicas: 2` แต่ `hpa.enabled=true` บรรทัด `replicas:` **หายไป** — แม่พิมพ์แก้กับดัก "replicas ใน YAML ทับ HPA" ของบท 013 LAB 10 ไว้ในตัว (image `postgres:17.11-alpine` คือ initContainer `wait-for-db`)

### ขั้นที่ 4: toYaml | nindent และ checksum

```bash
helm template som charts/som-shop --set db.password=x --show-only templates/web.yaml | grep -A6 "^          resources:"
helm template som charts/som-shop --set db.password=x --show-only templates/web.yaml | grep "checksum/config"
helm template som charts/som-shop --set db.password=x --set shop.SHOP_PROMO="ลด 50%" --show-only templates/web.yaml | grep "checksum/config"
```

```text
          resources:
            requests: {cpu: 10m, memory: 16Mi}
            limits: {cpu: 100m, memory: 64Mi}
      volumes:
        - name: announcement
          configMap:
            name: som-announcement
--
          resources:
            limits:
              cpu: 500m
              memory: 512Mi
            requests:
              cpu: 100m
              memory: 192Mi
        checksum/config: 26b21079c94c41e739e54c86e0e6bc3b645c05616ab6adc55adccc304e8ec8fd
        checksum/config: 25db4af18147f3bcf17521bf2bf231118fabf17c112d4dc934b5b08c0ab74532
```

- ก้อนแรกเป็น resources ของ initContainer ที่เขียนตรงในแม่พิมพ์ ก้อนที่สองคือหน้าร้านที่มาจาก `toYaml .Values.web.resources | nindent 12` (ย่อหน้า 12 ช่องพอดีใต้ `resources:`)
- แก้แค่ `SHOP_PROMO` ลายนิ้วมือ `checksum/config` เปลี่ยนจาก `26b21079…` เป็น `25db4af1…` → upgrade จริงจะได้ Pod ใหม่เอง (LAB 9 พิสูจน์)

### ขั้นที่ 5: fullnameOverride และ label ตาม tag

```bash
helm template som charts/som-shop --set db.password=x --set fullnameOverride=shop2 | grep -E "^  name:" | sort | uniq
helm template som charts/som-shop --set db.password=x | grep -E "^  name:" | sort | uniq
helm template som charts/som-shop --set db.password=x --set web.image.tag=1.8 --show-only templates/secret.yaml
```

```text
  name: shop2-announcement
  name: shop2-db
  name: shop2-db-secret
  name: shop2-seed
  name: shop2-test-health
  name: shop2-web
  name: shop2-web-config
  name: som-announcement
  name: som-db
  name: som-db-secret
  name: som-seed
  name: som-test-health
  name: som-web
  name: som-web-config
---
# Source: som-shop/templates/secret.yaml
# ซองปิดผนึก: รหัสฐานข้อมูล + DATABASE_URL (Helm เก็บค่านี้ใน release Secret ด้วย — ถอดได้!)
apiVersion: v1
kind: Secret
metadata:
  name: som-db-secret
  labels:
    app.kubernetes.io/name: som-shop
    app.kubernetes.io/instance: som
    app.kubernetes.io/version: "1.8"
    app.kubernetes.io/managed-by: Helm
    helm.sh/chart: som-shop-0.1.0
type: Opaque
stringData:
  POSTGRES_PASSWORD: "x"
  DATABASE_URL: "postgres://som:x@som-db-0.som-db:5432/catshop"
```

- release `som` → ชื่อ `som-*` **ตรงกับร้านบท 009–013 ทุกตัว** (LAB 12 จึงรับร้านเดิมได้) `fullnameOverride=shop2` เปลี่ยนคำนำหน้าทุกชิ้นพร้อมกัน
- `DATABASE_URL` ประกอบด้วย `printf` จากค่า user/รหัส/ชื่อ จึงไม่ต้องพิมพ์รหัสซ้ำ 2 ที่แบบบท 011
- label `app.kubernetes.io/version` ตาม tag ที่ส่ง (`"1.8"`) แต่ `helm.sh/chart` ยังเป็น `som-shop-0.1.0`

### สิ่งที่เห็น

- `range` วน key ตามตัวอักษร, `if` ทำให้ `replicas` หายเมื่อมี HPA, `include` ตรายางเดียวใช้ทุกไฟล์, `toYaml | nindent 12` ย่อหน้าตรง
- checksum เปลี่ยนเมื่อป้ายเปลี่ยน และชื่อ object ตามชื่อ release/`fullnameOverride`

**คำถามชวนคิด**

1. ถ้าเพิ่ม key ใหม่ `SHOP_HOURS: "9-18"` ใน `values-prod.yaml` ใต้ `shop:` ต้องแก้แม่พิมพ์ไหม แอปจะเห็นค่านี้อย่างไร
2. ทำไม label `app.kubernetes.io/version` ไม่ควรใส่ไว้ใน `spec.selector` ของ Deployment (คิดถึง selector ที่แก้ไม่ได้ ในบทที่ 7)

**เก็บกวาด:** ไม่มี (ไม่ได้ติดตั้งอะไร)

---

## LAB 8: ใบสั่งต่อสาขาและด่านตรวจ

<p align="center" id="fig-16">
  <img src="images/16-lab08-open.png" alt="รูปที่ 16 LAB 8 ใบสั่งต่อสาขา" width="900"><br>
  <em><b>รูปที่ 16</b> LAB 8: values-dev.yaml / values-prod.yaml + values.schema.json + required/lookup</em>
</p>

**เป้าหมาย:** เทียบผล render ของสาขา dev กับ prod ให้ด่านตรวจปฏิเสธใบสั่งผิด และเห็นความต่างของ `helm lint`/`template` (ไม่ต่อคลัสเตอร์) กับการติดตั้งจริง

**ไฟล์:** `charts/values-dev.yaml`, `charts/values-prod.yaml`, `charts/som-shop/values.schema.json`

### ขั้นที่ 1: ใบสั่ง 2 สาขา

```bash
cd /workspace/014_kubernetes_helm/02_LAB
cat charts/values-dev.yaml charts/values-prod.yaml
helm template som charts/som-shop -f charts/values-dev.yaml --set db.password=x | grep -E "^kind:" | sort | uniq -c
helm template som charts/som-shop -f charts/values-dev.yaml --set db.password=x | grep -E "^kind:" | wc -l
helm template som charts/som-shop -f charts/values-prod.yaml --set db.password=x | grep -E "^kind:" | sort | uniq -c
helm template som charts/som-shop -f charts/values-prod.yaml --set db.password=x | grep -E "^kind:" | wc -l
```

```text
# สาขาทดลอง (dev): บูธเดียว ไม่มี HPA ประตู http ธรรมดา ธีมส้ม
shop:
  SHOP_NAME: "ร้านอาหารแมวน้องส้ม (dev)"
  APP_THEME: "sunset"
  SHOP_PROMO: "🧪 สาขาทดลอง — ของจริงอยู่ที่ shop.localhost"
web:
  replicas: 1
hpa:
  enabled: false
ingress:
  enabled: true
  host: dev.shop.localhost
  tls: false
# สาขาจริง (prod): HPA 2–6 บูธ ประตู HTTPS shop.localhost
shop:
  SHOP_NAME: "ร้านอาหารแมวน้องส้ม"
  APP_THEME: "harbor"
  SHOP_PROMO: "🎉 เปิดสาขาใหม่ด้วย Helm คำสั่งเดียว"
hpa:
  enabled: true
  minReplicas: 2
  maxReplicas: 6
ingress:
  enabled: true
  host: shop.localhost
  tls: true
      2 kind: ConfigMap
      1 kind: Deployment
      1 kind: Ingress
      1 kind: Job
      1 kind: Pod
      1 kind: Secret
      2 kind: Service
      1 kind: StatefulSet
10
      2 kind: ConfigMap
      1 kind: Deployment
      1 kind: HorizontalPodAutoscaler
      1 kind: Ingress
      1 kind: Job
      1 kind: Middleware
      1 kind: Pod
      2 kind: Secret
      2 kind: Service
      1 kind: StatefulSet
13
```

| | dev (10) | prod (13) |
|---|---|---|
| หน้าร้าน | 1 บูธ (`replicas: 1`) | HPA 2–6 (ไม่มี `replicas`) |
| ประตู | `http://dev.shop.localhost:30080` | `https://shop.localhost:30081` + Secret `som-tls` + Middleware redirect |
| ป้าย | `(dev)` ธีม `sunset` แถบ 🧪 | ธีม `harbor` แถบ 🎉 |
| ส่วนที่เหมือนกัน | db, ConfigMap, Secret, Job seed (hook), Pod test — มาจากแม่พิมพ์ชุดเดียวกัน | |

ใบสั่งแต่ละใบมีแค่ "ส่วนที่ต่าง" ไม่กี่บรรทัด ค่าอื่นมาจาก `values.yaml` ของชุด (จำนวน 10/13 นับ Job hook และ Pod test ด้วย)

### ขั้นที่ 2: ด่านตรวจปฏิเสธใบสั่ง

```bash
helm template som charts/som-shop --set db.password=x --set web.image.tag=1.4 2>&1 | head -4
helm template som charts/som-shop --set db.password=x --set web.replicas=9 2>&1 | head -4
helm template som charts/som-shop --set db.password=x --set ingress.host=Shop_Localhost 2>&1 | head -3
```

```text
Error: values don't meet the specifications of the schema(s) in the following chart(s):
som-shop:
- at '/web/image/tag': 'not' failed

Error: values don't meet the specifications of the schema(s) in the following chart(s):
som-shop:
- at '/web/replicas': maximum: got 9, want 6

Error: values don't meet the specifications of the schema(s) in the following chart(s):
som-shop:
- at '/ingress/host': 'Shop_Localhost' does not match pattern '^[a-z0-9.-]+$'
```

<p align="center" id="fig-17">
  <img src="images/17-lab08-schema-reject.png" alt="รูปที่ 17 LAB 8 ด่านตรวจปฏิเสธ" width="900"><br>
  <em><b>รูปที่ 17</b> ด่านตรวจปฏิเสธใบสั่ง: --set web.replicas=9 → maximum: got 9, want 6</em>
</p>

`values.schema.json` ตรวจ **ก่อน render** ข้อความบอกตำแหน่งของค่า (`/web/replicas`) และกติกาที่ผิด (`maximum`, `not`, `pattern`) — tag `1.4` คือรุ่นพังของบทที่ 7, 9 บูธเกินเพดาน 6 ของร้าน, host ตัวใหญ่/ขีดล่างใช้เป็นชื่อโดเมนไม่ได้

chart ภายนอกก็มีด่านตรวจ ลองใส่ key ผิดให้ Traefik chart (ใช้แคตตาล็อกจาก LAB 1)

```bash
helm template traefik traefik/traefik --version 41.6.1 -n traefik -f labs/lab10-addons/traefik-values.yaml --set logs.access.enabled=true 2>&1 | head -3
helm template traefik traefik/traefik --version 41.6.1 -n traefik -f labs/lab10-addons/traefik-values.yaml --set accesslog.enabled=true 2>&1 | head -3
```

```text
Error: values don't meet the specifications of the schema(s) in the following chart(s):
traefik:
- at '': additional properties 'logs' not allowed
Error: values don't meet the specifications of the schema(s) in the following chart(s):
traefik:
- at '': additional properties 'accesslog' not allowed
```

key ที่ถูกของ chart 41.6.1 คือ `accessLog.enabled` (ตัว L ใหญ่ — ดูใน `labs/lab10-addons/traefik-values.yaml`) ถ้าไม่มี schema ค่าที่สะกดผิดจะถูกเพิกเฉยเงียบ ๆ

### ขั้นที่ 3: required — lint เตือน template หยุด

```bash
helm lint charts/som-shop
helm lint charts/som-shop -f charts/values-prod.yaml --set db.password=x
helm template som charts/som-shop 2>&1 | head -1
```

```text
level=WARN msg="missing required values" message="ติดตั้งครั้งแรกต้องตั้งรหัสฐานข้อมูล: --set db.password=<รหัส>"
level=WARN msg="missing required values" message="ติดตั้งครั้งแรกต้องตั้งรหัสฐานข้อมูล: --set db.password=<รหัส>"
==> Linting charts/som-shop
[INFO] Chart.yaml: icon is recommended

1 chart(s) linted, 0 chart(s) failed
==> Linting charts/som-shop
[INFO] Chart.yaml: icon is recommended

1 chart(s) linted, 0 chart(s) failed
Error: execution error at (som-shop/templates/web.yaml:29:28): ติดตั้งครั้งแรกต้องตั้งรหัสฐานข้อมูล: --set db.password=<รหัส>
```

ไม่ใส่รหัส: `helm lint` แค่ **WARN** (lint ไม่รู้ว่าในคลัสเตอร์มี Secret เดิมหรือไม่) แต่ `helm template` **หยุด** ที่ `required` (บรรทัด 29 ของ `web.yaml` คือ checksum/secret ที่ render `secret.yaml` → เรียกตรายาง `dbPassword`)

### ขั้นที่ 4: lookup มองไม่เห็นคลัสเตอร์ตอน template

```bash
for i in 1 2; do helm template som charts/som-shop -f charts/values-prod.yaml --set db.password=x --show-only templates/ingress.yaml | grep "tls.crt" | awk '{print $2}' | base64 -d | openssl x509 -noout -fingerprint -sha256 | cut -c1-45; done
helm template som charts/som-shop -f charts/values-prod.yaml --set db.password=x --show-only templates/ingress.yaml | grep "tls.crt" | awk '{print $2}' | base64 -d | openssl x509 -noout -subject -ext subjectAltName
```

```text
sha256 Fingerprint=95:82:4B:CC:A2:6E:6E:D1:E8
sha256 Fingerprint=46:94:7E:2E:C2:BA:33:71:83
subject=CN = shop.localhost
X509v3 Subject Alternative Name:
    DNS:shop.localhost
```

render 2 ครั้งได้ใบรับรอง **คนละใบ** เพราะ `helm template` ไม่ต่อคลัสเตอร์ `lookup` จึงไม่เจอ `som-tls` เดิม และ `genSelfSignedCert` สุ่มใบใหม่ทุกครั้ง ตอน install/upgrade จริง `lookup` เห็นใบเดิมจึงใช้ใบเดิมต่อ (LAB 12 พิสูจน์ด้วย fingerprint ก่อน/หลัง) — ทฤษฎีหัวข้อ 5.7

### สิ่งที่เห็น

- chart เดียว + ใบสั่ง 2 ใบ = dev 10 object / prod 13 object
- schema ปฏิเสธ tag 1.4, replicas 9, host ผิดรูป ตั้งแต่ก่อน render (ทั้งชุดเราและชุด Traefik)
- `required`: lint = WARN, template = error; `lookup` ว่างตอน template

**คำถามชวนคิด**

1. ถ้าอยากห้ามไม่ให้ใบสั่ง prod ปิด HPA (`hpa.enabled: false`) จะใช้ schema ได้ไหม หรือควรตรวจที่อื่น
2. ทำไม chart นี้จึงไม่ใช้ `randAlphaNum` สร้างรหัสฐานข้อมูลให้อัตโนมัติ

**เก็บกวาด:** ไม่มี (ไม่ได้ติดตั้งอะไร)

---

## LAB 9: เติมสินค้าหลังเปิดร้านและผู้ตรวจรับ (hook + test)

<p align="center" id="fig-18">
  <img src="images/18-lab09-open.png" alt="รูปที่ 18 LAB 9 hook และ test" width="900"><br>
  <em><b>รูปที่ 18</b> LAB 9: install สาขา dev → hook post-install (seed) เติมสินค้า → helm test --logs → ถอด release Secret</em>
</p>

**เป้าหมาย:** ติดตั้งร้านน้องส้มทั้งร้านเป็นสาขา dev ด้วยคำสั่งเดียว ดู hook seed ทำงาน สั่งผู้ตรวจรับร้าน และถอดดูว่า release Secret เก็บอะไรไว้

**ไฟล์:** `charts/som-shop`, `charts/values-dev.yaml` (namespace `som-dev` ใหม่ ไม่แตะร้านจริง `som-shop`)

### ขั้นที่ 1: hook ในแม่พิมพ์

```bash
cd /workspace/014_kubernetes_helm/02_LAB
grep -A3 "annotations:" charts/som-shop/templates/seed-job.yaml
```

```text
  annotations:
    "helm.sh/hook": post-install,post-upgrade
    "helm.sh/hook-weight": "0"
    "helm.sh/hook-delete-policy": before-hook-creation,hook-succeeded
```

Job `som-seed` (คำสั่ง `node scripts/seed.mjs` ใน image หน้าร้าน) รัน **หลัง install และหลังทุก upgrade** สำเร็จแล้วถูกลบ (`hook-succeeded`) แทน initContainer `db-seed` ของบท 009–013 ที่รันในทุกบูธ

### ขั้นที่ 2: เปิดสาขา dev ทั้งร้านด้วยคำสั่งเดียว

```bash
time helm install som charts/som-shop -n som-dev --create-namespace -f charts/values-dev.yaml --set db.password=meow1234 --wait
```

```text
NAME: som
LAST DEPLOYED: Tue Oct  6 05:53:27 2026
NAMESPACE: som-dev
STATUS: deployed
REVISION: 1
DESCRIPTION: Install complete
NOTES:
🐱 เปิดร้าน ร้านอาหารแมวน้องส้ม (dev) (release som, revision 1) ใน namespace som-dev แล้ว
   image หน้าร้าน: som-shop-web:1.7
   จำนวนบูธ: 1 (ไม่มี HPA)
   เปิดร้าน: curl http://dev.shop.localhost:30080/api/whoami
   ตรวจรับร้าน: helm test som -n som-dev --logs

real	0m17.892s
```

**17.9 วินาที** ได้ร้านครบ: db + ซอง + ป้าย + หน้าร้าน + ประตู + เติมสินค้า การ์ดต้อนรับ (NOTES) เป็นภาษาไทยจาก `templates/NOTES.txt` ที่ render ชื่อร้าน revision image และคำสั่งเปิดร้านให้ (`meow1234` เป็นรหัสตัวอย่างของ LAB)

```bash
kubectl get ns som-dev --show-labels
kubectl -n som-dev get all,pvc,cm,secret,ing
kubectl -n som-dev get job
```

```text
NAME      STATUS   AGE   LABELS
som-dev   Active   18s   kubernetes.io/metadata.name=som-dev,name=som-dev
NAME                           READY   STATUS    RESTARTS   AGE
pod/som-db-0                   1/1     Running   0          18s
pod/som-web-64c9f5cd95-t5pj7   1/1     Running   0          18s

NAME              TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)    AGE
service/som-db    ClusterIP   None            <none>        5432/TCP   18s
service/som-web   ClusterIP   10.96.216.214   <none>        80/TCP     18s

NAME                      READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/som-web   1/1     1            1           18s

NAME                                 DESIRED   CURRENT   READY   AGE
replicaset.apps/som-web-64c9f5cd95   1         1         1       18s

NAME                      READY   AGE
statefulset.apps/som-db   1/1     18s

NAME                                  STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
persistentvolumeclaim/data-som-db-0   Bound    pvc-8347bc95-a507-4042-9bcb-af75570ea79c   1Gi        RWO            standard       <unset>                 18s

NAME                         DATA   AGE
configmap/kube-root-ca.crt   1      18s
configmap/som-announcement   1      18s
configmap/som-web-config     5      18s

NAME                               TYPE                 DATA   AGE
secret/sh.helm.release.v1.som.v1   helm.sh/release.v1   1      18s
secret/som-db-secret               Opaque               2      18s

NAME                                CLASS     HOSTS                ADDRESS     PORTS   AGE
ingress.networking.k8s.io/som-web   traefik   dev.shop.localhost   localhost   80      18s
No resources found in som-dev namespace.
```

- Job `som-seed` **ไม่อยู่แล้ว** (`No resources found`) เพราะสำเร็จแล้วถูกลบตาม `hook-succeeded`
- namespace จาก `--create-namespace` ไม่มี label Pod Security (ดูขั้นที่ 4)
- สมุดหน้าแรกคือ `sh.helm.release.v1.som.v1`

```bash
curl -s http://dev.shop.localhost:30080/api/whoami; echo
curl -s http://dev.shop.localhost:30080/api/stats; echo
curl -s http://dev.shop.localhost:30080/ | grep -o "ร้านอาหารแมวน้องส้ม (dev)" | head -1
curl -s http://dev.shop.localhost:30080/ | grep -o "🧪 สาขาทดลอง[^<]*" | head -1
```

```text
som-web-64c9f5cd95-t5pj7 1.7
som-web-64c9f5cd95-t5pj7 1.7 orders=0 products=6
ร้านอาหารแมวน้องส้ม (dev)
🧪 สาขาทดลอง — ของจริงอยู่ที่ shop.localhost
```

สาขาใหม่ ออเดอร์ 0 สินค้า 6 รายการ (มาจาก hook seed) ชื่อร้านและแถบโปรโมชันมาจากใบสั่ง dev — 🌐 เปิด `http://dev.shop.localhost:30080` ใน browser ได้

### ขั้นที่ 3: ผู้ตรวจรับร้าน

```bash
helm test som -n som-dev --logs | sed -n '/TEST SUITE/,$p'
kubectl -n som-dev get pod
```

```text
TEST SUITE:     som-test-health
Last Started:   Tue Oct  6 05:53:45 2026
Last Completed: Tue Oct  6 05:53:53 2026
Phase:          Succeeded

POD LOGS: som-test-health (curl)
health:   {"ok":true,"db":"up"}
whoami:   som-web-64c9f5cd95-t5pj7 1.7
products: ok

NAME                       READY   STATUS    RESTARTS   AGE
som-db-0                   1/1     Running   0          26s
som-web-64c9f5cd95-t5pj7   1/1     Running   0          26s
```

Pod `som-test-health` (curl) เรียก `/api/health` (ร้านต่อ db ได้), `/api/whoami` และ `/api/products` ผ่าน Service ภายใน ผ่านทั้ง 3 = `Phase: Succeeded` และ Pod ทดสอบถูกลบทันที (delete policy `hook-succeeded`) แต่ `--logs` ยังแสดงผลตรวจให้

### ขั้นที่ 4: Pod Security ของ namespace ใหม่

```bash
kubectl label --dry-run=server --overwrite ns som-dev pod-security.kubernetes.io/enforce=restricted
```

```text
namespace/som-dev labeled (server dry run)
```

ลอง (แบบ dry run) ว่าถ้าบังคับระดับ `restricted` Pod ที่มีอยู่จะผิดกติกาไหม ผลไม่มี warning = Pod ของชุดร้าน (และ Job/test) ผ่าน `restricted` (แม่พิมพ์ตั้ง `runAsNonRoot`, `seccompProfile`, `drop: ["ALL"]` ไว้ทุก container) ถ้าต้องการให้ namespace ใหม่เตือนเหมือน `som-shop` ให้ label เอง เช่น `kubectl label ns som-dev pod-security.kubernetes.io/warn=restricted` (ไม่บังคับใน LAB นี้)

### ขั้นที่ 5: ซองในสมุด — ถอด release Secret

```bash
kubectl -n som-dev get secret -l owner=helm
kubectl -n som-dev get secret sh.helm.release.v1.som.v1 -o jsonpath='{.data.release}' | base64 -d | base64 -d | gzip -d \
  | python3 -c 'import json,sys,re; r=json.load(sys.stdin); print(json.dumps(r["config"],ensure_ascii=False)); print(re.findall(r"DATABASE_URL: .*", r["manifest"])); print([h["name"]+":"+",".join(h["events"]) for h in r["hooks"]])'
helm get values som -n som-dev
```

```text
NAME                        TYPE                 DATA   AGE
sh.helm.release.v1.som.v1   helm.sh/release.v1   1      26s
{"db": {"password": "meow1234"}, "hpa": {"enabled": false}, "ingress": {"enabled": true, "host": "dev.shop.localhost", "tls": false}, …}
['DATABASE_URL: "postgres://som:meow1234@som-db-0.som-db:5432/catshop"']
['som-test-health:test', 'som-seed:post-install,post-upgrade']
USER-SUPPLIED VALUES:
db:
  password: meow1234
hpa:
  enabled: false
...
```

(ผลตัดให้สั้น)

<p align="center" id="fig-19">
  <img src="images/19-lab09-release-secret.png" alt="รูปที่ 19 LAB 9 ถอด release Secret" width="900"><br>
  <em><b>รูปที่ 19</b> ถอดสมุดใน Secret ด้วย base64 -d | base64 -d | gzip -d เห็นรหัสฐานข้อมูลในใบสั่ง → ใครอ่าน Secret ได้ = อ่านรหัสได้</em>
</p>

รหัสฐานข้อมูลอยู่ใน release Secret **สองที่**: ใบสั่ง (`config.db.password`) และพิมพ์เขียว (`DATABASE_URL` ใน manifest ของ Secret ร้าน) และ `helm get values` ก็แสดงตรง ๆ — ใครมีสิทธิ์ `get secrets` ใน `som-dev` หรือรัน `helm` กับ namespace นี้ได้ = อ่านรหัสได้ (ทฤษฎีหัวข้อ 10) ข้อมูล hook ก็อยู่ในซองด้วย (`som-seed:post-install,post-upgrade`, `som-test-health:test`)

### ขั้นที่ 6: upgrade โดยไม่ส่งรหัส + เปลี่ยนประกาศ

```bash
kubectl -n som-dev get pod -l app=som-web -o name
time helm upgrade som charts/som-shop -n som-dev -f charts/values-dev.yaml --set announcement="ปลาแซลมอนมาแล้ว 🍣" --wait | grep -E "REVISION|STATUS"
kubectl -n som-dev get pod -l app=som-web -o name
kubectl -n som-dev get secret som-db-secret -o jsonpath='{.data.POSTGRES_PASSWORD}' | base64 -d; echo
curl -s http://dev.shop.localhost:30080/api/announcement; echo
helm history som -n som-dev
```

```text
pod/som-web-64c9f5cd95-t5pj7
STATUS: deployed
REVISION: 2

real	0m9.685s
pod/som-web-574cd55f96-g94jv
pod/som-web-64c9f5cd95-t5pj7
meow1234
som-web-574cd55f96-g94jv 1.7 ปลาแซลมอนมาแล้ว 🍣
REVISION	UPDATED                 	STATUS    	CHART         	APP VERSION	DESCRIPTION
1       	Tue Oct  6 05:53:27 2026	superseded	som-shop-0.1.0	1.7        	Install complete
2       	Tue Oct  6 05:53:53 2026	deployed  	som-shop-0.1.0	1.7        	Upgrade complete
```

- ไม่ได้ส่ง `--set db.password` แต่ Secret ยังเป็นรหัสเดิม (`meow1234` ค่าตัวอย่าง) เพราะตรายาง `dbPassword` ใช้ **`lookup`** อ่านจาก Secret เดิม
- เปลี่ยนแค่ประกาศ → `checksum/config` เปลี่ยน → ได้ Pod ใหม่ `som-web-574cd55f96-…` เอง (ไม่ต้อง `rollout restart` แบบบทที่ 10) Pod เก่ากำลังปิด (ยังเห็นคู่กันชั่วครู่)

### ขั้นที่ 7: ดู hook เกิดแล้วหายระหว่าง upgrade (2 หน้าต่าง)

**หน้าต่างที่ 2** ดู Pod แบบ watch (`kubectl get -w` ดูได้ทีละชนิด ถ้าสั่ง `get job,pod -w` จะได้ `error: you may only specify a single resource type`)

```bash
timeout 25 kubectl -n som-dev get pod -w
```

**หน้าต่างที่ 1** (ภายใน 25 วินาที)

```bash
cd /workspace/014_kubernetes_helm/02_LAB
helm upgrade som charts/som-shop -n som-dev -f charts/values-dev.yaml --set announcement="วันนี้ปลาทูสดมาก 🐟" --wait | grep -E "REVISION|STATUS"
kubectl -n som-dev get job
kubectl -n som-dev get events --field-selector involvedObject.kind=Job | tail -3
```

หน้าต่างที่ 2 (ตัดบรรทัดซ้ำ)

```text
NAME                       READY   STATUS    RESTARTS   AGE
som-db-0                   1/1     Running   0          43s
som-web-574cd55f96-g94jv   1/1     Running   0          16s
som-web-65b7dd9845-j9rm7   0/1     Pending   0          0s
som-web-65b7dd9845-j9rm7   0/1     Init:0/1   0          0s
som-web-65b7dd9845-j9rm7   0/1     PodInitializing   0          2s
som-web-65b7dd9845-j9rm7   0/1     Running           0          2s
som-web-65b7dd9845-j9rm7   1/1     Running           0          3s
som-web-574cd55f96-g94jv   1/1     Terminating       0          22s
som-seed-qk2k5             0/1     Pending           0          0s
som-seed-qk2k5             0/1     Init:0/1          0          0s
som-seed-qk2k5             0/1     PodInitializing   0          1s
som-seed-qk2k5             1/1     Running           0          1s
som-seed-qk2k5             0/1     Completed         0          2s
som-web-574cd55f96-g94jv   0/1     Error             0          27s
```

หน้าต่างที่ 1

```text
STATUS: deployed
REVISION: 3
No resources found in som-dev namespace.
32s         Normal   Completed          job/som-seed   Job completed
19s         Normal   SuccessfulCreate   job/som-seed   Created pod: som-seed-qk2k5
15s         Normal   Completed          job/som-seed   Job completed
```

ลำดับที่เห็นตรงกับทฤษฎีหัวข้อ 11: **Pod หน้าร้านใหม่พร้อม (1/1) ก่อน** (เพราะ `--wait`) → Pod เก่าเริ่มปิด → **จึงเกิด Job seed** (`post-upgrade`) → `Completed` → Job ถูกลบ (`No resources found`) Events บอกว่า seed รัน 2 ครั้งในนาทีที่ผ่านมา (upgrade rev 2 และ rev 3)

> Pod เก่าของหน้าร้านแสดง `Error` ชั่วครู่ตอนถูกปิด เป็นแค่ exit code ของ process หลังได้สัญญาณหยุด (SIGTERM) ระหว่าง rolling update ไม่ใช่ปัญหา (Pod ใหม่รับลูกค้าแล้ว)

### สิ่งที่เห็น

- `helm install ... --wait` ครั้งเดียวได้ร้านทั้งร้าน 17.9 วินาที + NOTES ภาษาไทย + hook seed (`orders=0 products=6`)
- `helm test` ผ่าน 3 บรรทัด, release Secret มีรหัสทั้งใน config และ manifest
- upgrade ไม่ส่งรหัส = `lookup` รหัสเดิม, เปลี่ยนประกาศ = Pod ใหม่เอง, hook รันหลังหน้าร้านพร้อม

**คำถามชวนคิด**

1. ถ้าสินค้าตั้งต้นต้องมีก่อนหน้าร้านรับลูกค้าคนแรก hook แบบ `post-install` เพียงพอไหม ควรใช้ hook ชนิดไหนแทน และมีข้อจำกัดอะไร (คิดถึง db ที่ต้องพร้อมก่อน)
2. ทำไม seed ต้อง "ทำซ้ำได้" (idempotent) เมื่อเปลี่ยนจาก initContainer มาเป็น hook `post-upgrade`

**เก็บกวาด LAB 9:** LAB 12 จะเปิดสาขา dev ใหม่ทั้งร้าน ให้ลบสาขานี้

```bash
helm uninstall som -n som-dev
kubectl -n som-dev get pvc
kubectl delete ns som-dev
helm list -A
```

```text
release "som" uninstalled
NAME            STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
data-som-db-0   Bound    pvc-8347bc95-a507-4042-9bcb-af75570ea79c   1Gi        RWO            standard       <unset>                 81s
namespace "som-dev" deleted
helm list -A
NAME	NAMESPACE	REVISION	UPDATED	STATUS	CHART	APP VERSION
```

หลัง `helm uninstall` ตู้เซฟ `data-som-db-0` **ยังอยู่** (PVC จาก `volumeClaimTemplates` ไม่ใช่ส่วนของ release — LAB 12 ใช้เรื่องนี้) การลบ namespace ลบ PVC ไปด้วย ตอนนี้ `helm list -A` ว่างอีกครั้ง

---

