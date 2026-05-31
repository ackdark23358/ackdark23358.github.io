# -*- coding: utf-8 -*-
"""Build static HTML/CSS/JS dashboard (no Vite/npm runtime)."""
from __future__ import annotations

import hashlib
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"
SITE = ROOT / "dashboard"
HERO_IMAGE_DIR = ROOT / "data" / "image"
HERO_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}
CATALOG_PATH = OUT / "catalog.json"
GITHUB_MAX_BYTES = 100 * 1024 * 1024
_ASSIGNMENT_DIR = "과제분류하기"
PROFESSOR_MASK = "OOO 교수님"
STUDENT_ID_MASK = "OOOOOOOO"

_SOURCE_HREF_RE = re.compile(
    r'<a href="(/(?:data|_extracted)/[^"]+)"([^>]*)>',
    re.I,
)


def is_assignment_path(rel_path: str) -> bool:
    return _ASSIGNMENT_DIR in rel_path.replace("\\", "/")


def mask_assignment_privacy(text: str) -> str:
    if not text:
        return text
    text = re.sub(
        r"(지도교수\s*[:：]\s*)\S+(?:\s*교수님)?",
        rf"\1{PROFESSOR_MASK}",
        text,
    )
    text = re.sub(
        r"((?:학\s*번|수\s*강\s*번\s*호)\s*[:：]\s*)\d+",
        rf"\1{STUDENT_ID_MASK}",
        text,
    )
    text = re.sub(r"\(\d{7,8}\s+", f"({STUDENT_ID_MASK} ", text)
    text = re.sub(r"\(\d{7,8}\)", f"({STUDENT_ID_MASK})", text)
    text = re.sub(r"_\d{7,8}_", f"_{STUDENT_ID_MASK}_", text)
    return text


def parse_frontmatter(raw: str) -> tuple[dict, str]:
    match = re.match(r"^---\r?\n([\s\S]*?)\r?\n---\r?\n([\s\S]*)$", raw)
    if not match:
        return {}, raw
    yaml, body = match.group(1), match.group(2)
    meta: dict = {}
    current_key = None
    in_sources = False
    source_item = None

    for line in yaml.split("\n"):
        if line.strip().startswith("sources:"):
            in_sources = True
            meta["sources"] = []
            continue
        if in_sources:
            if re.match(r"^\s+-\s+path:", line):
                source_item = {"path": line.split("path:", 1)[1].strip()}
                meta["sources"].append(source_item)
            elif source_item and re.match(r"^\s+unit:", line):
                source_item["unit"] = (
                    line.split("unit:", 1)[1].strip().strip("\"'")
                )
            elif line.strip() and not line.startswith(" "):
                in_sources = False
        if not in_sources:
            m = re.match(r"^(\w+):\s*(.*)$", line)
            if m:
                current_key = m.group(1)
                val = m.group(2).strip().strip("\"'")
                meta[current_key] = val
            elif current_key == "tags" and re.match(r"^\s+-\s+", line):
                meta.setdefault("tags", [])
                meta["tags"].append(line.split("-", 1)[1].strip())
    if isinstance(meta.get("tags"), str) and meta["tags"].startswith("["):
        try:
            meta["tags"] = json.loads(meta["tags"].replace("'", '"'))
        except json.JSONDecodeError:
            meta["tags"] = []
    return meta, body


def md_to_html(body: str) -> str:
    try:
        import markdown

        return markdown.markdown(
            body,
            extensions=["extra", "nl2br", "sane_lists"],
            output_format="html5",
        )
    except ImportError:
        html = []
        for block in re.split(r"\n\n+", body.strip()):
            block = block.strip()
            if not block:
                continue
            if block.startswith("### "):
                html.append(f"<h3>{_esc(block[4:])}</h3>")
            elif block.startswith("## "):
                html.append(f"<h2>{_esc(block[3:])}</h2>")
            elif block.startswith("# "):
                html.append(f"<h1>{_esc(block[2:])}</h1>")
            elif block.startswith("- "):
                items = "".join(
                    f"<li>{_inline_md(line[2:])}</li>"
                    for line in block.split("\n")
                    if line.startswith("- ")
                )
                html.append(f"<ul>{items}</ul>")
            else:
                html.append(f"<p>{_inline_md(block.replace(chr(10), ' '))}</p>")
        return "\n".join(html)


def _esc(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _inline_md(s: str) -> str:
    s = _esc(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(
        r"\[([^\]]+)\]\((/[^)]+)\)",
        r'<a href="\2">\1</a>',
        s,
    )
    return s


def rewrite_source_links(html: str, pending: set[str]) -> str:
    def repl(m: re.Match) -> str:
        href = m.group(1)
        key = href.lstrip("/")
        pending.add(key)
        attrs = m.group(2) or ""
        if "class=" in attrs:
            attrs = re.sub(
                r'class="([^"]*)"',
                lambda cm: f'class="{cm.group(1)} source-link"',
                attrs,
                count=1,
            )
        else:
            attrs += ' class="source-link"'
        return f'<a href="#" data-source="{key}"{attrs}>'

    return _SOURCE_HREF_RE.sub(repl, html)


def resolve_source_path(key: str) -> Path | None:
    if key.startswith("_extracted/"):
        return OUT / key
    if key.startswith("data/"):
        return ROOT / key
    return None


def read_source_text(key: str) -> str | None:
    path = resolve_source_path(key)
    if not path or not path.is_file():
        return None
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    if is_assignment_path(key):
        text = mask_assignment_privacy(text)
    return text


def collect_hero_images() -> list[str]:
    if not HERO_IMAGE_DIR.is_dir():
        return []
    paths: list[str] = []
    for path in sorted(HERO_IMAGE_DIR.iterdir(), key=lambda p: p.name.lower()):
        if not path.is_file():
            continue
        if path.suffix.lower() not in HERO_IMAGE_EXTS:
            continue
        paths.append(f"../data/image/{path.name}")
    return paths


def write_hero_images_js(js_dir: Path) -> int:
    images = collect_hero_images()
    content = "window.HERO_IMAGES = " + json.dumps(images, ensure_ascii=False) + ";\n"
    (js_dir / "hero-images.js").write_text(content, encoding="utf-8")
    return len(images)


def source_chunk_filename(key: str) -> str:
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]
    return f"{digest}.json"


def assert_under_github_limit(path: Path, label: str) -> None:
    size = path.stat().st_size
    if size > GITHUB_MAX_BYTES:
        mb = size / (1024 * 1024)
        raise SystemExit(
            f"{label} ({path}) is {mb:.1f} MB — exceeds GitHub 100 MB file limit."
        )


def collect_catalog(catalog_data: dict) -> list[dict]:
    items = []
    for it in catalog_data.get("items", []):
        items.append(
            {
                "id": it["id"],
                "type": it["type"],
                "title": it["title"],
                "slug": it["slug"],
                "summary": it.get("summary", ""),
                "tags": it.get("tags") or [],
            }
        )
    return items


def build_site() -> None:
    if not CATALOG_PATH.is_file():
        raise SystemExit("catalog.json 없음. 먼저 python scripts/build_output.py 실행")

    catalog_data = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    catalog = collect_catalog(catalog_data)
    articles: dict[str, str] = {}
    pending_sources: set[str] = set()

    for item in catalog_data.get("items", []):
        md_path = ROOT / item["output"]
        if not md_path.is_file():
            continue
        raw = md_path.read_text(encoding="utf-8")
        _, body = parse_frontmatter(raw)
        html = md_to_html(body)
        html = rewrite_source_links(html, pending_sources)
        articles[item["slug"]] = html

    source_map: dict[str, str] = {}
    sources_dir = SITE / "js" / "sources"
    if sources_dir.is_dir():
        shutil.rmtree(sources_dir)
    sources_dir.mkdir(parents=True, exist_ok=True)

    written_sources = 0
    sources_total_bytes = 0
    for key in sorted(pending_sources):
        text = read_source_text(key)
        if text is None:
            continue
        chunk_name = source_chunk_filename(key)
        chunk_path = sources_dir / chunk_name
        chunk_payload = {"key": key, "text": text}
        chunk_path.write_text(
            json.dumps(chunk_payload, ensure_ascii=False),
            encoding="utf-8",
        )
        assert_under_github_limit(chunk_path, "Source chunk")
        source_map[key] = chunk_name
        written_sources += 1
        sources_total_bytes += chunk_path.stat().st_size

    site_data = {
        "catalog": catalog,
        "articles": articles,
        "sourceMap": source_map,
        "counts": catalog_data.get("counts", {}),
    }

    js_dir = SITE / "js"
    css_dir = SITE / "css"
    js_dir.mkdir(parents=True, exist_ok=True)
    css_dir.mkdir(parents=True, exist_ok=True)

    data_js_path = js_dir / "data.js"
    data_js = "window.SITE_DATA = " + json.dumps(site_data, ensure_ascii=False) + ";\n"
    data_js_path.write_text(data_js, encoding="utf-8")
    assert_under_github_limit(data_js_path, "data.js")
    hero_count = write_hero_images_js(js_dir)

    print(f"Static data: {len(catalog)} items, {written_sources} source chunks")
    print(f"Wrote {data_js_path} ({data_js_path.stat().st_size // 1024} KB)")
    print(
        f"Wrote {sources_dir} ({written_sources} files, "
        f"{sources_total_bytes // 1024} KB total)"
    )
    print(f"Wrote {js_dir / 'hero-images.js'} ({hero_count} hero images)")


def main() -> None:
    build_site()
    print("Done. Open dashboard/index.html in a browser (or use a local static server).")


if __name__ == "__main__":
    main()
