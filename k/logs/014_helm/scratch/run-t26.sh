cd /workspace/pc
kubectl apply -f v9k8s/00-namespace.yaml
kubectl -n som-shop create secret generic som-db-secret --from-literal=POSTGRES_PASSWORD=meow1234 --from-literal=DATABASE_URL=postgres://som:meow1234@som-db-0.som-db:5432/catshop
cd /workspace/pc; openssl req -x509 -nodes -newkey rsa:2048 -days 365 -keyout tls.key -out tls.crt -subj '/CN=shop.localhost' -addext 'subjectAltName=DNS:shop.localhost,DNS:admin.localhost,DNS:localhost' 2>/dev/null
kubectl -n som-shop create secret tls som-tls --cert=tls.crt --key=tls.key
kubectl -n som-shop create secret generic som-admin-auth --type=kubernetes.io/basic-auth --from-literal=username=som --from-literal=password=meow-admin-123
kubectl apply -f v9k8s/ | tail -3
kubectl -n som-shop rollout status sts/som-db --timeout=240s && kubectl -n som-shop rollout status deploy/som-web --timeout=300s
curl -s -X POST -k https://shop.localhost:30081/api/orders -H 'content-type: application/json' -d '{"product_id":2,"qty":1}'; echo
echo "=== helm install over kubectl-applied shop"
helm install som final/charts/som-shop -n som-shop -f final/charts/values-prod.yaml 2>&1 | cut -c1-300
echo "=== take-ownership"
helm upgrade --install som final/charts/som-shop -n som-shop -f final/charts/values-prod.yaml --take-ownership 2>&1 | cut -c1-1500
