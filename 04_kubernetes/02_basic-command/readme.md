##### Open a terminal window and run the following command to check the version of kubectl:

```
kubectl version
```

##### displays a table of all the nodes in the cluster

```
kubectl get node
```

#### display all the namespaces in the cluster, including their names, statuses
```
kubectl get namespace
```



## Get information about resources in a specific namespace:

##### To get all pods across all namespaces in Kubernetes 

```
kubectl get pods --all-namespaces
```

##### Get a list of all pods in the kube-system namespace:

```
kubectl get pods -n kube-system
```

##### Get a list of all services in the kube-system namespace:
``` 
kubectl get services -n kube-system
```

##### Get a list of all deployments in the kube-system namespace:
``` 
kubectl get deployments -n kube-system

```

## Get familiar with the kubectl describe command


#### 1. display all the namespaces in the cluster, including their names, statuses
```
kubectl get namespace
```



#### 2. Check the kube-system namespace by running the following command:
```
kubectl get namespace kube-system
```



#### You should see output similar to the following:
```
NAME          STATUS   AGE
kube-system   Active   69m
```




#### 3. Use the kubectl describe kube-system namespace::
```
kubectl describe namespace kube-system

```

#### Describe a specific resource pods

```
kubectl get pods -n kube-system
```
You should see output similar to the following:

```
NAME                               READY   STATUS    RESTARTS      AGE
coredns-787d4945fb-88fqf           1/1     Running   0             75m
etcd-minikube                      1/1     Running   0             75m
kube-apiserver-minikube            1/1     Running   0             75m
kube-controller-manager-minikube   1/1     Running   0             75m
kube-proxy-9pgvb                   1/1     Running   0             75m
kube-scheduler-minikube            1/1     Running   0             75m
storage-provisioner                1/1     Running   1 (74m ago)   75m
```



```
kubectl describe pod coredns-787d4945fb-88fqf -n kube-system
```