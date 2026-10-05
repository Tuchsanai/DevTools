R="../r.sh lab03"; D=labs/lab03-use
$R $D 'kubectl apply -f spod.yaml && kubectl wait --for=condition=Ready pod/spod --timeout=120s'
$R $D "kubectl exec spod -- env | grep -E 'DB_|SD_'"
$R $D 'kubectl exec spod -- ls -la /etc/secret /etc/secret400/..data/'
$R $D 'kubectl exec spod -- ls -laL /etc/secret400'
$R $D 'kubectl exec spod -- mount | grep -E "secret|serviceaccount"'
$R $D 'kubectl exec spod -- cat /etc/secret/password; echo'
$R $D "kubectl exec spod -- cat /proc/1/environ | tr '\0' '\n' | grep DB_"
$R $D 'kubectl exec spod -- sh -c "echo hack > /etc/secret/password"'
$R $D './wait-secret.sh newpass-00'
$R $D './wait-secret.sh newpass-01'
$R $D 'kubectl delete pod spod --wait=true; kubectl apply -f spod.yaml && kubectl wait --for=condition=Ready pod/spod --timeout=120s && kubectl exec spod -- printenv DB_PASSWORD'
$R $D 'kubectl apply -f frozen.yaml; kubectl get secret frozen'
$R $D "kubectl patch secret frozen --type merge -p '{\"stringData\":{\"API_KEY\":\"example-key-v2\"}}'"
$R $D "kubectl patch secret frozen --type merge -p '{\"immutable\":false}'"
$R $D 'kubectl delete secret frozen && sed "s/example-key-v1/example-key-v2/" frozen.yaml | kubectl apply -f - && kubectl get secret frozen -o jsonpath="{.data.API_KEY}" | base64 -d; echo'
