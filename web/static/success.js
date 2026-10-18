// Payment success page: poll the order until its status changes, then reload (no inline script: CSP).
(function () {
  var el = document.getElementById("status-text");
  if (!el) return;
  var done = ["ready", "failed", "refunded"];
  if (done.indexOf(el.dataset.status) >= 0) return;
  var url = "/api/orders/" + encodeURIComponent(el.dataset.order);
  var tries = 0;
  var timer = setInterval(function () {
    if (++tries > 120) { clearInterval(timer); return; }
    fetch(url).then(function (r) { return r.json(); }).then(function (o) {
      if (o.status !== el.dataset.status) { clearInterval(timer); window.location.reload(); }
    }).catch(function () {});
  }, 3000);
})();
