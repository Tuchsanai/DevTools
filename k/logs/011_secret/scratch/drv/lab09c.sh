R="../r.sh lab09"; D=som-shop-v7; NS="-n som-shop"
# E
$R $D "kubectl $NS create secret tls som-tls --cert=../labs/lab04-tls/tls.crt --key=../labs/lab04-tls/tls.key; kubectl $NS get secret"
$R $D "kubectl apply -f k8s/30-https.yaml && kubectl $NS rollout status deploy/som-https --timeout=120s"
$R $D 'sleep 5; curl -sk https://localhost:30082/api/stats'
$R $D 'curl -s --cacert ../labs/lab04-tls/tls.crt https://localhost:30082/api/shop; echo'
$R $D 'curl -sS https://localhost:30082/api/stats; echo "rc=$?"'
$R $D 'curl -sk -XPOST -H "content-type: application/json" -d "{\"product_id\":5,\"qty\":1}" https://localhost:30082/api/orders; echo; curl -sk https://localhost:30082/api/stats'
$R $D 'curl -sk -o /dev/null -w "%{http_code} %{content_type}\n" https://localhost:30082/'
$R $D "kubectl $NS exec deploy/som-https -- ls -laL /etc/nginx/tls"
$R $D "kubectl apply -f extra/30-https-restricted.yaml && kubectl $NS rollout status deploy/som-https --timeout=120s"
$R $D "sleep 5; curl -sk https://localhost:30082/api/stats; kubectl $NS exec deploy/som-https -- sh -c 'id; ls -laL /etc/nginx/tls'"
$R $D "kubectl apply -f k8s/30-https.yaml && kubectl $NS rollout status deploy/som-https --timeout=120s; sleep 5; curl -sk https://localhost:30082/api/stats"
# F
$R $D "../labs/lab08-etcd/etcdget.sh /registry/secrets/som-shop/som-db-secret | grep -a -o 'postgres://[^@]*@'"
# สภาพสุดท้าย
$R $D "kubectl apply -f k8s/ 2>&1; kubectl $NS get all,secret,cm,pvc"
$R $D "kubectl --context intern get secrets; kubectl --context intern get deploy som-web -o yaml | grep -c -E 'meow1234|purr5678'"
$R $D 'curl -s localhost:30080/api/stats; curl -sk https://localhost:30082/api/stats'
