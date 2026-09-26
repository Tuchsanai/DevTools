docker network inspect cicd-net --format '{{range .IPAM.Config}}subnet={{.Subnet}} gateway={{.Gateway}}{{end}}'
docker inspect jenkins --format '{{range $n, $c := .NetworkSettings.Networks}}jenkins: {{$n}} {{$c.IPAddress}}{{end}}'
hostname -I
