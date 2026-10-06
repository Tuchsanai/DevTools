set -v
cd /workspace/014_kubernetes_helm/02_LAB
helm repo list
helm repo add podinfo https://stefanprodan.github.io/podinfo
helm repo add traefik https://traefik.github.io/charts
helm repo add metrics-server https://kubernetes-sigs.github.io/metrics-server/
helm repo update
helm repo list
helm search repo traefik/traefik --versions | head -5
helm search repo metrics-server --versions | head -3
helm search repo podinfo/podinfo --versions | head -3
helm search hub traefik --max-col-width 50 | head -8
helm show chart podinfo/podinfo --version 6.15.0
helm show values podinfo/podinfo --version 6.15.0 | grep -nE "^replicaCount|^ui:|^  color|^  message|^service:|^  type:|^ingress:" | head
cd labs/lab01-catalog
helm pull traefik/traefik --version 41.6.1 --untar
ls traefik | head -20
grep -E "^(version|appVersion)" traefik/Chart.yaml
ls traefik/crds | wc -l
cd ../..
