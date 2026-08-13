# Evidence transcript — LAB 1 · `001_LAB_Container_Control_Room`

รันจริงในเครื่องเรียน image `tuchsanai/devtools:2569_1`
outer container `devtools-lab001` · SSH `2222:22` · web `18081:8080`
ทุกบล็อกคือ **คำสั่งจริง + ผลลัพธ์จริง** ที่ capture มาโดยไม่แก้ไข (ยกเว้นที่ระบุว่าตัด ANSI escape ออก)
ก่อนเริ่มรอบนี้ ล้าง container และ image ทั้งหมด **ภายในเครื่องเรียน** เพื่อให้เห็น output ของการ pull ครั้งแรกจริง ๆ

---

## 0. เตรียมเครื่องเรียน

```bash
docker --version; docker compose version
```

```
Docker version 29.6.2, build dfc4efb
Docker Compose version v5.3.1
```

exit code: 0

## 1. เปิดกองเรือ 3 ลำ
```bash
docker run -d --name web --label lab=control-room -p 8080:80 -v /workspace/lab/site:/usr/share/nginx/html:ro nginx:1.29-alpine
```

```
Unable to find image 'nginx:1.29-alpine' locally
1.29-alpine: Pulling from library/nginx
612c0c1df4c5: Pulling fs layer
6a0ac1617861: Pulling fs layer
aee4e54b3865: Pulling fs layer
453da7dbc73e: Pulling fs layer
781ff50d2644: Pulling fs layer
583599bb7d38: Pulling fs layer
4a8b0b2a5b19: Pulling fs layer
82736a35d0e7: Pulling fs layer
6a0ac1617861: Download complete
4a8b0b2a5b19: Download complete
453da7dbc73e: Download complete
781ff50d2644: Download complete
82736a35d0e7: Download complete
aee4e54b3865: Download complete
583599bb7d38: Download complete
612c0c1df4c5: Download complete
6a0ac1617861: Pull complete
781ff50d2644: Pull complete
82736a35d0e7: Pull complete
aee4e54b3865: Pull complete
583599bb7d38: Pull complete
4a8b0b2a5b19: Pull complete
453da7dbc73e: Pull complete
e8fc446e336c: Download complete
6192e1e6a438: Download complete
612c0c1df4c5: Pull complete
Digest: sha256:5616878291a2eed594aee8db4dade5878cf7edcb475e59193904b198d9b830de
Status: Downloaded newer image for nginx:1.29-alpine
e24cad7406f77e2ffa5c68f3ed48eb31a33e19a10dfd57260bcc73e195a6d4d4
```

exit code: 0

```bash
docker run -d --name cache --label lab=control-room redis:7-alpine 2>&1 | tail -4
```

```
cac39341ecaa: Download complete
Digest: sha256:e7723ff73d963f5cc6d9c4643ea3d989527a402a319239054e9472a7fb9219a2
Status: Downloaded newer image for redis:7-alpine
ca4d825406e6be47ab1ce71a8f851a32b301d1552b877904d14a0a8e319c717a
```

exit code: 0

```bash
docker run -d --name box --label lab=control-room ubuntu:24.04 sleep 600 2>&1 | tail -4
```

```
966c395d29cb: Pull complete
Digest: sha256:561618e2c15bf2397621dd04f96926663a3b5616c189cf7e38db7e82f5c538ea
Status: Downloaded newer image for ubuntu:24.04
375dad3ca9b397e806451778454241a5c0641a9ee4c0f20fe13fad2a755ee739
```

exit code: 0

```bash
docker ps
```

```
CONTAINER ID   IMAGE               COMMAND                  CREATED                  STATUS                  PORTS                                     NAMES
375dad3ca9b3   ubuntu:24.04        "sleep 600"              Less than a second ago   Up Less than a second                                             box
ca4d825406e6   redis:7-alpine      "docker-entrypoint.s…"   7 seconds ago            Up 7 seconds            6379/tcp                                  cache
e24cad7406f7   nginx:1.29-alpine   "/docker-entrypoint.…"   21 seconds ago           Up 21 seconds           0.0.0.0:8080->80/tcp, [::]:8080->80/tcp   web
```

exit code: 0

## 2. ps vs ps -a · --format · --filter
```bash
docker ps -a
```

```
CONTAINER ID   IMAGE               COMMAND                  CREATED          STATUS          PORTS                                     NAMES
375dad3ca9b3   ubuntu:24.04        "sleep 600"              6 seconds ago    Up 5 seconds                                              box
ca4d825406e6   redis:7-alpine      "docker-entrypoint.s…"   13 seconds ago   Up 13 seconds   6379/tcp                                  cache
e24cad7406f7   nginx:1.29-alpine   "/docker-entrypoint.…"   27 seconds ago   Up 27 seconds   0.0.0.0:8080->80/tcp, [::]:8080->80/tcp   web
```

exit code: 0

```bash
docker run --name probe --label lab=control-room alpine:3.21 echo "probe ok" 2>&1 | tail -3
```

```
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
375dad3ca9b3   ubuntu:24.04        "sleep 600"              13 seconds ago   Up 13 seconds                                             box
ca4d825406e6   redis:7-alpine      "docker-entrypoint.s…"   20 seconds ago   Up 20 seconds   6379/tcp                                  cache
e24cad7406f7   nginx:1.29-alpine   "/docker-entrypoint.…"   34 seconds ago   Up 34 seconds   0.0.0.0:8080->80/tcp, [::]:8080->80/tcp   web
```

exit code: 0

```bash
docker ps -a
```

```
CONTAINER ID   IMAGE               COMMAND                  CREATED          STATUS                              PORTS                                     NAMES
f85ce59724c0   alpine:3.21         "echo 'probe ok'"        1 second ago     Exited (0) Less than a second ago                                             probe
375dad3ca9b3   ubuntu:24.04        "sleep 600"              14 seconds ago   Up 13 seconds                                                                 box
ca4d825406e6   redis:7-alpine      "docker-entrypoint.s…"   21 seconds ago   Up 20 seconds                       6379/tcp                                  cache
e24cad7406f7   nginx:1.29-alpine   "/docker-entrypoint.…"   35 seconds ago   Up 34 seconds                       0.0.0.0:8080->80/tcp, [::]:8080->80/tcp   web
```

exit code: 0

```bash
docker ps -a --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"
```

```
NAMES     IMAGE               STATUS                     PORTS
probe     alpine:3.21         Exited (0) 6 seconds ago   
box       ubuntu:24.04        Up 19 seconds              
cache     redis:7-alpine      Up 27 seconds              6379/tcp
web       nginx:1.29-alpine   Up 40 seconds              0.0.0.0:8080->80/tcp, [::]:8080->80/tcp
```

exit code: 0

```bash
docker ps --filter label=lab=control-room --format "{{.Names}}"
```

```
box
cache
web
```

exit code: 0

```bash
docker ps -a --filter status=exited --format "table {{.Names}}\t{{.Status}}"
```

```
NAMES     STATUS
probe     Exited (0) 7 seconds ago
```

exit code: 0

## 3. สามโหมดของ docker run
```bash
docker run --rm alpine:3.21 echo "hello from a container"
```

```
hello from a container
```

exit code: 0

```bash
docker ps -a --format "table {{.Names}}\t{{.Image}}\t{{.Status}}"
```

```
NAMES     IMAGE               STATUS
probe     alpine:3.21         Exited (0) 16 seconds ago
box       ubuntu:24.04        Up 29 seconds
cache     redis:7-alpine      Up 36 seconds
web       nginx:1.29-alpine   Up 50 seconds
```

exit code: 0

```bash
docker run -it --rm ubuntu:24.04 sh
```

(interactive session จริงผ่าน pty — พิมพ์ `whoami`, `cat /etc/os-release | head -2`, `exit`; ตัด ANSI escape ออก)

```
# whoami
root
# cat /etc/os-release | head -2
PRETTY_NAME="Ubuntu 24.04.4 LTS"
NAME="Ubuntu"
# exit
```

```bash
timeout 4 docker run --name fg-web --label lab=control-room nginx:1.29-alpine 2>&1 | head -12 ; echo "[... log ยังไหลต่อไปเรื่อย ๆ terminal ไม่คืน prompt จนกว่าจะกด Ctrl+C ...]"
```

```
/docker-entrypoint.sh: /docker-entrypoint.d/ is not empty, will attempt to perform configuration
/docker-entrypoint.sh: Looking for shell scripts in /docker-entrypoint.d/
/docker-entrypoint.sh: Launching /docker-entrypoint.d/10-listen-on-ipv6-by-default.sh
10-listen-on-ipv6-by-default.sh: info: Getting the checksum of /etc/nginx/conf.d/default.conf
10-listen-on-ipv6-by-default.sh: info: Enabled listen on IPv6 in /etc/nginx/conf.d/default.conf
/docker-entrypoint.sh: Sourcing /docker-entrypoint.d/15-local-resolvers.envsh
/docker-entrypoint.sh: Launching /docker-entrypoint.d/20-envsubst-on-templates.sh
/docker-entrypoint.sh: Launching /docker-entrypoint.d/30-tune-worker-processes.sh
/docker-entrypoint.sh: Configuration complete; ready for start up
2026/08/12 12:32:05 [notice] 1#1: using the "epoll" event method
2026/08/12 12:32:05 [notice] 1#1: nginx/1.29.8
2026/08/12 12:32:05 [notice] 1#1: built by gcc 15.2.0 (Alpine 15.2.0) 
[... log ยังไหลต่อไปเรื่อย ๆ terminal ไม่คืน prompt จนกว่าจะกด Ctrl+C ...]
```

exit code: 0

```bash
docker rm -f fg-web
```

```
fg-web
```

exit code: 0

```bash
docker run -d --name detached-demo --label lab=control-room nginx:1.29-alpine
```

```
908989a16b8ef767668667086d1894543e7c1c6f6f02e3ae985ed5e144a4eb5b
```

exit code: 0

```bash
docker ps --filter name=detached-demo --format "table {{.Names}}\t{{.Image}}\t{{.Status}}"
```

```
NAMES           IMAGE               STATUS
detached-demo   nginx:1.29-alpine   Up Less than a second
```

exit code: 0

```bash
docker rm -f detached-demo
```

```
detached-demo
```

exit code: 0

## 4. tag — latest ไม่ได้แปลว่าใหม่สุด
```bash
docker pull redis 2>&1 | tail -5
```

```
65405b53eed3: Pull complete
514dfa5816db: Pull complete
Digest: sha256:344e3945a0b431c8ff1eecd58c5573538126bd756f02fc7e218ddf1fc2546366
Status: Downloaded newer image for redis:latest
docker.io/library/redis:latest
```

exit code: 0

```bash
docker images
```

```
IMAGE               ID             DISK USAGE   CONTENT SIZE   EXTRA
alpine:3.21         48b0309ca019       12.2MB         3.73MB   U    
nginx:1.29-alpine   5616878291a2       93.5MB         26.9MB   U    
redis:7-alpine      e7723ff73d96       57.8MB         16.8MB   U    
redis:latest        344e3945a0b4        212MB         57.4MB        
ubuntu:24.04        561618e2c15b        119MB         31.7MB   U    
```

exit code: 0

```bash
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.Size}}"
```

```
REPOSITORY   TAG           IMAGE ID       SIZE
redis        latest        344e3945a0b4   212MB
ubuntu       24.04         561618e2c15b   119MB
redis        7-alpine      e7723ff73d96   57.8MB
alpine       3.21          48b0309ca019   12.2MB
nginx        1.29-alpine   5616878291a2   93.5MB
```

exit code: 0

```bash
docker run --rm redis:7-alpine redis-server --version
```

```
Redis server v=7.4.10 sha=00000000:0 malloc=jemalloc-5.3.0 bits=64 build=d70b7db78d693e15
```

exit code: 0

```bash
docker run --rm redis redis-server --version
```

```
Starting Redis Server
Redis server v=8.10.0 sha=00000000:1 malloc=jemalloc-5.3.0 bits=64 build=1e8a7369582ecb6d
```

exit code: 0

## 5. docker logs
```bash
curl -s -o /dev/null -w "HTTP %{http_code}  %{size_download} bytes\n" http://localhost:8080/
```

```
HTTP 200  6308 bytes
```

exit code: 0

```bash
for i in 1 2 3; do curl -s -o /dev/null http://localhost:8080/; done; curl -s -o /dev/null http://localhost:8080/missing.html; echo "ยิงไป 5 request (สำเร็จ 4 + พัง 1)"
```

```
ยิงไป 5 request (สำเร็จ 4 + พัง 1)
```

exit code: 0

```bash
docker logs web --tail 6
```

```
2026/08/12 12:32:31 [error] 34#34: *5 open() "/usr/share/nginx/html/missing.html" failed (2: No such file or directory), client: 172.18.0.1, server: localhost, request: "GET /missing.html HTTP/1.1", host: "localhost:8080"
172.18.0.1 - - [12/Aug/2026:12:32:31 +0000] "GET / HTTP/1.1" 200 6308 "-" "curl/8.5.0" "-"
172.18.0.1 - - [12/Aug/2026:12:32:31 +0000] "GET / HTTP/1.1" 200 6308 "-" "curl/8.5.0" "-"
172.18.0.1 - - [12/Aug/2026:12:32:31 +0000] "GET / HTTP/1.1" 200 6308 "-" "curl/8.5.0" "-"
172.18.0.1 - - [12/Aug/2026:12:32:31 +0000] "GET / HTTP/1.1" 200 6308 "-" "curl/8.5.0" "-"
172.18.0.1 - - [12/Aug/2026:12:32:31 +0000] "GET /missing.html HTTP/1.1" 404 153 "-" "curl/8.5.0" "-"
```

exit code: 0

```bash
docker logs web 2>&1 | wc -l
```

```
53
```

exit code: 0

```bash
docker logs -t web --tail 2
```

```
2026-08-12T12:32:31.384380097Z 172.18.0.1 - - [12/Aug/2026:12:32:31 +0000] "GET /missing.html HTTP/1.1" 404 153 "-" "curl/8.5.0" "-"
2026-08-12T12:32:31.384465822Z 2026/08/12 12:32:31 [error] 34#34: *5 open() "/usr/share/nginx/html/missing.html" failed (2: No such file or directory), client: 172.18.0.1, server: localhost, request: "GET /missing.html HTTP/1.1", host: "localhost:8080"
```

exit code: 0

```bash
timeout 6 docker logs -f web --tail 1 & sleep 1; curl -s -o /dev/null http://localhost:8080/; curl -s -o /dev/null http://localhost:8080/; sleep 3; echo "[บรรทัดใหม่โผล่มาเองแบบ real time — กด Ctrl+C เพื่อหยุด]"
```

```
2026/08/12 12:32:31 [error] 34#34: *5 open() "/usr/share/nginx/html/missing.html" failed (2: No such file or directory), client: 172.18.0.1, server: localhost, request: "GET /missing.html HTTP/1.1", host: "localhost:8080"
172.18.0.1 - - [12/Aug/2026:12:32:40 +0000] "GET / HTTP/1.1" 200 6308 "-" "curl/8.5.0" "-"
172.18.0.1 - - [12/Aug/2026:12:32:40 +0000] "GET / HTTP/1.1" 200 6308 "-" "curl/8.5.0" "-"
[บรรทัดใหม่โผล่มาเองแบบ real time — กด Ctrl+C เพื่อหยุด]
```

exit code: 0

```bash
docker logs web --tail 2
```

```
172.18.0.1 - - [12/Aug/2026:12:32:40 +0000] "GET / HTTP/1.1" 200 6308 "-" "curl/8.5.0" "-"
172.17.0.1 - - [12/Aug/2026:12:32:51 +0000] "GET / HTTP/1.1" 200 6308 "-" "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/151.0.7922.34 Safari/537.36" "-"
```

exit code: 0

## 6. docker exec
```bash
docker exec web nginx -v
```

```
nginx version: nginx/1.29.8
```

exit code: 0

```bash
docker exec box cat /etc/hosts
```

```
127.0.0.1	localhost
::1	localhost ip6-localhost ip6-loopback
fe00::	ip6-localnet
ff00::	ip6-mcastprefix
ff02::1	ip6-allnodes
ff02::2	ip6-allrouters
172.18.0.4	375dad3ca9b3
```

exit code: 0

```bash
docker exec cache redis-cli PING; docker exec cache redis-cli SET fleet 3; docker exec cache redis-cli GET fleet
```

```
PONG
OK
3
```

exit code: 0

```bash
docker exec probe ls /
```

```
Error response from daemon: container f85ce59724c0812f068b1199ab77fe36dccc789d0cf66fa5f5fcc064974d7bc3 is not running
```

exit code: 1

```bash
docker exec -it web sh
```

(interactive session จริงผ่าน pty — พิมพ์ `hostname`, `ls /usr/share/nginx/html`, `exit`; ตัด ANSI escape ออก)

```
/ # hostname
e24cad7406f7
/ # ls /usr/share/nginx/html
index.html
/ # exit
```

## 7. docker inspect
```bash
docker inspect web | wc -l
```

```
250
```

exit code: 0

```bash
docker inspect --format "{{.State.Status}}" web cache box probe
```

```
running
running
running
exited
```

exit code: 0

```bash
docker inspect --format "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}" web cache box
```

```
172.18.0.2
172.18.0.3
172.18.0.4
```

exit code: 0

```bash
docker inspect --format "{{json .Config.Cmd}}" web box
```

```
["nginx","-g","daemon off;"]
["sleep","600"]
```

exit code: 0

```bash
docker inspect --format "{{.State.StartedAt}}" web
```

```
2026-08-12T12:31:02.372179975Z
```

exit code: 0

```bash
docker inspect --format "{{range .Mounts}}{{.Source}} -> {{.Destination}} (RW={{.RW}}){{end}}" web
```

```
/workspace/lab/site -> /usr/share/nginx/html (RW=false)
```

exit code: 0

```bash
docker port web
```

```
80/tcp -> 0.0.0.0:8080
80/tcp -> [::]:8080
```

exit code: 0

## 8. docker stats / docker top
```bash
docker stats --no-stream
```

```
CONTAINER ID   NAME      CPU %     MEM USAGE / LIMIT   MEM %     NET I/O         BLOCK I/O   PIDS
375dad3ca9b3   box       0.00%     0B / 0B             0.00%     1.22kB / 126B   0B / 0B     1
ca4d825406e6   cache     0.22%     0B / 0B             0.00%     1.41kB / 126B   0B / 0B     6
e24cad7406f7   web       0.00%     0B / 0B             0.00%     6.4kB / 49kB    0B / 0B     33
```

exit code: 0

```bash
docker top box
```

```
UID                 PID                 PPID                C                   STIME               TTY                 TIME                CMD
root                3973                3949                0                   19:31               ?                   00:00:00            sleep 600
```

exit code: 0

```bash
docker top web | head -4
```

```
UID                 PID                 PPID                C                   STIME               TTY                 TIME                CMD
root                3744                3721                0                   19:31               ?                   00:00:00            nginx: master process nginx -g daemon off;
sshd                3804                3744                0                   19:31               ?                   00:00:00            nginx: worker process
sshd                3805                3744                0                   19:31               ?                   00:00:00            nginx: worker process
```

exit code: 0

## 9. stop != rm
```bash
docker inspect --format "{{.Id}}" cache
```

```
ca4d825406e6be47ab1ce71a8f851a32b301d1552b877904d14a0a8e319c717a
```

exit code: 0

```bash
docker stop cache
```

```
cache
```

exit code: 0

```bash
docker ps -a --format "table {{.Names}}\t{{.Status}}"
```

```
NAMES     STATUS
probe     Exited (0) About a minute ago
box       Up 2 minutes
cache     Exited (0) Less than a second ago
web       Up 2 minutes
```

exit code: 0

```bash
docker start cache
```

```
cache
```

exit code: 0

```bash
docker inspect --format "{{.Id}}" cache
```

```
ca4d825406e6be47ab1ce71a8f851a32b301d1552b877904d14a0a8e319c717a
```

exit code: 0

```bash
docker exec cache redis-cli GET fleet
```

```
3
```

exit code: 0

```bash
docker rm probe
```

```
probe
```

exit code: 0

```bash
docker rm cache
```

```
Error response from daemon: cannot remove container "cache": container is running: stop the container before removing or force remove
```

exit code: 1

```bash
docker rm -f cache
```

```
cache
```

exit code: 0

```bash
docker ps -a --format "table {{.Names}}\t{{.Status}}"
```

```
NAMES     STATUS
box       Up 2 minutes
web       Up 2 minutes
```

exit code: 0

## 10. images / rmi / prune / เก็บกวาดแบบปลอดภัย
```bash
docker rmi nginx:1.29-alpine
```

```
Error response from daemon: conflict: unable to delete nginx:1.29-alpine (must be forced) - container e24cad7406f7 is using its referenced image 5616878291a2
```

exit code: 1

```bash
docker ps -aq --filter label=lab=control-room
```

```
375dad3ca9b3
e24cad7406f7
```

exit code: 0

```bash
docker rm -f $(docker ps -aq --filter label=lab=control-room)
```

```
375dad3ca9b3
e24cad7406f7
```

exit code: 0

```bash
docker ps -a
```

```
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
```

exit code: 0

```bash
docker run -d --name t1 alpine:3.21 sleep 300; docker run --name t2 alpine:3.21 echo hi; docker ps -a --format "table {{.Names}}\t{{.Status}}"
```

```
eae3b3b063039907c9634a87eeb9dab15587ed40fb7eded9eb00f38705184a95
hi
NAMES     STATUS
t2        Exited (0) Less than a second ago
t1        Up Less than a second
```

exit code: 0

```bash
docker stop $(docker ps -aq)
```

```
436169922cc9
eae3b3b06303
```

exit code: 0

```bash
docker ps -a --format "table {{.Names}}\t{{.Status}}"
```

```
NAMES     STATUS
t2        Exited (0) 10 seconds ago
t1        Exited (137) Less than a second ago
```

exit code: 0

```bash
docker container prune -f
```

```
Deleted Containers:
436169922cc9a86b002cbc58652f618d2abee1c10c5c817acc510a61583d69ba
eae3b3b063039907c9634a87eeb9dab15587ed40fb7eded9eb00f38705184a95

Total reclaimed space: 8.192kB
```

exit code: 0

```bash
docker ps -a
```

```
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
```

exit code: 0

```bash
docker images
```

```
IMAGE               ID             DISK USAGE   CONTENT SIZE   EXTRA
alpine:3.21         48b0309ca019       12.2MB         3.73MB        
nginx:1.29-alpine   5616878291a2       93.5MB         26.9MB        
redis:7-alpine      e7723ff73d96       57.8MB         16.8MB        
redis:latest        344e3945a0b4        212MB         57.4MB        
ubuntu:24.04        561618e2c15b        119MB         31.7MB        
```

exit code: 0

```bash
docker rmi nginx:1.29-alpine
```

```
Untagged: nginx:1.29-alpine
Deleted: sha256:5616878291a2eed594aee8db4dade5878cf7edcb475e59193904b198d9b830de
```

exit code: 0

```bash
docker rmi redis:7-alpine redis:latest ubuntu:24.04 alpine:3.21 2>&1 | grep -E "^Untagged|^Deleted" | head -8
```

```
Untagged: redis:7-alpine
Deleted: sha256:e7723ff73d963f5cc6d9c4643ea3d989527a402a319239054e9472a7fb9219a2
Untagged: redis:latest
Deleted: sha256:344e3945a0b431c8ff1eecd58c5573538126bd756f02fc7e218ddf1fc2546366
Untagged: ubuntu:24.04
Deleted: sha256:561618e2c15bf2397621dd04f96926663a3b5616c189cf7e38db7e82f5c538ea
Untagged: alpine:3.21
Deleted: sha256:48b0309ca019d89d40f670aa1bc06e426dc0931948452e8491e3d65087abc07d
```

exit code: 0

```bash
docker image prune -f
```

```
Total reclaimed space: 0B
```

exit code: 0

```bash
docker images; docker ps -a
```

```
IMAGE   ID             DISK USAGE   CONTENT SIZE   EXTRA
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
```

exit code: 0

## 11. Cleanup (บังคับ)
```bash
docker rm -f $(docker ps -aq --filter label=lab=control-room) 2>/dev/null; echo "(ไม่มีอะไรให้ลบแล้ว)"
```

```
(ไม่มีอะไรให้ลบแล้ว)
```

exit code: 0

```bash
docker images
```

```
IMAGE   ID             DISK USAGE   CONTENT SIZE   EXTRA
```

exit code: 0

```bash
docker ps -a
```

```
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
```

exit code: 0

### บนเครื่องของเราเอง (outer host) — ลบเครื่องเรียนทิ้ง

```bash
docker rm -f devtools-lab001
docker ps -a --filter "name=^devtools-lab001"
```

```
devtools-lab001
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
```

