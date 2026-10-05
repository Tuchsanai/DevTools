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

| รูปที่ | เรื่อง | รูปที่ | เรื่อง |
|:---:|---|:---:|---|
| 1 | [เปิดบท กระดานประกาศกลาง](#fig-1) | 21 | [items เลือกบาง key](#fig-21) |
| 2 | [ทวนบท 009 ค่าเขียนตรงใน YAML](#fig-2) | 22 | [defaultMode สิทธิ์ไฟล์](#fig-22) |
| 3 | [อุปมาใหม่ของบทนี้](#fig-3) | 23 | [subPath ไฟล์เดียว](#fig-23) |
| 4 | [ค่าฝังใน image ต้อง build ใหม่](#fig-4) | 24 | [อ้าง ConfigMap/key ที่ไม่มี](#fig-24) |
| 5 | [หลัก 12-factor แยก config](#fig-5) | 25 | [optional: true](#fig-25) |
| 6 | [อะไรคือ config](#fig-6) | 26 | [env ไม่อัปเดตเอง](#fig-26) |
| 7 | [กายวิภาค ConfigMap](#fig-7) | 27 | [volume อัปเดตเอง](#fig-27) |
| 8 | [ขนาดไม่เกิน 1 MiB](#fig-8) | 28 | [..data symlink สลับทีเดียว](#fig-28) |
| 9 | [ConfigMap อยู่ใน namespace](#fig-9) | 29 | [แอปต้อง reload เอง](#fig-29) |
| 10 | [ไม่ใช่ที่เก็บความลับ](#fig-10) | 30 | [rollout restart และ checksum](#fig-30) |
| 11 | [สร้างด้วย --from-literal](#fig-11) | 31 | [immutable](#fig-31) |
| 12 | [สร้างด้วย --from-file](#fig-12) | 32 | [kustomize configMapGenerator](#fig-32) |
| 13 | [สร้างด้วย --from-env-file](#fig-13) | 33 | [ConfigMap ของระบบ](#fig-33) |
| 14 | [ให้ kubectl เขียน YAML](#fig-14) | 34 | [อ้างข้าม namespace ไม่ได้](#fig-34) |
| 15 | [env ทีละ key (configMapKeyRef)](#fig-15) | 35 | [RBAC ของ ConfigMap](#fig-35) |
| 16 | [envFrom และ prefix](#fig-16) | 36 | [เลือก env หรือ volume](#fig-36) |
| 17 | [$(VAR) ใน command/args](#fig-17) | 37 | [แนวปฏิบัติ](#fig-37) |
| 18 | [env ชนะ envFrom](#fig-18) | 38 | [แผนที่สรุปบท](#fig-38) |
| 19 | [ชื่อ key ที่กลายเป็น env](#fig-19) | 39 | [cheatsheet คำสั่ง](#fig-39) |
| 20 | [volume ทั้ง ConfigMap](#fig-20) | 40 | [ปัญหาที่เหลือ → บท 011](#fig-40) |

---

## 1. บทนำ: เปลี่ยนป้ายร้านต้อง build ใหม่ทุกครั้ง

<p align="center" id="fig-1">
  <img src="images/01-opening-notice-board.png" alt="รูปที่ 1 เปิดบท กระดานประกาศกลาง" width="900"><br>
  <em><b>รูปที่ 1</b> เปิดบทที่ 10: ต่อจากบท 009 — ร้านมี db เป็น StatefulSet แล้ว แต่จะเปลี่ยนชื่อร้าน/โปรโมชันทีไรต้องแก้ YAML หรือ build image ใหม่ น้องส้มจึงติดกระดานประกาศกลางให้ทุกบูธอ่าน</em>
</p>

ร้านอาหารแมวน้องส้มเดินทางมาไกลแล้ว: บทที่ 5–7 มีหน้าร้าน (web) 3 บูธที่ผู้จัดการร้าน (Deployment) ดูแลและเปลี่ยนรุ่นได้โดยไม่สะดุด บทที่ 6 มีประภาคาร (Service NodePort 30080) บทที่ 8–9 ครัวกลาง (db) มีตู้เซฟประจำตัวและชื่อคงที่ `som-db-0` ออเดอร์ไม่หายแม้ Pod ถูกสร้างใหม่

แต่วันหนึ่งน้องส้มอยากทำสิ่งที่ดูง่ายมาก คือ **เปลี่ยนชื่อร้านเป็น "ร้านน้องส้ม สาขาท่าเรือ" เปลี่ยนธีมเป็นสีส้ม และขึ้นป้ายโปรโมชัน** แล้วก็พบว่าต้องเปิดไฟล์ YAML ของ Deployment แก้ค่าในหลายจุด หรือแย่กว่านั้นคือ build image ใหม่ เพราะธีมและข้อความบางส่วนถูก "ฝัง" ไว้ใน image ตอน build

<p align="center" id="fig-2">
  <img src="images/02-recap-hardcoded-env.png" alt="รูปที่ 2 ทวนบท 009 ค่าเขียนตรงใน YAML" width="900"><br>
  <em><b>รูปที่ 2</b> ทวนบท 009: ค่า SHOP_NAME, SHOP_FOOTER และ DATABASE_URL (มีรหัส meow1234) เขียนตรงใน 20-web.yaml และธีม/เวอร์ชันฝังใน image ตอน build</em>
</p>

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

<p align="center" id="fig-3">
  <img src="images/03-metaphor-legend.png" alt="รูปที่ 3 อุปมาใหม่ของบทนี้" width="900"><br>
  <em><b>รูปที่ 3</b> อุปมาใหม่: ConfigMap = กระดานประกาศของโซน, env/envFrom = ป้ายโน้ตติดอกพนักงานตอนเข้ากะ, volume = กระดานเล็กในบูธที่หุ่นยนต์ kubelet มาอัปเดตให้</em>
</p>

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

<p align="center" id="fig-4">
  <img src="images/04-baked-into-image.png" alt="รูปที่ 4 ค่าฝังใน image ต้อง build ใหม่" width="900"><br>
  <em><b>รูปที่ 4</b> ถ้าชื่อร้านหรือธีมฝังใน image (build-arg APP_THEME) เปลี่ยนป้ายครั้งเดียวต้อง build → kind load → rollout ใหม่ทั้งหมด</em>
</p>

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

<p align="center" id="fig-5">
  <img src="images/05-twelve-factor-config.png" alt="รูปที่ 5 หลัก 12-factor แยก config" width="900"><br>
  <em><b>รูปที่ 5</b> หลัก 12-factor: แยก config ออกจากโค้ด — image เดียวกันใช้ได้ทุกสภาพแวดล้อม ค่าที่ต่างกันส่งเข้าไปตอนรัน</em>
</p>

แนวคิด [The Twelve-Factor App](https://12factor.net/config) ข้อที่ 3 (Config) บอกว่า **config คือทุกอย่างที่ต่างกันระหว่างการ deploy** (dev, staging, prod) และควรเก็บแยกจากโค้ด แอปควรอ่าน config จากสภาพแวดล้อมตอนรัน (เช่น environment variable หรือไฟล์) ผลคือ

- **build ครั้งเดียว ใช้ได้ทุกที่** image เดียวกันผ่านการทดสอบแล้วขึ้น prod ได้ทันที เปลี่ยนแค่ค่าที่ส่งเข้าไป
- **เปลี่ยนค่าโดยไม่แตะโค้ด** คนดูแลระบบปรับค่าได้โดยไม่ต้อง build
- **ทดสอบง่ายว่าแอปทนค่าผิด** เพราะค่าถูกส่งเข้ามาจากข้างนอกชัดเจน

Kubernetes มี object สำหรับเรื่องนี้โดยตรงสองตัว คือ **ConfigMap** (ค่าทั่วไป บทนี้) และ **Secret** (ค่าลับ บทที่ 11)

### 2.3 อะไรคือ config และอะไรไม่ใช่

<p align="center" id="fig-6">
  <img src="images/06-what-is-config.png" alt="รูปที่ 6 อะไรคือ config" width="900"><br>
  <em><b>รูปที่ 6</b> อะไรคือ config: ชื่อร้าน ธีม ข้อความประกาศ ไฟล์ตั้งค่า nginx — ไม่ใช่ข้อมูลออเดอร์ (อยู่ใน PVC) และไม่ใช่รหัสผ่าน (บทหน้า)</em>
</p>

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

<p align="center" id="fig-7">
  <img src="images/07-configmap-anatomy.png" alt="รูปที่ 7 กายวิภาค ConfigMap" width="900"><br>
  <em><b>รูปที่ 7</b> ConfigMap = object แบบ key-value: data (ข้อความ UTF-8) และ binaryData (ไฟล์ไบนารีเก็บแบบ base64) ไม่มี spec ไม่มี Pod — เป็นแค่ข้อมูลให้ Pod อ้างถึง</em>
</p>

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

<p align="center" id="fig-8">
  <img src="images/08-size-limit.png" alt="รูปที่ 8 ขนาดไม่เกิน 1 MiB" width="900"><br>
  <em><b>รูปที่ 8</b> ConfigMap หนึ่งตัวใหญ่ได้ไม่เกิน 1 MiB (ทดสอบ: ไฟล์ 1.1 MB → Too long: may not be more than 1048576 bytes) — ไฟล์ใหญ่ควรอยู่ใน image หรือ volume อื่น</em>
</p>

ConfigMap ทั้งก้อน (รวมทุก key) ใหญ่ได้ไม่เกิน **1 MiB = 1,048,576 bytes** เพราะทุก object ถูกเก็บใน etcd และถูกส่งให้ kubelet ทุก Node ที่มี Pod ใช้ ทดสอบจริงใน LAB 1

```text
-rw-r--r-- 1 root root 1100000 Oct  5 16:47 big.txt
error: failed to create configmap: ConfigMap "big" is invalid: []: Too long: may not be more than 1048576 bytes
```

ไฟล์ขนาด 1,048,000 bytes ยังสร้างได้ (`configmap/big2 created`) ถ้าต้องใช้ไฟล์ใหญ่กว่านี้ ให้ใส่ไว้ใน image หรือ volume ชนิดอื่น ConfigMap เหมาะกับ "ค่าตั้งค่า" ขนาดเล็กเท่านั้น

### 3.3 ConfigMap อยู่ใน namespace

<p align="center" id="fig-9">
  <img src="images/09-namespaced.png" alt="รูปที่ 9 ConfigMap อยู่ใน namespace" width="900"><br>
  <em><b>รูปที่ 9</b> ConfigMap อยู่ใน namespace (namespaced: true) — Pod ใช้ได้เฉพาะ ConfigMap ใน namespace เดียวกัน ไม่มีช่องให้ระบุ namespace อื่น</em>
</p>

ConfigMap เป็น **namespaced object** แบบเดียวกับ Pod และ Deployment (บทที่ 4)

```text
configmaps                          cm           v1                                true         ConfigMap
```

คอลัมน์ `true` คือ NAMESPACED และชื่อย่อคือ `cm` (`kubectl get cm`) ผลที่ตามมาคือ

- ชื่อ ConfigMap ซ้ำกันได้ถ้าอยู่คนละ namespace (เช่น `som-web-config` ใน `som-dev` กับ `som-prod` มีค่าต่างกัน — ตรงกับหลัก 12-factor)
- **Pod อ้างได้เฉพาะ ConfigMap ใน namespace เดียวกับตัวเอง** ช่อง `configMapKeyRef`, `configMapRef` และ volume `configMap` มีแค่ `name` ไม่มีช่อง `namespace` (หัวข้อ 11.2)

### 3.4 ConfigMap ไม่ใช่ที่เก็บความลับ

<p align="center" id="fig-10">
  <img src="images/10-not-for-secrets.png" alt="รูปที่ 10 ไม่ใช่ที่เก็บความลับ" width="900"><br>
  <em><b>รูปที่ 10</b> ConfigMap เก็บแบบข้อความธรรมดา ใครมีสิทธิ์ get configmaps ก็อ่านได้ — ห้ามใส่รหัสผ่าน/token</em>
</p>

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

<p align="center" id="fig-11">
  <img src="images/11-from-literal.png" alt="รูปที่ 11 สร้างด้วย --from-literal" width="900"><br>
  <em><b>รูปที่ 11</b> kubectl create configmap demo --from-literal=SHOP_NAME=ร้านน้องส้ม --from-literal=APP_THEME=sunset → การ์ด 2 ใบ (ค่าภาษาไทยใช้ได้)</em>
</p>

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

<p align="center" id="fig-12">
  <img src="images/12-from-file.png" alt="รูปที่ 12 สร้างด้วย --from-file" width="900"><br>
  <em><b>รูปที่ 12</b> --from-file=announcement.txt → key = ชื่อไฟล์; --from-file=nginx.conf=default.conf → ตั้งชื่อ key เองได้; --from-file=. → ทุกไฟล์ในโฟลเดอร์</em>
</p>

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

<p align="center" id="fig-13">
  <img src="images/13-from-env-file.png" alt="รูปที่ 13 สร้างด้วย --from-env-file" width="900"><br>
  <em><b>รูปที่ 13</b> --from-env-file=shop.env อ่านบรรทัด KEY=VALUE เป็นหลาย key; บรรทัด # ถูกข้าม, EMPTY= ได้ค่าว่าง (ทดสอบแล้ว)</em>
</p>

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

<p align="center" id="fig-14">
  <img src="images/14-dry-run-yaml.png" alt="รูปที่ 14 ให้ kubectl เขียน YAML" width="900"><br>
  <em><b>รูปที่ 14</b> ให้ kubectl เขียน YAML ให้: kubectl create configmap ... --dry-run=client -o yaml > cm.yaml แล้ว commit/apply เป็นไฟล์</em>
</p>

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

<p align="center" id="fig-15">
  <img src="images/15-config-map-key-ref.png" alt="รูปที่ 15 env ทีละ key (configMapKeyRef)" width="900"><br>
  <em><b>รูปที่ 15</b> env.valueFrom.configMapKeyRef: เลือกทีละ key มาตั้งชื่อตัวแปรเอง (name + key) — ค่าถูกคัดลอกตอน container เริ่ม</em>
</p>

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

<p align="center" id="fig-16">
  <img src="images/16-env-from-prefix.png" alt="รูปที่ 16 envFrom และ prefix" width="900"><br>
  <em><b>รูปที่ 16</b> envFrom.configMapRef: ดึงทุก key เป็น env ในครั้งเดียว ใส่ prefix: CFG_ ได้ → CFG_SHOP_NAME, CFG_APP_THEME</em>
</p>

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

<p align="center" id="fig-17">
  <img src="images/17-args-var-expansion.png" alt="รูปที่ 17 $(VAR) ใน command/args" width="900"><br>
  <em><b>รูปที่ 17</b> command/args อ้าง env ด้วย $(SHOP_NAME) ได้ (Kubernetes แทนค่าให้) — ถ้าไม่มีตัวแปรนั้น $(NOPE) ค้างเป็นข้อความเดิม</em>
</p>

Kubernetes แทนค่า `$(ชื่อ env)` ใน `command`, `args` และใน `value` ของ env ตัวถัดไปให้เอง **ก่อน** เริ่ม container (ไม่ใช่ shell เป็นคนแทน) โดยดูจาก env ที่ประกาศไว้ใน container นั้น

- `args: ["$(SHOP_NAME)", "$(NOPE)"]` → `ร้านน้องส้ม` และ `$(NOPE)` เพราะไม่มี env ชื่อ `NOPE` Kubernetes **คงข้อความเดิมไว้** ไม่แทนเป็นค่าว่าง และไม่ error
- ใน spec ที่เก็บใน API server ยังเป็นข้อความเดิม (`kubectl get pod envpod -o jsonpath="{.spec.containers[0].args}"` ได้ `["$(SHOP_NAME)","$(NOPE)"]`) การแทนค่าเกิดตอน kubelet สร้าง container
- อยากได้ข้อความ `$(X)` จริง ๆ ให้เขียน `$$(X)`
- `$SHOP_NAME` (ไม่มีวงเล็บ) ใน `command` ข้างบนเป็นของ **shell** (`sh -c`) ไม่ใช่ของ Kubernetes

### 5.4 ชื่อซ้ำ: env ชนะ envFrom และ $(VAR) ในค่าจาก envFrom

<p align="center" id="fig-18">
  <img src="images/18-env-precedence.png" alt="รูปที่ 18 env ชนะ envFrom" width="900"><br>
  <em><b>รูปที่ 18</b> ถ้าชื่อซ้ำกัน env ชนะ envFrom; และ $(POD_NAMESPACE) ในค่าที่มาจาก envFrom ไม่ถูกแทนค่า (ทดสอบ: footer ยังเป็น $(POD_NAMESPACE)) — ใส่ไว้ใน env แทน</em>
</p>

กฎลำดับความสำคัญที่ทดสอบแล้วใน LAB 3 และ LAB 10

1. **ชื่อซ้ำกัน `env` ชนะ `envFrom` เสมอ** (`CFG_APP_THEME=harbor (จาก env)` ทั้งที่ ConfigMap ตั้ง `APP_THEME: sunset`) ถ้ามีหลาย `envFrom` ที่มี key ซ้ำกัน ตัวที่อยู่ท้ายรายการชนะ
2. **`$(VAR)` ในค่าที่มาจาก ConfigMap ผ่าน `envFrom` ไม่ถูกแทนค่า** ConfigMap มี `FOOTER: "ร้านใน namespace $(POD_NAMESPACE)"` ผลใน container ยังเป็น `CFG_FOOTER=ร้านใน namespace $(POD_NAMESPACE)` ทั้งที่มี env `POD_NAMESPACE=default`

ข้อ 2 เกิดขึ้นจริงในร้านน้องส้ม LAB 10: เมื่อย้าย `SHOP_FOOTER` ที่เคยมี `$(POD_NAMESPACE)` จาก env เข้าไปใน ConfigMap หน้าเว็บแสดง `"footer":"LAB 010 · namespace $(POD_NAMESPACE)"` เป็นข้อความดิบ ทางแก้คือเก็บค่าที่ต้องอ้างตัวแปรไว้ใน `env` ของ Deployment (ซึ่งแทนค่าได้และชนะ `envFrom`) ผลจริงหลัง `kubectl set env` คือ `"footer":"LAB 010 · namespace som-shop"`

### 5.5 ชื่อ key ที่กลายเป็นชื่อ env

<p align="center" id="fig-19">
  <img src="images/19-key-names-env.png" alt="รูปที่ 19 ชื่อ key ที่กลายเป็น env" width="900"><br>
  <em><b>รูปที่ 19</b> Kubernetes v1.37 ยอมให้ key แปลก ๆ เช่น 1bad หรือ shop.name เป็นชื่อ env ได้ (ทดสอบแล้ว ไม่ถูกข้าม) แต่โปรแกรมหลายตัวอ่านไม่ได้ — ตั้งชื่อแบบ UPPER_SNAKE_CASE</em>
</p>

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

<p align="center" id="fig-20">
  <img src="images/20-volume-whole.png" alt="รูปที่ 20 volume ทั้ง ConfigMap" width="900"><br>
  <em><b>รูปที่ 20</b> volumes.configMap: ทุก key กลายเป็นไฟล์ชื่อเดียวกับ key ในโฟลเดอร์ที่ mount เช่น /etc/som/announcement.txt — ระบบไฟล์เป็น read-only</em>
</p>

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

<p align="center" id="fig-21">
  <img src="images/21-volume-items.png" alt="รูปที่ 21 items เลือกบาง key" width="900"><br>
  <em><b>รูปที่ 21</b> items เลือกเฉพาะบาง key และตั้ง path ใหม่ได้ เช่น key menu.txt → menu/today.txt; key อื่นไม่ถูก mount</em>
</p>

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

<p align="center" id="fig-22">
  <img src="images/22-default-mode.png" alt="รูปที่ 22 defaultMode สิทธิ์ไฟล์" width="900"><br>
  <em><b>รูปที่ 22</b> defaultMode: 0400 → ไฟล์ -r-------- อ่านได้เฉพาะเจ้าของ (ค่าปกติ 0644); YAML ใช้เลขฐานแปดนำหน้าด้วย 0</em>
</p>

ค่าเริ่มต้นของไฟล์จาก ConfigMap คือ `0644` (`-rw-r--r--`) เปลี่ยนได้ทั้ง volume ด้วย `defaultMode` หรือรายไฟล์ด้วย `items[].mode` ใน YAML ให้เขียนเป็น **เลขฐานแปดนำหน้าด้วย 0** (`0400`) ถ้าเขียนใน JSON ต้องใช้เลขฐานสิบ (`256`) เพราะ JSON ไม่มีเลขฐานแปด ผลจริง `0400` → `-r--------` (อ่านได้เฉพาะเจ้าของ) เหมาะกับไฟล์ที่ไม่อยากให้ user อื่นใน container อ่าน (แต่จำไว้ว่าคนที่อ่าน ConfigMap ใน API ได้ก็ยังเห็นค่าอยู่ดี)

### 6.4 subPath: ไฟล์เดียวไม่ทับโฟลเดอร์ แต่ไม่อัปเดต

<p align="center" id="fig-23">
  <img src="images/23-subpath-single-file.png" alt="รูปที่ 23 subPath ไฟล์เดียว" width="900"><br>
  <em><b>รูปที่ 23</b> subPath: mount ไฟล์เดียวลงในโฟลเดอร์ที่มีไฟล์อื่นอยู่แล้วโดยไม่ทับทั้งโฟลเดอร์ — แต่ไฟล์ subPath จะไม่อัปเดตเมื่อแก้ ConfigMap</em>
</p>

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

<p align="center" id="fig-24">
  <img src="images/24-missing-configmap.png" alt="รูปที่ 24 อ้าง ConfigMap/key ที่ไม่มี" width="900"><br>
  <em><b>รูปที่ 24</b> อ้าง ConfigMap/key ที่ไม่มี → Pod ค้าง CreateContainerConfigError (configmap "not-here" not found / couldn't find key NOPE in ConfigMap default/shop-config); ถ้าเป็น volume → ContainerCreating + FailedMount</em>
</p>

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

<p align="center" id="fig-25">
  <img src="images/25-optional-true.png" alt="รูปที่ 25 optional: true" width="900"><br>
  <em><b>รูปที่ 25</b> optional: true → ไม่มีก็เริ่มได้ (env ว่าง, โฟลเดอร์ว่าง); สร้าง ConfigMap ภายหลัง Pod ที่ค้างจะเริ่มเองโดยไม่ต้องลบ (ทดสอบแล้ว)</em>
</p>

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

---

## 8. การอัปเดต ConfigMap

เมื่อแก้ ConfigMap (`kubectl apply`, `kubectl patch`, `kubectl edit`) API server เปลี่ยนค่าทันที แต่ "Pod เห็นค่าใหม่เมื่อไร" ขึ้นกับว่า Pod อ่านค่าทางไหน และแอปอ่านค่าอย่างไร นี่คือหัวข้อที่ผู้เริ่มต้นสับสนมากที่สุดของบทนี้

### 8.1 env ไม่เปลี่ยนจนกว่าจะได้ Pod ใหม่

<p align="center" id="fig-26">
  <img src="images/26-env-no-update.png" alt="รูปที่ 26 env ไม่อัปเดตเอง" width="900"><br>
  <em><b>รูปที่ 26</b> แก้ ConfigMap แล้ว env ใน Pod เดิมไม่เปลี่ยน (ค่าถูกคัดลอกตอนเริ่มเท่านั้น) — ต้องได้ Pod ใหม่</em>
</p>

env ถูกคัดลอกเข้า process ตอน container เริ่ม (ป้ายติดอกตอนเข้ากะ) หลังจากนั้นไม่มีใครไปแก้ env ของ process ที่รันอยู่ได้ ผลจริง

- LAB 6: patch `shop-config` 3 รอบ (`SHOP_NAME=ร้านใหม่1/2/3`) env `SHOP_NAME` ใน `envpod` ยังเป็น `ร้านน้องส้ม` ทุกรอบ
- LAB 10 ขั้น C1: apply ConfigMap ชื่อร้านใหม่ ธีม sunset และโปรโมชัน แล้วรอ 90 วินาที `/api/shop` ของทั้ง 3 Pod ยังเป็น `"shopName":"ร้านอาหารแมวน้องส้ม","theme":"harbor","promo":""` และ `RESTARTS 0`

ถ้าอยากให้ค่าใหม่มีผล ต้องได้ **Pod ใหม่** (container restart เฉย ๆ ภายใน Pod เดิมก็ได้ค่าใหม่เหมือนกัน แต่ไม่ควรพึ่งวิธีนั้น) ซึ่ง Deployment ทำให้ได้อย่างปลอดภัยด้วย rolling update (หัวข้อ 8.5)

### 8.2 volume อัปเดตเอง แต่ช้าราว 1 นาที

<p align="center" id="fig-27">
  <img src="images/27-volume-auto-update.png" alt="รูปที่ 27 volume อัปเดตเอง" width="900"><br>
  <em><b>รูปที่ 27</b> ไฟล์จาก volume อัปเดตเองโดยไม่ restart แต่ช้า: kubelet sync + cache → วัดได้ราว 1 นาที (37–88 วินาที)</em>
</p>

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

<p align="center" id="fig-28">
  <img src="images/28-data-symlink-swap.png" alt="รูปที่ 28 ..data symlink สลับทีเดียว" width="900"><br>
  <em><b>รูปที่ 28</b> เบื้องหลัง: ไฟล์จริงอยู่ในโฟลเดอร์ ..2026_10_05_… และ ..data เป็น symlink ชี้รุ่นล่าสุด — kubelet เขียนชุดใหม่แล้วสลับลิงก์ทีเดียว ไฟล์จึงไม่ครึ่ง ๆ กลาง ๆ</em>
</p>

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

<p align="center" id="fig-29">
  <img src="images/29-app-must-reload.png" alt="รูปที่ 29 แอปต้อง reload เอง" width="900"><br>
  <em><b>รูปที่ 29</b> ไฟล์เปลี่ยนแล้วแต่แอปที่อ่านไฟล์ครั้งเดียวตอนเริ่ม (เช่น nginx) ยังใช้ค่าเก่า → ต้องสั่ง nginx -s reload หรือให้แอปอ่านไฟล์ใหม่ทุกครั้ง</em>
</p>

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

<p align="center" id="fig-30">
  <img src="images/30-rollout-restart-checksum.png" alt="รูปที่ 30 rollout restart และ checksum" width="900"><br>
  <em><b>รูปที่ 30</b> ให้ Pod ใหม่รับค่า: kubectl rollout restart (เพิ่ม annotation kubectl.kubernetes.io/restartedAt) หรือใส่ checksum ของ config ใน template annotation — แก้ config แล้ว checksum เปลี่ยน → rollout เอง</em>
</p>

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

<p align="center" id="fig-31">
  <img src="images/31-immutable.png" alt="รูปที่ 31 immutable" width="900"><br>
  <em><b>รูปที่ 31</b> immutable: true → แก้ data ไม่ได้ (data: Forbidden: field is immutable when `immutable` is set) และเปลี่ยนกลับเป็น false ไม่ได้ ต้องลบสร้างใหม่หรือใช้ชื่อใหม่; kubelet ไม่ต้องคอยเฝ้า ลดภาระ API server</em>
</p>

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

<p align="center" id="fig-32">
  <img src="images/32-kustomize-generator.png" alt="รูปที่ 32 kustomize configMapGenerator" width="900"><br>
  <em><b>รูปที่ 32</b> kubectl apply -k: configMapGenerator สร้างชื่อมี hash (web-config-gh5tkgmddg) และแก้ชื่อใน Deployment ให้; แก้ไฟล์ → ชื่อใหม่ → Deployment rollout เอง (ตัวเก่าค้างไว้ ต้องลบเอง)</em>
</p>

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

<p align="center" id="fig-33">
  <img src="images/33-kube-system-examples.png" alt="รูปที่ 33 ConfigMap ของระบบ" width="900"><br>
  <em><b>รูปที่ 33</b> ระบบเองก็ใช้ ConfigMap: kube-system มี coredns (Corefile), kube-proxy (config.conf), kubelet-config; ทุก namespace มี kube-root-ca.crt ให้อัตโนมัติ</em>
</p>

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

<p align="center" id="fig-34">
  <img src="images/34-cross-namespace.png" alt="รูปที่ 34 อ้างข้าม namespace ไม่ได้" width="900"><br>
  <em><b>รูปที่ 34</b> Pod ใน namespace other อ้าง shop-config ของ default → CreateContainerConfigError: configmap "shop-config" not found — ต้องสร้างสำเนาใน namespace นั้นเอง</em>
</p>

`configMapRef`/`configMapKeyRef`/volume `configMap` มีแค่ `name` Kubernetes จึงหาใน namespace ของ Pod เสมอ ไฟล์ `02_LAB/labs/lab04-missing/other-ns.yaml` สร้าง Pod `x` ใน namespace `other` ที่อ้าง `shop-config` (ซึ่งอยู่ใน `default`) ผลจริง

```text
NAME   READY   STATUS                       RESTARTS   AGE
x      0/1     CreateContainerConfigError   0          12s
  Warning  Failed     11s (x2 over 11s)  kubelet            spec.containers{c}: Error: configmap "shop-config" not found
```

ข้อความบอกว่า "not found" ทั้งที่ `shop-config` มีอยู่จริงในอีก namespace นี่คือการแยกโซนของบทที่ 4 ทางแก้คือ **สร้างสำเนา ConfigMap ใน namespace ที่ใช้** (apply ไฟล์เดียวกันด้วย `-n <ns>` หรือใช้ kustomize สร้างให้หลาย namespace) ซึ่งก็สอดคล้องกับหลักที่แต่ละ environment มีค่าของตัวเอง

### 11.3 RBAC: สิทธิ์อ่านกับสิทธิ์แก้แยกกัน

<p align="center" id="fig-35">
  <img src="images/35-rbac-configmap.png" alt="รูปที่ 35 RBAC ของ ConfigMap" width="900"><br>
  <em><b>รูปที่ 35</b> สิทธิ์ ConfigMap แยกตามคำกริยา: Role get,list configmaps → อ่านได้ แต่ patch ไม่ได้ (Forbidden ... cannot patch resource "configmaps") และอ่านใน namespace อื่นไม่ได้</em>
</p>

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

<p align="center" id="fig-36">
  <img src="images/36-env-vs-volume.png" alt="รูปที่ 36 เลือก env หรือ volume" width="900"><br>
  <em><b>รูปที่ 36</b> ตารางเลือก: env/envFrom เหมาะกับค่าสั้น อ่านครั้งเดียวตอนเริ่ม เปลี่ยนต้อง restart; volume เหมาะกับไฟล์ตั้งค่า/ข้อความยาว อัปเดตเองได้ (~1 นาที) แต่แอปต้องอ่านใหม่; subPath ไม่อัปเดต</em>
</p>

| | env / envFrom | volume (ทั้งโฟลเดอร์ หรือ `items`) | subPath |
|---|---|---|---|
| เหมาะกับ | ค่าสั้น ๆ ชื่อ UPPER_SNAKE_CASE (ชื่อร้าน, ธีม, โปรโมชัน) | ไฟล์ตั้งค่า, ข้อความยาว, ไฟล์ไบนารี (`nginx.conf`, `announcement.txt`) | ไฟล์เดียวที่ต้องวางในโฟลเดอร์ที่มีไฟล์อื่นของ image |
| แอปอ่านอย่างไร | `process.env`, `$VAR` | อ่านไฟล์ | อ่านไฟล์ |
| แก้ ConfigMap แล้ว | ❌ ไม่เปลี่ยน ต้องได้ Pod ใหม่ | ✅ ไฟล์เปลี่ยนเองราว 1 นาที แต่แอปต้องอ่านใหม่ | ❌ ไม่เปลี่ยน ต้องได้ Pod ใหม่ |
| `binaryData` | ❌ ไม่ถูกนำไปเป็น env | ✅ | ✅ |
| ConfigMap ไม่มี | `CreateContainerConfigError` | ค้าง `ContainerCreating` (`FailedMount`) | ค้าง `ContainerCreating` |
| ร้านน้องส้ม LAB 10 | `som-web-config` (ชื่อร้าน, ธีม, โปรโมชัน) | `som-announcement` (ประกาศหน้าร้าน) | ไม่ใช้ |

### 12.2 แนวปฏิบัติ

<p align="center" id="fig-37">
  <img src="images/37-best-practices.png" alt="รูปที่ 37 แนวปฏิบัติ" width="900"><br>
  <em><b>รูปที่ 37</b> แนวปฏิบัติ: เก็บ ConfigMap เป็น YAML ใน git, ตั้งชื่อ key ชัด, ไม่ใส่ความลับ, ใช้ immutable/ชื่อมีเวอร์ชันสำหรับค่าที่ไม่ควรเปลี่ยนกลางทาง, ใช้ checksum หรือ generator ให้ rollout เมื่อ config เปลี่ยน</em>
</p>

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

<p align="center" id="fig-38">
  <img src="images/38-summary-map.png" alt="รูปที่ 38 แผนที่สรุปบท" width="900"><br>
  <em><b>รูปที่ 38</b> สรุปบท: สร้าง (literal/file/env-file/YAML) → ใช้ (env, envFrom, volume, items, subPath) → อัปเดต (restart vs อัปเดตเอง) → ป้องกัน (immutable, RBAC)</em>
</p>

| ขั้น | สิ่งที่เรียน | ข้อควรจำ |
|---|---|---|
| สร้าง | `--from-literal`, `--from-file`, `--from-env-file`, YAML, `--dry-run=client -o yaml` | ≤ 1 MiB, namespaced, `data` = UTF-8, `binaryData` = base64 |
| ใช้ | `configMapKeyRef`, `envFrom` (+`prefix`), `$(VAR)`, volume, `items`, `defaultMode`, `subPath` | env ชนะ envFrom, `$(VAR)` ในค่าจาก envFrom ไม่แทน, volume read-only |
| อัปเดต | env ต้อง Pod ใหม่, volume ราว 1 นาที (`..data`), แอปต้อง reload, `rollout restart`, checksum, ชื่อใหม่/generator | subPath ไม่อัปเดต |
| ป้องกัน | `immutable`, RBAC, `optional`, ไม่ใส่ความลับ | แก้ immutable ไม่ได้ ต้องสร้างใหม่ |

### 12.4 Cheatsheet คำสั่ง

<p align="center" id="fig-39">
  <img src="images/39-command-cheatsheet.png" alt="รูปที่ 39 cheatsheet คำสั่ง" width="900"><br>
  <em><b>รูปที่ 39</b> cheatsheet: kubectl create configmap / get cm -o yaml / describe cm / edit cm / rollout restart / apply -k</em>
</p>

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

<p align="center" id="fig-40">
  <img src="images/40-next-chapter-password.png" alt="รูปที่ 40 ปัญหาที่เหลือ → บท 011" width="900"><br>
  <em><b>รูปที่ 40</b> ปัญหาที่เหลือ: รหัส meow1234 ใน DATABASE_URL และ POSTGRES_PASSWORD ยังเขียนตรงใน YAML ใครดู Deployment/ConfigMap ก็เห็น → บท 011 Secret ซองปิดผนึก</em>
</p>

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
