# 코탐록 이력서 & 자기소개 포트폴리오

IT·웹·모바일·AI 서비스 분야 취업 준비를 위해 제작한 정적 포트폴리오 사이트입니다. 자기소개서, 프로필, 온라인 명함, 이력서 페이지를 각각 분리해 관리하며, GitHub Pages 같은 정적 호스팅 환경에 배포할 수 있도록 구성했습니다.

## 프로젝트 소개

이 프로젝트는 지원자의 학습 과정과 관심 분야를 웹 페이지 형태로 정리한 개인 포트폴리오입니다.

- 자기소개서 내용을 기반으로 한 메인 랜딩 페이지
- 프로필과 관심 분야를 정리한 자기소개 페이지
- 스크롤 애니메이션이 있는 3D 온라인 명함
- 간단한 문서형 이력서 페이지
- 라이트/다크 테마 전환과 반응형 내비게이션

## 페이지 구성

| 페이지 | 경로 | 설명 |
| --- | --- | --- |
| 메인 자기소개서 | `index.html` | 지원 동기, 성장 과정, 보유 역량, 강점, 참고 정보를 담은 메인 페이지 |
| 자기소개 / 프로필 | `cover_letter/profile.html` | 프로필, 관심 분야, 학습 경험, 지원 동기 등을 정리한 페이지 |
| 온라인 명함 | `online_business_card/business-card.html` | 스크롤에 따라 명함이 회전하고 확대되는 인터랙티브 페이지 |
| 이력서 | `resume/resume.html` | 경력, 학력, 자격증을 간단히 정리한 문서형 이력서 |

## 주요 기능

- **정적 웹사이트 구성**: HTML, CSS, JavaScript만 사용해 별도 빌드 과정 없이 실행할 수 있습니다.
- **공통 헤더 내비게이션**: 주요 페이지를 상단 메뉴로 이동할 수 있습니다.
- **테마 전환**: 라이트/다크 테마를 전환하고 `localStorage`에 선택값을 저장합니다.
- **반응형 메뉴**: 모바일 화면에서도 메뉴 버튼으로 탐색할 수 있습니다.
- **온라인 명함 애니메이션**: 스크롤 위치에 따라 3D 명함이 회전하고 확대됩니다.
- **접근성 고려**: 스킵 링크, `aria` 속성, 키보드 탐색 보조 요소를 일부 적용했습니다.

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
├── 자기소개서.md
├── css/
│   ├── styles.css
│   └── site-header.css
├── js/
│   └── main.js
├── cover_letter/
│   ├── profile.html
│   ├── styles.css
│   ├── script.js
│   └── 자기소개서.txt
├── online_business_card/
│   ├── business-card.html
│   ├── cover_letter_draft.md
│   ├── style.css
│   └── script.js
└── resume/
    ├── resume.html
    ├── css/
    │   ├── reset.css
    │   └── style.css
    ├── js/
    │   ├── jquery-4.0.0.min.js
    │   └── ui.js
    └── img/
```

## 로컬에서 확인하기

별도 설치 과정은 필요하지 않습니다.

1. 저장소를 내려받습니다.
2. `index.html`을 브라우저로 엽니다.
3. 상단 메뉴에서 자기소개, 온라인 명함, 이력서 페이지로 이동합니다.

VS Code나 Cursor를 사용한다면 Live Server 같은 확장 프로그램으로 실행하면 페이지 이동과 리소스 확인이 더 편합니다.

## GitHub Pages 배포

GitHub 저장소에 업로드한 뒤 Pages 설정에서 배포할 수 있습니다.

1. GitHub 저장소를 생성합니다.
2. 프로젝트 파일을 저장소에 업로드합니다.
3. GitHub 저장소의 `Settings > Pages`로 이동합니다.
4. 배포 브랜치와 루트 폴더를 선택합니다.
5. 배포 URL에서 `index.html` 기준으로 사이트가 열리는지 확인합니다.

## 개인정보 공개 주의

GitHub Pages는 공개 웹사이트로 배포될 수 있으므로, 업로드 전 개인정보를 꼭 확인해야 합니다.

- 실명, 얼굴 사진, 나이, 성별, 정확한 학교명은 공개 범위를 신중히 결정합니다.
- 이력서 제출용 정보와 공개 포트폴리오용 정보는 분리하는 것을 권장합니다.
- 블로그 링크를 공개할 경우 블로그에 포함된 개인정보도 함께 점검합니다.
- 공개가 부담되는 내용은 `대학 졸업`, `학점은행제 도전 중`처럼 일반화해 표현합니다.

## 수정 가이드

- 메인 자기소개 문구: `index.html`
- 프로필 페이지 내용: `cover_letter/profile.html`
- 온라인 명함 문구와 애니메이션: `online_business_card/business-card.html`, `online_business_card/script.js`
- 이력서 내용: `resume/resume.html`
- 공통 헤더 스타일: `css/site-header.css`
- 메인 페이지 스타일: `css/styles.css`

## 제작 정보

2026년 제작. Cursor AI를 활용해 HTML, CSS, JavaScript 기반 정적 페이지로 구성했습니다.
