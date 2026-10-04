#!/bin/bash
# ทดสอบ LAB 01_Reference ภายใน container ทดลอง (รันด้วย docker exec)
set -u
step() { echo; echo "===== $* ====="; }

step "wait sshd + dockerd"
for i in $(seq 60); do (echo > /dev/tcp/127.0.0.1/22) 2>/dev/null && break; sleep 1; done && echo sshd-ready
for i in $(seq 90); do docker info >/dev/null 2>&1 && break; sleep 1; done && echo dockerd-ready

step "tool versions"
kind version; kubectl version --client | head -1; helm version --short; k9s version --short | head -3
ls /workspace/examples /workspace/examples/myapp

step "bash completion + alias (interactive shell)"
bash -ic 'type k; complete -p k' 2>&1 | grep -v 'no job control'

step "k8s-up"
time k8s-up

step "cluster state"
kubectl config current-context
kubectl get nodes
kubectl get pods -A

step "web deployment (NodePort 30080)"
kubectl apply -f /workspace/examples/web-deployment.yaml
kubectl rollout status deploy/web --timeout=180s
kubectl get pods -l app=web -o wide
curl -s -o /dev/null -w 'curl localhost:30080 -> %{http_code}\n' http://localhost:30080

step "hello pod"
kubectl apply -f /workspace/examples/hello-pod.yaml
kubectl wait --for=condition=Ready pod/hello --timeout=120s
kubectl logs hello

step "self-healing: delete one web pod"
P=$(kubectl get pods -l app=web -o jsonpath='{.items[0].metadata.name}')
kubectl delete pod "$P" --wait=false
sleep 5
kubectl get pods -l app=web

step "myapp: build + kind load + deploy (NodePort 30081)"
docker build -q -t myapp:1.0 /workspace/examples/myapp
kind load docker-image myapp:1.0 --name lab
kubectl apply -f /workspace/examples/myapp/myapp.yaml
kubectl rollout status deploy/myapp --timeout=120s
curl -s http://localhost:30081 | head -5

step "helm smoke test"
helm list -A

step "k8s-up again (idempotent)"
k8s-up | head -3
