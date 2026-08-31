/* Dependency-free force-directed graph for docs/graph.md.
 * Reads assets/graph.json (built by scripts/generate_graph.py), runs a
 * small physics simulation on <canvas>, and links each node to its page.
 */
(function () {
  function init() {
    var canvas = document.getElementById("kg-canvas");
    var status = document.getElementById("kg-status");
    if (!canvas) return;

    var base = canvas.dataset.base || ".";
    fetch(base + "/assets/graph.json")
      .then(function (r) { return r.json(); })
      .then(function (data) { render(canvas, status, data, base); })
      .catch(function (err) {
        if (status) status.textContent = "Could not load graph.json: " + err;
      });
  }

  function isDark() {
    var scheme = document.body.getAttribute("data-md-color-scheme");
    return scheme === "slate";
  }

  function render(canvas, status, data, base) {
    var nodes = data.nodes.map(function (n, i) {
      return {
        id: n.id, title: n.title, tags: n.tags || [],
        x: 200 * Math.cos((i / data.nodes.length) * Math.PI * 2) + Math.random() * 10,
        y: 200 * Math.sin((i / data.nodes.length) * Math.PI * 2) + Math.random() * 10,
        vx: 0, vy: 0, degree: 0,
      };
    });
    var byId = {};
    nodes.forEach(function (n) { byId[n.id] = n; });

    var edges = data.edges
      .map(function (e) { return { source: byId[e.source], target: byId[e.target], kind: e.kind }; })
      .filter(function (e) { return e.source && e.target; });

    edges.forEach(function (e) { e.source.degree++; e.target.degree++; });

    if (status) {
      var isolated = nodes.filter(function (n) { return n.degree === 0; }).length;
      status.textContent = nodes.length + " pages, " + edges.length + " connections" +
        (isolated ? " — " + isolated + " page(s) not yet linked or tagged in common with anything" : "");
    }

    var ctx = canvas.getContext("2d");
    var dpr = window.devicePixelRatio || 1;
    var width, height;

    function resize() {
      var rect = canvas.parentElement.getBoundingClientRect();
      width = rect.width;
      height = Math.max(420, Math.min(640, width * 0.6));
      canvas.width = width * dpr;
      canvas.height = height * dpr;
      canvas.style.width = width + "px";
      canvas.style.height = height + "px";
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }
    resize();
    window.addEventListener("resize", resize);

    var cx = 0, cy = 0; // simulation-space center, screen center is width/2,height/2

    function step() {
      var n = nodes.length;
      for (var i = 0; i < n; i++) {
        var a = nodes[i];
        for (var j = i + 1; j < n; j++) {
          var b = nodes[j];
          var dx = a.x - b.x, dy = a.y - b.y;
          var distSq = dx * dx + dy * dy + 0.01;
          var force = 1800 / distSq;
          var dist = Math.sqrt(distSq);
          var fx = (dx / dist) * force, fy = (dy / dist) * force;
          a.vx += fx; a.vy += fy;
          b.vx -= fx; b.vy -= fy;
        }
        // gentle pull toward center so the graph doesn't drift off-canvas
        a.vx += (cx - a.x) * 0.002;
        a.vy += (cy - a.y) * 0.002;
      }
      edges.forEach(function (e) {
        var dx = e.target.x - e.source.x, dy = e.target.y - e.source.y;
        var dist = Math.sqrt(dx * dx + dy * dy) || 1;
        var target = e.kind === "tag" ? 140 : 90;
        var force = (dist - target) * 0.02;
        var fx = (dx / dist) * force, fy = (dy / dist) * force;
        e.source.vx += fx; e.source.vy += fy;
        e.target.vx -= fx; e.target.vy -= fy;
      });
      nodes.forEach(function (nd) {
        if (nd.dragging) return;
        nd.vx *= 0.85; nd.vy *= 0.85;
        nd.x += nd.vx * 0.02; nd.y += nd.vy * 0.02;
      });
    }

    function draw() {
      var dark = isDark();
      ctx.clearRect(0, 0, width, height);
      ctx.save();
      ctx.translate(width / 2, height / 2);

      var linkColor = dark ? "rgba(79,179,168,0.35)" : "rgba(31,111,104,0.35)";
      var tagLinkColor = dark ? "rgba(217,164,65,0.25)" : "rgba(161,102,10,0.25)";
      edges.forEach(function (e) {
        ctx.beginPath();
        ctx.moveTo(e.source.x, e.source.y);
        ctx.lineTo(e.target.x, e.target.y);
        ctx.strokeStyle = e.kind === "tag" ? tagLinkColor : linkColor;
        ctx.lineWidth = e.kind === "tag" ? 1 : 1.5;
        ctx.stroke();
      });

      nodes.forEach(function (nd) {
        var r = 5 + Math.min(nd.degree, 8) * 1.3;
        ctx.beginPath();
        ctx.arc(nd.x, nd.y, r, 0, Math.PI * 2);
        ctx.fillStyle = nd === hovered
          ? (dark ? "#4fb3a8" : "#1f6f68")
          : (dark ? "#2a333c" : "#e2f0ee");
        ctx.strokeStyle = dark ? "#4fb3a8" : "#1f6f68";
        ctx.lineWidth = 1.5;
        ctx.fill();
        ctx.stroke();

        if (nd === hovered || nd.degree >= 3) {
          ctx.fillStyle = dark ? "#e8edf2" : "#182430";
          ctx.font = "12px ui-sans-serif, system-ui, sans-serif";
          ctx.textAlign = "center";
          ctx.fillText(nd.title, nd.x, nd.y - r - 6);
        }
      });

      ctx.restore();
    }

    var hovered = null;
    var dragged = null;

    function toSimSpace(evt) {
      var rect = canvas.getBoundingClientRect();
      return { x: evt.clientX - rect.left - width / 2, y: evt.clientY - rect.top - height / 2 };
    }

    function nodeAt(pt) {
      for (var i = 0; i < nodes.length; i++) {
        var nd = nodes[i];
        var r = 5 + Math.min(nd.degree, 8) * 1.3 + 4;
        if (Math.hypot(nd.x - pt.x, nd.y - pt.y) < r) return nd;
      }
      return null;
    }

    canvas.addEventListener("mousemove", function (evt) {
      var pt = toSimSpace(evt);
      if (dragged) {
        dragged.x = pt.x; dragged.y = pt.y;
        return;
      }
      var found = nodeAt(pt);
      if (found !== hovered) {
        hovered = found;
        canvas.style.cursor = found ? "pointer" : "default";
      }
    });

    canvas.addEventListener("mousedown", function (evt) {
      var pt = toSimSpace(evt);
      var found = nodeAt(pt);
      if (found) { found.dragging = true; dragged = found; }
    });

    window.addEventListener("mouseup", function () {
      if (dragged) dragged.dragging = false;
      dragged = null;
    });

    canvas.addEventListener("click", function (evt) {
      if (dragged) return;
      var pt = toSimSpace(evt);
      var found = nodeAt(pt);
      if (found) window.location.href = base + "/" + found.id.replace(/\.md$/, ".html");
    });

    var frame;
    function loop() {
      step();
      draw();
      frame = requestAnimationFrame(loop);
    }
    loop();

    if (typeof document$ !== "undefined") {
      document$.subscribe(function () {
        cancelAnimationFrame(frame);
        window.removeEventListener("resize", resize);
      }, { once: true });
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
  document.addEventListener("DOMContentLoaded", function () {
    if (typeof document$ !== "undefined") {
      document$.subscribe(init);
    }
  });
})();
