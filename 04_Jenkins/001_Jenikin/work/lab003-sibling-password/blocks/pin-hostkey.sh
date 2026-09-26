docker exec devtools sh -c "sed 's/^/devtools /' /etc/ssh/ssh_host_ed25519_key.pub > /tmp/devtools.known_hosts"
docker cp devtools:/tmp/devtools.known_hosts devtools.known_hosts
docker cp devtools.known_hosts jenkins:/tmp/devtools.known_hosts
docker exec jenkins sh -c "mkdir -p -m 700 /var/jenkins_home/.ssh && cp /tmp/devtools.known_hosts /var/jenkins_home/.ssh/known_hosts"
docker exec devtools ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub
docker exec jenkins ssh-keygen -lF devtools
