cd /workspace/pc/final
helm diff upgrade som charts/som-shop -n som-dev -f charts/values-dev.yaml --set web.image.tag=1.8 2>&1 | head -30
