# Secret: ซองปิดผนึกในกล่องกุญแจของโซน

> **รายวิชา:** Software Development Tools and Environments (DevTools)
> **หัวข้อ:** Kubernetes Secret — ความต่างจาก ConfigMap, base64 ไม่ใช่การเข้ารหัส, `type` ของ Secret (`Opaque`, `basic-auth`, `dockerconfigjson`, `tls`, `service-account-token`), การสร้าง (`--from-literal`, `--from-file`, `data`/`stringData`) และกับดัก `last-applied-configuration`, ใช้ใน Pod (`secretKeyRef`, `envFrom.secretRef`, volume แบบ tmpfs, `defaultMode`), การอัปเดตและ `immutable`, `imagePullSecrets` กับ registry ส่วนตัว, TLS Secret กับ nginx HTTPS, RBAC และการอ่าน Secret ทางอ้อม, etcd กับ encryption at rest, การเปลี่ยนรหัสผ่าน, Sealed Secrets / External Secrets / Vault และ projected volume
> **ผลลัพธ์การเรียนรู้ที่เกี่ยวข้อง:** CLO-5, CLO-6
> **บทก่อนหน้า:** [บทที่ 10 ConfigMap](../../010_kubernetes_configmap/01_Theory/README.md) · **LAB ของบทนี้:** [02_LAB](../02_LAB/README.md)

---

## บทคัดย่อ

ท้ายบทที่ 10 ร้านอาหารแมวน้องส้มย้ายชื่อร้าน ธีม โปรโมชัน และประกาศหน้าร้านไปไว้บน **กระดานประกาศของโซน (ConfigMap)** ได้แล้ว แต่ยังเหลือปัญหาใหญ่หนึ่งข้อ คือ **รหัสผ่านฐานข้อมูล `som:meow1234` ยังเขียนตรงอยู่ใน YAML** ของ Deployment (`DATABASE_URL`) และ StatefulSet (`POSTGRES_PASSWORD`) ใครที่มีสิทธิ์แค่ "ดู" Deployment ก็อ่านรหัสได้ บทนี้แนะนำ **Secret** หรือ **ซองสีกรมท่าปิดผนึกครั่งรูปอุ้งเท้า** ที่เก็บไว้ใน **กล่องกุญแจเหล็กบนผนังโซน** ข้างกระดานประกาศ ใช้งานคล้าย ConfigMap (key–value, namespaced, ส่งเข้า Pod เป็น env หรือไฟล์) แต่แยกสิทธิ์ RBAC ได้ `kubectl describe` ไม่พิมพ์ค่า ไฟล์ใน Pod อยู่บนหน่วยความจำ (tmpfs) และเปิดการเข้ารหัสใน etcd ได้

บทนี้เน้นความเข้าใจที่ถูกต้องว่า **base64 ไม่ใช่การเข้ารหัส** (เป็นแค่ **ซองใส** ใครก็แปลงกลับได้) ความปลอดภัยของ Secret มาจากหลายชั้นรวมกัน ได้แก่ **บัตรพนักงาน (RBAC)** ที่กำหนดว่าใครเปิดกล่องได้ **ตู้นิรภัยในหอบังคับการ (encryption at rest)** ที่เข้ารหัสข้อมูลใน etcd ไฟล์บนหน่วยความจำของ Node และวินัยของคนทำงาน เช่น ไม่ commit รหัสลง git เนื้อหาครอบคลุม `type` ทั้ง 5 แบบ วิธีสร้างและกับดัก `stringData` + `kubectl apply` การใช้ใน Pod และการอัปเดต บัตรผ่านคลัง image ส่วนตัว (`imagePullSecrets`) ท่อแก้วปิดสนิท (TLS) ช่องโหว่ "สร้าง Pod ได้ = อ่าน Secret ได้" การส่อง etcd การเปลี่ยนรหัสผ่านที่ต้องทำสองฝั่ง และเครื่องมือภายนอกอย่าง Sealed Secrets, External Secrets Operator และ Vault

ผลลัพธ์คำสั่งและข้อความ error ทั้งหมดในเอกสารนี้มาจากการทดลองจริงบนคลัสเตอร์ kind (Kubernetes v1.37.0, kubectl v1.37.1, OpenSSL 3.0.13 ใน k8s-lab) ใน LAB ประจำบทเมื่อ 5 ตุลาคม 2569 **เวลา, AGE, ชื่อ Pod ที่สุ่ม, IP, UID, ชื่อโฟลเดอร์ `..2026_10_05_…` และจำนวนวินาทีที่ไฟล์อัปเดตในเครื่องผู้เรียนจะต่างจากตัวอย่าง** รหัสผ่านทุกตัวในเอกสาร (`meow1234`, `purr5678`, `newpass-01`, `example-pass` ฯลฯ) เป็น **ค่าตัวอย่างเพื่อการเรียนเท่านั้น** ห้ามนำไปใช้กับระบบจริง

## วัตถุประสงค์การเรียนรู้

เมื่อศึกษาเอกสารนี้จบ ผู้เรียนควรสามารถ

1. อธิบายว่าทำไมรหัสผ่านที่เขียนใน YAML ของ Deployment/StatefulSet หรือใน ConfigMap จึงไม่ปลอดภัย และ Secret ต่างจาก ConfigMap อย่างไร
2. แยก base64 กับการเข้ารหัสได้ แปลงค่า Secret กลับด้วย `base64 -d` และหลีกเลี่ยงกับดัก newline ของ `echo`
3. เลือก `type` ของ Secret ให้ตรงงาน (`Opaque`, `kubernetes.io/basic-auth`, `kubernetes.io/dockerconfigjson`, `kubernetes.io/tls`, `kubernetes.io/service-account-token`) และอ่าน error การตรวจ key ของแต่ละ type ได้
4. สร้าง Secret ด้วย `kubectl create secret` และ YAML (`data`/`stringData`) พร้อมอธิบายกับดัก annotation `last-applied-configuration` และวิธีเลี่ยง
5. ส่ง Secret เข้า Pod ด้วย `secretKeyRef`, `envFrom.secretRef` และ volume (`defaultMode`, `items`) อธิบายว่า volume เป็น tmpfs และเหตุผลที่ไฟล์ปลอดภัยกว่า env
6. อธิบายพฤติกรรมเมื่อแก้ Secret (volume อัปเดตเองราว 1 นาที, env ไม่เปลี่ยน) และใช้ `immutable: true`
7. ใช้ `imagePullSecrets` ทั้งใน Pod และผ่าน ServiceAccount อ่านอาการ `no basic auth credentials` / `401 Unauthorized` และอธิบายการตรวจสิทธิ์ image ซ้ำของ kubelet
8. สร้างใบรับรอง self-signed, Secret ชนิด TLS และเปิด nginx HTTPS พร้อมทดสอบด้วย `curl -k` / `--cacert`
9. กำหนดสิทธิ์ RBAC ของ Secret อธิบายการอ่าน Secret ทางอ้อมผ่านสิทธิ์สร้าง Pod หรือ `pods/exec` และอธิบายว่า Secret ถูกเก็บใน etcd อย่างไร พร้อมแนวคิด encryption at rest
10. วางแผนเปลี่ยนรหัสผ่านฐานข้อมูลที่ต้องทำทั้งฝั่งฐานข้อมูลและฝั่ง Secret และเลือกแนวทางภายนอก (Sealed Secrets, External Secrets, Vault) ได้เหมาะกับงาน

## สารบัญ

1. [บทนำ: รหัสผ่านยังอยู่ใน YAML](#1-บทนำ-รหัสผ่านยังอยู่ใน-yaml)
2. [Secret คืออะไร และต่างจาก ConfigMap อย่างไร](#2-secret-คืออะไร-และต่างจาก-configmap-อย่างไร)
3. [type ของ Secret](#3-type-ของ-secret)
4. [วิธีสร้าง Secret](#4-วิธีสร้าง-secret)
5. [ใช้ Secret ใน Pod](#5-ใช้-secret-ใน-pod)
6. [imagePullSecrets: บัตรผ่านคลัง image ส่วนตัว](#6-imagepullsecrets-บัตรผ่านคลัง-image-ส่วนตัว)
7. [TLS Secret: ท่อแก้วปิดสนิท](#7-tls-secret-ท่อแก้วปิดสนิท)
8. [RBAC: ใครเปิดกล่องกุญแจได้](#8-rbac-ใครเปิดกล่องกุญแจได้)
9. [etcd และ encryption at rest](#9-etcd-และ-encryption-at-rest)
10. [ข้อควรระวังในการใช้งานจริง](#10-ข้อควรระวังในการใช้งานจริง)
11. [แนวทางภายนอกคลัสเตอร์](#11-แนวทางภายนอกคลัสเตอร์)
12. [projected volume: แฟ้มห่วงรวมเอกสาร](#12-projected-volume-แฟ้มห่วงรวมเอกสาร)
13. [สรุปและปัญหาที่ยังเหลือ](#13-สรุปและปัญหาที่ยังเหลือ)
14. [คำถามทบทวน](#14-คำถามทบทวน)
15. [เอกสารอ้างอิง](#15-เอกสารอ้างอิง)

### สารบัญรูปภาพ

{{FIGTABLE}}

---

## 1. บทนำ: รหัสผ่านยังอยู่ใน YAML

{{FIG:T01|เปิดบท ซองปิดผนึกในกล่องกุญแจ}}

ร้านอาหารแมวน้องส้มเดินทางมาไกลแล้ว: บทที่ 5–7 มีหน้าร้าน (web) 3 บูธที่ผู้จัดการร้าน (Deployment) ดูแล บทที่ 6 มีประภาคาร (Service NodePort 30080) บทที่ 8–9 ครัวกลาง (db) เป็น StatefulSet `som-db` พร้อมตู้เซฟ `data-som-db-0` และบทที่ 10 ย้ายชื่อร้าน ธีม และประกาศไปไว้บนกระดานประกาศของโซน (ConfigMap `som-web-config` และ `som-announcement`) ใช้ image `som-shop-web:1.5` ตัวเดียวโดยไม่ต้อง build ใหม่

แต่ในไฟล์ของร้านยังมีของที่ไม่ควรอยู่ตรงนั้น ลองดู `k8s-010/20-web.yaml` (สภาพท้ายบท 010 ที่คัดลอกมาไว้ในโฟลเดอร์ LAB ของบทนี้) ตัดมาเฉพาะส่วนที่เกี่ยวข้อง

```yaml
initContainers:
  - name: db-seed
    image: som-shop-web:1.5
    env:
      - name: DATABASE_URL
        value: postgres://som:meow1234@som-db-0.som-db:5432/catshop
containers:
  - name: web
    image: som-shop-web:1.5
    env:
      - name: DATABASE_URL     # เรียก db ด้วยชื่อ DNS รายตัว <pod>.<headless svc> (ไม่ใช่ IP ของ Pod db)
        value: postgres://som:meow1234@som-db-0.som-db:5432/catshop
```

และใน `k8s-010/10-db.yaml` ของ StatefulSet

```yaml
env:
  - name: POSTGRES_USER
    value: som
  - name: POSTGRES_PASSWORD
    value: meow1234        # เพื่อการเรียนเท่านั้น (ของจริงใช้ Secret — บท 011)
```

{{FIG:T02|ทวนบท 010 รหัสผ่านยังเห็นได้}}

ปัญหาไม่ได้อยู่แค่ "ไฟล์" แต่อยู่ที่ **ทุกคนที่อ่าน object เหล่านี้ได้** ใน LAB 9 ของบทนี้ เราให้ ServiceAccount `intern` ที่มีสิทธิ์แค่ "ดู" Pod, log, ConfigMap, Deployment และ StatefulSet (ไม่มีสิทธิ์ใด ๆ กับ Secret) ลองอ่านร้านที่เริ่มจาก `k8s-010/` ผลจริง

```text
$ kubectl --context intern get deploy som-web -o yaml | grep -o 'som:[a-z0-9]*@'
som:meow1234@
som:meow1234@
som:meow1234@
som:meow1234@
$ kubectl --context intern get pod som-db-0 -o yaml | grep -A1 POSTGRES_PASSWORD
    - name: POSTGRES_PASSWORD
      value: meow1234
```

intern เห็นรหัส 4 ที่ใน Deployment (2 ที่ใน spec ของ `db-seed` กับ `web` และอีก 2 ที่ใน annotation `kubectl.kubernetes.io/last-applied-configuration` ที่ `kubectl apply` เก็บสำเนาไฟล์ไว้) และเห็นใน StatefulSet กับ Pod ของ db ด้วย การย้ายรหัสไปไว้ใน ConfigMap ก็ไม่ช่วย เพราะ intern มีสิทธิ์อ่าน ConfigMap อยู่แล้ว และ ConfigMap ถูกออกแบบมาสำหรับค่าที่ไม่ลับ (บทที่ 10 หัวข้อ 3.4)

สิ่งที่ร้านต้องการคือ

1. **ที่เก็บแยก** สำหรับความลับ ให้สิทธิ์อ่านแยกจาก Deployment/ConfigMap ได้ เพื่อให้ intern ดูร้านได้ทุกอย่างยกเว้นรหัส
2. Deployment/StatefulSet **อ้างชื่อ** ที่เก็บนั้นแทนการเขียนค่า YAML ที่ใครอ่านก็เห็นแค่ "ชื่อซอง + ชื่อ key"
3. ส่งค่าเข้า Pod ได้ทั้งเป็น env และไฟล์ แบบเดียวกับที่เรียนใน ConfigMap
4. มีตัวเลือกด้านความปลอดภัยเพิ่ม เช่น ไม่พิมพ์ค่าใน `describe`, เก็บไฟล์บนหน่วยความจำ, เข้ารหัสในฐานข้อมูลของคลัสเตอร์

ทั้งหมดนี้คือ **Secret**

{{FIG:T03|อุปมาใหม่ของบทนี้}}

ตารางอุปมาของบทนี้ (ต่อจากอุปมาท่าเรือของบทก่อน ๆ)

| สิ่งใน Kubernetes | อุปมาในท่าเรือของน้องส้ม | ความหมาย |
|---|---|---|
| Secret | ซองสีกรมท่าปิดผนึกครั่งรูปอุ้งเท้าสีส้ม เก็บในกล่องกุญแจเหล็กบนผนังโซน | key–value ที่เป็นความลับ อยู่ใน namespace เดียวกับ Pod |
| base64 ใน `data` | ซองใส | แค่เขียนด้วยตัวอักษรอีกชุด ใครก็แปลงกลับได้ ไม่มีกุญแจ |
| RBAC | บัตรพนักงานคล้องคอ แถบเขียวเปิดกล่องได้ / แถบเทา (intern) ดูได้แค่กระดานและบูธ | กำหนดว่าใคร `get`/`list` Secret ได้ |
| encryption at rest | ประตูตู้นิรภัยกลมในหอบังคับการ หน้าตู้เอกสาร etcd | เข้ารหัส Secret ก่อนเขียนลง etcd |
| Secret volume (tmpfs) | ถาดฟองน้ำความจำในบูธ | ไฟล์อยู่ใน RAM ของ Node ไม่เขียนลงดาดฟ้าเรือ (ดิสก์) |
| TLS Secret | ท่อส่งแก้วปิดสนิทพร้อมเหรียญใบรับรอง | ใบรับรอง + กุญแจส่วนตัวสำหรับ HTTPS |
| `imagePullSecrets` | บัตรผ่านประตูคลังตู้สินค้าส่วนตัว | user/password ของ registry ที่ต้อง login |
| projected volume | แฟ้มห่วงรวมการ์ด + ซอง + ป้ายชื่อบูธ | รวม ConfigMap, Secret, Downward API ในโฟลเดอร์เดียว |
| service-account-token | บัตรพนักงานหุ่นยนต์แถบบาร์โค้ดยาว | token ของ ServiceAccount สำหรับคุยกับ API server |

> **ตัวละครเดิมที่ยังอยู่:** หุ่นยนต์ลูกเรือ kubelet (บทที่ 3, 10) เป็นคนเปิดซองแล้วนำค่าไปใส่ให้ Pod, กระดานประกาศ (ConfigMap, บทที่ 10) อยู่ข้างกล่องกุญแจ, บัตรพนักงานเฉพาะโซน (RBAC, บทที่ 4) ถูกใช้หนักขึ้นในบทนี้

---

## 2. Secret คืออะไร และต่างจาก ConfigMap อย่างไร

### 2.1 กายวิภาคของ Secret

Secret เป็น object ใน API group หลัก (`v1`) แบบ namespaced (ผลจริงจาก `kubectl api-resources`)

```text
NAME                                SHORTNAMES   APIVERSION                        NAMESPACED   KIND
secrets                                          v1                                true         Secret
```

สังเกตว่า Secret **ไม่มีชื่อย่อ** (ConfigMap มี `cm`) ต้องพิมพ์ `secret` หรือ `secrets` เต็ม ๆ ลองสร้าง Secret แรกด้วยคำสั่ง

```bash
kubectl create secret generic demo --from-literal=username=som --from-literal=password=meow1234
kubectl get secret demo
kubectl get secret demo -o yaml
```

```text
secret/demo created
NAME   TYPE     DATA   AGE
demo   Opaque   2      0s
apiVersion: v1
data:
  password: bWVvdzEyMzQ=
  username: c29t
kind: Secret
metadata:
  creationTimestamp: "2026-10-05T11:31:58Z"
  name: demo
  namespace: default
  resourceVersion: "742"
  uid: 9129defa-e305-4359-b188-df70f9e70f61
type: Opaque
```

| ฟิลด์ | ความหมาย |
|---|---|
| `data` | map ของ key → **ค่าที่เข้ารหัส base64** (ระบบเก็บแบบนี้เสมอ เพราะค่าอาจเป็นไฟล์ไบนารีก็ได้) |
| `stringData` | map ของ key → ข้อความธรรมดา ใช้ **ตอนเขียน** เท่านั้น ระบบแปลงเป็น base64 แล้วรวมลง `data` ให้ (หัวข้อ 4.2) |
| `type` | ชนิดของ Secret บอกว่าต้องมี key อะไร (หัวข้อ 3) ค่าเริ่มคือ `Opaque` |
| `immutable` | `true` = แก้ `data` ไม่ได้อีก (หัวข้อ 5.5) |
| `metadata.namespace` | Secret อยู่ใน namespace และ Pod ใช้ได้เฉพาะ Secret ใน namespace เดียวกัน |

ในคลัสเตอร์ใหม่ของ kind มี Secret ของระบบอยู่ตัวเดียวคือ `bootstrap-token-abcdef` ใน `kube-system` (type `bootstrap.kubernetes.io/token` ใช้ตอน Node เข้าร่วมคลัสเตอร์) ส่วน namespace อื่นยังว่าง

```text
NAMESPACE     NAME                     TYPE                            DATA   AGE
kube-system   bootstrap-token-abcdef   bootstrap.kubernetes.io/token   6      49s
```

### 2.2 เหมือน ConfigMap ตรงไหน ต่างตรงไหน

{{FIG:T04|Secret เทียบกับ ConfigMap}}

| เรื่อง | ConfigMap (บทที่ 10) | Secret (บทนี้) |
|---|---|---|
| เก็บอะไร | ค่าตั้งค่าที่ไม่ลับ (ชื่อร้าน, ธีม, ไฟล์ config) | ความลับ (รหัสผ่าน, token, กุญแจ TLS, credential ของ registry) |
| ขนาด | ≤ 1 MiB | ≤ 1 MiB (ผลจริง `data: Too long: may not be more than 1048576 bytes`) |
| ขอบเขต | namespaced | namespaced |
| รูปแบบใน API | `data` เป็นข้อความ | `data` เป็น **base64** (+ `stringData` ตอนเขียน) |
| `type` | ไม่มี | มี (`Opaque`, `kubernetes.io/tls`, …) ตรวจ key ให้ |
| `kubectl describe` | แสดงค่าเต็ม | แสดงแค่จำนวนไบต์ เช่น `password:  8 bytes` |
| ใช้เป็น env | `configMapKeyRef`, `envFrom.configMapRef` | `secretKeyRef`, `envFrom.secretRef` |
| ใช้เป็นไฟล์ | volume บนดิสก์ของ Node | volume แบบ **tmpfs** (อยู่ใน RAM) |
| RBAC | resource `configmaps` | resource `secrets` แยกกัน → ให้ดู ConfigMap ได้แต่ไม่ให้ดู Secret ได้ |
| เข้ารหัสใน etcd | ไม่ได้ออกแบบมาเพื่อสิ่งนี้ | เปิด encryption at rest ได้ (หัวข้อ 9) |
| ใช้กับส่วนอื่นของระบบ | – | `imagePullSecrets`, TLS ของ Ingress, token ของ ServiceAccount |

ข้อจำกัดขนาด 1 MiB เหมือนกัน ผลจริงเมื่อลองใส่ไฟล์ 1.1 MB

```bash
head -c 1100000 /dev/zero > big.bin; kubectl create secret generic huge --from-file=big.bin; rm -f big.bin
```

```text
error: failed to create secret Secret "huge" is invalid: data: Too long: may not be more than 1048576 bytes
```

### 2.3 base64 ไม่ใช่การเข้ารหัส

{{FIG:T05|base64 ไม่ใช่การเข้ารหัส}}

ความเข้าใจผิดที่พบบ่อยที่สุดคือ "Secret ปลอดภัยเพราะค่าถูกเข้ารหัสแล้ว" ค่าใน `data` เป็นแค่ **base64** ซึ่งเป็นการเขียนไบต์ด้วยตัวอักษร 64 ตัว (A–Z, a–z, 0–9, `+`, `/`) เพื่อให้ใส่ข้อมูลไบนารีลงใน JSON/YAML ได้ **ไม่มีกุญแจ** ใครได้ข้อความไปก็แปลงกลับได้ทันที

```bash
kubectl get secret demo -o jsonpath='{.data.password}'; echo
kubectl get secret demo -o jsonpath='{.data.password}' | base64 -d; echo
echo bWVvdzEyMzQ= | base64 -d; echo
```

```text
bWVvdzEyMzQ=
meow1234
meow1234
```

ดังนั้น **ใครที่ `get` Secret ได้ = อ่านรหัสได้** การเห็นข้อความ `bWVvdzEyMzQ=` บนจอที่แชร์หรือในไฟล์ที่ commit ไว้ก็เท่ากับเห็น `meow1234` ซองใสไม่ได้ปิดอะไรเลย มันแค่ทำให้ "อ่านด้วยตาเปล่าไม่ออก" ในเสี้ยววินาทีแรก

### 2.4 กับดัก newline ของ echo

{{FIG:T06|กับดัก newline ของ echo}}

เวลาเตรียมค่า base64 เองเพื่อใส่ใน `data` ต้องระวัง `echo` ที่เติมขึ้นบรรทัดใหม่ (`\n`) ต่อท้ายเสมอ

```bash
echo meow1234 | base64
echo -n meow1234 | base64
echo bWVvdzEyMzQK | base64 -d | od -c | head -2
```

```text
bWVvdzEyMzQK
bWVvdzEyMzQ=
0000000   m   e   o   w   1   2   3   4  \n
0000011
```

`bWVvdzEyMzQK` ถอดกลับได้ 9 ไบต์ (`meow1234\n`) รหัสจึงผิดไปหนึ่งตัวอักษรที่มองไม่เห็น แอปจะ login ฐานข้อมูลไม่ผ่านโดยที่ดูด้วยตาไม่ออก ใช้ `echo -n` หรือ `printf '%s' meow1234` แทน กับดักเดียวกันเกิดกับ `--from-file` ถ้าไฟล์มี newline ท้าย (หัวข้อ 4.1)

### 2.5 ความปลอดภัยจริงมาจากหลายชั้น

{{FIG:T07|ชั้นป้องกันที่แท้จริง}}

ถ้า base64 ไม่ได้ปกป้องอะไร แล้ว Secret ดีกว่าการเขียนรหัสใน Deployment ตรงไหน คำตอบคือ Secret เป็น **จุดรวมที่ Kubernetes ใส่กลไกความปลอดภัยให้ได้** ซึ่ง env ใน Deployment ทำไม่ได้

| ชั้น | กลไก | ป้องกันอะไร | หัวข้อ |
|---|---|---|---|
| 1 | **RBAC** แยก resource `secrets` | คนที่ดู Deployment/ConfigMap ได้ไม่จำเป็นต้องดู Secret ได้ | 8 |
| 2 | **encryption at rest** | คนที่ได้ไฟล์ etcd หรือ backup ไปอ่านค่าไม่ได้ | 9 |
| 3 | **tmpfs** บน Node | ไฟล์ความลับไม่ถูกเขียนลงดิสก์ของ Node | 5.3 |
| 4 | Node ได้เฉพาะ Secret ของ Pod บน Node นั้น | kubelet ดึงเฉพาะ Secret ที่ Pod บน Node ตัวเองใช้ | 5.3 |
| 5 | `describe` ไม่พิมพ์ค่า | ลดการรั่วโดยบังเอิญบนจอ/ในล็อกการสอน | 8.3 |
| 6 | วินัยของทีม | ไม่ commit ลง git, ไม่พิมพ์ลง log, เปลี่ยนรหัสเป็นระยะ | 10 |

ถ้าขาดชั้นที่ 1 และ 2 (เช่น ให้ทุกคนมีสิทธิ์ `get secrets` และ etcd ไม่เข้ารหัส อย่างค่าเริ่มของ kind) Secret ก็ปลอดภัยกว่า env ใน Deployment เพียงเล็กน้อย

---

## 3. type ของ Secret

### 3.1 type ที่ใช้บ่อย

{{FIG:T08|type ของ Secret}}

`type` บอกว่า Secret นี้ใช้ทำอะไร และ API server จะตรวจว่ามี key ที่จำเป็นครบหรือไม่

| type | สร้างด้วย | key ที่ต้องมี | ใช้ทำอะไร |
|---|---|---|---|
| `Opaque` (ค่าเริ่ม) | `kubectl create secret generic` | อะไรก็ได้ | รหัสผ่าน DB, API key, `DATABASE_URL` |
| `kubernetes.io/basic-auth` | `create secret generic --type=kubernetes.io/basic-auth` | `username` และ/หรือ `password` (อย่างน้อย 1) | user/password แบบมาตรฐาน |
| `kubernetes.io/dockerconfigjson` | `kubectl create secret docker-registry` | `.dockerconfigjson` | login registry (`imagePullSecrets`) |
| `kubernetes.io/tls` | `kubectl create secret tls` | `tls.crt`, `tls.key` (PEM) | ใบรับรอง HTTPS (nginx, Ingress) |
| `kubernetes.io/service-account-token` | YAML + annotation `kubernetes.io/service-account.name` | ระบบเติม `token`, `ca.crt`, `namespace` ให้ | token ถาวรของ ServiceAccount (แบบเก่า) |
| `bootstrap.kubernetes.io/token` | kubeadm | `token-id`, `token-secret`, … | Node เข้าร่วมคลัสเตอร์ (เห็นใน `kube-system`) |

ทุก type เก็บใน `data` เป็น base64 เหมือนกัน type ไม่ได้ทำให้ปลอดภัยขึ้น แค่ช่วยให้ "รูปซอง" ถูกแบบ

### 3.2 type ตรวจ key ให้

{{FIG:T09|type ตรวจ key ให้}}

ผลจริงจาก LAB 2 และ LAB 4

```text
$ kubectl create secret generic onlypw --type=kubernetes.io/basic-auth --from-literal=password=meow1234; kubectl get secret onlypw
secret/onlypw created
NAME     TYPE                       DATA   AGE
onlypw   kubernetes.io/basic-auth   1      0s
$ kubectl create secret generic emptyba --type=kubernetes.io/basic-auth
error: failed to create secret Secret "emptyba" is invalid: [data[username]: Required value, data[password]: Required value]
$ kubectl create secret generic badtls --type=kubernetes.io/tls --from-file=tls.crt=pw.txt
error: failed to create secret Secret "badtls" is invalid: data[tls.key]: Required value
$ kubectl create secret tls badtls2 --cert=pw.txt --key=pw.txt
error: tls: failed to find any PEM data in certificate input
$ kubectl create secret tls badtls --cert=tls.crt --key=../lab02-types/pw.txt
error: tls: failed to find any PEM data in key input
```

- `basic-auth` ใส่แค่ `password` อย่างเดียวได้ แต่ว่างทั้งคู่ไม่ได้
- `tls` ที่ขาด `tls.key` ถูก API server ปฏิเสธ (`Required value`)
- `kubectl create secret tls` ตรวจรูปแบบ PEM ฝั่ง client ก่อนส่ง ไฟล์ที่ไม่ใช่ PEM ได้ `failed to find any PEM data in certificate input` (ถ้า cert ผิด) หรือ `... in key input` (ถ้า cert ถูกแต่ key ผิด)

ส่วน `Opaque` ไม่ตรวจอะไรเลย ใส่ key อะไรก็ได้ ความผิดพลาดจะไปโผล่ตอนแอปใช้ค่านั้น

### 3.3 dockerconfigjson: บัตรผ่านคลังที่ก็อ่านได้เหมือนกัน

{{FIG:T10|dockerconfigjson}}

`kubectl create secret docker-registry` สร้าง Secret ชนิด `kubernetes.io/dockerconfigjson` ที่มี key เดียวชื่อ `.dockerconfigjson` ซึ่งเป็นไฟล์รูปแบบเดียวกับ `~/.docker/config.json` (ค่าในตัวอย่างเป็นค่าสมมติเพื่อการเรียน)

```bash
kubectl create secret docker-registry regcred --docker-server=registry.example.com --docker-username=som --docker-password=example-pass --docker-email=som@example.com
kubectl get secret regcred -o jsonpath='{.data.\.dockerconfigjson}' | base64 -d; echo
echo c29tOmV4YW1wbGUtcGFzcw== | base64 -d; echo
```

```text
secret/regcred created
{"auths":{"registry.example.com":{"username":"som","password":"example-pass","email":"som@example.com","auth":"c29tOmV4YW1wbGUtcGFzcw=="}}}
som:example-pass
```

รหัสผ่านของ registry ปรากฏสองครั้ง: ตรง ๆ ใน `password` และใน `auth` ที่เป็น base64 ของ `username:password` อีกชั้น ใครอ่าน Secret นี้ได้ก็ login registry แทนเราได้ (การใช้งานจริงอยู่ในหัวข้อ 6) จุดน่าสังเกตคือ jsonpath ต้องเขียน `.data.\.dockerconfigjson` เพราะชื่อ key ขึ้นต้นด้วยจุด

### 3.4 service-account-token: บัตรพนักงานหุ่นยนต์แบบไม่มีวันหมดอายุ

{{FIG:T11|token ของ ServiceAccount}}

Pod ทุกตัวได้ token ของ ServiceAccount อยู่แล้วโดยอัตโนมัติ (หัวข้อ 5.3) แต่ถ้าต้องการ token ไปใช้ **นอกคลัสเตอร์** เช่น ให้ระบบ CI เรียก API มีสองทาง

**ทางเก่า: Secret ชนิด `kubernetes.io/service-account-token`** ไฟล์ `labs/lab06-projected/builder-token.yaml`

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: builder
---
apiVersion: v1
kind: Secret
metadata:
  name: builder-token
  annotations:
    kubernetes.io/service-account.name: builder
type: kubernetes.io/service-account-token
```

ใส่แค่ annotation ชื่อ ServiceAccount แล้วระบบ (token controller) เติม `ca.crt`, `namespace` และ `token` ให้เอง ผลจริง (token ตัดเหลือ `eyJhbGciOi...`)

```text
NAME            TYPE                                  DATA   AGE
builder-token   kubernetes.io/service-account-token   3      3s
Name:         builder-token
Namespace:    default
Labels:       <none>
Annotations:  kubernetes.io/service-account.name: builder
              kubernetes.io/service-account.uid: b3f1b5c9-628c-4420-9e3a-a1a24f1a794e

Type:  kubernetes.io/service-account-token

Data
====
ca.crt:     1107 bytes
namespace:  7 bytes
token:      eyJhbGciOi...
```

> ⚠️ **`kubectl describe` แสดง token เต็มทั้งเส้น** (ต่างจาก Secret ชนิดอื่นที่แสดงแค่จำนวนไบต์) ในเอกสารนี้ตัดเหลือ `eyJhbGciOi...` เสมอ ห้ามแปะ token จริงลงรายงาน แชท หรือภาพหน้าจอ token แบบนี้ **ไม่มีวันหมดอายุ** จนกว่าจะลบ Secret

ตั้งแต่ Kubernetes v1.24 ระบบไม่สร้าง Secret แบบนี้ให้ ServiceAccount อัตโนมัติแล้ว ผลจริง `kubectl get sa builder -o yaml` ไม่มีฟิลด์ `secrets:` เลย

**ทางที่แนะนำ: `kubectl create token`** ได้ token ที่มีอายุ (bound token) ไม่ถูกเก็บเป็น Secret ใน etcd

```bash
kubectl create token builder --duration=10m | cut -d. -f2 | base64 -d 2>/dev/null | head -c 400; echo
```

```text
{"aud":["https://kubernetes.default.svc.cluster.local"],"exp":1791200849,"iat":1791200249,"iss":"https://kubernetes.default.svc.cluster.local","jti":"016bfa55-e5c5-450e-bc07-1ba3ed989451","kubernetes.io":{"namespace":"default","serviceaccount":{"name":"builder","uid":"b3f1b5c9-628c-4420-9e3a-a1a24f1a794e"}},"nbf":1791200249,"sub":"system:serviceaccount:default:builder"}
```

token เป็น JWT สามท่อนคั่นด้วยจุด ท่อนกลาง (payload) เป็นแค่ base64 อีกเช่นกัน จึงอ่านได้ว่าเป็นของใคร (`sub`) และหมดอายุเมื่อไร (`exp` − `iat` = 600 วินาที = 10 นาที) แต่ปลอมไม่ได้เพราะมีลายเซ็นในท่อนที่สาม LAB 9 ใช้วิธีนี้ในสคริปต์ `rbac/intern-context.sh` เพื่อสร้าง context ของ intern ที่ token อายุ 24 ชั่วโมง

### 3.5 Opaque: ค่าเริ่มที่ใช้บ่อยที่สุด

{{FIG:T12|Opaque ค่าเริ่ม}}

`kubectl create secret generic` ได้ type `Opaque` เสมอ ถ้าไม่ระบุ `--type` เหมาะกับข้อมูลลับทั่วไปของแอป ร้านน้องส้มใช้ Secret `som-db-secret` ชนิด `Opaque` ที่มี 2 key

| key | ค่า (ตัวอย่างเพื่อการเรียน) | ใครใช้ |
|---|---|---|
| `POSTGRES_PASSWORD` | `meow1234` | container `postgres` ของ StatefulSet `som-db` (ใช้ตอน initdb ครั้งแรก) |
| `DATABASE_URL` | `postgres://som:meow1234@som-db-0.som-db:5432/catshop` | init container `db-seed` และ container `web` ของ Deployment `som-web` |

ผลจริง `kubectl -n som-shop describe secret som-db-secret` บอกแค่ขนาด

```text
Type:  Opaque

Data
====
DATABASE_URL:       52 bytes
POSTGRES_PASSWORD:  8 bytes
```

---

## 4. วิธีสร้าง Secret

### 4.1 --from-literal และ --from-file

{{FIG:T13|สร้างด้วย literal และ file}}

`kubectl create secret generic` รับค่าได้หลายแบบ และ **เข้ารหัส base64 ให้เอง**

```bash
kubectl create secret generic demo --from-literal=username=som --from-literal=password=meow1234
kubectl create secret generic fromfile --from-file=db-password=pw.txt
```

`--from-file=db-password=pw.txt` = key ชื่อ `db-password` ค่าคือเนื้อไฟล์ทั้งไฟล์ (ไม่ใส่ `db-password=` จะได้ key ตามชื่อไฟล์ `pw.txt`) ไฟล์ `labs/lab02-types/pw.txt` มี 8 ไบต์ ไม่มี newline ท้าย เทียบกับไฟล์ที่สร้างด้วย `echo`

```text
$ od -c pw.txt
0000000   m   e   o   w   1   2   3   4
0000010
$ kubectl get secret fromfile -o jsonpath='{.data}'; echo
{"db-password":"bWVvdzEyMzQ="}
$ echo meow1234 > pw-nl.txt; kubectl create secret generic fromfile-nl --from-file=db-password=pw-nl.txt; kubectl get secret fromfile-nl -o jsonpath='{.data}'; echo
secret/fromfile-nl created
{"db-password":"bWVvdzEyMzQK"}
```

ไฟล์ที่มี newline ท้ายได้ค่า `bWVvdzEyMzQK` (มี `\n`) ซึ่งเป็นกับดักเดียวกับหัวข้อ 2.4 editor หลายตัวเติม newline ท้ายไฟล์ให้อัตโนมัติ จึงควรสร้างไฟล์รหัสด้วย `printf '%s' 'รหัส' > ไฟล์`

ข้อควรรู้อื่น ๆ

- `kubectl create` ใช้สร้างใหม่เท่านั้น สร้างซ้ำได้ `error: failed to create secret secrets "demo" already exists`
- `--dry-run=client -o yaml` ให้ kubectl เขียน YAML ให้โดยไม่ส่งไป API server (ค่าใน `data` เป็น base64 แล้ว)

```text
$ kubectl create secret generic demo2 --from-literal=password=meow1234 --dry-run=client -o yaml
apiVersion: v1
data:
  password: bWVvdzEyMzQ=
kind: Secret
metadata:
  name: demo2
```

- ข้อเสียของ `--from-literal` คือรหัสไปค้างใน **shell history** (`~/.bash_history`) ในระบบจริงควรอ่านจากไฟล์ที่ป้องกันไว้ หรือเว้นวรรคหน้าคำสั่งเมื่อ shell ตั้ง `HISTCONTROL=ignorespace` (ใน LAB ใช้ค่าตัวอย่างจึงไม่เป็นไร)

### 4.2 YAML: data กับ stringData

{{FIG:T14|data กับ stringData}}

ถ้าเขียน Secret เป็นไฟล์ YAML ใส่ค่าได้สองที่ ไฟล์ `labs/lab02-types/sd.yaml` ทดลองใส่ key `PASSWORD` ซ้ำทั้งสองที่

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: sd
type: Opaque
data:
  PASSWORD: bWVvdzEyMzQ=            # = base64 ของ meow1234 (แค่เปลี่ยนตัวอักษร ไม่ใช่การเข้ารหัส)
stringData:
  PASSWORD: override-by-stringData   # ทับ data.PASSWORD
  USERNAME: som                      # ระบบแปลงเป็น base64 เก็บใน data ให้เอง
```

ผลจริงหลัง `kubectl apply -f sd.yaml`

```text
$ kubectl get secret sd -o jsonpath='{.data.PASSWORD}' | base64 -d; echo
override-by-stringData
```

| | `data` | `stringData` |
|---|---|---|
| ใส่ค่าแบบไหน | base64 (ต้องแปลงเอง ระวัง newline) | ข้อความตรง ๆ |
| เก็บจริงที่ไหน | `data` | ระบบแปลงเป็น base64 แล้ว **รวมลง `data`** ไม่มี `stringData` ใน object ที่เก็บ |
| key ซ้ำกัน | แพ้ | **ชนะ** |
| เหมาะกับ | ค่าไบนารี, YAML ที่เครื่องมือสร้างให้ | เขียนด้วยมือ, template |

ฟิลด์ที่ API server เก็บจริงมีแค่ `data` (`PASSWORD: b3ZlcnJpZGUtYnktc3RyaW5nRGF0YQ==`, `USERNAME: c29t`) แต่ถ้าสร้างด้วย `kubectl apply` จะมีของแถมที่อันตราย ดูหัวข้อถัดไป

### 4.3 กับดัก: kubectl apply + stringData

{{FIG:T15|กับดัก last-applied-configuration}}

`kubectl apply` เก็บสำเนาไฟล์ที่ apply ไว้ใน annotation `kubectl.kubernetes.io/last-applied-configuration` เพื่อใช้เทียบครั้งถัดไป (เรื่องเดียวกับที่ทำให้ intern เห็น `som:meow1234@` 4 ที่ในหัวข้อ 1) เมื่อไฟล์มี `stringData` **annotation ก็เก็บ stringData เป็นข้อความ** ผลจริง

```text
$ kubectl get secret sd -o yaml
apiVersion: v1
data:
  PASSWORD: b3ZlcnJpZGUtYnktc3RyaW5nRGF0YQ==
  USERNAME: c29t
kind: Secret
metadata:
  annotations:
    kubectl.kubernetes.io/last-applied-configuration: |
      {"apiVersion":"v1","data":{"PASSWORD":"bWVvdzEyMzQ="},"kind":"Secret","metadata":{"annotations":{},"name":"sd","namespace":"default"},"stringData":{"PASSWORD":"override-by-stringData","USERNAME":"som"},"type":"Opaque"}
...
```

รหัสจึงปรากฏซ้ำอีกที่ในรูปที่ไม่ต้อง decode ด้วยซ้ำ (ใครอ่าน Secret ได้ก็อ่าน annotation ได้อยู่แล้ว แต่รหัสจะโผล่ในทุกที่ที่มีคนแปะ `get -o yaml` เช่น ticket หรือแชท) ทางเลี่ยงที่ทดลองแล้ว

| วิธี | annotation ที่ได้ (ผลจริง) |
|---|---|
| `kubectl create secret generic ...` | ไม่มี annotation |
| `kubectl create secret generic viapipe --from-literal=PASSWORD=pipe-pass-01 --dry-run=client -o yaml \| kubectl apply -f -` | มี แต่เก็บเป็น base64 ใน `data`: `{"apiVersion":"v1","data":{"PASSWORD":"cGlwZS1wYXNzLTAx"},...}` |
| `... --dry-run=client -o yaml \| kubectl apply --server-side -f -` | `secret/viass serverside-applied` และ **ไม่มี** annotation last-applied (server-side apply ใช้ `managedFields` แทน) |
| `kubectl apply -f` ไฟล์ที่มี `stringData` | มี และ **เก็บข้อความ** ❌ |

วิธีที่สองเป็นวิธีมาตรฐานสำหรับ "อัปเดต Secret ที่มีอยู่แล้วด้วยคำสั่ง create" (เพราะ `create` อย่างเดียวได้ `already exists`) ครั้งแรกที่ apply ทับ Secret ที่สร้างด้วย `create` จะมี Warning `missing the kubectl.kubernetes.io/last-applied-configuration annotation` ซึ่งเป็นเรื่องปกติ kubectl เติม annotation ให้เอง LAB 9 ใช้วิธีนี้ตอนเปลี่ยนรหัส

### 4.4 อ่านค่ากลับ

```bash
kubectl get secret demo -o jsonpath='{.data.password}' | base64 -d; echo
kubectl get secret demo -o go-template='{{range $k,$v := .data}}{{$k}}={{$v | base64decode}}{{"\n"}}{{end}}'
```

```text
meow1234
password=meow1234
username=som
```

go-template ของ kubectl มีฟังก์ชัน `base64decode` ในตัว จึงถอดทุก key ได้ในคำสั่งเดียว คำสั่งพวกนี้มีประโยชน์ตอนแก้ปัญหา แต่ก็เป็นเหตุผลว่าทำไม **สิทธิ์ `get secrets` = สิทธิ์อ่านรหัส** (หัวข้อ 8)

---

