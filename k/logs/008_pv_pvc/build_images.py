#!/usr/bin/env python3
"""Storyboard ภาพบท 008 PersistentVolume/PVC → images.json + imagegen-prompts.md (รัน: python3 build_images.py)"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from imgcommon import configure, t, l, main

configure("008")

# ---------------------------------------------------------------- Theory
S1 = "1. บทนำ: ร้านลืมออเดอร์"
t("opening-forgot-orders", S1,
  "เปิดบทที่ 8: ต่อจากท้ายบท 007 — Pod db ถูกสร้างใหม่ สมุดออเดอร์ในกล่อง emptyDir หายไปกับ Pod เดิม ร้านกลับไปเป็น orders=0",
  """A harbor dock in the morning. On a cargo ship, the kitchen booth (database booth) has just been rebuilt by a crane;
  beside it a plain cardboard box is being dropped into a recycling bin, its open lid showing loose ledger pages
  flying out. Inside the new booth an empty order ledger book lies open with blank pages. Nong Som stands on the dock
  with both paws on her cheeks, shocked, holding a long paper receipt strip of yesterday's orders.""",
  ["บทที่ 8", "Pod db ใหม่ = สมุดว่าง", "emptyDir", "orders=0"],
  "'บทที่ 8' is a title banner across the top; 'Pod db ใหม่ = สมุดว่าง' is a smaller subtitle under it; 'emptyDir' is printed on the cardboard box going into the bin; 'orders=0' is on a small display card on the new booth")
t("recap-007-reseed", S1,
  "ทวนบท 007: ข้อมูลใน emptyDir อยู่ได้นานเท่ากับ Pod — ลบ Pod/Recreate/rollout ของ db ทีไร ต้อง rollout restart web เพื่อเติมสินค้าใหม่ แต่ออเดอร์เดิมหายถาวร",
  """A horizontal timeline ribbon across the panel with three stations: left a database booth with a full ledger and
  a cardboard box, middle the booth being removed by a crane with the box falling away, right a new booth with an
  empty ledger while a store-manager robot presses a refresh button to restock shelves with kibble bags. Nong Som
  walks along the ribbon pointing at the gap in the middle.""",
  ["ลบ Pod db", "rollout restart web", "สินค้ากลับมา ออเดอร์ไม่กลับ"],
  "'ลบ Pod db' under the middle station; 'rollout restart web' on the refresh button; 'สินค้ากลับมา ออเดอร์ไม่กลับ' is a title banner at the top")
t("metaphor-legend", S1,
  "อุปมาใหม่ของบทนี้: PV = ตู้เซฟบนเรือ, PVC = ใบเบิกตู้เซฟ, StorageClass = โรงทำตู้เซฟอัตโนมัติ, ผูกกัน = กุญแจคู่, reclaimPolicy = ทิ้งหรือเก็บตู้เมื่อคืนใบเบิก",
  """A clean legend board divided into five rounded tiles in two rows. Tile 1: a steel safe in a ship cargo hold.
  Tile 2: a requisition slip card. Tile 3: a small workshop booth with a robot arm welding a new safe. Tile 4: two
  matching keys tied with a ribbon, one on a slip and one on a safe. Tile 5: split icon of a crusher press and a
  padlocked safe with a yellow tag. Nong Som stands at the side presenting the board with a pointer.""",
  ["PV = ตู้เซฟ", "PVC = ใบเบิก", "StorageClass = โรงทำตู้เซฟ", "bind = กุญแจคู่", "reclaimPolicy = ทิ้ง/เก็บ"],
  "each tile carries exactly one of the five labels in the order listed; no other text on the board")

S2 = "2. Volume และอายุของข้อมูล"
t("lifetime-ladder", S2,
  "อายุของที่เก็บข้อมูล 3 ชั้น: ไฟล์ใน container หายเมื่อ container เริ่มใหม่, emptyDir อยู่ถึงตอนลบ Pod, PV อยู่ต่อแม้ Pod หายจนกว่าจะลบ PVC/PV",
  """Three horizontal bars of increasing length like a growth chart: a short bar with a tiny shipping container icon,
  a medium bar with a cardboard box icon inside a booth, a long bar with a steel safe icon in a ship hold. A vertical
  dashed line marks where a booth is removed; only the long bar continues past it. Nong Som measures the bars with a
  ruler.""",
  ["container restart", "Pod ถูกลบ", "ไฟล์ใน container", "emptyDir", "PersistentVolume", "ยิ่งยาว ยิ่งอยู่นาน"],
  "'container restart' and 'Pod ถูกลบ' label two vertical dashed lines; bar labels 'ไฟล์ใน container', 'emptyDir', 'PersistentVolume' from short to long; 'ยิ่งยาว ยิ่งอยู่นาน' is a title banner at the top")
t("volume-types-map", S2,
  "แผนที่ประเภท volume: emptyDir (ชั่วคราวใน Pod), hostPath (ช่องบนเรือ), configMap/secret (ไฟล์ตั้งค่า — บทหน้า), persistentVolumeClaim (ตู้เซฟ), ephemeral (ใบเบิกที่ทิ้งพร้อม Pod)",
  """A central booth with five pneumatic tubes going out to five small destinations arranged in a fan: a cardboard
  box inside the booth, a hatch in the ship deck, a small sealed envelope tray, a steel safe in the cargo hold, and a
  disposable slip card stapled to the booth. Nong Som stands in the middle holding the tubes like a bouquet.""",
  ["emptyDir", "hostPath", "configMap / secret", "persistentVolumeClaim", "ephemeral", "volume มีหลายแบบ"],
  "each destination carries exactly one of the first five labels; 'volume มีหลายแบบ' is a title banner; the envelope tray is drawn small and faded to show it is a later topic",
  allow=True)
t("emptydir-detail", S2,
  "emptyDir: สร้างตอน Pod ขึ้น container ในPod เดียวกันใช้ร่วมกันได้ รอด container restart แต่หายเมื่อ Pod ถูกลบ; medium: Memory = ใช้ RAM, sizeLimit จำกัดขนาด",
  """Inside one booth two shipping containers share one cardboard box between them, passing a ledger page. One
  container blinks with a small restart arrow but the box stays. Outside, a ghost outline of the booth being lifted
  away with the box. A small inset shows a box made of glowing RAM chips. Nong Som points at the shared box.""",
  ["ใช้ร่วมกันใน Pod", "รอด container restart", "medium: Memory", "sizeLimit"],
  "'ใช้ร่วมกันใน Pod' above the shared box; 'รอด container restart' next to the restart arrow; 'medium: Memory' on the RAM inset; 'sizeLimit' on a small gauge on the box")
t("hostpath-danger", S2,
  "hostPath: ใช้โฟลเดอร์บน Node ตรง ๆ — ข้อมูลผูกกับเรือลำนั้น, Pod ย้ายเรือแล้วไม่เจอ, เสี่ยงความปลอดภัย จึงถูก Pod Security ระดับ restricted ห้าม",
  """Two ships side by side. On ship lab-worker a booth reaches into a hatch in the deck where an order ledger is
  stored. The same booth appears on ship lab-worker2 looking into an empty hatch with a question mark. A zone sign
  post with a red warning shield stands on the dock. Nong Som frowns, holding a flashlight into the empty hatch.""",
  ["hostPath", "lab-worker", "lab-worker2", "ย้ายเรือ = หาไม่เจอ", "restricted ห้ามใช้"],
  "'hostPath' on the first hatch; ship names on the hulls; 'ย้ายเรือ = หาไม่เจอ' as a title banner; 'restricted ห้ามใช้' on the warning shield")

S3 = "3. PV, PVC, StorageClass — ใครทำอะไร"
t("roles-admin-dev", S3,
  "แยกบทบาท: ผู้ดูแลคลัสเตอร์เตรียมตู้เซฟ (PV) หรือโรงทำตู้ (StorageClass); นักพัฒนาเขียนใบเบิก (PVC) แล้วให้ Pod ใช้ใบเบิก — ไม่ต้องรู้ว่าตู้อยู่ไหน",
  """Split scene. Left half: a faceless harbor administrator silhouette in a hard hat installs steel safes in a ship
  hold and runs the safe-making workshop. Right half: Nong Som as the shop developer fills in a requisition slip at a
  desk and hands it to her booth. A dashed divider line runs down the middle.""",
  ["ผู้ดูแลคลัสเตอร์", "นักพัฒนา", "PV / StorageClass", "PVC", "แยกหน้าที่กัน"],
  "'ผู้ดูแลคลัสเตอร์' above the left half; 'นักพัฒนา' above the right half; 'PV / StorageClass' on the workshop sign; 'PVC' on the slip; 'แยกหน้าที่กัน' as a title banner")
t("pvc-anatomy", S3,
  "กายวิภาค PVC: accessModes, resources.requests.storage, storageClassName (ไม่ใส่ = ใช้ default class) — PVC อยู่ใน namespace",
  """A giant requisition slip card pinned to a board, styled like a YAML form with highlighted rows; colored callout
  arrows point to three rows. A small namespace zone stamp in the corner. Nong Som holds a pen next to the card.""",
  ["kind: PersistentVolumeClaim", "accessModes", "requests.storage: 1Gi", "storageClassName", "ใบเบิก = อยู่ใน namespace"],
  "the first four labels are rows on the slip card; 'ใบเบิก = อยู่ใน namespace' is on the corner stamp")
t("pv-anatomy", S3,
  "กายวิภาค PV: capacity, accessModes, persistentVolumeReclaimPolicy, ที่เก็บจริง (hostPath/local/CSI), nodeAffinity, claimRef — PV เป็นของทั้งคลัสเตอร์ ไม่มี namespace",
  """A steel safe in a ship cargo hold with a large spec plate riveted on the door; callout arrows from the plate rows.
  A thin chain from the safe goes down to the ship hull marking it belongs to this ship. A harbor-wide map icon
  without zone colors floats next to it. Nong Som inspects the plate with a magnifying glass.""",
  ["kind: PersistentVolume", "capacity", "persistentVolumeReclaimPolicy", "nodeAffinity", "claimRef", "ไม่มี namespace"],
  "the first five labels are rows on the spec plate; 'ไม่มี namespace' on the harbor-map icon")
t("pod-uses-pvc", S3,
  "Pod อ้างแค่ชื่อ PVC: volumes[].persistentVolumeClaim.claimName + volumeMounts[].mountPath — Pod ไม่รู้จัก PV โดยตรง",
  """A booth with a pneumatic tube going from its back to a requisition slip clipped on a post, and the slip is tied
  by a ribbon with keys to a safe in the cargo hold below. The booth shows a small window labeled with a mount path.
  Nong Som traces the chain with her finger: booth → slip → safe.""",
  ["claimName: som-db-data", "mountPath", "Pod → PVC → PV", "Pod รู้จักแค่ใบเบิก"],
  "'claimName: som-db-data' on the slip; 'mountPath' on the booth window; 'Pod → PVC → PV' on an arrow strip along the chain; 'Pod รู้จักแค่ใบเบิก' as a title banner")

S4 = "4. Static provisioning (เตรียมตู้เซฟเอง)"
t("static-flow", S4,
  "Static provisioning: ผู้ดูแลสร้าง PV ไว้ก่อน (Available) → นักพัฒนาสร้าง PVC → control plane หา PV ที่เข้าเงื่อนไขแล้วผูกกัน (Bound)",
  """Three numbered steps left to right connected by arrows: an administrator silhouette rolls a new safe into a ship
  hold with a green 'available' light; Nong Som drops a slip into a slot at the control tower; the tower beams a
  ribbon that ties a key pair between slip and safe, the light turning blue.""",
  ["1 สร้าง PV", "2 สร้าง PVC", "3 ผูกกัน", "Available", "Bound"],
  "'1 สร้าง PV', '2 สร้าง PVC', '3 ผูกกัน' under each step; 'Available' on the green light; 'Bound' on the blue light")
t("storageclass-empty-string", S4,
  "storageClassName: \"\" = ขอเฉพาะ PV ที่ไม่มี class (ไม่ให้ default class สร้างตู้ใหม่) — ถ้าไม่ใส่ฟิลด์เลย default class (standard) จะเข้ามาทำแทน",
  """Two requisition slips at a sorting desk. The first slip with an empty quotation pair goes straight down a chute
  to a row of hand-made safes. The second slip with no class field is grabbed by the robot arm of the safe-making
  workshop which starts building a new safe. Nong Som watches the fork in surprise.""",
  ["storageClassName: \"\"", "ไม่ใส่ฟิลด์", "PV ที่เตรียมไว้", "standard สร้างใหม่", "ว่างเปล่า ≠ ไม่ใส่"],
  "'storageClassName: \"\"' on the first slip; 'ไม่ใส่ฟิลด์' on the second slip; 'PV ที่เตรียมไว้' over the hand-made safes; 'standard สร้างใหม่' on the workshop; 'ว่างเปล่า ≠ ไม่ใส่' as a title banner")
t("matching-rules", S4,
  "เงื่อนไขการจับคู่: class ตรง, accessModes ครบ, ขนาด PV ≥ ที่ขอ — ได้ตู้ใหญ่กว่าได้ (ขอ 50Mi ได้ PV 100Mi แสดง CAPACITY 100Mi) ขอเกินทุกตู้ = Pending",
  """A matching machine with a slip input slot and three safes on a turntable. A slip asking 50Mi lights up a 100Mi
  safe with a check mark; a second slip asking 1Gi bounces back with a red Pending stamp because all safes are
  smaller. Nong Som compares slip and safe sizes with a measuring tape.""",
  ["ขอ 50Mi", "PV 100Mi", "CAPACITY 100Mi", "ขอ 1Gi", "Pending", "ตู้ใหญ่กว่าได้ เล็กกว่าไม่ได้"],
  "'ขอ 50Mi' and 'ขอ 1Gi' on the two slips; 'PV 100Mi' on the matched safe; 'CAPACITY 100Mi' on a result card; 'Pending' on the red stamp; 'ตู้ใหญ่กว่าได้ เล็กกว่าไม่ได้' as a title banner",
  nt=True)
t("claimref-volumename", S4,
  "จองตู้ล่วงหน้า: PV ใส่ spec.claimRef (จองให้ PVC ชื่อนี้) หรือ PVC ใส่ spec.volumeName (ขอตู้ใบนี้) — ใช้ตอนกู้ข้อมูลจาก PV เดิม",
  """A safe with a reserved place card hung on its handle; a slip with a specific safe number written on it walks
  straight to that safe ignoring the others. Nong Som holds both reservation cards up, one in each paw.""",
  ["spec.claimRef", "spec.volumeName", "จองตู้ใบนี้"],
  "'spec.claimRef' on the place card on the safe; 'spec.volumeName' on the slip; 'จองตู้ใบนี้' as a title banner")

S5 = "5. Dynamic provisioning (StorageClass)"
t("dynamic-flow", S5,
  "Dynamic provisioning: PVC ระบุ StorageClass → provisioner สร้าง PV ชื่อ pvc-<uid> ให้อัตโนมัติแล้วผูกกับ PVC — ไม่ต้องรอผู้ดูแล",
  """Nong Som drops a slip into the window of the automatic safe-making workshop on the dock; the robot arm welds a
  new safe on a conveyor which slides into a ship cargo hold; a key pair ribbon ties the slip and the new safe.""",
  ["PVC", "StorageClass: standard", "PV: pvc-<uid>", "สร้างตู้ให้อัตโนมัติ"],
  "'PVC' on the slip; 'StorageClass: standard' on the workshop sign; 'PV: pvc-<uid>' on the new safe; 'สร้างตู้ให้อัตโนมัติ' as a title banner")
t("default-storageclass", S5,
  "kind มี StorageClass standard (default) — annotation storageclass.kubernetes.io/is-default-class: \"true\", provisioner rancher.io/local-path, Delete, WaitForFirstConsumer, ALLOWVOLUMEEXPANSION false",
  """A workshop booth with a big star badge on its roof marking it the default; a spec board on the wall lists its
  settings; a crown-shaped star stamp is on the board corner. Nong Som reads a laptop showing a table row.""",
  ["standard (default)", "rancher.io/local-path", "Delete", "WaitForFirstConsumer", "ALLOWVOLUMEEXPANSION false", "ไม่ระบุ class = ใช้ตัวนี้"],
  "'standard (default)' on the roof badge; next four labels are rows on the spec board; 'ไม่ระบุ class = ใช้ตัวนี้' as a title banner",
  nt=True)
t("local-path-inside", S5,
  "ข้างในของ local-path: สร้างโฟลเดอร์ /var/local-path-provisioner/pvc-<uid>_<ns>_<pvc> บน Node ที่ Pod ถูกวาง แล้วทำ PV แบบ hostPath + nodeAffinity ผูกกับ Node นั้น",
  """Cutaway view of a cargo ship lab-worker: in its hold a steel safe whose door opens into a folder drawer; a chain
  from the safe is locked to the ship's hull plate; the workshop robot arm on the dock reaches over the ship. Nong Som
  peeks into the drawer holding an order ledger.""",
  ["/var/local-path-provisioner/", "pvc-<uid>_som-shop_som-db-data", "nodeAffinity: lab-worker", "ข้อมูลอยู่บนดิสก์ของ Node"],
  "the path labels are on the drawer front, one above the other; 'nodeAffinity: lab-worker' on the chain lock; 'ข้อมูลอยู่บนดิสก์ของ Node' as a title banner",
  nt=True)
t("csi-concept", S5,
  "CSI (Container Storage Interface): มาตรฐานปลั๊กกลางให้ผู้ผลิต storage ต่อกับ Kubernetes — ระบบจริงใช้ CSI driver ของคลาวด์/NFS/Ceph ได้ RWX, expand, snapshot",
  """A wall in the workshop with one standard universal plug socket; three different safe models from different
  suppliers (generic shapes, no logos) each plug into it with an adapter cable. Nong Som plugs in the last one.""",
  ["CSI driver", "ปลั๊กมาตรฐานเดียว", "ต่อ storage ได้หลายแบบ"],
  "'CSI driver' on the socket; 'ปลั๊กมาตรฐานเดียว' as a title banner; 'ต่อ storage ได้หลายแบบ' as a subtitle under the safes; the three safe models carry no text")

S6 = "6. accessModes และ volumeMode"
t("access-modes-doors", S6,
  "accessModes 4 แบบ: RWO (เมานต์ได้จาก Node เดียว), ROX (อ่านได้หลาย Node), RWX (อ่านเขียนหลาย Node), RWOP (Pod เดียวเท่านั้น) — เป็นคุณสมบัติที่ storage ต้องรองรับ",
  """Four safes in a row, each with a different door: one door with a single ship-shaped key hole, one glass display
  door that many ships look through, one wide double door with many ships' tubes connected, one door with a single
  booth-shaped key hole. Nong Som walks along the row.""",
  ["RWO", "ROX", "RWX", "RWOP", "Node เดียว", "Pod เดียว"],
  "'RWO', 'ROX', 'RWX', 'RWOP' on the four safe doors in that order; 'Node เดียว' under the RWO safe; 'Pod เดียว' under the RWOP safe")
t("local-path-truth", S6,
  "ความจริงของ local-path (ทดสอบแล้ว): รองรับแค่ RWO และ RWOP, ขอ RWX → ProvisioningFailed, volumeMode: Block ไม่รองรับ, ขนาดไม่ถูกบังคับ (เขียน 50MB ลง PVC 10Mi ได้)",
  """The safe-making workshop with a results board: a slip marked RWX is rejected with a red X, a slip marked Block is
  rejected, slips RWO and RWOP get green checks; on the side a small safe labeled with a size overflows with ledger
  pages while still closing fine. Nong Som scratches her head reading the board.""",
  ["RWO ✓  RWOP ✓", "RWX ✗", "Block ✗", "ProvisioningFailed", "10Mi แต่เขียน 50MB ได้", "local-path ไม่บังคับขนาด"],
  "first three labels are rows on the results board; 'ProvisioningFailed' on the red stamp; '10Mi แต่เขียน 50MB ได้' on the overflowing safe; 'local-path ไม่บังคับขนาด' as a title banner",
  nt=True)
t("rwo-not-one-pod", S6,
  "RWO ≠ Pod เดียว: Pod 2 ตัวบน Node เดียวกันใช้ PVC RWO พร้อมกันได้; ถ้าต้องการ Pod เดียวจริงใช้ RWOP — Pod ที่ 2 จะ Pending",
  """Left: one ship with two booths both connected by tubes to the same safe, green check. Right: a second ship scene
  where a safe with a booth-shaped key hole connects to one booth, and a second booth waits in a queue with a
  yellow pending lamp. Nong Som stands between both scenes.""",
  ["RWO: 2 Pod บน Node เดียว ใช้ได้", "RWOP: Pod ที่ 2 รอ", "Pending"],
  "first label above the left scene; second label above the right scene; 'Pending' on the waiting booth lamp",
  nt=True)

S7 = "7. การผูก (binding) และสถานะ"
t("phases", S7,
  "สถานะ: PVC Pending → Bound (Lost เมื่อ PV หาย); PV Available → Bound → Released (คืนใบเบิกแล้ว) และ Failed เมื่อคืนตู้ไม่สำเร็จ",
  """Two parallel tracks like railway lines. Upper track: a slip card moving through stations. Lower track: a safe
  moving through stations, with the Released station showing a safe with a yellow tag and the Failed station a safe
  with a small smoke puff. Nong Som stands at the switch lever between tracks.""",
  ["PVC: Pending → Bound", "PV: Available → Bound → Released", "Failed", "Lost", "สถานะของใบเบิกและตู้"],
  "upper track label 'PVC: Pending → Bound'; lower track 'PV: Available → Bound → Released'; 'Failed' and 'Lost' on small side branches; 'สถานะของใบเบิกและตู้' as a title banner")
t("wffc-vs-immediate", S7,
  "volumeBindingMode: WaitForFirstConsumer = รอให้ scheduler เลือก Node ของ Pod ก่อนแล้วค่อยสร้างตู้บนเรือลำนั้น; Immediate สร้างทันที — กับ local-path ล้มเหลว \"no node was specified\"",
  """Left panel: the workshop robot waits with arms crossed beside a stopwatch until a booth lands on a ship, then
  builds the safe on that ship. Right panel: the robot rushes to build a safe immediately but stands confused on the
  dock with no ship chosen, a red error card in its hand. Nong Som looks at both panels.""",
  ["WaitForFirstConsumer", "รอ Pod ลงเรือก่อน", "Immediate", "no node was specified"],
  "'WaitForFirstConsumer' above left panel; 'รอ Pod ลงเรือก่อน' under it; 'Immediate' above right panel; 'no node was specified' on the red error card",
  nt=True)

S8 = "8. reclaimPolicy และ finalizers"
t("delete-vs-retain", S8,
  "reclaimPolicy เมื่อลบ PVC: Delete = PV และโฟลเดอร์บน Node ถูกลบทิ้ง (ค่า default ของ standard); Retain = PV เหลือสถานะ Released ข้อมูลยังอยู่; Recycle เลิกใช้แล้ว",
  """A returned slip in Nong Som's paw. Two paths: left path the safe rolls into a crusher press with a puff of dust;
  right path the safe is padlocked with a yellow tag and placed on a storage shelf. A third tiny faded path is closed
  with a barrier tape.""",
  ["Delete", "Retain", "Released", "Recycle (เลิกใช้)", "คืนใบเบิกแล้วตู้ไปไหน"],
  "'Delete' over the crusher; 'Retain' over the shelf; 'Released' on the yellow tag; 'Recycle (เลิกใช้)' on the barrier tape; 'คืนใบเบิกแล้วตู้ไปไหน' as a title banner")
t("released-rescue", S8,
  "กู้ PV ที่ Released: ลบ spec.claimRef → Available → สร้าง PVC ใหม่ใส่ volumeName → Bound ข้อมูลเดิมกลับมา (ทดสอบแล้ว)",
  """A padlocked safe with a yellow tag on a shelf. Step 1: Nong Som snips the old reservation tag string with
  scissors. Step 2: the safe light turns green. Step 3: a new slip with the safe's number ties to it with a fresh key
  pair ribbon and the ledger inside is still full.""",
  ["1 ลบ claimRef", "2 Available", "3 PVC ใหม่ + volumeName", "ข้อมูลเดิมกลับมา"],
  "the three step labels under each step; 'ข้อมูลเดิมกลับมา' on a ribbon over the full ledger",
  nt=True)
t("finalizers", S8,
  "finalizers kubernetes.io/pvc-protection และ pv-protection: ลบ PVC ที่ Pod ยังใช้อยู่ → ค้าง Terminating จนกว่า Pod จะเลิกใช้ กันข้อมูลหายระหว่างทำงาน",
  """A slip card on a post with a red protection clip; a faceless staff silhouette tries to pull the slip away but
  the clip holds; a booth is still connected to the slip by a tube. A status card shows a waiting hourglass. Nong Som
  points at the clip.""",
  ["kubernetes.io/pvc-protection", "Terminating", "Used By: writer", "ยังมี Pod ใช้ = ยังลบไม่ได้"],
  "'kubernetes.io/pvc-protection' on the red clip; 'Terminating' on the status card; 'Used By: writer' on the tube; 'ยังมี Pod ใช้ = ยังลบไม่ได้' as a title banner",
  nt=True)

S9 = "9. การขยาย PVC"
t("expansion", S9,
  "ขยาย PVC: แก้ requests.storage ให้ใหญ่ขึ้นได้ก็ต่อเมื่อ StorageClass มี allowVolumeExpansion: true และ driver รองรับ — standard ของ kind ถูกปฏิเสธ (Forbidden) ลดขนาดไม่ได้เสมอ",
  """Nong Som tries to stretch a safe with a big hand crank; a red error card pops from the workshop window. A small
  side panel shows a different safe with a CSI plug that grows a size step with a green arrow. A one-way arrow sign
  shows only growing is allowed.""",
  ["allowVolumeExpansion: true", "Forbidden", "only dynamically provisioned pvc can be resized", "ขยายได้ ลดไม่ได้"],
  "'allowVolumeExpansion: true' on the side panel; 'Forbidden' on the red card header; 'only dynamically provisioned pvc can be resized' as one line on the red card; 'ขยายได้ ลดไม่ได้' on the one-way arrow sign",
  nt=True)

S10 = "10. subPath, readOnly, fsGroup และสิทธิ์ไฟล์"
t("subpath-readonly", S10,
  "subPath = เมานต์เฉพาะโฟลเดอร์ย่อยของ volume; readOnly: true = อ่านได้อย่างเดียว เขียนแล้วได้ Read-only file system",
  """A safe with two drawers. One tube connects only to the lower drawer marked as a sub folder. Another tube from a
  second booth connects to the whole safe through a glass window, and a pen bounces off the window. Nong Som holds a
  diagram of the drawers.""",
  ["subPath: pgdata", "readOnly: true", "Read-only file system", "เมานต์บางส่วน / อ่านอย่างเดียว"],
  "'subPath: pgdata' on the lower drawer; 'readOnly: true' on the glass window; 'Read-only file system' on a small red card near the bouncing pen; last label as a title banner",
  nt=True)
t("fsgroup-postgres", S10,
  "สิทธิ์ไฟล์ของ postgres: รันเป็น uid 70 ต้องเป็นเจ้าของ PGDATA (โหมด 0700) — local-path สร้างโฟลเดอร์ 0777 ของ root และไม่สนใจ fsGroup จึงใช้ PGDATA เป็นโฟลเดอร์ย่อย pgdata ให้ postgres สร้างเอง",
  """Inside an open safe: an outer folder with a wide-open door and a root crown badge, and inside it an inner folder
  with a lock and a small badge number 70 where an order ledger sits. A faceless kitchen staff silhouette wearing a
  badge 70 opens only the inner folder. Nong Som points at the inner lock.""",
  ["drwxrwxrwx root", "pgdata: uid 70 (0700)", "fsGroup ไม่มีผลกับ local-path", "PGDATA เป็นโฟลเดอร์ย่อย"],
  "'drwxrwxrwx root' on the outer folder; 'pgdata: uid 70 (0700)' on the inner folder; 'fsGroup ไม่มีผลกับ local-path' as a subtitle; 'PGDATA เป็นโฟลเดอร์ย่อย' as a title banner; the staff silhouette is a person, not a robot",
  nt=True)

S11 = "11. ข้อมูลผูก Node (ต่อจากบท 003)"
t("node-down-pv-affinity", S11,
  "Node ล่มเมื่อใช้ local storage: Pod ใหม่ของ Deployment วางบน Node อื่นไม่ได้ เพราะ PV มี nodeAffinity — ค้าง Pending จนกว่า Node เดิมจะกลับมา",
  """Ship lab-worker is dark and anchored in fog with a NotReady flag, its safe locked inside. A new booth floats on
  a crane hook above ship lab-worker2 but cannot land because a chain from the booth's slip leads back to the foggy
  ship. Nong Som holds a radio, worried.""",
  ["lab-worker NotReady", "lab-worker2", "Pending", "didn't match PersistentVolume's node affinity", "ตู้เซฟอยู่บนเรือที่ล่ม"],
  "'lab-worker NotReady' on the foggy ship flag; 'lab-worker2' on the other hull; 'Pending' on the hanging booth; the long English message on a red card; 'ตู้เซฟอยู่บนเรือที่ล่ม' as a title banner",
  nt=True)

S12 = "12. ResourceQuota ของ storage และ ephemeral volume"
t("storage-quota", S12,
  "ResourceQuota คุมพื้นที่ต่อ namespace (ต่อบท 004): persistentvolumeclaims, requests.storage และ <class>.storageclass.storage.k8s.io/requests.storage — เกินแล้ว PVC ถูกปฏิเสธ exceeded quota",
  """A colored namespace zone with a budget board at its entrance showing three gauges; a slip trying to enter is
  stopped at the gate by a red barrier. Nong Som checks the gauges with a clipboard.""",
  ["persistentvolumeclaims: 2", "requests.storage: 1Gi", "standard...requests.storage: 500Mi", "exceeded quota", "งบพื้นที่ของโซน"],
  "first three labels on the three gauges; 'exceeded quota' on the red barrier; 'งบพื้นที่ของโซน' as a title banner",
  nt=True)
t("ephemeral-volume", S12,
  "Generic ephemeral volume: เขียน volumeClaimTemplate ใน Pod → ได้ PVC ชื่อ <pod>-<volume> จาก StorageClass และถูกลบพร้อม Pod (ทดสอบแล้ว fsg-e หายตาม Pod)",
  """A booth with a disposable slip stapled to its side, connected to a small safe. When the booth is lifted away by
  a crane, the stapled slip and the small safe go with it into the crusher. Nong Som waves goodbye.""",
  ["ephemeral", "PVC: <pod>-<volume>", "ลบ Pod = ลบใบเบิกด้วย"],
  "'ephemeral' on the booth side; 'PVC: <pod>-<volume>' on the stapled slip; 'ลบ Pod = ลบใบเบิกด้วย' as a title banner",
  nt=True)

S13 = "13. Backup และ snapshot (ปูทาง)"
t("backup-snapshot", S13,
  "PV ไม่ใช่ backup: Retain กันลบพลาดได้แต่ Node พัง/ดิสก์เสียข้อมูลก็หาย — ใช้ pg_dump สำรองระดับแอป และ VolumeSnapshot (ต้องมี CSI ที่รองรับ) สำรองระดับดิสก์",
  """A safe on a ship with a camera taking a snapshot photo of its contents onto a framed picture, and separately a
  staff silhouette copying the ledger into a second ledger stored on the dock warehouse. A cracked-disk icon on the
  ship with an alert. Nong Som holds the copied ledger proudly.""",
  ["PV ≠ backup", "pg_dump", "VolumeSnapshot", "ต้องมีสำเนานอกเรือ"],
  "'PV ≠ backup' as a title banner; 'pg_dump' on the copied ledger; 'VolumeSnapshot' on the framed picture; 'ต้องมีสำเนานอกเรือ' on the dock warehouse")

S14 = "14. ฐานข้อมูลกับ Deployment + PVC: ข้อควรระวัง"
t("two-postgres-one-folder", S14,
  "ผลทดสอบจริง: Deployment db replicas 2 + PVC RWO → Pod ทั้งคู่ลงเรือลำเดียวกันและเปิด postgres บนโฟลเดอร์เดียวกัน → ออเดอร์แยกกัน หาย หรือพัง PANIC",
  """One ship, two kitchen booths both connected by tubes to the same safe, two faceless cooks each writing in the
  same ledger at the same time; ink splatters and some pages tear. A lighthouse counter sends customers to both
  booths alternately. Nong Som rushes in with alarmed face.""",
  ["replicas: 2", "PVC RWO เดียวกัน", "2 ตัวเขียนสมุดเล่มเดียว", "PANIC"],
  "'replicas: 2' on a small sign on the ship; 'PVC RWO เดียวกัน' on the safe; '2 ตัวเขียนสมุดเล่มเดียว' as a title banner; 'PANIC' on a red alarm light",
  nt=True)
t("recreate-rwop-guard", S14,
  "วิธีกัน: db ต้อง replicas 1 + strategy Recreate (ไม่มีช่วงสองตัวพร้อมกัน) และใช้ ReadWriteOncePod ให้ระบบกันตัวที่ 2 — RWOP + RollingUpdate จะค้าง (Pod ใหม่ Pending รอตัวเก่า)",
  """Three shields standing in front of the kitchen booth: a shield with number 1, a shield with a swap-order arrow
  showing old booth leaves before new booth arrives, a shield with a single-booth key hole. Beside them a small
  warning inset: a rolling swap where the new booth waits forever behind the old one. Nong Som stands proudly
  behind the shields.""",
  ["replicas: 1", "strategy: Recreate", "ReadWriteOncePod", "RollingUpdate + RWOP = ค้าง", "กันสองตัวเขียนพร้อมกัน"],
  "first three labels on the three shields; 'RollingUpdate + RWOP = ค้าง' on the warning inset; 'กันสองตัวเขียนพร้อมกัน' as a title banner",
  nt=True)

S15 = "15. สรุป"
t("summary-table", S15,
  "ตารางสรุป: emptyDir / hostPath / PVC+static PV / PVC+StorageClass เทียบอายุข้อมูล, ใครสร้าง, ผูก Node ไหม, เหมาะกับอะไร",
  """A large clean table board on the dock with four rows and four columns, each row starting with an icon (cardboard
  box, deck hatch, hand-made safe, workshop-made safe). Cells contain only simple check marks, cross marks and clock
  icons. Nong Som stands beside it with a pointer.""",
  ["emptyDir", "hostPath", "static PV", "StorageClass", "อายุข้อมูล", "ผูก Node", "สรุปที่เก็บข้อมูล"],
  "four row headers 'emptyDir', 'hostPath', 'static PV', 'StorageClass'; two column headers 'อายุข้อมูล' and 'ผูก Node' (other columns are icon-only); 'สรุปที่เก็บข้อมูล' as a title banner; table cells are icon-only")
t("command-cheatsheet", S15,
  "คำสั่งที่ใช้บ่อย: kubectl get sc,pv,pvc / describe pvc / patch pv reclaimPolicy / ดูโฟลเดอร์บน Node ด้วย docker exec",
  """A chalkboard-style cheat sheet held on an easel with five command lines in monospace; small icons next to each
  line (safe, slip, workshop, magnifier, ship). Nong Som holds chalk.""",
  ["kubectl get sc,pv,pvc", "kubectl describe pvc", "kubectl patch pv", "docker exec lab-worker ls", "คำสั่งประจำบท"],
  "the four command lines on the board one per line; 'คำสั่งประจำบท' as the board title")
t("next-statefulset", S15,
  "ปิดบท: Deployment ให้ทุก Pod ใช้ใบเบิกใบเดียวกัน จึงขยาย db ไม่ได้ — บทหน้า StatefulSet ให้ Pod มีชื่อเลขลำดับคงที่และตู้เซฟประจำตัว",
  """At sunset, Nong Som looks across the harbor toward a new ship arriving where three booths with numbered plates
  each sit above their own safe in the cargo hold; a purple-navy numbering robot with a ticket dispenser waves from
  the deck. On the near dock a single kitchen booth with one safe.""",
  ["บทหน้า: StatefulSet", "som-db-0", "som-db-1", "som-db-2", "ตู้เซฟประจำตัวทุกบูธ"],
  "'บทหน้า: StatefulSet' as a title banner; the three booth plates on the arriving ship; 'ตู้เซฟประจำตัวทุกบูธ' as a subtitle",
  allow=True)

# ---------------------------------------------------------------- LAB
l("lab0-prepare", "LAB0 เตรียมคลัสเตอร์และ image",
  "LAB0: เช็ก 3 Node Ready, StorageClass standard (default) และ local-path-provisioner Running, โหลด postgres:17.11-alpine ด้วย image-archive และ som-shop-web:1.2/1.3",
  """Nong Som at a laptop on the dock; three ships with Ready flags; the safe-making workshop with a green running
  lamp; a crane unloading two crates of shop images and one crate of database image onto a ship.""",
  ["kubectl get sc", "standard (default)", "local-path-provisioner", "postgres:17.11-alpine", "เตรียมคลัสเตอร์"],
  "'kubectl get sc' on the laptop screen; 'standard (default)' on the workshop roof; 'local-path-provisioner' on the green lamp plate; 'postgres:17.11-alpine' on the database crate; the two shop crates are color-only; 'เตรียมคลัสเตอร์' as a title banner")
l("lab1-emptydir", "LAB1 emptyDir: อยู่เท่า Pod",
  "LAB1: เขียนไฟล์ลง emptyDir → kill container ไฟล์ยังอยู่ (RESTARTS 1) → ลบ Pod แล้วสร้างใหม่ ไฟล์หาย",
  """Two side-by-side frames. Frame 1: a booth whose container blinks with a restart arrow while the cardboard box
  with a note stays. Frame 2: the booth is replaced by a new one and the new cardboard box is empty. Nong Som holds a
  sticky note in each frame position.""",
  ["RESTARTS 1: ยังอยู่", "ลบ Pod: หาย", "emptyDir"],
  "'RESTARTS 1: ยังอยู่' under frame 1; 'ลบ Pod: หาย' under frame 2; 'emptyDir' on the box in frame 1",
  nt=True)
l("lab2-hostpath", "LAB2 hostPath: ข้อมูลอยู่บนเรือลำเดียว",
  "LAB2: Pod hostPath ปักไว้ lab-worker เขียนไฟล์ → docker exec lab-worker เห็นไฟล์ → ย้าย Pod ไป lab-worker2 ไม่เห็นไฟล์; namespace ที่ warn restricted เตือน hostPath",
  """Two ships; on lab-worker a hatch with a note visible, Nong Som peeks in from a ladder using a flashlight; on
  lab-worker2 the same hatch is empty. A small warning bell rings at the namespace zone sign.""",
  ["docker exec lab-worker", "lab-worker2: ไม่มีไฟล์", "hostPath", "เตือน restricted"],
  "'docker exec lab-worker' on a small terminal card near the ladder; 'lab-worker2: ไม่มีไฟล์' over the empty hatch; 'hostPath' on the first hatch; 'เตือน restricted' on the bell",
  nt=True)
l("lab3-first-pvc", "LAB3 PVC แรกจาก StorageClass",
  "LAB3: สร้าง PVC notes → Pending (WaitForFirstConsumer) → สร้าง Pod writer → Bound กับ PV pvc-<uid> บน Node ที่ Pod ลง; ลบ Pod สร้างใหม่ ข้อมูลยังอยู่",
  """A slip waits at the workshop window with an hourglass; then a booth lands on a ship and the workshop instantly
  builds a safe in that ship's hold, ribbon keys tying slip and safe. Nong Som watches the hourglass flip.""",
  ["notes: Pending", "waiting for first consumer", "Bound", "PVC แรกของน้องส้ม"],
  "'notes: Pending' on the waiting slip; 'waiting for first consumer' on a small grey event card; 'Bound' on the key ribbon; 'PVC แรกของน้องส้ม' as a title banner",
  nt=True)
l("lab3-peek-node", "LAB3 PVC แรกจาก StorageClass",
  "LAB3 (ต่อ): ดู PV ด้วย kubectl get pv -o yaml (hostPath + nodeAffinity) แล้ว docker exec lab-worker ls /var/local-path-provisioner เห็นโฟลเดอร์ pvc-<uid>_default_notes",
  """Cutaway of ship lab-worker's hold with the safe drawer open showing a folder; Nong Som on a ladder with a
  flashlight reads the folder tab; a terminal card floats beside her.""",
  ["/var/local-path-provisioner/", "pvc-<uid>_default_notes", "ตู้เซฟคือโฟลเดอร์บน Node"],
  "path labels on the drawer front; 'ตู้เซฟคือโฟลเดอร์บน Node' as a title banner; the terminal card is icon-only",
  nt=True)
l("lab4-static-pv", "LAB4 Static PV (hostPath) และ storageClassName \"\"",
  "LAB4: สร้าง PV pv-manual 100Mi (Retain, nodeAffinity lab-worker2) + PVC manual-claim 50Mi storageClassName \"\" → Bound ทันที CAPACITY 100Mi; PVC too-big 1Gi ค้าง Pending",
  """An administrator silhouette has placed a hand-made safe on ship lab-worker2; Nong Som's slip ties to it with a
  ribbon; another oversized slip stands alone with a Pending stamp and a grey message card.""",
  ["pv-manual 100Mi", "manual-claim: Bound", "too-big: Pending", "no storage class is set", "ตู้เซฟทำมือ"],
  "'pv-manual 100Mi' on the safe; 'manual-claim: Bound' on the tied slip; 'too-big: Pending' on the lone slip; 'no storage class is set' on the grey card; 'ตู้เซฟทำมือ' as a title banner",
  nt=True)
l("lab5-access-modes", "LAB5 accessModes กับ local-path",
  "LAB5: PVC RWX → ProvisioningFailed, Block → does not support block, RWOP Pod ที่ 2 Pending, RWO Pod 2 ตัวบน Node เดียวใช้ได้",
  """A test bench with four slips each with a result light: two red, one yellow with a waiting booth, one green with
  two booths sharing a safe on one ship. Nong Som writes results on a clipboard.""",
  ["RWX: ProvisioningFailed", "Block: ไม่รองรับ", "RWOP: Pending", "RWO: 2 Pod ใช้ได้", "ผลทดสอบประตูตู้เซฟ"],
  "first four labels next to the four lights; 'ผลทดสอบประตูตู้เซฟ' as a title banner",
  nt=True)
l("lab5-size-not-enforced", "LAB5 accessModes กับ local-path",
  "LAB5 (ต่อ): dd เขียน 50MB ลง PVC 10Mi สำเร็จ, df -h เห็นขนาดดิสก์ทั้งก้อนของ Node, ขยาย PVC ถูกปฏิเสธ — requests.storage ใน local-path เป็นแค่ตัวเลข",
  """A small safe with a 10Mi plate overflowing with kibble-bag sized data blocks yet still closing; a gauge beside
  it reads the whole ship's huge disk. Nong Som shrugs with paws up.""",
  ["10Mi", "เขียน 50MB ได้", "df -h = ดิสก์ทั้ง Node", "ขนาดเป็นแค่ตัวเลข"],
  "'10Mi' on the safe plate; 'เขียน 50MB ได้' on the overflow; 'df -h = ดิสก์ทั้ง Node' on the gauge; 'ขนาดเป็นแค่ตัวเลข' as a title banner",
  nt=True)
l("lab6-finalizer-delete", "LAB6 วงจรชีวิต: finalizer, Delete, Retain",
  "LAB6: ลบ PVC ที่ Pod ใช้อยู่ → Terminating (pvc-protection) → ลบ Pod → PVC หาย PV หาย โฟลเดอร์บน Node หาย (Delete)",
  """Left: a slip held by a red clip with an hourglass. Right: after the booth leaves, the slip and safe go into the
  crusher, and an empty spot remains in the ship hold. Nong Som watches with crossed arms.""",
  ["Terminating", "kubernetes.io/pvc-protection", "Delete: โฟลเดอร์หายด้วย"],
  "'Terminating' above the left scene; 'kubernetes.io/pvc-protection' on the red clip; 'Delete: โฟลเดอร์หายด้วย' above the right scene",
  nt=True)
l("lab6-retain-rescue", "LAB6 วงจรชีวิต: finalizer, Delete, Retain",
  "LAB6 (ต่อ): patch PV เป็น Retain → ลบ PVC → Released ไฟล์ k.txt ยังอยู่ → ลบ claimRef → Available → PVC ใหม่ volumeName → Bound อ่าน keepme ได้",
  """A padlocked safe with a yellow tag on a shelf; Nong Som snips a tag string, then a new slip ties to the safe and
  she pulls out a note from inside.""",
  ["Released", "Available", "Bound", "keepme", "กู้ตู้เซฟเดิมได้"],
  "'Released', 'Available', 'Bound' on three small status lights in a row; 'keepme' on the note; 'กู้ตู้เซฟเดิมได้' as a title banner",
  nt=True)
l("lab7-storageclass", "LAB7 StorageClass ของเราเอง",
  "LAB7: สร้าง standard-retain (Retain), local-immediate (Immediate → no node was specified), local-expand (allowVolumeExpansion: true → spec 20Mi แต่ capacity ยัง 10Mi ไม่มีใครขยายให้)",
  """Three small workshop booths on the dock with different roof signs; the first produces a padlocked safe; the
  second robot stands confused with a red card; the third robot holds a stretch tool but the safe stays the same
  size with a waiting clock. Nong Som walks past as an inspector.""",
  ["standard-retain", "local-immediate", "local-expand", "no node was specified", "20Mi ขอแล้ว ยังได้ 10Mi", "สร้าง StorageClass เอง"],
  "first three labels on the three roof signs; 'no node was specified' on the red card; '20Mi ขอแล้ว ยังได้ 10Mi' near the unchanged safe; 'สร้าง StorageClass เอง' as a title banner",
  nt=True)
l("lab8-node-down", "LAB8 Node ล่ม: ตู้เซฟติดเรือ",
  "LAB8: Deployment + PVC (tolerationSeconds 30) → docker stop Node ที่ Pod อยู่ → NotReady ~40 วิ → Pod ใหม่ Pending (PersistentVolume's node affinity) → docker start → กลับมา Running ข้อมูลเดิม",
  """A foggy dark ship with a locked safe inside; a new booth hangs on a crane above the other ship, unable to land;
  a stopwatch on the dock. Nong Som holds the ship's restart switch.""",
  ["docker stop lab-worker", "NotReady", "Pending", "PersistentVolume's node affinity", "รอเรือเดิมกลับมา"],
  "'docker stop lab-worker' on the switch; 'NotReady' on the foggy ship flag; 'Pending' on the hanging booth; 'PersistentVolume's node affinity' on a red card; 'รอเรือเดิมกลับมา' as a title banner",
  nt=True)
l("lab9-quota-ephemeral", "LAB9 งบพื้นที่, ephemeral, subPath/readOnly/fsGroup",
  "LAB9: ResourceQuota storage ปฏิเสธ PVC เกินงบ (exceeded quota), ephemeral volume ได้ PVC fsg-e ที่หายพร้อม Pod, subPath/readOnly ทำงาน, fsGroup 70 ไม่เปลี่ยนเจ้าของโฟลเดอร์ local-path",
  """A namespace zone gate stopping a slip at a red barrier; a booth with a stapled disposable slip; a safe with a
  sub drawer and a glass window; a folder tag showing an owner badge. Nong Som checks items with a tick list.""",
  ["exceeded quota", "fsg-e", "subPath", "readOnly", "gid 0 แม้ fsGroup 70", "ทดลองรวมมิตร"],
  "'exceeded quota' on the barrier; 'fsg-e' on the stapled slip; 'subPath' on the sub drawer; 'readOnly' on the glass window; 'gid 0 แม้ fsGroup 70' on the folder tag; 'ทดลองรวมมิตร' as a title banner",
  nt=True)
F = "LAB10 ร้านน้องส้มจำได้แล้ว"
l("lab10-architecture", F,
  "LAB10 ภาพรวม som-shop-v4: web Deployment 3 บูธ (NodePort 30080) → Service som-db → db Deployment replicas 1 Recreate → PVC som-db-data (standard 1Gi RWO) → PV บน Node",
  """Harbor overview: three web booths behind a lighthouse counter with a gangway door, a second lighthouse for the
  kitchen, one kitchen booth on a ship with a tube down to a safe in the hold; a slip with key ribbon between booth
  and safe. Nong Som on the dock holding the plan.""",
  ["som-web ×3", "30080", "som-db", "PVC som-db-data 1Gi", "ร้านน้องส้มจำได้แล้ว"],
  "'som-web ×3' over the web booths; '30080' on the gangway door; 'som-db' on the kitchen lighthouse name plate; 'PVC som-db-data 1Gi' on the slip; 'ร้านน้องส้มจำได้แล้ว' as a title banner")
l("lab10-first-orders", F,
  "LAB10 ขั้น A: apply → PVC Bound หลัง Pod db ลงเรือ → สั่งซื้อ 3 ครั้ง → /api/stats orders=3",
  """Customers silhouettes order at the web booths; the kitchen cook writes three lines in the ledger stored inside
  the safe; a counter display shows the count. Nong Som gives a thumbs up.""",
  ["Bound", "POST /api/orders", "orders=3", "ออเดอร์เก็บในตู้เซฟ"],
  "'Bound' on the key ribbon; 'POST /api/orders' on a customer's order card; 'orders=3' on the display; 'ออเดอร์เก็บในตู้เซฟ' as a title banner",
  nt=True)
l("lab10-delete-pod-db", F,
  "LAB10 ขั้น B–C: ลบ Pod db และ rollout restart db → Pod ใหม่ใช้ PVC เดิม orders=3 ทันที ไม่ต้อง rollout restart web แบบบท 007",
  """A crane replaces the kitchen booth; the new booth reconnects its tube to the same safe; the ledger inside still
  shows three lines. A small faded inset of chapter 007's empty ledger crossed out. Nong Som cheers.""",
  ["kubectl delete pod", "rollout restart deploy/som-db", "orders=3", "ไม่ต้องเติมร้านใหม่แล้ว"],
  "'kubectl delete pod' on the crane; 'rollout restart deploy/som-db' on a small button; 'orders=3' on the ledger display; 'ไม่ต้องเติมร้านใหม่แล้ว' as a title banner",
  nt=True)
l("lab10-delete-deploy", F,
  "LAB10 ขั้น D: ลบ Deployment som-db ทั้งตัว → PVC ยัง Bound → apply ใหม่ → ต่อตู้เดิม orders=3",
  """The store-manager robot of the kitchen is carried off the dock, but the slip on the post and the safe stay
  untouched; then a new manager robot arrives and reconnects. Nong Som points at the slip that never moved.""",
  ["delete deploy som-db", "som-db-data: Bound", "apply อีกครั้ง", "ใบเบิกไม่ได้เป็นของ Deployment"],
  "'delete deploy som-db' on the carried robot; 'som-db-data: Bound' on the slip; 'apply อีกครั้ง' on the arriving robot; last label as a title banner",
  nt=True)
l("lab10-peek-pgdata", F,
  "LAB10 ขั้น E: docker exec <node> ls -ln /var/local-path-provisioner/pvc-…_som-shop_som-db-data/pgdata → ไฟล์ของ postgres uid 70 (PG_VERSION, base)",
  """Cutaway into the ship hold: the safe is open showing a folder pgdata with files like PG_VERSION and a base
  drawer, owner badge 70. Nong Som on a ladder with a flashlight.""",
  ["pgdata", "PG_VERSION", "base", "70 70", "ไฟล์จริงของ postgres"],
  "'pgdata' on the folder; 'PG_VERSION' and 'base' on two file cards; '70 70' on the owner badge; 'ไฟล์จริงของ postgres' as a title banner",
  nt=True)
l("lab10-scale-two", F,
  "LAB10 ขั้น F: scale db เป็น 2 → ทั้งคู่ลง Node เดียว (RWO) Running/Ready ทั้งคู่ → postgres ตัวที่ 2 recovery บนโฟลเดอร์เดียวกัน → psql ผ่าน Service ได้ orders 3 กับ 6 สลับกัน",
  """One ship, two kitchen booths connected to the same safe; the lighthouse sends customers to both; two cooks
  write in the same ledger, but each sees a different page count on their screens. Nong Som squints confused.""",
  ["--replicas=2", "orders=3", "orders=6", "สองครัว สมุดเล่มเดียว"],
  "'--replicas=2' on a dial; 'orders=3' and 'orders=6' on the two cook screens; 'สองครัว สมุดเล่มเดียว' as a title banner",
  nt=True)
l("lab10-corruption", F,
  "LAB10 ขั้น F (ผล): scale กลับ 1 → ตัวที่เหลือ restart แล้วออเดอร์หาย หรือพังเป็น CrashLoopBackOff \"PANIC: could not locate a valid checkpoint record\" — ห้ามทำกับข้อมูลจริง",
  """The remaining kitchen booth has a red flashing lamp and smoke; the ledger has torn pages scattered; a red alarm
  card. Nong Som holds her head in dismay beside a 'do not try' cone.""",
  ["CrashLoopBackOff", "PANIC: could not locate a valid checkpoint record", "ห้ามทำกับข้อมูลจริง"],
  "'CrashLoopBackOff' on the red lamp plate; the PANIC message as one line on the red alarm card; 'ห้ามทำกับข้อมูลจริง' on the traffic cone banner",
  nt=True)
l("lab10-delete-pvc", F,
  "LAB10 ขั้น G: ลบ Deployment db + PVC → PV (Delete) ถูกลบพร้อมโฟลเดอร์ → apply ใหม่ได้ db ว่าง → rollout restart web เพื่อ seed → orders=0",
  """The slip and safe roll into the crusher; a fresh empty safe arrives from the workshop; the store-manager robot
  presses a restock button. Nong Som sadly waves at the crusher.""",
  ["delete pvc som-db-data", "reclaimPolicy: Delete", "orders=0", "ลบใบเบิก = ข้อมูลหายจริง"],
  "'delete pvc som-db-data' on the slip; 'reclaimPolicy: Delete' on the crusher; 'orders=0' on the new ledger display; last label as a title banner",
  nt=True)
l("lab10-retain-rwop", F,
  "LAB10 ขั้น H: StorageClass standard-retain + PVC ReadWriteOncePod → orders=2 → scale db 2 → Pod ที่ 2 Pending (ReadWriteOncePod already in-use) ปลอดภัย",
  """A padlock-ready safe with a single-booth key hole; a second kitchen booth waits behind a barrier with a yellow
  lamp. Nong Som stands with arms crossed, satisfied.""",
  ["standard-retain", "ReadWriteOncePod", "Pending", "ตัวที่ 2 เข้าไม่ได้"],
  "'standard-retain' on the safe plate; 'ReadWriteOncePod' on the key hole sign; 'Pending' on the waiting booth lamp; 'ตัวที่ 2 เข้าไม่ได้' as a title banner",
  nt=True)
l("lab10-rescue-retained", F,
  "LAB10 ขั้น H (ต่อ): ลบ PVC → PV Released ข้อมูลยังอยู่ → ลบ claimRef → PVC ใหม่ volumeName → Bound → orders=2 กลับมา",
  """A yellow-tagged padlocked safe on the storage shelf; Nong Som carries it back to the kitchen booth with a new
  slip; the ledger shows two lines.""",
  ["Released", "volumeName", "orders=2", "ตู้เซฟกลับมาพร้อมออเดอร์"],
  "'Released' on the yellow tag; 'volumeName' on the new slip; 'orders=2' on the ledger display; last label as a title banner",
  nt=True)
l("lab10-wrap-up", F,
  "LAB10 สรุป: PVC ทำให้ db จำได้ แต่ยังได้แค่ 1 ตัว, ข้อมูลผูก Node และ Deployment ให้ทุก Pod ใช้ใบเบิกเดียวกัน → บท 009 StatefulSet",
  """Evening dock: Nong Som sits on a crate writing a note list with three bullet icons; beyond the harbor a ship with
  numbered booths approaches.""",
  ["จำได้แล้ว ✓", "ขยายได้แค่ 1 ✗", "บทหน้า: StatefulSet"],
  "'จำได้แล้ว ✓' and 'ขยายได้แค่ 1 ✗' on the note list; 'บทหน้า: StatefulSet' on a banner on the arriving ship",
  allow=True)

if __name__ == "__main__":
    main()
