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




Configuring Jenkins on Ubuntu to run Docker commands requires a series of steps involving installing Jenkins, Docker, and then configuring the necessary permissions for Jenkins to interact with Docker. Here's a professional, step-by-step guide to set this up:

### 1. Installing Jenkins

First, you need to install Jenkins on your Ubuntu machine. You can do this by following these steps:

1. **Update your package index:**
   ```bash
   sudo apt update
   ```

2. **Install Java (Jenkins requires Java):**
   ```bash
   sudo apt install openjdk-11-jdk
   ```

3. **Add the Jenkins repository and key:**
   ```bash
   wget -q -O - https://pkg.jenkins.io/debian/jenkins.io.key | sudo apt-key add -
   sudo sh -c 'echo deb http://pkg.jenkins.io/debian-stable binary/ > /etc/apt/sources.list.d/jenkins.list'
   ```

4. **Update your package index again:**
   ```bash
   sudo apt update
   ```

5. **Install Jenkins:**
   ```bash
   sudo apt install jenkins
   ```

6. **Start the Jenkins service:**
   ```bash
   sudo systemctl start jenkins
   ```

7. **Enable Jenkins to start at boot:**
   ```bash
   sudo systemctl enable jenkins
   ```


# If you want Jenkins to run Docker commands without needing a password, you can configure sudoers:

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







