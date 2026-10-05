R="../r.sh lab09"; D=som-shop-v7; NS="-n som-shop"
PG="kubectl $NS exec som-db-0 -- sh -c"
# D1
$R $D "kubectl $NS exec som-db-0 -- psql -U som -d catshop -c \"ALTER USER som PASSWORD 'purr5678';\""
$R $D 'sleep 10; for i in 1 2 3 4 5 6; do curl -s -o /dev/null -w "%{http_code} " localhost:30080/api/stats; done; echo; curl -s localhost:30080/api/stats'
$R $D "kubectl $NS get pod -l app=som-web"
$R $D "$PG 'PGPASSWORD=meow1234 psql -h som-db-0.som-db -U som -d catshop -tAc \"select 1\"'"
$R $D "$PG 'PGPASSWORD=purr5678 psql -h som-db-0.som-db -U som -d catshop -tAc \"select 1\"'"
$R $D "$PG 'PGPASSWORD=wrong-anything psql -h 127.0.0.1 -U som -d catshop -tAc \"select 1\"'"
$R $D "kubectl $NS exec som-db-0 -- grep -v -E '^#|^\$' /var/lib/postgresql/data/pgdata/pg_hba.conf"
# D2 ลองผิด
$R $D "kubectl $NS rollout restart deploy/som-web"
$R $D "sleep 40; kubectl $NS get pod -l app=som-web"
$R $D "P=\$(kubectl $NS get pod -l app=som-web --no-headers | grep -v ' Running ' | awk '{print \$1}' | head -1); echo \"Pod ใหม่: \$P\"; kubectl $NS logs \$P -c db-seed"
$R $D "P=\$(kubectl $NS get pod -l app=som-web --no-headers | grep -v ' Running ' | awk '{print \$1}' | head -1); kubectl $NS describe pod \$P | sed -n '/Init Containers:/,/Containers:/p' | grep -E 'db-seed:|State|Reason|Exit Code|Restart Count'"
$R $D 'for i in 1 2 3 4 5 6; do curl -s -o /dev/null -w "%{http_code} " localhost:30080/api/stats; done; echo; curl -s localhost:30080/api/stats'
$R $D "kubectl $NS rollout status deploy/som-web --timeout=60s"
$R $D "kubectl $NS get deploy som-web; kubectl $NS describe deploy som-web | grep -A4 Conditions"
$R $D "kubectl $NS get pod -l app=som-web"
# D3
$R $D "kubectl $NS create secret generic som-db-secret --from-literal=POSTGRES_PASSWORD=purr5678 --from-literal=DATABASE_URL=postgres://som:purr5678@som-db-0.som-db:5432/catshop --dry-run=client -o yaml | kubectl apply -f -"
$R $D "kubectl $NS rollout restart deploy/som-web && time kubectl $NS rollout status deploy/som-web --timeout=240s"
$R $D "sleep 8; kubectl $NS get pod"
$R $D 'curl -s localhost:30080/api/stats; curl -s -XPOST -H "content-type: application/json" -d "{\"product_id\":4,\"qty\":2}" localhost:30080/api/orders; echo; ./hit.sh http://localhost:30080/api/stats 12 0.1'
$R $D "kubectl $NS get secret som-db-secret -o jsonpath='{.data.POSTGRES_PASSWORD}' | base64 -d; echo"
$R $D "kubectl $NS get secret som-db-secret -o jsonpath='{.metadata.annotations.kubectl\.kubernetes\.io/last-applied-configuration}'; echo; kubectl $NS get secret som-db-secret -o yaml | grep -c purr5678"
$R $D "kubectl $NS rollout history deploy/som-web"
# D4
$R $D "kubectl $NS exec som-db-0 -- psql -U som -d catshop -tAc 'select count(*) from orders'; kubectl $NS delete pod som-db-0 && kubectl $NS wait --for=condition=Ready pod/som-db-0 --timeout=120s"
$R $D "sleep 5; kubectl $NS exec som-db-0 -- psql -U som -d catshop -tAc 'select count(*) from orders'; curl -s localhost:30080/api/stats; $PG 'PGPASSWORD=purr5678 psql -h som-db-0.som-db -U som -d catshop -tAc \"select 1\"'"
