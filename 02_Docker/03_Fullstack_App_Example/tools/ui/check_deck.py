#!/usr/bin/env python3
"""ด่านตรวจเด็ค CampusOps — ความหนาแน่นต่อสไลด์ · โครงสร้าง · ความเป็นไฟล์เดียว · fidelity

ใช้: python3 tools/ui/check_deck.py            ตรวจทั้งหมด
     python3 tools/ui/check_deck.py --report   พิมพ์ตารางความหนาแน่นทุกหน้า (ไม่ตัดสิน)
     python3 tools/ui/check_deck.py --write-fidelity   บันทึก baseline คำสั่ง (ทำครั้งเดียว)
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import ConsoleMessage, sync_playwright

ROOT = Path(__file__).resolve().parents[2]
DECK = ROOT / "Fullstack_App_Example.html"
if "--deck" in sys.argv:
    DECK = Path(sys.argv[sys.argv.index("--deck") + 1]).resolve()
PARTS_DIR = ROOT / "deck_build"
FIDELITY = PARTS_DIR / "_baseline_fidelity.txt"

# ---- งบต่อสไลด์ (ตกลงในแผน v3 ข้อ 2) ----
MAX_PROSE = 800          # ตัวอักษร ~45 วินาทีของการอ่าน · ไม่นับข้อความใน <svg>, eyebrow, footer
MAX_CODE_LINES = 14      # รวมทุก <pre> ในสไลด์
MAX_TABLE_ROWS = 13      # รวมทุก <table> ในสไลด์
MIN_FONT_PX = 12.0       # ที่ฐานสไลด์ 1280px · ไม่นับข้อความใน <svg> (ต่ำกว่านี้ = ย่อฟอนต์เพื่อยัดเนื้อหา)
MAX_HEAVY = 1            # ของหนัก: svg diagram | รูป | pre>6 บรรทัด | table>4 แถว
MAX_HEAVY_CMP = 2        # สไลด์เปรียบเทียบ (class="slide cmp") ให้ได้ 2 ชิ้น ถ้าชนิดเดียวกันและชิ้นละ <= 8 บรรทัด
TOTAL_PROSE_BASELINE = 36409   # วัดจริงจากเด็ครุ่น 60 สไลด์ 21 ส.ค. 2026 — ห้ามพองเกิน +10%
MAX_DECK_MB = 4.0

PART_ORDER = [
    "s0_open.html", "s1_customer.html", "s2_require.html", "s3_design.html",
    "s4_lab1.html", "s5_lab2.html", "s6_lab3.html", "s7_lab4.html",
    "s8_lab5.html", "s9_summary.html",
]

MEASURE_JS = r"""() => {
  const sl = document.querySelector('.slot.active .slide');
  const clone = sl.cloneNode(true);
  clone.querySelectorAll('svg').forEach(e => e.remove());
  clone.querySelectorAll('.s-foot, .eyebrow').forEach(e => e.remove());
  const holder = document.createElement('div');
  holder.style.cssText = 'position:fixed;left:-99999px;top:0;width:1280px';
  holder.appendChild(clone);
  document.body.appendChild(holder);
  const prose = clone.innerText.replace(/\s+/g, ' ').trim().length;
  holder.remove();

  let codeLines = 0;
  sl.querySelectorAll('pre').forEach(p => {
    const cs = getComputedStyle(p);
    const lh = parseFloat(cs.lineHeight) || (parseFloat(cs.fontSize) * 1.5);
    const inner = p.getBoundingClientRect().height
                - parseFloat(cs.paddingTop) - parseFloat(cs.paddingBottom);
    codeLines += Math.max(p.innerText.split('\n').length, Math.round(inner / lh));
  });
  let tableRows = 0;
  sl.querySelectorAll('table').forEach(t => { tableRows += t.querySelectorAll('tr').length; });

  let minFont = 99, minFontText = '';
  sl.querySelectorAll('*').forEach(el => {
    if (el.closest('svg')) return;
    if (el.children.length) return;
    const t = (el.textContent || '').trim();
    if (!t) return;
    const f = parseFloat(getComputedStyle(el).fontSize);
    if (f < minFont) { minFont = f; minFontText = t.slice(0, 28); }
  });
  if (minFont === 99) minFont = 0;

  const heavyKinds = [];
  sl.querySelectorAll('svg[viewBox]').forEach(() => heavyKinds.push('svg'));
  sl.querySelectorAll('img').forEach(() => heavyKinds.push('img'));
  let maxPreLines = 0;
  sl.querySelectorAll('pre').forEach(p => {
    const n = p.innerText.split('\n').length;
    const cs2 = getComputedStyle(p);
    const lh2 = parseFloat(cs2.lineHeight) || (parseFloat(cs2.fontSize) * 1.5);
    const inner2 = p.getBoundingClientRect().height
                 - parseFloat(cs2.paddingTop) - parseFloat(cs2.paddingBottom);
    maxPreLines = Math.max(maxPreLines, n, Math.round(inner2 / lh2));
    if (n > 6) heavyKinds.push('pre');
  });
  sl.querySelectorAll('table').forEach(t => { if (t.querySelectorAll('tr').length > 4) heavyKinds.push('table'); });
  const heavy = heavyKinds.length;

  let minSvgFont = 99;
  sl.querySelectorAll('svg text').forEach(t => {
    const f = parseFloat(getComputedStyle(t).fontSize);
    if (f && f < minSvgFont) minSvgFont = f;
  });
  if (minSvgFont === 99) minSvgFont = 0;

  const body = sl.querySelector('.s-body');
  const bodyOverflow = body ? body.scrollHeight - body.clientHeight : 0;
  const sr = sl.getBoundingClientRect();
  /* ล้นออกนอกกรอบสไลด์ — ต้องดูทั้งสี่ด้าน เพราะ flex centering ดันเนื้อหาออกด้านบนได้
     โดย scrollHeight ไม่รายงาน (ปัญหา lost content ของ flexbox) */
  let spill = 0, spillEl = '';
  sl.querySelectorAll('.s-head *, .s-body *').forEach(el => {
    const r = el.getBoundingClientRect();
    if (!r.height || !r.width) return;
    const over = Math.max(sr.top - r.top, r.bottom - (sr.bottom - 38),
                          sr.left - r.left, r.right - sr.right);
    if (over > spill) { spill = over; spillEl = (el.className || el.tagName) + ' :: ' + (el.textContent || '').trim().slice(0, 24); }
  });

  const h = sl.querySelector('h1, h2');
  const eb = sl.querySelector('.eyebrow');
  return {
    prose, codeLines, tableRows, minFont, minFontText, heavy, heavyKinds, maxPreLines, minSvgFont,
    bodyOverflow, spill: Math.round(spill), spillEl,
    cls: sl.className,
    title: h ? h.innerText.replace(/\s+/g, ' ').trim() : '',
    eyebrow: eb ? eb.innerText.replace(/\s+/g, ' ').trim() : '',
    hasPg: !!sl.querySelector('.s-foot .pg'),
    videos: sl.querySelectorAll('video').length,
  };
}"""


def slide_to_part() -> list[str]:
    """คืนรายชื่อไฟล์ part ของสไลด์แต่ละหน้า ตามลำดับในเด็ค."""
    mapping: list[str] = []
    for name in PART_ORDER:
        path = PARTS_DIR / name
        if not path.exists():
            continue
        n = path.read_text(encoding="utf-8").count('<div class="slot"')
        mapping.extend([name] * n)
    return mapping


CMD_RE = re.compile(r"^\s*(?:\$\s*)?(docker|git|curl|psql|npm|npx|python3|bash|sh|ls|cat|wget|ssh|tar)\b")


def commands_in(html: str) -> set[str]:
    out: set[str] = set()
    for pre in re.findall(r"<pre[^>]*>(.*?)</pre>", html, flags=re.S):
        text = re.sub(r"<[^>]+>", "", pre)
        text = (text.replace("&lt;", "<").replace("&gt;", ">")
                    .replace("&quot;", '"').replace("&#39;", "'").replace("&amp;", "&"))
        for line in text.splitlines():
            if CMD_RE.match(line):
                out.add(re.sub(r"\s+", " ", line).strip())
    return out


def check_fidelity(failures: list[str]) -> None:
    if not FIDELITY.exists():
        failures.append("ไม่พบ baseline fidelity — รัน --write-fidelity ก่อน")
        return
    allowed = {l.strip() for l in FIDELITY.read_text(encoding="utf-8").splitlines() if l.strip()}
    for lab in sorted(ROOT.glob("00*_LAB_*/readme.md")):
        body = lab.read_text(encoding="utf-8")
        for line in body.splitlines():
            if CMD_RE.match(line):
                allowed.add(re.sub(r"\s+", " ", line).strip())
    now = commands_in(DECK.read_text(encoding="utf-8"))
    invented = sorted(c for c in now if c not in allowed)
    if invented:
        failures.append(f"พบคำสั่งที่ไม่มีในเด็คเดิมหรือใน readme ของแล็บ {len(invented)} บรรทัด")
        for c in invented[:12]:
            failures.append(f"    · {c}")


POINTER_RE = re.compile(
    r"\b((?:00\d_LAB_[A-Za-z_]+/|docs/)?[A-Za-z0-9_.\-]+\.md)(?:\s*·\s*(การทดลองที่\s*[\d\s·–\-]+))?")


SIZE_RE = re.compile(r"\b\d+(?:\.\d+)?\s?(?:GB|MB|kB|KB)\b")


def corpus() -> str:
    """ข้อความจากทุกไฟล์ที่ถือเป็นแหล่งความจริงของตัวเลข."""
    parts = [(ROOT / "readme.md").read_text(encoding="utf-8")]
    for f in sorted(ROOT.glob("00?_LAB_*/readme.md")):
        parts.append(f.read_text(encoding="utf-8"))
    for f in sorted(ROOT.glob("docs/*.md")):
        parts.append(f.read_text(encoding="utf-8"))
    for f in sorted(ROOT.glob("00?_LAB_*/images/*.svg")):
        parts.append(f.read_text(encoding="utf-8"))
    return "\n".join(parts)


def check_stale_sizes(failures: list[str]) -> None:
    """ตัวเลขขนาดในเด็คต้องหาเจอในแล็บ/เอกสาร — กันเลขค้างจากการรันรอบเก่า."""
    html = DECK.read_text(encoding="utf-8")
    text = re.sub(r"<[^>]+>", " ", re.sub(r"data:image/[^\"\']+", "", html))
    src = corpus()
    src_norm = re.sub(r"\s+", "", src)
    seen: set[str] = set()
    for m in SIZE_RE.finditer(text):
        tok = m.group(0)
        if tok in seen:
            continue
        seen.add(tok)
        if re.sub(r"\s+", "", tok) not in src_norm:
            ctx = re.sub(r"\s+", " ", text[max(0, m.start() - 45):m.end() + 25]).strip()
            failures.append(f"เด็คมีตัวเลขขนาด \"{tok}\" ที่ไม่พบในแล็บหรือเอกสารเลย — \"{ctx}\"")


def check_pointers(failures: list[str]) -> None:
    html = DECK.read_text(encoding="utf-8")
    text = re.sub(r"<[^>]+>", " ", re.sub(r"data:image/[^\"']+", "", html))
    for path, heading in sorted(set(POINTER_RE.findall(text))):
        target = ROOT / path
        if not target.exists():
            failures.append(f"pointer ชี้ไปไฟล์ที่ไม่มีอยู่: {path}")
            continue
        if heading:
            body = target.read_text(encoding="utf-8")
            for n in re.findall(r"\d+", heading):
                if not re.search(rf"^#+ .*การทดลองที่ {n}\b", body, flags=re.M):
                    failures.append(f"pointer {path} · การทดลองที่ {n} — ไม่พบหัวข้อนี้ในไฟล์")


def main() -> int:
    argv = sys.argv[1:]
    if "--write-fidelity" in argv:
        cmds = commands_in(DECK.read_text(encoding="utf-8"))
        FIDELITY.write_text("\n".join(sorted(cmds)) + "\n", encoding="utf-8")
        print(f"[OK] บันทึก baseline คำสั่ง {len(cmds)} บรรทัด -> {FIDELITY}")
        return 0
    report_only = "--report" in argv
    strict_tags = "--tags" in argv
    only = None
    if "--only" in argv:
        only = argv[argv.index("--only") + 1]

    failures: list[str] = []
    console_errors: list[str] = []
    page_errors: list[str] = []
    requests: list[str] = []
    rows: list[dict] = []

    size_mb = DECK.stat().st_size / 1024 / 1024
    if size_mb > MAX_DECK_MB:
        failures.append(f"ขนาดเด็ค {size_mb:.2f} MB เกิน {MAX_DECK_MB} MB")

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: page_errors.append(str(e)))
        page.on("request", lambda r: requests.append(r.url))
        page.goto(DECK.as_uri() + "#1", wait_until="load")
        page.wait_for_function(
            "Array.from(document.querySelectorAll('img[data-a]')).every(i => i.complete && i.naturalWidth > 0)"
        )
        total = page.evaluate("document.querySelectorAll('.slot').length")
        media = page.evaluate(r"""() => {
            const A = window.ASSETS || {};
            return Array.from(document.querySelectorAll('video, audio')).map(m => {
              const k = m.getAttribute('data-v') || '';
              return {
                key: k,
                src: (m.getAttribute('src') || '').slice(0, 24),
                assetOk: typeof A[k] === 'string' && A[k].startsWith('data:video/'),
                posterOk: (m.poster || '').startsWith('data:image/'),
                fallback: !!(m.parentNode && m.parentNode.querySelector('img.vposter')),
                err: m.error ? m.error.code : 0,
              };
            });
        }""")
        for i, m in enumerate(media):
            tag = m["key"] or f"ตัวที่ {i+1}"
            if not (m["src"].startswith("data:") or m["assetOk"]):
                failures.append(f"วิดีโอ {tag} ไม่ได้ฝังเป็น data URI")
            if m["err"]:
                failures.append(f"วิดีโอ {tag} decode ไม่ผ่าน (error {m['err']})")
            if not m["posterOk"]:
                failures.append(f"วิดีโอ {tag} ไม่มี poster เป็น data URI")
            if not m["fallback"]:
                failures.append(f"วิดีโอ {tag} ไม่มี <img class=\"vposter\"> สำรองสำหรับตอนพิมพ์")
        ext_attr = page.evaluate(r"""() => Array.from(
            document.querySelectorAll('script[src],link[href],iframe[src],img[src],video[src],source[src],audio[src]'))
            .map(e => e.getAttribute('src') || e.getAttribute('href'))
            .filter(v => v && /^(?:https?:)?\/\//i.test(v))""")
        if ext_attr:
            failures.append(f"พบ attribute ที่ชี้ออกนอกไฟล์: {ext_attr[:3]}")
        broken = page.evaluate("Array.from(document.images).filter(i => !i.complete || !i.naturalWidth).length")
        if broken:
            failures.append(f"ภาพ render ไม่สำเร็จ {broken} ใบ")

        page.keyboard.press("Home")
        for i in range(1, total + 1):
            if i > 1:
                page.keyboard.press("ArrowRight")
            r = page.evaluate(MEASURE_JS)
            r["page"] = i
            rows.append(r)
        browser.close()

    parts = slide_to_part()
    if parts and len(parts) != len(rows):
        failures.append(f"จำนวนสไลด์ในเด็ค {len(rows)} ไม่ตรงกับไฟล์ part {len(parts)}")
        parts = []

    if report_only:
        print(f"{'pg':>3} {'part':<16} {'prose':>5} {'code':>4} {'row':>4} {'font':>5} {'hv':>2} {'ov':>3}  title")
    over = 0
    for r in rows:
        part = parts[r["page"] - 1] if parts else "-"
        light = "cover" in r["cls"] or "section" in r["cls"]
        bad: list[str] = []
        if not light:
            if r["prose"] > MAX_PROSE:
                bad.append(f"prose {r['prose']}>{MAX_PROSE}")
            if r["codeLines"] > MAX_CODE_LINES:
                bad.append(f"code {r['codeLines']}>{MAX_CODE_LINES}")
            if r["tableRows"] > MAX_TABLE_ROWS:
                bad.append(f"table {r['tableRows']}>{MAX_TABLE_ROWS}")
            if r["minFont"] and r["minFont"] < MIN_FONT_PX:
                bad.append(f"font {r['minFont']}<{MIN_FONT_PX} ที่ \"{r['minFontText']}\"")
            cmp_ok = ("cmp" in r["cls"] and r["heavy"] <= MAX_HEAVY_CMP
                      and len(set(r["heavyKinds"])) == 1 and r["maxPreLines"] <= 8)
            if r["heavy"] > MAX_HEAVY and not cmp_ok:
                kinds = "+".join(r["heavyKinds"])
                hint = " (ใส่ class=\"slide cmp\" ได้ถ้าเป็นการเปรียบเทียบชนิดเดียวกัน ชิ้นละ <= 8 บรรทัด)" if len(set(r["heavyKinds"])) == 1 else ""
                bad.append(f"ของหนัก {r['heavy']}>{MAX_HEAVY} [{kinds}]{hint}")
        if r["bodyOverflow"] > 1 or r["spill"] > 1:
            bad.append(f"ล้นกรอบ {r['spill']}px [{r.get('spillEl','')}]")
        if not r["hasPg"]:
            bad.append("ไม่มี <span class=\"pg\">")
        if strict_tags and not light and part != "s0_open.html":
            eb = r["eyebrow"]
            if not re.match(r"ตอนที่ \d+ ·", eb):
                bad.append(f"eyebrow ไม่ขึ้นต้นด้วย 'ตอนที่ N ·' : {eb[:40]!r}")
            elif not any(t in eb for t in ("ทฤษฎี", "ลงมือ", "หลักฐาน")):
                bad.append(f"eyebrow ไม่มีป้าย ทฤษฎี/ลงมือ/หลักฐาน : {eb[:40]!r}")
        if report_only:
            flag = "  << " + " · ".join(bad) if bad else ""
            print(f"{r['page']:>3} {part:<16} {r['prose']:>5} {r['codeLines']:>4} {r['tableRows']:>4} "
                  f"{r['minFont']:>5.1f} {r['heavy']:>2} {r['bodyOverflow']:>3}  {r['title'][:44]}{flag}")
        elif bad and (only is None or part == only):
            over += 1
            failures.append(f"หน้า {r['page']} [{part}] {r['title'][:44]} — " + " · ".join(bad))

    total_prose = sum(r["prose"] for r in rows)
    if total_prose > TOTAL_PROSE_BASELINE * 1.10:
        failures.append(f"ตัวอักษรรวมทั้งเด็ค {total_prose} เกิน baseline {TOTAL_PROSE_BASELINE} เกิน 10% "
                        f"— รอบนี้คือย้ายรายละเอียด ไม่ใช่เพิ่มเนื้อหา")

    external = [u for u in requests
                if urlparse(u).scheme not in {"file", "data", "blob", "about"}
                and urlparse(u).hostname not in {"localhost", "127.0.0.1", "::1"}]
    if external:
        failures.append(f"request ออกนอกเครื่อง {len(external)} รายการ: {external[:3]}")
    if console_errors:
        failures.append(f"console error {len(console_errors)}: {console_errors[:3]}")
    if page_errors:
        failures.append(f"page error {len(page_errors)}: {page_errors[:3]}")

    check_pointers(failures)
    check_fidelity(failures)
    check_stale_sizes(failures)

    json.dump(rows, open(PARTS_DIR / "_last_report.json", "w"), ensure_ascii=False, indent=1)

    if report_only:
        small_svg = [r["page"] for r in rows if 0 < r["minSvgFont"] < 12]
        print(f"\nสไลด์ {len(rows)} หน้า · ขนาด {size_mb:.2f} MB · ตัวอักษรรวม {total_prose} "
              f"(baseline {TOTAL_PROSE_BASELINE})")
        if small_svg:
            print(f"[เตือน · ไม่บล็อก] ป้ายใน SVG เล็กกว่า 12px ที่หน้า {small_svg}")
        return 0
    if failures:
        print(f"[FAIL] {len(failures)} รายการ · สไลด์เกินงบ {over} หน้า")
        for f in failures:
            print(f"  {f}")
        return 1
    print(f"[PASS] สไลด์ {len(rows)} หน้า · ทุกหน้าอยู่ในงบ · ขนาด {size_mb:.2f} MB · ตัวอักษรรวม {total_prose}")
    print(f"[PASS] request ภายนอก 0 · console error 0 · pointer/fidelity ผ่าน")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
