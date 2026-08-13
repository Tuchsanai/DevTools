# LAB 4 — Network Detective : ภารกิจกู้ข้อความลับ 🕵️ (⏱ ~15–20 นาที)

> โฟลเดอร์ `004_LAB_Docker_Network_DNS` — คู่กับสไลด์ `new_Docker_Week11_Slides.html` Section 4
> แล็บ CLI ล้วน — มีแค่ `README.md` กับ `verify.sh` หลักฐานทั้งหมดอยู่ใน terminal

**เป้าหมาย:** พิสูจน์ว่า default bridge เรียกชื่อกันไม่ได้ · user-defined network แถม **Embedded DNS** ให้ฟรี · เสียบ/ถอด container เข้า network **สด ๆ โดยไม่ restart** · รู้จักโหมด `host` และ `none`

> **ทายก่อนเริ่ม:** โค้ดจริงเขียน `Redis(host="redis")` ทั้งที่ IP ของ container สุ่มใหม่ได้ทุกครั้งที่รัน — ชื่อ `redis` ถูกแปลงเป็น IP ได้ยังไง? ข้อ 3 จะเฉลย

---

## 0. เตรียมเครื่องเรียน

```bash
docker start devtools 2>/dev/null || \
  docker run -dit --name devtools --privileged -p 2222:22 tuchsanai/devtools:2569_1
ssh root@localhost -p 2222        # password : passwd
```

โฟลเดอร์แล็บ (ไว้รัน verify.sh ตอนจบ):

```bash
mkdir -p ~/labwork && cd ~/labwork
git clone https://github.com/Tuchsanai/DevTools.git 2>/dev/null
cd DevTools/03_Docker/04_Docker/004_LAB_Docker_Network_DNS
```

## 1. สำรวจ network ที่ Docker แถมมา

```bash
docker network ls
```

✅ 3 วงตั้งต้น (ลบไม่ได้): `bridge` = วง NAT ส่วนตัว ค่า default · `host` = ใช้ network เครื่องตรง ๆ · `none` = ตัดขาดโลก:

```
NETWORK ID     NAME      DRIVER    SCOPE
b3114e2547c3   bridge    bridge    local
a39fb678ffa4   host      host      local
3dc02e20d892   none      null      local
```

> 📝 `docker network inspect bridge` ดูรายละเอียดได้ — Subnet ในเครื่องเรียนคือ `172.18.0.0/16` (เครื่องเปล่า ๆ มักเป็น `172.17.x.x` — **เลขต่างกันได้ ไม่ใช่ความผิดพลาด**)

## 2. การทดลองที่ 1 : default bridge — IP ได้ แต่ชื่อไม่ได้

```bash
docker run -d --name box1 alpine sleep infinity
docker run -d --name box2 alpine sleep infinity
docker inspect -f '{{.Name}} -> {{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' box1 box2
```

> 📝 `alpine` = Linux จิ๋ว ~3MB · `sleep infinity` ให้ container เปิดค้างไว้ให้ `docker exec` เข้าได้ · ไม่ระบุ `--network` = ตกวง `bridge` อัตโนมัติ

✅ ได้ IP วงเดียวกัน — **จด IP ของ box2 ไว้** (เลขของแต่ละคนไม่ตรงกัน):

```
/box1 -> 172.18.0.2
/box2 -> 172.18.0.3
```

**ยกที่ 1 — ping ด้วย IP** (แทนด้วยค่าจริงของคุณ) แล้ว **ยกที่ 2 — ping ด้วยชื่อ**:

```bash
docker exec box1 ping -c 2 172.18.0.3
docker exec box1 ping -c 2 box2
```

✅ ยกแรก `0% packet loss` — ผ่านสบาย · ยกสอง **ล้มเหลว และนั่นคือผลที่ถูกต้อง**:

```
ping: bad address 'box2'
```

> 📝 **ปัญหาใหญ่:** default bridge ไม่มีบริการแปลชื่อ และ IP สุ่มใหม่ได้ทุกครั้งที่รัน — ฮาร์ดโค้ด IP ลง config คือหายนะ · ข้อถัดไปคือทางออก

## 3. การทดลองที่ 2 : user-defined network — DNS ในตัว

```bash
docker network create --driver bridge --subnet 172.30.0.0/24 lab_net
docker run -d --name box3 --network lab_net alpine sleep infinity
docker run -d --name box4 --network lab_net alpine sleep infinity
docker exec box3 ping -c 2 box4
```

✅ คำสั่งเดียวกับที่เพิ่งพ่ายแพ้ — คราวนี้**สำเร็จด้วยชื่อ!** สังเกตบรรทัดแรก: มีคนแปล `box4` → IP ให้แล้ว:

```
PING box4 (172.30.0.3): 56 data bytes
...
2 packets transmitted, 2 packets received, 0% packet loss
```

ใครแปลชื่อให้? เปิดไฟล์ DNS ใน box3:

```bash
docker exec box3 cat /etc/resolv.conf
```

✅ `nameserver 127.0.0.11` = **Embedded DNS** ที่ Docker ฝังให้ทุก user-defined network — รู้จักชื่อ container ทุกตัวในวง แปลชื่อ → IP ปัจจุบันให้สด ๆ · **นี่คือคำตอบของ `Redis(host="redis")`** และคือสิ่งที่ compose ทำให้อัตโนมัติใน LAB 5

## 4. กำหนด IP ตายตัว (ทำได้เพราะวงเรามี --subnet)

```bash
docker run -d --name box5 --network lab_net --ip 172.30.0.50 alpine sleep infinity
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' box5
```

✅ ตอบ `172.30.0.50` เป๊ะตามสั่ง (ลองกับ default bridge จะโดนปฏิเสธ: `user specified IP address is supported on user defined networks only`)

## 5. ภารกิจกู้ข้อความลับ 🕵️

**โจทย์:** server ลับซ่อนใน `lab_net` (ไม่มี `-p` — โลกภายนอกมองไม่เห็น) ส่วนสายลับเกิดผิดวง — ต้องอ่านข้อความลับให้ได้ **โดยห้าม restart ใคร**

```bash
docker run -d --name secret-server --network lab_net nginx:alpine
docker exec secret-server sh -c 'echo "<h1>ยินดีด้วย! คุณกู้ข้อความลับสำเร็จ 🎉 Embedded DNS ทำงานแล้ว</h1>" > /usr/share/nginx/html/index.html'
docker run -d --name spy alpine sleep infinity
```

**ความพยายามครั้งที่ 1** — ยิงข้ามวง:

```bash
docker exec spy wget -qO- --timeout=3 http://secret-server
```

✅ **ล้มเหลวตามคาด** — `wget: bad address 'secret-server'` (คนละวง = มองไม่เห็นกันโดยสิ้นเชิง)

**อุปกรณ์ลับ** — เสียบสายแลนสด ๆ แล้วยิงซ้ำ:

```bash
docker network connect lab_net spy
docker exec spy wget -qO- http://secret-server
```

✅ **ข้อความลับโผล่มา!** 🎉

```
<h1>ยินดีด้วย! คุณกู้ข้อความลับสำเร็จ 🎉 Embedded DNS ทำงานแล้ว</h1>
```

> 📝 `network connect` เสียบ container **ที่กำลังรันอยู่** เข้าวงเพิ่ม — ไม่มี downtime สักวินาที · ตอนนี้ `spy` มี 2 ขา (ดูได้: `docker inspect -f '{{json .NetworkSettings.Networks}}' spy`)

**พิสูจน์ย้อนกลับ** — ถอดสายแล้วต้องกลับไปมืดบอด:

```bash
docker network disconnect lab_net spy
docker exec spy wget -qO- --timeout=3 http://secret-server
```

✅ กลับไป `bad address` เหมือนเดิม — network คือตัวแปรจริง ไม่ใช่ความบังเอิญ

## 6. โหมดพิเศษ : host และ none

```bash
docker run -d --name hostnginx --network host nginx:alpine
curl -s localhost:80 | grep -o "<title>.*</title>"
docker run --rm --network none alpine ip addr
```

✅ `host`: เจอ `<title>Welcome to nginx!</title>` **โดยไม่มี `-p` เลย** — container ใช้ network เครื่องตรง ๆ (เร็ว แต่เสีย isolation) · `none`: มีแค่ `lo` ไม่มี `eth0` — ตัดขาดโลก เหมาะกับงานห้ามออกเน็ต

## 7. ตรวจงานด้วย verify.sh

รันจากโฟลเดอร์แล็บ **ก่อน** ล้างกระดาน (verify จะเล่นภารกิจ spy ซ้ำให้อัตโนมัติ):

```bash
bash verify.sh
```

✅ ทุกข้อ `PASS` จบด้วย `ALL CHECKS PASSED` (exit 0)

## 8. ล้างกระดาน

```bash
docker rm -f box1 box2 box3 box4 box5 secret-server spy hostnginx
docker network rm lab_net
docker ps -a && docker network ls
```

✅ ลำดับสำคัญ: **ลบ container ก่อน network** (ไม่งั้นเจอ `has active endpoints`) · จบแล้ว container ว่าง network เหลือ 3 วงตั้งต้น

---

## ปัญหาที่พบบ่อย

| อาการ | สาเหตุ | วิธีแก้ |
|---|---|---|
| `ping: bad address 'box2'` ในข้อ 2 | **ไม่ใช่ความผิดพลาด** — default bridge ไม่มี DNS | นี่คือผลการทดลองที่ถูกต้อง อ่านต่อข้อ 3 |
| `bad address` ทั้งที่อยู่ `lab_net` แล้ว | พิมพ์ชื่อผิด หรือปลายทางไม่ได้อยู่วงเดียวกันจริง | `docker network inspect lab_net` ดูรายชื่อสมาชิกใน `Containers` |
| `network rm` ฟ้อง `has active endpoints` | ยังมี container เสียบอยู่ในวง | `docker rm -f` สมาชิกให้หมดก่อน แล้วค่อย `network rm` |

*ผลลัพธ์ทั้งหมดมาจากการรันจริงในเครื่องเรียน `tuchsanai/devtools:2569_1` — เลขวง IP ของแต่ละเครื่องต่างกันได้*
