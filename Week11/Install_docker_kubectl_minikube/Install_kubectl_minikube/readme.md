#  install kubectl and minikube on Ubuntu 22.04

To install kubectl and minikube on Ubuntu 22.04 using a .sh file, you can follow the instructions from the official websites for Minikube and Kubernetes.
https://minikube.sigs.k8s.io/docs/start/ and  https://kubernetes.io/docs/tasks/tools/
Here is a sample shell script that combines the installation steps for both tools:


1. Open your terminal and type the following command to create a new shell script file using the vi editor:

    ```bash
    vi install_k8s_tools.sh
    ```

2. Press `i` to go into insert mode, then copy and paste the following shell script code into the editor:


```
#!/bin/bash


# Install Minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube



# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl




# Start Minikube cluster
minikube start 


 # Verify Minikube Installation
minikube version



# Verify kubectl Installation
kubectl version --client

# Check Minikube status
minikube status



```


3. Press ESC to exit insert mode.

4. Type :wq and press Enter to save the file and exit the vi editor.

5. Give the script executable permissions:

    ```bash
    chmod +x install_k8s_tools.sh
    ```


6. Run the script as a superuser:

```
sudo ./install_k8s_tools.sh
```


##  Minikube start  and  check the status:

####  minikube start
```
minikube start 
```
####  minikube status 
```
minikube status 

```


```
kubectl version --client
```