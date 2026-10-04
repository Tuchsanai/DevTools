#!/usr/bin/env python3
"""สร้าง images.json + imagegen-prompts.md ของบท 004 (Namespace)"""
import json, os

ROOT = "/root/workspace/DevTools/k/004_kubernetes_namespace"
OUT_JSON = "/root/workspace/DevTools/k/logs/004_namespace/images.json"

USE_CASE = ("Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai "
            "university DevTools course; must teach the concept correctly at a glance.")
ASSET = ("Asset type: landscape 3:2 educational story illustration for Thai Kubernetes Namespace lesson "
         "(README figure, about 1536x1024).")
CHAR = ("Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby "
        "orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, "
        "big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with "
        "a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and "
        "neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly.")
STYLE = ("Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, white background, palette "
         "navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; "
         "matches the chapter 002 and chapter 003 classroom illustration set. Shared metaphor (keep consistent across "
         "the series): cluster = the whole Kubernetes harbor; container = colored shipping container box; Pod = "
         "rounded translucent teal cabin box that wraps one or more shipping containers and carries one small IP tag, "
         "and a Pod always sits on exactly one ship; Node = cargo ship (worker ships lab-worker and lab-worker2); "
         "Control Plane = harbor control tower on the dock (lab-control-plane). New in this chapter: Namespace = a "
         "colored zone painted on the harbor map with a zone name sign; it is a logical grouping, NOT a ship, NOT a "
         "machine and NOT a piece of land that holds ships — every Pod box wears a small colored zone ribbon tag "
         "matching its zone color, and Pods of one zone may sit on different ships; ResourceQuota = a zone budget "
         "sheet with used/limit gauges; LimitRange = a zone signboard of standard box sizes; RBAC = staff ID badges "
         "with access rights per zone; ServiceAccount = the ID badge worn by a small friendly harbor robot worker "
         "(the robot is a simple box-shaped machine, never a second cat); Pod Security Admission = a security "
         "checkpoint gate at the zone entrance; NetworkPolicy = a fence with a gate between zones; cluster-scoped "
         "resources = shared harbor-wide property (ships, control tower, zone signs themselves, central warehouse). "
         "Every cargo item, crate or prop is cat-food-shop related only (kibble bags, cat food cans, fish-shaped "
         "treats, food bowls).")
BASE_CONS = ("only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish "
             "or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; "
             "every row, column, lane, zone or panel that is drawn has one of the listed labels or is clearly "
             "unlabeled decoration; a Pod box is never split across two ships; a namespace zone is never drawn as a "
             "ship or as a separate harbor")
NO_CTRL = ("; do not show Service, NodePort, Deployment, ReplicaSet, DaemonSet or Ingress objects or words")


def prompt(scene, labels, extra="", allow_ctrl=False):
    lab = "; ".join(f'"{l}"' for l in labels)
    cons = BASE_CONS + ("" if allow_ctrl else NO_CTRL) + (f"; {extra}" if extra else "") + "."
    return "\n".join([
        USE_CASE, ASSET, f"Scene: {scene}", CHAR, STYLE,
        f"Text (verbatim, at most {len(labels)} short labels): {lab}.",
        f"Constraints: {cons}",
    ])


T = []  # (slug, section, caption, scene, labels, extra, allow_ctrl, needs_test)
L = []

def t(slug, section, cap, scene, labels, extra="", allow=False, nt=False):
    T.append((slug, section, cap, scene, labels, extra, allow, nt))

def l(slug, section, cap, scene, labels, extra="", allow=False, nt=False):
    L.append((slug, section, cap, scene, labels, extra, allow, nt))

# ------------------------------------------------------------------ THEORY
S1 = "1. บทนำ: ท่าเรือที่ทุกทีมวางของปนกัน"
t("opening-crowded-harbor", S1,
  "ร้านน้องส้มโตขึ้น มีทั้งทีมทดลองของใหม่ ทีมทดสอบ และร้านจริง ทุกคนวางกล่องปนกันบนท่าเรือเดียว ชื่อชนกันและใครจะลบของใครก็ได้",
  "Busy harbor seen from the dock: two worker cargo ships packed with many teal Pod boxes in a messy jumble; two "
  "Pod boxes on different ships carry the same name card and a red clash spark between them; a faceless sailor "
  "silhouette carries a Pod box away by mistake while another faceless sailor reaches out in alarm. Nong Som stands "
  "in front scratching head with a worried face. The control tower is in the background, unlabeled.",
  ["บทที่ 4", "Namespace", "som-shop", "som-shop"],
  "the two 'som-shop' labels are name cards on two different Pod boxes; no colored zones are painted yet; "
  "sailors are faceless silhouettes, not cats")
t("new-metaphor-map", S1,
  "แผนผังอุปมาใหม่ของบทนี้: โซนทาสี = Namespace, ใบงบ = ResourceQuota, ป้ายขนาดกล่อง = LimitRange, บัตรพนักงาน = RBAC, ด่านตรวจ = Pod Security, รั้วประตู = NetworkPolicy",
  "A clean legend board with six illustrated rows, each row = one icon on the left and its Kubernetes term on the "
  "right: (1) a colored painted zone outline with a zone sign, (2) a budget sheet with a gauge, (3) a signboard "
  "showing three box sizes, (4) a staff ID badge on a lanyard, (5) a checkpoint gate with a barrier arm, (6) a "
  "fence with a small gate. Nong Som points at the board with a pointer stick.",
  ["Namespace", "ResourceQuota", "LimitRange", "RBAC", "Pod Security", "NetworkPolicy"],
  "exactly six rows and each row has exactly one of the six labels")

S2 = "2. Namespace คืออะไร"
t("zones-on-harbor-map", S2,
  "Namespace คือโซนทาสีบนแผนผังท่าเรือ กล่องทุกใบคล้องริบบิ้นสีของโซนตัวเอง ทั้งที่อยู่บนเรือคนละลำ",
  "Two-level picture. Top: a big harbor map board on an easel inside the control tower showing three painted "
  "zones as colored folders (blue zone, green zone, purple zone), each with a zone name sign. Bottom: the two "
  "worker cargo ships side by side; on them sit six teal Pod boxes, each wearing a small colored ribbon tag "
  "(blue, green or purple); blue-tagged boxes appear on BOTH ships. Dotted lines connect each colored folder on the "
  "map to the boxes with the same color ribbon. Nong Som holds a paint roller dripping blue paint next to the map.",
  ["team-a", "team-b", "team-c", "lab-worker", "lab-worker2"],
  "team-a is the blue zone sign, team-b the green zone sign, team-c the purple zone sign, all three on the map "
  "board only; lab-worker and lab-worker2 are painted on the ship hulls; paint is only on the map, not on the sea")
t("namespace-is-not-a-ship", S2,
  "ความเข้าใจผิดที่พบบ่อย: Namespace ไม่ใช่เรือหรือเครื่อง Pod ของโซนเดียวกันกระจายอยู่หลายเรือได้ และเรือหนึ่งลำรับกล่องได้จากหลายโซน",
  "Split panel. Left panel (wrong): a cargo ship painted entirely blue as if the whole ship were a namespace, with "
  "a big red X over it. Right panel (correct): two worker ships, each carrying a mix of blue-ribbon and "
  "green-ribbon teal Pod boxes, with a big green check mark. Nong Som stands between the panels wagging a finger at "
  "the left side.",
  ["ผิด", "ถูก", "Namespace ≠ Node"],
  "the red X is only on the left panel, the check mark only on the right panel")
t("why-namespaces", S2,
  "ทำไมต้องมี Namespace: หลายทีมและหลาย environment ใช้คลัสเตอร์เดียวกันได้ ถูกกว่าแยกคลัสเตอร์ต่อทีม แต่แยกขาดน้อยกว่า",
  "Comparison board with two columns. Left column: one big harbor divided into three colored zones (dev, staging, "
  "prod) sharing one control tower, with a small coin stack. Right column: three separate tiny harbors each with "
  "its own control tower, with a tall coin stack. Nong Som weighs the two coin stacks on a balance scale in the "
  "middle.",
  ["คลัสเตอร์เดียว หลาย namespace", "หลายคลัสเตอร์", "dev", "staging", "prod"],
  "dev, staging and prod are the three zone signs in the left column only")

S3 = "3. Namespace เริ่มต้นและสิ่งที่อยู่ข้างใน"
t("default-namespaces", S3,
  "คลัสเตอร์ kind มี namespace ตั้งต้น 5 โซน: default, kube-system, kube-public, kube-node-lease และ local-path-storage ที่ kind เพิ่มมา",
  "The harbor map board showing five painted zones as five rounded colored regions, each with its own sign: a "
  "plain white zone, a navy zone near a small tower icon, a light-yellow zone with a notice board icon, a teal "
  "zone with heartbeat radio icons, and a gray zone with a small warehouse icon. Nong Som presents the board with "
  "both arms open.",
  ["default", "kube-system", "kube-public", "kube-node-lease", "local-path-storage"],
  "exactly five zones and each zone has exactly one of the five labels")
t("kube-system-zone", S3,
  "kube-system คือโซนพนักงานของท่าเรือ มี Pod ระบบ เช่น etcd, apiserver, scheduler, coredns, kindnet และ kube-proxy",
  "Close-up of the navy zone on the harbor map; around it six small teal Pod boxes wearing navy ribbons, each box "
  "holding a tool icon (a filing cabinet, a telephone switchboard, a clipboard, a phone book, a network cable reel, "
  "a traffic arrow sign); a dotted line shows that some of these boxes ride on the control tower and some on the "
  "two worker ships. Nong Som peeks in carefully wearing a staff-only visitor sticker.",
  ["kube-system", "etcd", "coredns", "kindnet", "kube-proxy"],
  "the label kube-system is the navy zone sign; the other labels are name cards on four of the Pod boxes; "
  "the visitor sticker has no text")
t("kube-public-node-lease", S3,
  "kube-public เก็บประกาศที่ใครก็อ่านได้ (cluster-info) ส่วน kube-node-lease เก็บใบ Lease ของเรือแต่ละลำที่ต่ออายุทุก 10 วินาทีเป็นสัญญาณว่ายังอยู่",
  "Two zones side by side. Left: a light-yellow zone with a public notice board pinned with one big card, "
  "passers-by silhouettes reading it. Right: a teal zone with three lease cards on a rack, each card connected "
  "by a radio wave to a ship (control tower, ship one, ship two) and a small stopwatch. Nong Som listens with a "
  "radio headset between the zones.",
  ["kube-public", "cluster-info", "kube-node-lease", "Lease", "10 วินาที"],
  "kube-public and kube-node-lease are the zone signs; exactly three lease cards")

S4 = "4. Namespaced vs cluster-scoped resources"
t("zone-items-vs-shared", S4,
  "ของบางอย่างอยู่ประจำโซน (Pod, ServiceAccount, Role, ResourceQuota) แต่ของบางอย่างเป็นของส่วนกลางทั้งท่าเรือ (Node, Namespace, PersistentVolume, StorageClass)",
  "Harbor overview split by a dashed line. Upper area 'inside zones': two painted zones each holding small items — "
  "teal Pod boxes, ID badges, a budget sheet. Lower area 'shared by the whole harbor': two cargo ships, the zone "
  "signposts themselves standing on a common pier, a big central warehouse, and a VIP priority flag pole. Nong Som "
  "sorts items with two baskets.",
  ["namespaced", "cluster-scoped", "Pod", "Node", "Namespace", "PersistentVolume"],
  "Pod is under namespaced; Node, Namespace and PersistentVolume are under cluster-scoped")
t("api-resources-two-columns", S4,
  "kubectl api-resources --namespaced=true/false แบ่งชนิด resource เป็นสองกลุ่ม และ -n ไม่มีผลกับของส่วนกลาง",
  "A big terminal-styled card split into two columns of icon chips. Left column with a zone ribbon icon at top: "
  "Pod box chip, badge chip, budget sheet chip, fence chip. Right column with a harbor icon at top: ship chip, zone "
  "signpost chip, warehouse chip, VIP flag chip. Nong Som reads the card with a magnifier.",
  ["--namespaced=true", "--namespaced=false", "Pod", "Node", "StorageClass", "PriorityClass"],
  "Pod chip in the left column; Node, StorageClass and PriorityClass chips in the right column; other chips unlabeled")

S5 = "5. สร้างและใช้ namespace"
t("create-imperative-vs-yaml", S5,
  "สร้าง namespace ได้สองแบบ: สั่งตรงด้วย kubectl create namespace หรือเขียน YAML kind: Namespace แล้ว kubectl apply",
  "Two side-by-side cards. Left card: a paint roller quickly painting a new zone outline after a "
  "command card. Right card: a blueprint scroll describing a zone, being fed into a printer-like machine that "
  "paints the zone. Both zones end up identical below the cards. Nong Som stands between giving a thumbs up.",
  ["kubectl create namespace", "kind: Namespace", "kubectl apply -f", "blue"],
  "both resulting zones carry the same 'blue' sign; only one Nong Som")
t("manifest-ns-vs-flag", S5,
  "metadata.namespace ในไฟล์คือป้ายที่อยู่ติดกล่อง ส่วน -n คือคำสั่งปากเปล่า ถ้าไม่ตรงกัน kubectl จะปฏิเสธ",
  "Three-row flow chart. Row 1: a Pod box without an address label plus a voice bubble icon pointing to the blue "
  "zone, arrow to blue zone (check). Row 2: a Pod box with a printed address label pointing to the green zone, no "
  "voice bubble, arrow to green zone (check). Row 3: a Pod box with a green address label while the voice bubble "
  "points to blue, the box stops at a red X. Nong Som at the right side holds up a red stop paddle near row 3.",
  ["-n blue", "metadata.namespace: green", "ไม่ตรงกัน = error"],
  "the voice bubbles contain only small arrow icons, no words; the third label sits beside row 3")
t("same-name-different-zones", S5,
  "ชื่อซ้ำกันได้ถ้าอยู่คนละ namespace ชื่อเต็มคือ namespace/ชื่อ แต่ใน namespace เดียวกันชื่อต้องไม่ซ้ำ",
  "Two painted zones (blue and green) side by side on the harbor map. In each zone sits a teal Pod box with the "
  "same name card and a snack bowl inside. Above each box an address tag shows the full name. A third box trying "
  "to enter the blue zone with the same name is blocked by a small red X. Nong Som points at both identical names "
  "with a cheerful face.",
  ["blue/snack", "green/snack", "AlreadyExists"],
  "blue/snack above the box in the blue zone, green/snack above the box in the green zone, AlreadyExists beside "
  "the blocked third box in the blue zone")
t("flag-n-vs-all", S5,
  "-n ส่องดูทีละโซน ส่วน -A ส่องทั้งท่าเรือและเพิ่มคอลัมน์ NAMESPACE",
  "Night harbor map. Left half: Nong Som shines a handheld flashlight on one zone only, the other zones dark. Right "
  "half: a tall stadium floodlight on the tower lights up all zones at once and a small table card below lists Pod "
  "boxes with a colored zone column.",
  ["-n team-a", "-A", "NAMESPACE"],
  "Nong Som appears only once (in the left half); the floodlight is operated by no one")

S6 = "6. kubeconfig, context และ namespace เริ่มต้น"
t("kubeconfig-wallet", S6,
  "kubeconfig เหมือนกระเป๋าบัตร: บัตรท่าเรือ (cluster), บัตรประจำตัว (user) และ context ที่จับคู่ทั้งสองกับโซนที่ใช้บ่อย",
  "An open wallet card holder with three card slots: a harbor pass card with a harbor icon, an ID card with a "
  "fingerprint icon, and a combo card stapled from a small harbor icon, a small ID icon and a colored zone chip. "
  "An arrow highlights the combo card as the active one. Nong Som holds the wallet open.",
  ["cluster", "user", "context", "namespace", "kind-lab"],
  "kind-lab is printed on the combo context card; namespace is a small tag on the zone chip")
t("set-context-namespace", S6,
  "kubectl config set-context --current --namespace=blue เปลี่ยนโซนเริ่มต้น สะดวกแต่ต้องระวังลืมว่าตอนนี้อยู่โซนไหน",
  "Nong Som turns a big dial on a harbor control panel from a white 'default' position to a blue position; behind "
  "Nong Som a new Pod box drops into the blue zone. In a small corner inset, a forgetful moment: a trash bin icon "
  "hovering over a box in the wrong zone with a warning triangle.",
  ["set-context --current", "default", "blue", "ระวังอยู่ผิดโซน"],
  "default and blue are the two dial positions; the warning label is in the corner inset only")

S7 = "7. Label ของ namespace"
t("namespace-labels", S7,
  "namespace ติด label ได้เหมือน Pod เช่น env=prod, team=som และระบบใส่ kubernetes.io/metadata.name ให้อัตโนมัติ",
  "A tall zone signpost for a coral-colored zone with three hanging tags: two handwritten-style tags added by Nong "
  "Som and one engraved metal tag bolted on by the harbor (with a small lock icon). Nong Som ties one of the "
  "handwritten tags.",
  ["som-prod", "env=prod", "team=som", "kubernetes.io/metadata.name"],
  "som-prod is the sign board name; the metal locked tag carries kubernetes.io/metadata.name")

S8 = "8. การลบ namespace"
t("delete-namespace-everything", S8,
  "kubectl delete namespace ลบทุกอย่างในโซนทั้งก้อน: Pod, บัตรพนักงาน, ใบโควตา ไม่มีถังขยะให้กู้คืน แต่เรือและของส่วนกลางยังอยู่",
  "A purple painted zone on the harbor map being erased by a giant eraser; inside it Pod boxes, ID badges and a "
  "budget sheet fade away with sparkle dust; neighboring blue and green zones stay intact; the two ships below "
  "remain afloat. Nong Som watches with paws on cheeks.",
  ["kubectl delete namespace", "Terminating", "ทุกอย่างข้างในหายหมด"],
  "Terminating is a status tag on the purple zone sign; the ships are untouched")
t("finalizers-checklist", S8,
  "finalizers คือเช็กลิสต์ที่ต้องเคลียร์ครบก่อนปลดป้ายโซน ถ้ายังค้างอยู่ namespace จะติดสถานะ Terminating",
  "A zone signpost with a checklist clipboard hanging on it: three items, two ticked, one unticked with an "
  "hourglass. The sign has a Terminating status tag. A faceless harbor worker silhouette waits with a wrench to "
  "remove the sign. Nong Som checks the clipboard.",
  ["finalizers", "Terminating", "kubernetes"],
  "kubernetes is the text of the one unticked checklist item; the other checklist items have no text")

S9 = "9. Namespace ไม่ได้แยก network และ node"
t("cross-zone-same-ship", S9,
  "Pod ต่าง namespace อยู่บนเรือลำเดียวกันได้ และคุยกันด้วย Pod IP ได้ทันที เพราะ namespace ไม่ได้สร้างกำแพงเครือข่ายให้เอง",
  "One worker cargo ship carrying two teal Pod boxes: one wearing a blue ribbon, one wearing a green ribbon, each "
  "with an IP tag; a bright dashed line with a paper-plane icon goes from the green box to the blue box. No fence "
  "anywhere. Nong Som on the dock shrugs with an open palm.",
  ["team-a", "team-b", "10.244.1.2", "lab-worker"],
  "team-a is on the blue ribbon, team-b on the green ribbon, 10.244.1.2 is the IP tag of the blue box, lab-worker "
  "on the hull")
t("dns-search-domain", S9,
  "(ทฤษฎีปูทาง) resolv.conf ของ Pod มี search domain ตามชื่อ namespace ชื่อสั้นจึงหาได้แค่ในโซนตัวเอง ข้ามโซนต้องเติมชื่อ namespace",
  "A phone-book style card held open: a short name entry resolves inside the same colored zone, while reaching "
  "another zone needs a longer address card with an extra zone segment. Two small zone chips (blue and green) "
  "illustrate. Nong Som flips the phone book pages.",
  ["/etc/resolv.conf", "search team-b.svc.cluster.local", "ชื่อ.namespace"],
  "this is a theory preview; no Service object is drawn, only address cards")

S10 = "10. NetworkPolicy: รั้วและประตูระหว่างโซน"
t("networkpolicy-fence", S10,
  "NetworkPolicy คือรั้วรอบโซน: Pod ที่ถูกเลือกจะรับเฉพาะการเชื่อมต่อที่อนุญาต ที่เหลือถูกปฏิเสธ (kindnet ของ kind รองรับ)",
  "Top-down view of the harbor map: a blue zone surrounded by a neat picket fence; a paper-plane arrow from a "
  "green-zone box bounces off the fence with a red X; a paper-plane arrow from another blue-zone box inside reaches "
  "the target box with a green check. Nong Som hammers the last fence post.",
  ["NetworkPolicy", "team-a", "team-b", "podSelector: {}"],
  "team-a is the blue zone sign, team-b the green zone sign")
t("networkpolicy-gate-by-label", S10,
  "เปิดประตูให้เฉพาะโซนที่มีป้ายตรง ด้วย namespaceSelector อ้าง label เช่น kubernetes.io/metadata.name=team-b",
  "The fenced blue zone now has a gate; a gate guard reader scans the zone tag of an arriving paper-plane from the "
  "green zone and the gate swings open (green light); a paper-plane from a purple zone waits outside (red light). "
  "Nong Som holds the gate key ring.",
  ["namespaceSelector", "kubernetes.io/metadata.name=team-b", "team-b", "team-c"],
  "team-b is the green zone sign, team-c the purple zone sign; the long label is on the gate reader")

S11 = "11. ResourceQuota: งบประมาณของโซน"
t("quota-budget-sheet", S11,
  "ResourceQuota คือใบงบของโซน กำหนดเพดานรวม requests/limits ของ CPU และหน่วยความจำ ทุก Pod ใหม่ต้องอยู่ในงบ",
  "A big budget sheet pinned on a zone signpost with four horizontal gauges (each a bar with filled part and a "
  "limit line). Nong Som with a calculator checks a teal Pod box size tag against the remaining part of the "
  "gauges.",
  ["ResourceQuota", "requests.cpu", "requests.memory", "limits.cpu", "limits.memory"],
  "exactly four gauges, each labeled with one resource name")
t("quota-pod-count", S11,
  "quota แบบนับจำนวน object เช่น pods: 3 กล่องใบที่สี่ถูกปฏิเสธที่หน้าโซนทันที (exceeded quota)",
  "A zone entrance with a counter display showing three of three slots filled by teal Pod boxes; a fourth Pod box "
  "on a hand cart is stopped by a barrier arm with a red light. Nong Som shows the counter with an apologetic "
  "face.",
  ["pods: 3/3", "exceeded quota"],
  "only one counter display")
t("quota-must-specify", S11,
  "เมื่อโซนมีงบ requests แล้ว Pod ที่ไม่ระบุขนาด (requests/limits) จะถูกปฏิเสธ เพราะคำนวณงบไม่ได้",
  "A teal Pod box with an empty blank size tag stands at the budget desk; the clerk (faceless silhouette) shakes "
  "head with a red stamp; next to it a properly tagged Pod box passes with a green stamp. Nong Som points at the "
  "blank tag.",
  ["must specify requests.cpu", "ผ่าน", "ไม่ผ่าน"],
  "ผ่าน near the tagged box, ไม่ผ่าน near the blank-tag box")

S12 = "12. LimitRange: กฎขนาดกล่องมาตรฐาน"
t("limitrange-size-board", S12,
  "LimitRange คือป้ายกฎขนาดกล่องของโซน: กล่องที่ไม่ระบุขนาดจะได้สติกเกอร์ค่า default ให้ และห้ามเกิน max",
  "A zone signboard showing a ruler with marks: a small green mark, a medium teal mark, and a red max line. A "
  "conveyor carries a teal Pod box without size tag past a sticker machine that applies a size sticker; an "
  "oversized Pod box is stopped at the red max line. Nong Som operates the sticker machine.",
  ["LimitRange", "defaultRequest", "default", "max"],
  "defaultRequest at the small mark, default at the medium mark, max at the red line")
t("quota-vs-limitrange", S12,
  "ResourceQuota คุมงบรวมของทั้งโซน ส่วน LimitRange คุมขนาดต่อกล่องและเติมค่าให้ ใช้คู่กันได้ดี",
  "Two-column comparison card. Left: one big piggy bank feeding a whole zone of boxes (zone-wide total). Right: a "
  "single box measured by a ruler (per box). An arrow from right to left shows the sticker making boxes acceptable "
  "to the budget. Nong Som holds the piggy bank in one paw and the ruler in the other.",
  ["ResourceQuota", "รวมทั้งโซน", "LimitRange", "ต่อกล่อง"],
  "ResourceQuota and รวมทั้งโซน in the left column; LimitRange and ต่อกล่อง in the right column")

S13 = "13. RBAC แบบ namespace"
t("rbac-identities", S13,
  "ผู้เรียก API มีสองแบบ: คน (User) กับโปรแกรม (ServiceAccount) ServiceAccount เป็นของประจำโซน และทุกโซนมี default ให้",
  "Two staff badges on lanyards side by side: left badge with a faceless human silhouette photo; right badge worn "
  "by a small box-shaped friendly harbor robot standing inside a colored zone. Below the robot, a tiny second "
  "robot with a plain badge. Nong Som introduces them.",
  ["User", "ServiceAccount", "intern", "default"],
  "intern is the name on the big robot badge, default on the tiny robot badge; the robots are machines, not cats")
t("role-and-rolebinding", S13,
  "Role คือการ์ดสิทธิ์ (verbs + resources) RoleBinding คือสายคล้องผูกบัตรกับการ์ด มีผลเฉพาะในโซนนั้น",
  "Inside a blue zone: a rights card listing three icon pairs (eye + box, list + box, scroll + box) pinned on a "
  "board; a lanyard ribbon physically ties the robot's badge to the rights card. Outside the zone fence, the same "
  "badge has no effect (gray). Nong Som ties the lanyard knot.",
  ["Role", "RoleBinding", "get / list / watch", "pods, pods/log"],
  "Role on the card, RoleBinding on the lanyard")
t("clusterrole-with-rolebinding", S13,
  "ClusterRole เป็นสมุดกฎมาตรฐานของท่าเรือ (เช่น view) นำไปใช้ในโซนเดียวด้วย RoleBinding หรือใช้ทั้งท่าด้วย ClusterRoleBinding",
  "A thick rulebook on the central pier (shared). Left path: a single page copied into one green zone via a "
  "lanyard (local use). Right path: a megaphone broadcasting the rulebook to all zones at once, with a caution "
  "triangle. Nong Som carries the copied page.",
  ["ClusterRole: view", "RoleBinding", "ClusterRoleBinding", "ระวัง"],
  "ระวัง sits next to the right-hand ClusterRoleBinding path only")
t("auth-can-i", S13,
  "kubectl auth can-i --as=... เหมือนเครื่องอ่านบัตร ตอบ yes หรือ no ก่อนลงมือจริง",
  "A badge reader terminal at a zone door. The robot's badge is tapped: a green lamp lights for an eye icon "
  "request, a red lamp for a trash-bin icon request. Nong Som holds a clipboard and records the results.",
  ["kubectl auth can-i", "--as", "yes", "no"],
  "yes next to the green lamp, no next to the red lamp")
t("sa-token-context", S13,
  "ใช้ตัวตนของ ServiceAccount จริงด้วย token ใน context ใหม่ ระวัง: kubectl --token บน kubeconfig ที่มี client certificate ยังเป็น admin เหมือนเดิม",
  "Two lanes. Upper lane: Nong Som's wallet already holding a gold admin card, plus a token slipped in front; the "
  "gate still reads the gold card (gold light) — a warning triangle. Lower lane: a separate small wallet holding "
  "only the robot's token card; the gate reads it and opens only the robot's zone door.",
  ["kubectl create token", "--token", "admin", "context ใหม่"],
  "--token and admin in the upper lane; context ใหม่ in the lower lane; Nong Som appears once")

S14 = "14. Pod Security Admission: ด่านตรวจหน้าโซน"
t("psa-three-levels", S14,
  "Pod Security Standards มี 3 ระดับ: privileged (ปล่อยผ่าน), baseline (กันของอันตรายชัด ๆ), restricted (เข้มที่สุด)",
  "Three checkpoint gates in a row with increasing strictness: an open gate with no barrier, a gate with one "
  "barrier and a metal detector, a gate with double barriers, metal detector and a checklist scanner. Nong Som in a "
  "security vest stands at the strictest gate.",
  ["privileged", "baseline", "restricted"],
  "exactly three gates, one label each, ordered left to right as listed")
t("psa-modes", S14,
  "ตั้งด้วย label บน namespace ได้ 3 โหมด: enforce (ไม้กั้นปฏิเสธ), warn (กระดิ่งเตือนแต่ให้ผ่าน), audit (จดลงสมุดบันทึก)",
  "A zone entrance with three devices: a barrier arm blocking a box, a bell ringing while a box passes, a logbook "
  "on a podium being written by a feather pen. A zone signpost on top holds the label tag. Nong Som rings the "
  "bell.",
  ["pod-security.kubernetes.io/", "enforce", "warn", "audit"],
  "the long label prefix is on the zone signpost tag; one label per device")
t("restricted-checklist", S14,
  "ทำ Pod ให้ผ่าน restricted ด้วย securityContext: ไม่รันเป็น root, ห้ามยกระดับสิทธิ์, ทิ้ง capabilities ทั้งหมด, ใช้ seccomp RuntimeDefault",
  "A teal Pod box at the restricted gate with a checklist board beside it, four rows each with a green tick and an "
  "icon (a person with a crossed crown, an up-arrow crossed out, a toolbox emptied, a shield). Nong Som ticks the "
  "last row.",
  ["runAsNonRoot", "allowPrivilegeEscalation: false", "drop: ALL", "seccompProfile"],
  "exactly four rows, each with one label")

S15 = "15. แนวปฏิบัติการตั้งชื่อและแบ่ง namespace"
t("naming-practices", S15,
  "แบ่ง namespace ตามทีม ตาม environment หรือทั้งคู่ และให้ทุกโซนใหม่มีชุดตั้งต้น quota, LimitRange, RBAC และ Pod Security",
  "Harbor map board with zones named by team-plus-environment in a neat grid (two rows by three columns, colors "
  "by environment). Beside it a starter kit toolbox opened, containing a budget sheet, a size ruler, a badge and a "
  "mini checkpoint gate. Nong Som hands the toolbox forward.",
  ["som-dev", "som-staging", "som-prod", "ชุดตั้งต้น"],
  "only the first row of zones is labeled (som-dev, som-staging, som-prod); the second row is unlabeled decoration; "
  "ชุดตั้งต้น is on the toolbox")

S16 = "16. สรุปและคำถามทบทวน"
t("summary-harbor-zones", S16,
  "สรุปบท: ท่าเรือเดียวแบ่งโซนด้วย Namespace แต่ละโซนมีงบ กฎขนาดกล่อง บัตรพนักงาน ด่านตรวจ และรั้วของตัวเอง",
  "Sunset harbor panorama: the control tower, two worker ships carrying teal Pod boxes with three ribbon colors; "
  "above, the harbor map with three zones (green, yellow, coral), each with a tiny budget sheet, ruler, badge, "
  "checkpoint and fence icon. Nong Som salutes proudly at the dock edge.",
  ["สรุปบทที่ 4", "Namespace", "som-dev", "som-staging", "som-prod"],
  "som-dev is the green zone, som-staging the yellow zone, som-prod the coral zone, all on the map")

# ------------------------------------------------------------------ LAB
LS0 = "LAB0 สำรวจโซนเริ่มต้น"
l("lab0-survey-zones", LS0,
  "LAB0: kubectl get ns --show-labels เห็น 5 โซนตั้งต้นของ kind และ kubectl get pods -A เห็นว่า Pod ระบบอยู่ใน kube-system",
  "Nong Som at a laptop on the dock; above Nong Som a floating harbor map with five zone signs; a list card of Pod boxes "
  "with a zone column shows most boxes in the navy zone. A magnifier highlights the auto-added zone tag on one sign.",
  ["kubectl get ns", "default", "kube-system", "local-path-storage", "-A"],
  "only three of the five zones are labeled as listed; the other two zone signs are blank")
l("lab0-peek-public-lease", LS0,
  "LAB0: ดูของใน kube-public (ConfigMap cluster-info) และ kube-node-lease (Lease 3 ใบ ของเรือ 3 ลำ)",
  "Nong Som with a flashlight looks into two small zones: one with a notice board card, one with three lease cards "
  "on a rack linked to the tower and two ships by radio waves.",
  ["kube-public", "cluster-info", "kube-node-lease", "Lease x3"],
  "kube-public and kube-node-lease are zone signs; exactly three lease cards")

LS1 = "LAB1 สร้าง/ลบ namespace และ Pod ชื่อซ้ำ"
l("lab1-same-name-pods", LS1,
  "LAB1: สร้าง namespace blue และ green แล้ววาง Pod ชื่อ snack ในแต่ละโซนจากไฟล์เดียวกัน ไม่ชนกัน",
  "A YAML scroll with one Pod box drawing is photocopied twice; Nong Som drops one copy into the blue zone and "
  "another into the green zone on the harbor map; both boxes show the same name card. A third copy lands in a "
  "plain white zone.",
  ["snack-pod.yaml", "blue", "green", "default", "snack"],
  "snack is the name card printed on each box; blue, green and default are the zone signs")
l("lab1-namespace-mismatch", LS1,
  "LAB1: ไฟล์ที่เขียน metadata.namespace: green แต่สั่ง -n blue จะถูก kubectl ปฏิเสธ",
  "A Pod box with a green printed address label arrives at the blue zone gate where Nong Som is directing with "
  "a voice-bubble arrow to blue; a red error light flashes above the gate and the box bounces back.",
  ["metadata.namespace: green", "-n blue", "error"],
  "the box is not inside either zone")

LS2 = "LAB2 เปลี่ยน namespace เริ่มต้นของ context"
l("lab2-switch-context-ns", LS2,
  "LAB2: set-context --current --namespace=blue แล้ว kubectl get pods เห็นของในโซน blue ทันที อย่าลืมคืนค่าเป็น default",
  "Nong Som turns the wallet's context card over to swap its zone chip from white to blue; a terminal card behind "
  "Nong Som lists Pods from the blue zone only. A small reminder sticky-note icon with a curved return arrow sits in "
  "the corner.",
  ["kubectl config get-contexts", "kind-lab", "blue", "default"],
  "the sticky note has only the curved arrow icon, no words; default appears on the white chip")

LS3 = "LAB3 ของประจำโซน vs ของส่วนกลาง"
l("lab3-sort-scope", LS3,
  "LAB3: api-resources --namespaced=true/false และทดลองว่า kubectl get nodes -n blue ได้ผลเหมือนไม่ใส่ -n",
  "Nong Som sorts icon chips into two bins: a zone-ribbon bin (Pod box, badge, budget sheet) and a harbor bin "
  "(ship, zone signpost, warehouse, VIP flag). A ship chip wears a blue zone filter goggle that has no effect "
  "(the ship stays the same).",
  ["namespaced", "cluster-scoped", "get nodes -n blue"],
  "the third label is next to the ship chip with goggles")

LS4 = "LAB4 ข้ามโซน: Pod IP, เรือเดียวกัน และ NetworkPolicy"
l("lab4-cross-zone-ip", LS4,
  "LAB4: Pod web ใน team-a และ client ใน team-b อยู่บนเรือ lab-worker ลำเดียวกัน และ wget ถึงกันด้วย Pod IP ได้",
  "One worker ship carrying three teal Pod boxes: one blue-ribbon box with a food-bowl web sign and an IP tag, one "
  "blue-ribbon client box, one green-ribbon client box; paper-plane arrows from both client boxes reach the web "
  "box with green checks. Nong Som on the dock reads a terminal card.",
  ["web", "team-a", "team-b", "lab-worker", "wget"],
  "team-a on the blue ribbons, team-b on the green ribbon, lab-worker on the hull")
l("lab4-networkpolicy-blocks", LS4,
  "LAB4: ใส่ NetworkPolicy ให้ team-a รับเฉพาะ Pod ในโซนตัวเอง team-b ได้ download timed out จากนั้นเปิดประตูให้ team-b ด้วย namespaceSelector",
  "Two-step comic strip. Step 1: a fence appears around the blue-ribbon boxes; the green box's paper plane hits "
  "the fence (red X, small hourglass), the blue client's plane passes (green check). Step 2: a gate in the fence "
  "opens for the green box's plane (green check). Nong Som appears only in step 2, opening the gate.",
  ["1", "2", "timed out", "namespaceSelector"],
  "1 and 2 are the step numbers; timed out in step 1, namespaceSelector on the gate in step 2")

LS5 = "LAB5 ResourceQuota"
l("lab5-quota-rejects", LS5,
  "LAB5: ใบงบของโซน budget กำหนด pods: 3 Pod ที่ไม่ระบุ resources ถูกปฏิเสธ และ Pod ตัวที่ 4 ชนเพดาน exceeded quota",
  "A zone entrance with a budget sheet and a counter showing three filled slots; a box with a blank size tag is "
  "rejected at the desk on the left; a fourth properly tagged box is stopped by the barrier on the right. Nong Som "
  "holds a calculator.",
  ["budget", "pods: 3/3", "must specify", "exceeded quota"],
  "budget is the zone sign; must specify near the blank-tag box; exceeded quota near the fourth box")

LS6 = "LAB6 LimitRange"
l("lab6-limitrange-stickers", LS6,
  "LAB6: เพิ่ม LimitRange ให้โซน budget Pod ที่ไม่ระบุ resources ได้ค่า default อัตโนมัติ ส่วน Pod ที่ขอ cpu เกิน max ถูกปฏิเสธ",
  "A conveyor at the zone gate: a sticker machine stamps a size sticker on a blank box, which then passes; a giant "
  "box hits a red max height bar and is pushed back. Nong Som presses the sticker machine button.",
  ["LimitRange", "200m / 128Mi", "max 500m"],
  "200m / 128Mi is printed on the sticker; max 500m on the red bar")

LS7 = "LAB7 RBAC: บัตรพนักงานเฉพาะโซน"
l("lab7-intern-badge", LS7,
  "LAB7: ServiceAccount intern + Role pod-reader + RoleBinding ใน team-a ตรวจด้วย auth can-i --as ได้ yes เฉพาะการดู",
  "The small box-shaped harbor robot wears an intern badge tied by a lanyard to a rights card in the blue zone; a "
  "badge reader shows a green lamp for an eye icon and red lamps for a trash-bin icon and for the green zone "
  "door. Nong Som writes results on a clipboard.",
  ["intern", "pod-reader", "yes", "no"],
  "intern on the badge, pod-reader on the rights card; robot is a machine, not a cat")
l("lab7-token-context", LS7,
  "LAB7: kubectl --token ยังใช้บัตร admin เดิม ต้องสร้าง context ใหม่ที่มีแต่ token ของ intern จึงเห็นสิทธิ์จริงของ intern",
  "Two terminal windows side by side. Left: a gold admin card overlays a token slip and every zone door is open "
  "(warning triangle). Right: a slim wallet with only the robot's token; the blue zone door opens, the green zone "
  "door shows a red Forbidden light. Nong Som points at the right window.",
  ["--token", "admin", "--context intern", "Forbidden"],
  "--token and admin in the left window; --context intern and Forbidden in the right window")

LS8 = "LAB8 Pod Security Admission"
l("lab8-psa-gate", LS8,
  "LAB8: namespace secure เริ่มที่ baseline + warn restricted แล้วเปลี่ยนเป็น enforce restricted: nginx ที่รันเป็น root ถูกปฏิเสธ แต่ busybox ที่ตั้ง securityContext ครบผ่าน",
  "A zone checkpoint gate set to its strictest mode: a Pod box wearing a crown icon (root) is blocked by the "
  "barrier with a red light; a Pod box wearing a green security vest with four ticks passes with a green light; a "
  "bell above the gate rings. Nong Som operates the gate panel.",
  ["secure", "enforce=restricted", "nginx (root)", "ผ่าน"],
  "secure is the zone sign; nginx (root) next to the blocked box; ผ่าน next to the vested box")

LS9 = "LAB9 ลบโซนทั้งก้อน"
l("lab9-delete-zone", LS9,
  "LAB9: kubectl delete ns doomed ทุกอย่างข้างในหายตามไปหมด ระหว่าง Terminating สร้างของใหม่ในโซนนั้นไม่ได้",
  "Time-lapse three panels left to right: (1) a gray zone full of boxes, badges and a budget sheet; (2) the zone "
  "sign shows a Terminating tag, items fading, a new box trying to enter is blocked; (3) empty map spot with "
  "sparkles while the neighboring zone is unharmed. Nong Som appears only in panel 3, waving goodbye.",
  ["doomed", "Terminating", "1", "2", "3"],
  "doomed is the zone sign in panels 1 and 2; 1, 2, 3 are panel numbers")

LS10 = "LAB10 LAB สุดท้าย: ร้านน้องส้มแยก environment"
l("lab10-opening-three-envs", LS10,
  "LAB สุดท้าย: ร้านอาหารแมวน้องส้มแยกเป็น 3 environment คือ som-dev, som-staging, som-prod ในคลัสเตอร์เดียว ทุกโซนมี Pod ชื่อ som-shop เหมือนกัน",
  "Harbor map with three painted zones (green, yellow, coral) side by side, each zone holding one teal Pod box "
  "containing a cat-food shop stall (awning, kibble bags) with the same name card. Below, the two worker ships "
  "carry these three boxes (two on one ship, one on the other) with matching ribbon colors. Nong Som stands in "
  "front holding one YAML scroll.",
  ["som-dev", "som-staging", "som-prod", "som-shop", "som-shop.yaml"],
  "som-dev is the green zone, som-staging the yellow zone, som-prod the coral zone; som-shop is the name card on "
  "the boxes; som-shop.yaml on the scroll")
l("lab10-downward-namespace", LS10,
  "ไฟล์เดียวแต่หน้าร้านแต่ละ env ต่างกัน: Downward API ส่ง metadata.namespace เข้า env POD_NAMESPACE แล้วต่อเป็น SHOP_NAME",
  "Close-up of one teal shop Pod box in the coral zone: a faceless first mate silhouette pins a name banner on the "
  "shop awning, copying text from the coral zone signpost via a dotted arrow. A small card shows the env chain "
  "with two arrows. Nong Som admires the banner.",
  ["metadata.namespace", "POD_NAMESPACE", "SHOP_NAME", "som-prod"],
  "som-prod is the coral zone signpost; the banner on the awning is a plain decorative ribbon with no text")
l("lab10-prod-guardrails", LS10,
  "som-prod มีชุดป้องกันครบ: ResourceQuota (งบ), LimitRange (ขนาดกล่อง) และ Pod Security แบบ restricted ที่หน้าโซน",
  "The coral zone entrance: a checkpoint gate in strictest mode, a budget sheet with gauges on the left post, a "
  "standard box-size signboard on the right post. Green and yellow zones in the background have only a bell "
  "(warn) and no barrier. Nong Som stands guard at the coral gate in a security vest.",
  ["som-prod", "ResourceQuota", "LimitRange", "restricted", "warn"],
  "som-prod is the coral zone sign; warn appears next to the bell of the background zones")
l("lab10-old-shop-rejected", LS10,
  "ร้านฉบับบท 002 (ไม่มี securityContext) ถูกด่าน restricted ของ som-prod ปฏิเสธ ส่วนฉบับใหม่ที่รันด้วย uid 70 และ 1000 ผ่านเข้าไป",
  "At the coral zone gate: an older shop Pod box (slightly faded, with a crown icon for root) is blocked with a red "
  "light; a new shop Pod box wearing a security vest with ticks and two small id tags passes with a green light. "
  "Nong Som holds the gate checklist.",
  ["som-shop-v002.yaml", "Forbidden", "som-shop.yaml", "uid 70 / 1000"],
  "som-shop-v002.yaml and Forbidden near the blocked old box; som-shop.yaml and uid 70 / 1000 near the passing box",
  nt=True)
l("lab10-prod-quota-third-branch", LS10,
  "ใน som-prod เปิดสาขาที่ 2 ได้ แต่สาขาที่ 3 ชนงบ ResourceQuota (pods: 2) ถูกปฏิเสธ",
  "Coral zone with two shop Pod boxes inside and a budget counter showing two of two; a third shop Pod box on a "
  "hand cart is stopped at the barrier with a red light. Nong Som shows the full budget sheet.",
  ["som-shop", "som-shop-2", "som-shop-3", "pods: 2/2", "exceeded quota"],
  "som-shop and som-shop-2 are name cards on the two boxes inside; som-shop-3 on the blocked box",
  nt=True)
l("lab10-intern-dev-only", LS10,
  "ServiceAccount intern ดูได้อย่างเดียวและเฉพาะ som-dev: get/list/logs ได้ แต่ลบไม่ได้และเข้า som-prod ไม่ได้",
  "The small box-shaped harbor robot with an intern badge stands at a badge reader grid: a table with three rows "
  "(eye icon, scroll icon, trash icon) and two columns (green zone, coral zone) filled with green and red lamps — "
  "green for eye and scroll in the green zone column only, red everywhere else. Nong Som points at the grid.",
  ["intern", "som-dev", "som-prod", "get / list / logs", "delete"],
  "som-dev heads the green column, som-prod the coral column; get / list / logs labels the eye-and-scroll rows "
  "area, delete labels the trash row; robot is a machine, not a cat")
l("lab10-three-port-forwards", LS10,
  "เปิดหน้าร้านทั้ง 3 env พร้อมกัน: port-forward คนละ port (3001/3002/3003) แล้ว ssh -L ไปยัง browser บนเครื่องนักศึกษา",
  "Left: the three colored zones each with a shop Pod box; three colored pipes (green, yellow, coral) run from the "
  "boxes through a single SSH tunnel tube into a laptop on the right. The laptop screen shows three browser tabs, "
  "each with a cat-food shop page tinted in the matching zone color. Nong Som sits at the laptop.",
  ["3001", "3002", "3003", "ssh -L", "localhost"],
  "3001 on the green pipe, 3002 on the yellow pipe, 3003 on the coral pipe; browser tabs contain no readable text",
  nt=True)
l("lab10-delete-dev", LS10,
  "ลบ som-dev ทั้ง namespace: ร้าน dev, บัตร intern และสิทธิ์หายไปทั้งหมด แต่ som-staging และ som-prod ยังเปิดขายตามปกติ",
  "The green zone on the harbor map is erased by a giant eraser with sparkles; the intern robot's badge fades to "
  "gray; the yellow and coral zones beside it still have shop boxes with lights on and a happy cat-food customer "
  "silhouette at the coral shop. Nong Som holds the eraser handle.",
  ["kubectl delete ns som-dev", "som-staging", "som-prod"],
  "som-staging is the yellow zone sign, som-prod the coral zone sign; the erased green zone has no sign left",
  nt=True)
l("lab10-wrap-up", LS10,
  "สรุป LAB: namespace เดียวกันกับไฟล์เดียว ใช้แยก environment ได้ พร้อมงบ ขนาดกล่อง สิทธิ์ ด่านตรวจ และลบทั้งก้อนได้ในคำสั่งเดียว",
  "Checklist board with five ticked rows, each with an icon: a painted zone, a budget sheet, a size ruler, a staff "
  "badge, a checkpoint gate. Nong Som gives a big thumbs up next to the board with the harbor in the background.",
  ["Namespace", "ResourceQuota", "LimitRange", "RBAC", "Pod Security"],
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
            "prompt": prompt(scene, labels, extra, allow),
        }
        if nt:
            d["needs_test"] = True
        out.append(d)
    return out


def write_md(items, title, path):
    lines = ["Prompts for built-in image_gen via cyolo1 using 00-character-som.png as character reference", "",
             f"# Final image prompts — 004 Kubernetes Namespace ({title})", "",
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
