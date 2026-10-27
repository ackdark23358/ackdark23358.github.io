# 자료 사전 (DD)

DFD의 자료 흐름과 저장소에 실리는 자료의 이름, 의미, 구성을 적는다. 값은 예시로 학번이나 이름을 넣지 않는다.

## CatalogItem

학습 또는 과제 카드 하나다. 빌드 중의 파이썬 객체이고, 공개용 `catalog.json`과 `SITE_DATA.catalog`에는 일부만 나간다.

- id: `study-` 또는 `assignment-`로 시작하는 식별자
- type: `study` 또는 `assignment`
- category: 학습은 `book`(독서), `course`(강의), `cert`(자격), `tool`(도구). 과제는 `university`. 카드 배지는 이 네 단어만 쓴다. 과학동아는 `book`이다.
- title: 화면에 보이는 제목
- slug: 파일 이름과 요약 HTML 키
- summary: 한 줄 요약
- tags: 문자열 목록
- sources: `SourceRef` 목록. 공개 catalog에는 path와 unit만 남는다

## SourceRef

카드가 가리키는 원본 하나다.

- path: 저장소 기준 상대 경로. 예: `data/` 아래 노트
- unit: 장, 일차, 강, 주차, 서론, 부록, 코딩면허, 또는 `전체`. 과제는 `총괄과제`
- text: 추출한 본문. 빌드 메모리와 추출 캐시에만 있고 `data.js` 카드에는 넣지 않는다

## D1 학습 원본

`study_note_record_organization/data/`의 노트와 과제 문서, `data/image/`의 히어로 이미지다. 과제 프로그램 소스 코드는 화면 명세의 입력으로 다루지 않는다.

## D2 output

- `output/study/*.md`: 학습 요약. 앞에 YAML 프론트매터가 있다
- `output/assignment/*.md`: 과제 요약
- `output/catalog.json`: `items` 배열과 `counts.study`, `counts.assignment`, `counts.total`
- `output/_extracted/*.txt`: 가린 추출 본문
- `output/index.md`: 사람이 보는 요약 목록
- `output/study-audit.txt`: 학습 그룹 수가 어긋났을 때만 생기는 감사 기록

## D3 정적 데이터

`window.SITE_DATA`로 `dashboard/js/data.js`에 들어간다.

- catalog: 카드 배열. 각 항목은 id, type, title, slug, summary, tags
- articles: slug를 키로 하는 요약 HTML 문자열
- sourceMap: 원본 경로 키에서 `js/sources/` JSON 파일 이름으로의 대응
- sourceBuildId: 원본 지도 해시 12자. 스크립트 주소의 `v` 쿼리와 원본 요청 캐시 무효화에 쓴다
- counts: 학습, 과제, 전체 건수

원본 JSON 한 개의 구성은 다음이다.

- key: 원본 경로
- text: 가린 본문 전체

`window.HERO_IMAGES`는 이미지 상대 경로 문자열의 배열이다. `SITE_DATA`와 별도 파일이다.

## 테마 저장값

- 키: `portfolio-theme-v2`
- 값: `light` 또는 `dark`
- 위치: 브라우저 localStorage
- 없는 값이나 저장 실패: 페이지의 `data-default-theme`를 쓰고, 그것도 없으면 다크를 기본으로 하는 스크립트가 있다. 메인 문서의 기본 표시는 라이트다

## 가림 값

- 비밀 값 마스크: 고정 문자열. API 키와 토큰 패턴을 대체한다
- 학번 마스크: 8자리 영문 O
- 지도교수 마스크: 이름 대신 쓰는 고정 호칭 문자열

이 마스크 결과는 추출 본문, 요약에 실린 과제 경로, 원본 보기 화면에 적용된다.

## D4 리소스 보안 가드 및 수집 정책

- `window.__portfolioGuard`: `allowsAccess()` 메서드를 가진 전역 객체. `!isEmbedded() && allowedHost()` 결과를 반환한다.
- `ALLOWED_HOSTS`: 허용 호스트 매핑 객체 (`ackdark23358.github.io`, `localhost`, `127.0.0.1`).
- `tdmrep.json`: TDM 권리 유보 선언 JSON (`[{"location": "/", "tdm-reservation": 1}]`).
- 하단 고정 표기값:
  - 저작권: `© 2026 김신욱(깃허브 ackdark23358). All rights reserved.`
  - AI 생성 선언문: `자료를 제외한 문장이나 문구는 나의 생각을 프롬프트에 요청하여 생성한 문장이나 문구입니다.`

