import os
from typing import Literal

import cv2
import numpy as np
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import Response


Mode = Literal["grayscale", "edges", "blur"]
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")

app = FastAPI(
    title="Vision Lab API",
    version=APP_VERSION,
    description="Small OpenCV API used to demonstrate container networking.",
)


def decode_image(raw: bytes) -> np.ndarray:
    data = np.frombuffer(raw, dtype=np.uint8)
    image = cv2.imdecode(data, cv2.IMREAD_COLOR)
    if image is None:
        raise HTTPException(status_code=415, detail="ไฟล์นี้ไม่ใช่ภาพที่ OpenCV อ่านได้")
    return image


def apply_filter(image: np.ndarray, mode: Mode) -> np.ndarray:
    if mode == "grayscale":
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    if mode == "edges":
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return cv2.Canny(gray, 80, 160)
    if mode == "blur":
        return cv2.GaussianBlur(image, (19, 19), 0)
    raise HTTPException(status_code=422, detail=f"ไม่รู้จักโหมด {mode}")


def as_png(image: np.ndarray, mode: str) -> Response:
    ok, encoded = cv2.imencode(".png", image)
    if not ok:
        raise HTTPException(status_code=500, detail="เข้ารหัส PNG ไม่สำเร็จ")
    height, width = image.shape[:2]
    return Response(
        content=encoded.tobytes(),
        media_type="image/png",
        headers={
            "X-Process-Mode": mode,
            "X-Image-Width": str(width),
            "X-Image-Height": str(height),
            "X-App-Version": APP_VERSION,
        },
    )


def make_demo_image() -> np.ndarray:
    image = np.full((420, 720, 3), (248, 250, 252), dtype=np.uint8)
    cv2.rectangle(image, (35, 35), (685, 385), (171, 100, 24), 8)
    cv2.circle(image, (160, 205), 92, (74, 158, 237), -1)
    cv2.rectangle(image, (305, 115), (640, 295), (34, 197, 94), -1)
    cv2.putText(
        image,
        "Docker + OpenCV",
        (250, 350),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.15,
        (30, 30, 30),
        3,
        cv2.LINE_AA,
    )
    return image


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "vision-api", "version": APP_VERSION}


@app.get("/demo/{mode}", response_class=Response)
def demo(mode: Mode) -> Response:
    return as_png(apply_filter(make_demo_image(), mode), mode)


@app.post("/process", response_class=Response)
async def process_image(
    file: UploadFile = File(...),
    mode: Mode = Form("grayscale"),
) -> Response:
    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="ไฟล์ว่าง")
    return as_png(apply_filter(decode_image(raw), mode), mode)
