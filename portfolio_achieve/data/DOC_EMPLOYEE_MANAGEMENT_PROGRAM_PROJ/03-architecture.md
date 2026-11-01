# 구조

화면은 데이터베이스 문장을 만들지 않는다. 입력값은 `EmpDTO`에 담고, `EmpDAO`가 JDBC로 저장하고 조회한다.

```text
EmpMain
  ├─ SchemaInitializer   처음 실행 시 dept, emp 테이블과 샘플 데이터
  └─ EmpManagementFrame  Swing 화면
        ├─ EmpDTO, DeptDTO
        └─ EmpDAO
              └─ DBManager  →  data/empdb (H2)
```

## 클래스

| 클래스 | 패키지 | 역할 |
| --- | --- | --- |
| `EmpMain` | `emp` | 로케일과 화면 글꼴을 맞춘 뒤 데이터베이스를 준비하고 창을 연다. |
| `EmpManagementFrame` | `emp.ui` | 입력란, 목록, 검색, 등록·수정·삭제 버튼. |
| `EmpDTO` | `emp.dto` | 사원 한 명. 화면 표시용 부서명과 관리자 이름을 포함한다. |
| `DeptDTO` | `emp.dto` | 부서 한 건. 콤보박스에 `부서번호 부서명`으로 보인다. |
| `EmpDAO` | `emp.dao` | 전체 조회, 검색, 부서 조회, 다음 사원번호, 등록, 수정, 삭제. |
| `DBManager` | `emp.db` | `jdbc:h2:./data/empdb` 연결을 만든다. 계정은 `sa`, 비밀번호는 없다. |
| `SchemaInitializer` | `emp.db` | `emp` 테이블이 없을 때만 테이블과 샘플 데이터를 만든다. |

## 호출 방향

1. `EmpMain`이 `SchemaInitializer.init()`을 호출한다.
2. `EmpManagementFrame`이 부서 콤보박스와 사원 목록을 `EmpDAO`에 요청한다.
3. 등록, 수정, 삭제는 화면이 `EmpDTO` 또는 사원번호를 만들어 DAO 메서드를 호출한다.
4. DAO는 `PreparedStatement`로 쿼리를 실행하고, 조회 결과는 `EmpDTO` 목록으로 돌려준다.

DAO가 목록을 만들 때는 `emp`를 기준으로 `dept`와 관리자 사원(`emp` 자기 조인)을 왼쪽 조인한다. 그래서 목록의 관리자 칸에는 번호와 이름이 함께 나오고, 부서 칸에는 번호와 부서명이 함께 나온다.

## 저장 위치

데이터베이스 URL은 실행 폴더 기준 `./data/empdb`이다. `run.bat`은 자신이 있는 폴더로 이동한 뒤 실행하므로, 데이터 파일은 프로젝트의 `data` 폴더에 생긴다. 테이블이 이미 있으면 샘플 데이터를 다시 넣지 않는다. 따라서 이후의 등록과 수정은 프로그램을 껐다 켜도 남는다.
