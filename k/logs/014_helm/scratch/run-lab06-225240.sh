set -v
cd /workspace/014_kubernetes_helm/02_LAB/labs/lab06-debug
helm template web broken-required --set image.repository= 2>&1 | head -3
echo "=== v3: ลองลบบรรทัด type ออก"
sed -i '/^type:/d' broken-v3/Chart.yaml
helm lint broken-v3 2>&1 | tail -3
HELM_EXPERIMENTAL_CHART_V3=1 helm lint broken-v3 2>&1 | tail -3
HELM_EXPERIMENTAL_CHART_V3=1 helm template web broken-v3 2>&1 | head -3
helm template web broken-v3 2>&1 | head -3
echo "=== เก็บกวาด release ที่ล้ม"
helm uninstall web2 -n first
helm list -n first
