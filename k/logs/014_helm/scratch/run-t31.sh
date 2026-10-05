cd /workspace/pc/final
mkdir -p auth
docker run --rm --entrypoint htpasswd httpd:2.4-alpine -Bbn som meow-registry-123 > auth/htpasswd 2>/dev/null; wc -c auth/htpasswd
docker run -d --name som-registry -p 5000:5000 -v $PWD/auth:/auth -e REGISTRY_AUTH=htpasswd -e REGISTRY_AUTH_HTPASSWD_REALM=som -e REGISTRY_AUTH_HTPASSWD_PATH=/auth/htpasswd registry:2 >/dev/null; sleep 3
docker ps --format '{{.Names}} {{.Image}} {{.Status}}' | grep registry
helm package charts/som-shop
ls -la som-shop-0.1.0.tgz; tar tzf som-shop-0.1.0.tgz | head -20
echo "=== push without login"
helm push som-shop-0.1.0.tgz oci://localhost:5000/charts --plain-http 2>&1 | tail -2
echo "=== login with URL (helm4 breaking?)"
echo meow-registry-123 | helm registry login http://localhost:5000 -u som --password-stdin --plain-http 2>&1 | tail -2
echo meow-registry-123 | helm registry login localhost:5000 -u som --password-stdin --plain-http 2>&1 | tail -2
helm push som-shop-0.1.0.tgz oci://localhost:5000/charts --plain-http 2>&1
helm show chart oci://localhost:5000/charts/som-shop --version 0.1.0 --plain-http 2>&1 | head -5
helm pull oci://localhost:5000/charts/som-shop --version 0.1.0 --plain-http -d /tmp/pulled 2>&1 | tail -2
curl -s -u som:meow-registry-123 localhost:5000/v2/charts/som-shop/tags/list; echo
