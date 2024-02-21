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
sudo apt install -y fontconfig openjdk-17-jre
java -version


```

3. Long Term Support release

```
sudo wget -O /usr/share/keyrings/jenkins-keyring.asc \
  https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key
echo deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] \
  https://pkg.jenkins.io/debian-stable binary/ | sudo tee \
  /etc/apt/sources.list.d/jenkins.list > /dev/null
sudo apt-get update
sudo apt-get install jenkins

```


4.  Start Jenkins

```
sudo systemctl enable jenkins
sudo systemctl start jenkins
sudo systemctl status jenkins
```


## 5. Unlocking Jenkins

When you first access a new Jenkins instance, you are asked to unlock it using an automatically-generated password.



* Browse to http://localhost:8080 (or whichever port you configured for Jenkins when installing it) and wait until the Unlock Jenkins page appears.

![Unlock Jenkin](./images/setup-jenkins.jpeg)

* The command: ```sudo cat /var/lib/jenkins/secrets/initialAdminPassword``` will print the password at console


![Unlock Jenkin2](./images/setup-jenkins-02-copying-initial-admin-password.jpg)