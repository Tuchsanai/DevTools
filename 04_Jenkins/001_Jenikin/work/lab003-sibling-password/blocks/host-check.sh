docker ps --filter name=^devtools$ --filter name=^jenkins$ --format '{{.Names}}  {{.Status}}  {{.Ports}}'
docker network inspect cicd-net --format '{{range .Containers}}{{.Name}} {{end}}'
