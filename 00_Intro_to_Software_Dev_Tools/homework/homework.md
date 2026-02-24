# Principles to Software Professionals — Homework

> **Course:** SOFTWARE DEVELOPMENT TOOLS AND ENVIRONMENTS
> **Session:** 1 — Introduction to Software Development Tools & Environments
> **Total:** 100 Points

---

## ข้อ 1: Code Refactoring (30 คะแนน)

**โจทย์:** จงอ่านโค้ด Python ต่อไปนี้ แล้วทำตามที่กำหนด

```python
def proc(l, t, d):
    tot = 0
    for i in l:
        tot = tot + i[0] * i[1]
    if t == 1:
        tot = tot * 1.07
    if tot > 50000:
        tot = tot * 0.9
    if d == 1:
        tot = tot - 500
    return tot
```

**คำถาม:**

1. ระบุปัญหาที่พบในโค้ดนี้อย่างน้อย 4 ข้อ โดยอ้างอิง Clean Code Principles **(12 คะแนน)**
2. ระบุว่าโค้ดนี้ละเมิดหลักการ DRY, KISS, YAGNI หรือ SOLID ข้อใดบ้าง พร้อมอธิบายเหตุผล **(8 คะแนน)**
3. เขียนโค้ดใหม่ (Refactor) ให้เป็น Clean Code โดยแก้ไขทุกปัญหาที่ระบุ **(10 คะแนน)**

---

## ข้อ 2: SOLID Principles วิเคราะห์สถานการณ์ (20 คะแนน)

**โจทย์:** อ่านสถานการณ์ต่อไปนี้ แล้วระบุว่าละเมิดหลักการ SOLID ข้อใด พร้อมอธิบายเหตุผลและเสนอแนวทางแก้ไข **(ข้อละ 4 คะแนน)**

**สถานการณ์ A:**
คลาส `ReportGenerator` มีหน้าที่ดึงข้อมูลจาก Database, คำนวณสถิติ, สร้างกราฟ, และส่งอีเมลรายงาน

**สถานการณ์ B:**
ระบบส่วนลดมีฟังก์ชัน `calculate_discount()` ที่ใช้ if-else 15 ชั้นเพื่อรองรับส่วนลดแต่ละประเภท ทุกครั้งที่เพิ่มส่วนลดใหม่ต้องแก้ฟังก์ชันนี้

**สถานการณ์ C:**
คลาส `Ostrich` สืบทอดมาจากคลาส `Bird` แต่ method `fly()` ของ `Ostrich` ต้อง throw Exception เพราะนกกระจอกเทศบินไม่ได้

**สถานการณ์ D:**
มี interface `SmartDevice` ที่มี method: `call()`, `browse()`, `takePhoto()`, `scanFingerprint()` แต่โทรศัพท์รุ่นเก่าไม่มีกล้องและไม่มีเครื่องสแกนลายนิ้วมือ ก็ต้อง implement ทุก method

**สถานการณ์ E:**
คลาส `NotificationService` เรียกใช้ `GmailAPI` โดยตรงในโค้ด ทำให้เวลาจะเปลี่ยนไปใช้ SendGrid ต้องแก้โค้ดใน `NotificationService` ทั้งหมด

---

## ข้อ 3: SDLC & Roles (20 คะแนน)

**โจทย์:** บริษัท StartupThai กำลังจะพัฒนาแอปพลิเคชัน **"FoodExpress"** ซึ่งเป็นแอปสั่งอาหารออนไลน์

**คำถาม:**

1. จงระบุ Output ที่ควรได้จากแต่ละ Phase ของ SDLC สำหรับโปรเจกต์นี้ (อย่างน้อย Phase ละ 2 Output) **(10 คะแนน)**

| Phase | Output |
|-------|--------|
| 1. Planning | ? |
| 2. Analysis | ? |
| 3. Design | ? |
| 4. Develop & Test | ? |
| 5. Deployment | ? |
| 6. Maintenance | ? |

2. จงจับคู่บทบาท (Role) กับงานที่ต้องรับผิดชอบในโปรเจกต์นี้ โดยอธิบายว่าแต่ละคนทำอะไรเฉพาะเจาะจง **(10 คะแนน)**

| Role | งานที่รับผิดชอบ |
|------|----------------|
| Frontend Developer | ? |
| Backend Developer | ? |
| QA Engineer | ? |
| DevOps Engineer | ? |
| Product Owner | ? |

---

## ข้อ 4: Professional Ethics จำลองสถานการณ์ (15 คะแนน)

**โจทย์:** อ่านสถานการณ์ต่อไปนี้ แล้วตอบคำถาม

> คุณเป็น Backend Developer ในบริษัทแห่งหนึ่ง หัวหน้าสั่งให้คุณเพิ่มโค้ดที่เก็บ **ตำแหน่ง GPS ของผู้ใช้ทุก 5 นาที** โดยไม่แจ้งให้ผู้ใช้ทราบ เพื่อนำไปขายให้บริษัทโฆษณา แอปนี้เป็นแอปจดบันทึก (Note-taking app) ซึ่งไม่จำเป็นต้องใช้ GPS เลย

**คำถาม:**

1. สถานการณ์นี้ขัดกับ ACM/IEEE Code of Ethics ข้อใดบ้าง? อธิบายอย่างน้อย 3 ข้อ **(9 คะแนน)**
2. ในฐานะ Software Professional คุณควรปฏิบัติอย่างไร? เสนอแนวทางดำเนินการเป็นขั้นตอน **(6 คะแนน)**

---

## ข้อ 5: Growth Mindset & T-Shaped Skills (15 คะแนน)

**โจทย์:**

1. จงเปรียบเทียบ **Fixed Mindset** กับ **Growth Mindset** โดยยกตัวอย่างสถานการณ์จริงในการเรียนวิชา Software Development Tools อย่างน้อย 3 สถานการณ์ ว่าคนที่มี Mindset ต่างกันจะมีปฏิกิริยาอย่างไร **(9 คะแนน)**

| สถานการณ์ | Fixed Mindset | Growth Mindset |
|-----------|--------------|----------------|
| 1. ? | ? | ? |
| 2. ? | ? | ? |
| 3. ? | ? | ? |

2. จงออกแบบ **T-Shaped Skills** ของตัวเอง โดย **(6 คะแนน)**:
   - ระบุ Broad Knowledge (แนวนอน) อย่างน้อย 5 ด้านที่ต้องการเรียนรู้
   - ระบุ Deep Expertise (แนวตั้ง) 1 ด้านที่ต้องการเชี่ยวชาญ พร้อมอธิบายเหตุผลและแผนการพัฒนา

```
◄──────────── BROAD KNOWLEDGE ────────────►

┌────┬────┬────┬────┬────┬────┐
│ ?  │ ?  │ ?  │ ?  │ ?  │ ?  │
└────┴────┴────┴────┴────┴────┘
               │
        DEEP EXPERTISE
               │
        ┌──────┴──────┐
        │             │
        │     ?       │
        │             │
        │  เหตุผล:    │
        │  ?          │
        │             │
        │  แผนพัฒนา:  │
        │  ?          │
        │             │
        └─────────────┘
```

---

## สรุปโครงสร้างคะแนน

| ข้อ | หัวข้อ | คะแนน | ระดับ Bloom's Taxonomy |
|-----|--------|-------|----------------------|
| 1 | Code Refactoring (Clean Code, SOLID, DRY/KISS/YAGNI) | 30 | วิเคราะห์ + ประยุกต์ |
| 2 | SOLID Principles วิเคราะห์สถานการณ์ | 20 | วิเคราะห์ |
| 3 | SDLC & Roles | 20 | เข้าใจ + ประยุกต์ |
| 4 | Professional Ethics | 15 | วิเคราะห์ + ประเมินค่า |
| 5 | Growth Mindset & T-Shaped Skills | 15 | สังเคราะห์ + สร้างสรรค์ |
| | **รวม** | **100** | |

---
---

# ANSWER KEY (เฉลย)

> **สำหรับผู้สอนเท่านั้น**

---

## เฉลยข้อ 1: Code Refactoring (30 คะแนน)

### 1) ปัญหาที่พบ (12 คะแนน — ข้อละ 3 คะแนน)

| # | ปัญหา | หลักการที่ละเมิด |
|---|-------|-----------------|
| 1 | ชื่อฟังก์ชัน `proc` และ parameter `l, t, d` ไม่สื่อความหมาย อ่านแล้วไม่รู้ว่าทำอะไร | Meaningful Names |
| 2 | Magic Numbers: `1.07`, `50000`, `0.9`, `500`, `1` ปรากฏลอย ๆ ในโค้ดโดยไม่มีค่าคงที่ | No Magic Numbers |
| 3 | ฟังก์ชันเดียวทำหลายอย่าง (คำนวณยอดรวม, คิดภาษี, คิดส่วนลด, หักคูปอง) | Small Functions / SRP |
| 4 | ไม่มี Error Handling เลย เช่น ถ้า list ว่าง หรือค่าติดลบ | Error Handling |
| 5 | ใช้ `i[0]`, `i[1]` ทำให้ไม่รู้ว่าค่าแต่ละตัวคืออะไร (price? quantity?) | Meaningful Names |

### 2) หลักการที่ละเมิด (8 คะแนน — ข้อละ 4 คะแนน)

- **SRP (Single Responsibility Principle):** ฟังก์ชันเดียวรับผิดชอบทั้งคำนวณยอดรวม, คิดภาษี, คิดส่วนลด, หักคูปอง — ควรแยกเป็นฟังก์ชันย่อยแต่ละหน้าที่
- **KISS (Keep It Simple, Stupid):** แม้โค้ดสั้น แต่อ่านไม่รู้เรื่องเพราะตั้งชื่อไม่ดีและใช้ Magic Numbers ทำให้ซับซ้อนโดยไม่จำเป็น

### 3) โค้ดที่ Refactor แล้ว (10 คะแนน)

```python
TAX_RATE = 0.07
BULK_DISCOUNT_THRESHOLD = 50000
BULK_DISCOUNT_RATE = 0.9
COUPON_DISCOUNT_AMOUNT = 500
INCLUDE_TAX = 1
HAS_COUPON = 1


def calculate_order_total(items, tax_option, coupon_option):
    subtotal = calculate_subtotal(items)
    subtotal = apply_tax(subtotal, tax_option)
    subtotal = apply_bulk_discount(subtotal)
    subtotal = apply_coupon(subtotal, coupon_option)
    return subtotal


def calculate_subtotal(items):
    return sum(item["price"] * item["quantity"] for item in items)


def apply_tax(amount, tax_option):
    if tax_option == INCLUDE_TAX:
        return amount * (1 + TAX_RATE)
    return amount


def apply_bulk_discount(amount):
    if amount > BULK_DISCOUNT_THRESHOLD:
        return amount * BULK_DISCOUNT_RATE
    return amount


def apply_coupon(amount, coupon_option):
    if coupon_option == HAS_COUPON:
        return amount - COUPON_DISCOUNT_AMOUNT
    return amount
```

**เกณฑ์การให้คะแนน:**
- ตั้งชื่อฟังก์ชันและตัวแปรสื่อความหมาย (3 คะแนน)
- แทน Magic Numbers ด้วยค่าคงที่ (3 คะแนน)
- แยกฟังก์ชันตามหน้าที่ (SRP) (3 คะแนน)
- โค้ดทำงานได้ถูกต้อง (1 คะแนน)

---

## เฉลยข้อ 2: SOLID Principles (20 คะแนน)

| สถานการณ์ | หลักการที่ละเมิด | เหตุผล | แนวทางแก้ไข |
|-----------|-----------------|--------|------------|
| **A** | **S — Single Responsibility** | คลาสเดียวรับผิดชอบ 4 หน้าที่ (ดึงข้อมูล, คำนวณ, สร้างกราฟ, ส่งอีเมล) ถ้าต้องเปลี่ยนวิธีสร้างกราฟ ก็ต้องแก้คลาสนี้ด้วย | แยกเป็น `DataRepository`, `StatisticsCalculator`, `ChartGenerator`, `EmailService` |
| **B** | **O — Open/Closed** | ทุกครั้งที่เพิ่มส่วนลดใหม่ ต้องแก้โค้ดเดิม (ไม่ "ปิด" สำหรับการแก้ไข) ทำให้โค้ดเดิมอาจพังได้ | ใช้ Strategy Pattern สร้าง interface `DiscountStrategy` แล้วให้แต่ละประเภทส่วนลด implement เอง เพิ่มส่วนลดใหม่แค่สร้าง class ใหม่ |
| **C** | **L — Liskov Substitution** | `Ostrich` ไม่สามารถแทนที่ `Bird` ได้อย่างสมบูรณ์ เพราะ `fly()` จะ throw error ที่ไหนใช้ `Bird` ได้ ก็ควรใช้ `Ostrich` แทนได้ แต่กลับพัง | แยก interface เป็น `FlyableBird` และ `NonFlyableBird` ให้ `Ostrich` ไม่ต้อง implement `fly()` ที่ไม่สมเหตุสมผล |
| **D** | **I — Interface Segregation** | บังคับให้โทรศัพท์รุ่นเก่า implement method ที่ไม่ได้ใช้ (`takePhoto`, `scanFingerprint`) ทำให้เกิด method ว่าง ๆ ที่ไม่มีประโยชน์ | แยกเป็น interface ย่อย เช่น `Callable`, `Browsable`, `CameraDevice`, `BiometricDevice` ให้แต่ละรุ่น implement เฉพาะที่ใช้ |
| **E** | **D — Dependency Inversion** | Module ระดับสูง (`NotificationService`) พึ่งพา Module ระดับต่ำ (`GmailAPI`) โดยตรง เปลี่ยน provider ไม่ได้ง่าย ๆ | สร้าง interface `EmailProvider` ให้ `GmailAPI` และ `SendGrid` implement แล้วให้ `NotificationService` พึ่งพา interface แทน (เปรียบเหมือนเสียบปลั๊ก) |

**เกณฑ์การให้คะแนน (ข้อละ 4 คะแนน):**
- ระบุหลักการที่ละเมิดถูกต้อง (1 คะแนน)
- อธิบายเหตุผลชัดเจน (1.5 คะแนน)
- เสนอแนวทางแก้ไขที่สมเหตุสมผล (1.5 คะแนน)

---

## เฉลยข้อ 3: SDLC & Roles (20 คะแนน)

### 1) Output แต่ละ Phase (10 คะแนน)

| Phase | Output สำหรับ FoodExpress |
|-------|--------------------------|
| **1. Planning** | - Project Plan กำหนด Timeline 6 เดือน |
| | - Feasibility Study วิเคราะห์ตลาดแอปสั่งอาหาร |
| | - Resource Plan (ต้องใช้ Dev กี่คน, งบเท่าไหร่) |
| **2. Analysis** | - User Stories เช่น "ในฐานะลูกค้า ฉันต้องการค้นหาร้านอาหารใกล้ฉัน" |
| | - Use Case Diagram แสดงการทำงานระหว่างลูกค้า, ร้านอาหาร, คนส่ง |
| | - SRS Document ระบุ Requirement ทั้งหมด |
| **3. Design** | - System Architecture (Microservices: Order Service, Payment Service, Delivery Service) |
| | - Database Schema (ตาราง users, restaurants, orders, menu_items) |
| | - Wireframes/Mockups หน้าจอสั่งอาหาร |
| **4. Develop & Test** | - Source Code (Frontend + Backend + Mobile App) |
| | - Unit Test สำหรับระบบคำนวณราคาและส่วนลด |
| | - Integration Test ทดสอบการเชื่อมต่อระบบจ่ายเงิน |
| **5. Deployment** | - แอปพร้อมใช้งานบน App Store / Play Store |
| | - Release Notes รุ่น v1.0 |
| | - Deployment Documentation |
| **6. Maintenance** | - Bug Fix Patches |
| | - Performance Tuning (เช่น ลดเวลาโหลดหน้าค้นหาร้านอาหาร) |
| | - Feature Updates (เพิ่มระบบรีวิว, โปรโมชัน) |

**เกณฑ์การให้คะแนน:** Phase ละ ~1.7 คะแนน (ระบุ Output ได้ครบถ้วนและเกี่ยวข้องกับโปรเจกต์)

### 2) บทบาทและงานเฉพาะ (10 คะแนน)

| Role | งานเฉพาะเจาะจงในโปรเจกต์ FoodExpress |
|------|--------------------------------------|
| **Frontend Developer** | พัฒนาหน้า UI สำหรับค้นหาร้านอาหาร, หน้าเมนู, หน้าตะกร้าสินค้า, หน้าติดตามการส่ง โดยใช้ React/Vue ทำให้ Responsive ทั้ง Mobile และ Desktop |
| **Backend Developer** | พัฒนา API สำหรับ CRUD ร้านอาหาร, ระบบสั่งอาหาร, ระบบจ่ายเงิน (เชื่อมต่อ Payment Gateway), ระบบจับคู่คนส่งอาหาร, จัดการ Database |
| **QA Engineer** | เขียน Test Case ทดสอบ flow การสั่งอาหารตั้งแต่เลือกร้าน → สั่ง → จ่ายเงิน → ส่ง, ทำ Load Testing ว่าระบบรับ 10,000 คนพร้อมกันได้หรือไม่ |
| **DevOps Engineer** | ตั้งค่า CI/CD Pipeline ด้วย GitHub Actions, Deploy แอปบน AWS/GCP ด้วย Docker + Kubernetes, ตั้ง Monitoring ด้วย Prometheus + Grafana |
| **Product Owner** | กำหนด Priority ว่าฟีเจอร์ไหนทำก่อน (เช่น สั่งอาหารก่อน → ระบบรีวิวทีหลัง), เขียน User Stories, ตัดสินใจเรื่อง Business Requirements |

**เกณฑ์การให้คะแนน:** Role ละ 2 คะแนน (อธิบายงานเฉพาะเจาะจงสำหรับโปรเจกต์ FoodExpress ไม่ใช่ตอบแบบกว้าง ๆ)

---

## เฉลยข้อ 4: Professional Ethics (15 คะแนน)

### 1) ACM/IEEE Code of Ethics ที่ละเมิด (9 คะแนน — ข้อละ 3 คะแนน)

| ข้อ | หลักการ | เหตุผลที่ละเมิด |
|-----|---------|----------------|
| **1. PUBLIC** | ทำหน้าที่เพื่อประโยชน์สาธารณะ | การเก็บ GPS โดยไม่แจ้งผู้ใช้เป็นอันตรายต่อความเป็นส่วนตัว (Privacy) ของสาธารณชน ผู้ใช้ไม่ได้ยินยอม (No Consent) |
| **3. PRODUCT** | รับประกันคุณภาพของงาน | การฝัง Feature ซ่อนที่ผู้ใช้ไม่รู้ ไม่ใช่ซอฟต์แวร์ที่มีคุณภาพ เป็นการหลอกลวงผู้ใช้ |
| **4. JUDGMENT** | รักษาความซื่อสัตย์ในการตัดสินใจ | ถ้ารับทำตามคำสั่งโดยรู้ว่าผิดจริยธรรม แสดงว่าไม่ได้ใช้วิจารณญาณที่เป็นอิสระ |
| **6. PROFESSION** | ส่งเสริมความซื่อสัตย์ในวิชาชีพ | การทำเช่นนี้ทำลายความเชื่อมั่นที่สาธารณชนมีต่อวิชาชีพ Software Engineer โดยรวม |

(นักศึกษาตอบถูก 3 ข้อจาก 4 ข้อข้างต้นก็ได้คะแนนเต็ม)

### 2) แนวทางดำเนินการ (6 คะแนน — ขั้นตอนละ 1.5 คะแนน อย่างน้อย 4 ขั้นตอน)

1. **ปฏิเสธอย่างสุภาพ** — แจ้งหัวหน้าว่าคำสั่งนี้ขัดต่อจริยธรรมวิชาชีพและอาจผิดกฎหมาย PDPA/GDPR
2. **อธิบายความเสี่ยง** — ชี้ให้เห็นว่าหากถูกจับได้ บริษัทอาจถูกฟ้องร้อง สูญเสียความเชื่อมั่นจากผู้ใช้ และเสียชื่อเสียง
3. **เสนอทางเลือก** — เสนอว่าหากต้องการข้อมูล Location จริง ๆ ให้เพิ่มฟีเจอร์ที่สมเหตุสมผล (เช่น แท็กตำแหน่งที่บันทึก Note) พร้อม **ขอ Consent จากผู้ใช้อย่างชัดเจน**
4. **บันทึกเป็นลายลักษณ์อักษร** — ส่งอีเมลแจ้งข้อกังวลเพื่อเป็นหลักฐาน
5. **Escalate** — หากหัวหน้ายังคงยืนยัน ให้รายงานต่อผู้บริหารระดับสูงขึ้น หรือฝ่ายกฎหมายของบริษัท
6. **พิจารณาลาออก** — หากบริษัทยังคงยืนกรานให้ทำ ในฐานะ Software Professional ควรพิจารณาไม่ร่วมงานกับองค์กรที่ละเมิดจริยธรรม

---

## เฉลยข้อ 5: Growth Mindset & T-Shaped Skills (15 คะแนน)

### 1) เปรียบเทียบ Fixed Mindset vs Growth Mindset (9 คะแนน — สถานการณ์ละ 3 คะแนน)

| สถานการณ์ | Fixed Mindset | Growth Mindset |
|-----------|--------------|----------------|
| **ใช้ Git ครั้งแรกแล้ว merge conflict** | "Git มันยากเกินไป ฉันไม่เหมาะกับงานนี้" → เลิกพยายาม กลับไปใช้ copy โฟลเดอร์แทน | "ดีเลย ได้เรียนรู้วิธีแก้ conflict ตอนนี้เลย ครั้งหน้าจะเก่งขึ้น" → ไปศึกษาเพิ่มเติมจาก git-scm.com |
| **เขียน Docker ไม่ผ่าน build error 10 ครั้ง** | "ฉันไม่มีพรสวรรค์เรื่อง DevOps คนอื่นทำได้แต่ฉันทำไม่ได้" → ไม่กล้าลอง Kubernetes ต่อ | "ทุกครั้งที่ error ฉันเข้าใจ Docker มากขึ้น ฉันจดบันทึก error แต่ละตัวไว้เป็นความรู้" → ทำ cheat sheet ของตัวเอง |
| **Code Review ได้คอมเมนต์แก้เยอะมาก** | "เพื่อนจับผิดฉัน ฉันอายมาก ครั้งหน้าไม่อยากส่ง Review แล้ว" → หลีกเลี่ยง Code Review | "Feedback ช่วยให้โค้ดฉันดีขึ้น ฉันจะนำไปปรับปรุง" → นำ comment ไปศึกษาหลัก Clean Code เพิ่ม |

**เกณฑ์การให้คะแนน:** สถานการณ์ต้องเกี่ยวข้องกับวิชาเรียน (1 คะแนน), อธิบาย Fixed Mindset สมจริง (1 คะแนน), อธิบาย Growth Mindset พร้อม action ที่จะทำ (1 คะแนน)

### 2) T-Shaped Skills (6 คะแนน)

**ตัวอย่างคำตอบ:**

```
◄──────────── BROAD KNOWLEDGE ────────────►

┌────┬────┬────┬────┬────┬────┐
│ FE │ DB │ Git│Docker│K8s│ QA │
└────┴────┴────┴────┴────┴────┘
               │
        DEEP EXPERTISE
               │
        ┌──────┴──────┐
        │  Backend    │
        │  (Python)   │
        │             │
        │  Flask/     │
        │  FastAPI    │
        │  REST API   │
        │  Database   │
        │  Design     │
        └─────────────┘
```

- **Broad Knowledge:** Frontend (HTML/CSS/JS), Database (SQL/NoSQL), Git/GitHub, Docker, Kubernetes, QA/Testing
- **Deep Expertise:** Backend Development ด้วย Python
  - **เหตุผล:** Python เป็นภาษาที่ใช้ได้หลากหลาย ทั้ง Web, Data, AI และมี community ใหญ่
  - **แผนพัฒนา:** ปี 1 เรียน Python + Flask → ปี 2 เรียน FastAPI + Database Design → ปี 3 เรียน System Design + Microservices

**เกณฑ์การให้คะแนน:**
- ระบุ Broad Knowledge ครบ 5 ด้านขึ้นไป (2 คะแนน)
- ระบุ Deep Expertise 1 ด้านอย่างชัดเจน (1 คะแนน)
- อธิบายเหตุผลที่เลือกสมเหตุสมผล (1.5 คะแนน)
- มีแผนพัฒนาเป็นขั้นตอน (1.5 คะแนน)

---

<div align="center">

**Session 1 | SOFTWARE DEVELOPMENT TOOLS AND ENVIRONMENTS**

</div>
