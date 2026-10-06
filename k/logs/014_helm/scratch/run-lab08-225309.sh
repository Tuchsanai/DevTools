set -v
cd /workspace/014_kubernetes_helm/02_LAB
helm template som charts/som-shop 2>&1 | head -1
for i in 1 2; do helm template som charts/som-shop -f charts/values-prod.yaml --set db.password=x --show-only templates/ingress.yaml | grep "tls.crt" | awk '{print $2}' | base64 -d | openssl x509 -noout -fingerprint -sha256 | cut -c1-45; done
helm template som charts/som-shop -f charts/values-prod.yaml --set db.password=x --show-only templates/ingress.yaml | grep "tls.crt" | awk '{print $2}' | base64 -d | openssl x509 -noout -subject -ext subjectAltName
