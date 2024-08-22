# Kubernates

Install Kubernates for ubuntu

```
#!/bin/bash

# Update the package list and install dependencies
sudo apt-get update
sudo apt-get install -y apt-transport-https ca-certificates curl

# Download and add the Kubernetes signing key
sudo curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -

# Add the Kubernetes APT repository
sudo bash -c 'cat <<EOF >/etc/apt/sources.list.d/kubernetes.list
deb https://apt.kubernetes.io/ kubernetes-xenial main
EOF'

# Update the package list with the Kubernetes packages
sudo apt-get update

# Install Kubernetes components
sudo apt-get install -y kubelet kubeadm kubectl

# Hold the versions of these packages to prevent automatic upgrades
sudo apt-mark hold kubelet kubeadm kubectl

# Disable swap as it's required by Kubernetes
sudo swapoff -a

# Initialize the Kubernetes cluster
sudo kubeadm init --pod-network-cidr=192.168.0.0/16

# Set up the kubeconfig file for the root user
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

# Install a pod network add-on (we'll use Calico here)
kubectl apply -f https://docs.projectcalico.org/manifests/calico.yaml

# Allow the master node to run pods (since it's a single-node setup)
kubectl taint nodes --all node-role.kubernetes.io/control-plane-

echo "Kubernetes single-node setup is complete!"

# Command to check if Kubernetes is ready
kubectl get nodes
```




# Command to check if Kubernetes is ready
```
kubectl get nodes
```