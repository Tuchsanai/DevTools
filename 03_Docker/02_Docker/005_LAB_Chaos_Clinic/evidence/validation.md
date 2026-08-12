# Validation evidence

ทดสอบจริงวันที่ 2026-08-12 ด้วย Docker Compose และ Playwright CLI

```text
initial: status=running health=unhealthy uid=app restarts=0
HTTP /health = 503, reason="HEALTH_MODE must be ready"
readonly=true caps=["ALL"] security=["no-new-privileges:true"]

after recreate: status=running health=healthy
HEALTH_MODE=ready RELEASE=stable

after /crash: status=running health=starting restart_count=1
structured log: startup → request /crash → startup
```

ภาพ: `images/actual-unhealthy.png`, `images/actual-healthy.png`

พบและแยกข้อจำกัดของ topology: การใส่ CPU/memory controller บน nested daemon ของ host นี้ล้มด้วย `cannot enter cgroupv2 ... threaded mode` จึงย้าย resource limits ไป `compose.resources.yaml` สำหรับ Docker บน host โดยตรง ส่วน LAB หลักยังคงตรวจ hardening และ observability ได้ครบ

