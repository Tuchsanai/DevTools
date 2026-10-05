# PersistentVolume และ PersistentVolumeClaim: ตู้เซฟบนเรือที่ร้านน้องส้มเบิกใช้

> **รายวิชา:** Software Development Tools and Environments (DevTools)
> **หัวข้อ:** Kubernetes Volume และ Persistent Storage — อายุของข้อมูล (container / emptyDir / PV), ประเภท volume (emptyDir, hostPath, persistentVolumeClaim, ephemeral), PersistentVolume, PersistentVolumeClaim, StorageClass, static และ dynamic provisioning, `storageClassName: ""`, การจับคู่และการจองตู้ (`claimRef`/`volumeName`), local-path-provisioner ของ kind, CSI, accessModes (RWO/ROX/RWX/RWOP) และ volumeMode, สถานะและ `volumeBindingMode`, reclaimPolicy (Delete/Retain) และการกู้ PV, finalizers, การขยาย PVC, subPath/readOnly/fsGroup, ข้อมูลผูก Node, ResourceQuota ของ storage, generic ephemeral volume, backup/snapshot และข้อควรระวังเมื่อรันฐานข้อมูลบน Deployment
> **ผลลัพธ์การเรียนรู้ที่เกี่ยวข้อง:** CLO-5, CLO-6
> **บทก่อนหน้า:** [บทที่ 7 Deployment](../../007_kubernetes_deployment/01_Theory/README.md) · **LAB ของบทนี้:** [02_LAB](../02_LAB/README.md)

---

## บทคัดย่อ

บทที่ 7 จบลงที่ร้านอาหารแมวน้องส้มเปลี่ยนรุ่นได้ไม่สะดุดและย้อนรุ่นได้ แต่ทุกครั้งที่ Pod ฐานข้อมูล (`som-db`) ถูกสร้างใหม่ ไม่ว่าจะเพราะลบ Pod, `rollout restart` หรือ Recreate ข้อมูลทั้งหมดก็หายไปพร้อม `emptyDir` ของ Pod เดิม ร้านขึ้น "ร้านกำลังเตรียมสินค้า" (503) จนต้อง `rollout restart deploy/som-web` เพื่อเติมสินค้าใหม่ และออเดอร์เก่าก็หายถาวร บทนี้แก้ปัญหานั้นด้วย **PersistentVolume (PV)** ซึ่งเปรียบเหมือน **ตู้เซฟเหล็กในห้องเก็บของบนเรือ** และ **PersistentVolumeClaim (PVC)** หรือ **ใบเบิกตู้เซฟ** ที่ร้านถือไว้ ตราบใดที่ใบเบิกยังอยู่ ตู้และของในตู้ก็ยังอยู่ แม้บูธ (Pod) จะถูกรื้อสร้างใหม่กี่ครั้งก็ตาม

เนื้อหาเริ่มจาก **อายุของข้อมูล 3 ชั้น** (ไฟล์ใน container, `emptyDir`, PV) และแผนที่ประเภท volume ต่อด้วยการแยกบทบาท **ผู้ดูแลคลัสเตอร์** (สร้าง PV และ StorageClass ซึ่งเป็นของทั้งคลัสเตอร์) กับ **นักพัฒนา** (เขียน PVC ใน namespace แล้วให้ Pod อ้างแค่ชื่อ) วิธีได้ตู้สองแบบ คือ **static provisioning** (ผู้ดูแลเตรียมตู้ไว้ก่อน) และ **dynamic provisioning** (StorageClass + provisioner สร้างตู้ให้อัตโนมัติ) โดยเปิดดูข้างในของ `standard` (local-path-provisioner) ของ kind ว่าตู้จริงคือโฟลเดอร์บน Node จากนั้นเป็นกติกาที่ต้องรู้ตอนใช้งานจริง ได้แก่ **accessModes** (RWO ไม่ได้แปลว่า Pod เดียว), สถานะและ **WaitForFirstConsumer**, **reclaimPolicy** (Delete/Retain) กับการกู้ PV ที่ Released, **finalizers**, การขยาย PVC, `subPath`/`readOnly`/`fsGroup`, ข้อมูลที่ผูกกับ Node เมื่อ Node ล่ม, ResourceQuota ของ storage และ **generic ephemeral volume** ปิดท้ายด้วยความจริงว่า **PV ไม่ใช่ backup** และผลทดลองจริงที่แสดงว่า **ฐานข้อมูลบน Deployment ขยายเป็นหลายตัวไม่ได้** ซึ่งนำไปสู่ StatefulSet ในบทถัดไป

ผลลัพธ์คำสั่งและข้อความ error ที่ยกมาในเอกสารนี้มาจากการทดลองจริงบนคลัสเตอร์ kind (Kubernetes v1.37.0, kubectl v1.37.1) ใน LAB ประจำบท และการตรวจสอบก่อนเขียนบท (pre-check) เมื่อ 5 ตุลาคม 2569 **เวลา, AGE, IP, ชื่อ Pod ที่สุ่ม, ชื่อ PV (`pvc-<uid>`), Node ที่ Pod ถูกวาง และขนาดดิสก์ในเครื่องผู้เรียนจะต่างจากตัวอย่าง** เป็นเรื่องปกติ

## วัตถุประสงค์การเรียนรู้

เมื่อศึกษาเอกสารนี้จบ ผู้เรียนควรสามารถ

1. อธิบายอายุของข้อมูลในไฟล์ของ container, `emptyDir` และ PersistentVolume และเลือกที่เก็บให้เหมาะกับข้อมูลแต่ละแบบ
2. บอกข้อดีข้อเสียของ `emptyDir` (รวม `medium: Memory`, `sizeLimit`) และ `hostPath` รวมถึงเหตุผลที่ Pod Security ระดับ restricted ห้าม `hostPath`
3. แยกบทบาทของ PV, PVC และ StorageClass บอกได้ว่าอะไรเป็น cluster-scoped และอะไรอยู่ใน namespace และเขียน PVC กับ Pod ที่ใช้ PVC ได้
4. อธิบาย static provisioning, กติกาการจับคู่ PV–PVC, ความหมายของ `storageClassName: ""` และการจองตู้ด้วย `claimRef`/`volumeName`
5. อธิบาย dynamic provisioning ด้วย StorageClass, default StorageClass และกลไกของ local-path-provisioner ใน kind (โฟลเดอร์บน Node + PV แบบ hostPath + nodeAffinity) รวมถึงบทบาทของ CSI
6. อธิบาย accessModes ทั้ง 4 แบบ (RWO, ROX, RWX, RWOP) และ volumeMode และบอกข้อจำกัดของ local-path ได้จากผลทดลอง
7. อ่านสถานะของ PVC/PV และ Events (`WaitForFirstConsumer`, `ProvisioningSucceeded`, `ProvisioningFailed`, `FailedBinding`) และอธิบายความต่างของ `WaitForFirstConsumer` กับ `Immediate`
8. อธิบาย reclaimPolicy Delete/Retain เปลี่ยน policy ของ PV ที่มีอยู่ และกู้ PV ที่ `Released` กลับมาใช้ได้ พร้อมอธิบายบทบาทของ finalizers
9. อธิบายเงื่อนไขการขยาย PVC (`allowVolumeExpansion` + driver ที่รองรับ) และใช้ `subPath`, `readOnly`, `fsGroup` ได้ถูกต้อง
10. อธิบายผลของ local storage เมื่อ Node ล่ม และคุมพื้นที่ต่อ namespace ด้วย ResourceQuota ของ storage และใช้ generic ephemeral volume ได้
11. อธิบายว่าทำไม PV ไม่ใช่ backup และทำไมฐานข้อมูลบน Deployment จึงต้องเป็น `replicas: 1` + `Recreate` (และควรใช้ `ReadWriteOncePod`)

## สารบัญ

1. [บทนำ: ร้านลืมออเดอร์](#1-บทนำ-ร้านลืมออเดอร์)
2. [Volume และอายุของข้อมูล](#2-volume-และอายุของข้อมูล)
3. [PV, PVC, StorageClass — ใครทำอะไร](#3-pv-pvc-storageclass--ใครทำอะไร)
4. [Static provisioning (เตรียมตู้เซฟเอง)](#4-static-provisioning-เตรียมตู้เซฟเอง)
5. [Dynamic provisioning (StorageClass)](#5-dynamic-provisioning-storageclass)
6. [accessModes และ volumeMode](#6-accessmodes-และ-volumemode)
7. [การผูก (binding) และสถานะ](#7-การผูก-binding-และสถานะ)
8. [reclaimPolicy และ finalizers](#8-reclaimpolicy-และ-finalizers)
9. [การขยาย PVC](#9-การขยาย-pvc)
10. [subPath, readOnly, fsGroup และสิทธิ์ไฟล์](#10-subpath-readonly-fsgroup-และสิทธิ์ไฟล์)
11. [ข้อมูลผูก Node (ต่อจากบท 003)](#11-ข้อมูลผูก-node-ต่อจากบท-003)
12. [ResourceQuota ของ storage และ ephemeral volume](#12-resourcequota-ของ-storage-และ-ephemeral-volume)
13. [Backup และ snapshot (ปูทาง)](#13-backup-และ-snapshot-ปูทาง)
14. [ฐานข้อมูลกับ Deployment + PVC: ข้อควรระวัง](#14-ฐานข้อมูลกับ-deployment--pvc-ข้อควรระวัง)
15. [สรุปและบทถัดไป](#15-สรุปและบทถัดไป)
16. [คำถามทบทวน](#16-คำถามทบทวน)
17. [เอกสารอ้างอิง](#17-เอกสารอ้างอิง)

### สารบัญรูปภาพ

| รูปที่ | เรื่อง | รูปที่ | เรื่อง |
|:---:|---|:---:|---|
| 1 | [ร้านลืมออเดอร์](#fig-1) | 21 | [ความจริงของ local-path](#fig-21) |
| 2 | [ทวนบท 007: emptyDir กับการ seed ใหม่](#fig-2) | 22 | [RWO ไม่ได้แปลว่า Pod เดียว](#fig-22) |
| 3 | [อุปมาใหม่ของบทนี้](#fig-3) | 23 | [สถานะของ PVC และ PV](#fig-23) |
| 4 | [อายุของที่เก็บข้อมูล 3 ชั้น](#fig-4) | 24 | [WaitForFirstConsumer กับ Immediate](#fig-24) |
| 5 | [แผนที่ประเภท volume](#fig-5) | 25 | [Delete กับ Retain](#fig-25) |
| 6 | [emptyDir](#fig-6) | 26 | [กู้ PV ที่ Released](#fig-26) |
| 7 | [hostPath และความเสี่ยง](#fig-7) | 27 | [finalizers](#fig-27) |
| 8 | [แยกบทบาทผู้ดูแลกับนักพัฒนา](#fig-8) | 28 | [การขยาย PVC](#fig-28) |
| 9 | [กายวิภาค PVC](#fig-9) | 29 | [subPath และ readOnly](#fig-29) |
| 10 | [กายวิภาค PV](#fig-10) | 30 | [สิทธิ์ไฟล์ของ postgres](#fig-30) |
| 11 | [Pod อ้างแค่ชื่อ PVC](#fig-11) | 31 | [Node ล่มเมื่อใช้ local storage](#fig-31) |
| 12 | [Static provisioning](#fig-12) | 32 | [ResourceQuota ของ storage](#fig-32) |
| 13 | [storageClassName: ""](#fig-13) | 33 | [Generic ephemeral volume](#fig-33) |
| 14 | [เงื่อนไขการจับคู่](#fig-14) | 34 | [PV ไม่ใช่ backup](#fig-34) |
| 15 | [จองตู้ด้วย claimRef / volumeName](#fig-15) | 35 | [postgres 2 ตัวบนโฟลเดอร์เดียว](#fig-35) |
| 16 | [Dynamic provisioning](#fig-16) | 36 | [วิธีกัน db สองตัว](#fig-36) |
| 17 | [StorageClass standard ของ kind](#fig-17) | 37 | [ตารางสรุป](#fig-37) |
| 18 | [ข้างในของ local-path](#fig-18) | 38 | [คำสั่งที่ใช้บ่อย](#fig-38) |
| 19 | [CSI](#fig-19) | 39 | [ปิดบทและบทถัดไป](#fig-39) |
| 20 | [accessModes 4 แบบ](#fig-20) | | |

---

## 1. บทนำ: ร้านลืมออเดอร์

<p align="center">
  <img src="images/00-character-som.png" alt="น้องส้ม แมวส้มผู้ช่วยกัปตันท่าเรือ Kubernetes" width="320"><br>
  <em>น้องส้ม ผู้ช่วยกัปตันท่าเรือ Kubernetes ตัวละครหลักของบทนี้</em>
</p>

<p align="center" id="fig-1">
  <img src="images/01-opening-forgot-orders.png" alt="รูปที่ 1 ร้านลืมออเดอร์" width="900"><br>
  <em><b>รูปที่ 1</b> เปิดบทที่ 8: ต่อจากท้ายบท 007 — Pod db ถูกสร้างใหม่ สมุดออเดอร์ในกล่อง emptyDir หายไปกับ Pod เดิม ร้านกลับไปเป็น orders=0</em>
</p>

ตอนจบบทที่ 7 ร้านน้องส้มดูเป็นร้านโปรดักชันเต็มตัว หน้าร้าน `som-web` เป็น Deployment 3 บูธที่เปลี่ยนรุ่นได้โดยลูกค้าไม่เจอ error มีประภาคาร (Service NodePort 30080) ให้เปิดร้านที่ `http://localhost:30080` และครัวกลาง `som-db` เป็น Deployment 1 ตัวแบบ `Recreate` แต่การทดลองสุดท้ายของบทที่ 7 ทำให้เห็นจุดอ่อนใหญ่ที่สุดของร้าน

```bash
kubectl -n som-shop delete pod -l app=som-db
```

Deployment สร้าง Pod db ใหม่ให้ภายในไม่กี่วินาที แต่ `psql` ใน Pod ใหม่ตอบว่า `ERROR:  relation "orders" does not exist` หน้าร้านขึ้น **"ร้านกำลังเตรียมสินค้า" (HTTP 503)** และเมื่อสั่ง `kubectl -n som-shop rollout restart deploy/som-web` ให้ initContainer `db-seed` เติมตารางและสินค้าใหม่ ร้านก็กลับมาขายได้ แต่ **ออเดอร์จาก 5 เหลือ 0** การ `rollout restart deploy/som-db` (Recreate) ก็ให้ผลเดียวกัน

<p align="center" id="fig-2">
  <img src="images/02-recap-007-reseed.png" alt="รูปที่ 2 ทวนบท 007: emptyDir กับการ seed ใหม่" width="900"><br>
  <em><b>รูปที่ 2</b> ทวนบท 007: ข้อมูลใน emptyDir อยู่ได้นานเท่ากับ Pod — ลบ Pod/Recreate/rollout ของ db ทีไร ต้อง rollout restart web เพื่อเติมสินค้าใหม่ แต่ออเดอร์เดิมหายถาวร</em>
</p>

สาเหตุคือ volume `db-data` ของ Pod db เป็น `emptyDir` ซึ่ง **เกิดและตายพร้อม Pod** เมื่อ Pod เดิมถูกลบ โฟลเดอร์ข้อมูลของ postgres ก็ถูกลบตาม Pod ใหม่ได้ `emptyDir` ว่างเปล่าอันใหม่ Deployment ดูแล "จำนวนและรุ่น" ของ Pod ได้ดี แต่ไม่ได้ออกแบบมาดูแลข้อมูล สิ่งที่ร้านต้องการคือ **ที่เก็บข้อมูลที่อายุยืนกว่า Pod** และ Pod ตัวใหม่ "เบิก" กลับมาใช้ได้ ซึ่งคือเรื่องของบทนี้

**เป้าหมายของบทนี้:** เมื่อจบ LAB 10 ร้านน้องส้มจะ **ลบ Pod db, rollout restart db หรือแม้แต่ลบ Deployment db ทั้งตัวแล้ว apply ใหม่ ออเดอร์ก็ยังอยู่ครบโดยไม่ต้อง restart web** และเราจะเห็นด้วยตาว่าข้อมูลหายจริงเมื่อไร (ลบ PVC ที่ reclaimPolicy เป็น Delete) และกู้คืนได้อย่างไร (Retain)

<p align="center" id="fig-3">
  <img src="images/03-metaphor-legend.png" alt="รูปที่ 3 อุปมาใหม่ของบทนี้" width="900"><br>
  <em><b>รูปที่ 3</b> อุปมาใหม่ของบทนี้: PV = ตู้เซฟบนเรือ, PVC = ใบเบิกตู้เซฟ, StorageClass = โรงทำตู้เซฟอัตโนมัติ, ผูกกัน = กุญแจคู่, reclaimPolicy = ทิ้งหรือเก็บตู้เมื่อคืนใบเบิก</em>
</p>

**ตารางที่ 1** อุปมาท่าเรือที่ใช้ในบทนี้ (ต่อจากบทที่ 1–7)

| Kubernetes | อุปมาท่าเรือ | ใหม่ในบทนี้ |
|---|---|:---:|
| container / Pod / Node / Namespace | ตู้สินค้า / บูธร้าน / เรือ / โซนทาสี | |
| ReplicaSet / Deployment / Service | หัวหน้ากะ / ผู้จัดการร้าน / ประภาคาร (บทที่ 5–7) | |
| ข้อมูลของร้าน (ตาราง `orders`) | สมุดออเดอร์ปกส้ม | ✅ |
| `emptyDir` | กล่องกระดาษในบูธ — ทิ้งพร้อมบูธ | ✅ |
| `hostPath` | ช่องเปิดบนดาดฟ้าเรือ — ของอยู่บนเรือลำนั้นลำเดียว | ✅ |
| **PersistentVolume (PV)** | **ตู้เซฟเหล็กในห้องเก็บของบนเรือลำหนึ่ง** มีป้ายบอกขนาด | ✅ |
| **PersistentVolumeClaim (PVC)** | **ใบเบิกตู้เซฟ** ที่ร้านถือไว้ ระบุขนาดและแบบตู้ที่ต้องการ | ✅ |
| **StorageClass** | **โรงทำตู้เซฟอัตโนมัติบนท่า** (แขนกล) ทำตู้ตามใบเบิก | ✅ |
| bind (PV ↔ PVC) | กุญแจคู่ผูกริบบิ้น — ตู้หนึ่งใบต่อใบเบิกหนึ่งใบ | ✅ |
| reclaimPolicy `Delete` / `Retain` | เครื่องบดตู้ / ล็อกกุญแจติดป้ายเหลือง "เก็บไว้" | ✅ |
| `volumeMounts` | ท่อลมจากบูธถึงตู้ | ✅ |
| finalizer | คลิปแดงกันฉีกใบเบิกระหว่างที่ยังมีคนใช้ | ✅ |
| CSI | ปลั๊กมาตรฐานบนผนังโรงทำตู้ ให้ผู้ผลิตตู้หลายเจ้ามาเสียบ | ✅ |

> **ข้อควรจำของอุปมา:** ตู้เซฟแบบที่ใช้ในคลัสเตอร์ kind ของเรา **ไม่ลอยข้ามเรือ** ตู้ถูกสร้างบนเรือ (Node) ลำที่บูธแรกลง และบูธที่จะใช้ตู้นั้นต้องลงเรือลำเดียวกันเสมอ (หัวข้อ 5 และ 11)

---

## 2. Volume และอายุของข้อมูล

### 2.1 อายุของที่เก็บข้อมูล 3 ชั้น

<p align="center" id="fig-4">
  <img src="images/04-lifetime-ladder.png" alt="รูปที่ 4 อายุของที่เก็บข้อมูล 3 ชั้น" width="900"><br>
  <em><b>รูปที่ 4</b> อายุของที่เก็บข้อมูล 3 ชั้น: ไฟล์ใน container หายเมื่อ container เริ่มใหม่, emptyDir อยู่ถึงตอนลบ Pod, PV อยู่ต่อแม้ Pod หายจนกว่าจะลบ PVC/PV</em>
</p>

ไฟล์ที่ process ใน container เขียนลงระบบไฟล์ของ container เอง (เช่น `/tmp`) อยู่ในชั้นที่เขียนได้ของ container นั้น เมื่อ container จบและ kubelet เริ่ม container ใหม่ (restart) ชั้นนี้เริ่มใหม่จาก image จึงหายทั้งหมด **volume** คือโฟลเดอร์ที่ Kubernetes เตรียมให้แล้ว "เมานต์" (mount) เข้าไปใน container ตาม `volumeMounts` อายุของข้อมูลขึ้นกับชนิดของ volume

**ตารางที่ 2** อายุของข้อมูลแต่ละชั้น (ผลจาก LAB 1 และ LAB 10)

| ที่เก็บ | อยู่รอดเมื่อ container restart | อยู่รอดเมื่อลบ Pod แล้วสร้างใหม่ | หายเมื่อ |
|---|:---:|:---:|---|
| ไฟล์ใน container (`/tmp/y.txt`) | ❌ | ❌ | container เริ่มใหม่ |
| `emptyDir` (`/cache/x.txt`) | ✅ | ❌ | Pod ถูกลบ |
| PV ผ่าน PVC (ข้อมูล postgres) | ✅ | ✅ | ลบ PVC (ถ้า reclaimPolicy เป็น Delete) หรือผู้ดูแลลบ PV/ข้อมูลเอง |

ผลจริงจาก LAB 1: Pod `cache-demo` เขียน `/cache/x.txt` (emptyDir), `/ram/r.txt` (emptyDir ใน RAM) และ `/tmp/y.txt` (ไฟล์ใน container) แล้วทำให้ container จบเอง (`touch /tmp/stop`) จน `RESTARTS 1`

```text
NAME         READY   STATUS    RESTARTS     AGE
cache-demo   1/1     Running   1 (3s ago)   21s
```

```text
/cache:
boot.log
x.txt

/ram:
r.txt

/tmp:
hi-from-emptydir
start 05:38:03
start 05:38:16
```

`/tmp` ว่างแล้ว (ไฟล์ใน container หาย) แต่ `x.txt` และ `r.txt` ยังอยู่ และ `boot.log` มี 2 บรรทัด (บันทึกตอนเริ่มทั้งสองครั้ง) เมื่อลบ Pod แล้วสร้างใหม่ `boot.log` เหลือบรรทัดเดียว และ `x.txt` หายไป

> **ข้อสังเกตจาก LAB:** `kubectl exec cache-demo -- kill 1` และ `kill -9 1` **ไม่ทำให้ container ตาย** (RESTARTS ยังเป็น 0) เพราะ `sh` ที่เป็น PID 1 ใน container ไม่รับสัญญาณที่ไม่มี handler LAB จึงใช้วิธีสร้างไฟล์ `/tmp/stop` ให้ loop จบเอง (exit 1) ซึ่ง kubelet จะเริ่ม container ใหม่ตาม `restartPolicy: Always`

### 2.2 แผนที่ประเภท volume

<p align="center" id="fig-5">
  <img src="images/05-volume-types-map.png" alt="รูปที่ 5 แผนที่ประเภท volume" width="900"><br>
  <em><b>รูปที่ 5</b> แผนที่ประเภท volume: emptyDir (ชั่วคราวใน Pod), hostPath (ช่องบนเรือ), configMap/secret (ไฟล์ตั้งค่า — บทหน้า), persistentVolumeClaim (ตู้เซฟ), ephemeral (ใบเบิกที่ทิ้งพร้อม Pod)</em>
</p>

**ตารางที่ 3** ประเภท volume ที่พบบ่อย

| ประเภท | ข้อมูลอยู่ที่ไหน | อายุ | ใช้ทำอะไร | ในบทนี้ |
|---|---|---|---|---|
| `emptyDir` | โฟลเดอร์ว่างบนดิสก์ของ Node (หรือ RAM ถ้า `medium: Memory`) | เท่า Pod | cache, ไฟล์ชั่วคราว, แชร์ไฟล์ระหว่าง container ใน Pod เดียวกัน | LAB 1 (และ db ของบทที่ 6–7) |
| `hostPath` | โฟลเดอร์/ไฟล์บน Node ตรง ๆ | เท่า Node (ไม่มีใครลบให้) | agent ระดับ Node, static Pod, การทดลอง | LAB 2, PV ของ LAB 4 |
| `configMap` / `secret` | ข้อมูลใน API server ถูกเขียนเป็นไฟล์ | ตาม object | ไฟล์ตั้งค่า, รหัสผ่าน | บทหลัง (แนวคิดเท่านั้น) |
| `persistentVolumeClaim` | PV ที่ผูกกับ PVC (ดิสก์ของ Node, NFS, ดิสก์คลาวด์ ฯลฯ) | เท่า PVC/PV ไม่ขึ้นกับ Pod | ฐานข้อมูล, ไฟล์ที่ผู้ใช้อัปโหลด | LAB 3–10 |
| `ephemeral` (generic ephemeral) | PVC ที่ Kubernetes สร้างให้จาก template ใน Pod | เท่า Pod (PVC ถูกลบพร้อม Pod) | พื้นที่ชั่วคราวขนาดใหญ่จาก StorageClass | LAB 9 |

`configMap`/`secret` เป็นแค่การกล่าวถึงในแผนที่ ร้านน้องส้มบทนี้ยังเขียนรหัสผ่านฐานข้อมูลใน YAML ตรง ๆ (`meow1234` เป็นค่าตัวอย่างเพื่อการเรียนเท่านั้น)

### 2.3 emptyDir: กล่องกระดาษในบูธ

<p align="center" id="fig-6">
  <img src="images/06-emptydir-detail.png" alt="รูปที่ 6 emptyDir" width="900"><br>
  <em><b>รูปที่ 6</b> emptyDir: สร้างตอน Pod ขึ้น container ในPod เดียวกันใช้ร่วมกันได้ รอด container restart แต่หายเมื่อ Pod ถูกลบ; medium: Memory = ใช้ RAM, sizeLimit จำกัดขนาด</em>
</p>

`emptyDir` ถูกสร้างเมื่อ Pod ถูกวางบน Node และถูกลบเมื่อ Pod ออกจาก Node container ทุกตัวใน Pod เดียวกันเมานต์ volume เดียวกันได้ (เช่น initContainer เขียนไฟล์ให้ container หลักอ่าน) ตัวอย่างจาก `02_LAB/labs/lab01-emptydir/pod.yaml`

```yaml
  volumes:
    - name: cache
      emptyDir: {}                 # โฟลเดอร์ว่างบนดิสก์ของ Node ที่ Pod ลง
    - name: ram
      emptyDir:
        medium: Memory             # เก็บใน RAM (tmpfs) — เร็วแต่หายง่าย และนับเป็นหน่วยความจำของ Pod
        sizeLimit: 16Mi            # เกินขนาดนี้ Pod จะถูกไล่ออก (evict)
```

ผลจริงของ `df -h /cache /ram` ใน Pod: `/cache` อยู่บนดิสก์ของ Node (ตัวเลขคือขนาดดิสก์ทั้งก้อนของเครื่องทดสอบ ของนักศึกษาจะต่างกัน) ส่วน `/ram` เป็น `tmpfs` ขนาดตาม `sizeLimit`

```text
Filesystem                Size      Used Available Use% Mounted on
/dev/sdd               1006.9G    224.5G    731.1G  23% /cache
tmpfs                    16.0M      4.0K     16.0M   0% /ram
```

| ฟิลด์ | ความหมาย |
|---|---|
| `emptyDir: {}` | ใช้ดิสก์ของ Node (ค่า default) |
| `medium: Memory` | ใช้ RAM (tmpfs) เร็ว แต่ข้อมูลนับเป็นหน่วยความจำของ container และหายทันทีเมื่อ Node reboot |
| `sizeLimit` | ขนาดสูงสุด ถ้าใช้เกิน kubelet จะไล่ Pod ออก (evict) |

### 2.4 hostPath: ช่องเปิดบนดาดฟ้าเรือ

<p align="center" id="fig-7">
  <img src="images/07-hostpath-danger.png" alt="รูปที่ 7 hostPath และความเสี่ยง" width="900"><br>
  <em><b>รูปที่ 7</b> hostPath: ใช้โฟลเดอร์บน Node ตรง ๆ — ข้อมูลผูกกับเรือลำนั้น, Pod ย้ายเรือแล้วไม่เจอ, เสี่ยงความปลอดภัย จึงถูก Pod Security ระดับ restricted ห้าม</em>
</p>

`hostPath` เมานต์โฟลเดอร์หรือไฟล์บน Node เข้า Pod โดยตรง ตัวอย่างจาก `02_LAB/labs/lab02-hostpath/pod-worker.yaml`

```yaml
  nodeSelector:
    kubernetes.io/hostname: lab-worker     # ปักให้ลง Node นี้
  volumes:
    - name: host
      hostPath:
        path: /srv/som-hostpath       # โฟลเดอร์บน Node (ในคลัสเตอร์ kind = ใน container ของ Node)
        type: DirectoryOrCreate       # ไม่มีโฟลเดอร์ก็สร้างให้
```

`type` บอกว่าคาดหวังอะไรที่ path นั้น เช่น `DirectoryOrCreate` (ไม่มีก็สร้างโฟลเดอร์), `Directory` (ต้องมีโฟลเดอร์อยู่แล้ว), `FileOrCreate`, `File` และค่าว่าง (ไม่ตรวจ) ปัญหาของ `hostPath` มีสามข้อ

1. **ข้อมูลผูกกับ Node** — ใน LAB 2 Pod บน `lab-worker2` ที่ใช้ path เดียวกันเห็นเฉพาะไฟล์ของตัวเอง ไม่เห็นไฟล์ที่ Pod บน `lab-worker` เขียน เพราะเป็นคนละเรือ
2. **ไม่มีใครเก็บกวาด** — ลบ namespace `hostpath-lab` แล้ว `docker exec lab-worker cat /srv/som-hostpath/notes.txt` ยังเห็นไฟล์ ต้องลบเองบน Node
3. **ความปลอดภัย** — Pod ที่เมานต์ path สำคัญของ Node (เช่น `/`, `/var/run`) อ่าน/แก้ไฟล์ของ Node ได้ Pod Security ระดับ **restricted** (บทที่ 4) จึงห้าม `hostPath`

ผลจริงเมื่อ apply Pod ใน namespace ที่ติดป้าย `pod-security.kubernetes.io/warn: restricted` (Pod ยังถูกสร้างเพราะเป็นแค่ `warn`)

```text
Warning: would violate PodSecurity "restricted:latest": allowPrivilegeEscalation != false (container "app" must set securityContext.allowPrivilegeEscalation=false), unrestricted capabilities (container "app" must set securityContext.capabilities.drop=["ALL"]), restricted volume types (volume "host" uses restricted volume type "hostPath"), runAsNonRoot != true (pod or container "app" must set securityContext.runAsNonRoot=true), seccompProfile (pod or container "app" must set securityContext.seccompProfile.type to "RuntimeDefault" or "Localhost")
pod/hp-worker created
```

ส่วนที่เกี่ยวกับบทนี้คือ `restricted volume types (volume "host" uses restricted volume type "hostPath")` ถ้า namespace ตั้ง `enforce: restricted` Pod นี้จะถูกปฏิเสธ ส่วน `persistentVolumeClaim`, `emptyDir`, `ephemeral`, `configMap`, `secret` เป็นประเภทที่ restricted อนุญาต

> **ข้อควรจำ:** `hostPath` เหมาะกับงานระดับ Node และการทดลองเท่านั้น แอปทั่วไปที่ต้องการข้อมูลถาวรให้ใช้ PVC แม้ว่าเบื้องหลังของ local-path ใน kind จะเป็น hostPath ก็ตาม (หัวข้อ 5.3) เพราะ PVC ให้ Kubernetes ดูแลการสร้าง/ผูก/ลบ และบังคับให้ Pod ลง Node ที่ถูกต้องให้เอง

---

## 3. PV, PVC, StorageClass — ใครทำอะไร

### 3.1 แยกบทบาทผู้ดูแลกับนักพัฒนา

<p align="center" id="fig-8">
  <img src="images/08-roles-admin-dev.png" alt="รูปที่ 8 แยกบทบาทผู้ดูแลกับนักพัฒนา" width="900"><br>
  <em><b>รูปที่ 8</b> แยกบทบาท: ผู้ดูแลคลัสเตอร์เตรียมตู้เซฟ (PV) หรือโรงทำตู้ (StorageClass); นักพัฒนาเขียนใบเบิก (PVC) แล้วให้ Pod ใช้ใบเบิก — ไม่ต้องรู้ว่าตู้อยู่ไหน</em>
</p>

Kubernetes แยก "ที่เก็บจริง" ออกจาก "คำขอใช้" เพื่อให้นักพัฒนาเขียน manifest แบบเดียวกันได้ไม่ว่าคลัสเตอร์จะใช้ดิสก์แบบไหน

**ตารางที่ 4** object หลักของบทนี้

| Object | อุปมา | ใครสร้าง | scope | หน้าที่ |
|---|---|---|---|---|
| **PersistentVolume (PV)** | ตู้เซฟ | ผู้ดูแลคลัสเตอร์ (static) หรือ provisioner (dynamic) | **cluster-scoped** (ไม่มี namespace) | แทนพื้นที่เก็บจริงหนึ่งก้อน มีขนาด, accessModes, reclaimPolicy, ที่อยู่จริง |
| **PersistentVolumeClaim (PVC)** | ใบเบิก | นักพัฒนา | **namespaced** | ขอพื้นที่ตามขนาด/โหมด/class ที่ต้องการ แล้วผูกกับ PV หนึ่งตัว |
| **StorageClass** | โรงทำตู้อัตโนมัติ | ผู้ดูแลคลัสเตอร์ | **cluster-scoped** | บอกว่าใช้ provisioner ตัวไหนสร้าง PV และกติกาของ PV ที่สร้าง (reclaimPolicy, bindingMode, expansion) |
| Pod | บูธ | นักพัฒนา (ผ่าน Deployment ฯลฯ) | namespaced | อ้าง PVC ด้วย `claimName` แล้วเมานต์ |

ความสัมพันธ์คือ **Pod → PVC → PV → ที่เก็บจริง** Pod รู้จักแค่ชื่อ PVC ใน namespace เดียวกัน ส่วน PV และ StorageClass ไม่มี namespace ผลที่ตามมาในทางปฏิบัติ

- `kubectl get pv` และ `kubectl get sc` ไม่ต้องใส่ `-n` ส่วน `kubectl get pvc` ต้องใส่ `-n <ns>` (หรือ `-A`)
- **ลบ namespace แล้ว PVC ใน namespace นั้นถูกลบ แต่ PV ที่ Retain และ StorageClass ยังอยู่** (LAB 10 ขั้น I: ลบ `som-shop` แล้ว PV ยัง `Released`, class `standard-retain` ยังอยู่)

### 3.2 กายวิภาค PVC

<p align="center" id="fig-9">
  <img src="images/09-pvc-anatomy.png" alt="รูปที่ 9 กายวิภาค PVC" width="900"><br>
  <em><b>รูปที่ 9</b> กายวิภาค PVC: accessModes, resources.requests.storage, storageClassName (ไม่ใส่ = ใช้ default class) — PVC อยู่ใน namespace</em>
</p>

PVC แรกของ LAB 3 (`02_LAB/labs/lab03-first-pvc/pvc.yaml`)

```yaml
# ไม่ใส่ storageClassName → ใช้ class default ของคลัสเตอร์ (kind = standard) ให้แขนกลสร้างตู้ (PV) ให้เอง
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: notes
spec:
  accessModes: [ReadWriteOnce]
  resources:
    requests:
      storage: 10Mi
```

PVC ของร้านน้องส้ม (`02_LAB/som-shop-v4/k8s/10-db.yaml`) ระบุ class และ namespace ชัดเจน

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: som-db-data
  namespace: som-shop
spec:
  storageClassName: standard       # class ของ kind (rancher.io/local-path, Delete, WaitForFirstConsumer)
  accessModes: [ReadWriteOnce]     # เขียนได้จาก Node เดียว (local-path รองรับแค่ RWO/RWOP)
  resources:
    requests:
      storage: 1Gi                 # ขนาดที่ขอ (local-path ไม่ได้บังคับขนาดจริง)
```

**ตารางที่ 5** ฟิลด์สำคัญของ PVC

| ฟิลด์ | ความหมาย | หมายเหตุ |
|---|---|---|
| `accessModes` | โหมดที่ต้องการ (`ReadWriteOnce`, `ReadOnlyMany`, `ReadWriteMany`, `ReadWriteOncePod`) | ต้องเป็นโหมดที่ storage รองรับ (หัวข้อ 6) |
| `resources.requests.storage` | ขนาดขั้นต่ำที่ต้องการ (`10Mi`, `1Gi`) | ได้ PV ที่ใหญ่กว่าได้ (หัวข้อ 4.3) |
| `storageClassName` | ชื่อ StorageClass | ไม่ใส่ = default class, `""` = ไม่ใช้ class (หัวข้อ 4.2) |
| `volumeMode` | `Filesystem` (default) หรือ `Block` | หัวข้อ 6.4 |
| `volumeName` | ระบุ PV ที่ต้องการโดยตรง | ใช้ตอนกู้ PV เดิม (หัวข้อ 4.4, 8.2) |
| `selector` | เลือก PV ตาม label | ใช้กับ static PV |

### 3.3 กายวิภาค PV

<p align="center" id="fig-10">
  <img src="images/10-pv-anatomy.png" alt="รูปที่ 10 กายวิภาค PV" width="900"><br>
  <em><b>รูปที่ 10</b> กายวิภาค PV: capacity, accessModes, persistentVolumeReclaimPolicy, ที่เก็บจริง (hostPath/local/CSI), nodeAffinity, claimRef — PV เป็นของทั้งคลัสเตอร์ ไม่มี namespace</em>
</p>

PV ที่สร้างเองใน LAB 4 (`02_LAB/labs/lab04-static/pv.yaml`)

```yaml
# PV ไม่มี namespace (เป็นของทั้งคลัสเตอร์)
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv-manual
spec:
  capacity:
    storage: 100Mi
  accessModes: [ReadWriteOnce]
  persistentVolumeReclaimPolicy: Retain   # ลบใบเบิกแล้วตู้ยังอยู่ (ค่า default ของ PV ที่สร้างเอง)
  storageClassName: ""                    # ไม่มี class = ไม่ใช่ตู้จากแขนกล
  hostPath:
    path: /srv/som-manual                 # โฟลเดอร์บน Node
    type: DirectoryOrCreate
  nodeAffinity:                           # บอกว่าตู้นี้อยู่บนเรือลำไหน → Pod ที่ใช้ต้องลง Node นี้
    required:
      nodeSelectorTerms:
        - matchExpressions:
            - key: kubernetes.io/hostname
              operator: In
              values: [lab-worker2]
```

**ตารางที่ 6** ฟิลด์สำคัญของ PV

| ฟิลด์ | ความหมาย |
|---|---|
| `capacity.storage` | ขนาดของตู้ (แสดงในคอลัมน์ `CAPACITY`) |
| `accessModes` | โหมดที่ตู้นี้รองรับ |
| `persistentVolumeReclaimPolicy` | ทำอะไรกับตู้เมื่อใบเบิกถูกลบ: `Retain` หรือ `Delete` (หัวข้อ 8) |
| `storageClassName` | class ของตู้ (`""` = ไม่มี class) |
| ที่เก็บจริง (`hostPath`, `local`, `nfs`, `csi` …) | บอกว่าข้อมูลอยู่ที่ไหน ใช้ได้หนึ่งแบบต่อ PV |
| `nodeAffinity` | ตู้นี้เข้าถึงได้จาก Node ไหน — scheduler จะวาง Pod ที่ใช้ตู้นี้บน Node ที่ตรงเท่านั้น |
| `claimRef` | ตู้นี้ผูก (หรือจองไว้) กับ PVC ตัวไหน (namespace/name/uid) |
| `volumeMode` | `Filesystem` หรือ `Block` |

### 3.4 Pod อ้างแค่ชื่อ PVC

<p align="center" id="fig-11">
  <img src="images/11-pod-uses-pvc.png" alt="รูปที่ 11 Pod อ้างแค่ชื่อ PVC" width="900"><br>
  <em><b>รูปที่ 11</b> Pod อ้างแค่ชื่อ PVC: volumes[].persistentVolumeClaim.claimName + volumeMounts[].mountPath — Pod ไม่รู้จัก PV โดยตรง</em>
</p>

Pod `writer` ของ LAB 3 (`02_LAB/labs/lab03-first-pvc/pod.yaml`)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: writer
spec:
  terminationGracePeriodSeconds: 1   # ลบเร็ว (sh + sleep ไม่รับ SIGTERM)
  containers:
    - name: app
      image: busybox:1.36
      command: ["sh", "-c", "echo \"$(date +%T) hello from $(hostname)\" >> /data/log.txt; cat /data/log.txt; ls -ld /data; sleep 3600"]
      volumeMounts:
        - name: data
          mountPath: /data
      resources:
        requests: { cpu: 10m, memory: 16Mi }
        limits:   { cpu: 100m, memory: 64Mi }
  volumes:
    - name: data
      persistentVolumeClaim:
        claimName: notes            # อ้างใบเบิกด้วยชื่อเท่านั้น
```

- `volumes[].name` เป็นชื่อภายใน Pod ที่ `volumeMounts[].name` อ้าง
- `persistentVolumeClaim.claimName` ต้องเป็นชื่อ PVC ใน **namespace เดียวกับ Pod**
- สำหรับ Deployment เขียนส่วนเดียวกันใน `spec.template.spec` (ร้านน้องส้ม: volume `db-data` → `claimName: som-db-data` เมานต์ที่ `/var/lib/postgresql/data`)

ร้านของบทที่ 7 กับบทนี้ต่างกันแค่ volume `db-data` ของ `som-db`

```text
# บทที่ 7 (som-shop-v3)                    # บทที่ 8 (som-shop-v4/k8s/10-db.yaml)
      volumes:                              #       volumes:
        - name: db-data                     #         - name: db-data
          emptyDir: {}                      #           persistentVolumeClaim:
                                            #             claimName: som-db-data
```

---

## 4. Static provisioning (เตรียมตู้เซฟเอง)

### 4.1 ขั้นตอนของ static provisioning

<p align="center" id="fig-12">
  <img src="images/12-static-flow.png" alt="รูปที่ 12 Static provisioning" width="900"><br>
  <em><b>รูปที่ 12</b> Static provisioning: ผู้ดูแลสร้าง PV ไว้ก่อน (Available) → นักพัฒนาสร้าง PVC → control plane หา PV ที่เข้าเงื่อนไขแล้วผูกกัน (Bound)</em>
</p>

ใน static provisioning ผู้ดูแลสร้าง PV ไว้ล่วงหน้า (เช่น ดิสก์ที่ต่อไว้, share NFS) แล้ว controller ชื่อ `persistentvolume-controller` ใน kube-controller-manager จับคู่ PVC ที่เข้าเงื่อนไขให้ ผลจริงจาก LAB 4

```text
persistentvolume/pv-manual created
NAME        CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS      CLAIM   STORAGECLASS   VOLUMEATTRIBUTESCLASS   REASON   AGE
pv-manual   100Mi      RWO            Retain           Available                          <unset>                          0s
```

```text
persistentvolumeclaim/manual-claim created
NAME        CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS   CLAIM                  STORAGECLASS   VOLUMEATTRIBUTESCLASS   REASON   AGE
pv-manual   100Mi      RWO            Retain           Bound    default/manual-claim                  <unset>                          2s
NAME           STATUS   VOLUME      CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
manual-claim   Bound    pv-manual   100Mi      RWO                           <unset>                 2s
```

- PV `Available` → เมื่อมี PVC ที่เข้าเงื่อนไข ทั้งคู่เป็น `Bound` ภายใน 2 วินาที **โดยไม่ต้องมี Pod** (PV ที่ไม่มี class ผูกทันที ต่างจาก `standard` ที่รอ Pod — หัวข้อ 7.2)
- คอลัมน์ `CLAIM` ของ PV เป็น `<namespace>/<pvc>` และคอลัมน์ `STORAGECLASS` ของทั้งคู่ว่าง
- Pod `manual-user` ที่ใช้ `manual-claim` ไม่ได้ระบุ Node แต่ถูกวางบน `lab-worker2` ตาม `nodeAffinity` ของ PV และไฟล์อยู่ที่ `lab-worker2:/srv/som-manual/manual.txt`

### 4.2 storageClassName: "" ต่างจากการไม่ใส่

<p align="center" id="fig-13">
  <img src="images/13-storageclass-empty-string.png" alt="รูปที่ 13 storageClassName: &quot;&quot;" width="900"><br>
  <em><b>รูปที่ 13</b> storageClassName: "" = ขอเฉพาะ PV ที่ไม่มี class (ไม่ให้ default class สร้างตู้ใหม่) — ถ้าไม่ใส่ฟิลด์เลย default class (standard) จะเข้ามาทำแทน</em>
</p>

**ตารางที่ 7** สามแบบของ `storageClassName` ใน PVC

| เขียนใน PVC | ความหมาย | ผลในคลัสเตอร์ kind |
|---|---|---|
| ไม่ใส่ฟิลด์ | ใช้ **default StorageClass** (admission ใส่ชื่อ class ให้ตอนสร้าง) | ได้ `standard` → แขนกลสร้าง PV ใหม่ให้ (LAB 3 คอลัมน์ `STORAGECLASS` = `standard`) |
| `storageClassName: ""` | **ไม่ใช้ class** ขอเฉพาะ PV ที่ไม่มี class | จับกับ `pv-manual` ได้ (LAB 4) ถ้าไม่มี PV ที่ตรง → `Pending` |
| `storageClassName: standard-retain` | ใช้ class ที่ระบุ | ได้ PV จาก class นั้น (LAB 7, LAB 10 ขั้น H) |

> **ข้อควรจำ:** ถ้าต้องการให้ PVC ผูกกับ static PV ที่ไม่มี class อย่าลืม `storageClassName: ""` ไม่เช่นนั้นคลัสเตอร์ที่มี default class จะสร้างตู้ใหม่ให้แทน และ PV ที่เตรียมไว้จะไม่ถูกใช้

### 4.3 เงื่อนไขการจับคู่

<p align="center" id="fig-14">
  <img src="images/14-matching-rules.png" alt="รูปที่ 14 เงื่อนไขการจับคู่" width="900"><br>
  <em><b>รูปที่ 14</b> เงื่อนไขการจับคู่: class ตรง, accessModes ครบ, ขนาด PV ≥ ที่ขอ — ได้ตู้ใหญ่กว่าได้ (ขอ 50Mi ได้ PV 100Mi แสดง CAPACITY 100Mi) ขอเกินทุกตู้ = Pending</em>
</p>

PV จะถูกเลือกให้ PVC เมื่อ

1. `storageClassName` ตรงกัน (รวมกรณีว่างทั้งคู่)
2. `accessModes` ของ PV มีโหมดที่ PVC ขอครบ
3. ขนาด PV **มากกว่าหรือเท่ากับ** ที่ขอ (controller เลือกตู้ที่เล็กที่สุดที่ใหญ่พอ)
4. ตรง `selector` ของ PVC (ถ้ามี) และ `volumeMode` ตรงกัน
5. PV ยัง `Available` (ไม่ถูกผูกหรือจองโดย PVC อื่น)

PV หนึ่งตัวผูกกับ PVC ได้ตัวเดียว (กุญแจคู่) แม้ PVC ขอ 50Mi และ PV มี 100Mi ส่วนที่เหลือก็ไม่ถูกแบ่งให้ใคร คอลัมน์ `CAPACITY` ของ PVC จึงแสดง **ขนาดของ PV** (100Mi) ไม่ใช่ขนาดที่ขอ

PVC `too-big` ขอ 1Gi โดย `storageClassName: ""` ไม่มี PV ไหนใหญ่พอ และไม่มี class ให้สร้าง จึงค้าง `Pending` พร้อม Event

```text
too-big        Pending                                                        <unset>                 3s
Events:
  Type    Reason         Age   From                         Message
  ----    ------         ----  ----                         -------
  Normal  FailedBinding  3s    persistentvolume-controller  no persistent volumes available for this claim and no storage class is set
```

### 4.4 จองตู้ล่วงหน้าด้วย claimRef และ volumeName

<p align="center" id="fig-15">
  <img src="images/15-claimref-volumename.png" alt="รูปที่ 15 จองตู้ด้วย claimRef / volumeName" width="900"><br>
  <em><b>รูปที่ 15</b> จองตู้ล่วงหน้า: PV ใส่ spec.claimRef (จองให้ PVC ชื่อนี้) หรือ PVC ใส่ spec.volumeName (ขอตู้ใบนี้) — ใช้ตอนกู้ข้อมูลจาก PV เดิม</em>
</p>

การจับคู่อัตโนมัติไม่รับประกันว่าได้ตู้ใบไหน ถ้าต้องการจับคู่แบบเจาะจง ทำได้สองฝั่ง

- **ฝั่ง PV:** ใส่ `spec.claimRef` (`namespace` + `name`) ของ PVC ที่จะมาใช้ PV นี้จะถูกเก็บไว้ให้ PVC ตัวนั้นเท่านั้น เมื่อผูกแล้ว Kubernetes เติม `uid` ให้เอง ตัวอย่าง `claimRef` ที่ระบบเขียนลงใน PV หลังผูกแล้ว (ผลจริงจาก LAB 3)

  ```yaml
    claimRef:
      apiVersion: v1
      kind: PersistentVolumeClaim
      name: notes
      namespace: default
      resourceVersion: "1203"
      uid: b4fb1995-3929-4c26-930e-08074d960afb
  ```

- **ฝั่ง PVC:** ใส่ `spec.volumeName` ชี้ชื่อ PV ตรง ๆ ข้ามการค้นหาตู้ และไม่ให้แขนกลสร้างตู้ใหม่ LAB 6 และ LAB 10 ใช้วิธีนี้กู้ตู้เดิม (`02_LAB/labs/lab06-lifecycle/pvc-reuse.yaml`)

  ```yaml
  apiVersion: v1
  kind: PersistentVolumeClaim
  metadata:
    name: ledger
  spec:
    storageClassName: standard       # ต้องตรงกับ class ของ PV
    volumeName: PV_NAME              # ชี้ตู้เดิมโดยตรง (แขนกลจะไม่สร้างตู้ใหม่)
    accessModes: [ReadWriteOnce]
    resources:
      requests:
        storage: 10Mi                # ต้องไม่เกินขนาดของ PV
  ```

  `PV_NAME` ในไฟล์ถูกแทนด้วยชื่อ PV จริงตอนใช้งาน (`sed "s/PV_NAME/$PV/" pvc-reuse.yaml | kubectl apply -f -`) PV ต้องเป็น `Available` ก่อน และเงื่อนไขอื่น (class, โหมด, ขนาด) ยังต้องตรง

---

## 5. Dynamic provisioning (StorageClass)

### 5.1 ขั้นตอนของ dynamic provisioning

<p align="center" id="fig-16">
  <img src="images/16-dynamic-flow.png" alt="รูปที่ 16 Dynamic provisioning" width="900"><br>
  <em><b>รูปที่ 16</b> Dynamic provisioning: PVC ระบุ StorageClass → provisioner สร้าง PV ชื่อ pvc-&lt;uid&gt; ให้อัตโนมัติแล้วผูกกับ PVC — ไม่ต้องรอผู้ดูแล</em>
</p>

การให้ผู้ดูแลสร้าง PV ทีละตัวไม่สะดวกเมื่อมีหลายทีม **dynamic provisioning** ให้ผู้ดูแลสร้าง StorageClass ไว้ครั้งเดียว แล้ว **provisioner** (โปรแกรมที่ class ระบุ) สร้าง PV ให้ทุกครั้งที่มี PVC ใหม่ ผลจริงจาก LAB 3 (`describe pvc notes` หลังสร้าง Pod)

```text
Events:
  Type    Reason                 Age   From                                                                                                Message
  ----    ------                 ----  ----                                                                                                -------
  Normal  WaitForFirstConsumer   8s    persistentvolume-controller                                                                         waiting for first consumer to be created before binding
  Normal  ExternalProvisioning   5s    persistentvolume-controller                                                                         Waiting for a volume to be created either by the external provisioner 'rancher.io/local-path' or manually by the system administrator. If volume creation is delayed, please verify that the provisioner is running and correctly registered.
  Normal  Provisioning           5s    rancher.io/local-path_local-path-provisioner-75f7fc7dc5-5dkx2_6485bdfa-b176-4448-844b-ec03de28220b  External provisioner is provisioning volume for claim "default/notes"
  Normal  ProvisioningSucceeded  2s    rancher.io/local-path_local-path-provisioner-75f7fc7dc5-5dkx2_6485bdfa-b176-4448-844b-ec03de28220b  Successfully provisioned volume pvc-b4fb1995-3929-4c26-930e-08074d960afb
```

ลำดับคือ (1) PVC รอ Pod ตัวแรก (`WaitForFirstConsumer`) (2) เมื่อ scheduler เลือก Node ให้ Pod แล้ว controller ส่งงานให้ provisioner ภายนอก (`ExternalProvisioning`) (3) provisioner สร้างตู้ (`Provisioning` → `ProvisioningSucceeded`) (4) PV ใหม่ผูกกับ PVC

```text
NAME                          STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE   VOLUMEMODE
persistentvolumeclaim/notes   Bound    pvc-b4fb1995-3929-4c26-930e-08074d960afb   10Mi       RWO            standard       <unset>                 8s    Filesystem

NAME                                                        CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS   CLAIM           STORAGECLASS   VOLUMEATTRIBUTESCLASS   REASON   AGE   VOLUMEMODE
persistentvolume/pvc-b4fb1995-3929-4c26-930e-08074d960afb   10Mi       RWO            Delete           Bound    default/notes   standard       <unset>                          2s    Filesystem
```

ชื่อ PV ที่ได้คือ **`pvc-` + uid ของ PVC** (`claimRef.uid` ของ PV เป็น `b4fb1995-3929-4c26-930e-08074d960afb` ตรงกับชื่อ) ชื่อนี้สุ่มใหม่ทุกครั้ง ในเครื่องนักศึกษาจะไม่เหมือนตัวอย่าง reclaimPolicy ของ PV สืบทอดจาก class (`Delete`)

### 5.2 StorageClass standard ของ kind

<p align="center" id="fig-17">
  <img src="images/17-default-storageclass.png" alt="รูปที่ 17 StorageClass standard ของ kind" width="900"><br>
  <em><b>รูปที่ 17</b> kind มี StorageClass standard (default) — annotation storageclass.kubernetes.io/is-default-class: "true", provisioner rancher.io/local-path, Delete, WaitForFirstConsumer, ALLOWVOLUMEEXPANSION false</em>
</p>

คลัสเตอร์ kind มี StorageClass มาให้หนึ่งตัว ผลจริงจาก LAB 0

```text
NAME                 PROVISIONER             RECLAIMPOLICY   VOLUMEBINDINGMODE      ALLOWVOLUMEEXPANSION   AGE
standard (default)   rancher.io/local-path   Delete          WaitForFirstConsumer   false                  3m6s
```

```text
    storageclass.kubernetes.io/is-default-class: "true"
provisioner: rancher.io/local-path
reclaimPolicy: Delete
volumeBindingMode: WaitForFirstConsumer
```

**ตารางที่ 8** ฟิลด์ของ StorageClass

| ฟิลด์ | ค่าใน `standard` | ความหมาย |
|---|---|---|
| annotation `storageclass.kubernetes.io/is-default-class` | `"true"` | เป็น default class (คำว่า `(default)` หลังชื่อ) — PVC ที่ไม่ใส่ `storageClassName` ใช้ class นี้ ควรมี default เพียงตัวเดียว |
| `provisioner` | `rancher.io/local-path` | โปรแกรมที่สร้าง PV |
| `reclaimPolicy` | `Delete` (default ถ้าไม่ใส่) | ใส่ให้ PV ที่ class นี้สร้าง |
| `volumeBindingMode` | `WaitForFirstConsumer` | สร้างตู้เมื่อมี Pod ใช้ (หัวข้อ 7.2) — ค่า default ถ้าไม่ใส่คือ `Immediate` |
| `allowVolumeExpansion` | ไม่ใส่ (= `false`) | อนุญาตให้ขยาย PVC หรือไม่ (หัวข้อ 9) |
| `parameters` | – | ค่าเฉพาะของ provisioner (เช่น ชนิดดิสก์คลาวด์) |

StorageClass ของเราเองใน LAB 7 (`02_LAB/labs/lab07-storageclass/sc-retain.yaml`) ใช้ provisioner ตัวเดิมแต่เปลี่ยน reclaimPolicy

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: standard-retain
provisioner: rancher.io/local-path
reclaimPolicy: Retain
volumeBindingMode: WaitForFirstConsumer
```

> **ข้อควรจำ:** ฟิลด์ของ StorageClass (provisioner, reclaimPolicy, parameters) แก้ภายหลังไม่ได้ ถ้าต้องการค่าใหม่ให้สร้าง class ใหม่ และการแก้/ลบ class **ไม่มีผลกับ PV ที่สร้างไปแล้ว** (LAB 7: ลบ `standard-retain` แล้ว PV ของ `kept` ยังอยู่ `Released`)

### 5.3 ข้างในของ local-path

<p align="center" id="fig-18">
  <img src="images/18-local-path-inside.png" alt="รูปที่ 18 ข้างในของ local-path" width="900"><br>
  <em><b>รูปที่ 18</b> ข้างในของ local-path: สร้างโฟลเดอร์ /var/local-path-provisioner/pvc-&lt;uid&gt;_&lt;ns&gt;_&lt;pvc&gt; บน Node ที่ Pod ถูกวาง แล้วทำ PV แบบ hostPath + nodeAffinity ผูกกับ Node นั้น</em>
</p>

provisioner ของ kind คือ Deployment `local-path-provisioner` ใน namespace `local-path-storage` (ผลจริงจาก LAB 0)

```text
NAME                                      READY   STATUS    RESTARTS   AGE    IP           NODE                NOMINATED NODE   READINESS GATES
local-path-provisioner-75f7fc7dc5-5dkx2   1/1     Running   0          3m1s   10.244.0.4   lab-control-plane   <none>           <none>
docker.io/kindest/local-path-provisioner:v20260820-69b56db7
```

ConfigMap `local-path-config` บอกว่าจะสร้างโฟลเดอร์ที่ไหนบน Node

```text
{
        "nodePathMap":[
        {
                "node":"DEFAULT_PATH_FOR_NON_LISTED_NODES",
                "paths":["/var/local-path-provisioner"]
        }
        ]
}
```

เมื่อมี PVC ที่ต้องการตู้ provisioner สร้างโฟลเดอร์ `pvc-<uid>_<namespace>_<pvc>` ใต้ `/var/local-path-provisioner` **บน Node ที่ Pod ถูกวาง** แล้วสร้าง PV ที่ชี้โฟลเดอร์นั้นด้วย `hostPath` และติด `nodeAffinity` ไว้ที่ Node นั้น ผลจริงจาก LAB 3 (`kubectl get pv $PV -o yaml`)

```yaml
spec:
  accessModes:
  - ReadWriteOnce
  capacity:
    storage: 10Mi
  claimRef:
    apiVersion: v1
    kind: PersistentVolumeClaim
    name: notes
    namespace: default
    resourceVersion: "1203"
    uid: b4fb1995-3929-4c26-930e-08074d960afb
  hostPath:
    path: /var/local-path-provisioner/pvc-b4fb1995-3929-4c26-930e-08074d960afb_default_notes
    type: DirectoryOrCreate
  nodeAffinity:
    required:
      nodeSelectorTerms:
      - matchExpressions:
        - key: kubernetes.io/hostname
          operator: In
          values:
          - lab-worker
  persistentVolumeReclaimPolicy: Delete
  storageClassName: standard
  volumeMode: Filesystem
status:
  lastPhaseTransitionTime: "2026-10-05T05:39:12Z"
  phase: Bound
```

และบน Node (Node ในคลัสเตอร์ kind คือ container ใน k8s-lab จึงดูด้วย `docker exec` ได้)

```text
N=lab-worker
total 12
drwxr-xr-x  3 root root 4096 Oct  5 05:39 .
drwxr-xr-x 12 root root 4096 Oct  5 05:39 ..
drwxrwxrwx  2 root root 4096 Oct  5 05:39 pvc-b4fb1995-3929-4c26-930e-08074d960afb_default_notes
05:39:14 hello from writer
```

ข้อเท็จจริงสำคัญของ local-path ที่เห็นใน LAB

- โฟลเดอร์ `/var/local-path-provisioner` **ยังไม่มีบน Node จนกว่าจะมี PV แรก** (LAB 0: `No such file or directory`)
- โฟลเดอร์ของตู้เป็น `drwxrwxrwx root` (0777) ทุกคนเขียนได้ (หัวข้อ 10)
- ข้อมูลอยู่บน Node เดียว ตู้ "ไม่ลอยข้ามเรือ" ถ้า Node ล่ม Pod ย้ายไป Node อื่นไม่ได้ (หัวข้อ 11)
- ลบ PVC (Delete) แล้ว provisioner ลบทั้ง PV และโฟลเดอร์ (LAB 3: `ls /var/local-path-provisioner/` ว่าง)
- **ไม่บังคับขนาด ไม่รองรับการขยาย ไม่รองรับ RWX/Block และ `fsGroup` ไม่มีผล** (หัวข้อ 6, 9, 10)

local-path จึงเหมาะกับคลัสเตอร์ทดลองบนเครื่องเดียว (kind, เครื่องพัฒนา) ไม่ใช่ระบบจริงที่ต้องทน Node ล่ม

### 5.4 CSI: ปลั๊กมาตรฐานของโรงทำตู้

<p align="center" id="fig-19">
  <img src="images/19-csi-concept.png" alt="รูปที่ 19 CSI" width="900"><br>
  <em><b>รูปที่ 19</b> CSI (Container Storage Interface): มาตรฐานปลั๊กกลางให้ผู้ผลิต storage ต่อกับ Kubernetes — ระบบจริงใช้ CSI driver ของคลาวด์/NFS/Ceph ได้ RWX, expand, snapshot</em>
</p>

เดิมโค้ดของ storage แต่ละเจ้าฝังอยู่ใน Kubernetes เอง (in-tree) ปัจจุบันผู้ผลิต storage เขียน **CSI driver** ตามมาตรฐาน Container Storage Interface แล้วติดตั้งลงคลัสเตอร์ ความสามารถที่ได้จึงขึ้นกับ driver ที่ใช้

**ตารางที่ 9** local-path ของ kind เทียบกับ CSI driver ที่ใช้ในระบบจริง (แนวคิด — บทนี้ไม่ได้ติดตั้ง CSI driver)

| ความสามารถ | local-path (kind) | CSI driver ทั่วไปในระบบจริง |
|---|---|---|
| ข้อมูลอยู่ที่ | โฟลเดอร์บน Node เดียว | ดิสก์เครือข่าย/คลาวด์/ระบบไฟล์กระจาย ต่อเข้า Node ไหนก็ได้ |
| Node ล่ม | Pod ย้ายไม่ได้ ต้องรอ Node กลับ | ถอดดิสก์ไปต่อ Node ใหม่ได้ (ขึ้นกับชนิด) |
| RWX | ❌ | ได้กับ NFS, CephFS, ระบบไฟล์เครือข่ายของคลาวด์ |
| ขยาย PVC | ❌ | ได้ถ้า driver มี resizer |
| VolumeSnapshot | ❌ | ได้ถ้า driver รองรับ + มี snapshot controller |
| บังคับขนาด | ❌ (เป็นแค่ตัวเลข) | ✅ ดิสก์มีขนาดตามที่ขอจริง |

---

## 6. accessModes และ volumeMode

### 6.1 accessModes 4 แบบ

<p align="center" id="fig-20">
  <img src="images/20-access-modes-doors.png" alt="รูปที่ 20 accessModes 4 แบบ" width="900"><br>
  <em><b>รูปที่ 20</b> accessModes 4 แบบ: RWO (เมานต์ได้จาก Node เดียว), ROX (อ่านได้หลาย Node), RWX (อ่านเขียนหลาย Node), RWOP (Pod เดียวเท่านั้น) — เป็นคุณสมบัติที่ storage ต้องรองรับ</em>
</p>

**ตารางที่ 10** accessModes

| โหมด | ชื่อย่อ (คอลัมน์ ACCESS MODES) | ความหมาย | local-path |
|---|---|---|:---:|
| `ReadWriteOnce` | RWO | อ่านเขียนได้จาก **Node เดียว** (Pod หลายตัวบน Node นั้นใช้ร่วมได้) | ✅ |
| `ReadOnlyMany` | ROX | อ่านอย่างเดียวจากหลาย Node | – (ไม่ได้ทดลอง) |
| `ReadWriteMany` | RWX | อ่านเขียนจากหลาย Node พร้อมกัน | ❌ |
| `ReadWriteOncePod` | RWOP | อ่านเขียนได้จาก **Pod เดียว** ทั้งคลัสเตอร์ (GA ตั้งแต่ Kubernetes 1.29) | ✅ |

accessModes **ไม่ใช่สิทธิ์ที่ขอได้ตามใจ** แต่เป็นคุณสมบัติที่ storage ต้องรองรับ ดิสก์แบบบล็อกที่ต่อเข้าเครื่องได้ทีละเครื่องให้ RWX ไม่ได้ไม่ว่าจะเขียน YAML อย่างไร

### 6.2 ความจริงของ local-path (ทดสอบแล้ว)

<p align="center" id="fig-21">
  <img src="images/21-local-path-truth.png" alt="รูปที่ 21 ความจริงของ local-path" width="900"><br>
  <em><b>รูปที่ 21</b> ความจริงของ local-path (ทดสอบแล้ว): รองรับแค่ RWO และ RWOP, ขอ RWX → ProvisioningFailed, volumeMode: Block ไม่รองรับ, ขนาดไม่ถูกบังคับ (เขียน 50MB ลง PVC 10Mi ได้)</em>
</p>

ผลจริงจาก LAB 5 (`describe pvc shared` ที่ขอ `ReadWriteMany` และ `describe pvc blk` ที่ขอ `volumeMode: Block`)

```text
  Warning  ProvisioningFailed    8s               rancher.io/local-path_local-path-provisioner-75f7fc7dc5-5dkx2_6485bdfa-b176-4448-844b-ec03de28220b  failed to provision volume with StorageClass "standard": NodePath only supports ReadWriteOnce and ReadWriteOncePod (1.22+) access modes
```

```text
  Warning  ProvisioningFailed    9s               rancher.io/local-path_local-path-provisioner-75f7fc7dc5-5dkx2_6485bdfa-b176-4448-844b-ec03de28220b  rancher.io/local-path does not support block volume provisioning
```

PVC ทั้งสองค้าง `Pending` และ Pod ที่รอ (`use-rwx`, `use-blk`) ค้าง `Pending` **โดยไม่มี Event ของ Pod เลย** (`Events: <none>`) ต้องไปดูที่ `describe pvc` จึงจะรู้สาเหตุ

ส่วนเรื่องขนาด เขียนไฟล์ 50MB ลง PVC ที่ขอ 10Mi สำเร็จ และ `df` เห็นดิสก์ทั้งก้อนของ Node

```text
52428800 bytes (50.0MB) copied, 0.378015 seconds, 132.3MB/s
-rw-r--r--    1 root     root       50.0M Oct  5 05:40 /data/big
Filesystem                Size      Used Available Use% Mounted on
/dev/sdd               1006.9G    224.6G    731.1G  23% /data
NAME       STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
rwo-data   Bound    pvc-ef6d2f75-cbb0-4b2f-9696-408f278e2d5d   10Mi       RWO            standard       <unset>                 5s
```

> **ข้อควรจำ:** ใน local-path `resources.requests.storage` เป็นแค่ตัวเลขที่ใช้จับคู่และนับ quota ไม่ได้จำกัดพื้นที่จริง แอปเขียนจนดิสก์ของ Node เต็มได้ ในระบบจริงที่ใช้ดิสก์ตามขนาด ขนาดจะถูกบังคับจริง (ขนาดดิสก์ `1006.9G` เป็นของเครื่องทดสอบ ของนักศึกษาจะต่างกัน)

### 6.3 RWO ไม่ได้แปลว่า Pod เดียว

<p align="center" id="fig-22">
  <img src="images/22-rwo-not-one-pod.png" alt="รูปที่ 22 RWO ไม่ได้แปลว่า Pod เดียว" width="900"><br>
  <em><b>รูปที่ 22</b> RWO ≠ Pod เดียว: Pod 2 ตัวบน Node เดียวกันใช้ PVC RWO พร้อมกันได้; ถ้าต้องการ Pod เดียวจริงใช้ RWOP — Pod ที่ 2 จะ Pending</em>
</p>

ความเข้าใจผิดที่พบบ่อยคือคิดว่า RWO = Pod เดียว ผลจริงจาก LAB 5: Pod `rwo-b` ที่ใช้ PVC เดียวกับ `rwo-a` ถูก scheduler ส่งไป Node เดียวกัน (ตาม nodeAffinity ของ PV) และอ่านไฟล์ที่ `rwo-a` เขียนได้

```text
NAME    READY   STATUS    RESTARTS   AGE   IP            NODE         NOMINATED NODE   READINESS GATES
rwo-a   1/1     Running   0          5s    10.244.2.11   lab-worker   <none>           <none>
rwo-b   1/1     Running   0          1s    10.244.2.12   lab-worker   <none>           <none>
05:40:06 from rwo-a
05:40:07 from rwo-b
```

ถ้าต้องการให้ระบบกันไม่ให้มี Pod ตัวที่สองจริง ๆ ใช้ `ReadWriteOncePod` Pod ตัวที่ 2 (`rwop-b`) ค้าง `Pending`

```text
  Warning  FailedScheduling  8s    default-scheduler  0/3 nodes are available: 1 node(s) had untolerated taint(s), 2 node(s) unavailable due to PersistentVolumeClaim with ReadWriteOncePod access mode already in-use by another pod. preemption: 0/3 nodes are available: 1 Preemption is not helpful for scheduling, 2 No preemption victims found for incoming pod.
```

(`1 node(s) had untolerated taint(s)` คือ control-plane ที่มี taint ส่วน worker 2 ตัวถูกตัดเพราะตู้ RWOP มีเจ้าของแล้ว) ความต่างนี้สำคัญมากกับฐานข้อมูล (หัวข้อ 14)

### 6.4 volumeMode: Filesystem และ Block

| volumeMode | Pod ได้อะไร | เขียนใน Pod ด้วย |
|---|---|---|
| `Filesystem` (default) | โฟลเดอร์ที่มีระบบไฟล์แล้ว | `volumeMounts[].mountPath` |
| `Block` | อุปกรณ์ดิสก์ดิบ ไม่มีระบบไฟล์ (ฐานข้อมูลบางตัวจัดการเอง) | `volumeDevices[].devicePath` |

ตัวอย่างจาก `02_LAB/labs/lab05-access/blk.yaml` (local-path ไม่รองรับ จึงค้าง Pending ตามผลด้านบน)

```yaml
# ใบเบิกแบบ Block
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: blk
spec:
  accessModes: [ReadWriteOnce]
  volumeMode: Block                # ค่า default คือ Filesystem
  resources:
    requests:
      storage: 10Mi
```

ฝั่ง Pod (`use-blk`) ใช้ `volumeDevices` แทน `volumeMounts`

```yaml
      volumeDevices:
        - name: data
          devicePath: /dev/xvda      # ดิสก์ดิบจะโผล่เป็นอุปกรณ์ตรงนี้
```

---

## 7. การผูก (binding) และสถานะ

### 7.1 สถานะของ PVC และ PV

<p align="center" id="fig-23">
  <img src="images/23-phases.png" alt="รูปที่ 23 สถานะของ PVC และ PV" width="900"><br>
  <em><b>รูปที่ 23</b> สถานะ: PVC Pending → Bound (Lost เมื่อ PV หาย); PV Available → Bound → Released (คืนใบเบิกแล้ว) และ Failed เมื่อคืนตู้ไม่สำเร็จ</em>
</p>

**ตารางที่ 11** สถานะ (คอลัมน์ `STATUS`)

| Object | สถานะ | ความหมาย | เห็นใน LAB |
|---|---|---|---|
| PVC | `Pending` | ยังไม่ได้ตู้ (รอ Pod, ไม่มี PV ที่ตรง, provisioner ล้มเหลว, quota) | LAB 3, 4, 5, 7 |
| PVC | `Bound` | ผูกกับ PV แล้ว | ทุก LAB |
| PVC | `Lost` | PV ที่ผูกอยู่หายไป | – (ไม่ได้ทดลอง) |
| PV | `Available` | ว่าง ยังไม่ผูก | LAB 4, 6, 10 |
| PV | `Bound` | ผูกกับ PVC แล้ว | ทุก LAB |
| PV | `Released` | PVC ถูกลบแล้ว แต่ PV ยังไม่ถูกคืนสู่สภาพว่าง (ยังมี `claimRef` เดิม) | LAB 4, 6, 10 |
| PV | `Failed` | การคืนตู้อัตโนมัติล้มเหลว | – (ไม่ได้ทดลอง) |

PVC ใน Kubernetes v1.37 ยังมี **Conditions** บอกว่ามี Pod อ้างถึงอยู่หรือไม่ (ผลจริงจาก LAB 3)

```text
Used By:       writer
Conditions:
  Type     Status  LastProbeTime                     LastTransitionTime                Reason        Message
  ----     ------  -----------------                 ------------------                ------        -------
  Unused   False   Mon, 01 Jan 0001 00:00:00 +0000   Mon, 05 Oct 2026 12:39:12 +0700   PodUsingPVC   A pod is currently referencing this PVC
```

### 7.2 volumeBindingMode: WaitForFirstConsumer กับ Immediate

<p align="center" id="fig-24">
  <img src="images/24-wffc-vs-immediate.png" alt="รูปที่ 24 WaitForFirstConsumer กับ Immediate" width="900"><br>
  <em><b>รูปที่ 24</b> volumeBindingMode: WaitForFirstConsumer = รอให้ scheduler เลือก Node ของ Pod ก่อนแล้วค่อยสร้างตู้บนเรือลำนั้น; Immediate สร้างทันที — กับ local-path ล้มเหลว "no node was specified"</em>
</p>

PVC `notes` ของ LAB 3 ค้าง `Pending` ทันทีหลังสร้าง ไม่ได้แปลว่าผิด แต่ class `standard` เป็น **WaitForFirstConsumer**

```text
NAME    STATUS    VOLUME   CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
notes   Pending                                      standard       <unset>                 3s
...
  Normal  WaitForFirstConsumer  3s    persistentvolume-controller  waiting for first consumer to be created before binding
```

เมื่อ Pod `writer` ถูกสร้าง scheduler เลือก Node ให้ Pod ก่อน (ดู requests, taint, affinity ของ Pod ตามปกติ) แล้วเขียนชื่อ Node ลง annotation ของ PVC ให้ provisioner สร้างตู้บน Node นั้น

```text
Annotations:   pv.kubernetes.io/bind-completed: yes
               pv.kubernetes.io/bound-by-controller: yes
               volume.beta.kubernetes.io/storage-provisioner: rancher.io/local-path
               volume.kubernetes.io/selected-node: lab-worker
               volume.kubernetes.io/storage-provisioner: rancher.io/local-path
```

**ตารางที่ 12** เทียบ volumeBindingMode

| | `WaitForFirstConsumer` | `Immediate` |
|---|---|---|
| สร้าง/ผูกตู้เมื่อไร | เมื่อมี Pod ตัวแรกใช้ PVC และ scheduler เลือก Node แล้ว | ทันทีที่สร้าง PVC |
| ข้อดี | ตู้อยู่บน Node (หรือ zone) ที่ Pod ลงได้จริง | ได้ตู้ก่อน ไม่ต้องมี Pod |
| ข้อเสีย | PVC `Pending` จนกว่าจะมี Pod (ปกติ ไม่ใช่ error) | storage ที่ผูก Node/zone อาจได้ตู้ในที่ที่ Pod ลงไม่ได้ |
| กับ local-path | ✅ (ค่าของ `standard`) | ❌ `configuration error, no node was specified` |

ผลจริงของ class `local-immediate` ใน LAB 7 (provisioner ไม่รู้ว่าจะสร้างโฟลเดอร์บน Node ไหน PVC ค้าง Pending)

```text
  Warning  ProvisioningFailed    9s               rancher.io/local-path_local-path-provisioner-75f7fc7dc5-5dkx2_6485bdfa-b176-4448-844b-ec03de28220b  failed to provision volume with StorageClass "local-immediate": configuration error, no node was specified
```

**ตารางที่ 13** Events ที่ควรอ่านเป็น (`kubectl describe pvc <ชื่อ>`)

| Reason | ความหมาย |
|---|---|
| `WaitForFirstConsumer` | รอ Pod ตัวแรก (ปกติของ class แบบ WaitForFirstConsumer) |
| `ExternalProvisioning` | ส่งงานให้ provisioner ภายนอก รอสร้างตู้ |
| `Provisioning` / `ProvisioningSucceeded` | provisioner กำลังสร้าง / สร้างสำเร็จ |
| `ProvisioningFailed` | provisioner สร้างไม่ได้ (โหมด/ชนิดไม่รองรับ, ตั้งค่า class ผิด) |
| `FailedBinding` | ไม่มี PV ที่ตรงและไม่มี class ให้สร้าง |
| `ExternalExpanding` | รอ controller ภายนอกขยาย PVC (หัวข้อ 9) |

> **ข้อควรจำ:** Pod ที่ค้าง `Pending` เพราะ PVC บางครั้ง **ไม่มี Event ของ Pod เลย** (LAB 5) ให้ไล่ดู `kubectl describe pvc` ทุกครั้งที่ Pod ที่ใช้ PVC ไม่ขึ้น

---
