cd /workspace/pc/final/charts
helm template som som-shop -n som-dev -f values-dev.yaml --set db.password=meow1234 > /workspace/pc/final/rendered-dev.yaml
helm template som som-shop -n som-prod -f values-prod.yaml --set db.password=meow1234 > /workspace/pc/final/rendered-prod.yaml
cp /workspace/pc/podinfo-values.yaml /workspace/pc/final/
helm list -A
