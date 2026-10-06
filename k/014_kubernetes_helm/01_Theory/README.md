# Helm: ชุดแฟรนไชส์ร้านน้องส้ม — เปิดสาขาทั้งร้านด้วยคำสั่งเดียว

> **รายวิชา:** Software Development Tools and Environments (DevTools)
> **หัวข้อ:** Helm 4 (v4.3.0) — package manager ของ Kubernetes: chart, values, release, revision, repository; โครงสร้าง chart (`Chart.yaml` version/appVersion, `values.yaml`, `values.schema.json`, `templates/`, `_helpers.tpl`, `NOTES.txt`, `crds/`, `charts/`); Go template + Sprig (`include`, `default`, `quote`, `required`, `lookup`, `toYaml | nindent`, `if`/`range`/`with`, checksum annotation); ลำดับความสำคัญของ values และกับดัก upgrade; `helm template`/`lint`/`--dry-run`; lifecycle (install, upgrade, rollback, uninstall, `--wait`, `--rollback-on-failure`, `--keep-history`); server-side apply, field manager, `--take-ownership`/`--force-conflicts`; release Secret; hooks และ `helm test`; subchart; repository แบบ HTTP กับ OCI, Artifact Hub; ความปลอดภัยของแหล่ง chart (กรณี Bitnami 2568); เทียบ Kustomize และปูทาง GitOps/operator
> **ผลลัพธ์การเรียนรู้ที่เกี่ยวข้อง:** CLO-5, CLO-6
> **บทก่อนหน้า:** [บทที่ 13 HPA](../../013_kubernetes_hpa/01_Theory/README.md) · **LAB ของบทนี้:** [02_LAB](../02_LAB/README.md)

---

## บทคัดย่อ

ท้ายบทที่ 13 ร้านอาหารแมวน้องส้มรับวันลดราคาได้เองแล้ว หน้าร้าน `som-web` เพิ่ม/ลดบูธ 2 ↔ 6 ตาม HPA แต่ร้านทั้งร้านยังเป็น **กองไฟล์ YAML** (namespace, db, config, web, admin, ingress, hpa, customers) บวก Traefik และ metrics-server ที่ติดตั้งด้วย static manifest อีกชุด วันนี้น้องส้มอยากเปิด **สาขาที่ 2** (สาขาทดลอง dev) จึงเจอปัญหาเดิมซ้ำ ๆ: ค่าเดียวกันซ้ำหลายไฟล์ ต้อง copy โฟลเดอร์แล้วแก้ทีละจุด สองสาขาค่อย ๆ ต่างกันโดยไม่รู้ตัว และย้อนรุ่น "ทั้งร้าน" พร้อมกันไม่ได้เพราะ `kubectl rollout history` มีรุ่นเฉพาะ Deployment

บทนี้แนะนำ **Helm** หรือ **หุ่นยนต์ผู้รับเหมาติดตั้งร้าน** ที่รับ **ชุดแฟรนไชส์ (chart)** + **ใบสั่งปรับแต่งร้าน (values)** แล้วเปิด **ร้านสาขา (release)** ให้ทั้งร้านในคำสั่งเดียว พร้อม **สมุดบันทึกการปรับปรุงร้าน (revision)** ที่ใช้อัปเกรด ย้อนรุ่น และถอนการติดตั้งได้เป็นชุด เนื้อหาเริ่มจากปัญหาของ YAML ล้วน ศัพท์ 5 คำของ Helm และประวัติ Helm 2 → 3 → 4 ต่อด้วยโครงสร้าง chart, Go template + ฟังก์ชัน Sprig ที่ใช้จริงในชุด `som-shop`, ลำดับความสำคัญของ values, การ render/debug, lifecycle ของ release, **server-side apply ที่เป็นค่าเริ่มต้นใน Helm 4** และการ "รับร้านเดิม" ที่ติดตั้งด้วย `kubectl apply` เข้ามาอยู่ใต้ Helm, ที่เก็บ release (Secret ที่ถอดอ่านได้), hooks และ `helm test`, subchart, repository แบบ HTTP และ OCI, ความปลอดภัยของแหล่ง chart (บทเรียนจาก Bitnami ปี 2568) ปิดท้ายด้วยการเทียบกับ Kustomize และปูทางไป GitOps (Argo CD/Flux) และ operator

ผลลัพธ์คำสั่งและข้อความที่ยกมาในเอกสารนี้มาจากการทดลองจริงด้วย **helm v4.3.0** บนคลัสเตอร์ kind (Kubernetes v1.37.0, kubectl v1.37.1) ใน LAB ประจำบทเมื่อ 6 ตุลาคม 2569 (เวลาไทย) บนเครื่องที่จำกัดไว้ 4 CPU **เวลา, เลข revision, ชื่อ Pod และค่า hash ในเครื่องผู้เรียนอาจต่างจากตัวอย่าง** แต่ลำดับเหตุการณ์และข้อความ error ควรตรงกัน

## วัตถุประสงค์การเรียนรู้

เมื่อศึกษาเอกสารนี้จบ ผู้เรียนควรสามารถ

1. อธิบายปัญหาของการติดตั้งแอปด้วยไฟล์ YAML ล้วน (ค่าซ้ำ, drift ระหว่าง environment, ไม่มีรุ่นของทั้งชุด, ลบไม่หมด) และบอกได้ว่า Helm แก้ส่วนไหนและไม่แก้ส่วนไหน
2. ใช้ศัพท์ chart, values, release, revision, repository ได้ถูกต้อง และอธิบายความต่างของ Helm 2 (Tiller), Helm 3 และ Helm 4 ที่กระทบการใช้งาน
3. อ่านและเขียนโครงสร้าง chart `apiVersion: v2` ได้ แยก `version` กับ `appVersion` และรู้ข้อจำกัดของโฟลเดอร์ `crds/`
4. เขียน template ด้วย Go template + Sprig ระดับพื้นฐาน (`.Values`, `.Release`, `.Chart`, pipeline, `default`, `quote`, `required`, `toYaml | nindent`, `if`/`range`/`with`, `define`/`include`, `lookup`) และใช้ checksum annotation ให้ Pod ใหม่เกิดเองเมื่อ config เปลี่ยน
5. อธิบายลำดับความสำคัญของ values (`values.yaml` < `-f` < `--set`) การ merge แบบ map/list และกับดักของ `helm upgrade` ที่ส่งค่ามาเพียงบางตัว พร้อมใช้ `values.schema.json` เป็นด่านตรวจ
6. ใช้ `helm template`, `helm lint`, `--debug`, `--dry-run=client|server` หาจุดผิดของ chart ได้ และรู้ว่า `--dry-run=server` ของ Helm 4.3 **ไม่** ตรวจ field ผิด
7. ควบคุม lifecycle ของ release: install, upgrade, rollback (ระบุเลขเสมอ), uninstall, `--wait`, `--timeout`, `--rollback-on-failure`, `--keep-history` และอ่าน `helm history` ได้
8. อธิบาย server-side apply, field manager และ conflict และเลือกใช้ `--take-ownership`, `--force-conflicts`, `--force-replace` ได้อย่างเข้าใจผลข้างเคียง
9. ถอดข้อมูล release จาก Secret `helm.sh/release.v1` และอธิบายความเสี่ยงของรหัสผ่านใน values
10. เขียน hook และ test ของ chart อธิบาย `hook-weight` และ `hook-delete-policy` ได้
11. แยก repository แบบ HTTP กับ OCI ใช้ Artifact Hub เลือก chart จากผู้เผยแพร่ที่น่าเชื่อถือ pin เวอร์ชัน/digest และอธิบายว่า chart กับ image ถูกดึงโดยคนละตัว
12. เทียบ Helm กับ Kustomize และ static manifest และอธิบายบทบาทของ GitOps และ operator ที่ต่อยอดจาก Helm

## สารบัญ

1. [บทนำ: ร้านน้องส้มอยากเปิดสาขาที่ 2](#1-บทนำ-ร้านน้องส้มอยากเปิดสาขาที่-2)
2. [ปัญหาของ YAML ล้วน](#2-ปัญหาของ-yaml-ล้วน)
3. [Helm คืออะไร](#3-helm-คืออะไร)
4. [โครงสร้าง chart](#4-โครงสร้าง-chart)
5. [Go template และ Sprig ขั้นพื้นฐาน](#5-go-template-และ-sprig-ขั้นพื้นฐาน)
6. [values และลำดับความสำคัญ](#6-values-และลำดับความสำคัญ)
7. [การ render และ debug](#7-การ-render-และ-debug)
8. [lifecycle ของ release](#8-lifecycle-ของ-release)
9. [Helm 4 กับ server-side apply](#9-helm-4-กับ-server-side-apply)
10. [release เก็บที่ไหน](#10-release-เก็บที่ไหน)
11. [hooks และ helm test](#11-hooks-และ-helm-test)
12. [dependencies (subchart)](#12-dependencies-subchart)
13. [repository: HTTP vs OCI และ Artifact Hub](#13-repository-http-vs-oci-และ-artifact-hub)
14. [ความปลอดภัยและแหล่งที่มา](#14-ความปลอดภัยและแหล่งที่มา)
15. [Helm vs Kustomize vs static manifest](#15-helm-vs-kustomize-vs-static-manifest)
16. [ปูทาง GitOps และ operator](#16-ปูทาง-gitops-และ-operator)
17. [ตารางคำสั่งที่ใช้บ่อย](#17-ตารางคำสั่งที่ใช้บ่อย)
18. [สรุปบท](#18-สรุปบท)
19. [คำถามทบทวน](#19-คำถามทบทวน)
20. [เอกสารอ้างอิง](#20-เอกสารอ้างอิง)

### สารบัญรูปภาพ

| รูปที่ | เรื่อง | รูปที่ | เรื่อง |
|:---:|---|:---:|---|
| 1 | [เปิดบท ชุดแฟรนไชส์ร้านน้องส้ม](#fig-1) | 27 | [กับดัก upgrade ส่งค่าบางตัว](#fig-27) |
| 2 | [ทวนบท 013 กองไฟล์ YAML](#fig-2) | 28 | [values.schema.json ด่านตรวจใบสั่ง](#fig-28) |
| 3 | [อุปมาใหม่ (1)](#fig-3) | 29 | [template / lint / dry-run](#fig-29) |
| 4 | [อุปมาใหม่ (2)](#fig-4) | 30 | [error ที่เจอบ่อย 4 แบบ](#fig-30) |
| 5 | [เป้าหมายของบท](#fig-5) | 31 | [วงจรชีวิตสาขา](#fig-31) |
| 6 | [ค่าซ้ำหลายไฟล์](#fig-6) | 32 | [rollback เขียนหน้าใหม่](#fig-32) |
| 7 | [copy โฟลเดอร์แล้ว drift](#fig-7) | 33 | [กลยุทธ์ --wait](#fig-33) |
| 8 | [ไม่มีรุ่นของทั้งชุด](#fig-8) | 34 | [กับดัก rollback ไม่ระบุเลข](#fig-34) |
| 9 | [kubectl apply เทียบ helm install](#fig-9) | 35 | [field manager](#fig-35) |
| 10 | [Helm = package manager](#fig-10) | 36 | [SSA conflict](#fig-36) |
| 11 | [ศัพท์หลัก 5 คำ](#fig-11) | 37 | [รับของเดิมเข้า Helm](#fig-37) |
| 12 | [ประวัติ Helm 2 → 3 → 4](#fig-12) | 38 | [release Secret](#fig-38) |
| 13 | [สิ่งที่เปลี่ยนใน Helm 4](#fig-13) | 39 | [จังหวะของ hook](#fig-39) |
| 14 | [ข้างในชุดแฟรนไชส์](#fig-14) | 40 | [hook-delete-policy](#fig-40) |
| 15 | [version กับ appVersion](#fig-15) | 41 | [helm test ผู้ตรวจรับร้าน](#fig-41) |
| 16 | [crds/ และ charts/](#fig-16) | 42 | [subchart และ Chart.lock](#fig-42) |
| 17 | [แม่พิมพ์มีช่องว่าง](#fig-17) | 43 | [HTTP repository กับ OCI](#fig-43) |
| 18 | [built-in objects](#fig-18) | 44 | [Artifact Hub](#fig-44) |
| 19 | [pipeline และ default](#fig-19) | 45 | [chart กับ image คนละคนดึง](#fig-45) |
| 20 | [nindent กับ indent](#fig-20) | 46 | [เช็กลิสต์ความปลอดภัย](#fig-46) |
| 21 | [if / range / with](#fig-21) | 47 | [แคตตาล็อกหายได้](#fig-47) |
| 22 | [_helpers.tpl ตรายาง](#fig-22) | 48 | [static / Kustomize / Helm](#fig-48) |
| 23 | [required และ lookup](#fig-23) | 49 | [ปูทาง GitOps](#fig-49) |
| 24 | [checksum/config](#fig-24) | 50 | [ปูทาง operator](#fig-50) |
| 25 | [ลำดับความสำคัญของ values](#fig-25) | 51 | [คำสั่งที่ใช้บ่อย](#fig-51) |
| 26 | [ใบสั่งต่อ environment](#fig-26) | 52 | [สรุปบท](#fig-52) |

---

## 1. บทนำ: ร้านน้องส้มอยากเปิดสาขาที่ 2

<p align="center">
  <img src="images/00-character-som.png" alt="น้องส้ม แมวส้มผู้ช่วยกัปตันท่าเรือ Kubernetes" width="320"><br>
  <em>น้องส้ม ผู้ช่วยกัปตันท่าเรือ Kubernetes ตัวละครหลักของบทนี้</em>
</p>

<p align="center" id="fig-1">
  <img src="images/01-opening-franchise-kit.png" alt="รูปที่ 1 เปิดบท ชุดแฟรนไชส์ร้านน้องส้ม" width="900"><br>
  <em><b>รูปที่ 1</b> เปิดบทที่ 14: ร้านน้องส้มขายดีจนอยากเปิดสาขาใหม่ น้องส้มจึงแพ็กร้านทั้งร้านเป็นชุดแฟรนไชส์สำเร็จรูปที่ใช้เปิดสาขาได้ด้วยคำสั่งเดียว</em>
</p>

ร้านอาหารแมวน้องส้มเดินทางมาไกลแล้ว บทที่ 5–7 ร้านมีหัวหน้ากะ (ReplicaSet) ประภาคาร (Service) และผู้จัดการร้าน (Deployment) บทที่ 8–9 ครัวกลาง `som-db-0` มีตู้เซฟ (PVC) ของตัวเอง บทที่ 10–11 ป้ายร้านอยู่ใน ConfigMap และรหัสผ่านอยู่ใน Secret บทที่ 12 ลูกค้าเข้าร้านผ่านประตูหน้าท่าเรือ (Traefik + Ingress) และบทที่ 13 หุ่นยนต์ผู้ช่วยผู้จัดการ (HPA) เพิ่ม/ลดบูธเองตามความเหนื่อยที่เจ้าหน้าที่จดมิเตอร์ (metrics-server) จดไว้

ร้านขายดีจนน้องส้มอยากเปิด **สาขาที่ 2** เริ่มจากสาขาทดลอง (dev) ไว้ลองของใหม่ก่อนขึ้นสาขาจริง (prod) แต่พอเปิดโฟลเดอร์ร้านของบท 013 ก็พบว่าการ "ก็อปร้านทั้งร้าน" ไม่ง่ายอย่างที่คิด

<p align="center" id="fig-2">
  <img src="images/02-recap-yaml-pile.png" alt="รูปที่ 2 ทวนบท 013 กองไฟล์ YAML" width="900"><br>
  <em><b>รูปที่ 2</b> ทวนบท 013: ร้านทั้งร้านคือไฟล์ YAML หลายแผ่น (namespace, db, config, web, admin, ingress, hpa, customers) บวก Traefik และ metrics-server ที่ติดตั้งด้วย static manifest — จะเปิดสาขาใหม่ต้องก็อปทั้งหมด</em>
</p>

ทบทวนสิ่งที่ต้องทำเพื่อตั้งร้านหนึ่งร้านตั้งแต่ศูนย์ (ตามบทที่ 12–13)

1. `kubectl apply` CRD ของ Traefik แล้วตามด้วย `00-traefik.yaml` (namespace, ServiceAccount, ClusterRole, Deployment, Service NodePort, IngressClass)
2. `kubectl apply` `00-metrics-server.yaml` (เพิ่ม `--kubelet-insecure-tls` เฉพาะ LAB)
3. สร้าง namespace แล้วสร้าง **Secret 3 ซอง** ด้วยมือ (`som-db-secret`, `som-tls` จาก `openssl`, `som-admin-auth`)
4. `kubectl apply` ไฟล์ร้านตามลำดับ `00-namespace` → `10-db` → `15-config` → `20-web` → `40-admin` → `50-ingress` → `60-hpa` → `70-customers`
5. รอ db พร้อม ตรวจ Ingress และจดไว้ว่าสั่งอะไรไปบ้าง เพราะวันหนึ่งต้องลบออกให้หมด

ทุกคำสั่งข้างบนใช้ได้และเราเข้าใจทุกบรรทัดแล้ว ปัญหาคือ **มันไม่ใช่ "ชุด"** ไม่มีอะไรบอกว่าไฟล์ไหนเป็นของร้านไหน รุ่นไหน และไม่มีปุ่ม "ย้อนทั้งร้าน"

<p align="center" id="fig-3">
  <img src="images/03-metaphor-legend-1.png" alt="รูปที่ 3 อุปมาใหม่ (1)" width="900"><br>
  <em><b>รูปที่ 3</b> อุปมาใหม่ (1): chart = ชุดแฟรนไชส์, values = ใบสั่งปรับแต่งร้าน, templates = แม่พิมพ์ป้าย/บูธ, release = ร้านสาขาที่เปิดจริง, revision = สมุดบันทึกการปรับปรุงร้าน, helm = หุ่นยนต์ผู้รับเหมา</em>
</p>

<p align="center" id="fig-4">
  <img src="images/04-metaphor-legend-2.png" alt="รูปที่ 4 อุปมาใหม่ (2)" width="900"><br>
  <em><b>รูปที่ 4</b> อุปมาใหม่ (2): repository/Artifact Hub = แคตตาล็อกแฟรนไชส์, OCI registry = โกดังเก็บชุดแฟรนไชส์, hook = ขั้นตอนพิเศษก่อน/หลังเปิดร้าน, helm test = ผู้ตรวจรับร้าน, values.schema.json = ด่านตรวจใบสั่ง</em>
</p>

**ตารางที่ 1** อุปมาท่าเรือที่ใช้ในบทนี้ (ต่อจากบทที่ 1–13)

| Helm / Kubernetes | อุปมาท่าเรือ | ใหม่ในบทนี้ |
|---|---|:---:|
| Deployment, Service, Ingress, HPA ... | บูธ ผู้จัดการร้าน ประภาคาร ประตูหน้าท่าเรือ หุ่นยนต์ผู้ช่วย | |
| **helm (CLI)** | **หุ่นยนต์ผู้รับเหมาติดตั้งร้าน** (หมวกนิรภัยสีส้ม ถือแท็บเล็ต) | ✅ |
| **chart** | **ชุดแฟรนไชส์ร้านสำเร็จรูป**: กล่องที่มีคู่มือ แม่พิมพ์ และใบสั่ง | ✅ |
| **values (`values.yaml`, `-f`, `--set`)** | **ใบสั่งปรับแต่งร้าน** (ชื่อ สี จำนวนบูธ) | ✅ |
| **templates/** | **แม่พิมพ์ป้าย/บูธ** ที่เว้นช่องว่างไว้ให้เติม | ✅ |
| **`_helpers.tpl`** | **ตรายาง** ที่ปั๊มซ้ำได้ทุกแผ่น | ✅ |
| **`values.schema.json`** | **ด่านตรวจใบสั่ง** | ✅ |
| **release** | **ร้านสาขาที่เปิดจริง** จากชุดแฟรนไชส์ (มีป้ายชื่อสาขา) | ✅ |
| **revision** | **สมุดบันทึกการปรับปรุงร้าน** หน้าละ 1 รุ่น | ✅ |
| **release Secret** | สมุดที่เก็บในตู้ของโซน มีสำเนาใบสั่งอยู่ข้างใน | ✅ |
| **repository / Artifact Hub** | **แคตตาล็อกแฟรนไชส์** | ✅ |
| **OCI registry** | **โกดังเก็บชุดแฟรนไชส์** | ✅ |
| **hook** | **ขั้นตอนพิเศษก่อน/หลังเปิดร้าน** (เช่น เติมสินค้าเข้าชั้น) | ✅ |
| **`helm test`** | **ผู้ตรวจรับร้าน** | ✅ |
| **field manager (server-side apply)** | **ป้ายชื่อเจ้าของบนแต่ละช่องของร้าน** | ✅ |
| **conflict** | ช่องเดียวมีป้ายเจ้าของ 2 คนแย่งกัน | ✅ |
| **`--take-ownership`** | ติดป้ายสาขาใหม่บนร้านเดิม | ✅ |
| **subchart** | กล่องย่อยในกล่องแฟรนไชส์ | ✅ |
| GitOps (Argo CD / Flux) | หุ่นยนต์เฝ้าแฟ้มแผนร้าน (ปูทาง) | ✅ |

<p align="center" id="fig-5">
  <img src="images/05-chapter-goals.png" alt="รูปที่ 5 เป้าหมายของบท" width="900"><br>
  <em><b>รูปที่ 5</b> เป้าหมายของบท: ชุดแฟรนไชส์ som-shop ชุดเดียว + ใบสั่งต่างกัน → เปิดสาขา dev และ prod ได้ด้วยคำสั่งเดียว อัปเกรด/ย้อนรุ่นทั้งร้านได้</em>
</p>

เป้าหมายปลายบท (LAB 12) คือคำสั่งแบบนี้

```bash
# สาขาทดลอง (namespace ใหม่) — ติดตั้งทั้งร้านในคำสั่งเดียว
helm install som charts/som-shop -n som-dev --create-namespace \
  -f charts/values-dev.yaml --set db.password=meow1234 --wait

# สาขาจริง: อัปเกรดหน้าร้านเป็น 1.8 แล้วย้อนกลับถ้าไม่ชอบ
helm upgrade som charts/som-shop -n som-shop -f charts/values-prod.yaml --set web.image.tag=1.8 --wait
helm rollback som 2 -n som-shop --wait
```

> รหัส `meow1234` เป็น **รหัสตัวอย่างเพื่อการเรียนเท่านั้น** (ใช้ต่อเนื่องจากบทที่ 11) ห้ามใช้กับระบบจริง

ในเครื่องทดลอง คำสั่งแรกเปิดสาขา dev ครบทั้งร้าน (db + หน้าร้าน + ป้าย + ซอง + ประตู + เติมสินค้า) ภายใน **18.0 วินาที** และ `helm test` ตรวจรับร้านผ่าน ส่วนการอัปเกรด 1.7 → 1.8 และย้อนกลับใช้ 15 และ 11 วินาทีโดยลูกค้าที่ยิงเข้าร้านตลอดเวลา **ไม่เจอ error เลย** (`ok=400 err=0`, `ok=300 err=0`)

## 2. ปัญหาของ YAML ล้วน

### 2.1 ค่าเดียวกันซ้ำหลายไฟล์

<p align="center" id="fig-6">
  <img src="images/06-yaml-duplicate-values.png" alt="รูปที่ 6 ค่าซ้ำหลายไฟล์" width="900"><br>
  <em><b>รูปที่ 6</b> ค่าเดียวกันซ้ำหลายไฟล์: ชื่อร้าน, label, image tag อยู่หลายที่ แก้ไม่ครบเมื่อไรร้านเพี้ยน</em>
</p>

ลองนับค่าที่ซ้ำกันในไฟล์ร้านบท 013

| ค่า | อยู่ที่ไหนบ้าง | ถ้าแก้ไม่ครบ |
|---|---|---|
| ชื่อ `som-web` | Deployment, Service, Ingress backend, HPA `scaleTargetRef`, label/selector | Ingress ชี้ Service ที่ไม่มี (404) หรือ HPA หาเป้าไม่เจอ |
| ชื่อ `som-db` + DNS `som-db-0.som-db` | StatefulSet, headless Service, `DATABASE_URL` ใน Secret, initContainer `wait-for-db` | หน้าร้านต่อ db ไม่ได้ |
| image tag `1.7` | Deployment (container + annotation change-cause) | เปลี่ยนรุ่นแล้ว change-cause ยังบอกรุ่นเก่า |
| host `shop.localhost` + พอร์ต `30081` | Ingress, ใบรับรอง SAN, Middleware redirect | redirect ไปพอร์ตผิด หรือใบรับรองไม่ตรงชื่อ |
| รหัสฐานข้อมูล | `POSTGRES_PASSWORD` และใน `DATABASE_URL` (Secret เดียวกัน 2 key) | หน้าร้าน login db ไม่ได้ |

YAML ไม่มี "ตัวแปร" ค่าเหล่านี้จึงถูกพิมพ์ซ้ำ ทุกครั้งที่จะเปลี่ยนต้องจำว่ามันอยู่ที่ไหนบ้าง

### 2.2 หลาย environment = copy โฟลเดอร์แล้วค่อย ๆ ต่างกัน

<p align="center" id="fig-7">
  <img src="images/07-copy-folder-drift.png" alt="รูปที่ 7 copy โฟลเดอร์แล้ว drift" width="900"><br>
  <em><b>รูปที่ 7</b> อยากมีหลาย environment แบบ copy โฟลเดอร์แล้วแก้ = สองสาขาค่อย ๆ ต่างกันโดยไม่รู้ตัว (drift)</em>
</p>

ทางที่ง่ายที่สุดคือ `cp -r k8s k8s-dev` แล้วแก้ชื่อร้าน ธีม จำนวนบูธ และ host ในสำเนา วันแรกสองโฟลเดอร์ต่างกันแค่ 5 บรรทัด แต่หลังจากนั้นทุกการแก้ (เช่น เพิ่ม readinessProbe, เปลี่ยน requests) ต้องทำ 2 ที่ ไม่ช้าก็เร็วจะมีที่หนึ่งถูกลืม เกิด **drift** — สาขาทดลองไม่เหมือนสาขาจริงอีกต่อไป การทดสอบบน dev จึงไม่รับประกันอะไรกับ prod

### 2.3 ไม่มี "รุ่น" ของทั้งชุด

<p align="center" id="fig-8">
  <img src="images/08-no-bundle-version.png" alt="รูปที่ 8 ไม่มีรุ่นของทั้งชุด" width="900"><br>
  <em><b>รูปที่ 8</b> kubectl rollout history มีรุ่นเฉพาะ Deployment — ConfigMap, Secret, Ingress ไม่มีรุ่น ย้อนทั้งร้านพร้อมกันไม่ได้</em>
</p>

บทที่ 7 เราใช้ `kubectl rollout undo` ย้อนรุ่นหน้าร้านได้ แต่ถ้าการเปลี่ยนแปลงหนึ่งครั้งแตะ ConfigMap (ป้ายใหม่), Secret (รหัสใหม่) และ Deployment (image ใหม่) พร้อมกัน `rollout undo` ย้อนได้เฉพาะ Deployment ส่วนป้ายและซองยังเป็นค่าใหม่ ร้านจึงอยู่ในสภาพ "ครึ่งเก่าครึ่งใหม่" ที่ไม่เคยมีใครทดสอบ

### 2.4 kubectl apply ไม่รู้ว่าอะไรเป็นของชุดไหน

<p align="center" id="fig-9">
  <img src="images/09-kubectl-vs-helm.png" alt="รูปที่ 9 kubectl apply เทียบ helm install" width="900"><br>
  <em><b>รูปที่ 9</b> เทียบ kubectl apply (ติดตั้งทีละไฟล์ ไม่มีชื่อชุด) กับ helm install (ติดตั้งเป็นชุดที่มีชื่อสาขาและรุ่น)</em>
</p>

**ตารางที่ 2** สิ่งที่ `kubectl apply` ทำ/ไม่ทำ เทียบกับ Helm

| เรื่อง | `kubectl apply -f` | `helm install/upgrade` |
|---|---|---|
| สร้าง/อัปเดต object ตามไฟล์ | ✅ | ✅ (render template ก่อนแล้วส่งเข้า API server) |
| ตัวแปรและเงื่อนไขในไฟล์ | ❌ (ต้องใช้เครื่องมืออื่น เช่น Kustomize) | ✅ template + values |
| ชื่อของชุด ("ร้านนี้คือ release `som`") | ❌ | ✅ release name + namespace |
| รุ่นของทั้งชุด | ❌ (มีแค่ rollout history ของ Deployment) | ✅ revision 1, 2, 3, ... |
| ย้อนทั้งชุด | ❌ | ✅ `helm rollback som <rev>` |
| ลบทั้งชุดโดยไม่ต้องจำไฟล์ | ⚠️ ต้องมีไฟล์ชุดเดิม (`kubectl delete -f`) | ✅ `helm uninstall som` |
| ลบ object ที่ถูกเอาออกจากไฟล์ | ❌ (เว้นแต่ใช้ `--prune` ซึ่งต้องระวัง) | ✅ upgrade ลบ object ที่ chart รุ่นใหม่ไม่มีแล้ว |
| แจกจ่ายให้คนอื่นใช้ | ⚠️ ส่งโฟลเดอร์ | ✅ แพ็กเป็น `.tgz` เก็บใน repository/OCI registry |
| รู้ว่าใครติดตั้งอะไรไว้ในคลัสเตอร์ | ❌ | ✅ `helm list -A` |
| ดูแลแอปต่อหลังติดตั้ง (backup, ซ่อม) | ❌ | ❌ (เป็นงานของ operator — หัวข้อ 16) |

Helm **ไม่ได้แทน** ความรู้เรื่อง Deployment/Service/Ingress ที่เรียนมา object ที่ Helm สร้างยังเป็น object เดิมทุกประการ ต่างแค่ว่ามันถูก "ห่อ" เป็นชุดที่มีชื่อและรุ่น

## 3. Helm คืออะไร

### 3.1 package manager ของ Kubernetes

<p align="center" id="fig-10">
  <img src="images/10-package-manager.png" alt="รูปที่ 10 Helm = package manager" width="900"><br>
  <em><b>รูปที่ 10</b> Helm = package manager ของ Kubernetes: chart เป็นแพ็กเกจ ติดตั้ง อัปเกรด ถอนออก ได้เป็นชุด</em>
</p>

ถ้าเคยใช้ `apt install nginx` หรือ `npm install express` จะคุ้นกับแนวคิดของ Helm ทันที

| package manager | แพ็กเกจ | ที่เก็บแพ็กเกจ | ติดตั้ง | ของที่ติดตั้งแล้ว |
|---|---|---|---|---|
| apt (Debian/Ubuntu) | `.deb` | apt repository | `apt install` | package ในเครื่อง |
| npm (Node.js) | package `.tgz` | npm registry | `npm install` | `node_modules/` |
| **Helm (Kubernetes)** | **chart `.tgz`** | **chart repository / OCI registry** | **`helm install`** | **release ในคลัสเตอร์** |

ต่างจาก apt ตรงที่แพ็กเกจหนึ่งติดตั้ง **ได้หลายครั้ง** ในคลัสเตอร์เดียว (คนละชื่อ release หรือคนละ namespace) เช่น chart `som-shop` ตัวเดียวเปิดเป็น release `som` ใน `som-dev` และ release `som` ใน `som-shop` พร้อมกันได้

### 3.2 ศัพท์หลัก 5 คำ

<p align="center" id="fig-11">
  <img src="images/11-five-words.png" alt="รูปที่ 11 ศัพท์หลัก 5 คำ" width="900"><br>
  <em><b>รูปที่ 11</b> ศัพท์หลัก 5 คำ: repository (ที่เก็บ) → chart (ชุด) + values (ใบสั่ง) → release (สาขาที่เปิดจริง) → revision (หน้าในสมุด)</em>
</p>

**ตารางที่ 3** ศัพท์หลักของ Helm

| ศัพท์ | ความหมาย | อุปมา | ตัวอย่างในบทนี้ |
|---|---|---|---|
| **chart** | โฟลเดอร์ (หรือไฟล์ `.tgz`) ที่มี template ของ object + ค่าเริ่มต้น + ข้อมูลรุ่น | ชุดแฟรนไชส์ | `charts/som-shop`, `podinfo/podinfo`, `traefik/traefik` |
| **values** | ค่าที่เติมลง template (ค่าเริ่มต้นใน `values.yaml` ทับด้วย `-f`/`--set`) | ใบสั่งปรับแต่งร้าน | `values-dev.yaml`, `--set web.image.tag=1.8` |
| **release** | chart + values ที่ติดตั้งจริงในคลัสเตอร์ ระบุด้วย **ชื่อ + namespace** | ร้านสาขาที่เปิดจริง | release `som` ใน `som-dev`, release `traefik` ใน `traefik` |
| **revision** | เลขรุ่นของ release เพิ่มขึ้นทุกครั้งที่ install/upgrade/rollback | หน้าในสมุดบันทึก | `REVISION: 1`, `Rollback to 2` |
| **repository** | ที่เก็บ chart (HTTP repo หรือ OCI registry) | แคตตาล็อก/โกดัง | `https://traefik.github.io/charts`, `oci://localhost:5000/charts` |

ประโยคเดียวที่สรุปทั้งหมด: *"Helm ดึง **chart** จาก **repository** มาเติม **values** แล้วติดตั้งเป็น **release** ที่มี **revision** ให้ย้อนได้"*

### 3.3 ประวัติ: Helm 2 → 3 → 4

<p align="center" id="fig-12">
  <img src="images/12-helm-history-tiller.png" alt="รูปที่ 12 ประวัติ Helm 2 → 3 → 4" width="900"><br>
  <em><b>รูปที่ 12</b> ประวัติ: Helm 2 มี Tiller ตัวกลางสิทธิ์สูงในคลัสเตอร์ (ถูกเอาออก), Helm 3 ทำงานจากเครื่องเราอย่างเดียว, Helm 4 ใช้ server-side apply</em>
</p>

| รุ่น | ลักษณะสำคัญ | เหตุผลที่ต้องรู้ |
|---|---|---|
| **Helm 2** | มี **Tiller** (Pod ในคลัสเตอร์) รับคำสั่งจาก helm บนเครื่องแล้วสร้าง object แทน มักได้สิทธิ์ cluster-admin | ใครคุยกับ Tiller ได้ = ทำอะไรก็ได้ในคลัสเตอร์ เป็นช่องโหว่ใหญ่ — บทความเก่าที่มี `helm init`/Tiller ใช้ไม่ได้แล้ว |
| **Helm 3** | ไม่มี Tiller helm คุยกับ kube-apiserver ด้วย **kubeconfig ของเราเอง** (สิทธิ์ตาม RBAC ของเรา บทที่ 11) เก็บ release เป็น Secret ใน namespace ของ release, chart `apiVersion: v2`, รองรับ OCI | ส่วนใหญ่ของบทความในเน็ตเป็น Helm 3 |
| **Helm 4** | ออกปลายปี 2568 (พฤศจิกายน 2025) ยังเป็น client-only ใช้ **server-side apply เป็นค่าเริ่มต้น**, เปลี่ยนชื่อ flag บางตัว, ระบบ plugin ใหม่ที่ตรวจที่มา, chart API ยังเป็น v2 (v3 ยังทดลอง) | บทนี้สอน Helm 4 (v4.3.0 ใน image `k8s-lab`) |

**Helm 3 หมดอายุแล้ว:** ตามประกาศของโครงการ Helm 3 ได้รับ bug fix ถึง 9 กันยายน 2569 (2026) และ security fix ถึง 10 กุมภาพันธ์ 2570 (2027) ณ วันที่เขียนบทนี้ (ตุลาคม 2569) Helm 3 จึงได้แต่ security fix แล้ว ระบบใหม่ควรเริ่มที่ Helm 4

ตรวจรุ่นในเครื่อง (ผลจริงจาก LAB 0)

```text
version.BuildInfo{Version:"v4.3.0", GitCommit:"bec5b06ed841fe5269972d864d5177944fd5970f", GitTreeState:"clean", GoVersion:"go1.27.1", KubeClientVersion:"v1.37"}
```

### 3.4 สิ่งที่เปลี่ยนใน Helm 4 ที่บทนี้ใช้

<p align="center" id="fig-13">
  <img src="images/13-helm4-whats-new.png" alt="รูปที่ 13 สิ่งที่เปลี่ยนใน Helm 4" width="900"><br>
  <em><b>รูปที่ 13</b> สิ่งที่เปลี่ยนใน Helm 4 ที่บทนี้ใช้: server-side apply เป็นค่าเริ่มต้น, --atomic → --rollback-on-failure, --force → --force-replace, plugin ต้องตรวจลายเซ็น, chart API ยังเป็น v2</em>
</p>

**ตารางที่ 4** Helm 3 (ที่เจอในบทความ) เทียบกับ Helm 4.3.0 (ที่ทดสอบจริงในบทนี้)

| หัวข้อ | Helm 3 | Helm 4.3.0 (ผลจริง) | อ่านต่อ |
|---|---|---|---|
| วิธี apply | client-side 3-way merge | **server-side apply** เป็นค่าเริ่มต้นตอน install (`--server-side` = `true`) ส่วน upgrade/rollback = `auto` (ใช้วิธีเดียวกับ revision ก่อน) `helm get metadata` แสดง `APPLY_METHOD: server-side apply` | หัวข้อ 9 |
| ย้อนเองเมื่อล้ม | `--atomic` | `--rollback-on-failure` (`--atomic` ยังรับ แต่ขึ้น `Flag --atomic has been deprecated, use --rollback-on-failure instead`) | หัวข้อ 8.4 |
| แทนที่ object | `--force` | `--force-replace` | หัวข้อ 9.4 |
| รับ object ที่มีอยู่แล้ว | ต้องติด label/annotation เอง | `--take-ownership` + (ถ้าชน) `--force-conflicts` | หัวข้อ 9.3 |
| `--wait` | bool ไม่ใส่ = ไม่รอเลย | `--wait` = รอแบบ `watcher` (kstatus) ไม่ใส่ = **`hookOnly`** (รอแค่ hook) ค่าอื่น `legacy` | หัวข้อ 8.3 |
| `--dry-run` | `--dry-run` เฉย ๆ ได้ | ระบุ `client` / `server` / `none` | หัวข้อ 7 |
| `helm list` | `-a/--all` แสดงทุกสถานะ | **ไม่มี `-a` แล้ว** (`Error: unknown shorthand flag: 'a' in -a`) `helm list` เฉย ๆ แสดงทุกสถานะ (เห็น `failed`, `uninstalled`) กรองด้วย `--deployed`/`--failed`/`--uninstalled` | หัวข้อ 8 |
| `helm registry login` | รับ URL ได้ | ต้องเป็น **ชื่อโฮสต์** (`localhost:5000`) ใส่ `http://...` ได้ `invalid registry` | หัวข้อ 13 |
| plugin | ติดตั้งจาก git ได้เลย | ตรวจที่มา ถ้าแหล่งไม่เซ็นต้อง `--verify=false` (`plugin source does not support verification`) และ post-renderer ต้องเป็น plugin | หัวข้อ 14 |
| chart API | v2 | ยัง **v2** (v3 ยังทดลอง `helm lint` ไม่ยอมรับ) | หัวข้อ 4 |
| `helm create` | ไม่มี httproute | scaffold มี `templates/httproute.yaml` (Gateway API) เพิ่ม | LAB 5 |

> **ถ้าเจอบทความ Helm 3:** คำสั่งส่วนใหญ่ (`install`, `upgrade`, `rollback`, `template`, `repo add`) ใช้ได้เหมือนเดิม ให้แปลง flag ตามตารางข้างบน และจำไว้ว่า Helm 4 ไม่ใส่ `--wait` = ไม่รอให้ Pod พร้อม (รอแค่ hook)

## 4. โครงสร้าง chart

### 4.1 ข้างในชุดแฟรนไชส์

<p align="center" id="fig-14">
  <img src="images/14-chart-anatomy.png" alt="รูปที่ 14 ข้างในชุดแฟรนไชส์" width="900"><br>
  <em><b>รูปที่ 14</b> ข้างในชุดแฟรนไชส์: Chart.yaml (ฉลาก), values.yaml (ใบสั่ง), templates/ (แม่พิมพ์), _helpers.tpl (ตรายาง), values.schema.json (ด่านตรวจ), NOTES.txt (การ์ดต้อนรับ)</em>
</p>

chart คือโฟลเดอร์ที่มีโครงตายตัว ตัวอย่างจากชุดร้านน้องส้มของบทนี้ (`02_LAB/charts/som-shop` ผลจาก `find charts -type f | sort` ใน LAB 7)

```text
charts/som-shop/.helmignore
charts/som-shop/Chart.yaml
charts/som-shop/templates/NOTES.txt
charts/som-shop/templates/_helpers.tpl
charts/som-shop/templates/configmap.yaml
charts/som-shop/templates/db.yaml
charts/som-shop/templates/hpa.yaml
charts/som-shop/templates/ingress.yaml
charts/som-shop/templates/secret.yaml
charts/som-shop/templates/seed-job.yaml
charts/som-shop/templates/tests/test-health.yaml
charts/som-shop/templates/web.yaml
charts/som-shop/values.schema.json
charts/som-shop/values.yaml
charts/values-dev.yaml
charts/values-prod.yaml
```

**ตารางที่ 5** ไฟล์และโฟลเดอร์ใน chart

| ไฟล์/โฟลเดอร์ | หน้าที่ | ในชุด som-shop |
|---|---|---|
| `Chart.yaml` | ฉลากของชุด: ชื่อ รุ่น appVersion ชนิด dependency | `som-shop` 0.1.0, appVersion `"1.7"` |
| `values.yaml` | ใบสั่งค่าเริ่มต้น (ทุกค่าที่ template อ่านได้ควรมีค่าเริ่มต้นที่นี่) | `shop.*`, `web.*`, `hpa.*`, `db.*`, `ingress.*`, `seed`, `tests` |
| `values.schema.json` | JSON Schema ตรวจ values ก่อน render (ไม่บังคับ) | replicas 1–6, tag ห้าม `1.4`, host pattern |
| `templates/*.yaml` | แม่พิมพ์ของ object (render แล้วต้องได้ YAML ของ Kubernetes) | configmap, secret, db, web, hpa, ingress, seed-job |
| `templates/_*.tpl` | ไฟล์ขึ้นต้นด้วย `_` **ไม่ถูก render เป็น object** ใช้เก็บ `define` | `_helpers.tpl` 4 ตรายาง |
| `templates/NOTES.txt` | ข้อความที่แสดงหลัง install/upgrade (render ด้วย template เหมือนกัน) | ชื่อร้าน revision image วิธีเปิดร้าน |
| `templates/tests/` | Pod/Job ที่มี annotation `helm.sh/hook: test` สำหรับ `helm test` | `test-health.yaml` |
| `charts/` | subchart (ชุดย่อย) ที่ดึงมาด้วย `helm dependency update` | ไม่มี (ดู umbrella chart ในหัวข้อ 12) |
| `crds/` | CustomResourceDefinition ที่ติดตั้งก่อน template (ดู 4.3) | ไม่มี (Traefik chart มี 25 ไฟล์) |
| `.helmignore` | ไฟล์ที่ไม่ต้องแพ็กเข้า `.tgz` (รูปแบบเหมือน `.gitignore`) | `.git/`, `*.tgz`, `*.swp`, `*~` |
| `Chart.lock` | ล็อกเวอร์ชัน dependency ที่ดึงจริง | ไม่มี |

### 4.2 Chart.yaml: version กับ appVersion

ไฟล์ `Chart.yaml` ของชุดร้าน (ของจริงใน `02_LAB/charts/som-shop/Chart.yaml`)

```yaml
# ชุดแฟรนไชส์ร้านอาหารแมวน้องส้ม (บท 014) — chart API v2 (Helm 3 และ Helm 4 ใช้ได้)
apiVersion: v2
name: som-shop
description: ร้านอาหารแมวน้องส้ม — หน้าร้าน Next.js + ครัว PostgreSQL + Ingress + HPA
type: application
version: 0.1.0          # เวอร์ชันของ chart (ชุดแฟรนไชส์) — แก้ทุกครั้งที่แก้ templates
appVersion: "1.7"       # เวอร์ชันแอปเริ่มต้น = tag ของ som-shop-web ถ้าไม่ได้ตั้ง web.image.tag
kubeVersion: ">=1.30.0-0"
keywords: [som-shop, kubernetes-lab]
```

<p align="center" id="fig-15">
  <img src="images/15-version-vs-appversion.png" alt="รูปที่ 15 version กับ appVersion" width="900"><br>
  <em><b>รูปที่ 15</b> Chart.yaml มี 2 เลข: version = รุ่นของชุดแฟรนไชส์ (แก้แม่พิมพ์ต้องเพิ่ม) / appVersion = รุ่นแอปในร้าน</em>
</p>

| field | ความหมาย | กติกา |
|---|---|---|
| `apiVersion` | รุ่นของรูปแบบ chart | Helm 3/4 ใช้ **`v2`** (`v1` = chart ยุค Helm 2 ยังติดตั้งได้ เช่น podinfo ยังเป็น `apiVersion: v1`) ส่วน `v3` ยังทดลอง: `helm lint` ของ 4.3.0 ตอบ `apiVersion 'v3' is not valid. The value must be either "v1" or "v2"` |
| `name` | ชื่อ chart | ตรงกับชื่อโฟลเดอร์ |
| `version` | **รุ่นของชุดแฟรนไชส์** (SemVer 2) | แก้ template/values ครั้งใดต้องเพิ่ม (0.1.0 → 0.1.1 → 0.2.0) repository ใช้เลขนี้แยกรุ่น |
| `appVersion` | **รุ่นของแอปข้างใน** (ข้อความอิสระ) | ใช้เป็นข้อมูลแสดงผล และ template มักใช้เป็น image tag เริ่มต้น |
| `type` | `application` (ติดตั้งได้) หรือ `library` (มีแต่ `define` ให้ chart อื่นใช้) | ค่าเริ่มต้น `application` |
| `kubeVersion` | ช่วงรุ่น Kubernetes ที่รองรับ | ถ้าคลัสเตอร์ไม่อยู่ในช่วง helm ปฏิเสธการติดตั้ง |
| `dependencies` | subchart | หัวข้อ 12 |

ข้อสังเกตที่เห็นจริงใน LAB 12: เราอัปเกรดหน้าร้านเป็น 1.8 ด้วย `--set web.image.tag=1.8` แต่ **คอลัมน์ `APP VERSION` ใน `helm history` และ `helm list` ยังเป็น `1.7` ทุกแถว** เพราะคอลัมน์นี้อ่านจาก `appVersion` ใน `Chart.yaml` ไม่ได้อ่าน image ที่ใช้จริง ถ้าต้องการให้ตรง ต้องออก chart รุ่นใหม่ (เช่น `version: 0.2.0`, `appVersion: "1.8"`)

### 4.3 โฟลเดอร์พิเศษ: charts/ และ crds/

<p align="center" id="fig-16">
  <img src="images/16-crds-and-subcharts.png" alt="รูปที่ 16 crds/ และ charts/" width="900"><br>
  <em><b>รูปที่ 16</b> โฟลเดอร์พิเศษ: charts/ = ชุดย่อยในชุดใหญ่ และ crds/ = แบบพิมพ์ชนิดใหม่ที่ติดตั้งครั้งแรกเท่านั้น (upgrade/uninstall ไม่แตะ)</em>
</p>

- **`charts/`** เก็บ subchart (ไฟล์ `.tgz` หรือโฟลเดอร์) ที่ chart นี้พึ่งพา ดูหัวข้อ 12
- **`crds/`** เก็บ CustomResourceDefinition (ชนิด object ใหม่ เช่น `Middleware` ของ Traefik บทที่ 12) Helm ติดตั้งไฟล์ในโฟลเดอร์นี้ **ก่อน** render template และมีกติกาพิเศษ
  1. ติดตั้งเฉพาะตอน **install ครั้งแรก** และ **ข้ามถ้ามี CRD ชื่อนั้นอยู่แล้ว** (LAB 10: CRD ของ Traefik 25 ตัวจากบท 012 ยังอยู่ chart จึงข้ามไป)
  2. **`helm upgrade` ไม่อัปเกรด CRD** และ **`helm uninstall` ไม่ลบ CRD** เพราะการลบ CRD จะลบ custom resource ทุกตัวของชนิดนั้นทั้งคลัสเตอร์ (เช่น Middleware ทุกตัวของทุกร้าน)
  3. ไฟล์ใน `crds/` ใช้ template ไม่ได้ (ถูกส่งเข้าไปตรง ๆ)
  4. ข้ามทั้งหมดได้ด้วย `--skip-crds` (เช่น ทีมดูแลคลัสเตอร์ติดตั้ง CRD เอง)

ผลที่ตามมา: อัปเกรด chart ที่มี CRD รุ่นใหม่ ต้องอ่านคู่มือของ chart ว่าต้อง apply CRD เองหรือไม่ (Traefik แนะนำให้ apply CRD ด้วย `kubectl` ก่อนอัปเกรดรุ่นใหญ่)

## 5. Go template และ Sprig ขั้นพื้นฐาน

### 5.1 แม่พิมพ์มีช่องว่าง {{ }}

<p align="center" id="fig-17">
  <img src="images/17-template-slots.png" alt="รูปที่ 17 แม่พิมพ์มีช่องว่าง" width="900"><br>
  <em><b>รูปที่ 17</b> แม่พิมพ์มีช่องว่าง {{ }} — เอาใบสั่ง (values) มาเติมช่อง ได้ป้ายร้านจริง</em>
</p>

ไฟล์ใน `templates/` คือ YAML ที่มี **ช่องว่าง** `{{ ... }}` ภาษาในช่องคือ **Go template** (ไลบรารี `text/template` ของภาษา Go) บวกฟังก์ชันจาก **Sprig** ราว 70+ ตัว (เช่น `default`, `quote`, `b64enc`, `sha256sum`) และฟังก์ชันของ Helm เอง (`include`, `required`, `lookup`, `toYaml`, `tpl`) ตัวอย่างแม่พิมพ์ Service หน้าร้าน (ส่วนท้ายของ `templates/web.yaml`)

```gotemplate
apiVersion: v1
kind: Service
metadata:
  name: {{ $fn }}-web
  labels:
    {{- include "som-shop.labels" . | nindent 4 }}
spec:
  type: ClusterIP
  selector:
    app: {{ $fn }}-web
  ports:
    - {name: http, port: 80, targetPort: http}
```

เมื่อ render ด้วย release ชื่อ `som` ช่องว่างทุกช่องถูกเติมจนได้ YAML จริง ตัวอย่างผล render ของแม่พิมพ์ ConfigMap จาก `helm template` ใน LAB 7

```text
---
# Source: som-shop/templates/configmap.yaml
# กระดานประกาศ 2 แผ่น: ป้ายร้าน (envFrom) + ประกาศหน้าร้าน (mount เป็นไฟล์)
apiVersion: v1
kind: ConfigMap
metadata:
  name: som-web-config
  labels:
    app.kubernetes.io/name: som-shop
    app.kubernetes.io/instance: som
    app.kubernetes.io/version: "1.7"
    app.kubernetes.io/managed-by: Helm
    helm.sh/chart: som-shop-0.1.0
data:
  APP_THEME: "harbor"
  SHOP_EYEBROW: "⚓ ท่าเรือ Kubernetes · Helm"
  SHOP_FOOTER: "Next.js + PostgreSQL · Kubernetes LAB 014 · ติดตั้งทั้งร้านด้วย Helm"
  SHOP_NAME: "ร้านอาหารแมวน้องส้ม"
  SHOP_PROMO: ""
```

บรรทัด `# Source:` บอกว่า object มาจากแม่พิมพ์ไฟล์ไหน (มีประโยชน์มากเวลา debug) และ label `app.kubernetes.io/managed-by: Helm` คือป้ายที่บอกว่า object นี้เป็นของ Helm

### 5.2 ของที่แม่พิมพ์หยิบได้ (built-in objects)

<p align="center" id="fig-18">
  <img src="images/18-built-in-objects.png" alt="รูปที่ 18 built-in objects" width="900"><br>
  <em><b>รูปที่ 18</b> ของที่แม่พิมพ์หยิบได้: .Values (ใบสั่ง), .Release (ข้อมูลสาขา), .Chart (ฉลากชุด), .Capabilities (ความสามารถของท่าเรือ)</em>
</p>

จุด `.` ในแม่พิมพ์คือ "ของทั้งหมดที่ส่งเข้ามา" (scope ปัจจุบัน) ที่ระดับบนสุดมี

**ตารางที่ 6** built-in objects ที่ใช้บ่อย

| object | ตัวอย่าง | ค่าจริงใน LAB |
|---|---|---|
| `.Values` | `.Values.web.image.tag` | ค่าจาก `values.yaml` + `-f` + `--set` |
| `.Release.Name` | ชื่อ release | `som`, `hello`, `oci-som` |
| `.Release.Namespace` | namespace ของ release | `som-dev`, `som-shop` |
| `.Release.Revision` | เลข revision ที่กำลังติดตั้ง | `1` ตอน install (NOTES แสดง `revision 1`) |
| `.Release.IsInstall` / `.IsUpgrade` | true/false ตามคำสั่ง | ใช้แยกพฤติกรรม install กับ upgrade |
| `.Release.Service` | ผู้ render | `Helm` (ไปเป็นค่าของ label `managed-by`) |
| `.Chart.Name` / `.Version` / `.AppVersion` | จาก `Chart.yaml` | `som-shop` / `0.1.0` / `1.7` |
| `.Capabilities.KubeVersion` | รุ่น Kubernetes ของคลัสเตอร์ | ใช้เลือก apiVersion ตามรุ่นคลัสเตอร์ |
| `.Capabilities.APIVersions.Has` | คลัสเตอร์มี API นี้ไหม | เช่น ตรวจว่ามี `traefik.io/v1alpha1` |
| `.Template.BasePath` / `.Template.Name` | path ของแม่พิมพ์ | ใช้ใน checksum (หัวข้อ 5.8) |
| `.Files` | อ่านไฟล์อื่นใน chart | เช่น `.Files.Get "config/app.conf"` |

ข้อควรระวัง: ภายใน `range` หรือ `with` จุด `.` จะเปลี่ยนไปชี้สิ่งที่วนอยู่ ถ้าต้องการกลับไปที่ระดับบนสุดให้ใช้ **`$`** (เช่น `$.Release.Name`, `$.Template.BasePath`)

### 5.3 pipeline, default และ quote

<p align="center" id="fig-19">
  <img src="images/19-pipeline-default.png" alt="รูปที่ 19 pipeline และ default" width="900"><br>
  <em><b>รูปที่ 19</b> pipeline: ค่าไหลผ่านฟังก์ชันทีละขั้น — ไม่ใส่ image tag ให้ใช้ appVersion ของ chart (default) แล้วใส่เครื่องหมายคำพูด (quote)</em>
</p>

เครื่องหมาย `|` ส่งผลของฝั่งซ้ายเป็น **อาร์กิวเมนต์ตัวสุดท้าย** ของฟังก์ชันฝั่งขวา (เหมือน pipe ของ shell) ตัวอย่างจาก `_helpers.tpl`

```gotemplate
app.kubernetes.io/version: {{ .Values.web.image.tag | default .Chart.AppVersion | quote }}
```

อ่านจากซ้ายไปขวา: เอา `web.image.tag` → ถ้าว่างใช้ `.Chart.AppVersion` แทน (`default "ค่าสำรอง" ค่า`) → ครอบด้วยเครื่องหมายคำพูด ผลจริง: ไม่ตั้ง tag ได้ `"1.7"`, `--set web.image.tag=1.8` ได้ `"1.8"`

ทำไมต้อง `quote`: YAML ตีความ `1.7` เป็นตัวเลข และ `true`, `yes`, `on` เป็น boolean ถ้า field ต้องการข้อความ (label, env value, ค่าใน ConfigMap) ต้องครอบคำพูด ไม่งั้น API server ปฏิเสธหรือค่าเพี้ยน (เช่น `1.10` กลายเป็น `1.1`)

ฟังก์ชันพื้นฐานอื่นที่ควรรู้

| ฟังก์ชัน | ใช้ทำอะไร | ตัวอย่าง |
|---|---|---|
| `quote` / `squote` | ครอบด้วย `"` / `'` | `{{ .Values.db.user \| quote }}` |
| `default` | ค่าสำรองเมื่อว่าง | `{{ default .Release.Name .Values.fullnameOverride }}` |
| `printf` | ประกอบข้อความ | `{{ printf "%s-%s" .Chart.Name .Chart.Version }}` |
| `trunc` / `trimSuffix` | ตัดให้สั้น (ชื่อ object ยาวไม่เกิน 63) | `{{ ... \| trunc 40 \| trimSuffix "-" }}` |
| `b64enc` / `b64dec` | base64 | ใช้กับ `data:` ของ Secret |
| `sha256sum` | ลายนิ้วมือของข้อความ | checksum annotation |
| `toYaml` / `toJson` | แปลง map/list เป็นข้อความ | `toYaml .Values.web.resources` |
| `tpl` | render ข้อความที่มี `{{ }}` ซึ่งมาจาก values | ให้ผู้ใช้ใส่ template ใน values ได้ |
| `index` | หยิบ key ที่มีจุดหรือขีด | `index $old.data "tls.crt"` |

### 5.4 toYaml | nindent และการตัดช่องว่าง

<p align="center" id="fig-20">
  <img src="images/20-nindent-vs-indent.png" alt="รูปที่ 20 nindent กับ indent" width="900"><br>
  <em><b>รูปที่ 20</b> toYaml | nindent ขึ้นบรรทัดใหม่และย่อหน้าตรง ส่วน indent ผิดที่ทำให้ YAML พัง (mapping values are not allowed)</em>
</p>

YAML ถือการย่อหน้าเป็นโครงสร้าง แม่พิมพ์ที่เอา map ทั้งก้อนจาก values มาวางจึงต้องคุมย่อหน้าเอง ใน `values.yaml` ของร้าน

```yaml
web:
  resources:
    requests: {cpu: 100m, memory: 192Mi}
    limits: {cpu: 500m, memory: 512Mi}
```

ใน `templates/web.yaml`

```gotemplate
          resources:
            {{- toYaml .Values.web.resources | nindent 12 }}
```

ผล render จริง (LAB 7)

```text
          resources:
            limits:
              cpu: 500m
              memory: 512Mi
            requests:
              cpu: 100m
              memory: 192Mi
```

- `toYaml` แปลง map เป็นข้อความ YAML (เรียง key ตามตัวอักษร: `limits` มาก่อน `requests`)
- `nindent 12` = **ขึ้นบรรทัดใหม่ (n = newline) แล้วย่อหน้าทุกบรรทัด 12 ช่อง**
- `{{-` (ขีดด้านซ้าย) = ตัดช่องว่าง/ขึ้นบรรทัดใหม่ **ก่อน** ช่องนี้ทิ้ง ส่วน `-}}` ตัดช่องว่าง **หลัง** ช่อง สองอย่างนี้ทำงานคู่กัน: `{{-` ตัดย่อหน้าที่เราพิมพ์เพื่อความสวยงาม แล้ว `nindent` ขึ้นบรรทัดและย่อหน้าใหม่ให้ตรง

ถ้าใช้ `indent` (ไม่ขึ้นบรรทัดใหม่) ผิดที่ ข้อความจะไปต่อท้ายบรรทัดก่อนหน้า ใน LAB 6 สคริปต์ `make-broken.sh` เปลี่ยน `nindent 8` เป็น `indent 2` ที่บรรทัด `podLabels` แล้วได้

```text
[ERROR] templates/deployment.yaml: unable to parse YAML: error converting YAML to JSON: yaml: line 24: mapping values are not allowed in this context
```

และ `helm template --debug` แสดง YAML ที่พังให้เห็นว่า label สองตัวมาอยู่บรรทัดเดียวกัน: `app.kubernetes.io/managed-by: Helm  shop: som`

### 5.5 โครงควบคุม: if / range / with

<p align="center" id="fig-21">
  <img src="images/21-if-range-with.png" alt="รูปที่ 21 if / range / with" width="900"><br>
  <em><b>รูปที่ 21</b> โครงควบคุม: if = มีหรือไม่มีชิ้นนี้, range = ทำซ้ำทุกการ์ด, with = เปลี่ยนจุดอ้างอิง</em>
</p>

**`if` / `else`** — ใส่หรือไม่ใส่ชิ้นส่วน ตัวอย่างสำคัญจาก `templates/web.yaml` ที่แก้กับดักของบท 013 (`replicas` ใน YAML ทับ HPA)

```gotemplate
spec:
  {{- if not .Values.hpa.enabled }}
  replicas: {{ .Values.web.replicas }}
  {{- end }}
```

ผลจริง (LAB 7): `hpa.enabled=false` → มีบรรทัด `replicas: 2`, `--set hpa.enabled=true` → บรรทัด `replicas:` หายไป HPA จึงเป็นผู้ดูแลจำนวนบูธคนเดียว ทั้งไฟล์ `hpa.yaml`, `db.yaml`, `ingress.yaml` และ `seed-job.yaml` ก็ครอบด้วย `if` ทั้งไฟล์ (เช่น `{{- if .Values.hpa.enabled }}`) ไม่เปิด = ไม่มี object นั้นเลย ค่าที่ถือว่า "เท็จ" ใน `if` คือ `false`, `0`, ข้อความว่าง, `nil`, list/map ว่าง

**`range`** — วนซ้ำ ใช้กับ list หรือ map ตัวอย่างจาก `templates/configmap.yaml` ที่สร้างการ์ดบนกระดานประกาศจากทุก key ใต้ `shop:`

```gotemplate
data:
  {{- range $key, $value := .Values.shop }}
  {{ $key }}: {{ $value | quote }}
  {{- end }}
```

`range` บน map วนตาม **key ที่เรียงตามตัวอักษร** ผล render จึงได้ `APP_THEME`, `SHOP_EYEBROW`, `SHOP_FOOTER`, `SHOP_NAME`, `SHOP_PROMO` ตามลำดับนี้เสมอ (ไม่ใช่ลำดับในไฟล์) ข้อดีคือผลเหมือนเดิมทุกครั้ง checksum จึงไม่เปลี่ยนมั่ว

**`with`** — เปลี่ยน `.` ให้ชี้ที่ค่าหนึ่ง และข้ามทั้งบล็อกถ้าค่านั้นว่าง scaffold ของ `helm create` (LAB 5) ใช้แบบนี้

```gotemplate
      {{- with .Values.podLabels }}
        {{- toYaml . | nindent 8 }}
      {{- end }}
```

ภายในบล็อก `.` คือ `.Values.podLabels` ถ้า `podLabels: {}` ทั้งบล็อกหายไป

**ตัวแปร** ประกาศด้วย `:=` ใช้เก็บค่าที่ใช้ซ้ำ เช่นบรรทัดแรกของ `web.yaml`: `{{- $fn := include "som-shop.fullname" . }}` แล้วใช้ `{{ $fn }}-web`, `{{ $fn }}-db-secret` ทั้งไฟล์

### 5.6 _helpers.tpl: ตรายางที่ใช้ซ้ำ

<p align="center" id="fig-22">
  <img src="images/22-helpers-include.png" alt="รูปที่ 22 _helpers.tpl ตรายาง" width="900"><br>
  <em><b>รูปที่ 22</b> _helpers.tpl = ตรายางที่ใช้ซ้ำ: define ครั้งเดียว include ได้ทุกไฟล์ (ชื่อ, label มาตรฐาน)</em>
</p>

`define` สร้าง template ย่อยที่มีชื่อ `include` เรียกใช้แล้วได้ **ข้อความ** กลับมา (จึงต่อ pipeline ได้ เช่น `| nindent 4`) ชุด som-shop มีตรายาง 4 อัน (ผล `grep -n define` ใน LAB 7: บรรทัด 4, 9, 18, 23)

```gotemplate
{{/* คำนำหน้าชื่อทุก object: fullnameOverride หรือชื่อ release (release som → som-web, som-db) */}}
{{- define "som-shop.fullname" -}}
{{- default .Release.Name .Values.fullnameOverride | trunc 40 | trimSuffix "-" -}}
{{- end -}}

{{/* ป้ายมาตรฐานที่ทุก object ควรมี */}}
{{- define "som-shop.labels" -}}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Values.web.image.tag | default .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version }}
{{- end -}}

{{/* image ของหน้าร้าน: tag ว่าง = appVersion ของ chart */}}
{{- define "som-shop.webImage" -}}
{{ .Values.web.image.repository }}:{{ .Values.web.image.tag | default .Chart.AppVersion }}
{{- end -}}
```

ทุกไฟล์เรียกด้วย `{{- include "som-shop.labels" . | nindent 4 }}` ส่ง `.` (ของทั้งหมด) เข้าไปให้ตรายางอ่าน

**ทำไมชื่อ object ใช้ชื่อ release:** release `som` ได้ `som-web`, `som-db`, `som-db-secret`, `som-web-config`, `som-announcement`, `som-tls` **ตรงกับชื่อในบทที่ 9–13 ทุกตัว** (รวม DNS `som-db-0.som-db`) จึง "รับร้านเดิม" เข้า Helm ได้ใน LAB 12 ส่วน `--set fullnameOverride=shop2` เปลี่ยนคำนำหน้าทุก object เป็น `shop2-*` (ผลจริง LAB 7: `shop2-announcement`, `shop2-db`, `shop2-db-secret`, `shop2-seed`, `shop2-test-health`, `shop2-web`, `shop2-web-config`)

> **`include` กับ `template`:** Go template มี action `{{ template "ชื่อ" . }}` อยู่แล้ว แต่ผลของมัน **ต่อ pipeline ไม่ได้** (ใส่ `| nindent 4` ไม่ได้) chart ของ Helm จึงใช้ `include` เสมอ

### 5.7 required และ lookup

<p align="center" id="fig-23">
  <img src="images/23-required-lookup.png" alt="รูปที่ 23 required และ lookup" width="900"><br>
  <em><b>รูปที่ 23</b> required = ช่องที่ห้ามว่าง (หยุดทันที), lookup = แอบดูของเดิมในคลัสเตอร์ (helm template มองไม่เห็น จึงได้ค่าว่าง)</em>
</p>

**`required "ข้อความ" ค่า`** — ถ้าค่าว่าง หยุด render ทันทีพร้อมข้อความที่เราเขียน (ดีกว่าปล่อยให้ร้านเปิดด้วยรหัสว่าง)

**`lookup "apiVersion" "Kind" "namespace" "name"`** — อ่าน object ที่มีอยู่จริงในคลัสเตอร์ระหว่าง render (คืน map ว่างถ้าไม่เจอ) ชุดร้านใช้สองตัวนี้ร่วมกันในตรายาง `som-shop.dbPassword`

```gotemplate
{{/* รหัสฐานข้อมูล: --set db.password > Secret เดิมในคลัสเตอร์ (lookup) > error (required) */}}
{{- define "som-shop.dbPassword" -}}
{{- $old := lookup "v1" "Secret" .Release.Namespace (printf "%s-db-secret" (include "som-shop.fullname" .)) -}}
{{- if .Values.db.password -}}
{{- .Values.db.password -}}
{{- else if $old -}}
{{- index $old.data "POSTGRES_PASSWORD" | b64dec -}}
{{- else -}}
{{- required "ติดตั้งครั้งแรกต้องตั้งรหัสฐานข้อมูล: --set db.password=<รหัส>" .Values.db.password -}}
{{- end -}}
{{- end -}}
```

ลำดับการเลือกรหัส: (1) ส่งมาด้วย `--set db.password` ใช้ค่านั้น (2) ไม่ส่ง แต่มี Secret `som-db-secret` เดิมในคลัสเตอร์ ใช้รหัสเดิม (3) ไม่มีทั้งคู่ หยุดด้วยข้อความภาษาไทย ผลจริง

- ติดตั้งครั้งแรกโดยไม่ใส่รหัส: `Error: execution error at (som-shop/templates/web.yaml:29:28): ติดตั้งครั้งแรกต้องตั้งรหัสฐานข้อมูล: --set db.password=<รหัส>`
- `helm upgrade` สาขา dev โดยไม่ส่งรหัส (LAB 9): Secret ยังเป็นรหัสเดิม
- **รับร้านเดิม** (LAB 12) ไม่ต้อง `--set db.password` เลย chart อ่านรหัสจาก Secret ที่บท 011 สร้างไว้

แม่พิมพ์ ingress ใช้แนวเดียวกันกับใบรับรอง TLS: ถ้ามี Secret `som-tls` อยู่แล้วใช้ใบเดิม ถ้าไม่มีสร้างใหม่ด้วย `genSelfSignedCert` (เฉพาะ LAB) ผลจริงใน LAB 12: fingerprint ของ `som-tls` ก่อนและหลังรับร้านเป็นค่าเดียวกัน (`DF:E2:AD:87:…` ใบจากบท 012 ที่มี SAN รวม `admin.localhost`) หลังร้าน `admin.localhost` ที่ใช้ใบเดียวกันจึงไม่พัง

> **กับดักของ lookup:** `lookup` ทำงานเฉพาะตอนที่ helm **คุยกับคลัสเตอร์** (install, upgrade, `--dry-run=server`) ส่วน `helm template` และ `helm lint` ไม่ต่อคลัสเตอร์ `lookup` จึงคืนค่าว่างเสมอ ผลจริงใน LAB 8: `helm template` ไม่ใส่รหัส → error ของ `required` แม้คลัสเตอร์จะมี Secret อยู่แล้ว และ `helm template` 2 ครั้งได้ใบรับรองคนละใบ (fingerprint `95:82:4B:…` กับ `46:94:7E:…`) เพราะ `genSelfSignedCert` สุ่มใหม่ทุกครั้ง — ถ้าไม่มี lookup ทุก `helm upgrade` จะได้ใบรับรองใหม่ (และฟังก์ชันสุ่มอย่าง `randAlphaNum` ก็จะได้รหัสใหม่ทุกครั้ง ร้านจะ login db ไม่ได้) เครื่องมือที่ render ด้วย `helm template` อย่าง Argo CD ก็เจอข้อจำกัดเดียวกัน (หัวข้อ 16)

`helm lint` ที่ไม่ใส่รหัสจะแจ้งเตือนแต่ไม่ล้ม (เพราะไม่ต่อคลัสเตอร์จึงตัดสินไม่ได้)

```text
level=WARN msg="missing required values" message="ติดตั้งครั้งแรกต้องตั้งรหัสฐานข้อมูล: --set db.password=<รหัส>"
level=WARN msg="missing required values" message="ติดตั้งครั้งแรกต้องตั้งรหัสฐานข้อมูล: --set db.password=<รหัส>"
==> Linting charts/som-shop
[INFO] Chart.yaml: icon is recommended

1 chart(s) linted, 0 chart(s) failed
```

### 5.8 checksum/config: Pod ใหม่เกิดเองเมื่อ config เปลี่ยน

<p align="center" id="fig-24">
  <img src="images/24-checksum-rollout.png" alt="รูปที่ 24 checksum/config" width="900"><br>
  <em><b>รูปที่ 24</b> checksum/config: แก้กระดานประกาศแล้วลายนิ้วมือเปลี่ยน → ได้บูธใหม่เอง ไม่ต้อง rollout restart แบบบท 010</em>
</p>

บทที่ 10 เราเรียนว่า Pod ที่อ่าน ConfigMap ผ่าน `envFrom` **ไม่เห็นค่าใหม่** จนกว่าจะเกิดใหม่ จึงต้อง `kubectl rollout restart` เอง Helm มี pattern ที่แก้ปัญหานี้: ใส่ "ลายนิ้วมือ" ของ ConfigMap/Secret ไว้ใน annotation ของ **Pod template**

```gotemplate
  template:
    metadata:
      labels:
        app: {{ $fn }}-web
      annotations:
        # แก้กระดานประกาศ/ซอง → ค่า checksum เปลี่ยน → ได้ Pod ใหม่เอง (ไม่ต้อง rollout restart)
        checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}
        checksum/secret: {{ include (print $.Template.BasePath "/secret.yaml") . | sha256sum }}
```

`include (print $.Template.BasePath "/configmap.yaml") .` render แม่พิมพ์ ConfigMap ทั้งไฟล์เป็นข้อความ แล้ว `sha256sum` ย่อเป็นลายนิ้วมือ เมื่อค่าใน `shop.*` หรือ `announcement` เปลี่ยน ลายนิ้วมือเปลี่ยน → Pod template เปลี่ยน → Deployment ทำ rolling update ให้เอง ผลจริง

- LAB 7: `checksum/config: 26b21079…` → `--set shop.SHOP_PROMO="ลด 50%"` → `25db4af1…`
- LAB 9: `helm upgrade ... --set announcement="ปลาแซลมอนมาแล้ว 🍣"` (9.7 วินาที) ได้ Pod ใหม่ `som-web-574cd55f96-…` และ `/api/announcement` ตอบข้อความใหม่ทันที

> **ข้อแลกเปลี่ยน:** checksum ของ Secret ทำให้ "เปลี่ยนรหัส = Pod เกิดใหม่ทุกตัว" ซึ่งมักเป็นสิ่งที่ต้องการ แต่ถ้า ConfigMap ใหญ่และเปลี่ยนบ่อย Pod จะถูก restart บ่อยตาม ควรเลือกใส่เฉพาะ config ที่แอปอ่านตอนเริ่มเท่านั้น

## 6. values และลำดับความสำคัญ

### 6.1 ใบสั่งหลายชั้น: ใครชนะ

<p align="center" id="fig-25">
  <img src="images/25-values-precedence.png" alt="รูปที่ 25 ลำดับความสำคัญของ values" width="900"><br>
  <em><b>รูปที่ 25</b> ลำดับความสำคัญ: values.yaml ในชุด &lt; ไฟล์ -f (ไฟล์หลังชนะ) &lt; --set (บนสุดชนะ)</em>
</p>

Helm รวม values จากหลายแหล่งเป็นก้อนเดียวก่อน render จากต่ำไปสูง (ค่าที่อยู่สูงกว่าทับค่าที่ต่ำกว่า)

1. `values.yaml` ใน chart (ค่าเริ่มต้น)
2. ค่าที่ parent chart ส่งให้ subchart (ถ้าเป็น subchart — หัวข้อ 12)
3. ไฟล์ที่ส่งด้วย `-f`/`--values` **ตามลำดับที่เขียน ไฟล์หลังชนะไฟล์หน้า** (`-f base.yaml -f prod.yaml`)
4. `--set`, `--set-string`, `--set-file`, `--set-json`, `--set-literal` บนบรรทัดคำสั่ง (ชนะทุกอย่าง และตัวหลังชนะตัวหน้า)

ผลจริงจาก LAB 3: ไฟล์ `labs/lab03-values/podinfo-values.yaml` ตั้ง `ui.message: "ร้านน้องส้มสาขา values file"` แต่สั่ง

```bash
helm upgrade hello podinfo/podinfo --version 6.15.0 -n helm-demo \
  -f labs/lab03-values/podinfo-values.yaml --set ui.message="--set ชนะ" --wait
```

podinfo ตอบ `"message": "--set ชนะ"` และ `"color": "#ff8c00"` (สีมาจากไฟล์เพราะ `--set` ไม่ได้แตะ)

**ตารางที่ 7** รูปแบบของ `--set`

| รูปแบบ | ผล | หมายเหตุ |
|---|---|---|
| `--set web.replicas=3` | `web: {replicas: 3}` | จุด = ลงไปใน map |
| `--set a=1,b=2` | หลายค่าในครั้งเดียว | จุลภาคคั่น (ค่าที่มีจุลภาคต้อง escape `\,`) |
| `--set web.image.tag=1.8` | `"1.8"`? **ไม่แน่** | `--set` เดาชนิด: `1.8` อาจเป็นตัวเลข ใน chart ร้าน template ครอบ `quote` จึงปลอดภัย |
| `--set-string web.image.tag=1.10` | บังคับเป็นข้อความ `"1.10"` | ใช้กับ tag ที่เป็นตัวเลขเสมอ (กัน `1.10` → `1.1`) |
| `--set args[0]=--kubelet-insecure-tls` | ตั้งสมาชิกใน list | ระวัง: list ถูกแทนทั้งก้อน (6.2) |
| `--set-file key=path` | อ่านค่าจากไฟล์ | เช่น ใส่ไฟล์ประกาศทั้งไฟล์ |
| `--set-json 'web.resources={"requests":{"cpu":"200m"}}'` | ใส่ค่า JSON ทั้งก้อน | |
| `--set key=null` | ลบ key ที่มาจากค่าเริ่มต้น | ใช้ปิดค่าเริ่มต้นของ chart |

### 6.2 การ merge: map รวมกัน list แทนทั้งก้อน

- **map รวมกันทีละ key**: ไฟล์ dev ตั้งแค่ `web.replicas: 1` ค่า `web.image.repository` และ `web.resources` จาก `values.yaml` ยังอยู่ครบ
- **list ถูกแทนทั้งก้อน**: ถ้าค่าเริ่มต้นมี `args: [a, b]` แล้ว `-f` ส่ง `args: [c]` ผลคือ `[c]` (ไม่ใช่ `[a, b, c]`) เหตุนี้ `metrics-server-values.yaml` ใน LAB 10 ต้องเขียน args ที่ต้องการครบชุด
- `--set key=null` ลบ key ทิ้ง

ดูค่าที่ release ใช้จริงได้สองแบบ (LAB 2–3)

```bash
helm get values hello -n helm-demo         # เฉพาะค่าที่เราส่ง (USER-SUPPLIED VALUES)
helm get values hello -n helm-demo --all   # ค่าทั้งหมดหลัง merge กับค่าเริ่มต้น
```

### 6.3 ใบสั่งต่อ environment

<p align="center" id="fig-26">
  <img src="images/26-values-per-env.png" alt="รูปที่ 26 ใบสั่งต่อ environment" width="900"><br>
  <em><b>รูปที่ 26</b> ชุดแฟรนไชส์เดียว + ใบสั่งคนละใบ = สาขา dev (บูธเดียว) และ prod (HPA + HTTPS)</em>
</p>

แทนการ copy โฟลเดอร์ เราเก็บ **chart เดียว** และ **ใบสั่งคนละใบ** ที่มีเฉพาะส่วนที่ต่าง (ไฟล์จริงใน `02_LAB/charts/`)

```yaml
# values-dev.yaml — สาขาทดลอง (dev): บูธเดียว ไม่มี HPA ประตู http ธรรมดา ธีมส้ม
shop:
  SHOP_NAME: "ร้านอาหารแมวน้องส้ม (dev)"
  APP_THEME: "sunset"
  SHOP_PROMO: "🧪 สาขาทดลอง — ของจริงอยู่ที่ shop.localhost"
web:
  replicas: 1
hpa:
  enabled: false
ingress:
  enabled: true
  host: dev.shop.localhost
  tls: false
```

```yaml
# values-prod.yaml — สาขาจริง (prod): HPA 2–6 บูธ ประตู HTTPS shop.localhost
shop:
  SHOP_NAME: "ร้านอาหารแมวน้องส้ม"
  APP_THEME: "harbor"
  SHOP_PROMO: "🎉 เปิดสาขาใหม่ด้วย Helm คำสั่งเดียว"
hpa:
  enabled: true
  minReplicas: 2
  maxReplicas: 6
ingress:
  enabled: true
  host: shop.localhost
  tls: true
```

ผล render (LAB 8) นับ object ที่ได้

| ใบสั่ง | จำนวน `kind:` | ชนิด |
|---|:---:|---|
| dev | **10** | ConfigMap 2, Deployment, Ingress, Job (hook seed), Pod (test), Secret, Service 2, StatefulSet |
| prod | **13** | dev + HorizontalPodAutoscaler + Middleware (redirect https) + Secret ที่ 2 (`som-tls`) |

(ถ้าไม่นับ Job hook และ Pod test ที่ไม่ใช่ส่วนของร้านปกติ = 8 และ 11 object) ทุกการแก้ไขแม่พิมพ์ไปถึงทั้งสองสาขาพร้อมกัน drift จึงเหลือเฉพาะสิ่งที่ตั้งใจให้ต่างในใบสั่ง

### 6.4 กับดัก: upgrade ที่ส่งค่ามาแค่บางตัว

<p align="center" id="fig-27">
  <img src="images/27-upgrade-values-trap.png" alt="รูปที่ 27 กับดัก upgrade ส่งค่าบางตัว" width="900"><br>
  <em><b>รูปที่ 27</b> กับดัก: helm upgrade ที่ส่งค่ามาแค่บางตัว (เช่น --set อย่างเดียว) = ค่าอื่นที่เคยตั้งกลับเป็นค่าเริ่มต้นของชุด ส่วน upgrade ที่ไม่ส่งค่าเลยจะใช้ค่าเดิมต่อ — ปลอดภัยสุดคือส่ง -f ทุกครั้ง หรือใช้ --reuse-values</em>
</p>

`helm upgrade` **ไม่ได้** "แก้เฉพาะค่าที่ส่งมา" ทับค่าของ revision ก่อน แต่คำนวณ values ใหม่จาก **ค่าเริ่มต้นของ chart + สิ่งที่ส่งมาในคำสั่งนี้** กติกาที่ทดสอบจริงกับ Helm 4.3.0

| คำสั่ง upgrade | values ที่ได้ | ผลจริง |
|---|---|---|
| ส่ง `-f` (และ/หรือ `--set`) ครบ | ค่าเริ่มต้น + สิ่งที่ส่ง | ปกติ (rev 2, 4 ใน LAB 3) |
| **ส่งแค่ `--set` บางค่า** (ไม่ส่ง `-f`) | ค่าเริ่มต้น + `--set` นั้น **ค่าอื่นที่เคยตั้งหายหมด** | rev 3: `helm get values` เหลือ `replicaCount: 1` อย่างเดียว Ingress หาย `curl` ได้ `404` |
| **ไม่ส่งค่าอะไรเลย** | Helm ใช้ค่าของ revision ก่อนต่อ (reuse) | values ยังครบ (ทดสอบในรอบสำรวจของ LAB 3) |
| `--reuse-values --set x=y` | ค่าของ revision ก่อน + `--set` ใหม่ | rev 5: `replicaCount: 3`, สี และ Ingress อยู่ครบ message เปลี่ยน |
| `--reset-then-reuse-values --set x=y` | ค่าเริ่มต้น **ของ chart รุ่นใหม่** + ค่าเดิม + `--set` | ใช้ตอนอัปเกรด chart รุ่นใหม่ที่เพิ่ม key ใหม่ (`--reuse-values` จะไม่เห็น key ใหม่) |

ผลของ rev 3 (ส่ง `--set replicaCount=1` อย่างเดียว) ใน LAB 3

```text
helm get values hello -n helm-demo
USER-SUPPLIED VALUES:
replicaCount: 1
kubectl -n helm-demo get deploy,ing
NAME                            READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/hello-podinfo   1/1     1            1           43s
curl -s -o /dev/null -w "%{http_code}\n" http://podinfo.localhost:30080
404
```

**กติกาที่บทนี้ใช้:** ทุกคำสั่ง upgrade ส่งใบสั่ง `-f` ของสาขานั้นทุกครั้ง (เช่น `-f charts/values-prod.yaml --set web.image.tag=1.8`) ใบสั่งจึงอยู่ในไฟล์ที่ commit ได้ ไม่ใช่ "ในความจำของ release" ส่วน `--reuse-values` ใช้ได้เมื่อรู้ว่าไม่ได้เปลี่ยนรุ่น chart

### 6.5 values.schema.json: ด่านตรวจใบสั่ง

<p align="center" id="fig-28">
  <img src="images/28-schema-desk.png" alt="รูปที่ 28 values.schema.json ด่านตรวจใบสั่ง" width="900"><br>
  <em><b>รูปที่ 28</b> values.schema.json = ด่านตรวจใบสั่ง: ค่าผิดชนิด/เกินช่วงถูกปฏิเสธก่อนสร้างอะไรเลย (เช่น replicas 9 เกิน 6, tag 1.4)</em>
</p>

ถ้า chart มีไฟล์ `values.schema.json` (JSON Schema) Helm ตรวจ values ที่ merge แล้ว **ก่อน render** ทุกคำสั่ง (`install`, `upgrade`, `template`, `lint`) ค่าที่ผิดกติกาจะไม่ไปถึงคลัสเตอร์เลย ส่วนหนึ่งของด่านตรวจร้าน

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "som-shop values",
  "type": "object",
  "properties": {
    "web": {
      "type": "object",
      "properties": {
        "replicas": {"type": "integer", "minimum": 1, "maximum": 6},
        "image": {
          "type": "object",
          "properties": {
            "repository": {"type": "string", "minLength": 1},
            "tag": {"type": "string", "not": {"const": "1.4"}}
          }
        }
      }
    }
  }
}
```

ผลจริง (LAB 8)

```text
helm template som charts/som-shop --set db.password=x --set web.image.tag=1.4
Error: values don't meet the specifications of the schema(s) in the following chart(s):
som-shop:
- at '/web/image/tag': 'not' failed

helm template som charts/som-shop --set db.password=x --set web.replicas=9
Error: values don't meet the specifications of the schema(s) in the following chart(s):
som-shop:
- at '/web/replicas': maximum: got 9, want 6

helm template som charts/som-shop --set db.password=x --set ingress.host=Shop_Localhost
Error: values don't meet the specifications of the schema(s) in the following chart(s):
som-shop:
- at '/ingress/host': 'Shop_Localhost' does not match pattern '^[a-z0-9.-]+$'
```

ทำไมห้าม tag `1.4`: บทที่ 7 เราสร้าง `som-shop-web:1.4` เป็น "รุ่นพัง" ไว้ฝึก rollout undo ด่านตรวจจึงกันไม่ให้ใครเผลอส่งรุ่นนี้ขึ้นร้าน chart ภายนอกหลายตัวก็มี schema เช่น Traefik chart 41.6.1 ปฏิเสธ key ที่ไม่มีอยู่จริง (`--set logs.access.enabled=true` → `- at '': additional properties 'logs' not allowed`) ช่วยจับการพิมพ์ key ผิดที่ปกติจะ "เงียบ" (ค่าถูกเพิกเฉย)

> schema ตรวจได้แค่ "รูปร่าง" ของค่า (ชนิด ช่วง รูปแบบ) ตรวจไม่ได้ว่า image มีอยู่จริงหรือรหัสถูกต้อง สิ่งเหล่านั้นต้องอาศัย `--wait` และ `helm test`

## 7. การ render และ debug

### 7.1 เครื่องมือ 4 ระดับ

<p align="center" id="fig-29">
  <img src="images/29-render-table.png" alt="รูปที่ 29 template / lint / dry-run" width="900"><br>
  <em><b>รูปที่ 29</b> helm template = พิมพ์พิมพ์เขียวออกมาดูโดยไม่สร้างจริง, helm lint = ตรวจชุด, --dry-run=server = ลองกับท่าเรือจริงแต่ไม่บันทึก</em>
</p>

**ตารางที่ 8** เครื่องมือตรวจ chart

| คำสั่ง | ต่อคลัสเตอร์? | ทำอะไร | จับอะไรได้ | จับอะไรไม่ได้ |
|---|:---:|---|---|---|
| `helm lint <chart>` | ไม่ | render + ตรวจรูปแบบ chart และ YAML | YAML พัง, ฟังก์ชันไม่มี, `Chart.yaml` ผิด, schema | ค่าที่ API server ไม่ยอมรับ, `required` (แค่ WARN) |
| `helm template <name> <chart>` | ไม่ | render แล้วพิมพ์ manifest ออก stdout | เหมือน lint + เห็นผลจริงทุกบรรทัด (`--show-only templates/x.yaml` ดูไฟล์เดียว) | `lookup` (ได้ค่าว่าง), field ผิดของ Kubernetes |
| `helm install/upgrade --dry-run=client` | ไม่ | เหมือน template แต่แสดงในรูปผลของ install (NOTES, HOOKS) | เหมือน template | เหมือน template |
| `helm install/upgrade --dry-run=server` | ใช่ | render โดย `lookup` เห็นคลัสเตอร์ ตรวจ ownership | lookup, ชื่อชน | **field ผิดของ object (ดูกับดักข้างล่าง)** |
| `helm template ... \| kubectl apply --dry-run=server -f -` | ใช่ | ส่ง manifest ให้ API server ตรวจจริงแต่ไม่บันทึก | field ผิด, ค่าไม่อยู่ในชุดที่อนุญาต, admission | `lookup` (มาจาก template) |
| `--debug` | — | เพิ่มรายละเอียด และพิมพ์ YAML ที่พังให้ดู | ช่วยหาบรรทัดที่ผิด | — |

**กับดักที่เจอจริงใน Helm 4.3.0:** `--dry-run=server` **ไม่** ส่ง object ไปให้ API server ตรวจแบบ server-side dry run ใน LAB 6 ตั้ง `service.type=NodePortt` (พิมพ์ผิด) แล้ว

```text
helm install web2 ../lab05-first/mychart -n first --dry-run=server --set service.type=NodePortt
NAME: web2
...
STATUS: pending-install
REVISION: 1
DESCRIPTION: Dry run complete
```

ผ่านทั้งที่ค่าใช้ไม่ได้ แต่ส่ง manifest เดียวกันให้ `kubectl` ตรวจ

```text
helm template web2 ../lab05-first/mychart --set service.type=NodePortt | kubectl apply --dry-run=server -n first -f -
deployment.apps/web2-mychart created (server dry run)
pod/web2-mychart-test-connection created (server dry run)
The Service "web2-mychart" is invalid: spec.type: Unsupported value: "NodePortt": supported values: "ClusterIP", "ExternalName", "LoadBalancer", "NodePort"
```

และถ้าติดตั้งจริงจะล้มพร้อม **ทิ้ง release สถานะ `failed`** ไว้ (`web2 ... failed`) ต้อง `helm uninstall web2` เอง ข้อสรุป: ก่อนติดตั้งของสำคัญให้ตรวจสองชั้น — `helm lint`/`template` (รูปแบบ chart) แล้ว `helm template | kubectl apply --dry-run=server -f -` (ความถูกต้องของ object)

### 7.2 error ที่เจอบ่อย 4 แบบ

<p align="center" id="fig-30">
  <img src="images/30-common-errors.png" alt="รูปที่ 30 error ที่เจอบ่อย 4 แบบ" width="900"><br>
  <em><b>รูปที่ 30</b> error ที่เจอบ่อย 4 แบบ: YAML parse error (ย่อหน้า), function not defined (สะกดฟังก์ชันผิด), required (ลืมค่า), schema (ค่าผิดกติกา)</em>
</p>

**ตารางที่ 9** อ่าน error ของ Helm (ข้อความจริงจาก LAB 6 และ LAB 8)

| แบบ | ข้อความจริง | อ่านว่า | แก้ |
|---|---|---|---|
| YAML parse (ย่อหน้า) | `[ERROR] templates/deployment.yaml: unable to parse YAML: error converting YAML to JSON: yaml: line 24: mapping values are not allowed in this context` | render ได้ แต่ผลไม่ใช่ YAML ที่ถูก **"line 24" คือบรรทัดของผล render ไม่ใช่ของไฟล์ template** | `helm template --debug` ดูผลที่พัง มักเป็น `indent`/`nindent` หรือ `{{-` ตัดบรรทัดเกิน |
| function not defined | `[ERROR] templates/: parse error at (mychart/templates/deployment.yaml:18): function "toYml" not defined` | template parse ไม่ผ่าน (บรรทัด 18 ของไฟล์ template) | สะกดฟังก์ชันให้ถูก (`toYaml`) |
| required | `Error: execution error at (mychart/templates/deployment.yaml:41:21): ต้องใส่ image.repository` | `required` หยุด render ที่บรรทัด:คอลัมน์ | ส่งค่านั้นมา |
| schema | `- at '/web/replicas': maximum: got 9, want 6` | values ผิด schema (ยังไม่ render) | แก้ค่าในใบสั่ง |

อีกแบบที่ควรรู้: chart ที่ใช้ `apiVersion: v3` (ยังทดลอง) ได้ `[ERROR] Chart.yaml: chart type is not valid in apiVersion 'v3'. It is valid in apiVersion 'v2'` ถ้ามีบรรทัด `type:` และ `apiVersion 'v3' is not valid. The value must be either "v1" or "v2"` ถ้าไม่มี ส่วน `helm template` ตอบสั้น ๆ `Error: invalid chart apiVersion` (ทั้งมีและไม่มี `HELM_EXPERIMENTAL_CHART_V3=1`)

## 8. lifecycle ของ release

### 8.1 วงจรชีวิตสาขา

<p align="center" id="fig-31">
  <img src="images/31-lifecycle-cycle.png" alt="รูปที่ 31 วงจรชีวิตสาขา" width="900"><br>
  <em><b>รูปที่ 31</b> วงจรชีวิตสาขา: install → upgrade → rollback → uninstall ทุกครั้ง (ยกเว้น uninstall) เขียนหน้าใหม่ในสมุด</em>
</p>

**ตารางที่ 10** คำสั่งหลักของ lifecycle

| คำสั่ง | ทำอะไร | revision | ข้อสังเกต |
|---|---|---|---|
| `helm install <name> <chart>` | ติดตั้งครั้งแรก | 1 | ชื่อซ้ำกับ release ที่ยังอยู่ (รวม `uninstalled` ที่ keep-history) → `cannot reuse a name that is still in use` |
| `helm upgrade <name> <chart>` | render ใหม่แล้ว apply ความต่าง ลบ object ที่ chart ใหม่ไม่มีแล้ว | +1 | upgrade release ที่ `failed` ได้ (ใช้แก้ release ที่ล้ม) |
| `helm upgrade --install` | ถ้ายังไม่มี install ถ้ามีแล้ว upgrade | 1 หรือ +1 | idempotent เหมาะกับ script/CI (สั่งซ้ำได้) |
| `helm rollback <name> <rev>` | ใช้ manifest + values ของ revision นั้น apply อีกครั้ง | **+1 (ไม่ถอยเลข)** | description `Rollback to <rev>` |
| `helm uninstall <name>` | ลบทุก object ของ release + ลบประวัติ | — | ไม่ลบ PVC ที่เกิดจาก `volumeClaimTemplates`, CRD และ hook resource |
| `helm uninstall --keep-history` | ลบ object แต่เก็บประวัติ | สถานะ `uninstalled` | `helm rollback` กลับมาได้ |
| `helm history <name>` | ดูสมุด | — | เก็บ 10 รุ่นล่าสุด (`HELM_MAX_HISTORY`/`--history-max`) |
| `helm list` / `-A` | ดู release ใน namespace / ทุก namespace | — | Helm 4 ไม่มี `-a` แล้ว |
| `helm status <name>` | สถานะ + NOTES | — | |
| `helm get values/manifest/notes/metadata/hooks/all` | ดูข้อมูลของ revision (`--revision N`) | — | `metadata` บอก `APPLY_METHOD` |

สถานะของ revision ที่จะเห็นใน `helm history`/`helm list`: `pending-install`, `pending-upgrade`, `pending-rollback` (กำลังทำ), `deployed` (รุ่นปัจจุบัน มีได้ตัวเดียว), `superseded` (รุ่นเก่าที่ถูกแทน), `failed` (ล้ม), `uninstalled` (ลบแล้วแต่เก็บประวัติ)

> ถ้า helm ถูกขัดจังหวะ (กด Ctrl+C, เครือข่ายหลุด) ระหว่าง `pending-*` คำสั่งถัดไปอาจได้ `another operation (install/upgrade/rollback) is in progress` ให้ดู `helm history` แล้ว rollback ไปรุ่นที่ดีล่าสุด

### 8.2 rollback = เขียนหน้าใหม่ ไม่ใช่ถอยหน้า

<p align="center" id="fig-32">
  <img src="images/32-revision-logbook.png" alt="รูปที่ 32 rollback เขียนหน้าใหม่" width="900"><br>
  <em><b>รูปที่ 32</b> rollback ไม่ได้ถอยเลขหน้า แต่เขียนหน้าใหม่ที่คัดลอกจากหน้าเก่า (เลข revision เพิ่มขึ้นเสมอ)</em>
</p>

ผลจริง LAB 4 (podinfo): rev 6 ตั้ง image ผิด → `helm rollback hello 5 --wait` (11.9 วินาที) ได้ **rev 7** ไม่ใช่กลับไปเป็น rev 5

```text
6       	Tue Oct  6 05:50:32 2026	superseded	podinfo-6.15.0	6.15.0     	Upgrade complete
7       	Tue Oct  6 05:50:48 2026	deployed  	podinfo-6.15.0	6.15.0     	Rollback to 5
```

ข้อดีของการเขียนหน้าใหม่: สมุดเป็นบันทึกเหตุการณ์ที่ไม่ถูกลบย้อนหลัง เห็นว่า "เคยขึ้น rev 6 แล้วถอย" ซึ่งเป็นข้อมูลสำคัญเวลาหาสาเหตุปัญหา

### 8.3 --wait: Helm 4 ไม่รอถ้าไม่สั่ง

<p align="center" id="fig-33">
  <img src="images/33-wait-strategies.png" alt="รูปที่ 33 กลยุทธ์ --wait" width="900"><br>
  <em><b>รูปที่ 33</b> ไม่ใส่ --wait: Helm บอก deployed ทั้งที่บูธยังพัง / --wait รอให้พร้อม / --rollback-on-failure ล้มแล้วถอยกลับเอง</em>
</p>

Helm 4 รับ `--wait` เป็น **กลยุทธ์ (WaitStrategy)**

| ค่า | ความหมาย |
|---|---|
| ไม่ใส่ (`hookOnly`) | **รอแค่ hook** (เช่น Job seed) ไม่รอ Deployment/StatefulSet พร้อม — ส่ง manifest เสร็จก็ตอบ `deployed` |
| `--wait` (= `--wait=watcher`) | รอจน object ทุกตัวพร้อมตาม kstatus (Deployment Available ครบ, StatefulSet ready, Job สำเร็จ ...) ภายใน `--timeout` (ค่าเริ่มต้น 5m) |
| `--wait=legacy` | วิธีรอแบบ Helm 3 |

ผลจริง LAB 4: image `9.9.9-nope` (ไม่มีจริง) **ไม่ใส่ `--wait`** ใช้เวลา **0.2 วินาที** แล้วได้ `STATUS: deployed` ทั้งที่ 15 วินาทีต่อมา Pod ใหม่เป็น `ErrImagePull` (ร้านยังเปิดได้เพราะ Pod เก่ายังอยู่ตาม rolling update) — CI ที่เชื่อ `deployed` จะรายงานว่าสำเร็จ

> **กติกาของบทนี้: ใส่ `--wait` ทุกครั้งที่ install/upgrade/rollback** (และ `--timeout` ที่เหมาะกับแอป) ชุดร้านติดตั้งแบบ `--wait` ใช้ 18 วินาที ส่วนไม่ใส่ใช้ราว 12 วินาที (เพราะยังต้องรอ hook seed อยู่ดี) ต่างกันไม่มากแต่ได้ความมั่นใจ

### 8.4 --rollback-on-failure, --timeout และ --cleanup-on-fail

`--rollback-on-failure` (ชื่อเดิม `--atomic`) = รอ (เหมือน `--wait`) ถ้าไม่พร้อมภายใน `--timeout` ให้ **ถอยกลับไป revision ที่ใช้งานอยู่ก่อนหน้าเอง** ผลจริง LAB 4

```text
time helm upgrade hello podinfo/podinfo --version 6.15.0 -n helm-demo --reuse-values --set image.tag=9.9.9-nope --rollback-on-failure --timeout 40s
level=WARN msg="upgrade failed" name=hello error="resource Deployment/helm-demo/hello-podinfo not ready. status: InProgress, message: Updated: 2/3\ncontext deadline exceeded"
Error: UPGRADE FAILED: release hello failed, and has been rolled back due to rollback-on-failure being set: resource Deployment/helm-demo/hello-podinfo not ready. status: InProgress, message: Updated: 2/3
context deadline exceeded

real	0m42.959s
```

สมุดได้ 2 หน้าใหม่: rev 8 `failed` และ rev 9 `Rollback to 7` (rev 7 คือรุ่นที่ใช้งานอยู่ก่อน upgrade) ใช้เวลารวม ~43 วินาที (timeout 40 + ถอย)

- `--timeout` ควรยาวกว่าเวลาที่แอปใช้พร้อมจริง (รวมดึง image, readinessProbe, `minReadySeconds`) ไม่งั้นจะถอยทั้งที่แอปกำลังจะพร้อม
- `--cleanup-on-fail` ลบ object **ใหม่** ที่ถูกสร้างใน upgrade ที่ล้ม (ไม่งั้นค้างอยู่)
- ใน CI นิยม `helm upgrade --install ... --wait --timeout 5m --rollback-on-failure`

### 8.5 กับดัก: rollback ไม่ระบุเลข

<p align="center" id="fig-34">
  <img src="images/34-rollback-no-number.png" alt="รูปที่ 34 กับดัก rollback ไม่ระบุเลข" width="900"><br>
  <em><b>รูปที่ 34</b> กับดัก: helm rollback ไม่ระบุเลข = ถอยไปหน้าก่อนหน้า แม้หน้านั้นเป็นรุ่นที่ล้ม → ระบุเลข revision เสมอ</em>
</p>

`helm rollback hello` (ไม่ใส่เลข) ถอยไป **revision ก่อนหน้า** ซึ่งอาจเป็นรุ่นที่ `failed` ผลจริง LAB 4: หลัง rev 9 (`Rollback to 7`) สั่ง `helm rollback hello` ได้ rev 10 **`Rollback to 8`** = กลับไปรุ่นที่ image ผิด Pod ใหม่เป็น `ErrImagePull` อีกครั้ง ต้องสั่ง `helm rollback hello 9 --wait` แก้ (rev 11)

```text
8       	Tue Oct  6 05:51:00 2026	failed    	podinfo-6.15.0	6.15.0     	Upgrade "hello" failed: resource Deployment/helm-demo/hello-podinfo not ready. status: InProgress, message: Updated: ...
9       	Tue Oct  6 05:51:40 2026	superseded	podinfo-6.15.0	6.15.0     	Rollback to 7
10      	Tue Oct  6 05:51:43 2026	deployed  	podinfo-6.15.0	6.15.0     	Rollback to 8
```

> **กติกา: ดู `helm history` ก่อน แล้ว rollback ด้วยเลขที่ต้องการเสมอ** (และใส่ `--wait`)

### 8.6 uninstall, --keep-history และของที่ไม่ถูกลบ

- `helm uninstall hello --keep-history` ลบ object แต่เก็บสมุด `helm list` (ไม่ใส่ตัวกรอง) แสดง `hello ... 11 ... uninstalled` จากนั้น `helm rollback hello 11 --wait` เปิดร้านกลับมาเป็น rev 12 `deployed` (2.6 วินาที) และระหว่างนี้ `helm install hello ...` จะได้ `cannot reuse a name that is still in use` (ใช้ `upgrade --install` แทนได้)
- `helm uninstall` ปกติลบสมุดด้วย หลังจากนั้น `helm history hello` = `Error: release: not found`
- ของที่ **ไม่** ถูกลบ: PVC ที่ StatefulSet สร้างจาก `volumeClaimTemplates` (ตู้เซฟ `data-som-db-0` ค้างหลัง uninstall สาขา dev — บทที่ 9 ก็เป็นแบบนี้), CRD ใน `crds/`, hook resource ที่ไม่มี delete policy, object ที่มี annotation `helm.sh/resource-policy: keep` และ namespace ที่สร้างด้วย `--create-namespace` (namespace ไม่ใช่ส่วนของ release)

ผลข้อแรกมีผลจริงใน LAB 12: ติดตั้งสาขา dev ใหม่ด้วย **รหัสเดิม** ได้ออเดอร์เดิมกลับมา (`orders=1`) แต่ถ้าใช้ **รหัสใหม่** ตู้เซฟเดิมยังล็อกด้วยรหัสเก่า ร้านเปิดไม่ได้ (LAB 12 ขั้น 12.9)

## 9. Helm 4 กับ server-side apply

### 9.1 ป้ายชื่อเจ้าของบนทุกช่อง

<p align="center" id="fig-35">
  <img src="images/35-field-managers.png" alt="รูปที่ 35 field manager" width="900"><br>
  <em><b>รูปที่ 35</b> server-side apply: ทุกช่องของ object มีป้ายชื่อเจ้าของ (field manager) เช่น helm, kubectl-client-side-apply, kube-controller-manager</em>
</p>

บทที่ 13 เราเจอ annotation `kubectl.kubernetes.io/last-applied-configuration` ของ `kubectl apply` แบบเดิม (**client-side apply**: kubectl คำนวณความต่าง 3 ทางบนเครื่องเราแล้วส่ง patch) Kubernetes มีอีกวิธีคือ **server-side apply (SSA)**: ส่ง "สิ่งที่ฉันต้องการ" ไปให้ API server แล้ว API server จดว่า **field ไหนเป็นของใคร** ไว้ใน `metadata.managedFields` ผู้เป็นเจ้าของเรียกว่า **field manager**

Helm 4 ใช้ SSA เป็นค่าเริ่มต้นด้วย field manager ชื่อ **`helm`** ผลจริง LAB 2 (Deployment ของ podinfo)

```text
kubectl -n helm-demo get deploy hello-podinfo -o jsonpath='{range .metadata.managedFields[*]}{.manager}{" "}{.operation}{"\n"}{end}'
helm Apply
kube-controller-manager Update
```

`helm` เป็นเจ้าของ field ที่ chart ตั้ง ส่วน `kube-controller-manager` เป็นเจ้าของ `status` ที่มันอัปเดต ร้านบท 013 ที่ผ่านมือหลายคนมีเจ้าของหลายราย (ผลจริง LAB 12 ขั้น 12.1)

```text
kube-controller-manager Update
kubectl-rollout Update
kubectl Update
kubectl-client-side-apply Update
kube-controller-manager Update
```

| field manager | มาจาก | เป็นเจ้าของอะไร |
|---|---|---|
| `kubectl-client-side-apply` | `kubectl apply` (ไฟล์ `20-web.yaml` ฯลฯ) | field ที่อยู่ในไฟล์ (image, env, initContainers ...) |
| `kubectl` | `kubectl set image`, `annotate` | image ที่ set, annotation change-cause |
| `kubectl-rollout` | `kubectl rollout restart` | annotation `restartedAt` |
| `kube-controller-manager` | controller ในคลัสเตอร์ | `status`, (HPA ปรับ `replicas` ผ่าน `/scale`) |
| `helm` (Apply) | Helm 4 | field ที่ chart ตั้ง |

> `kubectl get -o yaml/json` ซ่อน `managedFields` เป็นค่าเริ่มต้น ต้องเพิ่ม `--show-managed-fields` (ใน LAB 12 คำสั่ง python ที่อ่าน `-o json` เฉย ๆ ได้ `KeyError: 'managedFields'`) ส่วน `-o jsonpath` ยังอ่านได้

### 9.2 conflict: ช่องเดียวมีเจ้าของสองคน

<p align="center" id="fig-36">
  <img src="images/36-ssa-conflict.png" alt="รูปที่ 36 SSA conflict" width="900"><br>
  <em><b>รูปที่ 36</b> conflict: ช่องเดียวมีเจ้าของ 2 คนอยากตั้งค่าต่างกัน → Helm หยุด, --force-conflicts = ยึดเป็นของ helm</em>
</p>

เมื่อ `helm` ขอตั้งค่า field ที่ **เจ้าของอื่นถืออยู่และค่าต่างกัน** API server ปฏิเสธด้วย conflict แทนที่จะเขียนทับเงียบ ๆ (ป้องกันการแย่งกันแก้) ผลจริง LAB 12 ขั้น 12.6 (upgrade แรกหลังรับร้าน เปลี่ยน image เป็น 1.8)

```text
Error: UPGRADE FAILED: conflict occurred while applying object som-shop/som-web apps/v1, Kind=Deployment: Apply failed with 1 conflict: conflict with "kubectl-client-side-apply" using apps/v1: .spec.template.spec.containers[name="web"].image
```

ทางเลือก

1. **`--force-conflicts`**: บังคับให้ `helm` เป็นเจ้าของ field นั้นแทน (ใช้เมื่อแน่ใจว่าค่าใน chart คือค่าที่ถูก) ผลจริง: rev 4 deployed 15 วินาที ลูกค้า `ok=400 err=0` และ **upgrade/rollback ครั้งต่อไปไม่ต้อง force อีก** เพราะ field ถูกโอนเจ้าของแล้ว
2. แก้ chart ให้ไม่ตั้ง field นั้น (ปล่อยเจ้าของเดิมดูแล)
3. ให้เจ้าของเดิมเลิกถือ field (เช่น ลบ field นั้นด้วยเครื่องมือเดิม)

**field ที่ chart ไม่ได้ตั้งยังอยู่ตามเดิม** เพราะ SSA ลบเฉพาะ field ที่ manager คนเดิมเคยถือแล้วเลิกถือ ผลจริงหลังรับร้าน: annotation change-cause `1.7 เพิ่ม /api/work + HPA`, annotation `restartedAt`, HPA `behavior` (window 60 วินาทีจากบท 013) และ **initContainer `db-seed` ของบท 013** ยังอยู่ทั้งหมด เพราะ `kubectl-client-side-apply` ยังถือ field เหล่านั้น LAB 12 ขั้น 12.5c จึงต้องถอด `db-seed` ด้วย `kubectl patch` เอง (chart ใช้ hook seed แทน — หัวข้อ 11)

### 9.3 รับของเดิมที่ kubectl apply ไว้ (adopt)

<p align="center" id="fig-37">
  <img src="images/37-adopt-steps.png" alt="รูปที่ 37 รับของเดิมเข้า Helm" width="900"><br>
  <em><b>รูปที่ 37</b> รับของเดิมที่ kubectl apply ไว้: install ทับ → invalid ownership / --take-ownership → conflict / + --force-conflicts → ผ่าน (ถ้า selector ต่าง = field is immutable)</em>
</p>

Helm ไม่ยอมแตะ object ที่ไม่ใช่ของ release ตัวเอง โดยดูจาก label `app.kubernetes.io/managed-by: Helm` และ annotation `meta.helm.sh/release-name`/`meta.helm.sh/release-namespace` การย้ายของที่ติดตั้งด้วย `kubectl apply` เข้ามาอยู่ใต้ Helm จึงมี 3 ชั้น (ผลจริงทั้งหมด)

| ชั้น | คำสั่ง | ผลกับร้านน้องส้ม (LAB 12) | ผลกับ Traefik (LAB 10) |
|---|---|---|---|
| 1. install ทับ | `helm install ...` | `Secret "som-tls" in namespace "som-shop" exists and cannot be imported into the current release: invalid ownership metadata; label validation error: missing key "app.kubernetes.io/managed-by": must be set to "Helm" ...` — **ไม่สร้าง release** ปลอดภัย | `ServiceAccount "traefik" ... invalid ownership metadata` เหมือนกัน |
| 2. `--take-ownership` | ข้ามการตรวจ ownership แล้วติดป้าย | **conflict** กับ `kubectl-client-side-apply`: ConfigMap 3 field (`.data.SHOP_EYEBROW/FOOTER/PROMO`), Deployment 2, StatefulSet 1 (`.spec.volumeClaimTemplates`) → **rev 1 `failed`** | conflict: Service `.spec.selector`, Deployment 11 field → rev 1 `failed` |
| 3. `--take-ownership --force-conflicts` | ยึด field ที่ชน | **rev 2 `deployed` 16.4 วินาที** ออเดอร์เดิม `orders=3` อยู่ครบ ใบรับรองเดิม รหัสจาก lookup | `spec.selector: Invalid value: ...: field is immutable` → rev 2 `failed` |

ทำไมร้านรับได้แต่ Traefik รับไม่ได้: chart ร้านออกแบบให้ชื่อและ **selector** ตรงกับบท 013 (`app: som-web`) ส่วน Traefik chart ใช้ selector `app.kubernetes.io/name: traefik, app.kubernetes.io/instance: traefik-traefik` ขณะที่ static manifest ใช้ `app: traefik` และ `spec.selector` ของ Deployment **แก้ไม่ได้หลังสร้าง (immutable)** (บทที่ 7) ทางเดียวคือลบของเดิมแล้วติดตั้งใหม่ ซึ่งทำให้ประตูปิดชั่วครู่ (LAB 10 วัดได้ ~19 วินาที)

> ⚠️ **ห้าม `helm uninstall` release ที่ adopt ล้ม** ผลจริงจากการทดลองแยก: หลังชั้น 2–3 ล้ม ServiceAccount และ Service ถูกติดป้าย Helm ไปแล้ว `helm uninstall` จึง **ลบสองตัวนั้นทิ้ง** (เก็บไว้แค่ Deployment ที่ยังไม่ถูกยึด: `skipping delete of resource not owned by this release`) ถ้าเป็น Traefik ตัวจริง ประตูของทุกร้านจะปิดทันที ใน LAB 10 จึงให้ทำจริงแค่ชั้น 1 ส่วนชั้น 2–3 แสดงเป็น "ผลจริง ไม่ต้องทำตาม"

### 9.4 --server-side, --force-replace และเมื่อไรควรใช้

- `--server-side=true|false|auto`: install ใช้ `true` เป็นค่าเริ่มต้น upgrade/rollback ใช้ `auto` (ตามวิธีของ revision ก่อน) release ที่ติดตั้งด้วย Helm 3 (client-side) จึงยังอัปเกรดแบบเดิมจนกว่าจะเปลี่ยน
- `--force-replace` (ชื่อเดิม `--force`): ลบแล้วสร้าง object ใหม่แทนการ patch ใช้กับ field immutable ได้ แต่ **ทำให้ service สะดุด** (Pod ถูกลบ/สร้างใหม่) และไม่ควรใช้กับ object ที่ถือข้อมูล
- `--force-conflicts`: ใช้เมื่อ "รับร้าน" หรือมีคนแก้ด้วยมือแล้วต้องการให้ chart เป็นความจริงหนึ่งเดียว — หลังรับร้านแล้ว **ทีมควรเลิกแก้ object ด้วย `kubectl` ตรง ๆ** ไม่งั้นจะชนกันอีก

## 10. release เก็บที่ไหน

<p align="center" id="fig-38">
  <img src="images/38-release-secret.png" alt="รูปที่ 38 release Secret" width="900"><br>
  <em><b>รูปที่ 38</b> release แต่ละ revision เก็บเป็น Secret type helm.sh/release.v1 แค่พับ (base64) และห่อ (gzip) ไม่ได้ล็อก — ใบสั่งที่มีรหัสจึงอ่านได้</em>
</p>

Helm 3/4 ไม่มีฐานข้อมูลกลาง สมุดของแต่ละ release เก็บเป็น **Secret ใน namespace ของ release** หน้าละ 1 ซอง

```text
kubectl -n helm-demo get secret -l owner=helm
NAME                          TYPE                 DATA   AGE
sh.helm.release.v1.hello.v1   helm.sh/release.v1   1      13s
```

- ชื่อ `sh.helm.release.v1.<release>.v<revision>` type `helm.sh/release.v1` label `owner=helm, name=<release>, status=<สถานะ>, version=<rev>`
- เก็บ **10 revision ล่าสุด** (`HELM_MAX_HISTORY="10"` จาก `helm env`) ผลจริง LAB 4: หลัง rev 11 ซอง `v1` หายไป เหลือ `v2`–`v11`
- ข้อมูลใน key `release` = JSON ของ release ที่ **gzip แล้ว base64 โดย Helm** และ Kubernetes base64 อีกชั้นตามปกติของ Secret ถอดได้ด้วย

```bash
kubectl -n som-dev get secret sh.helm.release.v1.som.v1 -o jsonpath='{.data.release}' \
  | base64 -d | base64 -d | gzip -d | python3 -c 'import json,sys; print(sorted(json.load(sys.stdin).keys()))'
```

ได้ key `apply_method chart config hooks info manifest name namespace version` ซึ่ง **`config` คือ values ที่ผู้ใช้ส่ง** และ **`manifest` คือ YAML ทุก object ที่ render แล้ว** (รวม Secret ของร้าน) ผลจริง (ตัดให้สั้น)

```text
{"db": {"password": "meow1234"}, "hpa": {"enabled": false}, "ingress": {"enabled": true, "host": "dev.shop.localhost", "tls": false}, …}
['DATABASE_URL: "postgres://som:meow1234@som-db-0.som-db:5432/catshop"']
```

และใน LAB 12 ร้าน prod ที่ **ไม่ได้ `--set` รหัสเลย** (รหัสมาจาก `lookup`) manifest ใน release Secret ก็ยังมี `POSTGRES_PASSWORD`, `DATABASE_URL` และ **`tls.key` ของใบรับรอง** อยู่ เพราะเป็นผล render ของ Secret ทั้งก้อน

ผลด้านความปลอดภัย

1. **ใครอ่าน Secret ใน namespace ได้ = อ่านรหัสทุกตัวที่เคยผ่าน Helm ได้ (ย้อนหลัง 10 revision)** RBAC ที่ให้สิทธิ์ `get secrets` (บทที่ 11) จึงสำคัญกว่าเดิม
2. `helm get values som` ก็แสดง `password: meow1234` ตรง ๆ ใครที่รัน `helm` กับ namespace นั้นได้ก็เห็น
3. **ห้าม commit values ที่มีรหัสจริงลง git** (ส่งด้วย `--set` จาก secret store ของ CI หรือใช้ `lookup` แบบ chart นี้)
4. ระบบจริงใช้ **External Secrets Operator** (ดึงรหัสจาก Vault/คลาวด์มาเป็น Secret), **Sealed Secrets** (เก็บรหัสที่เข้ารหัสแล้วใน git) หรือ **SOPS** (เข้ารหัสไฟล์ values) เพื่อให้รหัสจริงไม่ผ่าน values ของ Helm
5. driver อื่น: ตั้ง `HELM_DRIVER=configmap` (เก็บเป็น ConfigMap — แย่กว่าเพราะ RBAC ของ ConfigMap มักหลวมกว่า) หรือ `sql` (เก็บใน PostgreSQL ภายนอก)

## 11. hooks และ helm test

### 11.1 hook: ขั้นตอนพิเศษตามจังหวะ

<p align="center" id="fig-39">
  <img src="images/39-hooks-timeline.png" alt="รูปที่ 39 จังหวะของ hook" width="900"><br>
  <em><b>รูปที่ 39</b> hook = ขั้นตอนพิเศษตามจังหวะ: pre-install ก่อนสร้าง, post-install หลังสร้าง (เติมสินค้าเข้าชั้น), test = ตรวจรับร้าน</em>
</p>

hook คือ object ปกติ (มักเป็น Job หรือ Pod) ที่มี annotation `helm.sh/hook` บอกว่าให้รันใน **จังหวะไหน** ของ lifecycle มี 9 ชนิด

| hook | รันเมื่อ |
|---|---|
| `pre-install` / `post-install` | ก่อน/หลังสร้าง object ของ release ครั้งแรก |
| `pre-upgrade` / `post-upgrade` | ก่อน/หลัง upgrade |
| `pre-rollback` / `post-rollback` | ก่อน/หลัง rollback |
| `pre-delete` / `post-delete` | ก่อน/หลัง uninstall |
| `test` | เมื่อสั่ง `helm test` |

บทที่ 9–13 ร้านเติมสินค้าเข้าชั้นด้วย **initContainer `db-seed`** ในทุก Pod หน้าร้าน (ทุกบูธใหม่รัน seed ซ้ำ) ชุด som-shop เปลี่ยนเป็น **hook Job** ที่รันครั้งเดียวหลัง install/upgrade (`templates/seed-job.yaml`)

```gotemplate
apiVersion: batch/v1
kind: Job
metadata:
  name: {{ $fn }}-seed
  labels:
    {{- include "som-shop.labels" . | nindent 4 }}
  annotations:
    "helm.sh/hook": post-install,post-upgrade
    "helm.sh/hook-weight": "0"
    "helm.sh/hook-delete-policy": before-hook-creation,hook-succeeded
spec:
  backoffLimit: 3
  template:
    spec:
      restartPolicy: OnFailure
      containers:
        - name: seed
          image: {{ include "som-shop.webImage" . }}
          command: ["node", "scripts/seed.mjs"]
```

ลำดับของ `helm install --wait` ชุดร้าน: render → สร้าง object ทั้งหมด → **รอให้พร้อม (เพราะ `--wait`)** → สร้าง Job seed (post-install) → รอ Job สำเร็จ → ลบ Job (`hook-succeeded`) → `deployed` ผลจริงใน LAB 9 (`kubectl get pod -w` ระหว่าง upgrade): Pod หน้าร้านใหม่ `Running 1/1` ก่อน แล้ว `som-seed-qk2k5` จึงเกิด → `Completed` → หายไป `kubectl get job` ได้ `No resources found`

- `hook-weight`: hook ชนิดเดียวกันหลายตัวรันเรียงจากน้อยไปมาก (เป็นข้อความตัวเลข เช่น `"-5"`, `"0"`)
- **hook ล้ม = release ล้ม**: ใน LAB 12 ติดตั้งสาขา dev ใหม่ด้วยรหัสใหม่ทั้งที่ตู้เซฟเดิมใช้รหัสเก่า (ไม่ใส่ `--wait`) ได้ `Error: INSTALLATION FAILED: failed post-install: resource Job/som-dev/som-seed not ready. status: Failed, message: Job Failed. failed: 1/1` ใน 45.7 วินาที (ถ้าใส่ `--wait` จะล้มก่อนถึง hook ที่ `resource Deployment/som-dev/som-web not ready ... Available: 0/1` เพราะหน้าร้านก็ต่อ db ไม่ได้)
- hook **ไม่ใช่ส่วนของ release**: ไม่อยู่ใน `helm get manifest` (ดูได้ด้วย `helm get hooks`) และ `helm uninstall` ไม่ลบให้ ต้องพึ่ง delete policy

### 11.2 hook-delete-policy

<p align="center" id="fig-40">
  <img src="images/40-hook-delete-policy.png" alt="รูปที่ 40 hook-delete-policy" width="900"><br>
  <em><b>รูปที่ 40</b> hook-delete-policy: before-hook-creation (ค่าเริ่มต้น), hook-succeeded, hook-failed — และ helm uninstall ไม่ลบ hook ให้</em>
</p>

| policy | ลบเมื่อ | ใช้เมื่อ |
|---|---|---|
| `before-hook-creation` (ค่าเริ่มต้นถ้าไม่ระบุ) | ก่อนสร้าง hook ตัวใหม่ชื่อเดิมในครั้งถัดไป | ให้ hook รันซ้ำได้ทุก upgrade โดยชื่อไม่ชน |
| `hook-succeeded` | ทันทีที่ hook สำเร็จ | ไม่ให้ Job ที่เสร็จแล้วค้าง |
| `hook-failed` | เมื่อ hook ล้ม | (ระวัง: ลบแล้วจะดู log ไม่ได้) |

ชุดร้านใช้ `before-hook-creation,hook-succeeded`: สำเร็จก็ลบทิ้ง ล้มก็ **เก็บไว้ให้ดู log** (ใน LAB 12 เห็น `pod/som-seed-9sjtp 0/1 Error` และ `job.batch/som-seed Failed 0/1`) แล้วรอบหน้าลบก่อนสร้างใหม่

### 11.3 helm test: ผู้ตรวจรับร้าน

<p align="center" id="fig-41">
  <img src="images/41-helm-test-inspector.png" alt="รูปที่ 41 helm test ผู้ตรวจรับร้าน" width="900"><br>
  <em><b>รูปที่ 41</b> helm test: Pod ตรวจรับร้านเรียก /api/health ถ้าจบด้วย exit 0 = Succeeded, --logs ดูผลตรวจ</em>
</p>

test คือ hook ชนิด `test` ที่รันเมื่อสั่ง `helm test` เท่านั้น ผ่าน = container จบด้วย exit code 0 ชุดร้านมี `templates/tests/test-health.yaml` (image `curlimages/curl:8.22.0`) เรียก 3 endpoint ผ่าน Service ภายใน (`set -e` + `curl -f` = ผิดตัวไหนก็ล้ม)

```text
helm test som -n som-dev --logs
...
TEST SUITE:     som-test-health
Last Started:   Tue Oct  6 05:53:45 2026
Last Completed: Tue Oct  6 05:53:53 2026
Phase:          Succeeded

POD LOGS: som-test-health (curl)
health:   {"ok":true,"db":"up"}
whoami:   som-web-64c9f5cd95-t5pj7 1.7
products: ok
```

- `--logs` แสดง log ของ Pod ทดสอบ (Helm 4 เก็บ log ก่อนลบตาม delete policy)
- `--filter name=<ชื่อ test>` เลือกรันบางตัว
- `helm test` ใช้ test ของ **release ที่ติดตั้งอยู่** ไม่ใช่ไฟล์ในเครื่อง แก้ test แล้วต้อง upgrade ก่อน
- test ตรวจ "ร้านทำงานจริงไหม" ซึ่ง `--wait` (ดูแค่ Ready) และ schema (ดูแค่รูปร่างค่า) ตอบไม่ได้ เหมาะใส่เป็นขั้นสุดท้ายของ CI

## 12. dependencies (subchart)

<p align="center" id="fig-42">
  <img src="images/42-subcharts.png" alt="รูปที่ 42 subchart และ Chart.lock" width="900"><br>
  <em><b>รูปที่ 42</b> dependencies: ชุดใหญ่ใส่ชุดย่อยได้ (เช่น metrics-server) helm dependency update ดึงมาเก็บใน charts/ และล็อกเวอร์ชันใน Chart.lock</em>
</p>

chart หนึ่งพึ่ง chart อื่นได้โดยประกาศใน `Chart.yaml` ตัวอย่าง **umbrella chart** (กล่องใหญ่ที่ไม่มี template ของตัวเอง มีแต่กล่องย่อย) ใน LAB เสริม `02_LAB/labs/labx-extra/harbor-addons/Chart.yaml`

```yaml
# LAB เสริม: umbrella chart = กล่องแฟรนไชส์ที่มีกล่องย่อย (subchart) 2 กล่อง ไม่มี templates ของตัวเอง
apiVersion: v2
name: harbor-addons
description: ชุดอุปกรณ์เสริมของท่าเรือ — metrics-server + podinfo (เปิด/ปิดได้)
type: application
version: 0.1.0
dependencies:
  - name: metrics-server
    version: 3.14.0
    repository: https://kubernetes-sigs.github.io/metrics-server/
  - name: podinfo
    version: 6.15.0
    repository: oci://ghcr.io/stefanprodan/charts   # dependency จาก OCI registry ก็ได้
    condition: podinfo.enabled                      # ติดตั้งก็ต่อเมื่อ podinfo.enabled=true
```

ส่งค่าให้ subchart ด้วย **key ชื่อเดียวกับ subchart** ใน `values.yaml` ของ chart แม่

```yaml
# ส่งค่าให้ subchart ด้วย key ชื่อ subchart
metrics-server:
  args:
    - --kubelet-insecure-tls
podinfo:
  enabled: false
```

**ตารางที่ 11** field ของ dependency และคำสั่ง

| field / คำสั่ง | ความหมาย |
|---|---|
| `name`, `version`, `repository` | chart ไหน รุ่นไหน (ใช้ช่วงได้ เช่น `~3.14.0`) จาก repo ไหน (HTTP URL, `oci://`, หรือ `file://../path`) |
| `condition` | เปิด/ปิด subchart ด้วยค่า boolean ใน values (`podinfo.enabled`) |
| `tags` | เปิด/ปิดหลาย subchart พร้อมกันเป็นกลุ่ม |
| `alias` | ใช้ chart เดียวกันหลายครั้งในชื่อต่างกัน |
| `global:` ใน values | ค่าที่ chart แม่และทุก subchart อ่านได้ (`.Values.global.x`) |
| `helm dependency list` | ดูสถานะ (`missing` / `ok`) |
| `helm dependency update` | ดาวน์โหลด subchart ลง `charts/` และเขียน `Chart.lock` (ล็อกรุ่น + digest) |
| `helm dependency build` | ดึงตาม `Chart.lock` เดิม (ได้รุ่นเดิมเป๊ะ) |

ผลจริงใน LAB เสริม: ก่อน update ทั้งสองตัว `missing` หลัง `helm dependency update` มี `Chart.lock`, `charts/metrics-server-3.14.0.tgz`, `charts/podinfo-6.15.0.tgz` และสถานะ `ok` render แล้วได้ object ของ metrics-server 9 ตัว ถ้า `--set podinfo.enabled=true` จึงมี object จาก `harbor-addons/charts/podinfo` เพิ่ม 5 ตัว

**library chart** (`type: library`) คือ chart ที่มีแต่ `define` ให้ chart อื่น include ใช้ร่วมกัน (เช่น label มาตรฐานขององค์กร) ติดตั้งเองไม่ได้

> chart ที่มี subchart เยอะจะ debug ยากขึ้น (values ซ้อนหลายชั้น) และอัปเกรด subchart ทีละตัวไม่ได้ ระบบจริงหลายทีมจึงเลือกติดตั้ง add-on แยก release (แบบ LAB 10) แล้วใช้เครื่องมือ GitOps คุมลำดับแทน

## 13. repository: HTTP vs OCI และ Artifact Hub

### 13.1 แคตตาล็อก (HTTP) กับโกดัง (OCI)

<p align="center" id="fig-43">
  <img src="images/43-http-vs-oci.png" alt="รูปที่ 43 HTTP repository กับ OCI" width="900"><br>
  <em><b>รูปที่ 43</b> repository แบบ HTTP = แคตตาล็อก (index.yaml + ไฟล์ .tgz) ต้อง repo add; OCI = โกดัง (oci://) ดึงตรงได้เลย</em>
</p>

**ตารางที่ 12** repository สองแบบ

| | HTTP chart repository | OCI registry |
|---|---|---|
| ข้างใน | เว็บเซิร์ฟเวอร์ธรรมดาที่มี `index.yaml` (รายการทุก chart ทุกรุ่น) + ไฟล์ `.tgz` | registry แบบเดียวกับที่เก็บ container image (Docker Hub, GHCR, Harbor, `registry:2`) |
| เริ่มใช้ | `helm repo add traefik https://traefik.github.io/charts` แล้ว `helm repo update` | ไม่ต้อง add ใช้ URL `oci://...` ตรง ๆ |
| ค้นหา | `helm search repo traefik/traefik --versions` (ค้นใน index ที่ดาวน์โหลดไว้) | ไม่มี search ในตัว (ดูจากเว็บของ registry หรือ Artifact Hub) |
| ติดตั้ง | `helm install traefik traefik/traefik --version 41.6.1` | `helm install oci-som oci://localhost:5000/charts/som-shop --version 0.1.0` |
| เผยแพร่ | `helm package` + อัปโหลด `.tgz` + สร้าง `index.yaml` ใหม่ (`helm repo index`) | `helm package` + `helm push` |
| ยืนยันตัวตน | basic auth / ไม่มี | `helm registry login <host>` (Helm 4 รับแค่ชื่อโฮสต์) |
| อ้างอิงแบบล็อกเนื้อหา | ไม่มี | **digest** `oci://.../som-shop@sha256:...` |
| ตัวอย่างในบทนี้ | podinfo, traefik, metrics-server | `registry:2` ใน k8s-lab (LAB 11), `oci://ghcr.io/stefanprodan/charts` (LAB เสริม) |

ผลจริงจาก LAB 1 (เลือกรุ่นแล้ว **pin** ไว้ทุกคำสั่ง)

```text
helm search repo traefik/traefik --versions | head -5
NAME                	CHART VERSION	APP VERSION	DESCRIPTION
traefik/traefik     	41.6.1       	v3.7.13    	A Traefik based Kubernetes ingress controller
traefik/traefik     	41.6.0       	v3.7.13    	A Traefik based Kubernetes ingress controller
traefik/traefik     	41.5.0       	v3.7.13    	A Traefik based Kubernetes ingress controller
traefik/traefik     	41.4.0       	v3.7.12    	A Traefik based Kubernetes ingress controller
```

เราเลือก **`traefik/traefik` 41.6.1** (app v3.7.13 ตรงกับบท 012–013) และ **`metrics-server/metrics-server` 3.14.0** (app 0.9.0 ตรงกับบท 013) สังเกตว่า **CHART VERSION กับ APP VERSION เป็นคนละเลข** (หัวข้อ 4.2) chart 3 รุ่นติดกันใช้ Traefik รุ่นเดียวกัน

ผลจริงจาก LAB 11 (OCI)

```text
helm push som-shop-0.1.0.tgz oci://localhost:5000/charts --plain-http
Pushed: localhost:5000/charts/som-shop:0.1.0
Digest: sha256:ef59e9e33853a9e4af39916e648d7dca165471037781ab5c07e8934d6fcfda22
```

`--plain-http` ใช้เฉพาะ registry ใน LAB ที่ไม่มี TLS registry จริงต้องเป็น HTTPS ข้อมูล login ของ `helm registry login` เก็บที่ `~/.config/helm/registry/config.json` เป็น **base64 ของ `user:password`** (ผลจริง `{'localhost:5000': {'auth': 'c29tOm...'}}`) ไม่ใช่การเข้ารหัส (เหมือน Secret ในบทที่ 11) ควร logout บนเครื่องที่ใช้ร่วมกัน

### 13.2 Artifact Hub: ที่ค้นแคตตาล็อก

<p align="center" id="fig-44">
  <img src="images/44-artifact-hub.png" alt="รูปที่ 44 Artifact Hub" width="900"><br>
  <em><b>รูปที่ 44</b> Artifact Hub = ที่ค้นชุดแฟรนไชส์จากหลายผู้เผยแพร่ — ชื่อเดียวกันไม่ได้แปลว่าเป็นของทางการ ดูป้ายผู้เผยแพร่ที่ยืนยันแล้ว</em>
</p>

[Artifact Hub](https://artifacthub.io/) (โครงการของ CNCF) รวบรวมรายการ chart จาก repository จำนวนมาก ค้นจากเว็บหรือ `helm search hub` ผลจริงจาก LAB 1

```text
helm search hub traefik --max-col-width 50 | head -8
URL                                               	CHART VERSION              	APP VERSION	DESCRIPTION
https://artifacthub.io/packages/helm/traefik/tr...	41.6.1                     	v3.7.13    	A Traefik based Kubernetes ingress controller
https://artifacthub.io/packages/helm/quench-tra...	0.0.21                     	3.7.13     	Cloud-native reverse proxy and load balancer wi...
https://artifacthub.io/packages/helm/aigisuk/tr...	0.1.1                      	2.7.0-rc2  	Latest release candidate of the Traefik based K...
https://artifacthub.io/packages/helm/kubeblocks...	41.6.0                     	v3.7.13    	A Traefik based Kubernetes ingress controller
https://artifacthub.io/packages/helm/k3s/traefik  	41.4.2+up41.4.0            	v3.7.12    	A Traefik based Kubernetes ingress controller
...
```

มี chart ชื่อ `traefik` จากหลายผู้เผยแพร่ บางตัวเป็นสำเนาของ chart ทางการ (kubeblocks, k3s) บางตัวเป็นรุ่นเก่ามาก (`2.7.0-rc2`) วิธีเลือก

1. ดูป้าย **Verified Publisher** (ผู้เผยแพร่ยืนยันเจ้าของ repo แล้ว) และ **Official** (เป็นของเจ้าของโปรเจกต์)
2. ดู repository URL ว่าเป็นของเจ้าของโปรเจกต์ (`traefik.github.io/charts`, `kubernetes-sigs.github.io/metrics-server`)
3. ดูวันที่ออกรุ่น จำนวนรุ่น และหน้า Security Report (ช่องโหว่ใน image ที่ chart ใช้)
4. อ่าน `helm show chart/values/readme` ก่อนติดตั้งเสมอ

### 13.3 chart กับ image: คนละคนดึง

<p align="center" id="fig-45">
  <img src="images/45-chart-vs-image-registry.png" alt="รูปที่ 45 chart กับ image คนละคนดึง" width="900"><br>
  <em><b>รูปที่ 45</b> คนละคนดึง: helm บนเครื่องเราดึง chart (registry login) / kubelet บน Node ดึง image (imagePullSecrets บท 011)</em>
</p>

จุดที่สับสนบ่อย: chart อยู่ใน OCI registry ได้เหมือน image แต่ **ผู้ดึงเป็นคนละตัว**

| | chart | container image |
|---|---|---|
| ใครดึง | **helm บนเครื่องที่สั่งคำสั่ง** (k8s-lab) | **kubelet / containerd บน Node** |
| ยืนยันตัวตนด้วย | `helm registry login` (ไฟล์ในเครื่องเรา) | `imagePullSecrets` ใน Pod/ServiceAccount (บทที่ 11) |
| ตัวอย่างในบทนี้ | `localhost:5000` ใน k8s-lab → ดึงได้เพราะ helm รันใน k8s-lab | Node ของ kind **มองไม่เห็น** `localhost:5000` ของ k8s-lab (เป็น localhost ของ Node เอง) — LAB จึงไม่ push image เข้า registry นี้ |

เหตุนี้ install chart จาก OCI สำเร็จไม่ได้แปลว่า Pod จะดึง image ได้ ถ้า image อยู่ใน registry ส่วนตัวต้องตั้ง `imagePullSecrets` (chart ที่ดีมีช่องให้ใส่ใน values) และ Node ต้องมองเห็น registry นั้น

## 14. ความปลอดภัยและแหล่งที่มา

### 14.1 ก่อนติดตั้ง chart ใด ๆ

<p align="center" id="fig-46">
  <img src="images/46-security-checklist.png" alt="รูปที่ 46 เช็กลิสต์ความปลอดภัย" width="900"><br>
  <em><b>รูปที่ 46</b> ก่อนติดตั้ง chart: อ่าน values และ image ที่จะดึง, pin เวอร์ชัน (และ digest), ไม่ใส่รหัสจริงใน values ที่ commit, เลือกแหล่งของเจ้าของโปรเจกต์</em>
</p>

chart คือ "โค้ดที่จะสร้าง object ด้วยสิทธิ์ของเรา" ชุดที่ติดตั้ง ClusterRole หรือ Pod ที่มีสิทธิ์สูงจึงควรอ่านก่อนเหมือนอ่านโค้ด

```bash
helm show chart traefik/traefik --version 41.6.1          # ฉลาก: ใครทำ รุ่นอะไร
helm show values traefik/traefik --version 41.6.1 | less   # ค่าเริ่มต้นทั้งหมด
helm template traefik traefik/traefik --version 41.6.1 -f labs/lab10-addons/traefik-values.yaml \
  | grep -E "^kind:|image:"                                # จะสร้างอะไร และดึง image ไหน
```

เช็กลิสต์

1. **แหล่ง**: chart ของเจ้าของโปรเจกต์หรือ Verified Publisher (หัวข้อ 13.2)
2. **pin รุ่น**: ใส่ `--version` ทุกคำสั่ง (ไม่ใส่ = ได้รุ่นล่าสุด ณ วันนั้น ผลจึงเปลี่ยนตามวัน) ระบบสำคัญ pin ด้วย **digest** (`oci://...@sha256:...`) ซึ่งเปลี่ยนเนื้อหาไม่ได้แม้ผู้เผยแพร่จะ push tag เดิมทับ
3. **อ่าน image ที่จะถูกดึง** และ pin tag/digest ของ image ผ่าน values ถ้า chart เปิดให้ตั้ง
4. **ดูสิทธิ์**: ClusterRole, `privileged`, `hostNetwork`, ServiceAccount ที่ chart สร้าง
5. **ความลับ**: ไม่ใส่รหัสจริงใน values ที่ commit (หัวข้อ 10)
6. **provenance**: chart ที่เซ็นด้วย `helm package --sign` ตรวจได้ด้วย `helm verify` หรือ `--verify` ตอน install/pull
7. **plugin**: Helm 4 ตรวจที่มาของ plugin แหล่งที่ไม่ได้เซ็นต้องใส่ `--verify=false` เอง (LAB เสริม: `Error: plugin source does not support verification. Use --verify=false to skip verification`) ใช้เฉพาะ plugin ที่เชื่อถือได้และ pin `--version` (helm-diff ต้องเป็น v3.15.15 ขึ้นไปถึงใช้กับ Helm 4 ได้ — รุ่น v3.13.1 ใช้ไม่ได้)
8. ค่าที่ลดความปลอดภัยใน LAB นี้ (`api.insecure: true` ของ Traefik dashboard, `--kubelet-insecure-tls` ของ metrics-server, `--plain-http` ของ registry) **ใช้เฉพาะ LAB**

### 14.2 บทเรียนปี 2568: แคตตาล็อกดังก็หายได้

<p align="center" id="fig-47">
  <img src="images/47-catalog-can-vanish.png" alt="รูปที่ 47 แคตตาล็อกหายได้" width="900"><br>
  <em><b>รูปที่ 47</b> บทเรียนปี 2568: แคตตาล็อกดังเปลี่ยนเงื่อนไข image รุ่นเก่าถูกย้าย/หยุดอัปเดต → pin เวอร์ชัน และเก็บสำเนาในโกดังของเราเอง</em>
</p>

**Bitnami** เคยเป็นแคตตาล็อก chart ที่นิยมที่สุดแห่งหนึ่ง (PostgreSQL, Redis, WordPress, ...) และ chart เหล่านั้นใช้ image `docker.io/bitnami/*` ตามประกาศของ Bitnami ([bitnami/charts#35164](https://github.com/bitnami/charts/issues/35164)) **ตั้งแต่ 28 สิงหาคม 2568 (2025)** Bitnami หยุดเผยแพร่ image/chart รุ่นที่มีเลขเวอร์ชันแบบฟรีใน `docker.io/bitnami` ย้ายของเดิมไปไว้ที่ `docker.io/bitnamilegacy` (ไม่อัปเดตและไม่ซัพพอร์ตต่อ) มีช่วง "brownout" ที่ image ดึงไม่ได้ชั่วคราวหลายรอบก่อนถึงวันจริง และชุดฟรีที่เหลือ (`bitnamisecure`) มีให้แค่ tag `latest`

ผลคือระบบที่ `helm install bitnami/postgresql` ไว้โดยไม่ได้คิด เจอปัญหา Pod ดึง image ไม่ได้เมื่อ Node ใหม่เกิด หรือต้องรีบย้าย image ไป `bitnamilegacy` ที่ไม่มี security fix บทเรียนที่ใช้ได้กับทุกแหล่ง

1. **pin chart และ image** ทั้งเวอร์ชันและ digest
2. **เลือก chart ของเจ้าของโปรเจกต์** (บทนี้ใช้ Traefik จาก Traefik Labs, metrics-server จาก kubernetes-sigs)
3. **เก็บสำเนาในโกดังขององค์กร** (OCI registry ของเราเอง เช่น Harbor — LAB 11 ทำแบบเล็ก) ทั้ง chart และ image
4. **อ่านว่า chart ดึง image จากที่ไหน** (`helm template | grep image:`) ไม่ใช่ดูแค่ชื่อ chart
5. ติดตามประกาศของแหล่งที่ใช้ และมีแผนย้ายเมื่อเงื่อนไขเปลี่ยน

บทนี้ **ไม่ใช้ Bitnami** ฐานข้อมูลในชุดร้านใช้ image ทางการ `postgres:17.11-alpine` ใน chart ที่เราเขียนเอง

## 15. Helm vs Kustomize vs static manifest

<p align="center" id="fig-48">
  <img src="images/48-helm-kustomize-static.png" alt="รูปที่ 48 static / Kustomize / Helm" width="900"><br>
  <em><b>รูปที่ 48</b> เทียบ 3 แบบ: static manifest (แผ่นเดียวตายตัว), Kustomize (แผ่นใสซ้อนบนพิมพ์เขียว), Helm (ชุดแฟรนไชส์ + รุ่น + rollback)</em>
</p>

**Kustomize** (มีใน kubectl: `kubectl apply -k`, บทที่ 10 ใช้ `configMapGenerator`) แก้ปัญหาค่าต่างระหว่าง environment ด้วย **overlay**: มีโฟลเดอร์ `base/` เป็น YAML ปกติ แล้ว `overlays/dev/` ใส่ patch ทับบางส่วน ไม่มี template ไม่มีตัวแปร

**ตารางที่ 13** เทียบ 3 แนวทาง

| เรื่อง | static manifest (`kubectl apply -f`) | Kustomize (`kubectl apply -k`) | Helm |
|---|---|---|---|
| วิธีทำให้ต่างกันต่อ environment | copy ไฟล์ | base + overlay/patch | template + values |
| ไฟล์ที่อ่าน | YAML ล้วน | YAML ล้วน (อ่านง่าย) | YAML ปน `{{ }}` (อ่านยากกว่า) |
| เงื่อนไข/วนซ้ำ | ไม่ได้ | จำกัด (ผ่าน patch/component) | ได้เต็มที่ (`if`, `range`) |
| รุ่นของทั้งชุด + rollback | ไม่มี | ไม่มี (พึ่ง git) | **มี** revision + `helm rollback` |
| ลบของที่เอาออกจากชุด | ไม่ (ต้อง prune เอง) | ไม่ (ต้อง prune เอง) | ใช่ |
| hook / test | ไม่มี | ไม่มี | มี |
| แจกจ่ายให้คนอื่น | ส่งไฟล์ | ส่งโฟลเดอร์/อ้าง git URL | **แพ็กเกจ** `.tgz` ใน repo/OCI + Artifact Hub |
| debug | ง่ายสุด | ง่าย (`kubectl kustomize` ดูผล) | ต้อง `helm template --debug` |
| เหมาะกับ | แอปเล็ก ไม่กี่ไฟล์ | แอปของทีมเองที่ต่างกันเล็กน้อยต่อ environment | ซอฟต์แวร์ที่แจกให้หลายคนติดตั้ง (Traefik, metrics-server), แอปที่ต้องการ lifecycle |

ใช้ร่วมกันได้: `helm template ... | kubectl apply -k` แบบส่งผลไปให้ Kustomize patch ต่อ หรือใช้ **post-renderer** (Helm 4 ต้องเป็น plugin) ให้ Helm ส่ง manifest ไปผ่าน Kustomize ก่อน apply เหมาะกับการ "ปรับ chart ของคนอื่นเล็กน้อย" โดยไม่ fork chart

## 16. ปูทาง GitOps และ operator

### 16.1 GitOps: ให้หุ่นยนต์เฝ้าแฟ้มแผนร้าน

<p align="center" id="fig-49">
  <img src="images/49-gitops-preview.png" alt="รูปที่ 49 ปูทาง GitOps" width="900"><br>
  <em><b>รูปที่ 49</b> GitOps (ตัวอย่าง Argo CD/Flux): เก็บ chart + ใบสั่งไว้ใน Git แล้วหุ่นยนต์เฝ้าแฟ้มทำให้สาขาตรงกับแผนเสมอ ไม่ต้องสั่ง helm upgrade เอง</em>
</p>

ในบทนี้เราเป็นคนพิมพ์ `helm upgrade` เองทุกครั้ง ถ้ามีคนแก้ร้านด้วย `kubectl edit` (drift) ก็ไม่มีใครรู้ **GitOps** กลับทิศ: เก็บ "ร้านที่ควรเป็น" (chart + ใบสั่ง) ไว้ใน **Git เป็นแหล่งความจริง** แล้วให้ controller ในคลัสเตอร์คอยดึงและทำให้คลัสเตอร์ตรงกับ Git เสมอ อยากอัปเกรด = เปิด Pull Request แก้ `web.image.tag` แล้ว merge (มีคนรีวิว มีประวัติใน git) ย้อนรุ่น = `git revert`

ตัวอย่างแนวคิด (ยังไม่ได้ใช้ใน LAB ของบทนี้ — เป็นบทถัดไป) chart เดียวกับที่เราเขียน ถูกอ่านโดยเครื่องมือ GitOps 2 ตัวที่นิยม

```yaml
# Argo CD: Application ที่ชี้ chart ในโฟลเดอร์ของ git + ใบสั่ง prod
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: som-shop-prod
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/example/som-shop-gitops.git
    targetRevision: main
    path: charts/som-shop
    helm:
      valueFiles:
        - ../values-prod.yaml
  destination:
    server: https://kubernetes.default.svc
    namespace: som-shop
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

```yaml
# Flux: HelmRelease ที่ดึง chart จาก OCI registry ขององค์กร
apiVersion: source.toolkit.fluxcd.io/v1
kind: HelmRepository
metadata:
  name: som-charts
  namespace: som-shop
spec:
  type: oci
  url: oci://registry.example.com/charts
  interval: 10m
---
apiVersion: helm.toolkit.fluxcd.io/v2
kind: HelmRelease
metadata:
  name: som
  namespace: som-shop
spec:
  interval: 10m
  chart:
    spec:
      chart: som-shop
      version: 0.1.0
      sourceRef:
        kind: HelmRepository
        name: som-charts
  values:
    hpa:
      enabled: true
    ingress:
      enabled: true
      host: shop.localhost
      tls: true
```

ข้อต่างที่ควรรู้: Argo CD **render chart ด้วยวิธีแบบ `helm template`** แล้ว apply เอง (ไม่มี release Secret ของ Helm และ `lookup` ได้ค่าว่าง — chart ที่พึ่ง `lookup` แบบ som-shop ต้องปรับ เช่น ให้รหัสมาจาก External Secrets แทน) ส่วน Flux helm-controller ใช้ Helm SDK ติดตั้งเป็น release จริง (มี history, hook และ `lookup` ทำงาน) ทั้งสองแบบ **ไม่ต้องให้คนพิมพ์ `helm upgrade`** และแก้ drift กลับเอง (`selfHeal`)

### 16.2 operator: หุ่นยนต์ที่ดูแลร้านต่อทุกวัน

<p align="center" id="fig-50">
  <img src="images/50-operator-preview.png" alt="รูปที่ 50 ปูทาง operator" width="900"><br>
  <em><b>รูปที่ 50</b> Helm ติดตั้งจบแล้วไม่ดูแลต่อ — operator คือหุ่นยนต์ที่ดูแลร้านต่อทุกวัน (สำรองข้อมูล ซ่อม อัปเกรดฐานข้อมูล) บทถัดไป</em>
</p>

Helm ทำงาน **ตอนเราสั่ง** แล้วจบ หลังติดตั้งเสร็จ ถ้า `som-db-0` ข้อมูลเสีย ต้องสำรองข้อมูลทุกคืน หรือต้องอัปเกรด PostgreSQL 17 → 18 (ต้อง dump/restore) Helm ไม่รู้เรื่องเหล่านี้ **operator** คือ controller เฉพาะทาง (custom controller + CRD) ที่รันอยู่ในคลัสเตอร์ตลอดและรู้ "วิธีดูแล" แอปนั้น เช่น เราเขียน `kind: PostgresCluster` (custom resource) แล้ว operator สร้าง StatefulSet, ตั้ง replication, สำรองข้อมูลตามตาราง และสลับ primary เมื่อพัง — เหมือนจ้างผู้จัดการครัวที่รู้งานครัวจริง ไม่ใช่แค่ผู้รับเหมาที่สร้างครัวแล้วกลับบ้าน

ความสัมพันธ์ที่พบบ่อย: **ใช้ Helm ติดตั้ง operator** (operator ส่วนใหญ่แจกเป็น chart) แล้วให้ operator ดูแลแอป

## 17. ตารางคำสั่งที่ใช้บ่อย

<p align="center" id="fig-51">
  <img src="images/51-command-cheatsheet.png" alt="รูปที่ 51 คำสั่งที่ใช้บ่อย" width="900"><br>
  <em><b>รูปที่ 51</b> คำสั่งที่ใช้บ่อยของ Helm 4 จัดเป็นกลุ่ม: ติดตั้ง/อัปเกรด, ดูสถานะ, ดูข้อมูลสาขา, ย้อนรุ่น, render/ตรวจ</em>
</p>

**ตารางที่ 14** คำสั่ง Helm 4 ที่ใช้ในบทนี้ (ทดสอบแล้วทุกคำสั่งกับ v4.3.0)

| กลุ่ม | คำสั่ง | ใช้ทำอะไร |
|---|---|---|
| ข้อมูล | `helm version`, `helm env` | รุ่น, ที่เก็บ cache/config, `HELM_MAX_HISTORY` |
| แคตตาล็อก | `helm repo add <name> <url>`, `helm repo update`, `helm repo list` | จัดการ HTTP repository |
| | `helm search repo <repo/chart> --versions`, `helm search hub <คำ>` | ค้นรุ่นใน repo ที่ add / ค้นใน Artifact Hub |
| | `helm show chart\|values\|readme <chart> --version X` | อ่านก่อนติดตั้ง |
| | `helm pull <chart> --version X --untar [-d dir]` | ดาวน์โหลดมาดูข้างใน (`-d` ต้องมีโฟลเดอร์อยู่ก่อน) |
| ติดตั้ง/อัปเกรด | `helm install <rel> <chart> -n <ns> --create-namespace -f v.yaml --set k=v --wait` | ติดตั้งครั้งแรก |
| | `helm upgrade <rel> <chart> -n <ns> -f v.yaml --wait [--rollback-on-failure --timeout 5m]` | อัปเกรด (ส่ง `-f` ทุกครั้ง) |
| | `helm upgrade --install ...` | ติดตั้งหรืออัปเกรด (CI) |
| | `--reuse-values`, `--reset-then-reuse-values` | ใช้ค่าของ revision ก่อน |
| | `--take-ownership --force-conflicts` | รับ object เดิมเข้า release |
| ดูสถานะ | `helm list [-A] [--failed\|--uninstalled]`, `helm status <rel>`, `helm history <rel>` | release ทั้งหมด / สถานะ / สมุด |
| ดูข้อมูลสาขา | `helm get values [--all] [--revision N]`, `helm get manifest`, `helm get notes`, `helm get hooks`, `helm get metadata` | ใบสั่ง / พิมพ์เขียว / การ์ด / hook / วิธี apply |
| ย้อนรุ่น/ถอน | `helm rollback <rel> <rev> --wait` | ย้อน (ระบุเลขเสมอ) |
| | `helm uninstall <rel> [--keep-history]` | ถอน |
| ตรวจ | `helm test <rel> --logs` | ตรวจรับร้าน |
| render/debug | `helm lint <chart> [-f v.yaml]`, `helm template <rel> <chart> [--show-only templates/x.yaml] [--debug]` | ตรวจ/ดูผล render |
| | `helm install ... --dry-run=client\|server` | ซ้อมติดตั้ง (server ไม่ตรวจ field — ใช้ `helm template \| kubectl apply --dry-run=server -f -` เพิ่ม) |
| สร้าง/แพ็ก | `helm create <name>`, `helm package <dir>` | โครง chart / ได้ `.tgz` |
| OCI | `helm registry login <host> -u <user> --password-stdin`, `helm push <tgz> oci://<host>/<path>`, `helm registry logout <host>` | โกดัง |
| dependency | `helm dependency list\|update\|build <chart>` | subchart |
| plugin | `helm plugin install <url> --version X [--verify=false]`, `helm plugin list`, `helm plugin uninstall <name>` | ส่วนเสริม (เช่น helm-diff) |

**ตารางที่ 15** flag ของ Helm 3 → Helm 4

| Helm 3 | Helm 4 | หมายเหตุ |
|---|---|---|
| `--atomic` | `--rollback-on-failure` | ตัวเก่ายังรับแต่ขึ้นคำเตือน deprecated |
| `--force` | `--force-replace` | ลบแล้วสร้างใหม่ |
| (ไม่มี / client-side) | `--server-side=true\|false\|auto`, `--force-conflicts` | SSA |
| `--wait` (bool) | `--wait[=watcher\|hookOnly\|legacy]` | ไม่ใส่ = `hookOnly` |
| `--dry-run` | `--dry-run=client\|server\|none` | ต้องระบุค่า |
| `helm list -a` | `helm list` (แสดงทุกสถานะ) + ตัวกรอง `--deployed`, `--failed`, `--uninstalled`, ... | `-a` ถูกเอาออก |
| `helm registry login https://host` | `helm registry login host` | รับแค่ชื่อโฮสต์ |
| post-renderer เป็นไฟล์ที่รันได้ | post-renderer ต้องเป็น plugin | |
| `helm plugin install <git>` | `helm plugin install <git> --verify=false` (แหล่งที่ไม่ได้เซ็น) | ตรวจที่มา |

## 18. สรุปบท

<p align="center" id="fig-52">
  <img src="images/52-chapter-summary.png" alt="รูปที่ 52 สรุปบท" width="900"><br>
  <em><b>รูปที่ 52</b> สรุปบท: ชุดแฟรนไชส์ (chart) + ใบสั่ง (values) → ร้านสาขา (release) ที่มีสมุดบันทึก (revision) ติดตั้ง/อัปเกรด/ย้อน/ถอนได้ทั้งร้าน</em>
</p>

**ตารางที่ 16** ปัญหาต้นบทกับสิ่งที่ Helm ให้

| ปัญหาของ YAML ล้วน | Helm แก้ด้วย | ผลจริงใน LAB |
|---|---|---|
| ค่าซ้ำหลายไฟล์ | template + `_helpers.tpl` | ชื่อ/label/image มาจากตรายางเดียว |
| copy โฟลเดอร์แล้ว drift | chart เดียว + ใบสั่งต่อ environment | dev 10 object / prod 13 object จาก chart เดียว |
| ไม่มีรุ่นของทั้งชุด | revision + `helm rollback` | `Rollback to 2` ระหว่างลูกค้าเข้า `ok=300 err=0` |
| ติดตั้งหลายขั้นตามลำดับ | `helm install` ครั้งเดียว + hook | สาขา dev ทั้งร้าน 18.0 วินาที + seed + test ผ่าน |
| ลบไม่หมด | `helm uninstall` | ลบทุก object (ยกเว้น PVC ตามที่ออกแบบ) |
| ใช้ของจากภายนอก | repository/OCI + pin รุ่น | Traefik 41.6.1, metrics-server 3.14.0 จาก chart ทางการ |

### ข้อควรจำของบทนี้

1. **ใส่ `--wait` ทุกครั้ง** — Helm 4 ไม่ใส่ = `deployed` ทั้งที่ Pod `ErrImagePull`
2. **ส่ง `-f` ใบสั่งทุกครั้งที่ upgrade** — ส่งแค่ `--set` บางค่า = ค่าอื่นกลับค่าเริ่มต้น (ไม่ส่งอะไรเลย = ใช้ค่าเดิม)
3. **rollback ระบุเลขเสมอ** — ไม่ระบุ = ถอยไปรุ่นก่อนหน้าแม้เป็นรุ่นที่ล้ม และ rollback เขียน revision ใหม่เสมอ
4. **`--dry-run=server` ไม่ตรวจ field ผิด** — ใช้ `helm template | kubectl apply --dry-run=server -f -` เพิ่ม
5. **release Secret อ่านได้** — รหัส (และ `tls.key`) อยู่ในนั้น ควบคุมสิทธิ์อ่าน Secret และไม่ commit รหัสใน values
6. **รับของเดิม = `--take-ownership --force-conflicts`** ได้เมื่อ selector ตรงกัน ถ้า selector ต่างต้องลบแล้วติดตั้งใหม่ และ **ห้าม uninstall release ที่ adopt ล้ม**
7. **PVC ไม่ถูกลบ** ติดตั้งใหม่ต้องใช้รหัสเดิม
8. **pin chart และ image** อ่าน values ก่อนติดตั้ง และมีสำเนาในโกดังของตัวเอง

## 19. คำถามทบทวน

**1. ร้านที่ติดตั้งด้วย `kubectl apply -f` หลายไฟล์มีปัญหาอะไรบ้างเมื่ออยากเปิดสาขาที่ 2 และ Helm แก้ปัญหาใดได้ ปัญหาใดแก้ไม่ได้**

<details>
<summary>แนวคำตอบ</summary>

ปัญหา: ค่าเดียวกันซ้ำหลายไฟล์ (ชื่อ, label, image tag, host) ต้อง copy โฟลเดอร์แล้วแก้ทำให้เกิด drift ระหว่างสาขา ไม่มีรุ่นของทั้งชุด (rollout history มีแค่ Deployment) ต้องจำลำดับการ apply และจำว่ามีอะไรต้องลบ ไม่รู้ว่าใครติดตั้งอะไรไว้ Helm แก้ด้วย template + values (chart เดียวหลายใบสั่ง), release + revision (ย้อนทั้งร้าน), install/uninstall เป็นชุด, `helm list -A` ส่วนที่ Helm ไม่แก้: ไม่ดูแลแอปหลังติดตั้ง (backup, ซ่อม db — งานของ operator), ไม่แก้ drift ที่เกิดจากคนแก้ด้วยมือเอง (งานของ GitOps) และไม่ทำให้ความลับปลอดภัยขึ้นเอง (รหัสยังอยู่ใน release Secret)
</details>

**2. อธิบายความต่างของ chart, values, release และ revision โดยใช้ตัวอย่าง `som-shop` ในบทนี้**

<details>
<summary>แนวคำตอบ</summary>

chart = โฟลเดอร์ `charts/som-shop` (template + `values.yaml` + `Chart.yaml`) values = ใบสั่ง เช่น `values-dev.yaml` และ `--set db.password=...` release = chart + values ที่ติดตั้งแล้ว ระบุด้วยชื่อ + namespace เช่น release `som` ใน `som-dev` และ release `som` ใน `som-shop` (ชื่อซ้ำได้เพราะคนละ namespace) revision = เลขรุ่นของ release เช่น prod rev 1 failed → rev 2 deployed (รับร้าน) → rev 4 (1.8) → rev 5 `Rollback to 2`
</details>

**3. ทำไม Helm 2 (Tiller) จึงถูกมองว่าไม่ปลอดภัย และ Helm 3/4 ใช้สิทธิ์ของใครในการสร้าง object**

<details>
<summary>แนวคำตอบ</summary>

Tiller เป็น Pod ในคลัสเตอร์ที่รับคำสั่งจาก helm แล้วสร้าง object แทน มักได้สิทธิ์ cluster-admin ใครที่คุยกับ Tiller ได้ก็ทำได้ทุกอย่าง ข้ามระบบ RBAC ของผู้ใช้ Helm 3/4 ไม่มี Tiller helm คุยกับ kube-apiserver ด้วย kubeconfig ของผู้ใช้เอง สิทธิ์จึงเป็นไปตาม RBAC ของผู้ใช้ (บทที่ 11) และ release เก็บใน namespace ของ release
</details>

**4. `version` กับ `appVersion` ใน `Chart.yaml` ต่างกันอย่างไร ทำไมใน LAB 12 คอลัมน์ APP VERSION ของ `helm history` ยังเป็น 1.7 ทั้งที่หน้าร้านเป็น 1.8 แล้ว**

<details>
<summary>แนวคำตอบ</summary>

`version` คือรุ่นของ chart (ต้องเพิ่มเมื่อแก้ template/values) `appVersion` คือรุ่นของแอปข้างใน ใช้แสดงผลและเป็น image tag เริ่มต้นใน template ของเรา คอลัมน์ APP VERSION อ่านจาก `appVersion` ของ chart ที่ใช้ใน revision นั้น เราเปลี่ยนแค่ `--set web.image.tag=1.8` โดยใช้ chart 0.1.0 (appVersion 1.7) เดิม คอลัมน์จึงยังเป็น 1.7 ถ้าอยากให้ตรงต้องออก chart รุ่นใหม่ที่ `appVersion: "1.8"`
</details>

**5. อธิบาย `{{- include "som-shop.labels" . | nindent 4 }}` ทีละส่วน ถ้าเปลี่ยน `nindent 4` เป็น `indent 4` จะเกิดอะไร**

<details>
<summary>แนวคำตอบ</summary>

`{{-` ตัดช่องว่างและการขึ้นบรรทัดก่อนหน้าทิ้ง, `include "som-shop.labels" .` เรียกตรายางที่ define ไว้ใน `_helpers.tpl` โดยส่ง scope ทั้งหมด (`.`) ให้ ได้ข้อความ 5 บรรทัด, `| nindent 4` ขึ้นบรรทัดใหม่แล้วย่อหน้าทุกบรรทัด 4 ช่อง ให้อยู่ใต้ `labels:` ถูกระดับ ถ้าเป็น `indent 4` จะไม่ขึ้นบรรทัดใหม่ บวกกับ `{{-` ที่ตัดบรรทัดก่อนหน้าไปแล้ว บรรทัดแรกของ label จะไปต่อท้าย `labels:` เป็น `labels:    app.kubernetes.io/name: ...` ได้ YAML ผิด (`mapping values are not allowed in this context`) แบบ LAB 6
</details>

**6. ตรายาง `som-shop.dbPassword` เลือกรหัสอย่างไร ทำไม `helm template` ที่ไม่ใส่รหัสจึง error ทั้งที่ในคลัสเตอร์มี Secret อยู่แล้ว**

<details>
<summary>แนวคำตอบ</summary>

ลำดับ: ถ้าส่ง `--set db.password` ใช้ค่านั้น ไม่งั้น `lookup` Secret `<fullname>-db-secret` ใน namespace ของ release ถ้าเจอถอด `POSTGRES_PASSWORD` มาใช้ ถ้าไม่เจอ `required` หยุดด้วยข้อความภาษาไทย `helm template` (และ `lint`) ไม่ต่อคลัสเตอร์ `lookup` จึงคืนค่าว่างเสมอ จึงตกไปที่ `required` ส่วน `helm install/upgrade` ต่อคลัสเตอร์ `lookup` เห็น Secret จริง จึงรับร้านเดิมได้โดยไม่ต้องส่งรหัส
</details>

**7. ทำไมแม่พิมพ์ `web.yaml` จึงใส่ `checksum/config` ใน annotation ของ Pod template และถ้าใส่ไว้ที่ `metadata.annotations` ของ Deployment แทนจะได้ผลเหมือนกันไหม**

<details>
<summary>แนวคำตอบ</summary>

Pod ที่อ่าน ConfigMap ผ่าน envFrom ไม่เห็นค่าใหม่จนกว่าจะเกิดใหม่ checksum ของ ConfigMap ที่ render แล้วจะเปลี่ยนเมื่อค่าใน `shop.*`/announcement เปลี่ยน ทำให้ Pod template เปลี่ยน Deployment จึงทำ rolling update เอง (LAB 9 ได้ Pod ใหม่เอง) ถ้าใส่ที่ annotation ของ Deployment (ไม่ใช่ `spec.template`) Deployment controller ไม่ถือว่า Pod template เปลี่ยน จึงไม่สร้าง Pod ใหม่ ไม่ได้ผล
</details>

**8. ใน LAB 3 rev 3 สั่ง `helm upgrade hello podinfo/podinfo --set replicaCount=1` แล้ว Ingress หายและ curl ได้ 404 อธิบายสาเหตุ และบอก 2 วิธีป้องกัน**

<details>
<summary>แนวคำตอบ</summary>

upgrade ที่ส่ง values มา (แม้แค่ `--set` ตัวเดียว) คำนวณค่าใหม่จากค่าเริ่มต้นของ chart + สิ่งที่ส่งในคำสั่งนี้ ไม่ได้รวมกับค่าของ revision ก่อน ค่า `ingress.enabled: true` ที่มาจากไฟล์ `-f` ใน rev 2 จึงหายกลับเป็นค่าเริ่มต้น (`false`) Ingress ถูกลบ วิธีป้องกัน: ส่ง `-f podinfo-values.yaml` ทุกครั้งที่ upgrade หรือใช้ `--reuse-values` (หรือ `--reset-then-reuse-values` เมื่อเปลี่ยนรุ่น chart) ข้อควรรู้: ถ้า upgrade โดยไม่ส่งค่าอะไรเลย Helm 4.3 ใช้ค่าเดิมต่อ
</details>

**9. เครื่องมือตรวจ chart (`lint`, `template`, `--dry-run=server`, `kubectl apply --dry-run=server`) ต่างกันอย่างไร ใน LAB 6 ทำไม `helm install --dry-run=server --set service.type=NodePortt` จึงผ่าน**

<details>
<summary>แนวคำตอบ</summary>

`lint` ตรวจรูปแบบ chart และ YAML (ไม่ต่อคลัสเตอร์), `template` render ออกมาดู (ไม่ต่อคลัสเตอร์ lookup ว่าง), `--dry-run=server` ของ Helm ต่อคลัสเตอร์เพื่อให้ lookup ทำงานและตรวจ ownership/ชื่อชน แต่ไม่ได้ส่ง object ให้ API server ตรวจแบบ server-side dry run จึงไม่รู้ว่า `NodePortt` ไม่ใช่ค่าที่อนุญาต (ได้ `Dry run complete`) ส่วน `helm template | kubectl apply --dry-run=server -f -` ส่ง manifest ให้ API server validate จริง จึงจับได้ `spec.type: Unsupported value: "NodePortt"`
</details>

**10. Helm 4 ไม่ใส่ `--wait` จะเกิดอะไร ต่างจาก `--wait` และ `--rollback-on-failure` อย่างไร เลือกแบบไหนใน CI**

<details>
<summary>แนวคำตอบ</summary>

ไม่ใส่ = กลยุทธ์ `hookOnly` รอแค่ hook ส่ง manifest เสร็จก็ `deployed` (LAB 4: image ผิด 0.2 วินาทีได้ `deployed` แต่ Pod `ErrImagePull`) `--wait` (watcher) รอจน object พร้อมภายใน `--timeout` ถ้าไม่ทันได้ `failed` แต่ไม่ถอย `--rollback-on-failure` รอแบบเดียวกันและถ้าล้มจะ rollback ไปรุ่นที่ใช้อยู่เอง (LAB 4: ~43 วินาที rev 8 failed, rev 9 `Rollback to 7`) ใน CI นิยม `helm upgrade --install --wait --timeout <เวลาที่เหมาะ> --rollback-on-failure` ตามด้วย `helm test`
</details>

**11. ใน LAB 4 หลัง rev 9 (`Rollback to 7`) สั่ง `helm rollback hello` (ไม่ใส่เลข) แล้วร้านกลับไปพัง อธิบายว่าเพราะอะไร และ rollback เลขอะไรจึงถูก**

<details>
<summary>แนวคำตอบ</summary>

rollback ไม่ใส่เลข = ไป revision ก่อนหน้า (ก่อน rev 9 คือ rev 8) แม้ rev 8 จะเป็นรุ่นที่ `failed` (image ผิด) จึงได้ rev 10 `Rollback to 8` และ Pod ใหม่ `ErrImagePull` ที่ถูกคือดู `helm history` แล้วระบุเลขรุ่นที่ดี เช่น `helm rollback hello 9 --wait` (หรือ 7 หรือ 5 ซึ่งมีเนื้อหาเดียวกัน) ได้ rev 11
</details>

**12. field manager และ conflict ของ server-side apply คืออะไร ทำไม upgrade ครั้งแรกหลังรับร้าน (เปลี่ยน image เป็น 1.8) ยัง conflict ทั้งที่ตอนรับร้านใส่ `--force-conflicts` ไปแล้ว**

<details>
<summary>แนวคำตอบ</summary>

SSA จดว่าแต่ละ field เป็นของ manager ใด (`helm`, `kubectl-client-side-apply`, `kubectl`, `kube-controller-manager`) ถ้า manager หนึ่งจะตั้งค่า field ที่อีกคนถือด้วยค่าต่างกัน API server ตอบ conflict ตอนรับร้าน (rev 2) image ใน chart (`som-shop-web:1.7`) **ตรงกับ** ค่าที่ `kubectl-client-side-apply` ตั้งไว้ จึงไม่ conflict และ field image ยังมีเจ้าของร่วม พอ upgrade ตั้งเป็น 1.8 ค่าต่างจากที่ `kubectl-client-side-apply` ถือ จึง conflict (rev 3 failed) ต้อง `--force-conflicts` อีกครั้งเพื่อโอน field ให้ `helm` หลังจากนั้น upgrade/rollback ไม่ต้อง force
</details>

**13. ทำไมรับร้านน้องส้มเข้า Helm ได้ด้วย `--take-ownership --force-conflicts` แต่ Traefik ทำแบบเดียวกันไม่ได้ และทำไมห้าม `helm uninstall` release ที่ adopt ล้ม**

<details>
<summary>แนวคำตอบ</summary>

chart ร้านออกแบบชื่อและ selector (`app: som-web`) ให้ตรงกับของเดิม SSA จึงแค่ยึด field ที่ชน ส่วน Traefik chart ใช้ selector `app.kubernetes.io/name/instance` ต่างจาก static (`app: traefik`) และ `spec.selector` ของ Deployment เปลี่ยนไม่ได้ (`field is immutable`) ต้องลบของเดิมแล้วติดตั้งใหม่ (ประตูปิด ~19 วินาที) release ที่ adopt ล้มได้ติดป้าย Helm ให้บาง object ไปแล้ว (ServiceAccount, Service) `helm uninstall` จึงลบ object เหล่านั้นด้วย ทั้งที่มันคือของจริงที่ใช้งานอยู่ ประตูจะปิดทันที
</details>

**14. release Secret ของ Helm เก็บอะไรไว้ และถอดอย่างไร ใครควรมีสิทธิ์อ่าน และระบบจริงควรเก็บรหัสฐานข้อมูลอย่างไร**

<details>
<summary>แนวคำตอบ</summary>

Secret `sh.helm.release.v1.<release>.v<N>` type `helm.sh/release.v1` เก็บ JSON ของ release (chart, config = values ที่ส่ง, manifest = YAML ทุก object ที่ render แล้ว, hooks, info, version, apply_method) แบบ gzip + base64 (และ base64 อีกชั้นของ Secret) ถอดด้วย `base64 -d | base64 -d | gzip -d` จึงเห็นรหัสฐานข้อมูลและแม้แต่ `tls.key` ที่อยู่ใน manifest ย้อนหลัง 10 revision ควรให้สิทธิ์ `get secrets` เฉพาะผู้ดูแล namespace (RBAC) ระบบจริงไม่ส่งรหัสผ่าน values: ใช้ External Secrets, Sealed Secrets หรือ SOPS และไม่ commit รหัสลง git
</details>

**15. hook seed ของชุดร้านต่างจาก initContainer `db-seed` ของบท 009–013 อย่างไร และทำไมการติดตั้งสาขา dev ใหม่ด้วยรหัสใหม่จึงล้มที่ hook (หรือที่ som-web ถ้าใส่ `--wait`)**

<details>
<summary>แนวคำตอบ</summary>

initContainer รันทุกครั้งที่ Pod หน้าร้านเกิด (ทุกบูธ ทุก restart) hook Job `post-install,post-upgrade` รันครั้งเดียวหลัง install/upgrade และถูกลบเมื่อสำเร็จ (`hook-succeeded`) การติดตั้งใหม่หลัง uninstall ได้ PVC `data-som-db-0` เดิมที่ฐานข้อมูลถูกสร้างด้วยรหัสเก่า (postgres ตั้งรหัสแค่ตอนสร้าง data directory ครั้งแรก) Secret ใหม่มีรหัสใหม่ Job seed จึง login ไม่ได้ → `failed post-install ... Job Failed` ถ้าใส่ `--wait` Helm รอ som-web พร้อมก่อนถึง hook แต่หน้าร้านก็ต่อ db ไม่ได้ readinessProbe ไม่ผ่าน จึงล้มที่ `Deployment/som-dev/som-web not ready` ก่อน แก้ด้วย upgrade release ที่ failed ด้วยรหัสเดิม หรือลบ namespace (รวม PVC) แล้วเริ่มใหม่
</details>

**16. chart อยู่ใน OCI registry ได้เหมือน image ทำไมใน LAB 11 จึง install chart จาก `oci://localhost:5000` ได้ แต่ไม่ push image ของร้านเข้า registry เดียวกัน**

<details>
<summary>แนวคำตอบ</summary>

chart ถูกดึงโดย helm ที่รันใน k8s-lab ซึ่งมองเห็น `localhost:5000` (registry รันใน docker ของ k8s-lab) และใช้ credential จาก `helm registry login` ส่วน image ถูกดึงโดย containerd บน Node ของ kind ซึ่ง `localhost` คือตัว Node เอง มองไม่เห็น registry นั้น (ต้องตั้ง mirror ของ containerd) และใช้ `imagePullSecrets` ไม่ใช่ helm login
</details>

**17. จากกรณี Bitnami ปี 2568 ทีมควรมีแนวปฏิบัติอย่างไรในการเลือกและใช้ chart จากภายนอก**

<details>
<summary>แนวคำตอบ</summary>

เลือก chart ของเจ้าของโปรเจกต์/Verified Publisher, pin รุ่น chart และ image (ควรเป็น digest), อ่าน `helm show values` และ `helm template | grep image:` ก่อนติดตั้งเพื่อรู้ว่าดึง image จากไหน, เก็บสำเนา chart และ image ใน registry ขององค์กร, ติดตามประกาศของแหล่งที่ใช้และมีแผนย้าย, ไม่เปิดใช้ plugin/แหล่งที่ไม่ตรวจที่มาโดยไม่จำเป็น
</details>

**18. ถ้าทีมของคุณมีแอปภายในที่ deploy 3 environment (dev, staging, prod) ต่างกันแค่จำนวน replica, host และ resource ควรเลือก Kustomize หรือ Helm เพราะอะไร และ GitOps จะช่วยอะไรเพิ่ม**

<details>
<summary>แนวคำตอบ</summary>

ตอบได้ทั้งสองแบบถ้าให้เหตุผล: Kustomize เหมาะเพราะต่างกันเล็กน้อย YAML อ่านง่าย ไม่ต้องเรียนภาษา template แต่ไม่มี release/rollback ในตัว (พึ่ง git) Helm เหมาะถ้าต้องการ lifecycle (revision, rollback, hook, test), แจกให้ทีมอื่นติดตั้ง หรือมีเงื่อนไขเปิด/ปิดส่วนต่าง ๆ GitOps (Argo CD/Flux) ช่วยให้ Git เป็นแหล่งความจริง ทุกการเปลี่ยนผ่าน Pull Request มีรีวิวและประวัติ controller ทำให้คลัสเตอร์ตรงกับ Git เองและแก้ drift ไม่ต้องให้คนพิมพ์ `helm upgrade` และใช้ได้กับทั้ง Helm chart และ Kustomize
</details>

---

## 20. เอกสารอ้างอิง

1. The Helm Authors. *Helm 4 Overview* (server-side apply, plugin ใหม่, chart v3 ทดลอง, `--atomic` → `--rollback-on-failure`, `--force` → `--force-replace`). https://helm.sh/docs/overview/
2. The Helm Authors. *HIP-0023: Server Side Apply* (`--server-side=true|false|auto`, field manager `helm`, `--force-conflicts`). https://helm.sh/community/hips/hip-0023/
3. The Helm Authors. *Helm 4 Changelog* (4.1, 4.2, 4.3: `--wait` strategy, `helm test --logs`). https://helm.sh/docs/changelog/
4. The Helm Authors. *Release v4.3.0*. https://github.com/helm/helm/releases/tag/v4.3.0
5. The Helm Authors. *Helm v3 End of Life*. https://helm.sh/blog/helm-v3-end-of-life
6. The Helm Authors. *Charts* (Chart.yaml, version/appVersion, `crds/`, dependencies, schema). https://helm.sh/docs/topics/charts/
7. The Helm Authors. *Chart Template Guide* (built-in objects, values, functions and pipelines, flow control, named templates). https://helm.sh/docs/chart_template_guide/
8. The Helm Authors. *Template Function List* (รวม Sprig, `lookup`, `required`, `include`, `tpl`). https://helm.sh/docs/chart_template_guide/function_list/
9. The Helm Authors. *Chart Hooks* (hook 9 ชนิด, weight, delete policy). https://helm.sh/docs/topics/charts_hooks/
10. The Helm Authors. *Chart Tests*. https://helm.sh/docs/topics/chart_tests/
11. The Helm Authors. *Use OCI-based registries*. https://helm.sh/docs/topics/registries/
12. The Helm Authors. *Helm Provenance and Integrity*. https://helm.sh/docs/topics/provenance/
13. The Helm Authors. *Chart Best Practices* (values, labels, templates, dependencies). https://helm.sh/docs/chart_best_practices/
14. The Helm Authors. *Advanced Helm Techniques* (post rendering). https://helm.sh/docs/topics/advanced/
15. The Helm Authors. *helm upgrade* (`--reuse-values`, `--reset-then-reuse-values`, `--take-ownership`). https://helm.sh/docs/helm/helm_upgrade/
16. Masterminds. *Sprig Function Documentation*. https://masterminds.github.io/sprig/
17. The Go Authors. *Package text/template*. https://pkg.go.dev/text/template
18. The Kubernetes Authors. *Server-Side Apply* (field management, conflicts). https://kubernetes.io/docs/reference/using-api/server-side-apply/
19. The Kubernetes Authors. *Declarative Management of Kubernetes Objects Using Kustomize*. https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization/
20. The Kubernetes Authors. *Operator pattern*. https://kubernetes.io/docs/concepts/extend-kubernetes/operator/
21. Artifact Hub (CNCF). https://artifacthub.io/
22. Traefik Labs. *Traefik Helm Chart* (Artifact Hub). https://artifacthub.io/packages/helm/traefik/traefik และ source https://github.com/traefik/traefik-helm-chart (repository https://traefik.github.io/charts)
23. Kubernetes SIGs. *metrics-server Helm chart* (Artifact Hub). https://artifacthub.io/packages/helm/metrics-server/metrics-server (repository https://kubernetes-sigs.github.io/metrics-server/)
24. Stefan Prodan. *podinfo*. https://github.com/stefanprodan/podinfo
25. Bitnami. *Upcoming changes to the Bitnami catalog (effective August 28th, 2025)*. https://github.com/bitnami/charts/issues/35164
26. databus23. *helm-diff plugin*. https://github.com/databus23/helm-diff
27. Argo Project. *Argo CD — Helm*. https://argo-cd.readthedocs.io/en/stable/user-guide/helm/
28. Flux Project. *Helm Releases*. https://fluxcd.io/flux/components/helm/helmreleases/
29. External Secrets Operator. https://external-secrets.io/
30. Bitnami Labs. *Sealed Secrets*. https://github.com/bitnami-labs/sealed-secrets
31. SOPS. https://github.com/getsops/sops

---

> **หมายเหตุเกี่ยวกับภาพประกอบ:** ภาพประกอบ 52 ภาพในโฟลเดอร์ [`images/`](images/) และภาพตัวละครน้องส้ม (`00-character-som.png`) สร้างขึ้นด้วยปัญญาประดิษฐ์สำหรับการสร้างภาพเพื่อใช้ประกอบการเรียนการสอน ชุดคำสั่งสร้างภาพอยู่ใน [`images/imagegen-prompts.md`](images/imagegen-prompts.md) ภาพใช้อุปมาเชิงเปรียบเทียบเพื่อช่วยความเข้าใจ ตัวเลขในภาพ (เช่น เลข revision, จำนวนวินาที, ชื่อ Pod) เป็นค่าตัวอย่าง ผู้เรียนควรใช้เนื้อหาในเอกสารนี้และเอกสารอ้างอิงเป็นหลัก ผลลัพธ์คำสั่งทั้งหมดมาจากการทดลองจริง (helm v4.3.0, Kubernetes v1.37.0, kubectl v1.37.1, เครื่องจำกัด 4 CPU) ค่าเวลา เลข revision และชื่อ Pod ในเครื่องผู้เรียนอาจต่างกัน รหัสผ่านทุกตัวในเอกสาร (`passwd`, `meow1234`, `meow-admin-123`, `meow-registry-123`) เป็นค่าตัวอย่างเพื่อการเรียนเท่านั้น
