/* ASTRAVIA Creator Studio — small enhancements: mobile nav, inline formset rows, JSON checks, story-flow graph. */
(function () {
  "use strict";
  document.documentElement.classList.add("js");

  var side = document.querySelector("[data-studio-side]");
  var toggle = document.querySelector("[data-studio-nav-toggle]");
  if (side && toggle) {
    toggle.addEventListener("click", function () {
      var open = side.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  document.addEventListener("submit", function (e) {
    var form = e.target;
    if (form.matches && form.matches("[data-confirm]") && !window.confirm(form.getAttribute("data-confirm"))) e.preventDefault();
  });

  // Add inline rows by cloning the formset's empty form template.
  document.querySelectorAll("[data-formset]").forEach(function (set) {
    var prefix = set.getAttribute("data-formset");
    var total = set.querySelector("#id_" + prefix + "-TOTAL_FORMS");
    var template = set.querySelector("template[data-empty-form]");
    var target = set.querySelector("[data-rows]");
    var button = set.querySelector("[data-add-row]");
    if (!total || !template || !target || !button) return;
    button.hidden = false;
    button.addEventListener("click", function () {
      var index = parseInt(total.value, 10);
      var html = template.innerHTML.replace(/__prefix__/g, String(index));
      var wrapper = document.createElement("div");
      wrapper.innerHTML = html.trim();
      var row = wrapper.firstElementChild;
      target.appendChild(row);
      total.value = String(index + 1);
      var first = row.querySelector("input, select, textarea");
      if (first) first.focus();
    });
  });

  // Gentle JSON syntax check on blur (the server still validates).
  document.querySelectorAll("textarea.json").forEach(function (area) {
    area.addEventListener("blur", function () {
      var v = area.value.trim();
      if (!v) { area.removeAttribute("aria-invalid"); return; }
      try { JSON.parse(v); area.removeAttribute("aria-invalid"); area.setCustomValidity(""); }
      catch (err) { area.setAttribute("aria-invalid", "true"); area.setCustomValidity("This is not valid JSON."); area.reportValidity(); }
    });
  });

  // Story flow graph (data comes from a JSON script block rendered by Django).
  var graphEl = document.getElementById("flow-data");
  var canvas = document.querySelector("[data-flow-canvas]");
  if (graphEl && canvas) {
    var graph;
    try { graph = JSON.parse(graphEl.textContent); } catch (e) { graph = null; }
    if (graph && graph.nodes.length) {
      var NS = "http://www.w3.org/2000/svg";
      var colW = 230, rowH = 92, boxW = 180, boxH = 54, pad = 30;
      var rtl = document.documentElement.dir === "rtl";
      var maxX = 0, maxY = 0, pos = {};
      graph.nodes.forEach(function (n) { maxX = Math.max(maxX, n.x); maxY = Math.max(maxY, n.y); });
      var width = (maxX + 1) * colW + pad * 2, height = (maxY + 1) * rowH + pad * 2;
      graph.nodes.forEach(function (n) {
        var x = pad + n.x * colW; if (rtl) x = width - pad - boxW - n.x * colW;
        pos[n.id] = { x: x, y: pad + n.y * rowH };
      });
      var svg = document.createElementNS(NS, "svg");
      svg.setAttribute("width", width); svg.setAttribute("height", height); svg.setAttribute("role", "img");
      svg.setAttribute("aria-label", "Story flow with " + graph.nodes.length + " nodes and " + graph.edges.length + " branches");
      var defs = document.createElementNS(NS, "defs");
      defs.innerHTML = '<marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#A9B3D0"/></marker>';
      svg.appendChild(defs);
      graph.edges.forEach(function (e) {
        var a = pos[e.from], b = pos[e.to];
        if (!a) return;
        if (!b) b = { x: a.x + (rtl ? -colW : colW), y: a.y };
        var x1 = rtl ? a.x : a.x + boxW, y1 = a.y + boxH / 2, x2 = rtl ? b.x + boxW : b.x, y2 = b.y + boxH / 2;
        var mid = (x1 + x2) / 2;
        var path = document.createElementNS(NS, "path");
        path.setAttribute("d", "M" + x1 + "," + y1 + " C" + mid + "," + y1 + " " + mid + "," + y2 + " " + x2 + "," + y2);
        path.setAttribute("class", "flow-edge" + (e.conditional ? " conditional" : "") + (e.external ? " external" : ""));
        path.setAttribute("marker-end", "url(#arrow)");
        svg.appendChild(path);
        if (e.label) {
          var t = document.createElementNS(NS, "text");
          t.setAttribute("x", mid); t.setAttribute("y", (y1 + y2) / 2 - 6); t.setAttribute("text-anchor", "middle"); t.setAttribute("class", "flow-label");
          t.textContent = e.label.length > 28 ? e.label.slice(0, 27) + "…" : e.label;
          svg.appendChild(t);
        }
      });
      graph.nodes.forEach(function (n) {
        var p = pos[n.id];
        var g = document.createElementNS(NS, "g");
        g.setAttribute("class", "flow-node " + n.type + (n.start ? " start" : "") + (n.ending ? " ending" : ""));
        var r = document.createElementNS(NS, "rect");
        r.setAttribute("x", p.x); r.setAttribute("y", p.y); r.setAttribute("width", boxW); r.setAttribute("height", boxH); r.setAttribute("rx", 4);
        var t1 = document.createElementNS(NS, "text");
        t1.setAttribute("x", p.x + 10); t1.setAttribute("y", p.y + 21);
        t1.textContent = (n.title || n.key).length > 24 ? (n.title || n.key).slice(0, 23) + "…" : (n.title || n.key);
        var t2 = document.createElementNS(NS, "text");
        t2.setAttribute("x", p.x + 10); t2.setAttribute("y", p.y + 40); t2.setAttribute("class", "type");
        t2.textContent = n.key + " · " + n.type + (n.start ? " · start" : "") + (n.ending ? " · " + n.ending : "");
        g.appendChild(r); g.appendChild(t1); g.appendChild(t2);
        svg.appendChild(g);
      });
      canvas.innerHTML = "";
      canvas.appendChild(svg);
    }
  }
})();
