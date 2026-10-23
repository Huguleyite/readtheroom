/* SEASONAL:halloween
   Self-expiring Halloween layer. Active Oct 25 - Nov 1, 2026 (US Eastern).
   Rollback: run `python Tools/seasonal.py remove halloween <site>`, or delete this file
   and the one tagged loader line in each page. */
(function () {
  'use strict';
  if (window.self !== window.top) return;

  var forced = /[?&]season=halloween(&|$)/.test(location.search);

  function easternNow() {
    var m = 0, d = 0, y = 0;
    try {
      new Intl.DateTimeFormat('en-US', { timeZone: 'America/New_York', year: 'numeric', month: 'numeric', day: 'numeric' })
        .formatToParts(new Date()).forEach(function (p) {
          if (p.type === 'month') m = +p.value;
          if (p.type === 'day') d = +p.value;
          if (p.type === 'year') y = +p.value;
        });
    } catch (e) {
      var n = new Date(); m = n.getMonth() + 1; d = n.getDate(); y = n.getFullYear();
    }
    return { y: y, m: m, d: d };
  }

  var t = easternNow();
  var inWindow = t.y === 2026 && ((t.m === 10 && t.d >= 25) || (t.m === 11 && t.d === 1));
  if (!inWindow && !forced) return;

  var KEY = 'seasonal-halloween-dismissed-2026';
  if (!forced) {
    try { if (window.localStorage.getItem(KEY) === '1') return; } catch (e) {}
  }

  var host = String(window.__SEASONAL_SITE || location.hostname).toLowerCase();
  var msg = 'Happy Halloween';
  if (/vibefrag/.test(host)) msg = 'Spooky season picks are in. Boo-tiful bottles all week. Happy Halloween from VibeFrag';
  else if (/readtheroom/.test(host)) msg = 'Nothing scary about reading the room. Happy Halloween from Read the Room';
  else if (/atlasvalley/.test(host)) msg = 'Mystery loves October. Happy Halloween from Atlas Valley';

  function build() {
    if (document.getElementById('sx-halloween-bar')) return;

    var css = document.createElement('style');
    css.id = 'sx-halloween-style';
    css.setAttribute('data-seasonal', 'halloween');
    css.textContent =
      '.sx-bar{position:fixed;left:0;right:0;bottom:0;z-index:2147483000;background:#2a1a3d;color:#e8944a;' +
      'border-top:1px solid rgba(232,148,74,.35);font:500 12px/1.4 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;' +
      'letter-spacing:.04em;text-align:center;padding:8px 44px 8px 14px;box-sizing:border-box}' +
      '.sx-x{position:absolute;right:4px;top:50%;transform:translateY(-50%);background:none;border:0;color:#e8944a;' +
      'font:400 20px/1 system-ui,sans-serif;cursor:pointer;padding:6px 12px;margin:0}' +
      '.sx-x:hover,.sx-x:focus-visible{color:#fff}' +
      '.sx-x:focus-visible{outline:2px solid #e8944a;outline-offset:-2px}' +
      'main p a:not([class]):hover,article p a:not([class]):hover{color:#e8944a}' +
      '::selection{background:#e8944a;color:#1a1020}' +
      '@media print{.sx-bar,.sx-spacer{display:none!important}}';
    document.head.appendChild(css);

    var bar = document.createElement('div');
    bar.id = 'sx-halloween-bar';
    bar.className = 'sx-bar';
    bar.setAttribute('role', 'region');
    bar.setAttribute('aria-label', 'Seasonal message');
    var text = document.createElement('span');
    text.textContent = msg;
    var x = document.createElement('button');
    x.className = 'sx-x';
    x.type = 'button';
    x.setAttribute('aria-label', 'Dismiss Halloween message');
    x.textContent = '\u00d7';
    bar.appendChild(text);
    bar.appendChild(x);

    var spacer = document.createElement('div');
    spacer.className = 'sx-spacer';
    spacer.setAttribute('aria-hidden', 'true');

    document.body.appendChild(spacer);
    document.body.appendChild(bar);

    function size() { spacer.style.height = bar.offsetHeight + 'px'; }
    size();
    window.addEventListener('resize', size);

    x.addEventListener('click', function () {
      try { window.localStorage.setItem(KEY, '1'); } catch (e) {}
      window.removeEventListener('resize', size);
      if (bar.parentNode) bar.parentNode.removeChild(bar);
      if (spacer.parentNode) spacer.parentNode.removeChild(spacer);
    });
  }

  if (document.body) build();
  else document.addEventListener('DOMContentLoaded', build);
})();
