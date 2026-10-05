x(){ echo; echo "\$ $*"; bash -c "$*" 2>&1; echo "[rc=$?]"; }
cd /workspace/t
kubectl apply -f p8.yaml; kubectl wait --for=condition=Ready pod/ngx --timeout=120s
IP=$(kubectl get pod ngx -o jsonpath='{.status.podIP}')
x "kubectl exec ngx -- curl -s localhost/ || kubectl exec ngx -- wget -qO- localhost/"
kubectl patch cm nginx-conf --type merge -p '{"data":{"default.conf":"server { listen 80; location / { default_type text/plain; return 200 \"menu v2\\n\"; } }\n"}}'
t0=$(date +%s); until kubectl exec ngx -- grep -q v2 /etc/nginx/conf.d/default.conf; do sleep 2; done; echo "file updated after $(( $(date +%s)-t0 ))s"
x "kubectl exec ngx -- wget -qO- localhost/"
x "kubectl exec ngx -- nginx -s reload"
sleep 1
x "kubectl exec ngx -- wget -qO- localhost/"
# immutable in shop
cd /workspace/t/shop
x "kubectl -n som-shop create configmap som-web-config-v2 --from-literal=SHOP_NAME='ร้านน้องส้ม (v2)' --from-literal=APP_THEME=harbor --dry-run=client -o yaml > cmv2.yaml; sed -i 's/^kind: ConfigMap/immutable: true\nkind: ConfigMap/' cmv2.yaml; cat cmv2.yaml; kubectl apply -f cmv2.yaml"
x "kubectl -n som-shop patch deploy som-web --type json -p '[{\"op\":\"replace\",\"path\":\"/spec/template/spec/containers/0/envFrom/0/configMapRef/name\",\"value\":\"som-web-config-v2\"}]'"
kubectl -n som-shop rollout status deploy/som-web --timeout=180s >/dev/null; sleep 8
x curl -s localhost:30080/api/shop
x "kubectl -n som-shop edit cm som-web-config-v2 </dev/null; kubectl -n som-shop patch cm som-web-config-v2 --type merge -p '{\"data\":{\"SHOP_NAME\":\"x\"}}'"
x "kubectl -n som-shop rollout undo deploy/som-web"
kubectl -n som-shop rollout status deploy/som-web --timeout=180s >/dev/null; sleep 8
x curl -s localhost:30080/api/shop
x curl -s localhost:30080/api/stats
x "kubectl -n som-shop get cm som-web-config -o yaml | grep -n meow; kubectl -n som-shop get deploy som-web -o yaml | grep -n meow1234"
