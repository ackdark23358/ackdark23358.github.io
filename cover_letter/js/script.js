(function () {
  "use strict";

  function setActiveNav(id) {
    document.querySelectorAll(".nav-link").forEach(function (link) {
      var sec = link.getAttribute("data-section");
      if (sec === id) {
        link.classList.add("is-active");
      } else {
        link.classList.remove("is-active");
      }
    });
  }

  function initScrollSpy() {
    var sections = document.querySelectorAll(".content-section[id]");
    if (!sections.length) return;

    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting && entry.intersectionRatio >= 0.25) {
            setActiveNav(entry.target.id);
          }
        });
      },
      {
        root: null,
        rootMargin: "-20% 0px -55% 0px",
        threshold: [0, 0.25, 0.5, 0.75, 1]
      }
    );

    sections.forEach(function (section) {
      observer.observe(section);
    });

    /* 첫 화면 */
    var first = sections[0];
    if (first && first.id) setActiveNav(first.id);
  }

  function initToTop() {
    var btn = document.getElementById("toTop");
    if (!btn) return;
    btn.addEventListener("click", function () {
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    initScrollSpy();
    initToTop();
  });
})();
