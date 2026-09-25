// LAB 4 — Jenkins อ่าน Jenkinsfile จาก GitHub แล้วส่งซอร์สไปให้ devtools build/push/deploy ผ่าน SSH
pipeline {
  agent any

  environment {
    SSH_KEY     = credentials('devtools-ssh')     // private key เดียวกับ LAB 3
    DEVTOOLS    = 'root@devtools'
    SSH_OPTS    = '-o StrictHostKeyChecking=accept-new -o LogLevel=ERROR'
    BUILD_DIR   = '/tmp/hello-ci-build'            // โฟลเดอร์บน devtools ที่รับซอร์สของ build นี้
    IMAGE       = 'hello-ci'                       // ชื่อ image และ repository บน Docker Hub
    DEPLOY_NAME = 'catfood-web'                    // container ของร้าน (port 3000)
  }

  stages {
    stage('Check source') {
      steps {
        echo 'ตรวจ source ที่ Jenkins checkout มาจาก GitHub'
        sh '''
          git log -1 --format='commit %h : %s'
          test -f Dockerfile
          test -f package-lock.json
          test -f data/products.js
        '''
      }
    }

    stage('Send source to devtools') {
      steps {
        // ส่งไฟล์ของ commit นี้ (ไม่รวม .git) ไปให้ devtools ทาง SSH
        sh '''
          tar czf - --exclude=.git . | ssh -i "$SSH_KEY" $SSH_OPTS "$DEVTOOLS" \
            "rm -rf $BUILD_DIR && mkdir -p $BUILD_DIR && tar xzf - -C $BUILD_DIR && ls $BUILD_DIR"
        '''
      }
    }

    stage('Build image') {
      steps {
        sh '''
          VERSION=$(sed -n 's/.*"version": *"\\([^"]*\\)".*/\\1/p' package.json | head -1)
          COMMIT=$(git rev-parse --short HEAD)
          ssh -i "$SSH_KEY" $SSH_OPTS "$DEVTOOLS" \
            "DIR=$BUILD_DIR IMG=$IMAGE:$BUILD_NUMBER VERSION=$VERSION BUILD=$BUILD_NUMBER COMMIT=$COMMIT bash -s" <<'EOF'
set -e
cd "$DIR"
docker build --provenance=false \
  --build-arg APP_VERSION="$VERSION" \
  --build-arg BUILD_NUMBER="$BUILD" \
  --build-arg GIT_COMMIT="$COMMIT" \
  --build-arg BUILD_TIME="$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  -t "$IMG" .
EOF
        '''
      }
    }

    stage('Test image') {
      steps {
        sh '''
          COMMIT=$(git rev-parse --short HEAD)
          ssh -i "$SSH_KEY" $SSH_OPTS "$DEVTOOLS" \
            "IMG=$IMAGE:$BUILD_NUMBER NAME=hello-ci-test-$BUILD_NUMBER COMMIT=$COMMIT bash -s" <<'EOF'
docker run -d --name "$NAME" "$IMG" >/dev/null
for i in $(seq 1 30); do
  STATUS=$(docker inspect -f '{{.State.Health.Status}}' "$NAME")
  echo "health of $NAME: $STATUS"
  [ "$STATUS" = healthy ] && break
  sleep 1
done
docker inspect -f '{{range .Config.Env}}{{println .}}{{end}}' "$NAME" | grep -E '^(APP_VERSION|BUILD_NUMBER|GIT_COMMIT)='
docker rm -f "$NAME" >/dev/null
[ "$STATUS" = healthy ] && docker image inspect -f '{{range .Config.Env}}{{println .}}{{end}}' "$IMG" | grep -qx "GIT_COMMIT=$COMMIT"
EOF
        '''
      }
    }

    stage('Push image') {
      steps {
        withCredentials([usernamePassword(credentialsId: 'dockerhub',
            usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_TOKEN')]) {
          sh '''set +x
            echo "$DOCKER_TOKEN" | ssh -i "$SSH_KEY" $SSH_OPTS "$DEVTOOLS" \
              "DOCKER_CONFIG=/tmp/jenkins-docker-$BUILD_NUMBER docker login -u $DOCKER_USER --password-stdin"
            ssh -i "$SSH_KEY" $SSH_OPTS "$DEVTOOLS" \
              "IMG=$IMAGE:$BUILD_NUMBER HUB=docker.io/$DOCKER_USER/$IMAGE BUILD=$BUILD_NUMBER bash -s" <<'EOF'
export DOCKER_CONFIG=/tmp/jenkins-docker-$BUILD
trap 'docker logout >/dev/null 2>&1; rm -rf "$DOCKER_CONFIG"' EXIT
for tag in "$BUILD" latest; do
  docker tag "$IMG" "$HUB:$tag"
  docker push "$HUB:$tag"
done
EOF
          '''
        }
      }
    }

    stage('Deploy') {
      steps {
        withCredentials([usernamePassword(credentialsId: 'dockerhub',
            usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_TOKEN')]) {
          sh '''
            ssh -i "$SSH_KEY" $SSH_OPTS "$DEVTOOLS" \
              "HUB=docker.io/$DOCKER_USER/$IMAGE BUILD=$BUILD_NUMBER NAME=$DEPLOY_NAME bash -s" <<'EOF'
set -e
docker pull "$HUB:$BUILD"
docker rm -f "$NAME" 2>/dev/null || true
docker run -d --name "$NAME" --restart unless-stopped -p 3000:3000 "$HUB:$BUILD"
for i in $(seq 1 30); do
  STATUS=$(docker inspect -f '{{.State.Health.Status}}' "$NAME")
  echo "health of $NAME: $STATUS"
  [ "$STATUS" = healthy ] && break
  sleep 1
done
[ "$STATUS" = healthy ]
EOF
          '''
        }
      }
    }
  }

  post {
    success {
      echo "ร้านอัปเดตแล้ว: http://localhost:3000 (build #${env.BUILD_NUMBER}, commit ${env.GIT_COMMIT.substring(0, 7)})"
    }
  }
}
