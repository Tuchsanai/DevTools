#!/usr/bin/env python3
"""ส่วนกลางของ prompt ภาพ บท 008–014 (PV/PVC, StatefulSet, ConfigMap, Secret, Ingress, Helm)

บท 014: สำเนาจาก logs/templates/imgkit/imgcommon.py + CHAPTERS["014"], LATER["014"], M_HPA_SHORT/M_ING_SHORT/M_HELM,
ป้ายมีหมายเลขแบบบท 012 และกติกา Thai ที่เข้มขึ้น (สระ/วรรณยุกต์ครบ) — ค่าที่มีตัวเลขอยู่ใน Text ที่เดียว

บท 012: สำเนาจาก logs/templates/imgkit/imgcommon.py + CHAPTERS["012"], LATER["012"], M_ING และป้ายแบบมีหมายเลข
(Constraints อ้างป้ายด้วยหมายเลข "label N" จึงไม่ต้องพิมพ์ค่าที่อาจเปลี่ยนตามผลทดสอบซ้ำ — แก้ที่ Text ที่เดียว)

สำเนาเดียวกันวางไว้ที่ logs/010_configmap และ logs/011_secret (ต่อยอดจาก logs/templates/imgkit/imgcommon.py ของบท 008/009)
แต่ละบทเรียก configure(ch) แล้วใช้ t()/l() เพิ่มภาพ และ main() เขียน images.json + imagegen-prompts.md
"""
import json, os, re

K = "/root/workspace/DevTools/k"

CHAPTERS = {
    "008": {
        "root": f"{K}/008_kubernetes_pv_pvc",
        "out": f"{K}/logs/008_pv_pvc/images.json",
        "topic": "PersistentVolume and PersistentVolumeClaim",
        "title_th": "008 Kubernetes PersistentVolume และ PVC",
    },
    "009": {
        "root": f"{K}/009_kubernetes_statefulset",
        "out": f"{K}/logs/009_statefulset/images.json",
        "topic": "StatefulSet",
        "title_th": "009 Kubernetes StatefulSet",
    },
    "010": {
        "root": f"{K}/010_kubernetes_configmap",
        "out": f"{K}/logs/010_configmap/images.json",
        "topic": "ConfigMap",
        "title_th": "010 Kubernetes ConfigMap",
    },
    "011": {
        "root": f"{K}/011_kubernetes_secret",
        "out": f"{K}/logs/011_secret/images.json",
        "topic": "Secret",
        "title_th": "011 Kubernetes Secret",
    },
    "012": {
        "root": f"{K}/012_kubernetes_ingress",
        "out": f"{K}/logs/012_ingress/images.json",
        "topic": "Ingress",
        "title_th": "012 Kubernetes Ingress",
    },
    "014": {
        "root": f"{K}/014_kubernetes_helm",
        "out": f"{K}/logs/014_helm/images.json",
        "topic": "Helm",
        "title_th": "014 Kubernetes Helm",
    },
}

USE_CASE = ("Use case: scientific-educational story illustration (one panel of a continuous story) for a Thai "
            "university DevTools course; must teach the concept correctly at a glance.")
CHAR = ("Character: Nong Som (น้องส้ม) exactly as in the attached reference sheet 00-character-som.png — a chubby "
        "orange tabby cat with darker orange stripes on forehead and back, white chest, white muzzle and white paws, "
        "big round green eyes, small pink nose, short round ears, walking upright on two legs; navy captain hat with "
        "a white 7-spoke ship-wheel badge and a teal neckerchief. Keep face, proportions, colors, hat, badge and "
        "neckerchief identical to the reference; Nong Som appears exactly once, expressive and friendly.")

STYLE_HEAD = ("Style: clean flat vector cartoon, thick smooth navy outlines, soft cel shading, white background, palette "
              "navy / blue / teal with orange accents, rounded cards, crisp large legible labels, generous whitespace; "
              "matches the chapter 002–007 classroom illustration set. Shared metaphor (keep consistent across the "
              "series): cluster = the whole Kubernetes harbor; container = colored shipping container box; Pod = rounded "
              "translucent teal cabin box that wraps one or more shipping containers and carries one small IP tag, and a "
              "Pod always sits on exactly one ship; in these chapters each Pod box is also a small cat-food shop booth "
              "with a tiny awning; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor "
              "control tower on the dock (lab-control-plane); Namespace = a colored zone painted on the harbor map with "
              "a zone sign (chapter 004); a Pod label = a small colored luggage tag tied to the box.")
M_PREV = ("Learned in chapters 005–007: ReplicaSet = a shift-supervisor robot (small box-shaped teal harbor robot "
          "holding a clipboard with a head-count display); Pod template = a blueprint card the robot copies booths "
          "from; Service = a lighthouse-shaped reception counter on the dock with a fixed name plate that sends each "
          "customer to one ready booth; EndpointSlice = the clipboard list of open booths pinned on the lighthouse; "
          "readinessProbe = a green lamp above each booth (red = not ready); NodePort = a numbered gangway door on "
          "every ship; Deployment = a store-manager robot (taller navy box-shaped robot with a bow tie and a thick "
          "revision logbook). The shop's database booth (som-db) is the kitchen booth that keeps the order ledger.")
M_PV = ("Shop data = the order ledger book (a thick orange-covered notebook with a fish-shaped bookmark); volume = a "
        "storage space connected to a booth; emptyDir = a plain cardboard box inside the booth that is thrown away "
        "together with the booth; hostPath = a hatch cut into the deck of one particular ship; PersistentVolume (PV) "
        "= a sturdy steel safe locker standing in the cargo hold of exactly one ship, with a small capacity plate; "
        "PersistentVolumeClaim (PVC) = a requisition slip card held by the shop owner that states size and door "
        "type; StorageClass = an automatic safe-making workshop booth on the dock with a friendly robot arm that "
        "builds a new safe in the cargo hold of the ship where the booth was placed; binding = a matching pair of "
        "keys tied together with a ribbon, one key tag on the slip and one on the safe; reclaimPolicy = what happens "
        "to the safe when the slip is returned (Delete = the safe goes into a crusher press, Retain = the safe is "
        "padlocked and kept with a yellow tag); volumeMount = a short pneumatic tube from the booth to its safe; "
        "finalizer = a red protection clip on the slip that stops anyone tearing it while a booth still uses it; CSI "
        "driver = a universal plug adapter on the workshop wall. A safe never floats between ships")
M_STS = ("StatefulSet = a numbering shift-supervisor robot (purple-navy box-shaped robot with a numbered ticket "
         "dispenser on its chest) that opens booths one by one in order and gives each a fixed number plate ending "
         "in -0, -1, -2; every numbered booth has its own personal safe in the cargo hold painted with the same "
         "number; volumeClaimTemplates = a pad of pre-printed requisition slips, one slip torn off per booth; "
         "headless Service = an open directory book on a lectern (no lighthouse light) that lists each booth number "
         "with its direct address; partition = a rope barrier across the booth row; streaming replication = a small "
         "conveyor courier copying ledger pages from booth -0 to a read-only copy booth")
M_STS_SHORT = ("StatefulSet = a numbering shift-supervisor robot (purple-navy box-shaped robot with a numbered ticket "
               "dispenser on its chest); the database kitchen booth som-db-0 has number plate -0 and its own numbered "
               "safe in the cargo hold; headless Service = an open directory book on a lectern")
M_CM = ("ConfigMap = a teal-framed cork notice board standing in the zone, covered with neat index cards, each card "
        "showing one key and its value (the shop handbook that every booth in the same zone may read); data keys = "
        "the index cards; env / envFrom = a name-badge note card clipped on a staff member's chest at the start of "
        "a shift, copied from the board once (to change it the staff must start a new shift = a new Pod); volume "
        "mount = a small copy of the notice board hung inside the booth wall, kept up to date by kubelet; kubelet = "
        "a small deckhand robot (round grey body, one antenna, carrying a tote bag of cards) that lives on each ship "
        "and walks between the zone board and the booths every minute or so to refresh the booth boards; subPath "
        "= a single photocopied card taped flat on the booth wall that the deckhand never refreshes; ..data link = a "
        "small arrow sign on the booth board that the deckhand swings to the newest stack of cards in one move; "
        "immutable = a notice board sealed under a clear laminated acrylic sheet with a round seal sticker (cards "
        "can no longer be moved); configMapGenerator (kustomize) = a label-printer machine that prints a brand-new "
        "board whose name plate ends with a short random-looking code tag")
M_CM_SHORT = ("Learned in chapter 010: ConfigMap = a teal-framed cork notice board with index cards (key: value) that "
              "booths in the same zone read; env/envFrom = a name-badge card clipped on a staff chest at shift start "
              "(changes only with a new shift = new Pod); volume mount = a small notice board inside the booth that "
              "the kubelet deckhand robot (small round grey robot with one antenna) refreshes every minute or so; "
              "immutable = a board sealed under a clear laminated sheet")
M_SEC = ("Secret = a navy envelope closed with an orange paw-print wax seal, kept in a small steel key box on the "
         "zone wall next to the notice board; base64 = a TRANSPARENT envelope: the letters inside are only rewritten "
         "in a different alphabet and anyone can still see and convert them back (it is NOT a lock); a "
         "real lock = a padlock; encryption at rest = a heavy round vault door inside the harbor control tower "
         "where the tower archive cabinet (etcd) keeps every record; etcd = the tall archive cabinet of drawers in the "
         "control tower; RBAC = staff ID cards on lanyards with a colored stripe: a green-stripe card may open the "
         "key box, a grey-stripe intern card may only look at the notice board and booths (the key box stays shut "
         "with a red X); Secret volume = a sealed envelope tray inside the booth made of soft memory foam (tmpfs: "
         "kept only in memory, never written on the ship deck, emptied when the booth closes); TLS = a sealed "
         "glass delivery tube between the customer and the counter, with a certificate badge (tls.crt) on the tube "
         "and a private key (tls.key) hanging inside the counter; imagePullSecrets = a gate pass card shown at the "
         "gate of a private container warehouse (registry) on the dock before a crane may pick up a container; "
         "projected volume = one ring binder inside the booth that combines a notice card, a sealed envelope and the "
         "booth's own name tag; service-account-token = a robot staff ID card with a long stamped barcode strip")
M_SEC_SHORT = ("Learned in chapter 011: Secret = a navy envelope closed with an orange paw-print wax seal kept in a small "
               "steel key box on the zone wall; a kubernetes.io/tls Secret holds a certificate badge (tls.crt) and a "
               "private key (tls.key); a kubernetes.io/basic-auth Secret holds a username card and a dotted password "
               "card")
M_ING = ("Ingress = the harbor's single main front gate building on the dock: a grand reception hall with one big "
         "direction signboard on a stand listing rules (each rule row = a ship-shop name (host) and a hallway door "
         "name (path) pointing to one lighthouse counter = Service); Ingress controller = a friendly receptionist "
         "robot (rounded white-and-teal body, small cap, wears a uniform vest with a colored round emblem, holds a "
         "lantern) who stands at the gate, reads the signboard and walks each customer to the right lighthouse "
         "counter — without the receptionist robot the signboard does nothing; IngressClass = the uniform: the "
         "colored emblem on the robot's vest matches a small colored tag hanging on the signboard, telling which "
         "company's receptionist is responsible for that board (a gold star on the tag = the default class); host "
         "= the shop name written on the customer's visit ticket; path = a hallway door plate inside the hall; "
         "backend = the lighthouse counter the signboard row points to (counters are now indoor ClusterIP "
         "counters with no gangway door of their own); entry point = the gate's two doors: a plain wooden door "
         "(HTTP) and a glass security door (HTTPS); TLS at the Ingress = the glass security door carries a stamped "
         "certificate seal plate and the receptionist keeps the private key on a lanyard inside, the envelope "
         "comes from the zone key box; SNI = the customer says the shop name through the intercom before the glass "
         "door chooses which seal plate to show; default certificate = a plain grey generic seal plate; "
         "defaultBackend = a lost-and-found desk beside the gate for customers whose ticket matches no row; 404 = "
         "an empty wrong-door with a small sign; 503 = a counter that exists but every booth behind it is closed "
         "(red lamps); controller-specific middleware = small checkpoints along the hallway: an arrow stand that "
         "sends customers from the wooden door to the glass door (redirect), a turnstile that checks a staff ID "
         "card from a sealed envelope (basic auth), a ticket trimmer that cuts the first part off the ticket "
         "(strip prefix); access log = an open guest book on the reception desk; dashboard = a glass monitoring "
         "board behind the receptionist showing route lines; Gateway API = a brand-new modern passenger terminal "
         "building next to the old gate, with a terminal operator company plaque (GatewayClass), the terminal "
         "building with numbered boarding gates (Gateway listeners) and route boards that each shop team hangs "
         "itself (HTTPRoute); weighted canary = a turnstile splitting customers into two lanes of different "
         "widths")
M_ING_SHORT = ("Learned in chapter 012: Ingress = the harbor's single main front gate building with one big direction "
               "signboard (rules: shop name + hallway door → lighthouse counter); Traefik = a friendly receptionist robot "
               "(rounded white-and-teal body, small cap, teal uniform vest with a round emblem, holds a lantern) who walks "
               "each customer through the glass security door (HTTPS) to the right counter; IngressClass = the emblem on "
               "the vest (a gold star tag = default class); Middleware = small checkpoints along the hallway (redirect "
               "arrow stand, staff-card turnstile)")
M_HPA_SHORT = ("Learned in chapter 013: booth fatigue meter = a round gauge dial on the roof of every Pod booth (CPU); "
               "metrics-server = a small meter-reader robot (round mint-green body, one wheel, peaked cap, clipboard and a "
               "tiny pencil); HorizontalPodAutoscaler (HPA) = an assistant-manager robot (slim teal-and-navy box-shaped "
               "robot with a small headset and a tablet showing a gauge with plus and minus buttons) standing beside the "
               "store-manager robot; minReplicas / maxReplicas = a booth rail with a green anchor marker and a red "
               "end-stop")
M_HELM = ("chart = a franchise kit for a ready-made cat-food shop: a sturdy navy-and-orange cardboard crate with a "
          "paw-print logo, a rope handle and a ship-wheel sticker, containing a manual booklet, a stack of stencil "
          "molds and an order form (one kit can open many branches); Chart.yaml = the kit's label card stuck on the "
          "lid showing kit name, kit version and app version; values.yaml = the customization order form (a "
          "clipboard sheet with checkboxes and blank fields for shop name, theme color swatch and number of booths); "
          "an environment values file = a second order form with a colored corner tab (dev = orange tab, prod = navy "
          "tab) laid on top of the default form; --set = a sticky note slapped on the very top that wins over the "
          "forms below; templates = stencil molds for signs, booths and notice boards with empty slots shaped like "
          "curly brackets waiting to be filled; _helpers.tpl = a rack of reusable rubber stamps; values.schema.json "
          "= an inspection desk with a checklist and a stamp that rejects a wrong order form before any building "
          "starts; render (helm template) = a printing table where molds plus the order form produce finished paper "
          "blueprints without building anything; helm (the CLI) = the contractor robot: a sturdy orange-and-navy "
          "box-shaped builder robot with a bright orange safety hard hat, a tool belt and a tablet, who reads the "
          "order form, presses the molds and assembles the shop at the harbor (never an old iron helmet, never a big "
          "ship's steering wheel); release = a branch shop actually opened from the kit, with a branch name banner "
          "over its awning (one kit, many branches; each branch lives in its own painted zone); revision = the "
          "branch's renovation logbook, a thick spiral notebook with numbered tabbed pages, one page per install, "
          "upgrade or rollback, and a rollback writes a NEW page that copies an older page (page numbers never go "
          "backwards); release record = that logbook stored inside a navy steel cabinet drawer in the zone, the "
          "pages are only folded and shrink-wrapped (base64 + gzip), not locked; repository = a printed franchise "
          "catalog brochure with kit pictures and version stickers; Artifact Hub = a big catalog kiosk on the dock "
          "where many publishers list kits, verified publishers have a blue check badge; OCI registry = a franchise "
          "kit warehouse on the dock with numbered shelves and a gate-pass turnstile (registry login), kits stored "
          "as sealed crates with a fingerprint sticker (digest); package = shrink-wrapping the kit into a sealed "
          "crate; hook = a special step card clipped to the manual: before or after opening the branch (for example "
          "a shelf-stocking cart that fills the kitchen shelves right after opening); helm test = a shop inspector "
          "robot (small white robot with a magnifying glass, a checklist clipboard and a green approval stamp) that "
          "walks through the finished branch and stamps pass or fail; NOTES.txt = a welcome card handed over after "
          "opening; dependency (subchart) = smaller kits packed inside the big kit; server-side apply / field "
          "manager = little colored owner name tags pinned on each fitting of the shop (the contractor robot's tags "
          "are orange, older hand-applied kubectl tags are grey); conflict = one fitting carrying two different "
          "owner tags with a red spark between them; take-ownership = the contractor robot pinning its branch banner "
          "on an existing hand-built shop; force-conflicts = the robot replacing the grey owner tag with its orange "
          "tag; GitOps (Argo CD / Flux) = a watchful robot reading a binder of shop plans and keeping the branch the "
          "same as the binder; Kustomize = transparent overlay sheets laid on top of a plain blueprint")

STYLE_TAIL = ("Robots are simple friendly machines, never cats; customers and staff are faceless people silhouettes, "
              "never cats. Every cargo item, crate or prop is cat-food-shop or harbor related only (kibble bags, cat "
              "food cans, fish-shaped treats, food bowls, order ledgers, safes, ropes, ships).")

BASE_CONS = ("only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish "
             "or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; "
             "every sign, card, name plate, row, column, lane, zone or panel that is drawn carries exactly the "
             "listed label assigned to it — no blank signs, no extra signs (only small luggage tags, awnings and "
             "icon rows may be color-only where the constraints explicitly say so); a Pod box is never split across "
             "two ships; numbers appear only where listed; never draw technical words literally (no plant seeds for "
             "seed, no court papers for claim, no wedding rings or rope bondage for bind, no food rations for "
             "provision, no loudspeaker for volume, no gravestone for delete)")
LATER = {
    "008": ("; do not show StatefulSet, Ingress, HorizontalPodAutoscaler, ConfigMap or Secret objects or words, and "
            "no numbering ticket-dispenser robot"),
    "009": "; do not show Ingress, HorizontalPodAutoscaler, ConfigMap or Secret objects or words",
    "010": ("; do not show Secret objects or the word Secret, no sealed envelopes, no padlocks, no Ingress, "
            "HorizontalPodAutoscaler or Helm objects or words"),
    "011": "; do not show Ingress, HorizontalPodAutoscaler or Helm objects or words, no operator robots",
    "012": ("; do not show HorizontalPodAutoscaler, Helm, GatewayClass, Gateway or HTTPRoute objects or words, no "
            "passenger terminal building, no autoscaling robots"),
    "014": ("; do not show operator, Argo CD, Flux, GitOps or Kustomize objects or words, no plan-binder robot, no "
            "overlay sheets"),
}
# บท 014: ห้ามวาดคำตามตัวอักษร — ใช้กับทุกภาพของบท (รวมภาพที่ allow=True)
LITERAL_014 = ("never draw technical words literally: a chart is never a graph, plot, diagram or nautical map, a hook is "
               "never a fishing hook or metal hook, the helm CLI is never an iron helmet or a big ship's steering wheel (Nong Som's small hat badge stays exactly as in the reference), a release "
               "is never a balloon or a bird being released, a template is never a cookie cutter, a repository is never "
               "a library bookshelf, a registry is never a guest book, a rollback is never a rolling barrel; numbers, "
               "version strings, revision numbers and durations appear only inside the listed labels")
PW = ("never show a real-looking password: passwords appear only as the listed example value or as dots ●●●●")
THAI = ("Thai text must be rendered exactly as given, correct Thai spelling including all vowels and tone marks, "
        "clear Thai font, no garbled glyphs")
THAI_RE = re.compile(r"[฀-๿]")

CH = None
T, L = [], []


def configure(ch):
    global CH
    CH = ch


def style():
    if CH == "008":
        body = f"{M_PREV} New in this chapter: {M_PV}."
    elif CH == "009":
        body = f"{M_PREV} Learned in chapter 008: {M_PV}. New in this chapter: {M_STS}."
    elif CH == "010":
        body = (f"{M_PREV} Learned in chapters 008–009: PV = a steel safe locker in the cargo hold of one ship, PVC = "
                f"a requisition slip card; {M_STS_SHORT}. New in this chapter: {M_CM}.")
    elif CH == "014":
        body = (f"{M_PREV} Learned in chapters 008–011: PV = a steel safe locker in the cargo hold of one ship, PVC = "
                f"a requisition slip card; {M_STS_SHORT}. {M_CM_SHORT}. {M_SEC_SHORT}. {M_ING_SHORT}. {M_HPA_SHORT}. "
                f"New in this chapter: {M_HELM}.")
    elif CH == "012":
        body = (f"{M_PREV} Learned in chapters 008–010: PV = a steel safe locker in the cargo hold of one ship; "
                f"{M_STS_SHORT}. {M_CM_SHORT}. {M_SEC_SHORT}. New in this chapter: {M_ING}.")
    else:
        body = (f"{M_PREV} Learned in chapters 008–009: PV = a steel safe locker in the cargo hold of one ship, PVC = "
                f"a requisition slip card; {M_STS_SHORT}. {M_CM_SHORT}. New in this chapter: {M_SEC}.")
    return f"{STYLE_HEAD} {body} {STYLE_TAIL}"


def asset():
    c = CHAPTERS[CH]
    return (f"Asset type: landscape 3:2 educational story illustration for Thai Kubernetes {c['topic']} lesson "
            "(README figure, about 1536x1024).")


def prompt(scene, labels, extra="", allow_later=False):
    if CH in ("012", "014"):  # มีหมายเลข → Constraints อ้าง "label N" ได้โดยไม่ซ้ำค่า
        lab = "; ".join(f'label {i}: "{x}"' for i, x in enumerate(labels, 1))
    else:
        lab = "; ".join(f'"{x}"' for x in labels)
    pw = f"; {PW}" if CH in ("010", "011", "012", "014") else ""
    lit = f"; {LITERAL_014}" if CH == "014" else ""
    cons = BASE_CONS + ("" if allow_later else LATER[CH]) + lit + pw + (f"; {extra}" if extra else "") + f"; {THAI}."
    return "\n".join([
        USE_CASE, asset(), f"Scene: {scene}", CHAR, style(),
        f"Text (verbatim, exactly {len(labels)} short label instances; a label listed twice appears exactly twice): {lab}.",
        f"Constraints: {cons}",
    ])


def t(slug, section, cap, scene, labels, extra="", allow=False, nt=False):
    T.append((slug, section, cap, scene, labels, extra, allow, nt))


def l(slug, section, cap, scene, labels, extra="", allow=False, nt=False):
    L.append((slug, section, cap, scene, labels, extra, allow, nt))


def build(items, kind):
    root = CHAPTERS[CH]["root"]
    out = []
    for i, (slug, sec, cap, scene, labels, extra, allow, nt) in enumerate(items, 1):
        assert 1 <= len(labels) <= 7, (slug, len(labels))
        assert len(set(labels)) == len(labels), f"{slug}: duplicate label"
        assert all(x.strip() for x in labels), slug
        assert any(THAI_RE.search(x) for x in labels), f"{slug}: no Thai label"
        assert re.fullmatch(r"[a-z0-9-]+", slug), slug
        if CH == "014":  # ค่าที่มีตัวเลข (เวอร์ชัน revision เวลา พอร์ต) อยู่ใน Text ที่เดียว ห้ามซ้ำใน Scene/Constraints
            for x in labels:
                for tok in re.findall(r"[0-9][0-9.:/=-]*", x):
                    if len(tok) >= 2 or not tok.isdigit():
                        assert tok not in scene and tok not in extra, f"{slug}: '{tok}' (from '{x}') repeated outside Text"
            assert not re.search(r"[0-9]{2,}|v[0-9]|err=|orders=", scene + extra), f"{slug}: number outside Text"
        if CH == "012":  # ค่าที่มีตัวเลข (พอร์ต ผลทดสอบ) อยู่ใน Text ที่เดียว ห้ามซ้ำใน Scene/Constraints
            for x in labels:
                if re.search(r"[0-9]", x):
                    assert x not in scene and x not in extra, f"{slug}: '{x}' repeated outside Text"
            assert not re.search(r"300[89][0-9]|err=|orders=", scene + extra), f"{slug}: test value outside Text"
        sub = "01_Theory" if kind == "T" else "02_LAB"
        out.append({
            "id": f"{kind}{i:02d}",
            "path": f"{root}/{sub}/images/{i:02d}-{slug}.png",
            "section": sec,
            "caption_th": cap,
            "prompt": prompt(" ".join(scene.split()), labels, extra, allow),
            "needs_test": bool(nt),
        })
    return out


def write_md(items, title, path):
    c = CHAPTERS[CH]
    lines = ["Generated with built-in image_gen via cyolo1 using 00-character-som.png as character reference", "",
             f"# Final image prompts — {c['title_th']} ({title})", "",
             "ทุกภาพแนบ `01_Theory/images/00-character-som.png` เป็นภาพอ้างอิงตัวละครน้องส้ม", ""]
    for it in items:
        nt = " · needs_test (ตรวจ/ปรับหลังทดสอบ LAB จริง)" if it.get("needs_test") else ""
        lines += [f"## {os.path.basename(it['path'])}", "",
                  f"> {it['id']} · {it['section']} — {it['caption_th']}{nt}", "",
                  "```text", it["prompt"], "```", ""]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    c = CHAPTERS[CH]
    th = build(T, "T")
    lb = build(L, "L")
    data = th + lb
    paths = [d["path"] for d in data]
    assert len(paths) == len(set(paths)), "duplicate path"
    with open(c["out"], "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    write_md(th, "Theory", f"{c['root']}/01_Theory/images/imagegen-prompts.md")
    write_md(lb, "LAB", f"{c['root']}/02_LAB/images/imagegen-prompts.md")
    print(f"{CH}: theory {len(th)}, lab {len(lb)}, needs_test {sum(1 for d in data if d['needs_test'])}")
