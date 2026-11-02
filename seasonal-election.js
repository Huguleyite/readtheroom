/* SEASONAL:election
   Self-expiring Election Day layer. Active Nov 3, 2026 only (US Eastern).
   Read the Room switches to its results line at 7 PM Eastern.
   Preview any time: ?season=election  (add &phase=evening for the 7 PM wording).
   Rollback: run `python Tools/seasonal.py remove election <site>`, or delete this file
   and the one tagged loader line in each page. */
(function () {
  'use strict';
  if (window.self !== window.top) return;

  var search = location.search;
  var forced = /[?&]season=election(&|$)/.test(search);
  var forcedEvening = forced && /[?&]phase=evening(&|$)/.test(search);

  function easternNow() {
    var o = { y: 0, m: 0, d: 0, h: 0 };
    try {
      new Intl.DateTimeFormat('en-US', {
        timeZone: 'America/New_York', year: 'numeric', month: 'numeric', day: 'numeric',
        hour: 'numeric', hourCycle: 'h23'
      }).formatToParts(new Date()).forEach(function (p) {
        if (p.type === 'year') o.y = +p.value;
        if (p.type === 'month') o.m = +p.value;
        if (p.type === 'day') o.d = +p.value;
        if (p.type === 'hour') o.h = +p.value;
      });
    } catch (e) {
      var n = new Date(); o.y = n.getFullYear(); o.m = n.getMonth() + 1; o.d = n.getDate(); o.h = n.getHours();
    }
    return o;
  }

  var t = easternNow();
  var inWindow = t.y === 2026 && t.m === 11 && t.d === 3;
  if (!inWindow && !forced) return;

  var KEY = 'seasonal-election-dismissed-2026';
  if (!forced) {
    try { if (window.localStorage.getItem(KEY) === '1') return; } catch (e) {}
  }

  var evening = forcedEvening || (inWindow && t.h >= 19);
  var host = String(window.__SEASONAL_SITE || location.hostname).toLowerCase();

  // Per-site look and wording. Nonpartisan: no candidates, no party colors.
  var cfg = {
    msg: "It's Election Day. Go vote.",
    bg: '#0a0e1a', fg: '#e8c96a', rule: '#c9a84c', link: null
  };
  if (/vibefrag/.test(host)) {
    cfg.msg = "It's Election Day. Make a scent-sible choice and let your vote leave a lasting sillage.";
    cfg.bg = '#d4a878'; cfg.fg = '#09090b'; cfg.rule = '#09090b';
  } else if (/readtheroom/.test(host)) {
    cfg.bg = '#c8a96e'; cfg.fg = '#1a1a18'; cfg.rule = '#1a1a18';
    if (evening) {
      cfg.msg = 'Polls are closing. Follow Alabama results live on ';
      cfg.link = { text: 'Read the Returns', href: '/returns/' };
      cfg.tail = '. No refunds, just returns.';
    } else {
      cfg.msg = 'Today is Election Day. Check your ballot and polling place in our ';
      cfg.link = { text: 'Alabama Election Guide', href: '/signal/alabama-2026-election-guide.html' };
      cfg.tail = '.';
    }
  } else if (/atlasvalley/.test(host)) {
    cfg.msg = "It's Election Day. Cast your ballot, then curl up with a good mystery. Happy reading from Atlas Valley.";
  }

  function build() {
    if (document.getElementById('sx-election-bar')) return;

    var css = document.createElement('style');
    css.id = 'sx-election-style';
    css.setAttribute('data-seasonal', 'election');
    css.textContent =
      '.sx-ebar{position:fixed;left:0;right:0;bottom:0;z-index:2147483000;background:' + cfg.bg + ';color:' + cfg.fg + ';' +
      'border-top:2px solid ' + cfg.rule + ';font:600 16px/1.45 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;' +
      'letter-spacing:.02em;text-align:center;padding:16px 52px 16px 18px;box-sizing:border-box}' +
      '.sx-ebar a{color:inherit;text-decoration:underline;text-underline-offset:2px}' +
      '.sx-ebar a:hover,.sx-ebar a:focus-visible{text-decoration-thickness:2px}' +
      '.sx-ex{position:absolute;right:6px;top:50%;transform:translateY(-50%);background:none;border:0;color:' + cfg.fg + ';' +
      'font:400 24px/1 system-ui,sans-serif;cursor:pointer;padding:8px 14px;margin:0}' +
      '.sx-ex:focus-visible{outline:2px solid ' + cfg.fg + ';outline-offset:-2px}' +
      '@media(max-width:600px){.sx-ebar{font-size:14px;padding:14px 44px 14px 14px}}' +
      '@media print{.sx-ebar,.sx-espacer{display:none!important}}';
    document.head.appendChild(css);

    var bar = document.createElement('div');
    bar.id = 'sx-election-bar';
    bar.className = 'sx-ebar';
    bar.setAttribute('role', 'region');
    bar.setAttribute('aria-label', 'Election Day message');
    var text = document.createElement('span');
    text.appendChild(document.createTextNode(cfg.msg));
    if (cfg.link) {
      var a = document.createElement('a');
      a.href = cfg.link.href;
      a.textContent = cfg.link.text;
      text.appendChild(a);
      text.appendChild(document.createTextNode(cfg.tail || ''));
    }
    var x = document.createElement('button');
    x.className = 'sx-ex';
    x.type = 'button';
    x.setAttribute('aria-label', 'Dismiss Election Day message');
    x.textContent = '×';
    bar.appendChild(text);
    bar.appendChild(x);

    var spacer = document.createElement('div');
    spacer.className = 'sx-espacer';
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
