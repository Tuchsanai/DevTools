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

1. Navigate to the directory containing the Dockerfile.
2. Run the following command to build the Docker image:

```
  docker build -t kub-first-app .  
```

```
 docker tag kub-first-app  tuchsanai/kubfirstapp
```

```
docker push tuchsanai/kubfirstapp
```


3. Deploy the Docker image to a Kubernetes cluster using the following command:

```
kubectl create deployment first-app --image=tuchsanai/kub-first-app
```

4. To check the status of the deployment and see if it was successful, use the following command:

```
kubectl get deployment
```

5. 

```
kubectl  get pods
```