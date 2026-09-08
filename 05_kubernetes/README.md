# แนวคิดพื้นฐาน Kubernetes — จาก Container สู่ระบบที่สามารถดูแลตนเองได้

Docker Compose สามารถเปิดใช้งานระบบบนเครื่องเดียวได้ แต่ระบบที่มีหลาย node จำเป็นต้องมีกลไกสำหรับเฝ้าระวัง ซ่อมแซม และปรับเปลี่ยนระบบ
ชุดวิชาจำนวน 3 ครั้งนี้เริ่มต้นจาก Pod และ desired state แล้วจึงศึกษา network, config และ storage
ก่อนประยุกต์องค์ความรู้เพื่อประกอบ SkillSpace แบบ 3 ชั้น ดำเนินการอัปเดตโดยไม่หยุดชะงัก และวิเคราะห์ความผิดปกติอย่างมีเหตุผล

เป้าหมายมิใช่การจดจำคำสั่งหรือ YAML แต่เป็นความสามารถในการอธิบายว่า object แต่ละชนิดแก้ไขปัญหาใด
คำสั่งแต่ละรายการจึงเป็น “การทดสอบเพื่อพิสูจน์แนวคิด” มิใช่จุดหมายของการเรียนรู้

## วงจรการเรียนรู้ประจำทุกปฏิบัติการ

```text
คาดการณ์ผลลัพธ์ → เรียกใช้ → สังเกตหลักฐาน → อธิบายเหตุผล → จำลองความล้มเหลว → คืนสภาพ
```

ก่อนป้อนคำสั่ง ผู้เรียนควรคาดการณ์ว่าสภาพจริงจะเปลี่ยนแปลงอย่างไร แล้วตรวจสอบหลักฐานจากสามด้าน ดังนี้

- ผลลัพธ์จาก `kubectl`
- หน้าเว็บ SkillSpace หรือหน้าจอสำหรับสังเกตระบบ
- ผลลัพธ์จาก `kubectl logs` หรือ `kubectl get events`

เมื่อสร้างภาวะล้มเหลวของระบบ ผู้เรียนควรวิเคราะห์อาการและระบุ layer ที่ขัดข้องก่อนดำเนินการแก้ไข
ทุกปฏิบัติการเริ่มต้นจากสถานะที่ปราศจากทรัพยากรคงค้าง สิ้นสุดด้วยการล้างทรัพยากร (Cleanup) และควรสร้างซ้ำโดยได้ผลลัพธ์เดิม

## ความรู้พื้นฐานที่ควรมีก่อนเรียน

- Linux command line: การเปลี่ยน directory การอ่านไฟล์ และความเข้าใจพื้นฐานเกี่ยวกับ process/port
- Docker: ความเข้าใจเกี่ยวกับ image, container, Docker Compose, network และ port mapping
- Git: การใช้ `clone` และการอ่านโครงสร้าง repository
- แนวคิดเกี่ยวกับ reverse proxy และ load balancer จากบทเรียนก่อนหน้า

ผู้เรียนไม่จำเป็นต้องมีประสบการณ์ใช้งาน Kubernetes หรือจดจำ syntax ของ manifest ล่วงหน้า

## ผลลัพธ์การเรียนรู้ทั้งชุด

- **LO1** อธิบายปัญหาที่ Kubernetes สามารถแก้ไขเพิ่มเติมจาก Docker Compose บนเครื่องเดียว และจำแนกความแตกต่างระหว่าง control plane กับ worker node ได้
- **LO2** อธิบายความหมายของ Pod และเหตุผลที่หน่วยเล็กที่สุดซึ่ง Kubernetes ดูแลมิใช่ container ได้
- **LO3** อธิบาย desired state กับ self-healing และเหตุผลที่ Deployment สร้าง Pod ใหม่แทน Pod ที่ถูกลบได้
- **LO4** อธิบายเหตุผลที่ต้องใช้ Service แทนการเรียก Pod IP โดยตรง และจำแนก ClusterIP จาก NodePort ได้
- **LO5** อธิบายเหตุผลที่ config/รหัสผ่านต้องอยู่นอก image และเหตุผลที่ Volume/PVC จำเป็นต่อข้อมูลที่ต้องคงอยู่
- **LO6** อธิบายการประกอบแอปพลิเคชันหลายชั้นและวิธีที่ rolling update ลดการหยุดชะงักต่อผู้ใช้ได้
- **LO7** ตรวจสอบตามลำดับ `get → describe → logs → events` และตีความสถานะ Pending, ImagePullBackOff กับ CrashLoopBackOff ได้

## ลำดับการเรียนรู้ 3 ครั้ง

| ครั้ง | โฟลเดอร์ | หัวข้อหลัก | จำนวนปฏิบัติการ | ไฟล์สไลด์ |
|---:|---|---|---:|---|
| 1 | [`01_Session1_Kubernetes_Basics/`](./01_Session1_Kubernetes_Basics/) | บทบาทของ Kubernetes และการดูแล desired state | 7 | [`Kubernetes_Session1_Slides.html`](./01_Session1_Kubernetes_Basics/Kubernetes_Session1_Slides.html) (81 หน้า) |
| 2 | [`02_Session2_Networking_Config_Storage/`](./02_Session2_Networking_Config_Storage/) | การสื่อสารระหว่างแอปพลิเคชัน การกำหนดค่า และการบันทึกข้อมูล | 7 | [`Kubernetes_Session2_Slides.html`](./02_Session2_Networking_Config_Storage/Kubernetes_Session2_Slides.html) (87 หน้า) |
| 3 | [`03_Session3_Application_Deployment/`](./03_Session3_Application_Deployment/) | การประกอบระบบ การปรับเปลี่ยนระบบ และการวินิจฉัยความผิดปกติ | 7 | [`Kubernetes_Session3_Slides.html`](./03_Session3_Application_Deployment/Kubernetes_Session3_Slides.html) (79 หน้า) |

การสอนแต่ละครั้งมี **คู่มือ YAML** สำหรับ object ที่ศึกษาในครั้งนั้น ซึ่งใช้ประกอบการศึกษาร่วมกับปฏิบัติการ: [`01_Session1_Kubernetes_Basics/YAML_Guide.md`](./01_Session1_Kubernetes_Basics/YAML_Guide.md) · [`02_Session2_Networking_Config_Storage/YAML_Guide.md`](./02_Session2_Networking_Config_Storage/YAML_Guide.md) · [`03_Session3_Application_Deployment/YAML_Guide.md`](./03_Session3_Application_Deployment/YAML_Guide.md) — โดยทุกปฏิบัติการมีหัวข้อ "การอ่าน YAML ของปฏิบัติการนี้" ซึ่งอธิบาย manifest ทีละบรรทัด

ไฟล์ [`Fullstack_Slides.html`](../02_Docker/03_Fullstack_App_Example/Fullstack_Slides.html) เป็น README/slide ต้นแบบด้านรูปแบบ มิใช่สไลด์สำหรับการสอนสามครั้งข้างต้น

## การเตรียมเครื่องเพียงครั้งเดียวสำหรับทั้งชุดวิชา

### 1. การเริ่มต้นเครื่องสำหรับปฏิบัติการ

เรียกใช้คำสั่งต่อไปนี้บนเครื่องหลัก ซึ่งสอดคล้องกับสภาพแวดล้อมกลางของทุกปฏิบัติการ

```bash
docker pull tuchsanai/devtools-k8s:2569_1
docker run -d --name devtools-k8s --privileged --shm-size=1g \
  --ulimit nofile=65536:65536 \
  -p 2299:22 -p 8080:80 -p 8443:443 -p 3000:3000 -p 9090:9090 \
  tuchsanai/devtools-k8s:2569_1
docker exec -it devtools-k8s bash
```

`--privileged` จำเป็นต่อ Docker-in-Docker และ kind ภายในเครื่องสำหรับปฏิบัติการแบบใช้แล้วทิ้ง
เมื่อป้อนคำสั่งในเทอร์มินัลของเครื่องสำหรับปฏิบัติการ ให้เรียก Ingress ที่ `http://localhost` (พอร์ต 80)
สำหรับเบราว์เซอร์บนเครื่องของผู้เรียน ให้เปิด `http://localhost:8080`; ส่วนหน้าเว็บที่ใช้ port-forward ให้เปิดที่ `http://localhost:3000`

หากมี container เดิมและประสงค์จะรักษางานไว้ ให้ใช้ `docker start devtools-k8s` แล้วจึงใช้ `docker exec` แทนการสร้างใหม่

### 2. การดึงโค้ดเพียงครั้งเดียว (Clone)

เรียกใช้คำสั่งต่อไปนี้ภายในเครื่องสำหรับปฏิบัติการ

```bash
mkdir -p ~/labwork
cd ~/labwork
git clone https://github.com/Tuchsanai/DevTools.git
cd ~/labwork/DevTools/05_kubernetes
```

หากดำเนินการ clone แล้ว ให้เข้าสู่ repository เดิมและดึงการเปลี่ยนแปลงตามนโยบายของชั้นเรียน โดยไม่จำเป็นต้อง clone ซ้ำ

### 3. การสร้าง cluster ด้วยสคริปต์ที่กำหนด

```bash
k8s-bootstrap
```

สคริปต์จะสร้าง kind cluster ชื่อ `devtools` ซึ่งประกอบด้วย 1 control-plane, 2 worker,
metrics-server และ ingress-nginx โดยใช้ context `kind-devtools`
สำหรับเครื่องที่มี RAM จำกัด สามารถเลือกใช้ `k8s-bootstrap --single-node` ได้ แต่ชื่อ node ในหลักฐานผลลัพธ์จะแตกต่างจากตัวอย่าง

### 4. การสร้างและนำเข้า image ของ SkillSpace ทั้ง 4 tag

```bash
cd ~/labwork/DevTools/05_kubernetes/app
./build-images.sh
kind load docker-image \
  k8s-lab-web:v1 k8s-lab-web:v2 k8s-lab-api:v1 k8s-lab-db:v1 \
  --name devtools
```

รายละเอียดของ endpoint และวิธีทดสอบแอปพลิเคชันปรากฏใน [`app/README.md`](./app/README.md)
กระบวนการ build ดำเนินการใน Docker daemon ของเครื่องสำหรับปฏิบัติการ ส่วน `kind load` นำ image เข้าสู่ runtime ของ node
หากไม่ดำเนินการขั้นตอนดังกล่าว Pod อาจแสดงสถานะ `ImagePullBackOff` แม้ผลลัพธ์จาก `docker images` จะแสดง image แล้ว

### 5. การตรวจสอบความพร้อม

```bash
kubectl get nodes
docker exec devtools-control-plane crictl images | grep k8s-lab
kubectl -n ingress-nginx get pods
```

✅ **ผลลัพธ์ที่คาดหวัง (Expected output)** — อ้างอิงรูปแบบจาก LAB 001; ค่า `AGE`, image ID, ขนาด และชื่อ Pod อาจแตกต่างกันได้

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

ผลลัพธ์ในบรรทัด ingress controller ต้องมีสถานะ `Running` และค่า `READY` เป็น `1/1`; ชื่อ Pod มี hash จึงอาจแตกต่างกัน

## เวอร์ชันที่กำหนดในเครื่องสำหรับปฏิบัติการ

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

การระบุเวอร์ชันเหล่านี้มีวัตถุประสงค์เพื่อให้สามารถทำซ้ำผลการปฏิบัติในชั้นเรียนได้ มิใช่คำแนะนำให้กำหนดเวอร์ชันของ production อย่างถาวร
ก่อนนำไปใช้งานจริง ต้องตรวจสอบ release notes, compatibility และ patch version ที่แก้ไขช่องโหว่ล่าสุดเสมอ
เครื่องมือ Tier 2 เช่น Argo CD, Flux, Trivy, kube-linter, kubeconform และ Skaffold มีใน image
แต่ไม่ได้เป็นเนื้อหาหลักของปฏิบัติการและไม่มีหมายเลขเวอร์ชันที่ยืนยันในข้อกำหนดนี้ จึงไม่ระบุหมายเลขเวอร์ชันเพิ่มเติมโดยปราศจากข้อมูลยืนยัน

## แผนผังโดยสังเขปของโฟลเดอร์

```text
05_kubernetes/
├── README.md
├── 01_Session1_Kubernetes_Basics/             # LAB 001–007
├── 02_Session2_Networking_Config_Storage/      # LAB 008–014
├── 03_Session3_Application_Deployment/         # LAB 015–021
├── app/                                        # SkillSpace + build-images.sh
└── PROMPT_Kubernetes_Course_Spec.txt           # ข้อกำหนดของชุด
```

ให้เริ่มต้นจาก README ของการสอนครั้งที่กำลังศึกษา แล้วจึงอ่าน README ของปฏิบัติการตามลำดับ
ประเด็นสำคัญที่ควรจดจำ: **การดำเนินงานมิใช่การกำหนด container ทีละหน่วย แต่เป็นการประกาศสภาพที่ต้องการ แล้วตรวจสอบหลักฐานว่า Kubernetes ปรับระบบไปสู่สภาพดังกล่าวอย่างไร**
