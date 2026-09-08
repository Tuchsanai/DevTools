แก้ README LAB 008–014 รอบ 2 ครบแล้ว โดยไม่แตะ manifest หรือรูปภาพ

| แล็บ | รายการที่แก้ (อ้างอิงจุดตรวจ) | วิธี | ยังไม่แก้และเหตุผล |
|---|---|---|---|
| [008](/root/workspace/DevTools/05_kubernetes/02_Session2_Networking_Config_Storage/008-why-we-need-service/README.md:52) | แก้ port 80, เพิ่ม Ingress wait, ผล Connection refused, loop จริง 10 รอบ, Warning/NXDOMAIN/traceback, selector wait และ JSON ที่มี `error` ตาม review L133–330 | ก/ค | ไม่มี |
| [009](/root/workspace/DevTools/05_kubernetes/02_Session2_Networking_Config_Storage/009-service-types-and-access/README.md:141) | เพิ่ม node placement, ผล NodePort จริงทุก node, วิธีเปิด terminal ที่สอง, timeout 6 ครั้ง, `/ready` 503 และเลิก hard-code Node IP ตาม L139–311 | ก/ข/ค | ไม่มี |
| [010](/root/workspace/DevTools/05_kubernetes/02_Session2_Networking_Config_Storage/010-configmap-separate-config/README.md:55) | เติมขั้นเตรียมเครื่อง, เปลี่ยน Ingress เป็น port 80, เพิ่ม rollout/Ingress wait, `configured` และผล rollout จริงตาม L53–347 | ก | ไม่มี |
| [011](/root/workspace/DevTools/05_kubernetes/02_Session2_Networking_Config_Storage/011-secret-and-why-not-configmap/README.md:198) | จำกัด DB env ให้ตรงผล, แสดง Connection refused/503, ใช้ log filter ที่ตรง runlog, JSON คง `error` และเพิ่ม waits ตาม L52–358 | ก | ไม่มี |
| [012](/root/workspace/DevTools/05_kubernetes/02_Session2_Networking_Config_Storage/012-why-data-disappears/README.md:157) | เพิ่มผล Pod หลัง wait, retry initdb/psql, แสดง `PGDATA`, ผล delete และ `(1 row)` จริง พร้อมตัดขั้น EndpointSlice ที่หลุดจากการพัฒนาตาม L52–319 | ก/ค | ไม่มี |
| [013](/root/workspace/DevTools/05_kubernetes/02_Session2_Networking_Config_Storage/013-persistent-storage-with-pvc/README.md:102) | เพิ่ม YAML PVC และ storage จากไฟล์จริงพร้อมอธิบาย field, ตาราง Compose/PVC, finalizer/Used By และแก้ขั้นลบ/สร้าง PVC ตาม L17–301 | ก/ค | ไม่มี |
| [014](/root/workspace/DevTools/05_kubernetes/02_Session2_Networking_Config_Storage/014-running-is-not-ready/README.md:96) | เพิ่ม YAML probes, ผล `/health`/`/ready` จริงจากรอบเดียวกัน, `sleep 15`, API ready wait, `sleep 35`, `logs --previous`, Warning 503/404 ตาม L109–320 | ก/ข | ไม่มี |

ปรับนโยบาย port ของ [README ครั้งที่ 2](/root/workspace/DevTools/05_kubernetes/02_Session2_Networking_Config_Storage/README.md:69) แล้วด้วย ผลรันใหม่ถูกต่อท้าย [runlog LAB 009](/root/workspace/DevTools/05_kubernetes/.work/runlogs/lab009.txt:226) และ [runlog LAB 014](/root/workspace/DevTools/05_kubernetes/.work/runlogs/lab014.txt:816)

ผลตรวจสุดท้าย:

- Linter: 7/7 แล็บผ่าน, 0 FAIL
- ความยาว: `400, 400, 387, 400, 399, 394, 399` บรรทัด
- ไม่พบ `curl ... localhost:8080` ใน README ของทั้ง 21 แล็บ
- ทุก `✅ **Expected output**`, หัวข้อ และรูปมีบรรทัดว่างนำหน้า
- Footer LAB 008–014 ใช้ปี 2026
- Container `devtools-k8s-fix2-s2` ถูกลบแล้ว และ `docker ps -a` ยืนยันว่าไม่เหลือชื่อดังกล่าว