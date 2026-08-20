#!/usr/bin/env bash

# Shared bootstrap helpers.  Every public up_to_labN.sh sources this file.

BOOTSTRAP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
JENKINS_URL="${JENKINS_URL:-http://localhost:8080}"
JENKINS_AUTH='admin:admin2569'
BOOTSTRAP_JENKINS_IMAGE='jenkins-bootstrap-u0:2569'
JENKINS_DOCKER_IMAGE='jenkins-docker:2569'
DOCKER_HUB_API='https://hub.docker.com/v2'
GITHUB_API='https://api.github.com'
GH_API_REQUEST_COUNT=0
GH_API_BODY=''
GH_API_STATUS=''
GITHUB_REPO_CREATED_BY_THIS_RUN=false
GITHUB_HOOK_ID=''
BOOTSTRAP_GIT_ROOT="$(git -C "$BOOTSTRAP_DIR" rev-parse --show-toplevel 2>/dev/null || true)"
if [ -n "$BOOTSTRAP_GIT_ROOT" ]; then
  BOOTSTRAP_DIFF_BASELINE="$(git -C "$BOOTSTRAP_DIR" diff -- . | sha256sum | awk '{print $1}')"
else
  BOOTSTRAP_DIFF_BASELINE=''
fi

step() {
  printf '\n[bootstrap][%s] %s\n' "${DT_NAME:-devtools}" "$*"
}

die() {
  printf '[bootstrap][FAIL] %s\n' "$*" >&2
  exit 1
}

require_github_env() {
  if [ -z "${GITHUB_USER:-}" ] || [ -z "${GITHUB_TOKEN:-}" ]; then
    cat >&2 <<'MESSAGE'
[bootstrap][FAIL] LAB 4+ ต้องใช้บัญชี GitHub และ PAT classic
กรุณากำหนด GITHUB_USER และ GITHUB_TOKEN (scope public_repo + admin:repo_hook หรือ repo) แล้วรันใหม่:
  export GITHUB_USER='<ชื่อผู้ใช้ GitHub>'
  export GITHUB_TOKEN='<GitHub PAT>'
MESSAGE
    exit 1
  fi
  [[ "$GITHUB_USER" =~ ^[A-Za-z0-9][A-Za-z0-9-]{0,38}$ ]] \
    || die 'GITHUB_USER มีรูปแบบไม่ถูกต้อง'
}

# Usage: gh_api METHOD /path [json-body]
# Results are returned separately in GH_API_BODY and GH_API_STATUS.
gh_api() {
  local tracing=0
  local method="$1"
  local path="$2"
  local payload="${3:-}"
  local temporary_directory headers_file body_file config_file status retry_after curl_rc
  local -a curl_arguments

  case $- in
    *x*) tracing=1; set +x ;;
  esac
  require_github_env
  temporary_directory="$(mktemp -d)" || die 'สร้างพื้นที่ชั่วคราวสำหรับ GitHub API ไม่สำเร็จ'
  chmod 700 "$temporary_directory"
  headers_file="$temporary_directory/headers"
  body_file="$temporary_directory/body"
  config_file="$temporary_directory/curl.conf"
  printf 'header = "Authorization: token %s"\n' "$GITHUB_TOKEN" >"$config_file"
  chmod 600 "$config_file"
  curl_arguments=(
    --config "$config_file"
    --silent --show-error
    --connect-timeout 15
    --max-time 60
    --request "$method"
    --header 'Accept: application/vnd.github+json'
    --header 'X-GitHub-Api-Version: 2022-11-28'
    --dump-header "$headers_file"
    --output "$body_file"
    --write-out '%{http_code}'
  )
  if [ -n "$payload" ]; then
    curl_arguments+=(--header 'Content-Type: application/json' --data-binary "$payload")
  fi

  if status="$(curl "${curl_arguments[@]}" "$GITHUB_API$path")"; then
    curl_rc=0
  else
    curl_rc=$?
  fi
  if [ "$tracing" -eq 1 ]; then
    set -x
  fi

  GH_API_REQUEST_COUNT=$((GH_API_REQUEST_COUNT + 1))
  if [ "$curl_rc" -ne 0 ]; then
    rm -rf -- "$temporary_directory"
    die "เชื่อมต่อ GitHub API ไม่สำเร็จ (curl exit $curl_rc)"
  fi
  GH_API_STATUS="$status"
  GH_API_BODY="$(<"$body_file")"
  retry_after="$(awk '
    tolower($0) ~ /^retry-after:/ {
      sub(/^[^:]*:[[:space:]]*/, "")
      sub(/\r$/, "")
      print
      exit
    }
  ' "$headers_file")"
  rm -rf -- "$temporary_directory"

  if [ "$GH_API_STATUS" = '403' ] || [ "$GH_API_STATUS" = '429' ]; then
    die "GitHub API ปฏิเสธหรือจำกัดอัตราคำขอ (HTTP $GH_API_STATUS, Retry-After: ${retry_after:-ไม่ระบุ}) กรุณารอตามเวลาที่แจ้งแล้วรันใหม่"
  fi
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

github_git_with_askpass() {
  local askpass status tracing=0
  askpass="$(mktemp)" || die 'สร้าง GIT_ASKPASS ชั่วคราวไม่สำเร็จ'
  chmod 700 "$askpass"
  printf '%s\n' '#!/usr/bin/env sh' \
    'case "$1" in' \
    '  *Username*) printf '\''%s\n'\'' "$GITHUB_USER" ;;' \
    '  *) printf '\''%s\n'\'' "$GITHUB_TOKEN" ;;' \
    'esac' >"$askpass"
  trap 'rm -f -- "$askpass"' RETURN
  case $- in
    *x*) tracing=1; set +x ;;
  esac
  if GIT_ASKPASS="$askpass" GIT_TERMINAL_PROMPT=0 "$@"; then
    status=0
  else
    status=$?
  fi
  if [ "$tracing" -eq 1 ]; then
    set -x
  fi
  rm -f -- "$askpass"
  trap - RETURN
  return "$status"
}

github_marker_is_valid() {
  printf '%s' "$GH_API_BODY" | python3 -c '
import base64, json, sys
data = json.load(sys.stdin)
content = base64.b64decode(data.get("content", "")).decode("utf-8")
raise SystemExit(0 if content == "course fixture — safe to delete" else 1)
' 2>/dev/null
}

ensure_github_repo() {
  local name="$1"
  local temporary_directory repository_url payload
  require_github_env
  GITHUB_REPO_CREATED_BY_THIS_RUN=false

  gh_api GET "/repos/$GITHUB_USER/$name"
  if [ "$GH_API_STATUS" = '404' ]; then
    payload="$(NAME="$name" python3 -c \
      'import json, os; print(json.dumps({"name":os.environ["NAME"],"private":False,"auto_init":False}))')"
    gh_api POST '/user/repos' "$payload"
    [ "$GH_API_STATUS" = '201' ] \
      || die "สร้าง GitHub repository $GITHUB_USER/$name ไม่สำเร็จ (HTTP $GH_API_STATUS)"
    printf '%s' "$GH_API_BODY" | python3 -c \
      'import json,sys; d=json.load(sys.stdin); raise SystemExit(0 if not d.get("private", True) else 1)' \
      || die "GitHub repository $GITHUB_USER/$name ที่สร้างใหม่ไม่เป็น public"
    GITHUB_REPO_CREATED_BY_THIS_RUN=true
    step "created_by_this_run=true สำหรับ GitHub repository $GITHUB_USER/$name"

    temporary_directory="$(mktemp -d)" || die 'สร้าง working directory ชั่วคราวไม่สำเร็จ'
    trap 'rm -rf -- "$temporary_directory"' RETURN
    git -C "$temporary_directory" init -q -b main repo
    cp "$BOOTSTRAP_DIR/fixtures/hello-ci.Jenkinsfile" "$temporary_directory/repo/Jenkinsfile"
    cp "$BOOTSTRAP_DIR/fixtures/hello-ci.hello.sh" "$temporary_directory/repo/hello.sh"
    cp "$BOOTSTRAP_DIR/fixtures/hello-ci.expected.txt" "$temporary_directory/repo/expected.txt"
    printf '%s' 'course fixture — safe to delete' >"$temporary_directory/repo/.course-cicd2569"
    chmod +x "$temporary_directory/repo/hello.sh"
    git -C "$temporary_directory/repo" add .course-cicd2569 Jenkinsfile hello.sh expected.txt
    git -C "$temporary_directory/repo" \
      -c user.name=Student -c user.email=student@example.invalid \
      commit -q -m 'Create GitHub hello-ci course fixture'
    repository_url="https://github.com/$GITHUB_USER/$name.git"
    git -C "$temporary_directory/repo" remote add origin "$repository_url"
    github_git_with_askpass git -C "$temporary_directory/repo" push -q -u origin main \
      || die "push fixture ไปยัง $GITHUB_USER/$name ไม่สำเร็จ"
    rm -rf -- "$temporary_directory"
    trap - RETURN
  elif [ "$GH_API_STATUS" = '200' ]; then
    printf '%s' "$GH_API_BODY" | python3 -c \
      'import json,sys; d=json.load(sys.stdin); raise SystemExit(0 if not d.get("private", True) else 1)' \
      || die "GitHub repository $GITHUB_USER/$name มีอยู่แต่ไม่เป็น public"
    gh_api GET "/repos/$GITHUB_USER/$name/contents/.course-cicd2569?ref=main"
    if [ "$GH_API_STATUS" != '200' ] || ! github_marker_is_valid; then
      die "พบ repository $GITHUB_USER/$name แต่ไม่มี ownership marker ที่ถูกต้องบน main; ปิดการทำงานเพื่อความปลอดภัย กรุณา rename repository เดิมแล้วรันใหม่"
    fi
    step "created_by_this_run=false; ยืนยัน ownership marker ของ $GITHUB_USER/$name แล้ว"
  else
    die "ตรวจ GitHub repository $GITHUB_USER/$name ไม่สำเร็จ (HTTP $GH_API_STATUS)"
  fi

  gh_api GET "/repos/$GITHUB_USER/$name/contents/.course-cicd2569?ref=main"
  [ "$GH_API_STATUS" = '200' ] && github_marker_is_valid \
    || die "ownership marker ของ $GITHUB_USER/$name ไม่พร้อมหลัง converge"
}

put_github_job() {
  local name="$1"
  local template="$2"
  local rendered
  rendered="$(mktemp)" || die 'สร้างไฟล์ job XML ชั่วคราวไม่สำเร็จ'
  trap 'rm -f -- "$rendered"' RETURN
  sed "s/__GITHUB_USER__/${GITHUB_USER}/g" "$template" >"$rendered"
  grep -q '__GITHUB_USER__' "$rendered" \
    && die "render sentinel ใน $template ไม่ครบ"
  put_job "$name" "$rendered"
  rm -f -- "$rendered"
  trap - RETURN
}

push_github_probe() {
  local name="$1"
  local purpose="$2"
  local temporary_directory repository_url sha
  temporary_directory="$(mktemp -d)" || die 'สร้าง working directory สำหรับ probe ไม่สำเร็จ'
  trap 'rm -rf -- "$temporary_directory"' RETURN
  repository_url="https://github.com/$GITHUB_USER/$name.git"
  git clone -q --branch main --single-branch "$repository_url" "$temporary_directory/repo"
  printf 'probe %s %s\n' "$purpose" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    >>"$temporary_directory/repo/webhook-proof.txt"
  git -C "$temporary_directory/repo" add webhook-proof.txt
  git -C "$temporary_directory/repo" \
    -c user.name=Student -c user.email=student@example.invalid \
    commit -q -m "Verify $purpose bootstrap"
  sha="$(git -C "$temporary_directory/repo" rev-parse HEAD)"
  github_git_with_askpass git -C "$temporary_directory/repo" push -q origin main \
    || die "push $purpose probe ไปยัง $GITHUB_USER/$name ไม่สำเร็จ"
  rm -rf -- "$temporary_directory"
  trap - RETURN
  printf '%s\n' "$sha"
}

assert_build_contract() {
  local build_number="$1"
  local expected_sha="$2"
  local expected_cause="$3"
  local details console
  details="$(curl -gfsS -u "$JENKINS_AUTH" \
    "$JENKINS_URL/job/hello-ci-pipeline/$build_number/api/json?tree=result,building,actions[causes[shortDescription]]")"
  printf '%s' "$details" | python3 -c '
import json, sys
data = json.load(sys.stdin)
raise SystemExit(0 if data.get("result") == "SUCCESS" and not data.get("building", True) else 1)
' || die "hello-ci-pipeline build #$build_number ไม่สำเร็จ"
  grep -Fq "$expected_cause" <<<"$details" \
    || die "hello-ci-pipeline build #$build_number ไม่มี cause '$expected_cause'"
  console="$(curl -fsS -u "$JENKINS_AUTH" \
    "$JENKINS_URL/job/hello-ci-pipeline/$build_number/consoleText")"
  grep -Fq 'Hello from GitHub' <<<"$console" \
    || die "hello-ci-pipeline build #$build_number ไม่มีผลลัพธ์ Hello from GitHub"
  grep -Fq "$expected_sha" <<<"$console" \
    || die "hello-ci-pipeline build #$build_number checkout SHA ไม่ตรงกับ probe"
}

assert_bootstrap_tree_unchanged() {
  local current
  [ -n "$BOOTSTRAP_GIT_ROOT" ] || return 0
  current="$(git -C "$BOOTSTRAP_DIR" diff -- . | sha256sum | awk '{print $1}')"
  [ "$current" = "$BOOTSTRAP_DIFF_BASELINE" ] \
    || die 'มีไฟล์ใต้ tools/bootstrap ถูกแก้ระหว่าง render job XML'
  if git -C "$BOOTSTRAP_DIR" diff --quiet -- .; then
    git -C "$BOOTSTRAP_DIR" diff --exit-code -- .
  fi
  step 'ยืนยัน job template ไม่ถูกแก้ in-place'
}

ensure_lab4_state() {
  local baseline build_number probe_sha
  ensure_lab3_state
  step 'LAB 4: ตรวจ GitHub prerequisites และเตรียม public hello-ci fixture'
  require_github_env
  "$BOOTSTRAP_DIR/github_preflight.sh"
  ensure_github_repo hello-ci
  put_github_job hello-ci-pipeline "$BOOTSTRAP_DIR/jobs/hello-ci-poll.xml"

  baseline="$(job_last_number hello-ci-pipeline)"
  baseline="${baseline:-0}"
  probe_sha="$(push_github_probe hello-ci 'Poll SCM')"
  step "เรียก Poll SCM หลัง push probe (baseline #$baseline)"
  jenkins_post "$JENKINS_URL/job/hello-ci-pipeline/polling" >/dev/null
  build_number="$(wait_for_build_after hello-ci-pipeline "$baseline" 180)"
  assert_build_contract "$build_number" "$probe_sha" 'Started by an SCM change'
  step "LAB 4 verified build #$build_number: SCM cause, matching checkout SHA, Hello from GitHub"
  assert_bootstrap_tree_unchanged
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

validate_smee_channel() {
  local channel="$1"
  CHANNEL="$channel" python3 -c '
import os
from urllib.parse import urlsplit
url = urlsplit(os.environ["CHANNEL"])
ok = url.scheme == "https" and url.hostname == "smee.io" and bool(url.path.strip("/"))
ok = ok and url.path.count("/") == 1 and not url.query and not url.fragment
raise SystemExit(0 if ok else 1)
'
}

ensure_smee_channel() {
  local variable_name="$1"
  local channel='' headers relay candidate
  case "$variable_name" in
    SMEE_HELLO_URL) relay='smee-hello' ;;
    SMEE_WEBAPP_URL) relay='smee-webapp' ;;
    *) die 'ชื่อ env สำหรับ smee ต้องเป็น SMEE_HELLO_URL หรือ SMEE_WEBAPP_URL' ;;
  esac
  channel="${!variable_name:-}"
  if [ -n "$channel" ]; then
    validate_smee_channel "$channel" \
      || die "$variable_name ต้องมีรูปแบบ https://smee.io/<id>"
    step "$variable_name ใช้ channel ที่กำหนดไว้แล้ว: <SMEE_URL>"
    return 0
  fi

  if docker container inspect "$relay" >/dev/null 2>&1; then
    candidate="$(docker inspect -f '{{json .Config.Cmd}}' "$relay" | python3 -c '
import json, sys
args = json.load(sys.stdin)
try:
    print(args[args.index("--url") + 1])
except (ValueError, IndexError):
    pass
')"
    if [ -n "$candidate" ] && validate_smee_channel "$candidate"; then
      channel="$candidate"
    fi
  fi
  if [ -n "$channel" ]; then
    printf -v "$variable_name" '%s' "$channel"
    export "$variable_name"
    step "$variable_name กู้คืนจาก relay container เดิม: <SMEE_URL>"
    return 0
  fi

  headers="$(curl -sSI --max-time 30 'https://smee.io/new')" \
    || die 'ติดต่อ https://smee.io/new เพื่อสร้าง channel ไม่สำเร็จ'
  channel="$(printf '%s\n' "$headers" | awk '
    tolower($0) ~ /^location:/ {
      sub(/^[^:]*:[[:space:]]*/, "")
      sub(/\r$/, "")
      print
      exit
    }
  ')"
  [ -n "$channel" ] || die 'smee.io ไม่ส่ง Location header สำหรับ channel ใหม่'
  validate_smee_channel "$channel" \
    || die 'Location จาก smee.io ไม่ใช่ https://smee.io/<id> ที่ปลอดภัย'
  printf -v "$variable_name" '%s' "$channel"
  export "$variable_name"
  step "$variable_name สร้าง channel ใหม่: <SMEE_URL>"
}

ensure_smee_relay() {
  local name="$1"
  local channel="$2"
  local token="$3"
  local image target current_args current_image restart network relay_logs recreate=false i
  [[ "$name" =~ ^smee-(hello|webapp)$ ]] || die 'ชื่อ relay ต้องเป็น smee-hello หรือ smee-webapp'
  validate_smee_channel "$channel" || die 'smee channel สำหรับ relay มีรูปแบบไม่ถูกต้อง'
  image='deltaprojects/smee-client@sha256:20ea24c8c81bb3f3aa332c8939503e3c5bee048bb5a98ba2249d73a41a556e33'
  target="http://jenkins:8080/generic-webhook-trigger/invoke?token=$token"

  if docker container inspect "$name" >/dev/null 2>&1; then
    current_args="$(docker inspect -f '{{json .Config.Cmd}}' "$name")"
    current_image="$(docker inspect -f '{{.Config.Image}}' "$name")"
    restart="$(docker inspect -f '{{.HostConfig.RestartPolicy.Name}}' "$name")"
    network="$(docker inspect -f '{{if index .NetworkSettings.Networks "cicd-net"}}cicd-net{{end}}' "$name")"
    CURRENT_ARGS="$current_args" CHANNEL="$channel" TARGET="$target" python3 -c '
import json, os
actual = json.loads(os.environ["CURRENT_ARGS"])
expected = ["--url", os.environ["CHANNEL"], "--target", os.environ["TARGET"]]
raise SystemExit(0 if actual == expected else 1)
' || recreate=true
    [ "$current_image" = "$image" ] || recreate=true
    [ "$restart" = 'unless-stopped' ] || recreate=true
    [ "$network" = 'cicd-net' ] || recreate=true
    if [ "$recreate" = true ]; then
      step "$name args/config เปลี่ยน จึง recreate relay โดยคง URL เป็น <SMEE_URL>"
      docker rm -f "$name" >/dev/null
    else
      docker start "$name" >/dev/null
      step "$name ตรง contract แล้ว จึงคง container เดิม"
    fi
  fi
  if ! docker container inspect "$name" >/dev/null 2>&1; then
    docker run -d --name "$name" --restart unless-stopped --network cicd-net \
      "$image" --url "$channel" --target "$target" >/dev/null
    step "สร้าง $name บน cicd-net ด้วย channel <SMEE_URL>"
  fi

  for ((i = 1; i <= 90; i++)); do
    relay_logs="$(docker logs "$name" 2>&1 || true)"
    if grep -q 'Connected' <<<"$relay_logs"; then
      step "$name Connected"
      return 0
    fi
    sleep 2
  done
  die "$name ยังไม่ Connected ภายในเวลาที่กำหนด (ซ่อน channel id จาก log)"
}

assert_github_hook_json() {
  local channel="$1"
  CHANNEL="$channel" python3 -c '
import json, os, sys
hook = json.load(sys.stdin)
config = hook.get("config") or {}
ok = (
    hook.get("name") == "web"
    and hook.get("active") is True
    and hook.get("events") == ["push"]
    and config.get("url") == os.environ["CHANNEL"]
    and config.get("content_type") == "json"
    and str(config.get("insecure_ssl")) == "0"
)
raise SystemExit(0 if ok else 1)
'
}

ensure_github_hook() {
  local repo="$1"
  local channel="$2"
  local hook payload
  validate_smee_channel "$channel" || die 'GitHub hook channel มีรูปแบบไม่ถูกต้อง'
  gh_api GET "/repos/$GITHUB_USER/$repo/hooks?per_page=100"
  [ "$GH_API_STATUS" = '200' ] \
    || die "อ่าน GitHub hooks ของ $GITHUB_USER/$repo ไม่สำเร็จ (HTTP $GH_API_STATUS)"
  hook="$(CHANNEL="$channel" python3 -c '
import json, os, sys
for item in json.load(sys.stdin):
    if (item.get("config") or {}).get("url") == os.environ["CHANNEL"]:
        print(json.dumps(item))
        break
' <<<"$GH_API_BODY")"
  if [ -z "$hook" ]; then
    payload="$(CHANNEL="$channel" python3 -c '
import json, os
print(json.dumps({
  "name":"web", "active":True, "events":["push"],
  "config":{"url":os.environ["CHANNEL"], "content_type":"json", "insecure_ssl":"0"}
}))
')"
    gh_api POST "/repos/$GITHUB_USER/$repo/hooks" "$payload"
    [ "$GH_API_STATUS" = '201' ] \
      || die "สร้าง GitHub hook ของ $GITHUB_USER/$repo ไม่สำเร็จ (HTTP $GH_API_STATUS)"
    hook="$GH_API_BODY"
    step "สร้าง GitHub push hook ไปยัง <SMEE_URL>"
  else
    step "GitHub push hook ไปยัง <SMEE_URL> มีอยู่แล้ว"
  fi
  printf '%s' "$hook" | assert_github_hook_json "$channel" \
    || die 'GitHub hook fields ไม่ครบตาม contract (web/active/push/json/insecure_ssl=0)'
  GITHUB_HOOK_ID="$(printf '%s' "$hook" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("id", ""))')"
  [[ "$GITHUB_HOOK_ID" =~ ^[0-9]+$ ]] || die 'GitHub hook ไม่มี numeric id'
}

wait_for_github_delivery() {
  local repo="$1"
  local hook_id="$2"
  local expected_sha="$3"
  local i delivery_ids delivery_id
  for ((i = 1; i <= 60; i++)); do
    gh_api GET "/repos/$GITHUB_USER/$repo/hooks/$hook_id/deliveries?per_page=10"
    [ "$GH_API_STATUS" = '200' ] \
      || die "อ่าน GitHub hook deliveries ไม่สำเร็จ (HTTP $GH_API_STATUS)"
    delivery_ids="$(printf '%s' "$GH_API_BODY" | python3 -c '
import json, sys
for delivery in json.load(sys.stdin):
    if delivery.get("event") == "push":
        print(delivery.get("id", ""))
')"
    while IFS= read -r delivery_id; do
      [ -n "$delivery_id" ] || continue
      gh_api GET "/repos/$GITHUB_USER/$repo/hooks/$hook_id/deliveries/$delivery_id"
      if [ "$GH_API_STATUS" = '200' ] && EXPECTED_SHA="$expected_sha" python3 -c '
import json, os, sys
delivery = json.load(sys.stdin)
payload = ((delivery.get("request") or {}).get("payload") or {})
ok = delivery.get("event") == "push" and payload.get("after") == os.environ["EXPECTED_SHA"]
ok = ok and delivery.get("status_code") == 200
raise SystemExit(0 if ok else 1)
' <<<"$GH_API_BODY"; then
        step 'GitHub delivery event=push, after=<SHA>, status_code=200 ตรงกับ probe'
        return 0
      fi
    done <<<"$delivery_ids"
    sleep 2
  done
  die 'ไม่พบ GitHub push delivery ที่ after SHA ตรงกับ probe'
}

wait_for_relay_post_200() {
  local relay="$1"
  local since="$2"
  local i relay_logs
  for ((i = 1; i <= 60; i++)); do
    relay_logs="$(docker logs --since "$since" "$relay" 2>&1 || true)"
    if grep -Eq 'POST .*generic-webhook-trigger/invoke.* 200' <<<"$relay_logs"; then
      step "$relay มี POST ไป Jenkins และได้ HTTP 200 หลัง probe"
      return 0
    fi
    sleep 2
  done
  die "$relay ไม่มีหลักฐาน POST ไป Jenkins แล้วได้ HTTP 200 หลัง probe"
}

ensure_lab5_state() {
  local baseline after_ping build_number probe_sha probe_started final_number config
  ensure_lab4_state
  step 'LAB 5: ติดตั้ง GWT 2.4.2 และสลับจาก Poll SCM เป็น GitHub webhook'
  ensure_gwt_plugin
  put_github_job hello-ci-pipeline "$BOOTSTRAP_DIR/jobs/hello-ci-webhook.xml"
  ensure_smee_channel SMEE_HELLO_URL
  ensure_smee_relay smee-hello "$SMEE_HELLO_URL" cicd2569-hello

  baseline="$(job_last_number hello-ci-pipeline)"
  baseline="${baseline:-0}"
  ensure_github_hook hello-ci "$SMEE_HELLO_URL"
  step "ping acceptance: รอ 20 วินาทีจาก baseline #$baseline"
  sleep 20
  after_ping="$(job_last_number hello-ci-pipeline)"
  after_ping="${after_ping:-0}"
  [ "$after_ping" -eq "$baseline" ] \
    || die "GitHub ping ทำให้ build count เพิ่มจาก #$baseline เป็น #$after_ping"
  step 'ping ถูก filter: build count ไม่เพิ่ม'

  probe_started="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  probe_sha="$(push_github_probe hello-ci 'GitHub webhook')"
  build_number="$(wait_for_build_after hello-ci-pipeline "$baseline" 240)"
  [ "$build_number" -eq $((baseline + 1)) ] \
    || die "webhook probe ต้องสร้าง exactly one build ถัดจาก #$baseline"
  sleep 10
  final_number="$(job_last_number hello-ci-pipeline)"
  [ "$final_number" -eq "$build_number" ] \
    || die "webhook probe สร้างมากกว่าหนึ่ง build (#$build_number ถึง #$final_number)"
  assert_build_contract "$build_number" "$probe_sha" 'GitHub push'
  wait_for_github_delivery hello-ci "$GITHUB_HOOK_ID" "$probe_sha"
  wait_for_relay_post_200 smee-hello "$probe_started"

  config="$(curl -fsS -u "$JENKINS_AUTH" "$JENKINS_URL/job/hello-ci-pipeline/config.xml")"
  printf '%s' "$config" | grep -q '<token>cicd2569-hello</token>' \
    || die 'Jenkins webhook token หายไป'
  printf '%s' "$config" | grep -q '<key>ref</key>' \
    || die 'GWT generic variable ref หายไป'
  printf '%s' "$config" | grep -q '<key>after</key>' \
    || die 'GWT generic variable after หายไป'
  printf '%s' "$config" | grep -Fq '<regexpFilterText>$ref</regexpFilterText>' \
    || die 'GWT regexpFilterText ไม่ใช่ $ref'
  printf '%s' "$config" | grep -Fq '<regexpFilterExpression>^refs/heads/main$</regexpFilterExpression>' \
    || die 'GWT branch filter ไม่ตรง contract'
  if printf '%s' "$config" | grep -q '<hudson.triggers.SCMTrigger>'; then
    die 'Poll SCM ยังเปิดอยู่บน hello-ci-pipeline'
  fi
  step "LAB 5 verified exactly one GitHub webhook build #$build_number และ correlate SHA ครบทุก hop"
  step "GitHub API requests ใน run นี้: $GH_API_REQUEST_COUNT"
  assert_bootstrap_tree_unchanged
}
