**4.3) อ่าน `Jenkinsfile` ทั้งไฟล์ แล้วดูคำอธิบายทีละส่วน**

โค้ดด้านล่างคือ [`Jenkinsfile`](./Jenkinsfile) **ทั้งไฟล์ ตรงตัวทุกบรรทัด** · Jenkins อ่านไฟล์นี้จาก GitHub เองก่อนเริ่ม (ตาม Script Path ในข้อ 4.2) · คำอธิบายภาษาไทยของแต่ละส่วนอยู่ถัดจากโค้ด เรียงตามลำดับบนลงล่างของไฟล์

@@JENKINSFILE@@

**คำสั่งแต่ละส่วนรันที่เครื่องไหน** — จุดสำคัญที่สุดของไฟล์นี้:

| ส่วนของ `Jenkinsfile` | รันที่ | ตัวอย่าง |
|---|---|---|
| โค้ด Groovy ของ pipeline (`script { if ... }`, `error`, `echo`, `"${params...}"`) | **Jenkins** | ตรวจ `APP_VERSION` ใน Connect, ข้อความใน `post` |
| บรรทัดใน `sh '...'` | shell บน **Jenkins** (`agent any` คือ node ของ Jenkins ในแล็บนี้) | `set +x`, `echo "$HUB_TOKEN" \|`, การแทนค่า `$IMAGE` ที่อยู่นอก heredoc |
| คำสั่งหลัง `$SSH_DEVTOOLS` และสคริปต์ใน `<<'EOF' ... EOF` | **devtools** (ปลายทาง SSH) | `git clone`, `docker build/run/push/pull`, `curl` |

**ส่วนหัว (comment 3 บรรทัดแรก)** — บรรทัดที่ขึ้นต้นด้วย `//` เป็น comment Jenkins ไม่รัน · บอกลำดับ 6 stage, สิ่งที่ต้องเตรียมก่อน (plugin **SSH Agent** จากข้อ 2.7 และ credential `devtools-ssh`, `dockerhub` จากขั้นที่ 3) และหลักของแล็บว่าคำสั่ง git/docker ทุกคำสั่งรันบน devtools

**`pipeline { agent any ... }`** — `pipeline` คือบล็อกนอกสุดของ Declarative Pipeline ทุกส่วนต้องอยู่ข้างใน · `agent any` ให้ Jenkins เลือก node ที่ว่างมารัน `sh` ในแล็บนี้มีแค่ตัว Jenkins เอง คำสั่ง `ssh` จึงออกจาก container `jenkins`

**`options`** — สองบรรทัดนี้จำเป็นต้องมี:

- `disableConcurrentBuilds()` ถ้ากด Build ซ้อนกัน build หนึ่งจะลบโฟลเดอร์ clone, ไฟล์ login หรือ container ของอีก build ทิ้ง จึงให้รอคิวทีละ build
- `skipDefaultCheckout()` ไม่ให้ Jenkins clone repository ทั้งก้อนลง workspace ของตัวเองโดยไม่มีใครใช้ ซอร์สที่ build มีชุดเดียวคือที่ devtools clone ใน stage Clone

**`parameters`** — มีตัวเดียวคือ `APP_VERSION` ชนิด `string` ค่า default `1.0.0` · Jenkins จะรู้จัก parameter นี้หลังอ่านไฟล์ครั้งแรก เมนู **Build with Parameters** จึงมาหลังรันครั้งแรก (ข้อ 6) · ในโค้ด Groovy อ่านค่าได้ที่ `params.APP_VERSION`

**`environment`** — ค่าที่ทุก stage ใช้ร่วมกัน มีสี่ค่า ค่าอื่น (URL ของ repo, path ของโฟลเดอร์) เขียนตรง ๆ ในจุดที่ใช้ · ค่าในบล็อกนี้กลายเป็นตัวแปร shell ใน `sh` ทุกตัว:

- `SSH_DEVTOOLS` คือคำสั่ง SSH เข้า `root@devtools` · `accept-new` ให้ SSH จำ host key ของ devtools เองตอนต่อครั้งแรก และปฏิเสธถ้า key เปลี่ยนภายหลัง · `BatchMode=yes` ห้ามถามรหัสผ่าน key ใช้ไม่ได้ก็ล้มทันที
- `AUTH_DIR` คือโฟลเดอร์**บน devtools** ที่ `docker --config` เก็บไฟล์ login Docker Hub ชั่วคราว (ไม่ใช้ไฟล์ login ปกติของ root) · `post` ลบทิ้งตอนจบ
- `IMAGE` คือชื่อ image ในเครื่อง `catfood-shop:lab3-<เลข build>` (`${env.BUILD_NUMBER}` คือเลข build ที่ Jenkins ตั้งให้) ส่วนชื่อบน Docker Hub คือ `$HUB_USER/$IMAGE`
- `APP_VERSION = "${params.APP_VERSION}"` ส่งค่า parameter ให้ `sh` เป็น `$APP_VERSION` **ทุก build รวมถึง build แรก** · ตอนกด **Build Now** ครั้งแรก job ยังไม่มี parameter Jenkins จึงไม่ตั้งตัวแปร `$APP_VERSION` ให้ `sh` เอง (แม้ `params.APP_VERSION` ใน Groovy จะได้ค่า default `1.0.0`) · ถ้าไม่มีบรรทัดนี้ build แรกจะส่ง `APP_VERSION=` ค่าว่างไปที่ devtools และ stage Test ล้มเพราะหา `version:,build:1,` ไม่เจอ (เจอจริงตอนทดสอบแล็บ)

รูปแบบที่ทุก stage ใช้ซ้ำ:

- ทุก stage (และ `post`) ห่อคำสั่งด้วย `sshagent(credentials: ['devtools-ssh']) { ... }` ให้ `ssh` บน Jenkins ใช้ private key จาก credential `devtools-ssh` (ข้อ 3.1) โดยไม่ต้องเขียน key ลงไฟล์ใน `Jenkinsfile` · console จะแสดง `[ssh-agent] Started.` ตอนเข้า และ `[ssh-agent] Stopped.` ตอนออกจากบล็อก
- รูปแบบ `$SSH_DEVTOOLS "A=... bash -ex" <<'EOF' ... EOF` ส่งสคริปต์หลายบรรทัดไปรัน**บน devtools** (`-e` หยุดเมื่อคำสั่งใดล้ม `-x` พิมพ์คำสั่งลง console) · `.stripIndent()` ตัดช่องว่างหน้าบรรทัดออกก่อนรัน โค้ดจึงย่อหน้าตามโครงได้ และ `EOF` ตัวปิดยังอยู่ต้นบรรทัดตามที่ shell ต้องการ
- **ใครแทนค่าตัวแปร:** `'''...'''` เป็น string แบบ single quote ของ Groovy Groovy จึงไม่แทนค่า `$...` เอง · shell บน Jenkins แทนค่าตัวแปรที่อยู่**นอก** heredoc เช่น `"IMAGE=$IMAGE APP_VERSION=$APP_VERSION ..."` แล้วส่งค่าที่ได้ไปเป็นตัวแปรนำหน้า `bash` บน devtools · ส่วน `<<'EOF'` มี quote ทำให้ shell บน Jenkins **ไม่**แทนค่าในสคริปต์ ข้อความส่งไปตรงตัว แล้ว bash บน devtools แทนค่า `$IMAGE`, `$(git rev-parse ...)`, `$(date ...)` เอง

**Stage 1 — Connect**

1. **บน Jenkins:** บล็อก `script` ใช้ `==~` (ต้องตรงรูปแบบทั้งข้อความ) ตรวจว่า `params.APP_VERSION` เป็น `X.Y.Z` ถ้าไม่ตรง `error` หยุด build ทันทีโดยยังไม่ SSH · ค่านี้ถูกส่งเข้า shell บน devtools การตรวจนี้จึงกันการแทรกคำสั่ง
2. **Jenkins → devtools:** `sh` รัน `ssh` บน Jenkins ด้วย private key จาก `sshagent` ส่งคำสั่งในเครื่องหมาย `"..."` ไปรัน**บน devtools**: `hostname`, `whoami`, `docker --version`, `git --version` เพื่อยืนยันว่าต่อได้ เป็น `root` และมี Docker/git พร้อม (ครั้งแรก SSH จะจำ host key ของ devtools ไว้ตรงนี้)

**Stage 2 — Clone** — Jenkins แค่ส่งสคริปต์ทาง SSH · ทุกบรรทัดในสคริปต์รัน**ข้างใน devtools** (stage นี้ไม่ต้องส่งตัวแปร จึงเป็น `bash -ex` เฉย ๆ):

- `rm -rf` ลบโฟลเดอร์ clone ของ build ก่อน ให้เริ่มจากซอร์สใหม่ทุกครั้ง
- `git clone --depth 1 --filter=blob:none --sparse` ดึงเฉพาะ commit ล่าสุดของ branch เริ่มต้นบน GitHub โดยยังไม่โหลดไฟล์ทั้ง repo · `git sparse-checkout set ...` เลือกให้มีเฉพาะโฟลเดอร์ `catfood-shop`
- `git log -1 --oneline` และ `ls` แสดง commit ที่ได้และรายชื่อไฟล์ใน console เป็นหลักฐานว่า clone อะไรมา
- หมายเหตุ: stage นี้ clone ใหม่เอง ไม่ได้ใช้ commit เดียวกับที่ Jenkins อ่าน `Jenkinsfile` ถ้ามี commit ใหม่เข้ามาระหว่างนั้น สองฝั่งอาจเป็นคนละ commit

**Stage 3 — Build** — shell บน Jenkins แทนค่า `IMAGE`, `APP_VERSION`, `BUILD_NUMBER` แล้วส่งไปเป็นตัวแปรของ bash บน devtools · สคริปต์ที่เหลือรัน**บน devtools**: `cd` เข้าโฟลเดอร์ `catfood-shop` ที่เพิ่ง clone → `git rev-parse --short HEAD` อ่าน commit → `docker build` ด้วย Docker ของ devtools เป็น image `catfood-shop:lab3-<เลข build>` โดยส่ง `--build-arg` สี่ตัว (เวอร์ชัน, เลข build, commit, เวลา UTC) ที่ `Dockerfile` เก็บเป็น environment ใน image ให้ `/api/health` อ่านตอนรัน → `docker image ls` แสดง image ที่ได้ · image นี้อยู่ใน devtools เท่านั้น ยังไม่ขึ้น Docker Hub

**Stage 4 — Test** — ส่งตัวแปรแบบเดียวกับ Build · ทุกคำสั่งรัน**บน devtools**:

1. `docker rm -f catfood-test || true` ลบ container ทดสอบที่อาจค้างจากรอบก่อน (`|| true` ไม่ให้ล้มถ้าไม่มี)
2. `docker run -d --name catfood-test "$IMAGE"` รัน image ใหม่แบบไม่เปิด port ออกนอก container · `trap ... EXIT` ลบ container นี้เสมอเมื่อสคริปต์จบ แม้ test ไม่ผ่าน
3. ลูป `for` ถาม `docker inspect` ทุก 1 วินาที สูงสุด 30 รอบ จนสถานะ `HEALTHCHECK` (ที่ประกาศใน `Dockerfile`) เป็น `healthy` · ถ้าครบ 30 รอบแล้วยังไม่ healthy ลูปจะจบเฉย ๆ ไม่ทำให้ stage ล้ม ตัวตัดสินคือขั้นถัดไป
4. `docker exec catfood-test wget ...` เรียก `/api/health` **จากข้างใน container** (เพราะไม่ได้เปิด port) → `tr -d '"'` ตัดเครื่องหมายคำพูดของ JSON → `grep -F` ต้องเจอ `version:<APP_VERSION>,build:<เลข build>,` ถ้าไม่เจอ `grep` คืนค่าผิดพลาด `bash -e` จึงหยุด และ stage Test ล้ม

**Stage 5 — Push** — `withCredentials` ดึง username/token จาก credential `dockerhub` มาเป็นตัวแปร `HUB_USER` และ `HUB_TOKEN` เฉพาะในบล็อก (Jenkins ซ่อนค่าเป็น `****` ใน console) แล้วห่อ `sshagent` ไว้ข้างใน:

1. `set +x` ปิดการพิมพ์คำสั่งของ `sh` ชั่วคราว → `echo "$HUB_TOKEN" |` ส่ง token ทาง stdin ผ่าน SSH เข้า `docker login --password-stdin` บน devtools token จึงไม่อยู่ใน command line หรือ console · `umask 077` ให้ไฟล์ login ใน `AUTH_DIR` อ่านได้เฉพาะ root · `set -x` เปิดการพิมพ์คำสั่งกลับ
2. `docker tag` ตั้งชื่อ image เป็น `<DOCKER_USER>/catfood-shop:lab3-<เลข build>` แล้ว `docker --config $AUTH_DIR push` ขึ้น Docker Hub ด้วยไฟล์ login นั้น
3. `docker image rm $IMAGE` ลบแค่ชื่อในเครื่อง `catfood-shop:lab3-<เลข build>` ชื่อ `$HUB_USER/...` ยังอยู่ให้ stage ถัดไป
4. stage นี้เป็นคำสั่งเดี่ยวจึงส่งตรงทีละบรรทัด ไม่ต้องใช้ `<<'EOF'` · `$AUTH_DIR`, `$HUB_USER`, `$IMAGE` ถูกแทนค่าโดย shell บน Jenkins ก่อนส่ง

**Stage 6 — Deploy** — ใช้ `withCredentials` + `sshagent` เหมือน Push แต่ใช้แค่ `HUB_USER` ตั้งชื่อ image · ส่ง `AUTH_DIR` และ `IMAGE=$HUB_USER/$IMAGE` (ชื่อเต็มบน Docker Hub) ไปให้สคริปต์บน devtools:

1. `docker image rm "$IMAGE"` ลบ image ในเครื่อง แล้ว `docker --config "$AUTH_DIR" pull` ดึงกลับมาจาก Docker Hub เพื่อพิสูจน์ว่า image บน Hub ใช้ได้จริง (console ขึ้น `Downloaded newer image`)
2. `docker rm -f catfood-web || true` ลบร้านเวอร์ชันเดิม → `docker run -d --name catfood-web --restart unless-stopped -p 3000:3000` รันตัวใหม่ที่ port `3000` ของ devtools ซึ่ง map ออกมาเป็น `localhost:3000` ของเครื่องเรา (ช่วงสั้น ๆ ระหว่างสลับ container ร้านจะปิดชั่วคราว)
3. รอ `healthy` แบบเดียวกับ Test แล้ว `curl -fsS http://localhost:3000/api/health` จากบน devtools ต้องได้เวอร์ชันและเลข build ตรงกับ build นี้

**`post`** — ทำงานหลังจบทุก stage:

- `success` ทำเมื่อ build ผ่านเท่านั้น: `echo` พิมพ์ URL ของร้านพร้อมเวอร์ชันและเลข build · string นี้ใช้ `"..."` Groovy จึงแทนค่า `${params.APP_VERSION}` และ `${env.BUILD_NUMBER}` บน Jenkins
- `always` ทำเสมอ ทั้งตอนสำเร็จและตอน build หยุดกลางทาง: SSH ไป `rm -rf $AUTH_DIR` ลบไฟล์ login Docker Hub บน devtools · `|| true` ไม่ให้ขั้นลบนี้ทำให้ผลของ build เปลี่ยน

หลัง stage **Deploy** เขียว (และ `post` ลบไฟล์ login แล้ว) ให้เปิด **[ร้าน Meow Mart บนเครื่อง lab ของเรา — http://localhost:3000](http://localhost:3000)** ในเบราว์เซอร์ของเครื่องที่รัน container `devtools` (ลิงก์ใช้ได้เฉพาะหลัง Deploy สำเร็จ) แล้วตรวจ chip บนแถบด้านบนว่าตรงกับ `APP_VERSION` และเลข build ที่เพิ่งรัน หน้าร้านจะมีลักษณะแบบนี้:

[![หน้าร้าน Meow Mart (ภาพเดิม)](./images/lab3_sib_app_v110_crop.png)](./images/lab3_sib_app_v110.png)

*ภาพที่ 10 🕰️ **ภาพเดิม — ตัวอย่างผลลัพธ์จากการรันจริงรอบก่อน** (2026-09-26, workflow รุ่นก่อน, ซอร์สร้านเดียวกัน) chip แสดง `v1.1.0 · build #2` · ภาพตัดเฉพาะหน้าเว็บ ไม่มีแถบ URL ของเบราว์เซอร์ · ใช้ดูหน้าตาร้านเท่านั้น · build แรกของเราต้องเห็น `v1.0.0 · build #1`*

