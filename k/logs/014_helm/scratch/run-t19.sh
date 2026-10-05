cd /workspace/pc/final/charts
helm lint som-shop
helm lint som-shop -f values-prod.yaml --set db.password=x
echo "=== template without password (required)"
helm template som som-shop 2>&1 | tail -2
echo "=== schema: tag 1.4 / replicas 9"
helm template som som-shop --set db.password=x --set web.image.tag=1.4 2>&1 | head -4
helm template som som-shop --set db.password=x --set web.replicas=9 2>&1 | head -4
echo "=== dev kinds"
helm template som som-shop -f values-dev.yaml --set db.password=x | grep -E "^kind:|replicas:|^# Source"
echo "=== prod kinds"
helm template som som-shop -f values-prod.yaml --set db.password=x | grep -E "^kind:|replicas:|middlewares"
