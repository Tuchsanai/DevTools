cd /workspace/pc
bash final/hit.sh -q https://shop.localhost:30081/api/whoami 300 0.1 > hit-a.log 2>&1 &
sleep 2
helm upgrade som final/charts/som-shop -n som-shop -f final/charts/values-prod.yaml --set web.image.tag=1.8 --force-conflicts --wait 2>&1 | grep -E "REVISION|Error" | cut -c1-200
wait; tail -2 hit-a.log
kubectl -n som-shop get deploy som-web -o json | python3 -c 'import json,sys; d=json.load(sys.stdin); [print(m["manager"], m["operation"], "image" in json.dumps(m.get("fieldsV1",{})) and "f:image" in json.dumps(m.get("fieldsV1",{}))) for m in d["metadata"]["managedFields"]]'
echo "=== rollback (no force)"
helm rollback som -n som-shop --wait 2>&1 | tail -1 | cut -c1-300
echo "=== upgrade again no force"
helm upgrade som final/charts/som-shop -n som-shop -f final/charts/values-prod.yaml --set web.image.tag=1.8 --wait 2>&1 | grep -E "REVISION|Error" | cut -c1-300
helm history som -n som-shop | cut -c1-110
curl -sk https://shop.localhost:30081/api/stats; echo
