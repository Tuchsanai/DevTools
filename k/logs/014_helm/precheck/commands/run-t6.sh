cd /workspace/pc
kubectl apply --server-side -f static-traefik/traefik-crds-v3.7.13.yml >/dev/null 2>&1 || kubectl apply -f static-traefik/traefik-crds-v3.7.13.yml > /dev/null
kubectl apply -f static-traefik/00-traefik.yaml
kubectl apply -f static-ms/00-metrics-server.yaml | tail -2
kubectl -n traefik rollout status deploy/traefik --timeout=180s
kubectl -n kube-system rollout status deploy/metrics-server --timeout=180s
echo "=== helm install over static (no flags)"
time helm install traefik traefik/traefik --version 41.6.1 -n traefik -f addons/traefik-values.yaml
echo "rc=$?"
helm list -A -a
