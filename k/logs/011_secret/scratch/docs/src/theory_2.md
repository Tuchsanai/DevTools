## 5. ใช้ Secret ใน Pod

วิธีส่ง Secret เข้า Pod เหมือนกับ ConfigMap ทุกประการ เปลี่ยนแค่ชื่อฟิลด์ (`configMapKeyRef` → `secretKeyRef`, `configMapRef` → `secretRef`, volume `configMap` → `secret` และ `name` → `secretName`) Pod ตัวอย่าง `labs/lab03-use/spod.yaml` ใช้ทั้งสามแบบพร้อมกัน

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: spod
spec:
  terminationGracePeriodSeconds: 1     # sleep ไม่รับ SIGTERM → ลบเร็ว
  containers:
    - name: c
      image: busybox:1.36
      command: ["sleep", "86400"]
      env:
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: demo               # ชื่อ Secret
              key: password            # key ในซอง
      envFrom:
        - prefix: SD_
          secretRef:
            name: sd
      volumeMounts:
        - name: s
          mountPath: /etc/secret
          readOnly: true
        - name: s400
          mountPath: /etc/secret400
          readOnly: true
  volumes:
    - name: s
      secret:
        secretName: demo               # ทุก key = 1 ไฟล์ (/etc/secret/username, /etc/secret/password)
    - name: s400
      secret:
        secretName: demo
        defaultMode: 0400              # เลขฐานแปด → ไฟล์ -r--------
```

### 5.1 env: secretKeyRef และ envFrom.secretRef

{{FIG:T16|env จาก secretKeyRef}}

ผลจริง

```text
$ kubectl exec spod -- env | grep -E 'DB_|SD_'
SD_USERNAME=som
SD_PASSWORD=override-by-stringData
DB_PASSWORD=meow1234
```

- `secretKeyRef` หยิบทีละ key ตั้งชื่อ env เองได้ (`DB_PASSWORD` ← `demo/password`)
- `envFrom.secretRef` ถ่ายทุก key ของซองเป็น env และใส่ `prefix` ได้ (`SD_PASSWORD`, `SD_USERNAME` จาก Secret `sd`)
- กติกาเดียวกับ ConfigMap ในบทที่ 10: **env ชนะ envFrom** เมื่อชื่อซ้ำ และ `$(VAR)` ที่อยู่ในค่าที่มาจาก envFrom **ไม่ถูกแทนค่า** (แทนค่าเฉพาะ `$(VAR)` ที่เขียนใน `env[].value`, `command`, `args`)
- อ้าง Secret หรือ key ที่ไม่มี → Pod ค้าง `CreateContainerConfigError` เหมือน ConfigMap ใส่ `optional: true` ได้ถ้าค่านั้นไม่จำเป็นจริง
- **ค่าถูกคัดลอกครั้งเดียวตอน container เริ่ม** แก้ Secret ภายหลัง env ไม่เปลี่ยน (หัวข้อ 5.4)

ร้านน้องส้มใน LAB 9 ใช้ `secretKeyRef` ใน `k8s/20-web.yaml` ทั้งที่ `db-seed` และ `web`

```yaml
- name: DATABASE_URL     # postgres://som:<รหัส>@som-db-0.som-db:5432/catshop — ทั้งก้อนอยู่ในซอง
  valueFrom:
    secretKeyRef:
      name: som-db-secret
      key: DATABASE_URL
```

แอป `som-shop-web:1.5` **ไม่ต้องแก้โค้ดเลย** เพราะแอปอ่าน `process.env.DATABASE_URL` อยู่แล้ว ไม่สนว่าค่ามาจาก `value` หรือจาก Secret

### 5.2 volume: ไฟล์ละ key

{{FIG:T17|volume แบบ tmpfs}}

volume ชนิด `secret` สร้างไฟล์ 1 ไฟล์ต่อ 1 key ผ่าน symlink `..data` แบบเดียวกับ ConfigMap (บทที่ 10 หัวข้อ 8.3) ผลจริง

```text
$ kubectl exec spod -- ls -la /etc/secret /etc/secret400/..data/
/etc/secret:
total 4
drwxrwxrwt    3 root     root           120 Oct  5 11:32 .
drwxr-xr-x    1 root     root          4096 Oct  5 11:32 ..
drwxr-xr-x    2 root     root            80 Oct  5 11:32 ..2026_10_05_11_32_18.406880621
lrwxrwxrwx    1 root     root            31 Oct  5 11:32 ..data -> ..2026_10_05_11_32_18.406880621
lrwxrwxrwx    1 root     root            15 Oct  5 11:32 password -> ..data/password
lrwxrwxrwx    1 root     root            15 Oct  5 11:32 username -> ..data/username

/etc/secret400/..data/:
total 8
drwxr-xr-x    2 root     root            80 Oct  5 11:32 .
drwxrwxrwt    3 root     root           120 Oct  5 11:32 ..
-r--------    1 root     root             8 Oct  5 11:32 password
-r--------    1 root     root             3 Oct  5 11:32 username
```

- ค่าในไฟล์เป็น **ข้อความที่ถอด base64 แล้ว** (`cat /etc/secret/password` ได้ `meow1234`) แอปไม่ต้อง decode เอง
- `defaultMode: 0400` ทำให้ไฟล์เป็น `-r--------` (เจ้าของอ่านได้คนเดียว) ต้องเขียนเป็นเลขฐานแปดใน YAML (`0400`) ถ้าใช้ JSON ต้องเป็นเลขฐานสิบ `256`
- ใช้ `items` เลือกบาง key และตั้งชื่อไฟล์เองได้เหมือน ConfigMap (ตัวอย่างใน `proj.yaml` หัวข้อ 12)
- ถ้า container รันเป็นผู้ใช้ที่ไม่ใช่ root และไฟล์เป็น 0400 ของ root จะอ่านไม่ได้ ต้องใช้ `fsGroup` + `defaultMode: 0440` (ตัวอย่างจริงใน LAB 9 `extra/30-https-restricted.yaml`)

### 5.3 tmpfs: ถาดฟองน้ำความจำ

ไฟล์ของ Secret volume ไม่ได้อยู่บนดิสก์ของ Node แต่อยู่บน **tmpfs** (ระบบไฟล์ในหน่วยความจำ) และ mount แบบอ่านอย่างเดียว ผลจริง

```text
$ kubectl exec spod -- mount | grep -E "secret|serviceaccount"
tmpfs on /etc/secret type tmpfs (ro,relatime,size=64489564k,noswap)
tmpfs on /etc/secret400 type tmpfs (ro,relatime,size=64489564k,noswap)
tmpfs on /var/run/secrets/kubernetes.io/serviceaccount type tmpfs (ro,relatime,size=64489564k,noswap)
$ kubectl exec spod -- sh -c "echo hack > /etc/secret/password"
sh: can't create /etc/secret/password: Read-only file system
command terminated with exit code 1
```

- `noswap` = ไม่ถูกย้ายไปเก็บใน swap บนดิสก์ เมื่อ Pod ถูกลบ ไฟล์ก็หายไปพร้อมหน่วยความจำ ไม่ทิ้งร่องรอยไว้บนดิสก์ของ Node
- token ของ ServiceAccount ที่ Pod ได้อัตโนมัติ (`/var/run/secrets/kubernetes.io/serviceaccount`) ก็เป็น tmpfs เช่นกัน
- kubelet ดึง Secret มาเฉพาะที่ Pod บน Node ของตัวเองใช้ Node อื่นไม่ได้รับ (ลดผลกระทบถ้า Node ใด Node หนึ่งถูกเจาะ)

### 5.4 env รั่วง่ายกว่าไฟล์

{{FIG:T18|env รั่วง่าย}}

env ดูสะดวก แต่มีทางรั่วมากกว่าไฟล์ ผลจริงจาก LAB 3

```text
$ kubectl exec spod -- cat /proc/1/environ | tr '\0' '\n' | grep DB_
DB_PASSWORD=meow1234
```

| ทางรั่วของ env | ตัวอย่าง |
|---|---|
| `kubectl exec ... -- env` | ใครมีสิทธิ์ `pods/exec` เห็นทุกตัวแปร |
| `/proc/<pid>/environ` | process อื่นใน container เดียวกัน หรือเครื่องมือ debug อ่านได้ |
| log ของแอป | แอปหรือ framework บางตัวพิมพ์ env ทั้งหมดตอน error หรือตอนเริ่ม |
| crash dump / error report | ระบบรายงาน error ภายนอกมักแนบ env ไปด้วย |
| process ลูก | ทุก process ที่แอปเรียก (`sh -c ...`) ได้ env ไปทั้งชุด |

ไฟล์ใน volume ก็อ่านได้ด้วย `kubectl exec` เหมือนกัน แต่ไม่ติดไปกับ process ลูกและ dump อัตโนมัติ และ **อัปเดตเองได้** (หัวข้อถัดไป) แนวปฏิบัติจึงเป็น "ใช้ไฟล์เมื่อแอปรองรับ" ส่วนร้านน้องส้มยังใช้ env เพราะแอปอ่าน `DATABASE_URL` จาก env และต้องการแสดงหลักการพื้นฐานก่อน

### 5.5 การอัปเดต และ immutable

{{FIG:T19|อัปเดตและ immutable}}

สคริปต์ `labs/lab03-use/wait-secret.sh` แก้ `password` ใน Secret `demo` ด้วย `kubectl patch` แล้วจับเวลาว่าไฟล์ใน Pod `spod` เปลี่ยนเมื่อไร ผลจริงสองรอบ

```text
$ ./wait-secret.sh newpass-00
secret/demo patched
18:32:25 patch secret demo → password=newpass-00
  ไฟล์ /etc/secret/password เปลี่ยนหลัง 71 วินาที: newpass-00
  ไฟล์ /etc/secret400/password       : newpass-00
  env DB_PASSWORD (ไม่เปลี่ยน)        : meow1234
$ ./wait-secret.sh newpass-01
secret/demo patched
18:33:37 patch secret demo → password=newpass-01
  ไฟล์ /etc/secret/password เปลี่ยนหลัง 81 วินาที: newpass-01
  ไฟล์ /etc/secret400/password       : newpass-01
  env DB_PASSWORD (ไม่เปลี่ยน)        : meow1234
```

| ส่งค่าแบบ | แก้ Secret แล้วเป็นอย่างไร | ผลจริง |
|---|---|---|
| volume (ทั้งก้อน / `items`) | kubelet อัปเดตไฟล์เองเป็นรอบ ๆ | **ราว 1 นาที** (วัดได้ 71 และ 81 วินาที; บทที่ 10 วัด ConfigMap ได้ 37–88 วินาที) |
| volume แบบ `subPath` | ไม่อัปเดต | ต้องได้ Pod ใหม่ |
| env / envFrom | ไม่เปลี่ยน | `DB_PASSWORD` ยังเป็น `meow1234` จนกว่าจะได้ Pod ใหม่ |
| Pod ใหม่ | อ่านค่าล่าสุด | ลบแล้วสร้าง `spod` ใหม่ได้ `newpass-01` |

สำหรับ Deployment ใช้ `kubectl rollout restart` ให้ได้ Pod ใหม่ทั้งชุด (LAB 9 ขั้น D3) และอย่าลืมว่าไฟล์ที่เปลี่ยนแล้ว แอปต้องอ่านใหม่เองด้วย (บทที่ 10 หัวข้อ 8.4)

**immutable: ซองเคลือบ** ไฟล์ `labs/lab03-use/frozen.yaml`

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: frozen
type: Opaque
immutable: true
stringData:
  API_KEY: example-key-v1            # ค่าตัวอย่างเพื่อการเรียน
```

ผลจริงเมื่อพยายามแก้

```text
$ kubectl patch secret frozen --type merge -p '{"stringData":{"API_KEY":"example-key-v2"}}'
The Secret "frozen" is invalid: data: Forbidden: field is immutable when `immutable` is set
$ kubectl patch secret frozen --type merge -p '{"immutable":false}'
The Secret "frozen" is invalid: immutable: Forbidden: field is immutable when `immutable` is set
```

แก้ค่าไม่ได้และปิด immutable ก็ไม่ได้ ทางเดียวคือลบแล้วสร้างใหม่ (หรือสร้างชื่อใหม่แล้วชี้ Pod ไปชื่อใหม่) ข้อดีคือกันการแก้โดยไม่ตั้งใจ และ kubelet ไม่ต้องคอยเฝ้าดู Secret ตัวนั้น (ลดภาระ API server เมื่อมี Secret จำนวนมาก)

---

## 6. imagePullSecrets: บัตรผ่านคลัง image ส่วนตัว

### 6.1 registry ที่ต้อง login

{{FIG:T20|imagePullSecrets}}

ตลอดหลักสูตรเราใช้ image สาธารณะ (busybox, nginx, postgres) หรือ `kind load` image ของร้านเข้า Node โดยตรง แต่ในงานจริง image ของบริษัทมักอยู่ใน **registry ส่วนตัว** ที่ต้อง login ก่อนดึง Node ไม่รู้รหัสของเรา จึงต้องให้ Pod ถือ **บัตรผ่าน** คือ Secret ชนิด `kubernetes.io/dockerconfigjson`

```bash
kubectl -n reg create secret docker-registry regcred --docker-server=kind-registry:5000 --docker-username=som --docker-password=example-pass
```

แล้วอ้างใน Pod ด้วย `spec.imagePullSecrets` (ไฟล์ `labs/lab05-registry/2-withpull.yaml`)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: withpull
  namespace: reg
spec:
  nodeName: lab-worker
  terminationGracePeriodSeconds: 1
  imagePullSecrets:
    - name: regcred                  # Secret ใน namespace เดียวกับ Pod
  containers:
    - name: menu
      image: kind-registry:5000/som-menu:1.0
```

หรือผูกบัตรไว้กับ ServiceAccount ให้ทุก Pod ที่ใช้ SA นั้นได้บัตรอัตโนมัติ (ไม่ต้องเขียนในทุก Pod)

```bash
kubectl -n reg patch sa default -p '{"imagePullSecrets":[{"name":"regcred"}]}'
```

Pod `viasa` ที่ไม่ได้เขียน `imagePullSecrets` เลยถูกเติมให้ตอนสร้าง ผลจริง `[{"name":"regcred"}]  Running  lab-worker2`

อาการที่เห็นใน LAB 5 (registry `registry:2` ตั้งรหัสด้วย htpasswd)

| สถานการณ์ | STATUS | ข้อความใน Events (ผลจริง ตัดบางส่วน) |
|---|---|---|
| ไม่มีบัตร | `ErrImagePull` ↔ `ImagePullBackOff` | `pull access denied, repository does not exist or may require authorization: authorization failed: no basic auth credentials` |
| มีบัตรถูก | `Running` | `Successfully pulled image "kind-registry:5000/som-menu:1.0" in 311ms` |
| บัตรผิด (รหัสผิด) | `ErrImagePull` ↔ `ImagePullBackOff` | `unexpected status from HEAD request to http://kind-registry:5000/v2/som-menu/manifests/1.0: 401 Unauthorized` |
| บัตรอยู่คนละ namespace | เหมือนไม่มีบัตร | Secret ต้องอยู่ namespace เดียวกับ Pod |

### 6.2 image ที่ดึงด้วยบัตรแล้ว Pod อื่นยืมใช้ไม่ได้

{{FIG:T21|kubelet ตรวจบัตรซ้ำ}}

คำถามที่น่าสนใจ: ถ้า Node มี image ส่วนตัวอยู่แล้ว (เพราะ Pod ที่มีบัตรดึงมา) Pod ใน namespace อื่นที่ **ไม่มีบัตร** และตั้ง `imagePullPolicy: IfNotPresent` จะใช้ image นั้นได้ไหม ในอดีตใช้ได้ ซึ่งเป็นช่องโหว่ (ใครรู้ชื่อ image ก็ยืมใช้ได้) LAB 5 ทดลองด้วย Pod `cached` ใน namespace `reg2` ที่ตรึงลง `lab-worker` ซึ่งมี image แล้ว ผลจริงบน Kubernetes v1.37

```text
NAME     READY   STATUS             RESTARTS   AGE   IP           NODE         NOMINATED NODE   READINESS GATES
cached   0/1     ImagePullBackOff   0          20s   10.244.2.4   lab-worker   <none>           <none>
...
  Warning  Failed   5s (x2 over 20s)  kubelet  spec.containers{menu}: Failed to pull image "kind-registry:5000/som-menu:1.0": ... authorization failed: no basic auth credentials
```

แม้ `crictl images` บน `lab-worker` จะเห็น `kind-registry:5000/som-menu 1.0` อยู่ kubelet ก็ยังไปขอสิทธิ์จาก registry ใหม่ เพราะ kubelet จำไว้ว่า image นี้ถูกดึงมาด้วย credential ใด และให้ Pod ที่ไม่มี credential ที่ถูกต้องใช้ไม่ได้ (การตั้งค่า `imagePullCredentialsVerificationPolicy` ของ kubelet) ส่วน image ที่ `kind load` ใส่ Node ไว้ล่วงหน้า (เช่น `som-shop-web:1.5`) ไม่ได้ถูกดึงด้วยบัตรจึงใช้ได้ตามปกติ ผลจริง Pod `shopcheck` (`som-shop-web:1.5`) บน `lab-worker` เดียวกันรันได้ `som-shop-web:1.5 ok`

> **บทเรียนจากการเตรียม LAB:** ถ้านำ image ของร้าน (`som-shop-web:1.5` ตัวเดียวกันทุกไบต์) ขึ้น registry ส่วนตัวแล้วดึงด้วยบัตร kubelet จะผูก image นั้นกับบัตรไปด้วย Pod ร้านที่ไม่มีบัตรบน Node เดียวกันอาจดึงไม่ได้ LAB 5 จึงใช้ image แยกชื่อ `som-menu:1.0` (busybox + ไฟล์เมนู) และห้ามลบ image ด้วย `crictl rmi` บน Node

---

## 7. TLS Secret: ท่อแก้วปิดสนิท

### 7.1 ใบรับรองและกุญแจ

{{FIG:T22|ใบรับรองกับกุญแจ}}

HTTPS ต้องใช้ของสองชิ้น

| ไฟล์ | คืออะไร | แจกได้ไหม |
|---|---|---|
| `tls.crt` | **ใบรับรอง (certificate)** บอกว่าเซิร์ฟเวอร์นี้คือใคร (CN, subjectAltName) และมี public key | แจกได้ ลูกค้าทุกคนได้รับตอนเชื่อมต่อ |
| `tls.key` | **กุญแจส่วนตัว (private key)** ใช้พิสูจน์ว่าเป็นเจ้าของใบรับรองจริง | **ห้ามรั่ว** ใครได้ไปก็ปลอมเป็นเว็บเราได้ |

ในงานจริงใบรับรองออกโดย CA ที่เบราว์เซอร์เชื่อถือ (เช่น Let's Encrypt ผ่าน cert-manager) ใน LAB เราออกใบรับรองให้ตัวเอง (self-signed) ด้วย openssl

```bash
openssl req -x509 -nodes -newkey rsa:2048 -days 365 -keyout tls.key -out tls.crt -subj '/CN=shop.som.local' -addext 'subjectAltName=DNS:shop.som.local,DNS:localhost'
openssl x509 -in tls.crt -noout -subject -issuer -enddate -ext subjectAltName
kubectl create secret tls shop-tls --cert=tls.crt --key=tls.key
```

```text
subject=CN = shop.som.local
issuer=CN = shop.som.local
notAfter=Oct  5 11:35:09 2027 GMT
X509v3 Subject Alternative Name: 
    DNS:shop.som.local, DNS:localhost
secret/shop-tls created
```

`subject` = `issuer` คือลักษณะของใบรับรอง self-signed (เซ็นให้ตัวเอง) `-days 365` ทำให้หมดอายุในอีก 1 ปี เบราว์เซอร์และ curl ตรวจ **ชื่อใน subjectAltName** ไม่ใช่ CN จึงใส่ทั้ง `shop.som.local` และ `localhost` (คำสั่ง openssl พิมพ์จุดและเครื่องหมาย `+` ยาวหลายบรรทัดระหว่างสร้างกุญแจ เป็นเรื่องปกติ)

### 7.2 nginx HTTPS และการทดสอบด้วย curl

{{FIG:T23|HTTPS ด้วย nginx และ curl}}

nginx อ่านใบรับรองจากไฟล์ จึง mount Secret เป็น volume (ไฟล์ `labs/lab04-tls/tls.yaml` ตัดมาเฉพาะส่วนสำคัญ)

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: ngx-tls-conf
data:
  default.conf: |
    server {
      listen 443 ssl;
      ssl_certificate     /etc/nginx/tls/tls.crt;    # ไฟล์จาก Secret (key tls.crt)
      ssl_certificate_key /etc/nginx/tls/tls.key;    # ไฟล์จาก Secret (key tls.key)
      location / { default_type text/plain; return 200 "HTTPS ร้านน้องส้ม\n"; }
    }
```

```yaml
volumes:
  - name: conf
    configMap:
      name: ngx-tls-conf
  - name: tls
    secret:
      secretName: shop-tls
      defaultMode: 0400            # กุญแจลับอ่านได้แค่เจ้าของ (nginx master รันเป็น root จึงอ่านได้)
```

ConfigMap เก็บ "ค่าตั้งค่าที่ไม่ลับ" (`default.conf`) Secret เก็บ "กุญแจ" แต่ละอย่างอยู่ในที่ของตัวเอง ทดสอบผ่าน NodePort 30081 ผลจริง

| คำสั่ง | ผล | ความหมาย |
|---|---|---|
| `curl -sS https://localhost:30081/` | `curl: (60) SSL certificate problem: self-signed certificate` | curl ไม่เชื่อใบรับรองที่ไม่ได้ออกโดย CA ที่รู้จัก |
| `curl -sk https://localhost:30081/` | `HTTPS ร้านน้องส้ม` | `-k` = ข้ามการตรวจใบรับรอง (ใช้ทดสอบเท่านั้น ไม่กันการปลอมตัว) |
| `curl -s --cacert tls.crt https://localhost:30081/` | `HTTPS ร้านน้องส้ม` | บอก curl ให้เชื่อใบรับรองนี้ → ตรวจผ่านอย่างถูกต้อง |
| `curl -s --cacert tls.crt --resolve shop.som.local:30081:127.0.0.1 https://shop.som.local:30081/` | `HTTPS ร้านน้องส้ม` | เรียกด้วยชื่อในใบรับรองโดยไม่ต้องแก้ DNS |
| `curl -sS --cacert tls.crt https://127.0.0.1:30081/` | `curl: (60) SSL: no alternative certificate subject name matches target host name '127.0.0.1'` | ชื่อที่เรียกไม่อยู่ใน subjectAltName |
| `curl -sS http://localhost:30081/` | `400 The plain HTTP request was sent to HTTPS port` | ส่ง http ธรรมดาไปพอร์ต https |

ดูใบรับรองที่เซิร์ฟเวอร์ส่งมาได้ด้วย `openssl s_client`

```text
$ openssl s_client -connect localhost:30081 -servername shop.som.local </dev/null 2>/dev/null | openssl x509 -noout -subject -enddate
subject=CN = shop.som.local
notAfter=Oct  5 11:35:09 2027 GMT
```

> **จังหวะเวลา:** `curl` ทันทีหลัง Pod Ready ได้ `curl: (35) OpenSSL SSL_connect: SSL_ERROR_SYSCALL` (`rc=35`) เพราะเส้นทางของ NodePort ยังไม่พร้อม รอราว 5 วินาทีแล้วลองใหม่
>
> **จาก browser:** เปิด `https://localhost:30081` บนเครื่องนักศึกษา browser จะเตือนว่าการเชื่อมต่อไม่เป็นส่วนตัว (`NET::ERR_CERT_AUTHORITY_INVALID`) เพราะใบรับรองเป็น self-signed กด Advanced → Proceed เพื่อทดสอบได้ ในงานจริงต้องใช้ใบรับรองจาก CA จริง ไม่ใช่สอนให้ผู้ใช้กดข้ามคำเตือน

ในบทถัดไป **Ingress** จะรับหน้าที่ "ปลายท่อ TLS" แทน nginx ที่เราเขียนเอง โดยอ้าง Secret ชนิด `kubernetes.io/tls` แบบเดียวกันนี้ และ **cert-manager** ช่วยขอและต่ออายุใบรับรองให้อัตโนมัติ

---

## 8. RBAC: ใครเปิดกล่องกุญแจได้

### 8.1 บัตรแถบเทาของ intern

{{FIG:T24|intern ถูกปฏิเสธ}}

ต่อจาก RBAC ในบทที่ 4 ไฟล์ `labs/lab07-rbac/intern.yaml` ให้ intern ดู Pod, log และ ConfigMap ได้ แต่ไม่มีกฎใดเกี่ยวกับ `secrets`

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: intern-view
rules:
  - apiGroups: [""]
    resources: ["pods", "pods/log", "configmaps"]
    verbs: ["get", "list", "watch"]
```

ผลจริง

```text
get pods: yes
get configmaps: yes
get secrets: no
list secrets: no
$ kubectl get secret demo --as=system:serviceaccount:default:intern
Error from server (Forbidden): secrets "demo" is forbidden: User "system:serviceaccount:default:intern" cannot get resource "secrets" in API group "" in the namespace "default"
$ kubectl get secrets --as=system:serviceaccount:default:intern
Error from server (Forbidden): secrets is forbidden: User "system:serviceaccount:default:intern" cannot list resource "secrets" in API group "" in the namespace "default"
```

intern ยังดู `kubectl get pod spod -o yaml` ได้ แต่เห็นแค่ **ชื่อซองและชื่อ key** ไม่เห็นค่า

```text
    - name: DB_PASSWORD
      valueFrom:
        secretKeyRef:
          key: password
          name: demo
```

นี่คือเหตุผลหลักที่ต้องย้ายรหัสจาก env ไป Secret: **สิทธิ์ดู Deployment/Pod กับสิทธิ์ดู Secret แยกกันได้** (`describe secret` ก็ถูกปฏิเสธด้วยข้อความเดียวกัน) สำรวจสิทธิ์ทั้งหมดของ intern ได้ด้วย `kubectl auth can-i --list --as=...` ซึ่งไม่มีแถว `secrets` เลย

### 8.2 สิทธิ์สร้าง Pod = อ่าน Secret ทางอ้อม

{{FIG:T25|อ่าน Secret ทางอ้อม}}

ServiceAccount `maker` (ไฟล์ `labs/lab07-rbac/maker.yaml`) มีสิทธิ์ `get, list, create, delete` กับ `pods`, `pods/log` แต่ **ไม่มีสิทธิ์ `get secrets`**

```text
$ kubectl auth can-i get secrets --as=system:serviceaccount:default:maker; kubectl auth can-i create pods --as=system:serviceaccount:default:maker
no
yes
```

maker สร้าง Pod `peek` (ไฟล์ `labs/lab07-rbac/peek.yaml`) ที่ขอ Secret `demo` มาเป็น env แล้วพิมพ์ลง log

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: peek
spec:
  restartPolicy: Never
  containers:
    - name: peek
      image: busybox:1.36
      command: ["sh", "-c", "echo stolen=$P"]
      env:
        - name: P
          valueFrom:
            secretKeyRef:
              name: demo
              key: password
```

```text
$ kubectl logs peek --as=system:serviceaccount:default:maker
stolen=newpass-01
```

kubelet เป็นคนเปิดซองให้ Pod โดยไม่ได้ตรวจว่า "คนที่สร้าง Pod" มีสิทธิ์อ่าน Secret หรือไม่ ดังนั้นสิทธิ์ต่อไปนี้ **เท่ากับสิทธิ์อ่าน Secret ทุกตัวใน namespace นั้น**

| สิทธิ์ | อ่าน Secret ได้อย่างไร |
|---|---|
| `get secrets` | อ่านตรง ๆ (`get -o yaml` + `base64 -d`) |
| `list secrets` | อ่าน **ทุกตัว** ในคำสั่งเดียว (`list` คืนค่าเต็ม ไม่ใช่แค่ชื่อ) |
| `watch secrets` | ได้ค่าทุกครั้งที่มีการเปลี่ยน |
| `create pods` (และ Deployment, Job, …) | สร้าง Pod ที่ mount/อ้าง Secret แล้วพิมพ์ออกมา |
| `create pods/exec` | เข้าไปใน Pod ที่ใช้ Secret อยู่แล้ว `env` หรือ `cat` ไฟล์ |

นี่คือเหตุผลที่ร้านน้องส้มให้ intern แค่ `get/list/watch` และ **ไม่ให้ `pods/exec`** ผลจริงใน LAB 9 `kubectl --context intern exec ...` ได้ `cannot create resource "pods/exec"` แต่ intern ยังดู log ได้ (`pods/log` = yes) จึงต้องระวังไม่ให้แอปพิมพ์รหัสลง log

### 8.3 describe กับ get

{{FIG:T26|describe เทียบกับ get}}

```text
$ kubectl describe secret demo
Name:         demo
Namespace:    default
Labels:       <none>
Annotations:  <none>

Type:  Opaque

Data
====
password:  8 bytes
username:  3 bytes
```

`describe` ถูกออกแบบให้ "ไม่พิมพ์ค่า" เพื่อลดการรั่วโดยบังเอิญ (เช่น ตอนแชร์จอ) แต่ **ไม่ใช่การควบคุมสิทธิ์** ทั้ง `describe` และ `get -o yaml` ใช้สิทธิ์ `get secrets` เหมือนกัน คนที่ describe ได้ก็ `get -o jsonpath=... | base64 -d` ได้ทุกครั้ง (ข้อยกเว้นคือ token ของ service-account-token ที่ describe แสดงเต็มทั้งเส้น หัวข้อ 3.4)

---

## 9. etcd และ encryption at rest

### 9.1 Secret อยู่ใน etcd เป็นข้อความ

{{FIG:T27|etcd เก็บเป็นข้อความ}}

ทุก object ของคลัสเตอร์ถูกเก็บใน etcd บน control plane (บทที่ 1) Secret อยู่ที่ key `/registry/secrets/<namespace>/<ชื่อ>` LAB 8 ใช้สคริปต์ `labs/lab08-etcd/etcdget.sh` ที่เรียก `etcdctl` (อ่านอย่างเดียว) ใน Pod `etcd-lab-control-plane` ผลจริง

```text
$ ./etcdget.sh /registry/secrets/default/demo | grep -a -o 'newpass-01'
newpass-01
$ ./etcdget.sh /registry/secrets/default/demo | head -c 400 | cat -v; echo
/registry/secrets/default/demo
k8s^@
...
^Hpassword^R
newpass-01^R^O
^Husername^R^Csom^Z^FOpaque^Z^@"^@
```

ข้อมูลเป็น protobuf (มีอักขระไบนารี) แต่ค่า `newpass-01` อยู่ในนั้นเป็นข้อความตรง ๆ **ไม่ใช่แม้แต่ base64** (base64 เป็นแค่รูปแบบตอนส่งผ่าน JSON/YAML ของ API) เพราะ kind ค่าเริ่มไม่ได้เปิด encryption at rest

```text
$ docker exec lab-control-plane grep -n encryption /etc/kubernetes/manifests/kube-apiserver.yaml; echo "rc=$?"
rc=1
```

`rc=1` = ไม่พบคำว่า encryption ใน manifest ของ kube-apiserver เลย ConfigMap ก็เก็บแบบเดียวกัน (ผลจริงเห็น `วันนี้ปลาทูสดมาก` จาก `/registry/configmaps/default/shop-board`) แปลว่าใครที่เข้าถึง etcd, ไฟล์ข้อมูลของ etcd บนดิสก์ หรือไฟล์ backup ของ etcd ได้ ก็อ่าน Secret ทุกตัวได้โดยไม่ต้องผ่าน RBAC เลย

### 9.2 EncryptionConfiguration (แนวคิด)

{{FIG:T28|เปิด encryption at rest}}

การเข้ารหัสใน etcd ทำที่ **kube-apiserver** โดยเขียนไฟล์ `EncryptionConfiguration` แล้วชี้ด้วย flag `--encryption-provider-config` ตัวอย่างโครงสร้าง (เป็นแนวคิด **ไม่ทำใน LAB** เพราะต้องแก้ static Pod ของ control plane และค่า secret ในตัวอย่างเป็นค่าตัวอย่างที่ห้ามใช้จริง)

```yaml
apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
  - resources:
      - secrets
    providers:
      - aescbc:                     # provider แรก = ใช้เข้ารหัสของที่เขียนใหม่
          keys:
            - name: key1
              secret: "<base64 ของกุญแจสุ่ม 32 ไบต์ — ห้าม commit>"
      - identity: {}                # provider ท้าย = อ่านของเก่าที่ยังไม่เข้ารหัสได้
```

| provider | ลักษณะ |
|---|---|
| `identity` | ไม่เข้ารหัส (ค่าเริ่ม) ใส่ไว้ท้ายสุดเพื่ออ่านข้อมูลเก่าระหว่างย้าย |
| `aescbc`, `aesgcm`, `secretbox` | เข้ารหัสด้วยกุญแจที่อยู่ในไฟล์บน control plane (กุญแจกับข้อมูลอยู่เครื่องเดียวกัน) |
| `kms` (v2) | ให้บริการจัดการกุญแจภายนอก (cloud KMS, Vault) ถือ master key — แนะนำสำหรับโปรดักชัน |

ขั้นตอนโดยสรุป: (1) สร้างไฟล์บน control plane ทุกเครื่อง (2) เพิ่ม `--encryption-provider-config=<path>` ให้ kube-apiserver แล้วรอ restart (3) Secret ที่มีอยู่แล้วยังเป็นข้อความ จนกว่าจะเขียนใหม่ทั้งหมด เช่น `kubectl get secrets -A -o json | kubectl replace -f -` (4) ตรวจด้วย etcdctl ว่าค่าขึ้นต้นด้วย `k8s:enc:aescbc:v1:` แทนข้อความ คลัสเตอร์ของผู้ให้บริการคลาวด์ส่วนใหญ่เปิดการเข้ารหัสให้แล้วหรือมีตัวเลือกให้เปิด

### 9.3 ใครยังอ่านได้แม้เข้ารหัสแล้ว

{{FIG:T29|ใครยังอ่าน etcd ได้}}

encryption at rest ป้องกัน "คนที่ได้ไฟล์ etcd หรือ backup ไป" แต่ไม่ได้ป้องกัน

- ผู้ใช้ที่มีสิทธิ์ `get/list secrets` ผ่าน API (API server ถอดรหัสให้ตามปกติ) → ต้องใช้ RBAC
- `cluster-admin` และคนที่สร้าง Pod ได้ (หัวข้อ 8.2)
- root บน control plane ที่อ่านไฟล์กุญแจของ `aescbc` ได้ (เหตุผลที่โปรดักชันใช้ KMS)
- root บน worker Node ที่อ่าน tmpfs ของ Pod หรือ credential ของ kubelet ได้

ดังนั้นต้อง **ปกป้องไฟล์ backup ของ etcd** เหมือนเป็นรหัสผ่าน จำกัดคนที่มี `cluster-admin` และเข้าถึง Node ให้น้อยที่สุด

---

