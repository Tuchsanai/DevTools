docker exec devtools sh -c "docker ps -aq --filter label=devtools.lab=lab3 | xargs -r docker rm -f"
docker exec devtools sh -c "docker image ls -aq --filter label=devtools.lab=lab3 | sort -u | xargs -r docker image rm -f"
docker exec devtools sh -c "rm -rf /root/lab3-work /tmp/lab3-docker-*"
docker exec devtools docker ps -a --format '{{.Names}}'
docker ps --filter name=^devtools$ --filter name=^jenkins$ --format '{{.Names}}  {{.Status}}'
