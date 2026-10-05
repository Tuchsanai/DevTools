#!/usr/bin/env python3
"""Storyboard ภาพบท 011 Secret → images.json + imagegen-prompts.md (รัน: python3 build_images.py)"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from imgcommon import configure, t, l, main

configure("011")

# ---------------------------------------------------------------- Theory
S1 = "1. บทนำ: รหัสผ่านติดอยู่บนกระดานประกาศ"
t("opening-sealed-envelope", S1,
  "เปิดบทที่ 11: ต่อจากบท 010 — ป้ายร้านอยู่ใน ConfigMap แล้ว แต่รหัส DB ยังอยู่ใน YAML ที่ใครก็อ่านได้ น้องส้มจึงย้ายรหัสใส่ซองปิดผนึกในกล่องกุญแจ",
  """The harbor zone with the teal notice board; Nong Som takes a dotted password card off the board and slides it into a
  navy envelope with an orange paw wax seal, placing it into a small steel key box on the zone wall.""",
  ["บทที่ 11", "Secret", "ย้ายรหัสออกจากกระดาน"],
  "'บทที่ 11' as a title banner; 'Secret' on the key box; 'ย้ายรหัสออกจากกระดาน' as a subtitle")
t("recap-password-visible", S1,
  "ทวนบท 010: intern ที่อ่านได้แค่ Deployment ก็เห็น postgres://som:meow1234@... และ POSTGRES_PASSWORD ใน StatefulSet",
  """An intern silhouette with a grey ID card reads two blueprint cards (web and db) with a magnifier; on both a row is
  highlighted showing only dots. Nong Som frowns.""",
  ["DATABASE_URL", "POSTGRES_PASSWORD", "som:●●●●@", "ใครอ่าน YAML ก็เห็นรหัส"],
  "'DATABASE_URL' on the web blueprint; 'POSTGRES_PASSWORD' on the db blueprint; 'som:●●●●@' on the magnified row; last label as a title banner")
t("metaphor-legend", S1,
  "อุปมาใหม่: Secret = ซองปิดผนึกในกล่องกุญแจ, base64 = ซองใส (แปลงรูปเฉย ๆ), RBAC = บัตรพนักงานที่เปิดกล่องได้/ไม่ได้, encryption at rest = ตู้นิรภัยในหอบังคับการ",
  """A legend board with four tiles: a navy envelope with a paw wax seal in a key box; a transparent envelope with visible
  letters; two lanyard ID cards (green stripe and grey stripe); a round vault door inside the control tower.""",
  ["Secret = ซองปิดผนึก", "base64 = ซองใส", "RBAC = บัตรพนักงาน", "encryption at rest = ตู้นิรภัย"],
  "each tile carries exactly one of the four labels in the listed order")

S2 = "2. Secret ต่างจาก ConfigMap อย่างไร"
t("secret-vs-configmap", S2,
  "Secret ใช้คล้าย ConfigMap (key-value, ≤ 1 MiB, namespaced, env/volume) แต่ data เก็บเป็น base64, describe ไม่แสดงค่า, volume เป็น tmpfs และแยกสิทธิ์ RBAC ได้",
  """Side by side: the open teal notice board and the steel key box with sealed envelopes; a comparison strip under them with
  exactly two rows. Nong Som stands between.""",
  ["ConfigMap", "Secret", "≤ 1 MiB ทั้งคู่", "แยกสิทธิ์อ่านได้", "หน้าตาคล้าย แต่ระวังกว่า"],
  "'ConfigMap' over the board; 'Secret' over the key box; '≤ 1 MiB ทั้งคู่' and 'แยกสิทธิ์อ่านได้' on the two strip rows; last label as a title banner")
t("base64-not-encryption", S2,
  "base64 ไม่ใช่การเข้ารหัส: bWVvdzEyMzQ= | base64 -d → meow1234 ใครมีข้อความก็แปลงกลับได้ทันที ไม่ต้องมีกุญแจ",
  """A transparent envelope on a table; inside letters are visible; Nong Som slides it through a small converting roller and
  plain letters come out the other side; no key anywhere.""",
  ["bWVvdzEyMzQ=", "base64 -d", "meow1234", "ซองใส ไม่ใช่กุญแจ"],
  "'bWVvdzEyMzQ=' on the transparent envelope; 'base64 -d' on the roller; 'meow1234' on the output card; 'ซองใส ไม่ใช่กุญแจ' as a title banner",
  nt=True)
t("echo-newline-trap", S2,
  "ระวัง newline: echo meow1234 | base64 → bWVvdzEyMzQK (มี \\n ติดไปด้วย รหัสจะผิด) ต้องใช้ echo -n → bWVvdzEyMzQ=",
  """Two conveyor lanes: in the top lane a card has an extra small curly tail at the end and becomes a slightly different
  code; in the bottom lane a clean card becomes the right code with a green tick. Nong Som points at the tail.""",
  ["echo", "bWVvdzEyMzQK", "echo -n", "bWVvdzEyMzQ=", "อย่าให้มีขึ้นบรรทัดใหม่"],
  "'echo' and 'bWVvdzEyMzQK' on the top lane; 'echo -n' and 'bWVvdzEyMzQ=' on the bottom lane; last label as a title banner",
  nt=True)
t("real-protection-layers", S2,
  "ความปลอดภัยของ Secret ไม่ได้มาจาก base64 แต่มาจากหลายชั้น: RBAC ใครอ่านได้, encryption at rest ใน etcd, tmpfs บน Node, ไม่พิมพ์ค่าใน describe และการไม่ commit ลง git",
  """A layered shield made of exactly four stacked rings around a sealed envelope, each ring with a small icon (ID card,
  vault door, memory-foam tray, crossed-out code book). Nong Som assembles the rings.""",
  ["RBAC", "encryption at rest", "tmpfs", "ไม่ commit ลง git", "ป้องกันหลายชั้น"],
  "the first four labels on the four rings; 'ป้องกันหลายชั้น' as a title banner")

S3 = "3. ประเภท (type) ของ Secret"
t("secret-types", S3,
  "type บอกรูปแบบ key: Opaque (อิสระ), kubernetes.io/basic-auth (username/password), kubernetes.io/dockerconfigjson (.dockerconfigjson), kubernetes.io/tls (tls.crt/tls.key), kubernetes.io/service-account-token",
  """A shelf of five envelope styles in the key box, each with a different shape icon (plain, person, crane, padlock tube,
  robot ID card). Nong Som catalogs them.""",
  ["Opaque", "kubernetes.io/basic-auth", "kubernetes.io/dockerconfigjson", "kubernetes.io/tls", "kubernetes.io/service-account-token", "ชนิดของซอง"],
  "the five type names on the five envelopes; 'ชนิดของซอง' as a title banner")
t("type-validation", S3,
  "type ตรวจ key ให้: basic-auth ว่างเปล่า → data[username]: Required value, data[password]: Required value; tls ไม่มี key → data[tls.key]: Required value; key ไม่ใช่ PEM → failed to find any PEM data in key input",
  """A gate inspector robot checks envelopes; two envelopes are stopped with red cards; one passes with a green tick. Nong
  Som reads the red cards.""",
  ["data[username]: Required value", "data[tls.key]: Required value", "failed to find any PEM data", "type ช่วยตรวจรูปแบบ"],
  "the three English errors on three red cards; 'type ช่วยตรวจรูปแบบ' as a title banner",
  nt=True)
t("dockerconfigjson", S3,
  "kubectl create secret docker-registry regcred → type dockerconfigjson เก็บ {\"auths\":{server:{username,password,auth}}} — decode ได้รหัสเต็ม ๆ เช่นกัน",
  """A gate pass card for a private container warehouse; held up to the light it is transparent and shows a server row, a
  username row and a password row as dots. Nong Som holds the card.""",
  ["docker-registry", ".dockerconfigjson", "registry.example.com", "password: ●●●●", "บัตรผ่านคลังสินค้า"],
  "'docker-registry' on the card header; '.dockerconfigjson' on the card's key tag; 'registry.example.com' and 'password: ●●●●' as rows; last label as a title banner",
  nt=True)
t("service-account-token", S3,
  "Secret ชนิด service-account-token (ใส่ annotation kubernetes.io/service-account.name) → ระบบเติม token, ca.crt, namespace ให้; ระวัง kubectl describe แสดง token เต็ม ๆ — ปัจจุบันใช้ kubectl create token (มีอายุ) แทน",
  """A robot staff ID card with a long barcode strip being stamped by a machine in the control tower; a describe magnifier
  shows the full barcode; next to it a short-lived paper ticket with a clock icon. Nong Som prefers the ticket.""",
  ["service-account-token", "describe เห็น token", "kubectl create token", "ใช้แบบมีอายุดีกว่า"],
  "'service-account-token' on the ID card; 'describe เห็น token' on the magnifier; 'kubectl create token' on the ticket; last label as a title banner",
  nt=True)
t("opaque-default", S3,
  "kubectl create secret generic = type Opaque (ค่าปกติ) ใส่ key อะไรก็ได้ เหมาะกับรหัส DB และ DATABASE_URL ของร้าน",
  """A plain navy envelope with two cards inside visible as dot rows; the type tag says plain. Nong Som seals it.""",
  ["generic", "Opaque", "POSTGRES_PASSWORD", "DATABASE_URL", "ซองแบบทั่วไป"],
  "'generic' on the command card; 'Opaque' on the type tag; the two key names on the two cards; last label as a title banner")

S4 = "4. วิธีสร้าง Secret"
t("create-literal-file", S4,
  "--from-literal=password=meow1234 หรือ --from-file=db-password=pw.txt (ไฟล์ไม่มี newline) — kubectl เข้ารหัส base64 ให้เอง",
  """Nong Som at a desk drops a typed card and a small text file into an envelope-making machine that outputs sealed envelopes;
  a terminal card shows the command.""",
  ["--from-literal", "--from-file", "kubectl แปลง base64 ให้"],
  "'--from-literal' and '--from-file' on the two input slots; 'kubectl แปลง base64 ให้' as a title banner")
t("data-vs-stringdata", S4,
  "YAML: data ต้องใส่ base64 เอง; stringData ใส่ข้อความตรง ๆ แล้วระบบแปลงให้ — ถ้า key ซ้ำ stringData ชนะ (ทดสอบแล้ว) และ get -o yaml จะเห็นแค่ data",
  """Two input trays: one tray of transparent-coded cards, one tray of plain cards; both merge into one envelope where the
  plain card replaces the coded card with the same key. Nong Som watches the merge.""",
  ["data: (base64)", "stringData: (ข้อความ)", "key ซ้ำ stringData ชนะ", "เก็บจริงเป็น data"],
  "'data: (base64)' and 'stringData: (ข้อความ)' on the two trays; 'key ซ้ำ stringData ชนะ' on the merge point; 'เก็บจริงเป็น data' on the envelope",
  nt=True)
t("last-applied-leak", S4,
  "กับดัก: kubectl apply ไฟล์ที่มี stringData → annotation kubectl.kubernetes.io/last-applied-configuration เก็บข้อความรหัสแบบไม่ base64 ไว้ด้วย; ใช้ kubectl create secret หรือ apply --server-side",
  """A sealed envelope with a sticky note stuck on its outside that shows the plain password as dots; a magnifier reveals
  the note. Nong Som peels the note off with tweezers.""",
  ["stringData", "last-applied-configuration", "รหัสติดอยู่นอกซอง"],
  "'stringData' on the envelope tag; 'last-applied-configuration' on the sticky note; 'รหัสติดอยู่นอกซอง' as a title banner",
  nt=True)

S5 = "5. ใช้ Secret ใน Pod"
t("env-secret-key-ref", S5,
  "env.valueFrom.secretKeyRef (name + key) หรือ envFrom.secretRef — เหมือน ConfigMap: ค่าถูกคัดลอกตอนเริ่ม ไม่เปลี่ยนจนกว่าจะได้ Pod ใหม่",
  """A staff member at the booth door receives a sealed chest card copied from an envelope; the envelope goes back into the
  key box. Nong Som checks the staff member's card.""",
  ["secretKeyRef", "envFrom: secretRef", "คัดลอกตอนเข้ากะ"],
  "'secretKeyRef' and 'envFrom: secretRef' on two arrows from the key box; 'คัดลอกตอนเข้ากะ' as a title banner")
t("volume-tmpfs", S5,
  "volume ของ Secret เป็น tmpfs (อยู่ในหน่วยความจำ ไม่เขียนลงดิสก์ Node) ไฟล์ละ key ผ่าน ..data และตั้ง defaultMode: 0400 ได้ (ทดสอบ: mount = tmpfs ro)",
  """Inside a booth: a soft memory-foam tray holds sealed envelope files, each envelope tagged with one key name; the ship
  deck below shows nothing written. Nong Som points at the tray.""",
  ["tmpfs", "/etc/secret/password", "defaultMode: 0400", "อยู่ในหน่วยความจำ"],
  "'tmpfs' on the tray; '/etc/secret/password' on one envelope; 'defaultMode: 0400' on a permission tag; 'อยู่ในหน่วยความจำ' as a title banner",
  nt=True)
t("env-leak", S5,
  "env รั่วง่าย: kubectl exec ... env, /proc/1/environ, log ที่พิมพ์ตัวแปร, crash dump — ไฟล์ใน volume ปลอดภัยกว่าและอัปเดตได้",
  """A staff chest card is photocopied by passing gadgets: a shell terminal, a process window and a log scroll, each showing
  dots; in contrast a booth envelope tray stays closed. Nong Som covers a chest card with her paw.""",
  ["kubectl exec env", "/proc/1/environ", "log", "env รั่วง่ายกว่าไฟล์"],
  "the three English labels on the three gadgets; 'env รั่วง่ายกว่าไฟล์' as a title banner",
  nt=True)
t("update-and-immutable", S5,
  "แก้ Secret → ไฟล์ใน volume เปลี่ยนเอง (วัดได้ ~47 วินาที) แต่ env ไม่เปลี่ยน; immutable: true ใช้ได้เหมือน ConfigMap (data: Forbidden: field is immutable when `immutable` is set)",
  """Left: the deckhand robot replaces an envelope in the booth tray with a stopwatch showing under a minute while a staff
  chest card stays old. Right: an envelope sealed under a laminated sheet.""",
  ["~47 วินาที", "env ยังค่าเดิม", "immutable: true", "อัปเดตเหมือน ConfigMap"],
  "'~47 วินาที' on the stopwatch; 'env ยังค่าเดิม' on the chest card; 'immutable: true' on the laminated envelope; last label as a title banner",
  nt=True)

S6 = "6. imagePullSecrets: ดึง image จาก registry ส่วนตัว"
t("image-pull-secrets", S6,
  "registry ที่ต้อง login → Pod ใส่ imagePullSecrets: [{name: regcred}] หรือผูกไว้กับ ServiceAccount; ไม่มีบัตร → ErrImagePull no basic auth credentials, บัตรผิด → 401 Unauthorized",
  """A private container warehouse gate on the dock with a guard robot; a crane with a gate pass card is let through and
  lifts a container; another crane without a card is stopped with a red card; a third with a wrong card gets another
  red card. Nong Som holds a valid pass.""",
  ["imagePullSecrets", "no basic auth credentials", "401 Unauthorized", "บัตรผ่านคลัง image"],
  "'imagePullSecrets' on the valid pass; the two English errors on two red cards; 'บัตรผ่านคลัง image' as a title banner",
  nt=True)
t("pull-recheck-cached", S6,
  "Kubernetes v1.37 (ทดสอบแล้ว): image ที่เคยดึงด้วย imagePullSecrets มาอยู่บน Node แล้ว Pod อื่นที่ไม่มีบัตรก็ยังใช้ไม่ได้ (kubelet ตรวจสิทธิ์ซ้ำ) แม้ imagePullPolicy: IfNotPresent",
  """A container already sits in a ship's cargo hold; a booth without a gate pass asks to use it, and the deckhand robot
  checks for a pass and refuses with a red card. Nong Som nods approvingly.""",
  ["IfNotPresent", "ไม่มีบัตร = ใช้ไม่ได้", "kubelet ตรวจสิทธิ์ซ้ำ"],
  "'IfNotPresent' on the booth's request card; 'ไม่มีบัตร = ใช้ไม่ได้' on the red card; 'kubelet ตรวจสิทธิ์ซ้ำ' as a title banner",
  nt=True)

S7 = "7. TLS Secret: HTTPS ให้ร้าน"
t("tls-cert-key", S7,
  "kubernetes.io/tls เก็บ tls.crt (ใบรับรอง แจกได้) + tls.key (กุญแจส่วนตัว ห้ามรั่ว) สร้าง self-signed ด้วย openssl req -x509 แล้ว kubectl create secret tls",
  """A certificate badge on a ribbon and a small private key on a hook inside the counter; an openssl stamping press makes
  the pair; both go into one envelope. Nong Som holds the badge up.""",
  ["openssl req -x509", "tls.crt", "tls.key", "kubectl create secret tls", "ใบรับรอง + กุญแจ"],
  "'openssl req -x509' on the press; 'tls.crt' on the badge; 'tls.key' on the key tag; 'kubectl create secret tls' on the envelope; last label as a title banner")
t("https-nginx-curl", S7,
  "nginx mount Secret TLS แล้วฟัง 443 ssl: curl https://... → (60) SSL certificate problem: self-signed certificate; curl -k ข้ามการตรวจ; curl --cacert tls.crt ตรวจผ่านอย่างถูกต้อง",
  """A sealed glass delivery tube from a customer silhouette to the counter; three customers try: one is stopped by a red card,
  one jumps over a check gate, one shows the badge copy and walks through a green gate. Nong Som guards the gate.""",
  ["(60) self-signed certificate", "curl -k", "curl --cacert tls.crt", "HTTPS ร้านน้องส้ม"],
  "the English error on the red card; 'curl -k' on the jumper; 'curl --cacert tls.crt' on the green gate; 'HTTPS ร้านน้องส้ม' as a title banner",
  nt=True)

S8 = "8. RBAC: ใครเปิดซองได้"
t("rbac-intern-forbidden", S8,
  "ต่อบท 004: Role ของ intern ให้ get/list pods, configmaps → kubectl auth can-i get secrets = no และ get secret ได้ Error from server (Forbidden)",
  """An intern with a grey-stripe ID card reads the notice board and looks at booths happily, but at the key box a red X
  light blinks. Nong Som with a green-stripe card watches.""",
  ["intern", "get pods = yes", "get secrets = no", "Forbidden", "บัตรนี้เปิดกล่องไม่ได้"],
  "'intern' on the grey card; 'get pods = yes' near the booths; 'get secrets = no' near the key box; 'Forbidden' on the red X light; last label as a title banner",
  nt=True)
t("rbac-indirect-read", S8,
  "สิทธิ์สร้าง Pod = อ่าน Secret ทางอ้อมได้: ServiceAccount maker (get secrets = no) สร้าง Pod ที่ใส่ secretKeyRef แล้ว kubectl logs เห็นค่า — จำกัดสิทธิ์ create pods ใน namespace ที่มีความลับ",
  """A staff member with a card that cannot open the key box builds a tiny booth whose staff automatically receives a chest
  card from the envelope, then reads it from the booth's log scroll. Nong Som raises an alarm flag.""",
  ["get secrets = no", "create pods = yes", "stolen=●●●●", "สร้าง Pod ได้ = อ่านซองได้"],
  "'get secrets = no' and 'create pods = yes' on two lines of the staff card; 'stolen=●●●●' on the log scroll; last label as a title banner",
  nt=True)
t("describe-vs-get", S8,
  "kubectl describe secret แสดงแค่ขนาด (password: 8 bytes) แต่ get secret -o yaml / jsonpath แสดง base64 เต็ม = อ่านได้ — สิทธิ์ get secrets จึงเท่ากับอ่านรหัส",
  """Two windows of the key box: a frosted window showing only a byte count, and a clear window showing the transparent
  envelope letters. Nong Som points at the clear window.""",
  ["describe: 8 bytes", "get -o yaml: bWVvdzEyMzQ=", "get ได้ = อ่านได้"],
  "'describe: 8 bytes' on the frosted window; 'get -o yaml: bWVvdzEyMzQ=' on the clear window; 'get ได้ = อ่านได้' as a title banner",
  nt=True)

S9 = "9. etcd และ encryption at rest"
t("etcd-plaintext", S9,
  "Secret ทุกตัวถูกเก็บใน etcd ของ control plane — kind ค่าปกติไม่เปิด encryption at rest: etcdctl get /registry/secrets/default/demo เห็นค่ารหัสเป็นข้อความตรง ๆ (ทดสอบแล้ว)",
  """Inside the control tower: a tall archive cabinet of drawers; one drawer pulled open shows an envelope that is not sealed
  at all, letters visible as dots. Nong Som shines a flashlight into the drawer.""",
  ["etcd", "/registry/secrets/default/demo", "ไม่ได้เข้ารหัส", "เปิดลิ้นชักก็เห็น"],
  "'etcd' on the cabinet; '/registry/secrets/default/demo' on the drawer label; 'ไม่ได้เข้ารหัส' on the open envelope; last label as a title banner",
  nt=True)
t("encryption-configuration", S9,
  "เปิด encryption at rest: EncryptionConfiguration (resources: secrets, providers: aescbc/secretbox/kms v2 แล้วตามด้วย identity) + kube-apiserver --encryption-provider-config แล้วเขียน Secret ใหม่ทั้งหมดซ้ำ (แนวคิด ไม่ทำใน LAB)",
  """A round vault door installed in front of the archive cabinet; a config card on the wall lists provider rows; a robot arm
  rewrites old envelopes into sealed ones. Nong Som reads the config card.""",
  ["EncryptionConfiguration", "aescbc / kms v2", "identity", "--encryption-provider-config", "ล็อกตู้เอกสารในหอ"],
  "'EncryptionConfiguration' on the config card title; 'aescbc / kms v2' and 'identity' as two rows; '--encryption-provider-config' on the vault door; last label as a title banner")
t("who-can-read-etcd", S9,
  "แม้เข้ารหัสแล้ว ผู้ดูแลที่มีสิทธิ์ API/etcd/backup หรือ root บน Node ยังเข้าถึงได้ — ปกป้องไฟล์ backup ของ etcd และจำกัดสิทธิ์ cluster-admin",
  """A backup crate of archive drawers being carried off the tower by a crane; a guard robot checks staff cards at the tower
  door; a gold master key on a hook. Nong Som points at the backup crate.""",
  ["backup etcd", "cluster-admin", "ใครถือกุญแจหลักก็อ่านได้"],
  "'backup etcd' on the crate; 'cluster-admin' on the gold key tag; last label as a title banner")

S10 = "10. ข้อควรระวัง"
t("never-commit-git", S10,
  "อย่า commit Secret YAML/ไฟล์ .env ลง git (base64 อ่านกลับได้): ใส่ใน .gitignore, เก็บแค่ไฟล์ตัวอย่าง *.example.yaml ที่ใช้ค่าปลอม, ถ้าหลุดต้องเปลี่ยนรหัสทันที",
  """A code-repository bookshelf; Nong Som stops a staff silhouette from shelving a sealed envelope and instead shelves a
  sample card stamped 'example'; a gitignore sign lists blocked files.""",
  [".gitignore", "secret.example.yaml", "หลุดแล้วต้องเปลี่ยนรหัส", "อย่า commit รหัสจริง"],
  "'.gitignore' on the sign; 'secret.example.yaml' on the sample card; 'หลุดแล้วต้องเปลี่ยนรหัส' on a small warning card; last label as a title banner")
t("leak-checklist", S10,
  "ทางรั่วที่พบบ่อย: get secret -o yaml บนจอที่แชร์, แอปพิมพ์ env/DATABASE_URL ลง log, ใส่รหัสใน ConfigMap/annotation/args, คำสั่งที่พิมพ์รหัสค้างใน shell history",
  """A checklist board with four leak icons (a shared screen, a log scroll, a notice board card, a shell history scroll), each
  with a red drip; Nong Som plugs leaks with a cork.""",
  ["จอที่แชร์", "log", "ConfigMap / args", "shell history", "จุดที่รหัสรั่วบ่อย"],
  "the first four labels on the four leak icons; 'จุดที่รหัสรั่วบ่อย' as a title banner")
t("rotate-password", S10,
  "เปลี่ยนรหัสต้องทำ 2 ฝั่ง: ฐานข้อมูล (ALTER USER) และ Secret แล้ว rollout restart — POSTGRES_PASSWORD ใช้แค่ตอน initdb ครั้งแรก การแก้ Secret อย่างเดียวไม่เปลี่ยนรหัสใน DB",
  """Two synchronized dials: one on the kitchen booth -0 (database) and one on the key box (Secret); a link rod joins them;
  a booth swap happens after both dials turn. Nong Som turns both dials.""",
  ["ALTER USER", "Secret", "rollout restart", "เปลี่ยนรหัสต้องเปลี่ยนสองฝั่ง"],
  "'ALTER USER' on the db dial; 'Secret' on the key box dial; 'rollout restart' on the swap arrow; last label as a title banner",
  nt=True)

S11 = "11. แนวทางเก็บความลับนอกคลัสเตอร์ (ปูทาง)"
t("sealed-secrets", S11,
  "Sealed Secrets: เข้ารหัส Secret ด้วย public key ของ controller ในคลัสเตอร์ → ได้ SealedSecret ที่ commit ลง git ได้ เฉพาะคลัสเตอร์ถอดได้",
  """A locked metal canister (sealed with a padlock) placed on the git bookshelf; a controller robot in the harbor opens it
  with its private key and produces a normal envelope for the key box. Nong Som shelves the canister.""",
  ["SealedSecret", "commit ได้", "ถอดรหัสได้ในคลัสเตอร์เท่านั้น"],
  "'SealedSecret' on the canister; 'commit ได้' on the bookshelf; 'ถอดรหัสได้ในคลัสเตอร์เท่านั้น' as a title banner")
t("external-secrets-vault", S11,
  "External Secrets Operator / Vault / Secrets Store CSI: เก็บความลับในตู้นิรภัยภายนอก แล้วซิงก์หรือ mount เข้า Pod ตามสิทธิ์ — เปลี่ยนรหัสและตรวจ log การเข้าถึงได้ที่เดียว",
  """A big external vault building off the harbor; a courier conveyor brings envelopes into the zone key box on demand; an
  audit log book sits on the vault counter. Nong Som visits the vault.""",
  ["External Secrets", "Vault", "Secrets Store CSI", "ตู้นิรภัยนอกท่าเรือ"],
  "'External Secrets' on the conveyor; 'Vault' on the building; 'Secrets Store CSI' on a plug adapter at the booth; last label as a title banner")

S12 = "12. projected volume"
t("projected-volume", S12,
  "projected รวม configMap + secret + downwardAPI ไว้ในโฟลเดอร์เดียว เช่น /etc/som/announcement.txt, /etc/som/db/password, /etc/som/pod-name (ทดสอบแล้ว)",
  """One ring binder inside the booth combines a notice card, a sealed envelope and the booth's own name tag; three arrows
  come in from the notice board, the key box and the booth plate. Nong Som closes the binder.""",
  ["projected", "configMap", "secret", "downwardAPI", "รวมไว้แฟ้มเดียว"],
  "'projected' on the binder; 'configMap', 'secret', 'downwardAPI' on the three arrows; last label as a title banner",
  nt=True)

S13 = "13. สรุป"
t("configmap-vs-secret-table", S13,
  "ตารางสรุป ConfigMap vs Secret: เก็บอะไร, รูปแบบ (ข้อความ vs base64), describe, volume (ดิสก์ ro vs tmpfs), RBAC, encryption at rest, ใช้กับ imagePullSecrets/TLS",
  """A clean two-column comparison board with the notice board icon and the key box icon as headers and exactly two rows.
  Nong Som points with a pointer.""",
  ["ConfigMap", "Secret", "ข้อความธรรมดา", "base64 + จำกัดสิทธิ์", "ค่าตั้งค่า", "รหัส / กุญแจ / token"],
  "'ConfigMap' and 'Secret' as column headers; 'ข้อความธรรมดา' and 'ค่าตั้งค่า' under ConfigMap; 'base64 + จำกัดสิทธิ์' and 'รหัส / กุญแจ / token' under Secret; no other rows")
t("best-practices", S13,
  "แนวปฏิบัติ: สิทธิ์ get/list secrets ให้น้อยที่สุด, เปิด encryption at rest, mount เป็นไฟล์แทน env เมื่อทำได้, ไม่ commit ลง git, เปลี่ยนรหัสเป็นระยะ, ใช้ระบบภายนอกในโปรดักชัน",
  """A checklist poster with exactly four rows and icons (ID card, vault door, envelope tray, rotating dial). Nong Som ticks the boxes.""",
  ["ให้สิทธิ์น้อยที่สุด", "เปิด encryption at rest", "ใช้ไฟล์แทน env", "เปลี่ยนรหัสเป็นระยะ", "แนวปฏิบัติ Secret"],
  "the first four labels on the four checklist rows; 'แนวปฏิบัติ Secret' as a title banner")
t("command-cheatsheet", S13,
  "cheatsheet: kubectl create secret generic/tls/docker-registry, get secret -o jsonpath | base64 -d, auth can-i get secrets --as, rollout restart",
  """A tidy cheat sheet card pinned beside the key box with five command rows. Nong Som holds a magnifier.""",
  ["kubectl create secret generic", "kubectl create secret tls", "base64 -d", "kubectl auth can-i get secrets", "คำสั่งที่ใช้บ่อย"],
  "first four labels as rows on the card; 'คำสั่งที่ใช้บ่อย' as the card title")
t("next-ingress-hpa-helm", S13,
  "ต่อไป: Ingress (ประตูหน้าเดียวหลายร้าน + TLS ที่ Ingress), HPA (เพิ่มบูธอัตโนมัติตามโหลด), Helm (แพ็กทั้งร้านพร้อม ConfigMap/Secret เป็นชุดเดียว)",
  """A harbor road map with three upcoming signposts: a grand front gate with a certificate badge, a booth row that grows with
  a gauge, a big packing crate holding a whole mini shop. Nong Som walks toward them with a backpack.""",
  ["Ingress", "HPA", "Helm", "บทต่อไป"],
  "'Ingress', 'HPA', 'Helm' on the three signposts; 'บทต่อไป' as a title banner",
  allow=True)

# ---------------------------------------------------------------- LAB
l("lab0-prepare", "LAB0 เตรียมคลัสเตอร์และ image",
  "LAB0: 3 Node Ready, โหลด postgres:17.11-alpine (image-archive) และ som-shop-web:1.5 (สำเนาแอปจากบท 010 ไม่แก้โค้ด) ให้ทุก Node",
  """Three ships at the dock with a crane loading two containers onto every ship. Nong Som checks a clipboard.""",
  ["3 Node Ready", "postgres:17.11-alpine", "som-shop-web:1.5", "เตรียมของให้ครบทุกเรือ"],
  "'3 Node Ready' on the clipboard; the two image names on the two containers; last label as a title banner")
l("lab1-base64", "LAB1 base64 ไม่ใช่การเข้ารหัส",
  "LAB1: create secret generic demo → get -o yaml เห็น password: bWVvdzEyMzQ= → base64 -d ได้ meow1234; describe แสดง 8 bytes; echo vs echo -n",
  """A transparent envelope goes through a converting roller and plain letters come out; a frosted window shows only a byte
  count. Nong Som shrugs.""",
  ["bWVvdzEyMzQ=", "base64 -d → meow1234", "describe: 8 bytes", "แปลงกลับได้ทันที"],
  "'bWVvdzEyMzQ=' on the envelope; 'base64 -d → meow1234' on the roller output; 'describe: 8 bytes' on the frosted window; last label as a title banner",
  nt=True)
l("lab2-create-types", "LAB2 สร้างแบบต่าง ๆ และ type",
  "LAB2: --from-file, data + stringData (stringData ชนะ), basic-auth/tls/docker-registry และ error ของ type; ดู last-applied-configuration ที่เก็บ stringData เป็นข้อความ",
  """A workbench producing different envelope styles; two red cards from the inspector robot; one envelope has a sticky note
  outside. Nong Som inspects the sticky note.""",
  ["stringData ชนะ", "data[tls.key]: Required value", "kubernetes.io/basic-auth", "last-applied-configuration", "ซองแต่ละแบบ"],
  "'stringData ชนะ' on the merge envelope; the English error on a red card; 'kubernetes.io/basic-auth' on one envelope; 'last-applied-configuration' on the sticky note; last label as a title banner",
  nt=True)
l("lab3-use-in-pod", "LAB3 ใช้ใน Pod: env, envFrom, volume",
  "LAB3: spod ใช้ secretKeyRef/envFrom prefix SD_/volume → mount เป็น tmpfs ro, ไฟล์ -r-------- เมื่อ defaultMode 0400, /proc/1/environ เห็น DB_PASSWORD",
  """A cutaway booth: a staff member with a chest card, a memory-foam envelope tray with a permission tag, and a process
  window leaking dots. Nong Som points at each.""",
  ["secretKeyRef", "tmpfs (ro)", "-r--------", "/proc/1/environ", "env กับไฟล์ต่างกัน"],
  "'secretKeyRef' on the chest card; 'tmpfs (ro)' on the tray; '-r--------' on the tag; '/proc/1/environ' on the process window; last label as a title banner",
  nt=True)
l("lab3-update", "LAB3 ใช้ใน Pod: env, envFrom, volume",
  "LAB3 (ต่อ): patch Secret demo → ไฟล์ /etc/secret/password เปลี่ยนใน ~47 วินาที ส่วน env DB_PASSWORD ยังเป็นค่าเดิม; immutable frozen แก้ไม่ได้",
  """The deckhand robot replaces an envelope in the booth tray under a stopwatch while the staff chest card stays old; a
  laminated envelope on the side. Nong Som records.""",
  ["~47 วินาที", "env ค่าเดิม", "field is immutable", "ไฟล์เปลี่ยนเอง env ไม่เปลี่ยน"],
  "'~47 วินาที' on the stopwatch; 'env ค่าเดิม' on the chest card; 'field is immutable' on a red card by the laminated envelope; last label as a title banner",
  nt=True)
l("lab4-tls-nginx", "LAB4 TLS Secret กับ nginx HTTPS",
  "LAB4: openssl สร้าง cert CN=shop.som.local → secret tls shop-tls → nginx 443 ssl + NodePort 30081: curl ได้ (60) self-signed, curl -k ได้ HTTPS ร้านน้องส้ม, --cacert ผ่าน",
  """A glass delivery tube from a customer gangway door numbered 30081 to an nginx counter; the certificate badge on the tube;
  three customers at the check gate. Nong Som hands out the badge copy.""",
  ["shop-tls", "NodePort 30081", "curl -k", "--cacert tls.crt", "HTTPS ใช้ได้"],
  "'shop-tls' on the envelope at the counter; 'NodePort 30081' on the gangway; 'curl -k' and '--cacert tls.crt' on two customers; last label as a title banner",
  nt=True)
l("lab5-private-registry", "LAB5 imagePullSecrets กับ registry ส่วนตัว",
  "LAB5: registry:2 + htpasswd บน network kind (kind-registry:5000) → push som-menu:1.0 → Pod ไม่มีบัตร ErrImagePull, regcred ถูก Running, wrongcred 401 Unauthorized; ผูก regcred ที่ ServiceAccount default ได้",
  """A private warehouse gate on the dock with a guard robot; three cranes queue: one without a pass (red card), one with a
  wrong pass (red card), one with the right pass lifting a container. Nong Som stands by the gate.""",
  ["kind-registry:5000", "no basic auth credentials", "401 Unauthorized", "regcred", "มีบัตรถึงจะดึงได้"],
  "'kind-registry:5000' on the warehouse sign; the two English errors on two red cards; 'regcred' on the valid pass; last label as a title banner",
  nt=True)
l("lab5-cached-recheck", "LAB5 imagePullSecrets กับ registry ส่วนตัว",
  "LAB5 (ต่อ): Pod ใน namespace อื่นที่ไม่มีบัตร ตรึงลง Node ที่มี image แล้ว → ยัง ErrImagePull (kubelet v1.37 ตรวจบัตรซ้ำ) — เพราะฉะนั้น LAB นี้ใช้ image แยก som-menu ไม่ใช้ som-shop-web",
  """The container sits in a ship's cargo hold; a booth from a different zone without a pass asks for it; the deckhand robot
  refuses with a red card. A small side sign shows a separate container for this lab. Nong Som points at the side sign.""",
  ["nodeName: lab-worker", "ErrImagePull", "ใช้ image แยกสำหรับ LAB นี้", "มีบน Node ก็ต้องมีบัตร"],
  "'nodeName: lab-worker' on the booth request card; 'ErrImagePull' on the red card; 'ใช้ image แยกสำหรับ LAB นี้' on the side sign; last label as a title banner",
  nt=True)
l("lab6-projected-token", "LAB6 projected volume และ token",
  "LAB6: Pod proj รวม announcement.txt + db/password + pod-name ใน /etc/som (โหมด 0440); Secret service-account-token ของ builder ถูกเติม token/ca.crt/namespace และ describe แสดง token เต็ม",
  """A ring binder in a booth combining a notice card, an envelope and the booth name tag; beside it a robot ID card with a
  long barcode being shown fully under a magnifier. Nong Som closes the binder.""",
  ["/etc/som/db/password", "pod-name", "builder-token", "describe เห็น token", "รวมแฟ้มเดียว"],
  "'/etc/som/db/password' and 'pod-name' on two binder tabs; 'builder-token' on the ID card; 'describe เห็น token' on the magnifier; last label as a title banner",
  nt=True)
l("lab7-rbac-intern", "LAB7 RBAC: intern และสิทธิ์ทางอ้อม",
  "LAB7: intern (Role get/list/watch pods, pods/log, configmaps) → can-i get secrets = no, get secret demo → Forbidden; ยังดู Pod -o yaml เห็นแค่ชื่อ secretKeyRef ไม่เห็นค่า",
  """The intern with a grey-stripe card reads booths and the notice board; at the key box a red X blinks; a Pod blueprint
  shows only an envelope name tag, not its contents. Nong Som nods.""",
  ["can-i get secrets: no", "Forbidden", "secretKeyRef: demo", "ดูได้แต่เปิดซองไม่ได้"],
  "'can-i get secrets: no' on the intern's card; 'Forbidden' on the red X; 'secretKeyRef: demo' on the blueprint; last label as a title banner",
  nt=True)
l("lab7-pod-maker", "LAB7 RBAC: intern และสิทธิ์ทางอ้อม",
  "LAB7 (ต่อ): maker ไม่มีสิทธิ์ get secrets แต่ create pods ได้ → kubectl run peek ที่ใช้ secretKeyRef แล้ว logs ได้ stolen=<รหัส> — สิทธิ์สร้าง Pod ต้องให้อย่างระวัง",
  """A staff member builds a tiny booth that receives the envelope contents automatically, then reads them on a log scroll.
  Nong Som rings an alarm bell.""",
  ["maker", "kubectl run peek", "stolen=●●●●", "สร้าง Pod ได้ = อ่านซองได้"],
  "'maker' on the staff card; 'kubectl run peek' on the tiny booth; 'stolen=●●●●' on the scroll; last label as a title banner",
  nt=True)
l("lab8-etcd-peek", "LAB8 ส่อง etcd",
  "LAB8: kubectl -n kube-system exec etcd-lab-control-plane -- etcdctl ... get /registry/secrets/default/demo | grep -a → เห็นรหัสเป็นข้อความ (ไม่มี encryption at rest); EncryptionConfiguration เป็นทฤษฎี",
  """Inside the control tower: an archive drawer pulled out; the envelope inside is unsealed with letters visible as dots; a
  blueprint of a vault door pinned on the wall as a future plan. Nong Som holds a flashlight.""",
  ["etcdctl get", "/registry/secrets/default/demo", "เห็นเป็นข้อความ", "ยังไม่มีตู้นิรภัย"],
  "'etcdctl get' on the flashlight; '/registry/secrets/default/demo' on the drawer label; 'เห็นเป็นข้อความ' on the open envelope; last label as a title banner",
  nt=True)

F = "LAB9 ร้านน้องส้มซ่อนรหัสผ่าน"
l("lab9-architecture", F,
  "LAB9 ภาพรวม: Secret som-db-secret (POSTGRES_PASSWORD, DATABASE_URL) ให้ som-db-0 และ web ผ่าน secretKeyRef; ConfigMap ป้ายร้านจากบท 010; Secret som-tls ให้ nginx HTTPS NodePort 30082; intern อ่านได้แค่ Pod/ConfigMap",
  """Harbor overview: the key box with two envelopes on the zone wall next to the notice board; arrows from one envelope to
  the kitchen booth -0 and to three web booths; another envelope to an nginx counter with a glass tube at gangway 30082;
  the intern with a grey card in the plaza. Nong Som stands by the key box.""",
  ["som-db-secret", "som-tls", "secretKeyRef", "NodePort 30082", "intern", "ร้านที่ซ่อนรหัสแล้ว"],
  "'som-db-secret' and 'som-tls' on the two envelopes; 'secretKeyRef' on an arrow; 'NodePort 30082' on the gangway; 'intern' on the grey card; last label as a title banner")
l("lab9-start-visible", F,
  "ขั้น A: เริ่มจากสภาพท้ายบท 010 (k8s-010/) ออเดอร์ 3; intern ใช้ get deploy/sts -o yaml ยังเห็น meow1234",
  """The shop from chapter 010 with sunset awnings; the intern reads the web and db blueprints with a magnifier and finds dot
  rows. Nong Som points to the key box she is about to fill.""",
  ["k8s-010/", "orders=3", "intern เห็นรหัส", "ก่อนย้าย"],
  "'k8s-010/' on the blueprint folder; 'orders=3' on the counter; 'intern เห็นรหัส' on the magnifier; 'ก่อนย้าย' as a title banner",
  nt=True)
l("lab9-create-secret", F,
  "ขั้น B: kubectl create secret generic som-db-secret --from-literal=POSTGRES_PASSWORD=... --from-literal=DATABASE_URL=... (หรือไฟล์ 05-secret.example.yaml ที่ไม่ commit ค่าจริง)",
  """Nong Som types two dotted cards and seals them into one envelope placed in the key box; a sample YAML card stamped
  'example' sits on the desk.""",
  ["som-db-secret", "POSTGRES_PASSWORD", "DATABASE_URL", "05-secret.example.yaml", "ใส่ซองก่อนใช้"],
  "'som-db-secret' on the envelope; the two key names on the two cards; '05-secret.example.yaml' on the sample card; last label as a title banner")
l("lab9-db-secret-ref", F,
  "ขั้น C1: apply k8s/10-db.yaml (POSTGRES_PASSWORD จาก secretKeyRef) → som-db-0 rolling update ~2 วินาที PVC เดิม ออเดอร์ยัง 3",
  """The numbering robot refits booth -0; the new booth's staff gets a chest card from the envelope; the safe below is the
  same numbered safe. Nong Som checks the order counter.""",
  ["som-db-0", "secretKeyRef", "data-som-db-0", "orders=3", "รหัสมาจากซอง"],
  "'som-db-0' on the booth plate; 'secretKeyRef' on the arrow; 'data-som-db-0' on the safe; 'orders=3' on the counter; last label as a title banner",
  nt=True)
l("lab9-web-secret-ref", F,
  "ขั้น C2: apply k8s/20-web.yaml (web และ db-seed ใช้ DATABASE_URL จาก Secret) → orders=3; intern grep meow1234 ใน Deployment ได้ 0 บรรทัด, get secret → Forbidden, exec → Forbidden",
  """New web booths open; the intern's magnifier over the blueprint now finds only an envelope name tag; a red X at the key
  box and at the booth door. Nong Som smiles.""",
  ["orders=3", "meow1234: 0 บรรทัด", "Forbidden", "intern หาไม่เจอแล้ว"],
  "'orders=3' on the counter; 'meow1234: 0 บรรทัด' on the magnifier; 'Forbidden' on the red X; last label as a title banner",
  nt=True)
l("lab9-alter-user", F,
  "ขั้น D1: psql ALTER USER som PASSWORD 'purr5678' → Pod web เดิมยังตอบ 200 (connection เดิมใน pool ยังต่ออยู่) แต่รหัสเก่าต่อใหม่ไม่ได้: password authentication failed for user \"som\"",
  """The kitchen booth -0 changes the lock code on its door dial; staff already inside keep working; a new staff member with
  the old code is stopped at the door with a red card. Nong Som turns the dial.""",
  ["ALTER USER som", "200 OK", "password authentication failed", "คนเก่ายังอยู่ คนใหม่เข้าไม่ได้"],
  "'ALTER USER som' on the dial; '200 OK' on the busy booth; the English error on the red card; last label as a title banner",
  nt=True)
l("lab9-forgot-secret", F,
  "ขั้น D2 (ลองผิด): rollout restart โดยยังไม่แก้ Secret → Pod ใหม่ค้าง Init:Error (db-seed: auth_failed) แต่ Pod เดิมยังขายได้ (maxUnavailable: 0)",
  """A new web booth stuck at the gate with a red lamp because its chest card has the old code; the old booths keep serving
  customers with green lamps. Nong Som slaps her forehead.""",
  ["Init:Error", "auth_failed", "maxUnavailable: 0", "ลืมแก้ซอง"],
  "'Init:Error' on the stuck booth; 'auth_failed' on its chest card; 'maxUnavailable: 0' on the manager robot; 'ลืมแก้ซอง' as a title banner",
  nt=True)
l("lab9-update-restart", F,
  "ขั้น D3: create secret ... --dry-run=client -o yaml | kubectl apply -f - ด้วยรหัสใหม่ → rollout restart → Pod ใหม่ครบ 3 ตัว POST ได้ ออเดอร์เพิ่มเป็น 4 ข้อมูลเดิมไม่หาย",
  """Nong Som reseals a new envelope into the key box; the manager robot swaps all three booths; the order counter ticks up
  by one. Customers buy again.""",
  ["--dry-run=client -o yaml | kubectl apply -f -", "rollout restart", "orders=4", "ร้านกลับมาขายได้"],
  "the long command on the envelope sealing machine; 'rollout restart' on the manager robot; 'orders=4' on the counter; last label as a title banner",
  nt=True)
l("lab9-https", F,
  "ขั้น E: secret tls som-tls + 30-https.yaml (nginx proxy → som-web) NodePort 30082 → curl -k https://localhost:30082/api/stats ได้ร้านเดิม; ไม่มี -k ได้ (60); มี Warning PodSecurity เพราะ nginx รันเป็น root",
  """A glass delivery tube connects gangway 30082 to an nginx counter that forwards customers to the lighthouse counter of
  the web booths; a yellow warning card on the nginx counter. Nong Som cuts a ribbon.""",
  ["som-tls", "NodePort 30082", "curl -k", "Warning PodSecurity", "ร้านมี HTTPS แล้ว"],
  "'som-tls' on the envelope at the counter; 'NodePort 30082' on the gangway; 'curl -k' on a customer; 'Warning PodSecurity' on the yellow card; last label as a title banner",
  nt=True)
l("lab9-wrap-up", F,
  "สรุป LAB9: รหัสออกจาก YAML แล้ว (Secret + secretKeyRef), เปลี่ยนรหัสจริงสำเร็จ ออเดอร์ยังอยู่, intern อ่านซองไม่ได้ — แต่ etcd ยังเก็บเป็นข้อความ และต่อไปจะใช้ Ingress/HPA/Helm",
  """Nong Som stands in front of the shop holding a sealed envelope; a checklist with three ticks and one open item pointing
  to the control tower archive; three signposts toward the next chapters on the horizon.""",
  ["รหัสออกจาก YAML", "เปลี่ยนรหัสสำเร็จ", "intern เปิดซองไม่ได้", "etcd ยังต้องเข้ารหัส", "Ingress · HPA · Helm"],
  "first three labels as ticked rows; 'etcd ยังต้องเข้ารหัส' as an open row; 'Ingress · HPA · Helm' on the signposts",
  allow=True)

if __name__ == "__main__":
    main()
