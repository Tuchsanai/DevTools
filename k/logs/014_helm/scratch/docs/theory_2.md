## 6. values และลำดับความสำคัญ

### 6.1 ใบสั่งหลายชั้น: ใครชนะ

<p align="center" id="fig-25">
  <img src="images/25-values-precedence.png" alt="รูปที่ 25 ลำดับความสำคัญของ values" width="900"><br>
  <em><b>รูปที่ 25</b> ลำดับความสำคัญ: values.yaml ในชุด &lt; ไฟล์ -f (ไฟล์หลังชนะ) &lt; --set (บนสุดชนะ)</em>
</p>

Helm รวม values จากหลายแหล่งเป็นก้อนเดียวก่อน render จากต่ำไปสูง (ค่าที่อยู่สูงกว่าทับค่าที่ต่ำกว่า)

1. `values.yaml` ใน chart (ค่าเริ่มต้น)
2. ค่าที่ parent chart ส่งให้ subchart (ถ้าเป็น subchart — หัวข้อ 12)
3. ไฟล์ที่ส่งด้วย `-f`/`--values` **ตามลำดับที่เขียน ไฟล์หลังชนะไฟล์หน้า** (`-f base.yaml -f prod.yaml`)
4. `--set`, `--set-string`, `--set-file`, `--set-json`, `--set-literal` บนบรรทัดคำสั่ง (ชนะทุกอย่าง และตัวหลังชนะตัวหน้า)

ผลจริงจาก LAB 3: ไฟล์ `labs/lab03-values/podinfo-values.yaml` ตั้ง `ui.message: "ร้านน้องส้มสาขา values file"` แต่สั่ง

```bash
helm upgrade hello podinfo/podinfo --version 6.15.0 -n helm-demo \
  -f labs/lab03-values/podinfo-values.yaml --set ui.message="--set ชนะ" --wait
```

podinfo ตอบ `"message": "--set ชนะ"` และ `"color": "#ff8c00"` (สีมาจากไฟล์เพราะ `--set` ไม่ได้แตะ)

**ตารางที่ 7** รูปแบบของ `--set`

| รูปแบบ | ผล | หมายเหตุ |
|---|---|---|
| `--set web.replicas=3` | `web: {replicas: 3}` | จุด = ลงไปใน map |
| `--set a=1,b=2` | หลายค่าในครั้งเดียว | จุลภาคคั่น (ค่าที่มีจุลภาคต้อง escape `\,`) |
| `--set web.image.tag=1.8` | `"1.8"`? **ไม่แน่** | `--set` เดาชนิด: `1.8` อาจเป็นตัวเลข ใน chart ร้าน template ครอบ `quote` จึงปลอดภัย |
| `--set-string web.image.tag=1.10` | บังคับเป็นข้อความ `"1.10"` | ใช้กับ tag ที่เป็นตัวเลขเสมอ (กัน `1.10` → `1.1`) |
| `--set args[0]=--kubelet-insecure-tls` | ตั้งสมาชิกใน list | ระวัง: list ถูกแทนทั้งก้อน (6.2) |
| `--set-file key=path` | อ่านค่าจากไฟล์ | เช่น ใส่ไฟล์ประกาศทั้งไฟล์ |
| `--set-json 'web.resources={"requests":{"cpu":"200m"}}'` | ใส่ค่า JSON ทั้งก้อน | |
| `--set key=null` | ลบ key ที่มาจากค่าเริ่มต้น | ใช้ปิดค่าเริ่มต้นของ chart |

### 6.2 การ merge: map รวมกัน list แทนทั้งก้อน

- **map รวมกันทีละ key**: ไฟล์ dev ตั้งแค่ `web.replicas: 1` ค่า `web.image.repository` และ `web.resources` จาก `values.yaml` ยังอยู่ครบ
- **list ถูกแทนทั้งก้อน**: ถ้าค่าเริ่มต้นมี `args: [a, b]` แล้ว `-f` ส่ง `args: [c]` ผลคือ `[c]` (ไม่ใช่ `[a, b, c]`) เหตุนี้ `metrics-server-values.yaml` ใน LAB 10 ต้องเขียน args ที่ต้องการครบชุด
- `--set key=null` ลบ key ทิ้ง

ดูค่าที่ release ใช้จริงได้สองแบบ (LAB 2–3)

```bash
helm get values hello -n helm-demo         # เฉพาะค่าที่เราส่ง (USER-SUPPLIED VALUES)
helm get values hello -n helm-demo --all   # ค่าทั้งหมดหลัง merge กับค่าเริ่มต้น
```

### 6.3 ใบสั่งต่อ environment

<p align="center" id="fig-26">
  <img src="images/26-values-per-env.png" alt="รูปที่ 26 ใบสั่งต่อ environment" width="900"><br>
  <em><b>รูปที่ 26</b> ชุดแฟรนไชส์เดียว + ใบสั่งคนละใบ = สาขา dev (บูธเดียว) และ prod (HPA + HTTPS)</em>
</p>

แทนการ copy โฟลเดอร์ เราเก็บ **chart เดียว** และ **ใบสั่งคนละใบ** ที่มีเฉพาะส่วนที่ต่าง (ไฟล์จริงใน `02_LAB/charts/`)

```yaml
# values-dev.yaml — สาขาทดลอง (dev): บูธเดียว ไม่มี HPA ประตู http ธรรมดา ธีมส้ม
shop:
  SHOP_NAME: "ร้านอาหารแมวน้องส้ม (dev)"
  APP_THEME: "sunset"
  SHOP_PROMO: "🧪 สาขาทดลอง — ของจริงอยู่ที่ shop.localhost"
web:
  replicas: 1
hpa:
  enabled: false
ingress:
  enabled: true
  host: dev.shop.localhost
  tls: false
```

```yaml
# values-prod.yaml — สาขาจริง (prod): HPA 2–6 บูธ ประตู HTTPS shop.localhost
shop:
  SHOP_NAME: "ร้านอาหารแมวน้องส้ม"
  APP_THEME: "harbor"
  SHOP_PROMO: "🎉 เปิดสาขาใหม่ด้วย Helm คำสั่งเดียว"
hpa:
  enabled: true
  minReplicas: 2
  maxReplicas: 6
ingress:
  enabled: true
  host: shop.localhost
  tls: true
```

ผล render (LAB 8) นับ object ที่ได้

| ใบสั่ง | จำนวน `kind:` | ชนิด |
|---|:---:|---|
| dev | **10** | ConfigMap 2, Deployment, Ingress, Job (hook seed), Pod (test), Secret, Service 2, StatefulSet |
| prod | **13** | dev + HorizontalPodAutoscaler + Middleware (redirect https) + Secret ที่ 2 (`som-tls`) |

(ถ้าไม่นับ Job hook และ Pod test ที่ไม่ใช่ส่วนของร้านปกติ = 8 และ 11 object) ทุกการแก้ไขแม่พิมพ์ไปถึงทั้งสองสาขาพร้อมกัน drift จึงเหลือเฉพาะสิ่งที่ตั้งใจให้ต่างในใบสั่ง

### 6.4 กับดัก: upgrade ที่ส่งค่ามาแค่บางตัว

<p align="center" id="fig-27">
  <img src="images/27-upgrade-values-trap.png" alt="รูปที่ 27 กับดัก upgrade ส่งค่าบางตัว" width="900"><br>
  <em><b>รูปที่ 27</b> กับดัก: helm upgrade ที่ส่งค่ามาแค่บางตัว (เช่น --set อย่างเดียว) = ค่าอื่นที่เคยตั้งกลับเป็นค่าเริ่มต้นของชุด ส่วน upgrade ที่ไม่ส่งค่าเลยจะใช้ค่าเดิมต่อ — ปลอดภัยสุดคือส่ง -f ทุกครั้ง หรือใช้ --reuse-values</em>
</p>

`helm upgrade` **ไม่ได้** "แก้เฉพาะค่าที่ส่งมา" ทับค่าของ revision ก่อน แต่คำนวณ values ใหม่จาก **ค่าเริ่มต้นของ chart + สิ่งที่ส่งมาในคำสั่งนี้** กติกาที่ทดสอบจริงกับ Helm 4.3.0

| คำสั่ง upgrade | values ที่ได้ | ผลจริง |
|---|---|---|
| ส่ง `-f` (และ/หรือ `--set`) ครบ | ค่าเริ่มต้น + สิ่งที่ส่ง | ปกติ (rev 2, 4 ใน LAB 3) |
| **ส่งแค่ `--set` บางค่า** (ไม่ส่ง `-f`) | ค่าเริ่มต้น + `--set` นั้น **ค่าอื่นที่เคยตั้งหายหมด** | rev 3: `helm get values` เหลือ `replicaCount: 1` อย่างเดียว Ingress หาย `curl` ได้ `404` |
| **ไม่ส่งค่าอะไรเลย** | Helm ใช้ค่าของ revision ก่อนต่อ (reuse) | values ยังครบ (ทดสอบในรอบสำรวจของ LAB 3) |
| `--reuse-values --set x=y` | ค่าของ revision ก่อน + `--set` ใหม่ | rev 5: `replicaCount: 3`, สี และ Ingress อยู่ครบ message เปลี่ยน |
| `--reset-then-reuse-values --set x=y` | ค่าเริ่มต้น **ของ chart รุ่นใหม่** + ค่าเดิม + `--set` | ใช้ตอนอัปเกรด chart รุ่นใหม่ที่เพิ่ม key ใหม่ (`--reuse-values` จะไม่เห็น key ใหม่) |

ผลของ rev 3 (ส่ง `--set replicaCount=1` อย่างเดียว) ใน LAB 3

```text
helm get values hello -n helm-demo
USER-SUPPLIED VALUES:
replicaCount: 1
kubectl -n helm-demo get deploy,ing
NAME                            READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/hello-podinfo   1/1     1            1           43s
curl -s -o /dev/null -w "%{http_code}\n" http://podinfo.localhost:30080
404
```

**กติกาที่บทนี้ใช้:** ทุกคำสั่ง upgrade ส่งใบสั่ง `-f` ของสาขานั้นทุกครั้ง (เช่น `-f charts/values-prod.yaml --set web.image.tag=1.8`) ใบสั่งจึงอยู่ในไฟล์ที่ commit ได้ ไม่ใช่ "ในความจำของ release" ส่วน `--reuse-values` ใช้ได้เมื่อรู้ว่าไม่ได้เปลี่ยนรุ่น chart

### 6.5 values.schema.json: ด่านตรวจใบสั่ง

<p align="center" id="fig-28">
  <img src="images/28-schema-desk.png" alt="รูปที่ 28 values.schema.json ด่านตรวจใบสั่ง" width="900"><br>
  <em><b>รูปที่ 28</b> values.schema.json = ด่านตรวจใบสั่ง: ค่าผิดชนิด/เกินช่วงถูกปฏิเสธก่อนสร้างอะไรเลย (เช่น replicas 9 เกิน 6, tag 1.4)</em>
</p>

ถ้า chart มีไฟล์ `values.schema.json` (JSON Schema) Helm ตรวจ values ที่ merge แล้ว **ก่อน render** ทุกคำสั่ง (`install`, `upgrade`, `template`, `lint`) ค่าที่ผิดกติกาจะไม่ไปถึงคลัสเตอร์เลย ส่วนหนึ่งของด่านตรวจร้าน

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "som-shop values",
  "type": "object",
  "properties": {
    "web": {
      "type": "object",
      "properties": {
        "replicas": {"type": "integer", "minimum": 1, "maximum": 6},
        "image": {
          "type": "object",
          "properties": {
            "repository": {"type": "string", "minLength": 1},
            "tag": {"type": "string", "not": {"const": "1.4"}}
          }
        }
      }
    }
  }
}
```

ผลจริง (LAB 8)

```text
helm template som charts/som-shop --set db.password=x --set web.image.tag=1.4
Error: values don't meet the specifications of the schema(s) in the following chart(s):
som-shop:
- at '/web/image/tag': 'not' failed

helm template som charts/som-shop --set db.password=x --set web.replicas=9
Error: values don't meet the specifications of the schema(s) in the following chart(s):
som-shop:
- at '/web/replicas': maximum: got 9, want 6

helm template som charts/som-shop --set db.password=x --set ingress.host=Shop_Localhost
Error: values don't meet the specifications of the schema(s) in the following chart(s):
som-shop:
- at '/ingress/host': 'Shop_Localhost' does not match pattern '^[a-z0-9.-]+$'
```

ทำไมห้าม tag `1.4`: บทที่ 7 เราสร้าง `som-shop-web:1.4` เป็น "รุ่นพัง" ไว้ฝึก rollout undo ด่านตรวจจึงกันไม่ให้ใครเผลอส่งรุ่นนี้ขึ้นร้าน chart ภายนอกหลายตัวก็มี schema เช่น Traefik chart 41.6.1 ปฏิเสธ key ที่ไม่มีอยู่จริง (`--set logs.access.enabled=true` → `- at '': additional properties 'logs' not allowed`) ช่วยจับการพิมพ์ key ผิดที่ปกติจะ "เงียบ" (ค่าถูกเพิกเฉย)

> schema ตรวจได้แค่ "รูปร่าง" ของค่า (ชนิด ช่วง รูปแบบ) ตรวจไม่ได้ว่า image มีอยู่จริงหรือรหัสถูกต้อง สิ่งเหล่านั้นต้องอาศัย `--wait` และ `helm test`

## 7. การ render และ debug

### 7.1 เครื่องมือ 4 ระดับ

<p align="center" id="fig-29">
  <img src="images/29-render-table.png" alt="รูปที่ 29 template / lint / dry-run" width="900"><br>
  <em><b>รูปที่ 29</b> helm template = พิมพ์พิมพ์เขียวออกมาดูโดยไม่สร้างจริง, helm lint = ตรวจชุด, --dry-run=server = ลองกับท่าเรือจริงแต่ไม่บันทึก</em>
</p>

**ตารางที่ 8** เครื่องมือตรวจ chart

| คำสั่ง | ต่อคลัสเตอร์? | ทำอะไร | จับอะไรได้ | จับอะไรไม่ได้ |
|---|:---:|---|---|---|
| `helm lint <chart>` | ไม่ | render + ตรวจรูปแบบ chart และ YAML | YAML พัง, ฟังก์ชันไม่มี, `Chart.yaml` ผิด, schema | ค่าที่ API server ไม่ยอมรับ, `required` (แค่ WARN) |
| `helm template <name> <chart>` | ไม่ | render แล้วพิมพ์ manifest ออก stdout | เหมือน lint + เห็นผลจริงทุกบรรทัด (`--show-only templates/x.yaml` ดูไฟล์เดียว) | `lookup` (ได้ค่าว่าง), field ผิดของ Kubernetes |
| `helm install/upgrade --dry-run=client` | ไม่ | เหมือน template แต่แสดงในรูปผลของ install (NOTES, HOOKS) | เหมือน template | เหมือน template |
| `helm install/upgrade --dry-run=server` | ใช่ | render โดย `lookup` เห็นคลัสเตอร์ ตรวจ ownership | lookup, ชื่อชน | **field ผิดของ object (ดูกับดักข้างล่าง)** |
| `helm template ... \| kubectl apply --dry-run=server -f -` | ใช่ | ส่ง manifest ให้ API server ตรวจจริงแต่ไม่บันทึก | field ผิด, ค่าไม่อยู่ในชุดที่อนุญาต, admission | `lookup` (มาจาก template) |
| `--debug` | — | เพิ่มรายละเอียด และพิมพ์ YAML ที่พังให้ดู | ช่วยหาบรรทัดที่ผิด | — |

**กับดักที่เจอจริงใน Helm 4.3.0:** `--dry-run=server` **ไม่** ส่ง object ไปให้ API server ตรวจแบบ server-side dry run ใน LAB 6 ตั้ง `service.type=NodePortt` (พิมพ์ผิด) แล้ว

```text
helm install web2 ../lab05-first/mychart -n first --dry-run=server --set service.type=NodePortt
NAME: web2
...
STATUS: pending-install
REVISION: 1
DESCRIPTION: Dry run complete
```

ผ่านทั้งที่ค่าใช้ไม่ได้ แต่ส่ง manifest เดียวกันให้ `kubectl` ตรวจ

```text
helm template web2 ../lab05-first/mychart --set service.type=NodePortt | kubectl apply --dry-run=server -n first -f -
deployment.apps/web2-mychart created (server dry run)
pod/web2-mychart-test-connection created (server dry run)
The Service "web2-mychart" is invalid: spec.type: Unsupported value: "NodePortt": supported values: "ClusterIP", "ExternalName", "LoadBalancer", "NodePort"
```

และถ้าติดตั้งจริงจะล้มพร้อม **ทิ้ง release สถานะ `failed`** ไว้ (`web2 ... failed`) ต้อง `helm uninstall web2` เอง ข้อสรุป: ก่อนติดตั้งของสำคัญให้ตรวจสองชั้น — `helm lint`/`template` (รูปแบบ chart) แล้ว `helm template | kubectl apply --dry-run=server -f -` (ความถูกต้องของ object)

### 7.2 error ที่เจอบ่อย 4 แบบ

<p align="center" id="fig-30">
  <img src="images/30-common-errors.png" alt="รูปที่ 30 error ที่เจอบ่อย 4 แบบ" width="900"><br>
  <em><b>รูปที่ 30</b> error ที่เจอบ่อย 4 แบบ: YAML parse error (ย่อหน้า), function not defined (สะกดฟังก์ชันผิด), required (ลืมค่า), schema (ค่าผิดกติกา)</em>
</p>

**ตารางที่ 9** อ่าน error ของ Helm (ข้อความจริงจาก LAB 6 และ LAB 8)

| แบบ | ข้อความจริง | อ่านว่า | แก้ |
|---|---|---|---|
| YAML parse (ย่อหน้า) | `[ERROR] templates/deployment.yaml: unable to parse YAML: error converting YAML to JSON: yaml: line 24: mapping values are not allowed in this context` | render ได้ แต่ผลไม่ใช่ YAML ที่ถูก **"line 24" คือบรรทัดของผล render ไม่ใช่ของไฟล์ template** | `helm template --debug` ดูผลที่พัง มักเป็น `indent`/`nindent` หรือ `{{-` ตัดบรรทัดเกิน |
| function not defined | `[ERROR] templates/: parse error at (mychart/templates/deployment.yaml:18): function "toYml" not defined` | template parse ไม่ผ่าน (บรรทัด 18 ของไฟล์ template) | สะกดฟังก์ชันให้ถูก (`toYaml`) |
| required | `Error: execution error at (mychart/templates/deployment.yaml:41:21): ต้องใส่ image.repository` | `required` หยุด render ที่บรรทัด:คอลัมน์ | ส่งค่านั้นมา |
| schema | `- at '/web/replicas': maximum: got 9, want 6` | values ผิด schema (ยังไม่ render) | แก้ค่าในใบสั่ง |

อีกแบบที่ควรรู้: chart ที่ใช้ `apiVersion: v3` (ยังทดลอง) ได้ `[ERROR] Chart.yaml: chart type is not valid in apiVersion 'v3'. It is valid in apiVersion 'v2'` ถ้ามีบรรทัด `type:` และ `apiVersion 'v3' is not valid. The value must be either "v1" or "v2"` ถ้าไม่มี ส่วน `helm template` ตอบสั้น ๆ `Error: invalid chart apiVersion` (ทั้งมีและไม่มี `HELM_EXPERIMENTAL_CHART_V3=1`)

## 8. lifecycle ของ release

### 8.1 วงจรชีวิตสาขา

<p align="center" id="fig-31">
  <img src="images/31-lifecycle-cycle.png" alt="รูปที่ 31 วงจรชีวิตสาขา" width="900"><br>
  <em><b>รูปที่ 31</b> วงจรชีวิตสาขา: install → upgrade → rollback → uninstall ทุกครั้ง (ยกเว้น uninstall) เขียนหน้าใหม่ในสมุด</em>
</p>

**ตารางที่ 10** คำสั่งหลักของ lifecycle

| คำสั่ง | ทำอะไร | revision | ข้อสังเกต |
|---|---|---|---|
| `helm install <name> <chart>` | ติดตั้งครั้งแรก | 1 | ชื่อซ้ำกับ release ที่ยังอยู่ (รวม `uninstalled` ที่ keep-history) → `cannot reuse a name that is still in use` |
| `helm upgrade <name> <chart>` | render ใหม่แล้ว apply ความต่าง ลบ object ที่ chart ใหม่ไม่มีแล้ว | +1 | upgrade release ที่ `failed` ได้ (ใช้แก้ release ที่ล้ม) |
| `helm upgrade --install` | ถ้ายังไม่มี install ถ้ามีแล้ว upgrade | 1 หรือ +1 | idempotent เหมาะกับ script/CI (สั่งซ้ำได้) |
| `helm rollback <name> <rev>` | ใช้ manifest + values ของ revision นั้น apply อีกครั้ง | **+1 (ไม่ถอยเลข)** | description `Rollback to <rev>` |
| `helm uninstall <name>` | ลบทุก object ของ release + ลบประวัติ | — | ไม่ลบ PVC ที่เกิดจาก `volumeClaimTemplates`, CRD และ hook resource |
| `helm uninstall --keep-history` | ลบ object แต่เก็บประวัติ | สถานะ `uninstalled` | `helm rollback` กลับมาได้ |
| `helm history <name>` | ดูสมุด | — | เก็บ 10 รุ่นล่าสุด (`HELM_MAX_HISTORY`/`--history-max`) |
| `helm list` / `-A` | ดู release ใน namespace / ทุก namespace | — | Helm 4 ไม่มี `-a` แล้ว |
| `helm status <name>` | สถานะ + NOTES | — | |
| `helm get values/manifest/notes/metadata/hooks/all` | ดูข้อมูลของ revision (`--revision N`) | — | `metadata` บอก `APPLY_METHOD` |

สถานะของ revision ที่จะเห็นใน `helm history`/`helm list`: `pending-install`, `pending-upgrade`, `pending-rollback` (กำลังทำ), `deployed` (รุ่นปัจจุบัน มีได้ตัวเดียว), `superseded` (รุ่นเก่าที่ถูกแทน), `failed` (ล้ม), `uninstalled` (ลบแล้วแต่เก็บประวัติ)

> ถ้า helm ถูกขัดจังหวะ (กด Ctrl+C, เครือข่ายหลุด) ระหว่าง `pending-*` คำสั่งถัดไปอาจได้ `another operation (install/upgrade/rollback) is in progress` ให้ดู `helm history` แล้ว rollback ไปรุ่นที่ดีล่าสุด

### 8.2 rollback = เขียนหน้าใหม่ ไม่ใช่ถอยหน้า

<p align="center" id="fig-32">
  <img src="images/32-revision-logbook.png" alt="รูปที่ 32 rollback เขียนหน้าใหม่" width="900"><br>
  <em><b>รูปที่ 32</b> rollback ไม่ได้ถอยเลขหน้า แต่เขียนหน้าใหม่ที่คัดลอกจากหน้าเก่า (เลข revision เพิ่มขึ้นเสมอ)</em>
</p>

ผลจริง LAB 4 (podinfo): rev 6 ตั้ง image ผิด → `helm rollback hello 5 --wait` (11.9 วินาที) ได้ **rev 7** ไม่ใช่กลับไปเป็น rev 5

```text
6       	Tue Oct  6 05:50:32 2026	superseded	podinfo-6.15.0	6.15.0     	Upgrade complete
7       	Tue Oct  6 05:50:48 2026	deployed  	podinfo-6.15.0	6.15.0     	Rollback to 5
```

ข้อดีของการเขียนหน้าใหม่: สมุดเป็นบันทึกเหตุการณ์ที่ไม่ถูกลบย้อนหลัง เห็นว่า "เคยขึ้น rev 6 แล้วถอย" ซึ่งเป็นข้อมูลสำคัญเวลาหาสาเหตุปัญหา

### 8.3 --wait: Helm 4 ไม่รอถ้าไม่สั่ง

<p align="center" id="fig-33">
  <img src="images/33-wait-strategies.png" alt="รูปที่ 33 กลยุทธ์ --wait" width="900"><br>
  <em><b>รูปที่ 33</b> ไม่ใส่ --wait: Helm บอก deployed ทั้งที่บูธยังพัง / --wait รอให้พร้อม / --rollback-on-failure ล้มแล้วถอยกลับเอง</em>
</p>

Helm 4 รับ `--wait` เป็น **กลยุทธ์ (WaitStrategy)**

| ค่า | ความหมาย |
|---|---|
| ไม่ใส่ (`hookOnly`) | **รอแค่ hook** (เช่น Job seed) ไม่รอ Deployment/StatefulSet พร้อม — ส่ง manifest เสร็จก็ตอบ `deployed` |
| `--wait` (= `--wait=watcher`) | รอจน object ทุกตัวพร้อมตาม kstatus (Deployment Available ครบ, StatefulSet ready, Job สำเร็จ ...) ภายใน `--timeout` (ค่าเริ่มต้น 5m) |
| `--wait=legacy` | วิธีรอแบบ Helm 3 |

ผลจริง LAB 4: image `9.9.9-nope` (ไม่มีจริง) **ไม่ใส่ `--wait`** ใช้เวลา **0.2 วินาที** แล้วได้ `STATUS: deployed` ทั้งที่ 15 วินาทีต่อมา Pod ใหม่เป็น `ErrImagePull` (ร้านยังเปิดได้เพราะ Pod เก่ายังอยู่ตาม rolling update) — CI ที่เชื่อ `deployed` จะรายงานว่าสำเร็จ

> **กติกาของบทนี้: ใส่ `--wait` ทุกครั้งที่ install/upgrade/rollback** (และ `--timeout` ที่เหมาะกับแอป) ชุดร้านติดตั้งแบบ `--wait` ใช้ 18 วินาที ส่วนไม่ใส่ใช้ราว 12 วินาที (เพราะยังต้องรอ hook seed อยู่ดี) ต่างกันไม่มากแต่ได้ความมั่นใจ

### 8.4 --rollback-on-failure, --timeout และ --cleanup-on-fail

`--rollback-on-failure` (ชื่อเดิม `--atomic`) = รอ (เหมือน `--wait`) ถ้าไม่พร้อมภายใน `--timeout` ให้ **ถอยกลับไป revision ที่ใช้งานอยู่ก่อนหน้าเอง** ผลจริง LAB 4

```text
time helm upgrade hello podinfo/podinfo --version 6.15.0 -n helm-demo --reuse-values --set image.tag=9.9.9-nope --rollback-on-failure --timeout 40s
level=WARN msg="upgrade failed" name=hello error="resource Deployment/helm-demo/hello-podinfo not ready. status: InProgress, message: Updated: 2/3\ncontext deadline exceeded"
Error: UPGRADE FAILED: release hello failed, and has been rolled back due to rollback-on-failure being set: resource Deployment/helm-demo/hello-podinfo not ready. status: InProgress, message: Updated: 2/3
context deadline exceeded

real	0m42.959s
```

สมุดได้ 2 หน้าใหม่: rev 8 `failed` และ rev 9 `Rollback to 7` (rev 7 คือรุ่นที่ใช้งานอยู่ก่อน upgrade) ใช้เวลารวม ~43 วินาที (timeout 40 + ถอย)

- `--timeout` ควรยาวกว่าเวลาที่แอปใช้พร้อมจริง (รวมดึง image, readinessProbe, `minReadySeconds`) ไม่งั้นจะถอยทั้งที่แอปกำลังจะพร้อม
- `--cleanup-on-fail` ลบ object **ใหม่** ที่ถูกสร้างใน upgrade ที่ล้ม (ไม่งั้นค้างอยู่)
- ใน CI นิยม `helm upgrade --install ... --wait --timeout 5m --rollback-on-failure`

### 8.5 กับดัก: rollback ไม่ระบุเลข

<p align="center" id="fig-34">
  <img src="images/34-rollback-no-number.png" alt="รูปที่ 34 กับดัก rollback ไม่ระบุเลข" width="900"><br>
  <em><b>รูปที่ 34</b> กับดัก: helm rollback ไม่ระบุเลข = ถอยไปหน้าก่อนหน้า แม้หน้านั้นเป็นรุ่นที่ล้ม → ระบุเลข revision เสมอ</em>
</p>

`helm rollback hello` (ไม่ใส่เลข) ถอยไป **revision ก่อนหน้า** ซึ่งอาจเป็นรุ่นที่ `failed` ผลจริง LAB 4: หลัง rev 9 (`Rollback to 7`) สั่ง `helm rollback hello` ได้ rev 10 **`Rollback to 8`** = กลับไปรุ่นที่ image ผิด Pod ใหม่เป็น `ErrImagePull` อีกครั้ง ต้องสั่ง `helm rollback hello 9 --wait` แก้ (rev 11)

```text
8       	Tue Oct  6 05:51:00 2026	failed    	podinfo-6.15.0	6.15.0     	Upgrade "hello" failed: resource Deployment/helm-demo/hello-podinfo not ready. status: InProgress, message: Updated: ...
9       	Tue Oct  6 05:51:40 2026	superseded	podinfo-6.15.0	6.15.0     	Rollback to 7
10      	Tue Oct  6 05:51:43 2026	deployed  	podinfo-6.15.0	6.15.0     	Rollback to 8
```

> **กติกา: ดู `helm history` ก่อน แล้ว rollback ด้วยเลขที่ต้องการเสมอ** (และใส่ `--wait`)

### 8.6 uninstall, --keep-history และของที่ไม่ถูกลบ

- `helm uninstall hello --keep-history` ลบ object แต่เก็บสมุด `helm list` (ไม่ใส่ตัวกรอง) แสดง `hello ... 11 ... uninstalled` จากนั้น `helm rollback hello 11 --wait` เปิดร้านกลับมาเป็น rev 12 `deployed` (2.6 วินาที) และระหว่างนี้ `helm install hello ...` จะได้ `cannot reuse a name that is still in use` (ใช้ `upgrade --install` แทนได้)
- `helm uninstall` ปกติลบสมุดด้วย หลังจากนั้น `helm history hello` = `Error: release: not found`
- ของที่ **ไม่** ถูกลบ: PVC ที่ StatefulSet สร้างจาก `volumeClaimTemplates` (ตู้เซฟ `data-som-db-0` ค้างหลัง uninstall สาขา dev — บทที่ 9 ก็เป็นแบบนี้), CRD ใน `crds/`, hook resource ที่ไม่มี delete policy, object ที่มี annotation `helm.sh/resource-policy: keep` และ namespace ที่สร้างด้วย `--create-namespace` (namespace ไม่ใช่ส่วนของ release)

ผลข้อแรกมีผลจริงใน LAB 12: ติดตั้งสาขา dev ใหม่ด้วย **รหัสเดิม** ได้ออเดอร์เดิมกลับมา (`orders=1`) แต่ถ้าใช้ **รหัสใหม่** ตู้เซฟเดิมยังล็อกด้วยรหัสเก่า ร้านเปิดไม่ได้ (LAB 12 ขั้น 12.9)

## 9. Helm 4 กับ server-side apply

### 9.1 ป้ายชื่อเจ้าของบนทุกช่อง

<p align="center" id="fig-35">
  <img src="images/35-field-managers.png" alt="รูปที่ 35 field manager" width="900"><br>
  <em><b>รูปที่ 35</b> server-side apply: ทุกช่องของ object มีป้ายชื่อเจ้าของ (field manager) เช่น helm, kubectl-client-side-apply, kube-controller-manager</em>
</p>

บทที่ 13 เราเจอ annotation `kubectl.kubernetes.io/last-applied-configuration` ของ `kubectl apply` แบบเดิม (**client-side apply**: kubectl คำนวณความต่าง 3 ทางบนเครื่องเราแล้วส่ง patch) Kubernetes มีอีกวิธีคือ **server-side apply (SSA)**: ส่ง "สิ่งที่ฉันต้องการ" ไปให้ API server แล้ว API server จดว่า **field ไหนเป็นของใคร** ไว้ใน `metadata.managedFields` ผู้เป็นเจ้าของเรียกว่า **field manager**

Helm 4 ใช้ SSA เป็นค่าเริ่มต้นด้วย field manager ชื่อ **`helm`** ผลจริง LAB 2 (Deployment ของ podinfo)

```text
kubectl -n helm-demo get deploy hello-podinfo -o jsonpath='{range .metadata.managedFields[*]}{.manager}{" "}{.operation}{"\n"}{end}'
helm Apply
kube-controller-manager Update
```

`helm` เป็นเจ้าของ field ที่ chart ตั้ง ส่วน `kube-controller-manager` เป็นเจ้าของ `status` ที่มันอัปเดต ร้านบท 013 ที่ผ่านมือหลายคนมีเจ้าของหลายราย (ผลจริง LAB 12 ขั้น 12.1)

```text
kube-controller-manager Update
kubectl-rollout Update
kubectl Update
kubectl-client-side-apply Update
kube-controller-manager Update
```

| field manager | มาจาก | เป็นเจ้าของอะไร |
|---|---|---|
| `kubectl-client-side-apply` | `kubectl apply` (ไฟล์ `20-web.yaml` ฯลฯ) | field ที่อยู่ในไฟล์ (image, env, initContainers ...) |
| `kubectl` | `kubectl set image`, `annotate` | image ที่ set, annotation change-cause |
| `kubectl-rollout` | `kubectl rollout restart` | annotation `restartedAt` |
| `kube-controller-manager` | controller ในคลัสเตอร์ | `status`, (HPA ปรับ `replicas` ผ่าน `/scale`) |
| `helm` (Apply) | Helm 4 | field ที่ chart ตั้ง |

> ตั้งแต่ kubectl รุ่นใหม่ `kubectl get -o yaml/json` ซ่อน `managedFields` ต้องเพิ่ม `--show-managed-fields` (ใน LAB 12 คำสั่ง python ที่อ่าน `-o json` เฉย ๆ ได้ `KeyError: 'managedFields'`) ส่วน `-o jsonpath` ยังอ่านได้

### 9.2 conflict: ช่องเดียวมีเจ้าของสองคน

<p align="center" id="fig-36">
  <img src="images/36-ssa-conflict.png" alt="รูปที่ 36 SSA conflict" width="900"><br>
  <em><b>รูปที่ 36</b> conflict: ช่องเดียวมีเจ้าของ 2 คนอยากตั้งค่าต่างกัน → Helm หยุด, --force-conflicts = ยึดเป็นของ helm</em>
</p>

เมื่อ `helm` ขอตั้งค่า field ที่ **เจ้าของอื่นถืออยู่และค่าต่างกัน** API server ปฏิเสธด้วย conflict แทนที่จะเขียนทับเงียบ ๆ (ป้องกันการแย่งกันแก้) ผลจริง LAB 12 ขั้น 12.6 (upgrade แรกหลังรับร้าน เปลี่ยน image เป็น 1.8)

```text
Error: UPGRADE FAILED: conflict occurred while applying object som-shop/som-web apps/v1, Kind=Deployment: Apply failed with 1 conflict: conflict with "kubectl-client-side-apply" using apps/v1: .spec.template.spec.containers[name="web"].image
```

ทางเลือก

1. **`--force-conflicts`**: บังคับให้ `helm` เป็นเจ้าของ field นั้นแทน (ใช้เมื่อแน่ใจว่าค่าใน chart คือค่าที่ถูก) ผลจริง: rev 4 deployed 15 วินาที ลูกค้า `ok=400 err=0` และ **upgrade/rollback ครั้งต่อไปไม่ต้อง force อีก** เพราะ field ถูกโอนเจ้าของแล้ว
2. แก้ chart ให้ไม่ตั้ง field นั้น (ปล่อยเจ้าของเดิมดูแล)
3. ให้เจ้าของเดิมเลิกถือ field (เช่น ลบ field นั้นด้วยเครื่องมือเดิม)

**field ที่ chart ไม่ได้ตั้งยังอยู่ตามเดิม** เพราะ SSA ลบเฉพาะ field ที่ manager คนเดิมเคยถือแล้วเลิกถือ ผลจริงหลังรับร้าน: annotation change-cause `1.7 เพิ่ม /api/work + HPA`, annotation `restartedAt`, HPA `behavior` (window 60 วินาทีจากบท 013) และ **initContainer `db-seed` ของบท 013** ยังอยู่ทั้งหมด เพราะ `kubectl-client-side-apply` ยังถือ field เหล่านั้น LAB 12 ขั้น 12.5c จึงต้องถอด `db-seed` ด้วย `kubectl patch` เอง (chart ใช้ hook seed แทน — หัวข้อ 11)

### 9.3 รับของเดิมที่ kubectl apply ไว้ (adopt)

<p align="center" id="fig-37">
  <img src="images/37-adopt-steps.png" alt="รูปที่ 37 รับของเดิมเข้า Helm" width="900"><br>
  <em><b>รูปที่ 37</b> รับของเดิมที่ kubectl apply ไว้: install ทับ → invalid ownership / --take-ownership → conflict / + --force-conflicts → ผ่าน (ถ้า selector ต่าง = field is immutable)</em>
</p>

Helm ไม่ยอมแตะ object ที่ไม่ใช่ของ release ตัวเอง โดยดูจาก label `app.kubernetes.io/managed-by: Helm` และ annotation `meta.helm.sh/release-name`/`meta.helm.sh/release-namespace` การย้ายของที่ติดตั้งด้วย `kubectl apply` เข้ามาอยู่ใต้ Helm จึงมี 3 ชั้น (ผลจริงทั้งหมด)

| ชั้น | คำสั่ง | ผลกับร้านน้องส้ม (LAB 12) | ผลกับ Traefik (LAB 10) |
|---|---|---|---|
| 1. install ทับ | `helm install ...` | `Secret "som-tls" in namespace "som-shop" exists and cannot be imported into the current release: invalid ownership metadata; label validation error: missing key "app.kubernetes.io/managed-by": must be set to "Helm" ...` — **ไม่สร้าง release** ปลอดภัย | `ServiceAccount "traefik" ... invalid ownership metadata` เหมือนกัน |
| 2. `--take-ownership` | ข้ามการตรวจ ownership แล้วติดป้าย | **conflict** กับ `kubectl-client-side-apply`: ConfigMap 3 field (`.data.SHOP_EYEBROW/FOOTER/PROMO`), Deployment 2, StatefulSet 1 (`.spec.volumeClaimTemplates`) → **rev 1 `failed`** | conflict: Service `.spec.selector`, Deployment 11 field → rev 1 `failed` |
| 3. `--take-ownership --force-conflicts` | ยึด field ที่ชน | **rev 2 `deployed` 16.4 วินาที** ออเดอร์เดิม `orders=3` อยู่ครบ ใบรับรองเดิม รหัสจาก lookup | `spec.selector: Invalid value: ...: field is immutable` → rev 2 `failed` |

ทำไมร้านรับได้แต่ Traefik รับไม่ได้: chart ร้านออกแบบให้ชื่อและ **selector** ตรงกับบท 013 (`app: som-web`) ส่วน Traefik chart ใช้ selector `app.kubernetes.io/name: traefik, app.kubernetes.io/instance: traefik-traefik` ขณะที่ static manifest ใช้ `app: traefik` และ `spec.selector` ของ Deployment **แก้ไม่ได้หลังสร้าง (immutable)** (บทที่ 7) ทางเดียวคือลบของเดิมแล้วติดตั้งใหม่ ซึ่งทำให้ประตูปิดชั่วครู่ (LAB 10 วัดได้ ~19 วินาที)

> ⚠️ **ห้าม `helm uninstall` release ที่ adopt ล้ม** ผลจริงจากการทดลองแยก: หลังชั้น 2–3 ล้ม ServiceAccount และ Service ถูกติดป้าย Helm ไปแล้ว `helm uninstall` จึง **ลบสองตัวนั้นทิ้ง** (เก็บไว้แค่ Deployment ที่ยังไม่ถูกยึด: `skipping delete of resource not owned by this release`) ถ้าเป็น Traefik ตัวจริง ประตูของทุกร้านจะปิดทันที ใน LAB 10 จึงให้ทำจริงแค่ชั้น 1 ส่วนชั้น 2–3 แสดงเป็น "ผลจริง ไม่ต้องทำตาม"

### 9.4 --server-side, --force-replace และเมื่อไรควรใช้

- `--server-side=true|false|auto`: install ใช้ `true` เป็นค่าเริ่มต้น upgrade/rollback ใช้ `auto` (ตามวิธีของ revision ก่อน) release ที่ติดตั้งด้วย Helm 3 (client-side) จึงยังอัปเกรดแบบเดิมจนกว่าจะเปลี่ยน
- `--force-replace` (ชื่อเดิม `--force`): ลบแล้วสร้าง object ใหม่แทนการ patch ใช้กับ field immutable ได้ แต่ **ทำให้ service สะดุด** (Pod ถูกลบ/สร้างใหม่) และไม่ควรใช้กับ object ที่ถือข้อมูล
- `--force-conflicts`: ใช้เมื่อ "รับร้าน" หรือมีคนแก้ด้วยมือแล้วต้องการให้ chart เป็นความจริงหนึ่งเดียว — หลังรับร้านแล้ว **ทีมควรเลิกแก้ object ด้วย `kubectl` ตรง ๆ** ไม่งั้นจะชนกันอีก

## 10. release เก็บที่ไหน

<p align="center" id="fig-38">
  <img src="images/38-release-secret.png" alt="รูปที่ 38 release Secret" width="900"><br>
  <em><b>รูปที่ 38</b> release แต่ละ revision เก็บเป็น Secret type helm.sh/release.v1 แค่พับ (base64) และห่อ (gzip) ไม่ได้ล็อก — ใบสั่งที่มีรหัสจึงอ่านได้</em>
</p>

Helm 3/4 ไม่มีฐานข้อมูลกลาง สมุดของแต่ละ release เก็บเป็น **Secret ใน namespace ของ release** หน้าละ 1 ซอง

```text
kubectl -n helm-demo get secret -l owner=helm
NAME                          TYPE                 DATA   AGE
sh.helm.release.v1.hello.v1   helm.sh/release.v1   1      13s
```

- ชื่อ `sh.helm.release.v1.<release>.v<revision>` type `helm.sh/release.v1` label `owner=helm, name=<release>, status=<สถานะ>, version=<rev>`
- เก็บ **10 revision ล่าสุด** (`HELM_MAX_HISTORY="10"` จาก `helm env`) ผลจริง LAB 4: หลัง rev 11 ซอง `v1` หายไป เหลือ `v2`–`v11`
- ข้อมูลใน key `release` = JSON ของ release ที่ **gzip แล้ว base64 โดย Helm** และ Kubernetes base64 อีกชั้นตามปกติของ Secret ถอดได้ด้วย

```bash
kubectl -n som-dev get secret sh.helm.release.v1.som.v1 -o jsonpath='{.data.release}' \
  | base64 -d | base64 -d | gzip -d | python3 -c 'import json,sys; print(sorted(json.load(sys.stdin).keys()))'
```

ได้ key `apply_method chart config hooks info manifest name namespace version` ซึ่ง **`config` คือ values ที่ผู้ใช้ส่ง** และ **`manifest` คือ YAML ทุก object ที่ render แล้ว** (รวม Secret ของร้าน) ผลจริง (ตัดให้สั้น)

```text
{"db": {"password": "meow1234"}, "hpa": {"enabled": false}, "ingress": {"enabled": true, "host": "dev.shop.localhost", "tls": false}, …}
['DATABASE_URL: "postgres://som:meow1234@som-db-0.som-db:5432/catshop"']
```

และใน LAB 12 ร้าน prod ที่ **ไม่ได้ `--set` รหัสเลย** (รหัสมาจาก `lookup`) manifest ใน release Secret ก็ยังมี `POSTGRES_PASSWORD`, `DATABASE_URL` และ **`tls.key` ของใบรับรอง** อยู่ เพราะเป็นผล render ของ Secret ทั้งก้อน

ผลด้านความปลอดภัย

1. **ใครอ่าน Secret ใน namespace ได้ = อ่านรหัสทุกตัวที่เคยผ่าน Helm ได้ (ย้อนหลัง 10 revision)** RBAC ที่ให้สิทธิ์ `get secrets` (บทที่ 11) จึงสำคัญกว่าเดิม
2. `helm get values som` ก็แสดง `password: meow1234` ตรง ๆ ใครที่รัน `helm` กับ namespace นั้นได้ก็เห็น
3. **ห้าม commit values ที่มีรหัสจริงลง git** (ส่งด้วย `--set` จาก secret store ของ CI หรือใช้ `lookup` แบบ chart นี้)
4. ระบบจริงใช้ **External Secrets Operator** (ดึงรหัสจาก Vault/คลาวด์มาเป็น Secret), **Sealed Secrets** (เก็บรหัสที่เข้ารหัสแล้วใน git) หรือ **SOPS** (เข้ารหัสไฟล์ values) เพื่อให้รหัสจริงไม่ผ่าน values ของ Helm
5. driver อื่น: ตั้ง `HELM_DRIVER=configmap` (เก็บเป็น ConfigMap — แย่กว่าเพราะ RBAC ของ ConfigMap มักหลวมกว่า) หรือ `sql` (เก็บใน PostgreSQL ภายนอก)

## 11. hooks และ helm test

### 11.1 hook: ขั้นตอนพิเศษตามจังหวะ

<p align="center" id="fig-39">
  <img src="images/39-hooks-timeline.png" alt="รูปที่ 39 จังหวะของ hook" width="900"><br>
  <em><b>รูปที่ 39</b> hook = ขั้นตอนพิเศษตามจังหวะ: pre-install ก่อนสร้าง, post-install หลังสร้าง (เติมสินค้าเข้าชั้น), test = ตรวจรับร้าน</em>
</p>

hook คือ object ปกติ (มักเป็น Job หรือ Pod) ที่มี annotation `helm.sh/hook` บอกว่าให้รันใน **จังหวะไหน** ของ lifecycle มี 9 ชนิด

| hook | รันเมื่อ |
|---|---|
| `pre-install` / `post-install` | ก่อน/หลังสร้าง object ของ release ครั้งแรก |
| `pre-upgrade` / `post-upgrade` | ก่อน/หลัง upgrade |
| `pre-rollback` / `post-rollback` | ก่อน/หลัง rollback |
| `pre-delete` / `post-delete` | ก่อน/หลัง uninstall |
| `test` | เมื่อสั่ง `helm test` |

บทที่ 9–13 ร้านเติมสินค้าเข้าชั้นด้วย **initContainer `db-seed`** ในทุก Pod หน้าร้าน (ทุกบูธใหม่รัน seed ซ้ำ) ชุด som-shop เปลี่ยนเป็น **hook Job** ที่รันครั้งเดียวหลัง install/upgrade (`templates/seed-job.yaml`)

```gotemplate
apiVersion: batch/v1
kind: Job
metadata:
  name: {{ $fn }}-seed
  labels:
    {{- include "som-shop.labels" . | nindent 4 }}
  annotations:
    "helm.sh/hook": post-install,post-upgrade
    "helm.sh/hook-weight": "0"
    "helm.sh/hook-delete-policy": before-hook-creation,hook-succeeded
spec:
  backoffLimit: 3
  template:
    spec:
      restartPolicy: OnFailure
      containers:
        - name: seed
          image: {{ include "som-shop.webImage" . }}
          command: ["node", "scripts/seed.mjs"]
```

ลำดับของ `helm install --wait` ชุดร้าน: render → สร้าง object ทั้งหมด → **รอให้พร้อม (เพราะ `--wait`)** → สร้าง Job seed (post-install) → รอ Job สำเร็จ → ลบ Job (`hook-succeeded`) → `deployed` ผลจริงใน LAB 9 (`kubectl get pod -w` ระหว่าง upgrade): Pod หน้าร้านใหม่ `Running 1/1` ก่อน แล้ว `som-seed-qk2k5` จึงเกิด → `Completed` → หายไป `kubectl get job` ได้ `No resources found`

- `hook-weight`: hook ชนิดเดียวกันหลายตัวรันเรียงจากน้อยไปมาก (เป็นข้อความตัวเลข เช่น `"-5"`, `"0"`)
- **hook ล้ม = release ล้ม**: ใน LAB 12 ติดตั้งสาขา dev ใหม่ด้วยรหัสใหม่ทั้งที่ตู้เซฟเดิมใช้รหัสเก่า (ไม่ใส่ `--wait`) ได้ `Error: INSTALLATION FAILED: failed post-install: resource Job/som-dev/som-seed not ready. status: Failed, message: Job Failed. failed: 1/1` ใน 45.7 วินาที (ถ้าใส่ `--wait` จะล้มก่อนถึง hook ที่ `resource Deployment/som-dev/som-web not ready ... Available: 0/1` เพราะหน้าร้านก็ต่อ db ไม่ได้)
- hook **ไม่ใช่ส่วนของ release**: ไม่อยู่ใน `helm get manifest` (ดูได้ด้วย `helm get hooks`) และ `helm uninstall` ไม่ลบให้ ต้องพึ่ง delete policy

### 11.2 hook-delete-policy

<p align="center" id="fig-40">
  <img src="images/40-hook-delete-policy.png" alt="รูปที่ 40 hook-delete-policy" width="900"><br>
  <em><b>รูปที่ 40</b> hook-delete-policy: before-hook-creation (ค่าเริ่มต้น), hook-succeeded, hook-failed — และ helm uninstall ไม่ลบ hook ให้</em>
</p>

| policy | ลบเมื่อ | ใช้เมื่อ |
|---|---|---|
| `before-hook-creation` (ค่าเริ่มต้นถ้าไม่ระบุ) | ก่อนสร้าง hook ตัวใหม่ชื่อเดิมในครั้งถัดไป | ให้ hook รันซ้ำได้ทุก upgrade โดยชื่อไม่ชน |
| `hook-succeeded` | ทันทีที่ hook สำเร็จ | ไม่ให้ Job ที่เสร็จแล้วค้าง |
| `hook-failed` | เมื่อ hook ล้ม | (ระวัง: ลบแล้วจะดู log ไม่ได้) |

ชุดร้านใช้ `before-hook-creation,hook-succeeded`: สำเร็จก็ลบทิ้ง ล้มก็ **เก็บไว้ให้ดู log** (ใน LAB 12 เห็น `pod/som-seed-9sjtp 0/1 Error` และ `job.batch/som-seed Failed 0/1`) แล้วรอบหน้าลบก่อนสร้างใหม่

### 11.3 helm test: ผู้ตรวจรับร้าน

<p align="center" id="fig-41">
  <img src="images/41-helm-test-inspector.png" alt="รูปที่ 41 helm test ผู้ตรวจรับร้าน" width="900"><br>
  <em><b>รูปที่ 41</b> helm test: Pod ตรวจรับร้านเรียก /api/health ถ้าจบด้วย exit 0 = Succeeded, --logs ดูผลตรวจ</em>
</p>

test คือ hook ชนิด `test` ที่รันเมื่อสั่ง `helm test` เท่านั้น ผ่าน = container จบด้วย exit code 0 ชุดร้านมี `templates/tests/test-health.yaml` (image `curlimages/curl:8.22.0`) เรียก 3 endpoint ผ่าน Service ภายใน (`set -e` + `curl -f` = ผิดตัวไหนก็ล้ม)

```text
helm test som -n som-dev --logs
...
TEST SUITE:     som-test-health
Last Started:   Tue Oct  6 05:53:45 2026
Last Completed: Tue Oct  6 05:53:53 2026
Phase:          Succeeded

POD LOGS: som-test-health (curl)
health:   {"ok":true,"db":"up"}
whoami:   som-web-64c9f5cd95-t5pj7 1.7
products: ok
```

- `--logs` แสดง log ของ Pod ทดสอบ (Helm 4 เก็บ log ก่อนลบตาม delete policy)
- `--filter name=<ชื่อ test>` เลือกรันบางตัว
- `helm test` ใช้ test ของ **release ที่ติดตั้งอยู่** ไม่ใช่ไฟล์ในเครื่อง แก้ test แล้วต้อง upgrade ก่อน
- test ตรวจ "ร้านทำงานจริงไหม" ซึ่ง `--wait` (ดูแค่ Ready) และ schema (ดูแค่รูปร่างค่า) ตอบไม่ได้ เหมาะใส่เป็นขั้นสุดท้ายของ CI

