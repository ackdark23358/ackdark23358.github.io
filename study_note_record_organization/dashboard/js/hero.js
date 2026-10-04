/**
 * 학습 기록 대시보드 상단에서 이미지 두 장을 번갈아 보여 주는 히어로 갤러리를 초기화한다.
 */
(function () {
  "use strict";

  var AUTO_MS = 5500;
  var FADE_MS = 1200;

  /**
   * 상대 경로의 파일 이름만 인코딩해 img src로 쓸 수 있는 주소를 만든다.
   * @param {string} rel data/image 기준 상대 경로
   * @returns {string}
   */
  function heroSrc(rel) {
    var slash = rel.lastIndexOf("/");
    if (slash === -1) {
      return encodeURI(rel);
    }
    return rel.slice(0, slash + 1) + encodeURIComponent(rel.slice(slash + 1));
  }

  /**
   * 히어로에 쓸 이미지 경로 목록을 가져온다.
   * hero-images.js의 HERO_IMAGES를 우선하고, 없으면 SITE_DATA.heroImages를 본다.
   * @returns {string[]}
   */
  function getHeroImages() {
    if (window.HERO_IMAGES && window.HERO_IMAGES.length) {
      return window.HERO_IMAGES;
    }
    var data = window.SITE_DATA;
    if (data && data.heroImages && data.heroImages.length) {
      return data.heroImages;
    }
    return [];
  }

  /**
   * 히어로 영역을 찾고 이미지가 있으면 첫 장을 띄운 뒤, 클릭과 타이머로 다음 장으로 넘긴다.
   * 이미지가 없으면 히어로 구역을 숨긴다.
   */
  function initHero() {
    var section = document.getElementById("hero");
    var stage = document.getElementById("hero-stage");
    var imgA = document.getElementById("hero-img-a");
    var imgB = document.getElementById("hero-img-b");
    if (!section || !stage || !imgA || !imgB) return;

    var images = getHeroImages();
    if (!images.length) {
      section.classList.add("hidden");
      return;
    }

    section.classList.remove("hidden");
    section.removeAttribute("hidden");

    var current = -1;
    var showA = true;
    var busy = false;
    var timer = null;

    /**
     * 지금 화면에 보이는 히어로 이미지 요소를 돌려준다.
     * @returns {HTMLImageElement}
     */
    function visibleImg() {
      return showA ? imgA : imgB;
    }

    /**
     * 다음에 보여 주기 위해 숨겨 둔 히어로 이미지 요소를 돌려준다.
     * @returns {HTMLImageElement}
     */
    function hiddenImg() {
      return showA ? imgB : imgA;
    }

    /**
     * 현재 장과 다른 이미지 인덱스를 무작위로 고른다. 한 장이면 0을 돌려준다.
     * @returns {number}
     */
    function pickIndex() {
      if (images.length === 1) return 0;
      var idx;
      do {
        idx = Math.floor(Math.random() * images.length);
      } while (idx === current);
      return idx;
    }

    /**
     * 이미지 요소의 src와 대체 텍스트를 목록의 해당 장으로 바꾼다.
     * @param {HTMLImageElement} imgEl 대상 이미지
     * @param {number} index 이미지 목록 인덱스
     */
    function applyImage(imgEl, index) {
      var rel = images[index];
      imgEl.src = heroSrc(rel);
      imgEl.alt = "학습·과제 기록 갤러리 이미지";
    }

    /**
     * 숨겨 둔 이미지에 다음 장을 불러온 뒤, 로드가 끝나면 보이는 장을 교체한다.
     * 이미 전환 중이거나 같은 장이면 아무것도 하지 않는다.
     * @param {number} index 보여줄 이미지 인덱스
     */
    function swapTo(index) {
      if (busy || index === current) return;
      busy = true;

      var next = hiddenImg();
      var prev = visibleImg();
      applyImage(next, index);
      current = index;

      /**
       * 새 이미지에 표시 클래스를 옮기고 전환 중 상태를 해제한다.
       */
      function finish() {
        next.classList.add("is-visible");
        prev.classList.remove("is-visible");
        showA = next === imgA;
        busy = false;
      }

      if (next.complete && next.naturalWidth > 0) {
        finish();
      } else {
        next.onload = function () {
          next.onload = null;
          finish();
        };
        next.onerror = function () {
          next.onerror = null;
          busy = false;
        };
      }
    }

    /**
     * 현재와 다른 장을 골라 교체한다.
     */
    function nextRandom() {
      swapTo(pickIndex());
    }

    /**
     * 자동 전환 타이머를 다시 시작한다.
     * 동작 줄이기가 켜져 있거나 이미지가 한 장이면 타이머를 두지 않는다.
     */
    function startTimer() {
      if (timer) clearInterval(timer);
      var reduced =
        window.matchMedia &&
        window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      if (!reduced && images.length > 1) {
        timer = setInterval(nextRandom, AUTO_MS);
      }
    }

    current = pickIndex();
    applyImage(imgA, current);
    imgA.classList.add("is-visible");

    stage.addEventListener("click", function () {
      nextRandom();
      startTimer();
    });

    startTimer();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initHero);
  } else {
    initHero();
  }
})();
