# Excercise : Deploy Your First Kubernetes Application

## Objectives

- Build a Docker image for a Node.js application
- Deploy the application to a Kubernetes cluster

## Prerequisites

Make sure you have the following installed and set up:

- Docker
- Kubernetes cluster (either Minikube or a cloud-based Kubernetes service)
- kubectl command-line tool


** Hint
he kubectl expose command in Kubernetes is used to create a new service that exposes an existing resource within the cluster. This command is typically used to expose deployments, pods, or other resources as services, making them accessible to other parts of your cluster or external clients.

# `kubectl expose` Command Reference

The `kubectl expose` command in Kubernetes is used to create a new service that exposes an existing resource within the cluster. This table provides a reference for using the `kubectl expose` command with both `--port` and `--target-port` options.

| Command                                   | Description                                   | Example                                  |
|-------------------------------------------|-----------------------------------------------|------------------------------------------|
| `kubectl expose deployment <deployment-name> --port=<port> --target-port=<target-port>`  | Expose a deployment with a specific port and target port | `kubectl expose deployment my-deployment --port=80 --target-port=8080` |
| `kubectl expose pod <pod-name> --port=<port> --target-port=<target-port>`  | Expose a pod with a specific port and target port   | `kubectl expose pod my-pod --port=8080 --target-port=80`   |
| `kubectl expose service <service-name> --port=<port> --target-port=<target-port>`  | Expose an existing service with specific port and target port | `kubectl expose service my-service --port=8081 --target-port=8080` |
| `kubectl expose <resource-type> <resource-name> --port=<port> --target-port=<target-port>`  | Expose various Kubernetes resources with specified ports and target ports | `kubectl expose deployment my-deployment --port=8080 --target-port=80` |

These `kubectl expose` commands allow you to create services with customized port and target port configurations, enabling effective communication within your Kubernetes cluster.


## Steps

### Build the Docker Image

#### 1. Navigate to the directory containing the Dockerfile.
#### 2. Run the following command to build the Docker image:

```
  docker build -t kub-first-app .  
```

#### 3. Tag the Docker image with the desired repository name and version
```
 docker tag kub-first-app tuchsanai/kubfirstapp:version1.0
```

#### 4. Push image from local to DockerHub
```
docker push tuchsanai/kubfirstapp:version1.0
```

Delete all images
```
docker rmi $(docker images -a -q)
```


#### 5. Deploy the Docker image to a Kubernetes cluster using the following command:

```
kubectl create deployment first-app --image=tuchsanai/kubfirstapp:version1.0
```

#### 6. To check the status of the deployment and see if it was successful, use the following command:

```
kubectl get deployment
```

#### 7. show all pods and service

```
kubectl  get pods
```

```
kubectl get service
```

#### 8 . Create New service by   kubectl expose command 

```
kubectl expose deployment first-app --type=NodePort    --type=NodePort    --port=8080  --target-port=8080
```

#### 9.  service which created by kubectl expose


```
kubectl get service
```
  
#####  10. Test url from kubectl get service

```
url:port
```


#### 11 scale deployment

```
kubectl scale deployment/first-app  --replicas=3
```

##### Check Scale 
```
kubectl get pods -o wide
```
