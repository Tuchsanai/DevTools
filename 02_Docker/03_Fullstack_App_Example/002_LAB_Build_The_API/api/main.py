"""
CampusOps API — FastAPI + psycopg 3 (ไม่ใช้ ORM)

เขียนให้ "อ่านออกด้วยตาเปล่า" เป็นหลัก : SQL เห็นเต็ม ๆ กฎธุรกิจเป็น if/raise ธรรมดา
ทุก endpoint ตรงกับ docs/02_contract.md §4 · ทุกกฎธุรกิจอ้าง REQ ได้ในคอมเมนต์
"""

import os
import time
from contextlib import asynccontextmanager, contextmanager
from datetime import datetime
from typing import Any, Literal

import psycopg
from psycopg.rows import dict_row
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://opsuser:labpass@db:5432/campusops"
)

# SLA ตามความเร่งด่วน (วัน) — ใช้คำนวณงานค้างเกินกำหนดของ REQ-09
SLA_DAYS = {"HIGH": 1, "NORMAL": 3, "LOW": 7}

# ลำดับสถานะที่อนุญาต (REQ-02) — เดินหน้าทีละขั้นเท่านั้น ห้ามข้าม ห้ามถอยหลัง
ALLOWED_TRANSITIONS = {
    "NEW": ["ASSIGNED"],
    "ASSIGNED": ["IN_PROGRESS"],
    "IN_PROGRESS": ["DONE"],
    "DONE": [],
}


# ---------------------------------------------------------------------
# ข้อผิดพลาด — ทุกตัวต้องออกมาเป็น {"detail":..., "code":...} (contract §4)
# ---------------------------------------------------------------------
class ApiError(HTTPException):
    """HTTPException ที่พก code แบบ UPPER_SNAKE ติดตัวมาด้วย

    FastAPI มี HTTPException อยู่แล้วแต่มีแค่ detail ที่เป็นข้อความ
    เราจึงสืบทอดแล้วแปะ code เพิ่ม เพื่อให้ handler ข้างล่างประกอบ body ได้ครบรูป
    """

    def __init__(self, status_code: int, code: str, detail: str):
        super().__init__(status_code=status_code, detail=detail)
        self.code = code


# ---------------------------------------------------------------------
# การเชื่อมต่อฐานข้อมูล
# ---------------------------------------------------------------------
@contextmanager
def get_conn():
    """เปิด connection ใหม่ต่อ 1 คำขอ แล้วปิดเสมอ

    ทำไมไม่แชร์ connection ตัวเดียวทั้งแอป : connection เดียวใช้ข้าม request พร้อมกันไม่ได้
    และถ้ามันหลุด แอปจะพังทั้งตัว — เปิด/ปิดต่อคำขอเข้าใจง่ายกว่ามากสำหรับระบบขนาดนี้
    """
    conn = psycopg.connect(DATABASE_URL, row_factory=dict_row)
    try:
        yield conn
    finally:
        conn.close()


def wait_for_db(timeout_seconds: int = 60) -> None:
    """รอจน db พร้อม — ตอน compose up ขึ้นพร้อมกัน api มักติดต่อได้ก่อน postgres จะพร้อม
    ถ้าไม่ retry ตรงนี้ คอนเทนเนอร์ api จะตายทันทีแล้ววนรีสตาร์ตไม่จบ
    """
    deadline = time.time() + timeout_seconds
    while True:
        try:
            with psycopg.connect(DATABASE_URL, connect_timeout=3) as conn:
                conn.execute("SELECT 1")
            print("[api] เชื่อมต่อฐานข้อมูลได้แล้ว", flush=True)
            return
        except Exception as exc:  # noqa: BLE001 — ตอนบูตขอจับทุกกรณีแล้วลองใหม่
            if time.time() >= deadline:
                print(f"[api] รอฐานข้อมูลไม่สำเร็จ: {exc}", flush=True)
                return
            print("[api] ฐานข้อมูลยังไม่พร้อม รออีก 2 วินาที...", flush=True)
            time.sleep(2)


@asynccontextmanager
async def lifespan(app: FastAPI):
    wait_for_db()
    yield


API_DESCRIPTION = """
บริการเบื้องหลังสำหรับระบบดูแลครุภัณฑ์ภายในสถานศึกษา

**วิธีอ่านเอกสารนี้**

1. เลือก endpoint ซึ่งหมายถึง URL ที่เปิดให้โปรแกรมอื่นเรียกใช้
2. กด **Try it out** เพื่อเตรียมคำขอ และกด **Execute** เพื่อส่งคำขอจริง
3. อ่านรหัส HTTP และ Response body ในส่วน **Server response**

`REQ` ย่อมาจาก **Requirement** หรือข้อกำหนดที่ระบบต้องทำให้สำเร็จ
ข้อความ REQ ในแต่ละ endpoint จึงเชื่อมสิ่งที่ผู้ใช้ต้องการกับจุดที่ตรวจสอบได้จริง
"""

app = FastAPI(
    title="CampusOps API",
    version="1.0.0",
    description=API_DESCRIPTION,
    lifespan=lifespan,
    docs_url=None,
)


# ---------------------------------------------------------------------
# Swagger UI — คงพฤติกรรมมาตรฐานไว้ แต่เพิ่มลำดับชั้นทางสายตาสำหรับการเรียน
# ---------------------------------------------------------------------
@app.get("/docs", include_in_schema=False)
def custom_swagger_ui():
    """หน้าเอกสาร API ที่เพิ่มธีม CampusOps โดยไม่เปลี่ยน endpoint หรือ OpenAPI"""
    response = get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title="CampusOps API — Interactive Reference",
        swagger_ui_parameters={
            "docExpansion": "list",
            "displayRequestDuration": True,
            "filter": True,
            "persistAuthorization": False,
        },
    )
    theme = """
    <style>
      :root { color-scheme: light; --ink:#102a43; --navy:#0b2447; --cyan:#20c6d7; --paper:#f4f8fc; }
      html { scroll-behavior:smooth; }
      body { margin:0; background:
        radial-gradient(circle at 86% 5%, rgba(32,198,215,.18), transparent 26rem),
        linear-gradient(180deg, #eaf4fb 0, var(--paper) 25rem); }
      body::before { content:"CAMPUSOPS  /  API CONTROL PLANE"; display:block; box-sizing:border-box;
        padding:22px max(24px, calc((100vw - 1180px)/2)); color:#fff; font:700 13px/1.2 system-ui;
        letter-spacing:.16em; background:linear-gradient(100deg,var(--navy),#123d6a 65%,#0b7582);
        border-bottom:4px solid var(--cyan); box-shadow:0 10px 28px rgba(11,36,71,.18); }
      .swagger-ui { color:var(--ink); }
      .swagger-ui .topbar { display:none; }
      .swagger-ui .wrapper { max-width:1180px; }
      .swagger-ui .info { margin:34px 0 26px; padding:30px 34px; background:rgba(255,255,255,.94);
        border:1px solid #d8e7f2; border-radius:18px; box-shadow:0 16px 45px rgba(37,65,86,.10); }
      .swagger-ui .info .title { color:var(--navy); font-size:38px; letter-spacing:-.035em; }
      .swagger-ui .info .title small { top:-4px; }
      .swagger-ui .info .description { max-width:850px; color:#334e68; font-size:15px; line-height:1.7; }
      .swagger-ui .scheme-container { margin:0 0 24px; padding:18px 24px; background:#fff;
        border:1px solid #d8e7f2; border-radius:14px; box-shadow:none; }
      .swagger-ui .opblock-tag { color:var(--navy); border-bottom:0; font-size:20px; }
      .swagger-ui .opblock { overflow:hidden; margin:0 0 12px; border-width:1px; border-radius:12px;
        box-shadow:0 7px 20px rgba(37,65,86,.07); }
      .swagger-ui .opblock .opblock-summary { min-height:54px; padding:8px 12px; }
      .swagger-ui .opblock .opblock-summary-method { min-width:82px; border-radius:8px;
        text-shadow:none; font-weight:800; }
      .swagger-ui .btn { border-radius:8px; }
      .swagger-ui .btn.execute { border:0; background:linear-gradient(90deg,#1168a8,#0b8794); }
      .swagger-ui textarea, .swagger-ui input[type=text] { border-radius:9px; }
      .swagger-ui .responses-inner { background:#f8fbfd; }
      @media (max-width: 720px) {
        body::before { padding:18px 16px; }
        .swagger-ui .info { margin:18px 0; padding:22px 18px; border-radius:12px; }
        .swagger-ui .info .title { font-size:30px; }
      }
    </style>
    """
    html = response.body.decode("utf-8").replace("</head>", f"{theme}</head>")
    return HTMLResponse(content=html)


# ---------------------------------------------------------------------
# Exception handlers — ครอบให้ error ทุกตัวมีรูปเดียวกัน
# ---------------------------------------------------------------------
DEFAULT_CODE_BY_STATUS = {400: "BAD_REQUEST", 404: "NOT_FOUND", 409: "CONFLICT"}


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    code = getattr(exc, "code", None) or DEFAULT_CODE_BY_STATUS.get(
        exc.status_code, "ERROR"
    )
    return JSONResponse(
        status_code=exc.status_code, content={"detail": str(exc.detail), "code": code}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """ถ้าไม่เขียน handler ตัวนี้ FastAPI จะคืน detail เป็น array ของ pydantic
    ซึ่งผิดรูปที่ contract กำหนด (detail ต้องเป็นข้อความไทย + code)
    """
    first = exc.errors()[0] if exc.errors() else {}
    field = ".".join(str(p) for p in first.get("loc", []) if p != "body")
    return JSONResponse(
        status_code=422,
        content={
            "detail": f"ข้อมูลที่ส่งมาไม่ถูกต้อง: ฟิลด์ '{field or 'body'}' ({first.get('msg', '')})",
            "code": "VALIDATION_ERROR",
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"เกิดข้อผิดพลาดภายในระบบ: {exc}", "code": "INTERNAL_ERROR"},
    )


# ---------------------------------------------------------------------
# รูปของ request body (pydantic)
# ---------------------------------------------------------------------
class TicketCreate(BaseModel):
    asset_id: int
    title: str = Field(min_length=1)
    detail: str = ""
    priority: Literal["LOW", "NORMAL", "HIGH"]


class TicketStatusUpdate(BaseModel):
    status: Literal["NEW", "ASSIGNED", "IN_PROGRESS", "DONE"]
    assignee: str | None = None


class PartUse(BaseModel):
    part_id: int
    qty: int = Field(gt=0)  # เบิกต้องเป็นจำนวนบวกเสมอ ส่ง 0 หรือติดลบมาถือว่าผิดรูป


class TicketClose(BaseModel):
    parts: list[PartUse] = []  # ว่างได้ = ปิดงานโดยไม่ใช้อะไหล่ (REQ-05)


class LoanCreate(BaseModel):
    asset_id: int
    borrower: str = Field(min_length=1)


class StockMove(BaseModel):
    delta: int  # ลบ = เบิกออก, บวก = รับเข้า
    reason: str = ""


# ---------------------------------------------------------------------
# ตัวช่วยเล็ก ๆ
# ---------------------------------------------------------------------
def to_json(row: dict[str, Any] | None) -> dict[str, Any] | None:
    """แปลง datetime เป็นสตริง ISO เพื่อให้ JSON แสดงผลเหมือนกันทุกที่"""
    if row is None:
        return None
    out = {}
    for key, value in row.items():
        out[key] = value.isoformat() if isinstance(value, datetime) else value
    return out


def fetch_ticket(conn, ticket_id: int) -> dict[str, Any]:
    row = conn.execute(
        "SELECT id, asset_id, title, detail, priority, status, assignee,"
        " created_at, closed_at FROM tickets WHERE id = %s",
        (ticket_id,),
    ).fetchone()
    if row is None:
        raise ApiError(404, "NOT_FOUND", f"ไม่พบใบแจ้งซ่อมหมายเลข {ticket_id}")
    return row


# ---------------------------------------------------------------------
# /health — ต้องยิง query จริง ไม่ใช่ตอบ ok ลอย ๆ
# ---------------------------------------------------------------------
@app.get("/health")
def health():
    """ถ้าตอบ ok โดยไม่แตะ db เลย healthcheck จะเขียวทั้งที่ฐานข้อมูลล่ม
    → compose depends_on: service_healthy จะเชื่อถือไม่ได้ (NFR-1)
    """
    try:
        with get_conn() as conn:
            conn.execute("SELECT 1")
        return {"status": "ok", "db": "up"}
    except Exception as exc:  # noqa: BLE001
        return JSONResponse(
            status_code=503,
            content={"detail": f"ฐานข้อมูลไม่ตอบสนอง: {exc}", "code": "DB_DOWN"},
        )


# ---------------------------------------------------------------------
# ครุภัณฑ์
# ---------------------------------------------------------------------
@app.get("/api/assets")
def list_assets():
    """สถานะครุภัณฑ์เป็นค่าที่คำนวณ ไม่ใช่คอลัมน์ (contract §3)
    IN_REPAIR = มีใบซ่อมที่ยังไม่ DONE · ON_LOAN = มีสัญญายืมที่ยังไม่คืน
    """
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT a.id, a.code, a.name, a.location, a.created_at,
                   EXISTS (SELECT 1 FROM tickets t
                            WHERE t.asset_id = a.id AND t.status <> 'DONE') AS in_repair,
                   EXISTS (SELECT 1 FROM loans l
                            WHERE l.asset_id = a.id AND l.returned_at IS NULL) AS on_loan
            FROM assets a
            ORDER BY a.id
            """
        ).fetchall()

    result = []
    for row in rows:
        row = dict(row)
        in_repair = row.pop("in_repair")
        on_loan = row.pop("on_loan")
        # ลำดับความสำคัญตาม contract §3 : ซ่อมอยู่มาก่อนถูกยืม
        if in_repair:
            row["status"] = "IN_REPAIR"
        elif on_loan:
            row["status"] = "ON_LOAN"
        else:
            row["status"] = "AVAILABLE"
        result.append(to_json(row))
    return result


# ---------------------------------------------------------------------
# ใบแจ้งซ่อม
# ---------------------------------------------------------------------
@app.get("/api/tickets")
def list_tickets(status: str | None = None, assignee: str | None = None):
    """REQ-04 : กรองตามช่างผู้รับผิดชอบได้

    ต่อ WHERE ทีละชิ้นแล้วส่งค่าเป็นพารามิเตอร์ (%s) เสมอ
    ห้ามเอาค่าจาก query string ไปต่อสตริง SQL ตรง ๆ (SQL injection)
    """
    where = []
    params: list[Any] = []
    if status:
        where.append("status = %s")
        params.append(status)
    if assignee:
        where.append("assignee = %s")
        params.append(assignee)
    sql = (
        "SELECT id, asset_id, title, detail, priority, status, assignee,"
        " created_at, closed_at FROM tickets"
    )
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY id"

    with get_conn() as conn:
        rows = conn.execute(sql, params).fetchall()
    return [to_json(r) for r in rows]


@app.post("/api/tickets", status_code=201)
def create_ticket(payload: TicketCreate):
    """REQ-01 : สร้างใบแจ้งซ่อม → 201 และสถานะเริ่มต้นเป็น NEW เสมอ"""
    with get_conn() as conn:
        asset = conn.execute(
            "SELECT id FROM assets WHERE id = %s", (payload.asset_id,)
        ).fetchone()
        if asset is None:
            raise ApiError(404, "NOT_FOUND", f"ไม่พบครุภัณฑ์หมายเลข {payload.asset_id}")

        row = conn.execute(
            """
            INSERT INTO tickets (asset_id, title, detail, priority, status)
            VALUES (%s, %s, %s, %s, 'NEW')
            RETURNING id, asset_id, title, detail, priority, status, assignee,
                      created_at, closed_at
            """,
            (payload.asset_id, payload.title, payload.detail, payload.priority),
        ).fetchone()
        conn.commit()
    return to_json(row)


@app.patch("/api/tickets/{ticket_id}/status")
def update_ticket_status(ticket_id: int, payload: TicketStatusUpdate):
    """REQ-02 (ลำดับสถานะ) + REQ-03 (มอบหมายต้องมีชื่อช่าง)"""
    with get_conn() as conn:
        ticket = fetch_ticket(conn, ticket_id)

        # REQ-02 : ข้ามลำดับไม่ได้ เช่น NEW → DONE ตรง ๆ ต้องถูกปฏิเสธ และสถานะต้องไม่เปลี่ยน
        if payload.status not in ALLOWED_TRANSITIONS[ticket["status"]]:
            raise ApiError(
                409,
                "INVALID_TRANSITION",
                f"เปลี่ยนสถานะจาก {ticket['status']} ไป {payload.status} ไม่ได้",
            )

        # REQ-03 : จะมอบหมายงานต้องบอกว่ามอบให้ใคร ไม่งั้นหัวหน้าตอบไม่ได้ว่างานอยู่ที่ใคร
        if payload.status == "ASSIGNED" and not (payload.assignee or "").strip():
            raise ApiError(400, "ASSIGNEE_REQUIRED", "ต้องระบุชื่อช่างผู้รับผิดชอบ")

        # ปิดงานเมื่อไหร่ต้องประทับเวลาปิด ไม่งั้น REQ-09 คำนวณวันค้างไม่ได้
        closed_at_sql = "now()" if payload.status == "DONE" else "closed_at"
        new_assignee = payload.assignee if payload.assignee else ticket["assignee"]

        row = conn.execute(
            f"""
            UPDATE tickets
               SET status = %s, assignee = %s, closed_at = {closed_at_sql}
             WHERE id = %s
            RETURNING id, asset_id, title, detail, priority, status, assignee,
                      created_at, closed_at
            """,
            (payload.status, new_assignee, ticket_id),
        ).fetchone()
        conn.commit()
    return to_json(row)


@app.post("/api/tickets/{ticket_id}/close")
def close_ticket(ticket_id: int, payload: TicketClose):
    """REQ-05 : ปิดงานพร้อมบันทึกอะไหล่ที่ใช้ (ไม่ใช้อะไหล่ก็ปิดได้)
    REQ-06 : ถ้าอะไหล่ชิ้นใดไม่พอ ต้องยกเลิกทั้งรายการ ยอดคงเหลือห้ามเปลี่ยนแม้แต่ตัวเดียว

    ทั้งบล็อกนี้อยู่ใน transaction เดียว — psycopg เปิด transaction ให้อัตโนมัติ
    ถ้า raise ออกไปก่อน conn.commit() จะไม่มีอะไรถูกบันทึกเลย (rollback ตอนปิด connection)
    """
    with get_conn() as conn:
        ticket = fetch_ticket(conn, ticket_id)

        # ปิดงานได้จากขั้น IN_PROGRESS เท่านั้น ให้สอดคล้องกับลำดับสถานะของ REQ-02
        if ticket["status"] != "IN_PROGRESS":
            raise ApiError(
                409,
                "INVALID_TRANSITION",
                f"ปิดงานได้เฉพาะใบที่สถานะ IN_PROGRESS (ใบนี้อยู่สถานะ {ticket['status']})",
            )

        for item in payload.parts:
            # FOR UPDATE ล็อกแถวอะไหล่ไว้จนจบ transaction
            # กันช่างสองคนเบิกชิ้นสุดท้ายพร้อมกันแล้วยอดติดลบ
            part = conn.execute(
                "SELECT id, sku, name, qty_on_hand FROM parts WHERE id = %s FOR UPDATE",
                (item.part_id,),
            ).fetchone()
            if part is None:
                raise ApiError(404, "NOT_FOUND", f"ไม่พบอะไหล่หมายเลข {item.part_id}")

            if item.qty > part["qty_on_hand"]:
                # raise ตรงนี้ = ยังไม่ commit → อะไหล่ตัวก่อนหน้าที่หักไปแล้วถูกคืนกลับทั้งหมด
                raise ApiError(
                    409,
                    "INSUFFICIENT_STOCK",
                    f"อะไหล่ {part['sku']} คงเหลือ {part['qty_on_hand']} ไม่พอกับที่ขอเบิก {item.qty}",
                )

            conn.execute(
                "UPDATE parts SET qty_on_hand = qty_on_hand - %s WHERE id = %s",
                (item.qty, item.part_id),
            )
            # REQ-07 : ทุกการเคลื่อนไหวต้องถูกบันทึกไว้ย้อนดูได้
            conn.execute(
                "INSERT INTO stock_moves (part_id, ticket_id, delta, reason)"
                " VALUES (%s, %s, %s, %s)",
                (item.part_id, ticket_id, -item.qty, f"ใช้ในงานซ่อม #{ticket_id}"),
            )

        row = conn.execute(
            """
            UPDATE tickets SET status = 'DONE', closed_at = now()
             WHERE id = %s
            RETURNING id, asset_id, title, detail, priority, status, assignee,
                      created_at, closed_at
            """,
            (ticket_id,),
        ).fetchone()
        conn.commit()  # ทั้งการตัดสต็อกและการปิดงานถูกบันทึกพร้อมกันที่บรรทัดนี้บรรทัดเดียว
    return to_json(row)


# ---------------------------------------------------------------------
# ยืม-คืนครุภัณฑ์
# ---------------------------------------------------------------------
@app.get("/api/loans")
def list_loans():
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT l.id, l.asset_id, a.code AS asset_code, a.name AS asset_name,
                   l.borrower, l.borrowed_at, l.returned_at
            FROM loans l JOIN assets a ON a.id = l.asset_id
            ORDER BY l.returned_at IS NOT NULL, l.borrowed_at DESC
            """
        ).fetchall()
    return [to_json(r) for r in rows]


@app.post("/api/loans", status_code=201)
def create_loan(payload: LoanCreate):
    """REQ-10 : ของที่ยังไม่ถูกคืน ยืมซ้ำไม่ได้
    REQ-11 : ของที่มีใบซ่อมค้างอยู่ ยืมไม่ได้
    """
    with get_conn() as conn:
        asset = conn.execute(
            "SELECT id, code FROM assets WHERE id = %s", (payload.asset_id,)
        ).fetchone()
        if asset is None:
            raise ApiError(404, "NOT_FOUND", f"ไม่พบครุภัณฑ์หมายเลข {payload.asset_id}")

        # ตรวจ "ถูกยืมอยู่" ก่อน "ซ่อมอยู่" ให้ตรงลำดับตารางรหัสข้อผิดพลาดใน contract §4
        open_loan = conn.execute(
            "SELECT id, borrower FROM loans WHERE asset_id = %s AND returned_at IS NULL",
            (payload.asset_id,),
        ).fetchone()
        if open_loan is not None:
            raise ApiError(
                409,
                "ASSET_ON_LOAN",
                f"ครุภัณฑ์ {asset['code']} ถูกยืมอยู่โดย {open_loan['borrower']} ยังไม่ได้คืน",
            )

        open_ticket = conn.execute(
            "SELECT id FROM tickets WHERE asset_id = %s AND status <> 'DONE'",
            (payload.asset_id,),
        ).fetchone()
        if open_ticket is not None:
            raise ApiError(
                409,
                "ASSET_IN_REPAIR",
                f"ครุภัณฑ์ {asset['code']} มีใบแจ้งซ่อม #{open_ticket['id']} ที่ยังไม่ปิดงาน",
            )

        row = conn.execute(
            "INSERT INTO loans (asset_id, borrower) VALUES (%s, %s)"
            " RETURNING id, asset_id, borrower, borrowed_at, returned_at",
            (payload.asset_id, payload.borrower),
        ).fetchone()
        conn.commit()
    return to_json(row)


@app.post("/api/loans/{loan_id}/return")
def return_loan(loan_id: int):
    with get_conn() as conn:
        # เงื่อนไข returned_at IS NULL อยู่ใน UPDATE เลย → คืนซ้ำจะไม่มีแถวถูกแก้ แล้วได้ 404
        row = conn.execute(
            "UPDATE loans SET returned_at = now()"
            " WHERE id = %s AND returned_at IS NULL"
            " RETURNING id, asset_id, borrower, borrowed_at, returned_at",
            (loan_id,),
        ).fetchone()
        if row is None:
            raise ApiError(
                404, "NOT_FOUND", f"ไม่พบสัญญายืมหมายเลข {loan_id} ที่ยังไม่ได้คืน"
            )
        conn.commit()
    return to_json(row)


# ---------------------------------------------------------------------
# คลังอะไหล่
# ---------------------------------------------------------------------
@app.get("/api/parts")
def list_parts():
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, sku, name, qty_on_hand, reorder_point,"
            " (qty_on_hand < reorder_point) AS below_reorder"
            " FROM parts ORDER BY id"
        ).fetchall()
    return [to_json(r) for r in rows]


@app.get("/api/parts/{part_id}/moves")
def list_part_moves(part_id: int):
    """REQ-07 : ประวัติการเคลื่อนไหว เรียงเวลาใหม่ → เก่า"""
    with get_conn() as conn:
        part = conn.execute("SELECT id FROM parts WHERE id = %s", (part_id,)).fetchone()
        if part is None:
            raise ApiError(404, "NOT_FOUND", f"ไม่พบอะไหล่หมายเลข {part_id}")
        rows = conn.execute(
            "SELECT id, part_id, ticket_id, delta, reason, created_at"
            " FROM stock_moves WHERE part_id = %s"
            " ORDER BY created_at DESC, id DESC",  # id กันกรณีเวลาเท่ากันเป๊ะ
            (part_id,),
        ).fetchall()
    return [to_json(r) for r in rows]


@app.post("/api/parts/{part_id}/move")
def move_part(part_id: int, payload: StockMove):
    """รับเข้า (delta บวก) หรือเบิกออก (delta ลบ) — REQ-06 กันยอดติดลบ"""
    if payload.delta == 0:
        raise ApiError(422, "VALIDATION_ERROR", "delta ต้องไม่เป็นศูนย์")

    with get_conn() as conn:
        part = conn.execute(
            "SELECT id, sku, qty_on_hand FROM parts WHERE id = %s FOR UPDATE",
            (part_id,),
        ).fetchone()
        if part is None:
            raise ApiError(404, "NOT_FOUND", f"ไม่พบอะไหล่หมายเลข {part_id}")

        if part["qty_on_hand"] + payload.delta < 0:
            raise ApiError(
                409,
                "INSUFFICIENT_STOCK",
                f"อะไหล่ {part['sku']} คงเหลือ {part['qty_on_hand']} ไม่พอกับที่ขอเบิก {abs(payload.delta)}",
            )

        row = conn.execute(
            "UPDATE parts SET qty_on_hand = qty_on_hand + %s WHERE id = %s"
            " RETURNING id, sku, name, qty_on_hand, reorder_point,"
            " (qty_on_hand < reorder_point) AS below_reorder",
            (payload.delta, part_id),
        ).fetchone()
        conn.execute(
            "INSERT INTO stock_moves (part_id, ticket_id, delta, reason)"
            " VALUES (%s, NULL, %s, %s)",
            (part_id, payload.delta, payload.reason or "ปรับปรุงยอดคงเหลือ"),
        )
        conn.commit()
    return to_json(row)


# ---------------------------------------------------------------------
# หน้าสรุป
# ---------------------------------------------------------------------
@app.get("/api/dashboard")
def dashboard():
    """REQ-08 นับตามสถานะ · REQ-09 งานค้างเกินกำหนด · REQ-12 อะไหล่ใกล้หมด"""
    with get_conn() as conn:
        # เริ่มจาก 0 ทั้ง 4 สถานะ เพราะ GROUP BY จะไม่คืนแถวของสถานะที่ยังไม่มีใบเลย
        counts = {"NEW": 0, "ASSIGNED": 0, "IN_PROGRESS": 0, "DONE": 0}
        for row in conn.execute(
            "SELECT status, COUNT(*) AS n FROM tickets GROUP BY status"
        ).fetchall():
            counts[row["status"]] = row["n"]

        # วันที่ค้าง = ปัดลงเป็นจำนวนวันเต็ม · ค้างเกินกำหนดคือ "เกิน" SLA จริง ๆ (มากกว่า ไม่ใช่เท่ากับ)
        overdue_rows = conn.execute(
            """
            SELECT id, title, priority, assignee,
                   FLOOR(EXTRACT(EPOCH FROM (now() - created_at)) / 86400)::int AS days_open
            FROM tickets
            WHERE status <> 'DONE'
              AND now() - created_at > (CASE priority
                                          WHEN 'HIGH'   THEN interval '1 day'
                                          WHEN 'NORMAL' THEN interval '3 days'
                                          ELSE               interval '7 days'
                                        END)
            ORDER BY days_open DESC, id
            """
        ).fetchall()

        loans_active = conn.execute(
            "SELECT COUNT(*) AS n FROM loans WHERE returned_at IS NULL"
        ).fetchone()["n"]

        parts_low = conn.execute(
            "SELECT id, sku, name, qty_on_hand, reorder_point FROM parts"
            " WHERE qty_on_hand < reorder_point ORDER BY id"
        ).fetchall()

    overdue = [
        {
            "id": r["id"],
            "title": r["title"],
            "priority": r["priority"],
            "assignee": r["assignee"],
            "days_open": r["days_open"],
            "sla_days": SLA_DAYS[r["priority"]],
        }
        for r in overdue_rows
    ]
    return {
        "tickets": counts,
        "overdue": overdue,
        "loans_active": loans_active,
        "parts_low": [to_json(r) for r in parts_low],
    }
