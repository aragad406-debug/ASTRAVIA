/* ASTRAVIA — progressive enhancement for the public site. Everything works without JavaScript. */
(function () {
  "use strict";
  var root = document.documentElement;
  root.classList.remove("no-js");
  root.classList.add("js");

  // Mobile navigation
  var toggle = document.querySelector("[data-nav-toggle]");
  var nav = document.getElementById("primary-nav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && nav.classList.contains("is-open")) {
        nav.classList.remove("is-open");
        toggle.setAttribute("aria-expanded", "false");
        toggle.focus();
      }
    });
  }

  // Optional ambient audio: never autoplays; the visitor turns it on.
  var soundBtn = document.querySelector("[data-sound-toggle]");
  var audio = document.getElementById("ambient-audio");
  if (soundBtn && audio) {
    soundBtn.hidden = false;
    soundBtn.addEventListener("click", function () {
      if (audio.paused) {
        audio.volume = 0.35;
        audio.play().then(function () {
          soundBtn.setAttribute("aria-pressed", "true");
          soundBtn.textContent = soundBtn.dataset.labelOff;
        }).catch(function () {});
      } else {
        audio.pause();
        soundBtn.setAttribute("aria-pressed", "false");
        soundBtn.textContent = soundBtn.dataset.labelOn;
      }
    });
  }

  // Confirmations for destructive forms (studio + account)
  document.addEventListener("submit", function (e) {
    var form = e.target;
    if (form.matches && form.matches("[data-confirm]") && !window.confirm(form.getAttribute("data-confirm"))) {
      e.preventDefault();
    }
  });

  // Move focus to the first invalid field / error summary after a failed submission
  var summary = document.querySelector("[data-error-summary]");
  if (summary) summary.focus();
})();
