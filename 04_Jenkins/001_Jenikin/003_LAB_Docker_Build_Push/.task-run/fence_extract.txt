// LAB 3 — Jenkins สั่ง devtools ผ่าน SSH ด้วย key: Connect → Clone → Build → Test → Push → Deploy
// ต้องมี: plugin "SSH Agent" · credential devtools-ssh (SSH key) และ dockerhub (username + token)
// ทุกคำสั่ง git/docker รันบน devtools: Jenkins แค่ส่งคำสั่งไปทาง SSH

pipeline {
  agent any

  options {
    disableConcurrentBuilds()   // ทุก build ใช้โฟลเดอร์ ชื่อ container และ port 3000 เดียวกัน ห้ามรันซ้อน
    skipDefaultCheckout()       // Jenkins ไม่ต้อง checkout repo เอง devtools clone ใน stage Clone
  }

  parameters {
    string(name: 'APP_VERSION', defaultValue: '1.0.0', description: 'เวอร์ชันรูปแบบ X.Y.Z ที่แสดงบนหน้าเว็บ')
  }

  environment {
    // accept-new: จำ host key ของ devtools ครั้งแรก ถ้าเปลี่ยนภายหลังจะปฏิเสธ · BatchMode: ไม่ถามรหัสผ่าน
    SSH_DEVTOOLS = 'ssh -o StrictHostKeyChecking=accept-new -o BatchMode=yes root@devtools'
    AUTH_DIR     = '/root/lab3-work/docker-auth'   // ไฟล์ login Docker Hub ชั่วคราวบน devtools
    IMAGE        = "catfood-shop:lab3-${env.BUILD_NUMBER}"
    // build แรก (Build Now) Jenkins ยังไม่รู้จัก parameter จึงไม่ส่ง $APP_VERSION ให้ sh: กำหนดจาก params เอง
    APP_VERSION  = "${params.APP_VERSION}"
  }

  stages {
    stage('Connect') {
      steps {
        script {
          // ค่านี้ถูกส่งต่อเข้า shell บน devtools จึงต้องเป็นตัวเลขกับจุดเท่านั้น
          if (!(params.APP_VERSION ==~ /[0-9]+\.[0-9]+\.[0-9]+/)) {
            error 'APP_VERSION ต้องเป็นรูปแบบ X.Y.Z เช่น 1.0.0'
          }
        }
        sshagent(credentials: ['devtools-ssh']) {
          sh '$SSH_DEVTOOLS "hostname && whoami && docker --version && git --version"'
        }
      }
    }

    stage('Clone') {
      steps {
        sshagent(credentials: ['devtools-ssh']) {
          sh '''
            $SSH_DEVTOOLS bash -ex <<'EOF'
              rm -rf /root/lab3-work/DevTools
              git clone --depth 1 --filter=blob:none --sparse \
                https://github.com/Tuchsanai/DevTools.git /root/lab3-work/DevTools
              cd /root/lab3-work/DevTools
              git sparse-checkout set 04_Jenkins/001_Jenikin/003_LAB_Docker_Build_Push/catfood-shop
              git log -1 --oneline
              ls 04_Jenkins/001_Jenikin/003_LAB_Docker_Build_Push/catfood-shop
            EOF
            '''.stripIndent()
        }
      }
    }

    stage('Build') {
      steps {
        sshagent(credentials: ['devtools-ssh']) {
          sh '''
            $SSH_DEVTOOLS "IMAGE=$IMAGE APP_VERSION=$APP_VERSION BUILD_NUMBER=$BUILD_NUMBER bash -ex" <<'EOF'
              cd /root/lab3-work/DevTools/04_Jenkins/001_Jenikin/003_LAB_Docker_Build_Push/catfood-shop
              COMMIT=$(git rev-parse --short HEAD)
              docker build \
                --build-arg APP_VERSION="$APP_VERSION" \
                --build-arg BUILD_NUMBER="$BUILD_NUMBER" \
                --build-arg GIT_COMMIT="$COMMIT" \
                --build-arg BUILD_TIME="$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
                -t "$IMAGE" .
              docker image ls "$IMAGE"
            EOF
            '''.stripIndent()
        }
      }
    }

    stage('Test') {
      steps {
        sshagent(credentials: ['devtools-ssh']) {
          sh '''
            $SSH_DEVTOOLS "IMAGE=$IMAGE APP_VERSION=$APP_VERSION BUILD_NUMBER=$BUILD_NUMBER bash -ex" <<'EOF'
              docker rm -f catfood-test || true
              docker run -d --name catfood-test "$IMAGE"
              trap 'docker rm -f catfood-test' EXIT   # ลบ container ทดสอบเสมอ แม้ test ไม่ผ่าน
              for i in $(seq 1 30); do
                [ "$(docker inspect -f '{{.State.Health.Status}}' catfood-test)" = healthy ] && break
                sleep 1
              done
              docker exec catfood-test wget -qO- http://127.0.0.1:3000/api/health |
                tr -d '"' | grep -F "version:$APP_VERSION,build:$BUILD_NUMBER,"
            EOF
            '''.stripIndent()
        }
      }
    }

    stage('Push') {
      steps {
        withCredentials([usernamePassword(credentialsId: 'dockerhub',
                         usernameVariable: 'HUB_USER', passwordVariable: 'HUB_TOKEN')]) {
          sshagent(credentials: ['devtools-ssh']) {
            // token ส่งทาง stdin เข้า --password-stdin: ไม่อยู่ใน command line และ console
            sh '''
              set +x
              echo "$HUB_TOKEN" | $SSH_DEVTOOLS "umask 077; docker --config $AUTH_DIR login -u $HUB_USER --password-stdin"
              set -x
              $SSH_DEVTOOLS docker tag $IMAGE $HUB_USER/$IMAGE
              $SSH_DEVTOOLS docker --config $AUTH_DIR push $HUB_USER/$IMAGE
              $SSH_DEVTOOLS docker image rm $IMAGE
              '''.stripIndent()
          }
        }
      }
    }

    stage('Deploy') {
      steps {
        // ใช้ HUB_USER ตั้งชื่อ image และใช้ไฟล์ login จาก stage Push (post ลบให้ตอนจบ)
        withCredentials([usernamePassword(credentialsId: 'dockerhub',
                         usernameVariable: 'HUB_USER', passwordVariable: 'HUB_TOKEN')]) {
          sshagent(credentials: ['devtools-ssh']) {
            sh '''
              $SSH_DEVTOOLS "AUTH_DIR=$AUTH_DIR IMAGE=$HUB_USER/$IMAGE APP_VERSION=$APP_VERSION BUILD_NUMBER=$BUILD_NUMBER bash -ex" <<'EOF'
                docker image rm "$IMAGE"                  # ลบ image ในเครื่อง เพื่อให้ pull มาจาก Docker Hub จริง
                docker --config "$AUTH_DIR" pull "$IMAGE"
                docker rm -f catfood-web || true          # ลบร้านเวอร์ชันเดิม
                docker run -d --name catfood-web --restart unless-stopped -p 3000:3000 "$IMAGE"
                for i in $(seq 1 30); do
                  [ "$(docker inspect -f '{{.State.Health.Status}}' catfood-web)" = healthy ] && break
                  sleep 1
                done
                curl -fsS http://localhost:3000/api/health |
                  tr -d '"' | grep -F "version:$APP_VERSION,build:$BUILD_NUMBER,"
              EOF
              '''.stripIndent()
          }
        }
      }
    }
  }

  post {
    success {
      echo "เปิดร้านได้ที่ http://localhost:3000 (v${params.APP_VERSION} build #${env.BUILD_NUMBER})"
    }
    always {
      // ลบไฟล์ login Docker Hub บน devtools เสมอ ทั้งตอนสำเร็จและตอน build ล้มกลางทาง
      sshagent(credentials: ['devtools-ssh']) {
        sh '$SSH_DEVTOOLS "rm -rf $AUTH_DIR" || true'
      }
    }
  }
}
