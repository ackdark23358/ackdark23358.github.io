# 코탐록 이력서 & 자기소개 포트폴리오

IT·웹·모바일·AI 서비스 분야 취업 준비를 위해 제작한 정적 포트폴리오 사이트입니다. 자기소개서, 프로필, 온라인 명함, 이력서, 학습·과제 기록 아카이브를 각각 분리해 관리하며, GitHub Pages 같은 정적 호스팅 환경에 배포할 수 있도록 구성했습니다.

## 프로젝트 소개

이 프로젝트는 지원자의 학습 과정과 관심 분야를 웹 페이지 형태로 정리한 개인 포트폴리오입니다.

- 자기소개서 내용을 기반으로 한 메인 랜딩 페이지
- 프로필과 관심 분야를 정리한 자기소개 페이지
- 스크롤 애니메이션이 있는 3D 온라인 명함
- 간단한 문서형 이력서 페이지
- 학습·과제 노트 요약 아카이브(학습록 대시보드)
- 카드로 보는 프로젝트 아카이브(PROJ_01~PROJ_09)
- 라이트/다크 테마 전환과 반응형 내비게이션

## 페이지 구성

| 페이지 | 경로 | 설명 |
| --- | --- | --- |
| 메인 자기소개서 | `index.html` | 지원 동기, 성장 과정, 보유 역량, 강점, 참고 정보를 담은 메인 페이지 |
| 자기소개 / 프로필 | `cover_letter/profile.html` | 프로필, 관심 분야, 학습 경험, 지원 동기 등을 정리한 페이지 |
| 온라인 명함 | `online_business_card/business-card.html` | 스크롤에 따라 명함이 회전하고 확대되는 인터랙티브 페이지 |
| 이력서 | `cv/resume.html` | 경력, 학력, 자격증을 간단히 정리한 문서형 이력서 |
| 학습·과제 기록 | `study_note_record_organization/dashboard/index.html` | 독서·강의·과제 요약 검색 및 원본 텍스트 열람 |
| 프로젝트 아카이브 | `portfolio_achieve/index.html` | 카드로 보는 프로젝트 기록, 사용 도구, 실행 환경, 핵심 기능 |

## 주요 기능

- **정적 웹사이트 구성**: HTML, CSS, JavaScript만 사용해 별도 빌드 과정 없이 실행할 수 있습니다.
- **공통 헤더 내비게이션**: 주요 페이지를 상단 메뉴로 이동할 수 있습니다.
- **테마 전환**: 라이트/다크 테마를 전환하고 `localStorage`에 선택값을 저장합니다.
- **반응형 메뉴**: 모바일 화면에서도 메뉴 버튼으로 탐색할 수 있습니다.
- **온라인 명함 애니메이션**: 스크롤 위치에 따라 3D 명함이 회전하고 확대됩니다.
- **접근성 고려**: 스킵 링크, `aria` 속성, 키보드 탐색 보조 요소를 일부 적용했습니다.
- **펼친 사이트맵**: 각 페이지 하단에 6대 공개 페이지(자기소개서, 프로필, 온라인 명함, 이력서, 학습록, 프로젝트 아카이브)와 섹션 링크를 펼쳐 둡니다.
- **저작권 표기**: 하단 저작권자는 `© 2026 김신욱(깃허브 ackdark23358)`입니다.
- **복사·끼워 넣기 안내**: `js/protect-resources.js`가 복사·잘라내기·우클릭을 막고, 허용하지 않은 주소나 iframe에서는 본문 대신 안내 문장을 보여 줍니다. 학습록 검색 입력은 그대로 둡니다.
- **검색·수집 범위**: 메인 자기소개서는 검색에 남기고, 자료 페이지와 생성형 수집 로봇은 `robots.txt`와 텍스트·데이터 마이닝 거절 표시로 범위를 좁힙니다.
- **포트폴리오 북 & 4대 기술문서**: Cursor AI 바이브 코딩(Ask/Plan/Agent 모드) 방법론과 전체 프로젝트를 집약한 포트폴리오 북 단행본(`docs/portfolio-book.pdf`) 및 기술명세서, 코드북, 코드 설명, 소스 번들 등 5대 엔지니어링 PDF 문서 생태계를 완비했습니다.
- **학습 아카이브**: 학점은행제(멀티미디어학) 과제 18건 및 기술 도서·강의 독서 노트 37건 등 총 55건의 아카이브를 대시보드로 검색·열람할 수 있습니다.

## 기술 스택

- HTML5
- CSS3
- JavaScript
- GitHub Pages 배포 가능
- Cursor AI 활용 제작

## 참고 자료

이 프로젝트는 아래 자료를 수강하거나 참고하며 제작했습니다.

- 바로바로 바이브 코딩 - 골든레빗
- 요즘 바이브 코딩 - 골든레빗
- Udemy 취준생을 위한 이력서 만들기 HTML + CSS + JavaScript 강의

## 폴더 구조

```text
.
├── index.html
├── robots.txt
├── .well-known/
│   └── tdmrep.json
├── 자기소개서.md
├── css/
│   ├── styles.css
│   └── site-header.css
├── js/
│   ├── main.js
│   └── protect-resources.js
├── cover_letter/
│   ├── profile.html
│   ├── css/
│   │   └── styles.css
│   ├── js/
│   │   └── script.js
│   └── 자기소개서.txt
├── online_business_card/
│   ├── business-card.html
│   ├── cover_letter_draft.md
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── script.js
├── cv/
│   ├── resume.html
│   ├── css/
│   ├── js/
│   └── img/
├── docs/
│   ├── portfolio-book.pdf      # 포트폴리오 북 (프로젝트 전반·바이브 코딩·기술문서 집약 단행본)
│   ├── code-reference.pdf      # 함수·클래스 설명과 유사코드
│   ├── codebook.pdf            # 소스를 파일 순서대로 읽은 설명
│   ├── source-bundle.pdf       # 주석이 붙은 소스 본문
│   ├── technical-specs.pdf     # 요구사항부터 시험 명세까지
│   ├── build_portfolio_book.py
│   ├── build_code_reference.py
│   ├── build_codebook.py
│   ├── build_source_bundle.py
│   ├── build_specs.py
│   ├── portfolio-book/         # 포트폴리오 북 챕터 원본
│   ├── codebook/               # 코드북 원본 (리소스 보호 챕터 포함)
│   └── specs/                  # 기술명세 원본과 차트 이미지
├── portfolio_achieve/          # 프로젝트 아카이브 (PROJ_01~PROJ_09 메타 카드)
│   ├── index.html
│   ├── css/
│   ├── js/
│   └── img/
└── study_note_record_organization/
    ├── dashboard/          # 학습록 정적 사이트 (배포 대상)
    │   ├── index.html
    │   ├── css/
    │   └── js/
    │       ├── data.js
    │       ├── sources/    # 원본 텍스트 청크 (지연 로딩)
    │       └── ...
    ├── data/image/         # 히어로 갤러리
    └── scripts/            # 로컬 빌드용 (선택)
```

## 기술 문서

포트폴리오 북, 코드 설명, 코드북, 소스 모음, 기술명세는 `docs/`에 있습니다. 화면 코드와 빌드 스크립트에는 함수·클래스 주석이 있고, 그 주석을 모아 PDF로 만듭니다. 소스 모음은 그 주석이 붙어 있는 코드 본문입니다. `data/` 안의 과제 프로그램 코드는 이 문서들에서 빼 두었습니다.

| 문서 | 경로 | 내용 |
| --- | --- | --- |
| 포트폴리오 북 | `docs/portfolio-book.pdf` | Cursor AI 바이브 코딩(Ask/Plan/Agent), 기본 기술문서 체계, 웹 아키텍처, 보안·SEO 거버넌스, 55개 학습 아카이브를 집약한 포트폴리오 단행본 |
| 코드 설명 | `docs/code-reference.pdf` | 함수·클래스 설명, 인자, 반환, 유사코드 |
| 코드북 | `docs/codebook.pdf` | 화면과 빌드 소스를 파일 순서대로 읽은 설명 |
| 소스 모음 | `docs/source-bundle.pdf` | 주석이 붙은 소스를 파일 순서대로 이어 둔 본문 |
| 기술명세 | `docs/technical-specs.pdf` | 요구사항, 유스케이스, 자료 흐름도, 자료 사전, 화면 흐름, 프로세스 명세, 상태 전이, 구조도, 시험 명세 |

기술명세와 포트폴리오 북의 차트는 그림으로 들어갑니다. 유스케이스의 행위자는 사람 그림이고, 자료 흐름도의 작성자·방문자는 외부 실체 상자입니다. 같은 내용의 마크다운과 HTML도 `docs/`에 있습니다.

문서를 다시 만들 때:

```powershell
python docs/build_portfolio_book.py
python docs/build_code_reference.py
python docs/build_codebook.py
python docs/build_source_bundle.py
python docs/build_specs.py
```

명세 차트는 Edge 또는 Chrome으로 그립니다. 차트 문장이 바뀌면 그 그림을 새로 만들기 위해 인터넷 연결이 필요합니다.

## 로컬에서 확인하기

별도 설치 과정은 필요하지 않습니다.

1. 저장소를 내려받습니다.
2. `index.html`을 브라우저로 엽니다.
3. 상단 메뉴에서 자기소개, 온라인 명함, 이력서, 학습록 페이지로 이동합니다.

학습록 대시보드는 프로젝트 루트에서 로컬 서버를 띄운 뒤 `/study_note_record_organization/dashboard/`로 접속하는 것이 좋습니다(히어로 이미지 경로).

VS Code나 Cursor를 사용한다면 Live Server 같은 확장 프로그램으로 실행하면 페이지 이동과 리소스 확인이 더 편합니다.

## GitHub Pages 배포

GitHub 저장소에 업로드한 뒤 Pages 설정에서 배포할 수 있습니다.

1. GitHub 저장소를 생성합니다.
2. 프로젝트 파일을 저장소에 업로드합니다.
3. GitHub 저장소의 `Settings > Pages`로 이동합니다.
4. 배포 브랜치와 루트 폴더를 선택합니다.
5. 배포 URL에서 `index.html` 기준으로 사이트가 열리는지 확인합니다.
6. 학습록: `https://<username>.github.io/study_note_record_organization/dashboard/index.html`
7. 프로젝트 아카이브: `https://<username>.github.io/portfolio_achieve/index.html`

학습록 데이터 갱신 시:

```powershell
cd study_note_record_organization
python scripts/build_output.py
python scripts/build_static_site.py
```

## 개인정보 공개 주의

GitHub Pages는 공개 웹사이트로 배포될 수 있으므로, 업로드 전 개인정보를 꼭 확인해야 합니다.

- 실명, 얼굴 사진, 나이, 성별, 정확한 학교명은 공개 범위를 신중히 결정합니다.
- 이력서 제출용 정보와 공개 포트폴리오용 정보는 분리하는 것을 권장합니다.
- 블로그 링크를 공개할 경우 블로그에 포함된 개인정보도 함께 점검합니다.
- 공개가 부담되는 내용은 `대학 졸업`, `학점은행제 도전 중`처럼 일반화해 표현합니다.

## 수정 가이드

- 메인 자기소개 문구: `index.html`
- 프로필 페이지 내용: `cover_letter/profile.html`
- 온라인 명함 문구와 애니메이션: `online_business_card/business-card.html`, `online_business_card/js/script.js`
- 이력서 내용: `cv/resume.html`
- 학습록 아카이브: `study_note_record_organization/dashboard/`, 빌드 스크립트 `study_note_record_organization/scripts/`
- 포트폴리오 북: `docs/portfolio-book/`을 고친 뒤 `python docs/build_portfolio_book.py`
- 코드 설명: 함수·클래스 주석을 고친 뒤 `python docs/build_code_reference.py`
- 코드북: `docs/codebook/`을 고친 뒤 `python docs/build_codebook.py`
- 소스 모음: `python docs/build_source_bundle.py`
- 기술명세: `docs/specs/`를 고친 뒤 `python docs/build_specs.py`
- 공통 헤더 스타일: `css/site-header.css`
- 메인 페이지 스타일: `css/styles.css`
- 복사·접근 안내: `js/protect-resources.js`
- 검색·수집 범위: `robots.txt`, `.well-known/tdmrep.json`

## 제작 정보

2026년 5월 25일 제작. Cursor AI를 사용해 HTML, CSS, JavaScript 기반 정적 페이지로 구성했습니다.

자료를 제외한 문장이나 문구는 나의 생각을 프롬프트에 요청하여 생성한 문장이나 문구입니다. 학습록의 독서·강의·과제 원문과 요약은 자료로 두고, 이 문장의 대상에서 빼 둡니다. 같은 문장을 공개 페이지 하단의 제작 문구 다음에 둡니다.

저작권 표기는 `© 2026 김신욱(깃허브 ackdark23358). All rights reserved.`입니다.

## 공개 페이지에 반영한 사항

- 하단에 저작권 표기와, 페이지·섹션이 모두 펼쳐진 사이트맵을 두었습니다.
- 제작 문구 다음에 문장 생성 표시를 두었습니다. 학습·과제 자료는 그 표시에서 제외합니다.
- 학점은행제 전공을 '멀티미디어학'으로 정정하여 자기소개서, 프로필, 이력서, 포트폴리오 북 및 기술문서 전반에 일원화 반영했습니다.
- 복사, 잘라내기, 우클릭을 시도하면 `자료에 대해서 퍼가는 것을 방지하였습니다.`를 보여 줍니다. 페이지 스크롤은 그대로 둡니다.
- `robots.txt`는 자기소개, 명함, 이력서, 학습록, `docs/` 경로를 일반 검색에서 제외합니다. 메인 자기소개서는 검색에 남기고, 검색엔진 보관 복사본은 `noarchive`로 만들지 않습니다. 대표 주소는 `https://ackdark23358.github.io/`입니다.
- GPTBot, Google-Extended, ClaudeBot, PerplexityBot 등 학습·생성형 검색 로봇은 사이트 전체를 거절합니다. 페이지의 `tdm-reservation`과 `.well-known/tdmrep.json`도 텍스트·데이터 마이닝 거절을 표시합니다.
- 허용 주소는 `ackdark23358.github.io`, `localhost`, `127.0.0.1`입니다. 다른 주소로 옮기거나 iframe에 끼우면 본문 대신 안내가 나옵니다. 학습록은 허용되지 않은 주소에서 목록과 원문 요청을 그리지 않습니다.
- Cursor AI 바이브 코딩(Ask, Plan, Agent 모드) 개발 방법론 및 엔지니어링 아카이브를 집약한 단행본 `portfolio-book.pdf`를 포함해 5종의 PDF 기술문서를 완비하고 자동 빌드 파이프라인을 구축했습니다.

GitHub Pages는 서버 비밀번호를 두지 못합니다. 공개 저장소의 파일 주소와 저장소 복제는 페이지 스크립트와 별개로 열립니다.
