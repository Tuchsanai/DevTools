# 003 LAB — Volume Time Machine

ทำลาย container แล้วสร้างใหม่ แต่ตัวนับยังอยู่ครบ เพื่อพิสูจน์ว่า state ที่สำคัญต้องอยู่นอก writable layer ของ container

## เป้าหมาย

- แยก writable layer, bind mount, named volume และ tmpfs
- สร้าง/inspect named volume ด้วย `--mount`
- พิสูจน์ persistence ด้วย container ID คนละตัว
- ตัดสินใจได้ว่าเมื่อไรควรใช้ bind mount หรือ volume

ใช้เวลาประมาณ 30 นาที · SSH `2224` · Web `18083`

## 0) เปิดเครื่อง LAB (ทำบน host)

```bash
docker rm -f devtools-volume-time-machine 2>/dev/null
docker run -dit \
  --name devtools-volume-time-machine \
  --privileged \
  -p 2224:22 \
  -p 18083:8080 \
  tuchsanai/devtools:2569_1

docker exec devtools-volume-time-machine mkdir -p /workspace/lab
docker cp 003_LAB_Volume_Time_Machine/. \
  devtools-volume-time-machine:/workspace/lab/

ssh root@localhost -p 2224
# password: passwd
```

ภายใน SSH:

```bash
cd /workspace/lab
docker build -t devtools/volume-time-machine:1.0 ./app
docker volume create devtools-lab3-data
```

## 1) สร้าง generation แรก

```bash
docker run -d \
  --name devtools-lab3-time-1 \
  -p 8080:8080 \
  --mount type=volume,source=devtools-lab3-data,target=/data \
  devtools/volume-time-machine:1.0

curl -fsS http://localhost:8080/hit >/dev/null
curl -fsS http://localhost:8080/hit >/dev/null
curl -fsS http://localhost:8080/hit >/dev/null
docker exec devtools-lab3-time-1 cat /data/state.json
docker inspect -f '{{.Id}}' devtools-lab3-time-1
```

เปิด `http://localhost:18083` ต้องเห็น counter เป็น `3`

## 2) ทำลาย container แล้วเดินทางข้ามเวลา

```bash
docker rm -f devtools-lab3-time-1

docker run -d \
  --name devtools-lab3-time-2 \
  -p 8080:8080 \
  --mount type=volume,source=devtools-lab3-data,target=/data \
  devtools/volume-time-machine:1.0

docker inspect -f '{{.Id}}' devtools-lab3-time-2
docker exec devtools-lab3-time-2 cat /data/state.json
```

refresh browser: counter ยังเป็น `3` แม้ container ID เปลี่ยนแล้ว

## 3) Inspect ที่เก็บความทรงจำ

```bash
docker volume inspect devtools-lab3-data
docker inspect -f '{{json .Mounts}}' devtools-lab3-time-2
```

เลือก storage ให้ถูกงาน:

| ชนิด | อายุข้อมูล | ใช้เมื่อ |
|---|---|---|
| writable layer | เท่า container | output ชั่วคราวที่ทิ้งได้ |
| bind mount | ผูกกับ path บน host | แก้ source/config จาก host |
| named volume | แยกจาก container, Docker ดูแล | database/state ที่ต้องอยู่ต่อ |
| tmpfs | อยู่ใน RAM | secret/cache ชั่วคราว ไม่เขียน disk |

## Cleanup (บังคับ)

ใน SSH:

```bash
docker rm -f devtools-lab3-time-2
docker volume rm devtools-lab3-data
exit
```

บน host:

```bash
docker rm -f devtools-volume-time-machine
docker ps -a --filter "name=^devtools-"
```
