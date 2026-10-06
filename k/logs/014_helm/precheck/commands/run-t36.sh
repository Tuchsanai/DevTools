cd /workspace/pc/final
helm plugin uninstall diff
timeout 120 helm plugin install https://github.com/databus23/helm-diff --version v3.15.15 --verify=false 2>&1 | tail -1
helm plugin list
helm diff upgrade som charts/som-shop -n som-dev -f charts/values-dev.yaml --set web.image.tag=1.8 2>&1 | grep -E "^[+-] |has changed|Error" | head -12
