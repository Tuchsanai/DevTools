#!/usr/bin/env bash
# launch.sh <name> <outfile> <promptfile>  — detached cyolo1 job; writes .work/logs/<name>.log and <name>.done
NAME=$1; OUT=$2; PROMPT=$3
H=/tmp/claude-0/-root-workspace-DevTools-05-kubernetes/9011f9c5-af90-427b-8502-db533a0e0096/scratchpad/k8s-helpers.sh
LOG=/root/workspace/DevTools/05_kubernetes/.work/logs/$NAME.log
rm -f "$LOG.done"
nohup setsid bash -c "source $H; cd \$ROOT; date +'START %F %T' > '$LOG'; do_heavy '$OUT' \"\$(cat '$PROMPT')\" >> '$LOG' 2>&1; echo EXIT=\$? >> '$LOG'; date +'END %F %T' >> '$LOG'; touch '$LOG.done'" > /dev/null 2>&1 &
echo "launched $NAME pid=$!"
