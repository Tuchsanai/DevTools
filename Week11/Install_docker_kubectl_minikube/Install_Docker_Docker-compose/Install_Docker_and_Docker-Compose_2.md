# Installation Docker and Docker Compose and Minikube and kubectl Installation Script for Ubuntu 22.04



## Prerequisites

- Ubuntu 22.04 machine
- User with sudo privileges

## Installation Docker and Docker Compose on Ubuntu 22.04Steps

1. Open your terminal and type the following command to create a new shell script file using the vi editor:

    ```bash
    vi install_docker_docker-compose.sh
    ```

2. Press `i` to go into insert mode, then copy and paste the following shell script code into the editor:

```
#!/bin/bash -e


# Update package list and install dependencies
sudo apt update
sudo apt install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Add Docker’s official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker APT repository
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Update the package index and install Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# Enable and start Docker
sudo systemctl enable docker
sudo systemctl start docker

# Change permissions of Docker socket (Not Recommended for production)
sudo chmod 666 /var/run/docker.sock

# Add the current user to the Docker group
sudo usermod -aG docker $USER

# Install Docker Compose
echo "Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

echo "Installation complete. Please log out and log back in for changes to take effect."

# Verify Docker Installation using sudo to avoid permission issues
sudo docker --version
# Verify Docker Compose Installation
sudo docker-compose --version

```


3. Press ESC to exit insert mode.

4. Type :wq and press Enter to save the file and exit the vi editor.

5. Give the script executable permissions:

    ```bash
    chmod +x install_docker_docker-compose.sh
    ```


6. Run the script as a superuser:

```
sudo ./install_docker_docker-compose.sh
```