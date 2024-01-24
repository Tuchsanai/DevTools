## create directory

    ```
    mkdir Nginx_Port_mapping
    cd Nginx_Port_mapping
    ```     

## git clone branch week8
    
    
    ```
    git clone -b week8 https://github.com/Tuchsanai/DevTools.git
    ```

    ```
    cd DevTools/Nginx_Port_mapping
    ```


## Run Nginx with port mapping

```
docker run -p 8080:80 nginx
```


![Demo](./portmap_demo1.jpg)




