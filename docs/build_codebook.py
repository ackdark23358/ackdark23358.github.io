# -*- coding: utf-8 -*-
"""코드북 마크다운을 이어 한글 PDF로 만든다."""
from __future__ import annotations

import html
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CHAPTERS = ROOT / "codebook"
MD_PATH = ROOT / "codebook.md"
HTML_PATH = ROOT / "codebook.html"
PDF_PATH = ROOT / "codebook.pdf"

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
            body: list[str] = []
            index += 1
            while index < len(lines) and not lines[index].startswith("```"):
                body.append(lines[index])
                index += 1
            index += 1
            parts.append(f'<pre class="code">{html.escape(chr(10).join(body))}</pre>')
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
        if re.match(r"\d+\.\s+", line):
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
    files = sorted(CHAPTERS.glob("*.md"))
    if not files:
        raise SystemExit(f"코드북 마크다운이 없습니다: {CHAPTERS}")
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
ul, ol { margin: 0.2em 0 0.8em; padding-left: 1.2em; }
code { font-family: Consolas, "Malgun Gothic", monospace; font-size: 9.5pt; }
pre { font-family: Consolas, "Malgun Gothic", monospace; font-size: 9pt; background: #f3f3f3;
      padding: 8px 10px; white-space: pre-wrap; }
"""


def render_html(body: str) -> str:
    return "\n".join(
        [
            "<!DOCTYPE html>",
            '<html lang="ko">',
            "<head>",
            '<meta charset="utf-8" />',
            "<title>코드북</title>",
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


def write_pdf(html_path: Path, pdf_path: Path) -> None:
    browser = find_browser()
    if browser is None:
        raise SystemExit("PDF로 인쇄할 Edge 또는 Chrome을 찾지 못했습니다.")
    if pdf_path.exists():
        pdf_path.unlink()
    profile = Path(tempfile.mkdtemp(prefix="codebook-pdf-"))
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
    write_pdf(HTML_PATH, PDF_PATH)
    print(f"Wrote {MD_PATH}")
    print(f"Wrote {HTML_PATH}")
    print(f"Wrote {PDF_PATH} ({PDF_PATH.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
