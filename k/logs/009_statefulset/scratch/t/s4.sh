cd /root/t9; kubectl apply -f sts-tol.yaml >/dev/null; kubectl rollout status sts/web >/dev/null; kubectl get pod -l app=web -o wide --no-headers
N=$(kubectl get pod web-1 -o jsonpath='{.spec.nodeName}'); echo "stop $N $(date +%T)"; docker stop $N >/dev/null
for i in $(seq 1 14); do sleep 10; echo "--- $(date +%T) $(kubectl get node $N --no-headers | awk '{print $2}')"; kubectl get pod -l app=web -o wide --no-headers | awk '{print $1,$2,$3,$7}'; done
kubectl get pod web-1 -o jsonpath='{.metadata.deletionTimestamp} {.status.conditions[?(@.type=="Ready")].status}'; echo
echo "== out-of-service taint $(date +%T)"; kubectl taint node $N node.kubernetes.io/out-of-service=nodeshutdown:NoExecute
for i in $(seq 1 6); do sleep 10; echo "--- $(date +%T)"; kubectl get pod -l app=web -o wide --no-headers | awk '{print $1,$2,$3,$7}'; done
kubectl describe pod web-1 | grep FailedScheduling | tail -1
kubectl taint node $N node.kubernetes.io/out-of-service-; docker start $N; kubectl wait --for=condition=Ready node/$N --timeout=120s; kubectl wait --for=condition=Ready pod/web-1 --timeout=120s; kubectl get pod -l app=web -o wide --no-headers | awk '{print $1,$2,$3,$7}'; kubectl exec web-1 -- cat /usr/share/nginx/html/index.html
