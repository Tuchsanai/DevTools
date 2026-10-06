set -v
cd /workspace/014_kubernetes_helm/02_LAB
find charts -type f | sort
cat charts/som-shop/Chart.yaml
grep -n "define" charts/som-shop/templates/_helpers.tpl
helm template som charts/som-shop --set db.password=x --show-only templates/configmap.yaml
echo "=== hpa off: มี replicas"
helm template som charts/som-shop --set db.password=x --show-only templates/web.yaml | grep -nE "^kind:|replicas:|image:|checksum" 
echo "=== hpa on: replicas หาย"
helm template som charts/som-shop --set db.password=x --set hpa.enabled=true --show-only templates/web.yaml | grep -nE "^kind:|replicas:|image:"
echo "=== toYaml | nindent 12"
helm template som charts/som-shop --set db.password=x --show-only templates/web.yaml | grep -A6 "^          resources:"
echo "=== checksum/config เปลี่ยนเมื่อแก้ shop.*"
helm template som charts/som-shop --set db.password=x --show-only templates/web.yaml | grep "checksum/config"
helm template som charts/som-shop --set db.password=x --set shop.SHOP_PROMO="ลด 50%" --show-only templates/web.yaml | grep "checksum/config"
echo "=== fullnameOverride"
helm template som charts/som-shop --set db.password=x --set fullnameOverride=shop2 | grep -E "^  name:" | sort | uniq
helm template som charts/som-shop --set db.password=x | grep -E "^  name:" | sort | uniq
echo "=== labels จาก include"
helm template som charts/som-shop --set db.password=x --set web.image.tag=1.8 --show-only templates/secret.yaml
