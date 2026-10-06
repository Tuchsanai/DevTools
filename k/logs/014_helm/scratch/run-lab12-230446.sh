set -v
cd /workspace/014_kubernetes_helm/02_LAB
echo "=== 12.7 สมุดและย้อนรุ่น"
helm history som -n som-shop -o table --max 10 | cut -c1-120
for r in 2 4; do echo "rev $r: $(helm get values som -n som-shop --revision $r -o json)"; done
./hit.sh -q https://shop.localhost:30081/api/whoami 300 0.1 > /root/hit-rb.log 2>&1 &
sleep 3
t0=$(date +%s)
helm rollback som 2 -n som-shop --wait 2>&1 | tail -1
echo "rollback: $(( $(date +%s)-t0 )) วินาที"
wait; tail -5 /root/hit-rb.log
helm history som -n som-shop --max 2 | cut -c1-120
curl -sk https://shop.localhost:30081/api/whoami; echo
echo "=== หลัง force ครั้งเดียว upgrade ต่อไปไม่ต้อง force"
./hit.sh -q https://shop.localhost:30081/api/whoami 300 0.1 > /root/hit-up2.log 2>&1 &
sleep 3
t0=$(date +%s)
helm upgrade som charts/som-shop -n som-shop -f charts/values-prod.yaml --set web.image.tag=1.8 --wait 2>&1 | grep -E "REVISION|STATUS|Error"
echo "upgrade: $(( $(date +%s)-t0 )) วินาที"
wait; tail -5 /root/hit-up2.log
helm history som -n som-shop --max 3 | cut -c1-120
