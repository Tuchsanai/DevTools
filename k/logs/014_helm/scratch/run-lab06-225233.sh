set -v
cd /workspace/014_kubernetes_helm/02_LAB/labs/lab06-debug
bash make-broken.sh
echo "=== 1) indent"
helm lint broken-indent
helm template web broken-indent 2>&1 | tail -3
helm template web broken-indent --debug 2>&1 | grep -n -B2 -A3 "shop: som" | head -12
echo "=== 2) function"
helm lint broken-func 2>&1 | tail -4
echo "=== 3) required"
helm template web broken-required --set image.repository= 2>&1 | tail -2
helm template web broken-required | grep "image:" | head -1
echo "=== 4) apiVersion v3"
helm lint broken-v3 2>&1 | tail -4
HELM_EXPERIMENTAL_CHART_V3=1 helm lint broken-v3 2>&1 | tail -3
echo "=== 5) --dry-run=server กับ spec.type ผิด"
helm install web2 ../lab05-first/mychart -n first --dry-run=server --set service.type=NodePortt 2>&1 | head -8
helm install web2 ../lab05-first/mychart -n first --dry-run=server --set service.type=NodePortt 2>&1 | grep -n "type:"
helm template web2 ../lab05-first/mychart --set service.type=NodePortt | kubectl apply --dry-run=server -n first -f - 2>&1 | tail -3
helm install web2 ../lab05-first/mychart -n first --set service.type=NodePortt 2>&1 | tail -2
helm list -n first
