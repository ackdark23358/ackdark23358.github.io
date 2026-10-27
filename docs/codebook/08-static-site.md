# 정적 사이트 데이터

## 이 파일이 맡는 일

`study_note_record_organization/scripts/build_static_site.py`는 `output/catalog.json`과 요약 마크다운을 읽어 대시보드가 바로 여는 파일을 만든다.

- `dashboard/js/data.js`의 `window.SITE_DATA`
- `dashboard/js/sources/` 아래 원본 JSON
- `dashboard/js/hero-images.js`의 `window.HERO_IMAGES`
- `dashboard/index.html`의 `data.js`, `app.js` 쿼리

`main`은 `build_site`를 부르고, 브라우저로 `dashboard/index.html`을 열 수 있다고 안내한다.

## 읽는 순서

1. 가리기, 마크다운을 HTML로 바꾸기, 원본 링크 다시 쓰기
2. 원본 파일 읽기
3. 히어로 목록, 청크 이름, 빌드 아이디, 크기 한도
4. `collect_catalog`, `build_site`, `main`

## 구간 설명

### 가리기

`mask_secrets`와 `mask_assignment_privacy`, `is_assignment_path`는 `build_output.py`와 같은 역할이다. 이 파일에 따로 있다. 요약 HTML을 만들기 전과, 원본 JSON에 넣기 전에 한 번씩 탄다.

### 마크다운을 HTML로

`parse_frontmatter`는 앞의 `---` 블록과 본문을 나눈다. 프론트매터는 카드에 다시 쓰지 않고 본문만 HTML로 간다. 카드 필드는 `catalog.json`에서 `collect_catalog`가 고른다.

`md_to_html`은 제목, 목록, 문단, 이미지를 HTML로 바꾼다. `_esc`는 글자를 이스케이프하고, `_inline_md`는 `**굵게**`, `` `코드` ``, 슬래시로 시작하는 마크다운 링크를 인라인 HTML로 바꾼다. 상대 경로 이미지는 그대로 둔다.

`normalize_source_key`는 역슬래시를 슬래시로 바꾸고 앞의 슬래시를 뗀 뒤, 퍼센트 인코딩이 더 풀리지 않을 때까지 `unquote`한다.

`rewrite_source_links`는 HTML 안의 `/data`와 `/_extracted` 링크를 찾는다. 주소에서 원본 키를 꺼내 `pending` 집합에 넣고, `href="#"`와 `data-source="키"`, `source-link` 클래스를 붙인다. 이미 `class`가 있으면 그 값 뒤에 `source-link`를 더한다. 대시보드의 `bindSourceLinks`가 이 앵커를 누를 때 원본 보기를 연다.

### 원본 읽기

`resolve_source_path`는 `_extracted/`로 시작하면 `output/` 아래로, `data/`로 시작하면 저장소 루트 아래로 경로를 만든다. 둘 다 아니면 `None`이다.

`read_text_file`은 `utf-8`, `utf-8-sig`, `cp949` 순으로 읽는다. 모두 실패하면 깨진 글자를 대체해 utf-8로 읽는다.

`read_source_text`는 경로가 파일이 아니거나 읽기 `OSError`면 `None`이다. 읽은 뒤에는 `mask_secrets`를 적용하고, 과제 경로면 `mask_assignment_privacy`도 적용한다.

### 히어로, 청크, 한도

`collect_hero_images`는 `data/image`의 파일을 이름순으로 보고, 이미지 확장자만 `../data/image/파일이름`으로 모은다. 폴더가 없으면 빈 리스트다.

`write_hero_images_js`는 그 목록을 `window.HERO_IMAGES = ...;`로 `hero-images.js`에 쓰고 개수를 돌려준다.

`source_chunk_filename`은 원본 키 해시 8자와 본문 해시 8자를 이어 `키-본문.json` 이름을 만든다. 본문이 바뀌면 파일 이름이 바뀐다.

`source_build_id`는 정렬한 `키:파일이름` 전체를 해시해 12자를 돌려준다. `stamp_index_scripts`는 그 값에 `app.js`와 `styles.css` 해시를 더해 12자 토큰을 만든다. `dashboard/index.html`에서 `js/data.js`, `js/app.js`, `css/styles.css`의 기존 쿼리를 지우고 `?v=토큰`을 붙인다. `hero.js` 주소는 바꾸지 않는다.

`assert_under_github_limit`은 파일 크기가 100MB를 넘으면 `SystemExit`로 빌드를 멈춘다. 청크마다, 그리고 `data.js`를 쓴 뒤에 호출한다.

### collect_catalog, build_site

`collect_catalog`는 `catalog.json`의 `items`에서 `id`, `type`, `category`, `title`, `slug`, `summary`, `tags`를 남긴다. 요약이 없으면 빈 문자열, 태그가 없으면 빈 배열이다. `category`는 카드 배지에 쓴다. 출처 목록은 카드 데이터에 넣지 않는다.

`build_site`는 `catalog.json`이 없으면 `python scripts/build_output.py`를 먼저 실행하라는 메시지로 중단한다.

항목마다 `output` 경로의 마크다운을 연다. 파일이 없으면 그 항목의 요약 HTML은 만들지 않는다. 있으면 본문만 `mask_secrets`한 뒤 `md_to_html`과 `rewrite_source_links`를 거쳐 `articles[slug]`에 넣는다. 링크가 모은 원본 키는 `pending_sources`에 쌓인다.

`dashboard/js/sources`가 있으면 폴더를 지우고 다시 만든다. 키를 정렬해 `read_source_text`가 `None`이 아닌 것만 JSON으로 쓴다. 객체는 `key`와 `text`다. 청크가 한도를 넘으면 그 시점에 중단한다. `sourceMap`은 원본 키에서 청크 파일 이름으로 간다.

`SITE_DATA`에는 `catalog`, `articles`, `sourceMap`, `sourceBuildId`, `counts`가 들어간다. `counts`는 `catalog.json`의 값을 그대로 둔다. `data.js`는 `window.SITE_DATA =` 뒤에 그 JSON을 붙인 한 파일이다. 한도를 확인한 뒤 `stamp_index_scripts`와 `write_hero_images_js`를 부른다.

`main`은 `build_site`가 예외 없이 끝나면 완료 문장을 출력한다. 한도 초과나 `catalog.json` 없음은 `SystemExit`로 올라간다.

## 이 파일이 부르는 다른 파일

`output/catalog.json`, `output/study`와 `output/assignment`의 마크다운, `output/_extracted` 또는 `data/`의 원본, `data/image`를 읽는다. `dashboard/js/data.js`, `dashboard/js/sources/*.json`, `dashboard/js/hero-images.js`, `dashboard/index.html`을 쓴다. `app.js`와 `hero.js`의 내용은 바꾸지 않는다.
