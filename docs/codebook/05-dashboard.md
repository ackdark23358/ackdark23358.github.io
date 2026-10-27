# 학습 기록 대시보드

## 이 파일이 맡는 일

`study_note_record_organization/dashboard/index.html`은 히어로, 소개, 검색, 카드 그리드, 요약 모달, 원본 보기를 담는다. 카드와 모달의 동작은 `dashboard/js/app.js`다. 히어로 전환은 `hero.js`가 맡으며 다음 장에서 읽는다. 스타일은 `dashboard/css/styles.css`가 카드, 모달, 빈 상태, 히어로 겹침을 정한다.

페이지가 읽는 데이터는 빌드가 만든 `js/data.js`의 `window.SITE_DATA`다. 필드가 쓰이는 곳은 이렇다.

- `catalog`: 카드 배열. `type`, `title`, `slug`, `summary`, `tags`
- `articles`: 슬러그에서 요약 HTML로
- `sourceMap`: 원본 키에서 `js/sources/` JSON 파일 이름으로
- `sourceBuildId`: 원본 요청의 `v` 쿼리
- `sources`: 옛 형식. `sourceMap`이 없을 때만 캐시로 복사한다

HTML 조각은 `#subtitle`, `#info-compose`, `#note`, `#footer-count`, `#search`, `#grid`, `#empty`, `#modal-overlay`, `#modal-meta`, `#modal-body`, `#modal-close`, `#source-overlay`, `#source-title`, `#source-body`, `#source-close`다.

파일 안의 상태는 `catalog`, `articles`, `sourceMap`, `sourceCache`, `sourceBuildId`, `searchQuery`다. 검색어만 입력할 때마다 바뀌고, 나머지 데이터는 `init`에서 한 번 채워진다.

## 읽는 순서

선언과 DOM 조회 다음에 함수가 나오고, 파일 끝에서 닫기·검색·`init`을 연결한다.

1. `escapeHtml`, `getData`, `renderIntro`, `filteredItems`, `renderGrid`
2. `isAssignmentSourceKey`, `maskAssignmentPrivacy`, `htmlToPlainText`, `getSourceExtraImage`, `renderPlainSource`
3. `resolveSourceChunk`, `fetchSourceText`, `sourceDisplayName`, `openSourceViewer`, `closeSourceModal`
4. `bindSourceLinks`, `openModal`, `closeModal`, `init`
5. 버튼, 배경, Escape, 검색 입력, `DOMContentLoaded`

## 구간 설명

### escapeHtml, getData

`escapeHtml`은 임시 `div`의 `textContent`에 넣은 뒤 `innerHTML`을 돌려준다. `null`과 `undefined`는 빈 문자열이다. 카드 제목처럼 사용자 글을 HTML에 넣을 때 쓴다. 요약 본문 HTML은 빌드 결과이므로 이 함수를 거치지 않고 `innerHTML`에 들어간다.

`getData`는 `window.SITE_DATA`가 없으면 `null`이다.

### renderIntro

카탈로그를 돌며 `type`이 `study`와 `assignment`인 개수를 센다. 그 외 종류는 총계에만 들어간다. `#subtitle`에는 고정 소개 문구를 넣는다. `#info-compose`에는 학습 건수와 과제 건수를 HTML로 넣는다. 숫자는 카탈로그에서 세므로 태그가 되지 않는다. `#note`에는 총개수와 두 빌드 명령을 적는다. `#footer-count`는 `총 N개 기록`이다. 푸터 줄은 그 기록 수, 정적 HTML/CSS/JavaScript, 코탐록 메인 링크만 두고 빌드 명령은 적지 않는다. 요소가 없으면 그 칸만 건너뛴다.

### filteredItems, renderGrid

`filteredItems`는 `searchQuery`의 앞뒤 공백을 지우고 소문자로 만든다. 비어 있으면 카탈로그 전체를 돌려준다. 있으면 제목, 요약, 종류, 배지 문구, 태그를 한 문자열로 붙여 그 안에 검색어가 있는 항목만 남긴다. 태그가 없으면 빈 배열로 둔다. 배지 문구는 `book`이 독서, `course`가 강의, `cert`가 자격, `tool`이 도구다.

`renderGrid`는 `#grid`를 비운다. 결과가 없으면 `#empty`의 `hidden`을 제거하고 돌아간다. 있으면 빈 문구를 숨기고, 항목마다 `button.card.card--종류`를 만든다. 라벨은 `study`면 `STUDY NOTE`, `assignment`면 `ASSIGNMENT`, 그 외는 `RECORD`다. 학습 카드에는 그 옆에 배지를 둔다. 배지 문구는 독서, 강의, 자격, 도구 네 가지뿐이다. 과제 카드에는 배지를 붙이지 않는다. 제목과 요약은 `escapeHtml`을 거친다. 요약이 없으면 `요약 없음`이다. 클릭하면 그 항목으로 `openModal`을 부른다. 요약 모달의 윗줄에도 같은 라벨과 배지를 둔다.

### 원본 가리기와 평문

`isAssignmentSourceKey`는 경로에 `과제분류하기` 또는 `data_과제분류하기`가 있으면 참이다.

`maskAssignmentPrivacy`는 문자열을 돌려준다. 지도교수 줄은 `OOO 교수님`으로, 학번과 수강번호 숫자는 `OOOOOOOO`로 바꾼다. 괄호 안 7~8자리와 밑줄로 감싼 7~8자리도 같은 마스크다. 이 함수는 화면에서 원본을 열 때 한 번 더 적용된다. 빌드가 이미 가렸어도 같은 규칙을 다시 통과한다.

`htmlToPlainText`는 `DOMParser`로 HTML을 파싱해 `body.innerText`를 돌려준다. 본문이 없으면 입력 문자열을 그대로 둔다.

`getSourceExtraImage`는 키를 한 번 디코드한 뒤, `데이터베이스`와 `총괄`이 같이 있으면 ER 그림 정보 `{ src, alt, caption }`을 돌려준다. `src`는 `assets/database-er-diagram.png`다. 아니면 `null`이다. 디코드가 실패하면 원래 키로 검사한다.

`renderPlainSource`는 원문의 줄바꿈을 `\n`으로 맞추고 `escapeHtml`한 뒤 `.source-plain` HTML을 만든다. 추가 그림이 있으면 `figure`를 붙인다.

### 원본 불러오기

`resolveSourceChunk`는 `sourceMap[key]`를 먼저 본다. 없으면 키를 디코드해 한 번 더 본다. 둘 다 없으면 `null`이다.

`fetchSourceText`는 `sourceCache[key]`가 있으면 그 문자열로 바로 이행하는 프로미스를 돌려준다. 청크 이름이 없으면 `null`로 이행한다. 있으면 `js/sources/파일이름`을 현재 페이지 기준으로 만들고, `sourceBuildId`가 있으면 `v` 쿼리를 붙인다. `cache: "no-store"`로 `fetch`한다. 응답이 실패하면 거절되어 `catch`가 `null`을 돌려준다. 성공하면 `payload.text`를 캐시에 넣고, `payload.key`가 요청 키와 다르면 그 키에도 같은 텍스트를 넣는다.

`sourceDisplayName`은 링크 문구가 있으면 그것을, 없으면 경로의 마지막 조각을 쓴다. 끝의 `(텍스트 추출본)`은 뺀다. 결과가 비면 `원본`이다.

### openSourceViewer, closeSourceModal

`openSourceViewer(key, label)`은 원본 오버레이의 `hidden`을 빼고 `aria-hidden`을 거짓으로 둔다. `body`의 `overflow`를 `hidden`으로 잠근다. 요약 모달이 아직 보이면 그 오버레이의 `pointerEvents`를 `none`으로 두어 원본이 위에 있는 동안 요약 쪽 클릭을 막는다.

제목을 넣고 본문은 `원본을 불러오는 중…`으로 바꾼 뒤 `fetchSourceText`를 기다린다. 텍스트가 `null`이면 `build_static_site.py`를 실행하라는 오류를 보여 준다. 키가 `.html` 또는 `.htm`으로 끝나면 `htmlToPlainText`를 먼저 적용한다. 과제 경로면 `maskAssignmentPrivacy`를 적용한다. 그 다음 `renderPlainSource` 결과로 본문을 바꾼다.

`closeSourceModal`은 원본 오버레이를 숨기고 `pointerEvents`를 비운다. 요약 모달도 숨겨져 있을 때만 `body` 스크롤 잠금을 푼다. 요약이 남아 있으면 잠금은 유지된다.

### bindSourceLinks, openModal, closeModal

`bindSourceLinks`는 컨테이너 클릭에서 `a[data-source]` 또는 `a.source-link`만 가로챈다. 기본 이동과 버블을 막고, `data-source`가 있으면 `openSourceViewer`를 부른다. 키가 없는 링크는 이동만 막는다.

`openModal(item)`은 요약 오버레이를 열고 스크롤을 잠근다. 메타에는 라벨, 제목, 요약을 이스케이프해 넣는다. `articles[item.slug]`가 없으면 본문에 `요약본이 없습니다.`를 넣고 원본 링크는 연결하지 않는다. 있으면 `.md-content`로 넣고 `bindSourceLinks`를 부른다.

`closeModal`은 요약 오버레이를 숨긴다. 원본 오버레이가 숨겨져 있을 때만 스크롤 잠금을 푼다.

### init과 이벤트

`init`은 `SITE_DATA.catalog`가 없으면 그리드에 `data.js가 없습니다`를 넣고 돌아간다. 있으면 카탈로그, 요약 HTML, 원본 지도, 빌드 아이디를 채우고 캐시를 비운다. `sourceMap` 없이 `sources`만 있으면 그 객체를 캐시로 쓴다. 이어서 `renderIntro`와 `renderGrid`를 부른다.

닫기 버튼은 각 모달을 닫는다. 오버레이 배경을 직접 클릭했을 때만 닫고, 안쪽 클릭은 유지한다. Escape는 원본이 열려 있으면 원본만 닫고, 아니면 요약이 열려 있을 때 요약을 닫는다. 검색 입력은 `searchQuery`를 바꾸고 `renderGrid`만 다시 부른다. 소개 문구는 다시 그리지 않는다.

`readyState`가 `loading`이면 `DOMContentLoaded`에서 `init`하고, 아니면 바로 한다.

## 이 파일이 부르는 다른 파일

`window.SITE_DATA`는 `js/data.js`가 만든다. 원본 본문은 `js/sources/*.json`을 `fetch`한다. 히어로 목록은 읽지 않는다. 빌드 스크립트는 실행하지 않고, 데이터가 없을 때 명령 이름만 화면에 적는다.
