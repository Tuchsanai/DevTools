
![Demo](./demo3.jpg)


## 1 Git clone

```
git clone https://github.com/Tuchsanai/devopt_week8.git

cd devopt_week8/node-bulletin-board-master/bulletin-board-app

```

## 3 Build Docker image
```

docker build -t bulletinboard:1.0 .


```

## 3 Run Nginx with port mapping and volume mapping

```
docker run -p 8085:8080 -d --name bb bulletinboard:1.0

```