# StatefulSet: หัวหน้ากะที่ตั้งเลขบูธและแจกตู้เซฟประจำตัว

> **รายวิชา:** Software Development Tools and Environments (DevTools)
> **หัวข้อ:** Kubernetes StatefulSet — ทำไม Deployment ไม่พอสำหรับระบบ stateful, การรับประกัน 3 ข้อ (ชื่อ, DNS, storage), กายวิภาค manifest, ชื่อ `<sts>-<ordinal>` และ label อัตโนมัติ, headless Service (`clusterIP: None`) และ DNS ต่อ Pod, `serviceName`, `volumeClaimTemplates`, `persistentVolumeClaimRetentionPolicy`, `podManagementPolicy` (OrderedReady/Parallel), `updateStrategy` (RollingUpdate, partition, OnDelete), ControllerRevision และ `rollout history/undo`, `minReadySeconds`, replicas ≠ replication (postgres streaming replication, Operator), StatefulSet กับ Node ล่ม (at most one, force delete, taint `out-of-service`), การย้ายข้อมูลจาก Deployment และแนวปฏิบัติ
> **ผลลัพธ์การเรียนรู้ที่เกี่ยวข้อง:** CLO-5, CLO-6
> **บทก่อนหน้า:** [บทที่ 8 PersistentVolume และ PVC](../../008_kubernetes_pv_pvc/01_Theory/README.md) · **LAB ของบทนี้:** [02_LAB](../02_LAB/README.md)

---

## บทคัดย่อ

บทที่ 8 จบลงที่ร้านอาหารแมวน้องส้ม **จำออเดอร์ได้แล้ว** ลบ Pod db, `rollout restart` db หรือลบ Deployment db ทั้งตัวแล้ว apply ใหม่ ข้อมูลก็ยังอยู่ในตู้เซฟ (PV) ที่ร้านถือใบเบิก (PVC) ไว้ แต่การทดลองท้ายบทก็แสดงข้อจำกัดใหญ่ของการรันฐานข้อมูลด้วย Deployment คือ **db มีได้ตัวเดียว** เพราะ Deployment ใช้ Pod template เดียว ทุก Pod จึงอ้าง `claimName` เดียวกัน เมื่อ scale เป็น 2 postgres สองตัวก็เขียนโฟลเดอร์เดียวกันจนออเดอร์หาย ชื่อ Pod ก็สุ่มใหม่ทุกครั้ง และ RollingUpdate ยังทำให้มี Pod สองตัวพร้อมกันได้ บทนี้แนะนำ **StatefulSet** หรือ **หัวหน้ากะที่ถือเครื่องจ่ายบัตรคิว** ซึ่งเปิดบูธทีละบูธตามเลข `-0`, `-1`, `-2` และ **แจกตู้เซฟประจำตัวที่มีเลขเดียวกับบูธ** ให้ทุกบูธ บูธ `-1` ถูกรื้อสร้างใหม่กี่ครั้งก็ได้ชื่อเดิมและกลับไปใช้ตู้ใบเดิมเสมอ

เนื้อหาเริ่มจากความต่างของงาน stateless กับ stateful แล้วอธิบาย **การรับประกัน 3 ข้อ** ของ StatefulSet ได้แก่ ชื่อคงที่ตามเลขลำดับ (ordinal), ที่อยู่ DNS คงที่ต่อ Pod ผ่าน **headless Service** (`clusterIP: None`) และ storage ประจำตัวจาก **`volumeClaimTemplates`** ต่อด้วยพฤติกรรมที่ต้องรู้เมื่อใช้งานจริง ได้แก่ PVC ที่ไม่หายเมื่อ scale down หรือลบ StatefulSet (และ `persistentVolumeClaimRetentionPolicy`), ลำดับการสร้าง/ลบแบบ **OrderedReady** กับ **Parallel**, การอัปเดตแบบ **RollingUpdate** ที่ไล่จากเลขมากไปน้อย, **partition** สำหรับ canary, **OnDelete**, **minReadySeconds** และ ControllerRevision กับ `rollout history`/`rollout undo` จากนั้นเป็นความจริงสำคัญสองข้อ คือ **replicas หลายตัวไม่ได้แปลว่าข้อมูลถูกคัดลอก** (ต้องทำ replication ระดับแอป เช่น postgres streaming replication หรือใช้ Operator) และ **StatefulSet ยอมให้มี Pod ชื่อเดียวกันได้ไม่เกิน 1 ตัว** จึงไม่สร้าง Pod แทนเมื่อ Node ล่มจนกว่าจะยืนยันได้ว่า Pod เดิมตายจริง (taint `node.kubernetes.io/out-of-service`) ปิดท้ายด้วยการเลือกชื่อที่ web ใช้ต่อ db, การย้ายข้อมูลจาก Deployment ของบทที่ 8 มาเป็น PVC `data-som-db-0` ของ StatefulSet และแนวปฏิบัติ

ผลลัพธ์คำสั่งและข้อความ error ที่ยกมาในเอกสารนี้มาจากการทดลองจริงบนคลัสเตอร์ kind (Kubernetes v1.37.0, kubectl v1.37.1) ใน LAB ประจำบทและการตรวจสอบก่อนเขียนบท (pre-check) เมื่อ 5 ตุลาคม 2569 **เวลา, AGE, IP, UID, ชื่อ PV (`pvc-<uid>`), revision hash และ Node ที่ Pod ถูกวางในเครื่องผู้เรียนจะต่างจากตัวอย่าง** เป็นเรื่องปกติ แต่ **ชื่อ Pod ของ StatefulSet (`web-0`, `som-db-0`) และชื่อ PVC (`www-web-1`, `data-som-db-0`) จะเหมือนกันทุกเครื่อง** ซึ่งเป็นหัวใจของบทนี้

## วัตถุประสงค์การเรียนรู้

เมื่อศึกษาเอกสารนี้จบ ผู้เรียนควรสามารถ

1. อธิบายความต่างของงาน stateless และ stateful และบอกเหตุผลที่ Deployment + PVC ไม่เหมาะกับฐานข้อมูลหลายตัว (template เดียว, ชื่อสุ่ม, RollingUpdate มีสองตัวพร้อมกัน)
2. อธิบายการรับประกัน 3 ข้อของ StatefulSet และอ่าน/เขียน manifest ที่มี `serviceName`, `replicas`, `selector`, `template`, `volumeClaimTemplates`, `updateStrategy`, `podManagementPolicy`, `minReadySeconds` และ `persistentVolumeClaimRetentionPolicy` ได้
3. บอกรูปแบบชื่อ Pod (`<sts>-<ordinal>`), hostname, label อัตโนมัติ (`statefulset.kubernetes.io/pod-name`, `apps.kubernetes.io/pod-index`, `controller-revision-hash`) และอธิบายว่าอะไรคงที่ อะไรเปลี่ยนเมื่อ Pod ถูกสร้างใหม่ (ชื่อ/PVC คงที่, UID/IP เปลี่ยน)
4. เขียน headless Service อธิบายความต่างจาก Service ClusterIP ใช้ชื่อ DNS `<pod>.<service>.<namespace>.svc.cluster.local` และอธิบายว่าทำไม Pod ที่ไม่ Ready จึงไม่อยู่ใน DNS
5. อธิบายการตั้งชื่อ PVC จาก `volumeClaimTemplates` (`<template>-<sts>-<ordinal>`), ความสัมพันธ์ระหว่าง PVC กับชื่อ Pod และความต่างระหว่าง `persistentVolumeClaimRetentionPolicy` (PVC) กับ `persistentVolumeReclaimPolicy` (PV)
6. อธิบาย `podManagementPolicy` แบบ OrderedReady และ Parallel และลำดับของการ scale up/down
7. ใช้ `updateStrategy` แบบ RollingUpdate (รวม `partition`) และ OnDelete, อ่าน `currentRevision`/`updateRevision`, ใช้ `kubectl rollout status/history/undo` กับ StatefulSet และอธิบายผลของ `minReadySeconds`
8. อธิบายว่าทำไม replicas หลายตัวไม่ได้แปลว่าข้อมูลถูก replicate และบอกแนวทาง replication ระดับแอปกับบทบาทของ Operator
9. อธิบายพฤติกรรม at-most-one ของ StatefulSet เมื่อ Node ล่ม ความเสี่ยงของ force delete และการใช้ taint `node.kubernetes.io/out-of-service` รวมถึงข้อจำกัดของ local storage
10. เลือกชื่อที่แอปใช้ต่อฐานข้อมูลได้ถูกต้อง ย้ายข้อมูลจาก Deployment + PVC เดิมเข้า StatefulSet และบอกแนวปฏิบัติสำหรับฐานข้อมูลบน Kubernetes

## สารบัญ

1. [บทนำ: อยากมีครัว 3 ครัว](#1-บทนำ-อยากมีครัว-3-ครัว)
2. [ทำไม Deployment ไม่พอสำหรับระบบ stateful](#2-ทำไม-deployment-ไม่พอสำหรับระบบ-stateful)
3. [คุณสมบัติของ StatefulSet](#3-คุณสมบัติของ-statefulset)
4. [headless Service และ DNS ต่อ Pod](#4-headless-service-และ-dns-ต่อ-pod)
5. [volumeClaimTemplates: ตู้เซฟประจำตัว](#5-volumeclaimtemplates-ตู้เซฟประจำตัว)
6. [ลำดับการสร้าง/ลบ: podManagementPolicy](#6-ลำดับการสร้างลบ-podmanagementpolicy)
7. [การอัปเดต: updateStrategy](#7-การอัปเดต-updatestrategy)
8. [replicas หลายตัว ≠ ข้อมูล replicate](#8-replicas-หลายตัว--ข้อมูล-replicate)
9. [StatefulSet กับ Node ล่ม](#9-statefulset-กับ-node-ล่ม)
10. [เปรียบเทียบและแนวปฏิบัติ](#10-เปรียบเทียบและแนวปฏิบัติ)
11. [สรุปและบทถัดไป](#11-สรุปและบทถัดไป)
12. [คำถามทบทวน](#12-คำถามทบทวน)
13. [เอกสารอ้างอิง](#13-เอกสารอ้างอิง)

### สารบัญรูปภาพ

| รูปที่ | เรื่อง | รูปที่ | เรื่อง |
|:---:|---|:---:|---|
| 1 | [อยากมีครัว 3 ครัว](#fig-1) | 20 | [Parallel](#fig-20) |
| 2 | [ทวนบท 008: ใบเบิกใบเดียว](#fig-2) | 21 | [RollingUpdate ไล่จากเลขมาก](#fig-21) |
| 3 | [อุปมาใหม่ของบทนี้](#fig-3) | 22 | [partition: canary](#fig-22) |
| 4 | [stateless กับ stateful](#fig-4) | 23 | [ControllerRevision](#fig-23) |
| 5 | [ชื่อสุ่มของ Deployment](#fig-5) | 24 | [OnDelete](#fig-24) |
| 6 | [การรับประกัน 3 ข้อ](#fig-6) | 25 | [minReadySeconds](#fig-25) |
| 7 | [กายวิภาค StatefulSet](#fig-7) | 26 | [สมุดแยกกัน 3 เล่ม](#fig-26) |
| 8 | [ชื่อตามเลขลำดับและ label](#fig-8) | 27 | [streaming replication](#fig-27) |
| 9 | [ชื่อเดิม UID ใหม่](#fig-9) | 28 | [Operator](#fig-28) |
| 10 | [Service ปกติกับ headless](#fig-10) | 29 | [at most one](#fig-29) |
| 11 | [รูปแบบชื่อ DNS](#fig-11) | 30 | [ความเสี่ยงของ force delete](#fig-30) |
| 12 | [nslookup headless](#fig-12) | 31 | [out-of-service กับ local-path](#fig-31) |
| 13 | [serviceName](#fig-13) | 32 | [เทียบ controller](#fig-32) |
| 14 | [PVC ต่อ Pod](#fig-14) | 33 | [web ต่อ db ด้วยชื่อไหน](#fig-33) |
| 15 | [PVC ติดตามชื่อ Pod](#fig-15) | 34 | [ย้ายข้อมูลจาก Deployment](#fig-34) |
| 16 | [PVC ไม่หายตาม](#fig-16) | 35 | [แนวปฏิบัติ](#fig-35) |
| 17 | [persistentVolumeClaimRetentionPolicy](#fig-17) | 36 | [ตารางสรุป](#fig-36) |
| 18 | [OrderedReady](#fig-18) | 37 | [คำสั่งประจำบท](#fig-37) |
| 19 | [scale down ย้อนลำดับ](#fig-19) | 38 | [ปิดบทและบทถัดไป](#fig-38) |

---

## 1. บทนำ: อยากมีครัว 3 ครัว

<p align="center">
  <img src="images/00-character-som.png" alt="น้องส้ม แมวส้มผู้ช่วยกัปตันท่าเรือ Kubernetes" width="320"><br>
  <em>น้องส้ม ผู้ช่วยกัปตันท่าเรือ Kubernetes ตัวละครหลักของบทนี้</em>
</p>

<p align="center" id="fig-1">
  <img src="images/01-opening-three-kitchens.png" alt="รูปที่ 1 อยากมีครัว 3 ครัว" width="900"><br>
  <em><b>รูปที่ 1</b> เปิดบทที่ 9: ต่อจากบท 008 — ร้านจำออเดอร์ได้แล้ว แต่ db มีได้ตัวเดียว น้องส้มอยากมีครัวหลายครัวที่แต่ละครัวมีชื่อและตู้เซฟของตัวเอง</em>
</p>

ตอนจบบทที่ 8 ครัวกลาง `som-db` ของร้านน้องส้มเป็น Deployment 1 ตัวแบบ `Recreate` ที่ใช้ PVC `som-db-data` (class `standard`, RWO, 1Gi) ลบ Pod db หรือลบ Deployment แล้ว apply ใหม่ ออเดอร์ก็ไม่หาย แต่ไฟล์ `10-db.yaml` ของบทที่ 8 มีคอมเมนต์เตือนไว้ชัดเจน

```yaml
spec:
  # replicas ต้องเป็น 1 — ทุก Pod ของ Deployment อ้าง PVC เดียวกัน
  # postgres 2 ตัวบนโฟลเดอร์ข้อมูลเดียวกัน = ข้อมูลพัง (บท 008 LAB 10 ขั้น F)
  replicas: 1
  # Recreate = ปิด Pod db เดิมให้หมดก่อน แล้วค่อยสร้างตัวใหม่ → ไม่มีช่วงที่ postgres 2 ตัวเปิดโฟลเดอร์เดียวกัน
  strategy:
    type: Recreate
```

น้องส้มอยากให้ร้านรองรับลูกค้ามากขึ้นและมีครัวสำรอง จึงอยากมี **ครัว 3 ครัว แต่ละครัวมีชื่อของตัวเองและตู้เซฟของตัวเอง** แต่ผู้จัดการร้าน (Deployment) ถือใบเบิกได้แค่ใบเดียว

<p align="center" id="fig-2">
  <img src="images/02-recap-008-shared-slip.png" alt="รูปที่ 2 ทวนบท 008: ใบเบิกใบเดียว" width="900"><br>
  <em><b>รูปที่ 2</b> ทวนบท 008: Deployment ใช้ Pod template เดียว ทุก Pod จึงอ้าง claimName เดียวกัน — replicas 2 = postgres สองตัวเขียนโฟลเดอร์เดียว (ทดสอบแล้วออเดอร์หาย บางครั้ง PANIC)</em>
</p>

ผลทดลองจริงของบทที่ 8 (LAB 10 ขั้น F) เมื่อสั่ง `kubectl -n som-shop scale deploy/som-db --replicas=2`

- Pod ตัวที่ 2 ถูกวางบน **Node เดียวกัน** (ตาม nodeAffinity ของ PV) และ `Running` ทั้งคู่ เพราะ RWO กันแค่ "ต่าง Node" ไม่ได้กัน "ต่าง Pod"
- postgres สองตัวเปิดโฟลเดอร์ `pgdata` เดียวกัน ข้อมูลที่แต่ละตัวเห็นไม่ตรงกัน (`orders=6` กับ `orders=3`)
- เมื่อ scale กลับ ตัวที่เหลือหยุดตัวเองด้วย `performing immediate shutdown because data directory lock file is invalid` แล้วเริ่มใหม่ได้ **`orders=3` ออเดอร์หายไป 3 รายการ** และใน pre-check มีรอบที่หนักกว่านั้นคือ `PANIC: could not locate a valid checkpoint record`

ปัญหาไม่ได้อยู่ที่ PVC แต่อยู่ที่ **Deployment ถูกออกแบบมาให้ Pod ทุกตัวเหมือนกันและใช้แทนกันได้** ซึ่งตรงข้ามกับสิ่งที่ฐานข้อมูลต้องการ บทนี้จึงแนะนำ controller ตัวใหม่ที่ออกแบบมาเพื่องานที่ "แต่ละตัวมีตัวตน"

<p align="center" id="fig-3">
  <img src="images/03-metaphor-legend.png" alt="รูปที่ 3 อุปมาใหม่ของบทนี้" width="900"><br>
  <em><b>รูปที่ 3</b> อุปมาใหม่: StatefulSet = หัวหน้ากะที่ตั้งชื่อบูธตามเลขลำดับและแจกตู้เซฟประจำตัว, volumeClaimTemplates = สมุดใบเบิกฉีกได้, headless Service = สมุดรายชื่อบอกเลขบูธตรง ๆ</em>
</p>

**ตารางที่ 1** อุปมาท่าเรือที่ใช้ในบทนี้ (ต่อจากบทที่ 1–8)

| Kubernetes | อุปมาท่าเรือ | ใหม่ในบทนี้ |
|---|---|:---:|
| container / Pod / Node / Namespace | ตู้สินค้า / บูธร้าน / เรือ / โซนทาสี | |
| ReplicaSet / Deployment / Service | หัวหน้ากะ / ผู้จัดการร้าน / ประภาคาร (บทที่ 5–7) | |
| PV / PVC / StorageClass | ตู้เซฟบนเรือ / ใบเบิกตู้เซฟ / โรงทำตู้อัตโนมัติ (บทที่ 8) | |
| **StatefulSet** | **หุ่นยนต์หัวหน้ากะสีม่วง-กรมท่าที่ถือเครื่องจ่ายบัตรคิวตัวเลข** เปิดบูธทีละบูธ ติดป้าย `-0`, `-1`, `-2` | ✅ |
| ordinal (เลขลำดับ) | **บัตรคิวตัวเลข** ที่ติดบนป้ายบูธ เลขเดิมกลับมาเสมอ | ✅ |
| **volumeClaimTemplates** | **สมุดใบเบิกที่พิมพ์ไว้แล้ว** ฉีกทีละใบให้บูธแต่ละเลข ได้ตู้เซฟเลขเดียวกับบูธ | ✅ |
| **headless Service** | **สมุดรายชื่อบนแท่นอ่าน (ไม่มีไฟประภาคาร)** บอกที่อยู่ของแต่ละบูธตรง ๆ | ✅ |
| `partition` | **เชือกกั้นแถวบูธ** บูธที่อยู่หลังเชือกเท่านั้นที่ได้ของรุ่นใหม่ | ✅ |
| streaming replication | **สายพานส่งหน้าสมุด** จากบูธ `-0` ไปบูธสำเนา (อ่านอย่างเดียว) | ✅ |
| Node ล่ม | **เรือติดหมอก** มองไม่เห็นว่าบูธบนเรือยังทำงานอยู่หรือไม่ | ✅ |

> **ข้อควรจำของอุปมา:** หัวหน้ากะของบทที่ 5 (ReplicaSet) สนใจแค่ "จำนวนบูธครบไหม" บูธไหนหายก็สร้างบูธใหม่ชื่อใหม่ แต่หัวหน้ากะของบทนี้ **จำว่าบูธเลขไหนหายไป แล้วสร้างบูธเลขนั้นคืนพร้อมคืนตู้เซฟเลขเดิม** และจะไม่ยอมเปิดบูธเลขเดียวกันสองบูธพร้อมกันเด็ดขาด

**เป้าหมายของบทนี้:** เมื่อจบ LAB 10 ครัวกลางของร้านน้องส้มจะเป็น StatefulSet `som-db` ที่ใช้ข้อมูลเดิมจากบทที่ 8 (ย้าย PV มาเป็น PVC `data-som-db-0`) ลบ Pod `som-db-0` แล้วได้ `som-db-0` คืนพร้อมตู้เดิม ลบ StatefulSet ทั้งตัวแล้ว apply ใหม่ ออเดอร์ยังอยู่ และเห็นด้วยตาว่า scale เป็น 3 ได้ฐานข้อมูล 3 ตัวที่ **ข้อมูลแยกกัน** ไม่ใช่สำเนา พร้อม LAB เสริมที่ทำ read replica จริงด้วย postgres streaming replication

---

## 2. ทำไม Deployment ไม่พอสำหรับระบบ stateful

### 2.1 stateless กับ stateful

<p align="center" id="fig-4">
  <img src="images/04-stateless-vs-stateful.png" alt="รูปที่ 4 stateless กับ stateful" width="900"><br>
  <em><b>รูปที่ 4</b> stateless (web) สลับตัวไหนก็ได้ เหมือนชามกระดาษใช้แล้วทิ้ง; stateful (db) แต่ละตัวมีข้อมูล/ตัวตนของตัวเอง เหมือนชามเซรามิกสลักชื่อ</em>
</p>

**งาน stateless** คืองานที่ไม่เก็บสถานะสำคัญไว้ในตัวเอง ทุก request ตอบได้จากข้อมูลที่ได้รับหรือดึงจากที่อื่น เช่น หน้าร้าน `som-web` ของน้องส้มที่อ่านเขียนข้อมูลผ่าน db เสมอ Pod ไหนตอบก็ได้ผลเหมือนกัน หายไปตัวหนึ่งก็สร้างตัวใหม่ชื่อใหม่มาแทนได้ทันที Deployment จึงเหมาะที่สุด

**งาน stateful** คืองานที่แต่ละตัวมี "ของเฉพาะตัว" ที่ต้องคงอยู่ เช่น ฐานข้อมูล (PostgreSQL, MySQL), message broker (Kafka, RabbitMQ), ระบบ consensus (etcd, ZooKeeper) หรือ search engine (Elasticsearch) ซึ่งมักต้องการ

**ตารางที่ 2** สิ่งที่งาน stateful ต้องการ

| ความต้องการ | ตัวอย่าง | Deployment ให้ได้ไหม |
|---|---|:---:|
| ตัวตนคงที่ (ชื่อเดิมหลังเกิดใหม่) | สมาชิก etcd รู้จักกันด้วยชื่อ `etcd-0`, `etcd-1` | ❌ ชื่อสุ่มทุกครั้ง |
| ที่อยู่เครือข่ายคงที่ต่อตัว | replica ของ postgres ต้องต่อไปที่ primary ตัวเดิมเสมอ | ❌ Service ClusterIP กระจายไปทุกตัว |
| storage ประจำตัว (คนละก้อน) | แต่ละ broker เก็บ partition ของตัวเอง | ❌ ทุก Pod ใช้ `claimName` เดียวกัน |
| ลำดับการเริ่ม/หยุด | ต้องเปิดตัวหลักก่อน ตัวรองจึงมาขอเข้าร่วม | ❌ สร้าง/ลบพร้อมกัน |
| ไม่มีสองตัวที่เป็น "คนเดียวกัน" พร้อมกัน | ห้ามมี primary สองตัวเขียนข้อมูลเดียวกัน | ❌ RollingUpdate เปิดตัวใหม่ก่อนปิดตัวเก่า |

### 2.2 สามจุดอ่อนของ Deployment กับฐานข้อมูล

<p align="center" id="fig-5">
  <img src="images/05-deployment-random-names.png" alt="รูปที่ 5 ชื่อสุ่มของ Deployment" width="900"><br>
  <em><b>รูปที่ 5</b> Pod ของ Deployment ชื่อสุ่ม (som-db-7b786655f5-9hf7p) เปลี่ยนทุกครั้งที่สร้างใหม่ และ RollingUpdate ทำให้มี 2 ตัวพร้อมกันได้ — ไม่เหมาะกับ db ที่ต้องรู้ว่าใครคือใคร</em>
</p>

1. **Pod template เดียว = ใบเบิกใบเดียว** ทุก Pod ที่ ReplicaSet สร้างมาจาก template เดียวกันทุกตัวอักษร ถ้า template มี `persistentVolumeClaim: {claimName: som-db-data}` ทุก Pod ก็ใช้ PVC เดียวกัน ไม่มีทางเขียน template ให้ Pod ตัวที่ 2 ได้ PVC อีกใบ
2. **ชื่อสุ่ม** ชื่อ Pod ของ Deployment คือ `<deployment>-<pod-template-hash>-<สุ่ม 5 ตัว>` เช่น `som-db-7b786655f5-bdsgq` (ผลจริงจาก LAB 10 ขั้น A) ลบแล้วได้ชื่อใหม่ เปลี่ยน template แล้ว hash ก็เปลี่ยน ไม่มีใครรู้ล่วงหน้าว่า "ตัวหลัก" ชื่ออะไร
3. **RollingUpdate เปิดตัวใหม่ก่อนปิดตัวเก่า** (บทที่ 7) ค่า default `maxSurge: 25%` ทำให้ช่วงเปลี่ยนรุ่นมี Pod สองตัวรันพร้อมกัน บทที่ 8 จึงต้องใช้ `Recreate` กับ db ซึ่งแลกกับช่วงที่ไม่มี db เลย

ผลจริงจาก LAB 1 ของบทนี้ที่สร้าง nginx 3 ตัวด้วย Deployment `web-d` แล้วลบ Pod ไปหนึ่งตัว ได้ Pod ชื่อใหม่ `web-d-d8cf7b4b8-d7zkr` มาแทน `web-d-d8cf7b4b8-lgww5` ส่วน StatefulSet `web` ได้ `web-1` คืนมาชื่อเดิม (หัวข้อ 3.4)

> **ข้อควรจำ:** Deployment ไม่ได้ "ผิด" มันถูกออกแบบมาให้ Pod เป็น **ชามกระดาษ** ที่ใช้แทนกันได้ งานแบบนั้นควรใช้ Deployment ต่อไป (หน้าร้าน `som-web` ในบทนี้ยังเป็น Deployment) StatefulSet มีไว้สำหรับ **ชามเซรามิกสลักชื่อ** เท่านั้น

---

## 3. คุณสมบัติของ StatefulSet

### 3.1 การรับประกัน 3 ข้อ

<p align="center" id="fig-6">
  <img src="images/06-three-guarantees.png" alt="รูปที่ 6 การรับประกัน 3 ข้อ" width="900"><br>
  <em><b>รูปที่ 6</b> StatefulSet รับประกัน 3 อย่าง: ชื่อคงที่ (&lt;sts&gt;-0..N), ที่อยู่ DNS คงที่ต่อ Pod, และ storage ประจำตัวที่ตามกลับมาทุกครั้ง</em>
</p>

**StatefulSet** (`apps/v1`) เป็น workload controller ที่ดูแลกลุ่ม Pod ที่สร้างจาก template เดียวกันเหมือน Deployment แต่ **ให้ Pod แต่ละตัวมีตัวตนที่คงที่ (sticky identity)** ไม่ว่าจะถูกสร้างใหม่บน Node ไหนกี่ครั้ง ตามเอกสาร Kubernetes StatefulSet เหมาะกับงานที่ต้องการอย่างน้อยหนึ่งข้อต่อไปนี้

**ตารางที่ 3** การรับประกันของ StatefulSet

| ข้อ | การรับประกัน | ได้มาจาก | หลักฐานในบทนี้ |
|---|---|---|---|
| 1 | **ชื่อ (ตัวตน) คงที่** `<sts>-<ordinal>` | ordinal 0..N-1 ที่ controller กำหนด | ลบ `web-1` ได้ `web-1` คืน (LAB 1) |
| 2 | **ที่อยู่เครือข่ายคงที่** `<pod>.<service>` | headless Service ที่ระบุใน `serviceName` | `nslookup web-0.web.default.svc.cluster.local` (LAB 2) |
| 3 | **storage ประจำตัว** ที่ตามชื่อ Pod | `volumeClaimTemplates` → PVC `<template>-<pod>` | ลบ Pod แล้ว `first-born web-1` เดิม (LAB 3) |
| + | **ลำดับ** การสร้าง ลบ และอัปเดต | `podManagementPolicy`, `updateStrategy` | `bad-0` ไม่ Ready → `bad-1` ไม่เกิด (LAB 4) |

สิ่งที่ StatefulSet **ไม่ได้** ให้ (จะเห็นในหัวข้อ 8–9): ไม่คัดลอกข้อมูลระหว่าง Pod, ไม่สลับตัวหลักเมื่อตัวหลักตาย, ไม่ทำให้ local storage ย้าย Node ได้ และไม่สร้าง headless Service ให้เอง

### 3.2 กายวิภาค manifest

<p align="center" id="fig-7">
  <img src="images/07-manifest-anatomy.png" alt="รูปที่ 7 กายวิภาค StatefulSet" width="900"><br>
  <em><b>รูปที่ 7</b> โครง StatefulSet: serviceName (ชื่อ headless Service), replicas, selector, template และ volumeClaimTemplates — ไม่มี strategy แบบ Deployment แต่ใช้ updateStrategy</em>
</p>

ตัวอย่างจริงจาก `02_LAB/labs/lab03-vct/sts.yaml` (ใช้ใน LAB 3–8) ประกอบด้วย headless Service และ StatefulSet ในไฟล์เดียว

```yaml
# LAB 3 (ใช้ต่อใน LAB 4–8): StatefulSet web + ตู้เซฟประจำบูธ (volumeClaimTemplates)
# ได้ PVC ชื่อ <template>-<sts>-<เลข> = www-web-0, www-web-1, www-web-2
apiVersion: v1
kind: Service
metadata:
  name: web
spec:
  clusterIP: None                    # headless (เหมือน LAB 2)
  selector:
    app: web
  ports:
    - name: http
      port: 80
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: web
spec:
  serviceName: web
  replicas: 3
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      terminationGracePeriodSeconds: 5
      containers:
        - name: nginx
          image: nginx:1.27-alpine
          # เขียน "first-born ..." เฉพาะครั้งแรก (ถ้าไฟล์มีอยู่แล้วใน PVC = ไม่เขียนทับ) → ดูได้ว่าตู้เซฟเป็นใบเดิมไหม
          command:
            - sh
            - -c
            - '[ -f /usr/share/nginx/html/index.html ] || echo "first-born $(hostname) $(date +%T)" > /usr/share/nginx/html/index.html; exec nginx -g "daemon off;"'
          ports:
            - name: http
              containerPort: 80
          readinessProbe:
            httpGet:
              path: /
              port: 80
            periodSeconds: 2
          volumeMounts:
            - name: www                    # ต้องตรงกับชื่อใน volumeClaimTemplates
              mountPath: /usr/share/nginx/html
  # สมุดใบเบิกตู้เซฟ: ฉีก 1 ใบต่อ 1 Pod (ไม่มี storageClassName = ใช้ default "standard")
  volumeClaimTemplates:
    - metadata:
        name: www
      spec:
        accessModes: [ReadWriteOnce]
        resources:
          requests:
            storage: 10Mi
```

**ตารางที่ 4** ฟิลด์ใน `spec` ของ StatefulSet

| ฟิลด์ | ความหมาย | ค่า default |
|---|---|---|
| `serviceName` | ชื่อ headless Service ที่ "ดูแลโดเมน" ของ Pod (governing Service) ใช้สร้างชื่อ DNS `<pod>.<serviceName>` | – (ควรใส่เสมอ) |
| `replicas` | จำนวน Pod (ordinal 0 ถึง replicas-1) | 1 |
| `selector` | label ที่ใช้เลือก Pod ต้องตรงกับ `template.metadata.labels` (แก้ภายหลังไม่ได้) | – (บังคับ) |
| `template` | Pod template เหมือน Deployment | – (บังคับ) |
| `volumeClaimTemplates` | แม่แบบ PVC ที่สร้าง 1 ใบต่อ Pod ต่อแม่แบบ | ไม่มี (ไม่มี storage ประจำตัว) |
| `podManagementPolicy` | `OrderedReady` (ทีละตัวตามลำดับ) หรือ `Parallel` | `OrderedReady` |
| `updateStrategy` | `RollingUpdate` (มี `partition`, `maxUnavailable`) หรือ `OnDelete` | `{"rollingUpdate":{"maxUnavailable":1,"partition":0},"type":"RollingUpdate"}` |
| `minReadySeconds` | Pod ต้อง Ready ต่อเนื่องกี่วินาทีจึงนับว่า available | 0 |
| `persistentVolumeClaimRetentionPolicy` | ลบ PVC เมื่อ scale down (`whenScaled`) / ลบ StatefulSet (`whenDeleted`) หรือไม่ | `{"whenDeleted":"Retain","whenScaled":"Retain"}` |
| `revisionHistoryLimit` | จำนวน ControllerRevision ที่เก็บไว้ | 10 (ตามเอกสาร Kubernetes) |
| `ordinals.start` | เลขเริ่มต้นของ ordinal (เช่นเริ่มที่ 1 แทน 0) | 0 (แนวคิด — ไม่ได้ใช้ใน LAB) |

ค่า default ของ `podManagementPolicy`, `updateStrategy` และ `persistentVolumeClaimRetentionPolicy` ยืนยันจากการทดลองจริงด้วย `kubectl get sts web -o jsonpath=...` (LAB 5 และ LAB 6)

```text
{"whenDeleted":"Retain","whenScaled":"Retain"}
{"rollingUpdate":{"maxUnavailable":1,"partition":0},"type":"RollingUpdate"}
```

**ความต่างจาก Deployment ที่ต้องจำ**

- StatefulSet **ไม่มี `strategy`** แต่มี **`updateStrategy`** (ชื่อและค่าต่างกัน: ไม่มี `Recreate` ไม่มี `maxSurge`)
- StatefulSet **ไม่ใช้ ReplicaSet** มันสร้างและดูแล Pod เองโดยตรง รุ่นของ template เก็บเป็น **ControllerRevision** (หัวข้อ 7.3)
- `volumeClaimTemplates` อยู่ระดับเดียวกับ `template` (ไม่ได้อยู่ใน Pod spec) และในกรณีทั่วไป **แก้ไขหลังสร้างไม่ได้** ถ้าต้องเปลี่ยนขนาดหรือ class ต้องสร้าง StatefulSet ใหม่หรือแก้ที่ PVC โดยตรง
- `volumeMounts[].name` ใน container ต้องตรงกับ `volumeClaimTemplates[].metadata.name` (ในตัวอย่างคือ `www`) โดยไม่ต้องเขียน `volumes:` ใน Pod spec เอง

### 3.3 ชื่อ ลำดับ hostname และ label อัตโนมัติ

<p align="center" id="fig-8">
  <img src="images/08-ordinal-names-labels.png" alt="รูปที่ 8 ชื่อตามเลขลำดับและ label" width="900"><br>
  <em><b>รูปที่ 8</b> ชื่อ Pod = &lt;ชื่อ sts&gt;-&lt;ลำดับ&gt; และมี label อัตโนมัติ statefulset.kubernetes.io/pod-name กับ apps.kubernetes.io/pod-index — ใช้เลือก Pod รายตัวได้</em>
</p>

StatefulSet ที่มี `replicas: N` จะมี Pod ชื่อ `<ชื่อ sts>-0` ถึง `<ชื่อ sts>-(N-1)` เลขนี้เรียกว่า **ordinal** และ **hostname ภายใน Pod = ชื่อ Pod** ผลจริงจาก LAB 1 ที่ apply Deployment `web-d` และ StatefulSet `web` พร้อมกัน

```text
NAME                        READY   STATUS    RESTARTS   AGE   IP           NODE          NOMINATED NODE   READINESS GATES
pod/web-0                   1/1     Running   0          25s   10.244.2.4   lab-worker2   <none>           <none>
pod/web-1                   1/1     Running   0          15s   10.244.1.3   lab-worker    <none>           <none>
pod/web-2                   1/1     Running   0          14s   10.244.2.5   lab-worker2   <none>           <none>
pod/web-d-d8cf7b4b8-lgww5   1/1     Running   0          25s   10.244.2.2   lab-worker2   <none>           <none>
pod/web-d-d8cf7b4b8-pgrgg   1/1     Running   0          25s   10.244.1.2   lab-worker    <none>           <none>
pod/web-d-d8cf7b4b8-vn6cv   1/1     Running   0          25s   10.244.2.3   lab-worker2   <none>           <none>
```

สังเกต AGE: Pod ของ Deployment เกิดพร้อมกัน (25s ทั้งสามตัว) ส่วน `web-0` เกิดก่อน (25s) แล้ว `web-1` (15s) และ `web-2` (14s) จึงตามมา เพราะ StatefulSet รอให้ตัวก่อนหน้า Ready ก่อน (หัวข้อ 6) `web-0` ใช้เวลานานเพราะ Node ต้องดึง image nginx ครั้งแรก

StatefulSet ใส่ label ให้ Pod อัตโนมัติ 3 ตัว นอกเหนือจาก label ที่เราเขียนใน template

```text
NAME    READY   STATUS    RESTARTS   AGE   LABELS
web-1   1/1     Running   0          15s   app=web,apps.kubernetes.io/pod-index=1,controller-revision-hash=web-8776b8748,statefulset.kubernetes.io/pod-name=web-1
```

**ตารางที่ 5** label อัตโนมัติบน Pod ของ StatefulSet

| label | ค่า | ใช้ทำอะไร |
|---|---|---|
| `statefulset.kubernetes.io/pod-name` | ชื่อ Pod (`web-1`) | ทำ Service ที่ชี้ Pod ตัวเดียว (selector ด้วย label นี้) |
| `apps.kubernetes.io/pod-index` | ordinal (`1`) | เลือก Pod ตามเลข เช่นในสคริปต์หรือ affinity |
| `controller-revision-hash` | revision ที่ Pod นี้ใช้ (`web-8776b8748`) | บอกว่า Pod เป็นรุ่นไหนระหว่าง rollout (หัวข้อ 7.3) |

### 3.4 ลบ Pod แล้วได้ชื่อเดิม

<p align="center" id="fig-9">
  <img src="images/09-same-name-new-uid.png" alt="รูปที่ 9 ชื่อเดิม UID ใหม่" width="900"><br>
  <em><b>รูปที่ 9</b> ลบ Pod som-db-0 → ได้ Pod ชื่อเดิม som-db-0 แต่ UID และ IP ใหม่ และต่อ PVC เดิม data-som-db-0 (ทดสอบแล้ว)</em>
</p>

เมื่อ Pod ของ StatefulSet ถูกลบ controller จะสร้าง Pod **ชื่อเดิม** กลับมา แต่ Pod ตัวใหม่เป็น object ใหม่ จึงได้ **UID ใหม่** และ **IP ใหม่** (IP ผูกกับ Pod ไม่ใช่ชื่อ) ส่วน PVC ที่ใช้ **เป็นใบเดิม** เพราะชื่อ PVC คำนวณจากชื่อ Pod ผลจริงจาก LAB 10 ขั้น C

```text
ea0d5d48-b079-4995-8241-096236c5d94a 10.244.2.45 lab-worker2
pod "som-db-0" deleted from som-shop namespace
pod/som-db-0 condition met
acfc1cf3-faf0-43fc-ae01-83de4303be62 10.244.2.48 lab-worker2 claimName=data-som-db-0
```

**ตารางที่ 6** อะไรคงที่ อะไรเปลี่ยน เมื่อ Pod ของ StatefulSet ถูกสร้างใหม่

| สิ่งที่ดู | Deployment | StatefulSet |
|---|---|---|
| ชื่อ Pod / hostname | เปลี่ยน (`…-lgww5` → `…-d7zkr`) | **คงที่** (`web-1` → `web-1`) |
| UID | เปลี่ยน | เปลี่ยน (`3091ecf4…` → `1e1cfe64…`) |
| IP ของ Pod | เปลี่ยน | เปลี่ยน (`10.244.1.3` → `10.244.1.5`) |
| ชื่อ DNS รายตัว | ไม่มี | **คงที่** (`web-1.web`) ชี้ IP ใหม่ให้เอง |
| PVC | ใบเดียวกันทุก Pod | **ใบประจำตัวเดิม** (`www-web-1`) |
| Node | scheduler เลือกใหม่ | scheduler เลือกใหม่ (แต่ถ้า PV ผูก Node เช่น local-path ต้องกลับ Node เดิม) |

> **ข้อควรจำ:** "ตัวตนคงที่" ของ StatefulSet คือ **ชื่อ + DNS + PVC** ไม่ใช่ IP แอปที่ต่อกันจึงต้องใช้ **ชื่อ DNS** เสมอ ห้ามจำ IP ของ Pod

---

## 4. headless Service และ DNS ต่อ Pod

### 4.1 Service ปกติกับ headless Service

<p align="center" id="fig-10">
  <img src="images/10-normal-vs-headless.png" alt="รูปที่ 10 Service ปกติกับ headless" width="900"><br>
  <em><b>รูปที่ 10</b> Service ปกติมี ClusterIP เดียวแล้วกระจายไปทุก Pod; headless (clusterIP: None) ไม่มี IP กลาง DNS ตอบ IP ของ Pod โดยตรงและมีชื่อรายตัว</em>
</p>

บทที่ 6 Service แบบ ClusterIP เป็น **ประภาคาร** ที่มี IP กลางหนึ่งตัว (เช่น `10.96.99.37`) kube-proxy กระจาย connection ที่มาถึง IP นี้ไปยัง Pod ที่ Ready ตัวใดตัวหนึ่ง ผู้เรียกไม่รู้และไม่ต้องรู้ว่าได้ Pod ไหน ซึ่งดีสำหรับ web แต่ไม่ดีสำหรับฐานข้อมูลที่ต้องการต่อ "ตัวหลัก" ตัวเดิมเสมอ

**headless Service** คือ Service ที่ตั้ง `spec.clusterIP: None` จึง **ไม่มี IP กลางและ kube-proxy ไม่ทำ load balancing** สิ่งที่ได้แทนคือ DNS ที่ตอบ **IP ของ Pod โดยตรง** และเมื่อใช้คู่กับ StatefulSet Pod แต่ละตัวยังได้ **ชื่อ DNS รายตัว** เปรียบเหมือน **สมุดรายชื่อบนแท่นอ่าน** ที่ไม่มีไฟประภาคาร แต่บอกที่อยู่ของทุกบูธตรง ๆ

ไฟล์จริงจาก `02_LAB/labs/lab02-headless/svc-headless.yaml`

```yaml
# LAB 2: headless Service = สมุดรายชื่อบนแท่นอ่าน (ไม่มีไฟประภาคาร / ไม่มี ClusterIP)
# DNS ตอบ IP ของ Pod ที่ Ready ทุกตัว และมีชื่อรายตัว web-0.web, web-1.web, ...
apiVersion: v1
kind: Service
metadata:
  name: web
spec:
  clusterIP: None          # ← จุดสำคัญ: None = headless
  selector:
    app: web
  ports:
    - name: http
      port: 80
```

ผลจริงหลัง apply (LAB 2) คอลัมน์ `CLUSTER-IP` เป็น `None` แต่ยังมี EndpointSlice ที่มี IP ของทุก Pod เหมือน Service ปกติ

```text
NAME   TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)   AGE
web    ClusterIP   None         <none>        80/TCP    2s
...
NAME        ADDRESSTYPE   PORTS   ENDPOINTS                          AGE
web-jjj67   IPv4          80      10.244.2.6,10.244.1.6,10.244.2.7   2s
```

**ตารางที่ 7** Service ClusterIP กับ headless Service

| | ClusterIP (บทที่ 6) | headless (`clusterIP: None`) |
|---|---|---|
| IP กลาง | มี 1 ตัว (คงที่ตลอดอายุ Service) | ไม่มี (`None`) |
| DNS ของชื่อ Service ตอบ | ClusterIP ตัวเดียว | IP ของ **ทุก Pod ที่ Ready** (หลายบรรทัด) |
| load balancing | kube-proxy กระจายต่อ connection | ไม่มี ผู้เรียกเลือกเองจากรายการ IP |
| ชื่อรายตัว `<pod>.<svc>` | ไม่มี | มี เมื่อเป็น `serviceName` ของ StatefulSet |
| `type: NodePort` | ได้ | ไม่ได้ (headless ใช้ภายในคลัสเตอร์) |
| เหมาะกับ | web, API ที่ Pod ใช้แทนกันได้ | ฐานข้อมูล, cluster ที่สมาชิกต้องรู้จักกันรายตัว |

### 4.2 รูปแบบชื่อ DNS ต่อ Pod

<p align="center" id="fig-11">
  <img src="images/11-dns-format.png" alt="รูปที่ 11 รูปแบบชื่อ DNS" width="900"><br>
  <em><b>รูปที่ 11</b> รูปแบบ DNS ต่อ Pod: &lt;pod&gt;.&lt;service&gt;.&lt;namespace&gt;.svc.cluster.local เช่น som-db-0.som-db.som-shop.svc.cluster.local — ใน namespace เดียวกันใช้ som-db-0.som-db ได้</em>
</p>

**ตารางที่ 8** ชื่อ DNS ที่ได้จาก StatefulSet `som-db` + headless Service `som-db` ใน namespace `som-shop`

| ชื่อ | ตอบอะไร | ใช้เมื่อ |
|---|---|---|
| `som-db-0.som-db.som-shop.svc.cluster.local` | IP ของ Pod `som-db-0` ตัวเดียว | ชื่อเต็ม ใช้ได้จากทุก namespace |
| `som-db-0.som-db.som-shop` | เหมือนบรรทัดบน (ต่อท้าย `.svc.cluster.local` ด้วย search domain) | เรียกข้าม namespace |
| `som-db-0.som-db` | เหมือนบรรทัดบน | เรียกจาก Pod ใน namespace `som-shop` เดียวกัน (ร้านน้องส้มใช้แบบนี้) |
| `som-db` หรือ `som-db.som-shop.svc.cluster.local` | IP ของ **ทุก Pod ที่ Ready** ที่ selector ของ Service เลือก | ค้นหาสมาชิกทั้งหมด |

ชื่อย่อทำงานได้เพราะ `/etc/resolv.conf` ของ Pod มี **search domain** (บทที่ 4) เช่น `som-shop.svc.cluster.local svc.cluster.local cluster.local` resolver จึงลองต่อท้ายชื่อทีละโดเมนจนเจอ ร้านน้องส้มในบทนี้จึงตั้ง `DATABASE_URL=postgres://som:meow1234@som-db-0.som-db:5432/catshop` (รหัส `meow1234` เป็นค่าตัวอย่างเพื่อการเรียนเท่านั้น)

### 4.3 nslookup กับ Pod ที่ Ready และไม่ Ready

<p align="center" id="fig-12">
  <img src="images/12-nslookup-headless.png" alt="รูปที่ 12 nslookup headless" width="900"><br>
  <em><b>รูปที่ 12</b> nslookup ชื่อ headless Service ได้ IP ของทุก Pod ที่ Ready (หลายบรรทัด) ส่วน nslookup ชื่อรายตัวได้ IP เดียว — Pod ที่ไม่ Ready ไม่อยู่ในคำตอบ</em>
</p>

ผลจริงจาก LAB 2 ใน Pod busybox (`kubectl run dns --image=busybox:1.36 --rm -it --restart=Never -- sh`)

```text
/ # nslookup web
Server:		10.96.0.10
Address:	10.96.0.10:53


** server can't find web.cluster.local: NXDOMAIN

** server can't find web.svc.cluster.local: NXDOMAIN

** server can't find web.svc.cluster.local: NXDOMAIN

Name:	web.default.svc.cluster.local
Address: 10.244.1.6
Name:	web.default.svc.cluster.local
Address: 10.244.2.7
Name:	web.default.svc.cluster.local
Address: 10.244.2.6

** server can't find web.cluster.local: NXDOMAIN

/ # nslookup web-0.web.default.svc.cluster.local
Server:		10.96.0.10
Address:	10.96.0.10:53


Name:	web-0.web.default.svc.cluster.local
Address: 10.244.2.6
```

- `nslookup web` ได้ **3 Address** = IP ของ `web-0`, `web-1`, `web-2` (ลำดับอาจสลับทุกครั้ง)
- บรรทัด `** server can't find web.cluster.local: NXDOMAIN` **ไม่ใช่ error ของเรา** busybox ลองต่อท้ายชื่อด้วยทุก search domain แล้วพิมพ์ผลที่ไม่เจอปนออกมาด้วย ให้ดูเฉพาะบรรทัด `Name:`/`Address:` ที่ตามหลัง `Name: web.default.svc.cluster.local`
- ชื่อรายตัว `web-0.web.default.svc.cluster.local` ได้ IP เดียวตรงกับ `web-0`

**Pod ที่ไม่ Ready ไม่อยู่ใน DNS** LAB 2 ทำให้ `web-1` ไม่ Ready โดยลบหน้าเว็บ (nginx ตอบ 403 readinessProbe จึงไม่ผ่าน) ผลจริง

```text
  Warning  Unhealthy  1s (x5 over 7s)  kubelet            spec.containers{nginx}: Readiness probe failed: HTTP probe failed with statuscode: 403
```

```text
Name:	web.default.svc.cluster.local
Address: 10.244.2.6
Name:	web.default.svc.cluster.local
Address: 10.244.2.7
...
** server can't find web-1.web.default.svc.cluster.local: NXDOMAIN
```

`nslookup web` เหลือ 2 Address และชื่อ `web-1.web.default.svc.cluster.local` กลายเป็น `NXDOMAIN` ทั้งที่ Pod `web-1` ยัง `Running` อยู่ เพราะ DNS ของ headless Service สร้างจาก endpoint ที่ `conditions.ready=true` เท่านั้น (EndpointSlice ยังมี IP ของ Pod ครบแต่ระบุ `ready=false`) เมื่อเขียนหน้าเว็บคืน Pod กลับมา Ready ใน ~6 วินาทีและกลับเข้า DNS

> **ข้อสังเกตจากการทดลอง (สำคัญ):** ตอน `web-1` ไม่ Ready คำสั่ง `wget -qO- -T 3 web-1.web` (ชื่อสั้น) ได้ `wget: can't connect to remote host (127.0.53.53): Connection refused` แทนที่จะบอกว่า "ไม่พบชื่อ" เพราะเมื่อชื่อใน cluster ไม่มีคำตอบ resolver จะลองชื่อ `web-1.web` ตรง ๆ ซึ่งหลุดออกไปถาม DNS ภายนอก และ **`.web` เป็นโดเมนระดับบนสุด (TLD) ที่มีอยู่จริงบนอินเทอร์เน็ต** ส่วนชื่อเต็ม `web-2.web.default.svc.cluster.local` ได้ `wget: bad address` ตามที่ควรเป็น **เวลาตรวจว่า Pod อยู่ใน DNS หรือไม่ให้ใช้ชื่อเต็มเสมอ**

ถ้าแอปต้องการรู้จักสมาชิกที่ยังไม่ Ready (เช่นระบบ cluster ที่สมาชิกต้องคุยกันก่อนจะ Ready) Service มีฟิลด์ `publishNotReadyAddresses: true` ให้ DNS ใส่ Pod ที่ไม่ Ready ด้วย (แนวคิด — ไม่ได้ใช้ในบทนี้) และ CoreDNS อาจ cache คำตอบ "ไม่พบ" ไว้ช่วงสั้น ๆ Pod ที่เพิ่ง Ready จึงอาจต้องรอไม่กี่วินาทีกว่าชื่อจะ resolve ได้

### 4.4 serviceName และการเปลี่ยน Service เดิมเป็น headless

<p align="center" id="fig-13">
  <img src="images/13-servicename-governs.png" alt="รูปที่ 13 serviceName" width="900"><br>
  <em><b>รูปที่ 13</b> spec.serviceName ต้องชี้ headless Service ที่ selector ตรงกับ Pod — เป็นตัวกำหนดโดเมนของ Pod; ต้องสร้าง Service เอง StatefulSet ไม่สร้างให้</em>
</p>

`spec.serviceName` บอกว่า Pod อยู่ใต้โดเมนของ Service ไหน (governing Service) ข้อควรรู้

1. **StatefulSet ไม่สร้าง Service ให้** เราต้องเขียน headless Service เอง ชื่อตรงกับ `serviceName` และ selector เลือก Pod ของ StatefulSet
2. **ถ้ายังไม่มี Service ก็สร้าง Pod ได้** แต่ไม่มีชื่อ DNS รายตัว LAB 1 ใช้ `web-sts.yaml` ที่มี `serviceName: web` โดยยังไม่สร้าง Service แล้ว Pod `web-0/1/2` ก็ Running ปกติ (Service มาใน LAB 2)
3. **StatefulSet หลายตัวใช้ `serviceName` เดียวกันได้** เช่น `extra/replica.yaml` ของ LAB 10 ใช้ `serviceName: som-db` แต่ label `app: som-db-replica` จึงไม่ถูกนับรวมใน `nslookup som-db` (selector ไม่ตรง)
4. **เปลี่ยน Service ClusterIP ที่มีอยู่เป็น headless ด้วยการ apply ทับไม่ได้** เพราะ `clusterIP` แก้ไขหลังสร้างไม่ได้ ผลจริงจาก LAB 10 ขณะที่ Service `som-db` ของบทที่ 8 (ClusterIP `10.96.99.37`) ยังอยู่

```text
statefulset.apps/som-db created (server dry run)
The Service "som-db" is invalid: spec.clusterIPs[0]: Invalid value: ["None"]: may not change once set
```

ต้อง `kubectl -n som-shop delete svc som-db` ก่อน แล้วจึง apply headless Service ใหม่ (LAB 10 ขั้น B) ผลข้างบนได้จาก `kubectl apply -f k8s/10-db.yaml --dry-run=server` ซึ่งให้ API server ตรวจจริงแต่ไม่บันทึก สังเกตว่าส่วน StatefulSet ผ่าน (`created (server dry run)`) ถ้า apply จริง StatefulSet จะถูกสร้างและสร้าง PVC เปล่า `data-som-db-0` แย่งชื่อไปก่อนที่เราจะย้ายข้อมูลเดิมมา (หัวข้อ 10.3)

> **ข้อควรจำ:** headless Service = `clusterIP: None` + selector ที่ตรงกับ Pod + ชื่อตรงกับ `serviceName` ขาดอย่างใดอย่างหนึ่ง ชื่อ `<pod>.<svc>` จะไม่ทำงาน

---

## 5. volumeClaimTemplates: ตู้เซฟประจำตัว

### 5.1 PVC ต่อ Pod

<p align="center" id="fig-14">
  <img src="images/14-pvc-per-pod.png" alt="รูปที่ 14 PVC ต่อ Pod" width="900"><br>
  <em><b>รูปที่ 14</b> volumeClaimTemplates ชื่อ data → PVC ต่อ Pod ชื่อ data-&lt;sts&gt;-&lt;ลำดับ&gt; เช่น data-som-db-0, data-som-db-1 แต่ละใบได้ PV ของตัวเอง</em>
</p>

`volumeClaimTemplates` คือ **สมุดใบเบิกที่พิมพ์ไว้แล้ว** เมื่อ StatefulSet จะสร้าง Pod ordinal ใด มันจะตรวจว่ามี PVC ชื่อ **`<ชื่อ template>-<ชื่อ Pod>`** = `<template>-<sts>-<ordinal>` หรือยัง ถ้ายังไม่มีก็ "ฉีกใบเบิก" สร้าง PVC ใบใหม่ตาม spec ของแม่แบบ แล้วใส่ volume ที่อ้าง PVC นั้นลงใน Pod ให้เอง จากนั้นทุกอย่างเป็นไปตามบทที่ 8 คือ StorageClass `standard` (local-path, WaitForFirstConsumer) สร้าง PV ให้เมื่อ Pod ถูก schedule

ผลจริงจาก LAB 3 ดูทุก 2 วินาที (PVC เกิดตามลำดับเดียวกับ Pod และ Bound เมื่อ Pod ของตัวเองถูกวางลง Node)

```text
13:51:38 pod: web-0:Pending  pvc: www-web-0:Pending 
13:51:42 pod: web-0:ContainerCreating  pvc: www-web-0:Bound 
13:51:44 pod: web-0:Running web-1:Pending  pvc: www-web-0:Bound www-web-1:Pending 
13:51:47 pod: web-0:Running web-1:Pending  pvc: www-web-0:Bound www-web-1:Bound 
13:51:49 pod: web-0:Running web-1:Running web-2:Pending  pvc: www-web-0:Bound www-web-1:Bound www-web-2:Pending 
13:51:51 pod: web-0:Running web-1:Running web-2:Pending  pvc: www-web-0:Bound www-web-1:Bound www-web-2:Bound 
13:51:53 pod: web-0:Running web-1:Running web-2:Running  pvc: www-web-0:Bound www-web-1:Bound www-web-2:Bound 
```

```text
NAME        STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE   LABELS
www-web-0   Bound    pvc-11a1bc1a-1830-42de-8ddb-aa2974ac48eb   10Mi       RWO            standard       <unset>                 21s   app=web
www-web-1   Bound    pvc-86fad4ec-c326-469b-b8fc-161d70e0196c   10Mi       RWO            standard       <unset>                 16s   app=web
www-web-2   Bound    pvc-60504558-62a2-4cea-a578-8481929cf4ce   10Mi       RWO            standard       <unset>                 12s   app=web
```

- ชื่อ PVC = `www` (ชื่อแม่แบบ) + `-` + `web-0` (ชื่อ Pod) ทุกเครื่องได้ชื่อนี้เหมือนกัน ต่างกันแค่ชื่อ PV `pvc-<uid>`
- PVC ได้ **label `app=web`** ตาม selector ของ StatefulSet จึงเลือกทั้งชุดได้ด้วย `kubectl get pvc -l app=web` และลบทั้งชุดด้วย `kubectl delete pvc -l app=web`
- ไม่มี `storageClassName` ในแม่แบบ จึงใช้ default class `standard` (บทที่ 8)

### 5.2 PVC ติดตามชื่อ Pod

<p align="center" id="fig-15">
  <img src="images/15-sticky-pvc.png" alt="รูปที่ 15 PVC ติดตามชื่อ Pod" width="900"><br>
  <em><b>รูปที่ 15</b> PVC ติดตามชื่อ Pod: Pod web-1 เกิดใหม่กี่ครั้งก็ต่อ www-web-1 เดิม ไฟล์ที่เขียนครั้งแรก (first-born web-1) ยังอยู่</em>
</p>

container ใน `lab03-vct/sts.yaml` เขียน `first-born <hostname> <เวลา>` ลง PVC **เฉพาะครั้งแรก** (มีไฟล์แล้วไม่เขียนทับ) จึงเป็นเครื่องพิสูจน์ว่าตู้เป็นใบเดิมหรือไม่ ผลจริงจาก LAB 3 (เวลาใน container เป็น UTC)

```text
first-born web-0 06:51:43
first-born web-1 06:51:47
first-born web-2 06:51:52
www-web-1
pod "web-1" deleted from default namespace
pod/web-1 condition met
first-born web-1 06:51:47
```

ลบ `web-1` แล้ว Pod ใหม่อ่านได้ `first-born web-1 06:51:47` **เวลาเดิม** และ `claimName` ยังเป็น `www-web-1` ข้อความเดิมนี้ยังอยู่ไปจนจบ LAB 9 ผ่านการ scale, rolling update, ลบ StatefulSet และ Node ล่ม

### 5.3 PVC ไม่หายเมื่อ scale down หรือลบ StatefulSet

<p align="center" id="fig-16">
  <img src="images/16-pvc-survives.png" alt="รูปที่ 16 PVC ไม่หายตาม" width="900"><br>
  <em><b>รูปที่ 16</b> PVC ไม่ถูกลบเมื่อ scale down หรือลบ StatefulSet (ค่า default) — scale กลับหรือ apply ใหม่ Pod ชื่อเดิมกลับมาผูกตู้เดิม</em>
</p>

ค่าเริ่มต้นของ StatefulSet คือ **เก็บตู้ไว้เสมอ** เพื่อความปลอดภัยของข้อมูล

- **scale 3 → 1** (LAB 4–5): `web-2`, `web-1` ถูกลบ แต่ `www-web-1`, `www-web-2` ยัง `Bound` เมื่อ scale กลับเป็น 3 `web-2` อ่านได้ `first-born web-2 06:51:52` เดิม
- **`kubectl delete sts web`** (LAB 8): Pod หายทั้งหมดใน ~2 วินาที PVC 3 ใบยัง `Bound` apply ไฟล์เดิมได้ `service/web unchanged` + `statefulset.apps/web created` และทุก Pod อ่าน `first-born` เวลาเดิมครบ
- **`kubectl delete sts web --cascade=orphan`** (LAB 8): ลบเฉพาะ object StatefulSet ปล่อย Pod ไว้ให้ "กำพร้า" (`ownerReferences=[]`) Pod ที่กำพร้าถ้าถูกลบจะไม่มีใครสร้างคืน และเมื่อ apply StatefulSet ใหม่ มันรับ Pod เดิมกลับมาดูแล (ownerReferences เป็น `StatefulSet/web`) และสร้างตัวที่ขาด

ผลที่ตามมาคือ **ถ้าไม่ใช้ข้อมูลแล้วต้องลบ PVC เอง** ไม่อย่างนั้นทั้ง PVC และ PV ค้างในคลัสเตอร์ และถ้าวันหลัง scale ขึ้นมาใหม่จะได้ข้อมูลเก่าคืนมาโดยไม่ตั้งใจ (LAB 10 ขั้น G scale db กลับเป็น 1 แล้วต้องลบ `data-som-db-1/2` เอง)

### 5.4 persistentVolumeClaimRetentionPolicy

<p align="center" id="fig-17">
  <img src="images/17-retention-policy.png" alt="รูปที่ 17 persistentVolumeClaimRetentionPolicy" width="900"><br>
  <em><b>รูปที่ 17</b> persistentVolumeClaimRetentionPolicy: whenDeleted / whenScaled ค่า default Retain; ตั้ง Delete แล้ว PVC มี ownerReferences ถึง StatefulSet และถูกลบตาม (ทดสอบแล้ว)</em>
</p>

ถ้าต้องการให้ตู้หายตามบูธ (เช่นงานที่ใช้ storage แค่เป็นพื้นที่ทำงานชั่วคราวที่ใหญ่เกิน `emptyDir`) ตั้ง `persistentVolumeClaimRetentionPolicy` ไฟล์จริงจาก `02_LAB/labs/lab05-retention/par.yaml`

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: par
spec:
  serviceName: web
  podManagementPolicy: Parallel
  persistentVolumeClaimRetentionPolicy:
    whenScaled: Delete     # scale ลด → ลบ PVC ของ Pod ที่หายไป
    whenDeleted: Delete    # ลบ StatefulSet → ลบ PVC ทั้งหมด (PVC มี ownerReferences ชี้มาที่ StatefulSet)
  replicas: 3
  selector:
    matchLabels:
      app: par
  template:
    metadata:
      labels:
        app: par
    spec:
      terminationGracePeriodSeconds: 1
      containers:
        - name: c
          image: busybox:1.36
          command: ["sh", "-c", "[ -f /data/born.txt ] || echo \"first-born $(hostname) $(date +%T)\" > /data/born.txt; sleep 3600"]
          volumeMounts:
            - name: www
              mountPath: /data
  volumeClaimTemplates:
    - metadata:
        name: www
      spec:
        accessModes: [ReadWriteOnce]
        resources:
          requests:
            storage: 10Mi
```

ผลจริงจาก LAB 5: PVC ของ `par` มี `ownerReferences` ชี้ไปที่ StatefulSet ส่วน PVC ของ `web` (ค่า default) ไม่มี

```text
[{"apiVersion":"apps/v1","blockOwnerDeletion":true,"controller":true,"kind":"StatefulSet","name":"par","uid":"cd299542-9199-436e-80aa-ed99d44b9a01"}]
ownerReferences ของ www-web-0 = []
```

scale `par` 3 → 1 เหลือ PVC `www-par-0` ใบเดียว และเมื่อ `kubectl delete sts par` PVC ของ `par` หายหมด (`No resources found`) PV ที่เป็นของ `par` เหลือ 0 (PV ถูกลบตามเพราะ class `standard` เป็น `Delete`) กลไกนี้คือ garbage collector ของ Kubernetes ที่ลบ object ลูกเมื่อเจ้าของ (owner) ถูกลบ

**ตารางที่ 9** policy สองชั้นที่มักสับสน

| | `persistentVolumeClaimRetentionPolicy` (บทนี้) | `persistentVolumeReclaimPolicy` (บทที่ 8) |
|---|---|---|
| อยู่ที่ | StatefulSet `spec` | PV `spec` (ได้มาจาก `reclaimPolicy` ของ StorageClass) |
| ตัดสินว่า | เมื่อ scale down / ลบ StatefulSet จะลบ **PVC** หรือไม่ | เมื่อ PVC ถูกลบ จะลบ **PV และข้อมูล** หรือเก็บไว้ (`Released`) |
| ค่า | `whenDeleted`, `whenScaled`: `Retain` (default) / `Delete` | `Delete` / `Retain` |
| ตัวอย่างลำดับเหตุการณ์ | `whenScaled: Delete` → scale 3→1 → ลบ `www-par-1/2` | PVC `www-par-1` ถูกลบ → class `standard` = `Delete` → PV และโฟลเดอร์บน Node ถูกลบ |

> **ข้อควรจำ:** ข้อมูลจะหายจริงก็ต่อเมื่อ **ทั้งสองชั้น** ปล่อยให้ลบ ค่า default ของ StatefulSet (`Retain`) ปกป้องชั้นแรก ส่วนชั้นที่สองขึ้นกับ StorageClass สำหรับข้อมูลสำคัญควรใช้ PV แบบ `Retain` ด้วย (บทที่ 8)

---

## 6. ลำดับการสร้าง/ลบ: podManagementPolicy

### 6.1 OrderedReady (ค่า default)

<p align="center" id="fig-18">
  <img src="images/18-ordered-ready-create.png" alt="รูปที่ 18 OrderedReady" width="900"><br>
  <em><b>รูปที่ 18</b> OrderedReady (default): สร้าง -0 รอจน Ready ก่อนสร้าง -1 แล้ว -2 — ถ้า -0 ไม่ Ready ตัวถัดไปไม่เกิด</em>
</p>

ด้วย `podManagementPolicy: OrderedReady` StatefulSet

- **สร้าง** Pod ทีละตัวจาก ordinal 0 ขึ้นไป ตัวถัดไปจะถูกสร้างเมื่อตัวก่อนหน้าทั้งหมด **Running และ Ready** แล้วเท่านั้น
- **ลบ** (scale down) จาก ordinal มากไปน้อย ทีละตัว
- ถ้า Pod ตัวใดตัวหนึ่งไม่ Ready ระหว่างทาง controller **หยุดรอ** ไม่สร้างหรือลบตัวอื่นต่อ

ผลจริงจาก LAB 4 กับ `lab04-order/bad.yaml` ที่ readinessProbe คือ `cat /tmp/ready` (ไม่มีไฟล์ = ไม่ Ready)

```text
13:52:27 bad-0:0/1:Running 
...
13:52:39 bad-0:0/1:Running 
NAME   READY   AGE
bad    0/3     16s
13:52:41 bad-0:0/1:Running 
13:52:43 bad-0:1/1:Running bad-1:0/1:ContainerCreating 
...
13:52:59 bad-0:1/1:Running bad-1:1/1:Running bad-2:0/1:Running 
```

`bad-0` ค้าง `0/1` นานกว่า 16 วินาที โดยไม่มี `bad-1` เกิดขึ้นเลย พอ `kubectl exec bad-0 -- touch /tmp/ready` ภายใน 2 วินาที `bad-0` เป็น `1/1` และ `bad-1` ถูกสร้างทันที `bad-2` ก็รอแบบเดียวกันจนกว่า `bad-1` จะ Ready นี่คือเหตุผลที่ **readinessProbe ของ StatefulSet ต้องถูกต้อง** ถ้า probe ผิด StatefulSet ทั้งชุดจะค้างที่ตัวแรก

### 6.2 scale down ย้อนลำดับ

<p align="center" id="fig-19">
  <img src="images/19-scale-down-reverse.png" alt="รูปที่ 19 scale down ย้อนลำดับ" width="900"><br>
  <em><b>รูปที่ 19</b> scale down ลบจากเลขมากไปน้อย (-2 ก่อน -1) และรอตัวก่อนหน้าปิดเสร็จ — -0 ถูกลบเป็นตัวสุดท้ายเสมอ</em>
</p>

ผลจริงจาก LAB 4 `kubectl scale sts web --replicas=1` (ดูทุก 2 วินาที)

```text
13:53:38 web-0:Running web-1:Running web-2:Terminating 
13:53:40 web-0:Running web-1:Completed 
13:53:42 web-0:Running 
```

`web-2` ถูกปิดก่อนขณะที่ `web-1` ยัง Running จากนั้นจึงถึงคิว `web-1` ทั้งหมดใช้ราว 4 วินาที (`terminationGracePeriodSeconds: 5`) ordinal 0 จึงเหมาะเป็น "ตัวหลัก" เพราะเกิดก่อนและถูกลบหลังสุดเสมอ

> **หมายเหตุ:** การ **ลบ StatefulSet ทั้งตัว** ไม่รับประกันลำดับการปิด Pod (LAB 8 เห็น `web-0/1/2` เป็น `Terminating` พร้อมกัน) ถ้าต้องการปิดตามลำดับให้ `scale --replicas=0` ก่อนแล้วจึงลบ

### 6.3 Parallel

<p align="center" id="fig-20">
  <img src="images/20-parallel-policy.png" alt="รูปที่ 20 Parallel" width="900"><br>
  <em><b>รูปที่ 20</b> podManagementPolicy: Parallel สร้าง/ลบทุกตัวพร้อมกันไม่รอกัน (ทดสอบแล้ว par-0..2 Pending พร้อมกัน) — ชื่อและตู้ประจำตัวยังเหมือนเดิม</em>
</p>

งานบางชนิดต้องการชื่อคงที่และ storage ประจำตัว แต่ไม่ต้องการลำดับ (เช่น worker ที่ทำงานแยกกันตามเลข) ตั้ง `podManagementPolicy: Parallel` ได้ ผลจริงจาก LAB 4 (`lab04-order/par.yaml`)

```text
13:53:28 par-0:0/1:Pending par-1:0/1:Pending par-2:0/1:Pending 
13:53:29 par-0:1/1:Running par-1:1/1:Running par-2:1/1:Running 
statefulset.apps/par scaled
13:53:34 par-0:Terminating par-1:Terminating par-2:Terminating 
```

ทั้ง 3 ตัวเกิดในวินาทีเดียวกันและถูกปิดพร้อมกันเมื่อ scale เป็น 0 (ตอนลบจะเห็น `Error` ชั่วครู่ เพราะ `sleep` ใน busybox ไม่รับ SIGTERM และถูก kill เมื่อครบ `terminationGracePeriodSeconds: 1` ซึ่งปกติ)

**ตารางที่ 10** OrderedReady กับ Parallel

| | `OrderedReady` (default) | `Parallel` |
|---|---|---|
| สร้าง / scale up | ทีละตัว 0 → N-1 รอ Ready | พร้อมกันทุกตัว |
| scale down | ทีละตัว N-1 → 0 | พร้อมกันทุกตัว |
| Pod ไม่ Ready ระหว่างทาง | หยุดรอ | ไม่รอ |
| ชื่อ / DNS / PVC ประจำตัว | ✅ | ✅ |
| มีผลกับการอัปเดต (rolling update) | ไม่ — การอัปเดตทำตาม `updateStrategy` เสมอ | ไม่ |
| เหมาะกับ | ฐานข้อมูล, cluster ที่ต้องเปิดตัวหลักก่อน | งานที่แต่ละตัวอิสระ ต้องการ scale เร็ว |

---

## 7. การอัปเดต: updateStrategy

### 7.1 RollingUpdate ไล่จากเลขมากไปน้อย

<p align="center" id="fig-21">
  <img src="images/21-rolling-reverse.png" alt="รูปที่ 21 RollingUpdate ไล่จากเลขมาก" width="900"><br>
  <em><b>รูปที่ 21</b> RollingUpdate ของ StatefulSet: เปลี่ยนทีละตัวจากเลขมากไปน้อย (-2 → -1 → -0) รอแต่ละตัว Ready ก่อนไปตัวถัดไป</em>
</p>

เมื่อแก้ `template` (เช่น `kubectl set image` หรือ apply ไฟล์ที่เปลี่ยน image/resources) StatefulSet ที่ใช้ `updateStrategy.type: RollingUpdate` (ค่า default) จะ

1. เลือก Pod ที่ ordinal **มากที่สุด** ที่ยังเป็นรุ่นเก่า
2. **ลบ Pod นั้นก่อน** แล้วสร้าง Pod ชื่อเดิมด้วย template รุ่นใหม่ (ต่างจาก Deployment ที่สร้างตัวใหม่ก่อนลบตัวเก่า) จึงไม่มี Pod ชื่อเดียวกันสองตัวพร้อมกัน
3. รอจน Pod ใหม่ Running และ Ready (และครบ `minReadySeconds` ถ้าตั้งไว้) แล้วจึงไปตัวถัดไป

ผลจริงจาก LAB 6 หลังเอา partition ออก (ดูทุก 2 วินาที รูปแบบ `ชื่อ image ready`)

```text
--- 13:55:38 web-0 nginx:1.27-alpine true web-1 nginx:1.27-alpine true web-2 nginx:1.28-alpine true 
--- 13:55:40 web-0 nginx:1.27-alpine true web-1 nginx:1.28-alpine false web-2 nginx:1.28-alpine true 
--- 13:55:46 web-0 nginx:1.27-alpine false web-1 nginx:1.28-alpine true web-2 nginx:1.28-alpine true 
--- 13:55:48 web-0 nginx:1.28-alpine true web-1 nginx:1.28-alpine true web-2 nginx:1.28-alpine true 
```

`web-1` เปลี่ยนก่อนแล้วจึงถึง `web-0` (`web-2` เปลี่ยนไปแล้วในขั้น partition) ช่วงที่ `web-0 … false` คือ Pod ใหม่ที่ยังไม่ Ready ค่า `maxUnavailable: 1` (default) หมายถึงยอมให้ไม่พร้อมได้ทีละ 1 ตัว ฐานข้อมูล 1 ตัวของร้านน้องส้มจึงมี **ช่วงสั้น ๆ ที่ไม่มี db** เสมอเมื่อ rolling update (LAB 10 ขั้น D ใช้ 2.0 วินาที) แบบเดียวกับ `Recreate` ของบทที่ 8 แต่รับประกันได้ว่าไม่มี `som-db-0` สองตัวเปิดโฟลเดอร์เดียวกัน

### 7.2 partition: เชือกกั้นแถวสำหรับ canary

<p align="center" id="fig-22">
  <img src="images/22-partition-canary.png" alt="รูปที่ 22 partition: canary" width="900"><br>
  <em><b>รูปที่ 22</b> partition: N = อัปเดตเฉพาะ Pod ที่เลข ≥ N ใช้ทำ canary (partition 2 → เฉพาะ web-2 ได้ nginx:1.28-alpine) แล้วลด partition เป็น 0 เพื่อปล่อยทั้งหมด</em>
</p>

`updateStrategy.rollingUpdate.partition: N` ทำหน้าที่เป็น **เชือกกั้นแถวบูธ** เมื่อ template เปลี่ยน เฉพาะ Pod ที่ ordinal **≥ N** เท่านั้นที่ถูกอัปเดต Pod ที่ ordinal < N คงรุ่นเดิม และถ้าถูกลบก็จะถูกสร้างคืนด้วย **รุ่นเดิม** ด้วย ใช้ทำ **canary** (ทดลองรุ่นใหม่กับบางตัวก่อน) หรือ **staged rollout** (ลด partition ทีละขั้น)

ไฟล์ patch จริงจาก `02_LAB/labs/lab06-update/`

```yaml
# LAB 6: เชือกกั้นแถว partition=2 → อัปเดตเฉพาะบูธเลข >= 2 (web-2 เป็น canary) ที่เหลือคงรุ่นเดิม
# ใช้:  kubectl patch sts web --patch-file partition-2.yaml
spec:
  updateStrategy:
    type: RollingUpdate
    rollingUpdate:
      partition: 2
```

```yaml
# LAB 6: เอาเชือกออก partition=0 → อัปเดตบูธที่เหลือต่อ (เลขมากไปน้อย: web-1 แล้ว web-0)
# ใช้:  kubectl patch sts web --patch-file partition-0.yaml
spec:
  updateStrategy:
    rollingUpdate:
      partition: 0
```

ผลจริงจาก LAB 6 หลัง `kubectl patch sts web --patch-file partition-2.yaml` และ `kubectl set image sts/web nginx=nginx:1.28-alpine` (ผลของสคริปต์ `show.sh`)

```text
web-0   nginx:1.27-alpine   web-67f445dc6c   true    2026-10-05T06:51:38Z
web-1   nginx:1.27-alpine   web-67f445dc6c   true    2026-10-05T06:54:22Z
web-2   nginx:1.28-alpine   web-5888c97b8    true    2026-10-05T06:55:14Z
currentRevision=web-67f445dc6c  updateRevision=web-5888c97b8  updated=1/3
partitioned roll out complete: 1 new pods have been updated...
exit=0
```

- เฉพาะ `web-2` เป็น `nginx:1.28-alpine` และ `updated=1/3`
- `currentRevision` (รุ่นที่ Pod ส่วนใหญ่ใช้อยู่) ยังเป็นรุ่นเก่า ส่วน `updateRevision` (รุ่นเป้าหมาย) เป็นรุ่นใหม่
- **`kubectl rollout status` จบทันทีด้วย `partitioned roll out complete: 1 new pods have been updated...`** (exit 0) เพราะสำหรับ StatefulSet ที่มี partition "อัปเดตจนถึงเชือกแล้ว" ถือว่าเสร็จ ไม่ได้แปลว่าอัปเดตครบทุกตัว
- เมื่อ patch `partition-0.yaml` จึงได้ลำดับ `web-1` → `web-0` (หัวข้อ 7.1) และ `partitioned roll out complete: 3 new pods have been updated...`

### 7.3 ControllerRevision, rollout history และ rollout undo

<p align="center" id="fig-23">
  <img src="images/23-revisions.png" alt="รูปที่ 23 ControllerRevision" width="900"><br>
  <em><b>รูปที่ 23</b> StatefulSet เก็บรุ่นเป็น ControllerRevision: status.currentRevision / updateRevision และ label controller-revision-hash บน Pod — ดูด้วย kubectl rollout history sts</em>
</p>

Deployment เก็บรุ่นเป็น ReplicaSet (บทที่ 7) แต่ StatefulSet ไม่มี ReplicaSet จึงเก็บ template แต่ละรุ่นเป็น object ชนิด **ControllerRevision** ชื่อ `<sts>-<hash>` hash เดียวกันนี้คือ label `controller-revision-hash` บน Pod และค่า `status.currentRevision`/`status.updateRevision` ผลจริงจาก LAB 6

```text
statefulset.apps/web 
REVISION  CHANGE-CAUSE
1         <none>
2         <none>
```

`kubectl rollout undo sts/web` ย้อนไปรุ่นก่อนหน้าได้เหมือน Deployment (rolling update แบบไล่ 2 → 1 → 0 เช่นกัน) ผลจริง

```text
Warning: resource statefulsets/web was previously managed with 'kubectl apply'. Rolling back will not update the kubectl.kubernetes.io/last-applied-configuration annotation, which may cause unexpected behavior on future 'kubectl apply' operations. Consider using 'kubectl apply' with your previous configuration file instead.
statefulset.apps/web rolled back
...
statefulset.apps/web 
REVISION  CHANGE-CAUSE
2         <none>
3         <none>

NAME             CONTROLLER             REVISION   AGE
web-5888c97b8    statefulset.apps/web   2          105s
web-67f445dc6c   statefulset.apps/web   3          5m20s
```

- template ของรุ่น 1 (hash `web-67f445dc6c`) ถูกนำกลับมาใช้และ **เลื่อนเป็น REVISION 3** history จึงเหลือ `2, 3` (ไม่มีรุ่นซ้ำสองแถว) เหมือน Deployment ในบทที่ 7
- Warning บอกว่าคลัสเตอร์ไม่ตรงกับไฟล์ที่ apply ล่าสุดแล้ว ถ้า apply ไฟล์เดิมอีกครั้งจะกลับไปตามไฟล์ (ใน LAB 10 ขั้น E apply `k8s/10-db.yaml` ใหม่แล้ว memory limit กลับเป็น 512Mi ตามไฟล์) แนวปฏิบัติคือแก้ไฟล์แล้ว apply แทนการ patch/undo ค้างไว้
- CHANGE-CAUSE เป็น `<none>` เพราะไม่ได้ใส่ annotation `kubernetes.io/change-cause` (ทำแบบบทที่ 7 ได้)

### 7.4 OnDelete

<p align="center" id="fig-24">
  <img src="images/24-ondelete.png" alt="รูปที่ 24 OnDelete" width="900"><br>
  <em><b>รูปที่ 24</b> updateStrategy: OnDelete = แก้ template แล้ว Pod ยังไม่เปลี่ยน จนกว่าจะลบ Pod นั้นเอง — ควบคุมจังหวะได้ละเอียดสำหรับระบบที่ต้องอัปเกรดทีละขั้นด้วยมือ</em>
</p>

`updateStrategy.type: OnDelete` สั่งให้ StatefulSet **ไม่เปลี่ยน Pod เอง** template ใหม่จะถูกใช้เมื่อ Pod ถูกลบ (โดยเราหรือเหตุอื่น) แล้วสร้างใหม่เท่านั้น เป็นพฤติกรรมเดียวของ StatefulSet ใน Kubernetes รุ่นแรก ๆ และยังมีประโยชน์กับระบบที่ต้องอัปเกรดตามขั้นตอนเฉพาะ (เช่นอัปเกรดตัวรองก่อน สลับตัวหลัก แล้วจึงอัปเกรดตัวหลักเดิม) ไฟล์ patch จริง `02_LAB/labs/lab07-ondelete/ondelete.yaml`

```yaml
# LAB 7: OnDelete → StatefulSet ไม่เปลี่ยนรุ่นเอง จะใช้รุ่นใหม่เฉพาะบูธที่เราลบเอง
# ใช้:  kubectl patch sts web --patch-file ondelete.yaml
# (rollingUpdate: null = ลบค่า partition ทิ้ง เพราะใช้ได้เฉพาะ type RollingUpdate)
spec:
  minReadySeconds: 0
  updateStrategy:
    type: OnDelete
    rollingUpdate: null
```

ผลจริงจาก LAB 7 หลัง `kubectl set image sts/web nginx=nginx:1.27-alpine` รอ 10 วินาที ไม่มี Pod ใดเปลี่ยน แล้วลบ `web-1`

```text
currentRevision=web-5888c97b8  updateRevision=web-67f445dc6c  updated=/3
error: rollout status is only available for RollingUpdate strategy type
exit=1
pod "web-1" deleted from default namespace
pod/web-1 condition met
NAME    IMAGE               REVISION         READY   CREATED
web-0   nginx:1.28-alpine   web-5888c97b8    true    2026-10-05T06:57:42Z
web-1   nginx:1.27-alpine   web-67f445dc6c   true    2026-10-05T06:58:46Z
web-2   nginx:1.28-alpine   web-5888c97b8    true    2026-10-05T06:57:20Z
currentRevision=web-5888c97b8  updateRevision=web-67f445dc6c  updated=1/3
first-born web-1 06:51:47
```

- `kubectl rollout status` **ใช้กับ OnDelete ไม่ได้** (`error: rollout status is only available for RollingUpdate strategy type`) ต้องดูเองจาก `updatedReplicas` หรือ label `controller-revision-hash`
- เฉพาะ `web-1` ที่ถูกลบได้รุ่นใหม่ ไฟล์ใน PVC ยังเป็น `first-born web-1 06:51:47` เดิม

### 7.5 minReadySeconds

<p align="center" id="fig-25">
  <img src="images/25-min-ready-seconds.png" alt="รูปที่ 25 minReadySeconds" width="900"><br>
  <em><b>รูปที่ 25</b> minReadySeconds: Pod ต้อง Ready ต่อเนื่องครบกี่วินาทีจึงนับว่า available ก่อนไปตัวถัดไป — ชะลอ rollout ให้เห็นปัญหาทัน</em>
</p>

`spec.minReadySeconds` (มีใน Deployment ตั้งแต่บทที่ 7) ใช้กับ StatefulSet ได้เช่นกัน ผลจริงจาก LAB 7 เมื่อ `kubectl patch sts web --patch-file min-ready.yaml` (`minReadySeconds: 10`) แล้ว `kubectl set image sts/web nginx=nginx:1.28-alpine`

```text
--- 13:57:20 web-0 nginx:1.27-alpine true web-1 nginx:1.27-alpine true web-2 nginx:1.27-alpine true  | sts ready=3 available=3
--- 13:57:22 web-0 nginx:1.27-alpine true web-1 nginx:1.27-alpine true web-2 nginx:1.28-alpine true  | sts ready=3 available=2
...
--- 13:57:32 web-0 nginx:1.27-alpine true web-1 nginx:1.28-alpine true web-2 nginx:1.28-alpine true  | sts ready=3 available=2
...
--- 13:57:42 web-0 nginx:1.28-alpine false web-1 nginx:1.28-alpine true web-2 nginx:1.28-alpine true  | sts ready=2 available=2
...
--- 13:57:53 web-0 nginx:1.28-alpine true web-1 nginx:1.28-alpine true web-2 nginx:1.28-alpine true  | sts ready=3 available=3
```

Pod เปลี่ยนห่างกันราว 10–11 วินาที (13:57:21 → 13:57:32 → 13:57:42) เทียบกับราว 2 วินาทีตอน `rollout undo` ที่ไม่มี `minReadySeconds` และ `available` ค้างที่ 2 ราว 10 วินาทีหลังแต่ละตัว Ready ช่วงหน่วงนี้ทำให้ Pod ที่ Ready แล้วพังในไม่กี่วินาทีถูกจับได้ก่อน rollout ลามไปตัวอื่น การ patch `minReadySeconds` อย่างเดียวไม่ทำให้เกิด rollout เพราะไม่ได้แก้ template

### 7.6 rollout ที่ค้างเพราะ Pod พัง

ถ้า template รุ่นใหม่ทำให้ Pod ไม่เคย Ready (image ผิด, config ผิด) RollingUpdate แบบ OrderedReady จะ **หยุดรอ Pod นั้นไปเรื่อย ๆ** (หัวข้อ 6.1) เอกสาร Kubernetes เรียกสภาพนี้ว่า broken state และระบุว่า **แก้ template กลับอย่างเดียวไม่พอ** StatefulSet จะรอให้ Pod ที่พังนั้น Ready ก่อนจึงจะไปต่อ ขั้นตอนที่ถูกต้อง (forced rollback) คือ

1. แก้ template กลับเป็นรุ่นที่ใช้ได้ (หรือ `kubectl rollout undo sts/<ชื่อ>`)
2. **ลบ Pod ที่พังเองด้วย `kubectl delete pod <ชื่อ>`** StatefulSet จึงสร้างคืนด้วย template ที่แก้แล้ว

(แนวคิดตามเอกสาร — ไม่ได้ทดลองใน LAB ของบทนี้) ข้อนี้เป็นอีกเหตุผลที่ควรใช้ partition ทำ canary ก่อนปล่อยรุ่นใหม่ให้ทุกตัว

**ตารางที่ 11** updateStrategy ของ StatefulSet เทียบ strategy ของ Deployment

| | Deployment `RollingUpdate` | StatefulSet `RollingUpdate` | StatefulSet `OnDelete` |
|---|---|---|---|
| ลำดับ | สุ่ม | ordinal มาก → น้อย | ตามที่เราลบ |
| ตัวใหม่ก่อนหรือตัวเก่าก่อน | ตัวใหม่ก่อน (`maxSurge`) | ลบตัวเก่าก่อน แล้วสร้างชื่อเดิม | – |
| ทำบางส่วน | `rollout pause` | `partition` | ลบเฉพาะตัวที่ต้องการ |
| `rollout status` | ✅ | ✅ (partition จบที่เชือก) | ❌ |
| `rollout history/undo` | ✅ (ReplicaSet) | ✅ (ControllerRevision) | ✅ แต่มีผลเมื่อ Pod ถูกลบ |

---

## 8. replicas หลายตัว ≠ ข้อมูล replicate

### 8.1 scale เป็น 3 = ฐานข้อมูล 3 ก้อนที่แยกกัน

<p align="center" id="fig-26">
  <img src="images/26-independent-ledgers.png" alt="รูปที่ 26 สมุดแยกกัน 3 เล่ม" width="900"><br>
  <em><b>รูปที่ 26</b> scale som-db เป็น 3 ได้ 3 postgres ที่ข้อมูลแยกกัน: som-db-0 มี orders ส่วน som-db-1/2 ว่าง (relation "orders" does not exist) — StatefulSet ไม่คัดลอกข้อมูลให้</em>
</p>

ความเข้าใจผิดที่พบบ่อยที่สุดคือ "scale StatefulSet ของ postgres เป็น 3 แล้วจะได้ฐานข้อมูลที่มีสำเนา 3 ชุด" ผลจริงจาก LAB 10 ขั้น F หลัง `kubectl -n som-shop scale sts som-db --replicas=3`

```text
NAME                                  STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE     VOLUMEMODE
persistentvolumeclaim/data-som-db-0   Bound    pvc-6c88d7af-5c52-48b1-aa08-044104105355   1Gi        RWO            standard       <unset>                 2m55s   Filesystem
persistentvolumeclaim/data-som-db-1   Bound    pvc-c6e96a1b-b00f-4682-afd5-337771842007   1Gi        RWO            standard       <unset>                 17s     Filesystem
persistentvolumeclaim/data-som-db-2   Bound    pvc-1198dfe4-2201-4215-b09d-51eccf132f10   1Gi        RWO            standard       <unset>                 9s      Filesystem
som-db-0: 4
som-db-1: ERROR:  relation "orders" does not exist
som-db-2: ERROR:  relation "orders" does not exist
```

StatefulSet ทำหน้าที่ของมันถูกต้องทุกอย่าง คือได้ Pod ชื่อคงที่ 3 ตัว แต่ละตัวมีตู้ของตัวเอง (`data-som-db-1/2` ใบใหม่ว่างเปล่า) แต่ **ไม่มีอะไรคัดลอกข้อมูลจาก `som-db-0` ไปให้** postgres ตัวใหม่จึงสร้างฐาน `catshop` เปล่า (จาก env `POSTGRES_DB`) ไม่มีตาราง `orders` ร้านยังปกติ (`orders=4`) เพราะ web ต่อ `som-db-0.som-db` ตรง ๆ (หัวข้อ 10.2)

### 8.2 replication ต้องทำระดับแอป

<p align="center" id="fig-27">
  <img src="images/27-streaming-replication.png" alt="รูปที่ 27 streaming replication" width="900"><br>
  <em><b>รูปที่ 27</b> ถ้าต้องการสำเนาจริง แอปต้องทำเอง เช่น postgres streaming replication: replica ใช้ pg_basebackup -R จาก primary แล้วรับ WAL ต่อเนื่อง อ่านได้อย่างเดียว</em>
</p>

การทำสำเนาข้อมูลเป็นความสามารถของ **ซอฟต์แวร์ฐานข้อมูล** StatefulSet ให้แค่ "ชื่อคงที่ + ตู้ประจำตัว" ซึ่งเป็นสิ่งที่ replication ต้องใช้ PostgreSQL มี **streaming replication** ที่ทำงานแบบ **สายพานส่งหน้าสมุด**

1. ฝั่ง primary ต้องอนุญาตการเชื่อมต่อแบบ replication ใน `pg_hba.conf`
2. replica ตัวใหม่โคลนข้อมูลทั้งก้อนจาก primary ด้วย `pg_basebackup` ตัวเลือก `-R` เขียน `standby.signal` และ `primary_conninfo` ให้ เมื่อ postgres เปิดขึ้นมาจึงเป็น **standby** เอง
3. standby รับ WAL (บันทึกการเปลี่ยนแปลง) จาก primary ต่อเนื่อง **อ่านได้แต่เขียนไม่ได้**

LAB 10 เสริมทำตามนี้ด้วย StatefulSet `som-db-replica` (`02_LAB/som-shop-v5/extra/replica.yaml`) ที่มี init container โคลนครั้งแรกเท่านั้น

```yaml
      initContainers:
        # โคลนครั้งแรกเท่านั้น: มี PG_VERSION แล้ว (PVC เดิม) = ข้าม
        - name: clone-from-primary
          image: postgres:17.11-alpine
          env:
            - name: PGPASSWORD
              value: meow1234        # เพื่อการเรียนเท่านั้น
            - name: PGDATA
              value: /var/lib/postgresql/data/pgdata
          # -R = เขียน standby.signal + primary_conninfo ให้ → เปิดมาเป็น standby เอง
          command: ["sh", "-c", "if [ -s $PGDATA/PG_VERSION ]; then echo already-cloned; else pg_basebackup -h som-db-0.som-db -U som -D $PGDATA -R -X stream -P && echo cloned; fi"]
```

(ตัดบางส่วน — ไฟล์จริงมี securityContext และ volumeMounts ด้วย) ผลจริง

```text
waiting for checkpoint
30955/30955 kB (100%), 0/1 tablespace
30955/30955 kB (100%), 1/1 tablespace
cloned
...
t|4
{"ok":true,"order_id":5,"product":{"id":5,"name_th":"ขนมแมวเลียรสไก่ (แพ็ก 4)","stock":39}}
primary: 5  replica: 5
10.244.2.55|streaming|async
ERROR:  cannot execute INSERT in a read-only transaction
```

- `t|4` = `pg_is_in_recovery()` เป็นจริง (เป็น standby) และเห็นออเดอร์ 4 เท่า primary
- สั่งซื้อใหม่ผ่านร้าน replica เห็นทันที (`5 = 5`) และ `pg_stat_replication` ของ primary แสดงการเชื่อมต่อ `streaming` แบบ `async`
- INSERT บน replica ถูกปฏิเสธ (`read-only transaction`)
- สังเกตว่า init container ต่อ primary ด้วยชื่อ **`som-db-0.som-db`** นี่คือเหตุผลที่ระบบ replication ต้องการชื่อ DNS คงที่ของ StatefulSet

### 8.3 Operator: งานที่ StatefulSet ไม่ทำให้

<p align="center" id="fig-28">
  <img src="images/28-operator-concept.png" alt="รูปที่ 28 Operator" width="900"><br>
  <em><b>รูปที่ 28</b> ระบบจริง: failover, สลับ primary, backup อัตโนมัติ ใช้ Operator (controller เฉพาะทางของฐานข้อมูล) ดูแลบน StatefulSet/Pod — บทนี้ปูทางเท่านั้น</em>
</p>

replica ของ LAB 10 ยัง **ไม่ใช่ระบบ high availability** ถ้า `som-db-0` ตาย web ยังเขียนไม่ได้จนกว่า `som-db-0` จะกลับมา (ไม่มีใครเลื่อน replica เป็น primary) ใน LAB เมื่อลบ `som-db-0` replica ทำได้แค่รอแล้วต่อกลับเอง

```text
2026-10-05 07:12:13.644 UTC [43] FATAL:  could not connect to the primary server: could not translate host name "som-db-0.som-db" to address: Name does not resolve
2026-10-05 07:12:13.644 UTC [26] LOG:  waiting for WAL to become available at 0/3000AD0
2026-10-05 07:12:18.636 UTC [51] LOG:  started streaming WAL from primary at 0/3000000 on timeline 1
```

(ระหว่างที่ `som-db-0` ยังไม่ Ready ชื่อของมันไม่อยู่ใน DNS ตามหัวข้อ 4.3) งานอย่าง **failover อัตโนมัติ, สลับ primary, เพิ่ม/ลด replica พร้อมตั้งค่า replication, backup ตามเวลาและ point-in-time recovery, อัปเกรดรุ่นฐานข้อมูลตามขั้นตอน** ต้องการ "ผู้เชี่ยวชาญ" ที่รู้จักฐานข้อมูลนั้น Kubernetes จึงมีรูปแบบ **Operator** คือ controller เฉพาะทาง (มักมาพร้อม CustomResourceDefinition เช่น `kind: Cluster`) ที่เฝ้าดูสถานะแล้วสั่ง StatefulSet/Pod/PVC/Service ให้ถูกต้องตามความรู้ของฐานข้อมูลนั้น ตัวอย่างที่ใช้กันจริงสำหรับ PostgreSQL เช่น CloudNativePG, Zalando Postgres Operator และ Crunchy PGO (แนวคิด — ไม่ได้ใช้ในวิชานี้)

> **ข้อควรจำ:** StatefulSet = **โครงสร้าง** (ชื่อ, DNS, ตู้, ลำดับ) ส่วน replication/failover/backup = **ความรู้ของฐานข้อมูล** ที่ต้องมาจากแอปเองหรือ Operator

---

## 9. StatefulSet กับ Node ล่ม

### 9.1 at most one: ไม่สร้างแทนจนกว่าจะแน่ใจ

<p align="center" id="fig-29">
  <img src="images/29-at-most-one.png" alt="รูปที่ 29 at most one" width="900"><br>
  <em><b>รูปที่ 29</b> Node ล่ม: Pod web-1 ค้าง Terminating (Ready False) ไม่ถูกสร้างใหม่ที่ Node อื่น — StatefulSet ยอมให้มี Pod ชื่อเดียวกันได้ไม่เกิน 1 ตัว (at most one)</em>
</p>

บทที่ 3 และ 8 เห็นแล้วว่าเมื่อ Node หยุดตอบ Node controller จะ

1. ตั้ง Node เป็น `NotReady` และใส่ taint `node.kubernetes.io/unreachable` (NoExecute + NoSchedule)
2. เมื่อครบ `tolerationSeconds` (default 300 วินาที, LAB 9 ตั้งเป็น 30 วินาทีด้วย `sts-tol.yaml`) สั่งลบ Pod บน Node นั้น

สำหรับ Deployment ReplicaSet จะสร้าง Pod ใหม่ชื่อใหม่ทันทีที่ Pod เดิมเริ่มถูกลบ แต่ **StatefulSet ไม่ทำ** เพราะ Pod เดิมยังไม่ถูกลบจริง kubelet บน Node ที่หยุดตอบไม่สามารถยืนยันว่า container ตายแล้ว Pod จึงค้าง `Terminating` และ StatefulSet **ยึดหลัก at most one** คือต้องไม่มี Pod ชื่อเดียวกันสองตัวในเวลาเดียวกัน (ถ้า Node แค่หลุดเครือข่าย container เดิมอาจยังเขียนตู้อยู่) ผลจริงจาก LAB 9 หลัง `docker stop` Node ที่ `web-1` อยู่ (รอบนี้คือ `lab-worker`)

```text
N=lab-worker
14:00:25
lab-worker
stopped 14:00:26
...
--- 14:01:16 lab-worker=NotReady
...
--- 14:01:46 lab-worker=NotReady
web-0 1/1 Running lab-worker2
web-1 1/1 Terminating lab-worker
web-2 1/1 Running lab-worker2
...
--- 14:03:47 lab-worker=NotReady
web-0 1/1 Running lab-worker2
web-1 1/1 Terminating lab-worker
web-2 1/1 Running lab-worker2
deletionTimestamp=2026-10-05T07:01:50Z Ready=False
Taints:             node.kubernetes.io/unreachable:NoExecute
                    node.kubernetes.io/unreachable:NoSchedule
...
NAME   READY   AGE
web    2/3     4m9s
```

- Node เป็น `NotReady` ราว 40–50 วินาทีหลังหยุด และ `web-1` เป็น `Terminating` ราว 80 วินาทีหลังหยุด (ช่อง READY ยังแสดง `1/1` เพราะเป็นค่าล่าสุดที่ kubelet รายงานได้ แต่ condition `Ready=False`)
- **ค้างอย่างนั้นต่อเกิน 3 นาที** ไม่มี `web-1` ตัวใหม่ และ StatefulSet แสดง `2/3`
- ถ้าเป็นฐานข้อมูลตัวหลัก นี่คือช่วงที่ร้านเขียนข้อมูลไม่ได้ ซึ่ง StatefulSet เลือก "หยุดรอ" ดีกว่า "เสี่ยงมีสองตัว"

### 9.2 ความเสี่ยงของ force delete

<p align="center" id="fig-30">
  <img src="images/30-force-delete-danger.png" alt="รูปที่ 30 ความเสี่ยงของ force delete" width="900"><br>
  <em><b>รูปที่ 30</b> force delete (--grace-period=0 --force) เสี่ยง: ถ้า Node แค่หลุดเครือข่ายแต่ Pod ยังทำงาน จะมี som-db-0 สองตัวเขียนข้อมูลพร้อมกัน</em>
</p>

คำสั่ง `kubectl delete pod <ชื่อ> --grace-period=0 --force` ลบ Pod ออกจาก API server **ทันทีโดยไม่รอ kubelet ยืนยัน** StatefulSet จะเห็นว่าชื่อว่างแล้วสร้างตัวใหม่ทันที ถ้า Node ดับจริงก็ไม่เป็นไร แต่ถ้า Node แค่ **หลุดเครือข่าย (network partition)** container เดิมยังรันอยู่และยังเขียน storage ได้ (ถ้า storage เป็นแบบเครือข่ายที่ต่อได้จากทั้งสองที่) ผลคือ `som-db-0` สองตัวเขียนข้อมูลชุดเดียวกัน แบบเดียวกับความเสียหายของบทที่ 8 ขั้น F เอกสาร Kubernetes จึงเตือนให้ force delete Pod ของ StatefulSet เฉพาะเมื่อ **แน่ใจว่า Pod เดิมไม่ทำงานแล้ว** เท่านั้น **LAB ของบทนี้ไม่ใช้ force delete**

### 9.3 out-of-service taint กับ local storage

<p align="center" id="fig-31">
  <img src="images/31-out-of-service-local.png" alt="รูปที่ 31 out-of-service กับ local-path" width="900"><br>
  <em><b>รูปที่ 31</b> ยืนยันว่า Node ดับจริงแล้วใส่ taint node.kubernetes.io/out-of-service → ระบบลบ Pod ให้ แต่ PV ของ local-path ผูก Node เดิม Pod ใหม่จึง Pending จนเรือกลับมา</em>
</p>

วิธีที่ถูกต้องเมื่อผู้ดูแล **ยืนยันแล้วว่า Node ดับจริง** (non-graceful node shutdown) คือใส่ taint `node.kubernetes.io/out-of-service` ให้ Node นั้น เป็นการบอกระบบว่า "รับรองว่า Node นี้ไม่ทำงานแล้ว" ระบบจะลบ Pod ที่ค้างอยู่ (และถอด volume ที่ attach ไว้) ให้ StatefulSet สร้าง Pod ชื่อเดิมได้

```bash
kubectl taint node $N node.kubernetes.io/out-of-service=nodeshutdown:NoExecute
```

ผลจริงจาก LAB 9 ภายในราว 15 วินาที `web-1` ตัวเก่าหายไปและ `web-1` ตัวใหม่ถูกสร้าง แต่ **ค้าง `Pending`**

```text
--- 14:04:26
web-0 1/1 Running 4m23s lab-worker2
web-1 0/1 Pending 2s <none>
web-2 1/1 Running 4m26s lab-worker2
...
  Warning  FailedScheduling  17s (x2 over 17s)  default-scheduler  0/3 nodes are available: 1 node(s) didn't match PersistentVolume's node affinity, 2 node(s) had untolerated taint(s). preemption: 0/3 nodes are available: 3 Preemption is not helpful for scheduling.
...
["lab-worker"]
```

PV ของ `www-web-1` เป็น local-path ซึ่งมี `nodeAffinity` ผูกกับ `lab-worker` (บทที่ 8) จึงไม่มี Node อื่นรับ Pod นี้ได้ (Node ที่เหลือคือ `lab-worker2` ที่ไม่ใช่ Node ของ PV และ `lab-worker` กับ control-plane ที่มี taint) เมื่อเอา taint ออกและ `docker start` Node กลับมา Node `Ready` ใน 2 วินาที `web-1` Ready บน `lab-worker` และอ่านได้ `first-born web-1 06:51:47` เดิม

**ตารางที่ 12** Node ล่ม: Deployment กับ StatefulSet

| | Deployment (บทที่ 8 LAB 8) | StatefulSet (บทนี้ LAB 9) |
|---|---|---|
| Pod บน Node ที่ล่ม | `Terminating` ค้าง | `Terminating` ค้าง |
| สร้าง Pod แทน | ✅ ทันที ชื่อใหม่ | ❌ รอจน Pod เดิมถูกลบจริง (at most one) |
| ทางออกเมื่อยืนยันว่า Node ดับ | – | taint `out-of-service` (หรือ force delete อย่างระวัง) |
| ใช้ local-path | Pod ใหม่ `Pending` (PV node affinity) | Pod ใหม่ `Pending` (PV node affinity) |
| ทำให้ย้าย Node ได้จริง | storage เครือข่าย (CSI) | storage เครือข่าย หรือ **replication ระดับแอป** ที่มี replica บน Node อื่นพร้อมสลับ (Operator) |

> **ข้อควรจำ:** StatefulSet ปกป้องข้อมูลด้วยการ **ไม่เดา** ถ้า Node หายไปเฉย ๆ มันจะรอ เราต้องเป็นคนยืนยัน (out-of-service) และถ้าใช้ local storage ข้อมูลก็ยังรอ Node นั้นอยู่ดี ความทนทานต่อ Node ล่มจริงต้องมาจาก storage ที่ย้าย Node ได้หรือ replication

---

## 10. เปรียบเทียบและแนวปฏิบัติ

### 10.1 Deployment, StatefulSet และ DaemonSet

<p align="center" id="fig-32">
  <img src="images/32-compare-controllers.png" alt="รูปที่ 32 เทียบ controller" width="900"><br>
  <em><b>รูปที่ 32</b> เทียบ Deployment (Pod เหมือนกัน สลับได้) vs StatefulSet (ชื่อ/ตู้ประจำตัว เรียงลำดับ) vs DaemonSet (1 Pod ต่อ Node เช่น agent เก็บ log — แนวคิด)</em>
</p>

**ตารางที่ 13** workload controller สามแบบ

| | Deployment | StatefulSet | DaemonSet (แนวคิด) |
|---|---|---|---|
| คำถามที่ตอบ | "ต้องการ N ตัวที่เหมือนกัน" | "ต้องการ N ตัวที่แต่ละตัวมีตัวตน" | "ต้องการ 1 ตัวต่อทุก Node" |
| ชื่อ Pod | `<deploy>-<hash>-<สุ่ม>` | `<sts>-<ordinal>` | `<ds>-<สุ่ม>` |
| ใครสร้าง Pod | ReplicaSet | StatefulSet โดยตรง | DaemonSet โดยตรง |
| storage ประจำตัว | ❌ (PVC ร่วม) | ✅ `volumeClaimTemplates` | ❌ (มักใช้ hostPath ของ Node) |
| DNS ต่อ Pod | ❌ | ✅ ผ่าน headless Service | ❌ |
| ลำดับ | ไม่มี | OrderedReady (default) | ตาม Node |
| อัปเดต | RollingUpdate (surge) / Recreate | RollingUpdate (ย้อนลำดับ, partition) / OnDelete | RollingUpdate / OnDelete |
| ตัวอย่าง | หน้าร้าน `som-web`, API | `som-db`, etcd, Kafka | agent เก็บ log/metrics, CNI, kube-proxy |

### 10.2 web ควรต่อ db ด้วยชื่อไหน

<p align="center" id="fig-33">
  <img src="images/33-which-name-to-connect.png" alt="รูปที่ 33 web ต่อ db ด้วยชื่อไหน" width="900"><br>
  <em><b>รูปที่ 33</b> web ควรต่อ db ด้วยชื่อไหน: som-db (headless) ตอบ IP ทุกตัว เมื่อ scale เป็น 3 อาจต่อผิดตัว → ระบุ som-db-0.som-db ให้ชี้ primary ชัดเจน</em>
</p>

หลังเปลี่ยน Service `som-db` เป็น headless ชื่อ `som-db` ยังใช้ได้ (LAB 10 ขั้น B: web รุ่นเก่าที่ยังใช้ `som-db` ตอบ `orders=3` ได้ทันที เพราะตอนนั้นมี `som-db-0` ตัวเดียว) แต่เมื่อ scale เป็น 3 `nslookup som-db` ได้ 3 Address

```text
Name:	som-db.som-shop.svc.cluster.local
Address: 10.244.2.50
Name:	som-db.som-shop.svc.cluster.local
Address: 10.244.2.52
Name:	som-db.som-shop.svc.cluster.local
Address: 10.244.1.7
```

แอปที่ต่อ `som-db` อาจได้ `som-db-1` ซึ่งเป็นฐานข้อมูลเปล่า (หัวข้อ 8.1) หรือ replica ที่เขียนไม่ได้ ร้านน้องส้มจึงเปลี่ยน `k8s/20-web.yaml` ให้ต่อ **`som-db-0.som-db`** ทั้งใน `wait-for-db`, `db-seed` และ `web` ผลคือขั้น F `/api/stats` ยังได้ `orders=4` ทุกครั้งแม้มี db 3 ตัว

```yaml
            - name: DATABASE_URL     # เรียก db ด้วยชื่อ DNS รายตัว <pod>.<headless svc> (ไม่ใช่ IP ของ Pod db)
              value: postgres://som:meow1234@som-db-0.som-db:5432/catshop
```

**ตารางที่ 14** เลือกชื่อปลายทาง

| ต้องการ | ใช้ชื่อ | ตัวอย่าง |
|---|---|---|
| เขียนข้อมูล (primary ตัวเดียว) | ชื่อรายตัว | `som-db-0.som-db` |
| อ่านจาก replica ตัวใดตัวหนึ่ง | ชื่อรายตัวของ replica หรือ Service ปกติอีกตัวที่เลือกเฉพาะ replica | `som-db-replica-0.som-db` |
| ค้นหาสมาชิกทั้งหมด (ระบบ cluster) | ชื่อ headless Service | `som-db` |
| ให้ระบบเลือกตัวหลักให้อัตโนมัติ | Service ที่ Operator ดูแล (สลับเมื่อ failover) | (แนวคิด) |

ข้อควรรู้: ชื่อ `som-db-0.som-db` มีใน DNS **เฉพาะตอน Pod Ready** init container `wait-for-db` ของ web จึงวนรอ `pg_isready -h som-db-0.som-db` จนกว่า db พร้อม (ผลจริง `som-db-0.som-db:5432 - accepting connections`)

### 10.3 ย้ายข้อมูลจาก Deployment มาเป็น StatefulSet

<p align="center" id="fig-34">
  <img src="images/34-adopt-existing-pvc.png" alt="รูปที่ 34 ย้ายข้อมูลจาก Deployment" width="900"><br>
  <em><b>รูปที่ 34</b> ย้ายข้อมูลจาก Deployment: ตั้ง PV เป็น Retain → ลบ PVC เดิม → ลบ claimRef → สร้าง PVC ชื่อ data-som-db-0 (volumeName) ไว้ก่อน → StatefulSet ใช้ PVC ชื่อนั้นทันที</em>
</p>

StatefulSet **ใช้ PVC ที่มีอยู่แล้วถ้าชื่อตรง** (`<template>-<sts>-<ordinal>`) โดยไม่สร้างใหม่ เราจึงย้ายตู้เซฟของบทที่ 8 มาได้โดยใช้ความรู้เรื่อง Retain และ static binding จากบทที่ 8

1. `kubectl patch pv $PV -p '{"spec":{"persistentVolumeReclaimPolicy":"Retain"}}'` — กันไม่ให้ PV ถูกลบตอนลบ PVC เดิม
2. ลบ Deployment `som-db`, Service `som-db` (ClusterIP เปลี่ยนเป็น headless ไม่ได้) และ PVC `som-db-data` → PV เป็น `Released`
3. `kubectl patch pv $PV --type json -p '[{"op":"remove","path":"/spec/claimRef"}]'` → PV เป็น `Available`
4. สร้าง PVC ชื่อ **`data-som-db-0`** ที่มี `volumeName: <PV>` และ label `app: som-db` (`migrate/data-som-db-0-pvc.yaml`) → `Bound` กับ PV เดิม
5. apply headless Service + StatefulSet (`k8s/10-db.yaml`) → `som-db-0` ใช้ `data-som-db-0` ที่มีอยู่แล้ว
6. apply web ที่ต่อ `som-db-0.som-db` แล้ว (ทางเลือก) คืน PV เป็น `Delete` หรือคง `Retain` ไว้เป็นแนวปฏิบัติ

ไฟล์จริง `02_LAB/som-shop-v5/migrate/data-som-db-0-pvc.yaml`

```yaml
# LAB 10 ขั้น B: ใบเบิกใหม่ชื่อ "data-som-db-0" ที่ชี้ไปตู้เซฟ (PV) เดิมของบท 008
# ชื่อต้องเป็น <ชื่อ template>-<ชื่อ sts>-<เลข> = data-som-db-0 → StatefulSet จะ "รับไปใช้" แทนการสร้าง PVC ใหม่
# PVNAME จะถูกแทนด้วยชื่อ PV จริงตอนสั่ง:
#   sed "s/PVNAME/$PV/" migrate/data-som-db-0-pvc.yaml | kubectl apply -f -
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: data-som-db-0
  namespace: som-shop
  labels:
    app: som-db                    # label เดียวกับที่ StatefulSet ใส่ให้ PVC ที่สร้างเอง
spec:
  storageClassName: standard       # ต้องตรงกับ PV เดิม
  volumeName: PVNAME               # ผูกกับ PV เดิมโดยตรง (static binding แบบบท 008 LAB 6)
  accessModes: [ReadWriteOnce]
  resources:
    requests:
      storage: 1Gi
```

ผลจริง (LAB 10 ขั้น B): `som-db-0 1/1 Running` ภายใน 1.5 วินาที PV เดิมเป็น `Bound som-shop/data-som-db-0` และร้านได้ `orders=3` เท่าก่อนย้าย สองเงื่อนไขที่ทำให้ใช้ข้อมูลเดิมได้ทันทีคือ **mountPath และ `PGDATA` เหมือนบทที่ 8 ทุกตัวอักษร** (`/var/lib/postgresql/data` และ `…/pgdata`) และ **สร้าง PVC ก่อน apply StatefulSet** ถ้าสลับลำดับ StatefulSet จะสร้าง PVC `data-som-db-0` เปล่าจากแม่แบบไปก่อน

### 10.4 แนวปฏิบัติสำหรับฐานข้อมูลบน StatefulSet

<p align="center" id="fig-35">
  <img src="images/35-best-practices.png" alt="รูปที่ 35 แนวปฏิบัติ" width="900"><br>
  <em><b>รูปที่ 35</b> แนวปฏิบัติ: readinessProbe ที่ถูกต้อง, resources, PV Retain สำหรับข้อมูลสำคัญ, backup นอกคลัสเตอร์, ไม่ force delete, กระจาย Pod ข้าม Node และใช้ Operator สำหรับ HA</em>
</p>

**ตารางที่ 15** เช็กลิสต์ฐานข้อมูลบน Kubernetes

| แนวปฏิบัติ | เหตุผล | ในบทนี้ |
|---|---|---|
| readinessProbe ที่สะท้อนความพร้อมจริง | OrderedReady และ DNS รายตัวขึ้นกับ Ready (probe ผิด = ค้างทั้งชุด) | `pg_isready -h 127.0.0.1` |
| ตั้ง `resources` requests/limits | db ไม่ควรถูกแย่งหน่วยความจำหรือถูก OOMKill กลางทาง | `256Mi`/`512Mi` (ขั้น D ลองปรับเป็น `768Mi`) |
| PV แบบ `Retain` สำหรับข้อมูลสำคัญ | ลบ PVC พลาดแล้วยังกู้ได้ (บทที่ 8) | ใช้ระหว่างย้ายข้อมูล (ขั้น B) |
| **backup นอกคลัสเตอร์** | PV และ replica ไม่ใช่ backup (ลบผิด/ข้อมูลเสียถูกคัดลอกตาม) | แนวคิด (`pg_dump`, VolumeSnapshot) |
| ไม่ force delete Pod ของ db | อาจมีตัวหลักสองตัว (หัวข้อ 9.2) | ใช้ out-of-service เมื่อยืนยันว่า Node ดับ |
| กระจาย Pod คนละ Node | Node เดียวล่มไม่ควรพาทุกสำเนาไปด้วย | แนวคิด (pod anti-affinity, topology spread — บทที่ 3) |
| PodDisruptionBudget | กันการ drain Node ทำให้ db หายพร้อมกันหลายตัว | แนวคิด |
| ใช้ Operator สำหรับ HA | failover, backup, upgrade ต้องใช้ความรู้เฉพาะ | แนวคิด (หัวข้อ 8.3) |
| ไม่เก็บรหัสผ่านใน YAML | ไฟล์ YAML ถูกแชร์ใน git | ยังใช้ `meow1234` → ConfigMap/Secret บทหลัง |

---

## 11. สรุปและบทถัดไป

### 11.1 ตารางสรุป

<p align="center" id="fig-36">
  <img src="images/36-summary-table.png" alt="รูปที่ 36 ตารางสรุป" width="900"><br>
  <em><b>รูปที่ 36</b> ตารางสรุป StatefulSet: ชื่อ, DNS, PVC, ลำดับ, การอัปเดต, การลบ — เทียบกับ Deployment</em>
</p>

**ตารางที่ 16** StatefulSet เทียบ Deployment

| เรื่อง | Deployment | StatefulSet | หลักฐานในบทนี้ |
|---|---|---|---|
| ชื่อ Pod | สุ่ม | `<sts>-<ordinal>` คงที่ | LAB 1 |
| DNS | ผ่าน Service ClusterIP ตัวเดียว | `<pod>.<headless svc>` ต่อ Pod | LAB 2 |
| PVC | ใบเดียวร่วมกัน | 1 ใบต่อ Pod `<template>-<pod>` | LAB 3 |
| ลำดับสร้าง/ลบ | พร้อมกัน | 0 → N-1 / N-1 → 0 (Parallel ได้) | LAB 4 |
| PVC เมื่อ scale down / ลบ | – | เก็บไว้ (default Retain) | LAB 5, 8 |
| การอัปเดต | ตัวใหม่ก่อน (surge) | ลบตัวเก่าก่อน ไล่ N-1 → 0, partition, OnDelete | LAB 6–7 |
| Node ล่ม | สร้างแทนทันที | at most one: รอจนยืนยัน | LAB 9 |
| replication | ไม่มี | ไม่มี (ต้องทำระดับแอป) | LAB 10 ขั้น F, H |

### 11.2 สรุปบท

1. **Deployment = ชามกระดาษ** template เดียว ชื่อสุ่ม ตัวใหม่ก่อนตัวเก่า เหมาะกับ web แต่ไม่เหมาะกับ db หลายตัว
2. **StatefulSet รับประกัน** ชื่อ `<sts>-<ordinal>` (hostname = ชื่อ Pod), DNS `<pod>.<svc>.<ns>.svc.cluster.local` และ PVC ประจำตัว ลบ Pod แล้วชื่อและ PVC เดิม UID/IP ใหม่
3. **headless Service** (`clusterIP: None`) ต้องสร้างเอง ชื่อตรง `serviceName` DNS ตอบเฉพาะ Pod ที่ Ready เปลี่ยน ClusterIP เดิมเป็น headless ไม่ได้ (`spec.clusterIPs[0]: Invalid value: ["None"]: may not change once set`)
4. **volumeClaimTemplates** ได้ PVC `<template>-<sts>-<ordinal>` พร้อม label ตาม selector PVC ไม่หายเมื่อ scale down/ลบ StatefulSet เว้นแต่ตั้ง `persistentVolumeClaimRetentionPolicy: Delete` (PVC จะมี ownerReferences)
5. **OrderedReady** สร้างทีละตัวรอ Ready ลบจากเลขมาก **Parallel** ทำพร้อมกัน
6. **RollingUpdate** ไล่ N-1 → 0 ลบก่อนสร้าง **partition** ทำ canary (`rollout status` จบที่เชือก) **OnDelete** ใช้รุ่นใหม่เมื่อลบ Pod (`rollout status` ใช้ไม่ได้) **minReadySeconds** หน่วงแต่ละตัว รุ่นเก็บเป็น **ControllerRevision** ใช้ `rollout history/undo` ได้
7. **replicas ≠ replication** scale เป็น 3 ได้ db เปล่า 2 ตัว สำเนาจริงต้องใช้ความสามารถของฐานข้อมูล (streaming replication) และ HA ต้องใช้ Operator
8. **Node ล่ม** StatefulSet ไม่สร้างแทน (at most one) อย่า force delete ใช้ taint `out-of-service` เมื่อยืนยันว่า Node ดับ แต่ local-path ยังผูก Node
9. **web ต่อ primary ด้วยชื่อรายตัว** `som-db-0.som-db` และย้ายข้อมูลเดิมได้ด้วยการสร้าง PVC ชื่อ `data-som-db-0` ที่ชี้ PV เดิมไว้ก่อน

<p align="center" id="fig-37">
  <img src="images/37-command-cheatsheet.png" alt="รูปที่ 37 คำสั่งประจำบท" width="900"><br>
  <em><b>รูปที่ 37</b> คำสั่งประจำบท: kubectl get sts,pod,pvc / rollout status sts / patch partition / scale sts / nslookup &lt;pod&gt;.&lt;svc&gt;</em>
</p>

**ตารางที่ 17** คำสั่งที่ใช้ในบทนี้

| คำสั่ง | ใช้ทำอะไร |
|---|---|
| `kubectl get sts,pod,pvc -l app=<label> -o wide` | ดู StatefulSet, Pod และ PVC ประจำตัวพร้อม Node |
| `kubectl get pod <pod> --show-labels` | ดู label อัตโนมัติ (`pod-index`, `pod-name`, `controller-revision-hash`) |
| `kubectl rollout status sts/<ชื่อ>` | รอ rollout (ใช้กับ RollingUpdate เท่านั้น) |
| `kubectl rollout history sts/<ชื่อ>` / `kubectl rollout undo sts/<ชื่อ>` | ดูรุ่นและย้อนรุ่น |
| `kubectl patch sts <ชื่อ> --patch-file <ไฟล์>` | เปลี่ยน partition / OnDelete / minReadySeconds |
| `kubectl set image sts/<ชื่อ> <container>=<image>` | เปลี่ยน image |
| `kubectl get sts <ชื่อ> -o jsonpath='{.status.currentRevision} {.status.updateRevision} {.status.updatedReplicas}'` | ดูความคืบหน้าของ rollout |
| `kubectl scale sts <ชื่อ> --replicas=<N>` | เพิ่ม/ลดจำนวน (PVC ไม่หาย) |
| `kubectl delete sts <ชื่อ>` / `--cascade=orphan` | ลบ StatefulSet (PVC ยังอยู่) / ลบแต่เก็บ Pod |
| `kubectl delete pvc -l app=<label>` | ลบตู้ทั้งชุดเมื่อไม่ใช้แล้ว |
| `kubectl run dns --image=busybox:1.36 --rm -it --restart=Never -- sh` แล้ว `nslookup <pod>.<svc>.<ns>.svc.cluster.local` | ตรวจ DNS ของ headless Service |
| `kubectl taint node <node> node.kubernetes.io/out-of-service=nodeshutdown:NoExecute` | ยืนยันว่า Node ดับจริง (เอาออกด้วย `kubectl taint node <node> node.kubernetes.io/out-of-service-`) |

### 11.3 ปัญหาที่ยังเหลือและบทถัดไป

<p align="center" id="fig-38">
  <img src="images/38-next-chapters.png" alt="รูปที่ 38 ปิดบทและบทถัดไป" width="900"><br>
  <em><b>รูปที่ 38</b> ปิดบท: รหัสผ่าน db ยังเขียนตรงใน YAML → ConfigMap/Secret, เปิดร้านด้วย NodePort → Ingress, ปรับจำนวน web อัตโนมัติ → HPA</em>
</p>

ตอนจบ LAB 10 ครัวกลางของน้องส้มเป็น StatefulSet ที่มี **ชื่อคงที่ (`som-db-0`), ที่อยู่คงที่ (`som-db-0.som-db`) และตู้เซฟประจำตัว (`data-som-db-0`)** ใช้ข้อมูลเดิมจากบทที่ 8 ลบ Pod หรือลบ StatefulSet แล้วออเดอร์ไม่หาย และเห็นแล้วว่าการมีสำเนาจริงต้องทำอย่างไร แต่ร้านยังมีเรื่องที่ต้องทำต่อ

**ตารางที่ 18** ปัญหาที่ยังเหลือ

| ปัญหาที่ยังเหลือ | หลักฐานจากบทนี้ | แก้ด้วย |
|---|---|---|
| **รหัสผ่านฐานข้อมูลอยู่ใน YAML** ทุกไฟล์ (`POSTGRES_PASSWORD`, `DATABASE_URL`, `PGPASSWORD`) | `meow1234` อยู่ใน `k8s/10-db.yaml`, `k8s/20-web.yaml`, `extra/replica.yaml` และ `pg_hba.conf` ต้องแก้ด้วย `kubectl exec` | **ConfigMap/Secret** (บทถัดไป) แยกค่าตั้งและความลับออกจาก manifest |
| **เปิดร้านด้วยเลขพอร์ต** `http://localhost:30080` | Service NodePort 30080 จองพอร์ตได้ทีละ Service ทั้งคลัสเตอร์ | **Ingress** เปิดร้านด้วยชื่อโดเมนและ path หลายร้านใช้ทางเข้าเดียว |
| **web ต้อง scale เอง** | `som-web` ตั้ง `replicas: 3` ตายตัว | **HorizontalPodAutoscaler (HPA)** ปรับจำนวน Pod ตาม CPU/หน่วยความจำ (ต้องมี metrics-server) |
| **replicate ฐานข้อมูลจริงจัง** (failover, backup, เพิ่ม replica อัตโนมัติ) | replica ของ LAB 10 ต้องแก้ `pg_hba.conf` เอง และไม่สลับเป็น primary เมื่อ `som-db-0` ตาย | **Operator** ของฐานข้อมูล (เช่น CloudNativePG) — แนวคิดต่อยอด |
| ข้อมูลผูก Node (local-path) | LAB 9: Pod ใหม่ `Pending` จน Node กลับ | storage เครือข่าย (CSI) หรือ replication ข้าม Node |

> **ปูทางบทหน้า:** ร้านมีครัวกลางแบบโปรดักชันแล้ว เรื่องที่ "แตะ" ทุกไฟล์ของร้านคือรหัสผ่าน `meow1234` บทถัดไปจะย้ายค่าตั้งและความลับออกจาก YAML ด้วย **ConfigMap และ Secret** ก่อนจะเปิดร้านด้วยชื่อโดเมนผ่าน **Ingress** และให้หน้าร้านปรับขนาดเองด้วย **HPA**

---

## 12. คำถามทบทวน

**1. Deployment + PVC ของบทที่ 8 มีจุดอ่อนอะไรบ้างเมื่อต้องการฐานข้อมูลหลายตัว อธิบายอย่างน้อย 3 ข้อ**

<details>
<summary>แนวคำตอบ</summary>

(1) Deployment มี Pod template เดียว ทุก Pod จึงอ้าง `claimName` เดียวกัน scale เป็น 2 แล้ว postgres สองตัวเปิดโฟลเดอร์เดียวกัน ข้อมูลเสีย (บทที่ 8: ออเดอร์ 6 → 3, `lock file is invalid`, บางครั้ง `PANIC`) (2) ชื่อ Pod สุ่ม (`som-db-7b786655f5-bdsgq`) เปลี่ยนทุกครั้งที่ถูกสร้างใหม่ จึงไม่มีชื่อคงที่ให้ replica หรือแอปอ้างถึง "ตัวหลัก" (3) RollingUpdate สร้างตัวใหม่ก่อนลบตัวเก่า ทำให้มีสองตัวพร้อมกัน ต้องใช้ `Recreate` แทน (4) ไม่มีลำดับการเปิด/ปิด
</details>

**2. StatefulSet `web` มี `replicas: 3` ใน namespace `default` ใช้ headless Service `web` และ `volumeClaimTemplates` ชื่อ `www` จงบอกชื่อ Pod, hostname ของ Pod ตัวที่สอง, ชื่อ DNS เต็มของ Pod ตัวแรก และชื่อ PVC ของ Pod ตัวสุดท้าย**

<details>
<summary>แนวคำตอบ</summary>

Pod: `web-0`, `web-1`, `web-2` / hostname ของ Pod ตัวที่สองคือ `web-1` (hostname = ชื่อ Pod) / DNS เต็มของ Pod ตัวแรก: `web-0.web.default.svc.cluster.local` / PVC ของ Pod ตัวสุดท้าย: `www-web-2` (`<template>-<sts>-<ordinal>`)
</details>

**3. ลบ Pod `som-db-0` แล้ว อะไรคงเดิม อะไรเปลี่ยน และทำไมแอปจึงต้องต่อฐานข้อมูลด้วยชื่อ DNS ไม่ใช่ IP**

<details>
<summary>แนวคำตอบ</summary>

คงเดิม: ชื่อ `som-db-0`, hostname, ชื่อ DNS `som-db-0.som-db` และ PVC `data-som-db-0` (ข้อมูลเดิม) เปลี่ยน: UID (`ea0d5d48…` → `acfc1cf3…`) และ IP (`10.244.2.45` → `10.244.2.48`) และ Node อาจเปลี่ยนได้ถ้า storage ไม่ผูก Node เนื่องจาก IP เปลี่ยนทุกครั้งที่ Pod เกิดใหม่ แอปจึงต้องใช้ชื่อ DNS ที่ระบบอัปเดตให้ชี้ IP ใหม่อัตโนมัติ
</details>

**4. headless Service ต่างจาก Service ClusterIP อย่างไร และทำไม StatefulSet จึงต้องใช้ headless Service**

<details>
<summary>แนวคำตอบ</summary>

headless Service ตั้ง `clusterIP: None` ไม่มี IP กลางและ kube-proxy ไม่กระจาย connection DNS ของชื่อ Service ตอบ IP ของทุก Pod ที่ Ready โดยตรง และเมื่อเป็น `serviceName` ของ StatefulSet แต่ละ Pod ได้ชื่อ `<pod>.<svc>` StatefulSet ต้องใช้เพราะงาน stateful ต้องต่อ Pod รายตัว (เช่น replica ต่อ primary `som-db-0.som-db`) ซึ่ง Service ClusterIP ที่สุ่มปลายทางทำไม่ได้
</details>

**5. ใน LAB 2 ทำให้ `web-1` ไม่ Ready แล้ว `nslookup web` เหลือกี่ Address และ `wget web-1.web` (ชื่อสั้น) ได้ผลแปลก ๆ อย่างไร เพราะอะไร ควรตรวจด้วยชื่อแบบไหน**

<details>
<summary>แนวคำตอบ</summary>

เหลือ 2 Address และ `nslookup web-1.web.default.svc.cluster.local` ได้ `NXDOMAIN` เพราะ DNS ของ headless Service ใส่เฉพาะ endpoint ที่ ready ส่วน `wget -qO- -T 3 web-1.web` ได้ `can't connect to remote host (127.0.53.53): Connection refused` เพราะเมื่อไม่พบชื่อในคลัสเตอร์ resolver ลองชื่อ `web-1.web` ตรง ๆ ซึ่งหลุดไปถาม DNS ภายนอก และ `.web` เป็น TLD จริง จึงควรตรวจด้วยชื่อเต็ม `web-1.web.default.svc.cluster.local` (ชื่อเต็มของ Pod ที่ไม่ Ready ได้ `bad address`)
</details>

**6. ทำไม `kubectl apply -f k8s/10-db.yaml` ในขณะที่ Service `som-db` ของบทที่ 8 ยังอยู่จึงล้มเหลว ควรตรวจล่วงหน้าอย่างไร และถ้า apply จริงไปแล้วจะเกิดปัญหาอะไรกับการย้ายข้อมูล**

<details>
<summary>แนวคำตอบ</summary>

Service เดิมเป็น ClusterIP (`10.96.99.37`) และ `clusterIP` แก้ไขหลังสร้างไม่ได้ จึงได้ `The Service "som-db" is invalid: spec.clusterIPs[0]: Invalid value: ["None"]: may not change once set` ตรวจล่วงหน้าได้ด้วย `kubectl apply -f k8s/10-db.yaml --dry-run=server` ซึ่งให้ API server ตรวจจริงโดยไม่บันทึก ถ้า apply จริง ส่วน StatefulSet ผ่าน (`statefulset.apps/som-db created`) แล้วจะสร้าง PVC `data-som-db-0` เปล่าจากแม่แบบแย่งชื่อไปก่อน ต้องลบ StatefulSet และ PVC เปล่านั้นก่อนย้ายข้อมูลใหม่
</details>

**7. scale StatefulSet `web` จาก 3 เป็น 1 แล้วกลับเป็น 3 ไฟล์ `first-born web-2 …` ยังอยู่หรือไม่ เพราะอะไร ถ้าต้องการให้ตู้หายตามต้องตั้งค่าอะไร และ PVC จะมีอะไรเพิ่มขึ้น**

<details>
<summary>แนวคำตอบ</summary>

ยังอยู่ (LAB 5 อ่านได้ `first-born web-2 06:51:52` เดิม) เพราะค่า default `persistentVolumeClaimRetentionPolicy` คือ `whenScaled: Retain` PVC `www-web-2` จึงไม่ถูกลบตอน scale down และ Pod `web-2` ตัวใหม่กลับมาใช้ใบเดิม ถ้าต้องการให้หายตามตั้ง `whenScaled: Delete` (และ `whenDeleted: Delete` สำหรับตอนลบ StatefulSet) PVC จะมี `ownerReferences` ชี้ไปที่ StatefulSet (`kind: StatefulSet`, `controller: true`) ให้ garbage collector ลบตาม
</details>

**8. `persistentVolumeClaimRetentionPolicy` กับ `persistentVolumeReclaimPolicy` ต่างกันอย่างไร ยกตัวอย่างลำดับเหตุการณ์ที่ทำให้ข้อมูลหายจริง**

<details>
<summary>แนวคำตอบ</summary>

ตัวแรกอยู่ที่ StatefulSet ตัดสินว่าจะลบ **PVC** เมื่อ scale down/ลบ StatefulSet หรือไม่ ตัวหลังอยู่ที่ PV ตัดสินว่าจะลบ **PV และข้อมูล** เมื่อ PVC ถูกลบหรือไม่ ตัวอย่าง: StatefulSet `par` ตั้ง `whenScaled: Delete` → scale 3 → 1 → StatefulSet ลบ PVC `www-par-1/2` → PV จาก class `standard` เป็น `Delete` → PV และโฟลเดอร์บน Node ถูกลบ ข้อมูลหายจริง ถ้า PV เป็น `Retain` จะเหลือ `Released` ให้กู้ได้
</details>

**9. StatefulSet `bad` ใน LAB 4 ค้างอยู่ที่ `bad-0 0/1` และไม่มี `bad-1` เพราะอะไร ถ้าเปลี่ยนเป็น `podManagementPolicy: Parallel` คาดว่าจะเห็นอะไร และ Parallel มีผลกับ rolling update หรือไม่**

<details>
<summary>แนวคำตอบ</summary>

ค่า default `OrderedReady` สร้าง Pod ตัวถัดไปเมื่อตัวก่อนหน้า Ready เท่านั้น `bad-0` ไม่ Ready เพราะ readinessProbe `cat /tmp/ready` ไม่ผ่าน (ไม่มีไฟล์) จึงไม่มี `bad-1` จนกว่าจะ `touch /tmp/ready` ถ้าใช้ Parallel ทั้ง 3 ตัวจะถูกสร้างพร้อมกันและอยู่ที่ `0/1` ทั้งหมด (เทียบ `par-0/1/2 Pending` ในวินาทีเดียวกัน) Parallel มีผลเฉพาะการสร้าง/ลบ (scale) ไม่มีผลกับลำดับของ rolling update
</details>

**10. อธิบายการทำ canary ด้วย partition ใน LAB 6 ตั้งแต่ตั้ง partition จนปล่อยครบ และอธิบายว่าทำไม `kubectl rollout status` จึงตอบ `partitioned roll out complete: 1 new pods have been updated...` ทั้งที่อัปเดตไปตัวเดียว**

<details>
<summary>แนวคำตอบ</summary>

(1) `kubectl patch sts web --patch-file partition-2.yaml` (2) `kubectl set image sts/web nginx=nginx:1.28-alpine` → เฉพาะ `web-2` (ordinal ≥ 2) เปลี่ยน, `updated=1/3`, `currentRevision` ≠ `updateRevision` (3) ตรวจ canary แล้ว `kubectl patch sts web --patch-file partition-0.yaml` → `web-1` แล้ว `web-0` เปลี่ยนตามลำดับ `updated=3/3` `rollout status` ถือว่า rollout เสร็จเมื่ออัปเดตครบทุก Pod ที่อยู่หลังเชือก (ordinal ≥ partition) จึงจบทันทีด้วย exit 0
</details>

**11. `kubectl rollout undo sts/web` ใน LAB 6 ทำให้ history เปลี่ยนจาก `1, 2` เป็น `2, 3` และมี Warning เรื่อง last-applied-configuration อธิบายทั้งสองเรื่อง**

<details>
<summary>แนวคำตอบ</summary>

StatefulSet เก็บรุ่นเป็น ControllerRevision การ undo นำ template ของรุ่น 1 (hash `web-67f445dc6c`) กลับมาใช้และเลื่อนเลขเป็น REVISION 3 (ไม่เก็บรุ่นซ้ำ) history จึงเหลือ `2, 3` Warning บอกว่าวัตถุถูกจัดการด้วย `kubectl apply` แต่ undo ไม่ได้แก้ annotation `last-applied-configuration` ค่าในคลัสเตอร์จึงต่างจากไฟล์ ถ้า apply ไฟล์เดิมอีกครั้งจะเปลี่ยนตามไฟล์ แนวปฏิบัติคือแก้ไฟล์แล้ว apply
</details>

**12. OnDelete ต่างจาก RollingUpdate อย่างไร คำสั่งใดใช้กับ OnDelete ไม่ได้ และจะรู้ได้อย่างไรว่า Pod ไหนเป็นรุ่นใหม่แล้ว**

<details>
<summary>แนวคำตอบ</summary>

OnDelete ไม่เปลี่ยน Pod เองเมื่อ template เปลี่ยน Pod จะได้รุ่นใหม่เมื่อถูกลบแล้วสร้างใหม่เท่านั้น (LAB 7 ลบ `web-1` แล้วได้ `nginx:1.27-alpine` ตัวเดียว `updated=1/3`) `kubectl rollout status` ใช้ไม่ได้ (`error: rollout status is only available for RollingUpdate strategy type`) ดูได้จาก label `controller-revision-hash` ของ Pod เทียบกับ `status.updateRevision` และ `status.updatedReplicas` (สคริปต์ `show.sh`)
</details>

**13. `minReadySeconds: 10` ทำให้ rolling update ใน LAB 7 ต่างจาก LAB 6 อย่างไร และมีประโยชน์อย่างไร**

<details>
<summary>แนวคำตอบ</summary>

แต่ละ Pod ต้อง Ready ต่อเนื่อง 10 วินาทีจึงนับเป็น available ก่อนไปตัวถัดไป Pod จึงเปลี่ยนห่างกันราว 10–11 วินาที (13:57:21 → 13:57:32 → 13:57:42) เทียบราว 2 วินาทีเมื่อไม่ตั้ง และ `available` ค้างที่ 2 ช่วงนั้น ช่วยให้จับ Pod ที่ Ready แล้วพังในไม่กี่วินาทีได้ก่อน rollout ลามไปทุกตัว
</details>

**14. scale `som-db` เป็น 3 แล้ว `som-db-1` ตอบ `ERROR:  relation "orders" does not exist` แปลว่า StatefulSet ทำงานผิดหรือไม่ ถ้าต้องการสำเนาจริงต้องทำอย่างไร**

<details>
<summary>แนวคำตอบ</summary>

ไม่ผิด StatefulSet ให้ชื่อคงที่และ PVC ใหม่ประจำตัว (`data-som-db-1`) แต่ไม่คัดลอกข้อมูล postgres ตัวใหม่จึงเป็นฐานข้อมูลเปล่า การทำสำเนาต้องใช้ความสามารถของฐานข้อมูล เช่น postgres streaming replication: อนุญาต replication ใน `pg_hba.conf` ของ primary แล้วให้ replica โคลนด้วย `pg_basebackup -R` (LAB 10 เสริม ได้ `pg_is_in_recovery = t` และ `streaming|async`) สำหรับ failover/backup อัตโนมัติใช้ Operator
</details>

**15. replica ใน LAB 10 เสริมถือว่าเป็นระบบ high availability หรือไม่ ใช้หลักฐานจากการทดลองประกอบ**

<details>
<summary>แนวคำตอบ</summary>

ไม่ replica อ่านได้อย่างเดียว (`ERROR:  cannot execute INSERT in a read-only transaction`) และเมื่อลบ `som-db-0` replica ได้แค่รอ (`could not translate host name "som-db-0.som-db" to address`) แล้วต่อกลับเองเมื่อ primary กลับมา (`started streaming WAL from primary`) ไม่มีการเลื่อน replica เป็น primary ระหว่างนั้น web เขียนข้อมูลไม่ได้ ต้องใช้ Operator หรือระบบ failover เพิ่ม
</details>

**16. ใน LAB 9 เมื่อหยุด Node ที่ `web-1` อยู่ เกิดอะไรขึ้นตามลำดับ ทำไม StatefulSet ไม่สร้าง `web-1` ใหม่บน Node อื่น และ taint `out-of-service` ช่วยได้แค่ไหน**

<details>
<summary>แนวคำตอบ</summary>

Node เป็น `NotReady` ราว 40–50 วินาทีหลังหยุด, `web-1` เป็น `Terminating` ราว 80 วินาที (tolerationSeconds 30) แล้วค้างเกิน 3 นาที StatefulSet ไม่สร้างใหม่เพราะ Pod เดิมยังไม่ถูกลบจริง (kubelet ยืนยันไม่ได้) และต้องไม่มี Pod ชื่อเดียวกันสองตัว (at most one) เมื่อใส่ taint `node.kubernetes.io/out-of-service=nodeshutdown:NoExecute` ระบบลบ Pod เดิมให้และสร้าง `web-1` ใหม่ แต่ค้าง `Pending` เพราะ PV ของ local-path ผูก `lab-worker` (`didn't match PersistentVolume's node affinity`) ต้องรอ Node กลับมา
</details>

**17. ทำไม force delete (`--grace-period=0 --force`) Pod ของฐานข้อมูลบน Node ที่ไม่ตอบจึงอันตราย**

<details>
<summary>แนวคำตอบ</summary>

force delete ลบ Pod จาก API server โดยไม่รอ kubelet ยืนยัน StatefulSet จึงสร้าง Pod ชื่อเดิมทันที ถ้า Node แค่หลุดเครือข่ายแต่ container เดิมยังทำงานและยังเข้าถึง storage ได้ จะมี `som-db-0` สองตัวเขียนข้อมูลชุดเดียวกัน ข้อมูลเสียแบบบทที่ 8 ควรใช้เฉพาะเมื่อแน่ใจว่า Pod เดิมไม่ทำงานแล้ว และควรใช้ taint `out-of-service` เมื่อยืนยันว่า Node ดับ
</details>

**18. ร้านน้องส้มเปลี่ยน `DATABASE_URL` จาก `som-db` เป็น `som-db-0.som-db` เพราะอะไร ถ้ายังใช้ `som-db` และ scale db เป็น 3 จะเกิดอะไร**

<details>
<summary>แนวคำตอบ</summary>

`som-db` ซึ่งตอนนี้เป็น headless Service ตอบ IP ของทุก Pod ที่ Ready เมื่อ scale เป็น 3 `nslookup som-db` ได้ 3 Address web อาจต่อ `som-db-1`/`som-db-2` ซึ่งเป็นฐานข้อมูลเปล่า (ไม่มีตาราง orders) หรือ replica ที่เขียนไม่ได้ ร้านจะตอบไม่สม่ำเสมอ การระบุ `som-db-0.som-db` ทำให้ต่อ primary ตัวเดียวเสมอ (ขั้น F `/api/stats` ยัง `orders=4` ทุกครั้ง)
</details>

**19. เรียงลำดับขั้นตอนการย้ายข้อมูลจาก Deployment `som-db` (PVC `som-db-data`) ไปเป็น StatefulSet `som-db` และบอกว่าถ้าลืมขั้น "ตั้ง PV เป็น Retain" จะเกิดอะไร**

<details>
<summary>แนวคำตอบ</summary>

(1) patch PV เป็น `Retain` (2) ลบ Deployment, Service ClusterIP และ PVC `som-db-data` → PV `Released` (3) ลบ `claimRef` → `Available` (4) สร้าง PVC `data-som-db-0` ที่มี `volumeName` = PV เดิม → `Bound` (5) apply headless Service + StatefulSet → `som-db-0` ใช้ PVC นั้น (6) apply web ที่ต่อ `som-db-0.som-db` ถ้าลืม Retain PV จาก class `standard` เป็น `Delete` เมื่อลบ PVC `som-db-data` PV และโฟลเดอร์ข้อมูลถูกลบทันที ออเดอร์หายถาวร
</details>

**20. ถ้าน้องส้มต้องการรัน Kafka 3 broker, หน้าร้าน web 5 ตัว และ agent เก็บ log บนทุก Node ควรใช้ controller ใดกับแต่ละงาน เพราะอะไร**

<details>
<summary>แนวคำตอบ</summary>

Kafka 3 broker → StatefulSet (แต่ละ broker มีตัวตน ข้อมูลของตัวเอง และต้องรู้จักกันด้วยชื่อคงที่) หน้าร้าน web 5 ตัว → Deployment (stateless ใช้แทนกันได้ อัปเดตแบบ surge ได้) agent เก็บ log บนทุก Node → DaemonSet (ต้องการ 1 Pod ต่อ Node และเพิ่มตาม Node อัตโนมัติ)
</details>

---

## 13. เอกสารอ้างอิง

1. The Kubernetes Authors. *StatefulSets*. https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/
2. The Kubernetes Authors. *StatefulSet Basics* (tutorial). https://kubernetes.io/docs/tutorials/stateful-application/basic-stateful-set/
3. The Kubernetes Authors. *Run a Replicated Stateful Application*. https://kubernetes.io/docs/tasks/run-application/run-replicated-stateful-application/
4. The Kubernetes Authors. *Scale a StatefulSet*. https://kubernetes.io/docs/tasks/run-application/scale-stateful-set/
5. The Kubernetes Authors. *Delete a StatefulSet*. https://kubernetes.io/docs/tasks/run-application/delete-stateful-set/
6. The Kubernetes Authors. *Force Delete StatefulSet Pods*. https://kubernetes.io/docs/tasks/run-application/force-delete-stateful-set-pod/
7. The Kubernetes Authors. *Service* (headless Services). https://kubernetes.io/docs/concepts/services-networking/service/#headless-services
8. The Kubernetes Authors. *DNS for Services and Pods*. https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/
9. The Kubernetes Authors. *Persistent Volumes*. https://kubernetes.io/docs/concepts/storage/persistent-volumes/
10. The Kubernetes Authors. *Node Shutdowns* (non-graceful node shutdown, taint `node.kubernetes.io/out-of-service`). https://kubernetes.io/docs/concepts/cluster-administration/node-shutdown/
11. The Kubernetes Authors. *Taints and Tolerations* (taint based evictions). https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/
12. The Kubernetes Authors. *Garbage Collection* (owners and dependents, cascading deletion). https://kubernetes.io/docs/concepts/architecture/garbage-collection/
13. The Kubernetes Authors. *DaemonSet*. https://kubernetes.io/docs/concepts/workloads/controllers/daemonset/
14. The Kubernetes Authors. *Operator pattern*. https://kubernetes.io/docs/concepts/extend-kubernetes/operator/
15. The Kubernetes Authors. *Specifying a Disruption Budget for your Application*. https://kubernetes.io/docs/tasks/run-application/configure-pdb/
16. The Kubernetes Authors. *kubectl rollout*. https://kubernetes.io/docs/reference/kubectl/generated/kubectl_rollout/
17. PostgreSQL Global Development Group. *Log-Shipping Standby Servers / Streaming Replication*. https://www.postgresql.org/docs/17/warm-standby.html
18. PostgreSQL Global Development Group. *pg_basebackup*. https://www.postgresql.org/docs/17/app-pgbasebackup.html

---

> **หมายเหตุเกี่ยวกับภาพประกอบ:** ภาพประกอบ 38 ภาพในโฟลเดอร์ [`images/`](images/) และภาพตัวละครน้องส้ม (`00-character-som.png`) สร้างขึ้นด้วยปัญญาประดิษฐ์สำหรับการสร้างภาพเพื่อใช้ประกอบการเรียนการสอน ชุดคำสั่งสร้างภาพอยู่ใน [`images/imagegen-prompts.md`](images/imagegen-prompts.md) ภาพใช้อุปมาเชิงเปรียบเทียบเพื่อช่วยความเข้าใจ ตัวเลขในภาพ (เช่น ชื่อ Pod ที่สุ่ม, จำนวนออเดอร์ และเวลา) เป็นค่าตัวอย่าง ผู้เรียนควรใช้เนื้อหาในเอกสารนี้และเอกสารอ้างอิงเป็นหลัก ผลลัพธ์คำสั่งทั้งหมดมาจากการทดลองจริง (Kubernetes v1.37.0) ค่าเวลา, IP, UID, ชื่อ PV, revision hash และ Node ที่ Pod ถูกวางในเครื่องผู้เรียนอาจต่างกัน
