set -v
# จำลองสภาพท้ายบท 013 ตามเส้นทางที่นักศึกษาทำจริง (บท 012 LAB 0/1/10 ทางคลัสเตอร์ใหม่ → บท 013 LAB 0/1/11)
# --- บท 012 LAB 0: image
cd /workspace/012_kubernetes_ingress/02_LAB
time (docker pull -q postgres:17.11-alpine && docker save --platform linux/amd64 postgres:17.11-alpine -o /root/postgres.tar && kind load image-archive /root/postgres.tar --name lab; rm -f /root/postgres.tar)
cd som-shop-v8
time (docker build -q -t som-shop-web:1.5 --build-arg APP_VERSION=1.5 app && kind load docker-image som-shop-web:1.5 --name lab)
time (docker build -q -t som-shop-web:1.6 --build-arg APP_VERSION=1.6 app && kind load docker-image som-shop-web:1.6 --name lab)
# --- บท 012 LAB 1: Traefik static
cd ..
kubectl apply -f ingress-controller/traefik-crds-v3.7.13.yml | tail -2
kubectl apply -f ingress-controller/00-traefik.yaml
kubectl -n traefik rollout status deploy/traefik --timeout=180s
# --- บท 012 LAB 10 (ทางคลัสเตอร์ใหม่)
cd som-shop-v8
kubectl apply -f k8s/00-namespace.yaml
kubectl -n som-shop create secret generic som-db-secret --from-literal=POSTGRES_PASSWORD=meow1234 --from-literal=DATABASE_URL=postgres://som:meow1234@som-db-0.som-db:5432/catshop
kubectl apply -f k8s/00-namespace.yaml -f k8s/10-db.yaml -f k8s/15-config.yaml -f k8s/20-web.yaml
kubectl -n som-shop rollout status sts/som-db --timeout=240s && kubectl -n som-shop rollout status deploy/som-web --timeout=300s
openssl req -x509 -nodes -newkey rsa:2048 -days 365 -keyout tls.key -out tls.crt -subj '/CN=shop.localhost' -addext 'subjectAltName=DNS:shop.localhost,DNS:admin.localhost,DNS:localhost' 2>&1 | tail -1
kubectl -n som-shop create secret tls som-tls --cert=tls.crt --key=tls.key --dry-run=client -o yaml | kubectl apply -f -
kubectl -n som-shop create secret generic som-admin-auth --type=kubernetes.io/basic-auth --from-literal=username=som --from-literal=password=meow-admin-123
kubectl apply -f k8s/40-admin.yaml -f k8s/50-ingress.yaml
kubectl -n som-shop rollout status deploy/som-admin --timeout=120s
sleep 3
for i in 1 2 3; do curl -s --cacert tls.crt -XPOST -H "content-type: application/json" -d '{"productId":4,"qty":1}' https://shop.localhost:30081/api/orders; echo; done
kubectl -n som-shop annotate deploy/som-web kubernetes.io/change-cause="1.5 หน้าร้านผ่าน Ingress" --overwrite
kubectl -n som-shop rollout restart deploy/som-web && kubectl -n som-shop rollout status deploy/som-web --timeout=120s
kubectl -n som-shop set image deploy/som-web web=som-shop-web:1.6 && kubectl -n som-shop annotate deploy/som-web kubernetes.io/change-cause="1.6 ผ่าน Ingress" --overwrite
kubectl -n som-shop rollout status deploy/som-web --timeout=120s
# --- บท 013 LAB 0/1: image 1.7 + metrics-server static
cd /workspace/013_kubernetes_hpa/02_LAB
kubectl apply -f metrics-server/00-metrics-server.yaml | tail -3
cd som-shop-v9
time (docker build -q -t som-shop-web:1.7 --build-arg APP_VERSION=1.7 app && kind load docker-image som-shop-web:1.7 --name lab)
kubectl -n kube-system rollout status deploy/metrics-server --timeout=180s
# --- บท 013 LAB 11 ขั้น B/C/D/H
kubectl apply -f k8s/60-hpa.yaml
until [ "$(kubectl -n som-shop get deploy som-web -o jsonpath={.spec.replicas})" = 2 ]; do sleep 3; done
kubectl apply set-last-applied -f k8s/20-web.yaml
kubectl apply -f k8s/15-config.yaml -f k8s/20-web.yaml
kubectl -n som-shop rollout status deploy/som-web --timeout=180s
kubectl apply -f k8s/70-customers.yaml
kubectl -n som-shop scale deploy/customers --replicas=1
sleep 60; kubectl -n som-shop get hpa
kubectl -n som-shop scale deploy/customers --replicas=0
# --- สภาพท้ายบท 013
kubectl -n som-shop get deploy,sts,hpa,ing,middleware,secret
kubectl -n som-shop rollout history deploy/som-web
curl -sk https://shop.localhost:30081/api/stats; echo
