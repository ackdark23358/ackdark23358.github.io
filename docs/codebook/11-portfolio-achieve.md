# 프로젝트 아카이브

## 이 파일이 맡는 일

`portfolio_achieve/index.html`은 지원자가 실습하고 개발한 9개 실습 프로젝트(`PROJ_01` ~ `PROJ_09`) 및 6개 기관 과정 프로젝트(`PROJ_10` ~ `PROJ_15`)를 카드로 모아 총 15개 프로젝트를 제공하는 아카이브 메인 페이지다.

각 프로젝트 카드는 소개, 사용 도구(Pill 태그), 실행 환경, 간단 설명, 핵심 기능을 균일한 시맨틱 카드(`<article class="project-card">`) 구조로 담고 있으며, 외부 이동 없이 단일 페이지 내에서 일목요연하게 열람할 수 있도록 구성되었다.

동작을 지원하는 스타일과 스크립트는 다음과 같다:
- `portfolio_achieve/css/archive.css`: 다크/라이트 테마 변수, 프로젝트 카드 그리드, 정적 메타 카드 레이아웃 및 캡처 이미지 반응형 스타일
- `portfolio_achieve/js/site.js`: 테마 전환 토글(`portfolio-theme-v2` 동기화), 모바일 네비게이션 드롭다운 제어, 스크롤 이동 이벤트

## 읽는 순서

1. 테마 및 리소스 보호 메타 태그 (`robots`, `tdm-reservation`, `referrer`)
2. 상단 헤더 및 자료 드롭다운 네비게이션
3. 히어로 소개 구역 (`#archive`)
4. 프로젝트 카드 그리드 목록 (`#archive-list`, `PROJ_01` ~ `PROJ_15`)
5. 전개형 사이트맵 및 저작권·선언문 푸터
6. 테마 및 인터랙션 스크립트 (`js/site.js`, `../js/protect-resources.js`)

## 구간 설명

### 메타 태그와 테마 사전 적용

`<head>` 내부에서 `localStorage.getItem("portfolio-theme-v2")`를 즉시 실행하여 `data-theme` 속성을 지정한다. 화면이 그려지기 전에 적용되어 깜빡임 현상을 방지한다.

### 프로젝트 카드 구조 (`.project-card`)

각 카드는 독립적인 시맨틱 `<article>` 태그로 구성되며 다음과 같은 정보 블록을 표준화하여 배치한다:
- `.project-card__eyebrow`: 프로젝트 번호와 작업 일자 (예: `PROJ_01 · 2025.02.17`)
- `.project-card__title`: 프로젝트 명칭
- `.field-label` 및 `.field-body`: 프로젝트 소개, 간단 설명, 실행 환경, 핵심 기능
- `.pill-list`: 사용한 언어, 프레임워크, AI 도구 태그 목록 (Python, Express, Cursor 등)

### 테마 토글 및 드롭다운 (`js/site.js`)

- `initThemeToggle`: 버튼 클릭 시 다크 모드와 라이트 모드를 상호 전환하고 `localStorage`에 기록한다.
- `setMobileNav`, `closeDropdowns`: 모바일 뷰포트에서 햄버거 메뉴 및 자료 서브 드롭다운 메뉴를 여닫는다. 바깥 영역 클릭 또는 Escape 키 입력 시 열려 있는 메뉴를 닫는다.

## 이 파일이 부르는 다른 파일

- `portfolio_achieve/css/archive.css`: 아카이브 전용 스타일시트
- `portfolio_achieve/js/site.js`: 테마 및 네비게이션 스크립트
- `../js/protect-resources.js`: 복사·우클릭 방지 및 도메인 검증 보안 가드
- `portfolio_achieve/img/`: 각 프로젝트의 실행 및 테스트 캡처 이미지들
