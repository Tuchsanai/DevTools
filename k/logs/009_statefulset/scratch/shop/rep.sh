cd /root/shop9; kubectl -n som-shop delete pvc data-som-db-1 data-som-db-2
kubectl -n som-shop exec som-db-0 -- sh -c 'grep -q "^host replication all all" $PGDATA/pg_hba.conf || echo "host replication all all scram-sha-256" >> $PGDATA/pg_hba.conf; psql -U som -d catshop -tAc "select pg_reload_conf()"'
kubectl apply -f replica.yaml; kubectl -n som-shop rollout status sts/som-db-replica --timeout=180s; kubectl -n som-shop logs som-db-replica-0 -c clone-from-primary | tail -2
kubectl -n som-shop exec som-db-replica-0 -- psql -U som -d catshop -tAc "select pg_is_in_recovery(), count(*) from orders"
curl -s -o /dev/null -w "%{http_code}\n" -X POST localhost:30080/api/orders -H 'content-type: application/json' -d '{"product_id":5,"qty":1}'; sleep 1
kubectl -n som-shop exec som-db-0 -- psql -U som -d catshop -tAc "select count(*) from orders"
kubectl -n som-shop exec som-db-replica-0 -- psql -U som -d catshop -tAc "select count(*) from orders"
kubectl -n som-shop exec som-db-0 -- psql -U som -d catshop -tAc "select client_addr, state, sync_state from pg_stat_replication"
kubectl -n som-shop exec som-db-replica-0 -- psql -U som -d catshop -c "insert into orders(product_id,qty) values (1,1)" 2>&1 | head -1
kubectl -n som-shop delete pod som-db-replica-0; kubectl -n som-shop wait --for=condition=Ready pod/som-db-replica-0 --timeout=120s; kubectl -n som-shop logs som-db-replica-0 -c clone-from-primary; kubectl -n som-shop exec som-db-replica-0 -- psql -U som -d catshop -tAc "select pg_is_in_recovery(), count(*) from orders"
