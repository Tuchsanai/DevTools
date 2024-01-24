
![Demo](./demo3.jpg)



## create directory

   
    mkdir LAB5_node-bulletin-board-master
    cd    LAB5_node-bulletin-board-master
    

## git clone branch dev
    
    
   ```
    git clone -b dev https://github.com/Tuchsanai/DevTools.git
   ```
   
   ```   
    cd DevTools/02_Docker/Week08/LAB5_node-bulletin-board-master/bulletin-board-app
   ```



## 3 Build Docker image
```


docker build   -t bulletinboard:1.0 .


```

## 3 Run Nginx with port mapping and volume mapping

```
docker run -p 8085:8080 -d --name bb bulletinboard:1.0

```