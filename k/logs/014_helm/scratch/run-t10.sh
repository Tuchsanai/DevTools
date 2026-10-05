cd /workspace/pc
helm uninstall traefik -n traefik 2>&1 | tail -3
helm uninstall metrics-server -n kube-system 2>&1 | tail -3
kubectl -n traefik get sa,deploy,svc 2>&1; kubectl get clusterrole traefik system:metrics-server 2>&1 | tail -3
kubectl delete -f static-traefik/00-traefik.yaml --ignore-not-found --wait=true
kubectl delete -f static-ms/00-metrics-server.yaml --ignore-not-found --wait=true | tail -3
kubectl get crd | grep -c traefik.io
t0=$(date +%s)
helm install traefik traefik/traefik --version 41.6.1 -n traefik --create-namespace -f addons/traefik-values.yaml --wait --timeout 5m
t1=$(date +%s); echo "traefik install+wait: $((t1-t0))s"
helm install metrics-server metrics-server/metrics-server --version 3.14.0 -n kube-system -f addons/metrics-server-values.yaml --wait --timeout 5m
t2=$(date +%s); echo "ms install+wait: $((t2-t1))s"
kubectl get ingressclass; kubectl -n traefik get svc,pod
curl -s localhost:30080; echo; curl -s -o /dev/null -w "%{http_code}\n" localhost:30082/dashboard/
for i in $(seq 30); do kubectl top nodes >/dev/null 2>&1 && break; sleep 3; done; kubectl top nodes
kubectl get apiservice v1beta1.metrics.k8s.io
helm list -A
