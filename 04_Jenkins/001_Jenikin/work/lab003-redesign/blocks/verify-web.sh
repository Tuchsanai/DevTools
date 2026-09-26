docker ps --filter name=^catfood-web$ --format '{{.Names}}  {{.Image}}  {{.Status}}  {{.Ports}}'
curl -s http://localhost:3000/api/health; echo
ls /root/lab3-work
