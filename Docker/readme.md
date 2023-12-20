# Install  docker and docker-compose for ubuntu

https://docs.docker.com/engine/install/ubuntu/


### 1. Set up Docker's apt repository.

```
# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Add the current user to the Docker group
sudo usermod -aG docker $USER
sudo groupadd docker

# Add the current user to the Docker group
sudo chmod 666 /var/run/docker.sock 

# Enable and start the Docker service
sudo systemctl enable docker
sudo systemctl start docker

#  Install the Compose plugin
sudo apt-get update
sudo apt-get install docker-compose-plugin

# Print Docker and Docker Compose versions
docker --version
docker compose --version


```
