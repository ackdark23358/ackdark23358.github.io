# 소스 설명

패키지 루트는 `src`입니다. 이클립스 출력 폴더와 배치 파일의 컴파일 결과는 `bin`입니다.

```text
src/chat/Protocol.java
src/chat/server/ChatServer.java
src/chat/server/ClientHandler.java
src/chat/client/ChatClient.java
```

## Protocol

`chat.Protocol`은 서버와 클라이언트가 공유하는 한 줄 형식입니다. 명령 상수, 줄에서 명령과 내용을 나누는 메서드, `JOIN`·`CHAT`·퇴장·입장 결과·안내·목록 문장을 만드는 메서드, 대화명 검사가 있습니다.

대화명 검사는 앞뒤 내용이 비었는지, 12자를 넘는지, 공백이나 제어 문자가 있는지를 봅니다. 문제가 있으면 화면에 보여줄 문장을 돌려주고, 없으면 `null`입니다.

## ChatServer

`chat.server.ChatServer`는 서버 창이자 접속자 명단의 주인입니다. `main`에서 창을 띄웁니다. 인자가 있으면 그 값을 포트에 넣고 바로 엽니다.

여는 순서는 다음과 같습니다.

1. 포트 번호가 1부터 65535 안인지 확인합니다.
2. `ServerSocket`을 만들고 재사용을 허용한 뒤 그 포트에 묶습니다.
3. 로그에 시작, `127.0.0.1`, 이 컴퓨터의 IPv4, 방화벽 안내를 남깁니다.
4. 수락 스레드가 `accept`로 소켓을 받을 때마다 `ClientHandler`를 시작합니다.

접속자 목록은 서버만 수정합니다. 입장과 퇴장은 그 목록에서 넣고 뺀 뒤에 화면과 다른 클라이언트에 알립니다. 같은 대화명은 목록에 두 번 들어가지 않습니다.

## ClientHandler

`chat.server.ClientHandler`는 접속자 한 명의 스레드입니다. 생성자에서 소켓 스트림을 이렇게 연결합니다.

```text
InputStream  → InputStreamReader(UTF-8)  → BufferedReader
OutputStream → OutputStreamWriter(UTF-8) → BufferedWriter
```

`run`은 `readLine`으로 한 줄씩 읽습니다. `JOIN`이면 이름을 검사하고 서버 목록에 넣은 뒤 성공 또는 실패를 보냅니다. `CHAT`이면 앞뒤 공백을 정리하고 500자에서 자른 다음, 서버가 이 소켓의 대화명을 붙여 모두에게 보냅니다. `QUIT`이거나 읽기가 끝나면 소켓을 닫고 서버에 퇴장을 알립니다.

보낼 때는 버퍼에 한 줄을 쓰고 `newLine` 다음 `flush`합니다. 버퍼를 비우지 않으면 상대는 그 줄을 즉시 받지 못합니다.

## ChatClient

`chat.client.ChatClient`는 클라이언트 창입니다. 접속 버튼은 별도 스레드에서 소켓을 연결하고, 위와 같은 버퍼 스트림을 만든 뒤 `JOIN`을 보냅니다. 연결 제한 시간은 5초입니다.

수신은 창 안의 `ReceiveThread`가 맡습니다. 서버 줄을 읽으면 이벤트 스레드에서 채팅방이나 대화상대를 고칩니다. 전송 버튼과 Enter는 `CHAT` 한 줄을 출력 스트림에 씁니다. 나가기와 창 닫기는 `QUIT`을 보낸 뒤 소켓을 닫습니다.

`main` 인자는 순서대로 IP, 포트, 대화명입니다. 세 개가 있으면 창을 띄운 다음 바로 접속합니다.

## 실행 진입점

| 실행 | 클래스 |
| --- | --- |
| 서버 | `chat.server.ChatServer` |
| 클라이언트 | `chat.client.ChatClient` |

이클립스 실행 구성은 프로젝트 루트의 `ChatServer.launch`, `ChatClient.launch`입니다. 배치 파일 `run-server.bat`, `run-client.bat`은 UTF-8로 컴파일한 뒤 같은 클래스를 실행합니다.
