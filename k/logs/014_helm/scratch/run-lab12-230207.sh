set -v
cd /workspace/014_kubernetes_helm/02_LAB
echo "=== 12.1 จุดเริ่ม"
helm list -A
kubectl -n som-shop get deploy,sts,hpa,ing
curl -sk https://shop.localhost:30081/api/stats; echo
kubectl -n som-shop get deploy som-web -o jsonpath='{range .metadata.managedFields[*]}{.manager}{" "}{.operation}{"\n"}{end}'
fp() { kubectl -n som-shop get secret som-tls -o jsonpath='{.data.tls\.crt}' | base64 -d | openssl x509 -noout -fingerprint -sha256 | cut -c1-40; }
echo "cert ก่อน: $(fp)"
echo "=== 12.2 อ่านชุดแฟรนไชส์"
helm lint charts/som-shop -f charts/values-prod.yaml --set db.password=x
helm lint charts/som-shop -f charts/values-dev.yaml --set db.password=x | tail -1
echo "=== 12.3 สาขา dev คำสั่งเดียว"
time helm install som charts/som-shop -n som-dev --create-namespace -f charts/values-dev.yaml --set db.password=meow1234 --wait
helm test som -n som-dev --logs | sed -n '/Phase/,$p'
curl -s http://dev.shop.localhost:30080/api/whoami; echo
curl -s http://dev.shop.localhost:30080/ | grep -oE "ร้านอาหารแมวน้องส้ม \(dev\)|theme-[a-z]+|data-theme=\"[a-z]+\"" | sort -u
echo "=== 12.4 (ก) install ทับร้านเดิม"
helm install som charts/som-shop -n som-shop -f charts/values-prod.yaml 2>&1 | cut -c1-300
helm list -n som-shop
echo "=== 12.4 (ข) --take-ownership"
helm upgrade --install som charts/som-shop -n som-shop -f charts/values-prod.yaml --take-ownership 2>&1 | cut -c1-2000
helm history som -n som-shop | cut -c1-120
echo "=== 12.4 (ค) --take-ownership --force-conflicts"
time helm upgrade --install som charts/som-shop -n som-shop -f charts/values-prod.yaml --take-ownership --force-conflicts --wait --timeout 5m 2>&1 | cut -c1-300
helm history som -n som-shop | cut -c1-120
kubectl -n som-shop get deploy,sts,hpa,ing,pvc
curl -sk https://shop.localhost:30081/api/stats; echo
echo "cert หลัง: $(fp)"
kubectl -n som-shop get secret som-db-secret -o jsonpath='{.data.POSTGRES_PASSWORD}' | base64 -d | sed 's/./*/g'; echo " (รหัสเดิมจาก lookup ซ่อนเป็น *)"
kubectl -n som-shop get deploy som-web -o jsonpath='{range .metadata.managedFields[*]}{.manager}{" "}{.operation}{"\n"}{end}'
kubectl -n som-shop get deploy som-web -o jsonpath='{.metadata.annotations.kubernetes\.io/change-cause}{"\n"}{.metadata.annotations.meta\.helm\.sh/release-name}{"\n"}{.spec.template.spec.initContainers[*].name}{"\n"}'
kubectl -n som-shop get hpa som-web -o jsonpath='{.spec.behavior.scaleDown.stabilizationWindowSeconds}{"\n"}'
kubectl -n som-shop get ing
echo "=== 12.5 เก็บของเก่า"
kubectl -n som-shop delete ingress som-shop
kubectl -n som-shop delete deploy customers
kubectl -n som-shop get ing,middleware
curl -si http://shop.localhost:30080/ | grep -iE "^HTTP|^location"
curl -sk https://shop.localhost:30081/api/whoami; echo
curl -sk -u som:meow-admin-123 -o /dev/null -w "admin %{http_code}\n" https://admin.localhost:30081/
curl -sk https://shop.localhost:30081/ | grep -oE "⚓ ท่าเรือ Kubernetes · [A-Za-z]+|🎉 เปิดสาขาใหม่[^<]*" | sort -u
