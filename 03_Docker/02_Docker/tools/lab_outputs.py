# -*- coding: utf-8 -*-
"""Real captured command output used by the slides.

EVERY string in this file was copied verbatim out of a lab's
`evidence/transcript.md`, which in turn was captured from a live run on
`tuchsanai/devtools:2569_1`. Nothing here is written by hand or reconstructed.

Where a long line was shortened to fit a slide, the cut is marked with `…`
and the accompanying slide says so. Do not "tidy" these strings.
"""

MARKERS = {}

# ─────────────────────────────────────────────────────────── setup
MARKERS["SETUP_VER"] = """\
$ docker --version
Docker version 29.6.2, build dfc4efb

$ docker compose version
Docker Compose version v5.3.1"""

# ─────────────────────────────────────────────────── LAB 1 · control room
MARKERS["L1_PS"] = """\
$ docker ps
CONTAINER ID   IMAGE               COMMAND                  CREATED          STATUS          PORTS                                     NAMES
375dad3ca9b3   ubuntu:24.04        "sleep 600"              13 seconds ago   Up 13 seconds                                             box
ca4d825406e6   redis:7-alpine      "docker-entrypoint.s…"   20 seconds ago   Up 20 seconds   6379/tcp                                  cache
e24cad7406f7   nginx:1.29-alpine   "/docker-entrypoint.…"   34 seconds ago   Up 34 seconds   0.0.0.0:8080->80/tcp, [::]:8080->80/tcp   web

$ docker ps -a --format "table {{.Names}}\\t{{.Image}}\\t{{.Status}}\\t{{.Ports}}"
NAMES     IMAGE               STATUS                     PORTS
probe     alpine:3.21         Exited (0) 6 seconds ago
box       ubuntu:24.04        Up 19 seconds
cache     redis:7-alpine      Up 27 seconds              6379/tcp
web       nginx:1.29-alpine   Up 40 seconds              0.0.0.0:8080->80/tcp, [::]:8080->80/tcp"""

MARKERS["L1_LOGS"] = """\
$ docker logs web --tail 6
2026/08/12 12:32:31 [error] 34#34: *5 open() "/usr/share/nginx/html/missing.html" failed (2: No such file or directory), client: 172.18.0.1, server: localhost, request: "GET /missing.html HTTP/1.1", host: "localhost:8080"
172.18.0.1 - - [12/Aug/2026:12:32:31 +0000] "GET / HTTP/1.1" 200 6308 "-" "curl/8.5.0" "-"
172.18.0.1 - - [12/Aug/2026:12:32:31 +0000] "GET / HTTP/1.1" 200 6308 "-" "curl/8.5.0" "-"
172.18.0.1 - - [12/Aug/2026:12:32:31 +0000] "GET / HTTP/1.1" 200 6308 "-" "curl/8.5.0" "-"
172.18.0.1 - - [12/Aug/2026:12:32:31 +0000] "GET / HTTP/1.1" 200 6308 "-" "curl/8.5.0" "-"
172.18.0.1 - - [12/Aug/2026:12:32:31 +0000] "GET /missing.html HTTP/1.1" 404 153 "-" "curl/8.5.0" "-"

$ docker logs web 2>&1 | wc -l
53"""

MARKERS["L1_EXEC"] = """\
$ docker exec web nginx -v
nginx version: nginx/1.29.8

$ docker exec box cat /etc/hosts
127.0.0.1       localhost
::1     localhost ip6-localhost ip6-loopback
…
172.18.0.4      375dad3ca9b3

$ docker exec cache redis-cli PING
PONG

$ docker exec probe ls /
Error response from daemon: container f85ce59724c0…4d7bc3 is not running"""

MARKERS["L1_INSPECT"] = """\
$ docker inspect web | wc -l
250

$ docker inspect --format "{{.State.Status}}" web cache box probe
running
running
running
exited

$ docker inspect --format "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}" web cache box
172.18.0.2
172.18.0.3
172.18.0.4

$ docker inspect --format "{{json .Config.Cmd}}" web box
["nginx","-g","daemon off;"]
["sleep","600"]

$ docker inspect --format "{{range .Mounts}}{{.Source}} -> {{.Destination}} (RW={{.RW}}){{end}}" web
/workspace/lab/site -> /usr/share/nginx/html (RW=false)"""

MARKERS["L1_STATS"] = """\
$ docker ps --filter label=lab=control-room --format "{{.Names}}"
box
cache
web

$ docker ps -a --filter status=exited --format "table {{.Names}}\\t{{.Status}}"
NAMES     STATUS
probe     Exited (0) 7 seconds ago

$ docker top box
UID                 PID                 PPID                C                   STIME               TTY                 TIME                CMD
root                3973                3949                0                   19:31               ?                   00:00:00            sleep 600"""

MARKERS["L1_STOPSTART"] = """\
$ docker exec cache redis-cli SET fleet 3
OK
$ docker inspect --format "{{.Id}}" cache
ca4d825406e6be47ab1ce71a8f851a32b301d1552b877904d14a0a8e319c717a

$ docker stop cache
cache
$ docker ps -a --format "table {{.Names}}\\t{{.Status}}"
NAMES     STATUS
probe     Exited (0) About a minute ago
box       Up 2 minutes
cache     Exited (0) Less than a second ago
web       Up 2 minutes

$ docker start cache
cache
$ docker inspect --format "{{.Id}}" cache
ca4d825406e6be47ab1ce71a8f851a32b301d1552b877904d14a0a8e319c717a
$ docker exec cache redis-cli GET fleet
3"""

MARKERS["L1_IMAGES"] = """\
$ docker rmi nginx:1.29-alpine
Error response from daemon: conflict: unable to delete nginx:1.29-alpine (must be forced) - container e24cad7406f7 is using its referenced image 5616878291a2

$ docker ps -aq --filter label=lab=control-room
375dad3ca9b3
e24cad7406f7
$ docker rm -f $(docker ps -aq --filter label=lab=control-room)
375dad3ca9b3
e24cad7406f7
$ docker ps -a
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES"""

# ────────────────────────────────────────────────── LAB 2 · color factory
MARKERS["L2_PRECEDENCE"] = """\
$ docker run -d --name color-boss --env-file env/red.env -e APP_COLOR=pink -p 8085:8081 color-app:1.0
2a671c2a960b70abc785efd0a33efd5f81f617162d67312374e80e11d2859c43

$ docker exec color-boss env | grep APP_
APP_NAME=Red Factory
APP_COLOR=pink
APP_PORT=8081

$ docker inspect --format '{{json .Config.Env}}' color-boss
["APP_COLOR=red","APP_NAME=Red Factory","APP_COLOR=pink","PATH=…","LANG=C.UTF-8","GPG_KEY=…","PYTHON_VERSION=3.12.13","PYTHON_SHA256=…","APP_PORT=8081"]"""

MARKERS["L2_SECRET"] = """\
$ docker build -t leaky:1.0 secret-demo/
 - SecretsUsedInArgOrEnv: Do not use ARG or ENV instructions for sensitive data (ARG "DB_PASSWORD") (line 5)
 - SecretsUsedInArgOrEnv: Do not use ARG or ENV instructions for sensitive data (ENV "API_TOKEN") (line 6)

$ docker history --no-trunc --format "table {{.CreatedBy}}" leaky:1.0
CREATED BY
CMD ["sh" "-c" "echo leaky image"]
RUN |1 DB_PASSWORD=not-a-real-password-1234 /bin/sh -c echo "building with DB_PASSWORD=$DB_PASSWORD" > /build.log # buildkit
ENV API_TOKEN=not-a-real-token-abcd
ARG DB_PASSWORD=not-a-real-password-1234
CMD ["/bin/sh"]
ADD alpine-minirootfs-3.21.7-x86_64.tar.gz / # buildkit"""

MARKERS["L2_INSPECT_IMG"] = """\
$ docker image inspect --format '{{json .Config.Env}}' color-app:1.0
["PATH=…","LANG=C.UTF-8","GPG_KEY=…","PYTHON_VERSION=3.12.13","PYTHON_SHA256=…","APP_COLOR=blue","APP_NAME=Color Factory","APP_PORT=8081"]

$ docker image inspect --format '{{json .Config.Cmd}}' color-app:1.0
["python","app.py"]

$ docker image inspect --format '{{json .Config.ExposedPorts}}' color-app:1.0
{"8081/tcp":{}}

$ docker image inspect --format 'arch={{.Architecture}}  os={{.Os}}  size={{.Size}} bytes  workdir={{.Config.WorkingDir}}' color-app:1.0
arch=amd64  os=linux  size=48162906 bytes  workdir=/app"""

# ───────────────────────────────────────────────────── LAB 3 · image diet
MARKERS["L3_CTX"] = """\
$ docker build -f v2/Dockerfile -t ctx:off ~/ctx-off       # ไม่มี .dockerignore
#5 [internal] load build context
#5 transferring context: 47.21MB 0.1s done

$ docker build -f v2/Dockerfile -t ctx:on  ~/ctx-on        # มี .dockerignore
#5 [internal] load build context
#5 transferring context: 15.44kB done"""

MARKERS["L3_TABLE"] = """\
$ docker images
IMAGE              ID             DISK USAGE   CONTENT SIZE   EXTRA
diet-app:v1        e6bafffc232b       1.63GB          420MB
diet-app:v2        21a664610c84        210MB         51.9MB
diet-app:v3        52c0caeb7825        209MB         50.3MB
python:3.12        dd4fe98ab39f       1.62GB          429MB
python:3.12-slim   229a2c5bfa27        179MB         45.4MB

# rebuild หลังแก้ app.py หนึ่งบรรทัด — ดูว่าชั้น pip โดนอะไร
v1 :  #8 [4/4] RUN pip install flask gunicorn requests python-dotenv
      #8 DONE 2.7s                                     real  0m4.493s
v2 :  #8 [4/5] RUN pip install -r requirements.txt
      #8 CACHED                                        real  0m1.459s"""

MARKERS["L3_HISTORY"] = """\
$ docker image history diet-app:v3          # ตัดมา 9 ชั้นบนสุด (ของเราเอง) จากทั้งหมด 19 ชั้น
IMAGE          CREATED          CREATED BY                                      SIZE      COMMENT
76146f411612   7 seconds ago    CMD ["python" "app/app.py"]                     0B        buildkit.dockerfile.v0
<missing>      7 seconds ago    HEALTHCHECK {Test:[CMD-SHELL python -c "impo…   0B        buildkit.dockerfile.v0
<missing>      7 seconds ago    EXPOSE [8080/tcp]                               0B        buildkit.dockerfile.v0
<missing>      7 seconds ago    USER appuser                                    0B        buildkit.dockerfile.v0
<missing>      7 seconds ago    ENV PATH=/opt/venv/bin:/usr/local/bin:/usr/l…   0B        buildkit.dockerfile.v0
<missing>      7 seconds ago    COPY /build/app/ ./app/ # buildkit              53.2kB    buildkit.dockerfile.v0
<missing>      7 seconds ago    COPY /opt/venv /opt/venv # buildkit             24.8MB    buildkit.dockerfile.v0
<missing>      10 seconds ago   WORKDIR /app                                    8.19kB    buildkit.dockerfile.v0
<missing>      11 seconds ago   RUN /bin/sh -c useradd --create-home --uid 1…   69.6kB    buildkit.dockerfile.v0
<missing>      7 days ago       CMD ["python3"]                                 0B        buildkit.dockerfile.v0
<missing>      7 days ago       RUN /bin/sh -c set -eux;   savedAptMark="$(a…   41.4MB    buildkit.dockerfile.v0
<missing>      9 days ago       # debian.sh --arch 'amd64' out/ 'trixie' '@1…   87.4MB    debuerreotype 0.17"""

# ───────────────────────────────────────────────── LAB 4 · vision compose
MARKERS["L4_PS"] = """\
$ docker compose up -d --build
$ docker compose ps
NAME                IMAGE                 COMMAND                  SERVICE    CREATED          STATUS                    PORTS
vision-backend-1    vision-backend:1.0    "uvicorn main:app --…"   backend    13 seconds ago   Up 12 seconds (healthy)   0.0.0.0:8000->8000/tcp
vision-frontend-1   vision-frontend:1.0   "python app.py"          frontend   13 seconds ago   Up 7 seconds              0.0.0.0:8501->8501/tcp

$ docker compose logs backend --tail 4
backend-1  | INFO:     Application startup complete.
backend-1  | INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
backend-1  | INFO:     127.0.0.1:59174 - "GET /healthz HTTP/1.1" 200 OK"""

MARKERS["L4_DNS"] = """\
$ docker compose exec frontend python -c "import socket;print(socket.gethostbyname('backend'))"
172.19.0.2

$ docker compose exec backend python -c "import cv2;print(cv2.__version__)"
4.10.0

$ docker network ls --filter name=vision
NETWORK ID     NAME               DRIVER    SCOPE
71b76dbe7854   vision_visionnet   bridge    local

# ลองแบบผิด — container ที่อยู่บน default bridge เรียกชื่อ backend ไม่เจอ
$ docker exec frontend-bad python -c "import socket;print(socket.gethostbyname('backend'))"
socket.gaierror: [Errno -2] Name or service not known"""

# ────────────────────────────────────────────────────── LAB 5 · ops clinic
MARKERS["L5_RESTART"] = """\
$ docker run -d --name patient-a2 --restart on-failure:3 alpine:3.21 \\
      sh -c 'echo "boot: reading /etc/app.conf"; sleep 2; echo "FATAL: config not found" >&2; exit 1'
c3893a0743c9bd69949e03b98b452d41581f5d90dd310297f86ea244720cde7e

$ for i in 0 1 2 3 4 5 6 7; do printf 't=%2ss  RestartCount=%s  Status=%s\\n' $((i*2)) \\
      "$(docker inspect --format '{{.RestartCount}}' patient-a2)" … ; sleep 2; done
t= 0s  RestartCount=0  Status=running
t= 2s  RestartCount=1  Status=running
t= 4s  RestartCount=2  Status=running
t= 6s  RestartCount=3  Status=restarting
t= 8s  RestartCount=3  Status=running
t=10s  RestartCount=3  Status=exited
t=12s  RestartCount=3  Status=exited"""

MARKERS["L5_OOM"] = """\
$ docker stats --no-stream --format "table {{.Name}}\\t{{.MemUsage}}\\t{{.MemPerc}}\\t{{.CPUPerc}}"
NAME        MEM USAGE / LIMIT   MEM %     CPU %
patient-d   21.59MiB / 64MiB    33.73%    0.01%

$ curl -s -X POST "http://localhost:8083/leak?mb=2&delay=1"
{"chunk_mb":2,"delay_sec":1.0,"leaking":true,"limit_mb":64,"ok":true,"rss_mb":34.5}

$ … เฝ้าดูแรมไต่ขึ้นทุก 2 วินาที จนกว่าจะตาย
35.95MiB / 64MiB  56.17%     Up 12 seconds (healthy)
47.74MiB / 64MiB  74.59%     Up 18 seconds (healthy)
59.75MiB / 64MiB  93.36%     Up 24 seconds (healthy)
0B / 0B  0.00%               Exited (137) 1 second ago

$ docker inspect --format 'status={{.State.Status}}  exitCode={{.State.ExitCode}}  OOMKilled={{.State.OOMKilled}}  error="{{.State.Error}}"' patient-d
status=exited  exitCode=137  OOMKilled=true  error="\""""

MARKERS["L1_TAG"] = """\
$ docker run --rm redis:7-alpine redis-server --version
Redis server v=7.4.10 sha=00000000:0 malloc=jemalloc-5.3.0 bits=64 build=d70b7db78d693e15

$ docker run --rm redis redis-server --version        # ไม่ระบุ tag = Docker เติม :latest ให้
Starting Redis Server
Redis server v=8.10.0 sha=00000000:1 malloc=jemalloc-5.3.0 bits=64 build=1e8a7369582ecb6d"""
