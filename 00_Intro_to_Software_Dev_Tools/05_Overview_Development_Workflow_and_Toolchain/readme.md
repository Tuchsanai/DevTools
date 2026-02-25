# 📖 Overview of Development Workflow & Toolchain

> **Course:** SOFTWARE DEVELOPMENT TOOLS AND ENVIRONMENTS
> **Session:** 1 — Introduction to Software Development Tools & Environments
> **Level:** Beginner → Intermediate

---

## 📑 สารบัญ (Table of Contents)

- [0. วัตถุประสงค์การเรียนรู้](#0)
- [1. Development Workflow คืออะไร?](#1)
- [2. Toolchain คืออะไร?](#2)
- [3. Modern Development Workflow — End-to-End](#3)
- [4. Phase 1: Plan & Design](#4)
- [5. Phase 2: Code & Build](#5)
- [6. Phase 3: Test & Quality Assurance](#6)
- [7. Phase 4: Deploy & Release](#7)
- [8. Phase 5: Monitor & Feedback](#8)
- [9. Workflow Automation — ทำให้ทุกอย่างอัตโนมัติ](#9)
- [10. Toolchain Archetypes — ตัวอย่าง Toolchain ตามขนาดทีม](#10)
- [11. How Tools Connect — Integration Patterns](#11)
- [12. Building Your First Toolchain — Step by Step](#12)
- [13. Common Pitfalls & How to Avoid Them](#13)
- [14. Development Workflow ในวิชานี้](#14)
- [15. สรุป](#15)
- [16. แบบฝึกหัด](#16)

---

## 0. วัตถุประสงค์การเรียนรู้ <a name="0"></a>

```
╔══════════════════════════════════════════════════════════════════════╗
║  🎯 เมื่อเรียนจบหัวข้อนี้ คุณจะสามารถ...                            ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  1. อธิบาย Development Workflow แบบ End-to-End ได้ครบทุก Phase       ║
║  2. แยกแยะความแตกต่างระหว่าง Workflow กับ Toolchain ได้             ║
║  3. เข้าใจว่า Tools แต่ละตัวทำหน้าที่อะไรใน Workflow                ║
║  4. เลือก Toolchain ที่เหมาะสมกับขนาดทีมและประเภทโปรเจกต์ได้        ║
║  5. ออกแบบ Integration Flow ที่เชื่อม Tools เข้าด้วยกันได้           ║
║  6. เข้าใจ Workflow Automation และ CI/CD Pipeline เบื้องต้น          ║
║  7. เชื่อมโยงเนื้อหาทั้งหมดของ Session 1 เข้าเป็นภาพเดียวกันได้     ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
```

> **🕐 เวลาโดยประมาณ:** 2-3 ชั่วโมง (อ่าน + ทำแบบฝึกหัด)

---

## 1. Development Workflow คืออะไร? <a name="1"></a>

> 💡 **Development Workflow** คือ **ลำดับขั้นตอน** ที่ทีมพัฒนาซอฟต์แวร์ทำซ้ำ ๆ ในทุก ๆ รอบการพัฒนา ตั้งแต่ "ได้รับงาน" จนถึง "ส่งมอบให้ผู้ใช้" และ "ตรวจสอบผลลัพธ์" โดยมีเป้าหมายคือทำให้กระบวนการนี้ **เร็ว, เชื่อถือได้, ทำซ้ำได้** ทุกครั้ง

### 1.1 เปรียบเทียบให้เข้าใจง่าย

```
  🍕 Workflow เปรียบเหมือน "สายพานผลิตพิซซ่า"

  ร้านพิซซ่าที่ดี ≠ แค่ทำพิซซ่าอร่อย
  ร้านพิซซ่าที่ดี = กระบวนการที่ทำพิซซ่าอร่อย **ได้ทุกครั้ง** อย่าง**สม่ำเสมอ**

  สายพานร้านพิซซ่า:
  ────────────────────────────────────────────────────────────
  [รับ Order] → [เตรียมแป้ง] → [ใส่ Topping] → [อบ] → [ตรวจสอบ] → [ส่ง]
       │             │               │            │          │          │
    Jira/Trello   IDE/Editor      git add     CI Build   QA Test   Deploy
    (รับงาน)      (เขียนโค้ด)    git commit  (Build)   (ทดสอบ)   (ส่งมอบ)

  Software Development Workflow:
  ────────────────────────────────────────────────────────────
  [Plan] → [Code] → [Commit] → [Build] → [Test] → [Deploy] → [Monitor]
  ────────────────────────────────────────────────────────────

  ✅ ทั้งสองมีจุดร่วมคือ:
  → ทำซ้ำได้ทุกครั้ง (Repeatable)
  → ตรวจสอบคุณภาพก่อนส่ง (Quality Gate)
  → มีลำดับที่ชัดเจน (Sequential with feedback)
  → ปรับปรุงได้ตลอด (Continuous Improvement)
```

### 1.2 Workflow ≠ Toolchain — ความแตกต่างที่ต้องเข้าใจ

```
╔══════════════════════════════════════════════════════════════════════╗
║                 🔑 WORKFLOW vs TOOLCHAIN                             ║
╠═══════════════════════════╦══════════════════════════════════════════╣
║  WORKFLOW                 ║  TOOLCHAIN                               ║
║  (กระบวนการ)               ║  (ชุดเครื่องมือ)                         ║
╠═══════════════════════════╬══════════════════════════════════════════╣
║  "ขั้นตอนที่ต้องทำ"        ║  "เครื่องมือที่ใช้ในแต่ละขั้น"             ║
║                           ║                                          ║
║  1. รับงาน                ║  → Jira / Trello                        ║
║  2. เขียนโค้ด             ║  → VS Code / IntelliJ                   ║
║  3. Commit & Push         ║  → Git / GitHub                         ║
║  4. Build อัตโนมัติ       ║  → GitHub Actions / Jenkins             ║
║  5. ทดสอบ                 ║  → Jest / PyTest / Selenium             ║
║  6. Deploy                ║  → Docker / Kubernetes                  ║
║  7. Monitor               ║  → Grafana / Sentry                     ║
╠═══════════════════════════╬══════════════════════════════════════════╣
║  เปลี่ยนบ่อย: ❌ (Stable) ║  เปลี่ยนบ่อย: ✅ (Tool มาใหม่เรื่อย ๆ)  ║
╠═══════════════════════════╬══════════════════════════════════════════╣
║  📌 สิ่งที่ต้องเข้าใจก่อน ║  📌 เลือกหลังจากเข้าใจ Workflow แล้ว    ║
╚═══════════════════════════╩══════════════════════════════════════════╝

  💡 กฎทอง:
  "เข้าใจ Workflow (ทำไม/ทำอะไร) ก่อน → แล้วค่อยเลือก Tool (ทำด้วยอะไร)"

  ❌ BAD:  "Jenkins ดูเท่ ลอง setup ไว้ก่อน" (Tool-first)
  ✅ GOOD: "ทีมเราต้องการ CI/CD เพราะ Deploy พลาดบ่อย
            → Jenkins เป็นตัวเลือกที่เหมาะกับเรา" (Workflow-first)
```

### 1.3 ทำไม Workflow ที่ดีถึงสำคัญ?

```
  📊 เปรียบเทียบทีมที่มี vs ไม่มี Workflow ชัดเจน

  ┌───────────────────────────┬────────────────────┬───────────────────┐
  │ เกณฑ์                     │ ❌ ไม่มี Workflow   │ ✅ มี Workflow      │
  ├───────────────────────────┼────────────────────┼───────────────────┤
  │ Deploy Frequency          │ 1 ครั้ง/เดือน      │ 3-5 ครั้ง/สัปดาห์ │
  │ Deploy Failure Rate       │ 40%                │ 5%                │
  │ Time to Fix Bug           │ 1-3 วัน            │ 1-4 ชั่วโมง       │
  │ Onboard คนใหม่ (เริ่มส่ง  │ 2-4 สัปดาห์        │ 3-5 วัน           │
  │ งานได้)                   │                    │                   │
  │ ความมั่นใจในการ Deploy     │ 😰 ต่ำมาก          │ 😊 สูง             │
  │ เวลา "มือ" ที่ต้องทำ      │ สูง (ทำเองทุกขั้น) │ ต่ำ (อัตโนมัติ)    │
  └───────────────────────────┴────────────────────┴───────────────────┘

  ─────────────────────────────────────────────────────────────────

  🎯 Workflow ที่ดีช่วยให้:

  ✅ ส่งมอบงานเร็วขึ้น      → "เขียนโค้ดเสร็จ → ผู้ใช้ได้ใช้ภายในชั่วโมง"
  ✅ คุณภาพสูงขึ้น           → "ผ่าน Automated Tests ก่อน Deploy ทุกครั้ง"
  ✅ ลดข้อผิดพลาดจากมนุษย์  → "ไม่ต้อง Copy ไฟล์ขึ้น Server ด้วยมือ"
  ✅ ทำซ้ำได้ทุกครั้ง         → "Deploy ครั้งที่ 100 เหมือนครั้งที่ 1 ทุกประการ"
  ✅ คนใหม่เข้าใจง่าย        → "มีขั้นตอนเป็นลายลักษณ์อักษร ไม่ต้องเดา"
```

---

## 2. Toolchain คืออะไร? <a name="2"></a>

> 💡 **Toolchain** คือ **ชุดเครื่องมือที่เชื่อมต่อกันเป็นสายโซ่** แต่ละเครื่องมือรับผิดชอบขั้นตอนหนึ่ง ๆ ใน Workflow แล้ว **ส่งต่อผลลัพธ์** ให้เครื่องมือถัดไปอัตโนมัติ

### 2.1 คิดเปรียบเหมือน "โรงงานอัตโนมัติ"

```
  🏭 TOOLCHAIN = โรงงานผลิตซอฟต์แวร์อัตโนมัติ

  วัตถุดิบ (Code)
       │
       ▼
  ┌──────────────────────────────────────────────────────────────────┐
  │                         TOOLCHAIN                                │
  │                                                                  │
  │  [IDE]     →    [Git]      →    [CI Server]    →    [Registry]   │
  │  เขียนโค้ด     เก็บ Version     Build + Test       เก็บ Image    │
  │                                                                  │
  │  [Kubernetes]  ←  [Docker]   ←  [Approval]   ←   [QA Tests]     │
  │  จัดการ Deploy    สร้าง Container  อนุมัติ Deploy   ทดสอบคุณภาพ  │
  │                                                                  │
  │  [Monitoring]  →  [Alerting]  →  [Feedback]   →   [Plan Next]   │
  │  ดูแลระบบ        แจ้งเตือน       รับ Feedback      วางแผนต่อ    │
  │                                                                  │
  └──────────────────────────────────────────────────────────────────┘
       │
       ▼
  ผลิตภัณฑ์ (Running Application ที่ผู้ใช้เข้าถึงได้)
```

### 2.2 คุณสมบัติของ Toolchain ที่ดี

```
╔══════════════════════════════════════════════════════════════════════╗
║               ✅ GOOD TOOLCHAIN CHARACTERISTICS                      ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  1️⃣  INTEGRATED — เชื่อมต่อกันอย่างราบรื่น                           ║
║     → เครื่องมือตัวหนึ่งส่งต่อผลลัพธ์ให้ตัวถัดไปอัตโนมัติ             ║
║     → ไม่ต้อง Copy/Paste ข้อมูลระหว่าง Tools                         ║
║     Ex: Git Push → GitHub Actions รัน Test → Slack แจ้งผล           ║
║                                                                      ║
║  2️⃣  AUTOMATED — ลดขั้นตอนที่ต้องทำด้วยมือ                          ║
║     → Build, Test, Deploy เกิดขึ้นอัตโนมัติ                          ║
║     → มนุษย์ตัดสินใจ Machine ทำงาน                                   ║
║     Ex: Merge PR → Auto-build → Auto-test → Auto-deploy (Staging)  ║
║                                                                      ║
║  3️⃣  OBSERVABLE — มองเห็นทุกขั้นตอน                                  ║
║     → Dashboard แสดง Pipeline สถานะ Real-time                       ║
║     → Log ทุกอย่างดู Audit ย้อนหลังได้                               ║
║     Ex: Grafana Dashboard แสดง Build Time, Test Coverage, Uptime    ║
║                                                                      ║
║  4️⃣  REPLACEABLE — เปลี่ยน Tool ได้โดยไม่กระทบ Workflow               ║
║     → ถ้า Jenkins → GitHub Actions ได้โดยขั้นตอนงานเหมือนเดิม        ║
║     → เพราะเรายึดหลักการ Workflow ไม่ได้ยึดติดกับ Tool                 ║
║     Ex: เปลี่ยน Datadog → Prometheus+Grafana (ทั้งคู่คือ Monitoring) ║
║                                                                      ║
║  5️⃣  SCALABLE — โตตามทีมได้                                          ║
║     → ทีม 3 คน → 30 คน → Toolchain ยังรองรับ                        ║
║     → เพิ่ม Tool ใหม่ได้โดยไม่ทำลาย Tool เดิม                       ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
```

---

## 3. Modern Development Workflow — End-to-End <a name="3"></a>

> 💡 Workflow สมัยใหม่เป็น **วงรอบ (Loop)** ไม่ใช่เส้นตรง — ข้อมูลจากขั้นตอนท้าย (Monitor) ย้อนกลับไปปรับปรุง Plan ของรอบถัดไป

### 3.1 The 5-Phase Development Loop

```
══════════════════════════════════════════════════════════════════
              🔄 MODERN DEVELOPMENT WORKFLOW LOOP
══════════════════════════════════════════════════════════════════

                    ┌──────────────────────┐
                    │   1. PLAN & DESIGN   │
                    │   วางแผนและออกแบบ     │
                    └──────────┬───────────┘
                               │
                               ▼
   ┌──────────────────┐                    ┌───────────────────┐
   │  5. MONITOR &    │                    │   2. CODE & BUILD │
   │     FEEDBACK     │                    │   เขียนและ Build   │
   │  ติดตามและรับ     │                    │   โค้ด             │
   │  Feedback        │                    └─────────┬─────────┘
   └────────┬─────────┘                              │
            │                                        ▼
            │                              ┌───────────────────┐
            │                              │  3. TEST & QA     │
   ┌────────┴─────────┐                   │  ทดสอบคุณภาพ      │
   │  4. DEPLOY &     │◄──────────────────┘                   │
   │     RELEASE      │                                        │
   │  ส่งมอบ          │                                        │
   └──────────────────┘                                        │

══════════════════════════════════════════════════════════════════
  🔁 รอบนี้เกิดซ้ำทุก Sprint (1-2 สัปดาห์) หรือทุกครั้งที่ Push
══════════════════════════════════════════════════════════════════
```

### 3.2 แต่ละ Phase มี Tools อะไรบ้าง — Complete Map

```
══════════════════════════════════════════════════════════════════
       📦 COMPLETE WORKFLOW-TOOLCHAIN MAP
══════════════════════════════════════════════════════════════════

  PHASE 1: PLAN & DESIGN
  ─────────────────────────────────────────────────────────
  ┌────────────┬─────────────┬─────────────┬─────────────┐
  │ 📋 Task    │ 📝 Docs     │ 🎨 Design   │ 📐 Diagram  │
  │ Tracking   │             │             │             │
  │ Jira       │ Confluence  │ Figma       │ Draw.io     │
  │ Trello     │ Notion      │ Zeplin      │ Lucidchart  │
  │ Linear     │ Google Docs │ Adobe XD    │ Miro        │
  └────────────┴─────────────┴─────────────┴─────────────┘

  PHASE 2: CODE & BUILD
  ─────────────────────────────────────────────────────────
  ┌────────────┬─────────────┬─────────────┬─────────────┐
  │ 💻 Editor  │ 🔀 Version  │ 📦 Package  │ 🏗️ Build    │
  │            │  Control    │  Manager    │             │
  │ VS Code    │ Git         │ npm / yarn  │ Webpack     │
  │ IntelliJ   │ GitHub      │ pip / poetry│ Vite        │
  │ Cursor     │ GitLab      │ Maven       │ Gradle      │
  └────────────┴─────────────┴─────────────┴─────────────┘

  PHASE 3: TEST & QA
  ─────────────────────────────────────────────────────────
  ┌────────────┬─────────────┬─────────────┬─────────────┐
  │ 🧪 Unit    │ 🔗 Integra- │ 🖥️ E2E     │ 📊 Quality  │
  │  Test      │   tion Test │  Test       │  Analysis   │
  │ Jest       │ Postman     │ Cypress     │ SonarQube   │
  │ PyTest     │ Newman      │ Playwright  │ ESLint      │
  │ JUnit      │ SuperTest   │ Selenium    │ CodeClimate │
  └────────────┴─────────────┴─────────────┴─────────────┘

  PHASE 4: DEPLOY & RELEASE
  ─────────────────────────────────────────────────────────
  ┌────────────┬─────────────┬─────────────┬─────────────┐
  │ 🔄 CI/CD   │ 🐳 Container│ ☸️ Orchestr. │ 🏗️ IaC      │
  │            │             │             │             │
  │ GitHub     │ Docker      │ Kubernetes  │ Terraform   │
  │  Actions   │ Podman      │ Docker Swarm│ Ansible     │
  │ Jenkins    │             │ Helm        │ Pulumi      │
  └────────────┴─────────────┴─────────────┴─────────────┘

  PHASE 5: MONITOR & FEEDBACK
  ─────────────────────────────────────────────────────────
  ┌────────────┬─────────────┬─────────────┬─────────────┐
  │ 📈 Metrics │ 📋 Logs     │ 🔴 Error    │ 🔔 Alerting │
  │            │             │  Tracking   │             │
  │ Prometheus │ ELK Stack   │ Sentry      │ PagerDuty   │
  │ Grafana    │ Loki        │ Rollbar     │ Opsgenie    │
  │ Datadog    │ Papertrail  │ Bugsnag     │ Slack Alerts│
  └────────────┴─────────────┴─────────────┴─────────────┘

══════════════════════════════════════════════════════════════════
```

---

## 4. Phase 1: Plan & Design <a name="4"></a>

> 💡 ทุกอย่างเริ่มจาก **"ทำไม"** และ **"ทำอะไร"** ก่อน **"ทำยังไง"** — Phase นี้กำหนดทิศทางให้ทั้ง Sprint

### 4.1 Workflow ของ Phase Plan & Design

```
  📋 PLAN & DESIGN WORKFLOW

  ┌─────────────────────────────────────────────────────────────┐
  │                                                             │
  │   Idea / Request / Bug Report                               │
  │        │                                                    │
  │        ▼                                                    │
  │   ┌──────────────┐                                          │
  │   │ Triage &     │  ← PO ตัดสินใจว่างานนี้สำคัญพอไหม       │
  │   │ Prioritize   │    ถ้าไม่สำคัญ → Archive                  │
  │   └──────┬───────┘                                          │
  │          │                                                  │
  │          ▼                                                  │
  │   ┌──────────────┐                                          │
  │   │ Write User   │  ← เขียนในรูปแบบ As a..., I want...     │
  │   │ Story / Spec │    + Acceptance Criteria ที่ Testable    │
  │   └──────┬───────┘                                          │
  │          │                                                  │
  │          ▼                                                  │
  │   ┌──────────────┐                                          │
  │   │ Design &     │  ← UI Mockup (Figma), Architecture      │
  │   │ Estimation   │    Diagram (Draw.io), Story Points       │
  │   └──────┬───────┘                                          │
  │          │                                                  │
  │          ▼                                                  │
  │   ┌──────────────┐                                          │
  │   │ Sprint       │  ← เลือกงานเข้า Sprint ตาม Velocity     │
  │   │ Planning     │    กำหนด Sprint Goal                     │
  │   └──────────────┘                                          │
  │                                                             │
  └─────────────────────────────────────────────────────────────┘

  Tools ที่ใช้ใน Phase นี้:
  ┌─────────────────────────────────────────────────────────────┐
  │  Jira / Trello  → Track Items, Sprint Planning              │
  │  Figma          → UI/UX Design, Prototype                  │
  │  Miro / FigJam  → Brainstorm, Architecture Discussion      │
  │  Confluence      → Technical Spec, Decision Log             │
  │  Draw.io        → System Architecture Diagram              │
  └─────────────────────────────────────────────────────────────┘
```

### 4.2 Output ของ Phase 1

```
  📤 สิ่งที่ได้จาก Phase 1 (Input ให้ Phase 2):

  ┌───────────────────────────────────────────────────────────┐
  │  ✅ Sprint Goal ที่ชัดเจน 1 ประโยค                        │
  │  ✅ Sprint Backlog พร้อม User Stories ที่ Estimate แล้ว   │
  │  ✅ Acceptance Criteria สำหรับทุก Story                    │
  │  ✅ UI Mockup / Wireframe (ถ้าเป็น Frontend Task)         │
  │  ✅ Technical Spec / API Design (ถ้าเป็น Backend Task)    │
  │  ✅ Architecture Diagram (ถ้า Feature ใหม่ทั้งหมด)        │
  └───────────────────────────────────────────────────────────┘
```

---

## 5. Phase 2: Code & Build <a name="5"></a>

> 💡 Phase นี้คือหัวใจของ Development — เป็นจุดที่ Idea กลายเป็น Code ที่ทำงานได้จริง

### 5.1 Workflow ของ Phase Code & Build

```
  💻 CODE & BUILD WORKFLOW — Step by Step

  ┌─────────────────────────────────────────────────────────────────┐
  │                                                                 │
  │  Step 1: เริ่มงาน                                               │
  │  ────────────────────────────────────────────                  │
  │  Jira Issue "To Do" → "In Progress"                             │
  │  git checkout -b feature/PROJ-142-login-page                   │
  │  → สร้าง Branch ใหม่จาก main                                   │
  │                                                                 │
  │  Step 2: เขียนโค้ด                                              │
  │  ────────────────────────────────────────────                  │
  │  IDE (VS Code / IntelliJ)                                      │
  │  → เขียน Code + Unit Tests พร้อมกัน (TDD)                     │
  │  → ใช้ Linter (ESLint, Pylint) ตรวจ Code Style                │
  │                                                                 │
  │  Step 3: Commit & Push                                         │
  │  ────────────────────────────────────────────                  │
  │  git add .                                                      │
  │  git commit -m "PROJ-142 feat: add login page component"       │
  │  git push origin feature/PROJ-142-login-page                   │
  │  → Smart Commit Link กับ Jira Issue อัตโนมัติ                  │
  │                                                                 │
  │  Step 4: Pull Request                                          │
  │  ────────────────────────────────────────────                  │
  │  สร้าง Pull Request บน GitHub                                   │
  │  → Assign Reviewers                                            │
  │  → CI Pipeline เริ่มทำงานอัตโนมัติ (Build + Test)              │
  │  → Jira Issue ย้ายสถานะ → "Code Review"                        │
  │                                                                 │
  │  Step 5: Code Review                                           │
  │  ────────────────────────────────────────────                  │
  │  เพื่อนร่วมทีม Review Code บน GitHub PR                        │
  │  → Approve ✅ หรือ Request Changes ⚠️                          │
  │  → แก้ตาม Feedback → Push Again → Re-review                   │
  │                                                                 │
  │  Step 6: Merge                                                 │
  │  ────────────────────────────────────────────                  │
  │  PR Approved + CI Pass → Merge เข้า main Branch               │
  │  → Feature Branch ถูกลบ                                        │
  │  → CI/CD Pipeline เริ่มทำงานสำหรับ main                        │
  │                                                                 │
  └─────────────────────────────────────────────────────────────────┘
```

### 5.2 Git Flow ที่ใช้ใน Workflow

```
  🌿 BRANCHING STRATEGY — Feature Branch Workflow

  main ───●────────────────────●──────────────────────●────────►
          │                    ▲                      ▲
          │         Merge PR   │           Merge PR   │
          │                    │                      │
          └─── feature/login ──┘                      │
                    │                                 │
                    └────── feature/register ──────────┘

  กฎ:
  ─────────────────────────────────────────────────────────────────
  ✅ ทุก Feature สร้าง Branch จาก main
  ✅ ตั้งชื่อ: feature/[JIRA-KEY]-[short-description]
  ✅ PR ต้องผ่าน CI + Review ก่อน Merge
  ✅ main ต้อง Deployable ได้ตลอดเวลา
  ✅ ลบ Feature Branch หลัง Merge
  ❌ ห้าม Commit ตรงเข้า main โดยไม่ผ่าน PR
```

### 5.3 Conventional Commits — มาตรฐานข้อความ Commit

```
  📝 COMMIT MESSAGE FORMAT

  ┌─────────────────────────────────────────────────────────────┐
  │  [type](scope): [short description]                         │
  │                                                             │
  │  [optional body]                                            │
  │  [optional footer: JIRA-KEY, Breaking Changes]              │
  └─────────────────────────────────────────────────────────────┘

  Types ที่ใช้บ่อย:
  ┌──────────┬──────────────────────────────────────────────────┐
  │  Type    │  ใช้เมื่อ                                        │
  ├──────────┼──────────────────────────────────────────────────┤
  │  feat    │  เพิ่ม Feature ใหม่                               │
  │  fix     │  แก้ Bug                                         │
  │  docs    │  เปลี่ยนแปลง Documentation                       │
  │  style   │  Format, Spacing (ไม่กระทบ Logic)               │
  │  refactor│  Refactor Code (ไม่เปลี่ยน Behavior)            │
  │  test    │  เพิ่มหรือแก้ Tests                               │
  │  chore   │  งาน Maintenance (Config, Dependencies)         │
  │  ci      │  แก้ CI/CD Pipeline                              │
  └──────────┴──────────────────────────────────────────────────┘

  ตัวอย่าง:
  ─────────────────────────────────────────────────────────────
  ✅ feat(auth): add Google OAuth login button
  ✅ fix(cart): resolve price calculation overflow on large qty
  ✅ test(auth): add unit tests for JWT token validation
  ✅ chore: update Node.js from v18 to v20 LTS
  ❌ fixed stuff (ไม่รู้ว่าแก้อะไร)
  ❌ WIP (ไม่ควร Commit ของที่ยังไม่เสร็จ)
```

---

## 6. Phase 3: Test & Quality Assurance <a name="6"></a>

> 💡 การทดสอบไม่ใช่แค่ "ลองดูว่าพังไหม" แต่คือ **การสร้างหลักฐานว่าซอฟต์แวร์ทำงานถูกต้อง** ทุกครั้งที่มีการเปลี่ยนแปลง

### 6.1 Testing ใน Workflow

```
  🧪 TESTING IN WORKFLOW — เกิดขึ้นหลายจุด

  Developer Push Code
       │
       ▼
  ┌──────────────────────────────────────────────────────────────┐
  │  PRE-COMMIT (ก่อน Commit — Developer เครื่องของตัวเอง)       │
  │  ─────────────────────────────────────────────────────      │
  │  → Linter ตรวจ Code Style (ESLint, Pylint)                  │
  │  → Format ด้วย Prettier                                     │
  │  → Pre-commit Hook: ป้องกัน Commit ที่ไม่ผ่าน Lint           │
  └──────────────────────────┬───────────────────────────────────┘
                             │ git push
                             ▼
  ┌──────────────────────────────────────────────────────────────┐
  │  CI PIPELINE (อัตโนมัติ — ทุก Push/PR)                       │
  │  ─────────────────────────────────────────────────────      │
  │  Stage 1: 🧱 Build                                          │
  │           → Compile / Install Dependencies                  │
  │           → ถ้า Build Fail → หยุดทันที ❌                    │
  │                                                              │
  │  Stage 2: 🧪 Unit Tests                                      │
  │           → Jest, PyTest, JUnit (เร็วมาก, < 2 นาที)        │
  │           → Coverage Report → ต้อง > 80%                    │
  │                                                              │
  │  Stage 3: 🔗 Integration Tests                               │
  │           → API Tests ด้วย Postman/Newman                   │
  │           → Database Migration Tests                        │
  │                                                              │
  │  Stage 4: 📊 Static Analysis                                 │
  │           → SonarQube ตรวจ Code Quality Score               │
  │           → Security Scan (Dependabot, Snyk)                │
  └──────────────────────────┬───────────────────────────────────┘
                             │ All Pass ✅
                             ▼
  ┌──────────────────────────────────────────────────────────────┐
  │  POST-MERGE / STAGING (หลัง Merge → ทดสอบบน Staging)         │
  │  ─────────────────────────────────────────────────────      │
  │  → E2E Tests (Cypress, Playwright)                           │
  │  → Performance Tests (k6)                                    │
  │  → Manual QA (สำหรับ Visual/UX ที่ Automate ยาก)             │
  └──────────────────────────────────────────────────────────────┘

  💡 หลักการ: ทดสอบที่ถูก/เร็วก่อน ทดสอบที่แพง/ช้าทีหลัง
              Unit (เร็ว ถูก มาก) → Integration → E2E (ช้า แพง น้อย)
```

### 6.2 Quality Gates — ด่านตรวจคุณภาพ

```
  🚦 QUALITY GATES — ต้องผ่านทุกด่านก่อน Deploy

  ┌───────────────────┬────────────────────────┬────────────────┐
  │  Gate             │  เกณฑ์ที่ต้องผ่าน       │  ใครรับผิดชอบ  │
  ├───────────────────┼────────────────────────┼────────────────┤
  │  🟢 Gate 1:       │  Lint Pass, Build OK   │  Automated     │
  │  Build & Lint     │  ไม่มี Compile Error    │  (CI)          │
  ├───────────────────┼────────────────────────┼────────────────┤
  │  🟢 Gate 2:       │  Unit Test > 80%       │  Automated     │
  │  Unit Tests       │  Coverage, 0 Fails     │  (CI)          │
  ├───────────────────┼────────────────────────┼────────────────┤
  │  🟢 Gate 3:       │  1+ Approval จาก       │  Team Member   │
  │  Code Review      │  Reviewer, ทุก Comment │  (Manual)      │
  │                   │  Resolved              │                │
  ├───────────────────┼────────────────────────┼────────────────┤
  │  🟢 Gate 4:       │  E2E Tests Pass,       │  Automated +   │
  │  Staging QA       │  QA Manual Sign-off    │  QA Engineer   │
  ├───────────────────┼────────────────────────┼────────────────┤
  │  🟢 Gate 5:       │  No Critical/High      │  Team Lead /   │
  │  Release Approval │  Bugs Open, PO Accept  │  PO            │
  └───────────────────┴────────────────────────┴────────────────┘

  ❌ ถ้า Gate ไหนไม่ผ่าน → หยุดทันที → แก้ไข → ผ่าน Gate ใหม่
  ✅ ผ่านทุก Gate → พร้อม Deploy สู่ Production
```

---

## 7. Phase 4: Deploy & Release <a name="7"></a>

> 💡 Deploy คือการทำให้ Code ที่เขียนเสร็จ **ไปถึงมือผู้ใช้จริง** — เป้าหมายคือทำให้กระบวนการนี้ **เร็ว, ปลอดภัย, และย้อนกลับได้** ถ้ามีปัญหา

### 7.1 Deployment Pipeline

```
  🚀 DEPLOYMENT PIPELINE — จาก Merge สู่ Production

  git merge feature/login → main
       │
       ▼
  ┌──────────────────────────────────────────────────────────────┐
  │  Stage 1: BUILD                                              │
  │  ─────────────────────────────                              │
  │  docker build -t myapp:v2.1.0 .                             │
  │  → สร้าง Docker Image เพียงครั้งเดียว                        │
  │  → Image เดียวกันนี้ใช้ทุก Environment                       │
  └──────────────────────────┬───────────────────────────────────┘
                             │
                             ▼
  ┌──────────────────────────────────────────────────────────────┐
  │  Stage 2: PUSH TO REGISTRY                                   │
  │  ─────────────────────────────                              │
  │  docker push registry.example.com/myapp:v2.1.0              │
  │  → เก็บ Image ไว้ใน Container Registry                      │
  └──────────────────────────┬───────────────────────────────────┘
                             │
                             ▼
  ┌──────────────────────────────────────────────────────────────┐
  │  Stage 3: DEPLOY TO STAGING                                  │
  │  ─────────────────────────────                              │
  │  kubectl apply -f staging/deployment.yaml                   │
  │  → Deploy Image เดียวกันบน Staging Environment              │
  │  → รัน E2E Tests + Smoke Tests                              │
  │  → QA ทดสอบ Manual (ถ้าจำเป็น)                              │
  └──────────────────────────┬───────────────────────────────────┘
                             │ ✅ Staging Pass
                             ▼
  ┌──────────────────────────────────────────────────────────────┐
  │  Stage 4: DEPLOY TO PRODUCTION                               │
  │  ─────────────────────────────                              │
  │  Strategy: Rolling Update (ค่อย ๆ เปลี่ยน ไม่มี Downtime)   │
  │                                                              │
  │  Old Pods [v2.0] ████████████                                │
  │  New Pods [v2.1] ░░░░░░░░░░░░                               │
  │                    ▼                                         │
  │  Old Pods [v2.0] ████████░░░░                                │
  │  New Pods [v2.1] ░░░░████████                               │
  │                    ▼                                         │
  │  Old Pods [v2.0] ░░░░░░░░░░░░  (Terminated)                 │
  │  New Pods [v2.1] ████████████  ✅ 100% Traffic               │
  │                                                              │
  │  ⚠️ ถ้า Health Check Fail → Auto-rollback ทันที              │
  └──────────────────────────┬───────────────────────────────────┘
                             │
                             ▼
  ┌──────────────────────────────────────────────────────────────┐
  │  Stage 5: POST-DEPLOY VERIFICATION                           │
  │  ─────────────────────────────                              │
  │  → Smoke Test บน Production (API Health Check)              │
  │  → ดู Error Rate ใน Sentry (ต้องไม่สูงกว่าปกติ)             │
  │  → ดู Response Time ใน Grafana (ต้องไม่ช้าลง)              │
  │  → แจ้ง Slack: "🚀 v2.1.0 deployed successfully"           │
  └──────────────────────────────────────────────────────────────┘
```

### 7.2 Deployment Strategies เปรียบเทียบ

```
  📊 DEPLOYMENT STRATEGIES — เลือกให้เหมาะกับ Risk

  ┌──────────────────┬───────────────────────┬─────────────────────┐
  │  Strategy        │  วิธีการ               │  เหมาะกับ           │
  ├──────────────────┼───────────────────────┼─────────────────────┤
  │  Rolling Update  │  ค่อย ๆ เปลี่ยน Pod   │  ส่วนใหญ่ (Default) │
  │                  │  ทีละกลุ่ม             │  Risk ต่ำ-กลาง      │
  ├──────────────────┼───────────────────────┼─────────────────────┤
  │  Blue/Green      │  สร้าง Environment ใหม่│  ต้องการ Zero       │
  │                  │  แล้วสลับ Traffic      │  Downtime 100%      │
  ├──────────────────┼───────────────────────┼─────────────────────┤
  │  Canary          │  ส่ง Traffic 5% ไปที่  │  Feature ที่ Risk   │
  │                  │  Version ใหม่ก่อน      │  สูง ต้อง Test จริง │
  ├──────────────────┼───────────────────────┼─────────────────────┤
  │  Recreate        │  ปิด Old → เปิด New   │  Dev/Staging         │
  │                  │  (มี Downtime)        │  ที่ Downtime OK    │
  └──────────────────┴───────────────────────┴─────────────────────┘
```

---

## 8. Phase 5: Monitor & Feedback <a name="8"></a>

> 💡 Deploy เสร็จ ≠ จบงาน — ต้อง Monitor ว่าระบบทำงานได้ดีในสภาพจริง และ Feedback ต้องย้อนกลับไปปรับปรุง Plan ในรอบถัดไป

### 8.1 Monitoring Workflow

```
  📊 MONITOR & FEEDBACK WORKFLOW

  Production System Running
       │
       ├──────────────────────────────────────────────────────────┐
       │                                                          │
       ▼                                                          ▼
  ┌──────────────────────┐                    ┌──────────────────────┐
  │  📈 METRICS           │                    │  🔴 ERROR TRACKING    │
  │  (Prometheus/Grafana) │                    │  (Sentry)            │
  │                       │                    │                      │
  │  CPU: 35% ✅          │                    │  New Error Detected! │
  │  Memory: 2.1GB ✅     │                    │  TypeError at line 42│
  │  Req/sec: 1,200 ✅    │                    │  Users Affected: 847 │
  │  Resp Time: 120ms ✅  │                    │  Stack Trace: ...    │
  └───────────┬───────────┘                    └──────────┬───────────┘
              │                                            │
              │    ⚠️ Alert Triggered:                      │
              │    CPU > 80% or Error Rate > 1%            │
              │                                            │
              └─────────────────┬──────────────────────────┘
                                │
                                ▼
                    ┌──────────────────────┐
                    │  🔔 ALERTING          │
                    │  (PagerDuty / Slack)  │
                    └──────────┬───────────┘
                               │
                ┌──────────────┼──────────────┐
                ▼              ▼              ▼
           📧 Email       💬 Slack       📱 PagerDuty
           Summary       Instant        Wake On-call
                         Alert          Engineer
                               │
                               ▼
                    ┌──────────────────────┐
                    │  🔧 RESPOND & FIX     │
                    │  → Hotfix Branch       │
                    │  → Fast Track PR       │
                    │  → Deploy Hotfix       │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │  📋 FEEDBACK TO PLAN   │
                    │  → สร้าง Bug Issue     │
                    │  → เพิ่มใน Backlog      │
                    │  → ปรับปรุง Monitoring   │
                    │  → Retrospective       │
                    └──────────────────────┘

  💡 Feedback Loop ทำให้ Workflow เป็นวงกลม ไม่ใช่เส้นตรง
```

### 8.2 Feedback ย้อนกลับสู่ Phase 1

```
  🔄 FEEDBACK LOOP — ข้อมูลจาก Production ปรับปรุง Plan

  ┌──────────────────────────────────────────────────────────────┐
  │  ข้อมูลจาก Monitoring                                        │
  │  ─────────────────────────────────────────────────────      │
  │  📊 "Response Time เพิ่มขึ้น 40% หลัง Deploy v2.1"          │
  │  🔴 "Error Rate สูงขึ้น 0.3% จาก Safari Users"              │
  │  💬 "Users ร้องเรียนว่า Checkout ช้า"                        │
  │  📈 "API /search ถูกเรียก 10x มากกว่าที่คาด"                │
  └──────────────────────────┬───────────────────────────────────┘
                             │
                             ▼
  ┌──────────────────────────────────────────────────────────────┐
  │  Action Items ใน Sprint ถัดไป                                │
  │  ─────────────────────────────────────────────────────      │
  │  🐛 BUG: แก้ Performance Regression จาก v2.1                │
  │  🐛 BUG: Safari Cookie Issue (จาก Sentry Data)              │
  │  📖 STORY: Optimize Checkout Flow (จาก User Feedback)       │
  │  ✅ TASK: Add Caching for /search API (จาก Metrics)         │
  │  ✅ TASK: Add Alert สำหรับ Checkout Response Time > 2s       │
  └──────────────────────────────────────────────────────────────┘

  → ข้อมูลจริงจาก Production ทำให้ Backlog มีคุณค่ามากขึ้น
  → ไม่ต้อง "เดา" ว่าจะทำอะไร → ดูจาก Data
```

---

## 9. Workflow Automation — ทำให้ทุกอย่างอัตโนมัติ <a name="9"></a>

> 💡 **Automation** คือสิ่งที่ทำให้ Workflow ทำงานได้ **เร็ว, สม่ำเสมอ, ไม่มีข้อผิดพลาดจากมนุษย์** — ทุกขั้นตอนที่ทำซ้ำ ๆ ควร Automate

### 9.1 What to Automate vs What Not to Automate

```
╔══════════════════════════════════════════════════════════════════════╗
║              🤖 AUTOMATION DECISION MATRIX                           ║
╠═══════════════════════════════════╦══════════════════════════════════╣
║  ✅ AUTOMATE (ทำซ้ำ เหมือนเดิม)   ║  🧠 HUMAN (ตัดสินใจ สร้างสรรค์) ║
╠═══════════════════════════════════╬══════════════════════════════════╣
║  Build (Compile, Bundle)          ║  Code Review (Logic, Design)     ║
║  Run Tests (Unit, E2E)            ║  Architecture Decision           ║
║  Lint & Format Check              ║  Feature Prioritization          ║
║  Deploy to Environment            ║  Bug Triage (P0 vs P3)           ║
║  Send Notifications               ║  UX/UI Design Review             ║
║  Generate Reports                 ║  Sprint Planning                 ║
║  Security Scan                    ║  Incident Response Decision      ║
║  Rollback on Failure              ║  Customer Communication          ║
╚═══════════════════════════════════╩══════════════════════════════════╝

  💡 กฎ: "ถ้าเขียนเป็น Script ได้ → Automate"
         "ถ้าต้องคิด ตัดสินใจ สร้างสรรค์ → มนุษย์ทำ"
```

### 9.2 CI/CD Pipeline ตัวอย่าง (GitHub Actions)

```yaml
# .github/workflows/full-pipeline.yml
# ตัวอย่าง Full CI/CD Pipeline ครบ Workflow

name: "Full Development Pipeline"

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  # ─── STAGE 1: BUILD & LINT ───────────────────────────────
  build:
    name: "🏗️ Build & Lint"
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: npm ci                    # Install Dependencies
      - run: npm run lint              # ESLint Check
      - run: npm run build             # Build Application

  # ─── STAGE 2: UNIT TESTS ────────────────────────────────
  test:
    name: "🧪 Unit Tests"
    needs: build                       # รันหลัง Build สำเร็จ
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npm test -- --coverage    # Run Tests + Coverage
      - name: "📊 Upload Coverage"
        uses: codecov/codecov-action@v3

  # ─── STAGE 3: SECURITY SCAN ─────────────────────────────
  security:
    name: "🔒 Security Scan"
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: "Run Snyk Security Scan"
        uses: snyk/actions/node@master

  # ─── STAGE 4: DEPLOY TO STAGING ─────────────────────────
  deploy-staging:
    name: "🚀 Deploy Staging"
    needs: [test, security]            # ต้องผ่านทั้ง Test + Security
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - name: "🐳 Build Docker Image"
        run: docker build -t myapp:${{ github.sha }} .
      - name: "☸️ Deploy to Staging"
        run: kubectl apply -f k8s/staging/

  # ─── STAGE 5: E2E TESTS ON STAGING ──────────────────────
  e2e-test:
    name: "🖥️ E2E Tests"
    needs: deploy-staging
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: "Run Cypress E2E"
        run: npx cypress run --config baseUrl=https://staging.myapp.com

  # ─── STAGE 6: DEPLOY TO PRODUCTION ──────────────────────
  deploy-production:
    name: "🚀 Deploy Production"
    needs: e2e-test
    if: github.ref == 'refs/heads/main'
    environment: production            # Requires Manual Approval
    runs-on: ubuntu-latest
    steps:
      - name: "☸️ Deploy to Production"
        run: kubectl apply -f k8s/production/
      - name: "💬 Notify Slack"
        run: |
          curl -X POST $SLACK_WEBHOOK \
          -d '{"text":"🚀 v${{ github.sha }} deployed to Production!"}'
```

```
  Pipeline Visualization:

  Push to main
       │
       ▼
  [🏗️ Build & Lint] ─────┐
       │ Pass ✅          │
       ▼                  ▼
  [🧪 Unit Tests]    [🔒 Security]
       │ Pass ✅          │ Pass ✅
       └────────┬─────────┘
                │
                ▼
       [🚀 Deploy Staging]
                │
                ▼
       [🖥️ E2E Tests on Staging]
                │ Pass ✅
                ▼
       [⏸️ Manual Approval Required]
                │ Approved ✅
                ▼
       [🚀 Deploy Production]
                │
                ▼
       [💬 Slack: "Deployed! 🎉"]
```

---

## 10. Toolchain Archetypes — ตัวอย่าง Toolchain ตามขนาดทีม <a name="10"></a>

### 10.1 Solo Developer / Side Project (1 คน)

```
══════════════════════════════════════════════════════════════════
  🧑‍💻 SOLO DEVELOPER TOOLCHAIN — เน้นง่ายและฟรี

  PLAN          CODE           VERSION        CI/CD
  ──────────    ──────────     ──────────     ──────────
  Notion        VS Code        GitHub         GitHub
  (Todo List)   (Editor)       (Free)         Actions
                                              (Free Tier)

  TEST          DEPLOY         MONITOR
  ──────────    ──────────     ──────────
  Jest/PyTest   Vercel หรือ    Sentry
  (Basic)       Railway        (Free Tier)
                (PaaS ฟรี)     + UptimeRobot

  💰 ต้นทุน: $0/เดือน
  ⏱️ Setup: 1-2 ชั่วโมง
  ✅ ดี: เริ่มต้นเร็ว, ฟรี 100%
  ⚠️ จำกัด: Scale ยาก, ไม่มี Code Review Process
══════════════════════════════════════════════════════════════════
```

### 10.2 Small Startup (3-8 คน)

```
══════════════════════════════════════════════════════════════════
  🚀 STARTUP TOOLCHAIN — เน้นความเร็วและต้นทุนต่ำ

  PLAN             CODE             VERSION          CI/CD
  ─────────────    ─────────────    ─────────────    ───────────
  Trello           VS Code          GitHub           GitHub
  (Kanban Board)   + Cursor AI      (Free)           Actions
  + Notion (Docs)                                    (Free Tier)

  TEST             DEPLOY           MONITOR          COMMUNICATE
  ─────────────    ─────────────    ─────────────    ───────────
  Jest + PyTest    Docker +         Sentry (Free)    Slack
  Postman          Railway/Render   + UptimeRobot    (Free)
  (Manual API)     (PaaS)           + Grafana Cloud

  💰 ต้นทุน: $0-50/เดือน
  ⏱️ Setup: 1-2 วัน
  ✅ ดี: ต้นทุนต่ำ, เรียนรู้ง่าย, ทำงานเร็ว
  ⚠️ จำกัด: ไม่มี Sprint Report ที่ดี, Scale ยากเมื่อโตเกิน 10 คน
══════════════════════════════════════════════════════════════════
```

### 10.3 Mid-size Company (10-50 คน)

```
══════════════════════════════════════════════════════════════════
  🏢 MID-SIZE TOOLCHAIN — Balance ระหว่าง Speed & Control

  PLAN                CODE               VERSION CONTROL
  ─────────────────   ─────────────      ──────────────────
  Jira Software       VS Code /          GitHub / GitLab
  + Confluence        IntelliJ           (Protected Branches,
  (Sprint + Docs)     + Team Linters     PR Reviews Required)

  CI/CD               TEST               DEPLOY
  ─────────────────   ─────────────      ──────────────────
  GitHub Actions      Jest / PyTest      Docker +
  + SonarQube         + Cypress (E2E)    Kubernetes
  (Code Quality)      + Postman (API)    + Helm Charts
                      + k6 (Performance) + Terraform (IaC)

  MONITOR                                COMMUNICATE
  ─────────────────                      ──────────────────
  Prometheus +                           Slack
  Grafana +                              + Figma (Design)
  Sentry +                               + Miro (Whiteboard)
  PagerDuty (On-call)

  💰 ต้นทุน: $500-2,000/เดือน
  ⏱️ Setup: 1-2 สัปดาห์
  ✅ ดี: ครบ, Scale ได้, Reports ดี, มาตรฐานสูง
  ⚠️ จำกัด: ต้นทุนสูง, ต้องมีคนดูแล Infrastructure
══════════════════════════════════════════════════════════════════
```

### 10.4 เปรียบเทียบ Quick Reference

```
┌───────────────────┬───────────────┬───────────────┬───────────────┐
│                   │  Solo (1 คน)  │ Startup (3-8) │ Mid-size (10+)│
├───────────────────┼───────────────┼───────────────┼───────────────┤
│  Planning         │  Notion       │  Trello       │  Jira         │
│  Code Editor      │  VS Code      │  VS Code      │  VS Code/IDEA │
│  Version Control  │  GitHub       │  GitHub       │  GitHub/GitLab│
│  CI/CD            │  GH Actions   │  GH Actions   │  GH Actions + │
│                   │               │               │  SonarQube    │
│  Testing          │  Jest/PyTest  │  Jest+Postman │  Jest+Cypress │
│                   │               │               │  +k6+Postman  │
│  Deploy           │  Vercel/PaaS  │  Docker+PaaS  │  Docker+K8s   │
│  Monitoring       │  Sentry       │  Sentry       │  Full Stack   │
│  Cost/month       │  $0           │  $0-50        │  $500-2,000   │
└───────────────────┴───────────────┴───────────────┴───────────────┘
```

---

## 11. How Tools Connect — Integration Patterns <a name="11"></a>

> 💡 เครื่องมือแต่ละตัวทรงพลัง แต่ **พลังที่แท้จริง** มาจากการเชื่อมต่อเครื่องมือเข้าด้วยกัน ให้ข้อมูลไหลอัตโนมัติ

### 11.1 Integration Flow — ภาพรวม End-to-End

```
  🔗 HOW EVERYTHING CONNECTS

  ┌────────────────────────────────────────────────────────────────┐
  │                                                                │
  │  👨‍💻 Developer                        👥 Team                  │
  │  ──────────                          ──────                    │
  │  VS Code / IntelliJ          ←───── GitHub (PR Review)        │
  │       │ Code                          │ Approved ✅            │
  │       │                               │                        │
  │       ▼ git push                      ▼                        │
  │  ──────────────────────────────────────────────────────────── │
  │                 🤖 AUTOMATION (CI/CD)                          │
  │  ──────────────────────────────────────────────────────────── │
  │                          │                                     │
  │              GitHub Actions Triggered                          │
  │                          │                                     │
  │          ┌───────────────┼────────────────┐                   │
  │          ▼               ▼                ▼                   │
  │     Install Deps    Run Tests        Code Quality             │
  │     (npm/pip)      (Jest/PyTest)     (SonarQube)              │
  │          │               │                │                   │
  │          └───────────────┼────────────────┘                   │
  │                          │ All Pass ✅                         │
  │                          ▼                                     │
  │                    Docker Build                                │
  │                          │                                     │
  │                          ▼                                     │
  │              Deploy to Kubernetes                              │
  │                          │                                     │
  │  ──────────────────────────────────────────────────────────── │
  │                                                                │
  │     ┌────────────────────┼────────────────────┐               │
  │     ▼                    ▼                    ▼               │
  │  ┌──────────┐    ┌──────────────┐    ┌───────────────┐       │
  │  │  Jira    │    │  Slack       │    │  Monitoring   │       │
  │  │  ─────── │    │  ─────────── │    │  ───────────  │       │
  │  │  Update  │    │  #dev-alerts │    │  Grafana      │       │
  │  │  Issue   │    │  "Deployed   │    │  Sentry       │       │
  │  │  Status  │    │   v2.1 ✅"   │    │  PagerDuty    │       │
  │  └──────────┘    └──────────────┘    └───────────────┘       │
  │                                                                │
  └────────────────────────────────────────────────────────────────┘
```

### 11.2 ตัวอย่างข้อมูลที่ไหลระหว่าง Tools

```
  📊 DATA FLOW BETWEEN TOOLS

  ┌──────────────┬──────────────────┬──────────────────────────────┐
  │  จาก → ไป    │  ข้อมูลที่ส่ง     │  วิธี Integration             │
  ├──────────────┼──────────────────┼──────────────────────────────┤
  │  Git → Jira  │  Commit Message  │  Smart Commit                │
  │              │  ที่มี Issue Key  │  "PROJ-142 fix: ..."         │
  ├──────────────┼──────────────────┼──────────────────────────────┤
  │  GitHub →    │  PR Status       │  GitHub Actions Trigger      │
  │  CI/CD       │  (Created,       │  on: pull_request            │
  │              │   Merged)        │                              │
  ├──────────────┼──────────────────┼──────────────────────────────┤
  │  CI/CD →     │  Build Status    │  Slack Webhook               │
  │  Slack       │  (Pass/Fail)     │  Notification                │
  ├──────────────┼──────────────────┼──────────────────────────────┤
  │  CI/CD →     │  Docker Image    │  docker push to              │
  │  Registry    │  Tag + Hash      │  Container Registry          │
  ├──────────────┼──────────────────┼──────────────────────────────┤
  │  K8s →       │  Metrics         │  Prometheus Scraping         │
  │  Grafana     │  (CPU, Memory)   │  + Grafana Dashboard         │
  ├──────────────┼──────────────────┼──────────────────────────────┤
  │  Sentry →    │  Error Alert     │  Sentry → Jira              │
  │  Jira        │  (Auto-create    │  Auto-create Bug Issue       │
  │              │   Bug Issue)     │                              │
  ├──────────────┼──────────────────┼──────────────────────────────┤
  │  Grafana →   │  Alert When      │  PagerDuty Integration      │
  │  PagerDuty   │  Threshold Hit   │  Wake On-call Engineer       │
  └──────────────┴──────────────────┴──────────────────────────────┘
```

---

## 12. Building Your First Toolchain — Step by Step <a name="12"></a>

> 💡 ไม่ต้องเริ่มจาก Full Toolchain ตั้งแต่วันแรก — เริ่มจาก Core แล้วเพิ่มทีละตัว

### 12.1 Toolchain Adoption Roadmap

```
  🛤️ TOOLCHAIN ADOPTION — จากศูนย์สู่มืออาชีพ

  ══════════════════════════════════════════════════════════════════

  LEVEL 1: FOUNDATION (สัปดาห์ที่ 1-2)
  ──────────────────────────────────────────────────────────────
  ✅ Git + GitHub           → Version Control พื้นฐาน
  ✅ VS Code               → Code Editor + Extensions
  ✅ Trello (Kanban Board) → Task Tracking เบื้องต้น
  ✅ Basic Terminal/CLI     → Command Line Comfort

  เป้าหมาย: git add → commit → push → PR → merge ได้คล่อง

  ══════════════════════════════════════════════════════════════════

  LEVEL 2: AUTOMATION (สัปดาห์ที่ 3-4)
  ──────────────────────────────────────────────────────────────
  ✅ GitHub Actions         → CI Pipeline เบื้องต้น (Build + Test)
  ✅ Jest / PyTest          → Unit Testing
  ✅ ESLint / Pylint        → Code Quality ตรวจอัตโนมัติ
  ✅ Slack Integration      → แจ้งเตือนเมื่อ Build Pass/Fail

  เป้าหมาย: Push Code → CI Build + Test อัตโนมัติ → แจ้ง Slack

  ══════════════════════════════════════════════════════════════════

  LEVEL 3: CONTAINERIZATION (สัปดาห์ที่ 5-8)
  ──────────────────────────────────────────────────────────────
  ✅ Docker                 → Containerize Application
  ✅ Docker Compose         → Multi-container Setup (App + DB)
  ✅ Container Registry     → Push/Pull Docker Images
  ✅ Deploy to Staging      → CI/CD Deploy Docker Image

  เป้าหมาย: App ทำงานใน Docker → Deploy ขึ้น Staging อัตโนมัติ

  ══════════════════════════════════════════════════════════════════

  LEVEL 4: ORCHESTRATION (สัปดาห์ที่ 9-14)
  ──────────────────────────────────────────────────────────────
  ✅ Kubernetes             → Container Orchestration
  ✅ Monitoring Stack       → Prometheus + Grafana
  ✅ Error Tracking         → Sentry
  ✅ Full CI/CD Pipeline    → Build → Test → Deploy → Monitor

  เป้าหมาย: Full Pipeline ตั้งแต่ Code ถึง Production + Monitoring

  ══════════════════════════════════════════════════════════════════

  LEVEL 5: MASTERY (ต่อเนื่อง)
  ──────────────────────────────────────────────────────────────
  ✅ IaC (Terraform)        → Infrastructure as Code
  ✅ Advanced Testing       → E2E, Performance, Security
  ✅ Jira + Full Integration→ Enterprise Project Tracking
  ✅ On-call & Incident Mgmt→ PagerDuty + Runbooks

  เป้าหมาย: Toolchain ที่พร้อมสำหรับ Production ระดับ Enterprise

  ══════════════════════════════════════════════════════════════════
```

### 12.2 วิชานี้จะพาคุณถึง Level 4

```
  📚 MAPPING กับ Weekly Teaching Plan ของวิชานี้

  ┌──────────────────────┬────────────────────────────────────┐
  │  Level / Topic       │  Sessions ในวิชานี้                 │
  ├──────────────────────┼────────────────────────────────────┤
  │  LEVEL 1: Foundation │  Session 1-4 (Git & GitHub)        │
  │  Git, GitHub,        │  → Configure Git, Branch, Merge    │
  │  Agile Workflow      │  → PR, Fork, Collaboration         │
  ├──────────────────────┼────────────────────────────────────┤
  │  LEVEL 3: Container  │  Session 5-8 (Docker)              │
  │  Docker, Compose     │  → Docker Commands, Images         │
  │                      │  → Compose, Registry, Networking   │
  ├──────────────────────┼────────────────────────────────────┤
  │  LEVEL 2: Automation │  Session 9 (Jenkins CI/CD)         │
  │  CI/CD Pipeline      │  → Jenkins Pipeline, Build Tools   │
  ├──────────────────────┼────────────────────────────────────┤
  │  LEVEL 4: Orchestr.  │  Session 10-14 (Kubernetes)        │
  │  Kubernetes          │  → Pods, Services, Deployments     │
  │                      │  → Applications on K8s             │
  └──────────────────────┴────────────────────────────────────┘
```

---

## 13. Common Pitfalls & How to Avoid Them <a name="13"></a>

```
╔══════════════════════════════════════════════════════════════════════╗
║              ⚠️  COMMON TOOLCHAIN PITFALLS                           ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  🚫 PITFALL 1: "Tool Hoarding" — สะสม Tool มากเกินไป                ║
║  ──────────────────────────────────────────────────────────────     ║
║  ❌ อาการ: ทีมมี 15 Tools แต่ใช้จริงแค่ 5 ตัว ที่เหลือไม่มีใครเปิด ║
║  ✅ แก้: "ถ้าไม่ได้ใช้ใน 30 วัน → ลบออก"                            ║
║     เริ่มจาก Core 4-5 Tools แล้วเพิ่มเมื่อ Pain Point จริง ๆ       ║
║                                                                      ║
║  🚫 PITFALL 2: "Tool before Process" — เลือก Tool ก่อนเข้าใจปัญหา   ║
║  ──────────────────────────────────────────────────────────────     ║
║  ❌ อาการ: "ทีมอื่นใช้ Kubernetes เราก็ต้องใช้!"                     ║
║            (แต่มี User 100 คน, 1 Server ก็เพียงพอ)                  ║
║  ✅ แก้: ถาม "ปัญหาของเราคืออะไร?" ก่อนเลือก Tool เสมอ              ║
║                                                                      ║
║  🚫 PITFALL 3: "No Automation" — ทำทุกอย่างด้วยมือ                   ║
║  ──────────────────────────────────────────────────────────────     ║
║  ❌ อาการ: Deploy ด้วย FTP, Test ด้วยมือ, ส่ง Email แจ้งทีม         ║
║  ✅ แก้: เริ่ม Automate สิ่งที่ง่ายที่สุดก่อน (CI Build + Test)      ║
║     แล้วค่อย ๆ เพิ่ม Automation ทีละขั้น                             ║
║                                                                      ║
║  🚫 PITFALL 4: "Big Bang Setup" — Setup ทุกอย่างพร้อมกันวันเดียว     ║
║  ──────────────────────────────────────────────────────────────     ║
║  ❌ อาการ: ใช้เวลา 2 สัปดาห์ Setup Toolchain ก่อนเริ่มเขียนโค้ด     ║
║  ✅ แก้: เริ่ม Code วันแรก → เพิ่ม Tool เมื่อต้องการจริง              ║
║     Git → Day 1, CI → Week 2, Docker → Week 4                      ║
║                                                                      ║
║  🚫 PITFALL 5: "Islands of Tools" — Tools ไม่เชื่อมต่อกัน            ║
║  ──────────────────────────────────────────────────────────────     ║
║  ❌ อาการ: Jira อยู่ส่วนหนึ่ง, GitHub อีกส่วน, Slack อีก             ║
║     ต้อง Update 3 ที่ทุกครั้ง                                        ║
║  ✅ แก้: Integration สำคัญ! Jira ↔ GitHub ↔ Slack ↔ CI/CD           ║
║     ข้อมูลต้องไหลอัตโนมัติระหว่าง Tools                              ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
```

---

## 14. Development Workflow ในวิชานี้ <a name="14"></a>

> 💡 เพื่อเชื่อมโยงทุกอย่างที่เรียนใน Session 1 เข้าด้วยกัน — นี่คือภาพรวมของ Workflow ที่จะเรียนตลอดภาคเรียน

### 14.1 Course Workflow Map

```
══════════════════════════════════════════════════════════════════
  📚 COURSE WORKFLOW — สิ่งที่จะเรียนในแต่ละช่วง
══════════════════════════════════════════════════════════════════

  Session 1: 📋 OVERVIEW (วันนี้!)
  ─────────────────────────────────────────────────────────────
  เข้าใจภาพรวม Workflow ทั้งหมดก่อนลงรายละเอียด
  → Principles, Roles, Agile, Tracking, Toolchain

  Session 2-4: 🔀 VERSION CONTROL (Git & GitHub)
  ─────────────────────────────────────────────────────────────
  Workflow ที่เรียน:
  [Code] → [git add] → [git commit] → [git push]
       → [Pull Request] → [Code Review] → [Merge]
  Tools: Git, GitHub, Branch, Merge, Revert, Collaboration

  Session 5-8: 🐳 CONTAINERIZATION (Docker)
  ─────────────────────────────────────────────────────────────
  Workflow ที่เรียน:
  [Write Dockerfile] → [docker build] → [docker push]
       → [docker-compose up] → [Deploy with Container]
  Tools: Docker, Docker Compose, Docker Registry, Networking

  Session 9: 🔄 CI/CD (Jenkins)
  ─────────────────────────────────────────────────────────────
  Workflow ที่เรียน:
  [Push Code] → [Jenkins Detect] → [Build] → [Test]
       → [Deploy to Staging] → [Deploy to Production]
  Tools: Jenkins, Jenkinsfile, Pipeline, Build Triggers

  Session 10-14: ☸️ ORCHESTRATION (Kubernetes)
  ─────────────────────────────────────────────────────────────
  Workflow ที่เรียน:
  [Docker Image] → [kubectl apply] → [Pods Running]
       → [Services Exposed] → [Scale Up/Down]
       → [Rolling Update] → [Rollback]
  Tools: kubectl, Pods, Services, Deployments, ReplicaSets

  Session 15: 🎯 MINI PROJECT
  ─────────────────────────────────────────────────────────────
  รวมทุก Workflow เข้าด้วยกัน:
  [Plan] → [Code + Git] → [Docker] → [CI/CD] → [Kubernetes]
       → [Monitor] → [Present]

══════════════════════════════════════════════════════════════════
```

### 14.2 เชื่อมโยง Session 1 ทั้งหมด

```
  🗺️ SESSION 1 COMPLETE MAP — ทุกหัวข้อเชื่อมกันอย่างไร

  ┌──────────────────────────────────────────────────────────────┐
  │                                                              │
  │  📖 Principles to Software Professionals                     │
  │  → WHY: ทำไมต้องเป็น Professional ไม่ใช่แค่ Programmer       │
  │  → รู้จัก SOLID, DRY, KISS, Clean Code                      │
  │                     │                                        │
  │                     ▼                                        │
  │  📖 Roles of Applications in SE Tasks                        │
  │  → WHAT: แต่ละ Tool มีบทบาทอะไรใน SE                        │
  │  → 7 Categories: Plan → Code → Version → CI/CD              │
  │                   → Test → Deploy → Monitor                  │
  │                     │                                        │
  │                     ▼                                        │
  │  📖 Agile Software Development Tools                         │
  │  → HOW (Process): ทีมทำงานร่วมกันอย่างไร                     │
  │  → Scrum (Sprint-based) vs Kanban (Flow-based)               │
  │                     │                                        │
  │                     ▼                                        │
  │  📖 Product Development Tracking                              │
  │  → HOW (Tools): ติดตามงานด้วย Jira / Trello อย่างไร          │
  │  → Workflow Design, JQL, Integration                         │
  │                     │                                        │
  │                     ▼                                        │
  │  📖 Overview of Development Workflow & Toolchain  ← 📍 ตรงนี้│
  │  → CONNECT: เชื่อมทุกอย่างเข้าด้วยกัน                        │
  │  → 5-Phase Loop: Plan → Code → Test → Deploy → Monitor      │
  │  → Toolchain ที่เหมาะกับแต่ละขนาดทีม                         │
  │  → Roadmap สำหรับทั้งวิชา                                     │
  │                                                              │
  └──────────────────────────────────────────────────────────────┘
```

---

## 15. สรุป <a name="15"></a>

```
╔══════════════════════════════════════════════════════════════════════╗
║       🏆 KEY TAKEAWAYS — Overview of Dev Workflow & Toolchain        ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  1️⃣  Workflow คือ "ขั้นตอน" / Toolchain คือ "ชุดเครื่องมือ"          ║
║      เข้าใจ Workflow ก่อน → แล้วค่อยเลือก Tool                       ║
║      Workflow เปลี่ยนน้อย → Tool เปลี่ยนบ่อย                        ║
║                                                                      ║
║  2️⃣  Modern Workflow เป็น Loop 5 Phase                               ║
║      Plan → Code → Test → Deploy → Monitor → (กลับ Plan)            ║
║      ข้อมูลจาก Monitoring ย้อนกลับปรับปรุง Plan ตลอดเวลา             ║
║                                                                      ║
║  3️⃣  Automation คือกุญแจ                                             ║
║      ทุกสิ่งที่ทำซ้ำ → Automate                                       ║
║      CI/CD Pipeline ทำให้ Build, Test, Deploy เกิดอัตโนมัติ           ║
║                                                                      ║
║  4️⃣  Integration สำคัญกว่า Tool เดี่ยว ๆ                             ║
║      Jira + GitHub + Slack + CI/CD ที่เชื่อมกัน                      ║
║      ดีกว่า Tool ดี ๆ 10 ตัวที่ไม่คุยกัน                               ║
║                                                                      ║
║  5️⃣  เริ่มเล็ก เพิ่มทีละขั้น                                          ║
║      Day 1: Git + Editor + Basic Board                               ║
║      Week 2: CI/CD                                                   ║
║      Month 2: Docker + Monitoring                                    ║
║      ไม่ต้อง Setup ทุกอย่างวันแรก                                     ║
║                                                                      ║
║  6️⃣  Quality Gates ป้องกัน Bug เข้า Production                       ║
║      ทุก PR ต้องผ่าน: Build → Test → Review → QA                    ║
║      Deploy ที่ปลอดภัย = Deploy ที่มั่นใจ                              ║
║                                                                      ║
║  7️⃣  Toolchain เลือกตาม Context ของทีม                               ║
║      Solo → Simple (Vercel + GitHub)                                 ║
║      Startup → Lean (Docker + PaaS)                                  ║
║      Enterprise → Full Stack (K8s + Terraform + Full Monitoring)     ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
```

### ภาพสรุปทั้ง Session 1

```
  🗺️ COMPLETE SESSION 1 MIND MAP

                    ┌──────────────────────────┐
                    │  SOFTWARE DEVELOPMENT     │
                    │  TOOLS & ENVIRONMENTS     │
                    │      SESSION 1            │
                    └────────────┬─────────────┘
                                 │
       ┌─────────────────────────┼──────────────────────────┐
       │                         │                          │
       ▼                         ▼                          ▼
  ┌──────────────┐    ┌──────────────────┐    ┌─────────────────┐
  │  PRINCIPLES  │    │    PROCESS       │    │   TOOLCHAIN     │
  │  ──────────  │    │  ──────────────  │    │  ─────────────  │
  │  SOLID       │    │  Agile/Scrum     │    │  Plan: Jira     │
  │  DRY/KISS    │    │  Kanban          │    │  Code: VS Code  │
  │  Clean Code  │    │  Sprint Workflow │    │  VCS: Git       │
  │  Ethics      │    │  Tracking        │    │  CI: Jenkins    │
  │  Growth Mind │    │  Jira/Trello     │    │  Deploy: Docker │
  │              │    │                  │    │  Orch: K8s      │
  └──────────────┘    └──────────────────┘    └─────────────────┘
       │                         │                          │
       └─────────────────────────┼──────────────────────────┘
                                 │
                    ┌────────────▼─────────────┐
                    │   WORKFLOW LOOP           │
                    │   Plan → Code → Test     │
                    │   → Deploy → Monitor     │
                    │   → (Repeat)             │
                    └──────────────────────────┘
```

---

## 16. แบบฝึกหัด <a name="16"></a>

### ✏️ Exercise 1: Workflow Mapping — วาด Workflow ของตัวเอง

```
  โจทย์: จากประสบการณ์การทำงานหรือโปรเจกต์ที่เคยทำ

  1. วาด Development Workflow ของทีม/โปรเจกต์ปัจจุบัน
     (ตั้งแต่ "ได้รับงาน" จนถึง "ส่งมอบ")
     → ระบุแต่ละขั้นตอนว่าใช้ Tool อะไร หรือทำด้วยมือ

  2. ระบุ Pain Points (จุดเจ็บปวด) อย่างน้อย 3 จุด
     เช่น: "Deploy ด้วย FTP ทำให้ลืม Upload บางไฟล์"

  3. เสนอ Tool ที่จะนำมาแก้แต่ละ Pain Point
     พร้อมอธิบายว่า "ทำไม Tool นี้ถึงแก้ปัญหานี้ได้"

  4. วาด Improved Workflow ที่เพิ่ม Tool เข้ามาแล้ว
     เปรียบเทียบกับ Workflow เดิม
```

### ✏️ Exercise 2: Design Toolchain สำหรับ Scenario

```
  โจทย์: ออกแบบ Toolchain สำหรับ Scenario ต่อไปนี้

  ─────────────────────────────────────────────────────────────────
  Scenario A: ทีม 4 คน สร้าง Mobile App (React Native)
  Budget: $0/เดือน (ใช้ Free Tier ทั้งหมด)
  ข้อกำหนด: ต้อง Deploy ได้ทุกสัปดาห์

  Scenario B: ทีม 12 คน พัฒนา Web Platform (Microservices)
  Budget: $1,000/เดือน
  ข้อกำหนด: ต้องมี Staging + Production, Monitoring ครบ

  ─────────────────────────────────────────────────────────────────
  ให้ระบุ Tool สำหรับแต่ละ Phase:
  1. Planning & Tracking
  2. Code Editor & Version Control
  3. CI/CD Pipeline
  4. Testing Strategy (Unit, Integration, E2E)
  5. Deployment (Container, Platform)
  6. Monitoring & Alerting
  7. Communication

  พร้อมอธิบาย:
  → ทำไมถึงเลือก Tool นี้ (เหตุผลที่เหมาะกับ Context)
  → Tool ทำงานร่วมกันอย่างไร (Integration Flow)
  → ข้อจำกัดของ Toolchain ที่ออกแบบ
```

### ✏️ Exercise 3: CI/CD Pipeline Design

```
  โจทย์: เขียน CI/CD Pipeline สำหรับ Web Application

  ─────────────────────────────────────────────────────────────────
  Application: Python FastAPI Backend
  Repository: GitHub
  Deploy Target: Docker Container
  Requirements:
  ☐ Build ทุกครั้งที่ Push
  ☐ Run Unit Tests + Coverage Report
  ☐ Lint Check (flake8)
  ☐ Build Docker Image
  ☐ Deploy ไป Staging เมื่อ Merge เข้า main
  ☐ แจ้ง Slack เมื่อ Pipeline Pass/Fail

  ─────────────────────────────────────────────────────────────────
  ให้ออกแบบ:
  1. Pipeline Diagram (วาดลำดับ Stages)
  2. เขียน Quality Gates สำหรับแต่ละ Stage
  3. เขียน GitHub Actions YAML (ไม่จำเป็นต้องรันได้จริง)
  4. อธิบายว่าถ้า Stage ไหน Fail จะเกิดอะไรขึ้น
```

### ✏️ Exercise 4: Tool Evaluation

```
  โจทย์: เลือก Tool ใน Category เดียวกัน 2 ตัว แล้วเปรียบเทียบ

  ─────────────────────────────────────────────────────────────────
  เลือก 1 คู่จากตัวเลือกต่อไปนี้:

  Category A: CI/CD
  → GitHub Actions  vs  Jenkins

  Category B: Containerization
  → Docker  vs  Podman

  Category C: Monitoring
  → Datadog  vs  Prometheus + Grafana (Open Source)

  Category D: Project Management
  → Jira  vs  Linear

  ─────────────────────────────────────────────────────────────────
  สำหรับคู่ที่เลือก ให้ทำ:
  1. Comparison Table (อย่างน้อย 8 เกณฑ์)
  2. Pros & Cons ของแต่ละ Tool
  3. สถานการณ์ที่ Tool A ดีกว่า Tool B (พร้อมเหตุผล)
  4. สถานการณ์ที่ Tool B ดีกว่า Tool A (พร้อมเหตุผล)
  5. คำแนะนำสำหรับ:
     a. ทีม Startup 5 คน → ควรเลือกตัวไหน? ทำไม?
     b. ทีม Enterprise 50 คน → ควรเลือกตัวไหน? ทำไม?
```

### ✏️ Exercise 5: Reflection — เชื่อมโยง Session 1

```
  โจทย์: เขียน Reflection สรุปสิ่งที่เรียนรู้จาก Session 1 ทั้งหมด
  (1-2 หน้า)

  ─────────────────────────────────────────────────────────────────
  คำถามนำ:

  1. คุณเข้าใจ "Software Professional" ต่างจาก "Programmer"
     อย่างไรบ้างหลังจากเรียน Session นี้?

  2. ถ้าคุณเป็น Tech Lead ของทีม 6 คน ที่กำลังสร้าง Web App ใหม่
     คุณจะเลือก:
     a. Agile Framework: Scrum หรือ Kanban? ทำไม?
     b. Tracking Tool: Jira หรือ Trello? ทำไม?
     c. Toolchain (ระบุ Tool สำหรับแต่ละ Phase)

  3. จาก 5-Phase Workflow Loop (Plan → Code → Test → Deploy → Monitor)
     Phase ไหนที่คุณคิดว่า "สำคัญที่สุด" สำหรับทีมใหม่?
     ให้เหตุผล

  4. สิ่งที่คุณจะนำไปใช้ทันทีหลังจาก Session นี้คืออะไร?
     (ระบุ 3 สิ่งที่ Actionable)
```

---

## 🔗 แหล่งเรียนรู้เพิ่มเติม

```
┌──────────────────────────┬───────────────────────────┬──────────┐
│  หัวข้อ                   │  แหล่งข้อมูล              │  ประเภท  │
├──────────────────────────┼───────────────────────────┼──────────┤
│ DevOps Roadmap           │ roadmap.sh/devops          │ 🗺️ Map   │
│ (แผนที่การเรียนรู้ครบ)    │                           │          │
├──────────────────────────┼───────────────────────────┼──────────┤
│ GitHub Actions Tutorial  │ docs.github.com/actions    │ 📖 Docs  │
├──────────────────────────┼───────────────────────────┼──────────┤
│ Docker Getting Started   │ docs.docker.com/           │ 📖 Docs  │
│                          │ get-started                │          │
├──────────────────────────┼───────────────────────────┼──────────┤
│ Kubernetes Basics        │ kubernetes.io/docs/        │ 📖 Docs  │
│                          │ tutorials                  │          │
├──────────────────────────┼───────────────────────────┼──────────┤
│ The Phoenix Project      │ Gene Kim et al.            │ 📚 Book  │
│ (DevOps Novel)           │                           │          │
├──────────────────────────┼───────────────────────────┼──────────┤
│ Accelerate               │ Nicole Forsgren et al.     │ 📚 Book  │
│ (Science of DevOps)      │                           │          │
├──────────────────────────┼───────────────────────────┼──────────┤
│ Git Interactive Tutorial │ learngitbranching.js.org   │ 🎮 Game  │
├──────────────────────────┼───────────────────────────┼──────────┤
│ Play with Docker         │ play-with-docker.com       │ 🎮 Lab   │
├──────────────────────────┼───────────────────────────┼──────────┤
│ Killercoda K8s Labs      │ killercoda.com             │ 🎮 Lab   │
└──────────────────────────┴───────────────────────────┴──────────┘
```

---

## 📌 Quick Reference Card

```
╔══════════════════════════════════════════════════════════════════════╗
║            🃏 WORKFLOW & TOOLCHAIN CHEATSHEET                        ║
╠════════════════╦═════════════════════════════════════════════════════╣
║  Phase         ║  Workflow Step → Tool Options                       ║
╠════════════════╬═════════════════════════════════════════════════════╣
║  📋 PLAN       ║  Backlog → Sprint Planning                         ║
║                ║  Jira / Trello / Linear / Notion                   ║
╠════════════════╬═════════════════════════════════════════════════════╣
║  💻 CODE       ║  Branch → Code → Commit → Push → PR → Review      ║
║                ║  VS Code + Git + GitHub + ESLint                   ║
╠════════════════╬═════════════════════════════════════════════════════╣
║  🧪 TEST       ║  Unit → Integration → E2E → Quality               ║
║                ║  Jest/PyTest + Postman + Cypress + SonarQube       ║
╠════════════════╬═════════════════════════════════════════════════════╣
║  🚀 DEPLOY     ║  Build Image → Push Registry → Deploy K8s         ║
║                ║  Docker + GitHub Actions/Jenkins + Kubernetes      ║
╠════════════════╬═════════════════════════════════════════════════════╣
║  📊 MONITOR    ║  Metrics → Logs → Errors → Alerts                 ║
║                ║  Prometheus/Grafana + ELK + Sentry + PagerDuty    ║
╠════════════════╬═════════════════════════════════════════════════════╣
║  💬 COMMUNICATE║  Chat → Video → Whiteboard → Design               ║
║                ║  Slack + Zoom + Miro + Figma                       ║
╚════════════════╩═════════════════════════════════════════════════════╝
```

---

<div align="center">

**📌 Session 1 | SOFTWARE DEVELOPMENT TOOLS AND ENVIRONMENTS**
**👨‍🏫 TUCHSANAI PLOYSUWAN**

```
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║  "A great workflow makes good developers excellent,           ║
║   and a bad workflow makes excellent developers frustrated."  ║
║                                                               ║
║  "First, understand the process.                              ║
║   Then, choose the tools.                                     ║
║   Finally, automate everything you can."                      ║
║                                                               ║
║  "The goal is not to have the most tools —                    ║
║   it's to have the right tools, connected well."             ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

*สร้างด้วย ❤️ เพื่อนักพัฒนาซอฟต์แวร์รุ่นใหม่*

</div>