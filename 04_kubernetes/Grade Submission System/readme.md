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

### Grade Submission Portal Pod

File: `grade-submission-portal-pod.yaml`

This configuration creates a pod with two containers:
- The main portal container
- A health checker container

## Lab Instructions

Follow these steps to deploy and manage the Grade Submission System:

1. Clone this repository:
   ```
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Deploy the Grade Submission API pod:



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

```
Certainly, I'd be happy to explain the memory and CPU specifications you're asking about.
In Kubernetes resource requests and limits, "128Mi" for memory and "200m" for CPU have specific meanings:

Memory: "128Mi"

"Mi" stands for Mebibyte (1 Mebibyte = 1,048,576 bytes)
"128Mi" means 128 Mebibytes, which is approximately 134.2 Megabytes
This specifies that the container requests or is limited to 128 Mebibytes of memory


CPU: "200m"

"m" stands for milliCPU or millicores
1000m is equivalent to 1 full CPU core
"200m" means 200 millicores, which is 0.2 or 20% of a single CPU core
This specifies that the container requests or is limited to 20% of a CPU core



These values are used in the resource requests and limits sections of the Kubernetes pod specifications. Here's a brief explanation of requests vs. limits:

```

   ```
   kubectl apply -f grade-submission-api-pod.yaml
   ```

3. Deploy the Grade Submission Portal pod:


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



   ```
   kubectl apply -f grade-submission-portal-pod.yaml
   ```

4. Verify that the pods are running:
   ```
   kubectl get pods
   ```

5. Inspect pod details:
   ```
   kubectl describe pod grade-submission-api
   kubectl describe pod grade-submission-portal
   ```

6. Check pod logs:
   ```
   kubectl logs grade-submission-api -c grade-submission-api
   kubectl logs grade-submission-portal -c grade-submission-portal
   ```

## Resource Specifications

Both pods use the following resource specifications:

- Memory: 128Mi (128 Mebibytes ≈ 134.2 Megabytes)
- CPU: 
  - API: 128m (12.8% of a CPU core)
  - Portal: 200m (20% of a CPU core)

These specifications are used in the resource requests and limits sections of the pod configurations.

## Cleanup

To remove the deployed pods:

```
kubectl delete pod grade-submission-api
kubectl delete pod grade-submission-portal
```

## Contributing

Contributions to improve the lab or extend its functionality are welcome. Please follow these steps:

1. Fork the repository
2. Create a new branch for your feature
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request





