#!/usr/bin/env python3
"""d23 — Plane logical architecture (v1.4.2 community compose).

Geometry note: the canvas redraws every bound arrow as a straight centre-to-centre segment
(clipped at the box borders), so boxes are placed so that those segments never cross
another box. Browser and plane-minio share the same centre x → vertical upload arrow.
The api box spans both app rows (262..400) and plane-mq is centred at x=907 so that the
api → mq arrow and the mq → worker arrow leave room for the one-line 'publish task' label
inside the app band (400..455). Labels: api/migrator arrows on baseline y=410, the
worker/beat <-> mq arrows on y=428 (staggered so neighbouring labels never read as one string).
"""
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from diagrams import *

NAME = "d23-plane-architecture"
WHITE = "#ffffff"

CX = [365, 527, 689, 851, 1013]      # 5 columns inside the app zone (w 148, gap 14)
W = 148
R1, R2 = 262, 340                    # row tops
LBL = 410                            # baseline of the api/migrator arrow labels (app band is 400..455)
LBL2 = 428                           # second baseline: worker/beat <-> mq labels (staggered, no run-on text)
IY = 480                             # infrastructure zone top
BY = IY + 45                         # infrastructure box top

els = [
    title("สถาปัตยกรรม Plane 13 container : Browser → proxy เดียว → บริการแอป → บริการพื้นฐาน"),

    # ---------------------------------------------------------------- browser + notes (left column)
    box("brw", 164, 88, 176, 70, "Browser\nlocalhost:8080", GREEN, GREENBG, 14),
    txt(40, 205, "อัปโหลดไฟล์แนบ (/uploads)\nเบราว์เซอร์ POST ไฟล์ตรง\nถึง MinIO ผ่าน proxy\napi แค่ออก presigned URL\n+ เก็บ metadata ใน DB", 13, TEAL),
    txt(40, 318, "api · worker · beat-worker\n· migrator = image เดียวกัน\n(plane-backend)\nคนละ entrypoint", 13, MUTED),

    # ---------------------------------------------------------------- application zone
    zone(350, 62, 830, 393, BLUE, SKYBG),
    txt(365, 68, "ชั้นแอปพลิเคชัน — 9 container (image makeplane/*)", 17, BLUE),
    box("px", 365, 98, 796, 48, "proxy (Caddy) · เปิด port เดียว :8080 → :80 · route ตาม prefix ของ URL", BLUE, BLUEBG, 14),

    box("web", CX[0], R1, W, 60, "web (app)\n/*  (ที่เหลือ)", GREEN, GREENBG, 13),
    box("adm", CX[1], R1, W, 60, "admin\n/god-mode", GREEN, GREENBG, 13),
    box("api", CX[2], R1, W, 138, "api (Django)\n/api  /auth\nport 8000\nส่ง task → mq", ORANGE, ORANGEBG, 13),
    box("spc", CX[3], R1, W, 60, "space (public)\n/spaces", GREEN, GREENBG, 13),
    box("live", CX[4], R1, W, 60, "live (WebSocket)\n/live", PURPLE, PURPLEBG, 13),

    box("mig", CX[0], R2, W, 60, "migrator\n(รันครั้งเดียว)", MUTED, GREYBG, 13, dashed=True),
    box("wk", CX[3], R2, W, 60, "worker\n(Celery)", PURPLE, PURPLEBG, 13),
    box("bt", CX[4], R2, W, 60, "beat-worker\n(Celery beat)", PURPLE, PURPLEBG, 13),

    # browser → proxy, proxy → routed services
    arrow("brw", "px", GREEN, x=340, y=123, w=25, h=0),
    arrow("px", "web", GREEN, x=700, y=146, w=-230, h=116),
    arrow("px", "adm", GREEN, x=730, y=146, w=-120, h=116),
    arrow("px", "api", ORANGE, x=763, y=146, w=0, h=116),
    arrow("px", "spc", GREEN, x=796, y=146, w=120, h=116),
    arrow("px", "live", PURPLE, x=826, y=146, w=230, h=116),

    # ---------------------------------------------------------------- infrastructure zone
    zone(30, IY, 1150, 160, TEAL, TEALBG),
    txt(45, IY + 8, "บริการพื้นฐาน", 18, TEAL),
    box("mn", 142, BY, 220, 70, "plane-minio\nMinIO · S3 (uploads)", TEAL, WHITE, 13),   # centre x 252 = Browser
    box("db", 376, BY, 168, 70, "plane-db\nPostgreSQL 15", TEAL, WHITE, 13),
    box("rd", 558, BY, 215, 70, "plane-redis\nValkey/Redis · cache", TEAL, WHITE, 13),
    box("mq", 787, BY, 240, 70, "plane-mq\nRabbitMQ · queue", TEAL, WHITE, 13),          # centre x 907
    txt(150, BY + 78, "image minio/minio", 12, MUTED),
    txt(384, BY + 78, "image postgres:15.7-alpine", 12, MUTED),
    txt(566, BY + 78, "image valkey/valkey:7.2", 12, MUTED),
    txt(795, BY + 78, "image rabbitmq:3.13-management", 12, MUTED),

    # api → data stores
    arrow("api", "db", ORANGE, x=689, y=380, w=-180, h=130),
    arrow("api", "rd", ORANGE, x=728, y=400, w=-50, h=110),
    arrow("api", "mq", ORANGE, x=809, y=400, w=76, h=110),
    txt(832, LBL, "publish task", 14, ORANGE),
    # migrator → db (one-shot)
    arrow("mig", "db", MUTED, dashed=True, x=442, y=400, w=11, h=110),
    txt(455, LBL, "migrate ครั้งเดียว", 14, MUTED),
    # queue → worker (consume), beat → queue (schedule)
    arrow("mq", "wk", TEAL, x=913, y=510, w=13, h=-110),
    txt(936, LBL2, "consume", 14, TEAL),
    arrow("bt", "mq", PURPLE, x=1058, y=400, w=-111, h=110),
    txt(1040, LBL2, "schedule", 14, PURPLE),
    # browser upload path (via proxy /uploads) → MinIO, vertical down the left column
    arrow("brw", "mn", TEAL, dashed=True, x=252, y=158, w=0, h=367),
]

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), NAME + ".json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(els, f, ensure_ascii=False)
print(out, len(els), "elements")
