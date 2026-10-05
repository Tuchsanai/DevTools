cd /root/shop
st(){ for i in $(seq 1 40); do r=$(curl -s -m 2 localhost:30080/api/stats); case "$r" in *orders=*) echo "$r"; return;; esac; sleep 2; done; echo "stats fail: $r"; }
order(){ curl -s -o /dev/null -w "%{http_code} " -X POST localhost:30080/api/orders -H 'content-type: application/json' -d '{"product_id":1,"qty":1}'; }
echo "== delete PVC (Delete policy)"; PV=$(kubectl -n som-shop get pvc som-db-data -o jsonpath='{.spec.volumeName}'); N=$(kubectl get pv $PV -o jsonpath='{.spec.nodeAffinity.required.nodeSelectorTerms[0].matchExpressions[0].values[0]}')
kubectl -n som-shop delete deploy som-db; time kubectl -n som-shop delete pvc som-db-data; sleep 3; kubectl get pv $PV 2>&1; docker exec $N ls /var/local-path-provisioner/
kubectl apply -f 10-db.yaml >/dev/null; kubectl -n som-shop rollout status deploy/som-db --timeout=120s >/dev/null; sleep 5; curl -s localhost:30080/api/stats
kubectl -n som-shop rollout restart deploy/som-web >/dev/null; kubectl -n som-shop rollout status deploy/som-web >/dev/null; st
echo "== retain SC + RWOP"; kubectl -n som-shop delete deploy som-db >/dev/null; kubectl -n som-shop delete pvc som-db-data >/dev/null
kubectl apply -f sc-retain.yaml; kubectl get sc; kubectl apply -f 10-db-retain.yaml >/dev/null; kubectl -n som-shop rollout status deploy/som-db --timeout=120s >/dev/null
kubectl -n som-shop rollout restart deploy/som-web >/dev/null; kubectl -n som-shop rollout status deploy/som-web >/dev/null; order; order; echo; st
kubectl -n som-shop get pvc
echo "== scale 2 with RWOP"; kubectl -n som-shop scale deploy/som-db --replicas=2; sleep 15; kubectl -n som-shop get pod -l app=som-db -o wide; P=$(kubectl -n som-shop get pod -l app=som-db --field-selector=status.phase=Pending -o name); kubectl -n som-shop describe $P | grep FailedScheduling; kubectl -n som-shop scale deploy/som-db --replicas=1; sleep 5; st
echo "== delete PVC with Retain"; PV=$(kubectl -n som-shop get pvc som-db-data -o jsonpath='{.spec.volumeName}'); kubectl -n som-shop delete deploy som-db; kubectl -n som-shop delete pvc som-db-data; sleep 3; kubectl get pv $PV
echo "== rescue: remove claimRef + PVC volumeName"; kubectl patch pv $PV --type json -p '[{"op":"remove","path":"/spec/claimRef"}]'; kubectl get pv $PV --no-headers
sed "s/  storageClassName: standard-retain/  storageClassName: standard-retain\n  volumeName: $PV/" 10-db-retain.yaml > 10-db-rescue.yaml; kubectl apply -f 10-db-rescue.yaml >/dev/null; kubectl -n som-shop rollout status deploy/som-db --timeout=120s >/dev/null; kubectl -n som-shop get pvc; kubectl get pv $PV --no-headers; st
