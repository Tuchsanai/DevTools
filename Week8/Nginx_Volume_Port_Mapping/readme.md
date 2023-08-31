
![Demo](./mydemo2.jpg)

## 1 Git clone

```
git clone https://github.com/Tuchsanai/devopt_week8.git

cd devopt_week8/Nginx_Volume_Port_Mapping

```

## 2 Run Nginx with port mapping and volume mapping

```

docker run -d -p 8083:80 -v ${PWD}/web_demo:/usr/share/nginx/html:ro  nginx

```