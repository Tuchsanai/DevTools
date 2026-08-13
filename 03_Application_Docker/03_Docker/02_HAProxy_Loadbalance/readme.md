# load balancer with HAProxy

####  ref = https://www.haproxy.com/blog/how-to-run-haproxy-with-docker

![HA proxy](./images/0.jpg)


## create directory

   
    mkdir LAB2_Week10
    cd    LAB2_Week10
    

## git clone branch dev
    
    
   ```
    git clone -b dev https://github.com/Tuchsanai/DevTools.git
    cd DevTools/02_Docker/Week10/02_HAProxy_Loadbalance/
   ```
   
   
  display the files
  
  ```
    ls -a
  ``` 

### 0. Create a custom network for your Docker containers. This allows the containers to communicate with each other.

```bash
docker network create express-network
```


## 1. Create express-app Docker Image

go to Express_Server directory

```bash
 cd  ./Express_Server
``` 

```bash
docker build -t my-express-app   . 
```


## 2. Run the Express Containers



- Run  container:

```bash
docker run -d -p 8080:3000 --network express-network -e NAME='Server 1' --name express-server-1 my-express-app
docker run -d -p 8081:3000 --network express-network -e NAME='Server 2' --name express-server-2 my-express-app

# Sleep for 2 seconds
sleep 2

# Then list all Docker containers
docker ps -a

```

## 3. Create the HAProxy Docker Image


This is config of Haproxy. you can see at path HAProxy/haproxy.cfg

```
global
    log stdout format raw local0
    maxconn 4096

defaults
    log global
    mode http
    option httplog
    option dontlognull
    timeout connect 5000ms
    timeout client 50000ms
    timeout server 50000ms

frontend http_front
    bind *:8083
    default_backend http_back

backend http_back
    balance roundrobin
    server express-server-1 express-server-1:3000 check
    server express-server-2 express-server-2:3000 check

listen stats
    bind *:8084
    stats enable
    stats uri /haproxy?stats
    stats refresh 10s
    stats auth admin:password  # Optional: Set basic authentication for stats page

```


go to HAProxy directory

```bash
cd ~
cd   LAB2_Week10/DevTools/02_Docker/Week10/02_HAProxy_Loadbalance/HAProxy/
```

- Run the HAProxy Container



```bash

docker stop haproxy
docker rm    haproxy 

docker run -d --name haproxy \
    -p 8083:8083 \
    -p 8084:8084 \
    -v $(pwd)/haproxy.cfg:/usr/local/etc/haproxy/haproxy.cfg:ro \
    --network express-network \
    haproxy:latest


# Sleep for 3 seconds
sleep 3

# Then list all Docker containers
docker ps -a


```





### 5. Testing Load Balancing:

Open your browser and go to http://ExternalIP:8083. You should see responses from your Express containers, rotating with each refresh.

![myip](./images/ip0.jpg)   



| Loab balance 1 | Loab balance 12|
|----------|----------|
|   ![Page1](./images/1.jpg)       |    ![Page1](./images/2.jpg)      |



### Delete all containers

```
docker stop $(docker ps -a -q)  
docker rm $(docker ps -a -q) 
docker rmi $(docker images -q) 
docker volume rm $(docker volume ls -q)  
docker network prune -f
```
