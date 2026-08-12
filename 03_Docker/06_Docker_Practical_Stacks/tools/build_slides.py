#!/usr/bin/env python3
"""Build three self-contained 1280x720 HTML decks from Python slide data.

The HTML is the source-of-truth presentation format. SVG and PNG assets are
embedded so each generated deck can be opened without a web server or network.
"""

from __future__ import annotations

import base64
import html
import importlib.util
import mimetypes
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "slides" / "source"


DECKS = [
    ("part1.py", "Docker_Part1_Easy.html"),
    ("part2.py", "Docker_Part2_Intermediate.html"),
    ("part3.py", "Docker_Part3_Advanced.html"),
]


def load_source(filename: str):
    path = SOURCE / filename
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def rich(value: Any) -> str:
    """Render deliberately small Markdown subset used by slide source."""
    text = html.escape(str(value), quote=False)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    return text.replace("\n", "<br>")


def asset_markup(relative: str, alt: str) -> str:
    path = ROOT / relative
    if not path.exists():
        return (
            '<div class="asset-missing"><b>Asset pending</b><br>'
            f"{html.escape(relative)}</div>"
        )
    if path.suffix.lower() == ".svg":
        svg = path.read_text(encoding="utf-8")
        svg = re.sub(r"<\?xml[^>]*>\s*", "", svg, count=1)
        return f'<div class="svg-wrap" role="img" aria-label="{html.escape(alt)}">{svg}</div>'
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f'<img src="data:{mime};base64,{encoded}" alt="{html.escape(alt)}">'


def footer(course: str, part: str) -> str:
    return (
        '<div class="s-foot"><span>'
        f"{html.escape(course)} · {html.escape(part)}"
        '</span><span class="pg"></span></div>'
    )


def header(slide: dict[str, Any]) -> str:
    badge = slide.get("badge")
    badge_html = f'<span class="badge">{rich(badge)}</span>' if badge else ""
    subtitle = slide.get("subtitle")
    subtitle_html = f'<div class="sub">{rich(subtitle)}</div>' if subtitle else ""
    return (
        '<div class="s-head">'
        f"{badge_html}<h2>{rich(slide['title'])}</h2>{subtitle_html}"
        "</div>"
    )


def note_markup(slide: dict[str, Any]) -> str:
    note = slide.get("note")
    if not note:
        return ""
    tone = html.escape(slide.get("note_tone", "info"))
    return f'<div class="callout {tone}">{rich(note)}</div>'


def render_slide(slide: dict[str, Any], meta: dict[str, str]) -> str:
    kind = slide["type"]
    course = meta["course"]
    part = meta["part"]

    if kind == "cover":
        return f'''<div class="slot"><section class="slide cover">
  <div class="s-body"><div class="k">{rich(slide.get('kicker', part))}</div>
  <h1>{rich(slide['title'])}</h1><div class="rule"></div>
  <div class="m">{rich(slide.get('subtitle', ''))}</div></div>
  {footer(course, part)}</section></div>'''

    if kind == "section":
        return f'''<div class="slot"><section class="slide section">
  <div class="s-body"><div class="num">{rich(slide.get('number', ''))}</div>
  <h1>{rich(slide['title'])}</h1><div class="m">{rich(slide.get('subtitle', ''))}</div></div>
  {footer(course, part)}</section></div>'''

    if kind == "bullets":
        items = "".join(f"<li>{rich(item)}</li>" for item in slide["bullets"])
        body = f'<ul class="bul">{items}</ul>{note_markup(slide)}'

    elif kind == "cards":
        cards = []
        for card in slide["cards"]:
            tone = html.escape(card.get("tone", "blue"))
            cards.append(
                f'<div class="card {tone}"><h4>{rich(card["title"])}</h4>'
                f'<p>{rich(card["text"])}</p></div>'
            )
        cols = int(slide.get("columns", min(3, len(cards))))
        body = f'<div class="cards cols-{cols}">{"".join(cards)}</div>{note_markup(slide)}'

    elif kind == "code":
        code = html.escape(slide["code"], quote=False)
        output = slide.get("output")
        if output is not None:
            out = html.escape(output, quote=False)
            body = (
                '<div class="code-grid">'
                f'<div><div class="terminal-label">COMMAND</div><pre class="code">{code}</pre></div>'
                f'<div><div class="terminal-label output-label">EXPECTED</div><pre class="code output">{out}</pre></div>'
                f'</div>{note_markup(slide)}'
            )
        else:
            body = f'<pre class="code solo">{code}</pre>{note_markup(slide)}'

    elif kind == "table":
        columns = "".join(f"<th>{rich(c)}</th>" for c in slide["columns"])
        rows = "".join(
            "<tr>" + "".join(f"<td>{rich(cell)}</td>" for cell in row) + "</tr>"
            for row in slide["rows"]
        )
        body = f'<div class="table-wrap"><table><thead><tr>{columns}</tr></thead><tbody>{rows}</tbody></table></div>{note_markup(slide)}'

    elif kind == "diagram":
        figure = asset_markup(slide["asset"], slide.get("alt", slide["title"]))
        caption = f'<figcaption>{rich(slide["caption"])}</figcaption>' if slide.get("caption") else ""
        body = f'<figure>{figure}{caption}</figure>{note_markup(slide)}'

    elif kind == "quiz":
        options = "".join(
            f'<div class="quiz-option"><span>{chr(65 + index)}</span>{rich(option)}</div>'
            for index, option in enumerate(slide["options"])
        )
        answer = rich(slide["answer"])
        body = (
            f'<div class="quiz-prompt">{rich(slide["prompt"])}</div>'
            f'<div class="quiz-options">{options}</div>'
            f'<details><summary>เฉลยและเหตุผล</summary><div>{answer}</div></details>'
        )

    elif kind == "lab":
        goals = "".join(f"<li>{rich(item)}</li>" for item in slide["goals"])
        evidence = "".join(f"<li>{rich(item)}</li>" for item in slide["evidence"])
        body = f'''<div class="lab-grid">
          <div class="mission"><div class="lab-folder">{rich(slide['folder'])}</div>
          <h3>Mission</h3><ul>{goals}</ul></div>
          <div class="evidence"><h3>หลักฐานก่อนผ่าน</h3><ul>{evidence}</ul></div>
        </div>{note_markup(slide)}'''

    else:
        raise ValueError(f"Unknown slide type: {kind}")

    return f'''<div class="slot"><section class="slide">
  {header(slide)}<div class="s-body">{body}</div>
  {footer(course, part)}</section></div>'''


CSS = r'''
:root{--blue:#1864ab;--blue2:#1971c2;--sky:#e7f5ff;--orange:#e8590c;--orange2:#fff4e6;--green:#2f9e44;--green2:#ebfbee;--red:#c92a2a;--red2:#fff5f5;--purple:#6741d9;--purple2:#f3f0ff;--ink:#16212f;--muted:#5b6b7f;--line:#dfe5ec;--code:#0d1626;--s:1;--ovs:.25}
*{box-sizing:border-box;margin:0;padding:0}html,body{height:100%}body{background:#11151c;overflow:hidden;font-family:"Leelawadee UI","Noto Sans Thai",Sarabun,"Segoe UI",system-ui,sans-serif;color:var(--ink);-webkit-font-smoothing:antialiased}code,kbd,.mono{font-family:"Cascadia Code","JetBrains Mono",Consolas,monospace}code{background:#edf2f7;color:#c92a2a;border-radius:5px;padding:.05em .28em;font-size:.92em}#stage{position:fixed;inset:0}.slot{position:absolute;left:50%;top:50%;width:1280px;height:720px;margin-left:-640px;margin-top:-360px;transform:scale(var(--s));display:none}.slot.active{display:block}.slide{width:1280px;height:720px;background:#fff;position:relative;overflow:hidden;display:flex;flex-direction:column;box-shadow:0 20px 60px rgba(0,0,0,.5)}
.s-head{padding:30px 56px 0;flex:0 0 auto}.s-head .badge{display:inline-block;font-size:14px;font-weight:800;letter-spacing:.12em;text-transform:uppercase;color:#fff;background:var(--orange);padding:4px 13px;border-radius:5px;margin-bottom:10px}.s-head h2{font-size:38px;line-height:1.18;font-weight:800;color:var(--blue);border-left:8px solid var(--orange);padding-left:18px;letter-spacing:-.01em}.s-head .sub{font-size:19px;color:var(--muted);padding-left:27px;margin-top:7px}.s-body{flex:1;min-height:0;padding:22px 56px 56px;display:flex;flex-direction:column;justify-content:center}.s-foot{position:absolute;left:0;right:0;bottom:0;height:39px;padding:0 56px;display:flex;align-items:center;justify-content:space-between;font-size:13px;color:#8b99a9;border-top:1px solid var(--line)}.s-foot .pg{font-weight:800;color:var(--blue)}
.slide.cover,.slide.section{background:linear-gradient(135deg,#0b2545 0%,#134074 55%,#1864ab 100%);color:#fff;justify-content:center}.cover .s-body,.section .s-body{padding:0 86px}.cover .k{font-size:18px;letter-spacing:.2em;text-transform:uppercase;color:#8ec5ff;font-weight:800;margin-bottom:18px}.cover h1{font-size:62px;line-height:1.12;font-weight:900;letter-spacing:-.02em;max-width:1060px}.cover .rule{width:120px;height:6px;background:#ffa94d;border-radius:3px;margin:27px 0}.cover .m{font-size:23px;color:#c7dcf5;line-height:1.55;max-width:1040px}.section .num{font-size:120px;font-weight:900;color:rgba(255,255,255,.16);line-height:1}.section h1{font-size:54px;font-weight:900;margin-top:-16px}.section .m{font-size:22px;color:#c7dcf5;margin-top:18px;line-height:1.55;max-width:900px}.cover .s-foot,.section .s-foot{border-color:rgba(255,255,255,.15);color:#8ea9c6}.cover .s-foot .pg,.section .s-foot .pg{color:#ffa94d}
.bul{list-style:none;font-size:23px;line-height:1.5}.bul li{position:relative;padding-left:36px;margin:11px 0}.bul li:before{content:"▸";position:absolute;left:6px;color:var(--orange);font-weight:900}.bul strong{color:var(--blue)}.cards{display:grid;gap:18px}.cols-2{grid-template-columns:repeat(2,1fr)}.cols-3{grid-template-columns:repeat(3,1fr)}.cols-4{grid-template-columns:repeat(4,1fr)}.card{border:2px solid var(--blue2);background:var(--sky);border-radius:13px;padding:18px 20px;min-height:130px}.card h4{font-size:21px;color:var(--blue);margin-bottom:8px}.card p{font-size:17.5px;line-height:1.52;color:#33475e}.card.orange{border-color:var(--orange);background:var(--orange2)}.card.orange h4{color:var(--orange)}.card.green{border-color:var(--green);background:var(--green2)}.card.green h4{color:var(--green)}.card.red{border-color:var(--red);background:var(--red2)}.card.red h4{color:var(--red)}.card.purple{border-color:var(--purple);background:var(--purple2)}.card.purple h4{color:var(--purple)}
.callout{margin-top:16px;border-left:7px solid var(--blue);background:var(--sky);border-radius:8px;padding:13px 17px;font-size:18px;line-height:1.45}.callout.warn{border-color:var(--orange);background:#fff9db}.callout.good{border-color:var(--green);background:var(--green2)}.callout.bad{border-color:var(--red);background:var(--red2)}.code-grid{display:grid;grid-template-columns:1fr 1fr;gap:18px;align-items:stretch}.terminal-label{display:inline-block;background:#364152;color:#fff;border-radius:7px 7px 0 0;padding:5px 12px;font-size:13px;font-weight:800;letter-spacing:.1em}.output-label{background:var(--green)}pre.code{margin:0;background:var(--code);color:#dbe6f5;border-radius:0 11px 11px 11px;padding:17px 19px;font:16px/1.42 "Cascadia Code",Consolas,monospace;white-space:pre-wrap;overflow:hidden;min-height:250px}pre.code.output{background:#10251a;color:#d8f5e0}.code.solo{border-radius:11px;min-height:auto;font-size:18px}.table-wrap{border:1px solid var(--line);border-radius:11px;overflow:hidden}table{width:100%;border-collapse:collapse;font-size:17px}th{background:var(--blue);color:#fff;text-align:left;padding:11px 13px}td{padding:10px 13px;border-top:1px solid var(--line);line-height:1.35}tbody tr:nth-child(even){background:#f8fafc}td code{font-size:.86em}
figure{height:100%;min-height:0;display:flex;flex-direction:column;align-items:center;justify-content:center}figure img,.svg-wrap{display:flex;align-items:center;justify-content:center;max-width:100%;max-height:460px}.svg-wrap svg{width:100%;height:100%;max-height:450px}.svg-wrap text{font-family:"Noto Sans Thai","Segoe UI",sans-serif}figcaption{font-size:16px;color:var(--muted);margin-top:8px}.asset-missing{width:760px;height:330px;border:3px dashed #adb5bd;background:#f8f9fa;border-radius:15px;display:flex;flex-direction:column;align-items:center;justify-content:center;color:#687787;font-size:20px}
.quiz-prompt{font-size:28px;font-weight:800;color:var(--blue);line-height:1.35;margin-bottom:18px}.quiz-options{display:grid;grid-template-columns:1fr 1fr;gap:12px}.quiz-option{border:2px solid var(--line);border-radius:10px;padding:13px 16px;font-size:19px;background:#f8fafc}.quiz-option span{display:inline-grid;place-items:center;width:30px;height:30px;background:var(--blue);color:#fff;border-radius:50%;font-weight:800;margin-right:10px}details{margin-top:16px;border:2px solid var(--green);background:var(--green2);border-radius:10px;padding:12px 16px;font-size:18px}details summary{font-weight:800;color:var(--green);cursor:pointer}.lab-grid{display:grid;grid-template-columns:1fr 1fr;gap:20px}.mission,.evidence{border:2px solid var(--orange);background:var(--orange2);border-radius:14px;padding:19px 22px}.evidence{border-color:var(--green);background:var(--green2)}.lab-grid h3{font-size:24px;color:var(--orange);margin:8px 0 10px}.evidence h3{color:var(--green)}.lab-grid ul{padding-left:24px;font-size:18px;line-height:1.48}.lab-grid li{margin:7px 0}.lab-folder{font:15px "Cascadia Code",monospace;color:#fff;background:#9a5030;display:inline-block;border-radius:5px;padding:6px 10px}
#overview{display:none;position:fixed;inset:0;overflow:auto;background:#0d1117;padding:25px}.overview #stage{position:static;display:grid;grid-template-columns:repeat(4,320px);gap:18px;align-items:start}.overview .slot{display:block;position:relative;left:auto;top:auto;margin:0;width:1280px;height:720px;transform:scale(var(--ovs));transform-origin:top left;margin-right:-960px;margin-bottom:-540px;cursor:pointer}.overview #overview{display:block}.navhelp{position:fixed;right:14px;bottom:10px;color:#ced4da;background:rgba(0,0,0,.5);padding:5px 9px;border-radius:5px;font-size:12px;z-index:20}
@page{size:13.333333in 7.5in;margin:0}@media print{html,body{height:auto;background:#fff;overflow:visible}.navhelp,#overview{display:none!important}#stage{position:static}.slot{display:block!important;position:relative;left:auto;top:auto;margin:0;transform:none!important;page-break-after:always;break-after:page}.slide{box-shadow:none}.slot:last-child{page-break-after:auto;break-after:auto}}
'''


JS = r'''
(() => {
  const slots=[...document.querySelectorAll('.slot')]; let current=0;
  const clamp=n=>Math.max(0,Math.min(slots.length-1,n));
  function scale(){if(document.body.classList.contains('overview'))return;const s=Math.min(innerWidth/1280,innerHeight/720);document.documentElement.style.setProperty('--s',s)}
  function show(n,push=true){current=clamp(n);slots.forEach((s,i)=>s.classList.toggle('active',i===current));document.querySelectorAll('.pg').forEach((p,i)=>p.textContent=`${i+1} / ${slots.length}`);if(push)history.replaceState(null,'',`#${current+1}`)}
  function overview(){document.body.classList.toggle('overview');if(document.body.classList.contains('overview'))slots.forEach(s=>s.classList.remove('active'));else show(current,false)}
  addEventListener('keydown',e=>{if(['ArrowRight','PageDown',' '].includes(e.key)){e.preventDefault();show(current+1)}if(['ArrowLeft','PageUp'].includes(e.key)){e.preventDefault();show(current-1)}if(e.key==='Home')show(0);if(e.key==='End')show(slots.length-1);if(e.key.toLowerCase()==='o')overview();if(e.key.toLowerCase()==='f')document.documentElement.requestFullscreen?.()});
  addEventListener('resize',scale);addEventListener('hashchange',()=>show((parseInt(location.hash.slice(1))||1)-1,false));slots.forEach((s,i)=>s.addEventListener('click',()=>{if(document.body.classList.contains('overview')){document.body.classList.remove('overview');show(i)}}));
  window.__SLIDE_COUNT__=slots.length;scale();show((parseInt(location.hash.slice(1))||1)-1,false);
})();
'''


def build_deck(source_name: str, output_name: str) -> Path:
    source = load_source(source_name)
    meta = source.META
    rendered = "\n".join(render_slide(slide, meta) for slide in source.SLIDES)
    document = f'''<!doctype html>
<html lang="th"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(meta['title'])}</title><style>{CSS}</style></head>
<body><main id="stage">{rendered}</main><div id="overview"></div>
<div class="navhelp">← → เปลี่ยนหน้า · O ภาพรวม · F เต็มจอ</div>
<script>{JS}</script></body></html>'''
    output = ROOT / output_name
    output.write_text(document, encoding="utf-8")
    return output


def main() -> None:
    for source_name, output_name in DECKS:
        output = build_deck(source_name, output_name)
        print(f"built {output.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

