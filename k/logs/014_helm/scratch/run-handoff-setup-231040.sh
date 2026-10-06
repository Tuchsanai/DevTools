set -v
cd /workspace/014_kubernetes_helm/02_LAB
helm install som charts/som-shop -n som-dev --create-namespace -f charts/values-dev.yaml --set db.password=meow1234 --wait | grep -E "STATUS|REVISION"
for i in 1 2; do curl -sk -XPOST -H "content-type: application/json" -d '{"product_id":6,"qty":1}' https://shop.localhost:30081/api/orders; echo; done
curl -sk https://shop.localhost:30081/api/stats; echo
curl -s http://dev.shop.localhost:30080/api/stats; echo
helm list -A
kubectl get ns --show-labels | grep -E "som-|traefik"
