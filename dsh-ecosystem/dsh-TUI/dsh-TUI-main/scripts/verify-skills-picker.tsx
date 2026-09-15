/**
 * `/skills` SkillsPicker 冒烟（xterm-headless，mock 技能数据，不碰注册表）：
 *   1. zh 下渲染：标题、可直调技能 /name 形态、来源标签、简述截断、焦点 ❯；
 *   2. en 热切换（标题/页脚/来源标签）；
 *   3. 空目录显示「当前会话没有可用技能」；
 *   4. 窄终端每行宽度不超限；
 *   5. Loading 态渲染不炸。
 * 运行：node --import tsx/esm scripts/verify-skills-picker.tsx
 */
process.env.FORCE_COLOR = '3'

const [
  { Writable },
  React,
  { Terminal: XTerm },
  { render },
  { SkillsPicker, SkillsPickerLoading },
  { setLang },
  { stringWidth },
] = await Promise.all([
  import('node:stream'),
  import('react'),
  import('@xterm/headless'),
  import('../src/ui.js'),
  import('../src/components/SkillsPicker.js'),
  import('../src/i18n.js'),
  import('../src/ink/stringWidth.js'),
])

const sleep = (ms: number) => new Promise(r => setTimeout(r, ms))

let failures = 0
function assert(cond: boolean, msg: string) {
  if (cond) {
    console.log(`  ✓ ${msg}`)
  } else {
    failures++
    console.error(`  ✗ ${msg}`)
  }
}

function makeTerm(cols: number, rows: number) {
  const term = new XTerm({ cols, rows, scrollback: 0, allowProposedApi: true })
  class FakeStdout extends Writable {
    columns = cols
    rows = rows
    isTTY = true
    _write(chunk: unknown, _e: BufferEncoding, cb: () => void) { term.write(String(chunk), cb) }
  }
  return { term, stdout: new FakeStdout() }
}

function screenText(term: InstanceType<typeof XTerm>, rows: number): string {
  const buf = term.buffer.active
  const lines: string[] = []
  for (let y = 0; y < rows; y++) lines.push(buf.getLine(y)?.translateToString(true) ?? '')
  return lines.join('\n')
}

const skills = [
  { name: 'audit', description: '对当前项目做全面代码审计，找出安全与质量问题', userInvocable: true, source: 'bundled' },
  { name: 'my-helper', description: 'Personal helper skill', userInvocable: true, source: 'user-dsh' },
  { name: 'internal-router', description: 'Model-only routing skill', userInvocable: false, source: 'runtime' },
]

// --- 1. zh 列表渲染 -----------------------------------------------------------

console.log('zh 列表渲染:')

{
  const COLS = 90
  const ROWS = 24
  const { term, stdout } = makeTerm(COLS, ROWS)
  setLang('zh')
  const app = await render(
    React.createElement(SkillsPicker, { skills, focusIndex: 1 }),
    { stdout, exitOnCtrlC: false, patchConsole: false },
  )
  await sleep(300)

  const text = screenText(term, ROWS)
  assert(text.includes('技能'), '标题显示「技能」')
  assert(text.includes('/audit'), '可直调技能显示 /name 形态')
  assert(text.includes('internal-router'), '模型专用技能显示裸名（不带斜杠）')
  assert(!text.includes('/internal-router'), '模型专用技能不带 / 前缀')
  assert(text.includes('内置'), 'bundled 来源显示「内置」')
  assert(text.includes('用户'), 'user-dsh 来源显示「用户」')
  assert(text.includes('运行时'), 'runtime 来源显示「运行时」')
  assert(text.includes('对当前项目做全面代码审计'), '渲染简述')
  assert(text.includes('❯'), '渲染焦点指针')
  assert(text.includes('填入命令'), '页脚显示 Enter 填入提示')

  // --- 2. en 热切换 -------------------------------------------------------------
  setLang('en')
  app.rerender(React.createElement(SkillsPicker, { skills, focusIndex: 1 }))
  await sleep(200)
  const en = screenText(term, ROWS)
  assert(en.includes('Skills'), 'en：标题显示 Skills')
  assert(en.includes('built-in'), 'en：来源标签英文')
  assert(en.includes('Esc to exit'), 'en：页脚英文提示')

  // --- 3. 空目录态 --------------------------------------------------------------
  app.rerender(React.createElement(SkillsPicker, { skills: [], focusIndex: 0 }))
  await sleep(200)
  const empty = screenText(term, ROWS)
  assert(empty.includes('No skills available'), '空目录显示 No skills available')

  setLang('zh')
  app.unmount()
  await sleep(100)
}

// --- 4. 窄终端宽度不超限 -------------------------------------------------------

console.log('窄终端截断:')

{
  const COLS = 32
  const ROWS = 24
  const { term, stdout } = makeTerm(COLS, ROWS)
  setLang('zh')
  const app = await render(
    React.createElement(SkillsPicker, { skills, focusIndex: 0 }),
    { stdout, exitOnCtrlC: false, patchConsole: false },
  )
  await sleep(300)
  app.unmount()
  await sleep(100)

  const buf = term.buffer.active
  for (let y = 0; y < ROWS; y++) {
    const line = buf.getLine(y)?.translateToString(true) ?? ''
    if (line.trim() === '') continue
    const w = stringWidth(line)
    assert(w <= COLS, `第 ${y} 行宽 ${w} ≤ 终端宽 ${COLS}：'${line.trimEnd()}'`)
  }
}

// --- 5. Loading 态 -------------------------------------------------------------

console.log('Loading 态:')

{
  const COLS = 60
  const ROWS = 10
  const { term, stdout } = makeTerm(COLS, ROWS)
  setLang('zh')
  const app = await render(React.createElement(SkillsPickerLoading), {
    stdout,
    exitOnCtrlC: false,
    patchConsole: false,
  })
  await sleep(300)
  const text = screenText(term, ROWS)
  assert(text.includes('技能'), 'Loading：标题渲染')
  assert(text.includes('正在加载技能') || text.includes('正在查询技能注册表'), 'Loading：加载文案渲染')
  app.unmount()
  await sleep(100)
}

// --- 结果 -------------------------------------------------------------------

if (failures > 0) {
  console.error(`\n${failures} 项断言失败`)
  process.exit(1)
}
console.log('\n全部断言通过')
process.exit(0)
