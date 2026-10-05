cd /workspace/pc
helm uninstall traefik -n traefik --wait >/dev/null; kubectl delete ns traefik --wait=true >/dev/null 2>&1
kubectl apply -f static-traefik/00-traefik.yaml >/dev/null && kubectl -n traefik rollout status deploy/traefik --timeout=120s
sleep 5; curl -sk https://shop.localhost:30081/api/whoami
bash final/hit.sh -q https://shop.localhost:30081/api/whoami 600 0.1 > hit-mig.log 2>&1 &
sleep 3
t0=$(date +%s)
kubectl delete -f static-traefik/00-traefik.yaml --wait=true >/dev/null
helm install traefik traefik/traefik --version 41.6.1 -n traefik --create-namespace -f addons/traefik-values.yaml --wait >/dev/null
echo "migration: $(( $(date +%s)-t0 ))s"
wait; tail -8 hit-mig.log
