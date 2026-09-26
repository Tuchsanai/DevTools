#!/bin/bash
# Usage: hub_build.sh LABEL [k=v ...] — trigger via REST (verified queue → build number), save console/params/stages to out3. Owner: yolo3.
cd "$(dirname "$0")/.."; C=$(cat container_name3); O=out3; L=$1; shift
n=$(docker exec $C /tmp/jenkins_api.sh build "$@") || { echo "trigger failed for $L"; exit 1; }
echo "$L → build #$n"; echo "$n" > $O/$L.number
docker exec $C /tmp/jenkins_api.sh wait $n > $O/b$n.json
docker exec $C /tmp/jenkins_api.sh console $n > $O/b$n.txt
docker exec $C /tmp/jenkins_api.sh params $n > $O/b$n.params
docker exec $C /tmp/jenkins_api.sh stages $n > $O/b$n.stages
cat $O/b$n.json; echo; cat $O/b$n.stages
