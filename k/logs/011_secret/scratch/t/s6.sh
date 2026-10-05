x(){ echo; echo "\$ $*"; bash -c "$*" 2>&1; echo "[rc=$?]"; }
cd /workspace/t/shop011
NS="-n som-shop"
x "kubectl $NS get pod; curl -s localhost:30080/api/stats"
# intern before
x "kubectl $NS create sa intern; kubectl $NS create role intern-view --verb=get,list,watch --resource=pods,pods/log,configmaps,deployments,statefulsets; kubectl $NS create rolebinding intern-view --role=intern-view --serviceaccount=som-shop:intern"
I=system:serviceaccount:som-shop:intern
x "kubectl $NS get deploy som-web -o yaml --as=$I | grep -m2 -o 'som:[a-z0-9]*@'"
x "kubectl $NS get sts som-db -o yaml --as=$I | grep -A1 POSTGRES_PASSWORD | head -2"
# create secret
x "kubectl $NS create secret generic som-db-secret --from-literal=POSTGRES_PASSWORD=meow1234 --from-literal=DATABASE_URL=postgres://som:meow1234@som-db-0.som-db:5432/catshop"
x "kubectl $NS apply --dry-run=client -f 05-secret.example.yaml -o yaml | head -3"
t0=$(date +%s)
x "kubectl apply -f 10-db.yaml"
kubectl $NS rollout status sts/som-db --timeout=120s; echo "db rollout $(( $(date +%s)-t0 ))s"
x "kubectl apply -f 20-web.yaml"
kubectl $NS rollout status deploy/som-web --timeout=240s >/dev/null; echo "web rollout $(( $(date +%s)-t0 ))s"; sleep 8
x curl -s localhost:30080/api/stats
x "kubectl $NS get deploy som-web -o yaml --as=$I | grep -c meow1234"
x "kubectl $NS get deploy som-web -o yaml --as=$I | grep -B1 -A3 secretKeyRef | head -6"
x "kubectl $NS get secret som-db-secret --as=$I"
x "kubectl $NS auth can-i create pods/exec --as=$I"
x "kubectl $NS exec deploy/som-web -c web --as=$I -- printenv DATABASE_URL"
# change password
x "kubectl $NS exec som-db-0 -- psql -U som -d catshop -c \"ALTER USER som PASSWORD 'purr5678';\""
sleep 15
x "for i in 1 2 3 4 5 6; do curl -s -o /dev/null -w '%{http_code} ' localhost:30080/api/stats; done; echo; curl -s localhost:30080/api/stats; curl -s localhost:30080/api/health"
x "kubectl $NS logs deploy/som-web -c web --tail=3"
x "kubectl $NS get pod -l app=som-web"
x "kubectl $NS create secret generic som-db-secret --from-literal=POSTGRES_PASSWORD=purr5678 --from-literal=DATABASE_URL=postgres://som:purr5678@som-db-0.som-db:5432/catshop --dry-run=client -o yaml | kubectl apply -f -"
x "kubectl $NS rollout restart deploy/som-web"
kubectl $NS rollout status deploy/som-web --timeout=240s >/dev/null; sleep 8
x curl -s localhost:30080/api/stats
x "curl -s -XPOST -H 'content-type: application/json' -d '{\"product_id\":2,\"qty\":1}' localhost:30080/api/orders"
x curl -s localhost:30080/api/stats
x "kubectl $NS delete pod som-db-0; kubectl $NS wait --for=condition=Ready pod/som-db-0 --timeout=120s"
sleep 5
x curl -s localhost:30080/api/stats
x "kubectl $NS exec som-db-0 -- psql -U som -d catshop -tAc 'select count(*) from orders'"
x "kubectl $NS exec som-db-0 -- sh -c 'PGPASSWORD=meow1234 psql -h 127.0.0.1 -U som -d catshop -c \"select 1\"'"
x "kubectl $NS exec som-db-0 -- sh -c 'PGPASSWORD=purr5678 psql -h 127.0.0.1 -U som -d catshop -tAc \"select 1\"'"
# TLS
cd /workspace/t
x "kubectl $NS create secret tls som-tls --cert=tls.crt --key=tls.key"
x "kubectl apply -f shop011/30-https.yaml"
kubectl $NS rollout status deploy/som-https --timeout=120s; sleep 5
x "curl -sk https://localhost:30082/api/stats"
x "curl -s --cacert tls.crt https://localhost:30082/api/shop"
x "curl -s https://localhost:30082/api/stats; echo rc=\$?"
