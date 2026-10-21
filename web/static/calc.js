// Calculator pages (ADR-014, E34): a small, safe formula evaluator and the live page behaviour.
// JavaScript twin of app/calc_expr.py and app/calculators.py: the two must give the same results on every
// formula and example (tests/test_calculators.py runs both on the same cases). There is no eval and no
// Function constructor: a formula is tokenised, parsed to a tree and walked.
// Loaded in the browser it wires up every [data-calc] block; loaded by Node (the tests) it exports the pure parts.
(function (root) {
  "use strict";

  var MAX_LENGTH = 500, MAX_DEPTH = 40;
  var FUNCTIONS = { min: [2, Infinity], max: [2, Infinity], round: [1, 2], abs: [1, 1], "if": [3, 3] };
  var ALIAS = { "×": "*", "÷": "/", "−": "-" };
  var TOKEN = /[ \t\r\n]*(?:(\d+(?:\.\d+)?|\.\d+)|([a-z][a-z0-9_]*)|(<=|>=|==|!=|[-+*\/^<>(),×÷−]))/y;

  function ExprError(msg) { this.name = "ExprError"; this.message = msg; }
  ExprError.prototype = Object.create(Error.prototype);

  function tokenize(src) {
    if (src.length > MAX_LENGTH) throw new ExprError("formula too long");
    var out = [], pos = 0;
    for (;;) {
      while (pos < src.length && " \t\r\n".indexOf(src[pos]) >= 0) pos++;
      if (pos >= src.length) return out;
      TOKEN.lastIndex = pos;
      var m = TOKEN.exec(src);
      if (!m) throw new ExprError("unexpected character " + src[pos]);
      pos = TOKEN.lastIndex;
      if (m[1] !== undefined) out.push(["num", m[1]]);
      else if (m[2] !== undefined) out.push(["name", m[2]]);
      else out.push(["op", ALIAS[m[3]] || m[3]]);
    }
  }

  function parse(src) {
    var t = tokenize(src), i = 0, depth = 0;
    function peek() { return i < t.length ? t[i] : null; }
    function op() {
      var tok = peek();
      if (tok && tok[0] === "op") {
        for (var k = 0; k < arguments.length; k++) {
          if (tok[1] === arguments[k]) { i++; return tok[1]; }
        }
      }
      return null;
    }
    function expect(o) { if (!op(o)) throw new ExprError("expected " + o); }
    function comparison() {
      var node = sum(), o;
      while ((o = op("<=", ">=", "==", "!=", "<", ">")) !== null) node = ["bin", o, node, sum()];
      return node;
    }
    function sum() {
      var node = product(), o;
      while ((o = op("+", "-")) !== null) node = ["bin", o, node, product()];
      return node;
    }
    function product() {
      var node = unary(), o;
      while ((o = op("*", "/")) !== null) node = ["bin", o, node, unary()];
      return node;
    }
    function unary() {
      depth++;
      if (depth > MAX_DEPTH) throw new ExprError("formula nested too deeply");
      try {
        var o = op("-", "+");
        if (o !== null) { var inner = unary(); return o === "-" ? ["neg", inner] : inner; }
        return power();
      } finally { depth--; }
    }
    function power() {
      var node = atom();
      if (op("^")) return ["bin", "^", node, unary()];
      return node;
    }
    function atom() {
      var tok = peek();
      if (tok === null) throw new ExprError("unexpected end of formula");
      var kind = tok[0], text = tok[1];
      if (kind === "num") { i++; return ["num", parseFloat(text)]; }
      if (kind === "name") {
        i++;
        if (op("(")) {
          if (!Object.prototype.hasOwnProperty.call(FUNCTIONS, text)) throw new ExprError("unknown function " + text);
          var args = [comparison()];
          while (op(",")) args.push(comparison());
          expect(")");
          var lim = FUNCTIONS[text];
          if (args.length < lim[0] || args.length > lim[1]) throw new ExprError(text + "() has the wrong number of arguments");
          return ["call", text, args];
        }
        if (Object.prototype.hasOwnProperty.call(FUNCTIONS, text)) throw new ExprError(text + " is a function");
        return ["var", text];
      }
      if (op("(")) {
        depth++;
        if (depth > MAX_DEPTH) throw new ExprError("formula nested too deeply");
        var node = comparison();
        depth--;
        expect(")");
        return node;
      }
      throw new ExprError("unexpected " + text);
    }
    var node = comparison();
    if (peek() !== null) throw new ExprError("unexpected " + peek()[1]);
    return node;
  }

  function finite(x) { return isFinite(x) ? x : null; }

  function round(x, digits) {
    if (digits !== Math.floor(digits) || digits < 0 || digits > 9) return null;
    var m = Math.pow(10, digits), scaled = Math.abs(x) * m + 0.5;
    if (!isFinite(scaled)) return null;
    var r = Math.floor(scaled) / m;
    return x >= 0 ? r : -r;
  }

  function power(a, b) {
    if (a === 0 && b < 0) return null;
    if (a < 0 && b !== Math.floor(b)) return null;
    return finite(Math.pow(a, b));
  }

  // The value of a parsed formula; null when it cannot be computed (division by zero and the like).
  function evaluate(node, env) {
    var kind = node[0];
    if (kind === "num") return node[1];
    if (kind === "var") {
      if (!Object.prototype.hasOwnProperty.call(env, node[1])) throw new ExprError("unknown name " + node[1]);
      return env[node[1]];
    }
    if (kind === "neg") { var v = evaluate(node[1], env); return v === null ? null : -v; }
    if (kind === "bin") {
      var o = node[1], a = evaluate(node[2], env), b = evaluate(node[3], env);
      if (a === null || b === null) return null;
      switch (o) {
        case "+": return finite(a + b);
        case "-": return finite(a - b);
        case "*": return finite(a * b);
        case "/": return b === 0 ? null : finite(a / b);
        case "^": return power(a, b);
        case "<": return a < b ? 1 : 0;
        case "<=": return a <= b ? 1 : 0;
        case ">": return a > b ? 1 : 0;
        case ">=": return a >= b ? 1 : 0;
        case "==": return a === b ? 1 : 0;
        default: return a !== b ? 1 : 0;
      }
    }
    var name = node[1], args = node[2];
    if (name === "if") {
      var cond = evaluate(args[0], env);
      if (cond === null) return null;
      return evaluate(cond !== 0 ? args[1] : args[2], env);
    }
    var vals = [];
    for (var k = 0; k < args.length; k++) {
      var x = evaluate(args[k], env);
      if (x === null) return null;
      vals.push(x);
    }
    if (name === "min") return Math.min.apply(null, vals);
    if (name === "max") return Math.max.apply(null, vals);
    if (name === "abs") return Math.abs(vals[0]);
    return round(vals[0], vals.length > 1 ? vals[1] : 0);
  }

  // ---------- number formats (shared with app/calc_expr.py) ----------
  var FORMATS = {
    "int": ["", 0, ""], number1: ["", 1, ""], number2: ["", 2, ""],
    money: ["$", 0, ""], money2: ["$", 2, ""], percent: ["", 1, "%"], percent0: ["", 0, "%"], multiple: ["", 2, "x"]
  };
  var NONE_TEXT = "—";

  function formatValue(value, fmt) {
    var f = FORMATS[fmt];
    if (value === null || value === undefined || !isFinite(value) || Math.abs(value) >= 1e15) return NONE_TEXT;
    var s = Math.abs(value).toFixed(f[1]);  // exact decimal rounding, ties up: the same as the Python twin
    var parts = s.split(".");
    parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    var sign = value < 0 && parseFloat(s) !== 0 ? "-" : "";
    return sign + f[0] + parts.join(".") + f[2];
  }

  // ---------- a calculator spec (the JSON the page embeds) ----------
  function prepare(spec) {
    var asts = Object.create(null);
    spec.outputs.forEach(function (o) { asts[o.key] = parse(o.formula); });
    return { spec: spec, asts: asts };
  }

  // values: key -> number or null (null = an input that is not a valid number). Returns key -> number or null.
  function compute(p, values) {
    var env = Object.create(null), out = Object.create(null);
    p.spec.inputs.forEach(function (inp) {
      var v = values[inp.key] === undefined ? inp.default : values[inp.key];
      env[inp.key] = v === null ? null : clamp(v, inp);
    });
    p.spec.outputs.forEach(function (o) {
      var v = evaluate(p.asts[o.key], env);
      env[o.key] = v;
      out[o.key] = v;
    });
    return out;
  }

  function clamp(v, inp) { return Math.min(Math.max(v, inp.min), inp.max); }

  function inputOf(p, key) {
    for (var i = 0; i < p.spec.inputs.length; i++) if (p.spec.inputs[i].key === key) return p.spec.inputs[i];
    return null;
  }

  // The swept values of the sensitivity table for the current inputs (clamped to the input's range).
  function sweepValues(p, values) {
    var t = p.spec.table;
    if (!t) return [];
    var inp = inputOf(p, t.input);
    if (t.values) return t.values.map(function (v) { return clamp(v, inp); });
    var cur = values[t.input] === undefined ? inp.default : values[t.input];
    return t.relative.map(function (r) { return cur === null ? null : clamp(cur * (1 + r / 100), inp); });
  }

  // Rows of the sensitivity table: [{value, outputs}] with the other inputs as given.
  function sweep(p, values) {
    var t = p.spec.table;
    if (!t) return [];
    return sweepValues(p, values).map(function (sv) {
      var vals = Object.create(null);
      for (var k in values) vals[k] = values[k];
      vals[t.input] = sv;
      return { value: sv, outputs: compute(p, vals) };
    });
  }

  var api = {
    parse: parse, evaluate: evaluate, formatValue: formatValue, prepare: prepare, compute: compute,
    sweep: sweep, ExprError: ExprError
  };
  if (typeof module !== "undefined" && module.exports) { module.exports = api; return; }
  root.StartupCalc = api;

  // ---------- the page ----------
  function init(box) {
    var specEl = box.querySelector("script[data-calc-spec]");
    if (!specEl) return;
    var p = prepare(JSON.parse(specEl.textContent));
    var spec = p.spec;
    var byKey = {};
    spec.inputs.forEach(function (inp) { byKey[inp.key] = inp; });
    var fields = {};
    box.querySelectorAll("input[data-key]").forEach(function (el) { fields[el.getAttribute("data-key")] = el; });
    var live = box.querySelector("[data-live]");
    var liveTimer = null;

    function read() {
      var values = {}, ok = true;
      spec.inputs.forEach(function (inp) {
        var el = fields[inp.key], msg = box.querySelector('[data-msg="' + inp.key + '"]');
        var raw = el.value.trim(), n = raw === "" ? NaN : Number(raw);
        var valid = isFinite(n), range = formatValue(inp.min, inp.format) + " to " + formatValue(inp.max, inp.format);
        values[inp.key] = valid ? n : null;
        if (!valid) ok = false;
        el.setAttribute("aria-invalid", valid ? "false" : "true");
        if (msg) {
          var bad = !valid || n < inp.min || n > inp.max;
          if (!valid) msg.textContent = "Enter a number from " + range + ".";
          else if (bad) msg.textContent = "Calculated with " + formatValue(clamp(n, inp), inp.format) + ": the range is " + range + ".";
          else msg.textContent = msg.getAttribute("data-hint") || "";
          msg.classList.toggle("is-error", bad);
        }
      });
      return { values: values, ok: ok };
    }

    function render() {
      var r = read(), out = compute(p, r.values);
      spec.outputs.forEach(function (o) {
        var el = box.querySelector('[data-out="' + o.key + '"]');
        if (el) el.textContent = formatValue(out[o.key], o.format);
      });
      if (spec.table) {
        var rows = sweep(p, r.values), tIn = byKey[spec.table.input];
        rows.forEach(function (row, i) {
          var tr = box.querySelector('tr[data-row="' + i + '"]');
          if (!tr) return;
          tr.querySelector("[data-sweep]").textContent = formatValue(row.value, tIn.format);
          spec.table.outputs.forEach(function (key) {
            var cell = tr.querySelector('[data-cell="' + key + '"]');
            if (cell) cell.textContent = formatValue(row.outputs[key], outFormat(key));
          });
        });
      }
      if (live) {
        clearTimeout(liveTimer);
        liveTimer = setTimeout(function () {
          var hi = spec.outputs.filter(function (o) { return o.highlight; })[0] || spec.outputs[0];
          live.textContent = hi ? hi.label + ": " + formatValue(out[hi.key], hi.format) : "";
        }, 500);
      }
    }

    function outFormat(key) {
      for (var i = 0; i < spec.outputs.length; i++) if (spec.outputs[i].key === key) return spec.outputs[i].format;
      return "number2";
    }

    box.addEventListener("input", function (e) {
      if (e.target && e.target.hasAttribute && e.target.hasAttribute("data-key")) render();
    });
    render();
    box.classList.add("is-live");
  }

  if (typeof document !== "undefined") {
    var start = function () { document.querySelectorAll("[data-calc]").forEach(init); };
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start);
    else start();
  }
})(typeof window !== "undefined" ? window : this);
