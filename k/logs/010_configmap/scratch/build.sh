set -e
cd /workspace/t/shop/app
docker build -q -t som-shop-web:1.4 --build-arg APP_VERSION=1.4 .
kind load docker-image som-shop-web:1.4 --name lab
docker pull -q postgres:17.11-alpine
docker save --platform linux/amd64 postgres:17.11-alpine -o /root/pg.tar
kind load image-archive /root/pg.tar --name lab
echo LOADED
