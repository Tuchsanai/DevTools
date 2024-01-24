![Alt Text](demo0.jpg)
## create directory

   
    mkdir LAB3_Week9
    cd    LAB3_Week9
    

## git clone branch dev
    
    
   ```
    git clone -b dev https://github.com/Tuchsanai/DevTools.git
   ```
   
   ```   
    cd DevTools/02_Docker/Week09/Lab3
   ```


# build Docker image with docker build 

```
docker build -t flask-docker-app . 

```


# docker run with -it option
```
docker run -p 8081:8081 -d --name container_red  -e APP_COLOR=red flask-docker-app
docker run -p 8085:8081 -d --name container_green  -e APP_COLOR=green flask-docker-app


```
