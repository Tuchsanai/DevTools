# เตรียมสภาพแวดล้อม Kubernetes สำหรับแล็บ

คู่มือนี้ใช้เตรียมเครื่องให้พร้อมสำหรับแล็บของผู้สอน โดยรัน container `k8s-lab` สำหรับทดลอง Kubernetes บนเครื่องนักศึกษา ภายในมี `kubectl` และเครื่องมือ Kubernetes ที่ใช้ในแล็บ

![เครื่องนักศึกษารัน container k8s-lab ที่มีเครื่องมือ Kubernetes พร้อมสำหรับแล็บ](images/01-environment-overview.png)

ก่อนเริ่ม ให้ติดตั้งและเปิด Docker Desktop โดยใช้ Linux containers แล้วเปิด Terminal หรือ PowerShell ในโฟลเดอร์ `02_LAB` ที่มี `Dockerfile` และ `Devtool_SSH`

ตัวอย่างผลลัพธ์ด้านล่างมาจากการทดลองจริงผ่าน CLI บนเครื่องโลคอลและล็อกอิน SSH ด้วยรหัสผ่าน `passwd` วันที่ 4 ตุลาคม 2569 ตัดบางส่วนเพื่อให้อ่านง่าย โดยเวลา, ID และเวอร์ชันอาจต่างกันในแต่ละเครื่อง

## 1. Build image แล้ว Run container

![ขั้นตอน Build image จาก Dockerfile แล้ว Run container k8s-lab](images/02-build-then-run.png)

รันคำสั่งต่อไปนี้ **บนเครื่องนักศึกษา** โดย build image ก่อน:

```powershell
docker build -t devtools-kind:2569_1 .
```

เมื่อสำเร็จจะเห็นการตั้งชื่อ image (ตัดจากท้าย build log):

```text
#29 naming to docker.io/library/devtools-kind:2569_1 done
#29 DONE 0.4s
```

เมื่อ build สำเร็จ ให้สร้างและเริ่ม container (คัดลอกทั้งบรรทัด):

```powershell
docker run -dit --name k8s-lab --hostname k8s-lab --privileged -p 2223:22 -p 8889:8888 -p 30080-30082:30080-30082 -v "${PWD}/Devtool_SSH:/etc/devtools/ssh" devtools-kind:2569_1
```

ผลลัพธ์คือ ID ของ container ที่สร้างขึ้น:

```text
587e89ac026f5b8f0c4bee2233d482ce9f8841c458d90528d28e751a08509f14
```

`--privileged` รองรับ Docker ภายใน container สำหรับแล็บ ส่วน `-v` เชื่อมโฟลเดอร์ SSH keys จากเครื่องนักศึกษา พอร์ตที่เตรียมไว้คือ SSH `2223`, JupyterLab `8889` และพอร์ตสำหรับแล็บ `30080–30082`

ตรวจว่า container ทำงานและดูข้อความเริ่มต้น:

```powershell
docker ps --filter name=k8s-lab
docker logs k8s-lab
```

ควรเห็น `k8s-lab` มีสถานะ `Up` และ log จาก `start.sh` ระบุบริการ `sshd`, `dockerd` และ `jupyter lab`

ผล `docker ps` ที่ทดลองได้ (แสดงเฉพาะคอลัมน์สำคัญ):

```text
CONTAINER ID   IMAGE                  STATUS         NAMES
587e89ac026f   devtools-kind:2569_1   Up 4 seconds   k8s-lab
```

ส่วนหนึ่งของ `docker logs` ที่ยืนยันว่าเริ่มต้นและตั้งค่า SSH แล้ว:

```text
[start.sh] cgroup v2 controllers: cpuset cpu io memory hugetlb pids rdma
[start.sh] SSH key login enabled: /etc/devtools/ssh/devtoolSSH.pub
```

## 2. ล็อกอินเข้า container ผ่าน SSH

บนเครื่องนักศึกษา เชื่อมต่อ SSH ไปยัง `k8s-lab` เหมือนล็อกอินเข้าเซิร์ฟเวอร์ โดยใช้พอร์ต `2223` ที่เชื่อมไปยัง SSH ภายใน container:

```powershell
ssh -p 2223 root@localhost
```

ครั้งแรก SSH อาจถามให้ยืนยัน host key เมื่อเชื่อมต่อ `localhost` ของแล็บบนเครื่องตัวเอง ให้พิมพ์ `yes` แล้วกด Enter จากนั้นเมื่อถามรหัสผ่าน ให้พิมพ์ `passwd` แล้วกด Enter (ขณะพิมพ์รหัสผ่านจะไม่เห็นตัวอักษรบนหน้าจอ)

เมื่อล็อกอินสำเร็จ จะอยู่ใน shell ของ `k8s-lab` เช่น prompt `root@k8s-lab` ให้ใช้ SSH session นี้ทำขั้นตอนถัดไป

ตัวอย่างผลจากการเชื่อมต่อครั้งแรก (ตัด fingerprint และข้อความต้อนรับบางส่วน):

```text
The authenticity of host '[localhost]:2223 ([::1]:2223)' can't be established.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '[localhost]:2223' (ED25519) to the list of known hosts.
root@localhost's password:
Welcome to Ubuntu 24.04.5 LTS (GNU/Linux 6.6.87.2-microsoft-standard-WSL2 x86_64)
root@k8s-lab:~#
```

## 3. ตรวจว่าเครื่องมือ Kubernetes พร้อม

![ตรวจเวอร์ชันและรายการคำสั่ง kubectl ใน SSH session ของ k8s-lab เพื่อยืนยันว่าเครื่องมือพร้อม](images/03-kubectl-ready.png)

รันคำสั่งต่อไปนี้ **ใน SSH session ภายใน container `k8s-lab`**:

```bash
kubectl version --client
```

ผลลัพธ์จริง:

```text
Client Version: v1.37.1
Kustomize Version: v5.8.1
```

จากนั้นตรวจวิธีใช้และรายการคำสั่ง:

```bash
kubectl --help
```

ผลลัพธ์จริง (ตัดมาเฉพาะบางส่วนเพื่อความกระชับ):

```text
kubectl controls the Kubernetes cluster manager.

Basic Commands (Beginner):
  create          Create a resource from a file or from stdin

Usage:
  kubectl [flags] [options]

Use "kubectl <command> --help" for more information about a given command.
```

เมื่อเห็นเวอร์ชันและรายการคำสั่ง แสดงว่า **container มีเครื่องมือ Kubernetes ที่เรียกใช้งานได้ พร้อมสำหรับทำแล็บของผู้สอน**

ขั้นตอนนี้ตรวจเฉพาะเครื่องมือ ยังไม่ได้สร้างคลัสเตอร์หรือเริ่ม nodes
