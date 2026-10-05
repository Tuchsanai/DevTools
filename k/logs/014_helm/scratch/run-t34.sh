cd /workspace/pc/final
helm diff upgrade som charts/som-shop -n som-dev -f charts/values-dev.yaml --set web.image.tag=1.8 2>&1 | grep -E "^[+-]|has changed" | head -12
echo "=== dependency"
mkdir -p /workspace/pc/dep && cd /workspace/pc/dep && helm create harbor-addons >/dev/null && rm -rf harbor-addons/templates/* && cat >> harbor-addons/Chart.yaml <<'Y'
dependencies:
  - name: metrics-server
    version: 3.14.0
    repository: https://kubernetes-sigs.github.io/metrics-server/
  - name: podinfo
    version: 6.15.0
    repository: oci://ghcr.io/stefanprodan/charts
    condition: podinfo.enabled
Y
printf 'podinfo:\n  enabled: false\n' > harbor-addons/values.yaml
helm dependency list harbor-addons
helm dependency update harbor-addons 2>&1 | tail -4
ls harbor-addons/charts; cat harbor-addons/Chart.lock
helm template x harbor-addons | grep -E "^# Source" | cut -d/ -f1-3 | sort | uniq -c
