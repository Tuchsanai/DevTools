R="../r.sh lab08"; D=labs/lab08-etcd
$R $D 'kubectl -n kube-system get pod -l component=etcd'
$R $D './etcdget.sh --keys /registry/secrets/default/'
$R $D "./etcdget.sh /registry/secrets/default/demo | grep -a -o 'newpass-01'"
$R $D "./etcdget.sh /registry/secrets/default/demo | head -c 400 | cat -v; echo"
$R $D "./etcdget.sh /registry/configmaps/default/shop-board | grep -a -o 'วันนี้ปลาทูสดมาก'"
$R $D 'docker exec lab-control-plane grep -n encryption /etc/kubernetes/manifests/kube-apiserver.yaml; echo "rc=$?"'
$R $D 'docker exec lab-control-plane grep -n -E "etcd-servers|secure-port" /etc/kubernetes/manifests/kube-apiserver.yaml'
# เก็บกวาด LAB 1–8 (namespace default)
$R . 'kubectl delete pod spod proj ngx-tls --wait=true; kubectl delete svc ngx-tls; kubectl delete cm ngx-tls-conf shop-board; kubectl delete secret demo demo2 sd fromfile fromfile-nl viapipe viass onlypw ba regcred shop-tls frozen builder-token --ignore-not-found; kubectl delete -f labs/lab07-rbac/intern.yaml -f labs/lab07-rbac/maker.yaml -f labs/lab06-projected/builder-token.yaml --ignore-not-found; kubectl get all,secret,cm,sa,role,rolebinding'
