## LAB 10: Traefik และ metrics-server จากแคตตาล็อก

<p align="center" id="fig-20">
  <img src="images/20-lab10-open.png" alt="รูปที่ 20 LAB 10 add-on จาก chart" width="900"><br>
  <em><b>รูปที่ 20</b> LAB 10: แทน static manifest ด้วย chart traefik 41.6.1 (v3.7.13) และ metrics-server 3.14.0 (0.9.0)</em>
</p>

**เป้าหมาย:** เปลี่ยนพนักงานต้อนรับ (Traefik) และเจ้าหน้าที่จดมิเตอร์ (metrics-server) ที่ติดตั้งด้วย static manifest ในบท 012–013 ให้มาจาก chart ทางการ เทียบผล render กับของเดิม เห็นว่าทำไม "รับของเดิม" ไม่ได้ แล้วย้ายจริงระหว่างที่ลูกค้าเข้าร้าน

**ไฟล์:** `labs/lab10-addons/traefik-values.yaml`, `labs/lab10-addons/metrics-server-values.yaml`, `labs/lab10-addons/static-old/` (สำเนาไฟล์ static ของบท 012/013)

ใบสั่งของ Traefik ตั้งให้ได้ผลเหมือนประตูเดิม (ไฟล์จริง ตัดคอมเมนต์บางส่วน)

```yaml
service:
  spec:
    type: NodePort            # kind map ออกมาแค่ 30080-30082 (ไม่มี LoadBalancer)
ports:
  web:
    nodePort: 30080
  websecure:
    nodePort: 30081
  traefik:
    expose:
      default: true           # เปิด dashboard ออก Service (เฉพาะ LAB)
    nodePort: 30082
providers:
  kubernetesIngress:
    strictPrefixMatching: true
    allowEmptyServices: true
    publishedService:
      enabled: false
    ingressEndpoint:
      hostname: localhost     # คอลัมน์ ADDRESS = localhost เหมือนบท 012
ingressClass:
  enabled: true
  isDefaultClass: true
api:
  dashboard: true
  insecure: true              # dashboard ไม่มีรหัส — เฉพาะ LAB
accessLog:
  enabled: true
global:
  checkNewVersion: false
  sendAnonymousUsage: false
```

ส่วน `metrics-server-values.yaml` มีแค่ `args: [--kubelet-insecure-tls]` (เฉพาะ LAB เหมือนบท 013)

### ขั้นที่ 1: render chart เทียบกับ static

```bash
cd /workspace/014_kubernetes_helm/02_LAB
ls labs/lab10-addons labs/lab10-addons/static-old
helm list -A
helm template traefik traefik/traefik --version 41.6.1 -n traefik -f labs/lab10-addons/traefik-values.yaml > /root/traefik-rendered.yaml
grep "^kind:" /root/traefik-rendered.yaml | sort | uniq -c
grep -nE -- "--(entryPoints.websecure.http.tls|providers.kubernetesingress.strictPrefixMatching|providers.kubernetesingress.ingressendpoint.hostname|api.insecure|accesslog)" /root/traefik-rendered.yaml
grep -nE "nodePort:|image:" /root/traefik-rendered.yaml
grep -A3 "matchLabels" /root/traefik-rendered.yaml | head -4
grep -A2 "matchLabels" labs/lab10-addons/static-old/00-traefik.yaml | head -3
```

```text
labs/lab10-addons:
metrics-server-values.yaml
static-old
traefik-values.yaml

labs/lab10-addons/static-old:
00-metrics-server.yaml
00-traefik.yaml
traefik-crds-v3.7.13.yml
NAME	NAMESPACE	REVISION	UPDATED	STATUS	CHART	APP VERSION
      1 kind: ClusterRole
      1 kind: ClusterRoleBinding
      1 kind: Deployment
      1 kind: IngressClass
      1 kind: Service
      1 kind: ServiceAccount
200:        - --api.insecure=true
208:        - --providers.kubernetesingress.ingressendpoint.hostname=localhost
209:        - --providers.kubernetesingress.strictPrefixMatching=true
210:        - --entryPoints.websecure.http.tls=true
212:        - --accesslog=true
213:        - --accesslog.fields.defaultmode=keep
214:        - --accesslog.fields.headers.defaultmode=drop
142:    nodePort: 30082
147:    nodePort: 30080
152:    nodePort: 30081
226:        image: docker.io/traefik:v3.7.13
    matchLabels:
      app.kubernetes.io/name: traefik
      app.kubernetes.io/instance: traefik-traefik
  strategy:
    matchLabels: {app: traefik}
  template:
    metadata:
      labels:
        app: traefik
```

ผล render ได้ flag สำคัญของบท 012 ครบ (HTTPS ที่ websecure, `strictPrefixMatching`, ADDRESS `localhost`, dashboard, access log), NodePort 30080/30081/30082 และ image `traefik:v3.7.13` เดิม **แต่ selector ต่างกัน**: chart ใช้ `app.kubernetes.io/name: traefik` + `app.kubernetes.io/instance: traefik-traefik` ส่วน static ใช้ `app: traefik` ซึ่งเป็นตัวกำหนดว่ารับของเดิมได้หรือไม่ (ขั้นที่ 2) สังเกตด้วยว่า chart ไม่สร้าง Namespace (มาจาก `--create-namespace`) และไม่มี CRD ใน render (CRD อยู่ใน `crds/` ติดตั้งแยก)

### ขั้นที่ 2: ลองผิด — ติดตั้งทับของเดิม

```bash
helm install traefik traefik/traefik --version 41.6.1 -n traefik -f labs/lab10-addons/traefik-values.yaml 2>&1 | cut -c1-420
helm list -A
```

```text
Error: INSTALLATION FAILED: unable to continue with install: ServiceAccount "traefik" in namespace "traefik" exists and cannot be imported into the current release: invalid ownership metadata; label validation error: missing key "app.kubernetes.io/managed-by": must be set to "Helm"; annotation validation error: missing key "meta.helm.sh/release-name": must be set to "traefik"; annotation validation error: missing key
NAME	NAMESPACE	REVISION	UPDATED	STATUS	CHART	APP VERSION
```

<p align="center" id="fig-21">
  <img src="images/21-lab10-adopt-fail.png" alt="รูปที่ 21 LAB 10 ติดตั้งทับของเดิม" width="900"><br>
  <em><b>รูปที่ 21</b> ติดตั้งทับของเดิม: invalid ownership metadata → --take-ownership เจอ conflict → --force-conflicts ติด selector field is immutable ⇒ ลบของเดิมก่อน (เก็บ CRD) </em>
</p>

Helm ไม่ยอมแตะ ServiceAccount ที่ไม่มีป้าย `managed-by: Helm` และ annotation `meta.helm.sh/release-name` (**invalid ownership metadata**) ข้อดีคือหยุดก่อนสร้างอะไร **ไม่มี release ค้าง** (`helm list -A` ว่าง) ประตูเดิมยังทำงานปกติ

**ผลจริงจากการทดลองแยก (ไม่ต้องทำตาม)** — ทดลองบนสำเนาของ Traefik static ใน namespace ทดลอง `traefik-test` (ไม่มี NodePort/IngressClass) เพื่อดูว่าถ้าฝืน "รับของเดิม" จะเกิดอะไร

1. `helm install ... --take-ownership` → SSA **conflict** กับ `kubectl-client-side-apply` และเกิด release `failed` rev 1

   ```text
   Error: INSTALLATION FAILED: conflict occurred while applying object traefik-test/traefik /v1, Kind=Service: Apply failed with 1 conflict: conflict with "kubectl-client-side-apply" using v1: .spec.selector && conflict occurred while applying object traefik-test/traefik apps/v1, Kind=Deployment: Apply failed with 11 conflicts: conflicts with "kubectl-client-side-apply" using apps/v1:
   - .spec.selector
   - .spec.strategy.rollingUpdate.maxSurge
   ...
   - .spec.template.spec.containers[name="traefik"].readinessProbe.httpGet.port
   ```

2. `helm upgrade --install ... --take-ownership --force-conflicts` → ยึด conflict ได้ แต่ติด **selector แก้ไม่ได้** rev 2 `failed`

   ```text
   Error: UPGRADE FAILED: server-side apply failed for object traefik-test/traefik apps/v1, Kind=Deployment: Deployment.apps "traefik" is invalid: spec.selector: Invalid value: {"matchLabels":{"app.kubernetes.io/instance":"traefik-traefik-test","app.kubernetes.io/name":"traefik"}}: field is immutable
   ```

3. ระหว่างนั้น ServiceAccount และ Service **ถูกติดป้าย Helm ไปแล้ว** (Deployment ยังไม่ถูกยึด) แล้วถ้า `helm uninstall` release ที่ล้มนี้

   ```text
   level=WARN msg="skipping delete of resource not owned by this release" kind=Deployment name=traefik namespace=traefik-test release=traefik
   1 resource(s) were not deleted because they are not owned by this release:
   [Deployment] traefik

   release "traefik" uninstalled
   ```

   ServiceAccount และ Service **ถูกลบทิ้ง** เหลือแต่ Deployment ถ้าเป็น Traefik ตัวจริงใน namespace `traefik` ประตูของทุกร้านปิดทันที

> ⚠️ **ห้าม `helm uninstall` release ที่ adopt ล้ม** และอย่าทำข้อ 1–3 กับ Traefik ตัวจริง (ทฤษฎีหัวข้อ 9.3) ทางที่ถูกสำหรับ add-on ที่ selector ต่างกันคือ **ลบของเดิม (เก็บ CRD) แล้วติดตั้ง chart** ซึ่งประตูจะปิดชั่วครู่ (ขั้นที่ 3)

### ขั้นที่ 3: ย้าย Traefik จริงระหว่างลูกค้าเข้าร้าน (2 หน้าต่าง)

ก่อนเริ่ม ตรวจว่ามี CRD ของ Traefik (Middleware ของร้านอยู่บน CRD เหล่านี้ **ห้ามลบไฟล์ `traefik-crds-v3.7.13.yml`**)

```bash
kubectl get crd | grep -c traefik.io
```

```text
25
```

**หน้าต่างที่ 2** ยิงลูกค้าจำลองผ่านประตู HTTPS 600 ครั้ง (ราว 78 วินาที)

```bash
cd /workspace/014_kubernetes_helm/02_LAB
./hit.sh -q https://shop.localhost:30081/api/whoami 600 0.1
```

**หน้าต่างที่ 1** (เริ่มภายในไม่กี่วินาทีหลังหน้าต่างที่ 2)

```bash
t0=$(date +%s)
kubectl delete -f labs/lab10-addons/static-old/00-traefik.yaml --wait=true
helm install traefik traefik/traefik --version 41.6.1 -n traefik --create-namespace -f labs/lab10-addons/traefik-values.yaml --wait --timeout 5m
echo "ย้าย Traefik: $(( $(date +%s)-t0 )) วินาที"
```

หน้าต่างที่ 1

```text
namespace "traefik" deleted
serviceaccount "traefik" deleted from traefik namespace
clusterrole.rbac.authorization.k8s.io "traefik" deleted
clusterrolebinding.rbac.authorization.k8s.io "traefik" deleted
deployment.apps "traefik" deleted from traefik namespace
service "traefik" deleted from traefik namespace
ingressclass.networking.k8s.io "traefik" deleted
NAME: traefik
LAST DEPLOYED: Tue Oct  6 05:58:43 2026
NAMESPACE: traefik
STATUS: deployed
REVISION: 1
DESCRIPTION: Install complete
TEST SUITE: None
NOTES:
traefik with docker.io/traefik:v3.7.13 has been deployed successfully on traefik namespace!
ย้าย Traefik: 19 วินาที
```

หน้าต่างที่ 2

```text
............................xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx......................................
จำนวน  Pod  เวอร์ชัน
    528 1.7 (เวอร์ชัน)
ข้อความ error:
     61 curl: (35) OpenSSL SSL_connect: SSL_ERROR_SYSCALL in connection to shop.localhost:30081
     11 curl: (35) Recv failure: Connection reset by peer
ช่วงที่มี err: 18.8 วินาที
ok=528 err=72 (ใช้เวลา 77.9 วินาที)
```

<p align="center" id="fig-22">
  <img src="images/22-lab10-migrate-downtime.png" alt="รูปที่ 22 LAB 10 ย้ายจริง ประตูปิดชั่วคราว" width="900"><br>
  <em><b>รูปที่ 22</b> ย้ายจริง: ระหว่างลบของเดิมและติดตั้ง chart ประตูปิดชั่วคราว (~19 วินาที) แล้วกลับมาเป็น 404 page not found ตามเดิม</em>
</p>

ย้ายทั้งหมด **19 วินาที** ลูกค้าเจอ error 72 จาก 600 ครั้งต่อเนื่อง **18.8 วินาที** (ประตูไม่มีคนเฝ้าระหว่างลบตัวเก่าถึงตัวใหม่พร้อม) ระบบจริงต้องประกาศช่วงปิดปรับปรุง หรือทำแบบ blue/green (ติดตั้งตัวใหม่คู่ขนานบนพอร์ต/IP อื่นแล้วสลับ) — นี่คือเหตุผลที่ควรเลือกวิธีติดตั้ง add-on ให้ดีตั้งแต่แรก

ตรวจประตูใหม่

```bash
kubectl get crd | grep -c traefik.io
kubectl -n traefik get deploy,svc,pod
kubectl get ingressclass
kubectl get ns traefik --show-labels
curl -s localhost:30080; echo
curl -s -o /dev/null -w "dashboard %{http_code}\n" localhost:30082/dashboard/
curl -si http://shop.localhost:30080/ | grep -iE "^HTTP|^location"
curl -sk https://shop.localhost:30081/api/stats; echo
curl -sk -o /dev/null -w "admin no-auth %{http_code}\n" https://admin.localhost:30081/
curl -sk -u som:meow-admin-123 https://admin.localhost:30081/stats; echo
```

```text
25
NAME                      READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/traefik   1/1     1            1           69s

NAME              TYPE       CLUSTER-IP      EXTERNAL-IP   PORT(S)                                     AGE
service/traefik   NodePort   10.96.201.218   <none>        8080:30082/TCP,80:30080/TCP,443:30081/TCP   69s

NAME                          READY   STATUS    RESTARTS   AGE
pod/traefik-8b84c796d-s5ngq   1/1     Running   0          69s
NAME                CONTROLLER                      PARAMETERS   AGE
traefik (default)   traefik.io/ingress-controller   <none>       70s
NAME      STATUS   AGE   LABELS
traefik   Active   70s   kubernetes.io/metadata.name=traefik,name=traefik
404 page not found
dashboard 200
HTTP/1.1 301 Moved Permanently
Location: https://shop.localhost:30081/
som-web-774d99d8df-g67ln 1.7 orders=3 products=6
admin no-auth 401
som-web-774d99d8df-g67ln 1.7 orders=3 products=6
```

ทุกอย่างกลับมาเหมือนบท 012–013: CRD 25 ตัวยังอยู่, NodePort 3 พอร์ต, IngressClass `traefik (default)` (ดาวทอง), `404 page not found` ที่ประตูเปล่า, dashboard 200, redirect 301 ไป 30081, ร้านตอบ (ออเดอร์เดิม 3), หลังร้านยังถามบัตร (401) และเข้าได้ด้วยบัตรตัวอย่าง

### ขั้นที่ 4: ย้าย metrics-server

```bash
helm install metrics-server metrics-server/metrics-server --version 3.14.0 -n kube-system -f labs/lab10-addons/metrics-server-values.yaml 2>&1 | cut -c1-300
t0=$(date +%s)
kubectl delete -f labs/lab10-addons/static-old/00-metrics-server.yaml --wait=true | tail -3
helm install metrics-server metrics-server/metrics-server --version 3.14.0 -n kube-system -f labs/lab10-addons/metrics-server-values.yaml --wait --timeout 5m | grep -E "STATUS|REVISION"
echo "ย้าย metrics-server: $(( $(date +%s)-t0 )) วินาที"
kubectl get apiservice v1beta1.metrics.k8s.io
```

```text
Error: INSTALLATION FAILED: unable to continue with install: ServiceAccount "metrics-server" in namespace "kube-system" exists and cannot be imported into the current release: invalid ownership metadata; label validation error: missing key "app.kubernetes.io/managed-by": must be set to "Helm"; annot
service "metrics-server" deleted from kube-system namespace
deployment.apps "metrics-server" deleted from kube-system namespace
apiservice.apiregistration.k8s.io "v1beta1.metrics.k8s.io" deleted
STATUS: deployed
REVISION: 1
ย้าย metrics-server: 21 วินาที
NAME                     SERVICE                      AVAILABLE                      AGE
v1beta1.metrics.k8s.io   kube-system/metrics-server   False (FailedDiscoveryCheck)   21s
```

ติดตั้งทับได้ error เดียวกับ Traefik (ไม่มี release ค้าง) ย้ายจริงใช้ **21 วินาที** แต่ **APIService ยังเป็น `False (FailedDiscoveryCheck)` ทันทีหลัง `--wait`** — Pod พร้อมแล้ว แต่ kube-apiserver ยังต้องตรวจเส้นทางไปหา metrics-server และ metrics-server ต้องจดมิเตอร์รอบแรกก่อน รอสัก 20–45 วินาที

```bash
sleep 20; kubectl top nodes
kubectl -n som-shop get hpa
kubectl get apiservice v1beta1.metrics.k8s.io
helm list -A
```

```text
NAME                CPU(cores)   CPU(%)   MEMORY(bytes)   MEMORY(%)
lab-control-plane   140m         0%       1234Mi          1%
lab-worker          47m          0%       522Mi           0%
lab-worker2         42m          0%       643Mi           1%
NAME      REFERENCE            TARGETS       MINPODS   MAXPODS   REPLICAS   AGE
som-web   Deployment/som-web   cpu: 3%/50%   2         6         2          17m
NAME                     SERVICE                      AVAILABLE   AGE
v1beta1.metrics.k8s.io   kube-system/metrics-server   True        47s
NAME          	NAMESPACE  	REVISION	UPDATED                                	STATUS  	CHART                	APP VERSION
metrics-server	kube-system	1       	2026-10-06 05:59:54.289839067 +0700 +07	deployed	metrics-server-3.14.0	0.9.0
traefik       	traefik    	1       	2026-10-06 05:58:43.60397903 +0700 +07 	deployed	traefik-41.6.1       	v3.7.13
```

`kubectl top` ใช้ได้ HPA ของร้านอ่าน CPU ได้ต่อ (`cpu: 3%/50%`) APIService `True` ใน ~47 วินาที และ `helm list -A` เห็นอุปกรณ์ท่าเรือ 2 ชิ้นเป็น release — ต่อไปอัปเกรด Traefik/metrics-server ด้วย `helm upgrade ... --version <ใหม่>` และย้อนด้วย `helm rollback` ได้เหมือนแอปทั่วไป (ส่วน CRD ต้องดูแลตามทฤษฎีหัวข้อ 4.3)

### สิ่งที่เห็น

- ผล render ของ chart ทางการ ≈ static ของบท 012/013 แต่ selector ต่าง จึงรับของเดิมไม่ได้
- ติดตั้งทับ = `invalid ownership metadata` (ปลอดภัย) / ฝืนด้วย take-ownership + force-conflicts = `field is immutable` และ uninstall แล้วลบของจริง
- ย้ายจริง: Traefik 19 วินาที (err 18.8 วินาที), metrics-server 21 วินาที (+ รอ APIService)

**คำถามชวนคิด**

1. ทำไมต้องเก็บ CRD ของ Traefik ไว้ตอนลบ static และถ้าเผลอลบไปจะเกิดอะไรกับ Middleware `redirect-https`, `admin-auth` ของร้าน
2. ถ้าเป็นระบบจริงที่ห้ามประตูปิดแม้ 19 วินาที จะวางแผนย้ายอย่างไร (คิดถึงการติดตั้งตัวใหม่คู่ขนานด้วยชื่อ release/พอร์ตอื่น)
3. ทำไม metrics-server ขึ้น `deployed` แล้วแต่ `kubectl top` ยังใช้ไม่ได้ทันที `--wait` รอถึงไหน

**เก็บกวาด:** ไม่มี — Traefik และ metrics-server ที่มาจาก chart **ใช้ต่อ** (LAB 12 และบทถัดไป) ลบไฟล์ชั่วคราว `rm -f /root/traefik-rendered.yaml` ได้

---

## LAB 11: โกดังเก็บชุดแฟรนไชส์ (OCI registry)

<p align="center" id="fig-23">
  <img src="images/23-lab11-open.png" alt="รูปที่ 23 LAB 11 โกดัง OCI" width="900"><br>
  <em><b>รูปที่ 23</b> LAB 11: registry:2 ใน k8s-lab → helm package → helm push → helm install oci://</em>
</p>

**เป้าหมาย:** ตั้งโกดัง OCI registry ขนาดเล็ก (มีรหัส) ใน k8s-lab แพ็กชุดร้านเป็น `.tgz` push เข้าโกดัง แล้วติดตั้งสาขาจาก `oci://` แทนโฟลเดอร์

**ไฟล์:** ทำงานใน `labs/lab11-registry/` (โฟลเดอร์ `auth/` และ `pulled/` สร้างระหว่าง LAB ไม่เข้า git) บัญชีโกดัง `som` / `meow-registry-123` **เป็นค่าตัวอย่าง**

### ขั้นที่ 1: ตั้งโกดัง

```bash
cd /workspace/014_kubernetes_helm/02_LAB/labs/lab11-registry
mkdir -p auth
docker run --rm --entrypoint htpasswd httpd:2.4-alpine -Bbn som meow-registry-123 > auth/htpasswd
cut -c1-8 auth/htpasswd
docker run -d --name som-registry -p 5000:5000 -v $PWD/auth:/auth -e REGISTRY_AUTH=htpasswd -e REGISTRY_AUTH_HTPASSWD_REALM=som -e REGISTRY_AUTH_HTPASSWD_PATH=/auth/htpasswd registry:2 | cut -c1-12
sleep 3; docker ps --filter name=som-registry --format '{{.Names}} {{.Image}} {{.Status}} {{.Ports}}'
curl -s -o /dev/null -w "%{http_code}\n" localhost:5000/v2/
```

```text
Unable to find image 'httpd:2.4-alpine' locally
...
Status: Downloaded newer image for httpd:2.4-alpine
som:$2y$
Unable to find image 'registry:2' locally
...
Status: Downloaded newer image for registry:2
42045de1f2c8
som-registry registry:2 Up 3 seconds 0.0.0.0:5000->5000/tcp, [::]:5000->5000/tcp
401
```

- `htpasswd` (ยืมจาก image `httpd`) สร้างไฟล์บัญชีที่รหัสถูก hash ด้วย bcrypt (`$2y$`)
- `registry:2` รันใน docker ของ k8s-lab ที่พอร์ต 5000 (ไม่ชน 30080–30082 และไม่ต้องเปิดออกเครื่องนักศึกษา) ไม่มีบัตรได้ `401`

### ขั้นที่ 2: แพ็กชุดแฟรนไชส์

```bash
helm package ../../charts/som-shop
ls -l som-shop-0.1.0.tgz; tar tzf som-shop-0.1.0.tgz | head -20
```

```text
Successfully packaged chart and saved it to: /workspace/014_kubernetes_helm/02_LAB/labs/lab11-registry/som-shop-0.1.0.tgz
-rw-r--r-- 1 root root 5987 Oct  6 06:01 som-shop-0.1.0.tgz
som-shop/Chart.yaml
som-shop/values.yaml
som-shop/values.schema.json
som-shop/templates/NOTES.txt
som-shop/templates/_helpers.tpl
som-shop/templates/configmap.yaml
som-shop/templates/db.yaml
som-shop/templates/hpa.yaml
som-shop/templates/ingress.yaml
som-shop/templates/secret.yaml
som-shop/templates/seed-job.yaml
som-shop/templates/tests/test-health.yaml
som-shop/templates/web.yaml
som-shop/.helmignore
```

ชื่อไฟล์ = `<name>-<version>.tgz` จาก `Chart.yaml` ทั้งร้านแพ็กได้ไม่ถึง 6 KB (ไม่มีรหัสอยู่ข้างใน — รหัสส่งตอนติดตั้ง)

### ขั้นที่ 3: login (ลองผิด 2 แบบ) แล้ว push

```bash
helm push som-shop-0.1.0.tgz oci://localhost:5000/charts --plain-http 2>&1 | tail -1
echo meow-registry-123 | helm registry login http://localhost:5000 -u som --password-stdin --plain-http 2>&1 | tail -1
echo meow-registry-123 | helm registry login localhost:5000 -u som --password-stdin --plain-http
python3 -c 'import json; d=json.load(open("/root/.config/helm/registry/config.json")); print({k:{kk:(vv[:6]+"...") for kk,vv in v.items()} for k,v in d["auths"].items()})'
helm push som-shop-0.1.0.tgz oci://localhost:5000/charts --plain-http
```

```text
Error: failed to perform "Exists" on destination: HEAD "http://localhost:5000/v2/charts/som-shop/manifests/sha256:ef59e9e33853a9e4af39916e648d7dca165471037781ab5c07e8934d6fcfda22": basic credential not found
Error: invalid reference: invalid registry "http://localhost:5000"
Login Succeeded
{'localhost:5000': {'auth': 'c29tOm...'}}
Pushed: localhost:5000/charts/som-shop:0.1.0
Digest: sha256:ef59e9e33853a9e4af39916e648d7dca165471037781ab5c07e8934d6fcfda22
```

<p align="center" id="fig-24">
  <img src="images/24-lab11-push-install.png" alt="รูปที่ 24 LAB 11 login push install" width="900"><br>
  <em><b>รูปที่ 24</b> ต้อง helm registry login localhost:5000 (ใส่แค่ชื่อโฮสต์) ก่อน push ได้ digest แล้วติดตั้งจาก oci:// เป็นสาขา oci-demo</em>
</p>

- push ก่อน login = `basic credential not found`
- Helm 4 ให้ login ด้วย **ชื่อโฮสต์เท่านั้น** (`localhost:5000`) ใส่ `http://` ได้ `invalid registry`
- `--password-stdin` กันรหัสไปค้างในประวัติคำสั่ง (`ps`/history) ส่วน `--plain-http` ใช้เพราะโกดัง LAB ไม่มี TLS
- credential เก็บใน `~/.config/helm/registry/config.json` เป็น base64 ของ `som:...` (`c29tOm` = `som:`) **ไม่ได้เข้ารหัส**
- push แล้วได้ **digest** (ลายนิ้วมือของเนื้อหา) ใช้อ้างอิงแบบเปลี่ยนไม่ได้

### ขั้นที่ 4: ดู ดึง และติดตั้งจากโกดัง

```bash
helm show chart oci://localhost:5000/charts/som-shop --version 0.1.0 --plain-http 2>&1 | grep -E "^(name|version|appVersion|Pulled|Digest)"
mkdir -p pulled && helm pull oci://localhost:5000/charts/som-shop --version 0.1.0 --plain-http -d pulled --untar 2>&1 | tail -2; ls pulled/som-shop
time helm install oci-som oci://localhost:5000/charts/som-shop --version 0.1.0 --plain-http -n oci-demo --create-namespace \
  --set fullnameOverride=som --set db.password=meow1234 --set ingress.enabled=true --set ingress.host=oci.shop.localhost --set web.replicas=1 \
  --wait 2>&1 | grep -vE "^\s*$" | head -12
curl -s http://oci.shop.localhost:30080/api/whoami; echo
helm list -n oci-demo
```

```text
Pulled: localhost:5000/charts/som-shop:0.1.0
Digest: sha256:ef59e9e33853a9e4af39916e648d7dca165471037781ab5c07e8934d6fcfda22
appVersion: "1.7"
name: som-shop
version: 0.1.0
Pulled: localhost:5000/charts/som-shop:0.1.0
Digest: sha256:ef59e9e33853a9e4af39916e648d7dca165471037781ab5c07e8934d6fcfda22
Chart.yaml
templates
values.schema.json
values.yaml
Pulled: localhost:5000/charts/som-shop:0.1.0
Digest: sha256:ef59e9e33853a9e4af39916e648d7dca165471037781ab5c07e8934d6fcfda22
NAME: oci-som
LAST DEPLOYED: Tue Oct  6 06:01:08 2026
NAMESPACE: oci-demo
STATUS: deployed
REVISION: 1
DESCRIPTION: Install complete
NOTES:
🐱 เปิดร้าน ร้านอาหารแมวน้องส้ม (release oci-som, revision 1) ใน namespace oci-demo แล้ว
   image หน้าร้าน: som-shop-web:1.7
   จำนวนบูธ: 1 (ไม่มี HPA)

real	0m17.003s
som-web-59495f6db6-qrvkm 1.7
NAME   	NAMESPACE	REVISION	UPDATED                                	STATUS  	CHART         	APP VERSION
oci-som	oci-demo 	1       	2026-10-06 06:01:08.356324343 +0700 +07	deployed	som-shop-0.1.0	1.7
```

- `helm pull -d pulled` ต้องมีโฟลเดอร์ `pulled` อยู่ก่อน (จึง `mkdir -p` ไว้)
- ติดตั้งจาก `oci://` **ไม่ต้อง `helm repo add`** ใช้เวลา 17.0 วินาที เปิดได้ที่ `http://oci.shop.localhost:30080`
- release ชื่อ `oci-som` แต่ `--set fullnameOverride=som` ทำให้ object ยังชื่อ `som-*` (ไม่งั้นจะเป็น `oci-som-web`, `oci-som-db`)

### ขั้นที่ 5: ล็อกด้วย digest และ logout

```bash
DIG=$(helm show chart oci://localhost:5000/charts/som-shop --version 0.1.0 --plain-http 2>&1 | grep -oE "sha256:[0-9a-f]+" | head -1); echo "digest=${DIG:0:19}..."
helm template x oci://localhost:5000/charts/som-shop@$DIG --plain-http --set db.password=x 2>&1 | grep -E "^kind:|Pulled|Digest" | head -4
helm registry logout localhost:5000
helm pull oci://localhost:5000/charts/som-shop --version 0.1.0 --plain-http -d /root 2>&1 | tail -1
```

```text
digest=sha256:ef59e9e33853...
Pulled: localhost:5000/charts/som-shop@sha256:ef59e9e33853a9e4af39916e648d7dca165471037781ab5c07e8934d6fcfda22
Digest: sha256:ef59e9e33853a9e4af39916e648d7dca165471037781ab5c07e8934d6fcfda22
kind: Secret
kind: ConfigMap
Removing login credentials for localhost:5000
Error: failed to perform "FetchReference" on source: GET "http://localhost:5000/v2/charts/som-shop/manifests/0.1.0": basic credential not found
```

อ้างอิงด้วย `@sha256:...` ได้ chart ชุดเดิมเป๊ะ แม้วันหลังจะมีคน push `0.1.0` ทับ (ทฤษฎีหัวข้อ 14) หลัง logout ดึงไม่ได้อีก (`basic credential not found`)

> **chart กับ image คนละคนดึง:** chart ข้างบนถูกดึงโดย helm ที่รันใน k8s-lab (มองเห็น `localhost:5000`) แต่ image `som-shop-web` ถูกดึงโดย containerd บน Node ของ kind ซึ่ง `localhost` คือตัว Node เอง จึงไม่เห็นโกดังนี้ LAB จึงไม่ push image เข้าโกดัง (ระบบจริงใช้ registry ที่ Node มองเห็น + `imagePullSecrets` ของบทที่ 11)

### สิ่งที่เห็น

- `helm package` ได้ `som-shop-0.1.0.tgz` 5987 ไบต์, push ได้ digest `sha256:ef59e9e3…`
- login ต้องใช้ชื่อโฮสต์, credential เป็น base64
- ติดตั้งจาก `oci://` ได้ทั้งด้วย `--version` และ `@sha256:` (17.0 วินาที)

**คำถามชวนคิด**

1. ถ้าแก้ template แล้ว `helm package` + `helm push` โดยไม่เปลี่ยน `version: 0.1.0` จะเกิดอะไรกับคนที่ติดตั้งด้วย `--version 0.1.0` และคนที่ติดตั้งด้วย digest
2. องค์กรควรเก็บอะไรบ้างในโกดังของตัวเอง (chart อย่างเดียวพอไหม)

**เก็บกวาด LAB 11:**

```bash
helm uninstall oci-som -n oci-demo; kubectl delete ns oci-demo
docker rm -f som-registry
rm -rf som-shop-0.1.0.tgz auth pulled
cd ../..
```

```text
release "oci-som" uninstalled
namespace "oci-demo" deleted
som-registry
```

---

