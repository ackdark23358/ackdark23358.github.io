# 요약 빌드

## 이 파일이 맡는 일

`study_note_record_organization/scripts/build_output.py`는 `data/`의 노트와 과제 문서를 읽어 `output/`에 요약 마크다운, `catalog.json`, `index.md`, 추출 텍스트를 쓴다. 끝난 뒤 `build_static_site.py`를 한 번 실행한다. `extract_sources.py`는 이 `main`만 부른다.

과제 프로그램의 VB 원문을 이 코드북에서 풀지는 않는다. 이 스크립트가 그 파일을 텍스트로 읽어 캐시에 넣는 경로만 적는다. 학번과 이름은 마스크 문자로만 설명한다.

`CatalogItem` 하나가 카드 하나다. `SourceRef`는 그 카드가 가리키는 원본 파일 하나다.

## 읽는 순서

1. 본문 추출과 비밀·개인정보 가리기
2. 링크 주소와 추출 캐시
3. 학습 단위 이름과 정렬
4. `SourceRef`, `CatalogItem.load_sources`
5. 학습 그룹과 학습 카탈로그
6. 과제 카탈로그와 과제 요약 문장
7. `render_markdown`, `main`

## 구간 설명

### 본문 추출

`read_text_file`은 경로의 텍스트를 읽는다. `extract_docx`, `extract_pdf`, `extract_html`은 각각 워드, PDF, HTML에서 글자만 뽑는다. HTML은 `MLStripper`가 태그를 버리고 텍스트를 모은다.

`extract_source`는 확장자를 본다. `.txt`와 `.vb`는 텍스트 파일, `.docx`, `.pdf`, `.html`, `.htm`은 위 추출기다. 다른 확장자는 빈 문자열이다. 결과는 항상 `mask_secrets`를 거친다.

`mask_secrets`는 본문이 비면 그대로 돌려준다. 아니면 고정된 키·토큰 정규식과, `api_key`처럼 이름 있는 대입의 값만 마스크로 바꾼다. 대입 패턴은 이름과 따옴표는 남기고 가운데 값만 가린다.

`is_assignment_path`는 경로에 `과제분류하기`가 있으면 참이다. `mask_assignment_privacy`는 지도교수 이름을 `OOO 교수님`으로, 학번·수강번호와 파일명 속 7~8자리 숫자를 `OOOOOOOO`로 바꾼다. 빈 문자열은 그대로다.

### 링크와 추출 캐시

`source_href`는 `data/`를 떼고 경로 조각을 URL 인코딩해 `/data/...`를 만든다. `extracted_href`는 경로에서 영숫자와 밑줄, 하이픈만 남기고 120자로 잘라 `/_extracted/이름.txt`를 만든다.

`source_link_target`은 `SourceRef`의 종류로 보이는 이름과 주소를 정한다. 경로가 폴더이고 그 안에 `Form1.vb`가 있으면 그 VB로 연결한다. 워드와 PDF는 추출본 주소와 `(텍스트 추출본)` 꼬리를 쓴다. 텍스트, HTML, VB는 원본 `/data/` 주소다. 그 외도 원본 주소다.

`cache_extract`는 같은 안전 이름으로 `output/_extracted`에 텍스트를 쓴다. 내용이 비면 `[empty]`를 쓴다. 쓰기 전에 `mask_secrets`를 한 번 더 거친다.

### 학습 단위

`parse_unit`은 파일 이름에서 `장`, `일차`, `강`, `주차`, `서론`, `프롤로그`, `부록`, `코딩면허`를 찾는다. 없으면 `전체`다.

`sort_key_unit`은 정렬 튜플을 만든다. `전체`가 먼저, 서론·프롤로그, 구간 숫자, 본문 숫자, 부록 순이다. 숫자가 없으면 99로 둔다.

### SourceRef, CatalogItem.load_sources

`SourceRef` 필드는 `path`, `unit`, `text`다. `text`는 처음엔 빈 문자열이다.

`CatalogItem` 필드는 `id`, `type`, `category`, `title`, `slug`, `summary`, `tags`, `sources`다. `load_sources`는 각 출처를 돈다. 파일이면 `extract_source`로 `text`를 채운다. 폴더면 `obj`와 `bin`을 빼고 `Form1.vb`와 `Form1.Designer.vb`만 이어 붙인다. 과제 경로면 캐시에 넣기 전에 `mask_assignment_privacy`를 적용한다. 학습 경로는 추출 본문을 그대로 캐시한다. 카드의 `text` 필드 자체는 과제라도 이 함수에서 개인정보 마스크를 다시 씌우지 않는다. 마크다운을 만들 때 경로와 링크 문구를 따로 가린다.

### 학습 카탈로그

`normalize_study_title`은 확장자와 장·일차·독서노트 꼬리, 코딩면허, 실습 필기 꼬리를 떼고 과목 이름만 남긴다.

`collect_study_groups`는 `data/` 바로 아래 파일만 본다. `.hwpx`는 건너뛰고 이름만 따로 모은다. `.txt`와 `.docx`만 과목 이름 아래로 모은다. `STUDY_MERGE_ALIASES`에 있으면 별칭을 같은 과목 키로 합친다. 각 묶음은 `sort_key_unit`으로 정렬한다. 그룹 딕셔너리와 건너뛴 hwpx 목록을 돌려준다.

`build_study_catalog`는 그룹 수가 41이 아니면 `output/study-audit.txt`에 그룹 이름과 hwpx 목록을 쓰고 `SystemExit`로 중단한다. 41이면 제목순으로 `CatalogItem`을 만든다. `STUDY_META`에 있으면 슬러그, 한 줄 요약, 태그, 분류를 그대로 쓴다. 없으면 제목으로 슬러그를 만들고 요약은 `제목 학습 노트`, 태그는 `study`, 분류는 제목에 `Do it`이 있으면 `book` 아니면 `course`다. id는 `study-슬러그`다. 출처의 `unit`은 `parse_unit`이다.

`STUDY_NARRATIVES`는 슬러그별 고정 서술이다. `build_study_narrative`는 그 문장과 원문에서 뽑은 단계 문단을 묶어 `overview`, `main`, `reflection`, `units`를 돌려준다. 원문이 짧으면 `weave_narrative`와 `soften_sentence`가 문장을 다듬고, 점이 없으면 안내 문장으로 채운다.

### 과제 카탈로그

`find_assign_file`은 아직 `used`에 없는 파일 중 제외 문자열이 없고 키워드가 들어 있는 첫 파일을 돌려준다. 키워드 순서로 찾고, 없으면 `None`이다.

`build_assignment_catalog`는 과제 폴더의 파일만 목록으로 삼는다. 안쪽 `add`는 키워드로 파일 하나를 잡아 `assignment-슬러그` 항목을 추가한다. 맞은 파일의 출처 단위는 `총괄과제`다. 맞는 파일이 없어도 항목은 만들어지고 출처만 빈다. 윈도우 프로그래밍1은 `add`를 쓰지 않고 출처를 빈 리스트로 직접 넣는다. 요약 문구는 `WinForms 실행 프로그램 제출 (텍스트 문서 없음)`이다. 나머지 과목은 과목 이름과 키워드 표로 `add`한다. 인터넷프로그래밍은 이름에 `프로그래밍2`가 들어간 파일을 제외한다.

`extract_meta_assignment`는 학번, 수강번호, 이름, 지도교수, 제출일을 딕셔너리로 뽑는다. 이 값은 요약 문장을 만들 때 표지 정보로 쓰이며, 나중에 가리기 규칙을 탄다.

과제 본문 정리는 한 묶음이다.

- `strip_assignment_cover_block`, `strip_assignment_meta_text`, `is_assignment_meta_bullet`는 표지의 학번·교수·제출일 줄을 본문 요약에서 뺀다.
- `summarize_assignment_bullets`, `extract_assignment_points`는 남은 줄에서 항목을 고른다.
- `_split_assignment_sections`, `_has_assignment_section_markers`, `_extract_assignment_topics`는 절 제목이 있으면 절별로 나눈다.
- `_sentence_from_section`, `_compose_summary_from_topics`, `_sentence_from_points`, `_assignment_summary_filler`는 그 조각으로 문장을 만든다. 쓸 문장이 없으면 과목 이름에 기대는 채움 문장을 쓴다.
- `build_assignment_content_summary`는 위 결과를 문단 리스트로 돌려준다. `render_markdown`의 과제 본문이 이 리스트를 쓴다.

### render_markdown

슬러그가 `windows-programming-1`이면 `render_windows_programming1_markdown`으로 간다. 그 함수는 원문 없이 프론트매터와 화면 설명, 캡처 경로를 적는다. 출처 목록은 비어 있다.

다른 항목은 출처 `text`를 이어 붙인다. 학습이면 `build_study_narrative`의 개요, 배운 점, 단위별 문단을 쓴다. 과제가 아닌데 학습 서술이 없으면 글머리표 요약이다. 글머리표도 없으면 원본이 짧거나 비었다는 한 줄을 넣는다. 과제면 `build_assignment_content_summary`의 문단과 `배운 점 / 적용` 고정 문장을 넣는다.

맨 아래 `원본 출처`는 `source_link_target`의 링크다. 과제면 보이는 이름과 경로에 `mask_assignment_privacy`를 적용한다. 반환 문자열 전체에 `mask_secrets`를 한 번 더 적용한다.

### main

`output/study`, `output/assignment`, `output/_extracted`를 만든다. `build_study_catalog`가 41이 아니면 여기서 중단되므로 과제 카탈로그까지 가지 않는다. 통과하면 `build_assignment_catalog`를 부르고, 모든 항목에 `load_sources`를 한다.

이번 슬러그에 없는 예전 `.md`는 두 출력 폴더에서 지운다. 각 항목의 `render_markdown` 결과를 `study` 또는 `assignment` 폴더의 `슬러그.md`로 쓴다. `catalog.json`에는 id, 종류, 분류, 제목, 슬러그, 요약, 태그, 출력 경로, 출처 경로와 단위를 넣는다. `index.md`는 학습과 과제 링크 목록이다.

그 다음 `scripts/build_static_site.py`를 현재 파이썬으로 실행한다. `check=False`라서 정적 빌드가 실패해도 이 함수는 예외를 올리지 않는다. 스크립트 파일이 없거나 실행 자체가 `OSError`면 그 예외만 삼킨다.

## 이 파일이 부르는 다른 파일

`data/`의 노트와 과제 문서, 그리고 폴더 출처 안의 `Form1.vb`와 `Form1.Designer.vb`를 읽는다. 쓰는 곳은 `output/`이다. 마지막에 `build_static_site.py`를 subprocess로 부른다.
