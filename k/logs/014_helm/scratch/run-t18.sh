cd /workspace/pc/first
helm template web req --set image.repository= 2>&1 | head -3
grep -n required req/templates/deployment.yaml
helm template web2 mychart --set service.type=NodePortt | kubectl apply --dry-run=server -f - 2>&1 | tail -2
helm uninstall web -n first; kubectl delete ns first --wait=false
