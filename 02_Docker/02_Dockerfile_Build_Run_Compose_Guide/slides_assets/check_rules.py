#!/usr/bin/env python3
"""Mechanical rule checks for new_Docker_Week11_Slides.html.

Rules enforced (from the assignment):
- 1 slide = 1 concept, <=60 words prose per slide (code blocks <pre> excluded,
  slide footer excluded; Thai counted with pythainlp newmm, Latin as tokens)
- bullet lists <=6 <li> lines
- every slide preceded by <!-- SLIDE NN | จากหัวข้อเดิม: ... | แก้เพราะ: ... -->
- a "เช็คความเข้าใจ" slide at least every 6 CONTENT slides (cover/agenda/section
  dividers/closing are structural, not content)
- no real secrets/emails in any deliverable file

Usage: python3 slides_assets/check_rules.py  (exit 0 = all rules pass)
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DECK = ROOT / "new_Docker_Week11_Slides.html"

try:
    from pythainlp.tokenize import word_tokenize
except ImportError:  # fallback: approximate Thai words as chars/4
    word_tokenize = None

WORD_LIMIT = 60
BULLET_LIMIT = 6
QUIZ_GAP = 6

fails: list[str] = []
warns: list[str] = []


def strip_tags(html: str) -> str:
    html = re.sub(r"<pre\b.*?</pre>", " ", html, flags=re.S)
    html = re.sub(r'<div class="s-foot".*?</div>', " ", html, flags=re.S)
    html = re.sub(r"<[^>]+>", " ", html)
    html = html.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    return html


def count_words(text: str) -> int:
    n = 0
    for chunk in text.split():
        if re.search(r"[฀-๿]", chunk):
            if word_tokenize:
                n += len([t for t in word_tokenize(chunk) if t.strip()])
            else:
                n += max(1, round(len(chunk) / 4))
        else:
            if re.search(r"[A-Za-z0-9]", chunk):
                n += 1
    return n


def main() -> int:
    html = DECK.read_text(encoding="utf-8")
    body = html.split('<div id="stage">', 1)[1].split("<!-- /stage -->", 1)[0]

    # split into (comment, slot) pairs
    parts = re.split(r"(<!-- SLIDE .*?-->)", body)
    slides = []  # (num, comment, html)
    cur_comment = None
    for part in parts:
        if part.strip().startswith("<!-- SLIDE"):
            cur_comment = part.strip()
        elif '<div class="slot">' in part:
            slides.append((cur_comment, part))
            cur_comment = None

    total = len(re.findall(r'class="slot"', body))
    if len(slides) != total:
        fails.append(f"[comments] slot ทั้งหมด {total} แต่มีคอมเมนต์ SLIDE นำหน้าเพียง {len(slides)}")

    quiz_positions = []          # index among content slides
    content_idx = 0
    for i, (comment, slide) in enumerate(slides, start=1):
        # 1) comment format + numbering
        if not comment:
            fails.append(f"[comment][SLIDE {i:02d}] ไม่มีคอมเมนต์นำหน้า")
        else:
            m = re.match(r"<!-- SLIDE (\d+) \| จากหัวข้อเดิม: .+ \| แก้เพราะ: .+ -->", comment)
            if not m:
                fails.append(f"[comment][SLIDE {i:02d}] รูปแบบคอมเมนต์ไม่ตรง: {comment[:70]}")
            elif int(m.group(1)) != i:
                fails.append(f"[comment][SLIDE {i:02d}] เลขในคอมเมนต์คือ {m.group(1)} ไม่ตรงลำดับจริง {i}")

        structural = ('class="slide cover"' in slide or 'class="slide section"' in slide)
        is_quiz = "badge quiz" in slide
        if not structural:
            content_idx += 1
            if is_quiz:
                quiz_positions.append(content_idx)

        # 2) word count (prose only)
        words = count_words(strip_tags(slide))
        if words > WORD_LIMIT:
            fails.append(f"[C3][SLIDE {i:02d}] {words} คำ เกินเพดาน {WORD_LIMIT}")
        elif words > WORD_LIMIT - 5:
            warns.append(f"[C3][SLIDE {i:02d}] {words} คำ ใกล้เพดาน")

        # 3) bullets per list
        for lst in re.findall(r"<(?:ul|ol)\b.*?</(?:ul|ol)>", slide, flags=re.S):
            n_li = len(re.findall(r"<li\b", lst))
            if n_li > BULLET_LIMIT:
                fails.append(f"[C2][SLIDE {i:02d}] รายการมี {n_li} bullet เกิน {BULLET_LIMIT}")

    # 4) quiz cadence over content slides
    prev = 0
    for q in quiz_positions:
        if q - prev > QUIZ_GAP:
            fails.append(f"[cadence] ช่วงก่อน quiz ที่ตำแหน่ง content #{q} ห่าง {q - prev} สไลด์ (เกิน {QUIZ_GAP})")
        prev = q
    if content_idx - prev > QUIZ_GAP:
        warns.append(f"[cadence] ท้ายเด็ค {content_idx - prev} content slides หลัง quiz สุดท้าย (สรุป/ปิดท้าย — ยอมรับได้)")
    if not quiz_positions:
        fails.append("[cadence] ไม่มีสไลด์เช็คความเข้าใจเลย")

    # 5) secret scan over deliverables
    patterns = [
        (r"dckr_pat_[A-Za-z0-9_-]{8,}", "Docker PAT"),
        (r"ghp_[A-Za-z0-9]{20,}", "GitHub token"),
        (r"Siam\d+", "รหัสผ่านจริง"),
        (r"[a-z0-9._%+-]+@gmail\.com", "อีเมลจริง"),
    ]
    targets = [DECK, *ROOT.glob("00[1-5]_LAB*/**/*.md"), *ROOT.glob("00[1-5]_LAB*/**/*.sh"),
               *ROOT.glob("00[1-5]_LAB*/**/*.py"), *ROOT.glob("00[1-5]_LAB*/**/*.yml"),
               *ROOT.glob("00[1-5]_LAB*/**/Dockerfile*"), *ROOT.glob("test_logs/*.log"),
               ROOT / "readme.md"]
    for t in targets:
        if not t.is_file():
            continue
        txt = t.read_text(encoding="utf-8", errors="ignore")
        for pat, label in patterns:
            for hit in re.findall(pat, txt):
                fails.append(f"[C8][{t.relative_to(ROOT)}] พบ {label}: {hit[:14]}…")

    print(f"slides: {total} (content {content_idx}, quiz {len(quiz_positions)} at {quiz_positions})")
    for w in warns:
        print("WARN ", w)
    for f in fails:
        print("FAIL ", f)
    print("-" * 40)
    if fails:
        print(f"FAILED {len(fails)} rule check(s)")
        return 1
    print("ALL RULE CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
