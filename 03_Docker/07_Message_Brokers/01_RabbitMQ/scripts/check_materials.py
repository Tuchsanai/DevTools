#!/usr/bin/env python3
"""Run deterministic, offline checks for the RabbitMQ teaching materials."""

from __future__ import annotations

import ast
import base64
import binascii
import html as html_module
import json
import re
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
SLIDES = ROOT / "RabbitMQ_Slides.html"
ROOT_README = ROOT / "readme.md"
PINNED_RABBITMQ_IMAGE = "rabbitmq:4.3.4-management"

EXPECTED_LABS: dict[str, set[str]] = {
    "001_LAB_RabbitMQ_Setup": {"send.py", "receive.py"},
    "002_LAB_Work_Queue": {"new_task.py", "worker.py"},
    "003_LAB_Publish_Subscribe": {
        "emit_log.py",
        "receive_logs.py",
        "emit_log_durable.py",
        "receive_logs_durable.py",
    },
    "004_LAB_Topic_Routing": {
        "emit_log_direct.py",
        "receive_logs_direct.py",
        "emit_log_topic.py",
        "receive_logs_topic.py",
        "unroutable_demo.py",
    },
}

REQUIRED_LAB_HEADINGS = (
    "สิ่งที่จะได้เรียนรู้",
    "ภาพรวมของแล็บนี้",
    "ทดลองเพิ่มเติม",
    "แก้ปัญหาที่พบบ่อย",
    "เก็บกวาด (Cleanup)",
    "เช็กลิสต์ก่อนจบแล็บ",
)

VOID_HTML_TAGS = {
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "param",
    "source",
    "track",
    "wbr",
}

MARKDOWN_LINK_RE = re.compile(
    r"!?\[[^\]]*\]\(\s*(?:<([^>]+)>|([^\s)]+))", re.MULTILINE
)
FENCED_CODE_RE = re.compile(r"^```([^\n]*)\n(.*?)^```\s*$", re.MULTILINE | re.DOTALL)
RABBITMQ_IMAGE_RE = re.compile(r"\brabbitmq:[A-Za-z0-9][A-Za-z0-9._-]*")


class DeckHTMLParser(HTMLParser):
    """Collect deck structure and report explicit tag nesting mistakes."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[str] = []
        self.errors: list[str] = []
        self.ids: Counter[str] = Counter()
        self.slots = 0
        self.slides = 0
        self.asset_refs: list[str] = []
        self.images: list[dict[str, str]] = []
        self.buttons: list[dict[str, str]] = []
        self.resource_attributes: list[tuple[str, str, str]] = []
        self.html_lang: str | None = None
        self.declarations: list[str] = []

    def handle_decl(self, decl: str) -> None:
        self.declarations.append(decl)

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        tag = tag.lower()
        attributes = {name.lower(): value or "" for name, value in attrs}
        classes = set(attributes.get("class", "").split())
        if element_id := attributes.get("id"):
            self.ids[element_id] += 1
        if tag == "html":
            self.html_lang = attributes.get("lang")
        if tag == "div" and "slot" in classes:
            self.slots += 1
        if tag == "section" and "slide" in classes:
            self.slides += 1
        if tag == "img":
            self.images.append(attributes)
            if asset_ref := attributes.get("data-a"):
                self.asset_refs.append(asset_ref)
        if tag == "button":
            self.buttons.append(attributes)

        # href on an ordinary <a> is navigation, not a load-time dependency.
        # src attributes and stylesheet/icon <link href> values are dependencies.
        if value := attributes.get("src"):
            self.resource_attributes.append((tag, "src", value))
        if tag == "link" and (value := attributes.get("href")):
            self.resource_attributes.append((tag, "href", value))

        if tag not in VOID_HTML_TAGS:
            self.stack.append(tag)

    def handle_startendtag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        self.handle_starttag(tag, attrs)
        if tag.lower() not in VOID_HTML_TAGS:
            self.stack.pop()

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if not self.stack:
            self.errors.append(f"unexpected closing tag </{tag}>")
            return
        if self.stack[-1] == tag:
            self.stack.pop()
            return

        expected = self.stack[-1]
        self.errors.append(f"closing tag </{tag}> encountered while <{expected}> is open")
        if tag in self.stack:
            while self.stack and self.stack[-1] != tag:
                self.stack.pop()
            self.stack.pop()


class Checks:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.slide_count = 0
        self.asset_count = 0
        self.python_count = 0

    def error(self, message: str) -> None:
        self.errors.append(message)

    def require_file(self, path: Path) -> bool:
        if not path.is_file():
            self.error(f"missing file: {path.relative_to(ROOT)}")
            return False
        if path.stat().st_size == 0:
            self.error(f"empty file: {path.relative_to(ROOT)}")
            return False
        return True

    def check_html(self) -> None:
        if not self.require_file(SLIDES):
            return

        deck_html = SLIDES.read_text(encoding="utf-8")
        parser = DeckHTMLParser()
        try:
            parser.feed(deck_html)
            parser.close()
        except Exception as error:  # HTMLParser failures should remain actionable.
            self.error(f"{SLIDES.name}: HTML parser failed: {error}")
            return

        for problem in parser.errors:
            self.error(f"{SLIDES.name}: {problem}")
        if parser.stack:
            self.error(
                f"{SLIDES.name}: unclosed tags at EOF: {' > '.join(parser.stack[-8:])}"
            )
        if not parser.declarations or parser.declarations[0].lower() != "doctype html":
            self.error(f"{SLIDES.name}: missing <!DOCTYPE html>")
        if parser.html_lang != "th":
            self.error(f"{SLIDES.name}: expected <html lang=\"th\">")

        duplicate_ids = sorted(element_id for element_id, count in parser.ids.items() if count > 1)
        if duplicate_ids:
            self.error(f"{SLIDES.name}: duplicate ids: {', '.join(duplicate_ids)}")
        for required_id in ("stage", "ui", "counter", "ctl", "help"):
            if parser.ids[required_id] != 1:
                self.error(
                    f"{SLIDES.name}: expected one id=\"{required_id}\", "
                    f"found {parser.ids[required_id]}"
                )

        self.slide_count = parser.slots
        if parser.slots == 0 or parser.slots != parser.slides:
            self.error(
                f"{SLIDES.name}: slide wrapper mismatch: "
                f"slots={parser.slots}, slide sections={parser.slides}"
            )

        for index, image in enumerate(parser.images, start=1):
            if not image.get("alt", "").strip():
                self.error(f"{SLIDES.name}: image #{index} has no useful alt text")
        for index, button in enumerate(parser.buttons, start=1):
            if not button.get("aria-label", "").strip():
                self.error(f"{SLIDES.name}: button #{index} has no aria-label")

        for tag, attribute, value in parser.resource_attributes:
            if value.startswith(("data:", "#")):
                continue
            self.error(
                f"{SLIDES.name}: external file dependency in <{tag} {attribute}=\"{value}\">"
            )
        if re.search(r"@import\s+(?:url\()?\s*['\"]?(?:https?:)?//", deck_html):
            self.error(f"{SLIDES.name}: remote CSS @import dependency found")
        if re.search(r"url\(\s*['\"]?(?:https?:)?//", deck_html):
            self.error(f"{SLIDES.name}: remote CSS url() dependency found")
        if re.search(r"\bfetch\(\s*['\"](?:https?:)?//", deck_html):
            self.error(f"{SLIDES.name}: remote fetch() dependency found")

        asset_blocks = re.findall(
            r"<script>\s*window\.ASSETS=(\{.*?\});\s*</script>", deck_html, re.DOTALL
        )
        if len(asset_blocks) != 1:
            self.error(
                f"{SLIDES.name}: expected one window.ASSETS block, found {len(asset_blocks)}"
            )
            return
        try:
            assets = json.loads(asset_blocks[0])
        except json.JSONDecodeError as error:
            self.error(f"{SLIDES.name}: invalid window.ASSETS JSON: {error}")
            return
        if not isinstance(assets, dict):
            self.error(f"{SLIDES.name}: window.ASSETS must be an object")
            return

        refs = set(parser.asset_refs)
        keys = set(assets)
        missing_assets = sorted(refs - keys)
        unused_assets = sorted(keys - refs)
        if missing_assets:
            self.error(f"{SLIDES.name}: missing embedded assets: {', '.join(missing_assets)}")
        if unused_assets:
            self.error(f"{SLIDES.name}: unused embedded assets: {', '.join(unused_assets)}")
        self.asset_count = len(keys)

        for key, data_uri in sorted(assets.items()):
            if not isinstance(data_uri, str):
                self.error(f"{SLIDES.name}: asset {key!r} is not a string")
                continue
            match = re.fullmatch(
                r"data:(image/(?:svg\+xml|png|jpeg));base64,([A-Za-z0-9+/=]+)",
                data_uri,
            )
            if not match:
                self.error(f"{SLIDES.name}: asset {key!r} is not a supported base64 image")
                continue
            media_type, payload = match.groups()
            try:
                decoded = base64.b64decode(payload, validate=True)
            except (binascii.Error, ValueError) as error:
                self.error(f"{SLIDES.name}: asset {key!r} has invalid base64: {error}")
                continue
            if not decoded:
                self.error(f"{SLIDES.name}: asset {key!r} decodes to an empty file")
            elif media_type == "image/svg+xml" and b"<svg" not in decoded[:1000]:
                self.error(f"{SLIDES.name}: asset {key!r} is labelled SVG but has no <svg>")
            elif media_type == "image/png" and not decoded.startswith(b"\x89PNG\r\n\x1a\n"):
                self.error(f"{SLIDES.name}: asset {key!r} has an invalid PNG signature")
            elif media_type == "image/jpeg" and not decoded.startswith(b"\xff\xd8\xff"):
                self.error(f"{SLIDES.name}: asset {key!r} has an invalid JPEG signature")

    def check_markdown_links(self, markdown_files: list[Path]) -> None:
        for markdown_file in markdown_files:
            if not self.require_file(markdown_file):
                continue
            text = markdown_file.read_text(encoding="utf-8")
            for match in MARKDOWN_LINK_RE.finditer(text):
                raw_target = match.group(1) or match.group(2) or ""
                parsed = urlsplit(raw_target)
                if parsed.scheme or raw_target.startswith(("#", "//")):
                    continue
                local_part = unquote(parsed.path)
                if not local_part:
                    continue
                target = (markdown_file.parent / local_part).resolve()
                try:
                    target.relative_to(ROOT)
                except ValueError:
                    self.error(
                        f"{markdown_file.relative_to(ROOT)}: local link escapes material root: "
                        f"{raw_target}"
                    )
                    continue
                if not target.exists():
                    line = text.count("\n", 0, match.start()) + 1
                    self.error(
                        f"{markdown_file.relative_to(ROOT)}:{line}: missing link target "
                        f"{raw_target}"
                    )
                elif target.is_file() and target.stat().st_size == 0:
                    self.error(
                        f"{markdown_file.relative_to(ROOT)}: link target is empty: {raw_target}"
                    )

    def check_labs(self) -> list[Path]:
        found_lab_dirs = {path.name: path for path in ROOT.glob("00[1-4]_LAB_*") if path.is_dir()}
        missing_labs = sorted(set(EXPECTED_LABS) - set(found_lab_dirs))
        unexpected_labs = sorted(set(found_lab_dirs) - set(EXPECTED_LABS))
        if missing_labs:
            self.error(f"missing LAB directories: {', '.join(missing_labs)}")
        if unexpected_labs:
            self.error(f"unexpected LAB directories: {', '.join(unexpected_labs)}")

        readmes: list[Path] = []
        python_files: list[Path] = []
        for lab_name, required_scripts in EXPECTED_LABS.items():
            lab_dir = found_lab_dirs.get(lab_name)
            if lab_dir is None:
                continue
            readme = lab_dir / "readme.md"
            requirements = lab_dir / "requirements.txt"
            readmes.append(readme)
            self.require_file(readme)
            self.require_file(requirements)

            for script_name in sorted(required_scripts):
                self.require_file(lab_dir / script_name)
            if readme.is_file():
                readme_text = readme.read_text(encoding="utf-8")
                for heading in REQUIRED_LAB_HEADINGS:
                    if heading not in readme_text:
                        self.error(f"{lab_name}: missing section {heading!r}")
                for script_name in required_scripts:
                    if script_name not in readme_text:
                        self.error(f"{lab_name}: README does not mention {script_name}")

            if requirements.is_file():
                requirement_lines = [
                    line.strip()
                    for line in requirements.read_text(encoding="utf-8").splitlines()
                    if line.strip() and not line.lstrip().startswith("#")
                ]
                if requirement_lines != ["pika==1.3.2"]:
                    self.error(
                        f"{requirements.relative_to(ROOT)}: expected only pika==1.3.2, "
                        f"found {requirement_lines!r}"
                    )

            python_files.extend(sorted(lab_dir.glob("*.py")))

        python_files.append(Path(__file__).resolve())
        for script in python_files:
            if not self.require_file(script):
                continue
            try:
                ast.parse(script.read_text(encoding="utf-8"), filename=str(script))
            except SyntaxError as error:
                self.error(f"{script.relative_to(ROOT)}: Python syntax error: {error}")
        self.python_count = len(python_files) - 1
        return readmes

    def check_cross_material_consistency(self, material_files: list[Path]) -> None:
        texts = {
            path: path.read_text(encoding="utf-8")
            for path in material_files
            if path.is_file()
        }

        for path, text in texts.items():
            tags = sorted(set(RABBITMQ_IMAGE_RE.findall(text)))
            wrong_tags = [tag for tag in tags if tag != PINNED_RABBITMQ_IMAGE]
            if wrong_tags:
                self.error(
                    f"{path.relative_to(ROOT)}: unpinned/obsolete RabbitMQ image tag(s): "
                    f"{', '.join(wrong_tags)}; expected {PINNED_RABBITMQ_IMAGE}"
                )
            if "DevTools/06_RabbitMQ" in text:
                self.error(
                    f"{path.relative_to(ROOT)}: obsolete path DevTools/06_RabbitMQ; "
                    "expected DevTools/test/02_RabbitMQxx"
                )
            if re.search(r"rabbitmq-diagnostics\s+-q\s+ping\b", text):
                self.error(
                    f"{path.relative_to(ROOT)}: basic ping can pass before the RabbitMQ "
                    "application is ready; use rabbitmq-diagnostics -q check_running"
                )

            executable_blocks: list[str]
            if path.suffix.lower() == ".md":
                executable_blocks = [
                    body
                    for language, body in FENCED_CODE_RE.findall(text)
                    if language.strip().lower() in {"", "bash", "sh", "shell"}
                ]
            else:
                executable_blocks = [
                    html_module.unescape(re.sub(r"<[^>]+>", "", block))
                    for block in re.findall(r"<pre\b[^>]*>(.*?)</pre>", text, re.DOTALL)
                ]
            if any(
                re.search(r"^\s*docker\s+rm\s+-f\s+devtools\s*$", block, re.MULTILINE)
                for block in executable_blocks
            ):
                self.error(
                    f"{path.relative_to(ROOT)}: destructive classroom reset appears in an "
                    "executable block; preserve devtools with docker start || docker run"
                )
            for block in executable_blocks:
                for line in block.splitlines():
                    if "docker exec" not in line or "rabbitmq-diagnostics" not in line:
                        continue
                    if "docker exec --user rabbitmq rabbit rabbitmq-diagnostics" not in line:
                        self.error(
                            f"{path.relative_to(ROOT)}: readiness CLI must run as the "
                            "rabbitmq container user to avoid an Erlang-cookie ownership race"
                        )

        slide_source = texts.get(SLIDES, "")
        # Search rendered teaching copy, not random character sequences inside the
        # large base64 asset bundle, CSS, or navigation JavaScript.
        slide_source = re.sub(
            r"<script>\s*window\.ASSETS=\{.*?</script>",
            "",
            slide_source,
            flags=re.DOTALL,
        )
        slide_source = re.sub(
            r"<(?:style|script)\b[^>]*>.*?</(?:style|script)>",
            "",
            slide_source,
            flags=re.DOTALL | re.IGNORECASE,
        )
        slide_text = html_module.unescape(re.sub(r"<[^>]+>", " ", slide_source)).lower()
        for label, alternatives in {
            "publisher confirm": ("publisher confirm", "confirm_delivery"),
            "mandatory routing check": ("mandatory", "unroutable"),
            "at-least-once": ("at-least-once",),
            "idempotency": ("idempotent", "idempotency"),
            "dead-letter queue": ("dlq", "dead letter"),
        }.items():
            if not any(term in slide_text for term in alternatives):
                self.error(f"{SLIDES.name}: missing production bridge topic: {label}")

    def finish(self) -> None:
        if self.errors:
            for error in self.errors:
                print(f"ERROR: {error}")
            print(f"FAILED: {len(self.errors)} problem(s)")
            raise SystemExit(1)
        print(
            f"OK: {self.slide_count} slides, {self.asset_count} embedded assets, "
            f"{len(EXPECTED_LABS)} labs, {self.python_count} LAB Python files; "
            "HTML, links, assets and Python syntax passed"
        )


def main() -> None:
    checks = Checks()
    checks.check_html()
    lab_readmes = checks.check_labs()
    markdown_files = [ROOT_README, *lab_readmes]
    checks.check_markdown_links(markdown_files)
    checks.check_cross_material_consistency([ROOT_README, SLIDES, *lab_readmes])
    checks.finish()


if __name__ == "__main__":
    main()
