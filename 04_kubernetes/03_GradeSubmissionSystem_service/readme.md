# Kubernetes Service Configurations and Lab Structure

## Service Files Detailed Explanation

### 1. grade-submission-api-service.yaml

```yaml
apiVersion: v1
kind: Service
metadata:
  name: grade-submission-api
spec:
  selector:
    app.kubernetes.io/instance: grade-submission-api
  ports:
  - port: 3000
    targetPort: 3000
```

This service file defines a Kubernetes Service for the grade submission API:
- It creates a service named "grade-submission-api".
- The selector targets pods with the label `app.kubernetes.io/instance: grade-submission-api`.
- It exposes port 3000 and routes traffic to port 3000 on the selected pods.
- This is a ClusterIP service (default type), meaning it's only accessible within the cluster.

### 2. grade-submission-portal-service.yaml

```yaml
apiVersion: v1
kind: Service
metadata:
  name: grade-submission-portal
spec:
  type: NodePort
  selector:
    app.kubernetes.io/instance: grade-submission-portal
  ports:
  - port: 5001
    targetPort: 5001
    nodePort: 32000
```

This service file defines a Kubernetes Service for the grade submission portal:
- It creates a service named "grade-submission-portal".
- The type is set to NodePort, which exposes the service on each Node's IP at a static port.
- The selector targets pods with the label `app.kubernetes.io/instance: grade-submission-portal`.
- It exposes port 5001 internally, routes traffic to port 5001 on the selected pods, and makes the service accessible externally on port 32000 of the Node's IP.

## Lab Structure and Components

- Backend (API):
   - Pod: grade-submission-api
     - Container: grade-submission-api
     - Image: rslim087/kubernetes-course-grade-submission-api:stateless
     - Port: 3000
   - Service: grade-submission-api (ClusterIP)
     - Exposes port 3000 internally

- Frontend (Portal):
   - Pod: grade-submission-portal
     - Container: grade-submission-portal
     - Image: rslim087/kubernetes-course-grade-submission-portal
     - Port: 5001
     - Environment Variable: GRADE_SERVICE_HOST=grade-submission-api
   - Service: grade-submission-portal (NodePort)
     - Exposes port 5001 internally and 32000 externally


# Full Kubernetes Lab Service 

This demo will guide you through setting up and running the grade submission application in a Kubernetes environment.


## Step 1: Prepare the Environment



1. Create a new directory for the project and navigate to it:
    
   ```
   mkdir 03_GradeSubmissionSystem_service
   ```

   ```
   cd   03_GradeSubmissionSystem_service
   ```
    
    ```
    git clone -b dev https://github.com/Tuchsanai/DevTools.git
  
    ```

    ```
    cd  DevTools/04_kubernetes/03_GradeSubmissionSystem_service
    ```



## Step 2: Deploy the API

1. Create the API pod:
   ```
   kubectl apply -f grade-submission-api-pod.yaml
   ```

2. Create the API service:
   ```
   kubectl apply -f grade-submission-api-service.yaml
   ```

3. Verify the API pod is running:
   ```
   kubectl get pods
   ```

4. Check the API service:
   ```
   kubectl get services
   ```

## Step 3: Deploy the Portal

1. Create the portal pod:
   ```
   kubectl apply -f grade-submission-portal-pod.yaml
   ```

2. Create the portal service:
   ```
   kubectl apply -f grade-submission-portal-service.yaml
   ```

3. Verify the portal pod is running:
   ```
   kubectl get pods
   ```

4. Check the portal service:
   ```
   kubectl get services
   ```

## Step 4: Verify the Setup

1. Check all running pods:
   ```
   kubectl get pods
   ```
   You should see both grade-submission-api and grade-submission-portal pods running.

2. Check all services:
   ```
   kubectl get services
   ```
   You should see both grade-submission-api and grade-submission-portal services.

3. Get more details about the portal service:
   ```
   kubectl describe service grade-submission-portal
   ```
   Note the NodePort assigned (should be 32000).

## Step 5: Access the Application


   ```
   kubectl get nodes -o wide
   ```
   - Access the application at `http://<node-ip>:32000`


## Step 6: Clean Up

When you're done with the demo, you can clean up the resources:

1. Delete the pods:
   ```
   kubectl delete pod grade-submission-api grade-submission-portal
   ```
   or 
   ```
   kubectl delete pods --all
   ```

2. Delete the services:
   ```
   kubectl delete service grade-submission-api grade-submission-portal
   ```
    or
  
    ```
    kubectl delete svc --all
    ```

