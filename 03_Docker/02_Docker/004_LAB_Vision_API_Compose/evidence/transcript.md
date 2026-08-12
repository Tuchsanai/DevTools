# evidence — LAB 4 (004_LAB_Vision_API_Compose)

ทุกบล็อกด้านล่างคือคำสั่งจริงที่รันในเครื่องเรียน `tuchsanai/devtools:2569_1`
(outer container `devtools-lab004`, ports 2225:22 · 18041:8501 · 18042:8000)
และ output จริงที่ได้กลับมา — README.md ยกมาจากไฟล์นี้เท่านั้น

### $ docker --version; docker compose version

```bash
docker --version; docker compose version
```

```
Docker version 29.6.2, build dfc4efb
Docker Compose version v5.3.1
```

_exit code: 0_

### $ ls -R . | head -30

```bash
ls -R . | head -30
```

```
.:
backend
compose.yaml
env.example
frontend

./backend:
Dockerfile
main.py
requirements.txt

./frontend:
Dockerfile
app.py
requirements.txt
static

./frontend/static:
make_sample.py
sample.jpg
```

_exit code: 0_

### $ docker network create visionnet

```bash
docker network create visionnet
```

```
16205aa6d65436eda4783850c0a9757a50bc3901b366afdeac53b97d0bc56d3e
```

_exit code: 0_
