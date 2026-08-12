# 002 LAB — Image Factory

สร้าง image จาก Dockerfile ที่มี healthcheck และรันเป็น non-root จากนั้นเปลี่ยนสี/สภาพแวดล้อมด้วย `ENV` ตอน runtime โดยไม่ build ใหม่

## เป้าหมาย

- อ่านลำดับ `FROM → WORKDIR → COPY → USER → HEALTHCHECK → CMD`
- เห็น build layer/cache และ tag image แบบมีเวอร์ชัน
- แยก build-time `ARG` ออกจาก runtime `ENV`
- ตรวจ health, label และ user ด้วย `inspect`/`exec`
- ฝึก workflow registry ด้วย placeholder โดยไม่บันทึก token ลงไฟล์

ใช้เวลาประมาณ 35 นาที · SSH `2223` · Web `18082`

## 0) เปิดเครื่อง LAB (ทำบน host)

```bash
docker rm -f devtools-image-factory 2>/dev/null
docker run -dit \
  --name devtools-image-factory \
  --privileged \
  -p 2223:22 \
  -p 18082:8080 \
  tuchsanai/devtools:2569_1

docker exec devtools-image-factory mkdir -p /workspace/lab
docker cp 002_LAB_Image_Factory/. \
  devtools-image-factory:/workspace/lab/

ssh root@localhost -p 2223
# password: passwd
```

ภายใน SSH:

```bash
cd /workspace/lab
```

## 1) อ่าน build recipe ก่อนลงมือ

```bash
sed -n '1,220p' app/Dockerfile
sed -n '1,120p' app/.dockerignore
```

สังเกตว่าแอปรันด้วย UID `10001` ไม่ใช่ root และ `.dockerignore` กันไฟล์ที่ไม่เกี่ยวออกจาก build context

## 2) Build, tag และพิสูจน์ cache

```bash
docker build \
  --build-arg APP_VERSION=1.0.0 \
  -t devtools/image-factory:1.0.0 \
  ./app

docker image ls devtools/image-factory
docker image inspect -f '{{json .Config.Labels}}' devtools/image-factory:1.0.0
```

build ซ้ำทันที:

```bash
docker build \
  --build-arg APP_VERSION=1.0.0 \
  -t devtools/image-factory:1.0.0 \
  ./app
```

รอบสองควรเห็นหลายขั้นเป็น `CACHED`

## 3) Configure at run

```bash
docker run -d \
  --name devtools-lab2-app \
  -p 8080:8080 \
  -e APP_THEME=ocean \
  -e APP_STAGE=staging \
  devtools/image-factory:1.0.0

curl -fsS http://localhost:8080/health
docker inspect -f '{{.State.Health.Status}}' devtools-lab2-app
docker exec devtools-lab2-app id
```

เปิด `http://localhost:18082` ต้องเห็น theme `ocean`, stage `staging` และสถานะ healthy

เปลี่ยน config โดยใช้ image เดิม:

```bash
docker rm -f devtools-lab2-app
docker run -d \
  --name devtools-lab2-app \
  -p 8080:8080 \
  -e APP_THEME=sunset \
  -e APP_STAGE=production \
  devtools/image-factory:1.0.0
```

refresh browser: สีและ stage เปลี่ยน แต่ image ID ยังเป็นชิ้นเดิม

## Challenge: tag และ push อย่างปลอดภัย

ส่วนนี้ทำเฉพาะเมื่อมี repository ของตนเอง ใช้ placeholder เท่านั้นในเอกสาร:

```bash
export REGISTRY_USER="<dockerhub-username>"
read -rsp "Docker Hub token: " REGISTRY_TOKEN; echo
printf '%s' "$REGISTRY_TOKEN" | docker login -u "$REGISTRY_USER" --password-stdin

docker tag devtools/image-factory:1.0.0 \
  "$REGISTRY_USER/image-factory:1.0.0"
docker push "$REGISTRY_USER/image-factory:1.0.0"

unset REGISTRY_TOKEN
```

ห้ามใส่ token ใน Dockerfile, README, command history ที่แชร์ หรือ commit Git

## Cleanup (บังคับ)

ใน SSH:

```bash
docker rm -f devtools-lab2-app
exit
```

บน host:

```bash
docker rm -f devtools-image-factory
docker ps -a --filter "name=^devtools-"
```
