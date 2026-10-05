x(){ echo; echo "\$ $*"; bash -c "$*" 2>&1; echo "[rc=$?]"; }
cd /workspace/t/shop
x kubectl apply -f 00-namespace.yaml -f 10-db.yaml -f 15-config.yaml
kubectl -n som-shop rollout status sts/som-db --timeout=120s
x kubectl apply -f 20-web.yaml
x kubectl -n som-shop rollout status deploy/som-web --timeout=180s
for i in 1 2 3; do curl -s -XPOST -H 'content-type: application/json' -d '{"product_id":1,"qty":1}' localhost:30080/api/orders; echo; done
x curl -s localhost:30080/api/shop
x curl -s localhost:30080/api/announcement
x curl -s localhost:30080/api/stats
x "curl -s localhost:30080/ | grep -o '<title>[^<]*</title>'"
x "curl -s localhost:30080/ | grep -o 'class=\"theme-[a-z]*\"' | head -1"
x "curl -s localhost:30080/ | grep -o 'announcement\">[^<]*<' | head -1"
x "kubectl -n som-shop exec deploy/som-web -c web -- printenv SHOP_FOOTER"
