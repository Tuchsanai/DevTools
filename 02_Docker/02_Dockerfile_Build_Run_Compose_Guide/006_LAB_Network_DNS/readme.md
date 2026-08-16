# LAB 6 — Network & DNS : ให้ container คุยกันด้วย "ชื่อ"

> โฟลเดอร์ `006_LAB_Network_DNS` · ไฟล์ของแล็บ : `Dockerfile` · `site/index.html.tpl` (หน้า **Container Network Console**) · `docker/netlab.conf` · `docker/40-render-console.sh` · `secret/flag.txt` · `verify.sh`

### 🎯 แล็บนี้ใน 30 วินาที

| | |
|---|---|
| **คำถามเดียวที่ตอบให้จบ** | container สองตัวบนเครื่องเดียวกัน เรียกกันด้วย **ชื่อ** ได้ไหม — ถ้าไม่ได้ ต้องแก้ตรงไหน |
| **ต้องผ่านอะไรมาก่อน** | **LAB 1** (โดยเฉพาะ `EXPOSE` ไม่ได้เปิดพอร์ต · `-p` ต่างหากที่เปิด) |
| **เวลา** | ~35 นาที · การทดลอง **11 อัน** อันละ 2–4 นาที |
| **จบแล้วต้องทำได้เอง** | สร้าง user-defined network ให้ service เรียกกันด้วยชื่อ · ต่อ/ถอด network ตอนกำลังรัน · บอกได้ว่าเมื่อไรต้อง `-p` |
| **แล็บนี้ยัง *ไม่* สอน** | การประกาศ network ในไฟล์เดียวพร้อม `internal: true` → **LAB 7** |

---

## ทฤษฎีก่อนลงมือ

### container แต่ละตัวมีโลก network ของตัวเอง

![ภาพเปรียบเทียบเส้นทางจากเครื่องอื่นเข้าสู่ container ในโหมด bridge host และ none](./images/theory-network-modes.svg)

> 🖼 **วิธีอ่านรูปนี้:** เริ่มจากเครื่องอื่นทางซ้าย แล้วตามเส้นไปยัง container ของแต่ละโหมด — **bridge** ต้องผ่านขอบ host และกฎ publish port · **host** ใช้ทางเข้าเดียวกับเครื่องโดยตรง · **none** ไม่มีเส้นทางเข้าออกเลย

| ชนิด | แนวคิด | ใช้เมื่อไร |
|---|---|---|
| **bridge** | network เสมือนบนเครื่อง คุยออกนอกผ่าน NAT — **ค่าเริ่มต้น** | container ทั่วไป · **แต่ให้สร้างเองด้วย `docker network create`** เพื่อให้ได้ DNS |
| **host** | ใช้ network stack ของเครื่องตรง ๆ ไม่มี IP แยก ไม่ต้อง `-p` | กรณีเฉพาะที่ต้องการ performance สูงสุด (Linux เท่านั้น) |
| **none** | ไม่ต่อ network เลย เหลือแค่ `lo` | งานประมวลผลออฟไลน์ / ต้องการตัดการสื่อสาร |

### ความต่างข้อเดียวที่สำคัญที่สุด

> **default bridge = ไม่มี DNS ของชื่อ container** · **user-defined bridge = มี DNS ที่ `127.0.0.11`**

![ภาพ app-net ที่ embedded DNS จดชื่อ container เพื่อให้ client เรียกบริการด้วยชื่อ](./images/theory-appnet-dns.svg)

> 🖼 **วิธีอ่านรูปนี้:** ดูตารางชื่อภายใน `app-net` ก่อน แล้วตามลูกศรจาก client ไปถาม `127.0.0.11` และต่อถึง `web:80` · ชื่อยังใช้รูปเดิมได้แม้ Docker เปลี่ยน IP ภายหลัง

### สิ่งที่มักเข้าใจผิด

- **คิดว่า** default bridge ติดต่อกันไม่ได้ → **จริง ๆ** ติดต่อด้วย **IP ได้** ที่พังคือการแปลงชื่อ (การทดลองที่ 3–4)
- **คิดว่า** ต้อง `-p` ทุก service ถึงจะเรียกกันได้ → **จริง ๆ** container ใน network เดียวกันเรียก port ของกันได้ตรง ๆ (การทดลองที่ 8)
- **คิดว่า** IP เป็นตัวตนถาวรของ container → **จริง ๆ** IP เปลี่ยนได้เมื่อสร้างใหม่ ชื่อต่างหากที่คงที่ (การทดลองที่ 11)

---

## เตรียมเครื่องเรียน

### ขั้นที่ 1 — เปิดกล่องเรียน

รันบน **เครื่องของเราเอง** :

```bash
docker rm -f devtools-df-lab6 2>/dev/null
docker run -dit --name devtools-df-lab6 --privileged \
  -p 2236:22 -p 8186:8186 tuchsanai/devtools:2569_1
ssh root@localhost -p 2236        # password : passwd
```

> 📝 **ต้อง publish `8186` ตั้งแต่ตอนสร้างกล่อง** เพราะ Docker เปลี่ยน port mapping ของ container ที่สร้างแล้วไม่ได้

### ขั้นที่ 2 — โหลดโค้ดแล็บแล้ว build image

**คำสั่งทุกอันหลังจากนี้พิมพ์ข้างในกล่องเรียน**

```bash
mkdir -p ~/labwork && cd ~/labwork
git clone https://github.com/Tuchsanai/DevTools.git
cd DevTools/02_Docker/02_Dockerfile_Build_Run_Compose_Guide/006_LAB_Network_DNS
docker build -t netlab-web:1.0 .
```

> 📝 image นี้เป็น nginx ที่ **render หน้าเว็บใหม่ทุกครั้งที่ start** โดยอ่าน hostname / IP / DNS resolver **ของตัวเอง** — หน้าเว็บจึงรายงานของจริง ไม่ใช่ค่าที่พิมพ์ค้างไว้

---

## การทดลองที่ 1 — Docker แถม network อะไรมาให้บ้าง

**คำถาม:** เครื่องที่เพิ่งติดตั้ง Docker มี network กี่ตัว

```bash
docker network ls
```

✅ **สิ่งที่ต้องเห็น** — **3 แถวเป๊ะ** (NETWORK ID ของแต่ละเครื่องต่างกัน) :

```
NETWORK ID     NAME      DRIVER    SCOPE
efbc654b43bf   bridge    bridge    local
5d944a33c501   host      host      local
11f8ea3d2c95   none      null      local
```

> 📝 สังเกตว่า network ชื่อ `none` มี driver ว่า **`null`** — ชื่อกับ driver ไม่จำเป็นต้องสะกดเหมือนกัน · `SCOPE = local` แปลว่าใช้ได้เฉพาะเครื่องนี้

---

## การทดลองที่ 2 — บน default bridge เรียกด้วยชื่อได้ไหม

**คำถาม:** เปิด container ไว้เฉย ๆ แล้วให้อีกตัวยิงด้วยชื่อ จะได้หน้าเว็บไหม

```bash
docker run -d --name web-legacy -e SERVICE_NAME=web-legacy netlab-web:1.0
docker run --rm busybox:1.36 wget -qO- http://web-legacy
```

✅ **สิ่งที่ต้องเห็น** — ไม่ได้หน้าเว็บ แต่ได้ **error บรรทัดเดียว** :

```
wget: bad address 'web-legacy'
```

> 📝 ครั้งแรกที่เรียก `busybox:1.36` Docker จะ **pull image ก่อน** จึงมีบรรทัด `Pulling from library/busybox` นำหน้า — ไม่ใช่ error · **ไม่ได้ใส่ `--network`** จึงตกไปอยู่บน `bridge` (default) · `bad address` แปลว่า **แปลงชื่อเป็น IP ไม่สำเร็จ** — ยังไม่ทันได้ต่อ TCP ด้วยซ้ำ · `-qO-` = เงียบ ๆ แล้วพ่นผลออก stdout (ตัวหลังเป็น **ตัวโอใหญ่** ไม่ใช่เลขศูนย์)

---

## การทดลองที่ 3 — แล้วสายขาดหรือแค่หาชื่อไม่เจอ

**คำถาม:** ถ้าเปลี่ยนจากชื่อเป็น IP จะติดต่อได้ไหม

```bash
IP=$(docker inspect -f '{{.NetworkSettings.Networks.bridge.IPAddress}}' web-legacy)
echo "IP ของ web-legacy = $IP"
docker run --rm busybox:1.36 wget -qO- http://$IP/healthz
```

✅ **สิ่งที่ต้องเห็น** — **ต่อถึง!** (IP ของแต่ละคนจะต่างกัน) :

```
IP ของ web-legacy = 172.18.0.2
ok
```

> 📝 **สรุปสองการทดลองนี้:** default bridge **ต่อกันได้อยู่แล้ว** ปัญหาอยู่ที่ **ไม่มีบริการแปลงชื่อ** ให้เท่านั้น — และการไปจำ IP เองคือทางที่ผิด (การทดลองที่ 11 จะพิสูจน์ว่าทำไม)

---

## การทดลองที่ 4 — สร้าง network เองแล้วลองใหม่

**คำถาม:** ต้องแก้ตรงไหนถึงจะเรียกด้วยชื่อได้

```bash
docker network create app-net
docker run -d --name web --network app-net -e SERVICE_NAME=web -p 8186:8186 netlab-web:1.0
docker run --rm --network app-net busybox:1.36 cat /etc/resolv.conf
```

✅ **สิ่งที่ต้องเห็น** — resolver เปลี่ยนเป็น **`127.0.0.11`** :

```
# Generated by Docker Engine.
nameserver 127.0.0.11
options ndots:0

# Based on host file: '/etc/resolv.conf' (internal resolver)
# ExtServers: [host(192.168.65.7)]
```

ทีนี้ยิงด้วย **ชื่อ** :

```bash
docker run --rm --network app-net busybox:1.36 nslookup web
docker run --rm --network app-net busybox:1.36 wget -qO- http://web/healthz
```

✅ **สิ่งที่ต้องเห็น** — แปลงชื่อได้ และเรียกถึงจริง :

```
Name:	web
Address: 172.19.0.2

ok
```

> 📝 `docker network create <ชื่อ>` **ไม่ต้องระบุ driver** เพราะค่าเริ่มต้นคือ `bridge` อยู่แล้ว · `127.0.0.11` คือ **embedded DNS ของ Docker** ที่โผล่มาเฉพาะบน user-defined network · **ต้องใส่ `--network app-net` ทั้งสองฝั่ง** — DNS ทำงานเฉพาะภายใน network เดียวกัน

---

## การทดลองที่ 5 — เปิดหน้า Console ดูค่าจริงของ container

**คำถาม:** container มองเห็นตัวเองเป็นอย่างไร

เปิดในเบราว์เซอร์บนเครื่องเราที่ **`http://localhost:8186`** :

![Container Network Console แสดง service, hostname, container IP, DNS resolver 127.0.0.11, interfaces และแผนผัง network ทั้ง 3 ชนิด](./images/network-console.png)

หรือเช็กจาก terminal :

```bash
curl -s -m 3 http://localhost:8186/healthz
```

✅ **สิ่งที่ต้องเห็น** — `ok` และการ์ด **DNS RESOLVER** บนหน้าเว็บขึ้น `127.0.0.11`

> 📝 ถ้าเปิดไม่ขึ้น ให้ย้อนไปดูว่าตอนสร้างกล่องเรียนใส่ `-p 8186:8186` ครบไหม — **เพิ่มทีหลังไม่ได้** ต้องลบกล่องแล้วสร้างใหม่

---

## การทดลองที่ 6 — อ่านไส้ในของ network

**คำถาม:** ใครอยู่ใน network นี้บ้าง และได้ IP อะไร

เปิด container ตัวที่สองก่อน :

```bash
docker run -d --name api --network app-net -e SERVICE_NAME=api netlab-web:1.0
docker network inspect -f '{{range .IPAM.Config}}subnet={{.Subnet}} gateway={{.Gateway}}{{end}}' app-net
docker network inspect -f '{{range .Containers}}{{.Name}} = {{.IPv4Address}}{{println}}{{end}}' app-net
```

✅ **สิ่งที่ต้องเห็น** — ช่วง IP ของ network และรายชื่อสมาชิก (ลำดับแถวไม่แน่นอน) :

```
subnet=172.19.0.0/16 gateway=172.19.0.1

web = 172.19.0.2/16
api = 172.19.0.3/16
```

> 📝 **กติกาของ `--format` ที่ต้องจำ:** ค่าเดี่ยวอย่าง `.Name` เขียนตรง ๆ ได้ · แต่ `.IPAM.Config` เป็น **list** และ `.Containers` เป็น **map** — ต้อง `{{range}}...{{end}}` วนเสมอ · ถ้าเขียน `{{.Containers.Name}}` ตรง ๆ จะได้ `<no value>` เงียบ ๆ (หลอกกว่า error เสียอีก)

---

## การทดลองที่ 7 — ทำไม backend ไม่ต้อง `-p`

**คำถาม:** `api` ที่เปิดโดยไม่มี `-p` เลย เพื่อนเรียกได้ไหม

```bash
docker port api ; echo "^^^ ว่างเปล่า = ไม่ได้ publish port ใด ๆ"
docker run --rm --network app-net busybox:1.36 wget -qO- http://api/healthz
```

✅ **สิ่งที่ต้องเห็น** — `docker port api` **ไม่พิมพ์อะไรเลย** (ไม่ใช่ error) แต่เพื่อนใน network เดียวกันยังเรียกได้ปกติ :

```
^^^ ว่างเปล่า = ไม่ได้ publish port ใด ๆ
ok
```

> 📝 **คำตอบ:** `-p` มีไว้เปิดให้ **คนนอก** (เบราว์เซอร์บนเครื่องเรา) เข้าถึงเท่านั้น · `web` เรียก `api` (หรือ `redis`, `postgres`) **ไม่ต้อง `-p`** เพราะคุยกันภายใน network เดียวกัน — **การไม่เปิด port ที่ไม่จำเป็นคือความปลอดภัยที่ได้มาฟรี ๆ**

---

## การทดลองที่ 8 — ต่อ network เพิ่มตอน container กำลังรัน

**คำถาม:** container ที่รันอยู่แล้ว ย้าย/เพิ่ม network ได้ไหมโดยไม่ restart

> **โจทย์:** `vault` เก็บข้อความลับไว้ แต่อยู่คนละ network กับสายลับของเรา (`agent`) — **ห้ามลบหรือสร้าง `agent` ใหม่**

```bash
docker network create vault-net
docker run -d --name vault --network vault-net \
  -v $PWD/secret/flag.txt:/usr/share/nginx/html/flag.txt:ro \
  -e SERVICE_NAME=vault netlab-web:1.0
docker run -d --name agent --network app-net busybox:1.36 sleep 3600
docker exec agent wget -qO- http://vault/flag.txt
```

✅ **สิ่งที่ต้องเห็น** — ล้วงไม่ได้ เพราะคนละ network จึงมองไม่เห็นแม้แต่ชื่อ :

```
wget: bad address 'vault'
```

**เชื่อม network เพิ่มขณะที่ `agent` ยังรันอยู่:**

```bash
docker network connect vault-net agent
docker inspect -f '{{range $k,$v := .NetworkSettings.Networks}}{{$k}} {{end}}' agent
docker exec agent wget -qO- http://vault/flag.txt
```

✅ **สิ่งที่ต้องเห็น** — `agent` มี 2 network แล้ว และได้ธงมา :

```
app-net vault-net

DOCKER-NET-FLAG{name_resolution_beats_hardcoded_ip}
```

![ภาพภารกิจ agent บน app-net ที่หา vault ไม่พบก่อนเชื่อม vault-net และมีสองขาหลังเชื่อม](./images/theory-network-connect.svg)

> 🖼 **วิธีอ่านรูปนี้:** `docker network connect` **เพิ่มขา** เข้าสู่ `vault-net` โดยไม่ถอดขาเดิม — container เดียวจึงเห็นทั้ง `api` และ `vault`

**ถอดออกแล้วดูว่ากระทบขาอื่นไหม:**

```bash
docker network disconnect vault-net agent
docker exec agent wget -qO- http://vault/flag.txt
docker exec agent wget -qO- http://api/healthz
```

✅ **สิ่งที่ต้องเห็น** — `vault` หายไปจากสายตา แต่ `api` ยังเรียกได้ :

```
wget: bad address 'vault'
ok
```

> 📝 ลำดับ argument คือ **network ก่อน container ทีหลัง** (สลับแล้วจะเจอ `network agent not found`) · นี่คือหลักฐานว่า **แต่ละวง network แยกกันจริง ๆ** ไม่ใช่เปิด-ปิดทั้งตัว

---

## การทดลองที่ 9 — `--network none` ตัดขาดจากโลก

**คำถาม:** ไม่มี network เลยหน้าตาเป็นอย่างไร

```bash
docker run --rm --network none busybox:1.36 ip -o addr
docker run --rm --network none busybox:1.36 wget -T 5 -qO- http://1.1.1.1
```

✅ **สิ่งที่ต้องเห็น** — มีแต่ `lo` และออกไปไหนไม่ได้เลย :

```
1: lo    inet 127.0.0.1/8 scope host lo\       valid_lft forever preferred_lft forever
1: lo    inet6 ::1/128 scope host \       valid_lft forever preferred_lft forever

wget: can't connect to remote host (1.1.1.1): Network is unreachable
```

> 📝 `--network none` ไม่ได้แค่ "บล็อกเน็ต" แต่ **ไม่สร้าง `eth0` ให้เลย** — เคอร์เนลจึงตอบทันทีว่า `Network is unreachable` ไม่ต้องรอ timeout · **ใช้จริงเมื่อไร:** งานที่รับ input เป็นไฟล์แล้วประมวลผลอย่างเดียว เช่น แปลงรูป / รัน batch

---

## การทดลองที่ 10 — `--network host` ใช้ network ของเครื่องตรง ๆ

**คำถาม:** host mode ต่างจาก bridge อย่างไร

`web` จองพอร์ต 8186 อยู่ ให้คืนพอร์ตก่อน :

```bash
docker stop web
docker run -d --name host-web --network host -e SERVICE_NAME=host-web netlab-web:1.0
sleep 2
docker ps --filter name=host-web --format 'table {{.Names}}\t{{.Ports}}'
docker port host-web ; echo "^^^ ว่างเปล่าเช่นกัน"
curl -s -m 3 http://localhost:8186/healthz
```

✅ **สิ่งที่ต้องเห็น** — คอลัมน์ `PORTS` **ว่างเปล่า** และไม่มี mapping เลย แต่ curl ได้ `ok` :

```
NAMES      PORTS
host-web   

^^^ ว่างเปล่าเช่นกัน
ok
```

ดูให้ลึกอีกนิด :

```bash
docker inspect -f '{{.HostConfig.NetworkMode}}' host-web
docker inspect -f '{{range $k,$v := .NetworkSettings.Networks}}{{$k}} IP=[{{$v.IPAddress}}]{{end}}' host-web
```

✅ **สิ่งที่ต้องเห็น** — Docker **ไม่ได้แจก IP ให้ container นี้** :

```
host
host IP=[invalid IP]
```

> 📝 **ข้อแลกเปลี่ยน:** host mode เร็วเพราะไม่มีชั้น NAT แต่ **ไม่มี isolation และไม่มี DNS ของชื่อ container** — และ **ชนพอร์ตกับเครื่องได้จริง** (ถ้าไม่ `docker stop web` ก่อน จะเจอ `bind() to 0.0.0.0:8186 failed (98: Address in use)` ใน log) · ใช้ได้เต็มรูปแบบบน **Linux เท่านั้น**

คืนสภาพก่อนไปต่อ :

```bash
docker rm -f host-web
docker start web
```

---

## การทดลองที่ 11 — IP เปลี่ยนได้ แต่ชื่อไม่เปลี่ยน

**คำถาม:** ถ้า container ถูกสร้างใหม่ คนที่จำ IP ไว้จะเป็นอย่างไร

จด IP ปัจจุบันของ `web` ไว้ก่อน :

```bash
docker inspect -f '{{index .NetworkSettings.Networks "app-net" "IPAddress"}}' web
```

✅ **สิ่งที่ต้องเห็น** — `web` ถือ `.2` อยู่ :

```
172.19.0.2
```

ลบ `web` แล้วสร้างใหม่ โดยแทรก container อื่นเข้าไปก่อน (เลียนแบบตอน deploy จริง) :

```bash
docker rm -f web
docker run -d --name filler --network app-net busybox:1.36 sleep 600
docker run -d --name web --network app-net -e SERVICE_NAME=web -p 8186:8186 netlab-web:1.0
sleep 2
docker network inspect -f '{{range .Containers}}{{.Name}} = {{.IPv4Address}}{{println}}{{end}}' app-net
```

✅ **สิ่งที่ต้องเห็น** — `web` ได้ IP **ใหม่** ส่วน `.2` ตอนนี้เป็นของ `filler` :

```
api = 172.19.0.3/16
web = 172.19.0.5/16
agent = 172.19.0.4/16
filler = 172.19.0.2/16
```

ทีนี้เทียบว่า "คนใช้ชื่อ" กับ "คนจำ IP" ใครรอด :

```bash
docker run --rm --network app-net busybox:1.36 wget -qO- http://web/healthz
docker run --rm --network app-net busybox:1.36 wget -qO- http://172.19.0.2/healthz
```

✅ **สิ่งที่ต้องเห็น** — คนใช้ชื่อได้ IP ใหม่อัตโนมัติ ส่วนคน hardcode IP ยิงไปโดน container ผิดตัว :

```
ok
wget: can't connect to remote host (172.19.0.2): Connection refused
```

> 📝 **บทเรียนของแล็บนี้ทั้งแล็บอยู่ตรงนี้:** *อย่า hardcode IP ของ container* — ใช้ **ชื่อ container / ชื่อ service** บน user-defined network เสมอ · Docker แจก IP ที่ **ว่างต่ำสุด** ให้ตัวที่เกิดใหม่ เลขเดิมจึงถูกคนอื่นคว้าไปได้ · ใน `docker compose` ชื่อ service ทำหน้าที่นี้ให้อัตโนมัติ (**LAB 7**)

```bash
docker rm -f filler
```

---

## ตรวจงานด้วย `verify.sh`

รันจากในโฟลเดอร์ของแล็บ **และต้องรันก่อนหัวข้อ Cleanup** :

```bash
cd ~/labwork/DevTools/02_Docker/02_Dockerfile_Build_Run_Compose_Guide/006_LAB_Network_DNS
bash verify.sh ; echo "exit code = $?"
```

✅ **สิ่งที่ต้องเห็น** — 12 ข้อ ผ่านหมด :

```
[PASS] c1 default networks bridge, host, none exist
[PASS] c2 build netlab-web:1.0
[PASS] c3 embedded DNS resolves vfy-web
        ... (c4–c11) ...
[PASS] c12 host mode shares the host network stack (no port mapping)
ALL CHECKS PASSED
exit code = 0
```

> 📝 สคริปต์สร้างของใช้เองชื่อขึ้นต้นด้วย `vfy-` แล้วลบเฉพาะของตัวเองทิ้ง จึงไม่กระทบ `web`/`api`/`app-net` ที่เราสร้างระหว่างทำแล็บ

---

## แก้ปัญหาที่พบบ่อย

| อาการ | สาเหตุ | วิธีแก้ |
|---|---|---|
| `wget: bad address 'web'` | อยู่บน **default bridge** ซึ่งไม่มี DNS ของชื่อ container หรืออยู่คนละ network กับปลายทาง | `docker network create app-net` แล้วใส่ `--network app-net` **ทั้งสองฝั่ง** · ถ้าตัวหนึ่งรันอยู่แล้วใช้ `docker network connect` |
| `nslookup` ตอบ `NXDOMAIN` ทั้งที่ resolver เป็น `127.0.0.11` | อยู่บน user-defined network แล้ว แต่ **คนละวง** กับปลายทาง | `docker network inspect -f '{{range .Containers}}{{.Name}}{{println}}{{end}}' <net>` ดูว่าใครอยู่ในวง |
| `Connection refused` | แปลงชื่อ/IP ได้แล้วแต่ปลายทาง**ไม่มีใครฟัง port นั้น** (มัก hardcode IP ไว้แล้ว IP ย้าย) | เลิกใช้ IP หันมาใช้ชื่อ · เช็กว่าปลายทางรันจริงด้วย `docker logs` |
| `has active endpoints` ตอนลบ network | ยังมี container ต่ออยู่ | `docker rm -f <ชื่อ>` หรือ `docker network disconnect <net> <ชื่อ>` ก่อน |
| `container cannot be connected to multiple networks with one of the networks in private (none) mode` | container เกิดมาด้วย `--network none` | `docker network disconnect none <ชื่อ>` ก่อน แล้วค่อย `connect` |
| container `Up` แต่เว็บไม่ขึ้น + log มี `bind() ... Address in use` | port ชนกัน (มักเกิดกับ `--network host`) | หา/หยุดตัวที่จองอยู่ หรือเปลี่ยนไปใช้ port อื่น |
| `Network is unreachable` | รันด้วย `--network none` จึงไม่มี `eth0` | ถอด `--network none` ออก หรือ `disconnect` แล้ว `connect` เข้า network จริง |
| `template parsing error: bad character U+0022 '"'` | ชื่อ network มีขีดกลาง เลยเขียน `.Networks."app-net"` | ใช้ `{{index .NetworkSettings.Networks "app-net" "IPAddress"}}` แทน |
| เปิด `http://localhost:8186` ไม่ขึ้น | ตอนสร้างกล่องเรียนลืม `-p 8186:8186` | `docker ps` ดูว่ามี `0.0.0.0:8186->8186/tcp` ไหม · ถ้ากล่องเรียนไม่ได้ publish ต้องสร้างกล่องใหม่ |

---

## เก็บกวาด

**ในกล่องเรียน:**

```bash
docker rm -f web api agent vault web-legacy filler host-web 2>/dev/null
docker network rm app-net vault-net
docker network ls
docker rmi netlab-web:1.0
```

✅ `docker network ls` ต้องเหลือ **3 ตัวมาตรฐาน** (`bridge` · `host` · `none`) ซึ่ง **ลบไม่ได้และไม่ต้องลบ**

> 📝 **ต้องลบ container ก่อนลบ network เสมอ** ไม่งั้นเจอ `has active endpoints`

**ออกจากกล่องแล้วลบกล่องบนเครื่องเรา:**

```bash
exit
docker rm -f devtools-df-lab6
docker ps -a --filter "name=^devtools-"
```

---

## สรุปคำสั่งของแล็บนี้

| คำสั่ง | ความหมาย |
|---|---|
| `docker network ls` | ดู network ทั้งหมด — เครื่องใหม่มี `bridge` · `host` · `none` |
| `docker network create app-net` | สร้าง **user-defined bridge** → ได้ DNS ของชื่อ container |
| `docker run --network app-net ...` | ให้ container เกิดบน network ที่เราสร้าง (ต้องใส่ **ทั้งสองฝั่ง**) |
| `docker network inspect -f '{{range .Containers}}...{{end}}' <net>` | ดูว่าใครต่ออยู่และได้ IP อะไร (list/map ต้อง `range`) |
| `docker inspect -f '{{index .NetworkSettings.Networks "app-net" "IPAddress"}}' web` | ดึง IP บน network ที่ชื่อมีขีดกลาง (ต้องใช้ `index`) |
| `docker network connect <net> <container>` | เสียบ network เพิ่มให้ container **ที่กำลังรันอยู่** |
| `docker network disconnect <net> <container>` | ถอด network ออกโดยไม่กระทบขาอื่น |
| `docker run --network none ...` | ตัดขาด network ทั้งหมด เหลือแค่ `lo` |
| `docker run --network host ...` | ใช้ network stack ของเครื่องตรง ๆ ไม่ต้อง `-p` (Linux เท่านั้น) |
| `docker port <container>` | ดูว่า publish port อะไรออก host บ้าง (ไม่ publish = ไม่พิมพ์อะไร) |
| `docker network rm <net>` | ลบ network — ไม่ยอมลบถ้ายังมี **active endpoints** |

> จำสั้น ๆ : **default bridge = ไม่มี DNS** · **user-defined bridge = มี DNS ที่ `127.0.0.11`** · **`-p` มีไว้ให้คนนอกเข้า ไม่ใช่ให้ container คุยกันเอง** · **ชื่ออยู่ยง IP ไม่ยั่งยืน**

## ✅ เช็กลิสต์ก่อนจบแล็บ

- [ ] `docker network ls` เห็นครบ 3 ตัว และอธิบายได้ว่า `bridge` / `host` / `none` ใช้เมื่อไร
- [ ] บน default bridge เรียกด้วยชื่อได้ `bad address` แต่เรียกด้วย IP ได้ `ok`
- [ ] บน `app-net` : `/etc/resolv.conf` ขึ้น `nameserver 127.0.0.11` และ `nslookup web` คืน IP จริง
- [ ] เปิด `http://localhost:8186` แล้วการ์ด **DNS RESOLVER** บนหน้าเว็บขึ้น `127.0.0.11`
- [ ] ใช้ `{{range .Containers}}` และ `{{range .IPAM.Config}}` ได้ และอธิบายได้ว่าทำไมต้อง `range`
- [ ] `api` ไม่มี `-p` เลย แต่เพื่อนใน `app-net` ยังเรียกได้
- [ ] ภารกิจ `vault` : ก่อน connect ได้ `bad address` → หลัง connect ได้ `DOCKER-NET-FLAG{...}` → หลัง disconnect กลับไป `bad address` แต่ `api` ยังเรียกได้
- [ ] `--network none` เห็นแค่ `lo` และได้ `Network is unreachable`
- [ ] `--network host` : `docker port` ว่าง แต่ `curl localhost:8186` ได้ `ok`
- [ ] ลบแล้วสร้าง `web` ใหม่ : IP เปลี่ยน แต่ `http://web` ยังใช้ได้ ส่วน IP เก่ากลายเป็น `Connection refused`
- [ ] `bash verify.sh` ขึ้น `ALL CHECKS PASSED` และเก็บกวาดจน `docker network ls` เหลือ 3 ตัว

*ผลลัพธ์ทั้งหมดในเอกสารนี้มาจากการรันจริงในเครื่องเรียน `tuchsanai/devtools:2569_1`*
