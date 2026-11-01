# DOC_JAVA_CHATPROGRAM_PROJ

자바 채팅 프로그램을 [코탐록 프로젝트 아카이브](https://ackdark23358.github.io/portfolio_achieve/index.html)에 넣기 위한 문서 폴더입니다. 초안은 PROJ_17 다음인 PROJ_18로 적었습니다. 사원관리 프로그램이 먼저 PROJ_18이 되어, 아카이브 카드는 **PROJ_19 자바 채팅**으로 반영했습니다. 아카이브 이미지 이름은 `proj-19-`입니다.

원본 사이트 저장소는 `ackdark23358/ackdark23358.github.io`이고, 카드가 있는 파일은 `portfolio_achieve/index.html`입니다. 이 폴더는 그 저장소가 아니라 채팅 프로그램 폴더 안에 있습니다. 카드를 올리기 전에 아래 파일을 아카이브 쪽으로 복사합니다.

## 문서

| 파일 | 내용 |
| --- | --- |
| [01-archive-card.md](01-archive-card.md) | 카드 문장, 히어로 목록에 넣을 한 줄, `index.html`에 붙일 HTML |
| [02-overview.md](02-overview.md) | 무엇을 다시 만들었는지, 확인한 날짜, 화면 4장 |
| [03-specification.md](03-specification.md) | 요구사항, 사용 흐름, 화면, 접속 상태, 메시지 규칙 |
| [04-source-guide.md](04-source-guide.md) | 소스 파일별 역할과 스트림 연결 |
| [05-run.md](05-run.md) | 이클립스, 배치 파일, 다른 PC 접속 |

## 화면 파일

카드 대표 이미지는 대화 중인 클라이언트입니다. 나머지 세 장은 서버 시작, 입장, 서버에서 본 접속자입니다.

```text
img/proj-18-client-chat.png     카드에 넣는 대표 화면
img/proj-18-server-start.png    서버 실행
img/proj-18-client-joined.png   한 명 입장
img/proj-18-server-room.png     서버의 접속자와 로그
```

## 아카이브에 넣는 순서

1. `img/` 안의 PNG 4개를 `portfolio_achieve/img/`로 복사합니다.
2. `portfolio_achieve/index.html`의 PROJ_17 카드 아래, `다음 프로젝트 카드는 이 주석 아래에` 주석 앞에 [01-archive-card.md](01-archive-card.md)의 `<article>`을 붙입니다.
3. 같은 파일 히어로의 `범위`와 `현재` 문장에 PROJ_18을 한 줄 추가합니다. 문장은 카드 문서에 적어 두었습니다.
4. 목록 안내 문장에 확인 날짜를 보강합니다. 이 프로젝트 화면은 2026년 11월 2일에 로컬에서 실행해 찍었습니다.
5. 브라우저로 `portfolio_achieve/index.html`을 열어 카드, 이미지, 히어로 목록이 이어지는지 확인합니다.

호스팅 주소는 넣지 않습니다. 이 프로그램은 로컬에서 서버를 실행하는 데스크톱 프로그램이고, 공개 URL이 없습니다.
