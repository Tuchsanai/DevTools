
## LAB 5: ตาชั่งกองเรือ: topologySpreadConstraints

<p align="center" id="fig-7">
  <img src="images/07-lab5-spread-scale.png" alt="รูปที่ 7 LAB5 ตาชั่งกองเรือ" width="900"><br>
  <em><b>รูปที่ 7</b> LAB5: topologySpreadConstraints กระจาย Pod ให้สมดุล และเห็นกับดัก nodeTaintsPolicy: Ignore ที่นับ control-plane จนเกิด Pending</em>
</p>

**เป้าหมาย:** กระจาย 4 Pod ด้วย `maxSkew: 1` และเห็นด้วยตาว่าค่าเริ่มต้น `nodeTaintsPolicy: Ignore` ทำให้ Pod ค้างใน kind แล้วแก้ด้วย `Honor`

**ไฟล์:** `labs/lab05-topology-spread/`

| ไฟล์ | Pod | label | ต่างกันที่ |
|---|---|---|---|
| `spread-ignore-pods.yaml` | `spread-1..4` | `group=spread` | ไม่ระบุ `nodeTaintsPolicy` (ค่าเริ่มต้น Ignore) |
| `spread-honor-pods.yaml` | `honor-1..4` | `group=honor` | `nodeTaintsPolicy: Honor` |

ทั้งสองไฟล์ใช้ `maxSkew: 1`, `topologyKey: kubernetes.io/hostname`, `whenUnsatisfiable: DoNotSchedule` และใช้ label คนละกลุ่ม จึง apply ต่อกันได้และไม่นับข้ามกลุ่ม

### ขั้นที่ 1: แบบค่าเริ่มต้น (Ignore)

ก่อนรัน ลองทายก่อนว่า 4 Pod จะ Running กี่ตัว

```bash
kubectl apply -f labs/lab05-topology-spread/spread-ignore-pods.yaml; sleep 8; kubectl get pod -l group=spread -o wide
kubectl describe pod spread-3 | sed -n '/^Events/,$p'
```

```text
pod/spread-1 created
pod/spread-2 created
pod/spread-3 created
pod/spread-4 created
NAME       READY   STATUS    RESTARTS   AGE   IP            NODE          NOMINATED NODE   READINESS GATES
spread-1   1/1     Running   0          8s    10.244.2.16   lab-worker2   <none>           <none>
spread-2   1/1     Running   0          8s    10.244.1.11   lab-worker    <none>           <none>
spread-3   0/1     Pending   0          8s    <none>        <none>        <none>           <none>
spread-4   0/1     Pending   0          8s    <none>        <none>        <none>           <none>
Events:
  Type     Reason            Age   From               Message
  ----     ------            ----  ----               -------
  Warning  FailedScheduling  8s    default-scheduler  0/3 nodes are available: 1 node(s) had untolerated taint(s), 2 node(s) didn't match pod topology spread constraints. preemption: 0/3 nodes are available: 1 Preemption is not helpful for scheduling, 2 No preemption victims found for incoming pod.
```

ดู spec ที่ระบบเก็บไว้

```bash
kubectl get pod spread-1 -o jsonpath='{.spec.topologySpreadConstraints}{"\n"}'
```

```text
[{"labelSelector":{"matchLabels":{"group":"spread"}},"maxSkew":1,"topologyKey":"kubernetes.io/hostname","whenUnsatisfiable":"DoNotSchedule"}]
```

### ขั้นที่ 2: แบบ Honor

```bash
kubectl apply -f labs/lab05-topology-spread/spread-honor-pods.yaml; sleep 8; kubectl get pod -l group=honor -o wide
kubectl get pod -l group=honor -o jsonpath='{.items[0].spec.topologySpreadConstraints}{"\n"}'
```

```text
pod/honor-1 created
pod/honor-2 created
pod/honor-3 created
pod/honor-4 created
NAME      READY   STATUS    RESTARTS   AGE   IP            NODE          NOMINATED NODE   READINESS GATES
honor-1   1/1     Running   0          8s    10.244.2.17   lab-worker2   <none>           <none>
honor-2   1/1     Running   0          8s    10.244.1.12   lab-worker    <none>           <none>
honor-3   1/1     Running   0          8s    10.244.2.18   lab-worker2   <none>           <none>
honor-4   1/1     Running   0          8s    10.244.1.13   lab-worker    <none>           <none>
[{"labelSelector":{"matchLabels":{"group":"honor"}},"maxSkew":1,"nodeTaintsPolicy":"Honor","topologyKey":"kubernetes.io/hostname","whenUnsatisfiable":"DoNotSchedule"}]
```

### ขั้นที่ 3: เปรียบเทียบในตารางเดียว

```bash
kubectl get pod -l "group in (spread,honor)" -o custom-columns=NAME:.metadata.name,NODE:.spec.nodeName,STATUS:.status.phase
```

```text
NAME       NODE          STATUS
honor-1    lab-worker2   Running
honor-2    lab-worker    Running
honor-3    lab-worker2   Running
honor-4    lab-worker    Running
spread-1   lab-worker2   Running
spread-2   lab-worker    Running
spread-3   <none>        Pending
spread-4   <none>        Pending
```

### สิ่งที่เห็น

- แบบค่าเริ่มต้น: 1 + 1 แล้ว **ตัวที่ 3–4 Pending** (`didn't match pod topology spread constraints`) ทั้งที่ worker ยังว่างมาก เพราะ `lab-control-plane` ถูกนับเป็นโดเมนที่มี 0 Pod ตัวที่ 3 จะทำให้ skew = 2 − 0 = 2 เกิน 1
- spec ของแบบค่าเริ่มต้นไม่มีฟิลด์ `nodeTaintsPolicy` เลย (ใช้ค่าเริ่มต้น `Ignore`)
- แบบ `Honor`: ไม่นับ Node ที่ Pod ทน taint ไม่ได้ จึงได้ **2 : 2** ครบ 4 ตัว
- spread ต่างจาก anti-affinity ตรงที่ Pod มากกว่าจำนวน Node ได้ ขอแค่สมดุล

> **🤔 คำถามชวนคิด:** ถ้าเปลี่ยน `whenUnsatisfiable` ของ `spread-*` เป็น `ScheduleAnyway` (ยังเป็น Ignore) คาดว่า `spread-3` และ `spread-4` จะเป็นอย่างไร เพราะอะไร

### เก็บกวาด LAB 5

```bash
kubectl delete pod -l lab=03 --now; kubectl get pod
```

```text
pod "honor-1" deleted from default namespace
...
pod "spread-4" deleted from default namespace
No resources found in default namespace.
```

---

## LAB 6: ป้ายห้ามขึ้นและบัตรผ่าน: taints และ tolerations

<p align="center" id="fig-8">
  <img src="images/08-lab6-taint-pass.png" alt="รูปที่ 8 LAB6 ป้ายห้ามขึ้นและบัตรผ่าน" width="900"><br>
  <em><b>รูปที่ 8</b> LAB6: ติด taint ให้ lab-worker2 แล้วให้เฉพาะ Pod ที่มี toleration ขึ้นได้ และทดลองวาง Pod บน control-plane ด้วย toleration</em>
</p>

**เป้าหมาย:** ใช้ taint `NoSchedule`, toleration, วาง Pod บน control-plane และเห็นผลของ `NoExecute` + `tolerationSeconds`

**ไฟล์:** `labs/lab06-taints/`

| ไฟล์ | Pod | บัตรผ่าน (toleration) | ใบสั่ง (nodeSelector) |
|---|---|---|---|
| `plain-pod.yaml` | `plain-pod` | ไม่มี | ไม่มี |
| `vip-pod.yaml` | `vip-pod` | `dedicated=vip:NoSchedule` | `lab-worker2` |
| `control-plane-pod.yaml` | `control-plane-pod` | `node-role.kubernetes.io/control-plane` `Exists` `NoSchedule` | `node-role.kubernetes.io/control-plane: ""` |
| `noexecute-pods.yaml` | `no-pass` | `dedicated=vip` เท่านั้น | `lab-worker2` |
| | `pass-30s` | `dedicated=vip` + `maintenance=true:NoExecute` 30 วินาที | `lab-worker2` |
| | `pass-forever` | `dedicated=vip` + `maintenance=true:NoExecute` ไม่ระบุเวลา | `lab-worker2` |

### ขั้นที่ 1: ติดป้ายห้ามขึ้นที่ lab-worker2

```bash
kubectl taint node lab-worker2 dedicated=vip:NoSchedule
kubectl describe node lab-worker2 | grep -A1 Taints
```

```text
node/lab-worker2 tainted
Taints:             dedicated=vip:NoSchedule
Unschedulable:      false
```

### ขั้นที่ 2: Pod ธรรมดา, Pod VIP และ Pod บน control-plane

```bash
kubectl apply -f labs/lab06-taints/plain-pod.yaml -f labs/lab06-taints/vip-pod.yaml -f labs/lab06-taints/control-plane-pod.yaml
kubectl wait --for=condition=Ready pod -l lab=03 --timeout=60s; kubectl get pod -o wide
kubectl describe pod vip-pod | grep -A3 Tolerations
```

```text
pod/plain-pod created
pod/vip-pod created
pod/control-plane-pod created
pod/control-plane-pod condition met
pod/plain-pod condition met
pod/vip-pod condition met
NAME                READY   STATUS    RESTARTS   AGE   IP            NODE                NOMINATED NODE   READINESS GATES
control-plane-pod   1/1     Running   0          1s    10.244.0.6    lab-control-plane   <none>           <none>
plain-pod           1/1     Running   0          1s    10.244.1.14   lab-worker          <none>           <none>
vip-pod             1/1     Running   0          1s    10.244.2.19   lab-worker2         <none>           <none>
Tolerations:                 dedicated=vip:NoSchedule
                             node.kubernetes.io/not-ready:NoExecute op=Exists for 300s
                             node.kubernetes.io/unreachable:NoExecute op=Exists for 300s
Events:
```

พิสูจน์ว่า `plain-pod` ไม่ได้ลง `lab-worker` เพราะบังเอิญ: ลบแล้วสร้างใหม่ 5 รอบ

```bash
kubectl delete pod plain-pod --now
for i in 1 2 3 4 5; do kubectl apply -f labs/lab06-taints/plain-pod.yaml >/dev/null; kubectl wait --for=condition=PodScheduled pod/plain-pod --timeout=20s >/dev/null; echo "รอบ $i: $(kubectl get pod plain-pod -o jsonpath={.spec.nodeName})"; kubectl delete pod plain-pod --now >/dev/null; done
```

```text
pod "plain-pod" deleted from default namespace
รอบ 1: lab-worker
รอบ 2: lab-worker
รอบ 3: lab-worker
รอบ 4: lab-worker
รอบ 5: lab-worker
```

### ขั้นที่ 3: เตรียม 3 Pod บน lab-worker2 สำหรับป้ายไล่ลงเรือ

<p align="center" id="fig-9">
  <img src="images/09-lab6-noexecute-timer.png" alt="รูปที่ 9 LAB6 NoExecute และนาฬิกาทราย" width="900"><br>
  <em><b>รูปที่ 9</b> LAB6: taint แบบ NoExecute ไล่ no-pass ทันที, pass-30s ถูกไล่หลัง 30 วินาที, pass-forever อยู่ต่อ</em>
</p>

```bash
kubectl apply -f labs/lab06-taints/plain-pod.yaml -f labs/lab06-taints/noexecute-pods.yaml
kubectl wait --for=condition=Ready pod -l group=noexecute --timeout=60s; kubectl get pod -o wide
```

```text
pod/plain-pod created
pod/no-pass created
pod/pass-30s created
pod/pass-forever created
pod/no-pass condition met
pod/pass-30s condition met
pod/pass-forever condition met
NAME                READY   STATUS    RESTARTS   AGE   IP            NODE                NOMINATED NODE   READINESS GATES
control-plane-pod   1/1     Running   0          32s   10.244.0.6    lab-control-plane   <none>           <none>
no-pass             1/1     Running   0          0s    10.244.2.20   lab-worker2         <none>           <none>
pass-30s            1/1     Running   0          0s    10.244.2.21   lab-worker2         <none>           <none>
pass-forever        1/1     Running   0          0s    10.244.2.22   lab-worker2         <none>           <none>
plain-pod           1/1     Running   0          0s    10.244.1.16   lab-worker          <none>           <none>
vip-pod             1/1     Running   0          32s   10.244.2.19   lab-worker2         <none>           <none>
```

**ทายก่อน:** ตอนนี้บน `lab-worker2` มี 4 Pod (`vip-pod`, `no-pass`, `pass-30s`, `pass-forever`) ถ้าติด `maintenance=true:NoExecute` ตัวไหนจะถูกไล่ และเมื่อไร

### ขั้นที่ 4: ติดป้ายไล่ลงเรือ แล้วเฝ้าดู

🖥️ เปิดหน้าต่างใหม่บนเครื่องนักศึกษา `ssh -p 2223 root@localhost` (หน้าต่างเฝ้าดู) แล้ว 🐧 รัน

```bash
kubectl get pod -l lab=03 -w --output-watch-events -o wide
```

🐧 กลับมาที่ SSH session หลัก ติด taint แล้วดูซ้ำเป็นระยะ (เช่น ที่ 2, 20, 32, 45 วินาที)

```bash
kubectl taint node lab-worker2 maintenance=true:NoExecute
kubectl get pod -l lab=03 -o wide
```

ผลจริงที่ +2 และ +32 วินาทีหลังติด taint

```text
node/lab-worker2 tainted
--- +2s 19:03:32
control-plane-pod   1/1   Running   0     35s   10.244.0.6    lab-control-plane   <none>   <none>
pass-30s            1/1   Running   0     3s    10.244.2.21   lab-worker2         <none>   <none>
pass-forever        1/1   Running   0     3s    10.244.2.22   lab-worker2         <none>   <none>
plain-pod           1/1   Running   0     3s    10.244.1.16   lab-worker          <none>   <none>
...
--- +32s 19:04:02
control-plane-pod   1/1   Running   0     65s   10.244.0.6    lab-control-plane   <none>   <none>
pass-forever        1/1   Running   0     33s   10.244.2.22   lab-worker2         <none>   <none>
plain-pod           1/1   Running   0     33s   10.244.1.16   lab-worker          <none>   <none>
```

หน้าต่างเฝ้าดู (`--output-watch-events`) ผลจริง (ตัดบางคอลัมน์ท้ายออก)

```text
EVENT      NAME                READY   STATUS    RESTARTS   AGE   IP            NODE
ADDED      control-plane-pod   1/1     Running   0          33s   10.244.0.6    lab-control-plane
ADDED      no-pass             1/1     Running   0          1s    10.244.2.20   lab-worker2
ADDED      pass-30s            1/1     Running   0          1s    10.244.2.21   lab-worker2
ADDED      pass-forever        1/1     Running   0          1s    10.244.2.22   lab-worker2
ADDED      plain-pod           1/1     Running   0          1s    10.244.1.16   lab-worker
ADDED      vip-pod             1/1     Running   0          33s   10.244.2.19   lab-worker2
MODIFIED   vip-pod             1/1     Running   0          33s   10.244.2.19   lab-worker2
MODIFIED   no-pass             1/1     Running   0          1s    10.244.2.20   lab-worker2
MODIFIED   vip-pod             1/1     Terminating   0          33s   10.244.2.19   lab-worker2
MODIFIED   no-pass             1/1     Terminating   0          1s    10.244.2.20   lab-worker2
...
MODIFIED   vip-pod             0/1     Completed     0          33s   10.244.2.19   lab-worker2
DELETED    vip-pod             0/1     Completed     0          33s   10.244.2.19   lab-worker2
MODIFIED   no-pass             0/1     Completed     0          1s    10.244.2.20   lab-worker2
DELETED    no-pass             0/1     Completed     0          1s    10.244.2.20   lab-worker2
MODIFIED   pass-30s            1/1     Running       0          31s   10.244.2.21   lab-worker2
MODIFIED   pass-30s            1/1     Terminating   0          31s   10.244.2.21   lab-worker2
...
DELETED    pass-30s            0/1     Completed     0          31s   10.244.2.21   lab-worker2
```

กด Ctrl+C ในหน้าต่างเฝ้าดูแล้วดู Events

```bash
kubectl get events --field-selector reason=TaintManagerEviction
kubectl get events --sort-by=.lastTimestamp | grep -E "no-pass|pass-30s" | tail -8
```

```text
LAST SEEN   TYPE     REASON                 OBJECT         MESSAGE
61s         Normal   TaintManagerEviction   pod/no-pass    Marking for deletion Pod default/no-pass
31s         Normal   TaintManagerEviction   pod/pass-30s   Marking for deletion Pod default/pass-30s
61s         Normal   TaintManagerEviction   pod/vip-pod    Marking for deletion Pod default/vip-pod
...
61s         Normal    TaintManagerEviction      pod/no-pass                 Marking for deletion Pod default/no-pass
61s         Normal    Killing                   pod/no-pass                 Stopping container web
31s         Normal    Killing                   pod/pass-30s                Stopping container web
31s         Normal    TaintManagerEviction      pod/pass-30s                Marking for deletion Pod default/pass-30s
```

### สิ่งที่เห็น

- `NoSchedule` บน `lab-worker2`: `plain-pod` ไปอยู่ `lab-worker` ทุกรอบ ส่วน `vip-pod` (มีบัตร + ใบสั่ง) ลง `lab-worker2` ได้
- `control-plane-pod` Running บน `lab-control-plane` ได้เพราะมีทั้งบัตรผ่าน taint ของ control-plane และ nodeSelector
- `NoExecute`: `no-pass` ถูกไล่ **ทันที (< 1 วินาที)**, `pass-30s` ถูกไล่ที่ **~30–31 วินาที**, `pass-forever` อยู่ต่อ
- **`vip-pod` ถูกไล่ด้วย** เพราะมีบัตรแค่ `dedicated` ไม่มีบัตร `maintenance` (NoExecute ไล่ทุก Pod ที่ไม่มีบัตรตรง ไม่สนว่ามาก่อนหรือหลัง)
- Pod ที่ถูกไล่: `Terminating` → `Completed` → หายจากรายการภายใน ~1 วินาที (Node ปกติ kubelet ยืนยันได้ทันที) และ **ไม่มี Pod ใหม่เกิดแทน**
- Event ที่บอกว่าถูกไล่เพราะ taint คือ `TaintManagerEviction ... Marking for deletion Pod ...`

> **🤔 คำถามชวนคิด:** ถ้าลบ taint `maintenance=true:NoExecute` ออกตอนที่ `pass-30s` อยู่มาได้ 20 วินาที `pass-30s` จะยังถูกไล่ไหม

### เก็บกวาด LAB 6

ลบ **taint ทั้งสอง** ของ `lab-worker2` และลบ Pod แล้วตรวจว่าเหลือ taint เฉพาะ control-plane

```bash
kubectl taint node lab-worker2 maintenance=true:NoExecute- dedicated=vip:NoSchedule-
kubectl delete pod -l lab=03 --now
kubectl get node -o custom-columns=NAME:.metadata.name,TAINTS:.spec.taints[*].key; kubectl get pod
```

```text
node/lab-worker2 untainted
pod "control-plane-pod" deleted from default namespace
pod "pass-forever" deleted from default namespace
pod "plain-pod" deleted from default namespace
NAME                TAINTS
lab-control-plane   node-role.kubernetes.io/control-plane
lab-worker          <none>
lab-worker2         <none>
No resources found in default namespace.
```

---

## LAB 7: ซ่อมเรือ: cordon, drain และ uncordon

<p align="center" id="fig-10">
  <img src="images/10-lab7-cordon-drain.png" alt="รูปที่ 10 LAB7 cordon และ drain" width="900"><br>
  <em><b>รูปที่ 10</b> LAB7: cordon lab-worker แล้ว drain ด้วย --ignore-daemonsets --delete-emptydir-data --force Pod เดี่ยวบนเรือหายไปและไม่ถูกสร้างใหม่ ส่วน lab-worker2 ไม่ได้รับ Pod แทน</em>
</p>

**เป้าหมาย:** เห็นความต่างของ cordon กับ drain, อ่าน error ของ drain ทีละด่าน และเห็นชะตากรรมของ Pod เดี่ยว

**ไฟล์:** `labs/lab07-drain/fleet-pods.yaml` มี `cargo-1..4` (nginx กระจาย 2 worker ด้วย topology spread แบบ Honor) และ `pantry` (มี emptyDir ปักที่ `lab-worker`)

> ⚠️ ข้อความ drain ใน LAB นี้มีคำว่า "DaemonSet" ซึ่งหมายถึง Pod ระบบ `kindnet` และ `kube-proxy` ที่ **ระบบดูแลให้ทุกเรือมีหนึ่งตัว** เราไม่ได้สร้างเองและจะเรียนรายละเอียดภายหลัง

### ขั้นที่ 1: สร้างกองตู้สินค้า

```bash
kubectl apply -f labs/lab07-drain/fleet-pods.yaml; kubectl wait --for=condition=Ready pod -l lab=03 --timeout=60s >/dev/null; kubectl get pod -o wide
```

```text
pod/cargo-1 created
pod/cargo-2 created
pod/cargo-3 created
pod/cargo-4 created
pod/pantry created
NAME      READY   STATUS    RESTARTS   AGE   IP            NODE          NOMINATED NODE   READINESS GATES
cargo-1   1/1     Running   0          1s    10.244.2.23   lab-worker2   <none>           <none>
cargo-2   1/1     Running   0          1s    10.244.1.17   lab-worker    <none>           <none>
cargo-3   1/1     Running   0          1s    10.244.2.24   lab-worker2   <none>           <none>
cargo-4   1/1     Running   0          1s    10.244.1.18   lab-worker    <none>           <none>
pantry    1/1     Running   0          1s    10.244.1.19   lab-worker    <none>           <none>
```

### ขั้นที่ 2: cordon

```bash
kubectl cordon lab-worker; kubectl get nodes
kubectl get node lab-worker -o jsonpath='{.spec.unschedulable} {.spec.taints}{"\n"}'
kubectl run late-cargo --image=nginx:1.27-alpine -l lab=03; kubectl wait --for=condition=Ready pod/late-cargo --timeout=60s >/dev/null; kubectl get pod -o wide
```

```text
node/lab-worker cordoned
NAME                STATUS                     ROLES           AGE   VERSION
lab-control-plane   Ready                      control-plane   11m   v1.37.0
lab-worker          Ready,SchedulingDisabled   <none>          11m   v1.37.0
lab-worker2         Ready                      <none>          11m   v1.37.0
true [{"effect":"NoSchedule","key":"node.kubernetes.io/unschedulable","timeAdded":"2026-10-04T12:04:50Z"}]
pod/late-cargo created
NAME         READY   STATUS    RESTARTS   AGE   IP            NODE          NOMINATED NODE   READINESS GATES
cargo-1      1/1     Running   0          2s    10.244.2.23   lab-worker2   <none>           <none>
cargo-2      1/1     Running   0          2s    10.244.1.17   lab-worker    <none>           <none>
cargo-3      1/1     Running   0          2s    10.244.2.24   lab-worker2   <none>           <none>
cargo-4      1/1     Running   0          2s    10.244.1.18   lab-worker    <none>           <none>
late-cargo   1/1     Running   0          1s    10.244.2.25   lab-worker2   <none>           <none>
pantry       1/1     Running   0          2s    10.244.1.19   lab-worker    <none>           <none>
```

### ขั้นที่ 3: drain ทีละด่าน

ด่านที่ 1: ใส่แค่ `--ignore-daemonsets`

```bash
kubectl drain lab-worker --ignore-daemonsets
```

```text
node/lab-worker already cordoned
error: unable to drain node "lab-worker" due to error: [cannot delete Pods that declare no controller (use --force to override): default/cargo-2, default/cargo-4, cannot delete Pods with local storage (use --delete-emptydir-data to override): default/pantry], continuing command...
There are pending nodes to be drained:
 lab-worker
cannot delete Pods that declare no controller (use --force to override): default/cargo-2, default/cargo-4
cannot delete Pods with local storage (use --delete-emptydir-data to override): default/pantry
```

ด่านที่ 2 (เพื่อดูข้อความ): ใส่ `--force --delete-emptydir-data` แต่ไม่ใส่ `--ignore-daemonsets`

```bash
kubectl drain lab-worker --force --delete-emptydir-data 2>&1 | tail -4
```

```text
error: unable to drain node "lab-worker" due to error: cannot delete DaemonSet-managed Pods (use --ignore-daemonsets to ignore): kube-system/kindnet-dmj46, kube-system/kube-proxy-7xjpl, continuing command...
There are pending nodes to be drained:
 lab-worker
cannot delete DaemonSet-managed Pods (use --ignore-daemonsets to ignore): kube-system/kindnet-dmj46, kube-system/kube-proxy-7xjpl
```

ใส่ครบทั้งสาม

```bash
time kubectl drain lab-worker --ignore-daemonsets --delete-emptydir-data --force
```

```text
node/lab-worker already cordoned
Warning: deleting Pods that declare no controller: default/cargo-2, default/cargo-4, default/pantry; ignoring DaemonSet-managed Pods: kube-system/kindnet-dmj46, kube-system/kube-proxy-7xjpl
evicting pod default/pantry
evicting pod default/cargo-2
evicting pod default/cargo-4
pod/pantry evicted
pod/cargo-4 evicted
pod/cargo-2 evicted
node/lab-worker drained

real	0m2.064s
```

### ขั้นที่ 4: ดูผลหลัง drain

```bash
kubectl get pod -o wide; kubectl get pod -A -o wide --field-selector spec.nodeName=lab-worker
```

```text
NAME         READY   STATUS    RESTARTS   AGE   IP            NODE          NOMINATED NODE   READINESS GATES
cargo-1      1/1     Running   0          21s   10.244.2.23   lab-worker2   <none>           <none>
cargo-3      1/1     Running   0          21s   10.244.2.24   lab-worker2   <none>           <none>
late-cargo   1/1     Running   0          20s   10.244.2.25   lab-worker2   <none>           <none>
NAMESPACE     NAME               READY   STATUS    RESTARTS   AGE   IP           NODE         NOMINATED NODE   READINESS GATES
kube-system   kindnet-dmj46      1/1     Running   0          11m   172.19.0.4   lab-worker   <none>           <none>
kube-system   kube-proxy-7xjpl   1/1     Running   0          11m   172.19.0.4   lab-worker   <none>           <none>
```

### ขั้นที่ 5: uncordon

```bash
kubectl uncordon lab-worker; sleep 10; kubectl get nodes; kubectl get pod -o wide
kubectl get events --field-selector involvedObject.kind=Node,involvedObject.name=lab-worker | tail -5
```

```text
node/lab-worker uncordoned
NAME                STATUS   ROLES           AGE   VERSION
lab-control-plane   Ready    control-plane   12m   v1.37.0
lab-worker          Ready    <none>          12m   v1.37.0
lab-worker2         Ready    <none>          12m   v1.37.0
NAME         READY   STATUS    RESTARTS   AGE   IP            NODE          NOMINATED NODE   READINESS GATES
cargo-1      1/1     Running   0          46s   10.244.2.23   lab-worker2   <none>           <none>
cargo-3      1/1     Running   0          46s   10.244.2.24   lab-worker2   <none>           <none>
late-cargo   1/1     Running   0          45s   10.244.2.25   lab-worker2   <none>           <none>
12m         Normal   Starting                  node/lab-worker   
12m         Normal   RegisteredNode            node/lab-worker   Node lab-worker event: Registered Node lab-worker in Controller
12m         Normal   NodeReady                 node/lab-worker   Node lab-worker status is now: NodeReady
37s         Normal   NodeNotSchedulable        node/lab-worker   Node lab-worker status is now: NodeNotSchedulable
7s          Normal   NodeSchedulable           node/lab-worker   Node lab-worker status is now: NodeSchedulable
```

### สิ่งที่เห็น

- cordon: `Ready,SchedulingDisabled`, `spec.unschedulable: true` + taint `node.kubernetes.io/unschedulable:NoSchedule` Pod เดิมอยู่ต่อ Pod ใหม่ (`late-cargo`) ไป `lab-worker2`
- drain มี 3 ด่าน: Pod เดี่ยว (`--force`), emptyDir (`--delete-emptydir-data`), Pod ระบบที่ทุกเรือต้องมี (`--ignore-daemonsets`) **ทุกครั้งที่ error drain ก็ cordon ไว้แล้ว**
- drain สำเร็จใน ~2 วินาที `cargo-2`, `cargo-4`, `pantry` **หายไปเลย** ไม่มี Pod ใหม่บน `lab-worker2` (ก่อน drain 6 ตัว หลัง drain 3 ตัว)
- บน `lab-worker` เหลือแค่ `kindnet` และ `kube-proxy`
- uncordon แล้ว Node รับ Pod ใหม่ได้ (Event `NodeSchedulable`) แต่ **Pod ที่หายไม่กลับมา** และ Pod บน `lab-worker2` ก็ไม่ย้ายกลับ

> **🤔 คำถามชวนคิด:** ถ้าในงานจริงเราต้อง drain Node ที่มีร้านน้องส้มอยู่ทุกสัปดาห์ ทำไมการใช้ Pod เดี่ยวจึงไม่เหมาะ และอยากได้อะไรมาช่วย

### เก็บกวาด LAB 7

ตรวจว่า **ไม่มี Node ใดเป็น SchedulingDisabled** (ถ้ามี ให้ `kubectl uncordon <ชื่อ>`)

```bash
kubectl delete pod -l lab=03 --now; kubectl get nodes; kubectl get pod
```

```text
pod "cargo-1" deleted from default namespace
pod "cargo-3" deleted from default namespace
pod "late-cargo" deleted from default namespace
NAME                STATUS   ROLES           AGE   VERSION
lab-control-plane   Ready    control-plane   12m   v1.37.0
lab-worker          Ready    <none>          12m   v1.37.0
lab-worker2         Ready    <none>          12m   v1.37.0
No resources found in default namespace.
```

---

## LAB 8: เรือหายในหมอก: Node NotReady

<p align="center" id="fig-11">
  <img src="images/11-lab8-docker-stop-fog.png" alt="รูปที่ 11 LAB8 docker stop เรือล่ม" width="900"><br>
  <em><b>รูปที่ 11</b> LAB8: docker stop lab-worker2 จำลองเรือล่ม node เป็น NotReady และถูกใส่ taint unreachable อัตโนมัติ</em>
</p>

**เป้าหมาย:** จำลอง Node ล่ม แล้วดู NotReady, taint อัตโนมัติ, บัตรผ่านเริ่มต้น 300 วินาที, การไล่ Pod (ค้าง Terminating) และการคืนเรือ

**ไฟล์:** `labs/lab08-node-down/fog-pods.yaml` มี 2 Pod ปักที่ `lab-worker2`: `fog-default` (ไม่ได้ใส่ tolerations เอง) และ `fog-fast` (toleration `unreachable`/`not-ready` แบบ `NoExecute` `tolerationSeconds: 30`)

> ⏱️ LAB นี้ใช้เวลารอรวม **ประมาณ 6–7 นาที** (NotReady ~45–50 วินาที + `fog-default` รออีก 300 วินาที) ระหว่างรอทำอย่างอื่นหรือตอบคำถามชวนคิดได้
>
> ⚠️ คำสั่ง `docker stop`/`docker start`/`docker inspect` ทั้งหมดใน LAB นี้ **🐧 รันใน SSH session ของ k8s-lab** และหยุดได้เฉพาะ **`lab-worker2`** ห้ามหยุด `lab-control-plane`

### ขั้นที่ 1: สร้าง Pod บนเรือที่จะล่ม และดูบัตรผ่านที่ระบบเติมให้

```bash
kubectl apply -f labs/lab08-node-down/fog-pods.yaml; kubectl wait --for=condition=Ready pod -l group=fog --timeout=60s >/dev/null; kubectl get pod -o wide
kubectl get pod fog-default -o yaml | grep -A10 "tolerations:"
kubectl get pod fog-fast -o jsonpath='{range .spec.tolerations[*]}{.key} {.effect} {.tolerationSeconds}{"\n"}{end}'
docker inspect -f '{{.Name}} {{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' lab-control-plane lab-worker lab-worker2
```

```text
pod/fog-default created
pod/fog-fast created
NAME          READY   STATUS    RESTARTS   AGE   IP            NODE          NOMINATED NODE   READINESS GATES
fog-default   1/1     Running   0          1s    10.244.2.26   lab-worker2   <none>           <none>
fog-fast      1/1     Running   0          1s    10.244.2.27   lab-worker2   <none>           <none>
  tolerations:
  - effect: NoExecute
    key: node.kubernetes.io/not-ready
    operator: Exists
    tolerationSeconds: 300
  - effect: NoExecute
    key: node.kubernetes.io/unreachable
    operator: Exists
    tolerationSeconds: 300
  volumes:
  - name: kube-api-access-6v6m4
node.kubernetes.io/unreachable NoExecute 30
node.kubernetes.io/not-ready NoExecute 30
/lab-control-plane 172.19.0.3
/lab-worker 172.19.0.4
/lab-worker2 172.19.0.2
```

### ขั้นที่ 2: เปิดหน้าต่างเฝ้าดู

🖥️ เปิดหน้าต่างใหม่ `ssh -p 2223 root@localhost` แล้ว 🐧 รันลูปนี้ (แสดงเวลานับจากเริ่มลูป สถานะ Node และ Pod ทุก 2 วินาที) **เริ่มลูปก่อน แล้วค่อย docker stop ในขั้นถัดไปทันที**

```bash
T0=$(date +%s); while true; do echo "+$(( $(date +%s) - T0 ))s $(kubectl get node lab-worker2 --no-headers | awk '{print $2}') | $(kubectl get pod -l group=fog --no-headers 2>/dev/null | awk '{printf "%s=%s ", $1, $3}')"; sleep 2; done
```

### ขั้นที่ 3: ทำให้เรือหายในหมอก

🐧 **SSH session หลักของ k8s-lab**

```bash
date +%T; time docker stop lab-worker2; docker ps -a --format "{{.Names}}\t{{.Status}}"
```

```text
19:06:19
lab-worker2

real	0m0.821s
lab-worker	Up 13 minutes
lab-worker2	Exited (130) Less than a second ago
lab-control-plane	Up 13 minutes
```

ผลจริงจากสคริปต์เฝ้าดูที่ใช้ตอนทดสอบ (รูปแบบละเอียดกว่าลูปด้านบน ตัดบางบรรทัดและคอลัมน์ท้าย)

```text
19:06:19 +0s node=Ready Ready=True taints=[] pods: fog-default=Running fog-fast=Running
19:06:41 +21s node=Ready Ready=True taints=[] pods: fog-default=Running fog-fast=Running
19:07:03 +42s node=Ready Ready=True taints=[] pods: fog-default=Running fog-fast=Running
19:07:05 +45s node=NotReady Ready=Unknown taints=[node.kubernetes.io/unreachable:NoSchedule node.kubernetes.io/unreachable:NoExecute ] pods: fog-default=Running fog-fast=Running
19:07:31 +71s node=NotReady Ready=Unknown taints=[node.kubernetes.io/unreachable:NoSchedule node.kubernetes.io/unreachable:NoExecute ] pods: fog-default=Running fog-fast=Running
19:07:33 +73s node=NotReady Ready=Unknown taints=[node.kubernetes.io/unreachable:NoSchedule node.kubernetes.io/unreachable:NoExecute ] pods: fog-default=Running fog-fast=Terminating
...
19:12:05 +345s node=NotReady Ready=Unknown taints=[node.kubernetes.io/unreachable:NoSchedule node.kubernetes.io/unreachable:NoExecute ] pods: fog-default=Terminating fog-fast=Terminating
...
19:12:27 +366s node=NotReady Ready=Unknown taints=[node.kubernetes.io/unreachable:NoSchedule node.kubernetes.io/unreachable:NoExecute ] pods: fog-default=Terminating fog-fast=Terminating
```

<p align="center" id="fig-12">
  <img src="images/12-lab8-eviction-timeline.png" alt="รูปที่ 12 LAB8 ไทม์ไลน์การไล่ Pod" width="900"><br>
  <em><b>รูปที่ 12</b> LAB8: ไทม์ไลน์หลังเรือหายในหมอก: NotReady ประมาณ 45-50 วินาทีหลัง docker stop, fog-fast ถูกไล่หลัง NotReady 30 วินาที, fog-default รอหลัง NotReady 300 วินาที แล้ว docker start คืนเรือ</em>
</p>

### ขั้นที่ 4: สำรวจระหว่างเรือ NotReady (ภายใน 30 วินาทีหลัง NotReady)

```bash
kubectl get nodes
kubectl describe node lab-worker2 | sed -n '/^Taints/,/^Addresses/p'
kubectl get pod -o wide
kubectl get pod fog-default -o jsonpath='{range .status.conditions[*]}{.type}={.status} {end}{"\n"}'
```

```text
NAME                STATUS     ROLES           AGE   VERSION
lab-control-plane   Ready      control-plane   14m   v1.37.0
lab-worker          Ready      <none>          14m   v1.37.0
lab-worker2         NotReady   <none>          14m   v1.37.0
Taints:             node.kubernetes.io/unreachable:NoExecute
                    node.kubernetes.io/unreachable:NoSchedule
Unschedulable:      false
Lease:
  HolderIdentity:  lab-worker2
  AcquireTime:     <unset>
  RenewTime:       Sun, 04 Oct 2026 19:06:10 +0700
Conditions:
  Type             Status    LastHeartbeatTime                 LastTransitionTime                Reason              Message
  ----             ------    -----------------                 ------------------                ------              -------
  MemoryPressure   Unknown   Sun, 04 Oct 2026 19:02:44 +0700   Sun, 04 Oct 2026 19:07:03 +0700   NodeStatusUnknown   Kubelet stopped posting node status.
  DiskPressure     Unknown   Sun, 04 Oct 2026 19:02:44 +0700   Sun, 04 Oct 2026 19:07:03 +0700   NodeStatusUnknown   Kubelet stopped posting node status.
  PIDPressure      Unknown   Sun, 04 Oct 2026 19:02:44 +0700   Sun, 04 Oct 2026 19:07:03 +0700   NodeStatusUnknown   Kubelet stopped posting node status.
  Ready            Unknown   Sun, 04 Oct 2026 19:02:44 +0700   Sun, 04 Oct 2026 19:07:03 +0700   NodeStatusUnknown   Kubelet stopped posting node status.
Addresses:
NAME          READY   STATUS    RESTARTS   AGE   IP            NODE          NOMINATED NODE   READINESS GATES
fog-default   1/1     Running   0          83s   10.244.2.26   lab-worker2   <none>           <none>
fog-fast      1/1     Running   0          83s   10.244.2.27   lab-worker2   <none>           <none>
PodReadyToStartContainers=True Initialized=True Ready=False ContainersReady=True PodScheduled=True 
```

ลองคุยกับ Pod บนเรือที่ล่ม

```bash
timeout 15 kubectl exec fog-default -- hostname; echo "exit=$?"
timeout 15 kubectl logs fog-default | tail -2
kubectl get events --field-selector reason=NodeNotReady | tail -5
```

```text
error: unable to upgrade connection: error dialing backend: dial tcp 172.19.0.2:10250: connect: no route to host
exit=1
Error from server: Get "https://172.19.0.2:10250/containerLogs/default/fog-default/web": dial tcp 172.19.0.2:10250: connect: no route to host
LAST SEEN   TYPE      REASON         OBJECT             MESSAGE
42s         Warning   NodeNotReady   pod/fog-default    Node is not ready
42s         Warning   NodeNotReady   pod/fog-fast       Node is not ready
42s         Normal    NodeNotReady   node/lab-worker2   Node lab-worker2 status is now: NodeNotReady
```

### ขั้นที่ 5: fog-fast ถูกไล่ และลอง apply ซ้ำ

ราว 30 วินาทีหลัง NotReady

```bash
kubectl get pod -o wide
kubectl apply -f labs/lab08-node-down/fog-pods.yaml
kubectl get pod fog-fast -o jsonpath='{.metadata.deletionTimestamp} grace={.metadata.deletionGracePeriodSeconds}{"\n"}'
```

```text
NAME          READY   STATUS        RESTARTS   AGE    IP            NODE          NOMINATED NODE   READINESS GATES
fog-default   1/1     Running       0          2m7s   10.244.2.26   lab-worker2   <none>           <none>
fog-fast      1/1     Terminating   0          2m7s   10.244.2.27   lab-worker2   <none>           <none>
pod/fog-default unchanged
Warning: Detected changes to resource fog-fast which is currently being deleted.
pod/fog-fast unchanged
2026-10-04T12:08:03Z grace=30
```

### ขั้นที่ 6: รอ fog-default (ครบ 300 วินาทีหลัง NotReady)

ประมาณ 6 นาทีหลัง `docker stop`

```bash
kubectl get pod -o wide; kubectl get nodes
```

```text
NAME          READY   STATUS        RESTARTS   AGE     IP            NODE          NOMINATED NODE   READINESS GATES
fog-default   1/1     Terminating   0          6m25s   10.244.2.26   lab-worker2   <none>           <none>
fog-fast      1/1     Terminating   0          6m25s   10.244.2.27   lab-worker2   <none>           <none>
NAME                STATUS     ROLES           AGE   VERSION
lab-control-plane   Ready      control-plane   19m   v1.37.0
lab-worker          Ready      <none>          19m   v1.37.0
lab-worker2         NotReady   <none>          19m   v1.37.0
```

### ขั้นที่ 7: คืนเรือ

🐧 **SSH session หลักของ k8s-lab**

```bash
docker start lab-worker2; T0=$(date +%s); until kubectl get node lab-worker2 --no-headers | grep -q " Ready "; do sleep 1; done; echo "lab-worker2 กลับ Ready หลัง docker start $(( $(date +%s) - T0 )) วินาที"; kubectl get nodes -o wide
```

```text
lab-worker2
lab-worker2 กลับ Ready หลัง docker start 2 วินาที
NAME                STATUS   ROLES           AGE   VERSION   INTERNAL-IP   EXTERNAL-IP   OS-IMAGE                       KERNEL-VERSION                             CONTAINER-RUNTIME
lab-control-plane   Ready    control-plane   19m   v1.37.0   172.19.0.3    <none>        Debian GNU/Linux 13 (trixie)   6.6.87.2-microsoft-standard-WSL2 (amd64)   containerd://2.3.4
lab-worker          Ready    <none>          19m   v1.37.0   172.19.0.4    <none>        Debian GNU/Linux 13 (trixie)   6.6.87.2-microsoft-standard-WSL2 (amd64)   containerd://2.3.4
lab-worker2         Ready    <none>          19m   v1.37.0   172.19.0.2    <none>        Debian GNU/Linux 13 (trixie)   6.6.87.2-microsoft-standard-WSL2 (amd64)   containerd://2.3.4
```

รอประมาณ 10–30 วินาที แล้วตรวจ

```bash
kubectl get pod -o wide
kubectl get node lab-worker2 -o custom-columns=NAME:.metadata.name,TAINTS:.spec.taints[*].key
kubectl get pod -n kube-system -o wide --field-selector spec.nodeName=lab-worker2
```

```text
No resources found in default namespace.
NAME          TAINTS
lab-worker2   <none>
NAME               READY   STATUS    RESTARTS      AGE   IP           NODE          NOMINATED NODE   READINESS GATES
kindnet-68hkk      1/1     Running   1 (33s ago)   19m   172.19.0.2   lab-worker2   <none>           <none>
kube-proxy-7k6xk   1/1     Running   1 (33s ago)   19m   172.19.0.2   lab-worker2   <none>           <none>
```

สคริปต์เฝ้าดูหลัง `docker start` (ผลจริง)

```text
19:12:31 +3s node=Ready Ready=True taints=[node.kubernetes.io/unreachable:NoExecute ] pods: fog-default=Unknown fog-fast=Unknown
19:12:33 +5s node=Ready Ready=True taints=[node.kubernetes.io/unreachable:NoExecute ] pods:
19:12:35 +7s node=Ready Ready=True taints=[] pods:
```

กด Ctrl+C หยุดลูปในหน้าต่างเฝ้าดู

### ขั้นที่ 8 (ทางเลือก): เรือกลับมาก่อนครบเวลา

ทำซ้ำ แต่คืนเรือ **10 วินาทีหลัง NotReady** (ก่อนครบ 30 วินาทีของ `fog-fast`)

```bash
kubectl apply -f labs/lab08-node-down/fog-pods.yaml; kubectl wait --for=condition=Ready pod -l group=fog --timeout=60s >/dev/null; kubectl get pod -o wide
T0=$(date +%s); docker stop lab-worker2 >/dev/null; until kubectl get node lab-worker2 --no-headers | grep -q NotReady; do sleep 1; done; echo "NotReady หลัง docker stop $(( $(date +%s) - T0 )) วินาที"; sleep 10; docker start lab-worker2 >/dev/null; T1=$(date +%s); until kubectl get node lab-worker2 --no-headers | grep -q " Ready "; do sleep 1; done; echo "Ready หลัง docker start $(( $(date +%s) - T1 )) วินาที"; sleep 15; kubectl get pod -o wide
```

```text
pod/fog-default created
pod/fog-fast created
NAME          READY   STATUS    RESTARTS   AGE   IP           NODE          NOMINATED NODE   READINESS GATES
fog-default   1/1     Running   0          1s    10.244.2.2   lab-worker2   <none>           <none>
fog-fast      1/1     Running   0          1s    10.244.2.3   lab-worker2   <none>           <none>
NotReady หลัง docker stop 50 วินาที
Ready หลัง docker start 2 วินาที
NAME          READY   STATUS    RESTARTS      AGE   IP           NODE          NOMINATED NODE   READINESS GATES
fog-default   1/1     Running   1 (17s ago)   79s   10.244.2.3   lab-worker2   <none>           <none>
fog-fast      1/1     Running   1 (17s ago)   79s   10.244.2.2   lab-worker2   <none>           <none>
```

### สิ่งที่เห็น

- `docker stop` ใช้เวลาไม่ถึง 1 วินาที แต่ Node ยังแสดง `Ready` อีก **~45–50 วินาที** (วัดได้ 44–50 วินาที) ก่อนเป็น `NotReady` เพราะหอบังคับการรอ grace period ก่อนตัดสิน (heartbeat สุดท้าย 19:06:10 → NotReady 19:07:03)
- condition ทุกตัวเป็น `Unknown` (`Kubelet stopped posting node status.`) พร้อม taint `node.kubernetes.io/unreachable` ทั้ง `NoSchedule` และ `NoExecute`
- Pod บนเรือยังแสดง `1/1 Running` แต่ condition `Ready=False` และ exec/logs ใช้ไม่ได้ (`dial tcp 172.19.0.2:10250: connect: no route to host`)
- `fog-fast` ถูกไล่ที่ **NotReady + ~30 วินาที** (+73 วินาทีจาก stop) `fog-default` ถูกไล่ที่ **NotReady + ~300 วินาที** (+345 วินาทีจาก stop) **เวลานับจาก NotReady ไม่ใช่จาก docker stop**
- ถูกไล่แล้วค้าง `Terminating` จนเรือกลับ ไม่มี Pod ใหม่เกิดที่ `lab-worker` และ apply ซ้ำได้แค่ Warning `currently being deleted`
- `docker start` → Ready ใน 2 วินาที IP เดิม Pod ที่ถูกไล่หายจริงใน ~5 วินาที taint หายใน ~7 วินาที `kindnet`/`kube-proxy` RESTARTS +1
- ถ้าเรือกลับก่อนครบเวลา Pod ไม่ถูกไล่ แต่ RESTARTS เป็น 1 และ **Pod IP เปลี่ยน** (สลับ `.2` กับ `.3`)

> **🤔 คำถามชวนคิด:** ทำไมระบบจึงตั้งค่าเริ่มต้นให้รอถึง 300 วินาทีก่อนไล่ Pod แทนที่จะไล่ทันทีที่ NotReady ข้อดีและข้อเสียคืออะไร

### เก็บกวาด LAB 8

ตรวจว่า **`lab-worker2` กลับมาเป็น `Ready`** (ถ้ายังเป็น NotReady ให้ 🐧 `docker start lab-worker2` แล้วรอ) จากนั้นลบ Pod

```bash
kubectl delete pod -l lab=03 --now; kubectl get nodes; kubectl get pod
```

```text
pod "fog-default" deleted from default namespace
pod "fog-fast" deleted from default namespace
NAME                STATUS   ROLES           AGE   VERSION
lab-control-plane   Ready    control-plane   22m   v1.37.0
lab-worker          Ready    <none>          21m   v1.37.0
lab-worker2         Ready    <none>          21m   v1.37.0
No resources found in default namespace.
```

---

## LAB 9: ตู้ของต้นเรือ: static Pod

<p align="center" id="fig-13">
  <img src="images/13-lab9-static-pod.png" alt="รูปที่ 13 LAB9 static Pod" width="900"><br>
  <em><b>รูปที่ 13</b> LAB9: วางไฟล์ manifest ลง /etc/kubernetes/manifests ใน lab-worker ด้วย docker cp kubelet สร้าง static Pod และ mirror pod static-snack-lab-worker</em>
</p>

**เป้าหมาย:** เห็นว่า kubelet สร้าง Pod จากไฟล์บนเรือเองโดยไม่ผ่าน scheduler, รู้จัก mirror pod และวิธีลบ static Pod ที่ถูกต้อง

**ไฟล์:** `labs/lab09-static-pod/static-snack.yaml` (nginx ชื่อ `static-snack`) — **ไม่ได้ติด label `lab=03`** โดยตั้งใจ เพื่อไม่ให้คำสั่งเก็บกวาดของ LAB อื่นไปลบ mirror pod แล้วค้าง

> ⚠️ คำสั่ง `docker exec lab-control-plane ...`, `docker exec lab-worker ...` และ `docker cp ... lab-worker:...` ใน LAB นี้ **🐧 รันใน SSH session ของ k8s-lab**

### ขั้นที่ 1: static Pod ของหอบังคับการ

```bash
docker exec lab-control-plane ls /etc/kubernetes/manifests
kubectl get pod -n kube-system -o wide | grep lab-control-plane
```

```text
etcd.yaml
kube-apiserver.yaml
kube-controller-manager.yaml
kube-scheduler.yaml
coredns-559f6c778d-s7ml2                    1/1     Running   0             22m   10.244.0.4   lab-control-plane   <none>           <none>
coredns-559f6c778d-v4wmg                    1/1     Running   0             22m   10.244.0.3   lab-control-plane   <none>           <none>
etcd-lab-control-plane                      1/1     Running   0             22m   172.19.0.3   lab-control-plane   <none>           <none>
kindnet-wvgxp                               1/1     Running   0             22m   172.19.0.3   lab-control-plane   <none>           <none>
kube-apiserver-lab-control-plane            1/1     Running   0             22m   172.19.0.3   lab-control-plane   <none>           <none>
kube-controller-manager-lab-control-plane   1/1     Running   0             22m   172.19.0.3   lab-control-plane   <none>           <none>
kube-proxy-4cmxx                            1/1     Running   0             22m   172.19.0.3   lab-control-plane   <none>           <none>
kube-scheduler-lab-control-plane            1/1     Running   0             22m   172.19.0.3   lab-control-plane   <none>           <none>
```

### ขั้นที่ 2: ตรวจแฟ้มบนเรือ lab-worker

```bash
docker exec lab-worker grep staticPodPath /var/lib/kubelet/config.yaml; docker exec lab-worker ls -la /etc/kubernetes/manifests
```

```text
staticPodPath: /etc/kubernetes/manifests
total 8
drwxr-xr-x 2 root root 4096 Aug 20 11:25 .
drwxr-xr-x 1 root root 4096 Oct  4 11:53 ..
```

### ขั้นที่ 3: วางแฟ้มลงบนเรือ

```bash
docker exec lab-worker mkdir -p /etc/kubernetes/manifests
docker cp labs/lab09-static-pod/static-snack.yaml lab-worker:/etc/kubernetes/manifests/
kubectl wait --for=condition=Ready pod/static-snack-lab-worker --timeout=60s; kubectl get pod -o wide
```

(`mkdir -p` ไม่จำเป็นเพราะโฟลเดอร์มีอยู่แล้ว แต่ใส่ไว้กันพลาดได้ ถ้า `kubectl wait` ขึ้น `NotFound` เพราะ mirror pod ยังไม่ทันโผล่ ให้รอ 2–3 วินาทีแล้วรันใหม่)

```text
pod/static-snack-lab-worker condition met
NAME                      READY   STATUS    RESTARTS   AGE   IP            NODE         NOMINATED NODE   READINESS GATES
static-snack-lab-worker   1/1     Running   0          0s    10.244.1.20   lab-worker   <none>           <none>
```

### ขั้นที่ 4: ตรวจว่าเป็น mirror pod

```bash
kubectl get pod static-snack-lab-worker -o yaml | grep -E -A6 "^  annotations:|^  ownerReferences:"
kubectl describe pod static-snack-lab-worker | sed -n '/^Events/,$p'
```

```text
  annotations:
    kubernetes.io/config.hash: 2f1365a1083c561d7f460f6a6525964b
    kubernetes.io/config.mirror: 2f1365a1083c561d7f460f6a6525964b
    kubernetes.io/config.seen: "2026-10-04T12:15:43.509068771Z"
    kubernetes.io/config.source: file
  creationTimestamp: "2026-10-04T12:15:43Z"
  generation: 1
--
  ownerReferences:
  - apiVersion: v1
    controller: true
    kind: Node
    name: lab-worker
    uid: 15dc410e-40e0-4d3f-9d68-88b5ee898db2
  resourceVersion: "3625"
Events:
  Type    Reason   Age   From     Message
  ----    ------   ----  ----     -------
  Normal  Pulled   18s   kubelet  spec.containers{web}: Container image "nginx:1.27-alpine" already present on machine and can be accessed by the pod
  Normal  Created  18s   kubelet  spec.containers{web}: Container created
  Normal  Started  18s   kubelet  spec.containers{web}: Container started
```

### ขั้นที่ 5: ลองลบด้วย kubectl

`kubectl delete` mirror pod จะค้างประมาณ 1 นาที จึงใส่ `--wait=false` แล้วดูด้วย `-w` (กด Ctrl+C เมื่อเห็น Pod กลับมา)

```bash
kubectl delete pod static-snack-lab-worker --wait=false
kubectl get pod -w -o wide --output-watch-events
```

```text
pod "static-snack-lab-worker" deleted from default namespace
19:19:13 EVENT      NAME                      READY   STATUS        RESTARTS   AGE   IP            NODE         NOMINATED NODE   READINESS GATES
19:19:13 ADDED      static-snack-lab-worker   1/1     Terminating   0          5s    10.244.1.22   lab-worker   <none>           <none>
19:20:33 MODIFIED   static-snack-lab-worker   1/1     Terminating   0          85s   10.244.1.22   lab-worker   <none>           <none>
19:20:33 DELETED    static-snack-lab-worker   1/1     Terminating   0          85s   10.244.1.22   lab-worker   <none>           <none>
19:20:33 ADDED      static-snack-lab-worker   0/1     Pending       0          0s    <none>        lab-worker   <none>           <none>
```

(ผลจริงข้างบนมาจากรอบที่เติมเวลาไว้หน้าบรรทัด) ดู container จริงบนเรือ

```bash
docker exec lab-worker crictl ps --name web
```

```text
CONTAINER           IMAGE               CREATED              STATE               NAME                ATTEMPT             POD ID              POD                       NAMESPACE
23a0a2ec810e2       6769dc3a703c7       About a minute ago   Running             web                 0                   9b3ca85cc9e1c       static-snack-lab-worker   default
```

### ขั้นที่ 6: ลบให้หายจริง

```bash
docker exec lab-worker rm /etc/kubernetes/manifests/static-snack.yaml; sleep 4; kubectl get pod; docker exec lab-worker ls /etc/kubernetes/manifests
```

```text
No resources found in default namespace.
```

(`ls` ไม่แสดงอะไร = โฟลเดอร์ว่างแล้ว ในการทดลองวัดได้ว่า Pod หายภายใน 3 วินาทีหลังลบไฟล์)

### สิ่งที่เห็น

- องค์ประกอบหลักของหอบังคับการเป็น static Pod จาก 4 ไฟล์ใน `/etc/kubernetes/manifests` ชื่อลงท้าย `-lab-control-plane` และใช้ IP ของ Node
- `staticPodPath` ของ worker คือ `/etc/kubernetes/manifests` (มีอยู่แล้วและว่าง)
- วางไฟล์แล้ว mirror pod `static-snack-lab-worker` โผล่และ Ready เกือบทันที **Events ไม่มี `Scheduled`**
- mirror pod มี annotation `kubernetes.io/config.mirror`, `config.source: file` และ `ownerReferences` เป็น `kind: Node`
- `kubectl delete` ค้าง Terminating ราว 65–85 วินาที แล้ว **ถูกสร้างกลับมา** ส่วน container จริงไม่ถูกรีสตาร์ต (ATTEMPT 0)
- ลบไฟล์บนเรือ → Pod หายจริงในไม่กี่วินาที

> **🤔 คำถามชวนคิด:** ถ้า kube-scheduler ของคลัสเตอร์ล่ม Pod ใหม่ทั่วไปจะเป็นอย่างไร และ static Pod ที่วางไฟล์ใหม่จะยังเกิดได้ไหม เพราะอะไร

### เก็บกวาด LAB 9

ต้องมั่นใจว่า **ไม่มีไฟล์ static Pod ค้างบนเรือ** (ถ้าค้าง Pod จะกลับมาเองแม้รีสตาร์ตเรือ)

```bash
docker exec lab-worker rm -f /etc/kubernetes/manifests/static-snack.yaml
docker exec lab-worker ls /etc/kubernetes/manifests
kubectl get pod
```

---
