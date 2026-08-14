"""DevOps Board API สำหรับ LAB Docker Compose"""

import os
import socket
import time
from datetime import date, datetime

import psycopg
import redis
from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException


app = Flask(__name__)

# อ่านคอนฟิกจาก environment โดยใช้ชื่อ service ใน Compose เป็นค่าเริ่มต้น
REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
DB_HOST = os.environ.get("DB_HOST", "db")
POSTGRES_USER = os.environ.get("POSTGRES_USER", "appuser")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "")
POSTGRES_DB = os.environ.get("POSTGRES_DB", "appdb")
APP_ENV = os.environ.get("APP_ENV", "")
BOARD_TEAM = os.environ.get("BOARD_TEAM", "")
# เวลาที่ image ถูก build — Dockerfile เขียนไฟล์นี้ไว้ตอน docker build
try:
    API_BUILD_TIME = open("/app/BUILD_TIME", encoding="utf-8").read().strip()
except OSError:
    API_BUILD_TIME = "unknown"

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=6379,
    decode_responses=True,
    socket_connect_timeout=3,
    socket_timeout=3,
)


def db_connect():
    """เปิด connection ใหม่เพื่อให้แอปฟื้นตัวได้เมื่อ DB กลับมาออนไลน์"""
    return psycopg.connect(
        host=DB_HOST,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        dbname=POSTGRES_DB,
        connect_timeout=3,
    )


def retry_startup_services(attempts=10, delay=2):
    """ลองเชื่อมต่อ Redis และ PostgreSQL ซ้ำช่วงเริ่มต้น โดยไม่ทำให้ API ล่ม"""
    redis_ready = False
    db_ready = False

    for attempt in range(1, attempts + 1):
        if not redis_ready:
            try:
                redis_ready = bool(redis_client.ping())
            except redis.RedisError:
                pass

        if not db_ready:
            try:
                with db_connect() as connection:
                    connection.execute("SELECT 1")
                db_ready = True
            except psycopg.Error:
                pass

        if redis_ready and db_ready:
            return

        if attempt < attempts:
            time.sleep(delay)


def serialize_item(row):
    """แปลงแถวข้อมูลเป็น JSON contract ของรายการ"""
    created_at = row[4]
    if isinstance(created_at, (datetime, date)):
        created_at = created_at.strftime("%Y-%m-%d %H:%M:%S")

    return {
        "id": row[0],
        "name": row[1],
        "owner": row[2],
        "status": row[3],
        "created_at": created_at,
    }


@app.after_request
def disable_cache(response):
    """ป้องกัน browser หรือ proxy cache คำตอบทุก endpoint"""
    response.headers["Cache-Control"] = "no-store"
    return response


@app.get("/health")
def health():
    """ตอบสถานะ process ของ API สำหรับ Compose healthcheck"""
    return jsonify(status="ok"), 200


@app.get("/stats")
def stats():
    """รวมสถานะ service ตัวนับ และรายการจากฐานข้อมูล"""
    visits = -1
    redis_status = "down"
    redis_detail = "PONG"
    try:
        visits = int(redis_client.incr("devopsboard:visits"))
        redis_status = "up"
        redis_detail = "PONG"
    except redis.RedisError as error:
        app.logger.warning("Redis unavailable: %s", error)

    items = []
    db_status = "down"
    db_detail = "PostgreSQL 17.x"
    try:
        with db_connect() as connection:
            rows = connection.execute(
                "SELECT id, name, owner, status, created_at FROM items ORDER BY id"
            ).fetchall()
        items = [serialize_item(row) for row in rows]
        db_status = "up"
    except psycopg.Error as error:
        app.logger.warning("PostgreSQL unavailable: %s", error)

    return jsonify(
        visits=visits,
        hostname=socket.gethostname(),
        app_env=APP_ENV,
        env_file_only=BOARD_TEAM,
        api_build_time=API_BUILD_TIME,
        services=[
            {"name": "redis", "status": redis_status, "detail": redis_detail},
            {"name": "db", "status": db_status, "detail": db_detail},
        ],
        items=items,
        item_count=len(items),
    )


@app.post("/items")
def create_item():
    """ตรวจข้อมูลและเพิ่มรายการใหม่ลง PostgreSQL"""
    payload = request.get_json(silent=True) or {}
    name = payload.get("name")
    if not isinstance(name, str) or not name.strip():
        return jsonify(ok=False, error="name is required"), 400

    owner = payload.get("owner", "student")
    if not isinstance(owner, str) or not owner.strip():
        owner = "student"
    else:
        owner = owner.strip()
    try:
        with db_connect() as connection:
            row = connection.execute(
                """
                INSERT INTO items (name, owner, status)
                VALUES (%s, %s, 'new')
                RETURNING id, name, owner, status, created_at
                """,
                (name.strip(), owner),
            ).fetchone()
    except psycopg.Error as error:
        return jsonify(ok=False, error=str(error)), 503

    return jsonify(ok=True, item=serialize_item(row)), 201


@app.errorhandler(HTTPException)
def handle_http_error(error):
    """ทำให้ข้อผิดพลาด HTTP เช่น 404 ตอบเป็น JSON เสมอ"""
    return jsonify(ok=False, error=error.description), error.code


@app.errorhandler(Exception)
def handle_unexpected_error(error):
    """กันข้อผิดพลาดที่ไม่คาดคิดไม่ให้ตอบเป็นหน้า HTML"""
    return jsonify(ok=False, error=str(error)), 500


if __name__ == "__main__":
    retry_startup_services()
    app.run(host="0.0.0.0", port=5000)
