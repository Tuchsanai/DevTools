# LAB 4 — `CMD` vs `ENTRYPOINT`

> แล็บนี้สร้าง image ขนาดเล็ก 3 แบบ แล้วทดลอง override ให้ครบทุกกรณี เพื่อให้เห็นจากผลรันจริงว่า Docker ประกอบ “โปรแกรมหลัก” กับ “ค่าเริ่มต้น” อย่างไร

## สิ่งที่จะได้เรียนรู้

- อธิบายหน้าที่ของ `CMD` และ `ENTRYPOINT` โดยไม่จำเพียงคำแปล
- ทำนายผลของ argument ที่ต่อท้าย `docker run <image> ...`
- ใช้ `ENTRYPOINT` และ `CMD` ร่วมกันในรูปแบบ “โปรแกรมคงที่ + argument เริ่มต้น”
- override `ENTRYPOINT` ด้วย `--entrypoint`
- ตรวจค่าจริงที่บันทึกอยู่ใน image ด้วย `docker image inspect`
- แยก error “หา executable ไม่พบ” ออกจาก error ที่เกิดระหว่างโปรแกรมทำงาน

## ภาพรวมของแล็บ

1. เปิดเครื่องเรียน `devtools-cmd-entrypoint` ที่ SSH port `2225`
2. อ่าน Dockerfile ทั้งสามแบบก่อน build
3. build image `lab4-cmd:1.0`, `lab4-entrypoint:1.0`, `lab4-both:1.0`
4. ทดลองค่า default และการ override ทีละกรณี
5. ตั้งใจสั่ง CMD override ผิด เพื่ออ่าน error ให้เป็น
6. inspect ค่า `Entrypoint` และ `Cmd` ใน image
7. รัน validation script เพื่อตรวจ matrix ทั้งชุด
8. ลบ workload และ outer container

## Mental model ก่อนเริ่ม

| Dockerfile | สิ่งที่ Docker จำ | argument หลังชื่อ image |
|---|---|---|
| มี `CMD` อย่างเดียว | default command | แทน `CMD` ทั้งชุด |
| มี `ENTRYPOINT` อย่างเดียว | executable หลัก | ต่อท้าย `ENTRYPOINT` |
| มีทั้งสอง | `ENTRYPOINT` = executable, `CMD` = default arguments | แทนเฉพาะ `CMD` |

แล็บนี้ใช้ **exec form** เช่น `CMD ["/bin/echo", "CMD default"]` เพื่อให้เห็น array แยกเป็นคำชัดเจน และหลีกเลี่ยง shell ที่เข้ามาเป็น process กลาง

## 0. เปิดเครื่องเรียน

สั่งบนเครื่อง host:

```bash
docker rm -fv devtools-cmd-entrypoint 2>/dev/null
docker run -dit \
  --name devtools-cmd-entrypoint \
  --privileged \
  -p 2225:22 \
  -v /home/workspace/DevTools/03_Docker/06_Docker_Practical_Stacks:/course \
  tuchsanai/devtools:2569_1
ssh root@localhost -p 2225
```

**password:** `passwd`

> 📝 **คำอธิบาย:** `--privileged` ทำให้รัน Docker ซ้อนในเครื่องเรียนได้ ส่วน mount `/course` ทำให้ใช้ไฟล์แล็บจาก host โดยไม่ต้อง clone ซ้ำ `-p 2225:22` เป็น SSH port ของ LAB 4 โดยเฉพาะ

เข้าเครื่องเรียนแล้วตรวจสอบ:

```bash
docker --version
docker compose version
cd /course/004_LAB_CMD_ENTRYPOINT
pwd
```

✅ **Expected output:** สองคำสั่งแรกขึ้นเลขเวอร์ชัน และ `pwd` ลงท้ายด้วย `/004_LAB_CMD_ENTRYPOINT`

ถ้าเห็น `Cannot connect to the Docker daemon` ให้รอสักครู่แล้วลองใหม่ ห้ามสั่ง Docker ของ workload ผิดชั้นบน host

## 1. อ่าน Dockerfile ทั้งสามแบบ

### 1.1 CMD only

```dockerfile
FROM alpine:3.20
CMD ["/bin/echo", "CMD default"]
```

`CMD` เป็นคำสั่งเริ่มต้น หากผู้ใช้ไม่ต่อคำสั่งใหม่ Docker จะรัน `/bin/echo` พร้อม argument `CMD default`

### 1.2 ENTRYPOINT only

```dockerfile
FROM alpine:3.20
ENTRYPOINT ["/bin/echo"]
```

`/bin/echo` ถูกยึดเป็น executable หลัก สิ่งที่ต่อท้ายชื่อ image จะกลายเป็น argument ของ `echo`

### 1.3 ENTRYPOINT + CMD

```dockerfile
FROM alpine:3.20
ENTRYPOINT ["/bin/echo", "ENTRYPOINT:"]
CMD ["CMD default"]
```

เมื่อนำมารวมกัน คำสั่ง default คือ:

```text
/bin/echo ENTRYPOINT: "CMD default"
```

## 2. Build image

```bash
docker build -t lab4-cmd:1.0 ./cmd-only
docker build -t lab4-entrypoint:1.0 ./entrypoint-only
docker build -t lab4-both:1.0 ./both
docker images --filter reference='lab4-*'
```

> 📝 **คำอธิบาย:** แต่ละคำสั่งใช้คนละ build context จึงอ่าน Dockerfile คนละไฟล์ `-t` ตั้งชื่อและ version tag ให้เรียกซ้ำได้ง่าย

✅ **Expected output:** เห็น image ทั้งสามชื่อและ build จบโดยไม่มี error เลข IMAGE ID และขนาดอาจต่างจากเอกสาร

## 3. ทดลอง `CMD` อย่างเดียว

```bash
docker run --rm lab4-cmd:1.0
docker run --rm lab4-cmd:1.0 /bin/echo "CMD override"
```

✅ **Expected output:**

```text
CMD default
CMD override
```

> บรรทัดที่สองไม่ได้ส่งคำว่า `CMD override` เข้า `echo` เดิม แต่แทน array ของ `CMD` ทั้งชุดด้วย `/bin/echo "CMD override"`

### ทดลองกรณีผิด

```bash
docker run --rm lab4-cmd:1.0 hello
echo $?
```

✅ **Expected output:** Docker พยายามใช้ `hello` เป็น executable แล้วแจ้งประมาณ `executable file not found` พร้อม exit code `127` คำ error อาจต่างเล็กน้อยตาม Docker runtime

## 4. ทดลอง `ENTRYPOINT` อย่างเดียว

```bash
docker run --rm lab4-entrypoint:1.0
docker run --rm lab4-entrypoint:1.0 hello Docker
```

✅ **Expected output:** คำสั่งแรกได้บรรทัดว่างจาก `echo` ที่ไม่มี argument และคำสั่งที่สองได้:

```text
hello Docker
```

## 5. ทดลองใช้ร่วมกัน

```bash
docker run --rm lab4-both:1.0
docker run --rm lab4-both:1.0 custom
```

✅ **Expected output:**

```text
ENTRYPOINT: CMD default
ENTRYPOINT: custom
```

`custom` แทน `CMD` แต่ไม่แทน `ENTRYPOINT` จึงยังมี prefix `ENTRYPOINT:` อยู่

## 6. Override ENTRYPOINT โดยตรง

```bash
docker run --rm \
  --entrypoint /bin/sh \
  lab4-both:1.0 \
  -c 'echo entrypoint replaced'
```

✅ **Expected output:**

```text
entrypoint replaced
```

> 📝 **คำอธิบาย:** `--entrypoint` ต้องอยู่ก่อนชื่อ image ส่วน `-c ...` อยู่หลังชื่อ image และจึงถูกส่งให้ `/bin/sh`

## 7. Inspect ค่าที่ image จำไว้

```bash
docker image inspect lab4-cmd:1.0 \
  --format 'Entrypoint={{json .Config.Entrypoint}} Cmd={{json .Config.Cmd}}'
docker image inspect lab4-entrypoint:1.0 \
  --format 'Entrypoint={{json .Config.Entrypoint}} Cmd={{json .Config.Cmd}}'
docker image inspect lab4-both:1.0 \
  --format 'Entrypoint={{json .Config.Entrypoint}} Cmd={{json .Config.Cmd}}'
```

✅ **Expected output:**

```text
Entrypoint=null Cmd=["/bin/echo","CMD default"]
Entrypoint=["/bin/echo"] Cmd=null
Entrypoint=["/bin/echo","ENTRYPOINT:"] Cmd=["CMD default"]
```

นี่คือหลักฐานจาก metadata ของ image โดยตรง ไม่ได้อนุมานจากข้อความที่ `echo` พิมพ์

## 8. Validation อัตโนมัติ

```bash
chmod +x validate.sh
./validate.sh
```

✅ **Expected output:** มี `PASS` ครบ 7 กรณี และบรรทัดสุดท้ายเป็น:

```text
ALL LAB 4 CHECKS PASSED
```

## Common errors

| อาการ | สาเหตุ | วิธีตรวจ/แก้ |
|---|---|---|
| `executable file not found` | CMD ถูกแทนด้วยคำที่ไม่ใช่โปรแกรม | ระบุ executable เช่น `/bin/echo` |
| ผลยังมี prefix | CLI argument แทน CMD แต่ ENTRYPOINT ยังอยู่ | ใช้ `--entrypoint` หากตั้งใจแทนจริง |
| `unknown flag` | วาง `--entrypoint` หลังชื่อ image | ย้าย option ไว้ก่อน image |
| quote กลายเป็นส่วนหนึ่งของ argument | สับสน shell form กับ exec form | ใช้ JSON double quotes ที่ถูกต้อง |
| มี container ค้าง | ลืม `--rm` | ตรวจ `docker ps -a` และลบเฉพาะของ LAB 4 |

## สรุปคำสั่ง

```bash
docker build -t <image>:<tag> <context>
docker run --rm <image>
docker run --rm <image> <replacement-cmd-or-arguments>
docker run --rm --entrypoint <program> <image> <arguments>
docker image inspect <image> --format '...'
```

## เก็บกวาด

ภายในเครื่องเรียน:

```bash
docker ps -aq --filter ancestor=lab4-cmd:1.0
docker ps -aq --filter ancestor=lab4-entrypoint:1.0
docker ps -aq --filter ancestor=lab4-both:1.0
docker image rm lab4-cmd:1.0 lab4-entrypoint:1.0 lab4-both:1.0
exit
```

จากนั้นสั่งบน host:

```bash
docker rm -fv devtools-cmd-entrypoint
docker ps -a --filter 'name=^devtools-cmd-entrypoint$'
```

✅ ผลสุดท้ายต้องเหลือเพียงหัวตาราง ไม่มี outer container ค้าง `-v` ลบ anonymous volume ของ Docker-in-Docker ไปพร้อมกัน

## ✅ เช็กลิสต์ก่อนจบแล็บ

- [ ] Build image ครบสามแบบ
- [ ] CMD default ได้ `CMD default`
- [ ] Override CMD ได้ `CMD override`
- [ ] ENTRYPOINT รับ argument เป็น `hello Docker`
- [ ] แบบใช้ร่วมกันได้ `ENTRYPOINT: CMD default`
- [ ] CLI argument แทนเฉพาะ CMD แล้วได้ `ENTRYPOINT: custom`
- [ ] `--entrypoint` ทำให้ prefix เดิมหายไป
- [ ] inspect แสดง array ตรง Dockerfile
- [ ] `validate.sh` จบด้วย `ALL LAB 4 CHECKS PASSED`
- [ ] ลบ `devtools-cmd-entrypoint` ด้วย `docker rm -fv` แล้ว

ผลการทดสอบจริงและ output ที่ตัดข้อมูลแปรผันออกอยู่ใน [`validation.md`](./validation.md) และ [`evidence/validation-output.txt`](./evidence/validation-output.txt)
