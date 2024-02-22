# Dive Into Kubernetes


Here's a basic script to get you started. This script:

1. Installs `curl`, `docker.io`, and `conntrack` (required by Minikube).
2. Installs the latest version of `kubectl`.
3. Installs the latest version of Minikube.
4. Starts Minikube with Docker driver.

```bash
#!/bin/bash

# Update and Install Required Tools
sudo apt-get update -y
sudo apt-get install -y curl docker.io conntrack

# Install kubectl
sudo curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo chmod +x ./kubectl
sudo mv ./kubectl /usr/local/bin/kubectl

# Install Minikube
curl -Lo minikube https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
chmod +x minikube
sudo mv minikube /usr/local/bin/

```


### Start Minikube

```bash
minikube start --driver=docker
```
### After starting Minikube, you can launch the Kubernetes dashboard by running:




To check if Kubernetes is working, you typically want to verify the status of the cluster, nodes, and pods. Here’s a step-by-step guide on how to do this using `kubectl`, which is the Kubernetes command-line tool. Before proceeding, ensure that `kubectl` is installed and configured to communicate with your cluster.

1. **Check Cluster Health:**
   First, you want to ensure that your Kubernetes cluster is up and running. You can do this by checking the health status of the cluster.

   ```bash
   kubectl cluster-info
   ```

   This command will display the Kubernetes master and the KubeDNS services if your cluster is up.

2. **Get Nodes Status:**
   Next, check the status of the nodes in your cluster. Nodes are the physical or virtual machines where Kubernetes runs your applications.

   ```bash
   kubectl get nodes
   ```

   This command lists all nodes attached to the cluster and shows their status as Ready, NotReady, or Unknown. A node in the Ready state is working correctly.

3. **Check Pods Status:**
   Pods are the smallest deployable units in Kubernetes, and they host your application instances. Checking the status of your pods can help you verify if your applications are running as expected.

   ```bash
   kubectl get pods --all-namespaces
   ```

   This command lists all pods in all namespaces, along with their status. You’re looking for pods in the Running or Completed state, depending on the nature of your application.

4. **Check Deployments:**
   Deployments represent a set of multiple, identical pods. A Deployment runs multiple replicas of your application and automatically replaces any instances that fail or become unresponsive.

   ```bash
   kubectl get deployments
   ```

   This will show you the current deployments, their desired and current states, and how many are up to date and available.

5. **Check Services:**
   Services in Kubernetes are an abstract way to expose an application running on a set of Pods as a network service.

   ```bash
   kubectl get services
   ```
