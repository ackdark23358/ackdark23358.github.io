(function () {
  "use strict";

  var AUTO_MS = 5500;
  var FADE_MS = 1200;

  function heroSrc(rel) {
    var slash = rel.lastIndexOf("/");
    if (slash === -1) {
      return encodeURI(rel);
    }
    return rel.slice(0, slash + 1) + encodeURIComponent(rel.slice(slash + 1));
  }

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

    function visibleImg() {
      return showA ? imgA : imgB;
    }

    function hiddenImg() {
      return showA ? imgB : imgA;
    }

    function pickIndex() {
      if (images.length === 1) return 0;
      var idx;
      do {
        idx = Math.floor(Math.random() * images.length);
      } while (idx === current);
      return idx;
    }

    function applyImage(imgEl, index) {
      var rel = images[index];
      imgEl.src = heroSrc(rel);
      imgEl.alt = "학습·과제 기록 갤러리 이미지";
    }

    function swapTo(index) {
      if (busy || index === current) return;
      busy = true;

      var next = hiddenImg();
      var prev = visibleImg();
      applyImage(next, index);
      current = index;

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

    function nextRandom() {
      swapTo(pickIndex());
    }

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
