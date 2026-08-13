# evidence / transcript — LAB 5 `005_LAB_Ops_Clinic`

ทุกบล็อกด้านล่างคือ **คำสั่งจริง + ผลลัพธ์จริง** ที่รันในเครื่องเรียน
`tuchsanai/devtools:2569_1` (container ชื่อ `devtools-lab005`, SSH 2226, web 18051 → 8080)
เมื่อ 12 ส.ค. 2026 ทุกคำสั่งรันที่ `/workspace/lab` ซึ่งเป็นสำเนาของโฟลเดอร์แล็บนี้

รูปแบบ: บล็อกแรก = คำสั่ง · บล็อกที่สอง = output ดิบ (ไม่ตัด ไม่แต่ง) · ตามด้วย exit code

---

### 0b. ปลดล็อก memory controller ของเครื่องเรียน (Docker-in-Docker)

```bash
mkdir -p /sys/fs/cgroup/init
for p in $(cat /sys/fs/cgroup/cgroup.procs); do echo $p > /sys/fs/cgroup/init/cgroup.procs 2>/dev/null || true; done
echo "procs left in root: $(wc -l < /sys/fs/cgroup/cgroup.procs)"
echo "+cpu +memory +pids +io" > /sys/fs/cgroup/cgroup.subtree_control && echo "enable OK" || echo "enable FAIL"
cat /sys/fs/cgroup/cgroup.subtree_control
```

```
procs left in root: 0
enable OK
cpu io memory pids
```

_exit code: 0_

### 0b-2. รีสตาร์ท dockerd ในเครื่องเรียนให้รับค่าใหม่

```bash
pkill dockerd; sleep 3; (dockerd > /var/log/dockerd.log 2>&1 &); sleep 6
docker info >/dev/null 2>&1 && echo "dockerd back"
docker run --rm --memory=64m --memory-swap=64m alpine:3.21 sh -c "cat /sys/fs/cgroup/memory.max"
```

```
dockerd back
Digest: sha256:48b0309ca019d89d40f670aa1bc06e426dc0931948452e8491e3d65087abc07d
Status: Downloaded newer image for alpine:3.21
67108864
```

_exit code: 0_

### 0b-3. หลักฐานว่า "ถ้าไม่ทำ 0b จะพัง" (รันก่อนแก้ cgroup)

```bash
docker run -d --name patient-d --memory=64m --memory-swap=64m -p 8083:8080 ops-clinic:1.0
```

```
32ca27bc7b39484f60e88ea653047e65beb161a9ca269d159fada0eb8fdc4a3e
docker: Error response from daemon: failed to create task for container: failed to create shim task: OCI runtime create failed: runc create failed: unable to start container process: unable to apply cgroup configuration: cannot enter cgroupv2 "/sys/fs/cgroup/docker" with domain controllers -- it is in threaded mode

Run 'docker run --help' for more information
```

และ `docker stats` ในสภาพนั้นรายงาน `0B / 0B` :

```
NAME        MEM USAGE / LIMIT   MEM %     CPU %
patient-c   0B / 0B             0.00%     5.22%
patient-b   0B / 0B             0.00%     0.01%
```

_exit code: 0 (คำสั่ง run คืน container ID แล้วค่อย error ตอน start)_

### 0a. ตรวจว่า Docker พร้อม

```bash
docker --version; docker compose version
```

```
Docker version 29.6.2, build dfc4efb
Docker Compose version v5.3.1
```

_exit code: 0_

### 0c. ยืนยันว่า memory controller ถูกปลดล็อกแล้ว

```bash
cat /sys/fs/cgroup/cgroup.subtree_control; docker run --rm --memory=64m alpine:3.21 cat /sys/fs/cgroup/memory.max
```

```
cpuset cpu io memory hugetlb pids rdma
67108864
```

_exit code: 0_

### 0d. ดูไฟล์ในโฟลเดอร์แล็บ

```bash
ls -1 app patients compose.yaml
```

```
compose.yaml

app:
Dockerfile
app.py
requirements.txt

patients:
case-a.sh
case-b.sh
case-d.sh
```

_exit code: 0_

### 1. build image คนไข้

```bash
docker build -t ops-clinic:1.0 app/ 2>&1 | grep -vE "^#5 sha256|^#5 extracting|^$" | tail -22
```

```
#8 1.182 Downloading markupsafe-3.0.3-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (22 kB)
#8 1.193 Installing collected packages: MarkupSafe, itsdangerous, click, blinker, Werkzeug, Jinja2, flask
#8 1.422 Successfully installed Jinja2-3.1.6 MarkupSafe-3.0.3 Werkzeug-3.1.8 blinker-1.9.0 click-8.4.2 flask-3.1.0 itsdangerous-2.2.0
#8 1.422 WARNING: Running pip as the 'root' user can result in broken permissions and conflicting behaviour with the system package manager, possibly rendering your system unusable. It is recommended to use a virtual environment instead: https://pip.pypa.io/warnings/venv. Use the --root-user-action option if you know what you are doing and want to suppress this warning.
#8 1.481 
#8 1.481 [notice] A new release of pip is available: 25.0.1 -> 26.2.1
#8 1.481 [notice] To update, run: pip install --upgrade pip
#8 DONE 1.5s
#9 [5/5] COPY app.py .
#9 DONE 0.1s
#10 exporting to image
#10 exporting layers
#10 exporting layers 0.5s done
#10 exporting manifest sha256:a56c0037a3dcdddb35c97dbe390105410f8d20cea7da27995f8d147b170ceb07 0.0s done
#10 exporting config sha256:8fa67bb3eabd9fcd06cbe7631024ff45d27a9181afa32de39e40b1b9f63e79da 0.0s done
#10 exporting attestation manifest sha256:3f7d7783dd9bda76c1bad46db2ca66a1b532e6a55aaa9e6dfa84c7047fba3f59 0.0s done
#10 exporting manifest list sha256:75d571d2db84442848c95043c1316342d6c1eb2fa28aa76405319d510b520245
#10 exporting manifest list sha256:75d571d2db84442848c95043c1316342d6c1eb2fa28aa76405319d510b520245 0.0s done
#10 naming to docker.io/library/ops-clinic:1.0 done
#10 unpacking to docker.io/library/ops-clinic:1.0
#10 unpacking to docker.io/library/ops-clinic:1.0 0.2s done
#10 DONE 0.8s
```

_exit code: 0_

### 1b. docker images ops-clinic

```bash
docker images ops-clinic
```

```
IMAGE            ID             DISK USAGE   CONTENT SIZE   EXTRA
ops-clinic:1.0   75d571d2db84        197MB         48.2MB        
```

_exit code: 0_

### A1. เกิดคนไข้ A

```bash
docker rm -f patient-a >/dev/null 2>&1; docker run -d --name patient-a alpine:3.21 sh -c 'echo "boot: reading /etc/app.conf"; echo "FATAL: config not found" >&2; exit 1'
```

```
440f10188a766439dba3c4b4c83560891d0e7d879c81f20265856f0c3b3ac583
```

_exit code: 0_

### A2b. docker ps --filter name=patient-a

```bash
docker ps --filter name=patient-a
```

```
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
```

_exit code: 0_

### A3b. docker ps -a --filter name=patient-a

```bash
docker ps -a --filter name=patient-a
```

```
CONTAINER ID   IMAGE         COMMAND                   CREATED          STATUS                      PORTS     NAMES
440f10188a76   alpine:3.21   "sh -c 'echo \"boot: …"   15 seconds ago   Exited (1) 14 seconds ago             patient-a
```

_exit code: 0_

### A4. docker logs patient-a

```bash
docker logs patient-a
```

```
FATAL: config not found
boot: reading /etc/app.conf
```

_exit code: 0_

### A5. ใบชันสูตร

```bash
docker inspect --format 'status={{.State.Status}}  exitCode={{.State.ExitCode}}  OOMKilled={{.State.OOMKilled}}  error="{{.State.Error}}"' patient-a
```

```
status=exited  exitCode=1  OOMKilled=false  error=""
```

_exit code: 0_

### A6. รักษาผิดวิธี — --restart on-failure:3

```bash
docker rm -f patient-a2 >/dev/null 2>&1; docker run -d --name patient-a2 --restart on-failure:3 alpine:3.21 sh -c 'echo "boot: reading /etc/app.conf"; sleep 2; echo "FATAL: config not found" >&2; exit 1'
```

```
c3893a0743c9bd69949e03b98b452d41581f5d90dd310297f86ea244720cde7e
```

_exit code: 0_

### A7. เฝ้าดู RestartCount ไต่ขึ้น

```bash
for i in 0 1 2 3 4 5 6 7; do printf 't=%2ss  RestartCount=%s  Status=%s\n' $((i*2)) "$(docker inspect --format '{{.RestartCount}}' patient-a2)" "$(docker inspect --format '{{.State.Status}}' patient-a2)"; sleep 2; done
```

```
t= 0s  RestartCount=0  Status=running
t= 2s  RestartCount=1  Status=running
t= 4s  RestartCount=2  Status=running
t= 6s  RestartCount=3  Status=restarting
t= 8s  RestartCount=3  Status=running
t=10s  RestartCount=3  Status=exited
t=12s  RestartCount=3  Status=exited
t=14s  RestartCount=3  Status=exited
```

_exit code: 0_

### B1. รันแบบลืมใส่ -p

```bash
docker rm -f patient-b >/dev/null 2>&1; docker run -d --name patient-b ops-clinic:1.0
```

```
a95f5b508ea8f6964cd18e311b78d461336ba02399fb1cb56443625ba45f8852
```

_exit code: 0_

### B2. docker ps — Up ปกติดี

```bash
docker ps --filter name=patient-b
```

```
CONTAINER ID   IMAGE            COMMAND           CREATED         STATUS                   PORTS      NAMES
a95f5b508ea8   ops-clinic:1.0   "python app.py"   8 seconds ago   Up 7 seconds (healthy)   8080/tcp   patient-b
```

_exit code: 0_

### B3. เปิดเว็บไม่ได้

```bash
curl -s --max-time 3 http://localhost:8081/healthz; echo "curl exit code = $?"
```

```
curl exit code = 7
```

_exit code: 0_

### B4. docker port — ว่างเปล่า

```bash
docker port patient-b; echo "(ไม่มีบรรทัดไหนพิมพ์ออกมาเลย = ไม่มี port ที่ publish)"
```

```
(ไม่มีบรรทัดไหนพิมพ์ออกมาเลย = ไม่มี port ที่ publish)
```

_exit code: 0_

### B5. inspect Ports

```bash
docker inspect --format '{{json .NetworkSettings.Ports}}' patient-b
```

```
{"8080/tcp":null}
```

_exit code: 0_

### B6. แอปยังมีชีวิตอยู่ข้างใน

```bash
docker exec patient-b python -c "import urllib.request;print(urllib.request.urlopen('http://127.0.0.1:8080/healthz').read().decode())"
```

```
{"app":"ops-clinic","host":"a95f5b508ea8","rss_mb":32.2,"status":"ok","uptime_sec":7.6}
```

_exit code: 0_

### B7. รักษารอบแรก — -p 127.0.0.1:8081:8080

```bash
docker rm -f patient-b >/dev/null 2>&1; docker run -d --name patient-b -p 127.0.0.1:8081:8080 ops-clinic:1.0 >/dev/null; sleep 4; docker port patient-b
```

```
8080/tcp -> 127.0.0.1:8081
```

_exit code: 0_

### B8. ทดสอบสองทาง

```bash
probe(){ c=$(curl -s --max-time 3 -o /dev/null -w "%{http_code}" "$1"); if [ "$c" = "000" ]; then echo "$1  ->  ต่อไม่ติด"; else echo "$1  ->  HTTP $c"; fi; }; IP=$(hostname -i | awk "{print \$1}"); echo "IP ของเครื่องเรียน = $IP"; probe http://localhost:8081/healthz; probe http://$IP:8081/healthz
```

```
IP ของเครื่องเรียน = 172.17.0.3
http://localhost:8081/healthz  ->  HTTP 200
http://172.17.0.3:8081/healthz  ->  ต่อไม่ติด
```

_exit code: 0_

### B9. รักษาให้ถูก — -p 8081:8080

```bash
docker rm -f patient-b >/dev/null 2>&1; docker run -d --name patient-b -p 8081:8080 ops-clinic:1.0 >/dev/null; sleep 4; docker port patient-b
```

```
8080/tcp -> 0.0.0.0:8081
8080/tcp -> [::]:8081
```

_exit code: 0_

### B10. ทดสอบซ้ำ

```bash
probe(){ c=$(curl -s --max-time 3 -o /dev/null -w "%{http_code}" "$1"); if [ "$c" = "000" ]; then echo "$1  ->  ต่อไม่ติด"; else echo "$1  ->  HTTP $c"; fi; }; IP=$(hostname -i | awk "{print \$1}"); probe http://localhost:8081/healthz; probe http://$IP:8081/healthz
```

```
http://localhost:8081/healthz  ->  HTTP 200
http://172.17.0.3:8081/healthz  ->  HTTP 200
```

_exit code: 0_

### B11. สรุปด้วย docker ps

```bash
docker ps --filter name=patient-b --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

```
NAMES       STATUS                            PORTS
patient-b   Up 4 seconds (health: starting)   0.0.0.0:8081->8080/tcp, [::]:8081->8080/tcp
```

_exit code: 0_

### C1. บรรทัด HEALTHCHECK ใน Dockerfile

```bash
grep -n -A1 "^HEALTHCHECK" app/Dockerfile
```

```
17:HEALTHCHECK --interval=5s --timeout=3s --start-period=5s --retries=3 \
18-  CMD python -c "import urllib.request;urllib.request.urlopen('http://127.0.0.1:8080/healthz',timeout=2)"
```

_exit code: 0_

### C2. เกิดคนไข้ C แล้วเฝ้าดู STATUS

```bash
docker rm -f patient-c >/dev/null 2>&1; docker run -d --name patient-c -p 8082:8080 ops-clinic:1.0 >/dev/null; for i in 0 1 2 3 4 5; do printf "t=%2ss  %s\n" $((i*3)) "$(docker ps --filter name=patient-c --format "{{.Status}}")"; sleep 3; done
```

```
t= 0s  Up Less than a second (health: starting)
t= 3s  Up 3 seconds (health: starting)
t= 6s  Up 6 seconds (healthy)
t= 9s  Up 9 seconds (healthy)
t=12s  Up 12 seconds (healthy)
t=15s  Up 15 seconds (healthy)
```

_exit code: 0_

### C3. ทำให้ป่วย

```bash
curl -s -X POST http://localhost:8082/break; echo; curl -s -o /dev/null -w "GET /healthz -> HTTP %{http_code}\n" http://localhost:8082/healthz
```

```
{"healthy":false,"ok":true,"reason":"database connection lost (simulated by POST /break)"}

GET /healthz -> HTTP 500
```

_exit code: 0_

### C4. เฝ้าดู STATUS เปลี่ยนเป็น unhealthy

```bash
for i in 0 1 2 3 4 5 6; do printf "t=%2ss  %s\n" $((i*3)) "$(docker ps --filter name=patient-c --format "{{.Status}}")"; sleep 3; done
```

```
t= 0s  Up 18 seconds (healthy)
t= 3s  Up 21 seconds (healthy)
t= 6s  Up 24 seconds (healthy)
t= 9s  Up 27 seconds (healthy)
t=12s  Up 30 seconds (healthy)
t=15s  Up 33 seconds (unhealthy)
t=18s  Up 36 seconds (unhealthy)
```

_exit code: 0_

### C5b. หลักฐานชั้นที่ 1 — สรุปสถานะ

```bash
docker inspect --format 'Health = {{.State.Health.Status}}   FailingStreak = {{.State.Health.FailingStreak}}' patient-c
```

```
Health = unhealthy   FailingStreak = 3
```

_exit code: 0_

### C6b. หลักฐานชั้นที่ 2 — log ของหมอ (5 ครั้งล่าสุด)

```bash
docker inspect --format '{{json .State.Health}}' patient-c | python3 -c "import json,sys; h=json.load(sys.stdin); [print(p['Start'][11:19], 'exit=' + str(p['ExitCode']), '|', (p['Output'].strip().splitlines() or ['(ผ่าน ไม่มี output)'])[-1]) for p in h['Log']]"
```

```
19:43:45 exit=0 | (ผ่าน ไม่มี output)
19:43:51 exit=0 | (ผ่าน ไม่มี output)
19:43:56 exit=1 | urllib.error.HTTPError: HTTP Error 500: INTERNAL SERVER ERROR
19:44:01 exit=1 | urllib.error.HTTPError: HTTP Error 500: INTERNAL SERVER ERROR
19:44:06 exit=1 | urllib.error.HTTPError: HTTP Error 500: INTERNAL SERVER ERROR
```

_exit code: 0_

### C7b. unhealthy ไม่ได้ทำให้ container หยุดเอง

```bash
docker ps --filter name=patient-c --format "table {{.Names}}\t{{.Status}}"; curl -s -o /dev/null -w "หน้าเว็บ / ยังตอบ HTTP %{http_code}\n" http://localhost:8082/
```

```
NAMES       STATUS
patient-c   Up About a minute (unhealthy)
หน้าเว็บ / ยังตอบ HTTP 200
```

_exit code: 0_

### C8b. รักษา — POST /fix

```bash
curl -s -X POST http://localhost:8082/fix; echo; sleep 8; docker ps --filter name=patient-c --format "table {{.Names}}\t{{.Status}}"; docker inspect --format "Health = {{.State.Health.Status}}   FailingStreak = {{.State.Health.FailingStreak}}" patient-c
```

```
{"healthy":true,"ok":true}

NAMES       STATUS
patient-c   Up About a minute (healthy)
Health = healthy   FailingStreak = 0
```

_exit code: 0_

### D1. เกิดคนไข้ D — จำกัดแรม 64 MB

```bash
docker rm -f patient-d >/dev/null 2>&1; docker run -d --name patient-d --memory=64m --memory-swap=64m -p 8083:8080 ops-clinic:1.0; sleep 5; docker ps --filter name=patient-d --format "{{.Names}}  {{.Status}}"
```

```
6e0f71d152bb72810f0368c3f3a5b9d86fa969103dea7a9b6806d2fb4801d74c
patient-d  Up 5 seconds (health: starting)
```

_exit code: 0_

### D2. docker stats ก่อนป่วย

```bash
docker stats --no-stream --format "table {{.Name}}\t{{.MemUsage}}\t{{.MemPerc}}\t{{.CPUPerc}}"
```

```
NAME        MEM USAGE / LIMIT   MEM %     CPU %
patient-d   21.59MiB / 64MiB    33.73%    0.01%
```

_exit code: 0_

### D3. สั่งให้รั่ว 2 MB ทุก 1 วินาที

```bash
curl -s -X POST "http://localhost:8083/leak?mb=2&delay=1"; echo
```

```
{"chunk_mb":2,"delay_sec":1.0,"leaking":true,"limit_mb":64,"ok":true,"rss_mb":34.5}
```

_exit code: 0_

### D4. เฝ้าดูแรมไต่ขึ้นจนตาย

```bash
for i in 1 2 3 4 5 6 7 8; do S=$(docker stats --no-stream --format "{{.MemUsage}}  {{.MemPerc}}" patient-d 2>/dev/null); P=$(docker ps -a --filter name=patient-d --format "{{.Status}}"); printf "%-28s %s\n" "${S:-(ตายแล้ว)}" "$P"; sleep 2; done
```

```
35.95MiB / 64MiB  56.17%     Up 12 seconds (healthy)
41.89MiB / 64MiB  65.45%     Up 15 seconds (healthy)
47.74MiB / 64MiB  74.59%     Up 18 seconds (healthy)
53.82MiB / 64MiB  84.09%     Up 21 seconds (healthy)
59.75MiB / 64MiB  93.36%     Up 24 seconds (healthy)
0B / 0B  0.00%               Exited (137) 1 second ago
0B / 0B  0.00%               Exited (137) 3 seconds ago
0B / 0B  0.00%               Exited (137) 5 seconds ago
```

_exit code: 0_

### D5. ใบชันสูตร

```bash
docker inspect --format 'status={{.State.Status}}  exitCode={{.State.ExitCode}}  OOMKilled={{.State.OOMKilled}}  error="{{.State.Error}}"' patient-d
```

```
status=exited  exitCode=137  OOMKilled=true  error=""
```

_exit code: 0_

### D6. log ไม่ได้บอกอะไรเลย (ท้าย 4 บรรทัด)

```bash
docker logs --tail 4 patient-d
```

```
172.18.0.1 - - [12/Aug/2026 12:34:58] "POST /leak?mb=2&delay=1 HTTP/1.1" 200 -
127.0.0.1 - - [12/Aug/2026 12:35:02] "GET /healthz HTTP/1.1" 200 -
127.0.0.1 - - [12/Aug/2026 12:35:07] "GET /healthz HTTP/1.1" 200 -
127.0.0.1 - - [12/Aug/2026 12:35:12] "GET /healthz HTTP/1.1" 200 -
```

_exit code: 0_

### D7. ค่า limit ที่ตั้งไว้

```bash
docker inspect --format 'Memory={{.HostConfig.Memory}} bytes  MemorySwap={{.HostConfig.MemorySwap}} bytes  NanoCpus={{.HostConfig.NanoCpus}}' patient-d
```

```
Memory=67108864 bytes  MemorySwap=67108864 bytes  NanoCpus=0
```

_exit code: 0_

### E1. Terminal 2 — docker events (รันค้างไว้ระหว่างทำ Terminal 1)

```bash
docker events --filter type=container \
  --filter event=create --filter event=start --filter event=health_status \
  --filter event=kill --filter event=die --filter event=destroy
```

Terminal 1 ที่รันคู่กัน:

```bash
docker run -d --name patient-e -p 8084:8080 ops-clinic:1.0
sleep 9
curl -s -X POST http://localhost:8084/break
sleep 18
docker rm -f patient-e
```

ผลที่ Terminal 2 พิมพ์ออกมา:

```
2026-08-12T19:36:45.746034365+07:00 container create ff621db6e80a32d2019964823b3ee5735b0fc1cedab036b33b202f56149ca19a (image=ops-clinic:1.0, name=patient-e)
2026-08-12T19:36:45.984212851+07:00 container start ff621db6e80a32d2019964823b3ee5735b0fc1cedab036b33b202f56149ca19a (image=ops-clinic:1.0, name=patient-e)
2026-08-12T19:36:51.076190266+07:00 container health_status: healthy ff621db6e80a32d2019964823b3ee5735b0fc1cedab036b33b202f56149ca19a (image=ops-clinic:1.0, name=patient-e)
2026-08-12T19:37:06.354251147+07:00 container health_status: unhealthy ff621db6e80a32d2019964823b3ee5735b0fc1cedab036b33b202f56149ca19a (image=ops-clinic:1.0, name=patient-e)
2026-08-12T19:37:13.018027822+07:00 container kill ff621db6e80a32d2019964823b3ee5735b0fc1cedab036b33b202f56149ca19a (image=ops-clinic:1.0, name=patient-e, signal=9)
2026-08-12T19:37:13.360433406+07:00 container die ff621db6e80a32d2019964823b3ee5735b0fc1cedab036b33b202f56149ca19a (execDuration=27, exitCode=137, image=ops-clinic:1.0, name=patient-e)
2026-08-12T19:37:13.387867894+07:00 container destroy ff621db6e80a32d2019964823b3ee5735b0fc1cedab036b33b202f56149ca19a (image=ops-clinic:1.0, name=patient-e)
```

_exit code: 0 (คำสั่ง events ถูกหยุดด้วย Ctrl+C หลังจากนั้น)_

### F1. compose.yaml — ฉบับที่หายดีแล้ว

```bash
cat compose.yaml
```

```
services:
  clinic:
    build: ./app
    image: ops-clinic:1.0
    container_name: clinic
    ports:
      - "8080:8080"
    environment:
      APP_NAME: clinic-cured
    # ยาที่ 1 : ล้มแล้วลุกเองอัตโนมัติ (แต่ไม่ลุกถ้าเราสั่ง stop เอง)
    restart: unless-stopped
    # ยาที่ 2 : ให้ Docker วัดชีพจรเอง แทนที่จะรอคนมาเปิดเว็บดู
    healthcheck:
      test: ["CMD", "python", "-c",
             "import urllib.request;urllib.request.urlopen('http://127.0.0.1:8080/healthz',timeout=2)"]
      interval: 5s
      timeout: 3s
      retries: 3
      start_period: 5s
    # ยาที่ 3 : จำกัดทรัพยากร ไม่ให้ป่วยแล้วลากเครื่องทั้งเครื่องลงไปด้วย
    deploy:
      resources:
        limits:
          memory: 256M
          cpus: "0.50"
```

_exit code: 0_

### F2. docker compose up -d --build

```bash
docker compose up -d --build 2>&1 | tail -12
```

```
#11 unpacking to docker.io/library/ops-clinic:1.0 0.0s done
#11 DONE 0.2s

#12 resolving provenance for metadata file
#12 DONE 0.0s
 Image ops-clinic:1.0 Built 
 Network lab_default Creating 
 Network lab_default Created 
 Container clinic Creating 
 Container clinic Created 
 Container clinic Starting 
 Container clinic Started 
```

_exit code: 0_

### F3. docker compose ps

```bash
docker compose ps
```

```
NAME      IMAGE            COMMAND           SERVICE   CREATED          STATUS                    PORTS
clinic    ops-clinic:1.0   "python app.py"   clinic    18 seconds ago   Up 17 seconds (healthy)   0.0.0.0:8080->8080/tcp, [::]:8080->8080/tcp
```

_exit code: 0_

### F4. ยาถูกจ่ายจริงไหม

```bash
docker inspect --format 'RestartPolicy = {{.HostConfig.RestartPolicy.Name}}   Memory = {{.HostConfig.Memory}} bytes   NanoCpus = {{.HostConfig.NanoCpus}}   Health = {{.State.Health.Status}}' clinic
```

```
RestartPolicy = unless-stopped   Memory = 268435456 bytes   NanoCpus = 500000000   Health = healthy
```

_exit code: 0_

### F5b. compose logs (3 บรรทัดท้าย)

```bash
docker compose logs clinic --tail 3
```

```
clinic  | 127.0.0.1 - - [12/Aug/2026 12:56:15] "GET /healthz HTTP/1.1" 200 -
clinic  | 127.0.0.1 - - [12/Aug/2026 12:56:21] "GET /healthz HTTP/1.1" 200 -
clinic  | 127.0.0.1 - - [12/Aug/2026 12:56:26] "GET /healthz HTTP/1.1" 200 -
```

_exit code: 0_

### F6. เว็บตอบจริง

```bash
curl -s http://localhost:8080/healthz; echo
```

```
{"app":"clinic-cured","host":"c167d154ef47","rss_mb":32.2,"status":"ok","uptime_sec":17.7}
```

_exit code: 0_

### F7. ทดสอบยาที่ 1 — ฆ่าทิ้งแล้วมันลุกเองไหม

```bash
docker kill clinic; sleep 8; docker ps --filter name=clinic --format "{{.Names}}  {{.Status}}"; docker inspect --format "RestartCount = {{.RestartCount}}" clinic
```

```
clinic
RestartCount = 0
```

_exit code: 0_

### F8. ทำไมสั่งฆ่าเองแล้วไม่ลุก

```bash
docker inspect --format "status={{.State.Status}}  RestartCount={{.RestartCount}}  policy={{.HostConfig.RestartPolicy.Name}}  exitCode={{.State.ExitCode}}" clinic; grep -o "stopping restart-manager" /var/log/dockerd2.log | tail -1
```

```
status=exited  RestartCount=0  policy=unless-stopped  exitCode=137
stopping restart-manager
```

_exit code: 0_

### F9. สตาร์ทกลับ แล้วทดสอบด้วยอาการจริง (แรมรั่ว)

```bash
docker compose up -d >/dev/null 2>&1; sleep 8; docker compose ps --format "table {{.Name}}\t{{.Status}}"; curl -s -X POST "http://localhost:8080/leak?mb=8&delay=0.2"; echo
```

```
NAME      STATUS
clinic    Up 8 seconds (healthy)
{"chunk_mb":8,"delay_sec":0.2,"leaking":true,"limit_mb":256,"ok":true,"rss_mb":40.0}
```

_exit code: 0_

### F10. ตายแล้วลุกเองอัตโนมัติ

```bash
for i in 1 2 3 4 5 6 7 8 9 10; do printf "t=%2ss  %-34s RestartCount=%s  OOMKilled=%s\n" $((i*3)) "$(docker ps -a --filter name=clinic --format "{{.Status}}")" "$(docker inspect --format "{{.RestartCount}}" clinic)" "$(docker inspect --format "{{.State.OOMKilled}}" clinic)"; sleep 3; done
```

```
t= 3s  Up 13 seconds (healthy)            RestartCount=0  OOMKilled=false
t= 6s  Up 16 seconds (healthy)            RestartCount=0  OOMKilled=false
t= 9s  Up 19 seconds (healthy)            RestartCount=0  OOMKilled=false
t=12s  Up 2 seconds (health: starting)    RestartCount=1  OOMKilled=false
t=15s  Up 5 seconds (health: starting)    RestartCount=1  OOMKilled=false
t=18s  Up 8 seconds (healthy)             RestartCount=1  OOMKilled=false
t=21s  Up 11 seconds (healthy)            RestartCount=1  OOMKilled=false
t=24s  Up 14 seconds (healthy)            RestartCount=1  OOMKilled=false
t=27s  Up 17 seconds (healthy)            RestartCount=1  OOMKilled=false
t=30s  Up 20 seconds (healthy)            RestartCount=1  OOMKilled=false
```

_exit code: 0_

### G1. ปิดคลินิกด้วย compose

```bash
docker compose down
```

```
 Container clinic Stopping 
 Container clinic Stopped 
 Container clinic Removing 
 Container clinic Removed 
 Network lab_default Removing 
 Network lab_default Removed 
```

_exit code: 0_

### G2. ลบคนไข้ทั้งหมด

```bash
docker rm -f patient-a patient-a2 patient-b patient-c patient-d
```

```
patient-a
patient-a2
patient-b
patient-c
patient-d
```

_exit code: 0_

### G3. ลบ image

```bash
docker rmi ops-clinic:1.0
```

```
Untagged: ops-clinic:1.0
Deleted: sha256:0582a7b40c5af416d5ee8cdaebfff76453186109441b71f5d1bf72ae53db6bbc
```

_exit code: 0_

### G4. ตรวจว่าไม่เหลืออะไร

```bash
docker ps -a; docker images ops-clinic
```

```
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
IMAGE   ID             DISK USAGE   CONTENT SIZE   EXTRA
```

_exit code: 0_

---

### H. ลบเครื่องเรียนบน host ชั้นนอก (รันบนเครื่องของเราเอง ไม่ใช่ในเครื่องเรียน)

```bash
docker rm -f devtools-lab005
docker ps -a --filter "name=^devtools-lab005"
```

```
devtools-lab005
```

```
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
```

_exit code: 0 — ไม่มีเครื่องเรียนของแล็บไหนค้างอยู่บน host แล้ว_

### I. เก็บกวาดในเครื่องเรียนรอบสุดท้ายก่อนลบกล่องนอก

```bash
docker compose down >/dev/null 2>&1; docker rmi ops-clinic:1.0 >/dev/null 2>&1; docker ps -a
```

```
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
```

_exit code: 0_
