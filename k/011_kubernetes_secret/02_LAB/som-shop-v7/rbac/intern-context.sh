#!/usr/bin/env bash
# LAB 9 ขั้น A: ทำ "บัตรพนักงาน" ให้ intern ใน kubeconfig → ใช้ kubectl --context intern ได้เหมือนล็อกอินเป็น intern จริง
#   token ได้จาก kubectl create token (มีอายุ — ค่าเริ่ม 24h) ไม่ใช้ Secret แบบ service-account-token ที่ไม่มีวันหมดอายุ
#   token หมดอายุแล้วรันสคริปต์นี้ซ้ำได้
# ใช้:  ./rbac/intern-context.sh [อายุ token]   เช่น ./rbac/intern-context.sh 2h
DUR=${1:-24h}
TOKEN=$(kubectl -n som-shop create token intern --duration="$DUR") || exit 1
kubectl config set-credentials intern --token="$TOKEN" >/dev/null
kubectl config set-context intern --cluster=kind-lab --user=intern --namespace=som-shop
echo "ใช้: kubectl --context intern get pods   (token อายุ $DUR — ห้ามแชร์ token)"
