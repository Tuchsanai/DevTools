แก้ README ครบตามขอบเขตแล้ว: LAB 001–007 พร้อม README ระดับชุดและครั้งที่ 1 โดยไม่แตะแล็บ 008–021

| LAB | จุดแก้หลัก | วิธี | ยังไม่แก้ |
|---|---|---|---|
| 001 | รอ Docker daemon, อธิบาย image รอบแรก, ผล `kind load`, รอ node `NotReady`, หลักฐาน metrics-server แบบมีเงื่อนไข ([README](/root/workspace/DevTools/05_kubernetes/01_Session1_Kubernetes_Basics/001-kubernetes-introduction/README.md:53)) | ก + ค (ตัดส่วน k9s ที่ไม่มี runlog) | ไม่มี |
| 002 | ใช้ node/image จริง, namespace ผ่าน JSONPath และ ingress log เต็ม ([README](/root/workspace/DevTools/05_kubernetes/01_Session1_Kubernetes_Basics/002-kubectl-and-namespace/README.md:287)) | ก | ไม่มี |
| 003 | แสดง sidecar YAML จริง, รอ ImagePullBackOff, Events จริง และวิธีเปิด terminal ที่สอง ([README](/root/workspace/DevTools/05_kubernetes/01_Session1_Kubernetes_Basics/003-pod-the-smallest-unit/README.md:190)) | ก | ไม่มี |
| 004 | เติม dry-run YAML, terminal ที่สอง, Warning จริง, `printenv` และเปลี่ยนผลแต่งเป็น `get pod` จริง ([README](/root/workspace/DevTools/05_kubernetes/01_Session1_Kubernetes_Basics/004-declarative-yaml/README.md:207)) | ก | ไม่มี |
| 005 | แสดง manifest/selector จริง, FailedScheduling เต็ม และ ingress recovery log จริง ([README](/root/workspace/DevTools/05_kubernetes/01_Session1_Kubernetes_Basics/005-labels-the-glue/README.md:164)) | ก + ค (ตัดคำสั่ง log ที่ไม่เคยรัน) | ไม่มี |
| 006 | แก้ Ingress เป็นพอร์ต 80, เพิ่ม wait, ผล self-healing/scale/mixed-version จริงครบ และระบุภาพจากคนละรอบ ([README](/root/workspace/DevTools/05_kubernetes/01_Session1_Kubernetes_Basics/006-desired-state-and-self-healing/README.md:135)) | ก | ไม่มี |
| 007 | แสดง Deployment YAML จริงพร้อมอธิบาย probe, เพิ่ม rollout wait/watch, Warning, RS v3 และ describe error จริง ([README](/root/workspace/DevTools/05_kubernetes/01_Session1_Kubernetes_Basics/007-deployment-manages-change/README.md:85)) | ก + ค (ตัด history/events/pgrep ที่ไม่มีหลักฐานรัน) | ไม่มี |

ปรับนโยบายพอร์ตใน [README ระดับชุด](/root/workspace/DevTools/05_kubernetes/README.md:70) และ [README ครั้งที่ 1](/root/workspace/DevTools/05_kubernetes/01_Session1_Kubernetes_Basics/README.md:67) แล้ว

ผลตรวจสุดท้าย:

- Linter: ผ่านครบ 7 LAB, exit code `0`, `0 FAIL`, `0 WARN`
- ความยาว: 385–400 บรรทัดต่อแล็บ
- `curl ... localhost:8080` ใน README ของ LAB 001–021 และ README ระดับชุด/ครั้งที่ 1: `0`
- ปัญหาระยะห่างก่อน Expected output/หัวข้อ/รูป: `0`
- คำภายในและคำสั่ง `| jq` ที่ไม่ compact: `0`
- Footer ทุกแล็บใช้ปี 2026
- ใช้ผลจาก runlog และวิธี ก/ค จึงไม่ต้องรัน container ใหม่ ตามแนวทาง `devtools-lab`
- สั่ง cleanup ชื่อ `devtools-k8s-fix2-s1` และตรวจแล้วไม่เหลือ container (`0` รายการ); ไม่แตะ `devtools-k8s` ของผู้ใช้