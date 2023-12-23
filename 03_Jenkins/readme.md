# Jenkins Installation on Ubuntu  
#### Goto https://www.jenkins.io/doc/book/installing/linux/

This guide provides step-by-step instructions for installing Jenkins on Ubuntu. It is based on the official documentation found at [Jenkins Official Guide](https://www.jenkins.io/doc/book/installing/linux/).

## Prerequisites

- An Ubuntu machine (Physical or Virtual)
- Internet access

## Installation Jenkins Steps

1. **Update System Packages**
   Update the list of available packages and their versions.
   ```bash
   sudo apt-get update 
   ```

2. Installation of Java

```
sudo apt update -y
sudo apt install fontconfig openjdk-17-jre -y
java -version

```

3.  install Jenkins through Long Term Support release

```
sudo wget -O /usr/share/keyrings/jenkins-keyring.asc \
  https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key
echo deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] \
  https://pkg.jenkins.io/debian-stable binary/ | sudo tee \
  /etc/apt/sources.list.d/jenkins.list > /dev/null
sudo apt-get update
sudo apt-get install jenkins -y
```



4.  Start Jenkins


```
sudo systemctl enable jenkins
sudo systemctl start jenkins
sudo systemctl status jenkins
```

5.  Unlocking Jenkins with password


```
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
```

## Installing Docker

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

# Add the current user to the Docker group
sudo usermod -aG docker $USER
sudo groupadd docker

# Adjust permissions for the Docker socket
sudo chmod 666 /var/run/docker.sock 

# Enable and start the Docker service
sudo systemctl enable docker
sudo systemctl start docker

# Install the Compose plugin
sudo apt-get install -y docker-compose-plugin

# Print Docker and Docker Compose versions
docker --version
docker compose version

```


**check docker installation**

```
docker --version
docker compose version
```


## If you want Jenkins to run Docker commands without needing a password, you can configure sudoers:

1. **Edit the sudoers file:**
   ```bash
   sudo visudo
   ```

2. **Add the following line to allow Jenkins to run all commands without a password:**
   ```
   jenkins ALL=(ALL) NOPASSWD: ALL
   ```
   Alternatively, for a more secure approach, only allow Docker commands:
   ```
   jenkins ALL=(ALL) NOPASSWD: /usr/bin/docker
   ```

3. **Restart Jenkins:**
   ```bash
   sudo systemctl restart jenkins
   ```







