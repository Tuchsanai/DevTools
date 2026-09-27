**4.3) อ่าน `Jenkinsfile` ทีละ stage ตามลำดับที่รัน**

โค้ดด้านล่างตัดมาจาก [`Jenkinsfile`](./Jenkinsfile) ตรงตัวทุกบรรทัด (เปิดไฟล์เพื่อดูฉบับเต็ม) · Jenkins อ่านไฟล์นี้จาก GitHub เองก่อนเริ่ม (ตาม Script Path ในข้อ 4.2)

**คำสั่งแต่ละส่วนรันที่เครื่องไหน** — จุดสำคัญที่สุดของไฟล์นี้:

| ส่วนของ `Jenkinsfile` | รันที่ | ตัวอย่าง |
|---|---|---|
| โค้ด Groovy ของ pipeline (`script { if ... }`, `error`, `echo`) | **Jenkins** | ตรวจ `APP_VERSION` ใน Connect, ข้อความใน `post` |
| บรรทัดใน `sh '...'` | shell บน **Jenkins** (`agent any` คือ node ของ Jenkins ในแล็บนี้) | `set +x`, `echo "$HUB_TOKEN" \|`, การแทนค่า `$IMAGE` ที่อยู่นอก heredoc |
| คำสั่งหลัง `$SSH_DEVTOOLS` และสคริปต์ใน `<<'EOF' ... EOF` | **devtools** (ปลายทาง SSH) | `git clone`, `docker build/run/push/pull`, `curl` |

**ตั้งค่าของ pipeline** — `agent any` ให้ Jenkins เลือก node ที่ว่างมารัน `sh` · `options` สองบรรทัดนี้จำเป็นต้องมี:

```groovy
  options {
    disableConcurrentBuilds()   // ทุก build ใช้โฟลเดอร์ ชื่อ container และ port 3000 เดียวกัน ห้ามรันซ้อน
    skipDefaultCheckout()       // Jenkins ไม่ต้อง checkout repo เอง devtools clone ใน stage Clone
  }
```

- `disableConcurrentBuilds()` ถ้ากด Build ซ้อนกัน build หนึ่งจะลบโฟลเดอร์ clone, ไฟล์ login หรือ container ของอีก build ทิ้ง
- `skipDefaultCheckout()` ไม่ให้ Jenkins clone repository ทั้งก้อนลง workspace ของตัวเองโดยไม่มีใครใช้ ซอร์สที่ build มีชุดเดียวคือที่ devtools clone

**parameter ของ job** — มีตัวเดียว:

```groovy
  parameters {
    string(name: 'APP_VERSION', defaultValue: '1.0.0', description: 'เวอร์ชันรูปแบบ X.Y.Z ที่แสดงบนหน้าเว็บ')
  }
```

- build แรกใช้ค่า default `1.0.0` · Jenkins จะรู้จัก parameter นี้หลังอ่านไฟล์ครั้งแรก เมนู **Build with Parameters** จึงมาหลังรันครั้งแรก (ข้อ 6)
- ใน `sh` ค่านี้อ่านเป็นตัวแปร shell `$APP_VERSION` ได้ เช่นเดียวกับ `$BUILD_NUMBER` ที่ Jenkins ตั้งให้ทุก build

**ค่าที่ทุก stage ใช้ร่วมกัน** — `environment` มีแค่สามค่า ค่าอื่น (URL ของ repo, path ของโฟลเดอร์) เขียนตรง ๆ ในจุดที่ใช้:

```groovy
  environment {
    // accept-new: จำ host key ของ devtools ครั้งแรก ถ้าเปลี่ยนภายหลังจะปฏิเสธ · BatchMode: ไม่ถามรหัสผ่าน
    SSH_DEVTOOLS = 'ssh -o StrictHostKeyChecking=accept-new -o BatchMode=yes root@devtools'
    AUTH_DIR     = '/root/lab3-work/docker-auth'   // ไฟล์ login Docker Hub ชั่วคราวบน devtools
    IMAGE        = "catfood-shop:lab3-${env.BUILD_NUMBER}"
  }
```

- `SSH_DEVTOOLS` คือคำสั่ง SSH เข้า `root@devtools` · `accept-new` ให้ SSH จำ host key ของ devtools เองตอนต่อครั้งแรก และปฏิเสธถ้า key เปลี่ยนภายหลัง · `BatchMode=yes` ห้ามถามรหัสผ่าน key ใช้ไม่ได้ก็ล้มทันที
- `AUTH_DIR` คือโฟลเดอร์**บน devtools** ที่ `docker --config` เก็บไฟล์ login Docker Hub ชั่วคราว (ไม่ใช้ไฟล์ login ปกติของ root) · `post` ลบทิ้งตอนจบ
- `IMAGE` คือชื่อ image ในเครื่อง `catfood-shop:lab3-<เลข build>` ส่วนชื่อบน Docker Hub คือ `$HUB_USER/$IMAGE`
- ทุก stage (และ `post`) ห่อคำสั่งด้วย `sshagent(credentials: ['devtools-ssh']) { ... }` ให้ `ssh` บน Jenkins ใช้ private key จาก credential `devtools-ssh` (ข้อ 3.1) โดยไม่ต้องเขียน key ลงไฟล์ใน `Jenkinsfile`
- รูปแบบ `$SSH_DEVTOOLS "A=... bash -ex" <<'EOF' ... EOF` ส่งสคริปต์หลายบรรทัดไปรัน**บน devtools** (`-e` หยุดเมื่อคำสั่งใดล้ม `-x` พิมพ์คำสั่งลง console) · `.stripIndent()` ตัดช่องว่างหน้าบรรทัดออกก่อนรัน โค้ดจึงย่อหน้าตามโครงได้ และ `EOF` ตัวปิดยังอยู่ต้นบรรทัดตามที่ shell ต้องการ
- **ใครแทนค่าตัวแปร:** `'''...'''` เป็น string แบบ single quote ของ Groovy Groovy จึงไม่แทนค่า `$...` เอง · shell บน Jenkins แทนค่าตัวแปรที่อยู่**นอก** heredoc เช่น `"IMAGE=$IMAGE APP_VERSION=$APP_VERSION ..."` แล้วส่งค่าที่ได้ไปเป็นตัวแปรนำหน้า `bash` บน devtools · ส่วน `<<'EOF'` มี quote ทำให้ shell บน Jenkins **ไม่**แทนค่าในสคริปต์ ข้อความส่งไปตรงตัว แล้ว bash บน devtools แทนค่า `$IMAGE`, `$(git rev-parse ...)`, `$(date ...)` เอง

**Stage 1 — Connect**

```groovy
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
```

1. **บน Jenkins:** บล็อก `script` ใช้ `==~` (ต้องตรงรูปแบบทั้งข้อความ) ตรวจว่า `APP_VERSION` เป็น `X.Y.Z` ถ้าไม่ตรง `error` หยุด build ทันทีโดยยังไม่ SSH · ค่านี้ถูกส่งเข้า shell บน devtools การตรวจนี้จึงกันการแทรกคำสั่ง
2. **Jenkins → devtools:** `sh` รัน `ssh` บน Jenkins ด้วย private key จาก `sshagent` ส่งคำสั่งในเครื่องหมาย `"..."` ไปรัน**บน devtools**: `hostname`, `whoami`, `docker --version`, `git --version` เพื่อยืนยันว่าต่อได้ เป็น `root` และมี Docker/git พร้อม (ครั้งแรก SSH จะจำ host key ของ devtools ไว้ตรงนี้)

**Stage 2 — Clone** (ใน `sshagent` เหมือน Connect)

```groovy
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
```

Jenkins แค่ส่งสคริปต์ทาง SSH · ทุกบรรทัดในสคริปต์รัน**ข้างใน devtools** (stage นี้ไม่ต้องส่งตัวแปร จึงเป็น `bash -ex` เฉย ๆ):

- `rm -rf` ลบโฟลเดอร์ clone ของ build ก่อน ให้เริ่มจากซอร์สใหม่ทุกครั้ง
- `git clone --depth 1 --filter=blob:none --sparse` ดึงเฉพาะ commit ล่าสุดของ branch เริ่มต้นบน GitHub โดยยังไม่โหลดไฟล์ทั้ง repo · `git sparse-checkout set ...` เลือกให้มีเฉพาะโฟลเดอร์ `catfood-shop`
- `git log -1 --oneline` และ `ls` แสดง commit ที่ได้และรายชื่อไฟล์ใน console เป็นหลักฐานว่า clone อะไรมา
- หมายเหตุ: stage นี้ clone ใหม่เอง ไม่ได้ใช้ commit เดียวกับที่ Jenkins อ่าน `Jenkinsfile` ถ้ามี commit ใหม่เข้ามาระหว่างนั้น สองฝั่งอาจเป็นคนละ commit

**Stage 3 — Build**

```groovy
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
```

shell บน Jenkins แทนค่า `IMAGE`, `APP_VERSION`, `BUILD_NUMBER` แล้วส่งไปเป็นตัวแปรของ bash บน devtools · สคริปต์ที่เหลือรัน**บน devtools**: `cd` เข้าโฟลเดอร์ `catfood-shop` ที่เพิ่ง clone → `git rev-parse --short HEAD` อ่าน commit → `docker build` ด้วย Docker ของ devtools เป็น image `catfood-shop:lab3-<เลข build>` โดยส่ง `--build-arg` สี่ตัว (เวอร์ชัน, เลข build, commit, เวลา UTC) ที่ `Dockerfile` เก็บเป็น environment ใน image ให้ `/api/health` อ่านตอนรัน → `docker image ls` แสดง image ที่ได้ · image นี้อยู่ใน devtools เท่านั้น ยังไม่ขึ้น Docker Hub

**Stage 4 — Test**

```groovy
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
```

ส่งตัวแปรแบบเดียวกับ Build · ทุกคำสั่งรัน**บน devtools**:

1. `docker rm -f catfood-test || true` ลบ container ทดสอบที่อาจค้างจากรอบก่อน (`|| true` ไม่ให้ล้มถ้าไม่มี)
2. `docker run -d --name catfood-test "$IMAGE"` รัน image ใหม่แบบไม่เปิด port ออกนอก container · `trap ... EXIT` ลบ container นี้เสมอเมื่อสคริปต์จบ แม้ test ไม่ผ่าน
3. ลูป `for` ถาม `docker inspect` ทุก 1 วินาที สูงสุด 30 รอบ จนสถานะ `HEALTHCHECK` (ที่ประกาศใน `Dockerfile`) เป็น `healthy` · ถ้าครบ 30 รอบแล้วยังไม่ healthy ลูปจะจบเฉย ๆ ไม่ทำให้ stage ล้ม ตัวตัดสินคือขั้นถัดไป
4. `docker exec catfood-test wget ...` เรียก `/api/health` **จากข้างใน container** (เพราะไม่ได้เปิด port) → `tr -d '"'` ตัดเครื่องหมายคำพูดของ JSON → `grep -F` ต้องเจอ `version:<APP_VERSION>,build:<เลข build>,` ถ้าไม่เจอ `grep` คืนค่าผิดพลาด `bash -e` จึงหยุด และ stage Test ล้ม

**Stage 5 — Push**

```groovy
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
```

`withCredentials` ดึง username/token จาก credential `dockerhub` · token ส่งทาง stdin เข้า `--password-stdin` และ `set +x` ปิดการพิมพ์คำสั่งบรรทัดนั้น token จึงไม่อยู่ใน command line หรือ console · ไฟล์ login เก็บใน `AUTH_DIR` บน devtools (`umask 077` ให้ root อ่านได้คนเดียว) · จากนั้น tag เป็น `<DOCKER_USER>/catfood-shop:lab3-<เลข build>` แล้ว push ขึ้น Docker Hub · stage นี้เป็นคำสั่งเดี่ยวจึงส่งตรงทีละบรรทัด ไม่ต้องใช้ `<<'EOF'`

**Stage 6 — Deploy** (ใน `withCredentials` + `sshagent` เหมือน Push)

```groovy
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
```

ใช้ไฟล์ login เดิมจาก Push (บน devtools `IMAGE` คือชื่อเต็มบน Docker Hub) ลบ image ในเครื่องแล้ว **pull จาก Docker Hub** เพื่อพิสูจน์ว่า image บน Hub ใช้ได้จริง → ลบ `catfood-web` ตัวเดิม → รันตัวใหม่ที่ port `3000` → รอ `healthy` แล้ว `curl` ต้องได้เวอร์ชันและ build ตรง (ช่วงสั้น ๆ ระหว่างสลับ container ร้านจะปิดชั่วคราว)

**หลังจบทุก stage** — `post` บอก URL ของร้าน และลบไฟล์ login ใน `AUTH_DIR` เสมอ ทั้งตอนสำเร็จและตอน build หยุดกลางทาง:

```groovy
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
```

หลัง stage **Deploy** เขียว (และ `post` ลบไฟล์ login แล้ว) ให้เปิด **[ร้าน Meow Mart บนเครื่อง lab ของเรา — http://localhost:3000](http://localhost:3000)** ในเบราว์เซอร์ของเครื่องที่รัน container `devtools` (ลิงก์ใช้ได้เฉพาะหลัง Deploy สำเร็จ) แล้วตรวจ chip บนแถบด้านบนว่าตรงกับ `APP_VERSION` และเลข build ที่เพิ่งรัน หน้าร้านจะมีลักษณะแบบนี้:

[![หน้าร้าน Meow Mart (ภาพเดิม)](./images/lab3_sib_app_v110_crop.png)](./images/lab3_sib_app_v110.png)

*ภาพที่ 10 🕰️ **ภาพเดิม — ตัวอย่างผลลัพธ์จากการรันจริงรอบก่อน** (2026-09-26, workflow รุ่นก่อน, ซอร์สร้านเดียวกัน) chip แสดง `v1.1.0 · build #2` · ภาพตัดเฉพาะหน้าเว็บ ไม่มีแถบ URL ของเบราว์เซอร์ · ใช้ดูหน้าตาร้านเท่านั้น **ไม่ใช่ผลยืนยันของ `Jenkinsfile` ฉบับนี้** ซึ่งยังไม่ได้รันจริงบน Jenkins · build แรกของเราต้องเห็น `v1.0.0 · build #1`*

