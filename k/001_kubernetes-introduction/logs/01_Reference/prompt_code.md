งาน: สร้าง container สำหรับเรียน Kubernetes ด้วย kind ในโฟลเดอร์
/root/workspace/DevTools/k/001_kubernetes-introduction/02_LAB/00_Reference/01_Reference/

อ่านไฟล์ต้นแบบใน /root/workspace/DevTools/k/001_kubernetes-introduction/02_LAB/00_Reference/
(Dockerfile, start.sh, docker-compose.yml, jupyter_overrides.json, .dockerignore, .gitignore, readme.md, Devtool_SSH/)
ห้ามแก้ไขไฟล์ใด ๆ ใน 00_Reference (ยกเว้นสร้างของใหม่ใน 01_Reference/) ห้ามแตะโฟลเดอร์ 01_Reference/images/

## สิ่งที่ต้องสร้างใน 01_Reference/ (โฟลเดอร์ต้อง self-contained: copy โฟลเดอร์นี้ไปเครื่องอื่นแล้ว build ได้เลย)

1. `Dockerfile` — เนื้อหาเหมือน Dockerfile ต้นแบบทุก layer (Ubuntu 24.04, git PPA, Docker-in-Docker, Node 22, JupyterLab + extensions, jupyter config, SSH root/passwd + key) แล้วเพิ่ม layer Kubernetes:
   - `kind`, `kubectl`, `helm`, `k9s` — pin เวอร์ชันเป็น `ARG` (หาเวอร์ชัน stable ล่าสุดจริงตอนนี้ด้วย curl: GitHub API releases/latest ของ kubernetes-sigs/kind, helm/helm, derailed/k9s และ https://dl.k8s.io/release/stable.txt) รองรับ amd64/arm64 ผ่าน `dpkg --print-architecture` ดาวน์โหลดจาก official release URL และตรวจ checksum เมื่อ release มีให้ (อย่างน้อย kubectl .sha256 และ kind .sha256sum)
   - ติดตั้ง `bash-completion` และตั้ง completion ของ kubectl/kind/helm ใน /etc/bash_completion.d/ + `alias k=kubectl` พร้อม `complete -o default -F __start_kubectl k` (ใส่ใน /etc/bash.bashrc หรือ /etc/profile.d ให้ทั้ง SSH และ terminal ของ JupyterLab ได้)
   - แต่ละ layer ทดสอบ `--version` ตอน build
   - COPY `kind-lab.yaml` → `/etc/devtools/kind/kind-lab.yaml`, COPY `k8s-up` และ `k8s-down` → `/usr/local/bin/` (chmod +x)
   - EXPOSE 22 8888 30080 30081 30082
   - comment ภาษาไทยสไตล์เดียวกับต้นแบบ
2. `start.sh` — เหมือนต้นแบบ แต่เพิ่ม: หลังเริ่ม dockerd ถ้า `KIND_AUTO_CREATE=1` ให้รัน `k8s-up` แบบ background log ไป `/var/log/k8s-up.log` (default 0 = ไม่สร้างอัตโนมัติ) และปรับข้อความ echo ให้บอกพอร์ต NodePort ด้วย
3. `kind-lab.yaml` — kind config (apiVersion kind.x-k8s.io/v1alpha4) ชื่อคลัสเตอร์ `lab`: 1 control-plane + 2 worker; control-plane มี `extraPortMappings` containerPort 30080/30081/30082 → hostPort เดียวกัน `listenAddress: "0.0.0.0"` protocol TCP ไม่ pin node image (ใช้ default ของ kind เวอร์ชันนั้น)
4. `k8s-up` (bash) — รอ `docker info` พร้อม (deadline 90 วินาที ถ้าเกินให้ error พร้อมบอกให้ดู /var/log/dockerd.log), ถ้ามีคลัสเตอร์ `lab` อยู่แล้วให้แจ้งและข้าม, ไม่งั้น `kind create cluster --config /etc/devtools/kind/kind-lab.yaml` (รับ `KIND_CONFIG`, `KIND_CLUSTER_NAME`, `KIND_NODE_IMAGE` เป็น env override ได้) แล้ว `kubectl wait --for=condition=Ready nodes --all --timeout=180s` และพิมพ์ `kubectl get nodes -o wide` + คำแนะนำสั้น ๆ
5. `k8s-down` (bash) — `kind delete cluster --name ${KIND_CLUSTER_NAME:-lab}`
6. `docker-compose.yml` — ตามต้นแบบ แต่: image `devtools-kind:2569_1` + `build: .`, `container_name: k8s-lab`, `hostname: k8s-lab`, ports `${SSH_PORT:-2223}:22`, `${JUPYTER_PORT:-8889}:8888`, `30080-30082:30080-30082`, volumes `./workspace:/workspace`, `k8s-lab-dind:/var/lib/docker`, `./Devtool_SSH:/etc/devtools/ssh`, environment `KIND_AUTO_CREATE: ${KIND_AUTO_CREATE:-0}` และ JUPYTER_PASSWORD เหมือนเดิม; คง env_file แบบ required: false เหมือนต้นแบบ; comment ด้านบนอธิบายการใช้งานเป็นภาษาไทย (พอร์ตต่างจาก devtools 2222/8888 เพื่อรันคู่กันได้)
7. copy `jupyter_overrides.json` และโฟลเดอร์ `Devtool_SSH/` (ทั้ง 2 ไฟล์) จากต้นแบบมาไว้ใน 01_Reference
8. `.dockerignore` (เพิ่ม images, readme.md, workspace, Devtool_SSH, docker-compose.yml, .ipynb_checkpoints) และ `.gitignore` (workspace/)
9. `examples/` — manifest ตัวอย่างสำหรับ lab: `web-deployment.yaml` (Deployment `web` nginx replicas 3 + Service `web` type NodePort nodePort 30080 port 80), `hello-pod.yaml` (Pod เดี่ยว), และ `myapp/` (Dockerfile เล็ก ๆ ของ nginx:alpine ที่ copy index.html "Hello from myapp:1.0" + `myapp.yaml` Deployment+Service NodePort 30081 ใช้ image `myapp:1.0` imagePullPolicy IfNotPresent) — ใช้กับหัวข้อ kind load docker-image

ห้ามเขียน readme.md (จะทำทีหลัง) ห้าม docker build/run เอง (ผู้สั่งจะทดสอบเอง) ตรวจ syntax ด้วย `bash -n` กับ shell script และ `python3 -c 'import yaml'` (ถ้ามี) หรือวิธีอื่นสำหรับ YAML ได้
ห้ามใส่ข้อมูลลับ/อีเมลจริงลงไฟล์

ตอบกลับสั้น ๆ: รายการไฟล์ที่สร้าง + เวอร์ชันที่ pin ของ kind/kubectl/helm/k9s
