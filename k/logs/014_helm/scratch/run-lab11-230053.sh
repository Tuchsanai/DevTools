set -v
cd /workspace/014_kubernetes_helm/02_LAB/labs/lab11-registry
mkdir -p auth
docker run --rm --entrypoint htpasswd httpd:2.4-alpine -Bbn som meow-registry-123 > auth/htpasswd
cut -c1-8 auth/htpasswd
docker run -d --name som-registry -p 5000:5000 -v $PWD/auth:/auth -e REGISTRY_AUTH=htpasswd -e REGISTRY_AUTH_HTPASSWD_REALM=som -e REGISTRY_AUTH_HTPASSWD_PATH=/auth/htpasswd registry:2 | cut -c1-12
sleep 3; docker ps --filter name=som-registry --format '{{.Names}} {{.Image}} {{.Status}} {{.Ports}}'
curl -s -o /dev/null -w "%{http_code}\n" localhost:5000/v2/
helm package ../../charts/som-shop
ls -l som-shop-0.1.0.tgz; tar tzf som-shop-0.1.0.tgz | head -20
echo "=== push ก่อน login"
helm push som-shop-0.1.0.tgz oci://localhost:5000/charts --plain-http 2>&1 | tail -1
echo "=== login ด้วย URL (ผิด) แล้วด้วยชื่อโฮสต์"
echo meow-registry-123 | helm registry login http://localhost:5000 -u som --password-stdin --plain-http 2>&1 | tail -1
echo meow-registry-123 | helm registry login localhost:5000 -u som --password-stdin --plain-http
python3 -c 'import json; d=json.load(open("/root/.config/helm/registry/config.json")); print({k:{kk:(vv[:6]+"...") for kk,vv in v.items()} for k,v in d["auths"].items()})'
helm push som-shop-0.1.0.tgz oci://localhost:5000/charts --plain-http
helm show chart oci://localhost:5000/charts/som-shop --version 0.1.0 --plain-http 2>&1 | grep -E "^(name|version|appVersion|Pulled|Digest)"
mkdir -p pulled && helm pull oci://localhost:5000/charts/som-shop --version 0.1.0 --plain-http -d pulled --untar 2>&1 | tail -2; ls pulled/som-shop
echo "=== ติดตั้งจากโกดัง"
time helm install oci-som oci://localhost:5000/charts/som-shop --version 0.1.0 --plain-http -n oci-demo --create-namespace --set fullnameOverride=som --set db.password=meow1234 --set ingress.enabled=true --set ingress.host=oci.shop.localhost --set web.replicas=1 --wait 2>&1 | grep -vE "^\s*$" | head -12
curl -s http://oci.shop.localhost:30080/api/whoami; echo
helm list -n oci-demo
DIG=$(helm show chart oci://localhost:5000/charts/som-shop --version 0.1.0 --plain-http 2>&1 | grep -oE "sha256:[0-9a-f]+" | head -1); echo "digest=${DIG:0:19}..."
helm template x oci://localhost:5000/charts/som-shop@$DIG --plain-http --set db.password=x 2>&1 | grep -E "^kind:|Pulled|Digest" | head -4
echo "=== logout แล้วดึงอีก"
helm registry logout localhost:5000
helm pull oci://localhost:5000/charts/som-shop --version 0.1.0 --plain-http -d /root 2>&1 | tail -1
echo "=== เก็บกวาด"
helm uninstall oci-som -n oci-demo; kubectl delete ns oci-demo
docker rm -f som-registry
rm -f som-shop-0.1.0.tgz
