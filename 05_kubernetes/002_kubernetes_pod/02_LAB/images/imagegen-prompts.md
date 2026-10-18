Generated with built-in image_gen via cyolo1 using 00-character-som.png as character reference

# Final image prompts — 002 Kubernetes Pod (LAB)

ทุกภาพแนบ `01_Theory/images/00-character-som.png` เป็นภาพอ้างอิงตัวละครน้องส้ม

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

# LAB 0 step figures (added 2026-10-06, cyolo1 gpt-6-astra high, same character reference)

## 01-lab0-setup.png

> LAB0 ขั้นที่ 1 Setup: docker run → ssh -p 2223 → k8s-up (added 2026-10-18, Codex CLI image_gen, same character reference)

```text
Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai university DevTools course; must teach the concept correctly at a glance.
Asset type: landscape 3:2 educational story illustration for Thai Kubernetes Pod lesson (README figure, about 1536x1024).
Scene: One left-to-right setup flow in three numbered stages (digits 1, 2, 3 in small circles). Stage 1 (left): Nong Som at a student laptop; an arrow labeled docker run goes to a big rounded card / giant shipping container labeled k8s-lab, with one small door on its side; a small hourglass icon next to the card shows "wait a moment while it starts up" (no text on the hourglass). Stage 2 (middle): a glowing tunnel labeled ssh -p 2223 runs from the laptop into that side door of k8s-lab, with a small opened padlock icon (no text). Stage 3 (right, inside the k8s-lab card): a big button labeled k8s-up, and above it the harbor appears: exactly one harbor control tower and two cargo ships, with a bracket over all three labeled 3 nodes Ready and green check marks. No Pods yet.
Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly.
Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, white background, palette navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; matches the chapter 001 classroom illustration set. Shared metaphor (keep consistent across the series): container = colored shipping container box; Node = cargo ship; Control Plane = harbor control tower on the dock; the lab container k8s-lab = one big rounded card / giant shipping container that holds everything of the lab.
Text (verbatim, at most 5 short labels): "docker run"; "k8s-lab"; "ssh -p 2223"; "k8s-up"; "3 nodes Ready".
Constraints: only the verbatim labels listed above, spelled exactly, no other words, no gibberish or pseudo-text, no speech bubbles with text, no watermark, no signature, no real company logos (no Docker whale, no GitHub octocat); do not show Service, NodePort, Deployment, ReplicaSet or Ingress objects or words; do not write any password; exactly 1 control tower and 2 ships, no Pod boxes.
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

## 04b-lab3-vscode-ports.png

> LAB3 ขั้นที่ 4: ภาพจำลองหน้าจอ VS Code (attach เข้า container) แท็บ PORTS (updated 2026-10-18, Codex CLI image_gen)

```text
Use case: realistic software screenshot for a Thai university DevTools lab README; students must recognize the exact UI they will see.
Asset type: landscape 16:10 high-resolution realistic desktop screenshot (about 1600x1000), crisp UI text, looks like a real screen capture, NOT a cartoon.
Scene: A real-looking Visual Studio Code window, Dark Modern theme, attached to a running container. Bottom-left status bar shows the remote indicator with the text "Container tuchsanai/devtools-kind:2569_1 (k8s-lab)". Left Explorer sidebar shows folder 02_LAB with sub-folders images, labs, som-shop and file README.md. The editor area shows README.md open with a few faint markdown lines. The bottom panel is open with tabs PROBLEMS, OUTPUT, DEBUG CONSOLE, TERMINAL, PORTS; the PORTS tab is selected and shows a badge 1. The PORTS table has column headers Port, Forwarded Address, Running Process, Origin and exactly one row: Port 8080, Forwarded Address localhost:8080, Running Process kubectl port-forward pod/web 8080:80, Origin Auto Forwarded. The mouse cursor hovers that row, revealing the small globe icon next to the forwarded address, with its tooltip "Open in Browser" visible.
Annotation overlay (the only non-realistic part): a thick orange rounded rectangle around the PORTS tab and a thick orange circle around the globe icon, connected by a short orange arrow; in the lower-right corner a small sticker of Nong Som (the attached character reference, kept small, about 12% of image width) pointing at the globe icon.
Character sticker: Nong Som exactly as in the attached reference sheet 00-character-som.png — chubby orange tabby cat, white chest and muzzle, big green eyes, navy captain hat with white ship-wheel badge, teal neckerchief; appears exactly once, small, in the corner.
Text: all UI text must be real English VS Code labels spelled exactly as listed above; keep other text minimal or blurred; no gibberish.
Constraints: realistic flat UI rendering like an actual screenshot, no 3D, no cartoon editor, no watermark, no extra windows; exactly one row in the PORTS table; do not show passwords.
```

## 04a-lab3-vscode-attach.png

> LAB3 ขั้นที่ 0: ภาพจำลองหน้าจอ VS Code คลิกขวา container tuchsanai/devtools-kind:2569_1 (k8s-lab) → Attach Visual Studio Code ใช้ภาพจริงจากเอกสาร VS Code เป็นต้นแบบ UI (updated 2026-10-18, Codex CLI image_gen)

```text
Use case: realistic software screenshot for a Thai university DevTools lab README; students must recognize the exact UI they will see.
Asset type: landscape 16:10 high-resolution realistic desktop screenshot (about 1600x1000), crisp UI text, looks like a real screen capture, NOT a cartoon.
Reference: the second attached image is a REAL screenshot of the VS Code Container Tools sidebar; copy its exact look (fonts, colors, spacing, icons, section headers CONTAINERS / IMAGES / NETWORKS, context-menu style).
Scene: A full VS Code window on Windows, Dark Modern theme, no remote connected. The Activity Bar container-tools icon is selected; the side bar title reads CONTAINERS. The CONTAINERS section is expanded and contains exactly one running container item: a green play-triangle icon, the main label "tuchsanai/devtools-kind:2569_1" and, after it in dimmer grey text, the description "k8s-lab - Up 10 minutes". Below it the IMAGES section is collapsed. The user has RIGHT-CLICKED exactly on that container item (the row is highlighted) and its context menu is open next to it, styled like the reference, with items: View Logs, Attach Shell, Attach Visual Studio Code, Inspect, Open in Browser, Stop, Restart, Remove... ; the item "Attach Visual Studio Code" is highlighted in blue under the mouse cursor. The editor area on the right shows the VS Code Welcome page faintly.
Annotation overlay (the only non-realistic part): a thick orange rounded rectangle around the whole container row "tuchsanai/devtools-kind:2569_1 k8s-lab - Up 10 minutes" with a small orange label "1 คลิกขวา", and another thick orange rounded rectangle around "Attach Visual Studio Code" with a small orange label "2"; in the lower-right corner a small sticker of Nong Som (first attached image, kept small, about 12% of image width) pointing at the menu.
Character sticker: Nong Som exactly as in the first attached reference sheet — chubby orange tabby cat, white chest and muzzle, big green eyes, navy captain hat with white ship-wheel badge, teal neckerchief; appears exactly once, small, in the corner.
Text: UI text must be the real English labels spelled exactly as listed; no gibberish.
Constraints: realistic flat UI rendering like an actual screenshot, no 3D, no Docker whale logo, no watermark; exactly one container item.
```
