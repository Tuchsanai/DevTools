# LAB บทที่ 10: ConfigMap — กระดานประกาศของโซน สู่ร้านน้องส้มที่เปลี่ยนป้ายได้โดยไม่ build ใหม่

> **รายวิชา:** Software Development Tools and Environments (DevTools)
> **หัวข้อ:** ปฏิบัติการ ConfigMap — ส่องและสร้าง ConfigMap 4 วิธี, env ทีละ key และ `$(VAR)`, envFrom + prefix + ลำดับความสำคัญ, ConfigMap/key ที่ไม่มี + `optional` + การอ้างข้าม namespace, mount เป็นไฟล์ (`items`, `defaultMode`, `subPath`), จับเวลาการอัปเดต, แอปที่ต้อง reload เอง (nginx, `rollout restart`, checksum), `immutable`, kustomize `configMapGenerator` และร้านอาหารแมวน้องส้มที่ย้ายชื่อร้าน ธีม โปรโมชัน และประกาศหน้าร้านมาไว้ใน ConfigMap
> **ผลลัพธ์การเรียนรู้ที่เกี่ยวข้อง:** CLO-5, CLO-6
> **ทฤษฎีประกอบ:** [01_Theory/README.md](../01_Theory/README.md)

---

## บทนำ

ใน LAB นี้นักศึกษาจะช่วยน้องส้มติด **กระดานประกาศของโซน (ConfigMap)** เริ่มจากส่องกระดานที่ระบบติดไว้แล้ว ลองสร้างกระดานหลายวิธี ถ่ายการ์ดจากกระดานมาเป็น **ป้ายติดอกพนักงาน (env/envFrom)** ดูว่าเกิดอะไรเมื่ออ้างกระดานที่ไม่มี วาง **กระดานเล็กในบูธ (volume)** แล้วจับเวลาว่า **หุ่นยนต์ลูกเรือ kubelet** มาอัปเดตให้เมื่อไร เห็นว่าแอปอย่าง nginx ต้องโหลดไฟล์ใหม่เอง ลอง **กระดานเคลือบอะคริลิก (immutable)** และ **เครื่องพิมพ์ป้าย (kustomize configMapGenerator)** ปิดท้ายด้วย **ร้านอาหารแมวน้องส้ม `som-shop-v6`** ที่ย้ายชื่อร้าน ธีม และโปรโมชันไปไว้ใน ConfigMap (เปลี่ยนแล้ว `rollout restart`) และย้ายประกาศหน้าร้านไปไว้ใน volume (เปลี่ยนเองภายในราว 1 นาทีโดย Pod ไม่ restart) **โดยใช้ image `som-shop-web:1.5` ตัวเดียวตลอด ไม่ build ใหม่เลย** และออเดอร์ในฐานข้อมูลไม่หาย

ผลลัพธ์ทุกบล็อก ```` ```text ```` ในเอกสารนี้มาจาก **การทดลองจริง** บน container ที่สร้างจาก image เดียวกับ `k8s-lab` (`tuchsanai/devtools-kind:2569_1`, Kubernetes v1.37.0, kubectl v1.37.1, Kustomize v5.8.1) เมื่อ 5 ตุลาคม 2569 ตัดบางส่วนเพื่อให้กระชับ (แทนด้วย `...`) **เวลา, AGE, ชื่อ Pod ของ Deployment ที่สุ่ม, IP, UID, ชื่อโฟลเดอร์ `..2026_10_05_…`, Node ที่ Pod ถูกวาง และจำนวนวินาทีที่ไฟล์อัปเดต ในเครื่องนักศึกษาจะต่างจากตัวอย่าง** เป็นเรื่องปกติ ให้ยึดผลจากเครื่องตัวเองเสมอ ส่วนชื่อ ConfigMap ที่ kustomize สร้าง (`web-config-gh5tkgmddg`) จะเหมือนกันทุกเครื่องถ้าไฟล์ตรงกันทุกไบต์

### สัญลักษณ์บอกว่ารันคำสั่งที่ไหน

| สัญลักษณ์ | ความหมาย |
|---|---|
| 🖥️ **บนเครื่องนักศึกษา** | Terminal/PowerShell ของเครื่องตัวเอง (Windows/macOS/Linux) |
| 🐧 **ใน SSH session ของ k8s-lab** | หน้าต่างที่ล็อกอิน `ssh -p 2223 root@localhost` แล้ว (prompt `root@k8s-lab`) หรือ Terminal ของ JupyterLab `http://localhost:8889` |
| 🌐 **browser บนเครื่องนักศึกษา** | Chrome/Edge/Firefox บนเครื่องตัวเอง |

คำสั่ง `kubectl`, `kind`, `docker build` และ `curl` ของบทนี้รัน 🐧 **ใน SSH session ของ k8s-lab** ทั้งหมด ยกเว้นการ `docker cp` โฟลเดอร์เข้า container และการเปิด browser ที่ `http://localhost:30080` ใน LAB 10

### กติกาของ LAB บทนี้

- LAB 1–9 ทำในโฟลเดอร์ **`/workspace/010_kubernetes_configmap/02_LAB/labs/labNN-...`** ของแต่ละ LAB ส่วน LAB 10 ทำใน **`/workspace/010_kubernetes_configmap/02_LAB/som-shop-v6`** ทุก LAB เริ่มด้วย `cd` ไปโฟลเดอร์ของตัวเอง
- LAB 1–9 ใช้ namespace `default` และ LAB 10 ใช้ `som-shop` **ConfigMap `shop-config` กับ Pod `envpod` ที่สร้างใน LAB 2 ใช้ต่อถึง LAB 6** (LAB 3, 4, 5, 6 ต้องมี) ทำ LAB 2–6 ต่อกันในรอบเดียวจะง่ายที่สุด เก็บกวาดรวมไว้ท้าย LAB 6
- image สาธารณะ `busybox:1.36` และ `nginx:1.27-alpine` **ให้ Node ดึงจาก Docker Hub เองตอนใช้** ไม่ต้อง `kind load` ส่วน `som-shop-web:1.5` ต้อง build เองและ `kind load` และ `postgres:17.11-alpine` ต้อง `docker save --platform` + `kind load image-archive` (LAB 0) ทั้งสองใช้เฉพาะ LAB 10
- Pod busybox ทุกตัวรัน `sleep 86400` (1 วัน) และตั้ง `terminationGracePeriodSeconds: 1` เพราะ `sleep` ไม่รับ SIGTERM ตอนลบจึงจบเร็ว Pod `envpod`/`envfrom` เป็น `restartPolicy: Never` ถ้า `sleep` จบจะเป็น `Completed` แล้ว `kubectl exec` ไม่ได้
- **ไฟล์ใน volume อัปเดตเองราว 1 นาที บางครั้งเกือบ 1.5 นาที** (LAB 4, 6, 7, 10) อย่าเพิ่งสรุปว่าไม่ทำงานก่อนรอครบ 2 นาที
- **ห้ามใช้ `kubectl edit`** ใน terminal ที่ไม่ใช่แบบโต้ตอบ (เช่น สคริปต์ หรือส่งคำสั่งผ่าน `ssh ... "คำสั่ง"`) เพราะจะค้างอยู่ใน vim ทุก LAB จึงแก้ ConfigMap ด้วย `kubectl apply -f`, `kubectl patch` หรือสคริปต์ที่เตรียมไว้ ถ้าเผลอเปิด vim ใน terminal ปกติ ออกโดยไม่บันทึกด้วย `Esc` แล้วพิมพ์ `:q!`
- **NodePort 30080 จองได้ทีละ Service ทั้งคลัสเตอร์** บทนี้ใช้ใน LAB 10 เท่านั้น
- **ห้ามใช้ Secret ใน LAB บทนี้** รหัสผ่านฐานข้อมูลยังเขียนใน YAML ตรง ๆ โดยจงใจ เพื่อให้เห็นปัญหาที่บทที่ 11 จะแก้
- รหัสผ่าน SSH `passwd` และรหัสฐานข้อมูล `meow1234` ในเอกสารนี้เป็น **ค่าตัวอย่างเพื่อการเรียนเท่านั้น** ห้ามใช้กับระบบจริง

## สารบัญ LAB

| LAB | ชื่อ | เวลาโดยประมาณ | ความยาก |
|:---:|---|:---:|:---:|
| 0 | [เตรียมคลัสเตอร์และ image](#lab-0-เตรียมคลัสเตอร์และ-image) | 15–20 นาที | ⭐ |
| 1 | [ส่องและสร้าง ConfigMap](#lab-1-ส่องและสร้าง-configmap) | 15 นาที | ⭐ |
| 2 | [env ทีละ key และ $(VAR)](#lab-2-env-ทีละ-key-และ-var) | 10 นาที | ⭐ |
| 3 | [envFrom, prefix และลำดับความสำคัญ](#lab-3-envfrom-prefix-และลำดับความสำคัญ) | 10 นาที | ⭐⭐ |
| 4 | [ConfigMap ที่ไม่มี, optional และข้าม namespace](#lab-4-configmap-ที่ไม่มี-optional-และข้าม-namespace) | 15–20 นาที | ⭐⭐ |
| 5 | [mount เป็นไฟล์](#lab-5-mount-เป็นไฟล์) | 10 นาที | ⭐⭐ |
| 6 | [อัปเดตเองและจับเวลา](#lab-6-อัปเดตเองและจับเวลา) | 10 นาที | ⭐⭐⭐ |
| 7 | [แอปต้องโหลดใหม่เอง](#lab-7-แอปต้องโหลดใหม่เอง) | 15–20 นาที | ⭐⭐⭐ |
| 8 | [immutable](#lab-8-immutable) | 10 นาที | ⭐⭐⭐ |
| 9 | [kustomize configMapGenerator](#lab-9-kustomize-configmapgenerator) | 10 นาที | ⭐⭐⭐ |
| 10 | [LAB สุดท้าย: ร้านน้องส้มเปลี่ยนป้ายไม่ต้อง build ใหม่](#lab-10-lab-สุดท้าย-ร้านน้องส้มเปลี่ยนป้ายไม่ต้อง-build-ใหม่) | 60–75 นาที | ⭐⭐⭐⭐⭐ |
| – | [Troubleshooting](#troubleshooting) · [Checklist ส่งงาน](#checklist-ส่งงาน) · [ตารางเก็บกวาดและคืนสภาพ](#ตารางเก็บกวาดและคืนสภาพ) · [เก็บกวาดหลังจบบท](#เก็บกวาดหลังจบบท) | | |

รวมประมาณ 3–3.5 ชั่วโมง (รวมช่วงรอไฟล์อัปเดตใน LAB 4, 6, 7 และ 10 กับการ build image ใน LAB 0) ก่อนเริ่มแต่ละ LAB แนะนำให้อ่านหัวข้อทฤษฎีที่เกี่ยวข้อง: LAB 1 → หัวข้อ 3–4, LAB 2–3 → หัวข้อ 5, LAB 4 → หัวข้อ 7 และ 11.2, LAB 5 → หัวข้อ 6, LAB 6–7 → หัวข้อ 8, LAB 8 → หัวข้อ 9, LAB 9 → หัวข้อ 10, LAB 10 → หัวข้อ 8, 9, 11.3 และ 12

### สารบัญรูปภาพ

{{FIGTOC}}

### โครงสร้างไฟล์ LAB

```text
02_LAB/
├── README.md                          ← เอกสารนี้
├── images/                            ← ภาพประกอบ 01–21 (+ imagegen-prompts.md) และ screenshots/ ภาพหน้าจอจริงของร้าน
├── labs/                              ← ไฟล์ของ LAB 1–9
│   ├── lab01-create/{shop.env,announcement.txt,default.conf}      (วัตถุดิบสร้าง ConfigMap)
│   ├── lab02-env/{shop-config,envpod}.yaml                         (ConfigMap shop-config — ใช้ต่อ LAB 3–6 + Pod envpod)
│   ├── lab03-envfrom/envfrom-pod.yaml                              (Pod envfrom: envFrom + prefix CFG_ + env ชื่อซ้ำ)
│   ├── lab04-missing/{nocm,nokey,novol,optpod,other-ns}.yaml       (อ้างของที่ไม่มี / optional / ข้าม namespace)
│   ├── lab05-volume/volpod.yaml                                    (mount 3 แบบ: ทั้งก้อน, items+defaultMode, subPath)
│   ├── lab06-update/watch.sh                                       (patch shop-config แล้วจับเวลา)
│   ├── lab07-reload/{nginx-conf,nginx-conf-v2,nginx-conf-v3,ngx,plain-deploy}.yaml
│   ├── lab08-immutable/frozen.yaml
│   └── lab09-kustomize/kz/{kustomization.yaml,announcement.txt,deploy.yaml}
└── som-shop-v6/                       ← LAB 10 ร้านน้องส้มที่ป้ายร้านมาจาก ConfigMap
    ├── app/                           ← แอป Next.js + Dockerfile รุ่น 1.5 (build เป็น som-shop-web:1.5)
    ├── k8s-start/{00-namespace,10-db,20-web}.yaml   ← จุดเริ่ม: แบบท้ายบท 009 (ค่าร้านยังเขียนใน env) แต่ใช้ image 1.5
    ├── k8s/{00-namespace,10-db,15-config,20-web}.yaml ← บทนี้: ConfigMap som-web-config + som-announcement, web ใช้ envFrom + volume
    ├── extra/15-config-promo.yaml     ← ขั้น C: ป้ายร้านชุดใหม่ (ชื่อสาขา ธีม sunset โปรโมชัน)
    ├── extra/16-announcement-1800.yaml ← ขั้น D: ประกาศใหม่ "ปิดร้านเร็ว 18:00 น. ⛵"
    ├── extra/17-config-v2.yaml        ← ขั้น E: som-web-config-v2 แบบ immutable
    ├── rbac/intern.yaml               ← ขั้น F: ServiceAccount intern ดูได้อย่างเดียว
    ├── hit.sh                         ← ยิง request ทีละครั้งแล้วนับว่าไปตก Pod ไหน
    └── wait-announcement.sh           ← จับเวลาว่าประกาศใหม่ถึงทุก Pod เมื่อไร
```

> ไฟล์ของขั้น C/D/E อยู่ใน **`extra/`** ไม่ใช่ `k8s/` โดยตั้งใจ เพราะ `extra/15-config-promo.yaml` ใช้ชื่อ ConfigMap `som-web-config` เดียวกับ `k8s/15-config.yaml` ถ้าอยู่โฟลเดอร์เดียวกัน `kubectl apply -f k8s/` จะ apply ทั้งสองไฟล์ทับกันเอง โฟลเดอร์ `k8s/` จึงใช้ "เริ่มหรือคืนสภาพร้าน" ได้ด้วยคำสั่งเดียว

### แอปร้านรุ่น 1.5 เพิ่มอะไร

แอปของบทที่ 9 อ่าน env `SHOP_NAME`, `SHOP_EYEBROW`, `SHOP_FOOTER`, `APP_THEME` ได้อยู่แล้ว (หน้าเว็บอ่าน env ตอนรัน env ของ Pod จึงทับค่า `ENV` ใน image ได้) แต่ป้ายโปรโมชันผูกกับเงื่อนไข `version === '1.3'` และไม่มีการอ่านไฟล์ บทนี้จึงเพิ่มรุ่น **1.5** โดยแก้โค้ดให้น้อยที่สุด

| ไฟล์ใน `som-shop-v6/app/` | สิ่งที่เพิ่มในรุ่น 1.5 |
|---|---|
| `lib/shop.ts` | `promo` อ่านจาก env **`SHOP_PROMO`** (ว่าง = ไม่แสดง) และ `readAnnouncement()` อ่านไฟล์ **`/etc/som/announcement.txt` ใหม่ทุก request** (ไม่มีไฟล์ = ไม่มีประกาศ หน้าเว็บไม่พัง) |
| `app/page.tsx` | แถบ `promo` แสดงเมื่อ `SHOP_PROMO` ไม่ว่าง และแถบเหลือง `📢 <ประกาศ>` เมื่อมีไฟล์ประกาศ |
| `app/api/shop/route.ts` (ใหม่) | **`GET /api/shop`** ตอบ JSON ค่าที่ Pod นั้นเห็น `{pod, version, shopName, theme, promo, eyebrow, footer}` |
| `app/api/announcement/route.ts` (ใหม่) | **`GET /api/announcement`** ตอบ `<ชื่อ Pod> 1.5 <ข้อความประกาศ>` หรือ `(ไม่มีประกาศ)` |
| `Dockerfile` | build ด้วย `--build-arg APP_VERSION=1.5` อย่างเดียว ไม่ต้องใส่ `APP_THEME` เพราะธีมมาจาก ConfigMap |

> **ทำไมไม่ใช้เลข 1.4:** บทที่ 7 ใช้ `som-shop-web:1.4` เป็น **tag ที่ไม่มีอยู่จริง** เพื่อสาธิต rollout ที่พัง (`ImagePullBackOff`) ถ้าใช้เลข 1.4 ซ้ำจะสับสนกับรุ่นพังนั้น รุ่นของบทนี้จึงข้ามไปเป็น 1.5

---

## LAB 0: เตรียมคลัสเตอร์และ image

{{FIG:L01}}

**เป้าหมาย:** นำไฟล์ LAB เข้า `k8s-lab` เตรียมคลัสเตอร์ (ใช้ต่อจากบทที่ 9 หรือสร้างใหม่) ตรวจว่าไม่มีของค้างที่จอง NodePort 30080 และเตรียม image `postgres:17.11-alpine` กับ `som-shop-web:1.5` ให้ทุก Node สำหรับ LAB 10

**สิ่งที่ต้องมีก่อน:** ทำ LAB บทที่ [1](../../001_kubernetes-introduction/02_LAB/readme.md)–[9](../../009_kubernetes_statefulset/02_LAB/README.md) แล้ว มี container `k8s-lab` (SSH port `2223`, NodePort `30080–30082`) และมีโฟลเดอร์ `010_kubernetes_configmap` บนเครื่อง

### ขั้นที่ 1: นำโฟลเดอร์บทเรียนเข้า k8s-lab

🖥️ **บนเครื่องนักศึกษา** ตรวจว่า `k8s-lab` กำลังรัน (STATUS ต้องเป็น `Up`) ถ้าเป็น `Exited` ให้ `docker start k8s-lab`

```bash
docker ps -a --filter name=k8s-lab
```

`cd` ไปยังโฟลเดอร์ที่ **มีโฟลเดอร์ `010_kubernetes_configmap` อยู่ข้างใน** แล้วคัดลอกทั้งโฟลเดอร์เข้า `/workspace/` ของ container (คำสั่งเดียวกันทั้ง PowerShell และ bash)

```bash
docker cp 010_kubernetes_configmap k8s-lab:/workspace/
```

> `docker cp` เป็นการ **คัดลอก** ไม่ใช่การเชื่อมโฟลเดอร์ ถ้าแก้ไฟล์บนเครื่องตัวเองภายหลังต้องสั่งซ้ำ บทนี้มีแอปร้านรุ่น 1.5 ของตัวเอง (`02_LAB/som-shop-v6/app`) และไฟล์เริ่มร้าน (`som-shop-v6/k8s-start/`) จึง **ไม่ต้องมีโฟลเดอร์ของบทก่อนใน container** ก็ทำได้ครบ

### ขั้นที่ 2: ล็อกอินเข้า k8s-lab

🖥️ **บนเครื่องนักศึกษา**

```bash
ssh -p 2223 root@localhost
```

รหัสผ่าน `passwd` (ค่าตัวอย่างเพื่อการเรียน พิมพ์แล้วจะไม่เห็นตัวอักษร) เมื่อสำเร็จจะเห็น prompt `root@k8s-lab` (หรือใช้ Terminal ใน JupyterLab `http://localhost:8889` ก็ได้)

### ขั้นที่ 3: เข้าโฟลเดอร์ LAB และตรวจคลัสเตอร์

🐧 **ใน SSH session ของ k8s-lab**

```bash
cd /workspace/010_kubernetes_configmap/02_LAB
ls labs som-shop-v6
kubectl get nodes
kubectl version
```

| ผลของ `kubectl get nodes` | ทำอย่างไร |
|---|---|
| เห็น 3 Node เป็น `Ready` (คลัสเตอร์จากบทที่ 9 ยังอยู่) | **ใช้ต่อได้เลย** ไปขั้นที่ 4 |
| error เช่น `connection refused` / ไม่มีคลัสเตอร์ (เพิ่ง restart `k8s-lab` หรือเคย `k8s-down`) | สร้างใหม่ด้วย `k8s-up` (การทดลองใช้เวลาราว 55 วินาที) image ที่เคย `kind load` ในบทก่อนจะหายไป ต้องโหลด postgres ใหม่ในขั้นที่ 5 |

ผลจริงบนคลัสเตอร์ใหม่

```text
NAME                STATUS   ROLES           AGE     VERSION
lab-control-plane   Ready    control-plane   3m1s    v1.37.0
lab-worker          Ready    <none>          2m46s   v1.37.0
lab-worker2         Ready    <none>          2m46s   v1.37.0
Client Version: v1.37.1
Kustomize Version: v5.8.1
Server Version: v1.37.0
```

บรรทัด `Kustomize Version: v5.8.1` คือ kustomize ที่ติดมากับ kubectl ซึ่งใช้ใน LAB 9 (`kubectl kustomize`, `kubectl apply -k`) โดยไม่ต้องติดตั้งเพิ่ม

### ขั้นที่ 4: ตรวจของที่ค้างจากบทก่อน

🐧 **ใน SSH session ของ k8s-lab**

```bash
kubectl get sc; kubectl get pv,pvc -A; kubectl get svc -A | grep 3008 || echo "ไม่มี NodePort 3008x ค้าง"
```

ผลจริงบนคลัสเตอร์ใหม่

```text
NAME                 PROVISIONER             RECLAIMPOLICY   VOLUMEBINDINGMODE      ALLOWVOLUMEEXPANSION   AGE
standard (default)   rancher.io/local-path   Delete          WaitForFirstConsumer   false                  2m57s
No resources found
ไม่มี NodePort 3008x ค้าง
```

ถ้ายังเห็นร้านของบทที่ 9 (namespace `som-shop` จอง NodePort 30080 และมี PVC `data-som-db-0`) ให้ลบด้วย `kubectl delete ns som-shop` (ใช้เวลาราว 30 วินาที) LAB 10 จะสร้างร้านใหม่จาก `som-shop-v6/k8s-start/` ด้วยฐานข้อมูลเปล่า แล้วสั่งออเดอร์ใหม่เอง

### ขั้นที่ 5: โหลด postgres และ build som-shop-web:1.5

ตรวจก่อนว่า Node มี image อะไรอยู่แล้ว (ถ้าใช้คลัสเตอร์เดิมจากบทที่ 9 น่าจะมี `postgres:17.11-alpine` แล้ว)

```bash
docker exec lab-worker crictl images | grep -E "som-shop|postgres"; docker exec lab-worker2 crictl images | grep -E "som-shop|postgres"
```

**postgres** (ข้ามได้ถ้าเห็น `postgres 17.11-alpine` บนทั้งสอง worker แล้ว) เป็น image หลาย platform จึงใช้ `docker save --platform` + `kind load image-archive` 🐧 ในโฟลเดอร์ `02_LAB`

```bash
time (docker pull -q postgres:17.11-alpine && docker save --platform linux/amd64 postgres:17.11-alpine -o /root/postgres.tar && kind load image-archive /root/postgres.tar --name lab)
```

```text
docker.io/library/postgres:17.11-alpine

real	0m16.436s
user	0m0.295s
sys	0m0.963s
```

**som-shop-web:1.5** เป็นรุ่นใหม่ของบทนี้ **ต้อง build ทุกกรณี** (แม้ใช้คลัสเตอร์เดิม) จากแอปในโฟลเดอร์ `som-shop-v6/app` แล้ว `kind load` ให้ทุก Node

```bash
cd som-shop-v6
time (docker build -q -t som-shop-web:1.5 --build-arg APP_VERSION=1.5 app && kind load docker-image som-shop-web:1.5 --name lab)
```

```text
sha256:13bbe14f180ffd205d31ffaf14543520cd602e47465773d3d83fbdd2306d079a
Image: "som-shop-web:1.5" with ID "sha256:13bbe14f180ffd205d31ffaf14543520cd602e47465773d3d83fbdd2306d079a" not yet present on node "lab-worker", loading...
Image: "som-shop-web:1.5" with ID "sha256:13bbe14f180ffd205d31ffaf14543520cd602e47465773d3d83fbdd2306d079a" not yet present on node "lab-control-plane", loading...
Image: "som-shop-web:1.5" with ID "sha256:13bbe14f180ffd205d31ffaf14543520cd602e47465773d3d83fbdd2306d079a" not yet present on node "lab-worker2", loading...

real	0m33.893s
user	0m0.401s
sys	0m0.824s
```

build ครั้งแรกใช้ราว 30 วินาทีในเครื่องทดลอง (`npm ci` ดาวน์โหลด dependency แล้วคอมไพล์ Next.js) เครื่องนักศึกษาอาจนานกว่านี้หลายเท่า ค่า sha256 ในเครื่องนักศึกษาจะต่างจากตัวอย่าง ไฟล์ `/root/postgres.tar` ลบทิ้งได้หลัง load เสร็จ (`rm -f /root/postgres.tar`)

ตรวจซ้ำด้วยคำสั่ง `crictl` ข้างบน ผลจริงหลัง load

```text
docker.io/library/postgres                      17.11-alpine         79bd7c99e9231       117MB
docker.io/library/som-shop-web                  1.5                  23f2f2f04ed31       76.7MB
docker.io/library/postgres                      17.11-alpine         79bd7c99e9231       117MB
docker.io/library/som-shop-web                  1.5                  23f2f2f04ed31       76.7MB
```

### ขั้นที่ 6: กลับโฟลเดอร์ LAB

```bash
cd /workspace/010_kubernetes_configmap/02_LAB
pwd
```

### สิ่งที่เห็น

- คลัสเตอร์ 3 Node `Ready` (v1.37.0) พร้อม kubectl v1.37.1 ที่มี Kustomize v5.8.1 ในตัว StorageClass `standard (default)` และไม่มี PV/PVC หรือ NodePort 3008x ค้าง
- `postgres:17.11-alpine` และ `som-shop-web:1.5` อยู่บนทั้งสอง worker ส่วน busybox และ nginx ยังไม่ต้องมี (Node ดึงเองครั้งแรกที่ใช้)

**คำถามชวนคิด**

1. ทำไม LAB 10 ทั้งบทใช้ image `som-shop-web:1.5` ตัวเดียวได้ ทั้งที่ชื่อร้าน ธีม และประกาศเปลี่ยนหลายรอบ (เทียบกับบทที่ 7 ที่ต้องมีรุ่น 1.2 ธีม harbor และ 1.3 ธีม sunset)
2. ถ้าลืม `kind load docker-image som-shop-web:1.5` แล้วไปทำ LAB 10 จะเห็น Pod `som-web` สถานะแบบไหน (ดู `imagePullPolicy: IfNotPresent` ใน `k8s-start/20-web.yaml`)

---

## LAB 1: ส่องและสร้าง ConfigMap

{{FIG:L02}}

**เป้าหมาย:** ดู ConfigMap ที่ระบบสร้างไว้แล้ว และสร้าง ConfigMap ด้วย `--from-literal`, `--from-file`, `--from-env-file` และ `--dry-run=client -o yaml` เห็น error เมื่อสร้างซ้ำและเมื่อเกิน 1 MiB

**ไฟล์:** `labs/lab01-create/shop.env`, `announcement.txt`, `default.conf`

### ขั้นที่ 1: กระดานที่ระบบติดไว้แล้ว

🐧 **ใน SSH session ของ k8s-lab**

```bash
cd /workspace/010_kubernetes_configmap/02_LAB/labs/lab01-create
kubectl get cm -A
```

```text
NAMESPACE            NAME                                                   DATA   AGE
default              kube-root-ca.crt                                       1      3m56s
kube-node-lease      kube-root-ca.crt                                       1      3m56s
kube-public          cluster-info                                           2      4m3s
kube-public          kube-root-ca.crt                                       1      3m56s
kube-system          coredns                                                1      4m3s
kube-system          extension-apiserver-authentication                     6      4m5s
kube-system          kube-apiserver-legacy-service-account-token-tracking   1      4m5s
kube-system          kube-proxy                                             2      4m2s
kube-system          kube-root-ca.crt                                       1      3m56s
kube-system          kubeadm-config                                         1      4m3s
kube-system          kubelet-config                                         1      4m3s
local-path-storage   kube-root-ca.crt                                       1      3m56s
local-path-storage   local-path-config                                      4      4m1s
```

คอลัมน์ `DATA` คือจำนวน key ทุก namespace มี `kube-root-ca.crt` (ใบรับรอง CA ของคลัสเตอร์) ที่ระบบสร้างให้เอง ดูไฟล์ตั้งค่า DNS ของคลัสเตอร์ที่อยู่ใน key `Corefile`

```bash
kubectl -n kube-system get cm coredns -o jsonpath='{.data.Corefile}'
```

```text
.:53 {
    errors
    health {
       lameduck 5s
    }
    ready
    kubernetes cluster.local in-addr.arpa ip6.arpa {
       pods insecure
       fallthrough in-addr.arpa ip6.arpa
       ttl 30
    }
    prometheus :9153
    forward . /etc/resolv.conf {
       max_concurrent 1000
    }
    cache 30 {
       disable success cluster.local
       disable denial cluster.local
    }
    loop
    reload
    loadbalance
}
```

ดูโครงสร้างของ `kube-root-ca.crt` และยืนยันว่า ConfigMap เป็น namespaced object

```bash
kubectl get cm kube-root-ca.crt -o yaml | head -5
kubectl api-resources | grep -i configmap
```

```text
apiVersion: v1
data:
  ca.crt: |
    -----BEGIN CERTIFICATE-----
    MIIDBTCCAe2gAwIBAgIINGfKkmGa2F4wDQYJKoZIhvcNAQELBQAwFTETMBEGA1UE
configmaps                          cm           v1                                true         ConfigMap
```

> ConfigMap ใน `kube-system` ดูได้แต่ **ห้ามแก้หรือลบ** DNS และ kube-proxy ของทั้งคลัสเตอร์อาศัยค่าเหล่านี้

### ขั้นที่ 2: --from-literal

```bash
kubectl create configmap demo --from-literal=SHOP_NAME=ร้านน้องส้ม --from-literal=APP_THEME=sunset
kubectl get cm demo -o yaml
kubectl describe cm demo
```

```text
configmap/demo created
apiVersion: v1
data:
  APP_THEME: sunset
  SHOP_NAME: ร้านน้องส้ม
kind: ConfigMap
metadata:
  creationTimestamp: "2026-10-05T09:47:38Z"
  name: demo
  namespace: default
  resourceVersion: "956"
  uid: 033a9562-afb9-4b25-b50e-de91af7664d4
Name:         demo
Namespace:    default
Labels:       <none>
Annotations:  <none>

Data
====
APP_THEME:
----
sunset

SHOP_NAME:
----
ร้านน้องส้ม


BinaryData
====

Events:  <none>
```

สังเกตว่าไม่มี `spec`/`status` และ `describe` แยกส่วน `Data` กับ `BinaryData`

### ขั้นที่ 3: --from-file

```bash
cat announcement.txt default.conf; kubectl create configmap files --from-file=announcement.txt --from-file=nginx.conf=default.conf
kubectl get cm files -o jsonpath='{.data}'; echo
```

```text
วันนี้ปลาทูสด
# ไฟล์ตั้งค่า nginx ตัวอย่าง (LAB 1 ใช้แค่ดูว่า --from-file เก็บทั้งไฟล์เป็นค่าของ key เดียว)
server { listen 8080; }
configmap/files created
{"announcement.txt":"วันนี้ปลาทูสด\n","nginx.conf":"# ไฟล์ตั้งค่า nginx ตัวอย่าง (LAB 1 ใช้แค่ดูว่า --from-file เก็บทั้งไฟล์เป็นค่าของ key เดียว)\nserver { listen 8080; }\n"}
```

key แรกได้ชื่อจากชื่อไฟล์ (`announcement.txt`) key ที่สองตั้งชื่อเองเป็น `nginx.conf` ทั้งไฟล์ (รวม newline `\n` ท้ายไฟล์) เป็นค่าของ key เดียว

### ขั้นที่ 4: --from-env-file

```bash
cat shop.env; kubectl create configmap envf --from-env-file=shop.env
kubectl get cm envf -o jsonpath='{.data}'; echo
```

```text
SHOP_NAME=ร้านน้องส้ม
SHOP_THEME=sunset
# บรรทัดที่ขึ้นต้นด้วย # ถูกข้าม (ไม่กลายเป็น key)
EMPTY=
configmap/envf created
{"EMPTY":"","SHOP_NAME":"ร้านน้องส้ม","SHOP_THEME":"sunset"}
```

ได้ 3 key บรรทัด comment หายไป และ `EMPTY` ได้ค่าว่าง

### ขั้นที่ 5: ให้ kubectl เขียน YAML ให้

```bash
kubectl create configmap dir --from-file=. --dry-run=client -o yaml
kubectl get cm dir
```

```text
apiVersion: v1
data:
  announcement.txt: |
    วันนี้ปลาทูสด
  default.conf: |
    # ไฟล์ตั้งค่า nginx ตัวอย่าง (LAB 1 ใช้แค่ดูว่า --from-file เก็บทั้งไฟล์เป็นค่าของ key เดียว)
    server { listen 8080; }
  shop.env: |
    SHOP_NAME=ร้านน้องส้ม
    SHOP_THEME=sunset
    # บรรทัดที่ขึ้นต้นด้วย # ถูกข้าม (ไม่กลายเป็น key)
    EMPTY=
kind: ConfigMap
metadata:
  name: dir
Error from server (NotFound): configmaps "dir" not found
```

`--from-file=.` เอาทุกไฟล์ในโฟลเดอร์ (ไฟล์ละ 1 key) และ dry-run ไม่ได้สร้างจริง (`NotFound`) งานจริงให้ต่อท้าย `> cm.yaml` แล้วเก็บไฟล์ไว้ใน git

### ขั้นที่ 6: สร้างซ้ำ และอัปเดตด้วย dry-run + apply

```bash
kubectl create configmap demo --from-literal=APP_THEME=harbor
kubectl create configmap demo --from-literal=SHOP_NAME=ร้านน้องส้ม --from-literal=APP_THEME=harbor --dry-run=client -o yaml | kubectl apply -f -
kubectl get cm demo -o jsonpath='{.data.APP_THEME}'; echo
```

```text
error: failed to create configmap: configmaps "demo" already exists
Warning: resource configmaps/demo is missing the kubectl.kubernetes.io/last-applied-configuration annotation which is required by kubectl apply. kubectl apply should only be used on resources created declaratively by either kubectl create --save-config or kubectl apply. The missing annotation will be patched automatically.
configmap/demo configured
harbor
```

Warning ขึ้นครั้งแรกเพราะ `demo` ถูกสร้างด้วย `create` kubectl เติม annotation ให้เองแล้ว (ปกติ)

### ขั้นที่ 7: ไฟล์ไบนารี และขนาดเกิน 1 MiB

```bash
head -c 16 /dev/urandom > logo.bin; kubectl create configmap bin --from-file=logo.bin
kubectl get cm bin -o yaml | grep -A1 binaryData; kubectl describe cm bin | sed -n "/BinaryData/,/Events/p"
```

```text
configmap/bin created
binaryData:
  logo.bin: XIW0LDQ8x9pHOwF0PEo1Xw==
BinaryData
====
logo.bin: 16 bytes

Events:  <none>
```

ไฟล์สุ่ม 16 bytes ไม่ใช่ UTF-8 kubectl จึงใส่ไว้ใน `binaryData` (base64) เอง ค่า base64 ในเครื่องนักศึกษาจะต่าง (สุ่ม) ต่อไปลองไฟล์ 1,100,000 bytes กับ 1,048,000 bytes

```bash
head -c 1100000 /dev/zero | tr '\0' a > big.txt; ls -l big.txt; kubectl create configmap big --from-file=big.txt
head -c 1048000 /dev/zero | tr '\0' a > big2.txt; kubectl create configmap big2 --from-file=big2.txt
kubectl get cm
```

```text
-rw-r--r-- 1 root root 1100000 Oct  5 16:47 big.txt
error: failed to create configmap: ConfigMap "big" is invalid: []: Too long: may not be more than 1048576 bytes
configmap/big2 created
NAME               DATA   AGE
big2               1      1s
bin                1      1s
demo               2      9s
envf               3      9s
files              2      9s
kube-root-ca.crt   1      4m6s
```

### ขั้นที่ 8: เก็บกวาด

```bash
kubectl delete cm demo files envf bin big2; rm -f logo.bin big.txt big2.txt; kubectl get cm
```

```text
configmap "demo" deleted from default namespace
configmap "files" deleted from default namespace
configmap "envf" deleted from default namespace
configmap "bin" deleted from default namespace
configmap "big2" deleted from default namespace
NAME               DATA   AGE
kube-root-ca.crt   1      4m6s
```

kubectl v1.37 พิมพ์ผลการลบเป็น `... deleted from default namespace`

### สิ่งที่เห็น

- คลัสเตอร์ใหม่มี ConfigMap 13 ตัวที่ระบบใช้เอง (`coredns`, `kube-proxy`, `kube-root-ca.crt` ทุก namespace ฯลฯ) และ ConfigMap เป็น namespaced (`configmaps cm v1 true`)
- 4 วิธีสร้างให้ key ต่างกัน: literal = ตามที่พิมพ์, file = ชื่อไฟล์ (หรือตั้งเอง), env-file = หนึ่งบรรทัดหนึ่ง key, `--from-file=.` = ทุกไฟล์ในโฟลเดอร์
- `create` ซ้ำได้ `already exists` ต้องใช้ `--dry-run=client -o yaml | kubectl apply -f -` ไฟล์ไบนารีไป `binaryData` และขนาดรวมเกิน 1,048,576 bytes ถูกปฏิเสธ

**คำถามชวนคิด**

1. ถ้าใช้ `--from-file=shop.env` แทน `--from-env-file=shop.env` จะได้กี่ key และค่าเป็นอะไร
2. ทำไม Kubernetes จำกัดขนาด ConfigMap ไว้ที่ 1 MiB (คิดถึงว่า ConfigMap ถูกเก็บที่ไหน และถูกส่งไปที่ไหนบ้าง)

---

## LAB 2: env ทีละ key และ $(VAR)

{{FIG:L03}}

**เป้าหมาย:** สร้าง ConfigMap `shop-config` จาก YAML แล้วให้ Pod `envpod` หยิบทีละ key มาเป็น env ด้วย `configMapKeyRef` และเห็นการแทนค่า `$(VAR)` ใน `args`

**ไฟล์:** `labs/lab02-env/shop-config.yaml`, `envpod.yaml` (**ConfigMap `shop-config` และ Pod `envpod` ใช้ต่อถึง LAB 6 อย่าเพิ่งลบ**)

`shop-config.yaml` มีทั้ง key ปกติ key แปลก ๆ (ไว้ดูใน LAB 3) และ key ที่เป็นเนื้อไฟล์ (ไว้ใช้ใน LAB 5)

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: shop-config
data:
  SHOP_NAME: "ร้านน้องส้ม"
  APP_THEME: "sunset"
  FOOTER: "ร้านใน namespace $(POD_NAMESPACE)"   # LAB 3: ค่าจาก envFrom ที่มี $(...) จะไม่ถูกแทนค่า
  shop.name: "dot-key"                        # มีจุด — เป็นชื่อ env ได้แต่ shell อ่านไม่ได้
  1bad: "starts-with-digit"                   # ขึ้นต้นด้วยตัวเลข — เช่นกัน
  announcement.txt: |                         # | = ค่าหลายบรรทัด (เนื้อไฟล์)
    วันนี้ปลาทูสด
  menu.txt: |
    ขนมปลาทูน่า
```

ส่วนสำคัญของ `envpod.yaml`

```yaml
      command: ["sh", "-c", "echo SHOP_NAME=$SHOP_NAME; echo APP_THEME=$APP_THEME; echo ARGS: $0 $1; sleep 86400"]
      args: ["$(SHOP_NAME)", "$(NOPE)"]
      env:
        - name: SHOP_NAME                  # ชื่อ env ใน container
          valueFrom:
            configMapKeyRef:
              name: shop-config            # ชื่อ ConfigMap
              key: SHOP_NAME               # key ในกระดาน
```

### ขั้นที่ 1: apply แล้วรอ Pod พร้อม

🐧 **ใน SSH session ของ k8s-lab**

```bash
cd /workspace/010_kubernetes_configmap/02_LAB/labs/lab02-env
kubectl apply -f .
kubectl wait --for=condition=Ready pod/envpod --timeout=120s
```

```text
pod/envpod created
configmap/shop-config created
pod/envpod condition met
```

`kubectl apply -f .` สร้างตามลำดับชื่อไฟล์ (`envpod.yaml` ก่อน `shop-config.yaml`) ถ้าสั่ง `kubectl get pod` เร็วมากอาจเห็น `CreateContainerConfigError` ชั่วครู่แล้วหายเอง เพราะ kubelet ลองใหม่เมื่อ ConfigMap มาถึง (LAB 4 อธิบาย) ถ้าไม่อยากเห็นให้สั่ง `kubectl apply -f shop-config.yaml -f envpod.yaml` แทน

### ขั้นที่ 2: ดูผล

```bash
kubectl logs envpod
kubectl get pod envpod -o jsonpath="{.spec.containers[0].args}"; echo
kubectl exec envpod -- printenv SHOP_NAME APP_THEME
```

```text
SHOP_NAME=ร้านน้องส้ม
APP_THEME=sunset
ARGS: ร้านน้องส้ม $(NOPE)
["$(SHOP_NAME)","$(NOPE)"]
ร้านน้องส้ม
sunset
```

### สิ่งที่เห็น

- `configMapKeyRef` คัดลอกค่าจาก key ที่เลือกมาเป็น env ชื่อที่ตั้งเอง
- `$(SHOP_NAME)` ใน `args` ถูกแทนเป็น `ร้านน้องส้ม` แต่ `$(NOPE)` ที่ไม่มี env ชื่อนี้ **ค้างเป็นข้อความเดิม** ไม่ error
- spec ใน API server ยังเก็บเป็น `["$(SHOP_NAME)","$(NOPE)"]` การแทนค่าเกิดตอน kubelet สร้าง container ส่วน `$SHOP_NAME` (ไม่มีวงเล็บ) ใน `command` เป็นของ shell

**คำถามชวนคิด**

1. ถ้าอยากให้ `args` แสดงข้อความ `$(SHOP_NAME)` ตรง ๆ โดยไม่ถูกแทนค่า ต้องเขียนอย่างไร
2. ถ้าแก้ `SHOP_NAME` ใน `shop-config` ตอนนี้ `kubectl logs envpod` และ `printenv SHOP_NAME` จะเปลี่ยนไหม (คำตอบจริงอยู่ใน LAB 6)

---

## LAB 3: envFrom, prefix และลำดับความสำคัญ

{{FIG:L04}}

**เป้าหมาย:** ถ่าย "ทั้งกระดาน" มาเป็น env ด้วย `envFrom` + `prefix` เห็นว่า key แปลก ๆ กลายเป็น env อย่างไร env ชื่อซ้ำใครชนะ และ `$(VAR)` ในค่าจาก envFrom ไม่ถูกแทนค่า

**ไฟล์:** `labs/lab03-envfrom/envfrom-pod.yaml` (ต้องมี `shop-config` จาก LAB 2)

```yaml
      command: ["sh", "-c", "env | sort | grep -E '^(CFG_|POD_)'; sleep 86400"]
      envFrom:
        - prefix: CFG_                     # ทุก key ได้ชื่อ CFG_<key>
          configMapRef:
            name: shop-config
      env:
        - name: POD_NAMESPACE              # Downward API (บท 003)
          valueFrom:
            fieldRef:
              fieldPath: metadata.namespace
        - name: CFG_APP_THEME              # ชื่อซ้ำกับที่มาจาก envFrom → env ชนะ
          value: "harbor (จาก env)"
```

### ขั้นที่ 1: apply และดู log

🐧 **ใน SSH session ของ k8s-lab**

```bash
cd /workspace/010_kubernetes_configmap/02_LAB/labs/lab03-envfrom
kubectl apply -f envfrom-pod.yaml && kubectl wait --for=condition=Ready pod/envfrom --timeout=120s
kubectl logs envfrom
```

```text
pod/envfrom created
pod/envfrom condition met
CFG_1bad=starts-with-digit
CFG_APP_THEME=harbor (จาก env)
CFG_FOOTER=ร้านใน namespace $(POD_NAMESPACE)
CFG_SHOP_NAME=ร้านน้องส้ม
CFG_announcement.txt=วันนี้ปลาทูสด
CFG_menu.txt=ขนมปลาทูน่า
CFG_shop.name=dot-key
POD_NAMESPACE=default
```

### ขั้นที่ 2: ลำดับความสำคัญ และ $(VAR) ที่ไม่ถูกแทน

```bash
kubectl exec envfrom -- printenv CFG_APP_THEME CFG_FOOTER
```

```text
harbor (จาก env)
ร้านใน namespace $(POD_NAMESPACE)
```

- `CFG_APP_THEME` มีทั้งจาก envFrom (`sunset`) และ env (`harbor (จาก env)`) **env ชนะ**
- `CFG_FOOTER` ยังเป็น `$(POD_NAMESPACE)` ทั้งที่มี env `POD_NAMESPACE=default` เพราะ **`$(VAR)` ในค่าที่มาจาก ConfigMap ผ่าน envFrom ไม่ถูกแทนค่า** (การแทนค่าทำกับ `command`, `args` และ `value` ที่เขียนใน `env` เท่านั้น) ร้านน้องส้มใน LAB 10 จะเจอเรื่องนี้จริง

### ขั้นที่ 3: key แปลก ๆ กับ shell

```bash
kubectl exec envfrom -- sh -c "echo shell อ่าน CFG_SHOP_NAME=\$CFG_SHOP_NAME; echo \$CFG_1bad"
kubectl exec envfrom -- sh -c 'echo $CFG_shop.name'
kubectl get events --field-selector involvedObject.name=envfrom | grep -iE 'invalid|warn' || echo 'ไม่มี event เตือน'
```

```text
shell อ่าน CFG_SHOP_NAME=ร้านน้องส้ม
starts-with-digit
.name
ไม่มี event เตือน
```

Kubernetes v1.37 รับทุก key เป็นชื่อ env (ไม่ข้ามและไม่มี event `InvalidVariableNames` แบบรุ่นเก่า แม้ไม่มี prefix ก็ได้ env ชื่อ `1bad`, `shop.name`) แต่ shell อ่าน `$CFG_shop.name` เป็น `$CFG_shop` (ไม่มีค่า) + `.name` ส่วน `$CFG_1bad` อ่านได้เพราะชื่อเต็มขึ้นต้นด้วย `C` (ถ้าไม่มี prefix `$1bad` จะเป็น `$1` + `bad`)

### สิ่งที่เห็น

- `envFrom` + `prefix: CFG_` ได้ทุก key ของ `shop-config` เป็น `CFG_<key>` ในบรรทัดเดียว
- ชื่อซ้ำ env ชนะ envFrom และ `$(POD_NAMESPACE)` ในค่าจาก envFrom ค้างเป็นข้อความดิบ
- key ที่มีจุดหรือขึ้นต้นด้วยตัวเลขเป็น env ได้ แต่โปรแกรมอ่านลำบาก → ตั้ง key ที่ใช้เป็น env แบบ `UPPER_SNAKE_CASE`

**คำถามชวนคิด**

1. ถ้า Pod มี `envFrom` 2 ตัวที่มี key `SHOP_NAME` เหมือนกัน container จะเห็นค่าจากตัวไหน
2. ถ้าต้องการ footer ที่มีชื่อ namespace จริงโดยใช้ ConfigMap ช่วย ควรออกแบบอย่างไร (ใบ้: ค่าใดควรอยู่ใน `env` ของ Pod)

---

## LAB 4: ConfigMap ที่ไม่มี, optional และข้าม namespace

{{FIG:L05}}

**เป้าหมาย:** เห็นอาการจริงเมื่ออ้าง ConfigMap หรือ key ที่ไม่มี ทั้งแบบ env และ volume ใช้ `optional: true` สร้าง ConfigMap ภายหลังแล้วดูว่า Pod ไหนเริ่มเอง และลองอ้าง ConfigMap ข้าม namespace

**ไฟล์:** `labs/lab04-missing/nocm.yaml` (envFrom อ้าง `not-here`), `nokey.yaml` (อ้าง key `NOPE` ใน `shop-config`), `novol.yaml` (volume อ้าง `not-here`), `optpod.yaml` (อ้างแบบเดียวกันแต่ `optional: true` ทุกจุด), `other-ns.yaml` (Pod ใน namespace `other`) — ต้องมี `shop-config` จาก LAB 2

### ขั้นที่ 1: apply ทั้ง 4 Pod แล้วรอ 25 วินาที

🐧 **ใน SSH session ของ k8s-lab**

```bash
cd /workspace/010_kubernetes_configmap/02_LAB/labs/lab04-missing
kubectl apply -f nocm.yaml -f nokey.yaml -f optpod.yaml -f novol.yaml; date +%T
```

```text
pod/nocm created
pod/nokey created
pod/optpod created
pod/novol created
16:48:23
```

รอราว 25 วินาทีแล้วดูสถานะ

```bash
date +%T; kubectl get pod nocm nokey optpod novol
```

```text
16:48:48
NAME     READY   STATUS                       RESTARTS   AGE
nocm     0/1     CreateContainerConfigError   0          26s
nokey    0/1     CreateContainerConfigError   0          26s
optpod   1/1     Running                      0          26s
novol    0/1     ContainerCreating            0          26s
```

### ขั้นที่ 2: อ่านสาเหตุจาก describe

```bash
kubectl describe pod nocm | grep -E 'Reason|Warning'
kubectl describe pod nokey | grep -E 'Warning' | tail -2
kubectl describe pod novol | sed -n '/Events:/,$p'
```

```text
      Reason:       CreateContainerConfigError
  Type     Reason     Age               From               Message
  Warning  Failed     1s (x4 over 25s)  kubelet            spec.containers{c}: Error: configmap "not-here" not found
  Warning  Failed     1s (x4 over 25s)  kubelet            spec.containers{c}: Error: couldn't find key NOPE in ConfigMap default/shop-config
Events:
  Type     Reason       Age                From               Message
  ----     ------       ----               ----               -------
  Normal   Scheduled    26s                default-scheduler  Successfully assigned default/novol to lab-worker2
  Warning  FailedMount  10s (x6 over 25s)  kubelet            MountVolume.SetUp failed for volume "v" : configmap "not-here" not found
```

ดู `optpod` ที่ใส่ `optional: true`

```bash
kubectl logs optpod
```

```text
X=[] HELLO=[]
total 12
drwxrwxrwx    3 root     root          4096 Oct  5 09:48 .
drwxr-xr-x    1 root     root          4096 Oct  5 09:48 ..
drwxr-xr-x    2 root     root          4096 Oct  5 09:48 ..2026_10_05_09_48_24.2803764025
lrwxrwxrwx    1 root     root            32 Oct  5 09:48 ..data -> ..2026_10_05_09_48_24.2803764025
```

env `X` (key ที่ไม่มี) และ `HELLO` (จาก envFrom ที่ไม่มี) ไม่ถูกตั้ง และโฟลเดอร์ `/etc/opt-cm` ว่าง (มีแค่ `..data`)

### ขั้นที่ 3: สร้าง ConfigMap ที่หายไปภายหลัง

```bash
kubectl create configmap not-here --from-literal=HELLO=world; date +%T
```

```text
configmap/not-here created
16:48:49
```

รอราว 15 วินาทีแล้วดูอีกครั้ง

```bash
date +%T; kubectl get pod nocm nokey optpod novol
kubectl exec novol -- ls /etc/x; kubectl exec nocm -- printenv HELLO
```

```text
16:49:04
NAME     READY   STATUS                       RESTARTS   AGE
nocm     1/1     Running                      0          41s
nokey    0/1     CreateContainerConfigError   0          41s
optpod   1/1     Running                      0          41s
novol    1/1     Running                      0          41s
HELLO
world
```

- `nocm` และ `novol` **เริ่มเองเป็น Running ภายในราว 15 วินาที** โดยไม่ต้องลบ Pod (kubelet ลองใหม่อยู่ตลอด)
- `nokey` **ยังค้าง** — ถูกต้อง เพราะสาเหตุของมันคือ key `NOPE` ใน `shop-config` ไม่ใช่ ConfigMap `not-here` ต้องลบเองตอนเก็บกวาด

### ขั้นที่ 4: optional volume ได้ไฟล์ทีหลัง แต่ env ไม่ได้

ทันทีหลังสร้าง `not-here` ลองดู `optpod`

```bash
kubectl exec optpod -- ls /etc/opt-cm; kubectl exec optpod -- sh -c "echo HELLO=[\$HELLO]"
```

```text
HELLO=[]
```

ตอนนี้ `ls` ยังไม่พิมพ์อะไร (โฟลเดอร์ยังว่าง) และ env `HELLO` ว่าง รอราว 1 นาทีแล้วสั่ง `kubectl exec optpod -- ls /etc/opt-cm` ซ้ำ จะเห็นไฟล์ `HELLO` โผล่ขึ้นมาเอง (ผู้ทดลองวัดซ้ำ 3 รอบได้ 61, 64 และ 43 วินาที ถ้ายังไม่เห็นให้รอถึง 2 นาที) แต่ `HELLO=[]` ยังว่างตลอด เพราะ env อ่านครั้งเดียวตอน container เริ่ม ส่วน volume มี kubelet คอยอัปเดต

### ขั้นที่ 5: อ้างข้าม namespace

`other-ns.yaml` สร้าง Pod `x` ใน namespace `other` ที่ `envFrom` อ้าง `shop-config` (ซึ่งอยู่ใน `default`)

```bash
kubectl create ns other; kubectl apply -f other-ns.yaml
kubectl -n other get pod x; kubectl -n other describe pod x | grep -E 'Warning' | tail -1
```

```text
namespace/other created
pod/x created
NAME   READY   STATUS                       RESTARTS   AGE
x      0/1     CreateContainerConfigError   0          12s
  Warning  Failed     11s (x2 over 11s)  kubelet            spec.containers{c}: Error: configmap "shop-config" not found
```

`configMapRef` ไม่มีช่อง `namespace` Kubernetes หา `shop-config` ใน namespace `other` เท่านั้น จึงได้ `not found` ทั้งที่มีอยู่ใน `default`

### ขั้นที่ 6: เก็บกวาด (เก็บ shop-config และ envpod ไว้)

```bash
kubectl delete -f nocm.yaml -f nokey.yaml -f optpod.yaml -f novol.yaml --now; kubectl delete cm not-here; kubectl delete ns other
```

```text
pod "nocm" deleted from default namespace
pod "nokey" deleted from default namespace
pod "optpod" deleted from default namespace
pod "novol" deleted from default namespace
configmap "not-here" deleted from default namespace
namespace "other" deleted
```

### สิ่งที่เห็น

- env/envFrom อ้างของที่ไม่มี → `CreateContainerConfigError` (`configmap "not-here" not found`, `couldn't find key NOPE in ConfigMap default/shop-config`) ส่วน volume → ค้าง `ContainerCreating` + `FailedMount`
- `optional: true` ทำให้ Pod เริ่มได้ (env ไม่ถูกตั้ง โฟลเดอร์ว่าง)
- สร้าง ConfigMap ภายหลัง Pod ที่ค้างเพราะ ConfigMap นั้นเริ่มเองใน ~15 วินาที ไฟล์ใน optional volume โผล่ภายในราว 1 นาที แต่ env ไม่เปลี่ยน และ Pod ที่ค้างด้วยสาเหตุอื่น (`nokey`) ยังค้าง
- Pod อ้าง ConfigMap ข้าม namespace ไม่ได้

**คำถามชวนคิด**

1. ทำไม `novol` จึงค้างที่ `ContainerCreating` แต่ `nocm` เป็น `CreateContainerConfigError` (คิดถึงลำดับ: mount volume → สร้าง container)
2. ถ้า Deployment ของร้านอ้าง ConfigMap ที่สะกดชื่อผิด rollout จะเป็นอย่างไร และร้านเดิมยังขายได้ไหม (ทวน `maxUnavailable: 0` ในบทที่ 7)

---

## LAB 5: mount เป็นไฟล์

{{FIG:L06}}

**เป้าหมาย:** mount `shop-config` เป็นไฟล์ 3 แบบในคราวเดียว (ทั้งก้อน, `items` + `defaultMode`, `subPath`) ดู symlink `..data` สิทธิ์ไฟล์ และยืนยันว่าเป็น read-only

**ไฟล์:** `labs/lab05-volume/volpod.yaml` (ต้องมี `shop-config` จาก LAB 2 และ **Pod `volpod` ใช้ต่อใน LAB 6**)

| mountPath | ที่มา | สิ่งที่จะเห็น |
|---|---|---|
| `/etc/all` | volume `all` = ทั้ง `shop-config` | ทุก key เป็นไฟล์ |
| `/etc/some` | volume `some` = `items` เฉพาะ `menu.txt` → `menu/today.txt` + `defaultMode: 0400` | ไฟล์เดียว สิทธิ์ `-r--------` |
| `/etc/som/announcement.txt` | volume `all` + `subPath: announcement.txt` | ไฟล์เดียวในโฟลเดอร์ `/etc/som` |

### ขั้นที่ 1: apply และดูทุก key เป็นไฟล์

🐧 **ใน SSH session ของ k8s-lab**

```bash
cd /workspace/010_kubernetes_configmap/02_LAB/labs/lab05-volume
kubectl apply -f volpod.yaml && kubectl wait --for=condition=Ready pod/volpod --timeout=120s
kubectl exec volpod -- ls -la /etc/all
```

```text
pod/volpod created
pod/volpod condition met
total 12
drwxrwxrwx    3 root     root          4096 Oct  5 09:53 .
drwxr-xr-x    1 root     root          4096 Oct  5 09:53 ..
drwxr-xr-x    2 root     root          4096 Oct  5 09:53 ..2026_10_05_09_53_05.3156628874
lrwxrwxrwx    1 root     root            32 Oct  5 09:53 ..data -> ..2026_10_05_09_53_05.3156628874
lrwxrwxrwx    1 root     root            11 Oct  5 09:53 1bad -> ..data/1bad
lrwxrwxrwx    1 root     root            16 Oct  5 09:53 APP_THEME -> ..data/APP_THEME
lrwxrwxrwx    1 root     root            13 Oct  5 09:53 FOOTER -> ..data/FOOTER
lrwxrwxrwx    1 root     root            16 Oct  5 09:53 SHOP_NAME -> ..data/SHOP_NAME
lrwxrwxrwx    1 root     root            23 Oct  5 09:53 announcement.txt -> ..data/announcement.txt
lrwxrwxrwx    1 root     root            15 Oct  5 09:53 menu.txt -> ..data/menu.txt
lrwxrwxrwx    1 root     root            16 Oct  5 09:53 shop.name -> ..data/shop.name
```

ทุก key เป็น symlink ชี้ `..data/<key>` และ `..data` ชี้โฟลเดอร์ชื่อเวลา (เวลาใน Pod เป็น UTC ช้ากว่าเวลาไทย 7 ชั่วโมง)

### ขั้นที่ 2: items และ defaultMode

```bash
kubectl exec volpod -- ls -laR /etc/some
```

```text
/etc/some:
total 12
drwxrwxrwx    3 root     root          4096 Oct  5 09:53 .
drwxr-xr-x    1 root     root          4096 Oct  5 09:53 ..
drwxr-xr-x    3 root     root          4096 Oct  5 09:53 ..2026_10_05_09_53_05.3837634004
lrwxrwxrwx    1 root     root            32 Oct  5 09:53 ..data -> ..2026_10_05_09_53_05.3837634004
lrwxrwxrwx    1 root     root            11 Oct  5 09:53 menu -> ..data/menu

/etc/some/..2026_10_05_09_53_05.3837634004:
total 12
drwxr-xr-x    3 root     root          4096 Oct  5 09:53 .
drwxrwxrwx    3 root     root          4096 Oct  5 09:53 ..
drwxr-xr-x    2 root     root          4096 Oct  5 09:53 menu

/etc/some/..2026_10_05_09_53_05.3837634004/menu:
total 12
drwxr-xr-x    2 root     root          4096 Oct  5 09:53 .
drwxr-xr-x    3 root     root          4096 Oct  5 09:53 ..
-r--------    1 root     root            34 Oct  5 09:53 today.txt
```

มีแค่ `menu/today.txt` (key อื่นไม่ถูก mount) และสิทธิ์ `-r--------` ตาม `defaultMode: 0400`

### ขั้นที่ 3: อ่านเนื้อไฟล์ และ subPath

```bash
kubectl exec volpod -- cat /etc/all/SHOP_NAME; echo; kubectl exec volpod -- cat /etc/som/announcement.txt
kubectl exec volpod -- ls -la /etc/som
```

```text
ร้านน้องส้ม
วันนี้ปลาทูสด
total 12
drwxr-xr-x    2 root     root          4096 Oct  5 09:53 .
drwxr-xr-x    1 root     root          4096 Oct  5 09:53 ..
-rw-r--r--    1 root     root            40 Oct  5 09:53 announcement.txt
```

ไฟล์ `SHOP_NAME` ไม่มี newline ท้าย (ค่าใน YAML เป็นบรรทัดเดียว) จึงต้อง `echo` คั่น ส่วนไฟล์ subPath เป็น **ไฟล์จริง ไม่ใช่ symlink** สิทธิ์ปกติ `-rw-r--r--` (0644)

### ขั้นที่ 4: read-only และฟิลด์ของ volume configMap

```bash
kubectl exec volpod -- mount | grep -E 'etc/(all|some|som)'
kubectl exec volpod -- sh -c 'echo hack > /etc/all/menu.txt'
kubectl explain pod.spec.volumes.configMap | grep -E '^  [a-z]'
```

```text
/dev/sdd on /etc/all type ext4 (ro,relatime)
/dev/sdd on /etc/some type ext4 (ro,relatime)
/dev/sdd on /etc/som/announcement.txt type ext4 (ro,relatime)
sh: can't create /etc/all/menu.txt: Read-only file system
command terminated with exit code 1
  defaultMode	<integer>
  defaultUser	<integer>
  items	<[]KeyToPath>
  name	<string>
  optional	<boolean>
```

ทั้งสามจุด mount แบบ `ro` เขียนไม่ได้ (ชื่ออุปกรณ์ `/dev/sdd` ขึ้นกับเครื่อง) ฟิลด์ของ volume configMap คือ `defaultMode`, `items`, `name`, `optional` ที่เรียนในบทนี้ (`defaultUser` เป็นฟิลด์ใหม่ที่ยังไม่ใช้ในวิชานี้)

ยังไม่ต้องเก็บกวาด `volpod`, `envpod`, `envfrom` และ `shop-config` ใช้ต่อใน LAB 6

### สิ่งที่เห็น

- volume ทำให้ทุก key เป็นไฟล์ (symlink ผ่าน `..data`) `items` เลือก key และตั้ง path ใหม่ `defaultMode: 0400` → `-r--------`
- subPath ได้ไฟล์จริงไฟล์เดียวในโฟลเดอร์ `/etc/som` โดยไม่บังทั้งโฟลเดอร์
- ทุก mount เป็น read-only (`Read-only file system`)

**คำถามชวนคิด**

1. ถ้า mount volume ทั้งก้อนที่ `/etc` แทน `/etc/all` จะเกิดอะไรกับไฟล์ระบบอื่นใน `/etc` ของ container
2. ทำไม kubelet ต้องทำ `..data` เป็น symlink แทนที่จะเขียนทับไฟล์ตรง ๆ (คำตอบอยู่ใน LAB 6)
