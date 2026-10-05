cd /workspace/pc
time helm upgrade --install traefik traefik/traefik --version 41.6.1 -n traefik -f addons/traefik-values.yaml --take-ownership --force-conflicts 2>&1 | cut -c1-600
helm history traefik -n traefik | cut -c1-200
