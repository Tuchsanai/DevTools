# แหล่งที่มาของสไลด์ — วิธีแก้และ build ใหม่

ไฟล์ `Monitoring_Prometheus_Grafana_Slides.html` ที่ส่งมอบเป็น **ไฟล์เดียวจบ** (CSS/JS inline, รูปฝังเป็น data URI)
ซึ่งแก้ตรง ๆ ได้ลำบาก โฟลเดอร์นี้เก็บ "ต้นฉบับ" ที่ใช้ประกอบไฟล์นั้นขึ้นมา

## ไฟล์ในโฟลเดอร์นี้

| ไฟล์ | หน้าที่ |
|---|---|
| `00_head.html` | `<head>` + CSS ทั้งหมด + เปิด `<div id="stage">` |
| `10_slides_a.html` | สไลด์ 1–32 : ทำไมต้อง monitoring · Metrics 101 · Prometheus · PromQL |
| `20_slides_b.html` | สไลด์ 33–58 : LAB 1–6 · Grafana · instrumentation · alerting |
| `30_slides_c.html` | สไลด์ 59–64 : งานจริง · สรุป · cheat sheet · ปิดท้าย |
| `90_tail.html` | ปุ่มควบคุม · หน้าปุ่มลัด · JavaScript ทั้งหมด (นำทาง/overview/print) |
| `build_deck.py` | ประกอบทุกส่วน + ฝังรูปเป็น base64 → เขียนไฟล์สไลด์จริง |
| `check_deck.py` | เปิดสไลด์ด้วย Playwright ตรวจ JS error · รูปเสีย · เนื้อหาล้นกรอบ 1280×720 |
| `diagrams.py` | นิยามไดอะแกรมทั้ง 14 รูป แล้วสั่ง Excalidraw วาดและ export เป็น SVG |
| `qa_labs.py` | ตรวจกติกาของทั้งชุด (token/`latest`/`mem_limit`/CDN/รูปกำพร้า/หัวข้อ readme) |

## วิธี build ใหม่

```bash
cd slides_assets/deck_src
python3 build_deck.py      # → เขียนทับ ../../Monitoring_Prometheus_Grafana_Slides.html
python3 check_deck.py      # ต้องได้ broken images / overflowing slides / js errors = none
```

`build_deck.py` หยิบรูปจาก 2 ที่โดยอัตโนมัติ:

- `slides_assets/*.svg` → ใช้ชื่อนำหน้าเป็น key (`d01-why-monitoring.svg` → `data-a="d01"`)
- screenshot ของแต่ละแล็บ ตามรายการ `LAB_SHOTS` ในสคริปต์ (`data-a="l1a"`, `l2a`, …)

ถ้าหารูปไม่เจอ จะใส่ภาพ placeholder ให้แล้วพิมพ์ `MISSING SHOTS` เตือน — สไลด์ยังเปิดได้ ไม่พัง

## วิธีแก้ไดอะแกรม

ไฟล์ต้นฉบับที่แก้ได้อยู่ที่ `../scenes/*.excalidraw` — เปิดใน [excalidraw.com](https://excalidraw.com) แล้ว
export เป็น SVG ทับไฟล์เดิมใน `slides_assets/` ได้เลย **แล้วค่อย build สไลด์ใหม่**

ถ้าจะให้สคริปต์วาดใหม่ทั้งหมด (ต้องมี canvas server ของ Excalidraw รันอยู่):

```bash
PORT=3311 EXPRESS_SERVER_URL=http://127.0.0.1:3311 npx -y mcp-excalidraw-server start &
# เปิด http://127.0.0.1:3311 ค้างไว้ในเบราว์เซอร์ (ต้องมีแท็บเปิดอยู่ ไม่งั้น export ไม่ได้)
python3 diagrams.py                    # วาดใหม่ทุกรูป
python3 diagrams.py d11-alert-lifecycle  # หรือระบุเฉพาะรูปที่ต้องการ
```

> ⚠️ ถ้ามีงานอื่นใช้ canvas ที่ port 3000 อยู่ **อย่าใช้ port นั้นร่วมกัน** — `clear` จะลบงานของอีกฝ่ายทิ้ง
> ให้เปิด instance แยก port เหมือนตัวอย่างข้างบนเสมอ
