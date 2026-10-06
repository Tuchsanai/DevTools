## LAB 12: LAB สุดท้าย: ร้านน้องส้มพร้อมส่ง

<p align="center" id="fig-25">
  <img src="images/25-lab12-open.png" alt="รูปที่ 25 LAB 12 ภาพรวม" width="900"><br>
  <em><b>รูปที่ 25</b> LAB สุดท้าย: ร้านน้องส้มพร้อมส่ง — ติดตั้งทั้งร้านด้วยคำสั่งเดียว สาขา dev และรับร้านเดิมเป็นสาขา prod</em>
</p>

**เป้าหมาย:** ใช้ทุกอย่างของบทนี้กับร้านจริง

1. เปิด **สาขา dev** ทั้งร้านใน namespace ใหม่ด้วยคำสั่งเดียว และตรวจรับด้วย `helm test`
2. **รับร้านเดิมของบท 013** (`som-shop` ที่ติดตั้งด้วย `kubectl apply` และมีออเดอร์อยู่แล้ว) เข้ามาอยู่ใต้ Helm เป็นสาขา prod โดยออเดอร์และใบรับรองเดิมไม่หาย
3. อัปเกรดหน้าร้าน 1.7 → **1.8** และย้อนรุ่น **ขณะที่ลูกค้าจำลองยิงเข้าร้านตลอดเวลา** โดยไม่มีลูกค้าเจอ error
4. ปิดสาขา dev และเข้าใจผลของตู้เซฟ (PVC) ที่ค้างอยู่

**ไฟล์:** `charts/som-shop`, `charts/values-dev.yaml`, `charts/values-prod.yaml`, `hit.sh` (ทำในโฟลเดอร์ `02_LAB` ทั้งหมด ใช้ **2 หน้าต่าง SSH**)

**สิ่งที่ต้องมีก่อน:** LAB 0 (image 1.8), LAB 10 (Traefik และ metrics-server จาก chart) และสาขา dev ของ LAB 9 ถูกลบแล้ว

เลข revision ของสาขา prod ที่จะเกิดในเครื่องทดลอง (ของนักศึกษาอาจต่างถ้าสั่งซ้ำหรือล้มเพิ่ม — ดู `helm history` ก่อน rollback ทุกครั้ง)

| rev | มาจาก | สถานะ |
|:---:|---|---|
| 1 | 12.4 (ข) `--take-ownership` ชน conflict | `failed` (ภายหลังเป็น `superseded`) |
| 2 | 12.4 (ค) `--take-ownership --force-conflicts` รับร้าน 1.7 | `deployed` → `superseded` |
| 3 | 12.6 upgrade 1.8 ไม่ใส่ `--force-conflicts` | `failed` |
| 4 | 12.6 upgrade 1.8 + `--force-conflicts` | `superseded` |
| 5 | 12.7 `helm rollback som 2` | `Rollback to 2` (1.7) |
| 6 | 12.7 upgrade 1.8 อีกครั้ง (ไม่ต้อง force แล้ว) | `deployed` |

### 12.1 จุดเริ่ม

```bash
cd /workspace/014_kubernetes_helm/02_LAB
helm list -A
kubectl -n som-shop get deploy,sts,hpa,ing
curl -sk https://shop.localhost:30081/api/stats; echo
kubectl -n som-shop get deploy som-web -o jsonpath='{range .metadata.managedFields[*]}{.manager}{" "}{.operation}{"\n"}{end}'
fp() { kubectl -n som-shop get secret som-tls -o jsonpath='{.data.tls\.crt}' | base64 -d | openssl x509 -noout -fingerprint -sha256 | cut -c1-40; }
echo "cert ก่อน: $(fp)"
```

```text
NAME          	NAMESPACE  	REVISION	UPDATED                                	STATUS  	CHART                	APP VERSION
metrics-server	kube-system	1       	2026-10-06 05:59:54.289839067 +0700 +07	deployed	metrics-server-3.14.0	0.9.0
traefik       	traefik    	1       	2026-10-06 05:58:43.60397903 +0700 +07 	deployed	traefik-41.6.1       	v3.7.13
NAME                        READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/customers   0/0     0            0           18m
deployment.apps/som-admin   1/1     1            1           20m
deployment.apps/som-web     2/2     2            2           20m

NAME                      READY   AGE
statefulset.apps/som-db   1/1     20m

NAME                                          REFERENCE            TARGETS       MINPODS   MAXPODS   REPLICAS   AGE
horizontalpodautoscaler.autoscaling/som-web   Deployment/som-web   cpu: 2%/50%   2         6         2          19m

NAME                                  CLASS     HOSTS             ADDRESS     PORTS     AGE
ingress.networking.k8s.io/som-admin   traefik   admin.localhost   localhost   80, 443   20m
ingress.networking.k8s.io/som-shop    traefik   shop.localhost    localhost   80, 443   20m
som-web-774d99d8df-r72bt 1.7 orders=3 products=6
kube-controller-manager Update
kubectl-rollout Update
kubectl Update
kubectl-client-side-apply Update
kube-controller-manager Update
cert ก่อน: sha256 Fingerprint=DF:E2:AD:87:27:0E:8B:
```

- Helm รู้จักแค่ add-on 2 ตัว (LAB 10) ส่วนร้าน `som-shop` ยังเป็นของ `kubectl` ล้วน: เจ้าของ field ของ `som-web` มี `kubectl-client-side-apply` (apply ไฟล์), `kubectl` (`set image`), `kubectl-rollout` (`rollout restart`) และ `kube-controller-manager` (ทฤษฎีหัวข้อ 9.1)
- จดออเดอร์ (`orders=3` ในเครื่องทดลอง ของนักศึกษาอาจต่าง) และ fingerprint ของใบรับรอง `som-tls` ไว้เทียบหลังรับร้าน (ฟังก์ชัน `fp` ใช้ได้ตลอด session นี้)

### 12.2 อ่านชุดแฟรนไชส์

<p align="center" id="fig-26">
  <img src="images/26-lab12-chart-tree.png" alt="รูปที่ 26 LAB 12 โครงชุด som-shop" width="900"><br>
  <em><b>รูปที่ 26</b> โครงชุด charts/som-shop: แม่พิมพ์ web, db, config, secret, ingress, hpa, seed hook, test + ใบสั่ง dev/prod</em>
</p>

โครงชุดดูได้จาก LAB 7 ขั้นที่ 1 (`find charts -type f | sort`) ตรวจชุดด้วยใบสั่งทั้งสองก่อนใช้จริง

```bash
helm lint charts/som-shop -f charts/values-prod.yaml --set db.password=x
helm lint charts/som-shop -f charts/values-dev.yaml --set db.password=x | tail -1
```

```text
==> Linting charts/som-shop
[INFO] Chart.yaml: icon is recommended

1 chart(s) linted, 0 chart(s) failed
1 chart(s) linted, 0 chart(s) failed
```

### 12.3 สาขา dev ด้วยคำสั่งเดียว

```bash
time helm install som charts/som-shop -n som-dev --create-namespace -f charts/values-dev.yaml --set db.password=meow1234 --wait
helm test som -n som-dev --logs | sed -n '/Phase/,$p'
curl -s http://dev.shop.localhost:30080/api/whoami; echo
curl -s http://dev.shop.localhost:30080/ | grep -oE "ร้านอาหารแมวน้องส้ม \(dev\)|theme-[a-z]+|data-theme=\"[a-z]+\"" | sort -u
```

```text
NAME: som
LAST DEPLOYED: Tue Oct  6 06:02:08 2026
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

real	0m18.037s
Phase:          Succeeded

POD LOGS: som-test-health (curl)
health:   {"ok":true,"db":"up"}
whoami:   som-web-64c9f5cd95-lvbr9 1.7
products: ok

som-web-64c9f5cd95-lvbr9 1.7
theme-sunset
ร้านอาหารแมวน้องส้ม (dev)
```

<p align="center" id="fig-27">
  <img src="images/27-lab12-dev-branch.png" alt="รูปที่ 27 LAB 12 สาขา dev" width="900"><br>
  <em><b>รูปที่ 27</b> สาขา dev: helm install ... --wait ครั้งเดียวได้ทั้งร้าน (~18 วินาที) ป้ายร้านมีคำว่า (dev) ธีมส้ม</em>
</p>

ทั้งร้าน **18.0 วินาที** ตรวจรับผ่าน ธีม `sunset` และชื่อร้าน `(dev)` มาจากใบสั่ง 🌐 เปิด `http://dev.shop.localhost:30080`

<p align="center" id="fig-28">
  <img src="images/screenshots/20261006_0629_lab12helm_02-dev-branch.png" alt="รูปที่ 28 ภาพหน้าจอจริง สาขา dev" width="800"><br>
  <em><b>รูปที่ 28</b> ภาพหน้าจอจริงจากการทดลอง: สาขา dev ที่ http://dev.shop.localhost:30080 (release som ใน namespace som-dev) ธีมส้ม-ชมพู ชื่อร้าน &quot;ร้านอาหารแมวน้องส้ม (dev)&quot; ป้ายเวอร์ชัน 1.7 แถบ &quot;🧪 สาขาทดลอง&quot; ออเดอร์ 0 — เปิดจาก chart เดียวกับสาขาจริง ต่างแค่ใบสั่ง</em>
</p>

### 12.4 รับร้านเดิมเข้า Helm (สาขา prod)

<p align="center" id="fig-29">
  <img src="images/28-lab12-adopt-prod.png" alt="รูปที่ 29 LAB 12 รับร้านเดิมเป็น prod" width="900"><br>
  <em><b>รูปที่ 29</b> รับร้านเดิมของบท 013 (som-shop) เข้า Helm ด้วย --take-ownership --force-conflicts ออเดอร์เดิมยังอยู่ (rev 1 failed เพราะ conflict → rev 2 deployed)</em>
</p>

ร้านบท 013 มี object ชื่อ `som-web`, `som-db`, `som-db-secret`, `som-web-config`, `som-announcement`, `som-tls` ซึ่ง **ชื่อและ selector ตรงกับที่ chart สร้างจาก release `som`** (LAB 7) จึงรับได้ทีละชั้น (ทฤษฎีหัวข้อ 9.3) — ไม่ต้อง `--set db.password` เพราะ `lookup` อ่านรหัสจาก Secret เดิม

**(ก) install ทับ**

```bash
helm install som charts/som-shop -n som-shop -f charts/values-prod.yaml 2>&1 | cut -c1-300
helm list -n som-shop
```

```text
Error: INSTALLATION FAILED: unable to continue with install: Secret "som-tls" in namespace "som-shop" exists and cannot be imported into the current release: invalid ownership metadata; label validation error: missing key "app.kubernetes.io/managed-by": must be set to "Helm"; annotation validation e
NAME	NAMESPACE	REVISION	UPDATED	STATUS	CHART	APP VERSION
```

หยุดตั้งแต่ object แรกที่ไม่มีป้าย Helm ไม่มี release เกิดขึ้น

**(ข) --take-ownership**

```bash
helm upgrade --install som charts/som-shop -n som-shop -f charts/values-prod.yaml --take-ownership 2>&1 | cut -c1-2000
helm history som -n som-shop | cut -c1-120
```

```text
Release "som" does not exist. Installing it now.
Error: conflict occurred while applying object som-shop/som-web-config /v1, Kind=ConfigMap: Apply failed with 3 conflicts: conflicts with "kubectl-client-side-apply" using v1:
- .data.SHOP_EYEBROW
- .data.SHOP_FOOTER
- .data.SHOP_PROMO && conflict occurred while applying object som-shop/som-web apps/v1, Kind=Deployment: Apply failed with 2 conflicts: conflicts with "kubectl-client-side-apply" using apps/v1:
- .spec.template.spec.containers[name="web"].env[name="POD_NAMESPACE"].valueFrom.fieldRef
- .spec.template.spec.initContainers[name="wait-for-db"].command && conflict occurred while applying object som-shop/som-db apps/v1, Kind=StatefulSet: Apply failed with 1 conflict: conflict with "kubectl-client-side-apply" using apps/v1: .spec.volumeClaimTemplates
REVISION	UPDATED                 	STATUS	CHART         	APP VERSION	DESCRIPTION
1       	Tue Oct  6 06:02:28 2026	failed	som-shop-0.1.0	1.7        	Release "som" failed: conflict occurred while applyi
        	                        	      	              	           	- .data.SHOP_EYEBROW
        	                        	      	              	           	- .data.SHOP_FOOTER
        	                        	      	              	           	- .data.SHOP_PROMO && conflict o...
```

`--take-ownership` ข้ามการตรวจป้ายได้ แต่ server-side apply พบ field ที่ `kubectl-client-side-apply` ถือไว้ด้วยค่าที่ **ต่างจาก chart**: ป้ายร้าน 3 ใบ (ข้อความของบท 013 vs บท 014), `POD_NAMESPACE` และคำสั่ง `wait-for-db` (เขียนต่างรูปแบบ) และ `volumeClaimTemplates` ของ db ได้ rev 1 `failed` (ร้านยังทำงานตามเดิม) รายการ conflict ในเครื่องนักศึกษาอาจต่างเล็กน้อยตามประวัติร้านของตัวเอง

> ⚠️ **ห้าม `helm uninstall som -n som-shop` ตอนนี้** — release ที่ล้มได้ติดป้าย Helm ให้บาง object ไปแล้ว uninstall จะลบของจริงของร้าน (ดู LAB 10 ขั้นที่ 2) ให้ทำ (ค) ต่อเลย

**(ค) --take-ownership --force-conflicts**

```bash
time helm upgrade --install som charts/som-shop -n som-shop -f charts/values-prod.yaml --take-ownership --force-conflicts --wait --timeout 5m 2>&1 | cut -c1-300
helm history som -n som-shop | cut -c1-120
kubectl -n som-shop get deploy,sts,hpa,ing,pvc
curl -sk https://shop.localhost:30081/api/stats; echo
echo "cert หลัง: $(fp)"
kubectl -n som-shop get secret som-db-secret -o jsonpath='{.data.POSTGRES_PASSWORD}' | base64 -d | sed 's/./*/g'; echo " (รหัสเดิมจาก lookup ซ่อนเป็น *)"
```

```text
Release "som" has been upgraded. Happy Helming!
NAME: som
LAST DEPLOYED: Tue Oct  6 06:02:29 2026
NAMESPACE: som-shop
STATUS: deployed
REVISION: 2
DESCRIPTION: Upgrade complete
NOTES:
🐱 เปิดร้าน ร้านอาหารแมวน้องส้ม (release som, revision 2) ใน namespace som-shop แล้ว
   image หน้าร้าน: som-shop-web:1.7
   จำนวนบูธ: HPA 2–6 (cpu 50%)
   เปิดร้าน: curl -k https://shop.localhost:30081/api/whoami
   ตรวจรับร้าน: helm test som -n som-shop --logs

real	0m16.428s
REVISION	UPDATED                 	STATUS    	CHART         	APP VERSION	DESCRIPTION
1       	Tue Oct  6 06:02:28 2026	superseded	som-shop-0.1.0	1.7        	Release "som" failed: conflict occurred while ap
        	                        	          	              	           	- .data.SHOP_EYEBROW
        	                        	          	              	           	- .data.SHOP_FOOTER
        	                        	          	              	           	- .data.SHOP_PROMO && conflict o...
2       	Tue Oct  6 06:02:29 2026	deployed  	som-shop-0.1.0	1.7        	Upgrade complete
NAME                        READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/customers   0/0     0            0           18m
deployment.apps/som-admin   1/1     1            1           21m
deployment.apps/som-web     2/2     2            2           21m

NAME                      READY   AGE
statefulset.apps/som-db   1/1     21m

NAME                                          REFERENCE            TARGETS       MINPODS   MAXPODS   REPLICAS   AGE
horizontalpodautoscaler.autoscaling/som-web   Deployment/som-web   cpu: 2%/50%   2         6         2          19m

NAME                                  CLASS     HOSTS             ADDRESS     PORTS     AGE
ingress.networking.k8s.io/som-admin   traefik   admin.localhost   localhost   80, 443   21m
ingress.networking.k8s.io/som-shop    traefik   shop.localhost    localhost   80, 443   21m
ingress.networking.k8s.io/som-web     traefik   shop.localhost    localhost   80, 443   17s

NAME                                  STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
persistentvolumeclaim/data-som-db-0   Bound    pvc-df0cbf66-e96a-4b84-a06b-bd9e3511b621   1Gi        RWO            standard       <unset>                 21m
som-web-5d8b4f958-662lc 1.7 orders=3 products=6
cert หลัง: sha256 Fingerprint=DF:E2:AD:87:27:0E:8B:
******** (รหัสเดิมจาก lookup ซ่อนเป็น *)
```

รับร้านสำเร็จเป็น **rev 2 ใน 16.4 วินาที**

- **ออเดอร์เดิมอยู่ครบ** (`orders=3`) และ PVC เดิม (AGE 21m) — Helm ไม่ได้สร้างร้านใหม่ แค่ยึดของเดิมมาดูแล
- **ใบรับรองเดิม** (fingerprint `DF:E2:AD:87:…` ก่อน = หลัง) เพราะแม่พิมพ์ ingress `lookup` เจอ `som-tls` จึงไม่สร้างใบใหม่ หลังร้าน `admin.localhost` ที่ใช้ใบเดียวกันจึงไม่พัง
- **รหัสเดิม** (8 ตัวอักษร ซ่อนไว้) มาจาก `lookup` ไม่ต้องส่งรหัสในคำสั่ง
- HPA เดิมถูก chart รับไปดูแล หน้าร้านยัง 2/2 (ไม่มี `replicas` ใน chart จึงไม่ทับ HPA)
- rev 1 เปลี่ยนเป็น `superseded` แต่ DESCRIPTION ยังเป็นข้อความ failed เดิม (สมุดไม่ลบประวัติ)
- ตอนนี้มี Ingress 2 ตัวที่ host `shop.localhost` (`som-shop` ของบท 013 กับ `som-web` ของ chart) และ `customers` ที่ chart ไม่รู้จัก → 12.5 เก็บของเก่า

ดู field ที่ chart ไม่ได้ตั้งแต่ยังอยู่

```bash
kubectl -n som-shop get deploy som-web -o jsonpath='{range .metadata.managedFields[*]}{.manager}{" "}{.operation}{"\n"}{end}'
kubectl -n som-shop get deploy som-web -o jsonpath='{.metadata.annotations.kubernetes\.io/change-cause}{"\n"}{.metadata.annotations.meta\.helm\.sh/release-name}{"\n"}{.spec.template.spec.initContainers[*].name}{"\n"}'
kubectl -n som-shop get hpa som-web -o jsonpath='{.spec.behavior.scaleDown.stabilizationWindowSeconds}{"\n"}'
```

```text
helm Apply
kube-controller-manager Update
kubectl-rollout Update
kubectl Update
kubectl-client-side-apply Update
kube-controller-manager Update
1.7 เพิ่ม /api/work + HPA
som
wait-for-db db-seed
60
```

- มี field manager `helm Apply` เพิ่มเข้ามา และ annotation `meta.helm.sh/release-name: som` (ป้ายสาขา) แต่เจ้าของเดิมยังอยู่
- change-cause ของบท 013 และ HPA behavior (window 60 วินาที) **ยังอยู่** เพราะ chart ไม่ได้ตั้ง field เหล่านี้ (server-side apply ไม่ลบ field ของคนอื่น)
- **initContainer มี 2 ตัว: `wait-for-db` และ `db-seed`** — `db-seed` ของบท 013 ค้างอยู่ทั้งที่ chart ใช้ hook seed แทน (12.5 ขั้น ค แก้)

> **ทางสำรอง (ไม่มีร้านบท 013 — คลัสเตอร์ใหม่ของ LAB 0):** ไม่มีอะไรให้รับ ติดตั้งสาขา prod ใหม่ด้วย
> ```bash
> helm install som charts/som-shop -n som-shop --create-namespace -f charts/values-prod.yaml --set db.password=meow1234 --wait
> ```
> ผลจากรอบ pre-check ของบทนี้ (namespace ทดลอง): ติดตั้ง 16 วินาที, `http` ได้ `301`, `https` ตอบ 1.7, `curl --cacert` ด้วยใบจาก `som-tls` ผ่าน, HPA ทำงาน ทางนี้ **ไม่มีหลังร้าน `som-admin`** และไม่มี conflict ให้ข้าม 12.5 ทั้งหมด ใน 12.6 ไม่ต้องใส่ `--force-conflicts` และเลข revision จะเป็น 1 (install) → 2 (1.8) → 3 (`Rollback to 1`) ให้ใช้เลขของตัวเองใน 12.7–12.8

### 12.5 เก็บของเก่า

**ขั้น ก: Ingress เดิมและลูกค้าจำลอง** — Ingress `som-shop` (บท 012) ซ้ำ host กับ `som-web` ของ chart และ `customers` (บท 013) ไม่ได้อยู่ในชุด **ไม่ลบ** Middleware `redirect-https` เพราะ Ingress `som-admin` ยังใช้อยู่ (ลบแล้วหลังร้านได้ 404)

```bash
kubectl -n som-shop delete ingress som-shop
kubectl -n som-shop delete deploy customers
kubectl -n som-shop get ing,middleware
curl -si http://shop.localhost:30080/ | grep -iE "^HTTP|^location"
curl -sk https://shop.localhost:30081/api/whoami; echo
curl -sk -u som:meow-admin-123 -o /dev/null -w "admin %{http_code}\n" https://admin.localhost:30081/
curl -sk https://shop.localhost:30081/ | grep -oE "⚓ ท่าเรือ Kubernetes · [A-Za-z]+|🎉 เปิดสาขาใหม่[^<]*" | sort -u | head -2
```

```text
ingress.networking.k8s.io "som-shop" deleted from som-shop namespace
deployment.apps "customers" deleted from som-shop namespace
NAME                                  CLASS     HOSTS             ADDRESS     PORTS     AGE
ingress.networking.k8s.io/som-admin   traefik   admin.localhost   localhost   80, 443   21m
ingress.networking.k8s.io/som-web     traefik   shop.localhost    localhost   80, 443   17s

NAME                                       AGE
middleware.traefik.io/admin-auth           21m
middleware.traefik.io/redirect-https       21m
middleware.traefik.io/som-redirect-https   17s
HTTP/1.1 301 Moved Permanently
Location: https://shop.localhost:30081/
som-web-5d8b4f958-662lc 1.7

admin 200
⚓ ท่าเรือ Kubernetes · Helm
🎉 เปิดสาขาใหม่ด้วย Helm คำสั่งเดียว
```

ประตูหน้าร้านตอนนี้เป็นของ chart ทั้งหมด (Ingress `som-web` + Middleware `som-redirect-https`) redirect 301 ยังทำงาน หลังร้านยังเข้าได้ และหน้าร้านแสดงป้ายของบท 014 (`⚓ ท่าเรือ Kubernetes · Helm` + แถบ `🎉 เปิดสาขาใหม่ด้วย Helm คำสั่งเดียว` จากใบสั่ง prod)

🌐 ดู dashboard ของ Traefik ที่ `http://localhost:30082/dashboard/#/http/routers`

<p align="center" id="fig-30">
  <img src="images/screenshots/20261006_0629_lab12helm_03-traefik-routers.png" alt="รูปที่ 30 ภาพหน้าจอจริง Traefik routers" width="800"><br>
  <em><b>รูปที่ 30</b> ภาพหน้าจอจริงจากการทดลอง: dashboard ของ Traefik v3.7.13 ที่ติดตั้งจาก chart (LAB 10) หน้า HTTP Routers เห็น router ของ dev.shop.localhost (สาขา dev), admin.localhost และ shop.localhost (สาขา prod ที่ chart สร้าง) ครบทั้งทางเข้า web และ websecure (มีโล่ TLS) — ถ่ายตอนที่สาขา dev ถูกเปิดอีกครั้งเพื่อถ่ายภาพ</em>
</p>

สังเกตว่า router ของ Ingress ผูกกับ entrypoint `metrics` ด้วย เพราะ chart ของ Traefik เพิ่ม entrypoint `metrics` (พอร์ต 9100 สำหรับ Prometheus) ที่ static ของบท 012 ไม่มี และ Ingress ที่ไม่ระบุ entrypoint จะผูกกับทุก entrypoint (ยกเว้น `traefik`) — เป็นตัวอย่างว่า chart ทางการ "ไม่เหมือนเดิม 100%" ควรอ่านผล render ก่อน

**ขั้น ข: หา field ที่เหลือจากบท 013**

```bash
kubectl -n som-shop get deploy som-web -o json | python3 -c '
import json,sys; d=json.load(sys.stdin); s=d["spec"]["template"]["spec"]
print("initContainers:", [c["name"] for c in s.get("initContainers",[])])
print("pod annotations:", sorted(d["spec"]["template"]["metadata"].get("annotations",{}).keys()))'
helm get manifest som -n som-shop | python3 -c '
import sys,re; m=sys.stdin.read(); dep=[x for x in m.split("\n---") if "kind: Deployment" in x][0]
print("chart initContainers:", re.findall(r"- name: (wait-for-db|db-seed)", dep))'
kubectl -n som-shop get deploy som-web --show-managed-fields -o json | python3 -c '
import json,sys; d=json.load(sys.stdin)
for m in d["metadata"]["managedFields"]:
    f=json.dumps(m.get("fieldsV1",{}))
    print(m["manager"], m["operation"], "owns db-seed" if "db-seed" in f else "")'
```

```text
initContainers: ['wait-for-db', 'db-seed']
pod annotations: ['checksum/config', 'checksum/secret', 'kubectl.kubernetes.io/restartedAt']
chart initContainers: ['wait-for-db']
helm Apply
kube-controller-manager Update
kubectl-rollout Update
kubectl Update
kubectl-client-side-apply Update owns db-seed
kube-controller-manager Update
```

Deployment จริงมี initContainer 2 ตัว แต่ manifest ของ release (`helm get manifest`) มีแค่ `wait-for-db` และ **ผู้ถือ `db-seed` คือ `kubectl-client-side-apply`** Helm จึงไม่ลบให้ (ไม่ใช่ field ของ `helm`) — ไม่เสียหาย แต่ทุกบูธใหม่จะ seed ซ้ำโดยไม่จำเป็น และร้านไม่ตรงกับชุดแฟรนไชส์ annotation `restartedAt` ของ `kubectl-rollout` ก็ค้างเช่นกัน (ไม่มีผล)

> `kubectl get -o json` ซ่อน `managedFields` เป็นค่าเริ่มต้น ต้องใส่ `--show-managed-fields` (ในเครื่องทดลองรอบแรกที่ไม่ใส่ python ได้ `KeyError: 'managedFields'`)

**ขั้น ค: ถอด initContainer `db-seed` ระหว่างลูกค้าเข้าร้าน**

ใช้ JSON patch ที่มีคำสั่ง `test` ยืนยันก่อนว่าตำแหน่ง `initContainers/1` คือ `db-seed` จริง (ถ้าไม่ใช่ patch จะไม่ทำอะไรเลย กันลบผิดตัว) สั่ง patch ฉากหลังแล้วยิงลูกค้า 250 ครั้งพร้อมกัน

```bash
kubectl -n som-shop get deploy som-web -o jsonpath='{.spec.template.spec.initContainers[1].name}{"\n"}'
(sleep 2; kubectl -n som-shop patch deploy som-web --type=json -p='[{"op":"test","path":"/spec/template/spec/initContainers/1/name","value":"db-seed"},{"op":"remove","path":"/spec/template/spec/initContainers/1"}]') & ./hit.sh -q https://shop.localhost:30081/api/whoami 250 0.1; wait
kubectl -n som-shop rollout status deploy/som-web --timeout=180s
kubectl -n som-shop get pod -l app=som-web -o jsonpath='{range .items[*]}{.metadata.name}{" init="}{.spec.initContainers[*].name}{"\n"}{end}'
```

```text
db-seed
...................deployment.apps/som-web patched
...........................................................................................................
จำนวน  Pod  เวอร์ชัน
    250 1.7 (เวอร์ชัน)
ok=250 err=0 (ใช้เวลา 28.0 วินาที)
deployment "som-web" successfully rolled out
som-web-d776d4768-cqnvq init=wait-for-db
som-web-d776d4768-gbc7j init=wait-for-db
```

rolling update เปลี่ยนบูธทั้งสองเป็นแบบที่มีแค่ `wait-for-db` ลูกค้า **`ok=250 err=0`** ตอนนี้ร้านตรงกับชุดแฟรนไชส์แล้ว (ระบบจริงควรทำความสะอาดแบบนี้ทุกครั้งหลังรับของเดิมเข้า Helm)

### 12.6 อัปเกรดเป็น 1.8 ระหว่างลูกค้าเข้าร้าน

**ลองก่อนโดยไม่ force**

```bash
helm upgrade som charts/som-shop -n som-shop -f charts/values-prod.yaml --set web.image.tag=1.8 --wait 2>&1 | cut -c1-600
helm history som -n som-shop --max 2 | cut -c1-140
kubectl -n som-shop get deploy som-web -o jsonpath='{.spec.template.spec.containers[0].image}{"\n"}'
```

```text
level=WARN msg="upgrade failed" name=som error="conflict occurred while applying object som-shop/som-web apps/v1, Kind=Deployment: Apply failed with 1 conflict: conflict with \"kubectl-client-side-apply\" using apps/v1: .spec.template.spec.containers[name=\"web\"].image"
Error: UPGRADE FAILED: conflict occurred while applying object som-shop/som-web apps/v1, Kind=Deployment: Apply failed with 1 conflict: conflict with "kubectl-client-side-apply" using apps/v1: .spec.template.spec.containers[name="web"].image
REVISION	UPDATED                 	STATUS  	CHART         	APP VERSION	DESCRIPTION
2       	Tue Oct  6 06:02:29 2026	deployed	som-shop-0.1.0	1.7        	Upgrade complete
3       	Tue Oct  6 06:03:50 2026	failed  	som-shop-0.1.0	1.7        	Upgrade "som" failed: conflict occurred while applying object som-shop
som-shop-web:1.7
```

**conflict อีกครั้ง** ที่ field image: ตอนรับร้าน (rev 2) chart ตั้ง image เป็น `1.7` ซึ่ง **เท่ากับ** ค่าที่ `kubectl-client-side-apply` ถือไว้ จึงไม่ชน (ถือร่วมกัน) พอจะเปลี่ยนเป็น `1.8` ค่าไม่ตรงกับเจ้าของเดิมจึงชน (ทฤษฎีหัวข้อ 9.2) rev 3 `failed` ร้านยังเป็น 1.7 ไม่มีอะไรเสียหาย

**อัปเกรดจริงด้วย --force-conflicts (2 หน้าต่าง)**

**หน้าต่างที่ 2**

```bash
cd /workspace/014_kubernetes_helm/02_LAB
./hit.sh -q https://shop.localhost:30081/api/whoami 400 0.1
```

**หน้าต่างที่ 1** (ภายในไม่กี่วินาที)

```bash
t0=$(date +%s)
helm upgrade som charts/som-shop -n som-shop -f charts/values-prod.yaml --set web.image.tag=1.8 --force-conflicts --wait 2>&1 | grep -E "REVISION|STATUS|image|Error"
echo "upgrade: $(( $(date +%s)-t0 )) วินาที"
curl -sk https://shop.localhost:30081/api/whoami; echo
helm history som -n som-shop | cut -c1-120
```

หน้าต่างที่ 1

```text
STATUS: deployed
REVISION: 4
   image หน้าร้าน: som-shop-web:1.8
upgrade: 15 วินาที
som-web-56875c6cb5-6dwms 1.8

REVISION	UPDATED                 	STATUS    	CHART         	APP VERSION	DESCRIPTION
1       	Tue Oct  6 06:02:28 2026	superseded	som-shop-0.1.0	1.7        	Release "som" failed: conflict occurred while ap
        	                        	          	              	           	- .data.SHOP_EYEBROW
        	                        	          	              	           	- .data.SHOP_FOOTER
        	                        	          	              	           	- .data.SHOP_PROMO && conflict o...
2       	Tue Oct  6 06:02:29 2026	superseded	som-shop-0.1.0	1.7        	Upgrade complete
3       	Tue Oct  6 06:03:50 2026	failed    	som-shop-0.1.0	1.7        	Upgrade "som" failed: conflict occurred while ap
4       	Tue Oct  6 06:03:54 2026	deployed  	som-shop-0.1.0	1.7        	Upgrade complete
```

หน้าต่างที่ 2

```text
................................................................................................................
จำนวน  Pod  เวอร์ชัน
     84 1.7 (เวอร์ชัน)
    316 1.8 (เวอร์ชัน)
ok=400 err=0 (ใช้เวลา 44.7 วินาที)
```

<p align="center" id="fig-31">
  <img src="images/29-lab12-upgrade-err0.png" alt="รูปที่ 31 LAB 12 อัปเกรด 1.8 err=0" width="900"><br>
  <em><b>รูปที่ 31</b> อัปเกรด prod 1.7 → 1.8 ระหว่างลูกค้าเข้าร้าน (hit.sh) ไม่มีลูกค้าเจอ error แม้ upgrade แรกหลังรับร้านต้อง --force-conflicts อีกครั้ง</em>
</p>

rev 4 ใช้ **15 วินาที** ลูกค้า **`ok=400 err=0`** (84 ครั้งเจอ 1.7 ก่อนสลับ 316 ครั้งเจอ 1.8) — rolling update `maxUnavailable: 0` + readinessProbe + preStop ของบทที่ 7 ทำงานเหมือนเดิม Helm แค่เป็นคนสั่ง สังเกตคอลัมน์ **APP VERSION ยังเป็น 1.7** เพราะมาจาก `appVersion` ใน `Chart.yaml` ไม่ใช่ image ที่ใช้จริง (ทฤษฎีหัวข้อ 4.2)

### 12.7 ประวัติและย้อนรุ่น

```bash
helm history som -n som-shop -o table --max 10 | cut -c1-120
for r in 2 4; do echo "rev $r: $(helm get values som -n som-shop --revision $r -o json)"; done
```

```text
REVISION	UPDATED                 	STATUS    	CHART         	APP VERSION	DESCRIPTION
1       	Tue Oct  6 06:02:28 2026	superseded	som-shop-0.1.0	1.7        	Release "som" failed: conflict occurred while ap
...
2       	Tue Oct  6 06:02:29 2026	superseded	som-shop-0.1.0	1.7        	Upgrade complete
3       	Tue Oct  6 06:03:50 2026	failed    	som-shop-0.1.0	1.7        	Upgrade "som" failed: conflict occurred while ap
4       	Tue Oct  6 06:03:54 2026	deployed  	som-shop-0.1.0	1.7        	Upgrade complete
rev 2: {"hpa":{"enabled":true,"maxReplicas":6,"minReplicas":2},"ingress":{"enabled":true,"host":"shop.localhost","tls":true},"shop":{"APP_THEME":"harbor","SHOP_NAME":"ร้านอาหารแมวน้องส้ม","SHOP_PROMO":"🎉 เปิดสาขาใหม่ด้วย Helm คำสั่งเดียว"}}
rev 4: {"hpa":{"enabled":true,"maxReplicas":6,"minReplicas":2},"ingress":{"enabled":true,"host":"shop.localhost","tls":true},"shop":{"APP_THEME":"harbor","SHOP_NAME":"ร้านอาหารแมวน้องส้ม","SHOP_PROMO":"🎉 เปิดสาขาใหม่ด้วย Helm คำสั่งเดียว"},"web":{"image":{"tag":"1.8"}}}
```

ตาราง history บอกไม่ได้ว่ารุ่นไหนเป็น image อะไร (APP VERSION 1.7 ทุกแถว) ต้องดูใบสั่งของแต่ละ revision: rev 2 ไม่มี `web.image.tag` (= 1.7 จาก appVersion) rev 4 มี `tag: "1.8"` → **รุ่นที่ดีของ 1.7 คือ rev 2** (rev 3 ก็ "เป็น 1.7" แต่สถานะ `failed` — ห้ามเลือก และห้าม `helm rollback som` แบบไม่ใส่เลข เพราะจะไป rev 3)

**ย้อนเป็น 1.7 ระหว่างลูกค้าเข้าร้าน** — หน้าต่างที่ 2: `./hit.sh -q https://shop.localhost:30081/api/whoami 300 0.1` หน้าต่างที่ 1:

```bash
t0=$(date +%s)
helm rollback som 2 -n som-shop --wait 2>&1 | tail -1
echo "rollback: $(( $(date +%s)-t0 )) วินาที"
helm history som -n som-shop --max 2 | cut -c1-120
curl -sk https://shop.localhost:30081/api/whoami; echo
```

หน้าต่างที่ 1

```text
Rollback was a success! Happy Helming!
rollback: 11 วินาที
REVISION	UPDATED                 	STATUS    	CHART         	APP VERSION	DESCRIPTION
4       	Tue Oct  6 06:03:54 2026	superseded	som-shop-0.1.0	1.7        	Upgrade complete
5       	Tue Oct  6 06:04:49 2026	deployed  	som-shop-0.1.0	1.7        	Rollback to 2
som-web-d776d4768-twh2d 1.7

```

หน้าต่างที่ 2

```text
.......................................................................................................
จำนวน  Pod  เวอร์ชัน
    215 1.7 (เวอร์ชัน)
     85 1.8 (เวอร์ชัน)
ok=300 err=0 (ใช้เวลา 33.6 วินาที)
```

<p align="center" id="fig-32">
  <img src="images/30-lab12-rollback.png" alt="รูปที่ 32 LAB 12 rollback ระบุเลข" width="900"><br>
  <em><b>รูปที่ 32</b> helm history แล้ว rollback ไป revision ที่เป็น 1.7 (ระบุเลข) ได้หน้าใหม่ในสมุด ลูกค้าไม่เจอ error</em>
</p>

rollback **11 วินาที** ได้ **rev 5 `Rollback to 2`** ลูกค้า **`ok=300 err=0`** — ทั้งร้าน (ป้าย, ซอง, Deployment, HPA, Ingress) กลับไปตามใบสั่งของ rev 2 ไม่ใช่แค่ Deployment แบบ `kubectl rollout undo` สังเกตว่า Pod ที่ได้ (`som-web-d776d4768-…`) คือ ReplicaSet เดียวกับหลัง 12.5 ขั้น ค เพราะ Pod template เหมือนกันทุกตัวอักษร Deployment จึงนำ ReplicaSet เดิมกลับมาใช้

**upgrade กลับเป็น 1.8 — คราวนี้ไม่ต้อง force** (หน้าต่างที่ 2 ยิง 300 ครั้งเหมือนเดิม)

```bash
t0=$(date +%s)
helm upgrade som charts/som-shop -n som-shop -f charts/values-prod.yaml --set web.image.tag=1.8 --wait 2>&1 | grep -E "REVISION|STATUS|Error"
echo "upgrade: $(( $(date +%s)-t0 )) วินาที"
helm history som -n som-shop --max 3 | cut -c1-120
```

```text
STATUS: deployed
REVISION: 6
upgrade: 15 วินาที
REVISION	UPDATED                 	STATUS    	CHART         	APP VERSION	DESCRIPTION
4       	Tue Oct  6 06:03:54 2026	superseded	som-shop-0.1.0	1.7        	Upgrade complete
5       	Tue Oct  6 06:04:49 2026	superseded	som-shop-0.1.0	1.7        	Rollback to 2
6       	Tue Oct  6 06:05:23 2026	deployed  	som-shop-0.1.0	1.7        	Upgrade complete
```

หน้าต่างที่ 2 ได้ `ok=300 err=0` (1.7 = 87, 1.8 = 213) — `--force-conflicts` ครั้งเดียวใน rev 4 โอน field image ให้ `helm` แล้ว ต่อจากนี้ upgrade/rollback เป็นงานปกติของ Helm

**รอบถ่ายภาพหน้าจอ** (ทำซ้ำบนคลัสเตอร์เดิมหลังจบขั้น 12.10 โดยเปิดสาขา dev อีกครั้งและมีออเดอร์ทดสอบเพิ่ม ร้าน prod จึงมี 5 ออเดอร์) ผลคำสั่งจริงของรอบนั้น

```text
$ time helm rollback som 2 -n som-shop --wait
Rollback was a success! Happy Helming!

real	0m10.338s
--- hit.sh ระหว่าง rollback
ok=250 err=0 (ใช้เวลา 28.0 วินาที)
$ time helm upgrade som charts/som-shop -n som-shop -f charts/values-prod.yaml --set web.image.tag=1.8 --wait
Release "som" has been upgraded. Happy Helming!
NAME: som
LAST DEPLOYED: Tue Oct  6 06:29:41 2026
NAMESPACE: som-shop
STATUS: deployed
REVISION: 8

real	0m13.834s
--- hit.sh ระหว่าง upgrade
ok=250 err=0 (ใช้เวลา 28.0 วินาที)
$ helm history som -n som-shop --max 3
REVISION	UPDATED                 	STATUS    	CHART         	APP VERSION	DESCRIPTION
6       	Tue Oct  6 06:05:23 2026	superseded	som-shop-0.1.0	1.7        	Upgrade complete
7       	Tue Oct  6 06:29:13 2026	superseded	som-shop-0.1.0	1.7        	Rollback to 2
8       	Tue Oct  6 06:29:41 2026	deployed  	som-shop-0.1.0	1.7        	Upgrade complete
```

<p align="center" id="fig-33">
  <img src="images/screenshots/20261006_0629_lab12helm_04-after-rollback-1.7.png" alt="รูปที่ 33 ภาพหน้าจอจริง หลัง rollback เป็น 1.7" width="800"><br>
  <em><b>รูปที่ 33</b> ภาพหน้าจอจริงจากการทดลอง: หลัง helm rollback som 2 --wait (10.3 วินาที ได้ revision 7 &quot;Rollback to 2&quot;) หน้าร้าน https://shop.localhost:30081 กลับเป็นป้ายเวอร์ชัน 1.7 ออเดอร์ 5 รายการยังอยู่ ระหว่างนั้น hit.sh ได้ ok=250 err=0</em>
</p>

<p align="center" id="fig-34">
  <img src="images/screenshots/20261006_0629_lab12helm_05-after-upgrade-1.8.png" alt="รูปที่ 34 ภาพหน้าจอจริง หลัง upgrade กลับ 1.8" width="800"><br>
  <em><b>รูปที่ 34</b> ภาพหน้าจอจริงจากการทดลอง: helm upgrade ... --set web.image.tag=1.8 --wait (13.8 วินาที ได้ revision 8 ไม่ต้อง --force-conflicts แล้ว) หน้าร้านกลับเป็นเวอร์ชัน 1.8 ระหว่างนั้น hit.sh ได้ ok=250 err=0</em>
</p>

### 12.8 ซองในสมุดของสาขา prod

```bash
kubectl -n som-shop get secret -l owner=helm,name=som
kubectl -n som-shop get secret sh.helm.release.v1.som.v2 -o jsonpath='{.data.release}' | base64 -d | base64 -d | gzip -d \
  | python3 -c 'import json,sys,re; r=json.load(sys.stdin); print("config:", json.dumps(r["config"],ensure_ascii=False)); print(re.findall(r"DATABASE_URL: .*", r["manifest"])); print(re.findall(r"POSTGRES_PASSWORD: .*", r["manifest"])); print("tls.key อยู่ใน manifest:", "tls.key:" in r["manifest"])'
```

```text
NAME                        TYPE                 DATA   AGE
sh.helm.release.v1.som.v1   helm.sh/release.v1   1      3m39s
sh.helm.release.v1.som.v2   helm.sh/release.v1   1      3m38s
sh.helm.release.v1.som.v3   helm.sh/release.v1   1      2m17s
sh.helm.release.v1.som.v4   helm.sh/release.v1   1      2m13s
sh.helm.release.v1.som.v5   helm.sh/release.v1   1      78s
sh.helm.release.v1.som.v6   helm.sh/release.v1   1      44s
config: {"hpa": {"enabled": true, "maxReplicas": 6, "minReplicas": 2}, "ingress": {"enabled": true, "host": "shop.localhost", "tls": true}, "shop": {…}}
['DATABASE_URL: "postgres://som:meow1234@som-db-0.som-db:5432/catshop"']
['POSTGRES_PASSWORD: "meow1234"']
tls.key อยู่ใน manifest: True
```

(ผล config ตัดให้สั้น) rev 2 **ไม่ได้ส่งรหัสในคำสั่งเลย** (`config` ไม่มี `db.password`) แต่ **manifest** เก็บผล render ของ Secret ทั้งก้อน จึงมีรหัสฐานข้อมูล (ที่ `lookup` อ่านมา) **และกุญแจลับของใบรับรอง (`tls.key`)** ด้วย — การปกป้องร้านจึงต้องคุมสิทธิ์อ่าน Secret ใน namespace (RBAC บทที่ 11) ไม่ใช่แค่ไม่ใส่รหัสในใบสั่ง (ทฤษฎีหัวข้อ 10) **ห้ามคัดลอกหรือแชร์ผลถอดของ `tls.key`**

### 12.9 ปิดสาขา dev

**ขั้น ก: uninstall แล้วตู้เซฟค้าง**

```bash
curl -s -XPOST -H "content-type: application/json" -d '{"product_id":1,"qty":2}' http://dev.shop.localhost:30080/api/orders; echo
curl -s http://dev.shop.localhost:30080/api/stats; echo
helm uninstall som -n som-dev
sleep 8; kubectl -n som-dev get all,pvc,secret
helm list -A
```

```text
{"ok":true,"order_id":1,"product":{"id":1,"name_th":"อาหารเม็ดสูตรปลาทูน่า 1.5 กก.","stock":18}}
som-web-64c9f5cd95-lvbr9 1.7 orders=1 products=6

release "som" uninstalled
NAME                                  STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
persistentvolumeclaim/data-som-db-0   Bound    pvc-634d0a60-bd70-46ad-b23d-605ccc52a76b   1Gi        RWO            standard       <unset>                 4m7s
NAME          	NAMESPACE  	REVISION	UPDATED                                	STATUS  	CHART                	APP VERSION
metrics-server	kube-system	1       	2026-10-06 05:59:54.289839067 +0700 +07	deployed	metrics-server-3.14.0	0.9.0
som           	som-shop   	6       	2026-10-06 06:05:23.632314816 +0700 +07	deployed	som-shop-0.1.0       	1.7
traefik       	traefik    	1       	2026-10-06 05:58:43.60397903 +0700 +07 	deployed	traefik-41.6.1       	v3.7.13
```

(ออเดอร์ใช้ key `product_id` และ `qty` — ถ้าส่ง `productId` แอปตอบ `ข้อมูลไม่ถูกต้อง`) หลัง uninstall ทุก object ของสาขาหาย **เหลือแต่ตู้เซฟ `data-som-db-0` สถานะ `Bound`** (PVC จาก `volumeClaimTemplates` ไม่ใช่ส่วนของ release — บทที่ 9)

**ขั้น ข: ติดตั้งใหม่ด้วยรหัสเดิม → ข้อมูลเดิมกลับมา**

```bash
time helm install som charts/som-shop -n som-dev -f charts/values-dev.yaml --set db.password=meow1234 --wait | grep -E "STATUS|REVISION"
curl -s http://dev.shop.localhost:30080/api/stats; echo
helm uninstall som -n som-dev; sleep 8
```

```text
STATUS: deployed
REVISION: 1

real	0m11.904s
som-web-64c9f5cd95-869r5 1.7 orders=1 products=6

release "som" uninstalled
```

<p align="center" id="fig-35">
  <img src="images/31-lab12-uninstall-dev.png" alt="รูปที่ 35 LAB 12 uninstall สาขา dev" width="900"><br>
  <em><b>รูปที่ 35</b> helm uninstall สาขา dev: ร้านถูกรื้อ แต่ตู้เซฟ (PVC data-som-db-0) ยังอยู่ ติดตั้งใหม่รหัสเดิมได้ออเดอร์เดิม</em>
</p>

สาขาใหม่ REVISION 1 (สมุดเล่มใหม่) แต่ **`orders=1` กลับมา** เพราะ StatefulSet ใช้ PVC ชื่อเดิม ติดตั้งเร็วขึ้น (11.9 วินาที) เพราะ db ไม่ต้องสร้างฐานข้อมูลใหม่ จากนั้น uninstall อีกครั้ง (PVC ยังค้างอยู่) เพื่อลองกับดักถัดไป

**ขั้น ค: กับดัก — ติดตั้งใหม่ด้วยรหัสใหม่ (ไม่ใส่ --wait)**

`purr5678` เป็นรหัสตัวอย่างอีกตัว

```bash
time helm install som charts/som-shop -n som-dev -f charts/values-dev.yaml --set db.password=purr5678 --timeout 90s 2>&1 | tail -2
helm list -n som-dev
kubectl -n som-dev get pod,job
kubectl -n som-dev logs job/som-seed -c seed --tail=3 2>&1 | tail -3
```

```text
Error: INSTALLATION FAILED: failed post-install: resource Job/som-dev/som-seed not ready. status: Failed, message: Job Failed. failed: 1/1

real	0m45.711s
NAME	NAMESPACE	REVISION	UPDATED                                	STATUS	CHART         	APP VERSION
som 	som-dev  	1       	2026-10-06 06:09:08.509818895 +0700 +07	failed	som-shop-0.1.0	1.7
NAME                          READY   STATUS    RESTARTS      AGE
pod/som-db-0                  1/1     Running   0             46s
pod/som-seed-9sjtp            0/1     Error     3 (29s ago)   46s
pod/som-web-f45d5f58d-zqjwz   0/1     Running   0             46s

NAME                 STATUS   COMPLETIONS   DURATION   AGE
job.batch/som-seed   Failed   0/1           46s        46s
}

Node.js v22.23.3
```

<p align="center" id="fig-36">
  <img src="images/32-lab12-wrong-password.png" alt="รูปที่ 36 LAB 12 กับดักรหัสใหม่" width="900"><br>
  <em><b>รูปที่ 36</b> กับดัก: ติดตั้ง dev ใหม่ (ไม่ใส่ --wait) ด้วยรหัสใหม่ แต่ตู้เซฟเดิมใช้รหัสเก่า → hook เติมสินค้าล้ม failed post-install (ถ้าใส่ --wait จะล้มที่ som-web not ready ก่อนถึง hook)</em>
</p>

PostgreSQL ตั้งรหัสเฉพาะตอนสร้าง data directory ครั้งแรก ตู้เซฟเดิมจึงยังล็อกด้วย `meow1234` ขณะที่ Secret ใหม่ของ chart เป็น `purr5678` ผล:

- หน้าร้าน `0/1` (readinessProbe `/api/health` ต่อ db ไม่ได้)
- Job seed (`post-install`) login ไม่ได้ ล้มครบ `backoffLimit: 3` → **`failed post-install ... Job Failed`** ใน 45.7 วินาที release เป็น `failed`
- Job/Pod ที่ล้ม **ยังอยู่ให้ดู log** เพราะ delete policy ไม่มี `hook-failed` (ท้าย log เป็น stack trace ของ Node.js ดูเต็มด้วย `kubectl -n som-dev logs job/som-seed -c seed`)

ผลจริงอีกแบบ (ไม่ต้องทำตาม ใช้เวลา 90 วินาที): ถ้าสั่งแบบเดียวกันแต่ **ใส่ `--wait --timeout 90s`** Helm รอหน้าร้านพร้อมก่อนถึง hook จึงล้มที่หน้าร้านแทน

```text
Error: INSTALLATION FAILED: resource Deployment/som-dev/som-web not ready. status: InProgress, message: Available: 0/1
context deadline exceeded

real	1m30.215s
```

**แก้:** upgrade release ที่ `failed` ด้วยรหัสเดิม (upgrade ได้เลย ไม่ต้อง uninstall ก่อน)

```bash
helm upgrade som charts/som-shop -n som-dev -f charts/values-dev.yaml --set db.password=meow1234 --wait 2>&1 | grep -E "STATUS|REVISION|Error"
curl -s http://dev.shop.localhost:30080/api/stats; echo
```

```text
STATUS: deployed
REVISION: 2
som-web-64c9f5cd95-b4q8j 1.7 orders=1 products=6

```

(ผลนี้มาจากการแก้หลังกรณี `--wait` ในเครื่องทดลอง สภาพเริ่มต้นเหมือนกัน คือ release `failed` + ตู้เซฟเดิม) ร้านกลับมาพร้อมออเดอร์เดิม ถ้าต้องการเริ่มสาขาใหม่จริง ๆ ด้วยรหัสใหม่ ต้องลบตู้เซฟเดิมก่อน (ข้อมูลหาย)

**ลบสาขา dev จริงทั้งหมด (รวมตู้เซฟ)**

```bash
helm uninstall som -n som-dev
kubectl delete ns som-dev
```

```text
release "som" uninstalled
namespace "som-dev" deleted
```

### 12.10 ตรวจรับร้านและปิดบท

```bash
helm test som -n som-shop --logs | sed -n '/Phase/,$p'
kubectl -n som-shop get deploy,sts,hpa,ing
kubectl top pod -n som-shop
curl -sk https://shop.localhost:30081/api/stats; echo
curl -s --cacert <(kubectl -n som-shop get secret som-tls -o jsonpath='{.data.tls\.crt}' | base64 -d) https://shop.localhost:30081/api/whoami; echo " (cacert ok)"
helm list -A
```

```text
Phase:          Succeeded

POD LOGS: som-test-health (curl)
health:   {"ok":true,"db":"up"}
whoami:   som-web-56875c6cb5-9r2rg 1.8
products: ok

NAME                        READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/som-admin   1/1     1            1           27m
deployment.apps/som-web     2/2     2            2           27m

NAME                      READY   AGE
statefulset.apps/som-db   1/1     27m

NAME                                          REFERENCE            TARGETS       MINPODS   MAXPODS   REPLICAS   AGE
horizontalpodautoscaler.autoscaling/som-web   Deployment/som-web   cpu: 2%/50%   2         6         2          25m

NAME                                  CLASS     HOSTS             ADDRESS     PORTS     AGE
ingress.networking.k8s.io/som-admin   traefik   admin.localhost   localhost   80, 443   27m
ingress.networking.k8s.io/som-web     traefik   shop.localhost    localhost   80, 443   6m6s
NAME                         CPU(cores)   MEMORY(bytes)
som-admin-5f75ddc94b-lqswj   1m           23Mi
som-db-0                     8m           39Mi
som-web-56875c6cb5-5c54d     2m           42Mi
som-web-56875c6cb5-9r2rg     2m           41Mi
som-web-56875c6cb5-9r2rg 1.8 orders=3 products=6

som-web-56875c6cb5-5c54d 1.8
 (cacert ok)
NAME          	NAMESPACE  	REVISION	UPDATED                                	STATUS  	CHART                	APP VERSION
metrics-server	kube-system	1       	2026-10-06 05:59:54.289839067 +0700 +07	deployed	metrics-server-3.14.0	0.9.0
som           	som-shop   	6       	2026-10-06 06:05:23.632314816 +0700 +07	deployed	som-shop-0.1.0       	1.7
traefik       	traefik    	1       	2026-10-06 05:58:43.60397903 +0700 +07 	deployed	traefik-41.6.1       	v3.7.13
```

ผู้ตรวจรับร้านผ่าน (หน้าร้าน 1.8 ต่อ db ได้) HPA 2–6 ทำงานด้วย metrics-server จาก chart, `curl --cacert` ด้วยใบจาก `som-tls` ผ่านโดยไม่ต้อง `-k` (ใบเดิมของบท 012 ใช้ต่อได้จริง) ออเดอร์เดิม 3 รายการอยู่ครบ และ **`helm list -A` เห็นทั้งท่าเรือ 3 release** — ร้าน ประตู และเจ้าหน้าที่จดมิเตอร์ ติดตั้ง/อัปเกรด/ย้อนได้ด้วยคำสั่งเดียวทั้งหมด 🌐 เปิด `http://shop.localhost:30080`

<p align="center" id="fig-37">
  <img src="images/screenshots/20261006_0629_lab12helm_01-prod-1.8.png" alt="รูปที่ 37 ภาพหน้าจอจริง หน้าร้าน prod 1.8" width="800"><br>
  <em><b>รูปที่ 37</b> ภาพหน้าจอจริงจากการทดลอง: สาขาจริง (release som ใน namespace som-shop) รุ่น 1.8 ที่ https://shop.localhost:30081 หัวร้าน &quot;⚓ ท่าเรือ Kubernetes · Helm&quot; แถบ &quot;🎉 เปิดสาขาใหม่ด้วย Helm คำสั่งเดียว&quot; จากใบสั่ง prod และออเดอร์ 5 รายการ (ออเดอร์เดิมของบท 013 + ออเดอร์ทดสอบรอบถ่ายภาพ) ไม่หายระหว่างรับร้าน อัปเกรด และย้อนรุ่น</em>
</p>

<p align="center" id="fig-38">
  <img src="images/33-lab12-checklist.png" alt="รูปที่ 38 LAB 12 ตรวจรับร้าน" width="900"><br>
  <em><b>รูปที่ 38</b> ตรวจรับร้าน: dev helm test ผ่าน, prod HTTPS + HPA, upgrade 1.8 err=0, rollback ระบุเลข, เข้าใจ PVC ค้าง</em>
</p>

| ข้อตรวจรับ | ผลจริง (เครื่อง 4 CPU) |
|---|---|
| สาขา dev คำสั่งเดียว | 18.0 วินาที, `helm test` Succeeded, ธีม `sunset`, ชื่อ `(dev)` |
| รับร้านเดิมเป็น prod | rev 1 `failed` (conflict) → rev 2 `deployed` 16.4 วินาที, `orders=3`, ใบรับรองและรหัสเดิม |
| ร้านตรงกับชุด | ลบ Ingress `som-shop`, `customers`, initContainer `db-seed` (`ok=250 err=0`) |
| อัปเกรด 1.8 | rev 3 `failed` (conflict image) → rev 4 + `--force-conflicts` 15 วินาที `ok=400 err=0` |
| ย้อนรุ่นระบุเลข | `helm rollback som 2` → rev 5 `Rollback to 2` 11 วินาที `ok=300 err=0` |
| upgrade ครั้งต่อไปไม่ต้อง force | rev 6 15 วินาที `ok=300 err=0` |
| ความลับใน release Secret | rev 2 มีรหัส db และ `tls.key` แม้ไม่ได้ส่งรหัส |
| PVC ค้าง | uninstall dev เหลือ `data-som-db-0`, รหัสเดิมได้ `orders=1`, รหัสใหม่ `failed post-install` |
| ปิดท้าย | prod test Succeeded (1.8), `--cacert` ผ่าน, `helm list -A` 3 release |

<p align="center" id="fig-39">
  <img src="images/34-lab12-wrap-up.png" alt="รูปที่ 39 ปิดบท" width="900"><br>
  <em><b>รูปที่ 39</b> ปิดบท: เก็บ chart + ใบสั่งใน Git ให้หุ่นยนต์ GitOps ดูแล (Argo CD/Flux), แผ่นใสซ้อน (Kustomize), หุ่นยนต์ดูแลร้าน (operator)</em>
</p>

ร้านน้องส้มเป็น "ชุดแฟรนไชส์" แล้ว แต่ยังเหลือโจทย์ที่ Helm ไม่ได้ตอบ

- **ใครเป็นคนสั่ง `helm upgrade`?** ตอนนี้คือเราพิมพ์เอง ถ้ามีคนแก้ร้านด้วย `kubectl edit` ก็ไม่มีใครรู้ → **GitOps** (Argo CD/Flux): เก็บ `charts/som-shop` + `values-prod.yaml` ใน Git ให้ controller ทำให้ร้านตรงกับ Git เสมอ (ทฤษฎีหัวข้อ 16)
- **ปรับ chart ของคนอื่นเล็กน้อยโดยไม่ fork** → Kustomize/post-renderer (ทฤษฎีหัวข้อ 15)
- **ใครดูแลครัวหลังเปิดร้าน?** Helm ติดตั้งจบแล้วไม่สำรองข้อมูล ไม่ซ่อม db ไม่อัปเกรด PostgreSQL ให้ → **operator** (บทถัดไป)
- **รหัสยังอยู่ใน release Secret** → External Secrets / Sealed Secrets / SOPS

**คำถามท้าย LAB 12**

1. ทำไมรับร้านน้องส้มเข้า Helm ได้ แต่รับ Traefik static ไม่ได้ (เทียบ selector) และถ้าเผลอ `helm uninstall som -n som-shop` หลัง 12.4 (ข) จะเกิดอะไร
2. ทำไม upgrade แรกหลังรับร้านยัง conflict ที่ image ทั้งที่ตอนรับร้านใส่ `--force-conflicts` แล้ว และทำไม upgrade ครั้งที่สอง (rev 6) ไม่ต้อง force
3. ถ้าต้องย้อนเป็น 1.7 ควร rollback เลขอะไร ทำไมไม่ใช่ rev 3 และทำไมเลข revision ไม่ถอยหลัง
4. ทำไม PVC `data-som-db-0` ค้างหลัง `helm uninstall` เป็นข้อดีหรือข้อเสีย และทำไมติดตั้งใหม่ด้วยรหัสใหม่จึงล้ม
5. ใครอ่านรหัสฐานข้อมูลและ `tls.key` ของร้าน prod ได้บ้าง (ทั้งจาก Secret ของร้านและจาก release Secret) จะลดความเสี่ยงอย่างไร
6. ถ้าจะใช้ GitOps ดูแลร้านนี้ จะเก็บอะไรใน Git บ้าง และอะไรห้ามเก็บ

**เก็บกวาด LAB 12:** สาขา dev ถูกลบแล้วใน 12.9 สาขา prod (`som` ใน `som-shop`), Traefik และ metrics-server **เก็บไว้** (ดูตารางท้ายเอกสาร)

---

## LAB เสริม: helm-diff และ umbrella chart (ไม่บังคับ)

ทำหลัง LAB 12 (ใช้ release `som` ใน `som-shop`) ต้องต่ออินเทอร์เน็ต (GitHub และ `ghcr.io`)

### ก. helm-diff: ดูความต่างก่อน upgrade

plugin `helm-diff` แสดงว่า upgrade จะเปลี่ยนอะไร (คล้าย `git diff`) ก่อนสั่งจริง Helm 4 ตรวจที่มาของ plugin และ helm-diff ต้องเป็น **v3.15.15 ขึ้นไป** จึงใช้กับ Helm 4 ได้

```bash
cd /workspace/014_kubernetes_helm/02_LAB
timeout 180 helm plugin install https://github.com/databus23/helm-diff --version v3.15.15 2>&1 | tail -1
timeout 180 helm plugin install https://github.com/databus23/helm-diff --version v3.15.15 --verify=false 2>&1 | tail -1
helm plugin list
helm diff upgrade som charts/som-shop -n som-shop -f charts/values-prod.yaml --set web.image.tag=1.7 2>&1 | grep -E "^[+-] |has changed|Error" | head -12
helm plugin uninstall diff
```

```text
Error: plugin source does not support verification. Use --verify=false to skip verification
Installed plugin: diff
NAME	VERSION	TYPE  	APIVERSION	PROVENANCE	SOURCE
diff	3.15.15	cli/v1	legacy    	unknown   	unknown
som-shop, som-announcement, ConfigMap (v1) has changed:
-     app.kubernetes.io/version: "1.8"
+     app.kubernetes.io/version: "1.7"
som-shop, som-db, Service (v1) has changed:
-     app.kubernetes.io/version: "1.8"
+     app.kubernetes.io/version: "1.7"
som-shop, som-db, StatefulSet (apps) has changed:
-     app.kubernetes.io/version: "1.8"
+     app.kubernetes.io/version: "1.7"
som-shop, som-db-secret, Secret (v1) has changed:
-     app.kubernetes.io/version: "1.8"
+     app.kubernetes.io/version: "1.7"
Uninstalled plugin: diff
```

- แหล่งที่ไม่ได้เซ็นต้องใส่ `--verify=false` เอง (`PROVENANCE unknown`) — ใช้เฉพาะ plugin ที่เชื่อถือได้และ pin `--version`
- diff ถ้าย้อน tag เป็น 1.7 จะเปลี่ยน label `app.kubernetes.io/version` ของ **ทุก** object (ไม่ใช่แค่ Deployment) เพราะตรายาง labels ใช้ค่า tag — ข้อมูลแบบนี้ช่วยตัดสินใจก่อน upgrade

### ข. umbrella chart: กล่องใหญ่ที่มีกล่องย่อย

```bash
cd labs/labx-extra
helm dependency list harbor-addons
helm dependency update harbor-addons 2>&1 | tail -3
ls harbor-addons harbor-addons/charts
helm dependency list harbor-addons
helm template ha harbor-addons -n kube-system | grep -E "^kind:" | sort | uniq -c
helm template ha harbor-addons -n kube-system --set podinfo.enabled=true | grep -E "^# Source: [a-z-]+/charts/[a-z-]+" -o | sort | uniq -c
helm template ha harbor-addons -n kube-system | grep -- "--kubelet-insecure-tls"
rm -rf harbor-addons/charts harbor-addons/Chart.lock
cd ../..
```

```text
NAME          	VERSION	REPOSITORY                                       	STATUS
metrics-server	3.14.0 	https://kubernetes-sigs.github.io/metrics-server/	missing
podinfo       	6.15.0 	oci://ghcr.io/stefanprodan/charts                	missing

Pulled: ghcr.io/stefanprodan/charts/podinfo:6.15.0
Digest: sha256:ff3d3e14728f75476ed4d43c14f80d52d81d36bc16906843463d464c6146f0d8
Deleting outdated charts
harbor-addons:
Chart.lock
Chart.yaml
charts
values.yaml

harbor-addons/charts:
metrics-server-3.14.0.tgz
podinfo-6.15.0.tgz
NAME          	VERSION	REPOSITORY                                       	STATUS
metrics-server	3.14.0 	https://kubernetes-sigs.github.io/metrics-server/	ok
podinfo       	6.15.0 	oci://ghcr.io/stefanprodan/charts                	ok

      1 kind: APIService
      2 kind: ClusterRole
      2 kind: ClusterRoleBinding
      1 kind: Deployment
      1 kind: RoleBinding
      1 kind: Service
      1 kind: ServiceAccount
      9 # Source: harbor-addons/charts/metrics-server
      5 # Source: harbor-addons/charts/podinfo
            - --kubelet-insecure-tls
```

- `helm dependency update` ดึง subchart จากทั้ง HTTP repo และ OCI (`oci://ghcr.io/...`) มาไว้ใน `charts/` และเขียน `Chart.lock`
- ค่าเริ่มต้น `podinfo.enabled: false` → render ได้เฉพาะ metrics-server 9 object (`condition` ทำงาน) เปิดด้วย `--set podinfo.enabled=true` ได้ object ของ podinfo เพิ่ม 5 ตัว
- ค่าใต้ key `metrics-server:` ใน `values.yaml` ของกล่องใหญ่ไปถึง subchart (`--kubelet-insecure-tls`)
- LAB นี้ render อย่างเดียว **ไม่ติดตั้ง** (metrics-server ตัวจริงจาก LAB 10 ทำงานอยู่แล้ว ติดตั้งซ้ำจะชน)

---

## Troubleshooting

| อาการ | สาเหตุ | วิธีแก้ |
|---|---|---|
| `Error: INSTALLATION FAILED: ... cannot reuse a name that is still in use` | มี release ชื่อนั้นอยู่แล้ว (รวม `failed` หรือ `uninstalled` ที่ keep-history) | `helm list -n <ns>` แล้ว `helm uninstall`, `helm rollback` หรือใช้ `helm upgrade --install` |
| `... exists and cannot be imported into the current release: invalid ownership metadata` | object ชื่อเดียวกันถูกสร้างด้วย `kubectl` (ไม่มีป้าย Helm) | ถ้า selector ตรง: `--take-ownership --force-conflicts` (LAB 12) ถ้าไม่ตรง: ลบของเดิมแล้วติดตั้ง (LAB 10) |
| `conflict occurred while applying object ... conflicts with "kubectl-client-side-apply"` | field มีเจ้าของอื่นถือด้วยค่าต่างกัน (server-side apply) | ตรวจว่าค่าใน chart ถูกแล้วใส่ `--force-conflicts` (ครั้งเดียวพอ) และเลิกแก้ object นั้นด้วย kubectl |
| `spec.selector: Invalid value: ...: field is immutable` | selector ของ chart ต่างจากของเดิม | ลบ Deployment เดิมแล้วติดตั้งใหม่ (มี downtime) — **อย่า uninstall release ที่ adopt ล้ม** |
| `STATUS: deployed` แต่ Pod `ErrImagePull`/`CrashLoopBackOff` | ไม่ได้ใส่ `--wait` (Helm 4 = `hookOnly`) | ใส่ `--wait` (หรือ `--rollback-on-failure`) ทุกครั้ง แล้ว `helm rollback <rel> <rev> --wait` |
| upgrade แล้ว Ingress/ค่าอื่นหาย ได้ 404 | upgrade ส่งแค่ `--set` บางค่า ค่าอื่นกลับค่าเริ่มต้น | ส่ง `-f <ใบสั่ง>` ทุกครั้ง หรือ `--reuse-values` (LAB 3) |
| rollback แล้วร้านกลับไปพัง | `helm rollback <rel>` ไม่ใส่เลข ไปรุ่นก่อนหน้าที่ `failed` | `helm history` แล้ว rollback ระบุเลขรุ่นที่ดี (LAB 4) |
| `--dry-run=server` ผ่านแต่ install จริงล้ม | Helm 4.3 dry-run ไม่ส่ง object ให้ API server validate | `helm template ... \| kubectl apply --dry-run=server -f -` (LAB 6) |
| `yaml: line N: mapping values are not allowed in this context` | ย่อหน้า/`indent`/`{{-` ผิด (N = บรรทัดของผล render) | `helm template --debug` ดู YAML ที่พัง (LAB 6) |
| `function "xxx" not defined` | สะกดฟังก์ชันผิด | ดูรายชื่อฟังก์ชันในเอกสาร Helm/Sprig |
| `execution error at (som-shop/templates/web.yaml:29:28): ติดตั้งครั้งแรกต้องตั้งรหัสฐานข้อมูล` | `helm template` หรือ install ครั้งแรกโดยไม่ใส่รหัส (`lookup` ว่าง) | ใส่ `--set db.password=<รหัส>` (template ใส่ค่าอะไรก็ได้ เช่น `x`) |
| `values don't meet the specifications of the schema(s)` | ใบสั่งผิด schema (เช่น tag 1.4, replicas > 6, key ผิดของ Traefik) | แก้ค่าตามตำแหน่งที่ข้อความบอก (LAB 8) |
| `Error: invalid registry "http://localhost:5000"` | Helm 4 รับแค่ชื่อโฮสต์ | `helm registry login localhost:5000 ...` |
| `basic credential not found` | ยังไม่ login หรือ logout แล้ว | `helm registry login` (LAB 11) |
| `helm pull ... -d pulled`: no such file or directory | โฟลเดอร์ปลายทางยังไม่มี | `mkdir -p pulled` ก่อน |
| `plugin source does not support verification` | Helm 4 ตรวจที่มาของ plugin | ใส่ `--verify=false` เฉพาะ plugin ที่เชื่อถือได้ และ pin `--version` |
| `tree: command not found` | image ไม่มี `tree` | `find <dir> -type f \| sort` |
| `error: you may only specify a single resource type` | `kubectl get job,pod -w` | watch ทีละชนิด เช่น `kubectl get pod -w` |
| `KeyError: 'managedFields'` | `kubectl get -o json` ซ่อน managedFields | เพิ่ม `--show-managed-fields` |
| `kubectl top` ใช้ไม่ได้หลังติดตั้ง metrics-server ด้วย chart | APIService ยัง `False (FailedDiscoveryCheck)` ช่วงแรก | รอ 20–45 วินาที แล้วดู `kubectl get apiservice v1beta1.metrics.k8s.io` |
| สาขา dev ติดตั้งใหม่แล้ว `failed post-install ... som-seed` หรือ `som-web not ready ... Available: 0/1` | ตู้เซฟ (PVC) เดิมใช้รหัสเก่า | `helm upgrade` ด้วยรหัสเดิม หรือ `kubectl delete ns som-dev` แล้วเริ่มใหม่ (ข้อมูลหาย) |
| หลังร้าน `admin.localhost` ได้ 404 | เผลอลบ Middleware `redirect-https` ที่ `som-admin` ใช้ | `kubectl apply` ไฟล์ ingress ของบท 012/013 ที่มี Middleware นี้กลับ หรือย้อนจากสำเนาที่ backup ไว้ |
| เปิด `http://dev.shop.localhost:30080` ใน browser ไม่ได้ | browser ไม่แปลง `*.localhost` | ใช้ Chrome/Edge หรือทางสำรองของบทที่ 12 (แก้ไฟล์ hosts / `curl` ใน k8s-lab) |
| `./hit.sh: Permission denied` | สิทธิ์ execute หายตอนคัดลอก | `bash hit.sh ...` หรือ `chmod +x hit.sh labs/lab06-debug/make-broken.sh` |

## Checklist ส่งงาน

- [ ] ภาพ `helm version` (v4.3.0) และ `helm repo list` 3 แคตตาล็อก (LAB 0–1)
- [ ] ภาพ `helm get metadata` ที่มี `APPLY_METHOD: server-side apply` (LAB 2)
- [ ] ภาพกับดัก upgrade ของ LAB 3 (`replicaCount: 1` อย่างเดียว + `404`) และหลังแก้ด้วย `--reuse-values`
- [ ] ภาพ `helm history hello` ที่เห็น `failed` + `Rollback to N` จาก `--rollback-on-failure` และ `Rollback to 8` จาก rollback ไม่ใส่เลข (LAB 4)
- [ ] ภาพ error 4 แบบของ LAB 6 และผลต่างของ `--dry-run=server` กับ `kubectl apply --dry-run=server`
- [ ] ภาพ schema ปฏิเสธ `web.replicas=9` (LAB 8)
- [ ] ภาพ `helm test som -n som-dev --logs` (Succeeded) และผลถอด release Secret (ตัดรหัสให้สั้น) (LAB 9)
- [ ] ภาพ `helm list -A` ที่มี traefik 41.6.1 และ metrics-server 3.14.0 + ผล `hit.sh` ช่วงย้าย Traefik (LAB 10)
- [ ] ภาพ `Pushed: ... Digest: sha256:...` และ install จาก `oci://` (LAB 11)
- [ ] LAB 12: dev 1 คำสั่ง + test, adopt rev 1 failed → rev 2 deployed + ออเดอร์เดิม, upgrade 1.8 `err=0`, `helm rollback som <เลข>` `err=0`, `helm history`, PVC ค้างหลัง uninstall
- [ ] ภาพหน้าจอ browser ของตัวเอง: สาขา dev (`http://dev.shop.localhost:30080`) และสาขา prod 1.8 (`https://shop.localhost:30081`)
- [ ] ตอบคำถามท้าย LAB 12

## เก็บกวาดหลังจบบท

| สิ่งที่สร้างในบทนี้ | เก็บไว้บทถัดไป? | ลบด้วย |
|---|---|---|
| namespace `helm-demo`, `first`, `som-dev`, `oci-demo` | ไม่ (ลบแล้วใน LAB 4, 6, 12, 11) | `kubectl delete ns <ชื่อ>` |
| release `traefik` (ns `traefik`), `metrics-server` (ns `kube-system`) | **เก็บ** (ประตูและมิเตอร์ของท่าเรือ) | `helm uninstall traefik -n traefik` / `helm uninstall metrics-server -n kube-system` (ร้านจะไม่มีประตู/HPA) |
| release `som` (ns `som-shop`) = ร้านจริง | **เก็บ** | `helm uninstall som -n som-shop` (เหลือ PVC, `som-admin`, Middleware ของบท 012 — ห้ามทำถ้ายังเรียนบทถัดไป) |
| แคตตาล็อก podinfo, traefik, metrics-server | เก็บได้ | `helm repo remove podinfo traefik metrics-server` |
| image `som-shop-web:1.8` | เก็บ | — |
| container `som-registry`, ไฟล์ `.tgz`, `auth/`, `pulled/` | ไม่ (ลบแล้วใน LAB 11) | `docker rm -f som-registry` |
| โฟลเดอร์ที่ LAB สร้าง (`labs/lab01-catalog/traefik`, `labs/lab05-first/mychart`, `labs/lab06-debug/broken-*`) | ไม่ | `rm -rf` (ไม่เข้า git อยู่แล้ว) |
| plugin `diff`, `Chart.lock`/`charts/` ของ harbor-addons (LAB เสริม) | ไม่ (ลบแล้ว) | `helm plugin uninstall diff` |

ปิด container เมื่อเลิกใช้ 🖥️ `docker stop k8s-lab` (คลัสเตอร์ release และร้านรอด restart)

---

> **หมายเหตุเกี่ยวกับภาพประกอบ:** ภาพประกอบ LAB (ยกเว้นภาพในโฟลเดอร์ [`images/screenshots/`](images/screenshots/) ซึ่งเป็นภาพหน้าจอจริงจากการทดลอง) สร้างขึ้นด้วยปัญญาประดิษฐ์สำหรับการสร้างภาพเพื่อใช้ประกอบการเรียนการสอน ชุดคำสั่งสร้างภาพอยู่ใน [`images/imagegen-prompts.md`](images/imagegen-prompts.md) ภาพใช้อุปมาเชิงเปรียบเทียบ ตัวเลขในภาพ (เช่น เลข revision ชื่อ Pod และจำนวนวินาที) เป็นค่าตัวอย่าง ผู้เรียนควรใช้ผลลัพธ์จากเครื่องตัวเองและเนื้อหาในเอกสารนี้เป็นหลัก ภาพหน้าจอจริงถ่ายจาก browser ที่เปิด URL เดียวกับที่นักศึกษาใช้ บนเครื่องทดลองที่จำกัด 4 CPU ผลลัพธ์คำสั่งทั้งหมดมาจากการทดลองจริง (helm v4.3.0, Kubernetes v1.37.0, kubectl v1.37.1, Traefik chart 41.6.1, metrics-server chart 3.14.0) รหัสผ่านทุกตัว (`passwd`, `meow1234`, `purr5678`, `meow-admin-123`, `meow-registry-123`) เป็นค่าตัวอย่างเพื่อการเรียนเท่านั้น
