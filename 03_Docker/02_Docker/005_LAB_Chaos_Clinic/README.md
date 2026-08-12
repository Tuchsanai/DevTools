# 005 LAB — Chaos Clinic

รับเคส container ที่ “running แต่ unhealthy” วินิจฉัยจากหลักฐาน แก้ config แล้วจงใจ crash เพื่อดู restart policy และ restart count

## เป้าหมาย

- แยก process state (`running`) จาก readiness (`healthy`)
- อ่าน health history, structured logs, resource usage และ restart count
- แก้ runtime config ด้วย Compose recreate โดยไม่แก้ image
- เห็น secure defaults: non-root, read-only root filesystem และ dropped capabilities

ใช้เวลาประมาณ 35 นาที · SSH `2226` · Web `18085`

## 0) เปิดเครื่อง LAB (ทำบน host)

```bash
docker rm -f devtools-chaos-clinic-host 2>/dev/null
docker run -dit \
  --name devtools-chaos-clinic-host \
  --privileged \
  -p 2226:22 \
  -p 18085:8080 \
  tuchsanai/devtools:2569_1

docker exec devtools-chaos-clinic-host mkdir -p /workspace/lab
docker cp 005_LAB_Chaos_Clinic/. \
  devtools-chaos-clinic-host:/workspace/lab/

ssh root@localhost -p 2226
# password: passwd
```

ภายใน SSH:

```bash
cd /workspace/lab
docker compose up -d --build
sleep 10
docker compose ps
```

ค่าเริ่มต้นตั้งใจให้ผิด: process ยัง `Up` แต่ health เป็น `unhealthy`

เปิด `http://localhost:18085` จะเห็นไฟสีแดง

## 1) Triage จากหลักฐาน

```bash
curl -i http://localhost:8080/health
docker compose logs --tail 20 clinic

docker inspect -f '{{json .State.Health}}' \
  devtools-chaos-clinic-clinic-1

docker stats --no-stream devtools-chaos-clinic-clinic-1
docker exec devtools-chaos-clinic-clinic-1 id
```

หลักฐานชี้ว่า `HEALTH_MODE` ไม่ใช่ `ready` — ไม่ต้องเดา ไม่ต้อง rebuild

## 2) รักษาด้วย config แล้ว recreate

```bash
HEALTH_MODE=ready RELEASE=stable \
  docker compose up -d --force-recreate

sleep 8
docker compose ps
curl -fsS http://localhost:8080/health
```

refresh browser: ไฟต้องเป็นสีเขียวและ release เป็น `stable`

## 3) Inject failure และดู restart policy

```bash
curl -fsS http://localhost:8080/crash
sleep 3

docker inspect -f \
  'status={{.State.Status}} restart_count={{.RestartCount}}' \
  devtools-chaos-clinic-clinic-1

docker compose logs --tail 30 clinic
```

process จบด้วย exit code `17`; policy `on-failure:3` จึงเริ่มใหม่ และ `restart_count` ต้องมากกว่า 0

## Security scan ด้วยสายตา

```bash
docker inspect -f \
  'readonly={{.HostConfig.ReadonlyRootfs}} caps={{json .HostConfig.CapDrop}} security={{json .HostConfig.SecurityOpt}}' \
  devtools-chaos-clinic-clinic-1
```

ข้อจำกัดเหล่านี้ไม่แทนการ scan image แต่ช่วยลด blast radius ของ workload

### Optional: resource limits เมื่อรัน Docker บน host โดยตรง

ไฟล์ `compose.resources.yaml` เพิ่ม `128 MB` และ `0.5 CPU`:

```bash
docker compose -f compose.yaml -f compose.resources.yaml up -d
```

ไม่ใช้ override นี้ใน privileged Docker-in-Docker ของชั้นเรียน: host บางระบบส่ง cgroup v2 แบบ threaded ให้ nested daemon ทำให้สร้าง task พร้อม CPU/memory controller ไม่ได้ (`cannot enter cgroupv2 ... threaded mode`) นี่เป็นข้อจำกัดของ lab topology ไม่ใช่แอป

## Cleanup (บังคับ)

ใน SSH:

```bash
docker compose down -v --remove-orphans
exit
```

บน host:

```bash
docker rm -f devtools-chaos-clinic-host
docker ps -a --filter "name=^devtools-"
```
