// Wizard: one step at a time, live order summary, key numbers per business type.
// Progressive enhancement: without JavaScript the form shows every step and still submits.
(function () {
  "use strict";
  var form = document.getElementById("wizard");
  if (!form) return;
  var data = JSON.parse(document.getElementById("wizard-data").textContent);
  var steps = Array.prototype.slice.call(form.querySelectorAll(".step"));
  var labels = Array.prototype.slice.call(form.querySelectorAll("[data-step-label]"));
  var nav = form.querySelector(".nav");
  var prev = form.querySelector("[data-prev]");
  var next = form.querySelector("[data-next]");
  var kn = document.getElementById("key-numbers");
  var current = Math.min(Math.max(data.start_step || 1, 1), steps.length);

  form.classList.add("js");
  nav.hidden = false;

  function val(name) {
    var el = form.querySelector('[name="' + name + '"]:checked') || form.querySelector('[name="' + name + '"]:not([type=radio])');
    return el ? el.value : "";
  }
  function money(cents) { return "$" + Math.round(cents / 100).toLocaleString("en-US"); }

  function stepError(step, text) {
    var box = step.querySelector(".step-error");
    if (!text) { if (box) box.remove(); return; }
    if (!box) {
      box = document.createElement("p");
      box.className = "errors step-error";
      box.setAttribute("role", "alert");
      step.insertBefore(box, step.children[1]);
    }
    box.textContent = text;
  }

  function validate(n) {
    var step = steps[n - 1];
    var groups = {};
    step.querySelectorAll("input[type=radio][required]").forEach(function (r) { groups[r.name] = true; });
    for (var name in groups) {
      if (!val(name)) { stepError(step, "Choose one option to continue."); return false; }
    }
    if (n === 1 && data.available.indexOf(val("business_type")) < 0) {
      stepError(step, "This business type is not available yet. Choose another one."); return false;
    }
    if (n === 7) {
      var email = form.querySelector("#email").value.trim();
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) { stepError(step, "Enter a valid email address."); return false; }
    }
    stepError(step, "");
    return true;
  }

  function show(n, focus) {
    current = n;
    steps.forEach(function (s, i) { s.hidden = i !== n - 1; });
    labels.forEach(function (l, i) {
      if (i === n - 1) l.setAttribute("aria-current", "step"); else l.removeAttribute("aria-current");
      l.classList.toggle("done", i < n - 1);
    });
    prev.hidden = n === 1;
    next.hidden = n === steps.length;
    if (focus) {
      var h = steps[n - 1].querySelector("h2");
      h.setAttribute("tabindex", "-1");
      h.focus();
    }
  }

  function summary() {
    var set = function (k, v) { var el = document.querySelector('[data-sum="' + k + '"]'); if (el) el.textContent = v || "—"; };
    var bt = val("business_type"), name = form.querySelector("#business_name").value.trim();
    set("business_type", name || data.labels.business_type[bt]);
    set("goal", data.labels.goal[val("goal")]);
    set("stage", data.labels.stage[val("stage")]);
    var y = val("horizon_years");
    set("period", y ? y + (y === "1" ? " year, " : " years, ") + (data.labels.granularity[val("granularity")] || "").toLowerCase() : "");
    var tier = val("tier");
    set("tier", data.labels.tier[tier]);
    set("price", tier ? money(data.prices[tier]) : "");
  }

  function syncSample() {
    var off = form.querySelector('[name="sample_data"]').checked;
    kn.classList.toggle("is-off", off);
    kn.querySelectorAll("input").forEach(function (i) { i.disabled = off; });
  }

  var loaded = "";
  function loadKeyNumbers() {
    var bt = val("business_type"), stage = val("stage");
    var key = bt + "|" + stage;
    if (!bt || key === loaded) return;
    loaded = key;
    var typed = {};
    kn.querySelectorAll("input").forEach(function (i) { if (i.dataset.touched) typed[i.name] = i.value; });
    fetch(kn.dataset.endpoint + "?business_type=" + encodeURIComponent(bt) + "&stage=" + encodeURIComponent(stage))
      .then(function (r) { return r.json(); })
      .then(function (res) {
        kn.textContent = "";
        if (!res.available) {
          var p = document.createElement("p"); p.className = "hint";
          p.textContent = "This business type is not available yet."; kn.appendChild(p); return;
        }
        res.fields.forEach(function (f) {
          var row = document.createElement("div"); row.className = "field kn__row";
          var lab = document.createElement("label"); lab.htmlFor = "kn_" + f.key; lab.textContent = f.label;
          var wrap = document.createElement("div"); wrap.className = "kn__input";
          var inp = document.createElement("input");
          inp.type = "text"; inp.inputMode = "decimal"; inp.id = "kn_" + f.key; inp.name = "kn_" + f.key;
          inp.value = typed[inp.name] !== undefined ? typed[inp.name] : String(f.default);
          if (typed[inp.name] !== undefined) inp.dataset.touched = "1";
          inp.addEventListener("input", function () { inp.dataset.touched = "1"; });
          var unit = document.createElement("span"); unit.className = "unit"; unit.textContent = f.unit;
          wrap.appendChild(inp); wrap.appendChild(unit); row.appendChild(lab); row.appendChild(wrap); kn.appendChild(row);
        });
        syncSample();
      })
      .catch(function () { loaded = ""; });
  }

  prev.addEventListener("click", function () { if (current > 1) show(current - 1, true); });
  next.addEventListener("click", function () {
    if (!validate(current)) return;
    if (current === 4) loadKeyNumbers();
    if (current < steps.length) show(current + 1, true);
  });
  form.addEventListener("change", function (e) {
    summary();
    if (e.target.name === "sample_data") syncSample();
    if (e.target.name === "business_type" || e.target.name === "stage") loadKeyNumbers();
  });
  form.addEventListener("input", summary);
  form.addEventListener("submit", function (e) {
    for (var i = 1; i <= steps.length; i++) {
      if (!validate(i)) { e.preventDefault(); show(i, true); return; }
    }
  });
  form.addEventListener("keydown", function (e) {
    // Enter in a text field moves to the next step instead of submitting early.
    if (e.key === "Enter" && e.target.tagName === "INPUT" && e.target.type !== "submit" && current < steps.length) {
      e.preventDefault(); next.click();
    }
  });

  summary();
  syncSample();
  if (kn.querySelector("input")) {
    // server already rendered the fields for the chosen type and stage (e.g. after an error): keep them
    loaded = val("business_type") + "|" + val("stage");
    kn.querySelectorAll("input").forEach(function (i) {
      i.dataset.touched = "1";
      i.addEventListener("input", function () { i.dataset.touched = "1"; });
    });
  } else if (val("business_type")) {
    loadKeyNumbers();
  }
  show(current, data.start_step > 1);
  var errs = document.getElementById("errors");
  if (errs) errs.focus();
})();
