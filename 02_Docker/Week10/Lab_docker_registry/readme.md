## Lab docker registry

### Step 1: Login to Docker Hub

#### Run the following command to login to Docker Hub:

```
docker login xxx

```

### Step 2:

#### Clone

```
git clone https://github.com/Tuchsanai/devopt_week10.git
```

#### go to Directory
```
cd devopt_week10/Lab_docker_registry/
```

### Step 3: Build the Docker image


Build the Docker image with a custom tag using the following command:

```
docker build -t tuchsanai/custom-nginx-registry:1.0 .

```

Play with tag
```
docker build -t local_tuchsanai:1.0 .

```

 rename tag

```
docker tag  local_tuchsanai:1.0 tuchsanai/custom-nginx-registry:2.0
```

display image

``` 
docker images
```


### Step 4: Push the Docker image to Docker Hub

```
docker push tuchsanai/custom-nginx-registry:1.0
```

###  Step 5: Stop all Container and remove all images

```
docker stop $(docker ps -a -q)
docker rm $(docker ps -a -q)
docker rmi $(docker images -q)
```


### Step 6: Pull the Docker image from Docker Hub

```
docker pull tuchsanai/custom-nginx-registry:1.0
```


### Step 7: Run the Docker container using the pulled image with the following command:
    
```
docker run -d -p 8085:80 tuchsanai/custom-nginx-registry:1.0
```