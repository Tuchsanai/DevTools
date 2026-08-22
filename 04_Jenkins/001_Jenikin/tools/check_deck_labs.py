#!/usr/bin/env python3
"""Gate: the deck must follow the LAB README step-by-step, image-for-image.

Checks (all fatal):
  1. record shape        every slide line has the field count its kind requires
  2. assets exist        every data-asset / data-inline-svg path resolves
  3. no external URL     no http(s) src/href in the source deck
  4. lab openers         exactly one `labopen` per LAB, in order 1..6, one `labgo` each
  5. step coverage       every `## การทดลองที่ N` in a LAB README has a slide inside that LAB
  6. image coverage      every image a LAB README shows appears in that LAB's slides
                         (a deck crop registered in tools/deck_crops.py counts for its source)
  7. TOC targets         every data-goto / "หน้า N" pair on the contents slide agrees and
                         points at a `section`/`labopen` slide
Exit 0 = PASS.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "tools" / "slides_src.html"
US = "␟"

LABS = [
    (1, "001_LAB_Jenkins_On_Docker"),
    (2, "002_LAB_Declarative_Pipeline"),
    (3, "003_LAB_Docker_Build_Push"),
    (4, "004_LAB_Pipeline_From_Git"),
    (5, "005_LAB_Webhook_Trigger"),
    (6, "006_LAB_CICD_Capstone"),
]

FIELDS = {"cover": 5, "section": 5, "subsection": 5, "normal": 5, "labgo": 7, "labopen": 8}

problems: list[str] = []


def fail(msg: str) -> None:
    problems.append(msg)


def slides() -> list[list[str]]:
    text = SRC.read_text(encoding="utf-8")
    block = text.split('<script id="slideData" type="text/plain">')[1].split("</script>")[0].strip()
    return [line.split(US) for line in block.split("\n")]


def crop_sources() -> dict[str, str]:
    """source screenshot -> deck crop file name, read from tools/deck_crops.py."""
    text = (ROOT / "tools" / "deck_crops.py").read_text(encoding="utf-8")
    body = text.split("CROPS = {", 1)[1].split("\n}\n", 1)[0]
    pairs = re.findall(r'"([^"]+\.png)":\s*\(\s*"([^"]+\.png)"', body)
    return dict(pairs)


def main() -> int:
    recs = slides()
    total = len(recs)
    crops = crop_sources()

    # 1 · record shape
    for i, p in enumerate(recs, 1):
        kind = p[1] if len(p) > 1 else "?"
        want = FIELDS.get(kind)
        if want is None:
            fail(f"slide {i}: unknown kind {kind!r}")
        elif len(p) != want:
            fail(f"slide {i} ({kind}): has {len(p)} fields, expected {want}")

    raw = SRC.read_text(encoding="utf-8")

    # 2 · assets exist
    for rel in sorted(set(re.findall(r'data-(?:asset|inline-svg)="([^"]+)"', raw))):
        if not (ROOT / rel).is_file():
            fail(f"asset missing on disk: {rel}")

    # 3 · no external URL
    for m in re.finditer(r'\b(?:src|href)=["\'](https?:|//)', raw):
        fail(f"external URL in src/href at offset {m.start()}")

    # 4 · lab openers / closers
    openers = [(i, p) for i, p in enumerate(recs, 1) if p[1] == "labopen"]
    closers = [(i, p) for i, p in enumerate(recs, 1) if p[1] == "labgo"]
    if len(openers) != len(LABS):
        fail(f"expected {len(LABS)} labopen slides, found {len(openers)}")
    if len(closers) != len(LABS):
        fail(f"expected {len(LABS)} labgo slides, found {len(closers)}")
    for idx, (page, p) in enumerate(openers):
        want = str(LABS[idx][0]) if idx < len(LABS) else "?"
        if p[2].strip() != want:
            fail(f"slide {page}: labopen eyebrow {p[2]!r}, expected {want!r} (LAB order)")
    for idx, (page, p) in enumerate(closers):
        if idx < len(openers) and page <= openers[idx][0]:
            fail(f"slide {page}: labgo for LAB {idx+1} comes before its labopen")

    # lab page ranges: opener .. its labgo
    ranges: dict[int, tuple[int, int]] = {}
    for idx, (n, _) in enumerate(LABS):
        if idx < len(openers) and idx < len(closers):
            ranges[n] = (openers[idx][0], closers[idx][0])

    for n, folder in LABS:
        readme = ROOT / folder / "README.md"
        if not readme.is_file():
            fail(f"LAB {n}: README.md missing")
            continue
        md = readme.read_text(encoding="utf-8")
        if n not in ranges:
            continue
        lo, hi = ranges[n]
        window = recs[lo - 1 : hi]
        eyebrows = " | ".join(p[2] for p in window)
        blob = "\n".join(US.join(p) for p in window)

        # 5 · step coverage
        steps = [int(x) for x in re.findall(r"^## การทดลองที่ (\d+)", md, re.M)]
        for k in steps:
            if not re.search(rf"การทดลองที่ {k}(?!\d)", eyebrows):
                fail(f"LAB {n}: README has 'การทดลองที่ {k}' but no slide in pages {lo}-{hi} carries it")
        if steps and max(steps) != len(steps):
            fail(f"LAB {n}: README step numbers are not 1..N ({steps})")

        # 6 · image coverage
        used = set(re.findall(r'data-asset="slides_assets/([^"]+)"', blob))
        for img in re.findall(r"!\[[^\]]*\]\(\.\./slides_assets/([^)]+)\)", md):
            ok = img in used or crops.get(img, "\0") in used
            if not ok:
                alt = f" (crop {crops[img]})" if img in crops else ""
                fail(f"LAB {n}: README image {img}{alt} never appears in slides {lo}-{hi}")

    # 7 · TOC targets
    toc = next((p for p in recs if "data-goto=" in US.join(p)), None)
    if toc is None:
        fail("no contents slide with data-goto found")
    else:
        body = US.join(toc)
        gotos = re.findall(r'data-goto="(\d+)"', body)
        labels = re.findall(r'class="pg">หน้า (\d+)<', body)
        if len(gotos) != len(labels):
            fail(f"contents slide: {len(gotos)} data-goto vs {len(labels)} 'หน้า N' labels")
        for g, l in zip(gotos, labels):
            if g != l:
                fail(f"contents slide: data-goto={g} but label says หน้า {l}")
            page = int(g)
            if not 1 <= page <= total:
                fail(f"contents slide: target page {page} out of range 1..{total}")
            elif recs[page - 1][1] not in ("section", "labopen", "subsection"):
                fail(f"contents slide: page {page} is kind {recs[page-1][1]!r}, expected a divider")

    print(f"slides: {total}")
    for n, (lo, hi) in sorted(ranges.items()):
        print(f"LAB {n}: pages {lo}-{hi} ({hi - lo + 1} slides)")
    if problems:
        print()
        for p in problems:
            print(f"[FAIL] {p}")
        print(f"\nDECK LAB CHECK: FAIL ({len(problems)} problem(s))")
        return 1
    print("\nDECK LAB CHECK: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
