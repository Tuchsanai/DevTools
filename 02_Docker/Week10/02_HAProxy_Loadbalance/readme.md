# load balancer with HAProxy



## create directory

   
    mkdir LAB2_Week10
    cd    LAB2_Week10
    

## git clone branch dev
    
    
   ```
    git clone -b dev https://github.com/Tuchsanai/DevTools.git
   ```
   
   ```   
    cd DevTools/02_Docker/Week10/02_HAProxy_Loadbalanc
   ```



## 1. Create express-app Docker Image

```
docker build -t my-express-app  -f ./Express_Server/Dockerfile . 
```


## 2. Run the Express Containers

- Run the first container:

```bash
docker run -d -p 8080:3000 -e NAME='Server 1' --name express-server-1 my-express-app
```
- Run the second container:

```bash
docker run -d -p 8081:3000 -e NAME='Server 2' --name express-server-2 my-express-app
```

## 3. Create the HAProxy Docker Image

```bash
docker build -t my-haproxy -f ./HAProxy/Dockerfile .
```

- Run the HAProxy Container

```bash
docker run -d -p 8083:80 --name my-haproxy my-haproxy
```

### 5. Testing:

Open your browser and go to http://localhost:8083. You should see responses from your Express containers, rotating with each refresh.


Important Notes:

HAProxy health checks (check in the config) are recommended for production.
Consider network configuration or using an internal Docker network if running on a remote server.



# Delete all containers

```
docker stop $(docker ps -a -q)  
docker rm $(docker ps -a -q) 
docker rmi $(docker images -q) 
docker volume rm $(docker volume ls -q)  
docker network prune -f
```