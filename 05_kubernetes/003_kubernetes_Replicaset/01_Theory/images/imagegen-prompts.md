Generated with built-in image_gen via cyolo1 using 00-character-som.png as character reference

# Final image prompts — 003 Kubernetes ReplicaSet (Theory)

ทุกภาพแนบ `01_Theory/images/00-character-som.png` เป็นภาพอ้างอิงตัวละครน้องส้ม

## 01-opening-shop-closed.png

> 1. เริ่มเรื่อง — Pod เดี่ยวของร้านน้องส้มถูกลบ ร้านปิด ลูกค้ารอ

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes ReplicaSet lesson (README figure, about 1536x1024).
Scene: On the deck of cargo ship lab-worker, an empty spot where a teal Pod box used to be, only a faint dashed outline and a few drifting dust puffs remain. Next to it a small shop sign hangs on a post reading the closed text. A queue of three small customer figures (simple round-headed humans, not cats) waits with empty bowls. Nong Som stands nearby, paws on cheeks, shocked and sad.
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly. Nong Som is the ONLY cat in the picture.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, plain white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 002 illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps one shipping container and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock (lab-control-plane); ReplicaSet = crew chief, a faceless navy sailor silhouette (a human figure, NOT a cat, no animal features) holding a clipboard that reads replicas: 3; template = a box mold / stamp that produces identical teal Pod boxes; selector = a tag on each Pod box that the crew chief counts.
Text (verbatim, at most 2 short labels): "ร้านปิด"; "Pod หาย".
Constraints: only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; exactly one cat (Nong Som); the crew chief is a faceless human sailor silhouette, never a cat; do not show Service, Deployment, Ingress or NodePort objects or words.
```

## 02-harbor-metaphor-rs.png

> 1. เริ่มเรื่อง — อุปมาท่าเรือ + ตัวละครใหม่ ReplicaSet = หัวหน้าลูกเรือ

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes ReplicaSet lesson (README figure, about 1536x1024).
Scene: A friendly legend poster on the dock with five rounded cards arranged in a row: (1) an orange shipping container; (2) a teal translucent Pod cabin box wrapping that container with a small IP tag; (3) a blue cargo ship; (4) a navy harbor control tower; (5) NEW card highlighted with a star: the crew chief, a faceless navy sailor silhouette holding a clipboard with replicas: 3. Nong Som stands at the left pointing at the new crew chief card with a pointer stick.
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly. Nong Som is the ONLY cat in the picture.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, plain white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 002 illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps one shipping container and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock (lab-control-plane); ReplicaSet = crew chief, a faceless navy sailor silhouette (a human figure, NOT a cat, no animal features) holding a clipboard that reads replicas: 3; template = a box mold / stamp that produces identical teal Pod boxes; selector = a tag on each Pod box that the crew chief counts.
Text (verbatim, at most 6 short labels): "container"; "Pod"; "Node"; "Control Plane"; "ReplicaSet"; "replicas: 3".
Constraints: only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; exactly one cat (Nong Som); the crew chief is a faceless human sailor silhouette, never a cat; do not show Service, Deployment, Ingress or NodePort objects or words.
```

## 03-what-is-replicaset.png

> 2. ReplicaSet คืออะไร — ดูแล Pod เหมือนกัน 3 ตัวจากแม่พิมพ์เดียว

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes ReplicaSet lesson (README figure, about 1536x1024).
Scene: Center: the crew chief (faceless navy sailor silhouette) holding a clipboard replicas: 3 stands next to a box mold / stamp machine. Three identical teal Pod boxes come out of the mold in a row, each with an orange container inside and a tag app=web; each Pod box has its own different small IP tag. Nong Som on the right counts on her paw, smiling.
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly. Nong Som is the ONLY cat in the picture.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, plain white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 002 illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps one shipping container and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock (lab-control-plane); ReplicaSet = crew chief, a faceless navy sailor silhouette (a human figure, NOT a cat, no animal features) holding a clipboard that reads replicas: 3; template = a box mold / stamp that produces identical teal Pod boxes; selector = a tag on each Pod box that the crew chief counts.
Text (verbatim, at most 3 short labels): "replicas: 3"; "template"; "app=web".
Constraints: only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; exactly one cat (Nong Som); the crew chief is a faceless human sailor silhouette, never a cat; do not show Service, Deployment, Ingress or NodePort objects or words. The tag app=web appears on each of the three Pod boxes.
```

## 04-reconcile-loop.png

> 3. ReplicaSet ทำงานอย่างไร — วงจร นับ เทียบ แก้

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes ReplicaSet lesson (README figure, about 1536x1024).
Scene: A big circular loop of three arrows around the crew chief (faceless navy sailor silhouette with clipboard replicas: 3). Station 1 (top): crew chief counting Pod boxes with tags, label นับ. Station 2 (bottom right): a balance scale comparing 2 boxes vs the number 3, label เทียบ. Station 3 (bottom left): the box mold stamping out one new teal Pod box, label แก้. Nong Som stands outside the loop, watching and nodding.
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly. Nong Som is the ONLY cat in the picture.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, plain white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 002 illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps one shipping container and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock (lab-control-plane); ReplicaSet = crew chief, a faceless navy sailor silhouette (a human figure, NOT a cat, no animal features) holding a clipboard that reads replicas: 3; template = a box mold / stamp that produces identical teal Pod boxes; selector = a tag on each Pod box that the crew chief counts.
Text (verbatim, at most 4 short labels): "นับ"; "เทียบ"; "แก้"; "replicas: 3".
Constraints: only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; exactly one cat (Nong Som); the crew chief is a faceless human sailor silhouette, never a cat; do not show Service, Deployment, Ingress or NodePort objects or words.
```

## 05-rs-creation-journey.png

> 3. ตั้งแต่ apply จนได้ Pod — apiserver/etcd → replicaset-controller → scheduler → kubelet

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes ReplicaSet lesson (README figure, about 1536x1024).
Scene: A left-to-right journey with 4 numbered steps along the dock. Step 1: Nong Som hands a paper sheet to the harbor control tower window labeled kube-apiserver, with a small filing cabinet etcd beside it. Step 2: inside the tower, the crew chief (faceless sailor silhouette, clipboard replicas: 3) uses the box mold to stamp 3 teal Pod boxes, labeled replicaset-controller. Step 3: a planner silhouette with binoculars assigns boxes to ships, labeled kube-scheduler. Step 4: two cargo ships lab-worker and lab-worker2 receive the Pod boxes, a small deckhand on each ship opens the box, labeled kubelet.
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly. Nong Som is the ONLY cat in the picture.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, plain white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 002 illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps one shipping container and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock (lab-control-plane); ReplicaSet = crew chief, a faceless navy sailor silhouette (a human figure, NOT a cat, no animal features) holding a clipboard that reads replicas: 3; template = a box mold / stamp that produces identical teal Pod boxes; selector = a tag on each Pod box that the crew chief counts.
Text (verbatim, at most 8 short labels): "kubectl apply"; "kube-apiserver"; "etcd"; "replicaset-controller"; "kube-scheduler"; "kubelet"; "lab-worker"; "lab-worker2".
Constraints: only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; exactly one cat (Nong Som); the crew chief is a faceless human sailor silhouette, never a cat; do not show Service, Deployment, Ingress or NodePort objects or words. Nong Som appears only in step 1.
```

## 06-yaml-rs-nesting.png

> 4.1 YAML ของ ReplicaSet มีแม่พิมพ์ Pod ซ้อนอยู่ข้างใน

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes ReplicaSet lesson (README figure, about 1536x1024).
Scene: A large outer navy rounded box labeled ReplicaSet with a small tab replicas: 3 and a tag selector. Inside it, a smaller teal rounded box labeled template, and inside that a Pod outline containing one orange container. Show nesting with indentation-like steps (like a set of nested trays). Nong Som on the right holds a magnifying glass looking into the inner Pod.
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly. Nong Som is the ONLY cat in the picture.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, plain white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 002 illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps one shipping container and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock (lab-control-plane); ReplicaSet = crew chief, a faceless navy sailor silhouette (a human figure, NOT a cat, no animal features) holding a clipboard that reads replicas: 3; template = a box mold / stamp that produces identical teal Pod boxes; selector = a tag on each Pod box that the crew chief counts.
Text (verbatim, at most 6 short labels): "ReplicaSet"; "replicas: 3"; "selector"; "template"; "Pod"; "container".
Constraints: only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; exactly one cat (Nong Som); the crew chief is a faceless human sailor silhouette, never a cat; do not show Service, Deployment, Ingress or NodePort objects or words.
```

## 07-rs-yaml-three-parts.png

> 4.2 สามส่วนสำคัญ replicas / selector / template

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes ReplicaSet lesson (README figure, about 1536x1024).
Scene: Three large rounded cards side by side. Card 1: the crew chief's clipboard showing the number 3, title replicas. Card 2: a tag app=web with a magnifier, title selector. Card 3: a box mold stamping a teal Pod box that already carries the tag app=web, title template. Arrows show selector tag and template tag are the same. Nong Som below the cards giving a thumbs-up.
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly. Nong Som is the ONLY cat in the picture.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, plain white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 002 illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps one shipping container and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock (lab-control-plane); ReplicaSet = crew chief, a faceless navy sailor silhouette (a human figure, NOT a cat, no animal features) holding a clipboard that reads replicas: 3; template = a box mold / stamp that produces identical teal Pod boxes; selector = a tag on each Pod box that the crew chief counts.
Text (verbatim, at most 5 short labels): "replicas"; "selector"; "template"; "3"; "app=web".
Constraints: only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; exactly one cat (Nong Som); the crew chief is a faceless human sailor silhouette, never a cat; do not show Service, Deployment, Ingress or NodePort objects or words. Exactly 3 cards.
```

## 08-selector-must-match.png

> 5.1 selector ต้องตรงกับป้ายในแม่พิมพ์

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes ReplicaSet lesson (README figure, about 1536x1024).
Scene: Two-panel comparison. Left panel (green check): the crew chief's counting tag app=web matches the tag app=web on the Pod box produced by the mold; a big green check mark. Right panel (red X): counting tag app=web but the mold produces Pod boxes tagged app=website; a red stop sign saying the rejected text. Nong Som in the middle, pointing at the mismatch with a surprised face.
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly. Nong Som is the ONLY cat in the picture.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, plain white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 002 illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps one shipping container and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock (lab-control-plane); ReplicaSet = crew chief, a faceless navy sailor silhouette (a human figure, NOT a cat, no animal features) holding a clipboard that reads replicas: 3; template = a box mold / stamp that produces identical teal Pod boxes; selector = a tag on each Pod box that the crew chief counts.
Text (verbatim, at most 4 short labels): "app=web"; "app=website"; "ตรงกัน"; "ไม่ตรง ถูกปฏิเสธ".
Constraints: only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; exactly one cat (Nong Som); the crew chief is a faceless human sailor silhouette, never a cat; do not show Service, Deployment, Ingress or NodePort objects or words.
```

## 09-pod-name-owner.png

> 5.2 ชื่อ Pod สุ่มท้าย + ownerReferences ชี้กลับหา ReplicaSet

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes ReplicaSet lesson (README figure, about 1536x1024).
Scene: Three teal Pod boxes in a row, each with a name plate: web-l96sh, web-mr95m, web-vfd2r. From each box a thin dashed string leads back to the crew chief (faceless sailor silhouette with clipboard) labeled owner: web. Nong Som points at the random suffix part of a name plate.
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly. Nong Som is the ONLY cat in the picture.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, plain white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 002 illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps one shipping container and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock (lab-control-plane); ReplicaSet = crew chief, a faceless navy sailor silhouette (a human figure, NOT a cat, no animal features) holding a clipboard that reads replicas: 3; template = a box mold / stamp that produces identical teal Pod boxes; selector = a tag on each Pod box that the crew chief counts.
Text (verbatim, at most 4 short labels): "web-l96sh"; "web-mr95m"; "web-vfd2r"; "owner: web".
Constraints: only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; exactly one cat (Nong Som); the crew chief is a faceless human sailor silhouette, never a cat; do not show Service, Deployment, Ingress or NodePort objects or words.
```

## 10-self-healing.png

> 6. Self-healing — ลบ Pod แล้ว ReplicaSet สร้าง Pod ใหม่แทน

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes ReplicaSet lesson (README figure, about 1536x1024).
Scene: Three-step comic strip, left to right. Panel 1: three teal Pod boxes on a ship, one is being lifted away by a crane hook with a red X. Panel 2: crew chief (faceless sailor silhouette) looks at clipboard showing 2 / 3. Panel 3: the box mold stamps a brand new teal Pod box with a sparkle and a NEW small IP tag, back to 3 boxes, clipboard shows 3 / 3. Nong Som in panel 3 cheering.
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly. Nong Som is the ONLY cat in the picture.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, plain white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 002 illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps one shipping container and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock (lab-control-plane); ReplicaSet = crew chief, a faceless navy sailor silhouette (a human figure, NOT a cat, no animal features) holding a clipboard that reads replicas: 3; template = a box mold / stamp that produces identical teal Pod boxes; selector = a tag on each Pod box that the crew chief counts.
Text (verbatim, at most 3 short labels): "2 / 3"; "3 / 3"; "Pod ใหม่".
Constraints: only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; exactly one cat (Nong Som); the crew chief is a faceless human sailor silhouette, never a cat; do not show Service, Deployment, Ingress or NodePort objects or words. Nong Som appears only once, in panel 3.
```

## 11-who-fixes-what.png

> 6. kubelet ซ่อม container ส่วน ReplicaSet ซ่อมจำนวน Pod

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes ReplicaSet lesson (README figure, about 1536x1024).
Scene: Split picture. Left half: inside one teal Pod box, an orange container fell over; a deckhand mechanic with a wrench (faceless sailor silhouette) restarts it inside the same box; a counter shows RESTARTS 1; label kubelet. Right half: a Pod box is missing from a row of three; the crew chief with clipboard brings a brand new Pod box from the mold; label ReplicaSet. Nong Som stands at the center divider, pointing both ways.
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly. Nong Som is the ONLY cat in the picture.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, plain white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 002 illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps one shipping container and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock (lab-control-plane); ReplicaSet = crew chief, a faceless navy sailor silhouette (a human figure, NOT a cat, no animal features) holding a clipboard that reads replicas: 3; template = a box mold / stamp that produces identical teal Pod boxes; selector = a tag on each Pod box that the crew chief counts.
Text (verbatim, at most 4 short labels): "kubelet"; "ReplicaSet"; "RESTARTS 1"; "Pod ใหม่".
Constraints: only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; exactly one cat (Nong Som); the crew chief is a faceless human sailor silhouette, never a cat; do not show Service, Deployment, Ingress or NodePort objects or words.
```

## 12-scale-dial.png

> 7. Scale — หมุนปุ่ม replicas เพิ่มลดจำนวน Pod

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes ReplicaSet lesson (README figure, about 1536x1024).
Scene: A big round dial with numbers 0, 2, 3, 5 on the dock, Nong Som turning the knob from 3 to 5. To the right on a cargo ship deck: 3 existing teal Pod boxes plus 2 new ones popping in with sparkles (total 5). The crew chief (faceless sailor silhouette) updates the clipboard to replicas: 5.
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly. Nong Som is the ONLY cat in the picture.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, plain white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 002 illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps one shipping container and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock (lab-control-plane); ReplicaSet = crew chief, a faceless navy sailor silhouette (a human figure, NOT a cat, no animal features) holding a clipboard that reads replicas: 3; template = a box mold / stamp that produces identical teal Pod boxes; selector = a tag on each Pod box that the crew chief counts.
Text (verbatim, at most 6 short labels): "replicas: 5"; "0"; "2"; "3"; "5"; "+2".
Constraints: only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; exactly one cat (Nong Som); the crew chief is a faceless human sailor silhouette, never a cat; do not show Service, Deployment, Ingress or NodePort objects or words. Exactly 5 Pod boxes on the ship.
```

## 13-labels-adopt-release.png

> 8. Labels — ReplicaSet นับจากป้าย รับ Pod แปลกหน้า (ลบทิ้ง) และปล่อย Pod ที่ถอดป้าย

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes ReplicaSet lesson (README figure, about 1536x1024).
Scene: Two-panel picture. Left panel: crew chief (faceless sailor silhouette) counts 4 Pod boxes all tagged app=web, one of them is a stranger box labeled extra-web; the crew chief says too many and a crane hook removes extra-web. Right panel: Nong Som peels the tag off one Pod box; that box now has an empty tag and floats aside on its own, while the mold stamps a new box tagged app=web to fill the row.
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly. Nong Som is the ONLY cat in the picture.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, plain white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 002 illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps one shipping container and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock (lab-control-plane); ReplicaSet = crew chief, a faceless navy sailor silhouette (a human figure, NOT a cat, no animal features) holding a clipboard that reads replicas: 3; template = a box mold / stamp that produces identical teal Pod boxes; selector = a tag on each Pod box that the crew chief counts.
Text (verbatim, at most 4 short labels): "app=web"; "extra-web"; "4 > 3"; "app-".
Constraints: only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; exactly one cat (Nong Som); the crew chief is a faceless human sailor silhouette, never a cat; do not show Service, Deployment, Ingress or NodePort objects or words. Nong Som appears only in the right panel.
```

## 14-spread-cordon.png

> 9. Pod กระจายบนหลายเรือ + cordon ป้ายห้ามรับกล่องใหม่

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes ReplicaSet lesson (README figure, about 1536x1024).
Scene: Harbor view: the control tower lab-control-plane on the dock (no Pod boxes on it). Two cargo ships: lab-worker carries three teal Pod boxes; lab-worker2 carries no boxes and has a big yellow-black barrier sign with the cordon label. A new teal Pod box on a crane is redirected away from lab-worker2 toward lab-worker by a curved arrow. Nong Som on the dock holds the barrier rope.
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly. Nong Som is the ONLY cat in the picture.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, plain white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 002 illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps one shipping container and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock (lab-control-plane); ReplicaSet = crew chief, a faceless navy sailor silhouette (a human figure, NOT a cat, no animal features) holding a clipboard that reads replicas: 3; template = a box mold / stamp that produces identical teal Pod boxes; selector = a tag on each Pod box that the crew chief counts.
Text (verbatim, at most 4 short labels): "lab-control-plane"; "lab-worker"; "lab-worker2"; "cordon".
Constraints: only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; exactly one cat (Nong Som); the crew chief is a faceless human sailor silhouette, never a cat; do not show Service, Deployment, Ingress or NodePort objects or words.
```

## 15-template-update.png

> 10. แก้แม่พิมพ์ 1.0 → 2.0 แล้ว Pod เดิมไม่เปลี่ยน

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes ReplicaSet lesson (README figure, about 1536x1024).
Scene: On the left a box mold whose label was changed from 1.0 to 2.0 (the 1.0 crossed out, 2.0 shiny). On a ship to the right, three existing teal Pod boxes still all labeled version=1.0, each holding an orange container labeled som-menu:1.0. The crew chief (faceless sailor silhouette) checks clipboard showing 3 / 3 with a shrug. Nong Som scratches her head looking at the old boxes, confused.
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly. Nong Som is the ONLY cat in the picture.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, plain white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 002 illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps one shipping container and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock (lab-control-plane); ReplicaSet = crew chief, a faceless navy sailor silhouette (a human figure, NOT a cat, no animal features) holding a clipboard that reads replicas: 3; template = a box mold / stamp that produces identical teal Pod boxes; selector = a tag on each Pod box that the crew chief counts.
Text (verbatim, at most 3 short labels): "som-menu:2.0"; "version=1.0"; "3 / 3".
Constraints: only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; exactly one cat (Nong Som); the crew chief is a faceless human sailor silhouette, never a cat; do not show Service, Deployment, Ingress or NodePort objects or words. The mold shows som-menu:2.0; all three Pod boxes show version=1.0.
```

## 16-som-menu-yaml-skeleton.png

> 11. โครงไฟล์ som-menu-rs.yaml

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes ReplicaSet lesson (README figure, about 1536x1024).
Scene: A large paper document (like a blueprint sheet) pinned on a board, folded into collapsible sections with tab labels: apiVersion / kind, metadata, spec, replicas: 3, selector, template, containers. Each tab has a small icon: crew chief clipboard for replicas, tag for selector, box mold for template, orange container for containers. Nong Som holds the sheet corner, presenting it.
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly. Nong Som is the ONLY cat in the picture.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, plain white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 002 illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps one shipping container and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock (lab-control-plane); ReplicaSet = crew chief, a faceless navy sailor silhouette (a human figure, NOT a cat, no animal features) holding a clipboard that reads replicas: 3; template = a box mold / stamp that produces identical teal Pod boxes; selector = a tag on each Pod box that the crew chief counts.
Text (verbatim, at most 7 short labels): "som-menu-rs.yaml"; "metadata"; "spec"; "replicas: 3"; "selector"; "template"; "containers".
Constraints: only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; exactly one cat (Nong Som); the crew chief is a faceless human sailor silhouette, never a cat; do not show Service, Deployment, Ingress or NodePort objects or words.
```

## 17-port-forward-one-pod.png

> 12. port-forward ต่อท่อเข้า Pod เดียว Pod หายท่อก็ขาด

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes ReplicaSet lesson (README figure, about 1536x1024).
Scene: Left: Nong Som at a laptop showing localhost:8080. A single pipe runs from the laptop to only ONE of three teal Pod boxes on a cargo ship (the other two are not connected). That connected Pod box is being lifted away by a crane hook; the pipe is snapped with a red break spark near it. Nong Som looks surprised.
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly. Nong Som is the ONLY cat in the picture.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, plain white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 002 illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps one shipping container and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock (lab-control-plane); ReplicaSet = crew chief, a faceless navy sailor silhouette (a human figure, NOT a cat, no animal features) holding a clipboard that reads replicas: 3; template = a box mold / stamp that produces identical teal Pod boxes; selector = a tag on each Pod box that the crew chief counts.
Text (verbatim, at most 2 short labels): "localhost:8080"; "lost connection to pod".
Constraints: only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; exactly one cat (Nong Som); the crew chief is a faceless human sailor silhouette, never a cat; do not show Service, Deployment, Ingress or NodePort objects or words. Exactly three Pod boxes, only one pipe.
```

## 18-next-chapter-preview.png

> 12. ปูทางบทถัดไป — Deployment และ Service

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes ReplicaSet lesson (README figure, about 1536x1024).
Scene: Nong Som stands on the dock looking through a brass telescope toward the horizon. In a round telescope-view bubble in the upper right, far away: a fleet manager figure (faceless silhouette with a megaphone) labeled Deployment updating boxes one by one, and a lighthouse with a single beam labeled Service guiding customers to many Pod boxes. In the foreground, the crew chief with clipboard replicas: 3 waves goodbye.
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly. Nong Som is the ONLY cat in the picture.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, plain white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 002 illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps one shipping container and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock (lab-control-plane); ReplicaSet = crew chief, a faceless navy sailor silhouette (a human figure, NOT a cat, no animal features) holding a clipboard that reads replicas: 3; template = a box mold / stamp that produces identical teal Pod boxes; selector = a tag on each Pod box that the crew chief counts.
Text (verbatim, at most 3 short labels): "Deployment"; "Service"; "บทถัดไป".
Constraints: only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; exactly one cat (Nong Som); the crew chief is a faceless human sailor silhouette, never a cat. Deployment and Service appear only inside the distant telescope view.
```

## 19-chapter-summary.png

> 13. สรุปบทที่ 3

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes ReplicaSet lesson (README figure, about 1536x1024).
Scene: A summary poster with 4 rounded cards in a 2x2 grid around a center: (1) clipboard replicas: 3 with three Pod boxes, title นับให้ครบ; (2) a deleted Pod box replaced by a new one with sparkle, title ซ่อมเอง; (3) a dial turning, title scale; (4) a tag app=web, title นับจากป้าย. Nong Som in the center giving a proud salute; the crew chief silhouette stands beside her.
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly. Nong Som is the ONLY cat in the picture.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, plain white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 002 illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps one shipping container and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock (lab-control-plane); ReplicaSet = crew chief, a faceless navy sailor silhouette (a human figure, NOT a cat, no animal features) holding a clipboard that reads replicas: 3; template = a box mold / stamp that produces identical teal Pod boxes; selector = a tag on each Pod box that the crew chief counts.
Text (verbatim, at most 5 short labels): "บทที่ 3 ReplicaSet"; "นับให้ครบ"; "ซ่อมเอง"; "scale"; "นับจากป้าย".
Constraints: only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; exactly one cat (Nong Som); the crew chief is a faceless human sailor silhouette, never a cat; do not show Service, Deployment, Ingress or NodePort objects or words.
```
