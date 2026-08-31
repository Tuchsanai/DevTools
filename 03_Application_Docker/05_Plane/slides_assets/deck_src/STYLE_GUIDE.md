# Slide markup guide — Plane_Agile_Slides.html

The deck is assembled by `build_deck.py` from `00_head.html` (CSS) + every `[1-8]?_*.html` fragment (sorted by name) + `90_tail.html` (controls, overview, JS).
Each fragment is a sequence of **slots**. One slot = one slide, fixed **1280×720**. Nothing may overflow (check with `check_deck.py`).

```html
<!-- ===== N : short title ===== -->
<div class="slot" data-sec="3">            <!-- data-sec only on the FIRST slide of a ตอน (used by the overview page) -->
 <section class="slide">
  <div class="s-head"><div class="eyebrow">ตอนที่ 3 · Agile · Scrum</div><h2>Scrum <em>3 บทบาท · 5 อีเวนต์ · 3 อาร์ติแฟกต์</em></h2>
    <div class="sub">คำอธิบายใต้หัวเรื่อง 1 บรรทัด (ไม่บังคับ)</div></div>
  <div class="s-body">
     ... content ...
  </div>
  <div class="s-foot"><span>ตอนที่ 3 · Scrum</span><span class="pg"></span></div>   <!-- .pg is filled by JS -->
 </section>
</div>
```

## Slide kinds (class on `<section>`)
- `slide cover` — dark cover (only once). Uses `.k`, `h1`, `.rule`, `.m`, optional full-bleed `<img data-a="hero_cover">`.
- `slide section` — dark ตอน divider: `<div class="s-body"><div class="num-big">03</div><h1>ชื่อตอน</h1><div class="m">สรุป 1–2 ประโยค</div></div>`
- `slide` — normal light slide (head + body + foot).
- `slide figs` — "picture is the hero": smaller head, more room for `.fig`.
- `slide cmp` — two code panes side by side (`.g11` with `pre.code.xs`).

## Body layouts
- `.grid2 / .grid3 / .grid4` equal columns · `.g21` (1.25fr .75fr) · `.g12` · `.g11` two columns; add `mid` to vertically centre.
- `.s-body.top` = align content to the top (use when the slide is text-heavy).

## Components (all styled in 00_head.html)
- Cards: `<div class="card a|o|w|c|d"><h4><span class="n">1</span>Title</h4><p>text</p></div>` (a=accent blue, o=ok green, w=warn amber, c=critical red, d=muted).
- Bullets: `<ul class="bul"><li>ข้อความ<span class="s">คำอธิบายย่อย</span></li></ul>`; `ul.bul.sm` for smaller.
- Code: `<pre class="code sm">` / `xs` / `path` (no wrapping); colour spans `<span class="c">` comment, `k` keyword, `g` green, `y` yellow, `r` red, `d` dim. Escape `<` as `&lt;`.
- Table: `<table class="tbl sm"><thead><tr><th>..</th></tr></thead><tbody><tr><td>..</td></tr></tbody></table>` (`.tbl.xs` for dense).
- Note: `<div class="note a|o|w|c"><b>หัวข้อ</b> — ข้อความ</div>`; Quote: `<div class="quote">…<span class="who">— source</span></div>`.
- Tag: `<span class="tag a|o|w|c|d">LABEL</span>`; Stat: `<div class="stat"><div class="v">42</div><div class="l">label</div></div>`.
- Key/value: `<dl class="kv"><dt>key</dt><dd>value</dd></dl>`; Flow: `<div class="flow"><div class="b a"><div class="t">Step</div><div class="s">sub</div></div><span class="ar">→</span>…</div>`.
- Figure: `<div class="fig"><img data-a="d01" alt="…"></div>`; screenshot: `<div class="fig shot fix" style="height:430px"><img data-a="lab1:ui-home" alt="…"></div>`; caption `<div class="figcap">…</div>`; two figures: `<div class="figrow c11">…</div>`.
- Agenda (overview slide): `<div class="agenda"><div class="it" data-go="1"><div class="ix">01</div><div class="tt">ชื่อตอน<s>คำอธิบาย</s></div></div>…</div>` (`data-go` = ตอน number → JS jumps there).

## Assets (`<img data-a="KEY">`, embedded by build_deck.py)
- Excalidraw diagrams (`slides_assets/*.svg`): key = prefix before the first `-`: `d01`…`d14` (d01 scrum→plane, d02 kanban metrics, d03 lab architecture, d04 waterfall vs agile, d05 code of ethics, d06 work-item anatomy, d07 request path, d08 ER model, d09 API import flow, d10 dashboard flow, d11 jira/trello/plane terms, d12 celery/webhook flow, d13 roles, d14 first-run flow).
- Illustrations (`slides_assets/illustrations/*.svg`): key = file stem: `scrum_cycle`, `kanban_board`, `agile_manifesto`, `software_professional`, `sdlc_toolchain`, `jira_trello_plane`, `burndown_cfd`, `tracking_loop`, `hero_cover` (+ any added later).
- Screenshots: `slides_assets/screenshots/<stem>.png` → key `<stem>`; lab images `00N_LAB_*/images/<stem>.png` → key `labN:<stem>`.
- **Never depict Plane's UI with drawings — only real screenshots.** Illustrations are for concepts only.

## Rules that keep slides readable
- Thai body text ≥ 15.5px (cards), bullets 16–18px; at most ~7 bullets or ~2 code blocks per slide; split rather than shrink.
- A 1280×720 slide holds roughly: 1 head (2 lines) + 3 cards + 1 note, or a figure ≤ 430px tall + 3 bullets, or a 12-row `.tbl.sm`.
- Every ตอน starts with a `slide section` divider that carries `data-sec="N"` on its slot.
- Footer left text = `ตอนที่ N · topic`; keep `<span class="pg"></span>` in every foot.
- No external URLs in `src`/`href` of resources (CDN is forbidden); plain `<a>` links are fine but unnecessary.
- Validate: `python3 build_deck.py --only 20_topic1.html --out /tmp/x.html && python3 check_deck.py --deck /tmp/x.html --shots /tmp/xshots all` → must print `overflowing slides: none`, `broken images: none`, `js errors: none`; then look at a few PNGs.
