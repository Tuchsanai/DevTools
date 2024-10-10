# Kubernates

## Step 1 


### 1. Set up Docker's apt repository.


```
#!/bin/bash

# Update package information
sudo apt-get update -y

# Install prerequisites
sudo apt-get install -y ca-certificates curl gnupg

# Create a directory for the Docker GPG key
sudo install -m 0755 -d /etc/apt/keyrings

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Set permissions for the GPG key
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add the Docker repository to Apt sources
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Update package information again
sudo apt-get update -y

# Install Docker packages
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin


# Enable and start the Docker service
sudo systemctl enable docker
sudo systemctl start docker


# Add the current user to the Docker group
sudo usermod -aG docker $USER
sudo groupadd docker

# Adjust permissions for the Docker socket
sudo chmod 666 /var/run/docker.sock 

# Install the Compose plugin
sudo apt-get install -y docker-compose-plugin


```

```
# Add the current user to the Docker group
sudo usermod -aG docker $USER
sudo groupadd docker
sudo chmod 666 /var/run/docker.sock 
# Print Docker and Docker Compose versions
docker --version
docker compose version

```

# Install Minikube

```

# Download and install Minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
rm minikube-linux-amd64

# Download and install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install kubectl /usr/local/bin/kubectl
rm kubectl

# Start Minikube with Docker driver
minikube start --driver=docker

# Verify installation
minikube status
kubectl get nodes

```


# Verify installation

```
kubectl get nodes
```



https://www.youtube.com/watch?v=lv0DdVLZuHc