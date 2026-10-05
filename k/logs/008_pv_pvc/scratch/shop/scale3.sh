order(){ curl -s -o /dev/null -w "%{http_code} " -X POST localhost:30080/api/orders -H 'content-type: application/json' -d '{"product_id":3,"qty":1}'; }
q(){ kubectl -n som-shop exec $1 -- psql -U som -d catshop -tAc "select count(*) from orders"; }
kubectl -n som-shop rollout restart deploy/som-web >/dev/null; kubectl -n som-shop rollout status deploy/som-web >/dev/null
echo before=$(q deploy/som-db)
kubectl -n som-shop scale deploy/som-db --replicas=2; kubectl -n som-shop rollout status deploy/som-db
order; order; order; echo
P=$(kubectl -n som-shop get pod -l app=som-db -o name)
for p in $P; do echo "$p orders=$(q $p) restarts=$(kubectl -n som-shop get $p -o jsonpath='{.status.containerStatuses[0].restartCount}')"; done
POD1=$(echo "$P" | head -1); for i in $(seq 1 6); do kubectl -n som-shop exec $POD1 -- env PGPASSWORD=meow1234 psql -h som-db -U som -d catshop -tAc "select inet_server_addr(), count(*) from orders"; done
kubectl -n som-shop scale deploy/som-db --replicas=1; sleep 20
P=$(kubectl -n som-shop get pod -l app=som-db -o name); kubectl -n som-shop get pod -l app=som-db
echo "after-scale1 orders=$(q $P)"; kubectl -n som-shop logs $P --previous --tail=8 2>&1; echo ---; kubectl -n som-shop logs $P --tail=5
for i in 1 2 3; do curl -s localhost:30080/api/stats; done
