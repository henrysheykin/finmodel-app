// Runs web/static/calc.js on the cases the parity test sends (JSON on stdin) and prints the results as JSON.
// Used by tests/test_calculators.py; nothing here is shipped.
"use strict";
const path = require("path");
const calc = require(path.join(__dirname, "..", "..", "web", "static", "calc.js"));

function safe(fn) {
  try { return { v: fn() }; } catch (e) { return { error: true }; }
}

let input = "";
process.stdin.setEncoding("utf8");
process.stdin.on("data", (d) => { input += d; });
process.stdin.on("end", () => {
  const job = JSON.parse(input);
  const out = { exprs: [], formats: [], specs: [] };
  for (const c of job.exprs) {
    out.exprs.push(safe(() => calc.evaluate(calc.parse(c.src), c.env)));
  }
  for (const c of job.formats) out.formats.push(calc.formatValue(c.v, c.fmt));
  for (const s of job.specs) {
    const p = calc.prepare(s.spec);
    const cases = s.cases.map((values) => {
      const outputs = calc.compute(p, values);
      const rows = calc.sweep(p, values).map((r) => ({ value: r.value, outputs: Object.assign({}, r.outputs) }));
      const formatted = {};
      for (const o of s.spec.outputs) formatted[o.key] = calc.formatValue(outputs[o.key], o.format);
      return { outputs: Object.assign({}, outputs), rows, formatted };
    });
    out.specs.push({ slug: s.slug, cases });
  }
  process.stdout.write(JSON.stringify(out));
});
