# Grade Submission System Kubernetes Lab

This repository contains Kubernetes configurations and instructions for deploying a grade submission system consisting of a backend API and a frontend portal. This lab demonstrates basic Kubernetes concepts including pod creation, resource management, and container orchestration.

## Project Overview

The Grade Submission System consists of two main components:

1. **Grade Submission API**: A backend service that handles grade submissions.
2. **Grade Submission Portal**: A frontend application for user interaction.

Both components are containerized and deployed as Kubernetes pods, each with its own health checker.

## Prerequisites

To run this lab, you need:

- A Kubernetes cluster (local or cloud-based)
- kubectl command-line tool installed and configured
- Basic understanding of Kubernetes concepts

## Repository Structure

```
.
├── README.md
├── grade-submission-api-pod.yaml
└── grade-submission-portal-pod.yaml
```

## Kubernetes Configurations

### Grade Submission API Pod

File: `grade-submission-api-pod.yaml`

This configuration creates a pod with two containers:
- The main API container
- A health checker container

Detailed breakdown:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: grade-submission-api
  labels:
    app.kubernetes.io/name: grade-submission
    app.kubernetes.io/component: backend
    app.kubernetes.io/instance: grade-submission-api
spec:
  containers:
  - name: grade-submission-api
    image: rslim087/kubernetes-course-grade-submission-api:stateless
    resources:
      requests:
        memory: "128Mi"
        cpu: "128m"
      limits:
        memory: "128Mi"
    ports:
      - containerPort: 3000
  - name: grade-submission-api-health-checker
    image: rslim087/kubernetes-course-grade-submission-api-health-checker
    resources:
      requests:
        memory: "128Mi"
        cpu: "200m"
      limits:
        memory: "128Mi"
```

- The pod is named `grade-submission-api` and labeled for easy identification.
- It contains two containers:
  1. `grade-submission-api`: The main API container
     - Uses the image `rslim087/kubernetes-course-grade-submission-api:stateless`
     - Requests 128Mi of memory and 128m (12.8%) of CPU
     - Exposes port 3000
  2. `grade-submission-api-health-checker`: A separate container for health checks
     - Uses a specific health checker image
     - Requests 128Mi of memory and 200m (20%) of CPU
- Both containers have memory limits set to 128Mi

### Grade Submission Portal Pod

File: `grade-submission-portal-pod.yaml`

This configuration creates a pod with two containers:
- The main portal container
- A health checker container

Detailed breakdown:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: grade-submission-portal
  labels:
    app.kubernetes.io/name: grade-submission
    app.kubernetes.io/component: frontend
    app.kubernetes.io/instance: grade-submission-portal
spec:
  containers:
  - name: grade-submission-portal
    image: rslim087/kubernetes-course-grade-submission-portal
    resources:
      requests:
        memory: "128Mi"
        cpu: "200m"
      limits:
        memory: "128Mi"
    ports:
      - containerPort: 5001  
  - name: grade-submission-portal-health-checker
    image: rslim087/kubernetes-course-grade-submission-portal-health-checker
    resources:
      requests:
        memory: "128Mi"
        cpu: "200m"
      limits:
        memory: "128Mi"
```

- The pod is named `grade-submission-portal` and labeled as a frontend component.
- It contains two containers:
  1. `grade-submission-portal`: The main portal container
     - Uses the image `rslim087/kubernetes-course-grade-submission-portal`
     - Requests 128Mi of memory and 200m (20%) of CPU
     - Exposes port 5001
  2. `grade-submission-portal-health-checker`: A separate container for health checks
     - Uses a specific health checker image
     - Requests 128Mi of memory and 200m (20%) of CPU
- Both containers have memory limits set to 128Mi

## Lab Instructions

Follow these steps to deploy and manage the Grade Submission System:

0. Create directory

```
mkdir 02_GradeSubmissionSystem_pod
cd   02_GradeSubmissionSystem_pod
```

1. Clone this repository:
   ```
   git clone -b dev https://github.com/Tuchsanai/DevTools.git
  
   ```

  ```
    cd  DevTools/04_kubernetes/03_GradeSubmissionSystem_pod
  ```


2. Deploy the Grade Submission API pod:
   ```
   kubectl apply -f grade-submission-api-pod.yaml
   ```

3. Deploy the Grade Submission Portal pod:
   ```
   kubectl apply -f grade-submission-portal-pod.yaml
   ```

4. Verify that the pods are running:
   ```
   kubectl get pods
   ```

5. Inspect pod details:

   Inspect : grade-submission-api

   ```
   kubectl describe pod grade-submission-api
   ```

   Inspect : grade-submission-portal
   ```
   kubectl describe pod grade-submission-portal
   ```

6. Check pod inside logs:
   
   check inside grade-submission-api
   ```
   kubectl logs grade-submission-api -c grade-submission-api
   ```

 check inside grade-submission-portal
  
  ```
      kubectl logs grade-submission-portal -c grade-submission-portal
  ```



## Resource Specifications

Both pods use the following resource specifications:

- Memory: 128Mi (128 Mebibytes ≈ 134.2 Megabytes)
- CPU: 
  - API: 128m (12.8% of a CPU core) for the main container, 200m (20%) for the health checker
  - Portal: 200m (20% of a CPU core) for both containers

These specifications are used in the resource requests and limits sections of the pod configurations. The use of resource requests ensures that the pods are scheduled on nodes with sufficient resources, while limits prevent the containers from consuming more than the specified amount of resources.

## Cleanup

- To remove the deployed pods:

**Verify that the pods are running:

```
   kubectl get pods
```

```
kubectl delete pod grade-submission-api
kubectl delete pod grade-submission-portal
```


- To remove all deployed pods at once, use the following command:

** create pod
```
   kubectl apply -f grade-submission-api-pod.yaml
   kubectl apply -f grade-submission-portal-pod.yaml
```
**Verify that the pods are running:
```
   kubectl get pods
```

** delete all pod
```
kubectl delete pod --all
```

```
   kubectl get pods
```
