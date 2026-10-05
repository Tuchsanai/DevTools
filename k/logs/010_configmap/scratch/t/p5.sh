x(){ echo; echo "\$ $*"; bash -c "$*" 2>&1; echo "[rc=$?]"; }
cd /workspace/t
x "kubectl exec optpod -- ls /etc/opt-cm"
x "kubectl create configmap frozen --from-literal=PRICE=99 --dry-run=client -o yaml | sed 's/^kind: ConfigMap/immutable: true\nkind: ConfigMap/' | kubectl apply -f -"
x kubectl get cm frozen -o yaml
x "kubectl patch cm frozen --type merge -p '{\"data\":{\"PRICE\":\"79\"}}'"
x "kubectl patch cm frozen --type merge -p '{\"immutable\":false}'"
x "kubectl label cm frozen tier=menu"
x "kubectl create configmap frozen --from-literal=PRICE=79 --dry-run=client -o yaml | kubectl apply -f -"
x "kubectl create configmap frozen --from-literal=PRICE=79 --dry-run=client -o yaml | kubectl replace -f -"
x kubectl delete cm frozen
x "kubectl kustomize kz"
x "kubectl apply -k kz"
x kubectl get cm -l '!x' 
kubectl rollout status deploy/kz-web --timeout=60s
x "kubectl get deploy kz-web -o jsonpath='{.spec.template.spec.containers[0].envFrom}'"
printf 'ประกาศ v2\n' > kz/announcement.txt
x "kubectl apply -k kz"
kubectl rollout status deploy/kz-web --timeout=60s
x "kubectl get cm | grep web-config"
x "kubectl rollout history deploy/kz-web"
x "kubectl exec deploy/kz-web -- printenv announcement.txt"
# rollout restart on plain deployment
x "kubectl create deployment plain --image=busybox:1.36 -- sleep 3600"
kubectl rollout status deploy/plain --timeout=60s
x "kubectl rollout restart deploy/plain"
kubectl rollout status deploy/plain --timeout=60s
x "kubectl get deploy plain -o jsonpath='{.spec.template.metadata.annotations}'"
x "kubectl patch deploy plain -p '{\"spec\":{\"template\":{\"metadata\":{\"annotations\":{\"checksum/config\":\"abc123\"}}}}}'"
x "kubectl rollout history deploy/plain"
# cross namespace
x kubectl create ns other
x "kubectl -n other run x --image=busybox:1.36 --restart=Never --overrides='{\"spec\":{\"containers\":[{\"name\":\"x\",\"image\":\"busybox:1.36\",\"command\":[\"sleep\",\"3600\"],\"envFrom\":[{\"configMapRef\":{\"name\":\"shop-config\"}}]}]}}'"
sleep 10
x "kubectl -n other get pod x; kubectl -n other describe pod x | grep -E 'Error|Warning' | tail -2"
x "kubectl explain pod.spec.volumes.configMap | grep -E '^  [a-z]'"
# RBAC
x kubectl create sa reader
x "kubectl create role cm-reader --verb=get,list --resource=configmaps"
x "kubectl create rolebinding reader-cm --role=cm-reader --serviceaccount=default:reader"
x "kubectl auth can-i get configmaps --as=system:serviceaccount:default:reader"
x "kubectl auth can-i update configmaps --as=system:serviceaccount:default:reader"
x "kubectl get cm shop-config --as=system:serviceaccount:default:reader -o jsonpath='{.data.SHOP_NAME}'"
x "kubectl patch cm shop-config --as=system:serviceaccount:default:reader --type merge -p '{\"data\":{\"a\":\"b\"}}'"
x "kubectl -n other get cm --as=system:serviceaccount:default:reader"
