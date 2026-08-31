# syntax=docker/dockerfile:1
FROM postgres:17-alpine

# PostgreSQL entrypoint executes these files only when pgdata is empty.
# Baking them into the image also works when the Docker daemon cannot see
# the caller's host path for a bind mount.
COPY initdb/ /docker-entrypoint-initdb.d/
