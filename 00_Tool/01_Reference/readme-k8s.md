# DevTools Kubernetes Learning Container

**Ubuntu 26.04 LTS + Docker-in-Docker + Python + Node.js + git/gh + SSH + ชุดเครื่องมือ Kubernetes ครบ Tier 1 + Tier 2**
สร้าง cluster จริงได้ในตัว (kind / k3d) โดยไม่ต้องพึ่ง cloud

`Dockerfile.k8s` เป็น **ไฟล์เดียวจบ** เริ่มจาก `FROM ubuntu` — ไม่ต้อง build base image ก่อน

| ไฟล์ | หน้าที่ |
|------|---------|
| `Dockerfile.k8s` | image เต็ม (ระบบพื้นฐาน + Kubernetes toolchain) — **ใช้ไฟล์นี้** |
| `docker-compose.yml` | สภาพแวดล้อมพร้อมใช้ (volume, port, ulimit, healthcheck) |
| `Dockerfile` | base image เดิม สำหรับคนที่เรียนแค่ Docker/Git ไม่เอา k8s ([readme.md](readme.md)) |

---

## 1. เริ่มใช้งาน

### แบบเร็วสุด — ดึง image สำเร็จรูป (ไม่ต้อง build)

image publish ไว้ที่ [`tuchsanai/devtools-k8s`](https://hub.docker.com/r/tuchsanai/devtools-k8s)

```bash
docker pull tuchsanai/devtools-k8s:2569_1

docker run -d --name devtools-k8s --privileged --shm-size=1g --ulimit nofile=65536:65536 -p 2299:22 -p 8080:80 -p 8443:443 tuchsanai/devtools-k8s:2569_1

docker exec -it devtools-k8s bash
```

### หรือ build เอง

```bash
docker compose build
docker compose up -d

# เข้าไปใช้งาน
docker compose exec devtools-k8s bash
```

หรือ build โดยไม่ใช้ compose:

```bash
docker build -f Dockerfile.k8s -t devtools-k8s:2569_1 .
```

### push ขึ้น Docker Hub

```bash
docker tag devtools-k8s:2569_1 tuchsanai/devtools-k8s:2569_1
docker push tuchsanai/devtools-k8s:2569_1
```

build ข้าม architecture (amd64 + arm64) ในครั้งเดียว:

```bash
docker buildx build -f Dockerfile.k8s --platform linux/amd64,linux/arm64 -t tuchsanai/devtools-k8s:2569_1 --push .
```

สร้างคลัสเตอร์พร้อม add-on ที่จำเป็นด้วยคำสั่งเดียว:

```bash
docker compose exec devtools-k8s k8s-bootstrap
```

ได้ kind cluster **1 control-plane + 2 worker** พร้อม **metrics-server** และ **ingress-nginx**

```bash
docker compose exec devtools-k8s k9s          # TUI ดูทั้งคลัสเตอร์
docker compose exec devtools-k8s kubectl top nodes
```

---

## 2. เครื่องมือใน image

### Tier 1

| tool | version | ใช้ทำอะไร |
|---|---|---|
| kubectl | 1.37.0 | CLI หลัก (มี bash completion + alias `k`) |
| kind | 0.33.0 | สร้าง cluster หลาย node ใน Docker |
| k3d | 5.9.0 | cluster แบบเบา (k3s) |
| helm | 4.2.4 | package manager |
| k9s | 0.51.0 | TUI |
| stern | 1.34.0 | tail log หลาย pod พร้อมกัน |
| kubectx / kubens | 0.11.0 | สลับ context / namespace |
| kustomize | 5.8.1 | overlay dev/staging/prod |
| yq | 4.53.6 | จัดการ YAML |
| krew | 0.5.0 | plugin manager (ลง `neat`, `tree` มาให้แล้ว) |

### Tier 2

| tool | version | ใช้ทำอะไร |
|---|---|---|
| argocd | 3.5.2 | GitOps |
| flux | 2.9.5 | GitOps (ทางเลือก) |
| trivy | 0.74.0 | scan ช่องโหว่ image / manifest |
| kube-linter | 0.8.3 | ตรวจ manifest ตาม best practice |
| kubeconform | 0.8.0 | validate schema (ใช้ใน CI) |
| skaffold | 2.24.0 | inner-loop dev |

> ⚠️ **Helm 4** ไม่ใช่ Helm 3 — ตำราและ tutorial ส่วนใหญ่ยังเป็น 3 ถ้าอยากให้ตรงตำรา
> build ด้วย `--build-arg HELM_VERSION=v3.19.0`

---

## 3. `k8s-bootstrap`

```
k8s-bootstrap [options]
  --no-metrics     ไม่ลง metrics-server (default: ลง)
  --no-ingress     ไม่ลง ingress-nginx  (default: ลง)
  --cert-manager   ลง cert-manager
  --monitoring     ลง kube-prometheus-stack (หนัก ~5-10 นาที)
  --all            ลงทุกอย่าง
  --single-node    คลัสเตอร์ node เดียว (เครื่องแรมน้อย)

env: CLUSTER=<ชื่อ>   KIND_NODE_VERSION=<vX.Y.Z>
```

ลบคลัสเตอร์: `k8s-teardown`

### ทดสอบ Ingress

`docker-compose.yml` map พอร์ตไว้ให้แล้ว — จาก **เครื่อง host**:

```bash
curl -H 'Host: myapp.local' http://localhost:8080/
```

เส้นทาง: `host:8080` → `devtools-k8s:80` → `kind control-plane:80` → ingress-nginx → pod

---

## 4. ปรับเวอร์ชัน

ทุกเวอร์ชันเป็น `ARG` ปรับได้โดยไม่ต้องแก้ไฟล์

```bash
docker compose build --build-arg KUBECTL_VERSION=v1.36.4 --build-arg HELM_VERSION=v3.19.0
```

เปลี่ยนเวอร์ชัน Kubernetes ของคลัสเตอร์ (แก้ใน `docker-compose.yml` หรือ env):

```bash
KIND_NODE_VERSION=v1.35.8 k8s-bootstrap
```

> 💡 **pin เวอร์ชันทั้งเทอม** เพื่อให้ นศ. ทุกคนเห็น output เหมือนกัน
> ค่า default คือ kubectl 1.37 + cluster 1.36 ซึ่งเป็น version skew ที่ถูกต้อง (kubectl ใหม่กว่าได้ 1 minor)
> — ตัวนี้เป็นเนื้อหาสอบ CKA อยู่แล้ว ใช้เป็นตัวอย่างได้เลย

---

## 5. ทำไมต้อง `privileged` + เรื่อง cgroup

node ของ kind รัน **systemd เป็น PID 1** ซึ่งต้องใช้ cgroup controller `memory` และ `io`
แต่ cgroup root ของ container ตั้งต้นมาโดย `cgroup.subtree_control` **ว่างเปล่า**
ถ้าไม่ delegate ให้ kind จะล้มด้วยข้อความ:

```
ERROR: failed to create cluster: could not find a log line that matches
"Reached target .*Multi-User System.*|detected cgroup v1"
```

`k8s-entrypoint.sh` จัดการให้อัตโนมัติก่อน `dockerd` จะ start โดย:

1. `mkdir /sys/fs/cgroup/init` แล้วย้าย process ทั้งหมดเข้าไป
   (กฎ *no internal processes* ของ cgroup v2 — ห้ามเปิด controller ขณะยังมี process ค้างใน cgroup นั้น)
2. เขียน `+cpuset +cpu +io +memory +hugetlb +pids +rdma` ลง `cgroup.subtree_control`

เป็นขั้นตอนเดียวกับที่ image `docker:dind` ทางการทำ ตรวจว่าทำงานถูกได้จาก log:

```bash
docker compose logs devtools-k8s | grep cgroup
# [k8s-entrypoint] cgroup v2 delegation: ย้าย 4 procs -> /init, เปิด [cpuset cpu io memory hugetlb pids rdma]
```

ถ้าเห็น `WARN: delegate ไม่สำเร็จ` แปลว่าไม่ได้รันแบบ `privileged: true`

---

## 6. แก้ปัญหาที่เจอบ่อย

| อาการ | สาเหตุ / วิธีแก้ |
|-------|------------------|
| `could not find a log line that matches "Reached target..."` | cgroup delegation ไม่สำเร็จ — เช็ก `docker compose logs \| grep cgroup` และต้องมี `privileged: true` |
| kind node ขึ้นแต่ไม่ Ready | inotify limit ต่ำ — entrypoint ปรับให้แล้ว ถ้ายังไม่พอ ตั้งบน **host**: `sysctl -w fs.inotify.max_user_watches=524288` |
| pull `kindest/node` ใหม่ทุกครั้งที่ recreate | อย่าใช้ `docker compose down -v` — volume `docker-data` เก็บ image ของ dockerd ข้างในไว้ |
| ห้องเรียนหลายคน pull พร้อมกันจนเน็ตตาย | `docker compose --profile classroom up -d` แล้ว uncomment `REGISTRY_MIRROR` ใน compose |
| `curl localhost:8080` ไม่ตอบ | ต้องลง ingress-nginx ก่อน (`k8s-bootstrap`) และต้องส่ง `Host:` header ให้ตรงกับ Ingress rule |
| แรมไม่พอ | ใช้ `k8s-bootstrap --single-node` หรือใช้ k3d แทน: `k3d cluster create lab --agents 1` |

---

## 7. ขนาด image

| image | บนดิสก์ | โหลดจริง (gzip) |
|---|---:|---:|
| `devtools-k8s:2569_1` | ~2.6 GB | ~800 MB |
| `devtools:2569_2` (base เดิม ไม่มี k8s) | 1.43 GB | 467 MB |

ขนาดของเครื่องมือแต่ละตัว (วัดจริง):

| Tier 1 | | Tier 2 | |
|---|---:|---|---:|
| k9s | 126 MB | argocd | **238 MB** |
| helm | 61 | trivy | **161** |
| kubectl | 59 | skaffold | 124 |
| stern | 46 | flux | 74 |
| k3d | 24 | kube-linter | 47 |
| krew / yq / kustomize / kind | 50 | kubeconform | 13 |
| **รวม** | **365 MB** | **รวม** | **657 MB** |

ถ้าอยากได้ image เล็กลง ~650 MB ให้ลบ RUN block **2.3 (Tier 2)** ใน `Dockerfile.k8s` ออก
แล้วใช้ wrapper script เรียกผ่าน container แทน เช่น:

```bash
#!/usr/bin/env bash
exec docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  -v "$PWD:/work" -w /work aquasec/trivy:0.74.0 "$@"
```
