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

เมื่อ render ด้วย release ชื่อ `som` ได้ YAML จริง (ผลจาก `helm template` ใน LAB 7 รูปแบบเดียวกับ ConfigMap ข้างล่าง)

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

