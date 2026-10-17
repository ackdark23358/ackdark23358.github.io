(function () {
  "use strict";

  var THEME_KEY = "portfolio-theme-v2";
  var mqReduceMotion =
    typeof window.matchMedia === "function" ? window.matchMedia("(prefers-reduced-motion: reduce)") : null;

  function prefersReducedMotion() {
    return mqReduceMotion ? mqReduceMotion.matches : false;
  }

  function queryAll(selector) {
    return Array.prototype.slice.call(document.querySelectorAll(selector));
  }

  function initThemeToggle() {
    var toggle = document.querySelector("[data-theme-toggle]");
    if (!toggle) return;

    var storedTheme = null;
    try {
      storedTheme = localStorage.getItem(THEME_KEY);
    } catch (e) {
      storedTheme = null;
    }

    var theme = storedTheme || document.documentElement.getAttribute("data-default-theme") || "dark";
    applyTheme(theme, toggle);

    toggle.addEventListener("click", function () {
      var current = document.documentElement.getAttribute("data-theme") === "light" ? "light" : "dark";
      var next = current === "light" ? "dark" : "light";
      try {
        localStorage.setItem(THEME_KEY, next);
      } catch (e) {
        /* 저장이 막히면 이 페이지만 바꿉니다. */
      }
      applyTheme(next, toggle);
    });
  }

  function applyTheme(theme, toggle) {
    var normalized = theme === "light" ? "light" : "dark";
    var label = toggle.querySelector("[data-theme-label]");
    document.documentElement.setAttribute("data-theme", normalized);
    toggle.setAttribute("aria-pressed", normalized === "dark" ? "true" : "false");
    toggle.setAttribute("aria-label", normalized === "dark" ? "라이트 테마로 전환" : "다크 테마로 전환");
    if (label) label.textContent = normalized === "dark" ? "다크" : "라이트";
  }

  function setMobileNav(open) {
    var nav = document.getElementById("site-nav");
    var toggle = document.querySelector(".nav-toggle");
    if (!nav || !toggle) return;
    nav.classList.toggle("is-open", open);
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
    toggle.setAttribute("aria-label", open ? "메뉴 닫기" : "메뉴 열기");
    if (!open) closeDropdowns();
  }

  function setDropdown(dropdown, open) {
    var toggle = dropdown.querySelector(".site-nav__dropdown-toggle");
    var menu = dropdown.querySelector(".site-nav__dropdown-menu");
    dropdown.classList.toggle("is-open", open);
    if (toggle) toggle.setAttribute("aria-expanded", open ? "true" : "false");
    if (menu) menu.hidden = !open;
  }

  function closeDropdowns(except) {
    queryAll(".site-nav__dropdown").forEach(function (dropdown) {
      if (except && dropdown === except) return;
      setDropdown(dropdown, false);
    });
  }

  function initNav() {
    var nav = document.getElementById("site-nav");
    var toggle = document.querySelector(".nav-toggle");

    if (toggle && nav) {
      toggle.addEventListener("click", function () {
        setMobileNav(!nav.classList.contains("is-open"));
      });
    }

    queryAll(".site-nav__dropdown").forEach(function (dropdown) {
      var dropdownToggle = dropdown.querySelector(".site-nav__dropdown-toggle");
      if (!dropdownToggle) return;
      dropdownToggle.addEventListener("click", function (e) {
        e.preventDefault();
        var open = dropdownToggle.getAttribute("aria-expanded") !== "true";
        closeDropdowns(dropdown);
        setDropdown(dropdown, open);
      });
    });

    queryAll('a[href^="#"]').forEach(function (link) {
      link.addEventListener("click", function (e) {
        var id = (link.getAttribute("href") || "").slice(1);
        var target = id ? document.getElementById(id) : null;
        if (!target) return;
        e.preventDefault();
        target.scrollIntoView({ behavior: prefersReducedMotion() ? "auto" : "smooth", block: "start" });
        if (!target.hasAttribute("tabindex")) target.setAttribute("tabindex", "-1");
        target.focus({ preventScroll: true });
        setMobileNav(false);
        closeDropdowns();
      });
    });

    document.addEventListener("click", function (e) {
      var target = e.target;
      if (target instanceof Element && target.closest(".site-nav__dropdown")) return;
      closeDropdowns();
    });

    document.addEventListener("keydown", function (e) {
      if (e.key !== "Escape") return;
      closeDropdowns();
      if (nav && nav.classList.contains("is-open")) {
        setMobileNav(false);
        if (toggle) toggle.focus();
      }
    });

    window.addEventListener("resize", function () {
      if (window.innerWidth > 768) setMobileNav(false);
    });
  }

  function initSectionTargets() {
    queryAll(".section[id], .hero[id]").forEach(function (section) {
      if (!section.hasAttribute("tabindex")) section.setAttribute("tabindex", "-1");
    });
  }

  initThemeToggle();
  initNav();
  initSectionTargets();
})();
