set -v
cd /workspace/014_kubernetes_helm/02_LAB
echo "=== 12.6 อัปเกรด 1.8 (ครั้งแรกหลังรับร้าน)"
helm upgrade som charts/som-shop -n som-shop -f charts/values-prod.yaml --set web.image.tag=1.8 --wait 2>&1 | cut -c1-600
helm history som -n som-shop --max 2 | cut -c1-140
kubectl -n som-shop get deploy som-web -o jsonpath='{.spec.template.spec.containers[0].image}{"\n"}'
echo "--- ใส่ --force-conflicts ระหว่าง hit.sh"
./hit.sh -q https://shop.localhost:30081/api/whoami 400 0.1 > /root/hit-up.log 2>&1 &
sleep 3
t0=$(date +%s)
helm upgrade som charts/som-shop -n som-shop -f charts/values-prod.yaml --set web.image.tag=1.8 --force-conflicts --wait 2>&1 | grep -E "REVISION|STATUS|image|Error"
echo "upgrade: $(( $(date +%s)-t0 )) วินาที"
wait; tail -5 /root/hit-up.log
curl -sk https://shop.localhost:30081/api/whoami; echo
kubectl -n som-shop get deploy som-web --show-managed-fields -o json | python3 -c '
import json,sys; d=json.load(sys.stdin)
for m in d["metadata"]["managedFields"]:
    f=json.dumps(m.get("fieldsV1",{}))
    print(m["manager"], m["operation"], "owns image" if "f:image" in f else "")'
helm history som -n som-shop | cut -c1-120
