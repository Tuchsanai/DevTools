Generated with built-in image_gen via cyolo1 using 00-character-som.png as character reference

# Final image prompts — 002 Kubernetes Pod (LAB)

ทุกภาพแนบ `01_Theory/images/00-character-som.png` เป็นภาพอ้างอิงตัวละครน้องส้ม

## 01-lab0-cluster-up.png

> L01 · LAB0 สร้างคลัสเตอร์ท่าเรือ — LAB0: รัน k8s-up ใน k8s-lab เพื่อสร้าง kind cluster ชื่อ lab มี control-plane 1 ตัวและ worker 2 ตัว

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes Pod lesson (README figure, about 1536x1024).
Scene: Inside a big container card labeled k8s-lab, Nong Som presses a large button on a terminal. The harbor appears inside the card: one control tower lab-control-plane and two ships lab-worker and lab-worker2, each with a green Ready badge. No Pods yet.
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 001 classroom illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps one or more shipping containers and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock (lab-control-plane); image registry = warehouse of container blueprints.
Text (verbatim, at most 5 short labels): "k8s-up"; "lab-control-plane"; "lab-worker"; "lab-worker2"; "Ready".
Constraints: only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; do not show Service, NodePort, Deployment, ReplicaSet or Ingress objects or words; exactly 1 control tower and 2 ships, no Pod boxes.
```

## 02-lab1-kubectl-run.png

> L02 · LAB1 Pod แรกด้วย kubectl run — LAB1: สร้าง Pod แรกด้วย kubectl run แล้วดูสถานะด้วย kubectl get pods -o wide

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes Pod lesson (README figure, about 1536x1024).
Scene: Nong Som speaks a single command into a harbor radio; a crane drops one Pod box (with one orange nginx container) onto ship lab-worker. A status board on the dock shows the Pod row with READY 1/1 and STATUS Running and an IP tag 10.244.x.x.
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 001 classroom illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps one or more shipping containers and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock (lab-control-plane); image registry = warehouse of container blueprints.
Text (verbatim, at most 4 short labels): "kubectl run hello"; "nginx:1.27-alpine"; "1/1 Running"; "lab-worker".
Constraints: only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; do not show Service, NodePort, Deployment, ReplicaSet or Ingress objects or words.
```

## 03-lab2-first-yaml.png

> L03 · LAB2 Pod YAML แรก — LAB2: ร่าง YAML ด้วย --dry-run=client -o yaml เขียน nginx-pod.yaml แล้ว kubectl apply -f

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes Pod lesson (README figure, about 1536x1024).
Scene: Nong Som at a drafting desk writing a YAML blueprint sheet nginx-pod.yaml, then feeding it into a slot in the control tower. The resulting Pod box web appears on a ship. A small reply note shows pod/web created.
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 001 classroom illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps one or more shipping containers and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock (lab-control-plane); image registry = warehouse of container blueprints.
Text (verbatim, at most 3 short labels): "nginx-pod.yaml"; "kubectl apply -f"; "pod/web created".
Constraints: only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; do not show Service, NodePort, Deployment, ReplicaSet or Ingress objects or words.
```

## 04-lab3-exec-logs-portforward.png

> L04 · LAB3 exec / logs / port-forward — LAB3: เข้าไปใน Pod ด้วย exec แก้หน้าเว็บ ดู access log และเปิดเว็บผ่าน port-forward + ssh -L

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes Pod lesson (README figure, about 1536x1024).
Scene: Three mini-scenes in one panel: (a) Nong Som opens the container door with a key (exec) and pins a new page 'สวัสดีจากน้องส้ม' inside; (b) a log scroll unrolls from the container showing GET / lines as simple bars; (c) a tunnel from a student laptop browser through k8s-lab to the Pod on port 80 via local port 8080.
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 001 classroom illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps one or more shipping containers and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock (lab-control-plane); image registry = warehouse of container blueprints.
Text (verbatim, at most 5 short labels): "kubectl exec -it"; "kubectl logs -f"; "port-forward 8080:80"; "ssh -L 8080"; "สวัสดีจากน้องส้ม".
Constraints: only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; do not show Service, NodePort, Deployment, ReplicaSet or Ingress objects or words.
```

## 05-lab4-labels.png

> L05 · LAB4 Labels & Selectors — LAB4: ติดป้าย label ให้ Pod 3 ตัวและใช้ -l เลือกเฉพาะกลุ่มที่ต้องการ

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes Pod lesson (README figure, about 1536x1024).
Scene: Three Pod boxes on a ship: shop-web, shop-cache, toy-web, each with colored tags. Nong Som uses a label gun to stick a new tag env=dev on toy-web, while a selector beam highlights the two app=som-shop Pods.
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 001 classroom illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps one or more shipping containers and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock (lab-control-plane); image registry = warehouse of container blueprints.
Text (verbatim, at most 5 short labels): "shop-web"; "shop-cache"; "toy-web"; "-l app=som-shop"; "env=dev".
Constraints: only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; do not show Service, NodePort, Deployment, ReplicaSet or Ingress objects or words.
```

## 06-lab5-lifecycle-debug.png

> L06 · LAB5 Lifecycle & Debug — LAB5: สังเกต Completed, CrashLoopBackOff และ ImagePullBackOff แล้วใช้ describe กับ logs --previous หาสาเหตุ

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes Pod lesson (README figure, about 1536x1024).
Scene: A status board on the dock lists three Pods with colored status pills: completed-pod Completed (green), crash-pod CrashLoopBackOff (orange) with a growing restart counter, bad-image-pod ImagePullBackOff (red). Nong Som as a detective with a magnifying glass and notebook investigates the red row.
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 001 classroom illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps one or more shipping containers and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock (lab-control-plane); image registry = warehouse of container blueprints.
Text (verbatim, at most 5 short labels): "Completed"; "CrashLoopBackOff"; "ImagePullBackOff"; "kubectl describe"; "logs --previous".
Constraints: only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; do not show Service, NodePort, Deployment, ReplicaSet or Ingress objects or words.
```

## 07-lab6-env-command-resources.png

> L07 · LAB6 env / command / resources — LAB6: ส่ง env และ command เข้า container ทดลอง memory limit จนเกิด OOMKilled และ request CPU เกินจน Pending

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes Pod lesson (README figure, about 1536x1024).
Scene: Three cards: (1) a container receiving an env envelope SHOP_NAME and printing it; (2) a container overflowing a memory ceiling with a burst icon OOMKilled exit 137; (3) a huge Pod box that cannot fit on any ship, waiting on the dock with an hourglass, Pending Insufficient cpu. Nong Som holds a measuring tape.
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 001 classroom illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps one or more shipping containers and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock (lab-control-plane); image registry = warehouse of container blueprints.
Text (verbatim, at most 4 short labels): "SHOP_NAME"; "OOMKilled"; "Pending"; "Insufficient cpu".
Constraints: only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; do not show Service, NodePort, Deployment, ReplicaSet or Ingress objects or words.
```

## 08-lab7-probes.png

> L08 · LAB7 Probes — LAB7: liveness ล้มแล้ว container ถูก restart ส่วน readiness ล้มแล้ว Pod เป็น READY 0/1 โดยไม่ถูก restart

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes Pod lesson (README figure, about 1536x1024).
Scene: Two Pods side by side. Left: liveness-exec-pod with a broken heartbeat line and a circular restart arrow, RESTARTS counter going up. Right: readiness-http-pod with a shop sign flipping between closed (0/1) and open (1/1) as Nong Som creates the file ready.html inside with a paw. Nong Som wears a stethoscope.
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 001 classroom illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps one or more shipping containers and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock (lab-control-plane); image registry = warehouse of container blueprints.
Text (verbatim, at most 4 short labels): "Liveness → restart"; "Readiness → 0/1"; "ready.html"; "RESTARTS".
Constraints: only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; do not show Service, NodePort, Deployment, ReplicaSet or Ingress objects or words.
```

## 09-lab8-multi-container.png

> L09 · LAB8 Multi-container — LAB8: Pod หลาย container คุยกันผ่าน localhost ใช้ emptyDir ร่วมกัน มี init container เตรียมไฟล์ และ sidecar เขียนข้อมูลต่อเนื่อง

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes Pod lesson (README figure, about 1536x1024).
Scene: Cutaway of one Pod box with one IP tag. A small init container prepare finishes first (green check) after placing index.html on an emptyDir shelf; then web (nginx) serves the file and a sidecar menu-writer keeps appending time notes to the shelf. The sidecar reaches web via localhost:80 (same Pod IP). READY pill shows 2/2 (web + menu-writer). Nong Som watches with a clipboard.
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 001 classroom illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps one or more shipping containers and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock (lab-control-plane); image registry = warehouse of container blueprints.
Text (verbatim, at most 6 short labels): "init: prepare ✓"; "web"; "menu-writer"; "emptyDir"; "localhost:80"; "2/2".
Constraints: only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; do not show Service, NodePort, Deployment, ReplicaSet or Ingress objects or words.
```

## 10-lab9-som-shop-storefront.png

> L10 · LAB9 ร้านอาหารแมวน้องส้ม — LAB สุดท้าย: เปิดร้านอาหารแมวน้องส้มด้วย Next.js + PostgreSQL ใน Pod เดียว

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes Pod lesson (README figure, about 1536x1024).
Scene: Grand opening. Nong Som cuts a teal ribbon in front of a cute cat-food shop that sits inside a large teal Pod box on ship lab-worker. Shop shelves show kibble bags, wet food cans and lickable treats. A browser window card floats nearby showing product cards with prices in baht.
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 001 classroom illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps one or more shipping containers and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock (lab-control-plane); image registry = warehouse of container blueprints.
Text (verbatim, at most 4 short labels): "ร้านอาหารแมวน้องส้ม"; "Next.js"; "PostgreSQL"; "1 Pod".
Constraints: only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; do not show Service, NodePort, Deployment, ReplicaSet or Ingress objects or words.
```

## 11-lab9-pod-architecture.png

> L11 · LAB9 สถาปัตยกรรม Pod som-shop — สถาปัตยกรรม Pod som-shop: web (Next.js :3000) คุยกับ db (PostgreSQL :5432) ผ่าน localhost ภายใน Pod เดียว และเก็บข้อมูล DB บน emptyDir

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes Pod lesson (README figure, about 1536x1024).
Scene: Technical cutaway diagram of Pod som-shop with one IP tag on top. Inside: orange container web labeled som-shop-web:1.0 :3000; blue container db labeled postgres:17-alpine :5432 marked as sidecar; an arrow from web to db labeled localhost:5432; db mounts a shelf emptyDir db-data. Two small completed init container chips at the left edge (wait-for-db, db-seed) with check marks. Nong Som points at the localhost arrow.
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 001 classroom illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps one or more shipping containers and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock (lab-control-plane); image registry = warehouse of container blueprints.
Text (verbatim, at most 5 short labels): "Pod: som-shop"; "web :3000"; "db :5432"; "localhost:5432"; "emptyDir db-data".
Constraints: only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; do not show Service, NodePort, Deployment, ReplicaSet or Ingress objects or words; one IP for the whole Pod; web and db are inside the same single Pod box on one ship.
```

## 12-lab9-startup-order.png

> L12 · LAB9 ลำดับการเริ่มทำงาน — ลำดับเริ่ม Pod: db (native sidecar) เริ่มก่อนและผ่าน startupProbe → wait-for-db รอ pg_isready → db-seed สร้างตารางและสินค้า → web เริ่มทำงาน

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes Pod lesson (README figure, about 1536x1024).
Scene: Horizontal timeline with four numbered steps inside a Pod outline: 1 db starts and keeps running (a long bar continuing to the end of the timeline); 2 wait-for-db short bar ending with check; 3 db-seed short bar ending with check, small table icon with 6 products; 4 web starts and runs to the end. A single green status pill Running at the end of the timeline. Nong Som holds a stopwatch.
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 001 classroom illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps one or more shipping containers and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock (lab-control-plane); image registry = warehouse of container blueprints.
Text (verbatim, at most 5 short labels): "1 db (sidecar)"; "2 wait-for-db"; "3 db-seed"; "4 web"; "Running".
Constraints: only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; do not show Service, NodePort, Deployment, ReplicaSet or Ingress objects or words; db bar continues alongside web until the end; init bars 2 and 3 end before web begins. IMPORTANT: db-seed means inserting initial CAT-FOOD product rows into PostgreSQL — depict it as a small database table card with 3 rows showing cat-food icons (kibble bag, fish can, cat treat). Absolutely no fruit, vegetables, plants or garden seeds anywhere.
```

## 13-lab9-build-kind-load.png

> L13 · LAB9 Build image และ kind load — build image som-shop-web:1.0 ใน k8s-lab แล้วใช้ kind load docker-image นำ image เข้าไปในทุก node ของคลัสเตอร์

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes Pod lesson (README figure, about 1536x1024).
Scene: Inside the k8s-lab card: Nong Som operates a small factory machine turning a Dockerfile into a container box som-shop-web:1.0. A conveyor belt labeled kind load docker-image carries copies of the box onto all three nodes (control tower lab-control-plane and ships lab-worker, lab-worker2). Registry warehouse is not needed for this image.
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 001 classroom illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps one or more shipping containers and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock (lab-control-plane); image registry = warehouse of container blueprints.
Text (verbatim, at most 4 short labels): "docker build"; "som-shop-web:1.0"; "kind load docker-image"; "--name lab".
Constraints: only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; do not show Service, NodePort, Deployment, ReplicaSet or Ingress objects or words.
```

## 14-lab9-open-in-browser.png

> L14 · LAB9 เปิดร้านใน browser — เปิดร้านจากเครื่องนักศึกษา: kubectl port-forward pod/som-shop 3000:3000 ใน k8s-lab และ ssh -L 3000:localhost:3000 จากเครื่องนักศึกษา

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes Pod lesson (README figure, about 1536x1024).
Scene: A student laptop on the left shows the shop web page (product cards, an order button) at localhost:3000. A tunnel ssh -L leads into the k8s-lab card, where a second tunnel port-forward leads to the Pod som-shop on a ship, port 3000. Nong Som waves from inside the shop window in the Pod.
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 001 classroom illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps one or more shipping containers and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock (lab-control-plane); image registry = warehouse of container blueprints.
Text (verbatim, at most 4 short labels): "localhost:3000"; "ssh -L 3000:localhost:3000"; "port-forward pod/som-shop"; "สั่งซื้อ".
Constraints: only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; do not show Service, NodePort, Deployment, ReplicaSet or Ingress objects or words; no NodePort 30080-30082, no direct path from laptop to Pod. IMPORTANT: the shop page in the laptop browser is a CAT FOOD store — product cards must show only cat food items (dry kibble bag with fish icon, wet food can, cat treat pouch), orange "สั่งซื้อ" buttons; absolutely no T-shirts, mugs, hats or other merchandise.
```

## 15-lab9-emptydir-survive-vs-lost.png

> L15 · LAB9 ข้อมูลรอดหรือหาย — ทดลองกับข้อมูลออเดอร์: restart container db แล้วข้อมูลยังอยู่บน emptyDir แต่ลบ Pod แล้วข้อมูลหายทั้งหมด

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes Pod lesson (README figure, about 1536x1024).
Scene: Two-panel comparison. Left: inside Pod som-shop, the db container restarts (circular arrow, RESTARTS 1) while the emptyDir shelf still holds order receipts, green check, Nong Som relieved. Right: a crane removes the whole Pod som-shop; the shelf and receipts vanish; a new Pod box arrives with a different IP and an empty shelf with fresh stock, red X on orders, Nong Som surprised.
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 001 classroom illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps one or more shipping containers and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock (lab-control-plane); image registry = warehouse of container blueprints.
Text (verbatim, at most 4 short labels): "restart db: ออเดอร์ยังอยู่"; "ลบ Pod: ออเดอร์หาย"; "emptyDir"; "IP ใหม่".
Constraints: only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; do not show Service, NodePort, Deployment, ReplicaSet or Ingress objects or words.
```

## 16-lab9-next-split.png

> L16 · LAB9 ปูทางบทหน้า — Pod เดียวรวมเว็บกับฐานข้อมูลเป็นการออกแบบเพื่อการเรียนรู้ บทหน้าจะแยก web เป็น Deployment, db ใช้ที่เก็บถาวร และเชื่อมกันด้วย Service

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes Pod lesson (README figure, about 1536x1024).
Scene: Before/after planning board. Left: today's single Pod box containing web and db, marked with a graduation cap icon (learning design). Arrow to right: a preview plan sketch with web Pods managed by a Deployment crew on one side, a db with a durable storage barrel on the other side, and a Service lighthouse connecting them. Nong Som draws on the board with a marker.
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 001 classroom illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps one or more shipping containers and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock (lab-control-plane); image registry = warehouse of container blueprints.
Text (verbatim, at most 5 short labels): "วันนี้: 1 Pod"; "บทหน้า"; "Deployment"; "Service"; "ที่เก็บถาวร".
Constraints: only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; Deployment and Service appear only on the right-hand 'next chapter' sketch.
```

# LAB 0 step figures (added 2026-10-06, cyolo1 gpt-6-astra high, same character reference)

## 01a-lab0-step1-pull-run.png

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes Pod lesson (README figure, about 1536x1024).
Scene: Left to right flow on the student's laptop. Left: a warehouse of container blueprints (the image registry) with one blueprint crate labeled tuchsanai/devtools-kind:2569_1. An arrow labeled docker pull carries the crate to a student laptop in the middle where Nong Som types on the keyboard. A second arrow labeled docker run goes from the laptop to the right where one big closed shipping container card labeled k8s-lab appears, with three small port doors on its side; the first door is tagged 2223 → 22 (SSH door). Inside the k8s-lab card show only simple tool icons (wrench, ship wheel, small engine) and empty water, no ships yet.
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 001 classroom illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps one or more shipping containers and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock (lab-control-plane); image registry = warehouse of container blueprints; the lab container k8s-lab = one big rounded card / giant shipping container that holds everything of the lab.
Text (verbatim, at most 5 short labels): "docker pull"; "tuchsanai/devtools-kind:2569_1"; "docker run"; "k8s-lab"; "2223 → 22".
Constraints: only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos (no Docker whale, no GitHub octocat); do not show Service, NodePort, Deployment, ReplicaSet or Ingress objects or words. No cluster yet: no control tower, no ships, no Pod boxes.
```

## 01b-lab0-step2-ssh.png

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes Pod lesson (README figure, about 1536x1024).
Scene: Left: Nong Som sits at the student laptop with a terminal window. A glowing tunnel / pipe labeled ssh -p 2223 root@localhost runs from the laptop into the door tagged 2223 on the side of a big shipping container card labeled k8s-lab on the right. Inside the k8s-lab card a large terminal screen shows the prompt root@k8s-lab:~# with a blinking cursor, showing that the student is now working inside the container. A small padlock icon on the tunnel opens (login succeeded), with no text on it.
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 001 classroom illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps one or more shipping containers and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock (lab-control-plane); image registry = warehouse of container blueprints; the lab container k8s-lab = one big rounded card / giant shipping container that holds everything of the lab.
Text (verbatim, at most 3 short labels): "ssh -p 2223 root@localhost"; "k8s-lab"; "root@k8s-lab:~#".
Constraints: only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos (no Docker whale, no GitHub octocat); do not show Service, NodePort, Deployment, ReplicaSet or Ingress objects or words. No cluster yet: no control tower, no ships, no Pod boxes; do not write any password.
```

## 01c-lab0-step3-git-clone.png

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes Pod lesson (README figure, about 1536x1024).
Scene: Everything happens inside a big rounded card labeled k8s-lab (the lab container). Top: a generic code-repository cloud (no logo) with a folder labeled DevTools. A stream of folder icons labeled git clone flows down into a cabinet folder labeled /workspace/DevTools inside the card. From that folder a path of stepping stones leads down several nested folders to a highlighted open folder at the end; Nong Som walks along the path holding a map and arrives at the highlighted folder, whose open drawer shows two sub-folders labeled labs and som-shop. A signpost at the start of the path says cd .../02_LAB.
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 001 classroom illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps one or more shipping containers and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock (lab-control-plane); image registry = warehouse of container blueprints; the lab container k8s-lab = one big rounded card / giant shipping container that holds everything of the lab.
Text (verbatim, at most 5 short labels): "git clone"; "/workspace/DevTools"; "cd .../02_LAB"; "labs"; "som-shop".
Constraints: only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos (no Docker whale, no GitHub octocat); do not show Service, NodePort, Deployment, ReplicaSet or Ingress objects or words. No ships, no control tower, no Pod boxes.
```

## 01e-lab0-step5-check-cluster.png

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes Pod lesson (README figure, about 1536x1024).
Scene: Inside a big rounded card labeled k8s-lab, the harbor from the previous panel: exactly one harbor control tower labeled lab-control-plane and two cargo ships labeled lab-worker and lab-worker2. Nong Som stands on the dock holding a large magnifying glass and a clipboard, inspecting. Four numbered inspection callouts (just the digits 1 to 4 in circles plus the labels): (1) a radio antenna badge on Nong Som's clipboard labeled kind-lab (which cluster kubectl talks to); (2) a bracket over the tower and both ships labeled 3 nodes Ready with green check marks; (3) a small row of tiny crew huts on the dock grouped under a sign kube-system (system Pods), drawn as small teal cabins on the dock, not on the ships; (4) a red no-entry sign on the control tower gate labeled NoSchedule, meaning normal cargo cannot be placed on the tower.
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 001 classroom illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Pod = rounded translucent teal cabin box that wraps one or more shipping containers and carries one small IP tag; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor control tower on the dock (lab-control-plane); image registry = warehouse of container blueprints; the lab container k8s-lab = one big rounded card / giant shipping container that holds everything of the lab.
Text (verbatim, at most 6 short labels): "k8s-lab"; "kind-lab"; "3 nodes Ready"; "kube-system"; "NoSchedule"; "lab-control-plane".
Constraints: only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos (no Docker whale, no GitHub octocat); do not show Service, NodePort, Deployment, ReplicaSet or Ingress objects or words. Exactly 1 control tower and 2 ships; the ship names may appear as small hull text lab-worker and lab-worker2 in addition to the labels above; no user Pod boxes on the ships.
```
