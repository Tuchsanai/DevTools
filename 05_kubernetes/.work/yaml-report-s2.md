ดำเนินการครบตามสเปกแล้ว:

- เพิ่มหัวข้อ “อ่าน YAML ของแล็บนี้” หลัง Clone พร้อมเลื่อนเลขหัวข้อ
- สร้าง [YAML_Guide.md](/root/workspace/DevTools/05_kubernetes/02_Session2_Networking_Config_Storage/YAML_Guide.md)
- เพิ่มลิงก์คู่มือใน [README ระดับครั้ง](/root/workspace/DevTools/05_kubernetes/02_Session2_Networking_Config_Storage/README.md)

| แล็บ | ไฟล์ `.yaml` ที่ครอบ | field ใหม่ที่อธิบาย | README |
|---|---|---|---:|
| [008](/root/workspace/DevTools/05_kubernetes/02_Session2_Networking_Config_Storage/008-why-we-need-service/README.md) | `01-web.yaml`, `02-api.yaml`, `03-web-ip.yaml`, `04-api-service.yaml`, `05-web-by-name.yaml` | Service selector, port, targetPort, protocol, ClusterIP default, DNS, EndpointSlice | 436 |
| [009](/root/workspace/DevTools/05_kubernetes/02_Session2_Networking_Config_Storage/009-service-types-and-access/README.md) | `01-api.yaml`, `02-web-nodeport.yaml`, `03-nodeport-bad.yaml` | ClusterIP/NodePort, nodePort allocation/range, port mapping | 432 |
| [010](/root/workspace/DevTools/05_kubernetes/02_Session2_Networking_Config_Storage/010-configmap-separate-config/README.md) | `01-web.yaml`, `02-configmap.yaml`, `03-web-envfrom.yaml`, `04-configmap-rose.yaml` | ConfigMap data, envFrom, configMapKeyRef, file mount, restart behavior | 423 |
| [011](/root/workspace/DevTools/05_kubernetes/02_Session2_Networking_Config_Storage/011-secret-and-why-not-configmap/README.md) | `01-secret.yaml`–`05-door.yaml` | Opaque, stringData/data, base64, secretKeyRef, secretRef | 441 |
| [012](/root/workspace/DevTools/05_kubernetes/02_Session2_Networking_Config_Storage/012-why-data-disappears/README.md) | `02-db-emptydir.yaml`, `manifests/01-secret.yaml`–`05-door.yaml` | volumes/volumeMounts, emptyDir lifecycle, mountPath, PGDATA | 434 |
| [013](/root/workspace/DevTools/05_kubernetes/02_Session2_Networking_Config_Storage/013-persistent-storage-with-pvc/README.md) | `01-pvc.yaml`–`06-door.yaml` | accessModes RWO/ROX/RWX, storage request, storageClassName, claimName | 437 |
| [014](/root/workspace/DevTools/05_kubernetes/02_Session2_Networking_Config_Storage/014-running-is-not-ready/README.md) | `01-api-with-probes.yaml`, `02-api-bad-readiness.yaml`, `manifests/01-pvc.yaml`–`06-door.yaml` | readiness/liveness/startup, httpGet/exec, timing ทั้ง 5 ค่า, ผลเมื่อ fail | 444 |

โครงคู่มือ 300 บรรทัด:

1. โครง object 5 บรรทัดและชี้ไปฉบับเต็มครั้งที่ 1
2. Service — `#service`
3. ConfigMap — `#configmap`
4. Secret — `#secret`
5. Volume/PVC — `#volume-pvc`
6. Probes — `#probes`
7. ตารางสรุป field ทั้งหมดและ “จำภาพเดียวให้ได้”

ผลตรวจ:

- `check-readme.py`: exit `0`, `0 FAIL` — มี WARN เรื่องเกินเป้าหมาย 400 บรรทัด แต่ทุกไฟล์ไม่เกินข้อกำหนด 450 บรรทัด
- `check-yaml-teaching.py`: exit `0`, `YAML-TEACHING FAILS = 0`
- Exact-path check: ครบ 37/37 manifest
- Kubernetes v1.36.4 server dry-run: manifest ปกติผ่าน 36/36; `03-nodeport-bad.yaml` เป็นไฟล์ผิดโดยตั้งใจ
- ตรวจ default/ความหมายด้วย `kubectl explain` และ object ที่ API server บันทึกจริง

สิ่งที่ไม่แน่ใจ: ไม่มี field ที่ยังค้างตรวจสอบ ทั้งนี้ `nodePort` range และ default `storageClassName` เปลี่ยนตามการตั้งค่า cluster ได้ จึงเขียนกำกับตามบริบทแล้ว ส่วน field ที่ไม่มีตัวอย่างจริง (`configMapKeyRef`, `envFrom.secretRef`, `storageClassName`, `startupProbe`) อธิบายโดยไม่แต่ง YAML เพิ่ม

ยืนยันลบ container แยก `devtools-k8s-yaml-s2` แล้ว และ `docker ps -a --filter name=devtools-k8s-yaml-s2` ไม่พบ container ค้างอยู่ครับ