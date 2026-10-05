## 8. reclaimPolicy และ finalizers

### 8.1 Delete กับ Retain

<p align="center" id="fig-25">
  <img src="images/25-delete-vs-retain.png" alt="รูปที่ 25 Delete กับ Retain" width="900"><br>
  <em><b>รูปที่ 25</b> reclaimPolicy เมื่อลบ PVC: Delete = PV และโฟลเดอร์บน Node ถูกลบทิ้ง (ค่า default ของ standard); Retain = PV เหลือสถานะ Released ข้อมูลยังอยู่; Recycle เลิกใช้แล้ว</em>
</p>

`persistentVolumeReclaimPolicy` ของ PV บอกว่าเมื่อ **PVC ที่ผูกอยู่ถูกลบ** จะทำอะไรกับตู้

**ตารางที่ 14** reclaimPolicy

| Policy | เมื่อลบ PVC | ค่า default ของ | ผลจริงใน LAB |
|---|---|---|---|
| `Delete` | provisioner ลบ PV **และข้อมูลจริง** (local-path ลบโฟลเดอร์บน Node) | PV ที่ StorageClass สร้าง (เมื่อ class ไม่ระบุ reclaimPolicy) | LAB 6: PV `Released` 1–2 วินาทีแล้วหาย, `ls /var/local-path-provisioner/` ว่าง |
| `Retain` | PV เหลือสถานะ `Released` **ข้อมูลยังอยู่ครบ** ผู้ดูแลต้องจัดการเอง | PV ที่สร้างเองด้วยมือ | LAB 4, 6, 7, 10: PV `Released` + ไฟล์ยังอยู่บน Node |
| `Recycle` | (เลิกใช้แล้ว) เคยลบไฟล์ใน volume แล้วให้ใช้ต่อ | – | ไม่ใช้ ให้ใช้ dynamic provisioning แทน |

ผลจริงของ Delete ใน LAB 6 (ลบ Pod ที่ใช้ PVC ซึ่งถูกสั่งลบไว้แล้ว): ช่วงสั้น ๆ เห็น `Released` แล้ว PV ก็หายไปเอง ไม่ต้องตกใจกับสถานะนี้

```text
NAME                                                        CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS     CLAIM            STORAGECLASS   VOLUMEATTRIBUTESCLASS   REASON   AGE
persistentvolume/pvc-8584059b-0fd6-421f-9daa-44fd8f36a76d   10Mi       RWO            Delete           Released   default/ledger   standard       <unset>                          8s
...
No resources found
```

**เปลี่ยน policy ของ PV ที่มีอยู่แล้ว** ด้วย `kubectl patch pv` (ใช้ได้กับ PV จาก class `standard` ที่เป็น Delete เพื่อเก็บข้อมูลไว้ก่อนลบ PVC)

```bash
kubectl patch pv $PV -p '{"spec":{"persistentVolumeReclaimPolicy":"Retain"}}'
```

```text
persistentvolume/pvc-4c821b49-b44e-4818-a63e-c65943143e39 patched
NAME                                       CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS   CLAIM            STORAGECLASS   VOLUMEATTRIBUTESCLASS   REASON   AGE
pvc-4c821b49-b44e-4818-a63e-c65943143e39   10Mi       RWO            Retain           Bound    default/ledger   standard       <unset>                          2s
```

หลังลบ Pod และ PVC ตู้นี้ `Released` และไฟล์ `keepme.txt` ยังอยู่บน Node

```text
pvc-4c821b49-b44e-4818-a63e-c65943143e39   10Mi       RWO            Retain           Released   default/ledger   standard       <unset>                          10s
N=lab-worker
pvc-4c821b49-b44e-4818-a63e-c65943143e39_default_ledger
keepme เขียนเมื่อ 05:41:40
```

> **ข้อควรจำ:** Retain เก็บข้อมูลไว้ แต่ **ไม่มีใครลบให้** แม้จะลบ PV แล้วก็ตาม ใน LAB 6 ลบ PV ที่ Retain ไปแล้ว โฟลเดอร์ `pvc-…_default_ledger` ยังอยู่บน Node และใน LAB 10 ลบ namespace `som-shop` แล้ว PV ยัง `Released` ผู้ดูแลต้อง `kubectl delete pv` และลบโฟลเดอร์ (`docker exec <node> rm -rf …`) เอง

### 8.2 กู้ PV ที่ Released

<p align="center" id="fig-26">
  <img src="images/26-released-rescue.png" alt="รูปที่ 26 กู้ PV ที่ Released" width="900"><br>
  <em><b>รูปที่ 26</b> กู้ PV ที่ Released: ลบ spec.claimRef → Available → สร้าง PVC ใหม่ใส่ volumeName → Bound ข้อมูลเดิมกลับมา (ทดสอบแล้ว)</em>
</p>

PV ที่ `Released` ยังจำ `claimRef` ของ PVC ตัวเก่า (uid เดิม) ไว้ จึง **ไม่ถูกผูกกับ PVC ใหม่อัตโนมัติ แม้ PVC ใหม่จะชื่อเดิม** ผลจริงใน LAB 6: apply `pvc.yaml` ชื่อ `ledger` ซ้ำ ได้ PV ใหม่ (`pvc-9b83…`, reclaimPolicy Delete ตาม class) และ `keepme.txt` เป็นไฟล์ใหม่ (`05:41:53`) ส่วนตู้เดิมยัง `Released` อยู่ข้าง ๆ

```text
NAME                                       CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS     CLAIM            STORAGECLASS   VOLUMEATTRIBUTESCLASS   REASON   AGE
pvc-4c821b49-b44e-4818-a63e-c65943143e39   10Mi       RWO            Retain           Released   default/ledger   standard       <unset>                          15s
pvc-9b832bb3-1026-4f3b-a81e-1810820588b9   10Mi       RWO            Delete           Bound      default/ledger   standard       <unset>                          2s
keepme เขียนเมื่อ 05:41:53
```

ขั้นตอนกู้ตู้เดิม (ทดสอบแล้วทั้งใน LAB 6 และ LAB 10)

1. ลบ `spec.claimRef` ออกจาก PV → สถานะเป็น `Available`

   ```bash
   kubectl patch pv $PV --type json -p '[{"op":"remove","path":"/spec/claimRef"}]'
   ```

   ```text
   persistentvolume/pvc-4c821b49-b44e-4818-a63e-c65943143e39 patched
   NAME                                       CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS      CLAIM   STORAGECLASS   VOLUMEATTRIBUTESCLASS   REASON   AGE
   pvc-4c821b49-b44e-4818-a63e-c65943143e39   10Mi       RWO            Retain           Available           standard       <unset>                          30s
   ```

2. สร้าง PVC ที่มี `volumeName` ชี้ PV นั้น (class/โหมด/ขนาดต้องเข้ากัน) → `Bound` กับตู้เดิม และ Pod อ่านข้อมูลเดิมได้

   ```text
   NAME     STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
   ledger   Bound    pvc-4c821b49-b44e-4818-a63e-c65943143e39   10Mi       RWO            standard       <unset>                 1s
   ...
   keepme เขียนเมื่อ 05:41:40
   ```

> **ข้อควรจำ (LAB 10):** spec ของ PVC ที่ Bound แล้ว **แก้ไม่ได้** (ยกเว้น `resources.requests` และ `volumeAttributesClassName`) ถ้าสร้าง PVC กู้ตู้ด้วย `volumeName` แล้วไป `kubectl apply` ไฟล์ที่มี PVC ชื่อเดียวกันแต่ไม่มี `volumeName` จะได้ `The PersistentVolumeClaim "som-db-data" is invalid: spec: Forbidden: spec is immutable after creation except resources.requests and volumeAttributesClassName for bound claims` LAB จึง apply เฉพาะ Deployment ด้วย `-l app=som-db`

### 8.3 finalizers: คลิปแดงกันฉีกใบเบิก

<p align="center" id="fig-27">
  <img src="images/27-finalizers.png" alt="รูปที่ 27 finalizers" width="900"><br>
  <em><b>รูปที่ 27</b> finalizers kubernetes.io/pvc-protection และ pv-protection: ลบ PVC ที่ Pod ยังใช้อยู่ → ค้าง Terminating จนกว่า Pod จะเลิกใช้ กันข้อมูลหายระหว่างทำงาน</em>
</p>

finalizer คือชื่อที่ติดใน `metadata.finalizers` ของ object บอกว่า "ยังมีงานต้องทำก่อนลบจริง" (บทที่ 4 เห็นกับ namespace) PVC ทุกตัวมี `kubernetes.io/pvc-protection` และ PV มี `kubernetes.io/pv-protection` ผลจริงจาก LAB 6 เมื่อสั่งลบ PVC ที่ Pod `ledger-pod` ยังใช้อยู่

```text
persistentvolumeclaim "ledger" deleted from default namespace
NAME     STATUS        VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
ledger   Terminating   pvc-8584059b-0fd6-421f-9daa-44fd8f36a76d   10Mi       RWO            standard       <unset>                 7s
Status:        Terminating (lasts 2s)
Finalizers:    [kubernetes.io/pvc-protection]
Used By:       ledger-pod
```

PVC ค้าง `Terminating` (ข้อความ `deleted` แค่บอกว่ารับคำสั่งแล้ว) Pod ยังอ่านเขียนได้ตามปกติ เมื่อลบ Pod แล้ว finalizer จึงถูกถอดและ PVC ถูกลบจริง ส่วน PV ที่ยังผูกกับ PVC ก็ถูกกันไม่ให้ลบด้วย `kubernetes.io/pv-protection` (`["kubernetes.io/pv-protection"]`)

> **ข้อควรจำ:** ถ้า `kubectl delete pvc` แล้วค้าง ให้ดู `Used By:` ใน `describe pvc` แล้วหยุด Pod/Deployment ที่ใช้อยู่ก่อน **อย่าลบ finalizer เอง** เพราะจะทำให้ข้อมูลถูกลบขณะ Pod ยังใช้งาน

---

## 9. การขยาย PVC

<p align="center" id="fig-28">
  <img src="images/28-expansion.png" alt="รูปที่ 28 การขยาย PVC" width="900"><br>
  <em><b>รูปที่ 28</b> ขยาย PVC: แก้ requests.storage ให้ใหญ่ขึ้นได้ก็ต่อเมื่อ StorageClass มี allowVolumeExpansion: true และ driver รองรับ — standard ของ kind ถูกปฏิเสธ (Forbidden) ลดขนาดไม่ได้เสมอ</em>
</p>

การขยาย PVC คือการแก้ `spec.resources.requests.storage` ให้ใหญ่ขึ้น (`kubectl patch`, `kubectl edit` หรือแก้ไฟล์แล้ว apply) เงื่อนไขมีสองชั้น

1. **API server** ยอมรับก็ต่อเมื่อ PVC มาจาก StorageClass ที่ `allowVolumeExpansion: true`
2. **driver** ต้องขยายได้จริง (CSI driver ที่มี resizer) เมื่อขยายสำเร็จ `status.capacity` จึงเปลี่ยนตาม

ผลจริงจาก LAB 7

| ลอง | ผล |
|---|---|
| ขยาย PVC `std` (class `standard`) เป็น 20Mi | `Error from server (Forbidden): persistentvolumeclaims "std" is forbidden: only dynamically provisioned pvc can be resized and the storageclass that provisions the pvc must support resize` |
| ขยาย PVC `ex` (class `local-expand` ที่ตั้ง `allowVolumeExpansion: true`) เป็น 20Mi | `persistentvolumeclaim/ex patched` แต่ 20 วินาทีต่อมา `spec=20Mi status=10Mi`, PV ยัง `10Mi` และมี Event `ExternalExpanding  waiting for an external controller to expand this PVC` — local-path ไม่มีตัวขยาย จึงค้างแบบนี้ไปเรื่อย ๆ |
| ลด `ex` เป็น 5Mi | `The PersistentVolumeClaim "ex" is invalid: spec.resources.requests.storage: Forbidden: field can not be less than status.capacity` |

> **ข้อควรจำ:** PVC **ขยายได้ แต่ลดไม่ได้** และการตั้ง `allowVolumeExpansion: true` เป็นแค่ "ใบอนุญาต" ถ้า driver ไม่รองรับก็ไม่มีอะไรเกิดขึ้น ควรเผื่อขนาดตั้งแต่แรกเมื่อใช้ storage ที่ขยายไม่ได้

---

## 10. subPath, readOnly, fsGroup และสิทธิ์ไฟล์

### 10.1 subPath และ readOnly

<p align="center" id="fig-29">
  <img src="images/29-subpath-readonly.png" alt="รูปที่ 29 subPath และ readOnly" width="900"><br>
  <em><b>รูปที่ 29</b> subPath = เมานต์เฉพาะโฟลเดอร์ย่อยของ volume; readOnly: true = อ่านได้อย่างเดียว เขียนแล้วได้ Read-only file system</em>
</p>

volume เดียวกันเมานต์ได้หลายที่ในหลายแบบ ตัวอย่างจาก `02_LAB/labs/lab09-misc/pod-mounts.yaml`

```yaml
      volumeMounts:
        - name: data
          mountPath: /data             # ทั้งตู้
        - name: data
          mountPath: /site
          subPath: site                # เฉพาะโฟลเดอร์ย่อย site ในตู้ (ไม่มีจะถูกสร้างให้)
        - name: data
          mountPath: /ro
          readOnly: true               # ตู้เดียวกันแต่อ่านอย่างเดียว
        - name: e
          mountPath: /eph
```

ผลจริง (LAB 9): ไฟล์ที่เขียนผ่าน `/site/page.txt` ไปอยู่ใน `/data/site/` และเขียน `/ro` ไม่ได้

```text
ls /data/site → page.txt
touch: /ro/x: Read-only file system
readOnly ทำงาน: เขียน /ro ไม่ได้
```

| ฟิลด์ใน `volumeMounts` | ใช้ทำอะไร |
|---|---|
| `subPath` | ให้หลาย container/แอปใช้ PVC เดียวโดยแยกโฟลเดอร์ หรือเมานต์แค่ส่วนที่ต้องการ |
| `readOnly: true` | container ที่ควรอ่านอย่างเดียว (เช่น ตัวอ่าน log/รายงาน) กันเขียนพลาด |

### 10.2 fsGroup และสิทธิ์ไฟล์ของ postgres

<p align="center" id="fig-30">
  <img src="images/30-fsgroup-postgres.png" alt="รูปที่ 30 สิทธิ์ไฟล์ของ postgres" width="900"><br>
  <em><b>รูปที่ 30</b> สิทธิ์ไฟล์ของ postgres: รันเป็น uid 70 ต้องเป็นเจ้าของ PGDATA (โหมด 0700) — local-path สร้างโฟลเดอร์ 0777 ของ root และไม่สนใจ fsGroup จึงใช้ PGDATA เป็นโฟลเดอร์ย่อย pgdata ให้ postgres สร้างเอง</em>
</p>

`securityContext.fsGroup` ขอให้ kubelet เปลี่ยนกลุ่มเจ้าของของ volume เป็นกลุ่มที่ระบุ เพื่อให้ container ที่รันเป็น non-root เขียนได้ ได้ผลกับ `emptyDir` และ CSI driver ส่วนใหญ่ แต่ **ไม่มีผลกับ local-path** เพราะเบื้องหลังเป็น `hostPath` ผลจริงจาก LAB 9 (Pod `fsg` รันเป็น uid/gid 70 และตั้ง `fsGroup: 70`)

```text
uid=70 gid=70 groups=70
drwxrwxrwx    3 0        0             4096 Oct  5 05:46 /data
drwxrwxrwx    2 0        0             4096 Oct  5 05:46 /eph
```

โฟลเดอร์ยังเป็นของ root (`0 0`) แต่เพราะโหมดเป็น `drwxrwxrwx` (0777) uid 70 จึงยังเขียนได้ และไฟล์ที่เขียนเป็นของ `70 70` บน Node (`-rw-r--r-- 1 70 70   36 … page.txt`)

postgres มีเงื่อนไขเข้มกว่านั้น คือโฟลเดอร์ข้อมูล (PGDATA) ต้องเป็นของ uid ที่รัน postgres และมีโหมด 0700 ถ้าใช้ราก volume ที่เป็น 0777 ของ root ตรง ๆ จะเริ่มไม่ได้ ร้านน้องส้มจึงตั้ง `PGDATA` เป็น **โฟลเดอร์ย่อย** (แบบเดียวกับบทที่ 6–7) ให้ postgres สร้างเองด้วยสิทธิ์ที่ถูกต้อง (`02_LAB/som-shop-v4/k8s/10-db.yaml`)

```yaml
          env:
            - name: PGDATA           # ใช้โฟลเดอร์ย่อย pgdata (postgres ต้องการโฟลเดอร์ 0700 ของตัวเอง)
              value: /var/lib/postgresql/data/pgdata
          volumeMounts:
            - name: db-data
              mountPath: /var/lib/postgresql/data
```

ผลจริงบน Node (LAB 10 ขั้น E)

```text
N=lab-worker PV=pvc-6a5a0bc7-03be-4fd3-83ba-399ee081b07d
total 4
drwx------ 19 70 70 4096 Oct  5 05:48 pgdata
total 128
-rw------- 1 70 70     3 Oct  5 05:47 PG_VERSION
drwx------ 6 70 70  4096 Oct  5 05:47 base
drwx------ 2 70 70  4096 Oct  5 05:48 global
...
```

> **หมายเหตุ:** `fsGroupChangePolicy` (`OnRootMismatch` / `Always`) ใช้ลดเวลาที่ kubelet ไล่เปลี่ยนสิทธิ์ไฟล์ทุกไฟล์ใน volume ขนาดใหญ่ทุกครั้งที่ Pod เริ่ม มีผลเฉพาะ volume ที่รองรับ fsGroup (ไม่ได้ใช้ในบทนี้)

---

## 11. ข้อมูลผูก Node (ต่อจากบท 003)

<p align="center" id="fig-31">
  <img src="images/31-node-down-pv-affinity.png" alt="รูปที่ 31 Node ล่มเมื่อใช้ local storage" width="900"><br>
  <em><b>รูปที่ 31</b> Node ล่มเมื่อใช้ local storage: Pod ใหม่ของ Deployment วางบน Node อื่นไม่ได้ เพราะ PV มี nodeAffinity — ค้าง Pending จนกว่า Node เดิมจะกลับมา</em>
</p>

บทที่ 3 เห็นแล้วว่าเมื่อ Node ล่ม Pod ของ controller จะถูกสร้างใหม่บน Node อื่น แต่ถ้า Pod นั้นใช้ PV แบบ local (nodeAffinity ชี้ Node ที่ล่ม) Pod ใหม่ **ไปไหนไม่ได้** ผลจริงจาก LAB 8 (Deployment `nd` 1 ตัวใช้ PVC `nd-data` ลง `lab-worker` แล้ว `docker stop lab-worker`)

**ตารางที่ 15** ลำดับเหตุการณ์ในการทดลอง (นับจาก `docker stop` เสร็จ ซึ่งใช้เวลา 10 วินาที)

| เวลา | เหตุการณ์ |
|---|---|
| 0 วินาที | Node หยุดแล้ว แต่ `kubectl get node` ยังเป็น `Ready` (kubelet หยุดส่ง heartbeat) |
| ~41 วินาที | Node เป็น `NotReady` ได้ taint `node.kubernetes.io/unreachable:NoExecute` และ `NoSchedule` |
| ~66 วินาที | ครบ `tolerationSeconds: 30` → Pod เดิม `Terminating`, Pod ใหม่ `Pending` |
| `docker start` | Node `Ready` ใน 3 วินาที → Pod ใหม่ `Running` บน Node เดิมใน ~7 วินาที ข้อมูลเดิมอยู่ครบ |

```text
75s         Warning   FailedScheduling          pod/nd-d49d6fd9f-xdg9j           0/3 nodes are available: 1 node(s) didn't match PersistentVolume's node affinity, 2 node(s) had untolerated taint(s). preemption: 0/3 nodes are available: 3 Preemption is not helpful for scheduling.
```

`1 node(s) didn't match PersistentVolume's node affinity` คือ `lab-worker2` ที่ยังดีอยู่แต่ไม่มีตู้ ส่วน `2 node(s) had untolerated taint(s)` คือ control-plane กับ `lab-worker` ที่ล่ม LAB ลด `tolerationSeconds` จาก default 300 วินาทีเหลือ 30 วินาทีเพื่อไม่ต้องรอนาน

```yaml
      tolerations:
        - key: node.kubernetes.io/unreachable
          operator: Exists
          effect: NoExecute
          tolerationSeconds: 30
        - key: node.kubernetes.io/not-ready
          operator: Exists
          effect: NoExecute
          tolerationSeconds: 30
```

> **ข้อควรจำ:** PVC ไม่ได้ทำให้ข้อมูล "อยู่ทุกที่" ข้อมูลอยู่ที่ storage ของ PV ถ้า storage ผูกกับ Node (local-path, `local`, `hostPath`) แอปจะหยุดตลอดเวลาที่ Node ล่ม ระบบจริงจึงใช้ storage เครือข่าย (CSI ที่ย้ายดิสก์ไป Node ใหม่ได้) หรือทำสำเนาข้อมูลระดับแอป (เช่น replication ของฐานข้อมูล) ตัวเลขเวลาในเครื่องนักศึกษาอาจต่างจากตาราง

---

## 12. ResourceQuota ของ storage และ ephemeral volume

### 12.1 ResourceQuota ของ storage

<p align="center" id="fig-32">
  <img src="images/32-storage-quota.png" alt="รูปที่ 32 ResourceQuota ของ storage" width="900"><br>
  <em><b>รูปที่ 32</b> ResourceQuota คุมพื้นที่ต่อ namespace (ต่อบท 004): persistentvolumeclaims, requests.storage และ &lt;class&gt;.storageclass.storage.k8s.io/requests.storage — เกินแล้ว PVC ถูกปฏิเสธ exceeded quota</em>
</p>

ResourceQuota ของบทที่ 4 คุมพื้นที่เก็บข้อมูลได้ด้วย (`02_LAB/labs/lab09-misc/00-ns-quota.yaml`)

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: storage
  namespace: quota-lab
spec:
  hard:
    persistentvolumeclaims: "2"                              # ใบเบิกได้ไม่เกิน 2 ใบ
    requests.storage: 1Gi                                    # รวมทุก class ขอได้ไม่เกิน 1Gi
    standard.storageclass.storage.k8s.io/requests.storage: 500Mi   # เฉพาะ class standard ไม่เกิน 500Mi
```

| key | คุมอะไร |
|---|---|
| `persistentvolumeclaims` | จำนวน PVC ใน namespace |
| `requests.storage` | ผลรวม `requests.storage` ของทุก PVC |
| `<class>.storageclass.storage.k8s.io/requests.storage` | ผลรวมเฉพาะ PVC ของ class นั้น |
| `<class>.storageclass.storage.k8s.io/persistentvolumeclaims` | จำนวน PVC ของ class นั้น |

ผลจริงจาก LAB 9: มี `p400` (400Mi) แล้ว ขอ `p200` (200Mi) เกินงบของ class standard

```text
Error from server (Forbidden): error when creating "pvc-200.yaml": persistentvolumeclaims "p200" is forbidden: exceeded quota: storage, requested: standard.storageclass.storage.k8s.io/requests.storage=200Mi, used: standard.storageclass.storage.k8s.io/requests.storage=400Mi, limited: standard.storageclass.storage.k8s.io/requests.storage=500Mi
```

หลังสร้าง `p100` แล้ว `describe quota` เต็มทั้งจำนวนและงบของ class

```text
Resource                                               Used   Hard
--------                                               ----   ----
persistentvolumeclaims                                 2      2
requests.storage                                       500Mi  1Gi
standard.storageclass.storage.k8s.io/requests.storage  500Mi  500Mi
```

quota นับ **ตอนสร้าง PVC** (admission) แม้ PVC ยัง `Pending` (ยังไม่มี Pod) ก็นับแล้ว และ PVC ที่ไม่ใส่ class ถูกนับเป็น class `standard` เพราะ default class ถูกใส่ให้ก่อน

### 12.2 Generic ephemeral volume

<p align="center" id="fig-33">
  <img src="images/33-ephemeral-volume.png" alt="รูปที่ 33 Generic ephemeral volume" width="900"><br>
  <em><b>รูปที่ 33</b> Generic ephemeral volume: เขียน volumeClaimTemplate ใน Pod → ได้ PVC ชื่อ &lt;pod&gt;-&lt;volume&gt; จาก StorageClass และถูกลบพร้อม Pod (ทดสอบแล้ว fsg-e หายตาม Pod)</em>
</p>

ถ้าต้องการพื้นที่ชั่วคราวที่ใหญ่หรือมีคุณสมบัติของ StorageClass แต่อายุเท่า Pod (แบบ emptyDir) ใช้ volume ชนิด `ephemeral` (`02_LAB/labs/lab09-misc/pod-mounts.yaml`)

```yaml
  volumes:
    - name: e
      ephemeral:                       # generic ephemeral volume: ได้ PVC ชื่อ <pod>-<volume> = fsg-e เกิดและตายพร้อม Pod
        volumeClaimTemplate:
          spec:
            accessModes: [ReadWriteOnce]
            resources:
              requests:
                storage: 5Mi
```

Kubernetes สร้าง PVC ชื่อ `<ชื่อ Pod>-<ชื่อ volume>` (`fsg-e`) ที่มี ownerReferences ชี้ Pod เมื่อ Pod ถูกลบ garbage collector ลบ PVC ตาม (และ PV ตาม reclaimPolicy) ผลจริงจาก LAB 9

```text
[{"apiVersion":"v1","blockOwnerDeletion":true,"controller":true,"kind":"Pod","name":"fsg","uid":"dbd236f5-6739-4039-b67c-d238aac04b97"}]
```

หลัง `kubectl delete pod fsg` เหลือแค่ `fsg-data` (PVC ปกติ) ส่วน `fsg-e` หายไป

```text
NAME       STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
fsg-data   Bound    pvc-597b9f67-c9c4-42fb-9bfe-dca8e2184803   10Mi       RWO            standard       <unset>                 13s
```

> **ข้อควรจำ:** PVC ของ ephemeral volume เป็น PVC จริง จึง **ถูกนับใน ResourceQuota** ของ namespace ด้วย

---

## 13. Backup และ snapshot (ปูทาง)

<p align="center" id="fig-34">
  <img src="images/34-backup-snapshot.png" alt="รูปที่ 34 PV ไม่ใช่ backup" width="900"><br>
  <em><b>รูปที่ 34</b> PV ไม่ใช่ backup: Retain กันลบพลาดได้แต่ Node พัง/ดิสก์เสียข้อมูลก็หาย — ใช้ pg_dump สำรองระดับแอป และ VolumeSnapshot (ต้องมี CSI ที่รองรับ) สำรองระดับดิสก์</em>
</p>

PV ทำให้ข้อมูลอยู่รอดเมื่อ Pod เปลี่ยน แต่ข้อมูลยังมี **สำเนาเดียว** อยู่บน storage ของ PV ถ้าดิสก์เสีย Node พัง หรือแอปเขียนข้อมูลผิด (เช่น ขั้น F ของ LAB 10 ที่ postgres สองตัวเขียนทับกัน) ข้อมูลก็เสียหายไปด้วย Retain ช่วยได้แค่กรณี "ลบ PVC พลาด"

**ตารางที่ 16** วิธีสำรองข้อมูล (แนวคิด — ไม่ได้อยู่ในขั้นตอน LAB)

| วิธี | ระดับ | ต้องมีอะไร | หมายเหตุ |
|---|---|---|---|
| `pg_dump` / `pg_dumpall` (หรือเครื่องมือของฐานข้อมูลนั้น) | แอป | เข้าถึงฐานข้อมูลได้ | ได้ข้อมูลที่สอดคล้องกัน นำไปกู้ในคลัสเตอร์อื่นได้ ควรเก็บไฟล์ไว้นอกคลัสเตอร์ |
| VolumeSnapshot + VolumeSnapshotClass | ดิสก์ | CSI driver ที่รองรับ snapshot + snapshot controller และ CRD | kind ไม่มี snapshot controller/CSI จึงทดลองในบทนี้ไม่ได้ |
| สำรองทั้งคลัสเตอร์ด้วยเครื่องมือภายนอก | object + ดิสก์ | ติดตั้งเครื่องมือเพิ่ม | อยู่นอกขอบเขตวิชา |

ตัวอย่างแนวคิดการ dump ฐานข้อมูลร้านออกมาเป็นไฟล์บนเครื่องที่รัน kubectl (ไม่ได้อยู่ใน LAB)

```bash
kubectl -n som-shop exec deploy/som-db -- pg_dump -U som -d catshop > catshop-backup.sql
```

---

## 14. ฐานข้อมูลกับ Deployment + PVC: ข้อควรระวัง

### 14.1 postgres 2 ตัวบนโฟลเดอร์เดียว (ผลทดลองจริง)

<p align="center" id="fig-35">
  <img src="images/35-two-postgres-one-folder.png" alt="รูปที่ 35 postgres 2 ตัวบนโฟลเดอร์เดียว" width="900"><br>
  <em><b>รูปที่ 35</b> ผลทดสอบจริง: Deployment db replicas 2 + PVC RWO → Pod ทั้งคู่ลงเรือลำเดียวกันและเปิด postgres บนโฟลเดอร์เดียวกัน → ออเดอร์แยกกันแล้วหาย (บางครั้งพัง PANIC)</em>
</p>

Deployment มี Pod template เดียว ทุก Pod จึงอ้าง `claimName: som-db-data` เดียวกัน ถ้าสั่ง `kubectl -n som-shop scale deploy/som-db --replicas=2` กับ PVC แบบ RWO จะไม่มีอะไรห้าม เพราะ RWO กันแค่ "ต่าง Node" ผลจริงจาก LAB 10 ขั้น F

1. Pod ตัวที่ 2 ถูกวางบน **Node เดียวกัน** (ตาม nodeAffinity ของ PV) และ `Running 1/1` ทั้งคู่ อยู่ใน EndpointSlice ของ Service `som-db` ทั้งคู่ (`ready=true`)
2. postgres ตัวที่ 2 เปิดโฟลเดอร์ที่ตัวแรกยังใช้อยู่ และคิดว่าเครื่องดับกะทันหัน

   ```text
   2026-10-05 05:48:11.148 UTC [26] LOG:  database system was not properly shut down; automatic recovery in progress
   ...
   2026-10-05 05:48:11.192 UTC [1] LOG:  database system is ready to accept connections
   ```

   (ไม่มีอะไรกันได้ เพราะ container ทั้งสองอยู่คนละ PID/IPC namespace จึงมองไม่เห็นกันแม้ใช้โฟลเดอร์เดียวกัน)
3. สั่งซื้อเพิ่ม 3 รายการ หน้าเว็บเห็น `orders=6` แต่ฐานข้อมูลสองตัวเห็นไม่ตรงกัน และ psql ผ่าน Service ได้คำตอบสลับไปมาตาม Pod ที่ถูกสุ่ม

   ```text
   pod/som-db-7b786655f5-mkhsg orders=3
   pod/som-db-7b786655f5-phtbj orders=6
   ```

   ```text
   10.244.2.20|6
   10.244.2.20|6
   10.244.2.21|3
   10.244.2.21|3
   ...
   ```

4. scale กลับเป็น 1 ตัว ตัวที่เหลือทำงานต่อราว 35 วินาที (postgres ตรวจ lock file ทุกนาที) แล้วหยุดตัวเอง

   ```text
   2026-10-05 05:49:00.010 UTC [1] LOG:  could not open file "postmaster.pid": No such file or directory
   2026-10-05 05:49:00.010 UTC [1] LOG:  performing immediate shutdown because data directory lock file is invalid
   ```

   kubelet เริ่ม container ใหม่ และอ่านข้อมูลจากดิสก์ได้ **`orders=3` — ออเดอร์ 3 รายการหายไป** รอบทดลองซ้ำอีก 2 รอบได้ผลเดียวกัน (6 → 3) และมี `CrashLoopBackOff` ชั่วครู่ราว 10–24 วินาทีก่อนกลับมา Running เอง ส่วนในการตรวจสอบก่อนเขียนบท (pre-check) มีรอบที่หนักกว่านั้น คือ postgres เริ่มไม่ได้อีกเลยด้วย `PANIC: could not locate a valid checkpoint record` และค้าง `CrashLoopBackOff`

**ผลไม่แน่นอน แต่เสียหายทุกครั้ง** นี่คือเหตุผลที่ไฟล์ของร้านเขียนคอมเมนต์ไว้ว่า `replicas ต้องเป็น 1`

### 14.2 วิธีกัน: replicas 1 + Recreate + ReadWriteOncePod

<p align="center" id="fig-36">
  <img src="images/36-recreate-rwop-guard.png" alt="รูปที่ 36 วิธีกัน db สองตัว" width="900"><br>
  <em><b>รูปที่ 36</b> วิธีกัน: db ต้อง replicas 1 + strategy Recreate (ไม่มีช่วงสองตัวพร้อมกัน) และใช้ ReadWriteOncePod ให้ระบบกันตัวที่ 2 — RWOP + RollingUpdate จะค้าง (Pod ใหม่ Pending รอตัวเก่า)</em>
</p>

**ตารางที่ 17** สามชั้นของการกัน postgres สองตัว

| ชั้น | ตั้งค่า | กันอะไร | ข้อจำกัด |
|---|---|---|---|
| 1 | `replicas: 1` | ไม่ตั้งใจเปิดสองตัว | คน (หรือเครื่องมือ) ยัง scale ได้ |
| 2 | `strategy: Recreate` | ระหว่าง rollout ไม่มีตัวเก่ากับตัวใหม่พร้อมกัน (บทที่ 7) | มีช่วงสั้น ๆ ที่ไม่มี db |
| 3 | PVC `accessModes: [ReadWriteOncePod]` | ระบบไม่ยอมให้ Pod ตัวที่ 2 ใช้ตู้ | storage ต้องรองรับ RWOP (local-path รองรับ) |

ผลจริงจาก LAB 10 ขั้น H (`k8s-retain/10-db.yaml` ใช้ RWOP): scale เป็น 2 แล้ว Pod ที่ 2 ค้าง `Pending` ร้านยังขายปกติ

```text
  Warning  FailedScheduling  10s   default-scheduler  0/3 nodes are available: 1 node(s) had untolerated taint(s), 2 node(s) unavailable due to PersistentVolumeClaim with ReadWriteOncePod access mode already in-use by another pod. preemption: 0/3 nodes are available: 1 Preemption is not helpful for scheduling, 2 No preemption victims found for incoming pod.
NAME     READY   UP-TO-DATE   AVAILABLE   AGE
som-db   1/2     2            1           37s
```

RWOP ต้องคู่กับ Recreate เสมอ ใน pre-check ใช้ RWOP กับ RollingUpdate แล้ว Pod ใหม่ (ที่ RollingUpdate สร้างก่อนปิดตัวเก่า) ค้าง `Pending` รอตัวเก่าซึ่งไม่ถูกปิด `rollout status` จึงค้างที่ `1 old replicas are pending termination...` ไฟล์ `k8s-retain/10-db.yaml` จึงเขียนไว้ว่า `Recreate จำเป็นมากกับ RWOP`

> **ข้อควรจำ:** ทั้งสามชั้นทำให้ db **ปลอดภัยเมื่อมีตัวเดียว** แต่ไม่ได้ทำให้ db มีหลายตัวได้ การมีฐานข้อมูลหลายตัวต้องให้แต่ละตัวมีตู้ของตัวเองและชื่อที่คงที่ ซึ่ง Deployment ทำให้ไม่ได้ (หัวข้อ 15.3)

---

## 15. สรุปและบทถัดไป

### 15.1 ตารางสรุป

<p align="center" id="fig-37">
  <img src="images/37-summary-table.png" alt="รูปที่ 37 ตารางสรุป" width="900"><br>
  <em><b>รูปที่ 37</b> ตารางสรุป: emptyDir / hostPath / PVC+static PV / PVC+StorageClass เทียบอายุข้อมูล, ใครสร้าง, ผูก Node ไหม, เหมาะกับอะไร</em>
</p>

**ตารางที่ 18** เลือกที่เก็บข้อมูล

| | `emptyDir` | `hostPath` | PVC + static PV | PVC + StorageClass |
|---|---|---|---|---|
| อายุข้อมูล | เท่า Pod | เท่า Node (ไม่มีใครลบ) | ตาม PV (มักเป็น Retain) | ตาม reclaimPolicy ของ class (default Delete) |
| ใครสร้างที่เก็บ | kubelet | มีอยู่บน Node / kubelet สร้าง | ผู้ดูแลสร้าง PV เอง | provisioner สร้างอัตโนมัติ |
| ผูก Node | ✅ (อยู่บน Node ของ Pod) | ✅ | ขึ้นกับชนิด (hostPath/local ✅, NFS/CSI เครือข่าย ❌) | ขึ้นกับ provisioner (local-path ✅) |
| Pod Security restricted | อนุญาต | ห้าม | อนุญาต (Pod ใช้ PVC) | อนุญาต |
| เหมาะกับ | cache, ไฟล์ชั่วคราว, แชร์ไฟล์ใน Pod | agent ระดับ Node, ทดลอง | ดิสก์/share ที่มีอยู่แล้ว, กู้ข้อมูลเดิม | ฐานข้อมูลและข้อมูลถาวรทั่วไป (ค่าเริ่มต้น) |
| ในบทนี้ | LAB 1, ร้านบทที่ 7 | LAB 2 | LAB 4 | LAB 3, 5–10 |

### 15.2 สรุปบท

1. **อายุข้อมูล:** ไฟล์ใน container < `emptyDir` (เท่า Pod) < PV (ไม่ขึ้นกับ Pod) `hostPath` ผูก Node และถูก Pod Security restricted ห้าม
2. **PV / PVC / StorageClass:** PV และ StorageClass เป็น cluster-scoped (ผู้ดูแล) PVC อยู่ใน namespace (นักพัฒนา) Pod อ้างแค่ `claimName`
3. **Static:** PV `Available` → PVC ที่ตรงเงื่อนไข → `Bound` ได้ตู้ใหญ่กว่าได้ `storageClassName: ""` = ไม่ใช้ class จองตู้ด้วย `claimRef` (PV) หรือ `volumeName` (PVC)
4. **Dynamic:** StorageClass + provisioner สร้าง PV `pvc-<uid>` ให้ `standard` ของ kind = local-path (โฟลเดอร์ `/var/local-path-provisioner/pvc-<uid>_<ns>_<pvc>` + hostPath + nodeAffinity)
5. **accessModes** เป็นคุณสมบัติของ storage RWO = Node เดียว (หลาย Pod ได้) RWOP = Pod เดียว local-path ไม่รองรับ RWX/Block และไม่บังคับขนาด
6. **WaitForFirstConsumer** รอ scheduler เลือก Node ก่อนสร้างตู้ PVC `Pending` ระหว่างรอเป็นเรื่องปกติ `Immediate` ใช้กับ local-path ไม่ได้
7. **reclaimPolicy:** Delete ลบ PV + ข้อมูล, Retain เหลือ `Released` (ผู้ดูแลต้องลบเอง) กู้ด้วยการลบ `claimRef` + PVC ที่มี `volumeName` PVC ชื่อเดิมไม่ได้ตู้เดิมอัตโนมัติ
8. **finalizers** `pvc-protection`/`pv-protection` กันลบระหว่างใช้งาน (ค้าง `Terminating`)
9. **ขยายได้ ลดไม่ได้** ต้องมี `allowVolumeExpansion: true` + driver ที่ขยายได้จริง
10. **subPath/readOnly** ใช้ได้กับทุก volume, `fsGroup` ไม่มีผลกับ local-path postgres จึงใช้ PGDATA เป็นโฟลเดอร์ย่อย
11. **local storage ผูก Node:** Node ล่ม → Pod ใหม่ `Pending` (`didn't match PersistentVolume's node affinity`) จน Node กลับ
12. **quota/ephemeral:** ResourceQuota คุมจำนวนและขนาด PVC ต่อ class, ephemeral volume ได้ PVC ที่ตายพร้อม Pod
13. **PV ไม่ใช่ backup** และ **db บน Deployment ต้อง `replicas: 1` + `Recreate` (+ RWOP)** scale เป็น 2 แล้วข้อมูลเสียจริง

<p align="center" id="fig-38">
  <img src="images/38-command-cheatsheet.png" alt="รูปที่ 38 คำสั่งที่ใช้บ่อย" width="900"><br>
  <em><b>รูปที่ 38</b> คำสั่งที่ใช้บ่อย: kubectl get sc,pv,pvc / describe pvc / patch pv reclaimPolicy / ดูโฟลเดอร์บน Node ด้วย docker exec</em>
</p>

**ตารางที่ 19** คำสั่งที่ใช้ในบทนี้

| คำสั่ง | ใช้ทำอะไร |
|---|---|
| `kubectl get sc` | ดู StorageClass และ default class |
| `kubectl get pv` / `kubectl get pvc -A` (`-o wide`) | ดูตู้และใบเบิก สถานะ ขนาด class |
| `kubectl describe pvc <ชื่อ>` | ดู Events (สาเหตุที่ Pending), `Used By`, Finalizers, annotation `selected-node` |
| `kubectl get pv <ชื่อ> -o yaml` | ดู `hostPath`, `nodeAffinity`, `claimRef`, reclaimPolicy |
| `kubectl get pvc <ชื่อ> -o jsonpath='{.spec.volumeName}'` | หาชื่อ PV ของ PVC |
| `kubectl patch pv <ชื่อ> -p '{"spec":{"persistentVolumeReclaimPolicy":"Retain"}}'` | เปลี่ยน PV เป็น Retain ก่อนลบ PVC |
| `kubectl patch pv <ชื่อ> --type json -p '[{"op":"remove","path":"/spec/claimRef"}]'` | ทำ PV `Released` ให้เป็น `Available` |
| `kubectl patch pvc <ชื่อ> -p '{"spec":{"resources":{"requests":{"storage":"20Mi"}}}}'` | ลองขยาย PVC |
| `kubectl describe quota -n <ns>` | ดูงบ storage ที่ใช้ไป |
| `docker exec <node> ls -la /var/local-path-provisioner/` | ดูโฟลเดอร์ของตู้บน Node (เฉพาะคลัสเตอร์ kind) |

### 15.3 ปัญหาที่ยังเหลือและบทถัดไป

<p align="center" id="fig-39">
  <img src="images/39-next-statefulset.png" alt="รูปที่ 39 ปิดบทและบทถัดไป" width="900"><br>
  <em><b>รูปที่ 39</b> ปิดบท: Deployment ให้ทุก Pod ใช้ใบเบิกใบเดียวกัน จึงขยาย db ไม่ได้ — บทหน้า StatefulSet ให้ Pod มีชื่อเลขลำดับคงที่และตู้เซฟประจำตัว</em>
</p>

ตอนจบ LAB 10 ร้านน้องส้ม **จำได้แล้ว** ลบ Pod db, `rollout restart` db หรือลบ Deployment db แล้ว apply ใหม่ ออเดอร์ก็ยังอยู่ และไม่ต้อง restart web แบบบทที่ 7 อีก แต่การทดลองในบทนี้ก็เผยข้อจำกัดของการรันฐานข้อมูลด้วย Deployment

| ปัญหาที่ยังเหลือ | หลักฐานจากบทนี้ | บทที่ 9 StatefulSet แก้อย่างไร |
|---|---|---|
| **db ขยายเป็นหลายตัวด้วย Deployment ไม่ได้** — Pod template เดียว ทุก Pod อ้าง `claimName` เดียวกัน | scale `som-db` เป็น 2 → postgres สองตัวแชร์ PVC เดียว ออเดอร์ 6 → 3 / `lock file is invalid` / PANIC; ใช้ RWOP ก็ได้แค่ Pod ที่ 2 `Pending` | `volumeClaimTemplates` สร้าง **PVC ประจำตัวทุก Pod** (ตู้เซฟคนละใบ) |
| **ชื่อ Pod สุ่ม** ไม่รู้ว่าตัวไหนคือตัวหลัก และชื่อเปลี่ยนทุกครั้งที่ถูกสร้างใหม่ | `som-db-7b786655f5-tk2bn` → `som-db-7b786655f5-zdw4m` → `som-db-bb9948676-hgt7s` | **ชื่อคงที่ตามเลขลำดับ** (`<ชื่อ>-0`, `<ชื่อ>-1`, …) Pod ใหม่ได้ชื่อเดิมและตู้เดิม |
| ลำดับการเปิด/ปิดไม่แน่นอน | ReplicaSet สร้าง/ลบ Pod พร้อมกัน | เปิดและปิดทีละตัวตามลำดับ |
| ข้อมูลผูก Node เมื่อใช้ local storage | LAB 8: Node ล่มแล้ว Pod ใหม่ `Pending` | (StatefulSet ไม่ได้แก้เรื่องนี้โดยตรง — ต้องใช้ storage เครือข่ายหรือ replication ระดับแอป) |

บทถัดไปจะให้ครัวกลางของน้องส้มมี **ชื่อคงที่และตู้เซฟประจำตัวทุก Pod** ด้วย StatefulSet และใช้ความรู้เรื่อง PVC/StorageClass ทั้งหมดของบทนี้ต่อ รหัสผ่านใน YAML (ConfigMap/Secret) และทางเข้าด้วยชื่อโดเมน (Ingress) ยังเป็นเนื้อหาบทหลัง

---

## 16. คำถามทบทวน

**1. ใน LAB 1 หลังทำให้ container ของ `cache-demo` restart ไฟล์ `/cache/x.txt`, `/ram/r.txt` และ `/tmp/y.txt` อยู่หรือหาย และถ้าลบ Pod แล้วสร้างใหม่จะเป็นอย่างไร**

<details>
<summary>แนวคำตอบ</summary>

หลัง container restart (`RESTARTS 1`) `/cache/x.txt` และ `/ram/r.txt` ยังอยู่ เพราะ `emptyDir` (ทั้งบนดิสก์และ `medium: Memory`) ผูกกับ Pod ไม่ใช่ container ส่วน `/tmp/y.txt` อยู่ในระบบไฟล์ของ container จึงหายเมื่อ container เริ่มใหม่ `boot.log` จึงมี 2 บรรทัด เมื่อลบ Pod แล้วสร้างใหม่ `emptyDir` ทั้งสองถูกลบไปกับ Pod เดิม Pod ใหม่ได้โฟลเดอร์ว่าง (`boot.log` เหลือบรรทัดเดียว `x.txt` ไม่มี)
</details>

**2. ทำไม `kubectl exec cache-demo -- kill 1` จึงไม่ทำให้ container restart และ LAB ใช้วิธีใดแทน**

<details>
<summary>แนวคำตอบ</summary>

process ที่เป็น PID 1 ใน container (ที่นี่คือ `sh`) ไม่ถูกปิดด้วยสัญญาณที่ไม่มี handler ตามกติกาของ Linux สำหรับ init process ใน namespace ของตัวเอง ทั้ง `kill 1` และ `kill -9 1` จากใน container จึงไม่มีผล (RESTARTS ยังเป็น 0) LAB จึงเขียนสคริปต์ให้วนรอไฟล์ `/tmp/stop` เมื่อสั่ง `touch /tmp/stop` loop จบแล้ว `exit 1` kubelet จึงเริ่ม container ใหม่ และเพราะ `/tmp/stop` อยู่ในระบบไฟล์ของ container จึงหายไปเองหลัง restart ไม่วนซ้ำ
</details>

**3. ทำไม Pod Security ระดับ restricted จึงห้าม `hostPath` แต่อนุญาต `persistentVolumeClaim` ทั้งที่ PV ของ local-path ก็เป็น hostPath ข้างใน**

<details>
<summary>แนวคำตอบ</summary>

`hostPath` ใน Pod ให้ผู้เขียน Pod เลือก path ใดก็ได้บน Node รวมถึง path สำคัญของระบบ จึงอ่าน/แก้ไฟล์ของ Node ได้ ส่วน PVC ผู้เขียน Pod ได้แค่ "ใบเบิก" PV ถูกสร้างโดยผู้ดูแลหรือ provisioner ซึ่งกำหนด path ที่ปลอดภัย (`/var/local-path-provisioner/pvc-…`) เอง ผู้ใช้ทั่วไปจึงควบคุม path บน Node ไม่ได้ ข้อความใน LAB 2 ระบุ `restricted volume types (volume "host" uses restricted volume type "hostPath")`
</details>

**4. อธิบายว่าอะไรเป็น cluster-scoped และอะไรอยู่ใน namespace ระหว่าง PV, PVC, StorageClass และผลที่เห็นเมื่อลบ namespace `som-shop` ใน LAB 10 ขั้น I**

<details>
<summary>แนวคำตอบ</summary>

PV และ StorageClass เป็น cluster-scoped ส่วน PVC (และ Pod) อยู่ใน namespace เมื่อลบ `som-shop` PVC `som-db-data` ถูกลบตาม namespace แต่ PV ที่ reclaimPolicy เป็น Retain ไม่ได้อยู่ใน namespace จึงยังอยู่ในสถานะ `Released` พร้อมโฟลเดอร์บน Node และ StorageClass `standard-retain` ก็ยังอยู่ ต้อง `kubectl delete pv`, ลบโฟลเดอร์บน Node และ `kubectl delete sc standard-retain` เอง
</details>

**5. PVC `manual-claim` ขอ 50Mi และ `storageClassName: ""` ทำไมคอลัมน์ CAPACITY จึงเป็น 100Mi และถ้าลบบรรทัด `storageClassName: ""` ออกจะเกิดอะไรขึ้น**

<details>
<summary>แนวคำตอบ</summary>

PV ที่ตรงเงื่อนไข (class ว่างเหมือนกัน, RWO, ขนาด ≥ 50Mi) มีตัวเดียวคือ `pv-manual` 100Mi PV ผูกกับ PVC ได้ทั้งตัว CAPACITY ของ PVC จึงแสดงขนาดจริงของ PV คือ 100Mi ถ้าไม่ใส่ `storageClassName` เลย admission จะใส่ default class (`standard`) ให้ PVC จะไม่จับกับ `pv-manual` (class ไม่ตรง) แต่จะรอ Pod แล้วให้ local-path สร้างตู้ใหม่แทน
</details>

**6. ทำไม PVC `notes` ในคลัสเตอร์ kind จึง `Pending` ทันทีหลังสร้าง และเมื่อไรจึงเป็น `Bound` ดูได้อย่างไรว่าตู้ถูกสร้างบน Node ไหน**

<details>
<summary>แนวคำตอบ</summary>

class `standard` เป็น `volumeBindingMode: WaitForFirstConsumer` PVC จึงรอจนมี Pod ตัวแรกใช้ (Event `waiting for first consumer to be created before binding`) เมื่อสร้าง Pod `writer` scheduler เลือก Node ให้ Pod แล้วเขียน annotation `volume.kubernetes.io/selected-node: lab-worker` ลงใน PVC provisioner สร้างโฟลเดอร์และ PV บน Node นั้น (`ProvisioningSucceeded`) แล้ว PVC จึง `Bound` ดู Node ได้จาก annotation นั้น หรือจาก `nodeAffinity` ใน `kubectl get pv <ชื่อ> -o yaml`
</details>

**7. Pod `rwo-a` และ `rwo-b` ใช้ PVC RWO เดียวกันและ Running ทั้งคู่ ขัดกับความหมายของ ReadWriteOnce หรือไม่ ถ้าต้องการให้ Pod ที่ 2 ใช้ไม่ได้ต้องทำอย่างไร**

<details>
<summary>แนวคำตอบ</summary>

ไม่ขัด เพราะ RWO หมายถึงเมานต์แบบอ่านเขียนได้จาก **Node เดียว** Pod หลายตัวบน Node เดียวกันใช้ร่วมกันได้ scheduler ส่ง `rwo-b` ไป `lab-worker` เดียวกับ `rwo-a` ตาม nodeAffinity ของ PV ถ้าต้องการให้มีผู้ใช้ได้ Pod เดียวต้องใช้ `ReadWriteOncePod` Pod ตัวที่ 2 จะค้าง `Pending` ด้วยข้อความ `PersistentVolumeClaim with ReadWriteOncePod access mode already in-use by another pod`
</details>

**8. PVC ที่ขอ `ReadWriteMany` ใน LAB 5 ค้าง Pending ดูสาเหตุจากที่ไหน และถ้าระบบจริงต้องการ RWX ต้องทำอย่างไร**

<details>
<summary>แนวคำตอบ</summary>

Pod `use-rwx` ไม่มี Event เลย ต้องดูที่ `kubectl describe pvc shared` ซึ่งมี `ProvisioningFailed … NodePath only supports ReadWriteOnce and ReadWriteOncePod (1.22+) access modes` แปลว่า local-path ทำ RWX ไม่ได้ (โฟลเดอร์บน Node เดียวเข้าถึงจากหลาย Node ไม่ได้) ระบบจริงต้องใช้ storage ที่รองรับ RWX เช่น NFS, CephFS หรือระบบไฟล์เครือข่ายของคลาวด์ ผ่าน CSI driver และ StorageClass ของ driver นั้น
</details>

**9. ใน LAB 6 ทำไม apply `pvc.yaml` ชื่อ `ledger` ซ้ำแล้วไม่ได้ตู้เดิมที่ Retain ไว้ และต้องทำอย่างไรจึงจะได้ข้อมูลเดิมกลับมา**

<details>
<summary>แนวคำตอบ</summary>

PV ที่ `Released` ยังมี `claimRef` ชี้ PVC ตัวเก่า (uid เดิม) PVC ใหม่แม้ชื่อเดิมก็มี uid ใหม่ จึงจับกับ PV นั้นไม่ได้ และเพราะ PVC ใช้ class `standard` provisioner จึงสร้างตู้ใหม่ (`pvc-9b83…`) ให้ วิธีกู้คือ (1) `kubectl patch pv <PV> --type json -p '[{"op":"remove","path":"/spec/claimRef"}]'` ให้ PV เป็น `Available` (2) สร้าง PVC ที่ระบุ `volumeName: <PV>` (`pvc-reuse.yaml` ผ่าน `sed`) → `Bound` กับตู้เดิม และ Pod อ่าน `keepme เขียนเมื่อ 05:41:40` เดิมได้
</details>

**10. สั่ง `kubectl delete pvc ledger` แล้ว PVC ค้าง `Terminating` เกิดจากอะไร ควรแก้อย่างไร**

<details>
<summary>แนวคำตอบ</summary>

PVC มี finalizer `kubernetes.io/pvc-protection` และยังมี Pod ใช้อยู่ (`Used By: ledger-pod`) Kubernetes จึงยังไม่ลบจริงเพื่อไม่ให้ข้อมูลหายระหว่างที่ Pod ทำงาน วิธีแก้คือหยุด/ลบ Pod (หรือ scale Deployment ที่ใช้ PVC เป็น 0) เมื่อไม่มีผู้ใช้ finalizer จะถูกถอดและ PVC ถูกลบเอง ไม่ควรลบ finalizer ด้วยมือ
</details>

**11. ตั้ง StorageClass `local-expand` ให้ `allowVolumeExpansion: true` แล้ว patch PVC `ex` เป็น 20Mi สำเร็จ ทำไม CAPACITY ยังเป็น 10Mi และถ้าลดเป็น 5Mi จะเกิดอะไร**

<details>
<summary>แนวคำตอบ</summary>

`allowVolumeExpansion: true` ทำให้ API server ยอมรับการแก้ `spec` (จึง `patched` และ `spec=20Mi`) แต่การขยายจริงต้องมี controller ของ driver มาขยาย Event `ExternalExpanding … waiting for an external controller to expand this PVC` บอกว่ากำลังรอ local-path ไม่มีตัวขยาย `status.capacity` และ PV จึงค้าง 10Mi การลดขนาดถูกปฏิเสธเสมอ `spec.resources.requests.storage: Forbidden: field can not be less than status.capacity`
</details>

**12. ใน LAB 8 หลัง `docker stop` Node ที่ Pod `nd` อยู่ Pod ใหม่ค้าง Pending ด้วยข้อความอะไร ทำไมไม่ย้ายไป `lab-worker2` ที่ยังดีอยู่ และระบบจริงแก้ปัญหานี้อย่างไร**

<details>
<summary>แนวคำตอบ</summary>

`0/3 nodes are available: 1 node(s) didn't match PersistentVolume's node affinity, 2 node(s) had untolerated taint(s)` PV ของ local-path มี `nodeAffinity` ชี้ Node ที่ล่ม เพราะข้อมูลเป็นโฟลเดอร์บน Node นั้น `lab-worker2` ไม่มีข้อมูลจึงถูกตัดออก ส่วน control-plane และ Node ที่ล่มมี taint Pod จึงรอจน `docker start` แล้วกลับมา Running บน Node เดิมพร้อมข้อมูลเดิม ระบบจริงใช้ storage เครือข่ายที่ย้ายดิสก์ไป Node ใหม่ได้ หรือทำ replication ระดับแอป
</details>

**13. ResourceQuota ใน `quota-lab` มี `p400` และ `p100` แล้ว ทำไม `p10` (10Mi) จึงถูกปฏิเสธทั้งที่ `requests.storage` รวมยังใช้แค่ 500Mi จาก 1Gi**

<details>
<summary>แนวคำตอบ</summary>

quota มีหลายข้อพร้อมกัน `p10` ติด `persistentvolumeclaims: "2"` (มี 2 ใบแล้ว) และ `standard.storageclass.storage.k8s.io/requests.storage: 500Mi` (ใช้ครบ 500Mi แล้ว) ข้อความ error ระบุทั้งสองข้อ `requested: persistentvolumeclaims=1,standard.storageclass.storage.k8s.io/requests.storage=10Mi, used: persistentvolumeclaims=2,…=500Mi, limited: persistentvolumeclaims=2,…=500Mi` PVC ต้องผ่านทุกข้อจึงจะถูกสร้าง
</details>

**14. ทำไม `fsGroup: 70` จึงไม่ทำให้โฟลเดอร์ของ PVC จาก local-path เป็นของกลุ่ม 70 และร้านน้องส้มทำอย่างไรให้ postgres ใช้ PVC ได้**

<details>
<summary>แนวคำตอบ</summary>

kubelet เปลี่ยนสิทธิ์ตาม `fsGroup` ให้เฉพาะ volume ที่รองรับ (emptyDir, CSI ส่วนใหญ่) PV ของ local-path เป็น hostPath จึงไม่ถูกเปลี่ยน `ls -ldn /data` ยังเป็น `drwxrwxrwx 0 0` แต่ 0777 ทำให้ทุก uid เขียนได้ ร้านตั้ง `PGDATA=/var/lib/postgresql/data/pgdata` เป็นโฟลเดอร์ย่อย postgres (uid 70) จึงสร้างโฟลเดอร์ `pgdata` เองเป็น `drwx------ 70 70` ตามที่ postgres ต้องการ
</details>

**15. ถ้าเพื่อนเสนอให้ scale `som-db` เป็น 2 เพื่อให้ร้านทนขึ้น จะอธิบายผลจาก LAB 10 ขั้น F อย่างไร และควรตั้งค่าอะไรเพื่อกันพลาด**

<details>
<summary>แนวคำตอบ</summary>

Deployment ให้ทุก Pod ใช้ PVC เดียวกัน PVC เป็น RWO Pod ตัวที่ 2 จึงลง Node เดียวกันและเปิด postgres บนโฟลเดอร์เดียวกัน (`not properly shut down; automatic recovery in progress`) ทั้งคู่อยู่หลัง Service ข้อมูลที่เห็นแยกกัน (6 กับ 3) และหลัง scale กลับ postgres ตัวที่เหลือหยุดเพราะ `lock file is invalid` แล้วเริ่มใหม่ได้ข้อมูลเก่า ออเดอร์หาย 6 → 3 (บางครั้ง PANIC เริ่มไม่ได้เลย) ร้านไม่ได้ทนขึ้นแต่ข้อมูลเสีย ควรใช้ `replicas: 1` + `strategy: Recreate` และ PVC `ReadWriteOncePod` (ขั้น H: Pod ที่ 2 `Pending`) ถ้าต้องการหลายตัวจริงต้องใช้ StatefulSet ที่ให้ PVC ประจำตัวแต่ละ Pod และตั้ง replication ของฐานข้อมูล
</details>

**16. ทำไมจึงพูดว่า "PV ไม่ใช่ backup" ยกตัวอย่างจากบทนี้อย่างน้อยสองกรณีที่ PV ช่วยไม่ได้**

<details>
<summary>แนวคำตอบ</summary>

PV เก็บข้อมูลสำเนาเดียวบน storage ของมัน (1) ขั้น F: postgres สองตัวเขียนทับกันจนออเดอร์หาย PV เก็บข้อมูลที่เสียไว้อย่างซื่อสัตย์ (2) ขั้น G: ลบ PVC ที่ reclaimPolicy เป็น Delete แล้ว PV และโฟลเดอร์ถูกลบทันที ข้อมูลหายถาวร (3) ถ้าดิสก์ของ Node เสีย ข้อมูลใน local-path ก็หาย การสำรองต้องทำแยก เช่น `pg_dump` เก็บนอกคลัสเตอร์ หรือ VolumeSnapshot เมื่อใช้ CSI ที่รองรับ
</details>

---

## 17. เอกสารอ้างอิง

1. The Kubernetes Authors. *Volumes*. https://kubernetes.io/docs/concepts/storage/volumes/
2. The Kubernetes Authors. *Persistent Volumes*. https://kubernetes.io/docs/concepts/storage/persistent-volumes/
3. The Kubernetes Authors. *Storage Classes*. https://kubernetes.io/docs/concepts/storage/storage-classes/
4. The Kubernetes Authors. *Dynamic Volume Provisioning*. https://kubernetes.io/docs/concepts/storage/dynamic-provisioning/
5. The Kubernetes Authors. *Ephemeral Volumes* (generic ephemeral volumes). https://kubernetes.io/docs/concepts/storage/ephemeral-volumes/
6. The Kubernetes Authors. *Configure a Pod to Use a PersistentVolume for Storage*. https://kubernetes.io/docs/tasks/configure-pod-container/configure-persistent-volume-storage/
7. The Kubernetes Authors. *Change the Reclaim Policy of a PersistentVolume*. https://kubernetes.io/docs/tasks/administer-cluster/change-pv-reclaim-policy/
8. The Kubernetes Authors. *Change the default StorageClass*. https://kubernetes.io/docs/tasks/administer-cluster/change-default-storage-class/
9. The Kubernetes Authors. *Configure a Security Context for a Pod or Container* (fsGroup, fsGroupChangePolicy). https://kubernetes.io/docs/tasks/configure-pod-container/security-context/
10. The Kubernetes Authors. *Pod Security Standards* (restricted volume types). https://kubernetes.io/docs/concepts/security/pod-security-standards/
11. The Kubernetes Authors. *Resource Quotas* (Storage Resource Quota). https://kubernetes.io/docs/concepts/policy/resource-quotas/
12. The Kubernetes Authors. *Volume Snapshots*. https://kubernetes.io/docs/concepts/storage/volume-snapshots/
13. The Kubernetes Authors. *Taints and Tolerations* (taint based evictions, tolerationSeconds). https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/
14. The Kubernetes Authors. *Using Finalizers to Control Deletion*. https://kubernetes.io/docs/concepts/overview/working-with-objects/finalizers/
15. The Kubernetes Authors. *Deployments* (strategy Recreate). https://kubernetes.io/docs/concepts/workloads/controllers/deployment/
16. The Kubernetes Authors. *StatefulSets* (บทถัดไป). https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/
17. The Kubernetes Authors. *kubectl patch*. https://kubernetes.io/docs/reference/kubectl/generated/kubectl_patch/
18. Kubernetes Blog. *Kubernetes 1.29: Single Pod Access Mode for PersistentVolumes Graduates to Stable*. https://kubernetes.io/blog/2023/12/18/read-write-once-pod-access-mode-ga/
19. kind. *Persistent Volumes / local-path-provisioner* (ค่าเริ่มต้นของคลัสเตอร์ kind). https://kind.sigs.k8s.io/

---

> **หมายเหตุเกี่ยวกับภาพประกอบ:** ภาพประกอบ 39 ภาพในโฟลเดอร์ [`images/`](images/) และภาพตัวละครน้องส้ม (`00-character-som.png`) สร้างขึ้นด้วยปัญญาประดิษฐ์สำหรับการสร้างภาพเพื่อใช้ประกอบการเรียนการสอน ชุดคำสั่งสร้างภาพอยู่ใน [`images/imagegen-prompts.md`](images/imagegen-prompts.md) ภาพใช้อุปมาเชิงเปรียบเทียบเพื่อช่วยความเข้าใจ ตัวเลขในภาพ (เช่น ชื่อ PV, จำนวนออเดอร์ และเวลา) เป็นค่าตัวอย่าง ผู้เรียนควรใช้เนื้อหาในเอกสารนี้และเอกสารอ้างอิงเป็นหลัก ผลลัพธ์คำสั่งทั้งหมดมาจากการทดลองจริง (Kubernetes v1.37.0) ค่าเวลา, IP, ชื่อ Pod/PV, Node ที่ Pod ถูกวาง และขนาดดิสก์ในเครื่องผู้เรียนอาจต่างกัน
