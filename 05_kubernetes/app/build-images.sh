#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

docker build --build-arg APP_VERSION=v1 --build-arg DEFAULT_THEME=blue -t k8s-lab-web:v1 ./web
docker build --build-arg APP_VERSION=v2 --build-arg DEFAULT_THEME=emerald -t k8s-lab-web:v2 ./web
docker build -t k8s-lab-api:v1 ./api
docker build -t k8s-lab-db:v1 ./db

docker images | grep k8s-lab
