h() { printf '%-34s -> ' "$1 $2"; curl -s -o /tmp/b -w '%{http_code}' -H "Host: $1" "localhost:30080$2"; echo " $(grep -m1 -o 'Name: .*' /tmp/b || head -c 40 /tmp/b) $(grep -m1 '^GET' /tmp/b)"; }
kubectl get ing -n demo
kubectl get ing shop -n demo -o jsonpath='{.spec.ingressClassName}{"\n"}'
for p in / /order /api /api/ /api/stats /apix /API /admin /admin/x; do h shop.localhost $p; done
h admin.localhost /; h admin.localhost /api; h other.localhost /; h '' /
for p in /api /api/ /api/x /apix /docs /docs/ /docs/a /docsx /menu /menu/ /menux /impl /impl/ /impl/x /implx; do h paths.localhost $p; done
echo "--- real name resolution (curl built-in *.localhost)"; curl -s http://shop.localhost:30080/api/x | grep -E 'Name|Host:|GET'
curl -s http://admin.localhost:30080/ | grep -E 'Name|Host:'
