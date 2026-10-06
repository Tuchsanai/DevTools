cd /workspace/pc
echo "=== metrics-server plain"
helm install metrics-server metrics-server/metrics-server --version 3.14.0 -n kube-system -f addons/metrics-server-values.yaml 2>&1 | cut -c1-400
echo "=== metrics-server take-ownership"
helm upgrade --install metrics-server metrics-server/metrics-server --version 3.14.0 -n kube-system -f addons/metrics-server-values.yaml --take-ownership 2>&1 | cut -c1-700
echo "=== +force-conflicts"
helm upgrade --install metrics-server metrics-server/metrics-server --version 3.14.0 -n kube-system -f addons/metrics-server-values.yaml --take-ownership --force-conflicts 2>&1 | cut -c1-500
helm history metrics-server -n kube-system | cut -c1-120
