# Excercise : Deploy Your First Kubernetes Application

## Objectives

- Build a Docker image for a Node.js application
- Deploy the application to a Kubernetes cluster

## Prerequisites

Make sure you have the following installed and set up:

- Docker
- Kubernetes cluster (either Minikube or a cloud-based Kubernetes service)
- kubectl command-line tool

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

#### 7. show all pods

```
kubectl  get pods
```
#### 8 . 

```
kubectl expose deployment first-app --type=NodePort    --type=NodePort    --port=8080  --target-port=8080
```

#### 9.   

```
kubectl get service
```
  