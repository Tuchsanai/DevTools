import io
import os

import requests
import streamlit as st
from PIL import Image


API_URL = os.getenv("API_URL", "http://api:8000").rstrip("/")
DEFAULT_MODE = os.getenv("PROCESS_MODE", "edges")
MODES = {
    "edges": "หาเส้นขอบ (Canny)",
    "grayscale": "แปลงเป็นขาวดำ",
    "blur": "Gaussian blur",
}

st.set_page_config(page_title="Vision Stack Lab", page_icon="🔬", layout="wide")
st.markdown(
    """
    <style>
      .block-container {max-width: 1050px; padding-top: 2rem;}
      [data-testid="stMetricValue"] {font-size: 1.35rem;}
      .hero {padding: 1.2rem 1.5rem; border-radius: 16px;
             background: linear-gradient(120deg,#0b2545,#1864ab); color:white; margin-bottom:1rem;}
      .hero h1 {margin:0; font-size:2.1rem;} .hero p {margin:.45rem 0 0; color:#d0ebff;}
    </style>
    <div class="hero"><h1>FastAPI + OpenCV + Streamlit</h1>
    <p>หนึ่งภาพเดินทางข้ามสอง container ผ่าน Docker DNS</p></div>
    """,
    unsafe_allow_html=True,
)

try:
    health = requests.get(f"{API_URL}/health", timeout=3)
    health.raise_for_status()
    api_status = health.json()
    st.success(f"API พร้อมใช้งาน · {api_status['service']} v{api_status['version']}")
except requests.RequestException as exc:
    st.error(f"ติดต่อ API ที่ {API_URL} ไม่ได้: {exc}")
    st.stop()

left, right = st.columns([0.42, 0.58], gap="large")
with left:
    st.subheader("1. เลือกวิธีประมวลผล")
    mode_keys = list(MODES)
    default_index = mode_keys.index(DEFAULT_MODE) if DEFAULT_MODE in mode_keys else 0
    mode = st.selectbox("โหมด", mode_keys, index=default_index, format_func=MODES.get)
    upload = st.file_uploader("2. อัปโหลด JPG หรือ PNG", type=["jpg", "jpeg", "png"])
    st.caption("ถ้ายังไม่อัปโหลด ระบบจะแสดงภาพตัวอย่างที่ API สร้างให้")
    st.metric("ปลายทางภายใน network", API_URL.replace("http://", ""))

try:
    if upload:
        original = Image.open(upload).convert("RGB")
        payload = io.BytesIO()
        original.save(payload, format="PNG")
        response = requests.post(
            f"{API_URL}/process",
            files={"file": ("upload.png", payload.getvalue(), "image/png")},
            data={"mode": mode},
            timeout=20,
        )
    else:
        original = None
        response = requests.get(f"{API_URL}/demo/{mode}", timeout=10)
    response.raise_for_status()
except (requests.RequestException, OSError) as exc:
    st.error(f"ประมวลผลไม่สำเร็จ: {exc}")
    st.stop()

with right:
    st.subheader("ผลลัพธ์จาก OpenCV")
    st.image(response.content, caption=f"โหมด: {MODES[mode]}", use_container_width=True)
    cols = st.columns(3)
    cols[0].metric("HTTP", response.status_code)
    cols[1].metric("กว้าง", response.headers.get("X-Image-Width", "?"))
    cols[2].metric("สูง", response.headers.get("X-Image-Height", "?"))

st.info("สังเกต: browser เห็นเฉพาะ Streamlit ส่วน Streamlit เรียก API ด้วยชื่อ service `api` ผ่าน network ภายใน")
