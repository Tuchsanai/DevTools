
---

## 8. การอัปเดต ConfigMap

เมื่อแก้ ConfigMap (`kubectl apply`, `kubectl patch`, `kubectl edit`) API server เปลี่ยนค่าทันที แต่ "Pod เห็นค่าใหม่เมื่อไร" ขึ้นกับว่า Pod อ่านค่าทางไหน และแอปอ่านค่าอย่างไร นี่คือหัวข้อที่ผู้เริ่มต้นสับสนมากที่สุดของบทนี้

### 8.1 env ไม่เปลี่ยนจนกว่าจะได้ Pod ใหม่

{{FIG:T26}}

env ถูกคัดลอกเข้า process ตอน container เริ่ม (ป้ายติดอกตอนเข้ากะ) หลังจากนั้นไม่มีใครไปแก้ env ของ process ที่รันอยู่ได้ ผลจริง

- LAB 6: patch `shop-config` 3 รอบ (`SHOP_NAME=ร้านใหม่1/2/3`) env `SHOP_NAME` ใน `envpod` ยังเป็น `ร้านน้องส้ม` ทุกรอบ
- LAB 10 ขั้น C1: apply ConfigMap ชื่อร้านใหม่ ธีม sunset และโปรโมชัน แล้วรอ 90 วินาที `/api/shop` ของทั้ง 3 Pod ยังเป็น `"shopName":"ร้านอาหารแมวน้องส้ม","theme":"harbor","promo":""` และ `RESTARTS 0`

ถ้าอยากให้ค่าใหม่มีผล ต้องได้ **Pod ใหม่** (container restart เฉย ๆ ภายใน Pod เดิมก็ได้ค่าใหม่เหมือนกัน แต่ไม่ควรพึ่งวิธีนั้น) ซึ่ง Deployment ทำให้ได้อย่างปลอดภัยด้วย rolling update (หัวข้อ 8.5)

### 8.2 volume อัปเดตเอง แต่ช้าราว 1 นาที

{{FIG:T27}}

ไฟล์จาก volume ถูกดูแลโดย **kubelet** บน Node ที่ Pod อยู่ kubelet จะ sync volume ของ Pod เป็นรอบ ๆ (ค่าเริ่มต้น `syncFrequency` 1 นาที) และอ่านค่า ConfigMap ผ่าน cache ของตัวเอง เวลาตั้งแต่แก้ ConfigMap จนไฟล์เปลี่ยนจึง **ไม่ทันที** แต่ไม่ต้อง restart Pod ค่าที่วัดได้จริงในบทนี้

| การทดลอง | เวลาที่ไฟล์เปลี่ยน (วินาที) |
|---|---|
| LAB 6 busybox `/etc/all/announcement.txt` (3 รอบ) | 85 / 55 / 62 |
| LAB 7 nginx `/etc/nginx/conf.d/default.conf` (v2, v3) | 75 / 63 |
| LAB 4 optional volume สร้าง ConfigMap ทีหลัง (3 รอบ) | 61 / 64 / 43 |
| LAB 10 ร้าน `/api/announcement` Pod แรกเห็น (3 รอบ) | 37 / 63 / 59 |
| LAB 10 ร้าน ครบทุก Pod 12/12 (3 รอบ) | 48 / 82 / 88 |

สรุป: **ราว 1 นาที บางครั้งเกือบ 1.5 นาที** และแต่ละ Pod (คนละ Node) เห็นค่าใหม่ไม่พร้อมกัน ระหว่างนั้นลูกค้าที่ refresh อาจเจอ Pod ที่ยังเป็นข้อความเก่า อย่าเพิ่งสรุปว่า "ไม่ทำงาน" ก่อนรอครบ 2 นาที

### 8.3 เบื้องหลัง: ..data symlink สลับทีเดียว

{{FIG:T28}}

ทำไมไฟล์ใน volume ถึงเป็น symlink? เพราะ kubelet ต้องเปลี่ยน **ทุกไฟล์พร้อมกัน** โดยไม่ให้แอปอ่านเจอสภาพครึ่งเก่าครึ่งใหม่ ขั้นตอนคือ

1. เขียนค่าชุดใหม่ทั้งหมดลงโฟลเดอร์ใหม่ชื่อเวลา เช่น `..2026_10_05_09_56_42.2491344353`
2. สลับ symlink `..data` ให้ชี้โฟลเดอร์ใหม่ในการ rename ครั้งเดียว (atomic)
3. ลบโฟลเดอร์ชุดเก่า

ไฟล์ที่แอปเห็น (`announcement.txt -> ..data/announcement.txt`) ไม่ต้องแก้เลย เพราะชี้ผ่าน `..data` อยู่แล้ว ผลจริงท้าย LAB 6: ไฟล์ symlink ยังเป็นเวลาเดิม `09:53` แต่ `..data` ชี้โฟลเดอร์เวลาใหม่

```text
lrwxrwxrwx    1 root     root            32 Oct  5 09:56 ..data -> ..2026_10_05_09_56_42.2491344353
lrwxrwxrwx    1 root     root            23 Oct  5 09:53 announcement.txt -> ..data/announcement.txt
```

ผลข้างเคียงที่ควรรู้: โปรแกรมที่ "เฝ้าไฟล์" (เช่น inotify) ต้องเฝ้าการเปลี่ยนของโฟลเดอร์/`..data` ไม่ใช่ inode ของไฟล์เดิม และ `subPath` ใช้กลไกนี้ไม่ได้ (เป็นไฟล์จริงที่ bind mount ตอนเริ่ม) จึงไม่อัปเดต

### 8.4 ไฟล์เปลี่ยนแล้ว แต่แอปต้องอ่านใหม่เอง

{{FIG:T29}}

kubelet เปลี่ยน "ไฟล์" ให้ แต่ไม่รู้ว่าแอปอ่านไฟล์เมื่อไร โปรแกรมจำนวนมาก (nginx, postgres, Java หลายตัว) **อ่านไฟล์ตั้งค่าครั้งเดียวตอนเริ่ม** ผลจริงใน LAB 7 (Pod `ngx` mount `nginx-conf` ที่ `/etc/nginx/conf.d`)

```text
$ kubectl exec ngx -- cat /etc/nginx/conf.d/default.conf; kubectl exec ngx -- curl -s 127.0.0.1/
server { listen 80; location / { default_type text/plain; return 200 "menu v2\n"; } }
menu v1
$ kubectl exec ngx -- nginx -s reload; sleep 1; kubectl exec ngx -- curl -s 127.0.0.1/
2026/10/05 10:07:20 [notice] 310#310: signal process started
menu v2
```

ไฟล์เป็น v2 แล้วแต่ nginx ยังตอบ `menu v1` จนกว่าจะสั่ง `nginx -s reload` ทางเลือกของแอปที่อ่านไฟล์จาก ConfigMap

| วิธี | ตัวอย่าง |
|---|---|
| แอปอ่านไฟล์ใหม่ทุกครั้งที่ใช้ | ร้านน้องส้ม 1.5 อ่าน `/etc/som/announcement.txt` ทุก request (`fs.readFileSync`) ประกาศจึงเปลี่ยนเองโดยไม่ restart |
| แอปเฝ้าไฟล์แล้ว reload ตัวเอง | CoreDNS มี plugin `reload` ใน `Corefile` |
| มีคน/sidecar สั่ง reload | `nginx -s reload`, ส่งสัญญาณ `SIGHUP` |
| สร้าง Pod ใหม่ | `kubectl rollout restart` หรือ checksum annotation (หัวข้อถัดไป) |

### 8.5 ให้ Pod ใหม่รับค่า: rollout restart, checksum และชื่อใหม่

{{FIG:T30}}

สำหรับค่าที่ส่งเป็น env หรือแอปที่ไม่ reload เอง วิธีที่ปลอดภัยคือให้ Deployment สร้าง Pod ใหม่ทีละตัวด้วย rolling update (บทที่ 7) ซึ่งต้อง **เปลี่ยน Pod template** อย่างใดอย่างหนึ่ง

**1) `kubectl rollout restart`** — kubectl เติม annotation `kubectl.kubernetes.io/restartedAt` ใน template ให้ ผลจริงใน LAB 7

```text
{"kubectl.kubernetes.io/restartedAt":"2026-10-05T17:08:34+07:00"}
```

หลัง restart Deployment `plain` ตอบ `menu v3` ทันที (ก่อนหน้านั้นไฟล์เป็น v3 แต่ตอบ `menu v1`) ข้อเสียคือต้องจำไปสั่งเองทุกครั้งที่แก้ config และ `rollout history` ไม่ได้บันทึกว่าเปลี่ยนเพราะอะไร (ใน LAB 10 CHANGE-CAUSE ซ้ำข้อความเดิมทุก revision)

**2) checksum annotation** — ใส่ hash ของเนื้อหา config ไว้ใน annotation ของ template แก้ config → hash เปลี่ยน → template เปลี่ยน → rollout เอง เป็นรูปแบบที่ Helm แนะนำ (`checksum/config`) ผลจริงใน LAB 7

```bash
SUM=$(kubectl get cm nginx-conf -o jsonpath='{.data}' | sha256sum | cut -c1-12); echo $SUM
kubectl patch deploy plain -p "{\"spec\":{\"template\":{\"metadata\":{\"annotations\":{\"checksum/config\":\"$SUM\"}}}}}"
```

```text
a7aed9955c80
deployment.apps/plain patched
...
REVISION  CHANGE-CAUSE
1         <none>
2         <none>
3         <none>
```

ในไฟล์ YAML จะหน้าตาแบบนี้ (เครื่องมืออย่าง Helm คำนวณค่าให้ตอน render)

```yaml
spec:
  template:
    metadata:
      annotations:
        checksum/config: a7aed9955c80
```

**3) ตั้งชื่อ ConfigMap ใหม่ทุกครั้ง** (`som-web-config-v2`) แล้วแก้ชื่อใน Deployment ชื่อที่อ้างอยู่ใน template จึง rollout เอง ย้อนรุ่นด้วย `rollout undo` ก็ได้ ConfigMap ชุดเก่ากลับมาด้วย (LAB 10 ขั้น E) ใช้คู่กับ `immutable` ได้ดี และเป็นสิ่งที่ kustomize `configMapGenerator` ทำให้อัตโนมัติ (หัวข้อ 10)

| วิธี | rollout อัตโนมัติ | ย้อนรุ่นได้ค่าเก่า | ต้องทำอะไรเพิ่ม |
|---|:---:|:---:|---|
| `rollout restart` | ❌ ต้องสั่งเอง | ❌ (ConfigMap ถูกแก้ทับแล้ว) | จำไปสั่ง |
| checksum annotation | ✅ เมื่อ apply template ใหม่ | ❌ | คำนวณ hash (Helm ทำให้) |
| ชื่อใหม่ / generator | ✅ | ✅ (ConfigMap เก่ายังอยู่) | ลบ ConfigMap รุ่นเก่าเอง |

---

## 9. immutable: ConfigMap ที่แก้ไม่ได้

{{FIG:T31}}

ตั้ง `immutable: true` ที่ระดับบนสุดของ ConfigMap (ไม่ใช่ใต้ `data`) ไฟล์ `02_LAB/labs/lab08-immutable/frozen.yaml`

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: frozen
immutable: true
data:
  PRICE: "99"
```

ผลจริงใน LAB 8 ทุกวิธีที่แตะ `data` หรือพยายามปิด immutable ถูกปฏิเสธ

```text
$ kubectl patch cm frozen --type merge -p '{"data":{"PRICE":"79"}}'
The ConfigMap "frozen" is invalid: data: Forbidden: field is immutable when `immutable` is set
$ kubectl patch cm frozen --type merge -p '{"immutable":false}'
The ConfigMap "frozen" is invalid: immutable: Forbidden: field is immutable when `immutable` is set
$ sed 's/"99"/"79"/' frozen.yaml | kubectl replace -f -
The ConfigMap "frozen" is invalid: data: Forbidden: field is immutable when `immutable` is set
$ kubectl label cm frozen tier=menu; kubectl get cm frozen --show-labels
configmap/frozen labeled
NAME     DATA   AGE   LABELS
frozen   1      1s    tier=menu
```

- แก้ `data`/`binaryData` ไม่ได้ และเปลี่ยน `immutable` กลับเป็น `false` ไม่ได้
- แก้ **metadata** (label, annotation) ได้
- อยากเปลี่ยนค่า: **ลบแล้วสร้างใหม่** (`kubectl delete cm frozen` แล้ว apply ไฟล์ใหม่ → `79 true`) หรือ **สร้างชื่อใหม่** (`frozen-v2`) แล้วชี้ Deployment ไปชื่อใหม่ (วิธีที่แนะนำ เพราะ Pod เดิมยังอ้างของเดิมได้ระหว่าง rollout)

ข้อดีของ immutable

1. **กันแก้พลาด** ค่าที่ระบบจริงใช้อยู่ถูกเปลี่ยนกลางทางไม่ได้ แอปทุก Pod เห็นค่าชุดเดียวกันแน่นอน
2. **ลดภาระ API server** kubelet ไม่ต้องคอยเฝ้า (watch) ConfigMap ที่ immutable เพราะรู้ว่าไม่มีวันเปลี่ยน คลัสเตอร์ที่มี ConfigMap ใช้งานจำนวนมากได้ประโยชน์ชัดเจน

---

## 10. kustomize configMapGenerator

{{FIG:T32}}

kubectl มี **kustomize** ติดมาในตัว (`kubectl kustomize`, `kubectl apply -k`) ความสามารถเด่นที่เกี่ยวกับบทนี้คือ `configMapGenerator` ซึ่งสร้าง ConfigMap จาก literal/ไฟล์ แล้ว **ต่อท้ายชื่อด้วย hash ของเนื้อหา** พร้อมแก้ชื่อที่ Deployment อ้างถึงให้ตรงเอง ไฟล์ `02_LAB/labs/lab09-kustomize/kz/kustomization.yaml`

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

`deploy.yaml` อ้างชื่อสั้น `web-config` แต่ `kubectl kustomize kz` (ดูผลโดยไม่ apply) ได้ผลจริง

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
...
        envFrom:
        - configMapRef:
            name: web-config-gh5tkgmddg
```

เมื่อแก้ `announcement.txt` เป็น `ประกาศ v2` แล้ว `kubectl apply -k kz` อีกครั้ง

```text
configmap/web-config-6db7mkcg8t created
deployment.apps/kz-web configured
```

- เนื้อหาเปลี่ยน → hash เปลี่ยน → ชื่อใหม่ → template ของ Deployment เปลี่ยน → **rollout เอง** (REVISION 1 → 2) และ `rollout undo` ได้ค่าเก่าคืนด้วย
- hash คำนวณจากเนื้อหาทุกไบต์ ไฟล์เหมือนกันทุกไบต์ได้ชื่อเดียวกันทุกเครื่อง (`web-config-gh5tkgmddg` ในเอกสารนี้) แต่ถ้า editor เติม/ลบ newline ท้ายไฟล์จะได้ hash อื่น
- **ConfigMap รุ่นเก่าค้างอยู่** และ `kubectl delete -k kz` ลบเฉพาะชื่อล่าสุด ต้องลบรุ่นเก่าเอง (ใน GitOps มักใช้ระบบ prune ช่วย)
- ปิดการเติม hash ได้ด้วย `generatorOptions: disableNameSuffixHash: true` แต่จะเสียข้อดีเรื่อง rollout อัตโนมัติ
- kustomize มี `secretGenerator` ที่ทำงานแบบเดียวกันสำหรับ Secret (บทที่ 11)

---

## 11. ConfigMap ในคลัสเตอร์จริง ข้าม namespace และ RBAC

### 11.1 ระบบเองก็ใช้ ConfigMap

{{FIG:T33}}

คลัสเตอร์ kind ใหม่มี ConfigMap อยู่แล้ว 13 ตัว (ผลจริง `kubectl get cm -A` ใน LAB 1)

```text
NAMESPACE            NAME                                                   DATA   AGE
default              kube-root-ca.crt                                       1      3m56s
kube-node-lease      kube-root-ca.crt                                       1      3m56s
kube-public          cluster-info                                           2      4m3s
kube-public          kube-root-ca.crt                                       1      3m56s
kube-system          coredns                                                1      4m3s
kube-system          extension-apiserver-authentication                     6      4m5s
kube-system          kube-apiserver-legacy-service-account-token-tracking   1      4m5s
kube-system          kube-proxy                                             2      4m2s
kube-system          kube-root-ca.crt                                       1      3m56s
kube-system          kubeadm-config                                         1      4m3s
kube-system          kubelet-config                                         1      4m3s
local-path-storage   kube-root-ca.crt                                       1      3m56s
local-path-storage   local-path-config                                      4      4m1s
```

| ConfigMap | ใช้ทำอะไร |
|---|---|
| `kube-system/coredns` | key `Corefile` = ไฟล์ตั้งค่า DNS ของคลัสเตอร์ (บทที่ 6) mount เป็น volume ให้ Pod CoreDNS และมี plugin `reload` อ่านไฟล์ใหม่เอง |
| `kube-system/kube-proxy` | `config.conf` และ `kubeconfig.conf` ของ kube-proxy ทุก Node (DATA 2) |
| `kube-system/kubelet-config`, `kubeadm-config` | ค่าตั้งค่าที่ kubeadm ใช้ตอนสร้าง/เพิ่ม Node |
| `kube-public/cluster-info` | ข้อมูลสาธารณะของคลัสเตอร์ที่ใช้ตอนเข้าร่วมคลัสเตอร์ |
| `local-path-storage/local-path-config` | ค่าตั้งค่าของ local-path provisioner ที่สร้าง PV ให้ในบทที่ 8 (DATA 4) |
| `kube-root-ca.crt` (ทุก namespace) | ใบรับรอง CA ของคลัสเตอร์ (`ca.crt`) ที่ระบบสร้างให้ทุก namespace อัตโนมัติ Pod ใช้ตรวจว่ากำลังคุยกับ API server ตัวจริง |

ตัวอย่าง `Corefile` (ผลจริง `kubectl -n kube-system get cm coredns -o jsonpath='{.data.Corefile}'` ตัดบางส่วน)

```text
.:53 {
    errors
    health {
       lameduck 5s
    }
    ready
    kubernetes cluster.local in-addr.arpa ip6.arpa {
       pods insecure
       fallthrough in-addr.arpa ip6.arpa
       ttl 30
    }
    ...
    loop
    reload
    loadbalance
}
```

> ConfigMap ใน `kube-system` เป็น "กระดานของฝ่ายท่าเรือ" ดูเพื่อเรียนรู้ได้ แต่ **อย่าแก้หรือลบ** ในคลัสเตอร์ของวิชานี้ เพราะ DNS หรือ kube-proxy อาจพังทั้งคลัสเตอร์

### 11.2 อ้างข้าม namespace ไม่ได้

{{FIG:T34}}

`configMapRef`/`configMapKeyRef`/volume `configMap` มีแค่ `name` Kubernetes จึงหาใน namespace ของ Pod เสมอ ไฟล์ `02_LAB/labs/lab04-missing/other-ns.yaml` สร้าง Pod `x` ใน namespace `other` ที่อ้าง `shop-config` (ซึ่งอยู่ใน `default`) ผลจริง

```text
NAME   READY   STATUS                       RESTARTS   AGE
x      0/1     CreateContainerConfigError   0          12s
  Warning  Failed     11s (x2 over 11s)  kubelet            spec.containers{c}: Error: configmap "shop-config" not found
```

ข้อความบอกว่า "not found" ทั้งที่ `shop-config` มีอยู่จริงในอีก namespace นี่คือการแยกโซนของบทที่ 4 ทางแก้คือ **สร้างสำเนา ConfigMap ใน namespace ที่ใช้** (apply ไฟล์เดียวกันด้วย `-n <ns>` หรือใช้ kustomize สร้างให้หลาย namespace) ซึ่งก็สอดคล้องกับหลักที่แต่ละ environment มีค่าของตัวเอง

### 11.3 RBAC: สิทธิ์อ่านกับสิทธิ์แก้แยกกัน

{{FIG:T35}}

ConfigMap เป็น resource `configmaps` ใน API group หลัก (`""`) กำหนดสิทธิ์ด้วย Role/RoleBinding แบบบทที่ 4 ได้ทุกคำกริยา (`get`, `list`, `watch`, `create`, `update`, `patch`, `delete`) ผลจริงจากการทดลองก่อนเขียน LAB: ServiceAccount `reader` ที่มี Role `get,list configmaps` ใน `default`

```text
$ kubectl create role cm-reader --verb=get,list --resource=configmaps
role.rbac.authorization.k8s.io/cm-reader created
$ kubectl auth can-i get configmaps --as=system:serviceaccount:default:reader
yes
$ kubectl auth can-i update configmaps --as=system:serviceaccount:default:reader
no
$ kubectl patch cm shop-config --as=system:serviceaccount:default:reader --type merge -p '{"data":{"a":"b"}}'
Error from server (Forbidden): configmaps "shop-config" is forbidden: User "system:serviceaccount:default:reader" cannot patch resource "configmaps" in API group "" in the namespace "default"
$ kubectl -n other get cm --as=system:serviceaccount:default:reader
Error from server (Forbidden): configmaps is forbidden: User "system:serviceaccount:default:reader" cannot list resource "configmaps" in API group "" in the namespace "other"
```

- อ่านได้ แต่แก้ไม่ได้ — ให้สิทธิ์ `patch/update` เฉพาะคนที่ดูแล config จริง ๆ เพราะการแก้ ConfigMap = การเปลี่ยนพฤติกรรมของแอป (ไฟล์ใน volume เปลี่ยนเองภายใน 1 นาที)
- Role อยู่ใน namespace เดียว อ่านใน namespace อื่นไม่ได้
- กลับกัน **คนที่อ่าน ConfigMap ได้ อ่านทุกค่าในนั้นได้** RBAC แบ่งระดับ "ทั้ง object" (หรือรายชื่อด้วย `resourceNames`) ไม่ได้แบ่งราย key นี่คืออีกเหตุผลที่ห้ามใส่ความลับใน ConfigMap

---

## 12. แนวปฏิบัติและสรุป

### 12.1 เลือก env, volume หรือ subPath

{{FIG:T36}}

| | env / envFrom | volume (ทั้งโฟลเดอร์ หรือ `items`) | subPath |
|---|---|---|---|
| เหมาะกับ | ค่าสั้น ๆ ชื่อ UPPER_SNAKE_CASE (ชื่อร้าน, ธีม, โปรโมชัน) | ไฟล์ตั้งค่า, ข้อความยาว, ไฟล์ไบนารี (`nginx.conf`, `announcement.txt`) | ไฟล์เดียวที่ต้องวางในโฟลเดอร์ที่มีไฟล์อื่นของ image |
| แอปอ่านอย่างไร | `process.env`, `$VAR` | อ่านไฟล์ | อ่านไฟล์ |
| แก้ ConfigMap แล้ว | ❌ ไม่เปลี่ยน ต้องได้ Pod ใหม่ | ✅ ไฟล์เปลี่ยนเองราว 1 นาที แต่แอปต้องอ่านใหม่ | ❌ ไม่เปลี่ยน ต้องได้ Pod ใหม่ |
| `binaryData` | ❌ ไม่ถูกนำไปเป็น env | ✅ | ✅ |
| ConfigMap ไม่มี | `CreateContainerConfigError` | ค้าง `ContainerCreating` (`FailedMount`) | ค้าง `ContainerCreating` |
| ร้านน้องส้ม LAB 10 | `som-web-config` (ชื่อร้าน, ธีม, โปรโมชัน) | `som-announcement` (ประกาศหน้าร้าน) | ไม่ใช้ |

### 12.2 แนวปฏิบัติ

{{FIG:T37}}

1. **เก็บ ConfigMap เป็น YAML ใน git** คู่กับ Deployment ตรวจย้อนหลังได้ว่าใครเปลี่ยนค่าเมื่อไร (ใช้ `--dry-run=client -o yaml` ช่วยเขียน) หลีกเลี่ยง `kubectl edit` บนระบบจริงเพราะไฟล์ใน git จะไม่ตรงกับคลัสเตอร์
2. **ตั้งชื่อ key ให้ชัดและเหมาะกับวิธีใช้** key ที่เป็น env ใช้ `UPPER_SNAKE_CASE` key ที่เป็นไฟล์ใช้ชื่อไฟล์จริง (`announcement.txt`)
3. **ไม่ใส่ความลับ** รหัสผ่าน token key ใช้ Secret (บทที่ 11)
4. **ค่าที่ไม่ควรเปลี่ยนกลางทางใช้ชื่อมีเวอร์ชัน + `immutable: true`** (`som-web-config-v2`) เปลี่ยนค่า = สร้างรุ่นใหม่ + ชี้ Deployment ไปชื่อใหม่ ย้อนรุ่นได้
5. **ทำให้ config เปลี่ยนแล้ว rollout เสมอ** ด้วย checksum annotation หรือ `configMapGenerator` แทนการจำไปสั่ง `rollout restart`
6. **ถ้าใช้ volume ให้แอปรองรับการอ่านไฟล์ใหม่** (อ่านทุกครั้ง หรือ reload เมื่อไฟล์เปลี่ยน) และอย่าใช้ subPath กับไฟล์ที่ตั้งใจให้อัปเดตเอง
7. **ใช้ `optional: true` เฉพาะค่าที่ไม่จำเป็นจริง** ค่าจำเป็นปล่อยให้ Pod ค้างเพื่อให้เห็นปัญหา
8. **อย่าใส่ `$(VAR)` ในค่าของ ConfigMap ที่ใช้ผ่าน envFrom** ค่าที่ต้องอ้างตัวแปรให้ตั้งใน `env` ของ Deployment
9. **จำกัดสิทธิ์ `update/patch configmaps`** ให้เฉพาะคนดูแล config
10. **ConfigMap เล็กและแยกตามหน้าที่** เช่น ป้ายร้าน (env) แยกจากประกาศ (volume) แทนกระดานเดียวที่ใหญ่และใช้ทั้งสองแบบปนกัน

### 12.3 สรุปเส้นทางของบท

{{FIG:T38}}

| ขั้น | สิ่งที่เรียน | ข้อควรจำ |
|---|---|---|
| สร้าง | `--from-literal`, `--from-file`, `--from-env-file`, YAML, `--dry-run=client -o yaml` | ≤ 1 MiB, namespaced, `data` = UTF-8, `binaryData` = base64 |
| ใช้ | `configMapKeyRef`, `envFrom` (+`prefix`), `$(VAR)`, volume, `items`, `defaultMode`, `subPath` | env ชนะ envFrom, `$(VAR)` ในค่าจาก envFrom ไม่แทน, volume read-only |
| อัปเดต | env ต้อง Pod ใหม่, volume ราว 1 นาที (`..data`), แอปต้อง reload, `rollout restart`, checksum, ชื่อใหม่/generator | subPath ไม่อัปเดต |
| ป้องกัน | `immutable`, RBAC, `optional`, ไม่ใส่ความลับ | แก้ immutable ไม่ได้ ต้องสร้างใหม่ |

### 12.4 Cheatsheet คำสั่ง

{{FIG:T39}}

| งาน | คำสั่ง |
|---|---|
| สร้างจากค่า | `kubectl create configmap demo --from-literal=SHOP_NAME=ร้านน้องส้ม` |
| สร้างจากไฟล์ / ไฟล์ env | `kubectl create configmap files --from-file=announcement.txt` / `--from-env-file=shop.env` |
| เขียน YAML ให้ | `kubectl create configmap dir --from-file=. --dry-run=client -o yaml > cm.yaml` |
| อัปเดตจากคำสั่ง create | `kubectl create configmap demo ... --dry-run=client -o yaml \| kubectl apply -f -` |
| ดู | `kubectl get cm`, `kubectl get cm demo -o yaml`, `kubectl describe cm demo`, `kubectl get cm demo -o jsonpath='{.data}'` |
| แก้บางค่า | `kubectl patch cm shop-config --type merge -p '{"data":{"SHOP_NAME":"..."}}'` |
| แก้ใน editor | `kubectl edit cm demo` (เปิด vim ต้องใช้ใน terminal ที่โต้ตอบได้ ออกโดยไม่บันทึกด้วย `:q!`) |
| ให้ Deployment ได้ค่าใหม่ | `kubectl rollout restart deploy/<ชื่อ>` |
| kustomize | `kubectl kustomize <dir>` (ดู), `kubectl apply -k <dir>`, `kubectl delete -k <dir>` |
| ดูค่าที่ Pod เห็น | `kubectl exec <pod> -- printenv`, `kubectl exec <pod> -- ls -la /etc/som` |
| ตรวจสิทธิ์ | `kubectl auth can-i get configmaps --as=system:serviceaccount:<ns>:<sa>` |

### 12.5 ปัญหาที่ยังเหลือ: รหัสผ่านใน YAML

{{FIG:T40}}

ท้าย LAB 10 ร้านน้องส้มเปลี่ยนชื่อร้าน ธีม โปรโมชัน และประกาศได้โดยไม่ build image ใหม่แล้ว แต่ **รหัสผ่านฐานข้อมูล `som:meow1234` ยังเขียนตรงอยู่ในไฟล์ YAML** ทั้ง `DATABASE_URL` ใน `k8s/20-web.yaml` (container `web` และ init container `db-seed`) และ `POSTGRES_PASSWORD` ใน `k8s/10-db.yaml` ของ StatefulSet

LAB 10 ขั้น F ทดลองให้ ServiceAccount `intern` ที่มีสิทธิ์แค่ "ดู" Pod, ConfigMap, Deployment และ StatefulSet ใน `som-shop` (ไม่มีสิทธิ์ดู secrets เลย) ลองอ่าน ผลจริง

```text
$ kubectl -n som-shop get deploy som-web -o yaml --as=system:serviceaccount:som-shop:intern | grep -o 'som:[a-z0-9]*@' | sort | uniq -c
      4 som:meow1234@
$ kubectl -n som-shop get sts som-db -o yaml --as=system:serviceaccount:som-shop:intern | grep -A1 -- '- name: POSTGRES_PASSWORD'
        - name: POSTGRES_PASSWORD
          value: meow1234
```

intern เห็นรหัสผ่าน 4 ที่ใน Deployment (2 ใน spec ของ `web` กับ `db-seed` และอีก 2 ในบรรทัด annotation `last-applied-configuration`) และเห็นใน StatefulSet/Pod ของ db ด้วย ถ้าย้ายรหัสไปไว้ใน ConfigMap ก็ไม่ช่วย เพราะ intern มีสิทธิ์อ่าน ConfigMap และ ConfigMap เป็นข้อความธรรมดา (หัวข้อ 3.4) สิ่งที่ต้องการคือ object แยกสำหรับความลับ ที่ให้สิทธิ์อ่านแยกจาก ConfigMap/Deployment ได้ ใส่เข้า Pod เป็น env หรือไฟล์ได้แบบเดียวกับที่เรียนในบทนี้ และมีตัวเลือกด้านความปลอดภัยเพิ่ม นั่นคือ **Secret — ซองปิดผนึก** ในบทที่ 11

### ข้อควรจำของบทนี้

- ConfigMap = กระดาน key–value ของ namespace สำหรับค่าที่ไม่ลับ ขนาดรวม ≤ 1 MiB
- env/envFrom อ่านครั้งเดียวตอนเริ่ม → แก้ ConfigMap แล้วต้อง rollout (`rollout restart`, checksum, ชื่อใหม่)
- volume อัปเดตเองราว 1 นาที (วัดได้ 37–88 วินาที) ผ่าน `..data` symlink แต่แอปต้องอ่านไฟล์ใหม่เอง และ subPath ไม่อัปเดต
- env ชนะ envFrom และ `$(VAR)` ในค่าที่มาจาก envFrom ไม่ถูกแทนค่า
- อ้าง ConfigMap/key ที่ไม่มี → `CreateContainerConfigError` (env) หรือ `ContainerCreating` + `FailedMount` (volume) สร้าง ConfigMap ภายหลังแล้ว Pod เริ่มเอง
- อ้างข้าม namespace ไม่ได้ (`configmap "shop-config" not found`)
- `immutable: true` แก้ `data` ไม่ได้และปิดไม่ได้ ต้องสร้างใหม่/ชื่อใหม่
- `configMapGenerator` ต่อท้ายชื่อด้วย hash → เนื้อหาเปลี่ยน = rollout เอง แต่ ConfigMap เก่าค้าง

---

## 13. คำถามทบทวน

**1. ทำไมการฝังธีมหรือชื่อร้านไว้ใน image จึงขัดกับหลัก 12-factor และส่งผลต่อการทดสอบ/deploy อย่างไร**

<details>
<summary>แนวคำตอบ</summary>

12-factor ให้แยก config (สิ่งที่ต่างกันระหว่าง deploy) ออกจากโค้ด ถ้าฝังไว้ใน image ต้อง build image ต่อ environment หรือทุกครั้งที่เปลี่ยนค่า (build → kind load/push → rollout) image ที่ทดสอบผ่านใน test จึงไม่ใช่ image เดียวกับที่ขึ้น prod การย้ายค่าออกมาไว้ใน ConfigMap ทำให้ build ครั้งเดียวแล้วใช้ image เดียวกันทุกที่ เปลี่ยนแค่ค่าที่ส่งเข้าไปตอนรัน
</details>

**2. ข้อมูลต่อไปนี้ควรอยู่ที่ไหน: ชื่อร้าน, ไฟล์ `default.conf` ของ nginx, ตารางออเดอร์, รหัสผ่านฐานข้อมูล, รูปสินค้าขนาด 5 MB**

<details>
<summary>แนวคำตอบ</summary>

ชื่อร้าน → ConfigMap (env), `default.conf` → ConfigMap (volume), ตารางออเดอร์ → PVC ของฐานข้อมูล (ข้อมูลที่แอปเขียน), รหัสผ่าน → Secret (บทที่ 11) ไม่ใช่ ConfigMap, รูป 5 MB → image หรือ volume อื่น เพราะ ConfigMap ใหญ่ได้ไม่เกิน 1 MiB (ทดสอบแล้วได้ `Too long: may not be more than 1048576 bytes`)
</details>

**3. `--from-file=shop.env` กับ `--from-env-file=shop.env` ได้ ConfigMap ต่างกันอย่างไร**

<details>
<summary>แนวคำตอบ</summary>

`--from-file` ได้ key เดียวชื่อ `shop.env` ค่าคือเนื้อไฟล์ทั้งไฟล์ (รวมบรรทัด comment และ newline) ส่วน `--from-env-file` อ่านทีละบรรทัด `KEY=VALUE` เป็นหลาย key (`SHOP_NAME`, `SHOP_THEME`, `EMPTY`) ข้ามบรรทัดที่ขึ้นต้นด้วย `#` และ `EMPTY=` ได้ค่าว่าง ผลจริง `{"EMPTY":"","SHOP_NAME":"ร้านน้องส้ม","SHOP_THEME":"sunset"}`
</details>

**4. สั่ง `kubectl create configmap demo ...` ซ้ำแล้วได้ `already exists` ถ้าต้องการอัปเดตด้วยคำสั่งเดิมควรทำอย่างไร และ Warning ที่ขึ้นครั้งแรกหมายความว่าอะไร**

<details>
<summary>แนวคำตอบ</summary>

ใช้ `kubectl create configmap demo ... --dry-run=client -o yaml | kubectl apply -f -` ให้ create สร้างแค่ YAML แล้ว apply อัปเดตของเดิม Warning `missing the kubectl.kubernetes.io/last-applied-configuration annotation` ขึ้นเพราะ object ถูกสร้างด้วย `create` ซึ่งไม่ได้บันทึก annotation ที่ apply ใช้เทียบ kubectl เติมให้เองแล้วครั้งต่อไปไม่เตือน
</details>

**5. Pod มี `args: ["$(SHOP_NAME)", "$(NOPE)"]` โดยมี env `SHOP_NAME` แต่ไม่มี `NOPE` ผลคืออะไร และใครเป็นคนแทนค่า**

<details>
<summary>แนวคำตอบ</summary>

ได้ `ร้านน้องส้ม` และ `$(NOPE)` (คงข้อความเดิม ไม่ error ไม่เป็นค่าว่าง) ผลจริง `ARGS: ร้านน้องส้ม $(NOPE)` Kubernetes (kubelet) เป็นคนแทนค่าก่อนเริ่ม container โดยดูจาก env ที่ประกาศใน container ไม่ใช่ shell และ spec ใน API server ยังเก็บเป็นข้อความ `$(SHOP_NAME)`
</details>

**6. ConfigMap มี `APP_THEME: sunset` และ Deployment ใช้ `envFrom` กับ ConfigMap นี้ พร้อมตั้ง `env: APP_THEME=harbor` ด้วย container เห็นค่าใด และถ้าใส่ `SHOP_FOOTER: "namespace $(POD_NAMESPACE)"` ใน ConfigMap จะเห็นอะไร**

<details>
<summary>แนวคำตอบ</summary>

เห็น `harbor` เพราะ env ชนะ envFrom เมื่อชื่อซ้ำ ส่วน `SHOP_FOOTER` จะเห็นข้อความดิบ `namespace $(POD_NAMESPACE)` เพราะ `$(VAR)` ในค่าที่มาจาก envFrom ไม่ถูกแทนค่า (LAB 10 ได้ `"footer":"LAB 010 · namespace $(POD_NAMESPACE)"`) แก้โดยตั้ง `SHOP_FOOTER` ใน `env` ของ Deployment ซึ่งแทนค่าได้และชนะ envFrom (ได้ `namespace som-shop`)
</details>

**7. ทำไม key `shop.name` ใช้เป็น env ได้ใน Kubernetes v1.37 แต่ `echo $CFG_shop.name` ใน shell ได้ `.name`**

<details>
<summary>แนวคำตอบ</summary>

Kubernetes รุ่นนี้ยอมให้ชื่อ env มีอักขระพิเศษได้ (ไม่ถูกข้ามและไม่มี event เตือน) แต่ shell ตีความชื่อตัวแปรได้เฉพาะตัวอักษร ตัวเลข และ `_` จึงอ่านแค่ `$CFG_shop` (ไม่มีค่า) แล้วต่อด้วย `.name` โปรแกรมหลายตัวมีข้อจำกัดเดียวกัน จึงควรตั้ง key ที่ใช้เป็น env เป็น `UPPER_SNAKE_CASE`
</details>

**8. mount ConfigMap ทั้งก้อนที่ `/etc/nginx/conf.d` เทียบกับ `subPath` ที่ `/etc/nginx/conf.d/default.conf` ต่างกันอย่างไรทั้งเรื่องไฟล์เดิมของ image และการอัปเดต**

<details>
<summary>แนวคำตอบ</summary>

mount ทั้งก้อนจะ **บังไฟล์เดิมทั้งโฟลเดอร์** เหลือแต่ไฟล์จาก ConfigMap (เป็น symlink ผ่าน `..data`) และอัปเดตเองราว 1 นาทีเมื่อแก้ ConfigMap ส่วน `subPath` วางไฟล์เดียว (ไฟล์จริง ไม่ใช่ symlink) โดยไม่บังไฟล์อื่นในโฟลเดอร์ แต่ **ไม่อัปเดตเลย** จนกว่าจะได้ Pod ใหม่ (LAB 6 subPath ยังเป็น `วันนี้ปลาทูสด` ทุกรอบ)
</details>

**9. `defaultMode: 400` (ไม่มี 0 นำหน้า) ใน YAML ต่างจาก `defaultMode: 0400` อย่างไร**

<details>
<summary>แนวคำตอบ</summary>

YAML ตีความ `0400` เป็นเลขฐานแปด (= 256 ฐานสิบ) ได้สิทธิ์ `-r--------` ตามต้องการ ส่วน `400` เป็นเลขฐานสิบ (= 0620 ฐานแปด) ได้สิทธิ์ `-rw--w----` ซึ่งไม่ใช่สิ่งที่ตั้งใจ ถ้าเขียนเป็น JSON ต้องใช้ฐานสิบ (`256`) เพราะ JSON ไม่มีเลขฐานแปด
</details>

**10. Pod `nocm` (envFrom อ้าง `not-here`), `nokey` (อ้าง key `NOPE` ใน `shop-config`) และ `novol` (volume อ้าง `not-here`) อยู่สถานะอะไร และหลังสร้าง ConfigMap `not-here` แล้วแต่ละตัวเป็นอย่างไร**

<details>
<summary>แนวคำตอบ</summary>

`nocm`, `nokey` = `CreateContainerConfigError` (`configmap "not-here" not found`, `couldn't find key NOPE in ConfigMap default/shop-config`) ส่วน `novol` ค้าง `ContainerCreating` พร้อม event `FailedMount` หลังสร้าง `not-here` kubelet ที่ลองใหม่อยู่ทำให้ `nocm` และ `novol` เป็น `Running` เองในราว 15 วินาที ส่วน `nokey` ยังค้าง เพราะต้นเหตุคือ key `NOPE` ใน `shop-config` ซึ่งยังไม่มี
</details>

**11. แก้ ConfigMap ที่ mount เป็น volume แล้วรอ 20 วินาที ไฟล์ยังไม่เปลี่ยน แปลว่าผิดพลาดหรือไม่ เกิดจากอะไร**

<details>
<summary>แนวคำตอบ</summary>

ไม่ผิด kubelet อัปเดต volume ตามรอบ sync (ค่าเริ่มต้นราว 1 นาที) และอ่านค่าผ่าน cache ในบทนี้วัดได้ 37–88 วินาที และแต่ละ Pod/Node เห็นไม่พร้อมกัน ให้รออย่างน้อย 1.5–2 นาทีก่อนสรุป ถ้ายังไม่เปลี่ยนให้ตรวจว่าไม่ได้ใช้ subPath และ ConfigMap ไม่ใช่ immutable ที่ถูกลบสร้างใหม่ด้วยชื่ออื่น
</details>

**12. ทำไมไฟล์ใน volume ของ ConfigMap จึงเป็น symlink ไปที่ `..data/...` แทนไฟล์ธรรมดา**

<details>
<summary>แนวคำตอบ</summary>

เพื่อให้อัปเดตทุกไฟล์แบบ atomic kubelet เขียนชุดใหม่ลงโฟลเดอร์ชื่อเวลา (`..2026_10_05_…`) แล้วสลับ symlink `..data` ให้ชี้โฟลเดอร์ใหม่ในครั้งเดียว แอปที่อ่านไฟล์จึงไม่เจอสภาพครึ่งเก่าครึ่งใหม่ และไม่ต้องแก้ symlink ของแต่ละไฟล์ (ชี้ผ่าน `..data` อยู่แล้ว)
</details>

**13. ไฟล์ `default.conf` ใน Pod nginx เปลี่ยนเป็น v2 แล้ว แต่ `curl` ยังได้ `menu v1` เพราะอะไร มีทางแก้อะไรบ้าง**

<details>
<summary>แนวคำตอบ</summary>

nginx อ่านไฟล์ตั้งค่าครั้งเดียวตอนเริ่ม kubelet เปลี่ยนไฟล์ได้แต่ไม่ได้บอกแอป ทางแก้: สั่ง `nginx -s reload` (หรือให้ sidecar สั่งเมื่อไฟล์เปลี่ยน), สร้าง Pod ใหม่ด้วย `kubectl rollout restart` หรือ checksum annotation, หรือออกแบบแอปให้อ่านไฟล์ใหม่ทุกครั้งแบบร้านน้องส้ม 1.5
</details>

**14. เปรียบเทียบ `kubectl rollout restart`, checksum annotation และการตั้งชื่อ ConfigMap ใหม่ (`-v2`) ในแง่ rollout อัตโนมัติและการย้อนรุ่น**

<details>
<summary>แนวคำตอบ</summary>

`rollout restart` ต้องสั่งเอง (เพิ่ม annotation `restartedAt`) และย้อนรุ่นไม่ได้ค่าเก่าเพราะ ConfigMap ถูกแก้ทับ checksum annotation rollout เองเมื่อ apply template ที่มี hash ใหม่ แต่ย้อนรุ่นก็ยังได้ ConfigMap ตัวเดิมที่ถูกแก้แล้ว การตั้งชื่อใหม่ (มือหรือ `configMapGenerator`) rollout เองเพราะชื่อใน template เปลี่ยน และ `rollout undo` ได้ค่าเก่าคืนเพราะ ConfigMap เก่ายังอยู่ แลกกับต้องลบ ConfigMap รุ่นเก่าเอง
</details>

**15. ConfigMap `immutable: true` แก้ได้อะไรบ้าง และถ้าต้องการเปลี่ยนค่าควรทำอย่างไร มีข้อดีอะไรนอกจากกันแก้พลาด**

<details>
<summary>แนวคำตอบ</summary>

แก้ได้เฉพาะ metadata (label, annotation) แก้ `data` หรือเปลี่ยน `immutable` เป็น false ไม่ได้ (``Forbidden: field is immutable when `immutable` is set``) เปลี่ยนค่าโดยลบแล้วสร้างใหม่ หรือดีกว่าคือสร้างชื่อใหม่ (`-v2`) แล้วชี้ Deployment ไปชื่อใหม่ ข้อดีอีกข้อคือ kubelet ไม่ต้อง watch ConfigMap ที่ immutable ลดภาระของ API server
</details>

**16. Pod ใน namespace `som-dev` อยากใช้ ConfigMap `som-web-config` ที่อยู่ใน `som-prod` ได้หรือไม่ และ ServiceAccount ที่มีแค่สิทธิ์ `get,list configmaps` ควรเห็นอะไรได้บ้าง**

<details>
<summary>แนวคำตอบ</summary>

ไม่ได้ ช่องอ้าง ConfigMap ไม่มี `namespace` Kubernetes หาใน namespace ของ Pod เท่านั้น ได้ `CreateContainerConfigError: configmap "som-web-config" not found` ต้องสร้างสำเนาใน `som-dev` ส่วน ServiceAccount นั้นอ่านทุกค่าของทุก ConfigMap ใน namespace ที่ได้สิทธิ์ (RBAC ไม่แบ่งราย key) แต่แก้ไม่ได้ (`cannot patch resource "configmaps"`) และอ่านใน namespace อื่นไม่ได้
</details>

**17. ทำไมการย้าย `DATABASE_URL` ที่มีรหัสผ่านไปไว้ใน ConfigMap จึงไม่ได้แก้ปัญหาที่ intern ใน LAB 10 เห็นรหัสผ่าน**

<details>
<summary>แนวคำตอบ</summary>

intern มีสิทธิ์อ่าน ConfigMap อยู่แล้ว และ ConfigMap เก็บเป็นข้อความธรรมดา จึงเห็นรหัสเหมือนเดิม (แค่เปลี่ยนที่อ่าน) ต้องใช้ object สำหรับความลับที่ให้สิทธิ์แยกจาก ConfigMap/Deployment ได้ คือ Secret ในบทที่ 11
</details>

---

## 14. เอกสารอ้างอิง

1. The Kubernetes Authors. *ConfigMaps*. https://kubernetes.io/docs/concepts/configuration/configmap/
2. The Kubernetes Authors. *Configure a Pod to Use a ConfigMap*. https://kubernetes.io/docs/tasks/configure-pod-container/configure-pod-configmap/
3. The Kubernetes Authors. *Updating Configuration via a ConfigMap*. https://kubernetes.io/docs/tutorials/configuration/updating-configuration-via-a-configmap/
4. The Kubernetes Authors. *Define Environment Variables for a Container*. https://kubernetes.io/docs/tasks/inject-data-application/define-environment-variable-container/
5. The Kubernetes Authors. *Define Dependent Environment Variables*. https://kubernetes.io/docs/tasks/inject-data-application/define-interdependent-environment-variables/
6. The Kubernetes Authors. *Volumes — configMap*. https://kubernetes.io/docs/concepts/storage/volumes/#configmap
7. The Kubernetes Authors. *Declarative Management of Kubernetes Objects Using Kustomize*. https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization/
8. The Kubernetes Authors. *kubectl create configmap*. https://kubernetes.io/docs/reference/kubectl/generated/kubectl_create/kubectl_create_configmap/
9. The Kubernetes Authors. *kubectl rollout restart*. https://kubernetes.io/docs/reference/kubectl/generated/kubectl_rollout/kubectl_rollout_restart/
10. The Kubernetes Authors. *Well-Known Labels, Annotations and Taints* (`kubectl.kubernetes.io/restartedAt`). https://kubernetes.io/docs/reference/labels-annotations-taints/
11. The Kubernetes Authors. *Using RBAC Authorization*. https://kubernetes.io/docs/reference/access-authn-authz/rbac/
12. The Kubernetes Authors. *Kubelet Configuration (v1beta1)* (`syncFrequency`, `configMapAndSecretChangeDetectionStrategy`). https://kubernetes.io/docs/reference/config-api/kubelet-config.v1beta1/
13. The Kubernetes Authors. *Customizing DNS Service* (ConfigMap `coredns`). https://kubernetes.io/docs/tasks/administer-cluster/dns-custom-nameservers/
14. Adam Wiggins. *The Twelve-Factor App — III. Config*. https://12factor.net/config
15. Helm Authors. *Chart Development Tips and Tricks — Automatically Roll Deployments*. https://helm.sh/docs/howto/charts_tips_and_tricks/#automatically-roll-deployments

---

> **หมายเหตุเกี่ยวกับภาพประกอบ:** ภาพประกอบ 40 ภาพในโฟลเดอร์ [`images/`](images/) และภาพตัวละครน้องส้ม ([`00-character-som.png`](images/00-character-som.png)) สร้างขึ้นด้วยปัญญาประดิษฐ์สำหรับการสร้างภาพเพื่อใช้ประกอบการเรียนการสอน ชุดคำสั่งสร้างภาพอยู่ใน [`images/imagegen-prompts.md`](images/imagegen-prompts.md) ภาพใช้อุปมาเชิงเปรียบเทียบเพื่อช่วยความเข้าใจ ตัวเลขในภาพ (เช่น เวลาอัปเดต ชื่อโฟลเดอร์ `..2026_10_05_…` และ hash) เป็นค่าตัวอย่าง ผู้เรียนควรใช้เนื้อหาในเอกสารนี้และเอกสารอ้างอิงเป็นหลัก ผลลัพธ์คำสั่งทั้งหมดมาจากการทดลองจริง (Kubernetes v1.37.0, kubectl v1.37.1) ค่าเวลา, AGE และชื่อ Pod ในเครื่องผู้เรียนอาจต่างกัน
