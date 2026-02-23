## create directory

   
    mkdir LAB4_Week9_Backend
    cd    LAB4_Week9_Backend
    

## git clone branch dev
    
    
   ```
    git clone -b dev https://github.com/Tuchsanai/DevTools.git
   ```
   
   ```   
    cd DevTools/02_Docker/Week09/Lab4/backend
   ```



### build Docker image with docker build 
```
docker build -t fastapi-docker_lab4 .
```

### Run the Docker container by executing the following command:
```
docker run -d -p 8088:80 fastapi-docker_lab4
```

![Demo](./output.jpg)