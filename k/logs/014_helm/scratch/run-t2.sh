cd /workspace/pc/traefik; grep -nE "^[a-z]" values.yaml | head -80; grep -n "access:" -B3 -A3 values.yaml | head -30
