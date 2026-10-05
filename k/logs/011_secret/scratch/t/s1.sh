x(){ echo; echo "\$ $*"; bash -c "$*" 2>&1; echo "[rc=$?]"; }
cd /workspace/t
x "which openssl htpasswd; openssl version"
x "kubectl create secret generic demo --from-literal=username=som --from-literal=password=meow1234"
x "kubectl get secret demo -o yaml"
x "kubectl get secret demo -o jsonpath='{.data.password}' | base64 -d; echo"
x "echo -n meow1234 | base64; echo bWVvdzEyMzQ= | base64 -d; echo"
x "echo meow1234 | base64"
x kubectl describe secret demo
x "kubectl get secret demo"
x "kubectl get secret demo -o go-template='{{range \$k,\$v := .data}}{{\$k}}={{\$v|base64decode}}{{\"\\n\"}}{{end}}'"
x "kubectl create secret generic demo2 --from-literal=password=meow1234 --dry-run=client -o yaml"
printf 'meow1234' > pw.txt
x "kubectl create secret generic fromfile --from-file=db-password=pw.txt; kubectl get secret fromfile -o jsonpath='{.data}'"
x "kubectl create secret generic bad --from-literal=password=meow1234 --type=kubernetes.io/basic-auth"
x "kubectl create secret generic ba --from-literal=username=som --from-literal=password=meow1234 --type=kubernetes.io/basic-auth; kubectl get secret ba"
x "kubectl create secret docker-registry regcred --docker-server=registry.example.com --docker-username=som --docker-password=example-pass --docker-email=som@example.com; kubectl get secret regcred"
x "kubectl get secret regcred -o jsonpath='{.data.\\.dockerconfigjson}' | base64 -d; echo"
x kubectl apply -f s1.yaml
x "kubectl get secret sd -o yaml | grep -v -E 'creation|uid|resourceVersion'"
kubectl wait --for=condition=Ready pod/spod --timeout=90s
x "kubectl exec spod -- env | grep -E 'DB_|SD_'"
x "kubectl exec spod -- ls -la /etc/secret /etc/secret400/..data/"
x "kubectl exec spod -- mount | grep secret"
x "kubectl exec spod -- cat /etc/secret/password; echo"
x "kubectl exec spod -- cat /proc/1/environ | tr '\0' '\n' | grep DB_"
x "kubectl get secret"
x "kubectl create secret generic huge --from-file=big=/workspace/t/cm/big.txt"
x "kubectl explain secret.type"
