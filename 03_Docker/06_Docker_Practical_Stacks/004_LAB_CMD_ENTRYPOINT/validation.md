# Validation — LAB 4 CMD vs ENTRYPOINT

วันที่ทดสอบ: 12 สิงหาคม 2026 (UTC)  
สถานะ: **PASS**

## Environment ที่ใช้จริง

- Outer image: `tuchsanai/devtools:2569_1`
- Outer container: `devtools-cmd-entrypoint`
- SSH mapping: `2225:22`
- Docker Engine ภายใน: `29.6.2`
- Docker Compose ภายใน: `v5.3.1`
- Base image ของตัวอย่าง: `alpine:3.20`

Outer container รันด้วย `--privileged` และประกาศ bind mount course path ไป `/course` ตามโจทย์ ใน runner นี้ Docker daemon อยู่คนละ filesystem namespace กับ workspace จึงเห็น source bind mount เป็นโฟลเดอร์ว่าง ผู้ตรวจจึงใช้ `docker cp` ส่ง **สำเนาเฉพาะ LAB 4** เข้า destination `/course` เพื่อรันทดสอบ ไม่มีการเปลี่ยน source หรือใช้วิธีนี้เป็นคำสั่งหลักในเอกสารนักศึกษา

## สิ่งที่ตรวจ

1. Build image ทั้งสามแบบสำเร็จ
2. CMD default และ CMD override ให้ผลตรง matrix
3. ENTRYPOINT รับ CLI arguments ต่อท้าย
4. ENTRYPOINT + CMD ใช้ CMD เป็น default arguments
5. CLI arguments แทน CMD แต่ไม่แทน ENTRYPOINT
6. `--entrypoint` แทน executable หลักได้
7. inspect แสดง `Entrypoint`/`Cmd` ตรง Dockerfile
8. invalid CMD override คืน status `127` และ error `executable file not found`
9. ไม่มี inner container ค้างหลัง validation

ผลแบบ sanitized อยู่ที่ [`evidence/validation-output.txt`](./evidence/validation-output.txt)

## Cleanup ที่ยืนยันแล้ว

```text
docker rm -fv devtools-cmd-entrypoint
docker ps -a --filter name=^/devtools-cmd-entrypoint$
```

ผลตรวจสุดท้ายว่างเปล่า: ไม่มี outer container และ anonymous Docker-in-Docker volume ถูกลบพร้อม `-v`
