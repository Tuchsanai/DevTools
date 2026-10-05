#!/usr/bin/env python3
"""ส่วนกลางของ prompt ภาพ บท 005 ReplicaSet / 006 Service / 007 Deployment (แยกจากบทรวม 005_rs_deploy_svc)

สำเนาเดียวกันวางไว้ที่ logs/005_replicaset, logs/006_service, logs/007_deployment
แต่ละบทเรียก configure(ch) แล้วใช้ t()/l() เพิ่มภาพ และ main() เขียน images.json + imagegen-prompts.md
"""
import json, os

K = "/root/workspace/DevTools/k"

CHAPTERS = {
    "005": {
        "root": f"{K}/005_kubernetes_replicaset",
        "out": f"{K}/logs/005_replicaset/images.json",
        "topic": "ReplicaSet",
        "title_th": "005 Kubernetes ReplicaSet",
    },
    "006": {
        "root": f"{K}/006_kubernetes_service",
        "out": f"{K}/logs/006_service/images.json",
        "topic": "Service",
        "title_th": "006 Kubernetes Service",
    },
    "007": {
        "root": f"{K}/007_kubernetes_deployment",
        "out": f"{K}/logs/007_deployment/images.json",
        "topic": "Deployment",
        "title_th": "007 Kubernetes Deployment",
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
              "matches the chapter 002–004 classroom illustration set. Shared metaphor (keep consistent across the "
              "series): cluster = the whole Kubernetes harbor; container = colored shipping container box; Pod = rounded "
              "translucent teal cabin box that wraps one or more shipping containers and carries one small IP tag, and a "
              "Pod always sits on exactly one ship; in these chapters each Pod box is also a small cat-food shop booth "
              "with a tiny awning; Node = cargo ship (worker ships lab-worker and lab-worker2); Control Plane = harbor "
              "control tower on the dock (lab-control-plane); Namespace = a colored zone painted on the harbor map with "
              "a zone sign (chapter 004); a Pod label = a small colored luggage tag tied to the box.")
M_RS = ("ReplicaSet = a shift-supervisor robot (small box-shaped teal harbor robot holding a clipboard with a "
        "head-count display) that keeps counting the boxes wearing its tag and adds or removes boxes so the count "
        "always matches; Pod template = a blueprint card / stencil the robot copies boxes from; ownerReferences = a "
        "small owner badge clipped on each box pointing back to its robot")
M_SVC = ("Service = a lighthouse-shaped reception counter on the dock with a fixed name plate and a fixed address "
         "plate that sends each customer to one ready booth; EndpointSlice = the clipboard list of currently open "
         "booths pinned on the lighthouse counter; readinessProbe = a green lamp above each booth (red lamp = not "
         "ready, gets no customers); kube-proxy = a direction signpost standing on every ship; NodePort = a numbered "
         "gangway door on every ship that outside customers can walk in through")
M_DEP = ("Deployment = a store-manager robot (taller navy box-shaped robot with a bow tie and a thick revision "
         "logbook) that directs one or more shift-supervisor robots, one per version; pod-template-hash = a small "
         "barcode sticker identifying one version (never food); rolling update = swapping booth signboards one booth "
         "at a time while the shop stays open; rollback = flipping the revision logbook back to an earlier page")
STYLE_TAIL = ("Robots are simple friendly machines, never cats; customers and staff are faceless people silhouettes, "
              "never cats. Every cargo item, crate or prop is cat-food-shop related only (kibble bags, cat food cans, "
              "fish-shaped treats, food bowls).")

BASE_CONS = ("only the verbatim labels listed above, spelled exactly (Thai and English), no other words, no gibberish "
             "or pseudo-text, no extra speech bubbles with text, no watermark, no signature, no real company logos; "
             "every sign, card, name plate, row, column, lane, zone or panel that is drawn carries exactly the "
             "listed label assigned to it — no blank signs, no extra signs (only small luggage tags, awnings and "
             "icon rows may be color-only where the constraints explicitly say so); a Pod box is never split across "
             "two ships; numbers appear only where listed")
LATER = {
    # สิ่งที่ "ยังไม่เรียน" ของแต่ละบท — ห้ามโผล่ในภาพ ยกเว้นภาพที่ allow=True (ภาพปูทางบทถัดไป)
    "005": ("; do not show the lighthouse counter, store-manager robot, Service, Deployment, Ingress, StatefulSet, "
            "PersistentVolume, HorizontalPodAutoscaler or ConfigMap objects or words"),
    "006": ("; do not show the store-manager robot, Deployment, Ingress, StatefulSet, PersistentVolume, "
            "HorizontalPodAutoscaler or ConfigMap objects or words"),
    "007": ("; do not show Ingress, StatefulSet, PersistentVolume, HorizontalPodAutoscaler or ConfigMap objects or "
            "words"),
}

CH = None
T, L = [], []


def configure(ch):
    global CH
    CH = ch


def style():
    ms = {"005": [M_RS], "006": [M_RS, M_SVC], "007": [M_RS, M_SVC, M_DEP]}[CH]
    new = {"005": "New in this chapter: ", "006": "Learned in chapter 005: ", "007": "Learned in chapters 005–006: "}[CH]
    if CH == "005":
        body = new + ms[0] + "."
    elif CH == "006":
        body = new + ms[0] + ". New in this chapter: " + ms[1] + "."
    else:
        body = new + ms[0] + "; " + ms[1] + ". New in this chapter: " + ms[2] + "."
    return f"{STYLE_HEAD} {body} {STYLE_TAIL}"


def asset():
    c = CHAPTERS[CH]
    return (f"Asset type: landscape 3:2 educational story illustration for Thai Kubernetes {c['topic']} lesson "
            "(README figure, about 1536x1024).")


def prompt(scene, labels, extra="", allow_later=False):
    lab = "; ".join(f'"{x}"' for x in labels)
    cons = BASE_CONS + ("" if allow_later else LATER[CH]) + (f"; {extra}" if extra else "") + "."
    return "\n".join([
        USE_CASE, asset(), f"Scene: {scene}", CHAR, style(),
        f"Text (verbatim, exactly {len(labels)} short label instances; a label listed twice appears exactly twice): {lab}.",
        f"Constraints: {cons}",
    ])


def t(slug, section, cap, scene, labels, extra="", allow=False, nt=False, src="new"):
    """src: id/ชื่อไฟล์ในบทรวม เช่น 'T06 06-rs-self-healing.png' (แก้แล้วให้ต่อท้าย ' (แก้)') หรือ 'new'"""
    T.append((slug, section, cap, scene, labels, extra, allow, nt, src))


def l(slug, section, cap, scene, labels, extra="", allow=False, nt=False, src="new"):
    L.append((slug, section, cap, scene, labels, extra, allow, nt, src))


def build(items, kind):
    root = CHAPTERS[CH]["root"]
    out, srcs = [], []
    for i, (slug, sec, cap, scene, labels, extra, allow, nt, src) in enumerate(items, 1):
        assert 1 <= len(labels) <= 7, slug
        assert all(x.strip() for x in labels), slug
        sub = "01_Theory" if kind == "T" else "02_LAB"
        d = {
            "id": f"{kind}{i:02d}",
            "path": f"{root}/{sub}/images/{i:02d}-{slug}.png",
            "section": sec,
            "caption_th": cap,
            "prompt": prompt(" ".join(scene.split()), labels, extra, allow),
        }
        if nt:
            d["needs_test"] = True
        out.append(d)
        srcs.append((d["id"], os.path.basename(d["path"]), src))
    return out, srcs


def write_md(items, title, path):
    c = CHAPTERS[CH]
    lines = ["Generated with built-in image_gen via cyolo1 using 00-character-som.png as character reference", "",
             f"# Final image prompts — {c['title_th']} ({title})", "",
             "ทุกภาพแนบ `01_Theory/images/00-character-som.png` เป็นภาพอ้างอิงตัวละครน้องส้ม", ""]
    for it in items:
        nt = " · needs_test (สร้าง/ปรับหลังทดสอบ LAB จริง)" if it.get("needs_test") else ""
        lines += [f"## {os.path.basename(it['path'])}", "",
                  f"> {it['id']} · {it['section']} — {it['caption_th']}{nt}", "",
                  "```text", it["prompt"], "```", ""]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    c = CHAPTERS[CH]
    th, ts = build(T, "T")
    lb, ls = build(L, "L")
    data = th + lb
    paths = [d["path"] for d in data]
    assert len(paths) == len(set(paths)), "duplicate path"
    with open(c["out"], "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    write_md(th, "Theory", f"{c['root']}/01_Theory/images/imagegen-prompts.md")
    write_md(lb, "LAB", f"{c['root']}/02_LAB/images/imagegen-prompts.md")
    # แหล่งที่มาของแต่ละภาพ (ใช้เขียน README-split.md)
    with open(os.path.join(os.path.dirname(c["out"]), "image-sources.tsv"), "w", encoding="utf-8") as f:
        f.write("id\tfile\tsource\n")
        for r in ts + ls:
            f.write("\t".join(r) + "\n")
    print(f"{CH}: theory {len(th)}, lab {len(lb)}, needs_test {sum(1 for d in data if d.get('needs_test'))}")
