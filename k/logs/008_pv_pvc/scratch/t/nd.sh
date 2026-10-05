cd /root/t; kubectl apply -f nd.yaml; kubectl rollout status deploy/nd --timeout=90s
N=$(kubectl get pod -l app=nd -o jsonpath='{.items[0].spec.nodeName}'); echo "node=$N"; date +%T; docker stop $N >/dev/null; echo stopped $(date +%T)
for i in $(seq 1 30); do sleep 10; echo "--- $(date +%T)"; kubectl get node $N --no-headers; kubectl get pod -l app=nd -o wide --no-headers; done
kubectl describe pod -l app=nd | grep -E "Warning|FailedScheduling" | tail -3
kubectl get pv -o custom-columns=NAME:.metadata.name,CLAIM:.spec.claimRef.name,NODE:.spec.nodeAffinity.required.nodeSelectorTerms[0].matchExpressions[0].values[0]
docker start $N; echo started $(date +%T); for i in $(seq 1 20); do sleep 5; kubectl get pod -l app=nd -o wide --no-headers; kubectl get pod -l app=nd --no-headers | grep -q Running && break; done; date +%T
