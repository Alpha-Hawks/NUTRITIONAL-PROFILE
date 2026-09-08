/* ==========================================================================
   Navigation transition - "arrow flight" into the User Login page.

   Two halves that stitch together across the page load:

     exit   (this page)  a glowing arrow flies a curve from the nav link to
                         the point where the login card will appear, an iris
                         closes over that same point, then we navigate.
     enter  (next page)  a scrim opens from that point while the backdrop
                         pulls back and the card scales up into place.

   The handoff is a sessionStorage flag, so the enter half only plays when
   the visitor actually arrived through the arrow - a direct visit or a
   refresh keeps the ordinary gentle rise.

   Vanilla JS: base.html loads jQuery after the page content.
   ========================================================================== */
(function () {
  'use strict';

  var ARRIVE_KEY = 'lg:arrive';
  var TRAVEL_MS = 560;   // arrow flight
  var IRIS_LAG = 240;    // iris starts this far into the flight
  var SCRIM_MS = 620;    // enter-side scrim + card open

  var calm = window.matchMedia('(prefers-reduced-motion: reduce)');
  var inFlight = false;  // guards against double clicks

  /* ---- maths ----------------------------------------------------------- */

  function quad(p0, p1, p2, t) {
    var mt = 1 - t;
    return {
      x: mt * mt * p0.x + 2 * mt * t * p1.x + t * t * p2.x,
      y: mt * mt * p0.y + 2 * mt * t * p1.y + t * t * p2.y
    };
  }

  function quadTangent(p0, p1, p2, t) {
    var mt = 1 - t;
    return {
      x: 2 * mt * (p1.x - p0.x) + 2 * t * (p2.x - p1.x),
      y: 2 * mt * (p1.y - p0.y) + 2 * t * (p2.y - p1.y)
    };
  }

  /* Slow start, long glide, soft arrival - no sudden movement at either end. */
  function easeInOutQuint(t) {
    return t < 0.5 ? 16 * t * t * t * t * t : 1 - Math.pow(-2 * t + 2, 5) / 2;
  }

  /* Control point bowed off the straight line, so the flight arcs the way a
     thrown object would rather than tracking a ruler. */
  function controlPoint(from, to) {
    var mx = (from.x + to.x) / 2;
    var my = (from.y + to.y) / 2;
    var dx = to.x - from.x;
    var dy = to.y - from.y;
    var dist = Math.sqrt(dx * dx + dy * dy) || 1;
    var bow = Math.min(dist * 0.28, 190);
    /* Perpendicular, pushed to the side the nav sits on. */
    return { x: mx + (dy / dist) * bow, y: my - (dx / dist) * bow * 0.35 };
  }

  /* ---- exit ------------------------------------------------------------- */

  function buildLayer(from, to, ctrl) {
    var w = window.innerWidth;
    var h = window.innerHeight;

    var layer = document.createElement('div');
    layer.className = 'pt-layer';
    layer.setAttribute('aria-hidden', 'true');   /* decorative only */

    var svgNS = 'http://www.w3.org/2000/svg';
    var svg = document.createElementNS(svgNS, 'svg');
    svg.setAttribute('class', 'pt-svg');
    svg.setAttribute('viewBox', '0 0 ' + w + ' ' + h);
    svg.setAttribute('preserveAspectRatio', 'none');

    var defs = document.createElementNS(svgNS, 'defs');
    defs.innerHTML =
      '<linearGradient id="ptTrail" x1="0" y1="0" x2="1" y2="1">' +
        '<stop offset="0%" stop-color="#8fc22e" stop-opacity="0"/>' +
        '<stop offset="55%" stop-color="#8fc22e" stop-opacity=".75"/>' +
        '<stop offset="100%" stop-color="#ffffff" stop-opacity=".95"/>' +
      '</linearGradient>' +
      '<filter id="ptGlow" x="-60%" y="-60%" width="220%" height="220%">' +
        '<feGaussianBlur stdDeviation="6" result="b"/>' +
        '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>' +
      '</filter>';
    svg.appendChild(defs);

    var d = 'M ' + from.x + ' ' + from.y +
            ' Q ' + ctrl.x + ' ' + ctrl.y + ' ' + to.x + ' ' + to.y;

    var trail = document.createElementNS(svgNS, 'path');
    trail.setAttribute('class', 'pt-trail');
    trail.setAttribute('d', d);
    svg.appendChild(trail);

    var head = document.createElementNS(svgNS, 'g');
    head.setAttribute('class', 'pt-head');
    head.innerHTML =
      '<circle r="13" class="pt-halo"/>' +
      '<path class="pt-tip" d="M -7 -6.5 L 8 0 L -7 6.5 L -4 0 Z"/>';
    svg.appendChild(head);

    layer.appendChild(svg);

    var iris = document.createElement('div');
    iris.className = 'pt-iris';
    iris.style.left = to.x + 'px';
    iris.style.top = to.y + 'px';
    layer.appendChild(iris);

    document.body.appendChild(layer);
    return { layer: layer, trail: trail, head: head, iris: iris };
  }

  function flyTo(href, from) {
    var to = { x: window.innerWidth / 2, y: window.innerHeight * 0.46 };
    var ctrl = controlPoint(from, to);
    var parts = buildLayer(from, to, ctrl);

    var len = parts.trail.getTotalLength();
    var tail = Math.max(90, Math.min(len * 0.42, 240));
    parts.trail.style.strokeDasharray = tail + ' ' + (len + tail);

    var start = null;
    var navigated = false;

    function go() {
      if (navigated) return;
      navigated = true;
      try { sessionStorage.setItem(ARRIVE_KEY, '1'); } catch (e) { /* private mode */ }
      window.location.href = href;
    }

    /* Never strand the visitor if a frame callback stalls. */
    var failsafe = setTimeout(go, TRAVEL_MS + 500);

    function frame(now) {
      if (start === null) start = now;
      var t = Math.min((now - start) / TRAVEL_MS, 1);
      var e = easeInOutQuint(t);

      var p = quad(from, ctrl, to, e);
      var tan = quadTangent(from, ctrl, to, e);
      var angle = Math.atan2(tan.y, tan.x) * 180 / Math.PI;

      parts.head.setAttribute('transform',
        'translate(' + p.x + ' ' + p.y + ') rotate(' + angle + ')');
      parts.trail.style.strokeDashoffset = String(tail - e * (len + tail));

      /* Head fades as it lands; the iris takes over. */
      parts.head.style.opacity = String(t < 0.86 ? 1 : (1 - t) / 0.14);

      var irisT = Math.max(0, (now - start - IRIS_LAG) / (TRAVEL_MS - IRIS_LAG + 60));
      if (irisT > 0) {
        var ie = easeInOutQuint(Math.min(irisT, 1));
        var reach = Math.hypot(
          Math.max(to.x, window.innerWidth - to.x),
          Math.max(to.y, window.innerHeight - to.y)
        ) * 1.08;
        parts.iris.style.width = parts.iris.style.height = (reach * 2 * ie) + 'px';
        parts.iris.style.opacity = String(Math.min(ie * 1.5, 1));
      }

      if (t < 1) {
        requestAnimationFrame(frame);
      } else {
        clearTimeout(failsafe);
        go();
      }
    }

    requestAnimationFrame(frame);
  }

  function onNavClick(e) {
    /* Let people open it in a new tab / window as usual. */
    if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || e.button !== 0) return;

    var link = e.currentTarget;
    var href = link.getAttribute('href');
    if (!href) return;

    /* Already here - nothing to fly to. */
    if (link.pathname === window.location.pathname) return;

    if (calm.matches) return;          // reduced motion: ordinary navigation
    if (inFlight) { e.preventDefault(); return; }

    /* A link inside a collapsed mobile menu measures 0x0. Without this the
       arrow would launch from the top-left corner instead of the button. */
    var r = link.getBoundingClientRect();
    if (!r.width || !r.height) return;

    e.preventDefault();
    inFlight = true;
    document.documentElement.classList.add('pt-busy');
    link.classList.add('pt-firing');

    flyTo(href, { x: r.left + r.width / 2, y: r.bottom - 2 });
  }

  /* ---- enter ------------------------------------------------------------ */

  function playArrival() {
    var arrived = false;
    try {
      arrived = sessionStorage.getItem(ARRIVE_KEY) === '1';
      if (arrived) sessionStorage.removeItem(ARRIVE_KEY);
    } catch (e) { /* private mode */ }

    if (!arrived || calm.matches) return;

    var scope = document.querySelector('.lg-scope');
    if (scope) scope.classList.add('lg-arrive');

    var scrim = document.createElement('div');
    scrim.className = 'pt-arrive';
    scrim.setAttribute('aria-hidden', 'true');   /* decorative only */
    document.body.appendChild(scrim);

    /* Next frame, so the starting state is painted before it animates out. */
    requestAnimationFrame(function () {
      requestAnimationFrame(function () { scrim.classList.add('pt-arrive--out'); });
    });
    setTimeout(function () {
      if (scrim.parentNode) scrim.parentNode.removeChild(scrim);
    }, SCRIM_MS + 160);
  }

  /* ---- wiring ----------------------------------------------------------- */

  function init() {
    var links = document.querySelectorAll('[data-pt-link]');
    Array.prototype.forEach.call(links, function (a) {
      a.addEventListener('click', onNavClick);
    });
    playArrival();
  }

  /* A back/forward restore from bfcache must not stay locked out. */
  window.addEventListener('pageshow', function (ev) {
    if (ev.persisted) {
      inFlight = false;
      document.documentElement.classList.remove('pt-busy');
      var stale = document.querySelector('.pt-layer');
      if (stale && stale.parentNode) stale.parentNode.removeChild(stale);
    }
  });

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
