# Lab: Deploy Your First Kubernetes Application

## Objectives

- Build a Docker image for a Node.js application
- Deploy the application to a Kubernetes cluster

## Prerequisites

Make sure you have the following installed and set up:

- Docker
- Kubernetes cluster (either Minikube or a cloud-based Kubernetes service)
- kubectl command-line tool

## Steps

### Build the Docker Image

1. Navigate to the directory containing the Dockerfile.
2. Run the following command to build the Docker image:

   ```shell
   docker build -t first-app .
