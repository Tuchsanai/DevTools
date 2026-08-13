# LAB 5 — Docker Compose : แอปโหวต Cats vs Dogs ทั้งระบบในคำสั่งเดียว (⏱ ~20 นาที)

> โฟลเดอร์ `005_LAB_Docker_Compose_Voting` — คู่กับสไลด์ `new_Docker_Week11_Slides.html` Section 5
> ไฟล์ในแล็บ : `docker-compose.yml` · `vote/` · `result/` · `verify.sh`

**เป้าหมาย:** อ่าน `docker-compose.yml` ออกทุก key · เปิด 3 services ด้วยคำสั่งเดียว · เห็น `healthcheck`+`depends_on` บังคับลำดับจริง · พิสูจน์ `down` vs `down -v` ด้วยคะแนนโหวต

> **ทายก่อนเริ่ม:** `docker compose down` ลบ container ทั้งหมดทิ้ง แล้ว `up` ใหม่ — คะแนนโหวตจะหายไหม? ข้อ 6–7 พิสูจน์

---

## 0. เตรียมเครื่องเรียน

```bash
docker start devtools 2>/dev/null || \
  docker run -dit --name devtools --privileged -p 2222:22 tuchsanai/devtools:2569_1
ssh root@localhost -p 2222        # password : passwd
docker compose version
```

✅ เห็นเลขเวอร์ชัน Compose (สังเกต: `docker compose` เว้นวรรค — ปลั๊กอิน v2 ไม่ใช่ `docker-compose` ขีดกลางรุ่นเก่า)

## 1. Clone แล้วทัวร์โปรเจกต์

```bash
mkdir -p ~/labwork && cd ~/labwork
git clone https://github.com/Tuchsanai/DevTools.git 2>/dev/null
cd DevTools/03_Docker/04_Docker/005_LAB_Docker_Compose_Voting
cat docker-compose.yml
```

สถาปัตยกรรม: **3 services** (`vote` :8085 · `result` :8086 · `redis` ไม่ map port) · **2 networks** (`front-tier` โลกภายนอก / `back-tier` หลังบ้าน) · **1 volume** (`vote-data` — คะแนนตัวจริงนอนที่นี่)

> 📝 **อ่านทีละ key:** `build: ./vote` = build จาก Dockerfile ของเรา (ส่วน `image: redis:7-alpine` = ใช้ของสำเร็จรูป) · `ports:` คือ `-p` เดิมในรูป YAML · `environment: REDIS_HOST: redis` — ชี้ host ด้วย**ชื่อ service** ได้เพราะ Embedded DNS จาก LAB 4 · `depends_on: condition: service_healthy` = รอ redis **พร้อมจริง** ไม่ใช่แค่สตาร์ต · `healthcheck:` รัน `redis-cli ping` ทุก 5 วิ · `volumes: vote-data:/data` เก็บข้อมูล redis นอกตัว container · ไฟล์นี้**ไม่มีบรรทัด `version:`** — compose ยุคใหม่เลิกใช้แล้ว

> `vote/Dockerfile` โครงเดียวกับ LAB 1 เป๊ะ — compose ไม่ได้แทนความรู้เดิม แค่เลิกพิมพ์ flag เอง

## 2. เปิดทั้งระบบด้วยคำสั่งเดียว

```bash
docker compose up -d --build
```

✅ ยาวมาก — จุดที่ต้องจ้องคือ**ลำดับช่วงท้าย**: redis ต้องผ่านด่าน `Healthy` ก่อน vote/result ถึงเริ่ม `Starting`:

```
 Container ...-redis-1   Started
 Container ...-redis-1   Waiting
 Container ...-redis-1   Healthy    ← ผ่าน healthcheck ก่อน
 Container ...-vote-1    Starting   ← เว็บค่อยเปิดตาม
 Container ...-result-1  Starting
```

```bash
docker compose ps
```

✅ 3 ตัว `Up` ครบ — redis มีคำว่า **`(healthy)`** และ map port เฉพาะ vote/result · ชื่อ container = `<โปรเจกต์>-<service>-<ลำดับ>` (โปรเจกต์ = ชื่อโฟลเดอร์) — compose ตั้งให้เองทั้งหมด

## 3. เล่นจริง — โหวต 2 แท็บ

Forward port `8085` และ `8086` (VS Code แท็บ PORTS → Forward a Port ทีละพอร์ต) แล้วเปิด 2 แท็บ:
`http://localhost:8085` (หน้าโหวต) · `http://localhost:8086` (ผลคะแนนสด อัปเดตเองทุก ~2 วิ)

**ภารกิจ:** กด **CATS 6 ครั้ง** และ **DOGS 4 ครั้ง** — ดูแท่งคะแนนฝั่ง result ขยับโดยไม่ต้อง refresh

ตรวจตัวเลขดิบจาก terminal:

```bash
curl -s http://localhost:8086/data
```

✅ ตรงกับที่กด:

```
{
  "cats": 6,
  "dogs": 4
}
```

> 📝 เบื้องหลัง: ปุ่ม → POST หา `vote` → `INCR votes:cats` ใน **redis** → `result` อ่านมาวาดแท่ง · ทั้งคู่ต่อ redis ด้วยชื่อ `redis` เฉย ๆ — **ไม่มี IP สักตัวในโค้ด**

## 4. แอบดูในฐานข้อมูล

```bash
docker compose exec redis redis-cli GET votes:cats
```

✅ ตอบ `6` — เว็บทั้งสองเป็นแค่ "หน้ากาก" ของข้อมูลใน redis (`compose exec <service>` = `docker exec` เวอร์ชันเรียกด้วยชื่อ service ไม่ต้องจำชื่อ container จริง)

## 5. ตรวจงานด้วย verify.sh

รันจากโฟลเดอร์แล็บ **ตอนที่ระบบยังเปิดอยู่และโหวตแล้ว**:

```bash
bash verify.sh
```

✅ ทุกข้อ `PASS` จบด้วย `ALL CHECKS PASSED` (exit 0)

## 6. พิสูจน์พลัง volume — คะแนนรอด `down`

```bash
docker compose down
docker volume ls
docker compose up -d
sleep 8 && curl -s http://localhost:8086/data
```

✅ `down` ลบ container + network หมด แต่ **ไม่มีบรรทัด Volume ใน output** — `vote-data` ยังอยู่ใน `volume ls` · `up` รอบใหม่ (ไม่ต้อง `--build` — image มีแล้ว) แล้วคะแนน **6 : 4 กลับมาครบ** เพราะ redis ตัวใหม่ mount volume ลูกเดิม อ่านไฟล์ AOF เดิม

## 7. `down -v` = ลบข้อมูลจริง

```bash
docker compose down -v
docker compose up -d
sleep 8 && curl -s http://localhost:8086/data
```

✅ รอบนี้มีบรรทัด `Volume ..._vote-data Removed` แล้วคะแนนกลายเป็น `{"cats": 0, "dogs": 0}` — โลกใหม่ไร้ความทรงจำ

| คำสั่ง | Container | Network | Volume (ข้อมูล) |
|---|---|---|---|
| `compose stop` | หยุด (ยังอยู่) | อยู่ | อยู่ |
| `compose down` | **ลบ** | **ลบ** | อยู่ |
| `compose down -v` | **ลบ** | **ลบ** | **ลบ** |

## 8. โบนัส : `compose watch` — แก้โค้ดเห็นผลใน ~2 วิ

Terminal 1 (ค้างไว้):

```bash
docker compose up --watch
```

Terminal 2 (ssh เข้าอีก session):

```bash
cd ~/labwork/DevTools/03_Docker/04_Docker/005_LAB_Docker_Compose_Voting
sed -i 's|โหวตทีมโปรดของคุณ — เปลี่ยนใจโหวตใหม่ได้เสมอ|แก้โค้ดสด ๆ ผ่าน compose watch ⚡|' vote/app.py
curl -s http://localhost:8085 | grep -o 'compose watch ⚡'
```

✅ ฝั่ง T1 ขึ้น `Syncing service "vote"...` → Flask reload → curl เจอข้อความใหม่ **โดยไม่ build ไม่ restart เอง** · เสร็จแล้ว: T1 กด `Ctrl+C` และแก้ไฟล์กลับ (สลับ เก่า/ใหม่ ใน `sed`)

## 9. ล้างกระดาน

```bash
docker compose down -v --rmi local
docker ps -a && docker volume ls && docker network ls
```

✅ Container / Image (vote,result) / Volume / Network ถูก `Removed` ครบ — เหลือเฉพาะ `redis:7-alpine` ที่ pull มา (ลบได้ด้วย `docker rmi redis:7-alpine`) · ปิด forward port `8085`/`8086` ด้วย

---

## ปัญหาที่พบบ่อย

| อาการ | สาเหตุ | วิธีแก้ |
|---|---|---|
| `no configuration file provided: not found` | สั่ง `docker compose` นอกโฟลเดอร์ที่มี `docker-compose.yml` | `cd` เข้าโฟลเดอร์แล็บก่อนเสมอ |
| `up` ค้างที่ `redis-1 Waiting` แล้วล้ม | redis ไม่ผ่าน healthcheck | `docker compose logs redis` หา error — vote/result จะไม่เปิดจนกว่า redis จะ healthy (หน้าที่ของ `service_healthy`) |
| `port is already allocated` ตอน `up` | container แล็บก่อนยังจอง 8085/8086 | `docker ps` หาตัวจอง แล้ว `docker rm -f` หรือ `compose down` โปรเจกต์นั้น |

*ผลลัพธ์ทั้งหมดมาจากการรันจริงในเครื่องเรียน `tuchsanai/devtools:2569_1` (Docker 29.6.2 · Compose v5.3.1)*
