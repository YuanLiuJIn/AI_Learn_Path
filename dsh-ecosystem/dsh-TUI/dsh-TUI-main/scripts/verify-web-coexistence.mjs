/**
 * Regression gate for the dsh-web + dsh-tui mixed-profile failure:
 *
 *   duplicate loader entry id: storage
 *
 * dsh-web-app owns the host rows `storage`, `storage-json`, `storage-domain`,
 * `workspace`, `agent-presets` and `cordis-host-runner`. A bundle patch that
 * inserts the same unscoped ids into the same profile makes the Loader reject
 * the whole tree before any plugin starts. dsh-tui therefore inserts those
 * services under `dsh-tui-*` ids and disables each copy when the official
 * web-app row is already present in the tree.
 *
 * This script composes both patch layers with the include plugin's own patch
 * algorithm and fails if the entry id namespace collides again.
 */

import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { parse } from 'yaml'
import { applyEntryPatches } from '@deepseek-ai/cordis-plugin-include'

const yamlOptions = { logLevel: 'silent' }
const loadPatch = (path) => parse(readFileSync(path, 'utf8'), yamlOptions)

const tuiPath = fileURLToPath(new URL('../cordis.patch.yml', import.meta.url))
const webPath = fileURLToPath(import.meta.resolve('@deepseek-ai/dsh-web-app/cordis.patch.yml'))

const webPatches = loadPatch(webPath)
const tuiPatches = loadPatch(tuiPath)
assert.ok(Array.isArray(webPatches), 'web-app patch must be a top-level list')
assert.ok(Array.isArray(tuiPatches), 'dsh-tui patch must be a top-level list')

const composed = applyEntryPatches([], [...webPatches, ...tuiPatches], () => {})

const counts = new Map()
for (const row of composed) {
  if (typeof row?.id !== 'string') continue
  counts.set(row.id, (counts.get(row.id) ?? 0) + 1)
}
const duplicates = [...counts].filter(([, count]) => count > 1).map(([id]) => id)
assert.deepEqual(
  duplicates,
  [],
  `dsh-tui patch reuses web-app-owned loader entry ids: ${duplicates.join(', ')}. ` +
    'Use dsh-tui-scoped ids and disable the copy when the official row is present.',
)

const shared = [
  { id: 'storage', name: '@deepseek-ai/dsh-storage' },
  { id: 'storage-json', name: '@deepseek-ai/dsh-storage-json' },
  { id: 'storage-domain', name: '@deepseek-ai/dsh-storage-domain' },
  { id: 'workspace', name: '@deepseek-ai/dsh-workspace' },
  { id: 'agent-presets', name: '@deepseek-ai/dsh-agent-presets' },
  { id: 'cordis-host-runner', name: '@deepseek-ai/dsh-cordis-host-runner' },
]

for (const { id, name } of shared) {
  const official = composed.find(row => row?.id === id && row?.name === name)
  assert.ok(official, `web-app patch should mount the official ${id} row`)

  const scopedId = `dsh-tui-${id}`
  const tuiRow = composed.find(row => row?.id === scopedId && row?.name === name)
  assert.ok(tuiRow, `dsh-tui patch must mount a scoped ${scopedId} row`)
  assert.equal(
    typeof tuiRow.disabled,
    'string',
    `${scopedId} must carry a !!js disabled expression that yields to the official row`,
  )
  assert.ok(
    tuiRow.disabled.includes(`entry.options.id === '${id}'`) && tuiRow.disabled.includes(`'${name}'`),
    `${scopedId} disabled expression must target the official ${id}/${name} row`,
  )
}

const presetRow = composed.find(row => row?.id === 'dsh-tui-agent-presets')
assert.ok(
  presetRow?.config?.roots?.includes("@deepseek-ai/dsh/config/agent-presets"),
  'dsh-tui-agent-presets must carry the official CLI shipped preset root itself',
)

console.log(
  `web coexistence OK (${composed.length} composed rows, no loader entry id shared with dsh-web-app)`,
)
