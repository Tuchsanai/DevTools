#!/bin/bash
# สร้างรูปประกอบ readme ของ 01_Reference ผ่าน cyolo1 (built-in image_gen) ทีละ 2 รูปพร้อมกัน
set -u
OUT=/root/workspace/DevTools/k/001_kubernetes-introduction/02_LAB/00_Reference/01_Reference/images
LOG=/root/workspace/DevTools/k/001_kubernetes-introduction/logs/01_Reference/images
mkdir -p "$OUT" "$LOG"
cd "$LOG"

STYLE='Style: clean modern flat-vector educational infographic for Thai university students, 16:9 landscape (1536x1024), white background, soft blue/teal/orange palette, rounded boxes, clear arrows, numbered steps, friendly small mascot whale (Docker) and ship-wheel (Kubernetes) icons. All main labels in Thai with short English technical terms in parentheses, large readable font, correct spelling, no tiny text, no watermark. Exact names/ports given below must appear exactly as written.'

declare -A P
P[01-lab-big-picture]="Title: \"ภาพรวม LAB: Kubernetes ทั้งคลัสเตอร์ในกล่องเดียว\". Show nested boxes like Russian dolls from outside to inside: (1) \"เครื่องของเรา (Host / Laptop)\" with Docker Desktop, (2) container \"k8s-lab\" (image devtools-kind:2569_1) containing SSH :22, JupyterLab :8888 and \"dockerd (Docker-in-Docker)\", (3) inside dockerd three node containers \"lab-control-plane\", \"lab-worker\", \"lab-worker2\" built by \"kind\", (4) small Pods inside workers. Side arrows from Host: \"ssh -p 2223\", \"http://localhost:8889\", \"http://localhost:30080\" pointing into k8s-lab. Caption: \"ทุกอย่างอยู่ใน container เดียว ลบทิ้งแล้วเริ่มใหม่ได้เสมอ\"."
P[02-what-is-kind]="Title: \"kind = Kubernetes IN Docker\". Left side \"คลัสเตอร์จริง\": three physical servers / VMs each labeled Node with kubelet + container runtime, cost and setup time icons (slow, expensive). Right side \"kind\": one Docker engine with three containers, each container IS a Node (label \"Node = Docker container\"), inside each: kubelet, containerd, and Pods. Middle comparison arrow \"เหมือนกันในมุม Kubernetes\". Bottom bullet badges: \"สร้างคลัสเตอร์ใน ~1 นาที\", \"ใช้ทดลอง/สอน/CI\", \"ลบทิ้งด้วยคำสั่งเดียว\"."
P[03-build-and-run]="Title: \"จาก Dockerfile สู่ container k8s-lab\". Left-to-right pipeline with numbered steps: 1 folder \"01_Reference/\" with files Dockerfile, start.sh, docker-compose.yml, kind-lab.yaml; 2 command \"docker compose up -d --build\"; 3 image box \"devtools-kind:2569_1\" listing layers: Ubuntu 24.04, Docker-in-Docker, Python+Node.js, JupyterLab, kind, kubectl, helm, k9s; 4 running container \"k8s-lab\" with port badges \"2223 → 22 SSH\", \"8889 → 8888 JupyterLab\", \"30080-30082 → NodePort\" and a volume cylinder \"k8s-lab-dind → /var/lib/docker\"."
P[04-kind-create-cluster]="Title: \"k8s-up: kind create cluster ทำอะไรบ้าง?\". Vertical/zigzag timeline of 6 numbered steps with icons: 1 \"รอ dockerd พร้อม\", 2 \"ดึง image kindest/node\", 3 \"สร้าง node containers: lab-control-plane, lab-worker, lab-worker2\", 4 \"kubeadm init / join (ตั้งค่า control plane + ต่อ worker)\", 5 \"ติดตั้ง CNI kindnet + StorageClass\", 6 \"เขียน ~/.kube/config (context: kind-lab)\". Final badge: \"kubectl get nodes → 3 Ready\" with green check marks."
P[05-kubectl-kubeconfig]="Title: \"kubectl คุยกับคลัสเตอร์ได้อย่างไร\". Left: student terminal inside container k8s-lab typing \"kubectl get pods\". Arrow to a document icon \"~/.kube/config\" showing fields: cluster server https://127.0.0.1:<port>, user certificate, context kind-lab. Arrow (HTTPS) to \"kube-apiserver\" inside container \"lab-control-plane\" which also shows etcd, scheduler, controller-manager. API server then talks to kubelet on \"lab-worker\" and \"lab-worker2\". Caption: \"kubeconfig = ที่อยู่ + กุญแจ + ชื่อคลัสเตอร์\"."
P[06-multi-node-scheduling]="Title: \"คลัสเตอร์ 3 Node: ใครทำหน้าที่อะไร\". One big box \"lab-control-plane\" (สมองของคลัสเตอร์: API server, etcd, scheduler, controller-manager) at the top, two boxes \"lab-worker\" and \"lab-worker2\" below (แรงงาน: kubelet, kube-proxy, containerd). Show command \"kubectl create deployment web --image=nginx --replicas=4\" and the scheduler distributing 4 nginx Pods: 2 to lab-worker and 2 to lab-worker2, with dashed arrows labeled \"Scheduler เลือก Node\". Caption: \"Pod ถูกกระจายไปยัง worker อัตโนมัติ\"."
P[07-deploy-first-app]="Title: \"Deploy แอปแรก: Deployment → ReplicaSet → Pod → Service\". Left-to-right story with 4 stages: 1 YAML file icon \"web.yaml\" + \"kubectl apply -f web.yaml\", 2 \"Deployment web (replicas: 3)\" creating \"ReplicaSet\", 3 three \"Pod nginx\" boxes with IP labels like 10.244.1.5, 10.244.2.7, 4 \"Service web (NodePort 30080)\" acting as one stable door in front of the Pods with load-balancing arrows. A small inset shows one Pod crossed out and a new Pod appearing: \"Pod ตาย → สร้างใหม่ให้อัตโนมัติ (self-healing)\"."
P[08-nodeport-path]="Title: \"เส้นทางของ request: เบราว์เซอร์ → Pod\". Numbered horizontal path of hops: 1 browser on Host \"http://localhost:30080\", 2 \"docker -p 30080:30080\" into container \"k8s-lab\", 3 kind \"extraPortMappings 30080\" into node container \"lab-control-plane\", 4 \"Service NodePort 30080 / kube-proxy\", 5 load balanced to one of the \"Pod nginx\" on lab-worker or lab-worker2, response arrow back \"200 OK\". Use a winding road/pipe metaphor with checkpoints. Caption: \"ต้องเปิดพอร์ตครบทุกชั้น request ถึงจะเข้าไปถึง Pod\"."
P[09-kind-load-image]="Title: \"ใช้ image ที่ build เอง: kind load docker-image\". Story in 4 steps: 1 \"docker build -t myapp:1.0 .\" inside k8s-lab creates image in dockerd (Docker-in-Docker), 2 a red X with note \"node ของ kind ใช้ containerd ของตัวเอง มองไม่เห็น image นี้\", 3 command \"kind load docker-image myapp:1.0 --name lab\" copying the image box into containerd of lab-control-plane, lab-worker, lab-worker2, 4 Pod running \"myapp:1.0\" with label \"imagePullPolicy: IfNotPresent\". Green check at the end."
P[10-lifecycle-cleanup]="Title: \"วงจรชีวิตของ LAB: เริ่ม-ใช้-ล้าง\". Circular cycle diagram with 5 stations: 1 \"docker compose up -d --build (สร้าง k8s-lab)\", 2 \"k8s-up (สร้างคลัสเตอร์ lab)\", 3 \"kubectl apply / ทดลอง\", 4 \"k8s-down (kind delete cluster)\", 5 \"docker compose down (หยุด container)\". Side panel \"อะไรยังอยู่ อะไรหาย\": ./workspace = ยังอยู่ (green), volume k8s-lab-dind = ยังอยู่ จนกว่าจะ docker compose down -v (orange), คลัสเตอร์หลัง k8s-down = หาย (red)."

gen() {
  local key=$1
  local prompt="Use your built-in image generation tool (image_gen) to create exactly ONE image. Do NOT draw it with code, PIL, SVG or HTML. ${STYLE} Content: ${P[$key]} After the image is generated, copy the generated PNG file (it is saved under \$CODEX_HOME/generated_images/) to ${OUT}/${key}.png using a shell command, verify the file exists and is a PNG, then reply with only the saved path."
  echo "[$(date +%T)] start $key"
  cyolo1 exec --skip-git-repo-check -m gpt-6-astra -c model_reasoning_effort="high" --json -o "$key.out" "$prompt" </dev/null > "$key.jsonl" 2> "$key.err"
  if grep -q '"turn.failed"' "$key.jsonl" || [ ! -s "$OUT/$key.png" ]; then
    echo "[$(date +%T)] FAIL $key"
  else
    echo "[$(date +%T)] ok   $key"
  fi
}

KEYS=(01-lab-big-picture 02-what-is-kind 03-build-and-run 04-kind-create-cluster 05-kubectl-kubeconfig 06-multi-node-scheduling 07-deploy-first-app 08-nodeport-path 09-kind-load-image 10-lifecycle-cleanup)
for ((i=0; i<${#KEYS[@]}; i+=2)); do
  gen "${KEYS[$i]}" &
  [ -n "${KEYS[$((i+1))]:-}" ] && gen "${KEYS[$((i+1))]}" &
  wait
done
echo "[$(date +%T)] all done"
