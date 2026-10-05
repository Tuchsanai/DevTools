#!/usr/bin/env python3
"""Storyboard ภาพบท 009 StatefulSet → images.json + imagegen-prompts.md (รัน: python3 build_images.py)"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from imgcommon import configure, t, l, main

configure("009")

# ---------------------------------------------------------------- Theory
S1 = "1. บทนำ: อยากมีครัว 3 ครัว"
t("opening-three-kitchens", S1,
  "เปิดบทที่ 9: ต่อจากบท 008 — ร้านจำออเดอร์ได้แล้ว แต่ db มีได้ตัวเดียว น้องส้มอยากมีครัวหลายครัวที่แต่ละครัวมีชื่อและตู้เซฟของตัวเอง",
  """A harbor dock at morning. One kitchen booth sits on a ship above a single safe. Nong Som stands with a blueprint
  sketch showing three kitchen booths each above its own safe, a thought cloud with question marks over the store-
  manager robot who holds one slip only.""",
  ["บทที่ 9", "ครัวละตู้เซฟ", "Deployment: ใบเบิกใบเดียว"],
  "'บทที่ 9' as a title banner; 'ครัวละตู้เซฟ' on Nong Som's blueprint; 'Deployment: ใบเบิกใบเดียว' on the single slip the manager robot holds")
t("recap-008-shared-slip", S1,
  "ทวนบท 008: Deployment ใช้ Pod template เดียว ทุก Pod จึงอ้าง claimName เดียวกัน — replicas 2 = postgres สองตัวเขียนโฟลเดอร์เดียว (ทดสอบแล้วออเดอร์หาย/PANIC)",
  """Two kitchen booths on one ship connected to the same safe; their ledger has torn pages and a red alarm light;
  the shared blueprint card shows one claimName line. Nong Som points at the blueprint line.""",
  ["claimName: som-db-data", "replicas: 2", "PANIC", "template เดียว = ตู้เดียว"],
  "'claimName: som-db-data' on the blueprint card; 'replicas: 2' on a small sign; 'PANIC' on the alarm light; 'template เดียว = ตู้เดียว' as a title banner",
  nt=True)
t("metaphor-legend", S1,
  "อุปมาใหม่: StatefulSet = หัวหน้ากะที่ตั้งชื่อบูธตามเลขลำดับและแจกตู้เซฟประจำตัว, volumeClaimTemplates = สมุดใบเบิกฉีกได้, headless Service = สมุดรายชื่อบอกเลขบูธตรง ๆ",
  """A legend board with four rounded tiles: a purple-navy robot with a numbered ticket dispenser on its chest; a pad
  of pre-printed slips with one slip being torn off; three booths with number plates each above its own numbered
  safe; an open directory book on a lectern. Nong Som presents the board.""",
  ["StatefulSet = หัวหน้ากะตั้งเลข", "volumeClaimTemplates = สมุดใบเบิก", "บูธละตู้เซฟ", "headless Service = สมุดรายชื่อ"],
  "each tile carries exactly one of the four labels in the listed order; booth plates in tile 3 are color-only")

S2 = "2. ทำไม Deployment ไม่พอสำหรับระบบ stateful"
t("stateless-vs-stateful", S2,
  "stateless (web) สลับตัวไหนก็ได้ เหมือนชามกระดาษใช้แล้วทิ้ง; stateful (db) แต่ละตัวมีข้อมูล/ตัวตนของตัวเอง เหมือนชามเซรามิกสลักชื่อ",
  """Left shelf: a stack of identical paper food bowls, a hand takes any one. Right shelf: three ceramic food bowls
  each engraved with a number, each sitting on its own small safe. Nong Som holds one ceramic bowl carefully.""",
  ["stateless", "stateful", "หยิบใบไหนก็ได้", "แต่ละใบมีของตัวเอง"],
  "'stateless' above left shelf; 'stateful' above right shelf; 'หยิบใบไหนก็ได้' under left; 'แต่ละใบมีของตัวเอง' under right")
t("deployment-random-names", S2,
  "Pod ของ Deployment ชื่อสุ่ม (som-db-7b786655f5-9hf7p) เปลี่ยนทุกครั้งที่สร้างใหม่ และ RollingUpdate ทำให้มี 2 ตัวพร้อมกันได้ — ไม่เหมาะกับ db ที่ต้องรู้ว่าใครคือใคร",
  """A row of booths whose name plates are random barcode-like strings; one booth is replaced and its new plate is a
  different random string; a customer silhouette holding an address card looks lost. Nong Som scratches her head.""",
  ["som-db-7b786655f5-9hf7p", "ชื่อใหม่ทุกครั้ง", "ชื่อสุ่ม หาตัวไม่เจอ"],
  "'som-db-7b786655f5-9hf7p' on one booth plate (other plates are color-only stripes); 'ชื่อใหม่ทุกครั้ง' on an arrow to the replaced booth; 'ชื่อสุ่ม หาตัวไม่เจอ' as a title banner",
  nt=True)

S3 = "3. คุณสมบัติของ StatefulSet"
t("three-guarantees", S3,
  "StatefulSet รับประกัน 3 อย่าง: ชื่อคงที่ (<sts>-0..N), ที่อยู่ DNS คงที่ต่อ Pod, และ storage ประจำตัวที่ตามกลับมาทุกครั้ง",
  """Three podium pillars like an award stand: a name plate ending in -0, a directory book page with an address line,
  a numbered safe. The purple-navy numbering robot stands behind them. Nong Som applauds.""",
  ["ชื่อคงที่", "DNS คงที่", "ตู้เซฟประจำตัว", "som-db-0"],
  "'ชื่อคงที่', 'DNS คงที่', 'ตู้เซฟประจำตัว' on the three pillars; 'som-db-0' on the name plate on the first pillar")
t("manifest-anatomy", S3,
  "โครง StatefulSet: serviceName (ชื่อ headless Service), replicas, selector, template และ volumeClaimTemplates — ไม่มี strategy แบบ Deployment แต่ใช้ updateStrategy",
  """A big YAML card on a board with highlighted rows and callout arrows; the numbering robot holds the card corner.
  Nong Som with a pen.""",
  ["kind: StatefulSet", "serviceName: som-db", "volumeClaimTemplates", "updateStrategy", "โครงไฟล์ StatefulSet"],
  "first four labels are rows on the YAML card; 'โครงไฟล์ StatefulSet' as a title banner")
t("ordinal-names-labels", S3,
  "ชื่อ Pod = <ชื่อ sts>-<ลำดับ> และมี label อัตโนมัติ statefulset.kubernetes.io/pod-name กับ apps.kubernetes.io/pod-index — ใช้เลือก Pod รายตัวได้",
  """Three booths in a row with plates -0, -1, -2; each has a luggage tag with a small index number; the numbering
  robot hands out the next ticket. Nong Som reads a tag.""",
  ["web-0", "web-1", "web-2", "apps.kubernetes.io/pod-index", "ชื่อตามเลขลำดับ"],
  "'web-0', 'web-1', 'web-2' on the three booth plates; 'apps.kubernetes.io/pod-index' on the enlarged tag; 'ชื่อตามเลขลำดับ' as a title banner",
  nt=True)
t("same-name-new-uid", S3,
  "ลบ Pod som-db-0 → ได้ Pod ชื่อเดิม som-db-0 แต่ UID และ IP ใหม่ และต่อ PVC เดิม data-som-db-0 (ทดสอบแล้ว)",
  """A crane lifts away booth -0 and places a new booth with the same plate -0 in the same row; its IP tag is a new
  color; its tube reconnects to the same numbered safe. Nong Som compares old and new IP tags.""",
  ["som-db-0", "IP ใหม่", "data-som-db-0", "ชื่อเดิม ตู้เดิม"],
  "'som-db-0' on the new booth plate; 'IP ใหม่' on the new IP tag; 'data-som-db-0' on the safe; 'ชื่อเดิม ตู้เดิม' as a title banner",
  nt=True)

S4 = "4. headless Service และ DNS ต่อ Pod"
t("normal-vs-headless", S4,
  "Service ปกติมี ClusterIP เดียวแล้วกระจายไปทุก Pod; headless (clusterIP: None) ไม่มี IP กลาง DNS ตอบ IP ของ Pod โดยตรงและมีชื่อรายตัว",
  """Left: a lighthouse counter with one address plate sending customers to random booths. Right: an open directory
  book on a lectern listing each booth's direct address, customers going straight to a chosen booth. Nong Som
  stands between them.""",
  ["Service ปกติ", "ClusterIP", "clusterIP: None", "ชี้ตรงรายบูธ"],
  "'Service ปกติ' above left; 'ClusterIP' on the lighthouse address plate; 'clusterIP: None' on the lectern; 'ชี้ตรงรายบูธ' above right")
t("dns-format", S4,
  "รูปแบบ DNS ต่อ Pod: <pod>.<service>.<namespace>.svc.cluster.local เช่น som-db-0.som-db.som-shop.svc.cluster.local — ใน namespace เดียวกันใช้ som-db-0.som-db ได้",
  """A long address ribbon broken into colored segments like train cars, each segment with a small icon (booth,
  directory book, zone sign, harbor). Nong Som walks along the ribbon reading it.""",
  ["som-db-0", "som-db", "som-shop", "svc.cluster.local", "ที่อยู่เต็มของบูธ"],
  "the four English labels on four consecutive segments with dots between them; 'ที่อยู่เต็มของบูธ' as a title banner")
t("nslookup-headless", S4,
  "nslookup ชื่อ headless Service ได้ IP ของทุก Pod ที่ Ready (หลายบรรทัด) ส่วน nslookup ชื่อรายตัวได้ IP เดียว — Pod ที่ไม่ Ready ไม่อยู่ในคำตอบ",
  """A directory book showing a page with three address lines and one grayed-out line for a booth with a red lamp;
  a second small card shows a single address for one booth. Nong Som holds a telephone handset.""",
  ["nslookup som-db", "3 Address", "nslookup som-db-1.som-db", "ไม่ Ready = ไม่อยู่ในสมุด"],
  "'nslookup som-db' above the page; '3 Address' on the page; 'nslookup som-db-1.som-db' on the small card; 'ไม่ Ready = ไม่อยู่ในสมุด' next to the grayed line",
  nt=True)
t("servicename-governs", S4,
  "spec.serviceName ต้องชี้ headless Service ที่ selector ตรงกับ Pod — เป็นตัวกำหนดโดเมนของ Pod; ต้องสร้าง Service เอง StatefulSet ไม่สร้างให้",
  """The numbering robot holds a cord tied to the directory book; the book stands on a pedestal Nong Som just built
  with a hammer; booths in the background.""",
  ["serviceName", "headless Service", "ต้องสร้าง Service เอง"],
  "'serviceName' on the cord tag; 'headless Service' on the book cover; 'ต้องสร้าง Service เอง' as a title banner")

S5 = "5. volumeClaimTemplates: ตู้เซฟประจำตัว"
t("pvc-per-pod", S5,
  "volumeClaimTemplates ชื่อ data → PVC ต่อ Pod ชื่อ data-<sts>-<ลำดับ> เช่น data-som-db-0, data-som-db-1 แต่ละใบได้ PV ของตัวเอง",
  """The numbering robot tears slips from a pad, each slip numbered, and each slip ties to its own safe beneath each
  numbered booth on different ships. Nong Som collects one slip.""",
  ["volumeClaimTemplates", "data-som-db-0", "data-som-db-1", "data-som-db-2", "บูธละใบเบิก"],
  "'volumeClaimTemplates' on the pad; three slip names on three slips; 'บูธละใบเบิก' as a title banner")
t("sticky-pvc", S5,
  "PVC ติดตามชื่อ Pod: Pod web-1 เกิดใหม่กี่ครั้งก็ต่อ www-web-1 เดิม ไฟล์ที่เขียนครั้งแรก (first-born web-1) ยังอยู่",
  """Booth -1 is rebuilt three times shown as fading ghost outlines, all tubes connecting to the same safe -1 that
  holds a note. Nong Som reads the note.""",
  ["web-1", "www-web-1", "first-born web-1", "เกิดใหม่ก็ตู้เดิม"],
  "'web-1' on the booth plate; 'www-web-1' on the safe; 'first-born web-1' on the note; 'เกิดใหม่ก็ตู้เดิม' as a title banner",
  nt=True)
t("pvc-survives", S5,
  "PVC ไม่ถูกลบเมื่อ scale down หรือลบ StatefulSet (ค่า default) — scale กลับหรือ apply ใหม่ Pod ชื่อเดิมกลับมาผูกตู้เดิม",
  """The numbering robot and booths -1 and -2 are gone (dashed outlines), but safes -1 and -2 remain padlocked in the
  hold with their slips still pinned. Nong Som points at the waiting safes.""",
  ["scale 3 → 1", "delete sts", "PVC ยังอยู่", "ตู้รอเจ้าของกลับมา"],
  "'scale 3 → 1' and 'delete sts' on two small signs; 'PVC ยังอยู่' on the pinned slips; 'ตู้รอเจ้าของกลับมา' as a title banner",
  nt=True)
t("retention-policy", S5,
  "persistentVolumeClaimRetentionPolicy: whenDeleted / whenScaled ค่า default Retain; ตั้ง Delete แล้ว PVC มี ownerReferences ถึง StatefulSet และถูกลบตาม (ทดสอบแล้ว)",
  """A control panel on the numbering robot with two toggle switches, each switching between a padlock icon and a
  crusher icon; a slip shows an owner badge pointing to the robot. Nong Som flips a switch.""",
  ["whenDeleted", "whenScaled", "Retain", "Delete", "ownerReferences", "เลือกได้ว่าเก็บหรือทิ้ง"],
  "'whenDeleted' and 'whenScaled' on the two switches; 'Retain' and 'Delete' on the two switch positions (each once, shared legend); 'ownerReferences' on the owner badge; last label as a title banner",
  nt=True)

S6 = "6. ลำดับการสร้าง/ลบ: podManagementPolicy"
t("ordered-ready-create", S6,
  "OrderedReady (default): สร้าง -0 รอจน Ready ก่อนสร้าง -1 แล้ว -2 — ถ้า -0 ไม่ Ready ตัวถัดไปไม่เกิด",
  """A row of three booth slots; booth -0 has a green lamp, booth -1 is being lowered by a crane, slot -2 is empty
  with a waiting sign. The numbering robot holds the next ticket until the lamp turns green.""",
  ["OrderedReady", "0 → 1 → 2", "รอ Ready ทีละตัว"],
  "'OrderedReady' on the robot chest display; '0 → 1 → 2' on an arrow strip under the slots; 'รอ Ready ทีละตัว' as a title banner",
  nt=True)
t("scale-down-reverse", S6,
  "scale down ลบจากเลขมากไปน้อย (-2 ก่อน -1) และรอตัวก่อนหน้าปิดเสร็จ — -0 ถูกลบเป็นตัวสุดท้ายเสมอ",
  """Booth -2 is being lifted away first by a crane, booth -1 waits next in line with a queue number, booth -0 stays.
  Nong Som counts backwards on her paw.""",
  ["2 → 1 → 0", "ลบจากเลขมากก่อน", "-0 อยู่ท้ายสุด"],
  "'2 → 1 → 0' on an arrow strip; 'ลบจากเลขมากก่อน' as a title banner; '-0 อยู่ท้ายสุด' next to booth -0",
  nt=True)
t("parallel-policy", S6,
  "podManagementPolicy: Parallel สร้าง/ลบทุกตัวพร้อมกันไม่รอกัน (ทดสอบแล้ว par-0..2 Pending พร้อมกัน) — ชื่อและตู้ประจำตัวยังเหมือนเดิม",
  """Three cranes lower booths -0, -1 and -2 at the same moment; each booth still lines up with its own safe. Nong Som
  waves a starting flag.""",
  ["Parallel", "พร้อมกันทุกตัว", "ชื่อและตู้ยังคงที่"],
  "'Parallel' on the starting flag; 'พร้อมกันทุกตัว' as a title banner; 'ชื่อและตู้ยังคงที่' as a subtitle",
  nt=True)

S7 = "7. การอัปเดต: updateStrategy"
t("rolling-reverse", S7,
  "RollingUpdate ของ StatefulSet: เปลี่ยนทีละตัวจากเลขมากไปน้อย (-2 → -1 → -0) รอแต่ละตัว Ready ก่อนไปตัวถัดไป",
  """Three booths in a row; booth -2 already has a new signboard, booth -1 is being refitted with a crane, booth -0
  still has the old signboard. Nong Som directs the crane.""",
  ["RollingUpdate", "2 → 1 → 0", "ทีละตัวจากท้ายแถว"],
  "'RollingUpdate' on the robot display; '2 → 1 → 0' on the arrow strip; 'ทีละตัวจากท้ายแถว' as a title banner",
  nt=True)
t("partition-canary", S7,
  "partition: N = อัปเดตเฉพาะ Pod ที่เลข ≥ N ใช้ทำ canary (partition 2 → เฉพาะ web-2 ได้ nginx:1.28-alpine) แล้วลด partition เป็น 0 เพื่อปล่อยทั้งหมด",
  """A rope barrier across the booth row between -1 and -2; only booth -2 beyond the rope has the new signboard;
  booths -0 and -1 keep the old one. Nong Som holds the rope post ready to move it.""",
  ["partition: 2", "web-2: 1.28", "web-0, web-1: 1.27", "ทดลองรุ่นใหม่บางบูธ"],
  "'partition: 2' on the rope post; 'web-2: 1.28' on booth -2 sign; 'web-0, web-1: 1.27' on a shared card in front of booths -0 and -1; last label as a title banner",
  nt=True)
t("revisions", S7,
  "StatefulSet เก็บรุ่นเป็น ControllerRevision: status.currentRevision / updateRevision และ label controller-revision-hash บน Pod — ดูด้วย kubectl rollout history sts",
  """The numbering robot holds a thin logbook with two bookmarks of different colors; each booth wears a small
  barcode sticker matching one of the bookmarks. Nong Som compares stickers.""",
  ["currentRevision", "updateRevision", "controller-revision-hash", "rollout history sts", "รุ่นปัจจุบันกับรุ่นใหม่"],
  "first two labels on the two bookmarks; 'controller-revision-hash' on an enlarged sticker; 'rollout history sts' on the logbook cover; last label as a title banner",
  nt=True)
t("ondelete", S7,
  "updateStrategy: OnDelete = แก้ template แล้ว Pod ยังไม่เปลี่ยน จนกว่าจะลบ Pod นั้นเอง — ควบคุมจังหวะได้ละเอียดสำหรับระบบที่ต้องอัปเกรดทีละขั้นด้วยมือ",
  """A new blueprint card is pinned on the robot but all booths still show old signboards; Nong Som presses a
  delete button for booth -1 only, and only that rebuilt booth shows the new sign.""",
  ["OnDelete", "kubectl delete pod web-1", "ลบเมื่อไรเปลี่ยนเมื่อนั้น"],
  "'OnDelete' on the robot display; 'kubectl delete pod web-1' on the button; 'ลบเมื่อไรเปลี่ยนเมื่อนั้น' as a title banner",
  nt=True)
t("min-ready-seconds", S7,
  "minReadySeconds: Pod ต้อง Ready ต่อเนื่องครบกี่วินาทีจึงนับว่า available ก่อนไปตัวถัดไป — ชะลอ rollout ให้เห็นปัญหาทัน",
  """A booth with a green lamp and a stopwatch counting; the crane for the next booth waits at a stop line until the
  stopwatch completes. Nong Som holds the stopwatch.""",
  ["minReadySeconds: 10", "รอนิ่งก่อนไปต่อ"],
  "'minReadySeconds: 10' on the stopwatch; 'รอนิ่งก่อนไปต่อ' as a title banner")

S8 = "8. replicas หลายตัว ≠ ข้อมูล replicate"
t("independent-ledgers", S8,
  "scale som-db เป็น 3 ได้ 3 postgres ที่ข้อมูลแยกกัน: som-db-0 มี orders ส่วน som-db-1/2 ว่าง (relation \"orders\" does not exist) — StatefulSet ไม่คัดลอกข้อมูลให้",
  """Three kitchen booths each above its own safe; booth -0's ledger is full, booths -1 and -2 have blank ledgers.
  Nong Som looks surprised at the blank ones.""",
  ["som-db-0: 4 orders", "som-db-1: ว่าง", "som-db-2: ว่าง", "relation \"orders\" does not exist", "ไม่ได้คัดลอกให้อัตโนมัติ"],
  "the three booth labels on three ledgers; the English error on a red card near booth -1; last label as a title banner",
  nt=True)
t("streaming-replication", S8,
  "ถ้าต้องการสำเนาจริง แอปต้องทำเอง เช่น postgres streaming replication: replica ใช้ pg_basebackup -R จาก primary แล้วรับ WAL ต่อเนื่อง อ่านได้อย่างเดียว",
  """Booth -0 marked as the main kitchen sends ledger pages along a small conveyor courier to a copy booth whose
  ledger fills in sync; the copy booth has a glass read-only window. Nong Som checks the two ledgers match.""",
  ["primary", "replica", "pg_basebackup -R", "streaming", "อ่านอย่างเดียว"],
  "'primary' on booth -0; 'replica' on the copy booth; 'pg_basebackup -R' on the first conveyor box; 'streaming' on the conveyor belt; 'อ่านอย่างเดียว' on the glass window",
  nt=True)
t("operator-concept", S8,
  "ระบบจริง: failover, สลับ primary, backup อัตโนมัติ ใช้ Operator (controller เฉพาะทางของฐานข้อมูล) ดูแลบน StatefulSet/Pod — บทนี้ปูทางเท่านั้น",
  """A specialist robot wearing a chef hat and holding a toolbox oversees several kitchen booths and safes, ready to
  swap the main kitchen if one fails. Nong Som takes notes.""",
  ["Operator", "failover", "ผู้เชี่ยวชาญดูแลฐานข้อมูล"],
  "'Operator' on the specialist robot; 'failover' on a swap-arrow sign; 'ผู้เชี่ยวชาญดูแลฐานข้อมูล' as a title banner")

S9 = "9. StatefulSet กับ Node ล่ม"
t("at-most-one", S9,
  "Node ล่ม: Pod web-1 ค้าง Terminating (Ready False) ไม่ถูกสร้างใหม่ที่ Node อื่น — StatefulSet ยอมให้มี Pod ชื่อเดียวกันได้ไม่เกิน 1 ตัว (at most one)",
  """A ship stuck in thick fog with booth -1 shown as a dim silhouette; on the clear ship booths -0 and -2 are open; an
  empty slot -1 on the clear ship has a 'no entry' sign. Nong Som looks at the fog with binoculars.""",
  ["web-1 Terminating", "NotReady", "ชื่อเดียวกันมีได้ตัวเดียว"],
  "'web-1 Terminating' on the dim booth; 'NotReady' on the foggy ship flag; 'ชื่อเดียวกันมีได้ตัวเดียว' as a title banner",
  nt=True)
t("force-delete-danger", S9,
  "force delete (--grace-period=0 --force) เสี่ยง: ถ้า Node แค่หลุดเครือข่ายแต่ Pod ยังทำงาน จะมี som-db-0 สองตัวเขียนข้อมูลพร้อมกัน",
  """Two booths both labeled -0, one on the foggy ship still cooking, one on the clear ship just built; both connect
  to safes and write the ledger; red lightning icons between them. Nong Som raises a stop paw.""",
  ["--force", "som-db-0", "som-db-0", "อันตราย: สองตัวชื่อเดียว"],
  "'--force' on a red hammer; 'som-db-0' on each of the two booths (exactly twice); 'อันตราย: สองตัวชื่อเดียว' as a title banner")
t("out-of-service-local", S9,
  "ยืนยันว่า Node ดับจริงแล้วใส่ taint node.kubernetes.io/out-of-service → ระบบลบ Pod ให้ แต่ PV ของ local-path ผูก Node เดิม Pod ใหม่จึง Pending จนเรือกลับมา",
  """A harbor official tapes an out-of-service sign on the foggy ship; booth -1 is removed from it; a new booth -1
  hangs on a crane over the clear ship but cannot land because its slip is chained to the safe on the foggy ship.
  Nong Som holds the tape roll.""",
  ["node.kubernetes.io/out-of-service", "web-1 Pending", "didn't match PersistentVolume's node affinity", "ตู้เซฟยังติดเรือเดิม"],
  "taint label on the sign; 'web-1 Pending' on the hanging booth; the English message on a red card; 'ตู้เซฟยังติดเรือเดิม' as a title banner",
  nt=True)

S10 = "10. เปรียบเทียบและแนวปฏิบัติ"
t("compare-controllers", S10,
  "เทียบ Deployment (Pod เหมือนกัน สลับได้) vs StatefulSet (ชื่อ/ตู้ประจำตัว เรียงลำดับ) vs DaemonSet (1 Pod ต่อ Node เช่น agent เก็บ log — แนวคิด)",
  """Three columns: the store-manager robot with identical booths; the numbering robot with numbered booths and
  safes; a third robot placing exactly one small booth on every ship. Nong Som stands in front.""",
  ["Deployment", "StatefulSet", "DaemonSet", "ทุกตัวเหมือนกัน", "มีเลขประจำตัว", "เรือละ 1 ตัว"],
  "column headers 'Deployment', 'StatefulSet', 'DaemonSet'; under them 'ทุกตัวเหมือนกัน', 'มีเลขประจำตัว', 'เรือละ 1 ตัว' respectively")
t("which-name-to-connect", S10,
  "web ควรต่อ db ด้วยชื่อไหน: som-db (headless) ตอบ IP ทุกตัว เมื่อ scale เป็น 3 อาจต่อผิดตัว → ระบุ som-db-0.som-db ให้ชี้ primary ชัดเจน",
  """A web booth customer holding two address cards; one card points to the directory book page with three addresses
  (arrows scatter to three kitchens), the other card points directly to kitchen -0. Nong Som circles the second
  card.""",
  ["som-db", "som-db-0.som-db", "ชี้ตัวหลักให้ชัด"],
  "'som-db' on the first card; 'som-db-0.som-db' on the second card; 'ชี้ตัวหลักให้ชัด' as a title banner",
  nt=True)
t("adopt-existing-pvc", S10,
  "ย้ายข้อมูลจาก Deployment: ตั้ง PV เป็น Retain → ลบ PVC เดิม → ลบ claimRef → สร้าง PVC ชื่อ data-som-db-0 (volumeName) ไว้ก่อน → StatefulSet ใช้ PVC ชื่อนั้นทันที",
  """Nong Som wheels an old safe on a hand truck from an old single kitchen to the numbered booth -0; she sticks a new
  slip with the numbered name on it before the numbering robot arrives; the robot nods seeing the slip already
  there.""",
  ["Retain", "data-som-db-0", "volumeName", "ย้ายบ้านพร้อมตู้เซฟเดิม"],
  "'Retain' on the padlock; 'data-som-db-0' on the new slip; 'volumeName' on the slip's second line; 'ย้ายบ้านพร้อมตู้เซฟเดิม' as a title banner",
  nt=True)
t("best-practices", S10,
  "แนวปฏิบัติ: readinessProbe ที่ถูกต้อง, resources, PV Retain สำหรับข้อมูลสำคัญ, backup นอกคลัสเตอร์, ไม่ force delete, กระจาย Pod ข้าม Node และใช้ Operator สำหรับ HA",
  """A checklist board with six rows each with a small icon (green lamp, gauge, padlock, dock warehouse, stop sign,
  two ships). Nong Som ticks the boxes with a big pencil.""",
  ["readinessProbe", "resources", "Retain", "backup", "ไม่ force delete", "เช็กลิสต์ db"],
  "first five labels on five checklist rows (the sixth row is icon-only); 'เช็กลิสต์ db' as the board title")

S11 = "11. สรุป"
t("summary-table", S11,
  "ตารางสรุป StatefulSet: ชื่อ, DNS, PVC, ลำดับ, การอัปเดต, การลบ — เทียบกับ Deployment",
  """A clean table board with two columns (manager robot icon vs numbering robot icon) and five icon rows; cells are
  check and cross icons only. Nong Som points at it.""",
  ["ชื่อ Pod", "DNS ต่อ Pod", "PVC ต่อ Pod", "ลำดับ", "อัปเดต", "สรุปบท"],
  "five row headers 'ชื่อ Pod', 'DNS ต่อ Pod', 'PVC ต่อ Pod', 'ลำดับ', 'อัปเดต'; 'สรุปบท' as a title banner; column headers are icon-only; cells are icon-only")
t("command-cheatsheet", S11,
  "คำสั่งประจำบท: kubectl get sts,pod,pvc / rollout status sts / patch partition / scale sts / nslookup <pod>.<svc>",
  """A chalkboard cheat sheet on an easel with five command lines in monospace and small icons. Nong Som holds chalk.""",
  ["kubectl get sts,pvc", "kubectl rollout status sts/som-db", "kubectl scale sts som-db", "nslookup som-db-0.som-db", "คำสั่งประจำบท"],
  "the four commands as lines on the board; 'คำสั่งประจำบท' as the board title")
t("next-chapters", S11,
  "ปิดบท: รหัสผ่าน db ยังเขียนตรงใน YAML → ConfigMap/Secret, เปิดร้านด้วย NodePort → Ingress, ปรับจำนวน web อัตโนมัติ → HPA",
  """Sunset harbor with three signposts pointing to three upcoming islands: a sealed envelope vault, a grand harbor
  gate arch, an automatic dial that adds booths. Nong Som holds a map with the shop route.""",
  ["ConfigMap / Secret", "Ingress", "HPA", "บทถัดไป"],
  "the three English labels on the three signposts; 'บทถัดไป' as a title banner",
  allow=True)

# ---------------------------------------------------------------- LAB
l("lab0-prepare", "LAB0 เตรียมคลัสเตอร์",
  "LAB0: 3 Node Ready, StorageClass standard, ไม่มี PV/PVC ค้างจากบท 008 (kubectl get pv ว่าง), image postgres:17.11-alpine, nginx:1.27/1.28-alpine, som-shop-web:1.2 พร้อม",
  """Nong Som at a laptop on the dock; three ships with Ready flags; an empty clean cargo hold with no leftover safes;
  crates of images on a crane.""",
  ["kubectl get pv", "No resources found", "postgres:17.11-alpine", "เตรียมคลัสเตอร์"],
  "'kubectl get pv' and 'No resources found' on the laptop screen as two lines; 'postgres:17.11-alpine' on one crate (others color-only); 'เตรียมคลัสเตอร์' as a title banner",
  nt=True)
l("lab1-deploy-vs-sts", "LAB1 Deployment เทียบ StatefulSet",
  "LAB1: nginx 3 ตัวแบบ Deployment ได้ชื่อสุ่ม ลบแล้วชื่อใหม่; แบบ StatefulSet ได้ web-0/1/2 ลบ web-1 แล้วได้ web-1 คืน",
  """Two rows of booths: the upper row under the manager robot with random barcode plates, one replaced with a new
  random plate; the lower row under the numbering robot with plates -0, -1, -2 and a rebuilt -1 keeping its plate.
  Nong Som compares.""",
  ["Deployment: ชื่อสุ่ม", "StatefulSet: ชื่อคงที่", "web-1", "web-1"],
  "first label above the upper row; second label above the lower row; 'web-1' on the old booth -1 outline and on the rebuilt booth -1 (exactly twice); upper row plates are color-only stripes",
  nt=True)
l("lab2-headless-dns", "LAB2 headless Service และ DNS",
  "LAB2: Service web clusterIP: None → nslookup web ได้ 3 Address, nslookup web-0.web.default.svc.cluster.local ได้ IP เดียว, wget web-1.web ได้หน้าของ web-1",
  """A directory book on a lectern with three address lines; a telephone line from Nong Som's handset to booth -1;
  the booth replies with a page.""",
  ["clusterIP: None", "nslookup web", "web-1.web", "โทรหาบูธตรง ๆ"],
  "'clusterIP: None' on the lectern; 'nslookup web' on the book page header; 'web-1.web' on the phone cord tag; 'โทรหาบูธตรง ๆ' as a title banner",
  nt=True)
l("lab3-volume-claim-templates", "LAB3 volumeClaimTemplates",
  "LAB3: PVC www-web-0/1/2 เกิดตามลำดับ แต่ละ Pod เขียน first-born <ชื่อ> ครั้งแรก — ลบ Pod แล้วไฟล์เดิมยังอยู่",
  """Three numbered booths each with its own safe holding a note; one booth is rebuilt and its note remains. Nong Som
  holds a magnifier over a note.""",
  ["www-web-0", "www-web-1", "www-web-2", "first-born web-1", "บูธละตู้เซฟ"],
  "three safe names on three safes; 'first-born web-1' on the note in safe -1; 'บูธละตู้เซฟ' as a title banner",
  nt=True)
l("lab4-ordered-ready", "LAB4 ลำดับและ podManagementPolicy",
  "LAB4: StatefulSet bad ที่ readiness ไม่ผ่าน → ค้างที่ bad-0 ไม่สร้าง bad-1 จน touch /tmp/ready → bad-1 ตามมา",
  """Booth -0 with a red lamp; the crane holding booth -1 is frozen in mid-air; Nong Som flips the lamp switch to green
  and the crane starts moving.""",
  ["bad-0 0/1", "touch /tmp/ready", "bad-1 ตามมา", "รอตัวก่อนหน้า Ready"],
  "'bad-0 0/1' on booth -0; 'touch /tmp/ready' on the switch; 'bad-1 ตามมา' on the crane; 'รอตัวก่อนหน้า Ready' as a title banner",
  nt=True)
l("lab4-parallel", "LAB4 ลำดับและ podManagementPolicy",
  "LAB4 (ต่อ): podManagementPolicy: Parallel → par-0/1/2 เกิดพร้อมกัน; scale down OrderedReady ลบ web-2 ก่อน web-1",
  """Three cranes lowering three booths at once on the left; on the right booth -2 lifted away before booth -1. Nong
  Som with a stopwatch.""",
  ["Parallel: พร้อมกัน", "OrderedReady: 2 ก่อน 1"],
  "first label above the left scene; second label above the right scene",
  nt=True)
l("lab5-scale-retention", "LAB5 scale และ PVC retention",
  "LAB5: scale 3→1 แล้ว PVC www-web-1/2 ยังอยู่ → scale กลับ web-2 อ่าน first-born web-2 เดิม; StatefulSet par ตั้ง whenScaled/whenDeleted: Delete → PVC หายตาม",
  """Left: padlocked safes -1 and -2 waiting, then booths return to them. Right: the robot's switch set to crusher and
  safes going into a crusher press. Nong Som between the scenes.""",
  ["Retain (default)", "first-born web-2", "whenScaled: Delete", "PVC หายตาม"],
  "'Retain (default)' above left; 'first-born web-2' on a note; 'whenScaled: Delete' above right; 'PVC หายตาม' on the crusher",
  nt=True)
l("lab6-partition", "LAB6 RollingUpdate และ partition",
  "LAB6: partition 2 + nginx:1.28-alpine → เฉพาะ web-2 (updated=1) → partition 0 → web-1 แล้ว web-0 — rollout history มี 2 revision",
  """A rope barrier between booths -1 and -2; booth -2 shows the new signboard; then Nong Som moves the rope post to
  the start of the row and the crane refits booth -1 then -0.""",
  ["partition: 2", "updated=1", "partition: 0", "2 → 1 → 0", "ปล่อยรุ่นใหม่เป็นขั้น"],
  "'partition: 2' and 'partition: 0' on the two rope post positions; 'updated=1' on a status card; '2 → 1 → 0' on the arrow strip; last label as a title banner",
  nt=True)
l("lab7-ondelete", "LAB7 OnDelete และ minReadySeconds",
  "LAB7: OnDelete + set image กลับ 1.27 → ไม่มี Pod เปลี่ยน → ลบ web-1 → web-1 เป็น 1.27 คนเดียว; minReadySeconds ชะลอการเปลี่ยนแต่ละตัว",
  """All booths show the same old sign while a new blueprint is pinned; Nong Som presses a button for booth -1; only
  booth -1 gets the other sign; a stopwatch on the dock.""",
  ["OnDelete", "web-1: 1.27", "web-0, web-2: 1.28", "เปลี่ยนเมื่อสั่งลบ"],
  "'OnDelete' on the robot display; 'web-1: 1.27' on booth -1; 'web-0, web-2: 1.28' on a shared card; last label as a title banner",
  nt=True)
l("lab8-delete-reapply", "LAB8 ลบ StatefulSet แล้ว apply ใหม่",
  "LAB8: kubectl delete sts web → Pod หายหมด PVC 3 ใบยังอยู่ → apply ใหม่ → web-0/1/2 อ่าน first-born เดิมทุกตัว",
  """The numbering robot and booths vanish into dashed outlines; three padlocked safes remain; a new robot arrives and
  booths reappear above the same safes, each note unchanged. Nong Som smiles.""",
  ["delete sts web", "PVC ยังอยู่ 3 ใบ", "apply ใหม่", "ข้อมูลเดิมทุกตัว"],
  "'delete sts web' on the fading robot; 'PVC ยังอยู่ 3 ใบ' on the safes; 'apply ใหม่' on the arriving robot; last label as a title banner",
  nt=True)
l("lab9-node-down", "LAB9 Node ล่ม",
  "LAB9: docker stop Node ที่มี web-1 (tolerationSeconds 30) → NotReady → web-1 Terminating ค้าง ไม่มี web-1 ใหม่ (รอ ~2.5 นาที ยังค้าง)",
  """A foggy ship with dim booth -1; the clear ship has booths -0 and -2 and an empty slot with a no-entry sign; a
  stopwatch. Nong Som with binoculars.""",
  ["docker stop lab-worker2", "web-1 Terminating", "ไม่สร้างแทนให้"],
  "'docker stop lab-worker2' on a switch box; 'web-1 Terminating' on the dim booth; 'ไม่สร้างแทนให้' on the no-entry sign",
  nt=True)
l("lab9-out-of-service", "LAB9 Node ล่ม",
  "LAB9 (ต่อ): taint out-of-service → web-1 ถูกลบและสร้างใหม่แต่ Pending (PV node affinity) → เอา taint ออก + docker start → web-1 Running อ่าน first-born web-1 เดิม",
  """An official tapes a sign on the foggy ship; a new booth -1 hangs on a crane unable to land; then the fog clears
  and booth -1 sits back on its ship above its safe. Nong Som removes the tape.""",
  ["out-of-service", "web-1 Pending", "docker start", "กลับมาตู้เดิม"],
  "'out-of-service' on the taped sign; 'web-1 Pending' on the hanging booth; 'docker start' on the switch box; 'กลับมาตู้เดิม' as a title banner",
  nt=True)
F = "LAB10 ร้านน้องส้มแบบโปรดักชัน: db เป็น StatefulSet"
l("lab10-architecture", F,
  "LAB10 ภาพรวม som-shop-v5: web Deployment 3 บูธ (NodePort 30080) → DATABASE_URL som-db-0.som-db → headless Service som-db → StatefulSet som-db → PVC data-som-db-0",
  """Harbor overview: three web booths behind a lighthouse with a gangway door; a directory book on a lectern for the
  kitchen; kitchen booth -0 above its numbered safe; the numbering robot beside it. Nong Som holds the plan.""",
  ["som-web ×3", "30080", "som-db-0.som-db", "data-som-db-0", "ร้านแบบโปรดักชัน"],
  "'som-web ×3' over the web booths; '30080' on the gangway door; 'som-db-0.som-db' on the directory page; 'data-som-db-0' on the safe; last label as a title banner")
l("lab10-start-008", F,
  "LAB10 ขั้น A: เริ่มจากสภาพท้ายบท 008 (db Deployment + PVC som-db-data) สั่งซื้อ 3 ครั้ง → orders=3",
  """The old single kitchen booth under the store-manager robot with one safe; customers place orders; a display.
  Nong Som holds a moving-day checklist.""",
  ["som-db-data", "orders=3", "จุดเริ่ม = ท้ายบท 008"],
  "'som-db-data' on the slip; 'orders=3' on the display; last label as a title banner",
  nt=True)
l("lab10-migrate", F,
  "LAB10 ขั้น B: PV → Retain, ลบ Deployment/Service/PVC เดิม, ลบ claimRef, สร้าง PVC data-som-db-0 (volumeName) แล้ว apply StatefulSet → som-db-0 ผูก PV เดิม",
  """Nong Som wheels the padlocked safe on a hand truck to numbered booth -0 and pins a numbered slip onto it; the
  numbering robot arrives and connects booth -0 to the safe.""",
  ["Retain", "remove claimRef", "data-som-db-0", "ย้ายตู้เซฟไปบูธ -0"],
  "'Retain' on the padlock; 'remove claimRef' on scissors; 'data-som-db-0' on the slip; last label as a title banner",
  nt=True)
l("lab10-web-points-sts", F,
  "LAB10 ขั้น B (ต่อ): web ใช้ DATABASE_URL ...@som-db-0.som-db:5432 → rollout → /api/stats orders=3 ข้อมูลย้ายมาครบ",
  """Web booths each with a tube labeled with an address going to the directory book and on to kitchen -0; the display
  shows the same count as before. Nong Som cheers.""",
  ["som-db-0.som-db:5432", "orders=3", "ย้ายมาครบ"],
  "'som-db-0.som-db:5432' on the tube tag; 'orders=3' on the display; 'ย้ายมาครบ' as a title banner",
  nt=True)
l("lab10-delete-pod", F,
  "LAB10 ขั้น C: ลบ som-db-0 → กลับมาชื่อเดิม UID/IP ใหม่ PVC data-som-db-0 เดิม → orders=3",
  """A crane swaps kitchen booth -0 for a new booth with the same plate; new IP tag color; same safe. Nong Som compares
  tags.""",
  ["som-db-0", "IP ใหม่", "orders=3", "ชื่อเดิม ตู้เดิม ข้อมูลเดิม"],
  "'som-db-0' on the new plate; 'IP ใหม่' on the IP tag; 'orders=3' on the display; last label as a title banner",
  nt=True)
l("lab10-rolling-db", F,
  "LAB10 ขั้น D: patch memory limit 512Mi → 768Mi → rolling update som-db (revision 2) → สั่งซื้อเพิ่ม orders=4",
  """The kitchen booth -0 is refitted by a crane with a larger cooling unit; the logbook flips to page two; the ledger
  gains a line. Nong Som gives a thumbs up.""",
  ["memory: 768Mi", "REVISION 2", "orders=4", "อัปเดตแล้วข้อมูลไม่หาย"],
  "'memory: 768Mi' on the cooling unit; 'REVISION 2' on the logbook page; 'orders=4' on the display; last label as a title banner",
  nt=True)
l("lab10-delete-sts", F,
  "LAB10 ขั้น E: delete sts som-db → PVC data-som-db-0 ยัง Bound → apply 10-db.yaml → orders=4",
  """The numbering robot vanishes; the safe -0 with its slip stays; a new robot arrives and reconnects. Nong Som points
  at the safe.""",
  ["delete sts som-db", "data-som-db-0: Bound", "orders=4", "ลบหัวหน้ากะ ตู้ไม่หาย"],
  "'delete sts som-db' on the fading robot; 'data-som-db-0: Bound' on the slip; 'orders=4' on the display; last label as a title banner",
  nt=True)
l("lab10-scale-three", F,
  "LAB10 ขั้น F: scale som-db 3 → PVC data-som-db-1/2 ใหม่ (ต่าง Node ได้), som-db-1/2 ไม่มีตาราง orders, nslookup som-db ได้ 3 IP แต่ร้านยังปกติเพราะ web ชี้ som-db-0",
  """Three kitchen booths -0, -1, -2 on two ships each above its own safe; only booth -0's ledger is full; the web tube
  goes only to -0. Nong Som explains with a pointer.""",
  ["data-som-db-1", "data-som-db-2", "relation \"orders\" does not exist", "3 ตัว ≠ 3 สำเนา"],
  "slip names on safes -1 and -2; the English error on a red card near booth -1; '3 ตัว ≠ 3 สำเนา' as a title banner",
  nt=True)
l("lab10-scale-back", F,
  "LAB10 ขั้น G: scale กลับ 1 → som-db-1/2 ถูกลบ (2 ก่อน 1) แต่ PVC data-som-db-1/2 ยังอยู่ ต้องลบเอง",
  """Booths -2 then -1 lifted away; their safes remain padlocked; Nong Som holds a broom ready to clean them up.""",
  ["scale --replicas=1", "PVC ค้าง 2 ใบ", "ลบเองเมื่อไม่ใช้"],
  "'scale --replicas=1' on a dial; 'PVC ค้าง 2 ใบ' on the remaining safes; 'ลบเองเมื่อไม่ใช้' as a title banner",
  nt=True)
l("lab10-extra-replica", F,
  "LAB10 เสริม: เพิ่มบรรทัด host replication ใน pg_hba.conf ของ som-db-0 → StatefulSet som-db-replica (init pg_basebackup -R) → pg_is_in_recovery = t, pg_stat_replication streaming async",
  """Kitchen booth -0 sends pages by a conveyor courier to a copy booth with a glass window; both ledgers show the same
  count; a status card. Nong Som checks with a magnifier.""",
  ["som-db-replica-0", "pg_basebackup -R", "streaming async", "สำเนาอ่านอย่างเดียว"],
  "'som-db-replica-0' on the copy booth plate; 'pg_basebackup -R' on the first conveyor box; 'streaming async' on the status card; last label as a title banner",
  nt=True)
l("lab10-extra-readonly", F,
  "LAB10 เสริม (ต่อ): สั่งซื้อแล้ว replica เห็นตาม (orders เท่ากัน), INSERT บน replica → cannot execute INSERT in a read-only transaction, ลบ som-db-0 แล้ว replica ต่อกลับเอง",
  """A pen bounces off the copy booth's glass window with a red card; after kitchen -0 is rebuilt, the conveyor
  reconnects. Nong Som nods.""",
  ["cannot execute INSERT in a read-only transaction", "ต่อกลับเอง", "เขียนได้ที่ primary เท่านั้น"],
  "the English error on the red card; 'ต่อกลับเอง' on the reconnecting conveyor; last label as a title banner",
  nt=True)
l("lab10-wrap-up", F,
  "LAB10 สรุปและบทถัดไป: db มีชื่อคงที่และตู้เซฟประจำตัวแล้ว แต่รหัสผ่านยังอยู่ใน YAML (→ Secret), เปิดร้านผ่าน NodePort (→ Ingress), web ยังต้อง scale เอง (→ HPA)",
  """Evening dock: Nong Som sits on a crate writing a three-item to-do list; three signposts beyond the harbor.""",
  ["Secret", "Ingress", "HPA", "งานถัดไปของร้าน"],
  "'Secret', 'Ingress', 'HPA' on the three signposts; 'งานถัดไปของร้าน' on the to-do list header",
  allow=True)

if __name__ == "__main__":
    main()
