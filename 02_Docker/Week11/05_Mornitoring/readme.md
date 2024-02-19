
## id 
- 11074
- 1860
- 14574



## Node Exporter for Prometheus Dashboard based on 11074
## Dashboard for production env troubleshooting, 

![Alt Text](https://grafana.com/api/dashboards/15172/images/11186/image)


## Node Exporter  ID : 1860
 
![Alt Text](https://grafana.com/api/dashboards/1860/images/7994/image)


## Nvidia GPU Metrics ID: 14574

This dashboard uses the metrics exported by utkuozdemir/nvidia_gpu_exporter to provide rich visualization of various GPU stats.

![Alt Text](https://raw.githubusercontent.com/utkuozdemir/nvidia_gpu_exporter/master/grafana/dashboard.png)




## create directory

   
    mkdir LAB5_Week11
    cd    LAB5_Week11
    

## git clone branch dev
    
    
   ```
    git clone -b dev https://github.com/Tuchsanai/DevTools.git
     
    cd DevTools/02_Docker/Week11/05_Mornitoring/
   ```



## To start the services with Docker Compose, you would run:

```
docker compose up -d
```
**** display the running containers

```
docker ps -a
```

**** close the services with Docker Compose, you would run:

```
docker compose down
```

**** display the running containers

```
docker ps -a
```


### Accessing the Services by process docker-compose.yml

![pass](./images/s1.jpg)

- **Prometheus:** Access Prometheus at `http://localhost:9090`
- **Grafana:** Access Grafana at `http://localhost:3000` (default login is `admin`/`passwd`, which you'll be prompted to change)




# Delete all containers

```
docker stop $(docker ps -a -q)  
docker rm $(docker ps -a -q) 
docker rmi $(docker images -q) 
docker volume rm $(docker volume ls -q)  
docker network prune -f
```