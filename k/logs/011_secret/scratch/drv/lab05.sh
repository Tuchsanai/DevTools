R="../r.sh lab05"; D=labs/lab05-registry
$R $D 'ls; docker network ls | grep kind'
$R $D './setup-registry.sh'
$R $D 'curl -s -u som:example-pass http://localhost:5001/v2/_catalog; curl -s -u som:example-pass http://localhost:5001/v2/som-menu/tags/list'
$R $D 'docker exec lab-worker cat /etc/containerd/certs.d/kind-registry:5000/hosts.toml'
$R $D 'kubectl apply -f 00-ns.yaml -f 1-nopull.yaml; sleep 20; kubectl -n reg get pod nopull'
$R $D "kubectl -n reg describe pod nopull | grep -E 'Failed|BackOff' | tail -3"
$R $D 'kubectl -n reg create secret docker-registry regcred --docker-server=kind-registry:5000 --docker-username=som --docker-password=example-pass; kubectl -n reg get secret regcred'
$R $D 'kubectl apply -f 2-withpull.yaml; kubectl -n reg wait --for=condition=Ready pod/withpull --timeout=90s; kubectl -n reg get pod withpull -o wide'
$R $D "kubectl -n reg describe pod withpull | grep -E 'Pulling|Pulled' ; kubectl -n reg logs withpull"
$R $D 'kubectl -n reg create secret docker-registry wrongcred --docker-server=kind-registry:5000 --docker-username=som --docker-password=wrong-pass; kubectl apply -f 3-wrong.yaml; sleep 20; kubectl -n reg get pod wrong'
$R $D "kubectl -n reg describe pod wrong | grep -E 'Failed' | tail -3"
$R $D "kubectl -n reg patch sa default -p '{\"imagePullSecrets\":[{\"name\":\"regcred\"}]}'; kubectl -n reg get sa default -o yaml | grep -A1 imagePullSecrets"
$R $D "kubectl apply -f 4-viasa.yaml; kubectl -n reg wait --for=condition=Ready pod/viasa --timeout=90s; kubectl -n reg get pod viasa -o jsonpath='{.spec.imagePullSecrets}{\"  \"}{.status.phase}{\"  \"}{.spec.nodeName}'; echo"
$R $D 'kubectl apply -f 5-cached.yaml; sleep 20; kubectl -n reg2 get pod cached -o wide'
$R $D "kubectl -n reg2 describe pod cached | grep -E 'Failed|Pulled|already|Pulling' | tail -4"
$R $D 'docker exec lab-worker crictl images | grep -E "som-menu|som-shop|IMAGE"'
$R $D 'kubectl -n reg2 run shopcheck --image=som-shop-web:1.5 --image-pull-policy=IfNotPresent --restart=Never --overrides='"'"'{"spec":{"nodeName":"lab-worker"}}'"'"' --command -- node -e "console.log(\"som-shop-web:1.5 ok\")"; sleep 10; kubectl -n reg2 get pod shopcheck; kubectl -n reg2 logs shopcheck'
$R $D 'kubectl get pod -A -o wide | grep -E "reg|NAME"'
$R $D './cleanup-registry.sh'
$R $D 'docker ps -a | grep kind-registry || echo "ไม่มี kind-registry แล้ว"; ls'
