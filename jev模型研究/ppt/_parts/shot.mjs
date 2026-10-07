import { spawn } from 'node:child_process';
import os from 'node:os';
import path from 'node:path';
import fs from 'node:fs';

const EDGE = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe';
const deckUrl = process.argv[2];
const W = Number(process.argv[3] || 1600);
const H = Number(process.argv[4] || 900);
const outDir = process.argv[5] || path.join(import.meta.dirname, 'preview');
fs.mkdirSync(outDir, { recursive: true });
const port = 9500 + (Number(process.env.PORTOFF) || 0);
const ud = path.join(os.tmpdir(), 'edge-shot-' + Date.now());

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
  return r.result?.result?.value;
};

await sleep(1500);
await send('Page.enable');
let total = 0;
for (let i = 0; i < 60 && total === 0; i++) {
  await sleep(300);
  try { total = (await evaluate('document.readyState === "complete" ? document.querySelectorAll(".slide").length : 0')) || 0; } catch { }
}

const STATUS = `(() => {
  const anim = [...document.querySelectorAll('.slide [data-anim]')];
  const hidden = anim.filter(el => parseFloat(getComputedStyle(el).opacity) < 0.9).length;
  return { motionReady: document.body.classList.contains('motion-ready'), animCount: anim.length, hiddenInDeck: hidden };
})()`;

console.log(`\n=== 导出预览图 @ ${W}x${H} · ${total} 页 → ${outDir} ===`);
for (let i = 1; i <= total; i++) {
  await send('Page.navigate', { url: `${deckUrl}?slide=${i}` });
  await send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: 1, mobile: false });
  await sleep(900);
  await send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: 1, mobile: false });
  await sleep(3200);
  const st = await evaluate(STATUS);
  const st2 = await evaluate(`(() => {
    const s=[...document.querySelectorAll('.slide')];let b=1e9,k=0;
    s.forEach((x,j)=>{const r=x.getBoundingClientRect();const d=Math.abs(r.left)+Math.abs(r.top);if(d<b){b=d;k=j}});
    return { idx:k+1, id:s[k].dataset.slideId, hiddenCur:[...s[k].querySelectorAll('[data-anim]')].filter(el=>parseFloat(getComputedStyle(el).opacity)<0.9).length };
  })()`);
  const shot = await send('Page.captureScreenshot', { format: 'png', fromSurface: true });
  const file = path.join(outDir, `p${i}-${st2.id}.png`);
  fs.writeFileSync(file, Buffer.from(shot.result.data, 'base64'));
  console.log(`  P${i} ${st2.id}  动效引擎=${st.motionReady ? '已加载' : '未加载'}  [data-anim] ${st.animCount} 个 · 当前页半透明元素 ${st2.hiddenCur} 个  → ${path.basename(file)}`);
}
console.log(`\n提示：动效引擎未加载时，动效降级为「内容直接可见」，不会丢内容。`);
ws.close(); child.kill();
process.exit(0);
