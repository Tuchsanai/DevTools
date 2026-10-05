#!/usr/bin/env bash
# LAB 6: เทียบสูตร desiredReplicas = ceil(currentReplicas × currentUtilization / target) กับที่ HPA สั่งจริง
# ใช้: ./formula.sh [namespace=hpa-demo] [hpa=php-apache]
NS=${1:-hpa-demo}; H=${2:-php-apache}
read -r cur util desired target max <<<"$(kubectl -n "$NS" get hpa "$H" -o jsonpath='{.status.currentReplicas} {.status.currentMetrics[0].resource.current.averageUtilization} {.status.desiredReplicas} {.spec.metrics[0].resource.target.averageUtilization} {.spec.maxReplicas}')"
awk -v c="$cur" -v u="$util" -v d="$desired" -v t="$target" -v m="$max" 'BEGIN {
  r = c * u / t; f = (r == int(r)) ? r : int(r) + 1
  printf "currentReplicas=%d  currentUtilization=%d%%  target=%d%%\n", c, u, t
  printf "สูตร: ceil(%d × %d / %d) = ceil(%.2f) = %d", c, u, t, r, f
  if (f > m) printf "  → เกิน maxReplicas %d จึงได้ %d", m, m
  if (u/t >= 0.9 && u/t <= 1.1) printf "  (อัตราส่วน %.2f อยู่ใน tolerance 10%% → ไม่เปลี่ยน)", u/t
  printf "\nHPA สั่งจริง desiredReplicas=%d\n", d
}'
