import { spawn } from 'node:child_process';
import os from 'node:os';
import path from 'node:path';
import fs from 'node:fs';

const EDGE = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe';
const deckUrl = process.argv[2];
const W = Number(process.argv[3] || 1600);
const H = Number(process.argv[4] || 900);
const port = 9400 + (Number(process.env.PORTOFF) || 0);
const ud = path.join(os.tmpdir(), 'edge-audit-' + Date.now());

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

const AUDIT = `(() => {
  const slides = [...document.querySelectorAll('.slide')];
  let idx = 0, best = Infinity;
  slides.forEach((s, i) => { const r = s.getBoundingClientRect(); const d = Math.abs(r.left) + Math.abs(r.top); if (d < best) { best = d; idx = i; } });
  const slide = slides[idx];
  const card = slide.querySelector('.canvas-card');
  const nums = c => { const m = (c || '').match(/[\\d.]+/g); return m ? m.map(Number) : null; };
  const relLum = rgb => { const f = v => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); }; return 0.2126 * f(rgb[0]) + 0.7152 * f(rgb[1]) + 0.0722 * f(rgb[2]); };
  const bgOf = el => {
    let n = el;
    while (n && n !== document.documentElement) {
      const cs = getComputedStyle(n);
      const m = nums(cs.backgroundColor);
      if (m && (m.length === 3 || m[3] > 0.5)) return { rgb: m.slice(0, 3), src: (n.className || n.tagName).toString().slice(0, 26) };
      n = n.parentElement;
    }
    return { rgb: [255, 255, 255], src: 'root' };
  };
  const issues = [], radii = [], palette = new Set(), name = el => (el.className || el.tagName).toString().slice(0, 24);
  const els = [...card.querySelectorAll('*')].filter(el => {
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden') return false;
    if (parseFloat(cs.opacity) < 0.15) return false;
    return [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim().length > 1);
  });
  els.forEach(el => {
    const cs = getComputedStyle(el);
    let fg = nums(cs.color);
    if (!fg || fg.length < 3) return;
    fg = fg.slice(0, 3);
    const bg = bgOf(el);
    const op = parseFloat(cs.opacity);
    if (op < 1) fg = fg.map((v, i) => v * op + bg.rgb[i] * (1 - op));
    const L1 = relLum(fg), L2 = relLum(bg.rgb);
    const cr = (Math.max(L1, L2) + 0.05) / (Math.min(L1, L2) + 0.05);
    const size = parseFloat(cs.fontSize), bold = parseInt(cs.fontWeight) >= 600;
    const need = (size >= 24 || (size >= 18.66 && bold)) ? 3 : 4.5;
    if (cr < need) issues.push(name(el) + ' ' + size + 'px cr=' + cr.toFixed(2) + '<' + need + ' fg=' + cs.color + ' on ' + bg.src);
  });
  card.querySelectorAll('*').forEach(el => {
    const cs = getComputedStyle(el);
    const br = cs.borderRadius;
    if (br && br !== '0px') radii.push(name(el) + '=' + br);
    const m = nums(cs.color);
    if (m && m.length >= 3 && !(m[0] === m[1] && m[1] === m[2])) palette.add(cs.color);
    const b = nums(cs.backgroundColor);
    if (b && b.length >= 3 && (b.length === 3 || b[3] > 0.5) && !(b[0] === b[1] && b[1] === b[2])) palette.add('bg:' + cs.backgroundColor);
  });
  return { idx, id: slide.dataset.slideId, issues: [...new Set(issues)], radii: [...new Set(radii)], palette: [...palette] };
})()`;

await send('Page.enable');
await sleep(400);
const total = await evaluate('document.querySelectorAll(".slide").length');
console.log(`\n=== 视觉规范核对 @ ${W}x${H} · ${total} 页 ===`);
let bad = 0;
const paletteAll = new Set();
for (let i = 1; i <= total; i++) {
  await send('Page.navigate', { url: `${deckUrl}?slide=${i}` });
  await send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: 1, mobile: false });
  await sleep(900);
  await send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: 1, mobile: false });
  await sleep(1800);
  const r = await evaluate(AUDIT);
  console.log(`\n[P${r.idx + 1}] ${r.id}`);
  console.log(`  调色板(${r.palette.length}): ${r.palette.join('  ')}`);
  console.log(`  非直角: ${r.radii.length ? r.radii.join(', ') : '无 ✓'}`);
  if (r.issues.length) { bad += r.issues.length; console.log('   !! 对比度不足，共 ' + r.issues.length + ' 处'); r.issues.forEach(s => console.log('      - ' + s)); }
  else console.log('  对比度: 全部达标 ✓');
  r.palette.forEach(c => paletteAll.add(c.replace('bg:', '')));
}
console.log(`\n全篇出现的颜色: ${[...paletteAll].join('  ')}`);
console.log(`对比度问题总数: ${bad}`);
ws.close(); child.kill();
process.exit(0);
