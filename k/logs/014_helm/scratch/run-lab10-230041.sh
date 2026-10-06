set -v
grep -nE -- "--(entryPoints.websecure.http.tls|providers.kubernetesingress.strictPrefixMatching|providers.kubernetesingress.ingressendpoint.hostname|api.insecure|accesslog)" /root/traefik-rendered.yaml
kubectl get apiservice v1beta1.metrics.k8s.io
