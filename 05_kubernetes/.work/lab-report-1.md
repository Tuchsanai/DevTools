ทำ LAB 001–003 เสร็จครบและทดสอบบน cluster จริงแล้ว

- [LAB 001 README](/root/workspace/DevTools/05_kubernetes/01_Session1_Kubernetes_Basics/001-kubernetes-introduction/README.md) — 395 บรรทัด  
  ผ่าน bootstrap, ตรวจ 3 nodes, system Pods, build/load image 4 ตัว, k9s, หยุด worker2 จน `NotReady` และกู้กลับ `Ready`
- [LAB 002 README](/root/workspace/DevTools/05_kubernetes/01_Session1_Kubernetes_Basics/002-kubectl-and-namespace/README.md) — 353 บรรทัด  
  ผ่านการทดลอง namespace, `get/describe/wide/yaml/explain`, ตั้ง context ผิดแล้วแก้กลับ และ Clean Re-run
- [LAB 003 README](/root/workspace/DevTools/05_kubernetes/01_Session1_Kubernetes_Basics/003-pod-the-smallest-unit/README.md) — 364 บรรทัด  
  ผ่าน Pod lifecycle, logs/exec, port-forward, screenshot จริง, sidecar `2/2`, ลบ Pod แล้วไม่เกิดใหม่ และ `ImagePullBackOff`
- [Sidecar manifest](/root/workspace/DevTools/05_kubernetes/01_Session1_Kubernetes_Basics/003-pod-the-smallest-unit/02-pod-with-sidecar.yaml)
- [Screenshot จริง](/root/workspace/DevTools/05_kubernetes/01_Session1_Kubernetes_Basics/003-pod-the-smallest-unit/images/03-first-page-on-kubernetes.png)

จุดที่เบี่ยงจาก outline:

- LAB 003 พบว่า `wget localhost:3000` ใน web container ได้ `Connection refused` แต่ `127.0.0.1:3000` ตอบจริง จึงปรับ sidecar ให้ใช้ IPv4 loopback และบันทึกอาการ/เหตุผลใน README
- LAB 001–002 ไม่มี manifest ตาม outline จึงปรับ Clean Re-run ให้ LAB 001 ตรวจ cluster ซ้ำ และ LAB 002 สร้าง namespace ซ้ำแบบ imperative
- ขั้น interactive shell ของ LAB 003 ถูกทดสอบอัตโนมัติผ่าน stdin แทน TTY แต่ README ยังคง `-it` สำหรับผู้เรียน

ปัญหาที่พบ:

- การบันทึก bootstrap รอบแรกถูกตัดกลาง stream จึง teardown และ bootstrap ใหม่หนึ่งรอบจนสำเร็จ พร้อมเก็บ output ครบ
- การหยุด worker2 ทำให้ metrics-server probe ล้มชั่วคราวและ restart ก่อนกลับมา `1/1 Running` ซึ่งบันทึกไว้ตามผลจริง

Transcript ดิบอยู่ที่ [lab001.txt](/root/workspace/DevTools/05_kubernetes/.work/runlogs/lab001.txt), [lab002.txt](/root/workspace/DevTools/05_kubernetes/.work/runlogs/lab002.txt) และ [lab003.txt](/root/workspace/DevTools/05_kubernetes/.work/runlogs/lab003.txt)

ไม่มีงานค้าง: ทั้งสาม namespace ไม่มี resource, ไม่มี port-forward ค้าง และไดอะแกรมทั้งสามไฟล์มีอยู่แล้ว

ลบ `devtools-k8s-lab-g1` เรียบร้อย และ `docker ps -a --filter name=devtools-k8s-lab-g1` ว่าง ส่วน container `devtools-k8s` ของผู้ใช้ยังทำงานและไม่ได้ถูกแก้ไข การแยกและ cleanup นี้ทำตามแนวทางของ skill `devtools-lab` ครับ