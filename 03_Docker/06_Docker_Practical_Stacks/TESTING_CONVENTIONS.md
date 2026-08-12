# Testing Conventions

เอกสารนี้ใช้โดยผู้เขียนและผู้ตรวจชุด LAB เพื่อให้การทดลองซ้ำได้โดยไม่ชนงานอื่น

## Outer container

- ต้องชื่อ `devtools-<experiment>` ตามตารางใน `readme.md`
- ใช้ `--privileged` เพราะ image เป็นเครื่องเรียน Docker-in-Docker
- ใช้ SSH host port ไม่ซ้ำ
- ถ้าต้อง capture web ให้ map host → inner port เพิ่มตั้งแต่ `docker run`
- รอ `docker info` สำเร็จก่อนเริ่ม workload ภายใน

## Inner resource names

- container/image/network/volume/Compose project ต้องขึ้นต้นด้วย `labN-`
- ห้าม cleanup แบบ global (`prune`, `docker rm $(docker ps -aq)`)
- Compose ต้องใช้ `-p labN` หรือกำหนด `name: labN` เพื่อให้ scope แน่นอน

## Browser evidence

ใช้ Playwright CLI เท่านั้นสำหรับหน้าเว็บจริง:

```bash
npx playwright screenshot \
  --browser chromium \
  --viewport-size "1280, 800" \
  --wait-for-timeout 1000 \
  http://127.0.0.1:<HOST_PORT> \
  images/<evidence-name>.png
```

ก่อน capture ต้องทดสอบ HTTP status ด้วย `curl -fsS` และหลัง capture ต้องตรวจขนาด/เปิดดูภาพ

## Transcript hygiene

- ไม่บันทึกคำสั่ง login ที่มี token ลง transcript
- redact digest/ID ไม่จำเป็น แต่ต้องระบุว่าเป็นค่า dynamic
- password ใน classroom `.env.example` ต้องเป็น placeholder เช่น `change-me-for-lab`
- validation ต้องระบุวันที่, image เครื่องเรียน, Docker/Compose version และ cleanup result

## Final cleanup

1. ลบ resource ของ LAB ภายในด้วยชื่อเฉพาะ
2. ออกจาก outer container
3. `docker rm -fv devtools-<experiment>`
4. ตรวจ filter ชื่อของตัวเองให้ว่าง
5. ห้ามลบ container ที่ไม่ขึ้นต้นด้วยชื่อของการทดลอง

