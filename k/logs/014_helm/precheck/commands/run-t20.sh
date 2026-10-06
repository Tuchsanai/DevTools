cd /workspace/pc/final/charts
helm template som som-shop 2>&1 | head -3
echo "=== install dev"
t0=$(date +%s)
helm install som som-shop -n som-dev --create-namespace -f values-dev.yaml --set db.password=meow1234 --wait --timeout 5m
echo "dev install: $(( $(date +%s)-t0 ))s"
kubectl -n som-dev get all,pvc,secret,cm,ing
curl -s http://dev.shop.localhost:30080/api/whoami; echo
curl -s http://dev.shop.localhost:30080/api/stats; echo
curl -s http://dev.shop.localhost:30080/ | grep -o "ร้านอาหารแมวน้องส้ม (dev)" | head -1
