x(){ echo; echo "\$ $*"; bash -c "$*" 2>&1; echo "[rc=$?]"; }
cd /workspace/t
kubectl apply -f p3.yaml; sleep 25
x kubectl get pod nocm nokey optpod novol
x "kubectl describe pod nocm | sed -n '/State:/,/Ready:/p;/Events:/,\$p'"
x "kubectl describe pod nokey | sed -n '/Events:/,\$p'"
x "kubectl describe pod novol | sed -n '/Events:/,\$p'"
x kubectl logs optpod
x kubectl create configmap not-here --from-literal=HELLO=world
sleep 20
x kubectl get pod nocm novol optpod
x "kubectl exec optpod -- ls /etc/opt-cm; kubectl exec optpod -- printenv HELLO"
