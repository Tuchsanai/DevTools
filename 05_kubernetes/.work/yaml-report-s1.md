ดำเนินการครบแล้ว: เพิ่มการสอน YAML ใน README แล็บ 001–007, สร้าง [YAML_Guide.md](/root/workspace/DevTools/05_kubernetes/01_Session1_Kubernetes_Basics/YAML_Guide.md) และเพิ่มลิงก์หนึ่งบรรทัดใน [README ระดับครั้ง](/root/workspace/DevTools/05_kubernetes/01_Session1_Kubernetes_Basics/README.md)

| แล็บ | ไฟล์ `.yaml` ที่ครอบ | field ใหม่ที่อธิบาย | README หลังแก้ |
|---|---|---|---:|
| [001](/root/workspace/DevTools/05_kubernetes/01_Session1_Kubernetes_Basics/001-kubernetes-introduction/README.md) | ไม่มี manifest | การอ่าน `metadata` / `spec` / `status` จาก object จริง | 414 |
| [002](/root/workspace/DevTools/05_kubernetes/01_Session1_Kubernetes_Basics/002-kubectl-and-namespace/README.md) | ไม่มี manifest | Namespace, request/context และ `status` ที่ระบบเขียน | 399 |
| [003](/root/workspace/DevTools/05_kubernetes/01_Session1_Kubernetes_Basics/003-pod-the-smallest-unit/README.md) | `02-pod-with-sidecar.yaml` | `containers[]`, `name`, `image`, `imagePullPolicy`, `containerPort`, `command`, `args`, multi-container | 442 |
| [004](/root/workspace/DevTools/05_kubernetes/01_Session1_Kubernetes_Basics/004-declarative-yaml/README.md) | `01-pod.yaml`, `02-pod-v2.yaml`, `03-pod-typo.yaml` | โครง object, YAML syntax, `apiVersion`, `kind`, `metadata`, `spec/status`, Pod immutability | 437 |
| [005](/root/workspace/DevTools/05_kubernetes/01_Session1_Kubernetes_Basics/005-labels-the-glue/README.md) | `01-pods-with-labels.yaml` | multi-document `---` และ labels map | 418 |
| [006](/root/workspace/DevTools/05_kubernetes/01_Session1_Kubernetes_Basics/006-desired-state-and-self-healing/README.md) | `01-replicaset.yaml`, `02-door.yaml` | `replicas`, `selector.matchLabels`, `template`, namespace จาก `-n`, ภาพรวม Service/Ingress | 439 |
| [007](/root/workspace/DevTools/05_kubernetes/01_Session1_Kubernetes_Basics/007-deployment-manages-change/README.md) | `01-deployment.yaml`, `02-door.yaml`, `03-deployment-v2.yaml` | Deployment strategy/defaults, `minReadySeconds`, `revisionHistoryLimit`, change-cause, `fieldRef`, namespace ในไฟล์ | 450 |

เลขหัวข้อหลัง “อ่าน YAML ของแล็บนี้” ถูกเลื่อนและเรียงต่อเนื่องทุกแล็บ โดยไม่แก้แนวคิดหลัก ขั้นตอน หรือ Expected output เดิม

โครง `YAML_Guide.md` มี 296 บรรทัด:

- อ่าน YAML ให้เป็น
  - ไวยากรณ์ที่ต้องอ่านออก
- Pod
- ReplicaSet
- Deployment
- Downward API ด้วย `fieldRef`
- namespace ในไฟล์
- Service และ Ingress
- ตารางสรุป field ของครั้งนี้

ผลตรวจ:

- `check-readme.py`: exit `0`, **0 FAIL**, 6 WARN เฉพาะ README ที่เกินเป้าหมายแนะนำ 400 บรรทัด แต่ทุกไฟล์ยังไม่เกินเพดาน 450
- `check-yaml-teaching.py`: exit `0`, **0 FAIL**, ทุก manifest ถูกกล่าวถึงและทุก anchor ใช้งานได้
- YAML syntax: อ่านได้ครบทั้ง 10 ไฟล์ รวม 14 documents
- ตรวจ default และความหมายกับ [Kubernetes v1.36.4 OpenAPI](https://raw.githubusercontent.com/kubernetes/kubernetes/v1.36.4/api/openapi-spec/swagger.json) และเอกสาร v1.36 เรื่อง [Deployment](https://v1-36.docs.kubernetes.io/docs/concepts/workloads/controllers/deployment/), [image pull policy](https://v1-36.docs.kubernetes.io/docs/concepts/containers/images/) และ [Pod lifecycle](https://v1-36.docs.kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/)

สิ่งที่ไม่แน่ใจ: ไม่มี field ที่ค้างไม่แน่ใจ หลังตรวจ OpenAPI แล้ว อย่างไรก็ตาม `k8s-bootstrap` ใน container แยกล้มสองรอบเพราะ nested kubelet เริ่มไม่ได้ จึงไม่ได้ผล `kubectl explain` จาก runtime และใช้เอกสารทางการ v1.36.4 แทนตามสเปก

ยืนยันลบ container งาน `devtools-k8s-yaml-s1` แล้ว และผล `docker ps -a` ที่กรองชื่อนี้ว่าง ไม่มี port หรือ container ของงานค้างอยู่.