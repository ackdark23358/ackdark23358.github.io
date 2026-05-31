# -*- coding: utf-8 -*-
"""Extract sources, build catalog, generate 53 markdown summaries (37 study + 16 assignment)."""
from __future__ import annotations

import json
import os
import re
import textwrap
from urllib.parse import quote
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ASSIGN = DATA / "과제분류하기"
OUT = ROOT / "output"
EXTRACTED = OUT / "_extracted"
STUDY_OUT = OUT / "study"
ASSIGN_OUT = OUT / "assignment"

UNIT_RE = re.compile(
    r"(\d+[~\-]?\d*\s*)?(장|일차|강|주차)|서론|프롤로그|부록|코딩면허",
    re.I,
)
NOTE_SUFFIX_RE = re.compile(
    r"\s*(독서\s*노트|독서노트|수강노트|영상노트|독서 노트)\s*$",
    re.I,
)


class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)

    def get_text(self) -> str:
        return "\n".join(self.parts)


def read_text_file(path: Path) -> str:
    for enc in ("utf-8", "utf-8-sig", "cp949"):
        try:
            return path.read_text(encoding=enc)
        except (UnicodeDecodeError, OSError):
            continue
    return ""


def extract_docx(path: Path) -> str:
    try:
        from docx import Document
    except ImportError:
        return "[python-docx not installed]"
    doc = Document(str(path))
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


def extract_pdf(path: Path) -> str:
    try:
        import fitz
    except ImportError:
        return "[pymupdf not installed]"
    text_parts = []
    with fitz.open(str(path)) as pdf:
        for page in pdf:
            text_parts.append(page.get_text())
    return "\n".join(text_parts)


def extract_html(path: Path) -> str:
    raw = read_text_file(path)
    stripper = MLStripper()
    try:
        stripper.feed(raw)
        return stripper.get_text()
    except Exception:
        return raw


def extract_source(path: Path) -> str:
    ext = path.suffix.lower()
    if ext == ".txt":
        return read_text_file(path)
    if ext == ".docx":
        return extract_docx(path)
    if ext == ".pdf":
        return extract_pdf(path)
    if ext in (".html", ".htm"):
        return extract_html(path)
    if ext == ".vb":
        return read_text_file(path)
    return ""


def source_href(path: str) -> str:
    rel = path.replace("\\", "/")
    if rel.startswith("data/"):
        rel = rel[5:]
    return "/data/" + "/".join(quote(seg, safe="/") for seg in rel.split("/"))


def extracted_href(path: str) -> str:
    safe = re.sub(r"[^\w\-]", "_", path)[:120]
    return f"/_extracted/{safe}.txt"


def source_link_target(s: SourceRef) -> tuple[str, str]:
    """(표시 이름, 클릭 URL)"""
    p = ROOT / s.path
    if p.is_dir():
        vb = p / "Form1.vb"
        if vb.is_file():
            rel = f"{s.path.replace(chr(92), '/')}/Form1.vb"
            return "Form1.vb", source_href(rel)
        return os.path.basename(s.path), source_href(s.path)

    name = os.path.basename(s.path)
    ext = p.suffix.lower()
    if ext in (".docx", ".pdf"):
        return f"{name} (텍스트 추출본)", extracted_href(s.path)
    if ext in (".html", ".htm", ".txt", ".vb"):
        return name, source_href(s.path)
    return name, source_href(s.path)


PROFESSOR_MASK = "OOO 교수님"
STUDENT_ID_MASK = "OOOOOOOO"
_ASSIGNMENT_DIR = "과제분류하기"
_ID_META_KEYS = frozenset({"학번", "수강번호"})


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


def cache_extract(rel_path: str, content: str) -> Path:
    safe = re.sub(r"[^\w\-]", "_", rel_path)[:120]
    out = EXTRACTED / f"{safe}.txt"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content or "[empty]", encoding="utf-8")
    return out


def parse_unit(filename: str) -> str:
    name = filename.replace(".txt", "")
    for pat in [
        r"(\d+[~\-]?\d*)\s*장",
        r"(\d+[~\-]?\d*)\s*일차",
        r"(\d+[~\-]?\d*)\s*강",
        r"(서론|프롤로그|부록)",
        r"코딩면허",
        r"(\d+[~\-]?\d*)\s*주차",
    ]:
        m = re.search(pat, name, re.I)
        if m:
            return m.group(0)
    return "전체"


def sort_key_unit(unit: str) -> tuple:
    if unit == "전체":
        return (0, 0)
    if "서론" in unit or "프롤로그" in unit:
        return (1, 0)
    nums = re.findall(r"\d+", unit)
    n = int(nums[0]) if nums else 99
    if "~" in unit or "-" in unit:
        return (2, n)
    if "부록" in unit:
        return (4, n)
    return (3, n)


@dataclass
class SourceRef:
    path: str
    unit: str = "전체"
    text: str = ""


@dataclass
class CatalogItem:
    id: str
    type: str
    category: str
    title: str
    slug: str
    summary: str
    tags: list[str]
    sources: list[SourceRef] = field(default_factory=list)

    def load_sources(self) -> None:
        for s in self.sources:
            p = ROOT / s.path
            if p.is_file():
                s.text = extract_source(p)
                if is_assignment_path(s.path):
                    cache_extract(s.path, mask_assignment_privacy(s.text))
                else:
                    cache_extract(s.path, s.text)
            elif p.is_dir():
                for vb in sorted(p.rglob("*.vb")):
                    if "obj" in vb.parts or "bin" in vb.parts:
                        continue
                    if vb.name in ("Form1.vb", "Form1.Designer.vb"):
                        t = extract_source(vb)
                        s.text += f"\n\n--- {vb.name} ---\n{t}"
                if is_assignment_path(s.path):
                    cache_extract(s.path, mask_assignment_privacy(s.text))
                else:
                    cache_extract(s.path, s.text)


STUDY_MERGE_ALIASES: dict[str, str] = {
    "UI디자인&프로그래밍 서론": "UI디자인&프로그래밍",
    "커서AI 트랜드 &활용백과 프롤로그": "커서AI 트랜드 &활용백과",
    "커서AI 트랜드 &활용백과 부록": "커서AI 트랜드 &활용백과",
    "커서AI 트랜드 &활용백과 3~4장": "커서AI 트랜드 &활용백과",
    "된다! 블로그 10분 작성법 3~": "된다! 블로그 10분 작성법",
    "피지컬 컴퓨팅 데이터 수집 및 처리 - 노시훈": "피지컬 컴퓨팅 데이터 수집 및 처리",
    "페스트캠퍼스 일스트레이터 입문 팁": "페스트캠퍼스 일스트레이터 입문",
}

# slug, summary, tags, category — title은 그룹 키(과목명)
STUDY_META: dict[str, tuple[str, str, list[str], str]] = {
    "Do it! Node.js 프로그래밍 입문": ("doit-nodejs", "Node.js·Express·MongoDB 백엔드 입문", ["nodejs", "javascript"], "book"),
    "콜로소 바이브 코딩": ("coloso-vibe-coding", "Cursor AI·바이브 코딩·웹 배포", ["cursor", "ai", "web"], "course"),
    "UI디자인&프로그래밍": ("ui-design-programming", "UI·앱 아이디어·디자인·개발 프로세스", ["ui", "design"], "book"),
    "Do it 5일만에 끝내는 깃&깃허브 입문": ("doit-git-github", "Git·GitHub 협업·Pages", ["git", "github"], "book"),
    "Do it 점프 투 파이썬": ("doit-jump-python", "파이썬 기초·코딩면허", ["python"], "book"),
    "커서AI 트랜드 &활용백과": ("cursor-ai-encyclopedia", "Cursor AI 트렌드·활용", ["cursor", "ai"], "book"),
    "Do it 커서로 시작하는 AI 코딩 입문": ("doit-cursor-ai-intro", "AI 코딩·Cursor 입문", ["cursor", "ai"], "book"),
    "인프런 취준생이 반드시 일겅봐야 할 중고신입 전략": ("inflearn-job-strategy", "취업·면접·이력서 전략", ["career", "job"], "course"),
    "Do it 첫 알고리즘": ("doit-first-algorithm", "알고리즘·자료구조·정렬", ["algorithm"], "book"),
    "된다! 블로그 10분 작성법": ("blog-10min", "블로그·콘텐츠 작성", ["blog", "writing"], "book"),
    "코딩펙토리 flutter Dart": ("codingfactory-flutter", "Flutter·Dart 앱 개발", ["flutter", "dart"], "course"),
    "Do it! HTML + CSS + 자바스크립트 웹 표준의 정석": ("doit-html-css-js", "웹 표준·HTML/CSS/JS", ["html", "css", "javascript"], "book"),
    "Do it! 모던 자바스크립트 프로그래밍의 정석": ("doit-modern-javascript", "모던 JavaScript", ["javascript"], "book"),
    "가장 쉬운 독학 노션 첫걸음": ("notion-first-steps", "노션 워크스페이스·DB", ["notion", "productivity"], "book"),
    "과학동아 323호 AI 공정한가": ("science-donga-323", "AI 윤리·공정성", ["ai", "ethics"], "book"),
    "과학동아 40주년 AI 특이점, 그후 40년": ("science-donga-40", "AI 특이점·미래 전망", ["ai", "future"], "book"),
    "그래도 나아간다는 믿음": ("faith-forward", "자기계발·믿음", ["self-help"], "book"),
    "꿈은 이루어진다": ("dreams-come-true", "자기계발·목표", ["self-help"], "book"),
    "대기업을 이긴 한국의 스타트업": ("korean-startups", "스타트업·비즈니스", ["startup", "business"], "book"),
    "맛있는 디자인 에프터 이펙트": ("tasty-after-effects", "AE 실습", ["after-effects", "design"], "course"),
    "맛있는 디자인 일러스트레이터": ("tasty-illustrator", "일러스트 실습", ["illustrator", "design"], "course"),
    "맛있는 디자인 포토샵": ("tasty-photoshop", "포토샵 실습", ["photoshop", "design"], "course"),
    "맛있는 디자인 프리미어 프로": ("tasty-premiere", "프리미어 실습", ["premiere", "video"], "course"),
    "소스 코드, 더 비기닝": ("source-code-beginning", "IT 역사·스타트업", ["history", "startup"], "book"),
    "스마트폰으로 AI영상 제작": ("smartphone-ai-video", "모바일 AI 영상", ["ai", "video"], "book"),
    "스토리가 스펙을 이긴다": ("story-beats-spec", "스토리·커리어", ["career", "story"], "book"),
    "요즘 바이브 코딩 커서 AI 30가지 프로그램만들기": ("vibe-coding-30-apps", "바이브 코딩 30 프로젝트", ["cursor", "ai"], "book"),
    "정치가 왜이래": ("politics-why", "정치·시사", ["politics"], "book"),
    "트렌드 코리아 2026": ("trend-korea-2026", "2026 트렌드", ["trend", "business"], "book"),
    "패스트캠퍼스 안드로이드 코틀린": ("fastcampus-android-kotlin", "안드로이드·Kotlin", ["android", "kotlin"], "course"),
    "퍼플렉시티 완벽가이드": ("perplexity-guide", "Perplexity AI 활용", ["ai", "search"], "book"),
    "페스트캠퍼스 일스트레이터 입문": ("fastcampus-illustrator", "일러스트레이터 입문·팁", ["illustrator", "design"], "course"),
    "페스트캠퍼스 포토샵": ("fastcampus-photoshop", "포토샵 입문", ["photoshop", "design"], "course"),
    "프롬프트 텔링": ("prompt-telling", "프롬프트·스토리텔링", ["ai", "prompt"], "book"),
    "피지컬 컴퓨팅 데이터 수집 및 처리": ("physical-computing", "피지컬 컴퓨팅·센서", ["arduino", "iot"], "book"),
    "Do it android kotlin": ("doit-android-kotlin", "Android·Kotlin (Do it)", ["android", "kotlin"], "book"),
    "AI 에전트 트렌드 & 활용백과 독서노트": (
        "ai-agent-encyclopedia",
        "AI 에이전트 트렌드·활용 통합 노트",
        ["ai", "agent"],
        "book",
    ),
}

# 과목별 서술형 구어체 요약 (원문 메모를 그대로 나열하지 않음)
STUDY_NARRATIVES: dict[str, str] = {
    "doit-nodejs": (
        "백엔드가 어떻게 돌아가는지 처음부터 손으로 익혀 본 과목이에요. "
        "자바스크립트·Node.js·npm 개념을 잡고, Express로 서버를 만들고, "
        "데이터베이스와 CRUD, 인증까지 단계를 올려 가며 실습했어요. "
        "프론트와 서버가 어떻게 맞물리는지 감이 잡히기 시작한 시점이었어요."
    ),
    "coloso-vibe-coding": (
        "Cursor AI로 말하듯 코딩하고, 만든 결과를 웹에 올려 보는 흐름을 익힌 강의예요. "
        "자연어로 요청해 코드를 받고, HTML·CSS·JS로 페이지를 다듬은 뒤 "
        "FTP·호스팅으로 배포까지 연결해 봤어요. "
        "바이브 코딩이 실제 작업 속도를 어떻게 바꾸는지 체감한 과목이에요."
    ),
    "ui-design-programming": (
        "앱·서비스를 만들 때 아이디어부터 디자인, 개발까지 이어지는 과정을 정리한 책이에요. "
        "무엇을 만들지 구상하고, 사용자 관점에서 화면을 설계한 다음 "
        "구현과 피드백을 반복하는 흐름을 배웠어요. "
        "기술만이 아니라 기획·디자인 사고방식을 같이 챙긴 학습이었어요."
    ),
    "doit-git-github": (
        "Git과 GitHub를 처음 제대로 써 본 기록이에요. "
        "저장소·브랜치·커밋·병합 같은 기본기부터 협업·원격·Pages 배포까지 "
        "차근차근 따라 가며 익혔어요. "
        "버전 관리가 왜 필요한지, 실무에서 어떻게 쓰이는지 감이 잡힌 과목이에요."
    ),
    "doit-jump-python": (
        "파이썬 문법과 기본기를 처음부터 쌓은 과목이에요. "
        "설치·자료형·제어문·함수·클래스, 파일·인코딩, 예외 처리·실습 예제를 거치고 "
        "마지막에는 코딩면허 스타일 문제도 풀어 봤어요. "
        "데이터·AI·웹까지 파이썬이 어디에 쓰이는지 큰 그림도 같이 잡았어요."
    ),
    "cursor-ai-encyclopedia": (
        "Cursor AI가 어떤 도구인지, 어떻게 쓰면 생산성이 오르는지 훑어 본 책이에요. "
        "설치·기본 사용법부터 프롬프트·프로젝트 활용, 트렌드·부록까지 "
        "AI 코딩 환경을 한 바퀴 돌아본 느낌이에요. "
        "에디터와 AI가 합쳐진 작업 방식을 익히는 데 초점을 둔 학습이었어요."
    ),
    "doit-cursor-ai-intro": (
        "Cursor로 AI 코딩을 시작하는 입문 코스예요. "
        "환경 설정·프롬프트 작성·간단한 프로젝트 실습을 하루 단위로 진행했고, "
        "말로 요청하고 코드를 고치는 반복에 익숙해졌어요. "
        "처음 AI 코딩 툴을 손에 쥔 때의 로드맵을 정리한 기록이에요."
    ),
    "inflearn-job-strategy": (
        "취업·이직을 준비할 때 서류·면접·전략을 점검한 강의예요. "
        "이력서·자기소개·면접 대비를 단계별로 정리하고, "
        "중고신입으로서 어떤 포인트를 어필해야 하는지 배웠어요. "
        "기술만이 아니라 커리어 설계 관점에서 돌아본 학습이었어요."
    ),
    "doit-first-algorithm": (
        "알고리즘과 자료구조를 입문자 눈높이로 익힌 책이에요. "
        "시간 복잡도·기본 자료구조·정렬·탐색을 차례로 다루며 "
        "왜 이런 구조와 알고리즘이 쓰이는지 이해하려 했어요. "
        "코딩 테스트·면접 준비의 밑바닥을 다지는 과목이었어요."
    ),
    "blog-10min": (
        "블로그 글을 짧은 시간 안에 쓰는 루틴을 익힌 책이에요. "
        "주제 잡기·초안·발행까지 하루 단위로 연습하며 "
        "꾸준히 콘텐츠를 낼 수 있는 습관을 만들려 했어요. "
        "기록과 글쓰기를 병행하는 데 도움이 된 학습이었어요."
    ),
    "codingfactory-flutter": (
        "Flutter와 Dart로 앱 개발 입문을 시도한 강의예요. "
        "위젯·화면 구성·기본 문법을 강 단위로 따라 가며 "
        "크로스플랫폼 앱이 어떻게 짜이는지 훑어 봤어요. "
        "모바일 UI를 코드로 만드는 첫 경험에 가까웠어요."
    ),
    "doit-html-css-js": (
        "웹 표준에 맞춰 HTML·CSS·자바스크립트 기초를 정리한 책이에요. "
        "문서 구조·스타일·동작을 나눠 이해하고, "
        "브라우저에서 페이지가 어떻게 그려지는지 기초를 다졌어요. "
        "프론트엔드와 퍼블리싱의 출발점을 만든 학습이었어요."
    ),
    "doit-modern-javascript": (
        "모던 JavaScript 문법과 실습 위주로 필기한 기록이에요. "
        "ES6 이후 자주 쓰는 문법·패턴을 정리하고, "
        "예제를 따라 하며 최신 JS 스타일에 익숙해지려 했어요. "
        "Node·프론트로 가기 전 JS 기초를 보강한 과목이에요."
    ),
    "notion-first-steps": (
        "노션으로 워크스페이스와 데이터베이스를 처음 구성해 본 책이에요. "
        "요금제·페이지·DB·템플릿 개념을 익히고, "
        "개인 기록·할 일·자료를 한곳에 모으는 방법을 배웠어요. "
        "생산성 도구로 노션을 쓰기 시작한 계기가 된 학습이었어요."
    ),
    "science-donga-323": (
        "AI가 공정한지, 편향·윤리 문제는 없는지 다룬 과학동아 기사 학습이에요. "
        "기술만이 아니라 사회·윤리 관점에서 AI를 바라보는 "
        "짧지만 인상 깊은 독서 노트였어요."
    ),
    "science-donga-40": (
        "AI 특이점 이후 40년을 상상해 본 과학동아 특집을 읽고 정리했어요. "
        "기술·사회 변화를 장기 시계로 바라보는 관점을 "
        "가볍게 훑어 본 학습이었어요."
    ),
    "faith-forward": (
        "힘들 때도 나아간다는 믿음·마음가짐을 다룬 자기계발 독서예요. "
        "기술 서적과는 결이 다르게, 삶의 태도와 "
        "멘탈을 돌아보는 시간을 가졌어요."
    ),
    "dreams-come-true": (
        "꿈과 목표를 이루는 마음가짐을 다룬 자기계발 책이에요. "
        "무엇을 원하는지, 어떻게 밀고 나갈지에 대한 "
        "짧은 메모형 독서였어요."
    ),
    "korean-startups": (
        "대기업과 맞서 성장한 한국 스타트업 사례를 읽고 정리했어요. "
        "창업·비즈니스·기술이 어떻게 맞물리는지 "
        "이야기 위주로 훑어 본 책이에요."
    ),
    "tasty-after-effects": (
        "애프터 이펙트로 모션·합성을 실습 위주로 익힌 강의예요. "
        "효과·타임라인·레이어 작업을 따라 하며 "
        "영상 후반 작업이 어떻게 이뤄지는지 감을 잡았어요."
    ),
    "tasty-illustrator": (
        "일러스트레이터로 벡터 작업을 실습한 기록이에요. "
        "도구·패스·편집 기본을 익히고 "
        "그래픽 작업의 기초를 쌓는 데 집중했어요."
    ),
    "tasty-photoshop": (
        "포토샵으로 합성·보정을 실습 위주로 배운 강의예요. "
        "레이어·선택·보정 도구를 쓰며 "
        "이미지 편집 워크플로를 익혔어요."
    ),
    "tasty-premiere": (
        "프리미어 프로로 영상 편집 실습을 진행한 강의예요. "
        "컷 편집·타임라인·보내기까지 "
        "영상 제작 기초를 따라 해 본 학습이었어요."
    ),
    "source-code-beginning": (
        "IT·스타트업 역사를 인물과 사건 중심으로 읽은 책이에요. "
        "기술이 어떻게 비즈니스와 맞물려 왔는지 "
        "이야기로 풀어 보며 큰 그림을 챙긴 독서였어요."
    ),
    "smartphone-ai-video": (
        "스마트폰만으로 AI 영상을 만드는 방법을 익힌 책이에요. "
        "촬영·편집·AI 도구를 활용해 "
        "가벼운 영상 제작 파이프라인을 정리했어요."
    ),
    "story-beats-spec": (
        "스토리와 경험이 스펙만큼 중요하다는 관점의 책이에요. "
        "이력·자기소개·커리어를 이야기로 풀어야 한다는 "
        "메시지를 중심으로 읽고 정리했어요."
    ),
    "vibe-coding-30-apps": (
        "Cursor AI로 30가지 가벼운 프로그램을 만들어 보는 흐름을 담은 책이에요. "
        "아이디어·프롬프트·빠른 구현을 반복하며 "
        "바이브 코딩으로 무엇을 만들 수 있는지 넓혀 본 학습이었어요."
    ),
    "politics-why": (
        "정치·시사 이슈를 가볍게 읽고 생각해 본 독서예요. "
        "기술 학습과는 다른 맥락에서 "
        "사회 흐름을 이해하려 한 기록이에요."
    ),
    "trend-korea-2026": (
        "2026년 소비·기술·사회 트렌드를 한권에 정리한 책이에요. "
        "앞으로 어떤 키워드가 뜰지 "
        "미리 훑어 보며 시야를 넓힌 독서였어요."
    ),
    "fastcampus-android-kotlin": (
        "안드로이드 앱 개발을 Kotlin으로 입문한 강의예요. "
        "앱 구조·Kotlin 문법·기본 화면을 익히며 "
        "모바일 네이티브 개발의 문을 열어 본 학습이었어요."
    ),
    "perplexity-guide": (
        "Perplexity AI 검색·질의 도구를 활용하는 방법을 익힌 책이에요. "
        "출처와 함께 답을 받는 검색 경험과 "
        "리서치·학습에 쓰는 팁을 정리했어요."
    ),
    "fastcampus-illustrator": (
        "일러스트레이터 입문과 실무 팁을 함께 정리한 강의예요. "
        "기본 도구 사용법부터 단축키·작업 요령까지 "
        "벡터 작업 입문을 마친 과목이에요."
    ),
    "fastcampus-photoshop": (
        "포토샵 기초 도구와 합성 입문을 배운 강의예요. "
        "레이어·마스크·보정을 익히며 "
        "이미지 편집의 첫 단계를 밟았어요."
    ),
    "prompt-telling": (
        "프롬프트를 스토리처럼 설계하는 방법을 다룬 책이에요. "
        "AI에게 무엇을 어떻게 말해야 원하는 결과가 나오는지 "
        "구조·표현 관점에서 정리했어요."
    ),
    "physical-computing": (
        "아두이노·센서로 데이터를 수집하고 처리하는 피지컬 컴퓨팅을 공부했어요. "
        "하드웨어와 소프트웨어가 만나는 지점을 익히고, "
        "실습·보충 노트를 통해 IoT 기초 감각을 쌓았어요."
    ),
    "doit-android-kotlin": (
        "Do it 시리즈로 Android·Kotlin 기초를 정리한 학습이에요. "
        "앱 개발 환경·문법·화면 구성을 익히며 "
        "모바일 개발 학습을 이어 간 과목이에요."
    ),
    "ai-agent-encyclopedia": (
        "AI 에이전트 트렌드와 활용을 한권에 모아 읽은 통합 노트예요. "
        "에이전트 개념·도구·활용 방향을 훑으며 "
        "Cursor·AI 코딩과 연결해 본 학습이었어요."
    ),
}


def normalize_study_title(filename: str) -> str:
    n = filename.replace(".txt", "").replace(".docx", "")
    n = re.sub(
        r"\s+(\d+[~\-]?\d*\s*)?(장|일차|강|주차)\s*(독서\s*노트|독서노트|수강노트|영상노트|독서 노트)\s*$",
        "",
        n,
        flags=re.I,
    )
    n = re.sub(r"\s+(독서노트|수강노트|영상노트|독서 노트)\s*$", "", n, flags=re.I)
    n = re.sub(r"\s+코딩면허.*$", "", n, flags=re.I)
    n = re.sub(r"\s+노트는\s*실습.*$", "", n, flags=re.I)
    n = re.sub(r"\s+실습\s*필기.*$", "", n, flags=re.I)
    n = re.sub(r"\s+실습위주.*$", "", n, flags=re.I)
    n = re.sub(r"\s+통합\(단순합치기\).*$", "", n)
    return n.strip()


def collect_study_groups() -> dict[str, list[str]]:
    """data/ 내 txt·docx만 수집, 과목(도서/강의)당 1그룹."""
    raw: dict[str, list[str]] = {}
    skipped_hwpx: list[str] = []

    for f in sorted(DATA.iterdir()):
        if not f.is_file():
            continue
        ext = f.suffix.lower()
        if ext == ".hwpx":
            skipped_hwpx.append(f.name)
            continue
        if ext not in (".txt", ".docx"):
            continue
        base = normalize_study_title(f.name)
        raw.setdefault(base, []).append(f"data/{f.name}")

    merged: dict[str, list[str]] = {}
    for base, paths in raw.items():
        canonical = STUDY_MERGE_ALIASES.get(base, base)
        merged.setdefault(canonical, []).extend(paths)

    for paths in merged.values():
        paths.sort(key=lambda p: sort_key_unit(parse_unit(os.path.basename(p))))

    return merged, skipped_hwpx


def build_study_catalog() -> list[CatalogItem]:
    groups, skipped_hwpx = collect_study_groups()

    if len(groups) != 37:
        report = OUT / "study-audit.txt"
        lines = [
            f"학습 그룹 수: {len(groups)} (기대: 37)",
            f"제외 hwpx: {len(skipped_hwpx)}",
            "",
            "=== 그룹 목록 ===",
        ]
        for k in sorted(groups):
            lines.append(f"  [{len(groups[k]):2d}] {k}")
        if skipped_hwpx:
            lines.extend(["", "=== 제외 hwpx ===", *[f"  {x}" for x in skipped_hwpx]])
        report.write_text("\n".join(lines), encoding="utf-8")
        raise SystemExit(f"학습 과목 수가 37개가 아닙니다 ({len(groups)}개). output/study-audit.txt 참고")

    items: list[CatalogItem] = []
    for title in sorted(groups.keys()):
        paths = groups[title]
        meta = STUDY_META.get(title)
        if meta:
            slug, summary, tags, category = meta
        else:
            slug = re.sub(r"[^\w]+", "-", title.lower())[:48].strip("-") or "study-unknown"
            summary = f"{title} 학습 노트"
            tags = ["study"]
            category = "book" if "Do it" in title else "course"

        items.append(
            CatalogItem(
                id=f"study-{slug}",
                type="study",
                category=category,
                title=title,
                slug=slug,
                summary=summary,
                tags=tags,
                sources=[
                    SourceRef(path=p, unit=parse_unit(os.path.basename(p))) for p in paths
                ],
            )
        )

    return items


def find_assign_file(files: list[str], keywords: list[str], used: set[str], exclude_contains: list[str] | None = None) -> str | None:
    excludes = exclude_contains or []
    for kw in keywords:
        for f in files:
            if f in used:
                continue
            if any(ex in f for ex in excludes):
                continue
            if kw in f:
                return f
    return None


def build_assignment_catalog() -> list[CatalogItem]:
    """16 university assignments — matched to actual files in data/과제분류하기."""
    files = [f for f in os.listdir(ASSIGN) if (ASSIGN / f).is_file()]
    used: set[str] = set()
    items: list[CatalogItem] = []

    def add(slug: str, title: str, keywords: list[str], tags: list[str], exclude_contains: list[str] | None = None, extra_sources: list[SourceRef] | None = None):
        matched = find_assign_file(files, keywords, used, exclude_contains)
        srcs: list[SourceRef] = []
        if matched:
            used.add(matched)
            srcs.append(SourceRef(path=f"data/과제분류하기/{matched}", unit="총괄과제"))
        if extra_sources:
            srcs.extend(extra_sources)
        items.append(
            CatalogItem(
                id=f"assignment-{slug}",
                type="assignment",
                category="university",
                title=title,
                slug=slug,
                summary=f"{title} 총괄/최종 과제 수행 기록",
                tags=tags,
                sources=srcs,
            )
        )

    add("c-language-1", "C언어1", ["C언어1"], ["c", "pointer"])
    add("pc-skills-1", "PC활용1", ["PC활용1"], ["office", "pc"])
    add("database", "데이터베이스", ["데이터베이스"], ["database", "sql"])
    intro = find_assign_file(files, ["멀티미디어 개론", "멀티미디어개론"], used)
    telecom = find_assign_file(files, ["멀티미디어통신"], used)
    mm_srcs = []
    if intro:
        used.add(intro)
        mm_srcs.append(SourceRef(path=f"data/과제분류하기/{intro}", unit="멀티미디어 개론"))
    if telecom:
        used.add(telecom)
        mm_srcs.append(SourceRef(path=f"data/과제분류하기/{telecom}", unit="멀티미디어통신"))
    items.append(
        CatalogItem(
            id="assignment-multimedia",
            type="assignment",
            category="university",
            title="멀티미디어 (개론·통신)",
            slug="multimedia",
            summary="멀티미디어 개론·통신 총괄 과제",
            tags=["multimedia"],
            sources=mm_srcs,
        )
    )
    add("software-engineering", "소프트웨어공학", ["소프트웨어공학"], ["software-engineering"])
    add("system-analysis-design", "시스템분석설계", ["시스템분석설계"], ["system", "analysis"])
    add("discrete-math", "이산수학", ["이산수학"], ["math"])
    add("internet-marketing", "인터넷 마케팅", ["인터넷 마케팅"], ["marketing", "internet"])
    add("internet-programming", "인터넷프로그래밍", ["인터넷프로그래밍_"], ["html", "web"], exclude_contains=["프로그래밍2"])
    add("internet-programming-2", "인터넷프로그래밍2", ["인터넷프로그래밍2"], ["html", "web"])
    add("data-structures", "자료구조", ["자료구조"], ["algorithm", "data-structure"])
    add("information-processing", "정보처리", ["정보처리"], ["information"])
    add("computer-intro", "컴퓨터개론", ["컴퓨터개론"], ["computer-science"])
    add("computer-graphics-1", "컴퓨터그래픽1", ["컴퓨터그래픽1"], ["graphics"])
    add("computer-network", "컴퓨터네트워크", ["컴퓨터네트워크"], ["network", "protocol"])

    # 윈도우 프로그래밍1(VB) + 윈도우프로그래밍2(docx) 통합
    win2 = find_assign_file(files, ["윈도우프로그래밍2"], used)
    extra = []
    if win2:
        used.add(win2)
        extra.append(SourceRef(path=f"data/과제분류하기/{win2}", unit="윈도우프로그래밍2"))
    vb_path = "data/과제분류하기/윈도우 프로그래밍1 총괄과제"
    if (ASSIGN / "윈도우 프로그래밍1 총괄과제").is_dir():
        extra.append(SourceRef(path=vb_path, unit="Form1.vb"))
    items.append(
        CatalogItem(
            id="assignment-windows-programming",
            type="assignment",
            category="university",
            title="윈도우 프로그래밍",
            slug="windows-programming",
            summary="VB.NET WinForms 과제 및 윈도우프로그래밍2 문서 과제",
            tags=["vbnet", "winforms"],
            sources=extra,
        )
    )

    return items


def extract_meta_assignment(text: str) -> dict[str, str]:
    meta = {}
    patterns = [
        ("학번", r"학\s*번\s*[:：]\s*(\d+)"),
        ("수강번호", r"수\s*강\s*번\s*호\s*[:：]\s*(\d+)"),
        ("이름", r"이\s*름\s*[:：]\s*(\S+)"),
        ("지도교수", r"지도교수\s*[:：]\s*(\S+)"),
        ("제출일", r"제출일\s*[:：]\s*([\d\-]+)"),
    ]
    for key, pat in patterns:
        m = re.search(pat, text)
        if m:
            meta[key] = m.group(1)
    return meta


_HANGUL = re.compile(r"[가-힣]")
_CODE_NOISE = re.compile(
    r"^(>>>|\.\.\.|File \"|Traceback|import |from |def |class |#include|"
    r"using namespace|return |if |for |while |else|\{|\}|</|http://|https://)",
    re.I,
)


def is_prose_line(line: str) -> bool:
    s = line.strip()
    if len(s) < 12 or len(s) > 280:
        return False
    if not _HANGUL.search(s):
        return False
    if _CODE_NOISE.match(s):
        return False
    if s.count("=") > 4 or s.startswith("---"):
        return False
    ascii_ratio = sum(1 for c in s if ord(c) < 128) / len(s)
    if ascii_ratio > 0.65 and "파이썬" not in s and "프로그래" not in s:
        return False
    return True


def extract_study_points(text: str, max_items: int = 8) -> list[str]:
    """노트에서 서술에 쓸 만한 한국어 문장만 추출."""
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    points: list[str] = []
    seen: set[str] = set()
    for ln in lines:
        if not is_prose_line(ln):
            continue
        ln = re.sub(r"\s+", " ", ln)
        key = ln[:50]
        if key in seen:
            continue
        seen.add(key)
        points.append(ln)
        if len(points) >= max_items:
            break
    return points


def soften_sentence(s: str) -> str:
    s = s.rstrip(".")
    s = re.sub(r"\s*등의\s*$", "", s)
    if s and s[-1] not in ".!?":
        s += "."
    return s


def weave_narrative(opener: str, points: list[str], fallback: str = "") -> str:
    """추출한要点를 구어체 서술문으로 이어 붙임."""
    cleaned = [soften_sentence(p).rstrip(".") for p in points if p.strip()]
    if not cleaned:
        base = fallback or "교재·강의 흐름을 따라가며 전체 개념을 익히는 데 집중"
        return f"{opener.rstrip('.')} {base}했어요."

    if len(cleaned) == 1:
        return f"{opener.rstrip('.')} {cleaned[0]} 내용을 중심으로 공부했어요."

    first = " ".join(cleaned[:3])
    rest = " ".join(cleaned[3:6])
    if rest:
        return (
            f"{opener.rstrip('.')} {first} 같은 내용을 먼저 잡았고, "
            f"이어서 {rest} 부분까지 넓혀 가며 정리했어요."
        )
    return f"{opener.rstrip('.')} {first} 흐름으로 전반적인 내용을 익혔어요."


def _phase_unit_narratives(item: CatalogItem) -> list[tuple[str, str]]:
    """장·강·일차가 많을 때 앞·중·뒤 구간만 구어체로 요약."""
    n = len(item.sources)
    if n < 4:
        return []

    sources = item.sources
    if n <= 6:
        phases = [(0, 0, "처음"), (n // 2, n // 2, "중간"), (n - 1, n - 1, "마지막")]
    else:
        third = max(1, n // 3)
        phases = [
            (0, third - 1, "앞부분"),
            (third, 2 * third - 1, "중반"),
            (2 * third, n - 1, "후반"),
        ]

    blocks: list[tuple[str, str]] = []
    for start, end, label in phases:
        seg = sources[start : end + 1]
        u_from = seg[0].unit
        u_to = seg[-1].unit
        unit_label = u_from if u_from == u_to else f"{u_from}~{u_to}"
        if label in ("처음", "앞부분"):
            para = (
                f"{unit_label} 구간에서는 {item.summary}의 기초를 다지며 "
                f"개념과 환경 설정에 집중했어요."
            )
        elif label in ("마지막", "후반"):
            para = (
                f"{unit_label} 구간에서는 지금까지 배운 내용을 연결·정리하고 "
                f"실전·응용 쪽으로 마무리했어요."
            )
        else:
            para = (
                f"{unit_label} 구간에서는 예제·실습을 따라 하며 "
                f"손에 익히는 단계를 밟았어요."
            )
        blocks.append((unit_label, para))
    return blocks


def build_study_narrative(item: CatalogItem) -> dict[str, Any]:
    """과목 전체를 서술형 구어체로 요약 (원문 나열 없음)."""
    unit_hint = ""
    if len(item.sources) >= 3:
        units = [s.unit for s in item.sources if s.unit != "전체"]
        if units:
            unit_hint = f" ({units[0]}부터 {units[-1]}까지)"

    overview = (
        f"「{item.title}」을(를) 공부하면서{unit_hint} "
        f"총 {len(item.sources)}개의 노트를 남겼어요. "
        f"한 줄로 말하면 {item.summary} 쪽을 중심으로 학습했다고 보면 됩니다."
    )

    main = STUDY_NARRATIVES.get(item.slug)
    if not main:
        main = (
            f"이 과목에서는 {item.summary}을(를) 목표로 "
            f"{len(item.sources)}번에 걸쳐 내용을 쌓아 갔어요. "
            f"노트는 키워드 위주라서, 여기서는 그때의 학습 흐름과 목표를 "
            f"이야기하듯 풀어 썼어요."
        )

    reflection = (
        f"돌이켜 보면 {item.title}에서 {item.summary}와 관련된 내용을 "
        f"차근차근 쌓아 갔어요. 원본 문장을 그대로 옮기지 않고, "
        f"그때 무엇을 배우려 했는지 전체 흐름으로 정리한 거예요."
    )

    return {
        "overview": overview,
        "main": main,
        "reflection": reflection,
        "units": _phase_unit_narratives(item),
    }


def summarize_bullets(text: str, max_items: int = 10) -> list[str]:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    bullets = []
    for ln in lines:
        if len(ln) < 4:
            continue
        if ln.startswith(("-", "*", "•")):
            bullets.append(ln.lstrip("-*• ").strip())
        elif re.match(r"^\d+[\.\)]", ln):
            bullets.append(re.sub(r"^\d+[\.\)]\s*", "", ln))
        elif len(ln) > 15 and not ln.startswith("="):
            bullets.append(ln)
    seen = set()
    out = []
    for b in bullets:
        key = b[:60]
        if key not in seen:
            seen.add(key)
            out.append(b)
        if len(out) >= max_items:
            break
    return out


def make_overview(item: CatalogItem, bullets: list[str]) -> str:
    if item.type == "assignment":
        return (
            f"{item.title} 과목의 총괄/최종 과제를 수행하며 "
            f"과제 요구사항에 맞춰 답안·코드·문서를 작성했습니다. "
            f"원본 자료는 {len(item.sources)}개 파일에서 확인할 수 있습니다."
        )
    if bullets:
        topics = "·".join(b[:20] for b in bullets[:3])
        return (
            f"「{item.title}」 학습을 진행하며 {len(item.sources)}개 단위의 노트를 남겼습니다. "
            f"주요 키워드: {topics} 등."
        )
    return f"「{item.title}」 관련 학습 노트를 정리했습니다. 원본 메모가 짧거나 키워드 수준일 수 있습니다."


def render_markdown(item: CatalogItem) -> str:
    all_text = "\n\n".join(s.text for s in item.sources if s.text)
    bullets = summarize_bullets(all_text)
    study_narr = build_study_narrative(item) if item.type == "study" else None
    overview = study_narr["overview"] if study_narr else make_overview(item, bullets)
    fm_summary = item.summary

    progress_units = len(item.sources)
    fm_sources = [{"path": s.path, "unit": s.unit} for s in item.sources]

    lines = [
        "---",
        f"id: {item.id}",
        f"type: {item.type}",
        f"category: {item.category}",
        f'title: "{item.title}"',
        f"slug: {item.slug}",
        f'summary: "{fm_summary}"',
        f"tags: {json.dumps(item.tags, ensure_ascii=False)}",
        "progress:",
        f"  units: {progress_units}",
        f"  completed: {progress_units}",
        "sources:",
    ]
    for s in fm_sources:
        path = mask_assignment_privacy(s["path"]) if item.type == "assignment" else s["path"]
        lines.append(f"  - path: {path}")
        lines.append(f"    unit: \"{s['unit']}\"")
    lines.extend(["created_from: study_note_record_organization", "---", ""])

    lines.append(f"# {item.title}\n")
    lines.append("## 한눈에 보기\n")
    lines.append(overview + "\n")

    if item.type == "study" and study_narr:
        lines.append("## 무엇을 배웠는지\n")
        lines.append(study_narr["main"] + "\n\n")
        lines.append(study_narr["reflection"] + "\n\n")
        if study_narr["units"]:
            lines.append("## 단계별로 살보면\n")
            for unit, para in study_narr["units"]:
                lines.append(f"### {unit}\n")
                lines.append(para + "\n\n")
    elif item.type != "assignment":
        lines.append("## 핵심 요약\n")
        if bullets:
            for b in bullets:
                lines.append(f"- {b}")
        else:
            lines.append("- 원본 메모가 키워드 수준이거나 추출 텍스트가 비어 있습니다.")
        lines.append("")

    if item.type == "assignment":
        meta = extract_meta_assignment(all_text)
        if "지도교수" in meta:
            meta["지도교수"] = PROFESSOR_MASK
        for key in _ID_META_KEYS:
            if key in meta:
                meta[key] = STUDENT_ID_MASK
        masked_text = mask_assignment_privacy(all_text)
        lines.append("## 과제 정보\n")
        if meta:
            for k, v in meta.items():
                lines.append(f"- **{k}**: {v}")
        else:
            lines.append("- 원본에서 메타 정보를 추출하지 못했습니다.")
        lines.append("")

        lines.append("## 과제 주제·요구사항\n")
        topics = summarize_bullets(masked_text, 8)
        for b in topics[:5]:
            lines.append(f"- {b}")
        lines.append("")

        lines.append("## 수행 내용·답안 요약\n")
        for b in topics[5:] or topics:
            lines.append(f"- {b}")
        lines.append("")

        if "vb" in "".join(item.tags).lower() or any("Form1" in s.path for s in item.sources):
            lines.append("## 구현·소스\n")
            lines.append("- WinForms `txtInput` 입력 시 `lblOutput`에 동일 텍스트를 실시간 표시")
            lines.append("- 폼 로드 시 `lblOutput`에 포커스 설정")
            if "Form1.vb" in all_text or "txtInput" in all_text:
                lines.append("\n```vb")
                lines.append("Private Sub txtInput_TextChanged(...) Handles txtInput.TextChanged")
                lines.append("    lblOutput.Text = txtInput.Text")
                lines.append("End Sub")
                lines.append("```\n")

    if item.type == "assignment":
        lines.append("## 배운 점 / 적용\n")
        lines.append(f"- {item.title} 과목 핵심 개념을 과제 답안·구현으로 정리")
        lines.append("- 제출 형식(문서/HTML/PDF/코드)에 맞춘 산출물 작성 경험")
        lines.append("")

    lines.append("## 원본 출처\n")
    lines.append("아래 링크를 클릭하면 원본·추출 텍스트 전체를 볼 수 있습니다.\n")
    for s in item.sources:
        label, href = source_link_target(s)
        if item.type == "assignment":
            label = mask_assignment_privacy(label)
            disp_path = mask_assignment_privacy(s.path)
            lines.append(f"- [{label}]({href}) ({s.unit}) — `{disp_path}`")
        else:
            lines.append(f"- [{label}]({href}) ({s.unit}) — `{s.path}`")
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    STUDY_OUT.mkdir(parents=True, exist_ok=True)
    ASSIGN_OUT.mkdir(parents=True, exist_ok=True)
    EXTRACTED.mkdir(parents=True, exist_ok=True)

    study_items = build_study_catalog()
    assign_items = build_assignment_catalog()

    all_items = study_items + assign_items
    print(f"Study: {len(study_items)}, Assignment: {len(assign_items)}, Total: {len(all_items)}")

    for item in all_items:
        item.load_sources()

    expected_study = {f"{it.slug}.md" for it in study_items}
    expected_assign = {f"{it.slug}.md" for it in assign_items}
    for d, expected in ((STUDY_OUT, expected_study), (ASSIGN_OUT, expected_assign)):
        for old in d.glob("*.md"):
            if old.name not in expected:
                old.unlink()

    catalog_data = []
    for item in all_items:
        md = render_markdown(item)
        out_dir = STUDY_OUT if item.type == "study" else ASSIGN_OUT
        (out_dir / f"{item.slug}.md").write_text(md, encoding="utf-8")
        catalog_data.append(
            {
                "id": item.id,
                "type": item.type,
                "category": item.category,
                "title": item.title,
                "slug": item.slug,
                "summary": item.summary,
                "tags": item.tags,
                "output": f"output/{item.type}/{item.slug}.md",
                "sources": [{"path": s.path, "unit": s.unit} for s in item.sources],
            }
        )

    (OUT / "catalog.json").write_text(
        json.dumps({"items": catalog_data, "counts": {"study": len(study_items), "assignment": len(assign_items), "total": len(all_items)}}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # index.md
    idx = ["# 학습·과제 기록 인덱스\n", f"총 **{len(all_items)}**개 항목 (학습 {len(study_items)} + 과제 {len(assign_items)})\n"]
    idx.append("## 학습 (study)\n")
    for it in study_items:
        idx.append(f"- [{it.title}](study/{it.slug}.md) — {it.summary}")
    idx.append("\n## 과제 (assignment)\n")
    for it in assign_items:
        idx.append(f"- [{it.title}](assignment/{it.slug}.md) — {it.summary}")
    (OUT / "index.md").write_text("\n".join(idx), encoding="utf-8")
    print("Done.")
    try:
        import subprocess
        import sys

        script = ROOT / "scripts" / "build_static_site.py"
        if script.is_file():
            subprocess.run([sys.executable, str(script)], check=False)
    except OSError:
        pass


if __name__ == "__main__":
    main()
