cd /root/shop9
st(){ for i in $(seq 1 40); do r=$(curl -s -m 2 localhost:30080/api/stats); case "$r" in *orders=*) echo "$(date +%T) $r"; return;; esac; sleep 2; done; echo "stats fail: $r"; }
order(){ curl -s -o /dev/null -w "%{http_code} " -X POST localhost:30080/api/orders -H 'content-type: application/json' -d '{"product_id":4,"qty":1}'; }
echo "== 008 end-state"; kubectl apply -f 00-namespace.yaml -f 10-db-008.yaml -f 20-web.yaml >/dev/null; kubectl -n som-shop rollout status deploy/som-web --timeout=180s >/dev/null; order; order; order; echo; st
echo "== migrate"; PV=$(kubectl -n som-shop get pvc som-db-data -o jsonpath='{.spec.volumeName}')
kubectl patch pv $PV -p '{"spec":{"persistentVolumeReclaimPolicy":"Retain"}}'
kubectl -n som-shop delete deploy som-db; kubectl -n som-shop delete svc som-db; kubectl -n som-shop delete pvc som-db-data; kubectl get pv $PV --no-headers
kubectl patch pv $PV --type json -p '[{"op":"remove","path":"/spec/claimRef"}]'
sed "s/PVNAME/$PV/" migrate-pvc.yaml | kubectl apply -f -; kubectl apply -f 10-db.yaml; kubectl -n som-shop rollout status sts/som-db --timeout=120s
kubectl -n som-shop get sts,pod,pvc -o wide; kubectl get pv $PV --no-headers
kubectl apply -f 20-web-sts.yaml >/dev/null; kubectl -n som-shop rollout status deploy/som-web --timeout=180s >/dev/null; st
kubectl patch pv $PV -p '{"spec":{"persistentVolumeReclaimPolicy":"Delete"}}' >/dev/null
echo "== delete pod som-db-0"; kubectl -n som-shop get pod som-db-0 -o jsonpath='{.metadata.uid} {.status.podIP}{"\n"}'; kubectl -n som-shop delete pod som-db-0; kubectl -n som-shop wait --for=condition=Ready pod/som-db-0 --timeout=120s; kubectl -n som-shop get pod som-db-0 -o jsonpath='{.metadata.uid} {.status.podIP} {.spec.volumes[0].persistentVolumeClaim.claimName}{"\n"}'; st
echo "== rolling update resources"; kubectl -n som-shop patch sts som-db --type json -p '[{"op":"replace","path":"/spec/template/spec/containers/0/resources/limits/memory","value":"768Mi"}]'; kubectl -n som-shop rollout status sts/som-db --timeout=120s; kubectl -n som-shop rollout history sts/som-db; order; echo; st
echo "== delete sts + apply"; kubectl -n som-shop delete sts som-db; kubectl -n som-shop get pvc --no-headers; kubectl apply -f 10-db.yaml >/dev/null; kubectl -n som-shop rollout status sts/som-db --timeout=120s >/dev/null; st
echo "== scale 3"; kubectl -n som-shop scale sts som-db --replicas=3; kubectl -n som-shop rollout status sts/som-db --timeout=180s; kubectl -n som-shop get pod,pvc -l app=som-db -o wide
for i in 0 1 2; do echo "som-db-$i: $(kubectl -n som-shop exec som-db-$i -- psql -U som -d catshop -tAc 'select count(*) from orders' 2>&1 | head -1)"; done
kubectl -n som-shop run dns --image=busybox:1.36 --restart=Never --rm -i --quiet -- sh -c 'nslookup som-db | grep -A1 Name; nslookup som-db-1.som-db.som-shop.svc.cluster.local | tail -2' 2>/dev/null
for i in 1 2 3; do st; done
echo "== scale 1"; kubectl -n som-shop scale sts som-db --replicas=1; sleep 15; kubectl -n som-shop get pod,pvc -l app=som-db --no-headers; st
