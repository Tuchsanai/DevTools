cd /workspace/pc; grep -n -- '--' addons/traefik-rendered.yaml | grep -v "^.*# " | head -40; grep -n "kind: IngressClass" -A14 addons/traefik-rendered.yaml | tail -3
