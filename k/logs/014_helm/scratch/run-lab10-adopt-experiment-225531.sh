set -v
# ทดลองแยก (ไม่ใช่ขั้นของนักศึกษา): Traefik static สำเนาใน namespace traefik-test (ไม่มี NodePort/IngressClass, ClusterRole ชื่อ traefik-test)
cd /workspace/014_kubernetes_helm/02_LAB/labs/lab10-addons
mkdir -p /root/exp && python3 - <<'PY'
import re
src=open('static-old/00-traefik.yaml').read()
docs=[d for d in src.split('\n---') ]
out=[]
for d in docs:
    if re.search(r'^kind: IngressClass', d, re.M): continue
    d=d.replace('namespace: traefik\n','namespace: traefik-test\n')
    if re.search(r'^kind: Namespace', d, re.M): d=re.sub(r'name: traefik\b','name: traefik-test',d)
    if re.search(r'^kind: Cluster(Role|RoleBinding)', d, re.M):
        d=re.sub(r'(\n  name:) traefik\b',r'\1 traefik-test',d); d=re.sub(r'(\n  name:) traefik\n(\s+apiGroup|\s*subjects)',r'\1 traefik-test\n\2',d)
        d=d.replace('kind: ClusterRole\n  name: traefik\n','kind: ClusterRole\n  name: traefik-test\n')
    if re.search(r'^kind: Service\b', d, re.M):
        d=d.replace('type: NodePort','type: ClusterIP'); d=re.sub(r', nodePort: \d+','',d)
    out.append(d)
open('/root/exp/traefik-test.yaml','w').write('\n---'.join(out))
PY
grep -nE "^kind|^  name|namespace|type:|nodePort" /root/exp/traefik-test.yaml | grep -v "^.*#"
kubectl apply -f /root/exp/traefik-test.yaml
kubectl -n traefik-test rollout status deploy/traefik --timeout=120s
cat > /root/exp/v.yaml <<'V'
service: {spec: {type: ClusterIP}}
ports: {web: {nodePort: null}, websecure: {nodePort: null}}
ingressClass: {enabled: false}
providers: {kubernetesIngress: {ingressClass: none-test}}
V
echo "=== 1) install ทับ"
helm install traefik traefik/traefik --version 41.6.1 -n traefik-test -f /root/exp/v.yaml 2>&1 | cut -c1-400
helm list -n traefik-test
echo "=== 2) --take-ownership"
time helm install traefik traefik/traefik --version 41.6.1 -n traefik-test -f /root/exp/v.yaml --take-ownership 2>&1 | cut -c1-900
helm list -n traefik-test
echo "=== 3) --take-ownership --force-conflicts"
time helm upgrade --install traefik traefik/traefik --version 41.6.1 -n traefik-test -f /root/exp/v.yaml --take-ownership --force-conflicts 2>&1 | cut -c1-600
helm history traefik -n traefik-test
kubectl -n traefik-test get sa,deploy,svc -o custom-columns=KIND:.kind,NAME:.metadata.name,MANAGED:.metadata.labels.app\\.kubernetes\\.io/managed-by,RELEASE:.metadata.annotations.meta\\.helm\\.sh/release-name
echo "=== 4) helm uninstall release ที่ล้ม"
helm uninstall traefik -n traefik-test 2>&1 | tail -3
kubectl -n traefik-test get sa,deploy,svc,pod
kubectl get clusterrole traefik-test 2>&1 | tail -1
