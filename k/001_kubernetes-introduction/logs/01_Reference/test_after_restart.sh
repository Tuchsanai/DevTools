#!/bin/bash
# ตรวจสถานะคลัสเตอร์หลัง container restart / ถูกสร้างใหม่ด้วย volume เดิม
set -u
for i in $(seq 90); do docker info >/dev/null 2>&1 && break; sleep 1; done
echo "dockerd ready"
grep -h 'cgroup v2 controllers' /proc/1/fd/1 2>/dev/null | head -1
echo "kind clusters: $(kind get clusters 2>&1 | tr '\n' ' ')"
docker ps -a --format '{{.Names}} {{.Status}}'
echo "--- kubeconfig: $(ls /root/.kube/config 2>&1)"
for i in $(seq 60); do kubectl get nodes >/dev/null 2>&1 && break; sleep 2; done
kubectl get nodes 2>&1 | head -5
kubectl get pods -A --no-headers 2>&1 | awk '{print $4}' | sort | uniq -c
curl -s -o /dev/null -w 'curl 30080 -> %{http_code}\n' --max-time 5 http://localhost:30080
