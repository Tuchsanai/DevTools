# เฉลย LAB 6 — Observability Capstone

> ไฟล์นี้คือเฉลยของภารกิจไล่บั๊ก 3 จุด **เปิดเมื่อจนจริง ๆ หรือเปิดหลังทำเสร็จเพื่อเทียบเหตุผล**
> (ในชุดนี้ใช้ไฟล์ `SOLUTION.md` แทนโฟลเดอร์ `solution/` เพราะ `.gitignore` ของ repo ตัดโฟลเดอร์ชื่อนั้นทิ้ง)

สิ่งที่ต้องจำให้ได้จากแล็บนี้ไม่ใช่ "แก้บรรทัดไหน" แต่คือ **อาการแบบไหนชี้ไปที่ชั้นไหนของระบบ**

| # | อาการที่มองเห็น | ชั้นที่พัง | ไฟล์ | ทำให้ตกข้อไหน |
|---|---|---|---|---|
| 1 | `/targets` มี target หนึ่งเป็น DOWN + panel ของแอปว่าง | การเก็บข้อมูล (scrape) | `prometheus/prometheus.yml` | 1, 2, 3, 4, 5 |
| 2 | Prometheus มีข้อมูลครบ แต่ panel ขึ้น `Datasource prom was not found` | การแสดงผล (Grafana) | `grafana/dashboards/overview.json` | 3 |
| 3 | ข้อมูลครบ กราฟสวย แต่ alert ที่ต้องการไม่เคยเป็น firing | การประเมินกฎ (PromQL) | `prometheus/rules/alerts.yml` | 4, 5 |

(คอลัมน์สุดท้ายมาจากการ **เปิดบั๊กทีละตัวแล้วรัน `./check.sh` จริง** ดูตารางผลจริงท้ายไฟล์)

---

## บั๊ก #1 — Prometheus scrape ผิด port

**อาการ**

```text
FAIL  [1/5] targets: expected job = {alertmanager,app,cadvisor,node,prometheus} และ up ครบทุกตัว, got 4/5 up จาก job {alertmanager,app,cadvisor,node,prometheus}
        ตัวที่ล้ม: job app -> http://app:8001/metrics : ... connect: connection refused
FAIL  [2/5] app_requests_total: expected rate > 0, got 'none' (จำนวน series = 0)
```

และเมื่อบั๊ก #2 กับ #3 ถูกแก้ไปแล้ว บั๊ก #1 ตัวเดียวยังลากข้อ 3 กับ 4 ล้มตามไปด้วย (ผลรันจริง):

```text
FAIL  [3/5] panel 8/14 รายการ query แล้วไม่ได้ข้อมูลกลับมา (dashboard จะขึ้น No data)
        ไม่มีข้อมูล: อัตรา request (Rate) -> sum(rate(app_requests_total[30s]))
FAIL  [4/5] rule HighErrorRate: expected expr ที่ประเมินแล้วได้ผลจริง, got vector ว่าง (state=inactive)
        ตอนนี้ Prometheus ยังไม่มีเมตริกของแอปให้ประเมินเลย ให้ย้อนไปดูข้อ 1 และ 2 ก่อน
```

**สาเหตุ** — แอปฟัง port `8000` (ดู `app/Dockerfile` บรรทัด `EXPOSE 8000` และ `APP_PORT: "8000"` ใน compose)
แต่ `scrape_configs` ชี้ไปที่ `app:8001` ซึ่งไม่มีใครฟังอยู่ Prometheus จึงต่อไม่ติดและไม่มีเมตริกของแอปเลยแม้แต่ชุดเดียว

> `8001` ไม่ใช่ typo ธรรมดา แต่เป็นความสับสนคลาสสิกระหว่าง **host port** กับ **container port**
> การ scrape เกิดขึ้น *ภายใน* network `monnet` จึงต้องใช้ port ที่โปรแกรมฟังจริงในคอนเทนเนอร์เสมอ ไม่เกี่ยวกับ `ports:` ที่ publish ออกมา

**แก้** — `prometheus/prometheus.yml`

```diff
   - job_name: app
     static_configs:
-      - targets: ["app:8001"]
+      - targets: ["app:8000"]
```

```bash
sed -i 's|"app:8001"|"app:8000"|' prometheus/prometheus.yml
curl -sS -X POST http://localhost:9090/-/reload -o /dev/null -w 'reload=%{http_code}\n'
```

`/-/reload` ใช้ได้เพราะ compose เปิด flag `--web.enable-lifecycle` ไว้ — config ใหม่มีผลทันทีโดยคอนเทนเนอร์ไม่ restart และข้อมูลเก่าใน TSDB ไม่หาย

---

## บั๊ก #2 — dashboard อ้าง datasource uid ที่ไม่มีอยู่จริง

**อาการ**

```text
FAIL  [3/5] dashboard 'monlab6' อ้าง datasource uid ที่ไม่มีอยู่จริง: prom
        dashboard อ้าง uid : prom
        datasource ที่มีจริง: monprom
```

ทุก panel ขึ้นสามเหลี่ยมแดง เอาเมาส์ชี้จะเห็นข้อความ `Datasource prom was not found`

**สาเหตุ** — datasource ที่ provision ไว้มี `uid: monprom` (ดู `grafana/provisioning/datasources/prometheus.yml`)
แต่ dashboard JSON อ้าง `"uid": "prom"` — Grafana จับคู่ panel กับ datasource ด้วย **uid ตรงตัวอักษร** ไม่ใช่ชื่อ ไม่ใช่ประเภท
uid ที่ไม่ตรงจึงเท่ากับ "ชี้ไปยังของที่ไม่มีอยู่" panel เลยไม่มีทางได้ข้อมูล ทั้งที่ Prometheus มีข้อมูลครบ

**แก้** — `grafana/dashboards/overview.json` (มี 25 จุด ทั้ง panel และ target)

```bash
sed -i 's|"uid": "prom"|"uid": "monprom"|g' grafana/dashboards/overview.json
```

ไม่ต้อง restart Grafana — provider ของ *dashboard* ตั้ง `updateIntervalSeconds: 10` ไว้ รอราว 10-15 วินาทีแล้ว refresh หน้าเว็บ

> ทางกลับกันก็ถูกเหมือนกัน: จะแก้ `uid: monprom` ใน `grafana/provisioning/datasources/prometheus.yml` ให้เป็น `prom` ก็ได้
> **แต่ทางนี้ต้อง `docker compose restart grafana` ด้วย** เพราะ provisioning ของ *datasource* ถูกอ่านตอน Grafana เริ่มทำงานเท่านั้น ไม่ได้ poll ไฟล์ซ้ำเหมือน dashboard
> แก้แล้วไม่ restart จะเจออาการ "แก้ถูกแล้วแต่ไม่มีอะไรเปลี่ยน" ซึ่งไม่ได้สอนอะไรนอกจากความหงุดหงิด
>
> ```bash
> sed -i 's|uid: monprom|uid: prom|' grafana/provisioning/datasources/prometheus.yml
> docker compose restart grafana
> ```
>
> ในงานจริงเรามัก **ตรึง uid ของ datasource ไว้** แล้วให้ dashboard ทุกใบอ้าง uid นั้น เพราะ dashboard มีเป็นสิบใบ ส่วน datasource มีไม่กี่ตัว
> `check.sh` ข้อ 3 รับทั้งสองทาง เพราะมันตรวจว่า "uid ที่ dashboard อ้าง มี datasource ชนิด prometheus รองรับ และทุก panel ได้ข้อมูลจริง" ไม่ได้ตรวจว่าต้องชื่ออะไร

---

## บั๊ก #3 — alert rule ที่ไม่มีวันเป็น firing

**อาการ**

```text
FAIL  [4/5] rule HighErrorRate: expected expr ที่ประเมินแล้วได้ผลจริง, got vector ว่าง (state=inactive)
        expr: sum by (endpoint) (app_requests_total{status=~"5.."}) / sum(app_requests_total) > 0.05
        ยิง expr นี้ตรง ๆ ที่ /api/v1/query แล้วได้ result ว่าง
        สัดส่วน error จริงของระบบตอนนี้ = 0.1024 — ข้อมูลมีให้ประเมิน แต่ expr ของ rule กลับคืนค่าว่าง
FAIL  [5/5] HighErrorRate: expected rule state=firing, got 'inactive'
        alert ที่ receiver ได้รับทั้งหมด 5 ใบ (ชนิด: HighLatencyP95,TargetDown)
```

`promtool check rules` บอกว่า **ผ่าน** และ Prometheus โหลด rule สำเร็จ (`health: ok`) แต่สถานะค้างที่ `inactive` ตลอดกาล

**สาเหตุ มี 2 ชั้นซ้อนกัน**

1. **ลืม `rate()`** — `app_requests_total` เป็น counter ที่มีแต่เพิ่มขึ้นตั้งแต่แอปเริ่มทำงาน
   ค่าดิบของมันบอก "รวมทั้งชีวิต" ไม่ได้บอก "ตอนนี้แย่แค่ไหน" การเอา counter ดิบมาหารกันจึงเป็นสัดส่วนสะสม
   ซึ่งขยับช้ามากจนตรวจจับเหตุการณ์ปัจจุบันไม่ได้เลย
2. **label สองข้างของเครื่องหมายหารไม่ตรงกัน** — ตัวตั้งคือ `sum by (endpoint) (...)` ผลลัพธ์ยังมี label `endpoint` ติดมา
   ส่วนตัวหารคือ `sum(...)` ซึ่ง **ไม่มี label ใดเลย**
   PromQL จับคู่ series สองข้างด้วยชุด label ที่เหมือนกันเป๊ะ เมื่อชุด label ไม่มีทางตรงกัน ผลลัพธ์คือ **vector ว่าง**
   expr ที่คืนค่าว่างจะไม่มีวันกลายเป็น firing เพราะไม่มี series ให้เทียบกับ `> 0.05`

พิสูจน์ด้วยตาก่อนแก้ (ถอด `> 0.05` ออกแล้วยิงตรงไปที่ API):

```bash
curl -s --get --data-urlencode \
  'query=sum by (endpoint) (app_requests_total{status=~"5.."}) / sum(app_requests_total)' \
  http://localhost:9090/api/v1/query
# {"status":"success","data":{"resultType":"vector","result":[]}}   <-- ว่าง
```

**แก้** — `prometheus/rules/alerts.yml`

```diff
       - alert: HighErrorRate
-        expr: sum(app_requests_total{status=~"5.."}) by (endpoint) / sum(app_requests_total) > 0.05
+        expr: sum(rate(app_requests_total{status=~"5.."}[30s])) / sum(rate(app_requests_total[30s])) > 0.05
         for: 20s
```

```bash
sed -i 's|^        expr: sum(app_requests_total.*|        expr: sum(rate(app_requests_total{status=~"5.."}[30s])) / sum(rate(app_requests_total[30s])) > 0.05|' \
  prometheus/rules/alerts.yml
docker compose exec -T prometheus promtool check rules /etc/prometheus/rules/alerts.yml
curl -sS -X POST http://localhost:9090/-/reload -o /dev/null -w 'reload=%{http_code}\n'
```

ทำไมรูปนี้ถึงถูก:

- `rate(...[30s])` เปลี่ยน counter เป็น "ต่อวินาที ณ ช่วงเวลานี้" → ตอบคำถามว่าตอนนี้แย่แค่ไหน
- `sum(...)` ทั้งสองข้าง → ทั้งคู่ไม่มี label เหลือ จับคู่กันได้ ผลลัพธ์เป็นเลขตัวเดียว
- เรื่องขนาดหน้าต่าง แยกเป็นสองระดับ อย่าปนกัน
  - **ข้อกำหนดขั้นต่ำ:** `rate()` ต้องมีอย่างน้อย **2 sample** ในหน้าต่าง ไม่งั้นคืนค่าว่าง — ที่ `scrape_interval: 5s` แปลว่าหน้าต่างต้องกว้างกว่า 5 วินาทีจริง ๆ
  - **แนวปฏิบัติ:** ตั้งหน้าต่างราว **4 เท่าของ scrape interval ขึ้นไป** เพื่อเผื่อ jitter ของเวลา scrape และเผื่อ scrape หลุดไปหนึ่งรอบ ไม่ใช่กฎที่ Prometheus บังคับ แต่เป็นเผื่อไว้ให้ผลนิ่ง
  - แล็บนี้ใช้ `[30s]` = 6 เท่าของ 5 วินาที ซึ่งอยู่ในโซนปลอดภัยสบาย ๆ
- ผลจริงในแล็บนี้ ≈ `0.099` (loadgen ยิงรอบละ 20 request มี 500 อยู่ 2 ใบ = 10%) จึงเกินเกณฑ์ `0.05` แน่นอนและไม่กะพริบ

**รูปอื่นที่ถูกเหมือนกัน** — `check.sh` ตัดสินที่พฤติกรรม จึงรับทุกรูปที่ "ยิงแล้วได้สัดส่วนจริง" เช่น
`sum(increase(app_requests_total{status=~"5.."}[1m])) / sum(increase(app_requests_total[1m])) > 0.05`
(ทดสอบแล้วได้ `0.0995` และ checker ให้ผ่าน) ส่วนรูปที่ **ไม่ผ่าน** คือรูปที่ยิงแล้วได้ vector ว่าง
เช่น `sum by (endpoint) (rate(...)) / sum(rate(...))` ซึ่งมี `rate()` ครบสองข้างและมีเครื่องหมายหาร แต่ label สองข้างไม่เข้าคู่กัน

---

## ลำดับที่แนะนำและผลที่ควรเห็นระหว่างทาง

| ทำอะไร | ผล `./check.sh` (รันจริง) |
|---|---|
| ยังไม่แก้อะไร | `0/5` |
| แก้บั๊ก #1 แล้ว reload | `2/5` (ข้อ 1 และ 2 ผ่าน) |
| แก้บั๊ก #2 (รอ provider ~15 วินาที) | `3/5` |
| แก้บั๊ก #3 แล้ว reload | `5/5` และ exit code 0 |

### บั๊กแต่ละตัว "เดี่ยว ๆ" ทำให้ตกข้อไหนบ้าง (เปิดบั๊กทีละตัวแล้วรันจริง)

| สถานะบั๊ก | ผลจริง | ข้อที่ตก |
|---|---|---|
| เปิดครบทั้ง 3 (สภาพที่ส่งมอบ) | `0/5` | 1, 2, 3, 4, 5 |
| เปิดเฉพาะ #1 (scrape ผิด port) | `0/5` | 1, 2, 3, 4, 5 |
| เปิดเฉพาะ #2 (datasource uid) | `4/5` | 3 |
| เปิดเฉพาะ #3 (alert expr) | `3/5` | 4, 5 |
| แก้ครบทั้งสาม | `5/5` exit 0 | – |

อ่านตารางนี้ให้ขาด:

- **บั๊ก #1 ตัวเดียวลากทั้ง 5 ข้อ** เพราะไม่มีเมตริกของแอปเข้าระบบเลย → ข้อ 2 ไม่มีข้อมูล ·
  ข้อ 3 ตกเพราะ `check.sh` ยิง query ของทุก panel จริง แล้ว panel ที่ใช้ `app_*` คืนค่าว่าง (รันจริงได้ `panel 8/14 ไม่มีข้อมูล`) ·
  ข้อ 4 ตกเพราะ expr ประเมินแล้วได้ vector ว่าง · ข้อ 5 ตกเพราะไม่มีอะไรให้ยิง
- **บั๊ก #2 กระทบข้อ 3 ข้อเดียว** — Prometheus ยังทำงานปกติทุกอย่าง มันพังแค่ชั้นแสดงผล
- **บั๊ก #3 กระทบข้อ 4 และ 5** — ข้อมูลครบ แต่กฎประเมินไม่ออกจึงไม่มีวันแจ้งเตือน
- **`0/5` ตอนเริ่มต้นคือผลรวมของบั๊กทั้งสาม** ไม่ใช่ผลของบั๊ก #1 ตัวเดียว

**ลำดับการแก้เป็น "คำแนะนำ" ไม่ใช่ข้อบังคับ** — แก้ #3 หรือ #2 ก่อนก็ได้ ระบบไม่ได้ห้าม
แต่ถ้าแก้ #2 ก่อนโดยที่ #1 ยังอยู่ คะแนนจะไม่ขยับ (ข้อ 3 ยังตกอยู่ดีเพราะ panel ของแอปยังไม่มีข้อมูล)
ซึ่งเป็นเหตุผลเชิงปฏิบัติของหลักการ **ไล่จากต้นน้ำไปปลายน้ำ**: แก้ปลายน้ำก่อนมักไม่เห็นผล จนกว่าต้นน้ำจะมีข้อมูลจริงไหลมา

---

## คำถามท้ายบท (ตอบให้ได้ก่อนถือว่าจบ)

1. ทำไมบั๊ก #1 จุดเดียวถึงลาก FAIL ครบทั้ง 5 ข้อ ในขณะที่บั๊ก #2 กระทบแค่ข้อ 3 — ทั้งที่ทั้งคู่เป็น "พิมพ์ผิดหนึ่งบรรทัด" เหมือนกัน
2. ถ้า `promtool check rules` ผ่าน แปลว่า alert ใช้งานได้จริงหรือไม่ เพราะอะไร
3. ถ้าเปลี่ยน `[30s]` เป็น `[5s]` โดยที่ `scrape_interval: 5s` จะเกิดอะไรขึ้นกับ `rate()`
4. ระหว่าง "Prometheus แสดง firing" กับ "ทีมได้รับแจ้งเตือน" มีชั้นอะไรคั่นอยู่บ้าง และแต่ละชั้นพังได้อย่างไร
5. ทำไม `check.sh` ข้อ 4 ถึงไม่ตัดสินด้วยการ "นับว่ามี `rate()` กี่ครั้ง" แต่เลือกยิง expr ออกไปจริง —
   ลองคิดถึง expr ที่มี `rate()` ครบสองข้างแต่คืนค่าว่าง กับ expr ที่ใช้ `increase()` แล้วทำงานถูกต้อง
