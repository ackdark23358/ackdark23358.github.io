# -*- coding: utf-8 -*-
"""요약 마크다운과 원본 텍스트로 대시보드용 data.js, 소스 JSON, 히어로 목록을 만든다."""
from __future__ import annotations

import hashlib
import json
import re
import shutil
from pathlib import Path
from urllib.parse import unquote

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
KEY_MASK = "142857"

_SECRET_PATTERNS = [
    # Google API Key
    re.compile(r"AIza[0-9A-Za-z\-_]{35}"),
    # OpenAI API Key
    re.compile(r"sk-[a-zA-Z0-9_\-]{20,}"),
    # Anthropic API Key
    re.compile(r"sk-ant-[a-zA-Z0-9_\-]{20,}"),
    # GitHub Token
    re.compile(r"(?:ghp|gho|ghu|ghs|ghr)_[a-zA-Z0-9]{36}|github_pat_[a-zA-Z0-9_]{50,}"),
    # AWS Access Key
    re.compile(r"(?:AKIA|ABIA|ACCA|ASIA)[0-9A-Z]{16}"),
    # Slack Token
    re.compile(r"xox[baprs]-[0-9a-zA-Z]{10,}"),
    # Firebase FCM device registration token
    re.compile(r"[a-zA-Z0-9_\-]{15,}:APA91b[a-zA-Z0-9_\-]{50,}"),
]

_KEY_ASSIGNMENT_PATTERNS = [
    re.compile(
        r'(?i)((?:api[_-]?key|client[_-]?secret|secret[_-]?key|access[_-]?token|service[_-]?key)\s*[:=]\s*["\'])([a-zA-Z0-9_\-\.\%\+\=]{16,})(["\'])'
    ),
    re.compile(
        r'(?i)((?:android:name=["\']com\.google\.android\.maps\.v2\.API_KEY["\']\s+android:value=["\']))([^"\']+)(["\'])'
    ),
]


def mask_secrets(text: str, mask: str = KEY_MASK) -> str:
    """본문에서 API 키·토큰 패턴을 찾아 고정 마스크 문자열로 바꾼다."""
    if not text:
        return text
    for pat in _SECRET_PATTERNS:
        text = pat.sub(mask, text)
    for pat in _KEY_ASSIGNMENT_PATTERNS:
        text = pat.sub(rf"\g<1>{mask}\g<3>", text)
    return text

_SOURCE_HREF_RE = re.compile(
    r'<a href="(/(?:data|_extracted)/[^"]+)"([^>]*)>',
    re.I,
)


def is_assignment_path(rel_path: str) -> bool:
    """경로에 과제 폴더 이름이 있으면 참을 돌려준다."""
    return _ASSIGNMENT_DIR in rel_path.replace("\\", "/")


def mask_assignment_privacy(text: str) -> str:
    """과제 본문의 지도교수 이름, 학번, 파일명 속 학번 숫자를 가린다."""
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
    """마크다운 앞의 YAML 프론트매터를 딕셔너리와 본문으로 나눈다. 태그 목록과 sources도 읽는다."""
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
    """요약 마크다운 본문을 HTML로 바꾼다. markdown 패키지가 없으면 제목·목록·문단만 직접 변환한다."""
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
    """HTML에 넣을 문자열의 &, <, >, 따옴표를 이스케이프한다."""
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _inline_md(s: str) -> str:
    """한 줄 안의 굵게, 코드, 사이트 내부 링크를 HTML로 바꾼다."""
    s = _esc(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(
        r"\[([^\]]+)\]\((/[^)]+)\)",
        r'<a href="\2">\1</a>',
        s,
    )
    return s


def normalize_source_key(key: str) -> str:
    """마크다운 링크의 퍼센트 인코딩을 풀어 디스크의 원본 경로와 같게 만든다."""
    k = key.replace("\\", "/").lstrip("/")
    prev = None
    while prev != k:
        prev = k
        k = unquote(k)
    return k


def rewrite_source_links(html: str, pending: set[str]) -> str:
    """본문 HTML의 /data, /_extracted 링크를 원본 보기용 data-source 앵커로 바꾸고, 필요한 원본 키를 모은다."""
    def repl(m: re.Match) -> str:
        """링크 하나에서 원본 키를 꺼내 pending에 넣고, source-link 클래스가 있는 앵커로 바꾼다."""
        href = m.group(1)
        key = normalize_source_key(href)
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
    """원본 키를 output/_extracted 또는 저장소 data 아래의 실제 파일 경로로 바꾼다."""
    key = normalize_source_key(key)
    if key.startswith("_extracted/"):
        return OUT / key
    if key.startswith("data/"):
        return ROOT / key
    return None


def read_text_file(path: Path) -> str:
    """utf-8, utf-8-sig, cp949 순으로 읽고, 실패하면 깨진 글자를 대체해 utf-8로 읽는다."""
    for enc in ("utf-8", "utf-8-sig", "cp949"):
        try:
            return path.read_text(encoding=enc)
        except (UnicodeDecodeError, OSError):
            continue
    return path.read_text(encoding="utf-8", errors="replace")


def read_source_text(key: str) -> str | None:
    """원본 키의 파일을 읽어 비밀 값을 가리고, 과제면 개인정보도 가린 뒤 돌려준다. 파일이 없으면 None이다."""
    path = resolve_source_path(key)
    if not path or not path.is_file():
        return None
    try:
        text = read_text_file(path)
    except OSError:
        return None
    text = mask_secrets(text)
    if is_assignment_path(key):
        text = mask_assignment_privacy(text)
    return text


def collect_hero_images() -> list[str]:
    """data/image의 이미지 파일을 정렬해 대시보드에서 쓰는 상대 경로 목록으로 만든다."""
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
    """히어로 이미지 경로를 window.HERO_IMAGES 대입문으로 hero-images.js에 쓰고 개수를 돌려준다."""
    images = collect_hero_images()
    content = "window.HERO_IMAGES = " + json.dumps(images, ensure_ascii=False) + ";\n"
    (js_dir / "hero-images.js").write_text(content, encoding="utf-8")
    return len(images)


def source_chunk_filename(key: str, text: str) -> str:
    """원본 키와 본문 해시로 sources 폴더에 저장할 JSON 파일 이름을 만든다."""
    key_digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:8]
    content_digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:8]
    return f"{key_digest}-{content_digest}.json"


def source_build_id(source_map: dict[str, str]) -> str:
    """원본 지도 전체를 해시해 캐시 무효화에 쓰는 짧은 빌드 아이디를 만든다."""
    payload = "|".join(f"{k}:{v}" for k, v in sorted(source_map.items()))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]


def stamp_index_scripts(build_id: str) -> None:
    """대시보드 index.html의 data.js, app.js 주소에 빌드 아이디 쿼리를 붙인다."""
    index_path = SITE / "index.html"
    html = index_path.read_text(encoding="utf-8")
    html = re.sub(
        r'src="js/(data|app)\.js(?:\?[^"]*)?"',
        lambda m: f'src="js/{m.group(1)}.js?v={build_id}"',
        html,
    )
    index_path.write_text(html, encoding="utf-8")


def assert_under_github_limit(path: Path, label: str) -> None:
    """파일 크기가 GitHub 한 파일 한도를 넘으면 빌드를 중단한다."""
    size = path.stat().st_size
    if size > GITHUB_MAX_BYTES:
        mb = size / (1024 * 1024)
        raise SystemExit(
            f"{label} ({path}) is {mb:.1f} MB — exceeds GitHub 100 MB file limit."
        )


def collect_catalog(catalog_data: dict) -> list[dict]:
    """catalog.json 항목에서 카드에 필요한 id, 종류, 제목, 슬러그, 요약, 태그만 고른다."""
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
    """요약 HTML, 원본 JSON, data.js, 히어로 목록을 dashboard에 쓴다. catalog.json이 없으면 중단한다."""
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
        html = md_to_html(mask_secrets(body))
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
        chunk_name = source_chunk_filename(key, text)
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

    build_id = source_build_id(source_map)
    site_data = {
        "catalog": catalog,
        "articles": articles,
        "sourceMap": source_map,
        "sourceBuildId": build_id,
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
    stamp_index_scripts(build_id)
    hero_count = write_hero_images_js(js_dir)

    print(f"Static data: {len(catalog)} items, {written_sources} source chunks")
    print(f"Wrote {data_js_path} ({data_js_path.stat().st_size // 1024} KB)")
    print(
        f"Wrote {sources_dir} ({written_sources} files, "
        f"{sources_total_bytes // 1024} KB total)"
    )
    print(f"Wrote {js_dir / 'hero-images.js'} ({hero_count} hero images)")


def main() -> None:
    """build_site를 실행하고, 만든 대시보드를 브라우저에서 열 수 있다고 안내한다."""
    build_site()
    print("Done. Open dashboard/index.html in a browser (or use a local static server).")


if __name__ == "__main__":
    main()
