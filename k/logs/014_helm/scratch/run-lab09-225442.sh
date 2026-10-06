set -v
# เก็บกวาด LAB 5–6 และ LAB 9 (LAB 12 ติดตั้งสาขา dev ใหม่ทั้งร้าน)
helm uninstall web -n first; kubectl delete ns first
helm uninstall som -n som-dev
kubectl -n som-dev get pvc
kubectl delete ns som-dev
helm list -A
