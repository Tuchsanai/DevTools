docker exec -u root jenkins sh -c "apt-get update -qq && apt-get install -y -qq --no-install-recommends sshpass"
docker exec jenkins sh -c "command -v sshpass; command -v docker || echo 'docker: none'"
