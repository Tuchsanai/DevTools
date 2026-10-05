x(){ echo; echo "\$ $*"; bash -c "$*" 2>&1; echo "[rc=$?]"; }
set -x
mkdir -p /workspace/t/reg/auth && cd /workspace/t/reg
docker run --rm --entrypoint htpasswd httpd:2.4-alpine -Bbn som example-pass > auth/htpasswd
cat auth/htpasswd | cut -c1-10
docker run -d --restart=always --name kind-registry --network kind -p 127.0.0.1:5001:5000 \
  -v /workspace/t/reg/auth:/auth -e REGISTRY_AUTH=htpasswd -e REGISTRY_AUTH_HTPASSWD_REALM=som \
  -e REGISTRY_AUTH_HTPASSWD_PATH=/auth/htpasswd registry:2
sleep 3
curl -s -o /dev/null -w '%{http_code}\n' http://localhost:5001/v2/
echo example-pass | docker login localhost:5001 -u som --password-stdin
docker tag som-shop-web:1.4 localhost:5001/som-shop-web:1.4 && docker push -q localhost:5001/som-shop-web:1.4
for n in lab-control-plane lab-worker lab-worker2; do
  docker exec $n mkdir -p /etc/containerd/certs.d/kind-registry:5000
  printf '[host."http://kind-registry:5000"]\n  capabilities = ["pull", "resolve"]\n' | docker exec -i $n tee /etc/containerd/certs.d/kind-registry:5000/hosts.toml >/dev/null
done
docker exec lab-worker crictl pull kind-registry:5000/som-shop-web:1.4 2>&1 | tail -2
docker exec lab-worker crictl pull --creds som:example-pass kind-registry:5000/som-shop-web:1.4 2>&1 | tail -2
docker exec lab-worker crictl rmi kind-registry:5000/som-shop-web:1.4 2>&1 | tail -1
docker logout localhost:5001
