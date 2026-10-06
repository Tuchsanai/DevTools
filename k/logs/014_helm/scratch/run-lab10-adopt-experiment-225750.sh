set -v
# รอบ 2: แก้สำเนาให้ SA/ClusterRoleBinding อยู่ใน traefik-test ด้วย แล้วดูข้อความเต็มของ helm uninstall
kubectl delete -f /root/exp/traefik-test.yaml --ignore-not-found --wait=true 2>&1 | tail -2
sed -i -E 's/namespace: traefik( |$)/namespace: traefik-test\1/' /root/exp/traefik-test.yaml
grep -n "namespace:" /root/exp/traefik-test.yaml
kubectl apply -f /root/exp/traefik-test.yaml
kubectl -n traefik-test rollout status deploy/traefik --timeout=120s
helm install traefik traefik/traefik --version 41.6.1 -n traefik-test -f /root/exp/v.yaml --take-ownership 2>&1 | head -2 | cut -c1-200
helm upgrade --install traefik traefik/traefik --version 41.6.1 -n traefik-test -f /root/exp/v.yaml --take-ownership --force-conflicts 2>&1 | tail -1 | cut -c1-200
kubectl -n traefik-test get sa,deploy,svc -o custom-columns=KIND:.kind,NAME:.metadata.name,MANAGED:.metadata.labels.app\\.kubernetes\\.io/managed-by
helm uninstall traefik -n traefik-test 2>&1
kubectl -n traefik-test get sa,deploy,svc,pod
echo "=== เก็บกวาดการทดลอง"
kubectl delete -f /root/exp/traefik-test.yaml --ignore-not-found 2>&1 | tail -3
kubectl get ns traefik-test 2>&1 | tail -1
kubectl -n traefik get sa,deploy,svc
