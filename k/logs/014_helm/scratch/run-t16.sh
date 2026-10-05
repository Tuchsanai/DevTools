cd /workspace/pc/first
helm lint mychart
helm template web mychart | grep -E "^kind:|image:"
time helm install web mychart -n first --create-namespace --wait
helm test web -n first --logs
kubectl -n first get pod
echo "=== break template: indent error"
cp -r mychart broken
sed -i 's/{{- toYaml . | nindent 8 }}/{{- toYaml . | indent 2 }}/' broken/templates/deployment.yaml
sed -i 's/^podLabels: {}/podLabels: {shop: som}/' broken/values.yaml
helm lint broken 2>&1 | tail -6
helm template web broken 2>&1 | tail -4
helm template web broken --debug 2>&1 | grep -n -A3 "podLabels\|shop: som" | head -12
echo "=== required"
cp -r mychart req; sed -i 's|image: "{{ .Values.image.repository }}|image: "{{ required "ต้องใส่ image.repository" .Values.image.repository }}|' req/templates/deployment.yaml
helm template web req --set image.repository= 2>&1 | tail -2
echo "=== typo in function"
cp -r mychart typo; sed -i 's/toYaml/toYml/' typo/templates/service.yaml; grep -n toYml typo/templates/*.yaml | head -2
helm lint typo 2>&1 | tail -3
echo "=== dry-run server with bad field"
helm install web2 mychart -n first --dry-run=server --set service.type=NodePortt 2>&1 | tail -2
echo "=== chart v3"
sed 's/apiVersion: v2/apiVersion: v3/' mychart/Chart.yaml > /dev/null; cp -r mychart v3c; sed -i 's/apiVersion: v2/apiVersion: v3/' v3c/Chart.yaml
helm lint v3c 2>&1 | tail -2
HELM_EXPERIMENTAL_CHART_V3=1 helm lint v3c 2>&1 | tail -2
