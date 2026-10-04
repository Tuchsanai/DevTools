#!/usr/bin/env python3
"""สร้าง images.json + imagegen-prompts.md (Theory/LAB) ของบท 002 Pod จาก storyboard ด้านล่าง"""
import json
from pathlib import Path

ROOT = Path("/root/workspace/DevTools/k")
CH = ROOT / "002_kubernetes_pod"
OUT_JSON = ROOT / "logs/002_pod/images.json"

USE_CASE = "Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance."
ASSET = "Asset type: landscape 3:2 educational story illustration for Thai Kubernetes Pod lesson (README figure, about 1536x1024)."
CHARACTER = (
    "Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat "
    "with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, "
    "short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. "
    "Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly."
)
STYLE = (
    "Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, white background, palette navy / blue / teal with orange accents, "
    "rounded cards, crisp large legible labels, generous whitespace; matches the chapter 001 classroom illustration set. "
    "Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps "
    "one or more shipping containers and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); "
    "Control Plane = harbor control tower on the dock (lab-control-plane); image registry = warehouse of container blueprints."
)
BASE_CONSTRAINTS = (
    "only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, "
    "no extra speech bubbles with text, no watermark, no signature, no real company logos"
)
NO_ADV = "do not show Service, NodePort, Deployment, ReplicaSet or Ingress objects or words"


def prompt(e):
    texts = "; ".join(f'"{t}"' for t in e["text"])
    cons = [BASE_CONSTRAINTS]
    if not e.get("preview"):
        cons.append(NO_ADV)
    cons += e.get("constraints", [])
    return "\n".join([
        USE_CASE,
        ASSET,
        "Scene: " + e["scene"],
        CHARACTER,
        STYLE,
        f"Text (verbatim, at most {len(e['text'])} short labels): {texts}.",
        "Constraints: " + "; ".join(cons) + ".",
    ])


THEORY = [
    dict(slug="opening-som-dream-shop", section="1. บทนำ: น้องส้มอยากเปิดร้าน",
         caption="น้องส้ม ผู้ช่วยกัปตันท่าเรือ Kubernetes ฝันอยากเปิดร้านอาหารแมวบนเรือ จึงต้องเรียนรู้การจัดกล่อง Pod",
         scene="Morning at the Kubernetes harbor. Nong Som stands on the dock holding a rolled-up shop sign and a small bag of cat kibble, dreaming: a thought cloud above shows a cozy cat-food shop stall sitting inside a teal Pod cabin box on a cargo ship. In the background a harbor control tower and two cargo ships float calmly. Mood: hopeful start of a journey.",
         text=["ร้านอาหารแมวน้องส้ม", "Kubernetes Pod", "บทที่ 2"]),
    dict(slug="harbor-metaphor-map", section="1. บทนำ: น้องส้มอยากเปิดร้าน",
         caption="ทบทวนอุปมาท่าเรือจากบทที่ 1: ตู้สินค้า = container, กล่อง Pod ห่อตู้, เรือ = Node, หอบังคับการ = Control Plane",
         scene="A friendly legend poster on the dock. Nong Som points with a pointer stick at four rounded cards arranged left to right: an orange shipping container; a teal translucent Pod cabin box wrapping that container with a small IP tag; a blue cargo ship carrying the Pod box; a navy harbor control tower. Thin arrows show nesting: container inside Pod, Pod on ship, tower directing ships.",
         text=["container = ตู้สินค้า", "Pod = กล่องห่อตู้", "Node = เรือ", "Control Plane = หอบังคับการ"]),
    dict(slug="what-is-a-pod", section="2. Pod คืออะไร",
         caption="Pod คือหน่วยเล็กที่สุดที่ Kubernetes deploy ได้ ห่อ container ตั้งแต่ 1 ตัวขึ้นไป มี IP เดียวและใช้ volume ร่วมกันได้",
         scene="Close-up cutaway of one big teal Pod cabin box. Inside sit two shipping containers (one orange labeled app, one blue labeled helper) side by side, both plugged into one shared network plug with a single IP tag on the box roof, and a shared shelf (volume) at the bottom that both can reach. Nong Som holds a magnifying glass, looking inside with curiosity.",
         text=["Pod", "IP: 10.244.1.5", "container", "volume ร่วม", "หน่วยเล็กที่สุด"],
         constraints=["exactly one IP tag on the Pod box, containers have no IP tags of their own"]),
    dict(slug="why-pod-not-container", section="3. ทำไมต้องมี Pod",
         caption="container ที่ต้องทำงานใกล้ชิดกันถูกห่อไว้ใน Pod เดียว จึงถูกสร้าง ย้าย และลบไปพร้อมกัน",
         scene="Two-panel comparison. Left panel: two loose shipping containers (app and log helper) drifting apart on separate small rafts, connected by a stretched, fraying rope, Nong Som looks worried. Right panel: the same two containers safely packed together in one teal Pod cabin box being lifted by a crane as one unit, Nong Som gives a thumbs-up. A big arrow from left to right.",
         text=["แยกกัน = วุ่นวาย", "อยู่ด้วยกัน ไปด้วยกัน", "Pod"]),
    dict(slug="pod-lives-on-one-node", section="4. Pod กับ Node",
         caption="kube-scheduler เลือกเรือให้ Pod ครั้งเดียว ทุก container ใน Pod อยู่บน Node เดียวกันเสมอ ไม่มีการแยกครึ่ง Pod ข้ามเรือ",
         scene="Harbor view: control tower labeled lab-control-plane on the dock, two cargo ships named lab-worker and lab-worker2. A planner figure with a clipboard on the tower balcony (kube-scheduler, faceless sailor silhouette) assigns one whole Pod box with two containers onto lab-worker. Inset at bottom right: a crossed-out illustration of a Pod split in half with one container on each ship, red X. Nong Som waves a signal flag toward lab-worker.",
         text=["lab-control-plane", "lab-worker", "lab-worker2", "Pod อยู่บน Node เดียว"],
         constraints=["no Pod boxes on the control tower", "the valid Pod is entirely on one ship"]),
    dict(slug="pod-shared-network-localhost", section="5.1 หนึ่ง Pod หนึ่ง IP",
         caption="container ใน Pod เดียวกันใช้ network namespace ร่วมกัน มี IP เดียว และคุยกันผ่าน localhost ได้ แต่ห้ามใช้ port ซ้ำกัน",
         scene="Cutaway of a Pod box with one IP tag 10.244.1.7 on its roof. Inside, an orange container web listening on port 3000 and a blue container db listening on port 5432, connected by a short internal speaking tube labeled localhost:5432. Nong Som stands inside the cabin holding a tin-can phone between them. A small warning card in the corner shows two containers both wanting port 80 with a red X.",
         text=["IP: 10.244.1.7", "web :3000", "db :5432", "localhost:5432", "port ห้ามชนกัน"],
         constraints=["only one IP for the whole Pod"]),
    dict(slug="pod-to-pod-ip", section="5.2 Pod คุยกับ Pod",
         caption="แต่ละ Pod มี IP ของตัวเองบนเครือข่ายคลัสเตอร์ (CNI) Pod ต่างเรือคุยกันด้วย Pod IP ได้ แต่ IP จะเปลี่ยนเมื่อ Pod ถูกสร้างใหม่",
         scene="Two cargo ships lab-worker and lab-worker2, each carrying one Pod box with its own IP tag (10.244.1.7 and 10.244.2.4). A dotted underwater cable (cluster pod network) connects the two Pods with a message envelope travelling along it. Nong Som on a small boat between the ships holds a note card showing an old IP crossed out and a new IP written below, looking surprised.",
         text=["10.244.1.7", "10.244.2.4", "Pod network (CNI)", "IP เปลี่ยนได้!"]),
    dict(slug="pod-creation-journey", section="6. เส้นทางการเกิดของ Pod",
         caption="ลำดับเมื่อสั่ง kubectl apply: kube-apiserver บันทึกลง etcd, kube-scheduler เลือก Node, kubelet สั่ง container runtime ดึง image และเริ่ม container",
         scene="Left-to-right numbered journey path across the harbor. 1 Nong Som hands a YAML work order into the control tower window (kube-apiserver); 2 the order is filed in a vault drawer (etcd); 3 a planner pins the Pod onto a ship chart (kube-scheduler); 4 the ship's first mate (kubelet) on lab-worker receives the order; 5 a crane (container runtime) pulls a container from the warehouse registry and places it into the Pod box; 6 the Pod box glows with a green Running badge.",
         text=["kubectl apply", "kube-apiserver", "etcd", "kube-scheduler", "kubelet", "Running"],
         constraints=["numbers 1-6 as small circles only, no other text"]),
    dict(slug="yaml-syntax-basics", section="7.1 พื้นฐาน YAML",
         caption="YAML ใช้ key: value, การเยื้องด้วยช่องว่างบอกลำดับชั้น และขีด - บอกรายการ (list)",
         scene="Nong Som stands next to a large clipboard showing a short colorful YAML snippet with indentation guides drawn as faint vertical dotted lines: shop: then indented name and port, then a list of two items with dashes. Three callout tags point to the parts: key: value, indentation with 2 spaces, and list items. Nong Som measures the indent with a tiny ruler.",
         text=["key: value", "เยื้อง 2 ช่องว่าง", "- รายการ (list)", "YAML"],
         constraints=["the clipboard snippet may show only these exact lines in monospace: 'shop:', '  name: som', '  port: 3000', '  items:', '    - kibble', '    - treat' (these code lines are allowed in addition to the labels)"]),
    dict(slug="yaml-common-mistakes", section="7.2 ข้อผิดพลาดยอดฮิตของ YAML",
         caption="ข้อผิดพลาดที่พบบ่อย: ใช้ Tab แทนช่องว่าง, ลืมเว้นวรรคหลังเครื่องหมาย :, และเยื้องผิดระดับ",
         scene="Three small rounded cards in a row, each showing a broken YAML line with a red X on the left and the fixed line with a green check on the right: a tab arrow symbol versus spaces dots; a missing space after the colon; a wrongly indented line. Nong Som holds a big eraser and a pencil, fixing the cards with a determined look.",
         text=["ห้ามใช้ Tab", "ต้องเว้นวรรคหลัง :", "เยื้องให้ตรงระดับ"],
         constraints=["code on cards limited to 'name:som' (wrong) and 'name: som' (right), otherwise use symbols"]),
    dict(slug="manifest-four-parts", section="8.1 โครงสร้าง manifest",
         caption="Pod manifest มี 4 ส่วนหลัก: apiVersion, kind, metadata และ spec",
         scene="A big work-order document pinned on a board, split into four colored horizontal bands, each with a matching icon: apiVersion v1 (version stamp), kind Pod (Pod box icon), metadata (name tag and label tags), spec (blueprint of containers). Nong Som points at the spec band, looking proud.",
         text=["apiVersion: v1", "kind: Pod", "metadata", "spec"]),
    dict(slug="spec-vs-status", section="8.2 spec กับ status",
         caption="spec คือสิ่งที่เราต้องการ (desired state) ส่วน status คือสภาพจริงที่ระบบเขียนรายงานกลับมา",
         scene="Split view. Left: Nong Som writes on an order form labeled spec with a pencil (what we want: one nginx container). Right: the ship's first mate (kubelet, a friendly sailor silhouette without text) fills in a report card labeled status with phase Running and a podIP field. A two-way arrow between them showing comparison.",
         text=["spec = ที่ต้องการ", "status = ที่เป็นจริง", "phase: Running", "podIP"],
         constraints=["the kubelet helper is a simple faceless sailor silhouette, not a second cat"]),
    dict(slug="container-image-ports", section="9.1 image และ ports",
         caption="ระบุ image พร้อม tag เสมอ และ containerPort เป็นเพียงข้อมูลบอกว่า container ฟังพอร์ตใด ไม่ได้เปิดพอร์ตออกนอกคลัสเตอร์",
         scene="Nong Som at the warehouse registry counter picking a container blueprint box labeled nginx:1.27-alpine, while a box labeled latest sits behind with a small caution sign. On the right a shipping container has a door with a small port plate 80 and a dotted info tag (documentation note), with no path leading outside the harbor.",
         text=["nginx:1.27-alpine", "ระบุ tag เสมอ", "containerPort: 80", "imagePullPolicy"]),
    dict(slug="env-variables", section="9.2 env",
         caption="env ส่งค่าตั้งค่าเข้า container เป็นคู่ name/value โดย value ต้องเป็นข้อความ (string)",
         scene="Nong Som attaches small labeled envelopes onto the side of an orange shipping container through a mail slot. The envelopes show env pairs. One envelope with a number has quotes highlighted to show it must be a string.",
         text=["env", "SHOP_NAME", "DB_PORT: \"5432\"", "ค่าเป็น string"]),
    dict(slug="command-args-override", section="9.3 command และ args",
         caption="command ใน Pod ทับ ENTRYPOINT และ args ทับ CMD ของ image",
         scene="Two-row comparison table drawn as cards. Top row: Dockerfile card with ENTRYPOINT and CMD. Bottom row: Pod YAML card with command and args. Curved arrows show command replaces ENTRYPOINT and args replaces CMD. Nong Som swaps a sticker on the container door with a new instruction sticker.",
         text=["ENTRYPOINT", "CMD", "command", "args", "ทับค่าใน image"]),
    dict(slug="resources-requests-limits", section="9.4 resources",
         caption="requests ใช้ตอนเลือก Node (จองที่) ส่วน limits คือเพดานจริง ใช้ memory เกิน limit จะถูก OOMKilled ส่วน CPU จะถูกชะลอ",
         scene="On the dock, a ship cargo-capacity gauge. Nong Som books space for a Pod box using a reservation ticket (requests: cpu 100m, memory 128Mi). Next to it the Pod box has a ceiling bar (limits). Small inset: a container overflowing past the memory ceiling with a burst icon (OOMKilled); another inset: a CPU turtle slowing down (throttled).",
         text=["requests = จองที่", "limits = เพดาน", "OOMKilled", "CPU ถูกชะลอ"]),
    dict(slug="labels-selectors", section="10. Labels และ Selectors",
         caption="labels คือป้ายแท็กคู่ key=value ที่ติดกับ Pod และใช้ selector -l ค้นหากลุ่ม Pod ได้",
         scene="A row of four Pod boxes on a ship, each with hanging colored tags (app=som-shop, tier=web / tier=db, app=toy-shop). Nong Som holds a magnet-like selector wand labeled with a filter; the two Pods with app=som-shop tags light up and lift slightly, others stay dim.",
         text=["app=som-shop", "tier=web", "tier=db", "app=toy-shop", "-l app=som-shop"]),
    dict(slug="kubectl-explain-dry-run", section="11. เครื่องมือช่วยเขียน YAML",
         caption="kubectl explain เป็นคู่มือ field ของ YAML และ --dry-run=client -o yaml ช่วยร่างไฟล์ Pod โดยยังไม่สร้างจริง",
         scene="Nong Som at a desk. Left: an open thick manual book with a magnifier on the page labeled kubectl explain. Right: a small printer printing a draft YAML sheet stamped with a dashed outline DRAFT shape (no extra text), labeled with the dry-run command. A pencil and a clean pod.yaml file card wait on the desk.",
         text=["kubectl explain", "--dry-run=client -o yaml", "ร่าง ยังไม่สร้างจริง", "pod.yaml"]),
    dict(slug="pod-phases", section="12.1 Pod phase",
         caption="Pod phase มี 5 ค่า: Pending, Running, Succeeded, Failed และ Unknown",
         scene="A timeline path along the dock with five stations as rounded signposts: Pending (Pod box waiting on the dock with an hourglass), Running (box on ship with green light), then a fork to Succeeded (green check, finished cargo) and Failed (red X). A separate foggy side station Unknown (ship lost in fog, cannot contact node). Nong Som walks along the path with a lantern.",
         text=["Pending", "Running", "Succeeded", "Failed", "Unknown"]),
    dict(slug="container-states-restartpolicy", section="12.2 สถานะ container และ restartPolicy",
         caption="container มีสถานะ Waiting, Running, Terminated และ restartPolicy (Always, OnFailure, Never) กำหนดว่า kubelet จะ restart container ใน Pod เดิมหรือไม่",
         scene="Top row: three container state icons: Waiting (hourglass), Running (play), Terminated (stop square). Bottom: three switch dials on a ship control panel labeled with the three restartPolicy values; Nong Som turns the Always dial (default). A small circular arrow shows the same container restarting inside the same Pod box, not a new Pod.",
         text=["Waiting", "Running", "Terminated", "Always", "OnFailure", "Never"]),
    dict(slug="crashloopbackoff", section="12.3 CrashLoopBackOff",
         caption="container ล้มซ้ำ ๆ kubelet จะ restart โดยรอนานขึ้นเรื่อย ๆ 10 วินาที, 20, 40 ... สูงสุด 5 นาที เรียกว่า CrashLoopBackOff",
         scene="A container inside a Pod box repeatedly toppling over and being stood up again by the ship's first mate (kubelet, a faceless sailor silhouette). Above it, a spiral of growing clock icons showing increasing wait times. Nong Som reads a log scroll beside it with a thinking expression (curious face from the reference sheet).",
         text=["CrashLoopBackOff", "10s → 20s → 40s", "สูงสุด 5 นาที", "logs --previous"]),
    dict(slug="imagepullbackoff", section="12.4 ImagePullBackOff",
         caption="ถ้าชื่อหรือ tag ของ image ผิด หรือ image อยู่แค่ในเครื่องแต่ไม่ได้ kind load node จะดึง image ไม่ได้และขึ้น ErrImagePull / ImagePullBackOff",
         scene="At the warehouse registry, a crane on the ship tries to grab a container blueprint box labeled nginx:9.99 from an empty shelf; a 'not found' style empty slot. The empty Pod box waits on the ship. Nong Som checks a delivery slip with a surprised face (surprised expression from the reference).",
         text=["ErrImagePull", "ImagePullBackOff", "nginx:9.99", "tag ผิด?"]),
    dict(slug="probes-three-inspectors", section="13.1 Probes",
         caption="kubelet ใช้ probe ตรวจสุขภาพ container: startupProbe รอให้เริ่มเสร็จ, livenessProbe ตรวจว่ายังมีชีวิต, readinessProbe ตรวจว่าพร้อมรับงาน",
         scene="Three inspector stations next to one Pod box, each shown as a small stethoscope icon card: startup (alarm clock, waits for slow start), liveness (heartbeat line; failure arrow leads to a restart circular arrow), readiness (open/closed shop sign; failure shows READY 0/1 but no restart). Nong Som wears a stethoscope and listens to the container.",
         text=["startupProbe", "livenessProbe → restart", "readinessProbe → READY 0/1", "kubelet ตรวจ"]),
    dict(slug="probe-mechanisms", section="13.2 กลไกของ probe",
         caption="probe ตรวจได้ 3 แบบหลัก: httpGet, tcpSocket และ exec พร้อมพารามิเตอร์ periodSeconds และ failureThreshold",
         scene="Three tool cards: httpGet (a small HTTP request arrow to /api/health returning 200 green), tcpSocket (a plug knocking on port 5432), exec (a terminal icon running a command and returning exit code 0). Below, a slider panel shows timing knobs. Nong Som holds a clipboard checklist.",
         text=["httpGet /api/health", "tcpSocket :5432", "exec", "periodSeconds", "failureThreshold"]),
    dict(slug="emptydir-shared-shelf", section="14. Volume: emptyDir",
         caption="emptyDir เป็นพื้นที่เก็บไฟล์ร่วมของ Pod ข้อมูลรอดเมื่อ container restart แต่หายไปเมื่อ Pod ถูกลบ",
         scene="Three-step story strip. Step 1: inside a Pod box, two containers put files on a shared shelf labeled emptyDir. Step 2: one container falls over and stands up again (restart) while the shelf files are still there, green check. Step 3: the whole Pod box is removed by a crane and the shelf vanishes with it, files gone, red X. Nong Som reacts in each step (happy, relieved, surprised).",
         text=["emptyDir", "container restart: ข้อมูลอยู่", "ลบ Pod: ข้อมูลหาย"]),
    dict(slug="init-containers", section="15.1 Init container",
         caption="init container รันทีละตัวตามลำดับและต้องจบสำเร็จก่อน app container จึงจะเริ่มทำงาน",
         scene="A Pod box on a ship with a small prep stage in front. Two init containers line up and finish one after another (step 1 then step 2, each turning a green check), then the main app container starts with a green play icon. Nong Som as a stage manager holds a stopwatch. Status pill shows Init:1/2 progressing.",
         text=["init 1 ✓", "init 2 ✓", "app เริ่มทำงาน", "Init:1/2"]),
    dict(slug="sidecar-pattern", section="15.2 Sidecar container",
         caption="sidecar ทำงานคู่กับ container หลักตลอดอายุ Pod เช่น เก็บ log หรือเตรียมไฟล์ผ่าน volume ร่วม; native sidecar คือ initContainers ที่ตั้ง restartPolicy: Always",
         scene="Inside a Pod box: a main orange container app writes log pages onto a shared emptyDir shelf, and a smaller teal sidecar container (like a sidecar attached to a motorcycle) reads them and ships them out. A small YAML card below shows the native sidecar idea. Nong Som rides happily in the sidecar seat.",
         text=["app", "sidecar", "emptyDir", "initContainers + restartPolicy: Always"]),
    dict(slug="debug-toolkit", section="16. เข้าถึงและดีบัก Pod",
         caption="ชุดเครื่องมือดีบัก Pod: get -o wide, describe (Events), logs, exec และ port-forward",
         scene="Nong Som opens a captain's toolbox on the dock. Five tools pop out, each tied to a Pod box on a ship: binoculars (get -o wide), detective notebook (describe events), log scroll (logs), a door key into the container (exec -it), and a tunnel pipe (port-forward).",
         text=["get -o wide", "describe", "logs", "exec -it", "port-forward"]),
    dict(slug="port-forward-ssh-tunnel", section="16.1 เปิดเว็บจากเครื่องนักศึกษา",
         caption="เปิดเว็บใน Pod จาก browser: เครื่องนักศึกษา → ssh -L → container k8s-lab → kubectl port-forward → Pod",
         scene="Left-to-right chain of rounded cards connected by two tunnel pipes. Card 1: student laptop with a browser showing localhost:3000. Tunnel 1 labeled ssh -L (to port 2223). Card 2: k8s-lab container box holding a terminal. Tunnel 2 labeled kubectl port-forward. Card 3: a ship with a Pod box listening on port 3000. Nong Som crawls happily through the tunnel carrying a web page.",
         text=["localhost:3000", "ssh -L 3000", "k8s-lab", "kubectl port-forward", "Pod :3000"],
         constraints=["no NodePort 30080-30082 shown, no direct arrow from laptop to Pod"]),
    dict(slug="pod-is-ephemeral", section="17. Pod เป็นของชั่วคราว",
         caption="Pod เดี่ยวที่ถูกลบจะไม่มีใครสร้างคืนให้ และ Pod ใหม่จะได้ IP ใหม่กับ emptyDir ว่างเปล่า",
         scene="A crane removes a Pod box from the ship; the spot is empty with a dashed outline and a small sad paw print. Nong Som stands on the dock looking at an empty spot with a surprised expression. A thought cloud shows a new Pod box with a different IP tag. No other worker appears to rebuild it.",
         text=["kubectl delete pod", "ไม่มีใครสร้างคืน", "IP ใหม่", "ข้อมูลหาย"]),
    dict(slug="next-chapter-preview", section="18. ปูทางบทหน้า",
         caption="บทหน้า: Deployment ช่วยดูแลและสร้าง Pod ใหม่ให้อัตโนมัติ และ Service ให้ที่อยู่คงที่แม้ IP ของ Pod เปลี่ยน",
         scene="Preview panel. Nong Som looks through a telescope toward the next harbor. Through the lens: a fleet manager crew (Deployment) automatically placing replacement Pod boxes onto ships, and a lighthouse with a fixed address (Service) beaming to several Pods behind it. A banner flag at the horizon says next chapter.",
         text=["บทถัดไป", "Deployment", "Service", "สร้าง Pod ใหม่อัตโนมัติ", "ที่อยู่คงที่"],
         preview=True,
         constraints=["show Deployment and Service only as a distant preview seen through the telescope"]),
    dict(slug="chapter-summary", section="19. สรุป",
         caption="สรุปบทที่ 2: Pod, YAML, lifecycle, probes, emptyDir และ multi-container พร้อมสำหรับ LAB",
         scene="Nong Som stands proudly holding a completed checklist board with six check-marked icon rows: Pod box, YAML document, lifecycle timeline, stethoscope probe, emptyDir shelf, multi-container Pod. Behind Nong Som a cargo ship with a neat Pod box sails into sunset-colored teal waves (keep white background, waves as small flat shapes).",
         text=["สรุปบทที่ 2", "Pod", "YAML", "Lifecycle", "Probes", "Multi-container"]),
]

LAB = [
    dict(slug="lab0-cluster-up", section="LAB0 สร้างคลัสเตอร์ท่าเรือ",
         caption="LAB0: รัน k8s-up ใน k8s-lab เพื่อสร้าง kind cluster ชื่อ lab มี control-plane 1 ตัวและ worker 2 ตัว",
         scene="Inside a big container card labeled k8s-lab, Nong Som presses a large button on a terminal. The harbor appears inside the card: one control tower lab-control-plane and two ships lab-worker and lab-worker2, each with a green Ready badge. No Pods yet.",
         text=["k8s-up", "lab-control-plane", "lab-worker", "lab-worker2", "Ready"],
         constraints=["exactly 1 control tower and 2 ships, no Pod boxes"]),
    dict(slug="lab1-kubectl-run", section="LAB1 Pod แรกด้วย kubectl run",
         caption="LAB1: สร้าง Pod แรกด้วย kubectl run แล้วดูสถานะด้วย kubectl get pods -o wide",
         scene="Nong Som speaks a single command into a harbor radio; a crane drops one Pod box (with one orange nginx container) onto ship lab-worker. A status board on the dock shows the Pod row with READY 1/1 and STATUS Running and an IP tag 10.244.x.x.",
         text=["kubectl run hello", "nginx:1.27-alpine", "1/1 Running", "lab-worker"]),
    dict(slug="lab2-first-yaml", section="LAB2 Pod YAML แรก",
         caption="LAB2: ร่าง YAML ด้วย --dry-run=client -o yaml เขียน nginx-pod.yaml แล้ว kubectl apply -f",
         scene="Nong Som at a drafting desk writing a YAML blueprint sheet nginx-pod.yaml, then feeding it into a slot in the control tower. The resulting Pod box web appears on a ship. A small reply note shows pod/web created.",
         text=["nginx-pod.yaml", "kubectl apply -f", "pod/web created"]),
    dict(slug="lab3-exec-logs-portforward", section="LAB3 exec / logs / port-forward",
         caption="LAB3: เข้าไปใน Pod ด้วย exec แก้หน้าเว็บ ดู access log และเปิดเว็บผ่าน port-forward + ssh -L",
         scene="Three mini-scenes in one panel: (a) Nong Som opens the container door with a key (exec) and pins a new page 'สวัสดีจากน้องส้ม' inside; (b) a log scroll unrolls from the container showing GET / lines as simple bars; (c) a tunnel from a student laptop browser through k8s-lab to the Pod on port 80 via local port 8080.",
         text=["kubectl exec -it", "kubectl logs -f", "port-forward 8080:80", "ssh -L 8080", "สวัสดีจากน้องส้ม"]),
    dict(slug="lab4-labels", section="LAB4 Labels & Selectors",
         caption="LAB4: ติดป้าย label ให้ Pod 3 ตัวและใช้ -l เลือกเฉพาะกลุ่มที่ต้องการ",
         scene="Three Pod boxes on a ship: shop-web, shop-cache, toy-web, each with colored tags. Nong Som uses a label gun to stick a new tag env=dev on toy-web, while a selector beam highlights the two app=som-shop Pods.",
         text=["shop-web", "shop-cache", "toy-web", "-l app=som-shop", "env=dev"]),
    dict(slug="lab5-lifecycle-debug", section="LAB5 Lifecycle & Debug",
         caption="LAB5: สังเกต Completed, CrashLoopBackOff และ ImagePullBackOff แล้วใช้ describe กับ logs --previous หาสาเหตุ",
         scene="A status board on the dock lists three Pods with colored status pills: completed-pod Completed (green), crash-pod CrashLoopBackOff (orange) with a growing restart counter, bad-image-pod ImagePullBackOff (red). Nong Som as a detective with a magnifying glass and notebook investigates the red row.",
         text=["Completed", "CrashLoopBackOff", "ImagePullBackOff", "kubectl describe", "logs --previous"]),
    dict(slug="lab6-env-command-resources", section="LAB6 env / command / resources",
         caption="LAB6: ส่ง env และ command เข้า container ทดลอง memory limit จนเกิด OOMKilled และ request CPU เกินจน Pending",
         scene="Three cards: (1) a container receiving an env envelope SHOP_NAME and printing it; (2) a container overflowing a memory ceiling with a burst icon OOMKilled exit 137; (3) a huge Pod box that cannot fit on any ship, waiting on the dock with an hourglass, Pending Insufficient cpu. Nong Som holds a measuring tape.",
         text=["SHOP_NAME", "OOMKilled", "Pending", "Insufficient cpu"]),
    dict(slug="lab7-probes", section="LAB7 Probes",
         caption="LAB7: liveness ล้มแล้ว container ถูก restart ส่วน readiness ล้มแล้ว Pod เป็น READY 0/1 โดยไม่ถูก restart",
         scene="Two Pods side by side. Left: liveness-exec-pod with a broken heartbeat line and a circular restart arrow, RESTARTS counter going up. Right: readiness-http-pod with a shop sign flipping between closed (0/1) and open (1/1) as Nong Som creates the file ready.html inside with a paw. Nong Som wears a stethoscope.",
         text=["Liveness → restart", "Readiness → 0/1", "ready.html", "RESTARTS"]),
    dict(slug="lab8-multi-container", section="LAB8 Multi-container",
         caption="LAB8: Pod หลาย container คุยกันผ่าน localhost ใช้ emptyDir ร่วมกัน มี init container เตรียมไฟล์ และ sidecar เขียนข้อมูลต่อเนื่อง",
         scene="Cutaway of one Pod box with one IP tag. A small init container prepare finishes first (green check) after placing index.html on an emptyDir shelf; then web (nginx) serves the file and a sidecar menu-writer keeps appending time notes to the shelf. The sidecar reaches web via localhost:80 (same Pod IP). READY pill shows 2/2 (web + menu-writer). Nong Som watches with a clipboard.",
         text=["init: prepare ✓", "web", "menu-writer", "emptyDir", "localhost:80", "2/2"]),
    dict(slug="lab9-som-shop-storefront", section="LAB9 ร้านอาหารแมวน้องส้ม",
         caption="LAB สุดท้าย: เปิดร้านอาหารแมวน้องส้มด้วย Next.js + PostgreSQL ใน Pod เดียว",
         scene="Grand opening. Nong Som cuts a teal ribbon in front of a cute cat-food shop that sits inside a large teal Pod box on ship lab-worker. Shop shelves show kibble bags, wet food cans and lickable treats. A browser window card floats nearby showing product cards with prices in baht.",
         text=["ร้านอาหารแมวน้องส้ม", "Next.js", "PostgreSQL", "1 Pod"]),
    dict(slug="lab9-pod-architecture", section="LAB9 สถาปัตยกรรม Pod som-shop",
         caption="สถาปัตยกรรม Pod som-shop: web (Next.js :3000) คุยกับ db (PostgreSQL :5432) ผ่าน localhost ภายใน Pod เดียว และเก็บข้อมูล DB บน emptyDir",
         scene="Technical cutaway diagram of Pod som-shop with one IP tag on top. Inside: orange container web labeled som-shop-web:1.0 :3000; blue container db labeled postgres:17-alpine :5432 marked as sidecar; an arrow from web to db labeled localhost:5432; db mounts a shelf emptyDir db-data. Two small completed init container chips at the left edge (wait-for-db, db-seed) with check marks. Nong Som points at the localhost arrow.",
         text=["Pod: som-shop", "web :3000", "db :5432", "localhost:5432", "emptyDir db-data"],
         constraints=["one IP for the whole Pod", "web and db are inside the same single Pod box on one ship"]),
    dict(slug="lab9-startup-order", section="LAB9 ลำดับการเริ่มทำงาน",
         caption="ลำดับเริ่ม Pod: db (native sidecar) เริ่มก่อนและผ่าน startupProbe → wait-for-db รอ pg_isready → db-seed สร้างตารางและสินค้า → web เริ่มทำงาน",
         scene="Horizontal timeline with four numbered steps inside a Pod outline: 1 db starts and keeps running (a long bar continuing to the end of the timeline); 2 wait-for-db short bar ending with check; 3 db-seed short bar ending with check, small table icon with 6 products; 4 web starts and runs to the end. A single green status pill Running at the end of the timeline. Nong Som holds a stopwatch.",
         text=["1 db (sidecar)", "2 wait-for-db", "3 db-seed", "4 web", "Running"],
         constraints=["db bar continues alongside web until the end; init bars 2 and 3 end before web begins"]),
    dict(slug="lab9-build-kind-load", section="LAB9 Build image และ kind load",
         caption="build image som-shop-web:1.0 ใน k8s-lab แล้วใช้ kind load docker-image นำ image เข้าไปในทุก node ของคลัสเตอร์",
         scene="Inside the k8s-lab card: Nong Som operates a small factory machine turning a Dockerfile into a container box som-shop-web:1.0. A conveyor belt labeled kind load docker-image carries copies of the box onto all three nodes (control tower lab-control-plane and ships lab-worker, lab-worker2). Registry warehouse is not needed for this image.",
         text=["docker build", "som-shop-web:1.0", "kind load docker-image", "--name lab"]),
    dict(slug="lab9-open-in-browser", section="LAB9 เปิดร้านใน browser",
         caption="เปิดร้านจากเครื่องนักศึกษา: kubectl port-forward pod/som-shop 3000:3000 ใน k8s-lab และ ssh -L 3000:localhost:3000 จากเครื่องนักศึกษา",
         scene="A student laptop on the left shows the shop web page (product cards, an order button) at localhost:3000. A tunnel ssh -L leads into the k8s-lab card, where a second tunnel port-forward leads to the Pod som-shop on a ship, port 3000. Nong Som waves from inside the shop window in the Pod.",
         text=["localhost:3000", "ssh -L 3000:localhost:3000", "port-forward pod/som-shop", "สั่งซื้อ"],
         constraints=["no NodePort 30080-30082, no direct path from laptop to Pod"]),
    dict(slug="lab9-emptydir-survive-vs-lost", section="LAB9 ข้อมูลรอดหรือหาย",
         caption="ทดลองกับข้อมูลออเดอร์: restart container db แล้วข้อมูลยังอยู่บน emptyDir แต่ลบ Pod แล้วข้อมูลหายทั้งหมด",
         scene="Two-panel comparison. Left: inside Pod som-shop, the db container restarts (circular arrow, RESTARTS 1) while the emptyDir shelf still holds order receipts, green check, Nong Som relieved. Right: a crane removes the whole Pod som-shop; the shelf and receipts vanish; a new Pod box arrives with a different IP and an empty shelf with fresh stock, red X on orders, Nong Som surprised.",
         text=["restart db: ออเดอร์ยังอยู่", "ลบ Pod: ออเดอร์หาย", "emptyDir", "IP ใหม่"]),
    dict(slug="lab9-next-split", section="LAB9 ปูทางบทหน้า",
         caption="Pod เดียวรวมเว็บกับฐานข้อมูลเป็นการออกแบบเพื่อการเรียนรู้ บทหน้าจะแยก web เป็น Deployment, db ใช้ที่เก็บถาวร และเชื่อมกันด้วย Service",
         scene="Before/after planning board. Left: today's single Pod box containing web and db, marked with a graduation cap icon (learning design). Arrow to right: a preview plan sketch with web Pods managed by a Deployment crew on one side, a db with a durable storage barrel on the other side, and a Service lighthouse connecting them. Nong Som draws on the board with a marker.",
         text=["วันนี้: 1 Pod", "บทหน้า", "Deployment", "Service", "ที่เก็บถาวร"],
         preview=True,
         constraints=["Deployment and Service appear only on the right-hand 'next chapter' sketch"]),
]


def build():
    items = []
    for kind, lst, base in (("T", THEORY, CH / "01_Theory/images"), ("L", LAB, CH / "02_LAB/images")):
        for i, e in enumerate(lst, 1):
            items.append({
                "id": f"{kind}{i:02d}",
                "path": str(base / f"{i:02d}-{e['slug']}.png"),
                "section": e["section"],
                "caption_th": e["caption"],
                "prompt": prompt(e),
            })
    OUT_JSON.write_text(json.dumps(items, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    for kind, folder, title in (("T", "01_Theory", "Theory"), ("L", "02_LAB", "LAB")):
        lines = [
            "Generated with built-in image_gen via cyolo1 using 00-character-som.png as character reference",
            "",
            f"# Final image prompts — 002 Kubernetes Pod ({title})",
            "",
            "ทุกภาพแนบ `01_Theory/images/00-character-som.png` เป็นภาพอ้างอิงตัวละครน้องส้ม",
            "",
        ]
        for it in items:
            if it["id"][0] != kind:
                continue
            lines += [f"## {Path(it['path']).name}", "", f"> {it['id']} · {it['section']} — {it['caption_th']}", "",
                      "```text", it["prompt"], "```", ""]
        (CH / folder / "images/imagegen-prompts.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    build()
