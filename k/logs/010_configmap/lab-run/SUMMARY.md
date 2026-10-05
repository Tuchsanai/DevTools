# SUMMARY — ทดสอบ LAB บท 010 ConfigMap (5 ต.ค. 2569)

- container ทดลอง: `k8s-lab-cm010-b35a42` (image `tuchsanai/devtools-kind:2569_1` = `8108a1bc7901`, SSH 2224, NodePort 30090-30092 → 30080-30082) **เปิดค้างไว้ให้ถ่ายภาพ** ดู `handoff.md`
- kubectl v1.37.1 (Kustomize v5.8.1) / Server v1.37.0, `k8s-up` 54.6 วินาที
- รันทุกคำสั่งแบบนักศึกษา (`cd /workspace/010_kubernetes_configmap/02_LAB/...`) ด้วย `docker exec ... bash -lc` log จริง: `lab00.log` … `lab10.log` (บรรทัด `root@k8s-lab:...# <คำสั่ง>` + output + `[rc=N]`), สภาพสุดท้าย `final-state.txt`
- ทดสอบจาก host: `curl http://172.18.0.1:30090/...` (gateway → NodePort 30080) ได้ `/api/stats`, `/api/shop`, `/api/announcement`, `/` HTTP 200, `/som.png` 200 และ `k8s-lab.sh expect-host ... 30080 'orders=4'` PASS → บนเครื่องนักศึกษา `http://localhost:30080` ใช้ได้
- ไฟล์ LAB ที่สร้าง: `010_kubernetes_configmap/02_LAB/labs/lab01…lab09`, `som-shop-v6/` (ยังไม่ได้เขียน `02_LAB/README.md` — เป็นงานเขียนเอกสารแยก ใช้ log ชุดนี้เป็นค่าจริง)

## ผลรายข้อ

| LAB | ผล | เวลาจริง (เครื่องทดสอบ) | ข้อความ/ค่าจริงสำคัญ |
|---|---|---|---|
| 0 เตรียม | ✅ ผ่าน | postgres pull+save+load **16 วิ**, build+load `som-shop-web:1.5` **34 วิ** (npm ci ครั้งแรก) | 3 Node Ready v1.37.0, `standard (default)`, ไม่มี PV/PVC/NodePort ค้าง; `crictl images` บน worker ทั้งสอง: `som-shop-web 1.5`, `postgres 17.11-alpine`; **ไม่มี image 1.4 ใดๆ** |
| 1 ส่อง/สร้าง | ✅ | ~1 นาที | `kubectl get cm -A` 13 รายการ (kube-system 7 ตัวตามแผน + `local-path-config` DATA 4 + `cluster-info`); `configmaps cm v1 true ConfigMap`; envf → `{"EMPTY":"","SHOP_NAME":"ร้านน้องส้ม","SHOP_THEME":"sunset"}`; สร้างซ้ำ → `error: failed to create configmap: configmaps "demo" already exists`; ไฟล์ 1,100,000 B → `error: failed to create configmap: ConfigMap "big" is invalid: []: Too long: may not be more than 1048576 bytes`, 1,048,000 B ผ่าน; ไฟล์ไบนารี → `binaryData` (describe `logo.bin: 16 bytes`) |
| 2 env ทีละ key | ✅ | ~10 วิ | log `SHOP_NAME=ร้านน้องส้ม` / `APP_THEME=sunset` / `ARGS: ร้านน้องส้ม $(NOPE)` |
| 3 envFrom | ✅ | ~10 วิ | `CFG_1bad=starts-with-digit`, `CFG_shop.name=dot-key`, `CFG_announcement.txt=…`, `CFG_APP_THEME=harbor (จาก env)` (env ชนะ), `CFG_FOOTER=ร้านใน namespace $(POD_NAMESPACE)` (ไม่แทนค่า), ไม่มี event เตือน; ตรวจเพิ่มแบบไม่มี prefix: `1bad=…`, `shop.name=…` ก็เป็น env ได้ |
| 4 ไม่มี/optional/ข้าม ns | ✅ | ~2 นาที (+วัดซ้ำ) | 25 วิ: `nocm`/`nokey` `CreateContainerConfigError`, `novol` `ContainerCreating`, `optpod` Running `X=[] HELLO=[]`; `Error: configmap "not-here" not found`, `Error: couldn't find key NOPE in ConfigMap default/shop-config`, `MountVolume.SetUp failed for volume "v" : configmap "not-here" not found`; สร้าง not-here → `nocm`,`novol` Running เองใน **15 วิ** (`nokey` ยังค้าง — ถูกต้อง เพราะ key NOPE ยังไม่มี); optional volume ไฟล์ `HELLO` โผล่หลัง **61 / 64 / 43 วิ** (วัด 3 รอบ); env `HELLO` ใน optpod ยังว่างตลอด; ns other → `Error: configmap "shop-config" not found` |
| 5 volume | ✅ | <1 นาที | `..data -> ..2026_10_05_09_53_05.3156628874`, ทุก key เป็น symlink `-> ..data/<key>`; `menu/today.txt` `-r--------`; subPath เป็นไฟล์จริง (ไม่ใช่ symlink) `-rw-r--r--`; mount `ext4 (ro,relatime)`; `sh: can't create /etc/all/menu.txt: Read-only file system` |
| 6 จับเวลาอัปเดต | ✅ | 4.5 นาที (3 รอบ) | volume เปลี่ยนหลัง **85 / 55 / 62 วิ** (pre-check 65/70/85 → รวม 55–85 วิ); subPath = `วันนี้ปลาทูสด` ตลอด; env envpod = `ร้านน้องส้ม` ตลอด; `..data` ชี้โฟลเดอร์เวลาใหม่ |
| 7 nginx reload | ✅ | ~4 นาที | ไฟล์ใน ngx เปลี่ยนหลัง **75 วิ** (v2) / **63 วิ** (v3); `curl` ยังได้ `menu v1` → reload → `menu v2`; v3: ngx ยังตอบ `menu v2` จน reload → `menu v3`; Deployment `plain` ไฟล์เป็น v3 แต่ตอบ `menu v1` → `rollout restart` → `menu v3`, annotation `kubectl.kubernetes.io/restartedAt: 2026-10-05T17:08:34+07:00`; patch `checksum/config: a7aed9955c80` → REVISION 3; `wget -qO- localhost/` → `wget: can't connect to remote host: Connection refused` แต่ `127.0.0.1` ได้; namespace ที่ `warn: restricted` → `Warning: would violate PodSecurity "restricted:latest": allowPrivilegeEscalation != false … runAsNonRoot != true … seccompProfile …` (Pod ยังสร้างได้) — namespace `default` ไม่มีป้าย PSA จึงไม่เตือน |
| 8 immutable | ✅ | ~1 นาที | patch data → `The ConfigMap "frozen" is invalid: data: Forbidden: field is immutable when \`immutable\` is set`; patch immutable:false → `… invalid: immutable: Forbidden: …`; apply/replace (sed 99→79) → บรรทัด `data:` บรรทัดเดียว; label ได้; delete + apply → `79 true`; **`kubectl edit` แบบไม่มี tty ค้างใน vim จริง** (`Vim: Warning: Output is not to a terminal`) ต้อง kill |
| 9 kustomize | ✅ | ~30 วิ | `configmap/web-config-gh5tkgmddg created` → แก้ไฟล์ → `configmap/web-config-6db7mkcg8t created` + `deployment.apps/kz-web configured`; REVISION 1, 2; `printenv announcement.txt` = `ประกาศ v2`; cm เก่ายังอยู่; `kubectl delete -k kz` ลบแค่ตัวล่าสุด ตัว gh5… ค้างต้องลบเอง — **hash ตรงกับภาพ L10/T32** |
| 10 ร้าน som-shop-v6 | ✅ | ~12 นาที | ดูด้านล่าง; ออเดอร์ **0 → 3** (ขั้น A) คงที่ **3** ทุกขั้น (B, B เสริม, C1, C2, D, E) → **4** ตอนตั้งฉากสุดท้าย |

### LAB 10 รายขั้น

| ขั้น | ผลจริง |
|---|---|
| A `kubectl apply -f k8s-start/` | rollout เสร็จในไม่กี่วินาทีหลัง db Ready; `orders=0` → POST 3 → `orders=3 products=6`; `/api/shop` → `"version":"1.5","shopName":"ร้านอาหารแมวน้องส้ม","theme":"harbor","promo":"","eyebrow":null,"footer":"Next.js + PostgreSQL · Kubernetes LAB 010 · namespace som-shop"`; **`/api/announcement` → `som-web-… 1.5 (ไม่มีประกาศ)`**, ไม่มี `class="promo"` และ `class="announcement"`; หัวเว็บ `⚓ ท่าเรือ Kubernetes · ReplicaSet + Service` (ค่าเริ่มของแอป); `hit.sh` 30/30 ok; CHANGE-CAUSE `1.5 เริ่มบท 010 (ค่าร้านยังเขียนใน env)`; ไม่มี warning PSA |
| B `apply -f k8s/15-config.yaml -f k8s/20-web.yaml` | `som-web-config` DATA 5, `som-announcement` DATA 1; `/api/shop` → eyebrow `⚓ ท่าเรือ Kubernetes · ConfigMap`, footer `… · ConfigMap som-web-config`, theme harbor; `/api/announcement` → `som-web-… 1.5 วันนี้ปลาทูสดมาก 🐟`; HTML `class="announcement">📢 <!-- -->วันนี้ปลาทูสดมาก 🐟`; `/etc/som/announcement.txt -> ..data/announcement.txt`; REVISION 2 `1.5 ป้ายร้านจาก ConfigMap`; orders 3 |
| B เสริม | patch footer `LAB 010 · namespace $(POD_NAMESPACE)` + restart → `"footer":"LAB 010 · namespace $(POD_NAMESPACE)"`; `set env` → `"footer":"LAB 010 · namespace som-shop"`; env names `POD_NAMESPACE DATABASE_URL PORT HOSTNAME SHOP_FOOTER`; คืนด้วย `apply 15-config.yaml` + `set env SHOP_FOOTER-` |
| C1 `apply -f extra/15-config-promo.yaml` + รอ 90 วิ | ทั้ง 3 Pod ยัง `ร้านอาหารแมวน้องส้ม` / `harbor` / promo ว่าง, RESTARTS 0 |
| C2 `rollout restart` | `"shopName":"ร้านน้องส้ม สาขาท่าเรือ","theme":"sunset","promo":"🎉 โปรวันนี้: ขนมปลาทูน่าลด 20%"`; `<title>ร้านน้องส้ม สาขาท่าเรือ</title>`, `class="theme-sunset"`, `class="promo">🎉 โปรวันนี้: ขนมปลาทูน่าลด 20%`; hit.sh 12/12 ทั้ง 3 Pod ค่าใหม่; orders 3 |
| D ประกาศใหม่ | 3 รอบ: Pod แรก **37 / 63 / 59 วิ**, ทุก Pod (12/12) **48 / 82 / 88 วิ** (pre-check 58/75); ชื่อ Pod เดิม RESTARTS 0, AGE ต่อเนื่อง; HTML `📢 <!-- -->ปิดร้านเร็ว 18:00 น. ⛵` |
| E immutable v2 | json patch envFrom → `"shopName":"ร้านน้องส้ม (v2)"`; patch v2 → `The ConfigMap "som-web-config-v2" is invalid: data: Forbidden: field is immutable when \`immutable\` is set`; `rollout undo` → `Warning: resource deployments/som-web was previously managed with 'kubectl apply'. Rolling back will not update the …last-applied-configuration annotation…` แล้วกลับ `ร้านน้องส้ม สาขาท่าเรือ`/sunset; orders 3 |
| F intern | `can-i get configmaps` yes, `get deployments` yes, `get secrets` no, `patch configmaps` no; `get deploy som-web -o yaml --as=…intern` เจอ `som:meow1234@` **4 ครั้ง** (2 ใน `last-applied-configuration` บรรทัดเดียว + 2 ใน spec: db-seed และ web); `get sts som-db -o yaml` และ `get pod som-db-0 -o yaml` เห็น `POSTGRES_PASSWORD` `value: meow1234`; `get secrets` → `Forbidden … cannot list resource "secrets"`; patch cm → `Forbidden … cannot patch resource "configmaps"` |
| ฉากสุดท้าย | ลบ `som-web-config-v2`, `apply -f k8s/` + restart → ร้านอาหารแมวน้องส้ม/harbor/ประกาศ `วันนี้ปลาทูสดมาก 🐟`; POST 1 → `orders=4 products=6` |

## จุดที่แผนให้ยืนยัน (ข้อ 5 ของแผน)

1. ขั้น A ด้วย `k8s-start/` (1.5 ไม่มี ConfigMap) — ✅ `(ไม่มีประกาศ)` ไม่มีแถบโปรโมชัน ธีม harbor
2. change-cause — ✅ REVISION 1 `1.5 เริ่มบท 010 (ค่าร้านยังเขียนใน env)`, ตั้งแต่ REVISION 2 `1.5 ป้ายร้านจาก ConfigMap`; `rollout restart`/`set env`/`patch`/`undo` ไม่เปลี่ยน change-cause → history ซ้ำข้อความเดียวกัน (แม้ revision ของ v2 immutable ก็ยังเขียน `1.5 ป้ายร้านจาก ConfigMap`); revision เลขกระโดด (3 → ถูกใช้ซ้ำเป็น 5 เพราะ template เหมือนเดิม) และ `revisionHistoryLimit: 5` ทำให้ REVISION 1 หายจาก history ตอนจบ
3. เวลาอัปเดต volume — busybox 55–85 วิ, nginx 63–75 วิ, ร้าน 37–88 วิ → "≈ 1 นาที (บางครั้งเกือบ 1.5 นาที)"
4. optional volume สร้าง ConfigMap ทีหลัง — วัด 3 รอบ **43–64 วิ** (ไม่ช้ากว่าปกติแบบที่ pre-check เห็น ≥ 2 นาที) → README เขียน "ภายในราว 1 นาที (อาจถึง 2 นาที)"
5. hash kustomize — ✅ ตรง `gh5tkgmddg` / `6db7mkcg8t`
6. หลัง rollout — ใช้ `sleep 8` ก่อน curl แล้วไม่เจอ Pod เก่าเลยทุกครั้ง
7. ภาพ needs_test — ดูหัวข้อป้ายภาพด้านล่าง

## การเปลี่ยนแปลงจากแผน

1. **LAB 7: เพิ่ม `nginx-conf-v2.yaml`, `nginx-conf-v3.yaml`** แทน `kubectl patch` แบบ JSON (escape `\n` + `"` ซ้อนหลายชั้นพลาดง่าย — รอบแรกได้ `\\n` ดิบในไฟล์ log ทิ้งไว้ที่ `scratch/lab07-attempt1.log`) ใช้ `kubectl apply -f nginx-conf-v2.yaml` แทน
2. **LAB 7: `plain-deploy.yaml` เป็น nginx ที่ mount `nginx-conf`** (แทน busybox sleep) เพื่อให้เห็นว่า rollout restart ทำให้ได้ค่าใหม่จริง (`menu v1` → `menu v3`) และ checksum ใช้ `sha256sum` ของ `.data` จริง
3. **LAB 10: ไฟล์ C/D/E ย้ายไป `som-shop-v6/extra/`** (`15-config-promo.yaml`, `16-announcement-1800.yaml`, `17-config-v2.yaml`) ไม่ใส่ใน `k8s/` เพราะ `15-config-promo.yaml` ใช้ชื่อ `som-web-config` เดียวกัน `kubectl apply -f k8s/` จะทับกัน; `k8s/` = `00-namespace`, `10-db`, `15-config`, `20-web` ใช้เริ่ม/คืนสภาพได้ด้วยคำสั่งเดียว
4. **เพิ่ม `som-shop-v6/wait-announcement.sh <คำ>`** จับเวลาขั้น D (Pod แรก/ทุก Pod 12/12)
5. **LAB 2: `shop-config.yaml` เพิ่ม key `FOOTER: "ร้านใน namespace $(POD_NAMESPACE)"`** ให้ LAB 3 เห็น `$(POD_NAMESPACE)` ไม่ถูกแทน (ภาพ L04); LAB 3 ใช้ Pod `envfrom` แยก (ไฟล์ `envfrom-pod.yaml`) + env `CFG_APP_THEME` ชื่อซ้ำ
6. **LAB 4: เพิ่ม `other-ns.yaml`** (Pod `x` ใน ns `other`) แทน `kubectl run --overrides`
7. **ทุก Pod busybox ใช้ `sleep 86400`** (pre-check `sleep 3600` — envpod `restartPolicy: Never` จะ Completed ถ้าทำ LAB นานเกิน 1 ชม. แล้ว `watch.sh` ใน LAB 6 exec ไม่ได้)
8. **แอป 1.5**: เปลี่ยนเฉพาะ `package.json` version `1.5.0`, คอมเมนต์ Dockerfile/โค้ด `1.4:` → `1.5:` (ค่าเวอร์ชันมาจาก `--build-arg APP_VERSION=1.5`) — `package-lock.json` คงเดิม (root `1.0.0` เหมือนบทก่อน); ไม่มีคำว่า 1.4 ใน 02_LAB อีก
9. `k8s-start/20-web.yaml` CHANGE-CAUSE `1.5 เริ่มบท 010 (ค่าร้านยังเขียนใน env)`; footer `Kubernetes LAB 010 · namespace $(POD_NAMESPACE)` (env ปกติ แทนค่าได้)

## ป้าย/ข้อความในภาพ storyboard ที่ไม่ตรงผลจริง

| ภาพ | ส่วน | ปัจจุบัน | ควรใช้ |
|---|---|---|---|
| **L05** | caption_th | `สร้าง not-here ภายหลัง → ทุกตัว Running เอง` | `สร้าง not-here ภายหลัง → nocm และ novol Running เองใน ~15 วินาที (nokey ยังค้างเพราะ key NOPE ยังไม่มี)` |
| **L05** | Scene | `then a board is delivered and all lamps turn green` | `…three of the four lamps are green (the booth waiting for a missing card stays red)` — ป้าย "มากระดานแล้ว Running เอง" ใช้ได้ |
| **L07** | Text | `"volume: 65–85 วินาที"` | `"volume: 55–85 วินาที"` (หรือ `"volume: ≈ 1 นาที"`) |
| **L07** | caption_th | `เปลี่ยนหลัง 65/70/85 วินาที` | `เปลี่ยนหลัง 85/55/62 วินาที (ราว 1 นาที)` |
| **L08** | caption_th | `ไฟล์เปลี่ยน (~56 วินาที)` | `ไฟล์เปลี่ยน (~1 นาที: วัดได้ 63–75 วินาที)`; ป้าย `menu v2`/`menu v3`/`nginx -s reload` ตรงผลจริง |
| **L18** | caption_th | `Pod แรกเปลี่ยนหลัง ~58 วินาที ทุก Pod ภายใน ~75 วินาที` | `Pod แรกเปลี่ยนหลัง 37–63 วินาที ทุก Pod ภายใน 48–88 วินาที (≈ 1–1.5 นาที)`; ป้าย `≈ 1 นาที`, `RESTARTS 0` ใช้ได้ |
| **T27** | caption_th | `วัดได้ราว 1 นาที (56–85 วินาที)` | `วัดได้ราว 1 นาที (37–88 วินาที)` |
| **T25** | caption_th (เสริม) | `สร้าง ConfigMap ภายหลัง Pod ที่ค้างจะเริ่มเอง` | ถูกต้อง; ถ้าจะใส่เวลา: Pod ค้าง Running ใน ~15 วินาที, ไฟล์ใน optional volume โผล่ใน 43–64 วินาที |
| L20 | caption_th (เสริม) | — | ถ้าอ้างจำนวน: `som:meow1234@` อยู่ใน `get deploy -o yaml` 4 ที่ (2 ใน spec + 2 ใน annotation last-applied) ไม่ใช่ 3 |
| T28 | Text | `"..2026_10_05_08_47_02"` | ใช้ได้เป็นตัวอย่าง แต่ชื่อจริงมีเลขท้าย เช่น `..2026_10_05_09_53_05.3156628874` |

ภาพอื่น (L01–L04, L06, L09–L17, L19–L21, T08, T09, T13, T16–T20, T22–T24, T26, T29–T35) ข้อความตรงผลจริง — L02 ป้าย `configmaps "demo" already exists` เป็นส่วนท้ายของ `error: failed to create configmap: configmaps "demo" already exists` (ใช้ได้); T19 ยืนยันเพิ่มแล้วว่า `1bad`/`shop.name` เป็น env ได้แม้ไม่มี prefix

## ข้อควรระวังสำหรับนักศึกษา (ใส่ใน README)

- `kubectl apply -f .` ใน `lab02-env` สร้าง `pod/envpod` **ก่อน** `configmap/shop-config` (เรียงตามชื่อไฟล์) ถ้า `get pod` เร็วอาจเห็น `CreateContainerConfigError` ชั่วครู่แล้วหายเอง — หรือสั่ง `kubectl apply -f shop-config.yaml -f envpod.yaml`
- LAB 3 ใช้ prefix `CFG_` → `$CFG_1bad` อ่านใน shell ได้ (เพราะชื่อเต็มขึ้นต้นด้วย C) แต่ `$CFG_shop.name` ได้ `.name` (shell อ่านถึงแค่ `$CFG_shop`)
- `kubectl create configmap demo …` ซ้ำ → error; อัปเดตด้วย `--dry-run=client -o yaml | kubectl apply -f -` จะมี `Warning: resource configmaps/demo is missing the kubectl.kubernetes.io/last-applied-configuration annotation …` ครั้งแรก (ปกติ)
- kubectl v1.37 พิมพ์ผลลบเป็น `configmap "demo" deleted from default namespace`
- LAB 4: `nokey` **ไม่** หายเองหลังสร้าง `not-here` (คนละสาเหตุ) ต้องลบเอง
- LAB 6/7/10: ไฟล์จาก volume อัปเดตเอง **ราว 1 นาที บางครั้งเกือบ 1.5 นาที** อย่าเพิ่งสรุปว่าไม่ทำงานก่อน 2 นาที; subPath และ env ไม่เปลี่ยนเลย
- LAB 7: ใช้ `curl -s 127.0.0.1/` (หรือ `wget -qO- 127.0.0.1/`) ใน Pod nginx — `wget localhost` ไป `::1` แล้ว `Connection refused`; loop `until kubectl exec ngx -- grep -q …` ให้ใส่ `2>/dev/null` ไม่งั้นพิมพ์ `command terminated with exit code 1` ทุก 2 วินาที; รอ Pod เก่าหายก่อน apply ซ้ำ (`kubectl get pod` ว่าง) ไม่งั้นได้ `Warning: Detected changes to resource ngx which is currently being deleted`
- LAB 7: nginx (root, port 80) ใช้ใน `default` — ถ้าเอาไปใช้ใน `som-shop` (warn restricted) จะเห็น `Warning: would violate PodSecurity "restricted:latest" …` (แค่เตือน)
- LAB 8: **ห้ามใช้ `kubectl edit`** ใน terminal ที่ไม่ใช่ interactive (ค้างใน vim) ใช้ `patch`/`apply`; ถ้าเผลอเปิด vim ใน terminal ปกติ ออกด้วย `:q!`
- LAB 9: แก้ `kz/announcement.txt` แล้วให้คืนเป็น `printf 'ประกาศ v1\n' > kz/announcement.txt` ถ้าจะทำซ้ำ (hash ขึ้นกับเนื้อหาทุกไบต์ ใช้ editor ที่เติม/ลบ newline จะได้ hash อื่น); `kubectl delete -k kz` ไม่ลบ ConfigMap รุ่นเก่า
- LAB 10: `kubectl set env` ไม่ถูกบันทึกใน last-applied → `kubectl apply -f k8s/20-web.yaml` **ไม่ลบ** `SHOP_FOOTER` ที่ set ไว้ ต้อง `kubectl -n som-shop set env deploy/som-web SHOP_FOOTER-`
- LAB 10: `kubectl apply -f k8s/` ซ้ำหลังจบอาจพิมพ์ `statefulset.apps/som-db configured` ทั้งที่ไฟล์ไม่เปลี่ยน — ไม่สร้าง revision ใหม่และ `som-db-0` ไม่ restart (ปกติ)
- LAB 10: หลัง `rollout restart`/`undo` รอ ~8 วินาทีก่อน curl (preStop 5 วิ); `rollout undo` มี Warning last-applied (ปกติ)
- LAB 10 ขั้น F: รหัสผ่านในภาพ/สไลด์ให้แสดงเป็น `som:●●●●@` แม้ผลจริงบนจอจะเป็นค่าของ LAB
