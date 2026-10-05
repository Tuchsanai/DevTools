#!/usr/bin/env bash
# LAB 10 ขั้น D: จับเวลาว่าประกาศใหม่ไปถึงหน้าร้านเมื่อไร (ไม่ต้อง restart Pod)
# วนเรียก /api/announcement ทุก 2 วินาที → บอกเวลาที่ Pod แรกเห็นข้อความใหม่ และเวลาที่ "ทุก Pod" เห็น (ยิงติดกัน 12 ครั้งได้ข้อความใหม่หมด)
# ใช้:  ./wait-announcement.sh <คำในประกาศใหม่> [URL]
#   เช่น ./wait-announcement.sh 18:00
WORD=${1:?ใส่คำที่อยู่ในประกาศใหม่ เช่น 18:00}
URL=${2:-http://localhost:30080/api/announcement}
t0=$(date +%s); first=""
echo "เริ่ม $(date +%T) รอคำว่า \"$WORD\" จาก $URL"
while :; do
  n=0; last=""
  for i in $(seq 12); do
    out=$(curl -s -m 2 "$URL")
    case "$out" in *"$WORD"*) n=$((n + 1)); last=$out;; esac
  done
  now=$(( $(date +%s) - t0 ))
  if [ $n -gt 0 ] && [ -z "$first" ]; then first=$now; echo "  Pod แรกเห็นประกาศใหม่หลัง ${now} วินาที: $last"; fi
  if [ $n -eq 12 ]; then echo "  ทุก Pod เห็นประกาศใหม่ (12/12) หลัง ${now} วินาที"; break; fi
  [ $now -gt 240 ] && { echo "  เกิน 240 วินาที ยังเห็นแค่ $n/12"; break; }
  sleep 2
done
