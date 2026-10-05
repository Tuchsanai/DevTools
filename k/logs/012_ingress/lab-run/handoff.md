# Handoff บท 012 Ingress: container ทดลองที่เปิดไว้สำหรับ screenshot (5 ต.ค. 2569)

## Container

| หัวข้อ | ค่า |
|---|---|
| ชื่อ | `k8s-lab-ing012lab-609d0f` (owner `agent-012-lab`, image `tuchsanai/devtools-kind:2569_1` = `8108a1bc7901`, `--privileged --hostname k8s-lab`) |
| SSH | `ssh -p 2224 root@<gateway>` (หรือ `localhost:2224` บน Docker host), รหัส LAB `passwd` · password และ key ผ่าน (`ssh-check.log`) |
| NodePort → host port | `30080` → **`30090`** (Traefik web/HTTP) · `30081` → **`30091`** (websecure/HTTPS) · `30082` → **`30092`** (dashboard) |
| gateway (จาก agent) | `172.18.0.1` |
| โฟลเดอร์ LAB ใน container | `/workspace/012_kubernetes_ingress/02_LAB` (docker cp ไม่มี bind mount), ร้านอยู่ที่ `.../02_LAB/som-shop-v8` (มี `tls.crt`/`tls.key` ใบ `CN=shop.localhost` ที่ใช้ใน Secret `som-tls`) |
| ลบ | ผู้ประสานงานลบเอง: `docker rm -fv k8s-lab-ing012lab-609d0f` (agent ไม่ได้ลบ) |

## สภาพตอนส่งมอบ (ท้าย LAB 10, ดู `lab10-final-state.log`)

- Traefik v3.7.13 (namespace `traefik`) Service NodePort `80:30080, 443:30081, 8080:30082`, IngressClass `traefik (default)`, CRD traefik.io 10 ตัว, **ไม่มี** CRD Gateway API (LAB เสริมคืนสภาพแล้ว), ไม่มี namespace `ingress-demo` (ลบหลัง LAB 9)
- namespace `som-shop`: `som-web` 3/3 (**som-shop-web:1.6**, ClusterIP), `som-admin` 1/1 (ClusterIP), `som-db-0` (PVC `data-som-db-0`), Ingress `som-shop` (shop.localhost) + `som-admin` (admin.localhost) ทั้งคู่ `80, 443` ADDRESS `localhost`, Middleware `redirect-https` (port "30081") + `admin-auth` (Secret `som-admin-auth`), Secret `som-tls` (SAN shop.localhost, admin.localhost, localhost)
- ออเดอร์ **4** รายการ (`orders=4 products=6`), footer `Next.js + PostgreSQL · Kubernetes LAB 012 · เข้าร้านทาง Ingress https://shop.localhost`, eyebrow `⚓ ท่าเรือ Kubernetes · Ingress`
- rollout history: `1 1.5 หน้าร้านผ่าน Ingress` / `2 1.5 หน้าร้านผ่าน Ingress` / `3 1.6 ผ่าน Ingress`
- บัญชีหลังร้าน (ค่าตัวอย่างเพื่อการเรียน): `som` / `meow-admin-123`

## ข้อสำคัญก่อนเปิด browser: ห้ามเปิดด้วยพอร์ต 30090/30091 ตรง ๆ

- `http://<gateway>:30090/` (ไม่มีชื่อ) ได้ **404 page not found** เพราะไม่มีป้ายไหนรับ Host `172.18.0.1` (ใช้เป็นฉาก "host ผิด = 404" ได้)
- Middleware `redirect-https` เทียบพอร์ตใน Host: ถ้า URL เป็น `https://shop.localhost:30091` จะถูก 301 กลับไป `:30081` ทุกครั้ง (บนเครื่องนี้ 30081 คือ k8s-lab **ของผู้เรียน** ห้ามแตะ) → ให้ browser ใช้ URL พอร์ต 30080/30081/30082 เหมือนนักศึกษา แล้ว map ที่ระดับ resolver ไป gateway:30090/30091/30092

### Chromium บนเครื่องนี้: `--host-resolver-rules` (ทดสอบแล้ว `browser-check.log`)

```text
--host-resolver-rules=MAP shop.localhost:30080 172.18.0.1:30090, MAP shop.localhost:30081 172.18.0.1:30091, MAP admin.localhost:30080 172.18.0.1:30090, MAP admin.localhost:30081 172.18.0.1:30091, MAP other.localhost:30080 172.18.0.1:30090, MAP localhost:30082 172.18.0.1:30092
```

สคริปต์ Playwright Python ที่ใช้ยืนยัน: `logs/012_ingress/scratch/pw-check.py` (`python3 pw-check.py 172.18.0.1 30090`) — สร้าง rules ข้างบนให้เอง ผลจริง:

```text
shop: final url=https://shop.localhost:30081/ status=200 title=ร้านอาหารแมวน้องส้ม
shop redirect chain (ล่าสุดก่อน): ['https://shop.localhost:30081/', 'http://shop.localhost:30080/']
footer: 🐱 เสิร์ฟโดย Pod: som-web-bd5bb7d66-4cm5b | Next.js + PostgreSQL · Kubernetes LAB 012 · เข้าร้านทาง Ingress https://shop.localhost
admin no auth: 401
admin with auth: https://admin.localhost:30081/ 200 h1=หลังร้านน้องส้ม (admin)
admin /stats: 200 som-web-bd5bb7d66-4cm5b 1.6 orders=4 products=6
other: 404 404 page not found
dashboard: 200 title=Dashboard - Traefik Proxy
```

- สคริปต์ใช้ `ignore_https_errors=True` ถ้าต้องการภาพหน้าเตือน `NET::ERR_CERT_AUTHORITY_INVALID` ให้เปิด context ใหม่โดยไม่ใส่ตัวเลือกนี้ (ไม่ได้ถ่ายในรอบนี้)
- Playwright MCP ที่เปิดอยู่แล้วใส่ `--host-resolver-rules` ไม่ได้ ถ้าจะใช้ต้องเปิดตอน launch หรือใช้ `page.route()` ส่งต่อ (ต้องคง Host header `shop.localhost:30081` ไว้ ไม่งั้นโดน redirect วน)
- **คืนสภาพ**: rules อยู่แค่ใน process Chromium ที่เปิด ปิด browser แล้วหายเอง ไม่ต้องแก้ `/etc/hosts`

### curl จากเครื่องนี้ (ทดสอบแล้ว `host-final.log`)

```bash
G=172.18.0.1
# --connect-to = URL เหมือนนักศึกษา (พอร์ต 30080/30081) แต่ต่อไปที่ gateway:3009x — วิธีที่ตรงที่สุด
curl -sk -L --connect-to shop.localhost:30080:$G:30090 --connect-to shop.localhost:30081:$G:30091 -o /dev/null -w '%{http_code} %{url_effective}\n' http://shop.localhost:30080/   # 200 https://shop.localhost:30081/
curl -sk --connect-to shop.localhost:30081:$G:30091 https://shop.localhost:30081/api/stats                        # som-web-… 1.6 orders=4 products=6
curl -sk --connect-to admin.localhost:30081:$G:30091 -o /dev/null -w '%{http_code}\n' https://admin.localhost:30081/   # 401
curl -sk --connect-to admin.localhost:30081:$G:30091 -u som:meow-admin-123 https://admin.localhost:30081/stats   # 200 … orders=4
curl -si -H 'Host: shop.localhost:30080' http://$G:30090/ | grep -iE '^HTTP|^location'                          # 301 Location: https://shop.localhost:30081/
curl -s http://$G:30092/dashboard/ -o /dev/null -w '%{http_code}\n'                                             # 200
```

(ถ้าใช้ `--resolve shop.localhost:30091:$G https://shop.localhost:30091/` ตรง ๆ จะได้ `301 Moved Permanently` วนกลับ 30081 เพราะ Host มีพอร์ต 30091 ต้องเติม `-H 'Host: shop.localhost:30081'` — ทดสอบแล้วทั้งสองแบบ)

## ฉาก screenshot ที่แนะนำ (ทุกคำสั่ง 🐧 รันใน container ผ่าน `ssh -p 2224 root@<gateway>` แล้ว `cd /workspace/012_kubernetes_ingress/02_LAB/som-shop-v8`)

| ฉาก | วิธี | ผลที่ต้องเห็น |
|---|---|---|
| 1. redirect HTTP → HTTPS | Chromium (rules ข้างบน) เปิด `http://shop.localhost:30080` | แถบ URL เปลี่ยนเป็น `https://shop.localhost:30081/` หน้าร้าน "ร้านอาหารแมวน้องส้ม" เวอร์ชัน 1.6, ออเดอร์ 4, footer LAB 012 |
| 2. หน้าเตือนใบรับรอง | context ไม่ ignore HTTPS errors เปิด `https://shop.localhost:30081` | `NET::ERR_CERT_AUTHORITY_INVALID` (self-signed) |
| 3. admin ก่อน login | เปิด `https://admin.localhost:30081/` ไม่ใส่บัตร | 401 (Chromium ขึ้นกล่อง login / หน้า `401 Unauthorized`) |
| 4. admin หลัง login | context `http_credentials som / meow-admin-123` เปิด `http://admin.localhost:30080/` แล้ว `/stats` | หน้า "หลังร้านน้องส้ม (admin)" และ `som-web-… 1.6 orders=4 products=6` |
| 5. host ผิด = 404 | `http://other.localhost:30080/` หรือ `http://172.18.0.1:30090/` | `404 page not found` |
| 6. Traefik dashboard | `http://localhost:30082/dashboard/` (rules map → 30092) หรือตรง ๆ `http://172.18.0.1:30092/dashboard/` (ไม่มี Host rule จึงเปิดตรงได้) | Dashboard - Traefik Proxy; HTTP Routers 7 ตัว = ของร้าน 4 (`som-shop-som-shop-shop-localhost@kubernetes`, `websecure-som-shop-som-shop-shop-localhost@kubernetes`, admin ×2 มี middleware redirect + admin-auth) + ภายใน 3 (`api@internal`, `dashboard@internal`, `ping@internal`) |
| 7. terminal: ประตูเดียว | `kubectl get svc -A \| grep -E 'NodePort\|som-'; kubectl -n som-shop get ing` | traefik NodePort 30080/30081/30082 อย่างเดียว, som-web/som-admin ClusterIP, Ingress 2 แผ่น `80, 443` |
| 8. terminal: redirect + basic auth | `curl -si http://shop.localhost:30080/ \| grep -iE '^HTTP\|^location'; curl -s --cacert tls.crt -o /dev/null -w '%{http_code}\n' https://admin.localhost:30081/; curl -s --cacert tls.crt -u som:meow-admin-123 https://admin.localhost:30081/stats` | `301` + `Location: https://shop.localhost:30081/`, `401`, `… orders=4 …` |
| 9. rolling update ผ่าน Ingress ระหว่าง hit.sh | terminal 1: `./hit.sh -q https://shop.localhost:30081/api/whoami 300 0.05` · terminal 2 (ภายใน 2 วิ): `kubectl -n som-shop rollout restart deploy/som-web` | แถว `.` ไม่มี `x`, `ok=300 err=0` (ทดสอบจริง 2 รอบ: 250/0 และ 300/0) |

ข้อควรระวังตอนถ่าย:

- ถ้า POST ออเดอร์เพิ่มให้คงไว้ 3–5 รายการ (ตอนนี้ 4) — `curl -sk -XPOST -H "content-type: application/json" -d '{"product_id":5,"qty":1}' https://shop.localhost:30081/api/orders`
- หลัง `rollout restart` เสร็จ Pod เก่ายังตอบได้อีกราว 5 วิ (preStop) ภาพ/ข้อความแรกอาจยังเป็น Pod เก่า รอ 10 วิก่อนถ่าย
- ทุกครั้งที่ Traefik restart จะมี `ERR middleware "som-shop-…@kubernetescrd" does not exist` 4 บรรทัดชั่วครู่ (หายเองภายในวินาที) อย่าถ่าย log ช่วงนั้นเป็น "error"
- อย่าเปิด `localhost:30080–30082` บนเครื่องนี้ด้วยพอร์ตจริง (เป็นของ `k8s-lab` ผู้เรียน)
