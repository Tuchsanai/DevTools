docker exec devtools curl -s -w "\n" localhost:3000/api/health
docker exec devtools docker ps --filter label=devtools.lab=lab3 --format '{{.Names}}  {{.Status}}  build={{.Label "devtools.build"}}'
