ssh -i ~/.ssh/jenkins_devtools -o BatchMode=yes -o IdentitiesOnly=yes \
  -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
  root@127.0.0.1 'echo "key OK: $(whoami)@$(hostname)"'
