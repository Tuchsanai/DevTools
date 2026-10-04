# Pre-check ก่อนวางแผนบท 004 (รันจริง 4 ต.ค. 2569)

ไม่ใช่การรัน LAB จริง เป็นการทดสอบสั้นเพื่อใช้ตัดสินใจออกแบบ LAB เท่านั้น

- container: `k8s-lab-netpol-db4877` (image `tuchsanai/devtools-kind:2569_1`, ID `8108a1bc7901`), `k8s-up` → kind `lab` 3 node, K8s v1.37.0 — **ลบแล้ว** (`docker rm -fv`)
- kindnet image: `docker.io/kindest/kindnetd:v20260820-69b56db7` (DaemonSet `kindnet` ใน kube-system)

## ผลที่ได้

| เรื่อง | ผลจริง |
|---|---|
| namespace เริ่มต้นของ kind | `default`, `kube-node-lease`, `kube-public`, `kube-system`, **`local-path-storage`** (ของ kind เอง ใช้กับ StorageClass `standard`) ทุกตัวมี label `kubernetes.io/metadata.name=<ชื่อ>` |
| `kube-public` | ไม่มี Pod มี ConfigMap `cluster-info`, `kube-root-ca.crt` |
| `kube-node-lease` | Lease 3 ตัว `lab-control-plane`, `lab-worker`, `lab-worker2` |
| `namespace default` spec | `{"finalizers":["kubernetes"]}` |
| `api-resources --namespaced=true` | 34 ชนิด; `--namespaced=false` มี namespaces, nodes, persistentvolumes, clusterroles, clusterrolebindings, storageclasses, priorityclasses, csidrivers, ingressclasses, runtimeclasses ฯลฯ |
| Pod ข้าม namespace ด้วย Pod IP | ได้ (`team-b/client` → `team-a/web` 10.244.1.2 ได้หน้า nginx) |
| **NetworkPolicy บน kindnet** | **บังคับใช้จริง**: policy `podSelector: {}` + ingress from `podSelector: {}` ใน team-a → จาก team-b `wget: download timed out` (exit 1), จาก team-a เองยังได้; เพิ่ม policy `namespaceSelector: {matchLabels: {kubernetes.io/metadata.name: team-b}}` → team-b กลับมาเข้าได้ (มีผลภายใน 5 วินาที) |
| PSA restricted (label หลังมี Pod อยู่แล้ว) | `Warning: existing pods in namespace "team-b" violate the new PodSecurity enforce level "restricted:latest"` / `Warning: client: allowPrivilegeEscalation != false, unrestricted capabilities, runAsNonRoot != true, seccompProfile` แต่ Pod เดิมยังรัน |
| PSA restricted (สร้างใหม่) | `Error from server (Forbidden): pods "bad" is forbidden: violates PodSecurity "restricted:latest": allowPrivilegeEscalation != false (container "bad" must set securityContext.allowPrivilegeEscalation=false), unrestricted capabilities (container "bad" must set securityContext.capabilities.drop=["ALL"]), runAsNonRoot != true (pod or container "bad" must set securityContext.runAsNonRoot=true), seccompProfile (pod or container "bad" must set securityContext.seccompProfile.type to "RuntimeDefault" or "Localhost")` |
| **postgres:17.11-alpine ภายใต้ restricted** | **รันได้** ด้วย pod `runAsNonRoot: true, runAsUser: 70, runAsGroup: 70, fsGroup: 70, seccompProfile RuntimeDefault` + container `allowPrivilegeEscalation: false, capabilities.drop [ALL]`, PGDATA บน emptyDir → initdb ผ่าน, `PostgreSQL 17.11`, `id` = `uid=70(postgres)` |
| ResourceQuota (requests.cpu) Pod ไม่มี requests | `Error from server (Forbidden): pods "q1" is forbidden: failed quota: q: must specify requests.cpu for: q1` |
| ResourceQuota เกินจำนวน pods | `Error from server (Forbidden): pods "c" is forbidden: exceeded quota: q, requested: pods=1, used: pods=2, limited: pods=2` |
| LimitRange default | Pod ไม่ใส่ resources ได้ `{"limits":{"cpu":"200m","memory":"128Mi"},"requests":{"cpu":"100m","memory":"64Mi"}}` + annotation `kubernetes.io/limit-ranger: LimitRanger plugin set: cpu, memory request for container a; cpu, memory limit for container a` |
| LimitRange max | `Error from server (Forbidden): pods "big" is forbidden: maximum cpu usage per Container is 500m, but limit is 1` |
| RBAC `--as` | `can-i list pods -n team-a` → `yes`, `delete` → `no`, ns อื่น → `no`; `Error from server (Forbidden): pods "web" is forbidden: User "system:serviceaccount:team-a:intern" cannot delete resource "pods" in API group "" in the namespace "team-a"` |
| **`kubectl --token=<SA token>` กับ kubeconfig ของ kind** | **ไม่ได้เปลี่ยนตัวตน** — ยังเป็น admin (ดู ns อื่นได้) เพราะ kubeconfig ของ kind ใช้ client certificate ซึ่งถูกใช้ยืนยันตัวตนก่อน → ต้องสร้าง user/context แยกที่มีแต่ token: `kubectl config set-credentials intern --token=$T` + `kubectl config set-context intern-ctx --cluster=kind-lab --user=intern --namespace=...` แล้ว `kubectl --context intern-ctx ...` (ทดสอบผ่าน: ns ตัวเองได้ `No resources found`, ns อื่น Forbidden) |
| `kubectl auth whoami` ผ่าน context intern | `Username system:serviceaccount:t2:intern`, Groups `[system:serviceaccounts system:serviceaccounts:t2 system:authenticated]` |
| ลบ namespace | `namespace "team-a" deleted` → `STATUS Terminating` (ทันที) → หายภายใน < 60 วินาที (Pod nginx/busybox 3 ตัว) |

## สิ่งที่ยังไม่ได้ทดสอบ (ต้องยืนยันตอนรัน LAB จริง)

- `som-shop-web:1.0` (Dockerfile `USER node` เป็นชื่อ ไม่ใช่เลข) ภายใต้ `runAsNonRoot: true` ต้องใส่ `runAsUser: 1000` มิฉะนั้นคาดว่าได้ `CreateContainerConfigError` (`container has runAsNonRoot and image has non-numeric user (node), cannot verify user is non-root`)
- som-shop ทั้ง Pod (sidecar + init) ภายใต้ restricted + quota + LimitRange ของ som-prod
- ข้อความ error ของ `metadata.namespace` ไม่ตรงกับ `-n`, เวลา Terminating ของ som-dev ที่มี postgres, token ของ SA หลังลบ namespace
