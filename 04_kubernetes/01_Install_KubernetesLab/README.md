# Dive Into Kubernetes - Getting Started with Containers, Docker and Kubernetes - Docker Compose - Tutorial


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

# Start Minikube
minikube start --driver=docker
```

