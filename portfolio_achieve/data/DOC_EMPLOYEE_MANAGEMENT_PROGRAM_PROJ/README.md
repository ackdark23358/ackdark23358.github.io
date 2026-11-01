# 사원관리 프로그램 문서

[프로젝트 아카이브](https://ackdark23358.github.io/portfolio_achieve/index.html)에 넣기 위한 기록이다. 아카이브의 PROJ_15는 2017–2019 에듀펜 자바·모바일 과정인데, 2026년 10월 18일에 폴더를 열었을 때 소스와 캡처가 없었다. 이 문서는 그때 다루던 사원 CRUD를 Java Swing, DTO, DAO로 다시 구현한 결과를 정리한 것이다. 아카이브 카드는 **PROJ_18 사원관리 프로그램**으로 반영했다.

카드에 바로 옮길 문안은 [아카이브 카드 문안](01-archive-card.md)에 둔다. 나머지는 아래 순서로 읽는다.

1. [프로젝트 소개](02-introduction.md)
2. [구조](03-architecture.md)
3. [자료 사전](04-data-dictionary.md)
4. [화면과 흐름](05-screen-flow.md)
5. [처리 명세](06-process.md)
6. [실행과 확인](07-verification.md)

프로그램 소스와 실행 방법은 저장소 루트의 `README.md`, `run.bat`에 있다. 화면 캡처는 이 폴더의 `img/`와 루트의 `screenshots/`에 같은 파일로 있다. 캡처 일시는 2026년 11월 2일이다.

## 한 줄 요약

| 항목 | 내용 |
| --- | --- |
| 이름 | 사원관리 프로그램 |
| 기간 | 2026년 11월 2일 재구현 |
| 바탕 | 에듀펜 자바 과정(PROJ_15)의 사원 CRUD |
| 화면 | Java Swing |
| 데이터 | DTO, DAO, JDBC, H2 파일 데이터베이스 |
| 기능 | 사원 등록, 조회, 검색, 수정, 삭제 |
