# -*- coding: utf-8 -*-
"""주석이 붙은 소스를 파일 단위로 이어 하나의 PDF로 만든다."""
from __future__ import annotations

import html
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = Path(__file__).resolve().parent
HTML_PATH = DOCS / "source-bundle.html"
PDF_PATH = DOCS / "source-bundle.pdf"

SUFFIXES = {".html", ".css", ".js", ".py"}
SKIP_DIRS = {
    "data",
    "output",
    "sources",
    "__pycache__",
    ".vs",
    "obj",
    "bin",
    "node_modules",
    "prtfolio_acheve_add_2026_10_16",
}
SKIP_FILES = {"data.js", "hero-images.js"}


def include(path: Path) -> bool:
    if path.suffix.lower() not in SUFFIXES:
        return False
    if path.name in SKIP_FILES or path.name.endswith(".min.js"):
        return False
    if any(part in SKIP_DIRS for part in path.parts):
        return False
    if DOCS in path.parents and path.suffix.lower() == ".html":
        return False
    return True


def source_files() -> list[Path]:
    files = [path for path in ROOT.rglob("*") if path.is_file() and include(path)]
    return sorted(files, key=lambda path: path.relative_to(ROOT).as_posix())


def file_block(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    width = max(len(str(len(lines))), 2)
    numbered = "\n".join(f"{index:>{width}}  {line}" for index, line in enumerate(lines, start=1))
    return f"<h2>{html.escape(rel)}</h2>\n<pre>{html.escape(numbered)}</pre>"


def render_html(blocks: list[str]) -> str:
    intro = (
        "<h1>소스 모음</h1>"
        "<p>화면과 빌드 소스를 파일 순서대로 이어 두었습니다. "
        "주석은 코드 옆에 그대로 있습니다. "
        "data/ 과제 코드, 압축된 라이브러리, 빌드가 만든 data.js, hero-images.js, sources JSON은 넣지 않았습니다.</p>"
    )
    css = """
@page { margin: 12mm 10mm; }
body { font-family: "Malgun Gothic", sans-serif; color: #1c1c1c; }
h1 { font-size: 18pt; margin: 0 0 0.4em; }
h2 { font-size: 12pt; margin: 1.2em 0 0.3em; page-break-before: always; page-break-after: avoid; }
h2:first-of-type { page-break-before: auto; }
p { font-size: 10.5pt; line-height: 1.5; }
pre { font-family: Consolas, "Malgun Gothic", monospace; font-size: 8pt; line-height: 1.35;
      white-space: pre-wrap; word-break: break-all; margin: 0; }
"""
    return "\n".join(
        [
            "<!DOCTYPE html>",
            '<html lang="ko">',
            "<head>",
            '<meta charset="utf-8" />',
            "<title>소스 모음</title>",
            "<style>",
            css,
            "</style>",
            "</head>",
            "<body>",
            intro,
            "\n".join(blocks),
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
    profile = Path(tempfile.mkdtemp(prefix="source-bundle-"))
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
        subprocess.run(command, check=True, timeout=180)
    finally:
        shutil.rmtree(profile, ignore_errors=True)
    if not pdf_path.is_file() or pdf_path.stat().st_size < 1000:
        raise SystemExit(f"PDF가 만들어지지 않았습니다: {pdf_path}")


def main() -> None:
    files = source_files()
    if not files:
        raise SystemExit("묶을 소스 파일이 없습니다.")
    HTML_PATH.write_text(render_html([file_block(path) for path in files]), encoding="utf-8")
    write_pdf(HTML_PATH, PDF_PATH)
    print(f"Files {len(files)}")
    print(f"Wrote {PDF_PATH} ({PDF_PATH.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
