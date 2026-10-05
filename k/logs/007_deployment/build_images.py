#!/usr/bin/env python3
"""storyboard ภาพบท 007 Kubernetes Deployment (แยกจากบทรวม logs/005_rs_deploy_svc)

รัน: python3 build_images.py → images.json, image-sources.tsv,
007_kubernetes_deployment/01_Theory/images/imagegen-prompts.md, 02_LAB/images/imagegen-prompts.md
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import imgcommon
from imgcommon import t, l

imgcommon.configure("007")

# ================================================================== THEORY
S1 = "1. บทนำ: เปลี่ยนรุ่นด้วยมือแล้วร้านสะดุด"
t("opening-manual-swap-stumble", S1,
  "เปิดบทที่ 7: ต่อจากบท 006 — set image ที่ ReplicaSet แล้วบูธเดิมยังเป็น 1.2 น้องส้มต้องลบบูธเองทีละตัว ลูกค้าบางคนชนบูธที่กำลังปิด",
  "A harbor dock at midday. Three teal Pod shop booths stand on a cargo ship; the left two booths still show a "
  "teal signboard, the right booth is being lifted away by a crane with its shutter half closed, and a faceless "
  "customer silhouette bumps into that closing shutter holding an empty food bowl. A teal shift-supervisor robot "
  "stands beside the ship holding a new blueprint card. Nong Som, sweaty and tired, holds a big red delete button "
  "remote in one paw and wipes her forehead with the other.",
  ["บทที่ 7", "template: 1.3", "1.2", "1.2", "kubectl delete pod"],
  "'บทที่ 7' is a title banner across the top; 'template: 1.3' is on the blueprint card held by the robot; the two "
  "remaining booths each carry one '1.2' signboard; the booth being lifted has an awning only, no sign; "
  "'kubectl delete pod' is printed on the red button remote", src="T01 01-opening-lonely-pod-lost.png (แก้)")
t("rs-template-no-change", S1,
  "ทบทวนบท 005–006: แก้ template ของ ReplicaSet แล้ว Pod เดิมไม่เปลี่ยน มีผลเฉพาะ Pod ที่เกิดใหม่ และไม่มีสมุดประวัติให้ย้อนรุ่น",
  "The teal supervisor robot holds a new blueprint showing a booth with a star; on the ship two older booths have "
  "no star and only one freshly stamped booth has the star. Beside the robot stands an empty logbook stand with a "
  "big red question mark. Nong Som shakes her head with crossed arms.",
  ["template: 1.3", "1.2", "1.2", "1.3", "no history"],
  "'template: 1.3' on the blueprint; the two older booths each have one '1.2' signboard and the starred booth has "
  "the '1.3' signboard; the ship shows exactly three booths; 'no history' on the empty logbook stand",
  src="T12 12-rs-why-not-directly.png (แก้)")
t("new-metaphor-legend", S1,
  "อุปมาใหม่ของบทนี้: ผู้จัดการร้าน = Deployment, สติกเกอร์บาร์โค้ด = pod-template-hash, เปลี่ยนป้ายทีละบูธ = RollingUpdate, ปิดทั้งร้านก่อน = Recreate, สมุดบันทึกรุ่น = rollout history, ปุ่มกรอกลับ = rollout undo",
  "A clean legend board with exactly six illustrated rows; each row has one icon on the left and its Kubernetes "
  "term on the right: (1) a tall navy box robot with a bow tie and a thick logbook, (2) a small barcode sticker, "
  "(3) a booth signboard being swapped by a paw while the booth stays open, (4) a row of booths with shutters "
  "all down, (5) an open thick logbook, (6) a big round rewind button. Nong Som points at the board with a "
  "pointer stick.",
  ["Deployment", "pod-template-hash", "RollingUpdate", "Recreate", "rollout history", "rollout undo"],
  "exactly six rows and each row has exactly one of the six labels in the order listed; the shutters, sticker "
  "and signboard icons carry no text", src="T02 02-new-metaphor-legend.png (แก้)")

S2 = "2. Deployment → ReplicaSet → Pod"
t("deploy-hierarchy", S2,
  "ลำดับชั้น: Deployment (ผู้จัดการร้าน) → ReplicaSet (หัวหน้ากะ 1 คนต่อ 1 template) → Pod (บูธ) — เราสั่ง Deployment อย่างเดียว",
  "Top: a tall navy store-manager robot with bow tie and logbook. Middle: two teal supervisor robots linked by "
  "lines to the manager; the left one is faded (old version) holding an empty clipboard, the right one is bright. "
  "Bottom: three booths linked to the bright supervisor. Nong Som stands next to the manager giving orders through "
  "a megaphone.",
  ["Deployment: web", "ReplicaSet (old) 0", "ReplicaSet (new) 3", "Pod", "Pod", "Pod"],
  "each of the three booths carries one 'Pod' label; supervisor labels as listed under each supervisor robot",
  src="T13 13-deploy-hierarchy.png")
t("do-not-edit-owned-rs", S2,
  "ห้ามแก้ ReplicaSet ที่ Deployment เป็นเจ้าของ: scale RS ตรง ๆ เป็น 6 แล้วผู้จัดการร้านหมุนกลับเป็น 3 ทันที (แก้ที่ Deployment เท่านั้น)",
  "A teal supervisor robot with an owner badge clipped on its chest that points up to the tall navy manager "
  "robot. A faceless staff silhouette turns the supervisor's head-count dial up; the manager robot reaches down "
  "and turns the dial back. Two extra booths appear faded and dissolving next to three solid booths. Nong Som "
  "wags a finger at the staff silhouette.",
  ["kubectl scale rs", "6", "3", "ownerReferences: Deployment"],
  "'kubectl scale rs' on a small ticket held by the staff silhouette; '6' on the dial before (left inset) and "
  "'3' on the dial after (right inset); 'ownerReferences: Deployment' on the owner badge; booths carry no text")
t("deploy-manifest-anatomy", S2,
  "โครง manifest ของ Deployment: replicas, selector, template (เหมือน ReplicaSet) + strategy, minReadySeconds, revisionHistoryLimit, progressDeadlineSeconds",
  "The tall navy manager robot holds up a large rounded manifest card divided into two colored blocks: a teal block "
  "(fields shared with ReplicaSet) and a navy block (fields only the manager has). Each field line has a small "
  "icon: a head-count dial, a magnifier with a luggage tag, a blueprint, a swapping signboard, an hourglass, a "
  "logbook shelf, a stopwatch. Nong Som reads the card with a pencil behind her ear.",
  ["replicas", "selector", "template", "strategy", "minReadySeconds", "revisionHistoryLimit",
   "progressDeadlineSeconds"],
  "exactly seven field lines; the first three labels sit in the teal block and the last four in the navy block; "
  "each line has exactly one label; the two colored blocks have no headings")
t("create-dry-run", S2,
  "เริ่มเขียน YAML จากคำสั่ง: kubectl create deployment ... --dry-run=client -o yaml > web.yaml แล้วแก้ไฟล์ต่อ (ไม่สร้างอะไรในคลัสเตอร์)",
  "A small stencil-printing machine on the dock: a command ticket is fed into the top slot, and a fresh YAML "
  "card slides out of the bottom tray into a folder; a small dotted line shows the machine is not connected to "
  "the harbor control tower in the background. Nong Som catches the YAML card happily.",
  ["kubectl create deployment", "--dry-run=client -o yaml", "web.yaml"],
  "'kubectl create deployment' on the command ticket; '--dry-run=client -o yaml' on the machine's front panel; "
  "'web.yaml' on the folder tab; the YAML card shows only grey lines, no readable text")
t("ready-uptodate-available", S2,
  "อ่านคอลัมน์ kubectl get deploy: READY (Pod พร้อม/ต้องการ), UP-TO-DATE (Pod ที่เป็น template ล่าสุด), AVAILABLE (พร้อมต่อเนื่องครบ minReadySeconds)",
  "A three-column scoreboard on the dock above three booths. Column 1 icon: green lamps; column 2 icon: a "
  "booth with the newest barcode sticker; column 3 icon: a green lamp with a small hourglass. Under each header "
  "a big number. Nong Som points at the scoreboard.",
  ["READY", "UP-TO-DATE", "AVAILABLE", "3/3", "3", "3"],
  "exactly three columns; headers 'READY', 'UP-TO-DATE', 'AVAILABLE' in order; numbers '3/3', '3', '3' under "
  "them in order; booths carry no text")
t("pod-template-hash", S2,
  "pod-template-hash: Deployment ติดป้าย hash ของ template ให้ ReplicaSet และ Pod ของแต่ละรุ่น กันหัวหน้ากะสองรุ่นนับกล่องปนกัน — ชื่อ Pod = <deploy>-<hash>-<สุ่ม>",
  "Two supervisor robots each with their own colored blueprint; each blueprint has a small barcode sticker. "
  "Booths beside each robot carry two tags: the shared orange app tag and a small barcode sticker matching their "
  "own robot. One booth in front wears a name card. Nong Som compares the two barcode stickers with a magnifier.",
  ["app=web", "pod-template-hash=6f58b8bd67", "pod-template-hash=7c987cc6b4", "web-6f58b8bd67-frgpm"],
  "'app=web' appears once on a large orange tag held by Nong Som; each hash label appears once on its robot's "
  "blueprint sticker; 'web-6f58b8bd67-frgpm' on the name card of one booth beside the first robot; other booth "
  "barcode stickers have no readable text; draw barcodes only, no food or hash browns",
  src="T14 14-pod-template-hash.png (แก้)")

S3 = "3. อะไรทำให้เกิด rollout"
t("what-triggers-rollout", S3,
  "rollout (revision ใหม่) เกิดเมื่อ .spec.template เปลี่ยนเท่านั้น (image, env, probe, rollout restart = annotation restartedAt); scale replicas ไม่เกิด revision",
  "Two trays in front of the manager robot. Left tray: three change cards (a crate card, an env card, a green "
  "lamp card) plus a small sticky note, all falling into the blueprint; an arrow leads to a new logbook page "
  "with a sparkle. Right tray: a head-count dial; an arrow leads to the same old logbook page with a calm grey "
  "check. Nong Som holds the logbook open between the trays.",
  [".spec.template", "image / env / probe", "restartedAt", "revision +1", "replicas", "ไม่เกิด revision"],
  "'.spec.template' on the blueprint; 'image / env / probe' on a banner above the three change cards; "
  "'restartedAt' on the sticky note; 'revision +1' on the new logbook page; 'replicas' on the dial; "
  "'ไม่เกิด revision' on the old page")

S4 = "4. RollingUpdate: maxSurge / maxUnavailable"
t("rolling-update-steps", S4,
  "rolling update replicas 3 ค่า default (+1/−0): ลำดับ Events จริง — RS ใหม่ 0→1, เก่า 3→2, ใหม่ 1→2, เก่า 2→1, ใหม่ 2→3, เก่า 1→0 ร้านไม่ปิดเลย",
  "Seven stacked horizontal rows (timeline from top to bottom); each row shows the old supervisor's booths with a "
  "blue awning and the new supervisor's booths with an orange awning, booth counts exactly as the row label says. "
  "Customers keep walking into green-lit booths in every row. Nong Som rides a small cart along the side "
  "swapping signboards.",
  ["old 3 / new 0", "old 3 / new 1", "old 2 / new 1", "old 2 / new 2", "old 1 / new 2", "old 1 / new 3",
   "old 0 / new 3"],
  "exactly seven rows, each row has exactly one of the seven labels on its left in the listed order; the booth "
  "counts in each row match its label exactly; never more than four booths in one row; awnings carry no text",
  src="T15 15-rolling-update-steps.png (แก้)")
t("max-surge-unavailable", S4,
  "maxSurge ปัดขึ้น / maxUnavailable ปัดลง (default 25%/25%): replicas 3 → +1/−0, 4 → +1/−1, 10 → +3/−2 (สูงสุด 13 พร้อมอย่างน้อย 8); ตั้งเป็น 0 ทั้งคู่ไม่ได้",
  "A ruler-style gauge board with two bars. Top bar: ten booth icons plus three dashed extra booth slots at the "
  "right end, with an up-arrow ceiling icon. Bottom bar: ten booth icons with two of them dimmed, with a "
  "down-arrow floor icon. A small side card on the right shows two small examples stacked. Nong Som points at "
  "the up arrow and the down arrow.",
  ["replicas: 10", "maxSurge 25% → 3 (max 13)", "maxUnavailable 25% → 2 (min 8)", "ปัดขึ้น", "ปัดลง",
   "replicas: 3 → +1 / -0", "replicas: 4 → +1 / -1"],
  "'replicas: 10' as the board title; 'maxSurge 25% → 3 (max 13)' and 'ปัดขึ้น' on the top bar; "
  "'maxUnavailable 25% → 2 (min 8)' and 'ปัดลง' on the bottom bar; exactly 10 solid booth icons per bar; exactly "
  "3 dashed extra slots on the top bar; exactly 2 dimmed booths on the bottom bar; the side card has the two "
  "'replicas: 3' and 'replicas: 4' lines", src="T16 16-max-surge-unavailable.png (แก้)")
t("recreate-vs-rolling", S4,
  "RollingUpdate vs Recreate: Recreate ปิดทุกบูธเก่าก่อนแล้วค่อยเปิดรุ่นใหม่ (มีช่วงร้านปิด) เหมาะกับงานที่ห้ามมี 2 รุ่นพร้อมกัน",
  "Two horizontal lanes. Top lane: booths change color one by one, a small open sign stays lit all the time. "
  "Bottom lane: all blue booths close shutters at once, a gap with a closed sign and waiting customer silhouettes, "
  "then orange booths open. Nong Som stands between the lanes holding a little stopwatch.",
  ["RollingUpdate", "Recreate", "OPEN", "CLOSED"],
  "'RollingUpdate' labels the top lane, 'Recreate' the bottom lane; 'OPEN' is the sign on the top lane; 'CLOSED' "
  "is the sign in the gap of the bottom lane", src="T17 17-recreate-vs-rolling.png")
t("recreate-for-db", S4,
  "ทำไม som-db ใช้ Recreate: ถ้า rolling จะมี postgres 2 ตัวพร้อมกัน แต่ละตัวมีข้อมูลของตัวเอง (emptyDir) Service som-db จะส่ง web ไปคนละฐานข้อมูล — Recreate รับประกันว่ามีตัวเดียว",
  "Left panel (crossed with a big red X): a small lighthouse counter with a name plate sends web booths' arrows "
  "split between two database booths, each with its own separate storage chest of cat-food cans, one chest full "
  "and one empty. Right panel (green check): the same lighthouse points to exactly one database booth with one "
  "chest; a short CLOSED moment icon (small shutter) sits above it. Nong Som stands between the panels "
  "explaining with open paws.",
  ["RollingUpdate", "Recreate", "som-db", "som-db"],
  "'RollingUpdate' as the left panel heading; 'Recreate' as the right panel heading; each panel's small "
  "lighthouse name plate reads 'som-db' (so 'som-db' appears exactly twice); chests and shutter icons have no text")

S5 = "5. readinessProbe และ minReadySeconds ตัดสินจังหวะ rollout"
t("readiness-gates-rollout", S5,
  "readinessProbe และ minReadySeconds คุมจังหวะ rollout: บูธใหม่ต้องไฟเขียว (และเขียวต่อเนื่องตาม minReadySeconds) ก่อนจึงปิดบูธเก่าตัวถัดไป",
  "A new orange booth with its lamp switching from red to green, a small hourglass beside it; next to it the "
  "manager robot waits with a hand raised in a 'wait' gesture before an old blue booth. A second new booth with a "
  "red lamp gets no customers. Nong Som watches the hourglass.",
  ["readinessProbe", "minReadySeconds: 5", "Ready", "0/1"],
  "'readinessProbe' on the lamp of the first new booth; 'minReadySeconds: 5' on the hourglass; 'Ready' under the "
  "green-lit booth; '0/1' under the red-lit booth", src="T18 18-readiness-gates-rollout.png")
t("probe-roles", S5,
  "ไม่มี readinessProbe = ถือว่าพร้อมทันทีที่ container start (ลูกค้าเจอ error ระหว่าง rollout); readiness ตรวจ db ได้ แต่ liveness ไม่ควรพึ่ง db (db ล่มแล้ว web ถูก restart ทั้งร้าน)",
  "Left panel: a booth with no lamp at all is still unpacking crates behind the counter while a customer "
  "silhouette already receives an empty bowl with a small red spark. Right panel: one web booth with two "
  "instruments on its roof — a green lamp wired by a dotted line to a database booth with a chest, and a "
  "heartbeat monitor wired only to the web booth itself. Nong Som stands in the middle with a checklist.",
  ["ไม่มี readinessProbe", "error", "readinessProbe: /api/health", "livenessProbe: /api/live", "som-db"],
  "'ไม่มี readinessProbe' as the left panel heading; 'error' next to the red spark; 'readinessProbe: /api/health' "
  "on the green lamp; 'livenessProbe: /api/live' on the heartbeat monitor; 'som-db' on the database booth")

S6 = "6. zero-downtime: preStop + terminationGracePeriodSeconds + maxUnavailable 0"
t("termination-timeline", S6,
  "ลำดับการปิด Pod: ถูกสั่งลบ → endpoint เปลี่ยนเป็น terminating (ต่อจากบท 006) พร้อมกับ preStop sleep → SIGTERM → แอปปิด graceful — ทั้งหมดต้องจบใน terminationGracePeriodSeconds",
  "A wide horizontal timeline arrow across the panel with five stations, each with a small booth illustration: "
  "(1) booth gets a grey Terminating ribbon, (2) the lighthouse clipboard crosses the booth off while the booth "
  "still serves the last customer, (3) an hourglass in front of the booth, (4) a bell rings at the booth, (5) the "
  "shutter closes gently. A long bracket bar spans all five stations underneath. Nong Som walks along the "
  "timeline holding a stopwatch.",
  ["Terminating", "EndpointSlice: terminating", "preStop sleep 5s", "SIGTERM",
   "terminationGracePeriodSeconds: 30"],
  "stations 1–4 carry 'Terminating', 'EndpointSlice: terminating', 'preStop sleep 5s', 'SIGTERM' in order; "
  "station 5 has no text; 'terminationGracePeriodSeconds: 30' on the long bracket bar")
t("zero-downtime", S6,
  "zero-downtime rollout: readinessProbe + maxUnavailable: 0 + preStop sleep + grace period ให้บูธเก่าเลิกรับลูกค้าใหม่ก่อนปิดจริง — pre-check ร้าน Next.js ได้ 0 error จาก 300 คำขอสองรอบ",
  "A wide timeline of an old booth being closed: first its name is removed from the lighthouse list, then the "
  "booth keeps serving the last customer during a short hourglass wait, then the shutter closes; a new orange "
  "booth with a green lamp opens on the right. Above, a counter board tracks requests and errors. Nong Som holds "
  "a tally counter.",
  ["preStop sleep 5s", "maxUnavailable: 0", "readinessProbe", "errors: 0/300"],
  "'preStop sleep 5s' on the hourglass; 'maxUnavailable: 0' on the manager card at the left; 'readinessProbe' "
  "on the green lamp of the new booth; 'errors: 0/300' on the counter board",
  src="T38 38-zero-downtime.png (แก้)")

S7 = "7. progressDeadlineSeconds: rollout ค้างแต่ร้านยังขาย"
t("progress-deadline", S7,
  "รุ่นใหม่พัง (image tag ผิด → ImagePullBackOff): rollout ค้าง บูธรุ่นเก่ายังเปิดขายครบ เมื่อเกิน progressDeadlineSeconds สถานะเป็น ProgressDeadlineExceeded",
  "Three blue booths with green lamps keep serving customers on the left. On the right one new orange booth "
  "frame is empty because its container crate never arrived: an empty delivery cart with a red X next to it. An "
  "hourglass above it has run out. The manager robot shows a red status card. Nong Som points to the still-busy "
  "blue booths, relieved.",
  ["ImagePullBackOff", "progressDeadlineSeconds: 30", "ProgressDeadlineExceeded", "3/3"],
  "'ImagePullBackOff' under the empty orange booth; 'progressDeadlineSeconds: 30' on the hourglass; "
  "'ProgressDeadlineExceeded' on the manager's red card; '3/3' above the three blue booths",
  src="T19 19-progress-deadline.png")
t("no-auto-rollback", S7,
  "Kubernetes ไม่ rollback ให้อัตโนมัติ: เกิน deadline แล้วแค่ตั้ง Progressing=False (READY 3/3, UP-TO-DATE 1, AVAILABLE 3) คนต้องสั่ง rollout undo เอง",
  "The manager robot holds a red status card but keeps its logbook closed, hands folded, waiting. A status board "
  "on a post shows three readouts. Nong Som walks up to a big round rewind button on a pedestal and is about to "
  "press it herself.",
  ["Progressing=False", "READY 3/3", "UP-TO-DATE 1", "AVAILABLE 3", "kubectl rollout undo"],
  "'Progressing=False' on the manager's red card; the status board has exactly three readouts 'READY 3/3', "
  "'UP-TO-DATE 1', 'AVAILABLE 3' in order; 'kubectl rollout undo' on the rewind button")

S8 = "8. rollout history / change-cause / undo / pause / restart"
t("rollout-history", S8,
  "rollout history = สมุดบันทึกรุ่นของผู้จัดการร้าน: แต่ละ revision จำ template ไว้ ข้อความ CHANGE-CAUSE มาจาก annotation kubernetes.io/change-cause",
  "The manager robot opens a thick logbook to a page showing a table with exactly three rows, each row a revision "
  "number and a short note; a sticky note on the cover. Nong Som writes on the sticky note with a pencil.",
  ["REVISION", "CHANGE-CAUSE", "1  v1 nginx 1.27", "2  v2 nginx 1.28", "3  v3 broken",
   "kubernetes.io/change-cause"],
  "table header has 'REVISION' and 'CHANGE-CAUSE'; exactly three rows with the three row labels; "
  "'kubernetes.io/change-cause' on the sticky note on the cover", src="T20 20-rollout-history.png")
t("change-cause-trap", S8,
  "change-cause ใส่ด้วย kubectl annotate (--record ถูกถอดแล้ว) — กับดัก: revision ถัดไปที่ลืม annotate สืบทอดข้อความเดิม ทำให้ history หลอกตา",
  "The open logbook on a stand shows two rows; the second row is circled in red with a small warning triangle "
  "because it repeats the first row's note. Nong Som holds a rubber stamp; beside her a crossed-out old stamp "
  "lies in a small bin.",
  ["kubectl annotate", "2  v2 nginx 1.28", "3  v2 nginx 1.28", "--record"],
  "'kubectl annotate' on Nong Som's rubber stamp; exactly two logbook rows reading '2  v2 nginx 1.28' then "
  "'3  v2 nginx 1.28'; '--record' on the crossed-out stamp in the bin")
t("rollout-undo", S8,
  "rollout undo: ย้อนไปใช้ template ของรุ่นก่อน — Kubernetes ทำเป็น revision ใหม่ (เลขเดิมหายจากรายการ เช่นเหลือ 1, 3, 4) และขยายหัวหน้ากะรุ่นเก่ากลับมา",
  "The manager robot flips the logbook pages backward with a curved arrow; the faded old supervisor robot wakes "
  "up and its blue booths come back, while the orange broken booth shrinks away. A small revision list card "
  "shows that the old page moved to the end. Nong Som presses a big round rewind button.",
  ["kubectl rollout undo", "--to-revision=2", "1", "3", "4"],
  "'kubectl rollout undo' on the rewind button; '--to-revision=2' on the flipping page; the revision list card "
  "has exactly three rows reading '1', '3', '4' from top to bottom", src="T21 21-rollout-undo.png")
t("last-applied-warning", S8,
  "undo บน object ที่สร้างด้วย apply มีคำเตือน last-applied-configuration ไม่ถูกแก้ → undo คือการแก้ฉุกเฉิน แล้วต้องแก้ YAML ใน git ให้ตรงกับของจริง",
  "Left: the manager robot's logbook flipped back with a rewind arrow. Right: a git folder on a desk whose "
  "YAML card still shows a newer orange booth icon, with a yellow warning triangle between the two. Nong Som "
  "edits the YAML card with a pen to match the logbook.",
  ["rollout undo", "Warning", "last-applied-configuration", "แก้ YAML ใน git"],
  "'rollout undo' on the rewind arrow; 'Warning' on the yellow triangle; 'last-applied-configuration' on a tab "
  "of the folder; 'แก้ YAML ใน git' on a sticky note held by Nong Som")
t("pause-resume", S8,
  "rollout pause / resume: หยุด rollout ชั่วคราวเพื่อแก้หลายอย่างพร้อมกัน แล้ว resume ให้เปลี่ยนรุ่นครั้งเดียว (revision เดียว)",
  "The manager robot holds a pause sign while three small change cards (an image card, an env card, a resources "
  "card) stack up in a tray; then a resume sign and a single combined rollout arrow. Nong Som stacks the cards.",
  ["kubectl rollout pause", "kubectl rollout resume", "image", "env", "resources"],
  "each change card has exactly one of 'image', 'env', 'resources'", src="T22 22-pause-resume.png")
t("revision-history-limit", S8,
  "revisionHistoryLimit (default 10): ReplicaSet รุ่นเก่าเก็บไว้ด้วย replicas 0 = ข้อมูลสำหรับ undo; เกินจำนวนจะถูกลบ; ตั้ง 0 = undo ไม่ได้",
  "A shelf in the control tower with sleeping teal supervisor robots lined up, each with an empty clipboard; a "
  "shelf sign shows the limit; one robot at the far end is being gently carried out. One awake supervisor robot "
  "with booths stands in front. A small inset at the corner shows an empty shelf with a crossed-out rewind "
  "button. Nong Som counts the sleeping robots.",
  ["revisionHistoryLimit: 10", "replicas: 0", "replicas: 3", "revisionHistoryLimit: 0"],
  "'revisionHistoryLimit: 10' on the shelf sign; 'replicas: 0' printed once on the shelf edge; sleeping robots "
  "hold their clipboards face-down (no display visible); 'replicas: 3' on the awake robot's clipboard; "
  "'revisionHistoryLimit: 0' on the inset's empty shelf sign", src="T23 23-revision-history-limit.png (แก้)")

S9 = "9. วิธีเปลี่ยน Deployment และกับดัก apply"
t("ways-to-change", S9,
  "เปลี่ยน Deployment ได้หลายทาง: set image / set env / scale / edit / patch (เร็ว แต่ YAML ใน git ไม่ตรง) vs แก้ไฟล์แล้ว kubectl apply -f (แนวทางที่แนะนำ)",
  "A control panel with five buttons on the left side and a big folder with a check mark on the right side. "
  "Arrows from all buttons and the folder point to the manager robot. A small warning triangle sits between the "
  "buttons and the folder. Nong Som holds the folder proudly.",
  ["kubectl set image", "kubectl set env", "kubectl scale", "kubectl edit", "kubectl patch", "kubectl apply -f"],
  "exactly five buttons, each with one of the first five labels; 'kubectl apply -f' on the folder; the warning "
  "triangle has no text", src="T24 24-ways-to-change.png (แก้)")
t("apply-overwrites-replicas", S9,
  "กับดัก: scale ด้วยมือเป็น 5 แล้วภายหลัง apply ไฟล์ที่เขียน replicas: 3 → จำนวนกลับเป็น 3 (ไฟล์ชนะ) — ให้แก้ตัวเลขในไฟล์ หรือไม่ใส่ replicas ถ้าใช้ตัวปรับอัตโนมัติ",
  "Left: a staff silhouette turns the manager's dial to five booths. Right: Nong Som feeds a YAML folder into "
  "the manager robot and two of the five booths fade away, leaving three. A big curved arrow goes from left to "
  "right.",
  ["kubectl scale --replicas=5", "web.yaml: replicas: 3", "kubectl apply -f", "5 → 3"],
  "'kubectl scale --replicas=5' on the dial ticket; 'web.yaml: replicas: 3' on the folder; 'kubectl apply -f' "
  "on the big curved arrow; '5 → 3' above the remaining booths")

S10 = "10. ย้ายจาก ReplicaSet (บท 006) เป็น Deployment"
t("adopt-rs", S10,
  "ย้าย RS → Deployment: Deployment รับเลี้ยง ReplicaSet ที่ label ตรง selector และยังไม่มีเจ้าของ (ติด ownerReferences) — RS เดิมถูกมองเป็นรุ่นเก่า แล้วถูก scale ลงระหว่าง rolling (ต้องยืนยันใน LAB)",
  "The tall navy manager robot clips an owner badge onto an existing teal supervisor robot that had no badge; "
  "that old supervisor's three blue booths shrink one by one while a new supervisor robot behind the manager "
  "stamps orange booths. Both supervisors' booths wear the same orange app tag. Nong Som watches with a "
  "clipboard.",
  ["ReplicaSet som-web (เดิม)", "ownerReferences: Deployment", "app=som-web", "3 → 0", "0 → 3"],
  "'ReplicaSet som-web (เดิม)' on the old supervisor's chest plate; 'ownerReferences: Deployment' on the badge "
  "being clipped; 'app=som-web' printed once on a large tag held up by the manager; '3 → 0' under the old "
  "supervisor's booths; '0 → 3' under the new supervisor's booths; the booth tags themselves are color-only",
  nt=True)
t("orphan-alternative", S10,
  "ทางสำรอง: kubectl delete rs som-web --cascade=orphan ลบหัวหน้ากะแต่ทิ้งบูธไว้ขายต่อ (ไม่มีป้ายเจ้าของ) แล้วสร้าง Deployment เมื่อบูธใหม่พร้อมจึงลบบูธเก่าเอง",
  "An old teal supervisor robot walks away off the dock with its clipboard; three blue booths stay open and "
  "keep serving, each with an empty badge hook (no owner badge). On the right a manager robot with three new "
  "orange booths with green lamps; a small broom icon near the old booths. Nong Som holds a checklist.",
  ["--cascade=orphan", "ไม่มีเจ้าของ", "ลบ Pod เก่าทีหลัง"],
  "'--cascade=orphan' on a ticket in the leaving robot's hand; 'ไม่มีเจ้าของ' above the three old booths (once); "
  "'ลบ Pod เก่าทีหลัง' on the broom icon; no children, no animals, no orphan imagery")

S11 = "11. rollout พัง: อ่านอาการและแก้"
t("failure-modes", S11,
  "อาการพังที่พบบ่อยระหว่าง rollout: ErrImagePull/ImagePullBackOff (image ผิด), 0/1 Running (readiness ล้ม), CrashLoopBackOff (แอปล้มซ้ำ) — อ่านด้วย rollout status, describe deploy แล้ว rollout undo",
  "Three orange booths in a row, each with its own problem: (1) an empty booth frame with an empty delivery cart "
  "and a red X, (2) a booth with a red lamp and no customers, (3) a booth with a circular arrow showing it "
  "collapsing and restarting with a dizzy star. Below them a short debug checklist card with three lines. Nong "
  "Som holds a magnifier near the checklist.",
  ["ImagePullBackOff", "0/1 Running", "CrashLoopBackOff", "rollout status", "describe deploy", "rollout undo"],
  "the three booths carry 'ImagePullBackOff', '0/1 Running', 'CrashLoopBackOff' in order; the checklist has "
  "exactly three lines 'rollout status', 'describe deploy', 'rollout undo'")

S12 = "12. blue/green และ canary ด้วย label + Service"
t("blue-green", S12,
  "blue/green: เปิดชุดบูธใหม่ครบทั้งชุดคู่กับชุดเก่า แล้วสลับ selector ของ Service ทีเดียว ย้อนกลับได้ทันที (ใช้ทรัพยากร 2 เท่า)",
  "Two full rows of booths on two ships: a blue-awning row and a green-awning row. The lighthouse reception "
  "counter has a big switch lever pointing its guiding light at the green row; the blue row stands idle but lit. "
  "Nong Som pulls the lever.",
  ["version=blue", "version=green", "selector: version=green"],
  "'version=blue' above the blue row, 'version=green' above the green row; 'selector: version=green' on the "
  "lever plate of the lighthouse counter", src="T25 25-blue-green.png")
t("canary-by-label", S12,
  "canary: Deployment รุ่นใหม่ 1 replica + รุ่นเดิม 9 replicas ใช้ label app ร่วมกัน Service ส่งลูกค้าไปรุ่นใหม่ราว 10% (สุ่มตามสัดส่วนจำนวน Pod)",
  "Ten booths in a row: nine with blue awnings and one with an orange awning and a small star; all ten share the "
  "same orange luggage tag. The lighthouse counter sends ten customer silhouettes, nine to blue booths and one to "
  "the orange booth. Nong Som watches the orange booth with a notepad. No birds anywhere.",
  ["app=web", "track=stable ×9", "track=canary ×1", "~10%"],
  "'app=web' on the lighthouse counter's selector plate; 'track=stable ×9' above the nine blue booths; "
  "'track=canary ×1' above the orange booth; '~10%' on the arrow to the orange booth; do not draw any canary "
  "bird or any bird at all", src="T26 26-canary-by-label.png")

S13 = "13. สรุปและบทถัดไป"
t("decision-table", S13,
  "ตารางเลือก workload: Pod เดี่ยว (ทดลอง/debug) / ReplicaSet (แทบไม่สร้างเอง) / Deployment RollingUpdate (แอป stateless — ค่าเริ่มต้น) / Deployment Recreate (ห้ามมี 2 รุ่นพร้อมกัน)",
  "A tidy chart board with exactly four rows; each row has a small icon on the left (single booth, teal "
  "supervisor robot, navy manager robot with booths swapping signboards, navy manager robot with all shutters "
  "down) and its label on the right. Nong Som leans on the board with a thumbs up.",
  ["Pod: ทดลอง", "ReplicaSet: ไม่สร้างเอง", "Deployment: แอปทั่วไป", "Recreate: ห้ามมี 2 รุ่น"],
  "exactly four rows and each row has exactly one of the four labels in the listed order; no other text in the "
  "cells", src="T39 39-decision-table.png (แก้)")
t("command-cheatsheet", S13,
  "ตารางคำสั่งสรุปบท: set image, scale, rollout status / history / undo / restart",
  "A cheat-sheet board shaped like the manager robot's logbook opened flat, with six rows, each row with a "
  "small icon (crate, dial, hourglass, logbook, rewind button, refresh arrow). Nong Som holds the board up "
  "proudly in front of the harbor.",
  ["kubectl set image", "kubectl scale", "rollout status", "rollout history", "rollout undo",
   "rollout restart"],
  "exactly six rows, each row has exactly one of the six labels in the listed order; icons carry no text")
t("next-chapter", S13,
  "ปิดบท: เปลี่ยนรุ่นได้ไม่สะดุดและย้อนได้แล้ว แต่ฐานข้อมูลยังลืมทุกอย่างเมื่อ Pod ใหม่ → PVC/StatefulSet, ตั้งค่า/รหัสผ่าน → ConfigMap/Secret, ทางเข้าด้วยชื่อโดเมน → Ingress, ขยายอัตโนมัติ → HPA",
  "The harbor at sunset: the lighthouse shining, the navy manager robot with five booths serving happily. In the "
  "foreground a database booth with an empty storage shelf and a sad drop icon. Four closed treasure chests on "
  "the dock, each with a tag, hint at next chapters. Nong Som waves goodbye.",
  ["PVC / StatefulSet", "ConfigMap / Secret", "Ingress", "HPA"],
  "exactly four chests, each with exactly one of the four labels; the database booth and its shelf have no text",
  allow=True, src="T40 40-next-chapter.png (แก้)")

# ================================================================== LAB
LS0 = "LAB0 เตรียมคลัสเตอร์ พอร์ต และ image"
l("lab0-prepare", LS0,
  "LAB0: เช็กคลัสเตอร์ 3 Node, NodePort 30080 ว่าง (ไม่มี Service ค้างจากบท 006) และ image som-shop-web:1.2 / 1.3 ของบท 006 ยังอยู่บน Node (ถ้าไม่มี build ใหม่ + kind load)",
  "Nong Som at a laptop on the dock; three ships with Ready flags; a gangway door on the control-tower dock with "
  "a free sign; a cargo hold on one ship opened showing two cat-food crates with check marks.",
  ["kubectl get nodes", "Ready", "30080", "som-shop-web:1.2", "som-shop-web:1.3"],
  "'kubectl get nodes' on the laptop screen; 'Ready' flag is drawn once on a flagpole shared by the fleet; "
  "'30080' on the gangway door; the two crates carry 'som-shop-web:1.2' and 'som-shop-web:1.3'",
  src="L01 01-lab0-prepare.png (แก้)")

LS1 = "LAB1 Deployment แรก: deploy → rs → pod"
l("lab1-first-deployment", LS1,
  "LAB1: Deployment web (nginx หน้าเว็บบอกเวอร์ชันและชื่อ Pod) → เห็น deploy → rs → pod, pod-template-hash, strategy default 25%/25% แล้ว scale 3→5→2 (rollout history ยังเป็น revision 1)",
  "Nong Som stands next to the manager robot; a three-level tree card shows manager → one supervisor → booths; "
  "Nong Som turns a dial; the manager's logbook stays on page one.",
  ["deploy/web", "rs/web-<hash>", "--replicas=5", "--replicas=2", "REVISION 1"],
  "'deploy/web' on the manager robot; 'rs/web-<hash>' on the supervisor robot; '--replicas=5' and "
  "'--replicas=2' on two positions of the dial; 'REVISION 1' on the logbook page",
  src="L04 04-lab3-first-deployment.png (แก้)")
l("lab1-rs-scale-reverted", LS1,
  "LAB1 (ต่อ): ลอง scale RS ที่ Deployment เป็นเจ้าของตรง ๆ → ถูกปรับกลับ; ลบ Pod หนึ่งตัว → หัวหน้ากะสร้างแทน (ชื่อใหม่ hash เดิม)",
  "Two small scenes side by side. Left: a staff silhouette turns the supervisor robot's dial up and the manager "
  "robot turns it back. Right: one booth fades with a grey ribbon while the supervisor robot stamps a "
  "replacement booth that carries the same barcode sticker. Nong Som in the middle takes notes.",
  ["kubectl scale rs", "ปรับกลับ", "kubectl delete pod", "Terminating", "Running"],
  "'kubectl scale rs' on the staff ticket and 'ปรับกลับ' on a curved arrow from the manager (left scene); "
  "'kubectl delete pod' on a red button, 'Terminating' on the fading booth, 'Running' on the new booth (right "
  "scene); barcode stickers have no readable text")

LS2 = "LAB2 rolling update + Service ClusterIP: เห็น v1/v2 ปนช่วงสั้น"
l("lab2-rolling-rs", LS2,
  "LAB2: apply web-v2.yaml (nginx 1.28 + VERSION v2) แล้ว watch RS ใหม่เพิ่มทีละ 1 RS เก่าลดทีละ 1 จนเก่าเหลือ 0 (RS เก่ายังอยู่ไว้ undo)",
  "Two supervisor robots side by side with live counters; the old one's booths have blue awnings and decrease, "
  "the new one's booths have orange awnings and increase; a timeline ribbon under them. Nong Som watches through "
  "binoculars.",
  ["nginx:1.27-alpine", "nginx:1.28-alpine", "3 → 0", "0 → 3", "kubectl get rs -w"],
  "'nginx:1.27-alpine' and '3 → 0' under the old robot; 'nginx:1.28-alpine' and '0 → 3' under the new robot; "
  "'kubectl get rs -w' on the ribbon", src="L05 05-lab4-rolling-rs.png")
l("lab2-client-sees-mix", LS2,
  "LAB2 (ต่อ): Pod client ยิง wget http://web วนทุก 0.2 วิ ระหว่าง rollout เห็นคำตอบ v1 และ v2 ปนกันช่วงสั้น ๆ แล้วเหลือ v2 ล้วน — ชื่อ Service web คงเดิมตลอด",
  "A small client booth on the left with a faceless staff silhouette repeatedly sending paper planes to a "
  "lighthouse counter in the middle; the lighthouse forwards them to booths on the right, some blue-awning and "
  "some orange-awning. A long paper receipt strip comes back to the client showing alternating blue and orange "
  "stripes, ending in only orange. Nong Som reads the strip.",
  ["client", "http://web", "web v1", "web v2"],
  "'client' on the client booth; 'http://web' on the lighthouse name plate; 'web v1' on one blue stripe and "
  "'web v2' on one orange stripe of the receipt strip (each once); other stripes are color-only")

LS3 = "LAB3 history / change-cause / undo / pause-resume / restart"
l("lab3-history-undo", LS3,
  "LAB3: ใส่ change-cause ด้วย kubectl annotate ทุกครั้ง ดู rollout history / --revision แล้ว undo --to-revision=2 — revision 2 หายจากรายการกลายเป็นเลขใหม่ (ลืม annotate = ข้อความเดิมถูกสืบทอด)",
  "The manager robot's logbook open on a stand; Nong Som writes on a sticky note; a rewind arrow loops from the "
  "last page back to an earlier page and moves it to the end.",
  ["kubernetes.io/change-cause", "rollout history", "rollout undo --to-revision=2", "1", "3", "4", "5"],
  "the logbook page has exactly four rows labeled '1', '3', '4', '5' from top to bottom; "
  "'kubernetes.io/change-cause' on the sticky note; 'rollout history' on the logbook cover; 'rollout undo "
  "--to-revision=2' on the rewind arrow", nt=True, src="L06 06-lab4-history-undo.png (แก้)")
l("lab3-pause-restart", LS3,
  "LAB3 (ต่อ): pause → set image + set env → resume ได้ revision เดียว; rollout restart = เปลี่ยนแค่ annotation restartedAt ใน template แต่ Pod ใหม่ทุกตัว",
  "Left: the manager robot holds a pause sign while two change cards stack in a tray, then a single resume arrow "
  "produces one new logbook page. Right: the manager stamps a small sticky note onto the blueprint and every "
  "booth is swapped for a fresh identical booth with a sparkle. Nong Som stands between the two scenes.",
  ["rollout pause", "rollout resume", "set image", "set env", "rollout restart", "restartedAt"],
  "left scene: 'rollout pause' on the pause sign, 'rollout resume' on the resume arrow, the two cards carry "
  "'set image' and 'set env'; right scene: 'rollout restart' on a button, 'restartedAt' on the sticky note")

LS4 = "LAB4 เทียบ maxSurge/maxUnavailable และ Recreate"
l("lab4-strategies", LS4,
  "LAB4: Deployment 4 replicas 3 แบบ (rolling.yaml default 25%/25% = +1/−1, nosurge.yaml maxSurge 0/maxUnavailable 1, recreate.yaml) set env แล้ว watch จำนวน Pod สูงสุด/Ready ต่ำสุด",
  "Three horizontal lanes stacked; each lane shows four booth slots changing awning color: lane 1 has up to five "
  "booths at once, lane 2 never more than four with one dark gap, lane 3 has all four dark at the same moment. "
  "Nong Som holds a stopwatch beside the lanes.",
  ["rolling.yaml: max 5, min 3", "nosurge.yaml: max 4, min 3", "recreate.yaml: min 0"],
  "exactly three lanes, each with exactly one of the three labels at its left", nt=True,
  src="L07 07-lab5-strategies.png (แก้)")

LS5 = "LAB5 readinessProbe + minReadySeconds ตัดสิน rollout"
l("lab5-readiness-minready", LS5,
  "LAB5: minReadySeconds 10 ทำให้ AVAILABLE ตาม READY ช้ากว่า 10 วิ; แพตช์ readiness path ผิด → Pod ใหม่ 0/1 Running rollout ค้าง Pod เก่ายังรับลูกค้า → undo",
  "Left: a new booth with a green lamp and an hourglass, and a scoreboard where one number lags behind another. "
  "Right: a new orange booth with a red lamp and no customers while three blue booths keep serving; a red event "
  "ticket hangs from the red lamp. Nong Som presses a rewind button at the far right.",
  ["minReadySeconds: 10", "READY", "AVAILABLE", "0/1 Running", "statuscode: 404", "rollout undo"],
  "left: 'minReadySeconds: 10' on the hourglass, 'READY' and 'AVAILABLE' as the two scoreboard headers (no "
  "numbers); right: '0/1 Running' under the red-lamp booth, 'statuscode: 404' on the red ticket; 'rollout undo' "
  "on the rewind button", nt=True)

LS6 = "LAB6 image ผิด + progressDeadlineSeconds → ProgressDeadlineExceeded แต่ร้านยังขาย"
l("lab6-broken-rollout", LS6,
  "LAB6: set image เป็น tag ที่ไม่มี → ErrImagePull/ImagePullBackOff, rollout status ล้มเมื่อเกิน progressDeadlineSeconds 30 แต่ Service ยังส่งลูกค้าไป Pod เก่า 3 ตัว แล้ว rollout undo",
  "A lighthouse counter on the left keeps sending customers to three blue booths with green lamps; one new orange "
  "booth frame is empty with an empty delivery cart and a red X and gets no customers; an hourglass ran out "
  "above it; Nong Som presses a rewind button.",
  ["nginx:9.99-nope", "ImagePullBackOff", "exceeded its progress deadline", "http://web", "rollout undo"],
  "'nginx:9.99-nope' on the empty cart; 'ImagePullBackOff' under the empty booth; 'exceeded its progress "
  "deadline' on a red ticket from the hourglass; 'http://web' on the lighthouse name plate; 'rollout undo' on the "
  "rewind button", src="L08 08-lab6-broken-rollout.png (แก้)")

LS7 = "LAB7 zero-downtime: hit.sh ผ่าน NodePort เทียบไม่มี/มี preStop"
l("lab7-zero-downtime", LS7,
  "LAB7: hit.sh ยิง 300 ครั้งผ่าน NodePort 30080 ระหว่าง rollout เทียบ 2 รอบ: ไม่มี preStop (อาจมี error เล็กน้อย) กับ preStop sleep 5 + maxUnavailable 0 (คาด 0)",
  "Two scoreboards side by side above two lanes of booths being swapped; a numbered gangway door feeds customers "
  "into both lanes; Nong Som holds a tally counter between them; left lane has a tiny red spark, right lane has "
  "a calm green check.",
  ["no preStop", "errors: 3/300", "preStop 5s + maxUnavailable 0", "errors: 0/300", "30080"],
  "'no preStop' and 'errors: 3/300' on the left scoreboard; 'preStop 5s + maxUnavailable 0' and 'errors: 0/300' "
  "on the right scoreboard; '30080' on the gangway door", nt=True, src="L13 13-lab10-zero-downtime.png (แก้)")

LS8 = "LAB8 ย้าย ReplicaSet → Deployment (รับเลี้ยง / ownerReferences)"
l("lab8-migrate-rs", LS8,
  "LAB8: มี ReplicaSet web (แบบบท 006) อยู่แล้ว → apply Deployment ที่ selector ตรง → ดู ownerReferences ของ RS เดิมชี้ Deployment แล้ว RS เดิมถูก scale 3→0 ระหว่าง rolling (Service ยังตอบตลอด)",
  "A teal supervisor robot without a badge stands with three blue booths; the tall navy manager robot arrives "
  "and clips an owner badge on it; behind, a new supervisor robot stamps orange booths; a lighthouse in front "
  "keeps sending customers. Nong Som checks a terminal card.",
  ["rs/web", "ownerReferences: Deployment", "3 → 0", "0 → 3", "http://web"],
  "'rs/web' on the old robot's chest plate; 'ownerReferences: Deployment' on the badge; '3 → 0' under the blue "
  "booths; '0 → 3' under the orange booths; 'http://web' on the lighthouse name plate; terminal card shows only "
  "grey lines", nt=True)

LS9 = "LAB9 blue/green และ canary ด้วย label + Service"
l("lab9-blue-green-canary", LS9,
  "LAB9: blue/green — Deployment web-blue/web-green + kubectl patch svc เปลี่ยน selector version ทีเดียว; canary — stable 4 + canary 1 ใช้ app=web ร่วมกัน client ยิง 50 ครั้งเห็นรุ่นใหม่ราว 1 ใน 5",
  "Left half: a lighthouse lever switching its light from a blue booth row to a green booth row. Right half: a "
  "second lighthouse sending customers to four blue booths and one orange booth with a small star; a tally "
  "card below. Nong Som pulls the left lever with one paw and holds the tally card with the other. No birds "
  "anywhere.",
  ["kubectl patch svc", "version=green", "track=stable ×4", "track=canary ×1", "~20%"],
  "left: 'kubectl patch svc' on the lever plate, 'version=green' above the green row; right: 'track=stable ×4' "
  "above the blue booths, 'track=canary ×1' above the orange booth, '~20%' on the tally card; never draw a "
  "canary bird or any bird")

LS10 = "LAB10 LAB สุดท้าย: ร้านน้องส้มแบบโปรดักชันจริง (som-shop-v3)"
l("lab10-architecture", LS10,
  "LAB10: สถาปัตยกรรมเป้าหมาย — Deployment som-web 3 บูธ (RollingUpdate maxSurge 1 / maxUnavailable 0, preStop 5 วิ) + Service NodePort 30080 และ Deployment som-db 1 ตัว (Recreate, emptyDir) + Service ClusterIP som-db ใน namespace som-shop",
  "Harbor map with one orange zone. At the zone entrance a dock door; behind it a lighthouse guiding to three web "
  "booths spread on two ships, directed by a tall navy manager robot; the three booths send arrows to a second "
  "smaller lighthouse in front of one database booth that has a storage chest of cat-food cans and its own "
  "smaller manager robot holding a card. Nong Som stands at the entrance welcoming customers.",
  ["som-shop", "30080", "Deployment som-web ×3", "som-db", "Deployment som-db ×1", "Recreate"],
  "'som-shop' on the zone sign; '30080' on the dock door; 'Deployment som-web ×3' above the three web booths; "
  "'som-db' on the small lighthouse name plate; 'Deployment som-db ×1' above the database booth; 'Recreate' on "
  "the card held by the database manager robot", src="L15 15-lab12-architecture.png (แก้)")
l("lab10-start-from-rs", LS10,
  "LAB10 ขั้น 1: เริ่มจากสภาพบท 006 (apply k8s-rs/) — ร้านเปิดด้วย ReplicaSet + Service แต่ยังไม่มีผู้จัดการร้าน เปลี่ยนรุ่นต้องลบ Pod เอง",
  "The same harbor zone: two teal supervisor robots without managers, one with three web booths and one with a "
  "database booth; the lighthouse and dock door already working, customers walking in. A folder on the dock. "
  "Nong Som points at the empty spot where a manager should stand, with a thinking face.",
  ["k8s-rs/", "ReplicaSet som-web", "ReplicaSet som-db", "30080"],
  "'k8s-rs/' on the folder tab; 'ReplicaSet som-web' on the web supervisor's chest plate; 'ReplicaSet som-db' on "
  "the database supervisor's chest plate; '30080' on the dock door; the empty manager spot has no text")
l("lab10-convert-to-deployment", LS10,
  "LAB10 ขั้น 2: apply k8s/ (Deployment ชื่อ/selector เดิม) — som-db แบบ Recreate ปิดก่อนเปิดใหม่ (ข้อมูล emptyDir หาย) แล้ว som-web รับเลี้ยง RS เดิมและแทนบูธทีละตัวระหว่าง hit.sh",
  "Two navy manager robots arrive on the dock: one clips an owner badge on the database supervisor while the "
  "database booth briefly shows a closed shutter and an empty chest; the other clips an owner badge on the web "
  "supervisor while blue web booths are swapped one by one for orange ones. A scoreboard above shows the "
  "request count. Nong Som carries a folder into the zone.",
  ["k8s/", "Recreate", "ownerReferences", "hit.sh", "err=0"],
  "'k8s/' on the folder; 'Recreate' on the database shutter; 'ownerReferences' on the badge clipped onto the web "
  "supervisor (only that badge carries text); 'hit.sh' and 'err=0' on the scoreboard", nt=True)
l("lab10-rollout-1-3", LS10,
  "LAB10 ขั้น 3: rolling update 1.2 → 1.3 (set image web และ db-seed + annotate change-cause) ระหว่าง hit.sh -q 300 ครั้ง — นับแล้วไม่มี error",
  "Booth signboards change from teal theme to orange sunset-market theme one booth at a time; a scoreboard above "
  "shows the count; customers keep flowing through the numbered dock door. Nong Som swaps a signboard on a "
  "ladder.",
  ["เวอร์ชัน 1.2", "เวอร์ชัน 1.3", "hit.sh -q 300", "err=0"],
  "'เวอร์ชัน 1.2' on one teal signboard; 'เวอร์ชัน 1.3' on one orange signboard; other signboards show only theme "
  "colors without text; 'hit.sh -q 300' and 'err=0' on the scoreboard; the dock door has no number",
  nt=True, src="L23 23-lab12-rollout-1-3.png (แก้)")
l("lab10-shop-1-3-page", LS10,
  "LAB10: เปิด http://localhost:30080 บนเครื่องนักศึกษา (Ctrl+F5) เห็นธีม sunset ป้ายเวอร์ชัน 1.3 แบนเนอร์เมนูใหม่ และชื่อ Pod ที่เสิร์ฟ",
  "A laptop screen showing a cat-food shop page with an orange-pink sunset hero banner, a version badge, a new "
  "menu ribbon with a fish-shaped treat icon, and a chip showing the serving Pod name; Nong Som points proudly "
  "at the badge.",
  ["localhost:30080", "เวอร์ชัน 1.3", "เมนูใหม่: ขนมปลาทูน่าอบกรอบ", "som-web-…"],
  "'localhost:30080' on the browser bar; 'เวอร์ชัน 1.3' on the version badge; 'เมนูใหม่: ขนมปลาทูน่าอบกรอบ' on the "
  "ribbon; 'som-web-…' on the Pod chip; product cards show only food pictures without text", nt=True,
  src="L19 19-lab12-open-shop-30080.png (แก้)")
l("lab10-history-undo", LS10,
  "LAB10 ขั้น 4: rollout history เห็น change-cause → rollout undo กลับ 1.2 (ออเดอร์ยังอยู่ เพราะ db ไม่ถูกแตะ) → undo อีกครั้งกลับ 1.3",
  "The manager robot flips the logbook back and then forward again with two curved arrows; booth signboards "
  "change teal then orange. A small order counter on the database chest stays the same. Nong Som presses a "
  "rewind button.",
  ["rollout history", "rollout undo", "เวอร์ชัน 1.2", "เวอร์ชัน 1.3", "orders: 2"],
  "'rollout history' on the logbook cover; 'rollout undo' on the rewind button; 'เวอร์ชัน 1.2' on one teal "
  "signboard and 'เวอร์ชัน 1.3' on one orange signboard; 'orders: 2' on the database chest counter", nt=True,
  src="L24 24-lab12-rollback.png (แก้)")
l("lab10-broken-1-4", LS10,
  "LAB10 ขั้น 5: set image web=som-shop-web:1.4 (tag ไม่มี) → Pod ใหม่ 1 ตัว ImagePullBackOff (maxUnavailable 0 จึงไม่มีบูธเก่าถูกปิด) → ProgressDeadlineExceeded หลัง 60 วิ แต่ hit.sh ยัง ok ทั้งหมด → undo",
  "One new booth frame is empty with an empty delivery cart and a red X; an hourglass ran out; the other three "
  "booths keep serving customers who carry bags of cat food; a scoreboard above stays green. Nong Som points at "
  "the still-open booths with relief, holding a rewind button.",
  ["som-shop-web:1.4", "ImagePullBackOff", "ProgressDeadlineExceeded", "err=0", "rollout undo"],
  "'som-shop-web:1.4' on the empty cart; 'ImagePullBackOff' under the empty booth; 'ProgressDeadlineExceeded' "
  "on the hourglass ticket; 'err=0' on the scoreboard; 'rollout undo' on the button in Nong Som's paw", nt=True,
  src="L25 25-lab12-broken-still-selling.png (แก้)")
l("lab10-scale-3-to-5", LS10,
  "LAB10 ขั้น 6: kubectl scale deploy/som-web --replicas=5 → บูธเพิ่มเป็น 5 EndpointSlice เพิ่มเอง และ rollout history ไม่มี revision ใหม่",
  "Two new booths slide onto the ships next to three existing ones; the lighthouse clipboard grows from three to "
  "five rows with a sparkle; the manager's logbook stays closed on the same page. Nong Som turns a dial.",
  ["--replicas=5", "3 → 5", "EndpointSlice", "ไม่เกิด revision"],
  "'--replicas=5' on the dial; '3 → 5' near the new booths; 'EndpointSlice' as the clipboard title; clipboard rows "
  "are icon-only; 'ไม่เกิด revision' on the closed logbook", src="L21 21-lab12-scale-3-to-5.png (แก้)")
l("lab10-db-lost-restart", LS10,
  "LAB10 ขั้น 7: ลบ Pod db → Deployment สร้างใหม่ แต่ emptyDir ว่าง หน้าเว็บขึ้น 'ร้านกำลังเตรียมสินค้า' (503) → rollout restart deploy/som-web เติมสินค้าใหม่ ออเดอร์เป็น 0 → บทหน้า PVC",
  "The database booth is replaced by a new one, but its storage chest is empty with a little dust puff; the web "
  "booths show a sad empty-shelf sign; Nong Som presses a refresh button that restocks shelves with cat-food "
  "cans; a locked treasure chest on the dock hints at the future fix. Show shelves being stocked with cans; no "
  "plants, no seeds.",
  ["orders: 2", "orders: 0", "503", "rollout restart", "PVC"],
  "'orders: 2' on a faded note beside the old chest; 'orders: 0' on the new empty chest; '503' on the sad "
  "empty-shelf sign; 'rollout restart' on the refresh button; 'PVC' on the locked treasure chest", allow=True,
  nt=True, src="L26 26-lab12-db-pod-lost-data.png (แก้)")
l("lab10-wrap-up", LS10,
  "สรุป LAB สุดท้าย: Deployment ดูแลจำนวนและรุ่น, rolling + preStop ไม่สะดุด, rollout undo ย้อนได้, progress deadline บอกรุ่นพังโดยร้านยังขาย, Recreate สำหรับ db — แต่ db ยังลืมข้อมูล",
  "Checklist board with exactly five ticked rows, each with an icon (manager robot, swapping signboard, rewind "
  "button, hourglass, closed shutter), and one small unticked row at the bottom with a database chest icon and "
  "a question mark. Nong Som gives a big thumbs up with the busy harbor shop behind.",
  ["Deployment", "RollingUpdate + preStop", "rollout undo", "ProgressDeadlineExceeded", "Recreate",
   "db ยังลืมข้อมูล"],
  "exactly six rows: five ticked rows with the first five labels in order, and the unticked bottom row with "
  "'db ยังลืมข้อมูล'", src="L27 27-lab12-wrap-up.png (แก้)")

if __name__ == "__main__":
    imgcommon.main()
