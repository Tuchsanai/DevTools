# Handoff — container ทดลอง LAB 002 (ยังเปิดอยู่เพื่อถ่าย screenshot)

> สร้างเมื่อ 4 ต.ค. 2569 (~18:07 น.) โดย agent ทดสอบ LAB 002 — **ผู้ประสานงานเป็นคนลบ container เอง**

| หัวข้อ | ค่า |
|---|---|
| ชื่อ container | `k8s-lab-pod002-20f6d7` |
| image | `tuchsanai/devtools-kind:2569_1` (ID `8108a1bc7901`) `--privileged --hostname k8s-lab` |
| SSH host port | **`2224`** → 22 (user `root` / รหัส `passwd`) ไม่ได้ publish NodePort/Jupyter |
| คลัสเตอร์ | kind `lab` (context `kind-lab`), K8s v1.37.0, 3 node Ready |
| Pod ที่รันอยู่ | `som-shop` (2/2 Running, IP 10.244.3.16, node lab-worker2) — สร้างใหม่หลังทดสอบลบ Pod แล้ว ข้อมูลเป็นค่าเริ่มต้น (0 ออเดอร์, stock ตั้งต้น) |
| port-forward ใน container | `kubectl port-forward --address 127.0.0.1 pod/som-shop 3000:3000` (รันด้วย setsid/nohup, log ที่ `/tmp/pf-shop.log` ใน container) |

## เปิดหน้าร้าน

จาก Docker host (Windows/WSL ที่ publish port):

```bash
ssh -p 2224 -L 3000:localhost:3000 root@localhost      # รหัส passwd, ค้างหน้าต่างไว้
# แล้วเปิด browser http://localhost:3000
```

ถ้า agent อยู่ใน container (มี `/.dockerenv`) ให้ใช้ gateway แทน localhost และเลือก local port ว่าง เช่น:

```bash
ssh -f -N -p 2224 -L 13000:localhost:3000 root@172.18.0.1   # (ทดสอบแล้วว่าใช้ได้ ใช้ askpass ส่งรหัส passwd)
curl -s http://localhost:13000/api/health                     # {"ok":true,"db":"up"}
```

ถ้าต้องการให้หน้าเว็บมีออเดอร์ (ส่วน "ออเดอร์ล่าสุด" ไม่ว่าง) กดปุ่ม 🛒 สั่งซื้อ ในหน้าเว็บ หรือ:

```bash
docker exec k8s-lab-pod002-20f6d7 curl -s -X POST localhost:3000/api/orders -H 'Content-Type: application/json' -d '{"product_id":1,"qty":1}'
```

## ถ้า port-forward หลุด (เช่นลบ/สร้าง Pod ใหม่)

```bash
docker exec k8s-lab-pod002-20f6d7 bash -c 'pkill -f "kubectl port-forward pod/[s]om-shop"; setsid nohup kubectl port-forward --address 127.0.0.1 pod/som-shop 3000:3000 > /tmp/pf-shop.log 2>&1 < /dev/null & sleep 2; cat /tmp/pf-shop.log'
```

## ลบเมื่อเสร็จ

```bash
docker rm -fv k8s-lab-pod002-20f6d7
docker ps -a --filter "name=^k8s-lab-"
```
