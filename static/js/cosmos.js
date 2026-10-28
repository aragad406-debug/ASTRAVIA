/* ASTRAVIA — layered starfield with subtle parallax (Canvas 2D, no dependencies).
   Falls back to the CSS gradient background when canvas is unavailable.
   Honours prefers-reduced-motion (renders a single static frame) and pauses when the tab is hidden. */
(function () {
  "use strict";
  var canvas = document.getElementById("cosmos");
  if (!canvas || !canvas.getContext) return;
  var ctx = canvas.getContext("2d");
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)");
  var stars = [];
  var dust = [];
  var w = 0, h = 0, dpr = 1, scrollY = 0, raf = null, t0 = performance.now();
  var palette = ["245,247,255", "200,220,255", "99,230,255", "232,200,120", "180,160,255"];

  function rand(a, b) { return a + Math.random() * (b - a); }

  function build() {
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    w = window.innerWidth; h = window.innerHeight;
    canvas.width = Math.floor(w * dpr); canvas.height = Math.floor(h * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    var count = Math.min(420, Math.floor((w * h) / 4200));
    stars = [];
    for (var i = 0; i < count; i++) {
      var layer = Math.random() < 0.7 ? 0 : (Math.random() < 0.75 ? 1 : 2);
      stars.push({
        x: Math.random() * w, y: Math.random() * h * 1.6, layer: layer,
        r: layer === 0 ? rand(0.3, 0.9) : layer === 1 ? rand(0.7, 1.4) : rand(1.2, 2.1),
        a: rand(0.25, 0.95), tw: rand(0.4, 1.6), ph: Math.random() * Math.PI * 2,
        c: palette[Math.random() < 0.82 ? 0 : Math.floor(rand(1, palette.length))]
      });
    }
    dust = [];
    for (var j = 0; j < 26; j++) {
      dust.push({ x: Math.random() * w, y: Math.random() * h, r: rand(1, 2.4), vx: rand(-0.04, 0.04), vy: rand(-0.06, -0.015), a: rand(0.15, 0.45) });
    }
  }

  function frame(now) {
    var t = (now - t0) / 1000;
    ctx.clearRect(0, 0, w, h);
    for (var i = 0; i < stars.length; i++) {
      var s = stars[i];
      var parallax = (s.layer + 1) * 0.06;
      var y = ((s.y - scrollY * parallax) % (h * 1.6) + h * 1.6) % (h * 1.6);
      if (y > h + 4) continue;
      var alpha = reduce.matches ? s.a : s.a * (0.65 + 0.35 * Math.sin(t * s.tw + s.ph));
      ctx.beginPath();
      ctx.fillStyle = "rgba(" + s.c + "," + alpha.toFixed(3) + ")";
      ctx.arc(s.x, y, s.r, 0, Math.PI * 2);
      ctx.fill();
      if (s.layer === 2) {
        ctx.fillStyle = "rgba(" + s.c + "," + (alpha * 0.12).toFixed(3) + ")";
        ctx.beginPath(); ctx.arc(s.x, y, s.r * 4, 0, Math.PI * 2); ctx.fill();
      }
    }
    if (!reduce.matches) {
      for (var k = 0; k < dust.length; k++) {
        var d = dust[k];
        d.x += d.vx; d.y += d.vy;
        if (d.y < -10) { d.y = h + 10; d.x = Math.random() * w; }
        ctx.fillStyle = "rgba(99,230,255," + d.a + ")";
        ctx.beginPath(); ctx.arc(d.x, d.y, d.r, 0, Math.PI * 2); ctx.fill();
      }
    }
  }

  function loop(now) {
    frame(now);
    raf = reduce.matches ? null : requestAnimationFrame(loop);
  }

  function start() { if (!raf) raf = requestAnimationFrame(loop); }
  function stop() { if (raf) { cancelAnimationFrame(raf); raf = null; } }

  build();
  start();
  window.addEventListener("resize", function () { build(); if (reduce.matches) frame(performance.now()); }, { passive: true });
  window.addEventListener("scroll", function () { scrollY = window.scrollY; if (reduce.matches) frame(performance.now()); }, { passive: true });
  document.addEventListener("visibilitychange", function () { document.hidden ? stop() : start(); });
  if (reduce.addEventListener) reduce.addEventListener("change", function () { stop(); start(); });
})();
