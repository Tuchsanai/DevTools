cd /root/shop; kubectl apply -f 00-namespace.yaml -f 10-db.yaml -f 20-web.yaml >/dev/null
kubectl -n som-shop rollout status deploy/som-db --timeout=120s; kubectl -n som-shop rollout status deploy/som-web --timeout=180s
kubectl -n som-shop get pvc,pv; kubectl -n som-shop get pod -o wide
order(){ curl -s -X POST localhost:30080/api/orders -H 'content-type: application/json' -d '{"product_id":1,"qty":1}'; echo; }
st(){ for i in $(seq 1 30); do r=$(curl -s -m 2 localhost:30080/api/stats); case "$r" in *orders=*) echo "$r"; return;; esac; sleep 2; done; echo "stats fail: $r"; }
order; order; order; st
echo "== delete pod db"; date +%T; kubectl -n som-shop delete pod -l app=som-db; kubectl -n som-shop rollout status deploy/som-db --timeout=120s; date +%T; st
echo "== rollout restart db"; kubectl -n som-shop rollout restart deploy/som-db; kubectl -n som-shop rollout status deploy/som-db --timeout=120s; st
echo "== delete deploy db + apply"; kubectl -n som-shop delete deploy som-db; kubectl -n som-shop get pvc; kubectl apply -f 10-db.yaml; kubectl -n som-shop rollout status deploy/som-db --timeout=120s; st
N=$(kubectl -n som-shop get pod -l app=som-db -o jsonpath='{.items[0].spec.nodeName}'); PV=$(kubectl -n som-shop get pvc som-db-data -o jsonpath='{.spec.volumeName}'); echo node=$N pv=$PV; docker exec $N ls -ln /var/local-path-provisioner/${PV}_som-shop_som-db-data/ /var/local-path-provisioner/${PV}_som-shop_som-db-data/pgdata | head -8
kubectl -n som-shop exec deploy/som-db -- id; kubectl -n som-shop exec deploy/som-db -- psql -U som -d catshop -c 'select count(*) from orders'
