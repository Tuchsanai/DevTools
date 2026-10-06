set -v
cd /workspace/014_kubernetes_helm/02_LAB
timeout 180 helm plugin install https://github.com/databus23/helm-diff --version v3.15.15 2>&1 | tail -1
timeout 180 helm plugin install https://github.com/databus23/helm-diff --version v3.15.15 --verify=false 2>&1 | tail -1
helm plugin list
helm diff upgrade som charts/som-shop -n som-shop -f charts/values-prod.yaml --set web.image.tag=1.7 2>&1 | grep -E "^[+-] |has changed|Error" | head -12
helm plugin uninstall diff
echo "=== umbrella chart"
cd labs/labx-extra
helm dependency list harbor-addons
helm dependency update harbor-addons 2>&1 | tail -3
ls harbor-addons harbor-addons/charts
helm dependency list harbor-addons
helm template ha harbor-addons -n kube-system | grep -E "^kind:" | sort | uniq -c
helm template ha harbor-addons -n kube-system --set podinfo.enabled=true | grep -E "^# Source: [a-z-]+/charts/[a-z-]+" -o | sort | uniq -c
helm template ha harbor-addons -n kube-system | grep -- "--kubelet-insecure-tls"
rm -rf harbor-addons/charts harbor-addons/Chart.lock
