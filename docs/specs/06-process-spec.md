# 프로세스 명세

여기에는 처리 순서와 입출력만 적는다. 함수마다의 설명은 `docs/code-reference.md`를 본다.

## P1과 P2: build_output.main

- 입력: `data/`의 텍스트·워드 노트, `data/과제분류하기`의 과제 문서
- 출력: `output/study/*.md`, `output/assignment/*.md`, `output/catalog.json`, `output/index.md`, `output/_extracted/*.txt`
- 위치: `study_note_record_organization/scripts/build_output.py`

순서:

1. 학습, 과제, 추출 출력 폴더를 만든다.
2. 노트 파일 이름에서 과목명을 뽑아 그룹으로 묶는다. 그룹 수가 37이 아니면 감사 파일을 쓰고 중단한다.
3. 과제 파일 이름과 과목 키워드를 맞춰 과제 카드를 만든다. 텍스트 문서가 없는 윈도우 프로그래밍1 카드는 출처를 비워 둔다.
4. 각 카드의 원본을 읽어 본문을 채운다. 확장자에 따라 텍스트, 워드, PDF, HTML에서 뽑는다. 비밀 값을 가리고, 과제면 개인정보도 가린 뒤 추출 캐시에 저장한다.
5. 이번 카드 목록에 없는 예전 요약 마크다운은 지운다.
6. 학습 카드는 미리 둔 서술과 단계 구간으로, 과제 카드는 서론·본론·결론 또는 주제 문장으로 마크다운을 만든다.
7. `catalog.json`과 `index.md`를 쓴다.
8. `build_static_site.py`를 이어서 실행한다.

## P3: build_static_site.build_site

- 입력: `output/catalog.json`, 각 항목의 요약 마크다운, 그 안의 원본 링크가 가리키는 파일, `data/image/`
- 출력: `dashboard/js/data.js`, `dashboard/js/sources/*.json`, `dashboard/js/hero-images.js`, `dashboard/index.html`의 스크립트 쿼리
- 위치: `study_note_record_organization/scripts/build_static_site.py`
- 선행조건: `catalog.json`이 있어야 한다. 없으면 중단한다.

순서:

1. 카드에 필요한 필드만 고른다.
2. 요약 마크다운의 프론트매터를 떼고 본문을 HTML로 바꾼다. 비밀 값을 가린다.
3. HTML 안의 `/data`, `/_extracted` 링크를 원본 보기용 `data-source` 앵커로 바꾸고, 필요한 원본 키를 모은다.
4. 기존 `js/sources`를 지우고, 키마다 JSON 하나를 새로 쓴다. 본문은 다시 비밀 값과 과제 개인정보를 가린 값이다. 파일 하나가 크기 한도를 넘으면 중단한다.
5. 카드, 요약 HTML, 원본 지도, 빌드 아이디, 건수를 `window.SITE_DATA`로 `data.js`에 쓴다. 이 파일도 크기 한도를 검사한다.
6. `index.html`의 `data.js`, `app.js` 주소에 빌드 아이디 쿼리를 붙인다.
7. 이미지 폴더의 경로를 `window.HERO_IMAGES`로 쓴다.

## P4부터 P6: 브라우저

별도 서버 처리는 없다.

- P4 `init`: `SITE_DATA`가 있으면 소개와 그리드를 그린다. 없으면 빌드 안내를 보여 주고 끝난다.
- P5 `renderGrid`: 검색 문자열을 소문자로 바꿔 제목, 요약, 종류, 태그에 포함되는지 본다. 카드 클릭은 `openModal`로 이어진다.
- P6 `openSourceViewer`: 원본 키로 JSON 주소를 만들고 가져온다. HTML이면 평문으로, 과제 키이면 가린 뒤 본문에 넣는다.

`scripts/extract_sources.py`는 새 처리가 없다. `build_output.main`을 호출한다.
