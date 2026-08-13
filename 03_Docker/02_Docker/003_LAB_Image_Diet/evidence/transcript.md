# evidence / transcript — LAB 3 (`003_LAB_Image_Diet`)

หลักฐานการรันจริงทั้งหมดของแล็บนี้ เก็บจากเครื่องเรียน `tuchsanai/devtools:2569_1`
(outer container `devtools-lab003`, SSH 2224, web 18031 -> inner 8080) เมื่อ 12 ส.ค. 2026

- ทุกคำสั่งรันที่ `/workspace/lab` ซึ่งคือสำเนาของโฟลเดอร์ `003_LAB_Image_Diet` นี้
- ผลลัพธ์ทุกบล็อกใน `README.md` ตัดมาจากไฟล์นี้ ไม่มีการพิมพ์เพิ่มหรือแต่งเติม
- ค่า container ID / image ID / digest / เวลา / ขนาด ของแต่ละเครื่องจะไม่ตรงกันเป๊ะ ๆ


## 1. `docker --version; docker compose version`

```bash
docker --version; docker compose version
```

```
Docker version 29.6.2, build dfc4efb
Docker Compose version v5.3.1
```

_exit code: 0_

## 2. `ls -a; echo "---- app ----"; ls -l app; echo "---- requirements ----"; cat app/requirements.txt`

```bash
ls -a; echo "---- app ----"; ls -l app; echo "---- requirements ----"; cat app/requirements.txt
```

```
.
..
.dockerignore
.gitignore
app
v1
v2
v3
---- app ----
total 28
-rw-r--r-- 1 root root 8264 Aug 12 19:38 app.py
-rw-r--r-- 1 root root 1820 Aug 12 19:25 build_assets.py
-rw-r--r-- 1 root root   68 Aug 12 19:25 requirements.txt
-rw-r--r-- 1 root root 5037 Aug 12 19:38 style.css
---- requirements ----
flask==3.1.0
gunicorn==23.0.0
requests==2.32.3
python-dotenv==1.0.1
```

_exit code: 0_

## 3. `docker pull python:3.12 | tail -3; docker pull python:3.12-slim | tail -3`

```bash
docker pull python:3.12 | tail -3; docker pull python:3.12-slim | tail -3
```

```
Digest: sha256:dd4fe98ab39f91e936f8e7e7a65a3ce59ecfb11e32f9a125b3132779920ba7f7
Status: Image is up to date for python:3.12
docker.io/library/python:3.12
Digest: sha256:229a2c5bfa27522db7815ea81f9bed70af17ccb9de9fc7ad142b1877b5830d36
Status: Image is up to date for python:3.12-slim
docker.io/library/python:3.12-slim
```

_exit code: 0_

## 4. `docker images`

```bash
docker images
```

```
IMAGE              ID             DISK USAGE   CONTENT SIZE   EXTRA
python:3.12        dd4fe98ab39f       1.62GB          429MB        
python:3.12-slim   229a2c5bfa27        179MB         45.4MB        
```

_exit code: 0_

## 5. `mkdir -p app/assets`

```bash
mkdir -p app/assets
head -c 15M /dev/urandom > app/assets/dataset-01.bin
head -c 15M /dev/urandom > app/assets/dataset-02.bin
head -c 15M /dev/urandom > app/assets/dataset-03.bin
head -c 5M  /dev/urandom > debug.log
du -sh app/assets debug.log .
```

```
46M	app/assets
5.0M	debug.log
68K	.
```

_exit code: 0_

## 6. `mv .dockerignore .dockerignore.off && ls -a`

```bash
mv .dockerignore .dockerignore.off && ls -a
```

```
.
..
.dockerignore.off
.gitignore
app
debug.log
v1
v2
v3
```

_exit code: 0_

## 7. `cat v1/Dockerfile`

```bash
cat v1/Dockerfile
```

```
# =============================================================
# v1 — "แบบที่ทำงานได้ แต่ไม่มีใครอยากดูแล"
# ปัญหา 4 ข้อที่ตั้งใจใส่ไว้ให้เห็นกับตาในแล็บ
#   1) ใช้ base image เต็มรูปแบบ (python:3.12 ~1 GB)
#   2) COPY ทุกอย่างเข้ามา "ก่อน" pip install  -> แก้โค้ด 1 บรรทัด = ลง lib ใหม่ทั้งชุด
#   3) ไม่มี .dockerignore -> ไฟล์ขยะ/dataset ถูกยัดเข้า image ด้วย
#   4) ไม่ pin เวอร์ชัน + รันด้วย root
# =============================================================
FROM python:3.12

WORKDIR /app

COPY . .

RUN pip install flask gunicorn requests python-dotenv

ENV APP_VARIANT=v1 \
    BASE_IMAGE=python:3.12 \
    APP_PORT=8080

EXPOSE 8080

CMD ["python", "app/app.py"]
```

_exit code: 0_

## 8. `time docker build -f v1/Dockerfile -t diet-app:v1 .`

```bash
time docker build -f v1/Dockerfile -t diet-app:v1 .
```

```
#0 building with "default" instance using docker driver

#1 [internal] load build definition from Dockerfile
#1 transferring dockerfile: 1.07kB done
#1 DONE 0.0s

#2 [internal] load metadata for docker.io/library/python:3.12
#2 DONE 0.0s

#3 [internal] load .dockerignore
#3 transferring context:
#3 transferring context: 2B done
#3 DONE 0.0s

#4 [1/4] FROM docker.io/library/python:3.12@sha256:dd4fe98ab39f91e936f8e7e7a65a3ce59ecfb11e32f9a125b3132779920ba7f7
#4 resolve docker.io/library/python:3.12@sha256:dd4fe98ab39f91e936f8e7e7a65a3ce59ecfb11e32f9a125b3132779920ba7f7 0.0s done
#4 ...

#5 [internal] load build context
#5 transferring context: 52.46MB 0.1s done
#5 DONE 0.2s

#4 [1/4] FROM docker.io/library/python:3.12@sha256:dd4fe98ab39f91e936f8e7e7a65a3ce59ecfb11e32f9a125b3132779920ba7f7
#4 DONE 0.3s

#6 [2/4] WORKDIR /app
#6 DONE 0.1s

#7 [3/4] COPY . .
#7 DONE 0.1s

#8 [4/4] RUN pip install flask gunicorn requests python-dotenv
#8 0.961 Collecting flask
#8 1.005   Downloading flask-3.1.3-py3-none-any.whl.metadata (3.2 kB)
#8 1.038 Collecting gunicorn
#8 1.048   Downloading gunicorn-26.0.0-py3-none-any.whl.metadata (5.4 kB)
#8 1.084 Collecting requests
#8 1.092   Downloading requests-2.34.2-py3-none-any.whl.metadata (4.8 kB)
#8 1.125 Collecting python-dotenv
#8 1.135   Downloading python_dotenv-1.2.2-py3-none-any.whl.metadata (27 kB)
#8 1.165 Collecting blinker>=1.9.0 (from flask)
#8 1.174   Downloading blinker-1.9.0-py3-none-any.whl.metadata (1.6 kB)
#8 1.201 Collecting click>=8.1.3 (from flask)
#8 1.208   Downloading click-8.4.2-py3-none-any.whl.metadata (2.6 kB)
#8 1.238 Collecting itsdangerous>=2.2.0 (from flask)
#8 1.247   Downloading itsdangerous-2.2.0-py3-none-any.whl.metadata (1.9 kB)
#8 1.276 Collecting jinja2>=3.1.2 (from flask)
#8 1.284   Downloading jinja2-3.1.6-py3-none-any.whl.metadata (2.9 kB)
#8 1.338 Collecting markupsafe>=2.1.1 (from flask)
#8 1.347   Downloading markupsafe-3.0.3-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl.metadata (2.7 kB)
#8 1.381 Collecting werkzeug>=3.1.0 (from flask)
#8 1.388   Downloading werkzeug-3.1.8-py3-none-any.whl.metadata (4.0 kB)
#8 1.419 Collecting packaging (from gunicorn)
#8 1.427   Downloading packaging-26.3-py3-none-any.whl.metadata (3.5 kB)
#8 1.519 Collecting charset_normalizer<4,>=2 (from requests)
#8 1.526   Downloading charset_normalizer-3.4.9-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl.metadata (41 kB)
#8 1.558 Collecting idna<4,>=2.5 (from requests)
#8 1.566   Downloading idna-3.18-py3-none-any.whl.metadata (6.1 kB)
#8 1.600 Collecting urllib3<3,>=1.26 (from requests)
#8 1.611   Downloading urllib3-2.7.0-py3-none-any.whl.metadata (6.9 kB)
#8 1.644 Collecting certifi>=2023.5.7 (from requests)
#8 1.654   Downloading certifi-2026.7.22-py3-none-any.whl.metadata (2.5 kB)
#8 1.678 Downloading flask-3.1.3-py3-none-any.whl (103 kB)
#8 1.701 Downloading gunicorn-26.0.0-py3-none-any.whl (212 kB)
#8 1.735 Downloading requests-2.34.2-py3-none-any.whl (73 kB)
#8 1.758 Downloading python_dotenv-1.2.2-py3-none-any.whl (22 kB)
#8 1.776 Downloading blinker-1.9.0-py3-none-any.whl (8.5 kB)
#8 1.794 Downloading certifi-2026.7.22-py3-none-any.whl (136 kB)
#8 1.820 Downloading charset_normalizer-3.4.9-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (224 kB)
#8 1.845 Downloading click-8.4.2-py3-none-any.whl (119 kB)
#8 1.869 Downloading idna-3.18-py3-none-any.whl (65 kB)
#8 1.891 Downloading itsdangerous-2.2.0-py3-none-any.whl (16 kB)
#8 1.909 Downloading jinja2-3.1.6-py3-none-any.whl (134 kB)
#8 1.935 Downloading markupsafe-3.0.3-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (22 kB)
#8 1.954 Downloading urllib3-2.7.0-py3-none-any.whl (131 kB)
#8 1.979 Downloading werkzeug-3.1.8-py3-none-any.whl (226 kB)
#8 2.013 Downloading packaging-26.3-py3-none-any.whl (129 kB)
#8 2.052 Installing collected packages: urllib3, python-dotenv, packaging, markupsafe, itsdangerous, idna, click, charset_normalizer, certifi, blinker, werkzeug, requests, jinja2, gunicorn, flask
#8 2.569 Successfully installed blinker-1.9.0 certifi-2026.7.22 charset_normalizer-3.4.9 click-8.4.2 flask-3.1.3 gunicorn-26.0.0 idna-3.18 itsdangerous-2.2.0 jinja2-3.1.6 markupsafe-3.0.3 packaging-26.3 python-dotenv-1.2.2 requests-2.34.2 urllib3-2.7.0 werkzeug-3.1.8
#8 2.569 WARNING: Running pip as the 'root' user can result in broken permissions and conflicting behaviour with the system package manager, possibly rendering your system unusable. It is recommended to use a virtual environment instead: https://pip.pypa.io/warnings/venv. Use the --root-user-action option if you know what you are doing and want to suppress this warning.
#8 2.643 
#8 2.643 [notice] A new release of pip is available: 25.0.1 -> 26.2.1
#8 2.643 [notice] To update, run: pip install --upgrade pip
#8 DONE 2.7s

#9 exporting to image
#9 exporting layers
#9 exporting layers 0.8s done
#9 exporting manifest sha256:9d7c1eebbb02fcf121d70ea6557954f82dd258d554ab6eb2e0234cdefc599efb 0.0s done
#9 exporting config sha256:a2d00c2b917ba66a702d45ac4128df0b79bbbd0589e05e8f233133c52bc7a769 0.0s done
#9 exporting attestation manifest sha256:e8457926d7b24fdbb350880ee7849f6105d2e275e9d712ce749b710d4e93cd3d 0.0s done
#9 exporting manifest list sha256:b235b5abeaa174eb986f379a16602ccfa63740047e41e3d0752e82155efef047
#9 exporting manifest list sha256:b235b5abeaa174eb986f379a16602ccfa63740047e41e3d0752e82155efef047 0.0s done
#9 naming to docker.io/library/diet-app:v1 done
#9 unpacking to docker.io/library/diet-app:v1
#9 unpacking to docker.io/library/diet-app:v1 0.3s done
#9 DONE 1.3s

real	0m4.911s
user	0m0.160s
sys	0m0.155s
```

_exit code: 0_

## 9. `docker images`

```bash
docker images
```

```
IMAGE              ID             DISK USAGE   CONTENT SIZE   EXTRA
diet-app:v1        b235b5abeaa1       1.74GB          473MB        
python:3.12        dd4fe98ab39f       1.62GB          429MB        
python:3.12-slim   229a2c5bfa27        179MB         45.4MB        
```

_exit code: 0_

## 10. `grep -n "003_LAB_Image_Diet ·" app/app.py`

```bash
grep -n "003_LAB_Image_Diet ·" app/app.py
```

```
221:  <footer>LAB 3 · 003_LAB_Image_Diet · <code>/healthz</code> · <code>/facts</code></footer>
```

_exit code: 0_

## 11. `sed -i "s|LAB 3 · 003_LAB_Image_Diet|LAB 3 · 003_LAB_Image_Diet · แก้โค้ดรอบที่ 1|" app/app.py; grep -n "003_L`

```bash
sed -i "s|LAB 3 · 003_LAB_Image_Diet|LAB 3 · 003_LAB_Image_Diet · แก้โค้ดรอบที่ 1|" app/app.py; grep -n "003_LAB_Image_Diet ·" app/app.py
```

```
221:  <footer>LAB 3 · 003_LAB_Image_Diet · แก้โค้ดรอบที่ 1 · <code>/healthz</code> · <code>/facts</code></footer>
```

_exit code: 0_

## 12. `time docker build -f v1/Dockerfile -t diet-app:v1 . 2>&1 | grep -E "^#[0-9]+ \[|CACHED|^#[0-9]+ DONE|transferr`

```bash
time docker build -f v1/Dockerfile -t diet-app:v1 . 2>&1 | grep -E "^#[0-9]+ \[|CACHED|^#[0-9]+ DONE|transferring context"
```

```
#1 [internal] load build definition from Dockerfile
#1 DONE 0.0s
#2 [internal] load metadata for docker.io/library/python:3.12
#2 DONE 0.0s
#3 [internal] load .dockerignore
#3 transferring context: 2B done
#3 DONE 0.0s
#4 [internal] load build context
#4 DONE 0.0s
#5 [1/4] FROM docker.io/library/python:3.12@sha256:dd4fe98ab39f91e936f8e7e7a65a3ce59ecfb11e32f9a125b3132779920ba7f7
#5 DONE 0.0s
#4 [internal] load build context
#4 transferring context: 8.92kB done
#4 DONE 0.0s
#6 [2/4] WORKDIR /app
#6 CACHED
#7 [3/4] COPY . .
#7 DONE 0.1s
#8 [4/4] RUN pip install flask gunicorn requests python-dotenv
#8 DONE 2.7s
#9 DONE 1.3s

real	0m4.493s
user	0m0.038s
sys	0m0.120s
```

_exit code: 0_

## 13. `cat v2/Dockerfile`

```bash
cat v2/Dockerfile
```

```
# =============================================================
# v2 — "เรียง layer ให้ cache ทำงาน + เปลี่ยนไปใช้ base ที่ผอมกว่า"
#   1) python:3.12-slim แทน python:3.12
#   2) COPY requirements.txt -> pip install -> ค่อย COPY โค้ด
#      แก้โค้ด 1 บรรทัด จะไม่ทำให้ layer ของ pip เสีย cache
#   3) pin เวอร์ชันไว้ใน requirements.txt ทุกตัว
# ยังเหลืออีก 2 เรื่องที่ v3 จะไปแก้ต่อ : ยังรันด้วย root และยังมี pip cache ติดอยู่
# =============================================================
FROM python:3.12-slim

WORKDIR /app

COPY app/requirements.txt ./requirements.txt

RUN pip install -r requirements.txt

COPY app/ ./app/

ENV APP_VARIANT=v2 \
    BASE_IMAGE=python:3.12-slim \
    APP_PORT=8080

EXPOSE 8080

CMD ["python", "app/app.py"]
```

_exit code: 0_

## 14. `time docker build -f v2/Dockerfile -t diet-app:v2 . 2>&1 | grep -E "^#[0-9]+ \[|CACHED|^#[0-9]+ DONE|transferr`

```bash
time docker build -f v2/Dockerfile -t diet-app:v2 . 2>&1 | grep -E "^#[0-9]+ \[|CACHED|^#[0-9]+ DONE|transferring context"
```

```
#1 [internal] load build definition from Dockerfile
#1 DONE 0.0s
#2 [internal] load metadata for docker.io/library/python:3.12-slim
#2 DONE 0.0s
#3 [internal] load .dockerignore
#3 transferring context: 2B done
#3 DONE 0.0s
#4 [internal] load build context
#4 transferring context: 337B done
#4 DONE 0.0s
#5 [1/5] FROM docker.io/library/python:3.12-slim@sha256:229a2c5bfa27522db7815ea81f9bed70af17ccb9de9fc7ad142b1877b5830d36
#5 DONE 0.0s
#5 [1/5] FROM docker.io/library/python:3.12-slim@sha256:229a2c5bfa27522db7815ea81f9bed70af17ccb9de9fc7ad142b1877b5830d36
#5 DONE 0.2s
#6 [2/5] WORKDIR /app
#6 DONE 0.1s
#7 [3/5] COPY app/requirements.txt ./requirements.txt
#7 DONE 0.1s
#8 [4/5] RUN pip install -r requirements.txt
#8 DONE 2.6s
#9 [5/5] COPY app/ ./app/
#9 DONE 0.1s
#10 DONE 1.4s

real	0m4.699s
user	0m0.064s
sys	0m0.087s
```

_exit code: 0_

## 15. `docker images`

```bash
docker images
```

```
IMAGE              ID             DISK USAGE   CONTENT SIZE   EXTRA
diet-app:v1        c7d1b6ed18f0       1.74GB          473MB        
diet-app:v2        58afc2374362        304MB         99.1MB        
python:3.12        dd4fe98ab39f       1.62GB          429MB        
python:3.12-slim   229a2c5bfa27        179MB         45.4MB        
```

_exit code: 0_

## 16. `sed -i "s|แก้โค้ดรอบที่ 1|แก้โค้ดรอบที่ 2|" app/app.py; grep -n "003_LAB_Image_Diet ·" app/app.py`

```bash
sed -i "s|แก้โค้ดรอบที่ 1|แก้โค้ดรอบที่ 2|" app/app.py; grep -n "003_LAB_Image_Diet ·" app/app.py
```

```
221:  <footer>LAB 3 · 003_LAB_Image_Diet · แก้โค้ดรอบที่ 2 · <code>/healthz</code> · <code>/facts</code></footer>
```

_exit code: 0_

## 17. `time docker build -f v2/Dockerfile -t diet-app:v2 . 2>&1 | grep -E "^#[0-9]+ \[|CACHED|^#[0-9]+ DONE|transferr`

```bash
time docker build -f v2/Dockerfile -t diet-app:v2 . 2>&1 | grep -E "^#[0-9]+ \[|CACHED|^#[0-9]+ DONE|transferring context"
```

```
#1 [internal] load build definition from Dockerfile
#1 DONE 0.0s
#2 [internal] load metadata for docker.io/library/python:3.12-slim
#2 DONE 0.0s
#3 [internal] load .dockerignore
#3 transferring context: 2B done
#3 DONE 0.0s
#4 [internal] load build context
#4 transferring context: 8.66kB done
#4 DONE 0.0s
#5 [1/5] FROM docker.io/library/python:3.12-slim@sha256:229a2c5bfa27522db7815ea81f9bed70af17ccb9de9fc7ad142b1877b5830d36
#5 DONE 0.0s
#6 [3/5] COPY app/requirements.txt ./requirements.txt
#6 CACHED
#7 [2/5] WORKDIR /app
#7 CACHED
#8 [4/5] RUN pip install -r requirements.txt
#8 CACHED
#9 [5/5] COPY app/ ./app/
#9 DONE 0.1s
#10 DONE 1.0s

real	0m1.459s
user	0m0.053s
sys	0m0.071s
```

_exit code: 0_

## 18. `mv .dockerignore.off .dockerignore && cat .dockerignore`

```bash
mv .dockerignore.off .dockerignore && cat .dockerignore
```

```
# ไฟล์/โฟลเดอร์ที่ "ไม่ต้อง" ส่งเข้า build context
# ลดทั้งเวลาส่ง context และขนาดของ image
# หมายเหตุ : .dockerignore ใส่ comment ได้เฉพาะบรรทัดที่ขึ้นต้นด้วย # เท่านั้น
# ห้ามเขียน comment ต่อท้ายบรรทัด pattern เพราะจะกลายเป็นส่วนหนึ่งของ pattern

# dataset ก้อนใหญ่ ใช้ตอนพัฒนาเท่านั้น ไม่ต้องเข้า image
app/assets/

# log ของเครื่องเรา
*.log

# ขยะของ Python
__pycache__/
*.pyc
.venv/

# ประวัติ git ไม่เกี่ยวกับการรันแอป
.git/
.gitignore

# ผลลัพธ์ build เก่าบนเครื่องเรา ให้ builder stage สร้างใหม่เสมอ
app/static/

# เอกสารและภาพประกอบของแล็บ
README.md
images/
evidence/
```

_exit code: 0_

## 19. `time docker build -f v2/Dockerfile -t diet-app:v2 . 2>&1 | grep -E "^#[0-9]+ \[|CACHED|^#[0-9]+ DONE|transferr`

```bash
time docker build -f v2/Dockerfile -t diet-app:v2 . 2>&1 | grep -E "^#[0-9]+ \[|CACHED|^#[0-9]+ DONE|transferring context"
```

```
#1 [internal] load build definition from Dockerfile
#1 DONE 0.0s
#2 [internal] load metadata for docker.io/library/python:3.12-slim
#2 DONE 0.0s
#3 [internal] load .dockerignore
#3 transferring context: 1.21kB done
#3 DONE 0.0s
#4 [internal] load build context
#4 transferring context: 166B done
#4 DONE 0.0s
#5 [1/5] FROM docker.io/library/python:3.12-slim@sha256:229a2c5bfa27522db7815ea81f9bed70af17ccb9de9fc7ad142b1877b5830d36
#5 DONE 0.0s
#6 [2/5] WORKDIR /app
#6 CACHED
#7 [3/5] COPY app/requirements.txt ./requirements.txt
#7 CACHED
#8 [4/5] RUN pip install -r requirements.txt
#8 CACHED
#9 [5/5] COPY app/ ./app/
#9 DONE 0.1s
#10 DONE 0.3s

real	0m0.753s
user	0m0.031s
sys	0m0.090s
```

_exit code: 0_

## 20. `docker images`

```bash
docker images
```

```
IMAGE              ID             DISK USAGE   CONTENT SIZE   EXTRA
diet-app:v1        c7d1b6ed18f0       1.74GB          473MB        
diet-app:v2        a8b458a7bd3c        210MB         51.9MB        
python:3.12        dd4fe98ab39f       1.62GB          429MB        
python:3.12-slim   229a2c5bfa27        179MB         45.4MB        
```

_exit code: 0_

## 21. `rm -rf ~/ctx-off ~/ctx-on`

```bash
rm -rf ~/ctx-off ~/ctx-on
mkdir -p ~/ctx-off ~/ctx-on
cp -a . ~/ctx-off/
cp -a . ~/ctx-on/
rm -f ~/ctx-off/.dockerignore
du -sh ~/ctx-off ~/ctx-on
```

```
51M	/root/ctx-off
51M	/root/ctx-on
```

_exit code: 0_

## 22. `docker build -f v2/Dockerfile -t ctx:off ~/ctx-off 2>&1 | grep -A1 "load build context"`

```bash
docker build -f v2/Dockerfile -t ctx:off ~/ctx-off 2>&1 | grep -A1 "load build context"
```

```
#5 [internal] load build context
#5 transferring context: 47.21MB 0.1s done
```

_exit code: 0_

## 23. `docker build -f v2/Dockerfile -t ctx:on  ~/ctx-on  2>&1 | grep -A1 "load build context"`

```bash
docker build -f v2/Dockerfile -t ctx:on  ~/ctx-on  2>&1 | grep -A1 "load build context"
```

```
#5 [internal] load build context
#5 transferring context: 15.44kB done
```

_exit code: 0_

## 24. `docker images ctx`

```bash
docker images ctx
```

```
IMAGE     ID             DISK USAGE   CONTENT SIZE   EXTRA
ctx:off   2a6166344743        304MB         99.1MB        
ctx:on    d2115fcebc4b        210MB         51.9MB        
```

_exit code: 0_

## 25. `docker rmi ctx:off ctx:on; rm -rf ~/ctx-off ~/ctx-on; echo cleaned`

```bash
docker rmi ctx:off ctx:on; rm -rf ~/ctx-off ~/ctx-on; echo cleaned
```

```
Untagged: ctx:off
Deleted: sha256:2a616634474312e0ec823c3b799915db2812b079f68181eaa86d83a3ec510cd8
Untagged: ctx:on
Deleted: sha256:d2115fcebc4b96d69fcffbe48155e8c45ce1c91b047bab87c8fd46eb5cd2fd10
cleaned
```

_exit code: 0_

## 26. `cat v3/Dockerfile`

```bash
cat v3/Dockerfile
```

```
# =============================================================
# v3 — multi-stage + non-root + healthcheck
#   stage 1 (builder) : ใช้ base ตัวหนัก 1 GB ได้เต็มที่ ติดตั้ง lib ลง venv
#                       และรันขั้นตอน build asset (minify CSS)
#   stage 2 (runtime) : เริ่มจาก base ผอม แล้วหยิบมาเฉพาะ "ผลลัพธ์"
#                       -> เครื่องมือ build ไม่ตามไปกับ image สุดท้าย
# =============================================================

# ---------------------- stage 1 : builder ----------------------
FROM python:3.12 AS builder

WORKDIR /build

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY app/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
RUN python app/build_assets.py

# ---------------------- stage 2 : runtime ----------------------
FROM python:3.12-slim

RUN useradd --create-home --uid 10001 appuser

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /build/app/ ./app/

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    APP_VARIANT=v3 \
    BASE_IMAGE=python:3.12-slim \
    APP_PORT=8080

USER appuser

EXPOSE 8080

HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request as u; u.urlopen('http://127.0.0.1:8080/healthz')" || exit 1

CMD ["python", "app/app.py"]
```

_exit code: 0_

## 27. `time docker build -f v3/Dockerfile -t diet-app:v3 . 2>&1 | grep -E "^#[0-9]+ \[|CACHED|^#[0-9]+ DONE|transferr`

```bash
time docker build -f v3/Dockerfile -t diet-app:v3 . 2>&1 | grep -E "^#[0-9]+ \[|CACHED|^#[0-9]+ DONE|transferring context|build_assets"
```

```
#1 [internal] load build definition from Dockerfile
#1 DONE 0.0s
#2 [internal] load metadata for docker.io/library/python:3.12-slim
#2 DONE 0.0s
#3 [internal] load metadata for docker.io/library/python:3.12
#3 DONE 0.1s
#4 [internal] load .dockerignore
#4 transferring context: 1.21kB done
#4 DONE 0.0s
#5 [internal] load build context
#5 DONE 0.0s
#6 [stage-1 1/5] FROM docker.io/library/python:3.12-slim@sha256:229a2c5bfa27522db7815ea81f9bed70af17ccb9de9fc7ad142b1877b5830d36
#6 CACHED
#7 [builder 1/7] FROM docker.io/library/python:3.12@sha256:dd4fe98ab39f91e936f8e7e7a65a3ce59ecfb11e32f9a125b3132779920ba7f7
#7 CACHED
#5 [internal] load build context
#5 transferring context: 166B done
#5 DONE 0.0s
#8 [builder 2/7] WORKDIR /build
#8 DONE 0.1s
#9 [stage-1 2/5] RUN useradd --create-home --uid 10001 appuser
#9 DONE 0.4s
#10 [builder 3/7] RUN python -m venv /opt/venv
#11 [stage-1 3/5] WORKDIR /app
#11 DONE 0.1s
#10 [builder 3/7] RUN python -m venv /opt/venv
#10 DONE 1.7s
#12 [builder 4/7] COPY app/requirements.txt ./requirements.txt
#12 DONE 0.1s
#13 [builder 5/7] RUN pip install --no-cache-dir -r requirements.txt
#13 DONE 1.7s
#14 [builder 6/7] COPY app/ ./app/
#14 DONE 0.1s
#15 [builder 7/7] RUN python app/build_assets.py
#15 0.273 [build_assets] style.css 5037 B -> style.min.css 2941 B
#15 DONE 0.3s
#16 [stage-1 4/5] COPY --from=builder /opt/venv /opt/venv
#16 DONE 0.2s
#17 [stage-1 5/5] COPY --from=builder /build/app/ ./app/
#17 DONE 0.1s
#18 DONE 1.1s

real	0m5.822s
user	0m0.071s
sys	0m0.093s
```

_exit code: 0_

## 28. `docker images`

```bash
docker images
```

```
IMAGE              ID             DISK USAGE   CONTENT SIZE   EXTRA
diet-app:v1        c7d1b6ed18f0       1.74GB          473MB        
diet-app:v2        a8b458a7bd3c        210MB         51.9MB        
diet-app:v3        76146f411612        209MB         50.3MB        
python:3.12        dd4fe98ab39f       1.62GB          429MB        
python:3.12-slim   229a2c5bfa27        179MB         45.4MB        
```

_exit code: 0_

## 29. `docker build --target builder -f v3/Dockerfile -t diet-app:builder . 2>&1 | tail -3; docker images`

```bash
docker build --target builder -f v3/Dockerfile -t diet-app:builder . 2>&1 | tail -3; docker images
```

```
#12 unpacking to docker.io/library/diet-app:builder
#12 unpacking to docker.io/library/diet-app:builder 0.3s done
#12 DONE 1.1s
IMAGE              ID             DISK USAGE   CONTENT SIZE   EXTRA
diet-app:builder   5182e3993079       1.64GB          420MB        
diet-app:v1        c7d1b6ed18f0       1.74GB          473MB        
diet-app:v2        a8b458a7bd3c        210MB         51.9MB        
diet-app:v3        76146f411612        209MB         50.3MB        
python:3.12        dd4fe98ab39f       1.62GB          429MB        
python:3.12-slim   229a2c5bfa27        179MB         45.4MB        
```

_exit code: 0_

## 30. `docker rmi diet-app:builder`

```bash
docker rmi diet-app:builder
```

```
Untagged: diet-app:builder
Deleted: sha256:5182e399307925a26d5a9a6bf018a03185dfa2ef7026d3152f6d2c690553f04f
```

_exit code: 0_

## 31. `docker run --rm diet-app:v1 whoami; docker run --rm diet-app:v3 whoami; docker run --rm diet-app:v3 id`

```bash
docker run --rm diet-app:v1 whoami; docker run --rm diet-app:v3 whoami; docker run --rm diet-app:v3 id
```

```
root
appuser
uid=10001(appuser) gid=10001(appuser) groups=10001(appuser)
```

_exit code: 0_

## 32. `docker run --rm diet-app:v1 pip show flask 2>/dev/null | head -2; echo "--- v3 ---"; docker run --rm diet-app:`

```bash
docker run --rm diet-app:v1 pip show flask 2>/dev/null | head -2; echo "--- v3 ---"; docker run --rm diet-app:v3 pip show flask 2>/dev/null | head -2
```

```
Name: Flask
Version: 3.1.3
--- v3 ---
Name: Flask
Version: 3.1.0
```

_exit code: 0_

## 33. `docker image history diet-app:v1`

```bash
docker image history diet-app:v1
```

```
IMAGE          CREATED          CREATED BY                                      SIZE      COMMENT
c7d1b6ed18f0   23 seconds ago   CMD ["python" "app/app.py"]                     0B        buildkit.dockerfile.v0
<missing>      23 seconds ago   EXPOSE [8080/tcp]                               0B        buildkit.dockerfile.v0
<missing>      23 seconds ago   ENV APP_VARIANT=v1 BASE_IMAGE=python:3.12 AP…   0B        buildkit.dockerfile.v0
<missing>      23 seconds ago   RUN /bin/sh -c pip install flask gunicorn re…   25.8MB    buildkit.dockerfile.v0
<missing>      26 seconds ago   COPY . . # buildkit                             52.5MB    buildkit.dockerfile.v0
<missing>      31 seconds ago   WORKDIR /app                                    8.19kB    buildkit.dockerfile.v0
<missing>      7 days ago       CMD ["python3"]                                 0B        buildkit.dockerfile.v0
<missing>      7 days ago       RUN /bin/sh -c set -eux;  for src in idle3 p…   16.4kB    buildkit.dockerfile.v0
<missing>      7 days ago       RUN /bin/sh -c set -eux;   wget -O python.ta…   72.8MB    buildkit.dockerfile.v0
<missing>      7 days ago       ENV PYTHON_SHA256=c08bc65a81971c1dd578318282…   0B        buildkit.dockerfile.v0
<missing>      7 days ago       ENV PYTHON_VERSION=3.12.13                      0B        buildkit.dockerfile.v0
<missing>      7 days ago       ENV GPG_KEY=7169605F62C751356D054A26A821E680…   0B        buildkit.dockerfile.v0
<missing>      7 days ago       RUN /bin/sh -c set -eux;  apt-get update;  a…   19.9MB    buildkit.dockerfile.v0
<missing>      7 days ago       ENV LANG=C.UTF-8                                0B        buildkit.dockerfile.v0
<missing>      7 days ago       ENV PATH=/usr/local/bin:/usr/local/sbin:/usr…   0B        buildkit.dockerfile.v0
<missing>      7 days ago       RUN /bin/sh -c set -ex;  apt-get update;  ap…   694MB     buildkit.dockerfile.v0
<missing>      7 days ago       RUN /bin/sh -c set -eux;  apt-get update;  a…   202MB     buildkit.dockerfile.v0
<missing>      7 days ago       RUN /bin/sh -c set -eux;  apt-get update;  a…   65MB      buildkit.dockerfile.v0
<missing>      9 days ago       # debian.sh --arch 'amd64' out/ 'trixie' '@1…   134MB     debuerreotype 0.17
```

_exit code: 0_

## 34. `docker image history diet-app:v3`

```bash
docker image history diet-app:v3
```

```
IMAGE          CREATED          CREATED BY                                      SIZE      COMMENT
76146f411612   7 seconds ago    CMD ["python" "app/app.py"]                     0B        buildkit.dockerfile.v0
<missing>      7 seconds ago    HEALTHCHECK {Test:[CMD-SHELL python -c "impo…   0B        buildkit.dockerfile.v0
<missing>      7 seconds ago    EXPOSE [8080/tcp]                               0B        buildkit.dockerfile.v0
<missing>      7 seconds ago    USER appuser                                    0B        buildkit.dockerfile.v0
<missing>      7 seconds ago    ENV PATH=/opt/venv/bin:/usr/local/bin:/usr/l…   0B        buildkit.dockerfile.v0
<missing>      7 seconds ago    COPY /build/app/ ./app/ # buildkit              53.2kB    buildkit.dockerfile.v0
<missing>      7 seconds ago    COPY /opt/venv /opt/venv # buildkit             24.8MB    buildkit.dockerfile.v0
<missing>      10 seconds ago   WORKDIR /app                                    8.19kB    buildkit.dockerfile.v0
<missing>      11 seconds ago   RUN /bin/sh -c useradd --create-home --uid 1…   69.6kB    buildkit.dockerfile.v0
<missing>      7 days ago       CMD ["python3"]                                 0B        buildkit.dockerfile.v0
<missing>      7 days ago       RUN /bin/sh -c set -eux;  for src in idle3 p…   16.4kB    buildkit.dockerfile.v0
<missing>      7 days ago       RUN /bin/sh -c set -eux;   savedAptMark="$(a…   41.4MB    buildkit.dockerfile.v0
<missing>      7 days ago       ENV PYTHON_SHA256=c08bc65a81971c1dd578318282…   0B        buildkit.dockerfile.v0
<missing>      7 days ago       ENV PYTHON_VERSION=3.12.13                      0B        buildkit.dockerfile.v0
<missing>      7 days ago       ENV GPG_KEY=7169605F62C751356D054A26A821E680…   0B        buildkit.dockerfile.v0
<missing>      7 days ago       RUN /bin/sh -c set -eux;  apt-get update;  a…   4.95MB    buildkit.dockerfile.v0
<missing>      7 days ago       ENV LANG=C.UTF-8                                0B        buildkit.dockerfile.v0
<missing>      7 days ago       ENV PATH=/usr/local/bin:/usr/local/sbin:/usr…   0B        buildkit.dockerfile.v0
<missing>      9 days ago       # debian.sh --arch 'amd64' out/ 'trixie' '@1…   87.4MB    debuerreotype 0.17
```

_exit code: 0_

## 35. `sed -i "s|แก้โค้ดรอบที่ 2|แก้โค้ดรอบสุดท้าย|" app/app.py; grep -n "003_LAB_Image_Diet ·" app/app.py`

```bash
sed -i "s|แก้โค้ดรอบที่ 2|แก้โค้ดรอบสุดท้าย|" app/app.py; grep -n "003_LAB_Image_Diet ·" app/app.py
```

```
221:  <footer>LAB 3 · 003_LAB_Image_Diet · แก้โค้ดรอบสุดท้าย · <code>/healthz</code> · <code>/facts</code></footer>
```

_exit code: 0_

## 36. `echo "----- v1 -----"; time docker build -f v1/Dockerfile -t diet-app:v1 . >/dev/null 2>&1`

```bash
echo "----- v1 -----"; time docker build -f v1/Dockerfile -t diet-app:v1 . >/dev/null 2>&1
echo "----- v2 -----"; time docker build -f v2/Dockerfile -t diet-app:v2 . >/dev/null 2>&1
echo "----- v3 -----"; time docker build -f v3/Dockerfile -t diet-app:v3 . >/dev/null 2>&1
```

```
----- v1 -----

real	0m4.256s
user	0m0.073s
sys	0m0.076s
----- v2 -----

real	0m0.984s
user	0m0.040s
sys	0m0.088s
----- v3 -----

real	0m1.326s
user	0m0.044s
sys	0m0.087s
```

_exit code: 0_

## 37. `docker images`

```bash
docker images
```

```
IMAGE              ID             DISK USAGE   CONTENT SIZE   EXTRA
diet-app:v1        e6bafffc232b       1.63GB          420MB        
diet-app:v2        21a664610c84        210MB         51.9MB        
diet-app:v3        52c0caeb7825        209MB         50.3MB        
python:3.12        dd4fe98ab39f       1.62GB          429MB        
python:3.12-slim   229a2c5bfa27        179MB         45.4MB        
```

_exit code: 0_

## 38. `docker run -d --name diet-web -p 8080:8080 \`

```bash
docker run -d --name diet-web -p 8080:8080 \
  -e IMAGE_TAG=diet-app:v3 \
  -e SIZE_V1="$(docker images --format "{{.Size}}" diet-app:v1)" \
  -e SIZE_V2="$(docker images --format "{{.Size}}" diet-app:v2)" \
  -e SIZE_V3="$(docker images --format "{{.Size}}" diet-app:v3)" \
  -e REBUILD_V1=4.256s -e REBUILD_V2=0.984s -e REBUILD_V3=1.326s \
  diet-app:v3
```

```
5fce18350499e122a98c7cab82e3093fc09b80a3bbeff63873b70a3a2bd63f75
```

_exit code: 0_

## 39. `docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"`

```bash
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"
```

```
NAMES      IMAGE         STATUS                    PORTS
diet-web   diet-app:v3   Up 12 seconds (healthy)   0.0.0.0:8080->8080/tcp, [::]:8080->8080/tcp
```

_exit code: 0_

## 40. `curl -s http://localhost:8080/healthz; echo; docker inspect --format "{{.State.Health.Status}}" diet-web`

```bash
curl -s http://localhost:8080/healthz; echo; docker inspect --format "{{.State.Health.Status}}" diet-web
```

```
{"status":"ok","variant":"v3"}

healthy
```

_exit code: 0_

## 41. `docker exec diet-web env | grep -E "^(SIZE_|REBUILD_|APP_|BASE_)" | sort`

```bash
docker exec diet-web env | grep -E "^(SIZE_|REBUILD_|APP_|BASE_)" | sort
```

```
APP_PORT=8080
APP_VARIANT=v3
BASE_IMAGE=python:3.12-slim
REBUILD_V1=4.256s
REBUILD_V2=0.984s
REBUILD_V3=1.326s
SIZE_V1=1.63GB
SIZE_V2=210MB
SIZE_V3=209MB
```

_exit code: 0_

## 42. `docker exec diet-web ls -l /app/app /opt/venv/bin | head -20`

```bash
docker exec diet-web ls -l /app/app /opt/venv/bin | head -20
```

```
/app/app:
total 32
-rw-r--r-- 1 root root 8319 Aug 12 12:40 app.py
-rw-r--r-- 1 root root 1820 Aug 12 12:25 build_assets.py
-rw-r--r-- 1 root root   68 Aug 12 12:25 requirements.txt
drwxr-xr-x 2 root root 4096 Aug 12 12:40 static
-rw-r--r-- 1 root root 5037 Aug 12 12:38 style.css

/opt/venv/bin:
total 56
-rw-r--r-- 1 root root 9033 Aug 12 12:40 Activate.ps1
-rw-r--r-- 1 root root 2138 Aug 12 12:40 activate
-rw-r--r-- 1 root root  905 Aug 12 12:40 activate.csh
-rw-r--r-- 1 root root 2180 Aug 12 12:40 activate.fish
-rwxr-xr-x 1 root root  216 Aug 12 12:40 dotenv
-rwxr-xr-x 1 root root  212 Aug 12 12:40 flask
-rwxr-xr-x 1 root root  221 Aug 12 12:40 gunicorn
-rwxr-xr-x 1 root root  211 Aug 12 12:40 idna
-rwxr-xr-x 1 root root  237 Aug 12 12:40 normalizer
-rwxr-xr-x 1 root root  225 Aug 12 12:40 pip
```

_exit code: 0_

## 43. `docker system df`

```bash
docker system df
```

```
TYPE            TOTAL     ACTIVE    SIZE      RECLAIMABLE
Images          5         1         1.896GB   87.91MB (4%)
Containers      1         1         4.096kB   0B (0%)
Local Volumes   0         0         0B        0B
Build Cache     47        0         1.11GB    555.4MB
```

_exit code: 0_

## 44. `docker rm -f diet-web; docker ps -a`

```bash
docker rm -f diet-web; docker ps -a
```

```
diet-web
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
```

_exit code: 0_

## 45. `docker rmi diet-app:v1 diet-app:v2 diet-app:v3`

```bash
docker rmi diet-app:v1 diet-app:v2 diet-app:v3
```

```
Untagged: diet-app:v1
Deleted: sha256:e6bafffc232b059c72653d22ac87c7ef265ca57e61942c213dabad14c73f399b
Untagged: diet-app:v2
Deleted: sha256:21a664610c846374995eb68e52982f466a4d2179182c73d89c7dafa70645ca41
Untagged: diet-app:v3
Deleted: sha256:52c0caeb782501696d3461ef2c99da299a558d526f88c2885993bb0295f00d42
```

_exit code: 0_

## 46. `docker image prune -f`

```bash
docker image prune -f
```

```
Total reclaimed space: 0B
```

_exit code: 0_

## 47. `docker images`

```bash
docker images
```

```
IMAGE              ID             DISK USAGE   CONTENT SIZE   EXTRA
python:3.12        dd4fe98ab39f       1.62GB          429MB        
python:3.12-slim   229a2c5bfa27        179MB         45.4MB        
```

_exit code: 0_

## 48. `rm -rf app/assets debug.log && ls -a && du -sh .`

```bash
rm -rf app/assets debug.log && ls -a && du -sh .
```

```
.
..
.dockerignore
.gitignore
app
v1
v2
v3
68K	.
```

_exit code: 0_

## 49. `docker builder prune -f | tail -3; docker system df`

```bash
docker builder prune -f | tail -3; docker system df
```

```
6gbi6xpumi7bps8azm258ulkf               	true 	23.95MB   	About a minute ago
vvqabglhufd0y0hnz4yxila5c               	true 	8.287kB   	About a minute ago
Total:	656MB
TYPE            TOTAL     ACTIVE    SIZE      RECLAIMABLE
Images          2         0         1.796GB   1.796GB (99%)
Containers      0         0         0B        0B
Local Volumes   0         0         0B        0B
Build Cache     11        0         454.1MB   0B
```

_exit code: 0_
