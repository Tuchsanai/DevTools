set -v
cd /workspace/014_kubernetes_helm/02_LAB
kubectl -n som-shop get deploy som-web --show-managed-fields -o json | python3 -c '
import json,sys; d=json.load(sys.stdin)
for m in d["metadata"]["managedFields"]:
    f=json.dumps(m.get("fieldsV1",{}))
    print(m["manager"], m["operation"], "owns db-seed" if "db-seed" in f else "")'
echo "=== 12.5c ถอด initContainer db-seed ที่ค้างจากบท 013 (chart ใช้ hook seed แทน) ระหว่างลูกค้าเข้าร้าน"
kubectl -n som-shop get deploy som-web -o jsonpath='{.spec.template.spec.initContainers[1].name}{"\n"}'
(sleep 2; kubectl -n som-shop patch deploy som-web --type=json -p='[{"op":"test","path":"/spec/template/spec/initContainers/1/name","value":"db-seed"},{"op":"remove","path":"/spec/template/spec/initContainers/1"}]') & ./hit.sh -q https://shop.localhost:30081/api/whoami 250 0.1; wait
kubectl -n som-shop rollout status deploy/som-web --timeout=180s
kubectl -n som-shop get pod -l app=som-web -o jsonpath='{range .items[*]}{.metadata.name}{" init="}{.spec.initContainers[*].name}{"\n"}{end}'
