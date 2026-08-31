#!/bin/bash
# install_plane.sh — LAB 1: download Plane v1.4.2 compose + env into ~/plane-selfhost, patch 6 values, install the `pc` helper.
# Idempotent: an existing plane.env is never overwritten (delete it yourself if you want a fresh one).
# Env overrides (for instructors only): PLANE_TAG (default v1.4.2), HTTP_PORT (default 8080 = the port the browser uses).
set -euo pipefail
TAG=${PLANE_TAG:-v1.4.2}
PORT=${HTTP_PORT:-8080}
DIR="$HOME/plane-selfhost"
BASE="https://github.com/makeplane/plane/releases/download/$TAG"

mkdir -p "$DIR" && cd "$DIR"

if [ ! -f docker-compose.yml ]; then
  curl -sSL -o docker-compose.yml "$BASE/docker-compose.yml"
  echo "downloaded docker-compose.yml ($TAG)"
fi

if [ -f plane.env ]; then
  echo "plane.env already exists — keeping it (rm ~/plane-selfhost/plane.env to regenerate)"
else
  curl -sSL -o variables.env "$BASE/variables.env"
  mv variables.env plane.env
  # 1) the 6 values that must match the port the browser uses (WEB_URL builds every post-login redirect)
  sed -i "s|^APP_DOMAIN=.*|APP_DOMAIN=localhost:$PORT|; \
          s|^APP_RELEASE=.*|APP_RELEASE=$TAG|; \
          s|^LISTEN_HTTP_PORT=.*|LISTEN_HTTP_PORT=8080|; \
          s|^LISTEN_HTTPS_PORT=.*|LISTEN_HTTPS_PORT=8443|; \
          s|^WEB_URL=.*|WEB_URL=http://localhost:$PORT|; \
          s|^CORS_ALLOWED_ORIGINS=.*|CORS_ALLOWED_ORIGINS=http://localhost:$PORT|" plane.env
  # 2) never ship the upstream placeholder secrets
  sed -i "s|^SECRET_KEY=.*|SECRET_KEY=$(openssl rand -hex 32)|; \
          s|^LIVE_SERVER_SECRET_KEY=.*|LIVE_SERVER_SECRET_KEY=$(openssl rand -hex 32)|" plane.env
  chmod 600 plane.env
  echo "created $DIR/plane.env (secrets generated)"
fi

# 3) `pc` = docker compose with the right files and project name, usable from any directory (every later LAB uses it)
cat > /usr/local/bin/pc <<'PC'
#!/bin/bash
exec docker compose -f "$HOME/plane-selfhost/docker-compose.yml" --env-file "$HOME/plane-selfhost/plane.env" -p plane "$@"
PC
chmod +x /usr/local/bin/pc
echo "installed /usr/local/bin/pc"

echo "== key lines in plane.env"
grep -nE '^(APP_DOMAIN|APP_RELEASE|LISTEN_HTTP_PORT|LISTEN_HTTPS_PORT|WEB_URL|CORS_ALLOWED_ORIGINS)=' plane.env
