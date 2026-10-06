set -v
cd /workspace/014_kubernetes_helm/02_LAB
ls
helm version
helm env | grep -E "HELM_(CACHE|CONFIG|DATA)_HOME|MAX_HISTORY|HELM_DRIVER"
kubectl get nodes
kubectl get node -o jsonpath='{range .items[*]}{.metadata.name} {.status.nodeInfo.architecture}{"\n"}{end}'
kubectl get ns som-shop traefik
kubectl -n som-shop get deploy,sts,hpa
helm list -A
curl -sk https://shop.localhost:30081/api/stats; echo
cd som-shop-v10
time (docker build -q -t som-shop-web:1.8 --build-arg APP_VERSION=1.8 app && kind load docker-image som-shop-web:1.8 --name lab)
docker run --rm som-shop-web:1.8 node -e 'console.log(process.env.APP_VERSION)'
for n in lab-worker lab-worker2; do echo "== $n"; docker exec $n crictl images | grep -E "som-shop|postgres"; done
