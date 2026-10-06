Generated with built-in image_gen via cyolo1 using 00-character-som.png as character reference

# Final image prompts — 002 Kubernetes Pod (Theory)

ทุกภาพแนบ `01_Theory/images/00-character-som.png` เป็นภาพอ้างอิงตัวละครน้องส้ม

## 01-opening-som-dream-shop.png

> T01 · 1. บทนำ: น้องส้มอยากเปิดร้าน — น้องส้ม ผู้ช่วยกัปตันท่าเรือ Kubernetes ฝันอยากเปิดร้านอาหารแมวบนเรือ จึงต้องเรียนรู้การจัดกล่อง Pod

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes Pod lesson (README figure, about 1536x1024).
Scene: Morning at the Kubernetes harbor. Nong Som stands on the dock holding a rolled-up shop sign and a small bag of cat kibble, dreaming: a thought cloud above shows a cozy cat-food shop stall sitting inside a teal Pod cabin box on a cargo ship. In the background a harbor control tower and two cargo ships float calmly. Mood: hopeful start of a journey.
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 001 classroom illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps one or more shipping containers and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock (lab-control-plane); image registry = warehouse of container blueprints.
Text (verbatim, at most 3 short labels): "ร้านอาหารแมวน้องส้ม"; "Kubernetes Pod"; "บทที่ 2".
Constraints: only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; do not show Service, NodePort, Deployment, ReplicaSet or Ingress objects or words.
```

## 02-harbor-metaphor-map.png

> T02 · 1. บทนำ: น้องส้มอยากเปิดร้าน — ทบทวนอุปมาท่าเรือจากบทที่ 1: ตู้สินค้า = container, กล่อง Pod ห่อตู้, เรือ = Node, หอบังคับการ = Control Plane

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes Pod lesson (README figure, about 1536x1024).
Scene: A friendly legend poster on the dock. Nong Som points with a pointer stick at four rounded cards arranged left to right: an orange shipping container; a teal translucent Pod cabin box wrapping that container with a small IP tag; a blue cargo ship carrying the Pod box; a navy harbor control tower. Thin arrows show nesting: container inside Pod, Pod on ship, tower directing ships.
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 001 classroom illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps one or more shipping containers and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock (lab-control-plane); image registry = warehouse of container blueprints.
Text (verbatim, at most 4 short labels): "container = ตู้สินค้า"; "Pod = กล่องห่อตู้"; "Node = เรือ"; "Control Plane = หอบังคับการ".
Constraints: only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; do not show Service, NodePort, Deployment, ReplicaSet or Ingress objects or words.
```

## 03-what-is-a-pod.png

> T03 · 2. Pod คืออะไร — Pod คือหน่วยเล็กที่สุดที่ Kubernetes deploy ได้ ห่อ container ตั้งแต่ 1 ตัวขึ้นไป มี IP เดียวและใช้ volume ร่วมกันได้

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes Pod lesson (README figure, about 1536x1024).
Scene: Close-up cutaway of one big teal Pod cabin box. Inside sit two shipping containers (one orange labeled app, one blue labeled helper) side by side, both plugged into one shared network plug with a single IP tag on the box roof, and a shared shelf (volume) at the bottom that both can reach. Nong Som holds a magnifying glass, looking inside with curiosity.
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 001 classroom illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps one or more shipping containers and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock (lab-control-plane); image registry = warehouse of container blueprints.
Text (verbatim, at most 5 short labels): "Pod"; "IP: 10.244.1.5"; "container"; "volume ร่วม"; "หน่วยเล็กที่สุด".
Constraints: only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; do not show Service, NodePort, Deployment, ReplicaSet or Ingress objects or words; exactly one IP tag on the Pod box, containers have no IP tags of their own.
```

## 04-why-pod-not-container.png

> T04 · 3. ทำไมต้องมี Pod — container ที่ต้องทำงานใกล้ชิดกันถูกห่อไว้ใน Pod เดียว จึงถูกสร้าง ย้าย และลบไปพร้อมกัน

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes Pod lesson (README figure, about 1536x1024).
Scene: Two-panel comparison. Left panel: two loose shipping containers (app and log helper) drifting apart on separate small rafts, connected by a stretched, fraying rope, Nong Som looks worried. Right panel: the same two containers safely packed together in one teal Pod cabin box being lifted by a crane as one unit, Nong Som gives a thumbs-up. A big arrow from left to right.
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 001 classroom illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps one or more shipping containers and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock (lab-control-plane); image registry = warehouse of container blueprints.
Text (verbatim, at most 3 short labels): "แยกกัน = วุ่นวาย"; "อยู่ด้วยกัน ไปด้วยกัน"; "Pod".
Constraints: only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; do not show Service, NodePort, Deployment, ReplicaSet or Ingress objects or words.
```

## 05-pod-lives-on-one-node.png

> T05 · 4. Pod กับ Node — kube-scheduler เลือกเรือให้ Pod ครั้งเดียว ทุก container ใน Pod อยู่บน Node เดียวกันเสมอ ไม่มีการแยกครึ่ง Pod ข้ามเรือ

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes Pod lesson (README figure, about 1536x1024).
Scene: Harbor view: control tower labeled lab-control-plane on the dock, two cargo ships named lab-worker and lab-worker2. A planner figure with a clipboard on the tower balcony (kube-scheduler, faceless sailor silhouette) assigns one whole Pod box with two containers onto lab-worker. Inset at bottom right: a crossed-out illustration of a Pod split in half with one container on each ship, red X. Nong Som waves a signal flag toward lab-worker.
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 001 classroom illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps one or more shipping containers and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock (lab-control-plane); image registry = warehouse of container blueprints.
Text (verbatim, at most 4 short labels): "lab-control-plane"; "lab-worker"; "lab-worker2"; "Pod อยู่บน Node เดียว".
Constraints: only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; do not show Service, NodePort, Deployment, ReplicaSet or Ingress objects or words; no Pod boxes on the control tower; the valid Pod is entirely on one ship.
```

## 06-pod-shared-network-localhost.png

> T06 · 5.1 หนึ่ง Pod หนึ่ง IP — container ใน Pod เดียวกันใช้ network namespace ร่วมกัน มี IP เดียว และคุยกันผ่าน localhost ได้ แต่ห้ามใช้ port ซ้ำกัน

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes Pod lesson (README figure, about 1536x1024).
Scene: Cutaway of a Pod box with one IP tag 10.244.1.7 on its roof. Inside, an orange container web listening on port 3000 and a blue container db listening on port 5432, connected by a short internal speaking tube labeled localhost:5432. Nong Som stands inside the cabin holding a tin-can phone between them. A small warning card in the corner shows two containers both wanting port 80 with a red X.
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 001 classroom illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps one or more shipping containers and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock (lab-control-plane); image registry = warehouse of container blueprints.
Text (verbatim, at most 5 short labels): "IP: 10.244.1.7"; "web :3000"; "db :5432"; "localhost:5432"; "port ห้ามชนกัน".
Constraints: only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; do not show Service, NodePort, Deployment, ReplicaSet or Ingress objects or words; only one IP for the whole Pod.
```

## 07-pod-to-pod-ip.png

> T07 · 5.2 Pod คุยกับ Pod — แต่ละ Pod มี IP ของตัวเองบนเครือข่ายคลัสเตอร์ (CNI) Pod ต่างเรือคุยกันด้วย Pod IP ได้ แต่ IP จะเปลี่ยนเมื่อ Pod ถูกสร้างใหม่

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes Pod lesson (README figure, about 1536x1024).
Scene: Two cargo ships lab-worker and lab-worker2, each carrying one Pod box with its own IP tag (10.244.1.7 and 10.244.2.4). A dotted underwater cable (cluster pod network) connects the two Pods with a message envelope travelling along it. Nong Som on a small boat between the ships holds a note card showing an old IP crossed out and a new IP written below, looking surprised.
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 001 classroom illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps one or more shipping containers and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock (lab-control-plane); image registry = warehouse of container blueprints.
Text (verbatim, at most 4 short labels): "10.244.1.7"; "10.244.2.4"; "Pod network (CNI)"; "IP เปลี่ยนได้!".
Constraints: only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; do not show Service, NodePort, Deployment, ReplicaSet or Ingress objects or words.
```

## 08-pod-creation-journey.png

> T08 · 6. เส้นทางการเกิดของ Pod — ลำดับเมื่อสั่ง kubectl apply: kube-apiserver บันทึกลง etcd, kube-scheduler เลือก Node, kubelet สั่ง container runtime ดึง image และเริ่ม container

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes Pod lesson (README figure, about 1536x1024).
Scene: Left-to-right numbered journey path across the harbor. 1 Nong Som hands a YAML work order into the control tower window (kube-apiserver); 2 the order is filed in a vault drawer (etcd); 3 a planner pins the Pod onto a ship chart (kube-scheduler); 4 the ship's first mate (kubelet) on lab-worker receives the order; 5 a crane (container runtime) pulls a container from the warehouse registry and places it into the Pod box; 6 the Pod box glows with a green Running badge.
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 001 classroom illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps one or more shipping containers and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock (lab-control-plane); image registry = warehouse of container blueprints.
Text (verbatim, at most 6 short labels): "kubectl apply"; "kube-apiserver"; "etcd"; "kube-scheduler"; "kubelet"; "Running".
Constraints: only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; do not show Service, NodePort, Deployment, ReplicaSet or Ingress objects or words; numbers 1-6 as small circles only, no other text.
```

## 09-yaml-syntax-basics.png

> T09 · 7.1 พื้นฐาน YAML — YAML ใช้ key: value, การเยื้องด้วยช่องว่างบอกลำดับชั้น และขีด - บอกรายการ (list)

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes Pod lesson (README figure, about 1536x1024).
Scene: Nong Som stands next to a large clipboard showing a short colorful YAML snippet with indentation guides drawn as faint vertical dotted lines: shop: then indented name and port, then a list of two items with dashes. Three callout tags point to the parts: key: value, indentation with 2 spaces, and list items. Nong Som measures the indent with a tiny ruler.
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 001 classroom illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps one or more shipping containers and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock (lab-control-plane); image registry = warehouse of container blueprints.
Text (verbatim, at most 4 short labels): "key: value"; "เยื้อง 2 ช่องว่าง"; "- รายการ (list)"; "YAML".
Constraints: only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; do not show Service, NodePort, Deployment, ReplicaSet or Ingress objects or words; the clipboard snippet may show only these exact lines in monospace: 'shop:', '  name: som', '  port: 3000', '  items:', '    - kibble', '    - treat' (these code lines are allowed in addition to the labels).
```

## 10-yaml-common-mistakes.png

> T10 · 7.2 ข้อผิดพลาดยอดฮิตของ YAML — ข้อผิดพลาดที่พบบ่อย: ใช้ Tab แทนช่องว่าง, ลืมเว้นวรรคหลังเครื่องหมาย :, และเยื้องผิดระดับ

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes Pod lesson (README figure, about 1536x1024).
Scene: Three small rounded cards in a row, each showing a broken YAML line with a red X on the left and the fixed line with a green check on the right: a tab arrow symbol versus spaces dots; a missing space after the colon; a wrongly indented line. Nong Som holds a big eraser and a pencil, fixing the cards with a determined look.
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 001 classroom illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps one or more shipping containers and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock (lab-control-plane); image registry = warehouse of container blueprints.
Text (verbatim, at most 3 short labels): "ห้ามใช้ Tab"; "ต้องเว้นวรรคหลัง :"; "เยื้องให้ตรงระดับ".
Constraints: only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; do not show Service, NodePort, Deployment, ReplicaSet or Ingress objects or words; code on cards limited to 'name:som' (wrong) and 'name: som' (right), otherwise use symbols.
```

## 11-manifest-four-parts.png

> T11 · 8.1 โครงสร้าง manifest — Pod manifest มี 4 ส่วนหลัก: apiVersion, kind, metadata และ spec

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes Pod lesson (README figure, about 1536x1024).
Scene: A big work-order document pinned on a board, split into four colored horizontal bands, each with a matching icon: apiVersion v1 (version stamp), kind Pod (Pod box icon), metadata (name tag and label tags), spec (blueprint of containers). Nong Som points at the spec band, looking proud.
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 001 classroom illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps one or more shipping containers and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock (lab-control-plane); image registry = warehouse of container blueprints.
Text (verbatim, at most 4 short labels): "apiVersion: v1"; "kind: Pod"; "metadata"; "spec".
Constraints: only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; do not show Service, NodePort, Deployment, ReplicaSet or Ingress objects or words.
```

## 12-spec-vs-status.png

> T12 · 8.2 spec กับ status — spec คือสิ่งที่เราต้องการ (desired state) ส่วน status คือสภาพจริงที่ระบบเขียนรายงานกลับมา

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes Pod lesson (README figure, about 1536x1024).
Scene: Split view. Left: Nong Som writes on an order form labeled spec with a pencil (what we want: one nginx container). Right: the ship's first mate (kubelet, a friendly sailor silhouette without text) fills in a report card labeled status with phase Running and a podIP field. A two-way arrow between them showing comparison.
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 001 classroom illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps one or more shipping containers and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock (lab-control-plane); image registry = warehouse of container blueprints.
Text (verbatim, at most 4 short labels): "spec = ที่ต้องการ"; "status = ที่เป็นจริง"; "phase: Running"; "podIP".
Constraints: only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; do not show Service, NodePort, Deployment, ReplicaSet or Ingress objects or words; the kubelet helper is a simple faceless sailor silhouette, not a second cat.
```

## 13-container-image-ports.png

> T13 · 9.1 image และ ports — ระบุ image พร้อม tag เสมอ และ containerPort เป็นเพียงข้อมูลบอกว่า container ฟังพอร์ตใด ไม่ได้เปิดพอร์ตออกนอกคลัสเตอร์

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes Pod lesson (README figure, about 1536x1024).
Scene: Nong Som at the warehouse registry counter picking a container blueprint box labeled nginx:1.27-alpine, while a box labeled latest sits behind with a small caution sign. On the right a shipping container has a door with a small port plate 80 and a dotted info tag (documentation note), with no path leading outside the harbor.
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 001 classroom illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps one or more shipping containers and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock (lab-control-plane); image registry = warehouse of container blueprints.
Text (verbatim, at most 4 short labels): "nginx:1.27-alpine"; "ระบุ tag เสมอ"; "containerPort: 80"; "imagePullPolicy".
Constraints: only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; do not show Service, NodePort, Deployment, ReplicaSet or Ingress objects or words.
```

## 14-env-variables.png

> T14 · 9.2 env — env ส่งค่าตั้งค่าเข้า container เป็นคู่ name/value โดย value ต้องเป็นข้อความ (string)

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes Pod lesson (README figure, about 1536x1024).
Scene: Nong Som attaches small labeled envelopes onto the side of an orange shipping container through a mail slot. The envelopes show env pairs. One envelope with a number has quotes highlighted to show it must be a string.
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 001 classroom illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps one or more shipping containers and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock (lab-control-plane); image registry = warehouse of container blueprints.
Text (verbatim, at most 4 short labels): "env"; "SHOP_NAME"; "DB_PORT: "5432""; "ค่าเป็น string".
Constraints: only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; do not show Service, NodePort, Deployment, ReplicaSet or Ingress objects or words.
```

## 15-command-args-override.png

> T15 · 9.3 command และ args — command ใน Pod ทับ ENTRYPOINT และ args ทับ CMD ของ image

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes Pod lesson (README figure, about 1536x1024).
Scene: Two-row comparison table drawn as cards. Top row: Dockerfile card with ENTRYPOINT and CMD. Bottom row: Pod YAML card with command and args. Curved arrows show command replaces ENTRYPOINT and args replaces CMD. Nong Som swaps a sticker on the container door with a new instruction sticker.
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 001 classroom illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps one or more shipping containers and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock (lab-control-plane); image registry = warehouse of container blueprints.
Text (verbatim, at most 5 short labels): "ENTRYPOINT"; "CMD"; "command"; "args"; "ทับค่าใน image".
Constraints: only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; do not show Service, NodePort, Deployment, ReplicaSet or Ingress objects or words.
```

## 16-resources-requests-limits.png

> T16 · 9.4 resources — requests ใช้ตอนเลือก Node (จองที่) ส่วน limits คือเพดานจริง ใช้ memory เกิน limit จะถูก OOMKilled ส่วน CPU จะถูกชะลอ

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes Pod lesson (README figure, about 1536x1024).
Scene: On the dock, a ship cargo-capacity gauge. Nong Som books space for a Pod box using a reservation ticket (requests: cpu 100m, memory 128Mi). Next to it the Pod box has a ceiling bar (limits). Small inset: a container overflowing past the memory ceiling with a burst icon (OOMKilled); another inset: a CPU turtle slowing down (throttled).
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 001 classroom illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps one or more shipping containers and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock (lab-control-plane); image registry = warehouse of container blueprints.
Text (verbatim, at most 4 short labels): "requests = จองที่"; "limits = เพดาน"; "OOMKilled"; "CPU ถูกชะลอ".
Constraints: only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; do not show Service, NodePort, Deployment, ReplicaSet or Ingress objects or words.
```

## 17-labels-selectors.png

> T17 · 10. Labels และ Selectors — labels คือป้ายแท็กคู่ key=value ที่ติดกับ Pod และใช้ selector -l ค้นหากลุ่ม Pod ได้

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes Pod lesson (README figure, about 1536x1024).
Scene: A row of four Pod boxes on a ship, each with hanging colored tags (app=som-shop, tier=web / tier=db, app=toy-shop). Nong Som holds a magnet-like selector wand labeled with a filter; the two Pods with app=som-shop tags light up and lift slightly, others stay dim.
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 001 classroom illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps one or more shipping containers and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock (lab-control-plane); image registry = warehouse of container blueprints.
Text (verbatim, at most 5 short labels): "app=som-shop"; "tier=web"; "tier=db"; "app=toy-shop"; "-l app=som-shop".
Constraints: only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; do not show Service, NodePort, Deployment, ReplicaSet or Ingress objects or words.
```

## 18-kubectl-explain-dry-run.png

> T18 · 11.1 เครื่องมือเสริมเมื่อต้องเขียนไฟล์เอง — kubectl explain เป็นคู่มือ field ของ YAML และ --dry-run=client -o yaml ช่วยร่างไฟล์ Pod โดยยังไม่สร้างจริง

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes Pod lesson (README figure, about 1536x1024).
Scene: Nong Som at a desk. Left: an open thick manual book with a magnifier on the page labeled kubectl explain. Right: a small printer printing a draft YAML sheet stamped with a dashed outline DRAFT shape (no extra text), labeled with the dry-run command. A pencil and a clean pod.yaml file card wait on the desk.
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 001 classroom illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps one or more shipping containers and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock (lab-control-plane); image registry = warehouse of container blueprints.
Text (verbatim, at most 4 short labels): "kubectl explain"; "--dry-run=client -o yaml"; "ร่าง ยังไม่สร้างจริง"; "pod.yaml".
Constraints: only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; do not show Service, NodePort, Deployment, ReplicaSet or Ingress objects or words.
```

## 19-pod-phases.png

> T19 · 12.1 Pod phase — Pod phase มี 5 ค่า: Pending, Running, Succeeded, Failed และ Unknown

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes Pod lesson (README figure, about 1536x1024).
Scene: A timeline path along the dock with five stations as rounded signposts: Pending (Pod box waiting on the dock with an hourglass), Running (box on ship with green light), then a fork to Succeeded (green check, finished cargo) and Failed (red X). A separate foggy side station Unknown (ship lost in fog, cannot contact node). Nong Som walks along the path with a lantern.
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 001 classroom illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps one or more shipping containers and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock (lab-control-plane); image registry = warehouse of container blueprints.
Text (verbatim, at most 5 short labels): "Pending"; "Running"; "Succeeded"; "Failed"; "Unknown".
Constraints: only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; do not show Service, NodePort, Deployment, ReplicaSet or Ingress objects or words.
```

## 20-container-states-restartpolicy.png

> T20 · 12.2 สถานะ container และ restartPolicy — container มีสถานะ Waiting, Running, Terminated และ restartPolicy (Always, OnFailure, Never) กำหนดว่า kubelet จะ restart container ใน Pod เดิมหรือไม่

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes Pod lesson (README figure, about 1536x1024).
Scene: Top row: three container state icons: Waiting (hourglass), Running (play), Terminated (stop square). Bottom: three switch dials on a ship control panel labeled with the three restartPolicy values; Nong Som turns the Always dial (default). A small circular arrow shows the same container restarting inside the same Pod box, not a new Pod.
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 001 classroom illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps one or more shipping containers and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock (lab-control-plane); image registry = warehouse of container blueprints.
Text (verbatim, at most 6 short labels): "Waiting"; "Running"; "Terminated"; "Always"; "OnFailure"; "Never".
Constraints: only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; do not show Service, NodePort, Deployment, ReplicaSet or Ingress objects or words.
```

## 21-crashloopbackoff.png

> T21 · 12.3 CrashLoopBackOff — container ล้มซ้ำ ๆ kubelet จะ restart โดยรอนานขึ้นเรื่อย ๆ 10 วินาที, 20, 40 ... สูงสุด 5 นาที เรียกว่า CrashLoopBackOff

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes Pod lesson (README figure, about 1536x1024).
Scene: A container inside a Pod box repeatedly toppling over and being stood up again by the ship's first mate (kubelet, a faceless sailor silhouette). Above it, a spiral of growing clock icons showing increasing wait times. Nong Som reads a log scroll beside it with a thinking expression (curious face from the reference sheet).
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 001 classroom illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps one or more shipping containers and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock (lab-control-plane); image registry = warehouse of container blueprints.
Text (verbatim, at most 4 short labels): "CrashLoopBackOff"; "10s → 20s → 40s"; "สูงสุด 5 นาที"; "logs --previous".
Constraints: only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; do not show Service, NodePort, Deployment, ReplicaSet or Ingress objects or words.
```

## 22-imagepullbackoff.png

> T22 · 12.4 ImagePullBackOff — ถ้าชื่อหรือ tag ของ image ผิด หรือ image อยู่แค่ในเครื่องแต่ไม่ได้ kind load node จะดึง image ไม่ได้และขึ้น ErrImagePull / ImagePullBackOff

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes Pod lesson (README figure, about 1536x1024).
Scene: At the warehouse registry, a crane on the ship tries to grab a container blueprint box labeled nginx:9.99 from an empty shelf; a 'not found' style empty slot. The empty Pod box waits on the ship. Nong Som checks a delivery slip with a surprised face (surprised expression from the reference).
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 001 classroom illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps one or more shipping containers and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock (lab-control-plane); image registry = warehouse of container blueprints.
Text (verbatim, at most 4 short labels): "ErrImagePull"; "ImagePullBackOff"; "nginx:9.99"; "tag ผิด?".
Constraints: only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; do not show Service, NodePort, Deployment, ReplicaSet or Ingress objects or words.
```

## 23-probes-three-inspectors.png

> T23 · 13.1 Probes — kubelet ใช้ probe ตรวจสุขภาพ container: startupProbe รอให้เริ่มเสร็จ, livenessProbe ตรวจว่ายังมีชีวิต, readinessProbe ตรวจว่าพร้อมรับงาน

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes Pod lesson (README figure, about 1536x1024).
Scene: Three inspector stations next to one Pod box, each shown as a small stethoscope icon card: startup (alarm clock, waits for slow start), liveness (heartbeat line; failure arrow leads to a restart circular arrow), readiness (open/closed shop sign; failure shows READY 0/1 but no restart). Nong Som wears a stethoscope and listens to the container.
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 001 classroom illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps one or more shipping containers and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock (lab-control-plane); image registry = warehouse of container blueprints.
Text (verbatim, at most 4 short labels): "startupProbe"; "livenessProbe → restart"; "readinessProbe → READY 0/1"; "kubelet ตรวจ".
Constraints: only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; do not show Service, NodePort, Deployment, ReplicaSet or Ingress objects or words.
```

## 24-probe-mechanisms.png

> T24 · 13.2 กลไกของ probe — probe ตรวจได้ 3 แบบหลัก: httpGet, tcpSocket และ exec พร้อมพารามิเตอร์ periodSeconds และ failureThreshold

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes Pod lesson (README figure, about 1536x1024).
Scene: Three tool cards: httpGet (a small HTTP request arrow to /api/health returning 200 green), tcpSocket (a plug knocking on port 5432), exec (a terminal icon running a command and returning exit code 0). Below, a slider panel shows timing knobs. Nong Som holds a clipboard checklist.
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 001 classroom illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps one or more shipping containers and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock (lab-control-plane); image registry = warehouse of container blueprints.
Text (verbatim, at most 5 short labels): "httpGet /api/health"; "tcpSocket :5432"; "exec"; "periodSeconds"; "failureThreshold".
Constraints: only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; do not show Service, NodePort, Deployment, ReplicaSet or Ingress objects or words.
```

## 25-emptydir-shared-shelf.png

> T25 · 14. Volume: emptyDir — emptyDir เป็นพื้นที่เก็บไฟล์ร่วมของ Pod ข้อมูลรอดเมื่อ container restart แต่หายไปเมื่อ Pod ถูกลบ

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes Pod lesson (README figure, about 1536x1024).
Scene: Three-step story strip. Step 1: inside a Pod box, two containers put files on a shared shelf labeled emptyDir. Step 2: one container falls over and stands up again (restart) while the shelf files are still there, green check. Step 3: the whole Pod box is removed by a crane and the shelf vanishes with it, files gone, red X. Nong Som reacts in each step (happy, relieved, surprised).
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 001 classroom illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps one or more shipping containers and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock (lab-control-plane); image registry = warehouse of container blueprints.
Text (verbatim, at most 3 short labels): "emptyDir"; "container restart: ข้อมูลอยู่"; "ลบ Pod: ข้อมูลหาย".
Constraints: only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; do not show Service, NodePort, Deployment, ReplicaSet or Ingress objects or words.
```

## 26-init-containers.png

> T26 · 15.1 Init container — init container รันทีละตัวตามลำดับและต้องจบสำเร็จก่อน app container จึงจะเริ่มทำงาน

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes Pod lesson (README figure, about 1536x1024).
Scene: A Pod box on a ship with a small prep stage in front. Two init containers line up and finish one after another (step 1 then step 2, each turning a green check), then the main app container starts with a green play icon. Nong Som as a stage manager holds a stopwatch. Status pill shows Init:1/2 progressing.
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 001 classroom illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps one or more shipping containers and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock (lab-control-plane); image registry = warehouse of container blueprints.
Text (verbatim, at most 4 short labels): "init 1 ✓"; "init 2 ✓"; "app เริ่มทำงาน"; "Init:1/2".
Constraints: only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; do not show Service, NodePort, Deployment, ReplicaSet or Ingress objects or words.
```

## 27-sidecar-pattern.png

> T27 · 15.2 Sidecar container — sidecar ทำงานคู่กับ container หลักตลอดอายุ Pod เช่น เก็บ log หรือเตรียมไฟล์ผ่าน volume ร่วม; native sidecar คือ initContainers ที่ตั้ง restartPolicy: Always

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes Pod lesson (README figure, about 1536x1024).
Scene: Inside a Pod box: a main orange container app writes log pages onto a shared emptyDir shelf, and a smaller teal sidecar container (like a sidecar attached to a motorcycle) reads them and ships them out. A small YAML card below shows the native sidecar idea. Nong Som rides happily in the sidecar seat.
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 001 classroom illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps one or more shipping containers and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock (lab-control-plane); image registry = warehouse of container blueprints.
Text (verbatim, at most 4 short labels): "app"; "sidecar"; "emptyDir"; "initContainers + restartPolicy: Always".
Constraints: only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; do not show Service, NodePort, Deployment, ReplicaSet or Ingress objects or words.
```

## 28-debug-toolkit.png

> T28 · 16. เข้าถึงและดีบัก Pod — ชุดเครื่องมือดีบัก Pod: get -o wide, describe (Events), logs, exec และ port-forward

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes Pod lesson (README figure, about 1536x1024).
Scene: Nong Som opens a captain's toolbox on the dock. Five tools pop out, each tied to a Pod box on a ship: binoculars (get -o wide), detective notebook (describe events), log scroll (logs), a door key into the container (exec -it), and a tunnel pipe (port-forward).
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 001 classroom illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps one or more shipping containers and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock (lab-control-plane); image registry = warehouse of container blueprints.
Text (verbatim, at most 5 short labels): "get -o wide"; "describe"; "logs"; "exec -it"; "port-forward".
Constraints: only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; do not show Service, NodePort, Deployment, ReplicaSet or Ingress objects or words.
```

## 29-port-forward-ssh-tunnel.png

> T29 · 16.1 เปิดเว็บจากเครื่องนักศึกษา — เปิดเว็บใน Pod จาก browser: เครื่องนักศึกษา → ssh -L → container k8s-lab → kubectl port-forward → Pod

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes Pod lesson (README figure, about 1536x1024).
Scene: Left-to-right chain of rounded cards connected by two tunnel pipes. Card 1: student laptop with a browser showing localhost:3000. Tunnel 1 labeled ssh -L (to port 2223). Card 2: k8s-lab container box holding a terminal. Tunnel 2 labeled kubectl port-forward. Card 3: a ship with a Pod box listening on port 3000. Nong Som crawls happily through the tunnel carrying a web page.
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 001 classroom illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps one or more shipping containers and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock (lab-control-plane); image registry = warehouse of container blueprints.
Text (verbatim, at most 5 short labels): "localhost:3000"; "ssh -L 3000"; "k8s-lab"; "kubectl port-forward"; "Pod :3000".
Constraints: only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; do not show Service, NodePort, Deployment, ReplicaSet or Ingress objects or words; no NodePort 30080-30082 shown, no direct arrow from laptop to Pod.
```

## 30-pod-is-ephemeral.png

> T30 · 17. Pod เป็นของชั่วคราว — Pod เดี่ยวที่ถูกลบจะไม่มีใครสร้างคืนให้ และ Pod ใหม่จะได้ IP ใหม่กับ emptyDir ว่างเปล่า

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes Pod lesson (README figure, about 1536x1024).
Scene: A crane removes a Pod box from the ship; the spot is empty with a dashed outline and a small sad paw print. Nong Som stands on the dock looking at an empty spot with a surprised expression. A thought cloud shows a new Pod box with a different IP tag. No other worker appears to rebuild it.
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 001 classroom illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps one or more shipping containers and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock (lab-control-plane); image registry = warehouse of container blueprints.
Text (verbatim, at most 4 short labels): "kubectl delete pod"; "ไม่มีใครสร้างคืน"; "IP ใหม่"; "ข้อมูลหาย".
Constraints: only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; do not show Service, NodePort, Deployment, ReplicaSet or Ingress objects or words.
```

## 31-next-chapter-preview.png

> T31 · 18. ปูทางบทหน้า — บทหน้า: Deployment ช่วยดูแลและสร้าง Pod ใหม่ให้อัตโนมัติ และ Service ให้ที่อยู่คงที่แม้ IP ของ Pod เปลี่ยน

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes Pod lesson (README figure, about 1536x1024).
Scene: Preview panel. Nong Som looks through a telescope toward the next harbor. Through the lens: a fleet manager crew (Deployment) automatically placing replacement Pod boxes onto ships, and a lighthouse with a fixed address (Service) beaming to several Pods behind it. A banner flag at the horizon says next chapter.
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 001 classroom illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps one or more shipping containers and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock (lab-control-plane); image registry = warehouse of container blueprints.
Text (verbatim, at most 5 short labels): "บทถัดไป"; "Deployment"; "Service"; "สร้าง Pod ใหม่อัตโนมัติ"; "ที่อยู่คงที่".
Constraints: only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; show Deployment and Service only as a distant preview seen through the telescope.
```

## 32-chapter-summary.png

> T32 · 19. สรุป — สรุปบทที่ 2: Pod, YAML, lifecycle, probes, emptyDir และ multi-container พร้อมสำหรับ LAB

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes Pod lesson (README figure, about 1536x1024).
Scene: Nong Som stands proudly holding a completed checklist board with six check-marked icon rows: Pod box, YAML document, lifecycle timeline, stethoscope probe, emptyDir shelf, multi-container Pod. Behind Nong Som a cargo ship with a neat Pod box sails into sunset-colored teal waves (keep white background, waves as small flat shapes).
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 001 classroom illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps one or more shipping containers and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock (lab-control-plane); image registry = warehouse of container blueprints.
Text (verbatim, exactly 7 short labels): "สรุปบทที่ 2"; "Pod"; "YAML"; "Lifecycle"; "Probes"; "emptyDir"; "Multi-container". The checklist board has EXACTLY 6 rows and EVERY row has its text label (Pod, YAML, Lifecycle, Probes, emptyDir, Multi-container) — no row without text.
Constraints: only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; do not show Service, NodePort, Deployment, ReplicaSet or Ingress objects or words.
```
