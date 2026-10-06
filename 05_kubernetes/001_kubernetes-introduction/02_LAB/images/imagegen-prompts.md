# Final image prompts

Generated with built-in image_gen. These final prompts reflect tool verification only; no cluster or nodes are started.

## 01-environment-overview.png

```text
Use case: scientific-educational
Asset type: landscape illustration for a Thai student Kubernetes environment preparation README.
Primary request: Show a student's laptop on the left, running Docker. A simple arrow points to a large container card named k8s-lab on the right, containing a Kubernetes wheel icon and a toolkit labeled kubectl and kind. This is environment preparation only: installed tools ready for future labs, no cluster has been created.
Style/medium: clean flat educational infographic, white background, navy text, blue and teal shapes, rounded cards, restrained orange accents, crisp lines, large legible labels, generous whitespace, landscape 3:2 composition.
Text (verbatim): title "เตรียมเครื่องสำหรับ LAB"; laptop label "เครื่องนักศึกษา"; container title "k8s-lab"; toolkit labels "Kubernetes tools", "kubectl", "kind"; footer "พร้อมสำหรับทำ LAB".
Constraints: only these short labels. No node icons, no control plane, no workers, no cluster diagram, no Ready nodes, no pods, no cloud symbols, ports, terminal command output or watermark. Make installed tools distinct from running infrastructure.
```

## 02-build-then-run.png

```text
Use case: scientific-educational
Asset type: landscape illustration for a Thai student Kubernetes environment preparation README.
Primary request: A clear left-to-right two-step Docker workflow. Step 1 shows a Dockerfile becoming an image named devtools-kind:2569_1. A large arrow leads to step 2, where that image becomes a running container named k8s-lab. Convey Build image first, then Run container.
Style/medium: clean flat educational infographic, white background, navy text, blue and teal shapes, rounded cards, restrained orange accents, crisp lines, large legible labels, generous whitespace, landscape 3:2 composition. Match a consistent classroom illustration set.
Text (verbatim): title "เตรียม Container"; step titles "1  Build image", "2  Run container"; item labels "Dockerfile", "devtools-kind:2569_1", "k8s-lab".
Constraints: short exact text, obvious left-to-right arrow. No Compose, terminal commands, ports, cloud symbols, watermark, or detailed image layers.
```

## 03-kubectl-ready.png

```text
Use case: scientific-educational
Asset type: landscape illustration for a Thai student Kubernetes environment preparation README.
Primary request: Show one large terminal card labeled k8s-lab with exactly two command lines: kubectl version --client and kubectl --help. Beside it show a green check mark and a simple toolbox with Kubernetes wheel icon, indicating that the installed command-line tool works and is ready for future labs. This validates tools only; no cluster has been created.
Style/medium: clean flat educational infographic, white background, navy text, blue and teal shapes, rounded cards, restrained orange accents, crisp lines, large legible monospace terminal text, generous whitespace, landscape 3:2 composition. Match a consistent classroom illustration set.
Text (verbatim): title "ตรวจเครื่องมือ Kubernetes"; terminal label "k8s-lab"; terminal lines "kubectl version --client" and "kubectl --help"; check mark label "เครื่องมือพร้อม"; footer "พร้อมทำ LAB".
Constraints: no nodes, workers, control plane, cluster diagram, Ready status, kubectl get nodes, kubectl get pods, k8s-up, fabricated version output, networking, cloud symbols or watermark. Clearly show commands running inside k8s-lab.
```

# Cluster and node images (sections 4.2–4.5)

Generated 6 October 2569 with cyolo1 (gpt-6-astra, effort high) using built-in image_gen. Commands and results shown match the real run in readme.md. Images 05–07 were generated with `-i ref.png`, where ref.png is `../../01_Theory/images/03-cluster-architecture-overview.png` (theory Figure 3), so they reuse its harbor metaphor.

## 04-k8s-up-cluster.png

```text
Use case: scientific-educational
Asset type: landscape illustration for a Thai student Kubernetes lab README.
Primary request: Left: a terminal card labeled k8s-lab with one command line "k8s-up". A large arrow points right to a big rounded container card titled "k8s-lab" that contains a cluster box titled "cluster: lab". Inside the cluster box: one larger node card "lab-control-plane" with a steering wheel icon and role tag "control-plane", and two node cards "lab-worker" and "lab-worker2" with role tag "worker". Each of the three node cards has a small green "Ready" badge. Small note under the cluster: "แต่ละ node คือ container".
Style/medium: clean flat educational infographic, white background, navy text, blue and teal shapes, rounded cards, restrained orange accents, crisp lines, large legible labels and large legible monospace terminal text, generous whitespace, landscape 3:2 composition (1536x1024). Match a consistent classroom illustration set.
Text (verbatim): title "k8s-up สร้างคลัสเตอร์ 3 node"; terminal line "k8s-up"; labels exactly as above; footer "1 control-plane + 2 worker".
Constraints: only these short labels, spelled exactly. No pods, no cloud symbols, no ports, no IP addresses, no extra commands, no watermark.
```

## 05-which-cluster.png

```text
Use case: scientific-educational
Asset type: landscape illustration for a Thai student Kubernetes lab README.
Reference image: the attached ref.png is "รูปที่ 3 สถาปัตยกรรม Kubernetes Cluster" from the theory chapter. Reuse its visual language closely: harbor metaphor (control tower = Control Plane, cargo ships = worker nodes), blue Control Plane band, teal Worker Node band, same component chips, colors, Kubernetes wheel icon, cute flat style, harbor/sea background, bottom summary banner with a megaphone or wheel icon.
Primary request: Explain three commands that check which cluster kubectl is talking to. Left column: three dark terminal cards stacked vertically, each with a big blue number badge 1, 2, 3 and one monospace command:
 1 "kind get clusters"
 2 "kubectl config current-context"
 3 "kubectl cluster-info"
Right side: a harbor scene of the cluster (dashed box titled "cluster: lab") with a control tower labeled "Control Plane" holding chip "kube-apiserver", and a small chip "CoreDNS"; two small cargo ships in the teal band. Each command has a callout bubble with the same number badge, placed on the part of the scene it checks:
 1 on the dashed cluster box title: question "มีคลัสเตอร์อะไรบ้าง?" answer chip "lab"
 2 on a kubectl steering-wheel pointer aimed at the cluster: question "kubectl ใช้คลัสเตอร์ไหน?" answer chip "kind-lab"
 3 on the control tower: question "เชื่อมต่อได้ไหม?" answer chips "kube-apiserver" and "CoreDNS" with a green check mark
Bottom banner: "kind-lab = kind- + ชื่อคลัสเตอร์ lab".
Text (verbatim): title "ตรวจว่าเชื่อมต่อคลัสเตอร์ไหน"; all labels exactly as above.
Style/medium: clean flat educational infographic matching ref.png, 1536x1024 landscape, large legible labels, monospace for commands, generous whitespace.
Constraints: only these labels, spelled exactly. No URLs, ports, IP addresses, Pods, Cloud Provider, developer character, or watermark. Number badges must clearly pair each command with its callout; no crossing arrows.
```

## 06-count-nodes.png

```text
Use case: scientific-educational
Asset type: landscape illustration for a Thai student Kubernetes lab README.
Reference image: the attached ref.png is "รูปที่ 3 สถาปัตยกรรม Kubernetes Cluster" from the theory chapter. Reuse its visual language closely: harbor metaphor (control tower = Control Plane, cargo ships = worker nodes), blue Control Plane band, teal Worker Node band, same component chips, colors, Kubernetes wheel icon, cute flat style, harbor/sea background, bottom summary banner with a megaphone or wheel icon.
Primary request: Explain counting nodes in the lab cluster. Two horizontal panels.
Top panel titled "นับ node ทั้งหมด": left, a dark terminal card with monospace command "kubectl get nodes --no-headers | wc -l". Middle: the harbor scene in a row: one control tower labeled "lab-control-plane" and two cargo ships labeled "lab-worker" and "lab-worker2", each with a small green "Ready" badge and a small counting tag "1", "2", "3" above it. Right: a big result bubble "3".
Bottom panel titled "แยกตามบทบาท (label)": two terminal cards side by side.
 Left card (blue, control-plane color): command "kubectl get nodes -l node-role.kubernetes.io/control-plane --no-headers | wc -l", under it the control tower icon only, result bubble "1".
 Right card (teal, worker color): command "kubectl get nodes -l '!node-role.kubernetes.io/control-plane' --no-headers | wc -l", under it the two cargo ships only, result bubble "2", small note "! = ไม่มี label นี้".
Bottom banner: "3 node = 1 control-plane + 2 worker".
Text (verbatim): title "นับจำนวน node"; all labels and commands exactly as above.
Style/medium: clean flat educational infographic matching ref.png, 1536x1024 landscape, large legible labels, monospace for commands, generous whitespace.
Constraints: commands must be spelled exactly, in monospace, fully visible (may wrap onto two lines at a space). No Pods, IP addresses, Cloud Provider, developer character, Worker Node 3, or watermark.
```

## 07-kind-nodes-architecture.png

```text
Use case: scientific-educational
Asset type: landscape illustration for a Thai student Kubernetes lab README.
Reference image: the attached ref.png is "รูปที่ 3 สถาปัตยกรรม Kubernetes Cluster" from the theory chapter. Reuse its visual language closely: harbor metaphor (control tower = Control Plane, cargo ships = worker nodes), blue Control Plane band, teal Worker Node band, same component chips, colors, Kubernetes wheel icon, cute flat style, harbor/sea background, bottom summary banner with a megaphone or wheel icon.
The new image maps that architecture onto the REAL lab cluster that students just created.
Primary request:
- Left side: a dark terminal card titled "docker ps" showing exactly three monospace rows, each starting with a big round number badge: "① lab-control-plane", "② lab-worker", "③ lab-worker2", each followed by a small grey tag "kindest/node:v1.37.0". NO arrows from the terminal; pairing is done only by the number badges.
- Right side: a big dashed outer box titled "k8s-lab (Docker)" with subtitle "แต่ละ node = 1 container". Inside it a box titled "cluster: lab" containing:
  - Top (blue band, control tower): node card with number badge ① and title "lab-control-plane", role tag "control-plane", chips "kube-apiserver" (largest, center), "etcd" (database cylinder, two-way arrow to kube-apiserver), "kube-scheduler", "kube-controller-manager". Small grey line: "kubelet · kube-proxy · containerd".
  - Bottom (teal band): left cargo-ship card with badge ② "lab-worker" and right cargo-ship card with badge ③ "lab-worker2", role tag "worker", chips "kubelet", "kube-proxy", "container runtime", and an empty dashed slot "Pod (รอ deploy)".
  - One blue upward arrow from each worker card to kube-apiserver. No other arrows between workers.
  - Every node card has a small green "Ready" badge.
- Bottom banner: two bullets "3 node = 1 control-plane + 2 worker" and "ใน kind ทุก node คือ container ไม่ใช่เครื่องจริง".
Text (verbatim): title "คลัสเตอร์ lab เทียบกับสถาปัตยกรรม Kubernetes"; all labels exactly as listed.
Style/medium: clean flat educational infographic matching ref.png, 1536x1024 landscape, large legible labels, monospace for commands, generous whitespace.
Constraints: only these labels, spelled exactly. Do NOT draw Cloud Provider, cloud-controller-manager, a developer character, Worker Node 3, IP addresses, ports, or filled Pods. No watermark.
```
