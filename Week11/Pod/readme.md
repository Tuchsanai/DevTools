
### 1 Create a new file called nginx-pod.yaml with the following content:

```
nano nginx-pod.yaml
```

### 2 Add the following content

```
apiVersion: v1
kind: Pod
metadata:
  name: nginx-lab
  labels:
    app: nginx
spec:
  containers:
  - name: nginx
    image: nginx:latest
    ports:
    - containerPort: 80

```



## 3.Save and close the file.
```
Ctrl+X, then Y, then Enter.
```

## 4. Create the Nginx pod

```
kubectl apply -f nginx-pod.yaml

```

## 5. Check the status of the pod

```
kubectl get pods
```


### 6. Clean up:
### When you're finished with the lab, you can delete the Nginx pod to free up resources:

```
kubectl delete pod nginx-lab

```