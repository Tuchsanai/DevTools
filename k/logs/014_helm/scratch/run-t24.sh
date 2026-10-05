cd /workspace/pc/final
curl -s -X POST http://dev.shop.localhost:30080/api/orders -H 'content-type: application/json' -d '{"productId":1,"qty":1}' | head -c 200; echo
curl -s http://dev.shop.localhost:30080/api/stats; echo
helm uninstall som -n som-dev --keep-history
sleep 5
kubectl -n som-dev get all,pvc,secret 2>&1
helm list -n som-dev
echo "=== reinstall without password"
helm install som charts/som-shop -n som-dev -f charts/values-dev.yaml 2>&1 | tail -1
helm upgrade --install som charts/som-shop -n som-dev -f charts/values-dev.yaml 2>&1 | tail -1
echo "=== reinstall with password"
helm upgrade --install som charts/som-shop -n som-dev -f charts/values-dev.yaml --set db.password=meow1234 --wait 2>&1 | grep -E "REVISION|STATUS|Error"
curl -s http://dev.shop.localhost:30080/api/stats; echo
helm history som -n som-dev
kubectl -n som-dev get pvc
