# DB storage variants

manifest หลัก `../04-db.yaml` ใช้ PVC ส่วนไฟล์ในโฟลเดอร์นี้ใช้พิสูจน์อีกสองกรณี:

```bash
kubectl apply -f db-no-volume.yaml
kubectl apply -f db-emptydir.yaml
kubectl wait -n k8s-lab-ref --for=condition=available deploy/db-no-volume deploy/db-emptydir --timeout=120s
kubectl exec -n k8s-lab-ref deploy/db-no-volume -- psql -U opsuser -d skillspace -Atc 'select count(*) from assets'
kubectl exec -n k8s-lab-ref deploy/db-emptydir -- psql -U opsuser -d skillspace -Atc 'select count(*) from assets'
kubectl delete -f db-no-volume.yaml -f db-emptydir.yaml
```
