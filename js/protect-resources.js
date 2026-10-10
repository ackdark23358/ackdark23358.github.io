/**
 * 자료 복사와 다른 사이트의 끼워 넣기를 막고 안내를 보여 준다.
 * 허용된 호스트(GitHub Pages, localhost)에서만 정상 동작하며 불법 스크랩 및 임베딩을 방지한다.
 */
(function () {
  var MESSAGE = "자료에 대해서 퍼가는 것을 방지하였습니다.";
  var HIDE_MS = 2600;
  var hideTimer = 0;
  var ALLOWED_HOSTS = {
    "ackdark23358.github.io": true,
    localhost: true,
    "127.0.0.1": true
  };

  /**
   * 창이 다른 사이트의 iframe 안에 끼워져 있는지 확인한다.
   * @returns {boolean} iframe 임베딩 여부
   */
  function isEmbedded() {
    try {
      return window.top !== window.self;
    } catch (e) {
      return true;
    }
  }

  /**
   * 현재 주소의 프로토콜과 호스트가 허용 목록에 있는지 검사한다.
   * @returns {boolean} 허용 호스트 여부
   */
  function allowedHost() {
    var protocol = window.location.protocol;
    if (protocol !== "http:" && protocol !== "https:") return false;
    return !!ALLOWED_HOSTS[window.location.hostname];
  }

  window.__portfolioGuard = {
    allowsAccess: function () {
      return !isEmbedded() && allowedHost();
    }
  };

  /**
   * 비인가 호스트나 iframe일 때 전체 화면을 검은 배경으로 바꾸고 차단 안내를 표시한다.
   */
  function paintBlockedPage() {
    if (!document.body) return;
    document.body.innerHTML = "";
    document.body.style.margin = "0";
    document.body.style.background = "#111111";
    document.body.style.color = "#ffffff";
    var notice = document.createElement("p");
    notice.textContent = MESSAGE;
    notice.style.cssText = "margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:1.5rem;text-align:center;font:600 1rem/1.5 sans-serif;";
    document.body.appendChild(notice);
  }

  if (isEmbedded() || !allowedHost()) {
    if (document.body) paintBlockedPage();
    else document.addEventListener("DOMContentLoaded", paintBlockedPage);
    return;
  }
  var style = document.createElement("style");

  style.textContent = [
    "body {",
    "  -webkit-user-select: none;",
    "  user-select: none;",
    "}",
    "input, textarea, select, [contenteditable='true'] {",
    "  -webkit-user-select: text;",
    "  user-select: text;",
    "}",
    "#resource-protect-notice {",
    "  position: fixed;",
    "  left: 50%;",
    "  bottom: 1.75rem;",
    "  z-index: 5000;",
    "  max-width: min(32rem, calc(100vw - 2rem));",
    "  margin: 0;",
    "  padding: 0.95rem 1.25rem;",
    "  border-radius: 999px;",
    "  background: #111111;",
    "  color: #ffffff;",
    "  font: 600 0.95rem/1.45 sans-serif;",
    "  text-align: center;",
    "  pointer-events: none;",
    "  opacity: 0;",
    "  transform: translate(-50%, 18px) scale(0.92);",
    "}",
    "#resource-protect-notice.is-visible {",
    "  animation: resource-protect-pop 2.6s cubic-bezier(0.22, 1, 0.36, 1) forwards;",
    "}",
    "@keyframes resource-protect-pop {",
    "  0% { opacity: 0; transform: translate(-50%, 18px) scale(0.92); }",
    "  14% { opacity: 1; transform: translate(-50%, 0) scale(1); }",
    "  78% { opacity: 1; transform: translate(-50%, 0) scale(1); }",
    "  100% { opacity: 0; transform: translate(-50%, -10px) scale(0.98); }",
    "}"
  ].join("");
  document.head.appendChild(style);

  /**
   * 이벤트 대상이 입력 요소(검색창, 텍스트에어리어 등)인지 판별한다.
   * @param {EventTarget} target 판별할 대상 요소
   * @returns {boolean} 편집 가능 요소 여부
   */
  function isEditable(target) {
    if (!target || !target.closest) return false;
    return !!target.closest("input, textarea, select, [contenteditable='true']");
  }

  /**
   * 화면 하단에 자료 퍼가기 방지 안내 토스트 팝업을 띄운다.
   */
  function showNotice() {
    var notice = document.getElementById("resource-protect-notice");
    if (!notice) {
      notice = document.createElement("p");
      notice.id = "resource-protect-notice";
      notice.setAttribute("role", "status");
      notice.setAttribute("aria-live", "polite");
      notice.textContent = MESSAGE;
      document.body.appendChild(notice);
    }
    notice.classList.remove("is-visible");
    void notice.offsetWidth;
    notice.classList.add("is-visible");
    window.clearTimeout(hideTimer);
    hideTimer = window.setTimeout(function () {
      notice.classList.remove("is-visible");
    }, HIDE_MS);
  }

  /**
   * 복사, 잘라내기, 우클릭 등 금지된 이벤트의 기본 동작을 막고 안내를 띄운다.
   * @param {Event} event 가로챌 브라우저 이벤트
   */
  function block(event) {
    if (isEditable(event.target)) return;
    event.preventDefault();
    showNotice();
  }

  ["copy", "cut", "contextmenu", "dragstart", "selectstart"].forEach(function (type) {
    document.addEventListener(type, block);
  });

  document.addEventListener("keydown", function (event) {
    if (isEditable(event.target)) return;
    if (!(event.ctrlKey || event.metaKey)) return;
    var key = String(event.key || "").toLowerCase();
    if (key === "c" || key === "x" || key === "a" || key === "s" || key === "u") {
      event.preventDefault();
      showNotice();
    }
  });
})();
