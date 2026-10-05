x(){ echo; echo "\$ $*"; bash -c "$*" 2>&1; echo "[rc=$?]"; }
NS="-n som-shop"
kind load docker-image som-shop-web:1.4 --name lab 2>&1 | tail -1
kubectl $NS rollout restart deploy/som-web; kubectl $NS rollout status deploy/som-web --timeout=240s | tail -1
x "kubectl $NS get pod"
x "kubectl $NS exec som-db-0 -- cat /var/lib/postgresql/data/pgdata/pg_hba.conf | grep -v -E '^#|^$'"
PG="kubectl $NS exec som-db-0 -- sh -c"
x "$PG 'PGPASSWORD=meow1234 psql -h som-db-0.som-db -U som -d catshop -tAc \"select 1\"'"
x "$PG 'PGPASSWORD=purr5678 psql -h som-db-0.som-db -U som -d catshop -tAc \"select 1\"'"
# scenario: change password but forget secret
x "kubectl $NS exec som-db-0 -- psql -U som -d catshop -c \"ALTER USER som PASSWORD 'whisker9012';\""
sleep 5
x "for i in 1 2 3 4 5 6; do curl -s -o /dev/null -w '%{http_code} ' localhost:30080/api/stats; done"
x "kubectl $NS rollout restart deploy/som-web"
sleep 40
x "kubectl $NS get pod -l app=som-web"
P=$(kubectl $NS get pod -l app=som-web --no-headers | grep -v Running | awk '{print $1}' | head -1)
x "kubectl $NS logs $P -c db-seed --tail=5"
x "for i in 1 2 3 4 5 6; do curl -s -o /dev/null -w '%{http_code} ' localhost:30080/api/stats; done"
x "kubectl $NS create secret generic som-db-secret --from-literal=POSTGRES_PASSWORD=whisker9012 --from-literal=DATABASE_URL=postgres://som:whisker9012@som-db-0.som-db:5432/catshop --dry-run=client -o yaml | kubectl apply -f -"
x "kubectl $NS rollout restart deploy/som-web"
kubectl $NS rollout status deploy/som-web --timeout=240s | tail -1; sleep 8
x "kubectl $NS get pod"
x "curl -s localhost:30080/api/stats; curl -s -XPOST -H 'content-type: application/json' -d '{\"product_id\":3,\"qty\":1}' localhost:30080/api/orders; echo; curl -s localhost:30080/api/stats"
x "kubectl $NS get secret som-db-secret -o jsonpath='{.data.POSTGRES_PASSWORD}' | base64 -d; echo"
x "kubectl $NS describe secret som-db-secret | tail -4"
x "kubectl $NS get secret som-db-secret -o yaml | grep -c last-applied"
x "kubectl $NS get secret som-db-secret -o jsonpath='{.metadata.annotations}' | head -c 200"
