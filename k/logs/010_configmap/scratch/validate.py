import json, re, sys, os
TH = re.compile(r"[฀-๿]")
for ch, f in [("010", "010_configmap/images.json"), ("011", "011_secret/images.json")]:
    d = json.load(open(f))
    paths = [x["path"] for x in d]; ids = [x["id"] for x in d]
    assert len(paths) == len(set(paths)) and len(ids) == len(set(ids))
    bad = []
    for x in d:
        p = x["prompt"]
        m = re.search(r"Text \(verbatim, exactly (\d+) short label instances[^)]*\): (.*)\.\nConstraints:", p)
        labels = re.findall(r'"((?:[^"\\]|\\.)*?)"(?=; |$)', m.group(2))
        n = int(m.group(1))
        th = [l for l in labels if TH.search(l)]
        ok = (n == len(labels) and 1 <= n <= 7 and th and all(l.strip() for l in labels)
              and "Thai text must be rendered exactly as given, correct Thai spelling, clear Thai font, no garbled glyphs" in p
              and re.fullmatch(r".*/(01_Theory|02_LAB)/images/\d\d-[a-z0-9-]+\.png", x["path"])
              and x["path"].startswith(f"/root/workspace/DevTools/k/{'010_kubernetes_configmap' if ch=='010' else '011_kubernetes_secret'}/"))
        if ch == "010" and "do not show Secret" not in p and not any(k in x["path"] for k in ("next-chapter", "wrap-up")):
            ok = False
        if not ok: bad.append((x["id"], n, len(labels), len(th)))
    T = [x for x in d if x["id"].startswith("T")]; L = [x for x in d if x["id"].startswith("L")]
    md = [open(os.path.dirname(paths[0].replace("01_Theory/images", "01_Theory/images")) + "/imagegen-prompts.md").read()]
    root = paths[0].split("/01_Theory/")[0]
    mdT = open(f"{root}/01_Theory/images/imagegen-prompts.md").read(); mdL = open(f"{root}/02_LAB/images/imagegen-prompts.md").read()
    print(ch, "theory", len(T), "lab", len(L), "needs_test", sum(x["needs_test"] for x in d),
          "labels min/max", min(int(re.search(r"exactly (\d+)", x["prompt"]).group(1)) for x in d),
          max(int(re.search(r"exactly (\d+)", x["prompt"]).group(1)) for x in d),
          "md sections", mdT.count("\n## "), mdL.count("\n## "), "BAD", bad)
