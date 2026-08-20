#!/usr/bin/env bash

# Shared bootstrap helpers.  Every public up_to_labN.sh sources this file.

BOOTSTRAP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
JENKINS_URL="${JENKINS_URL:-http://localhost:8080}"
GITEA_URL="${GITEA_URL:-http://localhost:3000}"
JENKINS_AUTH='admin:admin2569'
GITEA_AUTH='student:student2569'
BOOTSTRAP_JENKINS_IMAGE='jenkins-bootstrap-u0:2569'
JENKINS_DOCKER_IMAGE='jenkins-docker:2569'
DOCKER_HUB_API='https://hub.docker.com/v2'

step() {
  printf '\n[bootstrap][%s] %s\n' "${DT_NAME:-devtools}" "$*"
}

die() {
  printf '[bootstrap][FAIL] %s\n' "$*" >&2
  exit 1
}

wait_for_url() {
  local url="$1"
  local attempts="${2:-180}"
  local delay="${3:-2}"
  local i
  for ((i = 1; i <= attempts; i++)); do
    if curl -fsS --max-time 5 "$url" >/dev/null 2>&1; then
      return 0
    fi
    sleep "$delay"
  done
  die "timeout waiting for $url"
}

wait_for_jenkins() {
  local attempts="${1:-180}"
  local i
  for ((i = 1; i <= attempts; i++)); do
    if curl -fsS --max-time 5 -u "$JENKINS_AUTH" \
      "$JENKINS_URL/api/json" >/dev/null 2>&1; then
      return 0
    fi
    sleep 2
  done
  docker logs --tail 100 jenkins >&2 || true
  die "Jenkins did not become ready at $JENKINS_URL"
}

ensure_network() {
  docker network inspect cicd-net >/dev/null 2>&1 || docker network create cicd-net >/dev/null
}

require_dockerhub_env() {
  if [ -z "${DOCKER_USER:-}" ] || [ -z "${DOCKER_TOKEN:-}" ]; then
    cat >&2 <<'MESSAGE'
[bootstrap][FAIL] LAB 3+ requires Docker Hub credentials.
Export your own Docker Hub username and a Read/Write access token, then run again:
  export DOCKER_USER='<your-docker-hub-username>'
  export DOCKER_TOKEN='<your-docker-hub-access-token>'
MESSAGE
    exit 1
  fi
}

jenkins_crumb_header() {
  local cookie_file="$1"
  local response field crumb
  response="$(curl -fsS -u "$JENKINS_AUTH" -c "$cookie_file" -b "$cookie_file" \
    "$JENKINS_URL/crumbIssuer/api/json")"
  field="$(printf '%s' "$response" | sed -n 's/.*"crumbRequestField":"\([^"]*\)".*/\1/p')"
  crumb="$(printf '%s' "$response" | sed -n 's/.*"crumb":"\([^"]*\)".*/\1/p')"
  [ -n "$field" ] && [ -n "$crumb" ] || die 'could not obtain Jenkins crumb'
  printf '%s:%s' "$field" "$crumb"
}

jenkins_post() {
  local url="$1"
  local cookie_file
  cookie_file="$(mktemp)"
  curl -fsS -u "$JENKINS_AUTH" -b "$cookie_file" \
    -H "$(jenkins_crumb_header "$cookie_file")" -X POST "$url"
  rm -f "$cookie_file"
}

seed_dockerhub_credential() {
  local cookie_file user_b64 token_b64 script response
  user_b64="$(printf '%s' "$DOCKER_USER" | base64 | tr -d '\n')"
  token_b64="$(printf '%s' "$DOCKER_TOKEN" | base64 | tr -d '\n')"
  script="$(cat <<GROOVY
import com.cloudbees.plugins.credentials.CredentialsScope
import com.cloudbees.plugins.credentials.SystemCredentialsProvider
import com.cloudbees.plugins.credentials.domains.Domain
import com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl

def decoder = java.util.Base64.decoder
def username = new String(decoder.decode('${user_b64}'), 'UTF-8')
def password = new String(decoder.decode('${token_b64}'), 'UTF-8')
def domain = Domain.global()
def store = SystemCredentialsProvider.getInstance().getStore()
def replacement = new UsernamePasswordCredentialsImpl(
  CredentialsScope.GLOBAL,
  'dockerhub',
  'Docker Hub Read/Write access token for the CI/CD lab',
  username,
  password
)
def existing = store.getCredentials(domain).find { it.id == 'dockerhub' }
if (existing == null) {
  assert store.addCredentials(domain, replacement)
} else {
  assert store.updateCredentials(domain, existing, replacement)
}
println 'dockerhub:UsernamePasswordCredentialsImpl:GLOBAL'
GROOVY
)"
  cookie_file="$(mktemp)"
  response="$(printf '%s' "$script" | curl -fsS -u "$JENKINS_AUTH" -b "$cookie_file" \
    -H "$(jenkins_crumb_header "$cookie_file")" \
    --data-urlencode script@- -X POST "$JENKINS_URL/scriptText")"
  rm -f "$cookie_file"
  unset script token_b64
  printf '%s' "$response" | grep -q 'dockerhub:UsernamePasswordCredentialsImpl:GLOBAL' \
    || die 'could not seed GLOBAL UsernamePassword credential id dockerhub'
  step 'seeded Jenkins credential dockerhub (UsernamePassword, GLOBAL)'
}

dockerhub_jwt() {
  local response jwt
  response="$(python3 -c \
    'import json, os; print(json.dumps({"identifier": os.environ["DOCKER_USER"], "secret": os.environ["DOCKER_TOKEN"]}))' \
    | curl -fsS -H 'Content-Type: application/json' --data-binary @- \
      "$DOCKER_HUB_API/auth/token")" \
    || die 'Docker Hub authentication failed; check DOCKER_USER and DOCKER_TOKEN'
  jwt="$(printf '%s' "$response" | python3 -c \
    'import json, sys; print(json.load(sys.stdin).get("access_token", ""))')"
  unset response
  [ -n "$jwt" ] || die 'Docker Hub authentication did not return a JWT'
  printf '%s' "$jwt"
}

ensure_dockerhub_repo() {
  local jwt response_file status
  jwt="$(dockerhub_jwt)"
  response_file="$(mktemp)"
  status="$(curl -sS -o "$response_file" -w '%{http_code}' \
    -H "Authorization: Bearer $jwt" \
    "$DOCKER_HUB_API/namespaces/$DOCKER_USER/repositories/ci-demo")"
  if [ "$status" = '404' ]; then
    status="$(python3 -c \
      'import json, os; print(json.dumps({"name":"ci-demo","namespace":os.environ["DOCKER_USER"],"description":"Jenkins CI/CD teaching lab","registry":"docker.io","is_private":False}))' \
      | curl -sS -o "$response_file" -w '%{http_code}' \
        -H "Authorization: Bearer $jwt" -H 'Content-Type: application/json' \
        --data-binary @- "$DOCKER_HUB_API/namespaces/$DOCKER_USER/repositories")"
    if [ "$status" != '201' ]; then
      rm -f "$response_file"
      unset jwt
      die "Docker Hub could not create $DOCKER_USER/ci-demo (HTTP $status)"
    fi
    step "created public Docker Hub repository $DOCKER_USER/ci-demo"
  elif [ "$status" != '200' ]; then
    rm -f "$response_file"
    unset jwt
    die "Docker Hub could not inspect $DOCKER_USER/ci-demo (HTTP $status)"
  fi
  python3 -c \
    'import json, sys; data=json.load(open(sys.argv[1])); raise SystemExit(1 if data.get("is_private", True) else 0)' \
    "$response_file" || {
      rm -f "$response_file"
      unset jwt
      die "Docker Hub repository $DOCKER_USER/ci-demo exists but is not public"
    }
  rm -f "$response_file"
  unset jwt
  step "verified public Docker Hub repository $DOCKER_USER/ci-demo"
}

put_job() {
  local name="$1"
  local config="$2"
  local endpoint cookie_file
  if curl -fsS -u "$JENKINS_AUTH" "$JENKINS_URL/job/$name/api/json" >/dev/null 2>&1; then
    endpoint="$JENKINS_URL/job/$name/config.xml"
  else
    endpoint="$JENKINS_URL/createItem?name=$name"
  fi
  cookie_file="$(mktemp)"
  curl -fsS -u "$JENKINS_AUTH" -b "$cookie_file" \
    -H "$(jenkins_crumb_header "$cookie_file")" \
    -H 'Content-Type: application/xml' --data-binary "@$config" -X POST "$endpoint" >/dev/null
  rm -f "$cookie_file"
}

job_last_number() {
  local name="$1"
  curl -gfsS -u "$JENKINS_AUTH" "$JENKINS_URL/job/$name/api/json?tree=lastBuild[number]" \
    | python3 -c 'import json, sys; build=json.load(sys.stdin).get("lastBuild"); print("" if build is None else build["number"])'
}

wait_for_build_after() {
  local name="$1"
  local baseline="$2"
  local attempts="${3:-240}"
  local i response number
  for ((i = 1; i <= attempts; i++)); do
    response="$(curl -gfsS -u "$JENKINS_AUTH" \
      "$JENKINS_URL/job/$name/lastBuild/api/json?tree=number,building,result" 2>/dev/null || true)"
    number="$(printf '%s' "$response" | sed -n 's/.*"number":\([0-9][0-9]*\).*/\1/p')"
    if [ -n "$number" ] && [ "$number" -gt "$baseline" ] \
      && printf '%s' "$response" | grep -q '"building":false'; then
      if printf '%s' "$response" | grep -q '"result":"SUCCESS"'; then
        printf '%s\n' "$number"
        return 0
      fi
      curl -fsS -u "$JENKINS_AUTH" "$JENKINS_URL/job/$name/$number/consoleText" >&2 || true
      die "$name build #$number did not finish SUCCESS"
    fi
    sleep 2
  done
  die "timeout waiting for a new $name build after #$baseline"
}

ensure_successful_build() {
  local name="$1"
  local current response result
  current="$(job_last_number "$name")"
  if [ -n "$current" ]; then
    response="$(curl -gfsS -u "$JENKINS_AUTH" \
      "$JENKINS_URL/job/$name/$current/api/json?tree=building,result")"
    result="$(printf '%s' "$response" | sed -n 's/.*"result":"\([A-Z]*\)".*/\1/p')"
    if [ "$result" = 'SUCCESS' ]; then
      step "$name already has successful build #$current"
      return 0
    fi
  fi
  current="${current:-0}"
  step "triggering $name (baseline #$current)"
  jenkins_post "$JENKINS_URL/job/$name/build" >/dev/null
  wait_for_build_after "$name" "$current" >/dev/null
}

assert_job_success() {
  local name="$1"
  curl -gfsS -u "$JENKINS_AUTH" \
    "$JENKINS_URL/job/$name/lastBuild/api/json?tree=building,result" \
    | grep -q '"result":"SUCCESS"' || die "$name has no successful last build"
}

anonymous_manifest_exists() {
  local image="$1"
  local docker_config status
  docker_config="$(mktemp -d)"
  if DOCKER_CONFIG="$docker_config" docker manifest inspect "$image" >/dev/null 2>&1; then
    status=0
  else
    status=$?
  fi
  rm -rf "$docker_config"
  return "$status"
}

ensure_lab1_state() {
  step 'LAB 1: create cicd-net and Jenkins with setup wizard disabled'
  ensure_network
  [ -s "$BOOTSTRAP_DIR/plugins.txt" ] || die "$BOOTSTRAP_DIR/plugins.txt is missing or empty"
  if ! docker image inspect "$BOOTSTRAP_JENKINS_IMAGE" >/dev/null 2>&1; then
    step "building $BOOTSTRAP_JENKINS_IMAGE (includes frozen suggested plugins)"
    docker build -t "$BOOTSTRAP_JENKINS_IMAGE" -f "$BOOTSTRAP_DIR/Dockerfile.bootstrap" "$BOOTSTRAP_DIR"
  fi
  if ! docker container inspect jenkins >/dev/null 2>&1; then
    docker run -d --name jenkins --restart unless-stopped \
      --network cicd-net -p 8080:8080 \
      -e JAVA_OPTS=-Djenkins.install.runSetupWizard=false \
      -v jenkins_home:/var/jenkins_home \
      "$BOOTSTRAP_JENKINS_IMAGE" >/dev/null
  fi
  docker start jenkins >/dev/null
  wait_for_jenkins
  put_job first-freestyle "$BOOTSTRAP_DIR/jobs/first-freestyle.xml"
  ensure_successful_build first-freestyle
  assert_job_success first-freestyle
  curl -fsS -u "$JENKINS_AUTH" "$JENKINS_URL/job/first-freestyle/api/json" >/dev/null
}

ensure_lab2_state() {
  ensure_lab1_state
  step 'LAB 2: create first-pipeline and retain one successful build'
  put_job first-pipeline "$BOOTSTRAP_DIR/jobs/first-pipeline.xml"
  local current response
  if ! curl -gfsS -u "$JENKINS_AUTH" \
    "$JENKINS_URL/job/first-pipeline/api/json?tree=property[parameterDefinitions[name]]" \
    | grep -q 'APP_ENV'; then
    current="$(job_last_number first-pipeline)"
    current="${current:-0}"
    step "seeding first-pipeline parameter definition (baseline #$current)"
    jenkins_post "$JENKINS_URL/job/first-pipeline/build" >/dev/null
    wait_for_build_after first-pipeline "$current" >/dev/null
  fi
  current="$(job_last_number first-pipeline)"
  if [ -n "$current" ]; then
    response="$(curl -gfsS -u "$JENKINS_AUTH" \
      "$JENKINS_URL/job/first-pipeline/$current/api/json?tree=building,result,actions[parameters[name,value]]")"
  else
    response=''
  fi
  if ! printf '%s' "$response" | python3 -c \
    'import json, sys; d=json.load(sys.stdin); ps=[p for a in d.get("actions",[]) for p in a.get("parameters",[])]; ok=(not d.get("building", True) and d.get("result")=="SUCCESS" and any(p.get("name")=="APP_ENV" and p.get("value")=="prod" for p in ps)); raise SystemExit(0 if ok else 1)' \
    2>/dev/null; then
    current="${current:-0}"
    step "triggering first-pipeline with APP_ENV=prod (baseline #$current)"
    jenkins_post "$JENKINS_URL/job/first-pipeline/buildWithParameters?APP_ENV=prod" >/dev/null
    wait_for_build_after first-pipeline "$current" >/dev/null
  else
    step "first-pipeline already has successful APP_ENV=prod build #$current"
  fi
  assert_job_success first-pipeline
}

jenkins_needs_lab3_recreate() {
  [ "$(docker inspect -f '{{.Config.Image}}' jenkins)" = "$JENKINS_DOCKER_IMAGE" ] || return 0
  [ "$(docker inspect -f '{{.Image}}' jenkins)" = "$(docker image inspect -f '{{.Id}}' "$JENKINS_DOCKER_IMAGE")" ] || return 0
  [ "$(docker inspect -f '{{.Config.User}}' jenkins)" = 'root' ] || return 0
  docker inspect -f '{{range .Mounts}}{{println .Destination}}{{end}}' jenkins \
    | grep -qx '/var/run/docker.sock' || return 0
  return 1
}

ensure_lab3_state() {
  require_dockerhub_env
  ensure_lab2_state
  step 'LAB 3: build Jenkins image with Docker CLI'
  if ! docker image inspect "$JENKINS_DOCKER_IMAGE" >/dev/null 2>&1 \
    || ! docker run --rm --entrypoint docker "$JENKINS_DOCKER_IMAGE" --version >/dev/null 2>&1; then
    docker build -t "$JENKINS_DOCKER_IMAGE" -f "$BOOTSTRAP_DIR/Dockerfile.jenkins" "$BOOTSTRAP_DIR"
  fi
  if jenkins_needs_lab3_recreate; then
    step 'recreating jenkins with preserved jenkins_home, root user, and Docker socket'
    docker rm -f jenkins >/dev/null
    docker run -d --name jenkins --restart unless-stopped \
      --network cicd-net -p 8080:8080 -u root \
      -e JAVA_OPTS=-Djenkins.install.runSetupWizard=false \
      -v jenkins_home:/var/jenkins_home \
      -v /var/run/docker.sock:/var/run/docker.sock \
      "$JENKINS_DOCKER_IMAGE" >/dev/null
  else
    docker start jenkins >/dev/null
  fi
  wait_for_jenkins

  step 'LAB 3: prepare Docker Hub repository and Jenkins credential'
  ensure_dockerhub_repo
  seed_dockerhub_credential
  put_job docker-build-push "$BOOTSTRAP_DIR/jobs/docker-build-push.xml"
  local current response result
  current="$(job_last_number docker-build-push)"
  if [ -n "$current" ]; then
    response="$(curl -gfsS -u "$JENKINS_AUTH" \
      "$JENKINS_URL/job/docker-build-push/$current/api/json?tree=building,result")"
    result="$(printf '%s' "$response" | sed -n 's/.*"result":"\([A-Z]*\)".*/\1/p')"
  else
    result=''
  fi
  if [ "$result" != 'SUCCESS' ] \
    || ! anonymous_manifest_exists "docker.io/$DOCKER_USER/ci-demo:$current"; then
    current="${current:-0}"
    step "triggering docker-build-push (baseline #$current)"
    jenkins_post "$JENKINS_URL/job/docker-build-push/build" >/dev/null
    current="$(wait_for_build_after docker-build-push "$current" 600)"
  else
    step "docker-build-push already has Hub-backed successful build #$current"
  fi
  assert_job_success docker-build-push
  anonymous_manifest_exists "docker.io/$DOCKER_USER/ci-demo:$current" \
    || die "Docker Hub manifest is missing: docker.io/$DOCKER_USER/ci-demo:$current"
  step "verified Docker Hub manifest docker.io/$DOCKER_USER/ci-demo:$current"
}

ensure_gitea_user() {
  if docker exec -u git gitea gitea admin user list --config /data/gitea/conf/app.ini \
    | grep -q '[[:space:]]student[[:space:]]'; then
    return 0
  fi
  docker exec -u git gitea gitea admin user create \
    --config /data/gitea/conf/app.ini \
    --username student --password student2569 \
    --email student@example.com --must-change-password=false >/dev/null
}

ensure_hello_repo() {
  local tmp_dir
  if ! curl -fsS -u "$GITEA_AUTH" "$GITEA_URL/api/v1/repos/student/hello-ci" >/dev/null 2>&1; then
    curl -fsS -u "$GITEA_AUTH" -H 'Content-Type: application/json' \
      -d '{"name":"hello-ci","private":false,"default_branch":"main"}' \
      "$GITEA_URL/api/v1/user/repos" >/dev/null
  fi
  tmp_dir="$(mktemp -d)"
  trap 'rm -rf "$tmp_dir"' RETURN
  if git ls-remote -q \
    "http://student:student2569@localhost:3000/student/hello-ci.git" \
    refs/heads/main | grep -q .; then
    git clone -q "http://student:student2569@localhost:3000/student/hello-ci.git" \
      "$tmp_dir/repo"
  else
    git -C "$tmp_dir" init -b main repo >/dev/null
  fi
  git -C "$tmp_dir/repo" config user.name student
  git -C "$tmp_dir/repo" config user.email student@example.com
  cp "$BOOTSTRAP_DIR/fixtures/hello-ci.Jenkinsfile" "$tmp_dir/repo/Jenkinsfile"
  cp "$BOOTSTRAP_DIR/fixtures/hello-ci.hello.sh" "$tmp_dir/repo/hello.sh"
  cp "$BOOTSTRAP_DIR/fixtures/hello-ci.expected.txt" "$tmp_dir/repo/expected.txt"
  chmod +x "$tmp_dir/repo/hello.sh"
  git -C "$tmp_dir/repo" add Jenkinsfile hello.sh expected.txt
  if ! git -C "$tmp_dir/repo" diff --cached --quiet; then
    git -C "$tmp_dir/repo" commit -m 'Normalize hello-ci LAB 4 fixture' >/dev/null
    if git -C "$tmp_dir/repo" remote get-url origin >/dev/null 2>&1; then
      git -C "$tmp_dir/repo" push origin main >/dev/null
    else
      git -C "$tmp_dir/repo" remote add origin \
        "http://student:student2569@localhost:3000/student/hello-ci.git"
      git -C "$tmp_dir/repo" push -u origin main >/dev/null
    fi
  fi
  rm -rf "$tmp_dir"
  trap - RETURN
}

ensure_lab4_state() {
  ensure_lab3_state
  step 'LAB 4: start canonical Gitea 1.27.2 and create student fixture'
  if ! docker container inspect gitea >/dev/null 2>&1; then
    docker run -d --name gitea --restart unless-stopped \
      --network cicd-net -p 3000:3000 \
      -e GITEA__webhook__ALLOWED_HOST_LIST=private \
      -e GITEA__server__DISABLE_SSH=true \
      -e GITEA__server__DOMAIN=localhost \
      -e GITEA__server__ROOT_URL=http://localhost:3000/ \
      -e GITEA__security__INSTALL_LOCK=true \
      -v gitea_data:/data gitea/gitea:1.27.2 >/dev/null
  fi
  docker start gitea >/dev/null
  wait_for_url "$GITEA_URL/api/v1/version" 180 2
  ensure_gitea_user
  git config --global init.defaultBranch main
  ensure_hello_repo

  put_job hello-ci-pipeline "$BOOTSTRAP_DIR/jobs/hello-ci-poll.xml"
  ensure_successful_build hello-ci-pipeline
  assert_job_success hello-ci-pipeline
  curl -fsS -u "$GITEA_AUTH" "$GITEA_URL/api/v1/repos/student/hello-ci" \
    | grep -q '"private":false' || die 'student/hello-ci is not public'
  docker exec gitea grep -Eq '^ROOT_URL[[:space:]]*=[[:space:]]*http://localhost:3000/' \
    /data/gitea/conf/app.ini || die 'Gitea ROOT_URL is not canonical'
}

gwt_is_active() {
  curl -fsS -u "$JENKINS_AUTH" "$JENKINS_URL/pluginManager/api/json?depth=1" \
    | python3 -c 'import json, sys; plugins=json.load(sys.stdin).get("plugins", []); raise SystemExit(0 if any(p.get("shortName") == "generic-webhook-trigger" and p.get("version") == "2.4.2" and p.get("active") for p in plugins) else 1)'
}

ensure_gwt_plugin() {
  if gwt_is_active; then
    return 0
  fi
  step 'installing generic-webhook-trigger:2.4.2 and restarting Jenkins'
  docker stop jenkins >/dev/null
  docker run --rm -u root -v jenkins_home:/var/jenkins_home \
    --entrypoint jenkins-plugin-cli "$JENKINS_DOCKER_IMAGE" \
    --plugin-download-directory /var/jenkins_home/plugins \
    --plugins generic-webhook-trigger:2.4.2
  docker start jenkins >/dev/null
  wait_for_jenkins 240
  gwt_is_active || die 'generic-webhook-trigger 2.4.2 is not active'
}

ensure_gitea_webhook() {
  local hook_url hooks
  hook_url='http://jenkins:8080/generic-webhook-trigger/invoke?token=cicd2569-hello'
  hooks="$(curl -fsS -u "$GITEA_AUTH" \
    "$GITEA_URL/api/v1/repos/student/hello-ci/hooks")"
  if printf '%s' "$hooks" | grep -Fq "$hook_url"; then
    return 0
  fi
  curl -fsS -u "$GITEA_AUTH" -H 'Content-Type: application/json' \
    -d '{"type":"gitea","active":true,"events":["push"],"config":{"url":"http://jenkins:8080/generic-webhook-trigger/invoke?token=cicd2569-hello","content_type":"json"}}' \
    "$GITEA_URL/api/v1/repos/student/hello-ci/hooks" >/dev/null
}

push_webhook_probe() {
  local baseline tmp_dir build_number
  baseline="$(job_last_number hello-ci-pipeline)"
  baseline="${baseline:-0}"
  tmp_dir="$(mktemp -d)"
  trap 'rm -rf "$tmp_dir"' RETURN
  git clone -q "http://student:student2569@localhost:3000/student/hello-ci.git" "$tmp_dir/repo"
  git -C "$tmp_dir/repo" config user.name student
  git -C "$tmp_dir/repo" config user.email student@example.com
  git -C "$tmp_dir/repo" commit --allow-empty \
    -m "Verify webhook bootstrap $(date -u +%Y%m%dT%H%M%SZ)" >/dev/null
  git -C "$tmp_dir/repo" push origin main >/dev/null
  build_number="$(wait_for_build_after hello-ci-pipeline "$baseline" 240)"
  rm -rf "$tmp_dir"
  trap - RETURN
  curl -gfsS -u "$JENKINS_AUTH" \
    "$JENKINS_URL/job/hello-ci-pipeline/$build_number/api/json?tree=actions[causes[shortDescription]]" \
    | grep -q 'Generic Cause' || die "build #$build_number did not report Generic Cause"
  step "webhook push triggered successful hello-ci-pipeline build #$build_number (Generic Cause)"
}

ensure_lab5_state() {
  ensure_lab4_state
  step 'LAB 5: install GWT 2.4.2, replace polling with tokenized webhook trigger'
  ensure_gwt_plugin
  put_job hello-ci-pipeline "$BOOTSTRAP_DIR/jobs/hello-ci-webhook.xml"
  ensure_gitea_webhook
  push_webhook_probe
  curl -fsS -u "$JENKINS_AUTH" "$JENKINS_URL/job/hello-ci-pipeline/config.xml" \
    | grep -q '<token>cicd2569-hello</token>' || die 'Jenkins webhook token is missing'
  if curl -fsS -u "$JENKINS_AUTH" "$JENKINS_URL/job/hello-ci-pipeline/config.xml" \
    | grep -q '<hudson.triggers.SCMTrigger>'; then
    die 'Poll SCM is still enabled on hello-ci-pipeline'
  fi
}
