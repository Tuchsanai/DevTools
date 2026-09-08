อ่านให้ครบก่อนเริ่ม:
- ข้อกำหนด : /root/workspace/DevTools/05_kubernetes/PROMPT_Kubernetes_Course_Spec.txt ส่วนที่ 5 (README 3 ระดับ — ห้ามเขียนซ้ำกัน แต่ละระดับตอบคนละคำถาม) · ส่วนที่ 1 (LO1-LO7 · หลักการ concept first) · ส่วนที่ 0 (วงจรการเรียนรู้) · ส่วนที่ 8 (สภาพแวดล้อม/เวอร์ชัน)
- แกนเนื้อหา : /root/workspace/DevTools/05_kubernetes/.work/lab-outline.md (กติการ่วม 10 ข้อ · แนวคิดหลักของทุกแล็บ)
- โครงจริงที่มีอยู่ : /root/workspace/DevTools/05_kubernetes (ls ทั้ง 3 โฟลเดอร์ครั้ง อ่านหัว README.md ของทั้ง 21 แล็บเพื่อดึงชื่อแล็บ แนวคิดหลัก ไฮไลต์ และ namespace ที่ใช้) · /root/workspace/DevTools/05_kubernetes/app/README.md (วิธี build image)
- README ต้นแบบระดับชุดของวิชานี้ (น้ำเสียง) : /root/workspace/DevTools/02_Docker/03_Fullstack_App_Example/readme.md

เขียน README 4 ไฟล์ (ภาษาไทย ศัพท์เทคนิคคงอังกฤษ น้ำเสียงครูที่ชวนคิด):
1. /root/workspace/DevTools/05_kubernetes/README.md — ระดับชุด (ส่วนที่ 5 ก) : ชื่อชุด+คำโปรย · วงจรการเรียนรู้ · ความรู้ที่ต้องมีมาก่อน · LO1-LO7 · ตารางสรุป 3 ครั้ง | ครั้ง | โฟลเดอร์ (ลิงก์) | ธีม | จำนวนแล็บ | ไฟล์สไลด์ | · การเตรียมเครื่องครั้งเดียวสำหรับทั้งชุด (คำสั่ง docker run ตามกติกาข้อ 9 ของ outline · k8s-bootstrap · build + kind load image แอปทั้ง 4 จาก app/ · คำสั่งตรวจความพร้อม พร้อม Expected output ที่ดึงจาก README แล็บ 001) · คำสั่ง clone ครั้งเดียว · ตารางเวอร์ชันที่ pin ทั้งหมด + คำเตือนเรื่อง patch version · แผนผังโฟลเดอร์ย่อ
2. /root/workspace/DevTools/05_kubernetes/01_Session1_Kubernetes_Basics/README.md — ระดับครั้ง (ส่วนที่ 5 ข)
3. /root/workspace/DevTools/05_kubernetes/02_Session2_Networking_Config_Storage/README.md
4. /root/workspace/DevTools/05_kubernetes/03_Session3_Application_Deployment/README.md
   แต่ละไฟล์ระดับครั้ง: ธีมและเป้าหมาย + ต่อยอดจากครั้งก่อนตรงไหน (อ้างเป็นข้อความ ไม่ใช่ path ข้ามโฟลเดอร์) · วิธีเปิดไฟล์สไลด์ของครั้งนี้ + ตารางปุ่มลัด (← → Space PgUp/PgDn Home End O F ? Esc Ctrl+P) · ตารางแล็บ | แล็บ | โฟลเดอร์ (ลิงก์สัมพัทธ์) | หัวข้อหลัก | ไฮไลต์ | ครบ 7 · ลำดับที่ควรทำ และแล็บที่ข้าม/แทรกได้ · การเตรียมและเก็บกวาดเฉพาะครั้งนี้ (namespace lab0NN ที่ใช้ · คำสั่งล้างทั้งหมด `kubectl delete ns lab0NN ...`) · เช็กลิสต์ปิดท้ายครั้ง (- [ ] อธิบายได้ว่า...)

กติกา: ลิงก์ทั้งหมดต้องชี้ไฟล์/โฟลเดอร์ที่มีจริง (ตรวจด้วย ls) · README ระดับครั้งห้ามอ้าง path ไปโฟลเดอร์ครั้งอื่นหรือไปที่ราก (ยกเว้นข้อความว่า "ดู README ระดับชุด") · ห้ามใส่ email/ชื่อจริง/token · ห้ามแก้ไฟล์อื่นนอกจาก 4 ไฟล์นี้ · ความยาว: ระดับชุด 120-200 บรรทัด · ระดับครั้ง 80-140 บรรทัด

รายงานกลับ (คำตอบสุดท้ายถูกเก็บเป็นไฟล์ — ห้ามสร้างไฟล์รายงานเพิ่ม): ไฟล์ที่เขียน + จำนวนบรรทัด · ลิงก์ที่ตรวจแล้วมีจริงทั้งหมดหรือไม่ · สิ่งที่ไม่แน่ใจ
