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

---

## LAB 6: อัปเดตเองและจับเวลา

{{FIG:L07}}

**เป้าหมาย:** แก้ `shop-config` แล้วจับเวลาว่าไฟล์ใน volume เปลี่ยนเมื่อไร เทียบกับไฟล์ subPath และ env ใน `envpod` ในการทดลองเดียวกัน และเห็น `..data` สลับไปโฟลเดอร์ใหม่

**ไฟล์:** `labs/lab06-update/watch.sh` (ต้องมี `envpod` จาก LAB 2 และ `volpod` จาก LAB 5)

สคริปต์ทำซ้ำ 3 รอบ (ค่าเริ่ม) รอบละ: `kubectl patch cm shop-config` เปลี่ยน `announcement.txt=ปลาทูรอบN` และ `SHOP_NAME=ร้านใหม่N` → วนอ่าน `/etc/all/announcement.txt` ใน `volpod` ทุก 1 วินาทีจนได้ค่าใหม่ (ไม่เกิน 180 วินาที) → พิมพ์ค่าจาก volume, subPath และ env

```bash
kubectl patch cm shop-config --type merge \
  -p "{\"data\":{\"announcement.txt\":\"$v\n\",\"SHOP_NAME\":\"ร้านใหม่$r\"}}" >/dev/null
```

### ขั้นที่ 1: รันสคริปต์ (ราว 4–5 นาที)

🐧 **ใน SSH session ของ k8s-lab**

```bash
cd /workspace/010_kubernetes_configmap/02_LAB/labs/lab06-update
./watch.sh
```

```text
รอบ 1: 16:53:11 patch shop-config → announcement.txt=ปลาทูรอบ1, SHOP_NAME=ร้านใหม่1
  volume /etc/all/announcement.txt เปลี่ยนหลัง 85 วินาที: ปลาทูรอบ1
  volume /etc/all/SHOP_NAME             : ร้านใหม่1
  subPath /etc/som/announcement.txt     : วันนี้ปลาทูสด
  env SHOP_NAME ใน envpod               : ร้านน้องส้ม
รอบ 2: 16:54:41 patch shop-config → announcement.txt=ปลาทูรอบ2, SHOP_NAME=ร้านใหม่2
  volume /etc/all/announcement.txt เปลี่ยนหลัง 55 วินาที: ปลาทูรอบ2
  volume /etc/all/SHOP_NAME             : ร้านใหม่2
  subPath /etc/som/announcement.txt     : วันนี้ปลาทูสด
  env SHOP_NAME ใน envpod               : ร้านน้องส้ม
รอบ 3: 16:55:41 patch shop-config → announcement.txt=ปลาทูรอบ3, SHOP_NAME=ร้านใหม่3
  volume /etc/all/announcement.txt เปลี่ยนหลัง 62 วินาที: ปลาทูรอบ3
  volume /etc/all/SHOP_NAME             : ร้านใหม่3
  subPath /etc/som/announcement.txt     : วันนี้ปลาทูสด
  env SHOP_NAME ใน envpod               : ร้านน้องส้ม
--- ..data ชี้ไปโฟลเดอร์เวลาใหม่:
lrwxrwxrwx    1 root     root            32 Oct  5 09:56 ..data -> ..2026_10_05_09_56_42.2491344353
lrwxrwxrwx    1 root     root            11 Oct  5 09:53 1bad -> ..data/1bad
lrwxrwxrwx    1 root     root            16 Oct  5 09:53 APP_THEME -> ..data/APP_THEME
lrwxrwxrwx    1 root     root            13 Oct  5 09:53 FOOTER -> ..data/FOOTER
lrwxrwxrwx    1 root     root            16 Oct  5 09:53 SHOP_NAME -> ..data/SHOP_NAME
lrwxrwxrwx    1 root     root            23 Oct  5 09:53 announcement.txt -> ..data/announcement.txt
lrwxrwxrwx    1 root     root            15 Oct  5 09:53 menu.txt -> ..data/menu.txt
lrwxrwxrwx    1 root     root            16 Oct  5 09:53 shop.name -> ..data/shop.name
```

ตัวเลขวินาทีในเครื่องนักศึกษาจะต่างไป (การทดลองอีกรอบก่อนหน้าได้ 65 / 70 / 85 วินาที) ช่วงที่คาดได้คือราว 30–90 วินาที ถ้าสคริปต์พิมพ์ `เกิน 180 วินาทีแล้วยังไม่เปลี่ยน` ให้ดู [Troubleshooting](#troubleshooting)

### ขั้นที่ 2: ดู ..data อีกครั้ง

```bash
kubectl exec volpod -- ls -la /etc/all | grep -E '(\.\.data|announcement\.txt) ->'
```

```text
lrwxrwxrwx    1 root     root            32 Oct  5 09:56 ..data -> ..2026_10_05_09_56_42.2491344353
lrwxrwxrwx    1 root     root            23 Oct  5 09:53 announcement.txt -> ..data/announcement.txt
```

symlink ของไฟล์ยังเป็นเวลาเดิม (`09:53`) แต่ `..data` ชี้โฟลเดอร์ใหม่ (`09:56`) kubelet เขียนชุดใหม่ทั้งหมดแล้ว "สลับป้ายลูกศร" ทีเดียว ทุกไฟล์จึงเปลี่ยนพร้อมกัน (`announcement.txt` และ `SHOP_NAME` เป็นรอบเดียวกันเสมอ)

### ขั้นที่ 3: เก็บกวาด LAB 2–6

```bash
cd /workspace/010_kubernetes_configmap/02_LAB/labs
kubectl delete pod envpod envfrom volpod --now; kubectl delete cm shop-config; kubectl get pod,cm
```

```text
pod "envpod" deleted from default namespace
pod "envfrom" deleted from default namespace
pod "volpod" deleted from default namespace
configmap "shop-config" deleted from default namespace
NAME                         DATA   AGE
configmap/kube-root-ca.crt   1      13m
```

### สิ่งที่เห็น

- ไฟล์ใน volume เปลี่ยนเองโดยไม่ restart Pod แต่ใช้เวลา **85 / 55 / 62 วินาที** (ราว 1 นาที บางครั้งเกือบ 1.5 นาที) เพราะ kubelet sync เป็นรอบ
- ไฟล์ **subPath ไม่เปลี่ยนเลย** (`วันนี้ปลาทูสด` ทุกรอบ) และ **env ไม่เปลี่ยนเลย** (`ร้านน้องส้ม` ทุกรอบ)
- `..data` ชี้โฟลเดอร์เวลาใหม่ ไฟล์ทั้งชุดจึงเปลี่ยนพร้อมกันแบบ atomic

**คำถามชวนคิด**

1. ถ้าแอปของเราอ่าน `SHOP_NAME` จาก env แต่อ่านประกาศจากไฟล์ใน volume แก้ ConfigMap แล้วผู้ใช้จะเห็นอะไรเปลี่ยนก่อน
2. ทำไมแต่ละรอบใช้เวลาไม่เท่ากัน (ใบ้: kubelet ไม่ได้เริ่มนับเวลาตอนที่เรา patch)

---

## LAB 7: แอปต้องโหลดใหม่เอง

{{FIG:L08}}

**เป้าหมาย:** เห็นว่าไฟล์ตั้งค่า nginx ใน volume เปลี่ยนแล้วแต่ nginx ยังใช้ค่าเก่าจนกว่าจะ `nginx -s reload` และใช้ `kubectl rollout restart` กับ checksum annotation ให้ Deployment ได้ Pod ใหม่ที่อ่านค่าล่าสุด

**ไฟล์:** `labs/lab07-reload/`

| ไฟล์ | เนื้อหา |
|---|---|
| `nginx-conf.yaml` | ConfigMap `nginx-conf` key `default.conf` ตอบ `menu v1` |
| `nginx-conf-v2.yaml`, `nginx-conf-v3.yaml` | ConfigMap ชื่อเดียวกัน ตอบ `menu v2` / `menu v3` (apply = แก้กระดานเดิม) |
| `ngx.yaml` | Pod `ngx` (nginx:1.27-alpine) mount `nginx-conf` ทับ `/etc/nginx/conf.d` ทั้งโฟลเดอร์ |
| `plain-deploy.yaml` | Deployment `plain` nginx แบบเดียวกัน 1 replica |

เนื้อหาของ `nginx-conf.yaml`

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: nginx-conf
data:
  default.conf: |
    server { listen 80; location / { default_type text/plain; return 200 "menu v1\n"; } }
```

> LAB นี้ใช้ไฟล์ `nginx-conf-v2.yaml`/`nginx-conf-v3.yaml` แทน `kubectl patch` เพราะค่าที่เป็นไฟล์ nginx มีทั้ง `"` และ `\n` ถ้าเขียนเป็น JSON ใน patch ต้อง escape หลายชั้นและพลาดง่าย (การทดลองรอบแรกได้ `\n` ดิบติดไปในไฟล์) การแก้ด้วยไฟล์ YAML แล้ว `kubectl apply -f` อ่านง่ายและเก็บใน git ได้

### ขั้นที่ 1: apply และเรียก nginx

🐧 **ใน SSH session ของ k8s-lab**

```bash
cd /workspace/010_kubernetes_configmap/02_LAB/labs/lab07-reload
ls; kubectl apply -f nginx-conf.yaml -f ngx.yaml -f plain-deploy.yaml
kubectl wait --for=condition=Ready pod/ngx --timeout=120s; kubectl rollout status deploy/plain --timeout=120s
kubectl exec ngx -- curl -s 127.0.0.1/; kubectl exec deploy/plain -- curl -s 127.0.0.1/
```

```text
nginx-conf-v2.yaml
nginx-conf-v3.yaml
nginx-conf.yaml
ngx.yaml
plain-deploy.yaml
configmap/nginx-conf created
pod/ngx created
deployment.apps/plain created
pod/ngx condition met
deployment "plain" successfully rolled out
menu v1
menu v1
```

> **ใช้ `127.0.0.1` ไม่ใช่ `localhost`** — `wget` ใน image ไปที่ `localhost` แล้วเลือก IPv6 `::1` ก่อน แต่ไฟล์ตั้งค่านี้ฟังแค่ IPv4 (`listen 80;`) ผลจริง
>
> ```text
> $ kubectl exec ngx -- wget -qO- localhost/
> wget: can't connect to remote host: Connection refused
> command terminated with exit code 1
> $ kubectl exec ngx -- wget -qO- 127.0.0.1/
> menu v1
> ```

### ขั้นที่ 2: เปลี่ยนเป็น v2 แล้วรอไฟล์

คำสั่งนี้ apply ConfigMap ชุดใหม่แล้ววนตรวจทุก 2 วินาทีว่าไฟล์ใน `ngx` มีคำว่า `v2` หรือยัง (`2>/dev/null` ซ่อนข้อความ `command terminated with exit code 1` ที่ `grep` พิมพ์ทุกรอบที่ยังไม่เจอ)

```bash
kubectl apply -f nginx-conf-v2.yaml; t0=$(date +%s); until kubectl exec ngx -- grep -q v2 /etc/nginx/conf.d/default.conf 2>/dev/null; do [ $(( $(date +%s)-t0 )) -gt 180 ] && break; sleep 2; done; echo "ไฟล์ใน ngx เปลี่ยนหลัง $(( $(date +%s)-t0 )) วินาที"
```

```text
configmap/nginx-conf configured
ไฟล์ใน ngx เปลี่ยนหลัง 75 วินาที
```

ดูไฟล์และเรียก nginx

```bash
kubectl exec ngx -- cat /etc/nginx/conf.d/default.conf; kubectl exec ngx -- curl -s 127.0.0.1/
```

```text
server { listen 80; location / { default_type text/plain; return 200 "menu v2\n"; } }
menu v1
```

**ไฟล์เป็น v2 แล้ว แต่ nginx ยังตอบ `menu v1`** เพราะ nginx อ่านไฟล์ตั้งค่าครั้งเดียวตอนเริ่ม

### ขั้นที่ 3: สั่ง nginx reload

```bash
kubectl exec ngx -- nginx -s reload; sleep 1; kubectl exec ngx -- curl -s 127.0.0.1/
```

```text
2026/10/05 10:07:20 [notice] 310#310: signal process started
menu v2
```

### ขั้นที่ 4: v3 — Pod เดี่ยวกับ Deployment

```bash
kubectl apply -f nginx-conf-v3.yaml; t0=$(date +%s); until kubectl exec ngx -- grep -q v3 /etc/nginx/conf.d/default.conf 2>/dev/null; do [ $(( $(date +%s)-t0 )) -gt 180 ] && break; sleep 2; done; echo "ไฟล์ใน ngx เปลี่ยนหลัง $(( $(date +%s)-t0 )) วินาที"
kubectl exec ngx -- curl -s 127.0.0.1/; kubectl exec deploy/plain -- cat /etc/nginx/conf.d/default.conf; kubectl exec deploy/plain -- curl -s 127.0.0.1/
kubectl exec ngx -- nginx -s reload; sleep 1; kubectl exec ngx -- curl -s 127.0.0.1/
```

```text
configmap/nginx-conf configured
ไฟล์ใน ngx เปลี่ยนหลัง 63 วินาที
menu v2
server { listen 80; location / { default_type text/plain; return 200 "menu v3\n"; } }
menu v1
2026/10/05 10:08:32 [notice] 546#546: signal process started
menu v3
```

(เลข process ในบรรทัด `[notice]` ในเครื่องนักศึกษาจะต่างไป) สังเกต Deployment `plain`: ไฟล์เป็น v3 แล้วแต่ยังตอบ **`menu v1`** เพราะไม่เคยมีใคร reload เลยตั้งแต่เริ่ม

### ขั้นที่ 5: rollout restart ให้ Pod ใหม่

แทนที่จะ `exec` เข้าไป reload ทีละ Pod ให้ Deployment สร้าง Pod ใหม่ ซึ่งอ่านไฟล์ล่าสุดตั้งแต่เริ่ม

```bash
kubectl rollout restart deploy/plain && kubectl rollout status deploy/plain --timeout=120s
kubectl exec deploy/plain -- curl -s 127.0.0.1/
kubectl get deploy plain -o jsonpath='{.spec.template.metadata.annotations}'; echo
```

```text
deployment.apps/plain restarted
Waiting for deployment "plain" rollout to finish: 1 old replicas are pending termination...
Waiting for deployment "plain" rollout to finish: 1 old replicas are pending termination...
deployment "plain" successfully rolled out
menu v3
{"kubectl.kubernetes.io/restartedAt":"2026-10-05T17:08:34+07:00"}
```

`rollout restart` ไม่มีเวทมนตร์ มันแค่เติม annotation `kubectl.kubernetes.io/restartedAt` ใน Pod template ทำให้ template เปลี่ยน → rolling update ตามปกติของบทที่ 7

### ขั้นที่ 6: checksum annotation

อีกวิธีคือใส่ hash ของเนื้อหา ConfigMap ไว้ใน annotation ของ template เนื้อหาเปลี่ยน = hash เปลี่ยน = rollout (Helm ใช้วิธีนี้ ในบทนี้คำนวณด้วยมือ)

```bash
SUM=$(kubectl get cm nginx-conf -o jsonpath='{.data}' | sha256sum | cut -c1-12); echo $SUM; kubectl patch deploy plain -p "{\"spec\":{\"template\":{\"metadata\":{\"annotations\":{\"checksum/config\":\"$SUM\"}}}}}" && kubectl rollout status deploy/plain --timeout=120s
kubectl get deploy plain -o jsonpath='{.spec.template.metadata.annotations}'; echo; kubectl rollout history deploy/plain
```

```text
a7aed9955c80
deployment.apps/plain patched
Waiting for deployment "plain" rollout to finish: 1 old replicas are pending termination...
Waiting for deployment "plain" rollout to finish: 1 old replicas are pending termination...
deployment "plain" successfully rolled out
{"checksum/config":"a7aed9955c80","kubectl.kubernetes.io/restartedAt":"2026-10-05T17:08:34+07:00"}
deployment.apps/plain 
REVISION  CHANGE-CAUSE
1         <none>
2         <none>
3         <none>
```

REVISION 2 มาจาก `rollout restart` และ REVISION 3 มาจาก checksum ค่า `a7aed9955c80` จะเหมือนกันทุกเครื่องถ้า ConfigMap เป็น v3 ตรงกัน

### ขั้นที่ 7 (สังเกตเพิ่ม): nginx กับ Pod Security

Pod nginx นี้รันเป็น root ฟังพอร์ต 80 ใช้ได้ใน `default` ที่ไม่มีป้าย Pod Security ถ้าเอาไปใช้ใน namespace ที่ตั้ง `warn: restricted` (แบบ `som-shop` ใน LAB 10) จะได้คำเตือน ลองแบบ server dry-run (ไม่สร้างจริง)

```bash
kubectl create ns psa-demo; kubectl label ns psa-demo pod-security.kubernetes.io/warn=restricted; kubectl -n psa-demo apply -f nginx-conf.yaml -f ngx.yaml --dry-run=server; kubectl delete ns psa-demo
```

```text
namespace/psa-demo created
namespace/psa-demo labeled
configmap/nginx-conf created (server dry run)
Warning: would violate PodSecurity "restricted:latest": allowPrivilegeEscalation != false (container "nginx" must set securityContext.allowPrivilegeEscalation=false), unrestricted capabilities (container "nginx" must set securityContext.capabilities.drop=["ALL"]), runAsNonRoot != true (pod or container "nginx" must set securityContext.runAsNonRoot=true), seccompProfile (pod or container "nginx" must set securityContext.seccompProfile.type to "RuntimeDefault" or "Localhost")
pod/ngx created (server dry run)
namespace "psa-demo" deleted
```

เป็นแค่ `warn` Pod ยังสร้างได้ (บทที่ 4) ร้านน้องส้มใน LAB 10 ตั้ง `securityContext` ครบจึงไม่มีคำเตือน

### ขั้นที่ 8: เก็บกวาด

```bash
kubectl delete -f ngx.yaml -f plain-deploy.yaml -f nginx-conf.yaml
```

```text
pod "ngx" deleted from default namespace
deployment.apps "plain" deleted from default namespace
configmap "nginx-conf" deleted from default namespace
```

ถ้าจะทำ LAB นี้ซ้ำ รอให้ Pod เก่าหายก่อน (`kubectl get pod` ว่าง) ไม่อย่างนั้นอาจได้ `Warning: Detected changes to resource ngx which is currently being deleted`

### สิ่งที่เห็น

- ไฟล์ใน volume ของ nginx เปลี่ยนเองหลัง **75 วินาที** (v2) และ **63 วินาที** (v3) แต่ nginx ยังตอบค่าเก่าจนกว่าจะ `nginx -s reload`
- Deployment `plain` ที่ไม่มีใคร reload ตอบ `menu v1` ทั้งที่ไฟล์เป็น v3 → `rollout restart` ได้ Pod ใหม่ตอบ `menu v3`
- `rollout restart` = เติม annotation `restartedAt` ส่วน checksum annotation ให้ rollout ตามเนื้อหา config (REVISION 3)

**คำถามชวนคิด**

1. ถ้า Deployment มี 3 Pod การ `kubectl exec ... nginx -s reload` ทีละ Pod มีข้อเสียอะไรเทียบกับ `rollout restart`
2. ข้อดีของ checksum annotation เหนือ `rollout restart` คืออะไร เมื่อเก็บ manifest ไว้ใน git

---

## LAB 8: immutable

{{FIG:L09}}

**เป้าหมาย:** สร้าง ConfigMap `immutable: true` ลองแก้ด้วยทุกวิธี (patch, apply, replace) เห็นว่าแก้ได้แค่ metadata และต้องลบสร้างใหม่

**ไฟล์:** `labs/lab08-immutable/frozen.yaml`

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: frozen
immutable: true
data:
  PRICE: "99"
```

### ขั้นที่ 1: สร้างและดู

🐧 **ใน SSH session ของ k8s-lab**

```bash
cd /workspace/010_kubernetes_configmap/02_LAB/labs/lab08-immutable
kubectl apply -f frozen.yaml; kubectl get cm frozen -o yaml | grep -E "immutable|PRICE"
```

```text
configmap/frozen created
  PRICE: "99"
immutable: true
      {"apiVersion":"v1","data":{"PRICE":"99"},"immutable":true,"kind":"ConfigMap","metadata":{"annotations":{},"name":"frozen","namespace":"default"}}
```

บรรทัดสุดท้ายคือ annotation `last-applied-configuration` ที่ `kubectl apply` บันทึกไว้

### ขั้นที่ 2: ลองแก้ทุกวิธี

```bash
kubectl patch cm frozen --type merge -p '{"data":{"PRICE":"79"}}'
kubectl patch cm frozen --type merge -p '{"immutable":false}'
sed 's/"99"/"79"/' frozen.yaml | kubectl apply -f -
sed 's/"99"/"79"/' frozen.yaml | kubectl replace -f -
```

```text
The ConfigMap "frozen" is invalid: data: Forbidden: field is immutable when `immutable` is set
The ConfigMap "frozen" is invalid: immutable: Forbidden: field is immutable when `immutable` is set
The ConfigMap "frozen" is invalid: data: Forbidden: field is immutable when `immutable` is set
The ConfigMap "frozen" is invalid: data: Forbidden: field is immutable when `immutable` is set
```

ทั้งแก้ราคา (`data`) และพยายามปิด immutable ถูกปฏิเสธที่ API server

> **อย่าใช้ `kubectl edit cm frozen` เพื่อทดลองข้อนี้** ถ้า terminal ไม่ใช่แบบโต้ตอบ (สคริปต์, `ssh ... "คำสั่ง"`) `kubectl edit` จะเปิด vim ค้างไว้ (การทดลองได้ `Vim: Warning: Output is not to a terminal` แล้วต้อง kill process) ถ้าใช้ใน SSH session ปกติ vim จะเปิดได้ แก้แล้วบันทึกก็จะได้ error แบบเดียวกัน ออกโดยไม่บันทึกด้วย `:q!`

### ขั้นที่ 3: แก้ metadata ได้

```bash
kubectl label cm frozen tier=menu; kubectl get cm frozen --show-labels
```

```text
configmap/frozen labeled
NAME     DATA   AGE   LABELS
frozen   1      1s    tier=menu
```

### ขั้นที่ 4: เปลี่ยนค่าด้วยการลบแล้วสร้างใหม่

```bash
kubectl delete cm frozen; sed "s/\"99\"/\"79\"/" frozen.yaml | kubectl apply -f -; kubectl get cm frozen -o jsonpath="{.data.PRICE} {.immutable}"; echo
```

```text
configmap "frozen" deleted from default namespace
configmap/frozen created
79 true
```

ในระบบจริงการลบ ConfigMap ที่ Pod ใช้อยู่เสี่ยง (Pod ที่เริ่มใหม่ระหว่างนั้นจะค้าง) วิธีที่ดีกว่าคือสร้าง **ชื่อใหม่** (`frozen-v2`) แล้วชี้ Deployment ไปชื่อใหม่ ซึ่ง LAB 10 ขั้น E จะทำให้ดู

### ขั้นที่ 5: เก็บกวาด

```bash
kubectl delete cm frozen
```

```text
configmap "frozen" deleted from default namespace
```

### สิ่งที่เห็น

- `immutable: true` → แก้ `data` ไม่ได้ทั้ง patch/apply/replace และเปลี่ยน `immutable` เป็น false ไม่ได้ (`Forbidden: field is immutable when ...`)
- แก้ label (metadata) ได้ เปลี่ยนค่าต้องลบสร้างใหม่หรือใช้ชื่อใหม่

**คำถามชวนคิด**

1. ทำไม immutable ช่วยลดภาระของ API server ในคลัสเตอร์ที่มี ConfigMap และ Pod จำนวนมาก
2. ถ้าทีมใช้ชื่อ ConfigMap แบบ `-v1`, `-v2`, `-v3` + immutable ต้องมีขั้นตอนอะไรเพิ่ม เพื่อไม่ให้ ConfigMap รุ่นเก่าค้างเต็มคลัสเตอร์

---

## LAB 9: kustomize configMapGenerator

{{FIG:L10}}

**เป้าหมาย:** ใช้ kustomize ที่ติดมากับ kubectl สร้าง ConfigMap ชื่อมี hash จากเนื้อหา แก้เนื้อหาแล้วเห็นชื่อใหม่และ Deployment rollout เอง

**ไฟล์:** `labs/lab09-kustomize/kz/kustomization.yaml`, `announcement.txt` (`ประกาศ v1`), `deploy.yaml` (Deployment `kz-web` busybox ที่ `envFrom` อ้างชื่อสั้น `web-config`)

```yaml
configMapGenerator:
- name: web-config
  literals:
  - SHOP_NAME=ร้านน้องส้ม
  files:
  - announcement.txt        # key = ชื่อไฟล์, ค่า = เนื้อไฟล์
resources:
- deploy.yaml
```

### ขั้นที่ 1: ดูผลก่อน apply

🐧 **ใน SSH session ของ k8s-lab**

```bash
cd /workspace/010_kubernetes_configmap/02_LAB/labs/lab09-kustomize
kubectl kustomize kz
```

```text
apiVersion: v1
data:
  SHOP_NAME: ร้านน้องส้ม
  announcement.txt: |
    ประกาศ v1
kind: ConfigMap
metadata:
  name: web-config-gh5tkgmddg
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kz-web
spec:
  replicas: 1
  selector:
    matchLabels:
      app: kz-web
  template:
    metadata:
      labels:
        app: kz-web
    spec:
      containers:
      - command:
        - sleep
        - "86400"
        envFrom:
        - configMapRef:
            name: web-config-gh5tkgmddg
        image: busybox:1.36
        name: c
      terminationGracePeriodSeconds: 1
```

ConfigMap ได้ชื่อ `web-config-gh5tkgmddg` และ `envFrom` ใน Deployment ถูกแก้เป็นชื่อเดียวกันให้เอง

### ขั้นที่ 2: apply -k

```bash
kubectl apply -k kz && kubectl rollout status deploy/kz-web --timeout=120s
kubectl get deploy kz-web -o jsonpath='{.spec.template.spec.containers[0].envFrom}'; echo; kubectl exec deploy/kz-web -- printenv announcement.txt
```

```text
configmap/web-config-gh5tkgmddg created
deployment.apps/kz-web created
Waiting for deployment "kz-web" rollout to finish: 0 of 1 updated replicas are available...
deployment "kz-web" successfully rolled out
[{"configMapRef":{"name":"web-config-gh5tkgmddg"}}]
ประกาศ v1

```

(บรรทัดว่างท้ายมาจาก newline ในไฟล์ `announcement.txt`)

### ขั้นที่ 3: แก้เนื้อหาแล้ว apply อีกครั้ง

```bash
printf 'ประกาศ v2\n' > kz/announcement.txt; kubectl apply -k kz && kubectl rollout status deploy/kz-web --timeout=120s
kubectl get cm | grep web-config; kubectl rollout history deploy/kz-web
kubectl exec deploy/kz-web -- printenv announcement.txt SHOP_NAME
```

```text
configmap/web-config-6db7mkcg8t created
deployment.apps/kz-web configured
Waiting for deployment "kz-web" rollout to finish: 1 old replicas are pending termination...
Waiting for deployment "kz-web" rollout to finish: 1 old replicas are pending termination...
deployment "kz-web" successfully rolled out
web-config-6db7mkcg8t   2      1s
web-config-gh5tkgmddg   2      2s
deployment.apps/kz-web 
REVISION  CHANGE-CAUSE
1         <none>
2         <none>

ประกาศ v2

ร้านน้องส้ม
```

- เนื้อหาเปลี่ยน → ชื่อใหม่ `web-config-6db7mkcg8t` → Deployment `configured` และ rollout เป็น REVISION 2 **โดยไม่ต้องสั่ง restart**
- Pod ใหม่เห็น `ประกาศ v2` ทันทีที่เริ่ม (env ของ Pod ใหม่)
- ConfigMap รุ่นเก่า `web-config-gh5tkgmddg` **ยังอยู่** ถ้า `rollout undo` ก็จะกลับไปใช้ตัวเก่าได้ทันที

> ใช้ `printf` แทนการแก้ด้วย editor เพื่อให้เนื้อไฟล์ตรงทุกไบต์ (hash ขึ้นกับทุกไบต์รวม newline ท้ายไฟล์) ไฟล์เหมือนกันจะได้ชื่อ `gh5tkgmddg` / `6db7mkcg8t` ตรงกับเอกสารทุกเครื่อง

### ขั้นที่ 4: delete -k ไม่ลบรุ่นเก่า แล้วเก็บกวาด

```bash
kubectl delete -k kz; kubectl get cm | grep web-config
kubectl get cm -o name | grep web-config | xargs -r kubectl delete; printf 'ประกาศ v1\n' > kz/announcement.txt; kubectl get cm,deploy
```

```text
configmap "web-config-6db7mkcg8t" deleted from default namespace
deployment.apps "kz-web" deleted from default namespace
web-config-gh5tkgmddg   2      3s
configmap "web-config-gh5tkgmddg" deleted from default namespace
NAME                         DATA   AGE
configmap/kube-root-ca.crt   1      26m
```

`kubectl delete -k kz` ลบเฉพาะชื่อที่ kustomize สร้างจากไฟล์ปัจจุบัน ตัวเก่าค้างต้องลบเอง และคืน `announcement.txt` เป็น `ประกาศ v1` ไว้สำหรับทำซ้ำ

### สิ่งที่เห็น

- `configMapGenerator` สร้าง `web-config-<hash>` และแก้ชื่อใน Deployment ให้ตรง
- แก้เนื้อหา → hash ใหม่ → Deployment rollout เอง (REVISION 2) แบบเดียวกับการตั้งชื่อใหม่ด้วยมือ แต่ไม่ต้องจำ
- ConfigMap รุ่นเก่าค้างทั้งหลัง apply และหลัง `delete -k` ต้องลบเอง

**คำถามชวนคิด**

1. ถ้าลืม `printf 'ประกาศ v1\n' > kz/announcement.txt` แล้วทำ LAB นี้ซ้ำ ชื่อ ConfigMap ในขั้นที่ 1 จะเป็นอะไร
2. ข้อดีของการที่ ConfigMap รุ่นเก่ายังค้างอยู่ มีผลต่อ `kubectl rollout undo` อย่างไร

---

## LAB 10: LAB สุดท้าย: ร้านน้องส้มเปลี่ยนป้ายไม่ต้อง build ใหม่

{{FIG:L11}}

**เป้าหมาย:** เริ่มจากร้านแบบท้ายบทที่ 9 (ค่าร้านเขียนตรงใน env) แล้วย้าย **ชื่อร้าน ธีม และโปรโมชัน** ไปไว้ใน ConfigMap `som-web-config` (ใช้ผ่าน `envFrom`) และย้าย **ประกาศหน้าร้าน** ไปไว้ใน ConfigMap `som-announcement` (mount เป็นโฟลเดอร์ `/etc/som`) จากนั้นพิสูจน์ว่า

1. เปลี่ยนป้ายร้านได้โดย **ไม่ build image ใหม่** (`som-shop-web:1.5` ตัวเดียวตลอด LAB) แต่ค่าจาก env ต้อง `rollout restart`
2. ประกาศหน้าร้านเปลี่ยนเองภายในราว 1 นาที **โดย Pod ไม่ restart**
3. ใช้ ConfigMap ชื่อใหม่แบบ `immutable` แล้วย้อนรุ่นด้วย `rollout undo` ได้
4. ออเดอร์ในฐานข้อมูล (StatefulSet + PVC จากบทที่ 9) ไม่หายตลอดทุกขั้น
5. และเห็นปัญหาที่ยังเหลือ: คนที่อ่าน Deployment ได้ยังเห็นรหัสผ่านฐานข้อมูล

**ไฟล์:** `som-shop-v6/` (ดู[โครงสร้างไฟล์ LAB](#โครงสร้างไฟล์-lab)) ต้องทำ LAB 0 แล้ว (มี `som-shop-web:1.5` และ `postgres:17.11-alpine` บนทุก Node) และไม่มี Service อื่นจอง NodePort 30080

### 10.1 ภาพรวมและไฟล์

| ส่วน | ชนิด | รายละเอียด |
|---|---|---|
| `som-shop` | Namespace | `pod-security.kubernetes.io/warn: restricted` (เหมือนบทที่ 4–9) |
| `som-db` + `som-db-0` | headless Service + StatefulSet | postgres 17.11 พร้อม PVC `data-som-db-0` (เหมือนบทที่ 9 ไม่เปลี่ยน) |
| `som-web` | Deployment 3 replicas + Service NodePort 30080 | `som-shop-web:1.5` + init container `wait-for-db`, `db-seed` |
| `som-web-config` | ConfigMap (ใหม่) | `SHOP_NAME`, `SHOP_EYEBROW`, `SHOP_FOOTER`, `APP_THEME`, `SHOP_PROMO` → `envFrom` |
| `som-announcement` | ConfigMap (ใหม่) | `announcement.txt` → volume ที่ `/etc/som` (ไม่ใช้ subPath) |

`k8s/15-config.yaml` (ตัดคอมเมนต์บางส่วน)

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: som-web-config
  namespace: som-shop
data:
  SHOP_NAME: "ร้านอาหารแมวน้องส้ม"
  SHOP_EYEBROW: "⚓ ท่าเรือ Kubernetes · ConfigMap"
  # ห้ามใส่ $(POD_NAMESPACE) ในค่าของ ConfigMap — envFrom ไม่แทนค่าให้ (ดูขั้น B เสริม)
  SHOP_FOOTER: "Next.js + PostgreSQL · Kubernetes LAB 010 · ConfigMap som-web-config"
  APP_THEME: "harbor"              # harbor (น้ำเงิน) หรือ sunset (ส้ม) — ทับค่าเริ่มใน image ได้
  SHOP_PROMO: ""                   # ว่าง = ไม่แสดงแถบโปรโมชัน
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: som-announcement
  namespace: som-shop
data:
  announcement.txt: |
    วันนี้ปลาทูสดมาก 🐟
```

ความต่างของ container `web` ระหว่าง `k8s-start/20-web.yaml` (ขั้น A) กับ `k8s/20-web.yaml` (ขั้น B เป็นต้นไป)

| | `k8s-start/20-web.yaml` | `k8s/20-web.yaml` |
|---|---|---|
| ชื่อร้าน / footer | `env: SHOP_NAME`, `SHOP_FOOTER` เขียนตรงในไฟล์ | `envFrom: configMapRef som-web-config` |
| ประกาศหน้าร้าน | ไม่มี | volume `som-announcement` mount ที่ `/etc/som` (`readOnly: true`) |
| env ที่เหลือ | `POD_NAMESPACE`, `DATABASE_URL`, `PORT`, `HOSTNAME` | เหมือนกัน (`DATABASE_URL` ยังมีรหัสผ่าน — จงใจ) |
| `kubernetes.io/change-cause` | `1.5 เริ่มบท 010 (ค่าร้านยังเขียนใน env)` | `1.5 ป้ายร้านจาก ConfigMap` |

ส่วนที่เพิ่มใน `k8s/20-web.yaml` (ตัดมาเฉพาะที่เกี่ยวข้อง)

```yaml
      volumes:
        # กระดานเล็กในบูธ: ทุก key ของ som-announcement = 1 ไฟล์ — kubelet อัปเดตให้เองราว 1 นาทีหลังแก้
        - name: announcement
          configMap:
            name: som-announcement
      containers:
        - name: web
          image: som-shop-web:1.5    # image เดิมทุกขั้น — เปลี่ยนป้ายร้านโดยไม่ build ใหม่
          envFrom:
            - configMapRef:
                name: som-web-config
          volumeMounts:
            - name: announcement
              mountPath: /etc/som        # ได้ไฟล์ /etc/som/announcement.txt (แอปอ่านใหม่ทุก request)
              readOnly: true
```

คำสั่งทั้งหมดของ LAB 10 รัน 🐧 ใน SSH session ของ k8s-lab ที่โฟลเดอร์ `som-shop-v6` (ใช้ `curl -s localhost:30080/...` ใน k8s-lab ได้เพราะ NodePort ของ kind ถูก map ไว้ที่ k8s-lab) และเปิดร้านใน 🌐 browser บนเครื่องนักศึกษาที่ **`http://localhost:30080`** ได้ทุกขั้น

### 10.2 ขั้น A: เริ่มจากร้านแบบบท 009

{{FIG:L12}}

```bash
cd /workspace/010_kubernetes_configmap/02_LAB/som-shop-v6
ls; kubectl apply -f k8s-start/
kubectl -n som-shop rollout status sts/som-db --timeout=180s && time kubectl -n som-shop rollout status deploy/som-web --timeout=240s
kubectl -n som-shop get pod,svc,pvc,cm
```

```text
app
extra
hit.sh
k8s
k8s-start
rbac
wait-announcement.sh
namespace/som-shop created
service/som-db created
statefulset.apps/som-db created
deployment.apps/som-web created
service/som-web created
Waiting for 1 pods to be ready...
partitioned roll out complete: 1 new pods have been updated...
Waiting for deployment "som-web" rollout to finish: 0 of 3 updated replicas are available...
...
deployment "som-web" successfully rolled out

real	0m5.436s
...
NAME                           READY   STATUS    RESTARTS   AGE
pod/som-db-0                   1/1     Running   0          14s
pod/som-web-7df8dc86bb-fj6st   1/1     Running   0          14s
pod/som-web-7df8dc86bb-h6crw   1/1     Running   0          14s
pod/som-web-7df8dc86bb-prwjh   1/1     Running   0          14s

NAME              TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)        AGE
service/som-db    ClusterIP   None            <none>        5432/TCP       14s
service/som-web   NodePort    10.96.135.175   <none>        80:30080/TCP   14s

NAME                                  STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
persistentvolumeclaim/data-som-db-0   Bound    pvc-8def5cb1-0e40-421b-880d-47f74296a138   1Gi        RWO            standard       <unset>                 14s

NAME                         DATA   AGE
configmap/kube-root-ca.crt   1      14s
```

ตอนนี้ namespace มีแค่ `kube-root-ca.crt` ยังไม่มี ConfigMap ของร้าน สั่งออเดอร์ 3 รายการแล้วดูค่าที่ร้านเห็น

```bash
curl -s localhost:30080/api/stats; echo
for i in 1 2 3; do curl -s -XPOST -H 'content-type: application/json' -d '{"product_id":1,"qty":1}' localhost:30080/api/orders; echo; done
curl -s localhost:30080/api/stats; echo; curl -s localhost:30080/api/shop; echo; curl -s localhost:30080/api/announcement
```

```text
som-web-7df8dc86bb-prwjh 1.5 orders=0 products=6

{"ok":true,"order_id":1,"product":{"id":1,"name_th":"อาหารเม็ดสูตรปลาทูน่า 1.5 กก.","stock":19}}
{"ok":true,"order_id":2,"product":{"id":1,"name_th":"อาหารเม็ดสูตรปลาทูน่า 1.5 กก.","stock":18}}
{"ok":true,"order_id":3,"product":{"id":1,"name_th":"อาหารเม็ดสูตรปลาทูน่า 1.5 กก.","stock":17}}
som-web-7df8dc86bb-h6crw 1.5 orders=3 products=6

{"pod":"som-web-7df8dc86bb-fj6st","version":"1.5","shopName":"ร้านอาหารแมวน้องส้ม","theme":"harbor","promo":"","eyebrow":null,"footer":"Next.js + PostgreSQL · Kubernetes LAB 010 · namespace som-shop"}
som-web-7df8dc86bb-prwjh 1.5 (ไม่มีประกาศ)
```

ดูหน้าเว็บจาก HTML (หรือเปิด 🌐 `http://localhost:30080`)

```bash
curl -s localhost:30080/ | grep -o '<title>[^<]*</title>'; curl -s localhost:30080/ | grep -o 'class="theme-[a-z]*"' | head -1; curl -s localhost:30080/ | grep -c 'class="promo"'; curl -s localhost:30080/ | grep -c 'class="announcement"'
curl -s localhost:30080/ | grep -o 'ท่าเรือ Kubernetes[^<]*' | head -1
./hit.sh http://localhost:30080/api/whoami 30
kubectl -n som-shop rollout history deploy/som-web
```

```text
<title>ร้านอาหารแมวน้องส้ม</title>
class="theme-harbor"
0
0
ท่าเรือ Kubernetes · ReplicaSet + Service
จำนวน  Pod  เวอร์ชัน
     13 som-web-7df8dc86bb-fj6st 1.5
     10 som-web-7df8dc86bb-h6crw 1.5
      7 som-web-7df8dc86bb-prwjh 1.5
ok=30 err=0 (ใช้เวลา 3.3 วินาที)
deployment.apps/som-web 
REVISION  CHANGE-CAUSE
1         1.5 เริ่มบท 010 (ค่าร้านยังเขียนใน env)
```

- แอป 1.5 ทำงานเหมือนบทที่ 9: ธีม harbor (ค่าเริ่มใน image) ไม่มีแถบโปรโมชัน (`SHOP_PROMO` ไม่ได้ตั้ง) ไม่มีแถบประกาศ (`/api/announcement` ตอบ `(ไม่มีประกาศ)` เพราะยังไม่มีไฟล์ `/etc/som/announcement.txt` แต่หน้าเว็บไม่พัง)
- `eyebrow` เป็น `null` หัวเว็บจึงใช้ข้อความตั้งต้นของแอป `⚓ ท่าเรือ Kubernetes · ReplicaSet + Service`
- footer มี `namespace som-shop` เพราะใน `k8s-start/20-web.yaml` ค่านี้อยู่ใน `env` ที่อ้าง `$(POD_NAMESPACE)` จึงถูกแทนค่า
- ออเดอร์ **3** รายการ (จำตัวเลขนี้ไว้ตรวจทุกขั้น)

### 10.3 ขั้น B: ย้ายป้ายร้านไปไว้ใน ConfigMap

{{FIG:L13}}

apply ConfigMap ทั้งสองแผ่นพร้อม Deployment รุ่นที่ใช้ `envFrom` + volume

```bash
kubectl apply -f k8s/15-config.yaml -f k8s/20-web.yaml && kubectl -n som-shop rollout status deploy/som-web --timeout=240s
kubectl -n som-shop get cm; curl -s localhost:30080/api/shop; echo; curl -s localhost:30080/api/announcement; curl -s localhost:30080/api/stats; echo
```

```text
configmap/som-web-config created
configmap/som-announcement created
deployment.apps/som-web configured
service/som-web unchanged
Waiting for deployment "som-web" rollout to finish: 1 out of 3 new replicas have been updated...
...
Waiting for deployment "som-web" rollout to finish: 1 old replicas are pending termination...
deployment "som-web" successfully rolled out
NAME               DATA   AGE
kube-root-ca.crt   1      60s
som-announcement   1      27s
som-web-config     5      27s
{"pod":"som-web-8655557674-tpgg6","version":"1.5","shopName":"ร้านอาหารแมวน้องส้ม","theme":"harbor","promo":"","eyebrow":"⚓ ท่าเรือ Kubernetes · ConfigMap","footer":"Next.js + PostgreSQL · Kubernetes LAB 010 · ConfigMap som-web-config"}
som-web-8655557674-jj7sr 1.5 วันนี้ปลาทูสดมาก 🐟
som-web-8655557674-tpgg6 1.5 orders=3 products=6
```

ดูหน้าเว็บ ไฟล์ใน Pod และ env

```bash
curl -s localhost:30080/ | grep -o '<title>[^<]*</title>'; curl -s localhost:30080/ | grep -o 'class="theme-[a-z]*"' | head -1; curl -s localhost:30080/ | grep -o 'class="announcement">[^<]*<!-- -->[^<]*' | head -1; curl -s localhost:30080/ | grep -c 'class="promo"'
kubectl -n som-shop exec deploy/som-web -c web -- ls -la /etc/som; kubectl -n som-shop exec deploy/som-web -c web -- printenv SHOP_NAME APP_THEME SHOP_FOOTER
kubectl -n som-shop rollout history deploy/som-web
```

```text
<title>ร้านอาหารแมวน้องส้ม</title>
class="theme-harbor"
class="announcement">📢 <!-- -->วันนี้ปลาทูสดมาก 🐟
0
total 12
drwxrwxrwx    3 root     root          4096 Oct  5 10:10 .
drwxr-xr-x    1 root     root          4096 Oct  5 10:10 ..
drwxr-xr-x    2 root     root          4096 Oct  5 10:10 ..2026_10_05_10_10_45.372685087
lrwxrwxrwx    1 root     root            31 Oct  5 10:10 ..data -> ..2026_10_05_10_10_45.372685087
lrwxrwxrwx    1 root     root            23 Oct  5 10:10 announcement.txt -> ..data/announcement.txt
ร้านอาหารแมวน้องส้ม
harbor
Next.js + PostgreSQL · Kubernetes LAB 010 · ConfigMap som-web-config
deployment.apps/som-web 
REVISION  CHANGE-CAUSE
1         1.5 เริ่มบท 010 (ค่าร้านยังเขียนใน env)
2         1.5 ป้ายร้านจาก ConfigMap
```

- `som-web-config` มี 5 key และ web ได้ทั้ง 5 เป็น env ผ่าน `envFrom` บรรทัดเดียว (`eyebrow` และ `footer` เป็นข้อความจาก ConfigMap แล้ว)
- `/etc/som/announcement.txt` เป็น symlink ผ่าน `..data` แบบ LAB 5 หน้าเว็บมีแถบ `📢 วันนี้ปลาทูสดมาก 🐟` (`<!-- -->` เป็นตัวคั่นที่ React แทรกใน HTML)
- ออเดอร์ยัง **3** — เปลี่ยน Deployment ไม่กระทบฐานข้อมูล

### 10.4 ขั้น B เสริม: $(POD_NAMESPACE) ในค่าของ ConfigMap

{{FIG:L16}}

ถ้าย้าย footer แบบเดิม (`... namespace $(POD_NAMESPACE)`) เข้าไปใน ConfigMap ตรง ๆ จะเกิดอะไร

```bash
kubectl -n som-shop patch cm som-web-config --type merge -p '{"data":{"SHOP_FOOTER":"LAB 010 · namespace $(POD_NAMESPACE)"}}' && kubectl -n som-shop rollout restart deploy/som-web && kubectl -n som-shop rollout status deploy/som-web --timeout=240s >/dev/null && sleep 8 && curl -s localhost:30080/api/shop; echo
```

```text
configmap/som-web-config patched
deployment.apps/som-web restarted
{"pod":"som-web-f686c9c85-4k8dt","version":"1.5","shopName":"ร้านอาหารแมวน้องส้ม","theme":"harbor","promo":"","eyebrow":"⚓ ท่าเรือ Kubernetes · ConfigMap","footer":"LAB 010 · namespace $(POD_NAMESPACE)"}
```

footer เป็นข้อความดิบ `$(POD_NAMESPACE)` (เหมือน LAB 3) ทางแก้คือตั้งค่านี้ใน `env` ของ Deployment ซึ่งแทนค่าได้และ **ชนะ envFrom**

```bash
kubectl -n som-shop set env deploy/som-web SHOP_FOOTER='LAB 010 · namespace $(POD_NAMESPACE)' && kubectl -n som-shop rollout status deploy/som-web --timeout=240s >/dev/null && sleep 8 && curl -s localhost:30080/api/shop; echo
kubectl -n som-shop get deploy som-web -o jsonpath='{.spec.template.spec.containers[0].env[*].name}'; echo
```

```text
deployment.apps/som-web env updated
{"pod":"som-web-78d9787b8c-bnvjm","version":"1.5","shopName":"ร้านอาหารแมวน้องส้ม","theme":"harbor","promo":"","eyebrow":"⚓ ท่าเรือ Kubernetes · ConfigMap","footer":"LAB 010 · namespace som-shop"}
POD_NAMESPACE DATABASE_URL PORT HOSTNAME SHOP_FOOTER
```

คืนค่าเดิม: apply ConfigMap จากไฟล์ และ **ลบ env `SHOP_FOOTER` ออกเอง** (`kubectl set env` ไม่ถูกบันทึกใน annotation last-applied การ `kubectl apply -f k8s/20-web.yaml` ภายหลังจึงไม่ลบ env ที่ set ไว้ ต้องใช้ `SHOP_FOOTER-`)

```bash
kubectl apply -f k8s/15-config.yaml && kubectl -n som-shop set env deploy/som-web SHOP_FOOTER- && kubectl -n som-shop rollout status deploy/som-web --timeout=240s >/dev/null && sleep 8 && curl -s localhost:30080/api/shop; echo
kubectl -n som-shop rollout history deploy/som-web; curl -s localhost:30080/api/stats; echo
```

```text
configmap/som-web-config configured
configmap/som-announcement unchanged
deployment.apps/som-web env updated
{"pod":"som-web-f686c9c85-55c2q","version":"1.5","shopName":"ร้านอาหารแมวน้องส้ม","theme":"harbor","promo":"","eyebrow":"⚓ ท่าเรือ Kubernetes · ConfigMap","footer":"Next.js + PostgreSQL · Kubernetes LAB 010 · ConfigMap som-web-config"}
deployment.apps/som-web 
REVISION  CHANGE-CAUSE
1         1.5 เริ่มบท 010 (ค่าร้านยังเขียนใน env)
2         1.5 ป้ายร้านจาก ConfigMap
4         1.5 ป้ายร้านจาก ConfigMap
5         1.5 ป้ายร้านจาก ConfigMap

som-web-f686c9c85-pd4nz 1.5 orders=3 products=6
```

สังเกต history: `rollout restart` และ `set env` **ไม่เปลี่ยน CHANGE-CAUSE** ทุก revision จึงซ้ำข้อความ `1.5 ป้ายร้านจาก ConfigMap` และ REVISION 3 หายไปเพราะ template หลังเอา `SHOP_FOOTER` ออกเหมือนกับ revision 3 (restartedAt เดิม) Deployment จึงนำ ReplicaSet เดิมกลับมาใช้เป็น revision 5 (ชื่อ Pod `som-web-f686c9c85-...` ชุดเดียวกับหลัง restart) ออเดอร์ยัง **3**

### 10.5 ขั้น C1: แก้ ConfigMap แล้ว Pod เดิมยังไม่เปลี่ยน

{{FIG:L14}}

`extra/15-config-promo.yaml` ใช้ชื่อ `som-web-config` เดิม แต่เปลี่ยนเป็นชื่อสาขา ธีม sunset และเพิ่มโปรโมชัน

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: som-web-config
  namespace: som-shop
data:
  SHOP_NAME: "ร้านน้องส้ม สาขาท่าเรือ"
  SHOP_EYEBROW: "⚓ ท่าเรือ Kubernetes · ConfigMap"
  SHOP_FOOTER: "Next.js + PostgreSQL · Kubernetes LAB 010 · ConfigMap som-web-config"
  APP_THEME: "sunset"
  SHOP_PROMO: "🎉 โปรวันนี้: ขนมปลาทูน่าลด 20%"
```

```bash
kubectl apply -f extra/15-config-promo.yaml; date +%T; kubectl -n som-shop get cm som-web-config -o jsonpath="{.data.SHOP_NAME} / {.data.APP_THEME} / {.data.SHOP_PROMO}"; echo
```

```text
configmap/som-web-config configured
17:12:45
ร้านน้องส้ม สาขาท่าเรือ / sunset / 🎉 โปรวันนี้: ขนมปลาทูน่าลด 20%
```

ConfigMap เปลี่ยนแล้ว **รอ 90 วินาที** แล้วถามทั้ง 3 Pod

```bash
date +%T; for i in 1 2 3; do curl -s localhost:30080/api/shop; echo; done; kubectl -n som-shop get pod -l app=som-web
```

```text
17:14:16
{"pod":"som-web-f686c9c85-pd4nz","version":"1.5","shopName":"ร้านอาหารแมวน้องส้ม","theme":"harbor","promo":"","eyebrow":"⚓ ท่าเรือ Kubernetes · ConfigMap","footer":"Next.js + PostgreSQL · Kubernetes LAB 010 · ConfigMap som-web-config"}
{"pod":"som-web-f686c9c85-55c2q","version":"1.5","shopName":"ร้านอาหารแมวน้องส้ม","theme":"harbor","promo":"","eyebrow":"⚓ ท่าเรือ Kubernetes · ConfigMap","footer":"Next.js + PostgreSQL · Kubernetes LAB 010 · ConfigMap som-web-config"}
{"pod":"som-web-f686c9c85-nzqxd","version":"1.5","shopName":"ร้านอาหารแมวน้องส้ม","theme":"harbor","promo":"","eyebrow":"⚓ ท่าเรือ Kubernetes · ConfigMap","footer":"Next.js + PostgreSQL · Kubernetes LAB 010 · ConfigMap som-web-config"}
NAME                      READY   STATUS    RESTARTS   AGE
som-web-f686c9c85-55c2q   1/1     Running   0          112s
som-web-f686c9c85-nzqxd   1/1     Running   0          2m4s
som-web-f686c9c85-pd4nz   1/1     Running   0          118s
```

ทั้ง 3 Pod ยังเป็น `ร้านอาหารแมวน้องส้ม` / `harbor` / promo ว่าง และ `RESTARTS 0` เพราะค่าเหล่านี้มาจาก **env ที่อ่านครั้งเดียวตอน container เริ่ม** (ป้ายติดอก) ไม่ว่าจะรอนานเท่าไรก็ไม่เปลี่ยน

### 10.6 ขั้น C2: rollout restart แล้วป้ายเปลี่ยน

{{FIG:L15}}

```bash
kubectl -n som-shop rollout restart deploy/som-web && kubectl -n som-shop rollout status deploy/som-web --timeout=240s
```

```text
deployment.apps/som-web restarted
Waiting for deployment "som-web" rollout to finish: 1 out of 3 new replicas have been updated...
...
Waiting for deployment "som-web" rollout to finish: 1 old replicas are pending termination...
deployment "som-web" successfully rolled out
```

rollout ใช้ราว 25–35 วินาที (3 Pod, `maxSurge: 1`, `minReadySeconds: 3`) หลัง `successfully rolled out` รอราว 8 วินาทีก่อน curl เพราะ Pod เก่ายังตอบอยู่ในช่วง preStop 5 วินาที

```bash
curl -s localhost:30080/api/shop; echo
curl -s localhost:30080/ | grep -o '<title>[^<]*</title>'; curl -s localhost:30080/ | grep -o 'class="theme-[a-z]*"' | head -1; curl -s localhost:30080/ | grep -o 'class="promo">[^<]*'; curl -s localhost:30080/api/stats; echo
./hit.sh http://localhost:30080/api/shop 12 | head -6
```

```text
{"pod":"som-web-b97c66d9c-tb2f7","version":"1.5","shopName":"ร้านน้องส้ม สาขาท่าเรือ","theme":"sunset","promo":"🎉 โปรวันนี้: ขนมปลาทูน่าลด 20%","eyebrow":"⚓ ท่าเรือ Kubernetes · ConfigMap","footer":"Next.js + PostgreSQL · Kubernetes LAB 010 · ConfigMap som-web-config"}
<title>ร้านน้องส้ม สาขาท่าเรือ</title>
class="theme-sunset"
class="promo">🎉 โปรวันนี้: ขนมปลาทูน่าลด 20%
som-web-b97c66d9c-tb2f7 1.5 orders=3 products=6
จำนวน  Pod  เวอร์ชัน
      5 {"pod":"som-web-b97c66d9c-86592","version":"1.5","shopName":"ร้านน้องส้ม สาขาท่าเรือ","theme":"sunset","promo":"🎉 โปรวันนี้: ขนมปลาทูน่าลด 20%","eyebrow":"⚓ ท่าเรือ Kubernetes · ConfigMap","footer":"Next.js + PostgreSQL · Kubernetes LAB 010 · ConfigMap som-web-config"}
      4 {"pod":"som-web-b97c66d9c-tb2f7","version":"1.5","shopName":"ร้านน้องส้ม สาขาท่าเรือ","theme":"sunset","promo":"🎉 โปรวันนี้: ขนมปลาทูน่าลด 20%","eyebrow":"⚓ ท่าเรือ Kubernetes · ConfigMap","footer":"Next.js + PostgreSQL · Kubernetes LAB 010 · ConfigMap som-web-config"}
      3 {"pod":"som-web-b97c66d9c-xx945","version":"1.5","shopName":"ร้านน้องส้ม สาขาท่าเรือ","theme":"sunset","promo":"🎉 โปรวันนี้: ขนมปลาทูน่าลด 20%","eyebrow":"⚓ ท่าเรือ Kubernetes · ConfigMap","footer":"Next.js + PostgreSQL · Kubernetes LAB 010 · ConfigMap som-web-config"}
ok=12 err=0 (ใช้เวลา 1.3 วินาที)
```

- ทั้ง 3 Pod ใหม่ได้ชื่อร้าน `ร้านน้องส้ม สาขาท่าเรือ` ธีม sunset และแถบโปรโมชัน ทั้งชื่อในแท็บ browser (`<title>`) ก็เปลี่ยนตาม
- image ยังเป็น `som-shop-web:1.5` ตัวเดิม **ไม่ได้ build ใหม่เลย** และออเดอร์ยัง **3**

### 10.7 ขั้น D: ประกาศหน้าร้านเปลี่ยนเองโดยไม่ restart

{{FIG:L17}}

ประกาศมาจากไฟล์ใน volume และแอป 1.5 อ่านไฟล์ใหม่ **ทุก request** จึงไม่ต้อง restart จดชื่อ Pod และ AGE ไว้ก่อน

```bash
kubectl -n som-shop get pod -l app=som-web; curl -s localhost:30080/api/announcement
```

```text
NAME                      READY   STATUS    RESTARTS   AGE
som-web-b97c66d9c-86592   1/1     Running   0          27s
som-web-b97c66d9c-tb2f7   1/1     Running   0          34s
som-web-b97c66d9c-xx945   1/1     Running   0          21s
som-web-b97c66d9c-86592 1.5 วันนี้ปลาทูสดมาก 🐟
```

{{FIG:L18}}

apply ประกาศใหม่ (`extra/16-announcement-1800.yaml` = `ปิดร้านเร็ว 18:00 น. ⛵`) แล้วให้ `wait-announcement.sh` จับเวลา สคริปต์เรียก `/api/announcement` ชุดละ 12 ครั้งทุก 2 วินาที บอกเวลาที่ Pod แรกเห็นคำว่า `18:00` และเวลาที่ครบ 12/12 (ทุก Pod)

```bash
kubectl apply -f extra/16-announcement-1800.yaml && ./wait-announcement.sh 18:00
kubectl -n som-shop get pod -l app=som-web; curl -s localhost:30080/ | grep -o 'class="announcement">[^<]*<!-- -->[^<]*'
```

```text
configmap/som-announcement configured
เริ่ม 17:14:51 รอคำว่า "18:00" จาก http://localhost:30080/api/announcement
  Pod แรกเห็นประกาศใหม่หลัง 37 วินาที: som-web-b97c66d9c-tb2f7 1.5 ปิดร้านเร็ว 18:00 น. ⛵
  ทุก Pod เห็นประกาศใหม่ (12/12) หลัง 48 วินาที
NAME                      READY   STATUS    RESTARTS   AGE
som-web-b97c66d9c-86592   1/1     Running   0          76s
som-web-b97c66d9c-tb2f7   1/1     Running   0          83s
som-web-b97c66d9c-xx945   1/1     Running   0          70s
class="announcement">📢 <!-- -->ปิดร้านเร็ว 18:00 น. ⛵
```

ชื่อ Pod เดิมทั้ง 3 ตัว `RESTARTS 0` และ AGE นับต่อเนื่อง (27s → 76s) แต่หน้าเว็บเปลี่ยนประกาศแล้ว

ลองอีกรอบด้วยการอัปเดตจากคำสั่ง (`create ... --dry-run=client -o yaml | kubectl apply -f -` แบบ LAB 1) แล้วกลับเป็นประกาศ 18:00

```bash
kubectl -n som-shop create configmap som-announcement --from-literal=announcement.txt='พรุ่งนี้เปิด 09:00 น. 🐟' --dry-run=client -o yaml | kubectl apply -f - && ./wait-announcement.sh 09:00
kubectl apply -f extra/16-announcement-1800.yaml && ./wait-announcement.sh 18:00; kubectl -n som-shop get pod -l app=som-web
```

```text
configmap/som-announcement configured
เริ่ม 17:15:46 รอคำว่า "09:00" จาก http://localhost:30080/api/announcement
  Pod แรกเห็นประกาศใหม่หลัง 63 วินาที: som-web-b97c66d9c-tb2f7 1.5 พรุ่งนี้เปิด 09:00 น. 🐟
  ทุก Pod เห็นประกาศใหม่ (12/12) หลัง 82 วินาที
configmap/som-announcement configured
เริ่ม 17:17:08 รอคำว่า "18:00" จาก http://localhost:30080/api/announcement
  Pod แรกเห็นประกาศใหม่หลัง 59 วินาที: som-web-b97c66d9c-tb2f7 1.5 ปิดร้านเร็ว 18:00 น. ⛵
  ทุก Pod เห็นประกาศใหม่ (12/12) หลัง 88 วินาที
NAME                      READY   STATUS    RESTARTS   AGE
som-web-b97c66d9c-86592   1/1     Running   0          4m13s
som-web-b97c66d9c-tb2f7   1/1     Running   0          4m20s
som-web-b97c66d9c-xx945   1/1     Running   0          4m7s
```

| รอบ | Pod แรกเห็น | ครบทุก Pod |
|---|---|---|
| 1 (`18:00`) | 37 วินาที | 48 วินาที |
| 2 (`09:00`) | 63 วินาที | 82 วินาที |
| 3 (`18:00`) | 59 วินาที | 88 วินาที |

ระหว่างช่วงนั้นการ refresh browser แต่ละครั้งอาจได้ Pod ที่ยังเป็นข้อความเก่า (Pod อยู่คนละ Node แต่ละ kubelet อัปเดตไม่พร้อมกัน) เผื่อเวลา **ราว 1–1.5 นาที** หลังแก้ประกาศ

### 10.8 ขั้น E: ConfigMap ชื่อใหม่แบบ immutable และ rollout undo

{{FIG:L19}}

`extra/17-config-v2.yaml` สร้าง `som-web-config-v2` แบบ `immutable: true` (ชื่อร้าน `ร้านน้องส้ม (v2)`) แล้วเปลี่ยนชื่อที่ `envFrom` อ้างด้วย JSON patch (ตำแหน่ง `/spec/template/spec/containers/0/envFrom/0/configMapRef/name`)

```bash
kubectl apply -f extra/17-config-v2.yaml; kubectl -n som-shop get cm
kubectl -n som-shop patch deploy som-web --type json -p '[{"op":"replace","path":"/spec/template/spec/containers/0/envFrom/0/configMapRef/name","value":"som-web-config-v2"}]' && kubectl -n som-shop rollout status deploy/som-web --timeout=240s >/dev/null
curl -s localhost:30080/api/shop; echo
```

```text
configmap/som-web-config-v2 created
NAME                DATA   AGE
kube-root-ca.crt    1      8m33s
som-announcement    1      8m
som-web-config      5      8m
som-web-config-v2   5      0s
deployment.apps/som-web patched
{"pod":"som-web-5dd747bf86-fzdzt","version":"1.5","shopName":"ร้านน้องส้ม (v2)","theme":"harbor","promo":"","eyebrow":"⚓ ท่าเรือ Kubernetes · ConfigMap v2 (immutable)","footer":"Next.js + PostgreSQL · Kubernetes LAB 010 · ConfigMap som-web-config-v2"}
```

ชื่อที่อ้างอยู่ใน Pod template เปลี่ยน → **rollout เอง** ไม่ต้องสั่ง restart ลองแก้ v2 และย้อนรุ่น

```bash
kubectl -n som-shop patch cm som-web-config-v2 --type merge -p '{"data":{"SHOP_NAME":"ร้านน้องส้ม (v2 แก้)"}}'
kubectl -n som-shop rollout undo deploy/som-web && kubectl -n som-shop rollout status deploy/som-web --timeout=240s >/dev/null
curl -s localhost:30080/api/shop; echo; curl -s localhost:30080/api/stats; echo; kubectl -n som-shop rollout history deploy/som-web
```

```text
The ConfigMap "som-web-config-v2" is invalid: data: Forbidden: field is immutable when `immutable` is set
Warning: resource deployments/som-web was previously managed with 'kubectl apply'. Rolling back will not update the kubectl.kubernetes.io/last-applied-configuration annotation, which may cause unexpected behavior on future 'kubectl apply' operations. Consider using 'kubectl apply' with your previous configuration file instead.
deployment.apps/som-web rolled back
{"pod":"som-web-b97c66d9c-s725k","version":"1.5","shopName":"ร้านน้องส้ม สาขาท่าเรือ","theme":"sunset","promo":"🎉 โปรวันนี้: ขนมปลาทูน่าลด 20%","eyebrow":"⚓ ท่าเรือ Kubernetes · ConfigMap","footer":"Next.js + PostgreSQL · Kubernetes LAB 010 · ConfigMap som-web-config"}
som-web-b97c66d9c-s725k 1.5 orders=3 products=6

deployment.apps/som-web 
REVISION  CHANGE-CAUSE
1         1.5 เริ่มบท 010 (ค่าร้านยังเขียนใน env)
2         1.5 ป้ายร้านจาก ConfigMap
4         1.5 ป้ายร้านจาก ConfigMap
5         1.5 ป้ายร้านจาก ConfigMap
7         1.5 ป้ายร้านจาก ConfigMap
8         1.5 ป้ายร้านจาก ConfigMap
```

- แก้ `som-web-config-v2` ไม่ได้ (`immutable`) ต้องสร้าง `-v3` แทน
- `rollout undo` กลับไป template ที่อ้าง `som-web-config` (ชื่อสาขาท่าเรือ/sunset) ทันที เพราะ ConfigMap เดิมยังอยู่ (ชื่อ Pod `som-web-b97c66d9c-...` = ReplicaSet เดิมของขั้น C2) Warning เรื่อง last-applied เป็นเรื่องปกติของ `undo` (บทที่ 7)
- ออเดอร์ยัง **3**

### 10.9 ขั้น F: ปัญหาที่เหลือ — รหัสผ่านยังเห็นได้

{{FIG:L20}}

`rbac/intern.yaml` สร้าง ServiceAccount `intern` ที่ได้สิทธิ์ `get, list, watch` เฉพาะ Pod, ConfigMap, Deployment และ StatefulSet ใน `som-shop` (แบบบทที่ 4)

```bash
kubectl apply -f rbac/intern.yaml
kubectl -n som-shop auth can-i get configmaps --as=system:serviceaccount:som-shop:intern; kubectl -n som-shop auth can-i get deployments --as=system:serviceaccount:som-shop:intern; kubectl -n som-shop auth can-i get secrets --as=system:serviceaccount:som-shop:intern; kubectl -n som-shop auth can-i patch configmaps --as=system:serviceaccount:som-shop:intern
kubectl -n som-shop get cm --as=system:serviceaccount:som-shop:intern
```

```text
serviceaccount/intern created
role.rbac.authorization.k8s.io/intern-read created
rolebinding.rbac.authorization.k8s.io/intern-read created
yes
yes
no
no
NAME                DATA   AGE
kube-root-ca.crt    1      9m34s
som-announcement    1      9m1s
som-web-config      5      9m1s
som-web-config-v2   5      61s
```

intern อ่าน ConfigMap และ Deployment ได้ แต่แก้ ConfigMap ไม่ได้ (และไม่มีสิทธิ์อ่านความลับแบบอื่นด้วย) ลองให้ intern ดู YAML ของ Deployment และ StatefulSet

```bash
kubectl -n som-shop get deploy som-web -o yaml --as=system:serviceaccount:som-shop:intern | grep -o 'som:[a-z0-9]*@' | sort | uniq -c
kubectl -n som-shop get deploy som-web -o yaml --as=system:serviceaccount:som-shop:intern | grep -n 'som:[a-z0-9]*@' | cut -c1-90
kubectl -n som-shop get sts som-db -o yaml --as=system:serviceaccount:som-shop:intern | grep -A1 -- '- name: POSTGRES_PASSWORD'
kubectl -n som-shop get pod som-db-0 -o yaml --as=system:serviceaccount:som-shop:intern | grep -A1 -- '- name: POSTGRES_PASSWORD'
kubectl -n som-shop patch cm som-web-config --as=system:serviceaccount:som-shop:intern --type merge -p '{"data":{"SHOP_NAME":"x"}}'
```

```text
      4 som:meow1234@
7:      {"apiVersion":"apps/v1","kind":"Deployment","metadata":{"annotations":{"kubernetes
45:          value: postgres://som:meow1234@som-db-0.som-db:5432/catshop
134:          value: postgres://som:meow1234@som-db-0.som-db:5432/catshop
        - name: POSTGRES_PASSWORD
          value: meow1234
    - name: POSTGRES_PASSWORD
      value: meow1234
Error from server (Forbidden): configmaps "som-web-config" is forbidden: User "system:serviceaccount:som-shop:intern" cannot patch resource "configmaps" in API group "" in the namespace "som-shop"
```

- intern เห็น `som:meow1234@` **4 ครั้ง** ใน Deployment: บรรทัด 45 และ 134 คือ `DATABASE_URL` ของ init container `db-seed` และ container `web` อีก 2 ครั้งอยู่ในบรรทัดเดียว (บรรทัด 7) ของ annotation `last-applied-configuration`
- เห็น `POSTGRES_PASSWORD: meow1234` ทั้งใน StatefulSet และ Pod `som-db-0`
- ถ้าย้ายรหัสไปไว้ใน ConfigMap ก็ไม่ช่วย เพราะ intern อ่าน ConfigMap ได้และ ConfigMap เป็นข้อความธรรมดา → **โจทย์ของบทที่ 11 Secret**

> รหัส `meow1234` เป็นค่าตัวอย่างของ LAB เท่านั้น ถ้าจะแปะภาพหน้าจอขั้นนี้ลงรายงาน ให้บังรหัสเป็น `som:●●●●@` เพื่อฝึกนิสัยที่ดี

### 10.10 คืนสภาพร้านและสั่งออเดอร์ที่ 4

ลบ ConfigMap v2 แล้ว apply โฟลเดอร์ `k8s/` ทั้งหมดเพื่อให้ ConfigMap และ Deployment กลับตรงกับไฟล์ (ชื่อร้านเดิม ธีม harbor ประกาศเดิม)

```bash
kubectl -n som-shop delete cm som-web-config-v2; kubectl apply -f k8s/ && kubectl -n som-shop rollout restart deploy/som-web && kubectl -n som-shop rollout status deploy/som-web --timeout=240s >/dev/null; echo rolled
curl -s -XPOST -H 'content-type: application/json' -d '{"product_id":2,"qty":1}' localhost:30080/api/orders; echo; curl -s localhost:30080/api/stats; echo; curl -s localhost:30080/api/shop; echo
```

```text
configmap "som-web-config-v2" deleted from som-shop namespace
namespace/som-shop unchanged
service/som-db unchanged
statefulset.apps/som-db configured
configmap/som-web-config configured
configmap/som-announcement configured
deployment.apps/som-web unchanged
service/som-web unchanged
deployment.apps/som-web restarted
rolled
{"ok":true,"order_id":4,"product":{"id":2,"name_th":"อาหารเม็ดลูกแมว สูตรนมแพะ 1 กก.","stock":14}}
som-web-77467d5bc4-w9zpt 1.5 orders=4 products=6

{"pod":"som-web-77467d5bc4-nvkw8","version":"1.5","shopName":"ร้านอาหารแมวน้องส้ม","theme":"harbor","promo":"","eyebrow":"⚓ ท่าเรือ Kubernetes · ConfigMap","footer":"Next.js + PostgreSQL · Kubernetes LAB 010 · ConfigMap som-web-config"}
```

- `deployment.apps/som-web unchanged` เพราะไฟล์เหมือนกับ template ปัจจุบัน แต่ ConfigMap `som-web-config` ถูกคืนเป็นค่าในไฟล์ (env ต้อง Pod ใหม่) จึงสั่ง `rollout restart` ต่อ
- `statefulset.apps/som-db configured` ขึ้นได้แม้ไฟล์ไม่เปลี่ยน (kubectl เติมค่าตั้งต้นบางช่อง) ไม่สร้าง revision ใหม่และ `som-db-0` ไม่ restart — ปกติ
- ออเดอร์ที่ 4 สั่งสำเร็จ (`orders=4`) ข้อมูลจากขั้น A ยังอยู่ครบ

### 10.11 เปิดร้านใน browser: เปลี่ยนป้ายอีกรอบ (ภาพหน้าจอจริง)

ทำขั้น C1, C2 และ D ซ้ำอีกรอบโดยดูผลใน 🌐 browser บนเครื่องนักศึกษาที่ **`http://localhost:30080`** ภาพหน้าจอ 4 ภาพในหัวข้อนี้เป็น **ภาพหน้าจอจริงจากการทดลอง** (browser เปิด NodePort 30080 โดยตรง) ถ่ายต่อจากขั้น 10.10 ออเดอร์จึงเป็น 4

**ฉาก 1 — ร้านที่ป้ายมาจาก ConfigMap** เปิด `http://localhost:30080` จะเห็นชื่อร้านอาหารแมวน้องส้ม ธีม harbor (น้ำเงิน) และแถบประกาศสีเหลือง

{{SHOT:1}}

**ฉาก 2 — แก้ ConfigMap แล้วหน้าเว็บยังเหมือนเดิม** 🐧 apply ป้ายชุดสาขาท่าเรือ รอ 90 วินาทีแล้ว refresh browser

```bash
kubectl apply -f extra/15-config-promo.yaml
curl -s localhost:30080/api/shop; echo
kubectl -n som-shop get pod -l app=som-web
```

```text
configmap/som-web-config configured
{"pod":"som-web-77467d5bc4-xbwpb","version":"1.5","shopName":"ร้านอาหารแมวน้องส้ม","theme":"harbor","promo":"","eyebrow":"⚓ ท่าเรือ Kubernetes · ConfigMap","footer":"Next.js + PostgreSQL · Kubernetes LAB 010 · ConfigMap som-web-config"}
NAME                       READY   STATUS    RESTARTS   AGE
som-web-77467d5bc4-nvkw8   1/1     Running   0          6m18s
som-web-77467d5bc4-w9zpt   1/1     Running   0          6m24s
som-web-77467d5bc4-xbwpb   1/1     Running   0          6m12s
```

{{SHOT:2}}

**ฉาก 3 — rollout restart แล้ว refresh** (รอราว 8 วินาทีหลัง `successfully rolled out`)

```bash
kubectl -n som-shop rollout restart deploy/som-web
kubectl -n som-shop rollout status deploy/som-web
curl -s localhost:30080/api/shop; echo; curl -s localhost:30080/api/stats; echo
kubectl -n som-shop get pod -l app=som-web
```

```text
deployment.apps/som-web restarted
Waiting for deployment "som-web" rollout to finish: 0 out of 3 new replicas have been updated...
...
deployment "som-web" successfully rolled out
{"pod":"som-web-5f4db546b6-766ft","version":"1.5","shopName":"ร้านน้องส้ม สาขาท่าเรือ","theme":"sunset","promo":"🎉 โปรวันนี้: ขนมปลาทูน่าลด 20%","eyebrow":"⚓ ท่าเรือ Kubernetes · ConfigMap","footer":"Next.js + PostgreSQL · Kubernetes LAB 010 · ConfigMap som-web-config"}
som-web-5f4db546b6-522dj 1.5 orders=4 products=6

NAME                       READY   STATUS    RESTARTS   AGE
som-web-5f4db546b6-522dj   1/1     Running   0          29s
som-web-5f4db546b6-766ft   1/1     Running   0          23s
som-web-5f4db546b6-c76dx   1/1     Running   0          35s
```

{{SHOT:3}}

**ฉาก 4 — แก้ประกาศ แล้ว refresh โดยไม่ restart**

```bash
kubectl apply -f extra/16-announcement-1800.yaml && ./wait-announcement.sh 18:00
kubectl -n som-shop get pod -l app=som-web
```

```text
configmap/som-announcement configured
เริ่ม 17:27:13 รอคำว่า "18:00" จาก http://localhost:30080/api/announcement
  Pod แรกเห็นประกาศใหม่หลัง 36 วินาที: som-web-5f4db546b6-c76dx 1.5 ปิดร้านเร็ว 18:00 น. ⛵
  ทุก Pod เห็นประกาศใหม่ (12/12) หลัง 65 วินาที
NAME                       READY   STATUS    RESTARTS   AGE
som-web-5f4db546b6-522dj   1/1     Running   0          94s
som-web-5f4db546b6-766ft   1/1     Running   0          88s
som-web-5f4db546b6-c76dx   1/1     Running   0          100s
```

{{SHOT:4}}

ชื่อ Pod ชุดเดิมจากฉาก 3 `RESTARTS 0` และ AGE ต่อเนื่อง (29s → 94s) แต่แถบประกาศเปลี่ยนเป็น `ปิดร้านเร็ว 18:00 น. ⛵` แล้ว

### 10.12 สรุป LAB 10

{{FIG:L21}}

| อยากเปลี่ยน | อยู่ที่ | ทำอย่างไร | ผลจริง |
|---|---|---|---|
| ชื่อร้าน, ธีม, โปรโมชัน | ConfigMap `som-web-config` → `envFrom` | แก้ ConfigMap + `rollout restart` (หรือชื่อใหม่ + แก้ Deployment) | รอ 90 วินาทีไม่เปลี่ยน → หลัง restart เปลี่ยนทุก Pod |
| ประกาศหน้าร้าน | ConfigMap `som-announcement` → volume `/etc/som` | แก้ ConfigMap อย่างเดียว | Pod แรก 36–63 วินาที ทุก Pod 48–88 วินาที `RESTARTS 0` |
| ค่าที่ต้องอ้าง `$(VAR)` | `env` ของ Deployment | `env` ชนะ `envFrom` | `namespace som-shop` |
| ป้ายชุดที่ห้ามแก้กลางทาง | `som-web-config-v2` (`immutable`) | ชื่อใหม่ + เปลี่ยนชื่อใน `envFrom` / `rollout undo` | rollout เอง, แก้ได้ `Forbidden` |
| image | `som-shop-web:1.5` | ไม่ต้องทำอะไร | ไม่ build ใหม่เลยทั้ง LAB |
| ออเดอร์ | PVC `data-som-db-0` | — | 3 → 3 ทุกขั้น → 4 |
| รหัสผ่านฐานข้อมูล | ยังเขียนใน YAML | — | intern เห็น `som:meow1234@` → บทที่ 11 |

**คำถามท้าย LAB 10**

1. ทำไมขั้น C1 รอ 90 วินาทีแล้วหน้าเว็บยังไม่เปลี่ยน แต่ขั้น D ประกาศเปลี่ยนเองภายในราว 1 นาที ทั้งที่แก้ ConfigMap เหมือนกัน
2. ถ้าแอปอ่าน `/etc/som/announcement.txt` แค่ครั้งเดียวตอนเริ่ม (แบบ nginx ใน LAB 7) ขั้น D จะเห็นผลแบบไหน และต้องแก้อย่างไร
3. ทำไม `k8s/20-web.yaml` mount `som-announcement` ทั้งโฟลเดอร์ `/etc/som` แทนการใช้ `subPath` ไปที่ `/etc/som/announcement.txt`
4. เปรียบเทียบการเปลี่ยนป้ายด้วย "แก้ `som-web-config` + `rollout restart`" (ขั้น C) กับ "สร้าง `som-web-config-v2` + เปลี่ยนชื่อใน Deployment" (ขั้น E) ในแง่ประวัติ (`rollout history`) และการย้อนรุ่น
5. ถ้าย้าย `DATABASE_URL` ไปไว้ใน ConfigMap `som-web-config` แล้วให้ intern ทำขั้น F ใหม่ ผลจะต่างไปไหม เพราะอะไร

### 10.13 เก็บกวาด LAB 10

ร้าน `som-shop` ตอนนี้ใช้ป้ายชุดสาขาท่าเรือและประกาศ 18:00 (สภาพหลังฉาก 4) ถ้าจะเรียนบทที่ 11 ต่อทันทีเก็บไว้ได้ ถ้าต้องการคืนทรัพยากร หรือก่อนทำ LAB นี้ซ้ำ ให้ลบทั้ง namespace (ลบ Deployment, StatefulSet, ConfigMap, ServiceAccount `intern` และ PVC `data-som-db-0` พร้อมออเดอร์ทั้งหมด และคืน NodePort 30080)

```bash
kubectl delete ns som-shop
```

ใช้เวลาราว 30 วินาที (Pod web มี preStop 5 วินาทีและ grace period) ถ้าแค่อยากคืนป้ายร้านเป็นค่าในไฟล์โดยไม่ลบออเดอร์ ให้ใช้คำสั่งของขั้น 10.10 (`kubectl apply -f k8s/` + `rollout restart`)

---

## Troubleshooting

| อาการ | สาเหตุ | วิธีแก้ |
|---|---|---|
| `ls` ใน k8s-lab ไม่เจอ `labs/` หรือ `som-shop-v6/`, kubectl แจ้ง `the path "..." does not exist` | ยังไม่ได้ `docker cp` หรืออยู่ผิดโฟลเดอร์ | 🖥️ `docker cp 010_kubernetes_configmap k8s-lab:/workspace/` แล้ว 🐧 `cd` ไปโฟลเดอร์ของ LAB นั้น ตรวจด้วย `pwd` |
| `./watch.sh: Permission denied` หรือ `./wait-announcement.sh: Permission denied` | สิทธิ์ execute หายระหว่างคัดลอก | `bash watch.sh` / `bash wait-announcement.sh 18:00` หรือ `chmod +x *.sh` |
| `kubectl get nodes` ต่อคลัสเตอร์ไม่ได้ | ยังไม่มีคลัสเตอร์ หรือ `k8s-lab` เพิ่ง restart | 🐧 `k8s-up` แล้วทำ LAB 0 ขั้นที่ 5 (โหลด postgres และ build/load `som-shop-web:1.5`) |
| `error: failed to create configmap: configmaps "demo" already exists` | `kubectl create` ใช้สร้างใหม่เท่านั้น | ลบก่อน หรือใช้ `kubectl create configmap ... --dry-run=client -o yaml \| kubectl apply -f -` |
| `Too long: may not be more than 1048576 bytes` | ConfigMap รวมทุก key เกิน 1 MiB | เก็บไฟล์ใหญ่ใน image หรือ volume อื่น |
| `envpod` เป็น `CreateContainerConfigError` ชั่วครู่หลัง `kubectl apply -f .` ใน LAB 2 | สร้าง Pod ก่อน ConfigMap (เรียงตามชื่อไฟล์) | รอไม่กี่วินาทีจะหายเอง หรือสั่ง `kubectl apply -f shop-config.yaml -f envpod.yaml` |
| Pod ค้าง `CreateContainerConfigError` + `configmap "..." not found` | ยังไม่มี ConfigMap ชื่อนั้นใน namespace ของ Pod (สะกดผิด, ลืม apply, อยู่คนละ namespace) | `kubectl get cm -n <ns>` สร้าง/แก้ชื่อให้ตรง Pod จะเริ่มเองภายในราว 15 วินาที |
| `couldn't find key NOPE in ConfigMap default/shop-config` และไม่หายเองหลังสร้าง ConfigMap อื่น | key ที่อ้างไม่มีใน ConfigMap (LAB 4 `nokey` ตั้งใจ) | เพิ่ม key ใน ConfigMap หรือแก้ YAML แล้วสร้าง Pod ใหม่ หรือใส่ `optional: true` ถ้าไม่จำเป็นจริง |
| Pod ค้าง `ContainerCreating` + `FailedMount ... configmap "..." not found` | volume อ้าง ConfigMap ที่ไม่มี | สร้าง ConfigMap แล้วรอ หรือใส่ `optional: true` |
| LAB 3/4/5/6: `configmap "shop-config" not found` หรือ `pods "envpod" not found` | ลบไปแล้ว หรือข้าม LAB 2/5 | ทำ LAB 2 (และ LAB 5 สำหรับ `volpod`) ใหม่ก่อน |
| `kubectl exec` เข้า `envpod`/`envfrom` ไม่ได้ และ STATUS เป็น `Completed` | `sleep 86400` จบหรือ Pod ถูกลบ (`restartPolicy: Never`) | ลบแล้ว apply Pod นั้นใหม่ |
| แก้ ConfigMap แล้วไฟล์ใน volume ยังไม่เปลี่ยนหลัง 20–60 วินาที | kubelet sync เป็นรอบ (วัดได้ 37–88 วินาที) | รอได้ถึง 2 นาที ถ้าเกินให้ตรวจว่าไม่ได้ใช้ subPath และแก้ ConfigMap ชื่อ/namespace ถูก |
| `watch.sh` พิมพ์ `เกิน 180 วินาทีแล้วยังไม่เปลี่ยน` | Pod `volpod` ไม่ได้อยู่ หรือ ConfigMap ถูกลบสร้างใหม่ | `kubectl get pod volpod`, `kubectl get cm shop-config -o yaml` แล้วรันใหม่ |
| ไฟล์ subPath / env ไม่เปลี่ยนเลย | พฤติกรรมปกติ อ่านครั้งเดียวตอนเริ่ม | `kubectl rollout restart` (Deployment) หรือลบแล้วสร้าง Pod ใหม่ |
| `wget: can't connect to remote host: Connection refused` ใน Pod nginx | `localhost` ไปที่ IPv6 `::1` แต่ nginx ฟัง IPv4 | ใช้ `curl -s 127.0.0.1/` หรือ `wget -qO- 127.0.0.1/` |
| วนรอไฟล์ใน LAB 7 พิมพ์ `command terminated with exit code 1` ซ้ำ ๆ | `grep -q` ยังไม่เจอคำแล้ว `kubectl exec` รายงาน exit code | ใส่ `2>/dev/null` ท้าย `kubectl exec ... grep -q ...` ตามคำสั่งในเอกสาร |
| ไฟล์ nginx เป็นค่าใหม่แต่ `curl` ได้ค่าเก่า | nginx อ่านไฟล์ครั้งเดียวตอนเริ่ม | `kubectl exec ngx -- nginx -s reload` หรือ `kubectl rollout restart deploy/plain` |
| `Warning: Detected changes to resource ngx which is currently being deleted` | apply ซ้ำขณะ Pod เดิมยัง Terminating | รอ `kubectl get pod` ว่างก่อนแล้ว apply ใหม่ |
| `Warning: would violate PodSecurity "restricted:latest" …` | ใช้ Pod nginx/busybox ใน namespace ที่ตั้ง `warn: restricted` | ปกติ เป็นแค่คำเตือน (LAB 1–9 ใช้ `default`) |
| `kubectl edit` ค้าง / หน้าจอแปลก ๆ `Vim: Warning: Output is not to a terminal` | `kubectl edit` เปิด vim แต่ไม่มี terminal โต้ตอบ | กด `Ctrl+C` หรือปิด session แล้วใช้ `kubectl patch`/`kubectl apply -f` แทน ใน terminal ปกติออกจาก vim ด้วย `Esc` แล้ว `:q!` |
| ``The ConfigMap "..." is invalid: data: Forbidden: field is immutable when `immutable` is set`` | ConfigMap เป็น `immutable: true` | ลบแล้วสร้างใหม่ หรือสร้างชื่อใหม่แล้วชี้ Deployment ไปชื่อใหม่ |
| LAB 9 ได้ชื่อ ConfigMap ไม่ใช่ `web-config-gh5tkgmddg` | `kz/announcement.txt` ไม่ตรงทุกไบต์ (ยังเป็น v2, editor เติม/ลบ newline) | `printf 'ประกาศ v1\n' > kz/announcement.txt` |
| LAB 9 ConfigMap `web-config-...` ค้างหลัง `kubectl delete -k kz` | `delete -k` ลบเฉพาะชื่อจากไฟล์ปัจจุบัน | `kubectl get cm -o name \| grep web-config \| xargs -r kubectl delete` |
| `ErrImagePull` / `ImagePullBackOff` ของ `som-shop-web:1.5` หรือ `postgres:17.11-alpine` | ยังไม่ได้ load image เข้า Node (คลัสเตอร์ใหม่หรือข้าม LAB 0) | LAB 0 ขั้นที่ 5 |
| `provided port is already allocated` ตอน apply `20-web.yaml` | Service อื่นจอง 30080 (เช่น `som-shop` ของบทที่ 9 ค้าง) | `kubectl get svc -A \| grep 30080` แล้วลบ namespace ที่ค้าง |
| `/api/shop` ได้ค่าเดิมหลัง `rollout restart` | Pod เก่ายังตอบในช่วง preStop 5 วินาที | รอราว 8 วินาทีหลัง `successfully rolled out` แล้วลองใหม่ |
| footer เป็น `$(POD_NAMESPACE)` ตรง ๆ | ใส่ `$(VAR)` ในค่าของ ConfigMap ที่ใช้ผ่าน envFrom | ตั้งค่านั้นใน `env` ของ Deployment (`kubectl set env` หรือแก้ YAML) |
| หลัง `kubectl apply -f k8s/20-web.yaml` footer ยังเป็นค่าที่ `set env` ไว้ | `kubectl set env` ไม่อยู่ใน last-applied apply จึงไม่ลบ | `kubectl -n som-shop set env deploy/som-web SHOP_FOOTER-` |
| `Warning: resource deployments/som-web was previously managed with 'kubectl apply' …` ตอน `rollout undo` | undo ไม่แก้ annotation last-applied | ปกติ ถ้าจะให้ตรงไฟล์ให้ `kubectl apply -f k8s/` ภายหลัง |
| `rollout history` CHANGE-CAUSE ซ้ำกันหลายบรรทัด / เลข revision กระโดด | `rollout restart`, `set env`, `patch`, `undo` ไม่เปลี่ยน annotation `change-cause` และ template ที่ซ้ำของเดิมถูกนำกลับมาเป็นเลขใหม่ | ปกติ (`revisionHistoryLimit: 5` ทำให้ revision เก่าสุดหายไปด้วย) |
| `statefulset.apps/som-db configured` ตอน `kubectl apply -f k8s/` ทั้งที่ไม่ได้แก้ไฟล์ | kubectl เทียบกับค่าตั้งต้นที่ API server เติม | ปกติ ไม่มี revision ใหม่ และ `som-db-0` ไม่ restart |
| browser เปิด `http://localhost:30080` ไม่ได้ ทั้งที่ใน k8s-lab `curl -s localhost:30080/api/stats` ได้ | container `k8s-lab` ไม่ได้ publish 30080 หรือโปรแกรมอื่นใช้พอร์ตนี้ | 🖥️ `docker port k8s-lab` ต้องมี `30080/tcp` ถ้าไม่มีใช้ 🖥️ `ssh -p 2223 -L 30080:localhost:30080 root@localhost` แล้วเปิดใหม่ |
| refresh browser แล้วประกาศสลับเก่า/ใหม่ | แต่ละ Pod เห็นไฟล์ใหม่ไม่พร้อมกัน | ปกติ รอราว 1–1.5 นาที (`wait-announcement.sh` บอกเวลาที่ครบ 12/12) |
| เวลาในชื่อโฟลเดอร์ `..2026_10_05_…` หรือ `ls -la` ใน Pod ช้ากว่านาฬิกา 7 ชั่วโมง | container ใช้ UTC | ปกติ |
| `Error from server (NotFound)` ตอนเก็บกวาด | ลบไปแล้วในขั้นก่อน | ไม่เป็นไร |

---

## Checklist ส่งงาน

ส่งภาพหน้าจอ (screenshot ของ terminal/browser) ตามรายการ พร้อมคำตอบคำถามชวนคิดอย่างน้อย LAB ละ 1 ข้อ และคำถามท้าย LAB 10 ทั้ง 5 ข้อ

- [ ] **LAB 0** `kubectl get nodes` (3 Ready), `kubectl version` (เห็น Kustomize), ไม่มี NodePort 3008x ค้าง และ `crictl images` ที่เห็น `som-shop-web 1.5` + `postgres 17.11-alpine` บนทั้งสอง worker
- [ ] **LAB 1** `kubectl get cm -A`, `api-resources` (`configmaps cm v1 true`), ผล `{"EMPTY":"",...}` ของ `--from-env-file`, `already exists`, `binaryData` ของ `logo.bin` และ `Too long: may not be more than 1048576 bytes`
- [ ] **LAB 2** `kubectl logs envpod` (`ARGS: ร้านน้องส้ม $(NOPE)`) และ args ใน spec `["$(SHOP_NAME)","$(NOPE)"]`
- [ ] **LAB 3** `kubectl logs envfrom` (มี `CFG_1bad`, `CFG_shop.name`), `CFG_APP_THEME=harbor (จาก env)`, `CFG_FOOTER=... $(POD_NAMESPACE)` และ `echo $CFG_shop.name` ได้ `.name`
- [ ] **LAB 4** สถานะ 4 Pod ตอน 25 วินาที, ข้อความ error ทั้ง 3 แบบ, สถานะหลังสร้าง `not-here` (`nokey` ยังค้าง), `ls /etc/opt-cm` ที่เห็น `HELLO` หลังรอ และ `configmap "shop-config" not found` ของ namespace `other`
- [ ] **LAB 5** `ls -la /etc/all` (symlink `..data`), `-r--------` ของ `menu/today.txt`, subPath เป็นไฟล์จริง และ `Read-only file system`
- [ ] **LAB 6** ผล `./watch.sh` ทั้ง 3 รอบพร้อมเวลาของเครื่องตัวเอง (volume เปลี่ยน subPath/env ไม่เปลี่ยน) และ `..data` ชี้โฟลเดอร์ใหม่
- [ ] **LAB 7** ไฟล์ v2 แต่ `curl` ได้ `menu v1` → reload → `menu v2`, `plain` ตอบ `menu v1` ทั้งที่ไฟล์ v3 → `rollout restart` → `menu v3`, annotation `restartedAt` + `checksum/config` และ `rollout history` 3 revision
- [ ] **LAB 8** error `Forbidden: field is immutable` ทั้ง 4 วิธี, label `tier=menu` และ `79 true` หลังลบสร้างใหม่
- [ ] **LAB 9** `kubectl kustomize kz` (`web-config-gh5tkgmddg`), หลังแก้ไฟล์ได้ `web-config-6db7mkcg8t` + `deployment.apps/kz-web configured`, REVISION 1–2 และ ConfigMap เก่าค้างหลัง `delete -k`
- [ ] **LAB 10** (1) ขั้น A `orders=3` + `(ไม่มีประกาศ)` (2) ขั้น B `/api/shop` ค่าจาก ConfigMap + `ls -la /etc/som` (3) ขั้นเสริม footer `$(POD_NAMESPACE)` → `namespace som-shop` (4) ขั้น C1 ค่าเดิมหลังรอ 90 วินาที + `RESTARTS 0` (5) ขั้น C2 `ร้านน้องส้ม สาขาท่าเรือ`/sunset/promo + `orders=3` (6) ขั้น D ผล `wait-announcement.sh` ของเครื่องตัวเอง + `get pod` ก่อน/หลัง (ชื่อเดิม RESTARTS 0) (7) ขั้น E `ร้านน้องส้ม (v2)` + `Forbidden` + ผลหลัง `rollout undo` (8) ขั้น F `4 som:meow1234@` (บังรหัสในภาพ) + `cannot patch resource "configmaps"` (9) `orders=4` หลังคืนสภาพ (10) browser 4 ฉาก: harbor → ยังเดิมหลังแก้ → sunset + โปร → ประกาศ 18:00
- [ ] ท้ายสุด `kubectl get cm` ใน `default` เหลือแค่ `kube-root-ca.crt` และ `kubectl get pod` ใน `default` ว่าง

---

## ตารางเก็บกวาดและคืนสภาพ

ใช้ตรวจหลังจบแต่ละ LAB หรือเมื่อผลเริ่มเพี้ยน 🐧 ทุกคำสั่งรันใน SSH session ของ k8s-lab

| สิ่งที่อาจค้าง | มาจาก LAB | ตรวจด้วย | คืนสภาพด้วย |
|---|---|---|---|
| ConfigMap `demo`, `files`, `envf`, `bin`, `big2` + ไฟล์ `logo.bin`, `big.txt`, `big2.txt` | 1 | `kubectl get cm`; `ls labs/lab01-create` | `kubectl delete cm demo files envf bin big2`; `rm -f logo.bin big.txt big2.txt` (ใน `lab01-create`) |
| ConfigMap `shop-config`, Pod `envpod`, `envfrom`, `volpod` (ใช้ LAB 2–6) | 2–6 | `kubectl get pod,cm` | `kubectl delete pod envpod envfrom volpod --now; kubectl delete cm shop-config` |
| Pod `nocm`, `nokey`, `optpod`, `novol`, ConfigMap `not-here`, namespace `other` | 4 | `kubectl get pod; kubectl get ns other` | `cd …/labs/lab04-missing && kubectl delete -f nocm.yaml -f nokey.yaml -f optpod.yaml -f novol.yaml --now; kubectl delete cm not-here; kubectl delete ns other` |
| Pod `ngx`, Deployment `plain`, ConfigMap `nginx-conf`, namespace `psa-demo` | 7 | `kubectl get pod,deploy,cm; kubectl get ns psa-demo` | `cd …/labs/lab07-reload && kubectl delete -f ngx.yaml -f plain-deploy.yaml -f nginx-conf.yaml; kubectl delete ns psa-demo` |
| ConfigMap `frozen` | 8 | `kubectl get cm frozen` | `kubectl delete cm frozen` |
| Deployment `kz-web`, ConfigMap `web-config-*`, ไฟล์ `kz/announcement.txt` ที่ถูกแก้ | 9 | `kubectl get deploy kz-web; kubectl get cm \| grep web-config; cat kz/announcement.txt` | `kubectl delete -k kz; kubectl get cm -o name \| grep web-config \| xargs -r kubectl delete; printf 'ประกาศ v1\n' > kz/announcement.txt` |
| namespace `som-shop` (**จอง NodePort 30080**) + ConfigMap ร้าน, ServiceAccount `intern`, PVC `data-som-db-0` | 10 | `kubectl get ns som-shop`; `kubectl -n som-shop get all,cm,pvc,sa` | `kubectl delete ns som-shop` (หรือเก็บไว้สำหรับบทที่ 11) |
| image `som-shop-web:1.5`, postgres, nginx, busybox บน Node และ `/root/postgres.tar` | 0–10 | `docker exec lab-worker crictl images`; `ls /root/postgres.tar` | **เก็บ image ไว้ได้** (ใช้ซ้ำในบทถัดไป ถ้า `k8s-down` จะหายไปด้วย) ไฟล์ tar ลบได้ `rm -f /root/postgres.tar` |

ตอนลบของที่ไม่มีอยู่แล้ว kubectl อาจแจ้ง `NotFound` ซึ่งไม่เป็นไร

---

## เก็บกวาดหลังจบบท

🐧 **ใน SSH session ของ k8s-lab** ตรวจครั้งสุดท้าย

```bash
kubectl get nodes
kubectl get ns
kubectl get pod,deploy,cm
kubectl get pv,pvc -A
```

ผลที่ถูกต้อง: 3 Node `Ready`, ใน namespace `default` ไม่มี Pod/Deployment และมี ConfigMap แค่ `kube-root-ca.crt` (ผลจริงท้ายการทดลอง: `configmap/kube-root-ca.crt   1      37m`) ถ้าลบ `som-shop` แล้ว namespace จะเหลือ 5 ตัวตั้งต้น (`default`, `kube-node-lease`, `kube-public`, `kube-system`, `local-path-storage`) และไม่มี PV/PVC

คลัสเตอร์ `lab` และ image ของร้านเก็บไว้ใช้ต่อในบทถัดไปได้ ถ้าต้องการคืนทรัพยากรเครื่อง ให้ลบคลัสเตอร์ด้วย `k8s-down` (image ที่ `kind load` ไว้จะหายไปด้วย ครั้งหน้าต้อง `k8s-up` และ build/`kind load` ใหม่) แล้วออกจาก SSH ด้วย `exit`

บทถัดไป: **บทที่ 11 Secret — ซองปิดผนึก** จะย้ายรหัสผ่าน `som:meow1234` ออกจาก YAML ของ Deployment/StatefulSet ไปไว้ในที่ที่ให้สิทธิ์แยกจาก ConfigMap ได้

---

> **หมายเหตุเกี่ยวกับภาพประกอบ:** ภาพประกอบ LAB (ยกเว้นภาพในโฟลเดอร์ [`images/screenshots/`](images/screenshots/) ซึ่งเป็นภาพหน้าจอจริงจากการทดลอง) สร้างขึ้นด้วยปัญญาประดิษฐ์สำหรับการสร้างภาพเพื่อใช้ประกอบการเรียนการสอน ชุดคำสั่งสร้างภาพอยู่ใน [`images/imagegen-prompts.md`](images/imagegen-prompts.md) ภาพใช้อุปมาเชิงเปรียบเทียบ ตัวเลขในภาพ (เช่น ชื่อ Pod, จำนวนวินาที และ hash) เป็นค่าตัวอย่าง ให้ยึดผลลัพธ์คำสั่งในเอกสารและในเครื่องของนักศึกษาเป็นหลัก ภาพหน้าจอจริง 4 ภาพถ่ายจาก browser ที่เปิด NodePort 30080 โดยตรง (บนเครื่องนักศึกษาคือ `http://localhost:30080`) ในรอบที่ทำขั้น C1, C2 และ D ซ้ำหลังคืนสภาพร้าน (หัวข้อ 10.11) ชื่อ Pod และจำนวนออเดอร์ (4) ในภาพจึงต่างจากผลคำสั่งในขั้นหลักของเอกสาร
