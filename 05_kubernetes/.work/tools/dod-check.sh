#!/usr/bin/env bash
# dod-check.sh — automated part of spec section 9 (Definition of Done). Prints PASS/FAIL lines.
R=/root/workspace/DevTools/05_kubernetes; cd $R; ok=0; bad=0
res(){ if [ "$1" = 0 ]; then echo "PASS  $2"; ok=$((ok+1)); else echo "FAIL  $2"; bad=$((bad+1)); fi; }
S1=01_Session1_Kubernetes_Basics; S2=02_Session2_Networking_Config_Storage; S3=03_Session3_Application_Deployment
n=$(find $S1 $S2 $S3 -maxdepth 1 -type d -name '0[0-9][0-9]-*' | wc -l); [ $n = 21 ]; res $? "21 lab folders ($n)"
seq=$(find $S1 $S2 $S3 -maxdepth 1 -type d -name '0[0-9][0-9]-*' | sed 's|.*/||' | cut -c1-3 | sort | tr '\n' ' '); [ "$seq" = "$(seq -f '%03g' 1 21 | tr '\n' ' ')" ]; res $? "lab numbering 001..021 continuous"
[ $(ls $S1 | grep -c '^00[1-7]-') = 7 ] && [ $(ls $S2 | grep -cE '^0(0[89]|1[0-4])-') = 7 ] && [ $(ls $S3 | grep -cE '^0(1[5-9]|2[01])-') = 7 ]; res $? "7 labs per session in correct session"
dirs=$(find $S1 $S2 $S3 -maxdepth 1 -type d -name '0[0-9][0-9]-*' | sort)
f=$(python3 .work/tools/check-readme.py $dirs 2>/dev/null | grep -c '^FAIL'); w=$(python3 .work/tools/check-readme.py $dirs 2>/dev/null | grep -c '^WARN'); [ $f = 0 ]; res $? "README linter: $f FAIL / $w WARN (template sections, 3-part rule, concept, footer, diagram ref, images, secrets)"
for d in $dirs; do grep -q 'การทดลองจำลองความล้มเหลว' $d/README.md || echo "   missing break: $d"; grep -q 'Clean Re-run' $d/README.md || echo "   missing clean re-run: $d"; grep -q 'แก้ปัญหาที่พบบ่อย' $d/README.md || echo "   missing troubleshooting: $d"; done
c8080=$(grep -lE 'curl[^\n]*localhost:8080' $S1/0*/README.md $S2/0*/README.md $S3/0*/README.md README.md $S1/README.md $S2/README.md $S3/README.md 2>/dev/null | wc -l); [ $c8080 = 0 ]; res $? "no in-container curl to localhost:8080 ($c8080 files)"
miss=0; for d in $dirs; do grep -q 'docker exec -it devtools-k8s bash' $d/README.md || { miss=$((miss+1)); echo "   no 'docker exec -it devtools-k8s bash': $d"; }; done; [ $miss = 0 ]; res $? "every lab enters the container ($miss missing)"
for s in $S1 $S2 $S3; do [ -f $s/README.md ]; res $? "session README $s"; done; [ -f README.md ]; res $? "root README"
python3 - <<'PY'
import re,os,sys
root='/root/workspace/DevTools/05_kubernetes'; bad=0
for f in ['README.md','01_Session1_Kubernetes_Basics/README.md','02_Session2_Networking_Config_Storage/README.md','03_Session3_Application_Deployment/README.md']:
    p=os.path.join(root,f); t=open(p,encoding='utf-8').read(); base=os.path.dirname(p)
    for l in re.findall(r'\]\(([^)#\s]+)(?:#[^)]*)?\)', t):
        if l.startswith('http'): continue
        if not os.path.exists(os.path.normpath(os.path.join(base,l))): print('   broken link', f, l); bad+=1
    if f!='README.md' and re.search(r'\.\./', t): print('   up-link in session README', f); bad+=1
print('LINKS_BAD='+str(bad))
PY
for s in $S1 $S2 $S3; do svg=$(ls $s/slides_assets/*.svg 2>/dev/null | wc -l); exc=$(ls $s/slides_assets/scenes/*.excalidraw 2>/dev/null | wc -l); ph=$(ls $s/slides_assets/photos/*.jpg 2>/dev/null | wc -l); [ $svg -ge 15 ] && [ "$svg" = "$exc" ] && [ $ph -ge 15 ]; res $? "$s assets: svg=$svg excalidraw=$exc photos=$ph"; done
for i in 1 2 3; do s=$(eval echo \$S$i); h=$s/Kubernetes_Session${i}_Slides.html; if [ -f $h ]; then out=$(node .work/tools/check-slides.js $h 2>/dev/null); python3 - "$out" "$i" <<'PY'
import json,sys; d=json.loads(sys.argv[1]); i=sys.argv[2]; nav=d['nav']
okk = not d['brokenImages'] and not d['externalRefs'] and d['externalImports']==0 and 55<=d['slides']<=90 and d['sizeMB']<=15 and len(d['labFoldersReferenced'])==7 and all(nav[k] for k in ['right','left','space','overviewVisible','helpVisible','hasProgressBar','hasCounter','hasControls']) and not d['pageErrors'] and d['imagesWithoutAlt']==0
print(('PASS  ' if okk else 'FAIL  ')+f"slides S{i}: {d['slides']} pages, {d['sizeMB']}MB, imgs={d['images']} broken={len(d['brokenImages'])} ext={len(d['externalRefs'])} labs={len(d['labFoldersReferenced'])} nav_ok={all(nav[k] for k in ['right','left','space','overviewVisible','helpVisible'])}")
PY
else echo "FAIL  slides S$i missing"; fi; done
leak=$(grep -rlE '172\.30\.|devtools-k8s-lab-|k8s-course-net|ghp_[A-Za-z0-9]{20}|sk-[A-Za-z0-9]{20}' --include='*.md' --include='*.yaml' --include='*.html' $S1 $S2 $S3 README.md app 2>/dev/null | wc -l); [ $leak = 0 ]; res $? "no production names/IPs/tokens in deliverables ($leak files)"
mail=$(grep -rhoE '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[a-z]{2,}' --include='*.md' $S1 $S2 $S3 README.md app 2>/dev/null | grep -vE 'example\.|noreply' | sort -u | head -3); [ -z "$mail" ]; res $? "no real emails (${mail:-none})"
cp=$(find . -name '.ipynb_checkpoints' -not -path './backup/*' | wc -l); [ $cp = 0 ]; res $? "no .ipynb_checkpoints ($cp)"
ct=$(docker ps -a --format '{{.Names}}' | grep -E '^devtools-k8s-(lab|app|shots|fix)' | wc -l); [ $ct = 0 ]; res $? "no leftover worker containers ($ct)"
grep -q 'v1.36.4' README.md && grep -q 'v1.37.0' README.md && grep -q 'v0.33.0' README.md && grep -q '2569_1' README.md; res $? "root README pins versions (k8s v1.36.4, kubectl v1.37.0, kind v0.33.0, image 2569_1)"
for s in $S1 $S2 $S3; do y=$(python3 .work/tools/check-yaml-teaching.py $s 2>/dev/null | grep -c '^FAIL'); [ "$y" = 0 ] && [ -f $s/YAML_Guide.md ]; res $? "YAML teaching $s: guide present, all manifests covered, anchors valid ($y FAIL)"; done
for i in 1 2 3; do s=$(eval echo \$S$i); h=$s/Kubernetes_Session${i}_Slides.html; c=$(grep -o 'กายวิภาค YAML' $h 2>/dev/null | wc -l); need=$(case $i in 1) echo 5;; 2) echo 7;; 3) echo 8;; esac); [ "$c" -ge "$need" ]; res $? "slides S$i has YAML anatomy pages ($c, need >= $need)"; done
echo "== DoD automated: $ok PASS / $bad FAIL =="
