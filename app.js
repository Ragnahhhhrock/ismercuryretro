/*ASTRO*/
const D2R = Math.PI / 180;
const MERC = { a:[0.38709927,0.00000037], e:[0.20563593,0.00001906], I:[7.00497902,-0.00594749], L:[252.25032350,149472.67411175], w:[77.45779628,0.16047689], O:[48.33076593,-0.12534081] };
const EARTH = { a:[1.00000261,0.00000562], e:[0.01671123,-0.00004392], I:[-0.00001531,-0.01294668], L:[100.46457166,35999.37244981], w:[102.93768193,0.32327364], O:[0,0] };
const SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces'];
const toJD = ms => ms / 864e5 + 2440587.5;
const fromJD = jd => new Date((jd - 2440587.5) * 864e5);

function helio(p, T) {
  const v = k => p[k][0] + p[k][1] * T;
  const a = v('a'), e = v('e'), I = v('I') * D2R, L = v('L'), w = v('w'), O = v('O') * D2R;
  let M = (((L - w) % 360) + 540) % 360 - 180;
  M *= D2R;
  let E = M + e * Math.sin(M);
  for (let i = 0; i < 10; i++) E -= (E - e * Math.sin(E) - M) / (1 - e * Math.cos(E));
  const xp = a * (Math.cos(E) - e), yp = a * Math.sqrt(1 - e * e) * Math.sin(E);
  const om = w * D2R - O;
  const co = Math.cos(om), so = Math.sin(om), cO = Math.cos(O), sO = Math.sin(O), cI = Math.cos(I);
  return [
    (co * cO - so * sO * cI) * xp + (-so * cO - co * sO * cI) * yp,
    (co * sO + so * cO * cI) * xp + (-so * sO + co * cO * cI) * yp
  ];
}
function geoLon(jd) {
  const T = (jd - 2451545) / 36525;
  const m = helio(MERC, T), e = helio(EARTH, T);
  const l = Math.atan2(m[1] - e[1], m[0] - e[0]) / D2R + 1.396971 * T;
  return ((l % 360) + 360) % 360;
}
const wrap180 = d => { d %= 360; if (d > 180) d -= 360; if (d < -180) d += 360; return d; };
function rate(jd) { return wrap180(geoLon(jd + 0.5) - geoLon(jd - 0.5)); }
function station(jd, dir) {
  const s = Math.sign(rate(jd));
  let t = jd;
  for (let i = 0; i < 200; i++) {
    const t2 = t + dir;
    if (Math.sign(rate(t2)) !== s) {
      let lo = t, hi = t2;
      for (let k = 0; k < 32; k++) {
        const mid = (lo + hi) / 2;
        if (Math.sign(rate(mid)) === s) lo = mid; else hi = mid;
      }
      return (lo + hi) / 2;
    }
    t = t2;
  }
  return null;
}
function status(jd) {
  const r = rate(jd), retro = r < 0;
  const back = station(jd, -1), fwd = station(jd, 1);
  if (retro) return { retro, rate: r, start: back, end: fwd };
  return { retro, rate: r, prevEnd: back, start: fwd, end: station(fwd + 0.5, 1) };
}
function windowsFrom(jd, n) {
  const s = status(jd), list = [{ start: s.start, end: s.end }];
  let t = s.end;
  while (list.length < n) {
    const s2 = status(t + 30);
    list.push({ start: s2.start, end: s2.end });
    t = s2.end;
  }
  return list;
}
function shadow(w) {
  const lS = geoLon(w.start), lE = geoLon(w.end);
  let pre = w.start, post = w.end;
  for (let t = w.start; t > w.start - 120; t -= 0.25) { if (wrap180(geoLon(t) - lE) <= 0) { pre = t; break; } }
  for (let t = w.end; t < w.end + 120; t += 0.25) { if (wrap180(geoLon(t) - lS) >= 0) { post = t; break; } }
  return { pre, post };
}
/*END*/

const $ = id => document.getElementById(id);
const fmt = (jd, withYear) => fromJD(jd).toLocaleDateString(undefined, withYear ? { month: 'short', day: 'numeric', year: 'numeric' } : { month: 'short', day: 'numeric' });
const plural = n => n === 1 ? 'day' : 'days';
const signOf = jd => { const l = geoLon(jd); return Math.floor(l % 30) + '° ' + SIGNS[Math.floor(l / 30)]; };
const pad = n => String(n).padStart(2, '0');
const ymd = d => d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate());
const nowJD = () => toJD(Date.now());

const PAGES = ['today', 'dates', 'science', 'astrology', 'tips'];
const page = document.body.dataset.page;
const on = (id, ev, fn) => { const el = $(id); if (el) el.addEventListener(ev, fn); };
let sel = null;            // null means right now
let calYear = new Date().getFullYear();
let stateSel = 'no', stateNow = 'no';

function applyState() { $('app').dataset.state = (page === 'today' ? stateSel : stateNow); }

/* ---------- Today ---------- */
function chartSVG(jd, st) {
  const W = 360, H = 190, ml = 34, mr = 12, mt = 12, mb = 26;
  const a = st.start - 30, b = st.end + 30;
  const pts = [];
  for (let t = a; t <= b + 1e-9; t += 0.5) pts.push([t, rate(t)]);
  const ymin = Math.min(0, ...pts.map(p => p[1])) - 0.15;
  const ymax = Math.max(0, ...pts.map(p => p[1])) + 0.15;
  const X = t => ml + (t - a) / (b - a) * (W - ml - mr);
  const Y = v => mt + (ymax - v) / (ymax - ymin) * (H - mt - mb);
  const f = n => n.toFixed(1);
  const line = 'M' + pts.map(p => f(X(p[0])) + ' ' + f(Y(p[1]))).join('L');
  const rp = [[st.start, 0]];
  for (let t = st.start + 0.25; t < st.end; t += 0.25) rp.push([t, rate(t)]);
  rp.push([st.end, 0]);
  const rpath = 'M' + rp.map(p => f(X(p[0])) + ' ' + f(Y(p[1]))).join('L');
  const step = (ymax - ymin) > 3 ? 1 : 0.5;
  let grid = '';
  for (let v = Math.ceil(ymin / step) * step; v <= ymax; v += step) {
    const vv = Math.round(v * 10) / 10;
    const lab = vv === 0 ? '0' : (vv > 0 ? '+' : '−') + Math.abs(vv).toFixed(step < 1 ? 1 : 0);
    grid += `<line class="${vv === 0 ? 'g-zero' : 'g-grid'}" x1="${ml}" x2="${W - mr}" y1="${f(Y(vv))}" y2="${f(Y(vv))}"/>` +
            `<text class="g-text" x="${ml - 6}" y="${f(Y(vv) + 3.5)}" text-anchor="end">${lab}</text>`;
  }
  let ticks = '';
  for (let i = 0; i < 5; i++) {
    const t = a + (b - a) * i / 4;
    const anchor = i === 0 ? 'start' : i === 4 ? 'end' : 'middle';
    ticks += `<text class="g-text" x="${f(X(t))}" y="${H - 8}" text-anchor="${anchor}">${fmt(t)}</text>`;
  }
  const zy = Y(0);
  let marks = `<circle class="g-dot" cx="${f(X(st.start))}" cy="${f(zy)}" r="3.5"/><circle class="g-dot" cx="${f(X(st.end))}" cy="${f(zy)}" r="3.5"/>` +
    `<text class="g-tag" x="${f(X(st.start) - 6)}" y="${f(zy + 14)}" text-anchor="end">Rx</text>` +
    `<text class="g-tag" x="${f(X(st.end) + 6)}" y="${f(zy + 14)}" text-anchor="start">D</text>`;
  const inWin = jd >= a && jd <= b;
  if (inWin) {
    marks += `<line class="g-now" x1="${f(X(jd))}" x2="${f(X(jd))}" y1="${mt}" y2="${H - mb}"/>` +
             `<circle class="g-now-dot" cx="${f(X(jd))}" cy="${f(Y(rate(jd)))}" r="4.5"/>`;
  }
  const svg = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Mercury's apparent speed across the sky from ${fmt(a)} to ${fmt(b)}. Below zero means retrograde.">` +
    grid + `<path class="g-retro-area" d="${rpath}Z"/><path class="g-line" pathLength="1" d="${line}"/><path class="g-retro-line" pathLength="1" d="${rpath}"/>` + marks + ticks + `</svg>`;
  return { svg, inWin };
}

/* ---------- Countdown to the end of the current retrograde ---------- */
let cdEnd = null;          // JD the current retrograde ends, or null when not shown
let cdLock = false;        // true while the load count-up owns the text
function tickCountdown() {
  const box = $('countdown');
  if (!box) return;
  if (cdEnd === null) { box.hidden = true; return; }
  const secs = Math.max(0, Math.floor((cdEnd - nowJD()) * 86400));
  const d = Math.floor(secs / 86400), h = Math.floor(secs % 86400 / 3600), m = Math.floor(secs % 3600 / 60), sec = secs % 60;
  box.hidden = false;
  if (!cdLock) $('cd-time').innerHTML = (d ? d + 'd ' : '') + h + 'h ' + pad(m) + 'm <span class="cd-s">' + pad(sec) + 's</span>';
  if (secs === 0) setTimeout(render, 1000);   // retrograde just ended: refresh the answer
}
setInterval(() => { tickCountdown(); }, 1000);

function render() {
  const when = sel || new Date();
  const jd = toJD(when.getTime());
  const st = status(jd);
  stateSel = st.retro ? 'yes' : 'no';
  $('answer').textContent = st.retro ? 'YES' : 'NO';

  if (st.retro) {
    const left = Math.max(0, Math.ceil(st.end - jd));
    $('line').textContent = 'Retrograde from ' + fmt(st.start) + ' to ' + fmt(st.end) + '.';
    $('sub').textContent = 'Day ' + (Math.floor(jd - st.start) + 1) + ' of ' + Math.round(st.end - st.start) + ' · ' + left + ' ' + plural(left) + ' to go';
  } else {
    const away = Math.max(0, Math.ceil(st.start - jd));
    $('line').textContent = 'Moving direct. Next retrograde starts ' + fmt(st.start, true) + '.';
    $('sub').textContent = away + ' ' + plural(away) + ' away · runs ' + Math.round(st.end - st.start) + ' days';
  }

  const c = chartSVG(jd, st);
  $('chart').innerHTML = c.svg;
  $('chart-cap').textContent = (c.inWin ? 'The dot is the date you are checking. ' : 'The date you are checking is outside this window. ') +
    'Shaded area is retrograde, from Rx to D.';

  $('f-date').textContent = sel ? fmt(jd, true) : 'Today';
  $('f-pos').textContent = signOf(jd);
  const r = st.rate;
  $('f-rate').textContent = (r < 0 ? '−' : '+') + Math.abs(r).toFixed(2) + '°/day';
  $('date').value = ymd(when);

  cdEnd = (st.retro && !sel) ? st.end : null;
  tickCountdown();

  const wins = windowsFrom(jd, 3);
  $('windows').innerHTML = wins.map(w => {
    const now = jd >= w.start && jd <= w.end;
    return '<li><div class="w-top"><span class="w-dates">' + fmt(w.start) + ' – ' + fmt(w.end, true) + (now ? '<span class="now-tag">Now</span>' : '') +
      '</span></div><div class="w-sub">Starts at ' + signOf(w.start) + '</div></li>';
  }).join('');
  applyState();
}

/* ---------- Shared: status chip on sub pages ---------- */
function renderChips() {
  const j = nowJD(), st = status(j);
  stateNow = st.retro ? 'yes' : 'no';
  const text = st.retro ? 'Retrograde now, until ' + fmt(st.end) : 'Moving direct, next retrograde ' + fmt(st.start);
  document.querySelectorAll('[data-chip]').forEach(el => {
    el.className = 'chip ' + stateNow;
    el.innerHTML = '<i></i><span></span>';
    el.lastChild.textContent = text;
  });
  return st;
}

/* ---------- Dates ---------- */
function yearWindows(year) {
  const j0 = toJD(new Date(year, 0, 1).getTime()), j1 = toJD(new Date(year + 1, 0, 1).getTime());
  const out = windowsFrom(j0, 5).filter(w => w.end >= j0 && w.start < j1);
  return { out, j0, j1 };
}
function renderDates() {
  const { out, j0, j1 } = yearWindows(calYear);
  $('cal-year').textContent = calYear;
  $('y-prev').disabled = calYear <= 1850;
  $('y-next').disabled = calYear >= 2048;

  const W = 360, H = 62, ml = 4, mr = 4;
  const X = j => ml + (j - j0) / (j1 - j0) * (W - ml - mr);
  let s = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Retrograde periods across ${calYear}">` +
    `<rect class="g-track" x="${ml}" y="8" width="${W - ml - mr}" height="24" rx="4"/>`;
  out.forEach((w, i) => {
    const x0 = X(Math.max(w.start, j0)), x1 = X(Math.min(w.end, j1));
    s += `<rect class="g-band" style="--b:${i}" x="${x0.toFixed(1)}" y="8" width="${Math.max(2, x1 - x0).toFixed(1)}" height="24"/>`;
  });
  for (let m = 0; m < 12; m++) {
    const a = X(toJD(new Date(calYear, m, 1).getTime())), b = X(toJD(new Date(calYear, m + 1, 1).getTime()));
    if (m > 0) s += `<line class="g-grid" x1="${a.toFixed(1)}" x2="${a.toFixed(1)}" y1="32" y2="38"/>`;
    const label = new Date(calYear, m, 15).toLocaleDateString(undefined, { month: 'short' });
    s += `<text class="g-text" x="${((a + b) / 2).toFixed(1)}" y="54" text-anchor="middle">${label}</text>`;
  }
  if (calYear === new Date().getFullYear()) {
    const x = X(nowJD()).toFixed(1);
    s += `<line class="g-now" x1="${x}" x2="${x}" y1="2" y2="38"/>`;
  }
  $('strip').innerHTML = s + '</svg>';

  const days = out.reduce((n, w) => n + (Math.min(w.end, j1) - Math.max(w.start, j0)), 0);
  $('cal-cap').textContent = out.length + ' retrograde ' + (out.length === 1 ? 'period' : 'periods') + ', about ' + Math.round(days) + ' days in all.' +
    (calYear === new Date().getFullYear() ? ' The dashed line is today.' : '');

  const nj = nowJD();
  const yr = jd => fromJD(jd).getFullYear() !== calYear;
  $('cal-list').innerHTML = out.map(w => {
    const sh = shadow(w), now = nj >= w.start && nj <= w.end;
    return '<li><div class="w-top"><span class="w-dates">' + fmt(w.start, yr(w.start)) + ' – ' + fmt(w.end, yr(w.end)) + (now ? '<span class="now-tag">Now</span>' : '') +
      '</span><span class="w-len">' + Math.round(w.end - w.start) + ' days</span></div>' +
      '<div class="w-sub">' + signOf(w.start) + ' back to ' + signOf(w.end) + '</div>' +
      '<div class="w-sub">Shadow: ' + fmt(sh.pre, yr(sh.pre)) + ' – ' + fmt(sh.post, yr(sh.post)) + '</div></li>';
  }).join('');
}

/* ---------- Astrology ---------- */
const ELEMENTS = [
  ['fire', 'a fire', 'Astrologers expect impulsive words, short tempers and rushed decisions.'],
  ['earth', 'an earth', 'Astrologers expect snags with money, work, schedules and practical plans.'],
  ['air', 'an air', 'Astrologers expect crossed wires in conversations, messages and devices.'],
  ['water', 'a water', 'Astrologers expect old feelings, memories and relationships to resurface.']
];
function renderAstro(st) {
  const sign = SIGNS[Math.floor(geoLon(st.start) / 30)];
  const el = ELEMENTS[SIGNS.indexOf(sign) % 4];
  $('astro-now').textContent = (st.retro ? 'The current retrograde began in ' : 'The next retrograde begins in ') + sign + ', ' + el[1] + ' sign. ' + el[2];
}

/* ---------- Tips ---------- */
const TIPS = [
  ['Before you send', ['Re-read important messages and check who they are going to.', 'Check the attachment is the right one.']],
  ['Tech', ['Back up your phone and laptop.', 'Save work often and keep a copy of anything critical somewhere else.']],
  ['Travel and plans', ['Reconfirm flights, bookings and meeting times the day before.', 'Leave extra time between connections and appointments.']],
  ['Money and contracts', ['Read the fine print twice and get agreements in writing.', 'Hold big purchases and launches until the retrograde ends, if you can.']],
  ['People', ['Say what you mean plainly and ask instead of assuming.']]
];
function loadChecks() { try { return JSON.parse(localStorage.getItem('mrx-checks') || '{}'); } catch (e) { return {}; } }
function saveChecks(o) { try { localStorage.setItem('mrx-checks', JSON.stringify(o)); } catch (e) {} }
function renderTips() {
  const on = loadChecks();
  let html = '', n = 0;
  TIPS.forEach(g => {
    html += '<p class="group-h">' + g[0] + '</p>';
    g[1].forEach(t => {
      const id = 'tip' + (n++);
      html += '<label class="check"><input type="checkbox" id="' + id + '" data-k="' + id + '"' + (on[id] ? ' checked' : '') + '><span>' + t + '</span></label>';
    });
  });
  $('checks').innerHTML = html;
}
on('checks', 'change', e => {
  const k = e.target.dataset.k;
  if (!k) return;
  const o = loadChecks();
  if (e.target.checked) o[k] = 1; else delete o[k];
  saveChecks(o);
});
on('clear', 'click', () => { saveChecks({}); renderTips(); });

/* ---------- Controls ---------- */
function setDate(d) {
  sel = ymd(d) === ymd(new Date()) ? null : new Date(d.getFullYear(), d.getMonth(), d.getDate(), 12);
  render();
}
function shift(n) {
  const base = sel ? new Date(sel) : new Date();
  base.setDate(base.getDate() + n);
  if (base.getFullYear() < 1850 || base.getFullYear() > 2049) return;
  setDate(base);
}
on('prev', 'click', () => shift(-1));
on('next', 'click', () => shift(1));
on('today', 'click', () => { sel = null; render(); });
on('date', 'change', e => {
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(e.target.value);
  if (m) setDate(new Date(+m[1], +m[2] - 1, +m[3], 12)); else render();
});
on('y-prev', 'click', () => { if (calYear > 1850) { calYear--; renderDates(); } });
on('y-next', 'click', () => { if (calYear < 2048) { calYear++; renderDates(); } });

/* ---------- Load animation (Today page, first render only) ---------- */
const reduceMotion = !!(window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches);
/* Counts every number in the element's text up from 0 to its final value, keeping the formatting. */
function countUp(el, delay, dur, done) {
  if (!el || !el.textContent) { if (done) done(); return; }
  const final = el.textContent;
  const parts = final.split(/(\d+(?:\.\d+)?)/);   // odd indexes are the numbers
  if (parts.length < 3) { if (done) done(); return; }
  const build = k => parts.map((p, i) => {
    if (i % 2 === 0) return p;
    const dec = p.includes('.') ? p.split('.')[1].length : 0;
    const s = dec ? (parseFloat(p) * k).toFixed(dec) : String(Math.round(parseFloat(p) * k));
    return (!dec && p.length > 1 && p[0] === '0') ? s.padStart(p.length, '0') : s;
  }).join('');
  el.textContent = build(0);
  setTimeout(() => {
    const t0 = performance.now();
    (function step(now) {
      const x = Math.min(1, (now - t0) / dur);
      el.textContent = x < 1 ? build(1 - Math.pow(1 - x, 3)) : final;
      if (x < 1) requestAnimationFrame(step); else if (done) done();
    })(t0);
  }, delay);
}
function playIntro() {
  if (reduceMotion) return;
  const app = $('app');
  document.querySelectorAll('.page .panel').forEach((el, i) => el.style.setProperty('--i', i));
  document.querySelectorAll('.page dl.facts, .page ul.windows').forEach(list =>
    list.querySelectorAll('.row, li').forEach((el, j) => el.style.setProperty('--j', j)));
  document.querySelectorAll('.page .ph > *').forEach((el, k) => el.style.setProperty('--k', k));
  app.classList.add('intro');
  if (page === 'today') {
    countUp($('sub'), 300, 1100);
    if (!$('countdown').hidden) { cdLock = true; countUp($('cd-time'), 400, 1300, () => { cdLock = false; tickCountdown(); }); }
    countUp($('f-rate'), 700, 1000);
  } else if (page === 'dates') {
    countUp($('cal-cap'), 500, 1100);
    document.querySelectorAll('#cal-list .w-len').forEach(el => countUp(el, 700, 900));
  }
  setTimeout(() => app.classList.remove('intro'), 3200);
}

/* ---------- Boot ---------- */
/* Old single-page links like /#tips go to the matching page. */
if (page === 'today' && PAGES.includes((location.hash || '').slice(1)) && location.hash !== '#today') {
  location.replace('/' + location.hash.slice(1) + '/');
}
const nowStatus = renderChips();
if (page === 'today') { render(); playIntro(); }
if (page === 'dates') { renderDates(); playIntro(); }
if (page === 'astrology') renderAstro(nowStatus);
if (page === 'tips') renderTips();
applyState();

/* ---------- Google Analytics events ---------- */
function track(name, params) { try { if (typeof gtag === 'function') gtag('event', name, params || {}); } catch (e) {} }
track('tab_view', { tab_name: page });
[['prev', 'previous_day'], ['next', 'next_day'], ['today', 'today']].forEach(p =>
  on(p[0], 'click', () => track('date_change', { method: p[1] })));
on('date', 'change', () => track('date_change', { method: 'date_picker' }));
on('y-prev', 'click', () => track('year_change', { direction: 'previous', year: calYear }));
on('y-next', 'click', () => track('year_change', { direction: 'next', year: calYear }));
on('checks', 'change', e => { if (e.target.dataset.k) track('tip_toggle', { tip_id: e.target.dataset.k, checked: e.target.checked }); });
on('clear', 'click', () => track('tips_clear'));
document.querySelectorAll('.coffee').forEach(a => a.addEventListener('click', () => track('coffee_click')));
document.querySelectorAll('a[href^="mailto:"]').forEach(a => a.addEventListener('click', () => track('contact_click')));
document.querySelectorAll('a[href="https://malgordon.com"]').forEach(a => a.addEventListener('click', () => track('creator_link_click')));
