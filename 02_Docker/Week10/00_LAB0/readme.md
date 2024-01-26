
### Step 1: Building Docker Images for Express Apps


```bash
# For app1
docker build -t express-app1 .

# For app2
docker build -t express-app2 .
```

### Step 2: Creating a Docker Network

Create a custom network for your Docker containers. This allows the containers to communicate with each other.

```bash
docker network create express-network
```

### Step 3: Running Express App Containers

Run the containers for `app1` and `app2` on the created network:

```bash
docker run -d --name app1 --network express-network -p 3001:3000 express-app1
docker run -d --name app2 --network express-network -p 3002:3000 express-app2
```

### Step 4: Setting Up Nginx for Load Balancing


    ```bash
    docker run -d --name nginx-load-balancer --network express-network -p 80:80 -v $(pwd)/nginx.conf:/etc/nginx/nginx.conf:ro nginx
    ```



### Instructions

- Build the Docker images for your Express applications.
- Create a Docker network for inter-container communication.
- Run the Express app containers on the custom network.
- Run an Nginx container configured as a load balancer on the same network.

Now, accessing your Docker host on port 80 will direct you through the Nginx load balancer, which then routes requests to either `app1` or `app2`. Remember, `app1` and `app2` are also accessible directly on ports 3001 and 3002, respectively.