/**
 * 포트폴리오 메인 페이지의 내비게이션, 자료 드롭다운, 테마 전환을 초기화한다.
 * DOM이 준비되면 부드러운 앵커 이동, 모바일 메뉴, 섹션 포커스를 연결한다.
 */
(function () {
  "use strict";

  var mqReduceMotion =
    typeof window.matchMedia === "function" ? window.matchMedia("(prefers-reduced-motion: reduce)") : null;
  var THEME_KEY = "portfolio-theme-v2";

  /**
   * 사용자가 동작 줄이기를 켰는지 확인한다.
   * 켜져 있으면 스크롤을 즉시 이동하고, 아니면 부드럽게 이동한다.
   * @returns {boolean}
   */
  function prefersReducedMotion() {
    return mqReduceMotion ? mqReduceMotion.matches : false;
  }

  /**
   * 문서 전체에서 선택자와 맞는 요소를 배열로 돌려준다.
   * @param {string} selector CSS 선택자
   * @returns {Element[]}
   */
  function queryAll(selector) {
    return Array.prototype.slice.call(document.querySelectorAll(selector));
  }

  /**
   * 지정한 요소 안에서만 선택자와 맞는 요소를 배열로 돌려준다.
   * @param {Element} root 검색을 시작할 요소
   * @param {string} selector CSS 선택자
   * @returns {Element[]}
   */
  function queryAllIn(root, selector) {
    return Array.prototype.slice.call(root.querySelectorAll(selector));
  }

  /**
   * 상단 메뉴의 페이지 안 링크를 부드러운 스크롤로 연결한다.
   * 햄버거 버튼으로 모바일 메뉴를 열고, Escape와 넓은 화면에서는 메뉴를 닫는다.
   */
  function initSmoothNav() {
    var nav = document.getElementById("site-nav");
    var toggle = document.querySelector(".nav-toggle");

    queryAll(".site-nav__link").forEach(function (link) {
      var href = link.getAttribute("href") || "";
      if (!href.startsWith("#") || href.length < 2) return;

      link.addEventListener("click", function (e) {
        var target = document.getElementById(href.slice(1));
        if (!target) return;
        e.preventDefault();
        target.scrollIntoView({ behavior: prefersReducedMotion() ? "auto" : "smooth", block: "start" });
        closeMobileNav(nav, toggle);
        target.focus({ preventScroll: true });
      });
    });

    if (toggle && nav) {
      toggle.addEventListener("click", function () {
        var open = !nav.classList.contains("is-open");
        setMobileNav(nav, toggle, open);
      });
    }

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && nav && nav.classList.contains("is-open")) {
        closeMobileNav(nav, toggle);
        if (toggle) toggle.focus();
      }
    });

    window.addEventListener(
      "resize",
      debounce(function () {
        if (window.innerWidth > 768 && nav && toggle) {
          closeMobileNav(nav, toggle);
        }
      }, 150),
    );
  }

  /**
   * 자료 메뉴 드롭다운의 열기, 항목 이동, 바깥 클릭·Escape 닫기를 연결한다.
   * 항목이 페이지 안 링크이면 해당 구역으로 스크롤한 뒤 메뉴를 닫는다.
   */
  function initResourceDropdown() {
    var nav = document.getElementById("site-nav");
    var navToggle = document.querySelector(".nav-toggle");

    queryAll(".site-nav__dropdown").forEach(function (dropdown) {
      var dropdownToggle = dropdown.querySelector(".site-nav__dropdown-toggle");

      if (!dropdownToggle) return;

      dropdownToggle.addEventListener("click", function (e) {
        e.preventDefault();
        var open = dropdownToggle.getAttribute("aria-expanded") !== "true";
        closeResourceDropdowns(dropdown);
        setResourceDropdown(dropdown, open);
      });

      queryAllIn(dropdown, ".site-nav__dropdown-link").forEach(function (link) {
        link.addEventListener("click", function (e) {
          var href = link.getAttribute("href") || "";

          if (href.startsWith("#") && href.length > 1) {
            var target = document.getElementById(href.slice(1));
            if (target) {
              e.preventDefault();
              target.scrollIntoView({ behavior: prefersReducedMotion() ? "auto" : "smooth", block: "start" });
              target.focus({ preventScroll: true });
            }
          }

          closeResourceDropdowns();
          closeMobileNav(nav, navToggle);
        });
      });
    });

    document.addEventListener("click", function (e) {
      var target = e.target;
      if (target instanceof Element && target.closest(".site-nav__dropdown")) return;
      closeResourceDropdowns();
    });

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") {
        closeResourceDropdowns();
      }
    });
  }

  /**
   * 저장된 테마를 적용하고, 버튼과 다른 탭의 저장소 변경으로 라이트·다크를 바꾼다.
   */
  function initThemeToggle() {
    var toggle = document.querySelector("[data-theme-toggle]");
    if (!toggle) return;

    var storedTheme = getStoredTheme();
    var theme = storedTheme || document.documentElement.getAttribute("data-default-theme") || "dark";

    applyTheme(theme, toggle);

    toggle.addEventListener("click", function () {
      var current = document.documentElement.getAttribute("data-theme") === "light" ? "light" : "dark";
      var next = current === "light" ? "dark" : "light";
      setStoredTheme(next);
      applyTheme(next, toggle);
    });

    window.addEventListener("storage", function (e) {
      if (e.key !== THEME_KEY) return;
      var syncedTheme = e.newValue || document.documentElement.getAttribute("data-default-theme") || "dark";
      applyTheme(syncedTheme, toggle);
    });
  }

  /**
   * html 요소와 토글 버튼에 라이트 또는 다크 테마 상태와 안내 문구를 반영한다.
   * @param {"dark" | "light" | string} theme 적용할 테마. light가 아니면 dark로 둔다.
   * @param {Element} toggle 테마 전환 버튼
   */
  function applyTheme(theme, toggle) {
    var normalizedTheme = theme === "light" ? "light" : "dark";
    var label = toggle.querySelector("[data-theme-label]");
    document.documentElement.setAttribute("data-theme", normalizedTheme);
    toggle.setAttribute("aria-pressed", normalizedTheme === "dark" ? "true" : "false");
    toggle.setAttribute("aria-label", normalizedTheme === "dark" ? "라이트 테마로 전환" : "다크 테마로 전환");

    if (label) {
      label.textContent = normalizedTheme === "dark" ? "다크" : "라이트";
    }
  }

  /**
   * 브라우저에 저장된 테마 값을 읽는다. 저장소를 쓸 수 없으면 null을 돌려준다.
   * @returns {string|null}
   */
  function getStoredTheme() {
    try {
      return localStorage.getItem(THEME_KEY);
    } catch (e) {
      return null;
    }
  }

  /**
   * 선택한 테마를 브라우저 저장소에 남긴다. 저장이 막히면 현재 페이지만 유지한다.
   * @param {string} theme 저장할 테마 이름
   */
  function setStoredTheme(theme) {
    try {
      localStorage.setItem(THEME_KEY, theme);
    } catch (e) {
      /* localStorage가 제한된 환경에서는 현재 페이지에만 적용합니다. */
    }
  }

  /**
   * 자료 드롭다운 하나의 열림 상태, 버튼 표시, 메뉴 숨김을 맞춘다.
   * @param {Element} dropdown 드롭다운 루트
   * @param {boolean} open 열지 여부
   */
  function setResourceDropdown(dropdown, open) {
    var toggle = dropdown.querySelector(".site-nav__dropdown-toggle");
    var menu = dropdown.querySelector(".site-nav__dropdown-menu");
    dropdown.classList.toggle("is-open", open);
    if (toggle) toggle.setAttribute("aria-expanded", open ? "true" : "false");
    if (menu) menu.hidden = !open;
  }

  /**
   * 지정한 하나를 제외한 자료 드롭다운을 모두 닫는다.
   * @param {Element=} except 닫지 않을 드롭다운
   */
  function closeResourceDropdowns(except) {
    queryAll(".site-nav__dropdown").forEach(function (dropdown) {
      if (except && dropdown === except) return;
      setResourceDropdown(dropdown, false);
    });
  }

  /**
   * 모바일 내비게이션을 닫고, 함께 열려 있던 자료 드롭다운도 닫는다.
   * @param {HTMLElement | null} nav 내비게이션 요소
   * @param {HTMLElement | null} toggle 햄버거 버튼
   */
  function closeMobileNav(nav, toggle) {
    setMobileNav(nav, toggle, false);
  }

  /**
   * 모바일 내비게이션의 열림 클래스와 버튼 안내 문구를 설정한다.
   * 닫을 때는 자료 드롭다운도 함께 닫는다.
   * @param {HTMLElement | null} nav 내비게이션 요소
   * @param {HTMLElement | null} toggle 햄버거 버튼
   * @param {boolean} open 열지 여부
   */
  function setMobileNav(nav, toggle, open) {
    if (!nav || !toggle) return;
    nav.classList.toggle("is-open", open);
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
    toggle.setAttribute("aria-label", open ? "메뉴 닫기" : "메뉴 열기");
    if (!open) closeResourceDropdowns();
  }

  /**
   * 연속 호출을 모아 마지막 호출만 wait 밀리초 뒤에 실행하는 함수를 만든다.
   * 창 크기 변경처럼 자주 일어나는 이벤트에서 메뉴를 한 번만 닫기 위해 쓴다.
   * @param {() => void} fn 지연 실행할 함수
   * @param {number} wait 대기 시간(밀리초)
   * @returns {Function}
   */
  function debounce(fn, wait) {
    var t;
    return function () {
      clearTimeout(t);
      t = window.setTimeout(fn, wait);
    };
  }

  /**
   * id가 있는 섹션에 tabindex -1을 넣어, 메뉴 이동 뒤 키보드 포커스를 받을 수 있게 한다.
   */
  function initSectionTargets() {
    queryAll(".section[id]").forEach(function (section) {
      if (!section.hasAttribute("tabindex")) {
        section.setAttribute("tabindex", "-1");
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () {
      initSmoothNav();
      initResourceDropdown();
      initThemeToggle();
      initSectionTargets();
    });
  } else {
    initSmoothNav();
    initResourceDropdown();
    initThemeToggle();
    initSectionTargets();
  }
})();
