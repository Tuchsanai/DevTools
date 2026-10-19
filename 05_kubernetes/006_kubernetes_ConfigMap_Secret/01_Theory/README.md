# บทที่ 6: Kubernetes ConfigMap และ Secret — เปลี่ยนป้ายร้านโดยไม่ต้อง build ใหม่

> **รายวิชา:** Software Development Tools and Environments (DevTools) · **CLO-5, CLO-6**
> **บทก่อนหน้า:** [บทที่ 5 Kubernetes Service](../../005_kubernetes_Service/01_Theory/README.md) · **LAB ของบทนี้:** [02_LAB](../02_LAB/README.md)

อ่านบทนี้จบแล้วควรทำได้ 4 อย่าง

1. อธิบายได้ว่าทำไมต้องแยก **ค่าตั้งค่า** ออกจาก image และ **ConfigMap** / **Secret** ต่างกันอย่างไร
2. **อ่านไฟล์ YAML ของ ConfigMap และ Secret ออกทุกบรรทัด** และบอกได้ว่า env ตัวไหนมาจากไหน ไฟล์ไหนถูก mount ไว้ที่ใด
3. เลือกส่งค่าเข้า Pod เป็น **env** หรือ **ไฟล์** ได้ถูก และรู้ว่าแก้ค่าแล้วแบบไหนเปลี่ยนเอง แบบไหนต้อง `kubectl rollout restart`
4. บอกได้ว่า Secret **ไม่ได้เข้ารหัส** และ ConfigMap / Secret ยังทำอะไร **ไม่ได้** (เก็บข้อมูลที่แอปเขียนให้รอดเมื่อได้ Pod ใหม่) ก่อนไปบทถัดไป

## สารบัญ

1. [เริ่มเรื่อง: เปลี่ยนป้ายร้านทีไร ต้อง build ใหม่](#1-เริ่มเรื่อง-เปลี่ยนป้ายร้านทีไร-ต้อง-build-ใหม่)
2. [ทำไมต้องแยกค่าตั้งค่าออกจาก image](#2-ทำไมต้องแยกค่าตั้งค่าออกจาก-image)
3. [ConfigMap คืออะไร และอ่าน YAML ทีละบรรทัด](#3-configmap-คืออะไร-และอ่าน-yaml-ทีละบรรทัด)
4. [ใช้ ConfigMap เป็น env: configMapKeyRef และ envFrom](#4-ใช้-configmap-เป็น-env-configmapkeyref-และ-envfrom)
5. [กับดัก: Pod มาก่อน ConfigMap](#5-กับดัก-pod-มาก่อน-configmap)
6. [แก้ ConfigMap แล้ว env ไม่เปลี่ยน](#6-แก้-configmap-แล้ว-env-ไม่เปลี่ยน)
7. [ใช้ ConfigMap เป็นไฟล์](#7-ใช้-configmap-เป็นไฟล์)
8. [env หรือไฟล์ เลือกแบบไหน](#8-env-หรือไฟล์-เลือกแบบไหน)
9. [Secret คืออะไร และ base64](#9-secret-คืออะไร-และ-base64)
10. [Secret ปลอดภัยแค่ไหน](#10-secret-ปลอดภัยแค่ไหน)
11. [kubectl rollout restart: เปลี่ยน Pod ใหม่ทั้งชุดโดยไม่แก้ YAML](#11-kubectl-rollout-restart-เปลี่ยน-pod-ใหม่ทั้งชุดโดยไม่แก้-yaml)
12. [อ่าน YAML ร้านน้องส้มทั้งไฟล์](#12-อ่าน-yaml-ร้านน้องส้มทั้งไฟล์)
13. [ปูทางบทถัดไป](#13-ปูทางบทถัดไป)
14. [สรุปและคำถามทบทวน](#14-สรุปและคำถามทบทวน)

---

## 1. เริ่มเรื่อง: เปลี่ยนป้ายร้านทีไร ต้อง build ใหม่

<p align="center">
  <img src="images/01-opening-rebuild-to-change-sign.png" alt="น้องส้มเหนื่อยกับการ build ตู้ใหม่ทุกครั้งที่เปลี่ยนป้าย และรหัสผ่านเขียนเปิดอยู่ใน YAML" width="800">
</p>

ในบทที่ 5 ร้านอาหารแมวน้องส้มมีที่อยู่เดียวแล้ว (`http://localhost:30080`) แต่ยังมีปัญหาที่ Service ช่วยไม่ได้ ([บทที่ 5 หัวข้อ 13](../../005_kubernetes_Service/01_Theory/README.md#13-ปูทางบทถัดไป))

- **ค่าตั้งค่าเขียนอยู่ใน YAML ของ Deployment** เช่น ชื่อร้าน แก้ทีต้องแก้ไฟล์ Deployment
- **ค่าบางอย่างฝังใน image ตอน build** เช่น `APP_VERSION` ที่ส่งด้วย `--build-arg` จะเปลี่ยนต้อง build image ใหม่
- **รหัสผ่านเขียนเปิดอยู่ใน YAML** เช่น `postgres://som:meow1234@...` ของร้านน้องส้มใน[บทที่ 2 หัวข้อ 7.2](../../002_kubernetes_pod/01_Theory/README.md#72-env-ส่งค่าเข้า-container) ใครเปิดไฟล์ก็เห็น

> "แค่จะเปลี่ยนป้ายประกาศหน้าร้าน ทำไมต้องสร้างตู้ใหม่ทั้งตู้ ส้มควรมี **แฟ้มคู่มือร้าน** ไว้ที่หอบังคับการ แก้ในแฟ้มแล้วทุกสาขาอ่านจากแฟ้มนั้น ส่วนรหัสผ่านก็ใส่ **ซองปิดผนึก** แยกไว้" — กัปตันบอก

ทบทวนอุปมาท่าเรือ แล้วเพิ่มตัวละครใหม่ 2 ตัว

<p align="center">
  <img src="images/02-harbor-metaphor-config.png" alt="อุปมาท่าเรือพร้อมตัวละครใหม่ ConfigMap แฟ้มคู่มือสีฟ้า และ Secret ซองปิดผนึกตราแดง" width="800">
</p>

- **container** = ตู้สินค้า / **Pod** = กล่องโปร่งห่อตู้ มีป้าย IP 1 อัน
- **Node** = เรือ (`lab-worker`, `lab-worker2`) / **Control Plane** = หอบังคับการ
- **ReplicaSet** = หัวหน้าลูกเรือ / **Deployment** = ผู้จัดการลูกเรือถือสมุดรุ่น (บทที่ 3–4)
- **Service** = พนักงานต้อนรับเสื้อกั๊กส้มที่บูธ / **NodePort** = ประตูท่าเรือ `30080` (บทที่ 5)
- **ConfigMap** = **แฟ้มคู่มือร้านสีฟ้า** วางบนชั้นที่หอบังคับการ ข้างในเป็นแผ่น `key: value` ถ่ายสำเนาส่งเข้ากล่องได้ 2 แบบ: **แผ่นโน้ตแปะในตู้ตอนเปิดกล่อง** (env ไม่เปลี่ยนจนกว่าจะเปิดกล่องใหม่) หรือ **กระดานแขวนในกล่อง** (ไฟล์ ที่คนเดินเอกสารจากหอบังคับการคอยเปลี่ยนแผ่นใหม่ให้เอง)
- **Secret** = **ซองปิดผนึกตราแดง** ข้างในเป็นรหัสผ่าน แต่แค่ **พับซอง** (base64) ไม่ได้ล็อกกุญแจ ใครเปิดซองก็อ่านได้

> **ขอบเขตบทนี้:** ConfigMap และ Secret แบบ **env** และแบบ **ไฟล์** กับ Pod / Deployment / Service จากบทก่อน ส่วนเครื่องมือเก็บรหัสภายนอก (external secret manager) และการเข้ารหัส Secret ในฐานข้อมูลของคลัสเตอร์ (encryption at rest) เป็นงานของผู้ดูแลคลัสเตอร์ ไม่อยู่ในบทนี้

---

## 2. ทำไมต้องแยกค่าตั้งค่าออกจาก image

<p align="center">
  <img src="images/03-why-separate-config.png" alt="พิมพ์เขียว som-menu:1.0 ใบเดียวสร้างตู้เหมือนกันทุกใบ แฟ้ม ConfigMap และซอง Secret ส่งค่าเข้ากล่อง เครื่อง docker build ปิดพัก" width="800">
</p>

แนวคิดหลักของบทนี้: **image เดียว ใช้ได้ทุกที่ ค่าที่ต่างกันส่งเข้าไปตอนรัน**

- **image** = โค้ด + สิ่งที่โปรแกรมต้องใช้ (เหมือนกันทุกร้าน ทุกสาขา ทุกเครื่อง)
- **ค่าตั้งค่า** = ชื่อร้าน ประกาศ เมนู รหัสผ่าน (ต่างกันได้ และเปลี่ยนบ่อย)
- ถ้าฝังค่าตั้งค่าไว้ใน image เปลี่ยนป้ายทีต้อง `docker build` → `kind load` → เปลี่ยนรุ่นใหม่ทุกครั้ง และรหัสผ่านก็ติดไปกับ image ทุกที่ที่ image ไปถึง

ร้านน้องส้มบทนี้ build image `som-menu:1.0` **ครั้งเดียว** ทั้ง LAB 4 หัวไฟล์ `02_LAB/som-menu/app/Dockerfile` เขียนไว้ว่า "image นี้ไม่มีชื่อร้าน ประกาศ เมนู หรือรหัสผ่านฝังอยู่" ค่าที่ฝังใน image เหลือแค่ค่าที่ไม่เคยเปลี่ยน (`ENV NODE_ENV=production`, `PORT=3000`) นอกนั้นมาจาก ConfigMap / Secret ตอนรันทั้งหมด

เทียบ 3 ที่ที่ค่าตั้งค่าอยู่ได้

| | ฝังใน image (`--build-arg`, `ENV`) | `env` เขียนตรงใน YAML (บทที่ 2–5) | ConfigMap / Secret (บทนี้) |
|---|---|---|---|
| เปลี่ยนค่าต้องทำอะไร | build image ใหม่ + เปลี่ยนรุ่น | แก้ YAML ของ Pod/Deployment ทุกไฟล์ที่ใช้ค่านั้น | แก้ ConfigMap ที่เดียว |
| ค่าเดียวกันใช้หลาย Pod | ต้องใช้ image เดียวกัน | เขียนซ้ำทุกไฟล์ | หลาย Pod อ้างชื่อเดียวกัน |
| ส่งเป็นไฟล์ได้ไหม | ได้ (COPY ตอน build) | ไม่ได้ | ได้ (หัวข้อ 7) อัปเดตเองด้วย |
| รหัสผ่าน | ติดไปกับ image | อยู่ในไฟล์ YAML เปิดอ่านได้ | แยกเป็น Secret คุมสิทธิ์แยกได้ (หัวข้อ 10) |

> **ประโยคเดียวที่ต้องจำ:** **build ครั้งเดียว ใช้ได้ทุกที่** ค่าที่เปลี่ยนบ่อยหรือต่างกันตามที่ใช้งาน ให้อยู่ใน ConfigMap รหัสผ่านให้อยู่ใน Secret

---

## 3. ConfigMap คืออะไร และอ่าน YAML ทีละบรรทัด

<p align="center">
  <img src="images/04-configmap-yaml.png" alt="เอกสาร shop-config.yaml มีบล็อก data เก็บ key: value ค่ามีเครื่องหมายคำพูด ไม่มี spec" width="800">
</p>

**ConfigMap คือ object ที่เก็บค่าตั้งค่าเป็นคู่ `key: value` ไว้ในคลัสเตอร์ ให้ Pod หยิบไปใช้เป็น env หรือเป็นไฟล์**

- ConfigMap **ไม่ได้รันอะไร** ไม่มี container ไม่มี Pod เป็นแค่ "แฟ้มเอกสาร" ที่วางไว้บนชั้นของหอบังคับการ
- Pod อ้าง ConfigMap ด้วย **ชื่อ** ดังนั้น ConfigMap กับ Pod ต้องอยู่ **namespace เดียวกัน** (ทุกอย่างในคอร์สอยู่ `default`)
- เหมาะกับค่าที่ไม่ลับ ถ้าลับให้ใช้ Secret (หัวข้อ 9)

### 3.1 ทบทวน YAML และสิ่งใหม่ของบทนี้

YAML ของบทนี้ใช้กฎเดิมจาก [บทที่ 2 หัวข้อ 5](../../002_kubernetes_pod/01_Theory/README.md#5-yaml-ฉบับเข้าใจง่าย)

- `key: value` = ค่าเดี่ยว / เยื้องเข้า = **เป็นลูก** / เยื้องเท่ากัน = **เป็นพี่น้อง**
- `- ` (ขีด + เว้นวรรค) = เริ่มรายการใหม่ 1 ชิ้น (`env`, `volumes` เป็น list)
- ค่าที่เป็นตัวเลขแต่อยากให้เป็นข้อความ ต้องใส่ `""` (เหมือน `OPEN_HOUR: "9"` ในบทที่ 2)

สิ่งใหม่ของ YAML บทนี้: **ข้อความหลายบรรทัดด้วย `|`** ใช้เก็บ "ไฟล์ทั้งไฟล์" ไว้ใน key เดียว (หัวข้อ 3.4)

### 3.2 ไล่ไฟล์จริงจาก LAB 1

ไฟล์ `02_LAB/labs/lab01-configmap-env/shop-config.yaml`

```yaml
# LAB 1: ConfigMap แรก — เก็บค่าตั้งค่าของร้านไว้นอก image เป็นคู่ key: value
apiVersion: v1
kind: ConfigMap
metadata:
  name: shop-config
data:                            # ค่าทุกตัวเป็นข้อความ (string) เสมอ
  SHOP_NAME: "ร้านอาหารแมวน้องส้ม"
  OPEN_HOURS: "09:00-21:00"
  ANNOUNCEMENT: "วันนี้ลด 10%"
```

อ่านทีละบรรทัด

| บรรทัด | ความหมาย |
|---|---|
| `apiVersion: v1` | ConfigMap อยู่กลุ่มหลัก `v1` (เหมือน Pod และ Service) |
| `kind: ConfigMap` | ขอสร้าง **ConfigMap** (C และ M ตัวใหญ่) |
| `metadata:` → `name: shop-config` | ชื่อแฟ้ม = ชื่อที่ Pod ใช้อ้าง (`name: shop-config` ใน Pod) |
| `data:` | **ข้อมูลในแฟ้ม** อยู่ระดับเดียวกับ `metadata` **ไม่มี `spec`** |
| `  SHOP_NAME: "ร้านอาหารแมวน้องส้ม"` | key ชื่อ `SHOP_NAME` ค่าเป็นข้อความ (ภาษาไทยได้) |
| `  OPEN_HOURS: "09:00-21:00"` | key ชื่อ `OPEN_HOURS` มี `:` อยู่ในค่า ใส่ `""` ให้ชัดว่าเป็นข้อความ |
| `  ANNOUNCEMENT: "วันนี้ลด 10%"` | key ชื่อ `ANNOUNCEMENT` ข้อความประกาศหน้าร้าน |

แปลทั้งไฟล์เป็นประโยคเดียว: **"ขอแฟ้มค่าตั้งค่าชื่อ `shop-config` มี 3 ค่า คือชื่อร้าน เวลาเปิด และประกาศ"**

ทำไม **ไม่มี `spec`**: `spec` คือ "สิ่งที่อยากให้เป็น" ที่ controller ต้องคอยทำให้จริง (เช่น `replicas: 3`) แต่ ConfigMap ไม่มีอะไรต้องทำ มีแค่ข้อมูล จึงใช้ `data` แทน (Secret ก็เหมือนกัน)

ผลจริงใน LAB 1 (`kube-root-ca.crt` เป็นใบรับรองที่คลัสเตอร์สร้างไว้เองทุก namespace ไม่ต้องไปยุ่ง)

```text
$ kubectl get configmap
NAME               DATA   AGE
kube-root-ca.crt   1      46s
shop-config        3      0s        ← DATA = จำนวน key

$ kubectl describe configmap shop-config
...
ANNOUNCEMENT:
----
วันนี้ลด 10%                          ← describe โชว์ค่าจริงทุกตัว เรียง key ตามตัวอักษร
...
```

### 3.3 ผิดบ่อย แก้ง่าย

| ผิด | ถูก | เพราะ |
|---|---|---|
| `kind: Configmap` | `kind: ConfigMap` | M ต้องใหญ่ |
| `spec:` → `data:` หรือ `spec:` แทน `data:` | `data:` อยู่ระดับเดียวกับ `metadata` | ConfigMap ไม่มี `spec` apply ไม่ผ่าน (field ที่ไม่รู้จัก) |
| `OPEN_HOUR: 9` หรือ `SALE: true` | `OPEN_HOUR: "9"`, `SALE: "true"` | `data` รับแต่ข้อความ ตัวเลข/true ไม่มี `""` apply ไม่ผ่าน |
| ConfigMap อยู่ namespace อื่น | อยู่ namespace เดียวกับ Pod | Pod หาแฟ้มด้วยชื่อในห้องตัวเองเท่านั้น |

### 3.4 ข้อความหลายบรรทัดด้วย `|`

ConfigMap ใน LAB 2 เก็บ **ไฟล์ทั้งไฟล์** ไว้ใน key เดียว (`02_LAB/labs/lab02-configmap-file/web-page.yaml`)

```yaml
data:
  index.html: |                  # | = ข้อความหลายบรรทัด เก็บตามที่เขียนทุกบรรทัด
    <meta charset="utf-8">
    <h1>ร้านน้องส้ม: เปิดแล้ว</h1>
```

- `index.html` = ชื่อ key (มีจุดในชื่อได้ จะกลายเป็นชื่อไฟล์ในหัวข้อ 7)
- `|` = ค่าคือ **ทุกบรรทัดถัดไปที่เยื้องลึกกว่า key** เก็บการขึ้นบรรทัดใหม่ไว้ตามที่เห็น
- ระยะเยื้องของบล็อก (4 ช่อง) **ถูกตัดออก** ใน LAB 2 `curl http://localhost:30080` ได้ 2 บรรทัดนี้ตรงตามที่เขียน ขึ้นต้นด้วย `<meta` เลย

> **⚠️ กับดัก:** ทุกบรรทัดในบล็อก `|` ต้องเยื้อง **เท่ากันหรือลึกกว่า** บรรทัดแรก ถ้าบรรทัดไหนเยื้องน้อยกว่า YAML จะคิดว่าบล็อกจบแล้ว และอ่านบรรทัดนั้นเป็น key ใหม่

---

## 4. ใช้ ConfigMap เป็น env: configMapKeyRef และ envFrom

<p align="center">
  <img src="images/05-env-keyref-vs-envfrom.png" alt="configMapKeyRef หยิบแผ่นเดียวแปะโน้ต 1 แผ่น envFrom ถ่ายสำเนาทั้งแฟ้มแปะโน้ตทุกแผ่น" width="800">
</p>

ใน [บทที่ 2 หัวข้อ 7.2](../../002_kubernetes_pod/01_Theory/README.md#72-env-ส่งค่าเข้า-container) เราเขียน `env` เป็นคู่ `name` / `value` ตรง ๆ บทนี้เปลี่ยน `value` เป็น **"ไปเอาค่ามาจาก ConfigMap"** มี 2 แบบ ไฟล์ `02_LAB/labs/lab01-configmap-env/config-pod.yaml` ใช้ทั้งคู่

```yaml
    - name: busybox
      ...
      env:
        - name: SHOP_NAME              # ดึงทีละ key: ตั้งชื่อตัวแปรเองได้
          valueFrom:
            configMapKeyRef:
              name: shop-config        # ชื่อ ConfigMap
              key: SHOP_NAME           # key ใน data
      envFrom:                         # ดึงทุก key ใน ConfigMap มาเป็นตัวแปรในครั้งเดียว
        - configMapRef:
            name: shop-config
```

วาง `shop-config.yaml` คู่กับ `config-pod.yaml` ให้เห็นว่า Pod **อ้างถึง ConfigMap ตรงไหนบ้าง** และค่าไหนต้องพิมพ์ให้ตรงกัน **วงสีเดียวกัน = ค่าที่ต้องตรงกัน**

<p align="center">
  <img src="images/05a-yaml-configmap-vs-pod-map.png" alt="shop-config.yaml กับ config-pod.yaml วางคู่กัน ลูกศรจากชื่อ ConfigMap และชื่อ key ไปยังจุดที่ Pod อ้างถึง" width="900">
</p>

- **① ชื่อแฟ้มต้องตรงกัน** `name: shop-config` ทั้งใต้ `configMapKeyRef` และใต้ `configMapRef` ต้องตรงกับ `metadata.name` ของ ConfigMap ไม่ตรง = หาแฟ้มไม่เจอ container ไม่ยอมเริ่ม (หัวข้อ 5)
- **② ชื่อ key ต้องตรงกัน** `key: SHOP_NAME` ต้องตรงกับชื่อ key ใต้ `data` ทุกตัวอักษร
- **③ `envFrom` เอาทุก key** ใต้ `data` มาเป็นตัวแปร ชื่อตัวแปร = ชื่อ key
- **④ ชื่อตัวแปรตั้งเองได้** `- name: SHOP_NAME` ใต้ `env` คือชื่อที่แอปเห็น ไม่จำเป็นต้องตรงกับ key (อธิบายต่อในแบบที่ 1)

### แบบที่ 1: `configMapKeyRef` หยิบทีละ key

- `env` → `- name:` = **ชื่อตัวแปร** ที่แอปจะเห็น
- `valueFrom` → `configMapKeyRef` = ค่าไม่ได้เขียนไว้ตรงนี้ ให้ไปเอาจาก ConfigMap `name` ที่ key `key`
- ชื่อตัวแปร **กับ** ชื่อ key **ไม่ต้องตรงกัน** เช่น `- name: STORE_TITLE` คู่กับ `key: SHOP_NAME` แอปจะเห็นตัวแปร `STORE_TITLE` ที่มีค่าของ `SHOP_NAME`

### แบบที่ 2: `envFrom` ดึงทั้งแฟ้ม

- `envFrom` → `- configMapRef:` → `name: shop-config` = **ทุก key** ใน ConfigMap กลายเป็นตัวแปร ชื่อตัวแปร = ชื่อ key
- `envFrom` อยู่ **ระดับเดียวกับ `env`** (เป็นพี่น้อง ไม่ได้อยู่ใต้ `env`)
- สะดวก แต่เพิ่ม key ในแฟ้มเมื่อไร Pod ใหม่ก็ได้ตัวแปรเพิ่มเองโดยไม่รู้ตัว

ผลจริงใน LAB 1: ได้ครบ 3 ตัว (`OPEN_HOURS` กับ `ANNOUNCEMENT` มาทาง `envFrom` อย่างเดียว) และ `describe` บอกที่มา **โดยไม่โชว์ค่า**

```text
$ kubectl exec config-pod -- printenv SHOP_NAME OPEN_HOURS ANNOUNCEMENT
ร้านอาหารแมวน้องส้ม
09:00-21:00
วันนี้ลด 10%

$ kubectl describe pod config-pod
    Environment Variables from:
      shop-config  ConfigMap  Optional: false                                     ← envFrom
    Environment:
      SHOP_NAME:  <set to the key 'SHOP_NAME' of config map 'shop-config'>  Optional: false   ← configMapKeyRef
```

- `SHOP_NAME` ได้มา 2 ทาง (ค่าเดียวกัน) ถ้าชื่อชนกัน ค่าจาก `env` **ชนะ** `envFrom`
- `Optional: false` = **ConfigMap นี้ต้องมี** ไม่มีแล้ว container ไม่ยอมเริ่ม (หัวข้อ 5)

> **เคล็ดลับ:** ใช้ `configMapKeyRef` เมื่ออยากรู้ชัดว่าแอปใช้ตัวแปรอะไรบ้าง (อ่าน YAML แล้วเห็นครบ) ใช้ `envFrom` เมื่อแฟ้มมีหลาย key ที่แอปใช้ทั้งหมด ร้านน้องส้มใน LAB 4 ใช้ `configMapKeyRef` เพราะแฟ้มของร้านมี `menu.txt` ที่ไม่ได้อยากให้เป็นตัวแปร

---

## 5. กับดัก: Pod มาก่อน ConfigMap

<p align="center">
  <img src="images/06-createcontainerconfigerror.png" alt="กล่อง Pod ไฟแดง CreateContainerConfigError เพราะไม่มีแฟ้ม shop-config บนชั้น พอวางแฟ้มแล้วกล่องเปิดได้ Running" width="800">
</p>

LAB 1 จงใจ apply **Pod ก่อน** ConfigMap (`config-pod.yaml` แล้วจึง `shop-config.yaml`)

```text
$ kubectl get pods
NAME         READY   STATUS                       RESTARTS   AGE
config-pod   0/1     CreateContainerConfigError   0          8s
```

`CreateContainerConfigError` = **เตรียมค่าตั้งค่าให้ container ไม่ได้** จึงสร้าง container ไม่ได้ ดูสาเหตุที่ Events (ตัดบางบรรทัดออก)

```text
$ kubectl describe pod config-pod
...
Events:
  Normal   Scheduled  8s               default-scheduler  Successfully assigned default/config-pod to lab-worker
  Normal   Pulled     1s               kubelet            ... Successfully pulled image "busybox:1.37" ...
  Warning  Failed     0s (x2 over 1s)  kubelet            spec.containers{busybox}: Error: configmap "shop-config" not found
```

อ่าน Events จากบนลงล่าง: หาเรือได้ (`lab-worker`) ✓ → ดึง image ได้ ✓ → จะสร้าง container แต่ **หาแฟ้ม `shop-config` ไม่เจอ** ✗ (`x2` = ลองแล้ว 2 รอบ)

ปัญหาไม่ได้อยู่ที่ image หรือแอป (ต่างจาก `ImagePullBackOff` / `CrashLoopBackOff` ใน [บทที่ 2 หัวข้อ 9.3](../../002_kubernetes_pod/01_Theory/README.md#93-อาการพังยอดฮิต)) แต่อยู่ที่ **ของที่ Pod อ้างถึงยังไม่มี**

### แก้: สร้าง ConfigMap แล้วรอ ไม่ต้องลบ Pod

หลัง apply `shop-config.yaml`

```text
$ kubectl get pods
NAME         READY   STATUS    RESTARTS   AGE
config-pod   1/1     Running   0          29s     ← Pod เดิม (AGE นับต่อ) RESTARTS 0
```

kubelet **ลองใหม่เองเป็นระยะ** พอแฟ้มมาวางบนชั้น container ก็เริ่มได้ เป็น Pod ตัวเดิม ไม่ได้สร้างใหม่

> **⚠️ กับดัก:** เห็น `CreateContainerConfigError` ให้ดู Events หาคำว่า `not found` แล้วเช็ก 3 อย่าง: **ชื่อ ConfigMap/Secret สะกดตรงไหม**, **apply แฟ้มแล้วหรือยัง**, **อยู่ namespace เดียวกันไหม** ถ้าชื่อ ConfigMap ถูกแต่ `key` ใน `configMapKeyRef` ผิด ก็ได้ STATUS เดียวกัน (Events บอกว่าหา key ไม่เจอ)

---

## 6. แก้ ConfigMap แล้ว env ไม่เปลี่ยน

<p align="center">
  <img src="images/07-env-not-updated.png" alt="แฟ้มเปลี่ยนเป็น 20% แต่โน้ตในตู้ของกล่องเดิมยังเป็น 10% กล่องใหม่ได้โน้ต 20%" width="800">
</p>

LAB 1 แก้ประกาศจาก 10% เป็น 20% ด้วย `shop-config-v2.yaml` (ต่างแค่บรรทัด `ANNOUNCEMENT: "วันนี้ลด 20%"   # ← เปลี่ยน`)

```text
$ kubectl describe configmap shop-config
...
ANNOUNCEMENT:
----
วันนี้ลด 20%                                  ← ในแฟ้มเปลี่ยนแล้ว

$ kubectl exec config-pod -- printenv ANNOUNCEMENT
วันนี้ลด 10%                                  ← แต่ใน Pod เดิมยังเป็นค่าเก่า
```

**ทำไม:** env ถูกใส่ให้โปรแกรม **ครั้งเดียวตอน container เริ่ม** (เหมือนโน้ตที่แปะในตู้ตอนเปิดกล่อง) หลังจากนั้นไม่มีใครมาเปลี่ยนตัวแปรของโปรแกรมที่รันอยู่ แฟ้มบนชั้นเปลี่ยนไปเท่าไรโน้ตในตู้ก็เท่าเดิม

**แก้:** ต้องได้ **container ใหม่** ใน LAB 1 ลบ Pod เดี่ยวแล้วสร้างใหม่

```text
$ kubectl delete pod config-pod
$ kubectl apply -f labs/lab01-configmap-env/config-pod.yaml
$ kubectl exec config-pod -- printenv ANNOUNCEMENT
วันนี้ลด 20%                                  ← Pod ใหม่อ่านค่าล่าสุด
```

- Pod เดี่ยว → ลบแล้วสร้างใหม่ (Pod แก้ส่วนใหญ่ไม่ได้ [บทที่ 2 หัวข้อ 14](../../002_kubernetes_pod/01_Theory/README.md#14-pod-เป็นของชั่วคราว-และบทถัดไป))
- Pod ของ Deployment → `kubectl rollout restart` เปลี่ยนใหม่ทั้งชุดแบบร้านไม่ปิด (หัวข้อ 11)
- apply ConfigMap ใหม่ **ไม่ทำให้ Deployment เปลี่ยนรุ่นเอง** เพราะแม่พิมพ์ (`template`) อ้างแค่ **ชื่อ** แฟ้ม ชื่อไม่เปลี่ยน แม่พิมพ์ก็ไม่เปลี่ยน

> **ประโยคเดียวที่ต้องจำ:** ConfigMap ที่ใช้เป็น **env** แก้แล้ว **Pod เดิมไม่รู้เรื่อง** ต้องได้ Pod ใหม่เสมอ

---

## 7. ใช้ ConfigMap เป็นไฟล์

<p align="center">
  <img src="images/08-configmap-as-file.png" alt="กระดานแขวนในกล่อง Pod มีแผ่น index.html คนเดินเอกสารเปลี่ยนแผ่นใหม่ให้เองราว 1 นาที โดยกล่องไม่ต้องเปิดใหม่" width="800">
</p>

แบบที่สองคือให้ ConfigMap กลายเป็น **ไฟล์ในโฟลเดอร์** ของ container **key = ชื่อไฟล์, value = เนื้อไฟล์** ใช้ 2 ขั้นเหมือน emptyDir ใน [บทที่ 2 หัวข้อ 11](../../002_kubernetes_pod/01_Theory/README.md#11-emptydir-ที่เก็บไฟล์ของ-pod): **ประกาศ volume** ที่ระดับ Pod แล้ว **mount** เข้า container

ไฟล์ `02_LAB/labs/lab02-configmap-file/web-deploy.yaml` (ส่วน Deployment, comment ที่มี `←` เพิ่มเพื่ออ่านคู่บทนี้)

```yaml
  template:
    ...
    spec:
      containers:
        - name: nginx
          image: nginx:1.27-alpine
          ...
          volumeMounts:                        # ← ขั้นที่ 2: เสียบเข้า container
            - name: page                       # ใช้ volume ชื่อ page (ประกาศข้างล่าง)
              mountPath: /usr/share/nginx/html # วางไว้ที่โฟลเดอร์หน้าเว็บของ nginx
      volumes:                                 # ← ขั้นที่ 1: ประกาศ volume ของ Pod
        - name: page
          configMap:                           # ← บทที่ 2 ใช้ emptyDir: {} ตรงนี้
            name: web-page                     # ทุก key ใน ConfigMap web-page กลายเป็นไฟล์ 1 ไฟล์
```

- `volumeMounts` → `name: page` ต้องตรงกับชื่อใน `volumes` และ `mountPath` = โฟลเดอร์ที่ไฟล์จะโผล่
- ConfigMap `web-page` มี key เดียวคือ `index.html` จึงได้ไฟล์ `/usr/share/nginx/html/index.html` (เนื้อไฟล์ = ข้อความ `|` ในหัวข้อ 3.4)

```text
$ kubectl exec web-6ffd6db47c-7sm82 -- ls /usr/share/nginx/html
index.html                ← LAB 2: เหลือแค่ไฟล์จาก ConfigMap
```

mount ลงโฟลเดอร์ไหน **ของเดิมในโฟลเดอร์นั้นถูกบังทั้งหมด** (หน้าเว็บเดิมของ nginx หายไปจากสายตา) และไฟล์จาก ConfigMap **อ่านได้อย่างเดียว** แอปเขียนทับไม่ได้

### แก้ ConfigMap แล้วไฟล์เปลี่ยนเอง

LAB 2 apply `web-page-v2.yaml` (เปลี่ยนบรรทัด `<h1>`) แล้ว curl ซ้ำ (ตัดบรรทัด `<meta charset="utf-8">` ออก)

```text
$ curl http://localhost:30080
<h1>ร้านน้องส้ม: เปิดแล้ว</h1>        ← ทันทีหลัง apply: ยังเดิม
...   (curl อีกครั้งหลัง 30 วินาที: ยังเดิม)
$ curl http://localhost:30080
<h1>ร้านน้องส้ม: มีเมนูใหม่</h1>       ← ราว 79 วินาทีหลัง apply: เปลี่ยนแล้ว

$ kubectl get pods
NAME                   READY   STATUS    RESTARTS   AGE
web-6ffd6db47c-7sm82   1/1     Running   0          90s    ← Pod ชื่อเดิม RESTARTS 0
web-6ffd6db47c-qg4dx   1/1     Running   0          90s
```

- **Pod เดิม ไม่ restart** แต่ไฟล์ข้างในเปลี่ยน nginx อ่านไฟล์ใหม่ทุกครั้งที่มีคนขอหน้าเว็บ จึงเห็นของใหม่ทันทีที่ไฟล์เปลี่ยน
- คนเปลี่ยนไฟล์คือ **kubelet** บนเรือแต่ละลำ (คนเดินเอกสารที่เปลี่ยนแผ่นบนกระดานแขวน) ซึ่งตรวจ ConfigMap เป็นรอบ ๆ จึงช้าราว **1 นาที** (LAB 2 ได้ 79 วินาที LAB 4 ได้ราว 63 วินาที)

### `items`: เลือกบาง key มาเป็นไฟล์

แฟ้มของร้านน้องส้ม (`som-menu-config`) มี 3 key แต่อยากได้แค่ `menu.txt` เป็นไฟล์ ไฟล์ `som-menu-deploy.yaml` จึงใช้ `items`

```yaml
      volumes:
        - name: menu
          configMap:
            name: som-menu-config
            items:                        # เลือกเฉพาะ key menu.txt มาเป็นไฟล์ (ไม่เอา SHOP_NAME, ANNOUNCEMENT)
              - key: menu.txt             # ← key ใน ConfigMap
                path: menu.txt            # ← ชื่อไฟล์ในโฟลเดอร์ที่ mount
```

ใน LAB 4 `kubectl exec som-menu-895b459c4-hrtbp -- ls /etc/som-menu` ได้ `menu.txt` ไฟล์เดียว ถ้าไม่มี `items` จะได้ 3 ไฟล์ (`SHOP_NAME`, `ANNOUNCEMENT`, `menu.txt`)

### ไฟล์เดียว หลาย object: `---`

`web-deploy.yaml` มีทั้ง Deployment และ Service ([บทที่ 5](../../005_kubernetes_Service/01_Theory/README.md#10-nodeport-ประตูบนทุก-node)) ในไฟล์เดียว คั่นด้วย `---` (ขีด 3 ตัวชิดซ้าย) = **"จบ object หนึ่ง เริ่ม object ถัดไป"**

ใน LAB 2 apply ครั้งเดียวได้ทั้ง `deployment.apps/web created` และ `service/web created` และ `kubectl delete -f` ไฟล์เดียวกันก็ลบทั้งคู่

> **⚠️ กับดัก:** ใน LAB 2 ต้อง apply **ConfigMap ก่อน** Deployment ถ้าสลับกัน Pod จะค้างที่ `ContainerCreating` เพราะเตรียม volume จาก ConfigMap ที่ยังไม่มีไม่ได้ (ดู Events ของ `describe pod` เหมือนหัวข้อ 5) พอสร้าง ConfigMap แล้วก็เดินต่อเอง

---

## 8. env หรือไฟล์ เลือกแบบไหน

<p align="center">
  <img src="images/09-env-vs-file.png" alt="ฝั่ง env โน้ตในตู้ต้อง rollout restart ฝั่ง file กระดานแขวนเปลี่ยนเอง หน้าเว็บร้าน เมนูเปลี่ยนแล้ว ประกาศยังเดิม" width="800">
</p>

| | env (`configMapKeyRef`, `envFrom`, `secretKeyRef`) | ไฟล์ (`volumes` + `volumeMounts`) |
|---|---|---|
| แอปอ่านค่าอย่างไร | อ่านตัวแปร (เช่น `process.env.SHOP_NAME`) | เปิดไฟล์ (เช่น `/etc/som-menu/menu.txt`) |
| แก้ ConfigMap แล้ว | **ไม่เปลี่ยน** จนกว่าจะได้ container ใหม่ | **ไฟล์เปลี่ยนเอง** ราว 1 นาที |
| ต้อง restart Pod ไหม | ต้อง (`rollout restart`) | ไม่ต้อง ถ้าแอปอ่านไฟล์ใหม่ทุกครั้ง |
| เหมาะกับ | ค่าสั้น ๆ: ชื่อร้าน, URL, ระดับ log, รหัสผ่าน | ไฟล์ทั้งไฟล์: หน้าเว็บ, เมนู, ไฟล์ตั้งค่าของ nginx |

### ผลจริงใน LAB 4: ร้านเดียว เห็นทั้ง 2 แบบ

แอปร้านน้องส้ม (`02_LAB/som-menu/app/server.js`) อ่านค่า 2 แบบต่างกัน

```js
const SHOP_NAME = process.env.SHOP_NAME || "ร้านอาหารแมวน้องส้ม";   // ← env: อ่านครั้งเดียวตอนเริ่ม
const ANNOUNCEMENT = process.env.ANNOUNCEMENT || "";
...
const MENU_FILE = process.env.MENU_FILE || "/etc/som-menu/menu.txt";
...
function readMenu() {
  ...
    const items = fs.readFileSync(MENU_FILE, "utf8").split("\n")   // ← ไฟล์: อ่านใหม่ทุกครั้งที่มีลูกค้า
```

LAB 4 apply `som-menu-config-v2.yaml` ที่เปลี่ยน **2 จุด**: ประกาศ (env) เป็น `มีไอศกรีมแมวแล้ว!` และเพิ่มเมนู (ไฟล์) `ไอศกรีมแมว รสนมแพะ|49`

1. **ราว 1 นาทีต่อมา** refresh หน้าร้าน: เมนูมี `ไอศกรีมแมว รสนมแพะ 49 บาท` แล้ว แต่ประกาศยังเป็น `เปิดร้านวันแรก ลด 10%` เสิร์ฟโดย Pod `som-menu-895b459c4-hrtbp` ตัวเดิม ([ภาพหน้าจอจริง](../02_LAB/images/screenshots/20261018_lab4_02-shop-menu-updated.png)) และ `kubectl get pods` ยังเป็น 3 ตัวเดิม (AGE `67s`, RESTARTS `0`)
2. หลัง `kubectl rollout restart` ประกาศเป็น `มีไอศกรีมแมวแล้ว!` เสิร์ฟโดย Pod ชื่อใหม่ `som-menu-7879c9f754-vxcn2` ([ภาพหน้าจอจริง](../02_LAB/images/screenshots/20261018_lab4_03-shop-after-restart.png))

> **เคล็ดลับ:** "ไฟล์เปลี่ยนเอง" ช่วยได้ก็ต่อเมื่อ **แอปอ่านไฟล์ใหม่** ด้วย แอปที่อ่านไฟล์ครั้งเดียวตอนเริ่ม (แล้วเก็บไว้ในหน่วยความจำ) จะไม่เห็นค่าใหม่เหมือน env ต้อง restart เช่นกัน

---

## 9. Secret คืออะไร และ base64

<p align="center">
  <img src="images/10-secret-sealed-envelope.png" alt="ชั้นในหอบังคับการมีแฟ้ม ConfigMap สีฟ้าและซอง Secret ตราแดง คนเดินเอกสารถือซอง admin-secret ไปส่งที่กล่อง Pod" width="800">
</p>

**Secret คือ object ที่หน้าตาและวิธีใช้เหมือน ConfigMap เกือบทุกอย่าง แต่ตั้งใจไว้เก็บค่าลับ** เช่น รหัสผ่าน token กุญแจ

ไฟล์ `02_LAB/labs/lab03-secret/admin-secret.yaml`

```yaml
# LAB 3: Secret แรก — เก็บรหัสผ่านแยกจาก ConfigMap
# ⚠️ ไฟล์นี้มีรหัสตัวอย่างไว้เรียนเท่านั้น งานจริงห้าม commit Secret ขึ้น Git
apiVersion: v1
kind: Secret
metadata:
  name: admin-secret
type: Opaque                     # Secret ทั่วไป เก็บ key: value อะไรก็ได้
stringData:                      # เขียนเป็นข้อความธรรมดา Kubernetes จะแปลงเป็น base64 ใน data ให้เอง
  ADMIN_PASSWORD: "meow-1234"
```

- `kind: Secret` + `apiVersion: v1` เหมือน ConfigMap และ **ไม่มี `spec`** เหมือนกัน
- `type: Opaque` = Secret ทั่วไป (Opaque = "ทึบ" Kubernetes ไม่สนว่าข้างในคืออะไร) ยังมีชนิดอื่นสำหรับใบรับรอง TLS หรือรหัสเข้า image registry ที่บทนี้ไม่ใช้
- **`stringData`** = เขียนค่าเป็นข้อความธรรมดา ตอนเก็บ Kubernetes แปลงเป็น base64 ไว้ใน **`data`** ให้
- ถ้าเขียน `data:` เอง ค่าต้องเป็น base64 อยู่แล้ว (เขียน `meow-1234` ตรง ๆ ใต้ `data:` apply ไม่ผ่าน)
- ใช้ได้ทั้งแบบ env (`secretKeyRef`, `envFrom` → `secretRef`) และแบบไฟล์ (volume `secret:`) เหมือน ConfigMap

LAB 3 ใช้ใน Pod ด้วย **`secretKeyRef`** ซึ่งหน้าตาเหมือน `configMapKeyRef` ทุกอย่าง (`02_LAB/labs/lab03-secret/secret-pod.yaml`)

```yaml
      env:
        - name: ADMIN_PASSWORD
          valueFrom:
            secretKeyRef:              # เหมือน configMapKeyRef แต่ดึงจาก Secret
              name: admin-secret
              key: ADMIN_PASSWORD
```

### base64 ไม่ใช่การเข้ารหัส

ผลจริงใน LAB 3

```text
$ kubectl get secret admin-secret -o yaml
...
data:
  ADMIN_PASSWORD: bWVvdy0xMjM0          ← base64 ของ meow-1234
...

$ kubectl exec secret-pod -- printenv ADMIN_PASSWORD
meow-1234                               ← ใน Pod ได้ค่าจริง
```

- **base64** = วิธี **เขียนข้อมูลใหม่ด้วยตัวอักษรชุดจำกัด** (A–Z a–z 0–9 + /) ให้ส่งข้อมูลอะไรก็ได้ผ่านข้อความได้ ไม่มีกุญแจ ใครก็แปลงกลับได้ (เช่นคำสั่ง `base64 -d` มีอยู่ทุกเครื่อง)
- `bWVvdy0xMjM0` ↔ `meow-1234` จึงเป็น **ของชิ้นเดียวกันเขียนคนละแบบ** ไม่ได้ปลอดภัยขึ้นเลย
- ในอุปมา: ซองตราแดง **แค่พับ** ไม่ได้ **ล็อก** ใครหยิบซองไปได้ก็คลี่อ่านได้

เทียบ ConfigMap กับ Secret

| | ConfigMap | Secret |
|---|---|---|
| ใช้เก็บ | ค่าตั้งค่าทั่วไป | รหัสผ่าน token กุญแจ |
| ค่าในฟิลด์ `data` | ข้อความตรง ๆ | base64 (เขียนตรง ๆ ได้ที่ `stringData`) |
| `kubectl describe` | โชว์ค่าทุกตัว | โชว์แค่ขนาด (`9 bytes`) |
| ใช้เป็น env | `configMapKeyRef`, `envFrom` → `configMapRef` | `secretKeyRef`, `envFrom` → `secretRef` |
| ใช้เป็นไฟล์ | volume `configMap:` | volume `secret:` |

---

## 10. Secret ปลอดภัยแค่ไหน

<p align="center">
  <img src="images/11-secret-not-encrypted.png" alt="ซองตราแดงแค่พับไว้ ไม่ได้ล็อก bWVvdy0xMjM0 แปลงกลับเป็น meow-1234 ได้ และแผ่น last-applied-configuration มีรหัสจริง" width="800">
</p>

Secret ช่วย **ไม่ให้รหัสโผล่โดยไม่ตั้งใจ** แต่ **ไม่ได้ซ่อนจากคนที่มีสิทธิ์อ่าน Secret** ไล่ดูจาก LAB 3 ว่ารหัสโผล่ที่ไหนบ้าง

**ที่ที่ไม่โผล่**: `describe` ไม่แสดงค่า คนที่ยืนดูจอเราขณะดีบักก็ไม่เห็นรหัส

```text
$ kubectl describe secret admin-secret
...
ADMIN_PASSWORD:  9 bytes              ← บอกแค่ขนาด (meow-1234 ยาว 9 ตัวอักษร)

$ kubectl describe pod secret-pod
    Environment:
      ADMIN_PASSWORD:  <set to the key 'ADMIN_PASSWORD' in secret 'admin-secret'>  Optional: false
```

**ที่ที่โผล่**

1. **`-o yaml`** โชว์ base64 (`bWVvdy0xMjM0`) ซึ่งแปลงกลับได้ทันที (หัวข้อ 9)
2. **ใน Pod** แอปต้องใช้รหัสจริง จึงเห็นค่าจริง ใครที่ `kubectl exec` เข้า Pod ได้ก็ `printenv` อ่านได้
3. **annotation `last-applied-configuration`** ใน `-o yaml` เดียวกันนั้นเอง

```text
$ kubectl get secret admin-secret -o yaml
...
metadata:
  annotations:
    kubectl.kubernetes.io/last-applied-configuration: |
      {"apiVersion":"v1","kind":"Secret",...,"stringData":{"ADMIN_PASSWORD":"meow-1234"},"type":"Opaque"}
```

`kubectl apply` จด **ไฟล์ทั้งไฟล์ที่เรา apply** ไว้ใน annotation นี้ (ไว้เทียบตอน apply ครั้งถัดไป) ไฟล์ของเราใช้ `stringData` รหัสจริง `meow-1234` จึงถูกจดไว้ตรง ๆ ไม่ได้เป็นแม้แต่ base64

**กติกาที่ใช้จริง**

- **ห้าม commit ไฟล์ Secret ที่มีรหัสจริงขึ้น Git** Git จำทุกเวอร์ชัน ลบทีหลังก็ยังค้นเจอในประวัติ ไฟล์ Secret ใน LAB (`meow-1234`, `tuna-5678`) เป็น **รหัสตัวอย่าง** หัวไฟล์จึงมีคำเตือน `⚠️` ไว้
- **ใครดู Secret ได้** ถูกคุมด้วยระบบสิทธิ์ของ Kubernetes (RBAC) ให้สิทธิ์อ่าน Secret เฉพาะคนและแอปที่จำเป็น บนคลัสเตอร์ kind ของเราเราเป็นผู้ดูแล จึงเห็นได้ทุกอย่าง
- งานจริงมักสร้าง Secret จากคำสั่งหรือเครื่องมือเก็บรหัส แทนการเก็บไฟล์รหัสไว้ในโปรเจกต์ (นอกขอบเขตบทนี้)

> **⚠️ ความปลอดภัย:** **base64 ไม่ใช่การเข้ารหัส** และ `kubectl apply` ไฟล์ที่ใช้ `stringData` จะทิ้ง **รหัสจริง** ไว้ใน annotation `last-applied-configuration` ใครอ่าน Secret ได้ก็ได้รหัสไปทันที จงคุมว่า **ใครอ่าน Secret ได้** และ **ไฟล์รหัสอยู่ที่ไหน**

---

## 11. kubectl rollout restart: เปลี่ยน Pod ใหม่ทั้งชุดโดยไม่แก้ YAML

<p align="center">
  <img src="images/12-rollout-restart.png" alt="ผู้จัดการลูกเรือกดปุ่ม rollout restart กล่องแถบส้มถูกเปลี่ยนเป็นแถบเขียวทีละใบ กล่องใหม่ได้โน้ตใหม่" width="800">
</p>

หัวข้อ 6 บอกว่า env ต้องได้ container ใหม่ ถ้าเป็น Pod ของ Deployment เราไม่ได้อยากลบทีละตัวเอง และ **ไม่มีอะไรใน YAML ของ Deployment ให้แก้** (image เดิม ชื่อแฟ้มเดิม) คำสั่งใหม่ของบทนี้คือ `kubectl rollout restart deployment/<ชื่อ>` = **"เปลี่ยน Pod ใหม่ทั้งชุดแบบ rolling update"** เหมือนเปลี่ยนรุ่นใน [บทที่ 4 หัวข้อ 7](../../004_kubernetes_Deployment/01_Theory/README.md#7-rolling-update-ทยอยเปลี่ยนทีละ-pod) แต่ไม่ต้องแก้ไฟล์

ผลจริงใน LAB 4 (หลัง apply `som-menu-config-v2.yaml`)

```text
$ kubectl rollout restart deployment/som-menu
deployment.apps/som-menu restarted

$ kubectl rollout status deployment/som-menu
...
deployment "som-menu" successfully rolled out

$ kubectl get pods
NAME                        READY   STATUS    RESTARTS   AGE
som-menu-7879c9f754-29kxc   1/1     Running   0          7s
som-menu-7879c9f754-jlnmg   1/1     Running   0          9s
som-menu-7879c9f754-vxcn2   1/1     Running   0          8s

$ kubectl logs som-menu-7879c9f754-29kxc
ร้านอาหารแมวน้องส้ม เปิดสาขา som-menu-7879c9f754-29kxc ที่ port 3000 ประกาศ: "มีไอศกรีมแมวแล้ว!" ตั้งรหัสหลังร้าน: แล้ว
```

- ชื่อ Pod เปลี่ยน hash จาก `895b459c4` เป็น **`7879c9f754`** = **ReplicaSet ใหม่** ([บทที่ 4 หัวข้อ 5](../../004_kubernetes_Deployment/01_Theory/README.md#5-ชื่อ-pod-3-ท่อน-และเจ้าของ-2-ชั้น))
- ทำไม hash เปลี่ยนทั้งที่เราไม่ได้แก้อะไร: `rollout restart` **แปะเวลาที่สั่ง restart** ไว้เป็น annotation ในแม่พิมพ์ (`template`) ให้เอง แม่พิมพ์เปลี่ยนนิดเดียว → hash ใหม่ → Deployment ทยอยเปลี่ยน Pod เหมือนเปลี่ยนรุ่นทุกอย่าง (นับเป็น revision ใหม่ในสมุดรุ่นด้วย)
- Pod ใหม่เริ่ม container ใหม่ จึงอ่าน env จาก ConfigMap ล่าสุด log ขึ้นประกาศใหม่ทันที
- ระหว่างเปลี่ยน มี readinessProbe + Service ([บทที่ 5 หัวข้อ 11](../../005_kubernetes_Service/01_Theory/README.md#11-service-ระหว่างเปลี่ยนรุ่น-readinessprobe-และ-rolling-update)) ร้านจึงไม่ปิด แค่ refresh browser

> **เคล็ดลับ:** `rollout restart` ใช้กับ **Deployment** (object ที่มีแม่พิมพ์) ไม่ใช้กับ Pod เดี่ยว Pod เดี่ยวต้องลบแล้วสร้างใหม่แบบ LAB 1

---

## 12. อ่าน YAML ร้านน้องส้มทั้งไฟล์

<p align="center">
  <img src="images/13-som-menu-config-yaml-skeleton.png" alt="โครง som-menu-deploy.yaml บล็อก env 3 แถว 2 แถวโยงแฟ้ม som-menu-config 1 แถวโยงซอง som-menu-secret และ volumes เลือก menu.txt" width="800">
</p>

LAB 4 apply 4 ไฟล์ใน `02_LAB/som-menu/k8s/` **ทีละไฟล์** ตามลำดับ `som-menu-config.yaml` → `som-menu-secret.yaml` → `som-menu-deploy.yaml` → `som-menu-svc.yaml` แฟ้มและซองมาก่อน Deployment เพื่อไม่ให้ติด `CreateContainerConfigError` (หัวข้อ 5)

### 12.1 แฟ้มและซองของร้าน

`som-menu-config.yaml`: 3 key ใช้ 2 แบบ

```yaml
kind: ConfigMap
metadata:
  name: som-menu-config
data:
  SHOP_NAME: "ร้านอาหารแมวน้องส้ม"          # ← ใช้เป็น env
  ANNOUNCEMENT: "เปิดร้านวันแรก ลด 10%"     # ← ใช้เป็น env
  menu.txt: |                    # 1 บรรทัด = 1 เมนู รูปแบบ ชื่อ|ราคา
    อาหารเม็ดสูตรปลาทูน่า|459
    อาหารเปียกปลาซาบะ|35
    ขนมแมวเลียรสไก่|59
```

(ตัด comment หัวไฟล์และ `apiVersion: v1` ออก comment ที่มี `←` เพิ่มเพื่ออ่านคู่บทนี้ `|` ใน `ชื่อ|ราคา` เป็นแค่ตัวคั่นในเนื้อไฟล์เมนู ไม่ใช่ `|` ของ YAML)

`som-menu-secret.yaml` หน้าตาเหมือน `admin-secret.yaml` (หัวข้อ 9) ต่างแค่ `name: som-menu-secret` และ `ADMIN_PASSWORD: "tuna-5678"` (รหัสหลังร้าน `/admin` ผู้ใช้ `som`)

### 12.2 โครงของ som-menu-deploy.yaml

พับเหลือแค่ส่วนที่บทนี้เพิ่ม

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: som-menu
spec:
  replicas: 3
  selector: ...
  template:
    metadata: ...           # ป้าย app: som-menu (Service ใช้ป้ายนี้ บทที่ 5)
    spec:
      containers:
        - name: web
          image: som-menu:1.0
          env: ...          # ← ใหม่: 3 ตัวแปร มาจาก ConfigMap 2 ตัว Secret 1 ตัว
          volumeMounts: ... # ← ใหม่: เสียบ volume menu ที่ /etc/som-menu
          ports: ...
          readinessProbe: ...
          resources: ...
      volumes: ...          # ← ใหม่: volume menu มาจาก ConfigMap เลือกแค่ menu.txt
```

### 12.3 เปิดดูทีละส่วน

```yaml
        - name: web
          image: som-menu:1.0
          imagePullPolicy: IfNotPresent   # ใช้ image ที่ kind load ไว้บน node
          env:
            - name: SHOP_NAME             # จาก ConfigMap (อ่านครั้งเดียวตอน container เริ่ม)   ← หัวข้อ 4
              valueFrom:
                configMapKeyRef:
                  name: som-menu-config
                  key: SHOP_NAME
            - name: ANNOUNCEMENT          # จาก ConfigMap (แก้แล้วต้อง restart Pod)            ← หัวข้อ 6, 11
              valueFrom:
                configMapKeyRef:
                  name: som-menu-config
                  key: ANNOUNCEMENT
            - name: ADMIN_PASSWORD        # จาก Secret                                         ← หัวข้อ 9
              valueFrom:
                secretKeyRef:
                  name: som-menu-secret
                  key: ADMIN_PASSWORD
          volumeMounts:
            - name: menu                  # เมนูเป็นไฟล์ /etc/som-menu/menu.txt (แก้แล้วไฟล์เปลี่ยนเอง) ← หัวข้อ 7
              mountPath: /etc/som-menu
          ...                             # ← ports / readinessProbe / resources เหมือนบทที่ 5
      volumes: ...                        # ← หัวข้อ 7: volume menu จาก som-menu-config ใช้ items เลือกแค่ menu.txt
```

(comment ที่มี `←` เพิ่มเพื่ออ่านคู่บทนี้ ในไฟล์จริงไม่มี)

ไล่ให้ครบว่าแต่ละค่ามาจากไหน ไปอยู่ไหน

- `SHOP_NAME`, `ANNOUNCEMENT` → **env** จากแฟ้ม `som-menu-config`
- `ADMIN_PASSWORD` → **env** จากซอง `som-menu-secret`
- `menu.txt` → **ไฟล์** `/etc/som-menu/menu.txt` ตรงกับค่า `MENU_FILE` ที่แอปเปิดอ่าน (หัวข้อ 8)
- แฟ้ม `som-menu-config` ถูกใช้ **2 ที่** ใน Deployment เดียว: ทีละ key เป็น env และ `items` เป็นไฟล์

### 12.4 ผลจริงใน LAB 4

```text
$ kubectl logs som-menu-895b459c4-hrtbp
ร้านอาหารแมวน้องส้ม เปิดสาขา som-menu-895b459c4-hrtbp ที่ port 3000 ประกาศ: "เปิดร้านวันแรก ลด 10%" ตั้งรหัสหลังร้าน: แล้ว

$ curl http://localhost:30080/admin
หลังร้าน: รหัสผ่านไม่ถูกต้อง
$ curl -u som:tuna-5678 http://localhost:30080/admin
หลังร้าน som-menu-895b459c4-sg9rv: เสิร์ฟไปแล้ว 0 ครั้ง
$ curl -u som:1234 http://localhost:30080/admin
หลังร้าน: รหัสผ่านไม่ถูกต้อง
```

- `curl -u ผู้ใช้:รหัส` = ส่งชื่อผู้ใช้และรหัสไปกับคำขอ (HTTP Basic Auth) ไม่ใส่หรือใส่ผิดได้ `รหัสผ่านไม่ถูกต้อง` ใส่ `tuna-5678` ที่มาจาก Secret จึงผ่าน
- log บอก `ตั้งรหัสหลังร้าน: แล้ว` โดย **ไม่พิมพ์รหัสออกมา** แอปที่ดีไม่ควรเขียนรหัสลง log
- Service `som-menu` คือไฟล์เดียวกับบทที่ 5 (NodePort `30080` → targetPort `3000`) ไม่ต้องแก้

> **⚠️ กับดัก:** โฟลเดอร์ `som-menu/k8s/` มี `som-menu-config.yaml` **และ** `som-menu-config-v2.yaml` ซึ่งใช้ชื่อ ConfigMap เดียวกัน ถ้าสั่ง `kubectl apply -f som-menu/k8s/` ทั้งโฟลเดอร์ ทั้ง 2 รุ่นจะถูก apply ต่อกัน ไฟล์ที่ apply ทีหลังทับไฟล์แรก ได้ค่าที่ไม่ได้ตั้งใจ LAB 4 จึงสั่ง **ทีละไฟล์** เสมอ

แปลทั้ง Deployment เป็นประโยคเดียว: **"ขอร้าน `som-menu` 3 สาขาจาก image `som-menu:1.0` ตัวเดิม โดยให้ชื่อร้านและประกาศมาจากแฟ้ม `som-menu-config` เป็น env รหัสหลังร้านมาจากซอง `som-menu-secret` เป็น env และเมนูมาจากแฟ้มเดียวกันเป็นไฟล์ `/etc/som-menu/menu.txt`"**

---

## 13. ปูทางบทถัดไป

<p align="center">
  <img src="images/14-next-chapter-preview.png" alt="ตัวอย่างบทหน้า มองผ่านกล้องส่องทางไกล" width="800">
</p>

ค่าตั้งค่าและรหัสผ่านแยกออกจาก image แล้ว แต่ยังมีของอีกประเภทที่ ConfigMap / Secret ช่วยไม่ได้: **ข้อมูลที่แอปเขียนขึ้นเองระหว่างทำงาน**

- ConfigMap / Secret เป็นของที่ **เราเขียนแล้วส่งเข้า Pod** ไฟล์จาก ConfigMap ยังอ่านได้อย่างเดียว แอปเขียนกลับไม่ได้
- ยอด `เสิร์ฟไปแล้ว ... ครั้ง` ในหน้า `/admin` อยู่ในหน่วยความจำของแต่ละ Pod (`let served = 0` ใน `server.js`) หลัง `rollout restart` ได้ Pod ใหม่ทั้ง 3 ตัว **ยอดจึงเริ่มนับจาก 0 ใหม่หมด**
- ฐานข้อมูลของร้านใน[บทที่ 2 หัวข้อ 11](../../002_kubernetes_pod/01_Theory/README.md#11-emptydir-ที่เก็บไฟล์ของ-pod) ใช้ emptyDir ลบ Pod แล้วออเดอร์กลับเป็น 0
- → **PersistentVolume / PersistentVolumeClaim** ที่เก็บข้อมูลที่อยู่ได้นานกว่า Pod **(บทที่ 7)** และ Secret ของบทนี้จะใช้เก็บ **รหัสฐานข้อมูล** แทนการเขียนตรงใน YAML แบบบทที่ 2

---

## 14. สรุปและคำถามทบทวน

<p align="center">
  <img src="images/15-chapter-summary.png" alt="สรุปบทที่ 6" width="800">
</p>

### สรุป

1. **แยกค่าตั้งค่าออกจาก image**: build ครั้งเดียว ใช้ได้ทุกที่ ค่าที่เปลี่ยนบ่อยอยู่ใน ConfigMap รหัสผ่านอยู่ใน Secret
2. **ConfigMap** = แฟ้ม `key: value` ใช้ `apiVersion: v1` มี **`data` แทน `spec`** ค่าเป็นข้อความเสมอ (ตัวเลขต้องมี `""`) และเก็บไฟล์ทั้งไฟล์ได้ด้วย `|`
3. ใช้เป็น env 2 แบบ: **`configMapKeyRef`** (ทีละ key ตั้งชื่อตัวแปรเองได้) และ **`envFrom`** (ทุก key ในครั้งเดียว) ชื่อซ้ำกัน `env` ชนะ
4. Pod อ้าง ConfigMap/Secret ที่ยังไม่มี → **`CreateContainerConfigError`** + Event `not found` สร้างแฟ้มแล้ว Pod เดิมเริ่มเอง
5. **env อ่านครั้งเดียวตอน container เริ่ม** แก้ ConfigMap แล้ว Pod เดิมยังเห็นค่าเก่า ต้องได้ Pod ใหม่
6. ใช้เป็น **ไฟล์** ด้วย `volumes` → `configMap` + `volumeMounts` (key = ชื่อไฟล์, `items` เลือกบาง key) แก้แล้ว **ไฟล์เปลี่ยนเองราว 1 นาที** โดย Pod ไม่ restart
7. **Secret** หน้าตาเหมือน ConfigMap (`type: Opaque`, `stringData` → เก็บเป็น base64 ใน `data`) ใช้ด้วย `secretKeyRef` `describe` ซ่อนค่าเหลือแค่ขนาด
8. **base64 ไม่ใช่การเข้ารหัส** (`bWVvdy0xMjM0` = `meow-1234`) และ `apply` ไฟล์ `stringData` ทิ้งรหัสจริงไว้ใน `last-applied-configuration` ห้าม commit Secret จริงขึ้น Git คุมสิทธิ์ด้วย RBAC
9. **`kubectl rollout restart deployment/<ชื่อ>`** เปลี่ยน Pod ใหม่ทั้งชุดแบบ rolling update โดยไม่แก้ YAML ใช้หลังแก้ค่าที่เป็น env
10. ConfigMap / Secret ส่งค่า **เข้า** Pod แต่ข้อมูลที่แอปเขียนยังหายเมื่อได้ Pod ใหม่ → บทหน้า **PersistentVolume / PersistentVolumeClaim**

### คำถามทบทวน

**1. อ่าน YAML นี้แล้วตอบ: container มีตัวแปร env อะไรบ้าง แต่ละตัวมาจาก ConfigMap หรือ Secret และไฟล์อะไรโผล่ที่ path ไหน**

```yaml
spec:
  containers:
    - name: api
      image: cat-api:1.0
      env:
        - name: DB_HOST
          valueFrom:
            configMapKeyRef:
              name: api-config
              key: database_host
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: api-secret
              key: password
      volumeMounts:
        - name: conf
          mountPath: /etc/cat-api
  volumes:
    - name: conf
      configMap:
        name: api-config
        items:
          - key: app.yaml
            path: app.yaml
```

<details>
<summary>แนวคำตอบ</summary>

env 2 ตัว: `DB_HOST` มาจาก ConfigMap `api-config` key `database_host` (ชื่อตัวแปรกับชื่อ key ไม่ต้องตรงกัน) และ `DB_PASSWORD` มาจาก Secret `api-secret` key `password` ส่วนไฟล์มี 1 ไฟล์คือ `/etc/cat-api/app.yaml` มาจาก key `app.yaml` ของ ConfigMap `api-config` (เลือกด้วย `items`)
</details>

**2. ConfigMap นี้ผิดกี่จุด อะไรบ้าง**

```text
apiVersion: apps/v1
kind: Configmap
metadata:
  name: shop-config
spec:
  OPEN_HOUR: 9
  ANNOUNCEMENT: "วันนี้ลด 10%"
```

<details>
<summary>แนวคำตอบ</summary>

1. `apiVersion: apps/v1` ต้องเป็น `v1`
2. `kind: Configmap` ต้องเป็น `ConfigMap` (M ใหญ่)
3. `spec:` ต้องเป็น `data:` (ConfigMap ไม่มี spec)
4. `OPEN_HOUR: 9` ต้องเป็น `"9"` เพราะค่าใน `data` ต้องเป็นข้อความ
</details>

**3. Pod นี้ใช้ ConfigMap `shop-config` ที่มี key `SHOP_NAME` อยู่แล้ว แต่ STATUS ยังเป็น `CreateContainerConfigError` จุดไหนผิด**

```yaml
      env:
        - name: SHOP_NAME
          valueFrom:
            configMapKeyRef:
              name: shop-config
              key: SHOPNAME
```

<details>
<summary>แนวคำตอบ</summary>

`key: SHOPNAME` สะกดไม่ตรงกับ key ในแฟ้ม (`SHOP_NAME` มีขีดล่าง) kubelet หา key ไม่เจอจึงเตรียม env ไม่ได้ ดูยืนยันที่ Events ของ `kubectl describe pod` แล้วแก้ `key` ให้ตรง
</details>

**4. เพื่อนส่งผลนี้มา บอกสาเหตุและวิธีแก้**

```text
NAME         READY   STATUS                       RESTARTS   AGE
config-pod   0/1     CreateContainerConfigError   0          8s

Events:
  Warning  Failed  0s (x2 over 1s)  kubelet  spec.containers{busybox}: Error: configmap "shop-config" not found
```

<details>
<summary>แนวคำตอบ</summary>

Pod อ้าง ConfigMap `shop-config` ที่ยังไม่มีในคลัสเตอร์ (apply Pod ก่อนแฟ้ม หรือชื่อ/namespace ไม่ตรง) แก้โดย `kubectl apply -f` ไฟล์ ConfigMap ไม่ต้องลบ Pod kubelet ลองใหม่เองแล้ว Pod เดิมจะ `Running` (LAB 1)
</details>

**5. ใน LAB 1 หลัง apply `shop-config-v2.yaml` แล้ว `describe configmap` ขึ้น `วันนี้ลด 20%` แต่ `printenv ANNOUNCEMENT` ใน `config-pod` ยังเป็น `วันนี้ลด 10%` เพราะอะไร แก้อย่างไร**

<details>
<summary>แนวคำตอบ</summary>

env ถูกใส่ให้โปรแกรมครั้งเดียวตอน container เริ่ม แก้แฟ้มทีหลัง Pod เดิมไม่รู้ ต้องได้ container ใหม่: Pod เดี่ยวลบแล้ว apply ใหม่ (LAB 1 ได้ `20%`) ถ้าเป็น Deployment ใช้ `kubectl rollout restart`
</details>

**6. ใน LAB 2 แก้ `index.html` ใน ConfigMap แล้วหน้าเว็บเปลี่ยนเองโดย Pod ไม่ restart แต่ใน LAB 4 แก้ `ANNOUNCEMENT` แล้วประกาศไม่เปลี่ยน ต่างกันตรงไหน**

<details>
<summary>แนวคำตอบ</summary>

`index.html` ถูก mount เป็น **ไฟล์** kubelet เขียนไฟล์ใหม่ให้เองราว 1 นาที และ nginx อ่านไฟล์ใหม่ทุกครั้ง ส่วน `ANNOUNCEMENT` เป็น **env** อ่านครั้งเดียวตอนเริ่ม ต้อง `rollout restart` จึงเห็นค่าใหม่
</details>

**7. เพื่อนบอกว่า "Secret ปลอดภัย เพราะ `kubectl get secret -o yaml` เห็นแค่ `bWVvdy0xMjM0` อ่านไม่ออก" ถูกไหม มีจุดไหนในผลเดียวกันที่เห็นรหัสจริง**

<details>
<summary>แนวคำตอบ</summary>

ไม่ถูก base64 ไม่ใช่การเข้ารหัส แปลงกลับเป็น `meow-1234` ได้ทันทีโดยไม่ต้องมีกุญแจ และในผล `-o yaml` เดียวกันมี annotation `kubectl.kubernetes.io/last-applied-configuration` ที่จด `stringData` ไว้ เห็น `meow-1234` ตรง ๆ ความปลอดภัยจริงมาจากการคุมสิทธิ์ว่าใครอ่าน Secret ได้ (RBAC) และไม่เก็บรหัสจริงใน Git
</details>

**8. ทำไม LAB 4 ให้ apply ไฟล์ใน `som-menu/k8s/` ทีละไฟล์ แทนที่จะสั่ง `kubectl apply -f som-menu/k8s/` ครั้งเดียว**

<details>
<summary>แนวคำตอบ</summary>

ในโฟลเดอร์มีทั้ง `som-menu-config.yaml` และ `som-menu-config-v2.yaml` ที่ใช้ชื่อ ConfigMap เดียวกัน apply ทั้งโฟลเดอร์ทั้ง 2 รุ่นจะทับกันเอง ได้ค่าที่ไม่ได้ตั้งใจ และอยากให้แฟ้มกับซองถูกสร้างก่อน Deployment ด้วย
</details>

**9. หลัง `kubectl rollout restart deployment/som-menu` Pod เปลี่ยนจาก `som-menu-895b459c4-...` เป็น `som-menu-7879c9f754-...` ทั้งที่ไม่ได้แก้ YAML ของ Deployment เลย เกิดอะไรขึ้น**

<details>
<summary>แนวคำตอบ</summary>

`rollout restart` แปะเวลาที่สั่งเป็น annotation ในแม่พิมพ์ให้เอง แม่พิมพ์เปลี่ยน → pod-template-hash ใหม่ (`7879c9f754`) → ReplicaSet ใหม่ แล้ว Deployment ทยอยเปลี่ยน Pod แบบ rolling update เหมือนบทที่ 4 Pod ใหม่จึงอ่าน env จาก ConfigMap ล่าสุด
</details>

**10. แอปตัวหนึ่งอ่านไฟล์ตั้งค่าจาก ConfigMap ที่ mount เป็นไฟล์ แต่อ่านครั้งเดียวตอนเริ่มแล้วเก็บไว้ในหน่วยความจำ แก้ ConfigMap แล้วรอ 2 นาที แอปจะเห็นค่าใหม่ไหม**

<details>
<summary>แนวคำตอบ</summary>

ไม่เห็น ไฟล์ใน container เปลี่ยนแล้วจริง (kubelet เขียนให้) แต่แอปไม่ได้เปิดไฟล์อ่านใหม่ ต้อง `rollout restart` เหมือน env ต่างจากร้านน้องส้มที่ `readMenu()` อ่านไฟล์ใหม่ทุกครั้งที่มีลูกค้า
</details>

---

## เอกสารอ้างอิง

- Kubernetes Docs: [ConfigMaps](https://kubernetes.io/docs/concepts/configuration/configmap/) · [Secrets](https://kubernetes.io/docs/concepts/configuration/secret/) · [Good practices for Kubernetes Secrets](https://kubernetes.io/docs/concepts/security/secrets-good-practices/)
- [Configure a Pod to Use a ConfigMap](https://kubernetes.io/docs/tasks/configure-pod-container/configure-pod-configmap/) · [kubectl rollout restart](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_rollout/kubectl_rollout_restart/)

> ภาพประกอบในโฟลเดอร์ [`images/`](images/) สร้างด้วย AI เพื่อการเรียนการสอน (prompt อยู่ใน [`images/imagegen-prompts.md`](images/imagegen-prompts.md)) ผลลัพธ์คำสั่งมาจาก LAB จริงบน kind v0.33.0 / Kubernetes v1.37.0 (ทดลอง 18 ต.ค. 2569) ชื่อ Pod และเวลาที่ไฟล์จาก ConfigMap อัปเดตในเครื่องผู้เรียนจะต่างกัน รหัสผ่านทุกตัวในบทนี้เป็นรหัสตัวอย่าง
