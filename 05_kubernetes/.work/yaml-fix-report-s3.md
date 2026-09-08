แก้ครบทุก FAIL/WARN และ NIT โดยไม่เปลี่ยนขั้นตอนหรือ Expected output เดิม

| ไฟล์ | รายการที่แก้ (บรรทัดปัจจุบัน) | ยังไม่แก้และเหตุผล |
|---|---|---|
| [YAML_Guide.md](/root/workspace/DevTools/05_kubernetes/03_Session3_Application_Deployment/YAML_Guide.md:52) | Ingress/default/port/error L52–70, ระบุการตัด probe L80–81, แก้ Recreate L179–181, ข้อความ wget L254, เพิ่มทบทวน L259–361 | ไม่มีตาม reviewer |
| [LAB 015 README](/root/workspace/DevTools/05_kubernetes/03_Session3_Application_Deployment/015-assembling-a-real-application/README.md:119) | แก้ลิงก์ ConfigMap/Deployment/Service L119–123 | ไม่มี |
| [LAB 016 README](/root/workspace/DevTools/05_kubernetes/03_Session3_Application_Deployment/016-adding-a-database/README.md:104) | แก้ลิงก์ทบทวน object/probes L104–113 | ไม่มี |
| [LAB 017 README](/root/workspace/DevTools/05_kubernetes/03_Session3_Application_Deployment/017-ingress-the-front-door/README.md:110) | แก้ลิงก์ทบทวน object/probes L110–119 | ไม่มี |
| [LAB 018 README](/root/workspace/DevTools/05_kubernetes/03_Session3_Application_Deployment/018-updating-without-downtime/README.md:99) | แก้ลิงก์ Service/Probes และ object อื่น L99–108 | ไม่มี |
| [LAB 019 README](/root/workspace/DevTools/05_kubernetes/03_Session3_Application_Deployment/019-telling-kubernetes-what-you-need/README.md:109) | แก้ลิงก์ Service L109 และ JSONPath ให้เลือก Pod L139 | ไม่มี |
| [LAB 020 README](/root/workspace/DevTools/05_kubernetes/03_Session3_Application_Deployment/020-reading-the-symptoms/README.md:103) | ไม่ต้องแก้—reviewer ระบุว่าผ่าน | ไม่มี |
| [LAB 021 README](/root/workspace/DevTools/05_kubernetes/03_Session3_Application_Deployment/021-the-big-picture/README.md:112) | แก้ลิงก์ทุก object L112–121 และคำอธิบาย Secret L118 | ไม่มี |

หัวข้อทบทวนที่เพิ่มจาก manifest จริงของ LAB 021:

- Deployment: 20 บรรทัด
- Service: 18 บรรทัด
- ConfigMap: 15 บรรทัด
- Secret: 14 บรรทัด
- PVC: 17 บรรทัด
- Probes: 18 บรรทัด

ตรวจ field/default ผ่าน `kubectl explain` บน server v1.36.4 แล้ว โดยไม่ได้สร้างหรือลบ container

ผล linter:

- `check-yaml-teaching.py`: **0 FAIL**, exit 0
- `check-readme.py`: **0 FAIL**, exit 0
- README ทุกไฟล์ยาว 401–437 บรรทัด จึงไม่เกิน 450
- มี advisory WARN เรื่องเป้าหมายเดิม 400 บรรทัด และ YAML Guide 374 บรรทัดเทียบเป้าหมายเดิม 300; ความยาวเพิ่มจากหัวข้อทบทวนที่บังคับและยังไม่ถือเป็น FAIL