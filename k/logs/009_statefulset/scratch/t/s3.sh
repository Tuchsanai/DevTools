cd /root/t9; kubectl delete sts web >/dev/null; kubectl delete pvc -l app=web >/dev/null 2>&1; kubectl delete pvc www-web-0 www-web-1 www-web-2 >/dev/null 2>&1
sed -e 's/name: web}/name: par}/; s/app: web}/app: par}/g; s/serviceName: web/serviceName: web\n  podManagementPolicy: Parallel\n  persistentVolumeClaimRetentionPolicy: {whenScaled: Delete, whenDeleted: Delete}/' sts.yaml | awk 'BEGIN{p=0} /^---/{p=1;next} p' > par.yaml
grep -nE "name: par|Parallel|Retention|app:" par.yaml
kubectl apply -f par.yaml; sleep 4; kubectl get pod -l app=par --no-headers; kubectl rollout status sts/par >/dev/null
kubectl get pvc -l app=par --no-headers 2>/dev/null; kubectl get pvc --no-headers | awk '{print $1,$2}'
kubectl get pvc www-par-0 -o jsonpath='{.metadata.ownerReferences}'; echo
echo "== scale par 3->1"; kubectl scale sts par --replicas=1; sleep 10; kubectl get pvc --no-headers | awk '{print $1,$2}'
echo "== delete par"; kubectl delete sts par; sleep 8; kubectl get pvc --no-headers | awk '{print $1,$2}'; kubectl get pv --no-headers | wc -l
echo "== OrderedReady blocked"; cat > bad.yaml <<'Y'
apiVersion: apps/v1
kind: StatefulSet
metadata: {name: bad}
spec:
  serviceName: web
  replicas: 3
  selector: {matchLabels: {app: bad}}
  template:
    metadata: {labels: {app: bad}}
    spec:
      containers:
      - {name: c, image: busybox:1.36, command: [sleep, "3600"], readinessProbe: {exec: {command: [cat, /tmp/ready]}, periodSeconds: 2}}
Y
kubectl apply -f bad.yaml; sleep 15; kubectl get pod -l app=bad --no-headers; kubectl exec bad-0 -- touch /tmp/ready; sleep 10; kubectl get pod -l app=bad --no-headers; kubectl delete sts bad
