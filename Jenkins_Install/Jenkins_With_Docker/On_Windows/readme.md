## Reference https://www.jenkins.io/doc/book/installing/docker/

## Create a bridge network in Docker using the following docker network create command

```
docker network create jenkins
```

## Run a docker:dind Docker image


```
docker run --name jenkins-docker --rm --detach ^
  --privileged --network jenkins --network-alias docker ^
  --env DOCKER_TLS_CERTDIR=/certs ^
  --volume jenkins-docker-certs:/certs/client ^
  --volume jenkins-data:/var/jenkins_home ^
  --publish 2376:2376 ^
  docker:dind
```

## Build a new docker image from this Dockerfile and assign the image a meaningful name, e.g. "myjenkins-blueocean:2.414.1-1":
```
docker build -t myjenkins-blueocean:2.414.1-1 .
```

## Run your own myjenkins-blueocean:2.414.1-1 image as a container in Docker using the following docker run command:

```
docker run --name jenkins-blueocean --restart=on-failure --detach ^
  --network jenkins --env DOCKER_HOST=tcp://docker:2376 ^
  --env DOCKER_CERT_PATH=/certs/client --env DOCKER_TLS_VERIFY=1 ^
  --volume jenkins-data:/var/jenkins_home ^
  --volume jenkins-docker-certs:/certs/client:ro ^
  --publish 8080:8080 --publish 50000:50000 myjenkins-blueocean:2.414.1-1
```