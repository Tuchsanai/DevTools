# ตัวอย่าง README สำหรับทดสอบ runner

<!-- run -->
```bash
test "$(printf ok)" = ok
```

<!-- bg -->
```bash
while :; do sleep 1; done
```

<!-- expect-fail:7 -->
```bash
exit 7
```

<!-- skip-auto ต้องเปิด tunnel แบบ interactive -->
```bash
ssh -L 8000:localhost:8000 example.invalid
```
