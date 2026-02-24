# 📖 Principles to Software Professionals

> **Course:** SOFTWARE DEVELOPMENT TOOLS AND ENVIRONMENTS  
> **Session:** 1 — Introduction to Software Development Tools & Environments  

---

## 📑 สารบัญ (Table of Contents)

- [1. Software Professional คืออะไร?](#1-software-professional-คืออะไร)
- [2. Core Principles of Software Professionals](#2-core-principles-of-software-professionals)
- [3. Competency Framework](#3-competency-framework)
- [4. Hard Skills vs Soft Skills](#4-hard-skills-vs-soft-skills)
- [5. Software Engineering Roles & Responsibilities](#5-software-engineering-roles--responsibilities)
- [6. Software Development Lifecycle (SDLC)](#6-software-development-lifecycle-sdlc)
- [7. Professional Ethics & Code of Conduct](#7-professional-ethics--code-of-conduct)
- [8. Growth Mindset & Continuous Learning](#8-growth-mindset--continuous-learning)
- [9. Toolchain ของ Software Professional](#9-toolchain-ของ-software-professional)
- [10. สรุป (Summary)](#10-สรุป-summary)

---

## 1. Software Professional คืออะไร?

> 💡 **Software Professional** คือบุคคลที่ทำงานเกี่ยวกับการพัฒนา ออกแบบ ทดสอบ และดูแลรักษาซอฟต์แวร์อย่างมีมาตรฐาน โดยมีความรับผิดชอบต่อผลิตภัณฑ์และผู้ใช้งาน

```
╔══════════════════════════════════════════════════════════════════╗
║                   👨‍💻 SOFTWARE PROFESSIONAL                       ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║    "A person who builds software with skill, responsibility,     ║
║     ethics, and a commitment to continuous improvement."         ║
║                                                                  ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║   🔧 Technical Expert     +     🧠 Problem Solver               ║
║   📋 Planner              +     🤝 Team Collaborator            ║
║   📚 Continuous Learner   +     ⚖️  Ethical Practitioner        ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
```

### 🔍 ความแตกต่างระหว่าง Programmer vs Software Professional

| ลักษณะ | Programmer 👨‍💻 | Software Professional 🏆 |
|--------|:--------------:|:------------------------:|
| **เป้าหมาย** | เขียนโค้ดให้ทำงานได้ | สร้างซอฟต์แวร์ที่มีคุณภาพและยั่งยืน |
| **มุมมอง** | มองแค่ Task ที่ได้รับ | มองภาพรวมทั้ง Product |
| **ทีม** | ทำงานคนเดียวได้ | ทำงานร่วมกับทีมและ Stakeholders |
| **มาตรฐาน** | ขอแค่ทำงานได้ | ยึดถือ Best Practices & Standards |
| **การเรียนรู้** | เรียนเมื่อจำเป็น | เรียนรู้อย่างต่อเนื่อง (Lifelong Learning) |
| **ความรับผิดชอบ** | รับผิดชอบโค้ดตัวเอง | รับผิดชอบต่อ Product & Users |
| **Ethics** | ไม่ได้โฟกัส | ให้ความสำคัญสูงมาก |

---

## 2. Core Principles of Software Professionals

> 💡 **Core Principles** คือหลักการพื้นฐานที่ Software Professional ทุกคนควรยึดถือและปฏิบัติตาม เพื่อให้การพัฒนาซอฟต์แวร์เป็นไปอย่างมีคุณภาพและมีจริยธรรม

```
                    🏆 CORE PRINCIPLES
                          │
          ┌───────────────┼───────────────┐
          │               │               │
    ┌─────▼─────┐   ┌─────▼─────┐   ┌────▼──────┐
    │  QUALITY  │   │COLLABORATION│  │   ETHICS  │
    │    品质    │   │    协作    │   │   道德    │
    └─────┬─────┘   └─────┬─────┘   └────┬──────┘
          │               │               │
          ▼               ▼               ▼
   Clean Code        Teamwork       Responsibility
   Testing           Communication  Transparency
   Refactoring       Respect        Integrity
          │               │               │
          └───────────────┼───────────────┘
                          │
                  ┌───────▼───────┐
                  │  CONTINUOUS   │
                  │  IMPROVEMENT  │
                  │    持续改进    │
                  └───────────────┘
```

### 2.1 หลักการ SOLID Principles

> 💡 **SOLID** คือชุดของหลักการออกแบบซอฟต์แวร์เชิงวัตถุ (Object-Oriented Design) ที่ช่วยให้โค้ดมีความยืดหยุ่น บำรุงรักษาง่าย และขยายได้

```
╔═════════════════════════════════════════════════════════════════════════╗
║                        🔩 SOLID PRINCIPLES                              ║
╠═══╦═════════════════════════════════════════════════════════════════════╣
║   ║                                                                     ║
║ S ║  Single Responsibility Principle (หลักความรับผิดชอบเดียว)          ║
║   ║  ─────────────────────────────────────────────────────────────      ║
║   ║  แต่ละคลาสควรมี "เหตุผลเดียว" ในการเปลี่ยนแปลง                   ║
║   ║  หมายความว่า 1 คลาส = 1 หน้าที่ ไม่ยัดทุกอย่างไว้ที่เดียว        ║
║   ║                                                                     ║
║   ║  ❌ BAD:  class User → สมัคร, ส่งอีเมล, สร้าง PDF, บันทึก Log    ║
║   ║  ✅ GOOD: class User → จัดการข้อมูลผู้ใช้เท่านั้น                  ║
║   ║           class EmailService → ส่งอีเมล                            ║
║   ║           class PDFGenerator → สร้าง PDF                           ║
║   ║                                                                     ║
║   ║  💡 ถ้าอธิบายหน้าที่ของคลาสแล้วต้องใช้คำว่า "และ" แสดงว่า        ║
║   ║     คลาสนั้นทำหลายอย่างเกินไป ควรแยกออก                           ║
║   ║                                                                     ║
╠═══╬═════════════════════════════════════════════════════════════════════╣
║   ║                                                                     ║
║ O ║  Open/Closed Principle (หลักเปิด-ปิด)                              ║
║   ║  ─────────────────────────────────────────────────────────────      ║
║   ║  ซอฟต์แวร์ควร "เปิด" ให้ขยายฟีเจอร์ใหม่ได้                       ║
║   ║  แต่ "ปิด" ไม่ต้องแก้โค้ดเดิมที่ใช้งานอยู่แล้ว                    ║
║   ║                                                                     ║
║   ║  ❌ BAD:  เพิ่มส่วนลดใหม่ → ต้องแก้ if-else ในฟังก์ชันเดิม       ║
║   ║  ✅ GOOD: เพิ่มส่วนลดใหม่ → สร้าง class ใหม่ที่ implement         ║
║   ║           DiscountStrategy โดยไม่แตะโค้ดเดิมเลย                    ║
║   ║                                                                     ║
║   ║  💡 ใช้ Polymorphism, Strategy Pattern, หรือ Plugin แทน            ║
║   ║     การเพิ่ม if-else ยาว ๆ ทุกครั้งที่มี Requirement ใหม่          ║
║   ║                                                                     ║
╠═══╬═════════════════════════════════════════════════════════════════════╣
║   ║                                                                     ║
║ L ║  Liskov Substitution Principle (หลักการแทนที่ของลิสคอฟ)            ║
║   ║  ─────────────────────────────────────────────────────────────      ║
║   ║                                                                     ║
║   ║  📖 คำศัพท์สำคัญ:                                                  ║
║   ║  ┌───────────────────────────────────────────────────────────┐      ║
║   ║  │ Superclass (คลาสแม่) = คลาสต้นแบบที่ถูกสืบทอด            │      ║
║   ║  │   → เปรียบเหมือน "แม่พิมพ์" ที่กำหนดคุณสมบัติกลาง       │      ║
║   ║  │   → ตัวอย่าง: class Animal มี method eat(), sleep()      │      ║
║   ║  │                                                           │      ║
║   ║  │ Subclass (คลาสลูก) = คลาสที่สืบทอดมาจาก Superclass      │      ║
║   ║  │   → ได้รับคุณสมบัติทุกอย่างจากคลาสแม่ + เพิ่มของตัวเอง  │      ║
║   ║  │   → ตัวอย่าง: class Dog extends Animal → มี eat(),       │      ║
║   ║  │     sleep() จาก Animal + เพิ่ม bark() ของตัวเอง          │      ║
║   ║  │                                                           │      ║
║   ║  │         Animal (Superclass/คลาสแม่)                       │      ║
║   ║  │        ┌──────────────────────┐                           │      ║
║   ║  │        │  eat()   sleep()     │                           │      ║
║   ║  │        └────────┬─────────────┘                           │      ║
║   ║  │           ┌─────┴─────┐                                   │      ║
║   ║  │           ▼           ▼                                   │      ║
║   ║  │   ┌──────────┐ ┌──────────┐  (Subclass/คลาสลูก)          │      ║
║   ║  │   │   Dog    │ │   Cat    │                               │      ║
║   ║  │   │ bark()   │ │ meow()   │  ← เพิ่ม method ของตัวเอง   │      ║
║   ║  │   └──────────┘ └──────────┘                               │      ║
║   ║  └───────────────────────────────────────────────────────────┘      ║
║   ║                                                                     ║
║   ║  หลัก LSP: Subclass ต้องสามารถ "แทนที่" Superclass ได้             ║
║   ║  โดยไม่ทำให้โปรแกรมทำงานผิดพลาด                                    ║
║   ║  → ที่ไหนใช้ Animal ได้ ต้องใช้ Dog หรือ Cat แทนได้เสมอ           ║
║   ║                                                                     ║
║   ║  ❌ BAD:  class Penguin extends Bird → fly() throws Error          ║
║   ║           เพราะเพนกวินบินไม่ได้ แต่ Bird บอกว่าบินได้              ║
║   ║           → ใช้ Penguin แทน Bird ไม่ได้ เพราะ fly() พัง!          ║
║   ║  ✅ GOOD: แยก interface FlyableBird และ NonFlyableBird              ║
║   ║           เพนกวินไม่ต้อง implement fly() ที่ไม่สมเหตุสมผล          ║
║   ║                                                                     ║
║   ║  💡 ถ้า Subclass ต้อง override method แล้ว throw error              ║
║   ║     หรือปล่อยว่าง → แสดงว่าผิดหลัก LSP ควรออกแบบใหม่              ║
║   ║                                                                     ║
╠═══╬═════════════════════════════════════════════════════════════════════╣
║   ║                                                                     ║
║ I ║  Interface Segregation Principle (หลักแยก Interface)                ║
║   ║  ─────────────────────────────────────────────────────────────      ║
║   ║  อย่าบังคับให้ class ต้อง implement method ที่ไม่ได้ใช้             ║
║   ║  แยก Interface ใหญ่ → หลาย Interface เล็กเฉพาะทาง                  ║
║   ║                                                                     ║
║   ║  ❌ BAD:  interface Worker → work(), eat(), sleep(), drive()       ║
║   ║           Robot ต้อง implement eat(), sleep() ทั้งที่ไม่จำเป็น     ║
║   ║  ✅ GOOD: interface Workable → work()                               ║
║   ║           interface Eatable  → eat()                                ║
║   ║           Robot implement แค่ Workable เท่านั้น                     ║
║   ║                                                                     ║
║   ║  💡 Interface ที่ดีควรมีขนาดเล็ก เฉพาะเจาะจง                      ║
║   ║     ดีกว่า Interface ใหญ่ที่รวมทุกอย่างไว้ที่เดียว                  ║
║   ║                                                                     ║
╠═══╬═════════════════════════════════════════════════════════════════════╣
║   ║                                                                     ║
║ D ║  Dependency Inversion Principle (หลักกลับทิศการพึ่งพา)             ║
║   ║  ─────────────────────────────────────────────────────────────      ║
║   ║  Module ระดับสูง ไม่ควรพึ่งพา Module ระดับต่ำโดยตรง                ║
║   ║  ทั้งคู่ควรพึ่งพา "Abstraction" (Interface) แทน                    ║
║   ║                                                                     ║
║   ║  ❌ BAD:  class OrderService ใช้ MySQLDatabase โดยตรง              ║
║   ║           → เปลี่ยนเป็น MongoDB ต้องแก้ OrderService               ║
║   ║  ✅ GOOD: class OrderService ใช้ interface Database                 ║
║   ║           → MySQLDatabase หรือ MongoDB implement Database           ║
║   ║           → เปลี่ยน DB ได้โดยไม่แก้ OrderService เลย               ║
║   ║                                                                     ║
║   ║  💡 คิดง่าย ๆ คือ "เสียบปลั๊ก" — ปลั๊กไฟ (Interface) เป็น        ║
║   ║     มาตรฐาน จะเสียบอุปกรณ์ไหนก็ได้ที่รองรับ                       ║
║   ║                                                                     ║
╚═══╩═════════════════════════════════════════════════════════════════════╝
```

### 2.2 หลักการ DRY, KISS, YAGNI

```
┌──────────────────────────────────────────────────────────────┐
│                   🎯 DEVELOPMENT PRINCIPLES                   │
├─────────────┬────────────────────────────────────────────────┤
│  DRY        │ Don't Repeat Yourself                          │
│             │ → อย่าเขียนโค้ดซ้ำซ้อน                       │
│             │ → ใช้ Function, Class, Module ในการ Reuse โค้ด│
│             │ Ex: แทนที่จะคำนวณ VAT ซ้ำในหลายที่           │
│             │     → สร้าง calculateVAT() function เดียว     │
├─────────────┼────────────────────────────────────────────────┤
│  KISS       │ Keep It Simple, Stupid                         │
│             │ → ออกแบบให้เรียบง่ายที่สุดเท่าที่เป็นไปได้   │
│             │ → ซอฟต์แวร์ที่ดีไม่จำเป็นต้องซับซ้อน         │
│             │ Ex: ใช้ if-else แทน nested ternary operator    │
├─────────────┼────────────────────────────────────────────────┤
│  YAGNI      │ You Aren't Gonna Need It                       │
│             │ → อย่าเขียนโค้ดสำหรับ Feature ที่ยังไม่ต้องการ│
│             │ → สร้างเฉพาะสิ่งที่จำเป็นตอนนี้              │
│             │ Ex: อย่าสร้าง Admin Panel ถ้ายังไม่มี Admin   │
└─────────────┴────────────────────────────────────────────────┘
```

### 2.3 Clean Code Principles

> 💡 **Clean Code** คือโค้ดที่อ่านง่าย เข้าใจง่าย และบำรุงรักษาได้ง่าย เป็นหนึ่งในสิ่งที่ Software Professional ต้องให้ความสำคัญ

```python
# ❌ BAD CODE — ยากต่อการอ่านและเข้าใจ
def calc(x, y, z):
    r = x * y
    if z == 1:
        r = r * 1.07
    return r

# ✅ CLEAN CODE — อ่านง่าย เข้าใจชัดเจน
TAX_RATE = 0.07
INCLUDE_TAX = 1

def calculate_total_price(unit_price: float, quantity: int, tax_option: int) -> float:
    """
    คำนวณราคารวมทั้งหมด
    
    Args:
        unit_price: ราคาต่อหน่วย
        quantity: จำนวน
        tax_option: 1 = รวมภาษี, 0 = ไม่รวมภาษี
    
    Returns:
        ราคารวมทั้งหมด
    """
    subtotal = unit_price * quantity
    
    if tax_option == INCLUDE_TAX:
        return subtotal * (1 + TAX_RATE)
    
    return subtotal
```

---

## 3. Competency Framework

> 💡 **Competency Framework** คือกรอบการพัฒนาความสามารถของ Software Professional ที่ประกอบด้วยทักษะหลากหลายด้าน

```
                    🎯 SOFTWARE PROFESSIONAL COMPETENCY FRAMEWORK
                    
    ┌─────────────────────────────────────────────────────────────┐
    │                                                             │
    │   ┌─────────────────────────────────────────────────┐      │
    │   │          💼 PROFESSIONAL SKILLS                  │      │
    │   │   Leadership │ Communication │ Time Management   │      │
    │   └─────────────────────────────────────────────────┘      │
    │                                                             │
    │   ┌─────────────────────────────────────────────────┐      │
    │   │            🤝 COLLABORATIVE SKILLS               │      │
    │   │    Teamwork │ Code Review │ Pair Programming     │      │
    │   └─────────────────────────────────────────────────┘      │
    │                                                             │
    │   ┌─────────────────────────────────────────────────┐      │
    │   │           🔧 ENGINEERING PRACTICES               │      │
    │   │   Testing │ CI/CD │ DevOps │ Code Quality        │      │
    │   └─────────────────────────────────────────────────┘      │
    │                                                             │
    │   ┌─────────────────────────────────────────────────┐      │
    │   │          💻 TECHNICAL KNOWLEDGE (CORE)           │      │
    │   │  Programming │ Algorithms │ Data Structures      │      │
    │   │  System Design │ Databases │ Networking          │      │
    │   └─────────────────────────────────────────────────┘      │
    │                                                             │
    └─────────────────────────────────────────────────────────────┘
                    (Foundation → Advanced)
```

### 3.1 T-Shaped Skills Model

> 💡 **T-Shaped Skills** คือแนวคิดที่ Software Professional ควรมีความรู้กว้างในหลายด้าน (แนวนอนของ T) และมีความเชี่ยวชาญเจาะลึกในอย่างน้อยหนึ่งด้าน (แนวตั้งของ T)

```
        ◄──────────── BROAD KNOWLEDGE (Breadth) ────────────►
        
  ┌────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┐
  │ FE │ BE │ DB │ OS │ NW │ CD │ QA │ UX │ PM │ SC │ AI │
  └────┴────┴────┴────┴────┴────┴────┴────┴────┴────┴────┘
                          │
                   DEEP EXPERTISE
                   (Depth)
                          │
                   ┌──────┴──────┐
                   │             │
                   │   Backend   │
                   │ Development │
                   │             │
                   │   Node.js   │
                   │   Python    │
                   │   APIs      │
                   │   Docker    │
                   │             │
                   └─────────────┘
                   
   FE=Frontend, BE=Backend, DB=Database, OS=Operating System
   NW=Networking, CD=CI/CD, QA=Quality Assurance
   UX=User Experience, PM=Project Management
   SC=Security, AI=Artificial Intelligence
```

---

## 4. Hard Skills vs Soft Skills

> 💡 **Software Professional ที่ดี** ต้องมีทั้ง Hard Skills (ทักษะทางเทคนิค) และ Soft Skills (ทักษะด้านบุคคล) เพราะทั้งสองส่วนขาดกันไม่ได้ในสภาพแวดล้อมการทำงานจริง

```
┌──────────────────────────────┐    ┌──────────────────────────────┐
│       💻 HARD SKILLS         │    │       🧠 SOFT SKILLS          │
├──────────────────────────────┤    ├──────────────────────────────┤
│                              │    │                              │
│  📌 Programming Languages    │    │  🗣️  Communication           │
│     Python, JS, Java, Go     │    │     พูด เขียน นำเสนอ        │
│                              │    │                              │
│  📌 Version Control          │    │  🤝 Teamwork                 │
│     Git, GitHub, GitLab      │    │     ทำงานร่วมกับผู้อื่น      │
│                              │    │                              │
│  📌 Databases                │    │  🧩 Problem Solving          │
│     SQL, NoSQL, Redis        │    │     คิดวิเคราะห์แก้ปัญหา    │
│                              │    │                              │
│  📌 DevOps Tools             │    │  ⏰ Time Management          │
│     Docker, K8s, CI/CD       │    │     จัดการเวลา ตรงต่อเวลา   │
│                              │    │                              │
│  📌 System Design            │    │  🔄 Adaptability             │
│     Architecture, API        │    │     ปรับตัวกับการเปลี่ยนแปลง │
│                              │    │                              │
│  📌 Testing                  │    │  🎯 Critical Thinking        │
│     Unit, Integration, E2E   │    │     คิดเชิงวิพากษ์           │
│                              │    │                              │
│  📌 Cloud Platforms          │    │  📚 Continuous Learning      │
│     AWS, GCP, Azure          │    │     เรียนรู้ตลอดชีวิต        │
│                              │    │                              │
└──────────────────────────────┘    └──────────────────────────────┘
```

### 4.1 ความสำคัญของ Soft Skills ในการทำงาน

```
📊 การสำรวจ: เหตุผลที่นักพัฒนาซอฟต์แวร์ถูกปฏิเสธหรือไล่ออก

  Soft Skills Issues  │████████████████████████████████████  75%
  Technical Issues    │████████████████████████             52%
  Attitude Issues     │██████████████████████████████       65%
  Culture Fit Issues  │████████████████████████████         60%
  
  ※ ข้อมูลแสดงให้เห็นว่า Soft Skills มีความสำคัญไม่แพ้ Technical Skills
```

---

## 5. Software Engineering Roles & Responsibilities

> 💡 ในการพัฒนาซอฟต์แวร์สมัยใหม่ มีบทบาทหลากหลายที่ทำงานร่วมกันเป็น Team เพื่อให้ Product สำเร็จ การเข้าใจบทบาทแต่ละส่วนช่วยให้ทำงานร่วมกันได้อย่างมีประสิทธิภาพ

```
╔═══════════════════════════════════════════════════════════════════╗
║              🏢 SOFTWARE DEVELOPMENT TEAM STRUCTURE               ║
╠═══════════════════════════════════════════════════════════════════╣
║                                                                   ║
║   [Product Owner]──────────────────────────────────────────┐     ║
║        │                                                    │     ║
║        │  Define Requirements & Priority                    │     ║
║        ▼                                                    ▼     ║
║   [Scrum Master]                                    [Stakeholders]║
║        │                                                         ║
║        │  Facilitate & Remove Blockers                           ║
║        ▼                                                         ║
║   ┌────────────────────────────────────────────────────┐         ║
║   │                  🛠️  DEV TEAM                       │         ║
║   │                                                    │         ║
║   │  [Frontend Dev] ←──→ [Backend Dev] ←──→ [DBA]     │         ║
║   │        │                   │               │       │         ║
║   │        └──────────┬────────┘               │       │         ║
║   │                   ▼                        │       │         ║
║   │            [Full Stack Dev]                │       │         ║
║   │                   │                        │       │         ║
║   │            [DevOps Engineer] ◄─────────────┘       │         ║
║   │                   │                                │         ║
║   │            [QA / Test Engineer]                    │         ║
║   │                   │                                │         ║
║   │            [Security Engineer]                     │         ║
║   └────────────────────────────────────────────────────┘         ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
```

### 5.1 รายละเอียดแต่ละบทบาท

| Role | หน้าที่หลัก | ทักษะที่ต้องการ | เครื่องมือที่ใช้ |
|------|------------|-----------------|-----------------|
| **Frontend Developer** | พัฒนา UI/UX ของแอปพลิเคชัน | HTML, CSS, JavaScript, React/Vue | VS Code, Figma, Chrome DevTools |
| **Backend Developer** | พัฒนา API, Business Logic, Database | Node.js, Python, Java, SQL | Postman, Docker, Database Tools |
| **Full Stack Developer** | พัฒนาทั้ง Frontend และ Backend | รวมทั้งสองฝั่ง | รวมทั้งสองฝั่ง |
| **DevOps Engineer** | CI/CD, Infrastructure, Automation | Linux, Docker, Kubernetes, Bash | Jenkins, GitLab CI, Terraform |
| **QA Engineer** | ทดสอบซอฟต์แวร์ให้ได้คุณภาพ | Testing Techniques, Test Automation | Selenium, JUnit, Jest, Postman |
| **Database Administrator** | ออกแบบและดูแลฐานข้อมูล | SQL, NoSQL, Query Optimization | MySQL, PostgreSQL, MongoDB |
| **Security Engineer** | ดูแลความปลอดภัยของระบบ | Penetration Testing, Security Audit | OWASP, Burp Suite, Nessus |
| **Scrum Master** | อำนวยการทำงานแบบ Agile | Agile, Scrum, Communication | Jira, Trello, Confluence |
| **Product Owner** | กำหนด Vision และ Priority ของ Product | Business Analysis, Communication | Jira, Figma, Miro |

---

## 6. Software Development Lifecycle (SDLC)

> 💡 **SDLC (Software Development Lifecycle)** คือกระบวนการพัฒนาซอฟต์แวร์ที่มีโครงสร้างชัดเจน ตั้งแต่การวางแผนจนถึงการบำรุงรักษา

### 6.1 SDLC Overview

```
     ┌─────────────────────────────────────────────────────────┐
     │                   🔄 SDLC CYCLE                         │
     └─────────────────────────────────────────────────────────┘
     
          ┌─────────────────────────────────────────┐
          │                                         │
          ▼                                         │
   ┌─────────────┐                          ┌───────────────┐
   │  1. PLAN    │                          │  6. MAINTAIN  │
   │  วางแผน     │                          │  บำรุงรักษา   │
   └──────┬──────┘                          └───────▲───────┘
          │                                         │
          ▼                                         │
   ┌─────────────┐                          ┌───────────────┐
   │  2. ANALYZE │                          │  5. DEPLOY    │
   │  วิเคราะห์  │                          │  ติดตั้ง      │
   └──────┬──────┘                          └───────▲───────┘
          │                                         │
          ▼                                         │
   ┌─────────────┐                          ┌───────────────┐
   │  3. DESIGN  │──────────────────────────│  4. DEVELOP & │
   │  ออกแบบ     │                          │     TEST      │
   └─────────────┘                          │  พัฒนาและทดสอบ│
                                            └───────────────┘
```

### 6.2 รายละเอียดแต่ละ Phase

```
╔══════════════════════════════════════════════════════════════════╗
║  PHASE          │ กิจกรรม              │ Output                 ║
╠══════════════════════════════════════════════════════════════════╣
║  1. PLANNING    │ • กำหนดวัตถุประสงค์  │ • Project Plan         ║
║  (วางแผน)      │ • ประเมินต้นทุน/เวลา │ • Feasibility Study    ║
║                 │ • วิเคราะห์ความเป็น  │ • Resource Plan        ║
║                 │   ไปได้               │                        ║
╠══════════════════════════════════════════════════════════════════╣
║  2. ANALYSIS    │ • รวบรวม Requirements │ • SRS Document         ║
║  (วิเคราะห์)   │ • วิเคราะห์ความต้อง  │ • Use Case Diagrams    ║
║                 │   การของผู้ใช้        │ • User Stories         ║
╠══════════════════════════════════════════════════════════════════╣
║  3. DESIGN      │ • ออกแบบ Architecture │ • System Architecture  ║
║  (ออกแบบ)      │ • ออกแบบ Database     │ • DB Schema            ║
║                 │ • ออกแบบ UI/UX        │ • Wireframes/Mockups   ║
╠══════════════════════════════════════════════════════════════════╣
║  4. DEVELOP &   │ • เขียนโค้ด           │ • Source Code          ║
║     TEST        │ • Unit Testing        │ • Test Reports         ║
║  (พัฒนาและ     │ • Integration Testing │ • Bug Reports          ║
║   ทดสอบ)       │ • Code Review         │ • Reviewed Code        ║
╠══════════════════════════════════════════════════════════════════╣
║  5. DEPLOYMENT  │ • Deploy สู่ Production│ • Running Application  ║
║  (ติดตั้ง)     │ • Configuration       │ • Deployment Docs      ║
║                 │ • Smoke Testing       │ • Release Notes        ║
╠══════════════════════════════════════════════════════════════════╣
║  6. MAINTENANCE │ • Bug Fixing          │ • Patches & Updates    ║
║  (บำรุงรักษา)  │ • Performance Tuning  │ • Performance Reports  ║
║                 │ • Feature Updates     │ • Updated Source Code  ║
╚══════════════════════════════════════════════════════════════════╝
```

### 6.3 SDLC Models เปรียบเทียบ

```
┌─────────────────────────────────────────────────────────────────┐
│                    📊 SDLC MODELS COMPARISON                     │
└─────────────────────────────────────────────────────────────────┘

🔴 WATERFALL MODEL
────────────────
[Plan]──►[Analyze]──►[Design]──►[Code]──►[Test]──►[Deploy]
 ↓ Linear, Sequential, ยากในการกลับมาแก้ไข Phase ก่อนหน้า

🟡 V-MODEL
──────────
[Req]──►[Design]──►[Code]──►[Test]──►[Integration Test]
  └──────────────────────────────────────────────────┘
 ↓ Testing ควบคู่กับ Development แต่ยังเป็น Sequential

🟢 AGILE MODEL (แนะนำ)
─────────────────────
Sprint 1:  [Plan]─[Dev]─[Test]─[Review] ──► Working Software
Sprint 2:  [Plan]─[Dev]─[Test]─[Review] ──► Working Software  
Sprint 3:  [Plan]─[Dev]─[Test]─[Review] ──► Working Software
Sprint N:  [Plan]─[Dev]─[Test]─[Review] ──► Final Product
 ↓ Iterative, Flexible, ตอบสนองต่อการเปลี่ยนแปลงได้ดี

🔵 DEVOPS MODEL
───────────────
 ┌─► Plan ─► Code ─► Build ─► Test ─► Release ─► Deploy ─┐
 └──────────────────── Monitor & Feedback ◄────────────────┘
 ↓ Continuous Delivery, Automation, Collaboration between Dev & Ops
```

---

## 7. Professional Ethics & Code of Conduct

> 💡 **จริยธรรมวิชาชีพ (Professional Ethics)** เป็นสิ่งที่ Software Professional ต้องยึดถือ เพราะซอฟต์แวร์มีผลกระทบต่อชีวิตผู้คนจำนวนมากในยุคดิจิทัล

### 7.1 ACM/IEEE Code of Ethics

> **ACM (Association for Computing Machinery)** และ **IEEE** ได้กำหนด Code of Ethics สำหรับ Software Engineers ไว้ 8 ข้อหลัก

```
╔═══════════════════════════════════════════════════════════════╗
║          ⚖️  ACM/IEEE SOFTWARE ENGINEERING CODE OF ETHICS      ║
╠═══╦═══════════════════════════════════════════════════════════╣
║ 1 ║ PUBLIC — ทำหน้าที่เพื่อประโยชน์สาธารณะ                  ║
║   ║ Software ต้องไม่เป็นอันตรายต่อสาธารณชน                  ║
╠═══╬═══════════════════════════════════════════════════════════╣
║ 2 ║ CLIENT & EMPLOYER — ทำงานให้ตรงกับผลประโยชน์ของลูกค้า  ║
║   ║ ซื่อสัตย์ต่อนายจ้าง ไม่เปิดเผยความลับขององค์กร          ║
╠═══╬═══════════════════════════════════════════════════════════╣
║ 3 ║ PRODUCT — รับประกันคุณภาพของงานที่ทำ                    ║
║   ║ ส่งงานที่มีมาตรฐานสูงสุดที่ทำได้                        ║
╠═══╬═══════════════════════════════════════════════════════════╣
║ 4 ║ JUDGMENT — รักษาความซื่อสัตย์และเป็นอิสระในการตัดสินใจ ║
║   ║ ไม่รับงานที่ขัดต่อจริยธรรม                               ║
╠═══╬═══════════════════════════════════════════════════════════╣
║ 5 ║ MANAGEMENT — ส่งเสริมจริยธรรมในการบริหารจัดการ          ║
║   ║ ผู้นำต้องปฏิบัติตนเป็นแบบอย่างที่ดี                     ║
╠═══╬═══════════════════════════════════════════════════════════╣
║ 6 ║ PROFESSION — ส่งเสริมความซื่อสัตย์ในวิชาชีพ             ║
║   ║ พัฒนาและยกระดับมาตรฐานวิชาชีพ                           ║
╠═══╬═══════════════════════════════════════════════════════════╣
║ 7 ║ COLLEAGUES — ปฏิบัติต่อเพื่อนร่วมงานอย่างยุติธรรม       ║
║   ║ ช่วยเหลือและสนับสนุนการพัฒนาของเพื่อนร่วมทีม            ║
╠═══╬═══════════════════════════════════════════════════════════╣
║ 8 ║ SELF — เรียนรู้และพัฒนาตนเองอย่างต่อเนื่อง              ║
║   ║ ติดตามความรู้ใหม่ ๆ ในวิชาชีพอยู่เสมอ                   ║
╚═══╩═══════════════════════════════════════════════════════════╝
```

### 7.2 ตัวอย่างสถานการณ์จริยธรรม

```
🔴 SCENARIO 1: Data Privacy
─────────────────────────────
สถานการณ์: บริษัทขอให้คุณเก็บข้อมูลผู้ใช้โดยไม่แจ้ง
❌ Wrong: เก็บข้อมูลลับ ๆ ตามที่บริษัทสั่ง
✅ Right: แจ้งให้บริษัทปรับ Privacy Policy หรือปฏิเสธงาน

🟡 SCENARIO 2: Code Quality
─────────────────────────────
สถานการณ์: PM กดดันให้ส่งงานเร็ว แต่ยังมี Bug อยู่
❌ Wrong: ส่งงานทั้งที่รู้ว่ามี Critical Bug
✅ Right: แจ้ง PM อย่างตรงไปตรงมา เสนอ Timeline ที่เหมาะสม

🟢 SCENARIO 3: Intellectual Property
──────────────────────────────────────
สถานการณ์: พบ Library ที่ดีมาก แต่ไม่ได้ดู License
❌ Wrong: ใช้เลย เพราะคิดว่า Open Source คือฟรี
✅ Right: ตรวจสอบ License (MIT, Apache, GPL) ก่อนเสมอ
```

---

## 8. Growth Mindset & Continuous Learning

> 💡 **Growth Mindset** คือความเชื่อว่าความสามารถสามารถพัฒนาได้ผ่านการฝึกฝนและการเรียนรู้ ซึ่งเป็นคุณสมบัติสำคัญของ Software Professional ในยุคที่เทคโนโลยีเปลี่ยนแปลงรวดเร็ว

### 8.1 Fixed Mindset vs Growth Mindset

```
┌──────────────────────────────────┬──────────────────────────────────┐
│      🔒 FIXED MINDSET            │      🌱 GROWTH MINDSET            │
├──────────────────────────────────┼──────────────────────────────────┤
│ "ฉันไม่เก่งเรื่องนี้"            │ "ฉันยังไม่เก่งเรื่องนี้"          │
│ "มันยากเกินไปสำหรับฉัน"          │ "ยาก แต่ฉันสามารถเรียนรู้ได้"    │
│ "ความล้มเหลวคือสัญญาณว่าฉันไม่เก่ง" │ "ความล้มเหลวคือบทเรียน"        │
│ "ฉันไม่ต้องการ Feedback"         │ "Feedback ช่วยให้ฉันพัฒนา"       │
│ "ความสำเร็จของคนอื่นทำให้ฉันรู้สึกแย่" │ "ความสำเร็จของคนอื่นสร้างแรงบันดาลใจ" │
└──────────────────────────────────┴──────────────────────────────────┘
```

### 8.2 Continuous Learning Path

```
📚 LEARNING PATHWAY FOR SOFTWARE PROFESSIONALS

Year 1: FOUNDATION
─────────────────
[Fundamentals] → [Version Control] → [Basic Programming] → [First Project]
     │                  │                    │                    │
  Math & Logic        Git/GitHub           Python/JS          Portfolio

Year 2: INTERMEDIATE  
────────────────────
[Backend Dev] → [Database] → [API Design] → [Testing] → [Docker]
     │               │             │             │          │
  Node/Python      SQL/NoSQL     REST/GraphQL  Unit Test  Container

Year 3: ADVANCED
────────────────
[System Design] → [Cloud] → [Kubernetes] → [CI/CD] → [Architecture]
       │             │           │             │            │
   Microservices  AWS/GCP     Orchestration  Jenkins    Senior Dev

Year 4+: EXPERT
───────────────
[Specialization] → [Leadership] → [Mentoring] → [Innovation]
        │               │               │              │
   Deep Expertise   Tech Lead      Teach Others    Create New Tools
```

### 8.3 แหล่งเรียนรู้สำหรับ Software Professional

```
🌐 LEARNING RESOURCES

┌─────────────────────────────────────────────────────────────┐
│  📖 DOCUMENTATION (อ่านเพิ่มเติมได้ที่)                     │
│  • docs.docker.com      • kubernetes.io/docs                │
│  • git-scm.com          • developer.mozilla.org             │
│  • docs.github.com      • pythondocs.org                    │
├─────────────────────────────────────────────────────────────┤
│  🎓 ONLINE COURSES                                          │
│  • Coursera             • Udemy                             │
│  • edX                  • Pluralsight                       │
│  • LinkedIn Learning    • MIT OpenCourseWare                │
├─────────────────────────────────────────────────────────────┤
│  💻 PRACTICE PLATFORMS                                      │
│  • LeetCode (Algorithms)  • HackerRank (Challenges)         │
│  • Exercism (Languages)   • Kaggle (Data Science)           │
│  • CodeWars (Katas)       • GitHub (Open Source)            │
├─────────────────────────────────────────────────────────────┤
│  📰 BLOGS & COMMUNITIES                                     │
│  • dev.to               • Medium/TechCrunch                 │
│  • Stack Overflow       • Reddit r/programming              │
│  • Hacker News          • ThaiDev Community                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 9. Toolchain ของ Software Professional

> 💡 **Toolchain** คือชุดเครื่องมือที่ Software Professional ใช้ในแต่ละ Phase ของการพัฒนาซอฟต์แวร์ การรู้จักและใช้เครื่องมือที่เหมาะสมช่วยเพิ่มประสิทธิภาพการทำงานได้อย่างมาก

### 9.1 Modern Developer Toolchain

```
╔═══════════════════════════════════════════════════════════════════╗
║              🛠️  MODERN SOFTWARE DEVELOPER TOOLCHAIN              ║
╠═════════════════════════╦═════════════════════════════════════════╣
║  PHASE                  ║  TOOLS                                  ║
╠═════════════════════════╬═════════════════════════════════════════╣
║  📋 Planning &          ║  Jira, Trello, Notion, Confluence       ║
║     Project Management  ║  GitHub Projects, Linear, Asana         ║
╠═════════════════════════╬═════════════════════════════════════════╣
║  💻 Code Editing        ║  VS Code, IntelliJ IDEA, Vim, Neovim    ║
║                         ║  Sublime Text, Cursor (AI Editor)       ║
╠═════════════════════════╬═════════════════════════════════════════╣
║  🔀 Version Control     ║  Git, GitHub, GitLab, Bitbucket         ║
╠═════════════════════════╬═════════════════════════════════════════╣
║  🏗️  Build Tools        ║  Make, Gradle, Maven, npm, pip          ║
║                         ║  Webpack, Vite, esbuild                 ║
╠═════════════════════════╬═════════════════════════════════════════╣
║  🧪 Testing             ║  Jest, PyTest, JUnit, Selenium          ║
║                         ║  Postman, k6, Cypress                   ║
╠═════════════════════════╬═════════════════════════════════════════╣
║  🔄 CI/CD               ║  Jenkins, GitHub Actions, GitLab CI     ║
║                         ║  CircleCI, Travis CI, ArgoCD            ║
╠═════════════════════════╬═════════════════════════════════════════╣
║  📦 Containerization    ║  Docker, Podman                         ║
║     & Orchestration     ║  Kubernetes, Docker Swarm, Helm         ║
╠═════════════════════════╬═════════════════════════════════════════╣
║  ☁️  Cloud Platforms    ║  AWS, Google Cloud, Azure               ║
║                         ║  DigitalOcean, Linode, Heroku           ║
╠═════════════════════════╬═════════════════════════════════════════╣
║  📊 Monitoring &        ║  Prometheus, Grafana, Datadog           ║
║     Observability       ║  ELK Stack, New Relic, Sentry           ║
╠═════════════════════════╬═════════════════════════════════════════╣
║  💬 Communication       ║  Slack, Microsoft Teams, Discord        ║
║     & Collaboration     ║  Zoom, Google Meet, Miro                ║
╚═════════════════════════╩═════════════════════════════════════════╝
```

### 9.2 DevOps Toolchain Flow

```
        CODE ──────────────────────────────────────────► PRODUCTION
        
  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────────┐
  │  WRITE   │    │  BUILD   │    │   TEST   │    │   DEPLOY     │
  │  CODE    │───►│  &       │───►│  &       │───►│   &          │
  │          │    │  COMPILE │    │  VERIFY  │    │   RELEASE    │
  └──────────┘    └──────────┘    └──────────┘    └──────────────┘
       │                │               │                 │
  VS Code           npm build         Jest           Docker/K8s
  Git               Webpack          Cypress          Jenkins
  GitHub            Docker build     SonarQube        GitHub Actions
                                     Postman          ArgoCD
  
  └──────────────────────────────────────────────────────────────┘
                             FEEDBACK LOOP
                         Monitoring + Alerting
                        Prometheus + Grafana + Sentry
```

### 9.3 เครื่องมือที่จะเรียนในวิชานี้

```
┌─────────────────────────────────────────────────────────────────┐
│          📚 TOOLS COVERED IN THIS COURSE                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Session 1-4:  🔀 GIT & GITHUB                                  │
│  ─────────────────────────────────────────                      │
│  git init    git clone   git add    git commit                  │
│  git push    git pull    git branch git merge                   │
│  git revert  git reset   git rebase                             │
│                                                                 │
│  Session 5-8:  🐳 DOCKER                                        │
│  ─────────────────────────────────────────                      │
│  docker run   docker build   docker push                        │
│  docker-compose              docker swarm                       │
│  Dockerfile   docker network docker volume                      │
│                                                                 │
│  Session 9:   🔄 CI/CD with JENKINS                             │
│  ─────────────────────────────────────────                      │
│  Jenkinsfile   Pipeline Stages   Build Triggers                 │
│  Automated Testing              Deployment Automation           │
│                                                                 │
│  Session 10-14: ☸️  KUBERNETES                                  │
│  ─────────────────────────────────────────                      │
│  kubectl       Pods             Services                        │
│  Deployments   ReplicaSets      ConfigMaps                      │
│  Namespaces    Ingress          YAML Configs                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 10. สรุป (Summary)

> 💡 หัวข้อ **Principles to Software Professionals** วางรากฐานสำคัญสำหรับการเดินทางสู่การเป็น Software Professional ที่มีคุณภาพ

```
╔═════════════════════════════════════════════════════════════════╗
║            🏆 KEY TAKEAWAYS — Principles to Software Pros       ║
╠═════════════════════════════════════════════════════════════════╣
║                                                                 ║
║  1️⃣  Software Professional ≠ แค่คนเขียนโค้ด                    ║
║     → ต้องมีทั้ง Technical Skills + Soft Skills + Ethics       ║
║                                                                 ║
║  2️⃣  Core Principles สำคัญมาก                                  ║
║     → SOLID, DRY, KISS, YAGNI ช่วยให้โค้ดมีคุณภาพ             ║
║                                                                 ║
║  3️⃣  เข้าใจ SDLC และ Agile                                     ║
║     → การพัฒนาซอฟต์แวร์มีกระบวนการที่ชัดเจน                   ║
║     → Agile ช่วยให้ทีมปรับตัวได้รวดเร็ว                        ║
║                                                                 ║
║  4️⃣  Professional Ethics สำคัญมากในยุคดิจิทัล                  ║
║     → ซอฟต์แวร์ส่งผลต่อชีวิตผู้คน จงรับผิดชอบ                 ║
║                                                                 ║
║  5️⃣  Growth Mindset & Continuous Learning                       ║
║     → เทคโนโลยีเปลี่ยนเร็ว ต้องเรียนรู้ตลอดเวลา               ║
║                                                                 ║
║  6️⃣  รู้จัก Toolchain ของตัวเอง                                 ║
║     → เลือกและใช้เครื่องมือให้เหมาะกับงาน                      ║
║                                                                 ║
╚═════════════════════════════════════════════════════════════════╝
```

### 🗺️ ภาพรวมการเดินทางสู่ Software Professional

```
              🎓 YOUR JOURNEY TO SOFTWARE PROFESSIONAL
              
BEGINNER ────────────────────────────────────────► EXPERT
   │                                                  │
   ▼                                                  ▼
[Student]  →  [Junior Dev]  →  [Mid Dev]  →  [Senior Dev]
   │               │               │               │
   │           1-2 years       3-5 years        5+ years
   │               │               │               │
Know the       Write Code      Design Systems  Lead Teams
Basics        Follow Patterns  Mentor Others   Architect Solutions
               Fix Bugs        Code Review     Drive Standards
               Learn Tools     Write Tests     Community Impact


               ┌─────────────────────────┐
               │  💡 REMEMBER:           │
               │                         │
               │  The best time to       │
               │  start was yesterday.   │
               │                         │
               │  The second best time   │
               │  is NOW. 🚀             │
               └─────────────────────────┘
```

---

## 📝 แบบฝึกหัด (Exercises)

### ✏️ Exercise 1: Self-Assessment
> ประเมินตนเองว่าคุณอยู่ใน Level ไหน และต้องพัฒนาทักษะใดบ้าง

```
Rate yourself (1-5) in each area:

Technical Skills:
[ ] Programming Fundamentals  ___/5
[ ] Version Control (Git)     ___/5
[ ] Database Knowledge         ___/5
[ ] System Design              ___/5
[ ] Testing                    ___/5

Soft Skills:
[ ] Communication              ___/5
[ ] Teamwork                   ___/5
[ ] Problem Solving            ___/5
[ ] Time Management            ___/5
[ ] Continuous Learning        ___/5

Professional Skills:
[ ] Understanding of SDLC      ___/5
[ ] Knowledge of Tools         ___/5
[ ] Ethics Awareness           ___/5
```

### ✏️ Exercise 2: Code Review Practice
> อ่านโค้ดต่อไปนี้แล้วระบุปัญหาตาม Clean Code Principles

```python
# ตรวจสอบโค้ดนี้ — มีปัญหาอะไรบ้าง?

def f(a, b, c, d, e):
    x = a + b
    y = x * c
    if d == True:
        y = y + (y * 0.07)
    if e == 1:
        print("สำเร็จ")
        return y
    else:
        print("ล้มเหลว")
        return -1

# คำถาม:
# 1. ชื่อ function และ parameter บอกอะไรได้บ้าง?
# 2. มีค่า Magic Number อะไรบ้าง?
# 3. Function นี้ทำหลายอย่างเกินไปไหม? (SRP)
# 4. จะ Refactor ให้ดีขึ้นอย่างไร?
```

---

## 🔗 แหล่งอ้างอิงเพิ่มเติม (References)

| หัวข้อ | แหล่งข้อมูล | ประเภท |
|--------|------------|--------|
| Clean Code | *"Clean Code"* by Robert C. Martin | 📚 Book |
| SOLID Principles | [solidprinciples.io](https://solidprinciples.io) | 🌐 Website |
| ACM Code of Ethics | [acm.org/code-of-ethics](https://www.acm.org/code-of-ethics) | 🌐 Website |
| Software Engineering | *"The Pragmatic Programmer"* by Hunt & Thomas | 📚 Book |
| Agile Manifesto | [agilemanifesto.org](https://agilemanifesto.org) | 🌐 Website |
| Git Documentation | [git-scm.com](https://git-scm.com/doc) | 🌐 Website |
| Docker Documentation | [docs.docker.com](https://docs.docker.com) | 🌐 Website |
| Kubernetes Documentation | [kubernetes.io/docs](https://kubernetes.io/docs) | 🌐 Website |

---

<div align="center">

**📌 Session 1 | SOFTWARE DEVELOPMENT TOOLS AND ENVIRONMENTS**  
**👨‍🏫 TUCHSANAI PLOYSUWAN**

```
"Good software is built by good professionals.
 Good professionals are built by good principles."
```

</div>