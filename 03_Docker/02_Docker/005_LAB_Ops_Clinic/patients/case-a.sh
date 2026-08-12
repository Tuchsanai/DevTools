#!/bin/sh
# คนไข้ A — "ตายทันทีที่เกิด"
# process หลักจบทันที (exit 1) → container ตายตาม เพราะ container มีชีวิตเท่ากับ PID 1
docker rm -f patient-a >/dev/null 2>&1
docker run -d --name patient-a alpine:3.21 sh -c 'echo "boot: reading /etc/app.conf"; echo "FATAL: config not found" >&2; exit 1'
