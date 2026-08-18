"""ChongJai Café API — FastAPI + SQL ตรง ไม่มี ORM"""

# (1) อ่าน feature flag ก่อน import broker: ปิดแล้วไม่มี client library ใน process
import json
import os
import socket
from contextlib import contextmanager
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

import psycopg
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from psycopg.rows import dict_row
from pydantic import BaseModel, Field, field_validator

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://student:student123@db:5432/cafedb")
RABBIT_URL = os.environ.get("RABBIT_URL", "amqp://student:student123@rabbit:5672/%2F")
KAFKA_BOOTSTRAP = os.environ.get("KAFKA_BOOTSTRAP", "kafka:9092")
ORDER_TRANSPORT = os.environ.get("ORDER_TRANSPORT", "db-only")
EVENTS_ENABLED = os.environ.get("EVENTS_ENABLED", "0") == "1"
API_VERSION = os.environ.get("API_VERSION", "1")
HOSTNAME = socket.gethostname()

if ORDER_TRANSPORT == "rabbit":
    import pika
if EVENTS_ENABLED:
    from kafka import KafkaProducer


# (2) นิยาม error และ request ให้ตรงรูปเดียวทั้งระบบ
class ApiError(HTTPException):
    def __init__(self, status_code: int, code: str, detail: str):
        super().__init__(status_code=status_code, detail=detail)
        self.code = code


class OrderCreate(BaseModel):
    menu_code: str
    qty: int = Field(ge=1, le=3)
    customer_name: str = Field(min_length=1, max_length=80)

    @field_validator("customer_name")
    @classmethod
    def name_not_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("ชื่อลูกค้าต้องไม่ว่าง")
        return value


@contextmanager
def get_conn():
    conn = psycopg.connect(DATABASE_URL, row_factory=dict_row)
    try:
        yield conn
    finally:
        conn.close()


def utc_text(value: datetime | None = None) -> str | None:
    if value is None:
        return None
    return value.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def order_json(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": row["id"], "menu_code": row["menu_code"], "menu_name_th": row["menu_name_th"],
        "qty": row["qty"], "customer_name": row["customer_name"], "status": row["status"],
        "price_total": float(row["price_total"]), "created_at": utc_text(row["created_at"]),
        "ready_at": utc_text(row["ready_at"]) if row["ready_at"] else None,
    }


ORDER_SELECT = """
SELECT o.id,o.menu_code,m.name_th AS menu_name_th,o.qty,o.customer_name,o.status,
       (m.price*o.qty)::numeric(12,2) AS price_total,o.created_at,o.ready_at
FROM orders o JOIN menus m ON m.code=o.menu_code
"""


# (3) middleware ทำให้ response จากแอปทุกชนิด รวม 404/422/503 มี header ครบ
app = FastAPI(title="ChongJai Café API", version=API_VERSION)
accepting = True


@app.middleware("http")
async def application_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Served-By"] = HOSTNAME
    response.headers["X-Cafe-Api-Version"] = API_VERSION
    return response


@app.exception_handler(HTTPException)
async def api_error_handler(request: Request, exc: HTTPException):
    code = getattr(exc, "code", "NOT_FOUND" if exc.status_code == 404 else "ERROR")
    return JSONResponse(status_code=exc.status_code, content={"detail": str(exc.detail), "code": code})


@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"detail": "ข้อมูลคำสั่งซื้อไม่ถูกต้อง", "code": "VALIDATION_ERROR"})


# (4) health สองแบบ: ping ไม่ toggle ส่วน active health แยกใน memory ต่อ replica
@app.get("/api/ping")
def ping():
    return {"status": "ok"}


@app.get("/api/health")
def health():
    if not accepting:
        raise ApiError(503, "HEALTH_FORCED", "พัก replica นี้ชั่วคราว")
    return {"status": "ok", "accepting": True}


@app.post("/api/health/fail")
def health_fail():
    global accepting
    accepting = False
    return {"status": "fail", "accepting": False}


@app.post("/api/health/ok")
def health_ok():
    global accepting
    accepting = True
    return {"status": "ok", "accepting": True}


# (5) endpoint อ่านข้อมูล ใช้ SQL ตรงตาม schema กลาง
@app.get("/api/menu")
def menu():
    with get_conn() as conn:
        rows = conn.execute("SELECT code,name_th,price FROM menus ORDER BY CASE code WHEN 'latte' THEN 1 WHEN 'espresso' THEN 2 WHEN 'americano' THEN 3 WHEN 'mocha' THEN 4 WHEN 'matcha' THEN 5 ELSE 6 END").fetchall()
    return {"items": [{"code": r["code"], "name_th": r["name_th"], "price": float(r["price"])} for r in rows]}


def rabbit_publish(message: dict[str, Any]) -> None:
    connection = pika.BlockingConnection(pika.URLParameters(RABBIT_URL))
    try:
        channel = connection.channel()
        channel.queue_declare(queue="order_queue", durable=True)
        channel.basic_publish(exchange="", routing_key="order_queue", body=json.dumps(message, ensure_ascii=False, separators=(",", ":")).encode("utf-8"), properties=pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent, content_type="application/json"))
    finally:
        connection.close()


def event_publish(event: dict[str, Any]) -> None:
    producer = KafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP, key_serializer=lambda value: value.encode("utf-8"), value_serializer=lambda value: json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))
    try:
        producer.send("cafe.events", key=event["menu_code"], value=event).get(timeout=10)
    finally:
        producer.close(timeout=5)


# (6) สร้าง order แล้วส่งหนึ่ง Rabbit message และหนึ่ง ORDER_PLACED ตาม feature ที่เปิด
@app.post("/api/orders", status_code=201)
def create_order(body: OrderCreate):
    with get_conn() as conn:
        menu_row = conn.execute("SELECT name_th,price FROM menus WHERE code=%s", (body.menu_code,)).fetchone()
        if menu_row is None:
            raise ApiError(404, "MENU_NOT_FOUND", f"ไม่พบเมนูรหัส {body.menu_code}")
        row = conn.execute("INSERT INTO orders(menu_code,qty,customer_name) VALUES (%s,%s,%s) RETURNING id,menu_code,qty,customer_name,status,created_at,ready_at", (body.menu_code, body.qty, body.customer_name)).fetchone()
        conn.commit()
    row = dict(row)
    row["menu_name_th"] = menu_row["name_th"]
    row["price_total"] = Decimal(menu_row["price"]) * body.qty
    result = order_json(row)
    if ORDER_TRANSPORT == "rabbit":
        try:
            rabbit_publish({"order_id": row["id"], "menu_code": body.menu_code, "qty": body.qty, "ts": result["created_at"]})
        except Exception as exc:
            raise ApiError(503, "BROKER_UNAVAILABLE", "ส่งออเดอร์เข้าคิวไม่สำเร็จ") from exc
    if EVENTS_ENABLED:
        try:
            event_publish({"event": "ORDER_PLACED", "order_id": row["id"], "menu_code": body.menu_code, "qty": body.qty, "price_total": float(row["price_total"]), "ts": result["created_at"]})
        except Exception as exc:
            raise ApiError(503, "EVENT_PUBLISH_FAILED", "ส่งเหตุการณ์คำสั่งซื้อไม่สำเร็จ") from exc
    return result


@app.get("/api/queue")
def queue():
    with get_conn() as conn:
        rows = conn.execute(ORDER_SELECT + " WHERE o.status IN ('QUEUED','BREWING') ORDER BY o.created_at,o.id").fetchall()
    items = [order_json(dict(row)) for row in rows]
    return {"items": items, "count": len(items)}


@app.get("/api/orders/{order_id}")
def one_order(order_id: int):
    with get_conn() as conn:
        row = conn.execute(ORDER_SELECT + " WHERE o.id=%s", (order_id,)).fetchone()
    if row is None:
        raise ApiError(404, "ORDER_NOT_FOUND", f"ไม่พบออเดอร์หมายเลข {order_id}")
    return order_json(dict(row))


@app.get("/api/report/sales")
def report_sales():
    with get_conn() as conn:
        rows = conn.execute("SELECT s.menu_code,m.name_th,s.cups,s.revenue FROM sales_stats s JOIN menus m ON m.code=s.menu_code ORDER BY CASE s.menu_code WHEN 'latte' THEN 1 WHEN 'espresso' THEN 2 WHEN 'americano' THEN 3 WHEN 'mocha' THEN 4 WHEN 'matcha' THEN 5 ELSE 6 END").fetchall()
    items = [{"menu_code": r["menu_code"], "name_th": r["name_th"], "cups": r["cups"], "revenue": float(r["revenue"])} for r in rows]
    return {"items": items, "totals": {"cups": sum(x["cups"] for x in items), "revenue": round(sum(x["revenue"] for x in items), 2)}, "claim": "trend-level"}


@app.get("/api/version")
def version():
    tagline = "ลองข้อความใหม่กับลูกค้ากลุ่มเล็ก" if API_VERSION == "2" else "ชงใจทุกแก้ว"
    return {"version": API_VERSION, "tagline": tagline}
