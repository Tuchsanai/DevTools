cd /workspace/pc
t0=$(date +%s)
docker build -q -t som-shop-web:1.7 --build-arg APP_VERSION=1.7 app && kind load docker-image som-shop-web:1.7 --name lab
t1=$(date +%s); echo "build+load 1.7: $((t1-t0))s"
docker build -q -t som-shop-web:1.8 --build-arg APP_VERSION=1.8 app && kind load docker-image som-shop-web:1.8 --name lab
t2=$(date +%s); echo "build+load 1.8: $((t2-t1))s"
docker pull -q postgres:17.11-alpine && docker save --platform linux/amd64 postgres:17.11-alpine -o /root/postgres.tar && kind load image-archive /root/postgres.tar --name lab; rm -f /root/postgres.tar
echo "postgres loaded: $(( $(date +%s)-t2 ))s"
