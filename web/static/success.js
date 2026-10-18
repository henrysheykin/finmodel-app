// Payment success page: poll the order until its status changes, then reload (no inline script: CSP).
(function () {
  var el = document.getElementById("status-text");
  if (!el) return;
  var done = ["ready", "failed", "refunded"];
  if (done.indexOf(el.dataset.status) >= 0) return;
  var url = "/api/orders/" + encodeURIComponent(el.dataset.order);
  // every 3 s for two minutes, then every 15 s for up to 30 minutes: a busy queue (one worker,
  // ~6-10 s per model) can hold a model for several minutes (E17 load test)
  var started = Date.now();
  function tick() {
    var age = Date.now() - started;
    if (age > 30 * 60 * 1000) return;
    fetch(url).then(function (r) { return r.json(); }).then(function (o) {
      if (o.status !== el.dataset.status) { window.location.reload(); return; }
      setTimeout(tick, age < 120000 ? 3000 : 15000);
    }).catch(function () { setTimeout(tick, 15000); });
  }
  setTimeout(tick, 3000);
})();
