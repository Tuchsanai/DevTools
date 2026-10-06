cd /workspace/pc/first
grep -n "image:" mychart/templates/deployment.yaml
sed -i 's|{{ .Values.image.repository }}|{{ required "ต้องใส่ image.repository" .Values.image.repository }}|' req/templates/deployment.yaml
helm template web req --set image.repository= 2>&1 | tail -2
sed -i 's/toYaml/toYml/' typo/templates/deployment.yaml
helm lint typo 2>&1 | tail -3
echo "=== dry-run server"
helm install web2 mychart -n first --dry-run=server --set service.type=NodePortt 2>&1 | head -12
echo "=== dry-run client"
helm install web2 mychart -n first --dry-run=client --set service.type=NodePortt 2>&1 | head -3
echo "=== real install bad type"
helm install web2 mychart -n first --set service.type=NodePortt 2>&1 | tail -3
helm list -n first -a 2>&1 | tail -2; helm list -n first
helm uninstall web2 -n first 2>&1 | tail -1
echo "=== v3"
helm lint v3c 2>&1 | head -5
HELM_EXPERIMENTAL_CHART_V3=1 helm lint v3c 2>&1 | head -5
