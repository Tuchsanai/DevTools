งาน: เขียน `readme.md` ภาษาไทยสำหรับการเรียนการสอน Kubernetes ด้วย kind
ไฟล์ปลายทาง: /root/workspace/DevTools/k/001_kubernetes-introduction/02_LAB/00_Reference/01_Reference/readme.md

## อ่านก่อนเขียน
- ไฟล์ทั้งหมดใน 01_Reference/ (Dockerfile, start.sh, docker-compose.yml, kind-lab.yaml, k8s-up, k8s-down, examples/) — อ้างค่าจากไฟล์จริงเท่านั้น
- readme ต้นแบบ ../readme.md (00_Reference) — ใช้สไตล์เดียวกัน: ตารางสรุป, คำสั่ง copy-paste ได้, ตารางอธิบาย flag/คำสั่งทีละส่วน, กล่องตัวอย่าง output แบบ ```text
- output จริงจากการทดสอบ (ใช้เป็นตัวอย่าง output ในเอกสาร ตัดให้กระชับได้ แต่ห้ามแต่งตัวเลข/ชื่อที่ไม่มีใน log):
  /root/workspace/DevTools/k/001_kubernetes-introduction/logs/01_Reference/test_in_container.log
  /root/workspace/DevTools/k/001_kubernetes-introduction/logs/01_Reference/test_from_host.log
  /root/workspace/DevTools/k/001_kubernetes-introduction/logs/01_Reference/test_k8s_down.log
- รูปประกอบ 10 รูปใน 01_Reference/images/ (เปิดดูรูปด้วย Read เพื่อเขียนคำอธิบายให้ตรงกับภาพ) อ้างด้วย path สัมพัทธ์ `images/<ชื่อ>.png`:
  01-lab-big-picture, 02-what-is-kind, 03-build-and-run, 04-kind-create-cluster, 05-kubectl-kubeconfig,
  06-multi-node-scheduling, 07-deploy-first-app, 08-nodeport-path, 09-kind-load-image, 10-lifecycle-cleanup

## โครงเรื่อง (เล่าเป็นเรื่องราวต่อเนื่อง ทุกหัวข้อมีรูปประกอบตามลำดับ ใต้รูปมีคำอธิบายสั้น ๆ 2-4 บรรทัดว่าภาพสื่ออะไร)
0. หัวเรื่อง + ตารางสรุป container (base, DinD, kind/kubectl/helm/k9s พร้อมเวอร์ชันจริง, node image kindest/node:v1.37.0 = Kubernetes v1.37.0, ports 2223/8889/30080-30082, SSH root/passwd + key devtoolSSH, workdir) + คำเตือนความปลอดภัยแบบต้นแบบ + บอกว่าต่อยอดจาก 00_Reference (รันคู่กับ container `devtools` ได้เพราะพอร์ตไม่ชน)
1. ภาพรวม LAB (รูป 01) และ kind คืออะไร (รูป 02)
2. Build & Run (รูป 03): `docker compose up -d --build` (แนะนำ) และทางเลือก `docker build -t devtools-kind:2569_1 .` + `docker run -dit --name k8s-lab --hostname k8s-lab --privileged -p 2223:22 -p 8889:8888 -p 30080-30082:30080-30082 -v "${PWD}/Devtool_SSH:/etc/devtools/ssh" devtools-kind:2569_1` พร้อมตาราง flag; ตรวจ `docker logs k8s-lab` (ใช้บรรทัด [start.sh] จริง — ใน log จริงมีบรรทัด "generated new SSH key pair" เพราะทดสอบโดยไม่ mount key; ในเอกสารให้แสดงกรณี mount Devtool_SSH คือ "SSH key login enabled") ; ระบุว่าไม่มี image บน Docker Hub ต้อง build เอง
3. เข้าใช้งาน: SSH password / key (`ssh -p 2223 root@localhost`, `ssh -i Devtool_SSH/devtoolSSH -p 2223 root@localhost`), JupyterLab http://localhost:8889, `docker exec -it k8s-lab bash`
4. สร้างคลัสเตอร์ `k8s-up` (รูป 04) — แสดง output จริง, อธิบาย kind-lab.yaml ทีละส่วน, ตัวเลือก env (KIND_AUTO_CREATE=1 ใน compose, KIND_NODE_IMAGE, KIND_CLUSTER_NAME)
5. kubectl + kubeconfig (รูป 05) — `kubectl config current-context`, `kubectl get nodes`, `kubectl get pods -A` (output จริง) อธิบายแต่ละ pod ใน kube-system สั้น ๆ, alias `k` + Tab completion, k9s
6. คลัสเตอร์หลาย node และการ schedule (รูป 06) — `kubectl get pods -o wide` ดูว่า pod ไปอยู่ node ไหน
7. LAB 1 Deploy แอปแรก (รูป 07) — /workspace/examples/web-deployment.yaml (แสดง YAML), apply, rollout status, get pods -o wide, self-healing (ลบ pod แล้วเกิดใหม่) + hello-pod.yaml และ kubectl logs
8. LAB 2 เส้นทาง NodePort (รูป 08) — curl http://localhost:30080 จากใน container และเปิดเบราว์เซอร์บนเครื่อง host; ตารางพอร์ตทุกชั้น
9. LAB 3 image ที่ build เอง (รูป 09) — docker build myapp, kind load docker-image (output จริง), apply myapp.yaml, curl :30081 (หมายเหตุ: ถ้า curl ทันทีหลัง rollout อาจยังว่าง ให้รอ 2-3 วินาทีแล้วลองใหม่)
10. วงจรชีวิตและการล้าง (รูป 10) — k8s-down (output จริง), docker compose down, docker compose down -v, ตาราง "อะไรยังอยู่/หาย"
11. แบบฝึกหัดท้าย LAB 4-6 ข้อ (เช่น scale replicas, rolling update image nginx:alpine→nginx:1.27-alpine และ rollout undo, ติดตั้ง chart ด้วย helm, ใช้ k9s ดู pod) พร้อมคำสั่งเฉลยแบบพับได้ (<details>)
12. Troubleshooting — โดยเฉพาะ: kind ล้มด้วย `could not find a log line that matches "Reached target .*Multi-User System.*|detected cgroup v1"` / ใน node log `Failed to create /init.scope control group: Structure needs cleaning` = cgroup v2 nesting (start.sh แก้ให้แล้ว ตรวจด้วย `docker logs k8s-lab | grep cgroup` ต้องเห็น `cpuset cpu io memory hugetlb pids rdma`; ถ้าไม่เห็น memory/io ให้ `docker rm -f k8s-lab` แล้วรันใหม่ ห้ามแค่ restart dockerd); ลืม --privileged; พอร์ตชน (เปลี่ยน SSH_PORT/JUPYTER_PORT); `docker build` บน Docker Desktop error `error getting credentials` (ตั้ง credsStore / ใช้ DOCKER_CONFIG ชั่วคราว); ImagePullBackOff เมื่อลืม kind load; ดึง kindest/node ครั้งแรกช้า (~1GB) volume k8s-lab-dind เก็บไว้ให้
13. คำสั่งที่ใช้บ่อย (ตาราง)

## กฎ
- ภาษาไทยอ่านง่าย ใช้ศัพท์เทคนิคภาษาอังกฤษตามจริง, คำสั่งทั้งหมดต้องตรงกับไฟล์จริงและ log จริง
- ห้ามใส่ข้อมูลส่วนตัว/อีเมล/token จริง; path `/root/workspace/DGX_2024/.env` ใน compose ให้อธิบายว่าเป็น env_file ส่วนตัวแบบ optional (required: false) ไม่ต้องลงรายละเอียดเนื้อหา
- ห้ามแก้ไฟล์อื่นนอกจาก readme.md ห้าม docker build/run
- ตรวจหลังเขียน: ทุก `images/*.png` ที่อ้างมีไฟล์จริง, ไม่มีลิงก์เสีย
- ตอบกลับสั้น ๆ: จำนวนบรรทัด, หัวข้อหลัก, รูปที่ใช้
