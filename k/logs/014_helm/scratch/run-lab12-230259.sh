set -v
echo "=== 12.5b field ที่เหลือจากบท 013 (เจ้าของคือ kubectl-client-side-apply) — เทียบ Deployment จริงกับ manifest ของ release"
kubectl -n som-shop get deploy som-web -o json | python3 -c '
import json,sys; d=json.load(sys.stdin); s=d["spec"]["template"]["spec"]
print("initContainers:", [c["name"] for c in s.get("initContainers",[])])
print("containers[web].env:", [e["name"] for e in s["containers"][0].get("env",[])])
print("volumes:", [v["name"] for v in s.get("volumes",[])])
print("pod labels:", d["spec"]["template"]["metadata"].get("labels"))
print("pod annotations:", sorted(d["spec"]["template"]["metadata"].get("annotations",{}).keys()))'
helm get manifest som -n som-shop | python3 -c '
import sys,re; m=sys.stdin.read(); dep=[x for x in m.split("\n---") if "kind: Deployment" in x][0]
print("chart initContainers:", re.findall(r"- name: (wait-for-db|db-seed)", dep))'
kubectl -n som-shop get pod -l app=som-web -o jsonpath='{range .items[*]}{.metadata.name}{" init="}{.spec.initContainers[*].name}{"\n"}{end}'
kubectl -n som-shop get deploy som-web -o json | python3 -c '
import json,sys; d=json.load(sys.stdin)
for m in d["metadata"]["managedFields"]:
    f=json.dumps(m.get("fieldsV1",{}))
    print(m["manager"], m["operation"], "db-seed" in f and "owns db-seed" or "")'
