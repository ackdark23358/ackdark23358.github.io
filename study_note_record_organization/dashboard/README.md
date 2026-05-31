# 학습·과제 기록 대시보드 (정적 사이트)

HTML5, CSS, JavaScript만으로 동작합니다. Node.js·Vite·npm은 사용하지 않습니다.

## 빌드 (Python)

```powershell
cd c:\study_note_record_organization
python scripts/build_output.py
python scripts/build_static_site.py
```

- `dashboard/js/data.js` — 카탈로그·요약 HTML·원본 텍스트
- `dashboard/js/hero-images.js` — `data/image` 사진 목록

## 히어로 이미지 추가·반영

상단 히어로 갤러리는 **`data/image/`** 폴더의 사진을 사용합니다. 파일을 넣거나 바꾼 뒤에는 목록 파일을 다시 만들어야 브라우저에 반영됩니다.

### 1. 이미지 넣기

1. `c:\study_note_record_organization\data\image\`에 사진을 복사합니다.
2. 지원 확장자: `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`, `.bmp`
3. 파일명에 한글·공백이 있어도 됩니다.

삭제·이름 변경도 같은 폴더에서 하면 됩니다. 반영은 아래 2단계가 필요합니다.

### 2. 목록 갱신 (`hero-images.js`)

**이미지만 바꾼 경우** (가볍게, 권장):

```powershell
cd c:\study_note_record_organization
python -c "from pathlib import Path; import importlib.util; spec=importlib.util.spec_from_file_location('b','scripts/build_static_site.py'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); n=m.write_hero_images_js(Path('dashboard/js')); print('hero images:', n)"
```

끝에 `hero images: 30`처럼 등록된 개수가 출력되면 성공입니다.

**전체 사이트 데이터까지 같이 갱신할 때**:

```powershell
python scripts/build_static_site.py
```

(`build_output.py`까지 돌리면 `data.js`도 함께 다시 만들어집니다.)

### 3. 브라우저에서 확인

1. [보기](#보기-로컬-서버-권장)처럼 **프로젝트 루트**에서 `python -m http.server` 실행
2. http://localhost:8080/dashboard/ 접속
3. **강력 새로고침**(Ctrl+F5) — 캐시 때문에 이전 사진이 보일 수 있음
4. 히어로를 **클릭**하면 다른 사진으로 바뀌는지 확인

> `dashboard` 폴더만 서버 루트로 쓰면 `data/image` 경로가 깨져 히어로 사진이 안 보일 수 있습니다.

## 보기 (로컬 서버 권장)

히어로 사진은 `../data/image`를 쓰므로 **프로젝트 루트**에서 서버를 띄웁니다.

```powershell
cd c:\study_note_record_organization
python -m http.server 8080
```

브라우저: http://localhost:8080/dashboard/

## 구조

```
dashboard/
  index.html
  css/styles.css
  js/app.js, hero.js, data.js, hero-images.js
  assets/          # 과제 도표 등 정적 첨부
```

## 기능

- 히어로 갤러리 (`data/image`, 페이드·클릭 랜덤)
- 기록 카드 그리드·검색
- 카드 클릭 → 요약 모달
- 원본 출처 → 텍스트·첨부 이미지 모달 (과제 교수·학번 마스킹)
