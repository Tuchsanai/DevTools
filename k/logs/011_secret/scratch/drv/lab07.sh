R="../r.sh lab07"; D=labs/lab07-rbac
I=system:serviceaccount:default:intern; M=system:serviceaccount:default:maker
$R $D 'kubectl apply -f intern.yaml'
$R $D "for r in pods configmaps secrets; do echo \"get \$r: \$(kubectl auth can-i get \$r --as=$I)\"; done; echo \"list secrets: \$(kubectl auth can-i list secrets --as=$I)\""
$R $D "kubectl get pods --as=$I"
$R $D "kubectl get secret demo --as=$I"
$R $D "kubectl get secrets --as=$I"
$R $D "kubectl describe secret demo --as=$I"
$R $D "kubectl get pod spod -o yaml --as=$I | grep -B2 -A3 secretKeyRef"
$R $D "kubectl exec spod --as=$I -- printenv DB_PASSWORD"
$R $D "kubectl auth can-i --list --as=$I"
$R $D 'kubectl apply -f maker.yaml'
$R $D "kubectl auth can-i get secrets --as=$M; kubectl auth can-i create pods --as=$M"
$R $D "kubectl get secret demo --as=$M"
$R $D "kubectl apply -f peek.yaml --as=$M; sleep 12; kubectl get pod peek --as=$M"
$R $D "kubectl logs peek --as=$M"
$R $D "kubectl delete pod peek --as=$M"
