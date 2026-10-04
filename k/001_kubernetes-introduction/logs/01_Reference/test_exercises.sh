#!/bin/bash
# ทดสอบแบบฝึกหัดท้าย LAB (ข้อ 1,2,3,5) ตามคำสั่งเฉลยใน readme
set -u
step() { echo; echo "===== $* ====="; }
for i in $(seq 90); do docker info >/dev/null 2>&1 && break; sleep 1; done
k8s-up >/dev/null 2>&1 && echo "k8s-up ok"
kubectl apply -f /workspace/examples/web-deployment.yaml >/dev/null
kubectl rollout status deploy/web --timeout=180s >/dev/null && echo "web ready"
docker build -q -t myapp:1.0 /workspace/examples/myapp >/dev/null
kind load docker-image myapp:1.0 --name lab >/dev/null 2>&1
kubectl apply -f /workspace/examples/myapp/myapp.yaml >/dev/null
kubectl rollout status deploy/myapp --timeout=120s >/dev/null && echo "myapp ready"

step "ข้อ 1 scale"
kubectl scale deployment web --replicas=5
kubectl rollout status deploy/web --timeout=120s
kubectl get pods -l app=web -o wide
kubectl scale deployment web --replicas=2
sleep 3
kubectl get deploy web

step "ข้อ 2 rolling update + undo"
kubectl set image deployment/web nginx=nginx:1.27-alpine
kubectl rollout status deployment/web --timeout=180s
kubectl get pods -l app=web
kubectl rollout history deployment/web
kubectl rollout undo deployment/web
kubectl rollout status deployment/web --timeout=180s
kubectl get deploy web -o jsonpath='{.spec.template.spec.containers[0].image}{"\n"}'

step "ข้อ 3 helm"
cd /workspace
helm create demo
helm install demo ./demo
helm list
kubectl rollout status deploy/demo --timeout=180s
kubectl get pods,svc -l app.kubernetes.io/instance=demo
kubectl patch svc demo -p '{"spec":{"type":"NodePort","ports":[{"port":80,"nodePort":30082}]}}'
kubectl get svc demo
sleep 3
curl -s -o /dev/null -w '%{http_code}\n' http://localhost:30082
helm uninstall demo

step "ข้อ 5 myapp:2.0"
cd /workspace/examples/myapp
sed -i 's/myapp:1.0/myapp:2.0/' index.html
docker build -q -t myapp:2.0 .
kind load docker-image myapp:2.0 --name lab
kubectl set image deployment/myapp myapp=myapp:2.0
kubectl rollout status deployment/myapp --timeout=120s
sleep 3
curl -s http://localhost:30081
