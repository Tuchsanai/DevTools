cd /workspace/pc
helm rollback som 4 -n som-shop --wait 2>&1 | tail -1; helm rollback som 2 -n som-shop --wait 2>&1 | tail -1
helm history som -n som-shop --max 3 | cut -c1-110
curl -sk https://shop.localhost:30081/api/whoami
kubectl -n som-shop get deploy som-web --show-managed-fields -o yaml | grep -E "^\s+manager:|operation:"
