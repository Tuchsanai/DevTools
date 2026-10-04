#!/usr/bin/env python3
"""สร้าง images.json + imagegen-prompts.md ของบท 003 (Node กับ Pod)"""
import json, os

ROOT = "/root/workspace/DevTools/k/003_kubernetes_node_pod"
OUT_JSON = "/root/workspace/DevTools/k/logs/003_node_pod/images.json"

USE_CASE = ("Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai "
            "university DevTools course; must teach the concept correctly at a glance.")
ASSET = ("Asset type: landscape 3:2 educational story illustration for Thai Kubernetes Node and Pod scheduling "
         "lesson (README figure, about 1536x1024).")
CHAR = ("Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby "
        "orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, "
        "big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with "
        "a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and "
        "neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly.")
STYLE = ("Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, white background, palette "
         "navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; "
         "matches the chapter 001 and chapter 002 classroom illustration set. Shared metaphor (keep consistent across "
         "the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps "
         "one or more shipping containers and carries one small IP tag, and a Pod always sits on exactly one ship; "
         "Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock "
         "(lab-control-plane), which is also a node but carries a red no-boarding sign; kube-scheduler = harbor "
         "loading officer with a clipboard; kubelet = first mate drawn as a friendly faceless sailor silhouette in navy uniform (never a second cat); node label = small "
         "flag on the ship mast; taint = red 'no boarding' sign hung on the ship rail; toleration = boarding pass card "
         "held by a Pod box; affinity = attracting magnet, anti-affinity = repelling magnet. Every cargo item, crate "
         "or prop is cat-food-shop related only (kibble bags, cat food cans, fish-shaped treats, food bowls).")
BASE_CONS = ("only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish "
             "or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; "
             "every row, column, lane or panel that is drawn has one of the listed labels or is clearly unlabeled "
             "decoration; a Pod box is never split across two ships")
NO_CTRL = ("; do not show Service, NodePort, Deployment, ReplicaSet, DaemonSet or Ingress objects or words")


def prompt(scene, labels, extra="", allow_ctrl=False):
    lab = "; ".join(f'"{l}"' for l in labels)
    cons = BASE_CONS + ("" if allow_ctrl else NO_CTRL) + (f"; {extra}" if extra else "") + "."
    return "\n".join([
        USE_CASE, ASSET, f"Scene: {scene}", CHAR, STYLE,
        f"Text (verbatim, at most {len(labels)} short labels): {lab}.",
        f"Constraints: {cons}",
    ])


T = []  # (slug, section, caption, scene, labels, extra, allow_ctrl)
L = []

def t(slug, section, cap, scene, labels, extra="", allow=False):
    T.append((slug, section, cap, scene, labels, extra, allow))

def l(slug, section, cap, scene, labels, extra="", allow=False):
    L.append((slug, section, cap, scene, labels, extra, allow))

# ------------------------------------------------------------------ THEORY
S1 = "1. บทนำ: ร้านน้องส้มอยากมีหลายสาขา"
t("opening-fleet-branches", S1,
  "ร้านอาหารแมวน้องส้มจากบทที่ 2 ขายดีจนอยากเปิดหลายสาขา แต่กล่อง Pod แต่ละกล่องจะไปอยู่บนเรือลำไหน ใครเป็นคนเลือก",
  "Morning at the Kubernetes harbor. Nong Som stands on the dock holding a teal Pod box that contains a small cat-food "
  "shop stall (awning, kibble bags), looking out at a fleet: the control tower on the dock and two worker cargo ships "
  "side by side. A big floating question mark hovers between the Pod box and the two ships. Mood: curious beginning of "
  "a new chapter.",
  ["ร้านอาหารแมวน้องส้ม", "Node กับ Pod", "บทที่ 3", "lab-worker", "lab-worker2"],
  "the control tower is drawn but not labeled; no Pod is on any ship yet")
t("new-metaphor-map", S1,
  "แผนผังอุปมาใหม่ของบทนี้: ธงบนเรือ = node label, ป้ายห้ามขึ้น = taint, บัตรผ่าน = toleration, แม่เหล็ก = affinity/anti-affinity, เชือกกั้น = cordon",
  "A clean legend board with five illustrated rows, each row = one icon on the left and its Kubernetes term on the "
  "right: (1) a small flag on a ship mast, (2) a red no-boarding sign on a ship rail, (3) a boarding pass card, "
  "(4) a pair of magnets one pulling and one pushing, (5) a rope barrier across a gangway. Nong Som points at the "
  "board with a pointer stick.",
  ["node label", "taint", "toleration", "affinity", "cordon"],
  "exactly five rows and each row has exactly one of the five labels; the taint sign is a sign, never a stain or dirt; "
  "the cordon is a rope barrier, never police tape")

S2 = "2. ทบทวน Node: เรือหนึ่งลำมีอะไรบ้าง"
t("node-anatomy", S2,
  "เรือ (Node) หนึ่งลำมี kubelet เป็นต้นเรือ, container runtime เป็นห้องเครื่องยกตู้ และ kube-proxy ดูแลเส้นทางจราจร",
  "Cutaway side view of one worker cargo ship. On the bridge the first mate (faceless sailor silhouette) holds a "
  "radio connected by a dotted line to the control tower. Below deck an engine room with a crane lifting a shipping "
  "container into a teal Pod box. On the deck a traffic-guide post with arrows. Three Pod boxes sit on deck holding "
  "cat-food containers. Nong Som explains with an open palm beside the ship.",
  ["kubelet", "container runtime", "kube-proxy", "Pod", "lab-worker"],
  "the first mate is a faceless sailor silhouette, not a cat; only one ship")
t("kind-nodes-are-containers", S2,
  "ใน kind แต่ละ Node คือ Docker container ที่รันอยู่ใน k8s-lab จึงจำลองเรือล่มได้ด้วย docker stop",
  "A large rounded card labeled k8s-lab like a bottle-ship display case. Inside it three big shipping containers "
  "stand in a row, and each container has a small ship drawn emerging from it, showing that each node is itself "
  "a container: the left one becomes the control tower, the other two become cargo ships. Nong Som peeks in with "
  "a magnifying glass.",
  ["k8s-lab", "docker ps", "lab-control-plane", "lab-worker", "lab-worker2"],
  "exactly three node containers with matching labels; no extra ships")

S3 = "3. Node object: สมุดประจำเรือ"
t("node-standard-labels", S3,
  "label มาตรฐานของ Node เปรียบเป็นธงบนเสากระโดง เช่น kubernetes.io/hostname, kubernetes.io/os, kubernetes.io/arch",
  "Close-up of a cargo ship's mast with three neat flags stacked vertically, each flag a pennant carrying one label "
  "text. Nong Som on deck salutes the flags. A small notebook (ship registry) lies at her feet.",
  ["kubernetes.io/hostname=lab-worker", "kubernetes.io/os=linux", "kubernetes.io/arch=amd64"],
  "exactly three flags, each with one label written clearly; no other flags")
t("capacity-vs-allocatable", S3,
  "capacity คือระวางเรือทั้งหมด allocatable คือส่วนที่เหลือให้ Pod หลังหักส่วนที่สงวนไว้ให้ระบบ",
  "Side view of a cargo ship's hold as a big bar: the whole hold outlined and labeled capacity; a smaller section "
  "at one end shaded gray holding crew supplies (reserved for the system); the rest shaded teal labeled allocatable "
  "with cat-food crates. A bracket under the whole bar and a bracket under the teal part. Nong Som measures with a "
  "tape measure.",
  ["capacity", "allocatable", "สงวนไว้ให้ระบบ"],
  "the allocatable bracket is clearly shorter than the capacity bracket and contained inside it")
t("node-conditions-panel", S3,
  "สถานะ (conditions) ของ Node เหมือนไฟบนแผงเรือ: Ready ต้องเป็น True ส่วน MemoryPressure, DiskPressure, PIDPressure ควรเป็น False",
  "A ship's control panel with four labeled indicator lamps in a row: the Ready lamp glows green, the other three "
  "lamps are dark gray (off). Each lamp has its label above it. Nong Som checks the panel with a clipboard and nods "
  "happily.",
  ["Ready", "MemoryPressure", "DiskPressure", "PIDPressure"],
  "exactly four lamps, each with exactly one label; only Ready is lit green; the word pressure must not be drawn as "
  "steam, pumps or pressure gauges")
t("describe-node-logbook", S3,
  "kubectl describe node เหมือนเปิดสมุดประจำเรือ เห็น Labels, Taints, Conditions, Allocatable และผลรวม requests ของ Pod บนเรือ",
  "Nong Som reads a big open logbook on a lectern on the dock; a cargo ship lab-worker floats behind. The logbook "
  "pages show five tabbed sections with simple icons: flags, a no-boarding sign, indicator lamps, a hold bar, and "
  "a stack of Pod boxes with a sum symbol.",
  ["kubectl describe node", "Labels", "Taints", "Conditions", "Allocated resources"],
  "the logbook shows only the five tab labels and simple icons, no paragraph text")

S4 = "4. kube-scheduler: เจ้าหน้าที่จัดตู้ขึ้นเรือ"
t("scheduler-watches-unscheduled", S4,
  "Pod ใหม่ที่ยังไม่มี nodeName รอที่ท่า kube-scheduler หยิบมาเลือกเรือ แล้ว kubelet บนเรือนั้นเป็นคนสร้าง container",
  "A left-to-right flow on the dock: a teal Pod box waits in a queue area marked with an empty name tag; the "
  "loading officer with a clipboard inspects it; an arrow leads to a binding stamp that writes a ship name on the "
  "tag; final arrow to a ship where the first mate lifts the Pod box aboard. Nong Som follows along the flow.",
  ["nodeName: (ว่าง)", "kube-scheduler", "Binding", "nodeName: lab-worker2", "kubelet"],
  "the scheduler only chooses and stamps, it does not carry the box; only one Pod box shown at each stage")
t("filter-score-bind", S4,
  "scheduler ทำ 3 ขั้น: Filtering ตัดเรือที่รับไม่ได้ → Scoring ให้คะแนนเรือที่เหลือ → Binding ผูก Pod กับเรือคะแนนสูงสุด",
  "Three labeled panels left to right. Panel 1: the loading officer crosses out the control tower (it has a red "
  "no-boarding sign) with a red X while two ships get green checks. Panel 2: the two remaining ships get score cards "
  "with stars (one has 3 stars, the other 2). Panel 3: the Pod box is tied with a rope to the 3-star ship. Nong Som "
  "watches holding a teal Pod box.",
  ["1 Filtering", "2 Scoring", "3 Binding", "lab-control-plane"],
  "exactly three panels each labeled; the control tower is filtered out, never chosen")
t("pending-failedscheduling", S4,
  "ถ้าไม่มีเรือลำไหนผ่าน filter Pod จะ Pending และมี Event FailedScheduling บอกเหตุผลของทุก node",
  "A teal Pod box with an oversized pile of kibble sacks sits alone on the dock with a yellow Pending tag. Three "
  "small cards fly from the officer's clipboard, one per node: the control tower card shows a no-boarding sign icon, "
  "the two ship cards show an overfilled-hold icon. Nong Som scratches her head reading a notice board.",
  ["Pending", "FailedScheduling", "0/3 nodes are available", "untolerated taint", "Insufficient memory"],
  "exactly three reason cards (one per node: 1 tower + 2 ships); nothing is broken or sinking")

S5 = "5. requests เทียบ allocatable"
t("requests-sum-vs-allocatable", S5,
  "scheduler ดูผลรวม requests ของ Pod บนเรือเทียบ allocatable ไม่ได้ดูการใช้งานจริง เมื่อเต็มแล้ว Pod ตัวถัดไปต้อง Pending",
  "A ship's hold drawn as a capacity gauge labeled allocatable with two Pod boxes already reserving blocks of space "
  "(each block tagged with its request). A third Pod box hangs from a crane above but its reserved block does not "
  "fit in the remaining gap; a yellow Pending tag. A small side note shows a thermometer-like usage meter that is "
  "low, crossed out to show actual usage is not what counts. Nong Som points at the reserved blocks.",
  ["allocatable cpu: 4", "requests 1500m", "requests 1500m", "requests 1500m", "Pending", "ดูจาก requests"],
  "the two placed blocks plus the third clearly exceed the gauge; the usage meter is small and secondary")

S6 = "6. nodeName: ข้ามเจ้าหน้าที่จัดตู้"
t("nodename-bypass", S6,
  "การใส่ nodeName คือเดินผ่านเจ้าหน้าที่จัดตู้ตรงไปหาต้นเรือเลย จึงไม่ผ่าน filter ของ scheduler ใช้เพื่อทดลองเท่านั้น",
  "Nong Som carries a teal Pod box with a pre-written name tag directly along a side gangway to a ship, walking past "
  "the loading officer who raises an eyebrow and holds an unused clipboard. A dashed arrow shows the normal route "
  "through the officer, a solid arrow shows the shortcut route.",
  ["nodeName: lab-worker", "ข้าม scheduler", "kube-scheduler", "ใช้ทดลองเท่านั้น"],
  "the shortcut arrow goes around the officer directly to the ship")

S7 = "7. nodeSelector"
t("nodeselector-flag-match", S7,
  "nodeSelector คือใบสั่งว่า Pod ต้องขึ้นเรือที่มีธงตรงกันเท่านั้น ถ้าไม่มีเรือลำไหนติดธงนั้น Pod จะ Pending",
  "Two cargo ships: lab-worker flies a green flag, lab-worker2 flies an orange flag. A teal Pod box holds a "
  "ticket showing the orange flag and boards only lab-worker2 along a dotted path; a crossed path toward lab-worker. "
  "Nong Som hangs the orange flag on the mast with a pole.",
  ["fleet=eco", "fleet=fast", "nodeSelector: fleet=fast", "lab-worker", "lab-worker2"],
  "fleet=eco is the flag on lab-worker and fleet=fast is the flag on lab-worker2; the Pod lands on lab-worker2 only")

S8 = "8. Node affinity"
t("node-affinity-required-preferred", S8,
  "node affinity แบบ required คือแม่เหล็กที่ต้องดูดติดเท่านั้น ส่วน preferred คือแม่เหล็กที่อยากได้ถ้าไม่มีก็ไปเรือลำอื่นได้",
  "Two side-by-side labeled panels. Left: a strong magnet on a Pod box locks onto a flag on a ship with a padlock "
  "icon; a second ship without the flag gets a red X. Right: a gentle magnet on a Pod box leans toward a flagged "
  "ship with a weight tag, while a dotted alternative arrow to an unflagged ship has a green check. Nong Som stands "
  "between the panels.",
  ["required (ต้อง)", "preferred (อยากได้)", "weight: 80"],
  "left panel = hard rule, right panel = soft rule; every panel labeled")
t("affinity-operators", S8,
  "ตัวดำเนินการของ node affinity: In, NotIn, Exists, DoesNotExist, Gt, Lt ใช้เทียบ label ของเรือ",
  "A tidy grid of six labeled tiles, each showing a tiny ship with flags and a magnet symbol: In (flag in a set "
  "bubble), NotIn (flag crossed in set bubble), Exists (any flag present), DoesNotExist (bare mast), Gt (deck number "
  "with greater sign), Lt (deck number with less sign). Nong Som holds a magnifier beside the grid.",
  ["In", "NotIn", "Exists", "DoesNotExist", "Gt", "Lt"],
  "exactly six tiles, each with exactly one operator label")

S9 = "9. Inter-pod affinity / anti-affinity"
t("pod-affinity-anti", S9,
  "pod affinity คือแม่เหล็กดึงกล่องให้อยู่ใกล้ Pod ที่มี label ตรง ส่วน pod anti-affinity คือแม่เหล็กผลักไม่ให้อยู่เรือลำเดียวกัน",
  "Two labeled panels. Left: a web Pod box is pulled by a magnet onto the same ship as a cache Pod box (fish-snack "
  "cooler). Right: two shop-branch Pod boxes with repelling magnets push apart and sit on two different ships. "
  "Nong Som juggles a pair of magnets.",
  ["podAffinity", "podAntiAffinity", "app=cache", "web", "สาขา"],
  "left: both Pods on the same ship; right: the two branch Pods on different ships")
t("topologykey-meaning", S9,
  "topologyKey บอกว่า \"ใกล้\" หมายถึงอะไร kubernetes.io/hostname คือเรือลำเดียวกัน ส่วน zone คือท่าเรือเดียวกัน",
  "A map with two harbor zones outlined by dashed lines, each zone holding two ships. A first highlight circle wraps "
  "a single ship; a second larger highlight wraps a whole harbor zone. Pod boxes with magnet icons are shown inside. "
  "Nong Som draws the outlines with a marker.",
  ["topologyKey", "kubernetes.io/hostname", "topology.kubernetes.io/zone", "zone-a", "zone-b"],
  "the hostname circle covers exactly one ship; the zone outline covers a group of ships; the ship names are not "
  "shown here (illustrative cloud example; kind has no zones)")

S10 = "10. topologySpreadConstraints"
t("topology-spread-maxskew", S10,
  "topologySpreadConstraints เหมือนตาชั่งกองเรือ จำนวน Pod ระหว่างเรือต่างกันได้ไม่เกิน maxSkew",
  "A giant balance scale on the dock with two ship-shaped pans: left pan holds 2 Pod boxes, right pan holds 2 Pod "
  "boxes, perfectly level; a third separate inset shows a 3-vs-1 imbalance with a red X. Nong Som stands at the "
  "scale's pivot.",
  ["maxSkew: 1", "lab-worker", "lab-worker2", "2 : 2", "3 : 1"],
  "the 2 : 2 scale is level and approved; the 3 : 1 inset is rejected")
t("spread-control-plane-trap", S10,
  "กับดักใน kind: ค่าเริ่มต้น nodeTaintsPolicy: Ignore นับ control-plane ที่มี taint เป็นช่องที่มี 0 Pod ทำให้ Pod ตัวที่ 3 Pending ต้องตั้ง Honor",
  "Two labeled panels. Left: three columns (control tower with no-boarding sign holding 0 boxes, ship lab-worker 1 "
  "box, ship lab-worker2 1 box); a third Pod box waits with a yellow Pending tag. Right: the control tower column is "
  "grayed out and excluded by a bracket, the two ships each hold 2 boxes, all happy. Nong Som flips a switch between "
  "the panels.",
  ["Ignore", "Honor", "lab-control-plane: 0", "Pending", "nodeTaintsPolicy"],
  "no Pod box ever sits on the control tower in either panel")

S11 = "11. Taints & Tolerations"
t("taint-and-toleration", S11,
  "taint คือป้ายห้ามขึ้นที่ติดบนเรือ toleration คือบัตรผ่านที่ติดกับ Pod มีบัตรตรงกันจึงขึ้นเรือได้",
  "A ship lab-worker2 has a red no-boarding sign on its rail. A Pod box holding a matching boarding pass walks up "
  "the gangway with a green check; another Pod box without a pass is stopped at the gangway with a red X. Nong Som "
  "checks the passes as a gate attendant.",
  ["taint: dedicated=vip:NoSchedule", "toleration", "lab-worker2"],
  "the taint is a sign on the ship (node), the toleration is a card on the Pod; do not draw taint as stain, dirt or "
  "contamination")
t("taint-effects", S11,
  "effect ของ taint: NoSchedule ไม่รับใหม่, PreferNoSchedule เลี่ยงถ้าได้, NoExecute ไม่รับใหม่และไล่ Pod ที่ไม่มีบัตรลงจากเรือ",
  "Three labeled ship panels side by side. NoSchedule: a red sign, a new Pod box blocked at gangway, old Pod box "
  "still on deck. PreferNoSchedule: a yellow sign, a Pod box hesitates but may board. NoExecute: a red sign with an "
  "outward arrow, a Pod box without a pass being walked off the ship onto the dock while a Pod with a pass stays. "
  "Nong Som points to the third panel.",
  ["NoSchedule", "PreferNoSchedule", "NoExecute"],
  "exactly three panels each labeled with one effect; the existing Pod stays aboard in NoSchedule")
t("control-plane-taint-kind", S11,
  "ใน kind หอบังคับการ lab-control-plane มี taint node-role.kubernetes.io/control-plane:NoSchedule Pod ทั่วไปจึงไปลงเฉพาะเรือ worker",
  "The control tower on the dock (also a node) has a big red no-boarding sign. Pod boxes with cat-food cargo go "
  "only to the two worker ships. One special Pod box holding a boarding pass is allowed into the tower area. Nong Som "
  "stands at the tower door as guard.",
  ["node-role.kubernetes.io/control-plane:NoSchedule", "lab-control-plane", "lab-worker", "lab-worker2", "toleration"],
  "only the Pod with the pass enters the tower; ordinary Pods are on the worker ships")
t("noexecute-tolerationseconds", S11,
  "NoExecute กับ tolerationSeconds: Pod ไม่มีบัตรถูกไล่ทันที, บัตรแบบมีเวลาอยู่ได้ตามนาฬิกาทราย, บัตรไม่มีเวลาอยู่ต่อได้",
  "A ship with a red NoExecute sign and a timeline ribbon across the bottom from 0s to 30s. Three Pod boxes on deck: "
  "the first without a pass already stepping off at 0s, the second holds a pass with an hourglass and steps off at "
  "30s, the third holds a pass with an infinity mark and stays. Nong Som holds a stopwatch.",
  ["NoExecute", "ไม่มีบัตร: ออกทันที", "tolerationSeconds: 30", "บัตรไม่จำกัดเวลา: อยู่ต่อ", "0s", "30s"],
  "each of the three Pods has exactly one of the three state labels; the Pods leave the ship, they are not destroyed")
t("toleration-not-attraction", S11,
  "มีบัตรผ่านไม่ได้แปลว่าต้องไปเรือลำนั้น ถ้าอยากได้เรือเฉพาะกิจต้องใช้ taint + toleration + node affinity คู่กัน",
  "Two labeled panels. Left: a VIP Pod box with a boarding pass wanders onto an ordinary ship (no sign) — a "
  "surprised face. Right: the VIP Pod box has both the pass and a magnet pulling it to the flagged VIP ship with "
  "the red sign; ordinary Pods without passes stay off it. Nong Som gives a thumbs-up to the right panel.",
  ["toleration อย่างเดียว", "taint + toleration + affinity", "dedicated=vip"],
  "left panel shows a possible but unwanted outcome, right panel is the recommended pattern")

S12 = "12. บำรุงรักษา node: cordon / drain / uncordon"
t("cordon-rope", S12,
  "kubectl cordon คือเชือกกั้นท่าเรือ เรือขึ้นสถานะ SchedulingDisabled ไม่รับ Pod ใหม่ แต่ Pod เดิมยังอยู่บนเรือ",
  "Nong Som ties a rope barrier across the gangway of lab-worker. Two existing Pod boxes stay on deck calmly. A new "
  "Pod box is redirected by an arrow to the other ship lab-worker2.",
  ["kubectl cordon", "SchedulingDisabled", "lab-worker", "lab-worker2"],
  "the rope barrier is a simple harbor rope with posts, not police tape; existing Pods remain aboard")
t("drain-standalone-pods-gone", S12,
  "kubectl drain ย้ายของลงจากเรือ Pod เดี่ยวต้องใช้ --force และถูกลบหายไปเลย ไม่มีใครสร้างใหม่บนเรือลำอื่น",
  "The cordoned ship lab-worker: the crew carries Pod boxes down the gangway; on the dock the unloaded standalone Pod "
  "boxes fade into dotted outlines (gone), while the other ship lab-worker2 shows an empty dotted spot with a big "
  "question mark (no replacement appears). Two small system Pods with a gear icon remain on the ship. Nong Som looks "
  "concerned holding an empty clipboard.",
  ["kubectl drain", "--force", "Pod เดี่ยวหายไป", "ไม่มีการสร้างใหม่", "lab-worker2"],
  "do NOT draw a literal drain, plumbing, pipes, sinks or water draining; no new Pod box appears on lab-worker2; the "
  "gear-icon system Pods stay on lab-worker")
t("uncordon-but-not-back", S12,
  "kubectl uncordon เอาเชือกออก เรือกลับมารับ Pod ใหม่ได้ แต่ Pod ที่ถูก drain ไปแล้วไม่กลับมาเอง",
  "Nong Som unties and coils the rope at lab-worker's gangway; the deck is empty except for two small gear-icon "
  "system Pods. A thought bubble shows the former Pod boxes as dotted outlines with a crossed return arrow.",
  ["kubectl uncordon", "Ready", "ไม่กลับมาเอง"],
  "no Pod boxes automatically return")

S13 = "13. เมื่อเรือล่ม: Node NotReady"
t("heartbeat-fog-notready", S13,
  "kubelet ส่งสัญญาณ heartbeat ทุกประมาณ 10 วินาที เมื่อเงียบไปนานเกิน grace period หอบังคับการเปลี่ยนเรือเป็น NotReady",
  "Left: ship lab-worker sends radio wave arcs to the control tower with a green heartbeat icon. Right: ship "
  "lab-worker2 is wrapped in thick gray fog, its radio silent (crossed-out wave), and the tower's status board shows "
  "a red light next to it. Nong Som on the tower balcony looks through binoculars into the fog.",
  ["Lease ทุก ~10s", "NotReady", "lab-worker", "lab-worker2", "Ready: Unknown"],
  "the fogged ship is intact, not sinking or broken; the Pod boxes on it are faint inside the fog")
t("auto-taints-unreachable", S13,
  "ระบบใส่ taint อัตโนมัติ node.kubernetes.io/unreachable ให้เรือที่ขาดการติดต่อ และทุก Pod มีบัตรผ่านเริ่มต้น 300 วินาที",
  "The fogged ship lab-worker2 gets two red signs hung automatically by a robotic arm from the tower. On deck each "
  "Pod box holds a default boarding pass with a 5-minute hourglass. A timeline at the bottom from 0s to 300s. Nong "
  "Som reads the timeline.",
  ["node.kubernetes.io/unreachable:NoSchedule", "node.kubernetes.io/unreachable:NoExecute", "tolerationSeconds: 300",
   "0s", "300s"],
  "two signs on the fogged ship; hourglasses on the Pods")
t("evicted-terminating-no-replacement", S13,
  "เมื่อหมดเวลา Pod บนเรือที่ล่มถูกไล่ (evict) ค้างสถานะ Terminating จนเรือกลับมา และ Pod เดี่ยวจะไม่ถูกสร้างใหม่บนเรือลำอื่น",
  "Three labeled steps left to right: (1) fogged ship with Pod boxes and an hourglass emptied; (2) the Pod boxes "
  "turn semi-transparent with a gray Terminating tag while still in the fog; (3) the fog clears, the ship returns "
  "with an empty deck and the healthy ship lab-worker next to it has no new box, only a question mark. Nong Som "
  "looks thoughtful.",
  ["1 หมดเวลา", "2 Terminating", "3 เรือกลับ: Pod หายไป", "ไม่มีใครสร้างใหม่"],
  "no new Pod box appears anywhere; the ship is not destroyed")

S14 = "14. Static Pod"
t("static-pod-first-mate", S14,
  "static Pod คือตู้ที่ต้นเรือ (kubelet) สร้างเองจากแฟ้มบนเรือ /etc/kubernetes/manifests ไม่ผ่านหอบังคับการและ scheduler",
  "On ship lab-worker the first mate (faceless sailor silhouette) reads a binder from a shelf and assembles a Pod "
  "box (a small cat-snack stall) by hand. The control tower in the distance shows only a ghostly reflection "
  "copy of that Pod on its board. The loading officer is absent from this route. Nong Som watches with paws on hips.",
  ["/etc/kubernetes/manifests", "kubelet", "static Pod", "mirror pod", "lab-worker"],
  "the mirror pod on the tower board is a transparent ghost copy, not a second real Pod; the first mate is not a cat; no lighthouse")
t("control-plane-static-pods", S14,
  "บน lab-control-plane ส่วนประกอบหลัก etcd, kube-apiserver, kube-controller-manager, kube-scheduler เป็น static Pod ที่ kubelet ของหอรันเอง",
  "Cutaway of the control tower showing four labeled rooms stacked as floors, each room a teal Pod box: a vault "
  "room, a front desk, a manager office, the loading officer's desk. A binder labeled manifests at the ground floor "
  "connects with dotted lines to all four rooms. Nong Som climbs the stairs pointing up.",
  ["etcd", "kube-apiserver", "kube-controller-manager", "kube-scheduler", "lab-control-plane"],
  "exactly four rooms, each with exactly one component label")

S15 = "15. Downward API"
t("downward-api-nametag", S15,
  "Downward API ให้ Pod รู้ข้อมูลตัวเอง เช่น spec.nodeName เป็น env NODE_NAME แล้วนำไปต่อข้อความด้วย $(NODE_NAME)",
  "The first mate stamps a name plate onto a Pod box as it boards ship lab-worker2. Inside the Pod box a small shop "
  "sign lights up with the ship name. A side card shows three env lines pointing from the Pod box. Nong Som reads "
  "the shop sign happily.",
  ["NODE_NAME=lab-worker2", "POD_IP=10.244.2.5", "metadata.name", "สาขา $(NODE_NAME)"],
  "the value lab-worker2 matches the ship the Pod is on")

S16 = "16. QoS กับ node-pressure eviction"
t("qos-node-pressure-eviction", S16,
  "เมื่อเรือใกล้เต็ม (MemoryPressure) kubelet ไล่ Pod ออกตามลำดับ QoS: BestEffort ก่อน, Burstable ที่ใช้เกิน requests, Guaranteed หลังสุด",
  "A ship with an amber MemoryPressure lamp lit on its panel. Three Pod boxes on deck in a queue toward the gangway "
  "with numbered badges 1, 2, 3: first a BestEffort box (no reservation tag), second a Burstable box overflowing its "
  "tag, third a Guaranteed box with a shield. The first one is being walked off. Nong Som holds a priority list.",
  ["MemoryPressure", "1 BestEffort", "2 Burstable", "3 Guaranteed", "Evicted"],
  "pressure is a status lamp, never steam or a pressure cooker; only the first Pod is leaving")

S17 = "17. Priority และ Preemption"
t("priority-preemption", S17,
  "PriorityClass ให้ Pod สำคัญแซงคิวได้ เมื่อเรือเต็ม scheduler อาจไล่ Pod priority ต่ำออก (preemption) เพื่อเปิดที่ให้",
  "A full ship; a Pod box with a gold VIP ribbon and high number arrives at the gangway; a low-priority Pod box with "
  "a small number steps aside onto the dock to free space. The loading officer gestures the VIP in. Nong Som "
  "watches with a cautious expression.",
  ["PriorityClass", "priority: 1000000", "priority: 0", "preemption"],
  "only one low-priority Pod leaves")

S18 = "18. เลือกเครื่องมือจัดวางแบบไหนเมื่อไร"
t("placement-cheatsheet", S18,
  "ตารางเลือกเครื่องมือจัดวาง: ต้องการเรือชนิดหนึ่ง ใช้ nodeSelector/node affinity, อยู่ใกล้/ห่าง Pod อื่น ใช้ pod (anti-)affinity, กระจาย ใช้ spread, กันเรือ ใช้ taint",
  "A neat cheat-sheet board with six labeled rows, each row = an icon and a tool name: flag, magnet to flag, pair "
  "of magnets, balance scale, red sign with boarding pass, rope barrier. Nong Som presents the board like a teacher.",
  ["nodeSelector", "node affinity", "pod (anti-)affinity", "topologySpread", "taint + toleration", "cordon / drain"],
  "exactly six rows, each row has exactly one of these labels; no extra words")

S19 = "19. ปูทางบทหน้า: Deployment และ Service"
t("preview-deployment-service", S19,
  "Pod เดี่ยวหายแล้วไม่มีใครสร้างใหม่ บทหน้าจะใช้ Deployment ดูแลจำนวน Pod และ Service เป็นที่อยู่คงที่ของทุกสาขา",
  "Split board. Left 'today': a ship in fog with a branch Pod box gone (dotted outline) and a sad question mark. "
  "Right 'next chapter' sketch: a crew captain icon with a counter keeps two branch Pod boxes on two ships, and a "
  "lighthouse with one address light beams to both. Nong Som draws an arrow from left to right.",
  ["วันนี้: Pod เดี่ยว", "บทหน้า", "Deployment", "Service"],
  "Deployment and Service appear only on the right-hand next-chapter sketch", allow=True)

S20 = "20. สรุปและคำถามทบทวน"
t("summary-fleet-master", S20,
  "สรุปบท: scheduler เลือกเรือด้วย filter/score, เราช่วยกำหนดด้วย label, affinity, spread, taint และดูแลเรือด้วย cordon/drain",
  "Sunset harbor panorama: the control tower with its no-boarding sign, two worker ships with flags; teal Pod boxes "
  "neatly placed on the two worker ships only; small icons float above as a recap ring (flag, magnet, scale, sign, "
  "rope). Nong Som salutes proudly at the dock edge.",
  ["สรุปบทที่ 3", "Node กับ Pod", "lab-worker", "lab-worker2"],
  "no Pod boxes on the control tower")

# ------------------------------------------------------------------ LAB
l("lab0-fleet-survey", "LAB0 สำรวจกองเรือ",
  "LAB0: สำรวจ Node ด้วย kubectl get nodes, --show-labels และ describe node ดู allocatable กับ taint ของ control-plane",
  "Nong Som on the dock with a laptop terminal; three node cards float above like a fleet roster: the control tower "
  "card with a red no-boarding sign and two ship cards with green Ready lamps and mast flags. A magnifier highlights "
  "the allocatable gauge on one ship card.",
  ["kubectl get nodes", "Ready", "control-plane:NoSchedule", "allocatable", "lab-worker", "lab-worker2"],
  "exactly three node cards")
l("lab0-inside-node-crictl", "LAB0 สำรวจกองเรือ",
  "LAB0: ใน k8s-lab node คือ container ใช้ docker exec lab-worker crictl ps ดู container ระบบที่รันในเรือ",
  "Nong Som opens a hatch in the side of the lab-worker ship (which sits inside a big container frame) and shines a "
  "flashlight; inside are small stacked containers with labels. A terminal bubble shows the command.",
  ["docker exec lab-worker crictl ps", "kube-proxy", "kindnet-cni"],
  "only these two system containers are labeled inside")
l("lab1-pending", "LAB1 เจ้าหน้าที่จัดตู้กับ Pending",
  "LAB1: Pod ที่ขอ memory เกิน allocatable ค้าง Pending อ่านเหตุผลจาก Events FailedScheduling แล้วลด requests ให้วางได้",
  "Two Pod boxes on the dock: a normal one already lifted aboard lab-worker with a green Running tag, and a huge "
  "one stuffed with giant kibble sacks stuck on the dock with a yellow Pending tag. Nong Som reads the event board "
  "and holds a smaller sack ready to swap.",
  ["fit-pod: Running", "huge-pod: Pending", "Insufficient memory", "requests: 4000Gi"],
  "the huge Pod never sits on a ship")
l("lab2-nodename-downward", "LAB2 nodeName และ Downward API",
  "LAB2: nodeName วาง Pod ตรงไปยัง node โดยไม่ผ่าน scheduler และ Downward API ให้ Pod บอกได้ว่าอยู่เรือลำไหน",
  "Two labeled halves. Left: Nong Som carries a Pod box past the loading officer straight to the control tower "
  "dock (the tower has a no-boarding sign, but the box goes in through the side door labeled nodeName). Right: a "
  "Pod box on lab-worker shows a glowing shop sign with its ship name taken from a name plate the first mate stamped.",
  ["nodeName: lab-control-plane", "ข้าม scheduler", "Downward API", "บนเรือ lab-worker"],
  "Nong Som appears only once, in the left half; the right half shows only the Pod box and the first mate")
l("lab3-flags-selector-affinity", "LAB3 ธงเรือ: nodeSelector + node affinity",
  "LAB3: ติด label ให้ node แล้วใช้ nodeSelector และ node affinity (required/preferred/Gt) เลือกเรือ",
  "Nong Som raises flags on the masts of two ships: lab-worker gets fleet=eco and deck=2, lab-worker2 gets fleet=fast "
  "and deck=5. A Pending Pod box waiting on the dock with a fast-flag ticket starts moving toward lab-worker2 as "
  "soon as the flag goes up.",
  ["kubectl label node", "fleet=eco", "fleet=fast", "nodeSelector", "lab-worker", "lab-worker2"],
  "flags: fleet=eco on lab-worker, fleet=fast on lab-worker2; no other flag text")
l("lab4-pod-magnets", "LAB4 แม่เหล็กระหว่างกล่อง",
  "LAB4: podAffinity ดึง web ไปอยู่เรือเดียวกับ cache ส่วน podAntiAffinity ผลัก crew 3 กล่องให้แยกเรือ กล่องที่ 3 ไม่มีที่จึง Pending",
  "Two ships. On lab-worker a cache Pod (fish-snack cooler) and a web Pod stuck together by a magnet; plus crew-1. "
  "On lab-worker2 crew-2. A third crew-3 Pod box stays on the dock with a yellow Pending tag, repelled by magnets "
  "from both ships; the control tower with its sign is also unavailable. Nong Som holds two magnets.",
  ["podAffinity", "podAntiAffinity", "crew-1", "crew-2", "crew-3: Pending"],
  "crew-1 and crew-2 on different ships; crew-3 on no ship")
l("lab5-spread-scale", "LAB5 ตาชั่งกองเรือ",
  "LAB5: topologySpreadConstraints กระจาย Pod ให้สมดุล และเห็นกับดัก nodeTaintsPolicy: Ignore ที่นับ control-plane จนเกิด Pending",
  "A long balance beam spanning three platforms: the control tower platform (red sign, 0 boxes), lab-worker (1 box), "
  "lab-worker2 (1 box); two more Pod boxes wait with Pending tags. Nong Som flips a lever switch from Ignore to "
  "Honor, and a small inset shows the result 2 and 2 on the ships with the tower excluded.",
  ["Ignore", "Honor", "Pending", "2 : 2", "maxSkew: 1"],
  "no Pod on the control tower")
l("lab6-taint-pass", "LAB6 ป้ายห้ามขึ้นและบัตรผ่าน",
  "LAB6: ติด taint ให้ lab-worker2 แล้วให้เฉพาะ Pod ที่มี toleration ขึ้นได้ และทดลองวาง Pod บน control-plane ด้วย toleration",
  "Nong Som hangs a red no-boarding sign on lab-worker2's rail; a VIP Pod box with a matching pass boards; a plain "
  "Pod box goes to lab-worker instead. In the background a Pod box with a control-plane pass enters the tower.",
  ["kubectl taint node", "dedicated=vip:NoSchedule", "vip-pod", "plain-pod", "control-plane-pod"],
  "plain-pod ends on lab-worker, vip-pod on lab-worker2, control-plane-pod at the tower")
l("lab6-noexecute-timer", "LAB6 ป้ายห้ามขึ้นและบัตรผ่าน",
  "LAB6: taint แบบ NoExecute ไล่ no-pass ทันที, pass-30s ถูกไล่หลัง 30 วินาที, pass-forever อยู่ต่อ",
  "Ship lab-worker2 gets a red NoExecute sign. Three Pod boxes: no-pass walking down the gangway immediately, "
  "pass-30s holding an hourglass, pass-forever relaxing with an infinity card. Nong Som holds a large stopwatch "
  "showing 30.",
  ["maintenance=true:NoExecute", "no-pass", "pass-30s", "pass-forever"],
  "Pods leave the ship, they are not destroyed or burned")
l("lab7-cordon-drain", "LAB7 ซ่อมเรือ: cordon / drain / uncordon",
  "LAB7: cordon lab-worker แล้ว drain ด้วย --ignore-daemonsets --force Pod เดี่ยวบนเรือหายไปและไม่ถูกสร้างใหม่บน lab-worker2",
  "Ship lab-worker at a repair dock with a rope barrier across its gangway and a wrench sign; crew unloads Pod boxes "
  "that fade into dotted outlines on the dock. lab-worker2 alongside has its own Pod boxes unchanged and an empty "
  "dotted slot with a question mark. Nong Som holds a checklist.",
  ["kubectl cordon", "kubectl drain --force", "SchedulingDisabled", "ไม่มีการสร้างใหม่", "lab-worker2"],
  "do NOT draw a literal drain or plumbing; no new boxes appear on lab-worker2")
l("lab8-docker-stop-fog", "LAB8 เรือหายในหมอก",
  "LAB8: docker stop lab-worker2 จำลองเรือล่ม node เป็น NotReady และถูกใส่ taint unreachable อัตโนมัติ",
  "Nong Som presses a red stop button on a terminal; ship lab-worker2 drifts into thick fog, radio silent. The tower "
  "status board shows lab-worker green and lab-worker2 red. Two red signs appear on the fogged ship.",
  ["docker stop lab-worker2", "NotReady", "node.kubernetes.io/unreachable", "lab-worker"],
  "the fogged ship is intact, not sinking")
l("lab8-eviction-timeline", "LAB8 เรือหายในหมอก",
  "LAB8: ไทม์ไลน์หลังเรือหายในหมอก NotReady ประมาณ 40-50 วินาที, fog-fast ถูกไล่หลัง 30 วินาที, fog-default รอ 300 วินาที แล้ว docker start คืนเรือ",
  "A long horizontal timeline ribbon with four labeled markers. Above it small scenes: ship fades into fog; a "
  "status light turns red; the fog-fast Pod becomes semi-transparent with a Terminating tag; the fog-default Pod "
  "holds a 5-minute hourglass; at the end the ship sails out of the fog with a start button. Nong Som walks along "
  "the timeline with a stopwatch.",
  ["docker stop", "NotReady ~40-50s", "fog-fast: +30s", "fog-default: +300s", "docker start"],
  "exactly five marker labels in left-to-right order; exact seconds are approximate")
l("lab9-static-pod", "LAB9 ตู้ของต้นเรือ: static Pod",
  "LAB9: วางไฟล์ manifest ลง /etc/kubernetes/manifests ใน lab-worker ด้วย docker cp kubelet สร้าง static Pod และ mirror pod static-snack-lab-worker",
  "Nong Som passes a binder page through a porthole of ship lab-worker; the first mate inside files it into a "
  "binder and builds a small cat-snack stall Pod box. On the tower board a translucent ghost copy "
  "appears with its name.",
  ["docker cp", "/etc/kubernetes/manifests", "static-snack-lab-worker", "mirror pod"],
  "the mirror pod is a ghost copy on the board, not a second real Pod")

SF = "LAB10 LAB สุดท้าย: ร้านน้องส้มหลายสาขาบนกองเรือ"
l("lab10-opening-branches", SF,
  "LAB สุดท้าย: เปิดร้านอาหารแมวน้องส้ม 2 สาขา som-shop-a และ som-shop-b บนเรือคนละลำ",
  "Grand opening at the harbor: ship lab-worker and ship lab-worker2 each carry one teal Pod box that is a cozy "
  "cat-food shop (awning, kibble bags, cat food cans, cat customers lining up). Both ships fly a shop flag. The "
  "control tower with its no-boarding sign has no shop. Nong Som cuts a ribbon on the dock.",
  ["som-shop-a", "som-shop-b", "shop=open", "lab-worker", "lab-worker2"],
  "exactly one shop Pod per worker ship; no shop on the control tower; all items are cat-food-shop items")
l("lab10-manifest-anatomy", SF,
  "โครง Pod สาขา: nodeAffinity เลือกเรือที่มีธง shop=open, podAntiAffinity ห้ามสาขาอยู่เรือเดียวกัน และ Downward API ใส่ NODE_NAME ในชื่อร้าน",
  "An exploded diagram of one branch Pod box with four callouts: a magnet pointing to a shop flag (node affinity), a "
  "pair of repelling magnets (anti-affinity), an hourglass boarding pass (toleration 60s), and a shop sign showing "
  "the branch ship name from a name plate (Downward API). Inside the box: a web container and a db container with an "
  "emptyDir shelf. Nong Som points at the shop sign.",
  ["nodeAffinity: shop=open", "podAntiAffinity", "tolerationSeconds: 60", "สาขา $(NODE_NAME)", "web + db"],
  "one Pod box only, sitting on a single ship")
l("lab10-images-ready", SF,
  "เตรียม image: build som-shop-web:1.0 จากบทที่ 2 แล้ว kind load ไปทุก node ส่วน postgres ใช้ docker save --platform แล้ว kind load image-archive",
  "A warehouse of container blueprints on the dock; Nong Som pushes a cart with two crates (web and postgres) "
  "toward a conveyor that splits into three lanes, one into each node (tower, lab-worker, lab-worker2). A small "
  "side note shows the postgres crate being repacked into an archive box first.",
  ["som-shop-web:1.0", "postgres:17.11-alpine", "kind load", "image-archive"],
  "three lanes, one per node; the archive box is a cardboard box, not a cat food item")
l("lab10-anti-affinity-pending", SF,
  "ทดลองสาขาที่ 3 som-shop-c: มีเรือติดธง shop=open แค่ 2 ลำและทั้งสองลำมีสาขาแล้ว จึง Pending",
  "Two ships each with one shop Pod and a shop flag; a third shop Pod box som-shop-c on the dock is pushed back by "
  "repelling magnets from both ships and cannot enter the tower (red sign, no shop flag). Yellow Pending tag. Nong "
  "Som shrugs with a small smile.",
  ["som-shop-c: Pending", "podAntiAffinity", "shop=open", "lab-control-plane"],
  "som-shop-c is on no ship")
l("lab10-two-tunnels", SF,
  "เปิดหน้าร้าน 2 สาขาด้วย kubectl port-forward คนละ port (3001, 3002) และ ssh -L สองชั้นจากเครื่องนักศึกษา",
  "Left: a student laptop with two browser tabs. A single tunnel tube labeled ssh -L runs into a box labeled "
  "k8s-lab, then splits into two port-forward pipes, one to the shop Pod on lab-worker and one to the shop Pod on "
  "lab-worker2. Nong Som stands at the tunnel entrance with a lantern.",
  ["localhost:3001", "localhost:3002", "ssh -L", "k8s-lab", "port-forward"],
  "no lighthouse and no load balancer; exactly two port-forward pipes, one per branch Pod")
l("lab10-browser-branch-names", SF,
  "หน้าเว็บสองสาขาแสดงชื่อร้านพร้อมชื่อเรือจาก Downward API และออเดอร์ของแต่ละสาขาแยกกันเพราะฐานข้อมูลอยู่ใน Pod ของตัวเอง",
  "Two browser windows side by side, each a cat-food shop page with product cards (kibble bag, wet food can, "
  "fish treat) and a big shop title. The left window's order counter shows 2, the right shows 0. Nong Som sits "
  "between them holding an order receipt.",
  ["ร้านอาหารแมวน้องส้ม สาขา lab-worker", "ร้านอาหารแมวน้องส้ม สาขา lab-worker2", "ออเดอร์: 2", "ออเดอร์: 0"],
  "Thai shop titles exactly as given; no other text on the pages")
l("lab10-drain-branch-closed", SF,
  "drain เรือของสาขา a: สาขา a ปิดและหายไป สาขา b ยังขายได้ เปิด a ใหม่ระหว่าง cordon จะ Pending จนกว่า uncordon",
  "Ship lab-worker at a repair dock with a rope barrier; its shop Pod faded to a dotted outline with a closed sign. "
  "Ship lab-worker2's shop is still open with cat customers. A new som-shop-a box waits on the dock with a yellow "
  "Pending tag until the rope is removed. Nong Som holds the rope end ready to untie it.",
  ["kubectl drain", "som-shop-a: ปิด", "som-shop-b: ยังขายได้", "Pending", "kubectl uncordon"],
  "do NOT draw a literal drain or plumbing; no automatic replacement shop appears")
l("lab10-fog-branch-lost", SF,
  "เรือ lab-worker2 หายในหมอก (docker stop): สาขา b ถูกไล่ออกหลัง 60 วินาที สาขา a ยังขายได้ แต่ไม่มีใครเปิดสาขาใหม่ให้",
  "Ship lab-worker2 in thick fog, its shop Pod semi-transparent with a Terminating tag and an empty hourglass. Ship "
  "lab-worker in sunshine with its shop still selling to cat customers. On the dock an empty spot with a big "
  "question mark where no new shop appears. Nong Som looks toward the fog worriedly.",
  ["docker stop lab-worker2", "NotReady", "som-shop-b: Terminating", "som-shop-a: ยังขายได้", "ไม่มีใครเปิดใหม่"],
  "the fogged ship is intact; no new Pod box anywhere")
l("lab10-next-deployment-service", SF,
  "ปิดท้าย: ถ้าอยากให้มีคนเปิดสาขาใหม่อัตโนมัติและมีที่อยู่เดียวสำหรับลูกค้า ต้องใช้ Deployment และ Service ในบทหน้า",
  "Planning board: left side 'today' shows two branch Pods each with its own port number sign and one branch "
  "crossed out; right side 'next chapter' sketch shows a crew captain with a counter keeping two shops alive and a "
  "lighthouse with one address light pointing customers to both shops. Nong Som draws on the board with a marker.",
  ["วันนี้: 2 Pod เดี่ยว", "บทหน้า", "Deployment", "Service"],
  "Deployment and Service appear only on the right-hand next-chapter sketch", allow=True)


def build(items, kind):
    out = []
    for i, (slug, sec, cap, scene, labels, extra, allow) in enumerate(items, 1):
        assert len(labels) <= 6, slug
        sub = "01_Theory" if kind == "T" else "02_LAB"
        out.append({
            "id": f"{kind}{i:02d}",
            "path": f"{ROOT}/{sub}/images/{i:02d}-{slug}.png",
            "section": sec,
            "caption_th": cap,
            "prompt": prompt(scene, labels, extra, allow),
        })
    return out


def write_md(items, title, path):
    lines = ["Generated with built-in image_gen via cyolo1 using 00-character-som.png as character reference", "",
             f"# Final image prompts — 003 Kubernetes Node กับ Pod ({title})", "",
             "ทุกภาพแนบ `01_Theory/images/00-character-som.png` เป็นภาพอ้างอิงตัวละครน้องส้ม", ""]
    for it in items:
        lines += [f"## {os.path.basename(it['path'])}", "",
                  f"> {it['id']} · {it['section']} — {it['caption_th']}", "",
                  "```text", it["prompt"], "```", ""]
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
