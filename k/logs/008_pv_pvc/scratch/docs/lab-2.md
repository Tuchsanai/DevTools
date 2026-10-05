## LAB 5: accessModes กับ local-path

<p align="center" id="fig-7">
  <img src="images/07-lab5-access-modes.png" alt="รูปที่ 7 LAB 5 accessModes" width="900"><br>
  <em><b>รูปที่ 7</b> LAB5: PVC RWX → ProvisioningFailed, Block → does not support block, RWOP Pod ที่ 2 Pending, RWO Pod 2 ตัวบน Node เดียวใช้ได้</em>
</p>

**เป้าหมาย:** ทดสอบว่า local-path รองรับ accessModes/volumeMode แบบไหน เห็นว่า RWO ไม่ได้แปลว่า Pod เดียว RWOP กัน Pod ที่ 2 ได้จริง และขนาดใน PVC ไม่ถูกบังคับ

**ไฟล์ (`lab05-access/`):**

| ไฟล์ | เนื้อหา |
|---|---|
| `rwo.yaml` | PVC `rwo-data` (RWO) + Pod `rwo-a` เขียน `/data/shared.txt` |
| `rwo-second.yaml` | Pod `rwo-b` ใช้ `rwo-data` เดียวกัน เขียนต่อแล้วแสดงไฟล์ |
| `rwop.yaml` | PVC `single` (ReadWriteOncePod) + Pod `rwop-a` |
| `rwop-second.yaml` | Pod `rwop-b` ขอใช้ `single` |
| `rwx.yaml` | PVC `shared` (ReadWriteMany) + Pod `use-rwx` |
| `blk.yaml` | PVC `blk` (`volumeMode: Block`) + Pod `use-blk` ที่ใช้ `volumeDevices` |

### ขั้นที่ 1: RWO — Pod 2 ตัวบน Node เดียวกัน

🐧 **ใน SSH session ของ k8s-lab**

```bash
cd /workspace/008_kubernetes_pv_pvc/02_LAB/labs/lab05-access
kubectl apply -f rwo.yaml; kubectl wait --for=condition=Ready pod/rwo-a --timeout=90s; kubectl apply -f rwo-second.yaml; kubectl wait --for=condition=Ready pod/rwo-b --timeout=90s; kubectl get pod rwo-a rwo-b -o wide; kubectl logs rwo-b
```

```text
persistentvolumeclaim/rwo-data created
pod/rwo-a created
pod/rwo-a condition met
pod/rwo-b created
pod/rwo-b condition met
NAME    READY   STATUS    RESTARTS   AGE   IP            NODE         NOMINATED NODE   READINESS GATES
rwo-a   1/1     Running   0          5s    10.244.2.11   lab-worker   <none>           <none>
rwo-b   1/1     Running   0          1s    10.244.2.12   lab-worker   <none>           <none>
05:40:06 from rwo-a
05:40:07 from rwo-b
```

ทั้งคู่ Running บน **Node เดียวกัน** และ `rwo-b` อ่านบรรทัดที่ `rwo-a` เขียนได้ RWO = เมานต์ได้จาก Node เดียว ไม่ใช่ Pod เดียว

### ขั้นที่ 2: ขนาดไม่ถูกบังคับ

<p align="center" id="fig-8">
  <img src="images/08-lab5-size-not-enforced.png" alt="รูปที่ 8 LAB 5 ขนาดไม่ถูกบังคับ" width="900"><br>
  <em><b>รูปที่ 8</b> LAB5 (ต่อ): dd เขียน 50MB ลง PVC 10Mi สำเร็จ, df -h เห็นขนาดดิสก์ทั้งก้อนของ Node — requests.storage ใน local-path เป็นแค่ตัวเลข</em>
</p>

```bash
kubectl exec rwo-a -- sh -c "dd if=/dev/zero of=/data/big bs=1M count=50 && ls -lh /data/big && df -h /data"; kubectl get pvc rwo-data
```

```text
50+0 records in
50+0 records out
52428800 bytes (50.0MB) copied, 0.378015 seconds, 132.3MB/s
-rw-r--r--    1 root     root       50.0M Oct  5 05:40 /data/big
Filesystem                Size      Used Available Use% Mounted on
/dev/sdd               1006.9G    224.6G    731.1G  23% /data
NAME       STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
rwo-data   Bound    pvc-ef6d2f75-cbb0-4b2f-9696-408f278e2d5d   10Mi       RWO            standard       <unset>                 5s
```

เขียน 50MB ลงตู้ที่ป้ายบอก 10Mi ได้ และ `df` เห็นดิสก์ทั้งก้อนของ Node (ตัวเลขเป็นของเครื่องทดสอบ ของนักศึกษาจะต่างกัน) เพราะตู้ของ local-path เป็นแค่โฟลเดอร์บนดิสก์ของ Node

### ขั้นที่ 3: RWOP — Pod ที่ 2 เข้าไม่ได้

```bash
kubectl apply -f rwop.yaml; kubectl wait --for=condition=Ready pod/rwop-a --timeout=90s; kubectl apply -f rwop-second.yaml; sleep 8; kubectl get pod rwop-a rwop-b -o wide; kubectl describe pod rwop-b | tail -4
```

```text
persistentvolumeclaim/single created
pod/rwop-a created
pod/rwop-a condition met
pod/rwop-b created
NAME     READY   STATUS    RESTARTS   AGE   IP            NODE         NOMINATED NODE   READINESS GATES
rwop-a   1/1     Running   0          14s   10.244.2.14   lab-worker   <none>           <none>
rwop-b   0/1     Pending   0          8s    <none>        <none>       <none>           <none>
Events:
  Type     Reason            Age   From               Message
  ----     ------            ----  ----               -------
  Warning  FailedScheduling  8s    default-scheduler  0/3 nodes are available: 1 node(s) had untolerated taint(s), 2 node(s) unavailable due to PersistentVolumeClaim with ReadWriteOncePod access mode already in-use by another pod. preemption: 0/3 nodes are available: 1 Preemption is not helpful for scheduling, 2 No preemption victims found for incoming pod.
```

`rwop-b` ค้าง `Pending` เพราะตู้ RWOP มีเจ้าของแล้ว (worker ทั้ง 2 ตัวถูกตัด ส่วน control-plane ติด taint) เราจะใช้คุณสมบัตินี้ป้องกันฐานข้อมูลใน LAB 10 ขั้น H

### ขั้นที่ 4: RWX และ Block — provisioner ปฏิเสธ

```bash
kubectl apply -f rwx.yaml -f blk.yaml; sleep 8; kubectl get pvc; kubectl get pod use-rwx use-blk
```

```text
persistentvolumeclaim/shared created
pod/use-rwx created
persistentvolumeclaim/blk created
pod/use-blk created
NAME       STATUS    VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
blk        Pending                                                                        standard       <unset>                 8s
rwo-data   Bound     pvc-ef6d2f75-cbb0-4b2f-9696-408f278e2d5d   10Mi       RWO            standard       <unset>                 30s
shared     Pending                                                                        standard       <unset>                 8s
single     Bound     pvc-024e3dd8-93b7-4c2a-91d5-23b055943fe5   10Mi       RWOP           standard       <unset>                 25s
NAME      READY   STATUS    RESTARTS   AGE
use-rwx   0/1     Pending   0          8s
use-blk   0/1     Pending   0          8s
```

ดูสาเหตุที่ PVC (ไม่ใช่ที่ Pod)

```bash
kubectl describe pvc shared | sed -n "/Events:/,\$p"
kubectl describe pvc blk | sed -n "/Events:/,\$p"
```

```text
Events:
  Type     Reason                Age              From                                                                                                Message
  ----     ------                ----             ----                                                                                                -------
  Normal   WaitForFirstConsumer  8s               persistentvolume-controller                                                                         waiting for first consumer to be created before binding
  Normal   Provisioning          8s               rancher.io/local-path_local-path-provisioner-75f7fc7dc5-5dkx2_6485bdfa-b176-4448-844b-ec03de28220b  External provisioner is provisioning volume for claim "default/shared"
  Warning  ProvisioningFailed    8s               rancher.io/local-path_local-path-provisioner-75f7fc7dc5-5dkx2_6485bdfa-b176-4448-844b-ec03de28220b  failed to provision volume with StorageClass "standard": NodePath only supports ReadWriteOnce and ReadWriteOncePod (1.22+) access modes
  Normal   ExternalProvisioning  0s (x2 over 8s)  persistentvolume-controller                                                                         Waiting for a volume to be created either by the external provisioner 'rancher.io/local-path' or manually by the system administrator. If volume creation is delayed, please verify that the provisioner is running and correctly registered.
Events:
  Type     Reason                Age              From                                                                                                Message
  ----     ------                ----             ----                                                                                                -------
  Normal   WaitForFirstConsumer  9s               persistentvolume-controller                                                                         waiting for first consumer to be created before binding
  Warning  ProvisioningFailed    9s               rancher.io/local-path_local-path-provisioner-75f7fc7dc5-5dkx2_6485bdfa-b176-4448-844b-ec03de28220b  rancher.io/local-path does not support block volume provisioning
  Normal   ExternalProvisioning  1s (x2 over 9s)  persistentvolume-controller                                                                         Waiting for a volume to be created either by the external provisioner 'rancher.io/local-path' or manually by the system administrator. If volume creation is delayed, please verify that the provisioner is running and correctly registered.
```

ส่วน Pod ที่รออยู่ **ไม่มี Event เลย**

```bash
kubectl describe pod use-rwx | tail -3
kubectl get events --field-selector involvedObject.name=shared -o custom-columns=REASON:.reason,COUNT:.count
```

```text
Tolerations:                 node.kubernetes.io/not-ready:NoExecute op=Exists for 300s
                             node.kubernetes.io/unreachable:NoExecute op=Exists for 300s
Events:                      <none>
REASON                 COUNT
WaitForFirstConsumer   1
ExternalProvisioning   3
Provisioning           2
ProvisioningFailed     2
```

provisioner ลองซ้ำเรื่อย ๆ (COUNT เพิ่มขึ้นตามเวลา) แต่จะไม่สำเร็จ เพราะโฟลเดอร์บน Node เดียวให้หลาย Node เขียนพร้อมกันไม่ได้ และไม่ใช่ดิสก์ดิบ

### ขั้นที่ 5: เก็บกวาด

```bash
time kubectl delete -f .; kubectl get pvc,pv
```

```text
persistentvolumeclaim "blk" deleted from default namespace
pod "use-blk" deleted from default namespace
pod "rwo-b" deleted from default namespace
persistentvolumeclaim "rwo-data" deleted from default namespace
pod "rwo-a" deleted from default namespace
pod "rwop-b" deleted from default namespace
persistentvolumeclaim "single" deleted from default namespace
pod "rwop-a" deleted from default namespace
persistentvolumeclaim "shared" deleted from default namespace
pod "use-rwx" deleted from default namespace

real	0m3.456s
...
NAME                                                        CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS     CLAIM              STORAGECLASS   VOLUMEATTRIBUTESCLASS   REASON   AGE
persistentvolume/pvc-024e3dd8-93b7-4c2a-91d5-23b055943fe5   10Mi       RWOP           Delete           Released   default/single     standard       <unset>                          50s
persistentvolume/pvc-ef6d2f75-cbb0-4b2f-9696-408f278e2d5d   10Mi       RWO            Delete           Released   default/rwo-data   standard       <unset>                          57s
```

`kubectl delete -f .` ลบทุกไฟล์ในโฟลเดอร์ PV ที่เห็น `Released` เป็นช่วงสั้น ๆ ก่อน provisioner ลบทิ้ง (Delete) รอสักครู่แล้วตรวจซ้ำ

```bash
kubectl get pv; docker exec lab-worker ls /var/local-path-provisioner/
```

```text
No resources found
```

### สิ่งที่เห็น

- RWO: Pod 2 ตัวบน Node เดียวใช้ร่วมได้ — RWOP: Pod ที่ 2 `Pending … ReadWriteOncePod access mode already in-use`
- RWX: `NodePath only supports ReadWriteOnce and ReadWriteOncePod (1.22+) access modes`, Block: `does not support block volume provisioning` — Pod ไม่มี Event ต้องดูที่ PVC
- ขนาดใน PVC ของ local-path ไม่ถูกบังคับ

**คำถามชวนคิด**

1. ถ้า `rwo-a` อยู่ `lab-worker` แล้วสร้าง Pod ที่ใช้ `rwo-data` โดยปัก `nodeSelector` ไว้ที่ `lab-worker2` คาดว่าจะเกิดอะไร
2. ร้านที่มีหลาย Pod ต้องอ่านเขียนโฟลเดอร์รูปสินค้าเดียวกันจากหลาย Node ต้องใช้ storage แบบไหน

---

## LAB 6: วงจรชีวิต: finalizer, Delete, Retain และกู้ PV

<p align="center" id="fig-9">
  <img src="images/09-lab6-finalizer-delete.png" alt="รูปที่ 9 LAB 6 finalizer และ Delete" width="900"><br>
  <em><b>รูปที่ 9</b> LAB6: ลบ PVC ที่ Pod ใช้อยู่ → Terminating (pvc-protection) → ลบ Pod → PVC หาย PV หาย โฟลเดอร์บน Node หาย (Delete)</em>
</p>

**เป้าหมาย:** ดูวงจรชีวิตของตู้ทั้งหมด: finalizer กันลบ, reclaimPolicy Delete, เปลี่ยนเป็น Retain, PVC ชื่อเดิมไม่ได้ตู้เดิม และกู้ตู้ที่ `Released` กลับมาด้วย `claimRef` + `volumeName`

**ไฟล์:** `lab06-lifecycle/pvc.yaml` (PVC `ledger` 10Mi class `standard`), `pod.yaml` (Pod `ledger-pod` เขียน `keepme.txt` ครั้งแรกครั้งเดียว ถ้ามีอยู่แล้วไม่เขียนทับ แล้วแสดงไฟล์), `pvc-reuse.yaml` (PVC `ledger` ที่มี `volumeName: PV_NAME`)

### ขั้นที่ 1: finalizer กันลบใบเบิกที่ยังใช้อยู่

🐧 **ใน SSH session ของ k8s-lab**

```bash
cd /workspace/008_kubernetes_pv_pvc/02_LAB/labs/lab06-lifecycle
kubectl apply -f pvc.yaml -f pod.yaml; kubectl wait --for=condition=Ready pod/ledger-pod --timeout=90s; kubectl logs ledger-pod; kubectl get pvc ledger
kubectl delete pvc ledger --wait=false; sleep 2; kubectl get pvc ledger; kubectl describe pvc ledger | grep -E "^Status|Finalizers|Used By"
```

```text
persistentvolumeclaim/ledger created
pod/ledger-pod created
pod/ledger-pod condition met
keepme เขียนเมื่อ 05:41:19
NAME     STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
ledger   Bound    pvc-8584059b-0fd6-421f-9daa-44fd8f36a76d   10Mi       RWO            standard       <unset>                 5s
persistentvolumeclaim "ledger" deleted from default namespace
NAME     STATUS        VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
ledger   Terminating   pvc-8584059b-0fd6-421f-9daa-44fd8f36a76d   10Mi       RWO            standard       <unset>                 7s
Status:        Terminating (lasts 2s)
Finalizers:    [kubernetes.io/pvc-protection]
Used By:       ledger-pod
```

`--wait=false` ให้ kubectl ไม่รอ (ไม่อย่างนั้นจะค้างรอจนกว่าจะลบได้) PVC ค้าง `Terminating` เพราะ finalizer `kubernetes.io/pvc-protection` และ `Used By: ledger-pod`

### ขั้นที่ 2: ลบ Pod → PVC, PV และโฟลเดอร์หาย (Delete)

```bash
PV=$(kubectl get pvc ledger -o jsonpath="{.spec.volumeName}"); N=$(kubectl get pod ledger-pod -o jsonpath="{.spec.nodeName}"); echo "PV=$PV N=$N"; kubectl delete pod ledger-pod; kubectl get pvc,pv; sleep 1; kubectl get pv; sleep 4; kubectl get pv; docker exec $N ls /var/local-path-provisioner/
```

```text
PV=pvc-8584059b-0fd6-421f-9daa-44fd8f36a76d N=lab-worker
pod "ledger-pod" deleted from default namespace
NAME                                                        CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS     CLAIM            STORAGECLASS   VOLUMEATTRIBUTESCLASS   REASON   AGE
persistentvolume/pvc-8584059b-0fd6-421f-9daa-44fd8f36a76d   10Mi       RWO            Delete           Released   default/ledger   standard       <unset>                          8s
NAME                                       CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS     CLAIM            STORAGECLASS   VOLUMEATTRIBUTESCLASS   REASON   AGE
pvc-8584059b-0fd6-421f-9daa-44fd8f36a76d   10Mi       RWO            Delete           Released   default/ledger   standard       <unset>                          9s
No resources found
```

เมื่อ Pod หายไป PVC ถูกลบจริง PV เป็น `Released` 1–2 วินาที แล้วถูกลบพร้อมโฟลเดอร์ (คำสั่ง `ls` สุดท้ายไม่แสดงอะไร) ข้อมูล `keepme.txt` หายถาวร

### ขั้นที่ 3: เปลี่ยนตู้เป็น Retain แล้วลบใบเบิก

<p align="center" id="fig-10">
  <img src="images/10-lab6-retain-rescue.png" alt="รูปที่ 10 LAB 6 Retain และกู้ตู้" width="900"><br>
  <em><b>รูปที่ 10</b> LAB6 (ต่อ): patch PV เป็น Retain → ลบ PVC → Released ไฟล์ keepme.txt ยังอยู่ → ลบ claimRef → Available → PVC ใหม่ใส่ volumeName → Bound อ่าน keepme ได้</em>
</p>

```bash
kubectl apply -f pvc.yaml -f pod.yaml; kubectl wait --for=condition=Ready pod/ledger-pod --timeout=90s; kubectl logs ledger-pod
PV=$(kubectl get pvc ledger -o jsonpath="{.spec.volumeName}"); echo PV=$PV; kubectl patch pv $PV -p "{\"spec\":{\"persistentVolumeReclaimPolicy\":\"Retain\"}}"; kubectl get pv $PV
```

```text
persistentvolumeclaim/ledger created
pod/ledger-pod created
pod/ledger-pod condition met
keepme เขียนเมื่อ 05:41:40
PV=pvc-4c821b49-b44e-4818-a63e-c65943143e39
persistentvolume/pvc-4c821b49-b44e-4818-a63e-c65943143e39 patched
NAME                                       CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS   CLAIM            STORAGECLASS   VOLUMEATTRIBUTESCLASS   REASON   AGE
pvc-4c821b49-b44e-4818-a63e-c65943143e39   10Mi       RWO            Retain           Bound    default/ledger   standard       <unset>                          2s
```

จำเวลาใน `keepme เขียนเมื่อ ...` ของตัวเองไว้ (ตัวอย่าง `05:41:40`) ใช้พิสูจน์ในขั้นที่ 5 ต่อไปลบ Pod และ PVC

```bash
kubectl delete -f pod.yaml -f pvc.yaml; sleep 3; kubectl get pv; PV=$(kubectl get pv -o jsonpath="{.items[0].metadata.name}"); N=$(kubectl get pv $PV -o jsonpath="{.spec.nodeAffinity.required.nodeSelectorTerms[0].matchExpressions[0].values[0]}"); echo "N=$N"; docker exec $N ls /var/local-path-provisioner/; docker exec $N sh -c "cat /var/local-path-provisioner/${PV}_default_ledger/keepme.txt"
```

```text
pod "ledger-pod" deleted from default namespace
persistentvolumeclaim "ledger" deleted from default namespace
NAME                                       CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS     CLAIM            STORAGECLASS   VOLUMEATTRIBUTESCLASS   REASON   AGE
pvc-4c821b49-b44e-4818-a63e-c65943143e39   10Mi       RWO            Retain           Released   default/ledger   standard       <unset>                          10s
N=lab-worker
pvc-4c821b49-b44e-4818-a63e-c65943143e39_default_ledger
keepme เขียนเมื่อ 05:41:40
```

ตู้ `Released` ค้างอยู่ (ไม่ถูกบด) และไฟล์ยังอยู่บน Node (หา Node จาก `nodeAffinity` ของ PV เพราะไม่มี Pod แล้ว)

### ขั้นที่ 4: ใบเบิกชื่อเดิมไม่ได้ตู้เดิม

```bash
kubectl apply -f pvc.yaml -f pod.yaml; sleep 5; kubectl get pvc ledger; kubectl get pv; kubectl logs ledger-pod
```

```text
persistentvolumeclaim/ledger created
pod/ledger-pod created
NAME     STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
ledger   Bound    pvc-9b832bb3-1026-4f3b-a81e-1810820588b9   10Mi       RWO            standard       <unset>                 5s
NAME                                       CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS     CLAIM            STORAGECLASS   VOLUMEATTRIBUTESCLASS   REASON   AGE
pvc-4c821b49-b44e-4818-a63e-c65943143e39   10Mi       RWO            Retain           Released   default/ledger   standard       <unset>                          15s
pvc-9b832bb3-1026-4f3b-a81e-1810820588b9   10Mi       RWO            Delete           Bound      default/ledger   standard       <unset>                          2s
keepme เขียนเมื่อ 05:41:53
```

PVC ใหม่ชื่อ `ledger` เหมือนเดิม แต่ได้ **ตู้ใหม่** (`pvc-9b83…`, Delete) และ `keepme.txt` เป็นไฟล์ใหม่ (เวลาใหม่) ตู้เดิมยัง `Released` เพราะยังจำ `claimRef` ของ PVC ตัวเก่า (uid เก่า) ลบชุดนี้ทิ้งก่อน (ตู้ใหม่เป็น Delete จึงหายไปเอง เหลือแต่ตู้ Retain)

```bash
kubectl delete -f pod.yaml -f pvc.yaml; sleep 6; kubectl get pv
```

```text
pod "ledger-pod" deleted from default namespace
persistentvolumeclaim "ledger" deleted from default namespace
NAME                                       CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS     CLAIM            STORAGECLASS   VOLUMEATTRIBUTESCLASS   REASON   AGE
pvc-4c821b49-b44e-4818-a63e-c65943143e39   10Mi       RWO            Retain           Released   default/ledger   standard       <unset>                          30s
```

### ขั้นที่ 5: กู้ตู้เดิม

ลบ `claimRef` ให้ตู้กลับเป็น `Available` แล้วสร้างใบเบิกที่ระบุชื่อตู้ (`pvc-reuse.yaml` ผ่าน `sed` แทน `PV_NAME`)

```bash
PV=$(kubectl get pv -o jsonpath="{.items[0].metadata.name}"); echo PV=$PV; kubectl patch pv $PV --type json -p "[{\"op\":\"remove\",\"path\":\"/spec/claimRef\"}]"; kubectl get pv $PV
```

```text
PV=pvc-4c821b49-b44e-4818-a63e-c65943143e39
persistentvolume/pvc-4c821b49-b44e-4818-a63e-c65943143e39 patched
NAME                                       CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS      CLAIM   STORAGECLASS   VOLUMEATTRIBUTESCLASS   REASON   AGE
pvc-4c821b49-b44e-4818-a63e-c65943143e39   10Mi       RWO            Retain           Available           standard       <unset>                          30s
```

```bash
PV=$(kubectl get pv -o jsonpath="{.items[0].metadata.name}"); sed "s/PV_NAME/$PV/" pvc-reuse.yaml | kubectl apply -f -; kubectl apply -f pod.yaml; kubectl wait --for=condition=Ready pod/ledger-pod --timeout=90s; kubectl get pvc ledger; kubectl get pv; kubectl logs ledger-pod
```

```text
persistentvolumeclaim/ledger created
pod/ledger-pod created
pod/ledger-pod condition met
NAME     STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
ledger   Bound    pvc-4c821b49-b44e-4818-a63e-c65943143e39   10Mi       RWO            standard       <unset>                 1s
NAME                                       CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS   CLAIM            STORAGECLASS   VOLUMEATTRIBUTESCLASS   REASON   AGE
pvc-4c821b49-b44e-4818-a63e-c65943143e39   10Mi       RWO            Retain           Bound    default/ledger   standard       <unset>                          31s
keepme เขียนเมื่อ 05:41:40
```

ได้ **ตู้เดิม** (`pvc-4c82…`) และ `keepme เขียนเมื่อ 05:41:40` ตรงกับเวลาที่จดไว้ในขั้นที่ 3 ข้อมูลกลับมาครบ (คำสั่ง `items[0]` ใช้ได้เพราะตอนนี้มี PV ตัวเดียว ถ้ามีหลายตัวให้ระบุชื่อเอง)

### ขั้นที่ 6: ลบตู้ Retain แล้วโฟลเดอร์ยังอยู่ (เก็บกวาด)

```bash
PV=$(kubectl get pvc ledger -o jsonpath="{.spec.volumeName}"); kubectl get pv $PV -o jsonpath="{.metadata.finalizers}{\"\n\"}"; kubectl delete pod ledger-pod; kubectl delete pvc ledger; kubectl delete pv $PV; kubectl get pv; docker exec lab-worker ls -la /var/local-path-provisioner/
```

```text
["kubernetes.io/pv-protection"]
pod "ledger-pod" deleted from default namespace
persistentvolumeclaim "ledger" deleted from default namespace
persistentvolume "pvc-4c821b49-b44e-4818-a63e-c65943143e39" deleted
No resources found
total 12
drwxr-xr-x  3 root root 4096 Oct  5 05:42 .
drwxr-xr-x 12 root root 4096 Oct  5 05:39 ..
drwxrwxrwx  2 root root 4096 Oct  5 05:41 pvc-4c821b49-b44e-4818-a63e-c65943143e39_default_ledger
```

PV ถูกลบแล้ว แต่โฟลเดอร์ `…_default_ledger` ยังอยู่บน Node (provisioner ไม่ลบข้อมูลของตู้ Retain) ลบเอง (ถ้าตู้ของนักศึกษาอยู่ `lab-worker2` ให้เปลี่ยนชื่อ Node)

```bash
docker exec lab-worker sh -c "rm -rf /var/local-path-provisioner/pvc-*_default_ledger"; docker exec lab-worker ls /var/local-path-provisioner/
```

### สิ่งที่เห็น

- ลบ PVC ที่ใช้อยู่ → `Terminating` (`pvc-protection`, `Used By`) จนกว่า Pod จะหาย
- Delete: PV `Released` ชั่วครู่แล้วหายพร้อมโฟลเดอร์ — Retain (`kubectl patch pv`): `Released` ข้อมูลอยู่
- PVC ชื่อเดิมได้ตู้ใหม่ กู้ตู้เดิมด้วยการลบ `claimRef` + PVC ที่มี `volumeName`
- ลบ PV ที่ Retain แล้วโฟลเดอร์บน Node ยังอยู่

**คำถามชวนคิด**

1. ถ้าลืม `--wait=false` ในขั้นที่ 1 terminal จะเป็นอย่างไร และจะออกจากสถานการณ์นั้นได้อย่างไร
2. ถ้าใช้ `pvc-reuse.yaml` ตอนที่ PV ยัง `Released` (ยังไม่ได้ลบ `claimRef`) คาดว่า PVC จะเป็นสถานะใด

---

## LAB 7: StorageClass ของเราเอง

<p align="center" id="fig-11">
  <img src="images/11-lab7-storageclass.png" alt="รูปที่ 11 LAB 7 StorageClass ของเราเอง" width="900"><br>
  <em><b>รูปที่ 11</b> LAB7: สร้าง standard-retain (Retain), local-immediate (Immediate → no node was specified), local-expand (allowVolumeExpansion: true → spec 20Mi แต่ capacity ยัง 10Mi ไม่มีใครขยายให้)</em>
</p>

**เป้าหมาย:** สร้าง StorageClass 3 แบบด้วย provisioner ตัวเดิม (`rancher.io/local-path`) เพื่อเห็นผลของ `reclaimPolicy`, `volumeBindingMode` และ `allowVolumeExpansion`

**ไฟล์ (`lab07-storageclass/`):** class `sc-retain.yaml` (`standard-retain` Retain), `sc-immediate.yaml` (`local-immediate` Immediate), `sc-expand.yaml` (`local-expand` `allowVolumeExpansion: true`) และใบเบิก `pvc-retain.yaml` (`kept` + Pod `kept-user`), `pvc-standard.yaml` (`std` + Pod `std-user`), `pvc-expand.yaml` (`ex` + Pod `ex-user`), `pvc-immediate.yaml` (`imm` ไม่มี Pod)

### ขั้นที่ 1: สร้าง class และใบเบิก

🐧 **ใน SSH session ของ k8s-lab**

```bash
cd /workspace/008_kubernetes_pv_pvc/02_LAB/labs/lab07-storageclass
kubectl apply -f sc-retain.yaml -f sc-immediate.yaml -f sc-expand.yaml; kubectl get sc
```

```text
storageclass.storage.k8s.io/standard-retain created
storageclass.storage.k8s.io/local-immediate created
storageclass.storage.k8s.io/local-expand created
NAME                 PROVISIONER             RECLAIMPOLICY   VOLUMEBINDINGMODE      ALLOWVOLUMEEXPANSION   AGE
local-expand         rancher.io/local-path   Delete          WaitForFirstConsumer   true                   0s
local-immediate      rancher.io/local-path   Delete          Immediate              false                  0s
standard (default)   rancher.io/local-path   Delete          WaitForFirstConsumer   false                  8m39s
standard-retain      rancher.io/local-path   Retain          WaitForFirstConsumer   false                  0s
```

```bash
kubectl apply -f pvc-retain.yaml -f pvc-standard.yaml -f pvc-expand.yaml -f pvc-immediate.yaml; kubectl wait --for=condition=Ready pod/kept-user pod/std-user pod/ex-user --timeout=90s; sleep 3; kubectl get pvc; kubectl get pv
```

```text
persistentvolumeclaim/kept created
pod/kept-user created
persistentvolumeclaim/std created
pod/std-user created
persistentvolumeclaim/ex created
pod/ex-user created
persistentvolumeclaim/imm created
pod/kept-user condition met
pod/std-user condition met
pod/ex-user condition met
NAME   STATUS    VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS      VOLUMEATTRIBUTESCLASS   AGE
ex     Bound     pvc-064ee503-ec2c-4d5c-abf1-004a8dd1759f   10Mi       RWO            local-expand      <unset>                 9s
imm    Pending                                                                        local-immediate   <unset>                 9s
kept   Bound     pvc-29503d87-cb90-4f0e-a081-439f3235d48b   10Mi       RWO            standard-retain   <unset>                 9s
std    Bound     pvc-a47bd8d7-34ef-44eb-ac9f-8ba88b7d068c   10Mi       RWO            standard          <unset>                 9s
NAME                                       CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS   CLAIM          STORAGECLASS      VOLUMEATTRIBUTESCLASS   REASON   AGE
pvc-064ee503-ec2c-4d5c-abf1-004a8dd1759f   10Mi       RWO            Delete           Bound    default/ex     local-expand      <unset>                          5s
pvc-29503d87-cb90-4f0e-a081-439f3235d48b   10Mi       RWO            Retain           Bound    default/kept   standard-retain   <unset>                          6s
pvc-a47bd8d7-34ef-44eb-ac9f-8ba88b7d068c   10Mi       RWO            Delete           Bound    default/std    standard          <unset>                          7s
```

PV ของ `kept` ได้ `Retain` ตาม class ส่วน `imm` ค้าง `Pending`

### ขั้นที่ 2: Immediate ใช้กับ local-path ไม่ได้

```bash
kubectl describe pvc imm | sed -n "/Events:/,\$p"
```

```text
Events:
  Type     Reason                Age              From                                                                                                Message
  ----     ------                ----             ----                                                                                                -------
  Normal   ExternalProvisioning  9s (x2 over 9s)  persistentvolume-controller                                                                         Waiting for a volume to be created either by the external provisioner 'rancher.io/local-path' or manually by the system administrator. If volume creation is delayed, please verify that the provisioner is running and correctly registered.
  Normal   Provisioning          9s               rancher.io/local-path_local-path-provisioner-75f7fc7dc5-5dkx2_6485bdfa-b176-4448-844b-ec03de28220b  External provisioner is provisioning volume for claim "default/imm"
  Warning  ProvisioningFailed    9s               rancher.io/local-path_local-path-provisioner-75f7fc7dc5-5dkx2_6485bdfa-b176-4448-844b-ec03de28220b  failed to provision volume with StorageClass "local-immediate": configuration error, no node was specified
```

`Immediate` เริ่มสร้างทันทีโดยไม่มี Pod จึงไม่มี `selected-node` provisioner ไม่รู้ว่าจะสร้างโฟลเดอร์บน Node ไหน (`no node was specified`)

### ขั้นที่ 3: ขยาย PVC

```bash
kubectl patch pvc std -p "{\"spec\":{\"resources\":{\"requests\":{\"storage\":\"20Mi\"}}}}"; echo "exit=$?"
```

```text
Error from server (Forbidden): persistentvolumeclaims "std" is forbidden: only dynamically provisioned pvc can be resized and the storageclass that provisions the pvc must support resize
exit=1
```

class `standard` ไม่อนุญาตให้ขยาย ลองกับ `ex` (class `local-expand`) แล้วรอ 20 วินาที

```bash
kubectl patch pvc ex -p "{\"spec\":{\"resources\":{\"requests\":{\"storage\":\"20Mi\"}}}}"; sleep 20; kubectl get pvc ex; kubectl get pvc ex -o jsonpath="spec={.spec.resources.requests.storage} status={.status.capacity.storage} conditions={.status.conditions}{\"\n\"}"; kubectl get pv $(kubectl get pvc ex -o jsonpath="{.spec.volumeName}") -o jsonpath="pv={.spec.capacity.storage}{\"\n\"}"; kubectl describe pvc ex | sed -n "/Events:/,\$p"
```

```text
persistentvolumeclaim/ex patched
NAME   STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
ex     Bound    pvc-064ee503-ec2c-4d5c-abf1-004a8dd1759f   10Mi       RWO            local-expand   <unset>                 33s
spec=20Mi status=10Mi conditions=[{"lastProbeTime":null,"lastTransitionTime":"2026-10-05T05:42:26Z","message":"A pod is currently referencing this PVC","reason":"PodUsingPVC","status":"False","type":"Unused"}]
pv=10Mi
Events:
  ...
  Normal  ProvisioningSucceeded  30s   rancher.io/local-path_local-path-provisioner-75f7fc7dc5-5dkx2_6485bdfa-b176-4448-844b-ec03de28220b  Successfully provisioned volume pvc-064ee503-ec2c-4d5c-abf1-004a8dd1759f
  Normal  ExternalExpanding      21s   volume_expand                                                                                       waiting for an external controller to expand this PVC
```

API ยอมรับ (`patched`, `spec=20Mi`) แต่ `status`/PV ยัง `10Mi` และ Event `ExternalExpanding` บอกว่ารอ controller ภายนอก ซึ่ง local-path ไม่มี จึงค้างแบบนี้ไปเรื่อย ๆ สุดท้ายลองลดขนาด

```bash
kubectl patch pvc ex -p "{\"spec\":{\"resources\":{\"requests\":{\"storage\":\"5Mi\"}}}}"; echo "exit=$?"
```

```text
The PersistentVolumeClaim "ex" is invalid: spec.resources.requests.storage: Forbidden: field can not be less than status.capacity
exit=1
```

### ขั้นที่ 4: ลบ class แล้ว PV ยังอยู่ (เก็บกวาด)

```bash
PV=$(kubectl get pvc kept -o jsonpath="{.spec.volumeName}"); N=$(kubectl get pod kept-user -o jsonpath="{.spec.nodeName}"); kubectl delete -f .; sleep 4; kubectl get pvc,pv; docker exec $N ls /var/local-path-provisioner/
```

```text
persistentvolumeclaim "ex" deleted from default namespace
pod "ex-user" deleted from default namespace
persistentvolumeclaim "imm" deleted from default namespace
persistentvolumeclaim "kept" deleted from default namespace
pod "kept-user" deleted from default namespace
persistentvolumeclaim "std" deleted from default namespace
pod "std-user" deleted from default namespace
storageclass.storage.k8s.io "local-expand" deleted
storageclass.storage.k8s.io "local-immediate" deleted
storageclass.storage.k8s.io "standard-retain" deleted
NAME                                                        CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS     CLAIM          STORAGECLASS      VOLUMEATTRIBUTESCLASS   REASON   AGE
persistentvolume/pvc-29503d87-cb90-4f0e-a081-439f3235d48b   10Mi       RWO            Retain           Released   default/kept   standard-retain   <unset>                          44s
pvc-29503d87-cb90-4f0e-a081-439f3235d48b_default_kept
```

class ถูกลบแล้ว แต่ PV ของ `kept` ยังอยู่ (`Released`, class `standard-retain` ที่ไม่มีแล้ว) พร้อมโฟลเดอร์ ลบเอง

```bash
kubectl get sc; PV=$(kubectl get pv -o jsonpath="{.items[0].metadata.name}"); N=$(kubectl get pv $PV -o jsonpath="{.spec.nodeAffinity.required.nodeSelectorTerms[0].matchExpressions[0].values[0]}"); kubectl delete pv $PV; docker exec $N sh -c "rm -rf /var/local-path-provisioner/${PV}_default_kept; ls /var/local-path-provisioner/"; kubectl get pv
```

```text
NAME                 PROVISIONER             RECLAIMPOLICY   VOLUMEBINDINGMODE      ALLOWVOLUMEEXPANSION   AGE
standard (default)   rancher.io/local-path   Delete          WaitForFirstConsumer   false                  9m27s
persistentvolume "pvc-29503d87-cb90-4f0e-a081-439f3235d48b" deleted
No resources found
```

### สิ่งที่เห็น

- class ใหม่ใช้ provisioner เดิมได้ reclaimPolicy ของ class ถูกใส่ให้ PV ที่สร้าง (`kept` → Retain)
- `Immediate` + local-path → `configuration error, no node was specified`
- `standard` ขยายไม่ได้ (Forbidden) `allowVolumeExpansion: true` ผ่าน API แต่ไม่มีใครขยายจริง (`ExternalExpanding`) ลดขนาดไม่ได้
- ลบ class ไม่กระทบ PV ที่สร้างไปแล้ว

**คำถามชวนคิด**

1. ถ้าตั้ง `standard-retain` เป็น default class แทน `standard` PVC ใน LAB 3 จะต่างไปอย่างไรตอนเก็บกวาด
2. ถ้าย้ายร้านไปคลาวด์ที่ CSI driver ขยายดิสก์ได้ ขั้นตอนขยาย PVC ของ db ควรเป็นอย่างไร และต้องตรวจอะไรใน StorageClass ก่อน

---

## LAB 8: Node ล่ม: ตู้เซฟติดเรือ

<p align="center" id="fig-12">
  <img src="images/12-lab8-node-down.png" alt="รูปที่ 12 LAB 8 Node ล่ม" width="900"><br>
  <em><b>รูปที่ 12</b> LAB8: Deployment + PVC (tolerationSeconds 30) → docker stop Node ที่ Pod อยู่ → NotReady ~40–50 วิ → Pod ใหม่ Pending ~65–70 วิ (PersistentVolume's node affinity) → docker start แล้ว Pod กลับมาพร้อมข้อมูลเดิม</em>
</p>

**เป้าหมาย:** ต่อจากบทที่ 3 (Node ล่ม) เห็นว่าเมื่อ Pod ใช้ local storage Deployment สร้าง Pod ใหม่ได้ แต่ Pod ใหม่ **ไปลง Node อื่นไม่ได้** จนกว่า Node เดิมจะกลับมา

**ไฟล์:** `lab08-node-down/nd.yaml` — PVC `nd-data` (10Mi) + Deployment `nd` (replicas 1, `Recreate`, tolerations `unreachable`/`not-ready` แบบ `tolerationSeconds: 30` แทน default 300) Pod เขียนบรรทัดใหม่ลง `/data/boot.txt` ทุกครั้งที่เริ่ม พร้อมชื่อ Node (Downward API)

> **ข้อควรระวัง:** LAB นี้หยุด container ของ Node **ภายใน k8s-lab** ด้วย `docker stop` **ต้อง `docker start` ให้ Node กลับมาก่อนไป LAB ถัดไปเสมอ** และ **ห้าม `kind load` ระหว่าง Node หยุด** (pre-check พบ `failed to detect containerd snapshotter`) ใช้ Node ที่ Pod อยู่จริง (`$N`) ซึ่งอาจเป็น `lab-worker` หรือ `lab-worker2`

### ขั้นที่ 1: สร้าง Deployment ที่ใช้ PVC

🐧 **ใน SSH session ของ k8s-lab**

```bash
cd /workspace/008_kubernetes_pv_pvc/02_LAB/labs/lab08-node-down
kubectl apply -f nd.yaml; kubectl rollout status deploy/nd --timeout=90s; kubectl get pod -l app=nd -o wide; kubectl logs deploy/nd; kubectl get pvc nd-data
```

```text
persistentvolumeclaim/nd-data created
deployment.apps/nd created
Waiting for deployment "nd" rollout to finish: 0 of 1 updated replicas are available...
deployment "nd" successfully rolled out
NAME                 READY   STATUS    RESTARTS   AGE   IP            NODE         NOMINATED NODE   READINESS GATES
nd-d49d6fd9f-hj8fp   1/1     Running   0          5s    10.244.2.35   lab-worker   <none>           <none>
05:43:21 start nd-d49d6fd9f-hj8fp on lab-worker
NAME      STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
nd-data   Bound    pvc-c20aba41-55db-4d7a-8003-770cdd1daa40   10Mi       RWO            standard       <unset>                 5s
```

### ขั้นที่ 2: หยุด Node ที่ Pod อยู่ แล้วเฝ้าดู

คำสั่งนี้หา Node ใส่ `$N` แล้ว `docker stop` และพิมพ์สถานะทุก 5 วินาที 24 รอบ (ราว 2 นาที)

```bash
N=$(kubectl get pod -l app=nd -o jsonpath="{.items[0].spec.nodeName}"); echo "N=$N"; date +%T; docker stop $N; echo "stopped $(date +%T)"; for i in $(seq 1 24); do sleep 5; echo "--- $(date +%T)"; kubectl get node $N --no-headers; kubectl get pod -l app=nd -o wide --no-headers; done
```

```text
N=lab-worker
12:43:21
lab-worker
stopped 12:43:31
--- 12:43:36
lab-worker   Ready   <none>   9m43s   v1.37.0
nd-d49d6fd9f-hj8fp   1/1   Running   0     20s   10.244.2.35   lab-worker   <none>   <none>
...
--- 12:44:07
lab-worker   Ready   <none>   10m   v1.37.0
nd-d49d6fd9f-hj8fp   1/1   Running   0     51s   10.244.2.35   lab-worker   <none>   <none>
--- 12:44:12
lab-worker   NotReady   <none>   10m   v1.37.0
nd-d49d6fd9f-hj8fp   1/1   Running   0     56s   10.244.2.35   lab-worker   <none>   <none>
...
--- 12:44:32
lab-worker   NotReady   <none>   10m   v1.37.0
nd-d49d6fd9f-hj8fp   1/1   Running   0     76s   10.244.2.35   lab-worker   <none>   <none>
--- 12:44:37
lab-worker   NotReady   <none>   10m   v1.37.0
nd-d49d6fd9f-hj8fp   1/1   Terminating   0     81s   10.244.2.35   lab-worker   <none>   <none>
nd-d49d6fd9f-xdg9j   0/1   Pending       0     0s    <none>        <none>       <none>   <none>
...
--- 12:45:33
lab-worker   NotReady   <none>   11m   v1.37.0
nd-d49d6fd9f-hj8fp   1/1   Terminating   0     2m17s   10.244.2.35   lab-worker   <none>   <none>
nd-d49d6fd9f-xdg9j   0/1   Pending       0     56s     <none>        <none>       <none>   <none>
```

| เวลา (ในการทดลอง) | เหตุการณ์ |
|---|---|
| 12:43:21 → 12:43:31 | `docker stop` ใช้ 10 วินาที |
| +41 วินาที (12:44:12) | Node เป็น `NotReady` (control plane ไม่ได้ heartbeat) Pod เดิมยังแสดง `Running` |
| +66 วินาที (12:44:37) | ครบ `tolerationSeconds: 30` → Pod เดิม `Terminating`, ReplicaSet สร้าง Pod ใหม่ `nd-…-xdg9j` ที่ค้าง `Pending` |
| ต่อจากนั้น | Pod ใหม่ `Pending` ตลอด ไม่ไป `lab-worker2` แม้จะว่าง |

เวลา (`date` ใน shell ของ k8s-lab เป็นเวลาไทย) และจำนวนวินาทีในเครื่องนักศึกษาอาจต่างกัน

### ขั้นที่ 3: ทำไม Pod ใหม่ไปไหนไม่ได้

```bash
kubectl get node; kubectl get pod -l app=nd -o wide
kubectl get pv -o custom-columns=NAME:.metadata.name,CLAIM:.spec.claimRef.name,NODE:.spec.nodeAffinity.required.nodeSelectorTerms[0].matchExpressions[0].values[0]; kubectl describe node $N | grep -A3 Taints
```

```text
NAME                STATUS     ROLES           AGE   VERSION
lab-control-plane   Ready      control-plane   12m   v1.37.0
lab-worker          NotReady   <none>          11m   v1.37.0
lab-worker2         Ready      <none>          11m   v1.37.0
NAME                 READY   STATUS        RESTARTS   AGE     IP            NODE         NOMINATED NODE   READINESS GATES
nd-d49d6fd9f-hj8fp   1/1     Terminating   0          2m23s   10.244.2.35   lab-worker   <none>           <none>
nd-d49d6fd9f-xdg9j   0/1     Pending       0          62s     <none>        <none>       <none>           <none>
NAME                                       CLAIM     NODE
pvc-c20aba41-55db-4d7a-8003-770cdd1daa40   nd-data   lab-worker
Taints:             node.kubernetes.io/unreachable:NoExecute
                    node.kubernetes.io/unreachable:NoSchedule
Unschedulable:      false
Lease:
```

ตู้ (PV) ผูกกับ Node ที่หยุด และ Node นั้นติด taint `unreachable` สาเหตุที่ scheduler เขียนไว้อยู่ใน Event ของ Pod ใหม่ ในการทดลองนี้ `kubectl describe pod -l app=nd | grep FailedScheduling` **ไม่เจอ** บรรทัดนั้น ให้ใช้ `kubectl get events` แทน (ทำในขั้นที่ 4 ด้วยชื่อ Pod จริงของตัวเอง หรือสั่งตอนนี้ก็ได้)

```bash
kubectl get events --sort-by=.lastTimestamp | grep FailedScheduling | tail -3
```

### ขั้นที่ 4: เปิด Node กลับมา

```bash
date +%T; docker start $N; echo "started $(date +%T)"; for i in $(seq 1 30); do sleep 3; echo "--- $(date +%T)"; kubectl get node $N --no-headers; kubectl get pod -l app=nd -o wide --no-headers; kubectl get pod -l app=nd --no-headers | grep -q "1/1.*Running" && break; done
```

```text
12:45:39
lab-worker
started 12:45:39
--- 12:45:42
lab-worker   Ready   <none>   11m   v1.37.0
nd-d49d6fd9f-hj8fp   0/1   Unknown             0     2m26s   <none>   lab-worker   <none>   <none>
nd-d49d6fd9f-xdg9j   0/1   ContainerCreating   0     65s     <none>   lab-worker   <none>   <none>
--- 12:45:46
lab-worker   Ready   <none>   11m   v1.37.0
nd-d49d6fd9f-xdg9j   1/1   Running   0     69s   10.244.2.2   lab-worker   <none>   <none>
```

```bash
kubectl logs deploy/nd; kubectl get events --sort-by=.lastTimestamp | grep -E "$(kubectl get pod -l app=nd -o jsonpath='{.items[0].metadata.name}')" | tail -8
```

```text
05:43:21 start nd-d49d6fd9f-hj8fp on lab-worker
05:45:43 start nd-d49d6fd9f-xdg9j on lab-worker
75s         Normal    SuccessfulCreate          replicaset/nd-d49d6fd9f          Created pod: nd-d49d6fd9f-xdg9j
75s         Warning   FailedScheduling          pod/nd-d49d6fd9f-xdg9j           0/3 nodes are available: 1 node(s) didn't match PersistentVolume's node affinity, 2 node(s) had untolerated taint(s). preemption: 0/3 nodes are available: 3 Preemption is not helpful for scheduling.
11s         Normal    Scheduled                 pod/nd-d49d6fd9f-xdg9j           Successfully assigned default/nd-d49d6fd9f-xdg9j to lab-worker
10s         Normal    TaintManagerEviction      pod/nd-d49d6fd9f-xdg9j           Cancelling deletion of Pod default/nd-d49d6fd9f-xdg9j
9s          Normal    Pulled                    pod/nd-d49d6fd9f-xdg9j           Container image "busybox:1.36" already present on machine and can be accessed by the pod
9s          Normal    Created                   pod/nd-d49d6fd9f-xdg9j           Container created
9s          Normal    Started                   pod/nd-d49d6fd9f-xdg9j           Container started
```

- Node `Ready` ใน 3 วินาที Pod ใหม่ `Running` บน **Node เดิม** ใน ~7 วินาที Pod เก่า `Unknown` แล้วหายไป
- `boot.txt` มี 2 บรรทัด ข้อมูลเดิมอยู่ครบ (เวลาใน log เป็น UTC)
- `FailedScheduling … 1 node(s) didn't match PersistentVolume's node affinity` = `lab-worker2` ที่ไม่มีตู้, `2 node(s) had untolerated taint(s)` = control-plane และ Node ที่หยุด

### ขั้นที่ 5: เก็บกวาดและตรวจ Node

```bash
kubectl delete -f nd.yaml; sleep 4; kubectl get node; kubectl get pv,pvc; docker exec lab-worker crictl images | grep -E "postgres|som-shop"
```

```text
persistentvolumeclaim "nd-data" deleted from default namespace
deployment.apps "nd" deleted from default namespace
NAME                STATUS   ROLES           AGE   VERSION
lab-control-plane   Ready    control-plane   12m   v1.37.0
lab-worker          Ready    <none>          12m   v1.37.0
lab-worker2         Ready    <none>          12m   v1.37.0
No resources found
docker.io/library/postgres                      17.11-alpine         79bd7c99e9231       117MB
docker.io/library/som-shop-web                  1.2                  fc97d28600ddf       76.6MB
```

ต้องเห็น 3 Node `Ready` และ image ของร้านยังอยู่บน Node (การ stop/start ไม่ทำให้ image หาย) ถ้าไม่เห็นให้ทำ LAB 0 ขั้นที่ 6 ใหม่หลัง Node ครบ

### สิ่งที่เห็น

- `docker stop` Node → `NotReady` ~40–50 วินาที → ครบ tolerationSeconds → Pod ใหม่ `Pending`
- `didn't match PersistentVolume's node affinity` — ตู้ไม่ลอยข้ามเรือ Pod ใหม่รอจน Node เดิมกลับ
- `docker start` → Pod กลับมาบน Node เดิมพร้อมข้อมูลเดิม

**คำถามชวนคิด**

1. ถ้าไม่ได้ตั้ง `tolerationSeconds: 30` (ใช้ default 300) Pod ใหม่จะถูกสร้างเมื่อไรหลัง Node NotReady
2. ร้านน้องส้มใน LAB 10 ใช้ local-path เหมือนกัน ถ้า Node ที่ db อยู่ล่ม ลูกค้าจะเจออะไร และ Deployment ช่วยได้หรือไม่

---

## LAB 9: งบพื้นที่, ephemeral, subPath/readOnly/fsGroup

<p align="center" id="fig-13">
  <img src="images/13-lab9-quota-ephemeral.png" alt="รูปที่ 13 LAB 9 quota, ephemeral, mount" width="900"><br>
  <em><b>รูปที่ 13</b> LAB9: ResourceQuota storage ปฏิเสธ PVC เกินงบ (exceeded quota), ephemeral volume ได้ PVC fsg-e ที่หายพร้อม Pod, subPath/readOnly ทำงาน, fsGroup 70 ไม่เปลี่ยนเจ้าของโฟลเดอร์ local-path</em>
</p>

**เป้าหมาย:** คุมพื้นที่ต่อ namespace ด้วย ResourceQuota (ต่อจากบทที่ 4) และลองวิธีเมานต์หลายแบบในตู้เดียว (`subPath`, `readOnly`) พร้อม generic ephemeral volume และดูผลของ `fsGroup` กับ local-path

**ไฟล์ (`lab09-misc/`):** `00-ns-quota.yaml` (namespace `quota-lab` + ResourceQuota `storage`: PVC ไม่เกิน 2 ใบ, รวม 1Gi, class standard 500Mi), `pvc-400.yaml`, `pvc-200.yaml`, `pvc-100.yaml`, `pvc-10.yaml` (PVC `p400` … `p10` ใน `quota-lab`), `pod-mounts.yaml` (PVC `fsg-data` + Pod `fsg` ใน `default` รันเป็น uid/gid 70, `fsGroup: 70`, เมานต์ตู้เดียวกันที่ `/data`, `/site` (`subPath: site`), `/ro` (`readOnly`) และ ephemeral volume `e` 5Mi ที่ `/eph`)

### ขั้นที่ 1: งบพื้นที่ต่อ namespace

🐧 **ใน SSH session ของ k8s-lab**

```bash
cd /workspace/008_kubernetes_pv_pvc/02_LAB/labs/lab09-misc
kubectl apply -f 00-ns-quota.yaml; kubectl apply -f pvc-400.yaml
kubectl apply -f pvc-200.yaml; echo "exit=$?"
```

```text
namespace/quota-lab created
resourcequota/storage created
persistentvolumeclaim/p400 created
Error from server (Forbidden): error when creating "pvc-200.yaml": persistentvolumeclaims "p200" is forbidden: exceeded quota: storage, requested: standard.storageclass.storage.k8s.io/requests.storage=200Mi, used: standard.storageclass.storage.k8s.io/requests.storage=400Mi, limited: standard.storageclass.storage.k8s.io/requests.storage=500Mi
exit=1
```

`p200` ถูกปฏิเสธเพราะ 400Mi + 200Mi เกินงบของ class standard (500Mi) แม้งบรวม (1Gi) ยังพอ ถัดไปขอ 100Mi และดูงบ

```bash
kubectl apply -f pvc-100.yaml; kubectl -n quota-lab get pvc; kubectl describe quota -n quota-lab
```

```text
persistentvolumeclaim/p100 created
NAME   STATUS    VOLUME   CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
p100   Pending                                      standard       <unset>                 0s
p400   Pending                                      standard       <unset>                 1s
Name:                                                  storage
Namespace:                                             quota-lab
Resource                                               Used   Hard
--------                                               ----   ----
persistentvolumeclaims                                 2      2
requests.storage                                       500Mi  1Gi
standard.storageclass.storage.k8s.io/requests.storage  500Mi  500Mi
```

PVC ยัง `Pending` (ไม่มี Pod) แต่ถูกนับในงบแล้ว และไฟล์ไม่ได้ใส่ class แต่ถูกนับเป็น `standard` สุดท้ายขอ 10Mi

```bash
kubectl apply -f pvc-10.yaml; echo "exit=$?"
```

```text
Error from server (Forbidden): error when creating "pvc-10.yaml": persistentvolumeclaims "p10" is forbidden: exceeded quota: storage, requested: persistentvolumeclaims=1,standard.storageclass.storage.k8s.io/requests.storage=10Mi, used: persistentvolumeclaims=2,standard.storageclass.storage.k8s.io/requests.storage=500Mi, limited: persistentvolumeclaims=2,standard.storageclass.storage.k8s.io/requests.storage=500Mi
exit=1
```

ติดทั้งจำนวนใบเบิก (2/2) และงบของ class (500Mi/500Mi) ข้อความบอกครบทุกข้อที่เกิน ลบ namespace (PVC ที่ยัง Pending ไม่มี PV จึงไม่มีอะไรต้องลบบน Node)

```bash
time kubectl delete ns quota-lab
```

```text
namespace "quota-lab" deleted

real	0m10.261s
```

### ขั้นที่ 2: subPath, readOnly, fsGroup และ ephemeral ใน Pod เดียว

```bash
kubectl apply -f pod-mounts.yaml; kubectl wait --for=condition=Ready pod/fsg --timeout=90s; sleep 2; kubectl logs fsg; kubectl get pvc
```

```text
persistentvolumeclaim/fsg-data created
pod/fsg created
pod/fsg condition met
uid=70 gid=70 groups=70
drwxrwxrwx    3 0        0             4096 Oct  5 05:46 /data
drwxrwxrwx    2 0        0             4096 Oct  5 05:46 /eph
ls /data/site → page.txt
touch: /ro/x: Read-only file system
readOnly ทำงาน: เขียน /ro ไม่ได้
NAME       STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
fsg-data   Bound    pvc-597b9f67-c9c4-42fb-9bfe-dca8e2184803   10Mi       RWO            standard       <unset>                 6s
fsg-e      Bound    pvc-1421697e-9a36-4079-9e2c-846adec65f72   5Mi        RWO            standard       <unset>                 6s
```

| บรรทัด | ความหมาย |
|---|---|
| `uid=70 gid=70 groups=70` | รันเป็น uid/gid 70 ตาม `runAsUser`/`runAsGroup` |
| `drwxrwxrwx 0 0 /data` และ `/eph` | โฟลเดอร์ของตู้ยังเป็นของ root **`fsGroup: 70` ไม่มีผลกับ local-path** แต่ 0777 ทำให้ uid 70 เขียนได้ |
| `ls /data/site → page.txt` | ไฟล์ที่เขียนผ่าน `/site` (`subPath: site`) ไปอยู่ในโฟลเดอร์ย่อย `site` ของตู้ |
| `touch: /ro/x: Read-only file system` | เมานต์ `readOnly: true` เขียนไม่ได้ |
| PVC `fsg-e` 5Mi | ephemeral volume ได้ PVC ชื่อ `<pod>-<volume>` อัตโนมัติ |

> **ข้อสังเกต:** ถ้าสั่ง `kubectl logs fsg` ทันทีหลัง `wait` (ไม่มี `sleep 2`) การทดลองได้แค่บรรทัดแรก `uid=70 gid=70 groups=70` เพราะสคริปต์ยังรันไม่ถึงบรรทัดถัดไป รอ 1–2 วินาทีแล้วสั่งใหม่

ดูเจ้าของของ `fsg-e` และไฟล์บน Node (ผลด้านล่างมาจากรอบทดลองก่อนหน้าของ LAB เดียวกัน ชื่อ PV จึงต่างจากขั้นด้านบน)

```bash
kubectl get pvc fsg-e -o jsonpath="{.metadata.ownerReferences}{\"\n\"}"; N=$(kubectl get pod fsg -o jsonpath="{.spec.nodeName}"); docker exec $N sh -c "ls -lan /var/local-path-provisioner/; ls -lan /var/local-path-provisioner/*_default_fsg-data/ /var/local-path-provisioner/*_default_fsg-data/site"
```

```text
[{"apiVersion":"v1","blockOwnerDeletion":true,"controller":true,"kind":"Pod","name":"fsg","uid":"dbd236f5-6739-4039-b67c-d238aac04b97"}]
total 16
drwxr-xr-x  4 0 0 4096 Oct  5 05:46 .
drwxr-xr-x 12 0 0 4096 Oct  5 05:39 ..
drwxrwxrwx  3 0 0 4096 Oct  5 05:46 pvc-1508f6e3-bb64-4f1e-aa89-1d39a561837f_default_fsg-data
drwxrwxrwx  2 0 0 4096 Oct  5 05:46 pvc-e6b1aff0-f67c-4375-b8fc-aa2b9dc7059f_default_fsg-e
/var/local-path-provisioner/pvc-1508f6e3-bb64-4f1e-aa89-1d39a561837f_default_fsg-data/:
total 12
drwxrwxrwx 3 0 0 4096 Oct  5 05:46 .
drwxr-xr-x 4 0 0 4096 Oct  5 05:46 ..
drwxrwxrwx 2 0 0 4096 Oct  5 05:46 site

/var/local-path-provisioner/pvc-1508f6e3-bb64-4f1e-aa89-1d39a561837f_default_fsg-data/site:
total 12
drwxrwxrwx 2  0  0 4096 Oct  5 05:46 .
drwxrwxrwx 3  0  0 4096 Oct  5 05:46 ..
-rw-r--r-- 1 70 70   36 Oct  5 05:46 page.txt
```

- `fsg-e` มี ownerReferences เป็น Pod `fsg` (`controller: true`) — garbage collector จะลบตาม Pod
- โฟลเดอร์ `site` (จาก subPath) ถูกสร้างให้อัตโนมัติ ไฟล์ `page.txt` เป็นของ `70 70` แต่โฟลเดอร์เป็นของ root ทั้งหมด

### ขั้นที่ 3: ลบ Pod → ephemeral PVC หายตาม

```bash
kubectl delete pod fsg; sleep 4; kubectl get pvc; kubectl get pv
```

```text
pod "fsg" deleted from default namespace
NAME       STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
fsg-data   Bound    pvc-597b9f67-c9c4-42fb-9bfe-dca8e2184803   10Mi       RWO            standard       <unset>                 13s
NAME                                       CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS   CLAIM              STORAGECLASS   VOLUMEATTRIBUTESCLASS   REASON   AGE
pvc-597b9f67-c9c4-42fb-9bfe-dca8e2184803   10Mi       RWO            Delete           Bound    default/fsg-data   standard       <unset>                          11s
```

`fsg-e` และ PV ของมันหายไปพร้อม Pod ส่วน `fsg-data` (PVC ปกติ) ยังอยู่

### ขั้นที่ 4: เก็บกวาด

```bash
kubectl delete -f pod-mounts.yaml; sleep 4; kubectl get pvc,pv
```

```text
persistentvolumeclaim "fsg-data" deleted from default namespace
Error from server (NotFound): error when deleting "pod-mounts.yaml": pods "fsg" not found
No resources found
```

`NotFound` ของ Pod `fsg` เป็นเรื่องปกติ (ลบไปแล้วในขั้นที่ 3)

### สิ่งที่เห็น

- ResourceQuota ปฏิเสธ PVC ที่เกินจำนวนหรือเกินงบรวม/งบต่อ class (`exceeded quota: storage, …`) นับตั้งแต่ PVC ยัง Pending
- `subPath` เมานต์โฟลเดอร์ย่อย, `readOnly` → `Read-only file system`, `fsGroup` ไม่เปลี่ยนเจ้าของโฟลเดอร์ของ local-path
- ephemeral volume ได้ PVC `fsg-e` ที่มี ownerReferences ถึง Pod และหายตาม Pod

**คำถามชวนคิด**

1. ถ้า Pod `fsg` อยู่ใน `quota-lab` (ที่ใช้ PVC ครบ 2 ใบแล้ว) Pod จะถูกสร้างได้หรือไม่ เพราะ ephemeral volume สร้างอะไรขึ้นมา
2. ถ้าย้ายไปใช้ CSI driver ที่รองรับ `fsGroup` คาดว่า `ls -ldn /data` จะเปลี่ยนเป็นอย่างไร

---
