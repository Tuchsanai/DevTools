#!/usr/bin/env bash
# LAB 8: อ่านค่าดิบจาก etcd (อ่านอย่างเดียว) ผ่าน etcdctl ใน Pod etcd-lab-control-plane
# ใช้:  ./etcdget.sh <key>     เช่น ./etcdget.sh /registry/secrets/default/demo
#       ./etcdget.sh --keys <prefix>   แสดงแค่ชื่อ key เช่น ./etcdget.sh --keys /registry/secrets/default/
# ผลเป็น protobuf (มีอักขระไบนารี) → ส่งต่อให้ grep -a หรือ cat -v
if [ "$1" = "--keys" ]; then shift; set -- "$1" --prefix --keys-only; fi
kubectl -n kube-system exec etcd-lab-control-plane -- etcdctl \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key \
  get "$@"
