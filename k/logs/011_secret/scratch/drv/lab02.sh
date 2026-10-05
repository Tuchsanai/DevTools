R="../r.sh lab02"; D=labs/lab02-types
$R $D 'ls -la; od -c pw.txt'
$R $D 'kubectl create secret generic fromfile --from-file=db-password=pw.txt'
$R $D "kubectl get secret fromfile -o jsonpath='{.data}'; echo"
$R $D "echo meow1234 > pw-nl.txt; kubectl create secret generic fromfile-nl --from-file=db-password=pw-nl.txt; kubectl get secret fromfile-nl -o jsonpath='{.data}'; echo; kubectl get secret fromfile-nl -o jsonpath='{.data.db-password}' | base64 -d | od -c | head -2"
$R $D 'cat sd.yaml | grep -v "^#"'
$R $D 'kubectl apply -f sd.yaml'
$R $D 'kubectl get secret sd -o yaml'
$R $D "kubectl get secret sd -o jsonpath='{.data.PASSWORD}' | base64 -d; echo"
$R $D "kubectl get secret sd -o jsonpath='{.metadata.annotations.kubectl\.kubernetes\.io/last-applied-configuration}'"
$R $D "kubectl create secret generic viapipe --from-literal=PASSWORD=pipe-pass-01 --dry-run=client -o yaml | kubectl apply -f -"
$R $D "kubectl get secret viapipe -o jsonpath='{.metadata.annotations.kubectl\.kubernetes\.io/last-applied-configuration}'"
$R $D "kubectl create secret generic viass --from-literal=PASSWORD=ss-pass-01 --dry-run=client -o yaml | kubectl apply --server-side -f -; kubectl get secret viass -o jsonpath='{.metadata.annotations}'; echo '(ไม่มี annotation last-applied)'"
$R $D 'kubectl create secret generic onlypw --type=kubernetes.io/basic-auth --from-literal=password=meow1234; kubectl get secret onlypw'
$R $D 'kubectl create secret generic emptyba --type=kubernetes.io/basic-auth'
$R $D 'kubectl create secret generic ba --type=kubernetes.io/basic-auth --from-literal=username=som --from-literal=password=meow1234; kubectl get secret ba'
$R $D 'kubectl create secret generic badtls --type=kubernetes.io/tls --from-file=tls.crt=pw.txt'
$R $D 'kubectl create secret tls badtls2 --cert=pw.txt --key=pw.txt'
$R $D 'kubectl create secret docker-registry regcred --docker-server=registry.example.com --docker-username=som --docker-password=example-pass --docker-email=som@example.com; kubectl get secret regcred'
$R $D "kubectl get secret regcred -o jsonpath='{.data.\.dockerconfigjson}' | base64 -d; echo"
$R $D "echo c29tOmV4YW1wbGUtcGFzcw== | base64 -d; echo"
$R $D 'head -c 1100000 /dev/zero > big.bin; kubectl create secret generic huge --from-file=big.bin; rm -f big.bin'
$R $D 'kubectl get secret'
