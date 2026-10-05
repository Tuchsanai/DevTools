#!/usr/bin/env bash
# LAB 3: แก้ password ใน Secret demo แล้วจับเวลาว่าไฟล์ใน volume ของ spod เปลี่ยนเมื่อไร
#   volume (/etc/secret/password) → kubelet อัปเดตให้เอง (ราว 1 นาที)
#   env DB_PASSWORD               → ไม่เปลี่ยน (อ่านครั้งเดียวตอน container เริ่ม)
# ใช้:  ./wait-secret.sh [รหัสใหม่]   (ค่าเริ่ม newpass-01)
NEW=${1:-newpass-01}
kubectl patch secret demo --type merge -p "{\"stringData\":{\"password\":\"$NEW\"}}"
echo "$(date +%T) patch secret demo → password=$NEW"
t0=$(date +%s)
while :; do
  out=$(kubectl exec spod -- cat /etc/secret/password 2>/dev/null)
  [ "$out" = "$NEW" ] && break
  [ $(( $(date +%s) - t0 )) -gt 180 ] && { echo "  เกิน 180 วินาทีแล้วยังไม่เปลี่ยน"; break; }
  sleep 1
done
echo "  ไฟล์ /etc/secret/password เปลี่ยนหลัง $(( $(date +%s) - t0 )) วินาที: $out"
echo "  ไฟล์ /etc/secret400/password       : $(kubectl exec spod -- cat /etc/secret400/password)"
echo "  env DB_PASSWORD (ไม่เปลี่ยน)        : $(kubectl exec spod -- printenv DB_PASSWORD)"
