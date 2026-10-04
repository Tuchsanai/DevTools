# Plane v1.4.2 (self-hosted Community Edition) — Authoritative Reference for Course Authors
Source tag: `makeplane/plane` **v1.4.2** (git tag `v1.4.2` = commit `5f7d927`, `package.json:3` → `"version": "1.4.2"`, AGPL-3.0).
Date: **2026-09-01**.
Every claim below carries a `(path:line)` citation into that tree and has been adversarially verified against the source; anything that could not be located is written as **NOT FOUND in v1.4.2** — treat those as "do not claim".

Conventions used below: "work item" is the UI name; the code, DB tables and most API paths still say `issue`. "God mode" = the instance-admin app served at `/god-mode/`. Roles are numeric: Admin=20, Member=15, Guest=5.

---

## 1. Overview & repository layout

Plane is a pnpm + turbo monorepo (pnpm 11.3.0, Node >= 22.18.0, lint oxlint) (`package.json:8-19,40-47`).

| Directory | What it is | Runtime / build | Evidence |
|---|---|---|---|
| `apps/api` | Django + DRF backend (`plane` project), Celery tasks, DB models, all REST APIs | python:3.12.10-alpine image, gunicorn + UvicornWorker on :8000 | `apps/api/Dockerfile.api:1,56-58`; `apps/api/bin/docker-entrypoint-api.sh:38` |
| `apps/web` | Main SPA ("app") | **React Router v7 framework mode on Vite, `ssr: false` — NOT Next.js**; production image is nginx:1.31-alpine serving `build/client` on :3000 | `apps/web/package.json:8-13`; `apps/web/react-router.config.ts:5-6`; `apps/web/Dockerfile.web:74-100` |
| `apps/admin` | God-mode instance admin SPA at `/god-mode/` | React Router v7, `ssr: false`; nginx image, assets under `/usr/share/nginx/html/god-mode` | `apps/admin/react-router.config.ts:4-11`; `apps/admin/Dockerfile.admin:83` |
| `apps/space` | Public "Spaces" app for published boards at `/spaces/` | React Router v7 **`ssr: true`**, `npx react-router-serve ./build/server/index.js`, container port 3000 | `apps/space/react-router.config.ts:4-10`; `apps/space/Dockerfile.space:79-105` |
| `apps/live` | Real-time collaboration server for Pages (Express + express-ws + Hocuspocus/Yjs) | `node apps/live`, port 3000, router at `/live` | `apps/live/package.json:29-63`; `apps/live/Dockerfile.live:74-76`; `apps/live/src/server.ts:33-40` |
| `apps/proxy` | Caddy 2.11.3 reverse proxy image (`makeplane/plane-proxy`) with cloudflare/digitalocean DNS plugins and caddy-l4 | `Caddyfile.ce` copied to `/etc/caddy/Caddyfile` | `apps/proxy/Dockerfile.ce:1-19` |
| `packages/*` | Shared TS packages: `codemods, constants, decorators, editor, hooks, i18n, logger, propel (charts), services, shared-state, tailwind-config, types, typescript-config, ui, utils` | | `ls packages` |
| `deployments/cli/community` | What self-hosters use: `install.sh` (shipped as `setup.sh`), `docker-compose.yml`, `variables.env`, `restore.sh`, `restore-airgapped.sh`, `build.yml`, `README.md` | | `.github/workflows/build-branch.yml:349-364` |
| `deployments/swarm/community` | `swarm.sh` — deploys the same release compose file with `docker stack deploy` | | `deployments/swarm/community/swarm.sh:63-70,233-240` |
| `deployments/aio/community` | All-in-one single-container image (supervisord) | | `deployments/aio/community/Dockerfile:9-64`; `supervisor.conf:7-100` |
| `deployments/kubernetes/community` | **README only**, linking to the `makeplane/plane-ce` Helm chart on Artifact Hub; no manifests | | `deployments/kubernetes/community/README.md:1-5` |
| `docs/` | Contains only `docs/linting.md`; API docs are external (developers.plane.so) | | `docs/linting.md:1`; `apps/api/plane/settings/openapi.py:16-20` |

CE/EE seams in the tree: the only `ce/` and `ee/` directories are `packages/editor/src/ce` and `packages/editor/src/ee`, and `ee/extensions/index.ts` just re-exports `src/ce/extensions` (`packages/editor/src/ee/extensions/index.ts:7`). `apps/web` has no `ce/` or `ee/` directory; `extendedRoutes` is an empty array (`apps/web/app/routes/extended.ts:9`). The backend has no `ee/` package and no license-key check; `InstanceEdition` contains the single value `PLANE_COMMUNITY` (`apps/api/plane/license/models/instance.py:18-19`). `IS_SELF_MANAGED = True` is hard-coded (`apps/api/plane/settings/common.py:54`).

Django URL roots (`apps/api/plane/urls.py:18-25`):

| Prefix | urlconf | Purpose |
|---|---|---|
| `api/` | `plane.app.urls` | Internal app API (session cookie) used by `apps/web` |
| `api/public/` | `plane.space.urls` | Public deploy-board API used by `apps/space` |
| `api/instances/` | `plane.license.urls` | Instance / god-mode API |
| `api/v1/` | `plane.api.urls` | External REST API (`X-Api-Key`) |
| `auth/` | `plane.authentication.urls` | Sign-in/up, magic code, OAuth, passwords |
| `""` | `plane.web.urls` | `/` health check returning `{"status": "OK"}` and `robots.txt` (`apps/api/plane/web/urls.py:8`) |
| `api/schema/…` | drf-spectacular, only when `ENABLE_DRF_SPECTACULAR=1` (`apps/api/plane/urls.py:27-40`) |

`plane.app.urls` concatenates 20 modules: analytic, asset, cycle, estimate, external, intake, issue, module, notification, page, project, search, state, user, views, workspace, api (tokens), webhook, timezone, exporter (`apps/api/plane/app/urls/__init__.py:5-47`). There is no importer or dashboard URL module.

---

## 2. Deployment architecture

### 2.1 Release assets and `install.sh`

The GitHub release attaches six files: `setup.sh` (copy of `deployments/cli/community/install.sh`), `restore.sh`, `restore-airgapped.sh`, `docker-compose.yml`, `variables.env`, `swarm.sh` (`.github/workflows/build-branch.yml:349-364`). CI rewrites `${APP_RELEASE:-stable}` to `${APP_RELEASE:-vX.Y.Z}` at release time (`build-branch.yml:351,389`).

`install.sh` behaviour (`deployments/cli/community/install.sh`):
- Works in `./plane-app/` using `plane-app/docker-compose.yaml` + `plane-app/plane.env` (`:5-6,19-20`). The compose **project name is the folder name `plane-app`**, so containers are `plane-app-api-1`, `plane-app-migrator-1`… and volumes are `plane-app_pgdata`, `plane-app_redisdata`, `plane-app_uploads`, `plane-app_rabbitmq_data` (`install.sh:340,368`; `README.md:471-473,512-522`; `restore.sh:70-72,88`).
- `install`: resolves `stable` to the latest GitHub release tag (`:58-67,219-221`), checks the `makeplane/plane-proxy:<tag>` manifest for the host CPU architecture (`:80-101`) and offers a local build if missing (`:225-239,185-213`).
- `download`: fetches `docker-compose.yml` + `variables.env` from the release (`:242-293`), archives the previous copies (`:246-248,295-299`) and `syncEnvFile` copies old values key-by-key into the new `plane.env` (`:163-183`). It appends `DOCKERHUB_USER`, `APP_RELEASE`, `PULL_POLICY`, `CUSTOM_BUILD` (`:154-161`).
- `start`: `docker compose … up -d --pull if_not_present` (`:338`), waits for the `plane-app-migrator` container to exit (`:340-350`), fails if its exit code != 0 (`:356-366`), then polls `http://localhost:8000/` *inside the api container* for up to 300 s (`:368-411`) — that URL is Django `health_check` returning `{"status":"OK"}` (`apps/api/plane/web/urls.py:8`; `apps/api/plane/web/views.py:8-9`). **The poll is advisory**: on timeout the script exits 1 only if the api container has stopped; if the container is running but never answered it just prints a warning, sets `api_ready=false` and still prints "Plane Server started successfully" (`install.sh:386-397,407-413`).
- `stop`: `docker compose … down` **without `-v`** — named volumes survive (`:420`). `docker compose down -v` would delete data.
- `backup`: `docker cp` of Postgres, MinIO `/export`, RabbitMQ and Valkey data dirs into `plane-app/backup/<ts>/*.tar.gz` (`:544-607`). `restore.sh` refuses to run while the project is up, then removes/recreates each `plane-app*_{pgdata,redisdata,uploads,rabbitmq_data}` volume and untars into it (`restore.sh:25,33,40-44,60-72,88`).
- Backup caveats for labs: the copy is taken from **running** containers (`install.sh:551-562,599-602`), so a live Postgres data-dir copy is not crash-consistent — teach `pg_dump` (or stop the stack first). Both scripts prefer the legacy Compose v1 binary when it exists (`COMPOSE_CMD="docker-compose"`, `install.sh:673-678`; `restore.sh:116-121`), and `restore.sh` additionally needs `jq` (`restore.sh:60`).
- Gotcha: the local-build path tags images `myplane/plane-*:local` but the release compose hard-codes `makeplane/…` image names, so `DOCKERHUB_USER` in `plane.env` is never consumed by the compose file (`install.sh:188-190`; `build.yml:3`; `docker-compose.yml:66`). `PULL_POLICY` is written to `plane.env` the same way and is equally dead: `startServices` hard-codes `up -d --pull if_not_present --quiet-pull` and the compose file references neither variable (`install.sh:9,158,338,689-704`).

### 2.2 The 13 compose services (`deployments/cli/community/docker-compose.yml`)

| Service (lines) | Image | Role | Container port(s) | depends_on | Volumes | Replicas / restart |
|---|---|---|---|---|---|---|
| `web` (65-73) | `makeplane/plane-frontend:${APP_RELEASE:-stable}` | nginx serving the web SPA | 3000 (internal) | api, worker | — | `${WEB_REPLICAS:-1}` / `condition: any` |
| `space` (75-84) | `makeplane/plane-space` | SSR app for public `/spaces/*` boards | 3000 | api, worker, web | — | `${SPACE_REPLICAS:-1}` / any |
| `admin` (86-94) | `makeplane/plane-admin` | nginx serving god-mode SPA at `/god-mode/` | 3000 | api, web | — | `${ADMIN_REPLICAS:-1}` / any |
| `live` (96-106) | `makeplane/plane-live` | Hocuspocus/WebSocket collaboration server | 3000 | api, web | — | `${LIVE_REPLICAS:-1}` / any; env = live-env + redis-env only |
| `api` (108-122) | `makeplane/plane-backend` | Django/DRF via gunicorn + uvicorn, command `./bin/docker-entrypoint-api.sh` | 8000 | plane-db, plane-redis, plane-mq | `logs_api:/code/plane/logs` | `${API_REPLICAS:-1}` / any |
| `worker` (124-139) | `makeplane/plane-backend` | Celery worker, `./bin/docker-entrypoint-worker.sh` | — | api, plane-db, plane-redis, plane-mq | `logs_worker` | `${WORKER_REPLICAS:-1}` / any |
| `beat-worker` (141-156) | `makeplane/plane-backend` | Celery beat scheduler, `./bin/docker-entrypoint-beat.sh` | — | api, plane-db, plane-redis, plane-mq | `logs_beat-worker` | `${BEAT_WORKER_REPLICAS:-1}` / any |
| `migrator` (158-171) | `makeplane/plane-backend` | one-shot `manage.py migrate`, `./bin/docker-entrypoint-migrator.sh` | — | plane-db, plane-redis | `logs_migrator` | 1 / `condition: on-failure` |
| `plane-db` (174-184) | `postgres:15.7-alpine` | PostgreSQL, `postgres -c 'max_connections=1000'` | 5432 (internal) | — | `pgdata:/var/lib/postgresql/data` | 1 / any |
| `plane-redis` (186-193) | `valkey/valkey:7.2.11-alpine` | Redis-compatible cache / throttle counters / pub-sub | 6379 (internal) | — | `redisdata:/data` | 1 / any |
| `plane-mq` (195-204) | `rabbitmq:3.13.6-management-alpine` | Celery broker | 5672, 15672 mgmt (internal only) | — | `rabbitmq_data:/var/lib/rabbitmq` | 1 / any |
| `plane-minio` (207-217) | `minio/minio:latest` | S3-compatible object store, `server /export --console-address ":9090"` | 9000, 9090 console (internal) | — | `uploads:/export` | 1 / any |
| `proxy` (220-245) | `makeplane/plane-proxy` | Caddy reverse proxy + TLS | **80→`${LISTEN_HTTP_PORT:-80}`, 443→`${LISTEN_HTTPS_PORT:-443}`, `mode: host`** | web, api, space, admin, live | `proxy_config:/config`, `proxy_data:/data` | 1 / any |

Key facts about this file:
- **Only `proxy` publishes ports** (`:228-236`). Postgres, Valkey, RabbitMQ and MinIO are reachable only on the compose network.
- api / worker / beat-worker / migrator share **one image** and differ only by command (`:110,126,143,160`); they receive the same env anchors `app-env, db-env, redis-env, minio-env, aws-s3-env, proxy-env` (`:118,134,151,168`).
- **No `healthcheck:` block and no `depends_on … condition: service_healthy` anywhere**; restart behaviour is only `deploy.restart_policy.condition` and `depends_on` is the plain list form, so it orders container *start* only (grep of the file; `:69-70,163-164`). The **images** do carry their own `HEALTHCHECK` for web, admin and space (`curl` on :3000, `apps/web/Dockerfile.web:87-88`; `apps/admin/Dockerfile.admin:87-88`; `apps/space/Dockerfile.space:102-103`), so `docker ps` shows `(healthy)` for exactly those three; api, worker, beat, migrator, db, mq and minio show no health state.
- `GUNICORN_WORKERS: 1` is hard-coded in the `app-env` anchor (`:53`) — the `GUNICORN_WORKERS=1` line in `variables.env` has no effect.
- The compose file uses Swarm-native keys (`deploy.replicas`, `deploy.restart_policy`, `ports.mode: host`) because `swarm.sh` deploys the *same* file with `docker stack deploy` (`deployments/swarm/community/swarm.sh:233-240`).
- Named volumes (`:247-257`): `pgdata, redisdata, uploads, logs_api, logs_worker, logs_beat-worker, logs_migrator, rabbitmq_data, proxy_config, proxy_data`.
- Comments say `plane-db` (`:173`), `plane-minio` (`:206`) and `proxy` (`:219`) may be commented out when external services exist.

### 2.3 Boot and readiness order

Container *start* order from `depends_on`: plane-db / plane-redis / plane-mq → migrator and api → worker / beat-worker → web → space / admin / live → proxy (`docker-compose.yml:71-73,81-84,92-94,104-106,119-122,135-139,152-156,169-171,240-245`). **`plane-minio` has no dependents** — no service lists it in `depends_on`, so it starts in parallel with everything else (`:119-122,169-171,207-217`). If MinIO is not yet reachable when the api runs `create_bucket`, the command swallows the error in a bare `except Exception` and the api keeps booting **without a bucket**; uploads then fail at request time until the bucket is created or the api is restarted (`apps/api/plane/db/management/commands/create_bucket.py:59-61`).

Real readiness is enforced by the entrypoint scripts in `apps/api/bin/` (all `set -e`):

| Script | Steps |
|---|---|
| `docker-entrypoint-migrator.sh` | `manage.py wait_for_db` → `manage.py migrate` (`:4-6`) |
| `docker-entrypoint-api.sh` | `wait_for_db` (`:3`) → `wait_for_migrations` (`:5`) → compute `MACHINE_SIGNATURE` = sha256(hostname+MAC+cpuinfo+free+df) (`:11-21`) → `register_instance "$MACHINE_SIGNATURE"` (`:24`) → `configure_instance` (`:27`) → `create_bucket` (`:30`) → `clear_cache` (`:33`) → `collectstatic --noinput` (`:36`) → `exec gunicorn -w "$GUNICORN_WORKERS" -k uvicorn.workers.UvicornWorker plane.asgi:application --bind 0.0.0.0:"${PORT:-8000}" --max-requests 1200 --max-requests-jitter 1000 --access-logfile -` (`:38`) — `--access-logfile -` is why `docker logs <api>` shows every request |
| `docker-entrypoint-worker.sh` / `-beat.sh` | `wait_for_db` → `wait_for_migrations` → `celery -A plane worker -l info` / `celery -A plane beat -l info` (`:4-8` each) |

- `wait_for_db` **is effectively a no-op**: `connections["default"]` only returns the `DatabaseWrapper` object and never opens a socket, so `OperationalError` cannot be raised and the loop exits on its first iteration (`apps/api/plane/db/management/commands/wait_for_db.py:17-22`). Real DB gating is done by `wait_for_migrations` (its `MigrationExecutor` actually queries the DB; with Postgres down it raises, `set -e` kills the container and `restart_policy: any` restarts it) and, for the migrator, by `manage.py migrate` itself (`restart_policy: on-failure`) (`apps/api/bin/docker-entrypoint-api.sh:2-5`; `deployments/cli/community/docker-compose.yml:113-114,163-164`).
- `wait_for_migrations` polls every 10 s until `MigrationExecutor.migration_plan(...)` is empty (`apps/api/plane/db/management/commands/wait_for_migrations.py:15-26`). **This is the migrator → api/worker/beat contract**: they block until the migrator has finished.
- `register_instance` creates the singleton `Instance` (`instance_name="Plane Community Edition"`, random `instance_id`, `edition=PLANE_COMMUNITY`) or refreshes versions, calling `https://api.github.com/repos/makeplane/plane/releases/latest` for `latest_version`, then enqueues `push_instance_metrics.delay()` — **so API boot needs a reachable RabbitMQ** (`apps/api/plane/license/management/commands/register_instance.py:40-51,61-90`). `current_version` comes from `APP_VERSION` or, failing that, from `/code/package.json` (copied by `apps/api/Dockerfile.api:46`), and the GitHub call has a 10 s timeout with a silent fallback — an offline boot works, it is just slower (`register_instance.py:28-51`). `Instance.is_test` is set from `IS_TEST=1` (`:73,85`).
- `configure_instance` raises `CommandError` if `SECRET_KEY` is empty (api container exits) and seeds `InstanceConfiguration` rows from env **only when the row does not exist** (`apps/api/plane/license/management/commands/configure_instance.py:22-40`).
- `create_bucket` does `head_bucket`/`create_bucket` on `AWS_S3_BUCKET_NAME` (`apps/api/plane/db/management/commands/create_bucket.py:20-44`); `clear_cache` calls `cache.clear()` (`clear_cache.py:24`).
- `swarm.sh` implements the same contract: wait for `<stack>_migrator` to stop with exit 0, then tail the api log until "Application Startup Complete" (`swarm.sh:245-286`).

### 2.4 Request path (browser → proxy → upstreams)

Caddy snippet `plane_proxy` is evaluated in this order (`apps/proxy/Caddyfile.ce:1-24`):

| Match | Upstream | Line |
|---|---|---|
| `request_body max_size {$FILE_SIZE_LIMIT}` | applies to all routes | 2-4 |
| `redir /spaces /spaces/ permanent`; `/spaces/*` | `space:3000` | 6-7 |
| `redir /god-mode /god-mode/ permanent`; `/god-mode/*` | `admin:3000` | 9-10 |
| `/live/*` | `live:3000` | 12 |
| `/api/*`, `/auth/*`, `/static/*` | `api:8000` | 14-18 |
| `/{$BUCKET_NAME}/*` and `/{$BUCKET_NAME}` (default `/uploads`) | `plane-minio:9000` | 20-21 |
| `/*` | `web:3000` | 23 |

Global block: `{$CERT_EMAIL}`, `acme_ca {$CERT_ACME_CA:https://acme-v02.api.letsencrypt.org/directory}`, `{$CERT_ACME_DNS}`, `servers { max_header_size 25MB; client_ip_headers X-Forwarded-For X-Real-IP; trusted_proxies static {$TRUSTED_PROXIES:0.0.0.0/0} }`; site block `{$SITE_ADDRESS} { import plane_proxy }` (`Caddyfile.ce:26-39`). There is **no `header_up Host` rewrite**, so upstreams see the browser's Host header (important for MinIO presigned URLs).

End-to-end flow:
1. Browser → host port `LISTEN_HTTP_PORT` (80) → proxy container :80 (`docker-compose.yml:228-232`); Caddy listens on `SITE_ADDRESS` (`:80`) (`Caddyfile.ce:37`).
2. `GET /` → `web:3000` nginx → `index.html` (SPA `try_files … /index.html`, `apps/web/nginx/nginx.conf:29-33`).
3. SPA calls `GET /api/instances/` → `api:8000` → `InstanceEndpoint` returns `is_activated`/`is_setup_done` and config flags (`apps/api/plane/license/api/views/instance.py:28-48,130-167`). The SPAs use **relative same-origin URLs** because build args `VITE_API_BASE_URL`, `VITE_ADMIN_BASE_URL`, `VITE_LIVE_BASE_URL`, `VITE_SPACE_BASE_URL` default to `""` (`apps/web/Dockerfile.web:46-68`; `packages/constants/src/endpoints.ts:7-25`).
4. Sign-in form posts go to `/auth/*` → api; server sets the `session-id` cookie stored in the DB `sessions` table (`apps/api/plane/settings/common.py:376-378`). Cookie `Secure` only when every `CORS_ALLOWED_ORIGINS` entry is https (`common.py:184-190,374`). Django honours `X-Forwarded-Proto: https` in production (`apps/api/plane/settings/production.py:15`).
5. Authenticated XHR `/api/...` (cookie, `withCredentials`) → gunicorn → Django → Postgres/Valkey. Client IP comes from `X-Forwarded-For` because Caddy trusts `0.0.0.0/0` (`Caddyfile.ce:32-33`). **Per-IP auth throttling is therefore spoofable out of the box**: `get_client_ip` takes the *first* `X-Forwarded-For` entry (`apps/api/plane/utils/ip_address.py:199-205`), so any client can forge the IP that `AUTHENTICATION_RATE_LIMIT` counts against. Fixing it needs `TRUSTED_PROXIES`, which the release compose never forwards to the proxy (`docker-compose.yml:26-35`).
6. `/god-mode/*` → `admin:3000` nginx serving `/usr/share/nginx/html/god-mode` (`apps/admin/Dockerfile.admin:83`); the admin SPA uses the same `/api/instances/…` endpoints; API-built redirects use `WEB_URL` + `ADMIN_BASE_PATH`/`SPACE_BASE_PATH` (`apps/api/plane/utils/host.py:25-67`).
7. `/spaces/*` → `space:3000` (SSR) which calls `/api/public/*`.
8. Pages collaboration: browser opens `ws(s)://<origin>/live/collaboration?documentType=project_page&projectId=…&workspaceSlug=…` (`apps/web/core/components/pages/editor/editor-body.tsx:198-214`) → Caddy → `live:3000` → Hocuspocus; live authenticates by calling `GET {API_BASE_URL}/api/users/me/` (`http://api:8000`) with the forwarded session cookie (`apps/live/src/lib/auth.ts:24-97`; `apps/live/src/services/user.service.ts:25-30`).
9. File upload: SPA asks `/api/assets/v2/…` for a presigned POST; with `USE_MINIO=1` the API builds the S3 endpoint from the incoming request Host (`https` forced when `MINIO_ENDPOINT_SSL=1`), so the browser POSTs to `http(s)://<APP_DOMAIN>/uploads/...` → Caddy → `plane-minio:9000` → volume `uploads` (`apps/api/plane/settings/storage.py:39-53`; `Caddyfile.ce:20-21`). `FILE_SIZE_LIMIT` is enforced three times: Caddy `request_body`, Django `DATA_UPLOAD_MAX_MEMORY_SIZE` (413 via `RequestBodySizeLimitMiddleware`), and the presigned POST `content-length-range` (`Caddyfile.ce:2-4`; `common.py:353,371`; `apps/api/plane/middleware/request_body_size.py:18-28`; `storage.py:71-75`). Uploads are also **MIME-filtered**: the request's `type` must be in `ATTACHMENT_MIME_TYPES` (`common.py:457-545`), and anything in `SCRIPT_CAPABLE_MIME_TYPES` (`image/svg+xml`, `text/javascript`, `application/javascript`, `text/html`, `application/xhtml+xml`, `text/xml`, `application/xml`) is always served as a forced download (`common.py:547-560`).
10. Background work: API publishes Celery tasks to RabbitMQ; `worker` consumes; `beat-worker` fires the schedule (§13).
11. Django static (`/static/*`) is served by WhiteNoise inside the api container after `collectstatic` (`common.py:124,277-278`).

### 2.5 Compose specifics: persistence, upgrade, TLS

- Persistent state lives in: `pgdata` (Postgres), `uploads` (MinIO objects), `rabbitmq_data` (queued Celery messages), `redisdata` (Valkey dump), `proxy_data`/`proxy_config` (Caddy certs), `logs_*` (rotating `plane-error.log`, `production.py:47-60`). Django logging is JSON to **stdout** for every logger; the rotating file (1 MiB × 5 backups) is written **only** by the `plane.exception` logger, so in normal operation the `logs_*` volumes stay nearly empty and `docker logs` is the real log (`apps/api/plane/settings/production.py:31-99`).
- Renaming the `plane-app` folder or running compose from elsewhere creates a new project → new empty volumes.
- Upgrade = stop, download new compose/env, sync old values, pull images (`install.sh:242-336,426-463`); migrations run on the next start via the migrator.
- TLS with the bundled Caddy: set `SITE_ADDRESS=<fqdn>`, `CERT_EMAIL="email <addr>"`, optionally `CERT_ACME_DNS="acme_dns cloudflare <key>"` (`variables.env:43-53`; `Caddyfile.ce:27-29`); certificates persist in `proxy_data` (`docker-compose.yml:239`). Then set `WEB_URL`/`CORS_ALLOWED_ORIGINS` to `https://…` and, if TLS terminates elsewhere, `MINIO_ENDPOINT_SSL=1` (`storage.py:41-44`).
- `LISTEN_HTTP_PORT`/`LISTEN_HTTPS_PORT` change only the host-side published ports; the Caddyfile does not reference them (`docker-compose.yml:230,234`; `Caddyfile.ce:37`). README says if you change them, `WEB_URL` and `CORS_ALLOWED_ORIGINS` must include the port (`deployments/cli/community/README.md:147-151`).
- Database credentials: the app always connects with `DATABASE_URL` (compose default `postgresql://plane:plane@plane-db/plane`, `:55`). Django's non-URL fallback reads `POSTGRES_HOST`, which compose never sets (it sets `PGHOST`) (`common.py:205-218`). **Changing `POSTGRES_PASSWORD` in `plane.env` without also setting `DATABASE_URL` leaves Django on the hard-coded default.**

### 2.6 Other deployment targets

- **Swarm**: `swarm.sh` downloads the same release files, stores `STACK_NAME` (default `plane`) in `plane.env`, exports the env with `set -o allexport` and runs `docker stack deploy -c … $stack_name` (`swarm.sh:63-70,161-211,233-240`).
- **AIO**: one `python:3.12.10-alpine` image containing web/admin static, space, live, caddy and the backend under supervisord — migrator priority 10, space `PORT 3002`, api `PORT 3004`, live `PORT 3005`, worker, beat, `caddy run` (`deployments/aio/community/Dockerfile:1-64`; `supervisor.conf:7-100`). `start.sh` requires `DOMAIN_NAME, DATABASE_URL, REDIS_URL, AMQP_URL, AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_S3_BUCKET_NAME`, forces `USE_MINIO=0` and regenerates `SECRET_KEY`/`LIVE_SERVER_SECRET_KEY` when the passed value is **empty, the placeholder `change-this-key-on-deployment`, or the old publicly-known insecure default** — it first reuses any non-placeholder value already stored in `plane.env`, so a generated key survives restarts (`start.sh:24-45,111-182,148-176`). Note the AIO `Dockerfile`'s default build arg is `ARG PLANE_VERSION=v0.27.1`, **not** v1.4.2 (`deployments/aio/community/Dockerfile:1`). `Caddyfile.aio.ce` serves web and admin as static files (`apps/proxy/Caddyfile.aio.ce:21-30`), although the AIO README lists ports 3001/3003 for them (no such supervisor program exists).
- **Kubernetes**: README link only (`deployments/kubernetes/community/README.md:1-5`).
- **Developer compose**: root `docker-compose.yml` builds from source with `env_file: ./apps/api/.env`; `docker-compose-local.yml` runs only db/redis/mq/minio/api/worker/beat/migrator with source bind-mounted and ports 5432/6379/9000/9090/8000 published — **no `live` service there** (`docker-compose-local.yml:1-151`).

---

## 3. Environment variables

### 3.1 Every variable in `deployments/cli/community/variables.env`

"Compose" = how `docker-compose.yml` forwards it. Line numbers in the first column refer to `variables.env`.

| Var (line) | Default | Meaning | Compose → services | Consumer in code |
|---|---|---|---|---|
| `APP_DOMAIN` (1) | `localhost` | Template variable only; expanded into `WEB_URL` and `CORS_ALLOWED_ORIGINS` (`:15,17`) | proxy-env:27 → proxy + api family | **No application code reads it** (grep hits only `deployments/`) |
| `APP_RELEASE` (2) | `stable` | Image tag; `install.sh` resolves `stable` → latest GitHub tag (`install.sh:219-221`) | image tags `:66,76,87,97,109,125,142,159,221` | — |
| `WEB_REPLICAS … LIVE_REPLICAS` (4-10) | 1 | Container replicas per service | `deploy.replicas` `:68,78,89,101,112,128,145` | — |
| `LISTEN_HTTP_PORT` / `LISTEN_HTTPS_PORT` (12-13) | 80 / 443 | Host ports bound to Caddy 80/443 | proxy `ports.published` `:230,234`; proxy-env `:32-33` | Caddyfile does not read them (binds `SITE_ADDRESS`) |
| `WEB_URL` (15) | `http://${APP_DOMAIN}` | Canonical public origin | app-env:50 | `settings.WEB_URL` (`common.py:422`); `base_host()` builds app/admin(`/god-mode/`)/space(`/spaces/`) origins for redirects (`apps/api/plane/utils/host.py:25-67`); MinIO custom domain `<host>/<bucket>` (`common.py:313-316`); telemetry `domain` attribute; bot user email domain (`workspace_seed_task.py:530`) |
| `DEBUG` (16) | 0 | Django debug | app-env:51 | `DEBUG = int(...)==1` (`production.py:12`); switches log file/level (`production.py:47-60`) |
| `CORS_ALLOWED_ORIGINS` (17) | `http://${APP_DOMAIN}` | Comma list of allowed origins | app-env:52 (**not passed to live**) | Also `CSRF_TRUSTED_ORIGINS`; any `http:` origin → cookies not `Secure`; **empty → `CORS_ALLOW_ALL_ORIGINS=True`** (`common.py:182-192,374,387,389`) |
| `API_BASE_URL` (18) | `http://api:8000` | Where the live server calls the Django API | live-env:46 (live only) | `apps/live/src/services/api.service.ts:17-23`; required URL in `apps/live/src/env.ts:17` |
| `PGHOST` / `PGDATABASE` (21-22) | plane-db / plane | Intended DB host/db | db-env:2-3 | **Django settings never read them** (the non-URL branch reads `POSTGRES_HOST`/`POSTGRES_DB`, `common.py:205-218`) — but Django omits an empty HOST/NAME from the psycopg kwargs, and libpq then honours `PGHOST`/`PGDATABASE`, so in that fallback branch they would still take effect. Moot with the release compose, which always sets `DATABASE_URL` (`docker-compose.yml:2-3,55`) |
| `POSTGRES_USER/PASSWORD/DB/PORT`, `PGDATA` (23-27) | plane/plane/plane/5432/`/var/lib/postgresql/data` | Initialise the postgres image | db-env:4-8 → plane-db and api family | Django fallback only when `DATABASE_URL` is empty (`common.py:208-218`) — and compose always sets it |
| `DATABASE_URL` (28) | empty → compose default `postgresql://plane:plane@plane-db/plane` (`:55`) | The DB connection actually used | app-env:55 | `dj_database_url.config()` (`common.py:205-207`) |
| `REDIS_HOST` / `REDIS_PORT` (31-32) | plane-redis / 6379 | | redis-env:11-12 → api family + live | Live builds `redis://host:port` when `REDIS_URL` is missing (`apps/live/src/redis.ts:42-56`); Django ignores them |
| `REDIS_URL` (33) | empty → `redis://plane-redis:6379/` (`:13`) | Cache / throttles / locks / live pub-sub | redis-env:13 | django_redis `CACHES` (`common.py:242-263`, `rediss://` enables TLS); `redis_instance()` (`settings/redis.py:10-24`); live ioredis (`redis.ts:47-49,70`) |
| `RABBITMQ_HOST/PORT/USER/PASSWORD/VHOST` (36-40) | plane-mq/5672/plane/plane/plane | Initialise RabbitMQ user & vhost | mq-env:38-43 → plane-mq only (as `RABBITMQ_DEFAULT_*`) | Django's `RABBITMQ_*` fallback (`common.py:319-330`) is not fed by compose; `AMQP_URL` wins |
| `AMQP_URL` (41) | empty → `amqp://plane:plane@plane-mq:5672/plane` (`:57`) | Celery broker | app-env:57 | `CELERY_BROKER_URL` (`common.py:324-328`) |
| `CERT_ACME_CA` (44) | letsencrypt v02 | ACME CA | proxy-env:30 | `acme_ca {$CERT_ACME_CA:…}` (`Caddyfile.ce:28`) |
| `TRUSTED_PROXIES` (45) | `0.0.0.0/0` | Caddy trusted proxies | **not in proxy-env (`:26-35`)** | Caddy falls back to its inline default `0.0.0.0/0` (`Caddyfile.ce:33`); editing plane.env has no effect |
| `SITE_ADDRESS` (46) | `:80` | Caddy site address; set to a hostname to enable automatic TLS | proxy-env:35 | `{$SITE_ADDRESS} { import plane_proxy }` (`Caddyfile.ce:37`) |
| `CERT_EMAIL` (47) | empty | Inserted verbatim into the Caddy global block; must be `email <addr>` | proxy-env:29 | `Caddyfile.ce:27` |
| `CERT_ACME_DNS` (53) | empty | DNS-challenge line, e.g. `acme_dns cloudflare <key>` | proxy-env:31 | `Caddyfile.ce:29`; plugins in `apps/proxy/Dockerfile.ce:4-5` |
| `SECRET_KEY` (59) | `change-this-key-on-deployment` | Django secret; **also derives the Fernet key that encrypts stored instance secrets** | app-env:56 (no default) | empty → random key per process (`common.py:32`); placeholder → CRITICAL log only (`:37-48`); empty → `configure_instance` hard-fails (`configure_instance.py:22-26`); PBKDF2 → Fernet (`apps/api/plane/license/utils/encryption.py:13-27`) — rotating it makes stored OAuth/SMTP/LLM secrets undecryptable |
| `USE_MINIO` (62) | 1 | Presign against the public host instead of `AWS_S3_ENDPOINT_URL` | app-env:54 | `common.py:301`; `storage.py:39-53` |
| `AWS_REGION` (63) | empty | S3 region | aws-s3-env:20 | boto3 (`storage.py:27-63`) |
| `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` (64-65) | access-key / secret-key | S3 credentials **and MinIO root user/password** | aws-s3-env:21-22; minio-env:16-17 | `storage.py`, `create_bucket.py:20-29` |
| `AWS_S3_ENDPOINT_URL` (66) | `http://plane-minio:9000` | Internal S3 endpoint | aws-s3-env:23 | `common.py:305-312`; used directly when `USE_MINIO=0` |
| `AWS_S3_BUCKET_NAME` (67) | `uploads` | Bucket name **and** the Caddy path `/{$BUCKET_NAME}/*` | aws-s3-env:24; proxy-env:34 as `BUCKET_NAME` | `common.py:307`; `Caddyfile.ce:20-21` |
| `FILE_SIZE_LIMIT` (68) | 5242880 (5 MiB) | Max upload/request body | proxy-env:28 | Caddy `request_body`, Django `FILE_SIZE_LIMIT` + `DATA_UPLOAD_MAX_MEMORY_SIZE` (`common.py:353,371`), presigned POST range |
| `GUNICORN_WORKERS` (71) | 1 | gunicorn `-w` | **hard-coded `1` in app-env:53** | `docker-entrypoint-api.sh:38` — plane.env value ignored |
| `DOCKER_PLATFORM` (74, commented) | `linux/amd64` | Hint for ARM hosts | not referenced by compose | NOT FOUND any consumer |
| `MINIO_ENDPOINT_SSL` (77) | 0 | Force `https` in presigned URLs behind an external TLS terminator | app-env:59 | `storage.py:41-44` |
| `API_KEY_RATE_LIMIT` (80) | `60/minute` | Per-API-key throttle for `/api/v1/` | app-env:58 | `common.py:154`; `apps/api/plane/api/rate_limit.py:12-48` |
| `AUTHENTICATION_RATE_LIMIT` (85) | `10/minute` | Per-IP throttle on anonymous auth endpoints | **not in app-env (`:49-62`)** | `apps/api/plane/authentication/rate_limit.py:23` reads env directly with the same default; plane.env edits have no effect with the release compose |
| `LIVE_SERVER_SECRET_KEY` (89) | `change-this-key-on-deployment` | Shared secret for live ↔ api | live-env:47; app-env:60 | Live: required by zod schema (`apps/live/src/env.ts:26`) and compared in `requireSecretKey` (`apps/live/src/lib/auth-middleware.ts:35-38`) **which no route applies**; Django: NOT FOUND any reader |
| `WEBHOOK_ALLOWED_IPS` (93) | empty | CIDRs allowed as webhook targets even if private | app-env:61 | `common.py:59-68` |
| `WEBHOOK_ALLOWED_HOSTS` (98) | empty | Hostnames bypassing the private-IP SSRF check (comment cites `silo`, a service not in this repo) | app-env:62 | `common.py:75-80`; `apps/api/plane/utils/ip_address.py:159-197` |

### 3.2 Useful env knobs read by code but absent from `variables.env`

`ALLOWED_HOSTS` (default `*`, `common.py:94`); `WEBHOOK_DISALLOWED_DOMAINS` (`:86-91`); `ENABLE_READ_REPLICA` + `DATABASE_READ_REPLICA_URL` / `POSTGRES_READ_REPLICA_*` (`:221-238`); `SESSION_COOKIE_AGE` 604800, `SESSION_COOKIE_NAME` `session-id`, `COOKIE_DOMAIN`, `SESSION_SAVE_EVERY_REQUEST` (`:377-380,390`); `ADMIN_SESSION_COOKIE_AGE` 3600 (`:384`); `ADMIN_BASE_URL`/`ADMIN_BASE_PATH` (`/god-mode/`), `SPACE_BASE_URL`/`SPACE_BASE_PATH` (`/spaces/`), `APP_BASE_URL`/`APP_BASE_PATH` (`/`), `LIVE_BASE_URL`/`LIVE_BASE_PATH` (`/live/`) (`:396-419`); `HARD_DELETE_AFTER_DAYS` 60 (`:424`); `API_ACTIVITY_LOG_RETENTION_DAYS` 14, `WEBHOOK_LOG_RETENTION_DAYS` 14, `EMAIL_LOG_RETENTION_DAYS` 7 (`:445-452`); `SKIP_ENV_VAR` default `1` (`:369`); `ENABLE_DRF_SPECTACULAR` (`:565`); `UNSPLASH_ACCESS_KEY`, `GITHUB_ACCESS_TOKEN`, `POSTHOG_API_KEY`/`POSTHOG_HOST`, `ANALYTICS_*` (`:356-366`); `SIGNED_URL_EXPIRATION` 3600, `MINIO_ENDPOINT_URL` alias (`storage.py:35-37`); `OTLP_ENDPOINT` default `https://telemetry.plane.so` (`apps/api/plane/utils/otlp_endpoints.py:19,52`); `METRICS_PUSH_INTERVAL_MINUTES` 360 (`apps/api/plane/celery.py:27`); `APP_VERSION` (`register_instance.py:29`); `PORT` for gunicorn. Live-only: `PORT` 3000, `HOSTNAME`, `LIVE_BASE_PATH` `/live`, `COMPRESSION_LEVEL` 6, `COMPRESSION_THRESHOLD` 5000, `CORS_ALLOWED_ORIGINS` (`apps/live/src/env.ts:13-40`; invalid env → `process.exit(1)`).

### 3.3 Instance-level settings that live in the DB (god mode), NOT in env

`configure_instance` seeds the `InstanceConfiguration` table (key / value / category / `is_encrypted`, `apps/api/plane/license/models/instance.py:72-83`) from env **once**; existing rows are never overwritten (`configure_instance.py:29-40`). Because `SKIP_ENV_VAR` defaults to `"1"`, runtime lookups (`get_configuration_value`) read the DB rows and only fall back to the caller's default (`apps/api/plane/license/utils/instance_value.py:17-39`). Consequence: **after first boot, changing these in `plane.env` does nothing; edit them in god mode.** A second trap: `GET /api/instances/` — the endpoint the SPAs read these flags from — is server-cached for **2 hours** (`@cache_response(60 * 60 * 2, user=False)`, `apps/api/plane/license/api/views/instance.py:34`), which is why the api entrypoint runs `clear_cache` at boot and why a god-mode auth/SMTP toggle can appear to lag until that cache key is invalidated.

| Key (seed default) | Category | Encrypted | God-mode page | Lines in `apps/api/plane/utils/instance_config_variables/core.py` |
|---|---|---|---|---|
| `ENABLE_SIGNUP` (`"1"`) | AUTHENTICATION | no | Authentication ("Allow anyone to sign up even without an invite") | 10-14 |
| `ENABLE_EMAIL_PASSWORD` (`"1"`) | AUTHENTICATION | no | Authentication → Passwords | 16-20 |
| `ENABLE_MAGIC_LINK_LOGIN` (`"0"`) | AUTHENTICATION | no | Authentication → Unique codes (needs SMTP) | 22-26 |
| `DISABLE_WORKSPACE_CREATION` (`"0"`) | WORKSPACE_MANAGEMENT | no | Workspaces | 31-35 |
| `IS_GOOGLE_ENABLED`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `ENABLE_GOOGLE_SYNC` | GOOGLE | secret yes | Authentication → Google | 40-62 |
| `IS_GITHUB_ENABLED`, `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`, `GITHUB_ORGANIZATION_ID`, `ENABLE_GITHUB_SYNC` | GITHUB | secret yes | Authentication → GitHub | 67-95 |
| `IS_GITLAB_ENABLED`, `GITLAB_HOST`, `GITLAB_CLIENT_ID`, `GITLAB_CLIENT_SECRET`, `ENABLE_GITLAB_SYNC` | GITLAB | secret yes | Authentication → GitLab | 101-129 |
| `IS_GITEA_ENABLED`, `GITEA_HOST`, `GITEA_CLIENT_ID`, `GITEA_CLIENT_SECRET`, `ENABLE_GITEA_SYNC` | GITEA | secret yes | Authentication → Gitea | 134-162 |
| `ENABLE_SMTP` (`"0"`), `EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_PORT` (`"587"`), `EMAIL_FROM`, `EMAIL_USE_TLS` (`"1"`), `EMAIL_USE_SSL` (`"0"`) | SMTP | password yes | Email (+ "Send test email") | 167-213 |
| `LLM_API_KEY`, `LLM_PROVIDER` (`"openai"`), `LLM_MODEL` (`"gpt-4o-mini"`), `GPT_ENGINE` (deprecated) | AI | key yes | AI | 218-241 |
| `UNSPLASH_ACCESS_KEY` | UNSPLASH | yes | Image | 246-250 |

`extended_config_variables = []` (`apps/api/plane/utils/instance_config_variables/extended.py:5`). Also on the `Instance` row itself (General page): `instance_name`, `is_telemetry_enabled` (default **True**), `is_setup_done` (`instance.py:24-44`). NOT FOUND: any `IS_INTERCOM_ENABLED`/Intercom key.

---

## 4. Domain model

All models live in Django app `db` (`apps/api/plane/db/models/*.py`); instance models in app `plane.license` (`common.py:111`). Latest migration in v1.4.2: `0122_alter_draftissue_assignees_alter_issue_assignees_and_more.py`.

### 4.1 Base classes, audit columns, soft delete

| Class | Gives | Evidence |
|---|---|---|
| `TimeAuditModel` | `created_at`, `updated_at` | `apps/api/plane/db/mixins.py:16-20` |
| `UserAuditModel` | `created_by`, `updated_by` FK→User `SET_NULL` | `mixins.py:26-42` |
| `SoftDeleteModel` | `deleted_at`; `objects` filters `deleted_at IS NULL`; `all_objects` unfiltered | `mixins.py:56-67` |
| `BaseModel` | UUID4 primary key + all of the above; `save()` auto-fills `created_by/updated_by` from the request user | `apps/api/plane/db/models/base.py:17-44`; `mixins.py:85` |
| `WorkspaceBaseModel` | `workspace` FK + **nullable** `project` FK | `workspace.py:185-195` |
| `ProjectBaseModel` | `project` FK + `workspace` FK (always copied from project) | `project.py:180-189` |
| `ChangeTrackerMixin` | snapshots `TRACKED_FIELDS` so `save()` can see what changed | `mixins.py:92-210` |

Soft delete rules (apply to every `BaseModel` subclass):
- `instance.delete()` defaults to soft: sets `deleted_at=now`, saves, then queues Celery `soft_delete_related_objects` to cascade through reverse relations (`mixins.py:72-78`; `apps/api/plane/bgtasks/deletion_task.py:17-105`). `QuerySet.delete()` is also soft — but it is a plain `update(deleted_at=now)` and **does not enqueue the cascade** (`mixins.py:48-53`), so bulk deletes leave child rows undeleted until the nightly hard delete.
- Rows are physically purged by the nightly `hard_delete` task (00:00 UTC) after `HARD_DELETE_AFTER_DAYS` (default **60**) (`deletion_task.py:113-191`; `common.py:424`). It purges 18 named models **in order, `Workspace` first**, then every remaining model that has a `deleted_at`; because the workspace goes first, deleting a workspace physically removes all of its rows on the first 00:00 run after 60 days — relevant to any "can we restore it?" discussion (`deletion_task.py:113-191`).
- Uniqueness is enforced with **partial `UniqueConstraint`s conditioned on `deleted_at IS NULL`**, so a soft-deleted row never blocks re-creation (pattern at `workspace.py:216-223`). `Workspace.delete()` additionally rewrites `slug` to `slug__<epoch>` (`workspace.py:156-176`).
- `User` is **not** a `BaseModel`: no `deleted_at`, no `created_by`; `USERNAME_FIELD = "email"` (`user.py:128,136`).

Common conventions: `sort_order` FloatField default 65535, new rows placed at `max+10000` (Issue/Label/View/Sticky/Favorite) or `min-10000` (Cycle/Module/ProjectUserProperty); `external_source`/`external_id` on most entities for importer round-tripping; rich text stored as `description_json` + `description_html` (default `<p></p>`) + `description_stripped` + `description_binary` (Yjs) (`issue.py:137-140`; `page.py:32-35`).

### 4.2 Workspace layer (`apps/api/plane/db/models/workspace.py`)

| Model (table) | Key fields / constraints |
|---|---|
| `Workspace` (`workspaces`, `:181`) | `name` ≤80 (`:122`); `slug` ≤48, unique, validated against `RESTRICTED_WORKSPACE_SLUGS` (`:136,114-116`; list `apps/api/plane/utils/constants.py:5-71` includes `api, god-mode, spaces, plane-pro, enterprise, silo, upgrade, billing, initiatives, workflow, epics, dashboard, pages, business, pro, license…`); `owner` FK; `organization_size`; `timezone` default UTC (`:138`) |
| `WorkspaceMember` (`workspace_members`, `:226`) | `member`, `role` (20/15/5, **default 5**) (`:199-205`); `is_active` (deactivation instead of delete, `:210`); `view_props/default_props/issue_props` JSON; unique `(workspace, member)` while not deleted (`:216-223`) |
| `WorkspaceMemberInvite` (`:254`) | `email, accepted, token, message, responded_at, role` (`:235-241`); unique `(email, workspace)` |
| `Team` (`teams`, `:282`) | Defined but **not exported** from `models/__init__.py` and has no CE views; `TeamMember`/`TeamPage` dropped in migration 0086 (`migrations/0086_…py:236-241`) |
| `WorkspaceUserProperties` (`:347`) | per-user `filters, display_filters, display_properties, rich_filters`, `navigation_project_limit` 10, `navigation_control_preference` ACCORDION/TABBED (`:311-334`) |
| `WorkspaceUserLink` (`:367`) | "quick links" `title, url, metadata, owner` |
| `WorkspaceHomePreference` (`:410`) | `key` ∈ `HomeWidgetKeys` {quick_links, recents, my_stickies, new_at_plane, quick_tutorial} (`:377-382`); `is_enabled, config, sort_order`; unique workspace+user+key |
| `WorkspaceUserPreference` (`:454`) | sidebar pins: `key` ∈ {views, active_cycles, analytics, drafts, your_work, archives, stickies}, `is_pinned, sort_order` (`:420-441`) |
| `WorkspaceTheme` (`:306`) | `name, actor, colors` |

### 4.3 Project layer (`apps/api/plane/db/models/project.py`)

`Project` (table `projects`, `:164`):

| Field | Detail |
|---|---|
| `name` | CharField(255); unique `(name, workspace)` while not deleted (`:70,156-160`) |
| `identifier` | CharField(**12**), **upper-cased and stripped on save** (`:76,170`); unique `(identifier, workspace)` (`:151-155`); forbidden chars regex (`:143`); mirrored by 1:1 `ProjectIdentifier` (`:264-280`) |
| `network` | `0 = Secret`, `2 = Public`, **default 2** (`:69,74`, enum `:30-36`). "Public" = visible/joinable by workspace Members; **not** internet-public (that is `DeployBoard`, §9) |
| `default_assignee`, `project_lead` | FK→User nullable (`:77-90`) |
| Feature toggles | `module_view` **False**, `cycle_view` **False**, `issue_views_view` **False**, `page_view` **True**, `intake_view` **False**, `is_time_tracking_enabled` False, `is_issue_type_enabled` False, `guest_view_all_features` False (`:93-100`) |
| `estimate` | FK→`Estimate` SET_NULL — selects the project's active estimate system (`:109`) |
| `archive_in`, `close_in` | Int 0-12 months, consumed by the nightly automation task (`:110-111`; `bgtasks/issue_automation_task.py:31-42`) |
| `default_state` | FK→State SET_NULL (`:113`) — target of auto-close |
| `archived_at` | DateTime (`:114`) |
| `timezone` | inherits workspace tz on create unless given (`:116-125,173-175`) |

Creating a project is allowed for workspace **Admins and Members** (`@allow_permission([ROLE.ADMIN, ROLE.MEMBER], level="WORKSPACE")`, `apps/api/plane/app/views/project/base.py:257`) — Guests cannot. On create the API bulk-creates the six `DEFAULT_STATES` (§5) (`:281-295`); creator becomes `ProjectMember(role=20)` and `project_lead` too (`:266-279`); enabling `intake_view` later auto-creates a default `Intake` named `"{project.name} Intake"` (`:358-365`). The intake toggle is sent by the UI under the **legacy key `inbox_view`** and mapped to `intake_view` in the update handler (`:341`).

Membership: `ProjectMember` (`project_members`, `:255`): `member`, `role` default 5 (`:219`), `view_props/default_props/preferences` (default tab `work_items`, `:64-65`), `sort_order`, `is_active`; `save()` on insert creates a `ProjectUserProperty` with `sort_order = min-10000` so new projects appear first in the sidebar (`:226-242`); unique project+member. `ProjectMemberInvite` (`:203`), `ProjectPublicMember` (`:338`, public-board users), `ProjectUserProperty` (`:360`, per-user filters/display props), `ProjectDeployBoard` (`:312`, **deprecated**, comment `:298-299`).

### 4.4 Work item = `Issue` (`apps/api/plane/db/models/issue.py`)

`Issue` (table `issues`, `:177`), ordering `-created_at`, inherits `ChangeTrackerMixin` with `TRACKED_FIELDS = ["state_id"]` (`:104-105`).

| Field | Detail |
|---|---|
| `parent` | self-FK CASCADE, `related_name="parent_issue"` → **sub-work-items** (`:114-120`) |
| `state` | FK→State nullable (`:121-127`) |
| `point` | legacy Int 0-12 (`:128`) — still summed by `DefaultAnalyticsEndpoint` |
| `estimate_point` | FK→`EstimatePoint` SET_NULL (`:129-135`) |
| `name` | CharField(255) required (`:136`) |
| `description_json/html/stripped/binary` | (`:137-140`) |
| `priority` | `urgent, high, medium, low, none`; **default `none`** (`:107-113,141-146`) |
| `start_date`, `target_date` | **DateField** (`:147-148`) |
| `assignees` | M2M→User through `IssueAssignee` (`:149-155`) — multiple assignees |
| `labels` | M2M through `IssueLabel` (`:157`) |
| `sequence_id` | Int — the number in `PROJ-123` (`:156`) |
| `sort_order` | Float default 65535 (`:158`) |
| `completed_at` | DateTime, **derived** (`:159`, see §5) |
| `archived_at` | **DateField** (`:160`) |
| `is_draft` | Bool (`:161`) |
| `type` | FK→`IssueType` SET_NULL (`:164-170`) — schema only in CE |

Managers: `objects` = soft-delete manager; **`issue_objects` additionally excludes triage-group, archived, archived-project and draft issues** and is what almost every list/progress/analytics query uses (`:92-101,172`).

`save()` (`:180-222`):
1. `_ensure_default_state()` — no state → project's non-triage `default=True` state, else first non-triage state (`:228-238`).
2. `_sync_completed_at()` — on create or when `state_id` changed: `completed_at = now()` if `state.group == "completed"`, else **reset to `None`** (`:240-255`).
3. On insert, inside `transaction.atomic()`: **Postgres transaction advisory lock keyed on the project UUID** (`pg_advisory_xact_lock`, `:185-193`; hash helper `apps/api/plane/utils/uuid.py:19-26`), `sequence_id = max(IssueSequence.sequence)+1` for the project (`:196-199`), `description_stripped = strip_tags(...)` (`:201-205`), `sort_order = max(sort_order in same project+state)+10000` (`:206-210`), save, then write an `IssueSequence` row (`:214`).

Satellite tables:

| Model (table) | Semantics |
|---|---|
| `IssueSequence` (`issue_sequences`, `:570`) | `issue` FK **SET_NULL** — the number survives issue deletion, so `PROJ-7` is never reused (`:562-565`) |
| `IssueAssignee` (`:364`) | unique issue+assignee |
| `IssueLabel` (`:550`) | no unique constraint |
| `IssueRelation` (`:316`) | `issue, related_issue, relation_type` default `blocked_by`; stored types `duplicate, relates_to, blocked_by, start_before, finish_before, implemented_by` (`:272-278`); reverse pairs `blocked_by↔blocking`, `start_before↔start_after`, `finish_before↔finish_after`, `implemented_by↔implements`; `relates_to`/`duplicate` symmetric (`:283-290`); unique `(issue, related_issue)` (`:306-313`). Writes of `blocking/start_after/finish_after/implements` are stored **reversed** (`apps/api/plane/app/views/issue/relation.py:209-245`); relations may cross projects within a workspace |
| `IssueBlocker` (`:265`) | legacy, unused by views |
| `IssueMention` (`:338`), `IssueSubscriber` (`:593`) | unique issue+user |
| `IssueLink` (`:380`) | `title, url, metadata` (title/favicon crawled async) |
| `IssueAttachment` (`:408`) | legacy; data migrated to `FileAsset(entity_type="ISSUE_ATTACHMENT")` in migration 0079 |
| `IssueReaction` (`:620`) | unique issue+actor+reaction; `CommentReaction` (`:647`) |
| `IssueVote` (`:670`) | `vote` ∈ {-1 DOWNVOTE, 1 UPVOTE}, unique issue+actor (public boards) |
| `IssueComment` (`issue_comments`, `:535`) | `comment_json/html/stripped`; 1:1 `Description` kept in sync atomically (`:481-530`); `actor` nullable (system comments); `access` INTERNAL/EXTERNAL default INTERNAL (`:467-471`); `edited_at`; **`parent` self-FK = threaded replies** (`:475-477`) |
| `IssueActivity` (`issue_activities`, `:443`) | `issue` FK **DO_NOTHING**; `verb` (created/updated/deleted/removed); `field`; `old_value`/`new_value` Text; `comment`; `attachments`; `issue_comment` FK DO_NOTHING; `actor` SET_NULL; `old_identifier`/`new_identifier` UUID; `epoch` Float (`:416-438`). State changes: `field="state"`, names in `old/new_value`, UUIDs in `old/new_identifier` (`bgtasks/issue_activities_task.py:189-226`) |
| `IssueVersion` (`:730`) | denormalised snapshot (state/parent/type/cycle as UUIDs, assignees/labels/modules as UUID arrays) via `log_issue_version` (`:686-725,737-779`) |
| `IssueDescriptionVersion` (`:798`) | description html/json/binary snapshots via `log_issue_description_version` (`:782-822`); trimmed to newest 20 nightly |
| `DraftIssue` (`draft.py:81`) | workspace-level mirror of Issue with own assignee/label/module/cycle join tables; converting a draft deletes it |
| `FileAsset` (`asset.py:70`) | `entity_type` ∈ ISSUE_ATTACHMENT, ISSUE_DESCRIPTION, COMMENT_DESCRIPTION, PAGE_DESCRIPTION, USER_COVER, USER_AVATAR, WORKSPACE_LOGO, PROJECT_COVER, DRAFT_ISSUE_ATTACHMENT, DRAFT_ISSUE_DESCRIPTION (`:36-46`); `is_uploaded`, `size`, `storage_metadata`; size validator = `FILE_SIZE_LIMIT` |

### 4.5 State (`apps/api/plane/db/models/state.py`)

`StateGroup`: **backlog, unstarted, started, completed, cancelled, triage** (`:14-20`). `State` (table `states`, `:114`), ordering `("sequence",)` (`:115`): `name, description, color, slug` (auto `slugify(name)`, `:118`), `sequence` Float default 65535, `group` default backlog, `is_triage`, `default`, `external_*`; unique `(name, project)` while not deleted (`:104-111`); new state `sequence = max(project sequence)+15000` (`:119-124`). Managers: `objects` **excludes triage** (`:65-69`), `all_state_objects`, `triage_objects` (`:72-76,95-97`).

### 4.6 Label (`label.py`)

`Label(WorkspaceBaseModel)` (`labels`, `:43`): `parent` self-FK (**label groups**, `:12-18`), `name, description, color, sort_order`; two partial uniques: `name` unique when `project IS NULL` (workspace label), `(project, name)` when project set (`:29-39`); insert `sort_order = max+10000` (`:46-54`).

### 4.7 Estimate (`estimate.py`)

`EstimateType` = **`categories` (default) and `points` only** (`:13-15`; migration 0121 narrowed the choices). `Estimate` (`estimates`, `:39`): `name, description, type, last_used`; unique name+project. `EstimatePoint` (`estimate_points`, `:56`, ordering `value`, `:57`): `estimate` FK (`related_name="points"`), `key` Int ≥0, `description`, **`value` CharField** (`:44-47`) — every points computation casts it to Float. `Project.estimate` selects the active one.

### 4.8 IssueType (`issue_type.py`) — schema only

`IssueType(BaseModel)` (`issue_types`, `:29`): `workspace, name, description, logo_props, is_epic, is_default, is_active, level` (`:15-22`); `ProjectIssueType` (`:51`, not exported). **No IssueType CRUD views exist under `apps/api/plane/app/views`**; only the external API serializer assigns a project's default type on create (`apps/api/plane/api/serializers/issue.py:160-166`).

### 4.9 Cycle (`cycle.py`)

`Cycle` (`cycles`, `:85`): `name, description`; **`start_date`/`end_date` are DateTimeFields** stored in UTC (converted from project timezone in the serializer, `apps/api/plane/app/serializers/cycle.py:23-38`) (`:63-64`); `owned_by`; `view_props`; `sort_order` (insert → `min-10000`, `:88-97`); `progress_snapshot` JSON default `{}` (`:74`); `archived_at`; `logo_props`; `timezone`; `version` (`:75-80`). `CycleIssue` (`cycle_issues`, `:123`): unique `(cycle, issue)` while not deleted (`:112-120`) — that constraint only stops the *same* issue appearing twice in the *same* cycle. **"One cycle per issue" is not a DB rule**: it is view logic, the create handlers re-point an existing `CycleIssue` row to the new cycle (`app/views/cycle/issue.py:242-299`; `api/views/cycle.py:992-1043`). `CycleUserProperties` (`:153`) per-user filters.

### 4.10 Module (`module.py`)

`ModuleStatus`: `backlog, planned, in-progress, paused, completed, cancelled` (`:58-64`); `Module.status` default **planned** (`:74-85`) and is a manual field — nothing derives it from progress. `Module` (`modules`, `:112`): `name, description, description_text (JSON), description_html (JSON)`; **`start_date`/`target_date` are DateFields** (`:72-73`); `lead` FK SET_NULL; `members` M2M through `ModuleMember` (`:87-93`); `sort_order` (min-10000); `archived_at`; unique name+project (`:102-109`). `ModuleIssue` (`:167`): unique `(issue, module)` → **an issue may belong to many modules**. `ModuleLink` (`:183`) `title, url, metadata`.

### 4.11 View (`view.py`)

`IssueView(WorkspaceBaseModel)` (`issue_views`, `:76`) holds **both project views and workspace views** (`project IS NULL` ⇒ workspace view, `:89`). Fields: `name, description`; `query` JSON (**derived**: `issue_filters(filters, "POST")` recomputed on every save, `:79-81`); `filters, display_filters, display_properties, rich_filters` (`:62-65`); `access` 0=Private / 1=Public **default 1** (`:66`); `sort_order`; `logo_props`; `owned_by`; `is_locked`; `archived_at`. A separate `GlobalView` model was removed in migration 0081.

### 4.12 Page (`page.py`)

`Page(BaseModel)` (`pages`, `:63`): `workspace` FK; `name` Text; `description_json/binary/html/stripped`; `owned_by`; `access` **0=Public, 1=Private, default 0** (`:24-25,37`); `color`; `labels` M2M via `PageLabel`; `parent` self-FK (nested pages, `:40-46`); `archived_at` DateField; `is_locked`; `view_props` `{"full_width": False}`; `logo_props`; `is_global`; `projects` M2M through `ProjectPage` (`:52`); `moved_to_page/project`; `sort_order`. `PageLog` (`page_logs`, `:106`) tracks embedded entities (`to_do, issue, image, video, file, link, cycle, module, back_link, forward_link, page_mention, user_mention`, `:81-94`). `PageVersion` (`:172`) keeps history (`description_binary/html/stripped/json`, `sub_pages_data`).

### 4.13 Intake (`intake.py`)

`Intake` (`intakes`, `:34`): `name, description, is_default, view_props, logo_props`; unique name+project. `IntakeIssueStatus`: **PENDING=-2, REJECTED=-1, SNOOZED=0, ACCEPTED=1, DUPLICATE=2** (`:42-47`). `IntakeIssue` (`intake_issues`, `:79`): `intake`, `issue` FK, `status` default -2, `snoozed_till`, `duplicate_to` FK→Issue SET_NULL, `source` — an **unconstrained CharField** defaulting to `"IN_APP"` (`:70`) next to a backend `SourceType` enum whose only member is `IN_APP` (`:38-39`) — `source_email`, `extra`. **Intake issues are normal `Issue` rows in the Triage state**, hence hidden from `Issue.issue_objects`.

### 4.14 Analytics, home, favourites, recents, stickies

`AnalyticView` (`analytic_views`, `analytic.py:21`): saved legacy analytics queries (`query`, `query_dict`). **`Dashboard`/`Widget`/`DashboardWidget` models: NOT FOUND — renamed `Deprecated*` and dropped in migration 0092** (`migrations/0092_…py:32-40`). Home widgets are only `WorkspaceHomePreference` rows (§4.2). `UserFavorite` (`favorite.py:44`): `entity_type` (cycle, issue, module, view, page, project, folder), `is_folder`, `parent` self-FK, unique entity+user (`:19-41`; serializer `app/serializers/favorite.py:46-56`). `UserRecentVisit` (`recent_visit.py:35`): VIEW, PAGE, ISSUE, CYCLE, MODULE, PROJECT (`:13-19`). `Sticky` (`sticky.py:35`): personal notes with `sort_order`.

### 4.15 Integrations: API token, webhook, exporter, deploy board

| Model | Detail |
|---|---|
| `APIToken` (`api_tokens`, `api.py:44`) | `token` unique, default `"plane_api_" + uuid4().hex` (`:19-20,31`); `label` (random hex), `description`, `is_active`, `last_used`; `user` FK; `user_type` 0=Human/1=Bot (`:35`); `workspace` nullable (never set by the create endpoint); `expired_at`; `is_service`; `allowed_rate_limit` default `"60/min"` — **stored but never enforced** (`:39`) |
| `APIActivityLog` (`api_activity_logs`, `:72`) | `token_identifier, path, method, query_params, headers, body, response_code, response_body, ip_address, user_agent` (`:52-67`) |
| `Webhook` (`webhooks`, `webhook.py:54`) | `url` URLField(1024) validated http/https, plus a `validate_domain` that compares the **netloc** against `["localhost","127.0.0.1"]` — so bare `localhost` is rejected but `localhost:8080` passes this validator and is stopped later by the SSRF check (`:21-31,36`); `is_active`; `secret_key` default `"plane_wh_" + hex` (`:17-18,38`); event toggles `project, issue, module, cycle, issue_comment` (`:39-43`); `is_internal`; `version "v1"`; unique `(workspace, url)` (`:56-61`). `WebhookLog` (`:87`): `webhook` plain UUID, `event_type`, request/response method/headers/body/status, `retry_count`. `ProjectWebhook` join table exists (`:108`) but nothing filters by it |
| `ExporterHistory` (`exporters`, `exporter.py:62`) | `type` `issue_exports` \| `issue_worklogs` (**no worklog model exists**), `project` = UUID array, `provider` json/csv/xlsx, `status` queued/processing/completed/failed, `key, url, token, initiated_by, filters` (`:25-57`) |
| `DeployBoard(WorkspaceBaseModel)` (`deploy_boards`, `deploy_board.py:56`) | `entity_identifier` + `entity_name` ∈ project, issue, module, cycle, page, view, intake (`:20-31`); `anchor` unique hex (`:32`); `is_comments_enabled, is_reactions_enabled, is_votes_enabled, is_activity_enabled, is_disabled`; `intake` FK; resolved by anchor in `apps/api/plane/space/views/project.py:23-32` |
| `Importer` (`importer.py:35`) | `service` github/jira, `status`… — model only; no importer URL module in v1.4.2 |
| Legacy `Integration`, `WorkspaceIntegration`, `GithubRepository*Sync`, `SlackProjectSync` | models exist (`integration/*.py`); no CE routes |

### 4.16 Users, sessions, notifications

`User` (`users`, `user.py:136`): UUID id, unique `email`, `display_name`, `first/last_name`, avatar/cover assets, flags `is_active, is_superuser, is_staff, is_email_verified, is_password_autoset, is_bot`/`bot_type` (WORKSPACE_SEED), `user_timezone`, `last_login_*`, `last_logout_*` (`:57-126`). `post_save` creates `UserNotificationPreference` for non-bots (`:298-312`). `Profile` (1:1, `:267`): theme, onboarding fields, `last_workspace_id`, `language` default `en`, `start_of_the_week`, `billing_address*` (no CE consumer), `product_tour` (`:225-262`). `Account` (`:294`): OAuth linkage (google/github/gitlab). `Session` (`sessions`, `session.py:27`): **DB-backed** sessions with `user_id` and `device_info` (`:17-56`). `Notification` (`notification.py:38`): in-app rows; `UserNotificationPreference` (`:113`): `property_change, state_change, comment, mention, issue_completed` (`:104-108`); `EmailNotificationLog` (`:148`).

### 4.17 Instance / licence (`apps/api/plane/license/models/instance.py`)

`InstanceEdition` enum = **only `PLANE_COMMUNITY`** (`:18-19`). `Instance` (`instances`, `:49`): `instance_name, whitelist_emails (unused), instance_id (unique), current_version, latest_version, edition, domain, last_checked_at, namespace, is_telemetry_enabled (True), is_support_required, is_setup_done (False), is_signup_screen_visited, is_verified, is_test, is_current_version_deprecated` (`:24-44`). **No `license_key`, plan, or seat count field** (the TS type `IInstance` still declares `license_key`/`user_count` — type-only leftovers, `packages/types/src/instance/base.ts:30,40`). `InstanceAdmin` (`:68`): `user, instance, role` (only choice `(20, "Admin")`, `:15`), `is_verified`; unique instance+user. `InstanceConfiguration` (`:82`): key/value/category/`is_encrypted`. `ChangeLog` (`:99`).

### 4.18 Roles

`ROLE_CHOICES = ((20,"Admin"),(15,"Member"),(5,"Guest"))` for workspace and project (`workspace.py:19`; `project.py:21-27`); **default 5** on `WorkspaceMember`, `ProjectMember` and both invite models (`workspace.py:205,241`; `project.py:198,219`). Workspace creator → 20 (`app/views/workspace/base.py:125-130`). Frontend enums mirror 20/15/5 (`packages/constants/src/user.ts:36-40`). Instance admin is a separate table — instance admin ≠ workspace admin.

### 4.19 ER summary

```
User ──owner──> Workspace (slug unique ≤48)
                  ├── WorkspaceMember(role 20/15/5, is_active) ── User
                  ├── WorkspaceMemberInvite, WorkspaceUserProperties, WorkspaceUserLink,
                  │   WorkspaceHomePreference, WorkspaceUserPreference, WorkspaceTheme
                  ├── Label (project NULL = workspace label)
                  ├── IssueView (project NULL = workspace view)
                  ├── Page (projects M2M via ProjectPage; parent self-FK)
                  ├── IssueType (schema only in CE)
                  ├── AnalyticView, Sticky, UserFavorite, UserRecentVisit, DraftIssue
                  ├── Webhook(+WebhookLog), APIToken, ExporterHistory, Notification,
                  │   DeployBoard, FileAsset, Description(+DescriptionVersion)
                  └── Project (identifier ≤12 unique per workspace; network 0/2)
                        ├── ProjectMember(role) / ProjectMemberInvite / ProjectPublicMember
                        ├── ProjectUserProperty, ProjectIdentifier (1:1)
                        ├── State (group backlog|unstarted|started|completed|cancelled|triage; ordering sequence)
                        ├── Label (project-scoped, parent self-FK = label group)
                        ├── Estimate ──< EstimatePoint   (Project.estimate picks the active one)
                        ├── Cycle ──< CycleIssue >── Issue   (unique(cycle,issue); 1 cycle per issue is view logic)
                        ├── Module ──< ModuleIssue >── Issue (N modules per issue), ModuleMember, ModuleLink
                        ├── IssueView (project views), ProjectPage ──> Page
                        ├── Intake ──< IntakeIssue(status -2..2) ──> Issue (in triage state)
                        └── Issue (sequence_id per project; parent self-FK = sub-work-items)
                              ├── IssueAssignee >── User      ├── IssueLabel >── Label
                              ├── IssueRelation (typed, unique pair, cross-project OK)
                              ├── IssueLink, FileAsset(ISSUE_ATTACHMENT)
                              ├── IssueComment (parent self-FK threads; 1:1 Description) ──< CommentReaction
                              ├── IssueActivity (issue FK DO_NOTHING)
                              ├── IssueSubscriber, IssueMention, IssueReaction, IssueVote
                              ├── IssueSequence (issue FK SET_NULL — number never reused)
                              └── IssueVersion, IssueDescriptionVersion
```

FK `on_delete` summary: almost everything CASCADE; SET_NULL on `Issue.estimate_point`, `Issue.type`, `IssueSequence.issue`, `Module.lead`, `Project.estimate`, `Project.default_state`, `IssueActivity.actor`, `IntakeIssue.duplicate_to`; DO_NOTHING on `IssueActivity.issue`/`issue_comment` (`issue.py:416,424-429`). Because deletes are soft, DB cascades only fire at hard delete after 60 days.

### 4.20 Key constraints in one place

| Rule | Evidence |
|---|---|
| `sequence_id` = per-project counter allocated under an advisory lock; never reused (IssueSequence SET_NULL) | `issue.py:185-199,214,558-565` |
| `sort_order` on insert = max in same project+state + 10000; default 65535 | `issue.py:158,206-210` |
| `completed_at` set only in `Issue.save()` when state group becomes `completed`; cleared on any other state change | `issue.py:240-255` |
| `archived_at` (DateField) set only by explicit archive (single/bulk) or nightly automation; requires state group completed/cancelled | `app/views/issue/archive.py:256-303,305-343`; `bgtasks/issue_automation_task.py:28-86` |
| Soft delete everywhere; hard delete after 60 days; partial unique constraints ignore deleted rows | `mixins.py:72-78`; `common.py:424`; `workspace.py:216-223` |
| DB level: unique `(cycle, issue)` and unique `(issue, module)` while not deleted. "One cycle per issue" is enforced by the **create handlers** (existing `CycleIssue` rows are re-pointed), not by the constraint; many modules per issue is genuinely allowed | `cycle.py:112-120`; `module.py:157-164`; `app/views/cycle/issue.py:242-299` |
| Project identifier ≤12 chars, upper-cased | `project.py:76,170` |
| Workspace slug ≤48, restricted list | `workspace.py:136`; `utils/constants.py:5-71` |
| Label name unique per project (or per workspace when project NULL) | `label.py:29-39` |
| Module `(name, project)`, Estimate `(name, project)` and both Label uniques are **partial constraints conditioned on `deleted_at IS NULL`**, so the name of a soft-deleted object can be reused immediately — matters for lab clean-up / re-run scripts | `module.py:102-109`; `estimate.py:29-36`; `label.py:27-40` |
| Estimate types only categories/points; `EstimatePoint.value` is a string | `estimate.py:13-15,47` |
| Workspace Admin who is a project member passes any project-level check | `app/permissions/base.py:64-78` |

---

## 5. Workflow / states

### 5.1 Groups and defaults

Every project is created with these `DEFAULT_STATES` (`apps/api/plane/db/models/state.py:24-62`; created in `app/views/project/base.py:281-295`):

| Name | Group | Colour | Sequence | Default |
|---|---|---|---|---|
| Backlog | `backlog` | #60646C | 15000 | **True** |
| Todo | `unstarted` | #60646C | 25000 | |
| In Progress | `started` | #F59E0B | 35000 | |
| Done | `completed` | #46A758 | 45000 | |
| Cancelled | `cancelled` | #9AA4BC | 55000 | |
| Triage | `triage` | #4E5355 | 65000 | hidden (intake only) |

Frontend group metadata: `backlog` (#d9d9d9), `unstarted` (#3f76ff), `started` (#f59e0b), `completed` (#16a34a), `cancelled` (#dc2626) (`packages/constants/src/state.ts:14-52`). Users may add any number of states per group, rename them, reorder by drag-and-drop (recomputes `sequence`) and "Mark as default" (`apps/web/core/components/project-states/state-item.tsx:61-118`). State group semantics used by the backend: `open` = backlog+unstarted+started; `completed` and `cancelled` are terminal; `triage` is invisible outside intake. State ordering for sorting is `backlog, unstarted, started, completed, cancelled` (`apps/api/plane/utils/order_queryset.py:8-34`).

### 5.2 State rules (API `StateViewSet`, `apps/api/plane/app/views/state/base.py:24-142`)

- Create / delete / mark-default: project **Admin only**; list excludes triage states; `mark_as_default` flips all others to `default=False`.
- **`partial_update` is NOT admin-only**: it is decorated `@allow_permission([ROLE.ADMIN, ROLE.MEMBER, ROLE.GUEST])`, so any active project member — Guests included — can rename, recolour, re-group or re-sequence a workflow state (`apps/api/plane/app/views/state/base.py:61-62`).
- Delete refuses the default state and any **non-empty** state (`"The state is not empty, only empty states can be deleted"`; also in v1: `apps/api/plane/api/views/state.py:225-245`). Cannot create a state with `group=triage` via v1 (`api/serializers/state.py:19-25`).
- `IntakeStateEndpoint` returns the triage state; the intake endpoint auto-creates it if missing (`app/views/intake/base.py:246-256`).

### 5.3 Transitions

**There are no transition rules in CE**: any state → any state is allowed; `workflow/state-option.tsx` is a plain Combobox option (`apps/web/core/components/workflow/state-option.tsx:26-45`), and no backend code validates transitions. Custom workflows / approvals are marketed as Business-plan features (`packages/constants/src/subscription.ts:7-23`).

What happens on a state change (`Issue.save()` + activity task):
1. `completed_at` is recomputed: `now()` if new group is `completed`, otherwise `NULL` (`issue.py:240-255`). **Reopening an issue erases its completion timestamp** — it disappears from burndown history.
2. `issue_activity` Celery task writes `IssueActivity(field="state", old_value/new_value=state names, old_identifier/new_identifier=state UUIDs)` (`bgtasks/issue_activities_task.py:189-226`) and, when `notification=True`, fans out in-app/email notifications per subscriber preference (`state_change`, `issue_completed`) (`bgtasks/notification_task.py:311-349`).
3. Webhooks: `model_activity` emits one `issue` `updated` event per changed key (`bgtasks/webhook_task.py:479-520`).

### 5.4 archived_at and automation

- Manual archive (single or bulk) requires the issue's state group to be `completed` or `cancelled`, else 400 `"Can only archive completed or cancelled state group issue"` / `INVALID_ARCHIVE_STATE_GROUP`; sets `archived_at = today` (`app/views/issue/archive.py:256-303,305-343`). Unarchive clears it. Single archive/unarchive require project **Admin or Member** (`archive.py:256,280`); the bulk endpoint (also Admin/Member, `:308`) selects through `Issue.objects` — not `issue_objects` — and writes with `bulk_update`, so it bypasses `Issue.save()` entirely (`:315-341`).
- Nightly `archive_and_close_old_issues` (01:00 UTC): for projects with `archive_in > 0`, archives completed/cancelled issues untouched for `archive_in*30` days (not in an open cycle/module); for `close_in > 0`, moves backlog/unstarted/started issues untouched for `close_in*30` days to `project.default_state` — or, when that is unset, to `State.objects.filter(group="cancelled").first()`, a query with **no project filter**, i.e. the first cancelled state in the whole database, which may belong to a different project (`bgtasks/issue_automation_task.py:119-122`). Set `default_state` before enabling `close_in`. Both paths write with `bulk_update` (`:68` archive, `:131` close), so `Issue.save()` — and therefore `_sync_completed_at` — never runs: `completed_at` is **not** resynced on auto-close or auto-archive. An activity row is still emitted per issue (`:22-149`). UI: Project settings → Automations, months 1/3/6/9/12 (`packages/constants/src/project.ts:61-67`).
- Archived issues are excluded from `issue_objects`, so from every board, cycle count and chart — but **not** from the CSV/XLSX/JSON export, which uses `Issue.objects` (`bgtasks/export_task.py:149-155`).

### 5.5 What "Done" means for progress and burndown

- Cycle/module **counters** (`completed_issues` etc.) use `state.group` live (`app/views/cycle/base.py:126-138`; `module/base.py:86-144`).
- Cycle/module **burndown and assignee/label distributions** use `completed_at IS NOT NULL` (`cycle/base.py:874-894,971-996`; `utils/analytics_plot.py:184-197`). They agree only because `_sync_completed_at` keeps them in lockstep.
- **Cancelled is not "done" for the burndown**: only `completed_at` subtracts from the remaining line, so a cancelled item stays on the remaining curve (`analytics_plot.py:251-263`).
- `ProjectStatsEndpoint.completed_issues` counts `completed` **and** `cancelled` (`app/views/analytic/base.py:424-428`) — a different definition.
- Advanced analytics "created vs completed" buckets by **creation month** and counts items whose *current* group is `completed`; `completed_at` is not used there (`app/views/analytic/advance.py:217-283`).

---

## 6. Cycles (Sprint)

### 6.1 Rules

| Rule | Evidence |
|---|---|
| Project must have `cycle_view=True` (default False) — else v1 create fails with "Cycles are not enabled for this project" | `apps/api/plane/api/serializers/cycle.py:61-97`; `project.py:94` |
| `start_date` and `end_date` are **both set or both null** (400 otherwise); `start > end` rejected; dates are converted to UTC in the project timezone; `owned_by` defaults to the caller | `api/views/cycle.py:301-357`; `api/serializers/cycle.py:61-97`; `app/serializers/cycle.py:23-38` |
| Status is **annotated in SQL, not stored**: `CURRENT` if `start_date <= now <= end_date`, `UPCOMING` if `start_date > now`, `COMPLETED` if `end_date < now`, `DRAFT` when both dates null (default). `now` is plain **`timezone.now()` in UTC** — the code converts UTC → project tz → UTC, which is an identity; the project timezone only bites at *write* time, where `convert_to_utc` turns the submitted local dates into UTC datetimes | `app/views/cycle/base.py:82-88,152-167`; `app/serializers/cycle.py:23-38` |
| `?cycle_view=current` filters the same range; v1 also supports `all\|upcoming\|completed\|draft\|incomplete` (`incomplete` = end ≥ now or null). **App API: every cycle_view is unpaginated** (`list` returns `queryset.values(...)` directly). **v1**: `current` is an unpaginated array, all other views use cursor pagination | `app/views/cycle/base.py:180-268`; `api/views/cycle.py:203-283` |
| Overlap is an **advisory client-side check only**: `POST cycles/date-check/` always answers HTTP 200, returning `{"status": false, "error": …}` when a cycle intersects (it does not exclude archived cycles), and only the React create modal / sidebar header act on it. Neither create nor PATCH calls it, so any API client can create overlapping cycles; there is no DB constraint enforcing "one active cycle" | `app/views/cycle/base.py:519-556`; `apps/web/core/components/cycles/modal.tsx:103`; `apps/web/core/components/cycles/analytics-sidebar/sidebar-header.tsx:77` |
| Consequence: a project can hold **several `CURRENT` cycles at once** (created via API, or by editing dates); `?cycle_view=current` then returns several rows and the UI shows the first. Warn any lab that scripts cycle creation | `app/views/cycle/base.py:82-88,204-237` |
| A completed cycle (`end_date < now`) rejects a PATCH **that lacks `sort_order`** (400 "The Cycle has already been completed so it cannot be edited"). The restriction is not actually enforced: both views compute a sanitised `request_data = {"sort_order": …}` but then hand the **original `request.data`** to the serializer, so a body containing `sort_order` plus name/dates/anything else is applied in full. Archived cycles cannot be edited at all | `app/views/cycle/base.py:347-359`; `api/views/cycle.py:559-573` |
| No new issues in a completed cycle: 400 `{"code":"CYCLE_COMPLETED"}` (v1) / `{"error": "The Cycle has already been completed so no new issues can be added"}` (app). Empty list: **v1** 400 `{"error":"Work items are required","code":"MISSING_WORK_ITEMS"}`, **app** 400 `{"error":"Issues are required"}` (no code) | `app/views/cycle/issue.py:227-236`; `api/views/cycle.py:972-989` |
| Adding an issue that is already in another cycle **moves** it: the handler re-points the existing `CycleIssue` row with `bulk_update(["cycle_id"])`. This "one cycle per issue" rule is **view logic, not a DB constraint** — the constraint is only unique `(cycle, issue)` | `app/views/cycle/issue.py:242-299`; `api/views/cycle.py:992-1043`; `cycle.py:112-120` |
| Archiving guards on `cycle.end_date >= timezone.now()`: a cycle whose end date is in the future gets 400 "Only completed cycles can be archived", while a **draft cycle (`end_date` NULL) raises `TypeError` → HTTP 500**. Archive is synchronous, no background task. The app endpoint answers **200 `{"archived_at": …}`**, v1 answers **204** | `app/views/cycle/archive.py:586-604`; `api/views/cycle.py:809-829` |
| Delete: **app API** requires project Admin **or the creator** (`@allow_permission([ROLE.ADMIN], creator=True, model=Cycle)`); **v1** requires the cycle owner or project role 20 (403 "Only admin or creator can delete the cycle") | `app/views/cycle/base.py:477`; `api/views/cycle.py:617-636` |
| Guests can **list** cycles but not open one: `GET cycles/<pk>/` is ADMIN/MEMBER only → 403 for Guests. Important when labs use guest accounts | `app/views/cycle/base.py:183,410-411` |
| App-API create sets `owned_by=request.user` in the view and its serializer does **not** check `cycle_view` — only v1 refuses with "Cycles are not enabled for this project" | `app/views/cycle/base.py:271-277`; `api/serializers/cycle.py:74-75` |
| Cycle status list in UI: `current` (#F59E0B), `upcoming` (#3F76FF), `completed` (#16A34A), `draft` (#525252) | `packages/constants/src/cycle.ts:8-48` |

### 6.2 Endpoints (app API, `apps/api/plane/app/urls/cycle.py`)

| URL under `/api/workspaces/<slug>/projects/<pid>/` | View | Lines |
|---|---|---|
| `cycles/` GET/POST, `cycles/<pk>/` GET/PATCH/DELETE | `CycleViewSet` | 22-38 |
| `cycles/<id>/cycle-issues/[<issue_id>/]` | `CycleIssueViewSet` | 39-55 |
| `cycles/date-check/` | `CycleDateCheckEndpoint` | 56-60 |
| `user-favorite-cycles/[<cycle_id>/]` | `CycleFavoriteViewSet` | 61-70 |
| `cycles/<id>/transfer-issues/` POST | `TransferCycleIssueEndpoint` | 71-75 |
| `cycles/<id>/user-properties/` | `CycleUserPropertiesEndpoint` | 76-80 |
| `cycles/<id>/archive/`, `archived-cycles/`, `archived-cycles/<pk>/` | `CycleArchiveUnarchiveEndpoint` | 81-95 |
| `cycles/<id>/progress/` GET | `CycleProgressEndpoint` | 96-100 |
| `cycles/<id>/analytics/?type=issues\|points` GET | `CycleAnalyticsEndpoint` | 101-105 |

`GET workspaces/<slug>/cycles/` (`urls/workspace.py:182-186`) returns **all non-archived cycles** the caller can see with six state-group counts — no "active only" filter (`app/views/workspace/cycle.py:19-109`). NOT FOUND: any route `cycles/<id>/cycle-progress/` (the frontend service method `workspaceActiveCyclesProgressPro` calls it and is labelled "(Pro feature)"; the store action is a no-op) (`packages/services/src/cycle/cycle-analytics.service.ts:65-83`; `apps/web/core/store/cycle.store.ts:496-504`).

### 6.3 Progress counters — `CycleProgressEndpoint` (`app/views/cycle/base.py:658-783`)

Permission ADMIN/MEMBER/GUEST. Response keys: `backlog_issues, unstarted_issues, started_issues, completed_issues, cancelled_issues, total_issues` plus `backlog/unstarted/started/completed/cancelled/total_estimate_points`.
- Estimate points: one `aggregate()` over `Issue.issue_objects.filter(estimate_point__estimate__type="points", issue_cycle__cycle_id=…)` with `Sum(Case(When(state__group=g, then=Cast(estimate_point__value, Float))))` per group (`:664-711`). **Always live**, never from the snapshot; category estimates never contribute.
- Issue counts: if `cycle.progress_snapshot` is non-empty, the six counts are read from the snapshot (`:712-718`); otherwise each is a live `.count()` by `state__group` (`:720-765`).
- The list/detail viewset itself annotates only `total_issues`, `completed_issues`, `cancelled_issues`, `status`, `assignee_ids` (filters: non-archived, non-draft, non-deleted) (`:113-178`).

### 6.4 Burndown — `CycleAnalyticsEndpoint` + `burndown_plot()`

`CycleAnalyticsEndpoint` (`app/views/cycle/base.py:786-1049`), `?type=issues` (default) or `points`:
1. Draft cycle (no start or end) → 400 `"Cycle has no start or end date"` (`:807-811`).
2. **Snapshot short-circuit**: if `progress_snapshot` exists, returns `progress_snapshot["distribution"]` (`labels, assignees, completion_chart`) regardless of `?type` (`:821-830`).
3. `type=points` only when the project's active estimate is `type="points"` (`:832-838`). If it is not, the endpoint still answers **200** with `assignees: []`, `labels: []`, `completion_chart: {}` — an empty payload, not an error; students routinely misread that as "no data" (`:832-838,1042-1048`).
   When it is: per assignee/label `total_estimates`, `completed_estimates` (filter `completed_at NOT NULL`), `pending_estimates` (`completed_at NULL`) (`:844-931`); `completion_chart = burndown_plot(plot_type="points")` (`:932-938`).
4. `type=issues`: per assignee/label `total_issues`, `completed_issues` (`completed_at NOT NULL`), `pending_issues` (`:941-1033`); `completion_chart = burndown_plot(plot_type="issues")` (`:1034-1040`).

`burndown_plot(queryset, slug, project_id, plot_type, cycle_id=None, module_id=None)` (`apps/api/plane/utils/analytics_plot.py:123-265`) — exact logic:
1. `total = queryset.total_issues` (scalar, `:125`); in points mode `total = sum(float(estimate_point__value))` over live cycle/module issues that have an estimate (`:134-156`).
2. Date axis: every calendar day from `start_date.date()` to `end_date.date()` inclusive (module: `start_date`..`target_date`) (`:158-165,199-203`); `chart_data = {"YYYY-MM-DD": 0}`.
3. Completed distribution: `Issue.issue_objects.filter(<membership>).annotate(date=TruncDate("completed_at")).values("date").annotate(Count("id"))`, or per-issue `estimate_point__value` in points mode (`:170-197,207-234`).
4. For each day `d`: `remaining = total − Σ(completed with completed-date ≤ d)`; if `d > today` the value is **`None`** so the line stops at today (`:237-264`).
5. Returns `{"YYYY-MM-DD": remaining | None}`.

Documented consequences: it is a **remaining-work line driven by `completed_at`**, not a replay of state history; `total` is a single scalar, so issues added mid-cycle raise every past day retroactively; issues completed before the cycle started count as done on day 1; cancelled issues are **not** subtracted; issues removed from the cycle vanish entirely; reopened issues lose their `completed_at` and re-appear as remaining for all days.

**Timezone behaviour** (matters for a UTC+7 classroom): `Project.timezone` defaults to `"UTC"` (`db/models/project.py:117`); cycle `start_date`/`end_date` are stored as UTC datetimes derived from project-local date boundaries by `convert_to_utc`; and the burndown's "stop the line after today" cutoff compares against the **server's UTC date** (`analytics_plot.py:246,260`). Early in the local morning the last plotted day can therefore still be "yesterday".

**Ideal line is frontend-only**: `ideal = totalIssues * (1 − index/(N−1))` per point, drawn dashed (`apps/web/core/components/core/sidebar/progress-chart.tsx:20-74`, colours `#3F76FF` current / `#A9BBD0` ideal). `ProgressChart` uses `@plane/propel` AreaChart (Recharts). "Points vs work items" toggle (`TCycleEstimateType = "issues"|"points"`) switches between `cycle.distribution` and `cycle.estimate_distribution` (`analytics-sidebar/sidebar-chart.tsx:38-79`; `packages/types/src/cycle/cycle.ts:138`). A `burnup` plot-type option exists in constants and the store, **but no burn-up renderer exists** (`issue-progress.tsx:40-43`; grep `burnup` → constant only). Pending label under the chart = backlog + unstarted + started (`active-cycle/productivity.tsx:66-69`).

### 6.5 `progress_snapshot` and transfer

`transfer_cycle_issues()` (`apps/api/plane/utils/cycle_transfer_issues.py`) is called by `POST …/cycles/<id>/transfer-issues/` (app `cycle/base.py:594-622`; v1 `api/views/cycle.py:1223-1250`, body `new_cycle_id`):
1. The shared utility checks **only the destination**: `end_date < now` → "The cycle where the issues are transferred is already completed" (`utils/cycle_transfer_issues.py:58-65`). The "The old cycle is not completed yet" guard exists **only in the v1 endpoint** (`api/views/cycle.py:1237-1247`), and even there it tests `end_date > now`, which lets draft cycles (`end_date` NULL) through. `TransferCycleIssueEndpoint` in the app API calls the utility with **no source check at all** (`app/views/cycle/base.py:594-622`), so the web app can transfer — and permanently snapshot — a running or draft cycle.
2. Annotates the old cycle with `total/completed/cancelled/started/unstarted/backlog_issues` (`:67-142`), builds assignee/label distributions and `completion_chart = burndown_plot("issues")` (and the points variants when the project uses points) (`:163-405`).
3. Saves `progress_snapshot` on the **old** cycle with exactly: `total_issues, completed_issues, cancelled_issues, started_issues, unstarted_issues, backlog_issues, distribution{labels, assignees, completion_chart}, estimate_distribution ({} or {labels, assignees, completion_chart})` (`:407-432`).
4. Moves only `CycleIssue` rows whose issue group is `backlog/unstarted/started` (non-archived, non-draft) by `bulk_update(cycle_id)` (`:434-458`); completed/cancelled items stay.
5. Emits one `IssueActivity(field="cycles", verb="updated", old_identifier=old cycle, new_identifier=new cycle)` per moved issue (`:460-476`; `bgtasks/issue_activities_task.py:755-796`).

**Transfer is the only code path that computes and stores a snapshot** — nothing writes one when `end_date` passes (`progress_snapshot` is assigned only at `cycle_transfer_issues.py:410`). It is nevertheless **writable over the app API**: `CycleWriteSerializer` is `fields = "__all__"` with only workspace/project/owned_by/archived_at read-only, so any session-authenticated client can `PATCH .../cycles/<pk>/` with an arbitrary `progress_snapshot` (the UI never does); the v1 serializers whitelist fields and do not expose it (`app/serializers/cycle.py:40-43`; `api/serializers/cycle.py:38-49,108-112`). Once set, a snapshot is **never cleared or regenerated** — no endpoint or task resets it — so `CycleProgressEndpoint` counts and `CycleAnalyticsEndpoint` distributions stay frozen forever while `*_estimate_points` stay live; a transfer performed on a still-running cycle (possible from the web app, above) permanently corrupts that cycle's dashboard. Once present it overrides live counts in `CycleProgressEndpoint` and the whole distribution in `CycleAnalyticsEndpoint`; the frontend copies snapshot keys over the cycle object (`validateCycleSnapshot`, `analytics-sidebar/issue-progress.tsx:45-58`). Archived-cycle retrieve recomputes charts on demand (`app/views/cycle/archive.py:355-372,455-470,566-585`).

### 6.6 UI surfaces (CE)

Project cycles page shows the **project's** active cycle: `ActiveCycleProgress` (state-group counts), `ActiveCycleProductivity` (burndown), `ActiveCycleStats` (Priority / Assignees / Labels tabs) (`apps/web/core/components/cycles/active-cycle/root.tsx:79-86`). The **workspace** `/:ws/active-cycles` route renders only `WorkspaceActiveCyclesUpgrade`, a `ProIcon` button linking to `MARKETING_PRICING_PAGE_LINK` = `https://plane.so/pricing` (`apps/web/core/components/active-cycles/workspace-active-cycles-upgrade.tsx:24,96,100`; `packages/constants/src/endpoints.ts:31`).

---

## 7. Modules (Epic-like grouping)

| Aspect | Fact | Evidence |
|---|---|---|
| Fields | `name, description, description_text (JSON), description_html (JSON), start_date, target_date (DateField), status, lead (SET_NULL), members (M2M), view_props, sort_order, external_*, archived_at, logo_props` | `apps/api/plane/db/models/module.py:68-99` |
| Status | `backlog, planned, in-progress, paused, completed, cancelled`; default `planned`; **manual, never derived from progress** | `module.py:58-64,74-85` |
| Constraints | unique `(name, project)` (v1: `MODULE_NAME_ALREADY_EXISTS`); `start > target` rejected; project needs `module_view=True` ("Modules are not enabled for this project") | `module.py:102-109`; `api/serializers/module.py:36-100` |
| Membership | `ModuleIssue` unique `(issue, module)` → many modules per issue; add via `modules/<id>/issues/` (app) or `module-issues/` (v1) | `module.py:157-164`; `app/urls/module.py:19-103` |
| Archive | Only `completed` or `cancelled` modules ("Only completed or cancelled modules can be archived"); synchronous; the app endpoint returns 200 `{"archived_at": …}` | `api/views/module.py:1084-1096`; `app/views/module/archive.py:546-550,559` |
| Permissions | `GET modules/<pk>/` (detail) is **ADMIN/MEMBER only** — Guests can list but get 403 on the detail route; delete requires project Admin **or the creator** (`@allow_permission([ROLE.ADMIN], creator=True, model=Module)`) | `app/views/module/base.py:353-354,395-396,723` |
| Progress counts | `ModuleViewSet.get_queryset` annotates `backlog/unstarted/started/completed/cancelled/total_issues` via correlated subqueries on `issue_objects`, plus `*_estimate_points` restricted to `estimate_point__estimate__type="points"`, all `Coalesce`d to 0; `member_ids` via ArrayAgg | `app/views/module/base.py:86-210,224-290` |
| Burndown | `retrieve` builds `distribution` (assignees/labels by `completed_at`) and `distribution.completion_chart = burndown_plot("issues", module_id=pk)` only when `start_date`, `target_date` **and** `total_issues > 0`; `estimate_distribution` + points chart when the project uses points and both dates exist | `app/views/module/base.py:396-649` |
| Workspace list | `GET workspaces/<slug>/modules/` annotates the six counts with `Count("issue_module")`; no estimate points | `app/views/workspace/module.py:44-114` |
| Webhooks | `module` flag also covers `module_issue` events | `bgtasks/webhook_task.py:433-448` |
| UI | Layouts list / board / gantt; order by name, progress, issues_length, target_date, created_at, sort_order; sidebar: status, date range, lead, members, counts, `ModuleAnalyticsProgress` (same `ProgressChart`), links | `packages/constants/src/module.ts:10-116`; `apps/web/core/components/modules/analytics-sidebar/root.tsx:41-45,201-429` |

---

## 8. Estimates

| Aspect | Fact | Evidence |
|---|---|---|
| Systems (frontend) | `POINTS` (templates Fibonacci / Linear / Squares / Custom), `CATEGORIES` (T-shirt sizes / Easy-to-hard / Custom), `TIME` (Hours, **`is_ee: true`**); 2–6 points per estimate | `packages/constants/src/estimates.ts:12-142` |
| Systems (backend) | `EstimateType` = `categories` (default) and `points` only; **no `time` type** (migration 0121) | `apps/api/plane/db/models/estimate.py:13-15` |
| CE availability | `isEstimateSystemEnabled` returns true only for POINTS/CATEGORIES; the create modal hides other systems | `apps/web/core/components/estimates/create/helper.tsx:10-18` (the file is `.tsx`, there is no `helper.ts`); `create/stage-one.tsx:39-64` |
| Editing | CE list items render **only a delete button**; no update modal is mounted — to change an estimate, delete and recreate | `estimates/estimate-list-item-buttons.tsx:21-33`; `estimates/root.tsx:40,82,100-140` |
| Activation | `Project.estimate` FK selects the active `Estimate`; settings page has an enable/disable switch; the detail sidebar shows the estimate dropdown only when enabled | `project.py:109`; `issue-detail/sidebar.tsx:84-250` |
| Attachment to issues | `Issue.estimate_point` FK → `EstimatePoint` (`key` int, `value` string) | `issue.py:129-135`; `estimate.py:44-47` |
| API (app) | `projects/<id>/project-estimates/`, `estimates/[<id>/]`, `estimates/<id>/estimate-points/[<pt>/]` | `app/urls/estimate.py:16-39` |
| API (v1) | `apps/api/plane/api/urls/estimate.py` exists but is **not included** in `plane.api.urls` → `/api/v1/…/estimates/` is unreachable; `estimate_point` may still be set on work items | `api/urls/__init__.py:5-31`; `api/serializers/issue.py:75-149` |
| In charts | Every points computation is `Cast(estimate_point__value, Float)` restricted to `estimate_point__estimate__type="points"`; category estimates never produce a points chart; cycle `*_estimate_points`, module `*_estimate_points`, `burndown_plot("points")`, legacy analytics `y_axis=estimate` | `cycle/base.py:664-711`; `module/base.py:145-210`; `analytics_plot.py:110-115,127-156` |
| Legacy | `Issue.point` (0-12 int) is still summed by `DefaultAnalyticsEndpoint.open/total_estimate_sum` — not `estimate_point` | `app/views/analytic/base.py:371-373` |
| Export column | `estimate` = `estimate_point.value` | `utils/porters/serializers/issue.py:36-66` |
| Advanced analytics | UI offers y-axis `ESTIMATE_POINT_COUNT`, but the CE backend only does `Count("id")` | `packages/constants/src/analytics/common.ts:175-188`; `utils/build_chart.py:37-41,179` |

---

## 9. Views, Pages, Intake, Labels, Priority

### 9.1 Views

- A view = saved filter set: `name, description, logo_props, rich_filters, display_filters, display_properties, access` where `EViewAccess { PRIVATE=0, PUBLIC=1 }` (`apps/web/core/components/views/form.tsx:46-98`; `packages/types/src/views.ts:15-18`). Backend `IssueView.access` default 1 = Public; `query` is recomputed from `filters` on every save (`view.py:66,79-81`).
- Project views: `projects/<id>/views/[<pk>/]` (`IssueViewViewSet`); workspace views: `workspaces/<slug>/views/[<pk>/]` (`WorkspaceViewViewSet`, delete Admin/creator) and their issues at `workspaces/<slug>/issues/` (`app/urls/views.py:17-64`; `app/views/view/base.py:52-262`).
- **`issue_views_view` is a UI navigation toggle, not an API gate**: no backend check reads it — `IssueViewViewSet.create` has no feature check and the flag appears in `app/views` only inside a project field list (`app/views/view/base.py:262-300`; `app/views/project/base.py:186`). Same for `page_view` in §9.2. (Contrast cycles/modules, which v1 *does* gate in the serializer.)
- **A view can only be edited by its creator**: PATCH on both project and workspace views is `@allow_permission(allowed_roles=[], creator=True, model=IssueView)` plus an explicit owner check, so not even a workspace or project Admin can edit someone else's saved view (`app/views/view/base.py:86-87,95`, `349-350,357-360`); delete is admin-or-creator.
- Default workspace views: `all-issues, assigned, created, subscribed` (`packages/constants/src/workspace.ts:174-191`).
- Layouts: `list, kanban, calendar, gantt_chart, spreadsheet` (`packages/types/src/issues/issue.ts:15-21`); kanban supports `sub_group_by` swimlanes; **list** `group_by` ∈ state, priority, cycle, module, labels, assignees, created_by, `null` (no grouping), **kanban** `group_by` is the same list **without `null`** — only kanban's `sub_group_by` offers `null` (`filter.ts:224,236-237`); `order_by` ∈ sort_order, -created_at, -updated_at, start_date, -priority, target_date (`packages/constants/src/issue/filter.ts:206-279`). Display properties: `assignee, start_date, due_date, labels, key, priority, state, sub_issue_count, link, attachment_count, estimate, created_on, updated_on, modules, cycle, issue_type` (`issue/common.ts:142-159`). Rich filter properties: `state_group, priority, start_date, target_date, assignee_id, mention_id, created_by_id, subscriber_id, label_id, state_id, cycle_id, module_id, project_id, created_at, updated_at` (`packages/types/src/view-props.ts:96-112`).
- Backend allowlists: `ISSUE_GROUP_BY_ALLOWLIST` = state_id, state__group, priority, labels__id, assignees__id, issue_module__module_id, cycle_id, project_id, created_by, target_date, start_date; order_by sanitised against `ISSUE_ORDER_BY_ALLOWLIST`; priority order urgent>high>medium>low>none (`utils/order_queryset.py:8-34,86-98,145-193`).
- **View publishing is a stub in CE**: `useViewPublish` returns `isPublishModalOpen:false` (`views/publish/use-view-publish.tsx:8-13`). Gantt dependency lines are off: `ENABLE_ISSUE_DEPENDENCIES = false` (`issue/filter.ts:361`).

### 9.2 Pages

- **Only project pages exist in CE**: `EPageStoreType.PROJECT` is the sole enum member (`apps/web/core/hooks/store/use-page-store.ts:13-15`); the live server handles only `documentType === "project_page"` — `team_page`/`workspace_page` are declared in web types but unhandled ("Implementation for this is found in the enterprise repository", `apps/live/src/services/page/extended.service.ts:9-18`; `apps/live/src/types/index.ts:26`). `page_view` (default True) is likewise only a **UI navigation toggle** — no page view or permission class reads it, the API creates pages regardless.
- Access: `0 Public / 1 Private`, default Public (`page.py:24-25,37`). Private pages are **owner-only** in CE (`_has_private_page_action_access` returns False, docstring "Override for feature flag logic", `apps/api/plane/app/permissions/page.py:93-98`). `usePageFlag` returns `isMovePageEnabled:false, isPageSharingEnabled:false` (`apps/web/core/hooks/use-page-flag.ts:12-14`).
- Rules: locked page rejects updates; only owner changes access; only owner/admin archive/unarchive/delete; delete requires archived first; archive cascades to descendants (`app/views/page/base.py:59-72,154-199,246-392`). Routes: `projects/<id>/pages/[<page_id>/]`, `pages/<id>/archive|lock|access|description|versions|duplicate/` (`app/urls/page.py:17-74`).
- Editor: TipTap starter-kit + callout, code, custom-image, custom-link, emoji, mentions, table, text-align, work-item-embed, slash commands (h1–h6, lists, to-do, table, quote, code, callout, divider, emoji, image, colours) (`packages/editor/src/core/extensions/slash-commands/command-items-list.tsx:63-297`). CE disables the `ai` and `collaboration-cursor` editor extensions (`apps/web/core/hooks/use-editor-flagging.ts:33-46`) — **multi-user cursors are not shown even though Yjs sync works**.
- Collaboration: `HocuspocusProvider` to `${LIVE_BASE_URL||origin}${LIVE_BASE_PATH}/collaboration` (`editor-body.tsx:198-215`); live fetches/stores the binary through `GET/PATCH /api/workspaces/{slug}/projects/{project}/pages/{id}/description/` with the user's cookie; PATCH triggers `page_transaction` and `track_page_version` tasks; store debounce 10 s (`apps/live/src/extensions/database.ts:26-91`; `app/views/page/base.py:521-575`; `apps/live/src/hocuspocus.ts:45-51`). Page versions: new version when same owner and >600 s since last save, else update; trimmed to 20 (`bgtasks/page_version_task.py:19-74`).
- Page actions: lock, access toggle, open in new tab, copy link, make a copy (duplicates assets via `copy_s3_objects_of_description_and_assets` → live `/convert-document`), archive/restore, delete (`pages/dropdowns/actions.tsx:84-147`; `bgtasks/copy_s3_object.py:67-125`). A `move` action is coded in the same menu (`actions.tsx:143`) but is gated off by `usePageFlag().isMovePageEnabled = false` (`use-page-flag.ts:19`). PDF export via live `POST /live/pdf-export/` (cookie required). The URL module also mounts `pages-summary/` and `favorite-pages/<page_id>/` (`app/urls/page.py:17-21,33-37`).

### 9.3 Intake

- Requires `intake_view=True` (UI key `inbox_view`); enabling auto-creates the default Intake; default intake cannot be deleted (`app/views/project/base.py:358-365`; `app/views/intake/base.py:82-88`).
- Creating an intake item creates a normal `Issue` forced into the project's **Triage** state (auto-created, seq 65000, #4E5355) plus `IntakeIssue(status=-2, source=IN_APP)` (`app/views/intake/base.py:228-266`; v1 `api/views/intake.py:143-226`). Any role incl. Guest can create; guests may only edit their own items' name/description; changing `status/snoozed_till/duplicate_to/source/source_email` requires role > 15 (`api/views/intake.py:342-393`).
- Status codes PENDING -2, REJECTED/DECLINED -1, SNOOZED 0, ACCEPTED 1, DUPLICATE 2; UI tabs `open`/`closed`; accept/decline/duplicate only from pending or snoozed (`packages/types/src/inbox.ts:12-31`; `inbox/content/inbox-issue-header.tsx:42-45,95-157`). Accepting moves the issue out of triage into the project's default state (it then appears in `issue_objects`) — but only inside the serializer's `update()`, and only when the issue is **still in a triage-group state** *and* the project actually has a `default=True` state; otherwise the issue silently keeps the state it has (`app/serializers/intake.py:68-84`; `api/serializers/intake.py:143-157`).
- Sources: the **backend** `SourceType` enum has the single member `IN_APP` and `IntakeIssue.source` is an unconstrained `CharField` defaulting to `"IN_APP"` (`apps/api/plane/db/models/intake.py:38-39,70`); only the **web** enum `EInboxIssueSource` adds `FORMS` and `EMAIL` (`packages/types/src/inbox.ts:27-31`). **No email/forms intake UI or backend in CE** — the settings page has a single toggle (`features/intake/page.tsx:44`). "Intake Forms" is marketed as Business plan (`subscription.ts:7-23`).
- Routes: `projects/<id>/intakes/[<pk>/]`, `intake-issues/[<pk>/]` (+ legacy `inboxes/`, `inbox-issues/`) (`app/urls/intake.py:17-64`); v1 `intake-issues/` (`api/urls/intake.py:14-23`).

### 9.4 Labels

Workspace-scoped model with nullable project (§4.6). UI: 10-colour palette + random; **label groups** via parent/child drag-and-drop (a parent cannot be dropped onto its child); inline create/update; delete modal (`packages/constants/src/label.ts:7-21`; `labels/project-setting-label-list.tsx:130-135`; `labels/label-utils.ts:66-67`). Routes: `projects/<id>/issue-labels/[<pk>/]`, `bulk-create-labels/` (`app/urls/issue.py:71-92`); v1 `labels/` with 409 on duplicate name (`api/views/issue.py:878-968`). Workspace aggregate `workspaces/<slug>/labels/` (`app/urls/workspace.py:157-186`).

### 9.5 Priority

Fixed enum `urgent, high, medium, low, none`, **default `none`** (`issue.py:107-113`; `packages/constants/src/issue/filter.ts:66-97`). Sorting: `PRIORITY_ORDER` urgent>high>medium>low>none (`utils/order_queryset.py:8-9`); legacy analytics orders low, medium, high, urgent, none (`analytics_plot.py:65-70`). Priority is one of the `group_by`/`sub_group_by` keys and a rich-filter property. Not user-configurable.

---

## 10. Analytics & Home dashboard

### 10.1 Home (`/:workspaceSlug`)

Widgets in CE: `quick_links` (DashboardQuickLinks), `recents` (RecentActivityWidget), `my_stickies` (StickiesWidget); `new_at_plane` and `quick_tutorial` map to `null` components and are excluded on GET (`apps/web/core/components/home/home-dashboard-widgets.tsx:27-59`; `app/views/workspace/home.py:31-63`). Preferences per user/workspace at `GET/PATCH workspaces/<slug>/home-preferences/[<key>/]` (`app/urls/workspace.py:229-238`), reorderable via `ManageWidgetsModal`. The GET seeds and returns one row per widget as `key, is_enabled, config, sort_order`, explicitly **excluding the `quick_tutorial` and `new_at_plane` keys**; `PATCH …/home-preferences/<key>/` toggles or reorders exactly one widget (`app/views/workspace/home.py:31-65,67-70`). Home also shows greeting, `TourRoot` until `is_tour_completed`, and peek overviews (`home/root.tsx:50-61`). **There is no progress/analytics widget on Home and no Dashboard/Widget DB model** (§4.14).

Other personal surfaces: **Your work** (`/:ws/profile/:userId`) — the overview page mounts five components, `ProfileActivity, ProfilePriorityDistribution, ProfileStateDistribution, ProfileStats, ProfileWorkload` (`apps/web/app/(all)/[workspaceSlug]/(projects)/profile/[userId]/page.tsx:15-19`), and the tab list is **role-split**: `PROFILE_VIEWER_TAB` is *summary only*, while assigned/created/subscribed/activity live in the admin-only `PROFILE_ADMINS_TAB` (`packages/constants/src/profile.ts:10-44`) backed by `GET workspaces/<slug>/user-stats/<user_id>/` (`state_distribution, priority_distribution, created/assigned/completed/pending/subscribed_issues, present_cycles, upcoming_cycles`, `app/views/workspace/user.py:405-529`) and `user-activity/<user_id>/`; **Inbox** = `/notifications` (tabs ALL/MENTIONS, filters ASSIGNED/CREATED/SUBSCRIBED, snooze 1d/3d/5d/1w/2w/custom, `packages/constants/src/notification.ts:36-108`); **Drafts**; **Stickies** (30 per page). Legacy `GET users/me/workspaces/<slug>/dashboard/` still returns `issue_activities` (3 months/day), `completed_issues` by week-in-month, assigned/pending/completed counts, due-this-week, `state_distribution`, `overdue_issues`, `upcoming_issues` (`app/views/workspace/base.py:257-345`).

### 10.2 Analytics page (`/:ws/analytics/:tabId`)

Permissions: every `advance-analytics*` endpoint and the project peek analytics are **workspace/project ADMIN+MEMBER only** — Guests get 403 (`app/views/analytic/advance.py:104,158,285`; `analytic/project_analytics.py:84,165`); only the legacy `default-analytics/` and `project-stats/` also allow GUEST (`analytic/base.py:252,392`).

Tabs in v1.4.2: **`overview` and `work-items` only** (`packages/types/src/analytics.ts:40`; `apps/web/core/components/analytics/tabs.tsx:11-14`). NOT FOUND: cycle or module analytics tabs. The page calls only the three `advance-analytics*` endpoints (`apps/web/core/services/analytics.service.ts:23-89`).

| Tab / component | Chart | Endpoint | What the data actually is |
|---|---|---|---|
| Overview → `TotalInsights` | number tiles | `GET workspaces/<slug>/advance-analytics/?tab=overview` | `total_users/admins/members/guests` (WorkspaceMember, or ProjectMember when `project_ids` given), `total_projects`, `total_work_items`, `total_cycles`, `total_intake` — **date filter applied on `created_at`** (`app/views/analytic/advance.py:44-91`) |
| Overview → `ProjectInsights` | RadarChart (lazy) | `advance-analytics-stats/?type=work-items` | per project `cancelled/completed/backlog/un_started/started_work_items` (`advance.py:144-156`) |
| Overview → `ActiveProjects` | list | `advance-analytics-charts/?type=projects` | single-row counts `work_items, cycles, modules, intake, members, pages, views` (`advance.py:173-215`) |
| Work items → `TotalInsights` | tiles | `advance-analytics/?tab=work-items` | `total, started, backlog, un_started, completed_work_items` (`advance.py:93-102`) |
| Work items → `CreatedVsResolved` | AreaChart | `advance-analytics-charts/?type=work-items` | per **month** from workspace creation: `TruncMonth(created_at)`, `created_count`, `completed_count = items now in group completed` — bucketed by **creation month, not completion month** (`advance.py:217-283`) |
| Work items → `CustomizedInsights` (`PriorityChart`) | BarChart with x/y selectors + optional group_by | `advance-analytics-charts/?type=custom-work-items&x_axis=…&group_by=…` | `build_analytics_chart`: x_axis/group_by ∈ `STATES, STATE_GROUPS, LABELS, ASSIGNEES, ESTIMATE_POINTS, CYCLES, MODULES, PRIORITY, START_DATE, TARGET_DATE, CREATED_AT, COMPLETED_AT, CREATED_BY`; aggregate is **always `Count("id", distinct=True)`** (`utils/build_chart.py:20-75,153-193`) |
| Work items → `WorkItemsInsightTable` | TanStack table + CSV export (`export-to-csv`) | same stats endpoint | (`analytics/export.ts:8-31`) |

Gaps between UI and backend: the y-axis dropdown lists `WORK_ITEM_COUNT | ESTIMATE_POINT_COUNT | EPIC_WORK_ITEM_COUNT` and the types also declare pending/blocked/due-today metrics, but `get_y_axis_filter` knows only `WORK_ITEM_COUNT` (`packages/constants/src/analytics/common.ts:175-188`; `packages/types/src/analytics.ts:28-38`; `build_chart.py:37-41`); x-axes `WORK_ITEM_TYPES, PROJECTS, EPICS` raise `ValidationError("Invalid x_axis field")` (`build_chart.py:160-161`). Duration filter: yesterday / last 7 / 30 days / 3 months (+ custom for the analytics type) applied to `created_at` (`utils/date_utils.py:12-122`).

Project "peek" analytics (`/projects/<id>/advance-analytics[-stats|-charts]/`, `app/urls/analytic.py:75-89`) accept `?cycle_id=`/`?module_id=`: stats are **per assignee** by state group (`project_analytics.py:119-163`); the cycle/module `work-items` chart is **daily** over the cycle/module range, counting `CycleIssue`/`ModuleIssue` bridge rows by their own `created_at` (when the issue was added): per day `created_issues` = rows created that day, `completed_issues` = those whose issue is *currently* in group `completed`, and the headline `count` = **`created_count + completed_count`**, so completed items are double-counted in that series (`project_analytics.py:223-258`, line 253). A cycle or module without a `start_date` returns `{"data": [], "schema": {}}` (`:196-201,204-214`).

### 10.3 Legacy analytics endpoints (still mounted, `app/urls/analytic.py:25-59`)

- `GET workspaces/<slug>/analytics/?x_axis=&y_axis=&segment=` (ws Admin/Member): x/segment ∈ `state_id, state__group, labels__id, assignees__id, estimate_point__value, issue_cycle__cycle_id, issue_module__module_id, priority, start_date, target_date, created_at, completed_at`; y ∈ `issue_count | estimate`; date axes bucketed `"YYYY-M"`; response `{total, distribution, extras}` (`app/views/analytic/base.py:37-173`; `utils/analytics_plot.py:25-121`). Saved queries via `AnalyticView` (`analytic-view/`, `saved-analytic-view/<id>/`). `POST export-analytics/` e-mails a CSV (`bgtasks/analytic_plot_export.py:349-406`).
- `GET default-analytics/`: `total_issues(_classified)`, `open_issues(_classified)` (backlog+unstarted+started), `issue_completed_month_wise` (current year, `ExtractMonth(completed_at)`), top-5 `most_issue_created_user` / `most_issue_closed_user`, `pending_issue_user`, `open/total_estimate_sum` (legacy `point` field) (`base.py:251-388`).
- `GET project-stats/?fields=&project_ids=`: `total_issues, completed_issues (completed+cancelled), total_members, total_cycles, total_modules` (`base.py:391-456`).

### 10.4 Which timestamp drives which chart

| Output | Driver | Granularity | Evidence |
|---|---|---|---|
| Cycle/module burndown `completion_chart` | `Issue.completed_at` (TruncDate) vs scalar total | day; `None` after today | `analytics_plot.py:178-197,237-264` |
| Cycle progress counters | `state.group` live, or `progress_snapshot` | scalar | `cycle/base.py:712-765` |
| Cycle analytics assignee/label completed/pending | `completed_at IS [NOT] NULL` | scalar | `cycle/base.py:874-894,971-996` |
| Legacy analytics date axes | `created_at/start_date/target_date/completed_at` | year-month | `analytics_plot.py:43-59` |
| Default analytics `issue_completed_month_wise` | `completed_at` (current year) | month | `analytic/base.py:276-282` |
| Advanced "created vs completed" (workspace/project) | `created_at` month; completed = current state group | month | `advance.py:234-242`; `project_analytics.py:266-274` |
| Advanced cycle/module "created vs completed" | `CycleIssue/ModuleIssue.created_at` day; completed = current group | day | `project_analytics.py:225-258` |
| User dashboard completed-by-week | `completed_at` | week-in-month | `workspace/base.py:278-290` |

NOT FOUND in v1.4.2: velocity chart (the word appears only in OpenAPI marketing prose, `settings/openapi.py:75,81`), burn-up renderer, cumulative flow diagram, precomputed lead/cycle time, dashboards/reports. Lead time can be derived as `completed_at − created_at` (reset on reopen); cycle time needs the activity log: join `issue_activities.new_identifier` → `states.id` where `field='state'` and `states.group='started'` (state *names* in `old_value/new_value` can be renamed later, so join on the UUID) (`issue.py:415-448`; `issue_activities_task.py:189-226`).

### 10.5 Export (Workspace settings → Exports)

`POST workspaces/<slug>/export-issues/` with `provider ∈ csv|xlsx|json`, optional `project: [ids]`, `multiple: bool` (one file per project); ws Admin/Member (`app/views/exporter/base.py:22-63`). Creates `ExporterHistory(status="queued")` and queues `issue_export_task`, which uses **`Issue.objects` (archived, draft and triage rows included)** restricted to projects where the initiator is an active member, serialises via `DataExporter`, zips, uploads to `<workspace_id>/export-<slug>-<token6>-<date>.zip` with a **7-day presigned URL**, status `completed` (`bgtasks/export_task.py:42-124,127-226`). `ExporterHistory.status` choices are queued / processing / completed / failed with default `queued` (`db/models/exporter.py:37-45`). The nightly cleanup runs at **01:30 UTC** (`celery.py:63-66`), deletes S3 objects older than 8 days and nulls `url` — **the history row itself is kept** (`bgtasks/exporter_expired_task.py:22-53`). Columns in order: `project_name, project_identifier, parent, identifier (PROJ-123), sequence_id, name, state_name, priority, assignees, subscribers, created_by_name, start_date, target_date, completed_at, created_at, updated_at, archived_at, estimate, labels, cycles, modules, links, relations, comments, sub_issues_count, link_count, attachment_count, is_draft` (`utils/porters/serializers/issue.py:36-66`); lists joined with `", "` in CSV/XLSX, arrays in JSON.

---

## 11. Public REST API v1 (`/api/v1/`)

### 11.1 Authentication

- Header **`X-Api-Key: plane_api_<hex>`** (`auth_header_name = "X-Api-Key"`; header lookup is case-insensitive; OpenAPI names it `X-API-Key`) (`apps/api/plane/api/middleware/api_authentication.py:24`; `utils/openapi/auth.py:29-34`). `X-API-Key` is also explicitly added to `CORS_ALLOW_HEADERS`, so browser-side `fetch` labs against `/api/v1/` work cross-origin (`common.py:192`) — session cookies are still not accepted there.
- Lookup: `APIToken.objects.get(Q(expired_at__gt=now)|Q(expired_at__isnull=True), token=…, is_active=True, user__is_active=True)`; on miss `AuthenticationFailed("Given API token is not valid")` → **403** `{"detail": "Given API token is not valid"}`; `last_used` updated on success (`api_authentication.py:29-43`).
- Failures surface as **HTTP 403, not 401** (no `WWW-Authenticate` header); the contract test accepts either (`tests/contract/api/test_authentication.py:38-45`). Session cookies are **not** accepted on `/api/v1/` (`api/views/base.py:50-52,157-160`).
- Tokens are created in the **session** API: `POST /api/users/api-tokens/` (`label, description, expired_at`), raw token returned **only at creation**; list/patch/delete filter `is_service=False` (`app/views/api.py:21-57`; `app/urls/api.py:10-19`). UI: Profile settings → API tokens, expiry 1 week / 1 month / 3 months / 1 year / never (`api-token/modal/form.tsx:24-55`). NOT FOUND: any `/api/v1/` route to manage tokens or webhooks; any code creating `is_service=True` tokens.
- Every request with `X-Api-Key` runs as that user with `TimezoneMixin` activating `user_timezone` (`api/views/base.py:35-46`).

### 11.2 Rate limit

`ApiKeyRateThrottle(SimpleRateThrottle)`, scope `api_key`, rate `API_KEY_RATE_LIMIT` (env, default `60/minute`), cache key `api_key:{<raw token>}` in Redis → **per token** (`api/rate_limit.py:12-23`; `common.py:154`); flushing Redis resets the counters. `API_KEY_RATE_LIMIT` is one of the few tunables the CE compose really does forward, so a lab can raise it from `plane.env` (`deployments/cli/community/docker-compose.yml:58`).
**It only applies to views built on `BaseAPIView`**, which is what overrides `get_throttles()` and `finalize_response()` (`api/views/base.py:61-62,115-128`). `StickyViewSet` and `WorkspaceInvitationsViewset` extend `BaseViewSet`, which has neither override (`api/views/base.py:154-161`; `api/views/sticky.py:24`; `api/views/invite.py:24`), so `/api/v1/workspaces/<slug>/stickies/` and `…/invitations/` fall back to DRF's default `AnonRateThrottle` — a no-op for an authenticated caller — and return no `X-RateLimit-*` headers (`common.py:140`).
On the endpoints that are throttled, responses carry **`X-RateLimit-Remaining`** and **`X-RateLimit-Reset`** (unix ts); the throttle writes those into `request.META` **only when the request is allowed**, so a 429 carries neither header (`rate_limit.py:25-48`). Over limit → 429, and because the global DRF `EXCEPTION_HANDLER` is `auth_exception_handler`, the body is the auth-style `{"error_code": 5900, "error_message": "RATE_LIMIT_EXCEEDED"}`, not DRF's "Request was throttled" (`common.py:148`; `authentication/adapter/exception.py:25-31`). `APIToken.allowed_rate_limit` is never read.

### 11.3 Pagination

Query params `cursor` and `per_page`. Cursor format **`value:offset:is_prev`** (value = page size, offset = page number); default `"{per_page}:0:0"`; **`per_page` default 1000, max 1000** (`MAX_LIMIT = 1000`) — the OpenAPI docstring claiming default 20 / max 100 is wrong (`utils/paginator.py:32,49-57,87,643-653,679`; `utils/openapi/parameters.py:274-281`). Errors: `"Invalid per_page parameter."`, `"Invalid per_page value. Cannot exceed {max}."`, `"Invalid cursor parameter."`. Envelope: `grouped_by, sub_grouped_by, total_count, next_cursor, prev_cursor, next_page_results, prev_page_results, count, total_pages, total_results, extra_stats, results` (`paginator.py:727-742`). Only the stickies list defaults to 20 (`api/views/sticky.py:76`).

### 11.4 `?fields=` and `?expand=`

Comma-separated (`api/views/base.py:143-151`). `fields` drops unlisted serializer fields; `expand` inlines related objects for `user, workspace, project, default_assignee, project_lead, state, created_by, updated_by, issue, actor, owned_by, members, parent, estimate_point`. Precisely: if the name **is a serializer field and is in that expansion map** → nested object; if it is a serializer field but **not** in the map → the value is replaced by `getattr(instance, "<name>_id")`; anything that is not a serializer field is **silently ignored** (`api/serializers/base.py:76-116`). `order_by` is sanitised through allowlists per resource (`utils/order_queryset.py:19-33,37-63,101-118`).

### 11.5 Error mapping (`api/views/base.py:64-101`)

| Exception | Status | Body |
|---|---|---|
| `IntegrityError` | 400 | `{"error": "The payload is not valid"}` |
| Django `ValidationError` | 400 | `{"error": "Please provide valid detail"}` |
| `ObjectDoesNotExist` | 404 | `{"error": "The requested resource does not exist."}` on every `BaseAPIView` endpoint; the two `BaseViewSet` endpoints (stickies, invitations) answer `{"error": "The required object does not exist."}` (`api/views/base.py:85-89,199-210`) |
| `KeyError` | 400 | `{"error": "The required key does not exist."}` |
| other | 500 | `{"error": "Something went wrong please try again later"}` |
| serializer errors | 400 | `serializer.errors` |

### 11.6 Route table (`<slug>` = workspace slug; work-item routes exist twice: legacy `issues/` and new `work-items/`, `api/urls/work_item.py:156`)

| Method(s) | Path under `/api/v1/` | Notes | Cite |
|---|---|---|---|
| GET | `users/me/` | `UserLiteSerializer` of the token's user | `urls/user.py:10-14` |
| POST; PATCH/DELETE | `assets/user-assets/[<id>/]` | avatar/cover presigned POST | `urls/asset.py:14-23` |
| POST; GET/PATCH | `workspaces/<slug>/assets/[<asset_id>/]` | generic presigned upload (`name,type,size,project_id,…`); GET returns presigned `asset_url`; PATCH marks uploaded | `urls/asset.py:34-43`; `views/asset.py:405-634` |
| router | `workspaces/<slug>/invitations/` | `WorkspaceOwnerPermission`; codes `EMAIL_ALREADY_INVITED`, `INVITE_ALREADY_ACCEPTED`… | `urls/invite.py:16-22`; `views/invite.py:114-151` |
| router | `workspaces/<slug>/stickies/` | owner-scoped | `urls/sticky.py:11-16` |
| GET, POST | `workspaces/<slug>/projects/` | POST adds creator + `project_lead` as role 20 and creates default states; identifier required & unique | `urls/project.py:16-20`; `views/project.py:224-262` |
| GET | `workspaces/<slug>/projects-lite/` | `?include_archived=true` | `urls/project.py:21-25` |
| GET, PATCH, DELETE | `workspaces/<slug>/projects/<pk>/` | archived → 400; identifier taken → 409; DELETE fires webhook `deleted` | `views/project.py:546-644` |
| POST, DELETE | `…/projects/<id>/archive/` | archive / unarchive | `urls/project.py:31-35` |
| GET | `…/projects/<id>/summary/?fields=members,states,labels,cycles,modules,issues,intakes,pages` | `WorkSpaceAdminPermission` | `views/project.py:702-740` |
| GET, POST; GET/PATCH/DELETE | `…/projects/<pid>/states/[<state_id>/]` | triage excluded; cannot create group=triage; delete refuses default/non-empty | `urls/state.py:13-22`; `views/state.py:47-127,225-245` |
| GET, POST; GET/PATCH/DELETE | `…/projects/<pid>/labels/[<pk>/]` | 409 on duplicate name | `urls/label.py:11-20` |
| GET | `workspaces/<slug>/work-items/search/?search=&limit=10&project_id=` | `{"issues": [...]}` | `views/issue.py:2256-2299` |
| GET | `workspaces/<slug>/work-items/<PROJ>-<seq>/` | lookup by identifier + `sequence_id` | `views/issue.py:233-253` |
| GET, POST | `…/projects/<pid>/work-items/` | §11.7; `?pql=`/`?filters=` → 400 "not supported on this Plane edition" | `views/issue.py:256-522,315-329` |
| GET, PATCH, DELETE | `…/work-items/<pk>/` | DELETE only creator or role 20 (403 "Only admin or creator can delete the work item"); PUT handler exists but the URL allows only get/patch/delete → 405 | `views/issue.py:575-590,616-746,846-863` |
| GET, POST; GET/PATCH/DELETE | `…/work-items/<id>/links/[<pk>/]` | http(s) URL, dup → "URL already exists for this Issue"; title crawled async | `api/serializers/issue.py:391-431` |
| GET, POST; GET/PATCH/DELETE | `…/work-items/<id>/comments/[<pk>/]` | `ProjectLitePermission` (guests too); `comment_json, comment_html, access, external_*` | `views/issue.py:1360-1653` |
| GET; GET | `…/work-items/<id>/activities/[<pk>/]` | excludes `field in (comment, vote, reaction, draft)`; `order_by` created_at/updated_at | `views/issue.py:1723-1730,1795` |
| GET, POST; GET/PATCH/DELETE | `…/work-items/<id>/attachments/[<pk>/]` (legacy `issue-attachments/`) | POST requires `name`, `size` **and `type`** (`size=min(size, FILE_SIZE_LIMIT)`); a missing/unknown `type` → 400 `{"error": "Invalid file type.", "status": false}` because it must be in `settings.ATTACHMENT_MIME_TYPES`; returns presigned `upload_data`; GET detail → 302 to presigned download; PATCH marks uploaded (`views/issue.py:1907-1919`; `common.py:457-545`) | `views/issue.py:1880-1980,2111-2212` |
| GET, POST | `…/work-items/<id>/relations/` | POST `{relation_type, issues:[…]}`, types `blocking, blocked_by, duplicate, relates_to, start_before, start_after, finish_before, finish_after`; GET dict keyed by the 8 types | `api/serializers/issue.py:540-560`; `views/issue.py:2370-2588` |
| GET, POST | `…/projects/<pid>/cycles/?cycle_view=all\|current\|upcoming\|completed\|draft\|incomplete` | §11.8; `current` unpaginated | `views/cycle.py:192-300` |
| GET | `…/cycles-lite/` | non-archived | `urls/cycle.py:23-27` |
| GET, PATCH, DELETE | `…/cycles/<pk>/` | completed → only `sort_order`; archived → 400; DELETE owner/role 20 | `views/cycle.py:543-636` |
| GET, POST; GET/DELETE | `…/cycles/<id>/cycle-issues/[<issue_id>/]` | POST `{"issues":[…]}`; `MISSING_WORK_ITEMS`, `CYCLE_COMPLETED` | `views/cycle.py:966-1160` |
| POST | `…/cycles/<id>/transfer-issues/` | `new_cycle_id`; source completed, target not completed; only backlog/unstarted/started move | `views/cycle.py:1223-1250` |
| POST; GET; DELETE | `…/cycles/<id>/archive/`, `…/archived-cycles/`, `…/archived-cycles/<id>/unarchive/` | "Only completed cycles can be archived" | `views/cycle.py:787-848` |
| GET, POST | `…/projects/<pid>/modules/` | `name, description, start_date, target_date, status, lead, members, external_*`; `MODULE_NAME_ALREADY_EXISTS` | `api/serializers/module.py:36-100` |
| GET | `…/modules-lite/` | | `urls/module.py:22-26` |
| GET, PATCH, DELETE | `…/modules/<pk>/` | archived → 400; DELETE creator/role 20 | `views/module.py:452-558` |
| GET, POST; DELETE | `…/modules/<id>/module-issues/[<issue_id>/]` | POST `{"issues":[…]}` | `views/module.py:712-940` |
| POST; GET; DELETE | `…/modules/<pk>/archive/`, `…/archived-modules/`, `…/archived-modules/<pk>/unarchive/` | "Only completed or cancelled modules can be archived" | `views/module.py:1084-1125` |
| GET, POST; GET/PATCH/DELETE | `…/projects/<pid>/intake-issues/[<issue_id>/]` | POST `{"issue": {"name" (req), "description_html", "priority"}}` → Issue in Triage + `IntakeIssue`; status changes need role > 15 | `views/intake.py:143-226,342-393` |
| GET | `workspaces/<slug>/members/`, `members-lite/` | `WorkSpaceAdminPermission` | `urls/member.py:42-51` |
| GET, POST; GET/PATCH/DELETE | `…/projects/<pid>/members/[<pk>/]` (alias `project-members/`), `project-members-lite/` | POST `ProjectAdminPermission`, `{member, role∈{20,15,5}}`, member must already be a workspace member; DELETE sets `is_active=False` | `views/member.py:102-232`; `api/serializers/member.py:15-43` |

NOT mounted in v1: `api/urls/estimate.py` (3 routes) and `api/urls/schema.py` are not imported by `api/urls/__init__.py:5-31`. NOT FOUND: work-item **types** CRUD (only `type_id` on create/patch), pages, views, webhooks, tokens.

### 11.7 Create work item — `POST …/projects/<pid>/work-items/` contract

- Serializer `IssueSerializer` with context `project_id, workspace_id, default_assignee_id` (`views/issue.py:449-458`). Read-only: `id, workspace, project, updated_by, updated_at, completed_at`; `description_json`/`description_stripped` excluded (`api/serializers/issue.py:70-73`).
- Writable: `name` (**required**, ≤255), `description_html`, `description_binary`, `priority` (`urgent|high|medium|low|none`, default `none`), `start_date`, `target_date` (YYYY-MM-DD), `state`, `parent`, `estimate_point`, `assignees` (list of user ids), `labels` (list), `type_id`, `external_id`, `external_source`, `sort_order`, `is_draft`.
- Because `IssueSerializer` uses `Meta.exclude` (not an allowlist), **every other non-read-only model field is writable too**: `point` (legacy 0–12), `sequence_id`, `archived_at` and `deleted_at` (`api/serializers/issue.py:70-73`; `db/models/issue.py:128,156,160`; `db/mixins.py:64`). Writing `sequence_id` corrupts the `PROJ-123` identifier; writing `deleted_at`/`archived_at` hides the item.
- `created_at` and `created_by` are **not** serializer-writable (auto_now_add / audit fields) — the *view* copies them straight from the raw request body after `save()`: `issue.created_at = request.data.get("created_at", now)`, `issue.created_by_id = request.data.get("created_by", request.user.id)` (`api/views/issue.py:493-496`, same on PATCH). Any token holder can therefore attribute a work item to an arbitrary user and timestamp, and activity/notifications follow that attribution. Course labs should warn against sending these fields.
- Validation (`serializers/issue.py:75-149`): `start_date > target_date` → "Start date cannot exceed target date"; invalid HTML → "Invalid HTML passed"; `assignees` silently filtered to active project members with **role ≥ 15**; `labels` filtered to project; `state` must belong to project ("State is not valid please pass a valid state_id"); `parent` same project; `estimate_point` in project.
- Defaults: no `state` → project default (non-triage) state (`db/models/issue.py:228-236`); no assignees → project `default_assignee` if active member role ≥ 15 (`serializers/issue.py:190-207`); `sequence_id` allocated under the advisory lock.
- `external_id`+`external_source` already present → **409** `{"error": "Issue with the same external id and external source already exists", "id": "<existing>"}` (same on PATCH) (`views/issue.py:466-489,787-804`).
- After save: fires `issue_activity` (`issue.activity.created`) and `model_activity` for webhooks (`:499-520`). Response is the serialised issue (201).

### 11.8 Create cycle — `POST …/projects/<pid>/cycles/` contract

- Pre-check: `start_date` and `end_date` **both set or both null** → else 400 "Both start date and end date are either required or are to be null" (`views/cycle.py:301-357`).
- `CycleCreateSerializer` fields `name, description, start_date, end_date, owned_by, external_source, external_id, timezone` (`api/serializers/cycle.py:38-49`); `validate`: project must exist with `cycle_view=True` ("Cycles are not enabled for this project"); `start > end` → "Start date cannot exceed end date"; date-only values converted to UTC in the project timezone; `owned_by` defaults to caller (`:61-97`).
- External-id conflict → 409 `{"error": "Cycle with the same external id and external source already exists", "id": "<existing>"}` (`views/cycle.py:314-336`); **PATCH raises the same 409** when the new `external_id` collides (`:575-591`) — useful for writing idempotent import scripts. Response: full `CycleSerializer` incl. `total_issues, completed_issues, cancelled_issues, started_issues, unstarted_issues, backlog_issues, total_estimates, completed_estimates, started_estimates` (`api/serializers/cycle.py:123-131`).

### 11.9 API activity log

`APITokenLogMiddleware` (global, `common.py:133`) records **every request carrying `X-Api-Key`** regardless of path (`middleware/logger.py:131-136`): `token_identifier` = HMAC-SHA256(`SECRET_KEY`, key) — raw key never stored (`:144-146`); `path, method, query_params`; `headers` with `x-api-key`, `authorization`, `cookie` redacted (`:117-128`); request `body` and `response_body` (binary replaced by `"[Binary Content]"`, `:107-114`); `response_code`; `ip_address` (first `X-Forwarded-For` hop); `user_agent`. Persisted asynchronously by Celery `process_logs` (`bgtasks/logger_task.py:32-41`) into `api_activity_logs`; purged after `API_ACTIVITY_LOG_RETENTION_DAYS` (default 14) daily at 02:30 UTC (`common.py:445`; `celery.py:71-74`). No UI shows this table.

### 11.10 OpenAPI

Opt-in with `ENABLE_DRF_SPECTACULAR=1` → `/api/schema/`, `/api/schema/swagger-ui/`, `/api/schema/redoc/` (`common.py:565-570`; `urls.py:27-40`). Schema keeps only `/api/v1/` paths, drops PUT and paths containing "server"; title "The Plane REST API", servers `http://localhost:8000` and `https://api.plane.so` (`utils/openapi/hooks.py:14-23`; `settings/openapi.py:35,46-49`). Contract tests live in `apps/api/plane/tests/contract/api/`.

---

## 12. Webhooks

### 12.1 Model & management

`Webhook` (§4.15): `url` ≤1024, http/https only; `secret_key` `plane_wh_<hex>`; flags `project, issue, module, cycle, issue_comment`. The model's `validate_domain` compares `urlparse(url).netloc` — host **and** port — against `["localhost","127.0.0.1"]`, so it blocks only the bare hostnames; `http://localhost:8080/…` passes it and is instead stopped by the SSRF loopback check (§12.2), which in turn can be lifted by adding `127.0.0.1/32` to `WEBHOOK_ALLOWED_IPS` — bare `localhost` stays rejected by the model validator either way (`db/models/webhook.py:27-31`; `utils/ip_address.py:78-96,151-152`). Uniqueness `(workspace, url)` is a **partial constraint on `deleted_at IS NULL`**, so a soft-deleted webhook's URL can be re-registered immediately and the old row is purged only by the 60-day hard delete (`db/models/webhook.py:56-62`).
**The secret is readable**: `WebhookSerializer` is `fields = "__all__"` with `secret_key` merely *read-only*, so `GET /api/workspaces/<slug>/webhooks/<pk>/` returns the current secret to any workspace Admin; `POST …/regenerate/` is the only way to rotate it (`app/serializers/webhook.py:68-71`). Management is **workspace Admin only** in the session API: `GET/POST /api/workspaces/<slug>/webhooks/`, `GET/PATCH/DELETE …/<pk>/`, `POST …/<pk>/regenerate/`, `GET …/webhook-logs/<webhook_id>/` (`app/urls/webhook.py:15-30`; `app/views/webhook/base.py:21,38,78,104,112,122`); duplicate URL → 409. UI: Workspace settings → Webhooks (URL, active toggle, secret, events `all|individual` with `project, cycle, issue ("Work items"), module, issue_comment`) (`packages/types/src/webhook.ts:7-21`; `web-hooks/form/individual-event-options.tsx:18-39`). NOT FOUND: any `/api/v1/` webhook route; any use of `ProjectWebhook`.

### 12.2 SSRF guard and allowed hosts

Settings (`common.py:56-91`): `WEBHOOK_ALLOWED_IPS` (CIDRs, `ip_network(strict=False)`), `WEBHOOK_ALLOWED_HOSTS` (hostnames that bypass the private-IP check — the comment cites "Silo", an integration service not in this repo), `WEBHOOK_DISALLOWED_DOMAINS`.
At create/update (`app/serializers/webhook.py:27-55`): `validate_url(url, allowed_ips, allowed_hosts)` → `{"url": "Invalid or disallowed webhook URL."}`; hosts in `WEBHOOK_ALLOWED_HOSTS` skip the disallowed-domain check; otherwise the **request's own host is appended** to the disallowed list, and any match/subdomain → `{"url": "URL domain or its subdomain is not allowed."}`.
`validate_url` (`utils/ip_address.py:159-196`): requires hostname + http/https; resolves via `getaddrinfo` and raises "Access to private/internal networks is not allowed" when any resolved IP is blocked and not in `allowed_ips`. Blocked: private/loopback/reserved/link-local/multicast/unspecified plus `0.0.0.0/8, 100.64.0.0/10, 169.254.0.0/16, 255.255.255.255/32, ::ffff:0:0/96, 64:ff9b::/96, 64:ff9b:1::/48, 2002::/16, 2001::/32, fec0::/10`, recursing into IPv4-embedded IPv6 (`:16-64`).
At delivery, `pinned_fetch` resolves once, validates, connects to the IP literal with the original hostname for Host/SNI, `allow_redirects=False`, `trust_env=False`, no proxies, timeout 30 s (`utils/url_security.py:103-222`; `bgtasks/webhook_task.py:317-325`). **Lab implication**: a webhook receiver on the same Docker network or on a private LAN IP is rejected unless its IP/CIDR is in `WEBHOOK_ALLOWED_IPS` or its hostname in `WEBHOOK_ALLOWED_HOSTS` (both forwarded by compose — `deployments/cli/community/docker-compose.yml:61-62`, **not** the root developer `docker-compose.yml`, whose lines 61-62 are `env_file` entries).

### 12.3 Events and payload

`model_activity` diffs `requested_data` vs `current_instance` and emits one `updated` event **per changed key** (`created` when no current instance) (`webhook_task.py:479-520`); `webhook_activity` selects active webhooks by flag: `project`, `issue`, `module` (also `module_issue`), `cycle` (also `cycle_issue`), `issue_comment` (`:433-448`). Call sites: app views for issue/cycle/module/project/comment and v1 issue create/update, comment create/update, cycle create/update, module create/update, project create/update/delete (`api/views/issue.py:512,819,1501,1640`; `cycle.py:339,595`; `module.py:231,489`; `project.py:291,585,633`). **v1 cycle-issue/module-issue add/remove and work-item delete do not emit webhooks** (`issue_activities_task` never references webhooks). Counting the entry points: 22 `model_activity.delay` sites plus 2 direct `webhook_activity.delay` sites for project delete (`app/views/project/base.py:400-402`; `api/views/project.py:633-635`).

Request headers: `Content-Type: application/json`, `User-Agent: Autopilot`, `X-Plane-Delivery: <uuid4>`, `X-Plane-Event: <event>`, **`X-Plane-Signature`** = hex HMAC-SHA256 of `json.dumps(payload)` keyed with `webhook.secret_key` (only when secret set) (`webhook_task.py:267-304`).

Payload:
```json
{"event": "issue", "action": "created|updated|deleted", "webhook_id": "...", "workspace_id": "...", "workspace_slug": "...",
 "data": { serialized model (IssueExpandSerializer with labels+assignees, CycleSerializer, ModuleSerializer, ProjectSerializer, IssueCommentSerializer, …) or {"id": …} on delete },
 "activity": {"field", "new_value", "old_value", "actor": {UserLite}, "old_identifier", "new_identifier"}}
```
(`webhook_task.py:58-68,286-294,455-465`). **`action` is the past-tense verb `"created"` / `"updated"` / `"deleted"`**: `webhook_activity` is always called with `verb=` one of those strings (`model_activity` at `:482-484,507-509`, project delete at `app/views/project/base.py:402` and `api/views/project.py:633-635`), and the `POST→create / PATCH,PUT→update / DELETE→delete` lookup at `webhook_task.py:279-284` never matches them, so it is dead code for every current caller and the verb passes through unchanged.

### 12.4 Retry, logging, deactivation

`webhook_send_task` is `bind=True, autoretry_for=(requests.RequestException,), retry_backoff=600, max_retries=5, retry_jitter=True` (`webhook_task.py:235-241`) — retries fire **only on transport exceptions; non-2xx HTTP responses are not retried**. The backoff is **not exponential**: `retry_backoff=600` is capped by Celery's default `retry_backoff_max=600`, so `min(600, 600·2ⁿ) = 600` for every retry, and `retry_jitter=True` then turns each wait into a uniformly random 0–600 s (`celery==5.5.3`, `apps/api/requirements/base.txt:18`) — worst case ≈50 minutes across the 5 retries. Every attempt is written to `WebhookLog` with `retry_count` (`:328-353`). Deactivation triggers when `self.request.retries >= max_retries`, i.e. on the **6th consecutive failed attempt** (initial + 5 retries): the webhook is set `is_active=False` and a "Webhook Deactivated" email goes to its creator (`:355-365`). Without SMTP that email — like every transactional mail — silently no-ops (`send_webhook_deactivation_email` swallows all exceptions, `:230-232`), so students must check the Webhooks settings page / `WebhookLog` rather than wait for mail; the webhook is deactivated either way. SSRF rejection (`ValueError`) is logged with status 400, not retried and does not deactivate (`:368-385`). Logs are purged after `WEBHOOK_LOG_RETENTION_DAYS` (14) at 03:30 UTC (`common.py:449`; `celery.py:87-90`).

---

## 13. Background services

### 13.1 Celery configuration

- App `plane`, config from Django settings namespace `CELERY`, `autodiscover_tasks()` + explicit `CELERY_IMPORTS` (issue_automation_task, exporter_expired_task, file_asset_task, email_notification_task, cleanup_task, `plane.license.bgtasks.telemetry_metrics`, dummy_data_task, issue_version_sync, issue_description_version_sync) (`apps/api/plane/celery.py:38-42,116`; `common.py:338-351`). Versions: celery 5.5.3, django_celery_beat 2.9.0 (`apps/api/requirements/base.txt:18-19`; django-celery-results 2.6.0 is installed at `:20` but unused).
- Broker: `AMQP_URL` or `amqp://{RABBITMQ_USER}:{PASSWORD}@{HOST}:{PORT}/{VHOST}` (defaults guest/guest@localhost:5672//) (`common.py:318-330`); CE compose → `amqp://plane:plane@plane-mq:5672/plane`.
- JSON-only serialisation; `CELERY_TIMEZONE = "UTC"` (`common.py:291,332-335`).
- **No result backend** (`CELERY_RESULT_BACKEND` absent; django-celery-results installed but not in `INSTALLED_APPS`) — results are discarded. **No custom queues/exchanges/routing**; worker starts without `-Q`, so everything goes to the default `celery` queue. **No `CELERY_TASK_ALWAYS_EAGER`** fallback (grep of `plane/settings`).
- Beat scheduler: `django_celery_beat.schedulers.DatabaseScheduler` (`celery.py:118`) — schedule state lives in Postgres, seeded from `app.conf.beat_schedule` into the `django_celery_beat_periodictask` table, and it **survives restarts**: editing `celery.py` alone does not remove an entry that has already been seeded (e.g. the duplicate `delete_old_s3_link`) — you have to delete the row. Missed crontab runs are not replayed (`celery.py:44-95,118`).
- A Redis client is created at import time (`ri = redis_instance()`, `celery.py:22`) — worker and beat need `REDIS_URL` to boot.

### 13.2 Beat schedule (all UTC, `celery.py:44-95`)

| Task | Schedule | Purpose |
|---|---|---|
| `email_notification_task.stack_email_notification` | every 5 min | group unsent `EmailNotificationLog` rows and dispatch emails |
| `license.bgtasks.telemetry_metrics.push_instance_metrics` | every `METRICS_PUSH_INTERVAL_MINUTES` (default 360) | OTLP telemetry to `https://telemetry.plane.so` unless disabled |
| `deletion_task.hard_delete` | 00:00 | purge soft-deleted rows older than `HARD_DELETE_AFTER_DAYS` (60) |
| `issue_automation_task.archive_and_close_old_issues` | 01:00 | project auto-archive / auto-close |
| `exporter_expired_task.delete_old_s3_link` | 01:30 **and again 03:45** (duplicate entry) | delete export zips older than 8 days |
| `file_asset_task.delete_unuploaded_file_asset` | 02:00 | drop `FileAsset` rows never uploaded after `UNUPLOADED_ASSET_DELETE_DAYS` (7) |
| `cleanup_task.delete_api_logs` | 02:30 | `API_ACTIVITY_LOG_RETENTION_DAYS` (14) |
| `cleanup_task.delete_email_notification_logs` | 02:45 | `EMAIL_LOG_RETENTION_DAYS` (7) |
| `cleanup_task.delete_page_versions` | 03:00 | keep newest 20 per page |
| `cleanup_task.delete_issue_description_versions` | 03:15 | keep newest 20 per issue |
| `cleanup_task.delete_webhook_logs` | 03:30 | `WEBHOOK_LOG_RETENTION_DAYS` (14) |

### 13.3 Task catalogue (`apps/api/plane/bgtasks/`, `@shared_task`)

| Task | Triggered by | What it does | Evidence |
|---|---|---|---|
| `issue_activity(type, requested_data, current_instance, issue_id, actor_id, project_id, epoch, subscriber, notification, origin, intake)` | 78 `.delay` call sites in app/api/space views + automation | stores request origin in Redis key `str(issue_id)` TTL 600 s; bumps `issue.updated_at`; dispatches to `ACTIVITY_MAPPER` (**27** types: issue ×3, comment ×3, cycle ×2, module ×2, link ×3, attachment ×2, issue_relation ×2, issue_reaction ×2, comment_reaction ×2, issue_vote ×2, issue_draft ×3, intake ×1, `:1540-1567`); `IssueActivity.bulk_create`; chains `notifications.delay` when `notification=True` | `issue_activities_task.py:1503-1604` |
| `notifications(...)` | only from `issue_activity` | skips cycle/module/reaction/vote/draft types; computes mentions; subscribes actor; per subscriber applies `UserNotificationPreference` (`state_change, issue_completed, comment, property_change, mention`), skips description changes; bulk-creates `Notification` + `EmailNotificationLog` | `notification_task.py:190-670` |
| `stack_email_notification()` | beat /5 min | groups unprocessed logs by receiver→issue, fires `send_email_notification.delay` per pair, marks `processed_at` (even if the send later fails) | `email_notification_task.py:46-84` |
| `send_email_notification(...)` | above | Redis lock `send_email_notif_{issue}_{receiver}_{ids}` (`SET NX EX 300`); reads origin from Redis key `str(issue_id)` and **silently returns if expired**; renders `emails/notifications/issue-updates.html`; SMTP send; `sent_at` | `email_notification_task.py:152-290` |
| `model_activity` → `webhook_activity` → `webhook_send_task` → `send_webhook_deactivation_email` | **22** `model_activity.delay` call sites **+ 2** direct `webhook_activity.delay` sites (project delete, app and v1) = 24 entry points | §12 | `webhook_task.py:171-521`; `app/views/project/base.py:400`; `api/views/project.py:633` |
| `issue_export_task(provider, workspace_id, project_ids, token_id, multiple, slug)` | `ExportIssuesEndpoint.post` | §10.5 | `export_task.py:127-226` |
| `delete_old_s3_link()` | beat | delete export objects >8 days, null `url` | `exporter_expired_task.py:22-53` |
| `analytic_export_task(email, data, slug)` | `export-analytics/` | CSV by e-mail | `analytic_plot_export.py:349-406` |
| `magic_link(email, key, token)` | magic-generate view | "Your unique Plane login code is {token}" via SMTP; failures swallowed | `magic_link_code_task.py:22-64` |
| `forgot_password(...)` | forgot-password view | reset link `/accounts/reset-password/?uidb64=&token=&email=` | `forgot_password_task.py:22-25` |
| `workspace_invitation(email, workspace_id, token, current_site, inviter)` | workspace invite view | invitation email; **any exception logged and swallowed** | `workspace_invitation_task.py:22-89` |
| `project_invitation(...)` | **never reached** — see bug §13.8 | | `project_invitation_task.py:23-43` |
| `project_add_user_email`, `user_activation_email`, `user_deactivation_email`, `send_email_update_magic_code`, `send_email_update_confirmation` | member/admin/user flows | transactional emails | respective `*_task.py` |
| `hard_delete()` | beat 00:00 | physical delete of soft-deleted rows for 18 named models then every model with `deleted_at` | `deletion_task.py:113-191` |
| `soft_delete_related_objects(app_label, model_name, pk)` | every `SoftDeleteModel.delete()` | cascades `deleted_at` through reverse relations | `deletion_task.py:17-105`; `mixins.py:72-78` |
| `delete_api_logs`, `delete_email_notification_logs`, `delete_page_versions`, `delete_issue_description_versions`, `delete_webhook_logs` | beat | retention (batches of 500; version trims keep newest 20) | `cleanup_task.py:31,85-202` |
| `delete_unuploaded_file_asset()` | beat 02:00 | `is_uploaded=False` older than 7 days | `file_asset_task.py:20-26` |
| `archive_and_close_old_issues()` | beat 01:00 | §5.4 | `issue_automation_task.py:22-149` |
| `track_page_version(page_id, existing_instance, user_id)` | page description PATCH | new/updated `PageVersion` (600 s window), trim to 20 | `page_version_task.py:19-74` |
| `page_transaction(new_html, old_html, page_id)` | page views | parses mention/image components → `PageLog` rows | `page_transaction_task.py:84-136` |
| `issue_description_version_task(...)` | issue/intake description updates | `IssueDescriptionVersion` (600 s window) | `issue_description_version_task.py:43-66` |
| `sync_issue_version` / `sync_issue_description_version` | `manage.py sync_issue_version` / `…_description_version` | back-fill in 5000-row batches, `apply_async(countdown=300)` | `issue_version_sync.py:180-236`; `issue_description_version_sync.py:39-125` |
| `get_asset_object_metadata(asset_id)` | after upload-complete (10 sites) | HEAD object → `FileAsset.storage_metadata` | `storage_metadata_task.py:14-24` |
| `copy_s3_objects_of_description_and_assets(...)` | page duplicate | copies image assets, rewrites HTML, POSTs to live `/convert-document/` for json+binary | `copy_s3_object.py:67-150` |
| `crawl_work_item_link_title(id, url)` | link create/update | SSRF-checked fetch of title + favicon → `IssueLink.metadata` | `work_item_link_task.py:29-60,248-259` |
| `recent_visited_task(...)` | retrieve views (10 sites) | upsert `UserRecentVisit`, cap 20 per user/workspace | `recent_visited_task.py:17-56` |
| `process_logs(log_data)` | `APITokenLogMiddleware` | writes `APIActivityLog` | `logger_task.py:32-41` |
| `track_event(...)` | workspace create/invite/join | PostHog only if `POSTHOG_API_KEY`+`POSTHOG_HOST` | `event_tracking_task.py:24-67` |
| `workspace_seed(workspace_id)` | workspace create | creates a bot user (`bot_type=WORKSPACE_SEED`) and seeds projects/states/labels/cycles/modules/issues/views/pages from `apps/api/plane/seeds/data/*.json` | `workspace_seed_task.py:504-571`; `app/views/workspace/base.py:139` |
| `create_dummy_data(...)` | `manage.py create_dummy_data` | demo project | `dummy_data_task.py:487-497` |
| `push_instance_metrics()` | beat + `register_instance` on every API boot | OTLP gauges (users, workspaces, projects, issues, modules, cycles, pages, per-workspace up to 1000) to `OTLP_ENDPOINT`; skipped when `is_telemetry_enabled` False | `license/bgtasks/telemetry_metrics.py:74-95,368-381`; `utils/otlp_endpoints.py:19,52` |
| Dead tasks | `issue_task` (IssueVersion tracking) and `export_analytics_to_csv_email` have **no callers** | | grep |

### 13.4 Roles of RabbitMQ and Redis/Valkey

| Backing service | Used for | Evidence |
|---|---|---|
| RabbitMQ (`plane-mq`) | Celery broker only; durable messages in `rabbitmq_data` buffer all `.delay()` calls while no worker runs; management plugin present but 15672 not published | `docker-compose.yml:195-204`; `common.py:327-330` |
| Valkey (`plane-redis`) | Django cache (`django_redis`, only `CACHES` backend); `@cache_response`/`@invalidate_cache` view cache (e.g. `GET /api/instances/` cached 2 h); start-up `cache.clear()`; DRF throttle counters (anon 30/min, api_key 60/min, authentication 10/min, email_verification 3/h, asset_id 5/min); magic-code storage `magic_{email}` TTL 600 s with `MAX_VERIFY_ATTEMPTS=5`; issue-origin key for emails (600 s); email dedupe lock; live-server Hocuspocus pub/sub + admin channel `hocuspocus:admin` | `common.py:140-144,241-263`; `utils/cache.py:25-69`; `magic_code.py:28,75-119`; `issue_activities_task.py:1527-1531`; `apps/live/src/extensions/redis.ts:16-102` |
| PostgreSQL (`plane-db`) | all models, **sessions** (`SESSION_ENGINE = "plane.db.models.session"`, table `sessions`), django_celery_beat schedule tables; `max_connections=1000` | `common.py:376`; `session.py:17-56`; `docker-compose.yml:176` |
| MinIO/S3 (`plane-minio`) | uploads (`FileAsset`), export zips, avatars; bucket `uploads` | `storage.py`; `export_task.py:42-124` |

**Sessions are NOT in Redis** — a Redis flush does not log users out; it clears caches, throttle counters, pending magic codes and the email-origin keys.

### 13.5 Live server (`apps/live`)

- Express + express-ws + helmet + compression + Hocuspocus (Yjs) with `@hocuspocus/extension-database`, `extension-redis`, `extension-logger`; ioredis; react-pdf (`apps/live/package.json:29-63`). Router at `LIVE_BASE_PATH` (default `/live`), port `PORT` (default 3000) (`src/server.ts:33-40,95-99`). Start order: Redis → Hocuspocus → controllers (`server.ts:42-55`). Env is zod-validated; invalid → `process.exit(1)` (`src/env.ts:13-40`). **Hard requirements**: `LIVE_SERVER_SECRET_KEY` (a bare `z.string()`, `:26`) and a syntactically valid `API_BASE_URL` (`:17`) — without either the container crash-loops, even though the secret is never actually enforced on a route. `CORS_ALLOWED_ORIGINS` defaults to `""` and `APP_VERSION` to `"1.0.0"` (`:14,19`), and the compose `live` service is given **no CORS value at all** (`docker-compose.yml:45-47,98-99`).
- Routes: `WS /live/collaboration/` (Hocuspocus), `POST /live/convert-document/` (**unauthenticated**; HTML → `{description_json, description_binary}`; used by the worker's copy task), `GET /live/health/` → `{status:"OK", timestamp, version}`, `POST /live/pdf-export/` (cookie required) (`src/controllers/*.ts`). `requireSecretKey` (header `live-server-secret-key` vs `LIVE_SERVER_SECRET_KEY`) is defined but **applied to no route** (`src/lib/auth-middleware.ts:35-56`).
- Auth handshake: provider token = `JSON.stringify({id, name, color, cookie?})`; `onAuthenticate` takes `id` + `cookie` (fallback: WS request Cookie header) and calls `GET {API_BASE_URL}/api/users/me/` requiring `user.id === id` (`src/lib/auth.ts:24-96`; `src/services/user.service.ts:25-38`). There is no shared secret in the handshake — it replays the browser's Django session cookie.
- Persistence via the Django API with the user's cookie: `GET/PATCH …/pages/{id}/description/`; store debounce 10 s; 413 → broadcast `content_too_large` and force-close across replicas (`src/extensions/database.ts:26-130`; `src/hocuspocus.ts:45-51`). `TitleSyncExtension` PATCHes `name` with 5 s debounce.
- Redis: `RedisManager` connects to `REDIS_URL` or `redis://REDIS_HOST:REDIS_PORT`; without either it logs a warning, but the always-registered `Redis` extension throws "Redis client not initialized" → **Redis is effectively mandatory** (`src/redis.ts:42-66`; `src/extensions/redis.ts:16-30`; `src/extensions/index.ts:13-19`).
- Only `documentType === "project_page"` is handled in CE (`src/types/index.ts:26`; `src/services/page/handler.ts:12-21`).

### 13.6 Email (SMTP) path

Tasks never use Django's global `EMAIL_HOST`; each builds `get_connection(host, port, username, password, use_tls=EMAIL_USE_TLS=="1", use_ssl=EMAIL_USE_SSL=="1")` from `get_email_configuration()` (`license/utils/instance_value.py:42-59`), which reads `InstanceConfiguration` rows (`SKIP_ENV_VAR=1`) with fallbacks `EMAIL_PORT 587`, `EMAIL_USE_TLS 1`, `EMAIL_FROM "Team Plane <team@mailer.plane.so>"`. God-mode "Send test email" (`POST /api/instances/email-credentials-check/`) is **synchronous** (no Celery) and maps SMTP exceptions to messages (`license/api/views/configuration.py:88-171`); CLI `python manage.py test_email <receiver@example.com>` — `to_email` is a **positional** argument, not an option (`db/management/commands/test_email.py:17-22`). `local.py` uses the console backend (`settings/local.py:20`).

### 13.7 Failure modes — what breaks when X is down

| Component down | Effect |
|---|---|
| **worker** (broker up) | Views still return immediately; messages queue in RabbitMQ (`rabbitmq_data`). Delayed until a worker returns: activity rows and in-app notifications (activities are written **only** by the task), all emails incl. **magic-link codes**, invitations, password resets, webhooks, exports (`ExporterHistory` stays `queued`), page/issue version snapshots, `PageLog`, recent visits, link metadata, storage metadata, API activity logs, **soft-delete cascades**, **workspace seeding** (new workspace stays empty). Not affected: login (DB sessions), password sign-in, CRUD, cache reads, magic-code *generation* (Redis, synchronous). **Beat keeps running** — it is a separate container (`beat-worker`, `apps/api/bin/docker-entrypoint-beat.sh:1-8`) independent of the worker (`docker-entrypoint-worker.sh:1-8`) — so its crontab messages pile up in RabbitMQ and all execute in one burst when a worker returns. Nothing is lost, but email-origin Redis keys expire after 600 s, so backlog emails older than 10 min are dropped by `send_email_notification` (`email_notification_task.py:163-168`) |
| **RabbitMQ** | `.delay()` raises inside the request; **the API container fails to boot** because `register_instance` calls `push_instance_metrics.delay()` under `set -e` (`register_instance.py:89-90`; `docker-entrypoint-api.sh:2,24`) |
| **Redis/Valkey** | API and worker cannot boot (`redis_instance()` at import; `cache.clear()` at api start); throttles, view cache, magic codes, email locks fail; live server's Redis extension throws. Sessions survive (DB) |
| **Postgres** | everything. Note the entrypoints do **not** block in `wait_for_db` (a no-op, §2.3): `wait_for_migrations` raises, `set -e` kills the container and it crash-loops under `restart_policy: any` until the DB is back |
| **live** | Pages editor cannot connect (syncing/offline badge); page duplication's format conversion is skipped when `LIVE_URL` unset; everything else works |
| **MinIO** | uploads/downloads/avatars/exports fail. `create_bucket` does **not** stop the api: it wraps everything in `except ClientError` plus a final `except Exception` that only prints `"An error occurred: …"`, so `set -e` is never triggered and the container boots on without a bucket (`db/management/commands/create_bucket.py:19-61`; `docker-entrypoint-api.sh:30`) |
| **proxy** | nothing is reachable from outside (only published ports) |

### 13.8 Verified bugs / gotchas in v1.4.2

1. **Project invitation emails cannot send**: `ProjectInvitationsViewset.create` calls `.role` on a `WorkspaceMember` *QuerySet* (`app/views/project/invite.py:65-67`), rebinds `project_invitations` to the `bulk_create` list and calls `.delay(...)` on it (`:101-114`); no email task is imported. The web app instead adds existing workspace members via `POST …/projects/<id>/members/` (`apps/web/core/services/project/project-member.service.ts:31`).
2. `delete_old_s3_link` scheduled twice (`celery.py:63-66,91-94`).
3. `hard_delete` comment says 30 days; setting default is 60 (`deletion_task.py:190`; `common.py:424`).
4. `stack_email_notification` marks logs processed even if the send later fails — no retry (`email_notification_task.py:84,292-296`).
5. `POST /live/convert-document/` is unauthenticated while `requireSecretKey` is unused.
6. OpenAPI pagination doc (20/100) contradicts code (1000/1000).
7. `GUNICORN_WORKERS`, `TRUSTED_PROXIES`, `AUTHENTICATION_RATE_LIMIT` in `plane.env` are ineffective with the release compose (§3.1); `PULL_POLICY` and `DOCKERHUB_USER` are written to `plane.env` and never read (§2.1).
8. Local build images (`myplane/…:local`) do not match the compose image names (`makeplane/…`).
9. `manage.py wait_for_db` never waits — `connections["default"]` opens no socket, so the loop exits immediately (§2.3).
10. A completed cycle can be fully edited as long as the PATCH body also carries `sort_order`: the sanitised `request_data` is computed and then discarded (§6.1).
11. Archiving a **draft** cycle raises `TypeError` (`None >= datetime`) → HTTP 500 instead of the intended 400 (§6.1).
12. Auto-close falls back to `State.objects.filter(group="cancelled").first()` **without a project filter** — it can move work items into another project's cancelled state (§5.4).
13. The v1 work-item create/patch view copies `created_at`/`created_by` from the raw request body, letting any token holder forge the creator and creation time; `sequence_id`, `archived_at` and `deleted_at` are writable too (§11.7).
14. `webhook_send_task`'s `POST→create / PATCH→update / DELETE→delete` mapping is dead code — callers pass `"created"`/`"updated"`/`"deleted"` (§12.3). Its `retry_backoff=600` is capped at 600 s, so "exponential backoff" never happens (§12.4).
15. The cycle/module analytics day series returns `count = created + completed`, double-counting completed items (§10.2).
16. `/api/v1/` stickies and invitations bypass the API-key throttle and emit no `X-RateLimit-*` headers (§11.2); 429 responses never carry those headers either.

---

## 14. Authentication & instance admin

### 14.1 Endpoints

`/auth/` (`apps/api/plane/authentication/urls.py`): `sign-in/` (:51), `sign-up/` (:52), `sign-out/` (:56), `get-csrf-token/` (:59), `magic-generate/` (:61), `magic-sign-in/` (:62), `magic-sign-up/` (:63), `google/` + `google/callback/` (:80-81), `github/` (:93-94), `gitlab/` (:106-107), `gitea/` (:141-142), `email-check/` (:119), `forgot-password/` (:122), `reset-password/<uidb64>/<token>/` (:124), `change-password/` (:138), `set-password/` (:139). Every route **except `change-password/` and `set-password/`** has a `spaces/…` twin for the public Space app (`authentication/urls.py:51-151`).
`/api/instances/` (`license/urls.py:23-74`): `""` (instance), `admins/`, `admins/me/`, `admins/session/`, `admins/sign-out/`, `admins/<pk>/`, `configurations/`, `configurations/disable-email-feature/`, `admins/sign-in/`, `admins/sign-up/`, `admins/sign-up-screen-visited/`, `email-credentials-check/`, `workspace-slug-check/`, `workspaces/`.

### 14.2 Sessions, cookies, CSRF, throttles

- DRF defaults: `SessionAuthentication`, `IsAuthenticated`, `AnonRateThrottle` anon `30/minute` + `asset_id 5/minute`, JSON renderer, custom `auth_exception_handler` (`NotAuthenticated`→401, `Throttled`→429 `RATE_LIMIT_EXCEEDED`) (`common.py:138-151`; `authentication/adapter/exception.py:17-34`).
- Web cookie `session-id`, **7 days** (`SESSION_COOKIE_AGE=604800`), HttpOnly, `Secure` only when every `CORS_ALLOWED_ORIGINS` entry is https; DB session engine (`common.py:374-380`). God-mode uses a separate `admin-session-id` cookie, **1 hour**, selected by the custom `SessionMiddleware` whenever `"instances"` is in the path (`common.py:383-384`; `authentication/middleware/session.py:22-27,43-44,62-66`). `user_login()` stores `device_info` (UA, IP, domain) (`authentication/utils/login.py:14-28`).
- CSRF: REST views skip it (`BaseSessionAuthentication.enforce_csrf` no-op, `authentication/session.py:8-11`); the form-POST auth views (sign-in, magic, OAuth, admin sign-in) require `csrfmiddlewaretoken` fetched from `/auth/get-csrf-token/` (`packages/services/src/auth/auth.service.ts:33-34`). `CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS` (`common.py:389`).
- Throttles: `AuthenticationThrottle` (scope `authentication`) = `AUTHENTICATION_RATE_LIMIT` (default `10/minute` per anonymous IP) on email-check, magic-generate, forgot-password, magic sign-in/up (and `TimezoneEndpoint`); the magic sign-in/up views are plain Django views, so they call `authentication_throttle_allows()` by hand (`authentication/rate_limit.py:20-24,36-49`; `views/app/magic.py:39,71,154`). `EmailVerificationThrottle` (scope `email_verification`) `3/hour` per user (`rate_limit.py:52-59`). DRF defaults add scope `anon` `30/minute` and `asset_id` `5/minute` (`common.py:140-144`). Combined with the 4-codes-per-10-minutes budget below, this per-IP limit is what students hit when they re-request codes during a lab — and, per §2.4, it is spoofable via `X-Forwarded-For`.
- `PASSWORD_RESET_TIMEOUT = 3600` (`common.py:274`).

### 14.3 Flows

**Email check** (`POST /auth/email-check/`, `views/app/check.py`): requires `instance.is_setup_done` else `INSTANCE_NOT_CONFIGURED` (:37-42). Existing user → `status="MAGIC_CODE"` only if `user.is_password_autoset and SMTP configured and magic enabled`, else `"CREDENTIAL"`; new user → `MAGIC_CODE` if SMTP configured and magic enabled, else `CREDENTIAL` (:84-103). The web form only requests a code when `config.is_smtp_configured` (`auth-forms/form-root.tsx:50,92-93`); with no OAuth and neither password nor magic enabled it shows "No authentication methods available" (`auth-root.tsx:54-55,105-113`).

**Shared adapter pipeline** `complete_login_or_signup()` (`authentication/adapter/base.py:310-409`): sanitise email → reject deactivated (`not is_active and last_logout_time`) and bot users → if new: `__check_signup` (`ENABLE_SIGNUP == "0"` and no pending `WorkspaceMemberInvite` for the email → `SIGNUP_DISABLED`, :103-121) → create `User` (OAuth/magic: random password, `is_password_autoset=True`, `is_email_verified=True`; password sign-up: **zxcvbn score ≥ 3** else `PASSWORD_TOO_WEAK`, :90-100,357-368) → `Profile` → IdP sync of name/avatar when `ENABLE_<P>_SYNC=="1"` → `save_user_data` (last login medium/IP/UA) → `process_workspace_project_invitations` (creates memberships from **accepted** invites) → OAuth `Account` upsert. Redirect: onboarding → last workspace → oldest workspace → `invitations` (pending invites) → `create-workspace` (`authentication/utils/redirection_path.py:8-46`).

**Email + password** (`provider/credentials/email.py`): `EMAIL_PASSWORD_AUTHENTICATION_DISABLED` when `ENABLE_EMAIL_PASSWORD=="0"`; sign-up rejects existing email (`USER_ALREADY_EXIST`); sign-in: `USER_DOES_NOT_EXIST`, `AUTHENTICATION_FAILED_SIGN_IN` (:27-85). Views are Django form POSTs redirecting with `error_code` (`views/app/email.py:26-238`).

**Magic (unique) code** (`provider/credentials/magic_code.py`): requires `EMAIL_HOST` (`SMTP_NOT_CONFIGURED`) and `ENABLE_MAGIC_LINK_LOGIN != "0"` (`MAGIC_LINK_LOGIN_DISABLED`) (:47-69); 6-digit code (`randbelow(900000)+100000`) in Redis `magic_<email>` TTL 600 s. The generation guard tests the **previously stored** counter (`data["current_attempt"] > 2`), so **4 codes are issued per e-mail per 10-minute window** (1 initial + 3 re-sends) and only the 5th request raises `EMAIL_CODE_ATTEMPT_EXHAUSTED_SIGN_IN`/`_SIGN_UP` (5100/5102); each re-send also refreshes the 600 s TTL and clears the verify-attempt counter. Max 5 wrong verifications (`MAX_VERIFY_ATTEMPTS`) (`:28,84-118`); email sent by Celery `magic_link` task (`views/app/magic.py:54-58`).

**OAuth** (all in CE core): Google (`GOOGLE_CLIENT_ID/SECRET`, rejects unverified email), GitHub (`read:user user:email` + `read:org` when `GITHUB_ORGANIZATION_ID` → `GITHUB_USER_NOT_IN_ORG`; primary+verified email required), GitLab (`GITLAB_HOST` default `https://gitlab.com`, needs `confirmed_at`), Gitea (`GITEA_HOST`, verified email) (`provider/oauth/{google,github,gitlab,gitea}.py`). Callbacks `/auth/<provider>/callback/`; `state` stored in session and checked (`views/app/google.py:48-50,67-76`); tokens in `Account`. `IS_<P>_ENABLED` only drives the button; the provider checks client id/secret.

**Password reset/change/set**: forgot-password requires `EMAIL_HOST` (`SMTP_NOT_CONFIGURED`), Django `PasswordResetTokenGenerator`, link `/accounts/reset-password/?uidb64=&token=&email=`; reset/change/set all require zxcvbn ≥ 3; `set-password` only when `is_password_autoset` (`views/app/password_management.py:38-165`; `views/common.py:52-128`).

Error codes (`authentication/adapter/error.py:5-76`): 5000 INSTANCE_NOT_CONFIGURED, 5015 SIGNUP_DISABLED, 5016 MAGIC_LINK_LOGIN_DISABLED, 5019 USER_ACCOUNT_DEACTIVATED, 5021 PASSWORD_TOO_WEAK, 5025 SMTP_NOT_CONFIGURED, 5030 USER_ALREADY_EXIST, 5056 EMAIL_PASSWORD_AUTHENTICATION_DISABLED, 5060 USER_DOES_NOT_EXIST, 5065 AUTHENTICATION_FAILED_SIGN_IN, 5090/5092 INVALID_MAGIC_CODE, 5095/5097 EXPIRED_MAGIC_CODE, 5100/5102 EMAIL_CODE_ATTEMPT_EXHAUSTED, 5122 GITHUB_USER_NOT_IN_ORG, 5124 OAUTH_PROVIDER_UNVERIFIED_EMAIL, 5145 PASSWORD_ALREADY_SET, 5900 RATE_LIMIT_EXCEEDED.

### 14.4 Password policy

- **Server**: zxcvbn `score < 3` → `PASSWORD_TOO_WEAK` on sign-up, reset, change, set and admin sign-up (`adapter/base.py:92-100`; `password_management.py:145-150`; `views/common.py:83-89,122-128`; `license/api/views/admin.py:195-212`). No explicit length rule server-side; Django `AUTH_PASSWORD_VALIDATORS` are configured but the code paths use zxcvbn (`common.py:266-271`).
- **Client**: `getPasswordStrength` requires ≥ 8 chars, upper, lower, digit, special (`packages/utils/src/auth.ts:26-46`; `PASSWORD_MIN_LENGTH = 8`, `packages/constants/src/auth/index.ts:18`). So a password can pass the client rule and still fail zxcvbn (e.g. `Password1!`).

### 14.5 Invitations — SMTP is not required

- Workspace invite `POST /api/workspaces/<slug>/invitations/` — permission `WorkSpaceAdminPermission` = **Admin or Member** (`permissions/workspace.py:61-71`); cannot invite a role higher than your own; rejects active members; creates `WorkspaceMemberInvite` with JWT token (`{email, timestamp}` HS256 `SECRET_KEY`), default role 5; queues `workspace_invitation.delay` per invite (`app/views/workspace/invite.py:44,63-105,121-128`). The email task swallows all exceptions (`workspace_invitation_task.py:85-89`).
- Without email the invitee still joins: after login, `get_redirection_path` sends users with pending invites to `/invitations`; `GET /api/users/me/workspaces/invitations/` lists invites by the session email and `POST` accepts in bulk (`invite.py:263-323`). **Sign-up is allowed for invited emails even when `ENABLE_SIGNUP=0`** (`adapter/base.py:111-118`).
- Link flow `POST …/invitations/<pk>/join/`: exact token + authenticated session + matching email (`invite.py:167-189`).
- Project membership: the web app adds **existing workspace members** via `POST …/projects/<id>/members/` (project Admin only); a workspace Admin cannot be added as 5/15, a workspace Guest cannot be added as 15/20 (`app/views/project/member.py:46-82`). Self-join `POST /api/users/me/workspaces/<slug>/projects/invitations/`: Secret projects only for workspace Admins; project role = workspace role (`project/invite.py:131-174`). The email-based project invitation endpoint is broken (§13.8).

### 14.6 Roles & permissions

| Scope | Class / rule | Meaning | Evidence |
|---|---|---|---|
| decorator | `@allow_permission(roles, level="WORKSPACE"\|"PROJECT", creator=False, model=None)` | WORKSPACE: active `WorkspaceMember` with role in list; PROJECT: active `ProjectMember` with role in list **or a workspace Admin who is a project member (any project role)**; `creator=True` short-circuits for the row's creator; else 403 "You don't have the required permissions." | `app/permissions/base.py:19-89` |
| workspace | `WorkSpaceBasePermission` | POST any authenticated; GET any; PUT/PATCH Admin+Member; DELETE Admin | `permissions/workspace.py:19-48` |
| workspace | `WorkspaceOwnerPermission` | Admin only | `:51-58` |
| workspace | `WorkSpaceAdminPermission` | **Admin or Member** (despite the name) | `:61-71` |
| workspace | `WorkspaceEntityPermission` | GET any active member; write Admin+Member | `:74-90` |
| workspace | `WorkspaceViewerPermission` / `WorkspaceUserPermission` / `WorkspaceMemberPermission` | any active member | `:93-137` |
| project | `ProjectBasePermission` | GET any workspace member; POST workspace Admin/Member; other writes project Admin or workspace Admin in project | `permissions/project.py:13-53` |
| project | `ProjectMemberPermission` | GET project member; POST workspace Admin/Member; else project Admin/Member | `:56-85` |
| project | `ProjectEntityPermission` | GET project member; write project Admin/Member | `:88-119` |
| project | `ProjectAdminPermission` / `ProjectLitePermission` | project Admin / any project member | `:122-146` |
| pages | `ProjectPagePermission` | POST/PUT/PATCH Admin+Member; GET all roles; DELETE Admin; private pages owner-only | `permissions/page.py:93-128` |
| instance | `InstanceAdminPermission` | `InstanceAdmin` row with role ≥ 15 | `license/api/permissions/instance.py:12-18` |

What each role can do (enforcement points):
- **Workspace Admin (20)**: everything; only Admins change roles / remove members; cannot change own role; demoting to Guest cascades all project roles to 5; cannot remove a higher role; **the last Admin cannot leave** (`app/views/workspace/member.py:76-118,164-171`). Sees all projects and may join Secret ones.
- **Member (15)**: create projects, invite with role ≤ own, edit workspace settings; sees own projects **plus `network=2` Public projects** and can self-join them (`app/views/project/base.py:116-128,215-223`; `invite.py:139-146`).
- **Guest (5)**: only projects they belong to; cannot create projects/pages; with `guest_view_all_features=False` (default) sees **only work items they created**, same for pages, views, intake, comments, versions (`project/base.py:105-114`; `issue/base.py:99-106,315-321`; `page/base.py:220`; `view/base.py:156-160`); cannot be given project role 15/20.
- **Project Admin (20)**: add/remove project members, publish deploy boards, update project. Member `partial_update`: cannot touch equal/higher roles, cannot assign ≥ own (`member.py:233-262`).
- Workspace creation: creator → 20; refused with 403 when `DISABLE_WORKSPACE_CREATION=="1"`; name ≤80, slug ≤48, restricted slugs rejected (`workspace/base.py:83-130,253`). Account deactivation is refused for instance admins, for the sole admin of **any project**, and for the sole admin of **any workspace** (`user/base.py:257-260,277-285,298-306`).
- Instance admin ≠ workspace admin: an instance admin has no workspace rights unless also a member.

### 14.7 God mode (instance admin)

Backend (`license/api/views/admin.py`): first-time `POST /api/instances/admins/sign-up/` is blocked (`ADMIN_ALREADY_EXIST`) once `is_setup_done` or **any** `InstanceAdmin` exists; needs `email, password, first_name`; zxcvbn ≥ 3; creates User + Profile(`company_name`) + InstanceAdmin; sets `instance.is_setup_done=True`, `instance_name=company_name`, `is_telemetry_enabled`; logs in with the admin cookie and redirects to `<god-mode>/general/` (`:90-266`). Admin sign-in requires an existing active non-bot user with a matching password who is an InstanceAdmin (`:269-404`). Additional admins are added by email of an **existing** user (`:50-69`). The web app links to god mode from the user menu when `GET /api/users/me/instance-admin` says `is_instance_admin` (`app/views/user/base.py:87-90`; `user-menu-root.tsx:142`).

Admin UI pages (`apps/admin/app/routes.ts:11-24`; no EE pages, `EXTENDED_HEADER_SEGMENT_LABELS = {}`):

| Page | Edits | Evidence |
|---|---|---|
| `/` | setup form (first/last name, email, company name, password, telemetry toggle) when `!is_setup_done`, else sign-in | `components/instance/setup-form.tsx:42-48,155-161`; `(home)/page.tsx:37-42` |
| `/general` | `instance_name`, read-only admin email & `instance_id`, `is_telemetry_enabled` | `general/form.tsx:36-135` |
| `/workspace`, `/workspace/create` | list/search workspaces (10/page, member & project counts), create (admin becomes role 20), `DISABLE_WORKSPACE_CREATION` toggle; note **"You can't yet delete workspaces"** | `workspace/page.tsx:39,89-135`; `license/api/views/workspace.py:40-103` |
| `/email` | `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_FROM` (required), user/password (optional), TLS/SSL/None, saves `ENABLE_SMTP=1`, "Send test email"; disable endpoint blanks the keys | `email/email-config-form.tsx:62-228`; `configuration.py:62-171` |
| `/authentication` (+ `/google`, `/github`, `/gitlab`, `/gitea`) | `ENABLE_SIGNUP`; modes Unique codes (`ENABLE_MAGIC_LINK_LOGIN`, "You need to have set up SMTP"), Passwords (`ENABLE_EMAIL_PASSWORD`), Google/GitHub/GitLab/Gitea (`IS_*_ENABLED` + client ids/secrets, org id, hosts, sync toggles); refuses to disable the last enabled method | `authentication/page.tsx:117-159`; `hooks/oauth/core.tsx:36-91`; `helpers/authentication.ts:20-36` |
| `/ai` | `LLM_MODEL` (placeholder gpt-4o-mini), `LLM_API_KEY`; providers openai / anthropic / gemini in the backend | `ai/form.tsx:34-106`; `app/views/external/base.py:42-131` |
| `/image` | `UNSPLASH_ACCESS_KEY` | `image/form.tsx:32-76` |

`GET /api/instances/` is public (AllowAny, cached 2 h) and returns `is_activated`, `is_setup_done`, `enable_signup`, `is_workspace_creation_disabled`, `is_*_enabled`, `is_magic_login_enabled`, `is_email_password_enabled`, `has_llm_configured`, `has_unsplash_configured`, `file_size_limit`, `is_smtp_configured = bool(EMAIL_HOST)`, `admin/space/app_base_url`, `instance_changelog_url`, `is_self_managed=True`, `workspaces_exist` (`license/api/views/instance.py:29-170`).

### 14.8 Telemetry

`push_instance_metrics` runs every 360 min and on every API boot; exits early when `Instance.is_telemetry_enabled` is False (model default **True**; toggle on the General page or at setup); otherwise OTLP gauges (users, workspaces, projects, issues, modules, cycles, pages, per-workspace counts, `instance_id`, versions, `edition`, domain from `WEB_URL`) go to `OTLP_ENDPOINT` default `https://telemetry.plane.so` (gRPC; `OTLP_METRICS_PROTOCOL=http` alternative) (`license/bgtasks/telemetry_metrics.py:41-143,368-381`; `utils/otlp_endpoints.py:19,46-59`). `register_instance` also calls `api.github.com` for the latest release on every boot.

---

## 15. Community Edition gating table

Ground truth: **there is no runtime licence or feature-flag check anywhere in v1.4.2** — grep for `feature_flag|FEATURE_FLAGS|useFlag|is_free|plane.payment|IS_MULTI_TENANT|check_feature_flag` across `apps/api`, `apps/web`, `apps/admin`, `apps/space`, `packages` returns nothing but marketing constants and UI stubs; `InstanceEdition` has one value; `IS_SELF_MANAGED = True` (`license/models/instance.py:18-19`; `common.py:54`). Gating is hard-coded in the frontend or simply absent from the backend.

| Feature | CE v1.4.2? | Evidence |
|---|---|---|
| Email + password login / sign-up | **Yes** (default on) | `instance_config_variables/core.py:16-20`; `provider/credentials/email.py` |
| Magic / unique-code login | **Yes**, needs SMTP; default off | `core.py:22-26`; `magic_code.py:47-69` |
| Google / GitHub / GitLab / Gitea OAuth, GitHub org restriction, IdP profile sync | **Yes** | `provider/oauth/*.py`; `github.py:57-60,157-165`; `adapter/base.py:125-138` |
| OIDC / SAML / LDAP SSO | **No** — no such provider under `apps/api/plane/authentication`; marketed as ONE/Enterprise | file tree; `packages/constants/src/subscription.ts:35,44` |
| Invite-only sign-up (`ENABLE_SIGNUP=0`), disable workspace creation | **Yes** | `adapter/base.py:103-121`; `workspace/base.py:85-98` |
| Multiple instance admins; SMTP + test email; password reset | **Yes** | `admin.py:50-69`; `configuration.py:88-171`; `password_management.py:62-69` |
| Delete a workspace from god mode | **No** ("You can't yet delete workspaces") — but workspace Admins can delete from Workspace settings → General | `admin workspace/page.tsx:128-129`; `workspace/settings/workspace-details.tsx:31-230` |
| API keys + `/api/v1/` | **Yes** | `api/middleware/api_authentication.py:24,29-43` |
| Service tokens (`is_service=True`), per-token rate limit | **No** — no create path; `allowed_rate_limit` unused (the only throttle is the global `API_KEY_RATE_LIMIT`, and it misses the `BaseViewSet` endpoints, §11.2) | `app/views/api.py:29-57`; `api/rate_limit.py:12-23` |
| `?pql=` / `?filters=` on v1 work-item list | **No** — 400 "not supported on this Plane edition" | `api/views/issue.py:315-329` |
| Estimates under `/api/v1/` | **No** — routes not mounted | `api/urls/__init__.py:5-31` |
| Webhooks (with HMAC signature, retries) | **Yes** | §12 |
| Projects, work items, sub-work-items, relations, comments (threaded), reactions, links, attachments, drafts, stickies, subscriptions, notifications, favourites | **Yes** | §4, §9 |
| Cycles, Modules, Views, Pages, Intake (project features) | **Yes** — all five `isPro: false` | `project/settings/features-list.tsx:30-76` |
| Per-project active cycle with burndown, progress, assignee/label stats | **Yes** | `cycles/active-cycle/root.tsx:79-86`; `cycle/base.py:658-1049` |
| **Workspace-wide Active Cycles** page | **No** — upgrade panel only; no backend endpoint | `apps/web/core/components/active-cycles/workspace-active-cycles-upgrade.tsx:24,96,100`; `packages/constants/src/endpoints.ts:31` |
| **Bulk operations** on selected work items | **No** — "Upgrade to One" banner only | `issues/bulk-operations/root.tsx:19-27`; `upgrade-banner.tsx:15-36` |
| Bulk archive / bulk delete / bulk date update via API | **Yes** (Admin/Member; delete Admin) — endpoints exist even though the UI selection bar is gated | `app/views/issue/base.py:773-798,1106-1170`; `archive.py:305-343` |
| Estimate systems Points / Categories | **Yes** | `apps/web/core/components/estimates/create/helper.tsx:10-18` |
| Estimate system **Time** | **No** (`is_ee: true`) | `packages/constants/src/estimates.ts:122-141` |
| Editing an existing estimate | **No** — delete + recreate only | `estimate-list-item-buttons.tsx:21-33` |
| Time tracking / worklogs | **No** — only `Project.is_time_tracking_enabled` column and an exporter enum value; no model/view/route/UI | `project.py:98`; `exporter.py:26-33`; grep `Worklog` |
| Work-item types / Epics | **No** — `IssueType` schema only; no CRUD views; `CreateUpdateEpicModal` renders `<></>`; `IssueTypeSwitcher` shows the identifier only | `issue_type.py:14-55`; `epic-modal/modal.tsx:24-26`; `issue-type-switcher.tsx:21-23` |
| Custom workflows / transition rules / approvals | **No** — plain state option; no backend validation | `workflow/state-option.tsx:26-45` |
| Project updates, Initiatives, Teamspaces | **No** — no routes/components; `Team` model has no views | `apps/web/app/routes/core.ts`; `workspace.py:261-283` |
| Dashboards + Reports / Custom reports | **No** — `Dashboard`/`Widget` models dropped (migration 0092); Home has quick_links/recents/stickies only | `migrations/0092_…:32-40`; `home-dashboard-widgets.tsx:27-59` |
| Analytics: overview + work-items tabs | **Yes** | `analytics/tabs.tsx:11-14` |
| Analytics: cycle/module tabs, estimate-point or epic y-axes, project/type/epic x-axes | **No** — backend counts ids only / rejects | `build_chart.py:20-41,160-161,179` |
| Velocity, burn-up, CFD, lead/cycle time | **No** (NOT FOUND) | §10.4 |
| Exports CSV / XLSX / JSON | **Yes** | `exporter/base.py:22-63` |
| Project **pages** with real-time Yjs sync, versions, lock, archive, duplicate, PDF export | **Yes** | §9.2 |
| Workspace pages / wiki, nested-page move, page sharing to non-owners | **No** — `EPageStoreType` only PROJECT; `usePageFlag` false; private pages owner-only | `use-page-store.ts:13-15`; `use-page-flag.ts:12-14`; `permissions/page.py:93-98` |
| Editor **collaboration cursors** and editor **AI** extension | **No** — disabled in `useEditorFlagging` | `use-editor-flagging.ts:33-46` |
| AI assist in the work-item description modal ("I'm feeling lucky", GPT popover) | **Yes** when `LLM_API_KEY` set in god mode | `description-editor.tsx:247-266`; `admin ai/form.tsx:35-82` |
| Unsplash covers | **Yes** if key set | `instance.py:150` |
| Intake in-app | **Yes**; **Intake forms / email sources: No** (backend `SourceType` has only `IN_APP`) | `apps/api/plane/db/models/intake.py:38-39`; `packages/types/src/inbox.ts:27-31`; `features/intake/page.tsx:44` |
| Publish project to public Space (deploy board with comments/reactions/votes) | **Yes** — despite marketing listing "Public Views and Pages" as paid | `project/base.py:535-575`; `space/views/project.py:19-31`; `publish-project/modal.tsx:167-168` |
| Publish a **view** | **No** — stub hook | `views/publish/use-view-publish.tsx:8-13` |
| Gantt dependency lines | **No** — `ENABLE_ISSUE_DEPENDENCIES = false` | `issue/filter.ts:361` |
| Importers (Jira/GitHub) / Integrations settings | **No** — `IMPORTERS_LIST` constant unused; no routes; legacy models only | `packages/constants/src/workspace.ts:135-148` |
| Thai (`th`) UI language | **No** — 19 languages, no `th` | `packages/i18n/src/constants/language.ts:11-31` |
| Telemetry to plane.so | **On by default**; toggle in god mode or redirect `OTLP_ENDPOINT` | `instance.py:35`; `otlp_endpoints.py:19,52` |
| Kubernetes manifests / Helm sources in repo | **No** — README link only | `deployments/kubernetes/community/README.md:1-5` |

Marketing artefacts that ship in CE (not features): sidebar edition badge literal "Community" opening `PaidPlanUpgradeModal` (`workspace/edition-badge.tsx:29-43`); "Pro" `UpgradeBadge` next to Active Cycles (`extended-sidebar-item.tsx:204-208`); Billing page "Community — Unlimited projects, issues, cycles, modules, pages, and storage" + plan comparison from `PLANE_COMMUNITY_PRODUCTS` (Pro $8/mo, Business $15/mo, upgrade URLs on app.plane.so) (`billing/root.tsx:53-67`; `payment.ts:34-147`); plan feature lists (ONE: OIDC+SAML, Active Cycles, time tracking + limited bulk ops; PRO: Dashboards+Reports, Full Time Tracking + Bulk Ops, Teamspaces, Wikis; BUSINESS: Project Templates, Workflows+Approvals, Custom Reports, Nested Pages, Intake Forms; ENTERPRISE: LDAP, GAC) (`subscription.ts:7-48`); reserved workspace slugs `plane-pro, plane-ultimate, enterprise, silo, upgrade, billing, initiatives, workflow, epics, dashboard, pages, business, pro, license…` (`utils/constants.py:5-71`); i18n files `wiki.json, workflow.json, work-item-type.json, template.json, integration.json` present without UI.

---

## 16. Glossary — Scrum / Kanban / Jira / Trello term → Plane term

| Familiar term | Plane (v1.4.2 CE) | Notes / evidence |
|---|---|---|
| Site / instance (Jira Cloud site) | **Instance** (one per deployment; god mode at `/god-mode/`) | `license/models/instance.py` |
| Organisation / team / Jira site → Trello Workspace | **Workspace** (unique slug) | `workspace.py:122-136` |
| Jira Project / Trello Board | **Project** (identifier ≤12 chars, e.g. `WEB`) | `project.py:76` |
| Project key / issue key `WEB-123` | `identifier` + `sequence_id`; UI "work item identifier"; URL `/browse/WEB-123` | `issue.py:156`; `routes/core.ts:76-78` |
| Issue / Story / Task / Bug / Trello Card | **Work item** (code & DB: `Issue`); there are no issue *types* in CE | `issue.py:177`; §15 |
| Sub-task / checklist item | **Sub-work item** (`parent` self-FK); to-do lists exist inside rich text | `issue.py:114-120` |
| Epic | Closest CE object is a **Module** (grouping with lead, members, dates, status, burndown); Plane's own "Epic" is a paid work-item type | `module.py`; `epic-modal/modal.tsx:24-26` |
| Sprint / Iteration | **Cycle** (dates → status current/upcoming/completed/draft) | §6 |
| Sprint backlog | Work items in the cycle; cycle view `?cycle_view=current` | `cycle/base.py:184-205` |
| Product backlog | Work items in a state of group **`backlog`** (default state "Backlog"); there is no separate backlog container | `state.py:24-31` |
| Status / Trello list / Kanban column | **State** (name + colour + `group`) | `state.py:80-124` |
| Jira status category (To Do / In Progress / Done) | **State group**: `backlog`, `unstarted`, `started`, `completed`, `cancelled` (+ hidden `triage`) | `state.py:14-20` |
| Workflow transitions | none in CE — any state → any state | §5.3 |
| Definition of Done (for charts) | state group `completed` → `completed_at` set | `issue.py:240-255` |
| Resolution "Won't do" | state group `cancelled` (not counted as done in burndown) | §5.5 |
| Board (Scrum/Kanban board) | **Kanban layout** (also list / calendar / gantt / spreadsheet), swimlanes = `sub_group_by` (kanban `group_by` has no "no grouping" option; only `sub_group_by` does) | `packages/types/src/issues/issue.ts:15-21`; `packages/constants/src/issue/filter.ts:233-245` |
| WIP limit | NOT FOUND — no WIP-limit option in the kanban display filters | `packages/constants/src/issue/filter.ts:206-279` |
| Story points | **Estimate** with system **Points**; value attached as `estimate_point` | §8 |
| T-shirt sizing | Estimate system **Categories** | `estimates.ts:12-142` |
| Original estimate / time spent / worklog | not in CE | §15 |
| Label / Jira component / Trello label | **Label** (project or workspace scoped, label groups) | `label.py` |
| Priority | `urgent / high / medium / low / none` (default `none`) | `issue.py:107-113` |
| Assignee | **Assignees** (multiple) | `issue.py:149-155` |
| Reporter | `created_by` | `mixins.py:26-42` |
| Watcher / follower | **Subscriber** (`IssueSubscriber`) | `issue.py:593` |
| Due date / start date | `target_date` / `start_date` (date only) | `issue.py:147-148` |
| Linked issues (blocks / is blocked by / duplicates / relates) | **Relations**: `blocking`, `blocked_by`, `duplicate`, `relates_to` (v1 also `start_before/after`, `finish_before/after`) | `issue.py:272-293`; `relations/index.tsx:12-41` |
| Attachment | `FileAsset(entity_type=ISSUE_ATTACHMENT)`, 5 MiB default limit | `asset.py:36-46`; `common.py:353` |
| Comment / reply | `IssueComment` with `parent` threads, INTERNAL/EXTERNAL access | `issue.py:455-477` |
| Jira Filter / saved search | **View** (project view or workspace view) | §9.1 |
| Jira Dashboard / gadget | **Home** widgets (quick links, recents, stickies) + **Analytics** page; no custom dashboards | §10 |
| Burndown chart | Cycle/Module **progress chart** (`completion_chart`, remaining vs ideal) | §6.4 |
| Velocity chart | NOT FOUND — compute from cycle `completed_issues`/`completed_estimate_points` per cycle | §10.4 |
| Cumulative flow diagram | NOT FOUND | §10.4 |
| Lead time / cycle time | not precomputed; derive from `completed_at − created_at` and `issue_activities` state rows | §10.4 |
| Confluence page / Notion doc / wiki | **Page** (project pages only in CE) | §9.2 |
| Service desk / request queue / Trello inbox | **Intake** (items sit in the hidden Triage state until accepted) | §9.3 |
| Archive (Trello) | `archived_at` on work items (only completed/cancelled), cycles (only completed), modules (completed/cancelled), projects | §5.4, §6.1, §7 |
| Trash / delete | soft delete (`deleted_at`), purged after 60 days | §4.1 |
| Jira Version / Release | no direct equivalent; use Module or Cycle | — |
| Roles: Product Owner / Scrum Master | no role concept; Plane roles are **Admin (20) / Member (15) / Guest (5)** per workspace and per project | §14.6 |
| Site admin | **Instance admin** (god mode) — separate from workspace admin | §14.7 |
| Personal access token | **API token** `plane_api_…` (Profile settings → API tokens) | §11.1 |
| Jira automation rule / Trello Butler | **Automations**: auto-archive (`archive_in`) and auto-close (`close_in`) only | §5.4 |
| Trello Power-Up / Jira Marketplace app | not in CE; integrate via `/api/v1/` + webhooks | §11, §12 |
| Public/shared board link | **Publish project** → deploy board at `/spaces/issues/<anchor>` | §14.6 project visibility |
| Draft | **Draft work item** (workspace-level, converted into an issue) | `draft.py:81` |
| Sticky note | **Sticky** (personal, workspace-level) | `sticky.py:35` |

---

## 17. Things authors must NOT claim (contradicted by the source)

Deployment
1. "Plane's web app is Next.js." — It is React Router v7 on Vite with `ssr: false`; Next imports are compatibility shims (`apps/web/react-router.config.ts:5-6`; `apps/web/vite.config.ts:9-31`).
2. "Compose waits for services to be healthy." — No `healthcheck:` and no `depends_on … condition: service_healthy` in the compose file (the web/admin/space *images* do carry one); readiness comes from `wait_for_migrations` inside the entrypoints — `wait_for_db` is a no-op (`docker-compose.yml`; `wait_for_db.py:17-22`; `wait_for_migrations.py:15-26`).
3. "Change `POSTGRES_PASSWORD` in `plane.env` to change the DB password." — Django uses `DATABASE_URL`; the fallback reads `POSTGRES_HOST`, which is never set (`common.py:205-218`; `docker-compose.yml:55`).
4. "Set `GUNICORN_WORKERS` / `TRUSTED_PROXIES` / `AUTHENTICATION_RATE_LIMIT` in `plane.env`." — Not forwarded / hard-coded to 1 (`docker-compose.yml:53`; `Caddyfile.ce:33`).
5. "`APP_DOMAIN` is read by the app." — Only expanded into `WEB_URL` and `CORS_ALLOWED_ORIGINS`.
6. "There is a `/api/health` endpoint." — The API health check is `GET /` on the api container (`{"status":"OK"}`); the live server has `GET /live/health/` (`web/urls.py:8`; `health.controller.ts:11-19`).
7. "Kubernetes manifests/Helm chart are in the repo." — README link only.
8. "`./setup.sh stop` deletes data." — `compose down` without `-v`; volumes persist.
9. "Sessions live in Redis." — DB-backed `sessions` table (`common.py:376`).
10. "Celery uses a result backend / dedicated queues." — Neither; default `celery` queue, results discarded.
11. "A placeholder `SECRET_KEY` aborts startup." — Only a CRITICAL log; an *empty* key makes `configure_instance` fail. Rotating it breaks decryption of stored OAuth/SMTP/LLM secrets.
12. "`LIVE_SERVER_SECRET_KEY` secures live ↔ api." — Required to exist but enforced on no route; Django never reads it.
13. "Telemetry is opt-in." — `is_telemetry_enabled` defaults True; pushes to `https://telemetry.plane.so` every 6 h and at every API boot.
14. "Editing SMTP/OAuth values in `plane.env` after first boot takes effect." — `configure_instance` seeds once; `SKIP_ENV_VAR=1` makes runtime read the DB; edit in god mode.
15. "The API can start without RabbitMQ." — `register_instance` enqueues a task under `set -e`.
16. "The local build (`myplane/…:local`) is what the release compose runs." — Image names differ.

Data model & workflow
17. "Work-item numbers are reused after deletion." — `IssueSequence.issue` is SET_NULL; numbers are never reused.
18. "Deleting removes the row." — Soft delete; hard delete after 60 days.
19. "An issue can be in several cycles." — In practice no: adding it to another cycle re-points the existing bridge row. But do not claim the DB enforces it: the constraint is unique `(cycle, issue)`, and single-cycle membership is view logic (`cycle.py:112-120`; `app/views/cycle/issue.py:242-299`). Modules: many per issue, genuinely.
20. "Default priority is medium." — Default is `none`.
21. "New projects have cycles/modules/views/intake enabled." — Only `page_view` defaults True (`project.py:93-99`).
22. "Project network default is Secret / 'Public' means visible on the internet." — Default is Public (2) = visible to workspace Members; internet publishing is a separate DeployBoard.
23. "Default membership role is Member." — Default role is Guest (5) on both workspace and project.
24. "Guests see all work items in their projects." — Only their own unless `guest_view_all_features=True`.
25. "`WorkSpaceAdminPermission` means Admin only." — It also allows Member.
26. "There are workflow transition rules / a Done column that locks." — None in CE.
27. "`completed_at` is preserved when an issue is reopened." — It is reset to NULL.
28. "Any issue can be archived." — Only completed/cancelled state groups.
29. "Cycle/module archiving is automatic." — Manual via the archive endpoints (cycles only after `end_date`); only *issue* auto-archive/close is scheduled.
30. "Module status is computed from progress." — Manual field, default `planned`.
31. "Cycle `start_date`/`end_date` are plain dates." — DateTimeFields in UTC (module dates are DateFields).
32. "Relations `blocking` are stored as such." — Stored reversed as `blocked_by`; `blocking/start_after/finish_after/implements` are UI/API aliases.
33. "Activity/notifications are written synchronously." — Written by the Celery `issue_activity` task; without a worker nothing appears.

Cycles, burndown, analytics
34. "The burndown replays state history." — It subtracts issues by `completed_at` from a scalar total; adding an issue mid-cycle raises all past days.
35. "Cancelled items reduce the remaining line." — They do not.
36. "The ideal line comes from the API." — Computed in `progress-chart.tsx`.
37. "Burn-up / velocity / CFD / lead-time charts exist." — NOT FOUND.
38. "`progress_snapshot` is captured when a cycle ends." — Only on transfer-issues (and, since the app-API write serializer is `fields="__all__"`, by anyone who PATCHes the field directly); once set it is never cleared.
39. "Plane enforces a single active cycle." — Nothing rejects overlap server-side: `cycles/date-check/` always returns 200 and is only consulted by the React modal/sidebar, so an API client can create several overlapping `CURRENT` cycles; status is a SQL annotation, no DB constraint.
40. "Workspace Active Cycles works in CE." — Upgrade panel; no backend route.
41. "Analytics has cycle/module tabs or estimate-point metrics." — Two tabs; backend counts ids only.
42. "'Created vs completed' uses completion dates." — Buckets by creation month with current state group.
43. "Exports respect archive/draft filters." — Export uses `Issue.objects`, so archived, draft and triage rows are included.

Estimates, pages, intake
44. "Time estimates / worklogs / time tracking exist in CE." — Only booleans/enum leftovers.
45. "Estimates can be edited." — Delete-and-recreate only in CE.
46. "Estimates are available in `/api/v1/`." — Routes exist but are not mounted.
47. "Workspace-level pages/wiki exist in CE." — Project pages only.
48. "Private pages can be shared." — Owner-only in CE.
49. "Multi-user cursors appear in the editor." — `collaboration-cursor` disabled; sync still works.
50. "Intake accepts email/form submissions." — In-app only.

API & webhooks
51. "`/api/v1/` accepts the session cookie / returns 401 on bad key." — API key only; failures are 403.
52. "Default page size is 20, max 100." — 1000 / 1000.
53. "Per-token rate limits apply." — Global `API_KEY_RATE_LIMIT` per key only, and it does not cover the `/api/v1/` stickies and invitations endpoints (`BaseViewSet`, §11.2).
54. "Webhooks retry on 4xx/5xx." — Only on transport exceptions, and the backoff is a flat random 0–600 s per retry, not exponential; the webhook is deactivated on the 6th consecutive failure (initial + 5 retries).
55. "Webhooks can target localhost or a private IP by default." — Rejected unless allow-listed via `WEBHOOK_ALLOWED_IPS`/`WEBHOOK_ALLOWED_HOSTS`. But do not claim the *model validator* blocks them: it only rejects the bare netlocs `localhost`/`127.0.0.1`; `localhost:<port>` gets past it and is stopped by the SSRF loopback check instead (`db/models/webhook.py:27-31`; `utils/ip_address.py:78-96`).
56. "Adding/removing cycle or module issues via v1 fires webhooks." — It does not.
57. "Work-item types can be managed via API." — No route; `type_id` only.
58. "API tokens / webhooks are managed via `/api/v1/`." — Session API (`/api/users/api-tokens/`, `/api/workspaces/<slug>/webhooks/`).

Auth & admin
59. "Server password rule is 8 chars + classes." — Server uses zxcvbn score ≥ 3; the 8-char rule is client-side only.
60. "SMTP is required to invite users." — Invite rows are created regardless; invitees see pending invites after login; invited emails can sign up even with sign-up disabled.
61. "Magic-link login works without SMTP." — `SMTP_NOT_CONFIGURED`.
62. "Project invitation by email works." — The endpoint is broken as written; the UI adds existing workspace members instead.
63. "OIDC/SAML/LDAP are available." — Not in CE.
64. "Instance admins are workspace admins." — Separate tables/roles.
65. "Workspaces can be deleted from god mode." — Not yet; workspace Admins delete from workspace settings.
66. "Thai UI is available." — Not in v1.4.2.
67. "There is a licence key / feature flag to unlock features." — None exists; CE gating is hard-coded stubs.
