# Lab Docker Network with Subnet 

This guide explains how to create a lab Docker network with a specific subnet using a busybox container.

### 1. Create a new Docker network named "lab_network" with a specific subnet, e.g., 192.168.100.0/24, using the following command:
```
docker network create --subnet 192.168.100.0/24 lab_network
```

### 2. To confirm that the "lab_network" has been created and to view its settings, run the following command:

```
docker network inspect lab_network

```

### 3. Run a new container with the busybox image and connect it to the "lab_network" using the following command:
```
docker run  --name busybox_container --network lab_network busybox

```

### 4 To check the IP address of a running busybox container, follow these steps:
```
docker exec -it busybox_container sh

```

```
ip addr
```

### 5. To disconnect the busybox container from the "lab_network", use the following command:
```
docker network disconnect lab_network busybox_container

```

### 6.To remove the "lab_network" when it's no longer needed, use the following command:

```
docker network rm lab_network

```