#!/usr/bin/env bash
# verify-app.sh — yolo1's independent Phase 4 check of app/ on the devtools-k8s-verify cluster. Prints PASS/FAIL per item.
C=devtools-k8s-verify; NS=k8s-lab-ref
kx() { docker exec $C kubectl -n $NS "$@"; }
kc() { docker exec $C bash -lc "$*"; }
IP=$C; echo "IP=$IP (container name on k8s-course-net)"
res() { if [ "$1" = 0 ]; then echo "PASS  $2"; else echo "FAIL  $2"; fi; }
echo "### build (clean: no k8s-lab images exist in this dockerd yet)"
kc 'docker images --format "{{.Repository}}:{{.Tag}}" | grep -c k8s-lab || true'
t0=$(date +%s); kc 'cd ~/labwork/DevTools/05_kubernetes/app && ./build-images.sh' > /tmp/build.log 2>&1; rc=$?; echo "build rc=$rc in $(( $(date +%s)-t0 ))s"; tail -6 /tmp/build.log; res $rc "10 build from clean state"
kc 'kind load docker-image k8s-lab-web:v1 k8s-lab-web:v2 k8s-lab-api:v1 k8s-lab-db:v1 --name devtools' 2>&1 | tail -2
kc 'docker exec devtools-control-plane crictl images | grep k8s-lab'
echo "### apply k8s-reference"
kc 'cd ~/labwork/DevTools/05_kubernetes/app && kubectl apply -f k8s-reference/' | tail -12
kx wait --for=condition=available deploy/db deploy/api deploy/web --timeout=300s; res $? "all deployments available"
kx get pods -o wide
echo "### 1 load balancing via Ingress"; for i in $(seq 1 24); do curl -s -m 3 http://$IP/info | jq -r .pod; done | sort | uniq -c | tee /tmp/lb.txt; [ $(wc -l < /tmp/lb.txt) -ge 3 ]; res $? "1 three distinct web pods answered"
echo "### 2 /api/whoami via Ingress"; curl -s -m 3 -i http://$IP/api/whoami | grep -iE 'x-pod-name|"pod"' ; curl -s -m 3 http://$IP/api/whoami | jq -e .pod >/dev/null; res $? "2 api reachable through Ingress /api"
echo "### 3 full stack status + data"; curl -s -m 3 http://$IP/info | jq -c '{api,db,version,theme,site_name}'; curl -s -m 3 http://$IP/info | jq -e '.api.reachable and .db.status=="up"' >/dev/null; res $? "3 status card: api reachable, db up"; curl -s -m 3 http://$IP/api/dashboard | jq -c .tickets
node /root/workspace/DevTools/05_kubernetes/.work/tools/shot.js "http://$IP/" /root/workspace/DevTools/05_kubernetes/.work/app-screens/yolo1-full-stack-v1.png --w 1280 --h 900 >/dev/null && echo "shot ok"
echo "### 4 standalone web (kubectl run + port-forward)"; kc 'kubectl create ns standalone-check >/dev/null; kubectl -n standalone-check run web --image=k8s-lab-web:v1 --port=3000 >/dev/null; kubectl -n standalone-check wait --for=condition=ready pod/web --timeout=120s'
kc 'nohup kubectl -n standalone-check port-forward pod/web 3000:3000 --address 0.0.0.0 >/tmp/pf.log 2>&1 & sleep 3; echo pf started'
for p in / /tickets /loans /parts /healthz /readyz /info; do printf "%-9s %s\n" $p "$(curl -s -m 5 -o /dev/null -w '%{http_code}' http://$IP:3000$p)"; done
curl -s -m 5 http://$IP:3000/info | jq -c '{pod,api,db}'; curl -s -m 5 http://$IP:3000/info | jq -e '.api.configured==false' >/dev/null; res $? "4 standalone mode reported, pages 200"
node /root/workspace/DevTools/05_kubernetes/.work/tools/shot.js "http://$IP:3000/" /root/workspace/DevTools/05_kubernetes/.work/app-screens/yolo1-standalone.png --w 1280 --h 900 >/dev/null && echo "shot ok"
kc 'pkill -f "port-forward pod/web" ; kubectl delete ns standalone-check --wait=false >/dev/null; echo cleaned'
echo "### 5 db down -> api not ready"; kx scale deploy db --replicas=0 >/dev/null; sleep 20; kx get pods -l app=api; kx get endpoints api; curl -s -m 3 -o /dev/null -w "ingress /api/ready -> %{http_code}\n" http://$IP/api/ready; curl -s -m 3 http://$IP/info | jq -c '{api,db}'
kx get endpoints api -o jsonpath='{.subsets}' | grep -q addresses; res $(( ! $? )) "5 api removed from endpoints while db down"
kx scale deploy db --replicas=1 >/dev/null; kx wait --for=condition=available deploy/db --timeout=180s >/dev/null; sleep 15; kx get pods -l app=api; kx get pods -l app=api -o jsonpath='{range .items[*]}{.status.containerStatuses[0].ready}{"\n"}{end}' | grep -c true | grep -q 2; res $? "5b api ready again after db back (no restart)"
echo "### 6 liveness toggle"; POD=$(kx get pods -l app=api -o jsonpath='{.items[0].metadata.name}'); B=$(kx get pod $POD -o jsonpath='{.status.containerStatuses[0].restartCount}'); kc "kubectl -n $NS exec $POD -- python -c \"import urllib.request,json;r=urllib.request.Request('http://127.0.0.1:8000/debug/health',data=json.dumps({'ok':False}).encode(),headers={'Content-Type':'application/json'});print(urllib.request.urlopen(r).read())\""
for i in $(seq 1 20); do sleep 5; A=$(kx get pod $POD -o jsonpath='{.status.containerStatuses[0].restartCount}'); [ "$A" -gt "$B" ] && break; done; echo "restarts before=$B after=$A ($((i*5))s)"; [ "$A" -gt "$B" ]; res $? "6 liveness restarted container"; kx get events --field-selector involvedObject.name=$POD | grep -i liveness | tail -2
echo "### 7 configmap change"; kx patch cm web-config -p '{"data":{"SITE_NAME":"ศูนย์ทดสอบ yolo1","THEME":"amber"}}' >/dev/null; kx rollout restart deploy web >/dev/null; kx rollout status deploy web --timeout=180s >/dev/null; curl -s -m 3 http://$IP/info | jq -c '{site_name,theme}'; curl -s -m 3 http://$IP/info | jq -e '.theme=="amber"' >/dev/null; res $? "7 configmap applied after restart"
node /root/workspace/DevTools/05_kubernetes/.work/tools/shot.js "http://$IP/" /root/workspace/DevTools/05_kubernetes/.work/app-screens/yolo1-amber.png --w 1280 --h 900 >/dev/null && echo "shot ok"
kx patch cm web-config -p '{"data":{"SITE_NAME":"SkillSpace","THEME":null}}' >/dev/null
echo "### 8 v1 -> v2"; kx set image deploy/web web=k8s-lab-web:v2 >/dev/null; kx rollout status deploy web --timeout=180s >/dev/null; curl -s -m 3 http://$IP/info | jq -c '{version,theme}'; curl -s -m 3 http://$IP/info | jq -e '.version=="v2" and .theme=="emerald"' >/dev/null; res $? "8 v2 image shows emerald/v2 without env"
node /root/workspace/DevTools/05_kubernetes/.work/tools/shot.js "http://$IP/" /root/workspace/DevTools/05_kubernetes/.work/app-screens/yolo1-v2.png --w 1280 --h 900 >/dev/null && echo "shot ok"; kx rollout undo deploy web >/dev/null; kx rollout status deploy web --timeout=180s >/dev/null
echo "### 9 PVC persistence"; ASSET=$(curl -s -m 3 http://$IP/api/assets | jq '.[0].id'); curl -s -m 3 -X POST http://$IP/api/tickets -H 'Content-Type: application/json' -d "{\"asset_id\":$ASSET,\"title\":\"YOLO1-PVC-CHECK\",\"detail\":\"verify\",\"priority\":\"NORMAL\"}" | jq -c '{id,title}'
OLD=$(kx get pods -l app=db -o jsonpath='{.items[0].metadata.name}'); kx delete pod $OLD --wait=true >/dev/null; kx wait --for=condition=available deploy/db --timeout=180s >/dev/null; sleep 12; NEW=$(kx get pods -l app=db -o jsonpath='{.items[0].metadata.name}'); echo "db pod $OLD -> $NEW"; curl -s -m 5 http://$IP/api/tickets | jq -r '.[].title' | grep -q YOLO1-PVC-CHECK; res $? "9 ticket survived db pod recreation (PVC)"; kx get pvc
echo "### cleanup ns"; kx delete ns $NS --wait=false 2>/dev/null; docker exec $C kubectl delete ns $NS --wait=true >/dev/null 2>&1; echo done
