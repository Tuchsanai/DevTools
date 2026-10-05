#!/usr/bin/env python3
"""ส่วนกลางของ prompt ภาพ บท 008 PersistentVolume/PVC และ 009 StatefulSet

สำเนาเดียวกันวางไว้ที่ logs/008_pv_pvc และ logs/009_statefulset (รูปแบบเดียวกับ logs/007_deployment/imgcommon.py)
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
}
THAI = ("Thai text must be rendered exactly as given, correct Thai spelling, clear Thai font, no garbled glyphs")
THAI_RE = re.compile(r"[฀-๿]")

CH = None
T, L = [], []


def configure(ch):
    global CH
    CH = ch


def style():
    if CH == "008":
        body = f"{M_PREV} New in this chapter: {M_PV}."
    else:
        body = f"{M_PREV} Learned in chapter 008: {M_PV}. New in this chapter: {M_STS}."
    return f"{STYLE_HEAD} {body} {STYLE_TAIL}"


def asset():
    c = CHAPTERS[CH]
    return (f"Asset type: landscape 3:2 educational story illustration for Thai Kubernetes {c['topic']} lesson "
            "(README figure, about 1536x1024).")


def prompt(scene, labels, extra="", allow_later=False):
    lab = "; ".join(f'"{x}"' for x in labels)
    cons = BASE_CONS + ("" if allow_later else LATER[CH]) + (f"; {extra}" if extra else "") + f"; {THAI}."
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
        assert all(x.strip() for x in labels), slug
        assert any(THAI_RE.search(x) for x in labels), f"{slug}: no Thai label"
        assert re.fullmatch(r"[a-z0-9-]+", slug), slug
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
