/* Recently Read — works with Material instant navigation */
(function () {
  var MAX = 6;
  var KEY = "muz_recent_pages";

  function track() {
    var url = window.location.pathname;
    var title = document.title.replace(/ - MuzOps Learning Zone$/, "").trim();
    var pages = JSON.parse(localStorage.getItem(KEY) || "[]");
    pages = pages.filter(function (p) { return p.url !== url; });
    pages.unshift({ url: url, title: title, time: Date.now() });
    pages = pages.slice(0, MAX);
    localStorage.setItem(KEY, JSON.stringify(pages));
  }

  function render() {
    var container = document.getElementById("recent-pages");
    if (!container) return;

    var current = window.location.pathname;
    var pages = JSON.parse(localStorage.getItem(KEY) || "[]");
    var others = pages.filter(function (p) { return p.url !== current; });

    if (others.length === 0) {
      container.innerHTML = "<p><em>Visit a few pages — your history will appear here.</em></p>";
      return;
    }

    var items = others.map(function (p) {
      return '<div class="recent-card"><a href="' + p.url + '">'
        + '<span class="recent-icon">📄</span>'
        + '<span class="recent-title">' + p.title + '</span>'
        + '</a></div>';
    }).join("");

    container.innerHTML = '<div class="recent-grid">' + items + "</div>";
  }

  function init() {
    track();
    render();
  }

  /* Normal first load */
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  /* Material instant navigation — fires on every SPA page switch */
  document.addEventListener("DOMContentLoaded", function () {
    if (typeof document$ !== "undefined") {
      document$.subscribe(function () { init(); });
    }
  });
})();
