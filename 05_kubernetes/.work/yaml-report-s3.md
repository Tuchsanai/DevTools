ดำเนินการครบครั้งที่ 3 แล้ว โดยเพิ่มหัวข้อ “อ่าน YAML ของแล็บนี้” หลัง Clone และเลื่อนเลขหัวข้อเดิมต่อเนื่องทุกแล็บ

| แล็บ | ไฟล์ `.yaml` ที่ครอบ | field/กลไกใหม่ที่อธิบาย | README |
|---|---|---|---:|
| [015](/root/workspace/DevTools/05_kubernetes/03_Session3_Application_Deployment/015-assembling-a-real-application/README.md) | `manifests/01-06` (6) | โครง `manifests/`, `apply/diff/get -f` | 422 บรรทัด |
| [016](/root/workspace/DevTools/05_kubernetes/03_Session3_Application_Deployment/016-adding-a-database/README.md) | `manifests/01-10` (10) | ทบทวน PVC และ `strategy: Recreate` | 401 บรรทัด |
| [017](/root/workspace/DevTools/05_kubernetes/03_Session3_Application_Deployment/017-ingress-the-front-door/README.md) | `manifests/01-10`, `06-ingress-bad.yaml` (11) | `ingressClassName`, `rules/paths`, `pathType`, backend, `host`, `tls` | 410 บรรทัด |
| [018](/root/workspace/DevTools/05_kubernetes/03_Session3_Application_Deployment/018-updating-without-downtime/README.md) | `manifests/01-10`, `02-web-recreate.yaml` (11) | RollingUpdate, Recreate, `maxSurge`, `maxUnavailable`, `minReadySeconds`, `revisionHistoryLimit` | 425 บรรทัด |
| [019](/root/workspace/DevTools/05_kubernetes/03_Session3_Application_Deployment/019-telling-kubernetes-what-you-need/README.md) | `manifests/02,03,06`, `03-web-too-big.yaml`, `04-web-oom.yaml` (5) | requests/limits, CPU/memory units, QoS | 437 บรรทัด |
| [020](/root/workspace/DevTools/05_kubernetes/03_Session3_Application_Deployment/020-reading-the-symptoms/README.md) | `broken/01-04`, `fixed/01-04`, `exercise/05` (9) | อ่าน manifest ที่พัง: request, image, command, selector, targetPort | 434 บรรทัด |
| [021](/root/workspace/DevTools/05_kubernetes/03_Session3_Application_Deployment/021-the-big-picture/README.md) | `manifests/01-10` (10) | อ่าน reference ข้าม Ingress → Service → Pod และ Config/Storage | 424 บรรทัด |

[YAML_Guide.md](/root/workspace/DevTools/05_kubernetes/03_Session3_Application_Deployment/YAML_Guide.md) มี 269 บรรทัด โครงหัวข้อคือ:

- สรุปโครง object ใน 5 บรรทัด
- Ingress
- resources และ QoS class
- strategy
- โครงโฟลเดอร์ manifests
- manifest ที่พังโดยตั้งใจของแล็บ 020
- ตารางสรุป field ทั้งหมด

เพิ่มลิงก์คู่มือไว้ช่วงต้นของ [README ระดับครั้ง](/root/workspace/DevTools/05_kubernetes/03_Session3_Application_Deployment/README.md:7) แล้ว โดยไม่แก้ส่วนอื่น

ผลตรวจ:

- YAML ทั้ง 62 ไฟล์ผ่าน `kubectl apply --dry-run=client`
- ตรวจ field ด้วย API server Kubernetes `v1.36.4`
- `check-readme.py`: exit 0, 112 OK, 0 FAIL; มี 7 WARN เฉพาะเกินเป้าหมาย 400 บรรทัด แต่ทุกไฟล์อยู่ภายในเพดาน 450
- `check-yaml-teaching.py`: exit 0, `YAML-TEACHING FAILS = 0`
- anchor และลิงก์ทั้งหมดผ่านตัวตรวจ

สิ่งที่ไม่แน่ใจ: ไม่มี field ที่ยังไม่ได้ตรวจ ทั้งนี้ `pathType: ImplementationSpecific` และพฤติกรรม TLS บางส่วนขึ้นกับ ingress controller ส่วน request ที่ไม่มีทั้ง request/limit ถูกระบุเป็น implementation-defined ตาม `kubectl explain` v1.36

ยืนยันลบ container `devtools-k8s-yaml-s3` แล้ว และตรวจไม่พบ container ชื่อนี้ค้างอยู่ครับ