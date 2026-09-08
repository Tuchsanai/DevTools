# Kubernetes Concept First — จาก Container สู่ระบบที่ดูแลตัวเอง

ถ้า Docker Compose เปิดระบบให้เราได้บนเครื่องเดียว แล้วใครจะคอยเฝ้า ซ่อม และเปลี่ยนระบบเมื่อมีหลาย node?
ชุดเรียน 3 ครั้งนี้พาผู้เรียนเริ่มจาก Pod และ desired state ต่อไปยัง network, config และ storage
ก่อนประกอบ SkillSpace แบบ 3 ชั้น อัปเดตโดยไม่สะดุด และอ่านอาการเสียอย่างมีเหตุผล

เป้าหมายไม่ใช่การจำคำสั่งหรือ YAML แต่คือการอธิบายให้ได้ว่า object แต่ละชนิดแก้ปัญหาอะไร
ทุกคำสั่งจึงเป็น “การทดลองเพื่อพิสูจน์ concept” ไม่ใช่ปลายทางของการเรียน

## วงจรการเรียนรู้ประจำทุกแล็บ

```text
คาดการณ์ผลลัพธ์ → เรียกใช้ → สังเกตหลักฐาน → อธิบายเหตุผล → จำลองความล้มเหลว → คืนสภาพ
```

ก่อนพิมพ์คำสั่ง ให้ทายว่าสภาพจริงจะเปลี่ยนอย่างไร แล้วตรวจหลักฐานสามมุม:

- ผลจาก `kubectl`
- หน้าเว็บ SkillSpace หรือหน้าจอสังเกตระบบ
- `kubectl logs` หรือ `kubectl get events`

เมื่อทำให้ระบบพัง อย่ารีบแก้จากความจำ ให้อ่านอาการ ระบุ layer ที่เสีย แล้วจึงแก้กลับ
ทุกแล็บเริ่มสะอาด จบด้วย Cleanup และควรสร้างซ้ำได้ผลเดิม

## ความรู้ที่ควรมีมาก่อน

- Linux command line: เปลี่ยน directory, อ่านไฟล์ และเข้าใจ process/port เบื้องต้น
- Docker: image, container, Docker Compose, network และ port mapping
- Git: `clone` และการอ่านโครง repository
- แนวคิด reverse proxy และ load balancer จากบทเรียนก่อนหน้า

ไม่ต้องเคยใช้ Kubernetes มาก่อน และไม่ต้องจำ syntax ของ manifest ล่วงหน้า

## ผลลัพธ์การเรียนรู้ทั้งชุด

- **LO1** อธิบายได้ว่า Kubernetes แก้ปัญหาใดที่ Docker Compose บนเครื่องเดียวแก้ไม่ได้ และ control plane ต่างจาก worker node อย่างไร
- **LO2** อธิบายได้ว่า Pod คืออะไร และเหตุใดหน่วยเล็กที่สุดที่ Kubernetes ดูแลจึงไม่ใช่ container
- **LO3** อธิบาย desired state กับ self-healing และเหตุผลที่ Deployment สร้าง Pod ใหม่แทนตัวที่ถูกลบได้
- **LO4** อธิบายเหตุผลที่ต้องมี Service แทนการเรียก Pod IP ตรง ๆ และแยก ClusterIP จาก NodePort ได้
- **LO5** อธิบายเหตุผลที่ config/รหัสผ่านต้องอยู่นอก image และเหตุผลที่ Volume/PVC จำเป็นต่อข้อมูลที่ต้องอยู่รอด
- **LO6** อธิบายการประกอบแอปหลายชั้นและวิธีที่ rolling update ลดการสะดุดของผู้ใช้ได้
- **LO7** ไล่ตรวจ `get → describe → logs → events` และตีความ Pending, ImagePullBackOff กับ CrashLoopBackOff ได้

## เส้นทางเรียน 3 ครั้ง

| ครั้ง | โฟลเดอร์ | ธีม | จำนวนแล็บ | ไฟล์สไลด์ |
|---:|---|---|---:|---|
| 1 | [`01_Session1_Kubernetes_Basics/`](./01_Session1_Kubernetes_Basics/) | Kubernetes คืออะไร และดูแล desired state อย่างไร | 7 | [`Kubernetes_Session1_Slides.html`](./01_Session1_Kubernetes_Basics/Kubernetes_Session1_Slides.html) (81 หน้า) |
| 2 | [`02_Session2_Networking_Config_Storage/`](./02_Session2_Networking_Config_Storage/) | แอปคุยกัน ตั้งค่า และเก็บข้อมูลอย่างไร | 7 | [`Kubernetes_Session2_Slides.html`](./02_Session2_Networking_Config_Storage/Kubernetes_Session2_Slides.html) (87 หน้า) |
| 3 | [`03_Session3_Application_Deployment/`](./03_Session3_Application_Deployment/) | ประกอบระบบจริง เปลี่ยนระบบ และวินิจฉัยอาการ | 7 | [`Kubernetes_Session3_Slides.html`](./03_Session3_Application_Deployment/Kubernetes_Session3_Slides.html) (79 หน้า) |

ทุกครั้งมี **คู่มือ YAML** ของ object ที่เรียนในครั้งนั้น (อ่านคู่กับแล็บ): [`01_Session1_Kubernetes_Basics/YAML_Guide.md`](./01_Session1_Kubernetes_Basics/YAML_Guide.md) · [`02_Session2_Networking_Config_Storage/YAML_Guide.md`](./02_Session2_Networking_Config_Storage/YAML_Guide.md) · [`03_Session3_Application_Deployment/YAML_Guide.md`](./03_Session3_Application_Deployment/YAML_Guide.md) — และทุกแล็บมีหัวข้อ "อ่าน YAML ของแล็บนี้" อธิบาย manifest ทีละบรรทัด

ไฟล์ [`Fullstack_Slides.html`](../02_Docker/03_Fullstack_App_Example/Fullstack_Slides.html) เป็น README/slide ต้นแบบด้านรูปแบบ ไม่ใช่สไลด์ของสามครั้งข้างต้น

## เตรียมเครื่องครั้งเดียวสำหรับทั้งชุด

### 1. เปิดเครื่องเรียน

รันบนเครื่องหลัก คำสั่งนี้ตรงกับ environment กลางของทุกแล็บ:

```bash
docker pull tuchsanai/devtools-k8s:2569_1
docker run -d --name devtools-k8s --privileged --shm-size=1g \
  --ulimit nofile=65536:65536 \
  -p 2299:22 -p 8080:80 -p 8443:443 -p 3000:3000 -p 9090:9090 \
  tuchsanai/devtools-k8s:2569_1
docker exec -it devtools-k8s bash
```

`--privileged` จำเป็นสำหรับ Docker-in-Docker และ kind ในเครื่องเรียนแบบใช้แล้วทิ้ง
เมื่อพิมพ์คำสั่งในเทอร์มินัลของเครื่องเรียน ให้เรียก Ingress ที่ `http://localhost` (พอร์ต 80)
ส่วนเบราว์เซอร์บนเครื่องของคุณให้เปิด `http://localhost:8080`; หน้าเว็บที่ใช้ port-forward เปิดที่ `http://localhost:3000`

ถ้ามี container เดิมและต้องการเก็บงานไว้ ให้ใช้ `docker start devtools-k8s` แล้วจึง `docker exec` แทนการสร้างซ้ำ

### 2. Clone โค้ดครั้งเดียว

รันภายในเครื่องเรียน:

```bash
mkdir -p ~/labwork
cd ~/labwork
git clone https://github.com/Tuchsanai/DevTools.git
cd ~/labwork/DevTools/05_kubernetes
```

ถ้า clone ไว้แล้ว ให้เข้า repository เดิมและดึงการเปลี่ยนแปลงตามนโยบายของชั้นเรียน ไม่ต้อง clone ซ้ำ

### 3. สร้าง cluster ด้วยสคริปต์ที่มีให้

```bash
k8s-bootstrap
```

สคริปต์จะสร้าง kind cluster ชื่อ `devtools` ที่มี 1 control-plane, 2 worker,
metrics-server และ ingress-nginx โดยใช้ context `kind-devtools`
เครื่องที่ RAM จำกัดเลือก `k8s-bootstrap --single-node` ได้ แต่หลักฐานชื่อ node จะต่างจากตัวอย่าง

### 4. Build และ load image ของ SkillSpace ทั้ง 4 tag

```bash
cd ~/labwork/DevTools/05_kubernetes/app
./build-images.sh
kind load docker-image \
  k8s-lab-web:v1 k8s-lab-web:v2 k8s-lab-api:v1 k8s-lab-db:v1 \
  --name devtools
```

รายละเอียด endpoint และวิธีทดสอบแอปอยู่ใน [`app/README.md`](./app/README.md)
การ build เกิดใน Docker daemon ของเครื่องเรียน ส่วน `kind load` นำ image เข้า runtime ของ node
หากข้ามขั้นหลัง Pod อาจขึ้น `ImagePullBackOff` แม้ `docker images` จะเห็น image แล้ว

### 5. ตรวจความพร้อม

```bash
kubectl get nodes
docker exec devtools-control-plane crictl images | grep k8s-lab
kubectl -n ingress-nginx get pods
```

✅ **Expected output** — ดึงรูปแบบจาก LAB 001; ค่า `AGE`, image ID, ขนาด และชื่อ Pod อาจต่างกันได้:

```text
NAME                     STATUS   ROLES           AGE     VERSION
devtools-control-plane   Ready    control-plane   5m14s   v1.36.4
devtools-worker          Ready    <none>          5m5s    v1.36.4
devtools-worker2         Ready    <none>          5m5s    v1.36.4
docker.io/library/k8s-lab-api   v1   c01adaec89c6d   186MB
docker.io/library/k8s-lab-db    v1   a5a8c986a5421   300MB
docker.io/library/k8s-lab-web   v1   34d144d726eda   209MB
docker.io/library/k8s-lab-web   v2   0bdb9ed2beecf   209MB
```

บรรทัด ingress controller ต้องมีสถานะ `Running` และ `READY` เป็น `1/1`; ชื่อ Pod มี hash จึงต่างกันได้

## เวอร์ชันที่ pin ในเครื่องเรียน

| รายการ | เวอร์ชัน/ค่า |
|---|---|
| Learning image | `tuchsanai/devtools-k8s:2569_1` |
| Base OS | Ubuntu 26.04 |
| Kubernetes kind node | v1.36.4 |
| kubectl | v1.37.0 |
| kind | v0.33.0 |
| helm | v4.2.4 |
| k9s | v0.51.0 |
| stern | v1.34.0 |
| kustomize | v5.8.1 |
| yq | v4.53.6 |
| Node.js | 24 |
| Python environment | venv ที่ `/opt/venv` พร้อม `uv` |
| kind cluster/context | `devtools` / `kind-devtools` |

ตัวเลขเหล่านี้มีไว้ทำให้ผลทดลองในห้องเรียนทำซ้ำได้ ไม่ใช่คำแนะนำให้ตรึง production ไว้ตลอดไป
ก่อนใช้จริงต้องตรวจ release notes, compatibility และ patch version ที่อุดช่องโหว่ล่าสุดเสมอ
เครื่องมือ Tier 2 เช่น Argo CD, Flux, Trivy, kube-linter, kubeconform และ Skaffold มีใน image
แต่ไม่ได้เป็นแกนแล็บและไม่มีหมายเลขเวอร์ชันยืนยันในข้อกำหนดนี้ จึงไม่เดาตัวเลขเพิ่ม

## แผนผังโฟลเดอร์ย่อ

```text
05_kubernetes/
├── README.md
├── 01_Session1_Kubernetes_Basics/             # LAB 001–007
├── 02_Session2_Networking_Config_Storage/      # LAB 008–014
├── 03_Session3_Application_Deployment/         # LAB 015–021
├── app/                                        # SkillSpace + build-images.sh
└── PROMPT_Kubernetes_Course_Spec.txt           # ข้อกำหนดของชุด
```

เริ่มจาก README ของครั้งที่กำลังเรียน แล้วเข้า README ของแล็บตามลำดับ
จำภาพเดียวให้ได้: **เราไม่ได้สั่ง container ทีละตัว แต่ประกาศสภาพที่อยากได้ แล้วใช้หลักฐานดูว่า Kubernetes พาระบบไปถึงสภาพนั้นอย่างไร**
