# LAB 4 — เชื่อมต่อ Web, API และ Database ด้วยชื่อ Container

> โฟลเดอร์ `004_LAB_Connect_Them` · ใช้ไฟล์ `api/`, `web/`, `db/initdb/` และ `verify.sh`

## ภาพรวม

| ประเด็น | รายละเอียด |
|---|---|
| **คำถามหลัก** | จะให้ Web, API และ Database ติดต่อกันโดยใช้ชื่อ Container แทน IP address และไม่เปิดฐานข้อมูลสู่ภายนอกได้อย่างไร |
| **พื้นฐานที่ใช้** | LAB 1: Environment Variable และ Volume · LAB 2: Image, Port และ API · LAB 3: Web Application |
| **ผลลัพธ์การเรียนรู้** | สร้าง Docker Network · ใช้ DNS ภายใน Network · ตรวจเส้นทาง Web → API → Database · พิสูจน์ว่าฐานข้อมูลไม่มี Published Port |
| **ขอบเขต** | LAB นี้ยังไม่ใช้ `compose.yaml`; จะนำโครงสร้างเดียวกันไปเขียนเป็น Compose ใน LAB 5 |

## คำศัพท์ที่ต้องทราบก่อนเริ่ม

- **Image** คือแม่แบบแบบอ่านอย่างเดียวที่ใช้สร้างหน่วยทำงานของ Docker
- **Container** คือหน่วยทำงานที่สร้างจาก Image และมี Process, File System และ Network ของตนเอง เอกสารนี้ใช้คำว่า **Container** โดยตรงเพื่อรักษาความหมายทางเทคนิค
- **Network** คือเครือข่ายเสมือนที่เชื่อม Container ที่เกี่ยวข้องกัน
- **IP address (Internet Protocol address)** คือหมายเลขที่ใช้ระบุปลายทางบน Network หมายเลขของ Container อาจเปลี่ยนเมื่อสร้างใหม่
- **DNS (Domain Name System)** คือบริการแปลงชื่อเป็น IP address ใน LAB นี้ DNS ภายใน Docker จะแปลงชื่อ Container เช่น `devtools-connect-db`
- **User-defined bridge network** คือ Network ชนิด bridge ที่ผู้ใช้สร้างเอง มี DNS ภายในและแยกสมาชิกออกจาก Container อื่น
- **API (Application Programming Interface)** คือช่องทางที่ Web ใช้ขอหรือแก้ข้อมูลจากบริการเบื้องหลัง
- **Database** คือบริการจัดเก็บข้อมูล ใน LAB นี้ใช้ PostgreSQL และใช้ชื่อย่อ `db` เฉพาะในชื่อ Container หรือผลลัพธ์ของระบบ
- **UI (User Interface)** คือหน้าจอที่ผู้ใช้มองเห็นและโต้ตอบผ่านเบราว์เซอร์
- **Published Port** คือ Port ของ Container ที่เชื่อมออกมายัง Host ด้วยตัวเลือก `-p`; หากไม่ Publish บริการจะไม่เปิดรับการเชื่อมต่อจาก Host ผ่าน Port นั้น
- **Environment Variable** คือตัวแปรกำหนดค่าขณะเริ่ม Container เช่น `DATABASE_URL` และ `API_BASE_URL`
- **NFR (Non-Functional Requirement)** คือข้อกำหนดด้านคุณภาพหรือข้อจำกัดของระบบ ต่างจาก Functional Requirement ที่อธิบายว่าระบบต้องทำงานอะไร ใน LAB นี้ **NFR-3** กำหนดว่า Database ต้องไม่เปิด Port สู่ภายนอก
- **Acceptance Criteria** หรือเกณฑ์การผ่าน คือผลลัพธ์ที่สังเกตและทดสอบซ้ำได้ สำหรับ LAB นี้ต้องเรียกบริการด้วยชื่อ Container ได้ หน้า UI แสดงข้อมูลจริง และ `docker port` ของ Database ต้องไม่คืนค่า

## เหตุผลที่ไม่ควรผูกบริการด้วย IP address

Docker จัดสรร IP address ตามลำดับที่ Container เข้าร่วม Network หมายเลขจึงอาจเปลี่ยนเมื่อสร้าง Container ใหม่ หาก `DATABASE_URL` บันทึก IP address เดิม API อาจชี้ไปยังปลายทางที่ไม่ถูกต้อง แต่ชื่อ Container คงเดิมและ DNS ภายใน Docker จะตอบ IP address ปัจจุบันให้ทุกครั้ง

![แผนภาพเปรียบเทียบการอ้าง Database ด้วย IP address และชื่อ Container](./images/theory-name-not-ip.svg)

*ภาพที่ 1 — DNS ภายใน User-defined Network ช่วยให้ API อ้าง Database ด้วยชื่อที่คงที่ แม้ IP address เปลี่ยน*

Default bridge คือ Network เริ่มต้นที่ Docker จัดให้เมื่อไม่ระบุ `--network`; ไม่ควรใช้ชื่อ Container เป็นกลไกเชื่อมบริการใน Network นี้ ส่วน User-defined bridge network มี DNS ภายในและจัดการสมาชิกได้ด้วย `docker network connect` หรือ `docker network disconnect`

![แผนภาพเปรียบเทียบ Default bridge กับ User-defined bridge network](./images/theory-bridge-vs-usernet.svg)

*ภาพที่ 2 — สิ่งที่เปลี่ยนคือ Network ที่ Container เข้าร่วม ไม่ใช่ Image หรือ Port ภายใน*

NFR-3 ตรวจจากโครงสร้างการเปิด Port: Web ต้องมี Published Port เพื่อให้ผู้ใช้เปิด UI แต่ API และ Database ติดต่อกันภายใน Network จึงไม่ต้อง Publish Port ออกสู่ Host

![แผนภาพเส้นทาง Web, API และ Database โดย Database ไม่มี Published Port](./images/theory-nfr3-closed-db.svg)

*ภาพที่ 3 — ลูกศรสีเขียวคือเส้นทางภายในที่อนุญาต เส้นประสีแดงคือเส้นทางจาก Host ที่เข้า Database ไม่ได้*

## เตรียมสภาพแวดล้อม

### 1. เริ่ม Container สำหรับเรียน

รันบน Host โดยแทน `<DOCKER_USER>` ด้วยชื่อบัญชีที่ผู้สอนจัดเตรียมให้

```bash
docker rm -f devtools-connect-lab 2>/dev/null
docker run -dit --name devtools-connect-lab --privileged \
  -p 2225:22 -p 8254:3000 <DOCKER_USER>/devtools:2569_1
```

เชื่อมต่อด้วย SSH (Secure Shell) ซึ่งเป็นวิธีเปิด Command-line Shell บนเครื่องปลายทาง

```bash
ssh root@localhost -p 2225
```

ใช้รหัสผ่านสำหรับ LAB ที่ผู้สอนจัดเตรียมให้ เอกสารนี้ไม่บันทึกรหัสผ่านจริง

### 2. เตรียม Source Code

ภายใน Container สำหรับเรียน ให้คัดลอกหรือ Clone Repository ของชั้นเรียนโดยใช้ Placeholder ต่อไปนี้

```bash
git clone https://github.com/<GITHUB_USER>/<REPOSITORY>.git ~/labwork
cd ~/labwork/004_LAB_Connect_Them
```

### 3. สร้าง Image ที่ใช้ใน LAB

คำสั่งต่อไปนี้สร้าง API Image และ Web Image จาก Source Code ในโฟลเดอร์ปัจจุบัน ส่วน PostgreSQL ใช้ Image มาตรฐาน

```bash
docker pull postgres:17-alpine
docker build -t skillspace-api:lab4 ./api
docker build -t skillspace-web:lab4 ./web
```

กำหนดข้อมูลทดสอบที่ไม่ใช่ข้อมูลบัญชีจริง

```bash
export DB_NAME=skillspace DB_USER=labuser DB_PASSWORD=labpass
```

---

## การทดลองที่ 1 — สร้าง Network สำหรับระบบ

**คำถาม:** User-defined bridge network ที่สร้างขึ้นมี Driver และ DNS ภายในตามที่ระบบต้องใช้หรือไม่

**คำสั่งที่ 1**

```bash
docker network create devtools-connect-net
```

**คำสั่งที่ 2**

```bash
docker network inspect devtools-connect-net --format 'name={{.Name}} driver={{.Driver}} scope={{.Scope}}'
```

✅ **สิ่งที่ต้องสังเกตเพียงหนึ่งรายการ:** ผลลัพธ์เป็น `name=devtools-connect-net driver=bridge scope=local` แสดงว่า Network ถูกสร้างบน Docker Host ปัจจุบันและใช้ Driver ชนิด bridge

---

## การทดลองที่ 2 — เริ่ม Database โดยไม่ Publish Port

**คำถาม:** PostgreSQL ทำงานภายใน Network ได้โดยไม่เปิด Port `5432` ออกสู่ Host หรือไม่

**คำสั่งที่ 1**

```bash
docker run -d --name devtools-connect-db --network devtools-connect-net \
  -e POSTGRES_DB="$DB_NAME" -e POSTGRES_USER="$DB_USER" -e POSTGRES_PASSWORD="$DB_PASSWORD" \
  -v devtools-connect-pgdata:/var/lib/postgresql/data \
  -v "$PWD/db/initdb:/docker-entrypoint-initdb.d:ro" postgres:17-alpine
```

**คำสั่งที่ 2**

```bash
docker port devtools-connect-db
```

✅ **สิ่งที่ต้องสังเกตเพียงหนึ่งรายการ:** `docker port` ไม่คืนบรรทัดใด แสดงว่า Database ไม่มี Published Port และผ่าน Acceptance Criteria ของ NFR-3; ข้อความ `5432/tcp` ใน `docker ps` เป็นเพียง Port ที่ Image ระบุไว้ ไม่ใช่ Published Port

---

## การทดลองที่ 3 — ให้ API ค้นหา Database ด้วยชื่อ Container

`DATABASE_URL` คือ Environment Variable ที่รวม Protocol, ผู้ใช้, รหัสผ่าน, ชื่อ Host, Port และชื่อ Database สำหรับการเชื่อมต่อ ในคำสั่งนี้ Host คือ `devtools-connect-db` ไม่ใช่ IP address

**คำถาม:** API แปลงชื่อ Database ผ่าน DNS ภายในและ Query PostgreSQL ได้จริงหรือไม่

**คำสั่งที่ 1**

```bash
docker run -d --name devtools-connect-api --network devtools-connect-net \
  -e DATABASE_URL="postgresql://$DB_USER:$DB_PASSWORD@devtools-connect-db:5432/$DB_NAME" \
  skillspace-api:lab4
```

**คำสั่งที่ 2**

```bash
docker exec devtools-connect-api sh -lc 'getent hosts devtools-connect-db && python -c "import urllib.request; print(urllib.request.urlopen(\"http://localhost:8000/health\").read().decode())"'
```

✅ **สิ่งที่ต้องสังเกตเพียงหนึ่งรายการ:** ผลลัพธ์แสดง IP address ของ `devtools-connect-db` และตามด้วย `{"status":"ok","db":"up"}` จึงยืนยันทั้ง DNS และการ Query Database จริง

---

## การทดลองที่ 4 — เชื่อม Web กับ API และเปิด UI

`API_BASE_URL` คือ Environment Variable ที่ Web ใช้ระบุตำแหน่ง API การตั้งค่าเป็น `http://devtools-connect-api:8000` ทำให้ Web ติดต่อ API ผ่าน Network ภายใน ส่วน `-p 3000:3000` เปิดเฉพาะ UI ให้ Host เข้าถึง

**คำถาม:** Web เรียก API ด้วยชื่อ Container และ Render ข้อมูลจาก Database ได้ครบทุกหน้าหรือไม่

**คำสั่งที่ 1**

```bash
docker run -d --name devtools-connect-web --network devtools-connect-net \
  -p 3000:3000 -e API_BASE_URL="http://devtools-connect-api:8000" skillspace-web:lab4
```

**คำสั่งที่ 2**

```bash
for path in / /tickets /loans /parts; do curl -s -o /dev/null -w "$path HTTP %{http_code}\n" "http://localhost:3000$path"; done
```

✅ **สิ่งที่ต้องสังเกตเพียงหนึ่งรายการ:** ทั้งสี่ Path ตอบ `HTTP 200` แสดงว่าเส้นทาง Browser → Web → API → Database ทำงานครบสาย

## ขั้นตอนใช้งาน UI แบบไม่ขาดช่วง

เปิด `http://localhost:8254` บน Host ภาพต่อไปนี้มาจากการรันจริงด้วย Playwright CLI โดย Marker สีแดงระบุจุดคลิกและตัวเลขระบุลำดับ

### ขั้นที่ ① — ตรวจหน้าสรุปภาพรวม

คลิก **สรุปภาพรวม** ที่แถบนำทางด้านซ้าย แล้วอ่านค่าจากการ์ดสรุป

![ขั้นที่ 1 Marker ล้อมเมนูสรุปภาพรวม](./images/ui-net-01-overview.png)

*ภาพที่ 4 — UI แสดงงานที่ยังไม่ปิด 6 ใบ งานเกินกำหนด 2 ใบ ครุภัณฑ์ที่ถูกยืม 2 ชิ้น และอะไหล่ที่ต้องสั่งเพิ่ม 2 รายการ*

### ขั้นที่ ② — ตรวจหน้ากระดานงานซ่อม

คลิก **กระดานงานซ่อม** แล้วตรวจว่างานถูกแบ่งตามสถานะและแสดงผู้รับผิดชอบ

![ขั้นที่ 2 Marker ล้อมเมนูกระดานงานซ่อม](./images/ui-net-02-tickets.png)

*ภาพที่ 5 — กระดานแสดงใบแจ้งซ่อม 6 ใบที่ยังไม่ปิด พร้อมสถานะ ความเร่งด่วน และผู้รับผิดชอบ*

### ขั้นที่ ③ — ตรวจหน้ายืม-คืนครุภัณฑ์

คลิก **ยืม-คืนครุภัณฑ์** แล้วตรวจรายการที่ยังไม่คืน

![ขั้นที่ 3 Marker ล้อมเมนูยืม-คืนครุภัณฑ์](./images/ui-net-03-loans.png)

*ภาพที่ 6 — ตารางแสดงครุภัณฑ์ที่ยังไม่คืน 2 รายการ พร้อมผู้ยืม วันยืม และจำนวนวันที่ยืมแล้ว*

### ขั้นที่ ④ — ตรวจหน้าคลังอะไหล่

คลิก **คลังอะไหล่** แล้วตรวจรายการที่ต่ำกว่าจุดสั่งซื้อ

![ขั้นที่ 4 Marker ล้อมเมนูคลังอะไหล่](./images/ui-net-04-parts.png)

*ภาพที่ 7 — ตารางแสดงอะไหล่ต่ำกว่าจุดสั่งซื้อ 2 รายการ และแสดงยอดคงเหลือเทียบจุดสั่งซื้อ*

### ขั้นที่ ⑤ — กลับหน้าสรุปภาพรวม

คลิก **สรุปภาพรวม** อีกครั้งเพื่อยืนยันว่าการนำทางกลับสมบูรณ์

![ขั้นที่ 5 Marker ล้อมเมนูสรุปภาพรวมหลังกลับจากหน้าคลังอะไหล่](./images/ui-net-05-back.png)

*ภาพที่ 8 — หน้าสรุปกลับมาแสดงข้อมูลเดิม เนื่องจากขั้นตอนก่อนหน้าเป็นการอ่านข้อมูลและไม่ได้ส่งคำสั่งแก้ไข*

---

## การทดลองที่ 5 — ตรวจ Acceptance Criteria ทั้งระบบ

`verify.sh` เป็น Automated Verification Script หรือสคริปต์ตรวจรับอัตโนมัติ สคริปต์สร้างทรัพยากรชื่อขึ้นต้นด้วย `devtools-lab004-check-` และลบทรัพยากรของตนเองเมื่อจบ

**คำถาม:** ระบบผ่านเกณฑ์ DNS, API Health, UI และ NFR-3 ครบโดยไม่พึ่งการสังเกตด้วยสายตาเพียงอย่างเดียวหรือไม่

**คำสั่งที่ 1**

```bash
bash verify.sh
```

✅ **สิ่งที่ต้องสังเกตเพียงหนึ่งรายการ:** บรรทัดสุดท้ายเป็น `ALL CHECKS PASSED` และคำสั่งคืน Exit Code `0` ซึ่งหมายถึงทุก Assertion ผ่าน

## ตารางแก้ปัญหาที่พบบ่อย

| อาการหรือข้อความที่พบ | สาเหตุ | วิธีตรวจและแก้ไข |
|---|---|---|
| `network ... not found` | ชื่อ Network ไม่ตรง หรือยังไม่ได้สร้าง | ใช้ `docker network ls` ตรวจชื่อ แล้วสร้าง `devtools-connect-net` |
| `Name or service not known` | API และ Database ไม่ได้อยู่บน Network เดียวกัน | ใช้ `docker network inspect devtools-connect-net` ตรวจสมาชิก แล้วใช้ `docker network connect` หากจำเป็น |
| `/health` ตอบ `DB_DOWN` | Database ยังเริ่มทำงานไม่เสร็จ หรือ `DATABASE_URL` ไม่ถูกต้อง | ใช้ `docker logs devtools-connect-db` และตรวจชื่อ Host ใน `DATABASE_URL` |
| `port is already allocated` | มี Container อื่นใช้ Host Port `3000` | ใช้ `docker ps --filter publish=3000` หา Container ที่เกี่ยวข้อง แล้วเปลี่ยน Host Port หรือหยุด Container นั้น |
| UI แสดงว่าติดต่อบริการเบื้องหลังไม่ได้ | Web ค้นหาชื่อ API ไม่สำเร็จ | ตรวจว่า `API_BASE_URL=http://devtools-connect-api:8000` และทั้งสอง Container เป็นสมาชิก Network เดียวกัน |
| ลบ Network ไม่ได้และพบ `active endpoints` | ยังมี Container เชื่อมต่อกับ Network | ลบ Container ของ LAB ก่อน แล้วจึงลบ Network |

## ทำความสะอาดทรัพยากร

รันภายใน Container สำหรับเรียน

```bash
docker rm -f devtools-connect-web devtools-connect-api devtools-connect-db 2>/dev/null
docker network rm devtools-connect-net 2>/dev/null
docker volume rm devtools-connect-pgdata 2>/dev/null
```

ตรวจว่าไม่มี Container ของการทดลองค้างอยู่

```bash
docker ps -a --filter 'name=^devtools-connect-'
```

ออกจาก SSH แล้วลบ Container สำหรับเรียนบน Host

```bash
docker rm -f devtools-connect-lab
```

## สรุป

- User-defined bridge network มี DNS ภายใน จึงเชื่อมบริการด้วยชื่อ Container ได้
- IP address เป็นรายละเอียดขณะรันและอาจเปลี่ยน ไม่ควรบันทึกเป็นค่าคงที่ระหว่างบริการ
- Web เป็นบริการเดียวที่ต้องมี Published Port สำหรับ UI
- API และ Database ติดต่อกันภายใน Network; Database ที่ไม่มี Published Port ผ่าน Acceptance Criteria ของ NFR-3
- การตรวจด้วย `verify.sh` และ UI Walkthrough ทำให้ยืนยันผลได้ทั้งระดับโครงสร้างและสิ่งที่ผู้ใช้เห็น

*ผลลัพธ์อ้างอิงในเอกสารนี้มาจากการรันจริงบน Image `<DOCKER_USER>/devtools:2569_1`; เอกสารใช้ Placeholder แทนชื่อผู้ใช้และข้อมูลรับรองทั้งหมด*
