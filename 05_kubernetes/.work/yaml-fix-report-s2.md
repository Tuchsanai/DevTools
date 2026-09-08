แก้ครบทุก FAIL/WARN และ NIT ที่ไม่เสี่ยงจาก reviewer แล้ว โดยไม่สร้างไฟล์รายงานเพิ่ม

| ไฟล์ | รายการที่แก้ (บรรทัด) | ยังไม่แก้และเหตุผล |
|---|---|---|
| [YAML_Guide.md](/root/workspace/DevTools/05_kubernetes/02_Session2_Networking_Config_Storage/YAML_Guide.md:4) | เปลี่ยนชื่อหัวข้อสรุป; เพิ่มทบทวน Deployment/Ingress (11–48); เติม comment ไทยและโครง parent ที่ถูกต้อง; แก้ EndpointSlice/error (49–97), Secret errors (139–181), PVC required fields/Event (182–241), probe status/แล็บแรก (242–298) | ไม่มี |
| [LAB 008 README](/root/workspace/DevTools/05_kubernetes/02_Session2_Networking_Config_Storage/008-why-we-need-service/README.md:98) | เพิ่มลิงก์ Deployment/Ingress; แยก `"fetch failed"` จาก timeout ของ Pod IP เก่า (98–126) | ไม่มี reviewer item ค้าง |
| [LAB 009 README](/root/workspace/DevTools/05_kubernetes/02_Session2_Networking_Config_Storage/009-service-types-and-access/README.md:108) | เพิ่มลิงก์ทบทวน Deployment (108–109) | ไม่มี reviewer item ค้าง |
| [LAB 010 README](/root/workspace/DevTools/05_kubernetes/02_Session2_Networking_Config_Storage/010-configmap-separate-config/README.md:98) | เพิ่มลิงก์ Deployment/Ingress (98–100) | ไม่มี reviewer item ค้าง |
| [LAB 011 README](/root/workspace/DevTools/05_kubernetes/02_Session2_Networking_Config_Storage/011-secret-and-why-not-configmap/README.md:101) | เพิ่มลิงก์ Deployment/Ingress; เปลี่ยนเป็น “rollout restart Deployment ที่อ้าง Secret” (101–133) | ไม่มี reviewer item ค้าง |
| [LAB 012 README](/root/workspace/DevTools/05_kubernetes/02_Session2_Networking_Config_Storage/012-why-data-disappears/README.md:89) | แก้โครง `containers/env/volumeMounts/volumes`; อธิบาย PGDATA และจังหวะ 503 ให้ตรง runlog (89–119) | ไม่มี reviewer item ค้าง |
| [LAB 013 README](/root/workspace/DevTools/05_kubernetes/02_Session2_Networking_Config_Storage/013-persistent-storage-with-pvc/README.md:101) | ระบุ `Recreate`, `readinessProbe.exec` และลิงก์ Deployment/Probes (101–135) | ไม่มี reviewer item ค้าง |
| [LAB 014 README](/root/workspace/DevTools/05_kubernetes/02_Session2_Networking_Config_Storage/014-running-is-not-ready/README.md:100) | อธิบาย `rollingUpdate: null`; แก้สถานะเป็น `READY 0/1`, Ready=False แต่ STATUS=Running (100–134) | ไม่มี reviewer item ค้าง |

หัวข้อทบทวนที่เพิ่ม:

- `#deployment` — 18 บรรทัด จาก `008/.../02-api.yaml`
- `#ingress` — 20 บรรทัด จาก `008/.../01-web.yaml`

ผลตรวจ:

- `check-yaml-teaching.py`: **0 FAIL** — คู่มือ 298 บรรทัด, 12 YAML blocks, manifest ครบและ anchor ถูกทั้งหมด
- `check-readme.py`: **0 FAIL** — มี WARN เฉพาะเป้าหมายแนะนำ 200–400 บรรทัด แต่ README ทั้งหมดอยู่ที่ 423–446 บรรทัด จึงผ่านข้อกำหนดจริง ≤450 โดยไม่ตัดขั้นตอนหรือ Expected output
- ยืนยัน schema/error กับ Kubernetes v1.36.4 แล้ว รวม PVC required fields และ Secret base64
- ใช้เฉพาะ `devtools-k8s-verify` ที่มีอยู่; container ยัง healthy และไม่ได้สร้างหรือลบ container ใด ๆ