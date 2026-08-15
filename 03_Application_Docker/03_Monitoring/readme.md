# Monitoring — Prometheus · PromQL · Grafana · Alertmanager

ชุดเรียนรู้ "ทำให้ระบบบอกอาการของตัวเองได้" แบบลงมือทำ เรียงจาก **ตัวเลขหนึ่งบรรทัดมาจากไหน**
ไปจนถึง dashboard ที่เฝ้าได้จริง และ alert ที่ยิงถึงปลายทางจริง โดยใช้วงจรนี้เป็นหลัก:

> **ทายผล → รัน → สังเกตหลักฐาน → อธิบายเหตุผล → ทดลองให้พัง → แก้กลับ**

ผู้เรียนต้องรู้ Docker พื้นฐานมาก่อน (image · container · compose · network · volume · port mapping)
เท่านั้น — ไม่ต้องเคยใช้ Prometheus, PromQL หรือ Grafana มาก่อน

## ผลลัพธ์การเรียนรู้

เมื่อจบชุดนี้ ผู้เรียนควรอธิบายและทดลองให้เห็นได้ว่า:

- metric หนึ่งบรรทัดประกอบด้วยอะไร และทำไม **1 ชุด label = 1 time series** จึงเป็นทั้งพลังและกับดัก
- Prometheus ใช้ **pull model** อย่างไร ทำไมจึงได้ metric `up` มาฟรี ๆ และ exporter ต่างจากตัวส่งข้อมูลอย่างไร
- ทำไม counter ต้องผ่าน `rate()` เสมอ · กฎ **หน้าต่าง ≥ 4 × `scrape_interval`** มาจากไหน · และทำไมต้อง `rate()` ก่อน `sum()`
- อ่าน histogram ออก — `_bucket` / `_sum` / `_count` / `le` ต่างกันอย่างไร และทำไม **p95 เป็นค่าประมาณ** ที่ดีกว่าค่าเฉลี่ย
- cAdvisor ให้ตัวเลขระดับ container ได้อย่างไร และทำไมถึงต้องกรอง `{name!=""}` ทุกครั้ง
- ทำ **dashboard as code** ด้วย Grafana provisioning และไล่ปัญหา `Datasource not found` ที่เกิดจาก `uid` ไม่ตรงได้
- ติดตัววัดในแอปของตัวเองด้วย client library แล้ววัด **RED** (Rate · Errors · Duration) ได้ครบ
- อธิบายได้ว่า **cardinality ระเบิด** เกิดจากอะไรและทำไมมันถึงฆ่า Prometheus ได้ทั้งตัว
- เขียน alert rule ที่มี `for:` · แยกงานของ Prometheus ออกจาก Alertmanager · ใช้ silence และ inhibition เป็น
- ไล่หาสาเหตุจาก "อาการ" ไปยัง "ชั้นที่พัง" ได้ — ชั้นเก็บข้อมูล · ชั้นแสดงผล · ชั้นแจ้งเตือน

## เปิดสไลด์

เปิด [`Monitoring_Prometheus_Grafana_Slides.html`](./Monitoring_Prometheus_Grafana_Slides.html)
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
> ทำให้ clone จากแล็บก่อนหน้าไม่หาย ส่วน `--privileged` ใช้เฉพาะ disposable classroom
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
cd DevTools/03_Application_Docker/03_Monitoring
```

## แล็บทั้ง 6 (ทำเรียงตามลำดับ)

| แล็บ | โฟลเดอร์ | เรียนเรื่อง | ไฮไลต์ |
|---|---|---|---|
| 1 | [`001_LAB_Prometheus_First_Scrape`](./001_LAB_Prometheus_First_Scrape/) | pull model · scrape · PromQL ชุดแรก | อ่าน `/metrics` ดิบ · หน้า `/targets` · ตั้ง target เป็น `localhost` แล้ว DOWN · hot reload ด้วย `POST /-/reload` |
| 2 | [`002_LAB_Container_Metrics_cAdvisor`](./002_LAB_Container_Metrics_cAdvisor/) | ตัวเลขระดับ container | รัน cAdvisor แบบผิดจน label `name=` หาย แล้วแก้ · `rate()` = จำนวน core · กับดัก `{name!=""}` |
| 3 | [`003_LAB_Grafana_Dashboard_As_Code`](./003_LAB_Grafana_Dashboard_As_Code/) | Grafana + provisioning | datasource/dashboard เป็นไฟล์ · variable · threshold · พัง `Datasource not found` แล้วแก้ · `down -v` แล้ว dashboard ยังอยู่ |
| 4 | [`004_LAB_App_Instrumentation_RED`](./004_LAB_App_Instrumentation_RED/) | ติดตัววัดในแอปเอง | Counter/Gauge/Histogram · RED · `histogram_quantile` p95 · ทำ cardinality ระเบิดจริงแล้วแก้ |
| 5 | [`005_LAB_Alerting_Alertmanager`](./005_LAB_Alerting_Alertmanager/) | alert ที่ใช้งานได้จริง | Inactive → Pending → Firing → Resolved · webhook receiver พร้อมหน้าเว็บ · silence · inhibition · `promtool check rules` |
| 6 | [`006_LAB_Observability_Capstone`](./006_LAB_Observability_Capstone/) | ประกอบทุกอย่าง | stack เต็ม + บั๊กซ่อน 3 จุดคนละชั้น · `check.sh` ตรวจ 5 ข้อ |

## ชุดเวอร์ชันที่ใช้ (pin ทุกตัว)

| บทบาท | image |
|---|---|
| Prometheus | `prom/prometheus:v3.7.3` |
| Node exporter | `prom/node-exporter:v1.10.2` |
| cAdvisor | `ghcr.io/google/cadvisor:v0.57.0` |
| Alertmanager | `prom/alertmanager:v0.29.0` |
| Grafana | `grafana/grafana:12.3.1` |
| แอป / load generator / receiver | `python:3.13-alpine` |

> ทุกแล็บ pin tag ไว้ทั้งหมด ไม่มีการใช้ `latest` เพื่อให้ผลที่เห็นตรงกับเอกสารและภาพประกอบ

## Port ที่ใช้ (ตรงกันทุกแล็บ)

| port | บริการ | ใช้ในแล็บ |
|---|---|---|
| 9090 | Prometheus | 1 – 6 |
| 9100 | node-exporter | 1, 2, 3, 5, 6 |
| 8080 | cAdvisor | 2, 3, 6 |
| 3000 | Grafana | 3, 4, 5, 6 |
| 9093 | Alertmanager | 5, 6 |
| 8000 | แอปตัวอย่าง | 4, 5, 6 |
| 5001 | webhook receiver + หน้าเว็บ | 5, 6 |

⚠️ ทุกแล็บใช้ port ชุดเดียวกัน จึงต้อง **`docker compose down` ของแล็บเดิมก่อนขึ้นแล็บถัดไปเสมอ**

การเปิดหน้าเว็บทั้งหมด (Prometheus · Grafana · Alertmanager · cAdvisor · receiver) ทำผ่าน
VS Code Remote-SSH port forwarding เหมือนที่แต่ละ readme อธิบายไว้

## ข้อควรทราบเรื่องสภาพแวดล้อม

- **`mem_limit:` และ `cpus:` ใช้ไม่ได้ในกล่องเรียนที่ซ้อน container หลายชั้น** — จะพร้อม error
  `cannot enter cgroupv2 "/sys/fs/cgroup/docker" with domain controllers -- it is in threaded mode`
  ชุดนี้จึงเลี่ยงไปใช้ `cpuset:` (ปักหมุด core) ในการสาธิตเพดาน CPU แทน ซึ่งทำงานได้ทุกกรณี
- **cAdvisor บน Docker 29** ต้องระบุ `--containerd=/var/run/docker/containerd/containerd.sock`
  เพราะ path เริ่มต้น (`/run/containerd/containerd.sock`) ไม่มีอยู่จริง ถ้าไม่ระบุ metric จะยังออกมา
  แต่**ไม่มี label `name=`** ทำให้ PromQL ทุกข้อที่กรองด้วยชื่อ container ได้ผลว่าง (LAB 2 สาธิตให้เห็นจริง)
- **node-exporter ห้าม mount `/:/host:ro,rslave`** ในสภาพแวดล้อมนี้ (จะได้ `path / is mounted on / but it is not a shared or slave mount`)
  ชุดนี้ mount `/proc`, `/sys`, `/` แยกกันแทน
- **หน่วยความจำรายตัวของ container อาจอ่านได้ `0`** ถ้ากล่องเรียนถูกรันซ้อนอีกชั้นหนึ่ง เพราะ controller `memory`
  ไม่ถูกส่งต่อลงมาใน `cgroup.subtree_control` ทำให้ kernel ไม่ได้บันทึกค่าแยกราย container เลย
  (`docker stats` ก็จะขึ้น `0B / 0B` เหมือนกัน ยืนยันว่าไม่ใช่ความผิดของ cAdvisor)
  LAB 2 ใช้จุดนี้สอนวิธี **ตรวจสอบความน่าเชื่อถือของตัวเลข 3 ชั้น** และ dashboard ใน LAB 3 จึงใช้
  หน่วยความจำ**ระดับเครื่อง** (`node_memory_*`) แทนหน่วยความจำรายตัวของ container
- Grafana ในแล็บเปิด **anonymous access** เพื่อความสะดวกในห้องเรียน — **ห้ามทำแบบนี้ใน production**

## เก็บกวาดท้ายคาบ

ข้างในเครื่องเรียน — `cd` เข้าโฟลเดอร์แล็บที่กำลังรันอยู่ก่อน แล้วปิด stack:

```bash
cd ~/labwork/DevTools/03_Application_Docker/03_Monitoring/<โฟลเดอร์แล็บ>
docker compose down -v
docker compose ps -a     # ต้องเหลือแค่หัวตาราง
```

> `-v` ลบ volume ของแล็บด้วย (ข้อมูล metric ที่เก็บไว้และ dashboard ที่แก้ใน UI จะหายไป)
> ซึ่งเป็นสิ่งที่ต้องการ เพราะแต่ละแล็บควรเริ่มจากสถานะสะอาด

## โครงสร้างโฟลเดอร์

```
03_Monitoring/
├── Monitoring_Prometheus_Grafana_Slides.html   สไลด์ไฟล์เดียว (CSS/JS inline ไม่มี CDN)
├── readme.md                                    ไฟล์นี้
├── slides_assets/                               ไดอะแกรมของสไลด์ (SVG + ไฟล์ .excalidraw ต้นฉบับ)
│   └── deck_src/                                ต้นฉบับของสไลด์ + สคริปต์ build/ตรวจ (ดู deck_src/README.md)
├── 001_LAB_Prometheus_First_Scrape/
├── 002_LAB_Container_Metrics_cAdvisor/
├── 003_LAB_Grafana_Dashboard_As_Code/
├── 004_LAB_App_Instrumentation_RED/
├── 005_LAB_Alerting_Alertmanager/
└── 006_LAB_Observability_Capstone/
```

แต่ละโฟลเดอร์แล็บมี `readme.md` ที่รันตามได้ตั้งแต่ต้นจนจบ พร้อม `images/` ที่เป็นภาพจากการรันจริง
