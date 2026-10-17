# 리소스 보호 및 보안 가드

## 이 파일이 맡는 일

`js/protect-resources.js`는 정적 호스팅(GitHub Pages) 환경에서 무단 복사, 스크랩, 악의적인 iframe 끼워 넣기를 방지하고 방문자에게 안내를 제공하는 클라이언트 보안 스크립트다.

함께 동작하는 거버넌스 설정은 다음과 같다:
- `robots.txt`: 일반 검색엔진에는 메인 페이지만 색인하도록 하고, 하위 자료 폴더와 17종의 인공지능 학습 크롤러는 사이트 전체에서 거절한다.
- `.well-known/tdmrep.json`: TDM(Text and Data Mining) 권리 유보 선언을 머신러닝 수집기에 전달한다.

## 읽는 순서

1. 허용 호스트(`ALLOWED_HOSTS`) 및 상수 정의 (`MESSAGE`, `HIDE_MS`)
2. `isEmbedded`, `allowedHost`, `window.__portfolioGuard`
3. 차단 화면 그리기 (`paintBlockedPage`) 및 조건 검사
4. 안내 토스트 스타일 및 키프레임 주입 (`#resource-protect-notice`)
5. 입력 요소 판별 (`isEditable`), 안내 표시 (`showNotice`), 이벤트 차단 (`block`)
6. 마우스 이벤트 리스너 및 키보드 단축키 리스너 등록

## 구간 설명

### isEmbedded

`window.top !== window.self`를 검사한다. 교차 출처 iframe에 갇혀 예외가 발생하더라도 `catch`에서 참을 돌려주어 임베딩 상태로 판단한다.

### allowedHost

접속 프로토콜이 `http:` 또는 `https:`인지 확인하고, `window.location.hostname`이 `ackdark23358.github.io`, `localhost`, `127.0.0.1`에 해당하는지 검사한다.

### paintBlockedPage

비인가 호스트나 iframe 환경일 때 실행된다. `document.body`의 내용을 모두 비우고 검은 배경에 "자료에 대해서 퍼가는 것을 방지하였습니다."라는 문구만 전체 화면 중앙에 띄운다. 본문 스크립트와 스타일 주입은 즉시 중단된다.

### isEditable

이벤트가 발생한 대상 요소(`event.target`)가 검색창이나 텍스트 입력창(`input`, `textarea`, `select`, `contenteditable`) 내부인지 검사한다. 학습록 대시보드에서 방문자가 검색어를 타이핑하는 동작이 차단되지 않도록 보호한다.

### showNotice와 block

`copy`, `cut`, `contextmenu`(우클릭), `dragstart`, `selectstart` 이벤트 및 `Ctrl+C`, `Ctrl+X`, `Ctrl+A`, `Ctrl+S`, `Ctrl+U` 단축키가 발생하면 `e.preventDefault()`로 가로채고 `showNotice()`를 호출한다. 하단에 토스트 팝업이 부드럽게 떠올랐다가 2.6초 뒤 사라진다.

## 이 파일이 부르는 다른 파일

외부 의존성은 없다. 6개 공개 HTML(`index.html`, `profile.html`, `business-card.html`, `resume.html`, `study_note_record_organization/dashboard/index.html`, `portfolio_achieve/index.html`) 및 프로젝트 상세 페이지의 바닥에서 로드되어 독립적으로 동작한다.
