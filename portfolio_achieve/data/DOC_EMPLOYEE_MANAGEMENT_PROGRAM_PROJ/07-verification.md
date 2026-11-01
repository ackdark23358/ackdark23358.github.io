# 실행과 확인

## 실행

Java 11 이상이 필요하다. 프로젝트 폴더에서 `run.bat`을 실행하면 소스를 UTF-8로 컴파일하고 `emp.EmpMain`을 연다. 클래스 경로는 `out`과 `lib/h2.jar`이다.

직접 실행할 때는 프로젝트 폴더가 현재 폴더여야 한다. 데이터베이스 경로가 `./data/empdb`이기 때문이다.

```bat
javac -encoding UTF-8 -cp lib\h2.jar -d out src\emp\dto\DeptDTO.java src\emp\dto\EmpDTO.java src\emp\db\DBManager.java src\emp\db\SchemaInitializer.java src\emp\dao\EmpDAO.java src\emp\ui\EmpManagementFrame.java src\emp\EmpMain.java
java -cp "out;lib\h2.jar" emp.EmpMain
```

## 처음 실행에서 볼 것

- 창 제목이 「사원관리 프로그램」이다.
- 상태 줄이 「전체 사원 14명」이다.
- 부서 콤보박스에 10 ACCOUNTING, 20 RESEARCH, 30 SALES, 40 OPERATIONS가 있다.
- 목록에 SMITH부터 MILLER까지 있고, KING의 관리자 칸은 비어 있다.
- `data` 폴더에 데이터베이스 파일이 생긴다.

## 기능 확인

| 확인 | 기대 |
| --- | --- |
| SMITH 행을 누른다 | 입력란에 7369, SMITH, CLERK, 7902, 1980-12-17, 800, 20 RESEARCH가 채워지고 수정 모드가 된다 |
| 검색어에 SALES를 넣고 검색한다 | 부서가 SALES인 사원과 직급이 SALESMAN인 사원이 나온다 |
| 검색어를 비우고 전체목록을 누른다 | 14명이 다시 나온다 |
| 초기화 후 이름만 입력하고 등록한다 | 급여가 없으면 등록되지 않는다 |
| 새 번호, 이름, 급여, 부서를 넣고 등록한다 | 목록 인원이 15명이 되고 그 사원이 선택된다 |
| 같은 사원번호로 다시 등록한다 | 이미 있는 번호라는 경고가 나온다 |
| 선택한 사원의 급여를 바꾸고 수정한다 | 목록의 급여가 바뀐다 |
| 그 사원을 삭제하고 예를 누른다 | 목록에서 빠지고 신규 등록 모드로 돌아간다 |
| 프로그램을 닫았다 연다 | 삭제와 수정이 유지된다 |

샘플로 되돌릴 때는 프로그램을 종료하고 `data` 폴더를 삭제한 뒤 다시 실행한다.

## 2026년 11월 2일 실행 기록

위 표의 조회, 등록, 수정, 삭제를 실행 화면으로 남겼다. 확인용 사원은 8001 홍길동이었고, 급여를 3200에서 4500으로 수정한 뒤 삭제했다. 확인이 끝난 목록은 샘플 14명이다. 이미지는 [화면과 흐름](05-screen-flow.md)과 `img/`에 있다.

같은 날 DAO 경로도 따로 확인했다. 샘플 14명 조회, SMITH의 관리자 이름 FORD, KING의 빈 관리자와 수당, 부서 4개, 홍길동 등록·수정·삭제 후 샘플 인원이 원래와 같은지를 보았고 통과했다.
