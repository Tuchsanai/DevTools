cd /workspace/pc
helm list --help | grep -E "^\s+-" | head -30
echo "=== take-ownership"
time helm install traefik traefik/traefik --version 41.6.1 -n traefik -f addons/traefik-values.yaml --take-ownership
echo "rc=$?"
helm list -n traefik
helm history traefik -n traefik
kubectl -n traefik get deploy,rs,pod,svc
