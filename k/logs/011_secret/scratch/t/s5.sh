x(){ echo; echo "\$ $*"; bash -c "$*" 2>&1; echo "[rc=$?]"; }
kubectl create ns reg2
x "kubectl -n reg2 run cached --image=kind-registry:5000/som-shop-web:1.4 --restart=Never --overrides='{\"spec\":{\"nodeName\":\"lab-worker\"}}' --command -- sleep 600"
sleep 15
x "kubectl -n reg2 get pod cached; kubectl -n reg2 describe pod cached | grep -E 'Failed|Pulled|already' | tail -3"
x "docker exec lab-worker grep -i -E 'ensureSecret|imagePullCredentialsVerificationPolicy' /var/lib/kubelet/config.yaml"
