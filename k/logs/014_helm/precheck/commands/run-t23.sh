cd /workspace/pc/final
fp() { kubectl -n som-prod get secret som-tls -o jsonpath='{.data.tls\.crt}' | base64 -d | openssl x509 -noout -fingerprint -sha256 | cut -c1-40; }
echo "cert before: $(fp)"
bash hit.sh -q https://shop.localhost:30081/api/whoami 400 0.1 > hit-up.log 2>&1 &
sleep 3
t0=$(date +%s)
helm upgrade som charts/som-shop -n som-prod -f charts/values-prod.yaml --set web.image.tag=1.8 --wait --timeout 5m | grep -E "REVISION|STATUS|image"
echo "upgrade: $(( $(date +%s)-t0 ))s"
echo "cert after: $(fp)"
wait; tail -6 hit-up.log
helm history som -n som-prod
bash hit.sh -q https://shop.localhost:30081/api/whoami 300 0.1 > hit-rb.log 2>&1 &
sleep 3
t0=$(date +%s)
helm rollback som -n som-prod --wait | tail -1
echo "rollback: $(( $(date +%s)-t0 ))s"
wait; tail -5 hit-rb.log
helm history som -n som-prod
curl -sk https://shop.localhost:30081/api/whoami; echo
helm get values som -n som-prod | grep -A2 "^web" ; helm get values som -n som-prod --revision 2 | grep -A3 "^web"
