# แผนบทเรียน 010 — Kubernetes ConfigMap (กระดานประกาศของโซนที่ทุกบูธอ่านได้)

> สถานะ: แผน + storyboard ภาพเท่านั้น (ยังไม่เขียน README/ไฟล์ LAB) — pre-check รันจริงแล้ว 5 ต.ค. 2569 ใน container ทดลอง `k8s-lab-cmsec-7ca683` (ใช้ร่วมกับบท 011, NodePort `30090-30092`, ลบแล้ว ยืนยันด้วย `k8s-lab.sh ls` ว่าว่าง) kubectl v1.37.1 (Kustomize v5.8.1) / Node v1.37.0
> Storyboard: `logs/010_configmap/images.json` (Theory 40 ภาพ T01–T40, LAB 21 ภาพ L01–L21, needs_test 40 ภาพ) สร้างจาก `logs/010_configmap/build_images.py` + `imgcommon.py` (สำเนาเดียวกับ `logs/011_secret/imgcommon.py`) → `images.json`, `010_kubernetes_configmap/01_Theory/images/imagegen-prompts.md`, `010_kubernetes_configmap/02_LAB/images/imagegen-prompts.md`
> ภาพตัวละครอ้างอิง: `010_kubernetes_configmap/01_Theory/images/00-character-som.png` · สร้างภาพด้วย `logs/010_configmap/gen_images.sh`
> ไฟล์ทดลอง: `logs/010_configmap/scratch/t/` (`p1–p9.sh` + `.log`, `p2.yaml`, `p3.yaml`, `p8.yaml`, `kz/`), แอปร่าง 1.4 (ต้องเปลี่ยนเป็น 1.5) + manifest ร้าน `logs/010_configmap/scratch/shop/` (`app/`, `00-namespace.yaml`, `10-db.yaml`, `15-config.yaml`, `20-web.yaml`), build log `scratch/build.log`, ตัวตรวจภาพ `scratch/validate.py`

## 0. ภาพรวมและข้อกำหนด

- ผู้เรียนผ่าน 001–009 (Pod, Node, Namespace/RBAC/PSA, ReplicaSet, Service, Deployment, PV/PVC, StatefulSet)
- โฟลเดอร์ LAB: `docker cp 010_kubernetes_configmap k8s-lab:/workspace/` → `cd /workspace/010_kubernetes_configmap/02_LAB` (LAB1–9 `cd labs/labNN-*`, LAB10 `cd som-shop-v6`)
- **ใช้ได้ใน LAB:** ทุกอย่างของ 001–009 + ConfigMap, `kubectl apply -k` (kustomize ใน kubectl), annotation checksum
- **ยังไม่ใช้:** Secret (ปิดบทด้วยปัญหารหัสผ่าน), Ingress, HPA, Helm (ปูทางเฉพาะ kustomize)
- **อุปมาใหม่:** ConfigMap = กระดานประกาศไม้ก๊อกกรอบ teal ในโซน มีการ์ด key: value; env/envFrom = การ์ดติดอกพนักงานตอนเข้ากะ (เปลี่ยนต้องเข้ากะใหม่ = Pod ใหม่); volume = กระดานเล็กในบูธที่ **kubelet = หุ่นยนต์ลูกเรือตัวกลมสีเทา หนวดเดียว ถือถุงการ์ด** เดินมาอัปเดตราวนาทีละครั้ง; subPath = สำเนาการ์ดแปะเทปที่ไม่มีใครมาเปลี่ยน; `..data` = ป้ายลูกศรที่สลับไปชุดการ์ดใหม่ทีเดียว; immutable = กระดานเคลือบแผ่นอะคริลิกใสติดสติกเกอร์ตราประทับ; configMapGenerator = เครื่องพิมพ์ป้ายที่พิมพ์กระดานใหม่พร้อมรหัสท้ายชื่อ
- ห้ามในภาพบทนี้: Secret/ซองปิดผนึก/กุญแจ (ยกเว้นภาพปิดบท T40, L21), รหัสผ่านแสดงเป็น `●●●●`

## 1. สารบัญทฤษฎี (01_Theory/README.md) — ภาพ T01–T40

| # | หัวข้อ | เนื้อหาหลัก | ภาพ |
|---|-------|------------|-----|
| 1 | บทนำ | ต่อบท 009: `SHOP_NAME`/`SHOP_FOOTER`/`DATABASE_URL` (มี `meow1234`) เขียนตรงใน `20-web.yaml`, ธีม/เวอร์ชันฝังใน image ด้วย build-arg; อุปมาใหม่ | T01–T03 |
| 2 | ปัญหาค่าตั้งค่าฝังใน image/YAML | เปลี่ยนชื่อร้าน = build → kind load → rollout; หลัก 12-factor (config แยกจากโค้ด, image เดียวหลายสภาพแวดล้อม dev/test/prod); config คืออะไร / ไม่ใช่อะไร (ข้อมูล = PVC, ความลับ = บท 011) | T04–T06 |
| 3 | ConfigMap คืออะไร | object key-value, `data` (UTF-8) vs `binaryData` (base64, ไฟล์ไบนารี; `--from-file` ไฟล์ที่ไม่ใช่ UTF-8 ไปอยู่ `binaryData` เอง — ทดสอบแล้ว), ไม่มี spec/status, ขนาดรวม ≤ 1 MiB (`Too long: may not be more than 1048576 bytes`), namespaced (`kubectl api-resources` → `configmaps cm v1 true`), ไม่ใช่ที่เก็บความลับ; `binaryData` ไม่ถูกนำไปเป็น env (จาก `kubectl explain`) | T07–T10 |
| 4 | วิธีสร้าง | `--from-literal` (ค่าไทยใช้ได้), `--from-file` (key = ชื่อไฟล์, `key=file` ตั้งชื่อเอง, `--from-file=.` ทั้งโฟลเดอร์), `--from-env-file` (บรรทัด `#` ข้าม, `EMPTY=` ได้ค่าว่าง), YAML (`data:` + block `|`), `--dry-run=client -o yaml`; สร้างซ้ำ → `configmaps "demo" already exists` ใช้ `--dry-run=client -o yaml \| kubectl apply -f -` เพื่ออัปเดต; `kubectl get cm -o yaml`, `describe cm` (แสดง Data/BinaryData) | T11–T14 |
| 5 | ใช้เป็น env | `env.valueFrom.configMapKeyRef` (name/key/optional), `envFrom.configMapRef` + `prefix`, `command/args` อ้าง `$(VAR)` (ตัวที่ไม่มีค้างเป็น `$(NOPE)`), env ชนะ envFrom เมื่อชื่อซ้ำ, **`$(VAR)` ในค่าที่มาจาก envFrom ไม่ถูกแทนค่า**, v1.37 รับ key ทุกแบบเป็นชื่อ env (`1bad`, `shop.name`, `announcement.txt` ไม่ถูกข้าม ไม่มี event เตือน) แต่ shell อ่านไม่ได้ → ตั้งชื่อ UPPER_SNAKE_CASE | T15–T19 |
| 6 | ใช้เป็น volume | `volumes.configMap` ทุก key = ไฟล์ (symlink → `..data/…`), mount เป็น read-only (`Read-only file system`; ConfigMap volume = ext4 `ro` ไม่ใช่ tmpfs), `items` (key → path ย่อย), `defaultMode`/`mode` (0400 → `-r--------`, ปกติ 0644, YAML ใช้เลขฐานแปดนำ 0), `subPath` (ไฟล์เดียวไม่ทับโฟลเดอร์ แต่ไม่อัปเดต), mount ทับโฟลเดอร์เดิมทั้งโฟลเดอร์ | T20–T23 |
| 7 | ไม่มี ConfigMap/key + optional | env/envFrom → `CreateContainerConfigError` (`Error: configmap "not-here" not found`, `Error: couldn't find key NOPE in ConfigMap default/shop-config`); volume → ค้าง `ContainerCreating` + `FailedMount … configmap "not-here" not found`; `optional: true` เริ่มได้ (env ว่าง, โฟลเดอร์ว่าง); สร้าง ConfigMap ภายหลัง → Pod ที่ค้าง Running เองไม่ต้องลบ | T24–T25 |
| 8 | การอัปเดต | env ไม่เปลี่ยนจนได้ Pod ใหม่; volume อัปเดตเอง ~1 นาที (kubelet sync period + cache; วัดได้ 56–85 วิ); `..data` symlink สลับแบบ atomic; subPath ไม่อัปเดต; แอปต้องอ่านไฟล์ใหม่เอง (nginx ต้อง `nginx -s reload`); `kubectl rollout restart` (annotation `kubectl.kubernetes.io/restartedAt`), checksum pattern (`checksum/config` ใน template annotation — Helm ใช้แบบนี้ ปูทาง), ชื่อใหม่ทุกครั้ง | T26–T30 |
| 9 | immutable | `immutable: true` → แก้ `data` ไม่ได้ / ปิด immutable ไม่ได้ (`Forbidden: field is immutable when \`immutable\` is set`), แก้ metadata (label) ได้, ต้อง delete + create หรือใช้ชื่อใหม่ (`-v2`); ข้อดี: kubelet ไม่ต้อง watch ลดภาระ API server, กันแก้พลาด | T31 |
| 10 | kustomize configMapGenerator | `kustomization.yaml` (`configMapGenerator` literals/files + `resources`), `kubectl kustomize`, `kubectl apply -k` → ชื่อ `web-config-<hash>` และแก้ชื่อใน Deployment ให้ → แก้ไฟล์ = ชื่อใหม่ = rollout อัตโนมัติ; ConfigMap เก่าค้าง (ต้องลบเอง/`--prune` แนวคิด); `secretGenerator` มีด้วย (ปูทางบท 011) | T32 |
| 11 | ของจริงในคลัสเตอร์ / ข้าม namespace / RBAC | `kube-system`: `coredns` (Corefile), `kube-proxy` (`config.conf`, `kubeconfig.conf`), `kubelet-config`, `kubeadm-config`; `kube-public/cluster-info`; `local-path-storage/local-path-config` (บท 008); `kube-root-ca.crt` ทุก namespace; อ้างข้าม namespace ไม่ได้ (ไม่มีฟิลด์ namespace) → `CreateContainerConfigError`; RBAC: Role `get,list configmaps` → อ่านได้ `patch` ได้ `Forbidden`, คนละ namespace `Forbidden` (ต่อบท 004) | T33–T35 |
| 12 | แนวปฏิบัติและสรุป | ตารางเลือก env vs volume vs subPath; แนวปฏิบัติ (YAML ใน git, ไม่ใส่ความลับ, ชื่อมีเวอร์ชัน/immutable, checksum/generator, แอปรองรับ reload); เส้นทางสรุป; cheatsheet; ปัญหาที่เหลือ: รหัสผ่านใน YAML/ConfigMap → บท 011 | T36–T40 |

## 2. ตาราง LAB (02_LAB/README.md) — ภาพ L01–L21

ทุกข้อรันจริงใน pre-check แล้ว (ผลในคอลัมน์ "ผลที่ต้องเห็น" มาจาก log `scratch/t/p*.log`)

| LAB | ชื่อ | เป้าหมาย | ไฟล์ (02_LAB/) | คำสั่งหลัก | ผลที่ต้องเห็น (pre-check) | สิ่งที่ต้องยืนยันตอนรัน LAB จริง |
|-----|------|---------|---------------|-----------|--------------------------|------------------|
| 0 | เตรียม | คลัสเตอร์ + image | `som-shop-v6/app/` | `kubectl get nodes`; postgres: `docker pull` + `docker save --platform linux/amd64` + `kind load image-archive`; `docker build -t som-shop-web:1.5 --build-arg APP_VERSION=1.5 app` + `kind load docker-image som-shop-web:1.5 --name lab` | build+load+postgres รวม 69 วิ (npm ci ใน container); busybox/nginx ให้ Node ดึงเอง | เวลา build บนเครื่องนักศึกษา |
| 1 | ส่องและสร้าง ConfigMap | รู้จัก object + 4 วิธีสร้าง | `labs/lab01-create/{shop.env,announcement.txt,default.conf}` | `kubectl get cm -A`; `kubectl -n kube-system get cm coredns -o jsonpath='{.data.Corefile}'`; `create configmap demo --from-literal=…`; `--from-file=announcement.txt --from-file=nginx.conf=default.conf`; `--from-env-file=shop.env`; `--from-file=. --dry-run=client -o yaml`; สร้าง demo ซ้ำ; ไฟล์ 1.1 MB | `{"EMPTY":"","SHOP_NAME":"ร้านน้องส้ม","SHOP_THEME":"sunset"}` (comment หาย); `configmaps "demo" already exists`; `Too long: may not be more than 1048576 bytes` (ไฟล์ 1,048,000 B ผ่าน); describe แสดง `Data`/`BinaryData`; ไฟล์ไบนารี → `binaryData` | ทำไฟล์ 1.1 MB ด้วย `head -c 1100000 /dev/zero \| tr '\0' a > big.txt` |
| 2 | env ทีละ key + `$(VAR)` | configMapKeyRef, args | `labs/lab02-env/{shop-config.yaml,envpod.yaml}` | `kubectl apply -f .`; `kubectl logs envpod` | `SHOP_NAME=ร้านน้องส้ม`, `ARGS: ร้านน้องส้ม $(NOPE)` | – |
| 3 | envFrom + prefix + ลำดับ | envFrom ทั้ง map | `labs/lab03-envfrom/envfrom-pod.yaml` | `kubectl logs`; `kubectl exec … -- printenv` | `CFG_1bad=…`, `CFG_shop.name=dot-key`, `CFG_announcement.txt=…` (ไม่ถูกข้าม, ไม่มี event InvalidVariableNames); `$(POD_NAMESPACE)` ในค่าจาก envFrom ค้างเป็นข้อความ; env ชื่อซ้ำชนะ envFrom | ไฟล์ pod แยกจาก LAB2 (pre-check รวม env+envFrom ใน `envpod` ตัวเดียว) |
| 4 | ไม่มีอยู่ + optional + ข้าม ns | error จริง | `labs/lab04-missing/{nocm,nokey,optpod,novol}.yaml` | apply → รอ 25 วิ → `get pod`, `describe`; `create configmap not-here --from-literal=HELLO=world` → รอ 20 วิ; `kubectl create ns other` + Pod อ้าง shop-config | `nocm/nokey CreateContainerConfigError`, `novol ContainerCreating` (`FailedMount … configmap "not-here" not found`), `optpod Running` `X=[]`; หลังสร้าง → `nocm`, `novol` Running เอง ≤ 20 วิ; ข้าม ns → `Error: configmap "shop-config" not found` | optpod volume ที่ optional: ไฟล์ `HELLO` โผล่หลังสร้าง ConfigMap ช้า (เห็นใน ≥ 2 นาที ไม่เห็นใน 40 วิแรก) — README บอก "ภายในไม่กี่นาที" |
| 5 | mount เป็นไฟล์ | volume, items, mode, subPath | `labs/lab05-volume/volpod.yaml` | `kubectl exec volpod -- ls -la /etc/all`; `ls -laR /etc/some`; `cat /etc/som/announcement.txt`; `mount \| grep etc`; `sh -c 'echo hack > /etc/all/menu.txt'` | `..data -> ..2026_10_05_…`, ทุก key เป็น symlink; `menu/today.txt` `-r--------`; mount `ext4 (ro,relatime)`; `Read-only file system` | – |
| 6 | อัปเดตเองและจับเวลา | env vs volume vs subPath | `labs/lab06-update/watch.sh` (patch + loop จับเวลา) | `./watch.sh` | 3 รอบ volume เปลี่ยนหลัง **65 / 70 / 85 วิ**; subPath ค่าเดิมตลอด; env ค่าเดิมตลอด; `..data` ชี้โฟลเดอร์เวลาใหม่ | เวลาบนเครื่องจริง (ช่วงคาด 30–90 วิ) |
| 7 | แอปต้องโหลดใหม่เอง | nginx reload, rollout restart, checksum | `labs/lab07-reload/{nginx-conf.yaml,ngx.yaml,plain-deploy.yaml}` | `kubectl exec ngx -- curl -s 127.0.0.1/`; patch → loop รอไฟล์ → curl → `nginx -s reload` → curl; `kubectl rollout restart deploy/plain`; patch annotation `checksum/config` | ไฟล์เปลี่ยนหลัง ~56 วิ แต่ยังตอบ `menu v2` จน reload → `menu v3`; restart เพิ่ม `kubectl.kubernetes.io/restartedAt`; patch checksum → REVISION 3 | **ใช้ `curl 127.0.0.1` ไม่ใช่ `wget localhost`** (busybox wget ไป `::1` แล้ว `Connection refused` เพราะ nginx ฟังแค่ IPv4) |
| 8 | immutable | แก้ไม่ได้ ต้องสร้างใหม่ | `labs/lab08-immutable/frozen.yaml` | `kubectl apply -f frozen.yaml`; patch data; patch `immutable:false`; `label cm frozen tier=menu`; apply/replace ไฟล์ที่แก้; delete + apply | ทุกการแก้ data/immutable → `The ConfigMap "frozen" is invalid: data: Forbidden: field is immutable when \`immutable\` is set` (apply/replace แสดง 2 บรรทัด `immutable:` + `data:`); label ได้; delete สำเร็จ | **ห้ามสาธิตด้วย `kubectl edit`** แบบไม่มี tty (ค้างใน vim) — ให้ใช้ patch/apply |
| 9 | kustomize | hash + rollout อัตโนมัติ | `labs/lab09-kustomize/kz/{kustomization.yaml,announcement.txt,deploy.yaml}` | `kubectl kustomize kz`; `kubectl apply -k kz`; แก้ `announcement.txt` → `apply -k kz`; `get cm \| grep web-config`; `rollout history` | `configmap/web-config-gh5tkgmddg created` → แก้ไฟล์ `configmap/web-config-6db7mkcg8t created` + `deployment.apps/kz-web configured`; REVISION 1, 2; `printenv announcement.txt` = `ประกาศ v2`; cm เก่ายังอยู่ | hash ขึ้นกับเนื้อหา — README ใส่ hash ตัวอย่างพร้อมบอกว่าเครื่องอื่นได้ค่าเดียวกันเมื่อไฟล์ตรงกันทุกไบต์ |
| 10 | **ร้านน้องส้มเปลี่ยนป้ายไม่ต้อง build ใหม่** | ข้อ 3 | `som-shop-v6/` | ข้อ 3 | ข้อ 3 | ข้อ 3 |

ภาพ LAB: L01 (LAB0), L02 (LAB1), L03 (LAB2), L04 (LAB3), L05 (LAB4), L06 (LAB5), L07 (LAB6), L08 (LAB7), L09 (LAB8), L10 (LAB9), L11–L21 (LAB10 = 11 ภาพ)

## 3. LAB10 "ร้านน้องส้มเปลี่ยนป้ายไม่ต้อง build ใหม่" (som-shop-v6)

### 3.1 การเปลี่ยนแอป → `som-shop-web:1.5` (ร่างและทดสอบแล้วที่ `scratch/shop/app/`)

แอปบท 009 อ่าน env `SHOP_NAME`, `SHOP_EYEBROW`, `SHOP_FOOTER`, `APP_THEME` (harbor/sunset; หน้าเป็น `force-dynamic` จึงอ่านตอนรัน — env ของ Pod ทับ `ENV` ใน image ได้), `APP_VERSION`, `DATABASE_URL` แต่ **โปรโมชันผูกกับ `version === '1.3'` และไม่มีการอ่านไฟล์** จึงเพิ่มรุ่น 1.5 (ห้ามใช้ 1.4 เพราะบท 007 ใช้ som-shop-web:1.4 เป็น tag ที่ไม่มีจริงเพื่อสาธิตรุ่นพัง) แก้น้อยที่สุด:

| ไฟล์ | การเปลี่ยน |
|------|-----------|
| `lib/shop.ts` | `promo: process.env.SHOP_PROMO ?? ''`; `ANNOUNCEMENT_FILE` (env, ค่าเริ่ม `/etc/som/announcement.txt`) + `readAnnouncement()` อ่านไฟล์ **ทุกครั้งที่เรียก** (`fs.readFileSync`, ไม่มีไฟล์/ว่าง → `null` ไม่ทำให้หน้าพัง) |
| `app/page.tsx` | แถบ `.promo` แสดงเมื่อ `SHOP_PROMO` ไม่ว่าง (แทนเงื่อนไข `version === '1.3'`); แถบ `.announcement` "📢 <ข้อความ>" เมื่อมีไฟล์ |
| `app/api/announcement/route.ts` (ใหม่) | `GET` → `"<pod> 1.5 <ข้อความ>"` หรือ `(ไม่มีประกาศ)` (text/plain) |
| `app/api/shop/route.ts` (ใหม่) | `GET` → JSON `{pod, version, shopName, theme, promo, eyebrow, footer}` ดูค่าที่ Pod เห็นโดยไม่ต้อง grep HTML |
| `app/globals.css` | `.announcement` (พื้นเหลือง ขอบส้ม) |
| `package.json`, `Dockerfile` | version 1.5.0; คอมเมนต์ build-arg `APP_VERSION=1.5` (ไม่ต้องใส่ APP_THEME — มาจาก ConfigMap) |

เลือก "แอปอ่านไฟล์ทุก request" แทน nginx sidecar เพราะ: Pod เดียว container เดียวเหมือนเดิม, `curl /api/announcement` ตรวจง่าย, ไม่ต้อง reload (nginx sidecar มีปัญหาเดียวกับ LAB7) — ยืนยันแล้วว่าทำงาน (ข้อ 3.3 ขั้น D)

### 3.2 ไฟล์

- `app/` (1.5), `hit.sh` (สำเนาบท 009)
- `k8s-start/` = สภาพเริ่ม (`00-namespace.yaml`, `10-db.yaml` = ของบท 009, `20-web.yaml` = ของบท 009 เปลี่ยน image เป็น 1.4 + footer `LAB 010`, ค่ายังเขียนใน env)
- `k8s/15-config.yaml` = ConfigMap `som-web-config` (`SHOP_NAME`, `SHOP_EYEBROW: ⚓ ท่าเรือ Kubernetes · ConfigMap`, `SHOP_FOOTER: Next.js + PostgreSQL · Kubernetes LAB 010 · ConfigMap som-web-config` (ไม่ใส่ `$(POD_NAMESPACE)`), `APP_THEME: harbor`, `SHOP_PROMO: ""`) + ConfigMap `som-announcement` (`announcement.txt`)
- `k8s/20-web.yaml` = web 1.5 ใช้ `envFrom: configMapRef som-web-config` + volume `som-announcement` mount ทั้งโฟลเดอร์ `/etc/som` (`readOnly`, **ไม่ใช้ subPath**); env เหลือ `POD_NAMESPACE`, `DATABASE_URL` (ยังมี `meow1234` — จงใจ), `PORT`, `HOSTNAME`; **ต้องแก้ `kubernetes.io/change-cause`** เป็น `1.5 ป้ายร้านจาก ConfigMap` (pre-check ลืมแก้ history จึงซ้ำ `1.2 db เป็น StatefulSet…`)
- `k8s/15-config-promo.yaml` (ชื่อสาขา/ธีม sunset/โปรโมชัน), `k8s/16-announcement-1800.yaml`, `k8s/17-config-v2.yaml` (immutable), `rbac/intern.yaml` (SA + Role get/list/watch pods, configmaps, deployments, statefulsets + RoleBinding)

### 3.3 ขั้นตอน (ผล pre-check จริง)

| ขั้น | คำสั่ง | ผลจริง |
|------|-------|-------|
| A | `kubectl apply -f k8s-start/` → POST 3 ครั้ง | `orders=3 products=6`; (pre-check เริ่มจาก ConfigMap เลย — **ขั้น A แบบ k8s-start ยังไม่ได้รัน** คาด `/api/announcement` → `(ไม่มีประกาศ)`, promo ว่าง) |
| B | `kubectl apply -f k8s/15-config.yaml -f k8s/20-web.yaml` | rollout สำเร็จ; `/api/shop` → `{"version":"1.5","shopName":"ร้านอาหารแมวน้องส้ม","theme":"harbor","promo":"","eyebrow":"⚓ ท่าเรือ Kubernetes · ConfigMap",…}`; `<title>ร้านอาหารแมวน้องส้ม</title>`, `class="theme-harbor"`; `/api/announcement` → `som-web-… 1.4 วันนี้ปลาทูสดมาก 🐟`; orders 3 |
| B (เสริม) | ใส่ `$(POD_NAMESPACE)` ใน ConfigMap | `"footer":"… namespace $(POD_NAMESPACE)"` (ไม่แทนค่า); `kubectl set env deploy/som-web SHOP_FOOTER='LAB 010 · namespace $(POD_NAMESPACE)'` → `"footer":"LAB 010 · namespace som-shop"` (env ชนะ envFrom) |
| C1 | `kubectl -n som-shop patch cm som-web-config --type merge -p '{"data":{"SHOP_NAME":"ร้านน้องส้ม สาขาท่าเรือ","APP_THEME":"sunset","SHOP_PROMO":"🎉 โปรวันนี้: ขนมปลาทูน่าลด 20%"}}'` (หรือ apply `15-config-promo.yaml`) → รอ 90 วิ | `/api/shop` ยังเป็น `ร้านอาหารแมวน้องส้ม`, `harbor`, promo ว่าง |
| C2 | `kubectl -n som-shop rollout restart deploy/som-web` | `"shopName":"ร้านน้องส้ม สาขาท่าเรือ","theme":"sunset","promo":"🎉 โปรวันนี้: ขนมปลาทูน่าลด 20%"`; `<title>ร้านน้องส้ม สาขาท่าเรือ</title>` (metadata ของ layout อ่าน env ตอนรัน ✅), `class="theme-sunset"`, `class="promo">🎉 โปรวันนี้…`; `orders=3` |
| D | `kubectl -n som-shop create configmap som-announcement --from-literal=announcement.txt='ปิดร้านเร็ว 18:00 น. ⛵' --dry-run=client -o yaml \| kubectl apply -f -` → loop `curl /api/announcement` | Pod แรกเปลี่ยนหลัง **58 วิ**, ครบทุก Pod (12 ครั้งติด) หลัง **75 วิ**; `RESTARTS 0`, AGE ต่อเนื่อง |
| E | apply `17-config-v2.yaml` (`som-web-config-v2`, `immutable: true`) → `kubectl -n som-shop patch deploy som-web --type json -p '[{"op":"replace","path":"/spec/template/spec/containers/0/envFrom/0/configMapRef/name","value":"som-web-config-v2"}]'` → patch cm v2 → `rollout undo` | rollout เอง `"shopName":"ร้านน้องส้ม (v2)"`; patch → `data: Forbidden: field is immutable when \`immutable\` is set`; undo มี Warning last-applied แล้วกลับเป็น `ร้านน้องส้ม สาขาท่าเรือ`; orders 3 |
| F (ปัญหา) | `kubectl apply -f rbac/intern.yaml`; `kubectl -n som-shop get deploy som-web -o yaml --as=system:serviceaccount:som-shop:intern \| grep -o 'som:[a-z0-9]*@'` | intern อ่านได้ → `som:meow1234@` (3 ที่: env web, db-seed, annotation last-applied); `get sts som-db -o yaml` เห็น `POSTGRES_PASSWORD` `meow1234` — ทดสอบในบท 011 ขั้น A แล้ว ✅ |
| คืนสภาพ | คงร้านไว้ให้บท 011 หรือ `kubectl delete ns som-shop` | (บท 011 มี `k8s-010/` เริ่มเองได้) |

## 4. ผล pre-check ที่ยืนยันแล้ว (5 ต.ค. 2569)

1. **สร้าง:** `--from-env-file` ข้ามบรรทัด `#` และเก็บ `EMPTY=""`; ไฟล์ไบนารีไป `binaryData`; ขนาดเกิน → `ConfigMap "big" is invalid: []: Too long: may not be more than 1048576 bytes` (1,048,000 B ผ่าน); สร้างซ้ำ → `configmaps "demo" already exists`
2. **kube-system:** `coredns`, `extension-apiserver-authentication`, `kube-apiserver-legacy-service-account-token-tracking`, `kube-proxy` (DATA 2), `kube-root-ca.crt`, `kubeadm-config`, `kubelet-config`; `local-path-storage/local-path-config` (DATA 4); `kube-public/cluster-info`
3. **env:** key ทุกแบบ (`1bad`, `shop.name`, `announcement.txt`) กลายเป็นชื่อ env ได้ใน v1.37 (ไม่ถูกข้าม ไม่มี event); `$(NOPE)` ค้าง; `$(VAR)` ในค่าจาก envFrom ไม่ถูกแทน; env ชนะ envFrom
4. **ข้อความ error จริง:** `CreateContainerConfigError` + `Error: configmap "not-here" not found`, `Error: couldn't find key NOPE in ConfigMap default/shop-config`; volume → `ContainerCreating` + `MountVolume.SetUp failed for volume "v" : configmap "not-here" not found`; สร้าง ConfigMap ภายหลัง → Running เองใน ≤ 20 วิ
5. **volume:** symlink `..data -> ..2026_10_05_08_41_40.4159514352`; `items` + `defaultMode: 0400` → `-r--------`; mount `ext4 (ro,relatime)`; เขียน → `Read-only file system`; `kubectl explain pod.spec.volumes.configMap` มี `defaultMode, defaultUser, items, name, optional` (`defaultUser` เป็นฟิลด์ใหม่ — ไม่สอน)
6. **อัปเดต:** volume 65/70/85 วิ (busybox), 56 วิ (nginx), 58–75 วิ (ร้าน); subPath และ env ไม่เปลี่ยน; nginx ต้อง `nginx -s reload`
7. **immutable:** patch/apply/replace data หรือ immutable → Forbidden; label ได้; delete ได้
8. **kustomize:** `kubectl apply -k` ใช้ได้ใน kubectl v1.37.1 (Kustomize v5.8.1), hash `web-config-gh5tkgmddg` → `web-config-6db7mkcg8t`, Deployment rollout เอง, cm เก่าค้าง
9. **RBAC:** `auth can-i get configmaps` yes / `update` no; patch → `Error from server (Forbidden): configmaps "shop-config" is forbidden: User "system:serviceaccount:default:reader" cannot patch resource "configmaps" in API group "" in the namespace "default"`; ns อื่น → `cannot list resource "configmaps" … in the namespace "other"`
10. **rollout restart** → annotation `kubectl.kubernetes.io/restartedAt: 2026-10-05T15:47:38+07:00`; patch `checksum/config` → REVISION ใหม่
11. **แอป 1.5:** build ผ่าน (Next.js 16.3.8), layout title/theme/promo/announcement เปลี่ยนตาม ConfigMap; `/api/stats` ยังใช้ได้ (`orders=3 products=6`)

## 5. จุดที่ต้องยืนยันตอนเขียน/รัน LAB จริง

1. LAB10 ขั้น A (`k8s-start/` ด้วย 1.5 ไม่มี ConfigMap) — ยังไม่ได้รันตรง ๆ: คาด `(ไม่มีประกาศ)` และไม่มีแถบโปรโมชัน
2. LAB10 `change-cause` ต้องแก้เป็นข้อความ 1.5 (pre-check ยังเป็นของบท 009); `rollout restart` ไม่เปลี่ยน change-cause → history มีข้อความซ้ำ (บอกใน README)
3. เวลาอัปเดต volume บนเครื่องนักศึกษา (ภาพใช้ "≈ 1 นาที", LAB6 ใส่ตัวเลขจริง 65–85 วิ)
4. LAB4 optional volume: ไฟล์โผล่ช้ากว่ากรณีปกติ (≥ 2 นาที) — วัดซ้ำ
5. LAB9 ค่า hash ตรงกับภาพ L10 เมื่อไฟล์ `kustomization.yaml`/`announcement.txt` ตรงไบต์ต่อไบต์ (`SHOP_NAME=ร้านน้องส้ม`, `ประกาศ v1\n` → `gh5tkgmddg`, `ประกาศ v2\n` → `6db7mkcg8t`)
6. หลัง rollout ไม่กี่วินาทีแรกอาจเจอ Pod เก่า (preStop 5 วิ) — ใน `curl` ให้รอ ~8 วิ
7. ทุกภาพ needs_test (40 ภาพ) ตรวจ Text/caption กับผล LAB จริงอีกรอบ
