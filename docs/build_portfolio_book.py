# -*- coding: utf-8 -*-
"""포트폴리오 북 마크다운 챕터들을 통합하여 A4 규격의 한글 PDF 단행본으로 빌드한다.

마크다운 표, 인용구, 코드 블록, 인라인 링크 및 Mermaid 다이어그램을 파싱하여
Microsoft Edge 또는 Google Chrome 헤드리스 엔진으로 고품질 인쇄용 PDF를 생성한다.
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
CHAPTERS = ROOT / "portfolio-book"
DIAGRAMS = CHAPTERS / "diagrams"
MD_PATH = ROOT / "portfolio-book.md"
HTML_PATH = ROOT / "portfolio-book.html"
PDF_PATH = ROOT / "portfolio-book.pdf"
USED_DIAGRAMS: set[str] = set()

INLINE_CODE = re.compile(r"`([^`]+)`")
BOLD = re.compile(r"\*\*(.+?)\*\*")
LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def inline(text: str) -> str:
    escaped = html.escape(text)
    escaped = INLINE_CODE.sub(lambda m: f"<code>{m.group(1)}</code>", escaped)
    escaped = BOLD.sub(lambda m: f"<strong>{m.group(1)}</strong>", escaped)
    escaped = LINK.sub(lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>', escaped)
    return escaped


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


def diagram_page(source: str) -> str:
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
            escaped = html.escape(source.strip())
            return f'<pre class="code diagram-fallback">{escaped}</pre>'
        html_path = DIAGRAMS / f"{digest}.html"
        html_path.write_text(diagram_page(source), encoding="utf-8")
        profile = Path(tempfile.mkdtemp(prefix="book-chart-"))
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
                time.sleep(0.3)
            crop_whitespace(png)
        except Exception as e:
            print(f"[경고] 차트 렌더링 실패 ({digest}): {e}")
            escaped = html.escape(source.strip())
            return f'<pre class="code diagram-fallback">{escaped}</pre>'
        finally:
            shutil.rmtree(profile, ignore_errors=True)
            if html_path.exists():
                html_path.unlink()
    rel = png.relative_to(ROOT).as_posix()
    return f'<figure class="chart"><img src="{rel}" alt="다이어그램" /></figure>'


def parse_table(lines: list[str]) -> str:
    rows: list[list[str]] = []
    for line in lines:
        raw_cells = [c.strip() for c in line.strip().strip("|").split("|")]
        rows.append(raw_cells)
    if not rows:
        return ""
    header = rows[0]
    data_rows = rows[1:]
    # Check if the next row is a separator line (e.g. :---: | :---)
    if data_rows and all(re.match(r"^:?-+:?$", cell) for cell in data_rows[0]):
        data_rows = data_rows[1:]

    html_parts = ['<div class="table-wrap"><table><thead><tr>']
    for cell in header:
        html_parts.append(f"<th>{inline(cell)}</th>")
    html_parts.append("</tr></thead><tbody>")
    for r in data_rows:
        html_parts.append("<tr>")
        for cell in r:
            html_parts.append(f"<td>{inline(cell)}</td>")
        html_parts.append("</tr>")
    html_parts.append("</tbody></table></div>")
    return "".join(html_parts)


def markdown_to_html(text: str) -> str:
    lines = text.splitlines()
    parts: list[str] = []
    index = 0
    first_h1 = True

    while index < len(lines):
        line = lines[index]

        # Fenced code blocks
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
                parts.append(f'<pre class="code"><code>{html.escape(source)}</code></pre>')
            continue

        stripped = line.strip()
        if not stripped:
            index += 1
            continue

        # Horizontal Rule
        if stripped in ("---", "***", "___"):
            parts.append('<hr class="divider" />')
            index += 1
            continue

        # Headings
        if line.startswith("#"):
            level = len(line) - len(line.lstrip("#"))
            level = min(max(level, 1), 4)
            title = line[level:].strip()
            cls = ""
            if level == 1:
                if first_h1:
                    cls = ' class="book-title"'
                    first_h1 = False
                else:
                    cls = ' class="chapter-title"'
            parts.append(f"<h{level}{cls}>{inline(title)}</h{level}>")
            index += 1
            continue

        # Blockquote
        if line.startswith(">"):
            quote_lines: list[str] = []
            while index < len(lines) and (lines[index].startswith(">") or (lines[index].strip() and not lines[index].startswith("#"))):
                curr = lines[index]
                if curr.startswith(">"):
                    curr = curr[1:].strip()
                else:
                    curr = curr.strip()
                quote_lines.append(curr)
                index += 1
            quote_body = "<br />".join(inline(ql) for ql in quote_lines if ql)
            parts.append(f"<blockquote><p>{quote_body}</p></blockquote>")
            continue

        # Tables (lines starting and ending with |)
        if stripped.startswith("|") and stripped.endswith("|"):
            table_lines: list[str] = []
            while index < len(lines) and lines[index].strip().startswith("|") and lines[index].strip().endswith("|"):
                table_lines.append(lines[index])
                index += 1
            parts.append(parse_table(table_lines))
            continue

        # Unordered Lists
        if line.startswith("- ") or line.startswith("* "):
            items: list[str] = []
            while index < len(lines) and (lines[index].startswith("- ") or lines[index].startswith("* ")):
                item_content = lines[index][2:].strip()
                items.append(f"<li>{inline(item_content)}</li>")
                index += 1
            parts.append(f"<ul>{''.join(items)}</ul>")
            continue

        # Ordered Lists
        ordered = re.match(r"^\d+\.\s+", line)
        if ordered:
            items = []
            while index < len(lines) and re.match(r"^\d+\.\s+", lines[index]):
                item_text = re.sub(r"^\d+\.\s+", "", lines[index]).strip()
                items.append(f"<li>{inline(item_text)}</li>")
                index += 1
            parts.append(f"<ol>{''.join(items)}</ol>")
            continue

        # Paragraphs
        paragraph = [line.strip()]
        index += 1
        while (
            index < len(lines)
            and lines[index].strip()
            and not lines[index].startswith(("#", "- ", "* ", ">", "```"))
            and not (lines[index].strip().startswith("|") and lines[index].strip().endswith("|"))
            and not lines[index].strip() in ("---", "***", "___")
            and not re.match(r"^\d+\.\s+", lines[index])
        ):
            paragraph.append(lines[index].strip())
            index += 1
        parts.append(f"<p>{inline(' '.join(paragraph))}</p>")

    return "\n".join(parts)


def combined_markdown() -> str:
    files = sorted(CHAPTERS.glob("*.md"))
    if not files:
        raise SystemExit(f"포트폴리오 북 챕터 마크다운이 없습니다: {CHAPTERS}")
    chunks = [path.read_text(encoding="utf-8").strip() for path in files]
    return "\n\n".join(chunks) + "\n"


HTML_CSS = """
@page {
  size: A4;
  margin: 20mm 18mm 22mm 18mm;
}

body {
  font-family: "Malgun Gothic", "Apple SD Gothic Neo", "Segoe UI", sans-serif;
  font-size: 10.5pt;
  line-height: 1.65;
  color: #1e293b;
  background: #ffffff;
  word-break: keep-all;
}

/* 제목 계층 스타일링 */
h1.book-title {
  font-size: 24pt;
  font-weight: 800;
  color: #0f172a;
  text-align: center;
  margin-top: 36px;
  margin-bottom: 12px;
  page-break-before: auto;
  line-height: 1.3;
}

h3:has(+ hr.divider),
h1.book-title + h3 {
  font-size: 12.5pt;
  font-weight: 500;
  color: #475569;
  text-align: center;
  margin-top: 0;
  margin-bottom: 24px;
}

h1.chapter-title {
  font-size: 18pt;
  font-weight: 700;
  color: #0f172a;
  border-bottom: 2px solid #2563eb;
  padding-bottom: 8px;
  margin-top: 0;
  margin-bottom: 20px;
  page-break-before: always;
}

h2 {
  font-size: 13.5pt;
  font-weight: 700;
  color: #1e3a8a;
  margin-top: 24px;
  margin-bottom: 10px;
  page-break-after: avoid;
  border-left: 4px solid #3b82f6;
  padding-left: 8px;
}

h3 {
  font-size: 11.5pt;
  font-weight: 700;
  color: #334155;
  margin-top: 18px;
  margin-bottom: 8px;
  page-break-after: avoid;
}

h4 {
  font-size: 10.5pt;
  font-weight: 700;
  color: #475569;
  margin-top: 14px;
  margin-bottom: 6px;
  page-break-after: avoid;
}

/* 문단 및 목록 */
p {
  margin: 0 0 10px;
  orphans: 3;
  widows: 3;
}

ul, ol {
  margin: 4px 0 12px;
  padding-left: 20px;
}

li {
  margin-bottom: 4px;
}

/* 인용 상자 */
blockquote {
  margin: 14px 0;
  padding: 12px 16px;
  background: #f8fafc;
  border-left: 4px solid #2563eb;
  border-radius: 0 4px 4px 0;
  color: #334155;
  font-size: 9.8pt;
  line-height: 1.6;
  page-break-inside: avoid;
}

blockquote p {
  margin: 0;
}

/* 구분선 */
hr.divider {
  border: none;
  border-top: 1px solid #cbd5e1;
  margin: 20px 0;
}

/* 표(Table) */
.table-wrap {
  margin: 14px 0;
  page-break-inside: avoid;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 9.2pt;
  line-height: 1.5;
}

th, td {
  border: 1px solid #cbd5e1;
  padding: 8px 10px;
  text-align: left;
}

th {
  background: #f1f5f9;
  color: #0f172a;
  font-weight: 700;
}

tr:nth-child(even) td {
  background: #f8fafc;
}

/* 코드 */
code {
  font-family: Consolas, "Segoe UI Mono", "Malgun Gothic", monospace;
  font-size: 9.2pt;
  background: #f1f5f9;
  color: #0f172a;
  padding: 2px 5px;
  border-radius: 3px;
  border: 1px solid #e2e8f0;
}

pre.code {
  font-family: Consolas, "Segoe UI Mono", "Malgun Gothic", monospace;
  font-size: 8.8pt;
  line-height: 1.45;
  background: #0f172a;
  color: #f8fafc;
  padding: 12px 14px;
  border-radius: 6px;
  overflow-x: auto;
  white-space: pre-wrap;
  page-break-inside: avoid;
  margin: 12px 0;
}

pre.code code {
  background: transparent;
  color: inherit;
  padding: 0;
  border: none;
}

/* 차트/다이어그램 이미지 */
figure.chart {
  margin: 16px 0;
  text-align: center;
  page-break-inside: avoid;
}

figure.chart img {
  max-width: 100%;
  max-height: 210mm;
  width: auto;
  height: auto;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 10px;
  background: #ffffff;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

a {
  color: #2563eb;
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}
"""


def render_html(body: str) -> str:
    return "\n".join(
        [
            "<!DOCTYPE html>",
            '<html lang="ko">',
            "<head>",
            '<meta charset="utf-8" />',
            "<title>코탐록 포트폴리오 북 (Kotamrok Portfolio Book)</title>",
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


def write_pdf(html_path: Path, pdf_path: Path) -> None:
    browser = find_browser()
    if browser is None:
        raise SystemExit("PDF로 인쇄할 Edge 또는 Chrome을 찾지 못했습니다.")
    if pdf_path.exists():
        pdf_path.unlink()
    profile = Path(tempfile.mkdtemp(prefix="portfolio-book-pdf-"))
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
    print("[1/4] 포트폴리오 북 마크다운 챕터 병합 중...")
    markdown = combined_markdown()
    MD_PATH.write_text(markdown, encoding="utf-8")
    print(f"  -> 통합 마크다운 저장: {MD_PATH}")

    print("[2/4] 마크다운 -> HTML 변환 및 다이어그램 렌더링 중...")
    html_content = render_html(markdown_to_html(markdown))
    HTML_PATH.write_text(html_content, encoding="utf-8")
    print(f"  -> HTML 저장: {HTML_PATH}")

    print("[3/4] 헤드리스 브라우저 A4 PDF 변환 중...")
    write_pdf(HTML_PATH, PDF_PATH)
    print(f"  -> PDF 완성: {PDF_PATH} ({PDF_PATH.stat().st_size // 1024} KB)")

    print("[4/4] 빌드 완료! 성공적으로 포트폴리오 북이 생성되었습니다.")


if __name__ == "__main__":
    main()
