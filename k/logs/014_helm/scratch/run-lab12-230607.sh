set -v
cd /workspace/014_kubernetes_helm/02_LAB
echo "=== 12.8 ซองในสมุด (prod rev 2 — ไม่ได้ --set รหัส)"
kubectl -n som-shop get secret -l owner=helm,name=som
kubectl -n som-shop get secret sh.helm.release.v1.som.v2 -o jsonpath='{.data.release}' | base64 -d | base64 -d | gzip -d | python3 -c 'import json,sys,re; r=json.load(sys.stdin); print("config:", json.dumps(r["config"],ensure_ascii=False)); print(re.findall(r"DATABASE_URL: .*", r["manifest"])); print(re.findall(r"POSTGRES_PASSWORD: .*", r["manifest"])); print("tls.key อยู่ใน manifest:", "tls.key:" in r["manifest"]); print(re.findall(r"tls.key: \S{0,20}", r["manifest"]))'
echo "=== 12.9 ปิดสาขา dev"
curl -s -XPOST -H "content-type: application/json" -d '{"product_id":1,"qty":2}' http://dev.shop.localhost:30080/api/orders; echo
curl -s http://dev.shop.localhost:30080/api/stats; echo
helm uninstall som -n som-dev
sleep 8; kubectl -n som-dev get all,pvc,secret
helm list -A
echo "--- ติดตั้งใหม่รหัสเดิม → ข้อมูลเดิมกลับมา"
time helm install som charts/som-shop -n som-dev -f charts/values-dev.yaml --set db.password=meow1234 --wait | grep -E "STATUS|REVISION"
curl -s http://dev.shop.localhost:30080/api/stats; echo
helm uninstall som -n som-dev; sleep 8
echo "--- (ผลจริง) ติดตั้งใหม่ด้วยรหัสใหม่ แต่ตู้เซฟยังเป็นรหัสเดิม"
time helm install som charts/som-shop -n som-dev -f charts/values-dev.yaml --set db.password=purr5678 --wait --timeout 90s 2>&1 | tail -2
helm list -n som-dev
kubectl -n som-dev get pod
kubectl -n som-dev logs job/som-seed --all-containers --tail=3 2>&1 | tail -3
echo "--- แก้: upgrade release ที่ failed ด้วยรหัสเดิม"
helm upgrade som charts/som-shop -n som-dev -f charts/values-dev.yaml --set db.password=meow1234 --wait 2>&1 | grep -E "STATUS|REVISION|Error"
curl -s http://dev.shop.localhost:30080/api/stats; echo
helm history som -n som-dev | cut -c1-140
echo "--- ลบจริงทั้ง namespace (รวม PVC)"
helm uninstall som -n som-dev
kubectl delete ns som-dev
echo "=== 12.10 ตรวจรับร้าน"
helm test som -n som-shop --logs | sed -n '/Phase/,$p'
kubectl -n som-shop get deploy,sts,hpa,ing
kubectl top pod -n som-shop
curl -sk https://shop.localhost:30081/api/stats; echo
curl -s --cacert <(kubectl -n som-shop get secret som-tls -o jsonpath='{.data.tls\.crt}' | base64 -d) https://shop.localhost:30081/api/whoami; echo " (cacert ok)"
helm list -A
