/* ASTRAVIA — Celestial Guide widget. Lines are rule-based and come from the public API
   (/api/v1/guides/<slug>/lines/), so editors change them in the Creator Studio, not in code. */
(function () {
  "use strict";
  var widget = document.querySelector("[data-guide]");
  if (!widget) return;
  var orb = widget.querySelector("[data-guide-open]");
  var panel = widget.querySelector("[data-guide-panel]");
  var textEl = widget.querySelector("[data-guide-text]");
  var nextBtn = widget.querySelector("[data-guide-next]");
  var closeBtn = widget.querySelector("[data-guide-close]");
  var progress = widget.querySelector("[data-guide-progress]");
  var lines = [], index = 0, loaded = false, audio = null;
  var lang = document.documentElement.lang || "en";

  function render() {
    if (!lines.length) {
      textEl.textContent = widget.dataset.emptyText;
      nextBtn.hidden = true;
      progress.textContent = "";
      return;
    }
    var line = lines[index];
    textEl.textContent = line.text;
    textEl.setAttribute("lang", line.lang || lang);
    progress.textContent = (index + 1) + " / " + lines.length;
    nextBtn.hidden = lines.length < 2;
    if (audio) { audio.pause(); audio = null; }
    if (line.voice_url && widget.dataset.voice === "on") {
      audio = new Audio(line.voice_url);
      audio.play().catch(function () {});
    }
  }

  function load() {
    if (loaded) return Promise.resolve();
    var params = new URLSearchParams({ page: widget.dataset.page || "any", lang: lang });
    if (widget.dataset.world) params.set("world", widget.dataset.world);
    return fetch(widget.dataset.endpoint + "?" + params.toString(), { headers: { Accept: "application/json" }, credentials: "same-origin" })
      .then(function (r) { return r.ok ? r.json() : { lines: [] }; })
      .then(function (data) { lines = data.lines || []; loaded = true; })
      .catch(function () { lines = []; loaded = true; });
  }

  function open() {
    load().then(function () {
      panel.hidden = false;
      orb.setAttribute("aria-expanded", "true");
      index = 0;
      render();
      closeBtn.focus();
    });
  }

  function close() {
    panel.hidden = true;
    orb.setAttribute("aria-expanded", "false");
    if (audio) { audio.pause(); audio = null; }
    orb.focus();
  }

  orb.addEventListener("click", function () { panel.hidden ? open() : close(); });
  closeBtn.addEventListener("click", close);
  nextBtn.addEventListener("click", function () { index = (index + 1) % lines.length; render(); });
  panel.addEventListener("keydown", function (e) { if (e.key === "Escape") close(); });
  document.querySelectorAll("[data-guide-trigger]").forEach(function (btn) {
    btn.addEventListener("click", function (e) { e.preventDefault(); open(); });
  });
})();
