# Week 8

# install docker with shell script on Ubuntu 22.04

Create a new file named install-git-docker.sh using the command 

```
nano install-git-docker.sh 
```
or any other text editor you prefer.

# Add the following lines to the file:
    
```
#!/bin/bash

# Update the package list
sudo apt update

# Install Git
sudo apt install git -y

# Install Docker
sudo apt install docker.io -y

# Add the current user to the Docker group
sudo usermod -aG docker ${USER}

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Make the Docker Compose binary executable
sudo chmod +x /usr/local/bin/docker-compose

# Enable Docker service
sudo systemctl enable docker.service

# Enable Docker Compose
sudo systemctl enable docker-compose.service

```

# Save the file by pressing 
```
Ctrl+X, then Y, then Enter.
```
# Make the file executable using the command 
```
chmod +x install-git-docker.sh
```
# Run the script using the command 
```
./install-git-docker.sh
```

# Allow to run docker without sudo

```
sudo usermod -aG docker $USER

```