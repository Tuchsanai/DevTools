cd /workspace/pc
helm template traefik traefik/traefik --version 41.6.1 -n traefik -f addons/traefik-values.yaml > addons/traefik-rendered.yaml || exit 1
grep "^kind:" addons/traefik-rendered.yaml | sort | uniq -c
grep -- '- "--' addons/traefik-rendered.yaml
grep -B3 -A2 nodePort addons/traefik-rendered.yaml
grep -B3 -A8 "kind: IngressClass" addons/traefik-rendered.yaml
grep -n "image:" addons/traefik-rendered.yaml
