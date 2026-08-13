# evidence / transcript — LAB 2 (002_LAB_Env_Color_Factory)

บันทึกดิบของทุกคำสั่งที่รันจริงในเครื่องเรียน `tuchsanai/devtools:2569_1`
(outer container `devtools-lab002` · SSH 2223 · web 18021/18022/18023 → inner 8081/8082/8083)
รันทั้งชุดแบบเรียงลำดับเดียวกับ `README.md` หลังล้าง build cache เพื่อให้ ID/ขนาด/ผลลัพธ์สอดคล้องกันทั้งไฟล์

---

## 1. `docker --version; docker compose version`

```bash
docker --version; docker compose version
```

```
Docker version 29.6.2, build dfc4efb
Docker Compose version v5.3.1
```

`RC=0`

## 2. `ls -R app env secret-demo`

```bash
ls -R app env secret-demo
```

```
app:
Dockerfile
app.py
requirements.txt

env:
green.env
red.env

secret-demo:
Dockerfile
```

`RC=0`

## 3. `cat app/app.py | head -30`

```bash
cat app/app.py | head -30
```

```
"""Color Factory — แอป Flask ตัวเล็ก ๆ ที่ 'บุคลิก' ทั้งหมดมาจาก environment variable

อ่านค่า 3 ตัวจากข้างนอก:
  APP_COLOR  สีของหน้าเว็บ   (default ในโค้ด: blue)
  APP_NAME   ชื่อที่โชว์บนการ์ด (default ในโค้ด: Color Factory)
  APP_PORT   port ที่ Flask ฟัง (default ในโค้ด: 8081)

ไฟล์ build_defaults.json ถูกเขียนตอน docker build จากค่า ENV ใน Dockerfile
แอปจึงบอกได้ว่าค่าที่ใช้อยู่ตอนนี้ "มาจากไหน" — โค้ด / Dockerfile ENV / override ตอน run
"""

import json
import os
import socket

from flask import Flask, jsonify

app = Flask(__name__)

# ---- default ในโค้ด (ชั้นล่างสุดของลำดับความสำคัญ) -------------------------
CODE_DEFAULTS = {
    "APP_COLOR": "blue",
    "APP_NAME": "Color Factory",
    "APP_PORT": "8081",
}

# ---- ค่า ENV ที่ถูก 'อบ' ไว้ใน image ตอน docker build ----------------------
try:
    with open("/app/build_defaults.json", encoding="utf-8") as fh:
        BUILD_DEFAULTS = json.load(fh)
```

`RC=0`

## 4. `cat app/Dockerfile`

```bash
cat app/Dockerfile
```

```
FROM python:3.12-slim

WORKDIR /app

# requirements ก่อน แล้วค่อย COPY โค้ด — layer ของ pip จะได้ถูก cache ไว้
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

# ค่า default ของ image (บุคลิกเริ่มต้นของโรงงาน)
ENV APP_COLOR=blue \
    APP_NAME="Color Factory" \
    APP_PORT=8081

# อบค่า ENV ตอน build ลงไฟล์ เพื่อให้แอปบอกได้ว่าค่าที่ใช้อยู่ถูก override หรือยัง
RUN python -c "import json,os;json.dump({k:os.environ[k] for k in ('APP_COLOR','APP_NAME','APP_PORT')},open('/app/build_defaults.json','w'))"

EXPOSE 8081

CMD ["python", "app.py"]
```

`RC=0`

## 5. `docker build -t color-app:1.0 app/`

```bash
docker build -t color-app:1.0 app/
```

```
#0 building with "default" instance using docker driver

#1 [internal] load build definition from Dockerfile
#1 transferring dockerfile: 860B done
#1 DONE 0.0s

#2 [internal] load metadata for docker.io/library/python:3.12-slim
#2 DONE 1.8s

#3 [internal] load .dockerignore
#3 transferring context: 87B done
#3 DONE 0.0s

#4 [1/6] FROM docker.io/library/python:3.12-slim@sha256:229a2c5bfa27522db7815ea81f9bed70af17ccb9de9fc7ad142b1877b5830d36
#4 resolve docker.io/library/python:3.12-slim@sha256:229a2c5bfa27522db7815ea81f9bed70af17ccb9de9fc7ad142b1877b5830d36 0.0s done
#4 ...

#5 [internal] load build context
#5 transferring context: 6.19kB done
#5 DONE 0.1s

#4 [1/6] FROM docker.io/library/python:3.12-slim@sha256:229a2c5bfa27522db7815ea81f9bed70af17ccb9de9fc7ad142b1877b5830d36
#4 sha256:b3c7a9bdb4f2a30d0a1358438d1539c06b86da99135cfd9d92756863cc87ae18 0B / 249B 0.2s
#4 sha256:b3c7a9bdb4f2a30d0a1358438d1539c06b86da99135cfd9d92756863cc87ae18 249B / 249B 0.3s done
#4 sha256:c85ad0bcaca895afa08053538ec1ea7642c7e9e05f5684d18e3627a2316ca8ae 0B / 12.11MB 0.2s
#4 sha256:5a31db4cd47898e862a567028aa41f7a11d814cf69be6904173402a8b8eac5cb 0B / 1.29MB 0.2s
#4 sha256:26c307b5e35a59ce911f5fde5b9458120ec8734e831ea2da5649a9ad14abfd3d 0B / 29.78MB 0.2s
#4 sha256:c85ad0bcaca895afa08053538ec1ea7642c7e9e05f5684d18e3627a2316ca8ae 2.10MB / 12.11MB 0.6s
#4 sha256:c85ad0bcaca895afa08053538ec1ea7642c7e9e05f5684d18e3627a2316ca8ae 6.29MB / 12.11MB 0.8s
#4 sha256:5a31db4cd47898e862a567028aa41f7a11d814cf69be6904173402a8b8eac5cb 1.29MB / 1.29MB 0.9s done
#4 sha256:c85ad0bcaca895afa08053538ec1ea7642c7e9e05f5684d18e3627a2316ca8ae 12.11MB / 12.11MB 1.1s
#4 sha256:c85ad0bcaca895afa08053538ec1ea7642c7e9e05f5684d18e3627a2316ca8ae 12.11MB / 12.11MB 1.1s done
#4 sha256:26c307b5e35a59ce911f5fde5b9458120ec8734e831ea2da5649a9ad14abfd3d 5.24MB / 29.78MB 1.1s
#4 sha256:26c307b5e35a59ce911f5fde5b9458120ec8734e831ea2da5649a9ad14abfd3d 9.44MB / 29.78MB 1.2s
#4 sha256:26c307b5e35a59ce911f5fde5b9458120ec8734e831ea2da5649a9ad14abfd3d 13.63MB / 29.78MB 1.4s
#4 sha256:26c307b5e35a59ce911f5fde5b9458120ec8734e831ea2da5649a9ad14abfd3d 16.78MB / 29.78MB 1.5s
#4 sha256:26c307b5e35a59ce911f5fde5b9458120ec8734e831ea2da5649a9ad14abfd3d 19.92MB / 29.78MB 1.7s
#4 sha256:26c307b5e35a59ce911f5fde5b9458120ec8734e831ea2da5649a9ad14abfd3d 23.07MB / 29.78MB 1.8s
#4 sha256:26c307b5e35a59ce911f5fde5b9458120ec8734e831ea2da5649a9ad14abfd3d 27.26MB / 29.78MB 2.0s
#4 sha256:26c307b5e35a59ce911f5fde5b9458120ec8734e831ea2da5649a9ad14abfd3d 29.78MB / 29.78MB 2.0s done
#4 extracting sha256:26c307b5e35a59ce911f5fde5b9458120ec8734e831ea2da5649a9ad14abfd3d
#4 extracting sha256:26c307b5e35a59ce911f5fde5b9458120ec8734e831ea2da5649a9ad14abfd3d 0.5s done
#4 DONE 2.8s

#4 [1/6] FROM docker.io/library/python:3.12-slim@sha256:229a2c5bfa27522db7815ea81f9bed70af17ccb9de9fc7ad142b1877b5830d36
#4 extracting sha256:5a31db4cd47898e862a567028aa41f7a11d814cf69be6904173402a8b8eac5cb 0.1s done
#4 extracting sha256:c85ad0bcaca895afa08053538ec1ea7642c7e9e05f5684d18e3627a2316ca8ae
#4 extracting sha256:c85ad0bcaca895afa08053538ec1ea7642c7e9e05f5684d18e3627a2316ca8ae 0.3s done
#4 DONE 3.1s

#4 [1/6] FROM docker.io/library/python:3.12-slim@sha256:229a2c5bfa27522db7815ea81f9bed70af17ccb9de9fc7ad142b1877b5830d36
#4 extracting sha256:b3c7a9bdb4f2a30d0a1358438d1539c06b86da99135cfd9d92756863cc87ae18 0.0s done
#4 DONE 3.2s

#6 [2/6] WORKDIR /app
#6 DONE 0.1s

#7 [3/6] COPY requirements.txt .
#7 DONE 0.1s

#8 [4/6] RUN pip install --no-cache-dir -r requirements.txt
#8 1.141 Collecting flask==3.1.0 (from -r requirements.txt (line 1))
#8 1.182   Downloading flask-3.1.0-py3-none-any.whl.metadata (2.7 kB)
#8 1.199 Collecting Werkzeug>=3.1 (from flask==3.1.0->-r requirements.txt (line 1))
#8 1.206   Downloading werkzeug-3.1.8-py3-none-any.whl.metadata (4.0 kB)
#8 1.217 Collecting Jinja2>=3.1.2 (from flask==3.1.0->-r requirements.txt (line 1))
#8 1.227   Downloading jinja2-3.1.6-py3-none-any.whl.metadata (2.9 kB)
#8 1.237 Collecting itsdangerous>=2.2 (from flask==3.1.0->-r requirements.txt (line 1))
#8 1.245   Downloading itsdangerous-2.2.0-py3-none-any.whl.metadata (1.9 kB)
#8 1.258 Collecting click>=8.1.3 (from flask==3.1.0->-r requirements.txt (line 1))
#8 1.266   Downloading click-8.4.2-py3-none-any.whl.metadata (2.6 kB)
#8 1.276 Collecting blinker>=1.9 (from flask==3.1.0->-r requirements.txt (line 1))
#8 1.285   Downloading blinker-1.9.0-py3-none-any.whl.metadata (1.6 kB)
#8 1.317 Collecting MarkupSafe>=2.0 (from Jinja2>=3.1.2->flask==3.1.0->-r requirements.txt (line 1))
#8 1.324   Downloading markupsafe-3.0.3-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl.metadata (2.7 kB)
#8 1.335 Downloading flask-3.1.0-py3-none-any.whl (102 kB)
#8 1.353 Downloading blinker-1.9.0-py3-none-any.whl (8.5 kB)
#8 1.360 Downloading click-8.4.2-py3-none-any.whl (119 kB)
#8 1.373 Downloading itsdangerous-2.2.0-py3-none-any.whl (16 kB)
#8 1.380 Downloading jinja2-3.1.6-py3-none-any.whl (134 kB)
#8 1.391 Downloading werkzeug-3.1.8-py3-none-any.whl (226 kB)
#8 1.418 Downloading markupsafe-3.0.3-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (22 kB)
#8 1.431 Installing collected packages: MarkupSafe, itsdangerous, click, blinker, Werkzeug, Jinja2, flask
#8 1.754 Successfully installed Jinja2-3.1.6 MarkupSafe-3.0.3 Werkzeug-3.1.8 blinker-1.9.0 click-8.4.2 flask-3.1.0 itsdangerous-2.2.0
#8 1.755 WARNING: Running pip as the 'root' user can result in broken permissions and conflicting behaviour with the system package manager, possibly rendering your system unusable. It is recommended to use a virtual environment instead: https://pip.pypa.io/warnings/venv. Use the --root-user-action option if you know what you are doing and want to suppress this warning.
#8 1.827 
#8 1.827 [notice] A new release of pip is available: 25.0.1 -> 26.2.1
#8 1.827 [notice] To update, run: pip install --upgrade pip
#8 DONE 1.9s

#9 [5/6] COPY app.py .
#9 DONE 0.1s

#10 [6/6] RUN python -c "import json,os;json.dump({k:os.environ[k] for k in ('APP_COLOR','APP_NAME','APP_PORT')},open('/app/build_defaults.json','w'))"
#10 DONE 0.4s

#11 exporting to image
#11 exporting layers
#11 exporting layers 0.6s done
#11 exporting manifest sha256:6923d33d1f2651d7cfed9506b4840129149e07659a5fd2377933c4344bf997a1 0.0s done
#11 exporting config sha256:e41e648447246521fd7be9c690b53ae83cf71e9c4ab4193fe057c251c0b818c3 0.0s done
#11 exporting attestation manifest sha256:d5f483f6d7c2b43679387321d5dee918aec14b76c7e0b5d728ad1dba40d09504 0.1s done
#11 exporting manifest list sha256:0fcb989cc8e778dd78a932d25c49bde3e6acd897ea9a5d06690dde68abfdf68d
#11 exporting manifest list sha256:0fcb989cc8e778dd78a932d25c49bde3e6acd897ea9a5d06690dde68abfdf68d 0.0s done
#11 naming to docker.io/library/color-app:1.0 done
#11 unpacking to docker.io/library/color-app:1.0
#11 unpacking to docker.io/library/color-app:1.0 0.2s done
#11 DONE 1.0s
```

`RC=0`

## 6. `docker images color-app`

```bash
docker images color-app
```

```
IMAGE           ID             DISK USAGE   CONTENT SIZE   EXTRA
color-app:1.0   0fcb989cc8e7        197MB         48.2MB        
```

`RC=0`

## 7. `docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.Size}}" color-app`

```bash
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.Size}}" color-app
```

```
REPOSITORY   TAG       IMAGE ID       SIZE
color-app    1.0       0fcb989cc8e7   197MB
```

`RC=0`

## 8. `docker run -d --name color-red   -e APP_COLOR=red                            -p 8081:8081 color-app:1.0`

```bash
docker run -d --name color-red   -e APP_COLOR=red                            -p 8081:8081 color-app:1.0
```

```
afed10122c2f49204bc089b95125748a052d208352db0a56cc4f4798810f2d6c
```

`RC=0`

## 9. `docker run -d --name color-green -e APP_COLOR=green -e APP_NAME="Green Factory" -p 8082:8081 color-app:1.0`

```bash
docker run -d --name color-green -e APP_COLOR=green -e APP_NAME="Green Factory" -p 8082:8081 color-app:1.0
```

```
9a2d2bd7a4e4156d4e5240f12e2b6bf70ce6b5c42a6b50950a2dd56c83e1e2fa
```

`RC=0`

## 10. `docker run -d --name color-blue                                              -p 8083:8081 color-app:1.0`

```bash
docker run -d --name color-blue                                              -p 8083:8081 color-app:1.0
```

```
33976a090f8cddbd3dfd3e3de3ee50d1854702f4d96f82f353f1b8035a46bc37
```

`RC=0`

## 11. `docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"`

```bash
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"
```

```
NAMES         IMAGE           STATUS         PORTS
color-blue    color-app:1.0   Up 2 seconds   0.0.0.0:8083->8081/tcp, [::]:8083->8081/tcp
color-green   color-app:1.0   Up 2 seconds   0.0.0.0:8082->8081/tcp, [::]:8082->8081/tcp
color-red     color-app:1.0   Up 3 seconds   0.0.0.0:8081->8081/tcp, [::]:8081->8081/tcp
```

`RC=0`

## 12. `docker inspect --format '{{.Name}} -> {{.Image}}' color-red color-green color-blue`

```bash
docker inspect --format '{{.Name}} -> {{.Image}}' color-red color-green color-blue
```

```
/color-red -> sha256:0fcb989cc8e778dd78a932d25c49bde3e6acd897ea9a5d06690dde68abfdf68d
/color-green -> sha256:0fcb989cc8e778dd78a932d25c49bde3e6acd897ea9a5d06690dde68abfdf68d
/color-blue -> sha256:0fcb989cc8e778dd78a932d25c49bde3e6acd897ea9a5d06690dde68abfdf68d
```

`RC=0`

## 13. `curl -s http://localhost:8081/healthz | python3 -m json.tool | head -6`

```bash
curl -s http://localhost:8081/healthz | python3 -m json.tool | head -6
```

```
{
    "app_color": "red",
    "app_color_source": "override at run (-e / --env-file)",
    "app_name": "Color Factory",
    "app_name_source": "Dockerfile ENV",
    "app_port": "8081",
```

`RC=0`

## 14. `curl -s http://localhost:8082/healthz | python3 -m json.tool | head -6`

```bash
curl -s http://localhost:8082/healthz | python3 -m json.tool | head -6
```

```
{
    "app_color": "green",
    "app_color_source": "override at run (-e / --env-file)",
    "app_name": "Green Factory",
    "app_name_source": "override at run (-e / --env-file)",
    "app_port": "8081",
```

`RC=0`

## 15. `curl -s http://localhost:8083/healthz | python3 -m json.tool | head -6`

```bash
curl -s http://localhost:8083/healthz | python3 -m json.tool | head -6
```

```
{
    "app_color": "blue",
    "app_color_source": "Dockerfile ENV",
    "app_name": "Color Factory",
    "app_name_source": "Dockerfile ENV",
    "app_port": "8081",
```

`RC=0`

## 16. `docker exec color-red env | grep APP_`

```bash
docker exec color-red env | grep APP_
```

```
APP_COLOR=red
APP_NAME=Color Factory
APP_PORT=8081
```

`RC=0`

## 17. `docker exec color-blue env | grep APP_`

```bash
docker exec color-blue env | grep APP_
```

```
APP_COLOR=blue
APP_NAME=Color Factory
APP_PORT=8081
```

`RC=0`

## 18. `docker inspect --format '{{json .Config.Env}}' color-red`

```bash
docker inspect --format '{{json .Config.Env}}' color-red
```

```
["APP_COLOR=red","PATH=/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin","LANG=C.UTF-8","GPG_KEY=7169605F62C751356D054A26A821E680E5FA6305","PYTHON_VERSION=3.12.13","PYTHON_SHA256=c08bc65a81971c1dd5783182826503369466c7e67374d1646519adf05207b684","APP_NAME=Color Factory","APP_PORT=8081"]
```

`RC=0`

## 19. `docker exec -e APP_COLOR=green color-red env | grep APP_COLOR`

```bash
docker exec -e APP_COLOR=green color-red env | grep APP_COLOR
```

```
APP_COLOR=green
```

`RC=0`

## 20. `curl -s http://localhost:8081/healthz | python3 -m json.tool | head -3`

```bash
curl -s http://localhost:8081/healthz | python3 -m json.tool | head -3
```

```
{
    "app_color": "red",
    "app_color_source": "override at run (-e / --env-file)",
```

`RC=0`

## 21. `cat env/red.env`

```bash
cat env/red.env
```

```
# env-file: หนึ่งบรรทัดหนึ่งตัวแปร รูปแบบ KEY=VALUE
# ห้ามใส่เครื่องหมาย " " ครอบค่า เพราะ Docker จะถือว่าเครื่องหมายเป็นส่วนหนึ่งของค่า
APP_COLOR=red
APP_NAME=Red Factory
```

`RC=0`

## 22. `docker run -d --name color-envfile --env-file env/red.env -p 8084:8081 color-app:1.0`

```bash
docker run -d --name color-envfile --env-file env/red.env -p 8084:8081 color-app:1.0
```

```
3c3d24a5ad39dc8ecdd5a5ef0242a26185b249079ceb1270531fc7bdffedf6fc
```

`RC=0`

## 23. `curl -s http://localhost:8084/healthz | python3 -m json.tool | head -6`

```bash
curl -s http://localhost:8084/healthz | python3 -m json.tool | head -6
```

```
{
    "app_color": "red",
    "app_color_source": "override at run (-e / --env-file)",
    "app_name": "Red Factory",
    "app_name_source": "override at run (-e / --env-file)",
    "app_port": "8081",
```

`RC=0`

## 24. `docker run -d --name color-boss --env-file env/red.env -e APP_COLOR=pink -p 8085:8081 color-app:1.0`

```bash
docker run -d --name color-boss --env-file env/red.env -e APP_COLOR=pink -p 8085:8081 color-app:1.0
```

```
2a671c2a960b70abc785efd0a33efd5f81f617162d67312374e80e11d2859c43
```

`RC=0`

## 25. `curl -s http://localhost:8085/healthz | python3 -m json.tool | head -6`

```bash
curl -s http://localhost:8085/healthz | python3 -m json.tool | head -6
```

```
{
    "app_color": "pink",
    "app_color_source": "override at run (-e / --env-file)",
    "app_name": "Red Factory",
    "app_name_source": "override at run (-e / --env-file)",
    "app_port": "8081",
```

`RC=0`

## 26. `docker exec color-boss env | grep APP_`

```bash
docker exec color-boss env | grep APP_
```

```
APP_NAME=Red Factory
APP_COLOR=pink
APP_PORT=8081
```

`RC=0`

## 27. `docker inspect --format '{{json .Config.Env}}' color-boss`

```bash
docker inspect --format '{{json .Config.Env}}' color-boss
```

```
["APP_COLOR=red","APP_NAME=Red Factory","APP_COLOR=pink","PATH=/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin","LANG=C.UTF-8","GPG_KEY=7169605F62C751356D054A26A821E680E5FA6305","PYTHON_VERSION=3.12.13","PYTHON_SHA256=c08bc65a81971c1dd5783182826503369466c7e67374d1646519adf05207b684","APP_PORT=8081"]
```

`RC=0`

## 28. `docker image inspect color-app:1.0 | head -30`

```bash
docker image inspect color-app:1.0 | head -30
```

```
[
    {
        "Id": "sha256:0fcb989cc8e778dd78a932d25c49bde3e6acd897ea9a5d06690dde68abfdf68d",
        "RepoTags": [
            "color-app:1.0"
        ],
        "RepoDigests": [
            "color-app@sha256:0fcb989cc8e778dd78a932d25c49bde3e6acd897ea9a5d06690dde68abfdf68d"
        ],
        "Comment": "buildkit.dockerfile.v0",
        "Created": "2026-08-12T19:27:32.399173669+07:00",
        "Config": {
            "ExposedPorts": {
                "8081/tcp": {}
            },
            "Env": [
                "PATH=/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
                "LANG=C.UTF-8",
                "GPG_KEY=7169605F62C751356D054A26A821E680E5FA6305",
                "PYTHON_VERSION=3.12.13",
                "PYTHON_SHA256=c08bc65a81971c1dd5783182826503369466c7e67374d1646519adf05207b684",
                "APP_COLOR=blue",
                "APP_NAME=Color Factory",
                "APP_PORT=8081"
            ],
            "Cmd": [
                "python",
                "app.py"
            ],
            "WorkingDir": "/app",
```

`RC=0`

## 29. `docker image inspect --format '{{json .Config.Env}}' color-app:1.0`

```bash
docker image inspect --format '{{json .Config.Env}}' color-app:1.0
```

```
["PATH=/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin","LANG=C.UTF-8","GPG_KEY=7169605F62C751356D054A26A821E680E5FA6305","PYTHON_VERSION=3.12.13","PYTHON_SHA256=c08bc65a81971c1dd5783182826503369466c7e67374d1646519adf05207b684","APP_COLOR=blue","APP_NAME=Color Factory","APP_PORT=8081"]
```

`RC=0`

## 30. `docker image inspect --format '{{json .Config.Cmd}}' color-app:1.0`

```bash
docker image inspect --format '{{json .Config.Cmd}}' color-app:1.0
```

```
["python","app.py"]
```

`RC=0`

## 31. `docker image inspect --format '{{json .Config.ExposedPorts}}' color-app:1.0`

```bash
docker image inspect --format '{{json .Config.ExposedPorts}}' color-app:1.0
```

```
{"8081/tcp":{}}
```

`RC=0`

## 32. `docker image inspect --format 'arch={{.Architecture}}  os={{.Os}}  size={{.Size}} bytes  workdir={{.Config.WorkingDir}}'`

```bash
docker image inspect --format 'arch={{.Architecture}}  os={{.Os}}  size={{.Size}} bytes  workdir={{.Config.WorkingDir}}' color-app:1.0
```

```
arch=amd64  os=linux  size=48162906 bytes  workdir=/app
```

`RC=0`

## 33. `cat secret-demo/Dockerfile`

```bash
cat secret-demo/Dockerfile
```

```
# ตัวอย่าง "วิธีที่ผิด" — ใช้สาธิตว่า ARG/ENV ไม่ใช่ที่เก็บความลับ
# ค่าทั้งสองบรรทัดนี้เป็นค่าสมมติสำหรับสอนเท่านั้น ห้ามใส่ค่าจริงลงใน Dockerfile
FROM alpine:3.21

ARG DB_PASSWORD=not-a-real-password-1234
ENV API_TOKEN=not-a-real-token-abcd

RUN echo "building with DB_PASSWORD=$DB_PASSWORD" > /build.log

CMD ["sh", "-c", "echo leaky image"]
```

`RC=0`

## 34. `docker build -t leaky:1.0 secret-demo/ 2>&1 | grep -a "SecretsUsedInArgOrEnv" | sed "s/\x1b\[[0-9;]*m//g"`

```bash
docker build -t leaky:1.0 secret-demo/ 2>&1 | grep -a "SecretsUsedInArgOrEnv" | sed "s/\x1b\[[0-9;]*m//g"
```

```
 - SecretsUsedInArgOrEnv: Do not use ARG or ENV instructions for sensitive data (ARG "DB_PASSWORD") (line 5)
 - SecretsUsedInArgOrEnv: Do not use ARG or ENV instructions for sensitive data (ENV "API_TOKEN") (line 6)
```

`RC=0`

## 35. `docker image inspect --format '{{json .Config.Env}}' leaky:1.0`

```bash
docker image inspect --format '{{json .Config.Env}}' leaky:1.0
```

```
["PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin","API_TOKEN=not-a-real-token-abcd"]
```

`RC=0`

## 36. `docker history --no-trunc --format "table {{.CreatedBy}}" leaky:1.0`

```bash
docker history --no-trunc --format "table {{.CreatedBy}}" leaky:1.0
```

```
CREATED BY
CMD ["sh" "-c" "echo leaky image"]
RUN |1 DB_PASSWORD=not-a-real-password-1234 /bin/sh -c echo "building with DB_PASSWORD=$DB_PASSWORD" > /build.log # buildkit
ENV API_TOKEN=not-a-real-token-abcd
ARG DB_PASSWORD=not-a-real-password-1234
CMD ["/bin/sh"]
ADD alpine-minirootfs-3.21.7-x86_64.tar.gz / # buildkit
```

`RC=0`

## 37. `docker rm -f color-red color-green color-blue color-envfile color-boss`

```bash
docker rm -f color-red color-green color-blue color-envfile color-boss
```

```
color-red
color-green
color-blue
color-envfile
color-boss
```

`RC=0`

## 38. `docker rmi color-app:1.0 leaky:1.0`

```bash
docker rmi color-app:1.0 leaky:1.0
```

```
Untagged: color-app:1.0
Deleted: sha256:0fcb989cc8e778dd78a932d25c49bde3e6acd897ea9a5d06690dde68abfdf68d
Untagged: leaky:1.0
Deleted: sha256:6c21fbac6bd16b78ca34f66374d0dce7458bfebd58fce7e9ac35f5bd5ab5081c
```

`RC=0`

## 39. `docker ps -a`

```bash
docker ps -a
```

```
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
```

`RC=0`

## 40. `docker images`

```bash
docker images
```

```
IMAGE   ID             DISK USAGE   CONTENT SIZE   EXTRA
```

`RC=0`

