import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const dir = path.dirname(fileURLToPath(import.meta.url));
const deckPath = path.join(dir, '..', 'index.html');
const read = f => fs.readFileSync(path.join(dir, f), 'utf8');

let html = fs.readFileSync(deckPath, 'utf8');
const before = html.length;

const eol = html.includes('\r\n') ? '\r\n' : '\n';
console.log('EOL =', JSON.stringify(eol));
const norm = s => s.split('\n').join(eol);

function splice(html, startMarker, endMarker, replacement, label) {
  const s = norm(startMarker), e = norm(endMarker);
  const i = html.indexOf(s);
  const j = html.indexOf(e, i + s.length);
  if (i < 0 || j < 0) throw new Error(`锚点未找到: ${label} (start=${i}, end=${j})`);
  return html.slice(0, i) + norm(replacement) + html.slice(j);
}

// 1) 替换示例页面
html = splice(
  html,
  '<!-- ============ 示例:第 1 页',
  '</div>' + '\n\n' + '<div id="nav">',
  '\n' + read('slides.html').trim() + '\n',
  'slides'
);

// 2) 替换演讲备注
html = splice(
  html,
  'const SPEAKER_NOTES = [',
  'window.__SPEAKER_NOTES__',
  read('notes.js').trim() + '\n',
  'notes'
);

// 3) 补全缺失版式类的 CSS
html = html.replace('</style>', norm(read('extra.css').trim()) + eol + '</style>');

// 4) 标题
html = html.replace(/<title>[\s\S]*?<\/title>/, '<title>一场模型的文艺复兴：Jev</title>');

// 5) 默认静态模式：关闭入场动画 / WebGL 网格背景 / ASCII 呼吸场（放映时按 B 可切回动态）
{
  const anchor = "window.__lowPowerMode = stored === '1' || (stored === null && reduced);";
  if (!html.includes(anchor)) throw new Error('锚点未找到: low-power 默认值');
  html = html.replace(anchor, "window.__lowPowerMode = stored === null ? true : stored === '1';");
}

fs.writeFileSync(deckPath, html, 'utf8');

const checks = {
  'slide sections': (html.match(/<section class="slide/g) || []).length,
  'section 闭合': (html.match(/<\/section>/g) || []).length,
  'canvas-card': (html.match(/canvas-card/g) || []).length,
  'notes ids': (html.match(/\n\s+id: '/g) || []).length,
  'deck-safe': (html.match(/deck-safe/g) || []).length,
  'sub-card': (html.match(/class="sub-card/g) || []).length,
  'stack-block': (html.match(/class="stack-block/g) || []).length,
  'ledger-row': (html.match(/class="ledger-row/g) || []).length,
  '示例残留': (html.match(/示例:第/g) || []).length,
  'title': (html.match(/<title>[^<]*<\/title>/) || [''])[0]
};
console.log(`bytes ${before} -> ${html.length}`);
console.log(checks);
