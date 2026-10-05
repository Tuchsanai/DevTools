cd /workspace/pc/final/charts
helm test som -n som-dev --logs | sed -n '/TEST SUITE/,$p'
echo "=== release secret shows password"
kubectl -n som-dev get secret sh.helm.release.v1.som.v1 -o jsonpath='{.data.release}' | base64 -d | base64 -d | gzip -d | python3 -c 'import json,sys; r=json.load(sys.stdin); print(json.dumps(r["config"],ensure_ascii=False)); import re; print(re.findall(r"DATABASE_URL: .*", r["manifest"]))'
helm get values som -n som-dev
echo "=== upgrade dev without password (lookup) + announcement change"
helm upgrade som som-shop -n som-dev -f values-dev.yaml --set announcement="ปลาแซลมอนมาแล้ว" --wait | grep -E "REVISION|STATUS"
kubectl -n som-dev get secret som-db-secret -o jsonpath='{.data.POSTGRES_PASSWORD}' | base64 -d; echo
kubectl -n som-dev get pod -l app=som-web
curl -s http://dev.shop.localhost:30080/api/announcement; echo
helm get values som -n som-dev
