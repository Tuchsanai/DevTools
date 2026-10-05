import json
items = json.load(open('005-items.json'))
orig = {x['id']: x for x in items}
P = {}

def keep(i):
    P[i] = {'labels': orig[i]['labels'], 'extra': orig[i]['extra']}

def put(i, labels, extra, **kw):
    P[i] = {'labels': labels, 'extra': extra, **kw}

put('T01', ["บทที่ 5", "หายแล้วต้องสร้างเอง", "10.244.1.7", "10.244.3.9", "port-forward"],
    "'บทที่ 5' is a title banner at the top; 'หายแล้วต้องสร้างเอง' is a smaller subtitle line directly under the title banner; '10.244.1.7' is the IP tag on the fading old booth; '10.244.3.9' is the IP tag on the new booth; 'port-forward' is a small tag on the snapped cable; the peeking robot has no text")
keep('T02')
put('T03', ["อุปมาของบทนี้", "ReplicaSet", "Pod template", "selector", "ownerReferences", "ตัวควบคุม (controller)"],
    "'อุปมาของบทนี้' is the title at the top of the legend board; below it exactly five rows and each row has exactly one of the other five labels in the order listed ('ReplicaSet', 'Pod template', 'selector', 'ownerReferences', 'ตัวควบคุม (controller)'); the icons have no text")
put('T04', ["ต้องการ 3", "มีจริง 2", "สังเกต", "เทียบ", "ลงมือ"],
    "'ต้องการ 3' on the wish card; 'มีจริง 2' under the ship; 'สังเกต', 'เทียบ', 'ลงมือ' each on one of the three arrow segments in clockwise order; no other text")
put('T05', ["kube-controller-manager", "kube-apiserver", "ReplicaSet controller", "Node controller", "Namespace controller", "สั่งงานผ่าน API เท่านั้น"],
    "the three robots each wear exactly one of the three controller labels ('ReplicaSet controller', 'Node controller', 'Namespace controller') on a desk name plate; 'kube-controller-manager' on the office door; 'kube-apiserver' on the central API desk; 'สั่งงานผ่าน API เท่านั้น' on a small sign hanging on the arrow from the API desk to the ships")
put('T06', ["แจ้งเตือน (watch)", "ดูสถานะปัจจุบันเสมอ (level-triggered)", "ต้องการ 3", "มีจริง 2"],
    "'แจ้งเตือน (watch)' on the missed news ticket on the left; 'ดูสถานะปัจจุบันเสมอ (level-triggered)' as the heading above the right part; 'ต้องการ 3' and 'มีจริง 2' as two lines on the robot's clipboard on the right")
put('T07', ["ReplicaSet 3 ส่วน", "replicas: 3", "selector: app=snack", "template", "app=snack"],
    "'ReplicaSet 3 ส่วน' is a title banner at the top; 'replicas: 3' on the clipboard callout; 'selector: app=snack' on the magnifier callout; 'template' on the blueprint callout; 'app=snack' printed once on the blueprint's luggage tag; the three real booth tags are plain matching color with no text")
put('T08', ["อ่าน YAML ของ ReplicaSet", "apiVersion: apps/v1", "kind: ReplicaSet", "replicas: 3", "selector", "template"],
    "'อ่าน YAML ของ ReplicaSet' is a title banner above the YAML card; each of the five bands of the YAML card carries exactly one of the other labels in the listed order top to bottom ('apiVersion: apps/v1', 'kind: ReplicaSet', 'replicas: 3', 'selector', 'template'); the objects on the right have no text")
put('T09', ["ReplicaSet ตั้งชื่อให้", "snack-rs", "snack-rs-4xk9p", "snack-rs-b7tqz", "snack-rs-zm2wd", "name: (none)"],
    "'ReplicaSet ตั้งชื่อให้' is a title banner at the top; 'snack-rs' on the robot's chest plate; the three booth name cards read 'snack-rs-4xk9p', 'snack-rs-b7tqz', 'snack-rs-zm2wd' left to right; 'name: (none)' next to the empty dashed box on the blueprint")
put('T10', ["selector 2 แบบ", "matchLabels", "matchExpressions", "In", "NotIn", "Exists", "DoesNotExist"],
    "'selector 2 แบบ' is a title banner at the top of the panel; 'matchLabels' heads the top section; 'matchExpressions' heads the bottom section; each of the four buttons carries exactly one of 'In', 'NotIn', 'Exists', 'DoesNotExist'")
put('T11', ["selector: app=snack", "app=snak", "selector does not match template labels", "label ไม่ตรง ถูกปฏิเสธ"],
    "'selector: app=snack' on the robot's magnifier; 'app=snak' on the blueprint tag; 'selector does not match template labels' inside the red stamp; 'label ไม่ตรง ถูกปฏิเสธ' is a title banner at the top")
put('T12', ["ownerReferences", "kind: ReplicaSet", "name: snack-rs", "controller: true", "blockOwnerDeletion: true", "ชี้กลับหาเจ้าของ"],
    "'ownerReferences' as the title of the magnified circle; 'kind: ReplicaSet', 'name: snack-rs', 'controller: true', 'blockOwnerDeletion: true' are the four lines inside it in the listed order; 'ชี้กลับหาเจ้าของ' on a small tag hanging on the dotted string to the robot")
put('T13', ["อ่านสถานะ ReplicaSet", "DESIRED 3", "CURRENT 3", "READY 2", "availableReplicas", "fullyLabeledReplicas"],
    "'อ่านสถานะ ReplicaSet' is a title banner at the top; the three scoreboard columns carry 'DESIRED 3', 'CURRENT 3', 'READY 2' left to right; the side card lists 'availableReplicas' and 'fullyLabeledReplicas'; lamps have no text")
put('T14', ["หายแล้วสร้างแทนเอง", "1", "2", "3", "3/3", "2/3", "3/3"],
    "'หายแล้วสร้างแทนเอง' is a title banner at the top; '1','2','3' are step numbers in circles above each step; the clipboard shows '3/3' in step 1, '2/3' in step 2 and '3/3' in step 3")
put('T15', ["ตัวใหม่เกิดทันที", "kubectl delete pod", "Terminating", "Running", "~3 วิ"],
    "'ตัวใหม่เกิดทันที' is a title banner at the top; 'kubectl delete pod' on the red button; 'Terminating' under the old booth; 'Running' under the new booth; '~3 วิ' on the stopwatch")
keep('T16')
put('T17', ["เรือล่มแล้วสร้างแทน", "docker stop lab-worker2", "NotReady ~45 วิ", "tolerationSeconds: 300", "tolerationSeconds: 30", "สร้างแทน ~75 วิ"],
    "'เรือล่มแล้วสร้างแทน' is a title banner at the top; 'docker stop lab-worker2' at the start of the timeline; 'NotReady ~45 วิ' at the grey marker; 'tolerationSeconds: 300' on the long hourglass bar; 'tolerationSeconds: 30' on the short one; 'สร้างแทน ~75 วิ' once as a marker on the timeline at the end of the short hourglass branch, near the newly stamped booth on the healthy ship; the end of the long branch has no text; the timeline has no other numbers",
    caption_th="เรือล่ม (docker stop lab-worker2): Node เป็น NotReady หลังราว 45 วิ แล้ว Pod ต้องรอ tolerationSeconds (ค่าเริ่มต้น 300) ก่อนถูกไล่ RS จึงสร้างแทนบนเรืออื่น ใส่ toleration 30 วิใน template ให้เร็วขึ้นได้ (ตัวแทนเกิดบนเรืออีกลำราว 75 วิหลังเริ่ม stop)")
put('T18', ["scale เพิ่ม/ลดทันที", "--replicas=5", "--replicas=2", "5", "2"],
    "'scale เพิ่ม/ลดทันที' is a title banner at the top; '--replicas=5' above the left scene, '--replicas=2' above the right scene; '5' and '2' are the counts on the dial in each scene")
put('T19', ["ยังไม่ได้วางบนเรือ", "Pending", "ไม่ Ready", "เรือแออัด", "ใหม่กว่า", "ลบก่อน"],
    "booths 1 to 5 carry 'ยังไม่ได้วางบนเรือ', 'Pending', 'ไม่ Ready', 'เรือแออัด', 'ใหม่กว่า' in order left to right; 'ลบก่อน' on the crane hook above booth 1")
put('T20', ["นับจาก label ไม่ใช่ชื่อ", "selector: app=snack", "app=snack", "app=drink"],
    "'นับจาก label ไม่ใช่ชื่อ' is a title banner at the top; 'selector: app=snack' on the flashlight; Nong Som's orange tag reads 'app=snack' and blue tag reads 'app=drink'; the booths' tags are plain colors without text")
put('T21', ["รับเลี้ยง Pod เดิม", "stray", "ownerReferences: snack-rs", "+2", "replicas: 3"],
    "'รับเลี้ยง Pod เดิม' is a title banner at the top; 'stray' is the name card on the lone booth; 'ownerReferences: snack-rs' on the owner badge clipped on it; '+2' near the two new stamped booths; 'replicas: 3' on the robot clipboard")
put('T22', ["เกินมา ลบทิ้งทันที", "4/3", "stray", "Deleted pod: stray"],
    "'เกินมา ลบทิ้งทันที' is a title banner at the top; '4/3' on the robot clipboard in orange; 'stray' name card on the fourth booth; 'Deleted pod: stray' as a small event ticket flying from the robot")
put('T23', ["selector ทับกัน", "rs-a", "rs-b", "selector: app=snack", "selector: app=snack", "ownerReferences"],
    "'selector ทับกัน' is a title banner at the top; 'rs-a' on the left robot's chest plate; 'rs-b' on the right robot's; each robot's magnifier shows one 'selector: app=snack'; 'ownerReferences' once as a callout pointing to one badge; other badges are color only")
put('T24', ["kubectl label pod snack-rs-4xk9p app-", "ตรวจแยก (debug)", "+1"],
    "'kubectl label pod snack-rs-4xk9p app-' on a card in Nong Som's paw; 'ตรวจแยก (debug)' on the inspection bench sign; '+1' near the fresh replacement booth")
put('T25', ["แก้ selector ไม่ได้", "selector", "field is immutable", "apps/v1"],
    "'แก้ selector ไม่ได้' is a title banner at the top; 'selector' on the padlock; 'field is immutable' inside the red stamp; 'apps/v1' on a small plate on the robot's arm")
keep('T26')
put('T27', ["kubectl delete rs snack-rs", "--cascade=background", "--cascade=foreground", "--cascade=orphan", "ลบ RS ก่อน", "ลบ Pod ก่อน", "ทิ้ง Pod ไว้"],
    "'kubectl delete rs snack-rs' as a banner across the top; the three panel headings are '--cascade=background', '--cascade=foreground', '--cascade=orphan' left to right; directly under each heading a short Thai subheading: 'ลบ RS ก่อน' in panel 1, 'ลบ Pod ก่อน' in panel 2, 'ทิ้ง Pod ไว้' in panel 3; never draw waterfalls")
put('T28', ["รับเลี้ยง ไม่สร้างเพิ่ม", "ownerReferences: (none)", "snack-rs", "+0", "replicas: 3"],
    "'รับเลี้ยง ไม่สร้างเพิ่ม' is a title banner at the top; 'ownerReferences: (none)' on a small sign in front of the unbadged booths; 'snack-rs' on the new robot's chest plate; '+0' on the idle stamping machine counter; 'replicas: 3' on the robot's clipboard")
put('T29', ["รุ่นพี่ที่เกษียณแล้ว", "ReplicationController (v1)", "ReplicaSet (apps/v1)", "app=snack", "app in (snack, drink)", "kubectl rolling-update"],
    "'รุ่นพี่ที่เกษียณแล้ว' is a title banner above the old robot; 'ReplicationController (v1)' on the old robot's chest plate; 'ReplicaSet (apps/v1)' on the modern robot's chest plate; 'app=snack' in the old magnifier; 'app in (snack, drink)' in the new magnifier; 'kubectl rolling-update' on the crossed-out remote control; shoulders have no text")
put('T30', ["ติดโควตา pods", "pods: 4", "replicas: 6", "4/6", "FailedCreate: exceeded quota", "ReplicaFailure", "LimitRange"],
    "'ติดโควตา pods' on the zone sign; 'pods: 4' on the gate post; 'replicas: 6' and '4/6' on the robot's clipboard (two lines); 'FailedCreate: exceeded quota' on the alert ticket; 'ReplicaFailure' on a small red flag on the robot's head; 'LimitRange' on the sticker machine; size stickers are color only")
put('T31', ["RS ผ่าน Pod ไม่ผ่าน", "warn", "enforce", "Warning: would violate PodSecurity", "FailedCreate", "0/3"],
    "'RS ผ่าน Pod ไม่ผ่าน' is a title banner at the top; 'warn' on the checkpoint booth at the entrance; 'enforce' on the red barrier arm inside; 'Warning: would violate PodSecurity' on the yellow slip; 'FailedCreate' on a small red ticket at the barrier; '0/3' on the robot's clipboard")
put('T32', ["ห้ามอยู่เรือเดียวกัน", "required", "lab-worker", "lab-worker2", "Pending", "replicas: 3"],
    "'ห้ามอยู่เรือเดียวกัน' is a title banner at the top; 'required' on the magnet symbol; 'lab-worker' and 'lab-worker2' on the two worker ship hulls; 'Pending' on the floating booth; 'replicas: 3' on the robot clipboard; the control tower ship and flag have no text")
put('T33', ["กระจายบูธให้สมดุล", "preferred", "2", "1", "topologySpreadConstraints", "maxSkew: 1"],
    "'กระจายบูธให้สมดุล' is a title banner across the top of both scenes; 'preferred' heads the left scene; '2' and '1' are count badges on the left two ships; 'topologySpreadConstraints' heads the right scene; 'maxSkew: 1' on the balance scale; right ships have no count text",
    caption_th="preferred (กระจายเท่าที่ทำได้ → 3 บูธบน 2 เรือ = 2+1) และ topologySpreadConstraints maxSkew 1 (จำนวนบนแต่ละเรือต่างกันไม่เกิน 1) (ใน kind ต้องใส่ nodeTaintsPolicy: Honor ไม่งั้นนับ control-plane ด้วย)")
put('T34', ["ชื่อใหม่ IP ใหม่", "snack-rs-4xk9p", "10.244.1.12", "snack-rs-q8vnc", "10.244.3.15", "port-forward"],
    "'ชื่อใหม่ IP ใหม่' is a title banner at the top; 'snack-rs-4xk9p' and '10.244.1.12' on the fading old outline (name card and IP tag); 'snack-rs-q8vnc' and '10.244.3.15' on the new booth; 'port-forward' on the snapped cable; the customer's address card has no text")
put('T35', ["สรุปบท ReplicaSet", "replicas", "selector", "template", "ownerReferences", "self-healing", "scale"],
    "'สรุปบท ReplicaSet' is the title at the top of the checklist board; below it exactly six rows, each with exactly one of the other labels in the listed order ('replicas', 'selector', 'template', 'ownerReferences', 'self-healing', 'scale')")
put('T36', ["ข้อมูลไม่ตรงกัน", "IP เปลี่ยน", "เปลี่ยนรุ่นด้วยมือ", "บท 6 Service", "บท 7 Deployment"],
    "the three thought clouds carry 'ข้อมูลไม่ตรงกัน', 'IP เปลี่ยน', 'เปลี่ยนรุ่นด้วยมือ' in order, exactly one each; 'บท 6 Service' hangs from the lighthouse silhouette; 'บท 7 Deployment' hangs from the tall robot silhouette; the silhouettes are shadowy and small")

keep('L01')
put('L02', ["ReplicaSet แรก", "snack-rs", "replicas: 3", "snack-rs-4xk9p", "ownerReferences", "SuccessfulCreate"],
    "'ReplicaSet แรก' is a title banner at the top; 'snack-rs' on the robot's chest plate; 'replicas: 3' on its clipboard; 'snack-rs-4xk9p' on the first booth's name card only (other name cards are color only); 'ownerReferences' on one badge callout; 'SuccessfulCreate' on the event ticket; the rejected blueprint stamp has no text")
put('L03', ["ลบแล้วเกิดใหม่ทันที", "kubectl delete pod", "Terminating", "Running", "kubectl get pods -w"],
    "'ลบแล้วเกิดใหม่ทันที' is a title banner at the top; 'kubectl delete pod' on the red button; 'Terminating' on the old fading booth; 'Running' on the new booth; 'kubectl get pods -w' on the second monitor")
put('L04', ["เกิดใหม่บนเรืออีกลำ", "kubectl drain lab-worker2", "SchedulingDisabled", "lab-worker", "lab-worker2", "kubectl uncordon"],
    "'เกิดใหม่บนเรืออีกลำ' is a title banner at the top; 'kubectl drain lab-worker2' on the work-order card; 'SchedulingDisabled' on the closed gate; 'lab-worker' and 'lab-worker2' on the ship hulls; 'kubectl uncordon' on the green ribbon")
put('L05', ["ปรับจำนวนบูธ", "--replicas=5", "--replicas=2", "--replicas=0", "SuccessfulDelete"],
    "'ปรับจำนวนบูธ' is a title banner at the top; the three scene headings are '--replicas=5', '--replicas=2', '--replicas=0' in order; 'SuccessfulDelete' on one event ticket")
put('L06', ["มาทีหลัง: ถูกลบ", "มาก่อน: ถูกรับเลี้ยง", "ถอด label (app-)", "stray", "stray"],
    "'มาทีหลัง: ถูกลบ' heading left, 'มาก่อน: ถูกรับเลี้ยง' heading middle, 'ถอด label (app-)' heading right; the stray booths in the left and middle scenes each have one 'stray' name card")
put('L07', ["Pod เดิมไม่เปลี่ยนรุ่น", "field is immutable", "nginx:1.27-alpine", "nginx:1.27-alpine", "nginx:1.28-alpine", "custom-columns"],
    "'Pod เดิมไม่เปลี่ยนรุ่น' is a title banner at the top; 'field is immutable' in the red stamp; the table card has exactly three rows reading 'nginx:1.27-alpine', 'nginx:1.27-alpine', 'nginx:1.28-alpine' top to bottom; 'custom-columns' as the table card title")
put('L08', ["ทิ้งไว้แล้วรับเลี้ยงคืน", "--cascade=orphan", "ownerReferences", "snack-rs", "+0"],
    "'ทิ้งไว้แล้วรับเลี้ยงคืน' is a title banner at the top; '--cascade=orphan' on the scissors; 'ownerReferences' on one re-clipped badge callout on the right; 'snack-rs' on the robot's chest plate on the right; '+0' on the stamping machine counter; never draw waterfalls")
put('L09', ["rs-quota", "pods: 4", "4/6", "exceeded quota", "LimitRange", "เพิ่มโควตา"],
    "'rs-quota' on the zone sign; 'pods: 4' on the gate post; '4/6' on the robot clipboard; 'exceeded quota' on the alert ticket; 'LimitRange' on the sticker machine; 'เพิ่มโควตา' on a small tag on the lever Nong Som pulls",
    caption_th="LAB7: namespace rs-quota มี quota pods=4 + LimitRange → RS replicas 6 ได้แค่ 4, Events FailedCreate exceeded quota, condition ReplicaFailure; เพิ่ม quota แล้ว RS สร้างต่อเอง (อาจรอราว 1 นาทีหลังเพิ่มโควตา เพราะ backoff); ทางเลือก PSA enforce ให้ RS สร้างได้แต่ Pod ถูกปฏิเสธ")
put('L10', ["กระจายบูธข้ามเรือ", "required: Pending", "preferred: 2+1", "lab-worker", "lab-worker2", "maxSkew: 1"],
    "'กระจายบูธข้ามเรือ' is a title banner at the top; 'required: Pending' heads the top scene; 'preferred: 2+1' heads the bottom scene; 'lab-worker' and 'lab-worker2' appear once each on the bottom scene ship hulls; 'maxSkew: 1' on a small side note card",
    caption_th="LAB8: required anti-affinity + replicas 3 บน worker 2 ลำ → 1 Pending; เปลี่ยนเป็น preferred → 2+1; topologySpreadConstraints maxSkew 1 ได้ 2+2 → scale 5 ได้ 2+3 เมื่อใส่ nodeTaintsPolicy: Honor (ไม่ใส่ จะนับ control-plane แล้วค้าง Pending)")
put('L11', ["ทุกบูธมี db ของตัวเอง", "som-booths", "som-booth", "replicas: 3", "web", "db", "som-shop-web:1.1"],
    "'ทุกบูธมี db ของตัวเอง' is a title banner at the top; 'som-booths' on the zone sign; 'som-booth' on the robot chest plate; 'replicas: 3' on its clipboard; 'web' and 'db' only on the two containers of the enlarged booth; 'som-shop-web:1.1' on the blueprint")
put('L12', ["เตรียม image ให้ทุกเรือ", "docker build", "som-shop-web:1.1", "kind load docker-image", "postgres:17.11-alpine"],
    "'เตรียม image ให้ทุกเรือ' is a title banner at the top; 'docker build' on the workbench; 'som-shop-web:1.1' on the first crate; 'kind load docker-image' on the delivery cart; 'postgres:17.11-alpine' on the second crate",
    caption_th="LAB9 เตรียม image: ถ้าคลัสเตอร์ใหม่ build som-shop-web:1.1 จากโฟลเดอร์ som-booths/app ของบทนี้ (สำเนาแอปจากบท 004) แล้ว kind load ให้ทุก Node, postgres ใช้ docker save --platform + kind load image-archive หรือให้ Node pull เอง")
put('L13', ["3 บูธบน 2 เรือ", "lab-worker", "lab-worker2", "kubectl get pods -o wide", "preferred"],
    "'3 บูธบน 2 เรือ' is a title banner at the top; 'lab-worker' and 'lab-worker2' on the hulls; 'kubectl get pods -o wide' on the laptop; 'preferred' on the magnet icon; booth name cards are color only")
put('L14', ["ต่อเข้าทีละบูธ", "8081", "8082", "8083", "port-forward", "ssh -L"],
    "'ต่อเข้าทีละบูธ' is a title banner at the top; '8081', '8082', '8083' on the three plugs; 'port-forward' on the relay box; 'ssh -L' on the tunnel cable; browser tabs have no text")
keep('L15')
keep('L16')
put('L17', ["เพิ่มแล้วลดบูธ", "3", "5", "2", "kubectl scale rs som-booth"],
    "'เพิ่มแล้วลดบูธ' is a title banner at the top; '3', '5', '2' are big count badges above the three scenes; 'kubectl scale rs som-booth' on the dial; the gauge has no text",
    caption_th="LAB9: kubectl scale rs som-booth --replicas=5 แล้ว 2 — ดูว่าบูธไหนถูกปิด; 5 บูธแบ่ง 2+3 (ลำไหนได้ 3 ไม่แน่นอน) (ระวัง resource: 5 บูธขอราว 1 CPU / 2.2Gi ถ้า Pending ให้ใช้ 4 — ในเครื่องทดสอบไม่มี Pending)")
put('L18', ["บูธเดิมยังไม่เปลี่ยน", "som-shop-web:1.1-promo", "โปรบูธใหม่", "1.1", "1.1", "1.1"],
    "'บูธเดิมยังไม่เปลี่ยน' is a title banner at the top; 'som-shop-web:1.1-promo' and 'โปรบูธใหม่' on the festive blueprint; each of the three booths shows one '1.1' signboard (exactly three '1.1' signboards); never draw real fireworks",
    caption_th="LAB9: scale กลับเป็น 3 ก่อน แล้วแก้ template เป็น som-shop-web:1.1-promo + ข้อความโปร แล้ว apply → บูธเดิมทั้ง 3 ยังเป็น 1.1 (template ใหม่ใช้กับบูธที่เกิดใหม่เท่านั้น; ถ้าไม่ scale กลับ apply จะคืน replicas=3 แล้วเกิดบูธ promo ทันที 1 ตัว)",
    scene="The robot holds a new festive blueprint with confetti and a star; the three booths on the ships still show the old plain signboards — two booths on one ship and one booth on the other ship, each booth standing entirely on one ship (no booth spans two ships). Nong Som compares the blueprint and the booths, eyebrows raised.")
keep('L19')
put('L20', ["ข้อมูลไม่ตรงกัน", "ชื่อ/IP เปลี่ยน", "เปลี่ยนรุ่นด้วยมือ", "บท 6 Service", "บท 7 Deployment"],
    "the three board rows carry 'ข้อมูลไม่ตรงกัน', 'ชื่อ/IP เปลี่ยน', 'เปลี่ยนรุ่นด้วยมือ' in order; 'บท 6 Service' under the lighthouse silhouette; 'บท 7 Deployment' under the tall robot silhouette; the silhouettes are shadowy and small")

assert set(P) == set(orig), set(P) ^ set(orig)
json.dump(P, open('005-patch.json', 'w'), ensure_ascii=False, indent=1)
ch = [i for i in P if P[i]['labels'] != orig[i]['labels']]
print('labels changed', len(ch))
print('caption/scene', [i for i in P if 'caption_th' in P[i] or 'scene' in P[i]])
