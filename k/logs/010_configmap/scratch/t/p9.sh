x(){ echo; echo "\$ $*"; bash -c "$*" 2>&1; echo "[rc=$?]"; }
x "kubectl exec ngx -- curl -s 127.0.0.1/"
x "kubectl exec ngx -- nginx -s reload"; sleep 1
x "kubectl exec ngx -- curl -s 127.0.0.1/"
kubectl patch cm nginx-conf --type merge -p '{"data":{"default.conf":"server { listen 80; location / { default_type text/plain; return 200 \"menu v3\\n\"; } }\n"}}'
t0=$(date +%s); until kubectl exec ngx -- grep -q v3 /etc/nginx/conf.d/default.conf; do sleep 2; done; echo "file updated after $(( $(date +%s)-t0 ))s"
x "kubectl exec ngx -- curl -s 127.0.0.1/"
x "kubectl exec ngx -- nginx -s reload"; sleep 1
x "kubectl exec ngx -- curl -s 127.0.0.1/"
