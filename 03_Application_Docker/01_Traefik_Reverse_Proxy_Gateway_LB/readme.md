# Reverse Proxy · API Gateway · Load Balancer — ด้วย Traefik

ชุดเรียนรู้ "ตัวกลางหน้าระบบ" แบบลงมือทำ เรียงจาก **ทำไมต้องมีตัวกลาง** ไปจนถึง
Reverse Proxy, Load Balancing, API Gateway middlewares, Canary/Mirroring และ Capstone
ที่รวมทุกบทบาทพร้อมโจทย์ debug ระหว่างทำให้ใช้วงจรนี้เป็นหลัก:

> **ทายผล → รัน → สังเกตหลักฐาน → อธิบายเหตุผล → ทดลองให้พัง → แก้กลับ**

ผู้เรียนต้องรู้ Docker พื้นฐานมาก่อน (image · container · compose · network · port mapping)
เท่านั้น — ไม่ต้องเคยใช้ Traefik หรือ proxy ใด ๆ มาก่อน

## ผลลัพธ์การเรียนรู้

เมื่อจบชุดนี้ ผู้เรียนควรอธิบายและทดลองให้เห็นได้ว่า:

- Reverse Proxy, Load Balancer และ API Gateway เป็น **"บทบาท" ที่ซ้อนทับกันได้** —
  Traefik ตัวเดียวเล่นได้ทั้งสามบท ขึ้นกับการประกอบ router + service + middleware
- reverse proxy ซ่อน backend ไว้หลังประตูเดียวอย่างไร และ `X-Forwarded-*` headers บอกอะไร
- round robin, sticky session (cookie) และ active health check แก้ปัญหาคนละจุดอย่างไร
  และ "container Up" ต่างจาก "server พร้อมรับงาน" ตรงไหน
- middlewares (`stripPrefix` · `basicAuth` · `headers` · `rateLimit`) เปลี่ยน reverse proxy
  ให้เป็น API gateway อย่างไร และเหตุใด middleware ที่ประกาศแล้วแต่ไม่ถูก attach จึงไม่มีผล
- weighted round robin (canary 90:10) กับ traffic mirroring ต่างกันอย่างไร และทำไมต้องประกาศ
  ผ่าน **file provider** ไม่ใช่ labels
- จะใช้ Traefik dashboard + `docker compose logs traefik` ไล่หาสาเหตุ 404 / 401 / 429 / 502 อย่างไร

## เปิดสไลด์

เปิด [`Traefik_Proxy_Gateway_LB_Slides.html`](./Traefik_Proxy_Gateway_LB_Slides.html)
ในเบราว์เซอร์ได้โดยตรง ไม่ต้องใช้ web server และไม่โหลด CDN:

- `←` / `→` หรือ `Space` — เปลี่ยนสไลด์
- `O` — overview และคลิกเพื่อกระโดดไปสไลด์ที่ต้องการ
- `F` — เต็มจอ
- `?` — ดูปุ่มลัด
- `Ctrl+P` — บันทึกเป็น PDF 16:9

## เตรียมเครื่องเรียนครั้งเดียว

คำสั่งชุดนี้รันบน **เครื่องของผู้เรียน** เพื่อเปิด container `devtools` แบบไม่ลบงานเก่า:

```bash
docker start devtools 2>/dev/null || \
  docker run -dit --name devtools --privileged \
  -p 2222:22 tuchsanai/devtools:2569_1
ssh root@localhost -p 2222        # password: passwd
```

> `docker start ... || docker run ...` หมายถึง "มีเครื่องเดิมให้เปิดต่อ; ยังไม่มีจึงค่อยสร้าง"
> ทำให้ clone จาก LAB ก่อนหน้าไม่หาย ส่วน `--privileged` ใช้เฉพาะ disposable classroom
> container เพื่อรัน Docker-in-Docker ไม่ใช่แนวทาง production

จากนั้นใช้ VS Code **Remote-SSH** ต่อ `root@localhost:2222` แล้วรันคำสั่งที่เหลือ
ข้างในเครื่องเรียน ตรวจว่า Docker พร้อม:

```bash
docker --version
docker info --format 'Docker daemon: {{.ServerVersion}}'
```

✅ ได้เลขเวอร์ชันทั้งสองบรรทัดและไม่มี `Cannot connect to the Docker daemon`

## Clone โค้ดครั้งเดียว

รันข้างในเครื่องเรียน:

```bash
mkdir -p ~/labwork && cd ~/labwork
git clone https://github.com/Tuchsanai/DevTools.git
cd DevTools/03_Application_Docker/01_Traefik_Reverse_Proxy_Gateway_LB
```

## แล็บทั้ง 5 (ทำเรียงตามลำดับ)

ทุกแล็บ pin image ชุดเดียวกัน: `traefik:v3.7.4` และ `traefik/whoami:v1.11` (LAB 2 และ 5
มีแอป Python stdlib ที่ build เองเพิ่ม) · Traefik เปิด entrypoint `web` ที่ `8000:80` และ dashboard ที่ `8080:8080`
เหมือนกันทุกแล็บ — จึงต้อง **`docker compose down` ก่อนย้ายไปแล็บถัดไปเสมอ**

| แล็บ | โฟลเดอร์ | บทบาทที่เล่น | ไฮไลต์ |
|---|---|---|---|
| 1 | [`001_LAB_Traefik_Reverse_Proxy`](./001_LAB_Traefik_Reverse_Proxy/) | Reverse Proxy | PathPrefix · backend ไม่ publish port · `X-Forwarded-*` · dashboard |
| 2 | [`002_LAB_Load_Balancing`](./002_LAB_Load_Balancing/) | Load Balancer | `--scale app=3` · หน้าเว็บโชว์ round robin เป็นแถบสี · sticky cookie · health check ป่วยแต่ไม่ตาย |
| 3 | [`003_LAB_API_Gateway_Middlewares`](./003_LAB_API_Gateway_Middlewares/) | API Gateway | stripPrefix · basicAuth (`$$`) · headers · rateLimit เห็น 429 จริง |
| 4 | [`004_LAB_Canary_Mirroring`](./004_LAB_Canary_Mirroring/) | Deploy patterns | weighted 9:1 → แก้ไฟล์เป็น 5:5 แบบ hot reload · mirror 10% · file provider |
| 5 | [`005_LAB_Gateway_Capstone`](./005_LAB_Gateway_Capstone/) | ทั้งสามบทบาท | Mini API Platform + บั๊กซ่อน 3 จุด · `check.sh` ตรวจ 4 ข้อ · หน้า live dashboard |

การเปิดหน้าเว็บ/dashboard ของทุกแล็บทำผ่าน VS Code Remote-SSH port forwarding
(port `8000` และ `8080`) เหมือนที่แต่ละ readme อธิบายไว้

## เก็บกวาดท้ายคาบ

ข้างในเครื่องเรียน — `cd` เข้าโฟลเดอร์แล็บที่กำลังรันอยู่ก่อน แล้วปิด stack:

```bash
cd ~/labwork/DevTools/03_Application_Docker/01_Traefik_Reverse_Proxy_Gateway_LB/<โฟลเดอร์แล็บ>
docker compose down
docker compose ps -a     # ต้องเหลือแค่หัวตาราง (container อื่นนอกแล็บไม่เกี่ยว)
```

บนเครื่องของเรา — จะเก็บ `devtools` ไว้ใช้คาบต่อไป (`docker stop devtools`)
หรือลบทิ้ง (`docker rm -f devtools`) ก็ได้

---

*Expected output และ screenshot ทั้งหมดในชุดนี้มาจากการรันจริงบน `tuchsanai/devtools:2569_1`*
