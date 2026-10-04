# 온라인 명함

## 이 파일이 맡는 일

`online_business_card/business-card.html`은 긴 스크롤 구간 위에 명함을 고정해 두고, 스크롤에 따라 카드를 뒤집고 확대한다. 동작은 `online_business_card/js/script.js` 한 파일이다. `DOMContentLoaded`에서 카드, 스크롤 컨테이너, 이력 절, 스크롤 안내를 찾고 스크롤 리스너와 관찰자를 붙인다.

`online_business_card/css/style.css`는 `.scroll-container`의 높이와 카드의 `position: sticky`, 앞면·뒷면, `.resume-content section`의 숨김과 `.visible` 표시를 정한다. 스크립트는 transform과 opacity, `is-hidden`, `visible`만 바꾸고 레이아웃 숫자의 대부분은 CSS에 있다.

HTML에서 이 스크립트가 찾는 조각은 이렇다.

- `#card`: transform을 받는 명함
- `.scroll-container`: 진행률의 기준 높이
- `.resume-content section`: 20% 이상 보이면 `visible`
- `#scrollHint`: 24px보다 많이 내리면 `is-hidden`

## 읽는 순서

1. 요소를 찾고 `ticking`을 거짓으로 둔다.
2. `updateAnimation`을 정의하고 스크롤마다 `requestAnimationFrame`으로 한 번만 부른다.
3. 로드 직후 `updateAnimation`을 한 번 실행한다.
4. 이력 절에 `IntersectionObserver`를 붙인다.

## 구간 설명

### updateAnimation

인자는 없다. `scrollY / (scrollContainer 높이 - 뷰포트 높이)`를 0과 1 사이로 자른 값이 `progress`다. 컨테이너가 뷰포트보다 작으면 분모가 0 이하가 되어 진행률이 숫자가 아닐 수 있다. 그 경우 뒤의 비교는 거짓 쪽으로 떨어져 앞 단계 분기로 가지 않는다.

진행률 0 이상 0.5 이하는 뒤집기다. `flipProgress`는 `progress / 0.5`다. `rotateX`는 10도에서 0도로 줄고, `rotateY`는 -15도에서 180도 쪽으로 195도를 곱해 더한다. `scale`은 1이고 opacity는 1이다.

0.5를 넘으면 확대다. `rotateX`는 0, `rotateY`는 180으로 고정한다. `scaleProgress`를 세 번 곱한 `easeScale`로 점점 가속하고, `scale`은 `1 + 40 * easeScale`이다. 끝에서는 약 41배다.

```javascript
if (progress <= 0.5) {
    const flipProgress = progress / 0.5;
    rotateY = -15 + (195 * flipProgress);
    scale = 1;
} else {
    const easeScale = scaleProgress * scaleProgress * scaleProgress;
    scale = 1 + (40 * easeScale);
}
```

계산이 끝나면 `#card`의 `transform`에 `rotateX`, `rotateY`, `scale`을 한 줄로 넣는다. `#scrollHint`가 있으면 `scrollY > 24`일 때 `is-hidden`을 붙인다. 맨 아래 `ticking`을 거짓으로 되돌려 다음 스크롤이 다시 프레임을 요청할 수 있게 한다.

### 스크롤 리스너

스크롤마다 `ticking`이 거짓일 때만 `requestAnimationFrame(updateAnimation)`을 요청하고 `ticking`을 참으로 둔다. 한 프레임 안에 스크롤이 여러 번 와도 `updateAnimation`은 한 번만 돈다. 로드 직후 한 번 호출하므로 새로고침 때의 스크롤 위치도 반영된다.

### 이력 절 관찰

`threshold` 0.2다. 절이 뷰포트의 20% 이상 교차하면 `visible`을 붙인다. 교차가 끝나면 `visible`을 뺀다. 한 번 나타난 뒤 관찰을 끊지 않으므로, 위로 올리면 절이 다시 숨는 클래스 상태로 돌아간다. 관찰자 콜백의 두 번째 인자는 쓰이지 않는다.

## 이 파일이 부르는 다른 파일

다른 JS 모듈을 부르지 않는다. `business-card.html`이 CSS와 이 스크립트를 읽는다. 공통 헤더를 포함했다면 테마는 그 페이지의 테마 스크립트가 따로 처리한다.
