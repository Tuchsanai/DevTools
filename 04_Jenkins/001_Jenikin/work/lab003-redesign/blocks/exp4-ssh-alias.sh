GW=$(docker network inspect cicd-net --format '{{range .IPAM.Config}}{{println .Gateway}}{{end}}' | grep -E '^[0-9]+(\.[0-9]+){3}$' | head -n 1)
hostname -I | tr ' ' '\n' | grep -qFx "$GW" && echo "gateway ของ cicd-net = $GW (เป็น IP ของ devtools เอง)" || { echo "หา gateway ไม่ได้ หยุดก่อน"; false; }
docker exec -i -u jenkins jenkins sh -c 'umask 077; mkdir -p ~/.ssh; cat > ~/.ssh/config' <<EOF
Host devtools-gw
  HostName $GW
  Port 22
  User root
  HostKeyAlias devtools-gw
  StrictHostKeyChecking yes
  IdentitiesOnly yes
  BatchMode yes
  ConnectTimeout 10
  LogLevel ERROR
EOF
echo "devtools-gw $(cut -d' ' -f1,2 /etc/ssh/ssh_host_ed25519_key.pub)" |
  docker exec -i -u jenkins jenkins sh -c 'umask 077; cat > ~/.ssh/known_hosts'
docker exec jenkins ls -la /var/jenkins_home/.ssh
