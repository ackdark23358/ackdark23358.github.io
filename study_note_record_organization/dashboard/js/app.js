/**
 * 학습 기록 대시보드에서 카드 목록, 검색, 요약 모달, 원본 보기를 초기화한다.
 */
(function () {
  "use strict";

  var CARD_LABEL = { study: "STUDY NOTE", assignment: "ASSIGNMENT" };
  var catalog = [];
  var articles = {};
  var sourceMap = {};
  var sourceCache = {};
  var sourceBuildId = "";
  var searchQuery = "";

  var grid = document.getElementById("grid");
  var empty = document.getElementById("empty");
  var subtitleEl = document.getElementById("subtitle");
  var noteEl = document.getElementById("note");
  var infoCompose = document.getElementById("info-compose");
  var footerCount = document.getElementById("footer-count");
  var searchInput = document.getElementById("search");
  var overlay = document.getElementById("modal-overlay");
  var modalBody = document.getElementById("modal-body");
  var modalMeta = document.getElementById("modal-meta");
  var modalClose = document.getElementById("modal-close");
  var sourceOverlay = document.getElementById("source-overlay");
  var sourceBody = document.getElementById("source-body");
  var sourceTitle = document.getElementById("source-title");
  var sourceClose = document.getElementById("source-close");

  /**
   * 사용자 문자를 HTML로 넣을 때 태그가 실행되지 않도록 이스케이프한다.
   * @param {string} s 원문
   * @returns {string}
   */
  function escapeHtml(s) {
    var d = document.createElement("div");
    d.textContent = s == null ? "" : String(s);
    return d.innerHTML;
  }

  /**
   * 빌드가 넣어 둔 window.SITE_DATA를 돌려준다. 없으면 null이다.
   * @returns {object|null}
   */
  function getData() {
    return window.SITE_DATA || null;
  }

  /**
   * 카탈로그 건수로 소개 문구, 학습·과제 수, 하단 총계를 채운다.
   */
  function renderIntro() {
    var study = 0;
    var assignment = 0;
    catalog.forEach(function (i) {
      if (i.type === "study") study++;
      else if (i.type === "assignment") assignment++;
    });
    var total = catalog.length;

    if (subtitleEl) {
      subtitleEl.textContent =
        "독서 노트·강의·과제 기록을 요약해 둔 개인 아카이브입니다. " +
        "웹·모바일·AI 학습 흐름을 한곳에서 이어 볼 수 있도록 정리했습니다.";
    }

    if (infoCompose) {
      infoCompose.innerHTML =
        "<strong>학습 " +
        study +
        "건</strong> — 독서·강의·자격·도구 노트<br>" +
        "<strong>과제 " +
        assignment +
        "건</strong> — 학점은행제 제출 했던 과제";
    }

    if (noteEl) {
      noteEl.textContent =
        "현재 총 " +
        total +
        "개 항목을 검색·열람할 수 있습니다. 요약 md는 " +
        "<code>python scripts/build_output.py</code>로, 정적 페이지 데이터는 " +
        "<code>python scripts/build_static_site.py</code>로 갱신합니다.";
    }

    if (footerCount) {
      footerCount.textContent = "총 " + total + "개 기록";
    }
  }

  /**
   * 검색어가 제목, 요약, 종류, 태그에 포함된 항목만 돌려준다. 검색어가 없으면 전체다.
   * @returns {object[]}
   */
  function filteredItems() {
    var q = searchQuery.trim().toLowerCase();
    return catalog.filter(function (item) {
      if (!q) return true;
      var hay = [item.title, item.summary, item.type]
        .concat(item.tags || [])
        .join(" ")
        .toLowerCase();
      return hay.indexOf(q) !== -1;
    });
  }

  /**
   * 검색 결과로 카드 그리드를 다시 그린다. 결과가 없으면 빈 상태 문구를 보여 준다.
   */
  function renderGrid() {
    var items = filteredItems();
    grid.innerHTML = "";

    if (items.length === 0) {
      empty.classList.remove("hidden");
      return;
    }
    empty.classList.add("hidden");

    items.forEach(function (item) {
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "card card--" + item.type;
      btn.setAttribute("aria-label", item.title + " 요약 보기");

      btn.innerHTML =
        '<p class="card-label">' +
        escapeHtml(CARD_LABEL[item.type] || "RECORD") +
        "</p>" +
        '<h3 class="card__title">' +
        escapeHtml(item.title) +
        "</h3>" +
        '<p class="card__summary">' +
        escapeHtml(item.summary || "요약 없음") +
        "</p>";

      btn.addEventListener("click", function () {
        openModal(item);
      });
      grid.appendChild(btn);
    });
  }

  /**
   * 원본 경로가 과제 폴더인지 판별한다. 과제면 열람 전에 개인정보를 가린다.
   * @param {string} key 원본 경로
   * @returns {boolean}
   */
  function isAssignmentSourceKey(key) {
    return key.indexOf("과제분류하기") !== -1 || key.indexOf("data_과제분류하기") !== -1;
  }

  /**
   * 과제 원문에서 지도교수 이름, 학번, 파일명 속 학번 숫자를 가린다.
   * @param {string} text 원문
   * @returns {string}
   */
  function maskAssignmentPrivacy(text) {
    return text
      .replace(/(지도교수\s*[:：]\s*)\S+(?:\s*교수님)?/g, "$1OOO 교수님")
      .replace(/((?:학\s*번|수\s*강\s*번\s*호)\s*[:：]\s*)\d+/g, "$1OOOOOOOO")
      .replace(/\(\d{7,8}\s+/g, "(OOOOOOOO ")
      .replace(/\(\d{7,8}\)/g, "(OOOOOOOO)")
      .replace(/_\d{7,8}_/g, "_OOOOOOOO_");
  }

  /**
   * HTML 원본을 태그가 없는 화면 텍스트로 바꾼다.
   * @param {string} html HTML 문자열
   * @returns {string}
   */
  function htmlToPlainText(html) {
    var doc = new DOMParser().parseFromString(html, "text/html");
    return (doc.body && doc.body.innerText) || html;
  }

  /**
   * 데이터베이스 총괄과제 원본에만 ER 다이어그램 이미지를 덧붙일 정보를 돌려준다.
   * @param {string} key 원본 경로
   * @returns {{src: string, alt: string, caption: string}|null}
   */
  function getSourceExtraImage(key) {
    if (!key) return null;
    var k = key;
    try {
      var decoded = decodeURIComponent(key);
      if (decoded) k = decoded;
    } catch (e) {
      /* ignore */
    }
    if (k.indexOf("데이터베이스") !== -1 && k.indexOf("총괄") !== -1) {
      return {
        src: "assets/database-er-diagram.png",
        alt: "게임개발 DB구축 ER 다이어그램",
        caption: "ER 다이어그램 (원본 PDF 도표)",
      };
    }
    return null;
  }

  /**
   * 원문 텍스트를 모달에 넣을 HTML로 만든다. 해당하면 ER 그림을 함께 넣는다.
   * @param {string} text 원문
   * @param {string} key 원본 경로
   * @returns {string}
   */
  function renderPlainSource(text, key) {
    var extra = getSourceExtraImage(key);
    var html =
      '<article class="md-content"><div class="source-plain">' +
      '<div class="source-plain__text">' +
      escapeHtml(text.replace(/\r\n/g, "\n")) +
      "</div>";
    if (extra) {
      html +=
        '<figure class="source-plain__figure">' +
        '<img src="' +
        escapeHtml(extra.src) +
        '" alt="' +
        escapeHtml(extra.alt) +
        '" loading="lazy" decoding="async" />' +
        '<figcaption>' +
        escapeHtml(extra.caption) +
        "</figcaption></figure>";
    }
    html += "</div></article>";
    return html;
  }

  /**
   * 원본 경로에 대응하는 소스 JSON 파일 이름을 찾는다. 인코딩된 경로도 풀어 본다.
   * @param {string} key 원본 경로
   * @returns {string|null}
   */
  function resolveSourceChunk(key) {
    if (sourceMap[key]) return sourceMap[key];
    try {
      var decoded = decodeURIComponent(key);
      if (decoded !== key && sourceMap[decoded]) return sourceMap[decoded];
    } catch (e) {
      /* ignore */
    }
    return null;
  }

  /**
   * 포트폴리오 가드 또는 호스트 화이트리스트를 검사하여 정당한 사이트 접근인지 판별한다.
   * @returns {boolean} 접근 허용 여부
   */
  function siteAccessAllowed() {
    var guard = window.__portfolioGuard;
    if (guard && typeof guard.allowsAccess === "function") return guard.allowsAccess();
    var protocol = window.location.protocol;
    var host = window.location.hostname;
    var known = host === "ackdark23358.github.io" || host === "localhost" || host === "127.0.0.1";
    return (protocol === "http:" || protocol === "https:") && known;
  }

  /**
   * 소스 JSON을 가져와 원문 텍스트를 돌려준다. 한 번 받은 값은 캐시에 둔다.
   * @param {string} key 원본 경로
   * @returns {Promise<string|null>}
   */
  function fetchSourceText(key) {
    if (!siteAccessAllowed()) {
      return Promise.resolve(null);
    }
    if (sourceCache[key]) {
      return Promise.resolve(sourceCache[key]);
    }
    var chunk = resolveSourceChunk(key);
    if (!chunk) {
      return Promise.resolve(null);
    }
    var url = new URL("js/sources/" + chunk, window.location.href);
    if (sourceBuildId) {
      url.searchParams.set("v", sourceBuildId);
    }
    return fetch(url.href, { cache: "no-store" })
      .then(function (res) {
        if (!res.ok) throw new Error("fetch failed");
        return res.json();
      })
      .then(function (payload) {
        var text = payload && payload.text != null ? payload.text : null;
        sourceCache[key] = text;
        if (payload && payload.key && payload.key !== key) {
          sourceCache[payload.key] = text;
        }
        return text;
      })
      .catch(function () {
        return null;
      });
  }

  /**
   * 원본 보기 제목에서 링크 문구 또는 파일 이름을 쓰고, 추출본 꼬리표를 뺀다.
   * @param {string} label 링크에 보이던 문구
   * @param {string} key 원본 경로
   * @returns {string}
   */
  function sourceDisplayName(label, key) {
    return (
      (label || key.split("/").pop() || key).replace(/\s*\(텍스트 추출본\)\s*$/, "").trim() ||
      "원본"
    );
  }

  /**
   * 원본 보기 오버레이를 열고 텍스트를 불러온다. HTML 과제는 평문으로, 과제 원문은 개인정보를 가린다.
   * @param {string} key 원본 경로
   * @param {string} label 제목에 쓸 문구
   */
  function openSourceViewer(key, label) {
    sourceOverlay.classList.remove("hidden");
    sourceOverlay.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
    if (!overlay.classList.contains("hidden")) {
      overlay.style.pointerEvents = "none";
    }

    sourceTitle.textContent = sourceDisplayName(label, key);
    sourceBody.innerHTML = '<p class="loading">원본을 불러오는 중…</p>';

    fetchSourceText(key).then(function (text) {
      if (text == null) {
        sourceBody.innerHTML =
          '<p class="error"><code>build_static_site.py</code> 실행 후 다시 시도하세요.</p>';
        return;
      }

      if (/\.html?$/i.test(key)) {
        text = htmlToPlainText(text);
      }
      if (isAssignmentSourceKey(key)) {
        text = maskAssignmentPrivacy(text);
      }
      sourceBody.innerHTML = renderPlainSource(text, key);
    });
  }

  /**
   * 원본 보기 오버레이를 닫는다. 요약 모달이 없으면 페이지 스크롤을 다시 연다.
   */
  function closeSourceModal() {
    sourceOverlay.classList.add("hidden");
    sourceOverlay.setAttribute("aria-hidden", "true");
    overlay.style.pointerEvents = "";
    if (overlay.classList.contains("hidden")) {
      document.body.style.overflow = "";
    }
  }

  /**
   * 요약 본문 안의 원본 링크 클릭을 가로채 원본 보기를 연다.
   * @param {Element} container 요약 HTML이 들어간 요소
   */
  function bindSourceLinks(container) {
    container.addEventListener("click", function (e) {
      var a = e.target.closest("a[data-source], a.source-link");
      if (!a) return;
      e.preventDefault();
      e.stopPropagation();
      var key = a.getAttribute("data-source");
      if (key) openSourceViewer(key, a.textContent.trim());
    });
  }

  /**
   * 카드에 해당하는 요약 HTML을 모달에 넣고 원본 링크를 연결한다. 요약이 없으면 오류 문구를 보여 준다.
   * @param {object} item 카탈로그 항목
   */
  function openModal(item) {
    overlay.classList.remove("hidden");
    overlay.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";

    modalMeta.innerHTML =
      '<p class="card-label">' +
      escapeHtml(CARD_LABEL[item.type] || "RECORD") +
      "</p>" +
      '<h2 id="modal-title" class="modal__title">' +
      escapeHtml(item.title) +
      "</h2>" +
      '<p class="modal__summary">' +
      escapeHtml(item.summary || "") +
      "</p>";

    var html = articles[item.slug];
    if (!html) {
      modalBody.innerHTML = '<p class="error">요약본이 없습니다.</p>';
      return;
    }

    modalBody.innerHTML = '<article class="md-content">' + html + "</article>";
    bindSourceLinks(modalBody);
  }

  /**
   * 요약 모달을 닫는다. 원본 보기가 열려 있지 않으면 페이지 스크롤을 다시 연다.
   */
  function closeModal() {
    overlay.classList.add("hidden");
    overlay.setAttribute("aria-hidden", "true");
    if (sourceOverlay.classList.contains("hidden")) {
      document.body.style.overflow = "";
    }
  }

  /**
   * SITE_DATA로 카탈로그와 원본 지도를 읽고 소개와 카드 그리드를 그린다.
   * 데이터가 없으면 빌드 스크립트를 실행하라는 안내를 보여 준다.
   */
  function init() {
    if (!siteAccessAllowed()) {
      grid.innerHTML = '<p class="error">자료에 대해서 퍼가는 것을 방지하였습니다.</p>';
      return;
    }
    var data = getData();
    if (!data || !data.catalog) {
      grid.innerHTML = '<p class="error">data.js가 없습니다. build_static_site.py를 실행하세요.</p>';
      return;
    }

    catalog = data.catalog;
    articles = data.articles || {};
    sourceMap = data.sourceMap || {};
    sourceBuildId = data.sourceBuildId || "";
    sourceCache = {};
    if (data.sources && !data.sourceMap) {
      sourceCache = data.sources;
    }
    renderIntro();
    renderGrid();
  }

  modalClose.addEventListener("click", closeModal);
  sourceClose.addEventListener("click", closeSourceModal);
  overlay.addEventListener("click", function (e) {
    if (e.target === overlay) closeModal();
  });
  sourceOverlay.addEventListener("click", function (e) {
    if (e.target === sourceOverlay) closeSourceModal();
  });

  document.addEventListener("keydown", function (e) {
    if (e.key !== "Escape") return;
    if (!sourceOverlay.classList.contains("hidden")) {
      closeSourceModal();
      return;
    }
    if (!overlay.classList.contains("hidden")) closeModal();
  });

  searchInput.addEventListener("input", function (e) {
    searchQuery = e.target.value;
    renderGrid();
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
