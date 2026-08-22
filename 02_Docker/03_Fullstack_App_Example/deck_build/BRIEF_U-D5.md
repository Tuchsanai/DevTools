# ใบงาน U-D5 — วิดีโอ Remotion 2 คลิป ฝังในเด็ค

## ผลของ spike ที่ทำไปแล้ว (ใช้เป็นฐาน ไม่ต้องพิสูจน์ซ้ำ)
h264 · 960×540 · 30fps · 3 วินาที = 159,037 bytes → 213 KB หลัง base64 · ฟอนต์ไทยผ่าน · เล่นจาก data URI ได้ (`readyState=4`)
โปรเจกต์ spike อยู่ที่ scratchpad — ใช้ต่อได้ **แต่ `node_modules` ห้ามเข้าโฟลเดอร์ชุดสอน**

## คลิปที่ต้องได้ (สั้น เรียบ ไม่มีเสียง ไม่มี transition หวือหวา)

### `v_name` — ตอนที่ 7 / LAB 4 · "ชื่อไม่เปลี่ยน · IP เปลี่ยนได้" (~9 วินาที)
1. กล่องสามใบ `ops-web` `ops-api` `ops-db` บน `ops-net` แสดง IP `172.19.0.2/3/4`
2. `docker rm -f ops-db` แล้วสร้างใหม่ → IP กลายเป็นเลขอื่น → เส้นที่ผูกกับ IP **ขาด สีแดง**
3. สลับสายไปใช้ `ops-db:5432` → เส้น **ต่อติด สีเขียว** ทั้งที่ IP เปลี่ยน
4. ค้างข้อความปิด: `DATABASE_URL=postgresql://opsuser:labpass@ops-db:5432/campusops`

### `v_ship` — ตอนที่ 8 / LAB 5 · "จากเครื่องเรา ถึงเครื่องลูกค้า" (~9 วินาที)
`build` → `tag 1.0` → `push` ขึ้น Docker Hub → ลบ image ในเครื่อง → `pull` → `compose up -d --no-build`
ใช้ `<DOCKER_USER>` เป็น placeholder เท่านั้น — ห้ามใส่ชื่อบัญชีจริง

## ข้อกำหนดการฝัง (ทุกข้อบังคับ ตกข้อใดข้อหนึ่ง = ไม่ผ่าน)

```html
<video data-v="v_name" poster="" muted loop playsinline preload="none"
       style="width:100%;border-radius:9px"></video>
```
1. **poster เป็นภาพหลัก** — ต้องมีเฟรมนิ่ง (PNG data URI) เสมอ เพื่อให้ตอนพิมพ์และก่อนเล่นมีภาพให้ดู
2. `src` ใส่จาก `window.ASSETS` เหมือน `img[data-a]` — เก็บ data URI ไว้ใน `<script id="video-assets">` ใน `_tail.html`
3. **เล่นเฉพาะสไลด์ที่แสดงอยู่** — เมื่อออกจากหน้าต้อง `pause()` และ `currentTime = 0`
4. `@media print{video{display:none} .vposter{display:block}}` — ตอนสั่งพิมพ์ต้องไม่มีวิดีโอเล่นพร้อมกันทุกหน้า
5. เคารพ `prefers-reduced-motion: reduce` → ไม่ autoplay
6. ขนาดรวมของเด็คหลังฝังต้อง ≤ **4 MB**

## ตรวจก่อนส่ง
```
python3 deck_build/build_deck.py --output /tmp/u-d5.html
python3 tools/ui/check_deck.py  --deck /tmp/u-d5.html
python3 tools/ui/verify_slides.py --deck /tmp/u-d5.html
```
`check_deck.py` ตรวจให้แล้วว่า วิดีโอต้องเป็น data URI · ต้องมี poster · ต้องไม่ decode error · attribute ต้องไม่ชี้ออกนอกไฟล์

เพิ่มการตรวจ lifecycle ด้วยตนเองแล้วแนบผลใน log: เปิดหน้าที่มีวิดีโอ → `currentTime` ต้องเดิน → กด `→` ออกจากหน้า → ต้อง `paused === true` และ `currentTime === 0`

## บรรทัดสุดท้ายของคำตอบ
```
UD5: clips=<n> bytes_v_name=<n> bytes_v_ship=<n> deck_mb=<x.xx> poster=OK lifecycle=OK print=OK
```
