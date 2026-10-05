x(){ echo; echo "\$ $*"; bash -c "$*" 2>&1; echo "[rc=$?]"; }
NS="-n som-shop"
kubectl delete ns reg reg2 --wait=true >/dev/null
docker exec lab-worker crictl rmi kind-registry:5000/som-shop-web:1.4 >/dev/null 2>&1
docker exec lab-worker sh -c 'rm -f /var/lib/kubelet/image_manager/pulled/sha256-068465*; systemctl restart kubelet'
docker save som-shop-web:1.4 -o /root/web14.tar && kind load image-archive /root/web14.tar --name lab
sleep 15
kubectl $NS delete pod -l app=som-web --field-selector=status.phase=Pending
t0=$(date +%s); kubectl $NS rollout status deploy/som-web --timeout=240s | tail -1; echo "rollout $(( $(date +%s)-t0 ))s"; sleep 8
x "kubectl $NS get pod"
x "for i in 1 2 3 4 5 6; do curl -s localhost:30080/api/stats; done | sort | uniq -c"
x "curl -sk https://localhost:30082/api/stats"
