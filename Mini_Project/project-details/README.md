# Mini Project: PetTech × DevTools

พัฒนาระบบที่แก้ปัญหาเกี่ยวกับสัตว์เลี้ยง และสาธิตกระบวนการพัฒนาตั้งแต่จัดการ Source Code, Build, Test, Deploy จนถึงตรวจสอบการทำงานของระบบด้วยเครื่องมือที่เรียนในรายวิชา

[← README หลักและกำหนดการ](../readme.md)

## เป้าหมาย

ผลงานต้องตอบได้ 3 เรื่อง:

1. ปัญหาคืออะไร เกิดกับใคร และมีหลักฐานใดสนับสนุน
2. ระบบแก้ปัญหาอย่างไร และมี Demo ที่ใช้งานได้
3. ทีมใช้ DevTools ทำให้การพัฒนาและ Deploy ทำซ้ำได้อย่างไร

หัวข้ออาจเป็นระบบดูแลสุขภาพสัตว์เลี้ยง การนัดหมาย การติดตามสัตว์สูญหาย การหาบ้านหรือพี่เลี้ยง หรือแนวคิดอื่นภายใต้ธีม PetTech

## ข้อกำหนดทางเทคนิค

### ส่วนที่ทุกกลุ่มต้องมี

#### 1. Git และ GitHub

- สมาชิกพัฒนางานผ่าน Branch และรวมงานด้วย Merge หรือ Pull Request
- มี Commit history ที่แสดงการมีส่วนร่วมของสมาชิก
- ใช้ `.gitignore` และห้ามเก็บ Password, Token หรือ Secret ใน Repository

#### 2. Docker และ Docker Compose

- Service ที่ทีมพัฒนามี `Dockerfile`
- ใช้ `compose.yaml` สำหรับรันระบบทั้งหมด
- กำหนด Network, Port, Environment Variable และ Volume เท่าที่ระบบจำเป็นต้องใช้
- ผู้ตรวจสามารถเริ่มระบบตามคำสั่งใน README ได้

#### 3. Jenkins CI/CD

- เก็บ `Jenkinsfile` ไว้ใน Repository
- Pipeline อย่างน้อยต้องทำ `Checkout → Test → Build Image → Push Image → Deploy → Verify`
- แสดงผล Pipeline ที่สำเร็จ และอธิบายการ Trigger จาก GitHub ด้วย SCM หรือ Webhook

### ส่วนประยุกต์: เลือกอย่างน้อย 2 หัวข้อ

เลือกเฉพาะเครื่องมือที่เหมาะกับปัญหาและสถาปัตยกรรมของระบบ พร้อมสาธิตผลการทำงานจริง

| หัวข้อ | สิ่งที่ต้องแสดง |
|---|---|
| **Traefik** | Reverse Proxy, Routing, Load Balancing หรือ Middleware |
| **RabbitMQ หรือ Kafka** | Queue/Event flow, Producer–Consumer และเหตุผลที่ระบบต้องใช้ Broker |
| **Prometheus และ Grafana** | Metrics ของระบบและ Dashboard; เพิ่ม Alertmanager หากมีเงื่อนไขแจ้งเตือน |
| **Kubernetes** | Manifest แบบ YAML และการ Deploy อย่างน้อยด้วย Pod และ Service |

> ไม่จำเป็นต้องใส่ทุกเครื่องมือ หากเครื่องมือนั้นไม่ช่วยแก้ Requirement ของระบบ

## หลักฐานที่ต้องมีใน Repository

```text
project/
├── README.md              # ปัญหา วิธีรัน และวิธีทดสอบ
├── compose.yaml
├── Jenkinsfile
├── src/                   # Source code ของระบบ
├── tests/                 # Automated tests
├── docs/
│   ├── architecture.*     # System architecture
│   └── pipeline.*         # CI/CD flow
└── k8s/ หรือ monitoring/  # ตามหัวข้อประยุกต์ที่เลือก
```

ชื่อโฟลเดอร์ปรับได้ตามเทคโนโลยี แต่ต้องหาไฟล์สำคัญได้ง่าย และ README ของทีมต้องระบุ:

- Problem, Target User และขอบเขตของระบบ
- Architecture และหน้าที่ของแต่ละ Service
- เครื่องมือที่เลือกใช้และเหตุผล
- ขั้นตอนรัน ทดสอบ และหยุดระบบ
- URL, Port และบัญชีทดสอบที่จำเป็น
- ข้อจำกัดหรือส่วนที่ยังไม่สมบูรณ์

## โครงสร้างการนำเสนอ 10 นาที

| เวลาโดยประมาณ | เนื้อหา |
|---:|---|
| 2 นาที | Problem, Target User และหลักฐานของปัญหา |
| 3 นาที | Solution และ Demo เส้นทางหลักของผู้ใช้ |
| 2 นาที | System Architecture, Docker Compose และเครื่องมือประยุกต์ |
| 2 นาที | Git workflow และ Jenkins Pipeline |
| 1 นาที | ผลการทดสอบ Metrics หรือข้อจำกัดของระบบ |

เวลาถาม–ตอบและลำดับการนำเสนอให้ยึดตาม [README หลัก](../readme.md#-กำหนดการนำเสนอผลงาน)

## สิ่งที่ใช้พิจารณาผลงาน

- ระบบทำงานได้จริงและแก้ Problem ที่กำหนด
- ใช้ Git, Docker และ Jenkins ได้ถูกต้อง
- เลือกเครื่องมือประยุกต์สอดคล้องกับ Requirement
- Build, Test และ Deploy ซ้ำได้จากเอกสารหรือ Pipeline
- สมาชิกอธิบาย Architecture, Workflow และส่วนที่ตนรับผิดชอบได้

## Checklist ก่อนส่งและนำเสนอ

- [ ] Demo เส้นทางหลักทำงานได้
- [ ] สมาชิกมีหลักฐานการทำงานใน Git history
- [ ] `docker compose up` เริ่มระบบได้ตาม README
- [ ] Automated tests ผ่าน
- [ ] Jenkins Pipeline ผ่านครบทุก Stage
- [ ] หัวข้อประยุกต์อย่างน้อย 2 หัวข้อมีหลักฐานและสาธิตได้
- [ ] ไม่มี Secret หรือข้อมูลส่วนบุคคลใน Repository และ Docker Image
- [ ] มี Architecture Diagram และ Pipeline Diagram
- [ ] เตรียมวิดีโอหรือภาพสำรองกรณีระบบภายนอกใช้งานไม่ได้
- [ ] ส่ง Slide, Source Code, Report และวิดีโอตามรายการใน [README หลัก](../readme.md#-รายการสิ่งที่ต้องส่งก่อนวันนำเสนอ)
