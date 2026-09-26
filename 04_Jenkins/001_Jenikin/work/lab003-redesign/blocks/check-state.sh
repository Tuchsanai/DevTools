docker ps --filter name=^jenkins$ --format '{{.Names}}  {{.Image}}  {{.Status}}'
docker network inspect cicd-net --format '{{.Name}} {{range .IPAM.Config}}{{.Subnet}} gw {{.Gateway}}{{end}}'
docker volume ls --filter name=jenkins_home
