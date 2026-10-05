#!/usr/bin/env bash
# LAB 6: แก้ shop-config แล้วจับเวลาว่าไฟล์ใน volume เปลี่ยนเมื่อไร (ต้องมี envpod จาก LAB 2 และ volpod จาก LAB 5)
#   volume (/etc/all)  → kubelet (หุ่นยนต์ลูกเรือ) มาอัปเดตให้เอง ราว 1 นาที
#   subPath (/etc/som) → ไม่อัปเดต
#   env (envpod)       → ไม่อัปเดต (อ่านครั้งเดียวตอน container เริ่ม)
# ใช้:  ./watch.sh [จำนวนรอบ]   (ค่าเริ่ม 3 รอบ รอบละ ~1–1.5 นาที)
ROUNDS=${1:-3}
for r in $(seq "$ROUNDS"); do
  v="ปลาทูรอบ$r"
  # แก้ 2 key พร้อมกัน: ไฟล์ประกาศ และชื่อร้าน
  kubectl patch cm shop-config --type merge \
    -p "{\"data\":{\"announcement.txt\":\"$v\n\",\"SHOP_NAME\":\"ร้านใหม่$r\"}}" >/dev/null
  echo "รอบ $r: $(date +%T) patch shop-config → announcement.txt=$v, SHOP_NAME=ร้านใหม่$r"
  t0=$(date +%s)
  while :; do
    out=$(kubectl exec volpod -- cat /etc/all/announcement.txt 2>/dev/null)
    [ "$out" = "$v" ] && break
    [ $(( $(date +%s) - t0 )) -gt 180 ] && { echo "  เกิน 180 วินาทีแล้วยังไม่เปลี่ยน"; break; }
    sleep 1
  done
  echo "  volume /etc/all/announcement.txt เปลี่ยนหลัง $(( $(date +%s) - t0 )) วินาที: $out"
  echo "  volume /etc/all/SHOP_NAME             : $(kubectl exec volpod -- cat /etc/all/SHOP_NAME)"
  echo "  subPath /etc/som/announcement.txt     : $(kubectl exec volpod -- cat /etc/som/announcement.txt)"
  echo "  env SHOP_NAME ใน envpod               : $(kubectl exec envpod -- printenv SHOP_NAME)"
  sleep 5
done
echo "--- ..data ชี้ไปโฟลเดอร์เวลาใหม่:"
kubectl exec volpod -- ls -la /etc/all | grep -E '(\.\.data|announcement\.txt) ->'
