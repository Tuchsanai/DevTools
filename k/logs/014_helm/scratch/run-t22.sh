cd /workspace/pc/final/charts
t0=$(date +%s)
helm install som som-shop -n som-prod --create-namespace -f values-prod.yaml --set db.password=meow1234 --wait --timeout 5m | sed -n '/NOTES/,$p'
echo "prod install: $(( $(date +%s)-t0 ))s"
kubectl -n som-prod get deploy,sts,hpa,ing,secret,middleware
curl -s -o /dev/null -w "%{http_code} %{redirect_url}\n" http://shop.localhost:30080/
curl -sk https://shop.localhost:30081/api/whoami; echo
curl -s --cacert <(kubectl -n som-prod get secret som-tls -o jsonpath='{.data.tls\.crt}' | base64 -d) https://shop.localhost:30081/api/whoami; echo " (cacert ok)"
for i in $(seq 20); do kubectl -n som-prod get hpa som-web --no-headers | grep -q "cpu: [0-9]" && break; sleep 5; done; kubectl -n som-prod get hpa
helm test som -n som-prod --logs | sed -n '/Phase/,$p'
