# 히어로 갤러리

## 이 파일이 맡는 일

`dashboard/js/hero.js`는 대시보드 상단의 사진 두 장을 겹쳐 두고 번갈아 보여 준다. 즉시 실행 함수이고, DOM이 준비되면 `initHero`만 부른다. 카드 목록과는 상태를 공유하지 않는다.

상수는 `AUTO_MS` 5500과 `FADE_MS` 1200이다. `FADE_MS`는 이 파일 안에서 타이머로 쓰이지 않는다. 사라지는 시간은 CSS 전환이 맡는다.

HTML 조각은 `#hero`, `#hero-stage`, `#hero-img-a`, `#hero-img-b`다. 두 이미지가 같은 자리에 겹치고, `.is-visible`인 쪽만 보인다.

## 읽는 순서

1. `heroSrc`, `getHeroImages`
2. `initHero` 안에서 `visibleImg`, `hiddenImg`, `pickIndex`, `applyImage`, `swapTo`, `nextRandom`, `startTimer`
3. 첫 장을 고르고 클릭과 타이머를 연결한다

## 구간 설명

### heroSrc, getHeroImages

`heroSrc(rel)`은 `data/image` 기준 상대 경로에서 마지막 슬래시 뒤 파일 이름만 `encodeURIComponent`한다. 슬래시가 없으면 경로 전체를 `encodeURI`한다. 디렉터리 구분 슬래시는 인코딩하지 않는다.

`getHeroImages`는 `window.HERO_IMAGES`가 비어 있지 않으면 그것을 돌려준다. 없으면 `window.SITE_DATA.heroImages`를 본다. 둘 다 없으면 빈 배열이다. 지금 빌드는 `hero-images.js`에 `window.HERO_IMAGES`를 넣으므로 보통 첫 갈래를 탄다.

### initHero

네 요소 중 하나라도 없으면 돌아간다. 이미지 목록이 비면 `#hero`에 `hidden` 클래스를 넣고 끝난다. 목록이 있으면 `hidden` 클래스와 `hidden` 속성을 제거한다.

안의 상태는 `current` 인덱스, 지금 A가 보이는지(`showA`), 전환 중인지(`busy`), `timer`다.

`visibleImg`와 `hiddenImg`는 `showA`에 따라 `#hero-img-a`와 `#hero-img-b` 중 하나를 돌려준다.

`pickIndex`는 목록이 한 장이면 0이다. 두 장 이상이면 `current`와 다른 인덱스가 나올 때까지 무작위로 고른다.

`applyImage`는 그 인덱스의 경로를 `heroSrc`로 바꿔 `src`에 넣고, `alt`는 `학습·과제 기록 갤러리 이미지`로 고정한다.

`swapTo(index)`는 `busy`이거나 `index`가 `current`와 같으면 아무 것도 하지 않는다. 아니면 `busy`를 참으로 두고, 숨은 이미지에 `applyImage`를 한 뒤 `current`를 먼저 바꾼다. 그 이미지가 이미 로드되어 있으면 바로 `finish`한다. 아니면 `onload`에서 `finish`하고, `onerror`에서는 `busy`만 거짓으로 되돌린다. 실패하면 보이던 장은 유지되고 `current`만 새 인덱스로 남아, 다음 무작위가 그 인덱스를 피할 수 있다.

`finish`는 새 이미지에 `is-visible`을 붙이고 이전 이미지에서 뺀다. `showA`를 새 이미지가 A인지로 맞추고 `busy`를 거짓으로 둔다.

`nextRandom`은 `pickIndex` 결과로 `swapTo`를 부른다.

`startTimer`는 기존 인터벌을 지운다. `prefers-reduced-motion: reduce`이거나 이미지가 한 장이면 새 인터벌을 만들지 않는다. 그 외에는 5500밀리초마다 `nextRandom`을 부른다.

초기화의 마지막은 첫 `pickIndex`로 A에 그림을 넣고 `is-visible`을 붙이는 것이다. 스테이지 클릭은 `nextRandom` 뒤 `startTimer`를 다시 불러 자동 전환 시간을 처음부터 센다. 동작 줄이기가 켜져 있으면 클릭으로만 넘긴다.

## 이 파일이 부르는 다른 파일

`hero-images.js`의 `window.HERO_IMAGES` 또는 `data.js`의 `heroImages`를 읽는다. `app.js`의 함수는 부르지 않는다. `dashboard/index.html`이 두 스크립트를 모두 읽는다.
