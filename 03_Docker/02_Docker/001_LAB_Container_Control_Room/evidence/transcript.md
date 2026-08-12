# Evidence transcript — LAB 1 (001_LAB_Container_Control_Room)

รันจริงในเครื่องเรียน `tuchsanai/devtools:2569_1` (outer container `devtools-lab001`, SSH 2222, web 18081)
ทุกบล็อกด้านล่างคือคำสั่งจริง + ผลลัพธ์จริงที่ capture มาโดยไม่แก้ไข

---

```bash
docker --version; docker compose version
```

```
Docker version 29.6.2, build dfc4efb
Docker Compose version v5.3.1
```

exit code: 0

```bash
docker run -d --name web --label lab=control-room -p 8080:80 -v /workspace/lab/site:/usr/share/nginx/html:ro nginx:1.29-alpine
```

```
Unable to find image 'nginx:1.29-alpine' locally
1.29-alpine: Pulling from library/nginx
612c0c1df4c5: Pulling fs layer
453da7dbc73e: Pulling fs layer
781ff50d2644: Pulling fs layer
82736a35d0e7: Pulling fs layer
aee4e54b3865: Pulling fs layer
4a8b0b2a5b19: Pulling fs layer
6a0ac1617861: Pulling fs layer
583599bb7d38: Pulling fs layer
4a8b0b2a5b19: Download complete
aee4e54b3865: Download complete
781ff50d2644: Download complete
583599bb7d38: Download complete
453da7dbc73e: Download complete
82736a35d0e7: Download complete
6a0ac1617861: Download complete
612c0c1df4c5: Download complete
6a0ac1617861: Pull complete
aee4e54b3865: Pull complete
781ff50d2644: Pull complete
583599bb7d38: Pull complete
82736a35d0e7: Pull complete
e8fc446e336c: Download complete
4a8b0b2a5b19: Pull complete
453da7dbc73e: Pull complete
6192e1e6a438: Download complete
612c0c1df4c5: Pull complete
Digest: sha256:5616878291a2eed594aee8db4dade5878cf7edcb475e59193904b198d9b830de
Status: Downloaded newer image for nginx:1.29-alpine
f34277c1bd51cd7b777897685e08a9ad4e61cd431190969d56a2c0cfd5f80127
```

exit code: 0

```bash
docker run -d --name cache --label lab=control-room redis:7-alpine
```

```
Unable to find image 'redis:7-alpine' locally
7-alpine: Pulling from library/redis
db197c512a33: Pulling fs layer
4f4fb700ef54: Pulling fs layer
f5a655897537: Pulling fs layer
93ebed1aef27: Pulling fs layer
63e63047b377: Pulling fs layer
897d797d2723: Pulling fs layer
627d9d06d3d0: Pulling fs layer
63e63047b377: Download complete
93ebed1aef27: Download complete
4f4fb700ef54: Download complete
f5a655897537: Download complete
db197c512a33: Download complete
897d797d2723: Download complete
627d9d06d3d0: Download complete
897d797d2723: Pull complete
63e63047b377: Pull complete
f5a655897537: Pull complete
22b5e73fc01c: Download complete
cac39341ecaa: Download complete
93ebed1aef27: Pull complete
627d9d06d3d0: Pull complete
4f4fb700ef54: Pull complete
db197c512a33: Pull complete
Digest: sha256:e7723ff73d963f5cc6d9c4643ea3d989527a402a319239054e9472a7fb9219a2
Status: Downloaded newer image for redis:7-alpine
679de539d53eadf56769edd89d63d51e6090ef5f59cd4590c427cb8b329647e1
```

exit code: 0

```bash
docker run -d --name box --label lab=control-room ubuntu:24.04 sleep 600
```

```
Unable to find image 'ubuntu:24.04' locally
24.04: Pulling from library/ubuntu
966c395d29cb: Pulling fs layer
966c395d29cb: Download complete
4029a2d69959: Download complete
966c395d29cb: Pull complete
Digest: sha256:561618e2c15bf2397621dd04f96926663a3b5616c189cf7e38db7e82f5c538ea
Status: Downloaded newer image for ubuntu:24.04
7cdac95d8437c46cb6827af9aa44da7fdf0640b2afbe736eed97eb81e68ca81a
```

exit code: 0

```bash
docker ps
```

```
CONTAINER ID   IMAGE               COMMAND                  CREATED          STATUS          PORTS                                     NAMES
7cdac95d8437   ubuntu:24.04        "sleep 600"              4 seconds ago    Up 4 seconds                                              box
679de539d53e   redis:7-alpine      "docker-entrypoint.s…"   12 seconds ago   Up 11 seconds   6379/tcp                                  cache
f34277c1bd51   nginx:1.29-alpine   "/docker-entrypoint.…"   23 seconds ago   Up 22 seconds   0.0.0.0:8080->80/tcp, [::]:8080->80/tcp   web
```

exit code: 0

```bash
docker ps -a
```

```
CONTAINER ID   IMAGE               COMMAND                  CREATED          STATUS          PORTS                                     NAMES
7cdac95d8437   ubuntu:24.04        "sleep 600"              4 seconds ago    Up 4 seconds                                              box
679de539d53e   redis:7-alpine      "docker-entrypoint.s…"   12 seconds ago   Up 11 seconds   6379/tcp                                  cache
f34277c1bd51   nginx:1.29-alpine   "/docker-entrypoint.…"   23 seconds ago   Up 22 seconds   0.0.0.0:8080->80/tcp, [::]:8080->80/tcp   web
```

exit code: 0

```bash
docker run --name probe --label lab=control-room alpine:3.21 echo "probe ok"
```

```
Unable to find image 'alpine:3.21' locally
3.21: Pulling from library/alpine
6bda28f35b00: Download complete
2be669017abd: Download complete
Digest: sha256:48b0309ca019d89d40f670aa1bc06e426dc0931948452e8491e3d65087abc07d
Status: Downloaded newer image for alpine:3.21
probe ok
```

exit code: 0

```bash
docker ps
```

```
CONTAINER ID   IMAGE               COMMAND                  CREATED          STATUS          PORTS                                     NAMES
7cdac95d8437   ubuntu:24.04        "sleep 600"              27 seconds ago   Up 26 seconds                                             box
679de539d53e   redis:7-alpine      "docker-entrypoint.s…"   35 seconds ago   Up 33 seconds   6379/tcp                                  cache
f34277c1bd51   nginx:1.29-alpine   "/docker-entrypoint.…"   46 seconds ago   Up 45 seconds   0.0.0.0:8080->80/tcp, [::]:8080->80/tcp   web
```

exit code: 0

```bash
docker ps -a
```

```
CONTAINER ID   IMAGE               COMMAND                  CREATED          STATUS                              PORTS                                     NAMES
a30113891b20   alpine:3.21         "echo 'probe ok'"        1 second ago     Exited (0) Less than a second ago                                             probe
7cdac95d8437   ubuntu:24.04        "sleep 600"              27 seconds ago   Up 26 seconds                                                                 box
679de539d53e   redis:7-alpine      "docker-entrypoint.s…"   35 seconds ago   Up 34 seconds                       6379/tcp                                  cache
f34277c1bd51   nginx:1.29-alpine   "/docker-entrypoint.…"   46 seconds ago   Up 45 seconds                       0.0.0.0:8080->80/tcp, [::]:8080->80/tcp   web
```

exit code: 0

```bash
docker ps -a --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'
```

```
NAMES     IMAGE               STATUS                     PORTS
probe     alpine:3.21         Exited (0) 4 seconds ago   
box       ubuntu:24.04        Up 30 seconds              
cache     redis:7-alpine      Up 38 seconds              6379/tcp
web       nginx:1.29-alpine   Up 49 seconds              0.0.0.0:8080->80/tcp, [::]:8080->80/tcp
```

exit code: 0

```bash
docker ps --filter label=lab=control-room --format '{{.Names}}'
```

```
box
cache
web
```

exit code: 0

```bash
docker ps -a --filter status=exited --format 'table {{.Names}}\t{{.Status}}'
```

```
NAMES     STATUS
probe     Exited (0) 4 seconds ago
```

exit code: 0

```bash
docker run --rm alpine:3.21 echo "hello from a container"
```

```
hello from a container
```

exit code: 0

```bash
docker ps -a --filter name=alpine --format "{{.Names}}" ; echo "(--rm ทำให้ไม่มีอะไรค้าง)"
```

```
(--rm ทำให้ไม่มีอะไรค้าง)
```

exit code: 0

```bash
docker ps -a --format "table {{.Names}}\t{{.Image}}\t{{.Status}}"
```

```
NAMES     IMAGE               STATUS
probe     alpine:3.21         Exited (0) 55 seconds ago
box       ubuntu:24.04        Up About a minute
cache     redis:7-alpine      Up About a minute
web       nginx:1.29-alpine   Up About a minute
```

exit code: 0

```bash
printf 'whoami\ncat /etc/os-release | head -2\nexit\n' | script -qec 'docker run -it --rm ubuntu:24.04 sh' /dev/null
```

```
whoami
cat /etc/os-release | head -2
exit
whoami
cat /etc/os-release | head -2
exit
# root
# PRETTY_NAME="Ubuntu 24.04.4 LTS"
NAME="Ubuntu"
# 
```

exit code: 0

```bash
docker run -it --rm ubuntu:24.04 sh
```

(interactive session — พิมพ์ `whoami`, `cat /etc/os-release | head -2`, `exit`; capture ผ่าน pty จริง)

```
# whoami
root
# cat /etc/os-release | head -2
PRETTY_NAME="Ubuntu 24.04.4 LTS"
NAME="Ubuntu"
# exit
```

