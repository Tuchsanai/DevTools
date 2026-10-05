#!/usr/bin/env bash
# LAB 9 ข: ตั้ง requests.cpu ของ php-apache = 60% ของ CPU ที่ Node worker รับจองได้ (allocatable)
#   → 1 Node วางได้แค่ 1 Pod (2 ตัว = 120% เกิน) → worker 2 ลำ = Running 2 ที่เหลือ Pending
# allocatable อาจเป็นเลข core ("4", "8") หรือหน่วย m ("7800m") — แปลงเป็น m ก่อนคิด
# ใช้: ./lab09-limits/big-requests.sh        คืนค่า: kubectl -n hpa-demo set resources deploy php-apache --requests=cpu=100m --limits=cpu=300m
A=$(kubectl get node lab-worker -o jsonpath='{.status.allocatable.cpu}')
case $A in *m) M=${A%m};; *) M=$((A * 1000));; esac
R=$((M * 60 / 100))
echo "allocatable ของ lab-worker = $A → requests = 60% = ${R}m"
kubectl -n hpa-demo set resources deploy php-apache --requests=cpu=${R}m --limits=cpu=${R}m
