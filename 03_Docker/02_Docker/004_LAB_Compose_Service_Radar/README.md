# 004 LAB — Compose Service Radar

ปลุก web + API + Redis ด้วยคำสั่งเดียว แล้วตาม request ข้าม service-name DNS, health gate, network สองชั้น และ named volume

## เป้าหมาย

- อ่าน `compose.yaml` แบบ Compose Specification (ไม่ต้องใส่ `version:`)
- เข้าใจ service discovery: เรียก `api:8000` และ `redis:6379` แทน IP
- ใช้ `healthcheck` ร่วมกับ `depends_on: condition: service_healthy`
- แยก public frontend network ออกจาก private backend network
- ใช้ `config`, `ps`, `logs`, `exec`, `down`

ใช้เวลาประมาณ 45 นาที · SSH `2225` · Web `18084`

## 0) เปิดเครื่อง LAB (ทำบน host)

```bash
docker rm -f devtools-compose-service-radar 2>/dev/null
docker run -dit \
  --name devtools-compose-service-radar \
  --privileged \
  -p 2225:22 \
  -p 18084:8080 \
  tuchsanai/devtools:2569_1

docker exec devtools-compose-service-radar mkdir -p /workspace/lab
docker cp 004_LAB_Compose_Service_Radar/. \
  devtools-compose-service-radar:/workspace/lab/

ssh root@localhost -p 2225
# password: passwd
```

ภายใน SSH:

```bash
cd /workspace/lab
docker compose version
docker compose config --services
docker compose config --networks
```

## 1) เปิด stack และรอ health gate

```bash
docker compose up -d --build
docker compose ps
```

ลำดับควรเป็น Redis healthy → API healthy → Web healthy เพราะ `depends_on` ตรวจ readiness ไม่ใช่แค่ process เริ่มแล้ว

เปิด `http://localhost:18084` แล้ว refresh 2–3 ครั้ง ตัวเลข request ต้องเพิ่มขึ้น

## 2) พิสูจน์ service-name DNS

```bash
docker compose exec web python -c \
  "import socket; print('api ->', socket.gethostbyname('api'))"

docker compose exec api python -c \
  "import socket; print('redis ->', socket.gethostbyname('redis'))"

docker compose exec web python -c \
  "import urllib.request; print(urllib.request.urlopen('http://api:8000/stats').read().decode())"
```

อย่าคัดลอก IP ที่เห็นไปใส่ config เพราะ IP เปลี่ยนเมื่อ recreate แต่ชื่อ service คงเดิม

## 3) ตรวจ network และขอบเขตการเปิด port

```bash
docker network ls --filter name=devtools-compose-radar
docker compose port web 8080
docker compose exec redis redis-cli GET radar:visits
```

มีเพียง `web` ที่ publish port; API กับ Redis ใช้ `expose`/internal network และเข้าถึงจาก host โดยตรงไม่ได้

## 4) Persistence drill

```bash
curl -fsS http://localhost:8080/data
docker compose down
docker compose up -d
curl -fsS http://localhost:8080/data
```

ค่า `visits` ต้องต่อจากเดิม เพราะ `down` ไม่ลบ named volume หากไม่ใส่ `-v`

## Cleanup (บังคับ)

ใน SSH:

```bash
docker compose down -v --remove-orphans
exit
```

บน host:

```bash
docker rm -f devtools-compose-service-radar
docker ps -a --filter "name=^devtools-"
```

## แหล่งอ้างอิง

- [Docker Compose networking](https://docs.docker.com/compose/how-tos/networking/)
- [Control startup order](https://docs.docker.com/compose/how-tos/startup-order/)
