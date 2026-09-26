docker exec jenkins sh -c 'docker version'; echo "exit=$?"
docker exec jenkins sh -c 'id; echo "HOME=$HOME"; ssh -V'
