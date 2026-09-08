แก้ไฟล์ [Kubernetes_Session2_Slides.html](/root/workspace/DevTools/05_kubernetes/02_Session2_Networking_Config_Storage/Kubernetes_Session2_Slides.html) เรียบร้อย

หน้าที่แก้ — เลขหลังแก้:

- หน้า 3: d09 เป็นภาพหลักกว้าง 1,154px
- หน้า 8: รวม Deployment + Ingress; โค้ดฝั่งละ 16 บรรทัด ขนาด 18px
- หน้า 52: `Volume · emptyDir (ก่อน LAB 012)`
- หน้า 64: `PersistentVolumeClaim (ก่อน LAB 013)`
- หน้า 72: รวม screenshot ticket #9 ก่อน–หลังไว้หน้าเดียว
- หน้า 13, 24, 34, 45, 56, 68, 79: รวมข้อความ “จำให้ได้” จากหน้าทฤษฎี 4/4 เข้า caption
- หน้า 9, 30, 74: ย้ายเนื้อหาที่เคยแก้ด้วย JavaScript มาอยู่ใน HTML โดยตรง
- Footer ของหน้า YAML ตรงกับ anchor ใน `YAML_Guide.md` ครบ
- จำนวนหน้าจริงทั้ง source และ browser ลดจาก 97 เหลือ 88 หน้า

ผล `check-slides.js`:

- Slides: 88
- Images: 48
- Broken images: 0
- External refs/imports: 0
- Page errors: 0
- Navigation และ controls: ผ่านทั้งหมด
- End navigation: `#88`
- Rendered screenshots: 88 ไฟล์
- เปิดตรวจภาพทุกหน้าที่แก้แล้ว ไม่พบข้อความชน footer หรือถูกตัด

ตรวจ schema ด้วย `kubectl explain` ผ่าน container `devtools-k8s-verify` ตามแนวทาง `devtools-lab`; ไม่ได้สร้างหรือลบ container เพิ่ม

ข้อที่ไม่แก้: ไม่มีข้อค้าง ส่วน Expected output เดิมถูกย่อเหลือเฉพาะหลักฐานสำคัญ 3–9 บรรทัดอยู่แล้ว จึงไม่ตัดข้อมูลเพิ่มครับ