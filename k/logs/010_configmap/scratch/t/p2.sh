x(){ echo; echo "\$ $*"; bash -c "$*" 2>&1; echo "[rc=$?]"; }
cd /workspace/t
kubectl apply -f p2.yaml
kubectl wait --for=condition=Ready pod/envpod pod/volpod --timeout=120s
x kubectl logs envpod
x "kubectl get events --field-selector involvedObject.name=envpod | grep -i -E 'invalid|warn'"
x "kubectl exec volpod -- ls -la /etc/all"
x "kubectl exec volpod -- ls -laR /etc/some"
x "kubectl exec volpod -- cat /etc/som/announcement.txt"
x "kubectl exec volpod -- mount | grep -E 'etc/(all|some|som)'"
x "kubectl exec volpod -- sh -c 'echo hack > /etc/all/menu.txt'"
x "kubectl exec volpod -- id"
