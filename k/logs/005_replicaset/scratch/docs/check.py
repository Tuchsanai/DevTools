#!/usr/bin/env python3
"""ตรวจ README บท 005: ภาพ/ลิงก์ชี้ไฟล์ที่มี, anchor มีปลายทาง, ใช้ภาพ T/L ครบและ caption ตรง images.json, YAML parse ได้, ไม่มี Service/Deployment ในขั้นตอน LAB, ไม่มีรายละเอียดเครื่องทดสอบ"""
import html, json, os, re, sys, unicodedata, urllib.parse
import yaml

ROOT = "/root/workspace/DevTools/k"
CH = f"{ROOT}/005_kubernetes_replicaset"
IMGS = json.load(open(f"{ROOT}/logs/005_replicaset/images.json"))
PENDING = {os.path.normpath(i["path"]) for i in IMGS}  # ภาพที่กำลังสร้าง (ชื่อตาม images.json)
DOCS = [f"{CH}/README.md", f"{CH}/01_Theory/README.md", f"{CH}/02_LAB/README.md"]
errors, notes = [], []


def slug(text):
    t = re.sub(r"<[^>]+>", "", text).strip().lower()
    t = re.sub(r"`", "", t)
    out = []
    for ch in t:
        cat = unicodedata.category(ch)
        if ch in "-_ " or cat[0] in "LMN":
            out.append("-" if ch == " " else ch)
    return "".join(out)


def anchors_of(path, cache={}):
    if path in cache:
        return cache[path]
    s = open(path, encoding="utf-8").read()
    s_nocode = re.sub(r"```.*?```", "", s, flags=re.S)
    seen, res = {}, set()
    for m in re.finditer(r"^#{1,6} (.+)$", s_nocode, flags=re.M):
        b = slug(m.group(1))
        n = seen.get(b, 0)
        res.add(b if n == 0 else f"{b}-{n}")
        seen[b] = n + 1
    res |= set(re.findall(r'id="([^"]+)"', s))
    cache[path] = res
    return res


for doc in DOCS:
    s = open(doc, encoding="utf-8").read()
    base = os.path.dirname(doc)
    rel = os.path.relpath(doc, ROOT)
    nocode = re.sub(r"```.*?```", "", s, flags=re.S)
    # 1) img src
    for src in re.findall(r'<img src="([^"]+)"', s):
        p = os.path.normpath(os.path.join(base, src))
        if os.path.exists(p):
            continue
        if p in PENDING:
            notes.append(f"{rel}: ภาพกำลังสร้าง (ชื่อตรง images.json) {src}")
        else:
            errors.append(f"{rel}: img ไม่มีไฟล์ {src}")
    # 2) markdown links
    for txt, href in re.findall(r"(?<!!)\[([^\]]*)\]\(([^)\s]+)\)", nocode):
        if href.startswith(("http://", "https://", "mailto:")):
            continue
        path, _, frag = href.partition("#")
        target = os.path.normpath(os.path.join(base, urllib.parse.unquote(path))) if path else doc
        if not os.path.exists(target):
            errors.append(f"{rel}: ลิงก์ไม่มีปลายทาง {href}")
            continue
        if frag:
            frag = urllib.parse.unquote(frag)
            if os.path.isdir(target) or not target.endswith(".md"):
                errors.append(f"{rel}: anchor ไปที่ไม่ใช่ .md {href}")
            elif frag not in anchors_of(target):
                errors.append(f"{rel}: anchor ไม่พบ {href}")
    # 3) YAML blocks
    for i, blk in enumerate(re.findall(r"```yaml\n(.*?)```", s, flags=re.S)):
        blk = re.sub(r"^> ?", "", blk, flags=re.M) if blk.lstrip().startswith(">") else blk
        try:
            list(yaml.safe_load_all(blk))
        except Exception as e:
            errors.append(f"{rel}: YAML block {i+1} parse ไม่ได้: {e}")
    # 4) รายละเอียดเครื่องทดสอบ / credential
    for pat in [r"2224", r"172\.18\.0\.1", r"askpass", r"\b1300\d\b", r"\b300[1-3]\b", r"rs005lab", r"abd71a", r"62\s?GB", r"61\.5GiB"]:
        for m in re.finditer(pat, s, flags=re.I):
            errors.append(f"{rel}: พบรายละเอียดเครื่องทดสอบ '{m.group(0)}'")

# 5) ภาพ T/L ครบ + caption ตรง
used = {}
for doc in DOCS[1:]:
    s = open(doc, encoding="utf-8").read()
    for src, cap in re.findall(r'<img src="([^"]+)"[^>]*><br>\s*<em><b>รูปที่ \d+</b> (.*?)</em>', s, flags=re.S):
        used[os.path.normpath(os.path.join(os.path.dirname(doc), src))] = html.unescape(cap)
for it in IMGS:
    p = os.path.normpath(it["path"])
    if p not in used:
        errors.append(f"ไม่ได้ใช้ภาพ {it['id']} {os.path.basename(p)}")
    elif used[p] != it["caption_th"]:
        errors.append(f"caption ไม่ตรง {it['id']}")
idx = open(DOCS[0], encoding="utf-8").read()
if html.unescape(re.search(r"<em>(.*?)</em>", idx, re.S).group(1)) != IMGS[0]["caption_th"]:
    errors.append("README หน้ารวม: caption T01 ไม่ตรง")
shots = re.findall(r'src="(images/screenshots/[^"]+)"', open(DOCS[2], encoding="utf-8").read())
if len(set(shots)) != 4:
    errors.append(f"LAB: screenshot ไม่ครบ 4 ({len(set(shots))})")

# 6) ไม่มี Service/Deployment ในขั้นตอน LAB (code block bash/text/yaml ของ 02_LAB)
lab = open(DOCS[2], encoding="utf-8").read()
for blk in re.findall(r"```(?:bash|yaml)\n(.*?)```", lab, flags=re.S):
    for pat in [r"kind:\s*(Service|Deployment)", r"kubectl\s+expose", r"kubectl\s+rollout", r"\b(svc|deploy|deployment|service)s?/", r"kubectl\s+(get|create|apply|describe|delete)\s+[^\n]*\b(svc|services?|deploy|deployments?)\b"]:
        for m in re.finditer(pat, blk, flags=re.I):
            errors.append(f"LAB: พบ Service/Deployment ในขั้นตอน: {m.group(0)}")

print(f"ตรวจ {len(DOCS)} ไฟล์, ภาพ T/L ที่ใช้ {len([p for p in used if p in PENDING])}/{len(IMGS)}, screenshot {len(set(shots))}")
for n in sorted(set(notes)):
    pass
print(f"ภาพที่ยังรอสร้าง (ชื่อตรง images.json): {len(set(notes))}")
if errors:
    print("❌ พบปัญหา", len(errors))
    for e in errors:
        print(" -", e)
    sys.exit(1)
print("✅ ผ่านทุกข้อ")
