# 메인 페이지와 공통 헤더

## 이 파일이 맡는 일

`index.html`은 지원 동기, 성장·학습, 역량, 자료, 강점, 마치며, 참고 절을 담은 정적 페이지다. 동작은 `js/main.js`가 맡는다. 즉시 실행 함수 하나가 내비게이션, 자료 드롭다운, 테마를 연결한다. 상단 막대의 배치와 색은 `css/site-header.css`가, 본문 절의 배치는 `css/styles.css`가 맡는다.

`index.html`의 읽는 조각은 이렇다.

- `header.site-header`: 브랜드, `nav#site-nav`, 테마 버튼
- 절 링크: `#section-motivation`, `#section-growth`, `#section-skills`, `#section-strengths`, `#section-closing`, `#section-refs`
- 자료 드롭다운: 같은 페이지의 `#section-links`, 그리고 자기소개, 명함, 이력서, 학습 기록으로 나가는 링크
- `main#main`: 히어로 문구와 본문 절

`css/site-header.css`는 `html[data-theme="light"]`일 때의 색, 링크와 햄버거 버튼의 포커스, 768px 이하에서 메뉴를 접는 배치를 정한다. 769px 이상에서는 메뉴가 한 줄로 펼쳐진다. `css/styles.css`는 메인 본문의 히어로, 절, 카드 간격을 정하고 테마 변수에 맞춰 글자색을 바꾼다.

## 읽는 순서

파일은 저장 키와 도우미부터 선언하고, 맨 아래에서 DOM이 준비되면 초기화 함수 넷을 부른다.

1. `prefersReducedMotion`, `queryAll`, `queryAllIn`
2. `initSmoothNav`, `initResourceDropdown`, `initThemeToggle`
3. `applyTheme`, `getStoredTheme`, `setStoredTheme`
4. `setResourceDropdown`, `closeResourceDropdowns`, `closeMobileNav`, `setMobileNav`, `debounce`
5. `initSectionTargets`
6. `DOMContentLoaded` 또는 이미 준비된 문서에서 초기화

테마 저장 키는 `portfolio-theme-v2`다. 다른 페이지의 테마 스크립트도 같은 키를 쓴다.

## 구간 설명

### prefersReducedMotion

인자는 없다. `matchMedia("(prefers-reduced-motion: reduce)")`가 있으면 그 `matches`를 돌려주고, 없으면 거짓이다. 참이면 절 이동 스크롤이 `auto`, 거짓이면 `smooth`다.

### queryAll, queryAllIn

`queryAll`은 문서 전체에서 선택자와 맞는 요소를 배열로 돌려준다. `queryAllIn`은 같은 일을 한 요소 안에서만 한다. `NodeList`를 배열로 바꾸어 `forEach`를 쓰기 위한 도우미다.

### initSmoothNav

`#site-nav`와 `.nav-toggle`을 찾는다. `.site-nav__link` 중 `href`가 `#`으로 시작하고 길이가 2 이상인 것만 클릭을 가로챈다. 대상 id가 없으면 그 클릭은 무시하고 브라우저 기본 이동을 막지 않는다. 대상이 있으면 스크롤하고 `closeMobileNav`를 부른 뒤, 그 절에 `preventScroll`로 포커스를 준다.

햄버거 버튼이 있으면 `is-open`의 반대로 `setMobileNav`를 부른다. Escape는 메뉴가 열려 있을 때만 닫고 버튼으로 포커스를 돌린다. `resize`는 `debounce` 150밀리초 뒤에, 너비가 768px보다 크면 메뉴를 닫는다.

```javascript
if (window.innerWidth > 768 && nav && toggle) {
  closeMobileNav(nav, toggle);
}
```

### initResourceDropdown

각 `.site-nav__dropdown`의 토글 버튼을 연결한다. 클릭하면 다른 드롭다운을 닫고, 이 버튼의 `aria-expanded`가 `true`가 아니면 연다. 이미 열려 있으면 닫는다.

드롭다운 링크가 페이지 안 `#` 링크이고 대상 절이 있으면 그 절로 스크롤하고 포커스를 준다. 다른 페이지로 가는 링크는 기본 이동을 막지 않는다. 어느 쪽이든 이어서 드롭다운과 모바일 메뉴를 닫는다.

문서 클릭이 드롭다운 밖이면 모두 닫는다. Escape도 드롭다운을 모두 닫는다. 이 Escape 처리와 `initSmoothNav`의 Escape는 따로 등록된다. 메뉴가 열려 있으면 모바일 메뉴 쪽도 닫힌다.

### initThemeToggle

`[data-theme-toggle]`이 없으면 바로 돌아간다. 저장값이 있으면 그것을, 없으면 `html`의 `data-default-theme`를, 그것도 없으면 `dark`를 쓴다. `applyTheme`로 화면에 반영한 뒤 버튼 클릭과 `storage` 이벤트를 연결한다.

클릭은 현재 `data-theme`가 `light`면 `dark`로, 아니면 `light`로 뒤집는다. `setStoredTheme` 다음에 `applyTheme`를 부른다. 다른 탭이 같은 키를 바꾸면 `storage`가 그 값으로 맞춘다. 새 값이 비어 있으면 다시 기본 테마나 `dark`로 간다.

### applyTheme

인자 `theme`은 `light`만 라이트로 두고 나머지는 `dark`로 정규화한다. 되돌리는 값은 없다. `html`의 `data-theme`를 바꾸고, 버튼의 `aria-pressed`는 다크일 때 `true`다. `aria-label`은 지금 테마의 반대로 전환한다고 안내하고, `[data-theme-label]` 문구는 `다크` 또는 `라이트`다.

### getStoredTheme, setStoredTheme

`getStoredTheme`는 `localStorage.getItem` 결과를 돌려준다. 읽기가 실패하면 `null`이다. `setStoredTheme`는 같은 키에 쓴다. 쓰기가 실패하면 예외를 삼키므로 메모리와 화면만 바뀌고 다음 방문에는 기본값으로 돌아간다.

### setResourceDropdown, closeResourceDropdowns

`setResourceDropdown(dropdown, open)`은 `is-open` 클래스, 버튼의 `aria-expanded`, 메뉴의 `hidden`을 같이 맞춘다. `closeResourceDropdowns(except)`는 `except`와 같은 요소만 남기고 나머지를 닫는다. `except`를 생략하면 전부 닫는다.

### closeMobileNav, setMobileNav

`closeMobileNav`는 `setMobileNav(..., false)`다. `setMobileNav`는 `nav`나 `toggle`이 없으면 아무 것도 하지 않는다. 열림이면 `is-open`과 `메뉴 닫기`, 닫힘이면 클래스 제거와 `메뉴 열기`다. 닫을 때만 `closeResourceDropdowns`를 부른다.

### debounce

`debounce(fn, wait)`는 타이머를 저장하는 함수를 돌려준다. 다시 호출되면 이전 타이머를 지우고 `wait` 뒤에 `fn`을 한 번 실행한다. 창 크기 변경에서 메뉴를 반복해서 닫지 않으려고 쓴다.

### initSectionTargets

`id`가 있는 `.section`에 `tabindex`가 없으면 `-1`을 넣는다. 메뉴로 이동한 뒤 그 절이 키보드 포커스를 받을 수 있게 한다. 이미 있는 `tabindex`는 건드리지 않는다.

### 시작점

`document.readyState`가 `loading`이면 `DOMContentLoaded`에서, 아니면 바로 `initSmoothNav`, `initResourceDropdown`, `initThemeToggle`, `initSectionTargets`를 부른다.

## 이 파일이 부르는 다른 파일

`js/main.js`는 다른 스크립트를 부르지 않는다. `index.html`이 `css/site-header.css`, `css/styles.css`, `js/main.js`를 읽는다. 자료 메뉴의 바깥 페이지는 각 페이지의 HTML로 넘어간다.
