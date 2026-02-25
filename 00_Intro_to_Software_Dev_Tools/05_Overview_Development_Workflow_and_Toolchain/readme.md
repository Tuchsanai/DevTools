# 📖 Overview of Development Workflow & Toolchain

> **Course:** SOFTWARE DEVELOPMENT TOOLS AND ENVIRONMENTS
> **Session:** 1 — Introduction to Software Development Tools & Environments
> **Level:** Beginner → Intermediate

---

## 📑 สารบัญ (Table of Contents)

| # | หัวข้อ | ระดับ |
|---|--------|-------|
| 0 | [วัตถุประสงค์การเรียนรู้](#0) | 🟢 เริ่มต้น |
| 1 | [Development Workflow คืออะไร?](#1) | 🟢 เริ่มต้น |
| 2 | [Toolchain คืออะไร?](#2) | 🟢 เริ่มต้น |
| 3 | [ภาพรวม Big Picture — ก่อนลงรายละเอียด](#big) | 🟢 เริ่มต้น |
| 4 | [Modern Development Workflow — End-to-End](#3) | 🟡 กลาง |
| 5 | [Phase 1: Plan & Design](#4) | 🟡 กลาง |
| 6 | [Phase 2: Code & Build](#5) | 🟡 กลาง |
| 7 | [Phase 3: Test & Quality Assurance](#6) | 🟡 กลาง |
| 8 | [Phase 4: Deploy & Release](#7) | 🟡 กลาง |
| 9 | [Phase 5: Monitor & Feedback](#8) | 🟡 กลาง |
| 10 | [Workflow Automation — CI/CD Pipeline](#9) | 🔴 ยาก |
| 11 | [Toolchain Archetypes — ตามขนาดทีม](#10) | 🟡 กลาง |
| 12 | [How Tools Connect — Integration Patterns](#11) | 🔴 ยาก |
| 13 | [Building Your First Toolchain — Roadmap](#12) | 🟡 กลาง |
| 14 | [Common Pitfalls & How to Avoid Them](#13) | 🟡 กลาง |
| 15 | [DevOps Culture — วัฒนธรรมที่ขับเคลื่อน Workflow](#devops) | 🟡 กลาง |
| 16 | [Workflow ในวิชานี้ + Session Map](#14) | 🟢 เริ่มต้น |
| 17 | [คำถามที่พบบ่อย (FAQ)](#faq) | 🟢 เริ่มต้น |
| 18 | [สรุป + Cheatsheet](#15) | 🟢 เริ่มต้น |
| 19 | [แบบฝึกหัด](#16) | 🟡 กลาง |

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
> **📋 Pre-requisite:** ไม่ต้องมีพื้นฐาน — อ่านตั้งแต่ต้นได้เลย

---

## 1. Development Workflow คืออะไร? <a name="1"></a>

> 💡 **Development Workflow** คือ **ลำดับขั้นตอน** ที่ทีมพัฒนาซอฟต์แวร์ทำซ้ำ ๆ ในทุก ๆ รอบการพัฒนา ตั้งแต่ "ได้รับงาน" จนถึง "ส่งมอบให้ผู้ใช้" และ "ตรวจสอบผลลัพธ์" โดยมีเป้าหมายคือทำให้กระบวนการนี้ **เร็ว, เชื่อถือได้, ทำซ้ำได้** ทุกครั้ง

### 1.1 เปรียบเทียบให้เข้าใจง่าย — "สายพานพิซซ่า"

```
  🍕 ร้านพิซซ่าที่ดี ≠ แค่ทำพิซซ่าอร่อยครั้งเดียว
     ร้านพิซซ่าที่ดี = กระบวนการที่ทำพิซซ่าอร่อย ได้ทุกครั้ง สม่ำเสมอ

  สายพานร้านพิซซ่า:
  ═══════════════════════════════════════════════════════════════════
  [รับ Order]──►[เตรียมแป้ง]──►[ใส่ Topping]──►[อบ]──►[ตรวจ]──►[ส่ง]
      │              │               │           │       │        │
   Jira/Trello   IDE/Editor       git add    CI Build  QA Test  Deploy
   (รับงาน)     (เขียนโค้ด)      git commit  (Build)  (ทดสอบ)  (ส่งมอบ)
  ═══════════════════════════════════════════════════════════════════

  ✅ ทั้งสองมีจุดร่วมคือ:

  ┌──────────────────────┬─────────────────────────────────────────┐
  │  คุณสมบัติ            │  ตัวอย่างใน Software                    │
  ├──────────────────────┼─────────────────────────────────────────┤
  │  Repeatable          │  Push ครั้งที่ 500 = ครั้งที่ 1 เสมอ    │
  │  (ทำซ้ำได้ทุกครั้ง)   │                                         │
  ├──────────────────────┼─────────────────────────────────────────┤
  │  Quality Gate        │  ผ่าน Automated Tests ก่อน Deploy ทุกที │
  │  (ตรวจก่อนส่ง)       │                                         │
  ├──────────────────────┼─────────────────────────────────────────┤
  │  Sequential + Loop   │  Plan→Code→Test→Deploy→Monitor→Plan...  │
  │  (ลำดับแบบวนซ้ำ)     │                                         │
  ├──────────────────────┼─────────────────────────────────────────┤
  │  Continuous Improve  │  ข้อมูล Monitor → ปรับปรุง Sprint ถัดไป │
  │  (ปรับปรุงตลอดเวลา)  │                                         │
  └──────────────────────┴─────────────────────────────────────────┘
```

### 1.2 Workflow ≠ Toolchain — ความแตกต่างสำคัญ

```
╔══════════════════════════════════════════════════════════════════════╗
║                 🔑 WORKFLOW vs TOOLCHAIN                             ║
╠═══════════════════════════╦══════════════════════════════════════════╣
║  WORKFLOW  (กระบวนการ)     ║  TOOLCHAIN  (ชุดเครื่องมือ)             ║
╠═══════════════════════════╬══════════════════════════════════════════╣
║                           ║                                          ║
║  "ขั้นตอนที่ต้องทำ"        ║  "เครื่องมือที่ใช้ในแต่ละขั้น"             ║
║                           ║                                          ║
║  1. รับงาน                ║  → Jira / Trello / Linear               ║
║  2. ออกแบบ                ║  → Figma / Draw.io / Miro               ║
║  3. เขียนโค้ด             ║  → VS Code / IntelliJ / Cursor          ║
║  4. Commit & Push         ║  → Git / GitHub / GitLab                ║
║  5. Build อัตโนมัติ       ║  → GitHub Actions / Jenkins             ║
║  6. ทดสอบ                 ║  → Jest / PyTest / Cypress              ║
║  7. Deploy                ║  → Docker / Kubernetes                  ║
║  8. Monitor               ║  → Grafana / Sentry                     ║
║                           ║                                          ║
╠═══════════════════════════╬══════════════════════════════════════════╣
║  เปลี่ยนบ่อย: ❌ (Stable) ║  เปลี่ยนบ่อย: ✅ (Tool มาใหม่เรื่อย ๆ)  ║
║  📌 เรียนรู้ก่อน          ║  📌 เลือกหลังจากเข้าใจ Workflow แล้ว    ║
╚═══════════════════════════╩══════════════════════════════════════════╝
```

```
  🔑 กฎทอง:
  ┌─────────────────────────────────────────────────────────────────┐
  │  เข้าใจ WHY/WHAT (Workflow) ก่อน → ค่อยเลือก HOW (Tool)        │
  │                                                                 │
  │  ❌ TOOL-FIRST (ผิด):                                           │
  │     "Jenkins ดูเท่ ลอง setup ไว้ก่อน"                          │
  │     ผลลัพธ์: ใช้เวลา 3 วัน setup แต่ไม่รู้จะใช้ทำอะไร           │
  │                                                                 │
  │  ✅ WORKFLOW-FIRST (ถูก):                                       │
  │     "ทีมเราต้องการ Build + Test อัตโนมัติ เพราะ Deploy พลาดบ่อย" │
  │     → Jenkins หรือ GitHub Actions เป็นตัวเลือกที่เหมาะ          │
  └─────────────────────────────────────────────────────────────────┘
```

### 1.3 ผลลัพธ์เปรียบเทียบ: มี vs ไม่มี Workflow ที่ดี

```
  📊 ทีมที่มี Workflow ชัดเจน vs ทีมที่ไม่มี

  ┌───────────────────────────┬────────────────────┬───────────────────┐
  │ เกณฑ์วัด                  │ ❌ ไม่มี Workflow   │ ✅ มี Workflow     │
  ├───────────────────────────┼────────────────────┼───────────────────┤
  │ Deploy Frequency          │ 1 ครั้ง/เดือน      │ 3-5 ครั้ง/สัปดาห์ │
  │ Deploy Failure Rate       │ 40%                │ 5%                │
  │ Time to Fix Bug (MTTR)    │ 1-3 วัน            │ 1-4 ชั่วโมง       │
  │ Onboard คนใหม่            │ 2-4 สัปดาห์        │ 3-5 วัน           │
  │ ความมั่นใจในการ Deploy     │ 😰 ต่ำมาก          │ 😊 สูง             │
  │ งาน Manual ต่อ Sprint     │ 60% ของเวลา        │ 15% ของเวลา       │
  │ Bug รั่วเข้า Production   │ บ่อย               │ น้อยมาก           │
  └───────────────────────────┴────────────────────┴───────────────────┘

  📌 แหล่งอ้างอิง: DORA Metrics (DevOps Research & Assessment, 2023)
```

---

## 2. Toolchain คืออะไร? <a name="2"></a>

> 💡 **Toolchain** คือ **ชุดเครื่องมือที่เชื่อมต่อกันเป็นสายโซ่** แต่ละเครื่องมือรับผิดชอบขั้นตอนหนึ่งใน Workflow แล้ว **ส่งต่อผลลัพธ์** ให้เครื่องมือถัดไปอัตโนมัติ

### 2.1 โรงงานซอฟต์แวร์อัตโนมัติ — เปรียบเทียบแบบเห็นภาพ

```
  🏭 TOOLCHAIN = สายพานโรงงานซอฟต์แวร์

  วัตถุดิบ
  (Code ที่นักพัฒนาเขียน)
        │
        ▼
  ╔═════════════════════════════════════════════════════════════════╗
  ║                    🏭 TOOLCHAIN FACTORY                         ║
  ║                                                                 ║
  ║  ① นักพัฒนาเขียนโค้ด  ─────────────►  ② บันทึก Version         ║
  ║    [IDE: VS Code]                         [Git + GitHub]        ║
  ║                                                │                ║
  ║                                                ▼                ║
  ║  ⑤ ส่งมอบให้ผู้ใช้  ◄────────────  ③ Build + ทดสอบอัตโนมัติ   ║
  ║    [Kubernetes]                       [GitHub Actions]         ║
  ║        │                                       │                ║
  ║        │                                       ▼                ║
  ║  ⑥ ตรวจสอบระบบ  ──────────────────  ④ บรรจุใน Container        ║
  ║    [Grafana+Sentry]                    [Docker]                ║
  ║                                                                 ║
  ╚═════════════════════════════════════════════════════════════════╝
        │
        ▼
  ผลิตภัณฑ์สำเร็จรูป
  (Application ที่ผู้ใช้เข้าถึงได้ 24/7)
```

### 2.2 คุณสมบัติของ Toolchain ที่ดี

```
╔══════════════════════════════════════════════════════════════════════╗
║               ✅ GOOD TOOLCHAIN — 5 คุณสมบัติหลัก                   ║
╠══════╦═══════════════════════════════════════════════════════════════╣
║  #   ║  คุณสมบัติ + ตัวอย่าง                                        ║
╠══════╬═══════════════════════════════════════════════════════════════╣
║  1️⃣  ║  INTEGRATED — เชื่อมต่อกันอย่างราบรื่น                        ║
║      ║  → Git Push → GitHub Actions รัน Test → Slack แจ้งผล         ║
║      ║  → ไม่ต้อง Copy/Paste ข้อมูลระหว่าง Tools ด้วยมือ             ║
╠══════╬═══════════════════════════════════════════════════════════════╣
║  2️⃣  ║  AUTOMATED — ลดขั้นตอน Manual                                ║
║      ║  → Merge PR → Auto-build → Auto-test → Auto-deploy           ║
║      ║  → มนุษย์ตัดสินใจ, Machine ทำงาน                              ║
╠══════╬═══════════════════════════════════════════════════════════════╣
║  3️⃣  ║  OBSERVABLE — มองเห็นทุกขั้นตอน                               ║
║      ║  → Dashboard แสดง Build Time, Coverage, Uptime Real-time     ║
║      ║  → Log ทุกอย่างเพื่อ Audit ย้อนหลัง                           ║
╠══════╬═══════════════════════════════════════════════════════════════╣
║  4️⃣  ║  REPLACEABLE — เปลี่ยน Tool ได้โดยไม่กระทบ Workflow           ║
║      ║  → Jenkins → GitHub Actions: ขั้นตอนงานเหมือนเดิม            ║
║      ║  → Datadog → Prometheus+Grafana: หน้าที่ Monitoring เหมือนกัน ║
╠══════╬═══════════════════════════════════════════════════════════════╣
║  5️⃣  ║  SCALABLE — โตตามทีมได้                                       ║
║      ║  → ทีม 3 คน → 30 คน: Toolchain ยังรองรับได้                   ║
║      ║  → เพิ่ม Tool ใหม่โดยไม่ทำลาย Tool เดิม                       ║
╚══════╩═══════════════════════════════════════════════════════════════╝
```

---

## 3. ภาพรวม Big Picture — ก่อนลงรายละเอียด <a name="big"></a>

> 🗺️ ดูภาพนี้ก่อนอ่านส่วนที่เหลือ — จะช่วยให้เห็นว่าแต่ละส่วนเชื่อมกันอย่างไร

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║           🗺️ THE COMPLETE SOFTWARE DEVELOPMENT UNIVERSE                      ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║   👤 STAKEHOLDER                                                             ║
║   "อยากได้ Feature X"                                                        ║
║         │                                                                    ║
║         ▼                                                                    ║
║  ┌──────────────────────────────────────────────────────────────────────┐    ║
║  │ 📋 PHASE 1: PLAN & DESIGN                                            │    ║
║  │  Jira → Backlog → Sprint Planning → User Stories → Figma Mockup     │    ║
║  └─────────────────────────────────┬────────────────────────────────────┘    ║
║                                    │ Sprint Goal ชัดเจน                      ║
║                                    ▼                                         ║
║  ┌──────────────────────────────────────────────────────────────────────┐    ║
║  │ 💻 PHASE 2: CODE & BUILD                                             │    ║
║  │  VS Code → git branch → เขียนโค้ด → git commit → PR → Code Review  │    ║
║  └─────────────────────────────────┬────────────────────────────────────┘    ║
║                                    │ PR Merged                               ║
║                                    ▼                                         ║
║  ┌──────────────────────────────────────────────────────────────────────┐    ║
║  │ 🧪 PHASE 3: TEST & QA                                                │    ║
║  │  CI Pipeline: Lint → Unit Test → Integration Test → Security Scan   │    ║
║  └─────────────────────────────────┬────────────────────────────────────┘    ║
║                                    │ All Quality Gates Pass ✅               ║
║                                    ▼                                         ║
║  ┌──────────────────────────────────────────────────────────────────────┐    ║
║  │ 🚀 PHASE 4: DEPLOY & RELEASE                                         │    ║
║  │  Docker Build → Push Registry → Deploy Staging → E2E → Production   │    ║
║  └─────────────────────────────────┬────────────────────────────────────┘    ║
║                                    │ Live in Production                      ║
║                                    ▼                                         ║
║  ┌──────────────────────────────────────────────────────────────────────┐    ║
║  │ 📊 PHASE 5: MONITOR & FEEDBACK                                       │    ║
║  │  Grafana Metrics → Sentry Errors → User Feedback → Alerts           │    ║
║  └─────────────────────────────────┬────────────────────────────────────┘    ║
║                                    │                                         ║
║                                    └───────► 🔄 ย้อนกลับ PHASE 1            ║
║                                              (ข้อมูลจริงปรับปรุง Plan)       ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

```
  🔑 จำสิ่ง 3 อย่างนี้จาก Big Picture:

  ① มัน "วนซ้ำ" (Loop) ไม่ใช่เส้นตรง
     → ทุก Sprint = รอบใหม่ของ Workflow เดิม

  ② ทุก Phase "ป้อนข้อมูล" ให้ Phase ถัดไป
     → Plan → Code → Test → Deploy → Monitor → Plan...

  ③ เครื่องมือ (Tools) อยู่ "ใต้" กระบวนการ (Workflow)
     → เปลี่ยน Tool ได้ แต่ Workflow ยังคงเดิม
```

---

## 4. Modern Development Workflow — End-to-End <a name="3"></a>

> 💡 Workflow สมัยใหม่เป็น **วงรอบ (Loop)** ไม่ใช่เส้นตรง — ข้อมูลจาก Monitor ย้อนกลับไปปรับปรุง Plan ของรอบถัดไปเสมอ

### 4.1 The 5-Phase Development Loop

```
══════════════════════════════════════════════════════════════════
              🔄 MODERN DEVELOPMENT WORKFLOW LOOP
              (ทำซ้ำทุก Sprint = ทุก 1-2 สัปดาห์)
══════════════════════════════════════════════════════════════════

                    ┌───────────────────────┐
                ┌──►│   1. PLAN & DESIGN    │◄──────────────┐
                │   │   วางแผนและออกแบบ      │               │
                │   │   ~2-4 ชม. ต่อ Sprint │               │
                │   └───────────┬───────────┘               │
                │               │ User Stories               │
                │               ▼                            │
                │   ┌───────────────────────┐               │
                │   │   2. CODE & BUILD     │               │
                │   │   เขียนและ Build โค้ด  │               │
                │   │   ~60-70% ของเวลา     │               │
                │   └───────────┬───────────┘               │
                │               │ Code ที่เขียนเสร็จ         │
                │               ▼                            │
                │   ┌───────────────────────┐               │
   Feedback     │   │   3. TEST & QA        │               │  Insights
   ย้อนกลับ    │   │   ทดสอบคุณภาพ         │               │  จาก Data
                │   │   (Auto + Manual)     │               │
                │   └───────────┬───────────┘               │
                │               │ ผ่าน Quality Gate          │
                │               ▼                            │
                │   ┌───────────────────────┐               │
                │   │   4. DEPLOY & RELEASE │               │
                │   │   ส่งมอบให้ผู้ใช้      │               │
                │   │   (Staging → Prod)    │               │
                │   └───────────┬───────────┘               │
                │               │ Running in Production      │
                │               ▼                            │
                │   ┌───────────────────────┐               │
                └───┤   5. MONITOR &        ├───────────────┘
                    │     FEEDBACK          │
                    │   ติดตามและรับ Feedback│
                    └───────────────────────┘

══════════════════════════════════════════════════════════════════
  🔁 รอบนี้เกิดซ้ำทุก Sprint (1-2 สัปดาห์)
  💡 ยิ่ง Loop สั้น = ยิ่งปรับปรุงได้เร็ว = ยิ่งเก่งขึ้นเร็ว
══════════════════════════════════════════════════════════════════
```

### 4.2 Complete Toolchain Map — แต่ละ Phase ใช้อะไร

```
══════════════════════════════════════════════════════════════════════════
  📦 COMPLETE WORKFLOW ↔ TOOLCHAIN MAP
══════════════════════════════════════════════════════════════════════════

  ┌─ PHASE 1: PLAN & DESIGN ──────────────────────────────────────────┐
  │                                                                    │
  │  Task Tracking      Documentation     UI/UX Design    Diagram     │
  │  ┌──────────────┐  ┌──────────────┐  ┌───────────┐  ┌─────────┐  │
  │  │ ⭐ Jira      │  │ ⭐ Confluence │  │ ⭐ Figma  │  │Draw.io  │  │
  │  │   Trello    │  │   Notion     │  │   Zeplin  │  │Lucidchart│ │
  │  │   Linear    │  │   Google Doc │  │   Adobe XD│  │  Miro   │  │
  │  └──────────────┘  └──────────────┘  └───────────┘  └─────────┘  │
  └────────────────────────────────────────────────────────────────────┘

  ┌─ PHASE 2: CODE & BUILD ────────────────────────────────────────────┐
  │                                                                    │
  │  Code Editor        Version Control   Package Mgr    Build Tool   │
  │  ┌──────────────┐  ┌──────────────┐  ┌───────────┐  ┌─────────┐  │
  │  │ ⭐ VS Code   │  │ ⭐ Git       │  │ ⭐ npm    │  │Webpack  │  │
  │  │  IntelliJ   │  │   GitHub    │  │   yarn    │  │  Vite   │  │
  │  │  Cursor AI  │  │   GitLab    │  │   pip     │  │ Gradle  │  │
  │  └──────────────┘  └──────────────┘  └───────────┘  └─────────┘  │
  └────────────────────────────────────────────────────────────────────┘

  ┌─ PHASE 3: TEST & QA ───────────────────────────────────────────────┐
  │                                                                    │
  │  Unit Test          Integration       E2E Test       Code Quality │
  │  ┌──────────────┐  ┌──────────────┐  ┌───────────┐  ┌─────────┐  │
  │  │ ⭐ Jest      │  │ ⭐ Postman   │  │ ⭐ Cypress │  │SonarQube│  │
  │  │  PyTest     │  │   Newman    │  │  Playwright│  │  ESLint │  │
  │  │  JUnit      │  │   SuperTest │  │  Selenium  │  │  Pylint │  │
  │  └──────────────┘  └──────────────┘  └───────────┘  └─────────┘  │
  └────────────────────────────────────────────────────────────────────┘

  ┌─ PHASE 4: DEPLOY & RELEASE ────────────────────────────────────────┐
  │                                                                    │
  │  CI/CD Pipeline     Container         Orchestration   IaC         │
  │  ┌──────────────┐  ┌──────────────┐  ┌───────────┐  ┌─────────┐  │
  │  │ ⭐ GH Actions│  │ ⭐ Docker    │  │ ⭐ K8s    │  │Terraform│  │
  │  │  Jenkins    │  │   Podman    │  │  Helm      │  │ Ansible │  │
  │  │  GitLab CI  │  │             │  │  Swarm     │  │  Pulumi │  │
  │  └──────────────┘  └──────────────┘  └───────────┘  └─────────┘  │
  └────────────────────────────────────────────────────────────────────┘

  ┌─ PHASE 5: MONITOR & FEEDBACK ──────────────────────────────────────┐
  │                                                                    │
  │  Metrics            Logs               Error Track    Alerting    │
  │  ┌──────────────┐  ┌──────────────┐  ┌───────────┐  ┌─────────┐  │
  │  │ ⭐Prometheus │  │ ⭐ ELK Stack │  │ ⭐ Sentry │  │PagerDuty│  │
  │  │  Grafana    │  │   Loki      │  │  Rollbar   │  │Opsgenie │  │
  │  │  Datadog    │  │  Papertrail │  │  Bugsnag   │  │  Slack  │  │
  │  └──────────────┘  └──────────────┘  └───────────┘  └─────────┘  │
  └────────────────────────────────────────────────────────────────────┘

  ⭐ = Tool ที่จะเรียนในวิชานี้
══════════════════════════════════════════════════════════════════════════
```

---

## 5. Phase 1: Plan & Design <a name="4"></a>

> 💡 ทุกอย่างเริ่มจาก **"ทำไม"** และ **"ทำอะไร"** ก่อน **"ทำยังไง"** — Phase นี้กำหนดทิศทางให้ทั้ง Sprint

### 5.1 Workflow ของ Phase Plan & Design

```
  📋 PLAN & DESIGN WORKFLOW

  ┌──────────────────────────────────────────────────────────────────┐
  │                                                                  │
  │   💡 Idea / Request / Bug Report / Customer Feedback             │
  │                          │                                       │
  │                          ▼                                       │
  │            ┌─────────────────────────┐                          │
  │            │    ① Triage & Priority  │                          │
  │            │    PO ตัดสินใจความสำคัญ  │                          │
  │            │    → ถ้าสำคัญ: ต่อไป    │                          │
  │            │    → ถ้าไม่สำคัญ: Archive│                          │
  │            └────────────┬────────────┘                          │
  │                         │                                        │
  │                         ▼                                        │
  │            ┌─────────────────────────┐                          │
  │            │  ② Write User Story     │                          │
  │            │  "As a [user],          │                          │
  │            │   I want [feature]      │                          │
  │            │   so that [benefit]"    │                          │
  │            │  + Acceptance Criteria  │                          │
  │            └────────────┬────────────┘                          │
  │                         │                                        │
  │                         ▼                                        │
  │            ┌─────────────────────────┐                          │
  │            │  ③ Design & Estimate    │                          │
  │            │  → UI Mockup (Figma)    │                          │
  │            │  → Architecture Diagram │                          │
  │            │  → Story Points         │                          │
  │            └────────────┬────────────┘                          │
  │                         │                                        │
  │                         ▼                                        │
  │            ┌─────────────────────────┐                          │
  │            │  ④ Sprint Planning      │                          │
  │            │  → เลือกงานเข้า Sprint  │                          │
  │            │  → กำหนด Sprint Goal    │                          │
  │            │  → Assign สมาชิก        │                          │
  │            └─────────────────────────┘                          │
  │                                                                  │
  └──────────────────────────────────────────────────────────────────┘

  📤 Output ที่ต้องได้จาก Phase นี้:
  ✅ Sprint Goal 1 ประโยค (ทุกคนในทีมต้องรู้)
  ✅ User Stories พร้อม Acceptance Criteria
  ✅ UI Mockup / Wireframe (สำหรับ Frontend)
  ✅ Technical Spec / API Design (สำหรับ Backend)
  ✅ Estimation (กี่ Story Points ต่อ Story)
```

### 5.2 ตัวอย่าง User Story ที่ดี

```
  📝 GOOD USER STORY EXAMPLE

  ┌──────────────────────────────────────────────────────────────────┐
  │  STORY: PROJ-142 — User Login with Email                         │
  │  ─────────────────────────────────────────────────────────────  │
  │                                                                  │
  │  📖 User Story:                                                  │
  │  As a registered user,                                           │
  │  I want to log in using my email and password,                   │
  │  so that I can access my personalized dashboard.                 │
  │                                                                  │
  │  ✅ Acceptance Criteria:                                          │
  │  1. User สามารถกรอก Email + Password แล้วกด Login ได้            │
  │  2. ถ้า Credentials ถูกต้อง → Redirect ไป Dashboard             │
  │  3. ถ้า Credentials ผิด → แสดง Error Message "Invalid credentials"│
  │  4. ถ้า Login ผิด 5 ครั้ง → Lock account 15 นาที                │
  │  5. Password field แสดงเป็น ●●●●●● (ซ่อนตัวอักษร)               │
  │  6. มี "Forgot Password" link                                    │
  │                                                                  │
  │  📊 Story Points: 5 (Medium Complexity)                          │
  │  👤 Assignee: มานะ                                               │
  │  🎯 Sprint: Sprint 12                                            │
  └──────────────────────────────────────────────────────────────────┘

  💡 ทำไม Acceptance Criteria ถึงสำคัญ?
  → Testable: ทดสอบได้ทุกข้อ (ไม่เดา)
  → Clear: ทีมเข้าใจตรงกัน ไม่มี "ฉันคิดว่า..."
  → Completeness: รู้ว่า "เสร็จ" คืออะไร
```

---

## 6. Phase 2: Code & Build <a name="5"></a>

> 💡 Phase นี้คือหัวใจของ Development — เป็นจุดที่ Idea กลายเป็น Code ที่ทำงานได้จริง

### 6.1 Git Workflow ทีละขั้นตอน

```
  💻 CODE & BUILD WORKFLOW — ทีละ Step

  ═════════════════════════════════════════════════════════════════

  STEP 1: รับงานและเตรียม Branch
  ─────────────────────────────────────────────────────────────────
  📋 Jira: เปลี่ยนสถานะ "To Do" → "In Progress"

  $ git checkout main
  $ git pull origin main                    # ดึง Code ล่าสุด
  $ git checkout -b feature/PROJ-142-login  # สร้าง Branch ใหม่

  ═════════════════════════════════════════════════════════════════

  STEP 2: เขียนโค้ด
  ─────────────────────────────────────────────────────────────────
  🖥️ เปิด VS Code → เขียน Code + Unit Tests ไปพร้อมกัน

  ตัวอย่าง (TDD Approach):
  1. เขียน Test ก่อน (Test Fails = ✅ ปกติ)
  2. เขียน Code ให้ Test ผ่าน
  3. Refactor ให้สวยขึ้น
  4. ESLint ตรวจ Style อัตโนมัติ

  ═════════════════════════════════════════════════════════════════

  STEP 3: Commit อย่างถูกต้อง
  ─────────────────────────────────────────────────────────────────
  $ git add src/components/LoginForm.jsx
  $ git add src/components/LoginForm.test.jsx
  $ git commit -m "feat(auth): add email/password login form

  - Add LoginForm component with validation
  - Add unit tests for form validation logic
  - Handle incorrect credentials with error message

  Closes PROJ-142"

  ═════════════════════════════════════════════════════════════════

  STEP 4: Push & สร้าง Pull Request
  ─────────────────────────────────────────────────────────────────
  $ git push origin feature/PROJ-142-login

  บน GitHub:
  → New Pull Request
  → Title: "PROJ-142: Add email/password login form"
  → Assign Reviewers: 2 คน
  → CI Pipeline เริ่มอัตโนมัติ! 🤖

  ═════════════════════════════════════════════════════════════════

  STEP 5: Code Review + Merge
  ─────────────────────────────────────────────────────────────────
  ⏳ Reviewers ตรวจ Code:
  → ✅ Approved: ผ่าน → รอ CI Pass
  → ⚠️ Request Changes: แก้ตาม Feedback → Push ใหม่ → Re-review

  ✅ CI Pass + Approved → Squash & Merge เข้า main
  🗑️ ลบ Feature Branch
  📋 Jira: อัปเดตเป็น "Done" อัตโนมัติ

  ═════════════════════════════════════════════════════════════════
```

### 6.2 Branching Strategy — ภาพ Git Tree

```
  🌿 FEATURE BRANCH WORKFLOW — ภาพจริงของ Git Tree

  main   ─────●───────────────────────────●────────────────────────►
              │                           ▲
              │  git checkout -b feature  │ Merge PR (Squash)
              │                           │
              └──── feature/PROJ-142 ─────●
                         │          │
                         ●          ●
                      "WIP add"   "fix review"
                      login form   comment


  ✅ กฎที่ทีมต้องตกลงร่วมกัน:
  ┌─────────────────────────────────────────────────────────────────┐
  │  1. ชื่อ Branch: feature/[JIRA-KEY]-[short-description]         │
  │     เช่น: feature/PROJ-142-login-page                           │
  │                                                                 │
  │  2. main = Deployable เสมอ (ห้าม Commit ที่ทำให้ Break)          │
  │                                                                 │
  │  3. PR ต้องมี: ✅ CI Pass + ✅ 1+ Reviewer Approved            │
  │                                                                 │
  │  4. ลบ Feature Branch ทันทีหลัง Merge                           │
  │                                                                 │
  │  5. ❌ ห้าม Push ตรงเข้า main โดยไม่ผ่าน PR                    │
  └─────────────────────────────────────────────────────────────────┘
```

### 6.3 Commit Message Format — มาตรฐาน Conventional Commits

```
  📝 CONVENTIONAL COMMITS FORMAT

  ┌─────────────────────────────────────────────────────────────────┐
  │  <type>(<scope>): <short description>                           │
  │                                                                 │
  │  [optional body: อธิบายรายละเอียด]                               │
  │                                                                 │
  │  [optional footer: Closes JIRA-KEY, BREAKING CHANGE: ...]       │
  └─────────────────────────────────────────────────────────────────┘

  ┌──────────┬─────────────────────────┬─────────────────────────────┐
  │  Type    │  ใช้เมื่อ               │  ตัวอย่าง                   │
  ├──────────┼─────────────────────────┼─────────────────────────────┤
  │  feat    │  เพิ่ม Feature ใหม่      │  feat(auth): add Google SSO │
  │  fix     │  แก้ Bug                │  fix(cart): price overflow   │
  │  docs    │  แก้ Documentation      │  docs: update API readme     │
  │  style   │  Format/Spacing         │  style: fix indentation      │
  │  refactor│  Refactor (ไม่เปลี่ยน   │  refactor: extract utils fn  │
  │          │  behavior)              │                              │
  │  test    │  เพิ่ม/แก้ Tests        │  test(auth): add JWT tests   │
  │  chore   │  Maintenance            │  chore: upgrade Node 18→20   │
  │  ci      │  แก้ CI/CD Config       │  ci: add security scan step  │
  └──────────┴─────────────────────────┴─────────────────────────────┘

  ✅ ดีงาม:
     feat(auth): add Google OAuth login button
     fix(cart): resolve price calculation overflow on large quantity
     test(auth): add unit tests for JWT token validation

  ❌ หลีกเลี่ยง:
     "fixed stuff"  →  ไม่รู้ว่าแก้อะไร
     "WIP"          →  อย่า Commit งานที่ยังไม่เสร็จ
     "asdfgh"       →  ไม่มีความหมาย
```

---

## 7. Phase 3: Test & Quality Assurance <a name="6"></a>

> 💡 การทดสอบไม่ใช่แค่ "ลองดูว่าพังไหม" — แต่คือ **การสร้างหลักฐานว่าซอฟต์แวร์ทำงานถูกต้องทุกครั้ง** ที่มีการเปลี่ยนแปลง

### 7.1 Testing Pyramid — ทดสอบแบบไหน เยอะแค่ไหน

```
  🏛️ THE TESTING PYRAMID — หลักการจัดสัดส่วนการทดสอบ

                         ▲
                        /E\
                       /2E \     ← จำนวน น้อย  (10-20%)
                      / Test\    ← ราคา แพง
                     /────────\   ← ความเร็ว ช้า
                    /Integration\
                   /    Tests    \  ← จำนวน ปานกลาง (20-30%)
                  /──────────────\  ← ราคา ปานกลาง
                 /   Unit Tests   \  ← ความเร็ว เร็วปานกลาง
                /─────────────────\
               /  (จำนวน มากที่สุด)\  ← 60-70% ของ Tests ทั้งหมด
              /     เร็ว ถูก มาก    \  ← รันใน < 2 นาที
             /──────────────────────\

  ┌────────────────┬────────────┬─────────────┬────────────────────┐
  │  Layer         │  จำนวน     │  ตัวอย่าง   │  Tool ที่ใช้        │
  ├────────────────┼────────────┼─────────────┼────────────────────┤
  │  Unit Tests    │ มากที่สุด  │ ทดสอบ       │ Jest, PyTest,      │
  │  (ฐาน)         │ (~60-70%)  │ Function,   │ JUnit              │
  │                │            │ Class เดียว │                    │
  ├────────────────┼────────────┼─────────────┼────────────────────┤
  │  Integration   │ ปานกลาง   │ ทดสอบ API,  │ Postman, Newman,   │
  │  Tests         │ (~20-30%)  │ Database    │ SuperTest          │
  │  (กลาง)        │            │ Connection  │                    │
  ├────────────────┼────────────┼─────────────┼────────────────────┤
  │  E2E Tests     │ น้อย       │ ทดสอบ User  │ Cypress,           │
  │  (ยอด)         │ (~10-20%)  │ Journey จริง│ Playwright         │
  └────────────────┴────────────┴─────────────┴────────────────────┘

  💡 ทำไมต้องเป็น Pyramid ไม่ใช่ Ice Cream Cone (E2E เยอะ)?
  → Unit Tests: รันใน milliseconds, แก้ Bug ได้แม่น
  → E2E Tests: รันใน นาที, ช้า, แก้ Bug ยาก
  → ถ้า E2E เยอะ → CI Pipeline ช้า → Developer หงุดหน่ง
```

### 7.2 Testing ใน Workflow — เกิดขึ้นหลายจุด

```
  🧪 WHEN DOES TESTING HAPPEN?

  ┌─────────────────────────────────────────────────────────────────────┐
  │  📍 จุดที่ 1: PRE-COMMIT (Developer เครื่องของตัวเอง)               │
  │  ─────────────────────────────────────────────────────────────────│
  │  → Linter ตรวจ Style ทันทีขณะพิมพ์                                 │
  │  → Pre-commit Hook: ป้องกัน Commit ที่ Lint ไม่ผ่าน                │
  │  เวลา: < 10 วินาที                                                  │
  └──────────────────────────────────────────────────────────────────────┘
                               │ git push
                               ▼
  ┌─────────────────────────────────────────────────────────────────────┐
  │  📍 จุดที่ 2: CI PIPELINE (อัตโนมัติ — ทุก Push/PR)                 │
  │  ─────────────────────────────────────────────────────────────────│
  │                                                                     │
  │  ① Build (< 2 min)                                                 │
  │     → Compile, Install Dependencies                                 │
  │     → ✅ Pass หรือ ❌ Fail Early                                    │
  │                                                                     │
  │  ② Unit Tests (< 2 min)                                            │
  │     → Jest / PyTest รัน Test ทั้งหมด                               │
  │     → Coverage Report → ต้อง > 80%                                │
  │                                                                     │
  │  ③ Integration Tests (< 5 min)                                     │
  │     → API Tests ด้วย Postman/Newman                                │
  │     → Database Migration Tests                                     │
  │                                                                     │
  │  ④ Static Analysis (< 3 min)                                       │
  │     → SonarQube ตรวจ Code Quality Score                            │
  │     → Security Scan: Dependabot, Snyk                              │
  │                                                                     │
  │  รวมเวลา: ~10-15 นาที                                               │
  └──────────────────────────────────────────────────────────────────────┘
                               │ All Pass ✅
                               ▼
  ┌─────────────────────────────────────────────────────────────────────┐
  │  📍 จุดที่ 3: POST-MERGE / STAGING (หลัง Deploy บน Staging)          │
  │  ─────────────────────────────────────────────────────────────────│
  │  → E2E Tests ด้วย Cypress / Playwright                             │
  │  → Performance Tests ด้วย k6                                       │
  │  → Manual QA (Visual/UX ที่ Automate ยาก)                          │
  │  เวลา: 20-60 นาที                                                   │
  └──────────────────────────────────────────────────────────────────────┘
```

### 7.3 Quality Gates — ด่านตรวจก่อน Deploy

```
  🚦 QUALITY GATES — ต้องผ่านทุกด่าน

  ╔═══╦════════════════════╦══════════════════════════╦══════════════╗
  ║ # ║  Gate              ║  เกณฑ์ผ่าน               ║  ใครรับผิดชอบ║
  ╠═══╬════════════════════╬══════════════════════════╬══════════════╣
  ║ 1 ║  🟢 Build & Lint   ║  Lint Pass, Build OK     ║  Automated   ║
  ║   ║                    ║  0 Compile Errors         ║  (CI)        ║
  ╠═══╬════════════════════╬══════════════════════════╬══════════════╣
  ║ 2 ║  🟢 Unit Tests     ║  Coverage > 80%           ║  Automated   ║
  ║   ║                    ║  0 Failed Tests            ║  (CI)        ║
  ╠═══╬════════════════════╬══════════════════════════╬══════════════╣
  ║ 3 ║  🟢 Code Review    ║  1+ Reviewer Approved    ║  Team Member ║
  ║   ║                    ║  ทุก Comment Resolved     ║  (Manual)    ║
  ╠═══╬════════════════════╬══════════════════════════╬══════════════╣
  ║ 4 ║  🟢 Staging QA     ║  E2E Tests Pass          ║  Auto + QA   ║
  ║   ║                    ║  QA Manual Sign-off       ║  Engineer    ║
  ╠═══╬════════════════════╬══════════════════════════╬══════════════╣
  ║ 5 ║  🟢 Release OK     ║  0 Critical Bugs Open    ║  PO / Lead   ║
  ║   ║                    ║  PO Accepted Feature      ║  (Manual)    ║
  ╚═══╩════════════════════╩══════════════════════════╩══════════════╝

  ❌ Gate ไหนไม่ผ่าน → หยุดทันที → แก้ไข → ผ่าน Gate ใหม่
  ✅ ผ่านทุก Gate → ปลอดภัยที่จะ Deploy Production
```

---

## 8. Phase 4: Deploy & Release <a name="7"></a>

> 💡 Deploy คือการทำให้ Code ไปถึงมือผู้ใช้จริง — เป้าหมายคือ **เร็ว, ปลอดภัย, และย้อนกลับได้** ถ้ามีปัญหา

### 8.1 Deployment Pipeline — ทุก Step ชัดเจน

```
  🚀 DEPLOYMENT PIPELINE — จาก Code ถึง Production

  git merge feature/login → main
           │
           ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │  Stage 1: 🏗️ BUILD                                              │
  │  ─────────────────────────────────────────────────────────────│
  │  docker build -t myapp:v2.1.0 .                                │
  │  → สร้าง Docker Image เพียงครั้งเดียว                           │
  │  → Image เดียวกันนี้ใช้ทุก Environment (Dev/Staging/Prod)       │
  │  ⏱️ เวลา: 3-8 นาที                                              │
  └──────────────────────────────┬──────────────────────────────────┘
                                 │ Image Built ✅
                                 ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │  Stage 2: 📦 PUSH TO REGISTRY                                   │
  │  ─────────────────────────────────────────────────────────────│
  │  docker push registry.example.com/myapp:v2.1.0                 │
  │  → เก็บ Image ไว้ใน Container Registry (เหมือน GitHub แต่สำหรับ │
  │    Docker Images)                                              │
  │  ⏱️ เวลา: 1-3 นาที                                              │
  └──────────────────────────────┬──────────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │  Stage 3: 🧪 DEPLOY TO STAGING                                  │
  │  ─────────────────────────────────────────────────────────────│
  │  kubectl apply -f staging/deployment.yaml                      │
  │  → Deploy Image เดียวกันบน Staging Environment                 │
  │  → รัน E2E Tests + Smoke Tests                                 │
  │  → QA ทดสอบ Manual (ถ้าจำเป็น)                                  │
  │  ⏱️ เวลา: 10-30 นาที                                             │
  └──────────────────────────────┬──────────────────────────────────┘
                                 │ Staging Tests Pass ✅
                                 ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │  Stage 4: ⏸️ APPROVAL GATE (Optional)                           │
  │  ─────────────────────────────────────────────────────────────│
  │  → GitHub Environment Protection Rules                         │
  │  → Tech Lead หรือ PO กด Approve ใน GitHub UI                   │
  │  → เหมาะกับ Production ที่ต้องการ Manual Control                │
  └──────────────────────────────┬──────────────────────────────────┘
                                 │ Approved ✅
                                 ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │  Stage 5: 🚀 DEPLOY TO PRODUCTION (Rolling Update)              │
  │  ─────────────────────────────────────────────────────────────│
  │                                                                 │
  │  ก่อน Deploy:                                                   │
  │  Pods [v2.0] ██████████████  (100% Traffic)                     │
  │  Pods [v2.1] ░░░░░░░░░░░░░░  (0% Traffic)                       │
  │                   ▼                                             │
  │  กำลัง Deploy (Rolling):                                         │
  │  Pods [v2.0] ████████░░░░░░  (50% Traffic)                      │
  │  Pods [v2.1] ░░░░░░████████  (50% Traffic)                      │
  │                   ▼                                             │
  │  Deploy เสร็จ:                                                   │
  │  Pods [v2.0] ░░░░░░░░░░░░░░  (0%, Terminated)                   │
  │  Pods [v2.1] ██████████████  (100% Traffic ✅)                  │
  │                                                                 │
  │  ⚠️ ถ้า Health Check Fail → Auto-rollback ทันที!                 │
  │  ⏱️ เวลา: 5-15 นาที (Zero Downtime)                              │
  └──────────────────────────────┬──────────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │  Stage 6: ✅ POST-DEPLOY VERIFICATION                            │
  │  ─────────────────────────────────────────────────────────────│
  │  → Smoke Test บน Production (ทดสอบ API หลัก ๆ)                  │
  │  → ดู Error Rate ใน Sentry (ต้องไม่สูงกว่าก่อน Deploy)           │
  │  → ดู Response Time ใน Grafana (ต้องไม่ช้าลง)                   │
  │  → 🎉 Slack: "v2.1.0 deployed to Production successfully!"     │
  └─────────────────────────────────────────────────────────────────┘
```

### 8.2 Deployment Strategies เปรียบเทียบ

```
  ⚖️ DEPLOYMENT STRATEGIES — เลือกตาม Risk Level

  ┌──────────────┬────────────────────────────────┬───────────────────┐
  │  Strategy    │  วิธีการ (ภาพ)                 │  เหมาะกับ          │
  ├──────────────┼────────────────────────────────┼───────────────────┤
  │  Rolling     │  Old ████████░░░░              │  ส่วนใหญ่ ✅       │
  │  Update      │  New ░░░░████████              │  Risk ต่ำ-กลาง    │
  │  (ค่าเริ่มต้น)│  ค่อย ๆ เปลี่ยนทีละกลุ่ม       │  Zero Downtime    │
  ├──────────────┼────────────────────────────────┼───────────────────┤
  │  Blue/Green  │  Blue  ████████ (Live)         │  ต้องการ          │
  │              │  Green ████████ (New)          │  Instant Rollback │
  │              │  → สลับ Traffic ทั้งก้อน       │  ต้นทุนสูงกว่า    │
  ├──────────────┼────────────────────────────────┼───────────────────┤
  │  Canary      │  v2.0 ████████████ (95%)       │  Feature ที่       │
  │              │  v2.1 █ (5% traffic ก่อน)     │  Risk สูง         │
  │              │  → ค่อย ๆ เพิ่ม Traffic ใหม่  │  A/B Testing      │
  ├──────────────┼────────────────────────────────┼───────────────────┤
  │  Recreate    │  ปิด Old → เปิด New            │  Dev/Staging เท่านั้น│
  │              │  (มี Downtime สั้น ๆ)          │  ประหยัด Resource │
  └──────────────┴────────────────────────────────┴───────────────────┘
```

---

## 9. Phase 5: Monitor & Feedback <a name="8"></a>

> 💡 Deploy เสร็จ ≠ จบงาน — ต้อง Monitor ว่าระบบทำงานดีในสภาพจริง และ Feedback ต้องย้อนกลับไปปรับ Plan รอบถัดไปเสมอ

### 9.1 Monitoring Workflow

```
  📊 MONITOR & FEEDBACK WORKFLOW

  Production System ทำงานอยู่
           │
           ├──────────────────────────────────────────────────────┐
           │                                                      │
           ▼                                                      ▼
  ┌──────────────────────┐                      ┌──────────────────────┐
  │  📈 METRICS           │                      │  🔴 ERROR TRACKING    │
  │  Prometheus + Grafana │                      │  Sentry              │
  │  ───────────────────  │                      │  ──────────────────  │
  │  CPU: 35% ✅         │                      │  🆕 New Error Found!  │
  │  Memory: 2.1GB ✅    │                      │  TypeError at line 42│
  │  Req/sec: 1,200 ✅   │                      │  Users Affected: 847 │
  │  Response: 120ms ✅  │                      │  Browser: Safari     │
  │                       │                      │  Stack Trace: ...    │
  └──────────┬────────────┘                      └──────────┬───────────┘
             │                                              │
             │  ⚠️ Alert Rules:                             │
             │  CPU > 80%                                   │
             │  Error Rate > 1%                             │
             │  Response > 2s                               │
             └──────────────────┬───────────────────────────┘
                                │
                                ▼
                    ┌─────────────────────────┐
                    │  🔔 ALERTING             │
                    │  PagerDuty / Slack       │
                    └──────────┬──────────────┘
                               │
               ┌───────────────┼───────────────┐
               ▼               ▼               ▼
          💬 Slack         📧 Email        📱 Phone
          "#prod-alerts"   Summary         On-Call Dev
               │               │               │
               └───────────────┼───────────────┘
                               │
                               ▼
                    ┌─────────────────────────┐
                    │  🔧 RESPOND & FIX        │
                    │  → Hotfix Branch         │
                    │  → Fast-Track PR Review  │
                    │  → Deploy Hotfix         │
                    └──────────┬──────────────┘
                               │
                               ▼
                    ┌─────────────────────────┐
                    │  📋 FEEDBACK → PLAN      │
                    │  → สร้าง Bug Issue Jira  │
                    │  → เพิ่มใน Next Sprint   │
                    │  → Post-mortem Meeting   │
                    │  → ปรับ Monitoring Rules │
                    └─────────────────────────┘
```

### 9.2 Feedback ย้อนกลับสู่ Phase 1 — ทำให้ Data-Driven

```
  🔄 FEEDBACK LOOP — Production Data → Better Planning

  ┌──────────────────────────────────────────────────────────────────┐
  │  ข้อมูลจาก Monitoring (Sprint ที่ผ่านมา)                         │
  │  ─────────────────────────────────────────────────────────────  │
  │  📊 Grafana: Response Time เพิ่มขึ้น 40% หลัง Deploy v2.1        │
  │  🔴 Sentry: Error Rate สูงขึ้น 0.3% จาก Safari Users             │
  │  💬 User Feedback: "Checkout หน้าเว็บช้ามาก"                     │
  │  📈 Analytics: /api/search ถูกเรียก 10x มากกว่าที่คาด             │
  └──────────────────────────────────────────────────────────────────┘
                              │
                              ▼  แปลงเป็น Action Items
  ┌──────────────────────────────────────────────────────────────────┐
  │  Sprint Backlog ถัดไป (Based on Data, ไม่ได้เดา)                  │
  │  ─────────────────────────────────────────────────────────────  │
  │  🐛 BUG (P1): แก้ Performance Regression จาก v2.1                │
  │  🐛 BUG (P2): Safari Cookie Bug (จาก Sentry Stack Trace)         │
  │  📖 STORY: Optimize Checkout Page (จาก User Feedback)            │
  │  ✅ TASK: Add Redis Cache สำหรับ /api/search                      │
  │  ✅ TASK: เพิ่ม Alert Rule สำหรับ Checkout Time > 2s              │
  └──────────────────────────────────────────────────────────────────┘

  💡 ประโยชน์ของ Feedback Loop:
  → ตัดสินใจด้วยข้อมูลจริง ไม่ใช่สัญชาตญาณ
  → Backlog มีคุณค่ามากขึ้น (ผู้ใช้จริง ๆ ต้องการ)
  → ทีมเรียนรู้จากความผิดพลาด → ไม่ทำซ้ำ
```

---

## 10. Workflow Automation — CI/CD Pipeline <a name="9"></a>

> 💡 **Automation** คือสิ่งที่ทำให้ Workflow ทำงาน **เร็ว, สม่ำเสมอ, ไม่มีข้อผิดพลาดจากมนุษย์** ทุกสิ่งที่ทำซ้ำ ๆ ควร Automate

### 10.1 Manual vs Automated — Before & After

```
  📊 BEFORE AUTOMATION vs AFTER AUTOMATION

  ════════════════════════════════════════════════════════════════

  ❌ BEFORE — Manual Deployment (เจ็บปวดมาก)

  นักพัฒนา:
  1. เขียนโค้ดเสร็จ (2 วัน)
  2. บอก QA ว่าเสร็จแล้ว (Email)
  3. QA ทดสอบด้วยมือ (3 วัน)
  4. รอ Tech Lead Approve (1 วัน)
  5. Copy ไฟล์ขึ้น Server ด้วย FTP 😰
  6. แก้ไขไฟล์ Config บน Server ด้วยมือ
  7. Test ด้วยมือบน Production
  8. 😱 "มันพัง!" → ต้อง Rollback ด้วยมือ

  รวมเวลา: 7-10 วัน / Feature
  Error Rate: สูง (ลืม Upload ไฟล์, แก้ Config ผิด)

  ════════════════════════════════════════════════════════════════

  ✅ AFTER — Automated CI/CD

  นักพัฒนา:
  1. เขียนโค้ดเสร็จ + Push ขึ้น GitHub
  2. 🤖 CI ทำงานอัตโนมัติ:
     → Build (3 min)
     → Unit Tests (2 min)
     → Integration Tests (5 min)
     → Security Scan (3 min)
  3. Slack แจ้ง: "✅ Pipeline passed, review ready"
  4. Code Review บน GitHub (1 วัน)
  5. Merge PR → 🤖 CD ทำงานอัตโนมัติ:
     → Docker Build + Push (5 min)
     → Deploy Staging + E2E Test (15 min)
     → Deploy Production (10 min)
  6. Slack: "🚀 Deployed to Production!"

  รวมเวลา: 1-2 วัน / Feature
  Error Rate: ต่ำมาก (อัตโนมัติทุกขั้น)

  ════════════════════════════════════════════════════════════════
```

### 10.2 อะไรควร Automate — Decision Matrix

```
╔══════════════════════════════════════════════════════════════════════╗
║              🤖 AUTOMATION DECISION MATRIX                           ║
╠═══════════════════════════════════╦══════════════════════════════════╣
║  ✅ AUTOMATE IT                   ║  🧠 HUMAN DOES IT                ║
║  (ทำซ้ำได้, มีกฎที่ชัดเจน)        ║  (ต้องตัดสินใจ, สร้างสรรค์)     ║
╠═══════════════════════════════════╬══════════════════════════════════╣
║  Build (Compile, Bundle)          ║  Code Review (Logic, Design)     ║
║  Run Tests (Unit, Integration)    ║  Architecture Decision           ║
║  Lint & Format Check              ║  Feature Prioritization          ║
║  Deploy to Environment            ║  Bug Severity Triage             ║
║  Send Notifications               ║  UX/UI Design Review             ║
║  Generate Reports/Changelog       ║  Sprint Planning                 ║
║  Security Vulnerability Scan      ║  Customer Communication          ║
║  Performance Benchmarking         ║  Incident Response Decision      ║
║  Dependency Updates (Dependabot)  ║  Business Logic Definition       ║
║  Auto-rollback on Failure         ║  Product Strategy                ║
╠═══════════════════════════════════╬══════════════════════════════════╣
║  💡 ถ้าเขียนเป็น Script ได้ → Automate                               ║
║  💡 ถ้าต้องคิด/ตัดสินใจ → มนุษย์ทำ                                  ║
╚══════════════════════════════════════════════════════════════════════╝
```

### 10.3 GitHub Actions — Full Pipeline ตัวอย่าง

```yaml
# .github/workflows/full-pipeline.yml
name: "🚀 Full CI/CD Pipeline"

# ─── TRIGGER: เมื่อไหร่ให้รัน ─────────────────────────────────────
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  # ─── STAGE 1: BUILD & LINT ─────────────────────────────────────
  build:
    name: "🏗️ Build & Lint"
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4           # ดึง Code จาก GitHub
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'                      # Cache เพื่อความเร็ว
      - run: npm ci                         # Install Dependencies
      - run: npm run lint                   # ESLint Check
      - run: npm run build                  # Build Application

  # ─── STAGE 2: UNIT TESTS ───────────────────────────────────────
  test:
    name: "🧪 Unit Tests + Coverage"
    needs: build                            # รันหลังจาก Build ผ่านก่อน
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20', cache: 'npm' }
      - run: npm ci
      - run: npm test -- --coverage         # Test + Coverage Report
      - name: "📊 Upload Coverage to Codecov"
        uses: codecov/codecov-action@v3
        with:
          fail_ci_if_error: true            # Fail ถ้า Coverage ต่ำกว่า 80%

  # ─── STAGE 3: SECURITY SCAN ────────────────────────────────────
  security:
    name: "🔒 Security Vulnerability Scan"
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: "Run Snyk Security Check"
        uses: snyk/actions/node@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}

  # ─── STAGE 4: DEPLOY TO STAGING ────────────────────────────────
  deploy-staging:
    name: "🚀 Deploy to Staging"
    needs: [test, security]                 # รอ Test + Security ทั้งคู่
    if: github.ref == 'refs/heads/main'     # เฉพาะ Push ไป main
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: "🐳 Build Docker Image"
        run: docker build -t myapp:${{ github.sha }} .
      - name: "📦 Push to Registry"
        run: docker push registry.example.com/myapp:${{ github.sha }}
      - name: "☸️ Deploy to Staging Kubernetes"
        run: kubectl apply -f k8s/staging/

  # ─── STAGE 5: E2E TESTS ON STAGING ────────────────────────────
  e2e-test:
    name: "🖥️ E2E Tests on Staging"
    needs: deploy-staging
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: "Run Cypress E2E Tests"
        uses: cypress-io/github-action@v6
        with:
          config: baseUrl=https://staging.myapp.com

  # ─── STAGE 6: DEPLOY TO PRODUCTION ────────────────────────────
  deploy-production:
    name: "🚀 Deploy to Production"
    needs: e2e-test
    if: github.ref == 'refs/heads/main'
    environment: production                 # ต้องการ Manual Approval!
    runs-on: ubuntu-latest
    steps:
      - name: "☸️ Rolling Deploy to Production"
        run: |
          kubectl set image deployment/myapp \
            app=registry.example.com/myapp:${{ github.sha }} \
            --record
      - name: "✅ Smoke Test"
        run: curl -f https://myapp.com/health
      - name: "💬 Notify Slack"
        run: |
          curl -X POST ${{ secrets.SLACK_WEBHOOK }} \
            -d '{"text":"🚀 *v${{ github.run_number }}* deployed to Production! ✅"}'
```

```
  📊 Pipeline Flow Diagram:

  Push to main
       │
       ├──────────────────────┐
       ▼                      ▼
  [🏗️ Build+Lint]        [same trigger]
       │ ✅                   │
       ├──────────┐           │
       ▼          ▼           │
  [🧪 Tests]  [🔒 Security] ◄─┘
       │ ✅        │ ✅
       └─────┬─────┘
             │ Both Pass
             ▼
     [🚀 Deploy Staging]
             │ ✅
             ▼
     [🖥️ E2E Tests]
             │ ✅
             ▼
     [⏸️ Manual Approval]
             │ ✅ Approved
             ▼
     [🚀 Deploy Production]
             │
             ▼
     [💬 Slack: "Done! 🎉"]
```

---

## 11. Toolchain Archetypes — ตามขนาดทีม <a name="10"></a>

### 11.1 Solo Developer / Side Project (1 คน)

```
══════════════════════════════════════════════════════════════════
  🧑‍💻 SOLO DEVELOPER TOOLCHAIN

  PLAN          CODE           VERSION        CI/CD
  ──────────    ──────────     ──────────     ──────────────────
  Notion        VS Code        GitHub         GitHub Actions
  (Simple TODO) + Extensions   (Free)         (2,000 min/month
                                              Free)

  TEST          DEPLOY         MONITOR        COST
  ──────────    ──────────     ──────────     ──────────────────
  Jest/PyTest   Vercel หรือ    Sentry         $0/เดือน 🎉
  (Basic)       Railway        (Free:         Setup: 1-2 ชม.
                (ฟรี PaaS)    5k errors/mo)

  ✅ ข้อดี:   เริ่มได้เลย, ฟรี 100%, Simple
  ⚠️ ข้อจำกัด: Scale ยาก, ไม่มี Code Review Process

══════════════════════════════════════════════════════════════════
```

### 11.2 Small Startup (3-8 คน)

```
══════════════════════════════════════════════════════════════════
  🚀 STARTUP TOOLCHAIN — Speed over Everything

  PLAN             CODE           VERSION        CI/CD
  ─────────────    ──────────     ──────────     ──────────────
  Trello           VS Code        GitHub         GitHub Actions
  + Notion Docs    + Cursor AI    (Branch        (Auto Test +
  (Kanban)         (AI Assist)    Protection)    Deploy)

  TEST             DEPLOY         MONITOR        COMMUNICATE
  ─────────────    ──────────     ──────────     ──────────────
  Jest + Cypress   Docker +       Sentry Free    Slack (Free)
  Postman Manual   Render/Railway + UptimeRobot  + Figma

  💰 ต้นทุน:   $0-50/เดือน
  ⏱️ Setup:    1-2 วัน
  ✅ ข้อดี:   ต้นทุนต่ำ, เรียนรู้เร็ว, Iterate ได้เร็ว
  ⚠️ ข้อจำกัด: Sprint Report ไม่ดี, Scale ยากเมื่อ > 10 คน

══════════════════════════════════════════════════════════════════
```

### 11.3 Mid-size Company (10-50 คน)

```
══════════════════════════════════════════════════════════════════
  🏢 MID-SIZE TOOLCHAIN — Balance: Speed + Control + Quality

  PLAN                   CODE               VERSION CONTROL
  ───────────────────    ──────────────     ─────────────────────
  Jira Software          VS Code /          GitHub / GitLab
  (Sprints, Epics,       IntelliJ           → Protected Branches
   Roadmap, Reports)     + Team Linters     → Required Reviews
  + Confluence           + EditorConfig     → Status Checks
  (Tech Spec, ADR)

  CI/CD                  TEST               DEPLOY
  ───────────────────    ──────────────     ─────────────────────
  GitHub Actions         Jest + PyTest      Docker +
  + SonarQube            + Cypress (E2E)    Kubernetes (EKS/GKE)
  (Code Quality Gate)    + Postman/Newman   + Helm Charts
  + Dependabot           + k6 (Load Test)   + Terraform (IaC)
  (Auto Security Fix)    + SonarQube Scan   + Staging/Prod Envs

  MONITOR                DESIGN             COMMUNICATE
  ───────────────────    ──────────────     ─────────────────────
  Prometheus + Grafana   Figma + Zeplin     Slack + Zoom
  + Sentry (Errors)      + Storybook        + Miro (Planning)
  + PagerDuty (On-call)  (Component Lib)    + Loom (Video)
  + Datadog (APM)

  💰 ต้นทุน:   $500-2,000/เดือน
  ⏱️ Setup:    1-2 สัปดาห์
  ✅ ข้อดี:   ครบ, Scale ได้ดี, มาตรฐานสูง, Reports ดี
  ⚠️ ข้อจำกัด: ต้นทุนสูง, ต้องมีคนดูแล Infrastructure

══════════════════════════════════════════════════════════════════
```

### 11.4 Quick Comparison — เลือก Toolchain ตามบริบท

```
  📊 TOOLCHAIN QUICK SELECTION GUIDE

  ┌───────────────────┬───────────────┬───────────────┬────────────────┐
  │  Tool Category    │  Solo (1)     │ Startup (3-8) │ Mid-size (10+) │
  ├───────────────────┼───────────────┼───────────────┼────────────────┤
  │  Planning         │  Notion       │  Trello       │  Jira          │
  │  Documentation    │  Notion       │  Notion       │  Confluence    │
  │  Code Editor      │  VS Code      │  VS Code      │  VS Code/IDEA  │
  │  Version Control  │  GitHub       │  GitHub       │  GitHub/GitLab │
  │  CI/CD            │  GH Actions   │  GH Actions   │  GH Actions +  │
  │                   │               │               │  SonarQube     │
  │  Unit Testing     │  Jest/PyTest  │  Jest/PyTest  │  Jest+Coverage │
  │  E2E Testing      │  ❌ ไม่จำเป็น │  Cypress      │  Cypress+k6    │
  │  Containerize     │  ❌ Optional  │  Docker       │  Docker        │
  │  Deploy Platform  │  Vercel/PaaS  │  Render/PaaS  │  Kubernetes    │
  │  Monitoring       │  UptimeRobot  │  Sentry Free  │  Full Stack    │
  │  Alerting         │  Email        │  Slack        │  PagerDuty     │
  ├───────────────────┼───────────────┼───────────────┼────────────────┤
  │  Cost/month       │  $0           │  $0-50        │  $500-2,000    │
  │  Setup Time       │  1-2 ชม.      │  1-2 วัน      │  1-2 สัปดาห์   │
  │  Complexity       │  ⭐           │  ⭐⭐          │  ⭐⭐⭐⭐        │
  └───────────────────┴───────────────┴───────────────┴────────────────┘

  💡 คำแนะนำ:
  → เริ่มจาก Solo Toolchain → เพิ่มเมื่อทีมโตและ Pain Point ชัดเจน
  → ไม่ต้องกระโดดไปใช้ Enterprise Toolchain ตั้งแต่วันแรก
  → "เพิ่ม Tool เมื่อรู้สึกเจ็บปวดจากการไม่มีมัน"
```

---

## 12. How Tools Connect — Integration Patterns <a name="11"></a>

> 💡 เครื่องมือแต่ละตัวทรงพลัง แต่ **พลังที่แท้จริง** มาจากการเชื่อมต่อให้ข้อมูลไหลอัตโนมัติระหว่างเครื่องมือ

### 12.1 Integration Flow — End-to-End

```
  🔗 HOW EVERYTHING CONNECTS — Complete Flow

  ╔══════════════════════════════════════════════════════════════════╗
  ║  👤 DEV          👥 TEAM              🤖 AUTOMATION              ║
  ╠══════════════════════════════════════════════════════════════════╣
  ║                                                                  ║
  ║  VS Code                                                         ║
  ║  → เขียนโค้ด                                                    ║
  ║  → ESLint แจ้ง Error ทันที                                       ║
  ║       │                                                          ║
  ║       │ git commit "feat(auth): PROJ-142 ..."                    ║
  ║       ▼                                                          ║
  ║  GitHub PR Created                                               ║
  ║       │                                    ↗ Jira: Issue → "In Review"  ║
  ║       │                                    ↗ Slack: "#dev PR created"   ║
  ║       │                                                          ║
  ║       ├──────────────────────────────────────────────────►       ║
  ║       │               GitHub Actions Triggered                   ║
  ║       │                        │                                 ║
  ║       │             ┌──────────┼──────────┐                     ║
  ║       │             ▼          ▼          ▼                     ║
  ║       │          [Build]   [Tests]   [Security]                  ║
  ║       │             │          │          │                     ║
  ║       │             └──────────┼──────────┘                     ║
  ║       │                        │ All Pass ✅                     ║
  ║       │                        ▼                                 ║
  ║       │              ← Slack: "CI ✅ Ready to review"           ║
  ║       │              ← GitHub PR: Green Checkmark ✅             ║
  ║       │                                                          ║
  ║  Reviewer Approves PR                                            ║
  ║       │                                                          ║
  ║       ▼                                                          ║
  ║  Merge to main                                                   ║
  ║       │                                                          ║
  ║       ├──────────────────────────────────────────────────►       ║
  ║       │               CD Pipeline Triggered                      ║
  ║       │               → Docker Build + Push                      ║
  ║       │               → Deploy Staging                           ║
  ║       │               → E2E Tests                                ║
  ║       │               → Deploy Production                        ║
  ║       │                                                          ║
  ║       ├─────────────────────────────────────────────────►        ║
  ║       │  Slack: "🚀 v2.1 deployed to Production"                ║
  ║       │  Jira: PROJ-142 → "Done" (Auto!)                        ║
  ║       │  Grafana: Monitor metrics...                             ║
  ║       │  Sentry: Watch for errors...                             ║
  ║                                                                  ║
  ╚══════════════════════════════════════════════════════════════════╝
```

### 12.2 Data Flow ระหว่าง Tools

```
  📊 DATA FLOW — ข้อมูลไหลระหว่าง Tools อย่างไร

  ┌────────────────┬──────────────────────┬──────────────────────────┐
  │  จาก → ไป      │  ข้อมูลที่ส่ง          │  วิธี Integration         │
  ├────────────────┼──────────────────────┼──────────────────────────┤
  │ Git → Jira     │ Commit ที่มี Issue Key │ Smart Commit             │
  │                │ "PROJ-142 feat: ..."  │ "PROJ-142" ใน message    │
  ├────────────────┼──────────────────────┼──────────────────────────┤
  │ GitHub → CI    │ Push/PR Event        │ on: push / pull_request  │
  │                │ (Branch, Commit SHA) │ ใน GitHub Actions        │
  ├────────────────┼──────────────────────┼──────────────────────────┤
  │ CI → Slack     │ Build Status         │ Slack Webhook URL        │
  │                │ Pass/Fail + Link     │ ใน Workflow YAML         │
  ├────────────────┼──────────────────────┼──────────────────────────┤
  │ CI → Registry  │ Docker Image         │ docker push command      │
  │                │ (Tag = git SHA)      │                          │
  ├────────────────┼──────────────────────┼──────────────────────────┤
  │ K8s → Grafana  │ CPU, Memory,         │ Prometheus Scraping      │
  │                │ Network Metrics      │ metrics endpoint         │
  ├────────────────┼──────────────────────┼──────────────────────────┤
  │ App → Sentry   │ Error + Stack Trace  │ Sentry SDK ใน Code       │
  │                │ User affected count  │ sentry.init(dsn=...)     │
  ├────────────────┼──────────────────────┼──────────────────────────┤
  │ Sentry → Jira  │ Auto-create Bug      │ Sentry → Jira            │
  │                │ Issue ทุกครั้งที่มี   │ Integration Plugin       │
  │                │ Error ใหม่           │                          │
  ├────────────────┼──────────────────────┼──────────────────────────┤
  │ Grafana →      │ Alert เมื่อ           │ PagerDuty Integration   │
  │ PagerDuty      │ Threshold Hit        │ ปลุก On-call Engineer    │
  └────────────────┴──────────────────────┴──────────────────────────┘

  💡 ทุก Integration เป็น Event-driven:
  "เมื่อ [Event X เกิดขึ้น] → ส่ง [ข้อมูล Y] ไปที่ [Tool Z]"
```

---

## 13. Building Your First Toolchain — Roadmap <a name="12"></a>

> 💡 ไม่ต้องเริ่มจาก Full Toolchain ตั้งแต่วันแรก — เริ่มจาก Core แล้วเพิ่มทีละตัวตาม Pain Point จริง

### 13.1 Toolchain Adoption Roadmap

```
  🛤️ TOOLCHAIN ADOPTION — จากศูนย์สู่มืออาชีพ

  ══════════════════════════════════════════════════════════════════

  🟢 LEVEL 1: FOUNDATION (สัปดาห์ที่ 1-2)
  ──────────────────────────────────────────────────────────────
  เริ่มทำ:
  ✅ Git + GitHub        → Version Control พื้นฐาน
  ✅ VS Code + Extensions→ Code Editor ที่ดี
  ✅ Trello/Notion       → Task Tracking เบื้องต้น
  ✅ Terminal/CLI Basics → Command Line สบาย

  ✅ เป้าหมาย:
     git add → commit → push → PR → merge ได้คล่อง
     ไม่กลัว Terminal

  ══════════════════════════════════════════════════════════════════

  🟡 LEVEL 2: AUTOMATION (สัปดาห์ที่ 3-4)
  ──────────────────────────────────────────────────────────────
  เพิ่ม:
  ✅ GitHub Actions       → CI Pipeline (Build + Test)
  ✅ Jest / PyTest        → Unit Testing เบื้องต้น
  ✅ ESLint / Pylint      → Code Quality อัตโนมัติ
  ✅ Slack Integration    → แจ้งเตือนเมื่อ Build Pass/Fail

  ✅ เป้าหมาย:
     Push Code → CI Auto Build + Test → Slack แจ้งผล
     ไม่ต้องรัน Test ด้วยมือทุกครั้ง

  ══════════════════════════════════════════════════════════════════

  🟠 LEVEL 3: CONTAINERIZATION (สัปดาห์ที่ 5-8)
  ──────────────────────────────────────────────────────────────
  เพิ่ม:
  ✅ Docker               → Containerize Application
  ✅ Docker Compose       → Multi-container (App + DB)
  ✅ Container Registry   → Push/Pull Docker Images
  ✅ CI/CD Deploy Docker  → Auto-deploy Docker Image

  ✅ เป้าหมาย:
     App ทำงานใน Docker Container
     Deploy ขึ้น Staging อัตโนมัติทุกครั้ง Merge

  ══════════════════════════════════════════════════════════════════

  🔴 LEVEL 4: ORCHESTRATION (สัปดาห์ที่ 9-14)
  ──────────────────────────────────────────────────────────────
  เพิ่ม:
  ✅ Kubernetes           → Container Orchestration
  ✅ Monitoring Stack     → Prometheus + Grafana
  ✅ Error Tracking       → Sentry
  ✅ Full CI/CD Pipeline  → Code → Production

  ✅ เป้าหมาย:
     Full Pipeline: Code → Test → Docker → K8s → Monitor
     Auto-rollback ถ้า Deploy ล้มเหลว

  ══════════════════════════════════════════════════════════════════

  🟣 LEVEL 5: MASTERY (ต่อเนื่อง หลังวิชานี้)
  ──────────────────────────────────────────────────────────────
  สำรวจต่อ:
  ✅ Terraform / Ansible  → Infrastructure as Code (IaC)
  ✅ Advanced Testing     → E2E, Performance, Security Testing
  ✅ Jira Advanced        → Epic, Roadmap, OKR Tracking
  ✅ On-call Management   → PagerDuty + Runbooks

  ══════════════════════════════════════════════════════════════════

  📌 กฎสำคัญ:
  "เพิ่ม Tool เมื่อรู้สึก Pain จากการไม่มีมัน"
  ไม่ใช่ "Setup ทุกอย่างก่อนแล้วค่อยเริ่ม Code"
```

### 13.2 Mapping กับ Course ของวิชานี้

```
  📚 COURSE ROADMAP — วิชานี้พาคุณถึง Level 4

  ┌──────────────────────┬────────────────────────────────────────────┐
  │  Toolchain Level     │  Sessions ในวิชานี้                         │
  ├──────────────────────┼────────────────────────────────────────────┤
  │  LEVEL 1+2:          │  Session 1-4 (Git & GitHub)                │
  │  Foundation +        │  → Configure Git, Branch Strategy          │
  │  Version Control     │  → PR Workflow, Code Review                │
  │                      │  → GitHub Collaboration                    │
  ├──────────────────────┼────────────────────────────────────────────┤
  │  LEVEL 3:            │  Session 5-8 (Docker)                      │
  │  Containerization    │  → Dockerfile, Images, Containers          │
  │                      │  → Docker Compose, Registry, Networking    │
  ├──────────────────────┼────────────────────────────────────────────┤
  │  LEVEL 2 (CI):       │  Session 9 (Jenkins CI/CD)                 │
  │  CI/CD Pipeline      │  → Jenkinsfile, Pipeline Stages            │
  │                      │  → Build Triggers, Artifacts               │
  ├──────────────────────┼────────────────────────────────────────────┤
  │  LEVEL 4:            │  Session 10-14 (Kubernetes)                │
  │  Orchestration       │  → Pods, Services, Deployments             │
  │                      │  → Scaling, Rolling Updates, Rollback      │
  ├──────────────────────┼────────────────────────────────────────────┤
  │  INTEGRATION:        │  Session 15 — Mini Project                 │
  │  ทั้งหมดรวมกัน        │  Plan → Code → Docker → CI/CD → K8s        │
  │                      │  → Monitor → Present                       │
  └──────────────────────┴────────────────────────────────────────────┘
```

---

## 14. Common Pitfalls & How to Avoid Them <a name="13"></a>

```
╔══════════════════════════════════════════════════════════════════════╗
║              ⚠️  5 COMMON TOOLCHAIN MISTAKES                         ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  🚫 MISTAKE 1: "Tool Hoarding" — สะสม Tool มากเกินไป                ║
║  ──────────────────────────────────────────────────────────────     ║
║  ❌ อาการ: ทีมมี 15 Tools แต่ใช้จริงแค่ 5 ตัว                       ║
║            เสียเงิน License + เสียเวลา Context Switching             ║
║  ✅ แก้ได้:                                                          ║
║     • "ถ้าไม่ได้ใช้ใน 30 วัน → ลบออก"                               ║
║     • เริ่มจาก 4-5 Core Tools แล้วเพิ่มเมื่อ Pain จริง ๆ            ║
║                                                                      ║
║  🚫 MISTAKE 2: "Tool before Process" — เลือก Tool ก่อนเข้าใจปัญหา   ║
║  ──────────────────────────────────────────────────────────────     ║
║  ❌ อาการ: "ทีมอื่นใช้ K8s เราก็ต้องใช้!"                            ║
║            (แต่มี User 100 คน, 1 Server พอ)                         ║
║  ✅ แก้ได้:                                                          ║
║     • ถาม "ปัญหาเราคืออะไร?" ก่อนเสมอ                               ║
║     • Tool ดีที่สุด = Tool ที่แก้ Pain ของทีมตอนนี้                  ║
║                                                                      ║
║  🚫 MISTAKE 3: "Manual Everything" — ไม่ Automate                   ║
║  ──────────────────────────────────────────────────────────────     ║
║  ❌ อาการ: Deploy ด้วย FTP, Test ด้วยมือ, ส่ง Email แจ้งทีม         ║
║            เสียเวลาซ้ำ ๆ กับงาน Mechanical                          ║
║  ✅ แก้ได้:                                                          ║
║     • เริ่ม Automate สิ่งง่ายที่สุดก่อน (CI Build + Test)           ║
║     • ทุกครั้งที่ทำ Manual สิ่งเดิม 3 ครั้ง → Automate มัน          ║
║                                                                      ║
║  🚫 MISTAKE 4: "Big Bang Setup" — Setup ทุกอย่างพร้อมกัน            ║
║  ──────────────────────────────────────────────────────────────     ║
║  ❌ อาการ: "รอ Setup Toolchain ให้ครบก่อน แล้วค่อยเริ่ม Code"        ║
║            ผล: 2 สัปดาห์ผ่านไป ยังไม่ได้เขียน Code เลย              ║
║  ✅ แก้ได้:                                                          ║
║     • Day 1: Code + Git                                             ║
║     • Week 2: เพิ่ม CI                                              ║
║     • Week 4: เพิ่ม Docker                                          ║
║     • Month 2: เพิ่ม Monitoring                                     ║
║                                                                      ║
║  🚫 MISTAKE 5: "Islands of Tools" — Tools ไม่เชื่อมต่อกัน           ║
║  ──────────────────────────────────────────────────────────────     ║
║  ❌ อาการ: Jira, GitHub, Slack ต่างคนต่างอยู่                        ║
║            ต้อง Update 3 ที่ทุกครั้งด้วยมือ → ลืม → ข้อมูลไม่ตรงกัน │
║  ✅ แก้ได้:                                                          ║
║     • Integration คือสิ่งที่สำคัญที่สุด                               ║
║     • Jira ↔ GitHub ↔ Slack ↔ CI/CD ต้องไหลอัตโนมัติ                ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
```

---

## 15. DevOps Culture — วัฒนธรรมที่ขับเคลื่อน Workflow <a name="devops"></a>

> 💡 Workflow และ Toolchain ที่ดีเกิดจาก **วัฒนธรรม (Culture)** ไม่ใช่แค่เครื่องมือ — DevOps คือการรวม Development + Operations เข้าด้วยกัน

### 15.1 DevOps คืออะไร และเกี่ยวกับ Workflow อย่างไร

```
  🔺 THE DEVOPS TRIANGLE

             CULTURE
              /\ /\
             /    \
            /      \
           /        \
          /──────────\
       PROCESS      TOOLS

  💡 ถ้าขาด Culture → Process และ Tools ก็ไม่ได้ผล

  DevOps = การทำลายกำแพงระหว่าง "ทีมพัฒนา" กับ "ทีม Operations"

  ❌ BEFORE DevOps (Siloed):
  ┌──────────────┐    กำแพง    ┌──────────────────────────┐
  │ Dev Team     │  ─────────► │ Ops Team                 │
  │ "เขียนโค้ด  │  "โยนข้าม   │ "Deploy และดูแลระบบ"     │
  │  แล้วก็จบ"  │   กำแพง"    │ "ไม่รู้ว่า Dev ทำอะไร"   │
  └──────────────┘             └──────────────────────────┘
  ผลลัพธ์: Deploy ช้า, Blame Game, ไม่มีใครรับผิดชอบรวม

  ✅ AFTER DevOps (Collaborative):
  ┌───────────────────────────────────────────────────────┐
  │              DEV + OPS = ONE TEAM                      │
  │                                                        │
  │  นักพัฒนา  ←→  ทำงานร่วมกัน  ←→  Ops Engineer        │
  │  • เขียน Code         • Deploy และดูแลระบบ             │
  │  • เขียน Test         • Monitor Production             │
  │  • เขียน IaC          • ให้ Feedback                   │
  │  • On-call ด้วยกัน                                     │
  └───────────────────────────────────────────────────────┘
  ผลลัพธ์: Deploy เร็ว, คุณภาพสูง, แก้ Bug เร็ว
```

### 15.2 DORA Metrics — วัดผลลัพธ์ของ DevOps

```
  📊 DORA METRICS — 4 ตัวชี้วัดสำคัญของ DevOps ทีม

  ┌──────────────────────────────────────────────────────────────────┐
  │  Metric             │ Elite Team  │ High Team  │ Low Team        │
  ├─────────────────────┼─────────────┼────────────┼─────────────────┤
  │  1. Deployment      │ On-demand   │ 1-7 วัน    │ เดือนละครั้ง    │
  │  Frequency          │ (หลายครั้ง  │            │ หรือน้อยกว่า    │
  │  (Deploy บ่อยแค่ไหน)│  ต่อวัน)   │            │                 │
  ├─────────────────────┼─────────────┼────────────┼─────────────────┤
  │  2. Lead Time for   │ < 1 ชม.     │ 1-7 วัน    │ 1-6 เดือน       │
  │  Changes            │             │            │                 │
  │  (Commit → Production)│           │            │                 │
  ├─────────────────────┼─────────────┼────────────┼─────────────────┤
  │  3. Change Failure  │ 0-15%       │ 16-30%     │ 46-60%          │
  │  Rate               │             │            │                 │
  │  (Deploy ล้มเหลวกี่%)│            │            │                 │
  ├─────────────────────┼─────────────┼────────────┼─────────────────┤
  │  4. Time to Restore │ < 1 ชม.     │ < 24 ชม.   │ 1-6 เดือน       │
  │  Service            │             │            │                 │
  │  (แก้ Incident เร็ว)│             │            │                 │
  └──────────────────────┴─────────────┴────────────┴─────────────────┘

  💡 ทีมที่มี Good Workflow + Toolchain → เข้าใกล้ "Elite" ได้
  📌 แหล่งอ้างอิง: DORA State of DevOps Report 2023
```

### 15.3 Shift Left — แนวคิดสำคัญใน Modern Workflow

```
  ⬅️ SHIFT LEFT — ตรวจสอบให้เร็วขึ้น ประหยัดมากขึ้น

  ค่าใช้จ่ายในการแก้ Bug ตามช่วงเวลา:
  ──────────────────────────────────────────────────────────────────

  Planning  │  Design  │  Code  │  Testing  │  Production
  ──────────┼──────────┼────────┼───────────┼───────────────────────
     $1     │    $6    │  $10   │   $100    │    $1,000+
  ──────────┴──────────┴────────┴───────────┴───────────────────────
  
  ยิ่งพบ Bug เร็ว → ยิ่งถูก → ยิ่งแก้ง่าย

  ❌ SHIFT RIGHT (เดิม):
  เขียนโค้ด → QA ทดสอบ → พบ Bug → แก้ → QA อีกรอบ (ช้ามาก!)

  ✅ SHIFT LEFT (สมัยใหม่):
  นักพัฒนาเขียน Unit Tests → Linter ตรวจ Code → CI Build+Test
  → Review → Merge → Deploy
  
  Bug ถูกจับตั้งแต่ขณะพิมพ์ (Lint) หรือขณะ Commit (CI)
  ไม่ต้องรอถึง QA หรือ Production!
```

---

## 16. Workflow ในวิชานี้ + Session Map <a name="14"></a>

> 💡 เชื่อมโยงทุกสิ่งที่เรียนใน Session 1 เข้าด้วยกัน และเห็นภาพว่าวิชานี้จะพาไปที่ไหน

### 16.1 Session 1 Complete Map

```
  🗺️ SESSION 1 — ทุกหัวข้อเชื่อมกันอย่างไร

  ┌──────────────────────────────────────────────────────────────────┐
  │  📖 Topic 1: Principles to Software Professionals               │
  │  WHY? → ทำไมต้องเป็น "Professional" ไม่ใช่แค่ Programmer        │
  │  WHAT? → SOLID, DRY, KISS, Clean Code, Growth Mindset          │
  └───────────────────────────────┬──────────────────────────────────┘
                                  │ "เข้าใจพื้นฐานความเป็นมืออาชีพ"
                                  ▼
  ┌──────────────────────────────────────────────────────────────────┐
  │  📖 Topic 2: Roles of Applications in SE Tasks                  │
  │  WHAT? → แต่ละ Tool มีบทบาทอะไรใน Software Engineering         │
  │  MAP? → 7 Tool Categories: Plan→Code→VCS→CI→Test→Deploy→Monitor │
  └───────────────────────────────┬──────────────────────────────────┘
                                  │ "รู้จักโลกของ Tools ทั้งหมด"
                                  ▼
  ┌──────────────────────────────────────────────────────────────────┐
  │  📖 Topic 3: Agile Software Development Tools                   │
  │  HOW (Process)? → ทีมทำงานร่วมกันอย่างไร                        │
  │  WHAT? → Scrum (Sprint) vs Kanban (Continuous Flow)             │
  └───────────────────────────────┬──────────────────────────────────┘
                                  │ "เข้าใจกระบวนการทำงานของทีม"
                                  ▼
  ┌──────────────────────────────────────────────────────────────────┐
  │  📖 Topic 4: Product Development Tracking                        │
  │  HOW (Tools)? → ติดตามงานด้วย Jira/Trello อย่างไร              │
  │  DETAIL? → Workflow Design, JQL, GitHub Integration              │
  └───────────────────────────────┬──────────────────────────────────┘
                                  │ "รู้จักเครื่องมือ Tracking"
                                  ▼
  ┌──────────────────────────────────────────────────────────────────┐
  │  📖 Topic 5: Overview of Workflow & Toolchain  ← 📍 ตรงนี้!     │
  │  CONNECT ALL? → เชื่อมทุกอย่างเข้าด้วยกัน                        │
  │  BIG PICTURE? → 5-Phase Loop, Toolchain, Automation, Roadmap    │
  └──────────────────────────────────────────────────────────────────┘
```

### 16.2 Course Timeline — ทุก Session บนแผนที่วิชา

```
  📅 FULL COURSE WORKFLOW MAP

  Session 1    Sessions 2-4   Sessions 5-8    Session 9
  ─────────    ────────────   ────────────    ─────────
  📋 OVERVIEW  🔀 GIT &       🐳 DOCKER       🔄 CI/CD
               GITHUB         Containerize    Jenkins
               Branch,        dockerfile,     Pipeline,
               PR, Collab     Compose, K8s    Build Trigger
       │             │              │              │
       ▼             ▼              ▼              ▼
  ─────────────────────────────────────────────────────────────►
       │             │              │              │
  You are        กำลังจะ         กำลังจะ         กำลังจะ
  here! 📍        เรียน           เรียน           เรียน

  Sessions 10-14                    Session 15
  ─────────────                     ──────────
  ☸️ KUBERNETES                     🎯 MINI PROJECT
  Pods, Services,                   รวมทุกอย่าง:
  Deployments,                      Plan+Code+Docker
  Scaling, RBAC                     +CI/CD+K8s+Monitor
       │                                  │
       ▼                                  ▼
  กำลังจะเรียน                       CAPSTONE!

  ═══════════════════════════════════════════════════════════
  เส้นทาง:  Git → Docker → Jenkins CI → Kubernetes
            L1-L2 → L3 → L2(CI) → L4 ตาม Toolchain Roadmap
  ═══════════════════════════════════════════════════════════
```

---

## 17. คำถามที่พบบ่อย (FAQ) <a name="faq"></a>

> 💡 รวมคำถามที่นักศึกษามักสงสัยเกี่ยวกับ Workflow และ Toolchain

```
  ❓ FAQ — คำถามที่พบบ่อย

  ╔════════════════════════════════════════════════════════════════════╗
  ║  Q1: เราต้องใช้ Tool ทั้งหมดใน Toolchain Map ไหม?                ║
  ╠════════════════════════════════════════════════════════════════════╣
  ║  A: ไม่! เลือกตามความจำเป็น                                        ║
  ║     Solo Project → Git + VS Code + Vercel ก็พอ                    ║
  ║     เพิ่มเมื่อรู้สึก "เจ็บปวด" จากการไม่มี                          ║
  ╚════════════════════════════════════════════════════════════════════╝

  ╔════════════════════════════════════════════════════════════════════╗
  ║  Q2: ถ้าทีมยังเล็ก จำเป็นต้องมี CI/CD ไหม?                        ║
  ╠════════════════════════════════════════════════════════════════════╣
  ║  A: ใช่! แม้แต่ทีมคนเดียวก็ควรมี CI พื้นฐาน                       ║
  ║     GitHub Actions ฟรีสำหรับ Public Repo                          ║
  ║     ประโยชน์: แจ้งเตือนเมื่อ Code พัง ก่อนที่จะ Push ไป Production ║
  ╚════════════════════════════════════════════════════════════════════╝

  ╔════════════════════════════════════════════════════════════════════╗
  ║  Q3: Workflow ที่เรียนในวิชานี้ใช้กับ Tech Stack ไหนก็ได้ไหม?      ║
  ╠════════════════════════════════════════════════════════════════════╣
  ║  A: ใช่! Workflow หลัก (Plan→Code→Test→Deploy→Monitor) เป็น       ║
  ║     Universal — ใช้ได้กับทุก Language และ Framework               ║
  ║     เฉพาะ Tool ที่เปลี่ยนตาม Tech Stack (Jest สำหรับ JS,          ║
  ║     PyTest สำหรับ Python เป็นต้น)                                  ║
  ╚════════════════════════════════════════════════════════════════════╝

  ╔════════════════════════════════════════════════════════════════════╗
  ║  Q4: Git และ GitHub ต่างกันอย่างไร?                                ║
  ╠════════════════════════════════════════════════════════════════════╣
  ║  A:                                                                ║
  ║  Git = เครื่องมือ Version Control ที่ทำงานบน Local เครื่อง         ║
  ║        คิดถึงมันว่า "ประวัติการแก้ไขไฟล์"                          ║
  ║                                                                    ║
  ║  GitHub = เว็บไซต์ที่เก็บ Git Repository บน Cloud                 ║
  ║           + Code Review, CI/CD, Issues, Wiki                      ║
  ║                                                                    ║
  ║  เปรียบเหมือน: Git = เอกสาร Word / GitHub = Google Drive          ║
  ╚════════════════════════════════════════════════════════════════════╝

  ╔════════════════════════════════════════════════════════════════════╗
  ║  Q5: Docker ต่างจาก Virtual Machine (VM) อย่างไร?                 ║
  ╠════════════════════════════════════════════════════════════════════╣
  ║  A:                                                                ║
  ║  VM = ทำ OS จำลองทั้งตัว (หนัก, ช้า, ใช้ RAM เยอะ)                ║
  ║  Docker Container = แชร์ OS กับ Host (เบา, เร็ว, ใช้ RAM น้อย)    ║
  ║                                                                    ║
  ║  เปรียบเหมือน:                                                     ║
  ║  VM = บ้านแต่ละหลัง (Foundation, Walls, Roof ของตัวเอง)            ║
  ║  Container = อพาร์ทเมนต์ (แชร์ Building Structure, มีห้องส่วนตัว) ║
  ╚════════════════════════════════════════════════════════════════════╝

  ╔════════════════════════════════════════════════════════════════════╗
  ║  Q6: Kubernetes คืออะไร และจำเป็นไหม?                             ║
  ╠════════════════════════════════════════════════════════════════════╣
  ║  A: Kubernetes = ระบบจัดการ Docker Containers หลาย ๆ ตัวอัตโนมัติ  ║
  ║     จำเป็นเมื่อ:                                                    ║
  ║     → App ต้องการ Scale (เพิ่ม/ลด Containers ตาม Load)             ║
  ║     → ต้องการ Zero Downtime Deploy                                 ║
  ║     → มี Containers หลายสิบหรือหลายร้อยตัว                          ║
  ║                                                                    ║
  ║     ยังไม่จำเป็นเมื่อ:                                              ║
  ║     → App ขนาดเล็ก, User น้อย → ใช้ Docker Compose ก็พอ           ║
  ╚════════════════════════════════════════════════════════════════════╝

  ╔════════════════════════════════════════════════════════════════════╗
  ║  Q7: เริ่มเรียนวิชานี้ต้องรู้อะไรบ้าง?                             ║
  ╠════════════════════════════════════════════════════════════════════╣
  ║  A: Pre-requisite ที่แนะนำ:                                        ║
  ║     ✅ เขียน Code ได้บ้าง (ภาษาอะไรก็ได้)                         ║
  ║     ✅ ใช้ Terminal / Command Line ได้พื้นฐาน                      ║
  ║     ✅ ความอยากรู้อยากเห็น และไม่กลัวลองผิดลองถูก                 ║
  ║                                                                    ║
  ║     ไม่จำเป็นต้องรู้:                                               ║
  ║     ❌ Git, Docker, Kubernetes มาก่อน (จะสอนตั้งแต่ต้น)            ║
  ╚════════════════════════════════════════════════════════════════════╝
```

---

## 18. สรุป + Quick Reference Cheatsheet <a name="15"></a>

```
╔══════════════════════════════════════════════════════════════════════╗
║      🏆 KEY TAKEAWAYS — 7 สิ่งที่ต้องจำจาก Session นี้              ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  1️⃣  Workflow = "ขั้นตอน" / Toolchain = "เครื่องมือ"                 ║
║      เรียนรู้ Workflow (WHY/WHAT) ก่อน → ค่อยเลือก Tool (HOW)       ║
║                                                                      ║
║  2️⃣  Modern Workflow เป็น Loop 5 Phase                               ║
║      Plan → Code → Test → Deploy → Monitor → (กลับ Plan)            ║
║      Data จาก Monitor → ทำให้ Plan รอบถัดไปดีขึ้น                   ║
║                                                                      ║
║  3️⃣  Automation = กุญแจสู่ความเร็วและความน่าเชื่อถือ                 ║
║      ทุกสิ่งที่ทำซ้ำ → Automate ด้วย CI/CD                          ║
║      มนุษย์ตัดสินใจ Machine ทำงาน                                    ║
║                                                                      ║
║  4️⃣  Integration สำคัญกว่า Tool เดี่ยว ๆ                             ║
║      Jira + GitHub + Slack + CI/CD ที่เชื่อมกัน                      ║
║      ดีกว่า Tool ดี ๆ 10 ตัวที่ไม่คุยกัน                               ║
║                                                                      ║
║  5️⃣  เริ่มเล็ก เพิ่มทีละขั้น (Incremental Adoption)                  ║
║      Day 1: Git + Editor                                             ║
║      Week 2: CI/CD Pipeline                                          ║
║      Month 2: Docker + Monitoring                                    ║
║                                                                      ║
║  6️⃣  Quality Gates ป้องกัน Bug เข้า Production                       ║
║      Build → Unit Test → Code Review → E2E → Approve → Deploy       ║
║      ผ่านทุก Gate = Deploy ที่ปลอดภัย                                 ║
║                                                                      ║
║  7️⃣  Toolchain เลือกตาม Context ไม่ใช่ตาม Trend                      ║
║      Solo → Simple PaaS tools                                        ║
║      Startup → Lean Docker + Cloud                                   ║
║      Enterprise → Full K8s + Terraform + Full Monitoring             ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
```

### Session 1 Mind Map — ภาพสรุปทั้งหมด

```
  🗺️ SESSION 1 COMPLETE MIND MAP

                    ┌──────────────────────────────┐
                    │  SOFTWARE DEVELOPMENT TOOLS  │
                    │      & ENVIRONMENTS          │
                    │         SESSION 1            │
                    └──────────────┬───────────────┘
                                   │
         ┌─────────────────────────┼───────────────────────────┐
         │                         │                           │
         ▼                         ▼                           ▼
  ┌─────────────┐         ┌──────────────────┐       ┌────────────────┐
  │  PRINCIPLES │         │    PROCESS       │       │   TOOLCHAIN    │
  │  ─────────  │         │  ──────────────  │       │  ────────────  │
  │  SOLID      │         │  Agile/Scrum     │       │  Plan: Jira    │
  │  DRY/KISS   │         │  Kanban          │       │  Code: VS Code │
  │  Clean Code │         │  Sprint Workflow  │       │  VCS: Git      │
  │  Ethics     │         │  Jira/Trello     │       │  CI: Jenkins   │
  │  Growth     │         │  Tracking        │       │  Container:    │
  │  Mindset    │         │  Backlog         │       │    Docker      │
  │             │         │                  │       │  Orch: K8s     │
  └─────────────┘         └──────────────────┘       └────────────────┘
         │                         │                           │
         └─────────────────────────┼───────────────────────────┘
                                   │
                    ┌──────────────▼──────────────────┐
                    │      5-PHASE WORKFLOW LOOP       │
                    │                                  │
                    │  Plan ──► Code ──► Test          │
                    │    ▲                  │          │
                    │    │               Deploy        │
                    │    │                  │          │
                    │  Monitor ◄───────────┘          │
                    │                                  │
                    │  → Automate everything           │
                    │  → Quality Gates at each step    │
                    │  → Feedback drives improvement   │
                    └──────────────────────────────────┘
```

### Quick Reference Card

```
╔══════════════════════════════════════════════════════════════════════╗
║            🃏 WORKFLOW & TOOLCHAIN CHEATSHEET                        ║
╠════════════════╦═════════════════════════════════════════════════════╣
║  Phase         ║  Core Steps → Tools (⭐ = เรียนในวิชานี้)           ║
╠════════════════╬═════════════════════════════════════════════════════╣
║  📋 PLAN       ║  Backlog → Sprint Planning → User Stories           ║
║                ║  ⭐ Jira / Trello / Linear / Notion                 ║
╠════════════════╬═════════════════════════════════════════════════════╣
║  💻 CODE       ║  Branch → Code → Commit → Push → PR → Review       ║
║                ║  ⭐ Git + ⭐ GitHub + VS Code + ESLint              ║
╠════════════════╬═════════════════════════════════════════════════════╣
║  🧪 TEST       ║  Unit → Integration → E2E → Quality Analysis       ║
║                ║  Jest/PyTest + Postman + Cypress + SonarQube       ║
╠════════════════╬═════════════════════════════════════════════════════╣
║  🚀 DEPLOY     ║  Build Image → Push Registry → Deploy K8s          ║
║                ║  ⭐ Docker + ⭐ Jenkins + ⭐ Kubernetes              ║
╠════════════════╬═════════════════════════════════════════════════════╣
║  📊 MONITOR    ║  Metrics → Logs → Errors → Alerts                  ║
║                ║  Prometheus/Grafana + ELK + Sentry + PagerDuty    ║
╠════════════════╬═════════════════════════════════════════════════════╣
║  💬 COMMUNICATE║  Chat → Video → Whiteboard → Design                ║
║                ║  Slack + Zoom + Miro + Figma                       ║
╚════════════════╩═════════════════════════════════════════════════════╝

  ⭐ = Tool หลักที่วิชานี้โฟกัส
```

---

## 19. แบบฝึกหัด <a name="16"></a>

### ✏️ Exercise 1: Workflow Mapping — วาด Workflow จากประสบการณ์ตัวเอง

```
  โจทย์ (30-45 นาที):

  จากโปรเจกต์ที่เคยทำ (วิชาก่อน, Personal Project, หรือจินตนาการ):

  ① วาด Current Workflow
     → ตั้งแต่ "ได้รับงาน" ถึง "ผู้ใช้เข้าถึงได้"
     → ระบุแต่ละขั้น: ใช้ Tool อะไร หรือทำด้วยมือ

  ② ระบุ Pain Points 3 จุด
     เช่น: "ทุกครั้ง Deploy ต้องส่ง FTP ด้วยมือ → ลืม Upload บ่อย"

  ③ เสนอ Tool แก้ Pain Point แต่ละจุด
     พร้อมอธิบาย "ทำไม Tool นี้ถึงแก้ปัญหานี้ได้"

  ④ วาด Improved Workflow
     เปรียบเทียบก่อน/หลัง: เร็วขึ้น/ดีขึ้นอย่างไร?

  📤 ส่ง: Diagram + อธิบาย 1 หน้า
```

### ✏️ Exercise 2: Toolchain Design สำหรับ Scenario

```
  โจทย์ (45-60 นาที):
  ออกแบบ Toolchain สำหรับ Scenario ต่อไปนี้

  ─────────────────────────────────────────────────────────────────
  SCENARIO A: Startup Web App (Budget: $0/เดือน)
  → ทีม 4 คน (2 Dev, 1 Design, 1 PM)
  → สร้าง React + Node.js Web App
  → ต้อง Deploy ได้ทุกสัปดาห์
  → ทุก Tool ต้องใช้ Free Tier

  SCENARIO B: Company Internal Tool (Budget: $800/เดือน)
  → ทีม 8 คน (5 Dev, 1 QA, 1 DevOps, 1 PM)
  → Python FastAPI + PostgreSQL Backend
  → ต้องมี Staging + Production
  → ต้องมี Monitoring พื้นฐาน
  ─────────────────────────────────────────────────────────────────

  สำหรับ Scenario ที่เลือก ระบุ:
  ① Tool สำหรับแต่ละ Phase (Plan/Code/VCS/CI-CD/Test/Deploy/Monitor)
  ② เหตุผลที่เลือก Tool นั้น (ไม่ใช่แค่ชื่อ)
  ③ Integration Flow: Tool A → B → C ข้อมูลอะไรไหลระหว่างกัน
  ④ ข้อจำกัดของ Toolchain ที่ออกแบบ (ซื่อสัตย์!)
  ⑤ ถ้าทีมโตเป็น 2 เท่า Toolchain นี้ยังรองรับได้ไหม?

  📤 ส่ง: Toolchain Diagram + Table + อธิบาย
```

### ✏️ Exercise 3: Pipeline Design + YAML

```
  โจทย์ (60-90 นาที):
  ออกแบบ CI/CD Pipeline สำหรับ Python FastAPI

  ─────────────────────────────────────────────────────────────────
  Application: Python FastAPI Backend (REST API)
  Repository: GitHub Private Repo
  Requirements:
  ☐ Auto Build ทุก Push
  ☐ Unit Tests + Coverage Report (ต้อง > 75%)
  ☐ Lint Check (flake8 + black)
  ☐ Build Docker Image
  ☐ Deploy ไป Staging เมื่อ Merge เข้า main
  ☐ แจ้ง Slack #dev-deploys เมื่อ Pipeline Pass/Fail
  ☐ Require Manual Approval ก่อน Deploy Production
  ─────────────────────────────────────────────────────────────────

  ① วาด Pipeline Flow Diagram (ทุก Stage และลำดับ)
  ② ระบุ Quality Gates แต่ละ Stage
  ③ อธิบาย: ถ้า Stage ไหน Fail → เกิดอะไร? ใครได้รับแจ้ง?
  ④ เขียน GitHub Actions YAML พื้นฐาน (ไม่จำเป็นต้องรันได้จริง)
  ⑤ Bonus: ถ้าจะเพิ่ม Security Scan จะเพิ่มตรงไหน?

  📤 ส่ง: Diagram + YAML + คำอธิบาย
```

### ✏️ Exercise 4: Tool Comparison Analysis

```
  โจทย์ (30-45 นาที):
  เปรียบเทียบ Tool ใน Category เดียวกัน 2 ตัว

  เลือก 1 คู่:
  A) GitHub Actions  vs  Jenkins
  B) Docker           vs  Podman
  C) Jira             vs  Linear
  D) Datadog          vs  Prometheus+Grafana

  ① สร้าง Comparison Table (อย่างน้อย 8 มิติ)
     เช่น: ราคา, Learning Curve, Integration, Community, Hosting

  ② Use Cases:
     → เมื่อไหรใช้ Tool A ดีกว่า (3 สถานการณ์)
     → เมื่อไหรใช้ Tool B ดีกว่า (3 สถานการณ์)

  ③ คำแนะนำสำหรับ:
     → Solo Dev ที่เพิ่งเริ่มต้น → ควรเลือกอะไร?
     → Startup 6 คน → ควรเลือกอะไร?
     → Enterprise 100 คน → ควรเลือกอะไร?

  📤 ส่ง: Table + Analysis + Recommendation
```

### ✏️ Exercise 5: Session 1 Reflection

```
  โจทย์ (30 นาที):
  เขียน Reflection เชื่อมโยงทุกหัวข้อใน Session 1
  ความยาว: 400-600 คำ

  คำถามนำ:
  ① หลังจากเรียน Session 1 คุณมองเห็น Workflow
     ของ Software Development ต่างจากก่อนเรียนอย่างไร?

  ② ถ้าคุณต้องออกแบบทีม 5 คน สร้าง Web App ใหม่:
     → Agile: เลือก Scrum หรือ Kanban? ทำไม?
     → Tracking: Jira หรือ Trello? ทำไม?
     → Toolchain: ระบุ Tool ที่จำเป็นที่สุด 3 ตัวแรก

  ③ Phase ใดใน 5-Phase Workflow Loop ที่คิดว่า
     สำคัญที่สุดสำหรับทีมใหม่? ให้เหตุผล

  ④ 3 สิ่งที่จะนำไปทดลองทำทันทีหลังจาก Session นี้
     (ต้องเป็น Actionable จริง ๆ ไม่ใช่แค่ "จะเรียนรู้")

  📤 ส่ง: Essay + Action Items
```

---

## 🔗 แหล่งเรียนรู้เพิ่มเติม

```
  📚 LEARNING RESOURCES — เรียนต่อด้วยตัวเอง

  ┌──────────────────────────┬────────────────────────────┬──────────┐
  │  หัวข้อ                   │  แหล่งข้อมูล               │  ประเภท  │
  ├──────────────────────────┼────────────────────────────┼──────────┤
  │ DevOps Roadmap สมบูรณ์   │ roadmap.sh/devops           │ 🗺️ Map   │
  ├──────────────────────────┼────────────────────────────┼──────────┤
  │ GitHub Actions Docs      │ docs.github.com/actions     │ 📖 Docs  │
  ├──────────────────────────┼────────────────────────────┼──────────┤
  │ Docker Getting Started   │ docs.docker.com/get-started │ 📖 Docs  │
  ├──────────────────────────┼────────────────────────────┼──────────┤
  │ Kubernetes Basics        │ kubernetes.io/docs/tutorials│ 📖 Docs  │
  ├──────────────────────────┼────────────────────────────┼──────────┤
  │ DORA Research            │ dora.dev                    │ 📊 Study │
  ├──────────────────────────┼────────────────────────────┼──────────┤
  │ The Phoenix Project      │ Gene Kim et al. (Novel)     │ 📚 Book  │
  │ (DevOps สอนผ่านนิยาย)   │                            │          │
  ├──────────────────────────┼────────────────────────────┼──────────┤
  │ Accelerate               │ Nicole Forsgren et al.      │ 📚 Book  │
  │ (Science of DevOps)      │                            │          │
  ├──────────────────────────┼────────────────────────────┼──────────┤
  │ Learn Git Branching      │ learngitbranching.js.org    │ 🎮 Game  │
  │ (เกม Interactive)        │                            │          │
  ├──────────────────────────┼────────────────────────────┼──────────┤
  │ Play with Docker         │ play-with-docker.com        │ 🎮 Lab   │
  │ (ทดลองใน Browser)        │                            │          │
  ├──────────────────────────┼────────────────────────────┼──────────┤
  │ Killercoda K8s Labs      │ killercoda.com              │ 🎮 Lab   │
  │ (ฝึก Kubernetes ฟรี)     │                            │          │
  └──────────────────────────┴────────────────────────────┴──────────┘

  💡 แนะนำลำดับการศึกษาเพิ่มเติม:
  1. learngitbranching.js.org  → ฝึก Git Branch (สนุก!)
  2. roadmap.sh/devops         → ดูภาพรวมสิ่งที่ต้องเรียน
  3. The Phoenix Project       → เข้าใจ DevOps Culture ผ่านเรื่องเล่า
  4. play-with-docker.com      → ทดลอง Docker ก่อน Session 5
```

---

<div align="center">

**📌 Session 1 | SOFTWARE DEVELOPMENT TOOLS AND ENVIRONMENTS**
**👨‍🏫 TUCHSANAI PLOYSUWAN**

```
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║   "A great workflow makes good developers excellent,              ║
║    and a bad workflow makes excellent developers frustrated."     ║
║                                                                   ║
║   "First, understand the process. (WHY & WHAT)                    ║
║    Then, choose the right tools. (HOW)                            ║
║    Finally, automate everything repeatable."                      ║
║                                                                   ║
║   "The goal is not to have the most tools —                       ║
║    it's to have the right tools, connected well,                  ║
║    serving a clear workflow."                                      ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
```

---


*สร้างด้วย ❤️ เพื่อนักพัฒนาซอฟต์แวร์รุ่นใหม่*
*ปรับปรุงเพื่อเพิ่มเนื้อหา ภาพประกอบ และความเข้าใจง่าย*

</div>