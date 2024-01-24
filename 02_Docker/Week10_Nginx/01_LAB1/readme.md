## create  nodeapp 

docker build . -t nodeapp
docker run --hostname nodeapp1 --name nodeapp1 -d nodeapp
docker run --hostname nodeapp2 --name nodeapp2 -d nodeapp
docker run --hostname nodeapp3 --name nodeapp3 -d nodeapp