# Minikube and kubectl Installation Script for Ubuntu 22.04

This repository contains a shell script for installing Minikube and kubectl on Ubuntu 22.04.

## Prerequisites

- Ubuntu 22.04 machine
- User with sudo privileges

## Installation Steps

1. Clone this repository:

    ```bash
    git clone https://github.com/yourusername/minikube-kubectl-installer.git
    ```

2. Change directory into the cloned repository:

    ```bash
    cd minikube-kubectl-installer
    ```

3. Make the shell script executable:

    ```bash
    chmod +x install_minikube_kubectl.sh
    ```

4. Run the installation script with sudo privileges:

    ```bash
    sudo ./install_minikube_kubectl.sh
    ```

## Verification

After the script completes, you can verify the installation with:

- Check Minikube status:

    ```bash
    minikube status
    ```

- Check kubectl version:

    ```bash
    kubectl version --client
    ```

## Contributors

- Your Name

