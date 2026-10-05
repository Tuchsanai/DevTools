#!/usr/bin/env python3
"""storyboard ภาพบท 005 Kubernetes ReplicaSet (แยกจากบทรวม logs/005_rs_deploy_svc)

รัน: python3 build_images.py → images.json, image-sources.tsv,
     005_kubernetes_replicaset/01_Theory/images/imagegen-prompts.md, 02_LAB/images/imagegen-prompts.md
src = ที่มาจากบทรวม ("T06 06-rs-self-healing.png", ต่อท้าย " (แก้)" ถ้าปรับ prompt) หรือ "new"
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import imgcommon  # noqa: E402
from imgcommon import t, l  # noqa: E402

imgcommon.configure("005")

# ================================================================== THEORY
S1 = "1. บทนำ: บูธเดี่ยวหาย ไม่มีใครสร้างใหม่"
t("opening-lonely-pod-lost", S1,
  "ทบทวนปัญหาจากบท 002–004: Pod เดี่ยวถูกลบหรือ Node ล่มแล้วหายไปเลย ไม่มีใครสร้างใหม่ IP ก็เปลี่ยน และ port-forward ที่ต่อไว้หลุด",
  "Left half: a single teal Pod shop booth on a cargo ship fades away into a dotted outline with a puff of smoke; "
  "an empty spot remains. Right half: a new teal booth that Nong Som rebuilt by hand appears with a different IP "
  "tag, and a thin cable that was plugged into the old booth hangs snapped and sparking. A faceless customer "
  "silhouette stands confused holding an empty food bowl. Nong Som stands in the middle, tired, holding a small "
  "hammer, paw on chin. At the far right edge a small teal box-shaped robot with a clipboard peeks in from behind "
  "a crate as a hint of the new helper.",
  ["บทที่ 5", "10.244.1.7", "10.244.2.9", "port-forward"],
  "'บทที่ 5' is a title banner at the top; '10.244.1.7' is the IP tag on the fading old booth; '10.244.2.9' is the "
  "IP tag on the new booth; 'port-forward' is a small tag on the snapped cable; the peeking robot has no text",
  src="T01 01-opening-lonely-pod-lost.png (แก้)")
t("recap-three-chapters", S1,
  "สามปัญหาที่ค้างมาจากบทก่อน: บท 002 ลบ Pod แล้วหายถาวร, บท 003 drain/เรือล่มแล้ว Pod เดี่ยวไม่ย้ายไปเรือลำอื่น, บท 004 Pod ใหม่ได้ IP ใหม่และ port-forward หลุด",
  "Three equal comic panels side by side, each with a chapter tab on top. Panel 1: a hand presses a red delete "
  "button and a booth vanishes, leaving an empty spot. Panel 2: two cargo ships, the left ship is being emptied "
  "for repair and its booth simply disappears; the right ship receives nothing. Panel 3: a cable from a laptop to "
  "a booth is snapped. Nong Som walks under the panels looking at them one by one, worried.",
  ["บท 002", "บท 003", "บท 004", "kubectl delete pod", "drain", "port-forward"],
  "'บท 002', 'บท 003', 'บท 004' are the three panel tabs in order left to right; 'kubectl delete pod' on the red "
  "button in panel 1; 'drain' on a small sign on the left ship in panel 2; 'port-forward' on the snapped cable in "
  "panel 3")
t("metaphor-legend", S1,
  "อุปมาใหม่ของบทนี้: หัวหน้ากะ = ReplicaSet, แบบพิมพ์ = Pod template, แว่นขยายส่องป้าย = selector, ป้ายเจ้าของบนบูธ = ownerReferences, หุ่นยนต์ในหอที่วนตรวจ = controller",
  "A clean legend board with exactly five illustrated rows; each row has one icon on the left and its term on the "
  "right: (1) a small teal box robot holding a clipboard with a head-count display, (2) a blueprint card showing "
  "a booth outline, (3) a magnifier looking at a colored luggage tag, (4) a small owner badge clipped on a booth "
  "corner, (5) a robot at a desk inside the control tower with a circular arrow. Nong Som points at the board "
  "with a pointer stick.",
  ["ReplicaSet", "Pod template", "selector", "ownerReferences", "controller"],
  "exactly five rows and each row has exactly one of the five labels in the order listed; the icons have no text",
  src="T02 02-new-metaphor-legend.png (แก้)")

S2 = "2. Controller และ reconciliation loop"
t("reconcile-loop", S2,
  "หัวใจของ Kubernetes: controller วนเทียบ 'สิ่งที่ต้องการ' (spec) กับ 'สิ่งที่เป็นจริง' (status) แล้วแก้ส่วนต่างไม่รู้จบ",
  "A big circular loop of three arrows around a harbor scene: at the top a wish card showing three booth icons, "
  "at the bottom-right a ship with only two booths, at the bottom-left a small teal supervisor robot adding one "
  "new booth. The three arrow segments carry the three step labels. Nong Som stands beside the loop holding a "
  "stopwatch, smiling.",
  ["desired: 3", "actual: 2", "observe", "diff", "act"],
  "'desired: 3' on the wish card; 'actual: 2' under the ship; 'observe', 'diff', 'act' each on one of the three "
  "arrow segments in clockwise order; no other text",
  src="T03 03-reconcile-loop.png")
t("controllers-in-tower", S2,
  "controller ทั้งหลายอยู่ใน kube-controller-manager (static Pod ใน kube-system) บนหอบังคับการ เฝ้าดู (watch) ผ่าน kube-apiserver และสั่งงานผ่าน API เท่านั้น ไม่คุยกับเรือตรง ๆ",
  "Cutaway of the harbor control tower: inside, an office where three small robots sit at desks watching a big "
  "screen connected by a cable to a central API desk; arrows go only from robots to the API desk and from the API "
  "desk out to the ships at sea. Nong Som peeks through the tower window from outside.",
  ["kube-controller-manager", "kube-apiserver", "ReplicaSet controller", "Node controller",
   "Namespace controller"],
  "the three robots each wear exactly one of the three controller labels on a desk name plate; "
  "'kube-controller-manager' on the office door; 'kube-apiserver' on the central API desk",
  src="T04 04-controllers-in-tower.png (แก้)")
t("level-triggered", S2,
  "level-triggered: controller ไม่ได้พึ่งการ 'ได้ยินเหตุการณ์' ทุกครั้ง แต่เทียบสภาพปัจจุบันทุกรอบ แม้พลาดข่าวไป (เช่น controller เพิ่งรีสตาร์ต) รอบถัดไปก็แก้ได้ถูก",
  "Two-part scene. Left: the supervisor robot is briefly switched off (a small power plug unplugged) while a booth "
  "on the ship disappears and a news ticket about it flies past unseen. Right: the robot is back on, looks at the "
  "ship through binoculars, counts the booths on its clipboard and stamps a new booth. Nong Som plugs the cable "
  "back in on the left side.",
  ["watch", "level-triggered", "desired 3", "actual 2"],
  "'watch' on the missed news ticket on the left; 'level-triggered' as the heading above the right part; "
  "'desired 3' and 'actual 2' as two lines on the robot's clipboard on the right")

S3 = "3. ReplicaSet manifest: replicas, selector, template"
t("rs-anatomy", S3,
  "โครง ReplicaSet 3 ส่วน: replicas (จำนวนที่ต้องมี), selector (นับกล่องที่ป้ายตรง), template (แบบพิมพ์ไว้สร้างกล่องใหม่)",
  "A teal shift-supervisor robot stands in the center holding three items, each with an arrow to a big callout: "
  "a head-count clipboard, a magnifier looking at a colored luggage tag, and a blueprint card showing a booth with "
  "the same luggage tag. Behind it three identical teal booths with matching tags sit on a ship. Nong Som reads "
  "the blueprint with interest.",
  ["replicas: 3", "selector: app=snack", "template", "app=snack"],
  "'replicas: 3' on the clipboard callout; 'selector: app=snack' on the magnifier callout; 'template' on the "
  "blueprint callout; 'app=snack' printed once on the blueprint's luggage tag; the three real booth tags are "
  "plain matching color with no text",
  src="T05 05-rs-anatomy.png")
t("rs-yaml-map", S3,
  "อ่าน YAML ของ ReplicaSet: apiVersion apps/v1, kind ReplicaSet แล้ว spec มี replicas, selector และ template (ข้างใน template คือ Pod spec ที่คุ้นเคยจากบท 002)",
  "A large rounded YAML card on the left drawn as five colored horizontal bands (no code text other than the "
  "labels), each band connected by a colored arrow to an object on the right: the robot's chest plate, the robot "
  "badge, the clipboard, the magnifier, and the blueprint. Inside the blueprint a tiny booth with containers is "
  "visible. Nong Som traces the arrows with a paw.",
  ["apiVersion: apps/v1", "kind: ReplicaSet", "replicas: 3", "selector", "template"],
  "each of the five bands of the YAML card carries exactly one label in the listed order top to bottom; the "
  "objects on the right have no text")
t("pod-naming", S3,
  "template ไม่มี metadata.name: ReplicaSet ตั้งชื่อ Pod เป็น <ชื่อ RS>-<สุ่ม 5 ตัว> ทุกตัวชื่อไม่ซ้ำ และตัวใหม่ได้ชื่อใหม่เสมอ",
  "The supervisor robot stamps booths out of a blueprint whose name field is an empty dashed box; three booths "
  "come out on a conveyor, each with a name card made of the robot's name plus a short random code. Nong Som "
  "reads the name cards, amused.",
  ["snack-rs", "snack-rs-4xk9p", "snack-rs-b7tqz", "snack-rs-zm2wd", "name: (none)"],
  "'snack-rs' on the robot's chest plate; the three booth name cards read 'snack-rs-4xk9p', 'snack-rs-b7tqz', "
  "'snack-rs-zm2wd' left to right; 'name: (none)' next to the empty dashed box on the blueprint")
t("match-expressions", S3,
  "selector 2 แบบ: matchLabels (เท่ากับ) และ matchExpressions ที่ใช้ตัวดำเนินการ In / NotIn / Exists / DoesNotExist (ใช้คู่กันได้ ต้องตรงทุกข้อ)",
  "A magnifier control panel with two sections: a simple top section with one equality tag, and a bottom section "
  "with four operator buttons, each button shows a tiny icon: (In) a tag entering a circle, (NotIn) a tag "
  "blocked from a circle, (Exists) a tag with a check mark, (DoesNotExist) an empty tag hook with a cross. Nong "
  "Som presses one of the buttons.",
  ["matchLabels", "matchExpressions", "In", "NotIn", "Exists", "DoesNotExist"],
  "'matchLabels' heads the top section; 'matchExpressions' heads the bottom section; each of the four buttons "
  "carries exactly one of 'In', 'NotIn', 'Exists', 'DoesNotExist'")
t("selector-template-mismatch", S3,
  "label ใน template ต้องตรงกับ selector ไม่งั้น API server ไม่รับ (เพราะ ReplicaSet จะสร้าง Pod ที่ตัวเองนับไม่เห็นไปเรื่อย ๆ)",
  "The robot hands its blueprint to the API desk clerk robot in the tower; the blueprint's luggage tag is a "
  "different color from the robot's magnifier tag; the clerk stamps a big red rejection stamp. A ghostly endless "
  "line of booths in the background shows what would happen otherwise. Nong Som looks at the two tags side by "
  "side.",
  ["selector: app=snack", "app=snak", "selector does not match template labels"],
  "'selector: app=snack' on the robot's magnifier; 'app=snak' on the blueprint tag; 'selector does not match "
  "template labels' inside the red stamp",
  nt=True)
t("owner-references", S3,
  "ownerReferences: ทุก Pod ที่ ReplicaSet สร้างหรือรับเลี้ยงมีป้ายเจ้าของชี้กลับไปที่ RS (ค่าจริงจาก pre-check #4)",
  "Close-up of a booth with a small owner badge clipped on its corner, enlarged in a magnified circle that shows "
  "four short lines; a dotted string runs from the badge back to the supervisor robot. Nong Som holds a magnifier "
  "over the badge.",
  ["ownerReferences", "kind: ReplicaSet", "name: snack-rs", "controller: true", "blockOwnerDeletion: true"],
  "'ownerReferences' as the title of the magnified circle; the other four labels are the four lines inside it in "
  "the listed order")
t("rs-status-columns", S3,
  "อ่านสถานะ: kubectl get rs แสดง DESIRED / CURRENT / READY และ status มี replicas, readyReplicas, availableReplicas, fullyLabeledReplicas",
  "The robot's back has a scoreboard with three big columns; below, on the ship, three booths: two with a green "
  "lamp and one with a red lamp still warming up. A side card lists two extra status fields. Nong Som reads the "
  "scoreboard with a cup of tea.",
  ["DESIRED 3", "CURRENT 3", "READY 2", "availableReplicas", "fullyLabeledReplicas"],
  "the three scoreboard columns carry 'DESIRED 3', 'CURRENT 3', 'READY 2' left to right; the side card lists "
  "'availableReplicas' and 'fullyLabeledReplicas'; lamps have no text")

S4 = "4. Self-healing: ลบ Pod, drain และเรือล่ม"
t("rs-self-healing", S4,
  "self-healing: กล่องหายไป 1 หัวหน้ากะนับได้ 2 ไม่ตรงกับ 3 จึงพิมพ์กล่องใหม่จากแบบทันที (ชื่อใหม่ IP ใหม่)",
  "Three-step comic strip in one wide panel (left to right): (1) three booths on a ship, one being lifted away by "
  "a crane and fading; (2) the supervisor robot's clipboard turns orange showing a mismatch; (3) the robot stamps "
  "a brand-new booth out of the blueprint, the new booth has a sparkle. Nong Som claps in the last step.",
  ["1", "2", "3", "3/3", "2/3", "3/3"],
  "'1','2','3' are step numbers in circles above each step; the clipboard shows '3/3' in step 1, '2/3' in step "
  "2 and '3/3' in step 3",
  src="T06 06-rs-self-healing.png")
t("delete-overlap-terminating", S4,
  "ลบ Pod ของ ReplicaSet: ตัวใหม่ถูกสร้างภายในราว 3 วินาที ขณะที่ตัวเก่ายัง Terminating อยู่ (RS ไม่นับ Pod ที่กำลังถูกลบ)",
  "A horizontal timeline ruler across the ship. On the left an old booth with a fading outline and closing "
  "shutters; directly next to it, overlapping in time, a new booth being stamped by the robot. A small stopwatch "
  "above the overlap. A big red button on the dock. Nong Som holds the stopwatch.",
  ["kubectl delete pod", "Terminating", "Running", "~3 วิ"],
  "'kubectl delete pod' on the red button; 'Terminating' under the old booth; 'Running' under the new booth; "
  "'~3 วิ' on the stopwatch")
t("drain-single-vs-rs", S4,
  "เทียบบท 003: drain เรือที่มี Pod เดี่ยว → Pod หายไปเลย, drain เรือที่มี Pod ของ ReplicaSet → หัวหน้ากะสร้างตัวแทนบนเรืออีกลำทันที (และไม่ต้องใช้ --force)",
  "Two horizontal lanes. Top lane: ship lab-worker2 under repair scaffolding, a single booth without an owner "
  "badge vanishes into dotted outline, ship lab-worker next to it stays empty. Bottom lane: the same repair, "
  "booths with owner badges leave lab-worker2 and the supervisor robot stamps the same number of new booths on "
  "lab-worker. Nong Som stands between the lanes with a wrench.",
  ["Pod เดี่ยว: หาย", "ReplicaSet: สร้างใหม่", "kubectl drain lab-worker2", "lab-worker", "lab-worker2"],
  "'Pod เดี่ยว: หาย' heads the top lane; 'ReplicaSet: สร้างใหม่' heads the bottom lane; 'kubectl drain "
  "lab-worker2' on a work-order card held by Nong Som; 'lab-worker' and 'lab-worker2' appear once each as hull "
  "names on the bottom lane ships only; the top lane ships have no hull text")
t("node-down-timeline", S4,
  "เรือล่ม (docker stop lab-worker2): Node เป็น NotReady หลังราว 50 วิ แล้ว Pod ต้องรอ tolerationSeconds (ค่าเริ่มต้น 300) ก่อนถูกไล่ RS จึงสร้างแทนบนเรืออื่น ใส่ toleration 30 วิใน template ให้เร็วขึ้นได้",
  "A long horizontal timeline. At the start a ship sinking into fog; then a marker where the ship turns grey; "
  "then two branches: a long hourglass bar and a short hourglass bar, each ending at a point where the robot "
  "stamps a new booth on the other healthy ship. The old booth stays as a faded outline on the sunk ship. Nong "
  "Som holds the short hourglass and smiles.",
  ["docker stop lab-worker2", "NotReady ~50 วิ", "tolerationSeconds: 300", "tolerationSeconds: 30", "สร้างแทน"],
  "'docker stop lab-worker2' at the start; 'NotReady ~50 วิ' at the grey marker; 'tolerationSeconds: 300' on the "
  "long hourglass bar; 'tolerationSeconds: 30' on the short one; 'สร้างแทน' once near the newly stamped booth",
  nt=True)

S5 = "5. Scale: เพิ่ม ลด และลบตัวไหนก่อน"
t("rs-scale", S5,
  "scale: เปลี่ยนเลข replicas หัวหน้ากะเพิ่มหรือลดกล่องให้ตรงทันที (kubectl scale, แก้ไฟล์แล้ว apply, kubectl edit หรือ scale เป็น 0)",
  "The supervisor robot turns a big dial on its clipboard; on the left the ship gets two new booths sliding in "
  "(total five), on the right a second scene shows the ship with two booths after turning the dial down. Nong Som "
  "turns the dial together with the robot.",
  ["--replicas=5", "--replicas=2", "5", "2"],
  "'--replicas=5' above the left scene, '--replicas=2' above the right scene; '5' and '2' are the counts on the "
  "dial in each scene",
  src="T11 11-rs-scale.png")
t("scale-down-order", S5,
  "scale ลงแล้ว RS เลือกลบ Pod ที่ 'เสียน้อยที่สุด' ก่อน: ยังไม่ได้วางบนเรือ > Pending > ไม่ Ready > อยู่เรือที่แออัดกว่า > เพิ่ง Ready/ใหม่กว่า",
  "A sorting line of five booths in front of the robot, ordered from left to right; the robot holds a "
  "priority card and a crane hook hovers above the leftmost booth. Booth 1 floats on the dock not yet on a ship, "
  "booth 2 is still assembling, booth 3 has a red lamp, booth 4 sits on a crowded ship, booth 5 is shiny new. "
  "Nong Som follows the order with a pointer.",
  ["ยังไม่ได้วางบนเรือ", "Pending", "ไม่ Ready", "เรือแออัด", "ใหม่กว่า", "ลบก่อน"],
  "booths 1 to 5 carry the first five labels in order left to right; 'ลบก่อน' on the crane hook above booth 1",
  nt=True)

S6 = "6. กับดัก label"
t("rs-counts-by-label", S6,
  "ReplicaSet ไม่ได้จำว่ากล่องไหนเป็นของตัวเองจากชื่อ แต่นับจาก label ที่ตรง selector — กล่องไหนป้ายตรงก็ถูกนับ",
  "The supervisor robot shines a flashlight beam across two ships; booths wearing an orange luggage tag light up "
  "with a check mark, booths wearing a blue tag stay dim. Exactly three orange-tag booths are lit, two blue-tag "
  "booths are dim. Nong Som holds an orange tag and a blue tag comparing them.",
  ["selector: app=snack", "app=snack", "app=drink"],
  "'selector: app=snack' on the flashlight; Nong Som's orange tag reads 'app=snack' and blue tag reads "
  "'app=drink'; the booths' tags are plain colors without text",
  src="T07 07-rs-counts-by-label.png")
t("rs-adopts-stray", S6,
  "กับดักที่ 1: Pod เดี่ยวที่มีอยู่ก่อนและ label ตรง จะถูก ReplicaSet 'รับเลี้ยง' (ใส่ ownerReferences) แล้วสร้างใหม่แค่ส่วนที่ขาด — แม้ Pod นั้นจะหน้าตาต่างจาก template",
  "A lone booth with an orange tag and a differently colored awning already sits on a ship. The supervisor robot "
  "arrives, clips a small owner badge on the lone booth and stamps only two new booths from the blueprint; the "
  "two new booths have the blueprint's awning color, different from the lone booth. Nong Som looks surprised with "
  "a paw on cheek.",
  ["stray", "ownerReferences: snack-rs", "+2", "replicas: 3"],
  "'stray' is the name card on the lone booth; 'ownerReferences: snack-rs' on the owner badge clipped on it; '+2' "
  "near the two new stamped booths; 'replicas: 3' on the robot clipboard",
  src="T08 08-rs-adopts-stray.png (แก้)")
t("rs-deletes-extra", S6,
  "กับดักที่ 2: สร้าง Pod เดี่ยวที่ label ตรงหลังจาก ReplicaSet มีครบแล้ว → นับได้ 4 เกิน 3 → ReplicaSet ลบทิ้งทันที (pre-check #2)",
  "Three orange-tag booths stand in a row with the supervisor robot; a fourth orange-tag booth is just being "
  "placed by a faceless sailor silhouette, and the robot immediately lifts it away with a red X. Nong Som facepalms "
  "gently.",
  ["4/3", "stray", "Deleted pod: stray"],
  "'4/3' on the robot clipboard in orange; 'stray' name card on the fourth booth; 'Deleted pod: stray' as a small "
  "event ticket flying from the robot",
  src="T09 09-rs-deletes-extra.png")
t("overlapping-selectors", S6,
  "กับดักที่ 3: สอง ReplicaSet ที่ selector ทับกัน — ownerReferences กันไม่ให้แย่ง Pod ที่มีเจ้าของแล้ว แต่ Pod ไร้เจ้าของจะถูกตัวที่เร็วกว่ารับไป และ get pods -l ดูปนกันจนงง",
  "Two teal supervisor robots with different chest plates stand on the same dock, both pointing magnifiers at the "
  "same row of orange-tag booths. Each booth carries a small owner badge in the color of one robot: three badges "
  "match the left robot, two match the right robot. A tangle of dotted strings between them. Nong Som scratches "
  "her head between the robots.",
  ["rs-a", "rs-b", "selector: app=snack", "selector: app=snack", "ownerReferences"],
  "'rs-a' on the left robot's chest plate; 'rs-b' on the right robot's; each robot's magnifier shows one "
  "'selector: app=snack'; 'ownerReferences' once as a callout pointing to one badge; other badges are color only")
t("unlabel-for-debug", S6,
  "เทคนิค debug: ถอด label ออกจาก Pod ที่มีปัญหา (kubectl label pod <ชื่อ> app-) → หลุดจาก RS, RS สร้างตัวแทนทันที ส่วน Pod เดิมยังอยู่พร้อม log/สถานะให้ตรวจ",
  "Nong Som unties an orange luggage tag from a booth with a red warning lamp and wheels the booth onto a small "
  "inspection bench on the side of the dock where a magnifier and a log scroll wait. The owner badge string "
  "falls off. Meanwhile the supervisor robot stamps a fresh replacement booth into the empty spot in the row.",
  ["kubectl label pod snack-rs-4xk9p app-", "debug", "+1"],
  "'kubectl label pod snack-rs-4xk9p app-' on a card in Nong Som's paw; 'debug' on the inspection bench sign; "
  "'+1' near the fresh replacement booth")

S7 = "7. selector แก้ไม่ได้ และ template ใหม่ไม่เปลี่ยน Pod เดิม"
t("selector-immutable", S7,
  "ใน apps/v1 selector ของ ReplicaSet แก้ไม่ได้หลังสร้าง (field is immutable) ถ้าต้องเปลี่ยนต้องสร้าง RS ใหม่",
  "The robot's magnifier is bolted to its arm with a big padlock. Nong Som tries to swap the luggage tag inside "
  "the magnifier for a different color; a red rejection stamp from the API desk lands next to it.",
  ["selector", "field is immutable", "apps/v1"],
  "'selector' on the padlock; 'field is immutable' inside the red stamp; 'apps/v1' on a small plate on the robot's "
  "arm",
  nt=True)
t("template-change-old-pods", S7,
  "แก้ template (เช่น image ใหม่) แล้ว Pod เดิมไม่เปลี่ยน มีผลเฉพาะ Pod ที่สร้างใหม่ ต้องลบ Pod เองทีละตัวจึงได้รุ่นใหม่ และไม่มีประวัติให้ย้อน — งานนี้คือเหตุผลของ Deployment (บท 007)",
  "The supervisor robot holds a new blueprint showing a booth with a star; but the three booths on the ship are "
  "still old booths without the star, except one booth that Nong Som just deleted by hand and that came back "
  "freshly stamped with the star. Nong Som wipes sweat while holding a small delete button, looking tired.",
  ["template: nginx:1.28-alpine", "1.27", "1.27", "1.28", "ลบเองทีละตัว"],
  "'template: nginx:1.28-alpine' on the new blueprint; two old booths have '1.27' signboards and the newest booth "
  "has '1.28'; the ship shows exactly three booths total; 'ลบเองทีละตัว' on the small delete button",
  src="T12 12-rs-why-not-directly.png (แก้)")

S8 = "8. ลบ ReplicaSet: cascade และ orphan"
t("rs-delete-cascade", S8,
  "ลบ ReplicaSet: background (ค่าเริ่มต้น — ลบ RS ทันทีแล้ว garbage collector ลบ Pod ตาม), foreground (ลบ Pod ก่อนแล้ว RS ค่อยหาย), orphan (ทิ้ง Pod ไว้ ถอดป้ายเจ้าของออก)",
  "Three vertical panels with the same harbor. Panel 1: the robot leaves first and its booths dissolve after it "
  "along dotted strings. Panel 2: the booths dissolve first while the robot waits holding a small hourglass, then "
  "leaves. Panel 3: the robot leaves, the strings are cut with scissors and the three booths stay on the ship "
  "without owner badges. Nong Som holds the scissors in panel 3. Booths without badges are ordinary booths, never "
  "children or animals.",
  ["kubectl delete rs snack-rs", "--cascade=background", "--cascade=foreground", "--cascade=orphan"],
  "'kubectl delete rs snack-rs' as a banner across the top; the three panel headings are '--cascade=background', "
  "'--cascade=foreground', '--cascade=orphan' left to right; never draw waterfalls",
  src="T10 10-rs-owner-cascade.png (แก้)")
t("orphan-readopt", S8,
  "Pod ที่ถูกทิ้งไว้ (orphan) ไม่มีเจ้าของ ถ้าสร้าง RS ใหม่ที่ selector ตรง RS ใหม่จะรับเลี้ยง (ติดป้ายเจ้าของ) โดยไม่สร้าง Pod เพิ่ม",
  "Three booths without owner badges on a ship. A new supervisor robot walks up and clips an owner badge on each "
  "booth one by one; its stamping machine stays idle with a zero counter. Nong Som hands the robot the badges. "
  "Booths are ordinary booths, never children or animals.",
  ["ownerReferences: (none)", "snack-rs", "+0", "replicas: 3"],
  "'ownerReferences: (none)' on a small sign in front of the unbadged booths; 'snack-rs' on the new robot's chest "
  "plate; '+0' on the idle stamping machine counter; 'replicas: 3' on the robot's clipboard")

S9 = "9. ReplicationController: รุ่นพี่ที่เกษียณแล้ว"
t("replicationcontroller-history", S9,
  "ReplicationController (v1) คือรุ่นก่อน ReplicaSet: selector ได้แค่แบบเท่ากับ และเคยเปลี่ยนรุ่นด้วย kubectl rolling-update ฝั่ง client ซึ่งถูกถอดออกแล้ว",
  "Left: an older, slightly rusty teal robot with a simple magnifier showing one equality tag, a small retired "
  "hat and an old crossed-out remote control. Right: the modern supervisor robot with a magnifier showing a set of "
  "tags. An arrow from left to right. Nong Som shakes hands with the old robot respectfully.",
  ["ReplicationController", "v1", "ReplicaSet", "apps/v1", "app=snack", "app in (snack, drink)",
   "kubectl rolling-update"],
  "'ReplicationController' and 'v1' on the old robot's chest plate and shoulder; 'ReplicaSet' and 'apps/v1' on "
  "the modern robot's chest plate and shoulder; 'app=snack' in the old magnifier; 'app in (snack, drink)' in the "
  "new magnifier; 'kubectl rolling-update' on the crossed-out remote control")

S10 = "10. ReplicaSet ใน namespace: quota, LimitRange และ PSA"
t("rs-quota-cap", S10,
  "RS กับ ResourceQuota: quota pods=4 แต่ replicas 6 → สร้างได้ 4 ตัว ที่เหลือ FailedCreate (exceeded quota) RS ตั้ง condition ReplicaFailure และพยายามซ้ำเรื่อย ๆ; LimitRange เติม requests/limits ให้ Pod ที่ RS สร้าง",
  "A painted zone on the harbor map with a zone sign and a counting gate post showing four slots, all filled by "
  "four booths. The supervisor robot holds two more stamped booths that bounce off the gate with red sparks; its "
  "clipboard shows a mismatch and an orange alert ticket hangs from it. A small sticker machine at the gate puts "
  "size stickers on each booth that passes. Nong Som reads the alert ticket. Never draw money or coins.",
  ["pods: 4", "replicas: 6", "4/6", "FailedCreate: exceeded quota", "ReplicaFailure", "LimitRange"],
  "'pods: 4' on the gate post; 'replicas: 6' and '4/6' on the robot's clipboard (two lines); 'FailedCreate: "
  "exceeded quota' on the alert ticket; 'ReplicaFailure' on a small red flag on the robot's head; 'LimitRange' on "
  "the sticker machine; size stickers are color only",
  nt=True)
t("psa-workload-warn", S10,
  "Pod Security Admission กับ ReplicaSet: โหมด warn เตือนตั้งแต่ตอนสร้าง RS (ตรวจ Pod template) แต่ enforce ตรวจที่ตัว Pod → RS ถูกสร้างได้ แต่ Pod ถูกปฏิเสธ (FailedCreate) จนกว่าจะแก้ template",
  "A security checkpoint at the entrance of a painted zone. The supervisor robot walks through with its blueprint "
  "and receives a yellow warning slip, but is allowed in. Inside the zone, each booth the robot tries to stamp is "
  "blocked by a red barrier arm. The robot's clipboard shows zero ready booths. Nong Som studies the yellow slip.",
  ["warn", "enforce", "Warning: would violate PodSecurity", "FailedCreate", "0/3"],
  "'warn' on the checkpoint booth at the entrance; 'enforce' on the red barrier arm inside; 'Warning: would "
  "violate PodSecurity' on the yellow slip; 'FailedCreate' on a small red ticket at the barrier; '0/3' on the "
  "robot's clipboard",
  nt=True)

S11 = "11. ReplicaSet กับการจัดวาง: anti-affinity และ topology spread"
t("anti-affinity-required", S11,
  "podAntiAffinity แบบ required + topologyKey hostname: ห้ามบูธ RS เดียวกันอยู่เรือเดียวกัน มี worker 2 ลำแต่ replicas 3 → ตัวที่ 3 ค้าง Pending",
  "Two worker cargo ships each carry exactly one booth with a matching orange tag; between the booths a strong "
  "repelling magnet symbol. A third booth floats on a raft at the dock, unable to board either ship, with a small "
  "pause icon. The control tower ship is in the background with a no-entry flag. The supervisor robot holds its "
  "clipboard. Nong Som looks at the floating booth, puzzled.",
  ["required", "lab-worker", "lab-worker2", "Pending", "replicas: 3"],
  "'required' on the magnet symbol; 'lab-worker' and 'lab-worker2' on the two worker ship hulls; 'Pending' on the "
  "floating booth; 'replicas: 3' on the robot clipboard; the control tower ship and flag have no text")
t("preferred-and-spread", S11,
  "preferred (กระจายเท่าที่ทำได้ → 3 บูธบน 2 เรือ = 2+1) และ topologySpreadConstraints maxSkew 1 (จำนวนบนแต่ละเรือต่างกันไม่เกิน 1)",
  "Two side-by-side scenes. Left: two ships, one carrying two booths and the other one booth, a gentle soft "
  "magnet icon above. Right: two ships with three and two booths and a balance scale icon between them showing a "
  "difference of one. The supervisor robot balances booths on the right. Nong Som gives a thumbs up.",
  ["preferred", "2", "1", "topologySpreadConstraints", "maxSkew: 1"],
  "'preferred' heads the left scene; '2' and '1' are count badges on the left two ships; "
  "'topologySpreadConstraints' heads the right scene; 'maxSkew: 1' on the balance scale; right ships have no "
  "count text")

S12 = "12. ข้อควรรู้: Pod จาก ReplicaSet ไม่มีชื่อคงที่และ IP คงที่"
t("names-ips-change", S12,
  "ทุกครั้งที่ RS สร้างตัวแทน ได้ชื่อใหม่และ IP ใหม่ ลูกค้าที่จำที่อยู่เดิมหรือ port-forward ที่ต่อ Pod เดิมไว้จะหลงทาง — ยังขาด 'ที่อยู่คงที่'",
  "A booth that just reappeared on the ship with a new name card and a new IP tag, while the old outline with the "
  "old name and IP fades away next to it. A faceless customer silhouette holds an address card matching the old "
  "booth and looks around lost; a laptop cable plugged into the old outline is snapped. Nong Som shrugs.",
  ["snack-rs-4xk9p", "10.244.1.12", "snack-rs-q8vnc", "10.244.2.15", "port-forward"],
  "'snack-rs-4xk9p' and '10.244.1.12' on the fading old outline (name card and IP tag); 'snack-rs-q8vnc' and "
  "'10.244.2.15' on the new booth; 'port-forward' on the snapped cable; the customer's address card has no text")

S13 = "13. สรุปและปูทางบทถัดไป"
t("summary-checklist", S13,
  "สรุปบท: ReplicaSet = controller ที่นับ Pod ตาม selector แล้วสร้าง/ลบจาก template ให้ครบ replicas ตลอดเวลา ดูแลด้วย ownerReferences และ scale ได้ทันที",
  "A checklist board with exactly six ticked rows, each with a small icon (clipboard, magnifier, blueprint, owner "
  "badge, healing sparkle, dial). The supervisor robot stands proudly beside it, and Nong Som gives a big thumbs "
  "up.",
  ["replicas", "selector", "template", "ownerReferences", "self-healing", "scale"],
  "exactly six rows, each with exactly one label in the listed order")
t("next-chapters", S13,
  "ปัญหาที่ยังเหลือ: แต่ละบูธมีฐานข้อมูลของตัวเอง ชื่อ/IP เปลี่ยนทุกครั้งจนลูกค้าหาร้านไม่เจอ (→ บท 006 Service) และเปลี่ยนรุ่นต้องลบ Pod เองทีละตัว (→ บท 007 Deployment)",
  "The harbor at dusk: three booths on two ships with the supervisor robot. Above them three thought clouds with "
  "simple icons: three different order notes, a lost customer silhouette in fog, a tired paw deleting booths one "
  "by one. On the horizon, drawn only as soft shadow silhouettes, a lighthouse and a taller robot with a bow tie, "
  "each with a hanging sign. Nong Som looks toward the horizon with hope.",
  ["ข้อมูลไม่ตรงกัน", "IP เปลี่ยน", "เปลี่ยนรุ่นด้วยมือ", "บท 6 Service", "บท 7 Deployment"],
  "each thought cloud carries exactly one of the first three labels in order; 'บท 6 Service' hangs from the "
  "lighthouse silhouette; 'บท 7 Deployment' hangs from the tall robot silhouette; the silhouettes are shadowy and "
  "small",
  allow=True)

# ================================================================== LAB
LS0 = "LAB0 เตรียมคลัสเตอร์ + ทบทวน Pod เดี่ยวหายถาวร"
l("lab0-prepare", LS0,
  "LAB0: เช็กเรือ 3 ลำ Ready, ลบ Pod เดี่ยวแล้วยืนยันว่าหายถาวร และส่องหา kube-controller-manager ใน kube-system",
  "Nong Som at a laptop on the dock; three ships with Ready flags; on one ship a single booth has just vanished "
  "into a dotted outline with nothing replacing it; a window of the control tower is open showing a robot at a "
  "desk.",
  ["kubectl get nodes", "Ready", "Pod เดี่ยว: หายถาวร", "kube-controller-manager"],
  "'kubectl get nodes' on the laptop screen; 'Ready' once on a flag shared by the fleet; 'Pod เดี่ยว: หายถาวร' "
  "next to the dotted outline; 'kube-controller-manager' on the tower window sign",
  src="L01 01-lab0-prepare.png (แก้)")

LS1 = "LAB1 ReplicaSet แรก"
l("lab1-first-rs", LS1,
  "LAB1: สร้าง snack-rs 3 ตัว ดูชื่อ Pod แบบ <rs>-<สุ่ม>, ownerReferences, Events SuccessfulCreate และลอง template ที่ label ไม่ตรง selector",
  "The supervisor robot proudly stamps three booths in a row on a ship; each booth has a name card and a small "
  "owner badge. A ticket roll with an event pops out of the stamping machine. Off to the side, a rejected "
  "blueprint lies in a bin with a red stamp. Nong Som types at a laptop.",
  ["snack-rs", "replicas: 3", "snack-rs-4xk9p", "ownerReferences", "SuccessfulCreate"],
  "'snack-rs' on the robot's chest plate; 'replicas: 3' on its clipboard; 'snack-rs-4xk9p' on the first booth's "
  "name card only (other name cards are color only); 'ownerReferences' on one badge callout; 'SuccessfulCreate' "
  "on the event ticket; the rejected blueprint stamp has no text")

LS2 = "LAB2 Self-healing: ลบ Pod, drain และเรือล่ม"
l("lab2-delete-watch", LS2,
  "LAB2: ลบ Pod (ทั้งทีละตัวและ -l app=snack) ขณะเปิด kubectl get pods -w อีกหน้าต่าง เห็นตัวใหม่เกิดขณะตัวเก่ายัง Terminating",
  "Nong Som presses a big red button; the old booth is fading with closing shutters while the supervisor robot is "
  "already stamping a replacement right next to it. A second monitor on the dock shows a live scrolling list with "
  "an eye icon.",
  ["kubectl delete pod", "Terminating", "Running", "kubectl get pods -w"],
  "'kubectl delete pod' on the red button; 'Terminating' on the old fading booth; 'Running' on the new booth; "
  "'kubectl get pods -w' on the second monitor",
  src="L02 02-lab1-rs-self-heal.png (แก้)")
l("lab2-drain-rebirth", LS2,
  "LAB2 (ต่อ): drain lab-worker2 → Pod ของ snack-rs บนเรือนั้นถูกไล่และเกิดใหม่บน lab-worker แล้ว uncordon (Pod ไม่ย้ายกลับเอง) — ทางเลือก: docker stop lab-worker2 + tolerationSeconds 30",
  "Ship lab-worker2 under repair scaffolding with a closed gate; booths leave it as dotted outlines while the "
  "supervisor robot stamps new booths onto ship lab-worker. Afterwards a green reopen ribbon is tied on the gate "
  "of lab-worker2 but its deck stays empty. Nong Som holds a work-order card.",
  ["kubectl drain lab-worker2", "SchedulingDisabled", "lab-worker", "lab-worker2", "kubectl uncordon"],
  "'kubectl drain lab-worker2' on the work-order card; 'SchedulingDisabled' on the closed gate; 'lab-worker' and "
  "'lab-worker2' on the ship hulls; 'kubectl uncordon' on the green ribbon",
  nt=True)

LS3 = "LAB3 Scale"
l("lab3-scale", LS3,
  "LAB3: scale ด้วย kubectl scale, แก้ไฟล์แล้ว apply, kubectl edit และ scale 0 พร้อมบันทึกว่า Pod ตัวไหนถูกลบตอน scale ลง",
  "The supervisor robot turns a dial in three steps shown as three small scenes left to right: five booths, two "
  "booths, zero booths with an empty but tidy deck. A crane removes booths and drops event tickets. Nong Som "
  "notes names on a clipboard.",
  ["--replicas=5", "--replicas=2", "--replicas=0", "SuccessfulDelete"],
  "the three scene headings are '--replicas=5', '--replicas=2', '--replicas=0' in order; 'SuccessfulDelete' on "
  "one event ticket",
  nt=True)

LS4 = "LAB4 กับดัก label"
l("lab4-label-trap", LS4,
  "LAB4: Pod stray ที่ label ตรงถูกลบทันทีเมื่อ RS ครบแล้ว แต่ถ้ามีอยู่ก่อนจะถูกรับเลี้ยง และถอด label เพื่อแยก Pod ออกมา debug",
  "Three small scenes side by side. Left: a stray booth placed next to three booths is lifted away by the robot. "
  "Middle: a stray booth already on the ship receives an owner badge from an arriving robot and only two new booths "
  "appear. Right: Nong Som unties a tag from a booth and wheels it to an inspection bench while the robot stamps "
  "a replacement.",
  ["after RS: deleted", "before RS: adopted", "app-", "stray", "stray"],
  "'after RS: deleted' heading left, 'before RS: adopted' heading middle, 'app-' heading right; the stray booths "
  "in the left and middle scenes each have one 'stray' name card",
  src="L03 03-lab2-label-trap.png (แก้)")

LS5 = "LAB5 selector แก้ไม่ได้ + template ใหม่ Pod เดิมไม่เปลี่ยน"
l("lab5-template-old-pods", LS5,
  "LAB5: เปลี่ยน selector ได้ field is immutable; เปลี่ยน image ใน template เป็น nginx:1.28-alpine แล้ว custom-columns ยังเห็น 1.27 ทุกตัว จนกว่าจะลบ Pod",
  "Left: the robot's magnifier with a padlock and a red stamp. Right: a terminal-style table card with three rows "
  "next to three booths; two old booths and one freshly stamped booth with a star. Nong Som points at the table.",
  ["field is immutable", "nginx:1.27-alpine", "nginx:1.27-alpine", "nginx:1.28-alpine", "custom-columns"],
  "'field is immutable' in the red stamp; the table card has exactly three rows reading 'nginx:1.27-alpine', "
  "'nginx:1.27-alpine', 'nginx:1.28-alpine' top to bottom; 'custom-columns' as the table card title",
  nt=True)

LS6 = "LAB6 ลบ RS แบบ cascade vs orphan"
l("lab6-cascade-orphan", LS6,
  "LAB6: ลบ RS ปกติ Pod หายตาม, ลบด้วย --cascade=orphan Pod อยู่ต่อแบบไม่มีเจ้าของ แล้ว apply RS เดิมอีกครั้ง → รับเลี้ยงโดยไม่สร้างเพิ่ม",
  "Two steps. Left: Nong Som cuts dotted owner strings with scissors as the robot leaves; three booths remain on "
  "the ship. Right: the robot returns and clips owner badges back onto the same three booths; its stamping "
  "machine shows zero. Booths are ordinary booths, never children or animals.",
  ["--cascade=orphan", "ownerReferences", "snack-rs", "+0"],
  "'--cascade=orphan' on the scissors; 'ownerReferences' on one re-clipped badge callout on the right; "
  "'snack-rs' on the robot's chest plate on the right; '+0' on the stamping machine counter; never draw waterfalls")

LS7 = "LAB7 ReplicaSet กับ quota, LimitRange และ PSA"
l("lab7-quota", LS7,
  "LAB7: namespace rs-quota มี quota pods=4 + LimitRange → RS replicas 6 ได้แค่ 4, Events FailedCreate exceeded quota, condition ReplicaFailure; เพิ่ม quota แล้ว RS สร้างต่อเอง; ทางเลือก PSA enforce ให้ RS สร้างได้แต่ Pod ถูกปฏิเสธ",
  "A painted zone with a gate post showing four filled slots; the supervisor robot holds two booths that bounce "
  "off; an alert ticket hangs from its clipboard. Nong Som raises the gate post limit with a lever on the side, "
  "and a sticker machine at the gate puts size stickers on each booth. Never draw money or coins.",
  ["rs-quota", "pods: 4", "4/6", "exceeded quota", "LimitRange"],
  "'rs-quota' on the zone sign; 'pods: 4' on the gate post; '4/6' on the robot clipboard; 'exceeded quota' on "
  "the alert ticket; 'LimitRange' on the sticker machine",
  nt=True)

LS8 = "LAB8 กระจาย replica ด้วย anti-affinity และ topology spread"
l("lab8-spread", LS8,
  "LAB8: required anti-affinity + replicas 3 บน worker 2 ลำ → 1 Pending; เปลี่ยนเป็น preferred → 2+1; topologySpreadConstraints maxSkew 1 → 2+2 / 3+2",
  "Two scenes stacked vertically. Top: two worker ships with one booth each and a third booth floating on a raft at "
  "the dock. Bottom: the same two ships with two booths and one booth, a soft magnet icon above. The supervisor "
  "robot moves between the scenes. Nong Som compares them with a pointer.",
  ["required: Pending", "preferred: 2+1", "lab-worker", "lab-worker2", "maxSkew: 1"],
  "'required: Pending' heads the top scene; 'preferred: 2+1' heads the bottom scene; 'lab-worker' and "
  "'lab-worker2' appear once each on the bottom scene ship hulls; 'maxSkew: 1' on a small side note card")

LS9 = "LAB9 LAB สุดท้าย: ร้านน้องส้ม 3 บูธด้วย ReplicaSet"
l("lab9-architecture", LS9,
  "LAB9 สถาปัตยกรรม: namespace som-booths, ReplicaSet som-booth replicas 3, Pod template = ร้าน all-in-one ของบท 004 (web som-shop-web:1.1 + db sidecar postgres + emptyDir) ทุกบูธจึงมีฐานข้อมูลของตัวเอง",
  "A painted zone on the harbor with the supervisor robot holding a blueprint. Three booths on two ships; one "
  "booth is enlarged in a cutaway showing two containers inside: a web counter container and a small database "
  "cabinet container with its own shelf of cat food cans. A dotted line ties every booth to the robot. Nong Som "
  "explains with a pointer.",
  ["som-booths", "som-booth", "replicas: 3", "web", "db", "som-shop-web:1.1"],
  "'som-booths' on the zone sign; 'som-booth' on the robot chest plate; 'replicas: 3' on its clipboard; 'web' and "
  "'db' only on the two containers of the enlarged booth; 'som-shop-web:1.1' on the blueprint")
l("lab9-prepare-image", LS9,
  "LAB9 เตรียม image: ถ้าคลัสเตอร์ใหม่ build som-shop-web:1.1 จากโฟลเดอร์บท 004 แล้ว kind load ให้ทุก Node, postgres ใช้ docker save --platform + kind load image-archive หรือให้ Node pull เอง",
  "A small dockside workshop: Nong Som packs a freshly built crate of cat food cans on a workbench, then a "
  "delivery cart carries copies of the crate onto all three ships. A second crate of database cabinets rides the "
  "same cart.",
  ["docker build", "som-shop-web:1.1", "kind load docker-image", "postgres:17.11-alpine"],
  "'docker build' on the workbench; 'som-shop-web:1.1' on the first crate; 'kind load docker-image' on the "
  "delivery cart; 'postgres:17.11-alpine' on the second crate")
l("lab9-three-booths-two-ships", LS9,
  "LAB9: apply แล้ว kubectl get pods -o wide เห็น 3 บูธกระจาย 2 เรือ (preferred anti-affinity → 2+1) แต่ละบูธชื่อไม่ซ้ำ",
  "Two worker ships: one carries two cat-food booths, the other carries one booth; each booth has a name card and "
  "a tiny awning; a soft magnet icon floats between ships. Nong Som on the dock checks a laptop table.",
  ["lab-worker", "lab-worker2", "kubectl get pods -o wide", "preferred"],
  "'lab-worker' and 'lab-worker2' on the hulls; 'kubectl get pods -o wide' on the laptop; 'preferred' on the "
  "magnet icon; booth name cards are color only",
  nt=True)
l("lab9-port-forward-each", LS9,
  "LAB9: ลูกค้าเข้าร้านได้ทีละบูธเท่านั้น: kubectl port-forward pod/<ชื่อ> 8081/8082/8083:3000 ใน k8s-lab แล้ว ssh -L จากเครื่องนักศึกษา เปิด 3 แท็บ",
  "Three separate cables run from three booths on two ships to a relay box on the dock, then one thick tunnel "
  "cable runs to Nong Som's laptop showing three browser tabs. Each booth cable has a numbered plug.",
  ["8081", "8082", "8083", "port-forward", "ssh -L"],
  "'8081', '8082', '8083' on the three plugs; 'port-forward' on the relay box; 'ssh -L' on the tunnel cable; "
  "browser tabs have no text")
l("lab9-orders-mismatch", LS9,
  "LAB9: สั่งซื้อที่บูธ a แล้วเปิดบูธ b/c → ออเดอร์ไม่ตรงกัน เพราะแต่ละบูธมี db ของตัวเอง",
  "Three booths side by side, each with an order board on its awning showing a different order count, and each "
  "with its own small database cabinet behind it. A faceless customer silhouette with a shopping bag stands at the "
  "first booth. Nong Som looks from one board to another, confused.",
  ["ออเดอร์ 2", "ออเดอร์ 0", "ออเดอร์ 0", "db", "db", "db"],
  "the three order boards read 'ออเดอร์ 2', 'ออเดอร์ 0', 'ออเดอร์ 0' left to right; each cabinet carries one "
  "'db'",
  nt=True)
l("lab9-delete-pod-data-lost", LS9,
  "LAB9: ลบ Pod บูธ a → RS สร้างบูธใหม่ ชื่อใหม่ IP ใหม่ ออเดอร์เป็น 0 (emptyDir หายพร้อม Pod) และ port-forward ที่ต่อบูธเดิมหลุด",
  "The old booth fades away together with its database cabinet; the robot stamps a fresh booth with a new name "
  "card and an empty database cabinet; its order board shows zero. The numbered cable that was plugged into the "
  "old booth hangs snapped and sparking. Nong Som holds a paw to her mouth.",
  ["kubectl delete pod", "ออเดอร์ 0", "port-forward", "8081"],
  "'kubectl delete pod' on a red button; 'ออเดอร์ 0' on the new booth's order board; 'port-forward' and '8081' "
  "on the snapped cable and its plug",
  nt=True)
l("lab9-scale-3-5-2", LS9,
  "LAB9: kubectl scale rs som-booth --replicas=5 แล้ว 2 — ดูว่าบูธไหนถูกปิด (ระวัง resource: 5 บูธขอราว 1 CPU / 2.2Gi ถ้า Pending ให้ใช้ 4)",
  "Three small scenes left to right: three booths on two ships, then five booths on two ships (three and two), "
  "then two booths (one per ship). The robot turns its dial in each scene. Nong Som watches a small resource "
  "gauge on the dock.",
  ["3", "5", "2", "kubectl scale rs som-booth"],
  "'3', '5', '2' are big count badges above the three scenes; 'kubectl scale rs som-booth' on the dial; the "
  "gauge has no text",
  nt=True)
l("lab9-template-promo", LS9,
  "LAB9: แก้ template เป็น som-shop-web:1.1-promo + ข้อความโปร แล้ว apply → บูธเดิมยังเป็น 1.1 ทุกบูธ (template ใหม่ใช้กับบูธที่เกิดใหม่เท่านั้น)",
  "The robot holds a new festive blueprint with confetti and a star; the two booths on the ships still show the "
  "old plain signboards. Nong Som compares the blueprint and the booths, eyebrows raised.",
  ["som-shop-web:1.1-promo", "โปรบูธใหม่", "1.1", "1.1"],
  "'som-shop-web:1.1-promo' and 'โปรบูธใหม่' on the festive blueprint; each of the two booths shows one '1.1' "
  "signboard; never draw real fireworks",
  nt=True)
l("lab9-manual-replace", LS9,
  "LAB9: ต้องลบ Pod ทีละตัวด้วยมือจึงได้บูธรุ่นโปร ระหว่างนั้นบูธที่ถูกลบปิดชั่วคราว ออเดอร์ของบูธนั้นหาย และต้อง port-forward ใหม่ทุกครั้ง",
  "Nong Som, tired and sweating, deletes one old booth with a small red button while the robot stamps a festive "
  "promo booth in its place; the other old booth waits its turn. A small 'next' arrow points to the remaining old "
  "booth.",
  ["kubectl delete pod", "1.1", "1.1-promo", "ทีละตัว"],
  "'kubectl delete pod' on the red button; '1.1' on the remaining old booth; '1.1-promo' on the new festive "
  "booth; 'ทีละตัว' on the next arrow",
  nt=True)
l("lab9-wrap-up-handoff", LS9,
  "สรุป LAB9 และปัญหาส่งต่อ: (1) แต่ละบูธมี db ของตัวเอง ข้อมูลไม่ตรงกัน (2) ชื่อ/IP เปลี่ยน ต้อง port-forward ทีละ Pod → บท 006 Service (3) เปลี่ยนรุ่นต้องลบ Pod เอง → บท 007 Deployment",
  "A checklist board with three rows each marked with an orange question mark icon. Behind the board, on the "
  "horizon, two soft shadow silhouettes: a lighthouse and a taller robot with a bow tie. Nong Som stands with the "
  "supervisor robot, pointing at the horizon.",
  ["ข้อมูลไม่ตรงกัน", "ชื่อ/IP เปลี่ยน", "เปลี่ยนรุ่นด้วยมือ", "บท 6 Service", "บท 7 Deployment"],
  "the three board rows carry the first three labels in order; 'บท 6 Service' under the lighthouse silhouette; "
  "'บท 7 Deployment' under the tall robot silhouette; the silhouettes are shadowy and small",
  allow=True)

if __name__ == "__main__":
    imgcommon.main()
