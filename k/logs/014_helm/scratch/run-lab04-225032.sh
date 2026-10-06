set -v
cd /workspace/014_kubernetes_helm/02_LAB
echo "=== 1) image ผิด ไม่ใส่ --wait"
time helm upgrade hello podinfo/podinfo --version 6.15.0 -n helm-demo --reuse-values --set image.tag=9.9.9-nope | grep -E "REVISION|STATUS"
sleep 15; kubectl -n helm-demo get pod
helm history hello -n helm-demo | tail -2
echo "=== 2) rollback ระบุเลข"
time helm rollback hello 5 -n helm-demo --wait
kubectl -n helm-demo get pod
helm history hello -n helm-demo | tail -2
echo "=== 3) --atomic (ดูคำเตือน) และ --rollback-on-failure"
helm upgrade hello podinfo/podinfo --version 6.15.0 -n helm-demo --reuse-values --atomic --dry-run=client 2>&1 | head -1
time helm upgrade hello podinfo/podinfo --version 6.15.0 -n helm-demo --reuse-values --set image.tag=9.9.9-nope --rollback-on-failure --timeout 40s 2>&1 | cut -c1-400
helm history hello -n helm-demo
kubectl -n helm-demo get pod
echo "=== 4) rollback ไม่ใส่เลข → ไป revision ก่อนหน้า (แม้ failed)"
helm rollback hello -n helm-demo
sleep 10; kubectl -n helm-demo get pod
helm history hello -n helm-demo | tail -3
time helm rollback hello 9 -n helm-demo --wait
helm history hello -n helm-demo | tail -2
curl -s http://podinfo.localhost:30080 | grep -E '"(message|version)"'
echo "=== 5) ถอด release Secret"
kubectl -n helm-demo get secret -l owner=helm,name=hello
kubectl -n helm-demo get secret sh.helm.release.v1.hello.v5 -o jsonpath='{.data.release}' | base64 -d | base64 -d | gzip -d | python3 -c 'import json,sys; r=json.load(sys.stdin); print(sorted(r.keys())); print(r["info"]["status"], r["info"]["description"], r["version"]); print(json.dumps(r["config"], ensure_ascii=False))'
echo "=== 6) uninstall --keep-history"
helm uninstall hello -n helm-demo --keep-history
helm list -n helm-demo
helm list -n helm-demo --uninstalled
kubectl -n helm-demo get all
helm history hello -n helm-demo | tail -2
helm install hello podinfo/podinfo --version 6.15.0 -n helm-demo 2>&1 | tail -1
time helm rollback hello 11 -n helm-demo --wait
helm list -n helm-demo
kubectl -n helm-demo get deploy
echo "=== 7) uninstall จริง"
helm uninstall hello -n helm-demo --wait
helm history hello -n helm-demo
kubectl -n helm-demo get secret -l owner=helm
kubectl delete ns helm-demo
