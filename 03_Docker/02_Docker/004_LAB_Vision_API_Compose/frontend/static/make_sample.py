"""สร้างรูปตัวอย่าง sample.jpg ที่มี "ขอบ" ชัด ๆ ไว้ทดสอบ Canny (ผลลัพธ์เหมือนเดิมทุกครั้ง)

รันด้วย image ของ backend ซึ่งมี numpy + opencv อยู่แล้ว:
    docker run --rm -v "$PWD/frontend/static:/out" vision-backend:1.0 python /out/make_sample.py
"""
import os

import cv2
import numpy as np

W, H = 800, 600
img = np.zeros((H, W, 3), np.uint8)

# ท้องฟ้าไล่สี
for y in range(H):
    t = y / H
    img[y, :] = (int(160 - 90 * t), int(90 + 40 * t), int(40 + 30 * t))

# ดวงอาทิตย์
cv2.circle(img, (660, 120), 60, (60, 200, 250), -1)
cv2.circle(img, (660, 120), 60, (20, 60, 110), 3)

# พื้น
cv2.rectangle(img, (0, 470), (W, H), (60, 70, 80), -1)

# ตึกสามหลัง + หน้าต่าง
buildings = [(60, 250, 200, 470), (240, 170, 380, 470), (420, 300, 560, 470)]
for x1, y1, x2, y2 in buildings:
    cv2.rectangle(img, (x1, y1), (x2, y2), (210, 210, 205), -1)
    cv2.rectangle(img, (x1, y1), (x2, y2), (30, 30, 30), 3)
    for wy in range(y1 + 25, y2 - 25, 45):
        for wx in range(x1 + 20, x2 - 30, 45):
            cv2.rectangle(img, (wx, wy), (wx + 25, wy + 25), (40, 40, 45), -1)

# หลังคาสามเหลี่ยม
cv2.fillPoly(img, [np.array([[240, 170], [310, 110], [380, 170]])], (90, 90, 200))
cv2.polylines(img, [np.array([[240, 170], [310, 110], [380, 170]])], True, (20, 20, 20), 3)

# ถนน + เส้นแบ่งเลน
cv2.line(img, (0, 540), (W, 540), (240, 240, 240), 4)
for x in range(20, W, 90):
    cv2.line(img, (x, 570), (x + 45, 570), (240, 240, 240), 5)

# ตารางเช็ก (ขอบถี่ ๆ)
for i in range(6):
    for j in range(3):
        if (i + j) % 2 == 0:
            cv2.rectangle(img, (600 + i * 30, 300 + j * 30),
                          (628 + i * 30, 328 + j * 30), (250, 250, 250), -1)

cv2.putText(img, "DOCKER VISION LAB", (60, 100), cv2.FONT_HERSHEY_SIMPLEX,
            1.1, (255, 255, 255), 3, cv2.LINE_AA)

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample.jpg")
cv2.imwrite(out, img, [cv2.IMWRITE_JPEG_QUALITY, 88])
print("wrote", out, os.path.getsize(out), "bytes")
