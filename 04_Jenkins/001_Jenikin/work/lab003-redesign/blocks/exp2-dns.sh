docker exec jenkins getent hosts devtools; echo "devtools exit=$?"
docker exec jenkins getent hosts jenkins; echo "jenkins exit=$?"
docker exec jenkins cat /etc/resolv.conf | grep nameserver
hostname
