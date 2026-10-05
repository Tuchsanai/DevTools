#!/usr/bin/env python3
"""สร้าง images.json + imagegen-prompts.md ของบท 005 (ReplicaSet, Deployment, Service)"""
import json, os

ROOT = "/root/workspace/DevTools/k/005_kubernetes_replicaset_deployment_service"
OUT_JSON = "/root/workspace/DevTools/k/logs/005_rs_deploy_svc/images.json"

USE_CASE = ("Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai "
            "university DevTools course; must teach the concept correctly at a glance.")
ASSET = ("Asset type: landscape 3:2 educational story illustration for Thai Kubernetes ReplicaSet / Deployment / "
         "Service lesson (README figure, about 1536x1024).")
CHAR = ("Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby "
        "orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, "
        "big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with "
        "a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and "
        "neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly.")
STYLE = ("Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, white background, palette "
         "navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; "
         "matches the chapter 002–004 classroom illustration set. Shared metaphor (keep consistent across the "
         "series): cluster = the whole Kubernetes harbor; container = colored shipping container box; Pod = rounded "
         "translucent teal cabin box that wraps one or more shipping containers and carries one small IP tag, and a "
         "Pod always sits on exactly one ship; in this chapter each Pod box is also a small cat-food shop booth with "
         "a tiny awning; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control "
         "tower on the dock (lab-control-plane); Namespace = a colored zone painted on the harbor map with a zone "
         "sign (chapter 004); a Pod label = a small colored luggage tag tied to the box. New in this chapter: "
         "ReplicaSet = a shift-supervisor robot (small box-shaped teal harbor robot holding a clipboard with a "
         "head-count display) that keeps counting the boxes wearing its tag and adds or removes boxes so the count "
         "always matches; Pod template = a blueprint card / stencil the robot copies boxes from; Deployment = a "
         "store-manager robot (taller navy box-shaped robot with a bow tie and a thick revision logbook) that "
         "directs one or more shift-supervisor robots, one per version; rolling update = swapping booth signboards "
         "one booth at a time while the shop stays open; rollback = flipping the revision logbook back to an "
         "earlier page; Service = a lighthouse-shaped reception counter on the dock with a fixed name plate and a "
         "fixed address plate that sends each customer to one ready booth; EndpointSlice = the clipboard list of "
         "currently open booths pinned on the lighthouse counter; readinessProbe = a green lamp above each booth "
         "(red lamp = not ready, gets no customers); kube-proxy = a direction signpost standing on every ship; "
         "NodePort = a numbered gangway door on every ship that outside customers can walk in through. Robots are "
         "simple friendly machines, never cats; customers and staff are faceless people silhouettes, never cats. "
         "Every cargo item, crate or prop is cat-food-shop related only (kibble bags, cat food cans, fish-shaped "
         "treats, food bowls).")
BASE_CONS = ("only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish "
             "or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; "
             "every sign, card, name plate, row, column, lane, zone or panel that is drawn carries exactly the "
             "listed label assigned to it — no blank signs, no extra signs (only small luggage tags, awnings and "
             "icon rows may be color-only where the constraints explicitly say so); a Pod box is never split across "
             "two ships; numbers appear only where listed")
NO_LATER = ("; do not show Ingress, StatefulSet, PersistentVolume, HorizontalPodAutoscaler or ConfigMap objects or "
            "words")


def prompt(scene, labels, extra="", allow_later=False):
    lab = "; ".join(f'"{l}"' for l in labels)
    cons = BASE_CONS + ("" if allow_later else NO_LATER) + (f"; {extra}" if extra else "") + "."
    return "\n".join([
        USE_CASE, ASSET, f"Scene: {scene}", CHAR, STYLE,
        f"Text (verbatim, exactly {len(labels)} short label instances; a label listed twice appears exactly twice): {lab}.",
        f"Constraints: {cons}",
    ])


T = []  # (slug, section, caption, scene, labels, extra, allow_later, needs_test)
L = []


def t(slug, section, cap, scene, labels, extra="", allow=False, nt=False):
    T.append((slug, section, cap, scene, labels, extra, allow, nt))


def l(slug, section, cap, scene, labels, extra="", allow=False, nt=False):
    L.append((slug, section, cap, scene, labels, extra, allow, nt))


# ================================================================== THEORY
S1 = "1. บทนำ: กล่องเดี่ยวหาย ไม่มีใครสร้างใหม่"
t("opening-lonely-pod-lost", S1,
  "ทบทวนปัญหาจากบท 002–004: Pod เดี่ยวถูกลบหรือ Node ล่มแล้วหายไปเลย ไม่มีใครสร้างใหม่ IP ก็เปลี่ยน และ port-forward ที่ต่อไว้หลุด",
  "Left half: a single teal Pod shop booth on a cargo ship fades away into dotted outline with a puff of smoke; "
  "an empty spot remains. Right half: a new teal booth appears with a different IP tag, and a thin cable that was "
  "plugged into the old booth hangs snapped and sparking. A faceless customer silhouette stands confused holding "
  "an empty food bowl. Nong Som looks worried in the middle, paw on chin.",
  ["บทที่ 5", "10.244.1.7", "10.244.2.9", "port-forward"],
  "'บทที่ 5' is a title banner at the top; '10.244.1.7' is the IP tag on the fading old booth; '10.244.2.9' is the "
  "IP tag on the new booth; 'port-forward' is a small tag on the snapped cable")
t("new-metaphor-legend", S1,
  "อุปมาใหม่ของบทนี้: หัวหน้ากะ = ReplicaSet, ผู้จัดการร้าน = Deployment, ประภาคาร = Service, รายชื่อบูธ = EndpointSlice, ไฟเขียวหน้าบูธ = readinessProbe, ประตูเลขบนเรือ = NodePort",
  "A clean legend board with exactly six illustrated rows; each row has one icon on the left and its Kubernetes "
  "term on the right: (1) a small teal box robot with a clipboard, (2) a taller navy box robot with a bow tie and "
  "a thick logbook, (3) a lighthouse-shaped reception counter, (4) a clipboard list pinned on a counter, (5) a "
  "booth awning with a green lamp, (6) a numbered gangway door on a ship hull. Nong Som points at the board with a "
  "pointer stick.",
  ["ReplicaSet", "Deployment", "Service", "EndpointSlice", "readinessProbe", "NodePort"],
  "exactly six rows and each row has exactly one of the six labels in the order listed; the door in row 6 has no "
  "number")

S2 = "2. Controller และ reconciliation loop"
t("reconcile-loop", S2,
  "หัวใจของ Kubernetes: controller วนเทียบ 'สิ่งที่ต้องการ' (spec) กับ 'สิ่งที่เป็นจริง' (status) แล้วแก้ส่วนต่างไม่รู้จบ",
  "A big circular loop of three arrows around a harbor scene: at the top a wish card showing three booth icons, "
  "at the bottom-right a ship with only two booths, at the bottom-left a small teal supervisor robot adding one "
  "new booth. The three arrow segments carry the three step labels. Nong Som stands beside the loop holding a "
  "stopwatch, smiling.",
  ["desired: 3", "actual: 2", "observe", "diff", "act"],
  "'desired: 3' on the wish card; 'actual: 2' under the ship; 'observe', 'diff', 'act' each on one of the three "
  "arrow segments in clockwise order; no other text")
t("controllers-in-tower", S2,
  "controller ทั้งหลายอยู่ใน kube-controller-manager บนหอบังคับการ เฝ้าดู API server ตลอดเวลาและสั่งงานผ่าน API เท่านั้น",
  "Cutaway of the harbor control tower: inside, an office labeled as the controller manager where three small "
  "robots sit at desks watching a big screen connected by a cable to a central API desk; arrows go only from "
  "robots to the API desk and from the API desk out to the ships. Nong Som peeks through the tower window "
  "from outside.",
  ["kube-controller-manager", "kube-apiserver", "ReplicaSet controller", "Deployment controller",
   "EndpointSlice controller"],
  "the three robots each wear exactly one of the three controller labels on a desk name plate; "
  "'kube-controller-manager' on the office door; 'kube-apiserver' on the central API desk")

S3 = "3. ReplicaSet: หัวหน้ากะที่นับกล่องให้ครบ"
t("rs-anatomy", S3,
  "โครง ReplicaSet 3 ส่วน: replicas (จำนวนที่ต้องมี), selector (นับกล่องที่ป้ายตรง), template (แบบพิมพ์ไว้สร้างกล่องใหม่)",
  "A teal shift-supervisor robot stands in the center holding three items, each with an arrow to a big callout: "
  "a head-count clipboard, a magnifier looking at a colored luggage tag, and a blueprint card showing a booth with "
  "the same luggage tag. Behind it three identical teal booths with matching tags sit on a ship. Nong Som reads "
  "the blueprint with interest.",
  ["replicas: 3", "selector: app=snack", "template", "app=snack"],
  "'replicas: 3' on the clipboard callout; 'selector: app=snack' on the magnifier callout; 'template' on the "
  "blueprint callout; 'app=snack' printed once on the blueprint's luggage tag; the three real booth tags are "
  "plain matching color with no text")
t("rs-self-healing", S3,
  "self-healing: กล่องหายไป 1 หัวหน้ากะนับได้ 2 ไม่ตรงกับ 3 จึงพิมพ์กล่องใหม่จากแบบทันที (ชื่อใหม่ IP ใหม่)",
  "Three-step comic strip in one wide panel (left to right): (1) three booths on a ship, one being lifted away by "
  "a crane and fading; (2) the supervisor robot's clipboard turns orange showing a mismatch; (3) the robot stamps "
  "a brand-new booth out of the blueprint, the new booth has a sparkle. Nong Som claps in the last step.",
  ["1", "2", "3", "3/3", "2/3", "3/3"],
  "'1','2','3' are step numbers in circles above each step; the clipboard shows '3/3' in step 1, '2/3' in step "
  "2 and '3/3' in step 3")
t("rs-counts-by-label", S3,
  "ReplicaSet ไม่ได้จำว่ากล่องไหนเป็นของตัวเองจากชื่อ แต่นับจาก label ที่ตรง selector — กล่องไหนป้ายตรงก็ถูกนับ",
  "The supervisor robot shines a flashlight beam across two ships; booths wearing an orange luggage tag light up "
  "with a check mark, booths wearing a blue tag stay dim. Exactly three orange-tag booths are lit, two blue-tag "
  "booths are dim. Nong Som holds an orange tag and a blue tag comparing them.",
  ["selector: app=snack", "app=snack", "app=drink"],
  "'selector: app=snack' on the flashlight; Nong Som's orange tag reads 'app=snack' and blue tag reads "
  "'app=drink'; the booths' tags are plain colors without text")
t("rs-adopts-stray", S3,
  "กับดักที่ 1: Pod เดี่ยวที่มีอยู่ก่อนและ label ตรง จะถูก ReplicaSet 'รับเลี้ยง' (ใส่ ownerReferences) แล้วสร้างใหม่แค่ส่วนที่ขาด",
  "A lone booth with an orange tag already sits on a ship. The supervisor robot arrives, hangs a small owner "
  "badge on the lone booth and stamps only two new booths from the blueprint. Nong Som looks surprised with a "
  "paw on cheek.",
  ["stray", "ownerReferences: snack-rs", "+2", "replicas: 3"],
  "'stray' is the name card on the lone booth; 'ownerReferences: snack-rs' on the owner badge hung on it; '+2' "
  "near the two new stamped booths; 'replicas: 3' on the robot clipboard")
t("rs-deletes-extra", S3,
  "กับดักที่ 2: สร้าง Pod เดี่ยวที่ label ตรงหลังจาก ReplicaSet มีครบแล้ว → นับได้ 4 เกิน 3 → ReplicaSet ลบทิ้งทันที",
  "Three orange-tag booths stand in a row with the supervisor robot; a fourth orange-tag booth is just being "
  "placed by a faceless sailor silhouette, and the robot immediately lifts it away with a red X. Nong Som facepalms "
  "gently.",
  ["4/3", "stray", "Deleted pod: stray"],
  "'4/3' on the robot clipboard in orange; 'stray' name card on the fourth booth; 'Deleted pod: stray' as a small "
  "event ticket flying from the robot")
t("rs-owner-cascade", S3,
  "ownerReferences: ลบ ReplicaSet แล้ว Pod ลูกถูกลบตาม (cascade) ยกเว้นสั่ง --cascade=orphan ที่ทิ้ง Pod ไว้เป็นกำพร้า",
  "Split panel. Left: the supervisor robot leaves the dock and its three booths dissolve with it, connected by "
  "dotted strings. Right: the robot leaves but the strings are cut with scissors and the three booths stay on "
  "the ship. Nong Som holds the scissors on the right side.",
  ["kubectl delete rs snack-rs", "--cascade=orphan"],
  "'kubectl delete rs snack-rs' as the heading of the left side; '--cascade=orphan' as the heading of the right "
  "side")
t("rs-scale", S3,
  "scale: เปลี่ยนเลข replicas หัวหน้ากะเพิ่มหรือลดกล่องให้ตรงทันที (kubectl scale rs snack-rs --replicas=5)",
  "The supervisor robot turns a big dial on its clipboard; on the left the ship gets two new booths sliding in "
  "(total five), on the right a second scene shows the ship with two booths after turning the dial down. Nong Som "
  "turns the dial together with the robot.",
  ["--replicas=5", "--replicas=2", "5", "2"],
  "'--replicas=5' above the left scene, '--replicas=2' above the right scene; '5' and '2' are the counts on the "
  "dial in each scene")
t("rs-why-not-directly", S3,
  "ทำไมไม่ใช้ ReplicaSet ตรง ๆ: แก้ template (เช่น image ใหม่) แล้ว Pod เดิมไม่เปลี่ยน มีผลเฉพาะ Pod ที่สร้างใหม่ และไม่มีประวัติ/ย้อนรุ่น",
  "The supervisor robot holds a new blueprint showing a version-2 booth with a star; but the three booths on the "
  "ship still are version-1 booths without the star; only a single newly stamped booth has the star. A small "
  "empty logbook stand with a red question mark sits beside the robot. Nong Som shakes head.",
  ["template: v2", "v1", "v1", "v2", "no history"],
  "'template: v2' on the new blueprint; two old booths have 'v1' signboards and the newest booth has 'v2'; the "
  "ship shows exactly three booths total (two 'v1' + one 'v2'); 'no history' on the empty logbook stand")

S4 = "4. Deployment: ผู้จัดการร้านที่เปลี่ยนรุ่นอย่างปลอดภัย"
t("deploy-hierarchy", S4,
  "ลำดับชั้น: Deployment (ผู้จัดการร้าน) → ReplicaSet (หัวหน้ากะ 1 คนต่อ 1 รุ่น) → Pod (บูธ) เราสั่ง Deployment อย่างเดียว",
  "Top: a tall navy store-manager robot with bow tie and logbook. Middle: two teal supervisor robots linked by "
  "lines to the manager; the left one is faded (old version) holding an empty clipboard, the right one is bright. "
  "Bottom: three booths linked to the bright supervisor. Nong Som stands next to the manager giving orders through "
  "a megaphone.",
  ["Deployment: web", "ReplicaSet (old) 0", "ReplicaSet (new) 3", "Pod", "Pod", "Pod"],
  "each of the three booths carries one 'Pod' label; supervisor labels as listed under each supervisor robot")
t("pod-template-hash", S4,
  "pod-template-hash: Deployment ติดป้าย hash ของ template ให้ ReplicaSet และ Pod ของแต่ละรุ่น เพื่อไม่ให้หัวหน้ากะสองรุ่นนับกล่องปนกัน",
  "Two supervisor robots each with their own colored blueprint; each blueprint has a small barcode sticker. "
  "Booths beside each robot carry two tags: the shared orange app tag and a small barcode sticker matching their "
  "own robot. Nong Som compares the two barcode stickers with a magnifier.",
  ["app=web", "pod-template-hash=6f58b8bd67", "pod-template-hash=7c987cc6b4"],
  "'app=web' appears once on a large orange tag held by Nong Som; each hash label appears once on its robot's "
  "blueprint sticker; booth barcode stickers have no readable text; draw barcodes only, no food or hash browns")
t("rolling-update-steps", S4,
  "rolling update ทีละบูธ (replicas 3, ค่า default): สร้างบูธรุ่นใหม่ 1 → พร้อมแล้วปิดบูธรุ่นเก่า 1 → ทำซ้ำจนครบ ร้านไม่ปิดเลย",
  "Five stacked horizontal rows (timeline from top to bottom); each row shows the old supervisor's booths with a "
  "blue awning and the new supervisor's booths with an orange awning: row 1 = 3 blue; row 2 = 3 blue + 1 orange; "
  "row 3 = 2 blue + 2 orange; row 4 = 1 blue + 3 orange; row 5 = 0 blue + 3 orange. Customers keep walking into green-lit booths in every "
  "row. Nong Som rides a small cart along the side swapping signboards.",
  ["old 3 / new 0", "old 3 / new 1", "old 2 / new 2", "old 1 / new 3", "old 0 / new 3"],
  "exactly five rows, each row has exactly one of the five labels on its left in the listed order; the booth "
  "counts in each row match its label exactly; never more than four booths in one row")
t("max-surge-unavailable", S4,
  "maxSurge 25% ปัดขึ้น / maxUnavailable 25% ปัดลง: replicas 10 → เกินได้ 3 (รวมสูงสุด 13) และหายได้ 2 (พร้อมอย่างน้อย 8); replicas 3 → เกิน 1 หาย 0",
  "A ruler-style gauge board with two bars. Top bar: ten booth icons plus three dashed extra booth slots at the "
  "right end. Bottom bar: ten booth icons with two of them dimmed. A small side card shows a three-booth example. "
  "Nong Som points at the ceiling arrow and the floor arrow.",
  ["replicas: 10", "maxSurge 25% → 3 (max 13)", "maxUnavailable 25% → 2 (min 8)", "replicas: 3 → +1 / -0"],
  "exactly 10 solid booth icons per bar; exactly 3 dashed extra slots on the top bar; exactly 2 dimmed booths on "
  "the bottom bar; 'replicas: 3 → +1 / -0' on the small side card")
t("recreate-vs-rolling", S4,
  "RollingUpdate vs Recreate: Recreate ปิดทุกบูธเก่าก่อนแล้วค่อยเปิดรุ่นใหม่ (มีช่วงร้านปิด) เหมาะกับงานที่ห้ามมี 2 รุ่นพร้อมกัน เช่นฐานข้อมูลที่ใช้ volume ร่วม",
  "Two horizontal lanes. Top lane: booths change color one by one, a small open sign stays lit all the time. "
  "Bottom lane: all blue booths close shutters at once, a gap with a closed sign and waiting customer silhouettes, "
  "then orange booths open. Nong Som stands between the lanes holding a little stopwatch.",
  ["RollingUpdate", "Recreate", "OPEN", "CLOSED"],
  "'RollingUpdate' labels the top lane, 'Recreate' the bottom lane; 'OPEN' is the sign on the top lane; 'CLOSED' "
  "is the sign in the gap of the bottom lane")
t("readiness-gates-rollout", S4,
  "readinessProbe และ minReadySeconds คุมจังหวะ rollout: บูธใหม่ต้องไฟเขียว (และเขียวต่อเนื่องตาม minReadySeconds) ก่อนจึงปิดบูธเก่าตัวถัดไป",
  "A new orange booth with its lamp switching from red to green, a small hourglass beside it; next to it the "
  "manager robot waits with a hand raised in a 'wait' gesture before an old blue booth. A second new booth with a "
  "red lamp gets no customers. Nong Som watches the hourglass.",
  ["readinessProbe", "minReadySeconds: 5", "Ready", "0/1"],
  "'readinessProbe' on the lamp of the first new booth; 'minReadySeconds: 5' on the hourglass; 'Ready' under the "
  "green-lit booth; '0/1' under the red-lit booth")
t("progress-deadline", S4,
  "รุ่นใหม่พัง (image tag ผิด → ImagePullBackOff): rollout ค้าง บูธรุ่นเก่ายังเปิดขายครบ เมื่อเกิน progressDeadlineSeconds สถานะเป็น ProgressDeadlineExceeded",
  "Three blue booths with green lamps keep serving customers on the left. On the right one new orange booth "
  "frame is empty because its container crate never arrived: an empty delivery cart with a red X next to it. An "
  "hourglass above it has run out. The manager robot shows a red status card. Nong Som points to the still-busy "
  "blue booths, relieved.",
  ["ImagePullBackOff", "progressDeadlineSeconds: 30", "ProgressDeadlineExceeded", "3/3"],
  "'ImagePullBackOff' under the empty orange booth; 'progressDeadlineSeconds: 30' on the hourglass; "
  "'ProgressDeadlineExceeded' on the manager's red card; '3/3' above the three blue booths")
t("rollout-history", S4,
  "rollout history = สมุดบันทึกรุ่นของผู้จัดการร้าน: แต่ละ revision จำ template ไว้ ข้อความ CHANGE-CAUSE มาจาก annotation kubernetes.io/change-cause",
  "The manager robot opens a thick logbook to a page showing a table with exactly three rows, each row a revision "
  "number and a short note; a sticky note on the cover. Nong Som writes on the sticky note with a pencil.",
  ["REVISION", "CHANGE-CAUSE", "1  v1 nginx 1.27", "2  v2 nginx 1.28", "3  v3 broken",
   "kubernetes.io/change-cause"],
  "table header has 'REVISION' and 'CHANGE-CAUSE'; exactly three rows with the three row labels; "
  "'kubernetes.io/change-cause' on the sticky note on the cover")
t("rollout-undo", S4,
  "rollout undo: ย้อนกลับไปใช้ template ของรุ่นก่อนหน้า — Kubernetes สร้างเป็น revision ใหม่ (เลขเดิมหายจากรายการ) และขยายหัวหน้ากะรุ่นเก่ากลับมา",
  "The manager robot flips the logbook pages backward with a curved arrow; the faded old supervisor robot wakes "
  "up and its blue booths come back, while the orange broken booth shrinks away. A small revision list card "
  "shows that the old page moved to the end. Nong Som presses a big round rewind button.",
  ["kubectl rollout undo", "--to-revision=2", "1", "3", "4"],
  "'kubectl rollout undo' on the rewind button; '--to-revision=2' on the flipping page; the revision list card "
  "has exactly three rows reading '1', '3', '4' from top to bottom")
t("pause-resume", S4,
  "rollout pause / resume: หยุด rollout ชั่วคราวเพื่อแก้หลายอย่างพร้อมกัน แล้ว resume ให้เปลี่ยนรุ่นครั้งเดียว",
  "The manager robot holds a pause sign while three small change cards (an image card, an env card, a resources "
  "card) stack up in a tray; then a resume sign and a single combined rollout arrow. Nong Som stacks the cards.",
  ["kubectl rollout pause", "kubectl rollout resume", "image", "env", "resources"],
  "each change card has exactly one of 'image', 'env', 'resources'")
t("revision-history-limit", S4,
  "revisionHistoryLimit (ค่า default 10): ReplicaSet รุ่นเก่าถูกเก็บไว้ด้วย replicas 0 เพื่อใช้ย้อนรุ่น เกินจำนวนนี้จะถูกลบ",
  "A shelf in the control tower with sleeping teal supervisor robots lined up, each with an empty clipboard; a "
  "shelf sign shows the limit; one robot at the far end is being gently carried out. One awake supervisor robot "
  "with booths stands in front. Nong Som counts the sleeping robots.",
  ["revisionHistoryLimit: 10", "replicas: 0", "replicas: 3"],
  "'revisionHistoryLimit: 10' on the shelf sign; 'replicas: 0' printed once on the shelf edge; sleeping robots "
  "hold their clipboards face-down (no display visible); 'replicas: 3' on the awake robot's clipboard")
t("ways-to-change", S4,
  "เปลี่ยน Deployment ได้หลายทาง: kubectl set image / scale / edit (เร็ว แต่ YAML ใน git ไม่ตรง) vs แก้ไฟล์แล้ว kubectl apply (แนวทางที่แนะนำ)",
  "A control panel with three buttons on the left side and a big folder with a check mark on the right side. "
  "Arrows from all buttons and the folder point to the manager robot. A small warning triangle sits between the "
  "buttons and the folder. Nong Som holds the folder proudly.",
  ["kubectl set image", "kubectl scale", "kubectl edit", "kubectl apply -f"],
  "each of three buttons has one of the first three labels; 'kubectl apply -f' on the folder")

S5 = "5. แนวคิด blue/green และ canary ด้วย label"
t("blue-green", S5,
  "blue/green: เปิดชุดบูธใหม่ครบทั้งชุดคู่กับชุดเก่า แล้วสลับ selector ของ Service ทีเดียว ย้อนกลับได้ทันที",
  "Two full rows of booths on two ships: a blue-awning row and a green-awning row. The lighthouse reception "
  "counter has a big switch lever pointing its guiding light at the green row; the blue row stands idle but lit. "
  "Nong Som pulls the lever.",
  ["version=blue", "version=green", "selector: version=green"],
  "'version=blue' above the blue row, 'version=green' above the green row; 'selector: version=green' on the "
  "lever plate of the lighthouse counter")
t("canary-by-label", S5,
  "canary: Deployment รุ่นใหม่ 1 replica + รุ่นเดิม 9 replicas ใช้ label app ร่วมกัน Service ส่งลูกค้าไปรุ่นใหม่ราว 10% เพื่อทดลองก่อน",
  "Ten booths in a row: nine with blue awnings and one with an orange awning and a small star; all ten share the "
  "same orange luggage tag. The lighthouse counter sends ten customer silhouettes, nine to blue booths and one to "
  "the orange booth. Nong Som watches the orange booth with a notepad. No birds anywhere.",
  ["app=web", "track=stable ×9", "track=canary ×1", "~10%"],
  "'app=web' on the lighthouse counter's selector plate; 'track=stable ×9' above the nine blue booths; "
  "'track=canary ×1' above the orange booth; '~10%' on the arrow to the orange booth; do not draw any canary bird")

S6 = "6. Service: ประภาคารที่มีชื่อและที่อยู่คงที่"
t("why-service", S6,
  "ทำไมต้องมี Service: Pod เกิดใหม่ได้ IP ใหม่ตลอด ลูกค้าจำ IP ไม่ไหว → Service ให้ชื่อและ ClusterIP คงที่แล้วส่งต่อไปยัง Pod ที่พร้อม",
  "Left: a confused customer silhouette holding a list of crossed-out IP tags while booths keep changing. Right: "
  "a lighthouse-shaped reception counter on the dock with a name plate and an address plate; customers line up "
  "calmly and the light beam guides them to three booths. Nong Som stands at the counter as the greeter.",
  ["10.244.1.4", "10.244.2.8", "web", "10.96.47.123"],
  "'10.244.1.4' and '10.244.2.8' are crossed-out tags on the customer's list; 'web' on the lighthouse name plate; "
  "'10.96.47.123' on the lighthouse address plate")
t("selector-endpointslice", S6,
  "selector → EndpointSlice: Service เลือก Pod ด้วย label เหมือน ReplicaSet แล้วระบบเขียนรายชื่อ IP:port ของบูธที่เปิดอยู่ลงใน EndpointSlice",
  "The lighthouse counter has a clipboard pinned on its side listing three booth entries with green dots; dotted "
  "lines connect each entry to a booth with an orange tag on two ships. A small EndpointSlice robot updates the "
  "clipboard. Nong Som reads the clipboard.",
  ["selector: app=web", "EndpointSlice", "10.244.1.4:80", "10.244.2.7:80", "10.244.2.8:80"],
  "'selector: app=web' on the lighthouse; 'EndpointSlice' as the clipboard title; exactly three clipboard rows "
  "with the three IP:port labels")
t("clusterip-ports", S6,
  "ClusterIP และพอร์ต 3 ชื่อ: port (พอร์ตของ Service) → targetPort (พอร์ตของ container) และ nodePort (ประตูบนเรือ เฉพาะ type NodePort)",
  "A clear diagram: a customer arrow enters a numbered gangway door on a ship hull, continues to the lighthouse "
  "counter, then to a booth's service window. Each stop has one port plate. Nong Som traces the path with a paw.",
  ["nodePort: 30080", "port: 80", "targetPort: 3000", "ClusterIP"],
  "'nodePort: 30080' on the gangway door; 'port: 80' on the lighthouse; 'targetPort: 3000' on the booth window; "
  "'ClusterIP' as the type badge on the lighthouse roof")
t("service-dns", S6,
  "DNS ของ Service: ชื่อสั้น web ใช้ได้ใน namespace เดียวกัน ข้าม namespace ใช้ web.shop หรือชื่อเต็ม web.shop.svc.cluster.local (ต่อจากบท 004)",
  "A harbor map with two colored zones: an orange zone with a lighthouse and a teal zone with a customer booth "
  "sending a carrier message. Three address envelopes show increasing detail; the shortest envelope bounces back "
  "from the zone border with a red X, the two longer ones reach the lighthouse with green checks. Nong Som holds the "
  "envelopes.",
  ["shop", "kitchen", "web", "web.shop", "web.shop.svc.cluster.local"],
  "'shop' is the orange zone sign (the lighthouse zone), 'kitchen' the teal zone sign (the sender's zone); "
  "'web' is the bounced envelope; 'web.shop' and 'web.shop.svc.cluster.local' are the delivered envelopes")
t("kube-proxy-signposts", S6,
  "kube-proxy (โหมด iptables ใน kind) ติดตั้งป้ายบอกทางบนเรือทุกลำ: แพ็กเก็ตที่ส่งไป ClusterIP ถูกแปลงปลายทางเป็น IP ของ Pod ที่พร้อมตั้งแต่บนเรือต้นทาง",
  "The control tower dock and two worker ships side by side; the dock and each ship have one identical "
  "direction signpost with three arrows (three signposts total). A message bottle addressed to the lighthouse is redirected by the "
  "signpost on its own ship straight to a booth on another ship, never passing through the lighthouse building. "
  "Nong Som adjusts one signpost.",
  ["kube-proxy", "kube-proxy", "kube-proxy", "iptables", "10.96.47.123 → 10.244.2.8"],
  "each of the three signposts has one 'kube-proxy' label; 'iptables' on a small rule sheet in Nong Som's paw; "
  "'10.96.47.123 → 10.244.2.8' on the message bottle; the ships and tower are unlabeled")
t("load-distribution", S6,
  "การกระจายโหลด: kube-proxy เลือก Pod แบบสุ่ม ไม่ใช่วนตามลำดับ ยิงน้อยครั้งอาจไม่โดนครบทุกตัว; sessionAffinity: ClientIP ให้ลูกค้าคนเดิมไปบูธเดิม",
  "Left: a bar chart made of stacked cat food cans over three booths showing uneven heights 5, 4 and 0 from nine "
  "customers. Right: one customer silhouette with a membership card always walking to the same booth along a "
  "highlighted path. Nong Som looks at the chart with a curious face.",
  ["9 requests", "5", "4", "0", "sessionAffinity: ClientIP"],
  "'9 requests' as chart title; '5','4','0' above the three can stacks; 'sessionAffinity: ClientIP' on the right "
  "side membership card")
t("nodeport", S6,
  "NodePort: เปิดประตูหมายเลขเดียวกัน (ช่วง 30000–32767) บนทุก Node; kind ของเรา map port 30080 ของเครื่องนักศึกษาเข้าประตู 30080 ของ lab-control-plane จึงเปิด localhost:30080 ได้ตรง ๆ",
  "A student's laptop on the left with a browser; a cable goes to the dock building of the control tower, which "
  "has a numbered gangway door; the two worker ships also have the same numbered door. Inside, arrows lead to the "
  "lighthouse counter and then to booths. Nong Som waves from the laptop side.",
  ["localhost:30080", "30080", "30080", "30080", "30000–32767"],
  "'localhost:30080' on the laptop browser bar; each of the three doors (control tower dock, lab-worker ship, "
  "lab-worker2 ship) has one '30080' label; '30000–32767' on a small range ruler under the doors")
t("loadbalancer-pending", S6,
  "LoadBalancer: บนคลาวด์ได้ IP ภายนอกจากผู้ให้บริการ แต่ใน kind ไม่มีตัวจัดสรร EXTERNAL-IP จึงค้าง <pending> (ยังได้ nodePort ให้ใช้)",
  "Left: a large cloud-provider pier crane handing a big public address plate to a lighthouse. Right: the kind "
  "harbor lighthouse with an empty plate holder and a small spinning hourglass; below it a gangway door still "
  "works. Nong Som shrugs with a smile.",
  ["type: LoadBalancer", "EXTERNAL-IP <pending>", "80:30456/TCP"],
  "'type: LoadBalancer' as the heading; 'EXTERNAL-IP <pending>' on the empty plate holder on the right; "
  "'80:30456/TCP' on the working gangway door on the right; the left plate has no readable text")
t("externalname-headless", S6,
  "Service แบบพิเศษ: ExternalName = ป้ายชี้ไปชื่อ DNS ภายนอก (ไม่มี ClusterIP) / clusterIP: None (headless) = ไม่มีเคาน์เตอร์กลาง DNS ตอบ IP ของทุก Pod",
  "Split panel. Left: a signpost at the edge of the harbor pointing out to sea toward a distant supplier island. "
  "Right: a phone-book board listing three booth addresses directly with no lighthouse counter in front of the "
  "booths. Nong Som stands between both panels. All figures are normal people silhouettes with heads.",
  ["ExternalName", "example.com", "clusterIP: None", "10.244.1.7", "10.244.1.8", "10.244.2.15"],
  "'ExternalName' heading left and 'example.com' on the signpost arrow; 'clusterIP: None' heading right; the "
  "phone-book board has exactly three rows with the three IP labels; never draw headless people")
t("selector-mismatch-debug", S6,
  "Service ที่ selector พิมพ์ผิด: ไม่มีบูธไหนตรง EndpointSlice ว่าง เรียกแล้ว Connection refused — ตรวจด้วย get endpointslice, เทียบ label ของ Pod",
  "The lighthouse counter shows an empty clipboard; its selector plate has a typo tag that does not match the "
  "orange tags on the booths; a customer silhouette bounces back with a red X. Nong Som holds a magnifier next to "
  "the selector plate and a booth tag side by side.",
  ["selector: app=wbe", "app=web", "ENDPOINTS <unset>", "Connection refused"],
  "'selector: app=wbe' on the lighthouse plate; 'app=web' on one booth tag highlighted by the magnifier; "
  "'ENDPOINTS <unset>' on the empty clipboard; 'Connection refused' on the red X bubble near the customer")
t("readiness-endpoints", S6,
  "readinessProbe กับ endpoints: บูธไฟแดงยังอยู่ในรายชื่อแต่ ready=false จึงไม่ได้ลูกค้า (คอลัมน์ ENDPOINTS ยังแสดง IP ครบ — ต้องดู conditions)",
  "Three booths: two with green lamps receive customers, one with a red lamp gets none. The lighthouse clipboard "
  "lists all three IPs with a check or cross beside each. Nong Som points at the cross mark.",
  ["10.244.1.7 ready=true", "10.244.1.8 ready=true", "10.244.2.15 ready=false", "0/1"],
  "exactly three clipboard rows with the three listed labels; '0/1' above the red-lamp booth")
t("zero-downtime", S6,
  "zero-downtime rollout: readinessProbe + maxUnavailable: 0 + preStop sleep ให้บูธเก่าเลิกรับลูกค้าใหม่ก่อนปิดจริง ทดสอบด้วยการยิงคำขอวนแล้วนับ error",
  "A wide timeline of an old booth being closed: first its name is removed from the lighthouse list, then the "
  "booth keeps serving the last customer during a short hourglass wait, then the shutter closes. Above, a "
  "counter board tracks requests and errors. Nong Som holds a tally counter.",
  ["preStop sleep 5s", "maxUnavailable: 0", "readinessProbe", "errors: 0"],
  "'preStop sleep 5s' on the hourglass; 'maxUnavailable: 0' on the manager card at the left; 'readinessProbe' "
  "on the green lamp of a new booth; 'errors: 0' on the counter board")

S7 = "7. สรุปและบทถัดไป"
t("decision-table", S7,
  "ตารางเลือกใช้: Pod เดี่ยว (ทดลอง) / ReplicaSet (แทบไม่สร้างเอง) / Deployment (แอป stateless) / Service ClusterIP (คุยภายใน) / NodePort (เปิดออกนอกใน LAB) / LoadBalancer (คลาวด์)",
  "A tidy two-column chart board with exactly six rows; each row has a small icon (single booth, supervisor robot, "
  "manager robot, lighthouse, numbered door, cloud crane) and its label. Nong Som leans on the board with a "
  "thumbs up.",
  ["Pod", "ReplicaSet", "Deployment", "ClusterIP", "NodePort", "LoadBalancer"],
  "exactly six rows and each row has exactly one of the six labels; no other text in the cells")
t("next-chapter", S7,
  "ปูทางบทถัดไป: ร้านเปิดหลายบูธได้แล้ว แต่ฐานข้อมูลยังหายเมื่อ Pod ถูกสร้างใหม่ → PVC/StatefulSet, ทางเข้าด้วยชื่อโดเมน → Ingress, ตั้งค่า → ConfigMap/Secret, ขยายอัตโนมัติ → HPA",
  "The harbor at sunset: the lighthouse shining, three booths serving happily. In the foreground a database booth "
  "with an empty storage shelf and a sad drop icon. Four closed treasure chests on the dock, each with a tag, "
  "hint at next chapters. Nong Som waves goodbye.",
  ["PVC / StatefulSet", "Ingress", "ConfigMap/Secret", "HPA"],
  "exactly four chests, each with exactly one of the four labels; the database booth and its shelf have no text",
  allow=True)

# ================================================================== LAB
LS0 = "LAB0 เตรียมคลัสเตอร์ ไฟล์ และ image"
l("lab0-prepare", LS0,
  "LAB0: เช็กคลัสเตอร์ 3 Node, ดูว่า NodePort 30080 ยังไม่มีใครใช้ (kubectl get svc -A) และเตรียม image (nginx ให้ Node pull เอง, som-shop-web ต้อง kind load)",
  "Nong Som at a laptop on the dock; three ships with Ready flags; a gangway door on the control-tower dock "
  "with a free sign; a delivery cart loading a cat-food crate onto the ships. ",
  ["kubectl get nodes", "Ready", "30080", "kind load docker-image"],
  "'Ready' flag is drawn once on a flagpole shared by the fleet; '30080' on the gangway door; 'kind load "
  "docker-image' on the delivery cart")

LS1 = "LAB1 ReplicaSet แรก + self-healing"
l("lab1-rs-self-heal", LS1,
  "LAB1: สร้าง ReplicaSet snack-rs 3 ตัว ลบ Pod ทิ้งหนึ่งตัวแล้วดูตัวใหม่เกิดภายในไม่กี่วินาที พร้อมดู ownerReferences และ scale",
  "Nong Som deletes a booth with a big red button; the supervisor robot is already stamping a replacement booth; "
  "a terminal card shows a short pod list with one Terminating row. ",
  ["kubectl delete pod", "Terminating", "Running", "snack-rs"],
  "'snack-rs' on the robot's chest plate; 'Terminating' on the old fading booth; 'Running' on the new booth; "
  "'kubectl delete pod' on the red button")

LS2 = "LAB2 กับดัก label: รับเลี้ยงและลบ Pod เกิน"
l("lab2-label-trap", LS2,
  "LAB2: Pod stray ที่ label ตรงถูกลบทันทีเมื่อ RS ครบแล้ว แต่ถ้ามีอยู่ก่อนจะถูกรับเลี้ยง; ลบ RS แล้ว Pod ลูกหายตาม",
  "Two small scenes side by side. Left: a stray booth placed next to three booths is lifted away by the robot. "
  "Right: a stray booth already on the ship receives an owner badge from an arriving robot and only two new booths "
  "appear. Nong Som in the center shrugs with both paws.",
  ["after RS: deleted", "before RS: adopted", "stray", "stray"],
  "'after RS: deleted' heading left, 'before RS: adopted' heading right; each stray booth has one 'stray' name "
  "card")

LS3 = "LAB3 Deployment แรก + scale"
l("lab3-first-deployment", LS3,
  "LAB3: Deployment web (nginx หน้าเว็บบอกชื่อ Pod) → เห็น deploy → rs → pod และ pod-template-hash แล้ว scale 3→5→2; ลอง scale RS ตรง ๆ แล้ว Deployment ปรับกลับ",
  "Nong Som stands next to the manager robot; a three-level tree card shows manager → one supervisor → booths; "
  "Nong Som turns a dial; a supervisor robot that someone else tried to adjust is being turned back by the "
  "manager.",
  ["deploy/web", "rs/web-6f58b8bd67", "--replicas=5", "--replicas=2"],
  "'deploy/web' on the manager robot; 'rs/web-6f58b8bd67' on the supervisor robot; '--replicas=5' and "
  "'--replicas=2' on two positions of the dial")

LS4 = "LAB4 Rolling update + history + undo"
l("lab4-rolling-rs", LS4,
  "LAB4: kubectl set image nginx:1.28-alpine แล้ว watch เห็น RS ใหม่เพิ่มทีละ 1 RS เก่าลดทีละ 1 จนเก่าเหลือ 0",
  "Two supervisor robots side by side with live counters; the old one's booths have blue awnings and decrease, "
  "the new one's booths have orange awnings and increase; a timeline ribbon under them. Nong Som watches through "
  "binoculars.",
  ["nginx:1.27-alpine", "nginx:1.28-alpine", "3 → 0", "0 → 3", "kubectl get rs -w"],
  "'nginx:1.27-alpine' and '3 → 0' under the old robot; 'nginx:1.28-alpine' and '0 → 3' under the new robot; "
  "'kubectl get rs -w' on the ribbon")
l("lab4-history-undo", LS4,
  "LAB4 (ต่อ): ใส่ change-cause ทุกครั้ง ดู rollout history แล้ว undo — สังเกตว่า revision ที่ย้อนไปได้เลขใหม่",
  "The manager robot's logbook open on a stand; Nong Som writes on a sticky note; a rewind arrow loops from the "
  "last page back to an earlier page and moves it to the end.",
  ["kubernetes.io/change-cause", "rollout history", "rollout undo", "1", "3", "4"],
  "the logbook page has exactly three rows labeled '1', '3', '4'; 'kubernetes.io/change-cause' on the sticky "
  "note; 'rollout history' on the logbook cover; 'rollout undo' on the rewind arrow")

LS5 = "LAB5 เทียบ maxSurge/maxUnavailable และ Recreate"
l("lab5-strategies", LS5,
  "LAB5: Deployment 4 replicas เปลี่ยนรุ่นด้วย 3 แบบ (default 25%/25% = +1/-1, maxSurge 0/maxUnavailable 1, Recreate) แล้ว watch จำนวน Pod เทียบกัน",
  "Three horizontal lanes stacked; each lane shows four booth slots changing awning color: lane 1 has up to five "
  "booths at once, lane 2 never more than four with one dark gap, lane 3 has all four dark at the same moment. "
  "Nong Som holds a stopwatch beside the lanes.",
  ["25% / 25% → max 5, min 3", "maxSurge 0 / maxUnavailable 1", "Recreate"],
  "exactly three lanes, each with exactly one of the three labels at its left")

LS6 = "LAB6 rollout พัง: image ผิด + readiness ล้ม แล้ว rollback"
l("lab6-broken-rollout", LS6,
  "LAB6: set image เป็น tag ที่ไม่มี → ErrImagePull/ImagePullBackOff, rollout status ล้มเพราะเกิน progressDeadlineSeconds แต่ Pod เก่า 3 ตัวยังรับลูกค้า แล้ว rollout undo",
  "Three blue booths with green lamps keep serving; one new orange booth frame is empty with an empty delivery "
  "cart and a red X; an hourglass ran out above it; Nong Som presses a rewind button. ",
  ["nginx:9.99-nope", "ImagePullBackOff", "exceeded its progress deadline", "rollout undo"],
  "'nginx:9.99-nope' on the empty cart; 'ImagePullBackOff' under the empty booth; 'exceeded its progress "
  "deadline' on a red ticket from the hourglass; 'rollout undo' on the rewind button")

LS7 = "LAB7 Service ClusterIP + DNS + การกระจายโหลด"
l("lab7-clusterip-dns", LS7,
  "LAB7: สร้าง Service web แล้วจาก Pod client เรียก http://web 30 ครั้ง นับชื่อ Pod ที่ตอบด้วย sort | uniq -c เห็นกระจายแบบสุ่ม",
  "A client booth sends a stream of message bottles to the lighthouse; the lighthouse guides them to three booths; "
  "a tally board with three bars of slightly different heights. Nong Som writes the tally.",
  ["client", "web", "10.96.47.123", "sort | uniq -c"],
  "'client' on the sender booth; 'web' on the lighthouse name plate; '10.96.47.123' on the lighthouse address "
  "plate; 'sort | uniq -c' as the tally board title; the bars have no numbers")

LS8 = "LAB8 debug Service ที่ไม่มี endpoints"
l("lab8-debug-endpoints", LS8,
  "LAB8: Service web-typo selector ผิด → EndpointSlice ว่าง Connection refused; targetPort ผิด; Pod ไม่ ready → ready=false ไล่ debug ทีละขั้น",
  "Nong Som as a detective with a magnifier follows a three-step checklist board beside an empty lighthouse "
  "clipboard. ",
  ["1 get endpointslice", "2 get pods --show-labels", "3 targetPort", "Connection refused"],
  "exactly three checklist rows with the first three labels; 'Connection refused' on a red bubble near the "
  "lighthouse")

LS9 = "LAB9 NodePort 30080 จาก browser บนเครื่องนักศึกษา"
l("lab9-nodeport-browser", LS9,
  "LAB9: เปลี่ยน Service เป็น NodePort 30080 แล้วเปิด http://localhost:30080 บนเครื่องนักศึกษาได้ทันที ไม่ต้อง port-forward หรือ ssh -L",
  "Nong Som at home desk with a laptop; a dotted path from the laptop through a door to the control-tower dock "
  "door, then to the lighthouse and booths; a crossed-out old tunnel pipe in the corner.",
  ["localhost:30080", "30080", "port-forward"],
  "'localhost:30080' on the laptop browser bar; '30080' on the dock door; 'port-forward' on the crossed-out "
  "tunnel pipe", nt=True)
l("lab9-keepalive-vs-curl", LS9,
  "LAB9 (ต่อ): กด refresh ใน browser มักเห็นชื่อ Pod เดิม (keep-alive ใช้ connection เดิม) ส่วน curl วน 30 ครั้งเห็นหลาย Pod",
  "Split panel. Left: a browser window with a single solid rope tied to one booth, the same booth highlighted "
  "three times. Right: a terminal with many short arrows fanning to three booths. Nong Som compares both.",
  ["browser", "keep-alive", "curl ×30"],
  "'browser' heading left with 'keep-alive' on the rope; 'curl ×30' heading right", nt=True)

LS10 = "LAB10 zero-downtime rollout ระหว่างยิงคำขอวน"
l("lab10-zero-downtime", LS10,
  "LAB10: ยิงคำขอวนระหว่าง rollout แล้วนับ error เทียบ 2 รอบ: ไม่มี preStop (อาจมี error เล็กน้อย) กับ preStop sleep + maxUnavailable: 0 (คาด 0)",
  "Two scoreboards side by side above two lanes of booths being swapped; Nong Som holds a tally counter between "
  "them; left lane has a tiny red spark, right lane has a calm green check.",
  ["no preStop", "errors: 3/300", "preStop + maxUnavailable 0", "errors: 0/300"],
  "'no preStop' and 'errors: 3/300' on the left scoreboard; 'preStop + maxUnavailable 0' and 'errors: 0/300' on "
  "the right scoreboard", nt=True)

LS11 = "LAB11 ข้าม namespace ด้วย DNS"
l("lab11-cross-namespace", LS11,
  "LAB11: Pod ใน namespace kitchen เรียก web (ไม่เจอ) แล้วเรียก web.shop และ web.shop.svc.cluster.local ได้; ดู search domain ใน resolv.conf",
  "Harbor map with two painted zones; a teal-zone booth sends three envelopes to the orange-zone lighthouse; the "
  "first bounces with a red X at the border, two arrive with green checks. Nong Som reads a small resolv card.",
  ["kitchen", "shop", "web", "web.shop", "web.shop.svc.cluster.local"],
  "'kitchen' on the teal zone sign, 'shop' on the orange zone sign; the three envelopes carry 'web' (bounced), "
  "'web.shop' and 'web.shop.svc.cluster.local' (delivered); the resolv card has no text")

LS12 = "LAB12 LAB สุดท้าย: ร้านน้องส้มแบบโปรดักชันจริงครั้งแรก"
l("lab12-architecture", LS12,
  "LAB12: สถาปัตยกรรมร้าน — web Deployment 3 บูธ + Service NodePort 30080 ให้ลูกค้าภายนอก และ db Deployment 1 ตัว (Recreate, emptyDir) + Service ClusterIP som-db ใน namespace som-shop",
  "Harbor map with one orange zone. At the zone entrance a dock door; behind it a lighthouse guiding to three web "
  "booths spread on two ships; the three booths send arrows to a second smaller lighthouse in front of one "
  "database booth that has a storage chest of cat-food cans. Nong Som stands at the entrance welcoming customers.",
  ["som-shop", "30080", "som-web ×3", "som-db", "som-db ×1"],
  "'som-shop' on the zone sign; '30080' on the dock door; 'som-web ×3' above the three web booths; 'som-db' on "
  "the small lighthouse name plate; 'som-db ×1' above the database booth")
l("lab12-build-images", LS12,
  "LAB12: build som-shop-web:1.2 และ 1.3 จากโค้ดเดียว (build-arg เวอร์ชัน/ธีม) แล้ว kind load ให้ทุก Node; postgres ใช้ kind load image-archive",
  "A small workshop on the dock: two identical crates come out of one machine, one with a teal ribbon and one "
  "with an orange ribbon; a delivery cart carries them toward three ships. Nong Som operates the machine.",
  ["som-shop-web:1.2", "som-shop-web:1.3", "kind load docker-image", "postgres:17.11-alpine"],
  "'som-shop-web:1.2' on the teal-ribbon crate; 'som-shop-web:1.3' on the orange-ribbon crate; 'kind load "
  "docker-image' on the cart; 'postgres:17.11-alpine' on a third plain crate already on the cart")
l("lab12-db-service", LS12,
  "LAB12: db = Deployment replicas 1, strategy Recreate, ข้อมูลอยู่ใน emptyDir; Service ClusterIP som-db ให้ web เรียกด้วยชื่อ som-db:5432",
  "A database booth with a storage chest; a small lighthouse in front with a name plate; a strategy card pinned on "
  "the booth; web booths in the background calling the name. Nong Som checks the chest.",
  ["som-db:5432", "strategy: Recreate", "emptyDir", "replicas: 1"],
  "'som-db:5432' on the small lighthouse; 'strategy: Recreate' on the pinned card; 'emptyDir' on the storage "
  "chest; 'replicas: 1' on a supervisor robot's clipboard beside the booth")
l("lab12-stock-shelves-once", LS12,
  "LAB12: web 3 replicas เริ่มพร้อมกัน initContainer เติมสินค้าเข้าฐานข้อมูลพร้อมกัน 3 ตัว — 1.2 ใช้ advisory lock ให้เข้าคิวทีละตัว และ ON CONFLICT DO NOTHING จึงไม่ซ้ำ",
  "Three helper robots each carrying a crate of cat-food cans queue in a single line at a storage room door with "
  "a turnstile; only the first enters, the shelves inside are already full for the later ones who just check and "
  "leave. Nong Som holds the turnstile key. Show shelves being stocked with cans; no plants, no seeds, no "
  "gardening.",
  ["pg_advisory_xact_lock", "ON CONFLICT DO NOTHING", "new: 6", "new: 0", "new: 0"],
  "'pg_advisory_xact_lock' on the turnstile; 'ON CONFLICT DO NOTHING' on the shelf sign; the three robots carry "
  "receipt cards 'new: 6' (first), 'new: 0', 'new: 0'", nt=True)
l("lab12-open-shop-30080", LS12,
  "LAB12: เปิด http://localhost:30080 บนเครื่องนักศึกษา หน้าร้านแสดงป้ายเวอร์ชัน 1.2 และชื่อ Pod ที่เสิร์ฟ",
  "A laptop screen showing a cat-food shop page with a hero banner (Nong Som's photo avatar), a version badge and a "
  "footer chip with a Pod name; Nong Som points proudly at the badge.",
  ["localhost:30080", "เวอร์ชัน 1.2", "som-web-7b44f6c986-4nhz6"],
  "'localhost:30080' on the browser bar; 'เวอร์ชัน 1.2' on the version badge; 'som-web-7b44f6c986-4nhz6' on the "
  "footer chip; product cards show only food pictures without text", nt=True)
l("lab12-curl-loop-balance", LS12,
  "LAB12: curl วน 30 ครั้งที่ /api/whoami เห็นคำตอบจากทั้ง 3 Pod (สุ่ม ไม่เท่ากันเป๊ะ)",
  "A terminal card with three result rows, each with a bar of cans; arrows from the dock door fan to three booths "
  "with matching colors. Nong Som counts on paws.",
  ["curl /api/whoami ×30", "som-web-…-4nhz6", "som-web-…-ccxvw", "som-web-…-pn7qs"],
  "exactly three result rows, each with one Pod label; bars have no numbers", nt=True)
l("lab12-scale-3-to-5", LS12,
  "LAB12: kubectl scale deploy/som-web --replicas=5 → บูธเพิ่มเป็น 5 รายชื่อใน EndpointSlice เพิ่มตามอัตโนมัติ",
  "Two new booths slide onto the ships next to three existing ones; the lighthouse clipboard grows from three to "
  "five rows with a sparkle. Nong Som turns a dial.",
  ["--replicas=5", "3 → 5", "EndpointSlice"],
  "'--replicas=5' on the dial; '3 → 5' near the new booths; 'EndpointSlice' as the clipboard title; clipboard rows "
  "are icon-only")
l("lab12-delete-web-pod", LS12,
  "LAB12: ลบ Pod web หนึ่งตัวระหว่างร้านเปิด → ReplicaSet สร้างแทนทันที ลูกค้ายังสั่งซื้อได้",
  "One web booth fades away while the supervisor robot stamps a replacement; customers keep entering the other "
  "green-lit booths. Nong Som holds a shopping basket, still smiling.",
  ["kubectl delete pod", "5/5"],
  "'kubectl delete pod' on a small ticket held by Nong Som; '5/5' on the supervisor robot clipboard")
l("lab12-rollout-1-3", LS12,
  "LAB12: rolling update เป็น 1.3 (ธีมใหม่ ป้ายเวอร์ชัน 1.3) ระหว่างยิงคำขอวน — นับแล้วไม่มี error",
  "Booth signboards change from teal theme to orange night-market theme one booth at a time; a scoreboard above "
  "shows the count; customers keep flowing. Nong Som swaps a signboard on a ladder.",
  ["เวอร์ชัน 1.2", "เวอร์ชัน 1.3", "errors: 0"],
  "'เวอร์ชัน 1.2' on one teal signboard; 'เวอร์ชัน 1.3' on one orange signboard; other signboards show only "
  "theme colors without text; 'errors: 0' on the scoreboard", nt=True)
l("lab12-rollback", LS12,
  "LAB12: rollout undo กลับไป 1.2 แล้ว rollout history เห็นเลข revision ใหม่",
  "The manager robot flips the logbook back; teal signboards return on the booths. Nong Som presses a rewind "
  "button.",
  ["rollout undo", "เวอร์ชัน 1.2"],
  "'rollout undo' on the rewind button; 'เวอร์ชัน 1.2' on one returning teal signboard")
l("lab12-broken-still-selling", LS12,
  "LAB12: จำลองเวอร์ชันพัง (image tag 1.4 ไม่มี) rollout ค้างเกิน progressDeadlineSeconds แต่ร้านยังขายได้จาก Pod เดิม แล้ว rollout undo",
  "One new booth frame is empty with an empty delivery cart and a red X; an hourglass ran out; the other booths "
  "keep serving customers who carry bags of cat food. Nong Som points at the still-open booths with relief.",
  ["som-shop-web:1.4", "ImagePullBackOff", "ProgressDeadlineExceeded", "rollout undo"],
  "'som-shop-web:1.4' on the empty cart; 'ImagePullBackOff' under the empty booth; 'ProgressDeadlineExceeded' "
  "on the hourglass ticket; 'rollout undo' on a button in Nong Som's paw", nt=True)
l("lab12-db-pod-lost-data", LS12,
  "LAB12: ลบ Pod db → Deployment สร้างใหม่ใน ~4 วินาที แต่ emptyDir ว่าง ออเดอร์และสินค้าหาย (ร้านขึ้นข้อความว่ายังไม่พร้อม) ต้อง rollout restart web เพื่อเติมสินค้าใหม่ → บทหน้าใช้ PVC",
  "The database booth is replaced by a new one, but its storage chest is empty with a little dust puff; the web "
  "booths show a sad empty-shelf sign; a locked treasure chest on the dock hints at the future fix. Nong Som "
  "looks surprised.",
  ["orders: 2", "orders: 0", "rollout restart", "PVC"],
  "'orders: 2' on a faded note beside the old chest; 'orders: 0' on the new empty chest; 'rollout restart' on a "
  "button near the web booths; 'PVC' on the locked treasure chest", allow=True, nt=True)
l("lab12-wrap-up", LS12,
  "สรุป LAB สุดท้าย: Deployment ดูแลจำนวนและรุ่น, Service ให้ชื่อคงที่และกระจายโหลด, NodePort เปิดร้านสู่ภายนอก, readiness + preStop ทำให้เปลี่ยนรุ่นไม่สะดุด",
  "Checklist board with exactly five ticked rows, each with an icon (manager robot, logbook, lighthouse, numbered "
  "door, green lamp). Nong Som gives a big thumbs up with the busy harbor shop behind.",
  ["Deployment", "rollout undo", "Service", "NodePort 30080", "readinessProbe"],
  "exactly five rows, each with one label")


def build(items, kind):
    out = []
    for i, (slug, sec, cap, scene, labels, extra, allow, nt) in enumerate(items, 1):
        assert len(labels) <= 6, slug
        sub = "01_Theory" if kind == "T" else "02_LAB"
        d = {
            "id": f"{kind}{i:02d}",
            "path": f"{ROOT}/{sub}/images/{i:02d}-{slug}.png",
            "section": sec,
            "caption_th": cap,
            "prompt": prompt(scene.strip(), labels, extra, allow),
        }
        if nt:
            d["needs_test"] = True
        out.append(d)
    return out


def write_md(items, title, path):
    lines = ["Generated with built-in image_gen via cyolo1 using 00-character-som.png as character reference", "",
             f"# Final image prompts — 005 Kubernetes ReplicaSet, Deployment และ Service ({title})", "",
             "ทุกภาพแนบ `01_Theory/images/00-character-som.png` เป็นภาพอ้างอิงตัวละครน้องส้ม", ""]
    for it in items:
        nt = " · needs_test (สร้าง/ปรับหลังทดสอบ LAB จริง)" if it.get("needs_test") else ""
        lines += [f"## {os.path.basename(it['path'])}", "",
                  f"> {it['id']} · {it['section']} — {it['caption_th']}{nt}", "",
                  "```text", it["prompt"], "```", ""]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    th, lb = build(T, "T"), build(L, "L")
    data = th + lb
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    write_md(th, "Theory", f"{ROOT}/01_Theory/images/imagegen-prompts.md")
    write_md(lb, "LAB", f"{ROOT}/02_LAB/images/imagegen-prompts.md")
    print(len(th), len(lb))
    for d in data:
        print(d["id"], os.path.basename(d["path"]), "needs_test" if d.get("needs_test") else "")
