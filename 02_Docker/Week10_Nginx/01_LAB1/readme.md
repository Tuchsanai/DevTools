## create  nodeapp 

```bash
docker build . -t nodeapp
docker run --hostname nodeapp1 --name nodeapp1 -d nodeapp
docker run --hostname nodeapp2 --name nodeapp2 -d nodeapp
docker run --hostname nodeapp3 --name nodeapp3 -d nodeapp
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
