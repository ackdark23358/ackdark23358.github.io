(function () {
  "use strict";

  var CARD_LABEL = { study: "STUDY NOTE", assignment: "ASSIGNMENT" };
  var catalog = [];
  var articles = {};
  var sourceMap = {};
  var sourceCache = {};
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

  function escapeHtml(s) {
    var d = document.createElement("div");
    d.textContent = s == null ? "" : String(s);
    return d.innerHTML;
  }

  function getData() {
    return window.SITE_DATA || null;
  }

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

  function isAssignmentSourceKey(key) {
    return key.indexOf("과제분류하기") !== -1 || key.indexOf("data_과제분류하기") !== -1;
  }

  function maskAssignmentPrivacy(text) {
    return text
      .replace(/(지도교수\s*[:：]\s*)\S+(?:\s*교수님)?/g, "$1OOO 교수님")
      .replace(/((?:학\s*번|수\s*강\s*번\s*호)\s*[:：]\s*)\d+/g, "$1OOOOOOOO")
      .replace(/\(\d{7,8}\s+/g, "(OOOOOOOO ")
      .replace(/\(\d{7,8}\)/g, "(OOOOOOOO)")
      .replace(/_\d{7,8}_/g, "_OOOOOOOO_");
  }

  function htmlToPlainText(html) {
    var doc = new DOMParser().parseFromString(html, "text/html");
    return (doc.body && doc.body.innerText) || html;
  }

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

  function fetchSourceText(key) {
    if (sourceCache[key]) {
      return Promise.resolve(sourceCache[key]);
    }
    var chunk = resolveSourceChunk(key);
    if (!chunk) {
      return Promise.resolve(null);
    }
    return fetch("js/sources/" + chunk)
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

  function sourceDisplayName(label, key) {
    return (
      (label || key.split("/").pop() || key).replace(/\s*\(텍스트 추출본\)\s*$/, "").trim() ||
      "원본"
    );
  }

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

  function closeSourceModal() {
    sourceOverlay.classList.add("hidden");
    sourceOverlay.setAttribute("aria-hidden", "true");
    overlay.style.pointerEvents = "";
    if (overlay.classList.contains("hidden")) {
      document.body.style.overflow = "";
    }
  }

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

  function closeModal() {
    overlay.classList.add("hidden");
    overlay.setAttribute("aria-hidden", "true");
    if (sourceOverlay.classList.contains("hidden")) {
      document.body.style.overflow = "";
    }
  }

  function init() {
    var data = getData();
    if (!data || !data.catalog) {
      grid.innerHTML = '<p class="error">data.js가 없습니다. build_static_site.py를 실행하세요.</p>';
      return;
    }

    catalog = data.catalog;
    articles = data.articles || {};
    sourceMap = data.sourceMap || {};
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
