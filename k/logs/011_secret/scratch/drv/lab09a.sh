R="../r.sh lab09"; D=som-shop-v7; NS="-n som-shop"
$R $D 'kubectl get ns som-shop 2>&1; kubectl get pv'
$R $D 'kubectl apply -f k8s-010/'
$R $D "time (kubectl $NS rollout status sts/som-db --timeout=180s && kubectl $NS rollout status deploy/som-web --timeout=240s)"
$R $D 'sleep 8; curl -s localhost:30080/api/stats; for p in 1 2 3; do curl -s -XPOST -H "content-type: application/json" -d "{\"product_id\":$p,\"qty\":1}" localhost:30080/api/orders; echo; done; curl -s localhost:30080/api/stats'
$R $D 'curl -s localhost:30080/api/shop; echo; curl -s localhost:30080/api/announcement'
$R $D "kubectl $NS rollout history deploy/som-web"
# A
$R $D 'kubectl apply -f rbac/intern.yaml'
$R $D './rbac/intern-context.sh'
$R $D 'kubectl config get-contexts; kubectl --context intern get pods'
$R $D "kubectl --context intern get deploy som-web -o yaml | grep -o 'som:[a-z0-9]*@'"
$R $D "kubectl --context intern get sts som-db -o yaml | grep -A1 POSTGRES_PASSWORD"
$R $D "kubectl --context intern get pod som-db-0 -o yaml | grep -A1 POSTGRES_PASSWORD"
$R $D "kubectl --context intern get secrets"
# B
$R $D "kubectl $NS create secret generic som-db-secret --from-literal=POSTGRES_PASSWORD=meow1234 --from-literal=DATABASE_URL=postgres://som:meow1234@som-db-0.som-db:5432/catshop"
$R $D "kubectl $NS get secret; kubectl $NS describe secret som-db-secret"
$R $D "kubectl $NS get secret som-db-secret -o jsonpath='{.metadata.annotations}'; echo '(ไม่มี last-applied)'"
$R $D "grep -v '^#' examples/05-secret.example.yaml; cat .gitignore"
$R $D "kubectl apply --dry-run=server -f examples/05-secret.example.yaml"
# C1
$R $D "kubectl $NS get pvc; kubectl $NS get pod som-db-0 -o jsonpath='{.metadata.uid}'; echo"
$R $D "kubectl apply -f k8s/10-db.yaml && time kubectl $NS rollout status sts/som-db --timeout=180s"
$R $D "kubectl $NS get pod som-db-0; kubectl $NS get pvc; sleep 5; curl -s localhost:30080/api/stats"
$R $D "kubectl --context intern get sts som-db -o yaml | grep -A4 'name: POSTGRES_PASSWORD'"
# C2
$R $D "kubectl apply -f k8s/15-config.yaml -f k8s/20-web.yaml && time kubectl $NS rollout status deploy/som-web --timeout=240s"
$R $D 'sleep 8; curl -s localhost:30080/api/stats; ./hit.sh http://localhost:30080/api/stats 12 0.1'
$R $D 'curl -s localhost:30080/api/shop; echo'
$R $D "kubectl $NS rollout history deploy/som-web"
$R $D "kubectl --context intern get deploy som-web -o yaml | grep -c meow1234"
$R $D "kubectl --context intern get deploy som-web -o yaml | grep -B1 -A3 secretKeyRef"
$R $D "kubectl --context intern get secret som-db-secret"
$R $D "kubectl --context intern describe secret som-db-secret"
$R $D "kubectl --context intern auth can-i get secrets; kubectl --context intern auth can-i create pods/exec; kubectl --context intern auth can-i get pods/log"
$R $D "kubectl --context intern exec deploy/som-web -c web -- printenv DATABASE_URL"
$R $D "kubectl --context intern logs deploy/som-web -c db-seed | tail -3"
