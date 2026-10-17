// Landing page: the spreadsheet window in the hero and the "How it works" demo brief.
// The window shows the real sample workbook (every sheet, cell, formula and value in each scenario,
// from app/data/landing_workbook.json). The first sheet is rendered on the server by app/xlview.py;
// this script renders the same markup, then behaves like a spreadsheet app: selection and ranges,
// keyboard navigation, edit mode with precedents highlighted, the scenario list on Dashboard!B4,
// sheet tabs and the status bar sum. It is read-only: nothing here changes the file.
(function () {
  "use strict";

  function readJson(id) {
    var el = document.getElementById(id);
    if (!el) return null;
    try { return JSON.parse(el.textContent); } catch (e) { return null; }
  }

  // ---------- shared with app/xlview.py (keep in step) ----------
  var ROW_HEAD_PX = 34, COL_HEAD_PX = 20, DEFAULT_COL_PX = 64, MIN_GRID_PX = 1600, EXTRA_ROWS = 10, MIN_ROWS = 32;
  var REF_COLORS = 7;

  function colLetter(n) {
    var s = "";
    while (n > 0) { var m = (n - 1) % 26; s = String.fromCharCode(65 + m) + s; n = Math.floor((n - 1) / 26); }
    return s;
  }
  function colNumber(letters) {
    var n = 0;
    for (var i = 0; i < letters.length; i++) n = n * 26 + (letters.charCodeAt(i) - 64);
    return n;
  }
  function parseAddr(a) {
    var m = /^\$?([A-Z]{1,3})\$?(\d+)$/.exec(String(a).toUpperCase());
    return m ? { r: Number(m[2]), c: colNumber(m[1]) } : null;
  }
  function addr(r, c) { return colLetter(c) + r; }

  function splitSections(fmt) {
    var out = [], cur = "", quoted = false;
    for (var i = 0; i < fmt.length; i++) {
      var ch = fmt[i];
      if (ch === "\\" && i + 1 < fmt.length) { cur += ch + fmt[i + 1]; i++; continue; }
      if (ch === '"') quoted = !quoted;
      if (ch === ";" && !quoted) { out.push(cur); cur = ""; continue; }
      cur += ch;
    }
    out.push(cur);
    return out;
  }
  function parseSection(sec) {
    var toks = [], i = 0;
    while (i < sec.length) {
      var ch = sec[i];
      if (ch === '"') {
        var j = sec.indexOf('"', i + 1);
        if (j < 0) j = sec.length;
        toks.push(["lit", sec.slice(i + 1, j)]); i = j + 1;
      } else if (ch === "\\") { toks.push(["lit", sec.slice(i + 1, i + 2)]); i += 2; }
      else if ("0#,.".indexOf(ch) !== -1) { toks.push(["ph", ch]); i++; }
      else { toks.push(["lit", ch]); i++; }
    }
    var run = "", first = -1, prefix = "", suffix = "";
    toks.forEach(function (t, n) {
      if (t[0] === "ph") { run += t[1]; if (first < 0) first = n; }
    });
    if (first < 0) first = toks.length;
    toks.forEach(function (t, n) { if (t[0] === "lit") { if (n < first) prefix += t[1]; else suffix += t[1]; } });
    var dot = run.indexOf(".");
    return { prefix: prefix, suffix: suffix, decimals: dot < 0 ? 0 : run.slice(dot + 1).replace(/[^0#]/g, "").length,
      thousands: run.indexOf(",") !== -1, percent: (prefix + suffix).indexOf("%") !== -1, digits: run.length > 0 };
  }
  function fixed(x, d, thousands) {
    var s = x.toFixed(d);
    if (!thousands) return s;
    var parts = s.split(".");
    parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    return parts.join(".");
  }
  function general(v) {
    if (Number.isInteger(v) && Math.abs(v) < 1e11) return String(v);
    return String(parseFloat(v.toPrecision(10)));
  }
  function formatValue(v, fmt) {
    if (v === null || v === undefined || v === "") return ["", "e"];
    if (typeof v === "boolean") return [v ? "TRUE" : "FALSE", "b"];
    if (typeof v === "string") return [v, "s"];
    if (fmt === "General" || fmt === "@") return [general(v), "n"];
    var secs = splitSections(fmt), sec, x, sign = "";
    if (v < 0 && secs.length > 1) { sec = secs[1]; x = -v; }
    else if (Math.abs(v) < 1e-9 && secs.length > 2) { sec = secs[2]; x = 0; }
    else { sec = secs[0]; x = Math.abs(v); sign = v < 0 ? "-" : ""; }
    var p = parseSection(sec);
    if (!p.digits) return [p.prefix + p.suffix, "n"];
    if (p.percent) x *= 100;
    return [sign + p.prefix + fixed(x, p.decimals, p.thousands) + p.suffix, "n"];
  }

  // ---------- the spreadsheet window ----------
  function initSheet(root) {
    var $ = function (id) { return document.getElementById(id); };
    var grid = $("xl-grid"), scroller = $("xl-scroll"), nameBox = $("xl-name"), fbar = $("xl-f"), fexp = $("xl-fexp");
    var fbtns = root.querySelector(".xl__fbtns"), modeEl = $("xl-mode"), statsEl = $("xl-stats");
    var tabs = Array.prototype.slice.call(root.querySelectorAll("[data-sheet]"));
    var tools = { size: $("xl-size"), b: $("xl-b"), i: $("xl-i"), fill: $("xl-fill"), color: $("xl-color"),
      al: $("xl-al"), ac: $("xl-ac"), ar: $("xl-ar"), nf: $("xl-nf") };
    if (!grid || !root.getAttribute("data-src")) return;

    var wb = null, sh = null, L = null, els = [], deco = [], msgTimer = null;
    var st = { sheet: 0, kase: 2, a: null, f: null, editing: false, list: false, drag: false, memo: {} };

    function cellEntry(r, c) { return sh.cells[addr(r, c)] || null; }
    function rawValue(e) {
      if (!e || e.length < 2) return null;
      var v = e[1];
      return Array.isArray(v) ? v[st.kase - 1] : v;
    }
    function styleOf(e) { return e ? wb.styles[e[0]] : {}; }
    function fmtOf(e) { return wb.numfmts[styleOf(e).nf || 0]; }
    function view(r, c) {
      var e = cellEntry(r, c);
      if (!e) return { text: "", kind: "e", cls: "c e", e: null };
      var s = styleOf(e), tk = formatValue(rawValue(e), fmtOf(e)), cls = ["c"];
      if (s.fill) cls.push("f" + s.fill);
      if (s.color) cls.push("k-" + s.color);
      if (s.b) cls.push("b");
      if (s.i) cls.push("i");
      if (s.sz) cls.push("z" + Math.floor(s.sz));
      if (s.bt) cls.push("bt");
      if (s.bb) cls.push(s.bb === "double" ? "bbd" : "bb");
      if (s.h === "left" || s.h === "center" || s.h === "right") cls.push("h" + s.h[0]);
      else if (tk[1] === "n") cls.push("hr");
      else if (tk[1] === "b") cls.push("hc");
      if (tk[1] === "e") cls.push("e");
      return { text: tk[0], kind: tk[1], cls: cls.join(" "), e: e };
    }

    function layout() {
      var cols = sh.cols.map(function (w) { return Math.floor(w * 7 + 5); });
      var sum = cols.reduce(function (a, b) { return a + b; }, 0);
      while (sum < MIN_GRID_PX || cols.length < sh.cols.length + 2) { cols.push(DEFAULT_COL_PX); sum += DEFAULT_COL_PX; }
      var rows = sh.rows.map(function (pt) { return Math.round(pt * 4 / 3); });
      while (rows.length < Math.max(MIN_ROWS, sh.rows.length + EXTRA_ROWS)) rows.push(20);
      var x = [ROW_HEAD_PX], y = [COL_HEAD_PX];
      cols.forEach(function (w, i) { x.push(x[i] + w); });
      rows.forEach(function (h, i) { y.push(y[i] + h); });
      var fr = sh.freeze ? sh.freeze[0] : 0, fc = sh.freeze ? sh.freeze[1] : 0;
      return { cols: cols, rows: rows, x: x, y: y, nr: rows.length, nc: cols.length, fr: fr, fc: fc };
    }
    function el(r, c) { return els[(r - 1) * L.nc + (c - 1)]; }
    function esc(s) { return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"); }

    function render() {
      L = layout();
      grid.style.gridTemplateColumns = ROW_HEAD_PX + "px " + L.cols.map(function (w) { return w + "px"; }).join(" ");
      grid.style.gridTemplateRows = COL_HEAD_PX + "px " + L.rows.map(function (h) { return h + "px"; }).join(" ");
      grid.setAttribute("aria-label", sh.name + " sheet");
      var h = ['<div role="row" class="xr"><span class="hd hd--corner" aria-hidden="true"></span>'];
      for (var c = 1; c <= L.nc; c++) {
        h.push('<span role="columnheader" class="hd' + (c <= L.fc ? " fzh" : "") + '" data-col="' + c + '"' + (c <= L.fc ? ' style="left:' + L.x[c - 1] + 'px"' : "") + ">" + colLetter(c) + "</span>");
      }
      h.push("</div>");
      for (var r = 1; r <= L.nr; r++) {
        h.push('<div role="row" class="xr"><span role="rowheader" class="rh' + (r <= L.fr ? " fzh" : "") + '" data-row="' + r + '"' + (r <= L.fr ? ' style="top:' + L.y[r - 1] + 'px"' : "") + ">" + r + "</span>");
        for (c = 1; c <= L.nc; c++) {
          var v = view(r, c), cls = v.cls, sty = "";
          if (r <= L.fr || c <= L.fc) {
            cls += " fz" + (r <= L.fr && c <= L.fc ? " fz2" : "");
            if (r <= L.fr) sty += "top:" + L.y[r - 1] + "px;";
            if (c <= L.fc) sty += "left:" + L.x[c - 1] + "px;";
            if (r === L.fr) cls += " fzr";
            if (c === L.fc) cls += " fzc";
          }
          h.push('<span role="gridcell" id="xc-' + addr(r, c) + '" class="' + cls + '" data-r="' + r + '" data-c="' + c + '"' +
            (sty ? ' style="' + sty + '"' : "") + ">" + esc(v.text) + "</span>");
        }
        h.push("</div>");
      }
      grid.innerHTML = h.join("");
      els = Array.prototype.slice.call(grid.querySelectorAll(".c"));
      overflowText();
      deco = [];
      select(st.a, st.f, false);
    }

    // Text runs on into empty cells to its right; numbers too wide for their column show ####.
    function overflowText() {
      var wide = [];
      for (var r = 1; r <= Math.min(L.nr, sh.rows.length); r++) {
        for (var c = 1; c <= Math.min(L.nc, sh.cols.length); c++) {
          var node = el(r, c);
          if (!node.textContent || node.classList.contains("hr") || node.classList.contains("hc")) {
            if (node.textContent && node.classList.contains("hr")) wide.push(node);
            continue;
          }
          if (node.scrollWidth > node.clientWidth + 1) wide.push(node);
        }
      }
      wide.forEach(function (node) {
        var r = Number(node.getAttribute("data-r")), c = Number(node.getAttribute("data-c"));
        if (node.classList.contains("hr")) {
          if (node.scrollWidth > node.clientWidth + 1 && view(r, c).kind === "n") {
            node.textContent = new Array(Math.max(2, Math.floor((node.clientWidth - 6) / 7.4)) + 1).join("#");
          }
          return;
        }
        var need = node.scrollWidth - node.clientWidth, cc = c + 1, covered = [];
        var stop = c <= L.fc ? L.fc : L.nc;  // text never runs across the frozen-pane split
        while (need > 0 && cc <= stop) {
          var next = el(r, cc);
          if (next.textContent) break;
          covered.push(next);
          need -= L.cols[cc - 1];
          cc++;
        }
        if (!covered.length) return;
        node.classList.add("ovf");
        covered.forEach(function (n, i) { if (i < covered.length - 1) n.classList.add("cov"); });
      });
    }

    // ---------- selection ----------
    function rect() {
      return { r1: Math.min(st.a.r, st.f.r), r2: Math.max(st.a.r, st.f.r), c1: Math.min(st.a.c, st.f.c), c2: Math.max(st.a.c, st.f.c) };
    }
    function edges(r, c, R, color, width) {
      var w = width || 2, out = [];
      if (r === R.r1) out.push("inset 0 " + w + "px 0 " + color);
      if (r === R.r2) out.push("inset 0 -" + w + "px 0 " + color);
      if (c === R.c1) out.push("inset " + w + "px 0 0 " + color);
      if (c === R.c2) out.push("inset -" + w + "px 0 0 " + color);
      return out;
    }
    function clearDeco() {
      deco.forEach(function (n) {
        n.classList.remove("inr", "act", "hdl", "on", "full", "edt");
        n.style.boxShadow = "";
        n.removeAttribute("aria-selected");
        var ed = n.querySelector(".xed");
        if (ed) ed.remove();
      });
      deco = [];
      ["xl-dv", "xl-list", "xl-tip"].forEach(function (id) { var n = $(id); if (n) n.remove(); });
    }
    function clamp(p) {
      return { r: Math.max(1, Math.min(L.nr, p.r)), c: Math.max(1, Math.min(L.nc, p.c)) };
    }

    function select(a, f, scrollIt) {
      st.a = clamp(a || parseAddr(sh.start));
      st.f = clamp(f || st.a);
      st.memo[st.sheet] = { a: st.a, f: st.f };
      clearDeco();
      var R = rect(), sel = getComputedStyle(root).getPropertyValue("--xl-sel").trim() || "#0F6E56";
      var single = R.r1 === R.r2 && R.c1 === R.c2;
      var shadows = {};
      var refs = st.editing ? precedents() : [];
      for (var r = R.r1; r <= R.r2; r++) {
        for (var c = R.c1; c <= R.c2; c++) {
          var n = el(r, c);
          if (!single && !(r === st.a.r && c === st.a.c)) n.classList.add("inr");
          shadows[r + ":" + c] = edges(r, c, R, sel, 2);
          deco.push(n);
        }
      }
      refs.forEach(function (ref) {
        for (var r = ref.r1; r <= Math.min(ref.r2, L.nr); r++) {
          for (var c = ref.c1; c <= Math.min(ref.c2, L.nc); c++) {
            var k = r + ":" + c;
            shadows[k] = (shadows[k] || []).concat(edges(r, c, ref, "var(--ref" + ref.color + ")", 2));
            deco.push(el(r, c));
          }
        }
      });
      Object.keys(shadows).forEach(function (k) {
        var rc = k.split(":"), n = el(Number(rc[0]), Number(rc[1]));
        n.style.boxShadow = shadows[k].join(",");
      });
      var act = el(st.a.r, st.a.c);
      act.classList.add("act");
      act.setAttribute("aria-selected", "true");
      el(R.r2, R.c2).classList.add("hdl");
      grid.setAttribute("aria-activedescendant", act.id);
      var full = { rows: R.r1 === 1 && R.r2 === L.nr, cols: R.c1 === 1 && R.c2 === L.nc };
      grid.querySelectorAll(".hd[data-col]").forEach(function (hd) {
        var c = Number(hd.getAttribute("data-col"));
        if (c >= R.c1 && c <= R.c2) { hd.classList.add("on"); if (full.rows) hd.classList.add("full"); deco.push(hd); }
      });
      grid.querySelectorAll(".rh").forEach(function (rh) {
        var r = Number(rh.getAttribute("data-row"));
        if (r >= R.r1 && r <= R.r2) { rh.classList.add("on"); if (full.cols) rh.classList.add("full"); deco.push(rh); }
      });
      if (st.editing) {
        act.classList.add("edt");
        var ed = document.createElement("span");
        ed.className = "xed";
        ed.innerHTML = formulaHtml(false);
        act.appendChild(ed);
      }
      nameBox.value = st.drag && !single ? (R.r2 - R.r1 + 1) + "R x " + (R.c2 - R.c1 + 1) + "C" : addr(st.a.r, st.a.c);
      fbar.innerHTML = formulaHtml(st.editing);
      fbtns.classList.toggle("edit", st.editing);
      if (!msgTimer) modeEl.textContent = st.editing ? "Edit" : "Ready";
      ribbon(view(st.a.r, st.a.c));
      stats(R);
      validation();
      if (scrollIt) reveal(st.f);
    }

    function reveal(p) {
      var fw = L.x[L.fc] , fh = L.y[L.fr];
      if (p.c > L.fc) {
        var left = L.x[p.c - 1], right = L.x[p.c];
        if (left < scroller.scrollLeft + fw) scroller.scrollLeft = left - fw;
        else if (right > scroller.scrollLeft + scroller.clientWidth) scroller.scrollLeft = right - scroller.clientWidth;
      }
      if (p.r > L.fr) {
        var top = L.y[p.r - 1], bottom = L.y[p.r];
        if (top < scroller.scrollTop + fh) scroller.scrollTop = top - fh;
        else if (bottom > scroller.scrollTop + scroller.clientHeight) scroller.scrollTop = bottom - scroller.clientHeight;
      }
    }

    // ---------- formula bar and precedents ----------
    var REF_RE = /^(?:('(?:[^']|'')+'|[A-Za-z_][A-Za-z0-9_.]*)!)?(\$?[A-Z]{1,3}\$?[0-9]+(?::\$?[A-Z]{1,3}\$?[0-9]+)?)(?![A-Za-z0-9_(])/;
    function tokens(f) {
      var out = [], i = 0, plain = "";
      function flush() { if (plain) { out.push({ t: plain }); plain = ""; } }
      while (i < f.length) {
        var ch = f[i];
        if (ch === '"') {
          var j = f.indexOf('"', i + 1);
          if (j < 0) j = f.length - 1;
          plain += f.slice(i, j + 1); i = j + 1; continue;
        }
        var prev = i ? f[i - 1] : "";
        if (!/[A-Za-z0-9_.$']/.test(prev)) {
          var m = REF_RE.exec(f.slice(i));
          if (m) {
            flush();
            out.push({ t: m[0], sheet: m[1] ? m[1].replace(/^'|'$/g, "").replace(/''/g, "'") : null, ref: m[2].replace(/\$/g, "") });
            i += m[0].length; continue;
          }
        }
        plain += ch; i++;
      }
      flush();
      var colors = {}, k = 0;
      out.forEach(function (t) {
        if (!t.ref) return;
        var key = (t.sheet || sh.name) + "!" + t.ref;
        if (!(key in colors)) colors[key] = k++ % REF_COLORS;
        t.color = colors[key];
      });
      return out;
    }
    function activeFormula() { var e = cellEntry(st.a.r, st.a.c); return e && e.length > 2 ? e[2] : null; }
    function barValue() {
      var e = cellEntry(st.a.r, st.a.c), v = rawValue(e);
      if (v === null || v === undefined) return "";
      if (typeof v === "number") return fmtOf(e).indexOf("%") !== -1 ? general(Math.round(v * 1e10) / 1e8) + "%" : general(v);
      if (typeof v === "boolean") return v ? "TRUE" : "FALSE";
      return String(v);
    }
    function formulaHtml(colored) {
      var f = activeFormula();
      if (!f) return esc(barValue());
      if (!colored) return esc(f);
      return tokens(f).map(function (t) {
        if (!t.ref) return esc(t.t);
        var target = (t.sheet || sh.name) + "!" + t.ref;
        return '<a class="r' + t.color + '" data-go="' + esc(target) + '" title="Go to ' + esc(target) + '">' + esc(t.t) + "</a>";
      }).join("");
    }
    function precedents() {
      var f = activeFormula();
      if (!f) return [];
      var out = [];
      tokens(f).forEach(function (t) {
        if (!t.ref || (t.sheet && t.sheet !== sh.name)) return;
        var parts = t.ref.split(":"), p1 = parseAddr(parts[0]), p2 = parseAddr(parts[1] || parts[0]);
        out.push({ r1: Math.min(p1.r, p2.r), r2: Math.max(p1.r, p2.r), c1: Math.min(p1.c, p2.c), c2: Math.max(p1.c, p2.c), color: t.color });
      });
      return out;
    }
    function setEditing(on) {
      if (st.editing === on) return;
      st.editing = on;
      select(st.a, st.a, false);
    }

    // ---------- ribbon, status bar, messages ----------
    var FILLS = { t: "var(--ink)", s: "var(--pine)", y: "#FFFF00" };
    var COLORS = { "in": "#0000FF", ln: "#008000", mu: "#6B7280", wh: "#FFFFFF", or: "#C55A11" };
    function ribbon(v) {
      var s = v.e ? styleOf(v.e) : {}, nf = v.e ? fmtOf(v.e) : "General";
      tools.size.textContent = s.sz ? String(s.sz) : "10";
      tools.b.classList.toggle("on", !!s.b);
      tools.i.classList.toggle("on", !!s.i);
      tools.fill.style.background = FILLS[s.fill] || "#FFFFFF";
      tools.color.style.background = COLORS[s.color] || "#000000";
      tools.al.classList.toggle("on", s.h === "left");
      tools.ac.classList.toggle("on", s.h === "center");
      tools.ar.classList.toggle("on", s.h === "right");
      tools.nf.textContent = nf === "General" ? "General" : nf === "0" ? "Number" : nf === "@" ? "Text" : "Custom";
    }
    function stats(R) {
      if (R.r1 === R.r2 && R.c1 === R.c2) { statsEl.textContent = ""; return; }
      var count = 0, nums = 0, sum = 0, fmt = null;
      for (var r = R.r1; r <= Math.min(R.r2, sh.rows.length); r++) {
        for (var c = R.c1; c <= Math.min(R.c2, sh.cols.length); c++) {
          var e = cellEntry(r, c), v = rawValue(e);
          if (v === null || v === undefined || v === "") continue;
          count++;
          if (typeof v === "number") { nums++; sum += v; if (!fmt) fmt = fmtOf(e); }
        }
      }
      var actFmt = fmtOf(cellEntry(st.a.r, st.a.c));
      if (cellEntry(st.a.r, st.a.c) && typeof rawValue(cellEntry(st.a.r, st.a.c)) === "number") fmt = actFmt;
      var out = [];
      if (nums) out.push("Average: " + formatValue(sum / nums, fmt || "General")[0]);
      if (count > 1 || nums) out.push("Count: " + count);
      if (nums) out.push("Sum: " + formatValue(sum, fmt || "General")[0]);
      statsEl.innerHTML = out.map(function (s) { return "<span>" + esc(s) + "</span>"; }).join("");
    }
    function say(text) {
      modeEl.textContent = text;
      clearTimeout(msgTimer);
      msgTimer = setTimeout(function () { msgTimer = null; modeEl.textContent = st.editing ? "Edit" : "Ready"; }, 3200);
    }

    // ---------- the scenario list (data validation on Dashboard!B4) ----------
    function listAt() { return sh.lists[addr(st.a.r, st.a.c)] || null; }
    function validation() {
      var dv = listAt();
      if (!dv || st.editing || st.a.r !== st.f.r || st.a.c !== st.f.c) return;
      var x = L.x[st.a.c], y = L.y[st.a.r - 1], h = L.rows[st.a.r - 1];
      var btn = document.createElement("button");
      btn.type = "button"; btn.id = "xl-dv"; btn.className = "xl__dv"; btn.tabIndex = -1;
      btn.setAttribute("aria-label", "Choose the scenario: 1 Low, 2 Base, 3 High");
      btn.setAttribute("aria-haspopup", "listbox");
      btn.setAttribute("aria-expanded", st.list ? "true" : "false");
      btn.style.left = x + "px"; btn.style.top = y + "px"; btn.style.height = h + "px";
      grid.appendChild(btn);
      if (st.list) {
        var ul = document.createElement("ul");
        ul.id = "xl-list"; ul.className = "xl__list"; ul.setAttribute("role", "listbox");
        ul.setAttribute("aria-label", "Scenario");
        ul.style.left = L.x[st.a.c - 1] + "px"; ul.style.top = (y + h) + "px";
        ul.style.minWidth = (L.cols[st.a.c - 1] + 17) + "px";
        dv.options.forEach(function (o) {
          var li = document.createElement("li");
          li.setAttribute("role", "option");
          li.setAttribute("data-v", o);
          li.id = "xl-opt-" + o;
          li.setAttribute("aria-selected", String(Number(o) === st.listPick));
          li.textContent = o;
          ul.appendChild(li);
        });
        grid.appendChild(ul);
        grid.setAttribute("aria-activedescendant", "xl-opt-" + st.listPick);
      } else if (dv.prompt) {
        var tip = document.createElement("div");
        tip.id = "xl-tip"; tip.className = "xl__tip"; tip.setAttribute("role", "note");
        tip.innerHTML = (dv.title ? "<strong>" + esc(dv.title) + "</strong>" : "") + esc(dv.prompt);
        // like a message the user has dragged aside: next to the used columns, so it hides no numbers
        tip.style.left = (Math.max(L.x[st.a.c] + 24, L.x[sh.cols.length] + 14)) + "px"; tip.style.top = (y - 4) + "px";
        grid.appendChild(tip);
      }
    }
    function openList(on) {
      st.list = on;
      st.listPick = Number(rawValue(cellEntry(st.a.r, st.a.c))) || st.kase;
      select(st.a, st.f, false);
    }
    function setCase(n) {
      n = Number(n);
      if (!(n >= 1 && n <= 3)) return;
      var keep = { a: st.a, f: st.f };
      st.list = false;
      st.kase = n;
      // B4 holds the scenario number: the preview writes it into the cell and recalculates every sheet
      var e = sh.cells[addr(keep.a.r, keep.a.c)];
      if (e) e[1] = n;
      wb.sheets[0].cells.B4[1] = n;
      render();
      select(keep.a, keep.f, false);
      say("Calculating... done. Scenario " + n + " (" + ["Low", "Base", "High"][n - 1] + ")");
      grid.focus({ preventScroll: true });
    }

    // ---------- sheets ----------
    function showSheet(i, focusTab, target) {
      st.editing = false; st.list = false;
      st.sheet = i;
      sh = wb.sheets[i];
      tabs.forEach(function (b, j) {
        b.setAttribute("aria-selected", j === i ? "true" : "false");
        b.tabIndex = j === i ? 0 : -1;
        if (j === i && focusTab) b.focus();
      });
      var memo = st.memo[i];
      st.a = target ? target.a : memo ? memo.a : parseAddr(sh.start);
      st.f = target ? target.f : memo ? memo.f : st.a;
      scroller.scrollTop = 0; scroller.scrollLeft = 0;
      render();
      reveal(st.f);
    }
    function go(text) {
      var m = /^(?:'?(.+?)'?!)?(\$?[A-Z]{1,3}\$?\d+)(?::(\$?[A-Z]{1,3}\$?\d+))?$/i.exec(String(text).trim());
      if (!m) { say("Reference isn't valid: " + text); return false; }
      var idx = st.sheet;
      if (m[1]) {
        idx = -1;
        wb.sheets.forEach(function (s, j) { if (s.name.toLowerCase() === m[1].toLowerCase()) idx = j; });
        if (idx < 0) { say("No sheet named " + m[1]); return false; }
      }
      var a = parseAddr(m[2]), f = m[3] ? parseAddr(m[3]) : a;
      if (idx !== st.sheet) showSheet(idx, false, { a: a, f: f });
      else { st.editing = false; select(a, f, true); }
      grid.focus({ preventScroll: true });
      return true;
    }

    // ---------- keyboard ----------
    function hasValue(r, c) { var v = rawValue(cellEntry(r, c)); return v !== null && v !== undefined && v !== ""; }
    function jump(p, dr, dc) {
      var lastR = sh.rows.length, lastC = sh.cols.length;
      var r = p.r, c = p.c;
      function inside(r2, c2) { return r2 >= 1 && c2 >= 1 && r2 <= Math.max(lastR, 1) && c2 <= Math.max(lastC, 1); }
      if (!inside(r + dr, c + dc)) return clamp({ r: dr ? (dr > 0 ? L.nr : 1) : r, c: dc ? (dc > 0 ? L.nc : 1) : c });
      if (hasValue(r, c) && hasValue(r + dr, c + dc)) {
        while (inside(r + dr, c + dc) && hasValue(r + dr, c + dc)) { r += dr; c += dc; }
        return { r: r, c: c };
      }
      r += dr; c += dc;
      while (inside(r, c) && !hasValue(r, c)) { r += dr; c += dc; }
      if (!inside(r, c)) return clamp({ r: dr ? (dr > 0 ? L.nr : 1) : r, c: dc ? (dc > 0 ? L.nc : 1) : c });
      return { r: r, c: c };
    }
    grid.addEventListener("keydown", function (e) {
      if (!wb) return;
      var k = e.key, ctrl = e.ctrlKey || e.metaKey;
      if (st.list) {
        if (k === "ArrowDown" || k === "ArrowUp") { e.preventDefault(); st.listPick = Math.max(1, Math.min(3, st.listPick + (k === "ArrowDown" ? 1 : -1))); select(st.a, st.f, false); return; }
        if (k === "Enter") { e.preventDefault(); setCase(st.listPick); return; }
        if (k === "Escape" || k === "Tab") { if (k === "Escape") e.preventDefault(); openList(false); return; }
      }
      var moves = { ArrowUp: [-1, 0], ArrowDown: [1, 0], ArrowLeft: [0, -1], ArrowRight: [0, 1] };
      if (moves[k] && e.altKey && k === "ArrowDown" && listAt()) { e.preventDefault(); openList(true); return; }
      if (moves[k]) {
        e.preventDefault();
        st.editing = false;
        var from = e.shiftKey ? st.f : st.a, d = moves[k];
        var to = ctrl ? jump(from, d[0], d[1]) : clamp({ r: from.r + d[0], c: from.c + d[1] });
        if (e.shiftKey) select(st.a, to, true); else select(to, to, true);
        return;
      }
      if (k === "Enter") {
        e.preventDefault();
        st.editing = false;
        var to2 = clamp({ r: st.a.r + (e.shiftKey ? -1 : 1), c: st.a.c });
        select(to2, to2, true);
        return;
      }
      if (k === "PageDown" || k === "PageUp") {
        e.preventDefault();
        if (ctrl) { showSheet((st.sheet + (k === "PageDown" ? 1 : wb.sheets.length - 1)) % wb.sheets.length, false); return; }
        var step = Math.max(5, Math.floor(scroller.clientHeight / 20) - 2) * (k === "PageDown" ? 1 : -1);
        var to3 = clamp({ r: st.a.r + step, c: st.a.c });
        select(to3, to3, true);
        return;
      }
      if (k === "Home") {
        e.preventDefault();
        var to4 = ctrl ? { r: 1, c: 1 } : { r: st.a.r, c: 1 };
        select(to4, to4, true);
        return;
      }
      if (k === "End" && ctrl) {
        e.preventDefault();
        var to5 = { r: sh.rows.length, c: sh.cols.length };
        select(to5, to5, true);
        return;
      }
      if (k === "F2") { e.preventDefault(); setEditing(!st.editing); return; }
      if (k === "Escape") { if (st.editing) { e.preventDefault(); setEditing(false); } return; }
      if (ctrl && (k === "a" || k === "A")) { e.preventDefault(); select({ r: 1, c: 1 }, { r: L.nr, c: L.nc }, false); return; }
      if (ctrl && (k === "c" || k === "C")) { copy(); e.preventDefault(); return; }
      if (!ctrl && !e.altKey && listAt() && /^[1-3]$/.test(k)) { e.preventDefault(); setCase(k); return; }
      if (!ctrl && !e.altKey && k.length === 1 && k !== " ") {
        say(listAt() ? "Type 1, 2 or 3 here, or open the list" : "Read-only preview. Change the scenario in Dashboard!B4");
      }
    });
    function copy() {
      var R = rect(), lines = [];
      for (var r = R.r1; r <= R.r2; r++) {
        var row = [];
        for (var c = R.c1; c <= R.c2; c++) row.push(view(r, c).text);
        lines.push(row.join("\t"));
      }
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(lines.join("\n")).then(function () { say("Copied " + (R.r2 - R.r1 + 1) * (R.c2 - R.c1 + 1) + " cells"); }, function () {});
      }
    }

    // ---------- mouse ----------
    function pointAt(target) {
      var cell = target.closest && target.closest(".c");
      return cell ? { r: Number(cell.getAttribute("data-r")), c: Number(cell.getAttribute("data-c")) } : null;
    }
    grid.addEventListener("mousedown", function (e) {
      if (!wb || e.button !== 0) return;
      if (e.target.closest("#xl-dv")) { e.preventDefault(); openList(!st.list); grid.focus({ preventScroll: true }); return; }
      var li = e.target.closest("#xl-list li");
      if (li) { e.preventDefault(); setCase(li.getAttribute("data-v")); return; }
      var hd = e.target.closest(".hd"), rh = e.target.closest(".rh");
      st.list = false;
      if (hd || rh) {
        e.preventDefault();
        st.editing = false;
        if (hd && hd.classList.contains("hd--corner")) { select({ r: 1, c: 1 }, { r: L.nr, c: L.nc }, false); }
        else if (hd) {
          var c = Number(hd.getAttribute("data-col"));
          if (e.shiftKey) select({ r: 1, c: st.a.c }, { r: L.nr, c: c }, false);
          else select({ r: 1, c: c }, { r: L.nr, c: c }, false);
        } else {
          var r = Number(rh.getAttribute("data-row"));
          if (e.shiftKey) select({ r: st.a.r, c: 1 }, { r: r, c: L.nc }, false);
          else select({ r: r, c: 1 }, { r: r, c: L.nc }, false);
        }
        grid.focus({ preventScroll: true });
        return;
      }
      var p = pointAt(e.target);
      if (!p) return;
      e.preventDefault();
      grid.focus({ preventScroll: true });
      if (st.editing && p.r === st.a.r && p.c === st.a.c) return;
      st.editing = false;
      if (e.shiftKey) { select(st.a, p, false); return; }
      st.drag = true;
      select(p, p, false);
    });
    grid.addEventListener("mouseover", function (e) {
      if (!st.drag) return;
      if (!(e.buttons & 1)) { st.drag = false; return; }
      var p = pointAt(e.target);
      if (p && (p.r !== st.f.r || p.c !== st.f.c)) select(st.a, p, false);
    });
    document.addEventListener("mouseup", function () {
      if (st.drag) { st.drag = false; if (wb) select(st.a, st.f, false); }
    });
    grid.addEventListener("dblclick", function (e) {
      if (!wb || e.target.closest("#xl-list, #xl-dv")) return;
      var p = pointAt(e.target);
      if (!p) return;
      st.a = p; st.f = p;
      if (listAt()) { openList(true); return; }
      setEditing(true);
    });
    fbar.addEventListener("click", function (e) {
      if (!wb) return;
      var link = e.target.closest("a[data-go]");
      if (link) { go(link.getAttribute("data-go")); return; }
      if (!st.editing) setEditing(true);
    });
    fexp.addEventListener("click", function () {
      var open = !fbar.classList.contains("is-open");
      fbar.classList.toggle("is-open", open);
      fexp.setAttribute("aria-expanded", String(open));
    });
    document.getElementById("xl-cancel").addEventListener("click", function () { if (st.editing) setEditing(false); });
    document.getElementById("xl-enter").addEventListener("click", function () { if (st.editing) setEditing(false); });
    nameBox.addEventListener("focus", function () { nameBox.select(); });
    nameBox.addEventListener("keydown", function (e) {
      if (e.key === "Enter") { e.preventDefault(); if (wb) go(nameBox.value); }
      if (e.key === "Escape") { e.preventDefault(); nameBox.value = addr(st.a.r, st.a.c); grid.focus({ preventScroll: true }); }
    });
    nameBox.addEventListener("blur", function () { if (wb) nameBox.value = addr(st.a.r, st.a.c); });
    document.addEventListener("mousedown", function (e) {
      if (!wb || !e.target.isConnected || root.contains(e.target)) return;
      if (st.editing || st.list) { st.editing = false; st.list = false; select(st.a, st.f, false); }
    });

    tabs.forEach(function (b, i) {
      b.addEventListener("click", function () { if (wb && i !== st.sheet) showSheet(i, false); });
      b.addEventListener("keydown", function (e) {
        var j = e.key === "ArrowRight" ? i + 1 : e.key === "ArrowLeft" ? i - 1 : e.key === "Home" ? 0 : e.key === "End" ? tabs.length - 1 : null;
        if (j === null || !wb) return;
        e.preventDefault();
        showSheet((j + tabs.length) % tabs.length, true);
      });
    });

    // ---------- load ----------
    fetch(root.getAttribute("data-src"), { credentials: "same-origin" })
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(function (data) {
        wb = data;
        sh = wb.sheets[0];
        st.a = parseAddr(sh.start); st.f = st.a;
        render();
        root.classList.add("is-live");
      })
      .catch(function () { modeEl.textContent = "Preview could not load; the sample file below has the same workbook."; });
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

  var xl = document.getElementById("xl");
  if (xl) initSheet(xl);
  initDemo(readJson("demo-data"));
})();
