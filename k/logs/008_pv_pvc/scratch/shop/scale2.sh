cd /root/shop; kubectl -n som-shop scale deploy/som-db --replicas=2; sleep 25
kubectl -n som-shop get pod -l app=som-db -o wide
for p in $(kubectl -n som-shop get pod -l app=som-db -o name); do echo "== $p"; kubectl -n som-shop logs $p --tail=6; done
kubectl -n som-shop get endpointslice -l kubernetes.io/service-name=som-db -o jsonpath='{range .items[*].endpoints[*]}{.addresses[0]} {.conditions.ready}{"\n"}{end}'
for i in 1 2 3 4; do curl -s -X POST localhost:30080/api/orders -H 'content-type: application/json' -d '{"product_id":2,"qty":1}'; echo; done
for i in $(seq 1 6); do curl -s localhost:30080/api/stats; done
for p in $(kubectl -n som-shop get pod -l app=som-db -o name); do echo "== $p"; kubectl -n som-shop exec $p -- psql -U som -d catshop -tAc 'select count(*) from orders' ; done
