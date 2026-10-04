# -*- coding: utf-8 -*-
"""기술명세 마크다운을 이어 한글 PDF로 만든다.

Mermaid 차트는 Edge로 그린 뒤 잘라서 PNG로 넣는다.
"""
from __future__ import annotations

import hashlib
import html
import os
import re
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parent
SPECS = ROOT / "specs"
DIAGRAMS = SPECS / "diagrams"
MD_PATH = ROOT / "technical-specs.md"
HTML_PATH = ROOT / "technical-specs.html"
PDF_PATH = ROOT / "technical-specs.pdf"
USED_DIAGRAMS: set[str] = set()

INLINE_CODE = re.compile(r"`([^`]+)`")
BOLD = re.compile(r"\*\*(.+?)\*\*")


def inline(text: str) -> str:
    escaped = html.escape(text)
    escaped = INLINE_CODE.sub(lambda match: f"<code>{match.group(1)}</code>", escaped)
    escaped = BOLD.sub(lambda match: f"<strong>{match.group(1)}</strong>", escaped)
    return escaped


def markdown_to_html(text: str) -> str:
    lines = text.splitlines()
    parts: list[str] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        if line.startswith("```"):
            language = line[3:].strip()
            body: list[str] = []
            index += 1
            while index < len(lines) and not lines[index].startswith("```"):
                body.append(lines[index])
                index += 1
            index += 1
            source = "\n".join(body).strip() + "\n"
            if language == "mermaid":
                parts.append(render_diagram(source))
            else:
                parts.append(f'<pre class="code">{html.escape(source)}</pre>')
            continue
        if not line.strip():
            index += 1
            continue
        if line.startswith("#"):
            level = len(line) - len(line.lstrip("#"))
            level = min(max(level, 1), 4)
            title = line[level:].strip()
            parts.append(f"<h{level}>{inline(title)}</h{level}>")
            index += 1
            continue
        if line.startswith("- "):
            items: list[str] = []
            while index < len(lines) and lines[index].startswith("- "):
                items.append(f"<li>{inline(lines[index][2:].strip())}</li>")
                index += 1
            parts.append("<ul>" + "".join(items) + "</ul>")
            continue
        ordered = re.match(r"\d+\.\s+", line)
        if ordered:
            items = []
            while index < len(lines) and re.match(r"\d+\.\s+", lines[index]):
                item_text = re.sub(r"^\d+\.\s+", "", lines[index]).strip()
                items.append(f"<li>{inline(item_text)}</li>")
                index += 1
            parts.append("<ol>" + "".join(items) + "</ol>")
            continue
        paragraph = [line.strip()]
        index += 1
        while (
            index < len(lines)
            and lines[index].strip()
            and not lines[index].startswith(("#", "- ", "```"))
            and not re.match(r"\d+\.\s+", lines[index])
        ):
            paragraph.append(lines[index].strip())
            index += 1
        parts.append(f"<p>{inline(' '.join(paragraph))}</p>")
    return "\n".join(parts)


def combined_markdown() -> str:
    files = sorted(SPECS.glob("*.md"))
    if not files:
        raise SystemExit(f"명세 마크다운이 없습니다: {SPECS}")
    chunks = [path.read_text(encoding="utf-8").strip() for path in files]
    return "\n\n".join(chunks) + "\n"


HTML_CSS = """
@page { margin: 18mm 16mm; }
body { font-family: "Malgun Gothic", sans-serif; font-size: 11pt; line-height: 1.55; color: #1c1c1c; }
h1 { font-size: 20pt; margin: 0 0 0.6em; page-break-before: always; }
h1:first-of-type { page-break-before: auto; }
h2 { font-size: 15pt; margin: 1.2em 0 0.4em; page-break-after: avoid; }
h3 { font-size: 12.5pt; margin: 1em 0 0.3em; page-break-after: avoid; }
p, li { orphans: 3; widows: 3; }
ul { margin: 0.2em 0 0.8em; padding-left: 1.2em; }
code { font-family: Consolas, "Malgun Gothic", monospace; font-size: 9.5pt; }
pre { font-family: Consolas, "Malgun Gothic", monospace; font-size: 9pt; background: #f3f3f3;
      padding: 8px 10px; white-space: pre-wrap; }
figure.chart { margin: 0.4em 0 1em; text-align: center; page-break-inside: avoid; break-inside: avoid; }
figure.chart img { max-width: 100%; max-height: 230mm; width: auto; height: auto; }
"""


def render_html(body: str) -> str:
    return "\n".join(
        [
            "<!DOCTYPE html>",
            '<html lang="ko">',
            "<head>",
            '<meta charset="utf-8" />',
            "<title>기술명세</title>",
            "<style>",
            HTML_CSS,
            "</style>",
            "</head>",
            "<body>",
            body,
            "</body>",
            "</html>",
        ]
    )


def find_browser() -> Path | None:
    local = os.environ.get("LOCALAPPDATA", "")
    candidates = [
        Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
        Path(local) / "Google" / "Chrome" / "Application" / "chrome.exe",
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


ACTOR_LINE = re.compile(r"^(\w+)\[(.+)\]$")
CASE_LINE = re.compile(r"^(\w+)\(\[(.+)\]\)$")
BOUNDARY_LINE = re.compile(r"^subgraph\s+\w+\[(.+)\]$")
ASSOC_LINE = re.compile(r"^(\w+)\s+---\s+(\w+)$")
EXTEND_LINE = re.compile(r"^(\w+)\s+-\.->\|([^|]+)\|\s+(\w+)$")
BREAK_LINE = re.compile(r"<br\s*/?>")


def parse_usecase(source: str) -> tuple[str, list, list, list, list]:
    actors: list[tuple[str, str]] = []
    cases: list[tuple[str, str]] = []
    assocs: list[tuple[str, str]] = []
    extends: list[tuple[str, str, str]] = []
    boundary = "시스템"
    for raw in source.splitlines():
        line = raw.strip()
        if not line or line.startswith(("%%", "flowchart", "direction")) or line == "end":
            continue
        found = BOUNDARY_LINE.match(line)
        if found:
            boundary = found.group(1)
            continue
        found = CASE_LINE.match(line)
        if found:
            cases.append((found.group(1), found.group(2)))
            continue
        found = ACTOR_LINE.match(line)
        if found:
            actors.append((found.group(1), found.group(2)))
            continue
        found = ASSOC_LINE.match(line)
        if found:
            assocs.append((found.group(1), found.group(2)))
            continue
        found = EXTEND_LINE.match(line)
        if found:
            extends.append((found.group(1), found.group(2), found.group(3)))
    if not actors or not cases:
        raise SystemExit("사람 그림으로 그릴 행위자나 유스케이스가 없습니다.")
    return boundary, actors, cases, assocs, extends


def text_width(text: str) -> int:
    return sum(17 if ord(char) > 127 else 9 for char in text)


def usecase_svg(source: str) -> str:
    boundary, actors, cases, assocs, extends = parse_usecase(source)
    parsed = [(case_id, BREAK_LINE.split(label)) for case_id, label in cases]
    ellipse_w = max(max(text_width(line) for line in lines) for _, lines in parsed) + 52
    row_h = 78
    ellipse_h = 50
    pad_top = 40
    pad_x = 48
    boundary_x = 188
    boundary_y = 10
    extend_room = 28
    boundary_w = pad_x + ellipse_w + pad_x + extend_room
    boundary_h = pad_top + row_h * len(parsed) + 8
    ellipse_x = boundary_x + pad_x
    centers: dict[str, float] = {}
    for index, (case_id, _) in enumerate(parsed):
        centers[case_id] = boundary_y + pad_top + index * row_h + ellipse_h / 2
    linked: dict[str, list[str]] = {}
    for actor_id, case_id in assocs:
        linked.setdefault(actor_id, []).append(case_id)

    def actor_anchor(actor_id: str) -> float:
        targets = linked.get(actor_id, [])
        if not targets:
            return boundary_y + boundary_h / 2
        return sum(centers[case_id] for case_id in targets) / len(targets)

    width = boundary_x + boundary_w + 20
    height = boundary_y + boundary_h + 28
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<defs><marker id='extend-arrow' markerWidth='8' markerHeight='8' refX='7' refY='4' orient='auto'>",
        "<path d='M0,0 L8,4 L0,8 Z' fill='#555'/></marker></defs>",
        f"<rect x='{boundary_x}' y='{boundary_y}' width='{boundary_w}' height='{boundary_h}' fill='none' stroke='#9a9a9a' stroke-width='1.4'/>",
        f"<text x='{boundary_x + boundary_w / 2}' y='{boundary_y + 24}' text-anchor='middle' font-size='15' fill='#333'>{html.escape(boundary)}</text>",
    ]
    hands: dict[str, tuple[float, float]] = {}
    for index, (actor_id, name) in enumerate(actors):
        center_x = 78
        center_y = actor_anchor(actor_id)
        radius = 13
        head_y = center_y - 34
        neck = head_y + radius
        hip = neck + 30
        arm_y = neck + 12
        foot = hip + 24
        arm = 20
        leg = 15
        parts.append(
            f"<g fill='none' stroke='#222' stroke-width='1.7' stroke-linecap='round'>"
            f"<circle cx='{center_x}' cy='{head_y}' r='{radius}'/>"
            f"<line x1='{center_x}' y1='{neck}' x2='{center_x}' y2='{hip}'/>"
            f"<line x1='{center_x - arm}' y1='{arm_y}' x2='{center_x + arm}' y2='{arm_y}'/>"
            f"<line x1='{center_x}' y1='{hip}' x2='{center_x - leg}' y2='{foot}'/>"
            f"<line x1='{center_x}' y1='{hip}' x2='{center_x + leg}' y2='{foot}'/>"
            f"</g>"
            f"<text x='{center_x}' y='{foot + 20}' text-anchor='middle' font-size='15' fill='#222'>{html.escape(name)}</text>"
        )
        hands[actor_id] = (center_x + arm, arm_y)
    for actor_id, case_id in assocs:
        start_x, start_y = hands[actor_id]
        end_x = ellipse_x
        end_y = centers[case_id]
        bend = (start_x + end_x) / 2
        parts.append(
            f"<path d='M {start_x} {start_y} C {bend} {start_y}, {bend} {end_y}, {end_x} {end_y}' fill='none' stroke='#777' stroke-width='1.3'/>"
        )
    right = ellipse_x + ellipse_w
    for source_id, label, target_id in extends:
        start_y = centers[source_id]
        end_y = centers[target_id]
        lane = right + 16
        mid_y = (start_y + end_y) / 2
        parts.append(
            f"<path d='M {right} {start_y} C {lane} {start_y}, {lane} {end_y}, {right} {end_y}' fill='none' stroke='#555' stroke-width='1.3' stroke-dasharray='4 3' marker-end='url(#extend-arrow)'/>"
            f"<text x='{lane + 8}' y='{mid_y + 4}' font-size='13' fill='#333'>{html.escape(label)}</text>"
        )
    for case_id, lines in parsed:
        center_y = centers[case_id]
        parts.append(
            f"<ellipse cx='{ellipse_x + ellipse_w / 2}' cy='{center_y}' rx='{ellipse_w / 2}' ry='{ellipse_h / 2}' fill='#f4f4f4' stroke='#666' stroke-width='1.3'/>"
        )
        if len(lines) == 1:
            parts.append(
                f"<text x='{ellipse_x + ellipse_w / 2}' y='{center_y + 5}' text-anchor='middle' font-size='15' fill='#222'>{html.escape(lines[0])}</text>"
            )
        else:
            first = center_y - 6
            spans = "".join(
                f"<tspan x='{ellipse_x + ellipse_w / 2}' y='{first + offset * 18}'>{html.escape(line)}</tspan>"
                for offset, line in enumerate(lines)
            )
            parts.append(f"<text text-anchor='middle' font-size='15' fill='#222'>{spans}</text>")
    parts.append("</svg>")
    return "".join(parts)


def svg_page(svg: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8" />
<style>
  html, body {{ margin: 0; background: #fff; }}
  body {{ padding: 20px; font-family: "Malgun Gothic", sans-serif; }}
  svg {{ font-family: "Malgun Gothic", sans-serif; }}
</style>
</head>
<body>
{svg}
</body>
</html>
"""


def diagram_page(source: str) -> str:
    if "actor-style: person" in source:
        return svg_page(usecase_svg(source))
    escaped = html.escape(source)
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8" />
<style>
  html, body {{ margin: 0; background: #fff; }}
  body {{ padding: 24px; }}
  .mermaid {{ font-family: "Malgun Gothic", sans-serif; }}
</style>
</head>
<body>
<pre class="mermaid">{escaped}</pre>
<script type="module">
  import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";
  mermaid.initialize({{ startOnLoad: true, theme: "neutral", fontFamily: "Malgun Gothic, sans-serif" }});
</script>
</body>
</html>
"""


def crop_whitespace(path: Path) -> None:
    image = Image.open(path).convert("RGB")
    background = Image.new("RGB", image.size, (255, 255, 255))
    box = ImageChops.difference(image, background).getbbox()
    if box is None:
        raise SystemExit(f"차트가 비어 있습니다: {path.name}")
    pad = 16
    left = max(box[0] - pad, 0)
    top = max(box[1] - pad, 0)
    right = min(box[2] + pad, image.width)
    bottom = min(box[3] + pad, image.height)
    cropped = image.crop((left, top, right, bottom))
    if cropped.width < 40 or cropped.height < 40:
        raise SystemExit(f"차트가 너무 작습니다: {path.name}")
    cropped.save(path)


def render_diagram(source: str) -> str:
    digest = hashlib.sha256(source.encode("utf-8")).hexdigest()[:12]
    USED_DIAGRAMS.add(digest)
    DIAGRAMS.mkdir(parents=True, exist_ok=True)
    png = DIAGRAMS / f"{digest}.png"
    if not png.is_file():
        browser = find_browser()
        if browser is None:
            raise SystemExit("차트를 그릴 Edge 또는 Chrome을 찾지 못했습니다.")
        html_path = DIAGRAMS / f"{digest}.html"
        html_path.write_text(diagram_page(source), encoding="utf-8")
        profile = Path(tempfile.mkdtemp(prefix="specs-chart-"))
        command = [
            str(browser),
            "--headless=new",
            "--disable-gpu",
            "--no-first-run",
            "--hide-scrollbars",
            "--force-device-scale-factor=2",
            "--virtual-time-budget=12000",
            "--window-size=1400,2200",
            f"--user-data-dir={profile}",
            f"--screenshot={png.resolve()}",
            html_path.resolve().as_uri(),
        ]
        try:
            subprocess.run(command, check=True, timeout=60)
            deadline = time.time() + 8
            while not png.is_file() and time.time() < deadline:
                time.sleep(0.2)
        finally:
            html_path.unlink(missing_ok=True)
            shutil.rmtree(profile, ignore_errors=True)
        if not png.is_file():
            raise SystemExit(f"차트 이미지가 만들어지지 않았습니다: {png.name}")
        crop_whitespace(png)
    relative = png.relative_to(ROOT).as_posix()
    return f'<figure class="chart"><img src="{html.escape(relative)}" alt="차트" /></figure>'


def cleanup_diagrams() -> None:
    if not DIAGRAMS.is_dir():
        return
    for path in DIAGRAMS.iterdir():
        if path.is_dir():
            shutil.rmtree(path, ignore_errors=True)
        elif path.stem not in USED_DIAGRAMS:
            path.unlink()


def write_pdf(html_path: Path, pdf_path: Path) -> None:
    browser = find_browser()
    if browser is None:
        raise SystemExit("PDF로 인쇄할 Edge 또는 Chrome을 찾지 못했습니다.")
    if pdf_path.exists():
        pdf_path.unlink()
    profile = Path(tempfile.mkdtemp(prefix="specs-pdf-"))
    command = [
        str(browser),
        "--headless=new",
        "--disable-gpu",
        "--no-first-run",
        "--no-pdf-header-footer",
        f"--user-data-dir={profile}",
        f"--print-to-pdf={pdf_path.resolve()}",
        html_path.resolve().as_uri(),
    ]
    try:
        subprocess.run(command, check=True, timeout=120)
    finally:
        shutil.rmtree(profile, ignore_errors=True)
    if not pdf_path.is_file() or pdf_path.stat().st_size < 1000:
        raise SystemExit(f"PDF가 만들어지지 않았습니다: {pdf_path}")


def main() -> None:
    markdown = combined_markdown()
    MD_PATH.write_text(markdown, encoding="utf-8")
    HTML_PATH.write_text(render_html(markdown_to_html(markdown)), encoding="utf-8")
    cleanup_diagrams()
    write_pdf(HTML_PATH, PDF_PATH)
    print(f"Wrote {MD_PATH}")
    print(f"Wrote {HTML_PATH}")
    print(f"Wrote {PDF_PATH} ({PDF_PATH.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
