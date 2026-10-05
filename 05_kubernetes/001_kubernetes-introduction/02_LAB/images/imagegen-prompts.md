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

