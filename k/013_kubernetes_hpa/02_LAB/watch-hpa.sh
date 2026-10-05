#!/usr/bin/env bash
# พิมพ์ "วินาทีที่ผ่านไป  TARGETS  REPLICAS(ที่ HPA สั่ง)  ready(Pod พร้อมจริง)" ทุก 5 วิ
# (kubectl get hpa -w พิมพ์เฉพาะตอนค่าเปลี่ยน และไม่บอกเวลา)
# ใช้: ./watch-hpa.sh <namespace> <hpa> [วินาทีรวม=600]
NS=$1; H=$2; T=${3:-600}; t0=$(date +%s)
D=$(kubectl -n "$NS" get hpa "$H" -o jsonpath='{.spec.scaleTargetRef.name}')
while [ $(( $(date +%s) - t0 )) -le "$T" ]; do
  # TARGETS อาจมีหลาย metric คั่นด้วย ", " (LAB 8) → เอาคอลัมน์ที่ 3 ถึงก่อน MINPODS ทั้งหมด
  row=$(kubectl -n "$NS" get hpa "$H" --no-headers 2>&1 | awk '{t=$3; for (i=4; i<=NF-4; i++) t=t " " $i; sub(/^cpu: /, "", t); print t, "replicas=" $(NF-1)}')
  ready=$(kubectl -n "$NS" get deploy "$D" -o jsonpath='{.status.readyReplicas}')
  printf '%4ss  %s ready=%s\n' $(( $(date +%s) - t0 )) "$row" "${ready:-0}"
  sleep 5
done
