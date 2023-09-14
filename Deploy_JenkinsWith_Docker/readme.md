

https://www.jenkins.io/doc/book/installing/docker/


# Jenkins Installation Guide for Docker

## Prerequisites

- 256 MB of RAM
- 1 GB of drive space (10 GB recommended if running Jenkins as a Docker container)

## Downloading and Running Jenkins in Docker

### On macOS and Linux

1. Create a bridge network in Docker: `docker network create jenkins`
2. Download and run the `docker:dind` Docker image.

### On Windows

Make sure your Docker for Windows installation is configured to run Linux Containers.

