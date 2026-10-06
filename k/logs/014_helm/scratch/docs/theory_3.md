## 12. dependencies (subchart)

<p align="center" id="fig-42">
  <img src="images/42-subcharts.png" alt="รูปที่ 42 subchart และ Chart.lock" width="900"><br>
  <em><b>รูปที่ 42</b> dependencies: ชุดใหญ่ใส่ชุดย่อยได้ (เช่น metrics-server) helm dependency update ดึงมาเก็บใน charts/ และล็อกเวอร์ชันใน Chart.lock</em>
</p>

chart หนึ่งพึ่ง chart อื่นได้โดยประกาศใน `Chart.yaml` ตัวอย่าง **umbrella chart** (กล่องใหญ่ที่ไม่มี template ของตัวเอง มีแต่กล่องย่อย) ใน LAB เสริม `02_LAB/labs/labx-extra/harbor-addons/Chart.yaml`

```yaml
# LAB เสริม: umbrella chart = กล่องแฟรนไชส์ที่มีกล่องย่อย (subchart) 2 กล่อง ไม่มี templates ของตัวเอง
apiVersion: v2
name: harbor-addons
description: ชุดอุปกรณ์เสริมของท่าเรือ — metrics-server + podinfo (เปิด/ปิดได้)
type: application
version: 0.1.0
dependencies:
  - name: metrics-server
    version: 3.14.0
    repository: https://kubernetes-sigs.github.io/metrics-server/
  - name: podinfo
    version: 6.15.0
    repository: oci://ghcr.io/stefanprodan/charts   # dependency จาก OCI registry ก็ได้
    condition: podinfo.enabled                      # ติดตั้งก็ต่อเมื่อ podinfo.enabled=true
```

ส่งค่าให้ subchart ด้วย **key ชื่อเดียวกับ subchart** ใน `values.yaml` ของ chart แม่

```yaml
# ส่งค่าให้ subchart ด้วย key ชื่อ subchart
metrics-server:
  args:
    - --kubelet-insecure-tls
podinfo:
  enabled: false
```

**ตารางที่ 11** field ของ dependency และคำสั่ง

| field / คำสั่ง | ความหมาย |
|---|---|
| `name`, `version`, `repository` | chart ไหน รุ่นไหน (ใช้ช่วงได้ เช่น `~3.14.0`) จาก repo ไหน (HTTP URL, `oci://`, หรือ `file://../path`) |
| `condition` | เปิด/ปิด subchart ด้วยค่า boolean ใน values (`podinfo.enabled`) |
| `tags` | เปิด/ปิดหลาย subchart พร้อมกันเป็นกลุ่ม |
| `alias` | ใช้ chart เดียวกันหลายครั้งในชื่อต่างกัน |
| `global:` ใน values | ค่าที่ chart แม่และทุก subchart อ่านได้ (`.Values.global.x`) |
| `helm dependency list` | ดูสถานะ (`missing` / `ok`) |
| `helm dependency update` | ดาวน์โหลด subchart ลง `charts/` และเขียน `Chart.lock` (ล็อกรุ่น + digest) |
| `helm dependency build` | ดึงตาม `Chart.lock` เดิม (ได้รุ่นเดิมเป๊ะ) |

ผลจริงใน LAB เสริม: ก่อน update ทั้งสองตัว `missing` หลัง `helm dependency update` มี `Chart.lock`, `charts/metrics-server-3.14.0.tgz`, `charts/podinfo-6.15.0.tgz` และสถานะ `ok` render แล้วได้ object ของ metrics-server 9 ตัว ถ้า `--set podinfo.enabled=true` จึงมี object จาก `harbor-addons/charts/podinfo` เพิ่ม 5 ตัว

**library chart** (`type: library`) คือ chart ที่มีแต่ `define` ให้ chart อื่น include ใช้ร่วมกัน (เช่น label มาตรฐานขององค์กร) ติดตั้งเองไม่ได้

> chart ที่มี subchart เยอะจะ debug ยากขึ้น (values ซ้อนหลายชั้น) และอัปเกรด subchart ทีละตัวไม่ได้ ระบบจริงหลายทีมจึงเลือกติดตั้ง add-on แยก release (แบบ LAB 10) แล้วใช้เครื่องมือ GitOps คุมลำดับแทน

## 13. repository: HTTP vs OCI และ Artifact Hub

### 13.1 แคตตาล็อก (HTTP) กับโกดัง (OCI)

<p align="center" id="fig-43">
  <img src="images/43-http-vs-oci.png" alt="รูปที่ 43 HTTP repository กับ OCI" width="900"><br>
  <em><b>รูปที่ 43</b> repository แบบ HTTP = แคตตาล็อก (index.yaml + ไฟล์ .tgz) ต้อง repo add; OCI = โกดัง (oci://) ดึงตรงได้เลย</em>
</p>

**ตารางที่ 12** repository สองแบบ

| | HTTP chart repository | OCI registry |
|---|---|---|
| ข้างใน | เว็บเซิร์ฟเวอร์ธรรมดาที่มี `index.yaml` (รายการทุก chart ทุกรุ่น) + ไฟล์ `.tgz` | registry แบบเดียวกับที่เก็บ container image (Docker Hub, GHCR, Harbor, `registry:2`) |
| เริ่มใช้ | `helm repo add traefik https://traefik.github.io/charts` แล้ว `helm repo update` | ไม่ต้อง add ใช้ URL `oci://...` ตรง ๆ |
| ค้นหา | `helm search repo traefik/traefik --versions` (ค้นใน index ที่ดาวน์โหลดไว้) | ไม่มี search ในตัว (ดูจากเว็บของ registry หรือ Artifact Hub) |
| ติดตั้ง | `helm install traefik traefik/traefik --version 41.6.1` | `helm install oci-som oci://localhost:5000/charts/som-shop --version 0.1.0` |
| เผยแพร่ | `helm package` + อัปโหลด `.tgz` + สร้าง `index.yaml` ใหม่ (`helm repo index`) | `helm package` + `helm push` |
| ยืนยันตัวตน | basic auth / ไม่มี | `helm registry login <host>` (Helm 4 รับแค่ชื่อโฮสต์) |
| อ้างอิงแบบล็อกเนื้อหา | ไม่มี | **digest** `oci://.../som-shop@sha256:...` |
| ตัวอย่างในบทนี้ | podinfo, traefik, metrics-server | `registry:2` ใน k8s-lab (LAB 11), `oci://ghcr.io/stefanprodan/charts` (LAB เสริม) |

ผลจริงจาก LAB 1 (เลือกรุ่นแล้ว **pin** ไว้ทุกคำสั่ง)

```text
helm search repo traefik/traefik --versions | head -5
NAME                	CHART VERSION	APP VERSION	DESCRIPTION
traefik/traefik     	41.6.1       	v3.7.13    	A Traefik based Kubernetes ingress controller
traefik/traefik     	41.6.0       	v3.7.13    	A Traefik based Kubernetes ingress controller
traefik/traefik     	41.5.0       	v3.7.13    	A Traefik based Kubernetes ingress controller
traefik/traefik     	41.4.0       	v3.7.12    	A Traefik based Kubernetes ingress controller
```

เราเลือก **`traefik/traefik` 41.6.1** (app v3.7.13 ตรงกับบท 012–013) และ **`metrics-server/metrics-server` 3.14.0** (app 0.9.0 ตรงกับบท 013) สังเกตว่า **CHART VERSION กับ APP VERSION เป็นคนละเลข** (หัวข้อ 4.2) chart 3 รุ่นติดกันใช้ Traefik รุ่นเดียวกัน

ผลจริงจาก LAB 11 (OCI)

```text
helm push som-shop-0.1.0.tgz oci://localhost:5000/charts --plain-http
Pushed: localhost:5000/charts/som-shop:0.1.0
Digest: sha256:ef59e9e33853a9e4af39916e648d7dca165471037781ab5c07e8934d6fcfda22
```

`--plain-http` ใช้เฉพาะ registry ใน LAB ที่ไม่มี TLS registry จริงต้องเป็น HTTPS ข้อมูล login ของ `helm registry login` เก็บที่ `~/.config/helm/registry/config.json` เป็น **base64 ของ `user:password`** (ผลจริง `{'localhost:5000': {'auth': 'c29tOm...'}}`) ไม่ใช่การเข้ารหัส (เหมือน Secret ในบทที่ 11) ควร logout บนเครื่องที่ใช้ร่วมกัน

### 13.2 Artifact Hub: ที่ค้นแคตตาล็อก

<p align="center" id="fig-44">
  <img src="images/44-artifact-hub.png" alt="รูปที่ 44 Artifact Hub" width="900"><br>
  <em><b>รูปที่ 44</b> Artifact Hub = ที่ค้นชุดแฟรนไชส์จากหลายผู้เผยแพร่ — ชื่อเดียวกันไม่ได้แปลว่าเป็นของทางการ ดูป้ายผู้เผยแพร่ที่ยืนยันแล้ว</em>
</p>

[Artifact Hub](https://artifacthub.io/) (โครงการของ CNCF) รวบรวมรายการ chart จาก repository จำนวนมาก ค้นจากเว็บหรือ `helm search hub` ผลจริงจาก LAB 1

```text
helm search hub traefik --max-col-width 50 | head -8
URL                                               	CHART VERSION              	APP VERSION	DESCRIPTION
https://artifacthub.io/packages/helm/traefik/tr...	41.6.1                     	v3.7.13    	A Traefik based Kubernetes ingress controller
https://artifacthub.io/packages/helm/quench-tra...	0.0.21                     	3.7.13     	Cloud-native reverse proxy and load balancer wi...
https://artifacthub.io/packages/helm/aigisuk/tr...	0.1.1                      	2.7.0-rc2  	Latest release candidate of the Traefik based K...
https://artifacthub.io/packages/helm/kubeblocks...	41.6.0                     	v3.7.13    	A Traefik based Kubernetes ingress controller
https://artifacthub.io/packages/helm/k3s/traefik  	41.4.2+up41.4.0            	v3.7.12    	A Traefik based Kubernetes ingress controller
...
```

มี chart ชื่อ `traefik` จากหลายผู้เผยแพร่ บางตัวเป็นสำเนาของ chart ทางการ (kubeblocks, k3s) บางตัวเป็นรุ่นเก่ามาก (`2.7.0-rc2`) วิธีเลือก

1. ดูป้าย **Verified Publisher** (ผู้เผยแพร่ยืนยันเจ้าของ repo แล้ว) และ **Official** (เป็นของเจ้าของโปรเจกต์)
2. ดู repository URL ว่าเป็นของเจ้าของโปรเจกต์ (`traefik.github.io/charts`, `kubernetes-sigs.github.io/metrics-server`)
3. ดูวันที่ออกรุ่น จำนวนรุ่น และหน้า Security Report (ช่องโหว่ใน image ที่ chart ใช้)
4. อ่าน `helm show chart/values/readme` ก่อนติดตั้งเสมอ

### 13.3 chart กับ image: คนละคนดึง

<p align="center" id="fig-45">
  <img src="images/45-chart-vs-image-registry.png" alt="รูปที่ 45 chart กับ image คนละคนดึง" width="900"><br>
  <em><b>รูปที่ 45</b> คนละคนดึง: helm บนเครื่องเราดึง chart (registry login) / kubelet บน Node ดึง image (imagePullSecrets บท 011)</em>
</p>

จุดที่สับสนบ่อย: chart อยู่ใน OCI registry ได้เหมือน image แต่ **ผู้ดึงเป็นคนละตัว**

| | chart | container image |
|---|---|---|
| ใครดึง | **helm บนเครื่องที่สั่งคำสั่ง** (k8s-lab) | **kubelet / containerd บน Node** |
| ยืนยันตัวตนด้วย | `helm registry login` (ไฟล์ในเครื่องเรา) | `imagePullSecrets` ใน Pod/ServiceAccount (บทที่ 11) |
| ตัวอย่างในบทนี้ | `localhost:5000` ใน k8s-lab → ดึงได้เพราะ helm รันใน k8s-lab | Node ของ kind **มองไม่เห็น** `localhost:5000` ของ k8s-lab (เป็น localhost ของ Node เอง) — LAB จึงไม่ push image เข้า registry นี้ |

เหตุนี้ install chart จาก OCI สำเร็จไม่ได้แปลว่า Pod จะดึง image ได้ ถ้า image อยู่ใน registry ส่วนตัวต้องตั้ง `imagePullSecrets` (chart ที่ดีมีช่องให้ใส่ใน values) และ Node ต้องมองเห็น registry นั้น

## 14. ความปลอดภัยและแหล่งที่มา

### 14.1 ก่อนติดตั้ง chart ใด ๆ

<p align="center" id="fig-46">
  <img src="images/46-security-checklist.png" alt="รูปที่ 46 เช็กลิสต์ความปลอดภัย" width="900"><br>
  <em><b>รูปที่ 46</b> ก่อนติดตั้ง chart: อ่าน values และ image ที่จะดึง, pin เวอร์ชัน (และ digest), ไม่ใส่รหัสจริงใน values ที่ commit, เลือกแหล่งของเจ้าของโปรเจกต์</em>
</p>

chart คือ "โค้ดที่จะสร้าง object ด้วยสิทธิ์ของเรา" ชุดที่ติดตั้ง ClusterRole หรือ Pod ที่มีสิทธิ์สูงจึงควรอ่านก่อนเหมือนอ่านโค้ด

```bash
helm show chart traefik/traefik --version 41.6.1          # ฉลาก: ใครทำ รุ่นอะไร
helm show values traefik/traefik --version 41.6.1 | less   # ค่าเริ่มต้นทั้งหมด
helm template traefik traefik/traefik --version 41.6.1 -f labs/lab10-addons/traefik-values.yaml \
  | grep -E "^kind:|image:"                                # จะสร้างอะไร และดึง image ไหน
```

เช็กลิสต์

1. **แหล่ง**: chart ของเจ้าของโปรเจกต์หรือ Verified Publisher (หัวข้อ 13.2)
2. **pin รุ่น**: ใส่ `--version` ทุกคำสั่ง (ไม่ใส่ = ได้รุ่นล่าสุด ณ วันนั้น ผลจึงเปลี่ยนตามวัน) ระบบสำคัญ pin ด้วย **digest** (`oci://...@sha256:...`) ซึ่งเปลี่ยนเนื้อหาไม่ได้แม้ผู้เผยแพร่จะ push tag เดิมทับ
3. **อ่าน image ที่จะถูกดึง** และ pin tag/digest ของ image ผ่าน values ถ้า chart เปิดให้ตั้ง
4. **ดูสิทธิ์**: ClusterRole, `privileged`, `hostNetwork`, ServiceAccount ที่ chart สร้าง
5. **ความลับ**: ไม่ใส่รหัสจริงใน values ที่ commit (หัวข้อ 10)
6. **provenance**: chart ที่เซ็นด้วย `helm package --sign` ตรวจได้ด้วย `helm verify` หรือ `--verify` ตอน install/pull
7. **plugin**: Helm 4 ตรวจที่มาของ plugin แหล่งที่ไม่ได้เซ็นต้องใส่ `--verify=false` เอง (LAB เสริม: `Error: plugin source does not support verification. Use --verify=false to skip verification`) ใช้เฉพาะ plugin ที่เชื่อถือได้และ pin `--version` (helm-diff ต้องเป็น v3.15.15 ขึ้นไปถึงใช้กับ Helm 4 ได้ — รุ่น v3.13.1 ใช้ไม่ได้)
8. ค่าที่ลดความปลอดภัยใน LAB นี้ (`api.insecure: true` ของ Traefik dashboard, `--kubelet-insecure-tls` ของ metrics-server, `--plain-http` ของ registry) **ใช้เฉพาะ LAB**

### 14.2 บทเรียนปี 2568: แคตตาล็อกดังก็หายได้

<p align="center" id="fig-47">
  <img src="images/47-catalog-can-vanish.png" alt="รูปที่ 47 แคตตาล็อกหายได้" width="900"><br>
  <em><b>รูปที่ 47</b> บทเรียนปี 2568: แคตตาล็อกดังเปลี่ยนเงื่อนไข image รุ่นเก่าถูกย้าย/หยุดอัปเดต → pin เวอร์ชัน และเก็บสำเนาในโกดังของเราเอง</em>
</p>

**Bitnami** เคยเป็นแคตตาล็อก chart ที่นิยมที่สุดแห่งหนึ่ง (PostgreSQL, Redis, WordPress, ...) และ chart เหล่านั้นใช้ image `docker.io/bitnami/*` ตามประกาศของ Bitnami ([bitnami/charts#35164](https://github.com/bitnami/charts/issues/35164)) **ตั้งแต่ 28 สิงหาคม 2568 (2025)** Bitnami หยุดเผยแพร่ image/chart รุ่นที่มีเลขเวอร์ชันแบบฟรีใน `docker.io/bitnami` ย้ายของเดิมไปไว้ที่ `docker.io/bitnamilegacy` (ไม่อัปเดตและไม่ซัพพอร์ตต่อ) มีช่วง "brownout" ที่ image ดึงไม่ได้ชั่วคราวหลายรอบก่อนถึงวันจริง และชุดฟรีที่เหลือ (`bitnamisecure`) มีให้แค่ tag `latest`

ผลคือระบบที่ `helm install bitnami/postgresql` ไว้โดยไม่ได้คิด เจอปัญหา Pod ดึง image ไม่ได้เมื่อ Node ใหม่เกิด หรือต้องรีบย้าย image ไป `bitnamilegacy` ที่ไม่มี security fix บทเรียนที่ใช้ได้กับทุกแหล่ง

1. **pin chart และ image** ทั้งเวอร์ชันและ digest
2. **เลือก chart ของเจ้าของโปรเจกต์** (บทนี้ใช้ Traefik จาก Traefik Labs, metrics-server จาก kubernetes-sigs)
3. **เก็บสำเนาในโกดังขององค์กร** (OCI registry ของเราเอง เช่น Harbor — LAB 11 ทำแบบเล็ก) ทั้ง chart และ image
4. **อ่านว่า chart ดึง image จากที่ไหน** (`helm template | grep image:`) ไม่ใช่ดูแค่ชื่อ chart
5. ติดตามประกาศของแหล่งที่ใช้ และมีแผนย้ายเมื่อเงื่อนไขเปลี่ยน

บทนี้ **ไม่ใช้ Bitnami** ฐานข้อมูลในชุดร้านใช้ image ทางการ `postgres:17.11-alpine` ใน chart ที่เราเขียนเอง

## 15. Helm vs Kustomize vs static manifest

<p align="center" id="fig-48">
  <img src="images/48-helm-kustomize-static.png" alt="รูปที่ 48 static / Kustomize / Helm" width="900"><br>
  <em><b>รูปที่ 48</b> เทียบ 3 แบบ: static manifest (แผ่นเดียวตายตัว), Kustomize (แผ่นใสซ้อนบนพิมพ์เขียว), Helm (ชุดแฟรนไชส์ + รุ่น + rollback)</em>
</p>

**Kustomize** (มีใน kubectl: `kubectl apply -k`, บทที่ 10 ใช้ `configMapGenerator`) แก้ปัญหาค่าต่างระหว่าง environment ด้วย **overlay**: มีโฟลเดอร์ `base/` เป็น YAML ปกติ แล้ว `overlays/dev/` ใส่ patch ทับบางส่วน ไม่มี template ไม่มีตัวแปร

**ตารางที่ 13** เทียบ 3 แนวทาง

| เรื่อง | static manifest (`kubectl apply -f`) | Kustomize (`kubectl apply -k`) | Helm |
|---|---|---|---|
| วิธีทำให้ต่างกันต่อ environment | copy ไฟล์ | base + overlay/patch | template + values |
| ไฟล์ที่อ่าน | YAML ล้วน | YAML ล้วน (อ่านง่าย) | YAML ปน `{{ }}` (อ่านยากกว่า) |
| เงื่อนไข/วนซ้ำ | ไม่ได้ | จำกัด (ผ่าน patch/component) | ได้เต็มที่ (`if`, `range`) |
| รุ่นของทั้งชุด + rollback | ไม่มี | ไม่มี (พึ่ง git) | **มี** revision + `helm rollback` |
| ลบของที่เอาออกจากชุด | ไม่ (ต้อง prune เอง) | ไม่ (ต้อง prune เอง) | ใช่ |
| hook / test | ไม่มี | ไม่มี | มี |
| แจกจ่ายให้คนอื่น | ส่งไฟล์ | ส่งโฟลเดอร์/อ้าง git URL | **แพ็กเกจ** `.tgz` ใน repo/OCI + Artifact Hub |
| debug | ง่ายสุด | ง่าย (`kubectl kustomize` ดูผล) | ต้อง `helm template --debug` |
| เหมาะกับ | แอปเล็ก ไม่กี่ไฟล์ | แอปของทีมเองที่ต่างกันเล็กน้อยต่อ environment | ซอฟต์แวร์ที่แจกให้หลายคนติดตั้ง (Traefik, metrics-server), แอปที่ต้องการ lifecycle |

ใช้ร่วมกันได้: `helm template ... | kubectl apply -k` แบบส่งผลไปให้ Kustomize patch ต่อ หรือใช้ **post-renderer** (Helm 4 ต้องเป็น plugin) ให้ Helm ส่ง manifest ไปผ่าน Kustomize ก่อน apply เหมาะกับการ "ปรับ chart ของคนอื่นเล็กน้อย" โดยไม่ fork chart

## 16. ปูทาง GitOps และ operator

### 16.1 GitOps: ให้หุ่นยนต์เฝ้าแฟ้มแผนร้าน

<p align="center" id="fig-49">
  <img src="images/49-gitops-preview.png" alt="รูปที่ 49 ปูทาง GitOps" width="900"><br>
  <em><b>รูปที่ 49</b> GitOps (ตัวอย่าง Argo CD/Flux): เก็บ chart + ใบสั่งไว้ใน Git แล้วหุ่นยนต์เฝ้าแฟ้มทำให้สาขาตรงกับแผนเสมอ ไม่ต้องสั่ง helm upgrade เอง</em>
</p>

ในบทนี้เราเป็นคนพิมพ์ `helm upgrade` เองทุกครั้ง ถ้ามีคนแก้ร้านด้วย `kubectl edit` (drift) ก็ไม่มีใครรู้ **GitOps** กลับทิศ: เก็บ "ร้านที่ควรเป็น" (chart + ใบสั่ง) ไว้ใน **Git เป็นแหล่งความจริง** แล้วให้ controller ในคลัสเตอร์คอยดึงและทำให้คลัสเตอร์ตรงกับ Git เสมอ อยากอัปเกรด = เปิด Pull Request แก้ `web.image.tag` แล้ว merge (มีคนรีวิว มีประวัติใน git) ย้อนรุ่น = `git revert`

ตัวอย่างแนวคิด (ยังไม่ได้ใช้ใน LAB ของบทนี้ — เป็นบทถัดไป) chart เดียวกับที่เราเขียน ถูกอ่านโดยเครื่องมือ GitOps 2 ตัวที่นิยม

```yaml
# Argo CD: Application ที่ชี้ chart ในโฟลเดอร์ของ git + ใบสั่ง prod
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: som-shop-prod
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/example/som-shop-gitops.git
    targetRevision: main
    path: charts/som-shop
    helm:
      valueFiles:
        - ../values-prod.yaml
  destination:
    server: https://kubernetes.default.svc
    namespace: som-shop
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

```yaml
# Flux: HelmRelease ที่ดึง chart จาก OCI registry ขององค์กร
apiVersion: source.toolkit.fluxcd.io/v1
kind: HelmRepository
metadata:
  name: som-charts
  namespace: som-shop
spec:
  type: oci
  url: oci://registry.example.com/charts
  interval: 10m
---
apiVersion: helm.toolkit.fluxcd.io/v2
kind: HelmRelease
metadata:
  name: som
  namespace: som-shop
spec:
  interval: 10m
  chart:
    spec:
      chart: som-shop
      version: 0.1.0
      sourceRef:
        kind: HelmRepository
        name: som-charts
  values:
    hpa:
      enabled: true
    ingress:
      enabled: true
      host: shop.localhost
      tls: true
```

ข้อต่างที่ควรรู้: Argo CD **render chart ด้วยวิธีแบบ `helm template`** แล้ว apply เอง (ไม่มี release Secret ของ Helm และ `lookup` ได้ค่าว่าง — chart ที่พึ่ง `lookup` แบบ som-shop ต้องปรับ เช่น ให้รหัสมาจาก External Secrets แทน) ส่วน Flux helm-controller ใช้ Helm SDK ติดตั้งเป็น release จริง (มี history, hook และ `lookup` ทำงาน) ทั้งสองแบบ **ไม่ต้องให้คนพิมพ์ `helm upgrade`** และแก้ drift กลับเอง (`selfHeal`)

### 16.2 operator: หุ่นยนต์ที่ดูแลร้านต่อทุกวัน

<p align="center" id="fig-50">
  <img src="images/50-operator-preview.png" alt="รูปที่ 50 ปูทาง operator" width="900"><br>
  <em><b>รูปที่ 50</b> Helm ติดตั้งจบแล้วไม่ดูแลต่อ — operator คือหุ่นยนต์ที่ดูแลร้านต่อทุกวัน (สำรองข้อมูล ซ่อม อัปเกรดฐานข้อมูล) บทถัดไป</em>
</p>

Helm ทำงาน **ตอนเราสั่ง** แล้วจบ หลังติดตั้งเสร็จ ถ้า `som-db-0` ข้อมูลเสีย ต้องสำรองข้อมูลทุกคืน หรือต้องอัปเกรด PostgreSQL 17 → 18 (ต้อง dump/restore) Helm ไม่รู้เรื่องเหล่านี้ **operator** คือ controller เฉพาะทาง (custom controller + CRD) ที่รันอยู่ในคลัสเตอร์ตลอดและรู้ "วิธีดูแล" แอปนั้น เช่น เราเขียน `kind: PostgresCluster` (custom resource) แล้ว operator สร้าง StatefulSet, ตั้ง replication, สำรองข้อมูลตามตาราง และสลับ primary เมื่อพัง — เหมือนจ้างผู้จัดการครัวที่รู้งานครัวจริง ไม่ใช่แค่ผู้รับเหมาที่สร้างครัวแล้วกลับบ้าน

ความสัมพันธ์ที่พบบ่อย: **ใช้ Helm ติดตั้ง operator** (operator ส่วนใหญ่แจกเป็น chart) แล้วให้ operator ดูแลแอป

## 17. ตารางคำสั่งที่ใช้บ่อย

<p align="center" id="fig-51">
  <img src="images/51-command-cheatsheet.png" alt="รูปที่ 51 คำสั่งที่ใช้บ่อย" width="900"><br>
  <em><b>รูปที่ 51</b> คำสั่งที่ใช้บ่อยของ Helm 4 จัดเป็นกลุ่ม: ติดตั้ง/อัปเกรด, ดูสถานะ, ดูข้อมูลสาขา, ย้อนรุ่น, render/ตรวจ</em>
</p>

**ตารางที่ 14** คำสั่ง Helm 4 ที่ใช้ในบทนี้ (ทดสอบแล้วทุกคำสั่งกับ v4.3.0)

| กลุ่ม | คำสั่ง | ใช้ทำอะไร |
|---|---|---|
| ข้อมูล | `helm version`, `helm env` | รุ่น, ที่เก็บ cache/config, `HELM_MAX_HISTORY` |
| แคตตาล็อก | `helm repo add <name> <url>`, `helm repo update`, `helm repo list` | จัดการ HTTP repository |
| | `helm search repo <repo/chart> --versions`, `helm search hub <คำ>` | ค้นรุ่นใน repo ที่ add / ค้นใน Artifact Hub |
| | `helm show chart\|values\|readme <chart> --version X` | อ่านก่อนติดตั้ง |
| | `helm pull <chart> --version X --untar [-d dir]` | ดาวน์โหลดมาดูข้างใน (`-d` ต้องมีโฟลเดอร์อยู่ก่อน) |
| ติดตั้ง/อัปเกรด | `helm install <rel> <chart> -n <ns> --create-namespace -f v.yaml --set k=v --wait` | ติดตั้งครั้งแรก |
| | `helm upgrade <rel> <chart> -n <ns> -f v.yaml --wait [--rollback-on-failure --timeout 5m]` | อัปเกรด (ส่ง `-f` ทุกครั้ง) |
| | `helm upgrade --install ...` | ติดตั้งหรืออัปเกรด (CI) |
| | `--reuse-values`, `--reset-then-reuse-values` | ใช้ค่าของ revision ก่อน |
| | `--take-ownership --force-conflicts` | รับ object เดิมเข้า release |
| ดูสถานะ | `helm list [-A] [--failed\|--uninstalled]`, `helm status <rel>`, `helm history <rel>` | release ทั้งหมด / สถานะ / สมุด |
| ดูข้อมูลสาขา | `helm get values [--all] [--revision N]`, `helm get manifest`, `helm get notes`, `helm get hooks`, `helm get metadata` | ใบสั่ง / พิมพ์เขียว / การ์ด / hook / วิธี apply |
| ย้อนรุ่น/ถอน | `helm rollback <rel> <rev> --wait` | ย้อน (ระบุเลขเสมอ) |
| | `helm uninstall <rel> [--keep-history]` | ถอน |
| ตรวจ | `helm test <rel> --logs` | ตรวจรับร้าน |
| render/debug | `helm lint <chart> [-f v.yaml]`, `helm template <rel> <chart> [--show-only templates/x.yaml] [--debug]` | ตรวจ/ดูผล render |
| | `helm install ... --dry-run=client\|server` | ซ้อมติดตั้ง (server ไม่ตรวจ field — ใช้ `helm template \| kubectl apply --dry-run=server -f -` เพิ่ม) |
| สร้าง/แพ็ก | `helm create <name>`, `helm package <dir>` | โครง chart / ได้ `.tgz` |
| OCI | `helm registry login <host> -u <user> --password-stdin`, `helm push <tgz> oci://<host>/<path>`, `helm registry logout <host>` | โกดัง |
| dependency | `helm dependency list\|update\|build <chart>` | subchart |
| plugin | `helm plugin install <url> --version X [--verify=false]`, `helm plugin list`, `helm plugin uninstall <name>` | ส่วนเสริม (เช่น helm-diff) |

**ตารางที่ 15** flag ของ Helm 3 → Helm 4

| Helm 3 | Helm 4 | หมายเหตุ |
|---|---|---|
| `--atomic` | `--rollback-on-failure` | ตัวเก่ายังรับแต่ขึ้นคำเตือน deprecated |
| `--force` | `--force-replace` | ลบแล้วสร้างใหม่ |
| (ไม่มี / client-side) | `--server-side=true\|false\|auto`, `--force-conflicts` | SSA |
| `--wait` (bool) | `--wait[=watcher\|hookOnly\|legacy]` | ไม่ใส่ = `hookOnly` |
| `--dry-run` | `--dry-run=client\|server\|none` | ต้องระบุค่า |
| `helm list -a` | `helm list` (แสดงทุกสถานะ) + ตัวกรอง `--deployed`, `--failed`, `--uninstalled`, ... | `-a` ถูกเอาออก |
| `helm registry login https://host` | `helm registry login host` | รับแค่ชื่อโฮสต์ |
| post-renderer เป็นไฟล์ที่รันได้ | post-renderer ต้องเป็น plugin | |
| `helm plugin install <git>` | `helm plugin install <git> --verify=false` (แหล่งที่ไม่ได้เซ็น) | ตรวจที่มา |

## 18. สรุปบท

<p align="center" id="fig-52">
  <img src="images/52-chapter-summary.png" alt="รูปที่ 52 สรุปบท" width="900"><br>
  <em><b>รูปที่ 52</b> สรุปบท: ชุดแฟรนไชส์ (chart) + ใบสั่ง (values) → ร้านสาขา (release) ที่มีสมุดบันทึก (revision) ติดตั้ง/อัปเกรด/ย้อน/ถอนได้ทั้งร้าน</em>
</p>

**ตารางที่ 16** ปัญหาต้นบทกับสิ่งที่ Helm ให้

| ปัญหาของ YAML ล้วน | Helm แก้ด้วย | ผลจริงใน LAB |
|---|---|---|
| ค่าซ้ำหลายไฟล์ | template + `_helpers.tpl` | ชื่อ/label/image มาจากตรายางเดียว |
| copy โฟลเดอร์แล้ว drift | chart เดียว + ใบสั่งต่อ environment | dev 10 object / prod 13 object จาก chart เดียว |
| ไม่มีรุ่นของทั้งชุด | revision + `helm rollback` | `Rollback to 2` ระหว่างลูกค้าเข้า `ok=300 err=0` |
| ติดตั้งหลายขั้นตามลำดับ | `helm install` ครั้งเดียว + hook | สาขา dev ทั้งร้าน 18.0 วินาที + seed + test ผ่าน |
| ลบไม่หมด | `helm uninstall` | ลบทุก object (ยกเว้น PVC ตามที่ออกแบบ) |
| ใช้ของจากภายนอก | repository/OCI + pin รุ่น | Traefik 41.6.1, metrics-server 3.14.0 จาก chart ทางการ |

### ข้อควรจำของบทนี้

1. **ใส่ `--wait` ทุกครั้ง** — Helm 4 ไม่ใส่ = `deployed` ทั้งที่ Pod `ErrImagePull`
2. **ส่ง `-f` ใบสั่งทุกครั้งที่ upgrade** — ส่งแค่ `--set` บางค่า = ค่าอื่นกลับค่าเริ่มต้น (ไม่ส่งอะไรเลย = ใช้ค่าเดิม)
3. **rollback ระบุเลขเสมอ** — ไม่ระบุ = ถอยไปรุ่นก่อนหน้าแม้เป็นรุ่นที่ล้ม และ rollback เขียน revision ใหม่เสมอ
4. **`--dry-run=server` ไม่ตรวจ field ผิด** — ใช้ `helm template | kubectl apply --dry-run=server -f -` เพิ่ม
5. **release Secret อ่านได้** — รหัส (และ `tls.key`) อยู่ในนั้น ควบคุมสิทธิ์อ่าน Secret และไม่ commit รหัสใน values
6. **รับของเดิม = `--take-ownership --force-conflicts`** ได้เมื่อ selector ตรงกัน ถ้า selector ต่างต้องลบแล้วติดตั้งใหม่ และ **ห้าม uninstall release ที่ adopt ล้ม**
7. **PVC ไม่ถูกลบ** ติดตั้งใหม่ต้องใช้รหัสเดิม
8. **pin chart และ image** อ่าน values ก่อนติดตั้ง และมีสำเนาในโกดังของตัวเอง

