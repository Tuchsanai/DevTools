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

| รูปที่ | เรื่อง | รูปที่ | เรื่อง |
|:---:|---|:---:|---|
| 1 | [เปิดบท ซองปิดผนึกในกล่องกุญแจ](#fig-1) | 21 | [kubelet ตรวจบัตรซ้ำ](#fig-21) |
| 2 | [ทวนบท 010 รหัสผ่านยังเห็นได้](#fig-2) | 22 | [ใบรับรองกับกุญแจ](#fig-22) |
| 3 | [อุปมาใหม่ของบทนี้](#fig-3) | 23 | [HTTPS ด้วย nginx และ curl](#fig-23) |
| 4 | [Secret เทียบกับ ConfigMap](#fig-4) | 24 | [intern ถูกปฏิเสธ](#fig-24) |
| 5 | [base64 ไม่ใช่การเข้ารหัส](#fig-5) | 25 | [อ่าน Secret ทางอ้อม](#fig-25) |
| 6 | [กับดัก newline ของ echo](#fig-6) | 26 | [describe เทียบกับ get](#fig-26) |
| 7 | [ชั้นป้องกันที่แท้จริง](#fig-7) | 27 | [etcd เก็บเป็นข้อความ](#fig-27) |
| 8 | [type ของ Secret](#fig-8) | 28 | [เปิด encryption at rest](#fig-28) |
| 9 | [type ตรวจ key ให้](#fig-9) | 29 | [ใครยังอ่าน etcd ได้](#fig-29) |
| 10 | [dockerconfigjson](#fig-10) | 30 | [อย่า commit ลง git](#fig-30) |
| 11 | [token ของ ServiceAccount](#fig-11) | 31 | [ทางรั่วที่พบบ่อย](#fig-31) |
| 12 | [Opaque ค่าเริ่ม](#fig-12) | 32 | [เปลี่ยนรหัสสองฝั่ง](#fig-32) |
| 13 | [สร้างด้วย literal และ file](#fig-13) | 33 | [Sealed Secrets](#fig-33) |
| 14 | [data กับ stringData](#fig-14) | 34 | [External Secrets และ Vault](#fig-34) |
| 15 | [กับดัก last-applied-configuration](#fig-15) | 35 | [projected volume](#fig-35) |
| 16 | [env จาก secretKeyRef](#fig-16) | 36 | [ตาราง ConfigMap กับ Secret](#fig-36) |
| 17 | [volume แบบ tmpfs](#fig-17) | 37 | [แนวปฏิบัติ](#fig-37) |
| 18 | [env รั่วง่าย](#fig-18) | 38 | [cheatsheet คำสั่ง](#fig-38) |
| 19 | [อัปเดตและ immutable](#fig-19) | 39 | [ต่อไป Ingress HPA Helm](#fig-39) |
| 20 | [imagePullSecrets](#fig-20) | | |

---

## 1. บทนำ: รหัสผ่านยังอยู่ใน YAML

<p align="center" id="fig-1">
  <img src="images/01-opening-sealed-envelope.png" alt="รูปที่ 1 เปิดบท ซองปิดผนึกในกล่องกุญแจ" width="900"><br>
  <em><b>รูปที่ 1</b> เปิดบทที่ 11: ต่อจากบท 010 — ป้ายร้านอยู่ใน ConfigMap แล้ว แต่รหัส DB ยังอยู่ใน YAML ที่ใครก็อ่านได้ น้องส้มจึงย้ายรหัสใส่ซองปิดผนึกในกล่องกุญแจ</em>
</p>

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

<p align="center" id="fig-2">
  <img src="images/02-recap-password-visible.png" alt="รูปที่ 2 ทวนบท 010 รหัสผ่านยังเห็นได้" width="900"><br>
  <em><b>รูปที่ 2</b> ทวนบท 010: intern ที่อ่านได้แค่ Deployment ก็เห็น postgres://som:meow1234@... และ POSTGRES_PASSWORD ใน StatefulSet</em>
</p>

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

<p align="center" id="fig-3">
  <img src="images/03-metaphor-legend.png" alt="รูปที่ 3 อุปมาใหม่ของบทนี้" width="900"><br>
  <em><b>รูปที่ 3</b> อุปมาใหม่: Secret = ซองปิดผนึกในกล่องกุญแจ, base64 = ซองใส (แปลงรูปเฉย ๆ), RBAC = บัตรพนักงานที่เปิดกล่องได้/ไม่ได้, encryption at rest = ตู้นิรภัยในหอบังคับการ</em>
</p>

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

<p align="center" id="fig-4">
  <img src="images/04-secret-vs-configmap.png" alt="รูปที่ 4 Secret เทียบกับ ConfigMap" width="900"><br>
  <em><b>รูปที่ 4</b> Secret ใช้คล้าย ConfigMap (key-value, ≤ 1 MiB, namespaced, env/volume) แต่ data เก็บเป็น base64, describe ไม่แสดงค่า, volume เป็น tmpfs และแยกสิทธิ์ RBAC ได้</em>
</p>

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

<p align="center" id="fig-5">
  <img src="images/05-base64-not-encryption.png" alt="รูปที่ 5 base64 ไม่ใช่การเข้ารหัส" width="900"><br>
  <em><b>รูปที่ 5</b> base64 ไม่ใช่การเข้ารหัส: bWVvdzEyMzQ= | base64 -d → meow1234 ใครมีข้อความก็แปลงกลับได้ทันที ไม่ต้องมีกุญแจ</em>
</p>

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

<p align="center" id="fig-6">
  <img src="images/06-echo-newline-trap.png" alt="รูปที่ 6 กับดัก newline ของ echo" width="900"><br>
  <em><b>รูปที่ 6</b> ระวัง newline: echo meow1234 | base64 → bWVvdzEyMzQK (มี \n ติดไปด้วย รหัสจะผิด) ต้องใช้ echo -n → bWVvdzEyMzQ=</em>
</p>

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

<p align="center" id="fig-7">
  <img src="images/07-real-protection-layers.png" alt="รูปที่ 7 ชั้นป้องกันที่แท้จริง" width="900"><br>
  <em><b>รูปที่ 7</b> ความปลอดภัยของ Secret ไม่ได้มาจาก base64 แต่มาจากหลายชั้น: RBAC ใครอ่านได้, encryption at rest ใน etcd, tmpfs บน Node, ไม่พิมพ์ค่าใน describe และการไม่ commit ลง git</em>
</p>

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

<p align="center" id="fig-8">
  <img src="images/08-secret-types.png" alt="รูปที่ 8 type ของ Secret" width="900"><br>
  <em><b>รูปที่ 8</b> type บอกรูปแบบ key: Opaque (อิสระ), kubernetes.io/basic-auth (username/password), kubernetes.io/dockerconfigjson (.dockerconfigjson), kubernetes.io/tls (tls.crt/tls.key), kubernetes.io/service-account-token</em>
</p>

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

<p align="center" id="fig-9">
  <img src="images/09-type-validation.png" alt="รูปที่ 9 type ตรวจ key ให้" width="900"><br>
  <em><b>รูปที่ 9</b> type ตรวจ key ให้: basic-auth ว่างเปล่า → data[username]: Required value, data[password]: Required value; tls ไม่มี key → data[tls.key]: Required value; key ไม่ใช่ PEM → failed to find any PEM data in key input</em>
</p>

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

<p align="center" id="fig-10">
  <img src="images/10-dockerconfigjson.png" alt="รูปที่ 10 dockerconfigjson" width="900"><br>
  <em><b>รูปที่ 10</b> kubectl create secret docker-registry regcred → type dockerconfigjson เก็บ {"auths":{server:{username,password,auth}}} — decode ได้รหัสเต็ม ๆ เช่นกัน</em>
</p>

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

<p align="center" id="fig-11">
  <img src="images/11-service-account-token.png" alt="รูปที่ 11 token ของ ServiceAccount" width="900"><br>
  <em><b>รูปที่ 11</b> Secret ชนิด service-account-token (ใส่ annotation kubernetes.io/service-account.name) → ระบบเติม token, ca.crt, namespace ให้; ระวัง kubectl describe แสดง token เต็ม ๆ — ปัจจุบันใช้ kubectl create token (มีอายุ) แทน</em>
</p>

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

<p align="center" id="fig-12">
  <img src="images/12-opaque-default.png" alt="รูปที่ 12 Opaque ค่าเริ่ม" width="900"><br>
  <em><b>รูปที่ 12</b> kubectl create secret generic = type Opaque (ค่าปกติ) ใส่ key อะไรก็ได้ เหมาะกับรหัส DB และ DATABASE_URL ของร้าน</em>
</p>

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

<p align="center" id="fig-13">
  <img src="images/13-create-literal-file.png" alt="รูปที่ 13 สร้างด้วย literal และ file" width="900"><br>
  <em><b>รูปที่ 13</b> --from-literal=password=meow1234 หรือ --from-file=db-password=pw.txt (ไฟล์ไม่มี newline) — kubectl เข้ารหัส base64 ให้เอง</em>
</p>

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

<p align="center" id="fig-14">
  <img src="images/14-data-vs-stringdata.png" alt="รูปที่ 14 data กับ stringData" width="900"><br>
  <em><b>รูปที่ 14</b> YAML: data ต้องใส่ base64 เอง; stringData ใส่ข้อความตรง ๆ แล้วระบบแปลงให้ — ถ้า key ซ้ำ stringData ชนะ (ทดสอบแล้ว) และระบบเก็บเป็น data แต่ถ้าสร้างด้วย kubectl apply ข้อความ stringData จะติดอยู่ใน annotation last-applied ด้วย</em>
</p>

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

<p align="center" id="fig-15">
  <img src="images/15-last-applied-leak.png" alt="รูปที่ 15 กับดัก last-applied-configuration" width="900"><br>
  <em><b>รูปที่ 15</b> กับดัก: kubectl apply ไฟล์ที่มี stringData → annotation kubectl.kubernetes.io/last-applied-configuration เก็บข้อความรหัสแบบไม่ base64 ไว้ด้วย; ใช้ kubectl create secret หรือ apply --server-side</em>
</p>

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

<p align="center" id="fig-16">
  <img src="images/16-env-secret-key-ref.png" alt="รูปที่ 16 env จาก secretKeyRef" width="900"><br>
  <em><b>รูปที่ 16</b> env.valueFrom.secretKeyRef (name + key) หรือ envFrom.secretRef — เหมือน ConfigMap: ค่าถูกคัดลอกตอนเริ่ม ไม่เปลี่ยนจนกว่าจะได้ Pod ใหม่</em>
</p>

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

<p align="center" id="fig-17">
  <img src="images/17-volume-tmpfs.png" alt="รูปที่ 17 volume แบบ tmpfs" width="900"><br>
  <em><b>รูปที่ 17</b> volume ของ Secret เป็น tmpfs (อยู่ในหน่วยความจำ ไม่เขียนลงดิสก์ Node) ไฟล์ละ key ผ่าน ..data และตั้ง defaultMode: 0400 ได้ (ทดสอบ: mount = tmpfs ro)</em>
</p>

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

<p align="center" id="fig-18">
  <img src="images/18-env-leak.png" alt="รูปที่ 18 env รั่วง่าย" width="900"><br>
  <em><b>รูปที่ 18</b> env รั่วง่าย: kubectl exec ... env, /proc/1/environ, log ที่พิมพ์ตัวแปร, crash dump — ไฟล์ใน volume ปลอดภัยกว่าและอัปเดตได้</em>
</p>

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

<p align="center" id="fig-19">
  <img src="images/19-update-and-immutable.png" alt="รูปที่ 19 อัปเดตและ immutable" width="900"><br>
  <em><b>รูปที่ 19</b> แก้ Secret → ไฟล์ใน volume เปลี่ยนเอง (วัดได้ราว 1 นาที 71–81 วินาที) แต่ env ไม่เปลี่ยน; immutable: true ใช้ได้เหมือน ConfigMap (data: Forbidden: field is immutable when `immutable` is set)</em>
</p>

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

<p align="center" id="fig-20">
  <img src="images/20-image-pull-secrets.png" alt="รูปที่ 20 imagePullSecrets" width="900"><br>
  <em><b>รูปที่ 20</b> registry ที่ต้อง login → Pod ใส่ imagePullSecrets: [{name: regcred}] หรือผูกไว้กับ ServiceAccount; ไม่มีบัตร → ErrImagePull no basic auth credentials, บัตรผิด → 401 Unauthorized</em>
</p>

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

<p align="center" id="fig-21">
  <img src="images/21-pull-recheck-cached.png" alt="รูปที่ 21 kubelet ตรวจบัตรซ้ำ" width="900"><br>
  <em><b>รูปที่ 21</b> Kubernetes v1.37 (ทดสอบแล้ว): image ที่เคยดึงด้วย imagePullSecrets มาอยู่บน Node แล้ว Pod อื่นที่ไม่มีบัตรก็ยังใช้ไม่ได้ (kubelet ตรวจสิทธิ์ซ้ำ) แม้ imagePullPolicy: IfNotPresent</em>
</p>

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

<p align="center" id="fig-22">
  <img src="images/22-tls-cert-key.png" alt="รูปที่ 22 ใบรับรองกับกุญแจ" width="900"><br>
  <em><b>รูปที่ 22</b> kubernetes.io/tls เก็บ tls.crt (ใบรับรอง แจกได้) + tls.key (กุญแจส่วนตัว ห้ามรั่ว) สร้าง self-signed ด้วย openssl req -x509 แล้ว kubectl create secret tls</em>
</p>

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

<p align="center" id="fig-23">
  <img src="images/23-https-nginx-curl.png" alt="รูปที่ 23 HTTPS ด้วย nginx และ curl" width="900"><br>
  <em><b>รูปที่ 23</b> nginx mount Secret TLS แล้วฟัง 443 ssl: curl https://... → (60) SSL certificate problem: self-signed certificate; curl -k ข้ามการตรวจ; curl --cacert tls.crt ตรวจผ่านอย่างถูกต้อง</em>
</p>

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

<p align="center" id="fig-24">
  <img src="images/24-rbac-intern-forbidden.png" alt="รูปที่ 24 intern ถูกปฏิเสธ" width="900"><br>
  <em><b>รูปที่ 24</b> ต่อบท 004: Role ของ intern ให้ get/list pods, configmaps → kubectl auth can-i get secrets = no และ get secret ได้ Error from server (Forbidden)</em>
</p>

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

<p align="center" id="fig-25">
  <img src="images/25-rbac-indirect-read.png" alt="รูปที่ 25 อ่าน Secret ทางอ้อม" width="900"><br>
  <em><b>รูปที่ 25</b> สิทธิ์สร้าง Pod = อ่าน Secret ทางอ้อมได้: ServiceAccount maker (get secrets = no) สร้าง Pod ที่ใส่ secretKeyRef แล้ว kubectl logs เห็นค่า — จำกัดสิทธิ์ create pods ใน namespace ที่มีความลับ</em>
</p>

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

<p align="center" id="fig-26">
  <img src="images/26-describe-vs-get.png" alt="รูปที่ 26 describe เทียบกับ get" width="900"><br>
  <em><b>รูปที่ 26</b> kubectl describe secret แสดงแค่ขนาด (password: 8 bytes) แต่ get secret -o yaml / jsonpath แสดง base64 เต็ม = อ่านได้ — สิทธิ์ get secrets จึงเท่ากับอ่านรหัส</em>
</p>

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

<p align="center" id="fig-27">
  <img src="images/27-etcd-plaintext.png" alt="รูปที่ 27 etcd เก็บเป็นข้อความ" width="900"><br>
  <em><b>รูปที่ 27</b> Secret ทุกตัวถูกเก็บใน etcd ของ control plane — kind ค่าปกติไม่เปิด encryption at rest: etcdctl get /registry/secrets/default/demo เห็นค่ารหัสเป็นข้อความตรง ๆ (ทดสอบแล้ว)</em>
</p>

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

<p align="center" id="fig-28">
  <img src="images/28-encryption-configuration.png" alt="รูปที่ 28 เปิด encryption at rest" width="900"><br>
  <em><b>รูปที่ 28</b> เปิด encryption at rest: EncryptionConfiguration (resources: secrets, providers: aescbc/secretbox/kms v2 แล้วตามด้วย identity) + kube-apiserver --encryption-provider-config แล้วเขียน Secret ใหม่ทั้งหมดซ้ำ (แนวคิด ไม่ทำใน LAB)</em>
</p>

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

<p align="center" id="fig-29">
  <img src="images/29-who-can-read-etcd.png" alt="รูปที่ 29 ใครยังอ่าน etcd ได้" width="900"><br>
  <em><b>รูปที่ 29</b> แม้เข้ารหัสแล้ว ผู้ดูแลที่มีสิทธิ์ API/etcd/backup หรือ root บน Node ยังเข้าถึงได้ — ปกป้องไฟล์ backup ของ etcd และจำกัดสิทธิ์ cluster-admin</em>
</p>

encryption at rest ป้องกัน "คนที่ได้ไฟล์ etcd หรือ backup ไป" แต่ไม่ได้ป้องกัน

- ผู้ใช้ที่มีสิทธิ์ `get/list secrets` ผ่าน API (API server ถอดรหัสให้ตามปกติ) → ต้องใช้ RBAC
- `cluster-admin` และคนที่สร้าง Pod ได้ (หัวข้อ 8.2)
- root บน control plane ที่อ่านไฟล์กุญแจของ `aescbc` ได้ (เหตุผลที่โปรดักชันใช้ KMS)
- root บน worker Node ที่อ่าน tmpfs ของ Pod หรือ credential ของ kubelet ได้

ดังนั้นต้อง **ปกป้องไฟล์ backup ของ etcd** เหมือนเป็นรหัสผ่าน จำกัดคนที่มี `cluster-admin` และเข้าถึง Node ให้น้อยที่สุด

---

## 10. ข้อควรระวังในการใช้งานจริง

### 10.1 อย่า commit Secret ลง git

<p align="center" id="fig-30">
  <img src="images/30-never-commit-git.png" alt="รูปที่ 30 อย่า commit ลง git" width="900"><br>
  <em><b>รูปที่ 30</b> อย่า commit Secret YAML/ไฟล์ .env ลง git (base64 อ่านกลับได้): ใส่ใน .gitignore, เก็บแค่ไฟล์ตัวอย่าง *.example.yaml ที่ใช้ค่าปลอม, ถ้าหลุดต้องเปลี่ยนรหัสทันที</em>
</p>

ไฟล์ Secret YAML (ทั้ง `data` ที่เป็น base64 และ `stringData` ที่เป็นข้อความ) และไฟล์ `.env` **ห้ามเข้า git** เพราะ git จำประวัติทุก commit แม้ลบไฟล์ใน commit ถัดไป รหัสก็ยังอยู่ในประวัติ และ repository มักถูก clone/fork ไปหลายที่จนตามลบไม่ได้ แนวทางที่ร้านน้องส้มใช้ในโฟลเดอร์ `som-shop-v7/`

`.gitignore`

```text
# ไฟล์ Secret ที่มีค่าจริง ห้ามเข้า git (ไฟล์ตัวอย่าง *.example.yaml commit ได้)
secret.yaml
*.secret.yaml
*.key
*.crt
```

`examples/05-secret.example.yaml` เก็บเฉพาะ **ไฟล์ตัวอย่างที่ใช้ค่าปลอม** และวางไว้นอกโฟลเดอร์ `k8s/` โดยตั้งใจ เพื่อไม่ให้ `kubectl apply -f k8s/` เขียนรหัสตัวอย่างทับรหัสที่เปลี่ยนแล้ว

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: som-db-secret
  namespace: som-shop
type: Opaque
stringData:
  POSTGRES_PASSWORD: meow1234
  DATABASE_URL: postgres://som:meow1234@som-db-0.som-db:5432/catshop
```

ถ้ารหัสจริงหลุดเข้า git ไปแล้ว **ให้ถือว่ารั่วแล้ว และเปลี่ยนรหัสทันที** (หัวข้อ 10.3) การแก้ประวัติ git ทำได้ยากและไม่รับประกันว่าไม่มีใครได้สำเนาไปก่อน

### 10.2 ทางรั่วที่พบบ่อย

<p align="center" id="fig-31">
  <img src="images/31-leak-checklist.png" alt="รูปที่ 31 ทางรั่วที่พบบ่อย" width="900"><br>
  <em><b>รูปที่ 31</b> ทางรั่วที่พบบ่อย: get secret -o yaml บนจอที่แชร์, แอปพิมพ์ env/DATABASE_URL ลง log, ใส่รหัสใน ConfigMap/annotation/args, คำสั่งที่พิมพ์รหัสค้างใน shell history</em>
</p>

| ทางรั่ว | ตัวอย่าง | ป้องกัน |
|---|---|---|
| จอที่แชร์ / ภาพหน้าจอ | `kubectl get secret -o yaml` ระหว่างสอนหรือประชุม, describe ของ service-account-token | ใช้ `describe` (เว้น SA token), บังรหัสในภาพ (เอกสารนี้ใช้ `●●●●` และ `eyJhbGciOi...`) |
| log ของแอป | แอปพิมพ์ `DATABASE_URL` เต็ม ๆ ตอนเริ่ม หรือ error ของ driver ที่แนบ connection string | ไม่พิมพ์ env ลง log, ตัดรหัสออกจากข้อความ error |
| วางผิดที่ | รหัสใน ConfigMap, annotation, `args` ของ container, label | ความลับอยู่ใน Secret เท่านั้น |
| `kubectl apply` + `stringData` | annotation `last-applied-configuration` เก็บข้อความ | หัวข้อ 4.3 |
| shell history | `--from-literal=PASSWORD=...`, `PGPASSWORD=... psql` | อ่านจากไฟล์ที่ป้องกันไว้ หรือล้าง history |
| แชท / ticket / รายงาน | แปะผลคำสั่งที่มีรหัสหรือ token | ตัดค่าก่อนแปะทุกครั้ง |
| สิทธิ์กว้างเกิน | ให้ `list secrets` หรือ `create pods` กับทุกคน | หัวข้อ 8 |

### 10.3 เปลี่ยนรหัสต้องทำสองฝั่ง

<p align="center" id="fig-32">
  <img src="images/32-rotate-password.png" alt="รูปที่ 32 เปลี่ยนรหัสสองฝั่ง" width="900"><br>
  <em><b>รูปที่ 32</b> เปลี่ยนรหัสต้องทำ 2 ฝั่ง: ฐานข้อมูล (ALTER USER) และ Secret แล้ว rollout restart — POSTGRES_PASSWORD ใช้แค่ตอน initdb ครั้งแรก การแก้ Secret อย่างเดียวไม่เปลี่ยนรหัสใน DB</em>
</p>

ความเข้าใจผิดที่พบบ่อยคือ "แก้ค่า `POSTGRES_PASSWORD` ใน Secret แล้วรหัสฐานข้อมูลจะเปลี่ยน" ความจริงคือ image postgres ใช้ `POSTGRES_PASSWORD` **แค่ตอน initdb ครั้งแรก** (ตอนโฟลเดอร์ข้อมูลใน PVC ยังว่าง) หลังจากนั้นรหัสอยู่ในฐานข้อมูลเอง การแก้ Secret อย่างเดียวไม่มีผลกับฐานข้อมูลที่มีอยู่แล้ว ลำดับที่ถูกต้อง (LAB 9 ขั้น D)

1. **ฝั่งฐานข้อมูล:** `ALTER USER som PASSWORD '<รหัสใหม่>';`
2. **ฝั่ง Secret:** แก้ทั้ง `POSTGRES_PASSWORD` และ `DATABASE_URL` ให้เป็นรหัสใหม่ (`create ... --dry-run=client -o yaml | kubectl apply -f -`)
3. **ให้ Pod อ่านค่าใหม่:** `kubectl rollout restart deploy/som-web` (env อ่านครั้งเดียวตอนเริ่ม)

ระหว่างขั้น 1 กับ 2 คือช่วงอันตราย ผลจริงจาก LAB 9 เมื่อเปลี่ยนรหัสใน DB แล้วยังไม่แก้ Secret

- Pod web เดิมยังตอบได้ **เฉพาะ request ที่ใช้ connection ซึ่งเปิดค้างอยู่ใน pool** (เปิดไว้ตั้งแต่ก่อนเปลี่ยนรหัส) curl ทันทีจึงอาจได้ 200 หลายครั้ง แต่เมื่อแอปต้องเปิด connection ใหม่ การยืนยันตัวตนไม่ผ่าน หน้าเว็บขึ้น 503 "ร้านกำลังเตรียมสินค้า" **เป็นช่วง ๆ** (ภาพหน้าจอจริงใน LAB 9) ร้านจึง **ไม่ได้ขายได้ปกติ** การที่ Pod เดิมยังตอบบางครั้งไม่ใช่สัญญาณว่ารหัสใหม่ใช้ได้
- ถ้า `rollout restart` ตอนนี้ Pod ใหม่ค้าง `Init:Error` เพราะ `db-seed` ใช้รหัสเก่าจาก Secret ได้ `error: password authentication failed for user "som"` และ rollout หยุดที่ `ProgressDeadlineExceeded` (Pod เดิมไม่ถูกลบเพราะ `maxUnavailable: 0`)

จึงควรทำขั้น 1–3 ต่อเนื่องกันให้เร็วที่สุด หรือใช้วิธีที่ไม่มีช่องว่าง เช่น สร้าง user ใหม่ที่มีรหัสใหม่ก่อน ย้ายแอปไปใช้ แล้วค่อยลบ user เก่า (ระบบภายนอกอย่าง Vault ทำ dynamic credential แบบนี้ให้อัตโนมัติ)

> **ทดสอบรหัสให้ถูกทาง:** `pg_hba.conf` ของ image postgres ตั้ง `host all all 127.0.0.1/32 trust` (เชื่อทุกการเชื่อมต่อจากในเครื่อง) และ `host all all all scram-sha-256` (เครือข่ายต้องใช้รหัส) ผลจริง `PGPASSWORD=wrong-anything psql -h 127.0.0.1 ...` ก็ได้ `1` จึงต้องทดสอบผ่านเครือข่ายด้วย `-h som-db-0.som-db` เสมอ รหัสเก่าได้ `FATAL:  password authentication failed for user "som"` รหัสใหม่ได้ `1`

---

## 11. แนวทางภายนอกคลัสเตอร์

Secret ของ Kubernetes เป็นพื้นฐาน แต่ยังมีโจทย์ที่แก้ไม่ได้ด้วยตัวเอง: จะเก็บ Secret ใน git แบบ GitOps ได้อย่างไร, จะเปลี่ยนรหัสอัตโนมัติอย่างไร, จะรู้ได้อย่างไรว่าใครอ่านรหัสไปเมื่อไร หัวข้อนี้เป็น **แนวคิดเพื่อปูทาง** ยังไม่ติดตั้งใน LAB

### 11.1 Sealed Secrets

<p align="center" id="fig-33">
  <img src="images/33-sealed-secrets.png" alt="รูปที่ 33 Sealed Secrets" width="900"><br>
  <em><b>รูปที่ 33</b> Sealed Secrets: เข้ารหัส Secret ด้วย public key ของ controller ในคลัสเตอร์ → ได้ SealedSecret ที่ commit ลง git ได้ เฉพาะคลัสเตอร์ถอดได้</em>
</p>

**Sealed Secrets** (Bitnami) มี controller ในคลัสเตอร์ถือ private key ไว้ ผู้พัฒนาใช้เครื่องมือ `kubeseal` เข้ารหัส Secret ด้วย public key ของ controller ได้เป็น object ชนิด `SealedSecret` ที่ **commit ลง git ได้** เพราะมีแต่ controller ในคลัสเตอร์นั้นที่ถอดได้ เมื่อ apply แล้ว controller จะสร้าง Secret ปกติให้ ข้อดีคือใช้กับ GitOps ได้ง่าย ข้อจำกัดคือถ้า private key ของ controller หาย ต้องเข้ารหัสใหม่ทั้งหมด และ Secret ที่ได้ในคลัสเตอร์ก็ยังเป็น Secret ธรรมดา (ยังต้องการ RBAC และ encryption at rest)

### 11.2 External Secrets Operator, Vault และ Secrets Store CSI Driver

<p align="center" id="fig-34">
  <img src="images/34-external-secrets-vault.png" alt="รูปที่ 34 External Secrets และ Vault" width="900"><br>
  <em><b>รูปที่ 34</b> External Secrets Operator / Vault / Secrets Store CSI: เก็บความลับในตู้นิรภัยภายนอก แล้วซิงก์หรือ mount เข้า Pod ตามสิทธิ์ — เปลี่ยนรหัสและตรวจ log การเข้าถึงได้ที่เดียว</em>
</p>

| เครื่องมือ | แนวคิด |
|---|---|
| **External Secrets Operator (ESO)** | ความลับอยู่ในตู้นิรภัยภายนอก (AWS Secrets Manager, GCP Secret Manager, Azure Key Vault, Vault) ESO อ่านแล้ว **sync** มาเป็น Secret ในคลัสเตอร์ตามรอบเวลา |
| **HashiCorp Vault** | ตู้นิรภัยกลาง มี audit log ว่าใครอ่านอะไร, นโยบายสิทธิ์ละเอียด และ dynamic secrets (สร้าง user ฐานข้อมูลอายุสั้นให้แต่ละแอป) |
| **Secrets Store CSI Driver** | **mount** ความลับจากตู้ภายนอกเป็นไฟล์ใน Pod โดยตรงผ่าน CSI volume (เลือกได้ว่าจะไม่สร้าง Secret ใน etcd เลย) |

ข้อดีร่วมกันคือ เปลี่ยนรหัสและตรวจการเข้าถึงได้ที่เดียว หลายคลัสเตอร์ใช้แหล่งเดียวกัน แลกกับระบบที่ต้องดูแลเพิ่ม

> **kustomize `secretGenerator`:** แบบเดียวกับ `configMapGenerator` ในบทที่ 10 สร้าง Secret จากไฟล์หรือ literal พร้อมต่อท้ายชื่อด้วย hash ทำให้ Deployment rollout เองเมื่อค่าเปลี่ยน แต่ไฟล์ต้นทางที่มีรหัสก็ยังต้องไม่เข้า git

---

## 12. projected volume: แฟ้มห่วงรวมเอกสาร

<p align="center" id="fig-35">
  <img src="images/35-projected-volume.png" alt="รูปที่ 35 projected volume" width="900"><br>
  <em><b>รูปที่ 35</b> projected รวม configMap + secret + downwardAPI ไว้ในโฟลเดอร์เดียว เช่น /etc/som/announcement.txt, /etc/som/db/password, /etc/som/pod-name (ทดสอบแล้ว)</em>
</p>

บางแอปต้องการไฟล์จากหลายแหล่งในโฟลเดอร์เดียว volume ชนิด `projected` รวม `configMap`, `secret`, `downwardAPI` และ `serviceAccountToken` เข้าด้วยกัน ไฟล์ `labs/lab06-projected/proj.yaml` (ส่วน volume)

```yaml
volumes:
  - name: all
    projected:
      defaultMode: 0440
      sources:
        - configMap:
            name: shop-board
            items:
              - key: announcement.txt
                path: announcement.txt
        - secret:
            name: demo
            items:
              - key: password
                path: db/password          # สร้างโฟลเดอร์ย่อย db/ ให้
        - downwardAPI:
            items:
              - path: pod-name
                fieldRef:
                  fieldPath: metadata.name
```

ผลจริง (ตัดบางส่วน)

```text
$ kubectl exec proj -- ls -laLR /etc/som
/etc/som:
...
-r--r-----    1 root     root            54 Oct  5 11:37 announcement.txt
drwxr-xr-x    2 root     root            60 Oct  5 11:37 db
-r--r-----    1 root     root             4 Oct  5 11:37 pod-name
...
/etc/som/db:
...
-r--r-----    1 root     root            10 Oct  5 11:37 password
$ kubectl exec proj -- sh -c "cat /etc/som/pod-name; echo; cat /etc/som/db/password; echo; cat /etc/som/announcement.txt"
proj
newpass-01
วันนี้ปลาทูสดมาก 🐟
$ kubectl exec proj -- mount | grep /etc/som
tmpfs on /etc/som type tmpfs (ro,relatime,size=64489564k,noswap)
```

- `defaultMode: 0440` ใช้ร่วมกันทุกไฟล์ → `-r--r-----`
- เมื่อมี Secret อยู่ในแหล่ง ทั้งโฟลเดอร์เป็น tmpfs
- token ที่ Pod ได้อัตโนมัติ (`/var/run/secrets/kubernetes.io/serviceaccount/` มี `ca.crt`, `namespace`, `token`) ก็สร้างด้วย projected volume ที่มี `serviceAccountToken` (token อายุสั้น ต่ออายุอัตโนมัติ) ซึ่งต่างจาก service-account-token Secret แบบเก่าในหัวข้อ 3.4

---

## 13. สรุปและปัญหาที่ยังเหลือ

### 13.1 ConfigMap กับ Secret

<p align="center" id="fig-36">
  <img src="images/36-configmap-vs-secret-table.png" alt="รูปที่ 36 ตาราง ConfigMap กับ Secret" width="900"><br>
  <em><b>รูปที่ 36</b> ตารางสรุป ConfigMap vs Secret: เก็บอะไร, รูปแบบ (ข้อความ vs base64), describe, volume (ดิสก์ ro vs tmpfs), RBAC, encryption at rest, ใช้กับ imagePullSecrets/TLS</em>
</p>

| | ConfigMap | Secret |
|---|---|---|
| ใช้เก็บ | ค่าตั้งค่าที่ไม่ลับ | ความลับ |
| รูปแบบใน API | ข้อความ | base64 (ไม่ใช่การเข้ารหัส) |
| `describe` | แสดงค่า | แสดงแค่ไบต์ (ยกเว้น SA token) |
| volume | ดิสก์ของ Node, ro | tmpfs ใน RAM, ro |
| อัปเดต volume | ราว 1 นาที | ราว 1 นาที |
| env | ไม่เปลี่ยนจนได้ Pod ใหม่ | ไม่เปลี่ยนจนได้ Pod ใหม่ |
| RBAC | `configmaps` | `secrets` (ให้แยกได้) |
| encryption at rest | ไม่จำเป็น | ควรเปิด |
| ระบบใช้ด้วย | – | `imagePullSecrets`, TLS ของ Ingress, token |

### 13.2 แนวปฏิบัติ

<p align="center" id="fig-37">
  <img src="images/37-best-practices.png" alt="รูปที่ 37 แนวปฏิบัติ" width="900"><br>
  <em><b>รูปที่ 37</b> แนวปฏิบัติ: สิทธิ์ get/list secrets ให้น้อยที่สุด, เปิด encryption at rest, mount เป็นไฟล์แทน env เมื่อทำได้, ไม่ commit ลง git, เปลี่ยนรหัสเป็นระยะ, ใช้ระบบภายนอกในโปรดักชัน</em>
</p>

1. ให้สิทธิ์ `get`/`list`/`watch secrets` น้อยที่สุด และระวังสิทธิ์ `create pods`/`pods/exec` ใน namespace ที่มีความลับ
2. เปิด encryption at rest (ดีที่สุดคือ KMS) และปกป้อง backup ของ etcd
3. mount เป็นไฟล์แทน env เมื่อแอปรองรับ ตั้ง `defaultMode` ให้แคบ (`0400`/`0440`)
4. ไม่ commit Secret ลง git ใช้ไฟล์ตัวอย่างค่าปลอม + `.gitignore`
5. สร้าง/อัปเดตด้วย `kubectl create secret` (+ `--dry-run=client -o yaml | kubectl apply -f -`) แทน `kubectl apply` ไฟล์ที่มี `stringData`
6. เปลี่ยนรหัสเป็นระยะ และเปลี่ยนทันทีเมื่อสงสัยว่ารั่ว (ทำทั้งฝั่งระบบปลายทางและฝั่ง Secret)
7. ใช้ token ที่มีอายุ (`kubectl create token`) แทน service-account-token Secret แบบถาวร
8. ในโปรดักชันพิจารณาระบบภายนอก (External Secrets, Vault, CSI Driver) หรือ Sealed Secrets สำหรับ GitOps

### 13.3 Cheatsheet คำสั่ง

<p align="center" id="fig-38">
  <img src="images/38-command-cheatsheet.png" alt="รูปที่ 38 cheatsheet คำสั่ง" width="900"><br>
  <em><b>รูปที่ 38</b> cheatsheet: kubectl create secret generic/tls/docker-registry, get secret -o jsonpath | base64 -d, auth can-i get secrets --as, rollout restart</em>
</p>

| งาน | คำสั่ง |
|---|---|
| สร้างแบบทั่วไป | `kubectl create secret generic <ชื่อ> --from-literal=KEY=VALUE --from-file=key=ไฟล์` |
| สร้าง TLS | `kubectl create secret tls <ชื่อ> --cert=tls.crt --key=tls.key` |
| สร้างบัตรผ่าน registry | `kubectl create secret docker-registry <ชื่อ> --docker-server=... --docker-username=... --docker-password=...` |
| อัปเดตของเดิม | `kubectl create secret generic <ชื่อ> ... --dry-run=client -o yaml \| kubectl apply -f -` |
| ดูแบบไม่โชว์ค่า | `kubectl describe secret <ชื่อ>` |
| อ่านค่า | `kubectl get secret <ชื่อ> -o jsonpath='{.data.KEY}' \| base64 -d` |
| ตรวจสิทธิ์ | `kubectl auth can-i get secrets --as=system:serviceaccount:<ns>:<sa>` |
| ให้ Pod ได้ค่าใหม่ (env) | `kubectl rollout restart deploy/<ชื่อ>` |
| token ที่มีอายุ | `kubectl create token <sa> --duration=10m` |
| ผูกบัตรกับ SA | `kubectl patch sa default -p '{"imagePullSecrets":[{"name":"regcred"}]}'` |

### 13.4 ปัญหาที่ยังเหลือ

<p align="center" id="fig-39">
  <img src="images/39-next-ingress-hpa-helm.png" alt="รูปที่ 39 ต่อไป Ingress HPA Helm" width="900"><br>
  <em><b>รูปที่ 39</b> ต่อไป: Ingress (ประตูหน้าเดียวหลายร้าน + TLS ที่ Ingress), HPA (เพิ่มบูธอัตโนมัติตามโหลด), Helm (แพ็กทั้งร้านพร้อม ConfigMap/Secret เป็นชุดเดียว)</em>
</p>

ท้าย LAB 9 ร้านน้องส้มย้ายรหัสออกจาก YAML ไปไว้ใน Secret `som-db-secret` แล้ว intern อ่านซองไม่ได้ เปลี่ยนรหัสจริงสำเร็จโดยออเดอร์ไม่หาย และเปิดร้านผ่าน HTTPS ที่ `https://localhost:30082` ได้ แต่ยังเหลือโจทย์ที่บทต่อ ๆ ไปจะแก้

| ปัญหาที่ยังเหลือ | สภาพตอนนี้ | แนวทางในบทถัดไป |
|---|---|---|
| เปิดร้านด้วยชื่อโดเมนและ TLS ที่ทางเข้าเดียว | ลูกค้าต้องจำพอร์ต 30080 (HTTP) และ 30082 (HTTPS) และเราดูแล nginx + Secret TLS เอง ใบรับรองเป็น self-signed | **Ingress** — ประตูหน้าเดียวรับหลายร้านตามชื่อโดเมน/เส้นทาง ทำ TLS ที่ Ingress โดยอ้าง Secret ชนิด `kubernetes.io/tls` แบบเดียวกับบทนี้ (ต่อด้วย cert-manager) |
| scale web อัตโนมัติ | `replicas: 3` ตายตัว ลูกค้าแน่นก็ยัง 3 บูธ | **HPA (HorizontalPodAutoscaler)** — เพิ่ม/ลดบูธตาม CPU หรือโหลด |
| manifest หลายไฟล์ | `00-namespace`, `10-db`, `15-config`, `20-web`, `30-https`, `rbac/`, คำสั่ง `create secret` แยก ต้อง apply ตามลำดับเอง | **Helm** — แพ็กทั้งร้าน (รวม ConfigMap/Secret) เป็น chart เดียว ติดตั้ง/อัปเกรด/ย้อนรุ่นด้วยคำสั่งเดียว และใช้ checksum ให้ rollout เมื่อค่าเปลี่ยน |
| etcd ยังไม่เข้ารหัส | etcdctl เห็น `postgres://som:purr5678@` เป็นข้อความ | **EncryptionConfiguration** (หัวข้อ 9.2, ดีที่สุดคือ KMS) หรือย้ายความลับไปตู้ภายนอกด้วย **External Secrets Operator / Vault** (หัวข้อ 11) |

### ข้อควรจำของบทนี้

- Secret = ซองปิดผนึก key–value ใน namespace ขนาดรวม ≤ 1 MiB ใช้แบบเดียวกับ ConfigMap (`secretKeyRef`, `envFrom.secretRef`, volume)
- **base64 ไม่ใช่การเข้ารหัส** ใคร `get` ได้ก็ถอดได้ ระวัง `echo` ที่เติม `\n` (ใช้ `echo -n`/`printf`)
- `type` ตรวจ key ให้ (`basic-auth`, `tls`, `dockerconfigjson`) `Opaque` ไม่ตรวจอะไร
- `stringData` ชนะ `data` เมื่อ key ซ้ำ แต่ `kubectl apply` + `stringData` ทิ้งรหัสเป็นข้อความใน `last-applied-configuration` → ใช้ `kubectl create secret` (+ `--dry-run=client -o yaml | kubectl apply -f -`) หรือ `--server-side`
- volume ของ Secret เป็น tmpfs ro อัปเดตเองราว 1 นาที (วัดได้ 71–81 วินาที) env ไม่เปลี่ยนจนได้ Pod ใหม่ `immutable: true` แก้ไม่ได้ต้องลบสร้างใหม่
- `describe` ไม่โชว์ค่า แต่ service-account-token โชว์ token เต็ม
- สิทธิ์ `get`/`list`/`watch secrets`, `create pods`, `pods/exec` = อ่าน Secret ได้
- kind ไม่เปิด encryption at rest: etcd เก็บรหัสเป็นข้อความ
- `imagePullSecrets` ต้องอยู่ namespace เดียวกับ Pod ผูกกับ ServiceAccount ได้ และ kubelet v1.37 ไม่ให้ Pod ที่ไม่มีบัตรยืม image ที่ดึงด้วยบัตร
- เปลี่ยนรหัส DB ต้องทำ 2 ฝั่ง (`ALTER USER` + Secret + `rollout restart`) ช่วงที่ทำไม่ครบ ร้านล่มเป็นช่วง ๆ และ Pod ใหม่ `Init:Error`

---

## 14. คำถามทบทวน

**1. ทำไมการย้าย `DATABASE_URL` ไปไว้ใน ConfigMap จึงไม่แก้ปัญหาที่ intern เห็นรหัสผ่าน แต่การย้ายไป Secret แก้ได้**

<details>
<summary>แนวคำตอบ</summary>

intern มีสิทธิ์ `get/list/watch configmaps` อยู่แล้ว และ ConfigMap เป็นข้อความธรรมดา ย้ายไปก็ยังอ่านได้ ส่วน Secret เป็น resource แยก (`secrets`) ที่ Role ของ intern ไม่ได้ให้สิทธิ์ ผลจริงหลังย้าย `grep -c meow1234` ใน Deployment ได้ `0` เห็นแค่ `secretKeyRef {key: DATABASE_URL, name: som-db-secret}` และ `kubectl --context intern get secret som-db-secret` ได้ `Forbidden` ความปลอดภัยมาจาก RBAC ที่แยกได้ ไม่ได้มาจากรูปแบบการเก็บ
</details>

**2. เพื่อนบอกว่า "Secret ปลอดภัยเพราะเข้ารหัสแล้ว ดูสิ `bWVvdzEyMzQ=` อ่านไม่ออก" จะอธิบายอย่างไร**

<details>
<summary>แนวคำตอบ</summary>

นั่นคือ base64 ซึ่งเป็นการแปลงรูปแบบ ไม่มีกุญแจ `echo bWVvdzEyMzQ= | base64 -d` ได้ `meow1234` ทันที ความปลอดภัยจริงมาจาก RBAC (ใครอ่าน Secret ได้), encryption at rest ใน etcd, tmpfs บน Node และการไม่ commit ลง git ถ้าไม่มีชั้นเหล่านี้ Secret ก็อ่านง่ายพอ ๆ กับ env ใน Deployment
</details>

**3. ใส่ `data: {PASSWORD: bWVvdzEyMzQK}` ใน YAML แล้วแอป login ฐานข้อมูลไม่ผ่าน ทั้งที่ตั้งใจใช้ `meow1234` เกิดจากอะไร**

<details>
<summary>แนวคำตอบ</summary>

`bWVvdzEyMzQK` คือ base64 ของ `meow1234\n` (9 ไบต์) มักเกิดจาก `echo meow1234 | base64` ที่ echo เติมขึ้นบรรทัดใหม่ รหัสจึงมี `\n` ติดท้าย ต้องใช้ `echo -n meow1234 | base64` ได้ `bWVvdzEyMzQ=` หรือใช้ `stringData`/`kubectl create secret --from-literal` ให้ระบบแปลงเอง ปัญหาเดียวกันเกิดกับ `--from-file` ที่ไฟล์มี newline ท้าย (ผลจริง `bWVvdzEyMzQK`)
</details>

**4. ไฟล์ `sd.yaml` มี `PASSWORD` ทั้งใน `data` และ `stringData` หลัง `kubectl apply` ค่าจริงคืออะไร และมีอะไรที่ไม่ควรเกิดขึ้นตามมา**

<details>
<summary>แนวคำตอบ</summary>

ค่าจริงคือค่าจาก `stringData` (`override-by-stringData`) เพราะ stringData ชนะ และระบบรวมลง `data` เป็น base64 แต่เพราะใช้ `kubectl apply` annotation `kubectl.kubernetes.io/last-applied-configuration` เก็บทั้งไฟล์ไว้ รวมถึง `"stringData":{"PASSWORD":"override-by-stringData","USERNAME":"som"}` เป็นข้อความ เลี่ยงได้ด้วย `kubectl create secret ...` หรือ `--dry-run=client -o yaml | kubectl apply -f -` (annotation เก็บเป็น base64) หรือ `kubectl apply --server-side` (ไม่มี annotation)
</details>

**5. `kubectl describe secret` ปลอดภัยกว่า `kubectl get secret -o yaml` จริงหรือไม่**

<details>
<summary>แนวคำตอบ</summary>

ปลอดภัยกว่าเฉพาะเรื่อง "การรั่วบนจอโดยบังเอิญ" เพราะแสดงแค่ `password:  8 bytes` แต่ไม่ใช่การควบคุมสิทธิ์ ทั้งสองคำสั่งใช้สิทธิ์ `get secrets` เหมือนกัน คนที่ describe ได้ก็ใช้ jsonpath + `base64 -d` ได้ และ describe ของ Secret ชนิด `service-account-token` แสดง token เต็มทั้งเส้นด้วย
</details>

**6. แก้รหัสใน Secret `demo` แล้ว ไฟล์ `/etc/secret/password` และ env `DB_PASSWORD` ใน Pod `spod` เปลี่ยนเมื่อไร**

<details>
<summary>แนวคำตอบ</summary>

ไฟล์ใน volume เปลี่ยนเองโดย kubelet ราว 1 นาที (ผลจริง 71 และ 81 วินาที) ไฟล์ใน `/etc/secret400` ก็เปลี่ยนด้วย ส่วน env `DB_PASSWORD` ยังเป็น `meow1234` เพราะ env ถูกคัดลอกครั้งเดียวตอน container เริ่ม ต้องลบแล้วสร้าง Pod ใหม่ (ผลจริงได้ `newpass-01`) หรือ `rollout restart` สำหรับ Deployment ถ้า mount ด้วย `subPath` ไฟล์ก็ไม่อัปเดตเช่นกัน
</details>

**7. ทำไมไฟล์ใน Secret volume จึงอยู่บน tmpfs และ `defaultMode: 0400` ช่วยอะไร มีข้อควรระวังอะไรเมื่อ container ไม่ได้รันเป็น root**

<details>
<summary>แนวคำตอบ</summary>

tmpfs อยู่ในหน่วยความจำ (`noswap`) ความลับจึงไม่ถูกเขียนลงดิสก์ของ Node และหายไปเมื่อ Pod ถูกลบ `0400` ทำให้ไฟล์ `-r--------` อ่านได้แค่เจ้าของ (root) ถ้า container รันเป็นผู้ใช้อื่น (เช่น `nginx-unprivileged` uid 101) จะอ่านไม่ได้ ต้องตั้ง `fsGroup` ให้ไฟล์ได้กลุ่มนั้นและใช้ `defaultMode: 0440` (ผลจริงใน `extra/30-https-restricted.yaml` ได้ `-r--r----- root nginx`)
</details>

**8. ServiceAccount `maker` ไม่มีสิทธิ์ `get secrets` เลย แต่อ่านรหัสใน Secret `demo` ได้อย่างไร และควรป้องกันอย่างไร**

<details>
<summary>แนวคำตอบ</summary>

maker มีสิทธิ์ `create pods` จึงสร้าง Pod `peek` ที่ใช้ `secretKeyRef` ไปที่ `demo` แล้ว `echo` ค่าลง log (`stolen=newpass-01`) kubelet เปิดซองให้ Pod โดยไม่ตรวจว่าคนสร้าง Pod มีสิทธิ์อ่าน Secret ป้องกันโดยจำกัดสิทธิ์สร้าง Pod/Deployment/Job และ `pods/exec` ใน namespace ที่มีความลับ แยก namespace ตามความลับ และใช้ policy (เช่น admission policy) จำกัด Secret ที่ Pod อ้างได้
</details>

**9. Pod ใน namespace `reg2` ที่ไม่มี `imagePullSecrets` ตรึงลง Node ที่มี image `kind-registry:5000/som-menu:1.0` อยู่แล้ว และตั้ง `imagePullPolicy: IfNotPresent` ผลคืออะไร เพราะอะไร**

<details>
<summary>แนวคำตอบ</summary>

ยังดึงไม่ได้ (`ImagePullBackOff`, `no basic auth credentials`) เพราะ kubelet v1.37 จำว่า image นี้ถูกดึงด้วย credential และตรวจสิทธิ์ซ้ำก่อนให้ Pod อื่นใช้ กันไม่ให้ Pod ที่ไม่มีบัตรยืม image ส่วนตัวที่ค้างบน Node ส่วน image ที่โหลดไว้ล่วงหน้าด้วย `kind load` (เช่น `som-shop-web:1.5`) ไม่ได้ผูกกับบัตรจึงใช้ได้ตามปกติ
</details>

**10. `curl https://localhost:30081/` ได้ `(60) SSL certificate problem: self-signed certificate` มีวิธีทดสอบต่ออย่างไรบ้าง วิธีใดที่ "ตรวจจริง"**

<details>
<summary>แนวคำตอบ</summary>

`curl -k` ข้ามการตรวจใบรับรองทั้งหมด ใช้ได้แค่ทดสอบว่า HTTPS ทำงาน แต่ไม่กันการปลอมตัว `curl --cacert tls.crt` บอกให้เชื่อใบรับรองนี้แล้วตรวจจริงทั้งลายเซ็นและชื่อ ซึ่งต้องเรียกด้วยชื่อที่อยู่ใน subjectAltName (`localhost` หรือ `shop.som.local` ผ่าน `--resolve`) ถ้าเรียก `127.0.0.1` จะได้ `no alternative certificate subject name matches target host name '127.0.0.1'`
</details>

**11. kind ไม่เปิด encryption at rest หมายความว่าอะไร และ EncryptionConfiguration แก้ได้แค่ไหน**

<details>
<summary>แนวคำตอบ</summary>

Secret ถูกเขียนลง etcd เป็นข้อความ ผลจริง etcdctl เห็น `newpass-01` และ `postgres://som:purr5678@` ใครได้ไฟล์ etcd หรือ backup ก็อ่านได้โดยไม่ผ่าน RBAC EncryptionConfiguration (`aescbc`/`secretbox`/`kms` ตามด้วย `identity`) ทำให้ข้อมูลใน etcd ถูกเข้ารหัส แต่ผู้ที่มีสิทธิ์ผ่าน API, `cluster-admin`, คนที่สร้าง Pod ได้ และ root บน control plane ที่อ่านไฟล์กุญแจได้ ยังเข้าถึงได้ จึงต้องใช้ร่วมกับ RBAC และ KMS
</details>

**12. หลัง `ALTER USER som PASSWORD 'purr5678'` โดยยังไม่แก้ Secret ร้านเป็นอย่างไร และถ้าสั่ง `rollout restart` ตอนนั้นจะเกิดอะไร**

<details>
<summary>แนวคำตอบ</summary>

Pod web เดิมยังตอบได้เฉพาะ request ที่ใช้ connection ที่ค้างอยู่ใน pool เมื่อต้องเปิด connection ใหม่การยืนยันตัวตนไม่ผ่าน หน้าเว็บขึ้น 503 "ร้านกำลังเตรียมสินค้า" เป็นช่วง ๆ (ล่มเป็นช่วง ไม่ใช่ขายได้ปกติ) ถ้า `rollout restart` Pod ใหม่ค้าง `Init:Error` เพราะ db-seed ใช้รหัสเก่า (`error: password authentication failed for user "som"`, `routine: 'auth_failed'`) Pod เดิมไม่ถูกลบเพราะ `maxUnavailable: 0` และ rollout จบด้วย `ProgressDeadlineExceeded` แก้โดยอัปเดต Secret ทั้ง 2 key เป็นรหัสใหม่แล้ว `rollout restart` อีกครั้ง
</details>

**13. ทำไมแก้ `POSTGRES_PASSWORD` ใน Secret แล้ว `kubectl delete pod som-db-0` รหัสในฐานข้อมูลจึงไม่เปลี่ยน**

<details>
<summary>แนวคำตอบ</summary>

image postgres ใช้ `POSTGRES_PASSWORD` เฉพาะตอน initdb ครั้งแรกที่โฟลเดอร์ข้อมูลว่าง PVC `data-som-db-0` มีข้อมูลอยู่แล้ว (รวมรหัสของ user `som`) Pod ใหม่จึงข้าม initdb รหัสในฐานข้อมูลเปลี่ยนได้ด้วย `ALTER USER` เท่านั้น ผลจริงในขั้น D4 ลบ `som-db-0` แล้ว `count(*)` ยังเป็น 4 และรหัส `purr5678` ที่ตั้งด้วย ALTER USER ยังใช้ได้
</details>

**14. ทดสอบรหัสใหม่ด้วย `psql -h 127.0.0.1` ใน Pod `som-db-0` แล้วผ่าน แม้ใส่รหัสมั่ว ทำไม และควรทดสอบอย่างไร**

<details>
<summary>แนวคำตอบ</summary>

`pg_hba.conf` ของ image ตั้ง `host all all 127.0.0.1/32 trust` การเชื่อมต่อจาก 127.0.0.1 จึงไม่ตรวจรหัสเลย ต้องทดสอบผ่านเครือข่ายด้วย `-h som-db-0.som-db` ซึ่งเข้ากฎ `host all all all scram-sha-256` แบบเดียวกับที่ Pod web ใช้ ผลจริงรหัสเก่าได้ `FATAL:  password authentication failed for user "som"` รหัสใหม่ได้ `1`
</details>

**15. เปรียบเทียบ Sealed Secrets กับ External Secrets Operator ว่าแก้ปัญหาต่างกันอย่างไร**

<details>
<summary>แนวคำตอบ</summary>

Sealed Secrets แก้ปัญหา "เก็บ Secret ใน git" โดยเข้ารหัสด้วย public key ของ controller ได้ SealedSecret ที่ commit ได้ ความลับยังมีแหล่งจริงอยู่ในคลัสเตอร์ External Secrets Operator ย้ายแหล่งความลับไปตู้นิรภัยภายนอก (Vault, cloud secret manager) แล้ว sync เข้ามา เหมาะกับการเปลี่ยนรหัสจากที่เดียว ใช้หลายคลัสเตอร์ และต้องการ audit ทั้งสองแบบยังได้ Secret ปกติในคลัสเตอร์ จึงยังต้องการ RBAC และ encryption at rest
</details>

---

## 15. เอกสารอ้างอิง

1. The Kubernetes Authors. *Secrets*. https://kubernetes.io/docs/concepts/configuration/secret/
2. The Kubernetes Authors. *Good practices for Kubernetes Secrets*. https://kubernetes.io/docs/concepts/security/secrets-good-practices/
3. The Kubernetes Authors. *Managing Secrets using kubectl*. https://kubernetes.io/docs/tasks/configmap-secret/managing-secret-using-kubectl/
4. The Kubernetes Authors. *Managing Secrets using Configuration File*. https://kubernetes.io/docs/tasks/configmap-secret/managing-secret-using-config-file/
5. The Kubernetes Authors. *Distribute Credentials Securely Using Secrets*. https://kubernetes.io/docs/tasks/inject-data-application/distribute-credentials-secure/
6. The Kubernetes Authors. *Pull an Image from a Private Registry*. https://kubernetes.io/docs/tasks/configure-pod-container/pull-image-private-registry/
7. The Kubernetes Authors. *Images — Ensure image pull credential verification*. https://kubernetes.io/docs/concepts/containers/images/
8. The Kubernetes Authors. *Configure Service Accounts for Pods*. https://kubernetes.io/docs/tasks/configure-pod-container/configure-service-account/
9. The Kubernetes Authors. *Service Accounts*. https://kubernetes.io/docs/concepts/security/service-accounts/
10. The Kubernetes Authors. *Encrypting Confidential Data at Rest*. https://kubernetes.io/docs/tasks/administer-cluster/encrypt-data/
11. The Kubernetes Authors. *Using a KMS provider for data encryption*. https://kubernetes.io/docs/tasks/administer-cluster/kms-provider/
12. The Kubernetes Authors. *Using RBAC Authorization*. https://kubernetes.io/docs/reference/access-authn-authz/rbac/
13. The Kubernetes Authors. *Role Based Access Control Good Practices*. https://kubernetes.io/docs/concepts/security/rbac-good-practices/
14. The Kubernetes Authors. *Projected Volumes*. https://kubernetes.io/docs/concepts/storage/projected-volumes/
15. The Kubernetes Authors. *Ingress — TLS*. https://kubernetes.io/docs/concepts/services-networking/ingress/#tls
16. The Kubernetes Authors. *kubectl create secret*. https://kubernetes.io/docs/reference/kubectl/generated/kubectl_create/kubectl_create_secret/
17. The Kubernetes Authors. *Server-Side Apply*. https://kubernetes.io/docs/reference/using-api/server-side-apply/
18. The Kubernetes Authors. *Secrets Store CSI Driver*. https://secrets-store-csi-driver.sigs.k8s.io/
19. Bitnami Labs. *Sealed Secrets*. https://github.com/bitnami-labs/sealed-secrets
20. External Secrets Authors. *External Secrets Operator*. https://external-secrets.io/
21. PostgreSQL Global Development Group. *The pg_hba.conf File*. https://www.postgresql.org/docs/17/auth-pg-hba-conf.html

---

> **หมายเหตุเกี่ยวกับภาพประกอบ:** ภาพประกอบ 39 ภาพในโฟลเดอร์ [`images/`](images/) และภาพตัวละครน้องส้ม ([`00-character-som.png`](images/00-character-som.png)) สร้างขึ้นด้วยปัญญาประดิษฐ์สำหรับการสร้างภาพเพื่อใช้ประกอบการเรียนการสอน ชุดคำสั่งสร้างภาพอยู่ใน [`images/imagegen-prompts.md`](images/imagegen-prompts.md) ภาพใช้อุปมาเชิงเปรียบเทียบเพื่อช่วยความเข้าใจ ตัวเลขและข้อความในภาพเป็นค่าตัวอย่าง ผู้เรียนควรใช้เนื้อหาในเอกสารนี้และเอกสารอ้างอิงเป็นหลัก รหัสผ่านทุกตัวในภาพและเอกสารเป็นค่าตัวอย่างเพื่อการเรียนเท่านั้น ผลลัพธ์คำสั่งทั้งหมดมาจากการทดลองจริง (Kubernetes v1.37.0, kubectl v1.37.1) ค่าเวลา, AGE และชื่อ Pod ในเครื่องผู้เรียนอาจต่างกัน
