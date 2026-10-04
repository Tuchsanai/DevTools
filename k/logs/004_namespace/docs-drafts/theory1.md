# Namespace: แบ่งโซนบนท่าเรือเดียวกัน

> **รายวิชา:** Software Development Tools and Environments (DevTools)
> **หัวข้อ:** Kubernetes Namespace และนโยบายระดับ namespace — namespace เริ่มต้น, namespaced/cluster-scoped resources, kubeconfig/context, label ของ namespace, การลบ namespace และ finalizers, DNS, NetworkPolicy, ResourceQuota, LimitRange, RBAC (ServiceAccount, Role, RoleBinding) และ Pod Security Admission
> **ผลลัพธ์การเรียนรู้ที่เกี่ยวข้อง:** CLO-5, CLO-6
> **บทก่อนหน้า:** [บทที่ 3 Node กับ Pod](../../003_kubernetes_node_pod/01_Theory/README.md) · **LAB ของบทนี้:** [02_LAB](../02_LAB/README.md)

---

## บทคัดย่อ

ตั้งแต่บทที่ 1 ถึงบทที่ 3 เราสร้าง Pod ทุกตัวลงใน namespace ชื่อ `default` โดยไม่รู้ตัว ซึ่งไม่มีปัญหาเมื่อมีคนใช้คลัสเตอร์คนเดียว แต่ร้านอาหารแมวน้องส้มโตขึ้นจนมีทีมทดลองของใหม่ ทีมทดสอบ และร้านจริงที่ลูกค้าใช้ ทุกทีมวางกล่องไว้บนท่าเรือเดียวกัน ชื่อชนกัน ใครจะลบของใครก็ได้ และทีมหนึ่งใช้ทรัพยากรจนอีกทีมช้า บทนี้แก้ปัญหานั้นด้วย **Namespace** ซึ่งเปรียบเหมือน **โซนทาสีบนแผนผังท่าเรือ**

เนื้อหาเริ่มจากนิยามและข้อเข้าใจผิดที่พบบ่อย (namespace **ไม่ใช่** Node และไม่ได้แยกเครือข่ายให้เอง) ต่อด้วย namespace ตั้งต้น 5 ตัวของ kind, การแยก **namespaced** กับ **cluster-scoped** resources, การสร้างและเลือก namespace ด้วย `metadata.namespace`, `-n`, `-A` และ **context** ใน kubeconfig, label ของ namespace และการลบ namespace ทั้งก้อนพร้อมกลไก **finalizers** จากนั้นเป็นเครื่องมือที่ทำให้แต่ละโซนมีกติกาของตัวเอง ได้แก่ **NetworkPolicy** (รั้วและประตู), **ResourceQuota** (ใบงบ), **LimitRange** (ป้ายกฎขนาดกล่อง), **RBAC** (บัตรพนักงานเฉพาะโซน) และ **Pod Security Admission** (ด่านตรวจหน้าโซน) ปิดท้ายด้วยแนวปฏิบัติในการแบ่งและตั้งชื่อ namespace

ผลลัพธ์คำสั่งและข้อความ error ที่ยกมาในเอกสารนี้มาจากการทดลองจริงบนคลัสเตอร์ kind (kind v0.33.0, Kubernetes v1.37.0) ใน LAB ประจำบทเมื่อ 4 ตุลาคม 2569 **เวลา, AGE, IP และ Node ที่ Pod ถูกวางในเครื่องผู้เรียนอาจต่างจากตัวอย่าง**

## วัตถุประสงค์การเรียนรู้

เมื่อศึกษาเอกสารนี้จบ ผู้เรียนควรสามารถ

1. อธิบายว่า namespace คืออะไร เป็นขอบเขตของ "ชื่อ" และหน่วยที่ใช้แนบนโยบาย และบอกได้ว่าทำไม namespace จึง **ไม่ใช่** Node, VM หรือกำแพงเครือข่าย
2. บอกหน้าที่ของ namespace ตั้งต้น `default`, `kube-system`, `kube-public`, `kube-node-lease` และ `local-path-storage` ของ kind ได้
3. แยก resource แบบ namespaced กับ cluster-scoped ด้วย `kubectl api-resources` และอธิบายผลของ `-n` กับ resource แต่ละแบบได้
4. สร้าง ดู และลบ namespace ได้ทั้งแบบคำสั่งและแบบ YAML และเลือกใช้ `metadata.namespace`, `-n`, `-A` ได้ถูกต้อง รวมถึงอธิบาย error เมื่อทั้งสองค่าไม่ตรงกัน
5. อ่านโครงสร้าง kubeconfig (clusters, users, contexts) และเปลี่ยน namespace เริ่มต้นของ context ได้อย่างปลอดภัย
6. อธิบายสิ่งที่เกิดขึ้นเมื่อลบ namespace (Terminating, finalizers, ลบทุกอย่างข้างใน) และ namespace ใดที่ระบบป้องกันการลบ
7. เขียน NetworkPolicy แบบ allow-same-namespace และแบบเปิดให้ namespace ที่มี label ตรงด้วย `namespaceSelector` ได้
8. ใช้ ResourceQuota และ LimitRange ร่วมกัน อ่าน Used/Hard และข้อความ `must specify`, `exceeded quota`, `maximum cpu usage per Container` ได้
9. สร้าง ServiceAccount, Role, RoleBinding (รวมถึง ClusterRole + RoleBinding) ตรวจสิทธิ์ด้วย `kubectl auth can-i --as` และใช้ token ของ ServiceAccount ผ่าน context ใหม่ได้ พร้อมอธิบายกับดัก `kubectl --token`
10. ตั้ง Pod Security Admission ด้วย label ของ namespace (enforce/warn/audit) และแก้ Pod ให้ผ่านระดับ `restricted` ด้วย `securityContext` ได้

## สารบัญ

1. [บทนำ: ท่าเรือที่ทุกทีมวางของปนกัน](#1-บทนำ-ท่าเรือที่ทุกทีมวางของปนกัน)
2. [Namespace คืออะไร](#2-namespace-คืออะไร)
3. [Namespace เริ่มต้นและสิ่งที่อยู่ข้างใน](#3-namespace-เริ่มต้นและสิ่งที่อยู่ข้างใน)
4. [Namespaced vs cluster-scoped resources](#4-namespaced-vs-cluster-scoped-resources)
5. [สร้างและใช้ namespace](#5-สร้างและใช้-namespace)
6. [kubeconfig, context และ namespace เริ่มต้น](#6-kubeconfig-context-และ-namespace-เริ่มต้น)
7. [Label ของ namespace](#7-label-ของ-namespace)
8. [การลบ namespace](#8-การลบ-namespace)
9. [Namespace ไม่ได้แยก network และ node](#9-namespace-ไม่ได้แยก-network-และ-node)
10. [NetworkPolicy: รั้วและประตูระหว่างโซน](#10-networkpolicy-รั้วและประตูระหว่างโซน)
11. [ResourceQuota: งบประมาณของโซน](#11-resourcequota-งบประมาณของโซน)
12. [LimitRange: กฎขนาดกล่องมาตรฐาน](#12-limitrange-กฎขนาดกล่องมาตรฐาน)
13. [RBAC แบบ namespace: บัตรพนักงานเฉพาะโซน](#13-rbac-แบบ-namespace-บัตรพนักงานเฉพาะโซน)
14. [Pod Security Admission: ด่านตรวจหน้าโซน](#14-pod-security-admission-ด่านตรวจหน้าโซน)
15. [แนวปฏิบัติการตั้งชื่อและแบ่ง namespace](#15-แนวปฏิบัติการตั้งชื่อและแบ่ง-namespace)
16. [สรุปและคำถามทบทวน](#16-สรุปและคำถามทบทวน)
17. [เอกสารอ้างอิง](#17-เอกสารอ้างอิง)

### สารบัญรูปภาพ

{{FIGTABLE}}

---

## 1. บทนำ: ท่าเรือที่ทุกทีมวางของปนกัน

<p align="center">
  <img src="images/00-character-som.png" alt="น้องส้ม แมวส้มผู้ช่วยกัปตันท่าเรือ Kubernetes" width="320"><br>
  <em>น้องส้ม ผู้ช่วยกัปตันท่าเรือ Kubernetes ตัวละครหลักของบทนี้</em>
</p>

{{FIG:T01|ท่าเรือที่ทุกทีมวางของปนกัน}}

ร้านอาหารแมวน้องส้มจากบทที่ 2 เปิดหลายสาขาบนกองเรือได้แล้วในบทที่ 3 ตอนนี้ทีมใหญ่ขึ้นอีก มี **ทีมพัฒนา** ที่ทดลองของใหม่ทุกวัน **ทีมทดสอบ** ที่ตรวจก่อนขึ้นระบบจริง และ **ร้านจริง** ที่ลูกค้าใช้ ทุกทีมใช้คลัสเตอร์ (ท่าเรือ) เดียวกัน และทุกคนสร้าง Pod ลงที่เดียวกันคือ `default` ปัญหาจึงตามมาทันที

- **ชื่อชนกัน** ทีม dev อยากสร้าง Pod ชื่อ `som-shop` เพื่อทดลอง แต่ชื่อนี้ถูกร้านจริงใช้อยู่แล้ว ต้องตั้งชื่อแปลก ๆ อย่าง `som-shop-dev-test2` ไปเรื่อย ๆ
- **ใครลบของใครก็ได้** ทุกคนมีสิทธิ์เท่ากันทั้งท่าเรือ เด็กฝึกงานสั่ง `kubectl delete pod som-shop` ผิดตัวเดียว ร้านจริงก็ปิด
- **แย่งทรัพยากร** ทีม dev เปิด Pod ทดลองกินหน่วยความจำจนร้านจริงช้า เพราะไม่มีใครกำหนดงบของแต่ละทีม
- **ความปลอดภัยไม่เท่ากัน** ร้านจริงควรตรวจเข้ม (ห้ามรันเป็น root) แต่ทีม dev อยากทดลองอิสระ เมื่ออยู่ที่เดียวกันจึงตั้งกฎแยกไม่ได้
- **เก็บกวาดยาก** จะลบของทั้งหมดของทีม dev ต้องไล่หาทีละชิ้นจาก label ที่ไม่แน่ใจว่าทุกคนติดครบ

ทบทวนสิ่งที่รู้จากบทก่อน

1. **คลัสเตอร์** คือท่าเรือทั้งท่า มี **Control Plane** เป็นหอบังคับการ และ **Node** เป็นเรือสินค้า (`lab-worker`, `lab-worker2`)
2. **Pod** คือกล่องห้องโดยสารใสที่ห่อตู้สินค้า (container) อยู่บนเรือลำเดียวเสมอ
3. ทุกคำสั่ง `kubectl` ที่ไม่ระบุอะไรเพิ่ม ทำงานกับ namespace `default` ทั้งหมด (ข้อความ `No resources found in default namespace.` ที่เห็นบ่อยในบทก่อนบอกเราอยู่แล้ว)

น้องส้มจึงตัดสินใจ **ทาสีแบ่งโซน** บนแผนผังท่าเรือ ให้แต่ละโซนมีชื่อของตัวเอง มีงบประมาณ มีกฎขนาดกล่อง มีบัตรพนักงานเฉพาะโซน มีด่านตรวจความปลอดภัย และมีรั้วระหว่างโซน แล้วปิดท้ายด้วยการแยกร้านเป็น `som-dev`, `som-staging`, `som-prod` ในคลัสเตอร์เดียว (LAB สุดท้าย)

{{FIG:T02|แผนผังอุปมาใหม่ของบทนี้}}

**ตารางที่ 1** อุปมาท่าเรือที่ใช้ในบทนี้ (ต่อจากบทที่ 1–3)

| Kubernetes | อุปมาท่าเรือ | ใหม่ในบทนี้ |
|---|---|:---:|
| container | ตู้สินค้า | |
| Pod | กล่องห้องโดยสารใสสี teal ห่อตู้ มีป้าย IP 1 ป้าย | |
| Node | เรือสินค้า (`lab-worker`, `lab-worker2`) | |
| Control Plane | หอบังคับการบนท่า (`lab-control-plane`) | |
| คลัสเตอร์ | ท่าเรือทั้งท่า | |
| **Namespace** | **โซนทาสีบนแผนผังท่าเรือ มีป้ายชื่อโซน** เป็นการแบ่งทางทะเบียน ไม่ใช่เรือและไม่ใช่ที่ดินจริง กล่องของโซนเดียวกันอยู่บนเรือหลายลำได้ (วาดเป็นริบบิ้นสีประจำโซนคล้องกล่อง) | ✓ |
| ชื่อเต็ม `namespace/name` | ที่อยู่แบบ "โซน + ชื่อกล่อง" (กล่องชื่อ `snack` มีได้ในหลายโซน) | ✓ |
| namespaced resource | ของประจำโซน (กล่อง Pod, บัตรพนักงาน, ใบโควตา) | ✓ |
| cluster-scoped resource | ของส่วนกลางของท่าเรือ (เรือ, ป้ายโซนเอง, โกดังกลาง = PersistentVolume/StorageClass, ธง VIP = PriorityClass) | ✓ |
| kubeconfig / context | กระเป๋าบัตร: บัตรท่าเรือ (cluster) + บัตรประจำตัว (user) + โซนที่ไปบ่อย (namespace) | ✓ |
| `-n` / `-A` | ไฟฉายส่องโซนเดียว / สปอตไลต์ส่องทั้งท่า | ✓ |
| ResourceQuota | ใบงบประมาณของโซน (มีมาตรวัดใช้ไป/เพดาน) | ✓ |
| LimitRange | ป้ายกฎขนาดกล่องมาตรฐานของโซน (ไม่ระบุขนาด → ติดสติกเกอร์ขนาดมาตรฐานให้) | ✓ |
| User / ServiceAccount | บัตรพนักงานของคน / บัตรของหุ่นยนต์พนักงานอัตโนมัติ | ✓ |
| Role / RoleBinding | การ์ดสิทธิ์ (ทำอะไรได้กับอะไร) / สายคล้องที่ผูกบัตรกับการ์ด ใช้ได้เฉพาะโซนนั้น | ✓ |
| ClusterRole / ClusterRoleBinding | สมุดกฎสิทธิ์มาตรฐานของท่าเรือ / ผูกทั้งท่า | ✓ |
| `kubectl auth can-i` | เครื่องอ่านบัตร ตอบไฟเขียว yes / ไฟแดง no | ✓ |
| Pod Security Admission | ด่านตรวจหน้าโซน 3 ระดับ (privileged/baseline/restricted) 3 โหมด (enforce = ไม้กั้น, warn = กระดิ่ง, audit = สมุดบันทึก) | ✓ |
| NetworkPolicy | รั้วและประตูระหว่างโซน (ประตูเปิดให้เฉพาะโซนที่มีป้ายตรง) | ✓ |
| finalizers | เช็กลิสต์ที่ต้องเคลียร์ครบก่อนปลดป้ายโซน (ค้าง = Terminating) | ✓ |

---

## 2. Namespace คืออะไร

### 2.1 นิยาม

{{FIG:T03|Namespace คือโซนทาสีบนแผนผังท่าเรือ}}

**Namespace** คือกลไกแบ่งกลุ่ม resource ภายใน **คลัสเตอร์เดียว** ออกเป็นส่วน ๆ มีบทบาทหลัก 2 อย่าง

1. **ขอบเขตของชื่อ (scope of names)** ชื่อของ object ต้องไม่ซ้ำกันเฉพาะภายใน namespace เดียวกัน ข้าม namespace ใช้ชื่อซ้ำได้ ชื่อเต็มของ object จึงเป็น `<namespace>/<name>` เช่น `blue/snack` กับ `green/snack` คือ Pod คนละตัว
2. **หน่วยที่ใช้แนบนโยบาย** เครื่องมือหลายตัวของ Kubernetes ทำงาน "ต่อ namespace" ได้แก่ ResourceQuota, LimitRange, RBAC (Role/RoleBinding), Pod Security Admission และ NetworkPolicy ทำให้แต่ละโซนมีงบ สิทธิ์ และกฎความปลอดภัยของตัวเองได้

Namespace เองก็เป็น object ตัวหนึ่ง (`apiVersion: v1`, `kind: Namespace`) เขียนเป็น YAML ได้ เช่นไฟล์ `labs/lab01-create-ns/ns-blue.yaml` ใน LAB 1

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: blue          # ชื่อโซน
  labels:
    lab: "04"         # label ของ namespace เอง (ไว้ค้นด้วย -l)
```

ในแผนผังท่าเรือ ให้นึกถึง **แฟ้มสีประจำโซน** ในหอบังคับการ กล่อง Pod ทุกใบมีริบบิ้นสีบอกว่าเป็นของโซนไหน แต่ตัวกล่องจริงจะอยู่บนเรือลำไหนก็ได้

### 2.2 Namespace ไม่ใช่เครื่อง ไม่ใช่ Node และไม่ใช่ VM

{{FIG:T04|Namespace ไม่ใช่เรือ}}

ความเข้าใจผิดที่พบบ่อยที่สุดคือคิดว่า namespace เป็น "เครื่องแยก" หรือ "พื้นที่จริง" ที่ Pod ถูกขังไว้ ความจริงคือ

- **Pod ใน namespace เดียวกันกระจายอยู่หลาย Node ได้** scheduler เลือกเรือให้ Pod โดยไม่สนใจว่า Pod อยู่ namespace ไหน (เว้นแต่เราจะเขียนกฎ affinity เอง)
- **Node เดียวรับ Pod จากหลาย namespace ได้** Node เป็นของส่วนกลาง (cluster-scoped) ไม่ได้เป็นของ namespace ใด

ผลจริงจาก LAB 1: Pod `snack` 3 ตัวใน 3 namespace อยู่บนเรือ 2 ลำปนกัน

```text
NAMESPACE   NAME    READY   STATUS    RESTARTS   AGE   IP           NODE          NOMINATED NODE   READINESS GATES
blue        snack   1/1     Running   0          7s    10.244.2.2   lab-worker    <none>           <none>
default     snack   1/1     Running   0          6s    10.244.2.3   lab-worker    <none>           <none>
green       snack   1/1     Running   0          6s    10.244.1.2   lab-worker2   <none>           <none>
```

และผลจริงจาก LAB 4: Pod ของ `team-a` และ `team-b` อยู่บน `lab-worker` ลำเดียวกันทั้งหมด

```text
NAMESPACE   NAME     READY   STATUS    RESTARTS   AGE   IP           NODE         NOMINATED NODE   READINESS GATES
team-a      client   1/1     Running   0          8s    10.244.2.7   lab-worker   <none>           <none>
team-a      web      1/1     Running   0          8s    10.244.2.6   lab-worker   <none>           <none>
team-b      client   1/1     Running   0          8s    10.244.2.8   lab-worker   <none>           <none>
```

> **สรุปสั้น ๆ:** namespace แบ่ง **ทะเบียน** (ชื่อ สิทธิ์ งบ กฎ) ไม่ได้แบ่ง **ฮาร์ดแวร์** หรือ **เครือข่าย** ถ้าต้องการให้แต่ละโซนอยู่คนละเรือ ต้องใช้ nodeSelector/affinity/taint จากบทที่ 3 เพิ่มเอง และถ้าต้องการกั้นเครือข่าย ต้องใช้ NetworkPolicy (หัวข้อ 10)

### 2.3 ทำไมต้องมี Namespace

{{FIG:T05|ทำไมต้องมี Namespace}}

รูปแบบการใช้งานที่พบบ่อย

| รูปแบบ | ตัวอย่างชื่อ namespace | เหมาะกับ |
|---|---|---|
| แยกตามทีม | `team-a`, `team-b`, `payments` | หลายทีมใช้คลัสเตอร์ร่วมกัน แต่ละทีมดูแลของตัวเอง |
| แยกตาม environment | `dev`, `staging`, `prod` | แอปเดียวกันหลายขั้นตอนการพัฒนา |
| แยกตามแอป/ระบบ | `som-shop`, `monitoring`, `logging` | แยกระบบที่ไม่เกี่ยวกันให้ดูแลง่าย |
| ทีม + environment | `som-dev`, `som-staging`, `som-prod` | องค์กรที่มีหลายทีมและแต่ละทีมมีหลาย environment (ใช้ใน LAB สุดท้าย) |

เทียบกับอีกทางเลือกคือ **"หนึ่งคลัสเตอร์ต่อทีม/ต่อ environment"**

| | หลาย namespace ในคลัสเตอร์เดียว | หลายคลัสเตอร์ |
|---|---|---|
| ค่าใช้จ่าย | ต่ำ ใช้ control plane และ Node ร่วมกัน | สูง ทุกคลัสเตอร์ต้องมี control plane และ Node ของตัวเอง |
| การดูแล | อัปเกรด/ติดตั้งเครื่องมือครั้งเดียว | ต้องดูแลทีละคลัสเตอร์ |
| การแยกขาด | **soft multi-tenancy** แยกด้วยนโยบาย (RBAC, quota, PSA, NetworkPolicy) แต่ยังใช้ kernel, Node, API server ร่วมกัน | แยกขาดจริง ปัญหาของคลัสเตอร์หนึ่งไม่กระทบอีกคลัสเตอร์ |
| ของที่แยกไม่ได้ | ของ cluster-scoped (Node, CRD, StorageClass) และเวอร์ชันของ Kubernetes | แยกได้ทั้งหมด |

แนวปฏิบัติทั่วไปคือใช้ namespace สำหรับทีมและ environment ที่ไว้ใจกันระดับหนึ่ง และแยกคลัสเตอร์เมื่อต้องการแยกขาดจริง (เช่น prod ขององค์กรใหญ่ หรือลูกค้าคนละบริษัท)

### 2.4 กฎของชื่อและโครงสร้าง

- **namespace ซ้อนกันไม่ได้ (flat)** ไม่มี namespace ย่อยใน namespace และ Namespace object เองไม่ได้อยู่ใน namespace ใด (เป็น cluster-scoped)
- **ชื่อต้องเป็น DNS label ตาม RFC 1123** คือ ตัวพิมพ์เล็ก a-z, ตัวเลข 0-9 และ `-` ขึ้นต้นและลงท้ายด้วยตัวอักษรหรือตัวเลข ยาวไม่เกิน 63 ตัวอักษร เพราะชื่อ namespace ถูกนำไปใช้ในชื่อ DNS (หัวข้อ 9)

ผลจริงเมื่อตั้งชื่อผิดกฎ (LAB 1)

```text
The Namespace "Blue_Zone" is invalid: metadata.name: Invalid value: "Blue_Zone": a lowercase RFC 1123 label must consist of lower case alphanumeric characters or '-', and must start and end with an alphanumeric character (e.g. 'my-name',  or '123-abc', regex used for validation is '[a-z0-9]([-a-z0-9]*[a-z0-9])?')
```

- **คำนำหน้า `kube-` สงวนไว้ให้ระบบตามธรรมเนียม** เอกสาร Kubernetes แนะนำว่า **อย่า** สร้าง namespace ที่ขึ้นต้นด้วย `kube-` เพราะเป็นชื่อที่ระบบใช้ แต่ API **ไม่ได้ห้าม** ผลจริงใน LAB 1

```text
$ kubectl create namespace kube-mine
namespace/kube-mine created
```

กล่าวคือ "ห้าม" ในที่นี้เป็นข้อตกลงร่วมกัน ไม่ใช่กฎ validation ของ API server ผู้เรียนจึงต้องระวังเอง (คอมเมนต์ในไฟล์ `ns-blue.yaml` ที่เขียนว่า "ห้ามขึ้นต้นด้วย kube-" หมายถึงข้อตกลงนี้)

---

## 3. Namespace เริ่มต้นและสิ่งที่อยู่ข้างใน

{{FIG:T06|namespace ตั้งต้น 5 โซนของ kind}}

คลัสเตอร์ kind ที่สร้างด้วย `k8s-up` มี namespace ตั้งแต่เริ่ม 5 ตัว ผลจริงจาก LAB 0

```text
$ kubectl get ns --show-labels
NAME                 STATUS   AGE    LABELS
default              Active   101s   kubernetes.io/metadata.name=default
kube-node-lease      Active   101s   kubernetes.io/metadata.name=kube-node-lease
kube-public          Active   101s   kubernetes.io/metadata.name=kube-public
kube-system          Active   101s   kubernetes.io/metadata.name=kube-system
local-path-storage   Active   97s    kubernetes.io/metadata.name=local-path-storage
```

**ตารางที่ 2** namespace ตั้งต้นและหน้าที่

| namespace | มีในทุกคลัสเตอร์? | หน้าที่ | ลบได้ไหม |
|---|:---:|---|---|
| `default` | ✓ | ที่ที่ object ไปอยู่เมื่อไม่ระบุ namespace | ไม่ได้ ระบบป้องกัน |
| `kube-system` | ✓ | Pod และ object ของระบบ (control plane, DNS, network plugin) | ไม่ได้ ระบบป้องกัน |
| `kube-public` | ✓ | ข้อมูลที่ใครก็อ่านได้ เช่น ConfigMap `cluster-info` | ไม่ได้ ระบบป้องกัน |
| `kube-node-lease` | ✓ | Lease ของแต่ละ Node (heartbeat) | ระบบ **ไม่กัน** แต่ **ห้ามลบ** |
| `local-path-storage` | เฉพาะ kind | ตัวจัดสรร storage ของ StorageClass `standard` | ของ kind ไม่ควรลบ |

ทุก namespace (รวมที่เราสร้างเอง) ได้ label `kubernetes.io/metadata.name=<ชื่อ>` อัตโนมัติ (หัวข้อ 7)

### 3.1 default

`default` คือ namespace ที่ kubectl ใช้เมื่อเราไม่ได้ระบุ `-n` และ context ไม่ได้ตั้ง namespace ไว้ (หัวข้อ 6) ทุก Pod ในบทที่ 1–3 จึงอยู่ที่นี่ ผลจริงจาก LAB 0

```text
$ kubectl describe ns default
Name:         default
Labels:       kubernetes.io/metadata.name=default
Annotations:  <none>
Status:       Active

No resource quota.

No LimitRange resource.
```

`No resource quota.` และ `No LimitRange resource.` บอกว่า `default` ไม่มีงบและไม่มีกฎขนาดกล่องเลย ใครจะสร้างอะไรขนาดเท่าไรก็ได้ ซึ่งเป็นเหตุผลหนึ่งที่ไม่ควรใช้ `default` กับงานจริง

### 3.2 kube-system

{{FIG:T07|kube-system โซนพนักงานของท่าเรือ}}

`kube-system` เป็นโซนพนักงานของท่าเรือ ผลจริงจาก LAB 0 มี Pod 12 ตัว

```text
$ kubectl get pods -n kube-system
NAME                                        READY   STATUS    RESTARTS   AGE
coredns-559f6c778d-5hcpz                    1/1     Running   0          93s
coredns-559f6c778d-6hfdw                    1/1     Running   0          93s
etcd-lab-control-plane                      1/1     Running   0          99s
kindnet-dq2ng                               1/1     Running   0          93s
kindnet-mbmsr                               1/1     Running   0          92s
kindnet-vlb7z                               1/1     Running   0          92s
kube-apiserver-lab-control-plane            1/1     Running   0          99s
kube-controller-manager-lab-control-plane   1/1     Running   0          100s
kube-proxy-6c5br                            1/1     Running   0          93s
kube-proxy-htcvs                            1/1     Running   0          92s
kube-proxy-hzmtb                            1/1     Running   0          92s
kube-scheduler-lab-control-plane            1/1     Running   0          99s
```

| กลุ่ม | Pod | ที่มา (โยงบทก่อน) |
|---|---|---|
| control plane | `etcd-`, `kube-apiserver-`, `kube-controller-manager-`, `kube-scheduler-lab-control-plane` | static Pod ของหอบังคับการ (บทที่ 3 หัวข้อ 14) ชื่อลงท้ายด้วยชื่อ Node |
| DNS ภายในคลัสเตอร์ | `coredns-...` × 2 | สร้างโดย Deployment ชื่อ `coredns` (ตัวสร้าง Pod ที่จะเรียนในบทถัดไป) |
| network | `kindnet-...` × 3, `kube-proxy-...` × 3 | สร้างโดย DaemonSet ให้เรือทุกลำมีลำละ 1 ตัว (บทที่ 3 เห็นเป็น container บนเรือ) |

> ข้อสังเกต: `local-path-provisioner` ของ kind **ไม่ได้** อยู่ใน `kube-system` แต่อยู่ใน `local-path-storage` (หัวข้อ 3.4) และ **ไม่ควร** สร้างหรือลบ Pod ใน `kube-system` เอง

### 3.3 kube-public และ kube-node-lease

{{FIG:T08|kube-public และ kube-node-lease}}

**`kube-public`** ไม่มี Pod เลย มีเพียง ConfigMap ที่ "ประกาศ" ข้อมูลพื้นฐานของคลัสเตอร์ ผลจริงจาก LAB 0

```text
$ kubectl get cm -n kube-public
NAME               DATA   AGE
cluster-info       2      100s
kube-root-ca.crt   1      93s
```

`cluster-info` เก็บที่อยู่ API server และใบรับรอง CA ของคลัสเตอร์ kubeadm (เครื่องมือที่ kind ใช้ตั้งคลัสเตอร์) ตั้งสิทธิ์ให้ ConfigMap นี้ **อ่านได้แม้ยังไม่ล็อกอิน** เพื่อให้ Node ใหม่ใช้ตอนเข้าร่วมคลัสเตอร์ ชื่อ "public" จึงหมายถึงสิ่งที่ตั้งใจเปิดให้ทุกคนอ่าน ไม่ได้แปลว่าของทุกอย่างที่เราวางในนั้นจะเป็นสาธารณะโดยอัตโนมัติ

**`kube-node-lease`** เก็บ **Lease** ของ Node ละ 1 ใบ kubelet ต่ออายุ Lease ของเรือตัวเองทุกประมาณ 10 วินาที เป็นสัญญาณว่า "เรือยังอยู่" (บทที่ 3 หัวข้อ 13) ผลจริงจาก LAB 0

```text
$ kubectl get lease -n kube-node-lease
NAME                HOLDER              AGE
lab-control-plane   lab-control-plane   99s
lab-worker          lab-worker          82s
lab-worker2         lab-worker2         82s
```

### 3.4 local-path-storage (ของ kind)

namespace นี้ **ไม่ได้มีในทุกคลัสเตอร์** kind เพิ่มมาเพื่อวาง `local-path-provisioner` ซึ่งเป็นตัวสร้างพื้นที่เก็บข้อมูลบนดิสก์ของ Node ให้ StorageClass `standard` (ปูทางบทที่ว่าด้วย storage) สังเกตว่าอายุ (AGE) น้อยกว่าตัวอื่นเล็กน้อย เพราะถูกสร้างหลัง control plane พร้อมแล้ว

```text
$ kubectl get pods -n local-path-storage
NAME                                      READY   STATUS    RESTARTS   AGE
local-path-provisioner-75f7fc7dc5-kn7sx   1/1     Running   0          93s
```

### 3.5 ของที่ทุก namespace ได้อัตโนมัติ

ทุกครั้งที่สร้าง namespace ใหม่ controller ในหอบังคับการจะใส่ของ 2 ชิ้นให้ทันที

| object | ใครสร้าง | ใช้ทำอะไร |
|---|---|---|
| ServiceAccount `default` | ServiceAccount controller | ตัวตนเริ่มต้นของ Pod ที่ไม่ได้ระบุ `serviceAccountName` (หัวข้อ 13) |
| ConfigMap `kube-root-ca.crt` | root CA publisher | ใบรับรอง CA ของคลัสเตอร์ ให้ Pod ใช้ตรวจว่าคุยกับ API server ตัวจริง |

ผลจริงจาก LAB 0

```text
$ kubectl get sa,cm -n default
NAME                     AGE
serviceaccount/default   93s

NAME                         DATA   AGE
configmap/kube-root-ca.crt   1      93s
```

---

## 4. Namespaced vs cluster-scoped resources

{{FIG:T09|ของประจำโซนกับของส่วนกลาง}}

resource ใน Kubernetes แบ่งเป็น 2 กลุ่ม

- **namespaced** อยู่ใน namespace ใด namespace หนึ่งเสมอ ชื่อซ้ำได้ข้าม namespace เช่น Pod, ConfigMap, Secret, ServiceAccount, Role, RoleBinding, ResourceQuota, LimitRange, NetworkPolicy, PersistentVolumeClaim, Event, Lease
- **cluster-scoped** เป็นของส่วนกลางของท่าเรือ ไม่อยู่ใน namespace ใด ชื่อต้องไม่ซ้ำทั้งคลัสเตอร์ เช่น Node, Namespace, PersistentVolume, StorageClass, PriorityClass, ClusterRole, ClusterRoleBinding, CSIDriver, IngressClass, RuntimeClass

เหตุผลง่าย ๆ คือ **ของบางอย่างเป็นของส่วนกลางโดยธรรมชาติ** เรือลำหนึ่งรับกล่องจากทุกโซน จึงเป็นของโซนใดโซนหนึ่งไม่ได้ ป้ายโซน (Namespace) ก็ต้องอยู่บนแผนผังกลาง ไม่ใช่อยู่ในโซนตัวเอง โกดังกลาง (PersistentVolume) และแบบฟอร์มขอพื้นที่ (StorageClass) ใช้ร่วมกันทั้งท่า

### 4.1 ดูด้วย kubectl api-resources

{{FIG:T10|api-resources แบ่งสองกลุ่ม}}

ผลจริงจาก LAB 3 (Kubernetes v1.37.0)

```text
$ kubectl api-resources --namespaced=true -o name | wc -l
34
$ kubectl api-resources --namespaced=false -o name | wc -l
37
```

เลือกดูเฉพาะชนิดที่ใช้ในบทนี้ (คอลัมน์ `NAMESPACED` บอก scope)

```text
$ kubectl api-resources | grep -E "^(pods|nodes|namespaces|resourcequotas|limitranges|networkpolicies|roles|clusterroles) "
limitranges                         limits       v1                                true         LimitRange
namespaces                          ns           v1                                false        Namespace
nodes                               no           v1                                false        Node
pods                                po           v1                                true         Pod
resourcequotas                      quota        v1                                true         ResourceQuota
networkpolicies                     netpol       networking.k8s.io/v1              true         NetworkPolicy
clusterroles                                     rbac.authorization.k8s.io/v1      false        ClusterRole
roles                                            rbac.authorization.k8s.io/v1      true         Role
```

คอลัมน์ `SHORTNAMES` ยังบอกชื่อย่อที่ใช้กับ kubectl ได้ เช่น `ns`, `quota`, `limits`, `netpol`, `sa`, `cm`

### 4.2 ผลของ -n กับ cluster-scoped resource

`-n` **ไม่มีผล** กับ resource แบบ cluster-scoped kubectl ไม่ฟ้อง error แต่ก็ไม่ได้กรองอะไร ผลจริงจาก LAB 3

```text
$ kubectl get nodes -n blue
NAME                STATUS   ROLES           AGE     VERSION
lab-control-plane   Ready    control-plane   2m25s   v1.37.0
lab-worker          Ready    <none>          2m15s   v1.37.0
lab-worker2         Ready    <none>          2m15s   v1.37.0

$ kubectl get ns blue -n green
NAME   STATUS   AGE
blue   Active   35s
```

ผลทั้งสองเหมือนไม่ได้ใส่ `-n` เลย ข้อนี้สำคัญเวลาเขียนสคริปต์: การเห็นผลลัพธ์จากคำสั่งที่มี `-n` ไม่ได้แปลว่าของชิ้นนั้นอยู่ใน namespace นั้น

ของ cluster-scoped อื่นที่เห็นใน LAB 3

```text
$ kubectl get sc
NAME                 PROVISIONER             RECLAIMPOLICY   VOLUMEBINDINGMODE      ALLOWVOLUMEEXPANSION   AGE
standard (default)   rancher.io/local-path   Delete          WaitForFirstConsumer   false                  2m21s

$ kubectl get priorityclass
NAME                      VALUE        GLOBAL-DEFAULT   AGE     PREEMPTIONPOLICY
system-cluster-critical   2000000000   false            2m24s   PreemptLowerPriority
system-node-critical      2000001000   false            2m24s   PreemptLowerPriority
```

> **เคล็ดลับ:** `kubectl explain <ชนิด>` บอกโครงสร้างฟิลด์ แต่ไม่ได้บอก scope ชัดเจน วิธีที่ตรงที่สุดคือดูคอลัมน์ `NAMESPACED` ของ `kubectl api-resources`

---

## 5. สร้างและใช้ namespace

### 5.1 สร้างแบบคำสั่งและแบบ YAML

{{FIG:T11|สร้าง namespace สองแบบ}}

| แบบ | คำสั่ง | ข้อดี | ข้อเสีย |
|---|---|---|---|
| imperative (สั่งตรง) | `kubectl create namespace green` | เร็ว เหมาะกับทดลอง | ไม่มีไฟล์บันทึก ใส่ label ต้องสั่งเพิ่ม |
| declarative (YAML) | `kubectl apply -f ns-blue.yaml` | เก็บใน git ได้ ใส่ label/annotation ในไฟล์เดียว สั่งซ้ำได้ | ต้องเขียนไฟล์ |

ผลจริงจาก LAB 1 และเทคนิค `--dry-run=client -o yaml` ที่ช่วย "พิมพ์ YAML ตั้งต้น" ให้โดยไม่สร้างจริง

```text
$ kubectl create namespace green
namespace/green created

$ kubectl create namespace green --dry-run=client -o yaml
apiVersion: v1
kind: Namespace
metadata:
  name: green
spec: {}
status: {}

$ kubectl apply -f labs/lab01-create-ns/ns-blue.yaml
namespace/blue created

$ kubectl get ns blue green --show-labels
NAME    STATUS   AGE   LABELS
blue    Active   0s    kubernetes.io/metadata.name=blue,lab=04
green   Active   0s    kubernetes.io/metadata.name=green
```

### 5.2 metadata.namespace ในไฟล์ เทียบกับ -n

{{FIG:T12|metadata.namespace เทียบกับ -n}}

object แบบ namespaced จะไปอยู่ namespace ไหน ขึ้นกับ 2 แหล่ง คือ `metadata.namespace` ในไฟล์ (ป้ายที่อยู่ติดกล่อง) และ `-n`/`--namespace` ตอนสั่ง (คำสั่งปากเปล่า)

**ตารางที่ 3** กฎการเลือก namespace (ยืนยันใน LAB 1)

| ในไฟล์ (`metadata.namespace`) | ตอนสั่ง (`-n`) | ผล |
|---|---|---|
| ไม่มี | ไม่มี | ไป namespace ของ context (ปกติ `default`) |
| ไม่มี | `-n blue` | ไป `blue` |
| `green` | ไม่มี | ไป `green` |
| `green` | `-n green` | ไป `green` |
| `green` | `-n blue` | **error** ไม่สร้างอะไรเลย |

ผลจริงเมื่อไฟล์ `snack-green-pod.yaml` (มี `namespace: green`) ถูกสั่งด้วย `-n blue`

```text
$ kubectl apply -f labs/lab01-create-ns/snack-green-pod.yaml -n blue
error: the namespace from the provided object "green" does not match the namespace "blue". You must pass '--namespace=green' to perform this operation.
```

**แนวปฏิบัติ**

- ไฟล์ที่ตั้งใจใช้ซ้ำหลาย environment (เช่น `som-shop.yaml` ใน LAB สุดท้าย) **ไม่ใส่** `metadata.namespace` แล้วเลือกด้วย `-n` ตอนสั่ง ไฟล์เดียวจึงใช้ได้ทั้ง dev, staging, prod
- ไฟล์ที่เป็นของ namespace เดียวแน่นอน (เช่น `prod-guardrails.yaml` ที่เป็นงบของ prod เท่านั้น) **ใส่** `metadata.namespace` เพื่อกันวางผิดโซน

### 5.3 ชื่อซ้ำได้ข้าม namespace

{{FIG:T13|ชื่อซ้ำได้ข้าม namespace}}

ไฟล์ `snack-pod.yaml` ไฟล์เดียว (ไม่มี `metadata.namespace`) สั่ง 3 ครั้งได้ Pod 3 ตัวชื่อ `snack` เหมือนกันใน `blue`, `green`, `default` (ผลจริงดูหัวข้อ 2.2) เพราะชื่อเต็มคือ `blue/snack`, `green/snack`, `default/snack`

แต่ **ใน namespace เดียวกันชื่อต้องไม่ซ้ำ** ผลจริงจาก LAB 1

```text
$ kubectl create -f labs/lab01-create-ns/snack-pod.yaml -n blue
Error from server (AlreadyExists): error when creating "labs/lab01-create-ns/snack-pod.yaml": pods "snack" already exists

$ kubectl apply -f labs/lab01-create-ns/snack-pod.yaml -n blue
pod/snack unchanged
```

สังเกตความต่าง: `kubectl create` ต้องการ "สร้างใหม่" จึงได้ `AlreadyExists` ส่วน `kubectl apply` ต้องการ "ทำให้เหมือนไฟล์" เมื่อของเดิมตรงกับไฟล์แล้วจึงตอบ `unchanged` (ถ้าไฟล์ต่างจากเดิม apply จะพยายามแก้ object เดิม ไม่ได้สร้างตัวใหม่)

### 5.4 -n และ -A

{{FIG:T14|-n ส่องทีละโซน -A ส่องทั้งท่า}}

| ตัวเลือก | ความหมาย | ตัวอย่าง |
|---|---|---|
| `-n <ns>` / `--namespace=<ns>` | ทำงานกับ namespace เดียว | `kubectl get pods -n blue` |
| `-A` / `--all-namespaces` | อ่านจากทุก namespace และเพิ่มคอลัมน์ `NAMESPACE` | `kubectl get pods -A` |
| ใช้ร่วมกับ `-l` | กรองด้วย label ข้ามทุก namespace | `kubectl get pods -A -l app=snack` |

`-A` ใช้กับการ "ดูรายการ" เท่านั้น ใช้ระบุชื่อตัวเดียวข้ามทุก namespace ไม่ได้ ผลจริงจาก LAB 1

```text
$ kubectl get pod snack -A
error: a resource cannot be retrieved by name across all namespaces

$ kubectl get pods -A --field-selector metadata.name=snack
NAMESPACE   NAME    READY   STATUS    RESTARTS   AGE
blue        snack   1/1     Running   0          9s
default     snack   1/1     Running   0          8s
green       snack   1/1     Running   0          8s
```

`--field-selector metadata.name=snack` คือการกรองด้วยฟิลด์ของ object ซึ่งใช้กับ `-A` ได้

อีกวิธีหนึ่งที่ใช้ดูว่า object อยู่ namespace ไหนคือ jsonpath

```text
$ kubectl get pod snack -n blue -o jsonpath="{.metadata.namespace}{\"\n\"}"
blue
```

### 5.5 Namespace object มีอะไรข้างใน

ผลจริงจาก LAB 1

```text
$ kubectl get ns blue -o yaml
apiVersion: v1
kind: Namespace
metadata:
  annotations:
    kubectl.kubernetes.io/last-applied-configuration: |
      {"apiVersion":"v1","kind":"Namespace","metadata":{"annotations":{},"labels":{"lab":"04"},"name":"blue"}}
  creationTimestamp: "2026-10-04T13:29:35Z"
  labels:
    kubernetes.io/metadata.name: blue
    lab: "04"
  name: blue
  resourceVersion: "736"
  uid: 477a7329-64c3-447f-ab6f-4cf12b358c36
spec:
  finalizers:
  - kubernetes
status:
  phase: Active
```

- `metadata` **ไม่มี** ฟิลด์ `namespace` เพราะ Namespace เป็น cluster-scoped
- `labels` มี `kubernetes.io/metadata.name: blue` ที่ระบบใส่ให้ (หัวข้อ 7) และ `lab: "04"` ที่มาจากไฟล์
- `spec.finalizers: [kubernetes]` คือเช็กลิสต์ที่ต้องเคลียร์ก่อนลบ namespace ได้ (หัวข้อ 8)
- `status.phase` มีได้ 2 ค่า คือ `Active` และ `Terminating`

---

## 6. kubeconfig, context และ namespace เริ่มต้น

### 6.1 โครงสร้าง kubeconfig

{{FIG:T15|kubeconfig เหมือนกระเป๋าบัตร}}

kubectl อ่านการตั้งค่าจากไฟล์ **kubeconfig** (ค่าเริ่มต้น `~/.kube/config`) ซึ่งเหมือนกระเป๋าบัตร มี 3 ส่วนหลักและตัวชี้ 1 ตัว

| ส่วน | อุปมา | เก็บอะไร |
|---|---|---|
| `clusters` | บัตรท่าเรือ | ที่อยู่ API server (`server`) และ CA ของคลัสเตอร์ |
| `users` | บัตรประจำตัว | หลักฐานยืนยันตัวตน เช่น client certificate + key หรือ token |
| `contexts` | บัตรรวม | จับคู่ cluster + user + **namespace** เริ่มต้น (ไม่บังคับ) |
| `current-context` | บัตรที่หยิบใช้อยู่ | ชื่อ context ที่ kubectl ใช้ตอนนี้ |

ผลจริงจาก LAB 2 (`--minify` = แสดงเฉพาะส่วนที่ context ปัจจุบันใช้, `DATA+OMITTED` = kubectl ซ่อนข้อมูลลับให้)

```text
$ kubectl config view --minify
apiVersion: v1
clusters:
- cluster:
    certificate-authority-data: DATA+OMITTED
    server: https://127.0.0.1:41301
  name: kind-lab
contexts:
- context:
    cluster: kind-lab
    user: kind-lab
  name: kind-lab
current-context: kind-lab
kind: Config
users:
- name: kind-lab
  user:
    client-certificate-data: DATA+OMITTED
    client-key-data: DATA+OMITTED
```

(เลข port ใน `server` kind สุ่มให้ตอนสร้างคลัสเตอร์ เครื่องผู้เรียนจะได้เลขอื่น)

สังเกต 2 อย่างที่จะใช้ต่อ

1. context `kind-lab` **ไม่มีบรรทัด `namespace`** จึงใช้ `default`
2. user `kind-lab` ยืนยันตัวตนด้วย **client certificate** (`client-certificate-data`, `client-key-data`) ไม่ใช่ token ซึ่งเป็นที่มาของกับดักในหัวข้อ 13.5

### 6.2 เปลี่ยน namespace เริ่มต้นของ context

{{FIG:T16|set-context เปลี่ยนโซนเริ่มต้น}}

ถ้าทำงานใน namespace เดียวนาน ๆ การพิมพ์ `-n blue` ทุกคำสั่งน่าเบื่อ เราตั้ง namespace ให้ context ได้ ผลจริงจาก LAB 2

```text
$ kubectl config get-contexts
CURRENT   NAME       CLUSTER    AUTHINFO   NAMESPACE
*         kind-lab   kind-lab   kind-lab   

$ kubectl config set-context --current --namespace=blue
Context "kind-lab" modified.

$ kubectl config get-contexts
CURRENT   NAME       CLUSTER    AUTHINFO   NAMESPACE
*         kind-lab   kind-lab   kind-lab   blue

$ kubectl get pods
NAME    READY   STATUS    RESTARTS   AGE
snack   1/1     Running   0          26s
```

คอลัมน์ `NAMESPACE` ตอนเริ่ม **ว่าง** (= ใช้ `default`) หลังตั้งค่ากลายเป็น `blue` และ `kubectl get pods` ที่ไม่มี `-n` ก็ส่องโซน blue ทันที Pod ใหม่ที่สร้างโดยไม่ระบุ namespace ก็ไปอยู่ `blue` ด้วย

ดู namespace ปัจจุบันแบบสั้น และคืนค่า

```bash
kubectl config view --minify -o jsonpath='{..namespace}'; echo   # ว่าง = default
kubectl config set-context --current --namespace=default
```

หลังคืนค่า คอลัมน์ `NAMESPACE` จะแสดง `default` (ไม่กลับเป็นช่องว่าง แต่ความหมายเหมือนกัน)

> ⚠️ **ข้อควรระวัง:** การเปลี่ยน namespace ของ context มีผลกับ **ทุก terminal** ที่ใช้ kubeconfig ไฟล์เดียวกัน และอยู่ถาวรจนกว่าจะเปลี่ยนกลับ ถ้าลืม คำสั่งถัดไปอาจสร้างหรือ **ลบ** ของผิดโซน
> - ตรวจด้วย `kubectl config get-contexts` (คอลัมน์ `NAMESPACE`) ก่อนสั่งคำสั่งอันตราย
> - กับ namespace สำคัญอย่าง prod และในสคริปต์ ให้ใส่ `-n` **ทุกครั้ง** อย่าพึ่ง context
> - เครื่องมือเสริม `kubens`/`kubectx` ช่วยสลับ namespace/context ได้เร็ว (กล่าวถึงเท่านั้น ไม่ได้ติดตั้งใน k8s-lab)

นอกจากเปลี่ยน namespace ของ context เดิม เรายังสร้าง **context ใหม่** ที่จับคู่ cluster เดิมกับ user อื่นและ namespace อื่นได้ด้วย `kubectl config set-context <ชื่อ> --cluster=... --user=... --namespace=...` แล้วเลือกใช้ทีละคำสั่งด้วย `kubectl --context <ชื่อ> ...` (ใช้ในหัวข้อ 13.5 และ LAB 7)

---

## 7. Label ของ namespace

{{FIG:T17|label ของ namespace}}

namespace ติด label ได้เหมือน Pod และมี label 2 ประเภท

| ประเภท | ตัวอย่าง | ใครใส่ | ใช้ทำอะไร |
|---|---|---|---|
| label อัตโนมัติ | `kubernetes.io/metadata.name=som-prod` | ระบบใส่ให้ทุก namespace ค่าเท่ากับชื่อ แก้ให้ต่างจากชื่อไม่ได้ | อ้าง namespace ใน `namespaceSelector` ของ NetworkPolicy (หัวข้อ 10) โดยไม่ต้องติด label เอง |
| label ของเรา | `env=prod`, `team=som` | เราเอง (ในไฟล์หรือ `kubectl label ns`) | ค้นหา/จัดกลุ่ม namespace, อ้างใน selector |
| label พิเศษ | `pod-security.kubernetes.io/enforce=restricted` | เราเอง | สั่งงาน Pod Security Admission (หัวข้อ 14) |

ผลจริงจาก LAB สุดท้าย: ค้นหา namespace ด้วย label และแสดงค่า label เป็นคอลัมน์ด้วย `-L`

```text
$ kubectl get ns -l team=som -L env
NAME          STATUS   AGE   ENV
som-dev       Active   0s    dev
som-prod      Active   0s    prod
som-staging   Active   0s    staging
```

ติด/แก้/ลบ label ด้วยคำสั่ง

```bash
kubectl label ns blue env=dev                 # ติด label ใหม่
kubectl label ns blue env=test --overwrite    # เปลี่ยนค่าที่มีอยู่ต้องใส่ --overwrite
kubectl label ns blue env-                    # ลบ label (ใส่ - ต่อท้ายชื่อ)
```

---

## 8. การลบ namespace

### 8.1 ลบโซน = ลบทุกอย่างข้างใน

{{FIG:T18|ลบ namespace ลบทุกอย่างข้างใน}}

`kubectl delete namespace <ชื่อ>` (หรือ `kubectl delete ns <ชื่อ>`) ลบ **ทุก object แบบ namespaced ใน namespace นั้น** ทั้ง Pod, ServiceAccount, Role, RoleBinding, ConfigMap, ResourceQuota ฯลฯ ในคำสั่งเดียว **ไม่มีถังขยะให้กู้คืน** แต่ของ cluster-scoped (Node, PersistentVolume, ClusterRole) ไม่ถูกลบ

ใน LAB 9 namespace `doomed` มีของ 7 ชนิด ผลจริงก่อนลบ

```text
$ kubectl get all,sa,role,rolebinding,cm,quota -n doomed
NAME          READY   STATUS    RESTARTS   AGE
pod/crate-1   1/1     Running   0          0s
pod/crate-2   1/1     Running   0          0s

NAME                     AGE
serviceaccount/cleaner   0s
serviceaccount/default   0s

NAME                                          CREATED AT
role.rbac.authorization.k8s.io/cleaner-role   2026-10-04T13:31:41Z

NAME                                                    ROLE                AGE
rolebinding.rbac.authorization.k8s.io/cleaner-binding   Role/cleaner-role   1s

NAME                         DATA   AGE
configmap/kube-root-ca.crt   1      1s
configmap/menu               1      1s

NAME                         REQUEST     LIMIT   AGE
resourcequota/doomed-quota   pods: 2/5           1s
```

> **ระวัง:** `kubectl get all` **ไม่ได้** แสดงทุกอย่างจริง ไม่รวม ConfigMap, ServiceAccount, Role, RoleBinding, ResourceQuota ฯลฯ ต้องระบุชนิดเพิ่มเองแบบคำสั่งข้างบน ส่วน `kubectl delete ns` ลบครบทุกชนิดจริง

### 8.2 ลำดับเหตุการณ์และ finalizers

{{FIG:T19|finalizers เช็กลิสต์ก่อนปลดป้ายโซน}}

**finalizer** คือรายการ "งานที่ต้องทำให้เสร็จก่อนลบ object ได้จริง" เขียนอยู่ใน object เอง Namespace มี finalizer ชื่อ `kubernetes` อยู่ใน `spec.finalizers` (ผลจริง `["kubernetes"]`) ลำดับเมื่อสั่งลบ

1. API server ตั้ง `deletionTimestamp` และเปลี่ยน `status.phase` เป็น **`Terminating`** ทันที
2. ระหว่าง Terminating **สร้างของใหม่ใน namespace นั้นไม่ได้**
3. namespace controller ไล่ลบ object ทุกชนิดข้างใน (Pod ต้องรอ grace period ของตัวเอง)
4. เมื่อข้างในว่างแล้ว controller เอา finalizer `kubernetes` ออก
5. finalizer ว่าง → Namespace object หายไปจริง

ผลจริงจาก LAB 9 (Pod ใน `doomed` ตั้ง `terminationGracePeriodSeconds: 15` ให้ Terminating นานพอสังเกต)

```text
$ kubectl delete ns doomed --wait=false
namespace "doomed" deleted

$ kubectl get ns doomed
NAME     STATUS        AGE
doomed   Terminating   1s

$ kubectl run x -n doomed --image=busybox:1.36 -- sleep 60
Error from server (Forbidden): pods "x" is forbidden: unable to create new content in namespace doomed because it is being terminated

$ time kubectl wait --for=delete ns/doomed --timeout=120s
namespace/doomed condition met

real	0m20.096s
```

คำว่า `deleted` ที่ kubectl ตอบหมายถึง "รับคำขอลบแล้ว" ไม่ได้หมายถึงหายแล้ว ปกติ `kubectl delete ns` (ไม่ใส่ `--wait=false`) จะรอจนหายจริงจึงคืน prompt ใน LAB สุดท้าย namespace ที่มีร้าน som-shop ใช้เวลาลบราว 10 วินาที

### 8.3 namespace ที่ลบไม่ได้ และกรณีค้าง Terminating

ผลจริงจาก LAB 9 (`--dry-run=server` = ให้ API server ตรวจทุกด่านแต่ไม่ลบจริง)

```text
$ kubectl delete ns default
Error from server (Forbidden): namespaces "default" is forbidden: this namespace may not be deleted

$ kubectl delete ns kube-system --dry-run=server
Error from server (Forbidden): namespaces "kube-system" is forbidden: this namespace may not be deleted

$ kubectl delete ns kube-public --dry-run=server
Error from server (Forbidden): namespaces "kube-public" is forbidden: this namespace may not be deleted

$ kubectl delete ns kube-node-lease --dry-run=server
namespace "kube-node-lease" deleted (server dry run)
```

ระบบป้องกันการลบเพียง **3 ตัว** คือ `default`, `kube-system`, `kube-public` ส่วน `kube-node-lease` **ระบบไม่กัน** (dry-run ผ่าน) แต่ **ห้ามลบเด็ดขาด** เพราะเป็นที่เก็บ heartbeat ของ Node ทุกลำ (`local-path-storage` ก็ไม่ควรลบเช่นกัน)

namespace อาจ **ค้าง Terminating นาน** ได้ เช่น มี object ที่มี finalizer ของตัวเองแต่ controller ที่ต้องเคลียร์ finalizer นั้นถูกลบไปแล้ว หรือ API ส่วนขยายที่ลงทะเบียนไว้ล่มทำให้ลิสต์ของข้างในไม่ครบ วิธีตรวจคือ

```bash
kubectl get ns <ชื่อ> -o jsonpath='{.status.conditions}'   # ดูว่าติดอะไร
kubectl api-resources --verbs=list --namespaced -o name \
  | xargs -n 1 kubectl get --show-kind --ignore-not-found -n <ชื่อ>   # หาของที่ยังเหลือ
```

> การไปแก้ลบ finalizer ออกเองเป็นทางลัดที่อาจทิ้งของค้างในระบบ (เช่น ทรัพยากรภายนอกที่ controller ยังไม่ได้เก็บกวาด) อย่าทำถ้ายังไม่เข้าใจว่า finalizer นั้นรออะไรอยู่

---

## 9. Namespace ไม่ได้แยก network และ node

### 9.1 Pod ต่างโซนคุยกันด้วย Pod IP ได้ทันที

{{FIG:T20|Pod ต่าง namespace คุยกันได้}}

เครือข่าย Pod ใน Kubernetes เป็น **flat network** (บทที่ 1) ทุก Pod ได้ IP ของตัวเองและคุยกับทุก Pod ได้โดยตรง ไม่ว่าจะอยู่ namespace ไหนหรือเรือลำไหน namespace **ไม่ได้สร้างกำแพงเครือข่าย** ให้เอง ผลจริงจาก LAB 4 (ก่อนมี NetworkPolicy)

```text
$ kubectl -n team-b exec client -- wget -qO- -T 3 http://10.244.2.6 | grep -o '<title>.*</title>'
<title>Welcome to nginx!</title>
```

`client` ใน `team-b` เข้าเว็บ `web` ของ `team-a` ได้ทันที (IP ในรูปที่ 20 และใน LAB เป็นตัวอย่าง IP จริงในเครื่องผู้เรียนต่างได้ ให้ดูจาก `kubectl get pod -o wide`)

### 9.2 DNS และ search domain (ทฤษฎีปูทาง)

{{FIG:T21|search domain ของ resolv.conf}}

แม้เครือข่ายไม่ได้แยก แต่ **ชื่อ DNS** ผูกกับ namespace ผลจริงจาก LAB 4

```text
$ kubectl -n team-b exec client -- cat /etc/resolv.conf
search team-b.svc.cluster.local svc.cluster.local cluster.local
nameserver 10.96.0.10
options ndots:5

$ kubectl -n team-a exec client -- cat /etc/resolv.conf
search team-a.svc.cluster.local svc.cluster.local cluster.local
nameserver 10.96.0.10
options ndots:5
```

- `nameserver 10.96.0.10` คือที่อยู่ของ CoreDNS ใน `kube-system`
- `search` ขึ้นต้นด้วย **`<namespace ของ Pod>.svc.cluster.local`** เมื่อ Pod ค้นชื่อสั้น ระบบจะลองต่อท้ายด้วย search domain ตามลำดับ

บทถัดไปจะเรียน **Service** ซึ่งเป็นที่อยู่คงที่ของกลุ่ม Pod ชื่อ DNS เต็มของ Service คือ `<service>.<namespace>.svc.cluster.local` ผลของ search domain คือ

| ชื่อที่ Pod ใน `team-b` เรียก | ถูกค้นเป็น | หาเจอ Service ใน |
|---|---|---|
| `web` | `web.team-b.svc.cluster.local` | `team-b` เท่านั้น |
| `web.team-a` | `web.team-a.svc.cluster.local` | `team-a` |
| `web.team-a.svc.cluster.local` | ชื่อเต็ม | `team-a` |

กล่าวคือ **ชื่อสั้นหาได้เฉพาะในโซนตัวเอง ข้ามโซนต้องเติมชื่อ namespace** ซึ่งเป็นประโยชน์ เพราะแอปเดียวกันที่เรียกชื่อสั้น `db` จะได้ฐานข้อมูลของ environment ตัวเองเสมอ (LAB ของบทนี้ยังไม่สร้าง Service จึงดูแค่ไฟล์ `resolv.conf`)

### 9.3 namespace ไม่ใช่ขอบเขตความปลอดภัยที่สมบูรณ์

namespace เพียงอย่างเดียวให้แค่ "แยกชื่อ" ส่วนการแยกอื่น ๆ ต้องเพิ่มเอง

| อยากแยกอะไร | ใช้อะไร | หัวข้อ |
|---|---|---|
| เครือข่าย (ใครคุยกับใครได้) | NetworkPolicy | 10 |
| ทรัพยากรรวมของโซน | ResourceQuota | 11 |
| ขนาดต่อ container และค่าตั้งต้น | LimitRange | 12 |
| สิทธิ์เรียก API | RBAC | 13 |
| ความปลอดภัยของ Pod (root, privileged) | Pod Security Admission | 14 |
| เรือ (Node) | nodeSelector/affinity/taint | บทที่ 3 |

---
