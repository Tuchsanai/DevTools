#!/usr/bin/env bash
# usage: sanitize.sh in out — replaces the Docker Hub username/token with placeholders
python3 - "$1" "$2" <<'PY'
import os,sys
s=open(sys.argv[1],encoding='utf-8',errors='replace').read()
for k,ph in (('DOCKER_TOKEN','<DOCKER_TOKEN>'),('DOCKER_USER','<DOCKER_USER>')):
    v=os.environ.get(k)
    if v: s=s.replace(v,ph)
open(sys.argv[2],'w',encoding='utf-8').write(s)
PY
