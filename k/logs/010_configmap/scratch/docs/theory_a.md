# ConfigMap: กระดานประกาศของโซนที่ทุกบูธอ่านได้

> **รายวิชา:** Software Development Tools and Environments (DevTools)
> **หัวข้อ:** Kubernetes ConfigMap — แยก config ออกจาก image (12-factor), `data`/`binaryData` และขนาด 1 MiB, การสร้าง 4 วิธี (`--from-literal`, `--from-file`, `--from-env-file`, YAML), ใช้เป็น env (`configMapKeyRef`, `envFrom`, `prefix`, `$(VAR)`), ใช้เป็นไฟล์ (volume, `items`, `defaultMode`, `subPath`), ConfigMap/key ที่ไม่มีและ `optional`, การอัปเดต (env ไม่เปลี่ยน, volume อัปเดตเอง, `..data` symlink, แอปต้อง reload, `rollout restart`, checksum annotation), `immutable`, kustomize `configMapGenerator`, ConfigMap ของระบบ, การอ้างข้าม namespace และ RBAC
> **ผลลัพธ์การเรียนรู้ที่เกี่ยวข้อง:** CLO-5, CLO-6
> **บทก่อนหน้า:** [บทที่ 9 StatefulSet](../../009_kubernetes_statefulset/01_Theory/README.md) · **LAB ของบทนี้:** [02_LAB](../02_LAB/README.md)

---

## บทคัดย่อ

บทที่ 9 ร้านอาหารแมวน้องส้มมีครัวกลางแบบโปรดักชันแล้ว (db เป็น StatefulSet `som-db` พร้อมตู้เซฟ `data-som-db-0`) แต่ทุกครั้งที่อยากเปลี่ยน **ชื่อร้าน ธีม หรือโปรโมชัน** ยังต้องแก้ค่าใน `20-web.yaml` หรือ build image ใหม่ เพราะค่าพวกนี้ถูกเขียนตรงใน env ของ Deployment หรือฝังใน image ด้วย `--build-arg` บทนี้แนะนำ **ConfigMap** หรือ **กระดานประกาศไม้ก๊อกของโซน** ที่ติดการ์ด `key: value` ไว้ให้ทุกบูธ (Pod) ใน namespace เดียวกันมาอ่าน แยก "ค่าตั้งค่า" ออกจาก "โค้ดและ image" ตามหลัก 12-factor ทำให้ image เดียวใช้ได้หลายสภาพแวดล้อม

เนื้อหาเริ่มจากว่า config คืออะไรและไม่ใช่อะไร ต่อด้วยโครงสร้างของ ConfigMap (`data`, `binaryData`, ข้อจำกัด 1 MiB, เป็น namespaced object, ไม่ใช่ที่เก็บความลับ) วิธีสร้าง 4 แบบ วิธีส่งค่าเข้า Pod 2 ทาง คือ **ป้ายติดอกพนักงาน** (env/envFrom ซึ่งอ่านครั้งเดียวตอน container เริ่ม) และ **กระดานเล็กในบูธ** (volume ที่ **หุ่นยนต์ลูกเรือ kubelet** เดินมาอัปเดตให้ราวนาทีละครั้ง) จากนั้นดูว่าเกิดอะไรเมื่ออ้าง ConfigMap หรือ key ที่ไม่มี การใช้ `optional` การอัปเดตค่าและเหตุผลที่แอปต้องโหลดใหม่เอง เทคนิคให้ Deployment rollout เมื่อ config เปลี่ยน (`rollout restart`, checksum, ชื่อใหม่) ConfigMap แบบ `immutable` (กระดานเคลือบอะคริลิก) และ `configMapGenerator` ของ kustomize (เครื่องพิมพ์ป้ายที่เติมรหัสท้ายชื่อ) ปิดท้ายด้วย ConfigMap ที่ระบบใช้เอง การอ้างข้าม namespace, RBAC แนวปฏิบัติ และปัญหาที่ยังเหลือ: **รหัสผ่านฐานข้อมูลยังอยู่ใน YAML** ซึ่งเป็นโจทย์ของบทที่ 11

ผลลัพธ์คำสั่งและข้อความ error ที่ยกมาในเอกสารนี้มาจากการทดลองจริงบนคลัสเตอร์ kind (Kubernetes v1.37.0, kubectl v1.37.1, Kustomize v5.8.1) ใน LAB ประจำบทเมื่อ 5 ตุลาคม 2569 **เวลา, AGE, ชื่อ Pod ที่สุ่ม, ชื่อโฟลเดอร์ `..2026_10_05_…` และจำนวนวินาทีที่ไฟล์อัปเดตในเครื่องผู้เรียนจะต่างจากตัวอย่าง**

## วัตถุประสงค์การเรียนรู้

เมื่อศึกษาเอกสารนี้จบ ผู้เรียนควรสามารถ

1. อธิบายปัญหาของการฝังค่าตั้งค่าไว้ใน image หรือใน YAML ของ Deployment และหลัก 12-factor เรื่องการแยก config ออกจากโค้ด
2. แยกได้ว่าข้อมูลแบบใดควรอยู่ใน ConfigMap แบบใดควรอยู่ใน PVC และแบบใดเป็นความลับที่ไม่ควรอยู่ใน ConfigMap
3. อธิบายโครงสร้างของ ConfigMap (`data`, `binaryData`, `immutable`) ข้อจำกัดขนาด 1 MiB และความเป็น namespaced object
4. สร้าง ConfigMap ด้วย `--from-literal`, `--from-file`, `--from-env-file` และ YAML รวมถึงใช้ `--dry-run=client -o yaml` สร้างไฟล์และอัปเดตของเดิม
5. ส่งค่าเข้า container ด้วย `env.valueFrom.configMapKeyRef`, `envFrom` (พร้อม `prefix`) และอ้าง `$(VAR)` ใน `command`/`args` ได้ พร้อมบอกลำดับความสำคัญเมื่อชื่อซ้ำ
6. mount ConfigMap เป็นไฟล์ด้วย volume, `items`, `defaultMode` และ `subPath` และอธิบายความต่างด้านการอัปเดตของแต่ละแบบ
7. อ่านอาการ `CreateContainerConfigError` และ `FailedMount` จาก ConfigMap/key ที่ไม่มี และใช้ `optional: true` ได้ถูกที่
8. อธิบายกลไกการอัปเดตไฟล์ใน volume (kubelet sync, `..data` symlink) เหตุผลที่แอปต้อง reload เอง และเลือกวิธีทำให้ Pod ได้ค่าใหม่ (`rollout restart`, checksum annotation, ชื่อใหม่/generator)
9. ใช้ `immutable: true` และ kustomize `configMapGenerator` ได้ พร้อมบอกข้อดีข้อเสีย
10. บอกตัวอย่าง ConfigMap ที่ระบบใช้เอง อธิบายว่าทำไม Pod อ้าง ConfigMap ข้าม namespace ไม่ได้ และกำหนดสิทธิ์ RBAC สำหรับ ConfigMap ได้

## สารบัญ

1. [บทนำ: เปลี่ยนป้ายร้านต้อง build ใหม่ทุกครั้ง](#1-บทนำ-เปลี่ยนป้ายร้านต้อง-build-ใหม่ทุกครั้ง)
2. [ปัญหา: ค่าตั้งค่าฝังอยู่ใน image และ YAML](#2-ปัญหา-ค่าตั้งค่าฝังอยู่ใน-image-และ-yaml)
3. [ConfigMap คืออะไร](#3-configmap-คืออะไร)
4. [วิธีสร้าง ConfigMap](#4-วิธีสร้าง-configmap)
5. [ใช้ ConfigMap เป็นตัวแปร env](#5-ใช้-configmap-เป็นตัวแปร-env)
6. [ใช้ ConfigMap เป็นไฟล์ (volume)](#6-ใช้-configmap-เป็นไฟล์-volume)
7. [ConfigMap หรือ key ที่ไม่มี และ optional](#7-configmap-หรือ-key-ที่ไม่มี-และ-optional)
8. [การอัปเดต ConfigMap](#8-การอัปเดต-configmap)
9. [immutable: ConfigMap ที่แก้ไม่ได้](#9-immutable-configmap-ที่แก้ไม่ได้)
10. [kustomize configMapGenerator](#10-kustomize-configmapgenerator)
11. [ConfigMap ในคลัสเตอร์จริง ข้าม namespace และ RBAC](#11-configmap-ในคลัสเตอร์จริง-ข้าม-namespace-และ-rbac)
12. [แนวปฏิบัติและสรุป](#12-แนวปฏิบัติและสรุป)
13. [คำถามทบทวน](#13-คำถามทบทวน)
14. [เอกสารอ้างอิง](#14-เอกสารอ้างอิง)

### สารบัญรูปภาพ

{{FIGTOC}}

---

## 1. บทนำ: เปลี่ยนป้ายร้านต้อง build ใหม่ทุกครั้ง

{{FIG:T01}}

ร้านอาหารแมวน้องส้มเดินทางมาไกลแล้ว: บทที่ 5–7 มีหน้าร้าน (web) 3 บูธที่ผู้จัดการร้าน (Deployment) ดูแลและเปลี่ยนรุ่นได้โดยไม่สะดุด บทที่ 6 มีประภาคาร (Service NodePort 30080) บทที่ 8–9 ครัวกลาง (db) มีตู้เซฟประจำตัวและชื่อคงที่ `som-db-0` ออเดอร์ไม่หายแม้ Pod ถูกสร้างใหม่

แต่วันหนึ่งน้องส้มอยากทำสิ่งที่ดูง่ายมาก คือ **เปลี่ยนชื่อร้านเป็น "ร้านน้องส้ม สาขาท่าเรือ" เปลี่ยนธีมเป็นสีส้ม และขึ้นป้ายโปรโมชัน** แล้วก็พบว่าต้องเปิดไฟล์ YAML ของ Deployment แก้ค่าในหลายจุด หรือแย่กว่านั้นคือ build image ใหม่ เพราะธีมและข้อความบางส่วนถูก "ฝัง" ไว้ใน image ตอน build

{{FIG:T02}}

ลองดูสภาพท้ายบทที่ 9 ใน `som-shop-v5/k8s/20-web.yaml` ค่าที่เกี่ยวกับ "หน้าตาร้าน" ถูกเขียนตรง ๆ ใน `env` ของ container ปนกับค่าการเชื่อมต่อฐานข้อมูล (ตัดมาเฉพาะส่วนที่เกี่ยวข้อง)

```yaml
containers:
  - name: web
    image: som-shop-web:1.2          # รุ่นและธีมฝังอยู่ใน image (APP_VERSION/APP_THEME)
    env:
      - name: SHOP_NAME
        value: "ร้านอาหารแมวน้องส้ม"
      - name: SHOP_FOOTER
        value: "Next.js + PostgreSQL · Kubernetes LAB 009 · namespace $(POD_NAMESPACE)"
      - name: DATABASE_URL
        value: postgres://som:meow1234@som-db-0.som-db:5432/catshop
```

ปัญหาที่ซ่อนอยู่มี 3 ข้อ

1. **ค่าตั้งค่าผูกกับ manifest ของแอป** อยากเปลี่ยนชื่อร้านต้องแก้ไฟล์ Deployment ทั้งที่โค้ดและ image ไม่ได้เปลี่ยน ถ้ามีหลาย Deployment ใช้ค่าเดียวกันก็ต้องแก้ทุกไฟล์
2. **ธีมและเวอร์ชันฝังใน image** (`--build-arg APP_THEME=harbor`) อยากได้ธีม sunset ต้อง build image ใหม่ เช่น รุ่น 1.3 ของบทที่ 7 ที่ build ด้วย `APP_THEME=sunset`
3. **รหัสผ่านฐานข้อมูล `meow1234` อยู่ในไฟล์เดียวกัน** ใครเปิดไฟล์หรืออ่าน Deployment ได้ก็เห็นรหัส (บทนี้จะแก้ข้อ 1–2 ส่วนข้อ 3 ส่งต่อบทที่ 11)

> รหัส `meow1234` ในเอกสารนี้เป็น **ค่าตัวอย่างเพื่อการเรียนเท่านั้น** ห้ามใช้กับระบบจริง

{{FIG:T03}}

บทนี้ใช้อุปมาใหม่ต่อจากท่าเรือ Kubernetes ของบทก่อน ๆ

| อุปมา | ของจริงใน Kubernetes | ลักษณะสำคัญ |
|---|---|---|
| กระดานประกาศไม้ก๊อกของโซน มีการ์ด `key: value` | **ConfigMap** | อยู่ใน namespace (โซน) เดียว บูธในโซนเดียวกันอ่านได้ |
| ป้ายโน้ตติดอกพนักงาน ถ่ายจากกระดานตอนเข้ากะ | **env / envFrom** | อ่านครั้งเดียวตอน container เริ่ม กระดานเปลี่ยนแล้วป้ายบนอกไม่เปลี่ยน ต้องเข้ากะใหม่ (Pod ใหม่) |
| กระดานเล็กในบูธ ที่หุ่นยนต์ลูกเรือ (kubelet) เดินมาอัปเดต | **volume จาก ConfigMap** | ทุก key เป็นไฟล์ อัปเดตเองราว 1 นาที แต่แอปต้องอ่านใหม่เอง |
| สำเนาการ์ดแปะเทป | **subPath** | ไฟล์เดียวไม่ทับโฟลเดอร์ แต่ไม่มีใครมาเปลี่ยนให้ |
| ป้ายลูกศรที่สลับไปชุดการ์ดใหม่ทีเดียว | **`..data` symlink** | ไฟล์เปลี่ยนพร้อมกันทั้งชุด ไม่ค้างครึ่ง ๆ กลาง ๆ |
| กระดานเคลือบแผ่นอะคริลิกติดตราประทับ | **`immutable: true`** | แก้ไม่ได้ ต้องสร้างใหม่ |
| เครื่องพิมพ์ป้ายที่พิมพ์รหัสท้ายชื่อ | **kustomize `configMapGenerator`** | เนื้อหาเปลี่ยน = ชื่อใหม่ = Deployment rollout เอง |

---

## 2. ปัญหา: ค่าตั้งค่าฝังอยู่ใน image และ YAML

### 2.1 ค่าฝังใน image: เปลี่ยนป้ายครั้งเดียวต้อง build ใหม่

{{FIG:T04}}

แอปร้านน้องส้ม (Next.js) อ่านธีมจาก env `APP_THEME` และใน `Dockerfile` ตั้งค่าเริ่มไว้จาก build-arg

```dockerfile
ARG APP_VERSION=dev
ARG APP_THEME=harbor
ENV APP_VERSION=$APP_VERSION \
    APP_THEME=$APP_THEME
```

ถ้าเราถือว่า "ธีมเป็นส่วนหนึ่งของ image" การเปลี่ยนธีมครั้งเดียวต้องทำทั้งสายพาน: `docker build` → `kind load docker-image` (หรือ push ขึ้น registry) → แก้ tag ใน Deployment → rollout ทั้งที่โค้ดไม่ได้เปลี่ยนเลยสักบรรทัด และถ้ามี dev/test/prod ที่อยากได้ชื่อร้านต่างกันก็ต้องมี image คนละ tag ซึ่งทำให้ "สิ่งที่ทดสอบผ่านใน test" ไม่ใช่ image เดียวกับที่ขึ้น prod

> ข่าวดีคือ env ที่ตั้งใน Pod **ทับ** `ENV` ใน image ได้เสมอ และหน้าเว็บของแอปเป็น `force-dynamic` (อ่าน env ตอนรัน ไม่ใช่ตอน build) ดังนั้นถ้าย้ายค่าออกมาไว้นอก image แอปเดิมก็ใช้ได้ทันที

### 2.2 หลัก 12-factor: แยก config ออกจากโค้ด

{{FIG:T05}}

แนวคิด [The Twelve-Factor App](https://12factor.net/config) ข้อที่ 3 (Config) บอกว่า **config คือทุกอย่างที่ต่างกันระหว่างการ deploy** (dev, staging, prod) และควรเก็บแยกจากโค้ด แอปควรอ่าน config จากสภาพแวดล้อมตอนรัน (เช่น environment variable หรือไฟล์) ผลคือ

- **build ครั้งเดียว ใช้ได้ทุกที่** image เดียวกันผ่านการทดสอบแล้วขึ้น prod ได้ทันที เปลี่ยนแค่ค่าที่ส่งเข้าไป
- **เปลี่ยนค่าโดยไม่แตะโค้ด** คนดูแลระบบปรับค่าได้โดยไม่ต้อง build
- **ทดสอบง่ายว่าแอปทนค่าผิด** เพราะค่าถูกส่งเข้ามาจากข้างนอกชัดเจน

Kubernetes มี object สำหรับเรื่องนี้โดยตรงสองตัว คือ **ConfigMap** (ค่าทั่วไป บทนี้) และ **Secret** (ค่าลับ บทที่ 11)

### 2.3 อะไรคือ config และอะไรไม่ใช่

{{FIG:T06}}

| ข้อมูล | ตัวอย่างในร้านน้องส้ม | ควรอยู่ที่ไหน |
|---|---|---|
| ค่าตั้งค่าสั้น ๆ | ชื่อร้าน, ธีม `harbor`/`sunset`, ข้อความโปรโมชัน, ระดับ log | **ConfigMap** → env |
| ไฟล์ตั้งค่า/ข้อความยาว | `announcement.txt` (ประกาศหน้าร้าน), `default.conf` ของ nginx, `Corefile` ของ CoreDNS | **ConfigMap** → volume |
| ข้อมูลที่แอปสร้างและต้องจำ | ออเดอร์, สต็อกสินค้าใน postgres | **PVC** (บทที่ 8–9) ไม่ใช่ ConfigMap |
| ความลับ | รหัสผ่านฐานข้อมูล, token, private key | **Secret** (บทที่ 11) ไม่ใช่ ConfigMap |
| โค้ดและ dependency | Next.js, `node_modules` | **image** |
| ไฟล์ใหญ่ (หลาย MB) | รูปสินค้า, โมเดล, ฐานข้อมูลตั้งต้น | image หรือ volume อื่น (ConfigMap รับได้ไม่เกิน 1 MiB) |

หลักจำง่าย ๆ: **ConfigMap = ค่าที่ "คนตั้ง" และอ่านได้โดยไม่เสียหายถ้ารั่ว** ส่วนข้อมูลที่ "แอปเขียน" ไปไว้ PVC และข้อมูลที่ "รั่วไม่ได้" ไปไว้ Secret

---

## 3. ConfigMap คืออะไร

### 3.1 กายวิภาคของ ConfigMap

{{FIG:T07}}

**ConfigMap** เป็น API object (`apiVersion: v1`, `kind: ConfigMap`) ที่เก็บคู่ **key–value** ไว้ให้ Pod อ้างถึง ต่างจาก Pod/Deployment ตรงที่ **ไม่มี `spec` และ `status`** ไม่มี controller คอยทำอะไร มันเป็นแค่ "ข้อมูล" ที่วางอยู่ใน API server จนกว่าจะมี Pod มาอ่าน

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: shop-config            # ชื่อกระดาน (ไม่ซ้ำใน namespace เดียวกัน)
  namespace: default
data:                          # ข้อความ UTF-8
  SHOP_NAME: "ร้านน้องส้ม"      # ค่าสั้น 1 บรรทัด
  APP_THEME: "sunset"
  announcement.txt: |          # | = ค่าหลายบรรทัด (เนื้อไฟล์ทั้งไฟล์)
    วันนี้ปลาทูสด
binaryData:                    # ไฟล์ไบนารี เก็บเป็น base64
  logo.bin: XIW0LDQ8x9pHOwF0PEo1Xw==
```

| ฟิลด์ | ความหมาย |
|---|---|
| `data` | map ของ key → **ข้อความ** (UTF-8) ใช้บ่อยที่สุด ค่าทุกตัวเป็น string จึงต้องใส่เครื่องหมายคำพูดให้ค่าที่ YAML จะตีความเป็นตัวเลขหรือ boolean เช่น `PRICE: "99"`, `ENABLED: "true"` |
| `binaryData` | map ของ key → ข้อมูลไบนารีแบบ base64 ใช้กับไฟล์ที่ไม่ใช่ข้อความ เวลาสร้างด้วย `--from-file` จากไฟล์ที่ไม่ใช่ UTF-8 kubectl จะใส่ไว้ที่นี่ให้เอง (ทดสอบใน LAB 1: `logo.bin` 16 bytes ไปอยู่ `binaryData`) |
| `immutable` | `true` = ห้ามแก้ `data`/`binaryData` อีก (หัวข้อ 9) |
| key | ใช้ได้เฉพาะตัวอักษร ตัวเลข `-`, `_`, `.` และ key เดียวกันห้ามอยู่ทั้งใน `data` และ `binaryData` |

ผล `kubectl describe` แยกสองส่วนให้เห็นชัด (ผลจริงจาก LAB 1)

```text
BinaryData
====
logo.bin: 16 bytes
```

> `binaryData` **ไม่ถูกนำไปเป็นตัวแปร env** — `kubectl explain pod.spec.containers.env.valueFrom.configMapKeyRef` บอกไว้ว่า `Keys in the BinaryData field are not currently propagated to container env vars.` ถ้าจะใช้ไฟล์ไบนารีต้อง mount เป็น volume

### 3.2 ขนาดไม่เกิน 1 MiB

{{FIG:T08}}

ConfigMap ทั้งก้อน (รวมทุก key) ใหญ่ได้ไม่เกิน **1 MiB = 1,048,576 bytes** เพราะทุก object ถูกเก็บใน etcd และถูกส่งให้ kubelet ทุก Node ที่มี Pod ใช้ ทดสอบจริงใน LAB 1

```text
-rw-r--r-- 1 root root 1100000 Oct  5 16:47 big.txt
error: failed to create configmap: ConfigMap "big" is invalid: []: Too long: may not be more than 1048576 bytes
```

ไฟล์ขนาด 1,048,000 bytes ยังสร้างได้ (`configmap/big2 created`) ถ้าต้องใช้ไฟล์ใหญ่กว่านี้ ให้ใส่ไว้ใน image หรือ volume ชนิดอื่น ConfigMap เหมาะกับ "ค่าตั้งค่า" ขนาดเล็กเท่านั้น

### 3.3 ConfigMap อยู่ใน namespace

{{FIG:T09}}

ConfigMap เป็น **namespaced object** แบบเดียวกับ Pod และ Deployment (บทที่ 4)

```text
configmaps                          cm           v1                                true         ConfigMap
```

คอลัมน์ `true` คือ NAMESPACED และชื่อย่อคือ `cm` (`kubectl get cm`) ผลที่ตามมาคือ

- ชื่อ ConfigMap ซ้ำกันได้ถ้าอยู่คนละ namespace (เช่น `som-web-config` ใน `som-dev` กับ `som-prod` มีค่าต่างกัน — ตรงกับหลัก 12-factor)
- **Pod อ้างได้เฉพาะ ConfigMap ใน namespace เดียวกับตัวเอง** ช่อง `configMapKeyRef`, `configMapRef` และ volume `configMap` มีแค่ `name` ไม่มีช่อง `namespace` (หัวข้อ 11.2)

### 3.4 ConfigMap ไม่ใช่ที่เก็บความลับ

{{FIG:T10}}

ค่าใน ConfigMap ถูกเก็บและแสดงเป็น **ข้อความธรรมดา** ใครมีสิทธิ์ `get`/`list` configmaps ใน namespace นั้นก็อ่านได้หมดด้วย `kubectl get cm -o yaml` หรือ `kubectl describe cm` และค่าที่ส่งเป็น env ก็ยังโผล่ใน `kubectl exec ... -- env` ด้วย จึง **ห้ามใส่รหัสผ่าน token หรือ private key** ใน ConfigMap ตัวอย่างข้างล่างจึงเป็นสิ่งที่ **ไม่ควรทำ**

```yaml
# ❌ ไม่ควรทำ: รหัสผ่านใน ConfigMap ใครอ่าน ConfigMap ได้ก็เห็นรหัส
apiVersion: v1
kind: ConfigMap
metadata:
  name: bad-idea
data:
  DATABASE_URL: postgres://som:meow1234@som-db-0.som-db:5432/catshop
```

---

## 4. วิธีสร้าง ConfigMap

ทุกตัวอย่างในหัวข้อนี้เป็นผลจริงจาก LAB 1 (โฟลเดอร์ `02_LAB/labs/lab01-create/` มีไฟล์ `shop.env`, `announcement.txt`, `default.conf`)

### 4.1 --from-literal: พิมพ์ค่าในคำสั่ง

{{FIG:T11}}

```bash
kubectl create configmap demo --from-literal=SHOP_NAME=ร้านน้องส้ม --from-literal=APP_THEME=sunset
kubectl get cm demo -o yaml
```

```text
configmap/demo created
apiVersion: v1
data:
  APP_THEME: sunset
  SHOP_NAME: ร้านน้องส้ม
kind: ConfigMap
metadata:
  creationTimestamp: "2026-10-05T09:47:38Z"
  name: demo
  namespace: default
  resourceVersion: "956"
  uid: 033a9562-afb9-4b25-b50e-de91af7664d4
```

ใส่ `--from-literal` ซ้ำได้หลายครั้ง (1 ครั้ง = การ์ด 1 ใบ) ค่าภาษาไทยใช้ได้ตามปกติ และ kubectl เรียง key ตามตัวอักษรให้เอง

### 4.2 --from-file: ทั้งไฟล์เป็นค่าของ key เดียว

{{FIG:T12}}

```bash
kubectl create configmap files --from-file=announcement.txt --from-file=nginx.conf=default.conf
kubectl get cm files -o jsonpath='{.data}'; echo
```

```text
configmap/files created
{"announcement.txt":"วันนี้ปลาทูสด\n","nginx.conf":"# ไฟล์ตั้งค่า nginx ตัวอย่าง (LAB 1 ใช้แค่ดูว่า --from-file เก็บทั้งไฟล์เป็นค่าของ key เดียว)\nserver { listen 8080; }\n"}
```

| รูปแบบ | key ที่ได้ |
|---|---|
| `--from-file=announcement.txt` | ชื่อไฟล์ `announcement.txt` |
| `--from-file=nginx.conf=default.conf` | ตั้งชื่อ key เอง (`nginx.conf`) ค่าคือเนื้อไฟล์ `default.conf` |
| `--from-file=.` (หรือชื่อโฟลเดอร์) | ทุกไฟล์ปกติในโฟลเดอร์ ไฟล์ละ 1 key |

สังเกตว่าค่าเก็บ **newline ท้ายไฟล์** (`\n`) ไว้ด้วย ซึ่งสำคัญเมื่อเทียบค่าหรือคำนวณ hash (หัวข้อ 10)

### 4.3 --from-env-file: ไฟล์ KEY=VALUE หลายบรรทัด

{{FIG:T13}}

ไฟล์ `shop.env`

```text
SHOP_NAME=ร้านน้องส้ม
SHOP_THEME=sunset
# บรรทัดที่ขึ้นต้นด้วย # ถูกข้าม (ไม่กลายเป็น key)
EMPTY=
```

```bash
kubectl create configmap envf --from-env-file=shop.env
kubectl get cm envf -o jsonpath='{.data}'; echo
```

```text
configmap/envf created
{"EMPTY":"","SHOP_NAME":"ร้านน้องส้ม","SHOP_THEME":"sunset"}
```

ต่างจาก `--from-file` ตรงที่ **แต่ละบรรทัดกลายเป็น key แยก** บรรทัด comment ถูกข้าม และ `EMPTY=` ได้ค่าว่าง (ไม่ถูกตัดทิ้ง)

### 4.4 YAML และ --dry-run=client -o yaml

{{FIG:T14}}

วิธีที่แนะนำสำหรับงานจริงคือ **เก็บ ConfigMap เป็นไฟล์ YAML ใน git** แล้ว `kubectl apply -f` เหมือน object อื่น ไม่ต้องพิมพ์ YAML เองทั้งหมด ให้ kubectl เขียนให้ด้วย `--dry-run=client -o yaml` (ไม่ส่งไป API server)

```bash
kubectl create configmap dir --from-file=. --dry-run=client -o yaml
kubectl get cm dir
```

```text
apiVersion: v1
data:
  announcement.txt: |
    วันนี้ปลาทูสด
  default.conf: |
    # ไฟล์ตั้งค่า nginx ตัวอย่าง (LAB 1 ใช้แค่ดูว่า --from-file เก็บทั้งไฟล์เป็นค่าของ key เดียว)
    server { listen 8080; }
  shop.env: |
    SHOP_NAME=ร้านน้องส้ม
    SHOP_THEME=sunset
    # บรรทัดที่ขึ้นต้นด้วย # ถูกข้าม (ไม่กลายเป็น key)
    EMPTY=
kind: ConfigMap
metadata:
  name: dir
Error from server (NotFound): configmaps "dir" not found
```

`kubectl get cm dir` ได้ `NotFound` ยืนยันว่า dry-run ไม่ได้สร้างจริง ถ้าต้องการไฟล์ให้ต่อท้าย `> cm.yaml` แล้ว commit/apply

### 4.5 สร้างซ้ำ และการอัปเดตด้วย dry-run + apply

`kubectl create` ใช้สร้างของใหม่เท่านั้น สั่งซ้ำชื่อเดิมจะ error

```text
error: failed to create configmap: configmaps "demo" already exists
```

ถ้าอยากใช้คำสั่ง `create configmap` อัปเดตของเดิม ให้ส่ง YAML จาก dry-run ต่อให้ `kubectl apply -f -`

```bash
kubectl create configmap demo --from-literal=SHOP_NAME=ร้านน้องส้ม --from-literal=APP_THEME=harbor --dry-run=client -o yaml | kubectl apply -f -
```

```text
Warning: resource configmaps/demo is missing the kubectl.kubernetes.io/last-applied-configuration annotation which is required by kubectl apply. kubectl apply should only be used on resources created declaratively by either kubectl create --save-config or kubectl apply. The missing annotation will be patched automatically.
configmap/demo configured
```

Warning นี้ขึ้นครั้งแรกเพราะ `demo` ถูกสร้างด้วย `create` (ไม่มี annotation ของ apply) kubectl เติมให้เองแล้วครั้งต่อไปจะไม่เตือน

| วิธี | เหมาะกับ | ข้อสังเกต |
|---|---|---|
| `--from-literal` | ค่าสั้นไม่กี่ตัว ทดลองเร็ว | ค่าอยู่ใน shell history |
| `--from-file` | ไฟล์ตั้งค่าทั้งไฟล์ (nginx.conf, ข้อความประกาศ) | key = ชื่อไฟล์ เก็บ newline ท้ายไฟล์ |
| `--from-env-file` | ไฟล์ `.env` ที่มีอยู่แล้ว | 1 บรรทัด = 1 key, ข้าม `#` |
| YAML + `apply -f` | งานจริง เก็บใน git ตรวจสอบย้อนหลังได้ | ใช้ `--dry-run=client -o yaml` ช่วยเขียน |

---

## 5. ใช้ ConfigMap เป็นตัวแปร env

### 5.1 env.valueFrom.configMapKeyRef: หยิบทีละ key

{{FIG:T15}}

ไฟล์ `02_LAB/labs/lab02-env/envpod.yaml` (ตัดคอมเมนต์บางส่วน) หยิบการ์ด 2 ใบจากกระดาน `shop-config` มาเป็น env ชื่อที่ตั้งเอง

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: envpod
spec:
  restartPolicy: Never
  terminationGracePeriodSeconds: 1
  containers:
    - name: c
      image: busybox:1.36
      command: ["sh", "-c", "echo SHOP_NAME=$SHOP_NAME; echo APP_THEME=$APP_THEME; echo ARGS: $0 $1; sleep 86400"]
      args: ["$(SHOP_NAME)", "$(NOPE)"]
      env:
        - name: SHOP_NAME                  # ชื่อ env ใน container
          valueFrom:
            configMapKeyRef:
              name: shop-config            # ชื่อ ConfigMap
              key: SHOP_NAME               # key ในกระดาน
        - name: APP_THEME
          valueFrom:
            configMapKeyRef:
              name: shop-config
              key: APP_THEME
```

| ฟิลด์ใน `configMapKeyRef` | ความหมาย |
|---|---|
| `name` | ชื่อ ConfigMap (ใน namespace เดียวกับ Pod) |
| `key` | key ที่ต้องการ (บังคับ) |
| `optional` | `true` = ไม่มี ConfigMap/key ก็เริ่ม container ได้ (env ตัวนั้นไม่ถูกตั้ง) — หัวข้อ 7 |

ผลจริงใน LAB 2

```text
SHOP_NAME=ร้านน้องส้ม
APP_THEME=sunset
ARGS: ร้านน้องส้ม $(NOPE)
```

สิ่งสำคัญที่สุดคือ **ค่าถูกคัดลอกตอน container เริ่ม** หลังจากนั้น env เป็นของ process แล้ว แก้ ConfigMap ภายหลัง env ใน container เดิมจะไม่เปลี่ยน (หัวข้อ 8.1)

### 5.2 envFrom.configMapRef: ถ่ายทั้งกระดาน และ prefix

{{FIG:T16}}

ถ้าต้องการทุก key ใช้ `envFrom` บรรทัดเดียว ไม่ต้องไล่เขียนทีละตัว และใส่ `prefix` นำหน้าชื่อได้ เพื่อกันชื่อชนหรือบอกที่มา ไฟล์ `02_LAB/labs/lab03-envfrom/envfrom-pod.yaml`

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: envfrom
spec:
  restartPolicy: Never
  terminationGracePeriodSeconds: 1
  containers:
    - name: c
      image: busybox:1.36
      command: ["sh", "-c", "env | sort | grep -E '^(CFG_|POD_)'; sleep 86400"]
      envFrom:
        - prefix: CFG_                     # ทุก key ได้ชื่อ CFG_<key>
          configMapRef:
            name: shop-config
      env:
        - name: POD_NAMESPACE              # Downward API (บท 003)
          valueFrom:
            fieldRef:
              fieldPath: metadata.namespace
        - name: CFG_APP_THEME              # ชื่อซ้ำกับที่มาจาก envFrom → env ชนะ
          value: "harbor (จาก env)"
```

ผลจริงใน LAB 3 (ConfigMap `shop-config` มี 7 key)

```text
CFG_1bad=starts-with-digit
CFG_APP_THEME=harbor (จาก env)
CFG_FOOTER=ร้านใน namespace $(POD_NAMESPACE)
CFG_SHOP_NAME=ร้านน้องส้ม
CFG_announcement.txt=วันนี้ปลาทูสด
CFG_menu.txt=ขนมปลาทูน่า
CFG_shop.name=dot-key
POD_NAMESPACE=default
```

แอปร้านน้องส้มใน LAB 10 ใช้ `envFrom` (ไม่มี prefix) กับ ConfigMap `som-web-config` จึงได้ `SHOP_NAME`, `SHOP_EYEBROW`, `SHOP_FOOTER`, `APP_THEME`, `SHOP_PROMO` ครบในบรรทัดเดียว

### 5.3 $(VAR) ใน command และ args

{{FIG:T17}}

Kubernetes แทนค่า `$(ชื่อ env)` ใน `command`, `args` และใน `value` ของ env ตัวถัดไปให้เอง **ก่อน** เริ่ม container (ไม่ใช่ shell เป็นคนแทน) โดยดูจาก env ที่ประกาศไว้ใน container นั้น

- `args: ["$(SHOP_NAME)", "$(NOPE)"]` → `ร้านน้องส้ม` และ `$(NOPE)` เพราะไม่มี env ชื่อ `NOPE` Kubernetes **คงข้อความเดิมไว้** ไม่แทนเป็นค่าว่าง และไม่ error
- ใน spec ที่เก็บใน API server ยังเป็นข้อความเดิม (`kubectl get pod envpod -o jsonpath="{.spec.containers[0].args}"` ได้ `["$(SHOP_NAME)","$(NOPE)"]`) การแทนค่าเกิดตอน kubelet สร้าง container
- อยากได้ข้อความ `$(X)` จริง ๆ ให้เขียน `$$(X)`
- `$SHOP_NAME` (ไม่มีวงเล็บ) ใน `command` ข้างบนเป็นของ **shell** (`sh -c`) ไม่ใช่ของ Kubernetes

### 5.4 ชื่อซ้ำ: env ชนะ envFrom และ $(VAR) ในค่าจาก envFrom

{{FIG:T18}}

กฎลำดับความสำคัญที่ทดสอบแล้วใน LAB 3 และ LAB 10

1. **ชื่อซ้ำกัน `env` ชนะ `envFrom` เสมอ** (`CFG_APP_THEME=harbor (จาก env)` ทั้งที่ ConfigMap ตั้ง `APP_THEME: sunset`) ถ้ามีหลาย `envFrom` ที่มี key ซ้ำกัน ตัวที่อยู่ท้ายรายการชนะ
2. **`$(VAR)` ในค่าที่มาจาก ConfigMap ผ่าน `envFrom` ไม่ถูกแทนค่า** ConfigMap มี `FOOTER: "ร้านใน namespace $(POD_NAMESPACE)"` ผลใน container ยังเป็น `CFG_FOOTER=ร้านใน namespace $(POD_NAMESPACE)` ทั้งที่มี env `POD_NAMESPACE=default`

ข้อ 2 เกิดขึ้นจริงในร้านน้องส้ม LAB 10: เมื่อย้าย `SHOP_FOOTER` ที่เคยมี `$(POD_NAMESPACE)` จาก env เข้าไปใน ConfigMap หน้าเว็บแสดง `"footer":"LAB 010 · namespace $(POD_NAMESPACE)"` เป็นข้อความดิบ ทางแก้คือเก็บค่าที่ต้องอ้างตัวแปรไว้ใน `env` ของ Deployment (ซึ่งแทนค่าได้และชนะ `envFrom`) ผลจริงหลัง `kubectl set env` คือ `"footer":"LAB 010 · namespace som-shop"`

### 5.5 ชื่อ key ที่กลายเป็นชื่อ env

{{FIG:T19}}

key ใน ConfigMap ใช้ `.` และขึ้นต้นด้วยตัวเลขได้ แต่ชื่อแบบนั้นไม่ใช่ชื่อตัวแปรที่ shell รู้จัก Kubernetes รุ่นเก่าจะข้าม key ที่ไม่ใช่ชื่อ env ที่ถูกต้องและแจ้ง event `InvalidVariableNames` แต่ **Kubernetes v1.37 ที่ใช้ในวิชานี้รับทุก key เป็นชื่อ env** (ทดสอบแล้ว: `1bad`, `shop.name`, `announcement.txt` ไม่ถูกข้ามและไม่มี event เตือน ทั้งแบบมีและไม่มี prefix)

ปัญหาอยู่ที่โปรแกรมปลายทาง ผลจริงใน LAB 3

```text
$ kubectl exec envfrom -- sh -c 'echo $CFG_shop.name'
.name
```

shell อ่านชื่อตัวแปรได้แค่ `$CFG_shop` (ไม่มีค่า) แล้วต่อด้วยข้อความ `.name` ส่วน `$CFG_1bad` อ่านได้เพราะชื่อเต็มขึ้นต้นด้วย `C` (ถ้าไม่มี prefix `$1bad` จะกลายเป็น `$1` + `bad`) **แนวปฏิบัติ: key ที่จะใช้เป็น env ให้ตั้งเป็น `UPPER_SNAKE_CASE`** (`SHOP_NAME`, `APP_THEME`) ส่วน key ที่มีจุดอย่าง `announcement.txt` เก็บไว้ใช้เป็น "ชื่อไฟล์" ใน volume

---

## 6. ใช้ ConfigMap เป็นไฟล์ (volume)

### 6.1 volumes.configMap: ทุก key เป็นไฟล์

{{FIG:T20}}

อีกทางหนึ่งคือ mount ConfigMap เป็นโฟลเดอร์ แต่ละ key กลายเป็นไฟล์ชื่อเดียวกับ key เนื้อไฟล์คือค่า ไฟล์ `02_LAB/labs/lab05-volume/volpod.yaml` mount `shop-config` 3 แบบในคราวเดียว

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: volpod
spec:
  terminationGracePeriodSeconds: 1
  containers:
    - name: c
      image: busybox:1.36
      command: ["sleep", "86400"]
      volumeMounts:
        - name: all
          mountPath: /etc/all
        - name: some
          mountPath: /etc/some
        - name: all
          mountPath: /etc/som/announcement.txt
          subPath: announcement.txt        # หยิบไฟล์เดียวจาก volume all
  volumes:
    - name: all
      configMap:
        name: shop-config
    - name: some
      configMap:
        name: shop-config
        defaultMode: 0400                  # เลขฐานแปด (นำด้วย 0) → -r--------
        items:
          - key: menu.txt
            path: menu/today.txt           # ตั้งชื่อ/โฟลเดอร์ย่อยเองได้
```

ผลจริงของ `kubectl exec volpod -- ls -la /etc/all`

```text
total 12
drwxrwxrwx    3 root     root          4096 Oct  5 09:53 .
drwxr-xr-x    1 root     root          4096 Oct  5 09:53 ..
drwxr-xr-x    2 root     root          4096 Oct  5 09:53 ..2026_10_05_09_53_05.3156628874
lrwxrwxrwx    1 root     root            32 Oct  5 09:53 ..data -> ..2026_10_05_09_53_05.3156628874
lrwxrwxrwx    1 root     root            11 Oct  5 09:53 1bad -> ..data/1bad
lrwxrwxrwx    1 root     root            16 Oct  5 09:53 APP_THEME -> ..data/APP_THEME
lrwxrwxrwx    1 root     root            13 Oct  5 09:53 FOOTER -> ..data/FOOTER
lrwxrwxrwx    1 root     root            16 Oct  5 09:53 SHOP_NAME -> ..data/SHOP_NAME
lrwxrwxrwx    1 root     root            23 Oct  5 09:53 announcement.txt -> ..data/announcement.txt
lrwxrwxrwx    1 root     root            15 Oct  5 09:53 menu.txt -> ..data/menu.txt
lrwxrwxrwx    1 root     root            16 Oct  5 09:53 shop.name -> ..data/shop.name
```

ข้อสังเกต

- **ไฟล์ที่เห็นเป็น symlink** ชี้ไปที่ `..data/<key>` และ `..data` ชี้ไปโฟลเดอร์ที่มีชื่อเป็นเวลา (หัวข้อ 8.3 อธิบายว่าทำไม)
- **ระบบไฟล์เป็น read-only** เขียนไม่ได้ `sh: can't create /etc/all/menu.txt: Read-only file system` และ `mount` แสดง `/dev/sdd on /etc/all type ext4 (ro,relatime)` (บน kind เป็นดิสก์ของ Node แบบ `ro`)
- **mount ทับทั้งโฟลเดอร์** ไฟล์เดิมที่ image มีอยู่ใน `mountPath` จะถูกบังทั้งหมด เช่น LAB 7 mount ที่ `/etc/nginx/conf.d` ไฟล์ `default.conf` เดิมของ image nginx จะมองไม่เห็น เหลือแต่ของจาก ConfigMap
- `binaryData` ก็ mount เป็นไฟล์ได้ตามปกติ (ต่างจาก env)

### 6.2 items: เลือกบาง key และตั้ง path เอง

{{FIG:T21}}

`items` ทำ 2 อย่าง คือ **เลือกเฉพาะ key ที่ระบุ** (key อื่นไม่ถูก mount) และ **ตั้งชื่อไฟล์/โฟลเดอร์ย่อยใหม่** ผลจริงของ `/etc/some` ที่มีแค่ `menu.txt` ไปอยู่ที่ `menu/today.txt`

```text
/etc/some:
total 12
drwxrwxrwx    3 root     root          4096 Oct  5 09:53 .
drwxr-xr-x    1 root     root          4096 Oct  5 09:53 ..
drwxr-xr-x    3 root     root          4096 Oct  5 09:53 ..2026_10_05_09_53_05.3837634004
lrwxrwxrwx    1 root     root            32 Oct  5 09:53 ..data -> ..2026_10_05_09_53_05.3837634004
lrwxrwxrwx    1 root     root            11 Oct  5 09:53 menu -> ..data/menu
...
/etc/some/..2026_10_05_09_53_05.3837634004/menu:
...
-r--------    1 root     root            34 Oct  5 09:53 today.txt
```

ถ้าใน `items` อ้าง key ที่ไม่มีใน ConfigMap (และไม่ได้ตั้ง `optional: true`) Pod จะ mount ไม่สำเร็จ

### 6.3 defaultMode และ mode: สิทธิ์ของไฟล์

{{FIG:T22}}

ค่าเริ่มต้นของไฟล์จาก ConfigMap คือ `0644` (`-rw-r--r--`) เปลี่ยนได้ทั้ง volume ด้วย `defaultMode` หรือรายไฟล์ด้วย `items[].mode` ใน YAML ให้เขียนเป็น **เลขฐานแปดนำหน้าด้วย 0** (`0400`) ถ้าเขียนใน JSON ต้องใช้เลขฐานสิบ (`256`) เพราะ JSON ไม่มีเลขฐานแปด ผลจริง `0400` → `-r--------` (อ่านได้เฉพาะเจ้าของ) เหมาะกับไฟล์ที่ไม่อยากให้ user อื่นใน container อ่าน (แต่จำไว้ว่าคนที่อ่าน ConfigMap ใน API ได้ก็ยังเห็นค่าอยู่ดี)

### 6.4 subPath: ไฟล์เดียวไม่ทับโฟลเดอร์ แต่ไม่อัปเดต

{{FIG:T23}}

บางครั้งเราอยากวางไฟล์ตั้งค่าไฟล์เดียวลงในโฟลเดอร์ที่มีไฟล์อื่นของ image อยู่แล้ว (เช่น `/etc/som/` ที่มีไฟล์อื่น) ถ้า mount ทั้ง volume จะบังของเดิมหมด `subPath` แก้ปัญหานี้โดย mount **เฉพาะไฟล์เดียว** ผลจริงของ `/etc/som` ใน `volpod`

```text
total 12
drwxr-xr-x    2 root     root          4096 Oct  5 09:53 .
drwxr-xr-x    1 root     root          4096 Oct  5 09:53 ..
-rw-r--r--    1 root     root            40 Oct  5 09:53 announcement.txt
```

ไฟล์ `announcement.txt` เป็น **ไฟล์จริง ไม่ใช่ symlink** (bind mount ไฟล์เดียว) ข้อเสียสำคัญคือ **ไฟล์ subPath จะไม่อัปเดตเมื่อแก้ ConfigMap** (LAB 6 แก้ 3 รอบ ไฟล์ subPath ยังเป็น `วันนี้ปลาทูสด` ตลอด) ต้องสร้าง Pod ใหม่เท่านั้น ร้านน้องส้มใน LAB 10 จึงเลือก **mount ทั้งโฟลเดอร์ `/etc/som` ไม่ใช้ subPath** เพื่อให้ประกาศอัปเดตเองได้

| แบบ | ไฟล์ที่เห็น | ทับโฟลเดอร์เดิม | อัปเดตเองเมื่อแก้ ConfigMap |
|---|---|---|---|
| volume ทั้ง ConfigMap | ทุก key (symlink) | ทับทั้งโฟลเดอร์ | ✅ ราว 1 นาที |
| volume + `items` | เฉพาะ key ที่เลือก ตาม path ใหม่ | ทับทั้งโฟลเดอร์ | ✅ ราว 1 นาที |
| `subPath` | ไฟล์เดียว (ไฟล์จริง) | ไม่ทับ | ❌ ไม่อัปเดตเลย |

---

## 7. ConfigMap หรือ key ที่ไม่มี และ optional

### 7.1 อ้างของที่ไม่มี: Pod ไม่เริ่ม

{{FIG:T24}}

ConfigMap แยกจาก Pod จึงเกิดกรณี "Pod อ้างกระดานที่ยังไม่มี" ได้ง่าย เช่น apply Deployment ก่อน ConfigMap หรือพิมพ์ชื่อผิด ผลจริงใน LAB 4 หลัง apply 25 วินาที

```text
NAME     READY   STATUS                       RESTARTS   AGE
nocm     0/1     CreateContainerConfigError   0          26s
nokey    0/1     CreateContainerConfigError   0          26s
optpod   1/1     Running                      0          26s
novol    0/1     ContainerCreating            0          26s
```

| กรณี | ไฟล์ LAB 4 | อาการ | ข้อความจริงใน `kubectl describe pod` |
|---|---|---|---|
| `envFrom` อ้าง ConfigMap ที่ไม่มี | `nocm.yaml` | `CreateContainerConfigError` | `Error: configmap "not-here" not found` |
| `configMapKeyRef` อ้าง key ที่ไม่มี | `nokey.yaml` | `CreateContainerConfigError` | `Error: couldn't find key NOPE in ConfigMap default/shop-config` |
| volume อ้าง ConfigMap ที่ไม่มี | `novol.yaml` | ค้าง `ContainerCreating` | `Warning  FailedMount ... MountVolume.SetUp failed for volume "v" : configmap "not-here" not found` |

ความต่างของสถานะมาจากจังหวะที่ล้ม: volume ต้อง mount ก่อนสร้าง container จึงค้างที่ `ContainerCreating` ส่วน env ถูกเตรียมตอนสร้าง container จึงเป็น `CreateContainerConfigError` ทั้งสองกรณี **kubelet ลองใหม่เรื่อย ๆ** (เห็น `x4 over 25s`, `x6 over 25s` ใน event) Pod ไม่ถูกลบและไม่นับ RESTARTS

### 7.2 optional: true และการสร้าง ConfigMap ภายหลัง

{{FIG:T25}}

ใส่ `optional: true` ได้ทั้ง 3 จุด (`configMapKeyRef`, `configMapRef`, volume `configMap`) ไฟล์ `02_LAB/labs/lab04-missing/optpod.yaml`

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: optpod
spec:
  terminationGracePeriodSeconds: 1
  containers:
    - name: c
      image: busybox:1.36
      command: ["sh", "-c", "echo X=[$X] HELLO=[$HELLO]; ls -la /etc/opt-cm; sleep 86400"]
      env:
        - name: X
          valueFrom:
            configMapKeyRef:
              name: shop-config
              key: NOPE
              optional: true
      envFrom:
        - configMapRef:
            name: not-here
            optional: true
      volumeMounts:
        - name: v
          mountPath: /etc/opt-cm
  volumes:
    - name: v
      configMap:
        name: not-here
        optional: true
```

ผลจริง: Pod `Running` env ที่ไม่มีไม่ถูกตั้ง (`X=[] HELLO=[]`) และโฟลเดอร์ `/etc/opt-cm` มีแค่ `..data` กับโฟลเดอร์เวลา (ไม่มีไฟล์ของ key ใด)

เมื่อ **สร้าง ConfigMap ภายหลัง** (`kubectl create configmap not-here --from-literal=HELLO=world`) ผลจริงที่วัดได้

- `nocm` และ `novol` ที่ค้างอยู่ **เริ่มเองเป็น `Running` ภายในราว 15 วินาที** ไม่ต้องลบ Pod (kubelet ลองใหม่จนสำเร็จ)
- `nokey` **ยังค้าง** `CreateContainerConfigError` เพราะสาเหตุของมันคือ key `NOPE` ใน `shop-config` ไม่ใช่ ConfigMap `not-here` ต้องแก้ YAML หรือเพิ่ม key แล้วรอ/สร้าง Pod ใหม่
- `optpod` ที่ใช้ optional volume จะเห็นไฟล์ `HELLO` โผล่ใน `/etc/opt-cm` ภายหลัง (วัด 3 รอบได้ 43–64 วินาที) แต่ **env `HELLO` ยังว่างตลอด** เพราะ env อ่านครั้งเดียวตอนเริ่ม

> ใช้ `optional: true` เฉพาะค่าที่แอป "มีค่าเริ่มต้นของตัวเอง" จริง ๆ เช่น ไฟล์ประกาศที่ไม่มีก็ได้ ถ้าเป็นค่าจำเป็น ให้ปล่อยให้ Pod ค้างจะดีกว่า เพราะเห็นปัญหาทันที ดีกว่าแอปรันด้วยค่าว่างแบบเงียบ ๆ
