# Handoff: container สำหรับถ่ายภาพหน้าจอบท 014 (Helm)

> สร้างเมื่อ 5–6 ต.ค. 2569 (log ใช้เวลา host UTC 22:39–23:11, ในคลัสเตอร์แสดงเวลาไทย 05:39–06:11)
> **container นี้ยังเปิดอยู่ตามคำสั่ง ห้ามลบจนกว่าจะถ่ายภาพเสร็จ** ลบด้วย `k8s-lab.sh down k8s-lab-helm014-0044d7`

## container

| หัวข้อ | ค่า |
|---|---|
| ชื่อ | `k8s-lab-helm014-0044d7` (owner label `helm014`, hashid `0044d7`) |
| image | `tuchsanai/devtools-kind:2569_1` (ID `8108a1bc7901`) `--privileged --hostname k8s-lab --cpus=4 --memory=8g` ไม่มี bind mount |
| SSH | host port **2225** → 22 (`ssh -p 2225 root@<host>` รหัส `passwd` เฉพาะ LAB) |
| NodePort | **30080 → 30100**, **30081 → 30101**, **30082 → 30102** |
| gateway (จาก agent ที่อยู่ใน container) | **`172.18.0.1`** (ถ้ารันบน Docker host โดยตรงใช้ `127.0.0.1`) |
| ไฟล์บทใน container | `/workspace/014_kubernetes_helm/02_LAB` (+ `012_kubernetes_ingress`, `013_kubernetes_hpa` ที่ใช้จำลองสภาพท้ายบท 013) |

## สภาพปัจจุบัน (ตรวจแล้ว)

```text
helm list -A
NAME            NAMESPACE    REVISION  STATUS    CHART                  APP VERSION
metrics-server  kube-system  1         deployed  metrics-server-3.14.0  0.9.0
som             som-dev      1         deployed  som-shop-0.1.0         1.7
som             som-shop     6         deployed  som-shop-0.1.0         1.7
traefik         traefik      1         deployed  traefik-41.6.1         v3.7.13
```

- **prod** (`som-shop`): release `som` rev 6, หน้าร้าน `som-shop-web:1.8` (ป้ายบนหน้าเว็บ "เวอร์ชัน 1.8"), HPA `som-web` 2–6 (`cpu: 2%/50%`), Ingress `som-web` (shop.localhost, TLS ใบเดิมจากบท 012), `orders=5`, หัวเว็บ `⚓ ท่าเรือ Kubernetes · Helm`, แถบ `🎉 เปิดสาขาใหม่ด้วย Helm คำสั่งเดียว`, footer `... Kubernetes LAB 014 · ติดตั้งทั้งร้านด้วย Helm`; หลังร้าน `som-admin` (บัตร `som` / `meow-admin-123`) ยังใช้ได้
- **dev** (`som-dev`): release `som` rev 1, รุ่น 1.7 ชื่อ `ร้านอาหารแมวน้องส้ม (dev)` ธีม `sunset` แถบ `🧪 สาขาทดลอง — ของจริงอยู่ที่ shop.localhost`, `orders=0`, http เท่านั้น (`dev.shop.localhost:30080`)
- Traefik (chart 41.6.1) + metrics-server (chart 3.14.0) ติดตั้งจาก chart แล้ว ไม่มี static เหลือ (CRD ของ Traefik 25 ตัวยังอยู่)
- revision ของ prod: 1 failed (take-ownership conflict) → 2 deployed (adopt, 1.7) → 3 failed (image conflict) → 4 deployed (1.8, `--force-conflicts`) → 5 `Rollback to 2` (1.7) → 6 deployed (1.8)

## ให้ Chromium เปิด `*.localhost` ผ่าน gateway

**สำคัญ:** Middleware `som-redirect-https` ส่งต่อไปพอร์ต `30081` เสมอ (และ Traefik redirect ทุก request ที่ Host มีพอร์ตอื่น) **ห้ามเปิด `https://shop.localhost:30101` ตรง ๆ** (ได้ `301` วนไป 30081) ให้ใช้ URL พอร์ตเดียวกับนักศึกษา (30080/30081/30082) แล้ว map ทั้ง host และ port ด้วย `--host-resolver-rules` (ทดสอบแล้วกับ `/opt/ms-playwright/chromium-1247` แบบ `--headless=new --dump-dom` ได้หน้า "เวอร์ชัน 1.8", หน้า dev และ `<title>Traefik Proxy`):

```bash
GW=172.18.0.1
chrome --ignore-certificate-errors \
  --host-resolver-rules="MAP shop.localhost:30081 $GW:30101, MAP admin.localhost:30081 $GW:30101, MAP *.localhost:30080 $GW:30100, MAP localhost:30082 $GW:30102"
```

Playwright: `chromium.launch({ args: ['--host-resolver-rules=MAP shop.localhost:30081 172.18.0.1:30101, MAP admin.localhost:30081 172.18.0.1:30101, MAP *.localhost:30080 172.18.0.1:30100, MAP localhost:30082 172.18.0.1:30102'] })` + `ignoreHTTPSErrors: true` (ใบรับรอง self-signed ของ LAB)

| ฉาก | URL (เหมือนที่นักศึกษาพิมพ์) |
|---|---|
| หน้าร้าน prod | `http://shop.localhost:30080` → 301 → `https://shop.localhost:30081/` |
| หน้าร้าน dev | `http://dev.shop.localhost:30080/` |
| หลังร้าน | `https://admin.localhost:30081/` (basic auth `som` / `meow-admin-123`) |
| Traefik dashboard | `http://localhost:30082/dashboard/` (routers: `#/http/routers`) |

ตรวจจากฝั่ง agent ด้วย curl ได้ (`--connect-to` คงพอร์ตใน Host):
`curl -sk --connect-to shop.localhost:30081:172.18.0.1:30101 https://shop.localhost:30081/api/whoami`

## คำสั่งฉากเพิ่ม (รันใน container)

นำหน้าทุกคำสั่งด้วย `docker exec k8s-lab-helm014-0044d7 bash -lc 'cd /workspace/014_kubernetes_helm/02_LAB && <คำสั่ง>'` (หรือ SSH port 2225)

```bash
# 1) ย้อน prod เป็น 1.7 (หน้าร้านป้าย "เวอร์ชัน 1.7") — ได้ revision ใหม่ 7 "Rollback to 2"
helm rollback som 2 -n som-shop --wait
# 2) อัปเกรดกลับเป็น 1.8 (ป้าย "เวอร์ชัน 1.8") — revision 8, ไม่ต้อง --force-conflicts แล้ว (~15 วินาที)
helm upgrade som charts/som-shop -n som-shop -f charts/values-prod.yaml --set web.image.tag=1.8 --wait
# ระหว่างนั้นยิงลูกค้า (หน้าต่างที่ 2) ดู err=0
./hit.sh -q https://shop.localhost:30081/api/whoami 300 0.1
# 3) สมุดบันทึก / รายการสาขา / ผู้ตรวจรับร้าน
helm history som -n som-shop
helm list -A
helm test som -n som-shop --logs
helm test som -n som-dev --logs
# 4) ถอดซองในสมุด (ในภาพให้ตัดค่าให้สั้น)
kubectl -n som-shop get secret sh.helm.release.v1.som.v2 -o jsonpath='{.data.release}' | base64 -d | base64 -d | gzip -d | python3 -c 'import json,sys; print(json.dumps(json.load(sys.stdin)["config"],ensure_ascii=False))'
# 5) HPA / มิเตอร์
kubectl -n som-shop get hpa; kubectl top pod -n som-shop
```

ข้อสังเกตตอนถ่าย: เลข revision จะเพิ่มทุกครั้งที่ rollback/upgrade (ภาพที่อ้างเลขต้องดูเลขจริงขณะถ่าย) และ refresh หน้าร้านจะเห็นชื่อ Pod 2 ชื่อ (HPA ถือ 2 บูธ)

## คืนสภาพ (ถ้าถ่ายแล้วสภาพเปลี่ยน)

```bash
cd /workspace/014_kubernetes_helm/02_LAB
helm upgrade som charts/som-shop -n som-shop -f charts/values-prod.yaml --set web.image.tag=1.8 --wait   # prod กลับ 1.8
helm status som -n som-dev >/dev/null 2>&1 || helm install som charts/som-shop -n som-dev --create-namespace -f charts/values-dev.yaml --set db.password=meow1234 --wait   # dev กลับมา
curl -sk https://shop.localhost:30081/api/stats; curl -s http://dev.shop.localhost:30080/api/stats
```

เลิกใช้แล้ว: `k8s-lab.sh down k8s-lab-helm014-0044d7` (ลบ kind cluster และข้อมูล DinD ทั้งหมด) แล้ว `k8s-lab.sh ls` ต้องไม่เหลือชื่อนี้
