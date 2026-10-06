cd /workspace/pc
kubectl -n som-shop get hpa som-web -o jsonpath='{.spec.behavior.scaleDown.stabilizationWindowSeconds}{"\n"}'
kubectl -n som-shop get deploy som-web -o jsonpath='{.metadata.annotations.kubernetes\.io/change-cause}{"\n"}{.metadata.annotations.meta\.helm\.sh/release-name}{"\n"}'
kubectl -n som-shop get deploy som-web -o jsonpath='{range .metadata.managedFields[*]}{.manager}{" "}{.operation}{"\n"}{end}'
kubectl -n som-shop get cm som-web-config -o jsonpath='{.data.SHOP_EYEBROW}{"\n"}'
kubectl -n som-shop delete ingress som-shop; kubectl -n som-shop delete middleware redirect-https
kubectl -n som-shop delete deploy customers
curl -s -o /dev/null -w "%{http_code} %{redirect_url}\n" http://shop.localhost:30080/
curl -sk https://shop.localhost:30081/api/whoami
curl -sk -u som:meow-admin-123 https://admin.localhost:30081/stats; echo
helm test som -n som-shop --logs | grep -E "Phase|health"
echo "=== upgrade again without force (conflicts gone?)"
helm upgrade som final/charts/som-shop -n som-shop -f final/charts/values-prod.yaml --set web.image.tag=1.8 --wait 2>&1 | grep -E "REVISION|Error|conflict" | cut -c1-300
