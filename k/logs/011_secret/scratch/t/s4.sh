x(){ echo; echo "\$ $*"; bash -c "$*" 2>&1; echo "[rc=$?]"; }
kubectl create ns reg
x "kubectl -n reg run nopull --image=kind-registry:5000/som-shop-web:1.4 --restart=Never --command -- sleep 600"
sleep 15
x "kubectl -n reg get pod nopull; kubectl -n reg describe pod nopull | grep -E 'Failed|BackOff' | tail -3"
x "kubectl -n reg create secret docker-registry regcred --docker-server=kind-registry:5000 --docker-username=som --docker-password=example-pass"
x "kubectl -n reg run withpull --image=kind-registry:5000/som-shop-web:1.4 --restart=Never --overrides='{\"spec\":{\"imagePullSecrets\":[{\"name\":\"regcred\"}]}}' --command -- sleep 600"
sleep 20
x "kubectl -n reg get pod withpull -o wide; kubectl -n reg describe pod withpull | grep -E 'Pulled|Pulling' | tail -2"
x "kubectl -n reg patch sa default -p '{\"imagePullSecrets\":[{\"name\":\"regcred\"}]}'"
x "kubectl -n reg run viasa --image=kind-registry:5000/som-shop-web:1.4 --restart=Never --command -- sleep 600"
sleep 15
x "kubectl -n reg get pod viasa -o jsonpath='{.spec.imagePullSecrets}{\"  \"}{.status.phase}'"
x "kubectl -n reg create secret docker-registry wrongcred --docker-server=kind-registry:5000 --docker-username=som --docker-password=wrong"
x "kubectl -n reg run wrong --image=kind-registry:5000/som-shop-web:1.4 --image-pull-policy=Always --restart=Never --overrides='{\"spec\":{\"imagePullSecrets\":[{\"name\":\"wrongcred\"}]}}' --command -- sleep 600"
sleep 15
x "kubectl -n reg describe pod wrong | grep -E 'Failed' | tail -2"
