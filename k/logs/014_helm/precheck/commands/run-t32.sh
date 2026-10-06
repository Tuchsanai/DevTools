cd /workspace/pc/final
mkdir -p pulled && helm pull oci://localhost:5000/charts/som-shop --version 0.1.0 --plain-http -d pulled --untar 2>&1 | tail -1; ls pulled/som-shop
cat ~/.config/helm/registry/config.json | python3 -c 'import json,sys; d=json.load(sys.stdin); print({k:{kk:(vv[:6]+"...") for kk,vv in v.items()} for k,v in d["auths"].items()})'
t0=$(date +%s)
helm install oci-som oci://localhost:5000/charts/som-shop --version 0.1.0 --plain-http -n oci-demo --create-namespace --set fullnameOverride=som --set db.password=meow1234 --set ingress.enabled=true --set ingress.host=oci.shop.localhost --set web.replicas=1 --wait 2>&1 | grep -E "NAME:|STATUS|REVISION|Error|Pulled|Digest"
echo "oci install: $(( $(date +%s)-t0 ))s"
curl -s http://oci.shop.localhost:30080/api/whoami
helm list -n oci-demo
helm get metadata oci-som -n oci-demo | head -4
echo "=== by digest"
helm template x oci://localhost:5000/charts/som-shop@sha256:e607fd8ffff22410f84531765be225897cab4eb9b80e222c44a687655c83f14a --plain-http --set db.password=x 2>&1 | grep -c "^kind:"
helm registry logout localhost:5000
helm show chart oci://localhost:5000/charts/som-shop --version 0.1.0 --plain-http 2>&1 | tail -1 | cut -c1-200
helm uninstall oci-som -n oci-demo; kubectl delete ns oci-demo --wait=false
