# Jenkins Installation on Ubuntu  
#### Goto https://www.jenkins.io/doc/book/installing/linux/

This guide provides step-by-step instructions for installing Jenkins on Ubuntu. It is based on the official documentation found at [Jenkins Official Guide](https://www.jenkins.io/doc/book/installing/linux/).

## Prerequisites

- An Ubuntu machine (Physical or Virtual)
- Internet access

## Installation Steps

1. **Update System Packages**
   Update the list of available packages and their versions.
   ```bash
   sudo apt-get update
   ```

2. Installation of Java

```
sudo apt update
sudo apt install fontconfig openjdk-17-jre
java -version
openjdk version "17.0.8" 2023-07-18
OpenJDK Runtime Environment (build 17.0.8+7-Debian-1deb12u1)
OpenJDK 64-Bit Server VM (build 17.0.8+7-Debian-1deb12u1, mixed mode, sharing)
```

3. Long Term Support release

```
curl -fsSL https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key | sudo tee \
  /usr/share/keyrings/jenkins-keyring.asc > /dev/null
echo deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] \
  https://pkg.jenkins.io/debian-stable binary/ | sudo tee \
  /etc/apt/sources.list.d/jenkins.list > /dev/null
sudo apt-get update
sudo apt-get install jenkins

```


4.  Start Jenkins

```
sudo systemctl enable jenkins
```

```
sudo systemctl start jenkins
```

```
sudo systemctl status jenkins
```