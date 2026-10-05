cd /workspace/pc
echo "=== --atomic (deprecated?) bad image"
time helm upgrade hello podinfo/podinfo --version 6.15.0 -n helm-demo --reuse-values --set image.tag=9.9.9-nope --atomic --timeout 40s 2>&1 | cut -c1-300
echo "=== --rollback-on-failure"
time helm upgrade hello podinfo/podinfo --version 6.15.0 -n helm-demo --reuse-values --set image.tag=9.9.9-nope --rollback-on-failure --timeout 40s 2>&1 | cut -c1-300
helm history hello -n helm-demo | cut -c1-160
echo "=== bad image no wait"
helm upgrade hello podinfo/podinfo --version 6.15.0 -n helm-demo --reuse-values --set image.tag=9.9.9-nope 2>&1 | grep -E "STATUS|REVISION"
sleep 15; kubectl -n helm-demo get pod | head; helm status hello -n helm-demo | grep STATUS
helm rollback hello -n helm-demo --wait 2>&1 | tail -1
helm history hello -n helm-demo --max 3 | cut -c1-120
echo "=== decode release secret"
kubectl -n helm-demo get secret sh.helm.release.v1.hello.v2 -o jsonpath='{.data.release}' | base64 -d | base64 -d | gzip -d | python3 -c 'import json,sys; r=json.load(sys.stdin); print(list(r.keys())); print(json.dumps(r["config"],ensure_ascii=False)); print(r["manifest"][:200])'
