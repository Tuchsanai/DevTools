cd /workspace/pc/final
kubectl -n som-dev delete pod som-test-health --ignore-not-found
curl -s -X POST http://dev.shop.localhost:30080/api/orders -H 'content-type: application/json' -d '{"product_id":1,"qty":2}'; echo
helm test som -n som-dev --logs | grep -E "Phase|health"
kubectl -n som-dev get pod
helm uninstall som -n som-dev
sleep 8; kubectl -n som-dev get pod,pvc,secret
echo "=== reinstall with WRONG password (PVC kept old one)"
time helm install som charts/som-shop -n som-dev -f charts/values-dev.yaml --set db.password=purr5678 --timeout 90s 2>&1 | tail -3
kubectl -n som-dev get pod
kubectl -n som-dev logs job/som-seed --all-containers --tail=3 2>&1 | tail -3
helm list -n som-dev
echo "=== fix"
helm upgrade som charts/som-shop -n som-dev -f charts/values-dev.yaml --set db.password=meow1234 --wait --timeout 3m 2>&1 | grep -E "REVISION|STATUS|Error"
curl -s http://dev.shop.localhost:30080/api/stats; echo
helm history som -n som-dev
