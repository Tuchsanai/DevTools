# สัญญาร่วมของการแยกบทรวม 005 → 005 ReplicaSet / 006 Service / 007 Deployment

แหล่งเดิม (อ่านอย่างเดียว): `logs/005_rs_deploy_svc/plan.md`, `build_images.py` (prompt ทั้ง 67 ภาพในรูป t()/l()), `images.json`, `precheck.md` (ผลทดลองจริง 27 ข้อ)
โมดูลภาพร่วม: `logs/<บท>/imgcommon.py` (สำเนาเดียวกันทั้ง 3 บท — **ห้ามแก้**; ถ้าคิดว่าต้องแก้ ให้รายงานกลับ)

## 0. กติกาทั่วไป

- ห้ามเขียนนอก `/root/workspace/DevTools/k/` (ห้าม /tmp — ไฟล์ชั่วคราวใช้ `logs/<บท>/scratch/`), ห้ามแตะ container `k8s-lab` (รวม docker exec), ห้ามรัน LAB/คลัสเตอร์, ห้ามแก้บท 001–004 และห้ามลบ/แก้ `005_kubernetes_replicaset_deployment_service/` และ `logs/005_rs_deploy_svc/`
- ห้ามแก้ `logs/<บท>/gen_images.sh` (ผู้ประสานงานจัดการเอง)
- ผู้เรียน: ผ่าน 001 (k8s-lab, kind `lab`: lab-control-plane / lab-worker / lab-worker2, K8s v1.37, kubectl 1.37; `ssh -p 2223 root@localhost` รหัส `passwd`, JupyterLab `http://localhost:8889`; พอร์ต 30080–30082 ของเครื่องนักศึกษา map ตรงเข้า NodePort 30080–30082 ของ lab-control-plane ด้วย extraPortMappings), 002 (Pod, YAML, labels, probes, multi-container/native sidecar, init container, ร้าน som-shop all-in-one web+db, `som-shop-web:1.0`), 003 (Node, scheduler, nodeSelector/affinity/anti-affinity/topology spread, taints/tolerations + `tolerationSeconds` 300, cordon/drain, `docker stop lab-worker2` จำลองเรือล่ม, Downward API), 004 (Namespace, ResourceQuota, LimitRange, RBAC, PSA restricted, NetworkPolicy, DNS search domain, `som-shop-web:1.1` อ่าน `SHOP_EYEBROW`/`SHOP_FOOTER` จาก env, ร้าน 3 environment som-dev/som-staging/som-prod, port-forward หลุดเมื่อ Pod ถูกลบ)
- LAB ทุกข้อทำใน namespace ของตัวเอง จบด้วย `kubectl delete ns ...`; Pod busybox ใส่ `terminationGracePeriodSeconds: 1`; image สาธารณะ (nginx/busybox) ให้ Node pull เอง (pre-check #6: `kind load docker-image nginx:...` ล้ม `ctr: content digest ...: not found`); image ที่ build เองใช้ `kind load docker-image ... --name lab`; postgres ใช้ `docker save --platform linux/amd64 postgres:17.11-alpine -o <ไฟล์ใน workspace> && kind load image-archive ... --name lab` หรือให้ Node pull เอง
- kubectl 1.37 พิมพ์ `pod "x" deleted from <ns> namespace` (pre-check #4)
- แอปตัวอย่างเบา (ไม่ต้อง build): `nginx:1.27-alpine` ที่ `command` เขียน `index.html` = `web $VERSION from $(hostname)` แล้ว `exec nginx -g 'daemon off;'` + readinessProbe httpGet / period 2 (ใช้ได้ทั้ง 3 บท; บท 005 ใช้ busybox เป็นหลักและ nginx ได้)

## 1. ลำดับความรู้ (ห้ามใช้สิ่งที่ยังไม่เรียนในขั้นตอน LAB — กล่าวปูทางได้)

| บท | รู้แล้ว | ห้ามใช้ใน LAB |
|---|---|---|
| 005 | Pod, label, probe, init/sidecar, scheduling, namespace/quota/PSA/NetworkPolicy | Service (รวม `kubectl expose`), Deployment, `kubectl rollout` |
| 006 | + ReplicaSet | Deployment, `kubectl rollout` (ใช้ ReplicaSet สร้าง Pod หลัง Service; `kubectl expose rs/...` ได้) |
| 007 | + ReplicaSet + Service | PVC/StatefulSet/Ingress/HPA/ConfigMap/Secret แบบละเอียด/Job (ปูทางเท่านั้น) |

ภาพก็ใช้กติกาเดียวกัน (imgcommon ใส่ข้อห้ามให้แล้ว: บท 005 ห้ามประภาคาร/ผู้จัดการร้าน, บท 006 ห้ามผู้จัดการร้าน) — ภาพปูทางบทถัดไปเท่านั้นที่ใส่ `allow=True`

## 2. เรื่องเล่าต่อเนื่องและจุดส่งต่อ

- **005 ReplicaSet** — เปิด: Pod เดี่ยวหายแล้วไม่มีใครสร้างใหม่ (บท 002–004) → น้องส้มจ้าง "หัวหน้ากะ" (ReplicaSet) นับบูธให้ครบ
  - LAB สุดท้าย "ร้านน้องส้ม 3 บูธด้วย ReplicaSet": ns `som-booths` (label PSA warn restricted แบบ 004), ReplicaSet `som-booth` replicas 3, Pod template = ร้าน all-in-one ของบท 004 (native sidecar `db` postgres:17.11-alpine + emptyDir, init `wait-for-db`, `db-seed`, container `web` image `som-shop-web:1.1`) + env `POD_NAME` (Downward API `metadata.name`) → `SHOP_EYEBROW="⚓ บูธ $(POD_NAME)"` เพื่อให้หน้าเว็บบอกว่าบูธไหน + podAntiAffinity **preferred** topologyKey `kubernetes.io/hostname` (กระจายคนละเรือเท่าที่ทำได้; 2 worker → 3 บูธ = 2+1)
  - ขั้น: build/โหลด 1.1 (ถ้าคลัสเตอร์ใหม่: build จากโฟลเดอร์บท 004 `som-shop-envs/app` — คัดลอกมาเป็น `02_LAB/som-booths/app/` ไม่ต้อง; ให้อ้างโฟลเดอร์ 004 หรือคัดลอกเป็นสำเนา ตัดสินใจในแผน) → apply → `get pods -o wide` เห็นกระจาย 2 เรือ → port-forward ทีละ Pod (`kubectl port-forward pod/<ชื่อ> 8081:3000` … ใน k8s-lab แล้ว `ssh -L` หรือ curl ใน k8s-lab) สั่งซื้อที่บูธ a แล้วดูบูธ b → **ออเดอร์ไม่ตรงกัน** (แต่ละบูธมี db ของตัวเอง) → ลบ Pod → เกิดใหม่ ชื่อ/IP ใหม่ ออเดอร์ของบูธนั้นหาย และ port-forward ที่ต่อไว้หลุด → scale 3→5→2 → แก้ template (image เป็น `som-shop-web:1.1-promo` ที่ได้จาก `docker tag som-shop-web:1.1 som-shop-web:1.1-promo` + `kind load`, และ `SHOP_EYEBROW="🎉 โปรบูธใหม่ · $(POD_NAME)"`) → Pod เดิมไม่เปลี่ยน (`kubectl get pods -o custom-columns=NAME:.metadata.name,IMAGE:.spec.containers[0].image`) → ลบ Pod ทีละตัวด้วยมือถึงจะได้แบบใหม่
  - ปิดบท (ปัญหาส่งต่อ): (1) แต่ละบูธมี db ของตัวเอง ข้อมูลไม่ตรงกัน (2) IP/ชื่อเปลี่ยนทุกครั้ง ต้อง port-forward ทีละ Pod ลูกค้าหาร้านไม่เจอ → **บท 006 Service** (3) เปลี่ยนรุ่นต้องลบ Pod เองทีละตัว → **บท 007 Deployment** (กล่าวถึง)
- **006 Service** — เปิด: บูธ 3 ตัวมีอยู่แต่ลูกค้าหาไม่เจอ IP เปลี่ยน → "ประภาคาร" ที่ชื่อและที่อยู่คงที่ ส่งลูกค้าไปบูธที่ไฟเขียว
  - LAB สุดท้าย "แยก web กับ db ครั้งแรก": ns `som-shop` (PSA warn restricted), โฟลเดอร์ `02_LAB/som-shop-v2/` (app สำเนาจาก 004 + แก้เป็น 1.2/1.3 ตามบทรวมหัวข้อ 3.3), `k8s/00-namespace.yaml`, `k8s/10-db.yaml` (**ReplicaSet** `som-db` replicas 1, postgres:17.11-alpine, emptyDir, readiness pg_isready + Service ClusterIP `som-db:5432`), `k8s/20-web.yaml` (**ReplicaSet** `som-web` replicas 3, `som-shop-web:1.2`, init `wait-for-db` (`pg_isready -h som-db`) + `db-seed` (advisory lock `pg_advisory_xact_lock(5005)`), readiness `/api/health`, liveness `/api/live`, env `DATABASE_URL=postgres://som:meow1234@som-db:5432/catshop` + Service NodePort `som-web` port 80 → targetPort 3000 nodePort **30080**), `hit.sh` (bash+curl ใน k8s-lab: `./hit.sh [URL=http://localhost:30080/api/whoami] [N=60] [DELAY=0.1]`, `-q` นับ ok/err)
  - ขั้น: เตรียม (30080 ว่าง) → build `som-shop-web:1.2` (และ 1.3 ไว้ใช้ท้าย LAB) + kind load → db → web → logs db-seed (`new: 6` ตัวเดียว ไม่มี init restart) → DNS som-db จากใน web → เปิด `http://localhost:30080` บนเครื่องนักศึกษา (ป้ายเวอร์ชัน 1.2 + "เสิร์ฟโดย Pod") → hit.sh เห็นทุก replica → สั่งซื้อ ออเดอร์รวมที่ db เดียว (**แก้ปัญหาบท 005**) → scale RS web 3→5 EndpointSlice 5 IP → ลบ Pod web ระหว่าง hit.sh → ลบ Pod db → RS สร้างใหม่ IP ใหม่ แต่ชื่อ som-db เดิมใช้ได้ (ClusterIP เดิม) → ตารางหาย หน้า 503 "ร้านกำลังเตรียมสินค้า" → เติมสินค้าใหม่ด้วยการลบ Pod web (initContainer รันใหม่ — ยังไม่รู้ rollout restart) → ออเดอร์ = 0 (ปูทาง PVC) → อยากอัปเดตเป็น 1.3: `kubectl set image rs/som-web web=som-shop-web:1.3 db-seed=som-shop-web:1.3` → ไม่มีอะไรเปลี่ยน → ลบ Pod ทีละตัวด้วยมือระหว่าง hit.sh (เห็น 1.2/1.3 ปน, อาจมี err) / ลบทีเดียว `kubectl delete pod -l app=som-web` → ร้านสะดุด (err หลายครั้ง/ช่วง endpoints ว่าง) → ปิดบท: "ต้องมีผู้จัดการที่เปลี่ยนรุ่นทีละบูธ รอไฟเขียว และย้อนรุ่นได้" → **บท 007 Deployment**; เก็บกวาด `kubectl delete ns som-shop` (บท 007 สร้างสภาพนี้ใหม่จากไฟล์เอง)
  - 1.2/1.3 ตามบทรวมหัวข้อ 3.3 (build-arg APP_VERSION/APP_THEME, `/api/whoami` ตอบ `<pod> <version>`, `/api/live`, หน้า 503 เป็นมิตร, advisory lock, 1.3 ธีม sunset + แบนเนอร์เมนูใหม่ ไม่แก้ schema) — footer ใน 1.2 เปลี่ยนเป็น `Kubernetes LAB 006`
- **007 Deployment** — เปิด: ร้านสะดุดตอนเปลี่ยนรุ่นด้วยมือ (บท 006) → "ผู้จัดการร้าน" ที่สั่งหัวหน้ากะรุ่นใหม่/รุ่นเก่า เปลี่ยนป้ายทีละบูธ และพลิกสมุดย้อนรุ่นได้
  - LAB สุดท้าย "ร้านน้องส้มแบบโปรดักชันจริง": โฟลเดอร์ `02_LAB/som-shop-v3/` มี `k8s-rs/` (สำเนา manifest ReplicaSet + Service จากบท 006 — จุดเริ่ม), `k8s/10-db.yaml` (Deployment `som-db` replicas 1 **strategy Recreate** + Service som-db เดิม), `k8s/20-web.yaml` (Deployment `som-web` replicas 3, `revisionHistoryLimit: 5`, `progressDeadlineSeconds: 60`, `minReadySeconds: 3`, rollingUpdate maxSurge 1 / maxUnavailable 0, `preStop.sleep.seconds: 5`, `terminationGracePeriodSeconds: 30` + Service NodePort 30080 เดิม), `hit.sh` (สำเนาจาก 006); ใช้ image 1.2/1.3 ของบท 006 (ถ้าคลัสเตอร์ใหม่ให้ build จากโฟลเดอร์บท 006); 1.4 ไม่มีจริง
  - ขั้น: สร้างสภาพบท 006 (apply `k8s-rs/`) → เปิดร้าน + hit.sh → แปลงเป็น Deployment (apply `k8s/` selector เดียวกัน) — **คาด**ว่า Deployment รับเลี้ยง RS เดิม (ownerReferences) แล้วแทน Pod เดิมด้วย rolling (ต้องยืนยัน; ทางสำรอง `kubectl delete rs som-web --cascade=orphan` แล้วลบ Pod เก่าหลัง Deployment พร้อม) และ db Recreate → ข้อมูล emptyDir หาย (เตือนก่อน) → rolling update 1.2→1.3 ระหว่าง hit.sh `-q` 300 → err=0 (pre-check #22: 0/300 สองรอบ) + annotate change-cause → rollout history → undo → set image 1.4 (+ annotate) → ErrImagePull/ImagePullBackOff, `exceeded its progress deadline` แต่ร้านยังขาย (hit.sh ok) → undo → scale 3→5 (ไม่เกิด revision) → `kubectl rollout restart deploy/som-web` (ใช้เติมสินค้าใหม่หลังลบ db ได้ ต่างจากบท 006 ที่ต้องลบ Pod เอง) → ลบ Pod db ข้อมูลหาย (ยังเป็นปัญหาเดิม) → ปิดบท: ปูทาง PVC/StatefulSet, ConfigMap/Secret, Ingress, HPA

## 3. การกระจายภาพจากบทรวม (ใช้ prompt เดิมได้ ต้องเปลี่ยนป้าย "บทที่ 5" ของบทใหม่ และตรวจว่าไม่อ้างสิ่งที่ยังไม่เรียน)

| บทรวม | ไปบท |
|---|---|
| T01 opening (แก้เป็นของบท 005), T02 legend (แยกเป็น legend ของแต่ละบท), T03–T04 controller/loop, T05–T12 ReplicaSet (T12 "why not directly" → ภาพปิด/ปูทางของ 005 หรือ 007 ตามเนื้อหา), L02 LAB1 RS, L03 LAB2 label trap | 005 |
| T27–T37 Service, T38 zero-downtime (ส่วน endpoint terminating → 006 ทฤษฎีสั้นได้, การทดลอง preStop → 007), L09 ClusterIP+DNS, L10 debug, L11–L12 NodePort/keep-alive, L14 cross-ns, L15–L22 + L26 ส่วนที่เป็น web/db + Service (ต้องแก้ Deployment → ReplicaSet ในภาพ/ป้าย) | 006 |
| T13–T26 Deployment + blue/green/canary, T38 zero-downtime, T39 decision table (แยก/ปรับ), T40 next chapter (ของ 007), L04–L08, L13, L23–L25, L27 | 007 |

ภาพเปิดบทและภาพสรุปบทต้องเป็นของแต่ละบท (ป้าย "บทที่ 5" / "บทที่ 6" / "บทที่ 7")

## 4. ข้อกำหนด images

- ทฤษฎี ≥ 32 ภาพ, LAB ≥ 18 ภาพ (ทุก LAB มีภาพเปิดอย่างน้อย 1 ภาพ, LAB สุดท้ายหลายภาพ ~8–10)
- เขียนเป็น `logs/<บท>/build_images.py` ที่ `import imgcommon` (sys.path ไดเรกทอรีเดียวกัน) → `imgcommon.configure("00X")` → `t(...)`/`l(...)` → `imgcommon.main()`; ใส่ `src=` ทุกภาพ ("T06 06-rs-self-healing.png", "T06 06-rs-self-healing.png (แก้)" หรือ "new") เพื่อเขียน README-split.md
- prompt รูปแบบเดิม: scene ภาษาอังกฤษละเอียด (ตำแหน่ง องค์ประกอบ ท่าทางน้องส้ม), labels ≤ 7 ป้ายต่อภาพ (สั้น), extra ระบุตำแหน่งของทุกป้าย + ป้ายซ้ำ + สิ่งที่เป็นสีล้วนไม่มีข้อความ; ของในภาพเป็นร้านอาหารแมว/ท่าเรือเท่านั้น; ห้ามวาดคำตามตัวอักษร (canary ≠ นก, headless ≠ คนไม่มีหัว, hash ≠ อาหาร, seed ≠ เมล็ดพืช → "เติมสินค้าเข้าชั้น", orphan ≠ เด็ก/สัตว์กำพร้า → บูธที่ไม่มีป้ายเจ้าของ, cascade ≠ น้ำตก, adopt → ติดป้ายเจ้าของ, quota ≠ เงิน → ป้ายจำกัดจำนวน); หุ่นยนต์ไม่เป็นแมว; คนเป็น silhouette ไม่มีหน้า; ตัวเลข/ข้อความเทคนิคต้องถูกต้องตาม precheck/kubectl จริง (ถ้าไม่แน่ใจ → `nt=True`)
- `needs_test=True` สำหรับภาพที่มีตัวเลข/ข้อความที่ต้องรอผลรัน LAB จริง (เวลา, จำนวน error, ข้อความ error ที่ยังไม่ยืนยัน, หน้าร้านจริง)
- ไฟล์ภาพ: `<บท>/01_Theory/images/NN-<slug>.png`, `<บท>/02_LAB/images/NN-<slug>.png` (NN เริ่ม 01; 00 = character มีอยู่แล้ว)

## 5. ส่งมอบต่อบท (logs/<บท>/)

1. `plan.md` รูปแบบเดียวกับบทรวม: 0 ภาพรวม/ข้อกำหนด/ผล pre-check ที่เกี่ยวข้อง (คัดลอกแถวจาก precheck.md พร้อมเลขข้อเดิม)/อุปมา/เรื่องเล่า, 1 สารบัญทฤษฎีละเอียด (ระบุภาพ Txx ต่อหัวข้อ), 2 โครงไฟล์ LAB + ตาราง LAB (LAB | ชื่อ | เป้าหมาย | ไฟล์ | คำสั่งหลัก | ผลที่ต้องเห็น | สิ่งที่ต้องยืนยันตอนทดสอบ), 3 LAB สุดท้าย (แนวคิด/สถาปัตยกรรม/ไฟล์ manifest/ขั้นตอน/ผลที่ต้องเห็น/จุดที่ต้องยืนยัน/screenshot ที่จะเก็บ), 4 งานถัดไป, 5 สรุป storyboard (+ รายการ needs_test)
2. `build_images.py` → `images.json`, `<บท>/01_Theory/images/imagegen-prompts.md`, `<บท>/02_LAB/images/imagegen-prompts.md`, `image-sources.tsv` (สร้างโดย imgcommon.main())
3. `README-split.md` สั้น: ตาราง id | ไฟล์ | มาจาก (บทรวม id+ไฟล์ / แก้ / ใหม่) + สรุปจำนวน
