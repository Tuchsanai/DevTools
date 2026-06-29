# ใบงาน: Base Learning Container สำหรับฝึกเครื่องมือ DevOps
### วิชา Software Development Tools and Environments

Container ฐานนี้ติดตั้งให้ล่วงหน้า **git**, **Docker (Docker-in-Docker)** และ **SSH server**
โดย **Docker daemon และ sshd จะสตาร์ทให้อัตโนมัติ** เมื่อเปิด container ส่วน **Web API** นักศึกษาติดตั้งเอง

> 📌 **ทุก LAB ต้องทำผ่าน SSH เท่านั้น** — เปิด container แล้ว SSH เข้าไปทำงาน
> (อย่าใช้เทอร์มินัลที่ attach โดยตรง หรือ `docker exec`)

---

## 1) สิ่งที่ต้องเตรียม
- Windows + **Docker Desktop** (เปิด **WSL2 backend** ใน Settings → General)
- เปิดด้วย **PowerShell**

## 2) รัน container
> ⚠️ ต้องใส่ `--privileged` เสมอ (Docker-in-Docker ต้องการ)
> รันแบบ `-dit` (เบื้องหลัง) เพราะเราจะเข้าไปทำงานผ่าน SSH

```powershell
# build image
docker build -t devtools-base-lab:24.04 .

# run แบบ detached (backtick ` = ขึ้นบรรทัดใหม่ใน PowerShell)
docker run -dit --privileged --name devtools-lab `
  -p 2222:22 `
  -p 8000:8000 `
  -v dind-data:/var/lib/docker `
  devtools-base-lab:24.04
```
> container จะรันเบื้องหลัง พร้อมสตาร์ท Docker daemon และ sshd ให้อัตโนมัติ

---

## 3) ภารกิจ — ทำผ่าน SSH ทุก LAB

**LAB 1 — SSH เข้า container จาก Windows  (ทำเป็นอันดับแรก)**
เชื่อมต่อจาก PowerShell (host พอร์ต 2222 -> container พอร์ต 22) ด้วยผู้ใช้ `student` รหัสผ่าน `student`:
```powershell
ssh student@localhost -p 2222
```
> ครั้งแรกจะถามยืนยัน fingerprint ให้พิมพ์ `yes` แล้วใส่รหัสผ่าน `student`
> หลัง login เปลี่ยนรหัสผ่านด้วยคำสั่ง `passwd` เพื่อความปลอดภัย
> **ทุก LAB ต่อจากนี้ให้ทำในเซสชัน SSH นี้**

ตรวจเครื่องมือที่ติดตั้งมาให้ (ในเซสชัน SSH):
```bash
git --version
docker run --rm hello-world        # ทดสอบ Docker-in-Docker
```

**LAB 2 — Web API ด้วย FastAPI**
สร้าง REST API ด้วย Python (FastAPI + uvicorn) แล้วเปิดดูจากเบราว์เซอร์บน Windows
ทำตามขั้นตอนต่อไปนี้ในเซสชัน SSH

1) สร้างโปรเจกต์ + virtual environment
```bash
cd ~
mkdir webapi && cd webapi
python -m venv venv
source venv/bin/activate            # prompt จะขึ้น (venv) นำหน้า
```
> Ubuntu 24.04 ใช้นโยบาย PEP 668 — ห้าม `pip install` ลงระบบตรง ๆ ต้องใช้ venv

2) ติดตั้งไลบรารี
```bash
pip install fastapi uvicorn
```

3) สร้างไฟล์ `main.py`
```bash
cat > main.py <<'PY'
from fastapi import FastAPI

app = FastAPI(title="DevTools Web API")

@app.get("/")
def home():
    return {"message": "Hello DevTools! Web API ทำงานแล้ว"}

@app.get("/students/{name}")
def greet(name: str):
    return {"student": name, "status": "ok"}
PY
```

4) รัน API ที่พอร์ต 8000
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```
> ต้องใช้ `--host 0.0.0.0` เพื่อให้เข้าถึงจากนอก container ได้ (อย่าใช้ 127.0.0.1)

5) ทดสอบจากเบราว์เซอร์บน Windows
- `http://localhost:8000` → เห็น JSON ตอบกลับ
- `http://localhost:8000/students/student01` → ลองส่งพารามิเตอร์ทาง URL
- `http://localhost:8000/docs` → หน้า **Swagger UI** อัตโนมัติ (ทดลองยิง API ได้จากหน้านี้)
> ถ้าอยากทดสอบในเชลล์: เปิด SSH อีกหน้าต่างแล้วใช้ `curl http://localhost:8000`

6) หยุด: กด `Ctrl + C` แล้วพิมพ์ `deactivate` เพื่อออกจาก venv

**LAB 3 — Docker-in-Docker**
เขียน Dockerfile เล็ก ๆ แล้ว `docker build` + `docker run` ภายใน container ให้สำเร็จ

---

## 4) เกณฑ์ส่งงาน
- [ ] รัน container ด้วย `docker run` สำเร็จ
- [ ] LAB 1: SSH จาก Windows เข้า container ได้ (แนบ screenshot)
- [ ] LAB 2: เปิด Web API ที่ `http://localhost:8000/docs` (Swagger UI) ได้ (แนบ screenshot)
- [ ] LAB 3: build และ run container ซ้อนใน DinD ได้

## 5) หยุด / ลบ
```powershell
docker stop devtools-lab           # หยุด container
docker start devtools-lab          # เปิดใหม่ (แล้ว ssh เข้าไปใหม่)
docker rm -f devtools-lab          # ลบ container
docker volume rm dind-data         # ลบข้อมูล DinD
```
