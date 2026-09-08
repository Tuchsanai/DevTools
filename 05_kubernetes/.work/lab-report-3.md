ทำ LAB 007–009 เสร็จครบและรันจริงแล้ว

- [LAB 007 README](/root/workspace/DevTools/05_kubernetes/01_Session1_Kubernetes_Basics/007-deployment-manages-change/README.md) — 400 บรรทัด  
  ผ่าน: Deployment→ReplicaSet→Pod, scale 3→5→3, rollout v1→v2, undo กลับ v1, ทดลอง v3 จนเกิด `ImagePullBackOff`, rollback, Cleanup และ Clean Re-run  
  [Raw transcript](/root/workspace/DevTools/05_kubernetes/.work/runlogs/lab007.txt)

- [LAB 008 README](/root/workspace/DevTools/05_kubernetes/02_Session2_Networking_Config_Storage/008-why-we-need-service/README.md) — 389 บรรทัด  
  ผ่าน: เรียก API ด้วย Pod IP, ลบ Pod แล้ว IP เก่าใช้ไม่ได้, Service DNS/Endpoints, กระจาย connection สอง API Pods, selector ผิดจนไม่มี endpoint, แก้กลับ, Cleanup และ Clean Re-run  
  [Raw transcript](/root/workspace/DevTools/05_kubernetes/.work/runlogs/lab008.txt)

- [LAB 009 README](/root/workspace/DevTools/05_kubernetes/02_Session2_Networking_Config_Storage/009-service-types-and-access/README.md) — 390 บรรทัด  
  ผ่าน: ClusterIP, NodePort จากทั้งสาม nodes, port-forward และ screenshot, nodePort นอกช่วง/ซ้ำถูกปฏิเสธ, Cleanup และ Clean Re-run  
  [Raw transcript](/root/workspace/DevTools/05_kubernetes/.work/runlogs/lab009.txt)

จุดที่เบี่ยงจาก outline ตามผลจริง:

- Ingress ต้องใช้เวลาสั้น ๆ เพื่อ sync; request แรกของ LAB 007/008 เคยได้ HTML 404 จึงเพิ่มขั้นรอก่อนส่งผลเข้า `jq`
- API ไม่มี readinessProbe ใน LAB 008/009 จึงอาจ Running ก่อน Uvicorn ฟังพอร์ต ต้อง retry `/health`
- หลังลบ API Pod ผ่าน Service พบ `fetch failed` ชั่วครู่จาก HTTP connection reuse ก่อน reconnect เอง จึงไม่อ้างว่าไร้การสะดุดโดยเด็ดขาด
- UI ไม่ได้สลับ API Pod ทุก refresh อย่างสม่ำเสมอเพราะ keep-alive จึงพิสูจน์ load balancing ด้วย connection ใหม่จาก `wget`
- BusyBox `nslookup` แสดง FQDN/ClusterIP ถูกต้อง แต่คืน exit code 1 จาก search suffix ที่หาไม่พบ
- curl policy ในเครื่องเรียน retry timeout หลายครั้งก่อนคืน exit code 28

สิ่งที่ยังค้าง: ไม่มีในขอบเขต LAB ไฟล์ diagram ทั้งสามมีอยู่และลิงก์ใช้งานได้แล้ว อย่างไรก็ตาม public GitHub ที่ clone ระหว่างทดสอบยังไม่มีโฟลเดอร์ใหม่เหล่านี้ จึงต้อง commit/push งานชุดนี้ก่อนผู้เรียนจะ `cd` ตาม README ได้

ตรวจ manifest แบบ client dry-run ผ่านทั้งหมด ยกเว้น `03-nodeport-bad.yaml` ซึ่งตั้งใจให้ server ปฏิเสธและตรวจเห็น error จริงแล้ว

ลบ `devtools-k8s-lab-g3` เรียบร้อย และยืนยันว่าไม่เหลือ container ชื่อนี้, namespace `lab007`–`lab009`, resource หรือ port-forward ค้างอยู่ครับ