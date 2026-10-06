set -v
cd /workspace/014_kubernetes_helm/02_LAB
grep -A3 "annotations:" charts/som-shop/templates/seed-job.yaml
(time helm install som charts/som-shop -n som-dev --create-namespace -f charts/values-dev.yaml --set db.password=meow1234 --wait) > /root/install-dev.out 2>&1 &
sleep 2; timeout 30 kubectl -n som-dev get job,pod -w
wait; cat /root/install-dev.out
kubectl get ns som-dev --show-labels
kubectl -n som-dev get all,pvc,cm,secret,ing
kubectl -n som-dev get job
curl -s http://dev.shop.localhost:30080/api/whoami; echo
curl -s http://dev.shop.localhost:30080/api/stats; echo
curl -s http://dev.shop.localhost:30080/ | grep -o "ร้านอาหารแมวน้องส้ม (dev)" | head -1
curl -s http://dev.shop.localhost:30080/ | grep -o "🧪 สาขาทดลอง[^<]*" | head -1
echo "=== ผู้ตรวจรับร้าน"
helm test som -n som-dev --logs | sed -n '/TEST SUITE/,$p'
kubectl -n som-dev get pod
echo "=== PSA: namespace ที่ --create-namespace สร้างไม่มี label pod-security → ลองตรวจกับ restricted"
kubectl label --dry-run=server --overwrite ns som-dev pod-security.kubernetes.io/enforce=restricted
echo "=== ซองในสมุด: ถอด release Secret"
kubectl -n som-dev get secret -l owner=helm
kubectl -n som-dev get secret sh.helm.release.v1.som.v1 -o jsonpath='{.data.release}' | base64 -d | base64 -d | gzip -d | python3 -c 'import json,sys,re; r=json.load(sys.stdin); print(json.dumps(r["config"],ensure_ascii=False)); print(re.findall(r"DATABASE_URL: .*", r["manifest"])); print([h["name"]+":"+",".join(h["events"]) for h in r["hooks"]])'
helm get values som -n som-dev
echo "=== upgrade โดยไม่ส่งรหัส (lookup) + เปลี่ยนประกาศ (checksum → Pod ใหม่เอง)"
kubectl -n som-dev get pod -l app=som-web -o name
time helm upgrade som charts/som-shop -n som-dev -f charts/values-dev.yaml --set announcement="ปลาแซลมอนมาแล้ว 🍣" --wait | grep -E "REVISION|STATUS"
kubectl -n som-dev get pod -l app=som-web -o name
kubectl -n som-dev get secret som-db-secret -o jsonpath='{.data.POSTGRES_PASSWORD}' | base64 -d; echo
curl -s http://dev.shop.localhost:30080/api/announcement; echo
helm history som -n som-dev
