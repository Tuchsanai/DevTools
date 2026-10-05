#!/usr/bin/env bash
# LAB 5: เก็บกวาด — ลบ namespace reg/reg2, ปิดคลัง, logout และลบไฟล์รหัสผ่าน
cd "$(dirname "$0")"
kubectl delete ns reg reg2 --ignore-not-found
docker rm -f kind-registry
docker logout localhost:5001
docker rmi localhost:5001/som-menu:1.0 >/dev/null 2>&1 || true
rm -rf auth
