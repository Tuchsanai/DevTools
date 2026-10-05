#!/usr/bin/env python3
"""Storyboard ภาพบท 010 ConfigMap → images.json + imagegen-prompts.md (รัน: python3 build_images.py)"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from imgcommon import configure, t, l, main

configure("010")

# ---------------------------------------------------------------- Theory
S1 = "1. บทนำ: เปลี่ยนป้ายร้านต้อง build ใหม่ทุกครั้ง?"
t("opening-notice-board", S1,
  "เปิดบทที่ 10: ต่อจากบท 009 — ร้านมี db เป็น StatefulSet แล้ว แต่จะเปลี่ยนชื่อร้าน/โปรโมชันทีไรต้องแก้ YAML หรือ build image ใหม่ น้องส้มจึงติดกระดานประกาศกลางให้ทุกบูธอ่าน",
  """A harbor dock in the morning. Three web booths on ships and a database kitchen booth -0 above its safe. In the
  middle of the zone stands a teal-framed cork notice board with index cards. Nong Som pins a new card onto the board
  while the booth staff look at it.""",
  ["บทที่ 10", "ConfigMap", "ค่าตั้งค่าแยกจาก image"],
  "'บทที่ 10' as a title banner; 'ConfigMap' on the notice board header; 'ค่าตั้งค่าแยกจาก image' as a subtitle under the banner")
t("recap-hardcoded-env", S1,
  "ทวนบท 009: ค่า SHOP_NAME, SHOP_FOOTER และ DATABASE_URL (มีรหัส meow1234) เขียนตรงใน 20-web.yaml และธีม/เวอร์ชันฝังใน image ตอน build",
  """A big blueprint card of the web booth with three text rows written directly on it in permanent ink, and a shipping
  container stamped with a theme color. Nong Som points at the ink rows with a worried face.""",
  ["SHOP_NAME", "SHOP_FOOTER", "DATABASE_URL", "เขียนตายตัวใน YAML"],
  "'SHOP_NAME', 'SHOP_FOOTER', 'DATABASE_URL' as three rows on the blueprint card; 'เขียนตายตัวใน YAML' as a title banner; the container stamp is color-only")
t("metaphor-legend", S1,
  "อุปมาใหม่: ConfigMap = กระดานประกาศของโซน, env/envFrom = ป้ายโน้ตติดอกพนักงานตอนเข้ากะ, volume = กระดานเล็กในบูธที่หุ่นยนต์ kubelet มาอัปเดตให้",
  """A legend board with four rounded tiles: a teal-framed cork notice board with index cards; a staff silhouette with
  a note card clipped on the chest; a booth with a small notice board on its inner wall; a small round grey deckhand
  robot with one antenna carrying a tote bag of cards. Nong Som presents the legend.""",
  ["ConfigMap = กระดานประกาศ", "env = ป้ายติดอก", "volume = กระดานในบูธ", "kubelet = หุ่นยนต์ส่งการ์ด"],
  "each tile carries exactly one of the four labels in the listed order")

S2 = "2. ปัญหา: ค่าตั้งค่าฝังอยู่ใน image/YAML"
t("baked-into-image", S2,
  "ถ้าชื่อร้านหรือธีมฝังใน image (build-arg APP_THEME) เปลี่ยนป้ายครั้งเดียวต้อง build → kind load → rollout ใหม่ทั้งหมด",
  """A long conveyor loop on the dock: a shipping container goes into a build workshop, out to a crane, onto a ship,
  just to repaint a small shop sign; a clock shows time passing. Nong Som sighs with a tiny paint brush.""",
  ["docker build", "kind load", "rollout", "แก้ป้ายนิดเดียว ต้องทำใหม่หมด"],
  "'docker build', 'kind load', 'rollout' on three stations of the loop; last label as a title banner")
t("twelve-factor-config", S2,
  "หลัก 12-factor: แยก config ออกจากโค้ด — image เดียวกันใช้ได้ทุกสภาพแวดล้อม ค่าที่ต่างกันส่งเข้าไปตอนรัน",
  """One identical shipping container image on a pedestal with three arrows to three zones (dev, test, prod) each with
  its own small notice board of different card colors. Nong Som holds a checklist.""",
  ["image เดียว", "dev", "test", "prod", "ค่าต่างกันตามโซน"],
  "'image เดียว' on the pedestal; 'dev', 'test', 'prod' on the three zone signs; 'ค่าต่างกันตามโซน' as a title banner")
t("what-is-config", S2,
  "อะไรคือ config: ชื่อร้าน ธีม ข้อความประกาศ ไฟล์ตั้งค่า nginx — ไม่ใช่ข้อมูลออเดอร์ (อยู่ใน PVC) และไม่ใช่รหัสผ่าน (บทหน้า)",
  """Three sorting bins on the dock: the left bin holds index cards and a small config file, the middle bin holds the
  orange order ledger in a safe, the right bin is closed with a 'next chapter' sticker. Nong Som sorts items.""",
  ["config", "ข้อมูลออเดอร์ = PVC", "รหัสผ่าน = บทหน้า", "แยกให้ถูกที่"],
  "'config' on the left bin; 'ข้อมูลออเดอร์ = PVC' on the middle bin; 'รหัสผ่าน = บทหน้า' on the right bin; 'แยกให้ถูกที่' as a title banner; no padlock or envelope on the right bin, it is just a closed grey box")

S3 = "3. ConfigMap คืออะไร"
t("configmap-anatomy", S3,
  "ConfigMap = object แบบ key-value: data (ข้อความ UTF-8) และ binaryData (ไฟล์ไบนารีเก็บแบบ base64) ไม่มี spec ไม่มี Pod — เป็นแค่ข้อมูลให้ Pod อ้างถึง",
  """A big YAML card pinned on the notice board with highlighted rows; arrows point to two groups of index cards:
  normal text cards and one small card showing a fish-shaped logo icon. Nong Som reads the card.""",
  ["kind: ConfigMap", "data:", "binaryData:", "SHOP_NAME: ร้านน้องส้ม", "key = ชื่อการ์ด"],
  "first four labels are rows on the YAML card; 'key = ชื่อการ์ด' on a callout arrow pointing at one index card")
t("size-limit", S3,
  "ConfigMap หนึ่งตัวใหญ่ได้ไม่เกิน 1 MiB (ทดสอบ: ไฟล์ 1.1 MB → Too long: may not be more than 1048576 bytes) — ไฟล์ใหญ่ควรอยู่ใน image หรือ volume อื่น",
  """A weighing scale on the dock with a notice board on it; the scale needle points into a red zone; a stack of
  cards overflows. Nong Som holds a huge rolled poster that does not fit.""",
  ["≤ 1 MiB", "Too long: may not be more than 1048576 bytes", "ไฟล์ใหญ่ห้ามใส่"],
  "'≤ 1 MiB' on the scale face; the English error on a red card; 'ไฟล์ใหญ่ห้ามใส่' as a title banner",
  nt=True)
t("namespaced", S3,
  "ConfigMap อยู่ใน namespace (namespaced: true) — Pod ใช้ได้เฉพาะ ConfigMap ใน namespace เดียวกัน ไม่มีช่องให้ระบุ namespace อื่น",
  """Two painted zones on the harbor map, each with its own notice board. A booth in the orange zone reaches toward the
  board in the teal zone but a painted zone line stops the arm. Nong Som stands on the line.""",
  ["som-shop", "other", "ข้ามโซนไม่ได้"],
  "'som-shop' and 'other' on the two zone signs; 'ข้ามโซนไม่ได้' as a title banner",
  nt=True)
t("not-for-secrets", S3,
  "ConfigMap เก็บแบบข้อความธรรมดา ใครมีสิทธิ์ get configmaps ก็อ่านได้ — ห้ามใส่รหัสผ่าน/token",
  """The notice board in the open plaza; passers-by silhouettes read the cards freely. One card is crossed out with a
  big red X and shows only dots. Nong Som waves a warning flag.""",
  ["ใครก็อ่านได้", "●●●●", "ห้ามใส่รหัสผ่าน"],
  "'ใครก็อ่านได้' above the readers; '●●●●' on the crossed-out card; 'ห้ามใส่รหัสผ่าน' as a title banner")

S4 = "4. วิธีสร้าง ConfigMap"
t("from-literal", S4,
  "kubectl create configmap demo --from-literal=SHOP_NAME=ร้านน้องส้ม --from-literal=APP_THEME=sunset → การ์ด 2 ใบ (ค่าภาษาไทยใช้ได้)",
  """Nong Som writes two index cards by hand at a small desk and pins them on a fresh notice board; a terminal card on
  the desk shows a command.""",
  ["--from-literal", "SHOP_NAME=ร้านน้องส้ม", "APP_THEME=sunset", "เขียนการ์ดทีละใบ"],
  "'--from-literal' on the terminal card; the two key=value labels on the two index cards; 'เขียนการ์ดทีละใบ' as a title banner")
t("from-file", S4,
  "--from-file=announcement.txt → key = ชื่อไฟล์; --from-file=nginx.conf=default.conf → ตั้งชื่อ key เองได้; --from-file=. → ทุกไฟล์ในโฟลเดอร์",
  """Paper files drop from a folder into a sorting machine; each file comes out as one index card whose title is the
  file name; one card gets a new title via a relabel stamp. Nong Som operates the stamp.""",
  ["--from-file", "announcement.txt", "nginx.conf=default.conf", "ชื่อไฟล์ = key"],
  "'--from-file' on the machine; 'announcement.txt' on one card; 'nginx.conf=default.conf' on the restamped card; 'ชื่อไฟล์ = key' as a title banner")
t("from-env-file", S4,
  "--from-env-file=shop.env อ่านบรรทัด KEY=VALUE เป็นหลาย key; บรรทัด # ถูกข้าม, EMPTY= ได้ค่าว่าง (ทดสอบแล้ว)",
  """A sheet with several lines goes through a slicer; normal lines become separate index cards, a comment line falls
  into a waste basket, an empty-value line becomes a blank-value card. Nong Som watches.""",
  ["--from-env-file", "SHOP_THEME=sunset", "# comment", "EMPTY= → ค่าว่าง", "บรรทัดละการ์ด"],
  "'--from-env-file' on the slicer; 'SHOP_THEME=sunset' on one card; '# comment' on the paper in the basket; 'EMPTY= → ค่าว่าง' on the blank-value card; 'บรรทัดละการ์ด' as a title banner",
  nt=True)
t("dry-run-yaml", S4,
  "ให้ kubectl เขียน YAML ให้: kubectl create configmap ... --dry-run=client -o yaml > cm.yaml แล้ว commit/apply เป็นไฟล์",
  """A printer prints a YAML card from a command card without touching the notice board (the board stays empty with a
  dashed outline); Nong Som files the printed YAML into a binder.""",
  ["--dry-run=client -o yaml", "ยังไม่สร้างจริง", "เก็บเป็นไฟล์ YAML"],
  "'--dry-run=client -o yaml' on the command card; 'ยังไม่สร้างจริง' next to the dashed board; 'เก็บเป็นไฟล์ YAML' on the binder")

S5 = "5. ใช้ ConfigMap เป็นตัวแปร env"
t("config-map-key-ref", S5,
  "env.valueFrom.configMapKeyRef: เลือกทีละ key มาตั้งชื่อตัวแปรเอง (name + key) — ค่าถูกคัดลอกตอน container เริ่ม",
  """A staff member at the booth door; the deckhand robot copies one card from the zone board onto the note card clipped
  on the staff member's chest. Nong Som checks the chest card.""",
  ["configMapKeyRef", "key: SHOP_NAME", "คัดลอกตอนเข้ากะ"],
  "'configMapKeyRef' on the arrow from board to chest; 'key: SHOP_NAME' on the copied card; 'คัดลอกตอนเข้ากะ' as a title banner")
t("env-from-prefix", S5,
  "envFrom.configMapRef: ดึงทุก key เป็น env ในครั้งเดียว ใส่ prefix: CFG_ ได้ → CFG_SHOP_NAME, CFG_APP_THEME",
  """The deckhand robot photocopies the whole board at once into a stack of chest cards; a stamp adds a small prefix tag
  to each copied card. Nong Som holds the stamp.""",
  ["envFrom", "prefix: CFG_", "CFG_SHOP_NAME", "ทั้งกระดานในครั้งเดียว"],
  "'envFrom' on the copier; 'prefix: CFG_' on the stamp; 'CFG_SHOP_NAME' on one stamped card; 'ทั้งกระดานในครั้งเดียว' as a title banner",
  nt=True)
t("args-var-expansion", S5,
  "command/args อ้าง env ด้วย $(SHOP_NAME) ได้ (Kubernetes แทนค่าให้) — ถ้าไม่มีตัวแปรนั้น $(NOPE) ค้างเป็นข้อความเดิม",
  """A command ribbon with two placeholder slots: the first slot is filled with the shop name card, the second slot stays
  showing its literal placeholder text. Nong Som points at the unfilled slot.""",
  ["$(SHOP_NAME) → ร้านน้องส้ม", "$(NOPE) → $(NOPE)", "ไม่มีตัวแปร = ไม่แทนค่า"],
  "the two English-arrow labels on the two slots; 'ไม่มีตัวแปร = ไม่แทนค่า' as a title banner",
  nt=True)
t("env-precedence", S5,
  "ถ้าชื่อซ้ำกัน env ชนะ envFrom; และ $(POD_NAMESPACE) ในค่าที่มาจาก envFrom ไม่ถูกแทนค่า (ทดสอบ: footer ยังเป็น $(POD_NAMESPACE)) — ใส่ไว้ใน env แทน",
  """Two chest cards for the same key: one from the zone board (envFrom) placed under, one written in the blueprint
  (env) placed on top and winning. A small card with an unfilled placeholder sits aside. Nong Som compares them.""",
  ["env ชนะ envFrom", "SHOP_FOOTER", "$(POD_NAMESPACE) ไม่ถูกแทน"],
  "'env ชนะ envFrom' as a title banner; 'SHOP_FOOTER' on both stacked cards' shared tag; '$(POD_NAMESPACE) ไม่ถูกแทน' on the aside card",
  nt=True)
t("key-names-env", S5,
  "Kubernetes v1.37 ยอมให้ key แปลก ๆ เช่น 1bad หรือ shop.name เป็นชื่อ env ได้ (ทดสอบแล้ว ไม่ถูกข้าม) แต่โปรแกรมหลายตัวอ่านไม่ได้ — ตั้งชื่อแบบ UPPER_SNAKE_CASE",
  """Index cards with odd titles pass through a gate unchanged, but a grumpy shell-terminal kiosk cannot read them; a
  neat card with an underscore name is read easily. Nong Som recommends the neat one.""",
  ["1bad", "shop.name", "SHOP_NAME", "ตั้งชื่อแบบ SHOP_NAME"],
  "'1bad' and 'shop.name' on the odd cards; 'SHOP_NAME' on the neat card; 'ตั้งชื่อแบบ SHOP_NAME' as a title banner",
  nt=True)

S6 = "6. ใช้ ConfigMap เป็นไฟล์ (volume)"
t("volume-whole", S6,
  "volumes.configMap: ทุก key กลายเป็นไฟล์ชื่อเดียวกับ key ในโฟลเดอร์ที่ mount เช่น /etc/som/announcement.txt — ระบบไฟล์เป็น read-only",
  """Inside a booth: a small notice board on the wall that mirrors the zone board, each card shown as a file folder icon
  under a path sign. A staff member tries writing on a card and the pen bounces off. Nong Som explains.""",
  ["/etc/som", "announcement.txt", "Read-only file system", "key = ชื่อไฟล์"],
  "'/etc/som' on the path sign; 'announcement.txt' on one file icon; 'Read-only file system' on a red card near the pen; 'key = ชื่อไฟล์' as a title banner",
  nt=True)
t("volume-items", S6,
  "items เลือกเฉพาะบาง key และตั้ง path ใหม่ได้ เช่น key menu.txt → menu/today.txt; key อื่นไม่ถูก mount",
  """The deckhand robot picks only one card from the zone board and slides it into a labeled sub-folder on the booth
  board; other cards stay on the zone board. Nong Som ticks a checklist.""",
  ["items", "menu.txt → menu/today.txt", "เลือกเฉพาะบางการ์ด"],
  "'items' on the robot's tote bag; the arrow label on the slid card; 'เลือกเฉพาะบางการ์ด' as a title banner")
t("default-mode", S6,
  "defaultMode: 0400 → ไฟล์ -r-------- อ่านได้เฉพาะเจ้าของ (ค่าปกติ 0644); YAML ใช้เลขฐานแปดนำหน้าด้วย 0",
  """A card in a booth folder with a small permission tag showing three slots; only the first slot has a reading-eye
  icon. Nong Som holds a dial set to a number.""",
  ["defaultMode: 0400", "-r--------", "เจ้าของอ่านได้คนเดียว"],
  "'defaultMode: 0400' on the dial; '-r--------' on the permission tag; 'เจ้าของอ่านได้คนเดียว' as a title banner",
  nt=True)
t("subpath-single-file", S6,
  "subPath: mount ไฟล์เดียวลงในโฟลเดอร์ที่มีไฟล์อื่นอยู่แล้วโดยไม่ทับทั้งโฟลเดอร์ — แต่ไฟล์ subPath จะไม่อัปเดตเมื่อแก้ ConfigMap",
  """A booth wall with existing posters; a single photocopied card is taped among them. The deckhand robot walks past it
  with new cards but cannot replace the taped one. Nong Som frowns at the old card.""",
  ["subPath", "ไม่ทับไฟล์อื่น", "แต่ไม่อัปเดต"],
  "'subPath' on the taped card; 'ไม่ทับไฟล์อื่น' over the existing posters; 'แต่ไม่อัปเดต' as a red title banner",
  nt=True)

S7 = "7. ConfigMap หรือ key ที่ไม่มี และ optional"
t("missing-configmap", S7,
  "อ้าง ConfigMap/key ที่ไม่มี → Pod ค้าง CreateContainerConfigError (configmap \"not-here\" not found / couldn't find key NOPE in ConfigMap default/shop-config); ถ้าเป็น volume → ContainerCreating + FailedMount",
  """Two booths stuck at the dock with red lamps: one staff member stands at an empty board hook, the other holds a card
  slot with no matching card; a third booth waits with its door half-built. Nong Som reads error cards.""",
  ["CreateContainerConfigError", "configmap \"not-here\" not found", "couldn't find key NOPE", "FailedMount", "ไม่มีกระดาน = เข้ากะไม่ได้"],
  "'CreateContainerConfigError' on the first booth status sign; the two quoted messages on two red cards; 'FailedMount' on the half-built booth; last label as a title banner",
  nt=True)
t("optional-true", S7,
  "optional: true → ไม่มีก็เริ่มได้ (env ว่าง, โฟลเดอร์ว่าง); สร้าง ConfigMap ภายหลัง Pod ที่ค้างจะเริ่มเองโดยไม่ต้องลบ (ทดสอบแล้ว)",
  """Left: a booth with an empty board hook still opens with a green lamp and a small optional tag. Right: a board is
  delivered to a waiting booth and its lamp turns green by itself. Nong Som gives a thumbs up.""",
  ["optional: true", "ไม่มีก็เปิดได้", "มากระดานแล้วเปิดเอง"],
  "'optional: true' on the tag; 'ไม่มีก็เปิดได้' above left; 'มากระดานแล้วเปิดเอง' above right",
  nt=True)

S8 = "8. การอัปเดต ConfigMap"
t("env-no-update", S8,
  "แก้ ConfigMap แล้ว env ใน Pod เดิมไม่เปลี่ยน (ค่าถูกคัดลอกตอนเริ่มเท่านั้น) — ต้องได้ Pod ใหม่",
  """The zone board shows a new card value, but a staff member still wears the old chest card; a clock shows minutes
  passing. Nong Som points from the board to the old chest card.""",
  ["ConfigMap ใหม่", "ป้ายติดอกยังเก่า", "env ต้องเข้ากะใหม่"],
  "'ConfigMap ใหม่' on the board; 'ป้ายติดอกยังเก่า' on the chest card; 'env ต้องเข้ากะใหม่' as a title banner",
  nt=True)
t("volume-auto-update", S8,
  "ไฟล์จาก volume อัปเดตเองโดยไม่ restart แต่ช้า: kubelet sync + cache → วัดได้ราว 1 นาที (56–85 วินาที)",
  """The deckhand robot walks from the zone board to the booth carrying a fresh card; a stopwatch above shows about one
  minute; the booth staff smile as the booth board changes. Nong Som holds the stopwatch.""",
  ["kubelet", "≈ 1 นาที", "ไฟล์เปลี่ยนเอง ไม่ต้อง restart"],
  "'kubelet' on the robot; '≈ 1 นาที' on the stopwatch; 'ไฟล์เปลี่ยนเอง ไม่ต้อง restart' as a title banner",
  nt=True)
t("data-symlink-swap", S8,
  "เบื้องหลัง: ไฟล์จริงอยู่ในโฟลเดอร์ ..2026_10_05_… และ ..data เป็น symlink ชี้รุ่นล่าสุด — kubelet เขียนชุดใหม่แล้วสลับลิงก์ทีเดียว ไฟล์จึงไม่ครึ่ง ๆ กลาง ๆ",
  """Inside the booth board: two stacks of cards with timestamp tabs; a small arrow sign swings from the old stack to the
  new stack in one move; the visible card pockets point at the arrow sign. Nong Som pulls the arrow lever.""",
  ["..data", "..2026_10_05_08_47_02", "สลับลิงก์ทีเดียว"],
  "'..data' on the arrow sign; '..2026_10_05_08_47_02' on the new stack tab (the old stack has no tab); 'สลับลิงก์ทีเดียว' as a title banner",
  nt=True)
t("app-must-reload", S8,
  "ไฟล์เปลี่ยนแล้วแต่แอปที่อ่านไฟล์ครั้งเดียวตอนเริ่ม (เช่น nginx) ยังใช้ค่าเก่า → ต้องสั่ง nginx -s reload หรือให้แอปอ่านไฟล์ใหม่ทุกครั้ง",
  """A booth board already shows a new menu card, but the chef inside still cooks from an old menu sheet memorized in a
  thought bubble; Nong Som rings a small bell to make the chef re-read the board.""",
  ["ไฟล์ใหม่แล้ว", "nginx ยังตอบ v2", "nginx -s reload", "แอปต้องอ่านใหม่เอง"],
  "'ไฟล์ใหม่แล้ว' on the booth board; 'nginx ยังตอบ v2' in the chef's thought bubble; 'nginx -s reload' on the bell; 'แอปต้องอ่านใหม่เอง' as a title banner",
  nt=True)
t("rollout-restart-checksum", S8,
  "ให้ Pod ใหม่รับค่า: kubectl rollout restart (เพิ่ม annotation kubectl.kubernetes.io/restartedAt) หรือใส่ checksum ของ config ใน template annotation — แก้ config แล้ว checksum เปลี่ยน → rollout เอง",
  """The store-manager robot swaps booths one by one; a blueprint card carries a small annotation tag with a stamped
  code; a new code tag replaces the old one and triggers the swap. Nong Som presses a restart button.""",
  ["rollout restart", "restartedAt", "checksum/config", "เปลี่ยนเลขแล้ว Pod ใหม่"],
  "'rollout restart' on the button; 'restartedAt' and 'checksum/config' on two annotation tags; 'เปลี่ยนเลขแล้ว Pod ใหม่' as a title banner",
  nt=True)

S9 = "9. immutable: ConfigMap ที่แก้ไม่ได้"
t("immutable", S9,
  "immutable: true → แก้ data ไม่ได้ (data: Forbidden: field is immutable when `immutable` is set) และเปลี่ยนกลับเป็น false ไม่ได้ ต้องลบสร้างใหม่หรือใช้ชื่อใหม่; kubelet ไม่ต้องคอยเฝ้า ลดภาระ API server",
  """A notice board sealed under a clear laminated acrylic sheet with a round seal sticker; Nong Som tries to move a card
  but her paw stops on the sheet; next to it a fresh board with a new name plate -v2 is carried in.""",
  ["immutable: true", "field is immutable", "ใช้ชื่อใหม่ -v2", "แก้ไม่ได้ ต้องสร้างใหม่"],
  "'immutable: true' on the seal sticker; 'field is immutable' on a red card; 'ใช้ชื่อใหม่ -v2' on the new board's name plate; 'แก้ไม่ได้ ต้องสร้างใหม่' as a title banner",
  nt=True)

S10 = "10. kustomize configMapGenerator"
t("kustomize-generator", S10,
  "kubectl apply -k: configMapGenerator สร้างชื่อมี hash (web-config-gh5tkgmddg) และแก้ชื่อใน Deployment ให้; แก้ไฟล์ → ชื่อใหม่ → Deployment rollout เอง (ตัวเก่าค้างไว้ ต้องลบเอง)",
  """A label-printer machine prints a new notice board with a code tag; the store-manager robot automatically swaps the
  booth blueprint to the new board name; the older board stays leaning in a corner. Nong Som feeds a file into the printer.""",
  ["kubectl apply -k", "web-config-gh5tkgmddg", "web-config-6db7mkcg8t", "ชื่อใหม่ = rollout เอง", "ตัวเก่าต้องลบเอง"],
  "'kubectl apply -k' on the printer; the two hashed names on the old (corner) and new boards; 'ชื่อใหม่ = rollout เอง' as a title banner; 'ตัวเก่าต้องลบเอง' on a small sign by the corner board",
  nt=True)

S11 = "11. ConfigMap ในคลัสเตอร์จริง, ข้าม namespace และ RBAC"
t("kube-system-examples", S11,
  "ระบบเองก็ใช้ ConfigMap: kube-system มี coredns (Corefile), kube-proxy (config.conf), kubelet-config; ทุก namespace มี kube-root-ca.crt ให้อัตโนมัติ",
  """The harbor control tower has its own notice boards on its wall: one for the DNS directory clerk, one for the gangway
  door keeper, one for the deckhands; every painted zone has a small certificate card board. Nong Som tours the tower.""",
  ["coredns", "kube-proxy", "kubelet-config", "kube-root-ca.crt", "ระบบก็ใช้กระดานประกาศ"],
  "'coredns', 'kube-proxy', 'kubelet-config' on three tower boards; 'kube-root-ca.crt' on a zone board; last label as a title banner",
  nt=True)
t("cross-namespace", S11,
  "Pod ใน namespace other อ้าง shop-config ของ default → CreateContainerConfigError: configmap \"shop-config\" not found — ต้องสร้างสำเนาใน namespace นั้นเอง",
  """A booth in the other zone shows a red lamp and an error card while the board it wants stands across the zone line;
  Nong Som carries a copy of the board over the line.""",
  ["configmap \"shop-config\" not found", "default", "other", "คัดลอกไปไว้ในโซนนั้น"],
  "the English error on the red card; 'default' and 'other' on the two zone signs; 'คัดลอกไปไว้ในโซนนั้น' as a title banner",
  nt=True)
t("rbac-configmap", S11,
  "สิทธิ์ ConfigMap แยกตามคำกริยา: Role get,list configmaps → อ่านได้ แต่ patch ไม่ได้ (Forbidden ... cannot patch resource \"configmaps\") และอ่านใน namespace อื่นไม่ได้",
  """A staff silhouette with a grey ID card reads the board happily, but when trying to move a card a red X sign appears;
  another zone's board is behind a rope. Nong Som checks a permission clipboard.""",
  ["get, list = อ่านได้", "patch = Forbidden", "คนละโซน = Forbidden", "สิทธิ์แยกตามการกระทำ"],
  "'get, list = อ่านได้' near the reading staff; 'patch = Forbidden' on the red X; 'คนละโซน = Forbidden' on the rope; last label as a title banner",
  nt=True)

S12 = "12. แนวปฏิบัติและสรุป"
t("env-vs-volume", S12,
  "ตารางเลือก: env/envFrom เหมาะกับค่าสั้น อ่านครั้งเดียวตอนเริ่ม เปลี่ยนต้อง restart; volume เหมาะกับไฟล์ตั้งค่า/ข้อความยาว อัปเดตเองได้ (~1 นาที) แต่แอปต้องอ่านใหม่; subPath ไม่อัปเดต",
  """A clean comparison board with three columns: chest note card, booth notice board, taped photocopy card; each column has
  one result card under its header. Nong Som points with a pointer.""",
  ["env / envFrom", "volume", "subPath", "ต้อง restart", "อัปเดตเอง ~1 นาที", "ไม่อัปเดต"],
  "'env / envFrom', 'volume', 'subPath' as the three column headers; 'ต้อง restart' under env, 'อัปเดตเอง ~1 นาที' under volume, 'ไม่อัปเดต' under subPath; no other rows")
t("best-practices", S12,
  "แนวปฏิบัติ: เก็บ ConfigMap เป็น YAML ใน git, ตั้งชื่อ key ชัด, ไม่ใส่ความลับ, ใช้ immutable/ชื่อมีเวอร์ชันสำหรับค่าที่ไม่ควรเปลี่ยนกลางทาง, ใช้ checksum หรือ generator ให้ rollout เมื่อ config เปลี่ยน",
  """A checklist poster on the dock with exactly four checkboxes and small icons (a binder, a crossed-out dotted card,
  a laminated board, a code tag). Nong Som ticks the boxes.""",
  ["เก็บ YAML ใน git", "ไม่ใส่ความลับ", "ใช้ชื่อมีเวอร์ชัน", "แก้แล้วต้อง rollout", "แนวปฏิบัติ ConfigMap"],
  "the first four labels on the four checklist rows; 'แนวปฏิบัติ ConfigMap' as a title banner")
t("summary-map", S12,
  "สรุปบท: สร้าง (literal/file/env-file/YAML) → ใช้ (env, envFrom, volume, items, subPath) → อัปเดต (restart vs อัปเดตเอง) → ป้องกัน (immutable, RBAC)",
  """A four-stop route on the harbor map with a path connecting four signposts, each with a small icon (pen, booth,
  deckhand robot, laminated board). Nong Som walks the route.""",
  ["สร้าง", "ใช้", "อัปเดต", "ป้องกัน", "เส้นทาง ConfigMap"],
  "the first four labels on the four signposts in order; 'เส้นทาง ConfigMap' as a title banner")
t("command-cheatsheet", S12,
  "cheatsheet: kubectl create configmap / get cm -o yaml / describe cm / edit cm / rollout restart / apply -k",
  """A tidy cheat sheet card pinned on the board with six command rows and small icons. Nong Som holds a magnifier.""",
  ["kubectl create configmap", "kubectl get cm -o yaml", "kubectl describe cm", "kubectl rollout restart", "kubectl apply -k", "คำสั่งที่ใช้บ่อย"],
  "first five labels as rows on the card; 'คำสั่งที่ใช้บ่อย' as the card title")
t("next-chapter-password", S12,
  "ปัญหาที่เหลือ: รหัส meow1234 ใน DATABASE_URL และ POSTGRES_PASSWORD ยังเขียนตรงใน YAML ใครดู Deployment/ConfigMap ก็เห็น → บท 011 Secret ซองปิดผนึก",
  """The open notice board in the plaza with a card showing dots, a passer-by silhouette peeking at it; at the right edge a
  navy envelope with an orange paw wax seal waits on a pedestal as the next stop. Nong Som points to the envelope.""",
  ["●●●● ใครก็เห็น", "บทที่ 11", "Secret", "ซ่อนรหัสผ่านให้ดี"],
  "'●●●● ใครก็เห็น' on the peeked card; 'บทที่ 11' on the pedestal; 'Secret' on the envelope tag; 'ซ่อนรหัสผ่านให้ดี' as a title banner",
  allow=True)

# ---------------------------------------------------------------- LAB
l("lab0-prepare", "LAB0 เตรียมคลัสเตอร์และ image",
  "LAB0: 3 Node Ready, โหลด postgres:17.11-alpine (docker save --platform linux/amd64 + kind load image-archive) และ build som-shop-web:1.5 แล้ว kind load docker-image",
  """Three ships at the dock with a crane loading two shipping containers onto every ship; one container has a fresh
  paint label for a new version. Nong Som checks a clipboard.""",
  ["3 Node Ready", "postgres:17.11-alpine", "som-shop-web:1.5", "เตรียมของให้ครบทุกเรือ"],
  "'3 Node Ready' on the clipboard; the two image names on the two containers; last label as a title banner")
l("lab1-create", "LAB1 ส่องและสร้าง ConfigMap",
  "LAB1: ดู ConfigMap ใน kube-system และ kube-root-ca.crt แล้วสร้างด้วย --from-literal / --from-file / --from-env-file / --dry-run=client -o yaml; สร้างซ้ำได้ already exists; ไฟล์ 1.1 MB ได้ Too long",
  """Nong Som at a workbench with four tools in a row (pen, folder, slicer, printer) producing notice boards; behind her
  the control tower's boards; a red card on the bench.""",
  ["--from-literal", "--from-file", "--from-env-file", "--dry-run=client", "configmaps \"demo\" already exists", "สร้างได้ 4 แบบ"],
  "the four flags on the four tools; the English error on the red card; 'สร้างได้ 4 แบบ' as a title banner",
  nt=True)
l("lab2-env-key", "LAB2 env ทีละ key และ $(VAR)",
  "LAB2: Pod envpod ใช้ configMapKeyRef ตั้ง SHOP_NAME และ args \"$(SHOP_NAME)\" \"$(NOPE)\" → log ARGS: ร้านน้องส้ม $(NOPE)",
  """A staff member with a chest card; a speech-free log scroll from the booth shows one line of output. Nong Som reads
  the scroll.""",
  ["configMapKeyRef", "ARGS: ร้านน้องส้ม $(NOPE)", "ตัวที่ไม่มีไม่ถูกแทน"],
  "'configMapKeyRef' on the chest card; 'ARGS: ร้านน้องส้ม $(NOPE)' on the scroll; last label as a title banner",
  nt=True)
l("lab3-envfrom", "LAB3 envFrom, prefix และลำดับความสำคัญ",
  "LAB3: envFrom + prefix CFG_ ได้ทุก key รวม CFG_1bad, CFG_shop.name; ตั้ง env ชื่อเดียวกัน → env ชนะ; $(POD_NAMESPACE) ในค่าจาก envFrom ไม่ถูกแทน",
  """A stack of stamped chest cards; one card written in the blueprint lies on top of a same-name card; an aside card shows
  an unfilled placeholder. Nong Som sorts the stack.""",
  ["CFG_SHOP_NAME", "CFG_1bad", "env ชนะ envFrom", "$(POD_NAMESPACE) ไม่ถูกแทน"],
  "first two labels on two stamped cards; 'env ชนะ envFrom' on the top card; last label on the aside card",
  nt=True)
l("lab4-missing-optional", "LAB4 ConfigMap ที่ไม่มีและ optional",
  "LAB4: nocm/nokey ค้าง CreateContainerConfigError, novol ค้าง ContainerCreating (FailedMount), optpod Running; สร้าง not-here ภายหลัง → ทุกตัว Running เอง; Pod ใน namespace other อ้างข้าม namespace ไม่ได้",
  """Four booths in a row: two with red lamps and error cards, one half-built, one open with an optional tag; then a
  board is delivered and all lamps turn green. Nong Som delivers the board.""",
  ["CreateContainerConfigError", "ContainerCreating", "optional: true", "มากระดานแล้ว Running เอง"],
  "'CreateContainerConfigError' over the two red booths; 'ContainerCreating' on the half-built booth; 'optional: true' on the open booth; last label as a title banner",
  nt=True)
l("lab5-volume", "LAB5 mount เป็นไฟล์",
  "LAB5: volpod เห็นทุก key เป็นไฟล์ (symlink → ..data), items → menu/today.txt, defaultMode 0400 → -r--------, subPath → /etc/som/announcement.txt, เขียนไฟล์ได้ Read-only file system",
  """A cutaway booth wall with three small boards (full board, one-card sub-folder, taped single card) and a pen bouncing
  off. Nong Som points at each with a pointer.""",
  ["..data", "menu/today.txt", "-r--------", "Read-only file system", "ไฟล์จาก ConfigMap"],
  "'..data' on the full board arrow sign; 'menu/today.txt' on the sub-folder; '-r--------' on its permission tag; 'Read-only file system' on a red card by the pen; last label as a title banner",
  nt=True)
l("lab6-update-timing", "LAB6 อัปเดตเองและจับเวลา",
  "LAB6: patch shop-config 3 รอบ → ไฟล์ใน volume เปลี่ยนหลัง 65/70/85 วินาที; ไฟล์ subPath ยังเป็นค่าเดิม; env ใน envpod ยังเป็นค่าเดิม",
  """Three lanes with stopwatches; lane 1 the booth board updates after the deckhand arrives, lane 2 the taped card stays
  old, lane 3 the chest card stays old. Nong Som records times on a clipboard.""",
  ["volume: 65–85 วินาที", "subPath: ค่าเดิม", "env: ค่าเดิม", "จับเวลาการอัปเดต"],
  "the first three labels on the three lanes; 'จับเวลาการอัปเดต' as a title banner",
  nt=True)
l("lab7-nginx-reload", "LAB7 แอปต้องโหลดใหม่เอง",
  "LAB7: nginx อ่าน default.conf จาก ConfigMap → แก้เป็น menu v3 ไฟล์เปลี่ยน (~56 วินาที) แต่ curl ยังได้ menu v2 จนกว่าจะ nginx -s reload; rollout restart / checksum annotation ให้ Pod ใหม่",
  """The chef booth: the wall board shows a new menu card, the chef still serves the older dish; Nong Som rings a bell and
  the chef serves the new dish. A restart button on the side.""",
  ["menu v2", "nginx -s reload", "menu v3", "rollout restart", "ไฟล์เปลี่ยน ≠ แอปเปลี่ยน"],
  "'menu v2' on the old dish; 'nginx -s reload' on the bell; 'menu v3' on the new dish; 'rollout restart' on the side button; last label as a title banner",
  nt=True)
l("lab8-immutable", "LAB8 immutable",
  "LAB8: ConfigMap frozen (immutable: true) → patch/apply/replace ได้ field is immutable when `immutable` is set ทั้ง data และ immutable; แก้ label ได้; ต้อง delete แล้วสร้างใหม่",
  """A laminated board with a seal sticker; three tools (patch, apply, replace) bounce off the sheet; a label tag can still be
  hung on the frame. Nong Som finally carries the board to a recycle bin and brings a new one.""",
  ["immutable: true", "field is immutable", "label ได้", "ลบแล้วสร้างใหม่"],
  "'immutable: true' on the sticker; 'field is immutable' on a red card; 'label ได้' on the hanging tag; 'ลบแล้วสร้างใหม่' as a title banner",
  nt=True)
l("lab9-kustomize", "LAB9 kustomize configMapGenerator",
  "LAB9: kubectl apply -k kz → web-config-gh5tkgmddg; แก้ announcement.txt แล้ว apply -k → web-config-6db7mkcg8t + deployment configured (REVISION 2) ตัวเก่ายังค้าง",
  """A label printer prints board after board; the manager robot swaps the booth to the newest board; an older board leans
  in a corner. Nong Som feeds an edited file.""",
  ["web-config-gh5tkgmddg", "web-config-6db7mkcg8t", "REVISION 2", "แก้ไฟล์แล้ว rollout เอง"],
  "the two hashed names on the old and new boards; 'REVISION 2' on the manager's logbook; last label as a title banner",
  nt=True)

F = "LAB10 ร้านน้องส้มเปลี่ยนป้ายไม่ต้อง build ใหม่"
l("lab10-architecture", F,
  "LAB10 ภาพรวม: web 3 Pod (som-shop-web:1.5) อ่าน som-web-config ผ่าน envFrom และ mount som-announcement ที่ /etc/som; db StatefulSet som-db-0 เหมือนบท 009; NodePort 30080",
  """Harbor overview: three web booths across two ships each with a chest-card staff member and a small booth notice board;
  a zone notice board and a smaller announcement board stand in the plaza; the kitchen booth -0 above its safe; a
  lighthouse counter with a numbered gangway. Nong Som stands at the plaza.""",
  ["som-web-config", "som-announcement", "envFrom", "/etc/som", "NodePort 30080", "ร้านน้องส้มแบบใช้กระดาน"],
  "'som-web-config' on the zone board; 'som-announcement' on the announcement board; 'envFrom' on an arrow to a chest card; '/etc/som' on a booth board; 'NodePort 30080' on the gangway; last label as a title banner")
l("lab10-start", F,
  "ขั้น A: apply k8s-start/ (1.5 แต่ค่ายังเขียนใน env เหมือนบท 009) → สั่ง 3 ออเดอร์ → /api/stats orders=3, /api/announcement ตอบ (ไม่มีประกาศ)",
  """The shop opens with hand-written chest cards on staff; an order ledger counter shows three; an empty announcement frame.
  Nong Som rings up orders.""",
  ["k8s-start/", "orders=3", "(ไม่มีประกาศ)", "จุดเริ่มต้นเหมือนบท 009"],
  "'k8s-start/' on the blueprint; 'orders=3' on the counter; '(ไม่มีประกาศ)' on the empty frame; last label as a title banner",
  nt=True)
l("lab10-envfrom", F,
  "ขั้น B: apply 15-config.yaml + k8s/20-web.yaml → web ใช้ envFrom som-web-config; /api/shop แสดง shopName/theme/eyebrow/footer จาก ConfigMap; ออเดอร์ยัง 3",
  """The manager robot replaces booths; each new staff member gets a chest card copied from the zone board instead of the
  blueprint. Nong Som compares a JSON card from the counter.""",
  ["envFrom: som-web-config", "/api/shop", "orders=3", "ค่ามาจากกระดาน"],
  "'envFrom: som-web-config' on the copy arrow; '/api/shop' on the JSON card; 'orders=3' on the counter; last label as a title banner",
  nt=True)
l("lab10-edit-no-change", F,
  "ขั้น C1: patch som-web-config เป็นชื่อสาขาท่าเรือ ธีม sunset และโปรโมชัน → รอ 90 วินาที /api/shop ยังเป็นค่าเดิม (env ไม่อัปเดตเอง)",
  """The zone board has new sunset-colored cards; the booths still show the old harbor-blue signs and staff still wear old
  chest cards; a stopwatch shows 90. Nong Som taps her foot.""",
  ["90 วินาที", "harbor", "ป้ายร้านยังเก่า"],
  "'90 วินาที' on the stopwatch; 'harbor' on an old booth sign; 'ป้ายร้านยังเก่า' as a title banner",
  nt=True)
l("lab10-rollout-restart", F,
  "ขั้น C2: kubectl rollout restart deploy/som-web → Pod ใหม่ได้ชื่อร้าน \"ร้านน้องส้ม สาขาท่าเรือ\" ธีม sunset และแถบโปรโมชัน; orders=3 เท่าเดิม",
  """Booths swapped one by one; the new booths have sunset-colored awnings and a promo ribbon; the order counter still shows
  three. Nong Som cheers.""",
  ["rollout restart", "theme-sunset", "🎉 โปรวันนี้", "ไม่ต้อง build ใหม่", "orders=3"],
  "'rollout restart' on the manager robot's display; 'theme-sunset' on a new awning; '🎉 โปรวันนี้' on the promo ribbon; 'ไม่ต้อง build ใหม่' as a title banner; 'orders=3' on the counter",
  nt=True)
l("lab10-footer-pitfall", F,
  "ขั้นเสริม: ถ้าใส่ $(POD_NAMESPACE) ในค่าของ ConfigMap จะได้ข้อความดิบ — ใช้ env SHOP_FOOTER ใน Deployment (env ชนะ envFrom) → namespace som-shop",
  """A footer card from the zone board shows an unfilled placeholder; a blueprint-written card placed on top shows the zone
  name filled in. Nong Som swaps the cards.""",
  ["$(POD_NAMESPACE)", "namespace som-shop", "env ทับค่าจาก ConfigMap"],
  "'$(POD_NAMESPACE)' on the bottom card; 'namespace som-shop' on the top card; last label as a title banner",
  nt=True)
l("lab10-announcement-mount", F,
  "ขั้น D1: som-announcement mount เป็นโฟลเดอร์ /etc/som (ไม่ใช้ subPath) แอป 1.5 อ่านไฟล์ทุก request → /api/announcement และแถบ 📢 บนหน้าเว็บ",
  """Inside each booth a small announcement board hangs on the wall; the shop web page window shows a yellow announcement banner.
  Nong Som reads the banner.""",
  ["/etc/som/announcement.txt", "อ่านทุก request", "ประกาศหน้าร้าน"],
  "'/etc/som/announcement.txt' on the booth board; 'อ่านทุก request' on an arrow from board to the web window; 'ประกาศหน้าร้าน' on the yellow banner",
  nt=True)
l("lab10-announcement-update", F,
  "ขั้น D2: apply ประกาศใหม่ \"ปิดร้านเร็ว 18:00 น. ⛵\" → Pod แรกเปลี่ยนหลัง ~58 วินาที ทุก Pod ภายใน ~75 วินาที โดย RESTARTS 0 และ AGE เดิม",
  """The deckhand robots on both ships carry the new announcement card into each booth; a stopwatch shows about one minute;
  booth lamps stay green the whole time. Nong Som holds the stopwatch.""",
  ["ปิดร้านเร็ว 18:00 น. ⛵", "≈ 1 นาที", "RESTARTS 0", "เปลี่ยนเองไม่ต้อง restart"],
  "'ปิดร้านเร็ว 18:00 น. ⛵' on the new card; '≈ 1 นาที' on the stopwatch; 'RESTARTS 0' on a booth status plate; last label as a title banner",
  nt=True)
l("lab10-immutable-v2", F,
  "ขั้น E: สร้าง som-web-config-v2 (immutable: true) แล้วเปลี่ยน envFrom ไปชื่อใหม่ → rollout เอง; patch v2 ได้ field is immutable; rollout undo กลับ som-web-config",
  """A laminated -v2 board is carried in; the manager robot swaps booths to read from it; a pen bounces off the laminated
  sheet; then the robot flips its logbook back one page. Nong Som directs.""",
  ["som-web-config-v2", "immutable: true", "field is immutable", "rollout undo", "เปลี่ยนชื่อ = rollout"],
  "'som-web-config-v2' on the new board; 'immutable: true' on its seal; 'field is immutable' on a red card; 'rollout undo' on the logbook; last label as a title banner",
  nt=True)
l("lab10-password-visible", F,
  "ขั้น F: ServiceAccount intern ที่อ่านได้แค่ Pod/ConfigMap/Deployment ยังเห็น postgres://som:meow1234@... ใน kubectl get deploy -o yaml — รหัสผ่านไม่ควรอยู่ใน YAML/ConfigMap",
  """An intern staff silhouette with a grey ID card reads the store-manager robot's blueprint and spots a row with the password
  as dots highlighted by a magnifier. Nong Som looks alarmed.""",
  ["intern", "get deploy -o yaml", "som:●●●●@", "เด็กฝึกงานก็เห็นรหัส"],
  "'intern' on the ID card; 'get deploy -o yaml' on the blueprint header; 'som:●●●●@' on the highlighted row; last label as a title banner",
  nt=True)
l("lab10-wrap-up", F,
  "สรุป LAB10: ชื่อร้าน/ธีม/โปรโมชันอยู่ใน ConfigMap (เปลี่ยน + rollout restart), ประกาศอยู่ใน volume (เปลี่ยนเองใน ~1 นาที), ออเดอร์ยังอยู่ — เหลือรหัสผ่านที่ต้องย้ายไป Secret ในบท 011",
  """Nong Som stands proudly in front of the shop with sunset awnings and an announcement banner; a checklist card with three
  ticks; at the far right a navy envelope with a paw wax seal on a pedestal.""",
  ["ป้ายร้าน = ConfigMap", "ประกาศ = volume", "ออเดอร์ยังอยู่", "ต่อไป: Secret"],
  "first three labels as ticked checklist rows; 'ต่อไป: Secret' on the pedestal",
  allow=True)

if __name__ == "__main__":
    main()
