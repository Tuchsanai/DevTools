# 🚀 Load Balancer with Nginx + Docker

This lab demonstrates how to use **Nginx** as a load balancer for multiple **Express.js containers**.  
You will learn about **Round Robin** and **Weighted Round Robin** strategies.

---

## 📌 Load Balancing Concepts

### 🔄 Round Robin
Each request is distributed sequentially across servers.

![Round Robin](round.png)

**nginx.conf**

```nginx
events {}

http {
  upstream food-app {
    server food-server1:5000;
    server food-server2:3000;  
    server food-server3:8000;  

  }

  server {
    listen 80;

    location / {
      proxy_pass http://food-app;
    }
  }
}
````

---

### ⚖️ Weighted Round Robin

Servers get different weights (priority).
Example: server1 gets 3 requests for every 2 requests sent to server2.

![Weighted Round Robin](weight.png)

**nginx.conf**

```nginx
# Example weight 3:2
events {}

http {
  upstream food-app {
    server food-server:5000 weight=3;
    server gin-test:3000 weight=2;  
  }

  server {
    listen 80;

    location / {
      proxy_pass http://food-app;
    }
  }
}
```

---

## 🧪 LAB A: Round Robin

### 1️⃣ Setup Project Directory

```bash
mkdir LAB1_Week10
cd LAB1_Week10
```

### 2️⃣ Clone Git Repository

```bash
git clone -b dev https://github.com/Tuchsanai/DevTools.git
cd DevTools/02_Docker/Week10/01_LAB1_Nginx_LoadBalance
```

### 3️⃣ Build Express App Image

```bash
docker build -t express-app .
```

### 4️⃣ Create Docker Network

```bash
docker network create express-network
```

### 5️⃣ Run Express App Containers

```bash
docker run -d --name app1 --network express-network -p 3001:3000 express-app
docker run -d --name app2 --network express-network -p 3002:3000 express-app
```

👉 Check containers:

```bash
docker ps -a
```

### 6️⃣ Configure & Run Nginx Load Balancer

Create **nginx.conf**:

```nginx
events {}

http {
    upstream backend {
        server app1:3000;
        server app2:3000;
    }

    server {
        listen 8080;

        location / {
            proxy_pass http://backend;
        }
    }
}
```

Run Nginx container:

```bash
docker run -d --name nginx-load-balancer \
  --network express-network \
  -p 8080:8080 \
  -v ./nginx.conf:/etc/nginx/nginx.conf:ro \
  nginx
```

👉 Check Nginx container:

```bash
docker ps -a
```

### 7️⃣ Test Load Balancing

Open browser:
[http://ExternalIP:8080](http://ExternalIP:8080)

You should see alternating responses from `app1` and `app2`.

| From App1      | From App2      |
| -------------- | -------------- |
| ![App1](1.jpg) | ![App2](2.jpg) |

---

## 🧪 LAB B: Weighted Round Robin

👉 Try setting up your own **weighted configuration** using the above example (3:2).

---

## 🧹 Cleanup

Stop and remove all containers, images, volumes, and networks:

```bash
docker stop $(docker ps -a -q)  
docker rm $(docker ps -a -q) 
docker rmi $(docker images -q) 
docker volume rm $(docker volume ls -q)  
docker network prune -f
```

---

✅ Congratulations! You’ve successfully deployed a **Dockerized Nginx Load Balancer** 🎉

```

