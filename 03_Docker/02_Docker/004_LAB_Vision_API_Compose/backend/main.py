"""Vision API — รับรูปแบบ base64 แล้วส่งภาพขอบ (Canny) กลับไป"""

import base64
import os
from typing import List

import cv2
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# ค่า threshold ของ Canny อ่านจาก environment variable (ตั้งจากข้างนอกได้ — LAB 2)
CANNY_LOW = int(os.environ.get("CANNY_LOW", "100"))
CANNY_HIGH = int(os.environ.get("CANNY_HIGH", "200"))

app = FastAPI(title="Vision API", version="1.0")


class ImageRequest(BaseModel):
    image: str
    name: str
    surname: str
    numbers: List[int]


def encode_image(image) -> str:
    """numpy array -> data URL (base64 jpeg)"""
    _, encoded_image = cv2.imencode(".jpg", image)
    return "data:image/jpeg;base64," + base64.b64encode(encoded_image).decode()


def decode_image(image_string: str):
    """data URL (base64 jpeg) -> numpy array"""
    encoded_data = image_string.split(",")[1]
    nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
    return cv2.imdecode(nparr, cv2.IMREAD_COLOR)


def apply_canny(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.Canny(gray, CANNY_LOW, CANNY_HIGH)


@app.get("/healthz")
def healthz():
    return {
        "status": "ok",
        "canny_low": CANNY_LOW,
        "canny_high": CANNY_HIGH,
        "cv2": cv2.__version__,
    }


@app.post("/process-image")
async def process_image(image_request: ImageRequest):
    image = decode_image(image_request.image)
    if image is None:
        raise HTTPException(status_code=400, detail="decode image failed")

    edges = apply_canny(image)
    processed_image = encode_image(edges)

    return {
        "name": image_request.name,
        "surname": image_request.surname,
        "numbers": image_request.numbers,
        "processed_image": processed_image,
    }
