
---

## LAB 6: อัปเดตเองและจับเวลา

{{FIG:L07}}

**เป้าหมาย:** แก้ `shop-config` แล้วจับเวลาว่าไฟล์ใน volume เปลี่ยนเมื่อไร เทียบกับไฟล์ subPath และ env ใน `envpod` ในการทดลองเดียวกัน และเห็น `..data` สลับไปโฟลเดอร์ใหม่

**ไฟล์:** `labs/lab06-update/watch.sh` (ต้องมี `envpod` จาก LAB 2 และ `volpod` จาก LAB 5)

สคริปต์ทำซ้ำ 3 รอบ (ค่าเริ่ม) รอบละ: `kubectl patch cm shop-config` เปลี่ยน `announcement.txt=ปลาทูรอบN` และ `SHOP_NAME=ร้านใหม่N` → วนอ่าน `/etc/all/announcement.txt` ใน `volpod` ทุก 1 วินาทีจนได้ค่าใหม่ (ไม่เกิน 180 วินาที) → พิมพ์ค่าจาก volume, subPath และ env

```bash
kubectl patch cm shop-config --type merge \
  -p "{\"data\":{\"announcement.txt\":\"$v\n\",\"SHOP_NAME\":\"ร้านใหม่$r\"}}" >/dev/null
```

### ขั้นที่ 1: รันสคริปต์ (ราว 4–5 นาที)

🐧 **ใน SSH session ของ k8s-lab**

```bash
cd /workspace/010_kubernetes_configmap/02_LAB/labs/lab06-update
./watch.sh
```

```text
รอบ 1: 16:53:11 patch shop-config → announcement.txt=ปลาทูรอบ1, SHOP_NAME=ร้านใหม่1
  volume /etc/all/announcement.txt เปลี่ยนหลัง 85 วินาที: ปลาทูรอบ1
  volume /etc/all/SHOP_NAME             : ร้านใหม่1
  subPath /etc/som/announcement.txt     : วันนี้ปลาทูสด
  env SHOP_NAME ใน envpod               : ร้านน้องส้ม
รอบ 2: 16:54:41 patch shop-config → announcement.txt=ปลาทูรอบ2, SHOP_NAME=ร้านใหม่2
  volume /etc/all/announcement.txt เปลี่ยนหลัง 55 วินาที: ปลาทูรอบ2
  volume /etc/all/SHOP_NAME             : ร้านใหม่2
  subPath /etc/som/announcement.txt     : วันนี้ปลาทูสด
  env SHOP_NAME ใน envpod               : ร้านน้องส้ม
รอบ 3: 16:55:41 patch shop-config → announcement.txt=ปลาทูรอบ3, SHOP_NAME=ร้านใหม่3
  volume /etc/all/announcement.txt เปลี่ยนหลัง 62 วินาที: ปลาทูรอบ3
  volume /etc/all/SHOP_NAME             : ร้านใหม่3
  subPath /etc/som/announcement.txt     : วันนี้ปลาทูสด
  env SHOP_NAME ใน envpod               : ร้านน้องส้ม
--- ..data ชี้ไปโฟลเดอร์เวลาใหม่:
lrwxrwxrwx    1 root     root            32 Oct  5 09:56 ..data -> ..2026_10_05_09_56_42.2491344353
lrwxrwxrwx    1 root     root            11 Oct  5 09:53 1bad -> ..data/1bad
lrwxrwxrwx    1 root     root            16 Oct  5 09:53 APP_THEME -> ..data/APP_THEME
lrwxrwxrwx    1 root     root            13 Oct  5 09:53 FOOTER -> ..data/FOOTER
lrwxrwxrwx    1 root     root            16 Oct  5 09:53 SHOP_NAME -> ..data/SHOP_NAME
lrwxrwxrwx    1 root     root            23 Oct  5 09:53 announcement.txt -> ..data/announcement.txt
lrwxrwxrwx    1 root     root            15 Oct  5 09:53 menu.txt -> ..data/menu.txt
lrwxrwxrwx    1 root     root            16 Oct  5 09:53 shop.name -> ..data/shop.name
```

ตัวเลขวินาทีในเครื่องนักศึกษาจะต่างไป (การทดลองอีกรอบก่อนหน้าได้ 65 / 70 / 85 วินาที) ช่วงที่คาดได้คือราว 30–90 วินาที ถ้าสคริปต์พิมพ์ `เกิน 180 วินาทีแล้วยังไม่เปลี่ยน` ให้ดู [Troubleshooting](#troubleshooting)

### ขั้นที่ 2: ดู ..data อีกครั้ง

```bash
kubectl exec volpod -- ls -la /etc/all | grep -E '(\.\.data|announcement\.txt) ->'
```

```text
lrwxrwxrwx    1 root     root            32 Oct  5 09:56 ..data -> ..2026_10_05_09_56_42.2491344353
lrwxrwxrwx    1 root     root            23 Oct  5 09:53 announcement.txt -> ..data/announcement.txt
```

symlink ของไฟล์ยังเป็นเวลาเดิม (`09:53`) แต่ `..data` ชี้โฟลเดอร์ใหม่ (`09:56`) kubelet เขียนชุดใหม่ทั้งหมดแล้ว "สลับป้ายลูกศร" ทีเดียว ทุกไฟล์จึงเปลี่ยนพร้อมกัน (`announcement.txt` และ `SHOP_NAME` เป็นรอบเดียวกันเสมอ)

### ขั้นที่ 3: เก็บกวาด LAB 2–6

```bash
cd /workspace/010_kubernetes_configmap/02_LAB/labs
kubectl delete pod envpod envfrom volpod --now; kubectl delete cm shop-config; kubectl get pod,cm
```

```text
pod "envpod" deleted from default namespace
pod "envfrom" deleted from default namespace
pod "volpod" deleted from default namespace
configmap "shop-config" deleted from default namespace
NAME                         DATA   AGE
configmap/kube-root-ca.crt   1      13m
```

### สิ่งที่เห็น

- ไฟล์ใน volume เปลี่ยนเองโดยไม่ restart Pod แต่ใช้เวลา **85 / 55 / 62 วินาที** (ราว 1 นาที บางครั้งเกือบ 1.5 นาที) เพราะ kubelet sync เป็นรอบ
- ไฟล์ **subPath ไม่เปลี่ยนเลย** (`วันนี้ปลาทูสด` ทุกรอบ) และ **env ไม่เปลี่ยนเลย** (`ร้านน้องส้ม` ทุกรอบ)
- `..data` ชี้โฟลเดอร์เวลาใหม่ ไฟล์ทั้งชุดจึงเปลี่ยนพร้อมกันแบบ atomic

**คำถามชวนคิด**

1. ถ้าแอปของเราอ่าน `SHOP_NAME` จาก env แต่อ่านประกาศจากไฟล์ใน volume แก้ ConfigMap แล้วผู้ใช้จะเห็นอะไรเปลี่ยนก่อน
2. ทำไมแต่ละรอบใช้เวลาไม่เท่ากัน (ใบ้: kubelet ไม่ได้เริ่มนับเวลาตอนที่เรา patch)

---

## LAB 7: แอปต้องโหลดใหม่เอง

{{FIG:L08}}

**เป้าหมาย:** เห็นว่าไฟล์ตั้งค่า nginx ใน volume เปลี่ยนแล้วแต่ nginx ยังใช้ค่าเก่าจนกว่าจะ `nginx -s reload` และใช้ `kubectl rollout restart` กับ checksum annotation ให้ Deployment ได้ Pod ใหม่ที่อ่านค่าล่าสุด

**ไฟล์:** `labs/lab07-reload/`

| ไฟล์ | เนื้อหา |
|---|---|
| `nginx-conf.yaml` | ConfigMap `nginx-conf` key `default.conf` ตอบ `menu v1` |
| `nginx-conf-v2.yaml`, `nginx-conf-v3.yaml` | ConfigMap ชื่อเดียวกัน ตอบ `menu v2` / `menu v3` (apply = แก้กระดานเดิม) |
| `ngx.yaml` | Pod `ngx` (nginx:1.27-alpine) mount `nginx-conf` ทับ `/etc/nginx/conf.d` ทั้งโฟลเดอร์ |
| `plain-deploy.yaml` | Deployment `plain` nginx แบบเดียวกัน 1 replica |

เนื้อหาของ `nginx-conf.yaml`

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: nginx-conf
data:
  default.conf: |
    server { listen 80; location / { default_type text/plain; return 200 "menu v1\n"; } }
```

> LAB นี้ใช้ไฟล์ `nginx-conf-v2.yaml`/`nginx-conf-v3.yaml` แทน `kubectl patch` เพราะค่าที่เป็นไฟล์ nginx มีทั้ง `"` และ `\n` ถ้าเขียนเป็น JSON ใน patch ต้อง escape หลายชั้นและพลาดง่าย (การทดลองรอบแรกได้ `\n` ดิบติดไปในไฟล์) การแก้ด้วยไฟล์ YAML แล้ว `kubectl apply -f` อ่านง่ายและเก็บใน git ได้

### ขั้นที่ 1: apply และเรียก nginx

🐧 **ใน SSH session ของ k8s-lab**

```bash
cd /workspace/010_kubernetes_configmap/02_LAB/labs/lab07-reload
ls; kubectl apply -f nginx-conf.yaml -f ngx.yaml -f plain-deploy.yaml
kubectl wait --for=condition=Ready pod/ngx --timeout=120s; kubectl rollout status deploy/plain --timeout=120s
kubectl exec ngx -- curl -s 127.0.0.1/; kubectl exec deploy/plain -- curl -s 127.0.0.1/
```

```text
nginx-conf-v2.yaml
nginx-conf-v3.yaml
nginx-conf.yaml
ngx.yaml
plain-deploy.yaml
configmap/nginx-conf created
pod/ngx created
deployment.apps/plain created
pod/ngx condition met
deployment "plain" successfully rolled out
menu v1
menu v1
```

> **ใช้ `127.0.0.1` ไม่ใช่ `localhost`** — `wget` ใน image ไปที่ `localhost` แล้วเลือก IPv6 `::1` ก่อน แต่ไฟล์ตั้งค่านี้ฟังแค่ IPv4 (`listen 80;`) ผลจริง
>
> ```text
> $ kubectl exec ngx -- wget -qO- localhost/
> wget: can't connect to remote host: Connection refused
> command terminated with exit code 1
> $ kubectl exec ngx -- wget -qO- 127.0.0.1/
> menu v1
> ```

### ขั้นที่ 2: เปลี่ยนเป็น v2 แล้วรอไฟล์

คำสั่งนี้ apply ConfigMap ชุดใหม่แล้ววนตรวจทุก 2 วินาทีว่าไฟล์ใน `ngx` มีคำว่า `v2` หรือยัง (`2>/dev/null` ซ่อนข้อความ `command terminated with exit code 1` ที่ `grep` พิมพ์ทุกรอบที่ยังไม่เจอ)

```bash
kubectl apply -f nginx-conf-v2.yaml; t0=$(date +%s); until kubectl exec ngx -- grep -q v2 /etc/nginx/conf.d/default.conf 2>/dev/null; do [ $(( $(date +%s)-t0 )) -gt 180 ] && break; sleep 2; done; echo "ไฟล์ใน ngx เปลี่ยนหลัง $(( $(date +%s)-t0 )) วินาที"
```

```text
configmap/nginx-conf configured
ไฟล์ใน ngx เปลี่ยนหลัง 75 วินาที
```

ดูไฟล์และเรียก nginx

```bash
kubectl exec ngx -- cat /etc/nginx/conf.d/default.conf; kubectl exec ngx -- curl -s 127.0.0.1/
```

```text
server { listen 80; location / { default_type text/plain; return 200 "menu v2\n"; } }
menu v1
```

**ไฟล์เป็น v2 แล้ว แต่ nginx ยังตอบ `menu v1`** เพราะ nginx อ่านไฟล์ตั้งค่าครั้งเดียวตอนเริ่ม

### ขั้นที่ 3: สั่ง nginx reload

```bash
kubectl exec ngx -- nginx -s reload; sleep 1; kubectl exec ngx -- curl -s 127.0.0.1/
```

```text
2026/10/05 10:07:20 [notice] 310#310: signal process started
menu v2
```

### ขั้นที่ 4: v3 — Pod เดี่ยวกับ Deployment

```bash
kubectl apply -f nginx-conf-v3.yaml; t0=$(date +%s); until kubectl exec ngx -- grep -q v3 /etc/nginx/conf.d/default.conf 2>/dev/null; do [ $(( $(date +%s)-t0 )) -gt 180 ] && break; sleep 2; done; echo "ไฟล์ใน ngx เปลี่ยนหลัง $(( $(date +%s)-t0 )) วินาที"
kubectl exec ngx -- curl -s 127.0.0.1/; kubectl exec deploy/plain -- cat /etc/nginx/conf.d/default.conf; kubectl exec deploy/plain -- curl -s 127.0.0.1/
kubectl exec ngx -- nginx -s reload; sleep 1; kubectl exec ngx -- curl -s 127.0.0.1/
```

```text
configmap/nginx-conf configured
ไฟล์ใน ngx เปลี่ยนหลัง 63 วินาที
menu v2
server { listen 80; location / { default_type text/plain; return 200 "menu v3\n"; } }
menu v1
2026/10/05 10:08:32 [notice] 546#546: signal process started
menu v3
```

(เลข process ในบรรทัด `[notice]` ในเครื่องนักศึกษาจะต่างไป) สังเกต Deployment `plain`: ไฟล์เป็น v3 แล้วแต่ยังตอบ **`menu v1`** เพราะไม่เคยมีใคร reload เลยตั้งแต่เริ่ม

### ขั้นที่ 5: rollout restart ให้ Pod ใหม่

แทนที่จะ `exec` เข้าไป reload ทีละ Pod ให้ Deployment สร้าง Pod ใหม่ ซึ่งอ่านไฟล์ล่าสุดตั้งแต่เริ่ม

```bash
kubectl rollout restart deploy/plain && kubectl rollout status deploy/plain --timeout=120s
kubectl exec deploy/plain -- curl -s 127.0.0.1/
kubectl get deploy plain -o jsonpath='{.spec.template.metadata.annotations}'; echo
```

```text
deployment.apps/plain restarted
Waiting for deployment "plain" rollout to finish: 1 old replicas are pending termination...
Waiting for deployment "plain" rollout to finish: 1 old replicas are pending termination...
deployment "plain" successfully rolled out
menu v3
{"kubectl.kubernetes.io/restartedAt":"2026-10-05T17:08:34+07:00"}
```

`rollout restart` ไม่มีเวทมนตร์ มันแค่เติม annotation `kubectl.kubernetes.io/restartedAt` ใน Pod template ทำให้ template เปลี่ยน → rolling update ตามปกติของบทที่ 7

### ขั้นที่ 6: checksum annotation

อีกวิธีคือใส่ hash ของเนื้อหา ConfigMap ไว้ใน annotation ของ template เนื้อหาเปลี่ยน = hash เปลี่ยน = rollout (Helm ใช้วิธีนี้ ในบทนี้คำนวณด้วยมือ)

```bash
SUM=$(kubectl get cm nginx-conf -o jsonpath='{.data}' | sha256sum | cut -c1-12); echo $SUM; kubectl patch deploy plain -p "{\"spec\":{\"template\":{\"metadata\":{\"annotations\":{\"checksum/config\":\"$SUM\"}}}}}" && kubectl rollout status deploy/plain --timeout=120s
kubectl get deploy plain -o jsonpath='{.spec.template.metadata.annotations}'; echo; kubectl rollout history deploy/plain
```

```text
a7aed9955c80
deployment.apps/plain patched
Waiting for deployment "plain" rollout to finish: 1 old replicas are pending termination...
Waiting for deployment "plain" rollout to finish: 1 old replicas are pending termination...
deployment "plain" successfully rolled out
{"checksum/config":"a7aed9955c80","kubectl.kubernetes.io/restartedAt":"2026-10-05T17:08:34+07:00"}
deployment.apps/plain 
REVISION  CHANGE-CAUSE
1         <none>
2         <none>
3         <none>
```

REVISION 2 มาจาก `rollout restart` และ REVISION 3 มาจาก checksum ค่า `a7aed9955c80` จะเหมือนกันทุกเครื่องถ้า ConfigMap เป็น v3 ตรงกัน

### ขั้นที่ 7 (สังเกตเพิ่ม): nginx กับ Pod Security

Pod nginx นี้รันเป็น root ฟังพอร์ต 80 ใช้ได้ใน `default` ที่ไม่มีป้าย Pod Security ถ้าเอาไปใช้ใน namespace ที่ตั้ง `warn: restricted` (แบบ `som-shop` ใน LAB 10) จะได้คำเตือน ลองแบบ server dry-run (ไม่สร้างจริง)

```bash
kubectl create ns psa-demo; kubectl label ns psa-demo pod-security.kubernetes.io/warn=restricted; kubectl -n psa-demo apply -f nginx-conf.yaml -f ngx.yaml --dry-run=server; kubectl delete ns psa-demo
```

```text
namespace/psa-demo created
namespace/psa-demo labeled
configmap/nginx-conf created (server dry run)
Warning: would violate PodSecurity "restricted:latest": allowPrivilegeEscalation != false (container "nginx" must set securityContext.allowPrivilegeEscalation=false), unrestricted capabilities (container "nginx" must set securityContext.capabilities.drop=["ALL"]), runAsNonRoot != true (pod or container "nginx" must set securityContext.runAsNonRoot=true), seccompProfile (pod or container "nginx" must set securityContext.seccompProfile.type to "RuntimeDefault" or "Localhost")
pod/ngx created (server dry run)
namespace "psa-demo" deleted
```

เป็นแค่ `warn` Pod ยังสร้างได้ (บทที่ 4) ร้านน้องส้มใน LAB 10 ตั้ง `securityContext` ครบจึงไม่มีคำเตือน

### ขั้นที่ 8: เก็บกวาด

```bash
kubectl delete -f ngx.yaml -f plain-deploy.yaml -f nginx-conf.yaml
```

```text
pod "ngx" deleted from default namespace
deployment.apps "plain" deleted from default namespace
configmap "nginx-conf" deleted from default namespace
```

ถ้าจะทำ LAB นี้ซ้ำ รอให้ Pod เก่าหายก่อน (`kubectl get pod` ว่าง) ไม่อย่างนั้นอาจได้ `Warning: Detected changes to resource ngx which is currently being deleted`

### สิ่งที่เห็น

- ไฟล์ใน volume ของ nginx เปลี่ยนเองหลัง **75 วินาที** (v2) และ **63 วินาที** (v3) แต่ nginx ยังตอบค่าเก่าจนกว่าจะ `nginx -s reload`
- Deployment `plain` ที่ไม่มีใคร reload ตอบ `menu v1` ทั้งที่ไฟล์เป็น v3 → `rollout restart` ได้ Pod ใหม่ตอบ `menu v3`
- `rollout restart` = เติม annotation `restartedAt` ส่วน checksum annotation ให้ rollout ตามเนื้อหา config (REVISION 3)

**คำถามชวนคิด**

1. ถ้า Deployment มี 3 Pod การ `kubectl exec ... nginx -s reload` ทีละ Pod มีข้อเสียอะไรเทียบกับ `rollout restart`
2. ข้อดีของ checksum annotation เหนือ `rollout restart` คืออะไร เมื่อเก็บ manifest ไว้ใน git

---

## LAB 8: immutable

{{FIG:L09}}

**เป้าหมาย:** สร้าง ConfigMap `immutable: true` ลองแก้ด้วยทุกวิธี (patch, apply, replace) เห็นว่าแก้ได้แค่ metadata และต้องลบสร้างใหม่

**ไฟล์:** `labs/lab08-immutable/frozen.yaml`

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: frozen
immutable: true
data:
  PRICE: "99"
```

### ขั้นที่ 1: สร้างและดู

🐧 **ใน SSH session ของ k8s-lab**

```bash
cd /workspace/010_kubernetes_configmap/02_LAB/labs/lab08-immutable
kubectl apply -f frozen.yaml; kubectl get cm frozen -o yaml | grep -E "immutable|PRICE"
```

```text
configmap/frozen created
  PRICE: "99"
immutable: true
      {"apiVersion":"v1","data":{"PRICE":"99"},"immutable":true,"kind":"ConfigMap","metadata":{"annotations":{},"name":"frozen","namespace":"default"}}
```

บรรทัดสุดท้ายคือ annotation `last-applied-configuration` ที่ `kubectl apply` บันทึกไว้

### ขั้นที่ 2: ลองแก้ทุกวิธี

```bash
kubectl patch cm frozen --type merge -p '{"data":{"PRICE":"79"}}'
kubectl patch cm frozen --type merge -p '{"immutable":false}'
sed 's/"99"/"79"/' frozen.yaml | kubectl apply -f -
sed 's/"99"/"79"/' frozen.yaml | kubectl replace -f -
```

```text
The ConfigMap "frozen" is invalid: data: Forbidden: field is immutable when `immutable` is set
The ConfigMap "frozen" is invalid: immutable: Forbidden: field is immutable when `immutable` is set
The ConfigMap "frozen" is invalid: data: Forbidden: field is immutable when `immutable` is set
The ConfigMap "frozen" is invalid: data: Forbidden: field is immutable when `immutable` is set
```

ทั้งแก้ราคา (`data`) และพยายามปิด immutable ถูกปฏิเสธที่ API server

> **อย่าใช้ `kubectl edit cm frozen` เพื่อทดลองข้อนี้** ถ้า terminal ไม่ใช่แบบโต้ตอบ (สคริปต์, `ssh ... "คำสั่ง"`) `kubectl edit` จะเปิด vim ค้างไว้ (การทดลองได้ `Vim: Warning: Output is not to a terminal` แล้วต้อง kill process) ถ้าใช้ใน SSH session ปกติ vim จะเปิดได้ แก้แล้วบันทึกก็จะได้ error แบบเดียวกัน ออกโดยไม่บันทึกด้วย `:q!`

### ขั้นที่ 3: แก้ metadata ได้

```bash
kubectl label cm frozen tier=menu; kubectl get cm frozen --show-labels
```

```text
configmap/frozen labeled
NAME     DATA   AGE   LABELS
frozen   1      1s    tier=menu
```

### ขั้นที่ 4: เปลี่ยนค่าด้วยการลบแล้วสร้างใหม่

```bash
kubectl delete cm frozen; sed "s/\"99\"/\"79\"/" frozen.yaml | kubectl apply -f -; kubectl get cm frozen -o jsonpath="{.data.PRICE} {.immutable}"; echo
```

```text
configmap "frozen" deleted from default namespace
configmap/frozen created
79 true
```

ในระบบจริงการลบ ConfigMap ที่ Pod ใช้อยู่เสี่ยง (Pod ที่เริ่มใหม่ระหว่างนั้นจะค้าง) วิธีที่ดีกว่าคือสร้าง **ชื่อใหม่** (`frozen-v2`) แล้วชี้ Deployment ไปชื่อใหม่ ซึ่ง LAB 10 ขั้น E จะทำให้ดู

### ขั้นที่ 5: เก็บกวาด

```bash
kubectl delete cm frozen
```

```text
configmap "frozen" deleted from default namespace
```

### สิ่งที่เห็น

- `immutable: true` → แก้ `data` ไม่ได้ทั้ง patch/apply/replace และเปลี่ยน `immutable` เป็น false ไม่ได้ (`Forbidden: field is immutable when ...`)
- แก้ label (metadata) ได้ เปลี่ยนค่าต้องลบสร้างใหม่หรือใช้ชื่อใหม่

**คำถามชวนคิด**

1. ทำไม immutable ช่วยลดภาระของ API server ในคลัสเตอร์ที่มี ConfigMap และ Pod จำนวนมาก
2. ถ้าทีมใช้ชื่อ ConfigMap แบบ `-v1`, `-v2`, `-v3` + immutable ต้องมีขั้นตอนอะไรเพิ่ม เพื่อไม่ให้ ConfigMap รุ่นเก่าค้างเต็มคลัสเตอร์

---

## LAB 9: kustomize configMapGenerator

{{FIG:L10}}

**เป้าหมาย:** ใช้ kustomize ที่ติดมากับ kubectl สร้าง ConfigMap ชื่อมี hash จากเนื้อหา แก้เนื้อหาแล้วเห็นชื่อใหม่และ Deployment rollout เอง

**ไฟล์:** `labs/lab09-kustomize/kz/kustomization.yaml`, `announcement.txt` (`ประกาศ v1`), `deploy.yaml` (Deployment `kz-web` busybox ที่ `envFrom` อ้างชื่อสั้น `web-config`)

```yaml
configMapGenerator:
- name: web-config
  literals:
  - SHOP_NAME=ร้านน้องส้ม
  files:
  - announcement.txt        # key = ชื่อไฟล์, ค่า = เนื้อไฟล์
resources:
- deploy.yaml
```

### ขั้นที่ 1: ดูผลก่อน apply

🐧 **ใน SSH session ของ k8s-lab**

```bash
cd /workspace/010_kubernetes_configmap/02_LAB/labs/lab09-kustomize
kubectl kustomize kz
```

```text
apiVersion: v1
data:
  SHOP_NAME: ร้านน้องส้ม
  announcement.txt: |
    ประกาศ v1
kind: ConfigMap
metadata:
  name: web-config-gh5tkgmddg
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kz-web
spec:
  replicas: 1
  selector:
    matchLabels:
      app: kz-web
  template:
    metadata:
      labels:
        app: kz-web
    spec:
      containers:
      - command:
        - sleep
        - "86400"
        envFrom:
        - configMapRef:
            name: web-config-gh5tkgmddg
        image: busybox:1.36
        name: c
      terminationGracePeriodSeconds: 1
```

ConfigMap ได้ชื่อ `web-config-gh5tkgmddg` และ `envFrom` ใน Deployment ถูกแก้เป็นชื่อเดียวกันให้เอง

### ขั้นที่ 2: apply -k

```bash
kubectl apply -k kz && kubectl rollout status deploy/kz-web --timeout=120s
kubectl get deploy kz-web -o jsonpath='{.spec.template.spec.containers[0].envFrom}'; echo; kubectl exec deploy/kz-web -- printenv announcement.txt
```

```text
configmap/web-config-gh5tkgmddg created
deployment.apps/kz-web created
Waiting for deployment "kz-web" rollout to finish: 0 of 1 updated replicas are available...
deployment "kz-web" successfully rolled out
[{"configMapRef":{"name":"web-config-gh5tkgmddg"}}]
ประกาศ v1

```

(บรรทัดว่างท้ายมาจาก newline ในไฟล์ `announcement.txt`)

### ขั้นที่ 3: แก้เนื้อหาแล้ว apply อีกครั้ง

```bash
printf 'ประกาศ v2\n' > kz/announcement.txt; kubectl apply -k kz && kubectl rollout status deploy/kz-web --timeout=120s
kubectl get cm | grep web-config; kubectl rollout history deploy/kz-web
kubectl exec deploy/kz-web -- printenv announcement.txt SHOP_NAME
```

```text
configmap/web-config-6db7mkcg8t created
deployment.apps/kz-web configured
Waiting for deployment "kz-web" rollout to finish: 1 old replicas are pending termination...
Waiting for deployment "kz-web" rollout to finish: 1 old replicas are pending termination...
deployment "kz-web" successfully rolled out
web-config-6db7mkcg8t   2      1s
web-config-gh5tkgmddg   2      2s
deployment.apps/kz-web 
REVISION  CHANGE-CAUSE
1         <none>
2         <none>

ประกาศ v2

ร้านน้องส้ม
```

- เนื้อหาเปลี่ยน → ชื่อใหม่ `web-config-6db7mkcg8t` → Deployment `configured` และ rollout เป็น REVISION 2 **โดยไม่ต้องสั่ง restart**
- Pod ใหม่เห็น `ประกาศ v2` ทันทีที่เริ่ม (env ของ Pod ใหม่)
- ConfigMap รุ่นเก่า `web-config-gh5tkgmddg` **ยังอยู่** ถ้า `rollout undo` ก็จะกลับไปใช้ตัวเก่าได้ทันที

> ใช้ `printf` แทนการแก้ด้วย editor เพื่อให้เนื้อไฟล์ตรงทุกไบต์ (hash ขึ้นกับทุกไบต์รวม newline ท้ายไฟล์) ไฟล์เหมือนกันจะได้ชื่อ `gh5tkgmddg` / `6db7mkcg8t` ตรงกับเอกสารทุกเครื่อง

### ขั้นที่ 4: delete -k ไม่ลบรุ่นเก่า แล้วเก็บกวาด

```bash
kubectl delete -k kz; kubectl get cm | grep web-config
kubectl get cm -o name | grep web-config | xargs -r kubectl delete; printf 'ประกาศ v1\n' > kz/announcement.txt; kubectl get cm,deploy
```

```text
configmap "web-config-6db7mkcg8t" deleted from default namespace
deployment.apps "kz-web" deleted from default namespace
web-config-gh5tkgmddg   2      3s
configmap "web-config-gh5tkgmddg" deleted from default namespace
NAME                         DATA   AGE
configmap/kube-root-ca.crt   1      26m
```

`kubectl delete -k kz` ลบเฉพาะชื่อที่ kustomize สร้างจากไฟล์ปัจจุบัน ตัวเก่าค้างต้องลบเอง และคืน `announcement.txt` เป็น `ประกาศ v1` ไว้สำหรับทำซ้ำ

### สิ่งที่เห็น

- `configMapGenerator` สร้าง `web-config-<hash>` และแก้ชื่อใน Deployment ให้ตรง
- แก้เนื้อหา → hash ใหม่ → Deployment rollout เอง (REVISION 2) แบบเดียวกับการตั้งชื่อใหม่ด้วยมือ แต่ไม่ต้องจำ
- ConfigMap รุ่นเก่าค้างทั้งหลัง apply และหลัง `delete -k` ต้องลบเอง

**คำถามชวนคิด**

1. ถ้าลืม `printf 'ประกาศ v1\n' > kz/announcement.txt` แล้วทำ LAB นี้ซ้ำ ชื่อ ConfigMap ในขั้นที่ 1 จะเป็นอะไร
2. ข้อดีของการที่ ConfigMap รุ่นเก่ายังค้างอยู่ มีผลต่อ `kubectl rollout undo` อย่างไร
