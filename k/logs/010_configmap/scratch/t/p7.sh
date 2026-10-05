x(){ echo; echo "\$ $*"; bash -c "$*" 2>&1; echo "[rc=$?]"; }
cd /workspace/t/shop
x "kubectl -n som-shop patch cm som-web-config --type merge -p '{\"data\":{\"SHOP_NAME\":\"ร้านน้องส้ม สาขาท่าเรือ\",\"APP_THEME\":\"sunset\",\"SHOP_PROMO\":\"🎉 โปรวันนี้: ขนมปลาทูน่าลด 20%\"}}'"
sleep 90
echo "--- after 90s, no restart:"
x curl -s localhost:30080/api/shop
x "kubectl -n som-shop rollout restart deploy/som-web"
kubectl -n som-shop rollout status deploy/som-web --timeout=180s
sleep 8
x curl -s localhost:30080/api/shop
x "curl -s localhost:30080/ | grep -o '<title>[^<]*</title>'"
x "curl -s localhost:30080/ | grep -o 'class=\"promo\">[^<]*<'"
x "curl -s localhost:30080/ | grep -o 'class=\"theme-[a-z]*\"' | head -1"
x curl -s localhost:30080/api/stats
x "kubectl -n som-shop rollout history deploy/som-web"
# announcement auto-update
x "kubectl -n som-shop create configmap som-announcement --from-literal=announcement.txt='ปิดร้านเร็ว 18:00 น. ⛵' --dry-run=client -o yaml | kubectl apply -f -"
t0=$(date +%s); P1=$(kubectl -n som-shop get pod -l app=som-web -o name | head -1)
while :; do out=$(curl -s localhost:30080/api/announcement); case "$out" in *18:00*) break;; esac; [ $(( $(date +%s)-t0 )) -gt 180 ] && { echo TIMEOUT; break; }; sleep 2; done
echo "first pod with new announcement after $(( $(date +%s)-t0 ))s: $out"
while :; do n=$(for i in $(seq 12); do curl -s localhost:30080/api/announcement; done | grep -c 18:00); [ "$n" = 12 ] && break; [ $(( $(date +%s)-t0 )) -gt 180 ] && { echo TIMEOUT2 $n; break; }; sleep 2; done
echo "all pods new after $(( $(date +%s)-t0 ))s"
x "kubectl -n som-shop get pod -l app=som-web"
# env precedence
x "kubectl -n som-shop set env deploy/som-web SHOP_FOOTER='LAB 010 · namespace \$(POD_NAMESPACE)'"
kubectl -n som-shop rollout status deploy/som-web --timeout=180s; sleep 8
x "curl -s localhost:30080/api/shop"
x "kubectl -n som-shop get deploy som-web -o jsonpath='{.spec.template.spec.containers[0].env[*].name}'"
