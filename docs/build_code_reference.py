# -*- coding: utf-8 -*-
"""소스 주석을 읽어 코드 설명 마크다운과 PDF를 만든다."""
from __future__ import annotations

import ast
import html
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = Path(__file__).resolve().parent
MD_PATH = DOCS / "code-reference.md"
HTML_PATH = DOCS / "code-reference.html"
PDF_PATH = DOCS / "code-reference.pdf"

ID_RE = re.compile(r"\d{7,8}")
NAME_RE = re.compile("김신욱")


def mask_privacy(text: str) -> str:
    """파일 목록에 섞인 학번과 이름을 가린다."""
    text = ID_RE.sub("OOOOOOOO", text)
    return NAME_RE.sub("OOO", text)


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


class Doc:
    def __init__(self) -> None:
        self.blocks: list[tuple] = []

    def h1(self, text: str) -> None:
        self.blocks.append(("h1", text))

    def h2(self, text: str) -> None:
        self.blocks.append(("h2", text))

    def h3(self, text: str) -> None:
        self.blocks.append(("h3", text))

    def h4(self, text: str) -> None:
        self.blocks.append(("h4", text))

    def p(self, text: str) -> None:
        self.blocks.append(("p", text))

    def ul(self, items: list[str]) -> None:
        self.blocks.append(("ul", items))

    def code(self, text: str) -> None:
        self.blocks.append(("code", text))

    def render_md(self) -> str:
        out: list[str] = []
        for kind, payload in self.blocks:
            if kind == "h1":
                out.append(f"# {payload}\n")
            elif kind == "h2":
                out.append(f"\n## {payload}\n")
            elif kind == "h3":
                out.append(f"\n### {payload}\n")
            elif kind == "h4":
                out.append(f"\n#### {payload}\n")
            elif kind == "p":
                out.append(payload + "\n")
            elif kind == "ul":
                out.extend(f"- {item}" for item in payload)
                out.append("")
            elif kind == "code":
                out.append("```")
                out.append(payload)
                out.append("```\n")
        return "\n".join(out).strip() + "\n"

    def render_html(self) -> str:
        parts = [
            "<!DOCTYPE html>",
            '<html lang="ko">',
            "<head>",
            '<meta charset="utf-8" />',
            "<title>코드 설명</title>",
            "<style>",
            HTML_CSS,
            "</style>",
            "</head>",
            "<body>",
        ]
        first_h2 = True
        for kind, payload in self.blocks:
            if kind == "h1":
                parts.append(f"<h1>{html.escape(payload)}</h1>")
            elif kind == "h2":
                cls = "first" if first_h2 else ""
                first_h2 = False
                parts.append(f'<h2 class="{cls}">{html.escape(payload)}</h2>')
            elif kind == "h3":
                parts.append(f"<h3>{html.escape(payload)}</h3>")
            elif kind == "h4":
                parts.append(f"<h4>{html.escape(payload)}</h4>")
            elif kind == "p":
                parts.append(f"<p>{inline_html(payload)}</p>")
            elif kind == "ul":
                items = "".join(f"<li>{inline_html(item)}</li>" for item in payload)
                parts.append(f"<ul>{items}</ul>")
            elif kind == "code":
                parts.append(f"<pre>{html.escape(payload)}</pre>")
        parts.append("</body></html>")
        return "\n".join(parts)


HTML_CSS = """
@page { margin: 18mm 16mm; }
body { font-family: "Malgun Gothic", sans-serif; font-size: 11pt; line-height: 1.55; color: #1c1c1c; }
h1 { font-size: 22pt; margin: 0 0 0.6em; }
h2 { font-size: 16pt; margin: 1.4em 0 0.4em; page-break-before: always; }
h2.first { page-break-before: auto; }
h3 { font-size: 13pt; margin: 1.1em 0 0.3em; page-break-after: avoid; }
h4 { font-size: 11.5pt; margin: 0.9em 0 0.25em; page-break-after: avoid; }
p, li { orphans: 3; widows: 3; }
ul { margin: 0.2em 0 0.8em; padding-left: 1.2em; }
code { font-family: Consolas, "Malgun Gothic", monospace; font-size: 9.5pt; }
pre { font-family: Consolas, "Malgun Gothic", monospace; font-size: 9.5pt; background: #f3f3f3;
      padding: 8px 10px; white-space: pre-wrap; page-break-inside: avoid; }
"""

INLINE_CODE = re.compile(r"`([^`]+)`")
BOLD = re.compile(r"\*\*(.+?)\*\*")


def inline_html(text: str) -> str:
    escaped = html.escape(text)
    escaped = INLINE_CODE.sub(lambda m: f"<code>{m.group(1)}</code>", escaped)
    escaped = BOLD.sub(lambda m: f"<strong>{m.group(1)}</strong>", escaped)
    return escaped


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def jsdoc_before(lines: list[str], index: int) -> str:
    if index == 0 or lines[index - 1].strip() != "*/":
        return ""
    start = index - 1
    while start >= 0 and "/**" not in lines[start]:
        start -= 1
    if start < 0:
        return ""
    chunk = "\n".join(lines[start:index])
    body_lines = []
    for line in chunk.splitlines():
        line = re.sub(r"^\s*/?\*+/?\s?", "", line).strip()
        if line in ("/**", "*/", "*"):
            continue
        if line:
            body_lines.append(line)
    return "\n".join(body_lines).strip()


def split_jsdoc(doc: str) -> tuple[str, list[str], str]:
    desc: list[str] = []
    params: list[str] = []
    returns = ""
    for line in doc.splitlines():
        param = re.match(r"@param\s+\{([^}]+)\}\s+(\S+)\s*(.*)", line)
        ret = re.match(r"@returns?\s+\{([^}]+)\}\s*(.*)", line)
        if param:
            extra = f" {param.group(3)}".rstrip()
            params.append(f"{param.group(2)}: {param.group(1)}{extra}")
        elif ret:
            extra = f" {ret.group(2)}".rstrip()
            returns = f"{ret.group(1)}{extra}"
        elif not line.startswith("@"):
            desc.append(line)
    return " ".join(desc).strip(), params, returns


def clip_expr(text: str, limit: int = 72) -> str:
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "…"


def py_expr(node: ast.AST | None) -> str:
    if node is None:
        return ""
    try:
        return clip_expr(ast.unparse(node))
    except Exception:
        return "식"


def append_py_stmt(stmt: ast.AST, depth: int, lines: list[str], limit: int) -> None:
    if len(lines) >= limit:
        return
    pad = "  " * depth
    if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant) and isinstance(stmt.value.value, str):
        return
    if isinstance(stmt, ast.Pass):
        return
    if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        lines.append(f"{pad}{stmt.name} 을 정의한다")
        return
    if isinstance(stmt, ast.Return):
        value = py_expr(stmt.value)
        lines.append(f"{pad}반환 {value}" if value else f"{pad}반환")
        return
    if isinstance(stmt, ast.Assign):
        targets = ", ".join(py_expr(target) for target in stmt.targets)
        lines.append(f"{pad}{targets} ← {py_expr(stmt.value)}")
        return
    if isinstance(stmt, ast.AnnAssign):
        if stmt.value is not None:
            lines.append(f"{pad}{py_expr(stmt.target)} ← {py_expr(stmt.value)}")
        else:
            lines.append(f"{pad}필드 {py_expr(stmt.target)}")
        return
    if isinstance(stmt, ast.AugAssign):
        lines.append(f"{pad}{py_expr(stmt.target)} ← {py_expr(stmt.target)} 연산 {py_expr(stmt.value)}")
        return
    if isinstance(stmt, ast.If):
        lines.append(f"{pad}만약 {py_expr(stmt.test)}")
        for child in stmt.body:
            append_py_stmt(child, depth + 1, lines, limit)
        if stmt.orelse:
            lines.append(f"{pad}아니면")
            for child in stmt.orelse:
                append_py_stmt(child, depth + 1, lines, limit)
        return
    if isinstance(stmt, ast.For):
        lines.append(f"{pad}반복 {py_expr(stmt.target)} ← {py_expr(stmt.iter)}")
        for child in stmt.body:
            append_py_stmt(child, depth + 1, lines, limit)
        return
    if isinstance(stmt, ast.While):
        lines.append(f"{pad}동안 {py_expr(stmt.test)}")
        for child in stmt.body:
            append_py_stmt(child, depth + 1, lines, limit)
        return
    if isinstance(stmt, ast.With):
        heads = ", ".join(py_expr(item.context_expr) for item in stmt.items)
        lines.append(f"{pad}범위 {heads}")
        for child in stmt.body:
            append_py_stmt(child, depth + 1, lines, limit)
        return
    if isinstance(stmt, ast.Try):
        lines.append(f"{pad}시도")
        for child in stmt.body:
            append_py_stmt(child, depth + 1, lines, limit)
        for handler in stmt.handlers:
            label = py_expr(handler.type) if handler.type else "예외"
            lines.append(f"{pad}실패 {label}")
            for child in handler.body:
                append_py_stmt(child, depth + 1, lines, limit)
        return
    if isinstance(stmt, ast.Raise):
        lines.append(f"{pad}중단 {py_expr(stmt.exc)}".rstrip())
        return
    if isinstance(stmt, ast.Continue):
        lines.append(f"{pad}다음 반복")
        return
    if isinstance(stmt, ast.Break):
        lines.append(f"{pad}반복 종료")
        return
    if isinstance(stmt, ast.Delete):
        lines.append(f"{pad}삭제 {', '.join(py_expr(target) for target in stmt.targets)}")
        return
    if isinstance(stmt, (ast.Import, ast.ImportFrom)):
        lines.append(f"{pad}모듈을 불러온다")
        return
    try:
        lines.append(f"{pad}{clip_expr(ast.unparse(stmt))}")
    except Exception:
        lines.append(f"{pad}문장을 실행한다")


def py_pseudocode(node: ast.AST) -> str:
    lines: list[str] = []
    if isinstance(node, ast.ClassDef):
        lines.append(f"클래스 {node.name}")
        for stmt in node.body:
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant):
                continue
            if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
                lines.append(f"  메서드 {stmt.name}")
            elif isinstance(stmt, ast.AnnAssign):
                lines.append(f"  필드 {py_expr(stmt.target)}")
            elif isinstance(stmt, ast.Assign):
                targets = ", ".join(py_expr(target) for target in stmt.targets)
                lines.append(f"  {targets} ← {py_expr(stmt.value)}")
            else:
                append_py_stmt(stmt, 1, lines, 40)
        return "\n".join(lines)
    for stmt in getattr(node, "body", []):
        append_py_stmt(stmt, 0, lines, 40)
    if len(lines) >= 40:
        lines.append("…")
    return "\n".join(lines) if lines else "수행할 문장이 없다"


def js_body_lines(lines: list[str], index: int) -> list[str]:
    blob = "\n".join(lines[index:])
    start = blob.find("{")
    if start < 0:
        return []
    depth = 0
    end = start
    for pos in range(start, len(blob)):
        char = blob[pos]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                end = pos
                break
    body = blob[start + 1 : end]
    return body.splitlines()


def js_pseudocode(lines: list[str], index: int) -> str:
    body = js_body_lines(lines, index)
    out: list[str] = []
    depth = 0
    skipping = False
    skip_depth = 0
    for raw in body:
        if len(out) >= 40:
            break
        line = raw.strip()
        if not line or line.startswith("//") or line.startswith("/*") or line.startswith("*"):
            if "{" in line or "}" in line:
                pass
            else:
                continue
        if skipping:
            skip_depth += line.count("{") - line.count("}")
            if skip_depth <= 0:
                skipping = False
            continue
        nested = re.match(r"function\s+(\w+)\s*\(", line)
        if nested:
            out.append(f"{'  ' * depth}{nested.group(1)} 을 정의한다")
            skip_depth = line.count("{") - line.count("}")
            if skip_depth > 0:
                skipping = True
            continue
        open_count = line.count("{")
        close_count = line.count("}")
        code = re.sub(r"\s*\{\s*$", "", line).rstrip(";").strip()
        if re.match(r"\}?\s*else\s+if\b", code):
            code = re.sub(r"^\}?\s*", "", code)
        elif re.match(r"\}?\s*else\b", code):
            code = "else"
        pad = "  " * depth
        if code.startswith("if ("):
            out.append(f"{pad}만약 {clip_expr(code[3:].strip(' ()'))}")
        elif code.startswith("} else if (") or code.startswith("else if ("):
            cond = code.split("(", 1)[1].rsplit(")", 1)[0]
            out.append(f"{pad}아니면 만약 {clip_expr(cond)}")
        elif code in ("else", "} else"):
            out.append(f"{pad}아니면")
        elif code.startswith("for ") or code.startswith("for("):
            out.append(f"{pad}반복 {clip_expr(code)}")
        elif code.startswith("while"):
            out.append(f"{pad}동안 {clip_expr(code)}")
        elif code.startswith("return"):
            value = code[6:].strip()
            out.append(f"{pad}반환 {clip_expr(value)}" if value else f"{pad}반환")
        elif re.match(r"(?:var|let|const)\s+", code):
            out.append(f"{pad}{clip_expr(re.sub(r'^(?:var|let|const)\s+', '', code).replace(' = ', ' ← ', 1))}")
        elif code.startswith("try"):
            out.append(f"{pad}시도")
        elif code.startswith("catch"):
            out.append(f"{pad}실패")
        elif code.startswith("throw"):
            out.append(f"{pad}중단 {clip_expr(code[5:].strip())}")
        elif code and not re.fullmatch(r"[\s{}\[\]();,]+", code):
            out.append(f"{pad}{clip_expr(code)}")
        depth += open_count - close_count
        if depth < 0:
            depth = 0
    if len(out) >= 40:
        out.append("…")
    return "\n".join(out) if out else "수행할 문장이 없다"


def parse_js(path: Path) -> tuple[str, list[dict]]:
    lines = read_text(path).splitlines()
    file_doc = ""
    if lines and lines[0].strip().startswith("/**"):
        end = 0
        while end < len(lines) and "*/" not in lines[end]:
            end += 1
        file_doc = jsdoc_before(lines, end + 1)
    symbols = []
    for index, line in enumerate(lines):
        match = re.match(r"\s*function\s+(\w+)\s*\(([^)]*)\)", line)
        if not match:
            continue
        doc = jsdoc_before(lines, index)
        desc, params, returns = split_jsdoc(doc)
        if not params and match.group(2).strip():
            params = [part.strip() for part in match.group(2).split(",") if part.strip()]
        symbols.append(
            {
                "name": match.group(1),
                "signature": f"function {match.group(1)}({match.group(2).strip()})",
                "line": index + 1,
                "desc": desc,
                "params": params,
                "returns": returns,
                "pseudo": js_pseudocode(lines, index),
            }
        )
    return file_doc, symbols


def annotation(node: ast.AST | None) -> str:
    if node is None:
        return ""
    return ast.unparse(node)


def py_params(node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[str]:
    args = node.args
    names: list[ast.arg] = list(args.posonlyargs) + list(args.args)
    default_start = len(names) - len(args.defaults)
    parts: list[str] = []
    for index, arg in enumerate(names):
        if arg.arg in ("self", "cls"):
            continue
        label = arg.arg
        ann = annotation(arg.annotation)
        if ann:
            label += f": {ann}"
        if index >= default_start:
            default = ast.unparse(args.defaults[index - default_start])
            label += f" = {default}"
        parts.append(label)
    if args.vararg:
        label = "*" + args.vararg.arg
        ann = annotation(args.vararg.annotation)
        parts.append(f"{label}: {ann}" if ann else label)
    for arg, default in zip(args.kwonlyargs, args.kw_defaults):
        label = arg.arg
        ann = annotation(arg.annotation)
        if ann:
            label += f": {ann}"
        if default is not None:
            label += f" = {ast.unparse(default)}"
        parts.append(label)
    if args.kwarg:
        label = "**" + args.kwarg.arg
        ann = annotation(args.kwarg.annotation)
        parts.append(f"{label}: {ann}" if ann else label)
    return parts


def py_signature(node: ast.AST) -> str:
    if isinstance(node, ast.ClassDef):
        bases = ", ".join(ast.unparse(base) for base in node.bases)
        return f"class {node.name}({bases})" if bases else f"class {node.name}"
    assert isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
    ret = annotation(node.returns)
    tail = f" -> {ret}" if ret else ""
    return f"{prefix} {node.name}({ast.unparse(node.args)}){tail}"


def iter_py_symbols(node: ast.AST, prefix: str = ""):
    for child in getattr(node, "body", []):
        if isinstance(child, ast.ClassDef):
            name = f"{prefix}{child.name}"
            yield name, child
            yield from iter_py_symbols(child, name + ".")
        elif isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
            name = f"{prefix}{child.name}"
            yield name, child
            yield from iter_py_symbols(child, name + ".")


def parse_py(path: Path) -> tuple[str, list[dict]]:
    tree = ast.parse(read_text(path))
    file_doc = ast.get_docstring(tree) or ""
    symbols = []
    for name, node in iter_py_symbols(tree):
        desc = ast.get_docstring(node) or ""
        params: list[str] = []
        returns = ""
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            params = py_params(node)
            returns = annotation(node.returns)
        symbols.append(
            {
                "name": name,
                "signature": py_signature(node),
                "line": node.lineno,
                "desc": " ".join(desc.split()),
                "params": params,
                "returns": returns,
                "pseudo": py_pseudocode(node),
            }
        )
    return file_doc, symbols


CODE_SUFFIXES = {
    ".vb",
    ".html",
    ".htm",
    ".js",
    ".css",
    ".py",
    ".cs",
    ".java",
    ".c",
    ".cpp",
    ".h",
    ".config",
    ".vbproj",
    ".sln",
    ".resx",
    ".settings",
    ".suo",
    ".user",
}


def file_comment(path: Path) -> str:
    text = read_text(path)
    if path.suffix.lower() == ".html":
        match = re.match(r"<!--\s*(.*?)\s*-->", text, re.S)
        return " ".join(match.group(1).split()) if match else ""
    if path.suffix.lower() == ".css":
        if text.startswith("@charset"):
            text = text.split("\n", 1)[1]
        match = re.search(r"/\*\s*(.*?)\s*\*/", text, re.S)
        return " ".join(match.group(1).split()) if match else ""
    return ""


def add_symbol(doc: Doc, path: Path, symbol: dict) -> None:
    doc.h4(symbol["name"])
    doc.p(f"`{rel(path)}:{symbol['line']}`")
    doc.code(symbol["signature"])
    doc.p(symbol["desc"] or "설명이 없습니다.")
    params = symbol["params"] or ["없음"]
    doc.ul([f"인자: {', '.join(params)}", f"반환: {symbol['returns'] or '없음'}"])
    pseudo = symbol.get("pseudo") or ""
    if pseudo:
        doc.p("유사코드")
        doc.code(pseudo)


def add_code_file(doc: Doc, path: Path, file_doc: str, symbols: list[dict]) -> None:
    doc.h3(rel(path))
    if file_doc:
        doc.p(file_doc)
    for symbol in symbols:
        add_symbol(doc, path, symbol)


def data_role(path: Path) -> str:
    name = path.name
    suffix = path.suffix.lower()
    if suffix in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"}:
        return "학습·과제 화면 캡처 또는 도표"
    if "과제분류하기" in path.parts:
        return "과제 제출 원본"
    if "독서" in name:
        return "독서 노트"
    if "수강" in name or "영상" in name:
        return "수강 노트"
    if suffix == ".hwpx":
        return "한글 문서 원본. 요약 빌드에서는 제외한다"
    return "학습 기록 원본"


def is_generated_data(path: Path) -> bool:
    parts = set(path.parts)
    if parts & {"obj", "bin", "My Project"}:
        return True
    if path.name.endswith(".Designer.vb"):
        return True
    if path.suffix.lower() in {".exe", ".dll", ".pdb", ".cache", ".suo", ".user"}:
        return True
    return False


def collect_originals() -> dict[str, list[str]]:
    data = ROOT / "study_note_record_organization" / "data"
    grouped: dict[str, list[str]] = {}
    if not data.is_dir():
        return grouped
    for path in sorted(data.rglob("*")):
        if not path.is_file() or is_generated_data(path):
            continue
        if ".vs" in path.parts or path.suffix.lower() in CODE_SUFFIXES:
            continue
        label = mask_privacy(f"{rel(path)} — {data_role(path)}")
        grouped.setdefault(path.suffix.lower() or "(확장자 없음)", []).append(label)
    return grouped


def build() -> Doc:
    doc = Doc()
    doc.h1("코드 설명")
    doc.p(
        "이력서, 자기소개, 온라인 명함, 학습 기록 대시보드와 그 빌드 스크립트를 함수·클래스 단위로 정리한 문서다. "
        "설명은 소스 주석에서 뽑았고, 함수가 없는 파일은 파일 역할만 적었다."
    )

    doc.h2("프로젝트 구성")
    doc.p(
        "루트는 취업 지원용 포트폴리오 페이지다. 이력서, 자기소개, 명함은 각각 폴더로 나뉘고, "
        "학습 노트와 과제 원본은 study_note_record_organization 안에 있다. "
        "그 폴더의 파이썬 스크립트가 원본을 요약 마크다운으로 바꾸고, 대시보드가 읽는 data.js와 원본 JSON을 만든다."
    )
    doc.ul(
        [
            "index.html, css/, js/main.js — 메인 포트폴리오",
            "cv/ — 이력서",
            "cover_letter/ — 자기소개",
            "online_business_card/ — 스크롤 명함",
            "study_note_record_organization/dashboard/ — 학습·과제 카드 화면",
            "portfolio_achieve/ — 프로젝트 아카이브 (PROJ_01~PROJ_17)",
            "study_note_record_organization/scripts/ — 요약과 정적 데이터 빌드",
            "study_note_record_organization/data/ — 노트, 과제, 이미지 원본",
        ]
    )

    doc.h2("디렉터리 지도")
    doc.ul(
        [
            "css/ — 메인 페이지와 공통 헤더 스타일",
            "js/ — 메인 페이지 내비게이션, 테마 및 리소스 보호(protect-resources.js)",
            "cv/css, cv/js — 이력서 스타일과 재직 기간 계산",
            "cover_letter/css, cover_letter/js — 자기소개 스타일과 스크롤 메뉴",
            "online_business_card/css, online_business_card/js — 명함 애니메이션",
            "study_note_record_organization/dashboard/js — 카드, 검색, 히어로. data.js와 sources는 생성물",
            "portfolio_achieve/ — 프로젝트 아카이브(PROJ_01~PROJ_17 메타 카드), 스타일(archive.css) 및 스크립트(site.js)",
            "study_note_record_organization/scripts — build_output.py, build_static_site.py, extract_sources.py",
            "study_note_record_organization/output — 빌드가 쓰는 요약 마크다운과 catalog.json",
            "study_note_record_organization/data/과제분류하기 — 과제 문서 원본. 코드 파일은 이 문서에서 빼 둔다",
            "docs/ — 기술명세서, 코드북, 코드 설명, 소스 번들, 포트폴리오 북 빌드 스크립트",
        ]
    )

    sections = [
        (
            "메인 사이트 및 보안 가드",
            [
                ROOT / "index.html",
                ROOT / "css" / "styles.css",
                ROOT / "css" / "site-header.css",
                ROOT / "js" / "main.js",
                ROOT / "js" / "protect-resources.js",
            ],
        ),
        (
            "이력서",
            [
                ROOT / "cv" / "resume.html",
                ROOT / "cv" / "css" / "reset.css",
                ROOT / "cv" / "css" / "style.css",
                ROOT / "cv" / "js" / "ui.js",
            ],
        ),
        (
            "자기소개서",
            [
                ROOT / "cover_letter" / "profile.html",
                ROOT / "cover_letter" / "css" / "styles.css",
                ROOT / "cover_letter" / "js" / "script.js",
            ],
        ),
        (
            "명함",
            [
                ROOT / "online_business_card" / "business-card.html",
                ROOT / "online_business_card" / "css" / "style.css",
                ROOT / "online_business_card" / "js" / "script.js",
            ],
        ),
        (
            "학습 기록 대시보드",
            [
                ROOT / "study_note_record_organization" / "dashboard" / "index.html",
                ROOT / "study_note_record_organization" / "dashboard" / "css" / "styles.css",
                ROOT / "study_note_record_organization" / "dashboard" / "js" / "app.js",
                ROOT / "study_note_record_organization" / "dashboard" / "js" / "hero.js",
            ],
        ),
        (
            "프로젝트 아카이브",
            [
                ROOT / "portfolio_achieve" / "index.html",
                ROOT / "portfolio_achieve" / "css" / "archive.css",
                ROOT / "portfolio_achieve" / "js" / "site.js",
            ],
        ),
    ]

    for title, paths in sections:
        doc.h2(title)
        for path in paths:
            suffix = path.suffix.lower()
            if suffix == ".js":
                file_doc, symbols = parse_js(path)
                add_code_file(doc, path, file_doc, symbols)
            else:
                doc.h3(rel(path))
                doc.p(file_comment(path) or "파일 역할 주석이 없습니다.")

    doc.h2("빌드 스크립트")
    doc.p(
        "scripts 폴더와 docs 폴더의 파이썬 스크립트가 학습 원본 요약, 대시보드 데이터 갱신, 기술문서 및 포트폴리오 북 생성을 맡는다. "
        "아래 설명은 각 함수와 클래스 독스트링이다."
    )
    for path in [
        ROOT / "study_note_record_organization" / "scripts" / "extract_sources.py",
        ROOT / "study_note_record_organization" / "scripts" / "build_output.py",
        ROOT / "study_note_record_organization" / "scripts" / "build_static_site.py",
        DOCS / "build_portfolio_book.py",
    ]:
        file_doc, symbols = parse_py(path)
        add_code_file(doc, path, file_doc, symbols)

    doc.h2("생성 산출물")
    doc.p(
        "다음 파일은 사람이 함수를 적어 둔 소스가 아니다. "
        "build_static_site.py를 다시 실행하면 data.js, hero-images.js, sources JSON의 본문이 바뀌므로 그 안에 설명 주석을 넣지 않았다."
    )
    sources = ROOT / "study_note_record_organization" / "dashboard" / "js" / "sources"
    source_count = len(list(sources.glob("*.json"))) if sources.is_dir() else 0
    doc.ul(
        [
            "study_note_record_organization/dashboard/js/data.js — 카드 목록, 요약 HTML, 원본 파일 지도를 window.SITE_DATA로 넣는다.",
            "study_note_record_organization/dashboard/js/hero-images.js — data/image 경로를 window.HERO_IMAGES 배열로 넣는다.",
            f"study_note_record_organization/dashboard/js/sources/*.json — 원본 텍스트 {source_count}개. 키와 본문만 담는다.",
        ]
    )

    doc.h2("학습 원본 파일 목록")
    doc.p(
        "data 폴더의 노트, 과제 문서, 이미지다. 함수가 없어 파일마다 한 줄만 적는다. "
        "코드 파일은 넣지 않았고, 원문 전문도 넣지 않았다. 학번과 이름은 가렸다."
    )
    grouped = collect_originals()
    if not grouped:
        doc.p("목록에 넣을 원본 파일이 없습니다.")
    for suffix in sorted(grouped):
        doc.h3(suffix)
        doc.ul(grouped[suffix])
    return doc


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
    profile = Path(tempfile.mkdtemp(prefix="code-ref-pdf-"))
    url = html_path.resolve().as_uri()
    command = [
        str(browser),
        "--headless=new",
        "--disable-gpu",
        "--no-first-run",
        "--no-pdf-header-footer",
        f"--user-data-dir={profile}",
        f"--print-to-pdf={pdf_path.resolve()}",
        url,
    ]
    try:
        subprocess.run(command, check=True, timeout=120)
    finally:
        shutil.rmtree(profile, ignore_errors=True)
    if not pdf_path.is_file() or pdf_path.stat().st_size < 1000:
        raise SystemExit(f"PDF가 만들어지지 않았습니다: {pdf_path}")


def main() -> None:
    doc = build()
    MD_PATH.write_text(doc.render_md(), encoding="utf-8")
    HTML_PATH.write_text(doc.render_html(), encoding="utf-8")
    write_pdf(HTML_PATH, PDF_PATH)
    print(f"Wrote {MD_PATH}")
    print(f"Wrote {HTML_PATH}")
    print(f"Wrote {PDF_PATH} ({PDF_PATH.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
