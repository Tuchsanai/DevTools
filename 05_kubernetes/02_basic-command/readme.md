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
