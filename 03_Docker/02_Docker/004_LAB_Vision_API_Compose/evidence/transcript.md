# evidence — LAB 4 (004_LAB_Vision_API_Compose)

ทุกบล็อกด้านล่างคือคำสั่งจริงที่รันในเครื่องเรียน `tuchsanai/devtools:2569_1`
(outer container `devtools-lab004`, ports 2225:22 · 18041:8501 · 18042:8000)
และ output จริงที่ได้กลับมา — README.md ยกมาจากไฟล์นี้เท่านั้น

### $ docker --version; docker compose version

```bash
docker --version; docker compose version
```

```
Docker version 29.6.2, build dfc4efb
Docker Compose version v5.3.1
```

_exit code: 0_

### $ ls -R . | head -30

```bash
ls -R . | head -30
```

```
.:
backend
compose.yaml
env.example
frontend

./backend:
Dockerfile
main.py
requirements.txt

./frontend:
Dockerfile
app.py
requirements.txt
static

./frontend/static:
make_sample.py
sample.jpg
```

_exit code: 0_

### $ docker network create visionnet

```bash
docker network create visionnet
```

```
16205aa6d65436eda4783850c0a9757a50bc3901b366afdeac53b97d0bc56d3e
```

_exit code: 0_

### $ docker build -t vision-backend:1.0 backend/

```bash
docker build -t vision-backend:1.0 backend/
```

```
#0 building with "default" instance using docker driver

#1 [internal] load build definition from Dockerfile
#1 transferring dockerfile: 544B done
#1 DONE 0.1s

#2 [internal] load metadata for docker.io/library/python:3.12-slim
#2 DONE 2.9s

#3 [internal] load .dockerignore
#3 transferring context: 78B done
#3 DONE 0.1s

#4 [internal] load build context
#4 transferring context: 2.12kB done
#4 DONE 0.1s

#5 [1/5] FROM docker.io/library/python:3.12-slim@sha256:229a2c5bfa27522db7815ea81f9bed70af17ccb9de9fc7ad142b1877b5830d36
#5 resolve docker.io/library/python:3.12-slim@sha256:229a2c5bfa27522db7815ea81f9bed70af17ccb9de9fc7ad142b1877b5830d36 0.1s done
#5 DONE 0.2s

#5 [1/5] FROM docker.io/library/python:3.12-slim@sha256:229a2c5bfa27522db7815ea81f9bed70af17ccb9de9fc7ad142b1877b5830d36
#5 sha256:b3c7a9bdb4f2a30d0a1358438d1539c06b86da99135cfd9d92756863cc87ae18 0B / 249B 0.2s
#5 sha256:b3c7a9bdb4f2a30d0a1358438d1539c06b86da99135cfd9d92756863cc87ae18 249B / 249B 0.3s done
#5 sha256:c85ad0bcaca895afa08053538ec1ea7642c7e9e05f5684d18e3627a2316ca8ae 0B / 12.11MB 0.2s
#5 sha256:5a31db4cd47898e862a567028aa41f7a11d814cf69be6904173402a8b8eac5cb 0B / 1.29MB 0.2s
#5 sha256:26c307b5e35a59ce911f5fde5b9458120ec8734e831ea2da5649a9ad14abfd3d 0B / 29.78MB 0.2s
#5 sha256:c85ad0bcaca895afa08053538ec1ea7642c7e9e05f5684d18e3627a2316ca8ae 1.05MB / 12.11MB 0.6s
#5 sha256:c85ad0bcaca895afa08053538ec1ea7642c7e9e05f5684d18e3627a2316ca8ae 3.15MB / 12.11MB 0.8s
#5 sha256:c85ad0bcaca895afa08053538ec1ea7642c7e9e05f5684d18e3627a2316ca8ae 6.29MB / 12.11MB 0.9s
#5 sha256:c85ad0bcaca895afa08053538ec1ea7642c7e9e05f5684d18e3627a2316ca8ae 9.44MB / 12.11MB 1.1s
#5 sha256:5a31db4cd47898e862a567028aa41f7a11d814cf69be6904173402a8b8eac5cb 1.29MB / 1.29MB 0.9s done
#5 sha256:c85ad0bcaca895afa08053538ec1ea7642c7e9e05f5684d18e3627a2316ca8ae 12.11MB / 12.11MB 1.2s done
#5 sha256:26c307b5e35a59ce911f5fde5b9458120ec8734e831ea2da5649a9ad14abfd3d 3.15MB / 29.78MB 1.1s
#5 sha256:26c307b5e35a59ce911f5fde5b9458120ec8734e831ea2da5649a9ad14abfd3d 9.44MB / 29.78MB 1.4s
#5 sha256:26c307b5e35a59ce911f5fde5b9458120ec8734e831ea2da5649a9ad14abfd3d 12.58MB / 29.78MB 1.5s
#5 sha256:26c307b5e35a59ce911f5fde5b9458120ec8734e831ea2da5649a9ad14abfd3d 17.83MB / 29.78MB 1.7s
#5 sha256:26c307b5e35a59ce911f5fde5b9458120ec8734e831ea2da5649a9ad14abfd3d 22.02MB / 29.78MB 1.8s
#5 sha256:26c307b5e35a59ce911f5fde5b9458120ec8734e831ea2da5649a9ad14abfd3d 26.21MB / 29.78MB 2.0s
#5 sha256:26c307b5e35a59ce911f5fde5b9458120ec8734e831ea2da5649a9ad14abfd3d 29.78MB / 29.78MB 2.1s done
#5 extracting sha256:26c307b5e35a59ce911f5fde5b9458120ec8734e831ea2da5649a9ad14abfd3d
#5 extracting sha256:26c307b5e35a59ce911f5fde5b9458120ec8734e831ea2da5649a9ad14abfd3d 0.5s done
#5 DONE 2.9s

#5 [1/5] FROM docker.io/library/python:3.12-slim@sha256:229a2c5bfa27522db7815ea81f9bed70af17ccb9de9fc7ad142b1877b5830d36
#5 extracting sha256:5a31db4cd47898e862a567028aa41f7a11d814cf69be6904173402a8b8eac5cb 0.1s done
#5 extracting sha256:c85ad0bcaca895afa08053538ec1ea7642c7e9e05f5684d18e3627a2316ca8ae
#5 extracting sha256:c85ad0bcaca895afa08053538ec1ea7642c7e9e05f5684d18e3627a2316ca8ae 0.3s done
#5 DONE 3.2s

#5 [1/5] FROM docker.io/library/python:3.12-slim@sha256:229a2c5bfa27522db7815ea81f9bed70af17ccb9de9fc7ad142b1877b5830d36
#5 extracting sha256:b3c7a9bdb4f2a30d0a1358438d1539c06b86da99135cfd9d92756863cc87ae18 0.0s done
#5 DONE 3.2s

#6 [2/5] WORKDIR /app
#6 DONE 0.1s

#7 [3/5] COPY requirements.txt .
#7 DONE 0.1s

#8 [4/5] RUN pip install --no-cache-dir -r requirements.txt
#8 1.056 Collecting fastapi==0.115.6 (from -r requirements.txt (line 1))
#8 1.104   Downloading fastapi-0.115.6-py3-none-any.whl.metadata (27 kB)
#8 1.132 Collecting uvicorn==0.34.0 (from uvicorn[standard]==0.34.0->-r requirements.txt (line 2))
#8 1.142   Downloading uvicorn-0.34.0-py3-none-any.whl.metadata (6.5 kB)
#8 1.173 Collecting opencv-python-headless==4.10.0.84 (from -r requirements.txt (line 3))
#8 1.183   Downloading opencv_python_headless-4.10.0.84-cp37-abi3-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (20 kB)
#8 1.308 Collecting numpy==2.2.1 (from -r requirements.txt (line 4))
#8 1.320   Downloading numpy-2.2.1-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (62 kB)
#8 1.392 Collecting pydantic==2.10.4 (from -r requirements.txt (line 5))
#8 1.402   Downloading pydantic-2.10.4-py3-none-any.whl.metadata (29 kB)
#8 1.424 Collecting starlette<0.42.0,>=0.40.0 (from fastapi==0.115.6->-r requirements.txt (line 1))
#8 1.434   Downloading starlette-0.41.3-py3-none-any.whl.metadata (6.0 kB)
#8 1.467 Collecting typing-extensions>=4.8.0 (from fastapi==0.115.6->-r requirements.txt (line 1))
#8 1.473   Downloading typing_extensions-4.16.0-py3-none-any.whl.metadata (3.3 kB)
#8 1.487 Collecting click>=7.0 (from uvicorn==0.34.0->uvicorn[standard]==0.34.0->-r requirements.txt (line 2))
#8 1.493   Downloading click-8.4.2-py3-none-any.whl.metadata (2.6 kB)
#8 1.500 Collecting h11>=0.8 (from uvicorn==0.34.0->uvicorn[standard]==0.34.0->-r requirements.txt (line 2))
#8 1.508   Downloading h11-0.16.0-py3-none-any.whl.metadata (8.3 kB)
#8 1.535 Collecting annotated-types>=0.6.0 (from pydantic==2.10.4->-r requirements.txt (line 5))
#8 1.543   Downloading annotated_types-0.8.0-py3-none-any.whl.metadata (15 kB)
#8 1.854 Collecting pydantic-core==2.27.2 (from pydantic==2.10.4->-r requirements.txt (line 5))
#8 1.862   Downloading pydantic_core-2.27.2-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (6.6 kB)
#8 1.883 Collecting httptools>=0.6.3 (from uvicorn[standard]==0.34.0->-r requirements.txt (line 2))
#8 1.893   Downloading httptools-0.8.0-cp312-cp312-manylinux1_x86_64.manylinux_2_28_x86_64.manylinux_2_5_x86_64.whl.metadata (3.5 kB)
#8 1.905 Collecting python-dotenv>=0.13 (from uvicorn[standard]==0.34.0->-r requirements.txt (line 2))
#8 1.914   Downloading python_dotenv-1.2.2-py3-none-any.whl.metadata (27 kB)
#8 1.938 Collecting pyyaml>=5.1 (from uvicorn[standard]==0.34.0->-r requirements.txt (line 2))
#8 1.947   Downloading pyyaml-6.0.3-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl.metadata (2.4 kB)
#8 1.971 Collecting uvloop!=0.15.0,!=0.15.1,>=0.14.0 (from uvicorn[standard]==0.34.0->-r requirements.txt (line 2))
#8 1.981   Downloading uvloop-0.22.1-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl.metadata (4.9 kB)
#8 2.024 Collecting watchfiles>=0.13 (from uvicorn[standard]==0.34.0->-r requirements.txt (line 2))
#8 2.035   Downloading watchfiles-1.2.0-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (4.9 kB)
#8 2.085 Collecting websockets>=10.4 (from uvicorn[standard]==0.34.0->-r requirements.txt (line 2))
#8 2.093   Downloading websockets-17.0.1-cp312-cp312-manylinux1_x86_64.manylinux_2_28_x86_64.manylinux_2_5_x86_64.whl.metadata (6.3 kB)
#8 2.111 Collecting anyio<5,>=3.4.0 (from starlette<0.42.0,>=0.40.0->fastapi==0.115.6->-r requirements.txt (line 1))
#8 2.118   Downloading anyio-4.14.2-py3-none-any.whl.metadata (4.6 kB)
#8 2.135 Collecting idna>=2.8 (from anyio<5,>=3.4.0->starlette<0.42.0,>=0.40.0->fastapi==0.115.6->-r requirements.txt (line 1))
#8 2.142   Downloading idna-3.18-py3-none-any.whl.metadata (6.1 kB)
#8 2.155 Downloading fastapi-0.115.6-py3-none-any.whl (94 kB)
#8 2.164 Downloading uvicorn-0.34.0-py3-none-any.whl (62 kB)
#8 2.176 Downloading opencv_python_headless-4.10.0.84-cp37-abi3-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (49.9 MB)
#8 4.367    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 49.9/49.9 MB 22.9 MB/s eta 0:00:00
#8 4.378 Downloading numpy-2.2.1-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (16.1 MB)
#8 5.028    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 16.1/16.1 MB 24.7 MB/s eta 0:00:00
#8 5.036 Downloading pydantic-2.10.4-py3-none-any.whl (431 kB)
#8 5.056 Downloading pydantic_core-2.27.2-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (2.0 MB)
#8 5.116    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 2.0/2.0 MB 34.1 MB/s eta 0:00:00
#8 5.123 Downloading annotated_types-0.8.0-py3-none-any.whl (13 kB)
#8 5.130 Downloading click-8.4.2-py3-none-any.whl (119 kB)
#8 5.143 Downloading h11-0.16.0-py3-none-any.whl (37 kB)
#8 5.153 Downloading httptools-0.8.0-cp312-cp312-manylinux1_x86_64.manylinux_2_28_x86_64.manylinux_2_5_x86_64.whl (523 kB)
#8 5.176 Downloading python_dotenv-1.2.2-py3-none-any.whl (22 kB)
#8 5.184 Downloading pyyaml-6.0.3-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (807 kB)
#8 5.218    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 807.9/807.9 kB 20.2 MB/s eta 0:00:00
#8 5.224 Downloading starlette-0.41.3-py3-none-any.whl (73 kB)
#8 5.235 Downloading typing_extensions-4.16.0-py3-none-any.whl (45 kB)
#8 5.248 Downloading uvloop-0.22.1-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (4.4 MB)
#8 5.498    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 4.4/4.4 MB 17.3 MB/s eta 0:00:00
#8 5.504 Downloading watchfiles-1.2.0-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (456 kB)
#8 5.547 Downloading websockets-17.0.1-cp312-cp312-manylinux1_x86_64.manylinux_2_28_x86_64.manylinux_2_5_x86_64.whl (220 kB)
#8 5.581 Downloading anyio-4.14.2-py3-none-any.whl (125 kB)
#8 5.601 Downloading idna-3.18-py3-none-any.whl (65 kB)
#8 5.671 Installing collected packages: websockets, uvloop, typing-extensions, pyyaml, python-dotenv, numpy, idna, httptools, h11, click, annotated-types, uvicorn, pydantic-core, opencv-python-headless, anyio, watchfiles, starlette, pydantic, fastapi
#8 7.975 Successfully installed annotated-types-0.8.0 anyio-4.14.2 click-8.4.2 fastapi-0.115.6 h11-0.16.0 httptools-0.8.0 idna-3.18 numpy-2.2.1 opencv-python-headless-4.10.0.84 pydantic-2.10.4 pydantic-core-2.27.2 python-dotenv-1.2.2 pyyaml-6.0.3 starlette-0.41.3 typing-extensions-4.16.0 uvicorn-0.34.0 uvloop-0.22.1 watchfiles-1.2.0 websockets-17.0.1
#8 7.975 WARNING: Running pip as the 'root' user can result in broken permissions and conflicting behaviour with the system package manager, possibly rendering your system unusable. It is recommended to use a virtual environment instead: https://pip.pypa.io/warnings/venv. Use the --root-user-action option if you know what you are doing and want to suppress this warning.
#8 8.029 
#8 8.029 [notice] A new release of pip is available: 25.0.1 -> 26.2.1
#8 8.029 [notice] To update, run: pip install --upgrade pip
#8 DONE 8.2s

#9 [5/5] COPY main.py .
#9 DONE 0.1s

#10 exporting to image
#10 exporting layers
#10 exporting layers 5.1s done
#10 exporting manifest sha256:8233905fa786579ecfd0b915b92f278cf4e05f3aa4b09d9e0176ddad0986e412 0.0s done
#10 exporting config sha256:160ecc63cad55b2be5bf97694feac19608e45c5c053494b47f9b951bf99795b5 0.0s done
#10 exporting attestation manifest sha256:51f1f464a4b49e94ec6a5610febf898b2ecf66c7e27f24f1f7c66722f771b330 0.1s done
#10 exporting manifest list sha256:330bb090509402999d9d9e86754bef017e9d0c86199583581a7de3e5f22785d8
#10 exporting manifest list sha256:330bb090509402999d9d9e86754bef017e9d0c86199583581a7de3e5f22785d8 0.0s done
#10 naming to docker.io/library/vision-backend:1.0 done
#10 unpacking to docker.io/library/vision-backend:1.0
#10 unpacking to docker.io/library/vision-backend:1.0 1.4s done
#10 DONE 6.7s
```

_exit code: 0_

### $ docker build -t vision-frontend:1.0 frontend/

```bash
docker build -t vision-frontend:1.0 frontend/
```

```
#0 building with "default" instance using docker driver

#1 [internal] load build definition from Dockerfile
#1 transferring dockerfile: 314B done
#1 DONE 0.0s

#2 [internal] load metadata for docker.io/library/python:3.12-slim
#2 DONE 0.3s

#3 [internal] load .dockerignore
#3 transferring context: 88B done
#3 DONE 0.0s

#4 [1/6] FROM docker.io/library/python:3.12-slim@sha256:229a2c5bfa27522db7815ea81f9bed70af17ccb9de9fc7ad142b1877b5830d36
#4 resolve docker.io/library/python:3.12-slim@sha256:229a2c5bfa27522db7815ea81f9bed70af17ccb9de9fc7ad142b1877b5830d36 0.1s done
#4 DONE 0.1s

#5 [internal] load build context
#5 transferring context: 52.08kB done
#5 DONE 0.1s

#6 [2/6] WORKDIR /app
#6 CACHED

#7 [3/6] COPY requirements.txt .
#7 DONE 0.1s

#8 [4/6] RUN pip install --no-cache-dir -r requirements.txt
#8 1.074 Collecting flask==3.1.0 (from -r requirements.txt (line 1))
#8 1.116   Downloading flask-3.1.0-py3-none-any.whl.metadata (2.7 kB)
#8 1.138 Collecting requests==2.32.3 (from -r requirements.txt (line 2))
#8 1.150   Downloading requests-2.32.3-py3-none-any.whl.metadata (4.6 kB)
#8 1.168 Collecting Werkzeug>=3.1 (from flask==3.1.0->-r requirements.txt (line 1))
#8 1.177   Downloading werkzeug-3.1.8-py3-none-any.whl.metadata (4.0 kB)
#8 1.190 Collecting Jinja2>=3.1.2 (from flask==3.1.0->-r requirements.txt (line 1))
#8 1.198   Downloading jinja2-3.1.6-py3-none-any.whl.metadata (2.9 kB)
#8 1.208 Collecting itsdangerous>=2.2 (from flask==3.1.0->-r requirements.txt (line 1))
#8 1.215   Downloading itsdangerous-2.2.0-py3-none-any.whl.metadata (1.9 kB)
#8 1.228 Collecting click>=8.1.3 (from flask==3.1.0->-r requirements.txt (line 1))
#8 1.236   Downloading click-8.4.2-py3-none-any.whl.metadata (2.6 kB)
#8 1.245 Collecting blinker>=1.9 (from flask==3.1.0->-r requirements.txt (line 1))
#8 1.252   Downloading blinker-1.9.0-py3-none-any.whl.metadata (1.6 kB)
#8 1.315 Collecting charset-normalizer<4,>=2 (from requests==2.32.3->-r requirements.txt (line 2))
#8 1.324   Downloading charset_normalizer-3.4.9-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl.metadata (41 kB)
#8 1.344 Collecting idna<4,>=2.5 (from requests==2.32.3->-r requirements.txt (line 2))
#8 1.354   Downloading idna-3.18-py3-none-any.whl.metadata (6.1 kB)
#8 1.376 Collecting urllib3<3,>=1.21.1 (from requests==2.32.3->-r requirements.txt (line 2))
#8 1.386   Downloading urllib3-2.7.0-py3-none-any.whl.metadata (6.9 kB)
#8 1.401 Collecting certifi>=2017.4.17 (from requests==2.32.3->-r requirements.txt (line 2))
#8 1.408   Downloading certifi-2026.7.22-py3-none-any.whl.metadata (2.5 kB)
#8 1.455 Collecting MarkupSafe>=2.0 (from Jinja2>=3.1.2->flask==3.1.0->-r requirements.txt (line 1))
#8 1.465   Downloading markupsafe-3.0.3-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl.metadata (2.7 kB)
#8 1.477 Downloading flask-3.1.0-py3-none-any.whl (102 kB)
#8 1.492 Downloading requests-2.32.3-py3-none-any.whl (64 kB)
#8 1.506 Downloading blinker-1.9.0-py3-none-any.whl (8.5 kB)
#8 1.514 Downloading certifi-2026.7.22-py3-none-any.whl (136 kB)
#8 1.528 Downloading charset_normalizer-3.4.9-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (224 kB)
#8 1.556 Downloading click-8.4.2-py3-none-any.whl (119 kB)
#8 1.577 Downloading idna-3.18-py3-none-any.whl (65 kB)
#8 1.594 Downloading itsdangerous-2.2.0-py3-none-any.whl (16 kB)
#8 1.604 Downloading jinja2-3.1.6-py3-none-any.whl (134 kB)
#8 1.619 Downloading urllib3-2.7.0-py3-none-any.whl (131 kB)
#8 1.645 Downloading werkzeug-3.1.8-py3-none-any.whl (226 kB)
#8 1.667 Downloading markupsafe-3.0.3-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (22 kB)
#8 1.683 Installing collected packages: urllib3, MarkupSafe, itsdangerous, idna, click, charset-normalizer, certifi, blinker, Werkzeug, requests, Jinja2, flask
#8 2.138 Successfully installed Jinja2-3.1.6 MarkupSafe-3.0.3 Werkzeug-3.1.8 blinker-1.9.0 certifi-2026.7.22 charset-normalizer-3.4.9 click-8.4.2 flask-3.1.0 idna-3.18 itsdangerous-2.2.0 requests-2.32.3 urllib3-2.7.0
#8 2.138 WARNING: Running pip as the 'root' user can result in broken permissions and conflicting behaviour with the system package manager, possibly rendering your system unusable. It is recommended to use a virtual environment instead: https://pip.pypa.io/warnings/venv. Use the --root-user-action option if you know what you are doing and want to suppress this warning.
#8 2.195 
#8 2.195 [notice] A new release of pip is available: 25.0.1 -> 26.2.1
#8 2.195 [notice] To update, run: pip install --upgrade pip
#8 DONE 2.3s

#9 [5/6] COPY app.py .
#9 DONE 0.1s

#10 [6/6] COPY static/ ./static/
#10 DONE 0.1s

#11 exporting to image
#11 exporting layers
#11 exporting layers 0.6s done
#11 exporting manifest sha256:5c4db59592edf7b78485d39dbf5acef77c00db839c5f0996b76106314d3e681a 0.0s done
#11 exporting config sha256:4750970f7efd1804fdff74fd2e1de1bc2f966b14da53d167128645fdfaed3428 0.0s done
#11 exporting attestation manifest sha256:0c8d796802b3c55d772ae9c6a06f16e95db7af280ab6f88f6e5a04ee721cfb95 0.1s done
#11 exporting manifest list sha256:410ad58d243f4ff8d135c8ed7ebf14e7eaed42f10e0138b649fb4ee7f4cb61ba
#11 exporting manifest list sha256:410ad58d243f4ff8d135c8ed7ebf14e7eaed42f10e0138b649fb4ee7f4cb61ba 0.0s done
#11 naming to docker.io/library/vision-frontend:1.0 done
#11 unpacking to docker.io/library/vision-frontend:1.0
#11 unpacking to docker.io/library/vision-frontend:1.0 0.3s done
#11 DONE 1.0s
```

_exit code: 0_

### $ docker images vision-*

```bash
docker images vision-*
```

```
IMAGE                 ID             DISK USAGE   CONTENT SIZE   EXTRA
vision-backend:1.0    330bb0905094        526MB          129MB        
vision-frontend:1.0   410ad58d243f        202MB         49.2MB        
```

_exit code: 0_

### $ docker run -d --network visionnet --name backend -p 8000:8000 vision-backend:1.0

```bash
docker run -d --network visionnet --name backend -p 8000:8000 vision-backend:1.0
```

```
6ac6c9aa28a70a057ad03686d18fbcf98ebdf795cf62f4554e03de54010dee4e
```

_exit code: 0_

### $ docker run -d --network visionnet --name frontend -e BACKEND_URL=http://backend:8000 -p 8501:8501 vision-frontend:1.0

```bash
docker run -d --network visionnet --name frontend -e BACKEND_URL=http://backend:8000 -p 8501:8501 vision-frontend:1.0
```

```
543db63a8e4608fe1f992c8f57b1f624a849fdf7be702722eba75ff01fc97640
```

_exit code: 0_

### $ docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"

```bash
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"
```

```
NAMES      IMAGE                 STATUS                    PORTS
frontend   vision-frontend:1.0   Up 18 seconds             0.0.0.0:8501->8501/tcp, [::]:8501->8501/tcp
backend    vision-backend:1.0    Up 19 seconds (healthy)   0.0.0.0:8000->8000/tcp, [::]:8000->8000/tcp
```

_exit code: 0_

### $ docker exec frontend python -c "import socket;print(socket.gethostbyname(\"backend\"))"

```bash
docker exec frontend python -c "import socket;print(socket.gethostbyname(\"backend\"))"
```

```
172.19.0.2
```

_exit code: 0_

### $ curl -s http://localhost:8000/healthz

```bash
curl -s http://localhost:8000/healthz
```

```
{"status":"ok","canny_low":100,"canny_high":200,"cv2":"4.10.0"}
```

_exit code: 0_

### $ curl -s http://localhost:8501/ | grep -o "BACKEND_URL = <b>[^<]*"

```bash
curl -s http://localhost:8501/ | grep -o "BACKEND_URL = <b>[^<]*"
```

```
BACKEND_URL = <b>http://backend:8000
```

_exit code: 0_

### $ curl -s -F name=Somchai -F surname=Jaidee -F use_sample=1 http://localhost:8501/ | grep -oE "(Original|Edges — cv2.Canny|data:image/jpeg;base64)" | sort | uniq -c

```bash
curl -s -F name=Somchai -F surname=Jaidee -F use_sample=1 http://localhost:8501/ | grep -oE "(Original|Edges — cv2.Canny|data:image/jpeg;base64)" | sort | uniq -c
```

```
      1 Edges — cv2.Canny
      1 Original
      2 data:image/jpeg;base64
```

_exit code: 0_

### $ docker run -d --name frontend-bad vision-frontend:1.0

```bash
docker run -d --name frontend-bad vision-frontend:1.0
```

```
444d32f81ef5f2a1ab14120411c73d645d309c4cd1bd6d9b519404b1d1c6f6f9
```

_exit code: 0_

### $ docker exec frontend-bad python -c "import socket;print(socket.gethostbyname(\"backend\"))"

```bash
docker exec frontend-bad python -c "import socket;print(socket.gethostbyname(\"backend\"))"
```

```
Traceback (most recent call last):
  File "<string>", line 1, in <module>
socket.gaierror: [Errno -2] Name or service not known
```

_exit code: 1_

### $ docker rm -f frontend-bad

```bash
docker rm -f frontend-bad
```

```
frontend-bad
```

_exit code: 0_

### $ docker rm -f backend frontend && docker network rm visionnet

```bash
docker rm -f backend frontend && docker network rm visionnet
```

```
backend
frontend
visionnet
```

_exit code: 0_

### $ cp env.example .env && cat .env

```bash
cp env.example .env && cat .env
```

```
APP_TITLE=Vision API — ตรวจจับขอบภาพ
CANNY_LOW=100
CANNY_HIGH=200
```

_exit code: 0_

### $ docker compose up -d --build

```bash
docker compose up -d --build
```

```
 Image vision-backend:1.0 Building 
 Image vision-frontend:1.0 Building 
#1 [internal] load local bake definitions
#1 reading from stdin 923B done
#1 DONE 0.0s

#2 [backend internal] load build definition from Dockerfile
#2 transferring dockerfile: 544B done
#2 DONE 0.0s

#3 [frontend internal] load build definition from Dockerfile
#3 transferring dockerfile: 314B done
#3 DONE 0.0s

#4 [backend internal] load metadata for docker.io/library/python:3.12-slim
#4 DONE 0.8s

#5 [backend internal] load .dockerignore
#5 transferring context: 78B done
#5 DONE 0.0s

#6 [frontend internal] load .dockerignore
#6 transferring context: 88B done
#6 DONE 0.0s

#7 [backend internal] load build context
#7 transferring context: 64B done
#7 DONE 0.0s

#8 [frontend internal] load build context
#8 transferring context: 127B done
#8 DONE 0.0s

#9 [frontend 1/5] FROM docker.io/library/python:3.12-slim@sha256:229a2c5bfa27522db7815ea81f9bed70af17ccb9de9fc7ad142b1877b5830d36
#9 resolve docker.io/library/python:3.12-slim@sha256:229a2c5bfa27522db7815ea81f9bed70af17ccb9de9fc7ad142b1877b5830d36 0.0s done
#9 DONE 0.0s

#10 [frontend 4/6] RUN pip install --no-cache-dir -r requirements.txt
#10 CACHED

#11 [frontend 5/6] COPY app.py .
#11 CACHED

#12 [frontend 3/6] COPY requirements.txt .
#12 CACHED

#13 [frontend 6/6] COPY static/ ./static/
#13 CACHED

#14 [backend 2/5] WORKDIR /app
#14 CACHED

#15 [backend 3/5] COPY requirements.txt .
#15 CACHED

#16 [backend 4/5] RUN pip install --no-cache-dir -r requirements.txt
#16 CACHED

#17 [backend 5/5] COPY main.py .
#17 CACHED

#18 [backend] exporting to image
#18 exporting layers done
#18 exporting manifest sha256:0ccded968ba95167decdc2a0d9c2ce1de06d2718a80d6e2e49baa0570e892258 0.0s done
#18 exporting config sha256:516da37b7942985b54f34cb06d1b03d15445ee7dc782bdede4130dfce32248ef 0.0s done
#18 exporting attestation manifest sha256:0cc5c355cfb8935322a26d89a105a91ed7696805ed292785f6767dd6f11cb01d 0.1s done
#18 exporting manifest list sha256:fa62e6fd5a0ab1e3b0709a7db6f111121c4312a838d3b864f0f69bf22244f01b
#18 ...

#19 [frontend] exporting to image
#19 exporting layers done
#19 exporting manifest sha256:0879a159ae09b2a90e9a73e3571301148e2f54e58039768295fbbc8c92500560 0.0s done
#19 exporting config sha256:03d0c242b628a70ebda32ac32641e4e6cad3756b6066dc6d45b63abc0e691ff7 0.0s done
#19 exporting attestation manifest sha256:5b256332118601203a1fcc413128694075d468f9e00256bf6f812199fbb78a69 0.1s done
#19 exporting manifest list sha256:393273ee375e137dad972ac2a8a58c597c97a26220effc843c0b6a6c060c146b 0.0s done
#19 naming to docker.io/library/vision-frontend:1.0 0.0s done
#19 unpacking to docker.io/library/vision-frontend:1.0 0.0s done
#19 DONE 0.3s

#18 [backend] exporting to image
#18 exporting manifest list sha256:fa62e6fd5a0ab1e3b0709a7db6f111121c4312a838d3b864f0f69bf22244f01b 0.0s done
#18 naming to docker.io/library/vision-backend:1.0 0.0s done
#18 unpacking to docker.io/library/vision-backend:1.0 0.0s done
#18 DONE 0.3s

#20 [backend] resolving provenance for metadata file
#20 DONE 0.0s

#21 [frontend] resolving provenance for metadata file
#21 DONE 0.0s
 Image vision-backend:1.0 Built 
 Image vision-frontend:1.0 Built 
 Network vision_visionnet Creating 
 Network vision_visionnet Created 
 Container vision-backend-1 Creating 
 Container vision-backend-1 Created 
 Container vision-frontend-1 Creating 
 Container vision-frontend-1 Created 
 Container vision-backend-1 Starting 
 Container vision-backend-1 Started 
 Container vision-backend-1 Waiting 
 Container vision-backend-1 Healthy 
 Container vision-frontend-1 Starting 
 Container vision-frontend-1 Started 
```

_exit code: 0_

### $ docker compose ps

```bash
docker compose ps
```

```
NAME                IMAGE                 COMMAND                  SERVICE    CREATED          STATUS                    PORTS
vision-backend-1    vision-backend:1.0    "uvicorn main:app --…"   backend    13 seconds ago   Up 12 seconds (healthy)   0.0.0.0:8000->8000/tcp, [::]:8000->8000/tcp
vision-frontend-1   vision-frontend:1.0   "python app.py"          frontend   13 seconds ago   Up 7 seconds              0.0.0.0:8501->8501/tcp, [::]:8501->8501/tcp
```

_exit code: 0_

### $ docker compose logs backend --tail 10

```bash
docker compose logs backend --tail 10
```

```
backend-1  | INFO:     Started server process [1]
backend-1  | INFO:     Waiting for application startup.
backend-1  | INFO:     Application startup complete.
backend-1  | INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
backend-1  | INFO:     127.0.0.1:59174 - "GET /healthz HTTP/1.1" 200 OK
backend-1  | INFO:     127.0.0.1:59182 - "GET /healthz HTTP/1.1" 200 OK
```

_exit code: 0_

### $ docker compose exec backend python -c "import cv2;print(cv2.__version__)"

```bash
docker compose exec backend python -c "import cv2;print(cv2.__version__)"
```

```
4.10.0
```

_exit code: 0_

### $ docker compose exec frontend python -c "import socket;print(socket.gethostbyname(\"backend\"))"

```bash
docker compose exec frontend python -c "import socket;print(socket.gethostbyname(\"backend\"))"
```

```
172.19.0.2
```

_exit code: 0_

### $ docker network ls --filter name=vision

```bash
docker network ls --filter name=vision
```

```
NETWORK ID     NAME               DRIVER    SCOPE
71b76dbe7854   vision_visionnet   bridge    local
```

_exit code: 0_

### $ sed -i "s/^CANNY_LOW=.*/CANNY_LOW=10/; s/^CANNY_HIGH=.*/CANNY_HIGH=40/" .env && cat .env

```bash
sed -i "s/^CANNY_LOW=.*/CANNY_LOW=10/; s/^CANNY_HIGH=.*/CANNY_HIGH=40/" .env && cat .env
```

```
APP_TITLE=Vision API — ตรวจจับขอบภาพ
CANNY_LOW=10
CANNY_HIGH=40
```

_exit code: 0_

### $ docker compose up -d

```bash
docker compose up -d
```

```
 Container vision-frontend-1 Running 
 Container vision-backend-1 Recreate 
 Container vision-backend-1 Recreated 
 Container vision-backend-1 Starting 
 Container vision-backend-1 Started 
 Container vision-backend-1 Waiting 
 Container vision-backend-1 Healthy 
```

_exit code: 0_

### $ curl -s http://localhost:8000/healthz

```bash
curl -s http://localhost:8000/healthz
```

```
{"status":"ok","canny_low":10,"canny_high":40,"cv2":"4.10.0"}
```

_exit code: 0_

### $ sed -i "s/^CANNY_LOW=.*/CANNY_LOW=100/; s/^CANNY_HIGH=.*/CANNY_HIGH=200/" .env && docker compose up -d && curl -s http://localhost:8000/healthz

```bash
sed -i "s/^CANNY_LOW=.*/CANNY_LOW=100/; s/^CANNY_HIGH=.*/CANNY_HIGH=200/" .env && docker compose up -d && curl -s http://localhost:8000/healthz
```

```
 Container vision-frontend-1 Running 
 Container vision-backend-1 Recreate 
 Container vision-backend-1 Recreated 
 Container vision-backend-1 Starting 
 Container vision-backend-1 Started 
 Container vision-backend-1 Waiting 
 Container vision-backend-1 Healthy 
{"status":"ok","canny_low":100,"canny_high":200,"cv2":"4.10.0"}
```

_exit code: 0_

### $ docker compose down

```bash
docker compose down
```

```
 Container vision-frontend-1 Stopping 
 Container vision-frontend-1 Stopped 
 Container vision-frontend-1 Removing 
 Container vision-frontend-1 Removed 
 Container vision-backend-1 Stopping 
 Container vision-backend-1 Stopped 
 Container vision-backend-1 Removing 
 Container vision-backend-1 Removed 
 Network vision_visionnet Removing 
 Network vision_visionnet Removed 
```

_exit code: 0_

### $ docker ps -a; docker network ls --filter name=vision

```bash
docker ps -a; docker network ls --filter name=vision
```

```
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
NETWORK ID   NAME      DRIVER    SCOPE
```

_exit code: 0_

### $ docker rmi vision-backend:1.0 vision-frontend:1.0

```bash
docker rmi vision-backend:1.0 vision-frontend:1.0
```

```
Untagged: vision-backend:1.0
Deleted: sha256:fa62e6fd5a0ab1e3b0709a7db6f111121c4312a838d3b864f0f69bf22244f01b
Untagged: vision-frontend:1.0
Deleted: sha256:393273ee375e137dad972ac2a8a58c597c97a26220effc843c0b6a6c060c146b
```

_exit code: 0_

### $ docker images

```bash
docker images
```

```
IMAGE   ID             DISK USAGE   CONTENT SIZE   EXTRA
```

_exit code: 0_

### $ docker compose down; echo "--- rc=$?"

```bash
docker compose down; echo "--- rc=$?"
```

```
--- rc=0
```

_exit code: 0_

### $ docker compose up -d --build 2>&1 | tail -20 && sleep 6 && docker compose ps && curl -s http://localhost:8501/ | grep -o "backend = <b>[^<]*" && curl -s -F use_sample=1 http://localhost:8501/ | grep -c "data:image/jpeg;base64"

```bash
docker compose up -d --build 2>&1 | tail -20 && sleep 6 && docker compose ps && curl -s http://localhost:8501/ | grep -o "backend = <b>[^<]*" && curl -s -F use_sample=1 http://localhost:8501/ | grep -c "data:image/jpeg;base64"
```

```
#18 [backend] exporting to image
#18 unpacking to docker.io/library/vision-backend:1.0 1.4s done
#18 DONE 1.7s

#21 [backend] resolving provenance for metadata file
#21 DONE 0.0s
 Image vision-backend:1.0 Built 
 Image vision-frontend:1.0 Built 
 Network vision_visionnet Creating 
 Network vision_visionnet Created 
 Container vision-backend-1 Creating 
 Container vision-backend-1 Created 
 Container vision-frontend-1 Creating 
 Container vision-frontend-1 Created 
 Container vision-backend-1 Starting 
 Container vision-backend-1 Started 
 Container vision-backend-1 Waiting 
 Container vision-backend-1 Healthy 
 Container vision-frontend-1 Starting 
 Container vision-frontend-1 Started 
NAME                IMAGE                 COMMAND                  SERVICE    CREATED          STATUS                    PORTS
vision-backend-1    vision-backend:1.0    "uvicorn main:app --…"   backend    13 seconds ago   Up 12 seconds (healthy)   0.0.0.0:8000->8000/tcp, [::]:8000->8000/tcp
vision-frontend-1   vision-frontend:1.0   "python app.py"          frontend   13 seconds ago   Up 6 seconds              0.0.0.0:8501->8501/tcp, [::]:8501->8501/tcp
backend = <b>ok
2
```

_exit code: 0_

### $ docker compose down && docker rmi vision-backend:1.0 vision-frontend:1.0 && docker ps -a && docker images && docker network ls --filter name=vision

```bash
docker compose down && docker rmi vision-backend:1.0 vision-frontend:1.0 && docker ps -a && docker images && docker network ls --filter name=vision
```

```
 Container vision-frontend-1 Stopping 
 Container vision-frontend-1 Stopped 
 Container vision-frontend-1 Removing 
 Container vision-frontend-1 Removed 
 Container vision-backend-1 Stopping 
 Container vision-backend-1 Stopped 
 Container vision-backend-1 Removing 
 Container vision-backend-1 Removed 
 Network vision_visionnet Removing 
 Network vision_visionnet Removed 
Untagged: vision-backend:1.0
Deleted: sha256:94a41c440470a25f64422e35484dbaa2005b30345ea950f37d4cba19bf9e0e00
Untagged: vision-frontend:1.0
Deleted: sha256:cf72b5c743b30cf23be96b73403edf3708d0c9c289f7e1f7105d5e5757986704
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
IMAGE   ID             DISK USAGE   CONTENT SIZE   EXTRA
NETWORK ID   NAME      DRIVER    SCOPE
```

_exit code: 0_

---

## screenshots

ถ่ายด้วย Playwright (chromium, viewport 1280×800, device_scale_factor=2) จากพอร์ตที่ publish ออกมาจริง
ของ container `devtools-lab004` ขณะที่ `docker compose up -d` ทำงานอยู่:

| ไฟล์ | URL ที่ถ่าย | เนื้อหา |
|---|---|---|
| `images/vision-ui.png` | `http://<host>:18041/` (= frontend 8501) | อัปโหลด `frontend/static/sample.jpg` จริงผ่านฟอร์ม แล้วได้ Original + Edges คู่กัน (CANNY 100/200) |
| `images/vision-docs.png` | `http://<host>:18042/docs` (= backend 8000) | Swagger UI ของ FastAPI : `GET /healthz`, `POST /process-image`, schema `ImageRequest` |
| `images/vision-ui-canny-low.png` | `http://<host>:18041/` | รูปเดิม หลังแก้ `.env` เป็น `CANNY_LOW=10` / `CANNY_HIGH=40` แล้ว `docker compose up -d` |

`frontend/static/sample.jpg` (44,099 bytes, 800×600) สร้างจาก `frontend/static/make_sample.py`
ด้วย numpy + OpenCV — ผลลัพธ์เหมือนเดิมทุกครั้งที่รัน (ไม่มีการสุ่ม)
