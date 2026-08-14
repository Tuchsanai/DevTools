#!/bin/sh
# app.sh — แอปจำลองที่ "ดักจับ SIGTERM" เพื่อปิดตัวเองอย่างสุภาพ (graceful shutdown)
# ใช้พิสูจน์ว่า exec form กับ shell form ส่งสัญญาณถึงแอปต่างกันอย่างไร

# trap ... TERM = ถ้าได้รับ SIGTERM ให้พิมพ์ข้อความแล้วจบด้วย exit 0 ทันที
trap 'echo "[app] ได้รับ SIGTERM แล้ว - ปิดตัวเองอย่างสุภาพ"; exit 0' TERM

echo "[app] เริ่มทำงานแล้ว PID=$$"

# วนรอไปเรื่อย ๆ : sleep 1 & wait $! ทำให้ shell ตื่นมารับ trap ได้ทันทีที่สัญญาณมาถึง
while true; do
    sleep 1 & wait $!
done
