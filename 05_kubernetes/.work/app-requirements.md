# ข้อกำหนดแอปตัวอย่าง `05_kubernetes/app/` (yolo1 ออกแบบ · ผู้สร้างแอปต้องทำให้ครบทุกข้อ)

ต้นแบบ: `/root/workspace/DevTools/02_Docker/03_Fullstack_App_Example/002_LAB_Fullstack_Compose/` (SkillSpace)
**ยกโครงจากต้นแบบมาแล้วปรับ** อย่าเขียนใหม่จากศูนย์ · UI/สี/องค์ประกอบของต้นแบบดีอยู่แล้ว ให้คงไว้ · เพิ่มเฉพาะสิ่งที่การสอน Kubernetes ต้องใช้
อ่านคู่กับ `.work/lab-outline.md` (จะเห็นว่าแต่ละ feature ถูกใช้ในแล็บไหน)

## 0. โครงที่ต้องได้
```
05_kubernetes/app/
├── README.md            วิธี build/ทดสอบ 20-40 บรรทัด (ภาษาไทย)
├── build-images.sh      build 4 image ตามชื่อ/tag ข้างล่าง (รันจากโฟลเดอร์นี้ ไม่ต้องมี argument)
├── compose.yaml         ทดสอบแอปทั้งชุดบน Docker Compose (WEB_PORT default 3000)
├── web/                 Next.js (App Router) + TypeScript + Tailwind — standalone build
├── api/                 FastAPI + psycopg
├── db/                  PostgreSQL 17 + initdb (schema + seed จากต้นแบบ)
└── k8s-reference/       manifest อ้างอิงระบบครบ (ใช้ทดสอบว่าขึ้นบน kind ได้จริง — ไม่ใช่ของสอน)
```
image ที่ต้องได้ (ชื่อ/tag ต้องตรงนี้เป๊ะ):
| image | ที่มา | หมายเหตุ |
|---|---|---|
| `k8s-lab-web:v1` | web/ | `--build-arg APP_VERSION=v1 --build-arg DEFAULT_THEME=blue` |
| `k8s-lab-web:v2` | web/ (โค้ดเดียวกัน) | `--build-arg APP_VERSION=v2 --build-arg DEFAULT_THEME=emerald` — **หน้าตาต่างจาก v1 ชัดเจนโดยไม่ต้องตั้ง env ใด ๆ** |
| `k8s-lab-api:v1` | api/ | |
| `k8s-lab-db:v1` | db/ | postgres:17-alpine + initdb |

## 1. web (Next.js 16 App Router · TypeScript · Tailwind 4)
### 1.1 ค่าที่อ่าน "ตอนรัน" (runtime env — ห้ามใช้ NEXT_PUBLIC_* สำหรับค่าเหล่านี้)
| env | ค่าเริ่มต้น | ใช้ในแล็บ |
|---|---|---|
| `SITE_NAME` | `SkillSpace` | 010 (ConfigMap) |
| `THEME` | ค่าจาก `DEFAULT_THEME` ของ image (v1=blue, v2=emerald) | 010 · รองรับอย่างน้อย `blue emerald amber rose violet slate` |
| `API_BASE_URL` | ไม่ตั้ง = **โหมดเดี่ยว** (standalone) | 003-007 ไม่ตั้ง · 008+ ตั้งเป็น `http://api:8000` |
| `POD_NAME` | ถ้าไม่ตั้ง ใช้ `os.hostname()` (= ชื่อ Pod อยู่แล้ว) | ทุกแล็บ |
| `NODE_NAME` | ไม่บังคับ แสดงถ้ามี | - |
| `APP_VERSION` | จาก build-arg (v1/v2) ฝังใน image | 004 007 018 |
| `PORT` | 3000 | |
- ทุกหน้าเป็น server component + `export const dynamic = "force-dynamic"` · fetch ไป api ใส่ `cache: "no-store"` และ timeout สั้น (≤ 2 วินาที) เพื่อให้หน้าโหลดเร็วแม้ api ล่ม
- ธีมต้องทำด้วย CSS variables / `data-theme` ที่มี CSS เตรียมไว้ทุกธีม **ห้าม** ประกอบชื่อคลาส Tailwind แบบ dynamic (จะถูก purge)

### 1.2 แถบ/การ์ดสถานะ (หัวใจของการสอน — ต้องมีทุกหน้า มองเห็นทันทีไม่ต้องเลื่อน)
แสดง 3 แถวเสมอ:
1. **web** — `ตอบโดย Pod: <POD_NAME>` · ป้ายเวอร์ชัน `v1`/`v2` (ใหญ่ ชัด สีตามธีม) · เวลาที่ตอบ `HH:MM:SS` (Asia/Bangkok) · ธีม/ชื่อระบบปัจจุบัน
2. **api** — ถ้า `API_BASE_URL` ไม่ตั้ง: "โหมดเดี่ยว — ยังไม่ได้เชื่อม API" (สีเทา) · ถ้าตั้งแล้วเรียกไม่ได้: "เชื่อมต่อไม่ได้" (แดง) + ข้อความ error สั้น · ถ้าได้: "เชื่อมต่อได้ · Pod: <ชื่อ Pod api>" (เขียว) — ชื่อ Pod api อ่านจาก header `X-Pod-Name` หรือ JSON ของ `/ready`
3. **db** — จากผล `GET {API_BASE_URL}/ready`: `up` (เขียว) / `down` (แดง + error สั้น) / `unknown` (เทา เมื่อ api ไม่ตอบ)
- ทั้ง 3 แถวต้องอัปเดตทุกครั้งที่รีเฟรช (ไม่ cache) เพื่อให้เห็นชื่อ Pod สลับเมื่อมีหลาย replica

### 1.3 โหมดเดี่ยว (standalone) — ครั้งที่ 1 ใช้ web ตัวเดียวโดยไม่มี api/db
- ถ้า api ไม่ตั้ง/ไม่ตอบ/db ล่ม หน้าเว็บ **ต้องไม่ error/ไม่ 500** · แผงข้อมูล (dashboard, tickets, loans, parts) แสดงสถานะ "รอเชื่อมต่อ API" หรือ "ฐานข้อมูลยังไม่พร้อม" อย่างสวยงามแทนตัวเลข · เมนูนำทางยังใช้ได้
- ฟอร์ม (สร้างใบแจ้งซ่อม ฯลฯ) เมื่อ api ล่ม ให้แจ้ง error ที่อ่านรู้เรื่อง ไม่ crash

### 1.4 endpoint ของ web (route handlers) — **ห้ามอยู่ใต้ `/api/*`** (path นั้นสงวนให้ Ingress ส่งไป api)
| path | พฤติกรรม |
|---|---|
| `GET /healthz` | 200 `{"status":"ok","pod":..,"version":..}` เสมอเมื่อ process ทำงาน |
| `GET /readyz` | 200 ถ้าโหมดเดี่ยว หรือ api `/health` ตอบ 200 · ไม่งั้น 503 |
| `GET /info` | JSON: `{pod, version, theme, site_name, time, node?, api:{configured, reachable, pod?, error?}, db:{status: up/down/unknown}}` — ใช้ใน `curl` loop ของแล็บ 006/018/021 |

### 1.5 หน้าตา
- คง UI ของต้นแบบ (dashboard, กระดานงานซ่อม, ยืม-คืน, คลังอะไหล่) · v1 = ธีมน้ำเงินป้าย v1 · v2 = ธีมเขียวมรกตป้าย v2 ต่างกันจนเห็นใน screenshot ย่อ
- ต้องสวยพอขึ้นสไลด์ (การ์ด ตาราง badge สีสื่อความหมาย ตามต้นแบบ)

## 2. api (FastAPI)
- ยก endpoint ธุรกิจทั้งหมดจากต้นแบบ (`/api/assets` `/api/tickets` `/api/loans` `/api/parts` `/api/dashboard` ...) ไม่ต้องเปลี่ยน
- env: รองรับทั้ง `DATABASE_URL` และแบบแยกส่วน `DB_HOST DB_PORT DB_NAME DB_USER DB_PASSWORD` (แบบแยกส่วนสำคัญกว่า เพราะแล็บ 011 ส่ง `DB_PASSWORD` จาก Secret) · `APP_VERSION` (default v1)
- **ห้าม exit เมื่อ db ไม่พร้อม** ตอนเริ่ม (ต้นแบบมี wait_for_db ที่ล้มแล้วออก — เปลี่ยนเป็นแค่ log แล้วเปิดให้บริการต่อ) เพราะแล็บ 008/015 รัน api โดยไม่มี db
- endpoint ใหม่:
| path | พฤติกรรม |
|---|---|
| `GET /health` | ตอบตัวเอง 200 `{"status":"ok","pod":..,"version":..}` **ไม่แตะ db** · ถ้าถูกสั่งป่วย (ข้างล่าง) ตอบ 503 |
| `GET /ready` | `SELECT 1` เข้า db จริง → 200 `{"status":"ready","db":"up","pod":..}` · ล้มเหลว → 503 `{"status":"not-ready","db":"down","error":"<สั้น>","pod":..}` |
| `POST /debug/health` body `{"ok": false}` / `{"ok": true}` | สลับให้ `/health` ตอบ 503/200 (เก็บใน memory ของ process — restart แล้วหาย) ใช้สอน liveness ในแล็บ 014 |
| `GET /api/health` `GET /api/ready` `GET /api/whoami` | alias สำหรับเรียกผ่าน Ingress path `/api` (`whoami` → `{pod, version, time}`) |
- **ทุก response** ใส่ header `X-Pod-Name: <hostname>` (middleware)
- log ทุก request หนึ่งบรรทัด (method path status) ให้ `kubectl logs` อ่านรู้เรื่อง

## 3. db
- `postgres:17-alpine` + `initdb/01-schema.sql` `02-seed.sql` จากต้นแบบ · env มาตรฐาน `POSTGRES_DB POSTGRES_USER POSTGRES_PASSWORD`
- ต้องรันได้ทั้งแบบไม่มี volume, emptyDir, และ PVC ที่ mount `/var/lib/postgresql/data` โดยตั้ง `PGDATA=/var/lib/postgresql/data/pgdata` (ทดสอบทั้ง 3 แบบใน k8s-reference)

## 4. compose.yaml + build-images.sh
- `compose.yaml` ขึ้นระบบครบด้วยคำสั่งเดียว (ใช้ image ที่ build แล้ว หรือ build จาก context ก็ได้) · web publish `${WEB_PORT:-3000}:3000`
- `build-images.sh` : build 4 image (v2 ใช้ build-arg) และพิมพ์ `docker images | grep k8s-lab` ตอนจบ · ต้องรันได้ในเครื่องเรียน (`tuchsanai/devtools-k8s:2569_1`) โดยไม่ต้องติดตั้งอะไรเพิ่ม · เวลา build รวมไม่ควรเกิน ~5 นาทีบนเครื่องปกติ

## 5. k8s-reference/ (ทดสอบบน kind จริง — ต้องผ่านก่อนส่ง)
manifest ชุดอ้างอิงใน namespace `k8s-lab-ref`: ConfigMap · Secret · PVC · Deployment+Service ของ db/api/web (web 3 replica, api 2) · readiness/liveness ของ api · Ingress path `/`→web `/api`→api (ไม่ใส่ host) · `imagePullPolicy: IfNotPresent` ทุกที่
ต้องพิสูจน์บน cluster (`k8s-bootstrap` ใน container ของตัวเอง ตาม `.work/worker-env.md`) ว่า:
1. `curl localhost:80/info` ผ่าน Ingress หลายครั้ง → `.pod` สลับครบ 3 ชื่อ
2. `curl localhost:80/api/whoami` → JSON จาก api (Ingress path ทำงาน)
3. หน้าเว็บผ่าน Ingress แสดงการ์ดสถานะเขียวทั้ง 3 แถว และ dashboard มีข้อมูล seed (screenshot ด้วย `shot.js` เก็บไว้ที่ `.work/app-screens/`)
4. web ตัวเดียวแบบไม่มี api (`kubectl run` ธรรมดา + port-forward) เปิดหน้าเว็บได้ ไม่ error การ์ดสถานะบอกโหมดเดี่ยว (screenshot)
5. `kubectl scale deploy db --replicas=0` → api `/ready` 503 → Pod api READY 0/1 → endpoints ว่าง → หน้าเว็บบอก api ไม่พร้อม/db down · scale กลับ → หาย
6. `POST /debug/health {"ok":false}` → api ถูก liveness restart (RESTARTS +1) ภายใน ~30-60 วิ
7. ConfigMap เปลี่ยน SITE_NAME/THEME + rollout restart → หน้าเว็บเปลี่ยน (screenshot)
8. `kubectl set image` web v1→v2 → หน้าเว็บเปลี่ยนธีม/ป้าย (screenshot v1 และ v2 คู่กัน)
9. เพิ่มใบแจ้งซ่อมผ่านหน้าเว็บ → ลบ Pod db → ข้อมูลยังอยู่ (PVC)
10. build ซ้ำจากสภาพสะอาด (`docker rmi` แล้ว `./build-images.sh`) ผ่าน

## 6. กติกา
- ไม่มี CDN/ฟอนต์ออนไลน์ (เครื่องเรียนอาจไม่มีเน็ตตอนสอน) · Tailwind build ในเครื่อง
- ไม่ใส่ email/ชื่อจริง/token ในโค้ด/seed/README (seed ของต้นแบบใช้ชื่อสมมุติอยู่แล้ว)
- image ต้องเล็กพอ (web standalone, api slim, db alpine) และ pin base image tag
- ลบ container/volume/cluster ทดสอบทั้งหมดก่อนส่งงาน (`docker rm -f devtools-k8s-app`)
- รายงานผลตรง ๆ ข้อไหนทำไม่ได้ให้บอก ห้ามกลบ
