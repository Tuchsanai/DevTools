cd /workspace/pc/final
t0=$(date +%s)
helm install som charts/som-shop -n som-nowait --create-namespace --set db.password=meow1234 2>&1 | grep -E "STATUS|Error"
echo "no --wait: $(( $(date +%s)-t0 ))s"; kubectl -n som-nowait get pod --no-headers
helm uninstall som -n som-nowait >/dev/null; kubectl delete ns som-nowait --wait=false
