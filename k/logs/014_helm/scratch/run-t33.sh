cd /workspace/pc
helm search hub traefik --max-col-width 60 2>&1 | head -5
helm plugin list
helm plugin --help | sed -n '/Available Commands/,/Flags/p'
timeout 120 helm plugin install https://github.com/databus23/helm-diff --version v3.13.1 2>&1 | tail -3
timeout 120 helm plugin install https://github.com/databus23/helm-diff --version v3.13.1 --verify=false 2>&1 | tail -3
helm plugin list
