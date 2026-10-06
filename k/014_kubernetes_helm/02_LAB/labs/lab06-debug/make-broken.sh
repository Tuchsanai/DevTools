#!/usr/bin/env bash
# LAB 6: คัดลอก mychart จาก LAB 5 แล้วทำ "แม่พิมพ์พัง" 4 แบบ (โฟลเดอร์ละ 1 แบบ) ให้ฝึกหาจุดผิด
# ใช้: bash make-broken.sh   (รันซ้ำได้ — ลบโฟลเดอร์ broken-* เดิมก่อน)
set -e
cd "$(dirname "$0")"
SRC=../lab05-first/mychart
[ -d "$SRC" ] || { echo "ยังไม่มี $SRC — ทำ LAB 5 ก่อน"; exit 1; }
rm -rf broken-indent broken-func broken-required broken-v3

# 1) ใช้ indent แทน nindent ที่บรรทัด podLabels + เปิด podLabels ให้มีค่า → YAML เยื้องผิด
cp -r "$SRC" broken-indent
sed -i '/with .Values.podLabels/{n;s/nindent 8/indent 2/}' broken-indent/templates/deployment.yaml
sed -i 's/^podLabels: {}/podLabels: {shop: som}/' broken-indent/values.yaml

# 2) พิมพ์ชื่อฟังก์ชันผิด toYaml → toYml
cp -r "$SRC" broken-func
sed -i 's/toYaml/toYml/' broken-func/templates/deployment.yaml

# 3) บังคับให้ต้องมี image.repository ด้วย required
cp -r "$SRC" broken-required
sed -i 's|{{ .Values.image.repository }}|{{ required "ต้องใส่ image.repository" .Values.image.repository }}|' broken-required/templates/deployment.yaml

# 4) chart apiVersion v3 (Helm 4.3 ยังไม่รองรับ)
cp -r "$SRC" broken-v3
sed -i 's/^apiVersion: v2/apiVersion: v3/' broken-v3/Chart.yaml

for d in broken-indent broken-func broken-required broken-v3; do
  echo "=== $d (บรรทัดที่ต่างจาก mychart)"
  diff -r "$SRC" "$d" | grep '^>' | head -3 || true
done
