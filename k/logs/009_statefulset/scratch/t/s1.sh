cd /root/t9; kubectl -n som-shop delete deploy som-db som-web --ignore-not-found >/dev/null; kubectl delete ns som-shop --wait=true >/dev/null; for pv in $(kubectl get pv -o name); do kubectl delete $pv; done
kubectl apply -f sts.yaml; kubectl get pod -l app=web -w --output-watch-events -o custom-columns=NAME:.metadata.name,PHASE:.status.phase,READY:.status.containerStatuses[0].ready --request-timeout=45s 2>/dev/null | awk '{print strftime("%T"), $0}' | head -30
kubectl rollout status sts/web; kubectl get sts,pod,pvc -o wide
kubectl get sts web -o yaml | grep -A12 "^spec:" | grep -E "podManagementPolicy|updateStrategy|partition|persistentVolumeClaimRetentionPolicy|whenDeleted|whenScaled|type:"
kubectl run dns --image=busybox:1.36 --restart=Never --rm -i --quiet -- sh -c 'nslookup web-0.web.default.svc.cluster.local | tail -2; nslookup web | grep Address | tail -3; wget -qO- web-1.web; wget -qO- web-2.web.default.svc.cluster.local' 2>&1
for i in 0 1 2; do kubectl exec web-$i -- hostname; done
kubectl get pod web-0 -o jsonpath='{.metadata.labels}'; echo
