
## 16. สรุปและคำถามทบทวน

{{FIG:T38|สรุปบทที่ 4}}

### 16.1 สรุป

1. **Namespace** คือการแบ่งคลัสเตอร์ทางทะเบียน เป็นขอบเขตของชื่อ (`namespace/name`) และหน่วยที่ใช้แนบนโยบาย **ไม่ใช่** Node, VM หรือกำแพงเครือข่าย Pod ของโซนเดียวกระจายหลายเรือได้ และเรือลำเดียวรับหลายโซนได้
2. kind มี namespace ตั้งต้น 5 ตัว: `default`, `kube-system`, `kube-public`, `kube-node-lease` และ `local-path-storage` (ของ kind) ทุก namespace ได้ label `kubernetes.io/metadata.name`, ServiceAccount `default` และ ConfigMap `kube-root-ca.crt` อัตโนมัติ
3. resource แบ่งเป็น **namespaced** (34 ชนิดใน v1.37) และ **cluster-scoped** (37 ชนิด) ดูได้จาก `kubectl api-resources` และ `-n` ไม่มีผลกับ cluster-scoped
4. namespace ของ object มาจาก `metadata.namespace` หรือ `-n` หรือ context ตามลำดับ ถ้าไฟล์กับ `-n` ไม่ตรงกันได้ error ไฟล์ที่ใช้หลาย environment จึงไม่ควรใส่ `metadata.namespace`
5. context ใน kubeconfig จับคู่ cluster + user + namespace เปลี่ยน namespace เริ่มต้นได้ด้วย `kubectl config set-context --current --namespace=...` แต่ต้องระวังลืมคืนค่า
6. `kubectl delete ns` ลบทุกอย่างข้างใน ผ่านสถานะ `Terminating` และ finalizer `kubernetes` ระหว่างนั้นสร้างของใหม่ไม่ได้ ระบบป้องกันการลบเฉพาะ `default`, `kube-system`, `kube-public` (`kube-node-lease` ลบได้แต่ห้ามลบ)
7. Pod ต่าง namespace คุยกันด้วย Pod IP ได้ทันที ชื่อ DNS สั้นหาได้เฉพาะในโซนตัวเองเพราะ search domain ขึ้นต้นด้วย `<ns>.svc.cluster.local`
8. **NetworkPolicy** (ต้องมี CNI ที่รองรับ kindnet รองรับ) ทำให้ Pod ที่ถูกเลือก "ปฏิเสธทุกอย่างยกเว้นที่อนุญาต" policy รวมกันแบบ OR และอ้าง namespace ด้วย `namespaceSelector` + `kubernetes.io/metadata.name`
9. **ResourceQuota** คุมงบรวมของโซน **LimitRange** คุมขนาดต่อกล่องและเติมค่าตั้งต้น ทั้งสองตรวจตอนสร้าง Pod โดย LimitRange ทำงานก่อน quota
10. **RBAC**: Role + RoleBinding = สิทธิ์ในโซนเดียว, ClusterRole + RoleBinding = กฎมาตรฐานในโซนเดียว, ClusterRoleBinding = ทั้งคลัสเตอร์ ตรวจด้วย `kubectl auth can-i --as` และใช้ token ของ ServiceAccount ผ่าน context ใหม่ (ไม่ใช่ `--token` บน kubeconfig ที่มี client certificate)
11. **Pod Security Admission** ใช้ label `pod-security.kubernetes.io/<enforce|warn|audit>` กับระดับ `privileged`/`baseline`/`restricted` ตรวจตอนสร้าง Pod เท่านั้น ผ่าน restricted ด้วย `runAsNonRoot` + `runAsUser` ตัวเลข, `allowPrivilegeEscalation: false`, `drop: ["ALL"]`, `seccompProfile: RuntimeDefault`

**ตารางที่ 7** สรุปคำสั่งที่ใช้ในบทนี้

| คำสั่ง | ใช้ทำอะไร |
|---|---|
| `kubectl get ns --show-labels` | ดู namespace ทั้งหมดพร้อม label |
| `kubectl create namespace <ns>` / `kubectl apply -f ns.yaml` | สร้าง namespace |
| `kubectl get pods -n <ns>` / `-A` | ดู Pod ในโซนเดียว / ทุกโซน |
| `kubectl get pods -A --field-selector metadata.name=<ชื่อ>` | หา object ชื่อเดียวกันข้ามทุกโซน |
| `kubectl api-resources --namespaced=true\|false` | แยกชนิด namespaced / cluster-scoped |
| `kubectl config get-contexts` | ดู context และ namespace เริ่มต้น |
| `kubectl config set-context --current --namespace=<ns>` | เปลี่ยน namespace เริ่มต้นของ context |
| `kubectl get ns -l team=som -L env` | ค้น namespace ด้วย label และแสดง label เป็นคอลัมน์ |
| `kubectl describe ns <ns>` | ดู label, quota และ LimitRange ของโซน |
| `kubectl delete ns <ns>` | ลบโซนทั้งก้อน |
| `kubectl describe quota -n <ns>` / `kubectl describe limitrange -n <ns>` | ดูงบ Used/Hard / กฎขนาดกล่อง |
| `kubectl get netpol -n <ns>` / `kubectl describe netpol -n <ns>` | ดู NetworkPolicy |
| `kubectl auth whoami` | ดูว่าเราเป็นใคร |
| `kubectl auth can-i <verb> <resource> -n <ns> --as=<subject>` | ตรวจสิทธิ์ |
| `kubectl create token <sa> -n <ns> --duration=1h` | ขอ token อายุสั้นของ ServiceAccount |
| `kubectl config set-credentials` / `set-context` / `delete-context` / `delete-user` | จัดการ user/context ใน kubeconfig |
| `kubectl label --dry-run=server --overwrite ns <ns> pod-security.kubernetes.io/enforce=restricted` | ลองเปลี่ยนระดับ PSA ก่อนบังคับจริง |

**ตารางที่ 8** เทียบนโยบาย 5 ชนิดที่แนบกับ namespace

| นโยบาย | ควบคุมอะไร | ตรวจเมื่อไร | ผลเมื่อผิด (ข้อความจริง) |
|---|---|---|---|
| NetworkPolicy | ใครเชื่อมต่อเครือข่ายถึง Pod ได้ | ทุก packet (โดย CNI) | packet ถูกทิ้ง `wget: download timed out` |
| ResourceQuota | งบรวม requests/limits และจำนวน object ของโซน | ตอนสร้าง/แก้ไข object | `exceeded quota: ...` / `must specify ...` |
| LimitRange | ขนาดต่อ container/Pod/PVC และค่าตั้งต้น | ตอนสร้าง/แก้ไข Pod (ก่อน quota) | `maximum cpu usage per Container is 500m, but limit is 1` |
| RBAC | ใครเรียก API อะไรได้ | ทุกคำขอ API | `User "..." cannot delete resource "pods" ...` |
| Pod Security Admission | การตั้งค่าความปลอดภัยของ Pod | ตอนสร้าง Pod | `violates PodSecurity "restricted:latest": ...` |

> **ข้อควรจำก่อนเข้า LAB**
> - ทุก LAB ทำใน namespace ของตัวเอง **ไม่ทิ้งของไว้ใน `default`** และจบด้วยการเก็บกวาดด้วย `kubectl delete ns ...`
> - หลัง LAB 2 ต้อง **คืน namespace ของ context เป็น `default`** และตรวจด้วย `kubectl config get-contexts` ทุกครั้งที่ผลดูแปลก
> - ห้ามลองลบ `kube-node-lease`, `kube-system` หรือ `local-path-storage` จริง (ใช้ `--dry-run=server` เท่านั้น)
> - context/user ของ intern ที่สร้างใน LAB 7 และ LAB สุดท้ายต้องลบออกจาก kubeconfig ตอนเก็บกวาด
> - IP, AGE, เวลา และ Node ที่ Pod ถูกวางในเครื่องผู้เรียนอาจต่างจากเอกสาร

### 16.2 คำถามทบทวน

**1. นักศึกษาคนหนึ่งบอกว่า "namespace `team-a` อยู่บนเครื่อง lab-worker ส่วน `team-b` อยู่บน lab-worker2" ข้อความนี้ผิดอย่างไร และจะพิสูจน์ด้วยคำสั่งอะไร**

<details>
<summary>แนวคำตอบ</summary>

namespace เป็นการแบ่งทางทะเบียน ไม่ได้ผูกกับ Node Pod ของ namespace เดียวกันอยู่หลาย Node ได้ และ Node เดียวรับ Pod จากหลาย namespace ได้ (Node เป็น cluster-scoped) พิสูจน์ด้วย `kubectl get pods -A -o wide` ดูคอลัมน์ NAMESPACE คู่กับ NODE เช่นใน LAB 4 ที่ Pod ของ `team-a` และ `team-b` อยู่บน `lab-worker` ทั้งหมด และใน LAB 1 ที่ `snack` ของ 3 namespace อยู่บน 2 Node ปนกัน
</details>

**2. ทำไม `kubectl get nodes -n blue` จึงได้ผลเหมือนไม่ใส่ `-n` แต่ `kubectl get pods -n blue` ได้เฉพาะ Pod ของ blue**

<details>
<summary>แนวคำตอบ</summary>

Node เป็น resource แบบ cluster-scoped ไม่อยู่ใน namespace ใด kubectl จึงไม่ใช้ค่า `-n` ในการเรียก API (ไม่ error แต่ไม่กรอง) ส่วน Pod เป็น namespaced จึงถูกกรองตาม namespace ตรวจ scope ได้จากคอลัมน์ `NAMESPACED` ของ `kubectl api-resources`
</details>

**3. ไฟล์ `app.yaml` มี `metadata.namespace: green` เมื่อสั่ง `kubectl apply -f app.yaml -n blue` จะเกิดอะไรขึ้น และถ้าต้องการใช้ไฟล์เดียวกับทั้ง dev/staging/prod ควรเขียนไฟล์อย่างไร**

<details>
<summary>แนวคำตอบ</summary>

kubectl ปฏิเสธด้วย `error: the namespace from the provided object "green" does not match the namespace "blue". You must pass '--namespace=green' to perform this operation.` และไม่สร้างอะไร ไฟล์ที่ใช้หลาย environment ไม่ควรใส่ `metadata.namespace` แล้วเลือกปลายทางด้วย `-n` ตอนสั่ง เช่น `kubectl apply -f som-shop.yaml -n som-prod`
</details>

**4. `kubectl create -f snack-pod.yaml -n blue` กับ `kubectl apply -f snack-pod.yaml -n blue` ให้ผลต่างกันอย่างไรเมื่อมี `blue/snack` อยู่แล้ว**

<details>
<summary>แนวคำตอบ</summary>

`create` ต้องการสร้างใหม่ จึงได้ `Error from server (AlreadyExists): ... pods "snack" already exists` ส่วน `apply` ต้องการให้ object ตรงกับไฟล์ เมื่อตรงอยู่แล้วตอบ `pod/snack unchanged` (ถ้าไฟล์ต่าง จะพยายามแก้ object เดิม ไม่สร้างตัวที่สอง) ทั้งสองแบบไม่ทำให้มี Pod ชื่อซ้ำใน namespace เดียวกัน
</details>

**5. หลังสั่ง `kubectl config set-context --current --namespace=blue` แล้วปิด terminal เปิดใหม่ คำสั่ง `kubectl delete pod snack` จะลบ Pod ใน namespace ไหน เพราะอะไร และควรป้องกันอย่างไร**

<details>
<summary>แนวคำตอบ</summary>

ลบ `blue/snack` เพราะค่าถูกเขียนลงไฟล์ kubeconfig (`~/.kube/config`) ซึ่งคงอยู่ข้าม terminal จนกว่าจะเปลี่ยนกลับ ป้องกันโดยตรวจ `kubectl config get-contexts` (คอลัมน์ NAMESPACE) ก่อนคำสั่งอันตราย ใส่ `-n` ชัดเจนเสมอกับ namespace สำคัญและในสคริปต์ และคืนค่าด้วย `--namespace=default` เมื่อเลิกใช้
</details>

**6. อธิบายลำดับเหตุการณ์ตั้งแต่ `kubectl delete ns doomed` จน namespace หายไป และทำไมช่วงนั้นจึงสร้าง Pod ใหม่ใน `doomed` ไม่ได้**

<details>
<summary>แนวคำตอบ</summary>

API server ตั้ง deletionTimestamp และ `status.phase` เป็น `Terminating` ทันที namespace controller ไล่ลบ object ทุกชนิดข้างใน (Pod รอ grace period ของตัวเอง ใน LAB 9 คือ 15 วินาที) เมื่อว่างแล้วจึงเอา finalizer `kubernetes` ออกจาก `spec.finalizers` แล้ว Namespace object ก็หายไป (ผลจริง ~20 วินาที) ระหว่าง Terminating API server ปฏิเสธการสร้างของใหม่ด้วย `unable to create new content in namespace doomed because it is being terminated` เพื่อไม่ให้มีของงอกใหม่ระหว่างกำลังเก็บกวาด ซึ่งจะทำให้ลบไม่จบ
</details>

**7. namespace ใดบ้างที่ระบบป้องกันการลบ และทำไม `kube-node-lease` แม้ลบได้ก็ไม่ควรลบ**

<details>
<summary>แนวคำตอบ</summary>

ระบบป้องกัน `default`, `kube-system`, `kube-public` (`this namespace may not be deleted`) ส่วน `kube-node-lease` ผ่าน `--dry-run=server` แปลว่าลบได้จริง แต่เป็นที่เก็บ Lease ซึ่ง kubelet ทุกเรือต่ออายุเป็น heartbeat ทุก ~10 วินาที ถ้าลบ ระบบตรวจสุขภาพ Node จะสะดุด เป็นข้อห้ามตามธรรมเนียมที่ API ไม่ได้บังคับ เช่นเดียวกับการตั้งชื่อขึ้นต้น `kube-`
</details>

**8. Pod `client` ใน `team-b` เรียกชื่อ `web` แต่ไม่พบ ทั้งที่มี Service ชื่อ `web` อยู่ใน `team-a` อธิบายจาก `/etc/resolv.conf` และบอกชื่อที่ควรใช้**

<details>
<summary>แนวคำตอบ</summary>

`resolv.conf` ของ Pod ใน team-b มี `search team-b.svc.cluster.local svc.cluster.local cluster.local` ชื่อสั้น `web` จึงถูกค้นเป็น `web.team-b.svc.cluster.local` ก่อน ซึ่งไม่มี ต้องเรียกด้วย `web.team-a` หรือชื่อเต็ม `web.team-a.svc.cluster.local` (การเรียกด้วย Pod IP ตรง ๆ ใช้ได้เสมอถ้าไม่มี NetworkPolicy กั้น)
</details>

**9. ใน LAB 4 หลัง apply `allow-same-namespace` และ `allow-from-team-b` แล้ว ทำไม `team-b/client` จึงเข้า `team-a/web` ได้ แต่เข้า `team-a/client` ไม่ได้ และ `blue/snack` เข้าอะไรใน team-a ไม่ได้เลย**

<details>
<summary>แนวคำตอบ</summary>

`allow-same-namespace` เลือกทุก Pod ใน team-a (`podSelector: {}`) ทำให้ทุกตัวปฏิเสธขาเข้ายกเว้นจาก Pod ใน team-a เอง ส่วน `allow-from-team-b` เลือกเฉพาะ `app=web` และอนุญาตจาก namespace ที่มี `kubernetes.io/metadata.name=team-b` policy รวมกันแบบ OR ดังนั้น `web` รับได้ทั้งจาก team-a และ team-b แต่ `client` ของ team-a ถูกเลือกโดย policy แรกเท่านั้นจึงรับแค่จาก team-a ส่วน `blue` ไม่ตรง policy ใดเลย
</details>

**10. namespace `budget` มี quota `pods: 3, requests.cpu: 500m` Pod ที่ไม่ระบุ resources เลยจะเกิดอะไรขึ้น และถ้าเพิ่ม LimitRange (`defaultRequest` 100m/64Mi, `default` 200m/128Mi) ผลจะเปลี่ยนอย่างไร**

<details>
<summary>แนวคำตอบ</summary>

ไม่มี LimitRange: ถูกปฏิเสธ `failed quota: ... must specify ...` เพราะ quota คำนวณงบไม่ได้ เมื่อมี LimitRange: LimitRanger ทำงานก่อน quota เติม requests 100m/64Mi และ limits 200m/128Mi ให้ (พร้อม annotation `kubernetes.io/limit-ranger`) แล้ว quota จึงคำนวณได้ Pod สร้างได้ถ้ายังไม่เกินงบ
</details>

**11. ร้าน `som-shop` มี sidecar `db` (req 100m/256Mi), init `wait-for-db` (10m/16Mi), init `db-seed` (50m/64Mi) และ `web` (100m/192Mi) quota จะนับ requests ของ Pod นี้เท่าไร เพราะอะไร**

<details>
<summary>แนวคำตอบ</summary>

นับค่าสูงสุดของช่วงเวลาที่รันพร้อมกัน: ช่วง wait-for-db = db + wait = 110m/272Mi, ช่วง db-seed = db + seed = 150m/320Mi, ช่วงร้านเปิด = db + web = 200m/448Mi ค่าสูงสุดคือ **200m/448Mi** ตรงกับ Used ที่เห็นจริงใน `som-prod` (limits คิดแบบเดียวกันได้ 1 CPU/1Gi)
</details>

**12. RoleBinding ที่อ้าง ClusterRole `view` ใน namespace `team-b` ทำให้ `auditor` ทำอะไรได้บ้าง และต่างจาก ClusterRoleBinding ที่อ้าง `view` อย่างไร**

<details>
<summary>แนวคำตอบ</summary>

RoleBinding ทำให้กฎของ ClusterRole `view` มีผลเฉพาะ `team-b` auditor จึงอ่าน Pod, ConfigMap ฯลฯ ใน team-b ได้ แต่อ่าน Secret ไม่ได้ (view ไม่รวม Secret) ลบไม่ได้ และดู namespace อื่นไม่ได้ (ผลจริง LAB 7) ถ้าใช้ ClusterRoleBinding auditor จะอ่านได้ **ทุก namespace** ซึ่งเกินความจำเป็นและเสี่ยง
</details>

**13. ทำไม `kubectl --token=$T get pods -n team-b` ด้วย token ของ intern จึงยังเห็น Pod ของ team-b และวิธีที่ถูกต้องในการทดสอบสิทธิ์ของ intern คืออะไร (บอกได้ 2 วิธี)**

<details>
<summary>แนวคำตอบ</summary>

kubeconfig ของ kind ใช้ user ที่มี client certificate kubectl จึงยังส่ง certificate และ API server ยืนยันตัวตนเป็น `kubernetes-admin` จาก certificate ได้ก่อน (`kubectl --token=$T auth whoami` ยังได้ kubernetes-admin) วิธีที่ถูก: (1) ใช้ `kubectl auth can-i ... --as=system:serviceaccount:team-a:intern` หรือสั่งคำสั่งจริงด้วย `--as` (2) สร้าง user ที่มีแต่ token ด้วย `kubectl config set-credentials intern --token=$T` และ context ใหม่ `kubectl config set-context intern@lab --cluster=kind-lab --user=intern --namespace=team-a` แล้วใช้ `kubectl --context intern@lab ...`
</details>

**14. namespace `secure` เดิมเป็น `enforce=baseline` และมี Pod nginx ที่รันเป็น root อยู่ ถ้าเปลี่ยนเป็น `enforce=restricted` จะเกิดอะไรกับ Pod เดิมและ Pod ใหม่ และควรทำอะไรก่อนเปลี่ยนจริง**

<details>
<summary>แนวคำตอบ</summary>

PSA ตรวจเฉพาะตอนสร้าง Pod เดิมจึงยัง Running แต่ kubectl แสดงคำเตือน `existing pods in namespace "secure" violate the new PodSecurity enforce level "restricted:latest"` ส่วน Pod ใหม่แบบเดียวกันจะถูกปฏิเสธ `violates PodSecurity "restricted:latest": ...` ก่อนเปลี่ยนจริงควรรัน `kubectl label --dry-run=server --overwrite ns secure pod-security.kubernetes.io/enforce=restricted` เพื่อดูว่า Pod ใดจะผิด หรือเริ่มจาก `warn=restricted` ก่อน
</details>

**15. Pod ที่ใช้ image `USER node` ตั้ง `runAsNonRoot: true` ครบตาม restricted แล้ว PSA ยอม แต่ Pod ค้าง `CreateContainerConfigError` เกิดจากอะไร และแก้อย่างไร**

<details>
<summary>แนวคำตอบ</summary>

kubelet ต้องยืนยันว่า user ไม่ใช่ root แต่ image ระบุ user เป็น "ชื่อ" (`node`) ซึ่ง kubelet แปลงเป็นเลขเพื่อตรวจไม่ได้ จึงได้ `container has runAsNonRoot and image has non-numeric user (node), cannot verify user is non-root` แก้โดยใส่ `runAsUser` (และควรใส่ `runAsGroup`) เป็นตัวเลข เช่น 1000 สำหรับ node, 70 สำหรับ postgres ใน image alpine
</details>

**16. ถ้าต้องตั้ง namespace ใหม่ให้ทีมหนึ่งใช้ทำ prod ควรมีอะไรบ้างใน "ชุดตั้งต้น" และเมื่อไรควรเลือกแยกคลัสเตอร์แทน**

<details>
<summary>แนวคำตอบ</summary>

ชุดตั้งต้น: label ระบุทีม/environment, ResourceQuota (งบรวม), LimitRange (ค่าตั้งต้นและขนาดสูงสุดต่อ container), RoleBinding ให้ทีม (เช่น ClusterRole `edit` ผ่าน RoleBinding และ `view` ให้ผู้ตรวจ), label PSA `enforce=restricted` และ NetworkPolicy (default deny + อนุญาตเฉพาะที่จำเป็น รวม DNS ถ้าคุม egress) ควรแยกคลัสเตอร์เมื่อต้องการแยกขาดจริง เช่น ลูกค้าต่างองค์กร ข้อกำหนดด้านความปลอดภัย/กฎหมาย หรือต้องการเวอร์ชัน/ของ cluster-scoped ต่างกัน เพราะ namespace ยังใช้ API server, Node และ kernel ร่วมกัน
</details>

---

## 17. เอกสารอ้างอิง

1. The Kubernetes Authors. *Namespaces*. https://kubernetes.io/docs/concepts/overview/working-with-objects/namespaces/
2. The Kubernetes Authors. *Share a Cluster with Namespaces*. https://kubernetes.io/docs/tasks/administer-cluster/namespaces/
3. The Kubernetes Authors. *Organizing Cluster Access Using kubeconfig Files*. https://kubernetes.io/docs/concepts/configuration/organize-cluster-access-kubeconfig/
4. The Kubernetes Authors. *Configure Access to Multiple Clusters*. https://kubernetes.io/docs/tasks/access-application-cluster/configure-access-multiple-clusters/
5. The Kubernetes Authors. *Object Names and IDs* (RFC 1123 label names). https://kubernetes.io/docs/concepts/overview/working-with-objects/names/
6. The Kubernetes Authors. *Finalizers*. https://kubernetes.io/docs/concepts/overview/working-with-objects/finalizers/
7. The Kubernetes Authors. *DNS for Services and Pods*. https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/
8. The Kubernetes Authors. *Network Policies*. https://kubernetes.io/docs/concepts/services-networking/network-policies/
9. The Kubernetes Authors. *Resource Quotas*. https://kubernetes.io/docs/concepts/policy/resource-quotas/
10. The Kubernetes Authors. *Limit Ranges*. https://kubernetes.io/docs/concepts/policy/limit-range/
11. The Kubernetes Authors. *Using RBAC Authorization*. https://kubernetes.io/docs/reference/access-authn-authz/rbac/
12. The Kubernetes Authors. *Service Accounts*. https://kubernetes.io/docs/concepts/security/service-accounts/
13. The Kubernetes Authors. *Authenticating*. https://kubernetes.io/docs/reference/access-authn-authz/authentication/
14. The Kubernetes Authors. *Pod Security Standards*. https://kubernetes.io/docs/concepts/security/pod-security-standards/
15. The Kubernetes Authors. *Pod Security Admission*. https://kubernetes.io/docs/concepts/security/pod-security-admission/
16. The Kubernetes Authors. *Enforce Pod Security Standards with Namespace Labels*. https://kubernetes.io/docs/tasks/configure-pod-container/enforce-standards-namespace-labels/
17. The Kubernetes Authors. *Configure a Security Context for a Pod or Container*. https://kubernetes.io/docs/tasks/configure-pod-container/security-context/
18. The Kubernetes Authors. *Multi-tenancy*. https://kubernetes.io/docs/concepts/security/multi-tenancy/
19. The Kubernetes Authors. *Well-Known Labels, Annotations and Taints* (`kubernetes.io/metadata.name`). https://kubernetes.io/docs/reference/labels-annotations-taints/
20. kind — Kubernetes IN Docker. *Quick Start*. https://kind.sigs.k8s.io/docs/user/quick-start/

---

> **หมายเหตุเกี่ยวกับภาพประกอบ:** ภาพประกอบ 38 ภาพในโฟลเดอร์ [`images/`](images/) และภาพตัวละครน้องส้ม (`00-character-som.png`) สร้างขึ้นด้วยปัญญาประดิษฐ์สำหรับการสร้างภาพเพื่อใช้ประกอบการเรียนการสอน ชุดคำสั่งสร้างภาพอยู่ใน [`images/imagegen-prompts.md`](images/imagegen-prompts.md) ภาพใช้อุปมาเชิงเปรียบเทียบเพื่อช่วยความเข้าใจ ตัวเลขในภาพ (เช่น IP ของ Pod) เป็นค่าตัวอย่าง ผู้เรียนควรใช้เนื้อหาในเอกสารนี้และเอกสารอ้างอิงเป็นหลัก ผลลัพธ์คำสั่งทั้งหมดมาจากการทดลองจริง (kind v0.33.0, Kubernetes v1.37.0) ค่าเวลา, IP และชื่อ Node ที่ Pod ถูกวางในเครื่องผู้เรียนอาจต่างกัน
