#!/usr/bin/env python3
"""QA gate for the Monitoring teaching set: house rules that must hold before hand-off."""
import glob, os, re, subprocess, sys

ROOT = "/home/workspace/DevTools/03_Application_Docker/03_Monitoring"
LABS = sorted(d for d in glob.glob(f"{ROOT}/0*_LAB_*") if os.path.isdir(d))

# real-credential leak patterns (documents must use placeholders only)
LEAKS = [
    (r"ghp_[A-Za-z0-9]{20,}", "GitHub token"),
    (r"dckr_pat_[A-Za-z0-9_\-]{10,}", "Docker Hub token"),
    (r"tuchsanai@gmail\.com", "real e-mail"),
    (r"docker login -u tuchsanai", "real Docker Hub username"),
]

# The course clone URL is deliberately the real public repo (same as the shipped Traefik set) —
# labs are not runnable with a placeholder there. Flag any OTHER use of the account name.
CLONE_URL = "https://github.com/Tuchsanai/DevTools.git"
# The classroom image is published under the same account and is required to run any lab.
ALLOWED_REAL = [CLONE_URL, "tuchsanai/devtools:2569_1", "tuchsanai/devtools"]

TEXT_EXT = {".md", ".yml", ".yaml", ".sh", ".py", ".json", ".html", ".txt", ".conf", ""}
fails, warns = [], []


def read(p):
    try:
        return open(p, encoding="utf-8", errors="replace").read()
    except Exception:
        return ""


def check_lab(lab):
    name = os.path.basename(lab)
    files = [p for p in glob.glob(f"{lab}/**/*", recursive=True) if os.path.isfile(p)]
    texts = [p for p in files if os.path.splitext(p)[1].lower() in TEXT_EXT]

    readme = os.path.join(lab, "readme.md")
    if not os.path.exists(readme):
        fails.append(f"{name}: ไม่มี readme.md")
        return
    rm = read(readme)

    # 1) credential leaks anywhere in the lab
    for p in texts:
        body = read(p)
        for pat, what in LEAKS:
            if re.search(pat, body):
                fails.append(f"{name}: พบ {what} ใน {os.path.relpath(p, ROOT)}")
        # account name is allowed only inside the canonical clone URL / classroom image name
        scrubbed = body
        for allowed in ALLOWED_REAL:
            scrubbed = scrubbed.replace(allowed, "")
        stray = [m for m in re.findall(r"[Tt]uchsanai[^\s\)\"'`]*", scrubbed)]
        if stray:
            fails.append(f"{name}: พบชื่อบัญชีจริงนอก clone URL ใน {os.path.relpath(p, ROOT)} → {stray[:3]}")

    # 2) no :latest tags, no obsolete compose `version:`
    for p in glob.glob(f"{lab}/**/*compose*.y*ml", recursive=True):
        body = read(p)
        for m in re.findall(r"image:\s*([^\s#]+)", body):
            if m.endswith(":latest") or ":" not in m.split("/")[-1]:
                fails.append(f"{name}: image ไม่ได้ pin tag → {m} ({os.path.basename(p)})")
        if re.search(r"^version:", body, re.M):
            warns.append(f"{name}: compose ยังมี `version:` (deprecated) ใน {os.path.basename(p)}")
        # 3) resource limits that cannot start in this DinD environment
        for bad in ("mem_limit:", "cpus:", "memswap_limit:"):
            if re.search(rf"^\s*{re.escape(bad)}", body, re.M):
                fails.append(f"{name}: ใช้ {bad} ซึ่งรันไม่ได้ใน DinD ({os.path.basename(p)})")

    # 4) every image in images/ must be referenced by the readme, and vice versa
    imgs = sorted(os.path.basename(p) for p in glob.glob(f"{lab}/images/*")
                  if os.path.splitext(p)[1].lower() in (".png", ".jpg", ".svg", ".gif"))
    refs = set(re.findall(r"!\[[^\]]*\]\(([^)]+)\)", rm)) | set(re.findall(r'src="([^"]+)"', rm))
    refbase = {os.path.basename(r.split("#")[0]) for r in refs}
    for im in imgs:
        if im not in refbase:
            warns.append(f"{name}: ภาพ {im} ไม่ถูกอ้างใน readme")
    for r in sorted(refbase):
        if r.lower().endswith((".png", ".jpg", ".svg")) and r not in imgs:
            # may point outside images/ (e.g. ../slides_assets)
            hit = glob.glob(f"{lab}/**/{r}", recursive=True) or glob.glob(f"{ROOT}/**/{r}", recursive=True)
            if not hit:
                fails.append(f"{name}: readme อ้างภาพที่ไม่มีอยู่จริง → {r}")

    # 5) house-style sections
    for must in ("## สิ่งที่จะได้เรียนรู้", "เตรียมเครื่องเรียน", "Expected output", "เก็บกวาด"):
        if must not in rm:
            warns.append(f"{name}: readme ไม่มีหัวข้อ/บล็อก '{must}'")

    # 6) unbounded readiness loops
    for p in texts:
        body = read(p)
        if re.search(r"while\s+true.*;\s*do", body) and "seq" not in body:
            warns.append(f"{name}: อาจมี loop ไม่รู้จบใน {os.path.relpath(p, ROOT)}")

    # 7) CDN references in any HTML the lab serves
    for p in [x for x in files if x.endswith((".html", ".py"))]:
        body = read(p)
        for m in re.findall(r'https?://[^\s"\')]+', body):
            if any(k in m for k in ("cdn.", "unpkg", "jsdelivr", "googleapis", "cloudflare", "bootstrapcdn")):
                fails.append(f"{name}: อ้าง CDN {m} ใน {os.path.relpath(p, ROOT)}")

    # 8) shell scripts must be syntactically valid
    for p in glob.glob(f"{lab}/**/*.sh", recursive=True):
        r = subprocess.run(["bash", "-n", p], capture_output=True, text=True)
        if r.returncode != 0:
            fails.append(f"{name}: {os.path.basename(p)} syntax error → {r.stderr.strip()[:120]}")

    print(f"{name:46s} readme={len(rm.splitlines()):4d} บรรทัด  images={len(imgs):2d}  ไฟล์={len(files):3d}")


def main():
    print(f"ตรวจ {len(LABS)} แล็บใน {ROOT}\n")
    for lab in LABS:
        check_lab(lab)

    # deck + root readme
    deck = f"{ROOT}/Monitoring_Prometheus_Grafana_Slides.html"
    if os.path.exists(deck):
        body = read(deck)
        for m in re.findall(r'<(?:script|link|img)[^>]+(?:src|href)="(https?://[^"]+)"', body):
            fails.append(f"deck: อ้าง resource ภายนอก {m}")
        for pat, what in LEAKS:
            if re.search(pat, body):
                fails.append(f"deck: พบ {what}")
        print(f"\n{'deck':46s} slides={body.count(chr(60) + 'div class=' + chr(34) + 'slot' + chr(34) + chr(62))}  size={os.path.getsize(deck)/1024/1024:.2f} MB")
    else:
        fails.append("ไม่พบไฟล์สไลด์")

    for pat, what in LEAKS:
        if re.search(pat, read(f"{ROOT}/readme.md")):
            fails.append(f"readme หลัก: พบ {what}")

    print("\n" + "=" * 72)
    if fails:
        print(f"FAIL {len(fails)} ข้อ")
        for f in fails:
            print("  ✗", f)
    if warns:
        print(f"\nWARN {len(warns)} ข้อ")
        for w in warns:
            print("  !", w)
    if not fails and not warns:
        print("ผ่านทุกข้อ")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
