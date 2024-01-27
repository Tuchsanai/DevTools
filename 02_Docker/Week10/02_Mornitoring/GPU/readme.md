To set up monitoring for server performance using Prometheus, Grafana, and Node Exporter in Docker containers, follow these steps.


## create directory

   
    mkdir LAB2_GPU_Week10
    cd    LAB2_GPU_Week10
    

## git clone branch dev
    
    
   ```
    git clone -b dev https://github.com/Tuchsanai/DevTools.git
   ```
   
   ```   
    cd DevTools/02_Docker/Week10/02_Mornitoring/GPU
   ```





### Step 1: Create a Docker Network
First, create a Docker network to connect the containers:
```bash
docker network create monitoring
```

### Step 2: Run Node Exporter abd Prometheus
Run Node Exporter in a Docker container:
```bash
docker run -d --name=node-exporter --net=monitoring prom/node-exporter
```

Run nvidia_gpu_exporter
```bash

docker run -d \
  --name nvidia_smi_exporter \
  --restart unless-stopped \
  --device /dev/nvidiactl:/dev/nvidiactl \
  --device /dev/nvidia0:/dev/nvidia0 \
  -v /usr/lib/x86_64-linux-gnu/libnvidia-ml.so:/usr/lib/x86_64-linux-gnu/libnvidia-ml.so \
  -v /usr/lib/x86_64-linux-gnu/libnvidia-ml.so.1:/usr/lib/x86_64-linux-gnu/libnvidia-ml.so.1 \
  -v /usr/bin/nvidia-smi:/usr/bin/nvidia-smi \
  -p 9835:9835 \
  --net=monitoring \
  utkuozdemir/nvidia_gpu_exporter:1.1.0

```


Run Prometheus in a Docker container, mounting the configuration file:
```bash
docker run -d --name=prometheus --net=monitoring -p 9090:9090 -v ./prometheus.yml:/etc/prometheus/prometheus.yml prom/prometheus
```



### Step 4: Grafana Configuration

Run Grafana, mounting the configuration files and dashboard directory:

```bash
docker run -d --name=grafana --net=monitoring -p 3000:3000 -v ./datasources.yaml:/etc/grafana/provisioning/datasources/datasources.yaml -v ./dashboards.yaml:/etc/grafana/provisioning/dashboards/dashboards.yaml -v ./grafana-dashboards:/var/lib/grafana/dashboards grafana/grafana
```
### Test Monitoring
- Grafana will be available at `http://localhost:3000` (default login is `admin`/`admin`, which you'll be prompted to change). 

| Step 1 | Step 2 | Step  3 |
|-----------|-----------|-----------|
| ![Image 1](./images/grafana_login.jpg) | ![Image 2](./images/grafana_login2.jpg) | ![Image 3](./images/grafana_login3.jpg)|
| Step 4 | Step 5 | end |
| ![Image 4](./images/grafana_login4.jpg) | ![Image 5](./images/grafana_login5.jpg) |   | 



### Accessing the Services
- **Prometheus:** Access Prometheus at `http://localhost:9090`
- **Grafana:** Access Grafana at `http://localhost:3000` (default login is `admin`/`admin`, which you'll be prompted to change)

This setup will get you started with monitoring server performance using Docker containers for Prometheus, Grafana, and Node Exporter. Remember, you might need to adjust firewall rules or Docker settings depending on your server configuration.




# Delete all containers

```
docker stop $(docker ps -a -q)  
docker rm $(docker ps -a -q) 
docker rmi $(docker images -q) 
docker volume rm $(docker volume ls -q)  
docker network prune -f
```
