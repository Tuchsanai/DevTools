# Validation evidence

ทดสอบจริงวันที่ 2026-08-12 ด้วย `tuchsanai/devtools:2569_1` และ Playwright CLI

```text
SSH_OK
Docker version 29.6.2
HTTP/1.1 200 OK
Server: nginx/1.29.8
name=devtools-lab1-nginx status=Up ports=0.0.0.0:8080->80/tcp
mount_rw=false
same_id=yes status=running
```

ภาพ: `images/actual-container-detective.png`

หมายเหตุจากสภาพแวดล้อมทดสอบ: host นี้เข้าถึง outer container ผ่าน bridge IP โดยตรง เพราะ localhost port publishing ของ outer Docker daemon ไม่ถูกส่งกลับมาที่ execution namespace; เส้นทางที่ผู้เรียนใช้ยังคงเป็น `http://localhost:18081`

