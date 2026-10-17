// Landing page: the live spreadsheet preview in the hero and the "How it works" demo brief.
// Every cell (address, formula, value per case) comes from the real engine via #xl-data;
// this script only renders it, moves the selection and swaps sheets and cases.
(function () {
  "use strict";

  function readJson(id) {
    var el = document.getElementById(id);
    if (!el) return null;
    try { return JSON.parse(el.textContent); } catch (e) { return null; }
  }

  // ---------- spreadsheet preview ----------
  function initSheet(data) {
    var grid = document.getElementById("xl-grid");
    var nameEl = document.getElementById("xl-name");
    var fEl = document.getElementById("xl-f");
    var tabBtns = Array.prototype.slice.call(document.querySelectorAll("#xl [data-tab]"));
    if (!grid || !nameEl || !fEl) return;
    var state = { tab: "sum", c: data["case"] || 2, sel: data.tabs.sum.start };

    function view() { return data.tabs[state.tab]; }
    function text(cell) { return Array.isArray(cell.v) ? cell.v[state.c - 1] : cell.v; }
    function findCell(addr) {
      var rows = view().rows;
      for (var i = 0; i < rows.length; i++) {
        for (var j = 0; j < rows[i].cells.length; j++) {
          if (rows[i].cells[j].a === addr) return rows[i].cells[j];
        }
      }
      return null;
    }
    function el(tag, cls, txt) {
      var e = document.createElement(tag);
      if (cls) e.className = cls;
      if (txt !== undefined && txt !== null) e.textContent = txt;
      return e;
    }

    function render() {
      var v = view();
      grid.textContent = "";
      grid.style.gridTemplateColumns = "40px " + v.cols.map(function (c, i) {
        return i === v.cols.length - 1 ? "minmax(" + c.px + "px, 1fr)" : c.px + "px";
      }).join(" ");
      grid.setAttribute("aria-label", v.sheet + " sheet");
      var head = el("div", "xl__row xl__row--head");
      head.setAttribute("role", "row");
      var corner = el("span", "xh xh--corner");
      corner.setAttribute("aria-hidden", "true");
      head.appendChild(corner);
      v.cols.forEach(function (c) {
        var h = el("span", "xh", c.letter);
        h.setAttribute("role", "columnheader");
        h.setAttribute("data-col", c.letter);
        head.appendChild(h);
      });
      grid.appendChild(head);
      v.rows.forEach(function (r, ri) {
        var row = el("div", "xl__row");
        row.setAttribute("role", "row");
        var n = el("span", "xn", String(r.n));
        n.setAttribute("role", "rowheader");
        n.setAttribute("data-row", String(r.n));
        row.appendChild(n);
        var ci = 0;
        r.cells.forEach(function (c) {
          var node;
          if (c.select) {
            node = el("span", "xc selector b");
            var lab = el("label", "sr-only", "Scenario: 1 Low, 2 Base, 3 High");
            lab.setAttribute("for", "xl-case");
            var s = el("select");
            s.id = "xl-case";
            s.setAttribute("data-a", c.a);
            ["1", "2", "3"].forEach(function (o) {
              var opt = el("option", null, o);
              opt.value = o;
              if (Number(o) === state.c) opt.selected = true;
              s.appendChild(opt);
            });
            node.appendChild(lab);
            node.appendChild(s);
          } else {
            node = el("button", "xc" + (c.cls ? " " + c.cls : ""), text(c));
            node.type = "button";
            node.tabIndex = -1;
            if (c.cls.indexOf("res") !== -1 && text(c).indexOf("PASS") !== 0) node.className += " res--warn";
            if (c.tick) {
              var tk = el("span", "tk", "✓");
              tk.setAttribute("aria-hidden", "true");
              node.appendChild(tk);
            }
          }
          node.setAttribute("role", "gridcell");
          node.setAttribute("data-a", c.a);
          node.setAttribute("data-r", String(ri));
          node.setAttribute("data-c", String(ci));
          node.setAttribute("data-s", String(c.span));
          if (c.span > 1) node.style.gridColumn = "span " + c.span;
          ci += c.span;
          row.appendChild(node);
        });
        grid.appendChild(row);
      });
      select(state.sel, false);
    }

    function select(addr, focus) {
      var cell = findCell(addr) || findCell(view().start);
      if (!cell) return;
      state.sel = cell.a;
      Array.prototype.forEach.call(grid.querySelectorAll(".xc"), function (n) {
        var on = n.getAttribute("data-a") === cell.a;
        n.classList.toggle("is-sel", on);
        if (n.tagName === "BUTTON") n.tabIndex = on ? 0 : -1;
      });
      var col = cell.a.replace(/[0-9]/g, ""), row = cell.a.replace(/[A-Z]/g, "");
      Array.prototype.forEach.call(grid.querySelectorAll(".xh[data-col]"), function (h) {
        h.classList.toggle("is-on", h.getAttribute("data-col") === col);
      });
      Array.prototype.forEach.call(grid.querySelectorAll(".xn"), function (h) {
        h.classList.toggle("is-on", h.getAttribute("data-row") === row);
      });
      nameEl.textContent = cell.a;
      fEl.textContent = cell.f || (cell.select ? String(state.c) : text(cell));
      if (focus) {
        var target = grid.querySelector('[data-a="' + cell.a + '"]');
        if (target) (target.tagName === "BUTTON" ? target : target.querySelector("select")).focus();
      }
    }

    function move(from, dr, dc) {
      var r = Number(from.getAttribute("data-r")), c = Number(from.getAttribute("data-c"));
      if (dc) {
        var sib = dc > 0 ? from.nextElementSibling : from.previousElementSibling;
        if (sib && sib.classList.contains("xc")) select(sib.getAttribute("data-a"), true);
        return;
      }
      var cells = grid.querySelectorAll('.xc[data-r="' + (r + dr) + '"]');
      for (var i = 0; i < cells.length; i++) {
        var s = Number(cells[i].getAttribute("data-c")), w = Number(cells[i].getAttribute("data-s"));
        if (c >= s && c < s + w) { select(cells[i].getAttribute("data-a"), true); return; }
      }
    }

    grid.addEventListener("click", function (e) {
      var cell = e.target.closest(".xc");
      if (cell) select(cell.getAttribute("data-a"), false);
    });
    grid.addEventListener("focusin", function (e) {
      if (e.target.id === "xl-case") select("B4", false);
    });
    grid.addEventListener("change", function (e) {
      if (e.target.id !== "xl-case") return;
      state.c = Number(e.target.value) || 2;
      render();
      select("B4", true);
    });
    grid.addEventListener("keydown", function (e) {
      var cell = e.target.closest(".xc");
      if (!cell || e.target.tagName === "SELECT") return;
      var d = { ArrowUp: [-1, 0], ArrowDown: [1, 0], ArrowLeft: [0, -1], ArrowRight: [0, 1] }[e.key];
      if (!d) return;
      e.preventDefault();
      move(cell, d[0], d[1]);
    });

    function showTab(k, focus) {
      state.tab = k;
      state.sel = view().start;
      tabBtns.forEach(function (b) {
        var on = b.getAttribute("data-tab") === k;
        b.setAttribute("aria-selected", on ? "true" : "false");
        b.tabIndex = on ? 0 : -1;
        if (on && focus) b.focus();
      });
      render();
    }
    tabBtns.forEach(function (b, i) {
      b.addEventListener("click", function () { showTab(b.getAttribute("data-tab"), false); });
      b.addEventListener("keydown", function (e) {
        var j = e.key === "ArrowRight" ? i + 1 : e.key === "ArrowLeft" ? i - 1 : e.key === "Home" ? 0 : e.key === "End" ? tabBtns.length - 1 : null;
        if (j === null) return;
        e.preventDefault();
        j = (j + tabBtns.length) % tabBtns.length;
        showTab(tabBtns[j].getAttribute("data-tab"), true);
      });
    });

    render();
  }

  // ---------- "How it works" demo brief ----------
  function initDemo(d) {
    var root = document.getElementById("demo");
    if (!root || !d) return;
    var steps = [
      { key: "type", q: "What kind of business is it?", opts: d.types },
      { key: "goal", q: "What should the model answer?", opts: d.goals },
      { key: "horizon", q: "How far ahead, and in how much detail?", opts: d.horizons.map(function (h) { return [h[0] + "|" + h[1], h[2]]; }) }
    ];
    var st = { i: 0, ans: {} };
    var $ = function (id) { return document.getElementById(id); };
    var legend = $("demo-legend"), opts = $("demo-opts"), bar = $("demo-bar"), label = $("demo-step");
    var back = $("demo-back"), next = $("demo-next"), done = $("demo-done"), q = $("demo-q"), foot = $("demo-foot");
    var sample = $("demo-sample"), go = $("demo-go"), summary = $("demo-summary"), restart = $("demo-restart");

    function labelOf(stepIdx, v) {
      var o = steps[stepIdx].opts.filter(function (x) { return x[0] === v; })[0];
      return o ? o[1] : "";
    }
    function render() {
      var finished = st.i >= steps.length;
      q.hidden = finished;
      foot.hidden = finished;
      done.hidden = !finished;
      bar.style.width = Math.round(Math.min(st.i + 1, steps.length) / steps.length * 100) + "%";
      label.textContent = finished ? "Preview complete" : "Step " + (st.i + 1) + " of " + steps.length;
      if (finished) {
        var hz = (st.ans.horizon || "3|monthly").split("|");
        summary.textContent = labelOf(0, st.ans.type) + ". " + labelOf(1, st.ans.goal) + ". " + labelOf(2, st.ans.horizon) + ". " +
          (sample.checked ? "Starting from sample numbers you can change." : "Starting from your own numbers.");
        var qs = "type=" + encodeURIComponent(st.ans.type) + "&goal=" + encodeURIComponent(st.ans.goal) +
          "&horizon=" + encodeURIComponent(hz[0]) + "&granularity=" + encodeURIComponent(hz[1]) + (sample.checked ? "&sample=1" : "");
        go.href = "/start?" + qs;
        go.focus();
        return;
      }
      var s = steps[st.i];
      legend.textContent = s.q;
      opts.textContent = "";
      s.opts.forEach(function (o) {
        var b = document.createElement("button");
        b.type = "button";
        b.className = "opt";
        b.textContent = o[1];
        b.setAttribute("data-v", o[0]);
        b.setAttribute("aria-pressed", st.ans[s.key] === o[0] ? "true" : "false");
        opts.appendChild(b);
      });
      back.hidden = st.i === 0;
      next.disabled = !st.ans[s.key];
    }
    opts.addEventListener("click", function (e) {
      var b = e.target.closest(".opt");
      if (!b) return;
      st.ans[steps[st.i].key] = b.getAttribute("data-v");
      Array.prototype.forEach.call(opts.children, function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
      next.disabled = false;
    });
    next.addEventListener("click", function () {
      if (!st.ans[steps[st.i].key]) return;
      st.i += 1;
      render();
      if (st.i < steps.length) legend.focus();
    });
    back.addEventListener("click", function () { st.i = Math.max(0, st.i - 1); render(); });
    restart.addEventListener("click", function () { st.i = 0; st.ans = {}; render(); legend.focus(); });
    legend.tabIndex = -1;
    render();
  }

  var sheet = readJson("xl-data");
  if (sheet) initSheet(sheet);
  initDemo(readJson("demo-data"));
})();
