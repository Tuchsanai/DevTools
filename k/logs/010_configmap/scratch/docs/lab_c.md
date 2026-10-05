
---

## LAB 10: LAB สุดท้าย: ร้านน้องส้มเปลี่ยนป้ายไม่ต้อง build ใหม่

{{FIG:L11}}

**เป้าหมาย:** เริ่มจากร้านแบบท้ายบทที่ 9 (ค่าร้านเขียนตรงใน env) แล้วย้าย **ชื่อร้าน ธีม และโปรโมชัน** ไปไว้ใน ConfigMap `som-web-config` (ใช้ผ่าน `envFrom`) และย้าย **ประกาศหน้าร้าน** ไปไว้ใน ConfigMap `som-announcement` (mount เป็นโฟลเดอร์ `/etc/som`) จากนั้นพิสูจน์ว่า

1. เปลี่ยนป้ายร้านได้โดย **ไม่ build image ใหม่** (`som-shop-web:1.5` ตัวเดียวตลอด LAB) แต่ค่าจาก env ต้อง `rollout restart`
2. ประกาศหน้าร้านเปลี่ยนเองภายในราว 1 นาที **โดย Pod ไม่ restart**
3. ใช้ ConfigMap ชื่อใหม่แบบ `immutable` แล้วย้อนรุ่นด้วย `rollout undo` ได้
4. ออเดอร์ในฐานข้อมูล (StatefulSet + PVC จากบทที่ 9) ไม่หายตลอดทุกขั้น
5. และเห็นปัญหาที่ยังเหลือ: คนที่อ่าน Deployment ได้ยังเห็นรหัสผ่านฐานข้อมูล

**ไฟล์:** `som-shop-v6/` (ดู[โครงสร้างไฟล์ LAB](#โครงสร้างไฟล์-lab)) ต้องทำ LAB 0 แล้ว (มี `som-shop-web:1.5` และ `postgres:17.11-alpine` บนทุก Node) และไม่มี Service อื่นจอง NodePort 30080

### 10.1 ภาพรวมและไฟล์

| ส่วน | ชนิด | รายละเอียด |
|---|---|---|
| `som-shop` | Namespace | `pod-security.kubernetes.io/warn: restricted` (เหมือนบทที่ 4–9) |
| `som-db` + `som-db-0` | headless Service + StatefulSet | postgres 17.11 พร้อม PVC `data-som-db-0` (เหมือนบทที่ 9 ไม่เปลี่ยน) |
| `som-web` | Deployment 3 replicas + Service NodePort 30080 | `som-shop-web:1.5` + init container `wait-for-db`, `db-seed` |
| `som-web-config` | ConfigMap (ใหม่) | `SHOP_NAME`, `SHOP_EYEBROW`, `SHOP_FOOTER`, `APP_THEME`, `SHOP_PROMO` → `envFrom` |
| `som-announcement` | ConfigMap (ใหม่) | `announcement.txt` → volume ที่ `/etc/som` (ไม่ใช้ subPath) |

`k8s/15-config.yaml` (ตัดคอมเมนต์บางส่วน)

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: som-web-config
  namespace: som-shop
data:
  SHOP_NAME: "ร้านอาหารแมวน้องส้ม"
  SHOP_EYEBROW: "⚓ ท่าเรือ Kubernetes · ConfigMap"
  # ห้ามใส่ $(POD_NAMESPACE) ในค่าของ ConfigMap — envFrom ไม่แทนค่าให้ (ดูขั้น B เสริม)
  SHOP_FOOTER: "Next.js + PostgreSQL · Kubernetes LAB 010 · ConfigMap som-web-config"
  APP_THEME: "harbor"              # harbor (น้ำเงิน) หรือ sunset (ส้ม) — ทับค่าเริ่มใน image ได้
  SHOP_PROMO: ""                   # ว่าง = ไม่แสดงแถบโปรโมชัน
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: som-announcement
  namespace: som-shop
data:
  announcement.txt: |
    วันนี้ปลาทูสดมาก 🐟
```

ความต่างของ container `web` ระหว่าง `k8s-start/20-web.yaml` (ขั้น A) กับ `k8s/20-web.yaml` (ขั้น B เป็นต้นไป)

| | `k8s-start/20-web.yaml` | `k8s/20-web.yaml` |
|---|---|---|
| ชื่อร้าน / footer | `env: SHOP_NAME`, `SHOP_FOOTER` เขียนตรงในไฟล์ | `envFrom: configMapRef som-web-config` |
| ประกาศหน้าร้าน | ไม่มี | volume `som-announcement` mount ที่ `/etc/som` (`readOnly: true`) |
| env ที่เหลือ | `POD_NAMESPACE`, `DATABASE_URL`, `PORT`, `HOSTNAME` | เหมือนกัน (`DATABASE_URL` ยังมีรหัสผ่าน — จงใจ) |
| `kubernetes.io/change-cause` | `1.5 เริ่มบท 010 (ค่าร้านยังเขียนใน env)` | `1.5 ป้ายร้านจาก ConfigMap` |

ส่วนที่เพิ่มใน `k8s/20-web.yaml` (ตัดมาเฉพาะที่เกี่ยวข้อง)

```yaml
      volumes:
        # กระดานเล็กในบูธ: ทุก key ของ som-announcement = 1 ไฟล์ — kubelet อัปเดตให้เองราว 1 นาทีหลังแก้
        - name: announcement
          configMap:
            name: som-announcement
      containers:
        - name: web
          image: som-shop-web:1.5    # image เดิมทุกขั้น — เปลี่ยนป้ายร้านโดยไม่ build ใหม่
          envFrom:
            - configMapRef:
                name: som-web-config
          volumeMounts:
            - name: announcement
              mountPath: /etc/som        # ได้ไฟล์ /etc/som/announcement.txt (แอปอ่านใหม่ทุก request)
              readOnly: true
```

คำสั่งทั้งหมดของ LAB 10 รัน 🐧 ใน SSH session ของ k8s-lab ที่โฟลเดอร์ `som-shop-v6` (ใช้ `curl -s localhost:30080/...` ใน k8s-lab ได้เพราะ NodePort ของ kind ถูก map ไว้ที่ k8s-lab) และเปิดร้านใน 🌐 browser บนเครื่องนักศึกษาที่ **`http://localhost:30080`** ได้ทุกขั้น

### 10.2 ขั้น A: เริ่มจากร้านแบบบท 009

{{FIG:L12}}

```bash
cd /workspace/010_kubernetes_configmap/02_LAB/som-shop-v6
ls; kubectl apply -f k8s-start/
kubectl -n som-shop rollout status sts/som-db --timeout=180s && time kubectl -n som-shop rollout status deploy/som-web --timeout=240s
kubectl -n som-shop get pod,svc,pvc,cm
```

```text
app
extra
hit.sh
k8s
k8s-start
rbac
wait-announcement.sh
namespace/som-shop created
service/som-db created
statefulset.apps/som-db created
deployment.apps/som-web created
service/som-web created
Waiting for 1 pods to be ready...
partitioned roll out complete: 1 new pods have been updated...
Waiting for deployment "som-web" rollout to finish: 0 of 3 updated replicas are available...
...
deployment "som-web" successfully rolled out

real	0m5.436s
...
NAME                           READY   STATUS    RESTARTS   AGE
pod/som-db-0                   1/1     Running   0          14s
pod/som-web-7df8dc86bb-fj6st   1/1     Running   0          14s
pod/som-web-7df8dc86bb-h6crw   1/1     Running   0          14s
pod/som-web-7df8dc86bb-prwjh   1/1     Running   0          14s

NAME              TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)        AGE
service/som-db    ClusterIP   None            <none>        5432/TCP       14s
service/som-web   NodePort    10.96.135.175   <none>        80:30080/TCP   14s

NAME                                  STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
persistentvolumeclaim/data-som-db-0   Bound    pvc-8def5cb1-0e40-421b-880d-47f74296a138   1Gi        RWO            standard       <unset>                 14s

NAME                         DATA   AGE
configmap/kube-root-ca.crt   1      14s
```

ตอนนี้ namespace มีแค่ `kube-root-ca.crt` ยังไม่มี ConfigMap ของร้าน สั่งออเดอร์ 3 รายการแล้วดูค่าที่ร้านเห็น

```bash
curl -s localhost:30080/api/stats; echo
for i in 1 2 3; do curl -s -XPOST -H 'content-type: application/json' -d '{"product_id":1,"qty":1}' localhost:30080/api/orders; echo; done
curl -s localhost:30080/api/stats; echo; curl -s localhost:30080/api/shop; echo; curl -s localhost:30080/api/announcement
```

```text
som-web-7df8dc86bb-prwjh 1.5 orders=0 products=6

{"ok":true,"order_id":1,"product":{"id":1,"name_th":"อาหารเม็ดสูตรปลาทูน่า 1.5 กก.","stock":19}}
{"ok":true,"order_id":2,"product":{"id":1,"name_th":"อาหารเม็ดสูตรปลาทูน่า 1.5 กก.","stock":18}}
{"ok":true,"order_id":3,"product":{"id":1,"name_th":"อาหารเม็ดสูตรปลาทูน่า 1.5 กก.","stock":17}}
som-web-7df8dc86bb-h6crw 1.5 orders=3 products=6

{"pod":"som-web-7df8dc86bb-fj6st","version":"1.5","shopName":"ร้านอาหารแมวน้องส้ม","theme":"harbor","promo":"","eyebrow":null,"footer":"Next.js + PostgreSQL · Kubernetes LAB 010 · namespace som-shop"}
som-web-7df8dc86bb-prwjh 1.5 (ไม่มีประกาศ)
```

ดูหน้าเว็บจาก HTML (หรือเปิด 🌐 `http://localhost:30080`)

```bash
curl -s localhost:30080/ | grep -o '<title>[^<]*</title>'; curl -s localhost:30080/ | grep -o 'class="theme-[a-z]*"' | head -1; curl -s localhost:30080/ | grep -c 'class="promo"'; curl -s localhost:30080/ | grep -c 'class="announcement"'
curl -s localhost:30080/ | grep -o 'ท่าเรือ Kubernetes[^<]*' | head -1
./hit.sh http://localhost:30080/api/whoami 30
kubectl -n som-shop rollout history deploy/som-web
```

```text
<title>ร้านอาหารแมวน้องส้ม</title>
class="theme-harbor"
0
0
ท่าเรือ Kubernetes · ReplicaSet + Service
จำนวน  Pod  เวอร์ชัน
     13 som-web-7df8dc86bb-fj6st 1.5
     10 som-web-7df8dc86bb-h6crw 1.5
      7 som-web-7df8dc86bb-prwjh 1.5
ok=30 err=0 (ใช้เวลา 3.3 วินาที)
deployment.apps/som-web 
REVISION  CHANGE-CAUSE
1         1.5 เริ่มบท 010 (ค่าร้านยังเขียนใน env)
```

- แอป 1.5 ทำงานเหมือนบทที่ 9: ธีม harbor (ค่าเริ่มใน image) ไม่มีแถบโปรโมชัน (`SHOP_PROMO` ไม่ได้ตั้ง) ไม่มีแถบประกาศ (`/api/announcement` ตอบ `(ไม่มีประกาศ)` เพราะยังไม่มีไฟล์ `/etc/som/announcement.txt` แต่หน้าเว็บไม่พัง)
- `eyebrow` เป็น `null` หัวเว็บจึงใช้ข้อความตั้งต้นของแอป `⚓ ท่าเรือ Kubernetes · ReplicaSet + Service`
- footer มี `namespace som-shop` เพราะใน `k8s-start/20-web.yaml` ค่านี้อยู่ใน `env` ที่อ้าง `$(POD_NAMESPACE)` จึงถูกแทนค่า
- ออเดอร์ **3** รายการ (จำตัวเลขนี้ไว้ตรวจทุกขั้น)

### 10.3 ขั้น B: ย้ายป้ายร้านไปไว้ใน ConfigMap

{{FIG:L13}}

apply ConfigMap ทั้งสองแผ่นพร้อม Deployment รุ่นที่ใช้ `envFrom` + volume

```bash
kubectl apply -f k8s/15-config.yaml -f k8s/20-web.yaml && kubectl -n som-shop rollout status deploy/som-web --timeout=240s
kubectl -n som-shop get cm; curl -s localhost:30080/api/shop; echo; curl -s localhost:30080/api/announcement; curl -s localhost:30080/api/stats; echo
```

```text
configmap/som-web-config created
configmap/som-announcement created
deployment.apps/som-web configured
service/som-web unchanged
Waiting for deployment "som-web" rollout to finish: 1 out of 3 new replicas have been updated...
...
Waiting for deployment "som-web" rollout to finish: 1 old replicas are pending termination...
deployment "som-web" successfully rolled out
NAME               DATA   AGE
kube-root-ca.crt   1      60s
som-announcement   1      27s
som-web-config     5      27s
{"pod":"som-web-8655557674-tpgg6","version":"1.5","shopName":"ร้านอาหารแมวน้องส้ม","theme":"harbor","promo":"","eyebrow":"⚓ ท่าเรือ Kubernetes · ConfigMap","footer":"Next.js + PostgreSQL · Kubernetes LAB 010 · ConfigMap som-web-config"}
som-web-8655557674-jj7sr 1.5 วันนี้ปลาทูสดมาก 🐟
som-web-8655557674-tpgg6 1.5 orders=3 products=6
```

ดูหน้าเว็บ ไฟล์ใน Pod และ env

```bash
curl -s localhost:30080/ | grep -o '<title>[^<]*</title>'; curl -s localhost:30080/ | grep -o 'class="theme-[a-z]*"' | head -1; curl -s localhost:30080/ | grep -o 'class="announcement">[^<]*<!-- -->[^<]*' | head -1; curl -s localhost:30080/ | grep -c 'class="promo"'
kubectl -n som-shop exec deploy/som-web -c web -- ls -la /etc/som; kubectl -n som-shop exec deploy/som-web -c web -- printenv SHOP_NAME APP_THEME SHOP_FOOTER
kubectl -n som-shop rollout history deploy/som-web
```

```text
<title>ร้านอาหารแมวน้องส้ม</title>
class="theme-harbor"
class="announcement">📢 <!-- -->วันนี้ปลาทูสดมาก 🐟
0
total 12
drwxrwxrwx    3 root     root          4096 Oct  5 10:10 .
drwxr-xr-x    1 root     root          4096 Oct  5 10:10 ..
drwxr-xr-x    2 root     root          4096 Oct  5 10:10 ..2026_10_05_10_10_45.372685087
lrwxrwxrwx    1 root     root            31 Oct  5 10:10 ..data -> ..2026_10_05_10_10_45.372685087
lrwxrwxrwx    1 root     root            23 Oct  5 10:10 announcement.txt -> ..data/announcement.txt
ร้านอาหารแมวน้องส้ม
harbor
Next.js + PostgreSQL · Kubernetes LAB 010 · ConfigMap som-web-config
deployment.apps/som-web 
REVISION  CHANGE-CAUSE
1         1.5 เริ่มบท 010 (ค่าร้านยังเขียนใน env)
2         1.5 ป้ายร้านจาก ConfigMap
```

- `som-web-config` มี 5 key และ web ได้ทั้ง 5 เป็น env ผ่าน `envFrom` บรรทัดเดียว (`eyebrow` และ `footer` เป็นข้อความจาก ConfigMap แล้ว)
- `/etc/som/announcement.txt` เป็น symlink ผ่าน `..data` แบบ LAB 5 หน้าเว็บมีแถบ `📢 วันนี้ปลาทูสดมาก 🐟` (`<!-- -->` เป็นตัวคั่นที่ React แทรกใน HTML)
- ออเดอร์ยัง **3** — เปลี่ยน Deployment ไม่กระทบฐานข้อมูล

### 10.4 ขั้น B เสริม: $(POD_NAMESPACE) ในค่าของ ConfigMap

{{FIG:L16}}

ถ้าย้าย footer แบบเดิม (`... namespace $(POD_NAMESPACE)`) เข้าไปใน ConfigMap ตรง ๆ จะเกิดอะไร

```bash
kubectl -n som-shop patch cm som-web-config --type merge -p '{"data":{"SHOP_FOOTER":"LAB 010 · namespace $(POD_NAMESPACE)"}}' && kubectl -n som-shop rollout restart deploy/som-web && kubectl -n som-shop rollout status deploy/som-web --timeout=240s >/dev/null && sleep 8 && curl -s localhost:30080/api/shop; echo
```

```text
configmap/som-web-config patched
deployment.apps/som-web restarted
{"pod":"som-web-f686c9c85-4k8dt","version":"1.5","shopName":"ร้านอาหารแมวน้องส้ม","theme":"harbor","promo":"","eyebrow":"⚓ ท่าเรือ Kubernetes · ConfigMap","footer":"LAB 010 · namespace $(POD_NAMESPACE)"}
```

footer เป็นข้อความดิบ `$(POD_NAMESPACE)` (เหมือน LAB 3) ทางแก้คือตั้งค่านี้ใน `env` ของ Deployment ซึ่งแทนค่าได้และ **ชนะ envFrom**

```bash
kubectl -n som-shop set env deploy/som-web SHOP_FOOTER='LAB 010 · namespace $(POD_NAMESPACE)' && kubectl -n som-shop rollout status deploy/som-web --timeout=240s >/dev/null && sleep 8 && curl -s localhost:30080/api/shop; echo
kubectl -n som-shop get deploy som-web -o jsonpath='{.spec.template.spec.containers[0].env[*].name}'; echo
```

```text
deployment.apps/som-web env updated
{"pod":"som-web-78d9787b8c-bnvjm","version":"1.5","shopName":"ร้านอาหารแมวน้องส้ม","theme":"harbor","promo":"","eyebrow":"⚓ ท่าเรือ Kubernetes · ConfigMap","footer":"LAB 010 · namespace som-shop"}
POD_NAMESPACE DATABASE_URL PORT HOSTNAME SHOP_FOOTER
```

คืนค่าเดิม: apply ConfigMap จากไฟล์ และ **ลบ env `SHOP_FOOTER` ออกเอง** (`kubectl set env` ไม่ถูกบันทึกใน annotation last-applied การ `kubectl apply -f k8s/20-web.yaml` ภายหลังจึงไม่ลบ env ที่ set ไว้ ต้องใช้ `SHOP_FOOTER-`)

```bash
kubectl apply -f k8s/15-config.yaml && kubectl -n som-shop set env deploy/som-web SHOP_FOOTER- && kubectl -n som-shop rollout status deploy/som-web --timeout=240s >/dev/null && sleep 8 && curl -s localhost:30080/api/shop; echo
kubectl -n som-shop rollout history deploy/som-web; curl -s localhost:30080/api/stats; echo
```

```text
configmap/som-web-config configured
configmap/som-announcement unchanged
deployment.apps/som-web env updated
{"pod":"som-web-f686c9c85-55c2q","version":"1.5","shopName":"ร้านอาหารแมวน้องส้ม","theme":"harbor","promo":"","eyebrow":"⚓ ท่าเรือ Kubernetes · ConfigMap","footer":"Next.js + PostgreSQL · Kubernetes LAB 010 · ConfigMap som-web-config"}
deployment.apps/som-web 
REVISION  CHANGE-CAUSE
1         1.5 เริ่มบท 010 (ค่าร้านยังเขียนใน env)
2         1.5 ป้ายร้านจาก ConfigMap
4         1.5 ป้ายร้านจาก ConfigMap
5         1.5 ป้ายร้านจาก ConfigMap

som-web-f686c9c85-pd4nz 1.5 orders=3 products=6
```

สังเกต history: `rollout restart` และ `set env` **ไม่เปลี่ยน CHANGE-CAUSE** ทุก revision จึงซ้ำข้อความ `1.5 ป้ายร้านจาก ConfigMap` และ REVISION 3 หายไปเพราะ template หลังเอา `SHOP_FOOTER` ออกเหมือนกับ revision 3 (restartedAt เดิม) Deployment จึงนำ ReplicaSet เดิมกลับมาใช้เป็น revision 5 (ชื่อ Pod `som-web-f686c9c85-...` ชุดเดียวกับหลัง restart) ออเดอร์ยัง **3**

### 10.5 ขั้น C1: แก้ ConfigMap แล้ว Pod เดิมยังไม่เปลี่ยน

{{FIG:L14}}

`extra/15-config-promo.yaml` ใช้ชื่อ `som-web-config` เดิม แต่เปลี่ยนเป็นชื่อสาขา ธีม sunset และเพิ่มโปรโมชัน

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: som-web-config
  namespace: som-shop
data:
  SHOP_NAME: "ร้านน้องส้ม สาขาท่าเรือ"
  SHOP_EYEBROW: "⚓ ท่าเรือ Kubernetes · ConfigMap"
  SHOP_FOOTER: "Next.js + PostgreSQL · Kubernetes LAB 010 · ConfigMap som-web-config"
  APP_THEME: "sunset"
  SHOP_PROMO: "🎉 โปรวันนี้: ขนมปลาทูน่าลด 20%"
```

```bash
kubectl apply -f extra/15-config-promo.yaml; date +%T; kubectl -n som-shop get cm som-web-config -o jsonpath="{.data.SHOP_NAME} / {.data.APP_THEME} / {.data.SHOP_PROMO}"; echo
```

```text
configmap/som-web-config configured
17:12:45
ร้านน้องส้ม สาขาท่าเรือ / sunset / 🎉 โปรวันนี้: ขนมปลาทูน่าลด 20%
```

ConfigMap เปลี่ยนแล้ว **รอ 90 วินาที** แล้วถามทั้ง 3 Pod

```bash
date +%T; for i in 1 2 3; do curl -s localhost:30080/api/shop; echo; done; kubectl -n som-shop get pod -l app=som-web
```

```text
17:14:16
{"pod":"som-web-f686c9c85-pd4nz","version":"1.5","shopName":"ร้านอาหารแมวน้องส้ม","theme":"harbor","promo":"","eyebrow":"⚓ ท่าเรือ Kubernetes · ConfigMap","footer":"Next.js + PostgreSQL · Kubernetes LAB 010 · ConfigMap som-web-config"}
{"pod":"som-web-f686c9c85-55c2q","version":"1.5","shopName":"ร้านอาหารแมวน้องส้ม","theme":"harbor","promo":"","eyebrow":"⚓ ท่าเรือ Kubernetes · ConfigMap","footer":"Next.js + PostgreSQL · Kubernetes LAB 010 · ConfigMap som-web-config"}
{"pod":"som-web-f686c9c85-nzqxd","version":"1.5","shopName":"ร้านอาหารแมวน้องส้ม","theme":"harbor","promo":"","eyebrow":"⚓ ท่าเรือ Kubernetes · ConfigMap","footer":"Next.js + PostgreSQL · Kubernetes LAB 010 · ConfigMap som-web-config"}
NAME                      READY   STATUS    RESTARTS   AGE
som-web-f686c9c85-55c2q   1/1     Running   0          112s
som-web-f686c9c85-nzqxd   1/1     Running   0          2m4s
som-web-f686c9c85-pd4nz   1/1     Running   0          118s
```

ทั้ง 3 Pod ยังเป็น `ร้านอาหารแมวน้องส้ม` / `harbor` / promo ว่าง และ `RESTARTS 0` เพราะค่าเหล่านี้มาจาก **env ที่อ่านครั้งเดียวตอน container เริ่ม** (ป้ายติดอก) ไม่ว่าจะรอนานเท่าไรก็ไม่เปลี่ยน

### 10.6 ขั้น C2: rollout restart แล้วป้ายเปลี่ยน

{{FIG:L15}}

```bash
kubectl -n som-shop rollout restart deploy/som-web && kubectl -n som-shop rollout status deploy/som-web --timeout=240s
```

```text
deployment.apps/som-web restarted
Waiting for deployment "som-web" rollout to finish: 1 out of 3 new replicas have been updated...
...
Waiting for deployment "som-web" rollout to finish: 1 old replicas are pending termination...
deployment "som-web" successfully rolled out
```

rollout ใช้ราว 25–35 วินาที (3 Pod, `maxSurge: 1`, `minReadySeconds: 3`) หลัง `successfully rolled out` รอราว 8 วินาทีก่อน curl เพราะ Pod เก่ายังตอบอยู่ในช่วง preStop 5 วินาที

```bash
curl -s localhost:30080/api/shop; echo
curl -s localhost:30080/ | grep -o '<title>[^<]*</title>'; curl -s localhost:30080/ | grep -o 'class="theme-[a-z]*"' | head -1; curl -s localhost:30080/ | grep -o 'class="promo">[^<]*'; curl -s localhost:30080/api/stats; echo
./hit.sh http://localhost:30080/api/shop 12 | head -6
```

```text
{"pod":"som-web-b97c66d9c-tb2f7","version":"1.5","shopName":"ร้านน้องส้ม สาขาท่าเรือ","theme":"sunset","promo":"🎉 โปรวันนี้: ขนมปลาทูน่าลด 20%","eyebrow":"⚓ ท่าเรือ Kubernetes · ConfigMap","footer":"Next.js + PostgreSQL · Kubernetes LAB 010 · ConfigMap som-web-config"}
<title>ร้านน้องส้ม สาขาท่าเรือ</title>
class="theme-sunset"
class="promo">🎉 โปรวันนี้: ขนมปลาทูน่าลด 20%
som-web-b97c66d9c-tb2f7 1.5 orders=3 products=6
จำนวน  Pod  เวอร์ชัน
      5 {"pod":"som-web-b97c66d9c-86592","version":"1.5","shopName":"ร้านน้องส้ม สาขาท่าเรือ","theme":"sunset","promo":"🎉 โปรวันนี้: ขนมปลาทูน่าลด 20%","eyebrow":"⚓ ท่าเรือ Kubernetes · ConfigMap","footer":"Next.js + PostgreSQL · Kubernetes LAB 010 · ConfigMap som-web-config"}
      4 {"pod":"som-web-b97c66d9c-tb2f7","version":"1.5","shopName":"ร้านน้องส้ม สาขาท่าเรือ","theme":"sunset","promo":"🎉 โปรวันนี้: ขนมปลาทูน่าลด 20%","eyebrow":"⚓ ท่าเรือ Kubernetes · ConfigMap","footer":"Next.js + PostgreSQL · Kubernetes LAB 010 · ConfigMap som-web-config"}
      3 {"pod":"som-web-b97c66d9c-xx945","version":"1.5","shopName":"ร้านน้องส้ม สาขาท่าเรือ","theme":"sunset","promo":"🎉 โปรวันนี้: ขนมปลาทูน่าลด 20%","eyebrow":"⚓ ท่าเรือ Kubernetes · ConfigMap","footer":"Next.js + PostgreSQL · Kubernetes LAB 010 · ConfigMap som-web-config"}
ok=12 err=0 (ใช้เวลา 1.3 วินาที)
```

- ทั้ง 3 Pod ใหม่ได้ชื่อร้าน `ร้านน้องส้ม สาขาท่าเรือ` ธีม sunset และแถบโปรโมชัน ทั้งชื่อในแท็บ browser (`<title>`) ก็เปลี่ยนตาม
- image ยังเป็น `som-shop-web:1.5` ตัวเดิม **ไม่ได้ build ใหม่เลย** และออเดอร์ยัง **3**

### 10.7 ขั้น D: ประกาศหน้าร้านเปลี่ยนเองโดยไม่ restart

{{FIG:L17}}

ประกาศมาจากไฟล์ใน volume และแอป 1.5 อ่านไฟล์ใหม่ **ทุก request** จึงไม่ต้อง restart จดชื่อ Pod และ AGE ไว้ก่อน

```bash
kubectl -n som-shop get pod -l app=som-web; curl -s localhost:30080/api/announcement
```

```text
NAME                      READY   STATUS    RESTARTS   AGE
som-web-b97c66d9c-86592   1/1     Running   0          27s
som-web-b97c66d9c-tb2f7   1/1     Running   0          34s
som-web-b97c66d9c-xx945   1/1     Running   0          21s
som-web-b97c66d9c-86592 1.5 วันนี้ปลาทูสดมาก 🐟
```

{{FIG:L18}}

apply ประกาศใหม่ (`extra/16-announcement-1800.yaml` = `ปิดร้านเร็ว 18:00 น. ⛵`) แล้วให้ `wait-announcement.sh` จับเวลา สคริปต์เรียก `/api/announcement` ชุดละ 12 ครั้งทุก 2 วินาที บอกเวลาที่ Pod แรกเห็นคำว่า `18:00` และเวลาที่ครบ 12/12 (ทุก Pod)

```bash
kubectl apply -f extra/16-announcement-1800.yaml && ./wait-announcement.sh 18:00
kubectl -n som-shop get pod -l app=som-web; curl -s localhost:30080/ | grep -o 'class="announcement">[^<]*<!-- -->[^<]*'
```

```text
configmap/som-announcement configured
เริ่ม 17:14:51 รอคำว่า "18:00" จาก http://localhost:30080/api/announcement
  Pod แรกเห็นประกาศใหม่หลัง 37 วินาที: som-web-b97c66d9c-tb2f7 1.5 ปิดร้านเร็ว 18:00 น. ⛵
  ทุก Pod เห็นประกาศใหม่ (12/12) หลัง 48 วินาที
NAME                      READY   STATUS    RESTARTS   AGE
som-web-b97c66d9c-86592   1/1     Running   0          76s
som-web-b97c66d9c-tb2f7   1/1     Running   0          83s
som-web-b97c66d9c-xx945   1/1     Running   0          70s
class="announcement">📢 <!-- -->ปิดร้านเร็ว 18:00 น. ⛵
```

ชื่อ Pod เดิมทั้ง 3 ตัว `RESTARTS 0` และ AGE นับต่อเนื่อง (27s → 76s) แต่หน้าเว็บเปลี่ยนประกาศแล้ว

ลองอีกรอบด้วยการอัปเดตจากคำสั่ง (`create ... --dry-run=client -o yaml | kubectl apply -f -` แบบ LAB 1) แล้วกลับเป็นประกาศ 18:00

```bash
kubectl -n som-shop create configmap som-announcement --from-literal=announcement.txt='พรุ่งนี้เปิด 09:00 น. 🐟' --dry-run=client -o yaml | kubectl apply -f - && ./wait-announcement.sh 09:00
kubectl apply -f extra/16-announcement-1800.yaml && ./wait-announcement.sh 18:00; kubectl -n som-shop get pod -l app=som-web
```

```text
configmap/som-announcement configured
เริ่ม 17:15:46 รอคำว่า "09:00" จาก http://localhost:30080/api/announcement
  Pod แรกเห็นประกาศใหม่หลัง 63 วินาที: som-web-b97c66d9c-tb2f7 1.5 พรุ่งนี้เปิด 09:00 น. 🐟
  ทุก Pod เห็นประกาศใหม่ (12/12) หลัง 82 วินาที
configmap/som-announcement configured
เริ่ม 17:17:08 รอคำว่า "18:00" จาก http://localhost:30080/api/announcement
  Pod แรกเห็นประกาศใหม่หลัง 59 วินาที: som-web-b97c66d9c-tb2f7 1.5 ปิดร้านเร็ว 18:00 น. ⛵
  ทุก Pod เห็นประกาศใหม่ (12/12) หลัง 88 วินาที
NAME                      READY   STATUS    RESTARTS   AGE
som-web-b97c66d9c-86592   1/1     Running   0          4m13s
som-web-b97c66d9c-tb2f7   1/1     Running   0          4m20s
som-web-b97c66d9c-xx945   1/1     Running   0          4m7s
```

| รอบ | Pod แรกเห็น | ครบทุก Pod |
|---|---|---|
| 1 (`18:00`) | 37 วินาที | 48 วินาที |
| 2 (`09:00`) | 63 วินาที | 82 วินาที |
| 3 (`18:00`) | 59 วินาที | 88 วินาที |

ระหว่างช่วงนั้นการ refresh browser แต่ละครั้งอาจได้ Pod ที่ยังเป็นข้อความเก่า (Pod อยู่คนละ Node แต่ละ kubelet อัปเดตไม่พร้อมกัน) เผื่อเวลา **ราว 1–1.5 นาที** หลังแก้ประกาศ

### 10.8 ขั้น E: ConfigMap ชื่อใหม่แบบ immutable และ rollout undo

{{FIG:L19}}

`extra/17-config-v2.yaml` สร้าง `som-web-config-v2` แบบ `immutable: true` (ชื่อร้าน `ร้านน้องส้ม (v2)`) แล้วเปลี่ยนชื่อที่ `envFrom` อ้างด้วย JSON patch (ตำแหน่ง `/spec/template/spec/containers/0/envFrom/0/configMapRef/name`)

```bash
kubectl apply -f extra/17-config-v2.yaml; kubectl -n som-shop get cm
kubectl -n som-shop patch deploy som-web --type json -p '[{"op":"replace","path":"/spec/template/spec/containers/0/envFrom/0/configMapRef/name","value":"som-web-config-v2"}]' && kubectl -n som-shop rollout status deploy/som-web --timeout=240s >/dev/null
curl -s localhost:30080/api/shop; echo
```

```text
configmap/som-web-config-v2 created
NAME                DATA   AGE
kube-root-ca.crt    1      8m33s
som-announcement    1      8m
som-web-config      5      8m
som-web-config-v2   5      0s
deployment.apps/som-web patched
{"pod":"som-web-5dd747bf86-fzdzt","version":"1.5","shopName":"ร้านน้องส้ม (v2)","theme":"harbor","promo":"","eyebrow":"⚓ ท่าเรือ Kubernetes · ConfigMap v2 (immutable)","footer":"Next.js + PostgreSQL · Kubernetes LAB 010 · ConfigMap som-web-config-v2"}
```

ชื่อที่อ้างอยู่ใน Pod template เปลี่ยน → **rollout เอง** ไม่ต้องสั่ง restart ลองแก้ v2 และย้อนรุ่น

```bash
kubectl -n som-shop patch cm som-web-config-v2 --type merge -p '{"data":{"SHOP_NAME":"ร้านน้องส้ม (v2 แก้)"}}'
kubectl -n som-shop rollout undo deploy/som-web && kubectl -n som-shop rollout status deploy/som-web --timeout=240s >/dev/null
curl -s localhost:30080/api/shop; echo; curl -s localhost:30080/api/stats; echo; kubectl -n som-shop rollout history deploy/som-web
```

```text
The ConfigMap "som-web-config-v2" is invalid: data: Forbidden: field is immutable when `immutable` is set
Warning: resource deployments/som-web was previously managed with 'kubectl apply'. Rolling back will not update the kubectl.kubernetes.io/last-applied-configuration annotation, which may cause unexpected behavior on future 'kubectl apply' operations. Consider using 'kubectl apply' with your previous configuration file instead.
deployment.apps/som-web rolled back
{"pod":"som-web-b97c66d9c-s725k","version":"1.5","shopName":"ร้านน้องส้ม สาขาท่าเรือ","theme":"sunset","promo":"🎉 โปรวันนี้: ขนมปลาทูน่าลด 20%","eyebrow":"⚓ ท่าเรือ Kubernetes · ConfigMap","footer":"Next.js + PostgreSQL · Kubernetes LAB 010 · ConfigMap som-web-config"}
som-web-b97c66d9c-s725k 1.5 orders=3 products=6

deployment.apps/som-web 
REVISION  CHANGE-CAUSE
1         1.5 เริ่มบท 010 (ค่าร้านยังเขียนใน env)
2         1.5 ป้ายร้านจาก ConfigMap
4         1.5 ป้ายร้านจาก ConfigMap
5         1.5 ป้ายร้านจาก ConfigMap
7         1.5 ป้ายร้านจาก ConfigMap
8         1.5 ป้ายร้านจาก ConfigMap
```

- แก้ `som-web-config-v2` ไม่ได้ (`immutable`) ต้องสร้าง `-v3` แทน
- `rollout undo` กลับไป template ที่อ้าง `som-web-config` (ชื่อสาขาท่าเรือ/sunset) ทันที เพราะ ConfigMap เดิมยังอยู่ (ชื่อ Pod `som-web-b97c66d9c-...` = ReplicaSet เดิมของขั้น C2) Warning เรื่อง last-applied เป็นเรื่องปกติของ `undo` (บทที่ 7)
- ออเดอร์ยัง **3**

### 10.9 ขั้น F: ปัญหาที่เหลือ — รหัสผ่านยังเห็นได้

{{FIG:L20}}

`rbac/intern.yaml` สร้าง ServiceAccount `intern` ที่ได้สิทธิ์ `get, list, watch` เฉพาะ Pod, ConfigMap, Deployment และ StatefulSet ใน `som-shop` (แบบบทที่ 4)

```bash
kubectl apply -f rbac/intern.yaml
kubectl -n som-shop auth can-i get configmaps --as=system:serviceaccount:som-shop:intern; kubectl -n som-shop auth can-i get deployments --as=system:serviceaccount:som-shop:intern; kubectl -n som-shop auth can-i get secrets --as=system:serviceaccount:som-shop:intern; kubectl -n som-shop auth can-i patch configmaps --as=system:serviceaccount:som-shop:intern
kubectl -n som-shop get cm --as=system:serviceaccount:som-shop:intern
```

```text
serviceaccount/intern created
role.rbac.authorization.k8s.io/intern-read created
rolebinding.rbac.authorization.k8s.io/intern-read created
yes
yes
no
no
NAME                DATA   AGE
kube-root-ca.crt    1      9m34s
som-announcement    1      9m1s
som-web-config      5      9m1s
som-web-config-v2   5      61s
```

intern อ่าน ConfigMap และ Deployment ได้ แต่แก้ ConfigMap ไม่ได้ (และไม่มีสิทธิ์อ่านความลับแบบอื่นด้วย) ลองให้ intern ดู YAML ของ Deployment และ StatefulSet

```bash
kubectl -n som-shop get deploy som-web -o yaml --as=system:serviceaccount:som-shop:intern | grep -o 'som:[a-z0-9]*@' | sort | uniq -c
kubectl -n som-shop get deploy som-web -o yaml --as=system:serviceaccount:som-shop:intern | grep -n 'som:[a-z0-9]*@' | cut -c1-90
kubectl -n som-shop get sts som-db -o yaml --as=system:serviceaccount:som-shop:intern | grep -A1 -- '- name: POSTGRES_PASSWORD'
kubectl -n som-shop get pod som-db-0 -o yaml --as=system:serviceaccount:som-shop:intern | grep -A1 -- '- name: POSTGRES_PASSWORD'
kubectl -n som-shop patch cm som-web-config --as=system:serviceaccount:som-shop:intern --type merge -p '{"data":{"SHOP_NAME":"x"}}'
```

```text
      4 som:meow1234@
7:      {"apiVersion":"apps/v1","kind":"Deployment","metadata":{"annotations":{"kubernetes
45:          value: postgres://som:meow1234@som-db-0.som-db:5432/catshop
134:          value: postgres://som:meow1234@som-db-0.som-db:5432/catshop
        - name: POSTGRES_PASSWORD
          value: meow1234
    - name: POSTGRES_PASSWORD
      value: meow1234
Error from server (Forbidden): configmaps "som-web-config" is forbidden: User "system:serviceaccount:som-shop:intern" cannot patch resource "configmaps" in API group "" in the namespace "som-shop"
```

- intern เห็น `som:meow1234@` **4 ครั้ง** ใน Deployment: บรรทัด 45 และ 134 คือ `DATABASE_URL` ของ init container `db-seed` และ container `web` อีก 2 ครั้งอยู่ในบรรทัดเดียว (บรรทัด 7) ของ annotation `last-applied-configuration`
- เห็น `POSTGRES_PASSWORD: meow1234` ทั้งใน StatefulSet และ Pod `som-db-0`
- ถ้าย้ายรหัสไปไว้ใน ConfigMap ก็ไม่ช่วย เพราะ intern อ่าน ConfigMap ได้และ ConfigMap เป็นข้อความธรรมดา → **โจทย์ของบทที่ 11 Secret**

> รหัส `meow1234` เป็นค่าตัวอย่างของ LAB เท่านั้น ถ้าจะแปะภาพหน้าจอขั้นนี้ลงรายงาน ให้บังรหัสเป็น `som:●●●●@` เพื่อฝึกนิสัยที่ดี

### 10.10 คืนสภาพร้านและสั่งออเดอร์ที่ 4

ลบ ConfigMap v2 แล้ว apply โฟลเดอร์ `k8s/` ทั้งหมดเพื่อให้ ConfigMap และ Deployment กลับตรงกับไฟล์ (ชื่อร้านเดิม ธีม harbor ประกาศเดิม)

```bash
kubectl -n som-shop delete cm som-web-config-v2; kubectl apply -f k8s/ && kubectl -n som-shop rollout restart deploy/som-web && kubectl -n som-shop rollout status deploy/som-web --timeout=240s >/dev/null; echo rolled
curl -s -XPOST -H 'content-type: application/json' -d '{"product_id":2,"qty":1}' localhost:30080/api/orders; echo; curl -s localhost:30080/api/stats; echo; curl -s localhost:30080/api/shop; echo
```

```text
configmap "som-web-config-v2" deleted from som-shop namespace
namespace/som-shop unchanged
service/som-db unchanged
statefulset.apps/som-db configured
configmap/som-web-config configured
configmap/som-announcement configured
deployment.apps/som-web unchanged
service/som-web unchanged
deployment.apps/som-web restarted
rolled
{"ok":true,"order_id":4,"product":{"id":2,"name_th":"อาหารเม็ดลูกแมว สูตรนมแพะ 1 กก.","stock":14}}
som-web-77467d5bc4-w9zpt 1.5 orders=4 products=6

{"pod":"som-web-77467d5bc4-nvkw8","version":"1.5","shopName":"ร้านอาหารแมวน้องส้ม","theme":"harbor","promo":"","eyebrow":"⚓ ท่าเรือ Kubernetes · ConfigMap","footer":"Next.js + PostgreSQL · Kubernetes LAB 010 · ConfigMap som-web-config"}
```

- `deployment.apps/som-web unchanged` เพราะไฟล์เหมือนกับ template ปัจจุบัน แต่ ConfigMap `som-web-config` ถูกคืนเป็นค่าในไฟล์ (env ต้อง Pod ใหม่) จึงสั่ง `rollout restart` ต่อ
- `statefulset.apps/som-db configured` ขึ้นได้แม้ไฟล์ไม่เปลี่ยน (kubectl เติมค่าตั้งต้นบางช่อง) ไม่สร้าง revision ใหม่และ `som-db-0` ไม่ restart — ปกติ
- ออเดอร์ที่ 4 สั่งสำเร็จ (`orders=4`) ข้อมูลจากขั้น A ยังอยู่ครบ

### 10.11 เปิดร้านใน browser: เปลี่ยนป้ายอีกรอบ (ภาพหน้าจอจริง)

ทำขั้น C1, C2 และ D ซ้ำอีกรอบโดยดูผลใน 🌐 browser บนเครื่องนักศึกษาที่ **`http://localhost:30080`** ภาพหน้าจอ 4 ภาพในหัวข้อนี้เป็น **ภาพหน้าจอจริงจากการทดลอง** (browser เปิด NodePort 30080 โดยตรง) ถ่ายต่อจากขั้น 10.10 ออเดอร์จึงเป็น 4

**ฉาก 1 — ร้านที่ป้ายมาจาก ConfigMap** เปิด `http://localhost:30080` จะเห็นชื่อร้านอาหารแมวน้องส้ม ธีม harbor (น้ำเงิน) และแถบประกาศสีเหลือง

{{SHOT:1}}

**ฉาก 2 — แก้ ConfigMap แล้วหน้าเว็บยังเหมือนเดิม** 🐧 apply ป้ายชุดสาขาท่าเรือ รอ 90 วินาทีแล้ว refresh browser

```bash
kubectl apply -f extra/15-config-promo.yaml
curl -s localhost:30080/api/shop; echo
kubectl -n som-shop get pod -l app=som-web
```

```text
configmap/som-web-config configured
{"pod":"som-web-77467d5bc4-xbwpb","version":"1.5","shopName":"ร้านอาหารแมวน้องส้ม","theme":"harbor","promo":"","eyebrow":"⚓ ท่าเรือ Kubernetes · ConfigMap","footer":"Next.js + PostgreSQL · Kubernetes LAB 010 · ConfigMap som-web-config"}
NAME                       READY   STATUS    RESTARTS   AGE
som-web-77467d5bc4-nvkw8   1/1     Running   0          6m18s
som-web-77467d5bc4-w9zpt   1/1     Running   0          6m24s
som-web-77467d5bc4-xbwpb   1/1     Running   0          6m12s
```

{{SHOT:2}}

**ฉาก 3 — rollout restart แล้ว refresh** (รอราว 8 วินาทีหลัง `successfully rolled out`)

```bash
kubectl -n som-shop rollout restart deploy/som-web
kubectl -n som-shop rollout status deploy/som-web
curl -s localhost:30080/api/shop; echo; curl -s localhost:30080/api/stats; echo
kubectl -n som-shop get pod -l app=som-web
```

```text
deployment.apps/som-web restarted
Waiting for deployment "som-web" rollout to finish: 0 out of 3 new replicas have been updated...
...
deployment "som-web" successfully rolled out
{"pod":"som-web-5f4db546b6-766ft","version":"1.5","shopName":"ร้านน้องส้ม สาขาท่าเรือ","theme":"sunset","promo":"🎉 โปรวันนี้: ขนมปลาทูน่าลด 20%","eyebrow":"⚓ ท่าเรือ Kubernetes · ConfigMap","footer":"Next.js + PostgreSQL · Kubernetes LAB 010 · ConfigMap som-web-config"}
som-web-5f4db546b6-522dj 1.5 orders=4 products=6

NAME                       READY   STATUS    RESTARTS   AGE
som-web-5f4db546b6-522dj   1/1     Running   0          29s
som-web-5f4db546b6-766ft   1/1     Running   0          23s
som-web-5f4db546b6-c76dx   1/1     Running   0          35s
```

{{SHOT:3}}

**ฉาก 4 — แก้ประกาศ แล้ว refresh โดยไม่ restart**

```bash
kubectl apply -f extra/16-announcement-1800.yaml && ./wait-announcement.sh 18:00
kubectl -n som-shop get pod -l app=som-web
```

```text
configmap/som-announcement configured
เริ่ม 17:27:13 รอคำว่า "18:00" จาก http://localhost:30080/api/announcement
  Pod แรกเห็นประกาศใหม่หลัง 36 วินาที: som-web-5f4db546b6-c76dx 1.5 ปิดร้านเร็ว 18:00 น. ⛵
  ทุก Pod เห็นประกาศใหม่ (12/12) หลัง 65 วินาที
NAME                       READY   STATUS    RESTARTS   AGE
som-web-5f4db546b6-522dj   1/1     Running   0          94s
som-web-5f4db546b6-766ft   1/1     Running   0          88s
som-web-5f4db546b6-c76dx   1/1     Running   0          100s
```

{{SHOT:4}}

ชื่อ Pod ชุดเดิมจากฉาก 3 `RESTARTS 0` และ AGE ต่อเนื่อง (29s → 94s) แต่แถบประกาศเปลี่ยนเป็น `ปิดร้านเร็ว 18:00 น. ⛵` แล้ว

### 10.12 สรุป LAB 10

{{FIG:L21}}

| อยากเปลี่ยน | อยู่ที่ | ทำอย่างไร | ผลจริง |
|---|---|---|---|
| ชื่อร้าน, ธีม, โปรโมชัน | ConfigMap `som-web-config` → `envFrom` | แก้ ConfigMap + `rollout restart` (หรือชื่อใหม่ + แก้ Deployment) | รอ 90 วินาทีไม่เปลี่ยน → หลัง restart เปลี่ยนทุก Pod |
| ประกาศหน้าร้าน | ConfigMap `som-announcement` → volume `/etc/som` | แก้ ConfigMap อย่างเดียว | Pod แรก 36–63 วินาที ทุก Pod 48–88 วินาที `RESTARTS 0` |
| ค่าที่ต้องอ้าง `$(VAR)` | `env` ของ Deployment | `env` ชนะ `envFrom` | `namespace som-shop` |
| ป้ายชุดที่ห้ามแก้กลางทาง | `som-web-config-v2` (`immutable`) | ชื่อใหม่ + เปลี่ยนชื่อใน `envFrom` / `rollout undo` | rollout เอง, แก้ได้ `Forbidden` |
| image | `som-shop-web:1.5` | ไม่ต้องทำอะไร | ไม่ build ใหม่เลยทั้ง LAB |
| ออเดอร์ | PVC `data-som-db-0` | — | 3 → 3 ทุกขั้น → 4 |
| รหัสผ่านฐานข้อมูล | ยังเขียนใน YAML | — | intern เห็น `som:meow1234@` → บทที่ 11 |

**คำถามท้าย LAB 10**

1. ทำไมขั้น C1 รอ 90 วินาทีแล้วหน้าเว็บยังไม่เปลี่ยน แต่ขั้น D ประกาศเปลี่ยนเองภายในราว 1 นาที ทั้งที่แก้ ConfigMap เหมือนกัน
2. ถ้าแอปอ่าน `/etc/som/announcement.txt` แค่ครั้งเดียวตอนเริ่ม (แบบ nginx ใน LAB 7) ขั้น D จะเห็นผลแบบไหน และต้องแก้อย่างไร
3. ทำไม `k8s/20-web.yaml` mount `som-announcement` ทั้งโฟลเดอร์ `/etc/som` แทนการใช้ `subPath` ไปที่ `/etc/som/announcement.txt`
4. เปรียบเทียบการเปลี่ยนป้ายด้วย "แก้ `som-web-config` + `rollout restart`" (ขั้น C) กับ "สร้าง `som-web-config-v2` + เปลี่ยนชื่อใน Deployment" (ขั้น E) ในแง่ประวัติ (`rollout history`) และการย้อนรุ่น
5. ถ้าย้าย `DATABASE_URL` ไปไว้ใน ConfigMap `som-web-config` แล้วให้ intern ทำขั้น F ใหม่ ผลจะต่างไปไหม เพราะอะไร

### 10.13 เก็บกวาด LAB 10

ร้าน `som-shop` ตอนนี้ใช้ป้ายชุดสาขาท่าเรือและประกาศ 18:00 (สภาพหลังฉาก 4) ถ้าจะเรียนบทที่ 11 ต่อทันทีเก็บไว้ได้ ถ้าต้องการคืนทรัพยากร หรือก่อนทำ LAB นี้ซ้ำ ให้ลบทั้ง namespace (ลบ Deployment, StatefulSet, ConfigMap, ServiceAccount `intern` และ PVC `data-som-db-0` พร้อมออเดอร์ทั้งหมด และคืน NodePort 30080)

```bash
kubectl delete ns som-shop
```

ใช้เวลาราว 30 วินาที (Pod web มี preStop 5 วินาทีและ grace period) ถ้าแค่อยากคืนป้ายร้านเป็นค่าในไฟล์โดยไม่ลบออเดอร์ ให้ใช้คำสั่งของขั้น 10.10 (`kubectl apply -f k8s/` + `rollout restart`)

---

## Troubleshooting

| อาการ | สาเหตุ | วิธีแก้ |
|---|---|---|
| `ls` ใน k8s-lab ไม่เจอ `labs/` หรือ `som-shop-v6/`, kubectl แจ้ง `the path "..." does not exist` | ยังไม่ได้ `docker cp` หรืออยู่ผิดโฟลเดอร์ | 🖥️ `docker cp 010_kubernetes_configmap k8s-lab:/workspace/` แล้ว 🐧 `cd` ไปโฟลเดอร์ของ LAB นั้น ตรวจด้วย `pwd` |
| `./watch.sh: Permission denied` หรือ `./wait-announcement.sh: Permission denied` | สิทธิ์ execute หายระหว่างคัดลอก | `bash watch.sh` / `bash wait-announcement.sh 18:00` หรือ `chmod +x *.sh` |
| `kubectl get nodes` ต่อคลัสเตอร์ไม่ได้ | ยังไม่มีคลัสเตอร์ หรือ `k8s-lab` เพิ่ง restart | 🐧 `k8s-up` แล้วทำ LAB 0 ขั้นที่ 5 (โหลด postgres และ build/load `som-shop-web:1.5`) |
| `error: failed to create configmap: configmaps "demo" already exists` | `kubectl create` ใช้สร้างใหม่เท่านั้น | ลบก่อน หรือใช้ `kubectl create configmap ... --dry-run=client -o yaml \| kubectl apply -f -` |
| `Too long: may not be more than 1048576 bytes` | ConfigMap รวมทุก key เกิน 1 MiB | เก็บไฟล์ใหญ่ใน image หรือ volume อื่น |
| `envpod` เป็น `CreateContainerConfigError` ชั่วครู่หลัง `kubectl apply -f .` ใน LAB 2 | สร้าง Pod ก่อน ConfigMap (เรียงตามชื่อไฟล์) | รอไม่กี่วินาทีจะหายเอง หรือสั่ง `kubectl apply -f shop-config.yaml -f envpod.yaml` |
| Pod ค้าง `CreateContainerConfigError` + `configmap "..." not found` | ยังไม่มี ConfigMap ชื่อนั้นใน namespace ของ Pod (สะกดผิด, ลืม apply, อยู่คนละ namespace) | `kubectl get cm -n <ns>` สร้าง/แก้ชื่อให้ตรง Pod จะเริ่มเองภายในราว 15 วินาที |
| `couldn't find key NOPE in ConfigMap default/shop-config` และไม่หายเองหลังสร้าง ConfigMap อื่น | key ที่อ้างไม่มีใน ConfigMap (LAB 4 `nokey` ตั้งใจ) | เพิ่ม key ใน ConfigMap หรือแก้ YAML แล้วสร้าง Pod ใหม่ หรือใส่ `optional: true` ถ้าไม่จำเป็นจริง |
| Pod ค้าง `ContainerCreating` + `FailedMount ... configmap "..." not found` | volume อ้าง ConfigMap ที่ไม่มี | สร้าง ConfigMap แล้วรอ หรือใส่ `optional: true` |
| LAB 3/4/5/6: `configmap "shop-config" not found` หรือ `pods "envpod" not found` | ลบไปแล้ว หรือข้าม LAB 2/5 | ทำ LAB 2 (และ LAB 5 สำหรับ `volpod`) ใหม่ก่อน |
| `kubectl exec` เข้า `envpod`/`envfrom` ไม่ได้ และ STATUS เป็น `Completed` | `sleep 86400` จบหรือ Pod ถูกลบ (`restartPolicy: Never`) | ลบแล้ว apply Pod นั้นใหม่ |
| แก้ ConfigMap แล้วไฟล์ใน volume ยังไม่เปลี่ยนหลัง 20–60 วินาที | kubelet sync เป็นรอบ (วัดได้ 37–88 วินาที) | รอได้ถึง 2 นาที ถ้าเกินให้ตรวจว่าไม่ได้ใช้ subPath และแก้ ConfigMap ชื่อ/namespace ถูก |
| `watch.sh` พิมพ์ `เกิน 180 วินาทีแล้วยังไม่เปลี่ยน` | Pod `volpod` ไม่ได้อยู่ หรือ ConfigMap ถูกลบสร้างใหม่ | `kubectl get pod volpod`, `kubectl get cm shop-config -o yaml` แล้วรันใหม่ |
| ไฟล์ subPath / env ไม่เปลี่ยนเลย | พฤติกรรมปกติ อ่านครั้งเดียวตอนเริ่ม | `kubectl rollout restart` (Deployment) หรือลบแล้วสร้าง Pod ใหม่ |
| `wget: can't connect to remote host: Connection refused` ใน Pod nginx | `localhost` ไปที่ IPv6 `::1` แต่ nginx ฟัง IPv4 | ใช้ `curl -s 127.0.0.1/` หรือ `wget -qO- 127.0.0.1/` |
| วนรอไฟล์ใน LAB 7 พิมพ์ `command terminated with exit code 1` ซ้ำ ๆ | `grep -q` ยังไม่เจอคำแล้ว `kubectl exec` รายงาน exit code | ใส่ `2>/dev/null` ท้าย `kubectl exec ... grep -q ...` ตามคำสั่งในเอกสาร |
| ไฟล์ nginx เป็นค่าใหม่แต่ `curl` ได้ค่าเก่า | nginx อ่านไฟล์ครั้งเดียวตอนเริ่ม | `kubectl exec ngx -- nginx -s reload` หรือ `kubectl rollout restart deploy/plain` |
| `Warning: Detected changes to resource ngx which is currently being deleted` | apply ซ้ำขณะ Pod เดิมยัง Terminating | รอ `kubectl get pod` ว่างก่อนแล้ว apply ใหม่ |
| `Warning: would violate PodSecurity "restricted:latest" …` | ใช้ Pod nginx/busybox ใน namespace ที่ตั้ง `warn: restricted` | ปกติ เป็นแค่คำเตือน (LAB 1–9 ใช้ `default`) |
| `kubectl edit` ค้าง / หน้าจอแปลก ๆ `Vim: Warning: Output is not to a terminal` | `kubectl edit` เปิด vim แต่ไม่มี terminal โต้ตอบ | กด `Ctrl+C` หรือปิด session แล้วใช้ `kubectl patch`/`kubectl apply -f` แทน ใน terminal ปกติออกจาก vim ด้วย `Esc` แล้ว `:q!` |
| ``The ConfigMap "..." is invalid: data: Forbidden: field is immutable when `immutable` is set`` | ConfigMap เป็น `immutable: true` | ลบแล้วสร้างใหม่ หรือสร้างชื่อใหม่แล้วชี้ Deployment ไปชื่อใหม่ |
| LAB 9 ได้ชื่อ ConfigMap ไม่ใช่ `web-config-gh5tkgmddg` | `kz/announcement.txt` ไม่ตรงทุกไบต์ (ยังเป็น v2, editor เติม/ลบ newline) | `printf 'ประกาศ v1\n' > kz/announcement.txt` |
| LAB 9 ConfigMap `web-config-...` ค้างหลัง `kubectl delete -k kz` | `delete -k` ลบเฉพาะชื่อจากไฟล์ปัจจุบัน | `kubectl get cm -o name \| grep web-config \| xargs -r kubectl delete` |
| `ErrImagePull` / `ImagePullBackOff` ของ `som-shop-web:1.5` หรือ `postgres:17.11-alpine` | ยังไม่ได้ load image เข้า Node (คลัสเตอร์ใหม่หรือข้าม LAB 0) | LAB 0 ขั้นที่ 5 |
| `provided port is already allocated` ตอน apply `20-web.yaml` | Service อื่นจอง 30080 (เช่น `som-shop` ของบทที่ 9 ค้าง) | `kubectl get svc -A \| grep 30080` แล้วลบ namespace ที่ค้าง |
| `/api/shop` ได้ค่าเดิมหลัง `rollout restart` | Pod เก่ายังตอบในช่วง preStop 5 วินาที | รอราว 8 วินาทีหลัง `successfully rolled out` แล้วลองใหม่ |
| footer เป็น `$(POD_NAMESPACE)` ตรง ๆ | ใส่ `$(VAR)` ในค่าของ ConfigMap ที่ใช้ผ่าน envFrom | ตั้งค่านั้นใน `env` ของ Deployment (`kubectl set env` หรือแก้ YAML) |
| หลัง `kubectl apply -f k8s/20-web.yaml` footer ยังเป็นค่าที่ `set env` ไว้ | `kubectl set env` ไม่อยู่ใน last-applied apply จึงไม่ลบ | `kubectl -n som-shop set env deploy/som-web SHOP_FOOTER-` |
| `Warning: resource deployments/som-web was previously managed with 'kubectl apply' …` ตอน `rollout undo` | undo ไม่แก้ annotation last-applied | ปกติ ถ้าจะให้ตรงไฟล์ให้ `kubectl apply -f k8s/` ภายหลัง |
| `rollout history` CHANGE-CAUSE ซ้ำกันหลายบรรทัด / เลข revision กระโดด | `rollout restart`, `set env`, `patch`, `undo` ไม่เปลี่ยน annotation `change-cause` และ template ที่ซ้ำของเดิมถูกนำกลับมาเป็นเลขใหม่ | ปกติ (`revisionHistoryLimit: 5` ทำให้ revision เก่าสุดหายไปด้วย) |
| `statefulset.apps/som-db configured` ตอน `kubectl apply -f k8s/` ทั้งที่ไม่ได้แก้ไฟล์ | kubectl เทียบกับค่าตั้งต้นที่ API server เติม | ปกติ ไม่มี revision ใหม่ และ `som-db-0` ไม่ restart |
| browser เปิด `http://localhost:30080` ไม่ได้ ทั้งที่ใน k8s-lab `curl -s localhost:30080/api/stats` ได้ | container `k8s-lab` ไม่ได้ publish 30080 หรือโปรแกรมอื่นใช้พอร์ตนี้ | 🖥️ `docker port k8s-lab` ต้องมี `30080/tcp` ถ้าไม่มีใช้ 🖥️ `ssh -p 2223 -L 30080:localhost:30080 root@localhost` แล้วเปิดใหม่ |
| refresh browser แล้วประกาศสลับเก่า/ใหม่ | แต่ละ Pod เห็นไฟล์ใหม่ไม่พร้อมกัน | ปกติ รอราว 1–1.5 นาที (`wait-announcement.sh` บอกเวลาที่ครบ 12/12) |
| เวลาในชื่อโฟลเดอร์ `..2026_10_05_…` หรือ `ls -la` ใน Pod ช้ากว่านาฬิกา 7 ชั่วโมง | container ใช้ UTC | ปกติ |
| `Error from server (NotFound)` ตอนเก็บกวาด | ลบไปแล้วในขั้นก่อน | ไม่เป็นไร |

---

## Checklist ส่งงาน

ส่งภาพหน้าจอ (screenshot ของ terminal/browser) ตามรายการ พร้อมคำตอบคำถามชวนคิดอย่างน้อย LAB ละ 1 ข้อ และคำถามท้าย LAB 10 ทั้ง 5 ข้อ

- [ ] **LAB 0** `kubectl get nodes` (3 Ready), `kubectl version` (เห็น Kustomize), ไม่มี NodePort 3008x ค้าง และ `crictl images` ที่เห็น `som-shop-web 1.5` + `postgres 17.11-alpine` บนทั้งสอง worker
- [ ] **LAB 1** `kubectl get cm -A`, `api-resources` (`configmaps cm v1 true`), ผล `{"EMPTY":"",...}` ของ `--from-env-file`, `already exists`, `binaryData` ของ `logo.bin` และ `Too long: may not be more than 1048576 bytes`
- [ ] **LAB 2** `kubectl logs envpod` (`ARGS: ร้านน้องส้ม $(NOPE)`) และ args ใน spec `["$(SHOP_NAME)","$(NOPE)"]`
- [ ] **LAB 3** `kubectl logs envfrom` (มี `CFG_1bad`, `CFG_shop.name`), `CFG_APP_THEME=harbor (จาก env)`, `CFG_FOOTER=... $(POD_NAMESPACE)` และ `echo $CFG_shop.name` ได้ `.name`
- [ ] **LAB 4** สถานะ 4 Pod ตอน 25 วินาที, ข้อความ error ทั้ง 3 แบบ, สถานะหลังสร้าง `not-here` (`nokey` ยังค้าง), `ls /etc/opt-cm` ที่เห็น `HELLO` หลังรอ และ `configmap "shop-config" not found` ของ namespace `other`
- [ ] **LAB 5** `ls -la /etc/all` (symlink `..data`), `-r--------` ของ `menu/today.txt`, subPath เป็นไฟล์จริง และ `Read-only file system`
- [ ] **LAB 6** ผล `./watch.sh` ทั้ง 3 รอบพร้อมเวลาของเครื่องตัวเอง (volume เปลี่ยน subPath/env ไม่เปลี่ยน) และ `..data` ชี้โฟลเดอร์ใหม่
- [ ] **LAB 7** ไฟล์ v2 แต่ `curl` ได้ `menu v1` → reload → `menu v2`, `plain` ตอบ `menu v1` ทั้งที่ไฟล์ v3 → `rollout restart` → `menu v3`, annotation `restartedAt` + `checksum/config` และ `rollout history` 3 revision
- [ ] **LAB 8** error `Forbidden: field is immutable` ทั้ง 4 วิธี, label `tier=menu` และ `79 true` หลังลบสร้างใหม่
- [ ] **LAB 9** `kubectl kustomize kz` (`web-config-gh5tkgmddg`), หลังแก้ไฟล์ได้ `web-config-6db7mkcg8t` + `deployment.apps/kz-web configured`, REVISION 1–2 และ ConfigMap เก่าค้างหลัง `delete -k`
- [ ] **LAB 10** (1) ขั้น A `orders=3` + `(ไม่มีประกาศ)` (2) ขั้น B `/api/shop` ค่าจาก ConfigMap + `ls -la /etc/som` (3) ขั้นเสริม footer `$(POD_NAMESPACE)` → `namespace som-shop` (4) ขั้น C1 ค่าเดิมหลังรอ 90 วินาที + `RESTARTS 0` (5) ขั้น C2 `ร้านน้องส้ม สาขาท่าเรือ`/sunset/promo + `orders=3` (6) ขั้น D ผล `wait-announcement.sh` ของเครื่องตัวเอง + `get pod` ก่อน/หลัง (ชื่อเดิม RESTARTS 0) (7) ขั้น E `ร้านน้องส้ม (v2)` + `Forbidden` + ผลหลัง `rollout undo` (8) ขั้น F `4 som:meow1234@` (บังรหัสในภาพ) + `cannot patch resource "configmaps"` (9) `orders=4` หลังคืนสภาพ (10) browser 4 ฉาก: harbor → ยังเดิมหลังแก้ → sunset + โปร → ประกาศ 18:00
- [ ] ท้ายสุด `kubectl get cm` ใน `default` เหลือแค่ `kube-root-ca.crt` และ `kubectl get pod` ใน `default` ว่าง

---

## ตารางเก็บกวาดและคืนสภาพ

ใช้ตรวจหลังจบแต่ละ LAB หรือเมื่อผลเริ่มเพี้ยน 🐧 ทุกคำสั่งรันใน SSH session ของ k8s-lab

| สิ่งที่อาจค้าง | มาจาก LAB | ตรวจด้วย | คืนสภาพด้วย |
|---|---|---|---|
| ConfigMap `demo`, `files`, `envf`, `bin`, `big2` + ไฟล์ `logo.bin`, `big.txt`, `big2.txt` | 1 | `kubectl get cm`; `ls labs/lab01-create` | `kubectl delete cm demo files envf bin big2`; `rm -f logo.bin big.txt big2.txt` (ใน `lab01-create`) |
| ConfigMap `shop-config`, Pod `envpod`, `envfrom`, `volpod` (ใช้ LAB 2–6) | 2–6 | `kubectl get pod,cm` | `kubectl delete pod envpod envfrom volpod --now; kubectl delete cm shop-config` |
| Pod `nocm`, `nokey`, `optpod`, `novol`, ConfigMap `not-here`, namespace `other` | 4 | `kubectl get pod; kubectl get ns other` | `cd …/labs/lab04-missing && kubectl delete -f nocm.yaml -f nokey.yaml -f optpod.yaml -f novol.yaml --now; kubectl delete cm not-here; kubectl delete ns other` |
| Pod `ngx`, Deployment `plain`, ConfigMap `nginx-conf`, namespace `psa-demo` | 7 | `kubectl get pod,deploy,cm; kubectl get ns psa-demo` | `cd …/labs/lab07-reload && kubectl delete -f ngx.yaml -f plain-deploy.yaml -f nginx-conf.yaml; kubectl delete ns psa-demo` |
| ConfigMap `frozen` | 8 | `kubectl get cm frozen` | `kubectl delete cm frozen` |
| Deployment `kz-web`, ConfigMap `web-config-*`, ไฟล์ `kz/announcement.txt` ที่ถูกแก้ | 9 | `kubectl get deploy kz-web; kubectl get cm \| grep web-config; cat kz/announcement.txt` | `kubectl delete -k kz; kubectl get cm -o name \| grep web-config \| xargs -r kubectl delete; printf 'ประกาศ v1\n' > kz/announcement.txt` |
| namespace `som-shop` (**จอง NodePort 30080**) + ConfigMap ร้าน, ServiceAccount `intern`, PVC `data-som-db-0` | 10 | `kubectl get ns som-shop`; `kubectl -n som-shop get all,cm,pvc,sa` | `kubectl delete ns som-shop` (หรือเก็บไว้สำหรับบทที่ 11) |
| image `som-shop-web:1.5`, postgres, nginx, busybox บน Node และ `/root/postgres.tar` | 0–10 | `docker exec lab-worker crictl images`; `ls /root/postgres.tar` | **เก็บ image ไว้ได้** (ใช้ซ้ำในบทถัดไป ถ้า `k8s-down` จะหายไปด้วย) ไฟล์ tar ลบได้ `rm -f /root/postgres.tar` |

ตอนลบของที่ไม่มีอยู่แล้ว kubectl อาจแจ้ง `NotFound` ซึ่งไม่เป็นไร

---

## เก็บกวาดหลังจบบท

🐧 **ใน SSH session ของ k8s-lab** ตรวจครั้งสุดท้าย

```bash
kubectl get nodes
kubectl get ns
kubectl get pod,deploy,cm
kubectl get pv,pvc -A
```

ผลที่ถูกต้อง: 3 Node `Ready`, ใน namespace `default` ไม่มี Pod/Deployment และมี ConfigMap แค่ `kube-root-ca.crt` (ผลจริงท้ายการทดลอง: `configmap/kube-root-ca.crt   1      37m`) ถ้าลบ `som-shop` แล้ว namespace จะเหลือ 5 ตัวตั้งต้น (`default`, `kube-node-lease`, `kube-public`, `kube-system`, `local-path-storage`) และไม่มี PV/PVC

คลัสเตอร์ `lab` และ image ของร้านเก็บไว้ใช้ต่อในบทถัดไปได้ ถ้าต้องการคืนทรัพยากรเครื่อง ให้ลบคลัสเตอร์ด้วย `k8s-down` (image ที่ `kind load` ไว้จะหายไปด้วย ครั้งหน้าต้อง `k8s-up` และ build/`kind load` ใหม่) แล้วออกจาก SSH ด้วย `exit`

บทถัดไป: **บทที่ 11 Secret — ซองปิดผนึก** จะย้ายรหัสผ่าน `som:meow1234` ออกจาก YAML ของ Deployment/StatefulSet ไปไว้ในที่ที่ให้สิทธิ์แยกจาก ConfigMap ได้

---

> **หมายเหตุเกี่ยวกับภาพประกอบ:** ภาพประกอบ LAB (ยกเว้นภาพในโฟลเดอร์ [`images/screenshots/`](images/screenshots/) ซึ่งเป็นภาพหน้าจอจริงจากการทดลอง) สร้างขึ้นด้วยปัญญาประดิษฐ์สำหรับการสร้างภาพเพื่อใช้ประกอบการเรียนการสอน ชุดคำสั่งสร้างภาพอยู่ใน [`images/imagegen-prompts.md`](images/imagegen-prompts.md) ภาพใช้อุปมาเชิงเปรียบเทียบ ตัวเลขในภาพ (เช่น ชื่อ Pod, จำนวนวินาที และ hash) เป็นค่าตัวอย่าง ให้ยึดผลลัพธ์คำสั่งในเอกสารและในเครื่องของนักศึกษาเป็นหลัก ภาพหน้าจอจริง 4 ภาพถ่ายจาก browser ที่เปิด NodePort 30080 โดยตรง (บนเครื่องนักศึกษาคือ `http://localhost:30080`) ในรอบที่ทำขั้น C1, C2 และ D ซ้ำหลังคืนสภาพร้าน (หัวข้อ 10.11) ชื่อ Pod และจำนวนออเดอร์ (4) ในภาพจึงต่างจากผลคำสั่งในขั้นหลักของเอกสาร
