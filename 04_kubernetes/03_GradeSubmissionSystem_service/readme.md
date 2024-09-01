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

1. Backend (API):
   - Pod: grade-submission-api
     - Container: grade-submission-api
     - Image: rslim087/kubernetes-course-grade-submission-api:stateless
     - Port: 3000
   - Service: grade-submission-api (ClusterIP)
     - Exposes port 3000 internally

2. Frontend (Portal):
   - Pod: grade-submission-portal
     - Container: grade-submission-portal
     - Image: rslim087/kubernetes-course-grade-submission-portal
     - Port: 5001
     - Environment Variable: GRADE_SERVICE_HOST=grade-submission-api
   - Service: grade-submission-portal (NodePort)
     - Exposes port 5001 internally and 32000 externally

3. Networking:
   - The frontend pod communicates with the backend service using the hostname "grade-submission-api" (set via environment variable).
   - External users access the frontend through the NodePort service on port 32000.
   - The backend is not directly accessible from outside the cluster.

4. Resource Management:
   - Both pods have resource requests and limits defined:
     - API: 128Mi memory, 128m CPU
     - Portal: 128Mi memory, 200m CPU

5. Labels and Selectors:
   - Pods are labeled with app.kubernetes.io/name, app.kubernetes.io/component, and app.kubernetes.io/instance.
   - Services use the app.kubernetes.io/instance label to select the correct pods.

