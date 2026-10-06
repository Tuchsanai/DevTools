#!/usr/bin/env python3
"""Storyboard ภาพบท 014 Helm → images.json + imagegen-prompts.md (รัน: python3 build_images.py)

ค่าที่ได้จาก pre-check (เวอร์ชัน chart, เลข revision, เวลา, ผล err=0 ฯลฯ) อยู่ใน labels (Text verbatim) ที่เดียว
Constraints อ้างป้ายด้วยหมายเลข "label N" — imgcommon ตรวจให้ว่าไม่มีตัวเลขจากป้ายซ้ำใน Scene/Constraints
ภาพที่ขึ้นกับผลทดสอบใส่ nt=True (needs_test) ให้ตรวจ/ปรับหลังเขียน LAB จริง
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from imgcommon import configure, t, l, main

configure("014")

KIT = "the franchise kit crate (navy-and-orange cardboard crate with a paw-print logo and a rope handle)"
ROBOT = "the contractor robot (orange-and-navy box-shaped builder robot with an orange safety hard hat and a tablet)"
FORM = "the customization order form (clipboard sheet with checkboxes, a theme color swatch and blank fields)"
BOOK = "the renovation logbook (thick spiral notebook with tabbed pages)"

# ================================================================ Theory
S1 = "1. บทนำ: ร้านน้องส้มอยากเปิดสาขาที่ 2"
t("opening-franchise-kit", S1,
  "เปิดบทที่ 14: ร้านน้องส้มขายดีจนอยากเปิดสาขาใหม่ น้องส้มจึงแพ็กร้านทั้งร้านเป็นชุดแฟรนไชส์สำเร็จรูปที่ใช้เปิดสาขาได้ด้วยคำสั่งเดียว",
  f"""The harbor dock at morning. Nong Som proudly presents {KIT}, lid open, showing a manual booklet, stencil molds
  and an order form inside. Behind her {ROBOT} waves; in the background the existing shop booth row and an empty
  painted zone waiting for a new branch.""",
  ["บทที่ 14", "Helm", "ชุดแฟรนไชส์ร้านสำเร็จรูป"],
  "label 1 as a title banner at the top; label 2 on the kit's lid label card; label 3 as a subtitle under the title")
t("recap-yaml-pile", S1,
  "ทวนบท 013: ร้านทั้งร้านคือไฟล์ YAML หลายแผ่น (namespace, db, config, web, admin, ingress, hpa, customers) บวก Traefik และ metrics-server ที่ติดตั้งด้วย static manifest — จะเปิดสาขาใหม่ต้องก็อปทั้งหมด",
  """Nong Som sits on a crate behind a tall wobbly stack of paper sheets, each sheet a plain page with a tiny booth
  icon; two separate bundles tied with string beside the stack (one with a receptionist robot sketch, one with a
  meter-reader robot sketch). She looks at the empty new zone with a worried face.""",
  ["ร้านบท 13 = ไฟล์ YAML หลายแผ่น", "Traefik (static)", "metrics-server (static)", "อยากเปิดสาขาที่ 2"],
  "label 1 on a tag on the big stack; label 2 on the receptionist bundle; label 3 on the meter-reader bundle; label 4 as a sign on the empty zone")
t("metaphor-legend-1", S1,
  "อุปมาใหม่ (1): chart = ชุดแฟรนไชส์, values = ใบสั่งปรับแต่งร้าน, templates = แม่พิมพ์ป้าย/บูธ, release = ร้านสาขาที่เปิดจริง, revision = สมุดบันทึกการปรับปรุงร้าน, helm = หุ่นยนต์ผู้รับเหมา",
  f"""A legend board with six rounded tiles in two rows: {KIT}; {FORM}; a stencil mold with empty curly-bracket
  slots; a branch shop booth with a name banner; {BOOK}; {ROBOT}. Nong Som points at the board.""",
  ["chart = ชุดแฟรนไชส์", "values = ใบสั่งปรับแต่งร้าน", "templates = แม่พิมพ์", "release = ร้านสาขา",
   "revision = สมุดบันทึกการปรับปรุงร้าน", "helm = หุ่นยนต์ผู้รับเหมา"],
  "each of the six tiles carries exactly one label in order label 1 to label 6; no other text on the board")
t("metaphor-legend-2", S1,
  "อุปมาใหม่ (2): repository/Artifact Hub = แคตตาล็อกแฟรนไชส์, OCI registry = โกดังเก็บชุดแฟรนไชส์, hook = ขั้นตอนพิเศษก่อน/หลังเปิดร้าน, helm test = ผู้ตรวจรับร้าน, values.schema.json = ด่านตรวจใบสั่ง",
  """A legend board with five rounded tiles: a franchise catalog brochure; a kit warehouse with numbered shelves and a
  turnstile; a special step card clipped to a manual with a shelf-stocking cart; a small white inspector robot with a
  magnifying glass and a green stamp; an inspection desk with a checklist. Nong Som holds a pointer.""",
  ["repository = แคตตาล็อกแฟรนไชส์", "OCI registry = โกดังเก็บชุดแฟรนไชส์", "hook = ขั้นตอนพิเศษก่อน/หลังเปิดร้าน",
   "helm test = ผู้ตรวจรับร้าน", "values.schema.json = ด่านตรวจใบสั่ง"],
  "each of the five tiles carries exactly one label in order label 1 to label 5; no other text on the board")
t("chapter-goals", S1,
  "เป้าหมายของบท: ชุดแฟรนไชส์ som-shop ชุดเดียว + ใบสั่งต่างกัน → เปิดสาขา dev และ prod ได้ด้วยคำสั่งเดียว อัปเกรด/ย้อนรุ่นทั้งร้านได้",
  f"""Center: {KIT}. Two arrows lead to two painted zones: left an orange zone with one small booth, right a navy zone
  with a row of booths behind a glass security door and an assistant-manager robot. {ROBOT} stands between them;
  Nong Som holds a plan board.""",
  ["ชุดแฟรนไชส์เดียว", "สาขา dev", "สาขา prod", "คำสั่งเดียวเปิดทั้งร้าน"],
  "label 1 on the crate; label 2 on the orange zone sign; label 3 on the navy zone sign; label 4 on Nong Som's plan board")

S2 = "2. ปัญหาของ YAML ล้วน"
t("yaml-duplicate-values", S2,
  "ค่าเดียวกันซ้ำหลายไฟล์: ชื่อร้าน, label, image tag อยู่หลายที่ แก้ไม่ครบเมื่อไรร้านเพี้ยน",
  """Three paper sheets pinned on a wall, the same small highlighted field circled in orange on each sheet; Nong
  Som with a pencil has corrected two sheets and missed the third, which shows a red mismatch spark.""",
  ["ค่าเดียวกันซ้ำหลายไฟล์", "แก้ไม่ครบ = ร้านเพี้ยน", "image tag / ชื่อ / label"],
  "label 1 as a title banner; label 2 next to the red spark; label 3 on a small note under the circled fields")
t("copy-folder-drift", S2,
  "อยากมีหลาย environment แบบ copy โฟลเดอร์แล้วแก้ = สองสาขาค่อย ๆ ต่างกันโดยไม่รู้ตัว (drift)",
  """Two identical folders placed side by side, an orange-tab folder and a navy-tab folder; thin arrows show small
  edits made only in one of them over time (a calendar strip under each); Nong Som compares them with a puzzled
  face.""",
  ["โฟลเดอร์ dev", "โฟลเดอร์ prod", "copy แล้วแก้ = ค่าเพี้ยนไม่รู้ตัว"],
  "label 1 on the orange-tab folder; label 2 on the navy-tab folder; label 3 as a title banner")
t("no-bundle-version", S2,
  "kubectl rollout history มีรุ่นเฉพาะ Deployment — ConfigMap, Secret, Ingress ไม่มีรุ่น ย้อนทั้งร้านพร้อมกันไม่ได้",
  """The store-manager robot holds its own revision logbook; next to it a notice board, a sealed envelope and the
  gate signboard stand with no logbook, each with a small grey question mark. Nong Som shrugs.""",
  ["rollout history มีแค่ Deployment", "ConfigMap / Secret / Ingress ไม่มีรุ่น", "ย้อนทั้งร้านพร้อมกันไม่ได้"],
  "label 1 on the robot's logbook; label 2 on a strip below the three items; label 3 as a title banner")
t("kubectl-vs-helm", S2,
  "เทียบ kubectl apply (ติดตั้งทีละไฟล์ ไม่มีชื่อชุด) กับ helm install (ติดตั้งเป็นชุดที่มีชื่อสาขาและรุ่น)",
  f"""Split scene. Left: Nong Som carries loose sheets one by one to the dock. Right: {ROBOT} opens {KIT} and a
  complete branch booth appears with a name banner and a logbook.""",
  ["kubectl apply -f", "ติดตั้งทีละไฟล์", "helm install", "ติดตั้งเป็นชุด + มีรุ่น"],
  "label 1 as the left panel header; label 2 under the left panel; label 3 as the right panel header; label 4 under the right panel")

S3 = "3. Helm คืออะไร"
t("package-manager", S3,
  "Helm = package manager ของ Kubernetes: chart เป็นแพ็กเกจ ติดตั้ง อัปเกรด ถอนออก ได้เป็นชุด",
  f"""{ROBOT} carries {KIT} from a catalog kiosk to an empty zone and unpacks it into a full shop; three small icons on
  a ribbon above: a down arrow (install), an up arrow (upgrade), a box with an exit arrow (uninstall). Nong Som
  watches with a clipboard.""",
  ["package manager ของ Kubernetes", "chart = แพ็กเกจ", "ติดตั้ง / อัปเกรด / ถอนออก"],
  "label 1 as a title banner; label 2 on the crate; label 3 on the icon ribbon")
t("five-words", S3,
  "ศัพท์หลัก 5 คำ: repository (ที่เก็บ) → chart (ชุด) + values (ใบสั่ง) → release (สาขาที่เปิดจริง) → revision (หน้าในสมุด)",
  f"""A left-to-right flow: a catalog brochure → {KIT} with {FORM} beside it → a branch shop with a name banner →
  {BOOK} open on its first page. Nong Som walks along the flow.""",
  ["repository", "chart", "values", "release", "revision", "ศัพท์ 5 คำของ Helm"],
  "label 1 to label 5 under the five items in flow order; label 6 as a title banner")
t("helm-history-tiller", S3,
  "ประวัติ: Helm 2 มี Tiller ตัวกลางสิทธิ์สูงในคลัสเตอร์ (ถูกเอาออก), Helm 3 ทำงานจากเครื่องเราอย่างเดียว, Helm 4 ใช้ server-side apply",
  """A three-step timeline on the dock. Step one: an old grey tower robot inside the harbor holding a big master key,
  crossed out with a red X. Step two: the contractor robot working from the dock with only Nong Som's staff card.
  Step three: the contractor robot pinning small orange owner tags on shop fittings.""",
  ["Helm 2: มี Tiller (เลิกใช้แล้ว)", "Helm 3: ไม่มี Tiller", "Helm 4: server-side apply", "วิวัฒนาการของ Helm"],
  "label 1 to label 3 under the three timeline steps in order; label 4 as a title banner")
t("helm4-whats-new", S3,
  "สิ่งที่เปลี่ยนใน Helm 4 ที่บทนี้ใช้: server-side apply เป็นค่าเริ่มต้น, --atomic → --rollback-on-failure, --force → --force-replace, plugin ต้องตรวจลายเซ็น, chart API ยังเป็น v2",
  f"""A notice card stand beside {ROBOT}, five rows each with a small icon (owner tag, back arrow, replace arrows,
  plugin with a seal, kit label card). Nong Som reads it with glasses.""",
  ["server-side apply เป็นค่าเริ่มต้น", "--atomic → --rollback-on-failure", "--force → --force-replace",
   "plugin ต้องตรวจลายเซ็น", "chart API v2 (v3 ยังทดลอง)", "Helm 4 เปลี่ยนอะไร"],
  "label 1 to label 5 as the five rows; label 6 as the card header")

S4 = "4. โครงสร้าง chart"
t("chart-anatomy", S4,
  "ข้างในชุดแฟรนไชส์: Chart.yaml (ฉลาก), values.yaml (ใบสั่ง), templates/ (แม่พิมพ์), _helpers.tpl (ตรายาง), values.schema.json (ด่านตรวจ), NOTES.txt (การ์ดต้อนรับ)",
  f"""{KIT} opened wide on a table, six items laid out around it with leader lines: a lid label card, an order form,
  a stack of stencil molds, a rack of rubber stamps, a small inspection checklist, a welcome card. Nong Som
  unpacks with excitement.""",
  ["Chart.yaml", "values.yaml", "templates/", "_helpers.tpl", "values.schema.json", "NOTES.txt", "ข้างในชุดแฟรนไชส์"],
  "label 1 to label 6 on the six items in the order listed in the scene; label 7 as a title banner")
t("version-vs-appversion", S4,
  "Chart.yaml มี 2 เลข: version = รุ่นของชุดแฟรนไชส์ (แก้แม่พิมพ์ต้องเพิ่ม) / appVersion = รุ่นแอปในร้าน",
  f"""Close-up of the kit's lid label card with two lines highlighted, one pointing to the crate itself and one
  pointing to a small shipping container (the app) inside the crate. Nong Som taps the card.""",
  ["version: 0.1.0 = รุ่นชุดแฟรนไชส์", "appVersion: 1.7 = รุ่นแอปในร้าน", "แก้แม่พิมพ์ → เพิ่ม version"],
  "label 1 on the line pointing to the crate; label 2 on the line pointing to the container; label 3 as a note at the bottom")
t("crds-and-subcharts", S4,
  "โฟลเดอร์พิเศษ: charts/ = ชุดย่อยในชุดใหญ่ และ crds/ = แบบพิมพ์ชนิดใหม่ที่ติดตั้งครั้งแรกเท่านั้น (upgrade/uninstall ไม่แตะ)",
  f"""Inside {KIT}: two smaller kit crates nested in one corner; in the other corner a sealed envelope of new form
  types with a one-time stamp. Nong Som holds a magnifier.""",
  ["charts/ = ชุดย่อย", "crds/ = ติดตั้งครั้งแรกเท่านั้น", "upgrade / uninstall ไม่แตะ CRD"],
  "label 1 on the nested crates; label 2 on the sealed envelope; label 3 as a note under the envelope")

S5 = "5. Go template และ Sprig ขั้นพื้นฐาน"
t("template-slots", S5,
  "แม่พิมพ์มีช่องว่าง {{ }} — เอาใบสั่ง (values) มาเติมช่อง ได้ป้ายร้านจริง",
  f"""A stencil mold of a shop sign with an empty slot shaped like double curly brackets; {FORM} feeds a name into the
  slot via a small funnel; a finished shop sign comes out on the right. Nong Som holds the finished sign.""",
  ["{{ .Values.shop.SHOP_NAME }}", "ร้านอาหารแมวน้องส้ม", "แม่พิมพ์ + ใบสั่ง = ป้ายจริง"],
  "label 1 inside the mold slot; label 2 on the finished sign; label 3 as a caption banner")
t("built-in-objects", S5,
  "ของที่แม่พิมพ์หยิบได้: .Values (ใบสั่ง), .Release (ข้อมูลสาขา), .Chart (ฉลากชุด), .Capabilities (ความสามารถของท่าเรือ)",
  """Four labeled trays on a workbench next to the stencil molds: an order form tray, a branch name banner tray, a
  kit label card tray, a tray with a small harbor capability plaque. Nong Som picks from the trays.""",
  [".Values = ใบสั่ง", ".Release = ข้อมูลสาขา", ".Chart = ฉลากชุด", ".Capabilities = ความสามารถของท่าเรือ"],
  "label 1 to label 4 on the four trays in order")
t("pipeline-default", S5,
  "pipeline: ค่าไหลผ่านฟังก์ชันทีละขั้น — ไม่ใส่ image tag ให้ใช้ appVersion ของ chart (default) แล้วใส่เครื่องหมายคำพูด (quote)",
  """A short conveyor belt: an empty tag card enters, passes a station that fills it from the kit label card, then a
  station that wraps it in quote marks, then exits as a finished tag. Nong Som presses the start button.""",
  ["{{ .Values.web.image.tag | default .Chart.AppVersion }}", "ไม่ใส่ tag → ใช้ appVersion", "pipeline ส่งต่อทีละขั้น"],
  "label 1 on a sign above the conveyor; label 2 on the filling station; label 3 as a caption banner")
t("nindent-vs-indent", S5,
  "toYaml | nindent ขึ้นบรรทัดใหม่และย่อหน้าตรง ส่วน indent ผิดที่ทำให้ YAML พัง (mapping values are not allowed)",
  """Two printed blueprints side by side. Left: neat aligned rows with a green check. Right: one row pushed onto the
  end of the previous line with a red X and a cracked edge. Nong Som measures with a ruler.""",
  ["toYaml | nindent 12 ✓", "indent ผิดที่ ✗ YAML พัง", "ย่อหน้าต้องตรง"],
  "label 1 above the left blueprint; label 2 above the right blueprint; label 3 as a caption banner")
t("if-range-with", S5,
  "โครงควบคุม: if = มีหรือไม่มีชิ้นนี้, range = ทำซ้ำทุกการ์ด, with = เปลี่ยนจุดอ้างอิง",
  """Three small stations: a switch that turns an assistant-manager robot booth on or off; a stamp that repeats one
  card shape into a row of cards on a notice board; a magnifier that zooms into one section of the order form.
  Nong Som demonstrates each.""",
  ["if = มีหรือไม่มี", "range = ทำซ้ำทุกการ์ด", "with = เปลี่ยนจุดอ้างอิง"],
  "label 1 to label 3 on the three stations in order")
t("helpers-include", S5,
  "_helpers.tpl = ตรายางที่ใช้ซ้ำ: define ครั้งเดียว include ได้ทุกไฟล์ (ชื่อ, label มาตรฐาน)",
  """A rack of rubber stamps on the wall; the contractor robot stamps the same neat label block onto several
  different molds (sign, booth, notice board). Nong Som hands over a stamp.""",
  ["_helpers.tpl = ตรายาง", "define / include", "label มาตรฐานทุกชิ้น"],
  "label 1 on the stamp rack; label 2 on a stamp handle; label 3 as a caption banner")
t("required-lookup", S5,
  "required = ช่องที่ห้ามว่าง (หยุดทันที), lookup = แอบดูของเดิมในคลัสเตอร์ (helm template มองไม่เห็น จึงได้ค่าว่าง)",
  """Left: the inspection desk stops an order form with an empty password field, a red stop paddle raised. Right: the
  contractor robot peeks into a zone cabinet and finds an existing sealed envelope; a printing table nearby has a
  blindfold drawn on it (cannot see the harbor). Nong Som points to both.""",
  ["required = ห้ามว่าง", "lookup = ดูของเดิมในคลัสเตอร์", "helm template มองไม่เห็นคลัสเตอร์"],
  "label 1 on the left panel; label 2 on the right panel; label 3 on the printing table")
t("checksum-rollout", S5,
  "checksum/config: แก้กระดานประกาศแล้วลายนิ้วมือเปลี่ยน → ได้บูธใหม่เอง ไม่ต้อง rollout restart แบบบท 010",
  """The notice board gets a new card; a fingerprint sticker on the booth blueprint changes color; the store-manager
  robot opens a fresh booth and closes the old one. Nong Som smiles.""",
  ["checksum/config", "แก้กระดาน → บูธใหม่เอง", "ไม่ต้อง rollout restart"],
  "label 1 on the fingerprint sticker; label 2 as a caption banner; label 3 on a crossed-out note")

S6 = "6. values และลำดับความสำคัญ"
t("values-precedence", S6,
  "ลำดับความสำคัญ: values.yaml ในชุด < ไฟล์ -f (ไฟล์หลังชนะ) < --set (บนสุดชนะ)",
  """A stack of three layers on a table: the default order form at the bottom, a navy-tab environment form on top of
  it, a bright sticky note on the very top; an arrow points upward. Nong Som presses the sticky note.""",
  ["values.yaml ในชุด", "-f values-prod.yaml", "--set web.image.tag=1.8", "ชั้นบนชนะ"],
  "label 1 on the bottom form; label 2 on the middle form; label 3 on the sticky note; label 4 on the upward arrow")
t("values-per-env", S6,
  "ชุดแฟรนไชส์เดียว + ใบสั่งคนละใบ = สาขา dev (บูธเดียว) และ prod (HPA + HTTPS)",
  f"""{KIT} in the middle; an orange-tab form leads to an orange zone with one booth; a navy-tab form leads to a navy
  zone with several booths, an assistant-manager robot and a glass security door. Nong Som stands at the kit.""",
  ["values-dev.yaml", "values-prod.yaml", "สาขา dev: บูธเดียว", "สาขา prod: HPA + HTTPS"],
  "label 1 on the orange-tab form; label 2 on the navy-tab form; label 3 on the orange zone sign; label 4 on the navy zone sign")
t("upgrade-values-trap", S6,
  "กับดัก: helm upgrade โดยไม่ส่งใบสั่งเดิม = กลับเป็นค่าเริ่มต้นของชุด (ค่าที่เคย --set หาย) ต้องส่ง -f ทุกครั้ง หรือ --reuse-values",
  f"""{ROBOT} rebuilds the branch using only the default form; the custom orange theme and extra booths disappear
  (ghost outlines). Nong Som runs in holding the forgotten navy-tab form.""",
  ["upgrade ไม่ส่งใบสั่ง = กลับค่าเริ่มต้น", "ส่ง -f ทุกครั้ง", "--reuse-values"],
  "label 1 as a title banner; label 2 on the form Nong Som holds; label 3 on a small side note")
t("schema-desk", S6,
  "values.schema.json = ด่านตรวจใบสั่ง: ค่าผิดชนิด/เกินช่วงถูกปฏิเสธก่อนสร้างอะไรเลย (เช่น replicas 9 เกิน 6, tag 1.4)",
  """The inspection desk with a checklist; an order form with a too-large booth count is stamped with a red reject
  stamp and pushed back; the contractor robot waits behind a closed rope. Nong Som reads the rejection.""",
  ["values.schema.json", "web.replicas = 9 ✗", "ตรวจก่อนสร้าง"],
  "label 1 on the desk sign; label 2 on the rejected form; label 3 as a caption banner")

S7 = "7. การ render และ debug"
t("render-table", S7,
  "helm template = พิมพ์พิมพ์เขียวออกมาดูโดยไม่สร้างจริง, helm lint = ตรวจชุด, --dry-run=server = ลองกับท่าเรือจริงแต่ไม่บันทึก",
  """A printing table where stencil molds and an order form produce paper blueprints (no booth is built); beside it a
  lint inspector checks the kit; in the corner a translucent ghost booth on the dock labelled as a trial. Nong Som
  reads a blueprint.""",
  ["helm template", "พิมพ์เขียว ไม่สร้างจริง", "helm lint", "--dry-run=server"],
  "label 1 on the printing table; label 2 on the blueprints; label 3 on the lint inspector; label 4 on the ghost booth")
t("common-errors", S7,
  "error ที่เจอบ่อย 4 แบบ: YAML parse error (ย่อหน้า), function not defined (สะกดฟังก์ชันผิด), required (ลืมค่า), schema (ค่าผิดกติกา)",
  """A board with four red error cards pinned in a grid, each with a small icon (crooked lines, misspelled stamp, empty
  field, rejected form). Nong Som holds a debug flashlight.""",
  ["YAML parse error", "function \"toYml\" not defined", "required: ห้ามว่าง", "schema: ค่าผิดกติกา", "error ที่เจอบ่อย"],
  "label 1 to label 4 on the four cards; label 5 as the board header")

S8 = "8. lifecycle ของ release"
t("lifecycle-cycle", S8,
  "วงจรชีวิตสาขา: install → upgrade → rollback → uninstall ทุกครั้ง (ยกเว้น uninstall) เขียนหน้าใหม่ในสมุด",
  f"""A circular path around a branch shop: four stations with icons (opening ribbon, renovation ladder, back arrow,
  closing shutter). {BOOK} in the center gains pages. Nong Som walks the circle.""",
  ["install", "upgrade", "rollback", "uninstall", "วงจรชีวิตของสาขา"],
  "label 1 to label 4 on the four stations in order; label 5 on the center logbook")
t("revision-logbook", S8,
  "rollback ไม่ได้ถอยเลขหน้า แต่เขียนหน้าใหม่ที่คัดลอกจากหน้าเก่า (เลข revision เพิ่มขึ้นเสมอ)",
  f"""{BOOK} open with four tabbed pages; an arrow copies the content of the second page onto a new fourth page. Nong
  Som writes on the new page.""",
  ["หน้า 1 install", "หน้า 2 upgrade", "หน้า 3 upgrade", "หน้า 4 = Rollback to 2", "rollback = หน้าใหม่ เลขไม่ถอย"],
  "label 1 to label 4 on the four page tabs in order; label 5 as a caption banner")
t("wait-strategies", S8,
  "ไม่ใส่ --wait: Helm บอก deployed ทั้งที่บูธยังพัง / --wait รอให้พร้อม / --rollback-on-failure ล้มแล้วถอยกลับเอง",
  f"""Three short panels. Panel one: {ROBOT} walks away with a thumbs-up while a booth behind shows a red lamp. Panel
  two: the robot waits beside the booth until its lamp turns green. Panel three: the booth lamp stays red, a timer
  rings, the robot restores the previous booth.""",
  ["ไม่ใส่ --wait: deployed แต่บูธยังพัง", "--wait: รอจนพร้อม", "--rollback-on-failure: ล้มแล้วถอยเอง"],
  "label 1 to label 3 as captions of the three panels in order")
t("rollback-no-number", S8,
  "กับดัก: helm rollback ไม่ระบุเลข = ถอยไปหน้าก่อนหน้า แม้หน้านั้นเป็นรุ่นที่ล้ม → ระบุเลข revision เสมอ",
  f"""{BOOK} where the previous page has a red failed stamp; an arrow from a rollback button lands on that failed page.
  Nong Som crosses it out and writes a page number on a sticky note.""",
  ["helm rollback som", "ถอยไปหน้าก่อนหน้า แม้เป็นรุ่นที่ล้ม", "ระบุเลข revision เสมอ"],
  "label 1 on the rollback button; label 2 next to the failed page; label 3 on Nong Som's sticky note")

S9 = "9. Helm 4 กับ server-side apply"
t("field-managers", S9,
  "server-side apply: ทุกช่องของ object มีป้ายชื่อเจ้าของ (field manager) เช่น helm, kubectl-client-side-apply, kube-controller-manager",
  """A booth blueprint pinned on a board; each fitting has a small owner tag: orange tags, grey tags and a few
  blue tags. Nong Som points to the tags with a pencil.""",
  ["helm", "kubectl-client-side-apply", "kube-controller-manager", "ป้ายเจ้าของทุกช่อง"],
  "label 1 on an orange tag; label 2 on a grey tag; label 3 on a blue tag; label 4 as a title banner")
t("ssa-conflict", S9,
  "conflict: ช่องเดียวมีเจ้าของ 2 คนอยากตั้งค่าต่างกัน → Helm หยุด, --force-conflicts = ยึดเป็นของ helm",
  f"""One fitting with a grey owner tag and an orange owner tag and a red spark between them; {ROBOT} holds a new
  orange tag ready to replace the grey one. Nong Som raises a caution hand.""",
  ["conflict", "ป้ายเจ้าของชนกัน", "--force-conflicts = ยึดเป็นของ helm"],
  "label 1 on the red spark; label 2 as a title banner; label 3 on the robot's tablet")
t("adopt-steps", S9,
  "รับของเดิมที่ kubectl apply ไว้: install ทับ → invalid ownership / --take-ownership → conflict / + --force-conflicts → ผ่าน (ถ้า selector ต่าง = field is immutable)",
  """A staircase of three steps up to an existing hand-built booth: step one has a closed gate, step two has a red
  spark between tags, step three shows the contractor robot pinning its branch banner on the booth; beside the
  stairs a locked side door with a padlock for a booth whose base plate shape differs. Nong Som climbs.""",
  ["invalid ownership metadata", "--take-ownership", "--force-conflicts", "selector ต่าง = field is immutable", "รับร้านเดิมทีละขั้น"],
  "label 1 to label 3 on the three steps in order; label 4 on the locked side door; label 5 as a title banner")

S10 = "10. release เก็บที่ไหน"
t("release-secret", S10,
  "release แต่ละ revision เก็บเป็น Secret type helm.sh/release.v1 แค่พับ (base64) และห่อ (gzip) ไม่ได้ล็อก — ใบสั่งที่มีรหัสจึงอ่านได้",
  f"""{BOOK} pages shrink-wrapped and stored in a navy steel cabinet drawer in the zone; one page is unwrapped on the
  desk, revealing a copy of the order form with a password line visible. Nong Som looks shocked.""",
  ["sh.helm.release.v1.som.v1", "type: helm.sh/release.v1", "base64 + gzip ≠ กุญแจ", "รหัสในใบสั่งอ่านได้"],
  "label 1 on the drawer label; label 2 on the cabinet; label 3 on the shrink-wrap; label 4 as a warning banner")

S11 = "11. hooks และ helm test"
t("hooks-timeline", S11,
  "hook = ขั้นตอนพิเศษตามจังหวะ: pre-install ก่อนสร้าง, post-install หลังสร้าง (เติมสินค้าเข้าชั้น), test = ตรวจรับร้าน",
  """A horizontal timeline along the dock: a step card before the booth is built, then the booth being built, then a
  shelf-stocking cart filling the kitchen shelves, then the inspector robot with a magnifier. Nong Som walks along
  the timeline.""",
  ["pre-install", "สร้างร้าน", "post-install: เติมสินค้า", "test: ตรวจรับร้าน"],
  "label 1 to label 4 on the four timeline points in order")
t("hook-delete-policy", S11,
  "hook-delete-policy: before-hook-creation (ค่าเริ่มต้น), hook-succeeded, hook-failed — และ helm uninstall ไม่ลบ hook ให้",
  """Three bins next to a finished shelf-stocking cart: a bin used before the next cart arrives, a bin with a green
  check, a bin with a red X; a leftover cart stays on the dock after the branch closes. Nong Som sweeps.""",
  ["before-hook-creation", "hook-succeeded", "hook-failed", "uninstall ไม่ลบ hook ให้"],
  "label 1 to label 3 on the three bins; label 4 on the leftover cart")
t("helm-test-inspector", S11,
  "helm test: Pod ตรวจรับร้านเรียก /api/health ถ้าจบด้วย exit 0 = Succeeded, --logs ดูผลตรวจ",
  """The white inspector robot with a magnifying glass checks a booth's health window and stamps a green approval
  stamp on its clipboard; a printed log strip comes out of the clipboard. Nong Som claps.""",
  ["helm test som --logs", "/api/health", "Phase: Succeeded", "ผู้ตรวจรับร้าน"],
  "label 1 on the clipboard header; label 2 on the health window; label 3 on the green stamp; label 4 on the inspector's badge")

S12 = "12. dependencies (subchart)"
t("subcharts", S12,
  "dependencies: ชุดใหญ่ใส่ชุดย่อยได้ (เช่น metrics-server) helm dependency update ดึงมาเก็บใน charts/ และล็อกเวอร์ชันใน Chart.lock",
  f"""A big {KIT} with two smaller kit crates being loaded inside by a small crane; a lock card is clipped to the lid.
  Nong Som checks a list.""",
  ["dependencies", "helm dependency update", "Chart.lock", "ชุดย่อยในชุดใหญ่"],
  "label 1 on Nong Som's list; label 2 on the crane; label 3 on the lock card; label 4 as a title banner")

S13 = "13. repository: HTTP vs OCI และ Artifact Hub"
t("http-vs-oci", S13,
  "repository แบบ HTTP = แคตตาล็อก (index.yaml + ไฟล์ .tgz) ต้อง repo add; OCI = โกดัง (oci://) ดึงตรงได้เลย",
  """Split scene. Left: a printed franchise catalog brochure with an index page and kit pictures. Right: a kit
  warehouse with numbered shelves, sealed crates with fingerprint stickers and a turnstile. Nong Som stands between
  them.""",
  ["HTTP repo: index.yaml", "OCI: oci://", "แคตตาล็อก vs โกดัง"],
  "label 1 on the brochure; label 2 on the warehouse gate; label 3 as a title banner")
t("artifact-hub", S13,
  "Artifact Hub = ที่ค้นชุดแฟรนไชส์จากหลายผู้เผยแพร่ — ชื่อเดียวกันไม่ได้แปลว่าเป็นของทางการ ดูป้ายผู้เผยแพร่ที่ยืนยันแล้ว",
  """A big catalog kiosk on the dock showing three kit cards with the same kit picture; only one card has a blue check
  badge. Nong Som compares them with a magnifier.""",
  ["Artifact Hub", "ชื่อซ้ำ ≠ ของทางการ", "ผู้เผยแพร่ที่ยืนยันแล้ว"],
  "label 1 on the kiosk header; label 2 on the two unverified cards area; label 3 next to the blue check badge")
t("chart-vs-image-registry", S13,
  "คนละคนดึง: helm บนเครื่องเราดึง chart (registry login) / kubelet บน Node ดึง image (imagePullSecrets บท 011)",
  """Left: the contractor robot on the dock picks a kit crate from the kit warehouse using a gate pass. Right: on a
  ship, the deckhand robot picks a shipping container from a container warehouse showing a different gate pass
  card. Nong Som points at both.""",
  ["helm ดึง chart: registry login", "kubelet ดึง image: imagePullSecrets", "คนละผู้ดึง คนละบัตร"],
  "label 1 on the left panel; label 2 on the right panel; label 3 as a title banner")

S14 = "14. ความปลอดภัยและแหล่งที่มา"
t("security-checklist", S14,
  "ก่อนติดตั้ง chart: อ่าน values และ image ที่จะดึง, pin เวอร์ชัน (และ digest), ไม่ใส่รหัสจริงใน values ที่ commit, เลือกแหล่งของเจ้าของโปรเจกต์",
  """A checklist board on the dock with four ticked rows and small icons; Nong Som ticks the last row while the
  contractor robot waits with an unopened kit.""",
  ["อ่าน values ก่อนติดตั้ง", "pin version + digest", "ไม่ใส่รหัสจริงใน values", "เลือกแหล่งทางการ", "ตรวจก่อนเปิดกล่อง"],
  "label 1 to label 4 as the four rows; label 5 as the board header")
t("catalog-can-vanish", S14,
  "บทเรียนปี 2568: แคตตาล็อกดังเปลี่ยนเงื่อนไข image รุ่นเก่าถูกย้าย/หยุดอัปเดต → pin เวอร์ชัน และเก็บสำเนาในโกดังของเราเอง",
  """A once-busy catalog shelf now half empty with dust outlines and a 'moved' arrow pointing to an old storage
  room; Nong Som carries a copy of her kit into her own small warehouse with a fingerprint sticker.""",
  ["แคตตาล็อกเปลี่ยนเงื่อนไขได้", "เก็บสำเนาในโกดังของเรา", "pin เวอร์ชันเสมอ"],
  "label 1 on the half-empty shelf; label 2 on Nong Som's warehouse; label 3 as a caption banner; no real company names or logos")

S15 = "15. Helm vs Kustomize vs static manifest"
t("helm-kustomize-static", S15,
  "เทียบ 3 แบบ: static manifest (แผ่นเดียวตายตัว), Kustomize (แผ่นใสซ้อนบนพิมพ์เขียว), Helm (ชุดแฟรนไชส์ + รุ่น + rollback)",
  f"""Three columns on a table: a single plain blueprint; a plain blueprint with transparent overlay sheets on top;
  {KIT} with an order form and a logbook. Nong Som stands behind with a thinking pose.""",
  ["static manifest", "Kustomize: แผ่นใสซ้อน", "Helm: ชุด + รุ่น + rollback", "เลือกให้เหมาะกับงาน"],
  "label 1 to label 3 under the three columns in order; label 4 as a title banner",
  allow=True)

S16 = "16. ปูทาง GitOps และ operator"
t("gitops-preview", S16,
  "GitOps (ตัวอย่าง Argo CD/Flux): เก็บ chart + ใบสั่งไว้ใน Git แล้วหุ่นยนต์เฝ้าแฟ้มทำให้สาขาตรงกับแผนเสมอ ไม่ต้องสั่ง helm upgrade เอง",
  """A watchful robot sits by a binder of shop plans on a lectern, holding a remote that keeps a branch shop identical
  to the binder; when a page in the binder changes the branch updates. Nong Som closes her laptop and relaxes.""",
  ["Git = แฟ้มแผนร้าน", "Argo CD / Flux", "สาขาตรงกับแผนเสมอ"],
  "label 1 on the binder; label 2 on the robot's badge; label 3 as a caption banner",
  allow=True)
t("operator-preview", S16,
  "Helm ติดตั้งจบแล้วไม่ดูแลต่อ — operator คือหุ่นยนต์ที่ดูแลร้านต่อทุกวัน (สำรองข้อมูล ซ่อม อัปเกรดฐานข้อมูล) บทถัดไป",
  """Left: the contractor robot waves goodbye after building a shop. Right: a caretaker robot with a wrench and a
  backup crate stays next to the kitchen booth. Nong Som points to a signpost to the next chapter.""",
  ["Helm: ติดตั้งจบ", "operator: ดูแลต่อทุกวัน", "บทต่อไป"],
  "label 1 on the left panel; label 2 on the right panel; label 3 on the signpost",
  allow=True)

S17 = "17. ตารางคำสั่งที่ใช้บ่อย"
t("command-cheatsheet", S17,
  "คำสั่งที่ใช้บ่อยของ Helm 4 จัดเป็นกลุ่ม: ติดตั้ง/อัปเกรด, ดูสถานะ, ดูข้อมูลสาขา, ย้อนรุ่น, render/ตรวจ",
  f"""A cheat-sheet board held by {ROBOT}, five rows each with a small icon; Nong Som copies it into her notebook.""",
  ["upgrade --install --wait", "list / status / history", "get values / manifest", "rollback <revision>",
   "template / lint", "คำสั่งที่ใช้บ่อย"],
  "label 1 to label 5 as the five rows in order; label 6 as the board header")

S18 = "18. สรุปบท"
t("chapter-summary", S18,
  "สรุปบท: ชุดแฟรนไชส์ (chart) + ใบสั่ง (values) → ร้านสาขา (release) ที่มีสมุดบันทึก (revision) ติดตั้ง/อัปเกรด/ย้อน/ถอนได้ทั้งร้าน",
  f"""Sunset over the harbor; two branch shops (orange zone and navy zone) open from the same {KIT}; {ROBOT} and the
  inspector robot stand together; Nong Som holds the logbook and waves.""",
  ["chart + values → release", "revision = สมุดบันทึกการปรับปรุงร้าน", "ทั้งร้านในคำสั่งเดียว", "สรุปบทที่ 14"],
  "label 1 on the crate; label 2 on the logbook; label 3 as a ribbon between the two shops; label 4 as a title banner")

# ================================================================ LAB
def opening(slug, sec, cap, scene, labels, extra, nt=False, allow=False):
    l(slug, sec, cap, scene, labels, extra, nt=nt, allow=allow)

K0 = "LAB 0: เตรียมท่าเรือ + แอป 1.8"
opening("lab00-open", K0,
  "LAB 0: ตรวจ helm v4.3.0 และร้านจากบท 013 แล้ว build som-shop-web:1.8 (โค้ดเดิม เปลี่ยนแค่ APP_VERSION)",
  """Nong Som at a harbor workbench with a laptop showing a terminal; the existing shop booths in the background and a
  fresh shipping container being stamped with a new version sticker by a small press.""",
  ["LAB 0", "เตรียมท่าเรือ", "helm v4.3.0", "som-shop-web:1.8"],
  "label 1 as a title banner; label 2 as a subtitle; label 3 on the laptop screen; label 4 on the new container sticker",
  nt=True)
l("lab00-build-arg", K0,
  "1.8 = โค้ดเดิม build ใหม่ด้วย --build-arg APP_VERSION=1.8 แล้ว kind load docker-image เข้า Node",
  """A conveyor: the same container shell passes a sticker station that prints a new version sticker, then a crane
  lifts it onto the three ships. Nong Som presses the button.""",
  ["--build-arg APP_VERSION=1.8", "โค้ดเดิม ป้ายเวอร์ชันใหม่", "kind load docker-image"],
  "label 1 on the sticker station; label 2 as a caption banner; label 3 on the crane")

K1 = "LAB 1: แคตตาล็อกแฟรนไชส์"
opening("lab01-open", K1,
  "LAB 1: helm repo add / update / search repo --versions / show — เลือก chart และ pin เวอร์ชัน",
  """Nong Som flips through three franchise catalog brochures on a dock table; the contractor robot holds a version
  sticker sheet.""",
  ["LAB 1", "แคตตาล็อกแฟรนไชส์", "helm repo add", "helm search repo --versions"],
  "label 1 as a title banner; label 2 as a subtitle; label 3 on the first brochure; label 4 on the robot's sticker sheet")
l("lab01-hub-names", K1,
  "helm search hub traefik เจอหลายผู้เผยแพร่ชื่อเดียวกัน เลือกของทางการ (traefik/traefik)",
  """The catalog kiosk shows four kit cards with the same name; one card has a blue check badge; Nong Som circles it.""",
  ["helm search hub traefik", "ชื่อเดียวกัน หลายผู้เผยแพร่", "traefik/traefik ของทางการ"],
  "label 1 on the kiosk header; label 2 above the cards; label 3 on the circled card")

K2 = "LAB 2: เปิดสาขาแรก (podinfo)"
opening("lab02-open", K2,
  "LAB 2: helm install hello podinfo/podinfo ด้วย --set ข้อความภาษาไทย แล้วดู list/status/get",
  """The contractor robot opens a small sample kit in a fresh light-blue zone and a tiny sample booth appears with a
  welcome message screen; Nong Som cuts a ribbon.""",
  ["LAB 2", "เปิดสาขาแรก: podinfo", "helm install hello", "สวัสดีจากร้านน้องส้ม"],
  "label 1 as a title banner; label 2 as a subtitle; label 3 on the robot's tablet; label 4 on the booth's message screen")
l("lab02-get", K2,
  "helm get values/manifest/metadata ดูใบสั่ง พิมพ์เขียว และวิธี apply (server-side apply) ส่วนสมุดถูกเก็บเป็น Secret sh.helm.release.v1.hello.v1",
  """Three windows of an information desk beside the sample booth: an order form window, a blueprint window, an owner
  tag window; a cabinet drawer below. Nong Som reads them.""",
  ["helm get values", "helm get manifest", "APPLY_METHOD: server-side apply", "sh.helm.release.v1.hello.v1", "ข้อมูลสาขา"],
  "label 1 to label 3 on the three windows in order; label 4 on the drawer; label 5 as a title banner")

K3 = "LAB 3: ใบสั่งปรับแต่งร้าน (values)"
opening("lab03-open", K3,
  "LAB 3: ไฟล์ -f + --set (--set ชนะ) + Ingress podinfo.localhost ผ่าน Traefik",
  """Nong Som stacks a values file and a sticky note on the sample booth's order form; the booth turns orange and
  the receptionist robot at the front gate points customers to it.""",
  ["LAB 3", "ใบสั่งปรับแต่งร้าน", "-f podinfo-values.yaml", "--set ชนะ", "podinfo.localhost"],
  "label 1 as a title banner; label 2 as a subtitle; label 3 on the values sheet; label 4 on the sticky note; label 5 on the gate signboard row")
l("lab03-reset-trap", K3,
  "upgrade โดยไม่ส่ง values = เหลือแค่ค่าที่ส่งครั้งนี้ (replicaCount: 1) ค่าอื่นกลับค่าเริ่มต้น — ใช้ --reuse-values หรือส่ง -f ทุกครั้ง",
  """The orange booth fades back to the default color and extra booths become ghost outlines; Nong Som holds a
  forgotten values sheet and a reuse stamp.""",
  ["upgrade ไม่ส่ง values", "เหลือแค่ replicaCount: 1", "--reuse-values"],
  "label 1 as a title banner; label 2 on a note by the faded booth; label 3 on the stamp")

K4 = "LAB 4: สมุดบันทึกการปรับปรุงร้าน"
opening("lab04-open", K4,
  "LAB 4: upgrade / history / rollback / rollback-on-failure / uninstall --keep-history",
  """Nong Som opens the renovation logbook on a desk next to the sample booth; the contractor robot holds a back-arrow
  sign.""",
  ["LAB 4", "สมุดบันทึกการปรับปรุงร้าน", "upgrade / history / rollback"],
  "label 1 as a title banner; label 2 on the logbook cover; label 3 on the robot's sign")
l("lab04-rollback-on-failure", K4,
  "image ผิด + --rollback-on-failure --timeout 40s: รอ ~40 วินาที ล้ม แล้วถอยกลับเอง สมุดมีหน้า failed ตามด้วย Rollback",
  """A booth with a container whose sticker is wrong shows a red lamp; a timer rings; the contractor robot restores the
  previous booth; the logbook shows a red failed page followed by a new page. Nong Som watches the timer.""",
  ["image: 9.9.9-nope", "--rollback-on-failure", "หน้าที่ล้ม: failed", "Rollback to 5"],
  "label 1 on the wrong container sticker; label 2 on the robot's tablet; label 3 on the red page tab; label 4 on the new page tab",
  nt=True)
l("lab04-keep-history", K4,
  "uninstall --keep-history: ร้านถูกรื้อแต่สมุดยังอยู่ (uninstalled) → helm rollback เปิดร้านกลับมาได้",
  """The sample booth area is empty with a closed shutter, but the logbook remains in the cabinet; the contractor robot
  reads it and rebuilds the booth. Nong Som smiles with relief.""",
  ["helm uninstall --keep-history", "STATUS: uninstalled", "rollback → ร้านกลับมา"],
  "label 1 on the shutter; label 2 on the logbook; label 3 as a caption banner")

K5 = "LAB 5: ชุดแฟรนไชส์ชุดแรก (helm create)"
opening("lab05-open", K5,
  "LAB 5: helm create mychart → lint → template → install → helm test --logs",
  """Nong Som assembles her own first franchise kit from a blank crate, molds and an order form; the inspector robot
  waits with a stamp.""",
  ["LAB 5", "ชุดแฟรนไชส์ชุดแรก", "helm create mychart", "helm test: Succeeded"],
  "label 1 as a title banner; label 2 as a subtitle; label 3 on the crate; label 4 on the inspector's stamp")

K6 = "LAB 6: แม่พิมพ์พัง (render & debug)"
opening("lab06-open", K6,
  "LAB 6: ทำแม่พิมพ์พัง 4 แบบ แล้วหาจุดผิดด้วย helm lint / helm template --debug",
  """Nong Som with a flashlight examines a cracked stencil mold on the printing table; a crooked blueprint comes out.""",
  ["LAB 6", "แม่พิมพ์พัง: หาจุดผิด", "helm lint", "--debug"],
  "label 1 as a title banner; label 2 as a subtitle; label 3 on the lint inspector card; label 4 on the flashlight")
l("lab06-dryrun-gap", K6,
  "helm install --dry-run=server ผ่าน (Dry run complete) แต่ kubectl apply --dry-run=server จับ spec.type ผิดได้ — ตรวจสองชั้น",
  """Two inspection gates in a row: the first gate waves a wrong blueprint through with a green light, the second gate
  stops it with a red light. Nong Som notes the difference.""",
  ["helm --dry-run=server: Dry run complete", "kubectl apply --dry-run=server: Unsupported value", "ตรวจสองชั้น"],
  "label 1 on the first gate; label 2 on the second gate; label 3 as a caption banner",
  nt=True)

K7 = "LAB 7: แม่พิมพ์ร้านน้องส้ม (template functions)"
opening("lab07-open", K7,
  "LAB 7: อ่านแม่พิมพ์ som-shop — range การ์ดกระดาน, if hpa ไม่ใส่ replicas, include ตรายาง, toYaml resources",
  """Nong Som and the contractor robot study the shop's stencil molds laid on the printing table: a notice board mold
  with repeating card slots, a booth mold with a switch, a stamp rack.""",
  ["LAB 7", "แม่พิมพ์ร้านน้องส้ม", "range / if / include / toYaml"],
  "label 1 as a title banner; label 2 as a subtitle; label 3 on a strip above the molds")

K8 = "LAB 8: ใบสั่งต่อสาขา + ด่านตรวจ"
opening("lab08-open", K8,
  "LAB 8: values-dev.yaml / values-prod.yaml + values.schema.json + required/lookup",
  """Two order forms with orange and navy tabs on the inspection desk; the desk checklist glows; Nong Som hands over
  the forms.""",
  ["LAB 8", "ใบสั่งต่อสาขา", "values-dev.yaml", "values-prod.yaml", "values.schema.json"],
  "label 1 as a title banner; label 2 as a subtitle; label 3 on the orange-tab form; label 4 on the navy-tab form; label 5 on the desk sign")
l("lab08-schema-reject", K8,
  "ด่านตรวจปฏิเสธใบสั่ง: --set web.replicas=9 → maximum: got 9, want 6",
  """The inspection desk stamps a red reject on an order form with too many booth checkboxes ticked; Nong Som reads the
  printed reason slip.""",
  ["--set web.replicas=9", "maximum: got 9, want 6", "ด่านตรวจไม่ให้ผ่าน"],
  "label 1 on the form; label 2 on the reason slip; label 3 as a caption banner")

K9 = "LAB 9: เติมสินค้าหลังเปิดร้าน + ผู้ตรวจรับ"
opening("lab09-open", K9,
  "LAB 9: install สาขา dev → hook post-install (seed) เติมสินค้า → helm test --logs → ถอด release Secret",
  """In the orange zone a new booth opens; right after, a shelf-stocking cart fills the kitchen shelves; then the
  inspector robot stamps approval. Nong Som checks her watch.""",
  ["LAB 9", "เติมสินค้า + ตรวจรับร้าน", "post-install", "helm test"],
  "label 1 as a title banner; label 2 as a subtitle; label 3 on the stocking cart; label 4 on the inspector")
l("lab09-release-secret", K9,
  "ถอดสมุดใน Secret ด้วย base64 -d | base64 -d | gzip -d เห็นรหัสฐานข้อมูลในใบสั่ง → ใครอ่าน Secret ได้ = อ่านรหัสได้",
  """Nong Som unwraps a shrink-wrapped logbook page from the zone cabinet; the page shows a copy of the order form with
  a password line; a staff card with a stripe hangs on the cabinet.""",
  ["base64 -d | base64 -d | gzip -d", "\"password\": \"meow1234\"", "อ่าน Secret ได้ = อ่านรหัสได้"],
  "label 1 on the unwrapping tool; label 2 on the page; label 3 as a warning banner")

K10 = "LAB 10: Traefik + metrics-server จากแคตตาล็อก"
opening("lab10-open", K10,
  "LAB 10: แทน static manifest ด้วย chart traefik 41.6.1 (v3.7.13) และ metrics-server 3.14.0 (0.9.0)",
  """At the front gate the receptionist robot and the meter-reader robot each receive a fresh franchise kit from the
  contractor robot; old paper sheets are bundled for removal. Nong Som supervises.""",
  ["LAB 10", "พนักงานต้อนรับ + จดมิเตอร์ จากแคตตาล็อก", "traefik 41.6.1", "metrics-server 3.14.0"],
  "label 1 as a title banner; label 2 as a subtitle; label 3 on the receptionist's kit; label 4 on the meter-reader's kit",
  nt=True)
l("lab10-adopt-fail", K10,
  "ติดตั้งทับของเดิม: invalid ownership metadata → --take-ownership เจอ conflict → --force-conflicts ติด selector field is immutable ⇒ ลบของเดิมก่อน (เก็บ CRD)",
  """A three-step staircase to the old hand-built receptionist post: a closed gate, a red spark between owner tags, a
  padlocked base plate; beside it Nong Som decides to remove the old post while keeping a sealed box of form types.""",
  ["invalid ownership metadata", "conflict: kubectl-client-side-apply", "selector: field is immutable", "ลบของเดิมก่อน (เก็บ CRD)"],
  "label 1 to label 3 on the three steps in order; label 4 on Nong Som's decision card")
l("lab10-migrate-downtime", K10,
  "ย้ายจริง: ระหว่างลบของเดิมและติดตั้ง chart ประตูปิดชั่วคราว (~17 วินาที) แล้วกลับมาเป็น 404 page not found ตามเดิม",
  """The front gate briefly closed with a small 'please wait' hourglass while the contractor robot installs a new
  receptionist post; then the gate reopens. Nong Som holds a stopwatch.""",
  ["ประตูปิดชั่วคราว ~17 วินาที", "helm install traefik --wait", "404 page not found"],
  "label 1 on the hourglass; label 2 on the robot's tablet; label 3 on a small card at the reopened gate",
  nt=True)

K11 = "LAB 11: โกดังเก็บชุดแฟรนไชส์ (OCI registry)"
opening("lab11-open", K11,
  "LAB 11: registry:2 ใน k8s-lab → helm package → helm push → helm install oci://",
  """Nong Som shrink-wraps her som-shop kit into a sealed crate and carries it to a small kit warehouse with a
  turnstile on the dock.""",
  ["LAB 11", "โกดังเก็บชุดแฟรนไชส์", "registry:2", "oci://localhost:5000/charts/som-shop"],
  "label 1 as a title banner; label 2 as a subtitle; label 3 on the warehouse sign; label 4 on the shelf label")
l("lab11-push-install", K11,
  "ต้อง helm registry login localhost:5000 (ใส่แค่ชื่อโฮสต์) ก่อน push ได้ digest แล้วติดตั้งจาก oci:// เป็นสาขา oci-demo",
  """The turnstile accepts a gate pass; the crate is placed on a shelf and a fingerprint sticker is printed; the
  contractor robot takes a crate back out and opens a new branch in a grey zone.""",
  ["helm registry login localhost:5000", "helm push", "Digest: sha256:…", "helm install oci://", "ล็อกอิน → เก็บ → ติดตั้ง"],
  "label 1 on the gate pass; label 2 on the shelf; label 3 on the fingerprint sticker; label 4 on the robot's tablet; label 5 as a title banner")

K = "LAB 12: ร้านน้องส้มพร้อมส่ง"
opening("lab12-open", K,
  "LAB สุดท้าย: ร้านน้องส้มพร้อมส่ง — ติดตั้งทั้งร้านด้วยคำสั่งเดียว สาขา dev และรับร้านเดิมเป็นสาขา prod",
  f"""Grand opening scene: {KIT} on a podium; two zones, orange dev and navy prod, each with a branch banner; the
  contractor robot, inspector robot, receptionist robot and assistant-manager robot line up. Nong Som cuts a big
  ribbon.""",
  ["LAB 12", "ร้านน้องส้มพร้อมส่ง", "ติดตั้งทั้งร้านด้วยคำสั่งเดียว"],
  "label 1 as a title banner; label 2 on the kit's podium; label 3 as a subtitle ribbon")
l("lab12-chart-tree", K,
  "โครงชุด charts/som-shop: แม่พิมพ์ web, db, config, secret, ingress, hpa, seed hook, test + ใบสั่ง dev/prod",
  f"""{KIT} opened on a table; inside, rows of stencil molds (booth, kitchen booth, notice board, sealed envelope,
  gate signboard, assistant robot badge, stocking cart, inspector badge); two tabbed order forms beside it. Nong Som
  checks items off.""",
  ["charts/som-shop", "แม่พิมพ์ทั้งร้าน", "values-dev.yaml", "values-prod.yaml"],
  "label 1 on the crate lid; label 2 above the molds; label 3 on the orange-tab form; label 4 on the navy-tab form")
l("lab12-dev-branch", K,
  "สาขา dev: helm install ... --wait ครั้งเดียวได้ทั้งร้าน (~17 วินาที) ป้ายร้านมีคำว่า (dev) ธีมส้ม",
  """In the orange zone, one booth with a sunset-orange awning and a kitchen booth with its numbered safe appear
  together; the stocking cart finishes; Nong Som checks a stopwatch.""",
  ["som-dev", "helm install som ... --wait", "~17 วินาที", "ร้านอาหารแมวน้องส้ม (dev)"],
  "label 1 on the zone sign; label 2 on the robot's tablet; label 3 on the stopwatch; label 4 on the booth's shop sign",
  nt=True)
l("lab12-adopt-prod", K,
  "รับร้านเดิมของบท 013 (som-shop) เข้า Helm ด้วย --take-ownership --force-conflicts ออเดอร์เดิมยังอยู่",
  """The navy zone's existing hand-built shop: the contractor robot replaces grey owner tags with orange ones and hangs
  a branch banner over the awning; inside, the kitchen order ledger is untouched. Nong Som hugs the ledger.""",
  ["som-shop (ร้านเดิมบท 13)", "--take-ownership --force-conflicts", "orders=1 ยังอยู่", "รับร้านเดิมเข้าชุดแฟรนไชส์"],
  "label 1 on the zone sign; label 2 on the robot's tablet; label 3 on the ledger; label 4 as a title banner",
  nt=True)
l("lab12-upgrade-err0", K,
  "อัปเกรด prod 1.7 → 1.8 ระหว่างลูกค้าเข้าร้าน (hit.sh) ไม่มีลูกค้าเจอ error แม้ upgrade แรกหลังรับร้านต้อง --force-conflicts อีกครั้ง",
  """Booths in the navy zone are swapped one by one for booths with a new version sticker while a line of customers
  keeps flowing through the glass door; a counter board shows zero errors. Nong Som gives a thumbs up.""",
  ["som-shop-web:1.7 → 1.8", "hit.sh: err=0", "upgrade แรกยังต้อง --force-conflicts"],
  "label 1 on the version sticker; label 2 on the counter board; label 3 as a small caution note",
  nt=True)
l("lab12-rollback", K,
  "helm history แล้ว rollback ไป revision ที่เป็น 1.7 (ระบุเลข) ได้หน้าใหม่ในสมุด ลูกค้าไม่เจอ error",
  """The renovation logbook with several pages, one marked failed in red; Nong Som points to a specific older page
  number; a new page is written with a copy arrow; booths switch back.""",
  ["helm history som", "helm rollback som <revision>", "Rollback to N", "เลข revision ไม่ถอยหลัง"],
  "label 1 on the logbook cover; label 2 on Nong Som's note; label 3 on the new page tab; label 4 as a caption banner",
  nt=True)
l("lab12-uninstall-dev", K,
  "helm uninstall สาขา dev: ร้านถูกรื้อ แต่ตู้เซฟ (PVC data-som-db-0) ยังอยู่ ติดตั้งใหม่รหัสเดิมได้ออเดอร์เดิม",
  """The orange zone after closing: booths removed, but a steel safe locker with number plate remains in the cargo hold
  with a yellow tag; Nong Som pats the safe.""",
  ["helm uninstall som -n som-dev", "data-som-db-0 ยังอยู่", "ตู้เซฟไม่ถูกทิ้ง"],
  "label 1 on the closing shutter; label 2 on the safe's tag; label 3 as a caption banner")
l("lab12-wrong-password", K,
  "กับดัก: ติดตั้ง dev ใหม่ด้วยรหัสใหม่ แต่ตู้เซฟเดิมใช้รหัสเก่า → hook เติมสินค้าล้ม failed post-install",
  """The stocking cart is stuck at the kitchen booth's safe with a red X; the safe's keypad shows a wrong-key light;
  Nong Som holds two different key cards, one crossed out.""",
  ["รหัสใหม่ ≠ รหัสในตู้เซฟ", "failed post-install", "Job Failed"],
  "label 1 as a title banner; label 2 on the stuck cart; label 3 on the cart's red tag",
  nt=True)
l("lab12-checklist", K,
  "ตรวจรับร้าน: dev helm test ผ่าน, prod HTTPS + HPA, upgrade 1.8 err=0, rollback ระบุเลข, เข้าใจ PVC ค้าง",
  """A checklist board at the front gate with five ticked rows; the inspector robot stamps it; Nong Som signs.""",
  ["dev: helm test ผ่าน", "prod: HTTPS + HPA", "1.8 err=0", "rollback ระบุเลข", "PVC ค้าง = ตั้งใจ", "ตรวจรับร้าน"],
  "label 1 to label 5 as the five rows; label 6 as the board header",
  nt=True)
l("lab12-wrap-up", K,
  "ปิดบท: เก็บ chart + ใบสั่งใน Git ให้หุ่นยนต์ GitOps ดูแล (Argo CD/Flux), แผ่นใสซ้อน (Kustomize), หุ่นยนต์ดูแลร้าน (operator)",
  """Nong Som stands at the dock at dusk looking at three signposts on the horizon pointing to the next topics.""",
  ["แฟ้มแผนร้าน → GitOps", "แผ่นใสซ้อน → Kustomize", "หุ่นยนต์ดูแลร้าน → operator"],
  "label 1 to label 3 on the three signposts",
  allow=True)

if __name__ == "__main__":
    main()
