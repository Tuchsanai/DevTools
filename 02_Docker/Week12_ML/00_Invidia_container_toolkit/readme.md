##To install the NVIDIA Container Toolkit and test its functionality, follow these steps. This guide assumes you are using a Linux distribution like Ubuntu or Debian. Make sure you have Docker installed and an NVIDIA GPU with the appropriate drivers.



```
#!/bin/bash

# Set up the distribution variable
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)

# Add the NVIDIA package repository and GPG key
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

# Update package lists
sudo apt-get update

# Install the NVIDIA Container Toolkit
sudo apt-get install -y nvidia-container-toolkit

# Configure Docker to use the NVIDIA runtime
sudo nvidia-ctk runtime configure --runtime=docker

# Restart Docker to apply changes
sudo systemctl restart docker


```



# Test the installation with a CUDA container
sudo docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi