// Landing hero: switch case (Low / Base / High) and sheet tab in the live preview.
// Every view is rendered on the server into #sheet-views; this script only swaps them.
(function () {
  "use strict";
  var dataEl = document.getElementById("sheet-views");
  var grid = document.getElementById("sheet-grid");
  if (!dataEl || !grid) return;
  var views;
  try { views = JSON.parse(dataEl.textContent); } catch (e) { return; }
  var state = { c: "2", t: "sum" };
  var caseBtns = document.querySelectorAll("[data-case]");
  var tabBtns = Array.prototype.slice.call(document.querySelectorAll("[data-tab]"));
  var fcell = document.getElementById("fcell");
  var fformula = document.getElementById("fformula");

  function span(text, role, cls) {
    var s = document.createElement("span");
    s.setAttribute("role", role);
    if (cls) s.className = cls;
    s.textContent = text;
    return s;
  }

  function row(r) {
    var head = r.kind === "head";
    var el = document.createElement("div");
    el.className = "r" + (r.chk ? " r--chk" : "") + (r.kind ? " r--" + r.kind : "");
    el.setAttribute("role", "row");
    var first = span(r.label, head ? "columnheader" : "rowheader");
    if (head && !r.label) {
      var hidden = document.createElement("span");
      hidden.className = "sr-only";
      hidden.textContent = "Line item";
      first.appendChild(hidden);
    }
    el.appendChild(first);
    if (r.chk) {
      el.appendChild(span(r.result, head ? "columnheader" : "cell", head ? "" : "res" + (r.warn ? " res--warn" : "")));
      el.appendChild(span(r.what, head ? "columnheader" : "cell", head ? "" : "what"));
      return el;
    }
    r.cells.forEach(function (c) {
      var s = span(c.v, head ? "columnheader" : "cell", c.on ? "on" : "");
      if (!head) {
        var tk = document.createElement("span");
        tk.className = "tk";
        tk.setAttribute("aria-hidden", "true");
        tk.textContent = c.tick ? "✓" : "";
        s.appendChild(tk);
      }
      el.appendChild(s);
    });
    return el;
  }

  function render() {
    var v = views[state.c][state.t];
    grid.textContent = "";
    v.rows.forEach(function (r) { grid.appendChild(row(r)); });
    fcell.textContent = v.cell;
    fformula.textContent = v.formula;
    grid.setAttribute("aria-labelledby", "tab-" + state.t);
    Array.prototype.forEach.call(caseBtns, function (b) {
      b.setAttribute("aria-pressed", b.getAttribute("data-case") === state.c ? "true" : "false");
    });
    tabBtns.forEach(function (b) {
      var on = b.getAttribute("data-tab") === state.t;
      b.setAttribute("aria-selected", on ? "true" : "false");
      b.tabIndex = on ? 0 : -1;
    });
  }

  Array.prototype.forEach.call(caseBtns, function (b) {
    b.addEventListener("click", function () { state.c = b.getAttribute("data-case"); render(); });
  });
  tabBtns.forEach(function (b, i) {
    b.addEventListener("click", function () { state.t = b.getAttribute("data-tab"); render(); });
    b.addEventListener("keydown", function (e) {
      var j = e.key === "ArrowRight" ? i + 1 : e.key === "ArrowLeft" ? i - 1 : e.key === "Home" ? 0 : e.key === "End" ? tabBtns.length - 1 : null;
      if (j === null) return;
      e.preventDefault();
      var next = tabBtns[(j + tabBtns.length) % tabBtns.length];
      state.t = next.getAttribute("data-tab");
      render();
      next.focus();
    });
  });
})();
