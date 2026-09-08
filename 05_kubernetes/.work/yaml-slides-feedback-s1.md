# feedback ของ yolo1 — หน้ากายวิภาค YAML สไลด์ครั้งที่ 1 (ดูหน้า 35-38, 59-60, 74-75 แล้ว)
ภาพรวม: โครงหน้าถูกต้อง ครอบ object ครบ (YAML คืออะไร · โครง object · Pod ×2 · ReplicaSet · Service+Ingress ทบทวน · Deployment ×2) — แก้เฉพาะ:
1. หน้า 35 การ์ด "ตรวจก่อนส่งจริง": ระบุ `kubectl apply --dry-run=client` แต่การ์ดผิดบ่อยยก `strict decoding error: unknown field` ซึ่ง client ไม่จับ (จับเฉพาะ server) → เปลี่ยนเป็น `kubectl apply --dry-run=server -f` และเขียนสั้น ๆ ว่า client = ตรวจแค่ syntax/kind (ให้ตรงกับ YAML_Guide.md ที่แก้แล้ว)
2. หน้า 36 "โครง object": ไดอะแกรม d09-yaml-anatomy เป็น thumbnail ~330px อ่านไม่ออก → ทำเป็นภาพหลักกว้างเต็มคอลัมน์ซ้าย (≥ 700px) หรือแยกเป็นหน้าไดอะแกรมเต็มหน้า + หน้าการ์ด
3. หน้า 35/37: พื้นที่ว่างมุมขวาล่าง ~30% → ขยายการ์ดหรือเพิ่มการ์ด "อ่านของจริง: kubectl get pod web -o yaml" ให้เต็ม
4. ทุกหน้า: footer anchor (#อ่าน-yaml-ให้เป็น · #pod · #replicaset · #service-และ-ingress · #deployment · #downward-api-ด้วย-fieldref) ตรวจว่ามีจริงใน YAML_Guide.md ครั้งที่ 1
(รวมกับ feedback ของ cyolo1 จาก .work/yaml-slides-review-s1.md เมื่อมาถึง)

## รวม feedback ของ cyolo1 (จาก .work/yaml-slides-review-s1.md ส่วน A) — ให้แก้ทุกข้อที่ยังคะแนน < 5 ในส่วน B ของรายงานนั้นด้วย
