x(){ echo; echo "\$ $*"; bash -c "$*" 2>&1; echo "[rc=$?]"; }
cd /workspace/t
x "openssl req -x509 -nodes -newkey rsa:2048 -days 365 -keyout tls.key -out tls.crt -subj '/CN=shop.som.local' -addext 'subjectAltName=DNS:shop.som.local,DNS:localhost' 2>&1 | tail -1; ls -la tls.*"
x "kubectl create secret tls shop-tls --cert=tls.crt --key=tls.key; kubectl get secret shop-tls; kubectl describe secret shop-tls | tail -4"
x "kubectl create secret tls badtls --cert=tls.crt --key=pw.txt"
x "kubectl create secret generic badtls2 --type=kubernetes.io/tls --from-file=tls.crt"
x "kubectl create secret generic emptyba --type=kubernetes.io/basic-auth"
x kubectl apply -f tls.yaml
kubectl wait --for=condition=Ready pod/ngx-tls pod/proj --timeout=120s
x "curl -s https://localhost:30081/"
x "curl -sk https://localhost:30081/"
x "curl -s http://localhost:30081/ | head -3"
x "curl -skv https://localhost:30081/ 2>&1 | grep -E 'subject:|issuer:|SSL connection'"
x "kubectl exec ngx-tls -- ls -laL /etc/nginx/tls"
x "kubectl exec proj -- ls -laLR /etc/som"
x "kubectl exec proj -- cat /etc/som/pod-name /etc/som/db/password; echo"
# SA token secret
x kubectl create sa builder
x "cat <<Y | kubectl apply -f -
apiVersion: v1
kind: Secret
metadata:
  name: builder-token
  annotations: {kubernetes.io/service-account.name: builder}
type: kubernetes.io/service-account-token
Y"
sleep 3
x "kubectl get secret builder-token; kubectl describe secret builder-token | grep -E '^(ca.crt|namespace|token)'"
x "kubectl get sa builder -o yaml | grep -A3 secrets"
x "kubectl create token builder --duration=10m | cut -c1-20"
# immutable secret
x "kubectl create secret generic frozen --from-literal=k=v --dry-run=client -o yaml | sed 's/^kind: Secret/immutable: true\nkind: Secret/' | kubectl apply -f -"
x "kubectl patch secret frozen --type merge -p '{\"stringData\":{\"k\":\"v2\"}}'"
# secret volume update timing + env
kubectl patch secret demo --type merge -p '{"stringData":{"password":"newpass-01"}}'
t0=$(date +%s); until [ "$(kubectl exec spod -- cat /etc/secret/password)" = newpass-01 ]; do sleep 2; [ $(( $(date +%s)-t0 )) -gt 180 ] && break; done
echo "secret volume updated after $(( $(date +%s)-t0 ))s; env DB_PASSWORD=$(kubectl exec spod -- printenv DB_PASSWORD)"
