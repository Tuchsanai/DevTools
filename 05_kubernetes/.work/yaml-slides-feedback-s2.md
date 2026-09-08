# feedback ของ yolo1 — หน้ากายวิภาค YAML สไลด์ครั้งที่ 2 (หน้า 3, 8, 9, 10, 33, 45, 57, 70, 82, 83 — ตำแหน่งถูกต้องแล้ว)
1. **จำนวนหน้า 97 เกินเพดาน 90**: ลดให้ ≤ 90 (ยอมได้ไม่เกิน 92) โดยห้ามตัดหน้า YAML และห้ามลด object: (ก) รวมหน้า "โครง object" (3) กับ "Deployment" (8) + "Ingress" (9) ทบทวน → 2 หน้า (ข) รวมหน้าหลักฐาน screenshot ก่อน/หลังที่แสดงการ์ดสถานะแบบเดียวกันเป็น 2 ภาพต่อหน้า (ค) หน้า Expected output ยาวให้เหลือบรรทัดหลักฐาน
2. หน้า 57 และ 70 ใช้ชื่อเดียวกัน "Volume / PVC" → ตั้งชื่อให้ต่าง: 57 = "Volume · emptyDir (ก่อน LAB 012)" · 70 = "PersistentVolumeClaim (ก่อน LAB 013)"
3. หน้า 3: ไดอะแกรม d09 ต้องเป็นภาพหลักอ่านออก (≥ 700px) ไม่ใช่ thumbnail
4. ทุกหน้า YAML: โค้ด ≥ 18px ≤ 16 บรรทัด (`# ...` ตรงที่ตัด) · footer anchor ตรงกับ YAML_Guide.md ครั้งที่ 2 (#deployment #ingress #service #configmap #secret #volume-pvc #probes)
(รวมกับ feedback ของ cyolo1 จาก .work/yaml-slides-review-s2.md เมื่อมาถึง)

## รวม feedback ของ cyolo1 (จาก .work/yaml-slides-review-s2.md ส่วน A) — ให้แก้ทุกข้อที่ยังคะแนน < 5 ในส่วน B ของรายงานนั้นด้วย · ข้อ 1 (จำนวนหน้า ≤ 90-92) เป็นข้อบังคับ
