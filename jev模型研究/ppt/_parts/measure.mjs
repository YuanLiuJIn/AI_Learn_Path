import { spawn } from 'node:child_process';
import os from 'node:os';
import path from 'node:path';
import fs from 'node:fs';

const EDGE = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe';
const deckUrl = process.argv[2];
const W = Number(process.argv[3] || 1600);
const H = Number(process.argv[4] || 900);
const port = 9333 + (Number(process.env.PORTOFF) || 0);
const ud = path.join(os.tmpdir(), 'edge-cdp-' + Date.now());

const child = spawn(EDGE, [
  '--headless=new', '--disable-gpu', '--no-first-run', '--hide-scrollbars',
  '--force-device-scale-factor=1',
  '--disable-background-timer-throttling', '--disable-backgrounding-occluded-windows',
  '--disable-renderer-backgrounding', '--disable-features=CalculateNativeWinOcclusion',
  `--remote-debugging-port=${port}`, `--user-data-dir=${ud}`, `${deckUrl}?slide=1`
], { stdio: 'ignore' });

async function targetUrl() {
  for (let i = 0; i < 80; i++) {
    try {
      const list = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
      const p = list.find(t => t.type === 'page' && t.webSocketDebuggerUrl);
      if (p) return p.webSocketDebuggerUrl;
    } catch { }
    await new Promise(r => setTimeout(r, 250));
  }
  throw new Error('DevTools 未就绪');
}

const ws = new WebSocket(await targetUrl());
await new Promise((res, rej) => { ws.addEventListener('open', res); ws.addEventListener('error', rej); });
let seq = 0; const pending = new Map();
ws.addEventListener('message', e => {
  const m = JSON.parse(e.data);
  if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); }
});
const send = (method, params = {}) => new Promise(res => { const id = ++seq; pending.set(id, res); ws.send(JSON.stringify({ id, method, params })); });
const sleep = ms => new Promise(r => setTimeout(r, ms));
const evaluate = async expr => {
  const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true });
  if (r.result?.exceptionDetails) throw new Error(JSON.stringify(r.result.exceptionDetails).slice(0, 300));
  return r.result.result.value;
};

await sleep(1500);

const MEASURE = `(() => {
  const slides = [...document.querySelectorAll('.slide')];
  let idx = 0, best = Infinity;
  slides.forEach((s, i) => { const r = s.getBoundingClientRect(); const d = Math.abs(r.left) + Math.abs(r.top); if (d < best) { best = d; idx = i; } });
  const slide = slides[idx];
  const card = slide.querySelector('.canvas-card');
  const sr = slide.getBoundingClientRect();
  const HH = sr.height, WW = sr.width;
  const cv = card.getBoundingClientRect();
  const hasText = el => [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim().length > 1);

  const textEls = [...card.querySelectorAll('*')].filter(el => {
    if (/^(CANVAS|SCRIPT|STYLE)$/.test(el.tagName)) return false;
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden') return false;
    const r = el.getBoundingClientRect();
    if (r.width < 1 || r.height < 1) return false;
    return hasText(el);
  });
  let top = Infinity, bottom = -Infinity, left = Infinity, right = -Infinity;
  textEls.forEach(el => { const r = el.getBoundingClientRect(); top = Math.min(top, r.top); bottom = Math.max(bottom, r.bottom); left = Math.min(left, r.left); right = Math.max(right, r.right); });

  const chrome = ['nav', 'hint'].map(id => document.getElementById(id)).filter(Boolean)
    .map(el => ({ id: el.id, r: el.getBoundingClientRect() }));
  const chromeInfo = chrome.map(c => c.id + ' y ' + Math.round(c.r.top) + '..' + Math.round(c.r.bottom) + ' x ' + Math.round(c.r.left) + '..' + Math.round(c.r.right));

  const clipped = [], tiny = [], invisible = [], outX = [], collide = [], nowrapOver = [];
  card.querySelectorAll('*').forEach(el => {
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden') return;
    const r = el.getBoundingClientRect();
    if ((cs.overflowY === 'hidden' || cs.overflowY === 'clip') && r.width > 0 && el.scrollHeight > el.clientHeight + 3 && !/^(IMG|CANVAS|SVG)$/.test(el.tagName))
      clipped.push((el.className || el.tagName) + '|' + el.scrollHeight + '>' + el.clientHeight);
    if (hasText(el) && parseFloat(cs.fontSize) < 14) tiny.push((el.className || el.tagName) + '|' + cs.fontSize);
    if (hasText(el) && parseFloat(cs.opacity) < 0.15) invisible.push((el.className || el.tagName));
    if (r.width > 0 && (r.left < sr.left - 2 || r.right > sr.right + 2)) outX.push((el.className || el.tagName) + '|' + Math.round(r.left) + '..' + Math.round(r.right));
    if ((cs.whiteSpace === 'nowrap' || cs.whiteSpace === 'pre') && el.clientWidth > 0 && el.scrollWidth > el.clientWidth + 1)
      nowrapOver.push((el.className || el.tagName) + '|sw' + el.scrollWidth + '>cw' + el.clientWidth);
    if (hasText(el) && r.height > 0) chrome.forEach(c => {
      if (r.bottom > c.r.top + 1 && r.top < c.r.bottom && r.right > c.r.left && r.left < c.r.right)
        collide.push((el.className || el.tagName) + '|' + Math.round(r.top) + '..' + Math.round(r.bottom) + ' vs #' + c.id);
    });
  });

  const gridDetail = {};
  ['.sub-grid-3-2', '.stack-row', '.stacked-ledger'].forEach(sel => {
    const g = card.querySelector(sel);
    if (!g) return;
    gridDetail[sel] = {
      box: [Math.round(g.clientWidth), Math.round(g.clientHeight)], scroll: g.scrollHeight,
      children: [...g.children].map(c => { const cs = getComputedStyle(c); return Math.round(c.getBoundingClientRect().height) + '/' + c.scrollHeight + (cs.borderTopWidth !== '0px' ? '*b' : ''); })
    };
  });
  const text = card.innerText.replace(/\\s+/g, ' ').trim();
  const navEl = document.getElementById('nav');
  const darkBody = document.body.classList.contains('dark-bg');
  let navConflict = '';
  if (navEl) {
    const nr2 = navEl.getBoundingClientRect();
    const blocks = [...card.querySelectorAll('.b-accent,.b-ink,.sub-card.accent,.sub-card.ink,.half.b-accent,.half.b-ink')];
    const hit = blocks.filter(b => {
      const r = b.getBoundingClientRect();
      if (!(r.bottom > nr2.top + 1 && r.top < nr2.bottom - 1 && r.right > nr2.left + 1 && r.left < nr2.right - 1)) return false;
      const m = (getComputedStyle(b).backgroundColor.match(/[\\d.]+/g) || [0, 0, 0]);
      const lum = 0.299 * +m[0] + 0.587 * +m[1] + 0.114 * +m[2];
      return (lum < 140) !== darkBody;
    });
    if (hit.length) navConflict = hit.map(b => (b.className || b.tagName).slice(0, 26)).join(' , ');
  }
  const ccs = getComputedStyle(card);
  const flexInfo = {
    card: ccs.display + '/' + ccs.flexDirection + ' box=' + ccs.boxSizing + ' pad ' + ccs.paddingTop + ',' + ccs.paddingBottom + ' gap ' + ccs.rowGap + ' justify ' + ccs.justifyContent,
    box: 'clientH ' + card.clientHeight + ' scrollH ' + card.scrollHeight + ' rectH ' + Math.round(cv.height),
    kids: [...card.children].filter(el => !el.classList.contains('ascii-bg')).map(el => {
      const k = getComputedStyle(el);
      return (el.className || el.tagName).slice(0, 26) + '|' + k.flexGrow + '/' + k.flexShrink + '/' + k.flexBasis + '|h' + Math.round(el.getBoundingClientRect().height) + '|offT' + el.offsetTop + ' offH' + el.offsetHeight + ' mB' + k.marginBottom;
    })
  };
  return {
    idx, id: slide.dataset.slideId, layout: slide.dataset.layout, size: [Math.round(WW), Math.round(HH)],
    cardBox: [Math.round(cv.width), Math.round(cv.height)], flexInfo,
    top: Math.round(top), bottom: Math.round(bottom),
    bottomPct: +(bottom / HH * 100).toFixed(1), topPct: +(top / HH * 100).toFixed(1),
    l: Math.round(left), r: Math.round(right),
    vFill: +(((bottom - top) / cv.height) * 100).toFixed(1),
    hFill: +(((right - left) / cv.width) * 100).toFixed(1),
    chars: text.length,
    clipped: [...new Set(clipped)], tiny: [...new Set(tiny)], invisible: [...new Set(invisible)], outX: [...new Set(outX)], collide: [...new Set(collide)], nowrapOver: [...new Set(nowrapOver)],
    chromeInfo, navConflict,
    scrollOverflow: card.scrollHeight > card.clientHeight + 2 || card.scrollWidth > card.clientWidth + 2,
    gridDetail, slideCount: slides.length
  };
})()`;

async function waitReady(timeout = 20000) {
  const t0 = Date.now();
  let n = 0;
  while (Date.now() - t0 < timeout) {
    try {
      const st = await evaluate('document.readyState');
      n = await evaluate('document.querySelectorAll(".slide").length');
      if (st === 'complete' && n > 0) return n;
    } catch { }
    await sleep(300);
  }
  return n;
}

async function settle(timeout = 12000) {
  const t0 = Date.now();
  await sleep(1800);
  while (Date.now() - t0 < timeout) {
    try {
      const running = await evaluate('document.getAnimations().filter(a=>a.playState==="running").length');
      if (running === 0) return true;
    } catch { }
    await sleep(300);
  }
  return false;
}

await send('Page.enable');
const total = await waitReady();
console.log(`ARG = ${deckUrl}\n页数 = ${total}`);
const rows = [];
for (let i = 1; i <= total; i++) {
  await send('Page.navigate', { url: `${deckUrl}?slide=${i}` });
  await send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: 1, mobile: false });
  await sleep(600);
  await send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: 1, mobile: false });
  await waitReady();
  const ok = await settle();
  if (!ok) console.log(`  (警告: P${i} 动画未在超时内结束)`);
  const got = await evaluate('(()=>{const s=[...document.querySelectorAll(".slide")];let b=1e9,i=-1;s.forEach((x,k)=>{const r=x.getBoundingClientRect();const d=Math.abs(r.left)+Math.abs(r.top);if(d<b){b=d;i=k}});return i+1})()');
  if (got !== i) console.log(`  (警告: 期望 P${i}，实际定位到 P${got})`);
  rows.push(await evaluate(MEASURE));
}

console.log(`\n=== 渲染量测 @ ${W}x${H} · ${total} 页 ===`);
let bad = 0;
for (const r of rows) {
  const flag = (c, msg) => { if (c) { bad++; console.log('   !! ' + msg); } };
  console.log(`\n[P${r.idx + 1}] ${r.id} · ${r.layout} · slide ${r.size[0]}x${r.size[1]} card ${r.cardBox[0]}x${r.cardBox[1]}`);
  console.log(`  文本 y ${r.top}..${r.bottom} (${r.topPct}%..${r.bottomPct}%H) | x ${r.l}..${r.r} | vFill ${r.vFill}% hFill ${r.hFill}% | chars ${r.chars}`);
  console.log(`  chrome: ${r.chromeInfo.join(' | ') || '无'}`);
  if (r.navConflict) { bad++; console.log('   !! 分页点落在对比不足的色块上 → ' + r.navConflict); }
  console.log(`  flex: card ${r.flexInfo.card}`);
  console.log(`        box ${r.flexInfo.box}`);
  r.flexInfo.kids.forEach(k => console.log(`     · ${k}`));
  flag(r.collide.length > 0, '文本与底部导航/提示重叠 → ' + r.collide.join(' ; '));
  flag(r.vFill < 62, `纵向填充不足 ${r.vFill}%（页面偏空）`);
  flag(r.topPct < 2, `顶部内容贴边 ${r.topPct}%`);
  flag(r.scrollOverflow, 'canvas-card 出现滚动溢出');
  flag(r.chars < 60, `可见文字过少 ${r.chars}`);
  if (r.outX.length) { bad++; console.log('   !! 横向越界 ' + r.outX.join(' ; ')); }
  if (r.clipped.length) { bad++; console.log('   !! 内容被裁切(overflow:hidden) ' + r.clipped.join(' ; ')); }
  if (r.tiny.length) { bad++; console.log('   !! 字号<14px ' + r.tiny.join(' ; ')); }
  if (r.invisible.length) { bad++; console.log('   !! 不可见 ' + r.invisible.join(' ; ')); }
  if (r.nowrapOver.length) { bad++; console.log('   !! 单行文本超宽(nowrap 溢出) ' + r.nowrapOver.join(' ; ')); }
  Object.entries(r.gridDetail).forEach(([k, v]) => console.log(`  ${k} box ${v.box.join('x')} scrollH ${v.scroll} children(h/scrollH) ${v.children.join(', ')}`));
}
console.log(`\n问题计数: ${bad}`);
fs.writeFileSync(path.join(import.meta.dirname, `measure-${W}x${H}.json`), JSON.stringify(rows, null, 2), 'utf8');
ws.close(); child.kill();
process.exit(0);
