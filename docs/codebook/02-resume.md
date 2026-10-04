# 이력서 기간

## 이 파일이 맡는 일

`cv/resume.html`은 경력, 학력, 자격증을 적은 문서형 페이지다. 기간 숫자는 HTML에 미리 적혀 있지 않다. `cv/js/ui.js`의 `fillCareerPeriods`가 각 경력 항목의 시작일과 종료일을 읽어 `.periodResult`에 괄호로 넣는다. 페이지는 jQuery의 `$(document).ready`에서 이 함수를 한 번 부른다. 이후 상태가 바뀌는 코드는 없다.

`cv/css/reset.css`는 브라우저 기본 여백을 지우는 리셋이다. `cv/css/style.css`는 문서 폭, 절 제목, 경력 항목의 줄을 정한다. 상단 헤더를 쓰는 페이지라면 공통 `css/site-header.css`와 테마 스크립트가 따로 연결된다. 기간 계산 자체는 테마와 무관하다.

경력 항목의 읽는 조각은 `.article` 하나다. 그 안에 `.startDate`, `.endDate`, `.periodResult`가 있다. 시작일 글자가 비어 있으면 그 항목은 건너뛴다.

## 읽는 순서

1. `.article`을 하나씩 돈다.
2. 시작일이 있을 때만 종료일을 고르고 기간을 계산한다.
3. 결과를 `.periodResult`에 쓴다.

## 구간 설명

### fillCareerPeriods

인자는 없다. 되돌리는 값도 없다. 각 `.article`에서 `.startDate` 텍스트를 앞뒤 공백 없이 읽는다. 빈 문자열이면 그 항목은 그대로 둔다.

시작일이 있으면 `.`으로 나누고, 공백을 지운 뒤 빈 조각을 버린다. 종료일 글자가 `today`이면 오늘 날짜로 바꾼다.

```javascript
if (endDate === 'today') {
    const now = new Date();
    endDateArr = [year, month, day];
    $(this).find('.endDate').text(`${year}. ${month}. ${day}.`);
}
```

`today`가 아니면 종료일 글자도 `.`으로 나누고, 월과 일을 두 자리로 맞춘 뒤 같은 형식으로 `.endDate`에 다시 쓴다. 화면의 `today` 문구는 이 시점에 구체적인 날짜로 바뀐다.

계산은 `new Date(연, 월, 일)` 두 개의 차이로 한다. 월 인자는 나눈 문자열의 두 번째 조각을 그대로 넘긴다. 자바스크립트 `Date`의 월은 0부터 세므로, 달력의 1월이 두 번째 인자 `1`로 들어가면 2월로 잡힌다. 일수는 그 밀리초 차이를 하루로 나눈 값이다.

연은 일수를 365로 나눈 몫이다. 남은 일을 30으로 나누어 반올림한 값이 개월이다. 둘 다 0이면 글자는 `-`다. 연만 0이면 `N개월`, 개월만 0이면 `N년`, 둘 다 있으면 `N년 N개월`이다. 이 글자를 괄호로 감싸 `.periodResult`에 넣는다.

시작일이 없는 항목, 또는 `.periodResult`가 없는 항목은 기간 칸이 생기지 않는다. 종료일 조각이 모자라면 `endDateArr`를 읽을 때 그 항목에서 예외가 날 수 있다. 함수는 그 예외를 잡지 않는다.

## 이 파일이 부르는 다른 파일

`cv/js/ui.js`는 jQuery의 `$`만 사용한다. `cv/resume.html`이 jQuery와 이 파일을 읽는다. 다른 페이지의 스크립트를 부르지 않는다.
