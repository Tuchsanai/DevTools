set -v
cd /workspace/014_kubernetes_helm/02_LAB
cat charts/values-dev.yaml charts/values-prod.yaml
echo "=== dev"
helm template som charts/som-shop -f charts/values-dev.yaml --set db.password=x | grep -E "^kind:" | sort | uniq -c
helm template som charts/som-shop -f charts/values-dev.yaml --set db.password=x | grep -E "^kind:" | wc -l
echo "=== prod"
helm template som charts/som-shop -f charts/values-prod.yaml --set db.password=x | grep -E "^kind:" | sort | uniq -c
helm template som charts/som-shop -f charts/values-prod.yaml --set db.password=x | grep -E "^kind:" | wc -l
echo "=== ด่านตรวจ schema"
helm template som charts/som-shop --set db.password=x --set web.image.tag=1.4 2>&1 | head -4
helm template som charts/som-shop --set db.password=x --set web.replicas=9 2>&1 | head -4
helm template som charts/som-shop --set db.password=x --set ingress.host=Shop_Localhost 2>&1 | head -3
echo "=== required: lint vs template"
helm lint charts/som-shop
helm lint charts/som-shop -f charts/values-prod.yaml --set db.password=x
helm template som charts/som-shop 2>&1 | tail -2
echo "=== lookup: helm template ไม่ต่อคลัสเตอร์ → ใบรับรองใหม่ทุกครั้ง"
helm template som charts/som-shop -f charts/values-prod.yaml --set db.password=x --show-only templates/ingress.yaml | grep "tls.crt" | cut -c1-60
helm template som charts/som-shop -f charts/values-prod.yaml --set db.password=x --show-only templates/ingress.yaml | grep "tls.crt" | cut -c1-60
echo "=== schema ของ chart อื่น (Traefik) ก็ปฏิเสธ key ผิด"
helm template traefik traefik/traefik --version 41.6.1 -n traefik -f labs/lab10-addons/traefik-values.yaml --set logs.access.enabled=true 2>&1 | head -3
helm template traefik traefik/traefik --version 41.6.1 -n traefik -f labs/lab10-addons/traefik-values.yaml --set accesslog.enabled=true 2>&1 | head -3
