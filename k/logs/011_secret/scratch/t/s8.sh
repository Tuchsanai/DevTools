x(){ echo; echo "\$ $*"; bash -c "$*" 2>&1; echo "[rc=$?]"; }
NS="-n som-shop"
docker save som-shop-web:1.4 -o /root/web14.tar && kind load image-archive /root/web14.tar --name lab
for n in lab-worker lab-worker2; do docker exec $n crictl images | grep som-shop; done
kubectl $NS rollout status deploy/som-web --timeout=240s | tail -1
x "kubectl $NS get pod -l app=som-web"
x "kubectl $NS exec som-db-0 -- psql -U som -d catshop -c \"ALTER USER som PASSWORD 'purr5678';\""
x "kubectl $NS rollout restart deploy/som-web"
sleep 45
x "kubectl $NS get pod -l app=som-web"
P=$(kubectl $NS get pod -l app=som-web --no-headers | grep -v ' Running ' | awk '{print $1}' | head -1)
x "kubectl $NS logs $P -c db-seed --tail=6"
x "for i in 1 2 3 4 5 6; do curl -s -o /dev/null -w '%{http_code} ' localhost:30080/api/stats; done"
x "kubectl $NS create secret generic som-db-secret --from-literal=POSTGRES_PASSWORD=purr5678 --from-literal=DATABASE_URL=postgres://som:purr5678@som-db-0.som-db:5432/catshop --dry-run=client -o yaml | kubectl apply -f -"
x "kubectl $NS rollout restart deploy/som-web"
t0=$(date +%s); kubectl $NS rollout status deploy/som-web --timeout=240s | tail -1; echo "rollout $(( $(date +%s)-t0 ))s"; sleep 8
x "kubectl $NS get pod"
x "curl -s localhost:30080/api/stats; curl -s -XPOST -H 'content-type: application/json' -d '{\"product_id\":1,\"qty\":1}' localhost:30080/api/orders; echo; curl -s localhost:30080/api/stats"
x "kubectl $NS rollout history deploy/som-web | tail -4"
