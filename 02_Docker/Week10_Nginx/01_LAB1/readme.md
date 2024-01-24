
## create directory

   
    mkdir LAB1_Nginx
    cd    LAB1_Nginx
    

## git clone branch dev
    
    
   ```
    git clone -b dev https://github.com/Tuchsanai/DevTools.git
   ```
   
   ```   
    cd DevTools/02_Docker/Week10_Nginx/01_LAB1
   ```   



## create  nodeapp 

```bash
docker build . -t nodeapp
docker run --hostname nodeapp1 --name nodeapp1 -d nodeapp
docker run --hostname nodeapp2 --name nodeapp2 -d nodeapp
docker run --hostname nodeapp3 --name nodeapp3 -d nodeapp
```

# show All container

```bash
docker ps -a
```

## create nginx

```bash
docker run --hostname ng1 --name nginx -p 80:8080 -v $(PWD)/nginx.conf:/etc/nginx/nginx.conf -d nginx
```

## create a docker network

```bash
docker network create backendnet
```

## connect containers to the network

```bash
docker network connect backendnet nodeapp1
docker network connect backendnet nodeapp2
docker network connect backendnet nodeapp3
docker network connect backendnet nginx
```
