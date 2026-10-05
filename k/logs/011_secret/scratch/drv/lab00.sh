R="../r.sh lab00"
$R . 'kubectl get nodes'
$R . 'kubectl version'
$R . 'kubectl get sc; kubectl get pv,pvc -A; kubectl get secret -A; kubectl get svc -A | grep 3008 || echo "ไม่มี NodePort 3008x ค้าง"'
$R . 'ls; ls labs som-shop-v7'
$R . 'time (docker pull -q postgres:17.11-alpine && docker save --platform linux/amd64 postgres:17.11-alpine -o /root/postgres.tar && kind load image-archive /root/postgres.tar --name lab)'
$R som-shop-v7 'time (docker build -q -t som-shop-web:1.5 --build-arg APP_VERSION=1.5 app && kind load docker-image som-shop-web:1.5 --name lab)'
$R . 'for n in lab-worker lab-worker2; do echo "== $n"; docker exec $n crictl images | grep -E "som-shop|postgres"; done'
$R . 'which openssl; openssl version; which htpasswd strings xxd hexdump || true'
