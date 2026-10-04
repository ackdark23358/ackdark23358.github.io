# 문서 생성 스크립트

## 이 파일이 맡는 일

`docs/`의 파이썬 스크립트는 사이트를 그리지 않는다. 이미 있는 마크다운이나 소스 주석을 한 권의 HTML로 합친 뒤 Edge 또는 Chrome으로 PDF를 인쇄한다. 글꼴은 맑은 고딕이다.

세 갈래다.

- `build_code_reference.py`는 함수·클래스 주석과 유사코드를 `code-reference.md`, HTML, PDF로 만든다.
- `build_specs.py`는 `docs/specs/*.md`를 `technical-specs.md`, HTML, PDF로 만든다. Mermaid 차트는 그림으로 바꾼다.
- `build_codebook.py`는 `docs/codebook/*.md`를 `codebook.md`, HTML, PDF로 만든다.

`data/` 과제 프로그램 소스는 코드 설명 수집 대상이 아니다. 파일 목록에 학번이나 이름이 섞이면 마스크로 바꾼다.

## 읽는 순서

각 스크립트는 글을 모으고, 마크다운의 일부만 HTML로 바꾼 다음, 브라우저의 `print-to-pdf`를 호출하는 순서다.

## 구간 설명

### build_code_reference.py

소스 트리를 돌며 자바스크립트 JSDoc, 파이썬 docstring, HTML·CSS 파일 머리 주석을 모은다. 생성물인 `data.js`, `hero-images.js`, `sources` JSON과 `data/` 아래 코드 확장자는 본문으로 풀지 않는다. 심볼마다 설명, 인자, 반환을 적고, 함수 본문에서 만든 유사코드를 붙인다. 클래스면 필드와 메서드를 적는다. 학번 숫자와 이름을 마스크한 뒤 마크다운으로 쓰고, 같은 HTML 변환으로 PDF를 만든다.

### build_specs.py

`docs/specs`의 마크다운을 파일 이름순으로 잇는다. 제목, 목록, 코드 울타리, 문단, 굵게, 인라인 코드를 HTML로 바꾼다. 울타리 언어가 `mermaid`이면 차트 소스를 브라우저로 그려 PNG로 저장하고 `img`로 넣는다. 유스케이스 소스에 `actor-style: person`이 있으면 Mermaid 대신 사람 그림이 있는 SVG를 그린다. 나머지 차트는 Mermaid다. 그림 파일 이름은 소스 해시다. 이번 빌드에 쓰이지 않은 그림은 지운다. PDF 인쇄는 머리글과 바닥글 없이 한다.

### build_codebook.py

`docs/codebook`의 마크다운을 파일 이름순으로 잇는다. HTML로 바꾸는 규칙은 명세와 같고, 차트 분기는 없다. 코드 울타리는 회색 `pre`로만 둔다. 브라우저를 찾지 못하거나 PDF가 너무 작으면 중단한다.

## 이 파일이 부르는 다른 파일

코드 설명 스크립트는 저장소의 화면 스크립트, 스타일, 빌드 스크립트를 읽는다. 명세와 코드북 스크립트는 `docs/specs`와 `docs/codebook`의 마크다운만 읽는다. 셋 다 Edge 또는 Chrome 실행 파일을 찾아 PDF를 쓴다.
