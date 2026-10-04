# 자기소개 페이지

## 이 파일이 맡는 일

`cover_letter/profile.html`은 프로필, 관심 분야, 학습 경험, 지원 동기를 절으로 나눈 페이지다. `cover_letter/js/script.js`는 지금 보이는 절에 맞춰 사이드 메뉴를 표시하고, 맨 위로 버튼을 연결한다. 즉시 실행 함수이고, DOM이 준비되면 `initScrollSpy`와 `initToTop`만 부른다.

`cover_letter/css/styles.css`는 본문 폭, 사이드 메뉴, 활성 링크, 맨 위로 버튼의 위치를 정한다. 공통 헤더가 있으면 테마와 모바일 메뉴는 `js/main.js`와 `css/site-header.css`가 맡는다. 이 파일은 테마 저장소를 건드리지 않는다.

HTML에서 이 스크립트가 찾는 조각은 이렇다.

- `.content-section[id]`: 관찰 대상 절
- `.nav-link[data-section]`: 절 id와 같은 값이면 활성
- `#toTop`: 맨 위로 버튼

## 읽는 순서

1. `setActiveNav`
2. `initScrollSpy`
3. `initToTop`
4. `DOMContentLoaded`에서 둘을 호출

## 구간 설명

### setActiveNav

인자 `id`는 현재 절의 id다. 되돌리는 값은 없다. 모든 `.nav-link`를 돌며 `data-section`이 `id`와 같으면 `is-active`를 붙이고, 아니면 뺀다. 한 번에 여러 링크가 같은 `data-section`을 가지면 그 링크들은 함께 활성이 된다.

### initScrollSpy

`.content-section[id]`가 없으면 바로 돌아간다. 있으면 `IntersectionObserver`를 만든다. 루트는 브라우저 뷰포트다. `rootMargin`은 `-20% 0px -55% 0px`라서 화면 가운데에 가까운 띠만 본다. `threshold`는 0, 0.25, 0.5, 0.75, 1이다.

항목이 교차하고 `intersectionRatio`가 0.25 이상일 때만 `setActiveNav(entry.target.id)`를 부른다. 비율이 그보다 작으면 활성 메뉴를 바꾸지 않는다. 스크롤로 절이 그 띠를 벗어나도 이전 활성 클래스를 이 콜백이 직접 지우지는 않는다. 다른 절이 조건을 만족할 때 `setActiveNav`가 나머지를 지운다.

관찰을 시작하기 전에 첫 절 id로 `setActiveNav`를 한 번 부른다. 그래서 로드 직후 메뉴는 첫 절을 가리킨다.

### initToTop

`#toTop`이 없으면 돌아간다. 클릭하면 `window.scrollTo({ top: 0, behavior: "smooth" })`만 한다. 동작 줄이기 설정을 보지 않으므로, 줄이기가 켜져 있어도 이 버튼은 부드러운 스크롤을 요청한다.

## 이 파일이 부르는 다른 파일

다른 스크립트를 임포트하지 않는다. `cover_letter/profile.html`이 CSS와 이 파일을 읽는다.
