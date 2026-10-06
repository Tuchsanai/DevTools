set -v
cd /workspace/014_kubernetes_helm/02_LAB
ls labs/lab10-addons labs/lab10-addons/static-old
helm list -A
echo "=== 1) render chart เทียบ static"
helm template traefik traefik/traefik --version 41.6.1 -n traefik -f labs/lab10-addons/traefik-values.yaml > /root/traefik-rendered.yaml
grep "^kind:" /root/traefik-rendered.yaml | sort | uniq -c
grep -E -- '- "--(entryPoints.websecure.http.tls|providers.kubernetesingress.strictPrefixMatching|providers.kubernetesingress.ingressendpoint.hostname|api.insecure|accesslog)' /root/traefik-rendered.yaml
grep -nE "nodePort:|image:" /root/traefik-rendered.yaml
grep -A3 "matchLabels" /root/traefik-rendered.yaml | head -4
grep -A2 "matchLabels" labs/lab10-addons/static-old/00-traefik.yaml | head -3
echo "=== 2) ติดตั้งทับของเดิม (ลองผิด)"
helm install traefik traefik/traefik --version 41.6.1 -n traefik -f labs/lab10-addons/traefik-values.yaml 2>&1 | cut -c1-420
helm list -A
echo "=== 3) ย้ายจริง: ลบ static (เก็บ CRD) แล้วติดตั้ง chart ระหว่างลูกค้าเข้าร้าน"
kubectl get crd | grep -c traefik.io
./hit.sh -q https://shop.localhost:30081/api/whoami 600 0.1 > /root/hit-mig.log 2>&1 &
sleep 3
t0=$(date +%s)
kubectl delete -f labs/lab10-addons/static-old/00-traefik.yaml --wait=true
helm install traefik traefik/traefik --version 41.6.1 -n traefik --create-namespace -f labs/lab10-addons/traefik-values.yaml --wait --timeout 5m
echo "ย้าย Traefik: $(( $(date +%s)-t0 )) วินาที"
wait; tail -8 /root/hit-mig.log
kubectl get crd | grep -c traefik.io
kubectl -n traefik get deploy,svc,pod
kubectl get ingressclass
kubectl get ns traefik --show-labels
curl -s localhost:30080; echo
curl -s -o /dev/null -w "dashboard %{http_code}\n" localhost:30082/dashboard/
curl -si http://shop.localhost:30080/ | grep -iE "^HTTP|^location"
curl -sk https://shop.localhost:30081/api/stats; echo
curl -sk -o /dev/null -w "admin no-auth %{http_code}\n" https://admin.localhost:30081/
curl -sk -u som:meow-admin-123 https://admin.localhost:30081/stats; echo
echo "=== 4) metrics-server"
helm install metrics-server metrics-server/metrics-server --version 3.14.0 -n kube-system -f labs/lab10-addons/metrics-server-values.yaml 2>&1 | cut -c1-300
t0=$(date +%s)
kubectl delete -f labs/lab10-addons/static-old/00-metrics-server.yaml --wait=true | tail -3
helm install metrics-server metrics-server/metrics-server --version 3.14.0 -n kube-system -f labs/lab10-addons/metrics-server-values.yaml --wait --timeout 5m | grep -E "STATUS|REVISION"
echo "ย้าย metrics-server: $(( $(date +%s)-t0 )) วินาที"
kubectl get apiservice v1beta1.metrics.k8s.io
sleep 20; kubectl top nodes
kubectl -n som-shop get hpa
helm list -A
