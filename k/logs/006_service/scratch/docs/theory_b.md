## 6. NodePort: ประตูหมายเลขเดียวกันบนทุกเรือ

### 6.1 แนวคิด

{{FIG:T13}}

ClusterIP ใช้ได้เฉพาะ **ภายในคลัสเตอร์** (Pod กับ Pod) ถ้าต้องการให้ลูกค้านอกคลัสเตอร์เข้าถึง วิธีที่ง่ายที่สุดคือ `type: NodePort` ซึ่งทำ 2 อย่าง

1. สร้าง ClusterIP ตามปกติ (NodePort = ClusterIP + ประตู)
2. เปิดพอร์ตหมายเลขเดียวกัน (**nodePort**) บน **ทุก Node** รวมถึง control plane แพ็กเก็ตที่เข้าประตูนี้ของ Node ไหนก็ตามจะถูกส่งต่อไปยัง Pod ที่พร้อมตัวใดก็ได้ แม้ Pod นั้นจะอยู่บนเรือลำอื่น

ไฟล์ `labs/lab08-nodeport/web-nodeport.yaml`

```yaml
# LAB 8: NodePort 30080 → เปิดประตูหมายเลข 30080 บน "ทุก Node"
# kind ของ k8s-lab map พอร์ต 30080 ของเครื่องนักศึกษา → lab-control-plane:30080 (extraPortMappings บท 001)
# → เปิด http://localhost:30080 จาก browser ได้เลย
apiVersion: v1
kind: Service
metadata:
  name: web-nodeport
  namespace: shop
spec:
  type: NodePort
  selector:
    app: web
  ports:
    - port: 80             # ClusterIP:80 (ภายในคลัสเตอร์)
      targetPort: http     # → Pod:80
      nodePort: 30080      # ทุก Node:30080 (ช่วงที่ใช้ได้ 30000–32767)
```

ผลจริงจาก LAB 8: `PORT(S)` แสดงเป็น `<port>:<nodePort>/TCP` และทั้ง 3 Node ตอบที่พอร์ต 30080 (แม้ `lab-control-plane` จะไม่มี Pod `web` อยู่เลย)

```text
NAME           TYPE       CLUSTER-IP     EXTERNAL-IP   PORT(S)        AGE
web-nodeport   NodePort   10.96.39.125   <none>        80:30080/TCP   0s

lab-control-plane: web v1 from web-k2nk5
lab-worker: web v1 from web-k2nk5
lab-worker2: web v1 from web-mgz49
```

### 6.2 เส้นทางของ http://localhost:30080 จากเครื่องนักศึกษา

{{FIG:T14}}

บทที่ 2–5 เราเปิดหน้าร้านด้วย `kubectl port-forward` + `ssh -L` บทนี้เป็น **บทแรกที่เปิดร้านจาก browser ด้วย `http://localhost:30080` ได้ตรง ๆ** เพราะทางเดินของพอร์ต 30080 ถูกเตรียมไว้ตั้งแต่บทที่ 1 แล้ว 3 ชั้น

| ชั้น | ใครเปิดไว้ | หลักฐาน |
|---|---|---|
| 1. เครื่องนักศึกษา `localhost:30080` → container `k8s-lab:30080` | `docker run ... -p 30080-30082:30080-30082 ...` ตอนสร้าง k8s-lab ในบทที่ 1 | คำสั่ง `docker run` ใน LAB บทที่ 1 |
| 2. `k8s-lab:30080` → container `lab-control-plane:30080` | kind `extraPortMappings` ในไฟล์ `/etc/devtools/kind/kind-lab.yaml` ที่ `k8s-up` ใช้ | `docker ps` ใน k8s-lab เห็น `lab-control-plane  0.0.0.0:30080-30082->30080-30082/tcp` |
| 3. `lab-control-plane:30080` → Pod | NodePort ของ Service + kube-proxy บน control plane | `kubectl get svc` เห็น `80:30080/TCP` |

ส่วนของไฟล์ `kind-lab.yaml` (ผลจริงจาก `cat /etc/devtools/kind/kind-lab.yaml` ใน LAB 0 ตัดบางส่วน)

```yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: lab
nodes:
  - role: control-plane
    extraPortMappings:
      - containerPort: 30080
        hostPort: 30080
        listenAddress: "0.0.0.0"
        protocol: TCP
      - containerPort: 30081
        hostPort: 30081
        listenAddress: "0.0.0.0"
        protocol: TCP
      - containerPort: 30082
        hostPort: 30082
        listenAddress: "0.0.0.0"
        protocol: TCP
  - role: worker
  - role: worker
```

ข้อสังเกต

- พอร์ตที่ map ออกมามีแค่ **30080, 30081, 30082** และ map เข้า **control plane เท่านั้น** ถ้าตั้ง nodePort เป็นเลขอื่น (เช่น 31841 ที่ระบบสุ่ม) Service ยังทำงานภายในคลัสเตอร์ แต่เปิดจาก browser บนเครื่องนักศึกษาไม่ได้
- control plane ไม่มี Pod ของเรา (มี taint `NoSchedule`) แต่ kube-proxy บน control plane ยังส่งต่อแพ็กเก็ตข้ามเรือไปหา Pod บน `lab-worker`/`lab-worker2` ได้ นี่คือความหมายของ "เข้าทางประตูของ Node ไหนก็ถึงบูธได้ทุกบูธ"
- ในการทดลอง เราเปิดหน้าร้านจากนอก container ผ่านเส้นทางเดียวกันนี้ได้ทั้ง curl และ browser แต่ **ยังไม่ได้ยืนยันบนเครื่อง Windows + Docker Desktop ทุกรุ่น** ถ้าเครื่องนักศึกษาเปิด `localhost:30080` ไม่ได้ ทางสำรองคือ `ssh -p 2223 -L 30080:localhost:30080 root@localhost` (ดู Troubleshooting ของ LAB)

### 6.3 กติกาของ NodePort

{{FIG:T15}}

| กติกา | ผลจริงเมื่อฝ่าฝืน (LAB 8) |
|---|---|
| nodePort ต้องอยู่ในช่วง **30000–32767** (ค่าเริ่มต้นของ API server) | `error: failed to create NodePort service: Service "bad" is invalid: spec.ports[0].nodePort: Invalid value: 29999: provided port is not in the valid range. The range of valid ports is 30000-32767` |
| เลขเดียวใช้ได้ **Service เดียวทั้งคลัสเตอร์** (ไม่ใช่แค่ใน namespace) | `The Service "web-dup" is invalid: spec.ports[0].nodePort: Invalid value: 30080: provided port is already allocated` |
| ไม่ระบุ nodePort ระบบสุ่มให้ | LoadBalancer ใน LAB 8 ได้ `80:31841/TCP` |

ผลของกติกาข้อ 2 คือ **ต้องลบ `web-nodeport` ของ LAB 8 ก่อนเริ่ม LAB 10** ซึ่งใช้ 30080 กับร้านน้องส้ม และตัวอย่าง `/workspace/examples/web-deployment.yaml` ของบทที่ 1 ก็จอง 30080 เช่นกัน (LAB 0 ตรวจและลบให้)

ข้อจำกัดของ NodePort ในงานจริง

- พอร์ตแปลก (30000+) ลูกค้าต้องพิมพ์เลขพอร์ตเอง
- ลูกค้าต้องรู้ IP ของ Node และถ้า Node นั้นล่มต้องเปลี่ยนไปใช้ Node อื่นเอง
- ไม่มีชื่อโดเมน ไม่มี TLS และ 1 พอร์ตต่อ 1 Service ไม่เหมาะกับหลายเว็บ

งานจริงจึงมักใช้ **LoadBalancer** (หัวข้อ 7) หรือ **Ingress/Gateway** (บทหลัง) ข้างหน้า ส่วน NodePort เหมาะกับ LAB และระบบ on-premise ขนาดเล็ก

---

## 7. LoadBalancer

{{FIG:T16}}

`type: LoadBalancer` = NodePort + ClusterIP + **load balancer ภายนอก** ที่ผู้ให้บริการคลาวด์สร้างให้ ลำดับการทำงานบนคลาวด์คือ

1. API server สร้าง ClusterIP และ nodePort ตามปกติ
2. **cloud-controller-manager** ของผู้ให้บริการเห็น Service ชนิดนี้ จึงสร้าง load balancer จริง (มี IP สาธารณะหรือชื่อโดเมน) ชี้เข้า nodePort ของทุก Node
3. controller เขียนที่อยู่ภายนอกลง `status.loadBalancer.ingress` ซึ่ง `kubectl get svc` แสดงในคอลัมน์ `EXTERNAL-IP`

ไฟล์ `labs/lab08-nodeport/web-lb.yaml`

```yaml
# LAB 8: LoadBalancer — บนคลาวด์จะได้ IP สาธารณะ ส่วน kind ไม่มีผู้จัดสรร → EXTERNAL-IP <pending>
# (แต่ยังได้ ClusterIP + nodePort แบบสุ่มให้)
apiVersion: v1
kind: Service
metadata:
  name: web-lb
  namespace: shop
spec:
  type: LoadBalancer
  selector:
    app: web
  ports:
    - port: 80
      targetPort: http
```

kind ไม่มี cloud-controller-manager จึงไม่มีใครจัดสรร IP ภายนอก ผลจริงจาก LAB 8 หลังรอ 5 วินาที

```text
NAME     TYPE           CLUSTER-IP     EXTERNAL-IP   PORT(S)        AGE
web-lb   LoadBalancer   10.96.28.238   <pending>     80:31841/TCP   5s
```

`<pending>` จะค้างอย่างนั้นตลอด แต่ Service ยังใช้ได้ทั้งทาง ClusterIP และ nodePort ที่สุ่มได้ (31841 ในการทดลอง, 30456 ในการตรวจก่อนเขียนบท ทุกครั้งต่างกัน) ถ้าต้องการทดลอง LoadBalancer บน kind จริง มีเครื่องมือเสริม เช่น **cloud-provider-kind** หรือ **MetalLB** ที่ทำหน้าที่จัดสรร IP ให้ (นอกขอบเขตของบทนี้)

---

## 8. ExternalName และ headless Service

### 8.1 ExternalName: ชื่อแฝงไปนอกคลัสเตอร์

{{FIG:T17}}

`type: ExternalName` เป็น Service ที่ **ไม่มี selector ไม่มี ClusterIP และไม่ผ่าน kube-proxy** DNS ของคลัสเตอร์แค่ตอบเป็น **CNAME** ไปยังชื่อที่กำหนด ไฟล์ `labs/lab09-cross-ns/supplier-externalname.yaml`

```yaml
# LAB 9: ExternalName — ชื่อในคลัสเตอร์ (supplier.shop) ที่ DNS ตอบเป็น CNAME ไปชื่อภายนอก
# ไม่มี selector / ClusterIP / kube-proxy
apiVersion: v1
kind: Service
metadata:
  name: supplier
  namespace: shop
spec:
  type: ExternalName
  externalName: example.com
```

ผลจริงจาก LAB 9

```text
$ kubectl -n shop get svc
NAME           TYPE           CLUSTER-IP      EXTERNAL-IP   PORT(S)           AGE
supplier       ExternalName   <none>          example.com   <none>            17s
...

$ kubectl -n kitchen exec cook -- nslookup supplier.shop.svc.cluster.local
Server:		10.96.0.10
Address:	10.96.0.10:53

supplier.shop.svc.cluster.local	canonical name = example.com
Name:	example.com
Address: 172.66.147.243
...
```

ประโยชน์คือแอปในคลัสเตอร์เรียกชื่อภายใน (`supplier`) ได้เสมอ วันหนึ่งถ้าซัพพลายเออร์ย้ายเข้าคลัสเตอร์ ก็เปลี่ยน Service เป็นชนิดอื่นโดยไม่ต้องแก้แอป

**ข้อควรระวัง:** ExternalName เปลี่ยนแค่ "ชื่อที่ DNS ตอบ" แต่ client ยังส่ง HTTP `Host` header เป็นชื่อเดิม (`supplier.shop`) และ TLS ก็ตรวจใบรับรองกับชื่อเดิม ปลายทางที่แยกเว็บไซต์ด้วย Host header จึงอาจปฏิเสธ ผลจริงจาก LAB 9

```text
$ kubectl -n kitchen exec cook -- wget -qO- -T 3 http://supplier.shop
wget: server returned error: HTTP/1.1 409 Conflict
command terminated with exit code 1
```

DNS ใช้ได้ (ได้ CNAME และ A record) แต่ปลายทางตอบ `409 Conflict` เพราะไม่รู้จัก Host `supplier.shop` ถ้าเครื่องไม่มีอินเทอร์เน็ต `nslookup` จะยังเห็นบรรทัด `canonical name = example.com` แต่ไม่ได้ A record

### 8.2 headless Service: สมุดรายชื่อบูธ

{{FIG:T18}}

headless Service คือ Service ที่ตั้ง `clusterIP: None` จึง **ไม่มี IP กลางและ kube-proxy ไม่กระจายให้** แต่ยังมี selector และ EndpointSlice ตามปกติ DNS ของคลัสเตอร์ตอบ **A record ของทุก Pod ที่ ready** ให้ client เลือกเอง ไฟล์ `labs/lab09-cross-ns/web-headless.yaml`

```yaml
# LAB 9: headless Service (clusterIP: None) — ไม่มี IP กลาง
# DNS คืน IP ของทุก Pod ที่ Ready (สมุดรายชื่อบูธ) และ kube-proxy ไม่กระจายให้
apiVersion: v1
kind: Service
metadata:
  name: web-headless
  namespace: shop
spec:
  clusterIP: None
  selector:
    app: web
  ports:
    - port: 80
      targetPort: http
```

ผลจริงจาก LAB 9 เทียบ headless กับ Service ปกติ

```text
$ kubectl -n kitchen exec cook -- nslookup web-headless.shop.svc.cluster.local
...
Name:	web-headless.shop.svc.cluster.local
Address: 10.244.1.4
Name:	web-headless.shop.svc.cluster.local
Address: 10.244.2.6
Name:	web-headless.shop.svc.cluster.local
Address: 10.244.1.5

$ kubectl -n kitchen exec cook -- nslookup web.shop.svc.cluster.local
...
Name:	web.shop.svc.cluster.local
Address: 10.96.55.132
```

`get svc` แสดง `web-headless   ClusterIP   None   <none>   80/TCP` (ชนิดยังเป็น ClusterIP แต่ค่า IP เป็น `None`)

headless เหมาะกับงานที่ client ต้องรู้จัก Pod **รายตัว** เช่น ฐานข้อมูลที่มีหลายตัวแบบตัวหลัก/ตัวสำรอง หรือระบบที่ client ทำ load balancing เอง (เนื้อหาบทหลัง) ส่วนเว็บทั่วไปควรใช้ Service ปกติ

---

## 9. DNS ของ Service

### 9.1 ชื่อเต็มและการเรียกข้าม namespace

{{FIG:T19}}

CoreDNS (Service `kube-dns` ที่ `10.96.0.10`) สร้างระเบียน DNS ให้ทุก Service อัตโนมัติ

| ระเบียน | รูปแบบ | ตอบอะไร |
|---|---|---|
| A ของ Service ปกติ | `<svc>.<ns>.svc.cluster.local` | ClusterIP เช่น `web.shop.svc.cluster.local` → `10.96.55.132` |
| A ของ headless | `<svc>.<ns>.svc.cluster.local` | IP ของทุก Pod ที่ ready |
| CNAME ของ ExternalName | `<svc>.<ns>.svc.cluster.local` | ชื่อภายนอก เช่น `example.com` |
| SRV ของพอร์ตที่มีชื่อ | `_<ชื่อพอร์ต>._<protocol>.<svc>.<ns>.svc.cluster.local` | เลขพอร์ต + ชื่อ เช่น `_http._tcp.web-multi.shop.svc.cluster.local` (กล่าวถึง ไม่มีใน LAB) |

วิธีเรียกชื่อจาก Pod

| เรียกจาก | ชื่อที่ใช้ได้ | ผลจริง |
|---|---|---|
| namespace เดียวกัน (`shop`) | `web`, `web.shop`, `web.shop.svc.cluster.local` | LAB 2–5 ใช้ `http://web` |
| namespace อื่น (`kitchen`) | `web.shop` หรือชื่อเต็ม **ไม่ใช่** `web` | `wget http://web` → `wget: bad address 'web'` แต่ `http://web.shop` และชื่อเต็มได้หน้าเว็บ (LAB 9) |
| ที่ไหนก็ได้ | ชื่อเต็มลงท้ายจุด `web.shop.svc.cluster.local.` | ข้ามการเติม search domain ทั้งหมด (LAB 4 ได้ `web v1 from web-k2nk5`) |

### 9.2 resolv.conf: search domain และ ndots

{{FIG:T20}}

ทำไมชื่อสั้น `web` จึงใช้ได้ในโซนเดียวกัน คำตอบอยู่ที่ `/etc/resolv.conf` ที่ kubelet เขียนให้ทุก Pod (ต่อจากบทที่ 4) ผลจริงจาก LAB 4 (Pod ใน `shop`) และ LAB 9 (Pod ใน `kitchen`)

```text
$ kubectl -n shop exec client -- cat /etc/resolv.conf
search shop.svc.cluster.local svc.cluster.local cluster.local
nameserver 10.96.0.10
options ndots:5

$ kubectl -n kitchen exec cook -- cat /etc/resolv.conf
search kitchen.svc.cluster.local svc.cluster.local cluster.local
nameserver 10.96.0.10
options ndots:5
```

- **`nameserver 10.96.0.10`** = ClusterIP ของ `kube-dns`
- **`search`** = รายการโดเมนที่จะเติมต่อท้ายชื่อ ตัวแรกคือ namespace ของ Pod เอง
- **`options ndots:5`** = ชื่อที่มีจุด **น้อยกว่า 5 จุด** จะถูกลองเติม search domain ทีละตัวก่อน แล้วค่อยถามชื่อตามที่พิมพ์

ดังนั้นใน Pod ของ `shop` ชื่อ `web` (0 จุด) จะถูกลองเป็น `web.shop.svc.cluster.local` ก่อน (เจอ) ส่วนชื่อ `web.shop` (1 จุด) จะได้ `web.shop.shop.svc.cluster.local` (ไม่เจอ) → `web.shop.svc.cluster.local` (เจอ) นี่คือเหตุผลที่ `web.shop` ใช้ได้จากทุกโซน ทั้งที่ `shop` ไม่ใช่โดเมนจริงบนอินเทอร์เน็ต ส่วน Pod ใน `kitchen` เรียก `web` แล้วได้ `web.kitchen.svc.cluster.local` ซึ่งไม่มี จึงเป็น `bad address`

ผลข้างเคียงของ `ndots:5` คือชื่อภายนอก เช่น `example.com` (1 จุด) จะถูกลองเติม search 3 รอบก่อนถามชื่อจริง ทำให้เกิดคำถาม DNS ที่ไม่จำเป็น ถ้าต้องการลดให้ใช้ชื่อเต็มลงท้ายจุด (`example.com.`)

**กับดักของ `nslookup` ใน busybox** (Pod `client`/`cook` ใช้ image `busybox:1.36`) ผลจริงจาก LAB 4

```text
$ kubectl -n shop exec client -- nslookup web
Server:		10.96.0.10
Address:	10.96.0.10:53

** server can't find web.cluster.local: NXDOMAIN

** server can't find web.cluster.local: NXDOMAIN

** server can't find web.svc.cluster.local: NXDOMAIN


Name:	web.shop.svc.cluster.local
Address: 10.96.55.132

** server can't find web.svc.cluster.local: NXDOMAIN

command terminated with exit code 1

$ kubectl -n shop exec client -- nslookup web.shop
...
** server can't find web.shop: NXDOMAIN
...
command terminated with exit code 1

$ kubectl -n shop exec client -- wget -qO- http://web.shop
web v1 from web-k2nk5
```

- `nslookup web` **หาเจอ** (`web.shop.svc.cluster.local → 10.96.55.132`) แต่เพราะ busybox ถามทุก search domain พร้อมกันแล้วพิมพ์ผลทุกตัว จึงมีบรรทัด `NXDOMAIN` ของโดเมนที่ไม่ตรงปน และจบด้วย exit code 1
- `nslookup web.shop` ได้ NXDOMAIN เพราะ `nslookup` ของ busybox ไม่เติม search domain ให้ชื่อที่มีจุด ทั้งที่ `wget http://web.shop` (ซึ่งใช้ resolver ปกติของระบบ) ใช้ได้
- **สรุป:** ทดสอบ DNS ด้วย `nslookup` ของ busybox ให้ใช้ **ชื่อเต็ม** `<svc>.<ns>.svc.cluster.local` เสมอ และทดสอบ "แอปเรียกได้จริงไหม" ด้วย `wget`

### 9.3 env var ของ Service

{{FIG:T21}}

นอกจาก DNS แล้ว kubelet ยังใส่ env var ของ Service ให้ Pod ด้วย (รูปแบบเดียวกับ docker link ยุคเก่า) ชื่อ Service ถูกแปลงเป็นตัวพิมพ์ใหญ่และ `-` เป็น `_` แต่มีเงื่อนไขสำคัญ 2 ข้อ

1. ใส่ให้เฉพาะ Pod ที่ **ถูกสร้างหลัง Service** (env ของ container ตั้งครั้งเดียวตอนเริ่ม)
2. ใส่ให้เฉพาะ Service ใน **namespace เดียวกัน** (และ Service `kubernetes` ของ `default`)

ผลจริงจาก LAB 4: `client` สร้างใน LAB 1 ก่อนมี Service จึงไม่มี env ของ `web` เลย ส่วน `client2` สร้างหลัง Service `web`, `web-alt`, `web-multi`

```text
$ kubectl -n shop exec client -- env | grep WEB_; echo "exit=$?"
exit=1

$ kubectl -n shop exec client2 -- env | grep WEB_ | sort
WEB_ALT_PORT=tcp://10.96.141.242:8080
...
WEB_ALT_SERVICE_HOST=10.96.141.242
WEB_ALT_SERVICE_PORT=8080
...
WEB_MULTI_SERVICE_HOST=10.96.28.97
WEB_MULTI_SERVICE_PORT=80
WEB_MULTI_SERVICE_PORT_ALT=8080
WEB_MULTI_SERVICE_PORT_HTTP=80
WEB_PORT=tcp://10.96.55.132:80
...
WEB_SERVICE_HOST=10.96.55.132
WEB_SERVICE_PORT=80
```

`WEB_MULTI_SERVICE_PORT_HTTP` และ `_ALT` มีเพราะพอร์ตของ `web-multi` มีชื่อ ส่วน `web` ไม่มี `WEB_SERVICE_PORT_HTTP` เพราะพอร์ตของ Service `web` ไม่ได้ตั้งชื่อ (ชื่อ `http` เป็นของ containerPort ไม่ใช่ของ Service)

เพราะลำดับการสร้างมีผลแบบนี้ **ควรใช้ DNS แทน env var** ถ้าไม่ต้องการ env เหล่านี้เลย (เช่น namespace ที่มี Service หลายร้อยตัวทำให้ env ยาวมาก) ปิดได้ด้วย

```yaml
spec:
  enableServiceLinks: false   # ไม่ใส่ env ของ Service อื่นให้ Pod นี้ (env ของ kubernetes ยังมี)
```

---

## 10. kube-proxy: ป้ายบอกทางบนเรือทุกลำ

### 10.1 kube-proxy แปลงปลายทางที่เรือต้นทาง

{{FIG:T22}}

**kube-proxy** คือโปรแกรมที่ทำให้ ClusterIP "ใช้ได้จริง" มันรันบน **ทุก Node** แล้วเขียนกฎในเคอร์เนลของ Node นั้น เมื่อ Pod ส่งแพ็กเก็ตไป `10.96.55.132:80` เคอร์เนลของ **Node ต้นทาง** จะเปลี่ยนปลายทางเป็น IP ของ Pod ตัวหนึ่ง เช่น `10.244.2.6:80` (เรียกว่า **DNAT** – Destination NAT) ก่อนแพ็กเก็ตออกจากเรือ จากนั้นแพ็กเก็ตเดินทางแบบ Pod-to-Pod ตามปกติ

ผลที่ตามมา

- ไม่มี "เครื่องประภาคาร" จริงที่แพ็กเก็ตต้องผ่าน จึงไม่มีคอขวดกลาง และ Service ไม่ล่มเพราะเครื่องใดเครื่องหนึ่งล่ม
- การตัดสินใจว่าจะไป Pod ไหนเกิดที่ Node ต้นทางทุกครั้งที่เปิด connection ใหม่ (หัวข้อ 11)
- NetworkPolicy ที่ Pod ปลายทางเห็นพอร์ตที่แปลงแล้ว (หัวข้อ 14)

### 10.2 kube-proxy เป็น DaemonSet ที่ watch API

{{FIG:T23}}

kube-proxy ถูกติดตั้งเป็น **DaemonSet** ใน `kube-system` (1 Pod ต่อ Node) ผลจริงจาก LAB 0

```text
$ kubectl -n kube-system get ds kube-proxy
NAME         DESIRED   CURRENT   READY   UP-TO-DATE   AVAILABLE   NODE SELECTOR            AGE
kube-proxy   3         3         3       3            3           kubernetes.io/os=linux   4m56s

$ kubectl -n kube-system get cm kube-proxy -o yaml | grep mode
    mode: iptables
```

kube-proxy แต่ละตัว **watch Service และ EndpointSlice** จาก API server (ไม่ได้ watch Pod โดยตรง) เมื่อรายชื่อเปลี่ยนก็เขียนกฎใหม่ ช่วงเวลาสั้น ๆ ระหว่าง "EndpointSlice เปลี่ยน" กับ "kube-proxy ทุก Node เขียนกฎเสร็จ" คือที่มาของอาการที่เห็นใน LAB เช่น Service ที่เพิ่งสร้างตอบ `Connection refused` ใน ~1 วินาทีแรก หรือ NodePort ที่เพิ่งลบยังตอบได้อีก ~1 วินาที

| โหมด | กลไก | หมายเหตุ |
|---|---|---|
| **iptables** | chain ของ iptables ต่อ Service (`KUBE-SVC-...`) และต่อ endpoint (`KUBE-SEP-...`) เลือก endpoint ด้วยความน่าจะเป็น (`--probability`) | โหมดที่ kind ของเราใช้ |
| **nftables** | กฎ nftables ซึ่งเป็นระบบใหม่ที่มาแทน iptables ใน Linux ขยายได้ดีกว่าเมื่อมี Service จำนวนมาก | GA ตั้งแต่ Kubernetes v1.33 |
| **ipvs** | ใช้ IPVS ของเคอร์เนล มีอัลกอริทึมกระจายโหลดให้เลือก | โหมดทางเลือกที่ใช้ในบางคลัสเตอร์ |

(ทางเลือก ไม่บังคับ) ผู้ที่อยากเห็นกฎจริงลองสั่งใน k8s-lab ขณะที่มี Service `web` ใน `shop` อยู่: `docker exec lab-worker iptables-save | grep 'shop/web'` จะเห็นบรรทัดที่อ้าง chain `KUBE-SVC-...`/`KUBE-SEP-...` (เอกสารนี้ไม่ได้แสดงผล เพราะชื่อ chain ต่างกันทุกคลัสเตอร์)

---

## 11. การกระจายโหลด

### 11.1 สุ่มต่อ connection ไม่ใช่วนตามลำดับ

{{FIG:T24}}

ในโหมด iptables kube-proxy เลือก endpoint **แบบสุ่มต่อ connection** ไม่ใช่ round-robin และไม่ใช่ต่อ request การยิงจำนวนน้อยจึงอาจไม่กระจายเลย ผลจากการตรวจก่อนเขียนบท: ยิง ClusterIP 9 ครั้งได้ **5/4/0** (Pod ตัวที่สามไม่ได้สักครั้ง) และยิง NodePort 12 ครั้งได้ 5/5/2 ส่วนผลจริงจาก LAB 5 ยิง 30 ครั้ง (busybox `wget` เปิด connection ใหม่ทุกครั้ง) 2 รอบติดกัน

```text
$ kubectl -n shop exec client -- sh -c 'for i in $(seq 30); do wget -qO- http://web; done' | sort | uniq -c
      4 web v1 from web-gsgss
     14 web v1 from web-k2nk5
     12 web v1 from web-mgz49
$ (รอบที่ 2)
      8 web v1 from web-gsgss
      9 web v1 from web-k2nk5
     13 web v1 from web-mgz49
```

ได้ทุก Pod แต่ไม่เท่ากันและแต่ละรอบต่างกัน ต้องยิงหลายสิบครั้งจึงเห็นภาพรวมว่ากระจายจริง

### 11.2 keep-alive: browser ติดบูธเดิม

{{FIG:T25}}

browser และ HTTP client สมัยใหม่ใช้ **keep-alive** คือเปิด connection เดียวแล้วส่งหลาย request ต่อกัน เนื่องจาก kube-proxy ตัดสินใจ **ตอนเปิด connection** ทุก request ใน connection เดียวกันจึงไปบูธเดิม ผลจริงจาก LAB 8 (Chromium เปิด NodePort 30080 จากนอก container)

| การทดลอง | ผล |
|---|---|
| เปิดหน้า + กด reload 9 ครั้ง (รวม 10) | `web v1 from web-k2nk5` ทั้ง 10 ครั้ง |
| `fetch()` 10 ครั้งในหน้าเดิม | Pod เดียวทั้ง 10 ครั้ง |
| เปิด browser context ใหม่ทุกครั้ง (คล้าย Incognito/ปิดเปิด browser) 5 ครั้ง | 2 ชื่อ (3 + 2) เปลี่ยนได้แต่ยังสุ่ม |
| `curl` หลาย URL ในคำสั่งเดียว (connection เดียว) 10 ครั้ง | Pod เดียว 10/10 และ curl แสดง `Re-using existing connection` |
| `curl` แยกคำสั่ง 30 ครั้ง (connection ใหม่ทุกครั้ง) | `7/8/15` กระจายครบ 3 Pod |

ดังนั้น **refresh browser แล้วเห็นชื่อ Pod เดิม ไม่ได้แปลว่ามี Pod เดียว** ถ้าจะดูการกระจายให้ใช้ `curl`/`wget` วนทีละคำสั่ง (LAB 10 มีสคริปต์ `hit.sh` ที่ทำแบบนี้)

### 11.3 sessionAffinity: บัตรสมาชิก

{{FIG:T26}}

บางแอปต้องการให้ลูกค้าคนเดิมไปบูธเดิม (เช่น เก็บตะกร้าสินค้าไว้ในหน่วยความจำของ Pod) ตั้งได้ด้วย

```yaml
spec:
  sessionAffinity: ClientIP
  sessionAffinityConfig:
    clientIP:
      timeoutSeconds: 10800   # ค่าเริ่มต้น 3 ชั่วโมง
```

ผลจริงจาก LAB 5 (`kubectl patch` เปลี่ยนเป็น `ClientIP`): ลูกค้า `client` ไป `web-k2nk5` ครบ 30/30 ส่วน `client2` (คนละ IP) ไป `web-mgz49` ครบ 30/30 และค่าเริ่มต้นที่ API เติมให้คือ `{"clientIP":{"timeoutSeconds":10800}}` เมื่อ patch กลับเป็น `None` ฟิลด์ `sessionAffinityConfig` หายไปเองและการกระจายกลับมา (`9/11/10`)

ข้อเสียของ `ClientIP`: ลูกค้าหลายคนที่อยู่หลังเครื่อง NAT เดียวกัน (เช่น ทั้งมหาวิทยาลัยออกอินเทอร์เน็ตด้วย IP เดียว) จะไปบูธเดียวกันหมด และถ้าบูธนั้นหายไปลูกค้าก็ต้องย้ายอยู่ดี ทางที่ดีกว่าคือเก็บ session ไว้นอก Pod (ฐานข้อมูล/แคช) แล้วปล่อยให้กระจายตามปกติ

**ข้อควรรู้เพิ่มเติม (ไม่มีใน LAB):**

- `externalTrafficPolicy: Local` (สำหรับ NodePort/LoadBalancer) ส่งลูกค้าที่เข้าประตูของ Node ไหน ไปเฉพาะ Pod บน Node นั้น ข้อดีคือรักษา IP ต้นทางของลูกค้าไว้และไม่ข้ามเรือ ข้อเสียคือ Node ที่ไม่มี Pod จะไม่รับลูกค้า (ในคลัสเตอร์ของเรา NodePort เข้าทาง control plane ที่ไม่มี Pod จึงห้ามใช้)
- `internalTrafficPolicy: Local` ทำแบบเดียวกันสำหรับลูกค้าในคลัสเตอร์ (ค่าเริ่มต้นของทั้งสองคือ `Cluster`)

---

