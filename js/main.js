(function () {
  "use strict";

  var mqReduceMotion =
    typeof window.matchMedia === "function" ? window.matchMedia("(prefers-reduced-motion: reduce)") : null;
  var THEME_KEY = "portfolio-theme";

  function prefersReducedMotion() {
    return mqReduceMotion ? mqReduceMotion.matches : false;
  }

  /** @param {string} selector */
  function queryAll(selector) {
    return Array.prototype.slice.call(document.querySelectorAll(selector));
  }

  /** @param {Element} root @param {string} selector */
  function queryAllIn(root, selector) {
    return Array.prototype.slice.call(root.querySelectorAll(selector));
  }

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

  /** @param {"dark" | "light" | string} theme @param {Element} toggle */
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

  function getStoredTheme() {
    try {
      return localStorage.getItem(THEME_KEY);
    } catch (e) {
      return null;
    }
  }

  /** @param {string} theme */
  function setStoredTheme(theme) {
    try {
      localStorage.setItem(THEME_KEY, theme);
    } catch (e) {
      /* localStorage가 제한된 환경에서는 현재 페이지에만 적용합니다. */
    }
  }

  /** @param {Element} dropdown @param {boolean} open */
  function setResourceDropdown(dropdown, open) {
    var toggle = dropdown.querySelector(".site-nav__dropdown-toggle");
    var menu = dropdown.querySelector(".site-nav__dropdown-menu");
    dropdown.classList.toggle("is-open", open);
    if (toggle) toggle.setAttribute("aria-expanded", open ? "true" : "false");
    if (menu) menu.hidden = !open;
  }

  /** @param {Element=} except */
  function closeResourceDropdowns(except) {
    queryAll(".site-nav__dropdown").forEach(function (dropdown) {
      if (except && dropdown === except) return;
      setResourceDropdown(dropdown, false);
    });
  }

  /** @param {HTMLElement | null} nav @param {HTMLElement | null} toggle */
  function closeMobileNav(nav, toggle) {
    setMobileNav(nav, toggle, false);
  }

  /**
   * @param {HTMLElement | null} nav
   * @param {HTMLElement | null} toggle
   * @param {boolean} open
   */
  function setMobileNav(nav, toggle, open) {
    if (!nav || !toggle) return;
    nav.classList.toggle("is-open", open);
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
    toggle.setAttribute("aria-label", open ? "메뉴 닫기" : "메뉴 열기");
    if (!open) closeResourceDropdowns();
  }

  /** @param {() => void} fn @param {number} wait */
  function debounce(fn, wait) {
    var t;
    return function () {
      clearTimeout(t);
      t = window.setTimeout(fn, wait);
    };
  }

  /** 섹션에 프로그래매틱 포커스용 tabIndex (스크린 리더 보조는 제한적이나 스킵 내비와 일관) */
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
