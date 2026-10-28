/* ASTRAVIA — homepage orrery: the five worlds orbiting the Heart of Eternity, with a faint broken
   sixth orbit. World data comes from the database via a JSON <script> block (no inline JS).
   Labels are real links (keyboard and screen-reader accessible); the canvas is decorative. */
(function () {
  "use strict";
  var host = document.querySelector("[data-orrery]");
  var dataEl = document.getElementById("orrery-data");
  if (!host || !dataEl) return;
  var canvas = host.querySelector("canvas");
  var labels = host.querySelectorAll("[data-orrery-label]");
  if (!canvas || !canvas.getContext) return;
  var worlds;
  try { worlds = JSON.parse(dataEl.textContent) || []; } catch (e) { return; }
  var ctx = canvas.getContext("2d");
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)");
  var rtl = document.documentElement.dir === "rtl";
  var size = 0, dpr = 1, raf = null, active = -1, start = performance.now();
  var baseAngles = worlds.map(function (_, i) { return -Math.PI / 2 + i * (Math.PI * 2 / Math.max(worlds.length, 1)) + 0.35; });
  var speeds = worlds.map(function (_, i) { return 0.05 / (1 + i * 0.45); });

  function resize() {
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    size = host.clientWidth;
    canvas.width = Math.floor(size * dpr); canvas.height = Math.floor(size * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }

  function hexToRgb(hex) {
    var n = parseInt(hex.replace("#", ""), 16);
    return [(n >> 16) & 255, (n >> 8) & 255, n & 255].join(",");
  }

  function orbitRadius(i) { return size * (0.17 + i * 0.062); }

  function draw(now) {
    var t = reduce.matches ? 0 : (now - start) / 1000;
    var c = size / 2;
    ctx.clearRect(0, 0, size, size);

    // Heart of Eternity
    var pulse = reduce.matches ? 1 : 1 + 0.06 * Math.sin(t * 1.4);
    var g = ctx.createRadialGradient(c, c, 0, c, c, size * 0.13 * pulse);
    g.addColorStop(0, "rgba(255,248,226,1)");
    g.addColorStop(0.18, "rgba(232,200,120,0.95)");
    g.addColorStop(0.45, "rgba(99,230,255,0.25)");
    g.addColorStop(1, "rgba(99,230,255,0)");
    ctx.fillStyle = g; ctx.beginPath(); ctx.arc(c, c, size * 0.13 * pulse, 0, Math.PI * 2); ctx.fill();

    // Orbits and worlds
    for (var i = 0; i < worlds.length; i++) {
      var r = orbitRadius(i);
      var rgb = hexToRgb(worlds[i].color || "#63E6FF");
      ctx.strokeStyle = i === active ? "rgba(" + rgb + ",0.75)" : "rgba(169,179,208,0.16)";
      ctx.lineWidth = i === active ? 1.4 : 1;
      ctx.beginPath(); ctx.arc(c, c, r, 0, Math.PI * 2); ctx.stroke();

      var a = baseAngles[i] + t * speeds[i] * (rtl ? -1 : 1);
      var x = c + Math.cos(a) * r, y = c + Math.sin(a) * r;
      var pr = size * (i === active ? 0.024 : 0.018);
      var glow = ctx.createRadialGradient(x, y, 0, x, y, pr * 4);
      glow.addColorStop(0, "rgba(" + rgb + ",0.55)"); glow.addColorStop(1, "rgba(" + rgb + ",0)");
      ctx.fillStyle = glow; ctx.beginPath(); ctx.arc(x, y, pr * 4, 0, Math.PI * 2); ctx.fill();
      var body = ctx.createRadialGradient(x - pr * 0.4, y - pr * 0.4, 0, x, y, pr);
      body.addColorStop(0, "#ffffff"); body.addColorStop(0.35, "rgb(" + rgb + ")"); body.addColorStop(1, "rgba(5,6,17,1)");
      ctx.fillStyle = body; ctx.beginPath(); ctx.arc(x, y, pr, 0, Math.PI * 2); ctx.fill();

      var label = labels[i];
      if (label) {
        var lx = c + Math.cos(a) * (r + size * 0.055), ly = c + Math.sin(a) * (r + size * 0.055);
        label.style.left = (lx / size * 100).toFixed(2) + "%";
        label.style.top = (ly / size * 100).toFixed(2) + "%";
      }
    }

    // The sixth orbit: broken, unlabeled, barely there.
    var r6 = orbitRadius(worlds.length) + size * 0.03;
    ctx.save();
    ctx.setLineDash([2, 9]);
    ctx.strokeStyle = "rgba(201,209,232,0.18)";
    ctx.beginPath(); ctx.arc(c, c, r6, 0.4 + t * 0.01, Math.PI * 1.55 + t * 0.01); ctx.stroke();
    ctx.restore();
  }

  function loop(now) { draw(now); raf = reduce.matches ? null : requestAnimationFrame(loop); }

  labels.forEach(function (el, i) {
    var link = el.querySelector("a");
    if (!link) return;
    var on = function () { active = i; link.classList.add("is-active"); if (reduce.matches) draw(performance.now()); };
    var off = function () { active = -1; link.classList.remove("is-active"); if (reduce.matches) draw(performance.now()); };
    link.addEventListener("mouseenter", on); link.addEventListener("focus", on);
    link.addEventListener("mouseleave", off); link.addEventListener("blur", off);
  });

  resize();
  raf = requestAnimationFrame(loop);
  window.addEventListener("resize", function () { resize(); draw(performance.now()); }, { passive: true });
  document.addEventListener("visibilitychange", function () {
    if (document.hidden && raf) { cancelAnimationFrame(raf); raf = null; }
    else if (!document.hidden && !raf) { raf = requestAnimationFrame(loop); }
  });
})();
