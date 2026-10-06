cd /workspace/pc
cat > podinfo-values.yaml <<'V'
replicaCount: 3
ui:
  color: "#ff8c00"
  message: "ร้านน้องส้มสาขา values file"
ingress:
  enabled: true
  className: traefik
  hosts:
    - host: podinfo.localhost
      paths:
        - path: /
          pathType: Prefix
V
echo "=== upgrade -f + --set (set wins)"
helm upgrade hello podinfo/podinfo --version 6.15.0 -n helm-demo -f podinfo-values.yaml --set ui.message="--set ชนะ" --wait | head -8
helm get values hello -n helm-demo
curl -s -H "Host: podinfo.localhost" localhost:30080 | grep -E "message|color"
curl -s http://podinfo.localhost:30080 | grep -E "message"
echo "=== upgrade without values (values reset!)"
helm upgrade hello podinfo/podinfo --version 6.15.0 -n helm-demo --set replicaCount=1 --wait | grep -E "REVISION|STATUS"
helm get values hello -n helm-demo
echo "=== reuse-values"
helm upgrade hello podinfo/podinfo --version 6.15.0 -n helm-demo --reuse-values --set ui.message="reuse" --wait | grep REVISION
helm get values hello -n helm-demo
helm history hello -n helm-demo
echo "=== rollback to 2"
helm rollback hello 2 -n helm-demo --wait
helm history hello -n helm-demo
helm get values hello -n helm-demo
kubectl -n helm-demo get deploy hello-podinfo
