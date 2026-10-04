#!/usr/bin/env python3
"""d25 — anatomy of docker-compose.yml + plane.env (13 services · 10 volumes · ${VAR} · boot order · proxy-only HTTP + HTTPS ports).

Box labels render at 20 px Excalifont on the canvas (label font size is not configurable through the add path), so
box text is kept short (label needs ~ measured_width x 1.25 + 10 px) and details go into txt() (Helvetica, size
honoured) — same convention as d03/d07. Free text is never below 13 px (the deck scales the diagram to ~0.65x)."""
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from diagrams import *

ENVBG = "#fff4e6"

els = [
    title("กายวิภาค docker-compose.yml + plane.env : 13 services · 10 volumes · proxy เท่านั้นที่ publish port (HTTP + HTTPS)"),

    # ---------------------------------------------------------------- left : plane.env
    zone(30, 75, 225, 537, ORANGE, ENVBG),
    txt(45, 84, "plane.env  (--env-file)", 18, ORANGE),
    box("e1", 40, 116, 205, 38, "URL / port", ORANGE, "#ffffff", 14),
    txt(46, 160, "APP_DOMAIN=localhost:8080\nLISTEN_HTTP_PORT=8080\nLISTEN_HTTPS_PORT=8443\nWEB_URL=http://localhost:8080", 13, INK),
    box("e2", 40, 232, 205, 38, "secrets", RED, "#ffffff", 14),
    txt(46, 276, "SECRET_KEY=<สุ่ม 64 hex>\nLIVE_SERVER_SECRET_KEY=…", 13, INK),
    box("e3", 40, 318, 205, 38, "data stores", TEAL, "#ffffff", 14),
    txt(46, 362, "DATABASE_URL · POSTGRES_*\nREDIS_URL · AMQP_URL\nAWS_S3_* · MINIO_ROOT_*", 13, INK),
    txt(45, 436, "APP_RELEASE=v1.4.2\n→ tag ของ image plane-*\n\nแก้แล้วต้อง pc up -d <svc>\n(pc restart ไม่พอ)\n\nsign-up · SMTP อยู่ใน DB\n→ ตั้งที่ god-mode ไม่ใช่ที่นี่", 13, MUTED),

    # ---------------------------------------------------------------- middle : docker-compose.yml
    zone(305, 75, 635, 537, BLUE, SKYBG, id="cz"),
    txt(315, 84, "docker-compose.yml  —  ${VAR} ถูกแทนด้วยค่าจาก plane.env", 18, BLUE),

    # app services
    zone(315, 115, 610, 275, GREEN, GREENBG, id="appz"),
    txt(327, 121, "app services  ·  image makeplane/plane-*:${APP_RELEASE}", 14, GREEN),
    box("px", 327, 150, 190, 64, "proxy (Caddy)\n8080/8443 → 80/443", BLUE, BLUEBG, 15),
    txt(327, 222, "ports: HTTP→80 · HTTPS→443\nproxy เท่านั้นที่ publish port (HTTP + HTTPS)", 13, BLUE),
    box("web", 532, 150, 86, 64, "web\n:3000", GREEN, "#ffffff", 15),
    box("adm", 626, 150, 86, 64, "admin\n:3000", GREEN, "#ffffff", 15),
    box("spc", 720, 150, 86, 64, "space\n:3000", GREEN, "#ffffff", 15),
    box("live", 814, 150, 86, 64, "live\n:3000", PURPLE, PURPLEBG, 15),
    txt(548, 222, "ไม่ publish port — เข้าถึงได้ผ่าน proxy ใน network plane_default", 13, MUTED),
    box("mig", 327, 262, 165, 64, "migrator\nExited (0)", MUTED, GREYBG, 15),
    box("api", 520, 262, 175, 64, "api (Django)\n:8000", PURPLE, PURPLEBG, 15),
    box("wk", 725, 248, 160, 44, "worker", PURPLE, PURPLEBG, 15),
    box("bt", 725, 300, 160, 44, "beat-worker", PURPLE, PURPLEBG, 15),
    arrow("mig", "api", MUTED, x=497, y=294, w=23, h=0),
    arrow("api", "wk", PURPLE, x=700, y=285, w=25, h=-15),
    arrow("api", "bt", PURPLE, x=700, y=303, w=25, h=19),
    txt(420, 338, "depends_on\n+ wait_for_db", 13, TEAL),
    txt(530, 350, "บูต : infra → migrator → api (wait_for_migrations) → worker / beat\n4 ตัวหลัง = image plane-backend เดียวกัน ต่างแค่ entrypoint", 13, MUTED),

    # infra + named volumes
    zone(315, 402, 610, 200, TEAL, TEALBG, id="infz"),
    txt(345, 408, "infra  ·  image ทางการ", 14, TEAL),
    box("db", 327, 434, 134, 56, "plane-db\npostgres 15", TEAL, "#ffffff", 14),
    box("rd", 467, 434, 134, 56, "plane-redis\nvalkey 7.2", TEAL, "#ffffff", 14),
    box("mq", 607, 434, 164, 56, "plane-mq\nrabbitmq", TEAL, "#ffffff", 14),
    box("mn", 777, 434, 134, 56, "plane-minio\nminio (S3)", TEAL, "#ffffff", 14),
    box("v1", 327, 520, 134, 40, "pgdata", MUTED, GREYBG, 14, dashed=True),
    box("v2", 467, 520, 134, 40, "redisdata", MUTED, GREYBG, 14, dashed=True),
    box("v3", 607, 520, 164, 40, "rabbitmq_data", MUTED, GREYBG, 14, dashed=True),
    box("v4", 777, 520, 134, 40, "uploads", MUTED, GREYBG, 14, dashed=True),
    arrow("v1", "db", MUTED, x=394, y=518, w=0, h=-26),
    arrow("v2", "rd", MUTED, x=534, y=518, w=0, h=-26),
    arrow("v3", "mq", MUTED, x=689, y=518, w=0, h=-26),
    arrow("v4", "mn", MUTED, x=844, y=518, w=0, h=-26),
    txt(327, 562, "volumes อีก 6 : logs_api · logs_worker · logs_beat-worker · logs_migrator · proxy_config · proxy_data\npc down เก็บ volume ไว้ (ข้อมูลอยู่)  ·  pc down -v ลบทั้งหมด", 13, MUTED),
    arrow("db", "mig", TEAL, x=338, y=432, w=0, h=-104),

    # env → compose (${VAR})
    arrow("e1", "px", ORANGE, x=247, y=135, w=78, h=35),
    txt(263, 110, "${VAR}", 13, ORANGE),
    arrow("e2", "appz", RED, x=247, y=251, w=68, h=10),
    arrow("e3", "infz", TEAL, x=247, y=337, w=68, h=100),

    # ---------------------------------------------------------------- right : pc up -d
    zone(955, 75, 225, 537, MUTED, GREYBG),
    txt(968, 84, "pc up -d  →  runtime", 18, MUTED),
    box("cmd", 967, 118, 200, 64, "pc up -d\n(compose -p plane)", ORANGE, ORANGEBG, 15),
    arrow("cmd", "ctn", MUTED, x=1067, y=184, w=0, h=28),
    box("ctn", 967, 212, 200, 116, "13 containers\nplane-<service>-1\n12 Up + migrator\nExited (0)", INK, "#ffffff", 14),
    arrow("ctn", "pub", MUTED, x=1067, y=330, w=0, h=34),
    box("pub", 967, 366, 200, 90, "proxy เท่านั้นที่\npublish port\n(HTTP + HTTPS)", BLUE, BLUEBG, 14),
    txt(967, 470, "8080→80 · 8443→443\npc ps โชว์ (healthy) เฉพาะ\nweb · admin · space\n(image อื่นไม่ประกาศ healthcheck)", 13, MUTED),
    txt(967, 548, "ห้าม pc down -v ก่อนจบ LAB 9\n(ลบ volume = ข้อมูลหาย)", 13, RED),
]

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "d25-compose-architecture.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(els, f, ensure_ascii=False)
print(out, len(els), "elements")
