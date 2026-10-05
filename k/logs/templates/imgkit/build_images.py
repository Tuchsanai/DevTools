#!/usr/bin/env python3
"""Storyboard ภาพบท 012 Ingress → images.json + imagegen-prompts.md (รัน: python3 build_images.py)

ค่าที่ได้จาก pre-check (พอร์ต, ข้อความ error, ผล err=0 ฯลฯ) อยู่ใน labels (Text verbatim) ที่เดียว
Constraints อ้างป้ายด้วยหมายเลข "label N" — imgcommon ตรวจให้ว่าไม่มีค่าเลขพอร์ต/ผลทดสอบซ้ำใน Scene/Constraints
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from imgcommon import configure, t, l, main

configure("012")

# ================================================================ Theory
S1 = "1. บทนำ: ร้านมีหลายประตู ลูกค้าจำไม่ไหว"
t("opening-front-gate", S1,
  "เปิดบทที่ 12: ต่อจากบท 011 ร้านน้องส้มมีทั้งประตู HTTP และ HTTPS คนละเลข น้องส้มจึงสร้างประตูหน้าท่าเรือบานเดียวที่มีป้ายบอกทาง",
  """The harbor dock seen from the sea road; a grand front gate building with one big direction signboard on a stand
  in front of it; behind the gate three indoor lighthouse counters. Nong Som cuts a ribbon at the gate.""",
  ["บทที่ 12", "Ingress", "ประตูหน้าท่าเรือบานเดียว"],
  "label 1 as a title banner; label 2 on the gate building; label 3 as a subtitle")
t("recap-many-doors", S1,
  "ทวนบท 010–011: ร้านเปิด NodePort 30080 (HTTP) และ 30082 (HTTPS ผ่าน nginx) ลูกค้าต้องจำเลขประตูเอง ถ้าเพิ่มหน้าแอดมินก็ต้องเพิ่มเลขอีก",
  """Two separate numbered gangway doors on the side of a ship, a confused customer silhouette holding a note with
  numbers; Nong Som scratches her head holding a key ring with many keys.""",
  ["NodePort 30080", "NodePort 30082", "ลูกค้าต้องจำเลขประตู", "เพิ่มบริการ = เพิ่มประตู"],
  "label 1 on the left gangway door; label 2 on the right gangway door; label 3 on the customer's note; label 4 as a title banner")
t("metaphor-legend", S1,
  "อุปมาใหม่ของบท: Ingress = ประตูหน้า + ป้ายบอกทาง, Ingress controller = พนักงานต้อนรับ (หุ่นยนต์), IngressClass = ยูนิฟอร์ม, TLS = ประตูกระจกนิรภัยมีตราประทับ, defaultBackend = โต๊ะของหาย",
  """A legend board with five tiles: the gate with its signboard; the receptionist robot with a lantern; a uniform
  vest emblem matching a tag; a glass security door with a stamped seal plate; a lost-and-found desk.""",
  ["Ingress = ประตูหน้า + ป้ายบอกทาง", "Ingress controller = พนักงานต้อนรับ", "IngressClass = ยูนิฟอร์ม",
   "TLS = ประตูกระจกนิรภัย", "defaultBackend = โต๊ะของหาย"],
  "each tile carries exactly one label in order label 1 to label 5")
t("story-goal-names", S1,
  "เป้าหมายของบท: ลูกค้าเข้าร้านด้วยชื่อ shop.localhost และแอดมินใช้ admin.localhost ผ่านประตูเดียว แทนการจำเลขพอร์ต",
  """Two customer silhouettes hold visit tickets with shop names; both walk through the same front gate and the
  receptionist robot points them to two different counters. Nong Som holds a plan board.""",
  ["shop.localhost", "admin.localhost", "ใช้ชื่อแทนเลขพอร์ต", "ป้ายเดียวพาไปถูกเคาน์เตอร์"],
  "label 1 and label 2 on the two tickets; label 3 on Nong Som's plan board; label 4 as a title banner")

S2 = "2. ทำไมต้องมี Ingress"
t("nodeport-sprawl", S2,
  "NodePort: ทุก Service ที่อยากให้คนนอกเข้าต้องมีเลขประตูของตัวเอง (ช่วง 30000–32767) และเปิดบนทุก Node — ร้านยิ่งมาก ยิ่งสับสน",
  """Three ships each with a row of many numbered gangway doors; tangled rope lines from customers to the doors. Nong
  Som looks overwhelmed.""",
  ["NodePort ต่อ Service", "ช่วง 30000–32767", "เปิดบนทุกเรือ", "ยิ่งร้านมาก ยิ่งสับสน"],
  "label 1 on a door row; label 2 on a small range plate; label 3 on the ships; label 4 as a title banner")
t("loadbalancer-per-service", S2,
  "LoadBalancer: ได้ IP ภายนอกต่อ Service ในคลาวด์ แต่จ่ายเงินทุกตัว และบน kind (ไม่มี cloud controller) EXTERNAL-IP จะค้าง <pending>",
  """A row of separate paid toll lighthouses on the sea road, one per counter, each with a coin box; at the end one
  lighthouse with a dim lamp and an hourglass. Nong Som counts coins.""",
  ["LoadBalancer ต่อ Service", "จ่ายเงินทุกตัว", "EXTERNAL-IP <pending>", "kind ไม่มีให้ในตัว"],
  "label 1 as a title banner; label 2 on a coin box; label 3 on the dim lighthouse; label 4 on a note next to it",
  nt=True)
t("one-gate-many-counters", S2,
  "Ingress: เปิดประตูออกนอกบานเดียว (Service ของ controller) แล้วกฎ host/path ภายในพาไปหลาย Service ที่เป็น ClusterIP",
  """A single front gate on the dock with one gangway; inside the hall the signboard splits into three hallways, each
  ending at an indoor lighthouse counter. Nong Som stands at the gate.""",
  ["Ingress", "ทางเข้าเดียว", "หลายเคาน์เตอร์ข้างใน", "ClusterIP"],
  "label 1 on the gate; label 2 on the gangway; label 3 above the hallways; label 4 on one indoor counter")

S3 = "3. L4 กับ L7"
t("l4-vs-l7", S3,
  "Service ทำงานชั้น L4 (ดูแค่ IP:port แล้วส่งต่อ) ส่วน Ingress controller ทำงานชั้น L7 อ่านคำขอ HTTP (Host, path, header) ก่อนเลือกปลายทาง",
  """Left: a lighthouse counter clerk-robot looks only at the address on a closed parcel. Right: the receptionist
  robot opens a visit ticket and reads its lines with a magnifier. Nong Som compares them.""",
  ["Service = L4", "ดูแค่ IP:port", "Ingress = L7", "อ่าน Host / path / header", "เลือกปลายทางจากเนื้อหา"],
  "label 1 and label 2 on the left half; label 3 and label 4 on the right half; label 5 as a title banner")
t("http-request-anatomy", S3,
  "คำขอ HTTP ที่ Ingress ใช้ตัดสิน: บรรทัด GET /api/stats และ header Host — browser/curl ใส่เลขพอร์ตต่อท้าย (shop.localhost:30080) ซึ่ง controller ตัดพอร์ตออกก่อนเทียบกฎ",
  """A large visit ticket held up by Nong Som; two highlighted lines on it; an arrow from the ticket to the signboard.""",
  ["GET /api/stats", "Host: shop.localhost:30080", "ตั๋วบอกชื่อร้านและทางเดิน", "เทียบชื่อโดยไม่สนพอร์ต"],
  "label 1 and label 2 as the two highlighted ticket lines; label 3 as a title banner; label 4 on the arrow",
  nt=True)

S4 = "4. Ingress (ป้าย) กับ Ingress controller (พนักงาน)"
t("sign-without-receptionist", S4,
  "Ingress เป็นแค่ object ที่บอกกฎ ถ้าไม่มี Ingress controller ในคลัสเตอร์ก็ไม่มีใครอ่านป้าย ลูกค้าไม่ถูกพาไปไหน",
  """The front gate signboard standing alone in an empty hall, no robot present, a few customers wandering lost.
  Nong Som points at the empty receptionist spot.""",
  ["Ingress = แค่ป้าย", "ยังไม่มีพนักงาน", "ไม่มีใครพาลูกค้าไป"],
  "label 1 on the signboard; label 2 on the empty receptionist spot; label 3 as a title banner")
t("controller-watches-api", S4,
  "Ingress controller เฝ้าดู (watch) Ingress, Service, EndpointSlice และ Secret จาก API server แล้วปรับเส้นทางของตัวเองทันทีโดยไม่ต้อง restart",
  """The receptionist robot holds a walkie-talkie connected to the harbor control tower; papers float from the tower
  to the robot; the robot redraws lines on its route map.""",
  ["Ingress controller", "watch Ingress / Service / EndpointSlice", "อัปเดตเส้นทางเอง", "ไม่ต้อง restart"],
  "label 1 on the robot's vest; label 2 on the radio stream; label 3 on the route map; label 4 as a small green note")
t("controller-is-a-pod", S4,
  "controller ก็คือแอปหนึ่งตัวในคลัสเตอร์: namespace traefik มี Deployment traefik + Service NodePort เป็นประตูออกนอกบานเดียว",
  """A painted zone on the dock with a booth Pod box containing the receptionist robot, a store-manager robot next to
  it, and one gangway door on the zone edge. Nong Som peeks inside.""",
  ["namespace: traefik", "Deployment traefik", "Service NodePort", "พนักงานต้อนรับก็เป็น Pod"],
  "label 1 on the zone sign; label 2 on the manager robot; label 3 on the gangway door; label 4 as a title banner")
t("controller-choices", S4,
  "มี Ingress controller หลายบริษัท ใช้ป้าย Ingress มาตรฐานเดียวกัน (networking.k8s.io/v1) แต่ความสามารถเสริมต่างกัน",
  """A wardrobe rack with four receptionist uniform vests of different colors, each with a plain emblem; one
  signboard in front fits all. Nong Som chooses a vest.""",
  ["Traefik", "HAProxy Ingress", "Contour", "NGINX Gateway Fabric", "ป้ายมาตรฐานเดียวกัน"],
  "label 1 to label 4 on the four vest name tags; label 5 on the signboard; plain emblems only, no logos")

S5 = "5. ingress-nginx เกษียณแล้ว และเหตุผลที่เลือก Traefik"
t("ingress-nginx-retired", S5,
  "ingress-nginx (kubernetes/ingress-nginx) หยุดดูแล 24 มี.ค. 2026 repo เป็น archive ไม่มี release/แพตช์ความปลอดภัยอีก ของที่ติดตั้งไว้ยังรันได้แต่เสี่ยง — ทางการแนะนำย้ายไป Gateway API หรือ controller อื่น",
  """An old receptionist robot sitting on a bench with a retirement sash, its toolbox closed with a tag; a small
  warning sign next to the bench; Nong Som waves goodbye respectfully.""",
  ["ingress-nginx", "หยุดดูแล 24 มี.ค. 2026", "ไม่มีแพตช์ความปลอดภัย", "ยังรันได้ แต่เสี่ยง"],
  "label 1 on the sash; label 2 on the toolbox tag; label 3 on the warning sign; label 4 as a title banner")
t("why-traefik", S5,
  "บทนี้ใช้ Traefik v3.7.13: ยังดูแลอยู่, image ทางการดึงได้ตรง, ติดตั้งด้วย YAML pin เวอร์ชัน (ไม่ต้องใช้ Helm), รองรับทั้ง Ingress และ Gateway API",
  """A checklist clipboard with four ticked rows; a new receptionist robot in a teal vest stands ready. Nong Som holds
  the clipboard.""",
  ["Traefik v3.7.13", "ยังดูแลอยู่", "ติดตั้งด้วย YAML pin เวอร์ชัน", "ใช้ได้ทั้ง Ingress และ Gateway API", "เลือกใช้ใน LAB นี้"],
  "label 1 on the robot's vest tag; label 2 to label 4 as the three ticked rows; label 5 as a title banner")

S6 = "6. IngressClass และ default class"
t("ingressclass-uniform", S6,
  "IngressClass บอกว่า controller ไหนรับผิดชอบ: IngressClass traefik มี controller: traefik.io/ingress-controller และ Ingress อ้างด้วย ingressClassName: traefik",
  """Close-up: the colored emblem on the receptionist robot's vest and the matching colored tag on the signboard,
  connected by a dotted line. Nong Som compares the two.""",
  ["IngressClass: traefik", "controller: traefik.io/ingress-controller", "ingressClassName: traefik", "ยูนิฟอร์มตรงกัน = รับผิดชอบป้ายนี้"],
  "label 1 and label 2 on the vest card; label 3 on the signboard tag; label 4 as a title banner")
t("default-class", S6,
  "annotation ingressclass.kubernetes.io/is-default-class: \"true\" ทำให้ Ingress ที่ไม่ระบุ class ถูกเติม ingressClassName: traefik ตอนสร้าง (kubectl get ingressclass แสดง traefik (default))",
  """A signboard arrives without a tag; a small stamping machine at the gate stamps a gold-star tag on it. Nong Som
  watches.""",
  ["is-default-class: \"true\"", "ไม่ระบุ class", "ระบบเติม ingressClassName ให้", "traefik (default)"],
  "label 1 on the stamping machine; label 2 on the untagged signboard; label 3 as a title banner; label 4 on the gold-star tag",
  nt=True)
t("wrong-class", S6,
  "ระบุ class ผิด (เช่น ingressClassName: nginx ที่ไม่มีอยู่) → ไม่มี controller ไหนรับ, ADDRESS ว่าง, กฎไม่ทำงาน",
  """A signboard with a tag color that matches no robot; the receptionist robot walks past it. Nong Som frowns at an
  empty status plate.""",
  ["ingressClassName: nginx", "ไม่มีพนักงานบริษัทนี้", "ADDRESS ว่าง", "ป้ายถูกเมิน"],
  "label 1 on the tag; label 2 near the robot; label 3 on the empty status plate; label 4 as a title banner",
  nt=True)

S7 = "7. โครงสร้าง YAML ของ Ingress และ backend"
t("ingress-yaml-anatomy", S7,
  "Ingress (networking.k8s.io/v1): spec.rules[] → host → http.paths[] (path + pathType) → backend.service (name + port) อ่านจากบนลงล่างเหมือนป้ายบอกทาง",
  """A tall blueprint card shaped like the signboard, with five indented sections connected by arrows. Nong Som traces
  the arrows with a pointer.""",
  ["apiVersion: networking.k8s.io/v1", "spec.rules", "host", "http.paths", "backend.service", "อ่านจากบนลงล่าง"],
  "label 1 at the top of the card; label 2 to label 5 on the four nested sections; label 6 as a title banner")
t("backend-port-name-number", S7,
  "backend.service.port ใช้ number (80) หรือ name (http) ของ Service ไม่ใช่ containerPort — ใส่ผิดจะเห็น ERR service port not found ใน log ของ controller",
  """A signboard row pointing to a lighthouse counter that has a port plate with a number and a name; a red card
  pinned to a wrong row. Nong Som checks with a clipboard.""",
  ["port.number: 80", "port.name: http", "พอร์ตของ Service", "ไม่ใช่ containerPort", "service port not found"],
  "label 1 and label 2 on the counter port plate; label 3 as a title banner; label 4 as a small note; label 5 on the red card",
  nt=True)
t("clusterip-enough", S7,
  "เมื่อมี Ingress แล้ว Service ของแอปเป็นแค่ ClusterIP (เคาน์เตอร์ในอาคาร) ประตูออกนอกเหลือบานเดียวคือ Service traefik",
  """Inside the hall indoor lighthouse counters with no gangway doors; only the gate has one gangway door outward.
  Nong Som closes an old gangway door on a counter.""",
  ["type: ClusterIP", "ไม่ต้องมี NodePort แล้ว", "ประตูออกนอกบานเดียว", "Service traefik"],
  "label 1 on an indoor counter; label 2 on the closed old door; label 3 as a title banner; label 4 on the gate gangway door")

S8 = "8. Host-based: หลายชื่อบนประตูเดียว"
t("name-based-vhost", S8,
  "name-based virtual hosting: ลูกค้าสองคนเข้าประตูเดียวกัน แต่ Host ต่างกัน (shop.localhost / admin.localhost) จึงถูกพาไปคนละ Service",
  """Two customer silhouettes with different tickets enter the same gate; the receptionist robot sends one to the
  shop counter and one to the back-office counter.""",
  ["shop.localhost", "admin.localhost", "ประตูเดียวกัน", "ไปคนละเคาน์เตอร์"],
  "label 1 and label 2 on the two tickets; label 3 on the gate; label 4 as a title banner")
t("localhost-subdomain", S8,
  "ชื่อ *.localhost ถูก browser และ curl แปลงเป็น 127.0.0.1 เอง (ทดสอบแล้วใน Chromium 153 และ curl 8.5) จึงไม่ต้องแก้ไฟล์ hosts",
  """A browser window shaped like a ship's porthole showing a name, with an arrow looping back to the student's own
  laptop at home; a closed notebook labelled hosts file stays on the shelf. Nong Som gives a thumbs up.""",
  ["*.localhost → 127.0.0.1", "Chrome / Edge / curl", "ไม่ต้องแก้ไฟล์ hosts", "ชื่อวนกลับเครื่องตัวเอง"],
  "label 1 on the loop arrow; label 2 on the porthole frame; label 3 on the closed notebook; label 4 as a title banner",
  nt=True)
t("host-fallback", S8,
  "ทางสำรองเมื่อโปรแกรมแปลง *.localhost ไม่ได้ (เช่น getent/wget/python): curl -H 'Host: ...' หรือ curl --resolve หรือแก้ไฟล์ hosts",
  """Three small paths to the same gate: a hand-written ticket, a pre-printed address card, and a notebook page;
  Nong Som recommends them in order.""",
  ["curl -H 'Host: shop.localhost'", "curl --resolve", "แก้ไฟล์ hosts", "บางโปรแกรมหาชื่อไม่เจอ"],
  "label 1 to label 3 on the three paths; label 4 as a title banner",
  nt=True)

S9 = "9. Path-based fan-out"
t("path-fanout", S9,
  "fan-out: ชื่อเดียว shop.localhost แต่แยก path / → menu, /api → api, /admin → admin (Service คนละตัว)",
  """Inside the hall three hallway doors under one shop name; each hallway leads to its own lighthouse counter.
  Nong Som directs traffic.""",
  ["/", "/api", "/admin", "menu", "api", "admin", "แยกทางตาม path"],
  "label 1 to label 3 on the three hallway door plates; label 4 to label 6 on the matching counters; label 7 as a title banner")
t("path-precedence", S9,
  "หลายกฎตรงพร้อมกัน path ที่ยาวกว่าชนะ: /api/stats ไป api, /order ไป menu (ตกที่ /)",
  """Two customers: one walks into a narrow long hallway, one into the wide main hallway; a measuring tape between
  door plates. Nong Som holds the tape.""",
  ["/api/stats → api", "/order → menu", "path ยาวกว่าชนะ"],
  "label 1 on the narrow hallway; label 2 on the wide hallway; label 3 as a title banner",
  nt=True)

S10 = "10. pathType: Prefix, Exact, ImplementationSpecific"
t("pathtype-three", S10,
  "pathType มี 3 แบบ: Prefix (ตรงทีละท่อนที่คั่นด้วย /), Exact (ตรงตัวเท่านั้น), ImplementationSpecific (แล้วแต่ controller)",
  """Three hallway door styles side by side: an arch with segmented stepping stones, a door with an exact-shape key
  hole, and a door with a question-mark plate. Nong Som explains.""",
  ["Prefix", "Exact", "ImplementationSpecific", "ตรงทีละท่อน /", "ตรงตัวเท่านั้น", "แล้วแต่ controller"],
  "label 1 to label 3 on the three door tops; label 4 to label 6 under the matching doors in the same order")
t("prefix-element-match", S10,
  "Prefix /api ตามมาตรฐาน: ตรง /api, /api/, /api/x แต่ไม่ตรง /apix และ /API (ตัวพิมพ์ใหญ่ต่างกัน) — ยืนยันกับ Traefik ที่เปิด strictPrefixMatching",
  """A hallway door with a stepping-stone path; customers with tickets: two walk through with green ticks, two are
  stopped with red crosses. Nong Som checks tickets.""",
  ["/api ✔", "/api/x ✔", "/apix ✘", "/API ✘", "Prefix ตัดตาม /"],
  "label 1 to label 4 on the four tickets; label 5 as a title banner",
  nt=True)
t("trailing-slash-exact", S10,
  "ระวัง / ท้าย: Prefix /docs/ ก็รับ /docs (ไม่สน / ท้าย) แต่ Exact /menu ไม่รับ /menu/",
  """Two door plates: one generous door accepting a ticket without the final slash; one strict door rejecting a ticket
  with an extra slash. Nong Som points at the tiny slash.""",
  ["Prefix /docs/ → /docs ✔", "Exact /menu → /menu/ ✘", "ระวังเครื่องหมาย / ท้าย"],
  "label 1 on the generous door; label 2 on the strict door; label 3 as a title banner",
  nt=True)
t("strict-prefix-traefik", S10,
  "ข้อควรรู้เฉพาะ Traefik: ค่าเริ่มต้นเทียบ Prefix แบบตัวอักษร (/api ตรง /apix ด้วย) ต้องเปิด --providers.kubernetesingress.strictPrefixMatching=true จึงตรงมาตรฐาน",
  """A switch panel on the receptionist robot's back with one lever; when off, a ticket with an extra letter slips
  through; when on, it is stopped. Nong Som flips the lever.""",
  ["ค่าเริ่มต้น: /apix ก็ผ่าน", "strictPrefixMatching=true", "ตรงตามมาตรฐาน", "เฉพาะ Traefik"],
  "label 1 on the off side; label 2 on the lever; label 3 on the on side; label 4 as a small vest badge",
  nt=True)

S11 = "11. defaultBackend, 404, 503 และ 502"
t("default-backend-lost-found", S11,
  "ไม่ตรงกฎใดเลย → controller ตอบ 404 page not found; ถ้าตั้ง spec.defaultBackend จะส่งไปโต๊ะของหายแทน (ใน Traefik เป็น catch-all ของทั้งคลัสเตอร์)",
  """A customer with an unknown ticket meets an empty wrong-door with a small sign; next to the gate a lost-and-found
  desk with a bell. Nong Som guides the customer to the desk.""",
  ["404 page not found", "ไม่ตรงกฎใดเลย", "defaultBackend", "โต๊ะของหาย"],
  "label 1 on the wrong-door sign; label 2 on the customer's ticket; label 3 and label 4 on the desk",
  nt=True)
t("status-404-503-502", S11,
  "อ่านรหัสให้ออก: 404 = ไม่มีกฎตรง, 503 = มีกฎแต่ไม่มี Pod พร้อม (no available server), 502 = Pod ปิดกลางคันระหว่างตอบ",
  """Three doors in a row: an empty wrong-door, a counter with all booths showing red lamps, a booth closing its
  shutter mid-sale. Nong Som holds a code card.""",
  ["404 = ไม่มีกฎตรง", "503 = ไม่มีบูธพร้อม", "502 = บูธปิดกลางคัน", "อ่านรหัสให้ออก"],
  "label 1 to label 3 above the three doors in order; label 4 as a title banner",
  nt=True)

S12 = "12. TLS ที่ Ingress"
t("tls-termination", S12,
  "TLS termination: spec.tls ชี้ Secret som-tls (kubernetes.io/tls จากบท 011) controller ถอดรหัสที่ประตู แล้วส่ง HTTP ธรรมดาเข้าเคาน์เตอร์ พร้อม X-Forwarded-Proto: https",
  """The glass security door with a stamped seal plate; the receptionist robot takes a sealed envelope from the zone
  key box; behind the door plain open hallways to the counters.""",
  ["spec.tls", "secretName: som-tls", "kubernetes.io/tls", "ถอดรหัสที่ประตู", "ข้างในเป็น HTTP"],
  "label 1 on the glass door; label 2 and label 3 on the envelope; label 4 as a title banner; label 5 on the inner hallway")
t("sni-cert-choice", S12,
  "SNI: ลูกค้าบอกชื่อก่อนเปิดประตู controller เลือกใบรับรองตามชื่อ — ชื่อที่ไม่มีใน spec.tls ได้ใบสำรอง TRAEFIK DEFAULT CERT",
  """A customer speaks into an intercom at the glass door; the door shows a matching seal plate; another customer
  with an unknown name gets a plain grey seal plate. Nong Som listens.""",
  ["SNI: shop.localhost", "ตราของ shop.localhost", "ชื่อไม่ตรง → TRAEFIK DEFAULT CERT", "เลือกใบรับรองจากชื่อ"],
  "label 1 on the intercom bubble; label 2 on the matching seal plate; label 3 on the grey plate; label 4 as a title banner",
  nt=True)
t("san-multi-name", S12,
  "ใบรับรองใบเดียวใส่ได้หลายชื่อใน subjectAltName (shop.localhost, admin.localhost, localhost) — เรียกด้วย 127.0.0.1 จะได้ curl: (60) เพราะไม่อยู่ในใบ",
  """One large certificate seal plate listing three names in rows; a customer holding a number-only ticket is
  stopped. Nong Som polishes the plate.""",
  ["DNS:shop.localhost", "DNS:admin.localhost", "DNS:localhost", "ใบเดียวหลายชื่อ", "127.0.0.1 ไม่อยู่ในใบ"],
  "label 1 to label 3 as the three rows; label 4 as a title banner; label 5 on the stopped ticket",
  nt=True)

S13 = "13. Redirect HTTP → HTTPS"
t("redirect-301", S13,
  "ลูกค้าที่เข้าประตูไม้ (HTTP) ถูกส่งต่อด้วย 301 ไปประตูกระจก (HTTPS) — Location ต้องเป็นพอร์ตที่ลูกค้าเห็นจริง",
  """A customer at the plain wooden door; an arrow stand turns them toward the glass security door. Nong Som holds
  the arrow stand.""",
  ["http://shop.localhost:30080", "301 Moved Permanently", "Location: https://shop.localhost:30081/", "พาไปประตูกระจกเสมอ"],
  "label 1 on the wooden door; label 2 on the arrow stand; label 3 on the glass door; label 4 as a title banner",
  nt=True)
t("redirect-port-gotcha", S13,
  "ข้อควรระวังบน kind: entrypoint websecure ฟังที่ :8443 ภายใน แต่ลูกค้าเห็น NodePort 30081 จึงต้องกำหนด port: \"30081\" ใน Middleware redirectScheme",
  """Two door numbers: a small inner door number plate inside the hall and the outer gangway number on the dock; Nong
  Som crosses out the inner one on a redirect card and writes the outer one.""",
  ["websecure :8443 (ภายใน)", "NodePort 30081 (ลูกค้าเห็น)", "port: \"30081\"", "บอกพอร์ตที่ลูกค้าเห็น"],
  "label 1 on the inner plate; label 2 on the outer gangway; label 3 on the redirect card; label 4 as a title banner",
  nt=True)

S14 = "14. annotation และ Middleware (เฉพาะ controller)"
t("standard-vs-specific", S14,
  "แยกให้ชัด: rules/host/path/tls/IngressClass เป็นมาตรฐาน ใช้ได้ทุก controller ส่วน annotation traefik.ingress.kubernetes.io/router.middlewares และ Middleware (traefik.io) เป็นของ Traefik เท่านั้น",
  """Two shelves: a big shelf of standard sign parts and a smaller shelf with special checkpoint gadgets painted in the
  receptionist's uniform color. Nong Som sorts parts.""",
  ["มาตรฐาน networking.k8s.io/v1", "เฉพาะ Traefik", "router.middlewares", "Middleware (traefik.io)", "ย้าย controller ต้องแปลส่วนนี้"],
  "label 1 on the big shelf; label 2 on the small shelf; label 3 and label 4 on two gadgets; label 5 as a title banner")
t("middleware-chain", S14,
  "Middleware ของ Traefik เป็นด่านเรียงตามลำดับใน annotation: redirectScheme, basicAuth, stripPrefix, rateLimit ฯลฯ",
  """A hallway with four small checkpoints in a row: an arrow stand, a turnstile, a ticket trimmer and a slow gate with
  a timer; a customer passes them in order.""",
  ["redirectScheme", "basicAuth", "stripPrefix", "rateLimit", "ด่านตรวจเรียงตามลำดับ"],
  "label 1 to label 4 on the four checkpoints; label 5 as a title banner")
t("basic-auth-secret", S14,
  "basicAuth อ่าน Secret type kubernetes.io/basic-auth (ต่อยอดบท 011) ไม่มีบัตร → 401 + WWW-Authenticate; บัตรถูก → 200",
  """A turnstile at the back-office hallway reads a staff card taken from a sealed envelope from the key box; one
  customer without a card is stopped. Nong Som shows her card.""",
  ["type: kubernetes.io/basic-auth", "401 Unauthorized", "username: som", "password: ●●●●", "ต่อยอดซองจากบท 11"],
  "label 1 on the envelope; label 2 on the stop light; label 3 and label 4 on Nong Som's card; label 5 as a title banner",
  nt=True)
t("strip-prefix", S14,
  "stripPrefix ตัด /admin ออกก่อนส่งให้แอปหลังร้าน: /admin/orders → /orders และส่ง X-Forwarded-Prefix: /admin บอกต้นทาง",
  """A ticket trimmer machine cuts the first part off a long ticket; the shorter ticket goes into the back-office
  counter. Nong Som feeds the machine.""",
  ["/admin/orders", "→ /orders", "X-Forwarded-Prefix: /admin", "ตัดหัวตั๋วก่อนส่ง"],
  "label 1 on the long ticket; label 2 on the short ticket; label 3 on a small sticker; label 4 as a title banner",
  nt=True)

S15 = "15. Traefik บน kind: entrypoint และ NodePort"
t("kind-port-map", S15,
  "เส้นทางจริงใน LAB: เครื่องนักศึกษา localhost:30080/30081/30082 → container k8s-lab → lab-control-plane → Service traefik → Pod traefik (:8000/:8443/:8080) — ไม่มีพอร์ต 80/443",
  """A long dock path: a laptop at home, a cargo container bridge, the control tower ship, then the gate building with
  three doors (wooden, glass, monitoring). Nong Som walks along it.""",
  ["localhost:30080 → web :8000", "localhost:30081 → websecure :8443", "localhost:30082 → dashboard :8080", "ไม่มีพอร์ต 80/443", "kind map ไว้แค่ 3 พอร์ต"],
  "label 1 to label 3 on the three doors; label 4 on a crossed-out plate; label 5 as a title banner",
  nt=True)
t("port-conflict", S15,
  "NodePort ชนกัน: ถ้า Service ร้านเดิมยังถือ 30080 อยู่ การสร้าง Service traefik จะ error provided port is already allocated ต้องคืนพอร์ตก่อน",
  """Two counters reaching for the same gangway door handle; a red error card hangs on the door. Nong Som separates
  them.""",
  ["provided port is already allocated", "som-web (NodePort เดิม)", "Service traefik", "คืนพอร์ตก่อน"],
  "label 1 on the red card; label 2 and label 3 on the two counters; label 4 as a title banner",
  nt=True)
t("install-order", S15,
  "ลำดับติดตั้ง: CRD ของ Traefik ก่อน → RBAC + Deployment + Service → IngressClass; ถ้าลืม CRD log จะมี Failed to watch และ Middleware ใช้ไม่ได้",
  """Three numbered crates delivered in order by a crane to the gate; one crate missing leaves an error note on the
  robot's screen. Nong Som checks the delivery list.""",
  ["1) CRD", "2) RBAC + Deployment + Service", "3) IngressClass", "ลืม CRD → Failed to watch"],
  "label 1 to label 3 on the three crates; label 4 on the robot's screen note",
  nt=True)

S16 = "16. การ debug Ingress"
t("debug-toolkit", S16,
  "เครื่องมือ debug: kubectl describe ingress (ดู backend/endpoint, Events มักเป็น <none>), log ของ controller (ERR), access log ว่า router ไหนตอบรหัสอะไร, dashboard",
  """A toolbox open on the reception desk: a magnifier on the signboard, the guest book, the robot's log tape and the
  glass monitoring board. Nong Som works through them.""",
  ["kubectl describe ingress", "Events: <none>", "kubectl logs -n traefik", "access log", "dashboard", "ไล่ตรวจทีละชั้น"],
  "label 1 on the magnifier; label 2 as a small note; label 3 on the log tape; label 4 on the guest book; label 5 on the monitoring board; label 6 as a title banner",
  nt=True)

S17 = "17. readiness, rolling update และ Ingress"
t("zero-downtime", S17,
  "Ingress ส่งเฉพาะ Pod ที่ Ready (ตาม EndpointSlice) — readinessProbe + preStop sleep 5 + maxUnavailable: 0 ทำให้เปลี่ยนรุ่นผ่าน Ingress ได้ err=0",
  """The manager robot swaps booths one by one behind a counter; green lamps above booths; the receptionist robot only
  sends customers to green booths; a closing booth keeps serving for a moment.""",
  ["readinessProbe", "preStop sleep 5", "maxUnavailable: 0", "err=0", "เปลี่ยนรุ่นโดยลูกค้าไม่สะดุด"],
  "label 1 on a green lamp; label 2 on the closing booth; label 3 on the manager robot; label 4 on a score board; label 5 as a title banner",
  nt=True)
t("without-prestop", S17,
  "ถ้าไม่มี readiness/preStop ลูกค้าบางคนถูกพาไปบูธที่กำลังปิด ได้ 502 Bad Gateway ระหว่าง rollout (pre-check เจอ 3–6 ครั้งจาก 300)",
  """A booth slams its shutter while a customer is still at the window; the receptionist robot looks surprised. Nong
  Som raises a red flag.""",
  ["ไม่มี readiness / preStop", "502 Bad Gateway", "ลูกค้าบางคนเจอประตูปิด"],
  "label 1 on the booth; label 2 on the red flag; label 3 as a title banner",
  nt=True)

S18 = "18. canary และการแบ่งน้ำหนัก"
t("canary-weight", S18,
  "canary: ปล่อยรุ่นใหม่ให้ลูกค้าส่วนน้อยก่อน (เช่น 90/10) — Ingress มาตรฐานไม่มี weight ต้องใช้ความสามารถเฉพาะ controller หรือ Gateway API",
  """A turnstile splitting a queue of customers into a wide lane to the old booth and a narrow lane to a new booth.
  Nong Som adjusts a dial.""",
  ["90%", "10%", "รุ่นเดิม", "รุ่นใหม่", "ปล่อยรุ่นใหม่ทีละน้อย", "Ingress มาตรฐานไม่มี weight"],
  "label 1 and label 3 on the wide lane; label 2 and label 4 on the narrow lane; label 5 as a title banner; label 6 as a small note")

S19 = "19. ข้อจำกัดของ Ingress และ Gateway API (ปูทาง)"
t("ingress-limits", S19,
  "ข้อจำกัดของ Ingress: เน้น HTTP/HTTPS, ฟีเจอร์เสริมกระจายอยู่ใน annotation ของแต่ละ controller, ทุกทีมแก้ป้ายเดียวกัน ย้าย controller ยาก",
  """The single old signboard crowded with sticky notes in different colors; several teams queue to edit it. Nong Som
  sighs.""",
  ["เน้น HTTP/HTTPS", "ฟีเจอร์เสริมอยู่ใน annotation", "ทุกทีมแก้ป้ายเดียวกัน", "ย้าย controller ยาก"],
  "label 1 to label 3 on three sticky notes; label 4 as a title banner")
t("gateway-api-roles", S19,
  "Gateway API แยกบทบาท: GatewayClass (บริษัทผู้ให้บริการ), Gateway (อาคาร/ประตูขึ้นเรือ ที่ผู้ดูแลคลัสเตอร์คุม), HTTPRoute (ป้ายเส้นทางที่ทีมร้านแขวนเอง)",
  """The brand-new passenger terminal building next to the old gate: an operator company plaque, the terminal with
  boarding gates, and route boards hung by shop teams. Nong Som tours it.""",
  ["GatewayClass", "Gateway", "HTTPRoute", "ผู้ดูแลคลัสเตอร์", "ทีมร้าน", "อาคารผู้โดยสารรุ่นใหม่"],
  "label 1 on the plaque; label 2 on the terminal; label 3 on a route board; label 4 near the terminal staff; label 5 near the route boards; label 6 as a title banner",
  allow=True)

S20 = "20. เปรียบเทียบ แนวปฏิบัติ และสรุป"
t("comparison-table", S20,
  "เปรียบเทียบ NodePort / LoadBalancer / Ingress / Gateway API: ชั้นที่ทำงาน, จำนวนประตูภายนอก, เลือกตามชื่อ/path ได้ไหม, TLS, ความสามารถขั้นสูง",
  """A comparison board with exactly four rows, each row with a small icon (gangway door, paid lighthouse, front gate,
  passenger terminal) and a short row of color dots; Nong Som points at the third row.""",
  ["NodePort", "LoadBalancer", "Ingress", "Gateway API", "เลือกให้เหมาะกับงาน"],
  "label 1 to label 4 as the four row headers; label 5 as a title banner; the color dots are icons only without text",
  allow=True)
t("best-practices", S20,
  "แนวปฏิบัติ: pin เวอร์ชัน controller, Service แอปเป็น ClusterIP, เปิด TLS + redirect, มี readiness + preStop, ไม่ commit tls.key, จำกัดการเข้าถึงหน้าแอดมิน",
  """A checklist poster on the gate wall with five ticked rows; Nong Som salutes.""",
  ["pin เวอร์ชัน controller", "Service เป็น ClusterIP", "TLS + redirect", "readiness + preStop", "ไม่ commit tls.key", "ข้อปฏิบัติที่ดี"],
  "label 1 to label 5 as the five rows; label 6 as a title banner")
t("chapter-summary", S20,
  "สรุปบท: ป้าย (Ingress) + พนักงาน (controller) + ยูนิฟอร์ม (IngressClass) + ประตูกระจก (TLS) ร้านมีหน้าร้านเดียวด้วยชื่อ — บทต่อไป HPA, Helm, Gateway API",
  """Nong Som stands at the busy front gate at sunset; customers flow in through the glass door; three signposts on the
  horizon toward the next chapters.""",
  ["Ingress พาลูกค้าตามชื่อ", "TLS ที่ประตูเดียว", "ต่อไป: HPA · Helm · Gateway API"],
  "label 1 on the gate; label 2 on the glass door; label 3 on the signposts",
  allow=True)

# ================================================================ LAB
A = "LAB 0: เตรียมคลัสเตอร์"
l("lab0-prepare", A,
  "LAB 0: ตรวจ 3 Node Ready, ดูว่าใครถือ NodePort 30080–30082 (ร้านบท 011) แล้วลบ Service som-web/som-https ชั่วคราว, โหลด postgres + build som-shop-web:1.5/1.6 ไว้ใช้ LAB 10",
  """Nong Som checks a list at the dock: three ships ready, two old gangway doors being unscrewed, and crates of
  images lifted onto the ships by a crane.""",
  ["LAB 0", "kubectl get svc -A | grep 3008", "คืน NodePort ของร้านเดิม", "postgres + som-shop-web 1.5 / 1.6"],
  "label 1 as a title banner; label 2 on Nong Som's list; label 3 on the old doors; label 4 on the crates",
  nt=True)

B = "LAB 1: ติดตั้ง Traefik และ IngressClass"
l("lab1-open", B,
  "LAB 1 เปิด: ติดตั้งพนักงานต้อนรับ — CRD (v3.7.13) → 00-traefik.yaml (RBAC, Deployment, Service NodePort, IngressClass default)",
  """A new receptionist robot unpacked from a crate at the front gate; three numbered crates line up. Nong Som reads the
  manual.""",
  ["LAB 1", "ติดตั้งพนักงานต้อนรับ", "traefik:v3.7.13", "CRD → Deployment → IngressClass"],
  "label 1 as a title banner; label 2 as a subtitle; label 3 on the robot crate; label 4 on the crate row")
l("lab1-result", B,
  "ผล LAB 1: traefik Running (ดึง image จาก Docker Hub ได้ตรง ~7 วิ), IngressClass traefik (default), curl localhost:30080 → 404 page not found เพราะยังไม่มีป้าย, dashboard ที่ 30082",
  """The receptionist robot stands at the gate with an empty signboard; a customer gets an empty wrong-door; the glass
  monitoring board glows behind. Nong Som nods.""",
  ["traefik (default)", "404 page not found", "ยังไม่มีป้าย = 404", "dashboard"],
  "label 1 on the robot vest; label 2 on the wrong-door sign; label 3 as a title banner; label 4 on the monitoring board",
  nt=True)
l("lab1-port-conflict", B,
  "LAB 1 ลองผิด: ถ้าข้าม LAB 0 แล้ว Service ร้านเดิมยังถือ 30080 → The Service \"traefik\" is invalid: ... provided port is already allocated",
  """Two counters grab the same gangway door; a red card on the door; Nong Som holds the LAB 0 checklist.""",
  ["provided port is already allocated", "ลืม LAB 0", "คืนพอร์ตแล้ว apply ใหม่"],
  "label 1 on the red card; label 2 on the checklist; label 3 as a title banner",
  nt=True)

C = "LAB 2: Ingress แรก (host เดียว)"
l("lab2-open", C,
  "LAB 2 เปิด: Ingress แรก shop.localhost → Service menu (whoami) เปิดทั้ง curl และ browser http://shop.localhost:30080",
  """The receptionist robot hangs the first row on the signboard; one customer with a ticket walks to the menu
  counter. Nong Som claps.""",
  ["LAB 2", "Ingress แรก", "shop.localhost → menu", "http://shop.localhost:30080"],
  "label 1 as a title banner; label 2 as a subtitle; label 3 on the signboard row; label 4 on the customer's ticket")
l("lab2-host-header", C,
  "ผล LAB 2: curl -H 'Host: shop.localhost' ได้ Name: menu, ไม่ใส่ Host → 404, ADDRESS แสดง localhost; whoami แสดง Host: shop.localhost:30080",
  """Two customers at the gate: one with a named ticket goes in, one with a blank ticket meets the wrong-door; the
  status plate on the signboard shows a word. Nong Som compares.""",
  ["curl -H 'Host: shop.localhost'", "Name: menu", "ไม่มี Host → 404", "ADDRESS: localhost"],
  "label 1 on the named ticket; label 2 on the menu counter; label 3 on the wrong-door; label 4 on the status plate",
  nt=True)

D = "LAB 3: path-based fan-out"
l("lab3-open", D,
  "LAB 3 เปิด: ชื่อเดียว shop.localhost แยก path / → menu, /api → api, /admin → admin (3 Service)",
  """Three hallway doors under one shop name with three counters; Nong Som paints door plates.""",
  ["LAB 3", "/ → menu", "/api → api", "/admin → admin", "หนึ่งชื่อ สามเคาน์เตอร์"],
  "label 1 as a title banner; label 2 to label 4 on the three hallway doors; label 5 as a subtitle")
l("lab3-result", D,
  "ผล LAB 3: /api/stats ไป api และ path ไม่ถูกตัด (GET /api/stats) ส่วน /order ไป menu; backend อ้าง port ได้ทั้ง number: 80 และ name: http",
  """A whoami-style receipt printed by the api counter showing the counter name and the request line; Nong Som reads it.""",
  ["Name: api", "GET /api/stats", "path ไม่ถูกตัด", "/order → menu"],
  "label 1 and label 2 on the receipt; label 3 as a title banner; label 4 on a second small receipt",
  nt=True)

E = "LAB 4: host-based virtual hosting"
l("lab4-open", E,
  "LAB 4: เพิ่มกฎ admin.localhost → admin, ชื่ออื่นเช่น other.localhost → 404; Ingress ที่ไม่ใส่ class ถูกเติม ingressClassName: traefik",
  """Two named tickets go to two counters through the same gate; an unknown ticket meets the wrong-door; a gold-star
  tag stamped on the signboard. Nong Som sorts tickets.""",
  ["LAB 4", "admin.localhost → admin", "other.localhost → 404", "เติม class ให้เอง", "แยกตามชื่อร้าน"],
  "label 1 as a title banner; label 2 on the admin ticket; label 3 on the wrong-door; label 4 on the gold-star tag; label 5 as a subtitle",
  nt=True)

F = "LAB 5: pathType"
l("lab5-open", F,
  "LAB 5 เปิด: Ingress paths.localhost มี Prefix /api, Prefix /docs/, Exact /menu, ImplementationSpecific /impl แล้วยิง path ทดสอบ 15 แบบ",
  """Three door styles in a hall with a queue of test tickets; Nong Som holds a results clipboard.""",
  ["LAB 5", "Prefix", "Exact", "ImplementationSpecific", "ทดลองทีละ path"],
  "label 1 as a title banner; label 2 to label 4 on the three doors; label 5 on the clipboard")
l("lab5-table", F,
  "ผล LAB 5 (strictPrefixMatching=true): /apix → 404, /docs → 200, /menu/ → 404, /implx → 404; ถ้าปิด strict /apix ไป api และ /docs กลายเป็น 404",
  """A results board with exactly four rows of tickets with ticks and crosses, and a lever on the side. Nong Som flips
  the lever.""",
  ["/apix → 404", "/docs → 200", "/menu/ → 404", "/implx → 404", "ปิด strict → /apix ผ่าน", "ผลจริง"],
  "label 1 to label 4 as the four rows; label 5 on the lever; label 6 as a title banner",
  nt=True)

G = "LAB 6: debug 404 / 503 / defaultBackend"
l("lab6-open", G,
  "LAB 6 เปิด: ทำพังทีละแบบ — class ผิด, ชื่อ Service ผิด, port ผิด, scale เป็น 0, เพิ่ม defaultBackend",
  """Nong Som with a detective magnifier stands before four broken signboard rows with warning stickers.""",
  ["LAB 6", "ลองทำพังทีละแบบ", "404", "503", "ERR"],
  "label 1 as a title banner; label 2 as a subtitle; label 3 to label 5 on three warning stickers")
l("lab6-errors", G,
  "ผล LAB 6: describe แสดง <error: services \"menuu\" not found>, log ERR service port not found, class nginx → ADDRESS ว่าง, scale 0 → 503 no available server",
  """Four evidence cards pinned on a board with strings to the signboard; Nong Som connects them.""",
  ["services \"menuu\" not found", "service port not found", "class nginx → ADDRESS ว่าง", "503 no available server", "หลักฐานจาก describe + log"],
  "label 1 to label 4 on the four evidence cards; label 5 as a title banner",
  nt=True)
l("lab6-default-backend", G,
  "ผล LAB 6 (defaultBackend): ทุกชื่อที่ไม่ตรงกฎ — และกฎที่ Service ไม่มี endpoint — ไหลไปโต๊ะของหาย (admin) ใน Traefik เป็น catch-all ของทั้งคลัสเตอร์ จึงลบทิ้งหลังทดลอง",
  """All unknown tickets flow to the lost-and-found desk; a warning sign on the desk; Nong Som carries the desk away
  after the test.""",
  ["defaultBackend", "ชื่อที่ไม่ตรง → admin", "จับทั้งคลัสเตอร์", "ทดลองแล้วลบทิ้ง"],
  "label 1 on the desk; label 2 on the ticket stream; label 3 on the warning sign; label 4 as a title banner",
  nt=True)

H = "LAB 7: TLS ที่ Ingress"
l("lab7-open", H,
  "LAB 7 เปิด: openssl สร้างใบรับรองหลายชื่อ (shop.localhost, admin.localhost, localhost) → Secret som-tls → spec.tls",
  """Nong Som stamps a seal plate for the glass door and slides an envelope into the key box.""",
  ["LAB 7", "som-tls", "shop.localhost · admin.localhost", "ประตูกระจกนิรภัย"],
  "label 1 as a title banner; label 2 on the envelope; label 3 on the seal plate; label 4 on the glass door")
l("lab7-results", H,
  "ผล LAB 7: ไม่มี -k → curl: (60), --cacert tls.crt ผ่าน, ชื่ออื่นได้ TRAEFIK DEFAULT CERT, browser เตือนใบรับรอง self-signed (ต้องเปิด --entryPoints.websecure.http.tls=true)",
  """Three customers at the glass door: one blocked, one with a matching copy card allowed, one given a grey plate;
  a browser window shows a warning triangle.""",
  ["curl: (60)", "--cacert tls.crt ✔", "TRAEFIK DEFAULT CERT", "เบราว์เซอร์เตือนใบรับรอง"],
  "label 1 on the blocked customer; label 2 on the allowed customer; label 3 on the grey plate; label 4 on the browser window",
  nt=True)

I = "LAB 8: Middleware — redirect, basic auth, stripPrefix"
l("lab8-open", I,
  "LAB 8 เปิด: Middleware ของ Traefik (ไม่ใช่มาตรฐาน) redirectScheme, basicAuth (Secret basic-auth จากบท 011), stripPrefix ผูกด้วย annotation router.middlewares",
  """Three checkpoint gadgets unpacked in the hallway; Nong Som installs them in order.""",
  ["LAB 8", "redirectScheme", "basicAuth", "stripPrefix", "ด่านเฉพาะ Traefik"],
  "label 1 as a title banner; label 2 to label 4 on the three gadgets; label 5 as a subtitle")
l("lab8-results", I,
  "ผล LAB 8: http → 301 Location https://shop.localhost:30081/..., /admin ไม่มีบัตร 401, บัตรผิด 401, บัตรถูก 200 และแอปเห็น /orders",
  """A customer journey strip of four panels: arrow stand, stopped turnstile, open turnstile, trimmed ticket.""",
  ["301 → https://shop.localhost:30081/", "401 ไม่มีบัตร", "200 บัตรถูก", "/admin/orders → /orders"],
  "label 1 to label 4 on the four panels in order",
  nt=True)

J = "LAB 9: rolling update ผ่าน Ingress"
l("lab9-open", J,
  "LAB 9: วน curl https ผ่าน Ingress ระหว่างเปลี่ยน menu → menu-v2 (readiness + preStop + maxUnavailable: 0) ได้ err=0",
  """The manager robot swaps booths while a steady stream of customers flows through the glass door; a score board
  above. Nong Som times it.""",
  ["LAB 9", "เปลี่ยนรุ่นระหว่างลูกค้าเข้า", "menu → menu-v2", "err=0"],
  "label 1 as a title banner; label 2 as a subtitle; label 3 on the booths; label 4 on the score board",
  nt=True)
l("lab9-contrast", J,
  "LAB 9 เปรียบเทียบ: เอา readiness/preStop ออก → rollout restart สองรอบได้ 502 Bad Gateway บางครั้ง; ใส่กลับ → err=0",
  """Split panel: left a booth shutter slams on a customer with a red score; right a booth closes politely with a green
  score. Nong Som points to the right.""",
  ["ไม่มี preStop/readiness", "502 Bad Gateway", "มี preStop/readiness", "err=0"],
  "label 1 and label 2 on the left panel; label 3 and label 4 on the right panel",
  nt=True)

K = "LAB 10: ร้านน้องส้มมีหน้าร้านเดียวด้วยชื่อโดเมน"
l("lab10-open", K,
  "LAB 10 เปิด: ร้าน som-shop-v8 (คัดลอกจากบท 011) เข้าทาง https://shop.localhost และหลังร้าน admin.localhost ผ่าน Ingress",
  """The cat-food shop now sits behind the grand front gate with the glass door; a banner over the gate. Nong Som
  welcomes customers.""",
  ["LAB 10", "ร้านน้องส้มมีหน้าร้านเดียวด้วยชื่อโดเมน", "som-shop-v8"],
  "label 1 as a title banner; label 2 as a subtitle; label 3 on the shop booth")
l("lab10-before-after", K,
  "ก่อน/หลัง: บท 011 ใช้ NodePort 30080 + nginx HTTPS 30082; บท 012 ใช้ Ingress เดียว Service som-web เป็น ClusterIP",
  """Split panel: left two separate gangway doors on the shop ship; right one front gate with a glass door and indoor
  counters. Nong Som stands at the border.""",
  ["ก่อน: NodePort 30080 + 30082", "หลัง: https://shop.localhost:30081", "Service som-web: ClusterIP", "ย้ายประตูมาที่ Ingress"],
  "label 1 on the left panel; label 2 on the right panel; label 3 on an indoor counter; label 4 as a title banner",
  nt=True)
l("lab10-ports-cleanup", K,
  "ขั้น A: apply k8s/ ของ v8 (som-web → ClusterIP, ConfigMap ป้ายบท 012) และลบ som-https (nginx TLS ของบท 011) — ข้อมูล db และออเดอร์เดิมยังอยู่",
  """Nong Som unscrews the old nginx glass tube booth while the kitchen booth with its numbered safe stays untouched.""",
  ["som-web → ClusterIP", "ลบ som-https", "ออเดอร์เดิมยังอยู่"],
  "label 1 on the shop counter; label 2 on the removed booth; label 3 on the kitchen ledger",
  nt=True)
l("lab10-tls-move", K,
  "ขั้น B: ทำ som-tls ใบใหม่ให้ชื่อตรง (CN เดิม shop.som.local ใช้กับ shop.localhost ไม่ได้) แล้วย้าย TLS จาก nginx มาที่ spec.tls ของ Ingress",
  """Nong Som exchanges an old seal plate with a different name for a new plate listing two names, and hangs it on the
  glass door.""",
  ["som-tls ใบใหม่", "DNS:shop.localhost", "DNS:admin.localhost", "ย้าย TLS มาที่ Ingress"],
  "label 1 on the envelope; label 2 and label 3 on the new plate; label 4 as a title banner",
  nt=True)
l("lab10-admin", K,
  "ขั้น C: หลังร้าน som-admin (nginx-unprivileged + ConfigMap หน้า HTML + /stats) ที่ admin.localhost ป้องกันด้วย basicAuth จาก Secret som-admin-auth (รหัสตัวอย่าง)",
  """A back-office booth behind a turnstile; a staff silhouette shows a card; a small board inside shows an order
  counter icon.""",
  ["admin.localhost", "basicAuth", "som-admin-auth", "หลังร้าน: ดูยอดออเดอร์", "401 / 200"],
  "label 1 on the hallway door; label 2 on the turnstile; label 3 on the envelope; label 4 on the board; label 5 on the turnstile light",
  nt=True)
l("lab10-redirect-browser", K,
  "ขั้น D: browser เปิด http://shop.localhost:30080 → 301 → https://shop.localhost:30081 เตือน self-signed → หน้าร้านแสดง footer บท 012 (ทดสอบด้วย Chromium แล้ว)",
  """A browser window journey in two frames: the wooden door with an arrow, then the glass door opening onto the shop
  page with a small warning triangle. Nong Som waves from the shop.""",
  ["http://shop.localhost:30080", "301", "https://shop.localhost:30081", "ร้านอาหารแมวน้องส้ม", "เตือนใบรับรอง self-signed"],
  "label 1 on the first frame; label 2 on the arrow; label 3 on the second frame; label 4 as the shop page title; label 5 on the warning triangle",
  nt=True)
l("lab10-rolling", K,
  "ขั้น E: hit.sh ยิง https ผ่าน Ingress ระหว่าง rollout restart และ set image 1.5 → 1.6 ได้ err=0 ทั้งสองรอบ, rollout history มี change-cause",
  """The manager robot swaps booths from an old color to a new color while customers stream through the glass door; a
  logbook open. Nong Som watches the score board.""",
  ["1.5 → 1.6", "err=0", "ลูกค้าไม่สะดุด", "rollout history"],
  "label 1 on the booths; label 2 on the score board; label 3 as a title banner; label 4 on the logbook",
  nt=True)
l("lab10-checklist", K,
  "ตรวจรับร้าน: http → https, shop.localhost ขายได้, admin.localhost ต้องมีบัตร, NodePort เดิมของร้านไม่มีแล้ว, rolling update err=0",
  """A checklist board at the gate with five ticked rows; Nong Som signs it.""",
  ["http → https", "shop.localhost ขายได้", "admin.localhost ต้องมีบัตร", "ไม่มี NodePort ของร้านแล้ว", "rolling update err=0", "ตรวจรับร้าน"],
  "label 1 to label 5 as the five rows; label 6 as a title banner",
  nt=True)
l("lab10-wrap-up", K,
  "ปิดบท: ร้านคนเยอะขึ้นต้องเพิ่มบูธอัตโนมัติ (HPA), ติดตั้ง controller/ร้านเป็นแพ็กเกจ (Helm), และอาคารผู้โดยสารรุ่นใหม่ (Gateway API)",
  """Nong Som stands at the gate looking at a long queue of customers; three signposts on the horizon point to the next
  chapters.""",
  ["ร้านคนแน่น → HPA", "ติดตั้งเป็นแพ็กเกจ → Helm", "อาคารใหม่ → Gateway API"],
  "label 1 to label 3 on the three signposts",
  allow=True)

X = "LAB เสริม: ลองชิม Gateway API"
l("labx-gateway-open", X,
  "LAB เสริม: ติดตั้ง Gateway API CRD v1.6.2 + เปิด --providers.kubernetesgateway แล้วสร้าง GatewayClass/Gateway/HTTPRoute แบ่งน้ำหนัก 90/10",
  """Nong Som opens the door of the new passenger terminal next to the old gate; a route board with two lanes of
  different widths.""",
  ["LAB เสริม", "Gateway API", "HTTPRoute weight 90 / 10", "ลองอาคารผู้โดยสารใหม่"],
  "label 1 as a title banner; label 2 on the terminal; label 3 on the route board; label 4 as a subtitle",
  allow=True, nt=True)
l("labx-gateway-result", X,
  "ผล LAB เสริม: GatewayClass ACCEPTED True, Gateway PROGRAMMED True, ยิง 40 ครั้งได้ร้าน 36 / หลังร้าน 4 (ใกล้ 90/10)",
  """A counting board next to the two lanes with tally marks; Nong Som checks the numbers.""",
  ["ACCEPTED True", "PROGRAMMED True", "36 : 4", "แบ่งลูกค้าตามน้ำหนัก"],
  "label 1 on the plaque; label 2 on the terminal; label 3 on the counting board; label 4 as a title banner",
  allow=True, nt=True)

if __name__ == "__main__":
    main()
