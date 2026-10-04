/**
 * 자기소개서 페이지에서 현재 보고 있는 절에 맞춰 사이드 메뉴를 표시하고, 맨 위로 버튼을 연결한다.
 */
(function () {
  "use strict";

  /**
   * data-section이 id와 같은 메뉴 링크에만 활성 클래스를 붙인다.
   * @param {string} id 현재 화면에 들어온 절의 id
   */
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

  /**
   * 본문 절이 화면의 일정 비율 이상 보이면 해당 메뉴를 활성으로 바꾼다.
   * 관찰이 시작되기 전에는 첫 절을 활성으로 둔다.
   */
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

  /**
   * 맨 위로 버튼을 누르면 페이지 최상단으로 부드럽게 스크롤한다.
   */
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
